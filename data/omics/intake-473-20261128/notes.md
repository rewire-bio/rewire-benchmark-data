# Intake for issue #473

Add discovered method RNAtomy: RNAtomy: structure-aware RNA foundation model with predicted-geometry pretraining

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-28. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-473-20261128-model-rnatomy` (model, depth tier 1)

## Sources

- https://github.com/Azam-Shi/RNAtomy: `intake-473-20261128-source-github-azam-shi-rnatomy-github`, SHA-256 0caf468b1183d06c0b27572f442c21c24ffe84f08b79429997f621f7269d3e58, text/html
- https://zenodo.org/records/23968854: `intake-473-20261128-source-rnatomy-a-structure-aware-rna-foundation-model-for-transfera`, SHA-256 e37120a171efac5878e0541e1a03322e1fd2945ae912e10efd3c1123510c4b3f, text/html
- https://www.biorxiv.org/content/10.64898/2026.11.10.765792v1: not opened (HTTP 429)

## Not added

- RNAtomy Zenodo release: verification: Drop. The Zenodo record is typed Model and its title is the model's title. It is the distribution point for the e1 weights, pretraining sequences and descriptors, not a separate dataset resource. Its fields are empty or unsupported, so it adds nothing beyond e1.

## Links

- None.

## Possible duplicates in the store

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| RNAtomy | source | https://www.biorxiv.org/content/10.64898/2026.11.10.765792v1 | No |
| RNAtomy | version |   | No |
| RNAtomy | access | Code in the GitHub repository; weights on Zenodo (record 23968854); full 2D maps (about 130 GB) on request only | Yes |
| RNAtomy | licence | Code MIT (README badge, LICENSE not opened); weights CC BY 4.0 (Zenodo, unverified) | Yes |
| RNAtomy | training_data | Pretraining on about 200K RNAs; trRosettaRNA-derived geometry and DSSR-derived descriptors (23 features per nucleotide), | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 10039 | 12302 | 31951 | 10479 | 0 | 3 | $0.0081 |
| claude-sonnet-5-5 | 4 | 17021 | 0 | 1984 | 0 | 0 | $0.0624 |
| Total | | | | | | | $0.0705 |
