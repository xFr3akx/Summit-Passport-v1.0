# Plan budowy Summit Passport

Stan uzgodnień: 10.09.2026. Baza zostaje zamrożona na czas kończenia aplikacji. Near Me przeniesiono do etapu 7.

| Etap | Zakres i warunek zakończenia | Stan |
| --- | --- | --- |
| 1. Szkielet | Repozytorium, struktura Android, ekrany i lokalny model danych. Osobno należy potwierdzić kompilację APK. | Szkielet zapisany; testowy APK zbudowany i podpis sprawdzony. |
| 2. Baza PL/DE | Zachowany materiał obu PDF-ów. Do aplikacji trafia zamrożony katalog: 1065 punktów po kontroli, 1198 miejsc bez publikowanej lokalizacji. | Uzupełnianie wstrzymane decyzją użytkownika. |
| 3. Wygląd i mapa | L4/T4 Light/Dark, symbole S1, mapa 451 punktów PL i 614 DE, grupowanie znaczników, filtry nazwy/kategorii/nieodwiedzonych, lista i szczegóły lokalizacji. Bez Near Me. | Zakończony. Kod zapisany na GitHubie, testowy APK zbudowany; raport w TESTING.md. |
| 4. Odwiedziny i kolekcje | Wiele wizyt jednego miejsca, zdjęcia, dziennik, kolekcje, klikane listy i propozycje kolejności odwiedzin. | Zakończony w 0.4.0: wizyty, zdjęcia, dziennik, 79 kolekcji, własne kolejności odwiedzin i 2 propozycje startowe. Test APK na urządzeniu pozostaje do wykonania. |
| 5. Odznaki i ustawienia | Rodziny odznak, jednakowa liczba poziomów w każdej rodzinie, uzgodnione progi, PL/DE/EN, motywy, eksport/import. | Przed nami. |
| 6. Testy i APK | Kompilacja, instalacja na telefonie, działanie bez internetu, trwałość wizyt i importu, kontrola mapy i końcowy APK. | Przed nami. |
| 7. Dodatki | Near Me i dalsze uzupełnianie katalogu po uruchomieniu działającej aplikacji. | Odłożone. |

Po odbiorze etapu 3 użytkownik zatwierdził poprawki 0.3.1 oraz rozpoczęcie wizyt i dziennika. Nie rozszerzamy teraz bazy. Niekompletność katalogu pozostaje jawna; na mapie publikowane są wyłącznie rekordy z map_ready.

## Zmiana dotycząca propozycji wycieczek

Przycisk na karcie miejsca pokazuje ponumerowaną listę kolejnych miejsc. Każdy element otwiera kartę miejsca i pokazuje stan odwiedzenia. Nie jest potrzebna wyszukiwarka szlaków ani wyznaczanie ich przebiegu. Szczegóły: data/VISIT_PROPOSALS.md.

## Otwarte ustalenia przed odpowiednim etapem

- L4 i S1 zaadaptowano do zasobów wektorowych, T4 do lokalnego tła aplikacji. Odznaki A1 pozostają do etapu 5.
- W opisie użytkownika są po dwa poziomy Bronze, Silver, Gold i Diamond oraz Master z 1, 2 i 3 gwiazdkami: łącznie 11. Szkielet ma również Master bez gwiazdki (12). Przed etapem 5 trzeba usunąć tę rozbieżność zgodnie z ostatecznym wyborem użytkownika; obecny szkielet nie stanowi zatwierdzenia dodatkowego poziomu.
- Liczbowe progi odznak nie są ustalone. Każda rodzina będzie miała taką samą liczbę poziomów, z własną tematyką ikon.

## Stałe ustalenia HOME — 10.09.2026

Osobna baza dla każdego kraju: **Niemcy — Overath; Polska — Jastrzębie-Zdrój**. Markery HOME są poza klastrami i filtrami atrakcji. Przycisk HOME zawsze pozwala wrócić do bazy, także po oddaleniu widoku. Są to centra wskazanych miast, nie adresy prywatne. Nie doliczamy ich do 1065 atrakcji.

## Odbiór etapu 4

Wersja 0.4.0 zawiera 31 kolekcji PL i 48 DE: 24 tematyczne i 55 grup szczytów według pasm/regionów źródłowych. Kolekcje obejmują 1065 istniejących punktów i nie oznaczają kompletnego wykazu szczytów czy oficjalnego programu odznak. Źródłowe grupy tras pozostają szkicami; nie zamieniono ich automatycznie na opublikowane propozycje. Użytkownik może tworzyć własne listy, zmieniać ich kolejność i usuwać listę bez usuwania wizyt.

Następny etap: odznaki (11 poziomów zgodnie z ustaleniem: po 2 Bronze/Silver/Gold/Diamond + Master 1/2/3 gwiazdki), języki oraz eksport/import. Nie rozpoczęto etapu 5.

## Uwagi po odbiorze 0.4.1 — zakres 0.4.2

Użytkownik potwierdził ponowne działanie aplikacji. W 0.4.2: kosz obok edycji wpisu w dzienniku, potwierdzenie usunięcia pojedynczej wizyty, ocena 1–5 gwiazdek (opcjonalna, edytowalna), symbol kategorii + nazwa + data + ocena w podsumowaniu. Ponowne kliknięcie zakładki Kolekcje otwiera widok główny, resetuje podkolekcję, wyszukiwanie i podzakładkę. Usunięcie ostatniej wizyty cofa odwiedzenie i postęp; pozostałe wizyty tego miejsca zachowują odwiedzenie.

### Zapisane na później — wyraźnie odłożone przez użytkownika

- Usunąć wybór motywu System (zgłoszony jako niedziałający). Docelowo Dark domyślny, z przełącznikiem Light. W 0.4.2 motywu nie zmieniano.
- Zdiagnozować konflikt aktualizacji Androida, który u użytkownika blokuje instalację bez odinstalowania. Mimo jednakowego lokalnego certyfikatu dostarczanych APK nie ustalono przyczyny konfliktu na urządzeniu. Nie uznajemy problemu za rozwiązany; nie zalecamy usuwania danych.
- W edytorze własnej kolejności odwiedzin dodać filtry i wybieranie z listy oprócz wyszukiwania nazw. Funkcja odłożona na później.
