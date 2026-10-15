import json
import os
from typing import List

import numpy as np
import pandas as pd

from AnomalySettings import AnomalySettings
from ProjectFolders import ProjectFolders


class DemoOrderData:
    """Dane demonstracyjne hurtowni: milion zamówień z 9 miesięcy 2026, 2 000 klientów, 300 produktów.

    Pliki powstają w input/ tylko wtedy, gdy ich tam nie ma (albo gdy w ustawieniach regenerate=True).
    W danych ukryto kilkadziesiąt nieprawidłowości: rabaty 35–45% (głównie jednego handlowca), ceny poniżej
    kosztu, gigantyczne ilości, zamówienia nocne, duplikaty, trzech klientów o identycznym wzorcu zakupów
    i dwóch klientów, którzy w ostatnim miesiącu nagle zamawiają kilka razy więcej niż zwykle.
    """

    FILES = ("orders.csv", "customers.json", "products.xlsx")
    SEGMENTS = {"Hurt": (0.25, 8.0), "Sieć": (0.10, 12.0), "Detal": (0.35, 2.0), "Instalator": (0.22, 5.0), "Eksport": (0.08, 6.0)}
    CATEGORIES = ["Kabel", "Złączka", "Profil", "Uszczelka", "Wkręt", "Panel", "Zawór", "Czujnik", "Lampa", "Moduł"]
    N_CUSTOMERS = 2000
    N_PRODUCTS = 300
    N_REPS = 20
    START = np.datetime64("2026-01-01T00:00:00")
    DAYS = 273
    SUSPECT_REP = "H07"
    CLONE_REP = "H12"

    def __init__(self, settings: AnomalySettings):
        self.settings = settings

    def generator(self) -> "DemoOrderData":
        return self

    def ensure(self, folders: ProjectFolders) -> bool:
        """Tworzy brakujące pliki demonstracyjne; zwraca True, gdy coś zapisano."""
        present = all(os.path.exists(folders.input_path(name)) for name in self.FILES)
        if present and not self.settings.regenerate:
            return False
        self.write(folders)
        return True

    def write(self, folders: ProjectFolders) -> None:
        rng = np.random.default_rng(self.settings.seed)
        customers = self.customers(rng)
        products = self.products(rng)
        orders = self.orders(rng, customers, products)
        orders = self.plant_anomalies(rng, orders, customers, products)
        orders = orders.sort_values("created_at", kind="stable").reset_index(drop=True)
        orders.insert(0, "order_id", "ZM-" + pd.Series(np.arange(1, len(orders) + 1)).astype(str).str.zfill(7))
        orders["created_at"] = orders.created_at.dt.strftime("%Y-%m-%d %H:%M:%S")
        orders.to_csv(folders.input_path("orders.csv"), index=False)
        with open(folders.input_path("customers.json"), "w", encoding="utf-8") as handle:
            json.dump(customers.to_dict("records"), handle, ensure_ascii=False, indent=1)
        products.to_excel(folders.input_path("products.xlsx"), index=False)

    # ── Słowniki ────────────────────────────────────────────────────────────────

    def customers(self, rng: np.random.Generator) -> pd.DataFrame:
        names = list(self.SEGMENTS)
        shares = np.array([self.SEGMENTS[n][0] for n in names])
        count = self.N_CUSTOMERS + 3
        segment = rng.choice(names, size=count, p=shares / shares.sum())
        rep = np.array(["H%02d" % (i + 1) for i in rng.integers(0, self.N_REPS, size=count)])
        segment[-3:], rep[-3:] = "Hurt", self.CLONE_REP
        stems = ["Elektro", "Bud", "Instal", "Term", "Hydro", "Tech", "Mont", "Pol", "Eko", "Inwest"]
        tails = ["mex", "pol", "serwis", "trade", "system", "bud", "hurt", "group"]
        name = ["%s%s %s" % (rng.choice(stems), rng.choice(tails), rng.choice(["sp. z o.o.", "S.A.", "sp.j."])) for _ in range(count)]
        return pd.DataFrame({"customer_id": ["C%04d" % (i + 1) for i in range(count)], "name": name,
                             "segment": segment, "sales_rep": rep,
                             "since": ["2019-01-01"] * self.N_CUSTOMERS + ["2026-07-20"] * 3})

    def products(self, rng: np.random.Generator) -> pd.DataFrame:
        price = np.round(np.exp(rng.normal(4.0, 0.9, self.N_PRODUCTS)), 2)
        category = rng.choice(self.CATEGORIES, size=self.N_PRODUCTS)
        return pd.DataFrame({"product_id": ["PR-%04d" % (i + 1) for i in range(self.N_PRODUCTS)],
                             "name": ["%s %s-%03d" % (c, c[:2].upper(), i + 1) for i, c in enumerate(category)],
                             "category": category, "list_price": price,
                             "unit_cost": np.round(price * rng.uniform(0.55, 0.75, self.N_PRODUCTS), 2),
                             "typical_qty": np.maximum(1, np.round(np.exp(rng.normal(2.5, 0.8, self.N_PRODUCTS))))})

    # ── Zwykłe zamówienia ───────────────────────────────────────────────────────

    def orders(self, rng: np.random.Generator, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
        n = self.settings.n_orders
        regular = self.N_CUSTOMERS
        weight = rng.pareto(1.5, regular) + 1
        customer = rng.choice(regular, size=n, p=weight / weight.sum())
        preferences = rng.integers(0, self.N_PRODUCTS, size=(regular, 12))
        product = np.where(rng.random(n) < 0.85, preferences[customer, rng.integers(0, 12, size=n)],
                           rng.integers(0, self.N_PRODUCTS, size=n))
        return self.frame(rng, customers, products, customer, product, self.business_times(rng, n))

    def business_times(self, rng: np.random.Generator, n: int, first_day: int = 0, days: int = DAYS) -> np.ndarray:
        day = rng.integers(first_day, first_day + days, size=n)
        stamps = self.START + day.astype("timedelta64[D]")
        weekday = (stamps.astype("datetime64[D]").view("int64") - 4) % 7  # 0 = poniedziałek
        stamps = stamps + (weekday == 6).astype("timedelta64[D]")  # niedziela → poniedziałek
        seconds = rng.integers(7 * 3600, 18 * 3600, size=n)
        return stamps + seconds.astype("timedelta64[s]")

    def frame(self, rng, customers, products, customer, product, times) -> pd.DataFrame:
        n = len(customer)
        segment = customers.segment.to_numpy()[customer]
        base_discount = np.array([self.SEGMENTS[s][1] for s in segment])
        typical = products.typical_qty.to_numpy()[product]
        return pd.DataFrame({
            "created_at": pd.to_datetime(times),
            "customer_id": customers.customer_id.to_numpy()[customer],
            "product_id": products.product_id.to_numpy()[product],
            "sales_rep": customers.sales_rep.to_numpy()[customer],
            "quantity": np.maximum(1, np.round(typical * np.exp(rng.normal(0, 0.5, n)))).astype(int),
            "unit_price": np.round(products.list_price.to_numpy()[product] * (1 + rng.normal(0, 0.02, n)), 2),
            "discount_pct": np.round(np.clip(base_discount + rng.normal(0, 1.0, n), 0, base_discount + 3), 1),
        })

    # ── Ukryte nieprawidłowości ─────────────────────────────────────────────────

    def plant_anomalies(self, rng, orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
        cost = products.set_index("product_id").unit_cost
        used = set()

        def pick(mask, count):
            pool = np.flatnonzero(mask & ~orders.index.isin(list(used)))
            chosen = rng.choice(pool, size=count, replace=False)
            used.update(chosen.tolist())
            return chosen

        everyone = np.ones(len(orders), dtype=bool)
        rows = np.concatenate([pick(orders.sales_rep.to_numpy() == self.SUSPECT_REP, 9), pick(everyone, 3)])
        orders.loc[rows, "discount_pct"] = np.round(rng.uniform(35, 45, len(rows)), 1)
        rows = pick(everyone, 8)
        orders.loc[rows, "unit_price"] = np.round(cost.reindex(orders.loc[rows, "product_id"]).to_numpy() * rng.uniform(0.55, 0.8, 8), 2)
        rows = pick(everyone, 6)
        orders.loc[rows, "quantity"] = orders.loc[rows, "quantity"] * 40
        rows = pick(everyone, 5)
        night = orders.loc[rows, "created_at"].dt.normalize() + pd.to_timedelta(rng.integers(3600, 4 * 3600, 5), unit="s")
        orders.loc[rows, "created_at"] = night.to_numpy()
        copies = orders.loc[pick(everyone, 4)].copy()
        copies["created_at"] = copies.created_at + pd.to_timedelta(rng.integers(60, 240, 4), unit="s")
        return pd.concat([orders, copies, self.clones(rng, customers, products), self.bursts(rng, orders, customers, products)],
                         ignore_index=True)

    def clones(self, rng, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
        """Trzech nowych klientów kupuje to samo, w tych samych ilościach, prawie w tych samych chwilach."""
        basket = rng.choice(self.N_PRODUCTS, size=8, replace=False)
        product = np.tile(rng.choice(basket, size=40), 3)
        customer = np.repeat(np.arange(self.N_CUSTOMERS, self.N_CUSTOMERS + 3), 40)
        times = np.tile(self.business_times(rng, 40, first_day=201, days=72), 3)
        frame = self.frame(rng, customers, products, customer, product, times)
        frame["created_at"] = frame.created_at + pd.to_timedelta(np.repeat([0, 7, 13], 40), unit="m")
        frame["quantity"] = np.tile(frame.quantity.to_numpy()[:40], 3)
        return frame

    def bursts(self, rng, orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
        """Dwóch zwykłych klientów, którzy we wrześniu zamawiają ~6× więcej niż zwykle."""
        counts = orders.customer_id.value_counts()
        steady = counts[(counts > 150) & (counts < 400)].index[:2]
        index = {cid: i for i, cid in enumerate(customers.customer_id)}
        frames = []
        for cid in steady:
            monthly = counts[cid] / 9
            extra = int(monthly * 5)
            history = orders.loc[orders.customer_id == cid, "product_id"].to_numpy()
            product = products.index[products.product_id.isin(history)].to_numpy()
            frames.append(self.frame(rng, customers, products, np.full(extra, index[cid]), rng.choice(product, size=extra),
                                     self.business_times(rng, extra, first_day=243, days=30)))
        return pd.concat(frames, ignore_index=True)
