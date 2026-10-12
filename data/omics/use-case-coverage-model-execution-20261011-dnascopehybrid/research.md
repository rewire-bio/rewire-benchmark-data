# Research: Hu et al. 2026, DNAscope Hybrid (Frontiers in Bioinformatics 5:1691056)

Use case: `use-case-diagnostic-genomics-model-execution`. Pass: diagnostic genomics execution literature search, window 2025-10-01 to 2026-10-11. The search log, candidates and gaps for the whole pass are in `data/omics/lit-search-20261011-uc-execution/` (ledger, scope audit and report).

Selected because it prints stage runtimes, core-hours and on-demand and spot cloud cost for CPU-only hybrid, long-read and short-read germline pipelines on one stated cloud instance, which no linked source covers.

Modelling:
- New method family `method-sentieon-dnascope` (distinct from the existing Sentieon DNASeq method).
- One protocol with three datasets, one per pipeline, because each pipeline ran on different input data.
- New metric `cpu-time` (core-hours, unit `hour`).
- Origin `author_reported`: all authors were Sentieon employees.

A companion bioRxiv preprint by the same authors (10.1101/2025.11.14.688541, ONT data) has a similar Table 2 printed as an image; it was not extracted (see the pass report).

Things a reviewer should judge:
1. Whether a table whose three columns use different inputs belongs in one protocol, and the `proxy` relevance.

## Records

| Kind | Count |
| --- | --- |
| claim | 1 |
| configuration | 3 |
| dataset | 3 |
| evaluation | 3 |
| method | 1 |
| protocol | 1 |
| result | 21 |
| source | 1 |
