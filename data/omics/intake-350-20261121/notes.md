# Intake for issue #350

Add discovered model ProtCell: ProtCell: foundation model for single-cell proteomics across fragmented antibody panels

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-21. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-350-20261121-model-protcell` (model, depth tier 3)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.10.22.760932v1: `intake-350-20261121-source-protcell-a-foundation-model-for-single-cell-proteomics-biorx`, SHA-256 f03aeb298cbdf3d75727e35083342f76d9047af40489a49e40faf61f12cb8e40, text/html

## Not added

- None.

## Links

- None.

## Possible duplicates in the store

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| ProtCell | version |   | No |
| ProtCell | access |   | No |
| ProtCell | licence |   | No |
| ProtCell | training_data | Public single-cell proteomic datasets from SPDB, Zenodo-hosted resources, SingPro and related public repositories, revie | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 8854 | 18406 | 14878 | 5753 | 0 | 1 | $0.0062 |
| claude-sonnet-5-5 | 4 | 3669 | 9875 | 1031 | 0 | 0 | $0.0205 |
| Total | | | | | | | $0.0267 |
