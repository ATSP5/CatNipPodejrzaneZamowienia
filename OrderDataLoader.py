import time

import pandas as pd

from DataScanner import DataScanner
from DemoOrderData import DemoOrderData
from OrderDataset import OrderDataset
from PipelineStep import PipelineStep
from ProjectFolders import ProjectFolders
from TableReader import TableReader


class OrderDataLoader:
    """Wczytuje zamówienia (CSV), klientów (JSON) i produkty (Excel), robi Data Scan i łączy je w jedną tabelę."""

    ORDER_TYPES = {"order_id": "string", "customer_id": "category", "product_id": "category", "sales_rep": "category"}
    REQUIRED = {
        "orders.csv": ["order_id", "created_at", "customer_id", "product_id", "sales_rep", "quantity", "unit_price", "discount_pct"],
        "customers.json": ["customer_id", "name", "segment"],
        "products.xlsx": ["product_id", "name", "list_price", "unit_cost"],
    }

    def __init__(self, folders: ProjectFolders, reader: TableReader, generator: DemoOrderData, scanner: DataScanner):
        self.folders = folders
        self.reader = reader
        self.generator = generator
        self.scanner = scanner

    def dataset(self) -> OrderDataset:
        started = time.perf_counter()
        demo = self.generator.ensure(self.folders)
        generated = time.perf_counter() - started
        started = time.perf_counter()
        tables = {}
        for name, columns in self.REQUIRED.items():
            path = self.folders.input_path(name)
            frame = self.reader.read(path, self.ORDER_TYPES if name == "orders.csv" else None)
            missing = [c for c in columns if c not in frame.columns]
            if missing:
                raise ValueError("%s: brak kolumn %s" % (name, ", ".join(missing)))
            tables[name] = (self.reader.format_of(path), frame)
        loaded = time.perf_counter() - started
        scan = self.scanner.scan(tables)
        frames = {name: frame for name, (_, frame) in tables.items()}
        if demo:
            scan.pipeline.insert(0, PipelineStep("Generate demo", "dane demonstracyjne zapisane w input/", generated))
        scan.pipeline.insert(1 if demo else 0, PipelineStep("Load", "%s zamówień + %d klientów + %d produktów" % (
            format(len(frames["orders.csv"]), ",").replace(",", " "), len(frames["customers.json"]), len(frames["products.xlsx"])), loaded))
        orders = self.join(frames, scan)
        return OrderDataset(orders, frames["customers.json"], frames["products.xlsx"], scan, demo)

    @staticmethod
    def join(frames, scan) -> pd.DataFrame:
        started = time.perf_counter()
        orders = frames["orders.csv"]
        orders["created_at"] = pd.to_datetime(orders.created_at, format="%Y-%m-%d %H:%M:%S")
        customers = frames["customers.json"].set_index("customer_id")
        products = frames["products.xlsx"].set_index("product_id")
        orders["segment"] = orders.customer_id.map(customers.segment).astype("category")
        orders["list_price"] = orders.product_id.map(products.list_price).astype(float)
        orders["unit_cost"] = orders.product_id.map(products.unit_cost).astype(float)
        orders["net_price"] = orders.unit_price * (1 - orders.discount_pct / 100)
        orders["value"] = orders.quantity * orders.net_price
        scan.pipeline.append(PipelineStep("Validate + Join", "zamówienia × klienci × produkty, braki w słownikach: %d" % int(
            orders.segment.isna().sum() + orders.unit_cost.isna().sum()), time.perf_counter() - started))
        return orders
