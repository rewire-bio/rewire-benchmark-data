# Research: CpGPT fine-tuning against classical classifiers on cfDNA targeted methylation, 2026-10-11

Use case: `use-case-plasma-ctdna-methylation`.

Bounds: window 2025-10-01 to 2026-10-11; about 30 queries per use case for the whole uc-ctdna pass (26 logged); at most about 6 sources extracted across both use cases. Lane `genomics`. Worker: Claude (Opus 5.5) research agent uc-ctdna; no human review claimed. The search log is `data/omics/lit-search-20261011-uc-ctdna/ledger.jsonl` and the pass report is `data/omics/lit-search-20261011-uc-ctdna/report.md`.

## Why this source

Xu and Feng 2026 (medRxiv, 10.64898/2026.07.26.26358979, version 1) fine-tune the published CpGPT methylation foundation model (Cancer-100M checkpoint) on plasma cfDNA targeted bisulfite data (EpiPanGI Dx, GSE149438) and compare it with SVM, elastic net, GBM and random forest on the same features and the same three train/validation/test partitions (Table 3). It is the only evaluation of a methylation foundation model on cfDNA with conventional comparators found in the window, and the authors did not develop CpGPT.

## Record design

- One source (PDF, not archived: no reuse licence). Table 3 extracted in full: 15 results with 95% CIs.
- One dataset, one protocol, two methods, five configurations, five evaluations. CpGPT `independent_paper`; the classical baselines `author_reported`.
- One relevance judgement, `proxy`.

## Things a reviewer should judge

1. **Leakage.** The 20,499 CpG features were selected with labels of all 300 samples, including the test partitions; the authors say so.
2. **Size.** Test partitions are about 30 samples with few controls; CIs over three split-runs are wide and bounded at 1.
3. **Preprint and licence.** Not peer reviewed; all rights reserved, so no archive copy.
