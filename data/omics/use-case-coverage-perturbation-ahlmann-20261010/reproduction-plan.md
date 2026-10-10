# Reproduction plan: Ahlmann-Eltze et al. 2025, Nature Methods

Source: Ahlmann-Eltze C, Huber W, Anders S. Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines. Nature Methods (2025). doi:10.1038/s41592-025-02772-6, PMC12328236, CC BY 4.0.

Status: not extracted, and not approved for reproduction. The paper prints no per-method metric value in the main text, Methods, figure and Extended Data legends, Reporting Summary or Peer Review file. Per-method results appear only in figures. The values below would be computed by Rewire from per-perturbation Source Data rows, so they would not meet the record contract that `printed_value` is exactly as printed. Run this plan only if the owner approves a reproduction, and label the results as Rewire-computed.

Checked 2026-10-10 by a Claude (Opus 5.5) research agent. No human review is claimed. All counts below are row counts. No metric aggregate has been computed.

## Files

Retrieved 2026-10-10 from `https://static-content.springer.com/esm/art%3A10.1038%2Fs41592-025-02772-6/MediaObjects/41592_2025_2772_MOESM<n>_ESM.xlsx`.

| File | Supports | sha256 |
| --- | --- | --- |
| MOESM3 | Fig. 1 | `c9bd4d688b8ca8a3d3846593da3bab80cc2e65dbdbdc251a96b2bdcd05b75081` |
| MOESM4 | Fig. 2 | `2ccfa7239c195f329e1632b51510adebfd493e0a5a7427a0f012e078e0e59c35` |
| MOESM6 | Extended Data Fig. 2 | `1f05ffc452445de659d9b0bb4b05c673892ce7a4f2657ea3098a7904f95f24b3` |
| MOESM10 | Extended Data Fig. 8 | `040dae4985b4461817b96eb807390c8fe3f2c115523f4dfcb7692485aa0734e3` |

Article XML (Europe PMC `fullTextXML`, 141,399 bytes): `dc5ccf62cb51d301f327a3c3e629d60be719bb2aaf02b57fb4999be43a4d95c7`.

## What the Source Data holds

Each row is one perturbation in one test-training split (column `seed`). The columns are `l2` (L2 distance over the 1,000 most highly expressed genes), `r2`, `r2_delta` (Pearson delta) and `method`.

- MOESM3 Panel A (Fig. 1a): 2,790 rows for the Norman double perturbations (scFoundation reprocessing). There are 9 methods with 310 rows each (62 perturbations by 5 splits). Within each split the sheet labels 31 held-out doubles `test` and 31 `val`.
- MOESM6 Panel A (Extended Data Fig. 2a): identical to MOESM3 Panel A, compared by row hash.
- MOESM4 Panel A (Fig. 2a): 5,061 rows for the unseen single perturbations. It has 7 methods (`gears`, `scgpt`, `geneformer`, `uce`, `scbert`, `mean`, `lpm_selftrained`). Each method has 48 Adamson rows, 262 Replogle K562 rows and 413 Replogle RPE1 rows, across 2 splits, labelled `test` or `val`.
- MOESM10 Panel A (Extended Data Fig. 8a): identical to MOESM4 Panel A.
- MOESM4 Panel C (Fig. 2c): 22,144 rows. It has 16 methods, including `cpa`, `uce33` and the linear-model embedding variants. 14,816 rows are labelled `train`. Each method has 20, 214 and 224 `test` or `val` rows (Adamson, K562, RPE1), and 6 rows with null `r2_delta`.
- MOESM6 Panel B and MOESM10 Panel B (Extended Data Fig. 2b and 8b): the authors' own `dist_mean` and `dist_se` for each method at each n. These are not usable as they stand:
  - The n grid steps from 991 to 1001, so there is no n = 1000 row.
  - `dist_mean` is not defined.
  - MOESM10 Panel B has no `sorted_by` column, although the legend describes two orderings.
- The other workbooks (MOESM5, 7, 8, 9, 11 and 12) hold dataset overviews, per-gene interaction rows, recurrence counts and compute use, not per-method metrics. Extended Data Fig. 4 (AUC with standard error) and Extended Data Fig. 7 have no Source Data.

## Stated aggregation

- Fig. 1a, Fig. 2a, Extended Data Fig. 2a and Extended Data Fig. 8a: "The horizontal red lines show the mean per model". Take the arithmetic mean over all held-out perturbations and splits, per model, and per dataset for Fig. 2. Pool the `test` and `val` rows to match the legend's 62 doubles per split. The paper gives no median.
- Fig. 2c: "overall mean and 95% confidence interval of the bootstrapped mean ratio between each model and the baseline". The paper gives no resample count or seed, and does not say whether the ratio is a ratio of means or a mean of per-perturbation ratios. Fig. 2c cannot be reproduced exactly, so leave it out.

## Rows needed

| Target | Sheet | Rows | Values |
| --- | --- | --- | --- |
| Fig. 1a mean L2 per model | MOESM3 Panel A | 2,790 | 9 |
| Extended Data Fig. 2a mean Pearson delta per model | same rows | (2,790) | 8; `no_change` is null in all 310 rows, as the legend notes |
| Fig. 2a mean L2 per model and dataset | MOESM4 Panel A | 5,061 | 21 |
| Extended Data Fig. 8a mean Pearson delta per model and dataset | same rows | (5,061) | 21 |
| Total | | 7,851 distinct rows | 59 |

## Inconsistencies to record as evidence concerns

- The Fig. 2 legend gives "134, 210 and 24 unseen single perturbations across two test–training splits". In MOESM4 Panel A, 134 and 210 are the split 1 counts only; split 2 has 128 and 203. The two-split totals are 262, 413 and 48.
- Methods (Single perturbation benchmark setup, paragraph 4) restricts the analysis to perturbations predicted by all models: 73 Adamson, 398 Replogle K562 and 629 Replogle RPE1. No sheet matches these counts.
- The `test` and `val` rows in MOESM4 Panel C (20, 214 and 224 per method) match neither the Fig. 2 legend nor Methods.
- Main text paragraph 16 says CPA was not included in the single-perturbation benchmark, but `cpa` appears in MOESM4 Panel C.

## Records to reuse

- Models: `catalog-model-gears`, `catalog-model-scgpt` and `catalog-model-scfoundation`. scFoundation is in the double-perturbation benchmark only (main text paragraph 16).
- Datasets:
  - Adamson and Replogle K562 and RPE1 are the GEARS-distributed files. Before reusing the Csendes 2025 dataset records, confirm the files are the same.
  - Norman is the scFoundation reprocessing, with 19,264 genes in main text paragraph 3 and 19,624 in the Extended Data Fig. 10 legend. It differs from the Csendes Norman record and needs its own dataset record.
