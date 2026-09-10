# Weryfikacja współrzędnych — katalog roboczy

Praca trwa. `completion_status.json` zawiera aktualne liczby; `complete: false` oznacza, że katalog nie jest ostatecznym wydaniem bazy. Plik źródłowy zachowuje wszystkie 2789 wystąpień z obu PDF-ów. Liczba miejsc po scaleniu jest robocza.

`catalog_working.json` przechowuje encje po przeglądzie duplikatów, nazwy źródłowe, trwałe ID i wyniki sprawdzania położenia. `source_entity_links.json` łączy każde wystąpienie źródłowe z encją. `entity_id_redirects.json` zachowuje przekierowania ID przy scaleniu. Oryginalne nazwy i kategorie nie są usuwane z materiału źródłowego.

## Znaczenie statusów

* `reviewed_source_context`: ręcznie wybrany obiekt OSM na podstawie nazwy, rodzaju i lokalnego kontekstu podregionu z PDF. Uzasadnienie jest zapisane w `coordinate_review` i `coordinate_decisions.json`.
* `cross_checked_osm_geonames`: zgodna nazwa i rodzaj w regionie źródłowym oraz punkt GeoNames w odległości do 1 km. Wybrane współrzędne pochodzą z OSM. Tolerancja służy do porównania źródeł i nie oznacza dokładności pomiaru.
* `automatic_match_needs_review`: kandydat wyszukany automatycznie, wymagający przeglądu; `map_ready: false`.
* `coordinate_sources_disagree`: źródła różnią się o ponad 2 km, wymagana kontrola tożsamości obiektu; `map_ready: false`.
* `needs_location_research`: brak zaakceptowanego dopasowania. Nie oznacza braku istnienia miejsca.
* `identity_requires_clarification`: podobna nazwa i położenie nie rozstrzygają, który obiekt opisuje PDF. Taki rekord pozostaje poza mapą, nawet gdy wyszukiwarki zwracają zgodne współrzędne.
* `ordered_places_review_required`: źródłowy szlak lub doświadczenie oczekujące na przegląd jako propozycja kolejności odwiedzin. Nie wymaga geometrii szlaku; model opisuje `VISIT_PROPOSALS.md`.

Obecność liczb latitude/longitude sama nie uprawnia do publikacji punktu. Import mapy musi sprawdzać `map_ready`. Liczniki końcowe i osiągnięcia wymagają zakończenia deduplikacji całego katalogu.

Dobór kandydatów uwzględnia nazwę dosłowną lub dwujęzyczną; dopuszcza również inny zapis nazwy OSM w promieniu 300 m od kandydata GeoNames. W obu przypadkach obowiązuje zgodność rodzaju i obszaru poszukiwań. To pomoc w wyszukiwaniu, a nie dowód tożsamości; niejednoznaczne wyniki wymagają przeglądu. OSM i GeoNames mogą korzystać ze wspólnych danych, więc ich zgodność nie jest niezależnym pomiarem terenowym.

## Rodzaj położenia

`osm_point` wskazuje punkt obiektu w OSM. `representative_point_not_entrance` jest punktem reprezentacyjnym obszaru/budynku — nie deklaracją wejścia, parkingu ani bezpiecznego dojścia. Punkty jaskiń mogą oznaczać wejście, jeżeli OSM klasyfikuje je jako `cave_entrance`. Dane nie potwierdzają legalnego dostępu ani bieżącej dostępności atrakcji.

`country` jest krajem kolekcji w dostarczonym katalogu. `location_country` pochodzi z lokalizacji OSM; może być inny dla miejsc przygranicznych, np. Pilska. Nazwa województwa/landu `admin_region_name` pochodzi z wyniku geokodowania, a nie ze starej grupy krajobrazowej PDF. Nie wyznaczono jeszcze pełnych granic ani kodów administracyjnych.

`coordinate_rejections.json` dokumentuje rozpoznane błędne trafienia. `coordinate_alias_candidates.json` zawiera kandydatów do dalszego scalenia, gdy różne nazwy wskazują ten sam obiekt OSM; wspólna współrzędna nie powoduje automatycznego scalenia.

## Źródła i licencje

* Współrzędne i metadane OSM: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0. Wyszukiwanie przez [Photon](https://photon.komoot.io), z zapisem URL i daty pozyskania. Ekran mapy oraz eksport wykorzystujący te dane muszą zachować atrybucję i warunki ODbL.
* Dane porównawcze: [GeoNames](https://www.geonames.org/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), pobrane z oficjalnego zrzutu PL/DE. Przechowywany jest identyfikator i URL rekordu.
* PDF-y użytkownika identyfikuje `manifest.json`. Zewnętrzne zapytania zawierają nazwy miejsc i obszar poszukiwań, bez wizyt i zdjęć użytkownika.
