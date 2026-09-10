# Propozycja wycieczki — decyzja użytkownika 08.09.2026

Proponowany szlak oznacza uporządkowaną grupę miejsc, czyli kolejność odwiedzin. Nie wdrażamy wyszukiwania szlaków, wyznaczania dróg ani geometrii przebiegu trasy.

Na karcie miejsca przycisk „Propozycja wycieczki” otwiera ponumerowaną listę. Każda pozycja prowadzi do karty konkretnego miejsca i pokazuje stan odwiedzenia. Przykład użytkownika: Malinów → Jaskinia Malinowska → Małe Skrzyczne → Skrzyczne. To przykład interakcji; skład i kolejność wymagają weryfikacji przy kuracji grup.

Model publikowanej propozycji: `id`, `title`, `country`, `anchor_place_ids`, `ordered_place_ids`, `description`, `review_status`. Odwołania używają trwałych ID miejsc. Lista musi zawierać co najmniej dwa różne istniejące miejsca. Propozycja nie jest osobnym odwiedzonym miejscem i nie zwiększa liczby POI ani liczników odznak.

Dotychczasowe źródłowe wpisy szlaków/ścieżek/doświadczeń są zachowane jako `suggested_visit_group` ze statusem `draft_from_source_requires_curation`. Puste `ordered_place_ids` oznacza brak opracowanej propozycji, nie gotową wycieczkę. Dopiero osobny przegląd ustali, które wpisy nadają się do tego modelu i jakie miejsca obejmują. Ogólnych nazw szlaków nie rozwijamy automatycznie w zgadywaną listę punktów.

W tej wersji nie podajemy wyliczonego czasu marszu ani odległości po szlaku. Współrzędne miejsc nadal służą do mapy i funkcji „Near me”.

## Implementacja 0.4.0

W pliku aplikacji `collections.json` opublikowano dwie ponumerowane propozycje: przykład użytkownika Malinów → Jaskinia Malinowska → Małe Skrzyczne → Skrzyczne oraz Brocken → Brockengarten. Każda odsyła do istniejących ID. Geograficzny kontekst sprawdzono w materiałach [Śląskie Travel](https://slaskie.travel/poi/3731/jaskinia-malinowska) i [Nationalpark Harz](https://www.nationalpark-harz.de/de/natur-erleben/brockengarten/). To zestawienia miejsc, bez wyznaczania dróg, czasów i odległości. Terminy wejścia do Brockengarten określa park.

W aplikacji `placeIds` odpowiada uporządkowanemu `ordered_place_ids`, a `anchorIds` — `anchor_place_ids`. Dla własnych list wszystkie miejsca są punktami wejścia do listy. Własne listy są przechowywane lokalnie w ustawieniach Androida, niezależnie od SQLite wizyt, maksymalnie 200 list po 100 różnych miejsc. Można je edytować, przestawiać elementy, kopiować propozycje i usuwać. Usunięcie listy nie usuwa wizyt. Nie ma automatycznej optymalizacji, GPS ani Near Me.
