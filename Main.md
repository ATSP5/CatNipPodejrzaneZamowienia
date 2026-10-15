Punkt wejścia demo „Które zamówienia są podejrzane?”. `AnomalySettings` → generator, reguły i wzorce klientów; foldery, czytnik, Data Scan → `OrderDataLoader` → `AnomalyDetector` → strona `PodejrzaneZamowienia` w zakładce Output. Subskrybuje akcję `eksport`: każde kliknięcie „Zapisz listę do CSV” tworzy `FindingsCsvWriter` i zapisuje plik w `output/`. Pierwsze uruchomienie generuje milion zamówień (kilka sekund); kolejne czytają gotowe pliki z `input/`.

## result
Wejście — wyjście `show` strony raportu.

## zapisany_csv
Wejście — ścieżka CSV zapisanego po kliknięciu przycisku.
