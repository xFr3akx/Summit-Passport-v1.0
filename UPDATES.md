# Aktualizacje APK

APK do instalacji: pliki downloads/Summit_Passport_<wersja>.apk, publikowane po lokalnej kompilacji. Certyfikat SHA-256: `2c2db6a5d195ec4e7e4c2225d7d022fcc7431e9192025dd80f2fe39c77371b1f`. Kolejne wersje zwiększają versionCode. Klucz podpisu pozostaje poza repozytorium.

Poprzedni workflow GitHub Actions tworzył i udostępniał debug APK z kluczem generowanym na maszynie CI. Taki APK mógł mieć inny certyfikat niż wersja z downloads. Workflow nadal kompiluje i testuje, ale udostępnia wyłącznie raporty. Nie publikuje już tych APK do instalowania.

To usuwa źródło mieszania różnych podpisów w przyszłej dystrybucji. Nie potwierdza przyczyny konfliktu istniejącej instalacji użytkownika. Do diagnozy poproszono o dokładny komunikat i źródło poprzedniego APK. Nie odinstalowywać ani nie czyścić danych w celu obejścia konfliktu. Nie obiecywać aktualizacji instalacji podpisanej innym, niedostępnym kluczem.
