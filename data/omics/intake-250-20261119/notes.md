# Intake for issue #250

Add discovered hEVO haplotype-based DNA model family with gated-access provenance

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-19. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-250-20261119-model-hevo` (model, depth tier 1)
- `intake-250-20261119-model-hevo-base-o` (model, depth tier 1)
- `intake-250-20261119-model-hevo-large-o` (model, depth tier 1)
- `intake-250-20261119-dataset-hevo-benchmarks` (dataset)

## Sources

- https://github.com/mulinlab/hEVO/blob/eac1314c7272e7ca16e2bb1dcb1a4fb2e362bc12/README.md: `intake-250-20261119-source-hevo-readme-md-at-eac1314c7272e7ca16e2bb1dcb1a4fb2e362bc12-m`, SHA-256 63d191e7877159d8247d0e727c12341c7736e57bec78aaf46554592cc63efade, text/html
- https://huggingface.co/MulinLab/hEVO-base-o: `intake-250-20261119-source-mulinlab-hevo-base-o-hugging-face`, SHA-256 907db7fba3a0183a11aded56971abf04b67248f79c100d9d5e76650b89f25e5f, text/html
- https://huggingface.co/MulinLab/hEVO-large-o: `intake-250-20261119-source-mulinlab-hevo-large-o-hugging-face`, SHA-256 36c4e0a5ecbb95a9d6de514db4bcf3d3347772dfd44739ad1f255839881a2b3e, text/html
- https://huggingface.co/datasets/MulinLab/hEvo-benchmarks: `intake-250-20261119-source-mulinlab-hevo-benchmarks-datasets-at-hugging-face`, SHA-256 c1a2ebb2415e7525aeb1b564743b926a7ce6230e3cfdff493ee7616967e401ee, text/html
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13738607/: `intake-250-20261119-source-a-genomic-foundation-model-for-interpreting-human-genetic-di`, SHA-256 1443e26b321fdcd3b3c721067e015fecb7dcac2bb0b670c6ff33df2a0c05bc80, text/html
- https://huggingface.co/api/models/MulinLab/hEVO-base-o: `intake-250-20261119-source-huggingface-co-api-models-mulinlab-hevo-base-o`, SHA-256 1fd7f1be2fbb761b3c394f365ca9c87dd82ff78fcba68b592535fe1906b758e7, application/json
- https://huggingface.co/api/models/MulinLab/hEVO-large-o: `intake-250-20261119-source-huggingface-co-api-models-mulinlab-hevo-large-o`, SHA-256 0d9746dc90a0a54e7c533469eab0f272f30884654fa591f18cc8344f0c116408, application/json

## Not added

- hEvo benchmarks: verification: Duplicates e5. Per the README, hEvo benchmarks is the evaluator workflow set for the data bundles in e5, so the two overlap and e4 is dropped. If one benchmark entity is wanted, keep e4 and cite the dataset card for e5 only.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| hEvo | version |   | No |
| hEvo | access | Primary hEvo-base and hEvo-large checkpoints are not released in the sources. Public-data variants are on HF, gated for  | Yes |
| hEvo | licence |   | No |
| hEvo | training_data |   | No |
| hEVO-base-o | source |   | Yes |
| hEVO-base-o | version | revision fa6139047c21d92b58bd8eda49ea2f89a884e33c | Yes |
| hEVO-base-o | access | Gated for peer reviewers. Request access on the HF page and wait for manual MulinLab approval. Load with trust_remote_co | Yes |
| hEVO-base-o | licence |   | No |
| hEVO-base-o | training_data | public 1000 Genomes Project and HGDP sequences, self-supervised MLM, no target-label supervision | Yes |
| hEVO-large-o | source |   | Yes |
| hEVO-large-o | version |   | Yes |
| hEVO-large-o | access | Gated for peer review with manual MulinLab approval (per README). Not verified on the page. | Yes |
| hEVO-large-o | licence |   | No |
| hEVO-large-o | training_data | public 1000 Genomes and HGDP (per README Models paragraph). Not verified on the large page. | Yes |
| hEvo-benchmarks | version |   | No |
| hEvo-benchmarks | access | Gated for peer review per README, with manual approval by MulinLab. | Yes |
| hEvo-benchmarks | species | not verified; the dataset card was not opened | Yes |
| hEvo-benchmarks | scope_note |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 2120 | 27923 | 219724 | 13247 | 0 | 3 | $0.0626 |
| claude-haiku-5-5 | 11678 | 0 | 0 | 9085 | 0 | 0 | $0.0057 |
| claude-sonnet-5-5 | 23522 | 8599 | 0 | 4387 | 0 | 0 | $0.1124 |
| Total | | | | | | | $0.1807 |
