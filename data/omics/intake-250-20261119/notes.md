# Intake for issue #250

Add discovered hEVO haplotype-based DNA model family with gated-access provenance

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-19. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-250-20261119-model-hevo` (model, depth tier 1)
- `intake-250-20261119-model-hevo-base-o` (model, depth tier 1)
- `intake-250-20261119-model-hevo-large-o` (model, depth tier 1)
- `intake-250-20261119-benchmark-hevo-benchmarks` (benchmark, depth tier 1)
- `intake-250-20261119-dataset-hevo-benchmarks` (dataset)

## Sources

- https://github.com/mulinlab/hEVO/blob/eac1314c7272e7ca16e2bb1dcb1a4fb2e362bc12/README.md: `intake-250-20261119-source-hevo-readme-md-at-eac1314c7272e7ca16e2bb1dcb1a4fb2e362bc12-m`, SHA-256 2c29da8de2efd16d2d759c4c36b877314155e30ed6ae071777b0522ccaeb9e88, text/html
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13738607/: not opened (bot check page instead of the source ("Checking your browser - reCAPTCHA"))
- https://huggingface.co/MulinLab/hEVO-base-o: `intake-250-20261119-source-mulinlab-hevo-base-o-hugging-face`, SHA-256 e9be9d4b4c920e7d6311ee1872c585b801f304e6fc081d7bf8d7cbd57088ade3, text/html
- https://huggingface.co/MulinLab/hEVO-large-o: `intake-250-20261119-source-mulinlab-hevo-large-o-hugging-face`, SHA-256 0a85d164a6109d644a23ea5eb9b5786498ebc897eace493cd0243e8949f9c7da, text/html
- https://huggingface.co/datasets/MulinLab/hEvo-benchmarks: `intake-250-20261119-source-mulinlab-hevo-benchmarks-datasets-at-hugging-face`, SHA-256 1800ba98001cdd7cfa79143727168ac99b92ee68fd89246e99f491523c0ed954, text/html
- https://huggingface.co/api/models/MulinLab/hEVO-base-o: `intake-250-20261119-source-huggingface-co-api-models-mulinlab-hevo-base-o`, SHA-256 1fd7f1be2fbb761b3c394f365ca9c87dd82ff78fcba68b592535fe1906b758e7, application/json
- https://huggingface.co/api/models/MulinLab/hEVO-large-o: `intake-250-20261119-source-huggingface-co-api-models-mulinlab-hevo-large-o`, SHA-256 0d9746dc90a0a54e7c533469eab0f272f30884654fa591f18cc8344f0c116408, application/json

## Not added

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| hEVO model family | name | hEVO model family | Yes |
| hEVO model family | version | v1 (preprint version of manuscript); no model version is stated | No |
| hEVO model family | access | Public checkpoints are only the two -o variants, which are gated on Hugging Face for peer review. Access to the primary  | Yes |
| hEVO model family | licence |   | No |
| hEVO model family | training_data | From abstract: 4.784 billion distinct haplotype sequences from WGS data for 63,809 individuals selected from 550,237 sam | Yes |
| hEVO-base-o | source |   | Yes |
| hEVO-base-o | version |   | No |
| hEVO-base-o | access | Hugging Face model repository, gated for peer review with manual approval by MulinLab. Model card not opened. | Yes |
| hEVO-base-o | licence |   | No |
| hEVO-base-o | training_data | Public 1000 Genomes Project and HGDP sequences, pretrained without target benchmark-label supervision. | Yes |
| hEVO-large-o | source |   | Yes |
| hEVO-large-o | version |   | No |
| hEVO-large-o | access | Hugging Face model repository, gated for peer review. Model card not opened. | Yes |
| hEVO-large-o | licence |   | No |
| hEVO-large-o | training_data | Public 1000 Genomes Project and HGDP sequences. | Yes |
| hEvo benchmarks | source |   | Yes |
| hEvo benchmarks | version |   | No |
| hEvo benchmarks | task | Sequence representations (NT tasks, Genomic Benchmark, URE); regulatory prediction (DeepSEA multi-label with LoRA); vari | Yes |
| hEvo benchmarks | scope_note |   | No |
| hEvo-benchmarks | source | https://github.com/mulinlab/hEVO/blob/eac1314c7272e7ca16e2bb1dcb1a4fb2e362bc12/README.md | No |
| hEvo-benchmarks | source |   | Yes |
| hEvo-benchmarks | version |   | No |
| hEvo-benchmarks | access | Gated; manual approval by MulinLab. Source-specific terms apply. | Yes |
| hEvo-benchmarks | species |   | No |
| hEvo-benchmarks | scope_note |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 2066 | 27341 | 187432 | 12728 | 0 | 3 | $0.0593 |
| claude-haiku-5-5 | 10437 | 0 | 0 | 9454 | 0 | 0 | $0.0058 |
| claude-sonnet-5-5 | 2857 | 36046 | 323233 | 8700 | 0 | 5 | $0.2152 |
| Total | | | | | | | $0.2802 |
