# Plasma ctDNA fragmentomics: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-ctdna-fragmentomics-20261009/` (772 records). Use case: `use-case-plasma-ctdna-fragmentomics`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced; this is a check of transcription against the pinned sources, plus a judgement of the relevance claims.

## Outcome

- All four source artifacts re-download to the pinned SHA-256, the UNITE zip member matches its recorded hash, and the three archived `artifacts/*.gz` decompress to the pinned bytes.
- All 593 results match their source cells. No printed value, numeric value, locator, metric, qualifier, unit, direction, interval, denominator, configuration, protocol or dataset was wrong. Every expected cell has exactly one result.
- The collector's source-level concern on the Hou et al. supplement is real but narrower than recorded. I found which table is wrong for the pan-cancer block and moved the concern from the source to the affected values:
  - 20 Table S2 pan-cancer sensitivities are `disputed`: Table S9 is right and Table S2 is shifted.
  - 20 Table S2 liver cancer sensitivities are `disputed`: the two columns are near copies.
  - The other 230 Hou supplement results are `source_checked`.
- 15 UNITE ichorCNA-TF fixed-specificity results are `disputed`: the 9 the collector flagged in the (0.1, 1] stratum, and 6 accuracy and F1 values in the [0, 0.03] stratum that contradict the per-fold data.
- The IFS author overlap is confirmed. The 7 IFS evaluations are now `author_reported`.
- The UNITE cross-validation set shares samples with two Hou et al. cohorts, not one: the DELFI 2019 cohort and the Jiang et al. liver cohort. Both are now recorded.
- All 10 relevance judgements hold as `proxy` and are `source_checked`, with `reviewed_evaluations` filled. Pins are left for the integrator.
- In an in-memory simulation with the approved use-case changes, all 10 new judgements derive as active. The existing DELFI judgement `use-case-mapping-amp-20261007-issue15` is withheld by the use-case text change and becomes active again once re-pinned.
- The proposed gap "no fragmentomic sensitivity at 98% or 99% specificity within a low tumour-fraction stratum was found in a printed table" is wrong. Such values are printed in the unextracted sheet STATS_xgb_all_feat, which has its own problem (see Remaining gaps). The approved text says this.

## How the check was done

1. Downloaded each `artifact_url` into its own empty directory and hashed it. Unzipped the UNITE data-file zip and hashed both members.
2. Read the workbooks with a stdlib OOXML reader written for this review: shared strings, raw `<v>` text, and the number format from `styles.xml`. Every extracted cell is General format. Read article Table 1 from `table-wrap id="advs8741-tbl-0001"` with a separate XML reader. The extractor's `extract/*.py` was not imported or run.
3. Built the expected identity of every cell from the sheet title, header row and row labels, then matched each result to its cell through `source_locator` and compared:
   - the raw cell text (`raw_xml_value`, or `printed_source_cell` for Table 1);
   - `printed_value`: the leading number of a text cell, or the shortest round-trip decimal of a numeric cell;
   - `numeric_value`, metric, qualifier, unit and direction;
   - the 95% interval, and for UNITE the median, SD and SEM cells in `source_cells`;
   - `denominator_note` against Hou Experimental Section P24;
   - the linked evaluation's configuration, protocol and dataset, and its `protocol` and `comparison.protocol_id`.
4. Recomputed the UNITE STATS sheets from the per-fold RAW sheets: every mean and median in STATS_xgb_x1-x6 (50 folds per row) and every traceable row of STATS_lr reproduces to within 7e-16.
5. Cross-checked Hou Table S2 against Tables S7, S8, S9 and S10 of the same workbook (see the Hou et al. section).
6. Read the cited paragraphs of both articles, both author lists and competing-interest statements, the CRAG paper's author affiliations (Europe PMC record for DOI 10.1186/s13073-022-01141-8), and UNITE Data file S1 sheets s3 and s13.
7. Loaded the reviewed batch with `recordSchema`, `validateVocabularies`, `validateAttributes` and `validateRecords` against the current store, in memory. Applied the approved use-case changes, computed pins with `claimPins`, and ran `deriveUseCaseInputs`. Nothing was written to the store.

Paragraph numbers count body paragraphs and exclude figure and table captions, the scheme the extractor used.

## Sources and hashes

| Source | Pinned SHA-256 | Re-download 2026-10-09 |
| --- | --- | --- |
| `ctdnafrag-20261009-source-hou2024` (PMC11321639 XML) | `d029fc9d...ace70` | Match; archive decompresses to it |
| `ctdnafrag-20261009-source-hou2024-supporting-information` (ADVS-11-2308243-s001.xlsx) | `41b24f7e...95fb0` | Match; archive decompresses to it |
| `ctdnafrag-20261009-source-wang2026` (PMC13353424 XML) | `61464a27...6fb23` | Match; archive decompresses to it |
| `ctdnafrag-20261009-source-wang2026-data-file-s2` (data files zip) | `d28e1dbf...efe12` | Match; member `ady9432_data_file_s2.xlsx` `32ae4ff3...65aa` matches `hash_scope` |

I also read the other zip member, `ady9432_data_file_s1.xlsx` (SHA-256 `65d739cda3c4bb10d550b8c7e74360ae7b5d3fd69370e448d6b98fdab10fbdb9`), to count shared samples. It is recorded in the data-file source's `limitations`.

## Values checked

| Table | Results | Matched | Wrong | Disputed after review |
| --- | --- | --- | --- | --- |
| Hou article Table 1 (25 cells; 8 `/` cells are not results) | 25 | 25 | 0 | 0 |
| Hou Table S2 (90 AUC, 180 sensitivity) | 270 | 270 | 0 | 40 |
| Hou Table S3 | 90 | 90 | 0 | 0 |
| UNITE STATS_xgb_x1-x6 (144 rows) | 144 | 144 | 0 | 0 |
| UNITE STATS_lr (64 rows) | 64 | 64 | 0 | 15 |
| Total | 593 | 593 | 0 | 55 |

Integer-valued UNITE cells are stored as `0` or `1` and printed that way. Hou S2 cell E64 lacks its closing bracket, as the collector noted.

Article text checks, not recorded as results:
- UNITE Results P13 AUCs for the [0, 0.03] stratum (0.878, 0.873, 0.857, 0.736, 0.715, 0.651) and P18 values (UNITE-XGB 0.916, ichorCNA-TF 0.642, 0.603 and 0.983, ichorCNA-TF sensitivity 37.4% at 95% specificity) match the sheets.
- Four printed confidence bounds differ from the sheet in the third decimal, for example the S/L lower bound is 0.640 in P13 and 0.639 in the sheet. Methods P54 uses a bootstrap, so this is consistent with a separate bootstrap run. Results use the sheet.
- UNITE P13 says the raw data are in "data file S1"; they are in Data file S2. Data file S1 holds the sample tables.
- Hou P24 cohort sizes match every dataset record and denominator note.

## Hou et al. Supporting Information: which table is wrong

### Pan-cancer block of Table S2

The collector's observation holds for all ten patterns: Table S9's SVM "Sensitivity @95% specificity" equals Table S2's "Sensitivity @85% specificity", and Table S9's values at 85% appear nowhere else. AUC is identical across S2, S9 and article Table 1. Table S2's values at 95% (D3:D12) also appear nowhere else in the workbook.

Two other tables in the same workbook decide it:

- **Table S10** reruns six patterns after GC correction in the same open chromatin regions. Where GC correction leaves AUC almost unchanged, its sensitivities sit within 0.01 of Table S9 and 0.03 to 0.05 above Table S2:

  | Pattern | AUC (S10, S2) | Sensitivity at 95% (S10, S9, S2) | Sensitivity at 85% (S10, S9, S2) |
  | --- | --- | --- | --- |
  | coverage | 0.9637, 0.9638 | 0.8857, 0.8877, 0.8444 | 0.9260, 0.9284, 0.8877 |
  | end | 0.9624, 0.9639 | 0.8756, 0.8775, 0.8212 | 0.9235, 0.9328, 0.8775 |
  | IFS | 0.9641, 0.9653 | 0.8793, 0.8856, 0.8492 | 0.9252, 0.9276, 0.8856 |

- **Table S7** has the same layout as Table S2 (TSS regions instead of open chromatin). Its pan-cancer rows agree with the TSS rows of Table S10 (coverage 0.8591 and 0.9254 against 0.8557 and 0.9245). So the layout itself is sound and the shift is specific to Table S2's pan-cancer block.

Conclusion: Table S9 is right. In Table S2's pan-cancer rows, the column labelled 85% holds the 95% values, and the column labelled 95% holds values at an unstated threshold. Both columns are wrong as labelled, so all 20 pan-cancer sensitivities are `disputed`.

### Per-cancer blocks of Table S2

Table S9 covers only the pan-cancer models, so the seven per-cancer blocks (BRCA to PAAD, 140 sensitivities) have no second table to check against. Their 85%-minus-95% gaps (median 0.05 to 0.10 per group) look like those of Tables S7 and S8 for the same groups. Nothing shows them to be wrong, so they stay `source_checked`, with a note on each result and a line in the judgement's limitations.

### Liver block of Table S2

Nine of ten rows print the same value and interval at 95% and 85% specificity. The tenth (length) differs by 0.0009 (0.4631 and 0.4640). In Tables S7 and S8 the same liver rows show a median gap of 0.15 and 0.10. The block does not behave like two measured thresholds, and which column is wrong cannot be told. All 20 liver sensitivities are `disputed`, including the two length values the collector did not flag. The 10 liver AUCs stay.

### Table S3

Table S3 (independent validation) has no second table to check against. Its values are counts over the cohort sizes (multiples of 1/8, 1/129 and 1/46), as expected. It stays `source_checked`, with a note on each result.

### Decision

I removed the source-level `evidence_concerns` entry and recorded the facts in the source's `limitations`. Each of the 40 affected results carries the detail in `source_warnings`. No evaluation is excluded: every Hou evaluation keeps at least one clean result, and disputed results are not shown on use-case pages (`buildUseCaseArtifact` keeps only `source_checked` or `reproduced` results). A source-level concern would have withheld all five Tables S2-S3 judgements, including 230 values with no evidence against them.

The collector's other Table S9 point is confirmed: the WPS logistic-regression row (C45:E45) repeats the OCF row (C35:E35). Table S9 is not extracted, and this does not affect the SVM rows used above.

## UNITE ichorCNA-TF fixed-specificity values

The collector flagged nine values in the (0.1, 1] stratum. RAW_lr confirms them and shows the problem is wider.

- **(0.1, 1].** The classifier is perfect in all 50 folds (AUROC, sensitivity, specificity, accuracy and F1 all 1). Sensitivity at any specificity of 95% or more must then be 1. The sheet prints 0 at 95%, 98% and 99%, F1 0, and accuracy equal to half the target specificity (0.475, 0.49, 0.495) with SD 0. All 9 fixed-specificity results are `disputed`.
- **[0, 0.03].** In 27 of 50 folds at 95% and all 50 at 99%, accuracy is exactly half the target specificity and F1 is 0. In 27 and 6 of those folds, sensitivity at the same specificity is above 0. F1 0 means no true positives, so the two cannot both hold at one threshold. The 98% rows show the same constants with SD 0. The 6 fixed-specificity accuracy and F1 results are `disputed`. Sensitivity at 95% is above 0 in every fold and is consistent with the stratum's AUROC of 0.603, so the three fixed-specificity sensitivities stay `source_checked` with a note.
- **(0.03, 0.1] and all.** At 99%, 4 and 8 of the 50 folds show the same constants (accuracy 0.495, F1 0, sensitivity 0). These are internally consistent, so the values stay, with a note that the means include them.
- **98% rows, all strata.** RAW_lr has no 98% rows, and Methods P47 names only 95% and 99%. These means cannot be recomputed. They stay, with a note.

As for Hou, the concern goes into the data-file source's `limitations` and each disputed result's `source_warnings`. No evaluation is excluded.

## Origin and author overlap

- **IFS.** Hou et al.'s IFS reference (ref 10) is Zhou X, Zheng H, Fu H, Dillehay McKillip KL, Pinney SM, Liu Y, Genome Med 2022 (CRAG). The Europe PMC record gives its first author's present address as "Hubei Key Laboratory of Agricultural Bioinformatics, College of Informatics, Huazhong Agricultural University", which is Hou et al.'s affiliation 1 for their corresponding author Xionghui Zhou, who also conceived the study. These are the same person. The 7 IFS evaluations (Table 1 open chromatin and PCA, S2 Cristiano and Jiang, S3 Zhou, LUCAS and Mathios independent) are now `author_reported`, each with a limitation. The Zhou cohort comes from the same CRAG paper; its dataset and protocol now say so. The other nine patterns, and DELFI, cite papers with no Hou et al. author.
- **UNITE.** The six XGBoost feature sets are the authors' framework (`author_reported`). The ichorCNA-TF comparator was built by the UNITE authors on ichorCNA output; no ichorCNA author is on the paper. I agree with `independent_paper`, consistent with how comparators built by other groups were recorded in the CNV review. Its existing limitation names who built it. H.W., H.Z. and N.R. are named inventors on two pending patent applications for the methods; this is now in the UNITE judgement limitations.

## Cohort overlaps

UNITE Data file S1 (sheet s13, split `cv`) shows the cross-validation set draws:
- 352 samples (182 healthy, 170 cancer) from the Cristiano et al. 2019 FinaleDB data, the cohort of the stored DELFI dataset and of Hou et al.'s cross-validation;
- 86 samples (23 healthy, 63 hepatocellular carcinoma) from FinaleDB data labelled "Jiang et al, 2015". Sheet s3 gives its full composition as 225 samples: 32 healthy, 67 hepatitis B, 36 cirrhosis and 90 hepatocellular carcinoma. That is exactly Hou et al.'s Jiang cohort (P24), which Hou et al. cite as Jiang et al. 2018.

FinaleDB's Cristiano data has 538 samples, more than the 423 of the DELFI cohort, so the exact number of shared individuals cannot be counted from the published tables. The UNITE dataset's `scope_note`, the Jiang dataset's `scope_note`, the UNITE protocols' limitations and the Hou and UNITE judgements now record both overlaps.

## Other points the collector asked about

- **LIHC controls.** Confirmed unstated. Methods P44 says the independent-validation liver model used "all samples" of the Jiang cohort, but does not say which controls the cross-validated model used. The record stays unreported.
- **DELFI records.** Agreed. The store has no DELFI method; the new method and Hou's configuration are not duplicates. The stored DELFI configuration was not changed.
- **Lung training set.** Methods P44 says the lung model for both Mathios cohorts was trained on the Cristiano lung cancers and their controls: 12 cancers and 215 healthy individuals. The protocols already said so; the judgements now do too.

## Corrections made in the batch

The batch is not in the store, so fields were edited in place. No ID, value, locator, metric, qualifier, unit, direction, interval, comparison field, link or source hash changed (checked by a field-by-field diff against the collector's copy, SHA-256 `24829f0270b5ae4a109af5d538fa0befd877b5908592a53427592637764d1d52`).

| Record | Field | Change |
| --- | --- | --- |
| 40 Hou S2 results (pan-cancer and liver sensitivities) | `status`, `source_warnings` | `disputed`, with the conflict described |
| 15 UNITE ichorCNA-TF results | `status`, `source_warnings` | `disputed`, with the per-fold evidence |
| Other 538 results | `status` | `source_checked` |
| All 593 results | `review` | Independent review block. Notes added on the 140 per-cancer S2 sensitivities, the 90 S3 values, and the kept ichorCNA-TF fixed-specificity values |
| `ctdnafrag-20261009-source-hou2024-supporting-information` | `evidence_concerns`, `limitations` | Concern removed; narrowed facts in `limitations` |
| `ctdnafrag-20261009-source-wang2026-data-file-s2` | `limitations` | ichorCNA-TF finding; the P13 file-name slip; Data file S1 hash |
| 7 IFS evaluations | `origin`, `limitations` | `independent_paper` to `author_reported`, with the reason |
| 4 ichorCNA-TF evaluations | `limitations` | Stratum-specific fixed-specificity notes |
| UNITE, Jiang and Zhou datasets | `scope_note` | Cohort overlaps; Zhou cohort authorship |
| 10 protocols | `limitations` | Source-concern wording narrowed; IFS origin; shared healthy controls and overlaps (UNITE); Zhou cohort authorship |
| 2 descriptive claims | `status`, `review` | Checked against the text; correct as worded |
| 10 relevance judgements | `status`, `review`, `reviewed_evaluations`, `limitations`; `endpoint` for 3; `rationale` and `description` for 5 | See Relevance judgements |
| All sources, methods, configurations, datasets, protocols, evaluations | `status` | `source_checked` |

`claims.csv` needs no change: no locator or printed value changed. `research.md`, `sources.md` and `coverage.json` are the collector's notes and still describe the concern as source-level; they were left unchanged.

## New metric concepts

`sensitivity-at-85-percent-specificity`, `sensitivity-at-95-percent-specificity` and `sensitivity-at-99-percent-specificity` are accepted. Each copies the shape of the existing `sensitivity-at-98-percent-specificity`: same type, scheme, definition pattern, `skos:broader :recall` and default direction `higher`. No external match is asserted, which is consistent with the 98% concept. The altLabels are source column labels (`Sensitivity @85% specificity`, `Sensitivity @95% specificity`, `test_sen_99spe`). The 95% concept lacks the matching `test_sen_95spe` label; that is harmless. The concepts name the metric only; how a source chooses its threshold (UNITE does not say) belongs in the result's qualifier and the evaluation's `metric_implementation`, which are unreported here.

## Relevance judgements

All ten are `proxy`, and I agree with each grade. The use case asks which fragmentomics workflow detects tumour-derived plasma DNA at low tumour fractions under a fixed false-positive constraint.

The UNITE [0, 0.03] stratum came closest to `direct`. It is real plasma, a low ichorCNA stratum and real cancers, but sensitivity at a fixed specificity exists only for the ichorCNA-TF comparator, which is not a fragmentomics workflow. The fragmentomic models have AUC and default-threshold metrics only. The stratum is also an ichorCNA estimate of 3% or less, which includes cancers below ichorCNA's detection limit, not a measured low fraction. That is proxy. If the fragmentomic models' fixed-specificity sensitivities are extracted from STATS_xgb_all_feat and pass review, a future judgement on that stratum could be graded direct, subject to the developer and cross-validation caveats.

| Judgement | Endpoint fit | Changes made | Reviewed evaluations |
| --- | --- | --- | --- |
| `...-hou2024-pattern-auc` | AUC only on one cohort | Limitations: IFS author-reported; UNITE overlap | 25 |
| `...-hou2024-cris` | Sensitivity at 95% and 85% on real plasma, no TF stratum | Endpoint and rationale say pan-cancer sensitivities are not shown; concern narrowed; IFS; overlap | 10 |
| `...-hou2024-jiang` | AUC only, after withholding the sensitivities | Endpoint, rationale and limitations rewritten; controls unstated; IFS; Jiang overlap | 10 |
| `...-hou2024-zhou` | Independent validation, 8 against 8 | Rationale; cohort and IFS by the same author; S3 has no cross-check | 10 |
| `...-hou2024-lucas` | Independent validation; non-cancer group includes benign nodules | Rationale; 12-cancer training set; S3 note; IFS | 10 |
| `...-hou2024-mathios-ind` | Independent validation | Rationale; 12-cancer training set; S3 note; IFS | 10 |
| `...-wang2026-tf-0-3pct` | Low ichorCNA stratum; fixed-specificity sensitivity only for the comparator | 70% training split; ichorCNA estimates; patents; overlaps; disputed comparator values | 7 |
| `...-wang2026-tf-3-10pct` | As above, intermediate stratum | As above; 99% fold note | 7 |
| `...-wang2026-tf-over-10pct` | High stratum, context for the ranking change | Endpoint says the comparator's fixed-specificity values are not shown | 7 |
| `...-wang2026-tf-all` | Unstratified | As above; 99% fold note | 7 |

No `excluded_evaluations` are needed: every evaluation still has a clean result, and disputed results are filtered from the page.

**Grouping.** Three comparison groups:
- `hou2024-pattern-auc`, headline `auroc`;
- `hou2024-sensitivity`, headline `sensitivity-at-95-percent-specificity`, strata 1 to 5 from cross-validation cohorts to independent cohorts;
- `wang2026-tf-strata`, headline `auroc`, strata ordered from the lowest tumour fraction to unstratified.

The headlines are right: sensitivity at 95% is the stricter of Hou's two thresholds, and AUROC is the only metric UNITE prints for every feature set. In the simulation, the Hou Cristiano stratum shows 70 headline values (seven cancer types), the Jiang stratum shows none (its sensitivities are withheld; AUC is still shown), and each UNITE stratum shows 7.

## Use-case changes (coverage.json)

The proposed `assessed_by` links are right. On `source_ids`, I approve adding both clean articles, `ctdnafrag-20261009-source-hou2024` and `ctdnafrag-20261009-source-wang2026`, because the new `setting` text rests on them. The supplement and data-file sources stay cited by their judgements only, so a later concern on a table does not withhold every judgement on the use case.

Changes to the proposal:
- The tumour-fraction exclusion becomes a gap, as proposed, but the proposed gap text is wrong. Fixed-specificity sensitivities for the fragmentomic models are printed in STATS_xgb_all_feat; they were not extracted.
- The Curtis et al. item is a gap, not an exclusion: the use case does not set false positives in inflammatory disease out of scope.
- The two gaps that said "evidence concern" are reworded to say which values are not shown.
- `decision`, `output`, `setting` and `clinical_scope` described only the DELFI result. They need wording that covers several methods.

Changing `decision`, `output`, `setting`, `exclusions` or `clinical_scope` alters pinned fields of `use-case-mapping-amp-20261007-issue15`. It will be withheld until re-pinned, and the release guard refuses a release that withholds a judgement the previous release served. The integrator must re-pin it in the same change: `npm run use-cases:repin -- docs/reviews/use-cases/plasma-ctdna-fragmentomics-2026-10-09.md use-case-mapping-amp-20261007-issue15`, together with the ten new judgements.

### Approved use-case changes

Exact final values for `use-case-plasma-ctdna-fragmentomics`. Fields not listed (`name`, `description`, `question`, `intended_users`, `inputs`, `search_terms`, `collection_plan`, `planned_work`, facets) are unchanged.

`links`: keep the existing `assessed_by` link to `amp-20261007-ctdna-fragmentomics-protocol` and add `assessed_by` links to:

```
ctdnafrag-20261009-protocol-hou2024-cristiano-pancan-cv-auc
ctdnafrag-20261009-protocol-hou2024-cristiano-cv-sensitivity
ctdnafrag-20261009-protocol-hou2024-jiang-lihc-cv-sensitivity
ctdnafrag-20261009-protocol-hou2024-zhou-lihc-independent
ctdnafrag-20261009-protocol-hou2024-mathios-lucas-independent
ctdnafrag-20261009-protocol-hou2024-mathios-independent
ctdnafrag-20261009-protocol-wang2026-unite-cv-tf-0-3pct
ctdnafrag-20261009-protocol-wang2026-unite-cv-tf-3-10pct
ctdnafrag-20261009-protocol-wang2026-unite-cv-tf-over-10pct
ctdnafrag-20261009-protocol-wang2026-unite-cv-tf-all
```

`source_ids`:

```
amp-20261007-ctdna-fragmentomics-source
ctdnafrag-20261009-source-hou2024
ctdnafrag-20261009-source-wang2026
```

`decision`:

> Compare the fragmentomic feature sets and classifiers with printed detection results on shared plasma cohorts, including one source stratified by ichorCNA tumour fraction, before selecting a workflow and a validation design with a fixed specificity for the intended screening or diagnostic population.

`output`:

> Sourced AUC and sensitivity-at-fixed-specificity figures for fragmentomic workflows from internal cross-validation and small independent validations, and AUCs within ichorCNA tumour-fraction strata from one developer study; no prospective screening-validation claim.

`setting`:

> Retrospective case-control plasma cfDNA whole-genome sequencing. The DELFI classifier achieves 73% (152 of 208) sensitivity at a reported 98% specificity in repeated 10-fold cross-validation (10 repeats) across 208 cancer patients (seven cancer types) and 215 healthy individuals. Hou et al. 2024 re-implemented ten published fragmentation patterns and DELFI with one support vector machine each on the same cohort, on a liver cancer cohort and on three independent validation cohorts. Wang et al. 2026 (UNITE) cross-validated five shallow-WGS fragmentomic feature sets, their combination and an ichorCNA tumour-fraction classifier within ichorCNA tumour-fraction strata, on pooled public and new data that include samples of the DELFI and Jiang et al. cohorts.

`exclusions` (the tumour-fraction exclusion is removed and becomes the third gap below):

```
A combined mutation+DELFI configuration (115/126, 91%), a different subset/configuration not ingested here
Prospective screening performance and clinical benefit: no prospective or intended-use cohort was ingested
```

`clinical_scope`:

> Clinical applicability is not established. Every result comes from a retrospective case-control cohort, with internal cross-validation or small independent validations (8 to 129 cancers), not from a prospective screening trial. The clinically identified cancers and healthy comparators differ from an intended screening population, and tumour fractions are ichorCNA estimates, not measured values.

`evidence_gaps`:

```
4 of 215 healthy individuals were misclassified at the source-labelled 98% specificity; the printed specificity is retained rather than recomputed.
cfDNA signal reflects total circulating DNA, not purified ctDNA.
Tumour-fraction-stratified evidence is cross-validation from one developer study (Wang et al. 2026). In the extracted tables, sensitivity at a fixed specificity within a tumour-fraction stratum is printed only for the ichorCNA tumour-fraction comparator. The fragmentomic models' values are in Data file S2 sheet STATS_xgb_all_feat, which was not extracted; that sheet prints identical sensitivity at 98% and 99% specificity for every feature set in the lowest stratum and needs checking before use.
Hou et al. 2024 Supporting Information Table S2 pan-cancer and liver cancer sensitivities conflict with other tables of the same file and are not shown.
No independent dilution-series or limit-of-detection comparison of fragmentomic tools (Griffin, LIQUORICE, FinaleToolkit, DELFI) with printed values was found.
No specificity in patients with inflammatory, autoimmune or vascular disease was ingested; Curtis et al. 2025 (PNAS) report false positives in these groups with per-sample data only.
No result is comparable across sources: cohorts, feature implementations, classifiers and validation designs differ, and the sources share samples of the DELFI 2019 and Jiang et al. cohorts.
```

`citation_locators`: keep the existing entry and add:

```
{"source_id": "ctdnafrag-20261009-source-hou2024", "locator": "Table 1; Experimental Section P24-P45"}
{"source_id": "ctdnafrag-20261009-source-wang2026", "locator": "Results P9-P18; Methods P38-P49"}
```

### Does `use-case-mapping-amp-20261007-issue15` still hold?

Yes, unchanged, as `proxy`. Its endpoint (DELFI sensitivity 73%, 152 of 208, at a reported 98% specificity, repeated 10-fold cross-validation) is still the only sensitivity at a screening-level specificity for a fragmentomic classifier among the use case's judgements. It matches the new decision, which asks for sensitivity at a fixed specificity. It is still proxy for the same reasons: internal cross-validation, a clinically identified cohort, and no tumour-fraction stratum. Every limitation it carries remains true, including "tumour fraction limit is unreported for this endpoint". The new setting text quotes its numbers unchanged.

One limitation is now missing: its cohort reappears in the Hou et al. judgements and, in part, in the UNITE cross-validation set. That is recorded on the new judgements and in the last evidence gap, so the DELFI judgement need not change. If the integrator prefers to state it there too, the text is: "The same cohort is re-analysed by Hou et al. 2024, and the UNITE cross-validation set (Wang et al. 2026) draws 352 samples from its FinaleDB data." That edit would need a records change citing this review.

## Evidence summary

The collector's proposal is mostly right. It needs five changes:
- It says the supplementary values "should not be cited until resolved"; now only the conflicting blocks are withheld.
- It does not name the DELFI developers as author-reported, or the IFS author overlap.
- It does not name the Jiang cohort overlap.
- It says no source gives fragmentomic sensitivity at 98% or 99% specificity within a low stratum; an unextracted sheet does.
- It does not mention that the lung model was trained on 12 cancers.

Final text:

> Three sources compare plasma cfDNA fragmentomic workflows on shared retrospective case-control cohorts. None is a prospective screening study and none measures clinical benefit. Cristiano et al. 2019, the DELFI developers, report 73% sensitivity (152 of 208 cancers) at a reported 98% specificity for DELFI in repeated cross-validation against 215 healthy individuals. Hou et al. 2024 re-implemented ten published fragmentation patterns and DELFI with one support vector machine each on the same cohort. They are independent of every pattern except IFS, which their corresponding author developed. In 10 x 10-fold cross-validation, pan-cancer AUC within open chromatin regions ranged from 0.8741 (fragment length) to 0.9736 (5' end motif), and their DELFI re-implementation reached 0.9575. Rankings changed on independent cohorts. On 46 lung cancers and 385 healthy individuals, with a model trained on 12 lung cancers, the end-motif model fell to AUC 0.5355 and sensitivity 0.0652 at 95% specificity, while fragment size distribution reached 0.9386 and 0.7174. Hou et al.'s supplementary pan-cancer and liver cancer sensitivities conflict with other tables of the same file and are not shown. Wang et al. 2026, the UNITE developers, stratified cancers by ichorCNA tumour fraction in pooled public and new 0.1x data that include samples of the DELFI and Jiang et al. cohorts used above. For cancers with an estimated tumour fraction of 3% or less, cross-validated AUC was 0.878 for all five features combined, 0.873 for fragment length, 0.857 for the SD of length counts, 0.736 for copy number, 0.715 for the C/T end-motif ratio and 0.651 for the short/long ratio, against 0.603 for a classifier using the ichorCNA tumour fraction alone, which detected 0.058 of these cancers at 95% specificity. For cancers with an estimated fraction above 3% and up to 10%, the ichorCNA classifier reached 0.983, above the combined model (0.962) and copy number alone (0.926). The extracted UNITE tables give sensitivity at a fixed specificity only for the ichorCNA comparator; the fragmentomic models' values are in a sheet not yet extracted. Cohorts, feature implementations, classifiers and validation designs differ, so no value is comparable across sources.

Every number above is a `source_checked` result:
- DELFI: `amp-20261007-ctdna-fragmentomics-result` (evaluation origin `author_reported`).
- Hou Table 1: `...-result-hou2024-t1-fragment-length-open-chromatin-auroc`, `...-t1-end-motif-open-chromatin-auroc`, `...-t1-delfi-original-auroc`.
- Hou Table S3: `...-s3-end-motif-mathios-ind-auroc`, `...-s3-end-motif-mathios-ind-sens95`, `...-s3-fsd-mathios-ind-auroc`, `...-s3-fsd-mathios-ind-sens95`.
- UNITE, rounded to three decimals: `...-result-wang2026-{all,len,sd,cna,ct,sl}-tf-0-3pct-auroc`, `...-wang2026-ichorcna-tf-tf-0-3pct-auroc`, `...-wang2026-ichorcna-tf-tf-0-3pct-sen-95spe`, `...-wang2026-ichorcna-tf-tf-3-10pct-auroc`, `...-wang2026-all-tf-3-10pct-auroc`, `...-wang2026-cna-tf-3-10pct-auroc`.

The case counts come from Hou P24 and P44 and the DELFI dataset record. The summary claim's `result_ids` should be these 18 results plus `amp-20261007-ctdna-fragmentomics-result`. It names the author-reported sources (DELFI, UNITE, Hou's IFS), the independent one (Hou et al. for the other patterns), both cohort overlaps, and the truth-set limits: clinically identified case-control cohorts and ichorCNA-estimated strata. It makes no recommendation.

## Checks run

- In memory: the reviewed batch passes `recordSchema`, the vocabulary check (including the three new metric concepts), the attribute check and `validateRecords` against the 29,444 stored records.
- Simulation with the approved use-case changes: before pinning, `use-case-mapping-amp-20261007-issue15` is withheld ("pinned evidence changed since review (use-case-plasma-ctdna-fragmentomics)"). After pinning the ten new judgements and re-pinning issue15, all eleven derive as active.
- `npm run typecheck`: exit 0.
- `npm run records -- check`: 29,444 records match their provenance (the batch is not in the store).
- `npm test`: 498 of 499. The failure is `tests/omics-data.test.ts` "documents an explicit scope decision": it expects 106 scope-audit entries and finds 113. The seven extra entries are this pass's new lines in `data/omics/scope-audit.jsonl`, not a review change. The count needs updating when the batch is integrated.
- `npm run build` was not run: the batch is not in the store, and the build writes release files outside this review's scope.

## Remaining gaps

- The Hou Table S2 conflicts and the UNITE ichorCNA-TF fixed-specificity failures are unresolved at the source. Both are worth reporting to the authors.
- The per-cancer Table S2 sensitivities and all of Table S3 rest on a single table each. Nothing contradicts them, but the same file has two faulty blocks.
- STATS_xgb_all_feat (not extracted) holds the fixed-specificity sensitivities the use case most needs: for example, sensitivity at 95% specificity of 0.388 for length alone and 0.464 for all five features in the [0, 0.03] stratum. In that stratum it prints identical values at 98% and 99% for all 16 feature sets, so a follow-up extraction must first check those columns against RAW_xgb_all_feat. These figures are not results and are not cited above.
- UNITE held-out and unseen test results are in prose and figures only.
- Figures were not checked in either article.
- Not covered, as the collector recorded: CCGA multi-feature comparisons, Griffin, LIQUORICE, FinaleToolkit and DELFI developer papers, dilution series, prospective studies, and Curtis et al. 2025, which publishes per-sample data only.
