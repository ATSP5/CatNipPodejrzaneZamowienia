Strona „Które zamówienia są podejrzane?”: KPI (ile przejrzano, ile do sprawdzenia, strata), odpowiedź, trafienia reguł, tabela zamówień z filtrem reguły i szczegółami klikniętego wiersza, koncentracja u handlowców, klony i nagłe zmiany, Data Scan z czasem każdego kroku. Dwa przyciski pod odpowiedzią: „Zapisz listę do CSV” (akcja `eksport`, Live) uruchamia `FindingsCsvWriter`, a „Eksportuj do Power BI” (akcja `powerbi`, Live) uruchamia `FindingsPowerBiTable` → `PowerBiExport`. Oba działają przy każdym kliknięciu, dopóki strona jest aktywna, i eksportują pełną listę podejrzanych zamówień (niezależnie od filtra reguły na stronie).

## findings
Wejście — `AnomalyReport`.

## narrator
Wejście — `AnomalyNarrator`.

## formatter
Wejście — `PlnFormat`.

## show
Wyjście — pokazuje stronę w zakładce Output.

## eksport
Wyjście akcji — przekazuje `AnomalyReport` do `FindingsCsvWriter` przy każdym kliknięciu.

## powerbi
Wyjście akcji — przekazuje `AnomalyReport` do `FindingsPowerBiTable` przy każdym kliknięciu „Eksportuj do Power BI”; plik dla Power BI trafia do `output/powerbi/podejrzane_zamowienia.parquet`.

## on_powerbi
Pokazuje komunikat „Eksportuję … zamówień do Power BI” i zwraca `self.findings` — to, co dostaje wyjście `powerbi`.
