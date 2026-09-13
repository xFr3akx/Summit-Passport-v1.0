# Weryfikacja Summit Passport 1.1.2

- Testy Android/JUnit: 11 testów, 0 błędów.
- Android lint: 0 błędów, 4 ostrzeżenia dotyczące istniejącego kodu.
- SQLite v5 → v6: zachowane ID, wszystkie pola wizyty, zdjęcia, listy i odznaki; stara ocena bez przeliczania, znacznik starszego formularza; możliwość zapisania 10/10.
- ZIP: formaty 1 i 2 nadal obsługiwane; format 3 przechowuje starsze i nowe oceny oraz wersję formularza.
- Interfejs: komunikat starszej wizyty, anulowanie, zapis i restart, dziesięć ocen, granice kolorów, filtr 10/10, ołówek i kosz po prawej, Wycieczki.
- Wizualnie sprawdzono formularz Dark i Dziennik Light/Dark, również przy szerokości 320 px.
- Katalog: 1511 DE / 451 PL, 178 nowych punktów DE, 163 wpisy DE nadal oczekują; brak zmian w starych zmapowanych miejscach i całej Polsce; kompletne kolekcje i metadane odznak.
- Kompilacja APK, testy i lint zakończone powodzeniem. Pakiet ma versionName 1.1.2 i versionCode 15; certyfikat podpisu zgodny z opublikowanym APK 1.1. Sprawdzono zgodność spakowanych danych i kodu interfejsu.
- Nie wykonano testu aktualizacji na fizycznym telefonie.

SHA-256 APK: `47365204f24410f21c456769cef5c7245981d62e8e17d1936bc9dcdd4361f28d`.
