Wczytuje zamówienia (CSV, identyfikatory jako `category`, żeby milion wierszy zmieścił się w pamięci kontenera), klientów (JSON) i produkty (Excel), robi Data Scan i łączy wszystko w jedną tabelę z ceną netto i wartością zamówienia.

## folders
Wejście — `ProjectFolders`.

## reader
Wejście — `TableReader`.

## generator
Wejście — `DemoOrderData`.

## scanner
Wejście — `DataScanner`.

## dataset
Wyjście bloku — `OrderDataset`.

## join
Dołącza segment klienta, cenę katalogową i koszt produktu; liczy `net_price` i `value`.
