Przepuszcza wszystkie zamówienia przez reguły zamówień i wzorce klientów, mierzy czas każdego kroku i zbiera listę do sprawdzenia: zamówienia z powodami, liczniki reguł, koncentrację u handlowców, klony i nagłe zmiany.

## dataset
Wejście — `OrderDataset`.

## rules
Wejście — `OrderRules`.

## patterns
Wejście — `CustomerPatterns`.

## findings
Wyjście bloku — `AnomalyReport`, liczony raz.

## flagged_table
Tabela oznaczonych zamówień z powodami i stratą.

## rep_rows
Udział handlowców w podejrzanych cenach i rabatach vs ich udział we wszystkich zamówieniach.
