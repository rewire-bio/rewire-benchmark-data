# Intake for issue #474

Add discovered benchmark AbBiBench: Zero-shot antibody-antigen binding affinity ranking benchmark

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-28. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-474-20261128-benchmark-abbibench` (benchmark, depth tier 2)
- `intake-474-20261128-dataset-antibody-binding-benchmark-dataset` (dataset)

## Sources

- https://arxiv.org/html/2506.04235v3: `intake-474-20261128-source-a-comprehensive-benchmark-of-computational-models-for-antibo`, SHA-256 39443b37b57d2776b3898f48dced099fbc87e73e31ca83cfee8461aff70b59a5, text/html
- https://github.com/MSBMI-SAFE/AbBiBench: `intake-474-20261128-source-github-msbmi-safe-abbibench-abbibench-antibody-binding-bench`, SHA-256 27043ba4b7ae8fad84efe8bdf7925dcfb60a927dffa438c906b735a11b321bf1, text/html
- https://huggingface.co/datasets/AbBibench/Antibody_Binding_Benchmark_Dataset: `intake-474-20261128-source-abbibench-antibody-binding-benchmark-dataset-datasets-at-hug`, SHA-256 770ba24856343697ef37fe03d3b5671b4a17a43012844a6784977ef95a083537, text/html

## Not added

- None.

## Links

- `intake-474-20261128-benchmark-abbibench` uses_data `intake-474-20261128-dataset-antibody-binding-benchmark-dataset` (Antibody Binding Benchmark Dataset), in this batch: arXiv Introduction (link to the standardized experimental binding affinity datasets on Hugging Face); GitHub README 'Data Resource' section

## Possible duplicates in the store

- Antibody Binding Benchmark Dataset against `reported-dataset-0edd8f724db696` ("antibody peptide-mapping training dataset"): distinct, Stored source is a paper on antibody deamidation prediction from peptide mapping, a different resource from this binding-affinity dataset
- Antibody Binding Benchmark Dataset against `poisk-20261115-dataset-poisk-v1-1` ("POISK patent-derived antibody dataset, version 1.1"): distinct, Stored description is a table of patent-extracted antibody and target sequences from Zenodo record 21775623, not experimental binding measurements

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| AbBiBench | version |   | No |
| AbBiBench | task | Zero-shot ranking of antibody variants by predicted binding affinity to an antigen, scored on the full antibody-antigen  | Yes |
| AbBiBench | scope_note | 16 assays, 13 antibodies, nine antigen targets, 216,560 observations from eight public studies (paper Section 1.1). | Yes |
| Antibody Binding Benchmark Dataset | version |   | No |
| Antibody Binding Benchmark Dataset | access | Public Hugging Face dataset, default/train split, 216k rows, CSV/parquet. | Yes |
| Antibody Binding Benchmark Dataset | species |   | No |
| Antibody Binding Benchmark Dataset | scope_note |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 2638 | 33281 | 388009 | 10012 | 0 | 3 | $0.0666 |
| claude-haiku-5-5 | 9255 | 0 | 0 | 5509 | 0 | 0 | $0.0037 |
| claude-sonnet-5-5 | 552 | 46269 | 67659 | 2423 | 0 | 0 | $0.1478 |
| Total | | | | | | | $0.2180 |
