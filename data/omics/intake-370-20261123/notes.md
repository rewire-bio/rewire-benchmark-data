# Intake for issue #370

Add discovered benchmark SAFFRON: SAFFRON: benchmark testing if spatial transcriptomics FM embeddings capture spatial gradients

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-23. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-370-20261123-benchmark-saffron` (benchmark, depth tier 1)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.08.01.742217v1.full: not opened (HTTP 429)
- https://github.com/chitra-lab/SAFFRON: `intake-370-20261123-source-github-chitra-lab-saffron-saffron-is-a-mechanistic-interpret`, SHA-256 24eedf84f25855ecfb8f257304b2c8d60d27d434dc57ea7bcb5f0fa11e848762, text/html
- https://www.biorxiv.org/content/10.64898/2026.08.01.742217v2: not opened (HTTP 429)
- https://huggingface.co/datasets/ChitraLab/saffron-benchmark: `intake-370-20261123-source-chitralab-saffron-benchmark-datasets-at-hugging-face`, SHA-256 6e8edacd61f4dbffd5b812ec8b5ed00c8e17d97be476251c167cbe147dd8b64b, text/html
- https://saffron-sae.readthedocs.io: `intake-370-20261123-source-saffron-sparse-autoencoder-framework-for-representing-omics`, SHA-256 52d91e7595163269799bd8d25917bd2bd8a010f33fcc8e790623d4d6b1323070, text/html

## Not added

- None.

## Links

- None.

Proposed but not written:

- SAFFRON uses_data ChitraLab/saffron-benchmark: not supported at a location in a source

## Possible duplicates in the store

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| SAFFRON | version |   | No |
| SAFFRON | task | Test whether embeddings from spatial transcriptomics foundation models (SFMs) encode known sources of spatial variation  | Yes |
| SAFFRON | scope_note | Spatial transcriptomics foundation-model embeddings, evaluated on gradient and plaque-related spatial variation. Per the | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 11060 | 13072 | 46157 | 9305 | 0 | 4 | $0.0079 |
| claude-sonnet-5-5 | 4 | 16591 | 0 | 2337 | 0 | 0 | $0.0649 |
| Total | | | | | | | $0.0727 |
