# Jamshidi et al. 2022 (CCGA substudy 1): independent review of the 2026-10-10 batch

Batch: `data/omics/use-case-coverage-ctdna-jamshidi-20261010/` (79 records). Use cases: `use-case-plasma-ctdna-methylation` and `use-case-plasma-ctdna-fragmentomics`.

Reviewer: a separate Claude review agent that did not extract the batch, and that reviewed the earlier ctDNA methylation batch to the same standard. No human review is claimed. Nothing was executed or reproduced. This review checks the transcription against the pinned source and judges the relevance claims.

## Outcome

- The figshare file re-downloads to the pinned SHA-256 and to figshare's MD5. It is the publisher PDF of the version of record.
- All 22 results match the source: 19 Table 3 cells and 3 cancer signal origin values from the Results.
  - Every percentage recomputes from its count to the printed rounding.
  - Every 95% interval recomputes exactly as a Clopper-Pearson interval.
  - All four observed specificities recompute.
  - No value, count, interval, metric, unit, direction or link was wrong.
- The 833 against 854 and 464 against 485 gap is explained by the source. Each set excludes its 21 plasma cell neoplasms and leukaemias, because detection was restricted to solid cancers. I replaced the "not explained" limitation everywhere.
- The post-unblinding issue is narrowed to rows:
  - Seven evaluations are excluded from the two methylation detection judgements: the fragment endpoint, fragment length, allelic imbalance and pan-feature classifiers.
  - The pan-feature classifier is excluded from the fragmentomics validation judgement.
  - Every remaining fragment row carries an explicit "not a blinded validation" limitation.
- The methylation validation judgement stays `direct`, restricted to the six classifiers analysed double-blinded. The methylation training judgement is regraded to `proxy`. The other three judgements hold as `proxy`.
- Seven footnote marks were moved out of `printed_value` into `printed_source_cell`.
- Simulation: I applied the use-case and summary changes below to an in-memory copy of the store and computed pins.
  - Methylation: all 11 judgements on the use case derive as active, and so does its summary.
  - Fragmentomics: all 13 judgements and the summary derive as active.

## How the check was done

1. Downloaded `https://ndownloader.figshare.com/files/38559380` into an empty directory. Checked its SHA-256, its MD5 against the figshare record, and its PDF metadata (title, Cancer Cell 40 (2022), Elsevier).
2. Read the text layer with `pdftotext -layout` and a parser written for this review. The extractor's script was not run.
3. Compared each Table 3 cell with its result:
   - printed value, interval and footnote mark;
   - numerator and denominator;
   - metric, qualifier, unit, direction;
   - configuration and protocol.
4. Recomputed every percentage from TP/total. Recomputed every interval with `scipy.stats.beta` as an exact two-sided 95% Clopper-Pearson interval, which STAR Methods name. Recomputed the four observed specificities from footnotes a and e, and the three origin accuracies from their counts.
5. Read STAR Methods on study design, blinding, classifier development, the solid-cancer restriction, the performance comparison and statistics. Read the Results on cancer signal origin and the Discussion on the targeted methylation test, to check every limitation and claim.
6. Loaded the reviewed batch against the current store in memory with `recordSchema`, `validateVocabularies`, `validateAttributes` and `validateRecords`. Then ran `deriveUseCaseInputs` with the approved changes and summaries for both use cases and computed pins. Nothing was written to the store.

This review gave no external service any personal identifier. The figshare download needs none, and I did not call Unpaywall.

The retrieval log says the collector called Unpaywall "with the required email parameter". An email address was sent with that call and has since been reported to the owner. No file in the batch records it.

## Source and hash

| Source | Pinned SHA-256 | Re-download |
| --- | --- | --- |
| `ctdnajam-20261010-source-jamshidi2022` (figshare 10.25418/crick.21731870.v1, file 38559380) | `5159294d...46d9a` | Match; MD5 `6f51c7dc523d231b6c0ce268257bd3b8` matches figshare |

The file is not archived in the batch, because the licence is CC BY-NC-ND 4.0. The source record says so.

## Values checked

| Classifier | Training printed (recomputed exact) | Validation printed (recomputed exact) |
| --- | --- | --- |
| WG methylation | 39% (36% to 43%), 328/833 (39.38; 36.04 to 42.79) | 34% (30% to 39%), 158/464 (34.05; 29.75 to 38.56) |
| SNV | 19% (16% to 22%), 159/833 | 16% (13% to 20%), 75/464, mark b |
| SNV-WBC | 36% (33% to 39%), 299/833 | 33% (29% to 38%), 155/464, unmarked |
| SCNA | 33% (29% to 36%), 271/833 | 27% (23% to 31%), 125/464, mark b |
| SCNA-WBC | 33% (30% to 37%), 278/833 | 30% (26% to 34%), 139/464, mark c |
| fragment endpoints | 22% (19% to 25%), 181/833 | 18% (15% to 22%), 84/464, mark b |
| fragment lengths | 28% (25% to 32%), 236/833 | 29% (25% to 34%), 136/464, mark c |
| allelic imbalance | 25% (22% to 28%), 210/833 | 22% (18% to 26%), 101/464, mark b |
| pan-feature | not reported | 36% (31% to 40%), 165/464, unmarked |
| clinical data | 2.7% (1.7% to 4.1%), 22/815 | 2.6% (1.4% to 4.5%), 12/457, mark b |

All 19 percentages and all 38 interval bounds match on recomputation. The footnote marks mean: b is p < 0.0001 and c is p < 0.01, both paired McNemar against WG methylation and computed only for validation.

The observed specificities match:
- 548/560 is 97.86%, printed 97.9%;
- 354/362 is 97.79%, printed 97.8%;
- 540/551 is 98.00%, printed 98.0%;
- 350/358 is 97.77%, printed 97.8%.

The origin accuracies are 95/127 (74.8%, printed 75%), 52/127 (40.9%, printed 41%) and 44/127 (34.6%, printed 35%). The McNemar values in the Results are p = 8 x 10^-9 (WG methylation against SCNA), p = 6.5 x 10^-12 (against SNV-WBC) and p = 0.35 (SCNA against SNV-WBC).

The three descriptive claims are correct:
- **cTAF:** cTAF was the only significant predictor of detection, and accounted for 72% of WG methylation score variance.
- **Observed specificity:** as listed above.
- **Targeted methylation clinical limit of detection:** 1.3 x 10^-4 cTAF at 98% specificity on 559 participants, and 3.1 x 10^-4 at 99.3% specificity. The claim correctly keeps it out of the results, because it is a different assay on different samples.

The one change to the results is that the batch kept the superscript footnote letters inside `printed_value` (for example `22%b` before the allelic imbalance interval). The seven marked cells now print as the value and interval, and the cell as read, with its letter, is kept in `printed_source_cell`. `claims.csv` is synced.

## The collector's points

- **Post hoc 98% threshold: direct or proxy?** STAR Methods: "A 98% specificity cutoff was determined post hoc for the training and validation sets."
  - **Validation stays `direct`**, but only for the six classifiers that STAR Methods say were analysed double-blinded: WG methylation, SNV, SNV-WBC, SCNA, SCNA-WBC and clinical data.
    - Those classifiers were locked before unblinding. The cutoff was then read off the validation non-cancer scores, which is how a sensitivity at a declared specificity is read from a locked classifier's ROC curve.
    - It differs from a threshold fixed in advance, so the specificity is near 98% by construction (97.8%). It is still the use case's declared endpoint, measured on a held-out set. The existing direct cfMethyl-Seq judgement measures the same kind of quantity.
    - The judgement's rationale now states this reasoning, and the threshold limitation stays on every record.
  - **Training is regraded to `proxy`.** It is 10-fold cross-validation within the set used to design the classifiers, with the same post hoc cutoff, and the same study's independent validation set gives the direct estimate for the same locked classifiers. That is the difference from the cfMethyl-Seq judgement, which has no separate validation set. The training row stays useful context: WG methylation fell from 39% to 34% between training and validation.
- **Classifiers developed after unblinding.** STAR Methods: "The fragment endpoint, fragment length, allelic imbalance, and pan-feature cancer signal detection classifiers, as well as the CSO classifiers were developed after blinding was lifted."
  - **Methylation validation (direct):** these four evaluations are excluded with reasons, so no post-unblinding value appears as blinded validation evidence on the methylation page.
  - **Methylation training (proxy):** the three with training values are excluded for the same reason.
  - **Fragmentomics training and validation (proxy):** the fragment classifiers are the subject, so they stay. The pan-feature classifier is excluded from the validation judgement, because it combines all nine cfDNA scores, including methylation and mutation, so it is not a fragmentomics workflow.
  - **Fragment rows in both fragmentomics judgements:** every one carries a limitation saying its validation value is not a blinded validation, even though the source calls the cohort held-out. The validation stratum is now labelled "Validation set (fragment classifiers developed after unblinding)".
  - **Origin classifiers:** the cancer signal origin judgement already says they were developed after unblinding.
- **833/464 against 854/485.** Explained by the source, not an unexplained gap:
  - STAR Methods restrict initial detection "to solid cancers, which were not expected to have circulating cancer background as a potential component of the WBC fraction".
  - Table 1 footnote a lists 11 plasma cell neoplasms and 10 leukaemias in training (21; 854 minus 21 is 833) and 8 and 13 in validation (21; 485 minus 21 is 464). Lymphomas stay in.
  - The origin classifiers "were later rerun with the previously restricted hematologic cancers". So the 127-cancer origin set can include them, as the dataset record already says.
  - I replaced the limitation on both detection protocols and all five judgements, added the explanation to both dataset populations, and noted the rerun on the origin dataset and judgement.
- **Origin-set definitions and "other".** Both confirmed.
  - The Results evaluate on cancers "jointly detected by all three corresponding cancer signal detection classifiers", where the three origin classifiers are WG methylation, SCNA and SNV-WBC. The STAR Methods give the detecting triple as WG methylation, SNV and SCNA-WBC.
  - The label "other" groups anus, unknown primary, melanoma, stomach, thyroid and uterus cancers, and "was counted as a correct result".
  - Both affect every row of the origin protocol equally. They are already limitations on the protocol, dataset and judgement, so they cannot be narrowed further. The judgement stays `proxy`.
  - No value depends on the contradictory sentence, so this is not a source concern.
- **Origin `author_reported` on all rows.** Correct, including the clinical data classifier, which GRAIL also built. The declaration of interests lists most authors as GRAIL employees with Illumina equity. Every evaluation and judgement says the study is developer-run.

## Judgements

| Judgement | Use case | Grade | Reviewed | Excluded |
| --- | --- | --- | --- | --- |
| `...-meth-validation` | methylation | direct | 6 double-blinded classifiers | 4 post-unblinding |
| `...-meth-training-cv` | methylation | proxy (was direct) | 6 | 3 post-unblinding |
| `...-meth-cso` | methylation | proxy | 3 | 0 |
| `...-frag-training-cv` | fragmentomics | proxy | 9 | 0 |
| `...-frag-validation` | fragmentomics | proxy | 9 | 1 (pan-feature) |

- **Fragmentomics grading.** Both fragmentomics judgements are proxy for reasons the collector gave and I agree with. The use case asks about low tumour fractions, and the per-classifier limits of detection by tumour allele fraction are in figures only. On top of that, the fragment classifiers were developed after unblinding.
- **Comparators.** On both use cases, the copy-number, mutation and clinical rows stay as same-participant comparators. They answer whether the use case's workflow beats other cfDNA features on the same blood draws, which bears on the workflow choice.
- **Comparison titles.** Both now read "cfDNA classifiers on the same participants at a post hoc 98% specificity", in place of "ten cfDNA classifiers", which no longer held after the exclusions.

## Approved use-case changes

### `use-case-plasma-ctdna-methylation`

**`links`:** add `assessed_by` links to these three protocols, keeping the eight existing links:
- `ctdnajam-20261010-protocol-ccga1-training-cv-sens-98spec`
- `ctdnajam-20261010-protocol-ccga1-validation-sens-98spec`
- `ctdnajam-20261010-protocol-ccga1-validation-cso-accuracy`

**`source_ids` and `citation_locators`:** add `ctdnajam-20261010-source-jamshidi2022`, which is clean and hash-verified, with:

```json
{"source_id": "ctdnajam-20261010-source-jamshidi2022", "locator": "Table 3 and footnotes; Results, cancer signal origin prediction; STAR Methods, performance comparison and statistical analysis"}
```

**`evidence_gaps`:** replace "No sensitivity at a declared specificity for several methods on the same plasma samples was found in a retrievable source; Jamshidi et al. 2022 (Cancer Cell, 10.1016/j.ccell.2022.10.022) could not be retrieved." with:

```json
"The only same-participant comparison at a declared specificity (Jamshidi et al. 2022) is developer-run on prototype assays in a case-control set, with the 98% specificity threshold set post hoc within each set; four of its classifiers, including the pan-feature classifier, were developed after validation unblinding and are not shown here."
```

Then append:

```json
"Jamshidi et al. 2022 tissue-of-origin accuracy is scored on 127 cancers detected by all three classifiers, comes from origin classifiers developed after unblinding, and counts 'other' as correct for six cancer types; the Results and Methods name different classifier triples for that set."
```

Keep "No independent methylation-only tissue-of-origin comparison on patient plasma with printed per-method values was found." It is still true, because Jamshidi et al. is the developer, not an independent group.

**`exclusions`:** replace the whole list with the following. This narrows the second exclusion: Jamshidi et al. add a methylation-only origin classifier, so "methylation alone" is no longer missing, but no ingested origin result classifies people without cancer.

```json
[
  "Prospective screening validation",
  "Tissue-of-origin identification as a screening result: the ingested tissue-of-origin results classify cancer patients only, and Jamshidi et al. 2022 only cancers already detected by three classifiers, so origin calls in people without cancer are not measured"
]
```

**`decision`:** this also needs to change, because it lists the evidence to inspect:

```json
"Inspect the cfMethyl-Seq repeated-split sensitivity/specificity evidence, the same-participant comparison of whole-genome methylation with other cfDNA classifiers at a post hoc 98% specificity (CCGA substudy 1), and the proxy comparisons of deconvolution methods and tissue-of-origin classifiers, before selecting a workflow and validation design for the intended cancer-detection population."
```

**`setting`:** the first sentence is unchanged; the second gains the CCGA comparison:

```json
"cfMethyl-Seq achieves 80.7% all-stage cancer-detection sensitivity (95% CI 68.6-90.7) at 97.9% specificity, under a repeated random 25% test split (cohort 217 cancers/191 non-cancers, test n=102). The other evidence is a developer comparison of a whole-genome bisulfite methylation classifier with mutation, copy-number, fragment and clinical classifiers on the same CCGA substudy 1 participants, an independent benchmark of five deconvolution methods on two plasma cohorts, a preprint benchmark of ten deconvolution tools on in silico mixtures, and one author-reported tissue-of-origin comparison on cancer patients recruited in Vietnam."
```

**`clinical_scope`:** this must change, because it says "the other comparisons are proxies", which is false once a direct CCGA judgement is linked:

```json
"Clinical applicability is not established as prospective screening performance. The cfMethyl-Seq figure comes from a repeated random test split on one assembled cohort, and the CCGA substudy 1 figures from a developer case-control validation set with a post hoc 98% specificity threshold; the other comparisons are proxies (a random forest AUC with no stated validation split, in silico mixtures, and tissue of origin among cancer patients only), and none is an independent prospective validation."
```

**Existing methylation judgements.** All eight hold under the new text:
- `use-case-mapping-amp-20261007-issue16`, the direct cfMethyl-Seq judgement. Its endpoint is unchanged, its figures stay word for word in `setting`, `decision` still names it first, and `clinical_scope` keeps its caveat.
- The three Giuili et al. 2025 judgements.
- The two Sun et al. 2024 judgements.
- The two Nguyen et al. 2023 judgements. They classify cancer patients only, which the new exclusion states, and their rationale does not rely on the removed "only tissue-of-origin comparison ingested" wording.

`decision`, `setting`, `exclusions` and `clinical_scope` are pinned, so all eight, and the reviewed summary, are withheld until re-pinned. In the simulation the only changed pin was the use case's. Re-pin all eight with the three new judgements and the updated summary.

### `use-case-plasma-ctdna-fragmentomics`

**`links`:** add `assessed_by` links to these two protocols, keeping the eleven existing links:
- `ctdnajam-20261010-protocol-ccga1-training-cv-sens-98spec`
- `ctdnajam-20261010-protocol-ccga1-validation-sens-98spec`

**`source_ids` and `citation_locators`:** add `ctdnajam-20261010-source-jamshidi2022` with:

```json
{"source_id": "ctdnajam-20261010-source-jamshidi2022", "locator": "Table 3 and footnotes; STAR Methods, WGS fragment classifiers and performance comparison"}
```

**`evidence_gaps`:** append:

```json
"Jamshidi et al. 2022 fragment endpoint, fragment length and allelic imbalance classifiers were developed after validation blinding was lifted, so their validation values are not a blinded validation; their clinical limits of detection by tumour allele fraction are in figures only."
```

**`clinical_scope`:** this must change, because it says every result comes from "small independent validations (8 to 129 cancers)", and the CCGA validation set has 464:

```json
"Clinical applicability is not established. Every result comes from a retrospective case-control cohort, with internal cross-validation, small independent validations (8 to 129 cancers) or one developer validation set (464 cancers) on which the fragment classifiers were developed after unblinding, not from a prospective screening trial. The clinically identified cancers and healthy comparators differ from an intended screening population, and tumour fractions are ichorCNA estimates, not measured values."
```

**`output`:** this also changes, for the same reason:

```json
"Sourced AUC and sensitivity-at-fixed-specificity figures for fragmentomic workflows from internal cross-validation, independent validations and one developer same-participant comparison, and AUCs within ichorCNA tumour-fraction strata from one developer study; no prospective screening-validation claim."
```

**`setting`:** append one sentence to the existing text:

```json
" Jamshidi et al. 2022 (CCGA substudy 1) scored fragment endpoint and fragment length classifiers from 30x cfDNA whole-genome sequencing against methylation, copy-number and mutation classifiers on the same participants at a post hoc 98% specificity."
```

**`exclusions`, `decision`, `inputs`:** unchanged. No fragmentomics exclusion concerns tissue of origin.

**Existing fragmentomics judgements.** All eleven hold under the new text:
- `use-case-mapping-amp-20261007-issue15`, the DELFI judgement;
- the six Hou et al. 2024 judgements;
- the four Wang et al. 2026 judgements.

Their endpoints are unaffected. `clinical_scope` keeps their "8 to 129 cancers" description. `output` keeps cross-validation, independent validations and ichorCNA strata. `setting` keeps every sentence about them. `output`, `setting` and `clinical_scope` are pinned, so all eleven, and the reviewed summary, are withheld until re-pinned. In the simulation the only changed pin was the use case's. Re-pin all eleven with the two new judgements and the updated summary.

## Final summary texts

Both use cases already have reviewed summaries. Adding new reviewed judgements changes each summary's pins, so both summaries must be updated and re-pinned with these exact texts. Add `ctdnajam-20261010-source-jamshidi2022` to each summary claim's `source_ids`, and append to each `source_locator`: "; ctdnajam-20261010-source-jamshidi2022: Table 3 validation column and Results, cancer signal origin prediction".

### `use-case-summary-plasma-ctdna-methylation`

> Four bounded sources compare cfDNA methylation methods. None is a prospective screening study and none measures clinical benefit. Jamshidi et al. 2022 (Cancer Cell), by the GRAIL developers, compared prototype cfDNA classifiers on the same CCGA substudy 1 participants at a 98% specificity threshold set post hoc within each set. On the validation set of 464 cancers and 362 non-cancers, analysed double-blinded, the whole-genome bisulfite methylation classifier detected 34% of cancers (95% CI 30% to 39%; 158 of 464), against 33% for variants with white-blood-cell correction, 30% for copy number with that correction, 27% for copy number, 16% for uncorrected variants and 2.6% for clinical risk factors alone; only the gap to the corrected variant classifier was not marked as significant. Among 127 validation cancers detected by all three representative classifiers, a methylation origin classifier developed after unblinding assigned the correct tissue for 75% (95 of 127), against 41% for copy number and 35% for corrected variants, with 'other' counted as correct for six cancer types. These are case-control results from the assay developer, not screening performance. Sun et al. 2024 (Genome Biology), an independent benchmark whose authors did not develop the tools, deconvolved real plasma with five methods and reported the ROC-AUC of a random forest trained on the estimated cell-type fractions; the paper does not state how the random forest was validated, so the AUCs may be in-sample. For 24 liver cancer patients and 32 healthy individuals (WGBS), AUCs were 0.96 (CelFEER), 0.93 (CelFiE), 0.91 (MethAtlas), 0.77 (cfNOMe) and 0.72 (UXM). On cfMethyl-Seq plasma (30 to 67 patients per cancer type, each against the same 193 healthy individuals), AUCs ranged from 0.72 (UXM, lung squamous cell carcinoma) to 0.93 (CelFiE, gastric cancer), and no method was highest for every cancer type. Giuili et al. 2025, a bioRxiv preprint not yet peer reviewed, ran ten reference-based tools inside the authors' DecoNFlow pipeline on in silico mixtures of tumour tissue or cell-line reads in healthy plasma reads. CelFiE had the lowest overall median tumour-fraction limit of detection in each dataset: 0.0070 (WGBS-TT), 0.0100 (RRBS-TT) and 0.0010 (RRBS-CL). CIBERSORT and EpiDISH had overall medians of 0.1000 to 0.2500 on WGBS-TT and RRBS-TT. For five tools the RRBS-CL values disagree between the supplementary table and Figure 4A and are not shown. Nguyen et al. 2023 (eLife), by the developers of the SPOT-MAS assay at Gene Solutions, compared three tissue-of-origin classifiers on combined methylation, fragment-length, copy-number and end-motif features from cancer patients only. In the validation cohort of 239 patients, overall accuracy was 0.53 (random forest), 0.69 (deep neural network) and 0.69 (graph convolutional network); the graph network was trained with the validation samples in its graph. Tissue-of-origin evidence here comes from two developer studies, one methylation-only classifier scored on already detected cancers and one multimodal workflow, and neither classifies people without cancer.

Where the new numbers come from:
- **Table 3 validation column:** WG methylation 34% with its interval and 158/464; SNV-WBC 33%; SCNA-WBC 30%; SCNA 27%; SNV 16%; clinical data 2.6%; the significance marks; and the 464 and 362 denominators.
- **Results:** the origin values 75% (95/127), 41% and 35%.
- **STAR Methods:** the "other" rule and the post-unblinding development.
- **Unchanged:** the rest of the text is the reviewed 2026-10-09 summary. The only other edits are the opening count ("Four" for "Three") and the closing sentence, which was no longer true once a methylation-only origin classifier is linked.

### `use-case-summary-plasma-ctdna-fragmentomics`

> Four sources compare plasma cfDNA fragmentomic workflows on retrospective case-control cohorts. None is a prospective screening study and none measures clinical benefit. Cristiano et al. 2019, the DELFI developers, report 73% sensitivity (152 of 208 cancers) at a reported 98% specificity for DELFI in repeated cross-validation against 215 healthy individuals. Hou et al. 2024 re-implemented ten published fragmentation patterns and DELFI with one support vector machine each on the same cohort. They are independent of every pattern except IFS, which their corresponding author developed. In 10 x 10-fold cross-validation, pan-cancer AUC within open chromatin regions ranged from 0.8741 (fragment length) to 0.9736 (5' end motif), and their DELFI re-implementation reached 0.9575. Rankings changed on independent cohorts. On 46 lung cancers and 385 healthy individuals, with a model trained on 12 lung cancers, the end-motif model fell to AUC 0.5355 and sensitivity 0.0652 at 95% specificity, while fragment size distribution reached 0.9386 and 0.7174. Hou et al.'s supplementary pan-cancer and liver cancer sensitivities conflict with other tables of the same file and are not shown. Wang et al. 2026, the UNITE developers, stratified cancers by ichorCNA tumour fraction in pooled public and new 0.1x data that include samples of the DELFI and Jiang et al. cohorts used above. For cancers with an estimated tumour fraction of 3% or less, cross-validated AUC was 0.878 for all five features combined, 0.873 for fragment length, 0.857 for the SD of length counts, 0.736 for copy number, 0.715 for the C/T end-motif ratio and 0.651 for the short/long ratio, against 0.603 for a classifier using the ichorCNA tumour fraction alone, which detected 0.058 of these cancers at 95% specificity. For cancers with an estimated fraction above 3% and up to 10%, the ichorCNA classifier reached 0.983, above the combined model (0.962) and copy number alone (0.926). The extracted UNITE tables give sensitivity at a fixed specificity only for the ichorCNA comparator; the fragmentomic models' values are in a sheet not yet extracted. Jamshidi et al. 2022 (Cancer Cell), by the GRAIL developers, scored fragment length and fragment endpoint classifiers from 30x cfDNA whole-genome sequencing on the same CCGA substudy 1 participants as their methylation, copy-number and variant classifiers, at a 98% specificity threshold set post hoc within each set. On the validation set of 464 cancers and 362 non-cancers the fragment length classifier detected 29% (95% CI 25% to 34%) and the fragment endpoint classifier 18% (15% to 22%), against 34% for whole-genome methylation analysed double-blinded; both fragment classifiers were developed after the validation set had been unblinded, so these are not blinded validation results, and no tumour-fraction-stratified sensitivity is printed. Cohorts, feature implementations, classifiers and validation designs differ, so no value is comparable across sources.

Where the new numbers come from:
- **Table 3 validation column:** fragment lengths 29% with its interval, fragment endpoints 18% with its interval, WG methylation 34%, and the 464 and 362 denominators.
- **STAR Methods:** the 30x depth.
- **Unchanged:** the rest of the text is the reviewed fragmentomics summary. The only other edit is the opening sentence, which no longer says "shared" cohorts: CCGA shares no samples with the other fragmentomics sources.

## Checks run

- In memory: the reviewed batch (79 records) passes the schema, vocabulary, attribute and record checks against the current store.
- `npm run typecheck`: exit 0.
- `npm run records -- check`: 42,481 records match their provenance (the batch is not in the store).
- `npm test`: 500 of 500 pass.
- `npm run build`: not run. The batch is not in the store, and the build writes release files outside this review's scope.

## Remaining gaps

- The per-classifier clinical limits of detection, stage-stratified sensitivity, origin accuracy on each classifier's own detected set, and the Table S2 partial AUCs are in figures or the supplement only, and were not extracted.
- The sequencing data are not public, so no value can be reproduced.
