import datetime as dt

import pandas as pd

from AnomalyReport import AnomalyReport


class FindingsPowerBiTable:
    """Tabela podejrzanych zamówień dla Power BI: kolumny jak w raporcie i CSV, Data jako data, plus czas eksportu."""

    def __init__(self, report: AnomalyReport):
        self.report = report

    def table(self) -> pd.DataFrame:
        rows = self.report.flagged.copy()
        rows["Data"] = pd.to_datetime(rows["Data"], format="%Y-%m-%d %H:%M", errors="coerce")
        rows["Wyeksportowano"] = pd.Timestamp(dt.datetime.now().replace(microsecond=0))
        return rows
