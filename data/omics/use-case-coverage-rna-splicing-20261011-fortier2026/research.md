# Research: Fortier, Rudy and Scherer 2026, Analyzing the performance of deep learning splice prediction algorithms (PLOS One)

Use case: `use-case-patient-rna-splicing-validation`. Pass: 2026-10-11 use-case literature search (window 2025-10-01 to 2026-10-11); the full query log is in `data/omics/lit-search-20261011-uc-splicing-cnv/ledger.jsonl` and the report in the same folder.

## Decisions

| Item | Decision | Reason |
| --- | --- | --- |
| Tables 1 to 6, all 96 cells | Extracted | Independent comparison of SpliceAI, CI-SpliceAI and OpenSpliceAI with a legacy ensemble on six splice benchmarks, four with experimental labels. |
| Tables 7 and 8 | Not extracted | Agreement of reimplementation scores and positions with SpliceAI, not accuracy against a truth set. |

## Modelling choices

- One protocol and one dataset per table: variant sets, labels and thresholds differ.
- Threshold policy differs by table (0.5, or optimised per algorithm and gene); recorded in each evaluation's comparison.adaptation and the result qualifier.
- New model records for OpenSpliceAI and CI-SpliceAI; SpliceAI reuses catalog-model-spliceai; the Legacy Ensemble is a new method record.
- Legacy Ensemble rows are author_reported because the authors' employer supplies VarSeq; the deep learning rows are independent_paper.
- No judgement for Tables 5 and 6: their labels are ClinVar clinical classifications, not splicing outcomes.

## Things a reviewer should judge

1. Prose and table disagree in two places (OpenSpliceAI SPiP balanced accuracy 0.787 versus 0.797; SpliceAI Riepe F1 and balanced accuracy swapped in the prose); recorded as source limitations, table values stored.
2. Whether the Riepe, CI-SpliceAI, SPiP and Barbosa deep intronic protocols should also be judged for use-case-splicing-follow-up (experimental splicing outcomes) is left to the reviewer and lead.

## Record counts

| Kind | Records |
| --- | --- |
| claim | 4 |
| configuration | 4 |
| dataset | 6 |
| evaluation | 24 |
| method | 1 |
| model | 2 |
| protocol | 6 |
| result | 96 |
| source | 1 |

All records have status `needs_review`. Nothing was executed or reproduced; values are transcribed from the pinned source.

After independent review (reviewer-scnv, 2026-10-12) the reviewed records are `source_checked`; the corrections and anything held are listed in review.md.
