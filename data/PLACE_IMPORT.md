# Controlled PL + DE place import

Production MASTER is `app/src/main/assets/ui/catalog.json`.

The Poland and Germany expansion is handled as one transaction from two JSON manifests:

- `data/import/poland_candidates.json`
- `data/import/germany_candidates.json`

The importer is `scripts/import_places.py`. It validates both manifests together, deduplicates against each other and against MASTER, writes dry-run reports, and refuses `--apply` whenever any candidate is `INVALID`, any conflict remains unresolved, or either manifest is not explicitly marked `manifest_complete: true` and `approval_status: "APPROVED_COMPLETE"`.

## Dry-run

```bash
python3 scripts/import_places.py \
  --poland data/import/poland_candidates.json \
  --germany data/import/germany_candidates.json \
  --dry-run
```

Outputs:

- `reports/PL_DE_IMPORT_DRY_RUN.json`
- `reports/PL_DE_IMPORT_DRY_RUN.md`

Exit code 0 means the dry-run is clean and apply is permitted. Exit code 2 means the dry-run completed but apply is blocked.

Candidate statuses are `ADD`, `DUPLICATE`, `CONFLICT`, and `INVALID`. The importer checks stable IDs, normalized names, aliases, diacritics/case/hyphen/space variants, simple type words in Polish/German/English, and coordinates. A coordinate-only match within 80 m is a `CONFLICT` with `NEAR_COORDINATE_MATCH`, never an automatic duplicate.

## Apply

Only after a clean dry-run:

```bash
python3 scripts/import_places.py \
  --poland data/import/poland_candidates.json \
  --germany data/import/germany_candidates.json \
  --apply
```

Apply re-reads and re-validates MASTER, prepares the complete result in memory, creates a timestamped backup under `backups/import/`, and replaces `catalog.json` once with an atomic rename. Existing records are deep-compared before and after; existing IDs cannot be changed or removed. The importer does not touch visits, user data, badges, achievements, or achievement place conditions.

After a successful apply it writes `reports/PL_DE_IMPORT_FINAL.md`.

## Current gate

The checked-in manifests intentionally preserve the latest verified repository state rather than pretending that review is complete. The Poland workflow artifact contains 522 unresolved runtime records, but only 17 have a completed OSM/GeoNames cross-check. The Germany final 54 review resolves semantic identity, but its own report says 51 new runtime records still require region/collection metadata. Therefore both manifests are currently marked incomplete and `--apply` must refuse to modify MASTER.
