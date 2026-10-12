# Review: plasma ctDNA fragmentomics and methylation batches, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-ctdna`, separate from the extracting agent `uc-ctdna`. No human review is claimed. Nothing was executed or reproduced. I did not edit any record, store file or batch file; every correction below is for the collector to apply in the batch folders before `records -- add`.

Worktree reviewed: `rewire-benchmark-data-lit-uc-ctdna` (branch `claude/lit-20261011-uc-ctdna`), batch folders as the source of truth. Store compared: `origin/main` at `bba147c` (release 2026-10-12-a3dac44c7353).

## Verdicts

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-ctdna-zeng2026-20261011` | Approved with corrections (Z1 to Z6) |
| `use-case-coverage-ctdna-helzer2025-20261011` | Approved with corrections (H1 to H4) |
| `use-case-coverage-ctdna-fragmentia2026-20261011` | Approved with corrections (F1 to F3) |
| `use-case-coverage-ctdna-fragmentiawgs2026-20261011` | Approved with corrections (W1 to W5) |
| `use-case-coverage-ctdna-cpgpt2026-20261011` | Approved with corrections (C1 to C2) |
| Summary proposals for both use cases | Approved with the corrected text in "Approved summary text" |
| Use-case field changes | Only `evidence_gaps` changes approved (U1, U2); no pinned field changes |

All 906 printed values match the pinned sources. No value needs a superseding record. The corrections are to one source-level concern that would hide the whole Zeng batch from the use-case pages, origin on 18 evaluations, relevance on one judgement, exclusions on two judgements, one block label, two dataset counts, and descriptive text.

## Corrections

Apply to records in the batch folders, then regenerate `claims.csv` and `coverage.json` as the extraction scripts do.

### All batches

A1. Delete `extract/__pycache__/` in all five batch folders before the review receipt is written; compiled bytecode should not be hashed into `review.json` or committed.

A2. Locators of the form `Results P32`, `Methods P59` count `<p>` elements of the JATS XML from zero in document order, front matter included (checked: Zeng `P32` is the paragraph beginning "We next assessed the generalization", Helzer `P12` begins "In the UW cohort, we found that the FoundationOne Liquid CDx panel", Fragmentia-AI WGS `P19` begins "We then assessed the generalizability"). The convention is stated nowhere. In the four JATS source records (`ctdnalit-20261011-zeng2026-source-article`, `ctdnalit-20261011-helzer2025-source-article`, `ctdnalit-20261011-fragmentia2026-source-article`, `ctdnalit-20261011-fragmentiawgs2026-source-article`) replace `attributes.source_locator`

`Full artifact bytes; per-record locators on each record`

with

`Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> element in document order in this JATS XML, front matter included.`

### Zeng et al. 2026

Z1. The source-level evidence concern would withhold every Zeng judgement. `cleanSource` in `shared/omics/use-cases.ts` rejects any source with a non-empty `evidence_concerns`, and every Zeng protocol, configuration, dataset and result cites `ctdnalit-20261011-zeng2026-source-source-data-fig4`. Follow the Hou et al. 2024 precedent (result-level dispute) instead:
- In `ctdnalit-20261011-zeng2026-source-source-data-fig4`, delete `attributes.evidence_concerns`.
- In `ctdnalit-20261011-zeng2026-result-pe-validation-methylation-auroc`, set `status` to `disputed`, add `attributes.source_warnings` = `["Source Data Fig. 4 sheet Fig.4c cell B6 prints a mean AUC of 0.69415032679738597 for the methylation-only classifier in the PE validation dataset; Results P32 of the article prints 0.674 for the same quantity. The other validation AUCs quoted in the text (0.954, 0.848) match the sheet. Which figure is right cannot be told from the source. The value is kept as printed and does not support comparison (independent review 2026-10-12)."]`, and replace `attributes.source_discrepancy` with `Results P32 prints 0.674 for this value; the sheet prints 0.69415032679738597. See source_warnings.`
- Update `sources.md` ("Evidence concern recorded on ..." paragraph), `retrieval-log.md` line 17 and `coverage.json` `remaining_gaps` item 4 to say the conflict is recorded as a disputed result with a source warning, not as a source evidence concern.
The evaluation `ctdnalit-20261011-zeng2026-eval-pe-validation-methylation` stays eligible through its sensitivity result.

Z2. Exclude the five classifiers that include end motifs from both PE validation judgements. The authors attribute their validation scores to a protocol difference in the healthy controls (Results P32: "Differences in 5' motif baselines for the HCC healthy controls ... reduced mAUCs and 99%-specificity sensitivities for motif-containing classifiers"), so those values measure a pre-analytical batch effect rather than the classifiers; three of them are below AUC 0.5 (0.066, 0.188, 0.455). In `use-case-mapping-ctdna-lit-20261011-zeng2026-meth-pe-validation` and `use-case-mapping-ctdna-lit-20261011-zeng2026-frag-pe-validation` add

`"excluded_evaluations": [{"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-end-motifs", "reason": "Includes 5' end motifs; the authors attribute motif-containing classifiers' validation scores to a laboratory-protocol difference in the HCC-study healthy controls (Results P32), so the values reflect that batch effect, not the classifier."}, {"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-motif-methylation-1pct", "reason": <same text>}, {"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-motif-methylation-ratios-1pct", "reason": <same text>}, {"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-all-features-1pct", "reason": <same text>}, {"id": "ctdnalit-20261011-zeng2026-eval-pe-validation-all-features-5pct", "reason": <same text>}]`

(`<same text>` is the first reason string, repeated.) The results and their `source_anomaly` notes stay as they are. Also correct the report, which says two validation AUCs are below 0.5; it is three (all-features-1pct 0.455 as well), and all three carry `source_anomaly` already.

Z3. Sensitivity at 99% specificity is read on very few healthy controls, which none of the records says. Append one string to `attributes.limitations`:
- `ctdnalit-20261011-zeng2026-protocol-pe-primary-cv`, and judgements `...-meth-pe-primary-cv` and `...-frag-pe-primary-cv`: `Sensitivity at 99% specificity is read within each outer fold, which holds six or seven of the 64 healthy donors, so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic).`
- `ctdnalit-20261011-zeng2026-protocol-pe-validation`, and judgements `...-meth-pe-validation` and `...-frag-pe-validation`: `The validation set has 17 healthy controls (Results P28 and P32), so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic).`
- `ctdnalit-20261011-zeng2026-protocol-se-primary-cv` and judgement `...-meth-se-primary-cv`: `Sensitivity at 99% specificity is read within each outer fold, which holds seven or eight of the 76 healthy donors, so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic).`
- `ctdnalit-20261011-zeng2026-protocol-se-validation` and judgement `...-meth-se-validation`: `The hold-out set has 9 healthy controls, so a 99% specificity threshold allows no false positive among them (counts from the source; the resolution is Rewire arithmetic).`
(Judgement IDs abbreviated; full prefix `use-case-mapping-ctdna-lit-20261011-zeng2026-`.)

Z4. The spread note is accurate but incomplete: Methods P61 says "error bars denote across-fold s.d.", the Figure 4 legend says s.e. for panels b, d, f and h, and Results P29 and P33 quote the sd_sens99 values as "± ... across folds". Keep `unresolved_spread`; in each sensitivity result's `uncertainty.note` append ` Methods P61 says error bars denote across-fold s.d.`

Z5. Keep `proxy` for the four methylation judgements (question 2). The 99% specificity is read on 6 to 17 healthy controls (Z3), the sensitivities count Li-Fraumeni carriers without cancer as cancers, and the developer ran every arm, so this is not the use case's declared-specificity endpoint in the way the CCGA validation is.

Z6. In `research.md` or the report, no change needed for the validation-size conflict (95 in Results P28, n = 140 in the Extended Data Fig. 9f legend); it is recorded on the dataset and protocol. Confirmed against the source.

### Helzer et al. 2025

H1. The UW commercial block is printed `Foundation One CDx` in Supplementary Table S2 (rendered page 9 checked), not `FoundationOne Liquid CDx`; the article text (Results P11 to P12) names the subset FoundationOne Liquid CDx for both cohorts, so the label in the table looks like a slip, but locators must quote what is printed. In every record of the batch and in `claims.csv`, replace the string

`Supplementary Table S2 (PDF caption), block 'FoundationOne Liquid CDx'`

with

`Supplementary Table S2 (PDF caption), block 'Foundation One CDx' (printed label; the article names this subset FoundationOne Liquid CDx)`

(131 results and the `version` of `ctdnalit-20261011-helzer2025-protocol-uw-foundationone`). Leave the Table S1 locators and all qualifiers unchanged. Append to `attributes.limitations` of `ctdnalit-20261011-helzer2025-protocol-uw-foundationone`: `Supplementary Table S2 prints this block as 'Foundation One CDx'; the article text (Results P11-P12) names the subset FoundationOne Liquid CDx (309 genes; 77% of them available on the UW panel).`

H2. The limitation `One-vs-rest AUROCs come from one multinomial model per metric; the 'Normal' column is the healthy-versus-all-cancer AUROC.` states more than the source. Methods P23 says GLMnet multinomial regression "was used for cancer type and cancer vs. healthy predictions" and does not say whether the Normal column comes from the multinomial model or a separate binary model. In all eight protocols and both judgements replace it with

`Methods P23 names GLMnet multinomial logistic regression for cancer-type and cancer-vs-healthy predictions; whether the 'Normal' (healthy vs all cancers) AUROC comes from the multinomial model or a separate binary model is not stated.`

Also append to the same `limitations` arrays: `The Figure 4 and 5 legends call the plotted value the average AUROC of 25 repeats; the table captions and Methods P23 say median. Values here follow the tables.`

H3. Judgement endpoints miscount the metrics (12 metrics plus All Combined in GRAIL; plus Griffin in UW). In `use-case-mapping-ctdna-lit-20261011-helzer2025-grail-full` replace `for 13 fragmentomic metrics` with `for 12 fragmentomic metrics and their combination`; in `use-case-mapping-ctdna-lit-20261011-helzer2025-uw-full` replace `for 14 fragmentomic metrics` with `for 12 fragmentomic metrics, their combination and Griffin`. In both rationales replace `Compares many published fragmentomic metric classes` with `Compares many fragmentomic metric classes, adapted to exon panels by the authors,`.

H4. Origin split confirmed (question 3): E1 SE is the authors' 2023 panel metric (Results P1 and P3: "We recently reported ... the entropy of fragmentation sizes at the exon nearest to a gene's transcription start site"), All Exons SE extends it and All Combined is the authors' model, so `author_reported`; the other metrics are re-implementations of other groups' WGS metrics and Griffin (Doebley, Ha et al.; no author overlap with the 27 Helzer authors), so `independent_paper`, consistent with the stored Hou et al. 2024 evaluations. The commercial-panel subsets (question 3) should not be mapped: they answer a different question (which genes a commercial panel retains) and the full-panel judgements already cover the comparison. Leave them as stored results without `assessed_by` links.

### Fragmentia-AI (Cell Reports Medicine 2026)

F1. Origin on the 18 baseline evaluations is wrong. The origin vocabulary defines `author_reported` as "reported by the authors of the evaluated method". Geneseeq did not develop DELFI, Griffin, FRAGMA, FDI or the nucleosome features; they re-implemented them (Results P44: "we implemented the feature extraction pipelines for each method"). The store records competitor baselines run by another method's developers as `independent_paper` (UNITE's ichorCNA comparator `ctdnafrag-20261009-eval-wang2026-ichorcna-tf-*`, Hou et al. 2024), and Helzer does the same in this pass. Set `attributes.origin` to `independent_paper` on `ctdnalit-20261011-fragmentia2026-eval-{delfi,griffin,fragma,fdi,nucleosome,subnucleosome}-{random-forest,xgboost,deep-learning}`. Keep `author_reported` on `ctdnalit-20261011-fragmentia2026-eval-fragmentia-ai-ulp-wgs`. In `sources.md` replace the Origin line with `Origin: the Fragmentia-AI evaluation is author_reported; the 18 baseline evaluations are independent_paper, because Geneseeq re-implemented methods it did not develop. The study is still a developer comparison: the baselines were re-implemented and run by the developers of the competing model.`

F2. The configuration parameters name a stored checkpoint the paper does not name. The article says the fragments are "processed ... through a DNABERT-2 architecture" with LoRA on the Wqkv layers; it does not say which pretrained weights, if any, initialise it. In `ctdnalit-20261011-fragmentia2026-config-fragmentia-ai-ulp-wgs` replace `attributes.parameters`

`DNABERT-2 backbone (catalog-model-dnabert-2) fine-tuned end to end with an attention-based MIL classifier on the ULP-WGS training cohort`

with

`DNABERT-2 architecture with LoRA on the Wqkv layers, trained end to end with an attention-based MIL classifier on the ULP-WGS training cohort; the paper does not name the pretrained weights, if any, that initialise it`

Do not add a `uses_model` link to `catalog-model-dnabert-2`.

F3. Append to `attributes.limitations` of `ctdnalit-20261011-fragmentia2026-protocol-ulp-wgs-heldout-auc` and of `use-case-mapping-ctdna-lit-20261011-fragmentia2026-ulp-wgs-heldout`: `The cohort has 1,245 non-cancer controls, the same number as the training cohort of the Fragmentia-AI WGS paper (Molecular Biomedicine 2026, Table S1) from the same company, so the two studies may share samples; neither paper says.`

Answers to question 4: the held-out split size is not printed (confirmed); 0.956 and 0.97 are both in Results P43 for what reads as the same quantity (confirmed, recorded); the p-value test is not named (confirmed); FRAGMA, FDI, nucleosome and subnucleosome are cited (refs 14 to 18) but not defined (confirmed). None of these blocks storage; all are in the limitations.

### Fragmentia-AI WGS (Molecular Biomedicine 2026)

W1. Supplementary Table S1 prints the class counts. Add to `ctdnalit-20261011-fragmentiawgs2026-data-train`: `"positives": 2450, "negatives": 1245`; to `ctdnalit-20261011-fragmentiawgs2026-data-validation`: `"positives": 894, "negatives": 1149`; and append ` Table S1: 2,450 cancers and 1,245 non-cancer controls.` and ` Table S1: 894 cancers and 1,149 non-cancer controls.` to their `population` strings.

W2. The limitation `Tumour-fraction strata are ichorCNA estimates; low TF (< 3%) is below ichorCNA's stated detection limit, so the stratum mixes truly low-TF cancers with misestimated ones.` adds an inference the paper does not make. In all four protocols and three judgements replace it with

`Tumour-fraction strata are ichorCNA estimates, not measured fractions; the authors chose the 3% cutoff because the ichorCNA study reported 0.03 as its lower limit for detecting tumour from ULP-WGS (Results P8), so the low stratum holds cancers whose tumour fraction ichorCNA cannot resolve.`

W3. Make `use-case-mapping-ctdna-lit-20261011-fragmentiawgs2026-test` `direct`. Its endpoint is the use case's: detection within ichorCNA tumour-fraction strata, including below 3%, at a false-positive cutoff fixed in advance, on whole-genome cfDNA, in a test cohort not used for fitting or selection. The proxy reasons given (no comparator, estimated strata, case-control, observed specificity 0.97) are limitations, not an endpoint mismatch; the CCGA methylation validation was judged `direct` with a post hoc threshold. Set `relevance` to `direct` and replace `rationale` with

`Measures the use case's endpoint for one workflow: detection within ichorCNA tumour-fraction strata, including below 3%, at a cutoff fixed in advance at 98% specificity in the training cohort and applied unchanged to an independent test cohort of 2,952 cancers and 3,044 non-cancer controls that was not used for fitting or model selection (observed specificity 0.97). Direct despite its limitations: the strata are ichorCNA estimates rather than measured tumour fractions, no comparator method is run on the cohort, the cohort is retrospective case-control, and the developer reports every value.`

Keep `proxy` for the validation judgement (the set was used for model selection) and the DELFI judgement (no strata, specificity 0.92 at the transferred cutoff, overlapping samples).

W4. Append to `attributes.limitations` of the test, validation and train protocols and of the test and validation judgements: `The training cohort has 1,245 non-cancer controls, the same number as the ULP-WGS cohort of the Fragmentia-AI paper (Cell Reports Medicine 2026) from the same company, so the two studies may share samples; neither paper says.`

W5. `coverage.json` `remaining_gaps` item 1 says cancer-type results are figure-only, but Results P19 prints test-cohort sensitivities for nine of 17 cancer types. Replace item 1 with `Per-stratum AUCs of the high/medium-TF scheme other than low TF, and cancer-type AUCs, are figure-only. Results P19 prints test-cohort sensitivity for nine of 17 cancer types (liver/biliary 0.88 to head and neck 0.29); these were not extracted because the list is partial.`

Answers to question 5: `recall` with the cutoff in the qualifier is correct. The vocabulary defines `sensitivity-at-98-percent-specificity` as recall at the threshold that gives 98% specificity, and the transferred cutoff gives 0.97 in the test cohort and 0.92 in the DELFI cohort. The DELFI overlap is recorded on the dataset, protocol and judgement. Question 7: the add order Helzer, Fragmentia-AI, Fragmentia-AI WGS is acceptable. Reusing the Fragmentia-AI method record is acceptable because it is a family record and each configuration carries the reported scheme name; the generic Griffin method under a `helzer2025` ID is acceptable because IDs are opaque.

### Xu and Feng 2026 (CpGPT)

C1. Source hash could not be re-verified. A fresh download of `https://www.medrxiv.org/content/10.64898/2026.07.26.26358979v1.full.pdf` on 2026-10-12 returned 2,761,577 bytes with SHA-256 `3d37b32e8ff782201ed8ee6677a01808d4f8c86eea70350a530dde7306cab7c9`, against the pinned 2,761,568 bytes and `369746bf...e7366961e`. Its PDF CreationDate is `D:20261011200812-07'00'` (2026-10-12T03:08Z, after the pinned retrieval at 21:49:59Z), so medRxiv regenerates the file and the pinned bytes are not retrievable. The text layer of my copy matches every one of the 15 extracted values, their intervals, the asserted sentences and the footnote. Do not change `artifact_sha256`. Add to `ctdnalit-20261011-cpgpt2026-source-preprint`:

`"hash_scope": "artifact_sha256 describes one retrieval (2026-10-11T21:49:59Z). medRxiv regenerates this PDF: a reviewer download on 2026-10-12 had 2,761,577 bytes, SHA-256 3d37b32e8ff782201ed8ee6677a01808d4f8c86eea70350a530dde7306cab7c9 and PDF CreationDate 2026-10-11T20:08:12-07:00. The reviewer's copy's text layer matched every extracted value. The licence does not allow archiving."`

and record the reviewer copy's hash as the review `artifact_sha256` on the 15 results and on the judgement.

C2. `coverage.json` `remaining_gaps` item 2 says per-split values are not printed for the classical models; they are printed for CpGPT (Results: validation 0.8942, 1.0000, 0.9520; test 1.0000, 1.0000, 0.9712) and were not extracted. Append ` CpGPT's per-split validation and test AUROCs are printed in the Results text and were not extracted.`

Answer to question 6: confirmed. The Methods say DMR discovery "was conducted using all 300 samples in the source cohort" and each test partition is "approximately 10%" with few controls. Origin is right: neither author is a CpGPT developer (Yili Xu, USC; Qianxi Feng, MicroTrace BioAI), the baselines are their own. Qianxi Feng is not Felix Y. Feng of the Helzer author list.

### Other questions in the report

Reference materials: agree not to add the two reference-material papers; neither defines a computational benchmark protocol or carries named-method results.

## Use-case field changes

No pinned field (question, decision, inputs, output, exclusions, setting, clinical_scope, intended_users) should change. Every existing judgement pins those fields, so a change would withhold all 13 fragmentomics and 11 methylation judgements until re-pinned, and the new evidence fits as `proxy` (and one `direct`) without it. Note for a later full re-pin: the fragmentomics `decision` ("including one source stratified by ichorCNA tumour fraction") and `output` ("AUCs within ichorCNA tumour-fraction strata from one developer study") are now out of date.

`evidence_gaps` is not pinned (`judgementPinFields` in `shared/omics/use-cases.ts`), so these are approved:

U1. `use-case-plasma-ctdna-fragmentomics` `attributes.evidence_gaps`: replace the item beginning `Tumour-fraction-stratified evidence is cross-validation from one developer study (Wang et al. 2026).` with

`Tumour-fraction-stratified evidence comes from two developer studies: cross-validation in Wang et al. 2026 and an independent test cohort in the Fragmentia-AI WGS paper (Molecular Biomedicine 2026), both using ichorCNA estimates rather than measured tumour fractions. In the extracted UNITE tables, sensitivity at a fixed specificity within a tumour-fraction stratum is printed only for the ichorCNA tumour-fraction comparator. The fragmentomic models' values are in Data file S2 sheet STATS_xgb_all_feat, which was not extracted; that sheet prints identical sensitivity at 98% and 99% specificity for every feature set in the lowest stratum and needs checking before use. The Fragmentia-AI WGS strata cover one model with no comparator.`

and append these items:

`Helzer et al. 2025 compare panel fragmentomic metrics at low ctDNA fraction by in silico mixing, but the values are in Figure 6B only.`

`The Fragmentia-AI (Cell Reports Medicine 2026) and Fragmentia-AI WGS (Molecular Biomedicine 2026) cohorts both come from the Geneseeq repository and report the same number of non-cancer controls (1,245) at 0.1x, so they may share samples; the Fragmentia-AI WGS external cohort is the public DELFI cohort, which overlaps the DELFI 2019 samples above.`

`Zeng et al. 2026 compute fragmentomic features from cfMeDIP-seq (methylation-enriched) reads, not whole-genome sequencing, and Helzer et al. 2025 from targeted exon panels.`

U2. `use-case-plasma-ctdna-methylation` `attributes.evidence_gaps`: append

`Zeng et al. 2026 compare methylation with fragmentomic features from one assay (cfMeDIP-seq) and one group; their sensitivities at 99% specificity are read on few healthy controls (six or seven per cross-validation fold, 17 in the validation set), and their methylation-only validation AUC is printed as 0.694 in the Source Data and 0.674 in the text.`

`Xu and Feng 2026 is a preprint whose candidate CpGs were selected using all 300 samples, including the test partitions of about 30 samples each.`

## Approved summary text

Both proposals had errors: "models with end motifs fell below 0.5" (two of the five motif-containing models did not: 0.514 and 0.826), "thirteen published fragmentomic metrics" (twelve metrics plus their combination, two of them the authors' own), "431 UW samples" (only 27 are healthy), and no mention of how few healthy controls set the 99% specificity in Zeng. The text below fixes those, reflects Z1 and Z2 (values not shown), and updates the opening source counts. Every number matches a stored result or a dataset count in these batches or in the existing reviewed summaries. Both name the developer-reported studies and the truth-set caveats (ichorCNA estimates, Li-Fraumeni carriers counted as cancers, the healthy-control protocol shift, feature selection on test samples), and neither recommends.

### `use-case-summary-plasma-ctdna-fragmentomics` (full replacement value)

Eight sources compare plasma cfDNA fragmentomic workflows on retrospective case-control cohorts. None is a prospective screening study and none measures clinical benefit. Cristiano et al. 2019, the DELFI developers, report 73% sensitivity (152 of 208 cancers) at a reported 98% specificity for DELFI in repeated cross-validation against 215 healthy individuals. Hou et al. 2024 re-implemented ten published fragmentation patterns and DELFI with one support vector machine each on the same cohort. They are independent of every pattern except IFS, which their corresponding author developed. In 10 x 10-fold cross-validation, pan-cancer AUC within open chromatin regions ranged from 0.8741 (fragment length) to 0.9736 (5' end motif), and their DELFI re-implementation reached 0.9575. Rankings changed on independent cohorts. On 46 lung cancers and 385 healthy individuals, with a model trained on 12 lung cancers, the end-motif model fell to AUC 0.5355 and sensitivity 0.0652 at 95% specificity, while fragment size distribution reached 0.9386 and 0.7174. Hou et al.'s supplementary pan-cancer and liver cancer sensitivities conflict with other tables of the same file and are not shown. Wang et al. 2026, the UNITE developers, stratified cancers by ichorCNA tumour fraction in pooled public and new 0.1x data that include samples of the DELFI and Jiang et al. cohorts used above. For cancers with an estimated tumour fraction of 3% or less, cross-validated AUC was 0.878 for all five features combined, 0.873 for fragment length, 0.857 for the SD of length counts, 0.736 for copy number, 0.715 for the C/T end-motif ratio and 0.651 for the short/long ratio, against 0.603 for a classifier using the ichorCNA tumour fraction alone, which detected 0.058 of these cancers at 95% specificity. For cancers with an estimated fraction above 3% and up to 10%, the ichorCNA classifier reached 0.983, above the combined model (0.962) and copy number alone (0.926). The extracted UNITE tables give sensitivity at a fixed specificity only for the ichorCNA comparator; the fragmentomic models' values are in a sheet not yet extracted. Jamshidi et al. 2022 (Cancer Cell), by the GRAIL developers, scored fragment length and fragment endpoint classifiers from 30x cfDNA whole-genome sequencing on the same CCGA substudy 1 participants as their methylation, copy-number and variant classifiers, at a 98% specificity threshold set post hoc within each set. On the validation set of 464 cancers and 362 non-cancers the fragment length classifier detected 29% (95% CI 25% to 34%) and the fragment endpoint classifier 18% (15% to 22%), against 34% for whole-genome methylation analysed double-blinded; both fragment classifiers were developed after the validation set had been unblinded, so these are not blinded validation results, and no tumour-fraction-stratified sensitivity is printed. Zeng et al. 2026 (Nature Cancer), by the cfMeDIP-seq developers, computed fragmentomic features from cfMeDIP-seq reads, which are enriched for methylated fragments rather than drawn from whole-genome sequencing, and report means over 10 fold models. On an independent paired-end validation set, a fragment-ratio classifier reached AUC 0.848 and detected 0.533 of cancers at 99% specificity, and fragment ratios combined with methylation reached 0.954 and 0.766. The validation set has 17 healthy controls, so its 99% specificity allows no false positive among them, and Li-Fraumeni syndrome carriers without current cancer count as cancers in its sensitivities. Three of the five classifiers that include end motifs scored below AUC 0.5 there, which the authors attribute to healthy controls processed with a different laboratory protocol, so validation results for all five are not shown. Helzer et al. 2025 (Nature Communications) compared twelve fragmentomic metrics adapted to targeted exon panels, including the authors' own fragment-size entropy metrics, their combination and Griffin, with one classifier and shared folds, on plasma from patients with metastatic cancer. The healthy-versus-cancer one-vs-rest AUROC ranged from 0.835 (open-chromatin entropy) to 0.989 (first-exon depth) in a UW cohort of 404 cancers and 27 healthy donors, with Griffin at 0.944, and from 0.951 to 1.000 in public GRAIL panel data from 151 cancers and 47 healthy donors. In a developer comparison on 0.1x whole-genome sequencing (Cell Reports Medicine 2026), a fragment-level language model (Fragmentia-AI) reached AUC 0.9561 on a held-out set of unstated size, against 0.9209 to 0.935 for the developers' re-implementation of DELFI features and 0.881 to 0.8863 for Griffin features under three classifiers. The same company's whole-genome model (Molecular Biomedicine 2026), on an independent test cohort of 2,952 cancers and 3,044 non-cancer controls, reached AUC 0.910 for cancers with an ichorCNA tumour fraction below 3% and detected 0.46 of them at a cutoff set to 98% specificity in training (observed test specificity 0.97); among those low-fraction cancers it detected 0.391 at stage I/II (637 of 1,628) and 0.708 at stage III/IV (345 of 487). Its tumour-fraction strata are ichorCNA estimates, no comparator was run on its cohorts, and its training cohort has the same number of non-cancer controls (1,245) as the Cell Reports Medicine cohort, so the two studies may share samples. Three of these four studies report on their authors' own method, and in the fourth the authors' own entropy metrics are among those compared. Cohorts, feature implementations, classifiers and validation designs differ, so no value is comparable across sources.

### `use-case-summary-plasma-ctdna-methylation` (full replacement value)

Six bounded sources compare cfDNA methylation methods. None is a prospective screening study and none measures clinical benefit. Jamshidi et al. 2022 (Cancer Cell), by the GRAIL developers, compared prototype cfDNA classifiers on the same CCGA substudy 1 participants at a 98% specificity threshold set post hoc within each set. On the validation set of 464 cancers and 362 non-cancers, analysed double-blinded, the whole-genome bisulfite methylation classifier detected 34% of cancers (95% CI 30% to 39%; 158 of 464), against 33% for variants with white-blood-cell correction, 30% for copy number with that correction, 27% for copy number, 16% for uncorrected variants and 2.6% for clinical risk factors alone; only the gap to the corrected variant classifier was not marked as significant. Among 127 validation cancers detected by all three representative classifiers, a methylation origin classifier developed after unblinding assigned the correct tissue for 75% (95 of 127), against 41% for copy number and 35% for corrected variants, with 'other' counted as correct for six cancer types. These are case-control results from the assay developer, not screening performance. Sun et al. 2024 (Genome Biology), an independent benchmark whose authors did not develop the tools, deconvolved real plasma with five methods and reported the ROC-AUC of a random forest trained on the estimated cell-type fractions; the paper does not state how the random forest was validated, so the AUCs may be in-sample. For 24 liver cancer patients and 32 healthy individuals (WGBS), AUCs were 0.96 (CelFEER), 0.93 (CelFiE), 0.91 (MethAtlas), 0.77 (cfNOMe) and 0.72 (UXM). On cfMethyl-Seq plasma (30 to 67 patients per cancer type, each against the same 193 healthy individuals), AUCs ranged from 0.72 (UXM, lung squamous cell carcinoma) to 0.93 (CelFiE, gastric cancer), and no method was highest for every cancer type. Giuili et al. 2025, a bioRxiv preprint not yet peer reviewed, ran ten reference-based tools inside the authors' DecoNFlow pipeline on in silico mixtures of tumour tissue or cell-line reads in healthy plasma reads. CelFiE had the lowest overall median tumour-fraction limit of detection in each dataset: 0.0070 (WGBS-TT), 0.0100 (RRBS-TT) and 0.0010 (RRBS-CL). CIBERSORT and EpiDISH had overall medians of 0.1000 to 0.2500 on WGBS-TT and RRBS-TT. For five tools the RRBS-CL values disagree between the supplementary table and Figure 4A and are not shown. Nguyen et al. 2023 (eLife), by the developers of the SPOT-MAS assay at Gene Solutions, compared three tissue-of-origin classifiers on combined methylation, fragment-length, copy-number and end-motif features from cancer patients only. In the validation cohort of 239 patients, overall accuracy was 0.53 (random forest), 0.69 (deep neural network) and 0.69 (graph convolutional network); the graph network was trained with the validation samples in its graph. Zeng et al. 2026 (Nature Cancer), by the cfMeDIP-seq developers, compared a cfMeDIP-seq methylation classifier with fragmentomic features of the same reads and their combinations, reporting means over 10 fold models. In cross-validation on 356 cancers and 64 healthy donors, methylation alone reached AUC 0.986 and detected 0.949 of cancers at 99% specificity; on an independent validation set its sensitivity at 99% specificity was 0.633, against 0.766 for methylation combined with fragment ratios. These sensitivities are read on few healthy controls (six or seven per cross-validation fold and 17 in the validation set), so 99% specificity there allows no false positive among them, and Li-Fraumeni syndrome carriers without current cancer count as cancers in the validation sensitivities. The Source Data give the methylation-only validation AUC as 0.694 and the text as 0.674, so that value is not shown. Xu and Feng 2026, a medRxiv preprint not yet peer reviewed, by authors who did not develop CpGPT, fine-tuned the CpGPT methylation foundation model on public targeted bisulfite cfDNA data from 254 gastrointestinal cancers and 46 non-cancer controls and built four classical classifiers themselves. On three train/validation/test splits with test partitions of about 30 samples, mean test AUROC was 0.9904 for CpGPT against 0.9573 (SVM), 0.9420 (elastic net), 0.8460 (gradient boosting) and 0.8408 (random forest); the candidate CpGs were selected using all 300 samples, including the test partitions. Neither study reports performance in a screening population. Tissue-of-origin evidence here comes from two developer studies, one methylation-only classifier scored on already detected cancers and one multimodal workflow, and neither classifies people without cancer.

## Reviewed evaluations for each judgement

After the corrections, list these in `reviewed_evaluations` and repin with `npm run use-cases:repin`.

- Zeng `meth-pe-primary-cv`, `frag-pe-primary-cv`: all 10 `ctdnalit-20261011-zeng2026-eval-pe-primary-cv-*`.
- Zeng `meth-pe-validation`, `frag-pe-validation`: `ctdnalit-20261011-zeng2026-eval-pe-validation-{fragment-ratio,insert-size,methylation,nucleosome-peak,ratios-methylation-1pct}`; the other five excluded (Z2).
- Zeng `meth-se-primary-cv`, `meth-se-validation`: the three evaluations on each protocol.
- Helzer `grail-full`: the 13 `ctdnalit-20261011-helzer2025-eval-grail-full-*`; `uw-full`: the 14 `ctdnalit-20261011-helzer2025-eval-uw-full-*`.
- Fragmentia-AI `ulp-wgs-heldout`: all 19 evaluations.
- Fragmentia-AI WGS `test`: `ctdnalit-20261011-fragmentiawgs2026-eval-test-high-medium-low-tf`; `validation`: `...-eval-validation-{high-tf,high-medium-tf,high-medium-low-tf}`; `delfi`: `...-eval-delfi-high-medium-low-tf`.
- CpGPT `split-runs`: all 5 evaluations.

## Checks run and outcomes

Sources. Re-downloaded every pinned artifact into a scratch directory (no email or personal identifier sent).
- Zeng article XML `72e82320...e761e323` and Source Data Fig. 4 XLSX `fae75168...0163b4`: match.
- Helzer article XML `48e63b92...2f70ead835` and Supplementary Information PDF `3fe7690e...e79b6e`: match; the archived `artifacts/helzer2025-article.xml.gz` decompresses to the same hash.
- Fragmentia-AI article XML `42a96f1b...dfd5fdbd`: match. The Europe PMC supplementary zip has a different hash per download, as the source record says; its `mmc1.pdf` member `357004ee...8122d41`: match.
- Fragmentia-AI WGS article XML `8c2cd974...32652b5ead` and Springer DOCX `df6f4b15...6e6055e85d0`: match; the archived article XML decompresses to the same hash.
- CpGPT medRxiv PDF: mismatch, regenerated by medRxiv (C1). Text layer checked instead.

Values: automated full comparison, my own parsers, no collector code imported or run.
- Zeng: stdlib OOXML reader (shared strings, raw values, style check: every value cell is General). All 52 results matched on value and s.d. column, sheet, row label and header; all 52 data rows of the eight sheets are present, none missed. 36 values quoted in Results P29, P32 and P33 were cross-checked against the sheet; all agree except the known 0.674 against 0.694.
- Helzer: parser of the pdftotext layout text with panel blocks fixed by row order (13 rows per block; 14 for the UW full panel), every Mean AUROC checked against its row mean within 0.0015. UW column order checked independently from the word bounding boxes of the rotated header (Bladder, ERneg, ERpos, NEPC, NSCLC, Normal, Prostate, RCC, SCLC, Mean). 790 of 790 cells matched, none missed or extra.
- Fragmentia-AI: all 19 Table S5 AUCs and 18 p-values compared with a table transcribed from the layout text; all match, none missed.
- Fragmentia-AI WGS: Table S4 read from the DOCX table XML with my own reader; all 6 sensitivities, intervals and denominators match, and each sensitivity equals detected/total to three decimals. The 24 text values were compared with Results P13, P14, P19 and P21; all match.
- CpGPT: all 15 Table 3 values and intervals compared with the layout text; all match.

Hand checks against the rendered table:
- Helzer: rendered pages 8 and 9 of the PDF and compared 44 values by eye (29 from Table S2 across all four blocks and nine of ten columns, 15 from Table S1 across all four blocks and all five columns); 44 of 44 match.
- The other batches have fewer than 40 values, so every value was checked against the printed table or sentence: Zeng 52 (sheet dump read in full), Fragmentia-AI 19, Fragmentia-AI WGS 30, CpGPT 15.

Mapping:
- Metric, qualifier, direction, unit, uncertainty type, denominators and dataset and split links checked for every result. Findings Z3, Z4, H1, H2, W1. Recall-with-cutoff is right (W, question 5).
- Every `null` and `missing_metadata` I sampled is unstated in the source (held-out size, p-value test, versions, metric implementations).

Origin and author overlap:
- Zeng, Fragmentia-AI and Fragmentia-AI WGS are developer studies; competing interests checked in the article XML.
- Helzer: the 27 authors include no Griffin developer.
- CpGPT: neither author developed CpGPT.
- One correction (F1).

Locators: the zero-based `<p>` convention was confirmed on all four JATS sources (A2). Every table locator resolved to its cell. One printed block label is wrong (H1).

Duplicates:
- No ID collides with the 54,592 IDs on `origin/main`. Every external link target exists (`ctdnafrag-20261009-method-delfi`, both use cases).
- No source with these DOIs or PMC IDs, and no CpGPT, Fragmentia, Griffin or Helzer record, exists on `origin/main`.
- The same holds on the 14 other `claude/lit-20261011-*` branches (local and remote) and in their sources, models, methods and batch files, and in the worktrees `rewire-benchmark-data-lit-{cells-networks,microbial-interactions,rna-otheromics,uc-execution,uc-splicing-cnv}`. The `protein-structure` worktree check returned no output, but its branch was clean.
- `claims.csv` agrees with `batch.jsonl` on every record ID, printed value and locator; no duplicate IDs inside the batches.

Scope and relevance:
- All five batches are in scope: plasma cfDNA, omics endpoints.
- Every judgement's endpoint matches the protocol. Proxy reasons were checked against the use-case inputs: cfMeDIP-seq and targeted panels are not whole-genome sequencing, and most endpoints are AUC with no fixed specificity.
- Changes: one relevance (W3), two exclusion lists (Z2) and added caveats (Z3, F3, W2, W4).

Store gating:
- Read `shared/omics/use-cases.ts` to check what the corrections do to publication. This found that the Zeng source concern would withhold the whole batch (Z1).
- Changing a pinned use-case field would withhold every existing judgement, which is why only `evidence_gaps` changes are approved.

Not done:
- I did not run `npm test`, `npm run typecheck`, `npm run build` or `records -- add`; the collector should run them after applying the corrections.
- I did not write `review.json`, the dated review or the record `review` objects. The collector, or whoever applies these corrections, should write them, citing this file and the checks above. Reviewer: `Claude (Opus 5.5) review agent reviewer-ctdna; no human review claimed`.
- I did not check whether Razavi et al. 2019's 47 non-cancer controls come from a GRAIL cohort that overlaps CCGA substudy 1 samples behind the Jamshidi judgements. This is worth a look before the summaries are cited together.
