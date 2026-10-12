# Research: Hwang et al. 2026, Improving CNV Detection Performance Except for Software-Specific Problematic Regions (Genes)

Use case: `use-case-cnv-detection-characterisation`. Pass: 2026-10-11 use-case literature search (window 2025-10-01 to 2026-10-11); the full query log is in `data/omics/lit-search-20261011-uc-splicing-cnv/ledger.jsonl` and the report in the same folder.

## Decisions

| Item | Decision | Reason |
| --- | --- | --- |
| Table 4, all 48 cells | Extracted | Four exome CNV callers against CMA truth, before and after removing tool-specific problematic regions; covers duplications. |
| Tables 1 to 3 | Not extracted | Reference set description, call counts and true/false-negative features; no per-tool accuracy. |

## Modelling choices

- Two protocols (pre-filter and post-filter) because the reference exon set changes after filtering.
- Pre-filter evaluations independent_paper; post-filter author_reported (the filter is the authors' method).
- CNVkit is a new method record; ExomeDepth, CoNIFER and cn.MOPS reuse existing records.

## Things a reviewer should judge

1. Abstract and Results prose disagree slightly with Table 4 (14.4% versus 14.5 points; 7.9% versus 7.7 points; 'five-fold' versus about four-fold); recorded as source limitations.
2. Relevance proxy: exome, not whole-genome, input.

## Record counts

| Kind | Records |
| --- | --- |
| claim | 2 |
| configuration | 8 |
| dataset | 1 |
| evaluation | 8 |
| method | 1 |
| protocol | 2 |
| result | 48 |
| source | 1 |

All records have status `needs_review`. Nothing was executed or reproduced; values are transcribed from the pinned source.

After independent review (reviewer-scnv, 2026-10-12) the reviewed records are `source_checked`; the corrections and anything held are listed in review.md.
