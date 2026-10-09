# RNA pathogen detection: independent review of the 2026-10-09 batch

Batch: `data/omics/use-case-coverage-rna-pathogen-20261009/` (1,177 records). Use case: `use-case-diagnostic-rna-pathogen-detection`.

Reviewer: a separate Claude review agent that did not extract the batch. No human review is claimed. Nothing was executed or reproduced. This is a check of transcription and judgement against the pinned sources.

## Verdict

- All six pinned artifacts re-download to their recorded SHA-256, and the three archived copies decompress to the same bytes.
- All 994 results match their cells. No value, printed form, locator, metric, unit, direction or configuration, protocol and dataset link was wrong.
- I replaced the two source-wide evidence concerns, on the de Vries and CAMI II supplements, with row-level disputes:
  - the "DIAMOND pipeline 3A" evaluation and its 15 results;
  - the two Bracken evaluations and their 4 results.
  The disputed evaluations are excluded from their judgements with reasons, so the clean ENNGS and CAMI II comparisons still show.
- The three Carbo species and genus judgements change from `direct` to `proxy`.
- All 7 judgements hold as `proxy`, with limitations corrected and extended. Each has `reviewed_evaluations` and is `source_checked`. Pins are left for the integrator.
- Every other record is `source_checked`, except the 3 disputed evaluations and 19 disputed results.
- The summary proposal has two numerical errors and some missing caveats. My corrected text is at the end.

Do not rerun `extract/extract_rna_pathogen.py` on this folder; it would overwrite these changes.

## How the check was done

1. Downloaded every `artifact_url` into an empty directory and hashed it.
2. Read the three workbooks with a stdlib OOXML reader written for this review; the extractor's script was not imported or run. For each result, the locator's cell was compared with the record:
   - text cells must equal `printed_value` exactly; numeric cells must equal the shortest round-trip decimal;
   - `numeric_value` must be null for text cells;
   - metric, unit and direction come from the column header;
   - the evaluation's `system`, `assessment` and `data` links must match the row label, block, sheet and column set.
3. 994 expected cells, 994 matched, none missing and none duplicated.
4. Arithmetic checks against each source's own numbers:
   - Carbo ROC distance against sensitivity and selectivity, all 60 rows;
   - de Vries Table S4: TP + FN = 15, TP + FP = total, PPV and hit-level sensitivity;
   - de Vries Table S2: sample-level sensitivity = correct / 13.
5. Read the three articles' Methods, Results and Discussion.
6. Dry run: `addBatch` into a scratch copy of the store, then `deriveUseCaseInputs` with the 7 proposed links added in memory.

## Sources and hashes

| Source ID | Artifact | SHA-256 (re-downloaded 2026-10-09T20:34Z) | Matches |
| --- | --- | --- | --- |
| `rna-pathogen-20261009-source-carbo2022` | PMC8953373 full-text XML | `e6683855ad278a555598295fdc4166e54ddb0e39e3d971878b898b20bc8ddf95` | Yes |
| `rna-pathogen-20261009-source-carbo2022-supp` | medRxiv 2022.01.21.22269647 v1 `media-1.xlsx` | `cd3a80d785b78377e79960d0280667f98cba3305d68426fdfaf8efeecd4542d7` | Yes |
| `rna-pathogen-20261009-source-devries2021` | medRxiv 2021.05.04.21256618 v1 JATS XML | `735ce2e42ae5fe6f5a198bdc14fd2e92ef27fc1d3734d2137a3c86d24480c718` | Yes |
| `rna-pathogen-20261009-source-devries2021-supp` | medRxiv 2021.05.04.21256618 v1 `media-1.xlsx` | `be0ea61fcffe8ea580077467ca19ef1ac39e88bbc82d916bc65b58a6683214f6` | Yes |
| `rna-pathogen-20261009-source-meyer2022` | PMC9007738 full-text XML | `2532db9c9abd1f040047afdcc859cb83739a9cceb4dbd998cd550017da9bd7ba` | Yes |
| `rna-pathogen-20261009-source-meyer2022-supp` | Springer `41592_2022_1431_MOESM3_ESM.xlsx` | `9a5ebd2364bb2660ea841227b9d04848b9c60b4d3c2a9f4939fc5994efc851ce` | Yes |

The three `artifacts/*.gz` files decompress to the Carbo article, CAMI II article and CAMI II workbook hashes above. I did not retry the published supplements that failed for the collector.

## Values checked

| Source table | Results | Mismatches |
| --- | --- | --- |
| Carbo Supplementary Table 1, species (cut-offs 0 and 10), genus, family; 12 blocks of 5 classifiers, 11 value columns | 660 | 0 |
| de Vries Supplementary Table 2 (14 rows of 15 read counts, plus 13 rows of 2 summary cells) | 236 | 0 |
| de Vries Supplementary Table 4 (13 rows, columns O to T) | 78 | 0 |
| Meyer Supplementary Table 39 (10 rows, 2 outcome columns) | 20 | 0 |
| Total | 994 | 0 |

`research.md` and `sources.md` say 720 Carbo results (12 value columns) and "210 + 78" for de Vries. The batch correctly holds 660 (11 value columns: Informedness through Taxa) and 236 + 78. These are counting slips in the notes, not missing data.

All 60 Carbo rows satisfy ROC distance = sqrt((1 - SN)^2 + (1 - SL)^2) within 0.0001, when each `10000` cell is read as 1.0000. All de Vries summary cells are arithmetically consistent with their own counts.

## The collector's points

| Point | Finding |
| --- | --- |
| Eight Carbo `10000` cells | Confirmed as printed: U33 and V33 (species cut-off 10, normalised, Genome Detective), E16, H16, E18, H18, E26, H26 (family). In every one of those rows, the printed ROC distance equals the value computed with 1.0000, for example Kaiju family 0.0534 from SN 1, SL 0.9466. This confirms the reading. An artefact note is enough: the values are not disputed, only their notation, and `numeric_value` stays null. I appended the ROC check to each `source_anomaly`. The judgements' "Four cells" limitation was wrong: the counts are 6 (family), 2 (species cut-off 10) and 0 (the other two). Corrected. |
| Informedness stored as `roc-distance` | Correct. Section 2.7 defines the column as "the ROC distance to the closest error-free point (0,1, informedness)", and the arithmetic holds in all 60 rows. It is not Youden's J. The claim and `source_label` keep the printed label. |
| de Vries 14 rows versus 13 pipelines, 80% versus 76.9% | Only one row and one Abstract figure are affected, so a source-wide hold is not warranted. Methods name 13 pipelines and say DAMIAN was run by two participants (A and B). Table S2 prints one DAMIAN row and a 14th row, "DIAMOND pipeline 3A (see table 1)", with read counts and no summary values; Tables S3 and S4 have 13 pipelines. I disputed that row's evaluation and 15 results, and excluded it from the sample-level judgement. The 80% appears only in the Abstract; Results print 77% (10/13) and Table S2 prints 76.92. It is a limitation on the article source and the judgements. The concern was removed. |
| CAMI II Bracken swap | Affects only the two Bracken rows. The text says Bracken v2.5 named CCHFV causal and Bracken v2.2 "correctly identified orthonairovirus" (a genus), so even the "in list" cells are uncertain for Bracken. I disputed both Bracken evaluations and their 4 results, and excluded them from the judgement. The counts of 4 listed and 3 causal are the same under either reading. The concern was removed. |
| Carbo species and genus `direct` | Changed to `proxy`. The original PCR panel as reference is not the issue, since the UCSF anchor uses the same kind of reference. The reasons are three: (1) sensitivity, selectivity, PPV and NPV are taken at the operating point chosen from the ROC over read-count cut-offs on the same 1144 results (columns marked "(ROC)", Section 2.7), so they are optimistic for a new cohort; (2) libraries were made with a protocol that processes RNA and DNA together (Section 2.2), not the DNase-treated RNA the use case's inputs describe; (3) the use case's own UCSF judgement is `proxy`. Family stays `proxy`. |
| Preprint versus published | Recorded in every affected judgement's limitations. The Carbo article is the published version, but its supplement is the medRxiv v1 workbook. de Vries is the preprint throughout, and the published J Clin Virol version was not retrieved. |
| ENNGS pipeline versions unextracted | Confirmed: Table 1 is an image in the preprint. `missing_metadata.version` reason `unextracted` with that note is right, and it is now a judgement limitation. |

Other checks:
- Carbo configuration versions match Table 2 and Section 2.6. Genome Detective is 1.126 in Table 2, and its database is 1.130 per Section 2.5.
- All 13 Carbo PCR targets are RNA viruses (Table 1).
- de Vries origins agree with Results: most pipelines were "developed or adapted at a local site", four are commercial, and DAMIAN and Centrifuge are public.
- CAMI II: the article says all ten submissions were manually curated; Table 39 marks eight as manually curated and the two NSSAC submissions "Not specified". This is now a limitation.
- The CAMI II Methods say CCHFV causality is the most plausible explanation, not clinically proven. This is now a limitation.

## Corrections made in the batch

None changes a value.

1. Source concerns on `...source-devries2021-supp` and `...source-meyer2022-supp` were removed. Their messages are kept in this review and in the receipt, and limitations were added to those sources and to `...source-devries2021` (the Abstract figure).
2. `...eval-devries2021-sample-diamond-pipeline-3a` and its 15 results were set to `disputed`, as were `...eval-meyer2022-bracken-v2-2`, `...eval-meyer2022-bracken-v2-5` and their 4 results. Each carries the reason. They are excluded from their judgements through `excluded_evaluations`.
3. Carbo species cut-off 0, species cut-off 10 and genus: `relevance` changed from direct to proxy, with a new rationale.
4. Judgement limitations:
   - Carbo: the 10000 counts, ROC-selected operating point, library preparation and preprint supplement.
   - de Vries: preprint, unextracted Table 1, dry-lab design, PPV definition and index hopping, the Abstract figure, read counts not comparable, DNA targets and specimen mix, and pipeline 3A.
   - CAMI II: CCHFV causality, modified case and replaced human reads, curation per Table 39, and the Bracken exclusion.
5. `...claim-devries2021-negative-control`: the value now attributes the fetal bovine serum explanation to BVDV only, as the source does. The source says RD114 and the leukemia viruses may be genuinely present. `claims.csv` was updated.
6. The eight `source_anomaly` notes record the ROC check.
7. `data/vocab/metric.ttl`, `negative-predictive-value`: added `skos:exactMatch` STATO_0000619 (see Vocabulary).

## Judgements

All 7 pass as `proxy`.

| Judgement | Reviewed evaluations | Excluded | Grouping |
| --- | --- | --- | --- |
| carbo2022-species-cutoff-0 | 15 | none | `carbo2022-respiratory`, stratum 1 |
| carbo2022-species-cutoff-10 | 15 | none | stratum 2 |
| carbo2022-genus-cutoff-0 | 15 | none | stratum 3 |
| carbo2022-family-cutoff-0 | 15 | none | stratum 4 |
| devries2021-sample-level | 13 | DIAMOND pipeline 3A | `devries2021-ennngs`, stratum 1, headline recall |
| devries2021-hit-level | 13 | none | stratum 2, headline precision |
| meyer2022-cami2-pathogen | 8 | Bracken v2.2, Bracken v2.5 | own group, headline success-rate |

Fit: the use case's question covers both detection and separating real detections from background. Carbo bears on both, since PPV shows the spurious calls. ENNGS hit-level and CAMI II bear on the second. The use case's `decision`, `inputs` and `output` still describe only the UCSF assay, so none of these endpoints matches the output exactly. That is what `proxy` covers. I recommend widening those fields in a reviewed change, with the UCSF judgement re-pinned in the same change.

Grouping:
- Carbo strata go species, species at cut-off 10, genus, family, with headline recall. Recall is acceptable but is the most cut-off-dependent column. AUC would be the threshold-free choice; I left the collector's headline.
- ENNGS: sample level then hit level, headlines recall and precision. Right.
- CAMI II: one stratum. Right.

Dry run, with the 7 links: all 7 are withheld only because pins are not yet recorded. The two ENNGS judgements have 13 eligible evaluations each, CAMI II has 8, and the UCSF judgement stays active.

## Scope: the non-respiratory exclusion

Approved exclusions text, replacing the second item:

> Non-respiratory specimen types, except in a comparison of several workflows on the same data that is recorded as proxy evidence and names its specimen types

The first item, the composite-PPA figure, is unchanged. I dropped the collector's parenthetical "(currently CSF, brain biopsy and plasma datasets in the ENNGS benchmark, and one blood metagenome in the CAMI II pathogen challenge)". `exclusions` is a pinned field, so a list of current evidence there would withhold every judgement whenever the evidence changes. The specimen types are already named in the ENNGS and CAMI II judgements' limitations and in the setting text.

Effect on the UCSF judgement (`use-case-mapping-amp-20261007-issue14`): its claim does not change. Its endpoint is respiratory specimens (103 of 110 against the original respiratory panel), the exception only admits proxy multi-workflow comparisons, and none of its fields refers to the exclusion. It must be re-pinned because `attributes.exclusions` is among its pinned fields.

## Vocabulary

| Concept | Check | Outcome |
| --- | --- | --- |
| `negative-predictive-value` | TN / (TN + FN). OLS4 STATO_0000619 "negative predictive value": "a proportion in which the numerator represents the correctly non-detected items within the denominator that represents all items not detected". Same meaning | Accepted; `skos:exactMatch` STATO_0000619 added, consistent with `specificity` (STATO_0000134) |
| `regression-slope`, `regression-intercept` | Descriptive coefficients of a linear fit; direction unknown is right (Carbo regresses Ct on read counts) | Accepted, unmapped |
| `roc-distance` | Euclidean distance from (1 - specificity, sensitivity) to (0, 1), lower is better. Reproduces all 60 Carbo rows | Accepted, unmapped |

## coverage.json

**`add_links`:** the 7 targets equal the judgement protocols. Correct.

**`setting_proposal`:** the numbers are right (103 of 110, 88 specimens, 1144 results, 13 laboratories and datasets, 10 submissions). Two edits: say that 5 of the 13 ENNGS datasets are respiratory, and bound the last sentence. Approved text:

> Published comparisons cover one assay's sensitivity against original clinical respiratory panel testing (UCSF SURPI+, 103 of 110), five classifiers on the same 88 respiratory specimens against a 1144-result PCR panel (Carbo et al. 2022), thirteen clinical virology laboratory pipelines on the same 13 clinical datasets, five of them respiratory (de Vries et al. 2021, preprint), and ten submissions on one blood metagenome in the CAMI II pathogen challenge (Meyer et al. 2022). None of the sources found in this bounded search compares workflows prospectively on a large cohort with an adjudicated composite reference standard.

**`evidence_gaps_add` (6):** accurate. Two notes:
- Gap 5 (Brinkmann) rests on the collector's reading, which I did not repeat.
- Gap 6 should end "was found in this pass".

**`summary_proposal`:** the numbers trace, except two.
1. "between 33% and 58%" should be 31% to 58%. One minus the highest PPV, 0.6875 (CLARK, human reads kept), is 31%.
2. "raised specificity for every classifier except CLARK" is wrong. Genome Detective's species-level values are identical with and without human reads (specificity 0.9857), so the change affected only Centrifuge, Kaiju and Kraken2.

It also omits several caveats: the ROC-selected operating point, the preprint status, that the two Bracken rows are disputed, and that 2 of the 10 CAMI II submissions are marked "Not specified" rather than manually curated. It does not mention the UCSF result.

## Final summary text

> The one single-assay result is a UCSF respiratory RNA metagenomic sequencing assay, reported by its developers, at 93.6% (103 of 110) sensitivity against original clinical respiratory panel testing. Three comparisons of several workflows add proxy evidence. On 88 nasal washings from COPD patients scored against 1144 respiratory virus PCR results, 24 of them positive (Carbo et al. 2022, values from the preprint supplement), all five classifiers detected 22 or 23 of the 24 PCR-positive results at species level (sensitivity 0.9167, or 0.9583 for Kaiju) at a read-count cut-off chosen from the ROC on the same data, but 31% to 58% of their positive calls were PCR-negative: species-level PPV was 0.42 to 0.69 with human reads kept and 0.52 to 0.67 after removing them. Removing human reads raised specificity for Centrifuge, Kaiju and Kraken2, left it unchanged for CLARK and Genome Detective, and lowered CLARK's sensitivity to 0.8333. When 13 European clinical virology laboratories each ran their own pipeline blind on the same 13 clinical datasets, five of them respiratory (de Vries et al. 2021, preprint), 10 to 13 of the 13 samples were correctly called positive; the three pipelines that found every sample (DNASTAR, FEVIR and MetaMix) reported 6, 2 and 0 additional viruses whose PCR was negative, giving hit-level PPV of 71.4%, 88.2% and 100%. Rotavirus, reported in one CSF sample by most pipelines, was also present in a negative run control that the participants never saw. In the CAMI II clinical pathogen challenge on one blood metagenome (Meyer et al. 2022), 4 of 10 submissions listed the causal virus, CCHFV, and 3 named it as causal; the supplementary table and the article text disagree on which Bracken version did which. None of this is clinical validation: the respiratory cohort has 24 positive results, the ENNGS panel mixes specimen types and includes DNA virus targets, each laboratory used its own database and reporting rules, and the CAMI II submissions were mostly manually curated and not reproducible.

Number trace:
- 93.6% and 103 of 110 come from `amp-20261007-rna-pathogens-result`; the evaluation is `author_reported`.
- 0.9167 and 0.9583 come from the species cut-off 0, human-reads-kept sensitivity results.
- 22 and 23 of 24 come from those values and the 24 positives in the dataset record.
- PPV 0.4151 to 0.6875 (kept) and 0.5227 to 0.6667 (removed). 31% to 58% is one minus the kept range.
- Specificity, kept against removed: Centrifuge 0.9596 to 0.9792, Kaiju 0.9583 to 0.9727, Kraken2 0.9635 to 0.9779, CLARK 0.9870 both, Genome Detective 0.9857 both.
- CLARK 0.8333 comes from the human-reads-removed sensitivity.
- ENNGS: correct-sample counts 10 to 13; DNAstar, FEVIR and MetaMix false-positive counts 6, 2 and 0 with PPV 71.43, 88.24 and 100. Rotavirus comes from the negative-control claim.
- CAMI II: the 20 Table 39 results, 4 of them disputed. The counts do not depend on the Bracken dispute.

## Remaining gaps

- Published supplements of Carbo et al. and the whole published de Vries et al. article were not retrieved; whether values differ from the preprint is unknown.
- Figures and image tables were not checked: de Vries Tables 1 and 2, and CAMI II Supplementary Fig. 16.
- Screened sources, including Brinkmann et al. 2019, were not re-read.
- Pins are not recorded; the integrator pins with this review.
- The use case's decision, inputs and output still describe only the UCSF assay.
