# Research notes

Part of the 2026-10-11 genomics literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-genomics/ledger.jsonl`.

## Why this source

Completeness check: GenBench (arXiv 2024) was absent from the store. All result tables were extracted.

## Record counts

- benchmark: 1
- configuration: 10
- dataset: 52
- evaluation: 350
- model: 3
- protocol: 52
- result: 367
- source: 1

Record counts are after the corrections from the 2026-10-11 independent review. The review, its corrections and the receipt are in `review.md` and `review.json`.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- 'Top-1' is not defined beyond the captions; read as the best run over the Table 9 hyperparameter ranges.
- Table 7 prints '-' for DNABERT2, GENA-LM and NT (did not converge); kept as non-numeric results.
- Table 4 short-range values for multi-dataset tasks are aggregates of the Table 10 rows.
- Model checkpoints are given only by parameter count (Table 9).
