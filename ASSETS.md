# Zasoby etapu 3

- Logo L4: wektorowa adaptacja zatwierdzonej sylwetki gór i litery S. Kolory dopasowują się do motywu; forma pozostaje wspólna. Kod w `app/src/main/assets/ui/icons.js`, ikona Android w `app/src/main/res/drawable/ic_launcher.xml`.
- Symbole S1: 16 wektorowych adaptacji zapisanych w `icons.js`. Mapa wykorzystuje rodzaje występujące w zamrożonym katalogu. Kolory kategorii pozostają jednakowe w Light/Dark. Odwiedzone miejsca mają zielonkawe koło oraz znak ✓.
- Tło: `app/src/main/assets/ui/landscape.png`, przygotowane narzędziem wbudowanym imagegen na podstawie zatwierdzonej makiety. Dark korzysta z tego samego krajobrazu z nakładką przyciemniającą w CSS.

Prompt użyty do przygotowania tła:

> Create one production mobile application background image, portrait 1024x1536, derived from the LIGHT left-hand alpine forest mist landscape of this reference. Full bleed photorealistic alpine jagged mountain range across middle, evergreen forest in foreground, mist in valley, pale warm ivory sky in upper 35 percent for UI overlay. Preserve the approved T4 landscape mood and palette. Remove ALL phones, frames, logos, labels, text, UI cards, flags and controls. Landscape ONLY, not a mockup or side-by-side. Dark mode will use a code overlay on this same photo so do not create a dark panel. Save the resulting asset locally.

Biblioteki są dołączone do APK: Leaflet 1.9.4 (BSD-2-Clause), Leaflet.markercluster 1.5.3 (MIT). Teksty licencji są w `app/src/main/assets/ui/vendor`. Kafelki mapy: © OpenStreetMap contributors, ODbL. Weryfikacja współrzędnych: GeoNames, CC BY 4.0. Obrazy kafelków są pobierane na żądanie, bez pobierania pakietów offline.

## Granice i bazy HOME (0.3.1)

`app/src/main/assets/ui/boundaries.json`: wybrane geometrie PL/DE z [Geo Countries](https://github.com/datasets/geo-countries/blob/main/data/countries.geojson), pobrane 10.09.2026; źródło [Natural Earth — public domain](https://www.naturalearthdata.com/about/terms-of-use/). Nie modyfikują katalogu atrakcji.

HOME potwierdzone przez użytkownika: Overath (50.9320015, 7.2839042), [OSM relation 173104](https://www.openstreetmap.org/relation/173104); Jastrzębie-Zdrój (49.9519085, 18.6023614), [OSM relation 2415561](https://www.openstreetmap.org/relation/2415561). Współrzędne centrów miast uzyskano z Photon 10.09.2026 w ramach zgody na zapytania.
