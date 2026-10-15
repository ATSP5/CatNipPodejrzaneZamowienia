class AnomalySettings:
    """Ustawienia analizy — zmieniasz je w Inspektorze tego bloku, sekcja INITIALISER (Refresh → zmień → Apply).

    n_orders           ile zamówień ma mieć zbiór demonstracyjny (powstaje tylko, gdy input/ jest pusty)
    regenerate         True = wygeneruj dane demo od nowa, nawet jeśli już są
    seed               ziarno losowania danych demo
    price_z            ile odchyleń (odpornych, MAD) cena może odbiegać od typowej ceny produktu
    quantity_z         to samo dla ilości (w skali logarytmicznej)
    discount_gap_pp    o ile punktów rabat może przekroczyć typowy rabat segmentu klienta
    night_end_hour     zamówienia przed tą godziną (i od 22:00, i w niedziele) są nietypowe
    duplicate_minutes  to samo zamówienie powtórzone w tylu minutach = podejrzany duplikat
    behaviour_ratio    ile razy więcej zamówień w ostatnim miesiącu niż średnio = nagła zmiana
    similarity         podobieństwo koszyków (cosinus 0–1), od którego klienci są „klonami”
    """

    def __init__(self, n_orders: int = 1000000, regenerate: bool = False, seed: int = 42, price_z: float = 6.0, quantity_z: float = 5.0, discount_gap_pp: float = 15.0, night_end_hour: int = 6, duplicate_minutes: int = 10, behaviour_ratio: float = 4.0, similarity: float = 0.98):
        self.n_orders = int(n_orders)
        self.regenerate = bool(regenerate)
        self.seed = int(seed)
        self.price_z = float(price_z)
        self.quantity_z = float(quantity_z)
        self.discount_gap_pp = float(discount_gap_pp)
        self.night_end_hour = int(night_end_hour)
        self.duplicate_minutes = int(duplicate_minutes)
        self.behaviour_ratio = float(behaviour_ratio)
        self.similarity = float(similarity)
        if self.n_orders < 10000:
            raise ValueError("n_orders: co najmniej 10 000 zamówień")
        if not 0 < self.similarity <= 1:
            raise ValueError("similarity: liczba z przedziału (0, 1]")

    def settings(self) -> "AnomalySettings":
        return self
