# Research notes

Part of the 2026-10-11 pathogen use-case literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-uc-pathogens/ledger.jsonl` and the pass report in `data/omics/lit-search-20261011-uc-pathogens/report.md`.

## Why this source

A clinical-cohort comparison of two complete DNA mNGS workflows against three reference standards, including a composite reference. The use case's stated gaps are that multi-tool evidence comes only from mock communities or constructed metagenomes, and that no comparison on clinical specimens with an adjudicated reference was found.

## Record counts

- benchmark: 1
- claim: 4
- configuration: 2
- dataset: 1
- evaluation: 6
- method: 1
- protocol: 3
- result: 108
- source: 2

All records were extracted as `needs_review` and set to `source_checked` after the independent review in `review.md`.

## Relevance judgements (drafts)

- `use-case-mapping-dna-pathogen-20261011-hu2026-cmt` on `use-case-diagnostic-dna-pathogen-identification`: proxy; protocol `dna-pathogen-20261011-hu2026-protocol-cmt`; headline recall; group `hu2026-balf-ngs-tgs` stratum 2 ('Clinical microbiological tests (CMT)').
- `use-case-mapping-dna-pathogen-20261011-hu2026-crs` on `use-case-diagnostic-dna-pathogen-identification`: proxy; protocol `dna-pathogen-20261011-hu2026-protocol-crs`; headline recall; group `hu2026-balf-ngs-tgs` stratum 3 ('Composite reference standard (CRS)').
- `use-case-mapping-dna-pathogen-20261011-hu2026-culture` on `use-case-diagnostic-dna-pathogen-identification`: proxy; protocol `dna-pathogen-20261011-hu2026-protocol-culture`; headline recall; group `hu2026-balf-ngs-tgs` stratum 1 ('Culture').

## Not extracted

Mock-community detection (Supplemental Tables S1 and S2, Figures 2 and 3): per-organism rows; the prose aggregates (100% (50/50), 43.3% (13/30), 6.7% (2/30)) were not recorded. Table 1 (mixed model) and Supplemental Tables S3 and S4 (read output, correlations) are not detection endpoints.

## Questions put to the reviewer

1. Table 2 HD-ONT NPA against CMT is printed 79.2% but the block's counts give 42/52 = 80.8% (source_anomaly on the result). Decide whether a result-level dispute is warranted.
2. The CRS adds organisms detected by both sequencing workflows (incorporation bias). Check the limitation wording.
3. A co-corresponding author is from Genskey (clinical mNGS provider) while the article declares no conflict; origin is author_reported. Confirm.
4. Organism scope (all, bacteria, fungi) is held in metric_qualifier within one protocol per reference standard; check that this grouping is acceptable.
