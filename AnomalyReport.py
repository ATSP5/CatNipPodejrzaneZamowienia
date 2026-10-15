from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd

from DataScan import DataScan


@dataclass
class AnomalyReport:
    """Wynik przeglądu zamówień: ile przejrzano, co oznaczono i dlaczego, plus wzorce na poziomie klientów."""

    total_orders: int
    total_value: float
    flagged: pd.DataFrame
    rule_rows: List[Dict[str, object]] = field(default_factory=list)
    similar_groups: List[List[str]] = field(default_factory=list)
    similar_rows: List[Dict[str, object]] = field(default_factory=list)
    behaviour_rows: List[Dict[str, object]] = field(default_factory=list)
    rep_rows: List[Dict[str, object]] = field(default_factory=list)
    scan: Optional[DataScan] = None
    demo: bool = False
    seconds: float = 0.0

    @property
    def flagged_count(self) -> int:
        return len(self.flagged)

    @property
    def flagged_value(self) -> float:
        return float(self.flagged["Wartość"].sum()) if len(self.flagged) else 0.0

    @property
    def customer_count(self) -> int:
        return sum(len(g) for g in self.similar_groups) + len(self.behaviour_rows)
