Reguły dla pojedynczego zamówienia — każda zwraca maskę True/False dla wszystkich zamówień naraz (wektorowo, milion wierszy w ułamku sekundy). Typowe wartości liczone są per produkt albo per segment, a odchylenia odpornie (mediana i MAD), więc kilka złych zamówień nie przesuwa samej normy.

## settings
Wejście — `AnomalySettings` (progi reguł).

## rules
Wyjście bloku — te reguły, podawane do `AnomalyDetector`.

## catalogue
Nazwa reguły → funkcja.

## below_cost
Cena netto po rabacie niższa niż koszt produktu.

## unusual_discount
Rabat wyższy od typowego dla segmentu o więcej niż `discount_gap_pp`.

## unusual_price
Cena daleko od typowej ceny produktu (`price_z`).

## unusual_quantity
Ilość wielokrotnie większa od typowej dla produktu (`quantity_z`).

## off_hours
Noc, późny wieczór albo niedziela.

## duplicate
To samo zamówienie (klient, produkt, ilość, cena, rabat) w ciągu `duplicate_minutes`.
