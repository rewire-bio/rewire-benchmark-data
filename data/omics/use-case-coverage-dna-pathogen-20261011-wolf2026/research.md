# Research notes

Part of the 2026-10-11 pathogen use-case literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-uc-pathogens/ledger.jsonl` and the pass report in `data/omics/lit-search-20261011-uc-pathogens/report.md`.

## Why this source

The use case's anchor is the Karius plasma mcfDNA assay with agreement against blood culture. This is a second, prospective cohort for the same assay type and endpoint, from a different site and population, with the laboratory masked to sample status.

## Record counts

- benchmark: 1
- claim: 4
- configuration: 2
- dataset: 2
- evaluation: 4
- protocol: 3
- result: 44
- service: 1
- source: 1

All records were extracted as `needs_review` and set to `source_checked` after the independent review in `review.md`.

## Relevance judgements (drafts)

- `use-case-mapping-dna-pathogen-20261011-wolf2026-diagnosis` on `use-case-diagnostic-dna-pathogen-identification`: proxy; protocol `dna-pathogen-20261011-wolf2026-protocol-diagnosis`; headline recall; group `wolf2026-plasma-mcfdna` stratum 1 ('Diagnosis (day 0 or 1)').
- `use-case-mapping-dna-pathogen-20261011-wolf2026-prediction` on `use-case-diagnostic-dna-pathogen-identification`: proxy; protocol `dna-pathogen-20261011-wolf2026-protocol-prediction`; headline recall; group `wolf2026-plasma-mcfdna` stratum 2 ('Prediction (day -3 to -1)').
- `use-case-mapping-dna-pathogen-20261011-wolf2026-specificity` on `use-case-diagnostic-dna-pathogen-identification`: proxy; protocol `dna-pathogen-20261011-wolf2026-protocol-specificity`; headline specificity; group `wolf2026-plasma-mcfdna` stratum 3 ('Control samples').

## Not extracted

Day-by-day sensitivity (Figure 2 and appendix), regression results and the appendix PDF were not extracted. The post-hoc 140 molecules per microlitre diagnostic sensitivity (80.7%) is printed only in prose and was not recorded.

## Questions put to the reviewer

1. The diagnosis judgement is proposed as direct: same assay type (Karius plasma mcfDNA) and endpoint (agreement with blood culture) as the use case's anchor, in a paediatric high-risk leukaemia population. Decide direct or proxy.
2. Karius provided testing and took part in processing and analysis; one author is a Karius employee. Origin recorded as author_reported.
3. Table 3 specificity denominators are taken as 162 from the column header 'Negative (n=162)'; the cutoff rows use the same denominator.
