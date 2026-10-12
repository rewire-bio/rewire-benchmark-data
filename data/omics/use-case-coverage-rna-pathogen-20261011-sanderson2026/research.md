# Research notes

Part of the 2026-10-11 pathogen use-case literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-uc-pathogens/ledger.jsonl` and the pass report in `data/omics/lit-search-20261011-uc-pathogens/report.md`.

## Why this source

A prospective validation of an RNA metagenomic workflow on 344 respiratory swabs against the original clinical PCR panel, with thresholds fixed on a separate derivation set. It matches the use case's inputs and output closely and bears on the gap that no prospective RNA cohort was found.

## Record counts

- claim: 2
- configuration: 2
- dataset: 1
- evaluation: 2
- method: 1
- protocol: 1
- result: 14
- source: 1

All records were extracted as `needs_review` and set to `source_checked` after the independent review in `review.md`.

## Relevance judgements (drafts)

- `use-case-mapping-rna-pathogen-20261011-sanderson2026-validation` on `use-case-diagnostic-rna-pathogen-detection`: proxy; protocol `rna-pathogen-20261011-sanderson2026-protocol-validation`; headline recall; group `sanderson2026-nanopore-nps` stratum 1 ('Validation set').

## Not extracted

Table 3 (image) and Figures 3 to 7; derivation-set results; the Abstract's specificity counts (recorded only as a source_anomaly); subtyping and cost results.

## Questions put to the reviewer

1. Abstract specificity 3836/3845 against Results 3901/3910 (source_anomaly on the pre-specified specificity result). Decide between a result note, a result-level dispute and a source concern.
2. Alternative-criterion sensitivity 159/274: the sentence calls 274 'samples passing batch controls', while 260 elsewhere counts PCR-positive targets (source_anomaly).
3. The judgement is proposed as direct (pre-specified criteria validated on an independent prospective set, same endpoint as the use case's anchor). The alternative criterion is post hoc. Decide direct or proxy, or exclude the alternative evaluation.
4. Per-pathogen sensitivities are recorded under the pre-specified evaluation, as the Results paragraph states ('using pre-specified criteria').
