# Kopia danych — 0.5.0

Ustawienia → Kopia danych — eksport / import. Android otwiera systemowy wybór miejsca zapisu lub pliku. ZIP zawiera data.json oraz photos/*.jpg. Dane pozostają w aplikacji i w miejscu wybranym przez użytkownika; aplikacja nie przesyła ich do własnej chmury. Plik nie jest szyfrowany.

Import najpierw rozpakowuje do prywatnego katalogu tymczasowego, kontroluje format, wersję, daty, identyfikatory, kraje list, oceny, adresy AllTrails i sumy SHA-256 zdjęć. Nieznane ID miejsc powodują odrzucenie całej kopii. Po podsumowaniu użytkownik potwierdza połączenie. Powtarzające się ID wizyt/list są pomijane: lokalna wersja jest zachowana. To łączenie, bez usuwania lokalnych wpisów. Ustawienia motywu i kraju przywracane są z kopii. Nowe zdjęcia dostają nowe nazwy, dzięki czemu nie nadpisują lokalnych plików.

Wizyty, listy i ustawienia zapisują się w jednej transakcji SQLite. Migracja v4 przenosi listy/kraj z dawnych SharedPreferences; dotychczasowy Light zostaje zachowany, System zmienia się na Dark. W razie błędu transakcji nowe kopie zdjęć są usuwane. Oryginały w galerii nie są modyfikowane.

Limity: 10 000 wizyt, 200 list, 100 miejsc/listę, 10 zdjęć/wizytę, 8 MiB/zdjęcie, 16 MiB data.json i 512 MiB po rozpakowaniu. Niepełny zapis pliku należy ponowić; komunikat sukcesu pojawia się dopiero po zamknięciu ZIP.

Testy JVM sprawdziły ZIP ze zdjęciem i polskimi znakami, integralność, błędne ścieżki, duży wpis, wersję, ocenę oraz deduplikację bez nadpisania. Test UI sprawdził motywy, podsumowanie i potwierdzenie. Test SQLite sprawdził wspólne wycofanie wpisów i ustawień. Nie zastępuje to testu pełnego procesu Android SAF na urządzeniu — zaplanowany w punkcie 6.
