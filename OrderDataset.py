from dataclasses import dataclass

import pandas as pd

from DataScan import DataScan


@dataclass
class OrderDataset:
    """Zamówienia połączone z klientami i produktami (jedna tabela) oraz wynik Data Scan."""

    orders: pd.DataFrame
    customers: pd.DataFrame
    products: pd.DataFrame
    scan: DataScan
    demo: bool = False
