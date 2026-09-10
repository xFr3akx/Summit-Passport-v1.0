# Aktualizacja 0.3.1 — 10.09.2026

Zrealizowano uwagi po teście etapu 3: maska kraju i ograniczenie przesuwania, osobne HOME, uproszczona karta, formularz wizyty, zapis i edycja w dzienniku, zdjęcia, ustawienia źródeł oraz More countries coming soon. Poprzednią wersję użytkownik uruchomił na swoim telefonie.

Walidacja: poprzedni zestaw UI PASS; dodatkowy test `scripts/test_visits.cjs` PASS (anulowanie, zapis, edycja, dwie wizyty jednego miejsca, trwałość po odświeżeniu, zdjęcie w trybie przeglądarki, błędny link AllTrails, filtry, HOME, maska, rozdzielenie dzienników krajów, ustawienia prawne i szerokość 320 px). `scripts/test_migration.py` PASS: SQL migracji v1→v2 zachowuje wizytę i notatkę, klucze obce i zgodność nowej instalacji.

Gradle assembleDebug, testDebugUnitTest i lintDebug: BUILD SUCCESSFUL. Lint: 0 błędów; istniejące ostrzeżenia dotyczące tekstów do tłumaczenia i ustawień transferu danych. APK podpisany tym samym lokalnym kluczem co dostarczony APK 0.3.0. Podpis sprawdzono. Katalog wewnątrz APK ma niezmieniony SHA-256 i 1065 punktów.

SHA-256 APK 0.3.1: `b2d6c4d2535465de302610c418eeb5510e4c4f38187225a524257bc62183ebe1`.

Nie wykonano jeszcze testu tej aktualizacji na telefonie. Wybór zdjęcia przez Androida, orientacja EXIF i aktualizacja istniejącej instalacji wymagają sprawdzenia na urządzeniu; test browserowy nie zastępuje WebView ani natywnego wyboru zdjęć. Migrację SQL sprawdzono na SQLite, nie na emulatorze Androida. Zdjęcia są kopiowane i zmniejszane lokalnie (do około 1600 px), do 10 na wizytę. Brak eksportu, usuwania całych wizyt i pełnych kolekcji w tej wersji.

Granice Natural Earth są uproszczoną maską wizualną. Widok nie jest narzędziem do dokładnego ustalania przebiegu granicy. Znaczniki bazy i atrakcji zachowują zapisane współrzędne. Podkład OSM nadal wymaga internetu. HOME jest osobnym znacznikiem; po przesunięciu poza ekran można do niego wrócić stale widocznym przyciskiem.

---

# Etap 3 — raport odbioru, 10.09.2026

Etap 3 zakończony. Baza pozostaje zamrożona. Near Me jest odłożone do etapu 7.

## Sprawdzone

- Walidacja katalogu: 2263 miejsca, z czego 1065 z publikowanymi współrzędnymi (451 PL / 614 DE). Identyfikatory, współrzędne i źródła odpowiadają zamrożonemu katalogowi. Pozostałe 1198 miejsc nie otrzymało zastępczych współrzędnych.
- Automatyczne testy interfejsu w Edge/Playwright: motywy jasny/ciemny i ich zapamiętanie, wybór kraju, wyszukiwanie, kategorie, filtr nieodwiedzonych, puste wyniki, lista i karta punktu, lokalne filtrowanie bez sieci, brak poziomego przepełnienia przy 390 × 844. Brak błędów JavaScript.
- Wizualna kontrola ekranów startowych Light/Dark i mapy; grupowanie znaczników ogranicza nakładanie symboli.
- Gradle 8.9 / JDK 17: `:app:assembleDebug :app:testDebugUnitTest :app:lintDebug` — BUILD SUCCESSFUL.
- Istniejący test jednostkowy szkieletu odznak: 1 test, 0 błędów. Test dotyczy obecnego szkieletu 12 poziomów; nie zatwierdza dodatkowego poziomu względem 11 wskazanych przez użytkownika. Rozbieżność opisana w ROADMAP.md.
- Android Lint: 0 błędów, 3 ostrzeżenia — konfiguracja transferu danych na Androidzie 12+ oraz dwa teksty ekranu ładowania wymagające przeniesienia do zasobów przed lokalizacją.
- Podpis APK zweryfikowany przez apksigner (v2). Katalog odczytany z gotowego APK: 2263 miejsca, 1065 punktów mapy, zgodne liczby PL/DE.

## Artefakt

Testowy APK: `Summit_Passport_Etap_3.apk`, wersja 0.3.0, Android 8.0+.

SHA-256: `72fe35ecba353d0832d796155e02b3429fecbb6373e867cbc02d23c556c5f411`.

APK podpisano lokalnym kluczem deweloperskim. Klucz nie jest publikowany w repozytorium. Kolejne kompilacje z innego klucza mogą wymagać ponownej instalacji zamiast aktualizacji.

## Granice weryfikacji i dalsza praca

Nie przeprowadzono instalacji na fizycznym telefonie ani testu Android WebView na urządzeniu. Testy przeglądarkowe nie zastępują tych kontroli. Etap 6 obejmuje testy urządzenia, trwałości danych i końcowego APK.

Podkład OpenStreetMap wymaga internetu; katalog jest lokalny. Nie ma pobierania całych map offline. Jedynym uprawnieniem aplikacji jest INTERNET.

Odwiedziny, zdjęcia, dziennik, kolekcje i propozycje kolejności odwiedzin czekają na etap 4. Filtr odwiedzonych korzysta z istniejących danych SQLite; scenariusz filtra sprawdzono na danych testowych przeglądarki. Pełne odznaki, języki oraz eksport/import czekają na etap 5. Zakładki przyszłych funkcji pokazują informację o planowanym etapie.

Po tym etapie praca zostaje zatrzymana do omówienia kolejnego zakresu.
