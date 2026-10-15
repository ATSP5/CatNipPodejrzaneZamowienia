Ustawienia analizy. Zmieniasz je w Inspektorze tego bloku, sekcja **INITIALISER**: Refresh → zmień wartości → Apply. Ten sam obiekt trafia do generatora danych, reguł zamówień i wzorców klientów.

## n_orders
Ile zamówień ma zbiór demonstracyjny (domyślnie 1 000 000). Działa, gdy dane powstają od nowa.

## regenerate
`True` — wygeneruj dane demo od nowa, nawet jeśli już są w `input/`.

## seed
Ziarno losowania danych demo.

## price_z
Ile odpornych odchyleń (MAD) cena może odbiegać od typowej ceny produktu.

## quantity_z
To samo dla ilości, w skali logarytmicznej.

## discount_gap_pp
O ile punktów rabat może przekroczyć typowy rabat segmentu klienta.

## night_end_hour
Zamówienia przed tą godziną (oraz od 22:00 i w niedziele) są nietypowe.

## duplicate_minutes
To samo zamówienie powtórzone w tylu minutach to podejrzany duplikat.

## behaviour_ratio
Ile razy więcej zamówień w ostatnim miesiącu niż średnio oznacza nagłą zmianę.

## similarity
Podobieństwo koszyków (cosinus 0–1), od którego klienci są „klonami”.

## settings
Wyjście bloku — te ustawienia.
