# Research: Alavi 2026, Probing Genomic Foundation Models with Splice-Variant Perturbations (bioRxiv)

Use case: `use-case-patient-rna-splicing-validation`. Pass: 2026-10-11 use-case literature search (window 2025-10-01 to 2026-10-11); the full query log is in `data/omics/lit-search-20261011-uc-splicing-cnv/ledger.jsonl` and the report in the same folder.

## Decisions

| Item | Decision | Reason |
| --- | --- | --- |
| Table III (96 cells) and Table IV (72 cells) | Extracted | Six splice predictors and genomic foundation models (NTv3 650M, Evo2 40B, Genos 10B) on variants with established splicing defects; Table IV is a held-out set confirmed by patient RNA studies. |
| Supplementary Tables I to VI, ROC-AUC and PR-AUC | Not extracted | Supplement not retrieved; AUCs are in prose and figures only. |

## Modelling choices

- Three protocols: OPA1 evaluation sets (thresholds tuned on them), OPA1 extended corpus positive-call rates (no labels), and the 65-gene test set.
- Cells print 'count (percent)'; printed_value keeps the cell, numeric_value is the percentage, unit_detail says so. Type II error uses the proportion concept with a qualifier because the vocabulary has no false-negative-rate concept.
- Configurations reuse catalog-model-spliceai, catalog-model-alphagenome, regulatory-variant-20261009-model-borzoi, lit-genomics-20261011-guanine-model-nucleotide-transformer-v3 and catalog-model-evo-2; Genos was a new model record; after review it reuses lit-microbial-20261011-virobench-model-genos (review correction 1).
- The Genos 10B row is taken as ZhejiangLab/Genos-10B (v1) because Results H says the table configuration outperformed the v2 iteration, which is in Supplementary Table III; a reviewer should confirm.

## Things a reviewer should judge

1. Two Table IV percentages do not match their counts (15 of 107 printed 13.9%; 31 of 107 printed 28.7%); recorded as a source limitation.
2. Relevance proxy for both judged protocols; the extended-corpus protocol has no truth labels and is not judged.

## Record counts

| Kind | Records |
| --- | --- |
| claim | 2 |
| configuration | 12 |
| dataset | 3 |
| evaluation | 36 |
| model | 1 |
| protocol | 3 |
| result | 168 |
| source | 1 |

All records have status `needs_review`. Nothing was executed or reproduced; values are transcribed from the pinned source.

After independent review (reviewer-scnv, 2026-10-12) the reviewed records are `source_checked`; the corrections and anything held are listed in review.md.
