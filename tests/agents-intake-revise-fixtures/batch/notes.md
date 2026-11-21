# Intake for issue #283

Add CycPepNet cyclic-peptide property benchmark metadata (tier 3)

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-21. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-283-20261121-benchmark-cycpepnet` (benchmark, depth tier 2)

## Sources

- https://github.com/molML/CycPepNet/blob/1ed5e2b98d0239468b1998b64aa6c18148ede11a/README.md: `intake-283-20261121-source-cycpepnet-readme-md-at-1ed5e2b98d0239468b1998b64aa6c18148ede`, SHA-256 62ea199bdeeec90c9a4b8a6e87f83e316e51ab00d515a61415f870f92eb0aa8b, text/html
- https://github.com/molML/CycPepNet/blob/1ed5e2b98d0239468b1998b64aa6c18148ede11a/cycpepnet/benchmark.py: `intake-283-20261121-source-cycpepnet-cycpepnet-benchmark-py-at-1ed5e2b98d0239468b1998b6`, SHA-256 4a9a9353eea36cbb1ef24a2a1f3ea59fb89b7d09f21951d9857f2344d5aab407, text/html
- https://github.com/molML/CycPepNet/blob/1ed5e2b98d0239468b1998b64aa6c18148ede11a/results/learnability.csv: `intake-283-20261121-source-cycpepnet-results-learnability-csv-at-1ed5e2b98d0239468b1998`, SHA-256 fa693c66deb651b07040f7c8886b3f41bdfda8437182e444f54b5b5ce496458a, text/html
- https://github.com/molML/CycPepNet/blob/1ed5e2b98d0239468b1998b64aa6c18148ede11a/data/sources.csv: `intake-283-20261121-source-cycpepnet-data-sources-csv-at-1ed5e2b98d0239468b1998b64aa6c1`, SHA-256 3f9ad0f6650ea4fae1d553dd35246aac6804eb412753bcd13698b76902aa8821, text/html
- https://doi.org/10.26434/chemrxiv.15011871/v1: not opened (HTTP 403)

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
| CycPepNet | version | 1.0.0 | No |
| CycPepNet | task | Predict binding affinity (main binding tasks for OPRM1, MC4R and SSTR2), membrane permeability and half-life from cyclic | Yes |
| CycPepNet | scope_note | Cyclic-peptide property prediction is molecular property prediction, placed in scope for molecular-interactions by the i | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 11862 | 10730 | 17419 | 10218 | 0 | 1 | $0.0078 |
| claude-sonnet-5-5 | 4 | 29852 | 0 | 2372 | 0 | 0 | $0.0984 |
| Total | | | | | | | $0.1062 |
