# Summit Passport

Etap 1 — natywny szkielet Android, lokalne dane, Polska i Niemcy.

## Dostępne
- Wybór kraju; nawigacja kraju dopiero po wyborze.
- Motyw System / Light / Dark zapisany lokalnie.
- Szkielet ekranów Mapa, Kolekcje, Dziennik, Osiągnięcia.
- SQLite: katalog, wiele wizyt jednego miejsca, trwałe daty odblokowania.
- 12 poziomów każdej rodziny osiągnięć.

## Stan danych i grafiki
Końcowy katalog NIE jest jeszcze zaimportowany. Źródłem ma być zamrożona baza PL/DE + 273 zaakceptowane dodatki (154 PL, 119 DE) z rozmowy „Paszport szczytów Europy”, 08.09.2026. Potrzebne są rzeczywiste pliki rekordów; same liczniki i specyfikacja nie wystarczają. Bez wymyślonych współrzędnych i testowych miejsc w produkcji.
Logo L4, tło T4, odznaki A1 i symbole S1 są zaakceptowanym kierunkiem. Ten szkielet nie zawiera jeszcze finalnych zasobów graficznych ani silnika mapy. Progi liczbowe odznak pozostają do ustalenia.

## Budowanie
JDK 17, Android SDK 35, Gradle 8.9. Uruchom `gradle :app:assembleDebug :app:testDebugUnitTest :app:lintDebug`.
Repozytorium nie zawiera jeszcze Gradle Wrapper; użyj wskazanej wersji Gradle. GitHub Actions instaluje ją i publikuje testowy APK po poprawnym buildzie.
Zgodność narzędzi: https://developer.android.com/build/releases/agp-8-7-0-release-notes

## Następne etapy
1. Dostarczenie i walidacja zamrożonego katalogu (ID, regiony, współrzędne, duplikaty).
2. Mapa, szczegóły miejsc i formularz wielu wizyt.
3. Kolekcje i naliczanie osiągnięć, zasoby graficzne Light/Dark.
4. GPS, proponowane trasy, zdjęcia, eksport/import i testy na telefonie.

Brak kont, chmury, telemetrii i uprawnień lokalizacji na tym etapie. APK debug nie jest wydaniem do sklepu.
