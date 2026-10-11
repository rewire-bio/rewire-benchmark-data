# Research notes

Part of the 2026-10-11 pathogen use-case literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-uc-pathogens/ledger.jsonl` and the pass report in `data/omics/lit-search-20261011-uc-pathogens/report.md`.

## Why this source

Two DNA sequencing workflows on blood (targeted bstNGS and untargeted mNGS) compared with conventional tests on the same 122 patients against an adjudicated clinical diagnosis. It bears on the gap 'no independent comparison of workflows on clinical DNA specimens with printed per-tool values'.

## Record counts

- claim: 2
- configuration: 4
- dataset: 1
- evaluation: 4
- method: 4
- protocol: 1
- result: 80
- source: 1

All records were extracted as `needs_review` and set to `source_checked` after the independent review in `review.md`.

## Relevance judgements (drafts)

- `use-case-mapping-dna-pathogen-20261011-huang2026-clinical-diagnosis` on `use-case-diagnostic-dna-pathogen-identification`: proxy; protocol `dna-pathogen-20261011-huang2026-protocol-clinical-diagnosis`; headline recall; group `huang2026-blood-sepsis` stratum 1 ('122 ICU patients').

## Not extracted

Figures 2 to 4 (detection rates, concordance with BALF, survival) are not extracted. Supplementary methods (DOCX) and STable 1 (panel organism list) were not retrieved.

## Questions put to the reviewer

1. The reference diagnosis incorporates NGS and CMT results; CMT is both a comparator and part of the reference.
2. Fungal blood culture PPV printed 0.00% (0.00% to 0.00%) with a zero denominator (source_anomaly).
3. The p value column is attached to accuracy as reported_p_value because Results paragraph 'Comparative diagnostic performance' ties the p values to accuracy; Table 2 does not label which metric the p value tests. Confirm.
4. Licence CC BY-NC-ND: no artifact archived.
