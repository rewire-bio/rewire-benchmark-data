# Research notes

Part of the 2026-10-11 genomics literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-genomics/ledger.jsonl`.

## Why this source

Completeness check: the store had no results for the Nucleotide Transformer benchmark (18 tasks), one of the standard gLM suites. Supplementary Tables 6 (probing), 7 (fine-tuning) and 9 (normalised averages) were extracted in full.

## Record counts

- benchmark: 1
- configuration: 23
- dataset: 19
- evaluation: 419
- method: 1
- model: 1
- protocol: 37
- result: 419
- source: 1

Record counts are after the corrections from the 2026-10-11 independent review. The review, its corrections and the receipt are in `review.md` and `review.json`.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- Developer paper: InstaDeep and NVIDIA authors; NT, BPNet and Raw Probe rows are author_reported. DNABERT-2, Enformer and HyenaDNA rows were run by the NT authors and are independent_paper.
- Values are medians over 10 cross-validation folds with standard deviations, recorded as uncertainty.
- Supplementary Table 9 has a DNABERT-1 fine-tuning average with no per-task row; it uses the DNABERT family created in the GFMBench batch (add GFMBench first).
- BPNet and Raw Probe rows repeat between Tables 6 and 7; they are recorded once per table as printed.
