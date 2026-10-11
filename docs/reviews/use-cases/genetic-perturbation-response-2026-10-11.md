# Genetic perturbation response: independent review of the Ahlmann-Eltze et al. 2025 derived batch

Batch: `data/omics/perturbation-ahlmann-derived-20261011/` (131 records), draft PR #105. Use case: `use-case-genetic-perturbation-response`. Plan: `data/omics/use-case-coverage-perturbation-ahlmann-20261010/reproduction-plan.md`.

Reviewer: a separate Claude (Opus 5.5) review agent that did not extract the batch. No human review is claimed. No model was run; the 59 values are means recomputed from the authors' Source Data, not reproductions.

## Verdict

Pass, with five small fixes and one addition to an evidence concern, listed below. All 131 records are now `source_checked`.

- All five artifacts re-download to their recorded SHA-256.
- The script's SHA-256 matches every derivation. Rerun on the fresh downloads, its output is byte-identical to `derived-values.jsonl`.
- A separate reader (openpyxl, written for this review) gives the same 59 values and the same row counts. No mean lies within 0.001 of a rounding tie, so the half-to-even rule changes nothing.
- The aggregation is the legends' own wording and the script applies it and nothing else: an arithmetic mean per model, and per dataset for Fig. 2, over every row of sheet "Panel A".
- Fig. 2c was not computed. No value comes from figure pixels.
- The four inconsistencies in the plan are recorded as evidence concerns with hashes and locators.
- The origin split is right, and the four judgements hold as `proxy`.
- The three single-perturbation judgements will be withheld after intake, because their Source Data sources carry evidence concerns. Only the Norman judgement can become active. The review supports this: the split choice changes which model ranks first.

Do not rerun `extract/build_batch.py` on this folder; it would overwrite the review.

## How the check was done

1. Downloaded the four workbooks and the article XML with `curl` into an empty scratch directory. No email or credentials were sent. Hashed each file.
2. Copied the workbooks to the names the script expects and ran `python3 -I scripts/omics/derive/ahlmann_eltze_2025.py <dir> <out>`. The script's assertions passed: row counts, inline strings only, and the Extended Data sheets repeat the main-figure sheets row for row. The output matched `derived-values.jsonl` exactly.
3. Read sheet "Panel A" of each workbook with openpyxl and recomputed every mean in floating point, rounded to 3 places. I also counted rows per split and per `train` label, and checked that every method has the same perturbations in each split.
4. Cross-checked all 59 results in `batch.jsonl`: `printed_value` and `numeric_value`, metric, qualifier, unit, direction, the evaluation link, the input source and hash, `row_filter`, `row_count`, coverage, the aggregation quote and locator, and the script hash.
5. Parsed the article XML: main text (paragraphs numbered as in `retrieval-log.md`), Methods sections, figure and Extended Data legends, Data availability and the supplementary file captions.
6. Read every entity, evaluation and claim record against the article.
7. Trial `npm run records -- add` of the reviewed batch: derivation checks and SHACL shapes passed (131 records added). The store was then restored with `git checkout`.

## Sources and hashes

Re-downloaded 2026-10-11.

| Source ID | Artifact | SHA-256 | Matches |
| --- | --- | --- | --- |
| `perturbation-ahlmann-20261011-source-article` | PMC12328236 full-text XML, 141,399 bytes | `dc5ccf62cb51d301f327a3c3e629d60be719bb2aaf02b57fb4999be43a4d95c7` | Yes |
| `perturbation-ahlmann-20261011-source-data-fig1` | MOESM3, 1,659,842 bytes | `c9bd4d688b8ca8a3d3846593da3bab80cc2e65dbdbdc251a96b2bdcd05b75081` | Yes |
| `perturbation-ahlmann-20261011-source-data-fig2` | MOESM4, 1,837,063 bytes | `2ccfa7239c195f329e1632b51510adebfd493e0a5a7427a0f012e078e0e59c35` | Yes |
| `perturbation-ahlmann-20261011-source-data-ed-fig2` | MOESM6, 529,066 bytes | `1f05ffc452445de659d9b0bb4b05c673892ce7a4f2657ea3098a7904f95f24b3` | Yes |
| `perturbation-ahlmann-20261011-source-data-ed-fig8` | MOESM10, 586,193 bytes | `040dae4985b4461817b96eb807390c8fe3f2c115523f4dfcb7692485aa0734e3` | Yes |

Script `scripts/omics/derive/ahlmann_eltze_2025.py`: `452a7a7aaab7e4965142de87ed9f00209a6d9664760919cb39b921bb45aec45c`, equal to `script_sha256` on all 59 results.

The inputs are the source's own data. The article's supplementary captions call each file "The raw data used to make the plots in Fig. N". The files are served from the publisher's ESM path for this DOI, and every source record carries the article's DOI.

## Aggregation and filters

- Fig. 1a legend: "Beeswarm plot of the prediction errors for 62 double perturbations across five test-training splits ... The horizontal red lines show the mean per model". The Extended Data Fig. 2a and 8a legends and the Fig. 2a legend use the same sentence. Each `aggregation_locator` names the right legend and panel.
- Rows: in MOESM3 Panel A every method has 62 rows per split (31 `test`, 31 `val`) over seeds 1 to 5, 310 in all. Within a split, all methods have the same perturbations. Pooling `test` and `val` is required to reach the legend's 62, so the pooling is right.
- In MOESM4 Panel A every method has 24 and 24 Adamson rows, 134 and 128 Replogle K562 rows, and 210 and 203 Replogle RPE1 rows for splits 1 and 2. All methods have the same perturbations within each split.
- Fig. 2a pooling both splits: I agree with the batch. The Fig. 1 legend gives a per-split count ("62 double perturbations across five ... splits"), and the Fig. 2 legend uses the same form ("134, 210 and 24 unseen single perturbations across two ... splits"). That reads as split 1's count, not a statement that only split 1 is plotted. The sheet is captioned as the plotted data, and it has both splits.
- Using split 1 only is material, so the concern stays. It would move the per-model means by up to 0.61 (L2) and 0.06 (Pearson delta), and would change the model with the lowest mean L2 on Adamson and Replogle RPE1. I added this to the first concern on `perturbation-ahlmann-20261011-source-data-fig2`.
- Pooled mean or mean of split means: these are equal for Norman, where split sizes are equal. For Fig. 2 they differ by at most 0.011 (L2) and 0.001 (Pearson delta). "Mean per model" over the plotted points reads as the pooled mean, which the script computes.
- Extended Data Fig. 2a `no_change`: all 310 `r2_delta` cells are empty, as the legend states. No result is recorded.

## Not computed, as required

- Fig. 2c: no result uses MOESM4 Panel C. The bootstrapped mean ratio has no resample count, and the article does not say whether it is a ratio of means or a mean of ratios. Recorded as a gap in `coverage.json` and `research.md`.
- No value is read from a figure image. Extended Data Fig. 4's printed AUC labels and Extended Data Fig. 2b and 8b are recorded as gaps.

## Evidence concerns

| Source | Concern | Checked |
| --- | --- | --- |
| Source Data Fig. 2 | The legend's counts 134, 210 and 24 are the split 1 counts; two-split totals are 262, 413 and 48 | Counts confirmed. Reviewer addition: the split choice changes the means and the top model |
| Source Data Fig. 2 | Methods counts of perturbations predicted by all models (73, 398, 629) match no sheet | Confirmed against Single perturbation benchmark setup paragraph 4; Panel A has 48, 262, 413 and Panel C has 20, 214, 224 |
| Source Data Fig. 2 | Panel C `test` and `val` rows (20, 214, 224 per method) match neither legend nor Methods | Confirmed |
| Source Data Fig. 2 | Main text paragraph 16 excludes CPA, but Panel C has `cpa` rows | Confirmed: 1,384 `cpa` rows, 458 of them `test` or `val` |
| Source Data Extended Data Fig. 8 | Panel A repeats Fig. 2 Panel A, and the Methods counts match neither | Confirmed (row-for-row equality asserted by the script and checked separately) |

Each entry has `source_id`, message, locator, the artifact SHA-256 of its own source, and a review date. The Norman gene-count discrepancy (19,264 in main text paragraph 3, 19,624 in the Extended Data Fig. 10 legend) is recorded on the dataset record, not as a source concern. That is appropriate: it does not affect the scored rows.

## Records

- Origin. Evaluations of the authors' own or adopted baselines (no change, additive, mean, linear model) are `author_reported`. Evaluations of GEARS, scGPT, scFoundation, CPA, Geneformer, UCE and scBERT are `independent_paper`. That follows the origin vocabulary ("authors independent of the evaluated method") and the Csendes et al. 2025 precedent. `derivations.ts` accepts both. No evaluation is `rewire_run` or `paper_compilation`. The derivation, not the origin, marks the values as computed by Rewire.
- Metrics. `l2-distance` matches the Methods formula, the square root of the summed squared differences. The Methods' "also called root mean squared error" is wrong because the formula has no mean, so the new concept is justified. No existing concept respells it. `pearson-delta` matches the Methods definition. Directions are lower for L2 and higher for Pearson delta. The qualifier names the gene set and the aggregation.
- Units. Pearson delta is `unitless`. L2 is `unit-unreported` with a `unit_detail` (see fix F1).
- Configurations: versions match Methods 'Software versions and parameters'. That is GEARS 0.1.2, scGPT 0.2.1, scFoundation on a GEARS 0.0.2 fork, CPA 0.8.8, Geneformer 0.1.0, scBERT commit 262fd4b9 and UCE commit 8227a65c (four-layer). The linear model uses K = 10 and lambda = 0.1. Asterisked labels in the sheets (`Geneformer*`, `UCE*`, `scBERT*`) match main text paragraph 2 and the linear decoder in Methods.
- Datasets: the Dataverse and figshare file IDs match Data availability. The Norman record is correctly kept apart from the GEARS-processed Norman record.
- Reused records fit. `perturbation-response-20261009-method-train-mean` is the same mean-of-training baseline. No CPA or scBERT model record existed; the existing CPA configurations and the scBERT pipeline are other papers' runs.
- Protocols: splits, denominators and metric definitions match the article and the sheets.

## Fixes made

| Fix | Records | Change | Basis |
| --- | --- | --- | --- |
| F1 | the 21 Fig. 2a L2 results | `unit_detail` no longer says "log-transformed" | The article states a log transform only for the Norman data (main text paragraph 3) |
| F2 | the three `claim-*-single-baselines-not-beaten` claims | Added that the paper states the finding for the single-perturbation benchmark as a whole, not per dataset | Paragraph 16 says "consistently", across datasets. Per dataset, GEARS has a lower mean L2 than both baselines on Adamson and Replogle K562, so attaching the sentence to one dataset's protocol without this note overstates it |
| F3 | `claim-linear-model-pretrained-embeddings` | Moved "(Fig. 2c)" to the paragraph 17 statement and noted that paragraph 18 cites no figure | Paragraph 17 cites Fig. 2c; paragraph 18 does not |
| F4 | the three single-perturbation judgements and protocols; the Norman protocol | Added the UCE and scBERT ground-truth embedding caveat, and named scBERT in the Norman protocol | Methods: UCE paragraph, and scBERT "used the same approach" |
| F5 | `model-cpa`, `model-scbert` | Names and descriptions limited to what the article states | "compositional perturbation autoencoder" and "BERT-style masked objective" are not in the article |

Added to the first concern on Source Data Fig. 2: the effect of using split 1 only (see above).

`claims.csv` was updated for the changed claim text and the review scope.

## Descriptive claims

All nine match their paragraphs (6, 8 and 9, 16, 17 and 18, and the Methods UCE and scBERT paragraphs) after fixes F2 and F3. They report the authors' conclusions as the authors' and do not generalise them. The interaction claim's Fig. 1c reference is supported by paragraph 8.

## Relevance judgements

All four hold as `proxy` for "Which prediction methods and controls should I test before using expression predictions to plan genetic perturbation experiments?":

- The inputs fit: perturbed and control single-cell expression with perturbation labels.
- The output fits: predicted post-perturbation expression assessed against measured responses.
- Each protocol scores models and simple controls on the same held-out perturbations, which I confirmed in the sheets.
- Proxy, not direct: the use case's exclusions say expression scores do not establish mechanism or experimental prioritisation, and the endpoint is expression error in cancer cell lines.
- The Norman protocol trains on all singles and half of the doubles. That meets the use case's input that combinations need combination examples in training.
- Limitations carry the source's caveats: four cancer-cell-line datasets, unimproved QC, authors running every model, UCE and scBERT leakage (F4), no spread, and the evidence concerns. They also state that the values are computed by Rewire.
- `excluded_evaluations` is empty and none is needed. `reviewed_evaluations` lists 9 (Norman) and 7 (each single-perturbation dataset).

Pins are not set. The records are not in the store, so `npm run use-cases:repin` cannot run here.

## Summary claim

The batch adds no summary. The stored `use-case-summary-genetic-perturbation-response` describes Csendes et al. 2025 only, and it stays correct after intake: adding judgements does not withhold it. Any revision must be a separate reviewed change after the judgements are pinned. It must cite only values that pass the gates, which today means the Norman L2 and Pearson delta means, labelled as computed by Rewire from the authors' Source Data. It must not recommend a method.

## For the integrator

1. `npm run records -- add data/omics/perturbation-ahlmann-derived-20261011/batch.jsonl data/omics/perturbation-ahlmann-derived-20261011`.
2. Add the four `assessed_by` links to `use-case-genetic-perturbation-response`. Replace the evidence gap that says Ahlmann-Eltze et al. 2025 was not extracted. Run `records -- change` with this review.
3. `npm run use-cases:repin -- docs/reviews/use-cases/genetic-perturbation-response-2026-10-11.md use-case-mapping-perturbation-ahlmann-20261011-norman-double use-case-mapping-perturbation-ahlmann-20261011-adamson-single use-case-mapping-perturbation-ahlmann-20261011-replogle-k562-single use-case-mapping-perturbation-ahlmann-20261011-replogle-rpe1-single`.
4. Expect the three single-perturbation judgements to be withheld ("a cited source ... has evidence concerns") and the Norman judgement to be active. They are new, so this does not trip the release check on withdrawn judgements.

## Checks

On the reviewed batch: `npm test` (48 files, 511 tests) passed, `npm run typecheck` passed and `npm run build` passed. The build's generated release files were removed and are not part of this review. The trial `records -- add` is described above.

## Remaining gaps

- Fig. 2c, Fig. 1c, Extended Data Fig. 2b, 4 and 8b, and Extended Data Fig. 10, as listed in `coverage.json`.
- No spread of any mean. None was computed.
- The workbooks are not archived in the batch folder. They are hash-pinned at stable publisher URLs. I did not add them, to keep the repository small.
- The article's GitHub link is a branch, not a commit.

## Values checked

59 values, 59 matches. The Extended Data Fig. 2a `no_change` row has no value and no result.

| Figure | Dataset | Method | Metric | Rows |  Batch and script rerun  | Independent reader | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fig. 1a | Norman | `additive_model` | L2 | 310 | 2.766 | 2.766 | Match |
| Fig. 1a | Norman | `cpa` | L2 | 310 | 12.205 | 12.205 | Match |
| Fig. 1a | Norman | `gears` | L2 | 310 | 4.096 | 4.096 | Match |
| Fig. 1a | Norman | `geneformer` | L2 | 310 | 3.478 | 3.478 | Match |
| Fig. 1a | Norman | `no_change` | L2 | 310 | 5.616 | 5.616 | Match |
| Fig. 1a | Norman | `scbert` | L2 | 310 | 4.279 | 4.279 | Match |
| Fig. 1a | Norman | `scfoundation` | L2 | 310 | 4.722 | 4.722 | Match |
| Fig. 1a | Norman | `scgpt` | L2 | 310 | 4.616 | 4.616 | Match |
| Fig. 1a | Norman | `uce` | L2 | 310 | 4.279 | 4.279 | Match |
| ED Fig. 2a | Norman | `additive_model` | Pearson delta | 310 | 0.892 | 0.892 | Match |
| ED Fig. 2a | Norman | `cpa` | Pearson delta | 310 | 0.146 | 0.146 | Match |
| ED Fig. 2a | Norman | `gears` | Pearson delta | 310 | 0.631 | 0.631 | Match |
| ED Fig. 2a | Norman | `geneformer` | Pearson delta | 310 | 0.773 | 0.773 | Match |
| ED Fig. 2a | Norman | `no_change` | Pearson delta | 310 | none | none | No value, as legend states |
| ED Fig. 2a | Norman | `scbert` | Pearson delta | 310 | 0.610 | 0.610 | Match |
| ED Fig. 2a | Norman | `scfoundation` | Pearson delta | 310 | 0.537 | 0.537 | Match |
| ED Fig. 2a | Norman | `scgpt` | Pearson delta | 310 | 0.527 | 0.527 | Match |
| ED Fig. 2a | Norman | `uce` | Pearson delta | 310 | 0.610 | 0.610 | Match |
| Fig. 2a | Adamson | `gears` | L2 | 48 | 3.867 | 3.867 | Match |
| Fig. 2a | Adamson | `geneformer` | L2 | 48 | 3.908 | 3.908 | Match |
| Fig. 2a | Adamson | `lpm_selftrained` | L2 | 48 | 4.081 | 4.081 | Match |
| Fig. 2a | Adamson | `mean` | L2 | 48 | 3.936 | 3.936 | Match |
| Fig. 2a | Adamson | `scbert` | L2 | 48 | 3.878 | 3.878 | Match |
| Fig. 2a | Adamson | `scgpt` | L2 | 48 | 4.951 | 4.951 | Match |
| Fig. 2a | Adamson | `uce` | L2 | 48 | 3.936 | 3.936 | Match |
| Fig. 2a | Replogle K562 | `gears` | L2 | 262 | 4.079 | 4.079 | Match |
| Fig. 2a | Replogle K562 | `geneformer` | L2 | 262 | 4.236 | 4.236 | Match |
| Fig. 2a | Replogle K562 | `lpm_selftrained` | L2 | 262 | 4.097 | 4.097 | Match |
| Fig. 2a | Replogle K562 | `mean` | L2 | 262 | 4.193 | 4.193 | Match |
| Fig. 2a | Replogle K562 | `scbert` | L2 | 262 | 4.192 | 4.192 | Match |
| Fig. 2a | Replogle K562 | `scgpt` | L2 | 262 | 4.437 | 4.437 | Match |
| Fig. 2a | Replogle K562 | `uce` | L2 | 262 | 4.200 | 4.200 | Match |
| Fig. 2a | Replogle RPE1 | `gears` | L2 | 413 | 6.113 | 6.113 | Match |
| Fig. 2a | Replogle RPE1 | `geneformer` | L2 | 413 | 5.494 | 5.494 | Match |
| Fig. 2a | Replogle RPE1 | `lpm_selftrained` | L2 | 413 | 5.390 | 5.390 | Match |
| Fig. 2a | Replogle RPE1 | `mean` | L2 | 413 | 5.534 | 5.534 | Match |
| Fig. 2a | Replogle RPE1 | `scbert` | L2 | 413 | 5.528 | 5.528 | Match |
| Fig. 2a | Replogle RPE1 | `scgpt` | L2 | 413 | 5.991 | 5.991 | Match |
| Fig. 2a | Replogle RPE1 | `uce` | L2 | 413 | 5.507 | 5.507 | Match |
| ED Fig. 8a | Adamson | `gears` | Pearson delta | 48 | 0.726 | 0.726 | Match |
| ED Fig. 8a | Adamson | `geneformer` | Pearson delta | 48 | 0.726 | 0.726 | Match |
| ED Fig. 8a | Adamson | `lpm_selftrained` | Pearson delta | 48 | 0.717 | 0.717 | Match |
| ED Fig. 8a | Adamson | `mean` | Pearson delta | 48 | 0.724 | 0.724 | Match |
| ED Fig. 8a | Adamson | `scbert` | Pearson delta | 48 | 0.728 | 0.728 | Match |
| ED Fig. 8a | Adamson | `scgpt` | Pearson delta | 48 | 0.595 | 0.595 | Match |
| ED Fig. 8a | Adamson | `uce` | Pearson delta | 48 | 0.724 | 0.724 | Match |
| ED Fig. 8a | Replogle K562 | `gears` | Pearson delta | 262 | 0.388 | 0.388 | Match |
| ED Fig. 8a | Replogle K562 | `geneformer` | Pearson delta | 262 | 0.404 | 0.404 | Match |
| ED Fig. 8a | Replogle K562 | `lpm_selftrained` | Pearson delta | 262 | 0.436 | 0.436 | Match |
| ED Fig. 8a | Replogle K562 | `mean` | Pearson delta | 262 | 0.408 | 0.408 | Match |
| ED Fig. 8a | Replogle K562 | `scbert` | Pearson delta | 262 | 0.408 | 0.408 | Match |
| ED Fig. 8a | Replogle K562 | `scgpt` | Pearson delta | 262 | 0.316 | 0.316 | Match |
| ED Fig. 8a | Replogle K562 | `uce` | Pearson delta | 262 | 0.409 | 0.409 | Match |
| ED Fig. 8a | Replogle RPE1 | `gears` | Pearson delta | 413 | 0.636 | 0.636 | Match |
| ED Fig. 8a | Replogle RPE1 | `geneformer` | Pearson delta | 413 | 0.678 | 0.678 | Match |
| ED Fig. 8a | Replogle RPE1 | `lpm_selftrained` | Pearson delta | 413 | 0.680 | 0.680 | Match |
| ED Fig. 8a | Replogle RPE1 | `mean` | Pearson delta | 413 | 0.678 | 0.678 | Match |
| ED Fig. 8a | Replogle RPE1 | `scbert` | Pearson delta | 413 | 0.678 | 0.678 | Match |
| ED Fig. 8a | Replogle RPE1 | `scgpt` | Pearson delta | 413 | 0.588 | 0.588 | Match |
| ED Fig. 8a | Replogle RPE1 | `uce` | Pearson delta | 413 | 0.680 | 0.680 | Match |
