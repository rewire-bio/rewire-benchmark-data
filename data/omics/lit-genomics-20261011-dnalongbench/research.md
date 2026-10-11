# Research notes

Part of the 2026-10-11 genomics literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-genomics/ledger.jsonl`.

## Why this source

Completeness check: the store held only 2 DNALongBench results (Table 3, from the bioRxiv preprint). The journal version (Nature Communications, 2025-11-18, inside the window) was extracted in full: five long-range tasks, an expert model per task, a CNN, HyenaDNA and two Caduceus variants.

## Record counts

- benchmark: 1
- configuration: 13
- dataset: 5
- evaluation: 25
- model: 3
- protocol: 5
- result: 135
- source: 1

Record counts are after the corrections from the 2026-10-11 independent review. The review, its corrections and the receipt are in `review.md` and `review.json`.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- The two cells already in the store (evaluation-lit-007 and evaluation-lit-008, preprint source dnalongbench-2025) duplicate Table 3 HyenaDNA and Caduceus-Ph AUROC from this version. A reviewer may want to supersede or link them.
- Expert models differ per task (ABC, Enformer, Akita, Puffin-D); ABC uses DNase-seq, H3K27ac and Hi-C, not sequence alone.
- Contact-map results use a new metric concept, stratum-adjusted-correlation-coefficient, added to data/vocab/metric.ttl.
- CNN rows are recorded as author_reported (the authors' own baseline); the foundation-model and expert rows as independent_paper.
