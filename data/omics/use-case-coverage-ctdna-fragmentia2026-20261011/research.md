# Research: Fragmentia-AI cfDNA language model against fragmentomic feature sets (Table S5), 2026-10-11

Use case: `use-case-plasma-ctdna-fragmentomics`.

Bounds: window 2025-10-01 to 2026-10-11; about 30 queries per use case for the whole uc-ctdna pass (26 logged); at most about 6 sources extracted across both use cases. Lane `genomics`. Worker: Claude (Opus 5.5) research agent uc-ctdna; no human review claimed. The search log is `data/omics/lit-search-20261011-uc-ctdna/ledger.jsonl` and the pass report is `data/omics/lit-search-20261011-uc-ctdna/report.md`.

## Why this source

Xu et al. 2026 (Cell Reports Medicine, 10.1016/j.xcrm.2026.102866) present Fragmentia-AI, a DNABERT-2 based fragment-level language model, and in Table S5 compare it on the same 0.1x ULP-WGS training and held-out validation cohorts with six fragmentomic feature sets (DELFI, Griffin, FRAGMA, FDI, nucleosome, subnucleosome), each trained with random forest, XGBoost and a deep learning classifier. It is the only head-to-head of a cfDNA foundation-model approach against established fragmentomic baselines found in the window.

## Record design

- Two sources (article XML; Document S1 PDF), Table S5 extracted in full: 19 AUC results, with the printed p value against Fragmentia-AI in `reported_p_value`.
- One dataset, one protocol, 19 configurations (6 feature sets x 3 classifiers, plus Fragmentia-AI), 19 evaluations: the Fragmentia-AI evaluation `author_reported` and the 18 baselines `independent_paper` (review F1).
- DELFI configurations point at the stored DELFI feature-definition method; Griffin at the method added by the Helzer et al. 2025 batch. FRAGMA, FDI, nucleosome and subnucleosome get new method records whose descriptions say only what the paper prints.
- One relevance judgement, `proxy`.

## Things a reviewer should judge

1. **Split.** The held-out validation set behind Table S5 is not sized or described; the same paragraph calls the same-platform AUC 0.956 and 0.97.
2. **p values.** The test is not named.
3. **Baselines.** Re-implemented by the developer; FRAGMA, FDI, nucleosome and subnucleosome are not defined in the paper.
4. **Panel-sequencing results** (Tables S1-S3) are single-model and were not extracted.
