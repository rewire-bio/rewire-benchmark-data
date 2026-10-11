# Research notes

Part of the 2026-10-11 pathogen use-case literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-uc-pathogens/ledger.jsonl` and the pass report in `data/omics/lit-search-20261011-uc-pathogens/report.md`.

## Why this source

Pathogen-free negative controls (human genome reads, mouse RNA, environmental libraries) and divergent positive-control genomes bear on both use cases' questions about background signal and organisms poorly represented in the reference, and on the RNA gap 'no RNA virus spike-in or reference-material comparison of workflows'. It is the only new multi-tool viral comparison found in the window.

## Record counts

- benchmark: 1
- claim: 6
- configuration: 5
- dataset: 3
- evaluation: 15
- method: 4
- protocol: 3
- result: 105
- source: 2

All records were extracted as `needs_review` and set to `source_checked` after the independent review in `review.md`.

## Relevance judgements (drafts)

- `use-case-mapping-dna-pathogen-20261011-tisza2026-neg` on `use-case-diagnostic-dna-pathogen-identification`: proxy; protocol `rna-pathogen-20261011-tisza2026-protocol-neg`; headline false-positive-count; group `tisza2026-virus-profilers` stratum 2 ('Pathogen-free negative controls').
- `use-case-mapping-dna-pathogen-20261011-tisza2026-pos` on `use-case-diagnostic-dna-pathogen-identification`: proxy; protocol `rna-pathogen-20261011-tisza2026-protocol-pos`; headline recall; group `tisza2026-virus-profilers` stratum 1 ('Positive controls (divergent genomes)').
- `use-case-mapping-rna-pathogen-20261011-tisza2026-mock` on `use-case-diagnostic-rna-pathogen-detection`: proxy; protocol `rna-pathogen-20261011-tisza2026-protocol-mock`; headline f1-score; group `tisza2026-virus-profilers` stratum 3 ('Mutated mock communities').
- `use-case-mapping-rna-pathogen-20261011-tisza2026-neg` on `use-case-diagnostic-rna-pathogen-detection`: proxy; protocol `rna-pathogen-20261011-tisza2026-protocol-neg`; headline false-positive-count; group `tisza2026-virus-profilers` stratum 2 ('Pathogen-free negative controls').
- `use-case-mapping-rna-pathogen-20261011-tisza2026-pos` on `use-case-diagnostic-rna-pathogen-detection`: proxy; protocol `rna-pathogen-20261011-tisza2026-protocol-pos`; headline recall; group `tisza2026-virus-profilers` stratum 1 ('Positive controls (divergent genomes)').

## Not extracted

Parameter sweeps (S5, S10, S22, S24), LD50 (S4), model coefficients and contrasts (S1, S3, S11, S12), test statistics (S7, S8, S17 to S21), calibration (S13), robustness (S14, S23), timing (S15) and the Zenodo data.

## Questions put to the reviewer

1. Developer benchmark: EsViritu authors ran every comparator and chose headline settings (origin author_reported for all five tools).
2. S2 values are model-estimated detection probabilities (Firth regression marginal means), recorded as recall with a qualifier; check the metric choice.
3. Kraken2 version printed 'v2.17.1' followed by reference marker 19; recorded as 2.17.1 with a note.
4. Numeric cells are stored floats; printed_value is the shortest round-trip decimal (for example 0.727 for 0.72699999999999998), following the 2026-10-09 RNA batch convention.
5. New metric concept bray-curtis-dissimilarity (unmapped) needs vocabulary review.
6. Judgements are proposed on both use cases (three RNA, two DNA). Check whether the DNA ones should be kept.
