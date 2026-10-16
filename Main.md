Punkt wejścia demo „Które zamówienia są podejrzane?”. `AnomalySettings` → generator, reguły i wzorce klientów; foldery, czytnik, Data Scan → `OrderDataLoader` → `AnomalyDetector` → strona `PodejrzaneZamowienia` w zakładce Output. Subskrybuje dwie akcje strony: `eksport` — każde kliknięcie „Zapisz listę do CSV” tworzy `FindingsCsvWriter` i zapisuje plik w `output/`; `powerbi` — każde kliknięcie „Eksportuj do Power BI” tworzy `FindingsPowerBiTable` i `PowerBiExport` i nadpisuje `output/powerbi/podejrzane_zamowienia.parquet`. Pierwsze uruchomienie generuje milion zamówień (kilka sekund); kolejne czytają gotowe pliki z `input/`.

## result
Wejście — wyjście `show` strony raportu.

## zapisany_csv
Wejście — ścieżka CSV zapisanego po kliknięciu przycisku.

## plik_power_bi
Wejście — pełna ścieżka pliku Parquet dla Power BI zapisanego po kliknięciu „Eksportuj do Power BI”.
