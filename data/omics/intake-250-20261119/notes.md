# Intake for issue #250

Add discovered hEVO haplotype-based DNA model family with gated-access provenance

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-19. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-250-20261119-model-hevo-base-o` (model, depth tier 1)
- `intake-250-20261119-model-hevo-large-o` (model, depth tier 1)
- `intake-250-20261119-model-hevo-base` (model, depth tier 1)
- `intake-250-20261119-model-hevo-large` (model, depth tier 1)
- `intake-250-20261119-method-hevo-two-stage-haplotype-pretraining-and-paired-allele-llr-s` (method, depth tier 1)
- `intake-250-20261119-benchmark-hevo-benchmark-workflows` (benchmark, depth tier 1)

## Sources

- https://huggingface.co/datasets/MulinLab/hEvo-benchmarks: `intake-250-20261119-source-mulinlab-hevo-benchmarks-datasets-at-hugging-face`, SHA-256 56942cf81f04783b71e6928f20848c103ef756bccbed0a47df59716dd4f66d63, text/html

## Not added

- 1 more: over the per-issue cap of 6

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| hEVO-base-o | version | fa6139047c21d92b58bd8eda49ea2f89a884e33c | No |
| hEVO-base-o | access | Gated. Peer reviewers request access on the HF page and MulinLab approves manually. Users need their own HF read token. | Yes |
| hEVO-base-o | licence |   | No |
| hEVO-base-o | training_data | 1000 Genomes Project and Human Genome Diversity Project (HGDP) sequences; self-supervised masked language modelling; no  | Yes |
| hEVO-large-o | version |   | Yes |
| hEVO-large-o | access | Gated for peer review, the same as base (README Getting started; base card). | Yes |
| hEVO-large-o | licence |   | No |
| hEVO-large-o | training_data | The README says both -o models were pretrained on 1000 Genomes and HGDP. Not confirmed on the large card, which was not  | Yes |
| hEvo-base | version |   | No |
| hEvo-base | access |   | No |
| hEvo-base | licence |   | No |
| hEvo-base | training_data |   | No |
| hEvo-large | version |   | No |
| hEvo-large | access |   | No |
| hEvo-large | licence |   | No |
| hEvo-large | training_data |   | No |
| hEvo two-stage haplotype pretraining and paired-allele LLR scoring | version |   | No |
| hEvo two-stage haplotype pretraining and paired-allele LLR scoring | access | Code is in the GitHub repository. Pretraining and dataset-construction code is in a gated HF repository (hEvo-pretrainin | Yes |
| hEvo benchmark workflows | version |   | No |
| hEvo benchmark workflows | task | Evaluation of sequence representations and variant effect scoring | No |
| hEvo benchmark workflows | scope_note | Benchmark workflows table at pinned commit; results and score comparisons are out of scope for this issue. | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 1822 | 25453 | 232828 | 13172 | 0 | 3 | $0.0614 |
| claude-haiku-5-5 | 9598 | 0 | 0 | 10747 | 0 | 0 | $0.0063 |
| claude-sonnet-5-5 | 3038 | 28728 | 122854 | 5286 | 0 | 5 | $0.1430 |
| Total | | | | | | | $0.2108 |
