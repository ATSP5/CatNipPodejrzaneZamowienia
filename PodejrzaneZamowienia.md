Strona „Które zamówienia są podejrzane?”: KPI (ile przejrzano, ile do sprawdzenia, strata), odpowiedź, trafienia reguł, tabela zamówień z filtrem reguły i szczegółami klikniętego wiersza, koncentracja u handlowców, klony i nagłe zmiany, Data Scan z czasem każdego kroku. Przycisk „Zapisz listę do CSV” (akcja `eksport`, Live) uruchamia `FindingsCsvWriter`.

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
