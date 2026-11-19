# Intake for issue #250

Add discovered hEVO haplotype-based DNA model family with gated-access provenance

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-19. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-250-20261119-model-hevo` (model, depth tier 1)
- `intake-250-20261119-model-hevo-base-o` (model, depth tier 1)
- `intake-250-20261119-model-hevo-large-o` (model, depth tier 1)
- `intake-250-20261119-dataset-hevo-benchmarks` (dataset)

## Sources

- https://github.com/mulinlab/hEVO/blob/eac1314c7272e7ca16e2bb1dcb1a4fb2e362bc12/README.md: `intake-250-20261119-source-hevo-readme-md-at-eac1314c7272e7ca16e2bb1dcb1a4fb2e362bc12-m`, SHA-256 cef00b3f0d6dce79db3d7928546f4a823a29d6dcd3fe953fce2a0c488cf58273, text/html
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13738607/: `intake-250-20261119-source-a-genomic-foundation-model-for-interpreting-human-genetic-di`, SHA-256 7b025f6b0f0fd3f9af24f63648cdab1553ea7f4925fbd65af44356d193d444a5, text/html
- https://huggingface.co/MulinLab/hEVO-base-o: `intake-250-20261119-source-mulinlab-hevo-base-o-hugging-face`, SHA-256 a10151e047c28498eca781bd0e7d9a44f84e6bcbf1b2c82e809d2a0e931da2bc, text/html
- https://huggingface.co/api/models/MulinLab/hEVO-base-o: `intake-250-20261119-source-huggingface-co-api-models-mulinlab-hevo-base-o`, SHA-256 1fd7f1be2fbb761b3c394f365ca9c87dd82ff78fcba68b592535fe1906b758e7, application/json
- https://huggingface.co/MulinLab/hEVO-large-o: `intake-250-20261119-source-mulinlab-hevo-large-o-hugging-face`, SHA-256 da9dd2babf3f440ae1e9b4f1bcd912a3fde0d8ff5d279984fbe525c7814cb2aa, text/html
- https://huggingface.co/api/models/MulinLab/hEVO-large-o: `intake-250-20261119-source-huggingface-co-api-models-mulinlab-hevo-large-o`, SHA-256 0d9746dc90a0a54e7c533469eab0f272f30884654fa591f18cc8344f0c116408, application/json
- https://huggingface.co/datasets/MulinLab/hEvo-benchmarks: `intake-250-20261119-source-mulinlab-hevo-benchmarks-datasets-at-hugging-face`, SHA-256 802c0f9864619446804490e340019d8a5b22acfcf1bcd0071285fde92d3b0e93, text/html

## Not added

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| hEVO | version | preprint v1, 21 October 2026, DOI 10.64898/2026.10.19.760276 | Yes |
| hEVO | access | gated for peer review (issue; manual gating per Hugging Face API, not checked) | Yes |
| hEVO | licence |   | No |
| hEVO | training_data | StageI masked-span pretraining on deduplicated haplotype windows; StageII nucleotide calibration on variant-centred cont | Yes |
| hEVO-base-o | version |   | No |
| hEVO-base-o | access | Hugging Face model repo, manually gated, reviewer-only (issue) | Yes |
| hEVO-base-o | licence |   | No |
| hEVO-base-o | training_data |   | Yes |
| hEVO-large-o | version |   | No |
| hEVO-large-o | access | Hugging Face model repo, manually gated, reviewer-only (issue) | Yes |
| hEVO-large-o | licence |   | No |
| hEVO-large-o | training_data |   | Yes |
| hEvo-benchmarks | version |   | No |
| hEvo-benchmarks | access | Hugging Face datasets repo (gated status unknown) | Yes |
| hEvo-benchmarks | species |   | No |
| hEvo-benchmarks | scope_note | Kind is dataset, not yet confirmed against the card; the benchmark bundle may instead be a benchmark suite and the verif | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 10692 | 9598 | 25064 | 11460 | 0 | 3 | $0.0082 |
| claude-sonnet-5-5 | 22708 | 8517 | 0 | 3166 | 0 | 0 | $0.0984 |
| Total | | | | | | | $0.1066 |
