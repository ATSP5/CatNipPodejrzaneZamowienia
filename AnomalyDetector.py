import time
from typing import Dict, List

import pandas as pd

from AnomalyReport import AnomalyReport
from CustomerPatterns import CustomerPatterns
from OrderDataset import OrderDataset
from OrderRules import OrderRules
from PipelineStep import PipelineStep


class AnomalyDetector:
    """Przepuszcza wszystkie zamówienia przez reguły i wzorce klientów i zbiera to, co warto sprawdzić."""

    def __init__(self, dataset: OrderDataset, rules: OrderRules, patterns: CustomerPatterns):
        self.dataset = dataset
        self.rules = rules
        self.patterns = patterns
        self._report = None

    def findings(self) -> AnomalyReport:
        if self._report is None:
            self._report = self.detect()
        return self._report

    def detect(self) -> AnomalyReport:
        orders = self.dataset.orders
        scan = self.dataset.scan
        masks = {}
        for name, rule in self.rules.catalogue().items():
            begun = time.perf_counter()
            masks[name] = rule(orders).fillna(False).to_numpy(dtype=bool)
            scan.pipeline.append(PipelineStep("Rule: " + name, "%d trafień" % int(masks[name].sum()), time.perf_counter() - begun))
        hits = pd.DataFrame(masks, index=orders.index)
        any_hit = hits.any(axis=1)
        flagged = self.flagged_table(orders[any_hit], hits[any_hit])

        begun = time.perf_counter()
        groups = self.patterns.similar_groups(orders)
        behaviour = self.patterns.behaviour_changes(orders)
        scan.pipeline.append(PipelineStep("Customer patterns", "%d grup klonów, %d nagłych zmian" % (len(groups), len(behaviour)),
                                          time.perf_counter() - begun))
        report = AnomalyReport(
            total_orders=len(orders), total_value=float(orders.value.sum()), flagged=flagged,
            rule_rows=self.rule_rows(orders, hits), similar_groups=groups, similar_rows=self.similar_rows(orders, groups),
            behaviour_rows=self.named(behaviour), rep_rows=self.rep_rows(orders, hits), scan=scan, demo=self.dataset.demo)
        report.seconds = sum(step.seconds for step in scan.pipeline if step.name != "Generate demo")
        return report

    def flagged_table(self, orders: pd.DataFrame, hits: pd.DataFrame) -> pd.DataFrame:
        names = self.customer_names()
        products = self.dataset.products.set_index("product_id").name
        reasons = hits.apply(lambda row: ", ".join(name for name, hit in row.items() if hit), axis=1)
        loss = ((orders.unit_cost - orders.net_price) * orders.quantity).clip(lower=0)
        table = pd.DataFrame({
            "Zamówienie": orders.order_id.astype(str), "Data": orders.created_at.dt.strftime("%Y-%m-%d %H:%M"),
            "Klient": orders.customer_id.astype(str) + " " + orders.customer_id.astype(str).map(names),
            "Segment": orders.segment.astype(str), "Produkt": orders.product_id.astype(str).map(products),
            "Handlowiec": orders.sales_rep.astype(str), "Ilość": orders.quantity, "Cena": orders.unit_price.round(2),
            "Rabat %": orders.discount_pct, "Wartość": orders.value.round(2), "Strata": loss.round(2),
            "Powody": reasons, "Liczba reguł": hits.sum(axis=1)})
        return table.sort_values(["Liczba reguł", "Wartość"], ascending=False).reset_index(drop=True)

    @staticmethod
    def rule_rows(orders: pd.DataFrame, hits: pd.DataFrame) -> List[Dict[str, object]]:
        return [{"Reguła": name, "Zamówienia": int(hits[name].sum()), "Wartość": round(float(orders.value[hits[name]].sum()))}
                for name in hits.columns]

    @staticmethod
    def rep_rows(orders: pd.DataFrame, hits: pd.DataFrame) -> List[Dict[str, object]]:
        """Kto stoi za rabatami i cenami poniżej kosztu — koncentracja u jednej osoby to sygnał."""
        pricing = hits["Nietypowy rabat"] | hits["Cena poniżej kosztu"]
        if not pricing.any():
            return []
        counts = orders.sales_rep[pricing].astype(str).value_counts()
        share_of_orders = orders.sales_rep.astype(str).value_counts(normalize=True)
        return [{"Handlowiec": rep, "Podejrzane ceny/rabaty": int(n), "Udział w podejrzanych %": round(float(100 * n / pricing.sum()), 1),
                 "Udział we wszystkich zamówieniach %": round(100 * float(share_of_orders.get(rep, 0)), 1)}
                for rep, n in counts.items() if n > 0]

    def customer_names(self) -> Dict[str, str]:
        customers = self.dataset.customers
        return dict(zip(customers.customer_id, customers.name))

    def named(self, rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
        names = self.customer_names()
        return [{"Klient": "%s %s" % (r["customer_id"], names.get(r["customer_id"], "")), **{k: v for k, v in r.items() if k != "customer_id"}}
                for r in rows]

    def similar_rows(self, orders: pd.DataFrame, groups: List[List[str]]) -> List[Dict[str, object]]:
        customers = self.dataset.customers.set_index("customer_id")
        rows = []
        for number, group in enumerate(groups, 1):
            part = orders[orders.customer_id.isin(group)]
            for cid in group:
                info = customers.loc[cid]
                mine = part[part.customer_id == cid]
                rows.append({"Grupa": number, "Klient": "%s %s" % (cid, info["name"]),
                             "Klient od": info.get("since", ""), "Handlowiec": info.get("sales_rep", ""),
                             "Zamówienia": len(mine), "Wartość": round(float(mine.value.sum()))})
        return rows
