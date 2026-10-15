from typing import Dict, List

import numpy as np
import pandas as pd

from AnomalySettings import AnomalySettings


class CustomerPatterns:
    """Reguły na poziomie klienta: nagła zmiana zachowania i klienci o niemal identycznym wzorcu zakupów."""

    MIN_ORDERS = 20
    MIN_MONTHLY = 5

    def __init__(self, settings: AnomalySettings):
        self.settings = settings

    def patterns(self) -> "CustomerPatterns":
        return self

    def behaviour_changes(self, orders: pd.DataFrame) -> List[Dict[str, object]]:
        """Klienci, którzy w ostatnim miesiącu zamówili behaviour_ratio razy więcej niż ich średnia."""
        month = orders.created_at.dt.to_period("M")
        last = month.max()
        counts = orders.groupby([orders.customer_id, month], observed=True).size().unstack(fill_value=0)
        before = counts.drop(columns=[last]).mean(axis=1)
        ratio = counts[last] / before.replace(0, np.nan)
        hits = ratio[(ratio >= self.settings.behaviour_ratio) & (before >= self.MIN_MONTHLY)].sort_values(ascending=False)
        values = orders[month == last].groupby("customer_id", observed=True).value.sum()
        return [{"customer_id": cid, "Średnio / mies.": round(float(before[cid]), 1), "Ostatni miesiąc": int(counts.at[cid, last]),
                 "Krotność": round(float(ratio[cid]), 1), "Wartość ost. miesiąca": round(float(values.get(cid, 0.0)))}
                for cid in hits.index]

    def similar_groups(self, orders: pd.DataFrame) -> List[List[str]]:
        """Grupy klientów, których koszyki (udział ilości w produktach) mają podobieństwo cosinusowe ≥ similarity."""
        active = orders.customer_id.value_counts()
        active = active[active >= self.MIN_ORDERS].index
        subset = orders[orders.customer_id.isin(active)]
        matrix = subset.pivot_table(index="customer_id", columns="product_id", values="quantity", aggfunc="sum",
                                    fill_value=0, observed=True)
        vectors = matrix.to_numpy(dtype=float)
        vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        similarity = vectors @ vectors.T
        np.fill_diagonal(similarity, 0)
        pairs = np.argwhere(np.triu(similarity >= self.settings.similarity))
        return self.connected(pairs, list(matrix.index))

    @staticmethod
    def connected(pairs: np.ndarray, names: List[str]) -> List[List[str]]:
        parent = list(range(len(names)))

        def root(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for a, b in pairs:
            parent[root(a)] = root(b)
        groups: Dict[int, List[str]] = {}
        for i in {int(x) for pair in pairs for x in pair}:
            groups.setdefault(root(i), []).append(names[i])
        return [sorted(g) for g in groups.values()]
