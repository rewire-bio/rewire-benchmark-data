# AMP #11: Tumour RNA fusion detection

Primary source: Discovery of clinically relevant fusions in pediatric cancer. https://doi.org/10.1186/s12864-021-08094-z
Retrieved: 2026-10-07T12:25:20.810843+00:00; source-byte SHA256: a5fd574d3b186fa29f835aff44491e1d1d0447ea2352f627c21f95ca666e9225

Evidence scope: synthetic RNA reference-standard proxy; additional clinical-cohort ascertainment in same article

Consensus ≥3 callers, with specified filtering and known fusion list rescue; Table 2 displays mean of duplicate undiluted experiments. Only 14 Seraseq fusions are positive; all others counted false positive. Comparators processed by same authors.

Population: 14 cancer-associated synthetic fusion RNAs in GM24385 background; duplicate experiments
Input: 500 ng input; rRNA depletion and NEBNext Ultra II directional RNA-seq; HiSeq 4000 2×151 bp, overall Seraseq mean 149 million read pairs (range 86–227 million)

## Numerical extraction

- Arriba: sensitivity = 92.9% %; Table 2, Arriba row, corresponding column (JATS Tab2). Uncertainty: None.
- Arriba: precision = 55.3% %; Table 2, Arriba row, corresponding column (JATS Tab2). Uncertainty: None.
- Arriba: mean total fusions identified = 23.5 fusions; Table 2, Arriba row, corresponding column (JATS Tab2). Uncertainty: None.
- Arriba: mean Seraseq fusions identified = 13 fusions; Table 2, Arriba row, corresponding column (JATS Tab2). Uncertainty: None.
- STAR-Fusion: sensitivity = 100.0% %; Table 2, STAR-Fusion row, corresponding column (JATS Tab2). Uncertainty: None.
- STAR-Fusion: precision = 43.6% %; Table 2, STAR-Fusion row, corresponding column (JATS Tab2). Uncertainty: None.
- STAR-Fusion: mean total fusions identified = 32 fusions; Table 2, STAR-Fusion row, corresponding column (JATS Tab2). Uncertainty: None.
- STAR-Fusion: mean Seraseq fusions identified = 14 fusions; Table 2, STAR-Fusion row, corresponding column (JATS Tab2). Uncertainty: None.
- EnFusion 3 callers: sensitivity = 100.0% %; Table 2, EnFusion 3 callers row, corresponding column (JATS Tab2). Uncertainty: None.
- EnFusion 3 callers: precision = 90.3% %; Table 2, EnFusion 3 callers row, corresponding column (JATS Tab2). Uncertainty: None.
- EnFusion 3 callers: mean total fusions identified = 15.5 fusions; Table 2, EnFusion 3 callers row, corresponding column (JATS Tab2). Uncertainty: None.
- EnFusion 3 callers: mean Seraseq fusions identified = 14 fusions; Table 2, EnFusion 3 callers row, corresponding column (JATS Tab2). Uncertainty: None.
- EnFusion 3 callers + filter + known fusion list: sensitivity = 100.0% %; Table 2, EnFusion 3 callers + filter + known fusion list row, corresponding column (JATS Tab2). Uncertainty: None.
- EnFusion 3 callers + filter + known fusion list: precision = 100.0% %; Table 2, EnFusion 3 callers + filter + known fusion list row, corresponding column (JATS Tab2). Uncertainty: None.
- EnFusion 3 callers + filter + known fusion list: mean total fusions identified = 14 fusions; Table 2, EnFusion 3 callers + filter + known fusion list row, corresponding column (JATS Tab2). Uncertainty: None.
- EnFusion 3 callers + filter + known fusion list: mean Seraseq fusions identified = 14 fusions; Table 2, EnFusion 3 callers + filter + known fusion list row, corresponding column (JATS Tab2). Uncertainty: None.

## Baselines

- Arriba v1.2.0
- STAR-Fusion v1.6.0
- MapSplice v2.2.1
- FusionCatcher v0.99.7c
- CICERO v0.3.0
- JAFFA direct v1.09
- FusionMap v mono-2.10.9

## Limits and unknowns

- The optimized known-fusion rescue uses prior knowledge of true reference fusions; 100% precision/sensitivity is an optimization-control observation, not unbiased generalization.
- Table2 caption v3 versus optimization narrative v2 is unresolved; dataset_version=null and automatic comparison blocked.
- STAR-Fusion precision 43.6% in Table2 vs 43.8% Par31; numeric candidate retains printed table value but requires disputed-result warning or omission pending resolution.
- All non-Seraseq fusions counted false positives although endogenous background fusions may exist.
- No CI or dispersion printed for Table2 rows.
- Clinical Table1 sensitivity is relative to 67 fusions ascertained through optimized ensemble, not independently exhaustive truth or treatment benefit.

Missing metadata: {"dataset_version": "Table 2 caption says v3; Fig1 and Par31/50 discuss undiluted v2. Do not resolve silently.", "pipeline_version": "EnFusion software release/commit not established", "metric_implementation": "Printed percentage retained; per-replicate aggregation details not extracted", "budget": "Unknown"}

Candidate status is needs_review. Main text/XML inspected by automated curator; no experimental reproduction or human scientific review. No clinical benefit claimed. See candidates.json for integration metadata.

## Additional actual patient-cohort endpoint

Table 1 (JATS Tab1), STAR-Fusion v1.6.0 row: 94.0% sensitivity (63/67 clinically relevant fusions); Arriba v1.2.0: 88.1% (59/67). The denominator is 67 EnFusion-ascertained fusions in 229 NCH pediatric/hematologic samples, not an independent exhaustive truth set. This is separate from the synthetic controls. Population: 138 CNS, 73 solid tumors, 18 hematologic malignancies/disorders. No uncertainty printed. Ascertainment bias prevents a clinical accuracy or benefit claim.
