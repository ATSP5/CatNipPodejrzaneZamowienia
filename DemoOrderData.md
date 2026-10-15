Dane demonstracyjne hurtowni: milion zamówień z 9 miesięcy 2026 (`orders.csv`), 2 000 klientów (`customers.json`), 300 produktów (`products.xlsx`). W danych ukryto: 12 rabatów 35–45% (9 u handlowca H07), 8 cen poniżej kosztu, 6 gigantycznych ilości, 5 zamówień nocnych, 4 duplikaty, 3 nowych klientów kupujących identycznie i 2 klientów z nagłym wzrostem zamówień we wrześniu. Pliki powstają w `input/` tylko wtedy, gdy ich tam nie ma albo gdy `regenerate=True`.

## settings
Wejście — `AnomalySettings` (`n_orders`, `seed`, `regenerate`).

## generator
Wyjście bloku — ten generator, podawany do `OrderDataLoader`.

## ensure
Tworzy brakujące pliki; zwraca `True`, gdy coś zapisał.

## plant_anomalies
Wstawia nieprawidłowości pojedynczych zamówień.

## clones
Trzech klientów o identycznym wzorcu zakupów.

## bursts
Dwóch klientów z nagłym wzrostem zamówień w ostatnim miesiącu.
