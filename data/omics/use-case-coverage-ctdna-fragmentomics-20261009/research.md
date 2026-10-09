# Research: plasma ctDNA fragmentomics use-case pass, 2026-10-09

Use case: `use-case-plasma-ctdna-fragmentomics` ("Which fragmentomics workflow detects tumour-derived plasma DNA under realistic low tumour fractions and fixed false-positive constraints?"). Before this pass it had one judgement: DELFI sensitivity 73% (152/208) at a reported 98% specificity, internal cross-validation, no comparator and no tumour-fraction stratum.

Goal: comparisons of several fragmentomics methods or feature sets on the same plasma cohort or dilution series, with printed per-method values, ideally stratified by tumour fraction or coverage.

Bounds: cutoff 2026-10-09; budget 25 queries, 8 used; at most 3 sources, 2 extracted. Lane `genomics`. Worker: Claude (Opus 5.5) research agent; no human review claimed.

This file is the pass's research dossier. The CNV example keeps its search log in `research.md` and its dated document in `docs/reviews/use-cases/` is the independent review, so no separate collector dossier was written there.

## Queries

The full entries are `search-use-case-ctdna-fragmentomics-genomics-q1` to `q8` in `data/omics/search-ledger.jsonl`. Times for web searches (q1, q3, q5, q7) are approximate.

| # | Query (short form) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | cfDNA fragmentomic feature benchmark, DELFI, end motif, nucleosome, same cohort | web search | GigaScience 2025 preprocessing study; an eLife reviewed preprint 95320 |
| 2 | eLife 95320 lookup | Europe PMC | No match; GigaScience study has no per-method values |
| 3 | eLife reviewed preprint 95320 | web search | No usable result |
| 4 | fragmentomics benchmark or systematic comparison with ichorCNA, DELFI, Griffin, LIQUORICE or end motif | Europe PMC | Hou et al. 2024 and Wang et al. 2026 (UNITE) taken forward |
| 5 | tumour-fraction estimation benchmark, dilution series, ichorCNA, WisecondorX, ACE | web search | Nothing peer-reviewed with printed values |
| 6 | ichorCNA tumour fraction with fragmentomic features and dilution or in silico mixing | Europe PMC | Curtis et al. 2025 PNAS (false positives in non-cancer disease) screened; per-sample data only |
| 7 | Griffin, LIQUORICE, ichorCNA independent comparison | web search | Nothing usable |
| 8 | multi-feature fragmentomics with base models and sensitivity at fixed specificity | Europe PMC | Three developer multi-feature assays kept as leads |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Hou et al. 2024, Advanced Science, article Table 1 | Extract all 25 value cells | Independent re-implementation of ten published fragmentation patterns and DELFI, one SVM each, on the DELFI 2019 cohort. All ten patterns are cited to earlier publications. |
| Hou et al. 2024, Supporting Information Tables S2 and S3 | Extract all 360 value cells | The only printed sensitivity at fixed specificity for several fragmentomic feature definitions on the same samples, with three independent cohorts. |
| Wang et al. 2026, Science Advances (UNITE), Data file S2 sheets STATS_xgb_x1-x6 and STATS_lr | Extract all 208 rows | The only printed tumour-fraction-stratified comparison found: five fragmentomic feature sets, their combination and an ichorCNA tumour-fraction classifier within ichorCNA strata. Author-reported. |
| UNITE sheet STATS_xgb_all_feat | Not extracted | 1,024 rows (16 feature combinations). It holds fixed-specificity sensitivity for the fragmentomic models, so it is the most useful omission; left for a follow-up pass to keep the batch bounded. |
| Curtis et al. 2025, PNAS | Excluded | Directly relevant to false-positive constraints (autoimmune and vascular disease), but only per-sample data and figures are published. |
| LIONHEART (Nat Commun 2025), FinaleToolkit (Bioinform Adv 2025), GigaScience 2025, Genome Biology 2025 framework, four-assay breast study | Excluded | No printed per-method detection comparison, or no false-positive constraint. |

## Record design

- Hou et al. Table 1: one protocol (pan-cancer vs healthy, 10 x 10-fold CV) on the stored DELFI dataset, 25 configurations (pattern by feature setting), one evaluation and one AUC result each. Cites only the article, which has no concern.
- Hou et al. Tables S2-S3: five protocols (Cristiano CV with eight case groups as qualifiers; Jiang liver CV; three independent cohorts). The ten open-chromatin configurations are shared with Table 1. Origin `independent_paper` throughout.
- UNITE: four protocols, one per ichorCNA stratum ([0, 0.03], (0.03, 0.1], (0.1, 1], all), seven evaluations each (six XGBoost feature sets, origin `author_reported`; the ichorCNA-TF logistic regression, origin `independent_paper` because ichorCNA is not the authors' tool). Means are values, the 95% CIs are uncertainty, and median, sd and sem are kept in `source_cells`.
- Ten relevance judgements, all `proxy`, in three comparison groups (see `coverage.json`).
- Three metric concepts were added to `data/vocab/metric.ttl`: sensitivity at 85%, 95% and 99% specificity, copying the existing 98% concept.

## Things a reviewer should judge

1. **Hou et al. Table S2 against Table S9.** For every PANCAN pattern, S9's SVM sensitivity at 95% equals S2's sensitivity at 85% (length: S9 D3 0.6033 = S2 E3; S2 D3 prints 0.5210). One of the tables has its sensitivity columns shifted. Recorded as an evidence concern on the supplement source, which withholds the five Tables S2-S3 judgements until resolved. The AUC columns match article Table 1 exactly.
2. **Hou et al. Table S2 LIHC.** Nine of ten rows print identical sensitivity at 95% and 85% specificity, CI included. Possible but implausible; `source_anomaly` is set on those 18 results.
3. **Hou et al. Table S9 WPS logistic regression** repeats the OCF logistic-regression row. Part of the concern; S9 is not extracted.
4. **Hou et al. LIHC controls.** The table does not say whether the Jiang-cohort model used healthy controls only or all 135 non-cancer samples.
5. **UNITE ichorCNA-TF, (0.1, 1] stratum.** AUROC, sensitivity and specificity are all 1, but sensitivity at 95%, 98% and 99% specificity print 0 and the fixed-specificity accuracies are constants. The fixed-specificity values look undefined; `source_anomaly` is set on those nine results.
6. **UNITE origin.** The six feature-set models are the authors' framework (`author_reported`). The ichorCNA-TF comparator was built by the authors from ichorCNA output; recorded as `independent_paper` with a limitation note. A reviewer may prefer `author_reported` for it.
7. **UNITE text check.** Results P13 quotes AUCs 0.878, 0.873, 0.857, 0.736, 0.715 and 0.651 for the [0, 0.03] stratum; these match sheet STATS_xgb_x1-x6 column D. P18 quotes ichorCNA-TF 0.603 ([0, 0.03]) and 0.983 ((0.03, 0.1]); these match STATS_lr. The text says the raw data are in "data file S1"; they are in Data file S2.
8. **Overlap.** The UNITE pooled set includes the Cristiano et al. 2019 cohort, so UNITE, Hou et al. and the existing DELFI judgement share samples.
9. **Possible author overlap for IFS.** IFS and the Zhou et al. liver cohort come from CRAG (Zhou X et al., Genome Med 2022). Hou et al.'s senior author is Xionghui Zhou; whether this is the same person was not checked. If so, the IFS evaluations and the Zhou-cohort validation are closer to `author_reported` than the recorded `independent_paper`.
10. **DELFI records.** Hou's DELFI re-implementation is a new configuration of a new DELFI method record. The stored DELFI configuration has no `configuration_of` link and was not changed.

## Coverage

Bounded pass against the sources above; not systematic. Not covered: CCGA multi-feature comparisons (Jamshidi et al. 2022); Griffin, LIQUORICE, FinaleToolkit and DELFI developer papers; developer multi-feature assays with base-model tables; held-out and unseen-test results of UNITE (prose and figures only); the UNITE all-feature sheet; any prospective screening study.
