# Zamrożony katalog źródłowy — 08.09.2026

Zaimportowano oba dostarczone PDF-y w całości w zakresie głównych wykazów. Aneksy DUP nie zostały policzone ponownie.

| Kraj | Baza | Dodatki | Wystąpienia |
| --- | ---: | ---: | ---: |
| Polska | 984 | 154 | 1138 |
| Niemcy | 1532 | 119 | 1651 |
| Razem | 2516 | 273 | 2789 |

Kontrola ekstrakcji: 34/56 regionów oraz 264/209 podregionów bazowych, zgodnie z audytem. Wszystkie 2789 identyfikatorów źródłowych są różne. Dodatki mają osobną przestrzeń ID PL-ADD/DE-ADD.

catalog_source.json przechowuje wystąpienia źródłowe, nie gotowe unikalne miejsca. duplicate_candidates.json zawiera 200 grup równych nazw w obrębie kraju; nie jest listą zatwierdzonych scaleń. Te same nazwy mogą oznaczać różne miejsca. Zachowano oryginalne kategorie, regiony krajobrazowe, wysokości, numery audytowe i strony źródeł.

Brak współrzędnych, kodów administracyjnych, potwierdzonych trudności i geometrii tras w tych PDF-ach. Pola te pozostają puste. Katalog nie trafia jeszcze do tabeli places ani do liczników osiągnięć; zapobiega to naliczaniu duplikatów. Przy zamianie wystąpień na miejsca potrzebna jest trwała tabela source_id → canonical_place_id.

Nie dodano nowych miejsc spoza zamrożonej listy. Nazwy zachowano ze źródeł, również potencjalne literówki. manifest.json identyfikuje dostarczone PDF-y przez SHA-256.
