# Research notes

Part of the 2026-10-11 genomics literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-genomics/ledger.jsonl`.

## Why this source

GFMBench-API (Larey et al., NVIDIA with Sheba and Mount Sinai) wraps existing genomic tasks and a new ClinVar indel task behind one evaluation interface and reports five gLMs. Chosen for breadth (supervised and three zero-shot scoring families on 19 tasks), relevance to the regulatory-variant and BRCA1/BRCA2 use cases (TraitGym, BRCA1 SGE tasks), and independence from the model developers.

## Record counts

- benchmark: 1
- claim: 9
- configuration: 10
- dataset: 20
- evaluation: 139
- model: 1
- protocol: 37
- result: 552
- source: 1

Record counts are after the corrections from the 2026-10-11 independent review. The review, its corrections and the receipt are in `review.md` and `review.json`.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- The paper describes Tables 1-5 as results 'reproduced' from earlier benchmarks; the protocols differ from the originals in places (for example fixed test folds instead of cross-validation for VariantBenchmarks). Results should not be compared with the original benchmark papers.
- Single run per cell; no uncertainty.
- Several Table 1 cells show degenerate classifiers (MCC 0.0000, AUROC 0.5000); these are transcribed as printed.
- The NTv3 family record is created in the GUANinE batch; add that batch first.
- How the BRCA1 three-class labels were made binary for AUROC is not stated.

## Use-case judgements

Relevance judgement claims are in `batch.jsonl`. The matching `assessed_by` links are listed in `use-case-links.json`; see `review.md` for how they were applied.
