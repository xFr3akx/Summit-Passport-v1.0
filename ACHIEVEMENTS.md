# Prezentacja 0.6.2

Lista pokazuje liczbę zdobytych progów / 11, niezależnie od bieżącej wartości metryki. Szczegóły zawierają opis reguły, grafikę po lewej, postęp i status/datę po prawej. Peak/Castle/Cave/Waterfall mają własne jednostki z odmianą PL i tłumaczeniami DE/EN. Progi i trwały rejestr przyznań nie zmieniły się.

# Odznaki — 0.6.1

Każda z 12 rodzin ma 11 poziomów: po 2 Bronze, Silver, Gold i Diamond, następnie Master z 1/2/3 gwiazdkami. Wyniki i nagrody liczymy osobno dla kraju. Collection Master ma nazwy Poland / Germany i progi do 50. Pełna tabela: ACHIEVEMENTS_PROPOSAL.md.

Każda wizyta aktualizuje wyniki. Miejsca w Peak/Explorer/Castle/Cave/Waterfall/Must See liczą się raz. Dystans, czas i podejścia sumują się ze wszystkich wizyt. Regional Explorer liczy pierwszą wizytę w dowolnym miejscu kolejnego województwa/landu. Collection Master wymaga odwiedzenia wszystkich miejsc danej kolekcji; własne kolejności nie są kolekcjami. Country Complete dotyczy procentu opublikowanego katalogu kraju.

Datę zdobycia ustalamy jako datę wizyty, przy której chronologicznie osiągnięto próg. Starsze wizyty również są przeliczane. Osobno zapisujemy moment pierwszego rozpoznania nagrody. Raz zdobyte nagrody oraz daty pozostają zapisane po edycji/usunięciu wizyty lub rozbudowie katalogu, choć bieżący licznik może spaść. Ponowne przeliczenie nie tworzy duplikatów i nie zmienia zapisanej daty. Wszystkie przekroczone poziomy, także kilka jednego dnia, są przyznawane.

Nagrody przechowuje SQLite (migracja v4 → v5). Eksport ZIP v2 zawiera achievements; import zachowuje lokalny rekord przy tym samym kluczu kraj/rodzina/poziom. Starsze kopie v1 nadal są obsługiwane i po imporcie uruchamiają obliczenie należnych odznak z wizyt. Błąd zapisu odznak jest wyświetlany w zakładce; ponowne otwarcie ponawia zapis.

Must See to redakcyjny zestaw startowy Summit Passport, po 30 wyróżnionych punktów PL i DE z dotychczasowego katalogu. Nie jest to oficjalny program ani obiektywny ranking. Zestaw można wyświetlić filtrem mapy. Wyższe progi tej i innych rodzin mogą wymagać rozbudowy bazy.

Metadane regionów i wyróżnień: app/src/main/assets/ui/achievement-places.json. Nazwy województw/landów z danych OSM ujednolicono; dla 12 istniejących obiektów granicznych zastosowano region po stronie wybranego kraju, według zweryfikowanego kontekstu źródłowej grupy. Nowe miejsca DE mają zgodne przypisanie GeoNames/OSM.
