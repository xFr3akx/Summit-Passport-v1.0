# Germany REVIEW — ręczne rozstrzygnięcie 61 wpisów

Zakres: wszystkie 61 rekordów oznaczonych wcześniej `REVIEW` w pełnym audycie Niemiec.

## Wynik

- **READY: 8**
- **REPRESENTATIVE: 46**
- **UNRESOLVED: 7**
- **REVIEW: 0**
- Produkcyjny `catalog.json` nie został zmieniony.

## READY

1. Clemensberg — OSM `N323202958` — 51.2546, 8.5672
2. Moselblick Alken — 50.247250, 7.451203; punkt potwierdzony przez Traumpfade/Outdooractive, do końcowego cross-checku OSM
3. Brauselay — OSM `W1442003722` — 50.1425144, 7.1839825
4. Hubertushöhe — OSM `N10770721162` — 50.140858, 7.155444
5. Mühlsteinhöhlen — OSM `N926982906` — 50.1935448, 6.7597951
6. Sandkopf — OSM `N2658969413` — 49.7332368, 7.098109
7. Himmelspforte — 49.945927, 7.117198; punkt potwierdzony przez regionalne źródło turystyczne, do końcowego cross-checku OSM
8. Steinwand — OSM `N272625017` — 50.52226, 9.86459

## REPRESENTATIVE

Hohe Wart; Federath / Bergische Höhen; Kettners Weiher; Wupperberge; Nachtigallental; Narzissenwiesen; Vulkanpark; Mayener Grubenfeld; Elztal; Gasseschlucht; Giebelwald; Erlebnisberg Kappe; Kyrillpfad; Hannoversche Klippen; Rheinhöhen Braubach; Bleidenberg; Schrumpftal; Pyrmonter Felsen; Elzbachtal; Buchsbaum-Wanderpfad; Beilstein; Baybachklamm; Ehrbachklamm; Hahnenbachtal; Zeller Schwarze Katz Weinberge; Kanonenbahn; Wolfer Schanzen; Ürziger Felsen; Piesporter Goldtröpfchen; Hammelsberg; Baumwipfelpfad Saarschleife; Brockenbahn; Bodetal; Kernberge; Ruhestein; Gaishöll-Wasserfälle; Polenztal; Dresdner Elbhänge; Oybin; Steinernes Meer; Höllental; Leutaschklamm / Geisterklamm; Mittenwalder Altstadt; Neuendorfer Rummel; Havelhöhenweg; Stubbenkammer.

Dla tej grupy tożsamość miejsca została rozstrzygnięta, ale obiekt jest obszarem, trasą, doliną, zespołem lub kompleksem. Kolejny krok to przypisanie `coordinateRole=representative` albo `start` i konkretnego OSM/punktu wejścia bez udawania współrzędnej dokładnego obiektu punktowego.

## UNRESOLVED

1. Dörrebachklamm — brak wiarygodnego potwierdzenia obiektu o tej nazwie w oczekiwanym rejonie Hunsrück.
2. Moselblick Trier — nazwa zbyt ogólna; wiele niezależnych punktów widokowych.
3. Haberstein — FICHTELGEBIRGE — istnieje więcej niż jeden realny Haberstein w regionie.
4. Haberstein — FICHTELGEBIRGE - FELSEN / BURGEN — ten sam problem homonimii; brak danych pozwalających przypisać właściwy obiekt.
5. Steinerne Rinne — w regionie istnieje kilka różnych obiektów o tej nazwie.
6. Kreuzfelsen — znalezione homonimy nie dają bezpiecznego dopasowania do kontekstu Dreisessel / Osser.
7. Wattenmeer — zakres Sylt / Amrum / Helgoland jest zbyt szeroki na jeden kanoniczny punkt.

## Zasada dalszej pracy

- `READY` → cross-check OSM i staging.
- `REPRESENTATIVE` → dobrać reprezentatywny punkt lub start, zapisać rolę współrzędnej, następnie staging.
- `UNRESOLVED` → pozostawić na końcową listę wyjątków; nie zgadywać.

Pełne dane per rekord, wraz ze stable ID i notatkami decyzyjnymi, znajdują się w `data/germany_review_manual_resolution.json`.
