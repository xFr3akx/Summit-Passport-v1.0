# Języki — 0.6.0

Ustawienia → Język aplikacji: Polski / Deutsch / English. Domyślnie polski. Zmiana przeładowuje interfejs, zachowując wybrany kraj i zapisane dane. Język nie zależy od kraju: można używać niemieckiego interfejsu w Polsce i odwrotnie.

Tłumaczenia obejmują nawigację, filtry, karty miejsc, formularze wizyt, pogodę, dziennik, kolekcje tematyczne, propozycje odwiedzin, odznaki, ustawienia, kopie danych i informacje prawne. Własne nazwy i notatki oraz nazwy geograficzne nie są tłumaczone. Nazwy rodzin odznak (np. Peak Hunter, Collection Master Poland) zachowują uzgodnione nazwy.

Pogoda jest wyświetlana w wybranym języku, ale zapis zachowuje dotychczasowe stałe wartości. Daty wpisów pozostają w jednoznacznym formacie YYYY-MM-DD. Okna wyboru plików i zdjęć należą do Androida i mogą używać języka systemu.

Język zapisany jest w SQLite app_state oraz lokalnym ustawieniu interfejsu. Nowe ZIP-y zawierają opcjonalne settings.language: pl/de/en. Starsze kopie bez tego pola pozostają obsługiwane i nie zmieniają bieżącego języka; nieprawidłowa wartość powoduje odrzucenie importu. Język jest przywracany razem z pozostałymi ustawieniami w transakcji.

Tłumaczenia są lokalne w i18n.js: bez sieci i bez wysyłania treści użytkownika. Wywołania t() są jawne; nie zastępujemy automatycznie tekstu w notatkach ani nazwach miejsc.
