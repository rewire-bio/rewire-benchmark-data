# Research: Zhang, Zhang and Chen 2026, Can automated CNV pathogenicity prediction tools replace manual review under the ACMG framework? (Global Medical Genetics)

Use case: `use-case-cnv-detection-characterisation`. Pass: 2026-10-11 use-case literature search (window 2025-10-01 to 2026-10-11); the full query log is in `data/omics/lit-search-20261011-uc-splicing-cnv/ledger.jsonl` and the report in the same folder.

## Decisions

| Item | Decision | Reason |
| --- | --- | --- |
| Tables 3 (35 cells) and 4 (30 cells) | Extracted | Independent comparison of five automated ACMG CNV classifiers against 3,031 expert-classified CNVs, split by duplication and deletion. |
| Supplementary Table S1 (MarCNV-ISV modes) | Not extracted | Supplement not retrieved; mode values appear in Discussion prose only. |

## Modelling choices

- Three protocols: five-category (Table 3) and three-category per-class agreement for duplications and for deletions (Table 4).
- Table 4 'Accuracy' per reference class is recorded as recall with a qualifier, because it is the share of that class assigned to it.
- Five new method records and configurations; only AnnotSV has a printed version (v3.5.2).

## Things a reviewer should judge

1. How Table 3 averages the five classes is not stated; comparison.aggregation is unreported, which blocks automatic comparison.
2. Relevance proxy: classification of detected CNVs bears on characterisation and analyst assessment, not detection. A reviewer may prefer outside_scope.

## Record counts

| Kind | Records |
| --- | --- |
| claim | 3 |
| configuration | 5 |
| dataset | 1 |
| evaluation | 15 |
| method | 5 |
| protocol | 3 |
| result | 65 |
| source | 1 |

All records have status `needs_review`. Nothing was executed or reproduced; values are transcribed from the pinned source.

After independent review (reviewer-scnv, 2026-10-12) the reviewed records are `source_checked`; the corrections and anything held are listed in review.md.
