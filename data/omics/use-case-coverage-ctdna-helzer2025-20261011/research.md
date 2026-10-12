# Research: Helzer et al. 2025 fragmentomic metrics on targeted panels, 2026-10-11

Use case: `use-case-plasma-ctdna-fragmentomics`.

Bounds: window 2025-10-01 to 2026-10-11; about 30 queries per use case for the whole uc-ctdna pass (26 logged); at most about 6 sources extracted across both use cases. Lane `genomics`. Worker: Claude (Opus 5.5) research agent uc-ctdna; no human review claimed. The search log is `data/omics/lit-search-20261011-uc-ctdna/ledger.jsonl` and the pass report is `data/omics/lit-search-20261011-uc-ctdna/report.md`.

## Why this source

Helzer et al. 2025 (Nature Communications, 10.1038/s41467-025-64153-z, published 2025-10-14) re-implement thirteen whole-genome fragmentomic metrics, and Griffin in one cohort, on targeted exon-panel cfDNA data and compare them with one classifier on shared folds in two cohorts (UW, 431 samples; public GRAIL panel data of Razavi et al. 2019, 198 samples), on the full panels and on gene subsets of three commercial panels. It is the largest same-sample comparison of fragmentomic feature definitions found in the window, and most metrics come from other groups.

## Record design

- Two sources (article XML, archived; supplementary PDF). Both supplementary tables extracted in full: 790 results.
- Two datasets, eight protocols (cohort x panel), 14 methods and 14 configurations (one per metric), 105 evaluations.
- Each phenotype column is a one-vs-rest AUROC from a multinomial model, stored with the class in `metric_qualifier`; 'Normal' is healthy vs all cancers, the column that bears on detection. 'Mean AUROC' is stored with its own qualifier.
- Two relevance judgements (`proxy`), on the full-panel protocols only. The commercial-panel protocols are stored for completeness but not mapped.
- A generic Griffin method record is added here and reused by the Fragmentia-AI batch, so this batch must be added first.

## Things a reviewer should judge

1. **Table labels.** The article cites the UW results as Table S1 and GRAIL as Table S2; the PDF captions say the reverse. Values quoted in the text match the PDF tables as captioned. Locators follow the PDF.
2. **Origin split.** `author_reported` for E1 SE, All Exons SE and All Combined (the authors' 2023 entropy metric and its extensions); `independent_paper` for the others. All are the authors' re-implementations on panel exons.
3. **Relevance.** `proxy`: targeted panels rather than WGS, metastatic cancers, AUROC only, and the low-fraction mixing analysis is figure-only.
4. **Mapping scope.** Whether the six commercial-panel protocols should also be mapped.
