from typing import Callable, Dict

import numpy as np
import pandas as pd

from AnomalySettings import AnomalySettings


class OrderRules:
    """Reguły dla pojedynczego zamówienia. Każda zwraca maskę True/False dla wszystkich zamówień naraz.

    Typowe wartości liczone są per produkt lub per segment klienta, a odchylenia odpornie (mediana i MAD),
    więc kilka nieprawidłowych zamówień nie przesuwa samej normy.
    """

    def __init__(self, settings: AnomalySettings):
        self.settings = settings

    def rules(self) -> "OrderRules":
        return self

    def catalogue(self) -> Dict[str, Callable[[pd.DataFrame], pd.Series]]:
        return {
            "Cena poniżej kosztu": self.below_cost,
            "Nietypowy rabat": self.unusual_discount,
            "Cena odbiega od cennika": self.unusual_price,
            "Nietypowa ilość": self.unusual_quantity,
            "Nietypowa pora": self.off_hours,
            "Możliwy duplikat": self.duplicate,
        }

    @staticmethod
    def robust_z(values: pd.Series, groups: pd.Series) -> pd.Series:
        grouped = values.groupby(groups, observed=True)
        median = grouped.transform("median")
        mad = (values - median).abs().groupby(groups, observed=True).transform("median")
        return 0.6745 * (values - median) / mad.replace(0, np.nan)

    def below_cost(self, orders: pd.DataFrame) -> pd.Series:
        return orders.net_price < orders.unit_cost

    def unusual_discount(self, orders: pd.DataFrame) -> pd.Series:
        typical = orders.discount_pct.groupby(orders.segment, observed=True).transform("median")
        return orders.discount_pct - typical > self.settings.discount_gap_pp

    def unusual_price(self, orders: pd.DataFrame) -> pd.Series:
        return self.robust_z(orders.unit_price, orders.product_id).abs() > self.settings.price_z

    def unusual_quantity(self, orders: pd.DataFrame) -> pd.Series:
        return self.robust_z(np.log(orders.quantity.astype(float)), orders.product_id) > self.settings.quantity_z

    def off_hours(self, orders: pd.DataFrame) -> pd.Series:
        hour = orders.created_at.dt.hour
        return (hour < self.settings.night_end_hour) | (hour >= 22) | (orders.created_at.dt.dayofweek == 6)

    def duplicate(self, orders: pd.DataFrame) -> pd.Series:
        keys = ["customer_id", "product_id", "quantity", "unit_price", "discount_pct"]
        ordered = orders.sort_values(keys + ["created_at"])
        same = (ordered[keys] == ordered[keys].shift()).all(axis=1)
        close = ordered.created_at.diff() <= pd.Timedelta(minutes=self.settings.duplicate_minutes)
        return (same & close).reindex(orders.index)
