Reguły na poziomie klienta: nagła zmiana zachowania (ostatni miesiąc vs średnia) i grupy klientów o niemal identycznym koszyku zakupów (podobieństwo cosinusowe wektorów ilości per produkt).

## settings
Wejście — `AnomalySettings` (`behaviour_ratio`, `similarity`).

## patterns
Wyjście bloku — te reguły, podawane do `AnomalyDetector`.

## behaviour_changes
Klienci, którzy w ostatnim miesiącu zamówili `behaviour_ratio` razy więcej niż średnio.

## similar_groups
Grupy klientów o podobieństwie koszyków ≥ `similarity`.

## connected
Łączy pary podobnych klientów w grupy.
