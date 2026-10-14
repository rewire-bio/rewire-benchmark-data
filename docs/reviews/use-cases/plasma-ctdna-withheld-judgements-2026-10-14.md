# Plasma ctDNA judgements withheld as changed evidence, 2026-10-14

Issue #126. Reviewer: a separate Claude review agent that did not extract these batches, write these judgements or carry out their earlier reviews. No human review is claimed.

Claims re-reviewed:

| Claim (prefix `use-case-mapping-`) | Use case | Reviewed evaluations | Results checked | Of which disputed |
| --- | --- | --- | --- | --- |
| `ctdna-fragmentomics-20261009-hou2024-cris` | fragmentomics | 10 | 240 | 20 |
| `ctdna-fragmentomics-20261009-hou2024-jiang` | fragmentomics | 10 | 30 | 20 |
| `ctdna-fragmentomics-20261009-wang2026-tf-0-3pct` | fragmentomics | 7 | 52 | 6 |
| `ctdna-fragmentomics-20261009-wang2026-tf-over-10pct` | fragmentomics | 7 | 52 | 9 |
| `ctdna-lit-20261011-zeng2026-frag-pe-validation` | fragmentomics | 5 | 10 | 1 |
| `ctdna-lit-20261011-zeng2026-meth-pe-validation` | methylation | 5 (the same five) | 10 | 1 |
| `ctdna-methylation-20261009-nguyen2023-too-discovery` | methylation | 3 | 90 | 24 |
| `ctdna-methylation-20261009-nguyen2023-too-validation` | methylation | 3 | 90 | 24 |

All eight judgements hold. No value, relevance grade, endpoint, limitation or excluded evaluation changes. `reviewed_evaluations` is unchanged and matches what was checked.

## What changed

Nothing in the evidence. The stored pins of all eight claims match the store, so `deriveUseCaseInputs` marks them active. They were withheld by the release build, with the reason "Referenced evidence changed since the recorded review", and had been in every release from 2026-10-12-f3dd882d8231, before PR #123 merged, to 2026-10-14-53895165fa97. The issue's reading (pin drift from the #123 batch) does not match this history.

Cause: each judgement has a reviewed evaluation with at least one `disputed` result. `deriveUseCaseInputs` computed the mapping's `evidence_sha256` over the whole store, disputed results included. `buildUseCaseArtifact` recomputes it over the release snapshot, which holds only public records (`publicRecords` drops disputed results). The two hashes can never agree, so the build always marked these mappings as changed. Six mappings on other use cases were withheld the same way (BRCA Cubuk 2021 BRCA1 and BRCA2, Franzoso 2025 WGS, Samarakoon 2025 total, Dieckhaus 2024 S669, Kaschta 2026 manual versus Talos).

Fix on this branch: `loadUseCases` passes the public records to `deriveUseCaseInputs`, which computes `evidence_sha256` over them. A test builds the artifact from the store and checks that no mapping is marked stale and that the Hou Cristiano judgement, which has disputed results, is active. Pins are unaffected: they already record each result's status, so a result that becomes disputed after review still withholds its judgement.

Re-pinning changes nothing for these claims, because their pins already match; `use-cases:repin` was run on them and reported no change.

## Sources

Re-downloaded on 2026-10-14; every SHA-256 matches its source record.

| Source record | Artifact | SHA-256 |
| --- | --- | --- |
| `ctdnafrag-20261009-source-hou2024` | Europe PMC PMC11321639 full-text XML | `d029fc9d...6ace70` |
| `ctdnafrag-20261009-source-hou2024-supporting-information` | `ADVS-11-2308243-s001.xlsx` | `41b24f7e...695fb0` |
| `ctdnafrag-20261009-source-wang2026` | Europe PMC PMC13353424 full-text XML | `61464a27...f6fb23` |
| `ctdnafrag-20261009-source-wang2026-data-file-s2` | `sciadv.ady9432_data_files_s1_and_s2.zip` | `d28e1dbf...efe12` |
| `ctdnalit-20261011-zeng2026-source-article` | Europe PMC PMC12948677 full-text XML | `72e82320...61e323` |
| `ctdnalit-20261011-zeng2026-source-source-data-fig4` | `43018_2026_1116_MOESM6_ESM.xlsx` | `fae75168...0163b4` |
| `ctdnameth-20261009-source-nguyen2023` | Europe PMC PMC10567114 full-text XML | `e09cfb58...09cfa8` |
| `ctdnameth-20261009-source-nguyen2023-supp-file-1` | `elife-89083-supp1.xlsx` | `4797d7ea...7b5331` |

None of these sources has an `evidence_concerns` entry.

## Method

- Read every result on the reviewed evaluations of the eight claims (564 distinct results; the two Zeng claims share five evaluations) and opened the cell its `source_locator` names, with openpyxl in a script written for this review. The extractor's and earlier reviewers' scripts were not run.
- Compared the cell with `printed_value` and `numeric_value`. For Hou et al. the cells hold "value (95 CI: lower - upper)"; the leading number and both interval bounds were compared with the stored value and `uncertainty`.
- Checked that every row label quoted in a locator (pattern, feature set, stratum, metric, method) is in the cited row.
- Re-checked each dispute against the source, and the stated reason for each excluded evaluation.
- Re-read each judgement's endpoint, relevance grade and limitations against the use case and the disputes.

## Values

| Source | Results | Outcome |
| --- | --- | --- |
| Hou et al. 2024, Supporting Information sheet S2 | 270 | All match, values and 95% intervals. Three cells differ only in layout: two have a leading space (`fsd-stad-sens85`, `fragment-end-count-nsclc-sens85`) and one lacks its closing bracket (`pfe-ov-sens85`, already noted on the record). |
| Wang et al. 2026, Data file S2 sheets `STATS_xgb_x1-x6` and `STATS_lr` | 104 | All match. |
| Zeng et al. 2026, Source Data Fig. 4 sheets `Fig.4c` and `Fig.4d` | 10 | All match. The combined ratio and methylation AUC (0.954), fragment-ratio AUC (0.848) and the 99%-specificity sensitivities (76.6% and 63.3%) also match Results P33. |
| Nguyen et al. 2023, Supplementary file 1 sheet `Table S9` | 180 | All match. |

## Disputes

All 104 disputed results are correctly disputed, and each judgement's limitations say why they are not shown.

- Hou, pan-cancer (20 results, `hou2024-cris`). The S2 pan-cancer column headed "Sensitivity @85% specificity" holds Table S9's SVM sensitivities at 95% specificity (fragment length 0.6033, PFE 0.8259, FSR 0.8091), so neither S2 pan-cancer sensitivity column can be taken at its label.
- Hou, liver (20 results, `hou2024-jiang`). S2 prints the same sensitivity at 95% and 85% specificity for nine of ten patterns; fragment length differs by 0.0009 (0.4631 and 0.4640).
- Wang, ichorCNA-TF comparator, 0 to 3% stratum (6 results). Accuracy and F1 at fixed specificity are inconsistent with the sensitivity printed at the same specificity: at 95%, the median F1 is 0 while the median sensitivity is 0.055, and the means (F1 0.057, sensitivity 0.058) imply precision near 0.056, which at 95% specificity would need about 20 healthy samples per cancer; the default-threshold row (sensitivity 0.58, specificity 0.57, PPV 0.69) implies about 0.6. At 98% and 99%, F1 is 0 in every fold (sd 0) while mean sensitivity is above 0. I did not recount the per-fold contradictions (27 of 50) the limitation cites; the aggregate rows are enough to support the dispute.
- Wang, ichorCNA-TF comparator, above 10% stratum (9 results). AUROC, sensitivity and specificity are 1 in every fold, yet sensitivity at 95%, 98% and 99% specificity is printed as 0.
- Zeng, methylation-only validation AUC (1 result, both Zeng claims). Source Data prints 0.694; Results P33 says 0.674.
- Nguyen, stage strata for breast and all cancers (48 results). The Table S9 stage counts differ from Table S8 for breast (discovery 29, 78, 25, 24 against 31, 84, 27, 14; validation 13, 20, 5, 29 against 14, 31, 8, 14) and so for all cancers. The other four cancer types agree.

Zeng excluded evaluations: the five validation classifiers that include 5' end motifs are excluded from both Zeng judgements. Results P33 says protocol-related differences in the HCC healthy controls' 5' motif baselines "reduced mAUCs and 99%-specificity sensitivities for motif-containing classifiers", and P32 that those 17 controls used a different laboratory protocol. The exclusion reason matches.

## Judgements

- Endpoints, relevance (`proxy` for all eight) and limitations still fit the use cases. Each limitation that describes a dispute matches what the source shows.
- No text change is needed. The rewire.it ctDNA reviews (rewire.it#398) cite UNITE and Nguyen values that are unchanged, and describe the disputed Hou Table S2 and Zeng values in words only, which matches the records.
- Each claim's `review` block now names this review.

## Remaining gaps

- The Wang per-fold contradiction count (27 of 50) was not recounted.
- No figures were read.
- No human scientific review; no reproduction.
