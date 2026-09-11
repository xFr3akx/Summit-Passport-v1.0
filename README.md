# Summit Passport 0.5.0

[Pobierz APK](https://github.com/xFr3akx/Summit-Passport-v1.0/raw/refs/heads/main/downloads/Summit_Passport_0.5.0.apk)

Eksport/import wizyt, ocen, zdjęć, własnych list i ustawień przez lokalny ZIP. Podsumowanie przed importem; istniejące wpisy nie są nadpisywane. Dark domyślny, Light do wyboru, bez System. Instrukcje: BACKUP.md, UPDATES.md. Testy urządzenia są zaplanowane w punkcie 6; konflikt istniejącej instalacji wymaga dalszej diagnozy.

---

# Summit Passport 0.4.2

[Pobierz APK 0.4.2](https://github.com/xFr3akx/Summit-Passport-v1.0/raw/refs/heads/main/downloads/Summit_Passport_0.4.2.apk)

Oceny 1–5 gwiazdek, podsumowanie wizyty z symbolem kategorii, usuwanie pojedynczej wizyty z potwierdzeniem oraz powrót do widoku głównego kolekcji po kliknięciu zakładki. Migracja zachowuje poprzednie wpisy bez przypisywania im oceny. Szczegóły kontroli: TESTING.md. Motyw System, konflikt instalacji i filtry edytora list pozostają na później.

---

# Summit Passport 0.4.1 — poprawka uruchamiania

[Pobierz aktualizację 0.4.1](https://github.com/xFr3akx/Summit-Passport-v1.0/raw/refs/heads/main/downloads/Summit_Passport_0.4.1.apk)

Naprawia błąd „Nie udało się wczytać katalogu” przy uruchamianiu 0.4.0. Instaluj jako aktualizację, bez usuwania danych aplikacji. Zachowano ten sam klucz podpisu; wizyty, zdjęcia i listy nie są usuwane. Korzystaj z 0.4.1 zamiast 0.4.0.

---

# Summit Passport 0.4.0 — etap 4

[Pobierz APK 0.4.0](https://github.com/xFr3akx/Summit-Passport-v1.0/raw/refs/heads/main/downloads/Summit_Passport_0.4.0.apk)

Kolekcje z postępem (31 PL / 48 DE), lista odwiedzonych na górze, kolekcje szczytów według pasm i regionów, propozycje kolejności odwiedzin i własne edytowalne listy. Wizyty i zdjęcia pozostają w lokalnym dzienniku. Baza zamrożona: 451 PL + 614 DE. Podkład mapy wymaga internetu; kolekcje i listy są lokalne. Testy i ograniczenia opisano w TESTING.md.

---

# Aktualizacja 0.3.1

[Pobierz aktualny APK](https://github.com/xFr3akx/Summit-Passport-v1.0/raw/refs/heads/main/downloads/Summit_Passport_0.3.1.apk)

Mapa tylko wybranego kraju, HOME Overath / Jastrzębie-Zdrój, zapisywanie wielu wizyt, pogoda, data, link AllTrails, dystans, czas, suma podejść, notatki i zdjęcia. Edycja wizyt w Dzienniku. Źródła w osobnym podpunkcie ustawień. Katalog atrakcji pozostaje zamrożony. Raport i ograniczenia: TESTING.md.

---

# Summit Passport

Etap 3 — Android, lokalny katalog Polski i Niemiec, motywy i mapa.

## Dostępne
- Wybór kraju; nawigacja kraju dopiero po wyborze.
- Motyw System / Light / Dark zapisany lokalnie.
- Mapa 1065 punktów: 451 PL i 614 DE; szczegóły, lista, grupowanie znaczników i filtry.
- Logo L4, tło w kierunku T4 i wektorowe adaptacje symboli S1.
- Szkielety Kolekcji, Dziennika i Odznak; ich funkcje należą do kolejnych etapów.
- SQLite: katalog, wiele wizyt jednego miejsca, trwałe daty odblokowania.
- 12 poziomów każdej rodziny osiągnięć.

## Stan danych i grafiki
Baza została zamrożona decyzją użytkownika. `app/src/main/assets/ui/catalog.json` zawiera 2263 miejsca, w tym 1065 punktów do mapy. Pozostałe 1198 miejsc nie otrzymuje zastępczych współrzędnych; 321 szkiców grup odwiedzin pozostaje w materiale roboczym. `data/catalog_source.json` zachowuje wszystkie 2789 wystąpień z obu PDF-ów, w tym 273 dodatki. Katalog nie jest ogłoszony kompletnym.
Przy pierwszym uruchomieniu i aktualizacji rekordy mapy są importowane do SQLite bez usuwania istniejących wizyt. Brak kodu administracyjnego jest zapisany jako pusty tekst, nie zgadywany kod. Progi liczbowe odznak pozostają do ustalenia.

Interfejs i biblioteki Leaflet są dołączone do APK. Mapa pobiera wyłącznie aktualnie oglądane kafelki OpenStreetMap; korzysta z pamięci podręcznej WebView i pokazuje atrybucję. Podkład wymaga internetu przy pierwszym wyświetleniu danego obszaru. Katalog i filtrowanie są lokalne. Nie ma GPS ani uprawnień lokalizacji.

## Budowanie
JDK 17, Android SDK 35, Gradle 8.9. Uruchom `gradle :app:assembleDebug :app:testDebugUnitTest :app:lintDebug`.
Repozytorium nie zawiera jeszcze Gradle Wrapper; użyj wskazanej wersji Gradle. GitHub Actions instaluje ją i publikuje testowy APK po poprawnym buildzie.
Zgodność narzędzi: https://developer.android.com/build/releases/agp-8-7-0-release-notes

## Następne etapy
Etap 3: motywy, logo, symbole i mapa. Po nim omawiamy dalsze kroki. Near Me należy do etapu 7. Propozycje wycieczek będą uporządkowanymi listami miejsc, zgodnie z `data/VISIT_PROPOSALS.md`.

Brak kont, chmury, telemetrii i uprawnień lokalizacji na tym etapie. APK debug nie jest wydaniem do sklepu.
