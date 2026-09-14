# Summit Passport — klasyfikacja pozostałych wpisów DE

Data audytu: 2026-09-14
Branch: `analysis/germany-remaining`
Baza odniesienia: aktualny `main` po wydaniu 1.1.2.
Produkcja nie została zmieniona.

## Zakres wymagany przez użytkownika — 145 wpisów

Pierwsze 145 rekordów z aktualnej tablicy `unresolved` w `data/germany_completion_12.json` zostało przejrzane według polityki READY / REPRESENTATIVE / DUPLICATE / REVIEW / UNRESOLVED.

Podsumowanie 145:
- READY: 7
- REPRESENTATIVE: 12
- DUPLICATE: 1
- REVIEW: 57
- UNRESOLVED: 68
- Razem: 145
- Bezpieczne do przygotowania stagingu: 19 (READY + REPRESENTATIVE)
- Do połączenia jako duplikat: 1
- Nie publikować automatycznie: 125 (REVIEW + UNRESOLVED)

### READY — 7
1. Gerolsteiner Dolomiten
2. Reiler Hals
3. Doctorberg
4. Petrisberg
5. Basaltprismenwand
6. Oberharzer Wasserregal
7. Muskauer Faltenbogen

### REPRESENTATIVE — 12
1. Niederwald
2. Ringelsteiner Mühle
3. Briederner Schweiz
4. Galgenlay
5. Dürres Maar
6. Ulmener Maar-Stollen
7. Habichtswald
8. Steinachtal
9. Wiesenttal
10. Gutachtal
11. Muskauer Park
12. Rakotzbrücke / Kromlauer Park

### DUPLICATE — 1
- Nitteler Felsen — ta sama tożsamość OSM jest już opublikowana w aktualnym katalogu; nie tworzyć drugiego obiektu. Należy powiązać/reużyć istniejący stable ID.

### REVIEW — 57
Wpisy z co najmniej dwiema wiarygodnymi interpretacjami albo pojedynczym kandydatem bez wystarczającej przewagi kontekstowej. Nie publikować automatycznie. Szczegółowe kandydatury i powody są w artefakcie `germany-remaining-review` z workflow run `34878672963`.

### UNRESOLVED — 68
Nie znaleziono wystarczająco wiarygodnej tożsamości w obecnym przebiegu. Nie zgadywać współrzędnych i nie publikować automatycznie. Szczegóły są w artefakcie audytu.

## Dodatkowa różnica względem wiadomości Work — 18 wpisów

Aktualny `main` ma 163 rekordy w `unresolved`, nie 145. Dlatego dodatkowo przejrzano rekordy 146–163.

Wynik dodatkowych 18:
- READY: 1 — Dammkar
- REPRESENTATIVE: 2 — Soinsee; Lausitzer Seenland
- DUPLICATE: 0
- REVIEW: 4 — Neuendorfer Rummel; Havelhöhenweg; Stubbenkammer; Wattenmeer
- UNRESOLVED: 11

## Pełny wynik aktualnego main — 163

- READY: 8
- REPRESENTATIVE: 14
- DUPLICATE: 1
- REVIEW: 61
- UNRESOLVED: 79
- Safe to stage: 22
- Production overwritten: false

## Zasady klasyfikacji

- READY — jedna jednoznaczna, punktowa tożsamość OSM zgodna z nazwą i kontekstem.
- REPRESENTATIVE — jednoznaczny obszar/way/relation lub obiekt szeroki; stosować punkt reprezentatywny i `coordinateRole=representative_point_not_entrance`.
- DUPLICATE — ten sam OSM identity lub praktycznie ten sam istniejący obiekt; nie tworzyć nowego miejsca, zachować istniejący stable ID.
- REVIEW — kilka wiarygodnych interpretacji albo za mało kontekstu do bezpiecznego wyboru.
- UNRESOLVED — brak wiarygodnej identyfikacji; pozostawić poza mapą, nie zgadywać.

Jedno źródło wystarcza tylko wtedy, gdy jednoznacznie identyfikuje obiekt i współrzędne. Dla homonimów, obiektów granicznych i szerokich obszarów wymagany jest dodatkowy sygnał kontekstowy.

## Źródła audytu

- `data/germany_completion_12.json`
- `app/src/main/assets/ui/catalog.json`
- Photon / OpenStreetMap
- pełny workflow: `Germany remaining analysis`, run `34878672963`
- artefakt: `germany-remaining-review`, artifact id `10362246209`

## Następny krok

Nie zmieniać `main` automatycznie. Najpierw z 19 rekordów READY/REPRESENTATIVE utworzyć staging patch zachowujący istniejące ID, nazwy i kategorie. Nitteler Felsen obsłużyć jako DUPLICATE. Rekordy REVIEW/UNRESOLVED pozostawić poza produkcją do kolejnego, ukierunkowanego researchu.
