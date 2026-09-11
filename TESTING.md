# Kontrole 0.6.2

PASS: formularz nie-szczytu z wyborem dnia; zachowanie starszych ukrytych parametrów i załączników; trasa tekstowa i bezpieczne wyświetlanie znaków HTML; ikony pogody i parametrów; filtry dnia/oceny, sortowanie; nowa sesja zaczyna od kraju; przeładowanie języka zachowuje kraj; nawigacja; odznaki x/11 i jednostki.

PASS: regresje wizyt, Dziennika, kolekcji, przyznawania odznak, startu z opóźnionym skryptem, kopii UI i PL/DE/EN. Nowy test JVM sprawdza zapis/odczyt tekstu trasy w ZIP i limit 4000 znaków; dotychczasowe testy kopii ze zdjęciami zachowane. Android assembleDebug, testDebugUnitTest i lintDebug PASS. Obejrzano Light/Dark i szerokość 320 px. Nie wykonywano testu na fizycznym Androidzie.

# 0.6.1 — trwałe odznaki i Niemcy 1000

Gradle assembleDebug/testDebugUnitTest/lintDebug: BUILD SUCCESSFUL. 9 testów JVM: 7 BackupArchiveTest, 1 AchievementRecordsTest i 1 AchievementTierTest — bez błędów.

PASS: test_awards (daty historycznych wizyt, wszystkie przekroczone progi, unikalne miejsca vs sumy, kraje, trwałość po usunięciu wizyt i rozbudowie katalogu); test_achievements (zapis, restart, daty, usunięcie wizyt, Light/Dark); test_languages; regresje mapy, wizyt, kolekcji, startu, dziennika i kopii danych. Testy SQL potwierdziły migrację dat v4→v5, zachowanie dat przy duplikatach importu i wycofanie nagród/wizyt przy błędzie transakcji.

validate_release_061: 386 unikalnych nowych identyfikatorów, zgodne nazwy i pozycje OSM/GeoNames do 500 m, wykluczenie punktów bliższych niż 400 m, 1000 DE / 451 PL. Wszystkie 2263 oryginalne rekordy zachowane bez zmian. validate_collections: pełne pokrycie kategoriami i grupami szczytów, zgodność kraju i brak duplikatów członków. Dawne validate_catalog / validate_stage3 nadal sprawdzają historyczną bazę źródłową; nowy runtime i rozszerzenie mają osobny gate release_061.

Wizualnie sprawdzono zapisane odznaki z datą w Light; wcześniejsze testy Light/Dark i 320px przeszły. W APK potwierdzono 1451 metadanych punktów, aktywne odznaki i sumę kontrolną nowego katalogu. SHA-256 APK: 3e067fa276563ff69c69433055070a89d09b1a2fd97b6423d23e7aea2af7c19f. Podpis zgodny z poprzednimi lokalnymi wydaniami.

Nie wykonywano testu aktualizacji ani pełnego systemowego importu na fizycznym telefonie — pozostają w punkcie 6. Nie ogłaszamy naprawienia wcześniej zgłoszonego konfliktu istniejącej instalacji bez testu urządzenia.

---

# 0.6.0 — etap 5: PL / DE / EN

Gradle assembleDebug, testDebugUnitTest i lintDebug: BUILD SUCCESSFUL. Test JVM potwierdził opcjonalny język w starszych kopiach, ZIP round-trip pl/de/en, zachowanie pogody i odrzucenie błędnej wartości języka.

PASS: test_languages.cjs oraz regresje test_ui, test_visits, test_collections, test_startup, test_journal, test_backup_ui, test_achievements. Nowy test sprawdza trzy języki, formularz wizyty, przełączanie i restart, zachowanie pogodowych wartości, ocen, notatek z HTML oraz własnej nazwy listy, tłumaczenia kolekcji tematycznych, informacji prawnych i podsumowania kopii. Sprawdzono widoki 390px i 320px oraz natywne pierwszeństwo zapisanego języka. Wizualnie sprawdzono niemieckie podsumowanie kopii i angielski dziennik; długie okna przewijają się pionowo.

Katalog wewnątrz APK ma niezmienioną sumę SHA-256. Podpis APK zgodny z dotychczasowym lokalnym certyfikatem; versionCode 10. SHA-256 APK: 89ed4eac0fe79867078f3581bdb288fcdcf469f5defcc42726a107d6afde26c4.

Pełny proces Android SAF, aktualizacja istniejącej instalacji i odbiór na fizycznym telefonie pozostają w punkcie 6. Testy przeglądarkowe nie zastępują tych prób. Zakres trwałego przyznawania odznak pozostaje niedokończony w punkcie 4.

---

# Podgląd odznak 0.5.1

Zawiera gotowy zakres 0.5.0 (eksport/import i Dark/Light) oraz podgląd 12 rodzin po 11 poziomów. Obliczenia: unikalne miejsca, sumy dystansu/czasu/podejść, ukończone kolekcje, procent aktualnego katalogu kraju. Must See i regiony administracyjne pozostają nieaktywne wobec braku zweryfikowanych oznaczeń. Nie ma przyznawania ani zapisu dat zdobycia; to podgląd do uzgodnienia, nie zakończony etap odznak.

PASS: test_achievements.cjs — 12 rodzin, 11 rosnących progów, unikalność vs sumy, oddzielenie krajów, granice progów, drabinka Master ★★★, Light/Dark i 320px. JUnit sprawdza teraz 11 poziomów (usunął dawny Master bez gwiazdek); 5 testów BackupArchiveTest nadal PASS. Gradle assembleDebug/testDebugUnitTest/lintDebug: BUILD SUCCESSFUL. Wizualnie sprawdzono karty i drabinkę. Podpis i obecność 11 poziomów wewnątrz APK sprawdzone; katalog niezmieniony.

SHA-256 APK 0.5.1: `dbdbde9138a4501feafea97ab3c4082050ca83c7b33ec0fcd7fcd29083dc248f`.

Progi: ACHIEVEMENTS_PROPOSAL.md. Pytanie o akceptację pozostaje otwarte. Konflikt instalacji wymaga odpowiedzi o komunikacie i źródle poprzedniego APK. Testy telefonu, w tym nowej kopii danych, zaplanowane w punkcie 6.

---

# 0.5.0 — kopia danych i motywy

Gradle assembleDebug/testDebugUnitTest/lintDebug: BUILD SUCCESSFUL. 5 testów BackupArchiveTest PASS (ZIP/photo/Unicode; odrzucenie błędnej wersji/ID/oceny; ścieżki/duży wpis; integralność zdjęcia; deduplikacja zachowująca obecne dane), plus istniejący test szkieletu odznak. Android Lint: 0 błędów, 5 ostrzeżeń dotyczących istniejących EXIF, tekstów i ustawień backupu Androida.

PASS: test_backup_ui.cjs, test_startup.cjs, test_journal.cjs, test_collections.cjs, test_migration.py oraz test_backup_transaction.py. Wizualnie sprawdzono podsumowanie importu. Baza katalogu wewnątrz APK bez zmian. Podpis APK sprawdzony, zgodny z dotychczasowym lokalnym certyfikatem.

SHA-256 APK: `9090cc65df581ba44dccaa61eac79e5e84266b1b14a3498cee8c05e477081371`.

Pełnego wyboru plików i odtworzenia danych na telefonie nie testowano — zgodnie z instrukcją testy urządzenia są przeniesione do punktu 6. Test SQLite jest kontrolą transakcji, nie testem natywnego interfejsu Androida. Konflikt instalacji na telefonie nadal nie został potwierdzony ani rozwiązany; usunięto dystrybucję tymczasowo podpisanych APK CI. Szczegóły: BACKUP.md i UPDATES.md.

---

# Poprawki dziennika 0.4.2 — 10.09.2026

Kosz z potwierdzeniem usuwa pojedynczą wizytę. Ocena 1–5 jest opcjonalna; 0 oznacza brak oceny. Dziennik pokazuje symbol kategorii, nazwę, datę i gwiazdki. Kolekcje otwierają widok główny po kliknięciu zakładki.

Kontrole PASS: test_journal.cjs (ocena/zapis/edycja/wyczyszczenie/trwałość, ikona i data, anulowanie usunięcia, błąd zapisu bez utraty UI, usunięcie jednej z wielu i ostatniej wizyty, przeliczenie postępu i filtra, reset nawigacji, 320 px), test_collections.cjs, test_startup.cjs i test_visits.cjs. Kontrola wizualna podsumowania dziennika. test_migration.py: migracje SQL v1→v3 oraz v2→v3 zachowują istniejące dane, rating domyślnie 0, ograniczenie 0–5, poprawne zachowanie po usuwaniu wizyt.

Gradle assembleDebug/testDebugUnitTest/lintDebug: BUILD SUCCESSFUL. Podpis sprawdzony, ten sam lokalny certyfikat co wcześniejsze APK. Poprawki obecne w APK, katalog bez zmian. Test urządzenia tej wersji jeszcze nie został przeprowadzony. Testy UI używają przeglądarki; migracje sprawdzono na SQLite, a natywne usuwanie kopii zdjęć wymaga sprawdzenia na urządzeniu. Usuwane są tylko kopie w pamięci aplikacji, które nie są używane przez inne wizyty; oryginały w galerii pozostają nietknięte.

SHA-256 APK 0.4.2: `ca082dde0e7ed5a15ed7e99340e49be7e1f2e9bad7eac707054bc5e68c31908d`.

Zgłoszony konflikt instalacji i motyw System pozostają do późniejszej diagnozy/poprawki zgodnie z instrukcją użytkownika. Nie obiecujemy rozwiązania konfliktu w tej wersji. Filtry edytora list również odłożono; zakres zapisano w ROADMAP.md.

---

# Poprawka 0.4.1 — błąd startu katalogu

W 0.4.0 `start()` wywoływano podczas wykonywania app.js, przed kolejnymi skryptami visits.js i collections.js. Szybki odczyt lokalnych danych mógł zakończyć się przed inicjalizacją collectionData. Błąd odtworzono przez opóźnienie collections.js przy symulowanym synchronicznym mostku Androida: ReferenceError: collectionData is not defined, a następnie zgłoszony komunikat o katalogu.

Poprawka uruchamia start po DOMContentLoaded, kiedy wszystkie skrypty funkcji są już wykonane. Nie zmienia schematu ani zapisanej bazy, list, zdjęć czy współrzędnych.

`test_startup.cjs` przed zmianą FAIL; po zmianie PASS dla ekranu głównego i zapamiętanego PL/DE, z zachowaną wizytą i własną listą. Test używa symulowanego mostka, nie urządzenia Android. `test_collections.cjs` PASS. Gradle assembleDebug/testDebugUnitTest/lintDebug: BUILD SUCCESSFUL. Podpis APK sprawdzony i zgodny z poprzednimi wersjami. W APK potwierdzono poprawkę i niezmieniony katalog. Test na telefonie użytkownika pozostaje do wykonania.

SHA-256 APK 0.4.1: `143eb35dffcbd4d650c137b10ac13b365aa5c2b10f57df3064709b205cc9573a`.

---

# Etap 4 / 0.4.0 — 10.09.2026

Gotowe: 79 kolekcji (31 PL / 48 DE), 24 grupy tematyczne i 55 grup szczytów według regionów źródłowych. Postęp liczy unikalne odwiedzone miejsca. Kolekcje mają klikane karty, wyszukiwarkę i sortowanie odwiedzone najpierw. Propozycje pokazują stałą kolejność (nie są sortowane według odwiedzin). Własne listy mają zapis, edycję, przestawianie, usuwanie elementów i całych list z potwierdzeniem. Kliknięcie punktu otwiera kartę i umożliwia wizytę lub przejście do mapy.

Kontrole zakończone powodzeniem:

- `test_ui.cjs` — regresja map, motywów i filtrów.
- `test_visits.cjs` — regresja wizyt, zdjęć przeglądarkowych i dziennika.
- `test_collections.cjs` — zapis wizyty z kolekcji, przeniesienie odwiedzonego elementu z końca na początek, licznik, wyszukiwanie, przejście do mapy, pasma, dokładna kolejność przykładu użytkownika, kopiowanie/edycja/przestawianie/usuwanie elementów, zapis po odświeżeniu, brak duplikatów, separacja PL/DE, usunięcie listy zachowujące wizyty, 320 px i działanie kolekcji bez sieci.
- `validate_collections.py` — pełne pokrycie istniejącego katalogu kategoriami, pełne pokrycie szczytów regionami, unikalne identyfikatory i kraj, poprawne referencje propozycji; niezmieniony SHA-256 katalogu.
- Gradle assembleDebug, testDebugUnitTest i lintDebug: BUILD SUCCESSFUL. Brak błędów Lint.
- Kontrola wizualna kolekcji Light, list Dark i propozycji Malinów.
- Podpis APK zweryfikowany, certyfikat zgodny z 0.3.0/0.3.1. Katalog i 79 kolekcji sprawdzone wewnątrz APK.

SHA-256 APK: `d8671ee43e216207b09e6f26eb448ef154eb4eb651fcbf5bce8d869c1c7c116e`.

Nie wykonano jeszcze instalacji 0.4.0 na fizycznym telefonie. Trwałość list sprawdzono w przeglądarce; natywna ścieżka SharedPreferences została skompilowana i sprawdzona statycznie, ale wymaga testu urządzenia. Zdjęcia i aktualizacja aplikacji także pozostają do sprawdzenia na telefonie. Odznaki, języki i eksport/import to etap 5. Katalog nadal ma 1065 punktów; nie uzupełniano współrzędnych. Źródłowe szkice tras nie są publikowane jako gotowe propozycje.

---

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
