# Summit Passport — Germany manual review batch 54

## Final status

Branch: `analysis/germany-remaining`

Final verified workflow: `Germany manual 54 final staging`

- Run: `34886157794`
- Result: `SUCCESS`
- Input: 54 manually resolved records
- `STAGE_EXISTING`: 2
- `STAGE_NEW_RUNTIME_RECORD`: 51
- `DUPLICATE`: 1
- `REVIEW`: 0
- Total ready for staging: **53**
- Production catalog overwritten: **no**

Artifact: `germany-manual-54-final-staging` (artifact id `10365355020`)

Files in artifact:

- `data/germany_manual_54_final_staging.json`
- `data/catalog_germany_manual_54_final_candidate.json`

## Duplicate policy

Distance alone is not enough to classify records as duplicates.

Final policy:

- duplicate only when the semantic identity is the same, or the exact stable ID is already map-ready;
- proximity below 80 m is recorded only as `nearExistingWarnings` and requires semantic interpretation.

This prevents nearby but distinct attractions, viewpoints, churches, rocks, valleys and trail features from being collapsed incorrectly.

## One true duplicate

`Elztal` (`SP-54a45d82-f2ca-5e6d-80d0-2a6debb5ec72`) is an alias/duplicate of canonical `Elzbachtal` (`SP-67fa2d8d-bd23-55eb-a2f0-a062338d10ca`). Keep only the canonical valley entry.

## Important corrections made during final review

### Mühlsteinhöhlen

The previous automatic candidate near `Nerother Kopf` was wrong. The plural `Mühlsteinhöhlen` entry refers to the caves at **Rother Kopf** near Gerolstein.

Final point:

- lat: `50.247649`
- lon: `6.620380`
- role: `exact_point`
- source: `https://www.outdooractive.com/de/poi/eifel/muehlsteinhoehlen-rother-kopf/15029416/`

This record must be staged as a separate place, not deduplicated against Nerother Kopf.

### Hannoversche Klippen

`Hannoversche Klippen` are the natural cliff group. `Weser-Skywalk` is a viewing platform located on one of the cliffs; they are related but not the same entity.

Final representative point:

- lat: `51.65`
- lon: `9.43167`
- role: `representative_point_not_entrance`

### Ürziger Felsen

The entry represents the rocky/Urley landscape east of Ürzig, not the `Ürziger Würzgarten` vineyard itself.

Final representative point:

- lat: `49.9809`
- lon: `7.0167`
- role: `representative_point_not_entrance`

### Elztal / Elzbachtal

The names describe the same Elzbach valley context around Pyrmont. `Elzbachtal` remains canonical and `Elztal` is linked as a duplicate/alias.

## Runtime metadata gate

Of the 53 staging candidates:

- 2 already exist as unresolved records in the runtime catalog and can be updated in place:
  - `Hohe Wart`
  - `Federath / Bergische Höhen`
- 51 stable IDs are absent from the current runtime catalog.

The 51 records already have the reviewed coordinate decision, coordinate role and source, but before production merge they still require the normal runtime metadata gate:

- region / region code as required by runtime schema;
- collection membership / collection consistency;
- final source and coordinate-role normalization to the runtime schema;
- preservation of the existing stable IDs from the working data.

Do not mint replacement IDs.

## Near-existing warnings

Four staged records remain spatially close to an existing map-ready place. They are not automatically duplicates because the semantic identity is different:

- `Pyrmonter Felsen`
- `Elzbachtal`
- `Beilstein`
- `Baumwipfelpfad Saarschleife`

Keep these warnings visible during final production patch review.

## Next step

Build a production-ready patch for the **53 staging candidates** by completing runtime metadata for the 51 missing-runtime records, updating the 2 existing unresolved runtime records, linking `Elztal` to canonical `Elzbachtal`, and validating the complete candidate catalog before modifying `app/src/main/assets/ui/catalog.json`.
