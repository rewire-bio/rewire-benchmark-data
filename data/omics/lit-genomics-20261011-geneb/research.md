# Research notes

Part of the 2026-10-11 genomics literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-genomics/ledger.jsonl`.

## Why this source

Completeness check: GENEB (arXiv 2026, inside the window) was in the store with only 22 results (v1 Table 8, 11 models). The official leaderboard covers 41 models in three data regimes; MCC aggregates (micro, macro and 13 categories) were extracted.

## Record counts

- benchmark: 1
- configuration: 41
- dataset: 1
- evaluation: 123
- model: 19
- protocol: 3
- result: 1845
- source: 1

Record counts are after the corrections from the 2026-10-11 independent review. The review, its corrections and the receipt are in `review.md` and `review.json`.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- Mutable leaderboard; pinned by commit.
- Only MCC aggregates are extracted (1,845 results); accuracy and F1 aggregates and the 100 per-task scores (leaderboard_tasks.json, 2.5 MB) are not, to keep the batch bounded.
- SpliceBERT is a self-reported submission (official=false); its evaluations are origin unreported.
- Evo 1 has its own new family record, separate from Evo 2.
- One value is stored in scientific notation (2.1089155370300136e-05); numeric_value is its decimal expansion.
