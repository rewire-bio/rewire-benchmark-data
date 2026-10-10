# Research: BRCA1/BRCA2 germline interpretation use-case pass, 2026-10-09

Use case: `use-case-brca1-brca2-germline-interpretation` ("Which evidence-support methods improve BRCA1/BRCA2 variant review without increasing serious classification errors?"). Existing evidence: ten judgements from the ENIGMA specification, Benet-Pages, the HECTOR preprint, Hu 2026 and So 2024. Their sources are not duplicated.

Bounds: cutoff 2026-10-09; 2 of 25 queries; 2 papers (3 source records) of 3. Lane `genomics`. Ledger IDs `search-use-case-brca-germline-genomics-q1` and `-q2`.

## Queries

| # | Query (abridged) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | BRCA1 or BRCA2, functional assay or MAVE, named predictors, sensitivity or likelihood ratio | Europe PMC | Both sources selected; Hum Mutat 2026 panel study opened and excluded |
| 2 | Title search for BRCA1/2 in silico tool performance | Europe PMC | Ernst et al. 2018 opened and excluded |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Cubuk et al. 2021, Supplementary Tables 6 and 9 (BRCA1 and BRCA2 columns) | Extract 504 results | 44 tools at 70 thresholds plus 14 concordance combinations against two clinical-grade functional truth sets, with counts. False negatives are the serious error if a tool is used for BP4. No author developed the tools |
| Ramadane-Morchadi et al. 2025, Tables 1 and 2 | Extract 54 results | Compares AlphaMissense and FoldX ΔΔG with the BayesDel thresholds in the BRCA1 VCEP specification, as PP3/BP4 evidence strength and as binary sensitivity and NPV |
| Ramadane-Morchadi et al. 2025, Table 3 | Not extracted | Breast cancer odds ratios; the use case excludes individual risk estimation |
| Ernst et al. 2018 | Excluded | Per-tool results not in article tables; four older tools |
| Hum Mutat 2026 panel study | Excluded | Results in figures and a supplementary workbook |

This is a scoped extraction of Cubuk: the other genes, the pooled and ClinVar columns, and Supplementary Tables 8, 10, 11 and 13 are left out (recorded in `coverage.json`).

## Modelling choices

- Four protocols, one judgement each: Cubuk BRCA1 and BRCA2 (one comparison group, two strata), Ramadane-Morchadi Table 1 and Table 2. All `proxy`: functional class stands in for clinical classification, and no source measures complete classifications, reviewer errors or time.
- Cubuk's positive likelihood ratio is stored as `likelihood-ratio`. Its "negative likelihood ratio" is TNR/FNR (Supplementary Table 7), the reciprocal of the store's `likelihood-ratio` definition for the below-threshold interval, so it is stored under a new concept `benignity-likelihood-ratio` (direction higher). Ramadane-Morchadi's log2 LR is stored under a new concept `log2-likelihood-ratio`, with direction lower for BP4 ranges and higher for PP3 ranges.
- False-negative counts carry the number of deleterious variants with a call as `denominator`. Likelihood ratios carry the number of variants with a call; tools with an intermediate band and the combinations drop variants, so denominators differ by row.
- One configuration per Cubuk tool-threshold row (84) and per Ramadane-Morchadi threshold pair (8). Table 2 evaluations reuse the threshold-pair configuration whose PP3 cut they use. Combinations have no `configuration_of`; they link `uses_model` to each component method. MSC configurations link `configuration_of` to MSC and `uses_model` to the scored tool.
- Methods: 16 new family records. BayesDel reuses `uc-clinical-20260930-method-bayesdel`; 27 others reuse reviewed records in the unmerged somatic oncogenicity batch, and FoldX reuses the protein stability batch's record. VEST3 configurations link to the oncogenicity record named "VEST4", which is a family record.
- Method types follow Cubuk Supplementary Table 1 (statistical, consensus and conservation scores as `specialist`; trained models as `supervised_machine_learning`). My classification; needs review.

## Things a reviewer should judge

1. Cubuk's printed benignity-ratio intervals have the PLR interval's width in every BRCA1/BRCA2 cell and are not consistent with the counts. They are not recorded as structured uncertainty. Whether this warrants a source `evidence_concern` (which would withhold both Cubuk judgements).
2. Zero-count rows: printed values match a Haldane correction the Table 9 note does not mention (62 results marked).
3. Ramadane-Morchadi Table 2 NPV for ΔΔG AF ≥+3 (interval 92.3-97.5 around 96.6), marked as a possible misprint.
4. The two new metric concepts.
5. The dependency on two unmerged batches, and the VEST4 record name.
6. Cubuk's BayesDel "gene-specific" thresholds are not the VCEP thresholds; readers may confuse them with the ENIGMA judgements.

## Coverage

Bounded pass. Not covered: complete-classification or reviewer-error studies, BRCA2 saturation genome editing (Huang et al. 2025), splicing predictors, non-missense variants, and the unextracted Cubuk and Ramadane-Morchadi supplementary tables.
