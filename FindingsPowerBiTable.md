Przygotowuje listę podejrzanych zamówień do eksportu do Power BI. Bierze tabelę `flagged` z `AnomalyReport` — te same kolumny, które widać w raporcie i w CSV — i poprawia to, co Power BI odczytałby źle: kolumna `Data` z raportu jest tekstem (`"2026-01-02 10:15"`), więc zamienia ją na prawdziwą datę i godzinę, a na końcu dopisuje kolumnę `Wyeksportowano` z czasem eksportu. Dzięki temu w Power BI można filtrować i grupować po dacie, a na raporcie pokazać, z kiedy są dane.

Blok istnieje osobno, żeby wybór i kształt danych dla Power BI był w jednym miejscu, a sam zapis pliku (`PowerBiExport`) pozostał ogólny. Wejście `report` jest podłączone do akcji `powerbi` strony `PodejrzaneZamowienia`, wyjście `table` do `PowerBiExport.data`. Uruchamia się przy każdym kliknięciu przycisku „Eksportuj do Power BI”.

## report
Wejście — `AnomalyReport` przekazany przez akcję `powerbi` raportu (w chwili kliknięcia). Używana jest tylko jego tabela `flagged`.

## table
Wyjście — `pandas.DataFrame` z kolumnami: `Zamówienie`, `Data` (data i godzina), `Klient`, `Segment`, `Produkt`, `Handlowiec`, `Ilość`, `Cena`, `Rabat %`, `Wartość`, `Strata`, `Powody` (reguły rozdzielone przecinkami), `Liczba reguł`, `Wyeksportowano` (data i godzina eksportu, ta sama dla wszystkich wierszy). Kolejność wierszy jak w raporcie: najpierw najwięcej reguł, potem największa wartość. Data, której nie da się odczytać, staje się pusta, a nie zatrzymuje eksportu.

Nazwy kolumn zmieniaj ostrożnie: zapytania i wizualizacje w Power BI odwołują się do nich po nazwie (`PowerBiExport` ostrzeże o zmianie schematu).
