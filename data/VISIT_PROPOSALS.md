# Propozycja wycieczki — decyzja użytkownika 08.09.2026

Proponowany szlak oznacza uporządkowaną grupę miejsc, czyli kolejność odwiedzin. Nie wdrażamy wyszukiwania szlaków, wyznaczania dróg ani geometrii przebiegu trasy.

Na karcie miejsca przycisk „Propozycja wycieczki” otwiera ponumerowaną listę. Każda pozycja prowadzi do karty konkretnego miejsca i pokazuje stan odwiedzenia. Przykład użytkownika: Malinów → Jaskinia Malinowska → Małe Skrzyczne → Skrzyczne. To przykład interakcji; skład i kolejność wymagają weryfikacji przy kuracji grup.

Model publikowanej propozycji: `id`, `title`, `country`, `anchor_place_ids`, `ordered_place_ids`, `description`, `review_status`. Odwołania używają trwałych ID miejsc. Lista musi zawierać co najmniej dwa różne istniejące miejsca. Propozycja nie jest osobnym odwiedzonym miejscem i nie zwiększa liczby POI ani liczników odznak.

Dotychczasowe źródłowe wpisy szlaków/ścieżek/doświadczeń są zachowane jako `suggested_visit_group` ze statusem `draft_from_source_requires_curation`. Puste `ordered_place_ids` oznacza brak opracowanej propozycji, nie gotową wycieczkę. Dopiero osobny przegląd ustali, które wpisy nadają się do tego modelu i jakie miejsca obejmują. Ogólnych nazw szlaków nie rozwijamy automatycznie w zgadywaną listę punktów.

W tej wersji nie podajemy wyliczonego czasu marszu ani odległości po szlaku. Współrzędne miejsc nadal służą do mapy i funkcji „Near me”.
