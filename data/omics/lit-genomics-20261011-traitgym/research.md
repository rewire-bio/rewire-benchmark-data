# Research notes

Part of the 2026-10-11 genomics literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-genomics/ledger.jsonl`.

## Why this source

Completeness check: TraitGym, a standard causal regulatory variant benchmark for gLMs, was absent from the store. Its paper prints the main results only in figures, so the official per-model metric files were used. Preprint and dataset predate the window.

## Record counts

- benchmark: 1
- claim: 4
- configuration: 81
- dataset: 2
- evaluation: 156
- method: 5
- model: 1
- protocol: 4
- result: 156
- source: 1

Record counts are after the corrections from the 2026-10-11 independent review. The review, its corrections and the receipt are in `review.md` and `review.json`.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- The source is the official dataset repository, not the paper; the paper (bioRxiv, CC BY-NC-ND) is cited in the source limitations.
- Printed values are the full-precision numbers stored in the CSVs, with bootstrap standard errors.
- GPN-MSA and GPN-Promoter ('GPN_final') rows are author_reported; GPN_final is mapped to the GPN family.
- Duplicate scoring variants exist for some models (for example Caduceus_InnerProduct and Caduceus_Embeddings.minus.inner_product); both are kept as printed.

## Use-case judgements

Relevance judgement claims are in `batch.jsonl`. The matching `assessed_by` links are listed in `use-case-links.json`; see `review.md` for how they were applied.
