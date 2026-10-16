Zapisuje dane, które dostaje, do pliku Parquet czytanego przez Power BI i zwraca pełną ścieżkę tego pliku. W tym projekcie dostaje tabelę podejrzanych zamówień z `FindingsPowerBiTable` po każdym kliknięciu przycisku „Eksportuj do Power BI” na stronie `PodejrzaneZamowienia` i zapisuje ją do `output/powerbi/podejrzane_zamowienia.parquet`; ścieżka trafia do `Main` (`plik_power_bi`). To blok z szablonu CatNip *Templates → Block Template → Data → Power BI Export* z ustawioną ścieżką pliku.

Przyjmuje DataFrame, tabelę pyarrow, słownik kolumn albo listę słowników / rekordów `@dataclass`, sprowadza typy kolumn do tych, które Power BI rozumie, kompresuje Snappy i zapisuje plik atomowo — Power BI w trakcie odświeżania widzi albo stary plik, albo nowy, nigdy w połowie zapisany.

## Podłączenie Power BI (raz)

1. Uruchom przepływ w CatNip (Code Run) i kliknij **Eksportuj do Power BI**. W konsoli pojawi się ścieżka pliku i gotowe zapytanie Power Query (`let Source = Parquet.Document(File.Contents("C:\…\output\powerbi\podejrzane_zamowienia.parquet")) in Source`).
2. W Power BI Desktop: *Pobierz dane → Puste zapytanie → Edytor zaawansowany*, zastąp całą treść tym zapytaniem (to samo jest w pliku `output/powerbi/podejrzane_zamowienia.pq`) i kliknij *Gotowe*.

Nie wklejaj ścieżki w *Pobierz dane → Parquet → Adres URL* — to pole przyjmuje tylko adres w sieci i odpowiada „Nieprawidłowy identyfikator URI: nie można przeanalizować nazwy hosta”.

**Uruchomienie w Dockerze.** W kontenerze plik leży w `/app/output/powerbi/…` — takiej ścieżki Power BI nie otworzy. CatNip przekazuje kontenerowi, gdzie jest `/app` na Twoim komputerze (`CATNIP_HOST_WORKDIR`), i blok wypisuje oraz zapisuje do zapytania właśnie tę ścieżkę. Gdy tej informacji nie ma (starsza wersja CatNip), blok mówi, gdzie plik leży względem folderu projektu.

Potem wystarczy: kliknąć przycisk w raporcie CatNip → w Power BI **Odśwież**.

**Odświeżanie w usłudze Power BI (w chmurze)** nie widzi pliku na tym komputerze bez bramy danych (gateway). Jeśli raport ma się odświeżać sam w usłudze, ustaw `output_path` na folder OneDrive/SharePoint synchronizowany z tym komputerem i podłącz Power BI do linku SharePoint pliku — blok sam podpowie to w konsoli, gdy zobaczy ścieżkę OneDrive.

## data
Wejście — wiersze do eksportu (tu: `FindingsPowerBiTable.table`). Uzupełnia je generator; zostaw domyślne `None`.

## output_path
Domyślnie `'output/powerbi/podejrzane_zamowienia.parquet'`. Gdzie Power BI czyta dane. Ścieżka względna jest liczona od folderu, w którym działa przepływ (w CatNip — folder projektu, w Dockerze `/app`); blok zawsze wypisuje i zwraca ścieżkę pełną, bo tę podaje się Power BI. Zmiana ścieżki wymaga zmiany źródła w Power BI. W trybie `folder` to folder (końcówka `.parquet` jest pomijana).

## mode
Domyślnie `'overwrite'`. `'overwrite'`: jeden plik zastępowany przy każdym kliknięciu — Power BI zawsze pokazuje ostatni eksport. `'folder'`: każde kliknięcie dodaje nowy plik `part-<data>-<godzina>-<id>.parquet`, a w Power BI łączy się je przez *Pobierz dane → Folder → Połącz* (albo plik `.pq` folderu) — historia eksportów; kolumna `Wyeksportowano` odróżnia wtedy kolejne eksporty.

## timestamp_timezone
Domyślnie `'UTC'`. Power BI nie ma w Parquet daty ze strefą czasową, więc kolumna ze strefą jest zapisywana jako zwykła data i godzina w tej strefie (`'UTC'` albo np. `'Europe/Warsaw'`). Kolumny bez strefy — jak `Data` i `Wyeksportowano` w tym projekcie — są zapisywane bez zmian, więc tu ustawienie nie ma wpływu.

## on_schema_change
Domyślnie `'warn'`. Co zrobić, gdy kolumny różnią się od pliku, który już jest: `'warn'` zapisuje i wypisuje, które kolumny dodano, usunięto albo zmieniły typ; `'error'` odmawia i nic nie zapisuje (zalecane, gdy raport w Power BI jest już zbudowany); `'ignore'` nie porównuje.

## compression
Domyślnie `'snappy'`. Kodek Parquet; Snappy Power BI czyta na pewno. Zmieniaj tylko po sprawdzeniu, że Twój Power BI czyta wybrany kodek.

## write_query
Domyślnie `True`. Zapisuje obok danych zapytanie Power Query (M), które je wczytuje: `podejrzane_zamowienia.pq` (albo `<folder>.pq` w trybie `folder`).

## retries
Domyślnie `20` (≥ 0). Ile razy ponowić podmianę pliku, gdy trzyma go inny program — zwykle Power BI w trakcie odświeżania. Po ostatniej próbie eksport kończy się czytelnym komunikatem i nie zostawia plików tymczasowych.

## retry_delay
Domyślnie `0.5` s (> 0). Przerwa między próbami; razem z `retries` daje ok. 10 s czekania.

## path
Wyjście — pełna ścieżka zapisanego pliku (w trybie `folder` — nowego pliku części). Metoda `path()` wykonuje cały eksport.

## Co jest zmieniane po drodze

Każda zmiana jest wypisywana w konsoli z nazwą kolumny: znaczniki czasu w nanosekundach → mikrosekundy (precyzja Power BI); liczby bez znaku → 64-bitowe ze znakiem; kolumny kategorii → ich wartości; czas trwania → sekundy; listy i struktury → tekst JSON; kolumna bez żadnej wartości → tekst. Nazwy kolumn muszą być niepuste i unikalne **bez względu na wielkość liter**.

## Pakiety

`pyarrow` i `pandas` (są w `requirements.txt`).
