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
