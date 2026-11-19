# Intake for issue #250

Add discovered hEVO haplotype-based DNA model family with gated-access provenance

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-19. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-250-20261119-model-hevo-base` (model, depth tier 1)
- `intake-250-20261119-model-hevo-large` (model, depth tier 1)
- `intake-250-20261119-model-hevo-base-o` (model, depth tier 1)
- `intake-250-20261119-model-hevo-large-o` (model, depth tier 1)
- `intake-250-20261119-benchmark-hevo-benchmark-suite` (benchmark, depth tier 1)
- `intake-250-20261119-dataset-hevo-benchmarks` (dataset)

## Sources

- https://github.com/mulinlab/hEVO/blob/eac1314c7272e7ca16e2bb1dcb1a4fb2e362bc12/README.md: `intake-250-20261119-source-hevo-readme-md-at-eac1314c7272e7ca16e2bb1dcb1a4fb2e362bc12-m`, SHA-256 8e1ed543268f14bcd0f60a4024824081d671a40f028964122c165ce9c46a3490, text/html
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13738607/: not opened (bot check page instead of the source ("Checking your browser - reCAPTCHA"))
- https://huggingface.co/MulinLab/hEVO-base-o: `intake-250-20261119-source-mulinlab-hevo-base-o-hugging-face`, SHA-256 ea51b98360919cf0ed4a318a2aa1b08538cf26506f990b3daba6f0da03221e50, text/html

## Not added

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| hEvo-base | version |   | No |
| hEvo-base | access |   | No |
| hEvo-base | licence |   | No |
| hEvo-base | training_data | Abstract (S2) describes a corpus of 4.784 billion distinct haplotype sequences from WGS of 63,809 individuals drawn from | No |
| hEvo-large | version |   | No |
| hEvo-large | access |   | No |
| hEvo-large | licence |   | No |
| hEvo-large | training_data | Abstract (S2) describes a corpus of 4.784 billion distinct haplotype sequences from WGS of 63,809 individuals drawn from | No |
| hEVO-base-o | version | fa6139047c21d92b58bd8eda49ea2f89a884e33c | Yes |
| hEVO-base-o | access | Gated; request access on the HF page; MulinLab reviews requests manually. The -o suffix does not mean open weights. | Yes |
| hEVO-base-o | licence |   | No |
| hEVO-base-o | training_data | Public 1000 Genomes Project and HGDP sequences; self-supervised masked language modelling; no benchmark-label supervisio | Yes |
| hEVO-large-o | version |   | No |
| hEVO-large-o | access | Gated, same as hEVO-base-o per the README. | Yes |
| hEVO-large-o | licence |   | No |
| hEVO-large-o | training_data | Public 1000 Genomes Project and HGDP sequences. | Yes |
| hEvo benchmark suite | version |   | No |
| hEvo benchmark suite | task | Sequence representations (NT tasks, Genomic Benchmark, URE); regulatory prediction (DeepSEA multi-label with LoRA); vari | Yes |
| hEvo benchmark suite | scope_note |   | No |
| hEvo benchmarks | version |   | No |
| hEvo benchmarks | access | Gated for peer review. | Yes |
| hEvo benchmarks | species | human | Yes |
| hEvo benchmarks | scope_note |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 2088 | 34548 | 421739 | 13541 | 0 | 3 | $0.0776 |
| claude-haiku-5-5 | 9868 | 0 | 0 | 8830 | 0 | 0 | $0.0054 |
| claude-sonnet-5-5 | 3182 | 41476 | 121402 | 6133 | 0 | 3 | $0.1835 |
| Total | | | | | | | $0.2665 |
