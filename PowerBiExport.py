import dataclasses
import datetime
import json
import os
import time
import uuid

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


class PowerBiExport:

    CONTAINER_ROOT = '/app'

    def __init__(self, data=None, output_path='output/powerbi/podejrzane_zamowienia.parquet', mode='overwrite',
                 timestamp_timezone='UTC', on_schema_change='warn', compression='snappy',
                 write_query=True, retries=20, retry_delay=0.5):
        self._data = data
        self.output_path = output_path
        self.mode = mode
        self.timestamp_timezone = timestamp_timezone
        self.on_schema_change = on_schema_change
        self.compression = compression
        self.write_query = write_query
        self.retries = retries
        self.retry_delay = retry_delay

    def path(self, data=None):
        table = self._to_table(self._data if data is None else data)
        table = self._for_power_bi(table)
        target = self._target()
        self._check_schema(table, target)
        self._write_atomically(table, target)
        shown = self._host_path(target)
        print('[Power BI] wrote %d rows, %d columns to %s' % (table.num_rows, table.num_columns, shown))
        if shown == target and target.startswith(self.CONTAINER_ROOT + '/'):
            print('[Power BI] This path is inside a Docker container: on your computer the file is %s '
                  'in the project folder.' % target[len(self.CONTAINER_ROOT) + 1:])
        if self.write_query:
            self._write_query(target, shown)
        return target

    def _to_table(self, data):
        if data is None:
            raise ValueError('PowerBiExport received no data: connect a block to its data input.')
        if isinstance(data, pa.Table):
            return data
        if isinstance(data, pa.RecordBatch):
            return pa.Table.from_batches([data])
        if hasattr(data, 'to_arrow') and not hasattr(data, 'to_parquet'):
            return data.to_arrow()
        if type(data).__module__.startswith('pandas') and hasattr(data, 'columns'):
            if any(name is not None for name in data.index.names):
                data = data.reset_index()
            return pa.Table.from_pandas(data, preserve_index=False)
        if isinstance(data, dict):
            return pa.table({str(name): list(values) for name, values in data.items()})
        if isinstance(data, (list, tuple)):
            rows = list(data)
            if not rows:
                raise ValueError('PowerBiExport received an empty list: there are no rows and no columns to write.')
            if dataclasses.is_dataclass(rows[0]):
                rows = [dataclasses.asdict(row) for row in rows]
            if not isinstance(rows[0], dict):
                raise TypeError('PowerBiExport needs named columns: a list of dicts or of @dataclass records, '
                                'not a list of %s.' % type(rows[0]).__name__)
            return pa.Table.from_pylist(rows)
        raise TypeError('PowerBiExport cannot write %s. Give it a pandas DataFrame, a pyarrow Table, '
                        'a dict of columns, or a list of dicts / @dataclass records.' % type(data).__name__)

    def _for_power_bi(self, table):
        names = [str(name) for name in table.column_names]
        blank = [i for i, name in enumerate(names) if not name.strip()]
        if blank:
            raise ValueError('Power BI needs a name for every column; columns %s have none.' % blank)
        seen = set()
        for name in names:
            if name.lower() in seen:
                raise ValueError('Power BI needs unique column names; "%s" appears twice '
                                 '(column names are compared without case).' % name)
            seen.add(name.lower())
        columns = []
        for name, column in zip(names, table.columns):
            converted, note = self._column_for_power_bi(name, column)
            if note:
                print('[Power BI] column "%s": %s' % (name, note))
            columns.append(converted)
        return pa.table(columns, names=names)

    def _column_for_power_bi(self, name, column):
        kind = column.type
        if pa.types.is_dictionary(kind):
            column = column.cast(kind.value_type)
            kind = column.type
        if pa.types.is_timestamp(kind):
            return self._timestamp_for_power_bi(column)
        if pa.types.is_time64(kind) and kind.unit == 'ns':
            return column.cast(pa.time64('us'), safe=False), 'time cut to microseconds'
        if pa.types.is_date64(kind):
            return column.cast(pa.date32()), None
        if pa.types.is_duration(kind):
            seconds = pc.divide(column.cast(pa.duration('us'), safe=False).cast(pa.int64()), 1000000.0)
            return seconds, 'duration written as seconds (decimal number)'
        if pa.types.is_uint64(kind):
            largest = pc.max(column).as_py()
            if largest is not None and largest > 2 ** 63 - 1:
                raise ValueError('Column "%s" holds %d, larger than Power BI\'s whole-number limit.' % (name, largest))
            return column.cast(pa.int64()), 'unsigned 64-bit written as signed 64-bit'
        if pa.types.is_unsigned_integer(kind):
            return column.cast(pa.int64()), None
        if pa.types.is_float16(kind):
            return column.cast(pa.float64()), None
        if pa.types.is_decimal(kind):
            if kind.precision > 38:
                return column.cast(pa.float64()), 'decimal wider than 38 digits written as a decimal number'
            if isinstance(kind, pa.Decimal256Type):
                return column.cast(pa.decimal128(kind.precision, kind.scale)), None
            return column, None
        if pa.types.is_large_string(kind):
            return column.cast(pa.string()), None
        if pa.types.is_large_binary(kind):
            return column.cast(pa.binary()), None
        if pa.types.is_null(kind):
            return column.cast(pa.string()), 'empty column written as text'
        if pa.types.is_nested(kind):
            values = [None if value is None else json.dumps(value, default=str, ensure_ascii=False)
                      for value in column.to_pylist()]
            return pa.chunked_array([pa.array(values, pa.string())]), 'nested values written as JSON text'
        return column, None

    def _timestamp_for_power_bi(self, column):
        kind = column.type
        note = 'timestamp cut to microseconds' if kind.unit == 'ns' else None
        if kind.tz is not None:
            if self.timestamp_timezone and self.timestamp_timezone.upper() != 'UTC':
                column = pc.local_timestamp(column.cast(pa.timestamp(kind.unit, tz=self.timestamp_timezone)))
                note = 'time zone removed, shown as %s time' % self.timestamp_timezone
            else:
                column = column.cast(pa.timestamp(kind.unit))
                note = 'time zone removed, shown as UTC'
        return column.cast(pa.timestamp('us'), safe=False), note

    def _target(self):
        location = os.path.abspath(self.output_path)
        if self.mode == 'overwrite':
            return location
        if self.mode == 'folder':
            folder = location[:-len('.parquet')] if location.lower().endswith('.parquet') else location
            stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            return os.path.join(folder, 'part-%s-%s.parquet' % (stamp, uuid.uuid4().hex[:6]))
        raise ValueError("mode must be 'overwrite' or 'folder', not %r." % self.mode)

    def _previous_schema(self, target):
        if self.mode == 'overwrite':
            return pq.read_schema(target) if os.path.exists(target) else None
        folder = os.path.dirname(target)
        if not os.path.isdir(folder):
            return None
        parts = [os.path.join(folder, name) for name in os.listdir(folder) if name.lower().endswith('.parquet')]
        return pq.read_schema(max(parts, key=os.path.getmtime)) if parts else None

    def _check_schema(self, table, target):
        if self.on_schema_change == 'ignore':
            return
        try:
            previous = self._previous_schema(target)
        except (OSError, pa.ArrowInvalid):
            return
        if previous is None:
            return
        before = {field.name: field.type for field in previous}
        after = {field.name: field.type for field in table.schema}
        changes = ['added ' + name for name in after if name not in before]
        changes += ['removed ' + name for name in before if name not in after]
        changes += ['%s changed from %s to %s' % (name, before[name], after[name])
                    for name in after if name in before and before[name] != after[name]]
        if not changes:
            return
        message = ('The columns differ from the file Power BI already reads (%s). Queries and visuals '
                   'using them may break on the next refresh.' % '; '.join(changes))
        if self.on_schema_change == 'error':
            raise ValueError(message + " Nothing was written; set on_schema_change='warn' to write anyway.")
        print('[Power BI] WARNING: ' + message)

    def _write_atomically(self, table, target):
        folder = os.path.dirname(target)
        os.makedirs(folder, exist_ok=True)
        temporary = os.path.join(folder, '.%s.%s.tmp' % (os.path.basename(target), uuid.uuid4().hex[:8]))
        pq.write_table(table, temporary, compression=self.compression)
        for attempt in range(self.retries + 1):
            try:
                os.replace(temporary, target)
                return
            except PermissionError:
                if attempt == self.retries:
                    os.remove(temporary)
                    raise PermissionError('%s is in use by another program - most likely Power BI in the '
                                          'middle of a refresh. Let it finish, then run again.' % target)
                time.sleep(self.retry_delay)

    def _host_path(self, target):
        host = os.environ.get('CATNIP_HOST_WORKDIR', '')
        prefix = self.CONTAINER_ROOT + '/'
        if not host or not target.startswith(prefix):
            return target
        windows = (len(host) > 1 and host[1] == ':') or host.startswith('\\\\')
        separator = '\\' if windows else '/'
        return host.rstrip('\\/') + separator + target[len(prefix):].replace('/', separator)

    def _write_query(self, target, shown):
        if self.mode == 'overwrite':
            query_path = os.path.splitext(target)[0] + '.pq'
            query = 'let\n    Source = Parquet.Document(File.Contents("%s"))\nin\n    Source\n' % shown.replace('"', '""')
            hint = 'Power BI: Get data > Blank query > Advanced editor, paste this query'
        else:
            folder = os.path.dirname(shown)
            query_path = os.path.dirname(target) + '.pq'
            query = ('let\n'
                     '    Source = Folder.Files("%s"),\n'
                     '    Parts = Table.SelectRows(Source, each Text.Lower([Extension]) = ".parquet"),\n'
                     '    Tables = Table.AddColumn(Parts, "Data", each Parquet.Document([Content])),\n'
                     '    Combined = Table.Combine(Tables[Data])\n'
                     'in\n'
                     '    Combined\n') % folder.replace('"', '""')
            hint = ('Power BI: Get data > Folder, pick %s, Combine - or Get data > Blank query > '
                    'Advanced editor, paste this query' % folder)
        with open(query_path, 'w', encoding='utf-8') as handle:
            handle.write(query)
        print('[Power BI] %s (also saved in %s):' % (hint, self._host_path(query_path)))
        print(query)
        for variable in ('OneDrive', 'OneDriveCommercial', 'OneDriveConsumer'):
            synced = os.environ.get(variable)
            if synced and os.path.abspath(target).lower().startswith(os.path.abspath(synced).lower() + os.sep):
                print('[Power BI] The file is in OneDrive: connect to it with its SharePoint/OneDrive link '
                      'so the Power BI service refreshes it without a gateway.')
                break
