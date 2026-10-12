# Research: Silverstein et al. 2026, Benchmarking RNA-seq Tools for Real-World Diagnostic Applications (medRxiv)

Use case: `use-case-patient-rna-splicing-validation`. Pass: 2026-10-11 use-case literature search (window 2025-10-01 to 2026-10-11); the full query log is in `data/omics/lit-search-20261011-uc-splicing-cnv/ledger.jsonl` and the report in the same folder.

## Decisions

| Item | Decision | Reason |
| --- | --- | --- |
| Table S9, all 81 cells | Extracted | Only per-tool table of TP, FN, TN, FP, accuracy, precision, recall, F1 and MCC; the use case had no false-positive evidence in a table. |
| Tables S3 to S5, S7, S8 (per-event Yes/No) | Not extracted | Per-event detection behind Table S9; a later pass could add them as event-detected results like Segarra-Casas et al. |
| Figure 2A per-tissue recall; Table 1 (image) | Not extracted | Figure values and an image table are not read. |

## Modelling choices

- Three protocols (splicing, expression, allelic imbalance) because the truth sets differ (events versus genes) even though Table S9 is one sheet.
- Denominators differ by tool within the splicing protocol; each evaluation's comparison.population states which tissue sets the tool ran on, which blocks automatic comparison between tools with different populations.
- ANEVA-H is author_reported (the ANEVA-h preprint, reference 36, shares authors with this paper); all other rows independent_paper.
- New method records: MINTIE, ANEVA-h and the DROP MAE module. FRASER, LeafCutterMD, rMATS-turbo and OUTRIDER reuse the 2026-10-09 method records.

## Things a reviewer should judge

1. Five discrepancies are recorded on the supplement source: 22 versus 21 true-negative samples, OUTRIDER + GTEx 83% (prose) versus 4 of 5 (Table S9), LeafcutterMD 67 versus FRASER 68 positives, a typed 0 for LeafcutterMD F1, and per-tool denominators. A reviewer should decide whether any should be an evidence concern that blocks comparison rather than a limitation.
2. Relevance: splicing protocol judged direct, expression and allelic imbalance proxy.
3. MCC is negative for every tool because true negatives are counted per sample with any outlier as a false positive; the authors say this underestimates predictive ability.

## Record counts

| Kind | Records |
| --- | --- |
| claim | 4 |
| configuration | 9 |
| dataset | 1 |
| evaluation | 9 |
| method | 3 |
| protocol | 3 |
| result | 81 |
| source | 2 |

All records have status `needs_review`. Nothing was executed or reproduced; values are transcribed from the pinned source.

After independent review (reviewer-scnv, 2026-10-12) the reviewed records are `source_checked`; the corrections and anything held are listed in review.md.
