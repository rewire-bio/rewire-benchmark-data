# BRCA1/BRCA2 germline interpretation: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-brca-20261009/` (862 records). Use case: `use-case-brca1-brca2-germline-interpretation`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription against the pinned sources, a recomputation of the ratios from the published counts, and a review of the relevance judgements.

## Outcome

- **Sources.** All three pinned artifacts re-download to their recorded SHA-256. The archived `artifacts/*.gz` decompress to the same bytes.
- **Values.** All 558 results match their source cells. No number was wrong.
- **Recomputation.** All 168 BRCA1/BRCA2 positive likelihood ratios and benignity likelihood ratios were recomputed from Supplementary Table 6 counts. Every value with no zero count in its own cells agrees to the printed three significant figures. Cubuk et al. sometimes truncate rather than round: 72 positive and 73 benignity values match only the truncated form.
- **Disputed results.** 31 Cubuk likelihood ratios divide by a zero count, so they are undefined as printed: 30 benignity ratios with no false negatives, and 1 positive ratio with no calls of deleterious. They are now `disputed`, so they are not shown. Their counts stay visible as the false-negative results.
- **Interval fix.** The Ramadane-Morchadi NPV interval that is probably misprinted is no longer recorded as structured uncertainty.
- **No evidence concerns.** No source `evidence_concerns` were raised and no evaluation is excluded; every problem is limited to specific cells.
- **Judgements.** All four judgements hold as `proxy` after correction. They are `source_checked` with all evaluations in `reviewed_evaluations`. Pins are left for the integrator.
- **Record status.** Every other record is `source_checked`.

## How the check was done

1. Downloaded each `artifact_url` into an empty directory and hashed it.
2. Read the workbook with a stdlib OOXML reader written for this review, and the Ramadane-Morchadi tables from the article XML with my own `table-wrap` reader. The extractor's `extract/*.py` were not imported or run.
3. Matched every result to its cell and compared printed value, numeric value, metric, qualifier, denominator, interval, tool label and the linked configuration and protocol. That is 504 Cubuk and 54 Ramadane-Morchadi cells, all matched once.
4. Cubuk recomputation. From the Supplementary Table 6 counts I computed:
   - TPR/FPR (positive likelihood ratio) and TNR/FNR (benignity likelihood ratio), as Supplementary Table 7 defines them;
   - the 95% log-scale interval for each, from the counts;
   - TP + FN and FP + TN, checked against the printed totals.

   Where a count is zero I also tried the Haldane correction.
5. Ramadane-Morchadi recomputation. No counts are printed. I recomputed PPV, NPV and accuracy from the printed sensitivity and specificity, with the stated 337 LoF and 1,182 FUNC variants. The Results counts (1,015 + 426 + 78 = 1,519 for AlphaMissense at 0.65 and 0.75) were also checked.
6. Read both articles, the Cubuk workbook notes and Supplementary Tables 3, 5 and 7, and the Ramadane-Morchadi declaration of interests and methods.
7. Searched the store of main and every `rewire-benchmark-data-*` worktree, and every batch folder in them, for `model`, `method`, `baseline`, `pipeline` and `service` records matching each new method.
8. Integration dry run in a scratch copy of the repository, with this worktree's store and vocabulary plus the `antisymmetry-bias` concept.
   - Added the somatic oncogenicity batch (1,191 records; re-run with its current `batch.jsonl`, SHA-256 `98a3b2998df30b5e652051d39076804d6e38729b8736bd51c6369f4145c75bbb`, after its BayesDel and ESM-1b duplicates were removed), the protein stability batch (651) and this reviewed batch (862, SHA-256 `f24f480d...`) with `addBatch`. All passed vocabulary, declared-attribute and record validation; SHACL was not run.
   - Added the four `assessed_by` links, pinned the four judgements in memory, and ran `deriveUseCaseInputs`.
   - All four new judgements are `active` (84, 84, 6 and 8 evaluations), and all ten existing judgements stay `active`.

## Sources and hashes

| Source ID | Artifact checked | SHA-256 (re-downloaded 2026-10-09) | Matches record |
| --- | --- | --- | --- |
| `brca-20261009-source-cubuk2021` | PMC8553612 full-text XML | `ea6391e04f5f01353bb611fd45437f21c531848cf3e93b288bdc52494efc90ae` | Yes |
| `brca-20261009-source-cubuk2021-supplementary-tables` | `41436_2021_1265_MOESM3_ESM.xlsx` from static-content.springer.com | `02df1b0dbf916d598dd8278ba45091022bf78c5722ac13a07d5b1b70d64dc179` | Yes |
| `brca-20261009-source-ramadane2025` | PMC12120176 full-text XML | `cd089e7c621818f457f54f93c37cc1b9d535e531212b1aaf431fcbdd733bbda1` | Yes |

## Values checked

| Source table | Results | Metrics | Transcription mismatches | Recomputation |
| --- | --- | --- | --- | --- |
| Cubuk Supplementary Table 9, BRCA1 and BRCA2 columns, 84 rows | 336 | 168 positive LR, 168 benignity LR | 0 | 31 divide by a zero count (disputed); of the other 305, 304 agree with the uncorrected counts to three significant figures, and one zero-count row (Combined-Revel_b-AND-MetaSNP, BRCA2 PLR) prints 3.59 against 3.60 |
| Cubuk Supplementary Table 6, BRCA1_FN and BRCA2_FN | 168 | false-negative count | 0 | TP + FN and FP + TN equal the printed totals on every row |
| Ramadane-Morchadi Table 1 | 24 | 16 log2 LR, 8 no-code proportion | 0 | 1,015 + 426 + 78 = 1,519 for AlphaMissense at 0.65 and 0.75 |
| Ramadane-Morchadi Table 2 | 30 | sensitivity, specificity, PPV, NPV, accuracy | 0 | PPV, NPV and accuracy within 0.3 points of values from sensitivity and specificity |
| Total | 558 | | 0 | |

## Corrections made in the batch

None changes a number. The batch is not in the store, so fields were edited in place. The collector's copy has SHA-256 `e60f1c9563e7478fe96aad381bdeecb6a2877d2671be4651708e907a63093c86`. The reviewed `batch.jsonl` has SHA-256 `f24f480d661e32396f31c0729b38d27d570ecdcaa64699f4d78cf3729786411c`; `review.json` binds it and every other file in the folder. A stray `extract/__pycache__` folder (Python bytecode) was removed before hashing.

1. **Status.** Every record is `source_checked`, except the 31 disputed results. Results carry a `review` block, with the collector's note kept.
2. **Disputed results.** 31 Cubuk likelihood ratios, whose uncorrected ratio is undefined, are now `disputed`, with the counts in `source_anomaly`. The other 31 zero-count results (the ratio not dividing by the zero) keep their values; their `source_anomaly` now says why they are close to the uncorrected ratio.
3. **Ramadane-Morchadi interval.** For `brca-20261009-result-ramadane2025-ddg-af-1-0-3-0-binary-npv`, the structured interval (92.3 to 97.5) was removed. `missing_metadata.uncertainty` is now `conflicting`, and the printed cell is kept in `printed_source_cell`.
4. **Ramadane-Morchadi qualifiers.** These named each tool's threshold, for example "BP4 range (score ≤0.34)", so no two tools could ever share a qualifier and be compared. They now read "BP4 range, LoF versus FUNC", "PP3 range, LoF versus FUNC", "LoF versus FUNC at the tool's PP3 threshold" and "Variants with no computational code (score between the BP4 and PP3 thresholds)". The threshold moved to `score_category` and stays in each configuration's `protocol`.
5. **Configuration notes.**
   - The four Cubuk BayesDel configurations: their thresholds are not the VCEP's.
   - The three VEST3 configurations: they are VEST3 although the family record is named VEST4.
   - The two Align-GVGD configurations: trained on BRCA1/2 classifications (Cubuk Discussion).
   - The three Ramadane-Morchadi configurations whose thresholds were tuned on the evaluated variants.
6. **Limitations.** All six protocol and judgement `limitations` were rewritten (below). Two collector statements were not supported by the sources and were replaced:
   - "the same saturation genome editing data underlie the ENIGMA BayesDel calibration". The stored ENIGMA records describe functional reference labels in the same domains but do not name the data, so overlap is possible, not established.
   - "several authors contribute to the ENIGMA BRCA1/2 VCEP". The article does not say this.
7. **Constraint.** Added to the Cubuk BRCA1 and both Ramadane-Morchadi judgements: they share the same truth data, so agreement is not independent replication. The Ramadane-Morchadi citation locators now include the Declaration of interests.
8. **Vocabulary.** I added a `skos:scopeNote` to each new metric concept (see "New metric concepts").

## Collector concerns: decisions

1. **Cubuk benignity-ratio intervals.** Confirmed, with one correction to the collector's count. The printed interval disagrees with the 95% interval from the counts in 166 of 168 cells. In 131 of them it has the log-scale width of the same row's positive likelihood ratio interval, which looks like a copying error; it is not in all 168. The point values agree with the counts. **Decision: the current treatment is enough.** The interval is not structured uncertainty (`missing_metadata.uncertainty` `conflicting`), and the printed cell survives in `printed_source_cell`; each result's review note now says the interval is not used. Disputing the results would hide correct point values. An `evidence_concern` would withhold both Cubuk judgements for a fault limited to one column of intervals. The positive likelihood ratio intervals agree with the counts in 167 of 168 cells (the exception is a zero-count row) and are kept.
2. **Zero-count cells.**
   - The source says two different things. The Table 9 sheet note says zero-count cells are blank. Methods say a Haldane correction was used, but only for Supplementary Tables 10 and 11.
   - Values are printed in all 31 zero-count tool and gene pairs. Where the zero is in a cell the ratio divides by, the uncorrected ratio is undefined: 30 benignity ratios with FN = 0, and the PrimateAI_a BRCA2 positive ratio with TP = FP = 0. The printed number then reflects only the correction, and my Haldane recomputation reproduces only some of them.
   - **Decision.** Those 31 results are `disputed` and not shown. The false-negative count of 0 stays visible.
   - The other 31 zero-count results divide by non-zero counts and are close to the uncorrected ratio. They are kept with a note.
3. **Ramadane-Morchadi NPV interval.**
   - For ΔΔG (AlphaFold2) at +3 or more, the NPV prints 96.6 (92.3 to 97.5). Sensitivity 89.1 and specificity 85.9 give about 1,052 predicted-FUNC variants and a binomial interval of roughly 95.4 to 97.6. The point estimate itself agrees, at 96.5 recomputed.
   - **Decision.** Keep the value and drop the interval as `conflicting`.
4. **Ramadane-Morchadi conflict of interest and thresholds.**
   - Three authors are Ambry Genetics employees. Ambry is a commercial testing laboratory and none of the compared tools is its own; this is recorded as a limitation. Origin is `independent_paper` for all 14 evaluations, because no author developed AlphaMissense, FoldX or BayesDel.
   - Threshold choice. The AlphaMissense 0.65/0.75 and ΔΔG 1.5/2.5 thresholds were chosen by a "trade-off iterative process" on the same 1,519 variants (Results). The 0.60/0.80 and 1.0/3.0 alternatives have no stated origin. The 0.34/0.56 thresholds are the AlphaMissense developers', and 0.15/0.28 the VCEP's.
   - Recorded on the configurations and in the limitations.
5. **Cubuk's BayesDel thresholds.** Confirmed. Cubuk uses gene-specific cut-offs of 0.074 (BRCA1) and −0.11 (BRCA2) with MaxAF (Supplementary Table 5). The BRCA1 VCEP uses BayesDel no-AF, PP3 at 0.28 or more and BP4 at 0.15 or less (Ramadane-Morchadi Figure 1 legend). Recorded on the four configurations and in the Cubuk limitations, so readers do not equate them with the ENIGMA judgements.
6. **Shared SGE data.**
   - Cubuk BRCA1 (Methods: Findlay et al. 2018 saturation genome editing) and Ramadane-Morchadi (reference 22, the same study) use the same BRCA1 functional data.
   - The page groups them separately (`cubuk2021-functional-truth`, `ramadane2025-pp3-bp4`, `ramadane2025-binary`).
   - A constraint and a limitation on each of the three judgements say that agreement between them is not independent replication.
   - The existing ENIGMA calibration also uses functional labels in these domains, but its data are not named in the stored records, so I do not claim overlap.
7. **New metric concepts.** See below.
8. **Dependencies and VEST4.** The batch needs the somatic oncogenicity and protein stability batches first; the dry run confirms the order works. The oncogenicity record `somatic-oncogenicity-20261009-method-vest4` is a family record (`entity_level` `method`) named "VEST4". Cubuk's three rows are VEST3, so linking them is right, but the family record should be renamed "VEST" in that batch. Until then, the configuration notes say these are VEST3.

## New metric concepts

- **`benignity-likelihood-ratio`.**
  - Definition: proportion benign over proportion pathogenic in an interval, the reciprocal of `likelihood-ratio`. That is correct for Cubuk's TNR/FNR.
  - Direction `higher` is right: larger values are stronger benign evidence.
  - No external match: STATO's negative likelihood ratio is FNR/TNR, the reciprocal, so a match would be wrong.
  - I added a scope note saying so. Because comparison requires the same metric concept, these values can never be compared with `likelihood-ratio` values.
- **`log2-likelihood-ratio`.**
  - Definition: base-2 log of the pathogenic over benign likelihood ratio, negative favouring benignity. Correct.
  - Default direction `unknown` is right, because the direction depends on the interval. Results set `lower` for BP4 ranges and `higher` for PP3 ranges.
  - I added a scope note on this and on the points scale.
  - It is a separate concept from `likelihood-ratio`, so log2 values cannot be compared with linear ones.
- **`negative-predictive-value`.** Added in this branch with the same text as in the oncogenicity branch; the two will merge cleanly. I checked its `skos:exactMatch` against OLS: STATO_0000619 is "negative predictive value".

## Origins and new methods

- Cubuk: all 168 evaluations are `independent_paper`. The authors developed none of the 44 tools, and the paper declares no competing interests. The combinations are the authors' concordance rule over published tools; `independent_paper` is acceptable because the scored outputs are the tools' own calls.
- Ramadane-Morchadi: all 14 are `independent_paper` (see concern 4).
- The 16 new method records (Align-GVGD, Condel, GAVIN, Grantham, Meta-SNP, MLP badmut, MSC, PANTHER, PhD-SNPg, PMut, PON-P2, PredictSNP, rfPred, SiPhy, SNAP2, SuSPect) have no matching `model`, `method`, `baseline`, `pipeline` or `service` record in main, in any worktree store, or in any batch folder.
- The 27 oncogenicity methods, the FoldX method and main's `uc-clinical-20260930-method-bayesdel` all resolve. No link points to a missing record.

## Judgements

The question is "Which evidence-support methods improve BRCA1/BRCA2 variant review without increasing serious classification errors?" None of the sources measures complete classifications, reviewer error or review time. All four protocols score computational evidence inputs against functional classes, so all four are `proxy`, consistent with the ten existing judgements. The serious error for computational evidence is a functionally deleterious variant called tolerated, which would support BP4 for a pathogenic variant. Cubuk's false-negative counts and Ramadane-Morchadi's sensitivity and NPV measure it directly.

| Judgement (`use-case-mapping-brca-20261009-`) | Relevance | Reviewed | Decision |
| --- | --- | --- | --- |
| `cubuk2021-brca1` | proxy | 84 of 84 | Holds; 5 benignity ratios disputed |
| `cubuk2021-brca2` | proxy | 84 of 84 | Holds; 25 benignity ratios and 1 positive ratio disputed |
| `ramadane2025-pp3-bp4` | proxy | 8 of 8 | Holds |
| `ramadane2025-binary` | proxy | 6 of 6 | Holds; NPV interval for one row not recorded |

No evaluation is excluded: each disputed result's evaluation keeps at least its false-negative count and one ratio. Groups and headline metrics hold:
- `cubuk2021-functional-truth`: strata BRCA1 then BRCA2; headline `likelihood-ratio`.
- `ramadane2025-pp3-bp4`: headline `log2-likelihood-ratio`.
- `ramadane2025-binary`: headline `recall`.

The judgement `review` follows the earlier reviews; `reviewed_at` is 2026-10-09T21:50:00Z. After `records -- add` for the two dependency batches and this one, and the link change, pin the four with `npm run use-cases:repin -- docs/reviews/use-cases/brca1-brca2-germline-interpretation-2026-10-09.md <claim-id>...`.

## Approved use-case changes

Apply to `use-case-brca1-brca2-germline-interpretation`. These are links and gaps only, with no pinned field changes, so the ten existing judgements are not affected and need no re-pin. The dry run confirms they stay active.

1. Add `assessed_by` links to `brca-20261009-protocol-cubuk2021-brca1`, `brca-20261009-protocol-cubuk2021-brca2`, `brca-20261009-protocol-ramadane2025-pp3-bp4` and `brca-20261009-protocol-ramadane2025-binary`.
2. Append to `evidence_gaps`:
   - "No linked study measures complete BRCA1/BRCA2 classifications, serious misclassification or reviewer time when computational evidence is added; Cubuk et al. 2021 and Ramadane-Morchadi et al. 2025 score evidence inputs against functional classes."
   - "Cubuk et al. 2021 BRCA1 and Ramadane-Morchadi et al. 2025 both use the Findlay et al. 2018 saturation genome editing data as truth, so they are not independent replications; BRCA2 functional truth in Cubuk et al. covers 188 variants in the DNA-binding domain."
   - "Cubuk et al. 2021 benignity likelihood ratio intervals are inconsistent with the published counts and are not used; ratios that divide by a zero count are not shown."
   - "Ramadane-Morchadi et al. 2025 chose the AlphaMissense and ΔΔG thresholds on the same variants they report; no held-out BRCA1 test of those thresholds is linked."
   - "BRCA2 saturation genome editing (Huang et al. 2025), splicing predictors and non-missense variants are not covered by the linked comparisons."

No change to `decision`, `inputs`, `output`, `setting` or `exclusions` is approved. The existing exclusion "Functional scores and computational predictions are evidence inputs, not complete classifications" already covers the new evidence.

## Evidence summary

Replaces the collector's summary, if one is drafted.

> Two studies add computational-evidence comparisons beside the ENIGMA calibration and the existing classification studies. Both score evidence inputs against functional assay classes, which stand in for pathogenic and benign; neither measures complete classifications, serious misclassification or reviewer time, and values from different studies must not be pooled. For computational evidence, the serious error is a functionally deleterious variant called tolerated, because it would support benign evidence (BP4) for a damaging variant. Cubuk et al. 2021, who developed none of the tools, scored 70 tool-threshold settings and 14 tool combinations against 1,641 BRCA1 variants from saturation genome editing (371 deleterious) and 188 BRCA2 variants from a homology-directed repair assay (64 deleterious). Tools that missed few deleterious BRCA1 variants gave weak evidence toward pathogenicity: CADD (phred, setting a) missed 1 of 370 with a positive likelihood ratio of 1.10, and SIFT missed 3 of 370 with 1.23. REVEL at 0.7 gave 4.54 but called 72 of 371 deleterious variants tolerated, and Meta-SNP gave 2.04 and missed 23. In BRCA2, REVEL gave 2.88 and missed 4 of 64, and Meta-SNP 2.74 and missed 3. Cubuk et al.'s BayesDel thresholds are their own, not the ENIGMA VCEP's. Ramadane-Morchadi et al. 2025 compared scores on 1,519 BRCA1 missense variants from the same saturation genome editing data (337 loss of function, 1,182 functional), so the two BRCA1 analyses are not independent. With the VCEP BayesDel thresholds, the log2 likelihood ratio was −2.923 in the benign-evidence range and +2.643 in the pathogenic range, with 14% of variants left without computational evidence. With the AlphaMissense developers' thresholds, it was −4.603 and +2.083 with 12% left, and with AlphaMissense thresholds the authors chose on these same variants, −2.914 and +2.810 with 5% left. At the PP3 threshold, sensitivity for loss of function was 79.8% for BayesDel, 84.3% for AlphaMissense at 0.75 and 89.1% for FoldX ΔΔG on AlphaFold2 models at +3 kcal/mol. Three of those authors work for a commercial testing laboratory. These are BRCA1 RING and BRCT and BRCA2 DNA-binding-domain missense results only, and they do not establish clinical classification performance.

`source_ids`: `brca-20261009-source-cubuk2021`, `brca-20261009-source-cubuk2021-supplementary-tables`, `brca-20261009-source-ramadane2025`.

| Statement | Record (`brca-20261009-`) | Printed |
| --- | --- | --- |
| 1,641 BRCA1 variants, 371 deleterious | `data-cubuk2021-brca1-functional` (`population`, `denominator`) | 1641; 371 |
| 188 BRCA2 variants, 64 deleterious | `data-cubuk2021-brca2-functional` | 188; 64 |
| 70 settings and 14 combinations | `protocol-cubuk2021-brca1` (`description`); 84 evaluations | |
| CADD phred_a: 1 of 370 missed, PLR 1.10 | `result-cubuk2021-cadd-phred-a-brca1-false-negatives` (denominator 370), `-plr` | 1; 1.10 |
| SIFT: 3 of 370 missed, PLR 1.23 | `result-cubuk2021-sift-brca1-false-negatives`, `-plr` | 3; 1.23 |
| REVEL_b BRCA1: PLR 4.54, 72 of 371 missed | `result-cubuk2021-revel-b-brca1-plr`, `-false-negatives` | 4.54; 72 |
| Meta-SNP BRCA1: PLR 2.04, 23 missed | `result-cubuk2021-metasnp-brca1-plr`, `-false-negatives` | 2.04; 23 |
| REVEL_b BRCA2: PLR 2.88, 4 of 64 missed | `result-cubuk2021-revel-b-brca2-plr`, `-false-negatives` | 2.88; 4 |
| Meta-SNP BRCA2: PLR 2.74, 3 missed | `result-cubuk2021-metasnp-brca2-plr`, `-false-negatives` | 2.74; 3 |
| Cubuk BayesDel thresholds are not the VCEP's | `config-cubuk2021-bayesdel-*` (`model_identity_note`) | |
| 1,519 variants, 337 LoF, 1,182 FUNC | `data-ramadane2025-brca1-mave` | |
| BayesDel VCEP: −2.923, +2.643, 14% | `result-ramadane2025-bayesdel-0-15-0-28-pp3-bp4-{bp4-log2-lr,pp3-log2-lr,no-code-proportion}` | −2.923; +2.643; 14% |
| AlphaMissense developer thresholds: −4.603, +2.083, 12% | `result-ramadane2025-am-0-34-0-56-pp3-bp4-{bp4-log2-lr,pp3-log2-lr,no-code-proportion}` | −4.603; +2.083; 12% |
| AlphaMissense tuned thresholds: −2.914, +2.810, 5% | `result-ramadane2025-am-0-65-0-75-pp3-bp4-{bp4-log2-lr,pp3-log2-lr,no-code-proportion}`; tuning in `config-ramadane2025-am-0-65-0-75` | −2.914; +2.810; 5% |
| Sensitivity 79.8, 84.3, 89.1 | `result-ramadane2025-{bayesdel-0-15-0-28,am-0-65-0-75,ddg-af-1-0-3-0}-binary-sensitivity` | 79.8; 84.3; 89.1 |
| Three authors at a commercial laboratory | `protocol-ramadane2025-*` (`limitations`), Declaration of interests | |

## Checks run

`npm test` passed (46 files, 499 tests) and `npm run typecheck` passed, on the worktree with the reviewed batch and the vocabulary scope notes. The batch is not yet in the store, so the tests do not read it; the scratch three-batch `addBatch` and `deriveUseCaseInputs` dry run is the check that covers it. `npm run build` and SHACL shapes were not run.

## Remaining gaps

- Cubuk Supplementary Tables 8, 10, 11 and 13, the other genes and the ClinVar columns were not extracted (collector's scope); Supplementary Table 1 tool classifications were not checked against the method types.
- Ramadane-Morchadi Tables S1 to S6 and Table 3 were not read.
- The stored ENIGMA records do not name the functional data behind the VCEP BayesDel calibration, so overlap with the Findlay data is unresolved.
- The oncogenicity "VEST4" family record name should change in that batch.
