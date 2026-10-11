# Ahlmann-Eltze et al. 2025: values computed from Source Data

Use case: `use-case-genetic-perturbation-response`. Follows `data/omics/use-case-coverage-perturbation-ahlmann-20261010/reproduction-plan.md`, after the owner decided that values computed from a source's own supplementary data are evidence (record contract, `derivation`). No new literature search was run.

Extraction by a Claude (Opus 5.5) agent on 2026-10-11. All records are `needs_review`. No review by the extractor, and no human review, is claimed.

## What was extracted

The paper prints no per-model value. Fig. 1a, Fig. 2a, Extended Data Fig. 2a and Extended Data Fig. 8a plot one point per held-out perturbation and a red line at "the mean per model". Their Source Data hold the plotted rows. Rewire computed each mean with `scripts/omics/derive/ahlmann_eltze_2025.py`:

| Figure | Workbook, sheet | Metric | Rows | Values |
| --- | --- | --- | --- | --- |
| Fig. 1a | MOESM3, Panel A | L2 distance | 2,790 | 9 |
| Extended Data Fig. 2a | MOESM6, Panel A (same rows as MOESM3) | Pearson delta | 2,790 | 8 |
| Fig. 2a | MOESM4, Panel A | L2 distance | 5,061 | 21 |
| Extended Data Fig. 8a | MOESM10, Panel A (same rows as MOESM4) | Pearson delta | 5,061 | 21 |

Both metrics are over the 1,000 most highly expressed genes in control (Fig. 1 and 2 legends; the Extended Data Fig. 2 and 8 legends say n = 1000 is "the choice in Panel a").

Decisions:

- Aggregation: arithmetic mean per model, and per dataset for Fig. 2, over all held-out rows. The sheets label held-out perturbations `test` or `val`. Both are held out from training, and the Fig. 1 legend's "62 double perturbations" per split equals 31 test plus 31 val, so both are pooled. All splits are pooled, as the legends describe the points "across five" or "two test-training splits".
- Precision: exact mean of the stored cell strings, rounded half to even to 3 decimal places. The paper gives no precision.
- Fig. 2a uses both splits as in the sheet, although the legend's counts are split 1 only. This is recorded as an evidence concern, which also keeps these results out of automatic comparisons.
- Evaluation origin: `author_reported` for the no change, additive, mean and linear-model baselines the authors built or adopted; `independent_paper` for GEARS, scGPT, scFoundation, CPA, Geneformer, UCE and scBERT, which the authors ran but did not develop. This follows the Csendes et al. 2025 batch.
- Metric: a new concept `l2-distance` in `data/vocab/metric.ttl`. The Methods call the L2 distance "also called root mean squared error", but the formula has no mean, so `root-mean-squared-error` would be wrong. rb-only; no external term was checked to match exactly.
- Unit: L2 distance is `unit-unreported` with a `unit_detail` (log-transformed expression; the paper does not name the unit). Pearson delta is `unitless`.
- Datasets: new records. The Norman data are the scFoundation reprocessing, not the GEARS processing used for the Csendes Norman record. Adamson and Replogle are the GEARS Dataverse files named in Data availability; the Csendes records describe cell-gears v0.0.1 processing with a different split, so they were not reused.
- Reused records: `catalog-model-gears`, `catalog-model-scgpt`, `catalog-model-scfoundation`, `catalog-model-geneformer`, `cell-type-20261009-model-uce` and `perturbation-response-20261009-method-train-mean`. New: scBERT and CPA models, and no change, additive and linear-model methods.
- One configuration per model, used on every dataset it was run on, as in the Csendes batch.
- `budget` in the evaluation comparison is null: Methods limit fine-tuning to 3 days, but that does not describe the baselines. This blocks automatic comparison, as intended for an unstated field.

## Not extracted (gaps)

- Fig. 2c (forest plot of bootstrapped mean ratios against the mean baseline, including the linear models with pretrained embeddings): no resample count or seed, and the ratio could be a ratio of means or a mean of per-perturbation ratios. Ambiguous aggregation, so not computed. The main-text conclusion about it is recorded as a claim.
- Extended Data Fig. 2a, `no_change`: all 310 Pearson delta cells are empty; the legend says the correlation could not be calculated because the predictions were all zero. No value recorded.
- Fig. 1c and Extended Data Fig. 4 (genetic-interaction detection): Fig. 1c is a curve with no stated summary. Extended Data Fig. 4 has no Source Data, but its legend says the figure prints each model's AUC with the standard error across the five splits as labels. Those are printed numbers that a later pass could transcribe from the rendered figure; they were outside this batch's scope. The main-text conclusion is recorded as a claim.
- Extended Data Fig. 2b and 8b (error against n): the sheets have `dist_mean` and `dist_se` per n, but the n grid skips 1000, `dist_mean` is not defined, and MOESM10 Panel B lacks the `sorted_by` column the legend describes.
- Extended Data Fig. 10 (compute): not a performance metric for this use case.

## Evidence concerns recorded

On `perturbation-ahlmann-20261011-source-data-fig2` (four) and `perturbation-ahlmann-20261011-source-data-ed-fig8` (one):

1. The Fig. 2 legend counts (134, 210 and 24) are the split 1 counts; the two-split totals are 262, 413 and 48.
2. Methods restrict the single-perturbation analysis to 73, 398 and 629 perturbations predicted by all models; no sheet has these counts.
3. The Panel C test and val counts (20, 214 and 224 per method) match neither the legend nor Methods.
4. The main text says CPA was not in the single-perturbation benchmark, but Panel C has `cpa` rows.

Not a source concern but noted on the Norman dataset: the gene count is 19,264 in main text paragraph 3 and 19,624 in the Extended Data Fig. 10 legend.

## Needs a reviewer's judgement

- Whether Fig. 2a's plotted mean uses both splits (as the Source Data sheet) or only split 1 (as the legend counts). The recorded values use both.
- Whether pooling `test` and `val` rows is right for Fig. 2a, as it is for Fig. 1a by the legend's count. For Fig. 2 the legend's split 1 counts also equal test plus val.
- The relevance of each protocol (`proxy`, as for the Csendes protocols).
- Whether to archive the four workbooks in the batch folder.
