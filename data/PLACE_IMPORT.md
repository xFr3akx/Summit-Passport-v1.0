# Szybki import miejsc — Summit Passport

Ten pipeline służy do hurtowego przygotowania nowych miejsc bez ręcznej edycji `catalog.json`.

## Zasada bezpieczeństwa

`app/src/main/assets/ui/catalog.json` jest źródłem produkcyjnym. Importer go **nie nadpisuje**. Generuje:

- `data/new_places_report.json` — wynik deduplikacji i walidacji,
- `data/catalog_next.json` — kopię katalogu z dopisanymi wyłącznie rekordami `NEW`.

Dopiero po przeglądzie raportu można świadomie zastąpić katalog produkcyjny.

## Kolejka

Wpisuj kandydatów do `data/new_places_queue.csv` albo podaj własny CSV/JSON. Kolumny:

`country,name,category,lat,lon,region,area,source,coordinate_role,priority,notes`

Wspierane role współrzędnych:

- `exact` — dokładny POI,
- `representative` — punkt reprezentatywny większego obszaru,
- `start` — wejście/start szlaku lub doliny,
- `review` — wymaga ręcznej decyzji.

Importer rozumie również nazwy roboczej taksonomii, np. `ROCK_GEOLOGY`, `PASS_SADDLE`, `TRAIL_EXPERIENCE`, i mapuje je na typy runtime aplikacji.

## Uruchomienie

```bash
python3 scripts/import_places.py
```

lub:

```bash
python3 scripts/import_places.py moja_paczka.csv
```

## Statusy

- `NEW` — bezpieczny kandydat dopisany do `catalog_next.json`,
- `EXISTS` — rekord już istnieje,
- `POSSIBLE_DUPLICATE` — podobna nazwa / bardzo bliski punkt; sprawdzić ręcznie,
- `REVIEW` — lokalizacja świadomie niejednoznaczna,
- `INVALID` — brak wymaganych danych albo błędny format.

## Reguły szybkości

Pracujemy paczkami 100–200 rekordów. Ręcznie sprawdzamy tylko `POSSIBLE_DUPLICATE`, `REVIEW` i `INVALID`. Nie weryfikujemy drugi raz rekordów `EXISTS` i nie przepisujemy ręcznie rekordów `NEW`.

Po zatwierdzeniu paczki uruchamiamy istniejące walidatory katalogu, kolekcji oraz testy aplikacji.
