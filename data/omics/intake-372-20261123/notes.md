# Intake for issue #372

Add discovered benchmark Where single-cell foundation models help: a public-data benchmark of annotation, in silico perturbation and gene regulatory inference: Benchmark of single-cell foundation mode

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-23. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-372-20261123-benchmark-where-single-cell-foundation-models-help-a-public-data-bench` (benchmark, depth tier 1)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.11.03.763968v3: not opened (HTTP 429)
- https://www.biorxiv.org/content/10.64898/2026.11.03.763968v3.full: `intake-372-20261123-source-where-single-cell-foundation-models-help-a-public-data-bench`, SHA-256 14fc25f877d02b4b99aae1311b2aec14c9567f4fb7947c6c4520350b4c5db20d, text/html
- https://www.biorxiv.org/content/10.64898/2026.11.03.763968v2: not opened (HTTP 429)

## Not added

- None.

## Links

- None.

Proposed but not written:

- Where single-cell foundation models help: a public-data benchmark of annotation, in silico perturbation and gene regulatory inference evaluates_task reported-task-3063ed4da76b4b: not supported at a location in a source

## Possible duplicates in the store

- Where single-cell foundation models help: a public-data benchmark of annotation, in silico perturbation and gene regulatory inference against `lit-cells-networks-20261011-chen2026-benchmark-harmonised-sc-spatial-fm` ("Harmonised single-cell and spatial foundation model benchmark (Chen et al. 2026)"): distinct, The store record cites a different paper, Harmonised benchmarking of foundation models for single-cell and spatial transcriptomics, which covers six models (Nicheformer, CellPLM, scGPT-spatial, GenePT-w, scELMo, Novae). The new entity benchmarks scGPT, Geneformer V1 and V2, Nicheformer and scFoundation, CellOracle and STATE.
- Where single-cell foundation models help: a public-data benchmark of annotation, in silico perturbation and gene regulatory inference against `lit-cells-networks-20261011-ye2026grn-benchmark-static-grn-fm` ("Static GRN reconstruction from single-cell foundation models (Ye et al. 2026)"): distinct, The store record is a different paper on zero-shot GRN reconstruction on BEELINE datasets. The new entity covers annotation, perturbation and GRN inference on Perturb-seq and organoid data.
- Where single-cell foundation models help: a public-data benchmark of annotation, in silico perturbation and gene regulatory inference against `gfm-guides-20261014-kedzierska2025-benchmark-zero-shot-scfm` ("Zero-shot cell embedding evaluation of single-cell foundation models (Kedzierska et al. 2025)"): distinct, The store record is Kedzierska et al. 2025, a zero-shot embedding evaluation of scGPT and Geneformer scored with scIB metrics. It is a different paper and task.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| Where single-cell foundation models help: a public-data benchmark of annotation, in silico perturbation and gene regulatory inference | version |   | No |
| Where single-cell foundation models help: a public-data benchmark of annotation, in silico perturbation and gene regulatory inference | task | Test whether single-cell foundation models beat simple baselines on cell-type annotation (within- and cross-species), in | Yes |
| Where single-cell foundation models help: a public-data benchmark of annotation, in silico perturbation and gene regulatory inference | scope_note | Inputs are per-cell expression profiles, cell state plus virtual gene knockout or overexpression, and patient-level tumo | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 10394 | 4003 | 40131 | 8352 | 0 | 3 | $0.0061 |
| claude-sonnet-5-5 | 3152 | 4452 | 25842 | 2512 | 0 | 0 | $0.0451 |
| Total | | | | | | | $0.0513 |

## Revision after review

The reviewer agent requested changes (https://github.com/rewire-bio/rewire-benchmark-data/pull/376#pullrequestreview-6028784381). The intake agent revised the batch once; it changes only the fields the review did not pass, and it does not revise again.

- `intake-372-20261123-benchmark-where-single-cell-foundation-models-help-a-public-data-bench` duplicates: ruled distinct from `discovery-benchmark-virtual-cell-challenge-2026` ("Virtual Cell Challenge 2026"). Ruled in the revision after review: a different resource. New record: "gene regulatory network inference". Store record discovery-benchmark-virtual-cell-challenge-2026 (benchmark): "unseen cellular contexts". The script compared the source URLs, DOIs and repository addresses the two records give and found none in common; it cannot see one resource cited at two unrelated addresses. The new record is a public-data benchmark of single-cell foundation models and baselines covering cell-type annotation, in silico perturbation and gene regulatory network inference, while the store record is the Virt
