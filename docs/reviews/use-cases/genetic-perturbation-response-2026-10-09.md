# Genetic perturbation response: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-perturbation-response-20261009/` (447 records). Use case: `use-case-genetic-perturbation-response`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced.

## Verdict

- Both pinned artifacts re-download to their recorded SHA-256, and both archived copies decompress to the same bytes.
- All 352 results match their cells in Supplementary Table 2. No value, metric, qualifier, unit, direction, configuration, protocol, dataset or origin was wrong.
- The origin split is right on every row.
- All 4 judgements hold as `proxy`. Their limitations now name:
  - the author affiliation, and that the authors configured the foundation-model runs;
  - the single split and the absent spread;
  - for Norman, the combination share.
- Each judgement is `source_checked` with `reviewed_evaluations` (15 each, none excluded). Pins are left for the integrator.
- Every other record is `source_checked`.
- The summary proposal says "independent benchmark", which misleads. My corrected text is at the end.

Do not rerun `extract/extract_perturbation.py` on this folder; it would overwrite these changes.

## How the check was done

1. Downloaded the article XML and the supplementary bundle into an empty directory, unpacked the bundle, and hashed `12864_2025_11600_MOESM4_ESM.xlsx`.
2. Read Supplementary Table 2 with a stdlib OOXML reader written for this review; the extractor's script was not run. For each result I compared:
   - the cell's shortest round-trip decimal with `printed_value` and `numeric_value`;
   - the metric and qualifier implied by the column;
   - unit and direction;
   - the evaluation's configuration, protocol, dataset and origin, which must match the row's dataset and model.
3. 352 expected cells, 352 matched, none missing and none duplicated. The 8 cells not stored are the Wilcoxon column for scGPT and scFoundation in each dataset, which are blank in the workbook.
4. Checked the 24 Pearson Delta values quoted in Results paragraphs 6 and 7 against the table: all match to three decimals.
5. Read Supplementary Table 1 and the article's Methods, Results and declarations.
6. Dry run: `addBatch` into a scratch copy of the store, then `deriveUseCaseInputs` with the 4 proposed links added in memory.

## Sources and hashes

| Source ID | Artifact | SHA-256 (re-downloaded 2026-10-09T21:10Z) | Matches |
| --- | --- | --- | --- |
| `perturbation-response-20261009-source-csendes2025` | PMC12016270 full-text XML | `b59088e4169385c602d0b7a51253d7c1131688666e64e95c06fb54950a514c19` | Yes |
| `perturbation-response-20261009-source-csendes2025-supp` | `12864_2025_11600_MOESM4_ESM.xlsx` from the Europe PMC bundle | `b5bfcb633921a642de077a39fcb015c6d36bc36a52d9c5e9ceca33be483d3261` | Yes |

## Values checked

| Source table | Results | Mismatches |
| --- | --- | --- |
| Supplementary Table 2: 4 datasets, 15 models, 6 Pearson columns, minus 8 blank Wilcoxon cells | 352 | 0 |

The table header prints "Pearson Delta " with a trailing space; locators omit it. That is a harmless normalisation.

## The lead's points

| Point | Finding |
| --- | --- |
| Origin | Right on every row. The Competing interests statement says "All authors are full-time employees of Turbine Ltd., KSz is a founder as well". The authors built Train Mean and the twelve RF, EN and kNN regressors (52 evaluations), so `author_reported` is right. That includes the regressors on scGPT and scFoundation embeddings: the authors built those models, and the embeddings are only features. The 8 scGPT and scFoundation evaluations are re-runs by authors who did not develop those models, so `independent_paper` is right. Whatever the origin value, the authors configured and ran the foundation-model fine-tuning and argue that the baselines win; this is now a limitation on every judgement. |
| scGPT and scFoundation links and versions | `configuration_of` `catalog-model-scgpt` and `catalog-model-scfoundation` (both family records) is right. The versions match Methods 'Foundation models'. scGPT is "a fork of scGPT v0.2.1 (commit 7301b51)", fine-tuned 15 epochs with default hyperparameters. scFoundation is the repository at "commit 69b0710", fine-tuned 10 epochs with effective batch size 32, against defaults of 15 and 30. The fork is not named, so the commit may not resolve upstream, and neither pretrained checkpoint is identified beyond "the pretrained models from the original publications". Both are now `model_identity_note` entries on the configurations. The regressors' scikit-learn 1.5.2 and tuned hyperparameters match Methods 'Baseline models'. |
| Split | Methods 'Benchmark datasets': all four datasets were processed with cell-gears v0.0.1 and "split into train, validation and test sets according to the GEARS publication, corresponding to Perturbation Exclusive split". Each dataset is one cell line, so the cross-cell-type exclusion is respected. There is one split per dataset and one fine-tuning run per foundation model; no seeds or spread are printed. |
| Replogle and Norman against the GEARS combination exclusion | Adamson, Replogle K562 and Replogle RPE1 are single-gene CRISPRi, so the exclusion is not engaged. Norman is not single-gene: Supplementary Table 1 gives 116 test perturbations, of which 79 are two-gene combinations and 37 are unseen single genes. The combinations break down as 9 with neither gene in training, 52 with one and 18 with both. The 138 training perturbations are not broken down. So the source does not show whether training included combination examples, which the use case's `inputs` require ("combinations require combination examples during GEARS training"). scFoundation runs through GEARS, so the exclusion applies to it directly. The Norman judgement now says all of this, and that every Norman value pools combinations and singles. The per-subgroup values in Supplementary Table 3 are not extracted because their metric is unlabelled. The regressors represent a combination as the sum of the two genes' embeddings. |
| Citation slip | Confirmed, and there are three, not one. Results paragraph 7 cites Supplementary Table 1 for the random-forest-on-embedding values, and paragraph 8 twice cites it for the Pearson Delta DE results; all are in Supplementary Table 2. Recorded as a limitation; no value depends on it. |

The two descriptive claims match the source: the Norman subgroups match Supplementary Table 1 rows 7 to 9, and the target-gene claim matches Results paragraph 8.

## Corrections made in the batch

None changes a value.

1. `...config-csendes2025-scgpt` and `...config-csendes2025-scfoundation`: `model_identity_note` added.
2. All four judgements: two short limitations replaced with fuller ones on the affiliation, the configuration and the split. Added the blank Wilcoxon cells and the citation slips. Norman gets the combination, training make-up and summed-embedding limitations; the other three get a single-gene scope note. `reason` cites this review.

## Judgements

| Judgement | Relevance | Reviewed evaluations | Stratum |
| --- | --- | --- | --- |
| csendes2025-adamson | proxy | 15 | 1, Adamson (K562 CRISPRi) |
| csendes2025-norman | proxy | 15 | 2, Norman (K562 CRISPRa, singles and pairs) |
| csendes2025-replogle-k562 | proxy | 15 | 3, Replogle K562 (CRISPRi) |
| csendes2025-replogle-rpe1 | proxy | 15 | 4, Replogle RPE1 (CRISPRi) |

Proxy is right for the same reason as the three existing judgements: expression prediction scores do not establish mechanism or experimental prioritisation, which is one of the use case's exclusions. The grouping (`csendes2025-perturbseq`, headline `pearson-delta`) matches the authors' own headline metric. The raw Pearson columns are stored but, as the authors note, are not informative (all above 0.95).

Dry run with the 4 links: the 4 new judgements are withheld only because pins are not yet recorded. The 3 existing judgements stay active.

## Approved use-case changes

Links and gaps only. No pinned field changes, so the three existing judgements are unaffected: `use-case-map-gears-norman-table6-mse`, `use-case-map-gears-norman-table6-pearson-de` and `use-case-map-perteval-scfm-norman-single-auspc`. In the dry run they stay active with the links added; use-case links are not pinned.

Add these `assessed_by` links to `use-case-genetic-perturbation-response`:

- `perturbation-response-20261009-protocol-csendes2025-adamson-pex`
- `perturbation-response-20261009-protocol-csendes2025-norman-pex`
- `perturbation-response-20261009-protocol-csendes2025-replogle-k562-pex`
- `perturbation-response-20261009-protocol-csendes2025-replogle-rpe1-pex`

Add these `evidence_gaps`, exact text:

1. Ahlmann-Eltze et al. 2025 (Nature Methods), the main independent comparison of foundation and deep models against additive, mean and linear baselines, reports per-method results only in figures; its Source Data are per-perturbation rows. Not extracted.
2. Control-aware metrics (Systema, Nature Biotechnology 2025) are reported only in figures; no printed per-method values were found in this pass.
3. The one extracted multi-method comparison (Csendes et al. 2025) uses one GEARS perturbation-exclusive split per dataset with no spread; its authors, all employees of one company, built the baselines and re-ran the foundation models.
4. For Norman, Csendes et al. 2025 does not print how many training perturbations are combinations, so its combination results cannot be checked against the requirement for combination examples in GEARS training.
5. PerturBench combination-prediction results are in the store as task records and need a protocol before they can be judged for this use case.

Gaps 1, 2 and 5 rest on the collector's screening, which I did not repeat. Gaps 3 and 4 replace the collector's third gap.

## Final summary text

> In Csendes et al. 2025, whose authors are all employees of Turbine Ltd. and built the baselines themselves, a Train Mean control that predicts the mean training response for every unseen perturbation scored a higher Pearson correlation of expression change (Pearson Delta) than scGPT and scFoundation, as re-run by the same authors, on all four Perturb-seq datasets: 0.711, 0.557, 0.373 and 0.628 for Adamson, Norman, Replogle K562 and Replogle RPE1, against 0.641, 0.554, 0.327 and 0.596 for scGPT and 0.552, 0.459, 0.269 and 0.471 for scFoundation. A random forest on Gene Ontology features of the perturbed gene scored 0.739, 0.586, 0.480 and 0.648. Each dataset was scored on a single GEARS perturbation-exclusive split within one cell line, with one run per model and no spread printed, so small gaps such as 0.557 against 0.554 on Norman cannot be tested. On Norman, 79 of the 116 test perturbations are two-gene combinations and the scores pool them with single genes. The authors note that these datasets have little perturbation-specific variance, so they separate models poorly. The GEARS Norman comparison and PertEval-scFM on this page are separate protocols and are not pooled with these values. Expression scores do not show which experiments will succeed.

Number trace:
- **Train Mean:** the `mean` Pearson Delta results E14, E29, E44 and E59 (0.711148, 0.557266, 0.372996, 0.628385).
- **scGPT:** E15, E30, E45 and E60 (0.641038, 0.553838, 0.326502, 0.596358).
- **scFoundation:** E16, E31, E46 and E61 (0.552166, 0.458965, 0.269329, 0.470948).
- **RF_go:** E2, E17, E32 and E47 (0.738712, 0.586124, 0.48, 0.64772).
- **Norman test set:** 79 combinations and 116 test perturbations are from Supplementary Table 1 (D3 and B9 to E9), recorded in the dataset record and the subgroup claim.
- **Variance:** "little perturbation-specific variance" is from Results 'Limited perturbation diversity biases benchmarking outcomes'.

Three decimals are used so the Norman gap (0.003) is not hidden by rounding.

## Remaining gaps

- Supplementary Table 3 (Norman subgroups) and the figures were not checked.
- Screened sources in `research.md` were not re-read.
- Pins are not recorded; the integrator pins with this review.
