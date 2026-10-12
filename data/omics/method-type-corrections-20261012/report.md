# Method-type tag corrections, 2026-10-12

This batch applies the method-type tag fixes from the independent use-case baseline review, `docs/reviews/use-cases/baselines-2026-10-12.md`. It covers both tables under "Method-type tag fixes for a separate reviewed PR". Each fix is a metadata correction of `facets.method_types`.

Status: prepared, not applied. The store files and provenance are unchanged. Every claim is `needs_review`, and so are the two new source records. Nothing here is marked reviewed. A separate reviewer will check the batch before it is applied.

## Files

| File | Content |
| --- | --- |
| `corrections.csv` | The 246 staged store edits, one row per record, in the `npm run records:correct` format (`record_id, field, old_value, new_value, evidence`) |
| `batch.jsonl` | 246 `metadata-correction-tags-20261012-*` claims, each keeping the previous value, and two new source records |
| `benelli-source.json`, `shi2019-lshvec-source.json` | The new source records, as included in `batch.jsonl` |
| `prepare.py`, `decisions.py` | Generate `corrections.csv` and `batch.jsonl` from the store and the review rows. `decisions.py` holds the rows that depended on a source check. Run from the repository root: `python3 -I data/omics/method-type-corrections-20261012/prepare.py` |

Each claim follows the `metadata-correction-qa-20261010-*` pattern:

- `field`: `facets.method_types`.
- `previous_value`: the old JSON array, or `absent` if the record had no tag.
- `value`: the new JSON array.
- `source_locator`: the review's evidence.
- A `subject` link to the corrected record.
- `source_ids`: the record's own sources plus the source that holds the evidence.
- `review`: names the agent and says it is not an independent review.

No source text is archived in this batch. The Benelli 2012 article is "All rights reserved", and only its hash and locator are recorded. Nothing from CPPC Table S2 columns E and F, which hold contributors' contact details, is copied.

## Applying after review

1. `npm run records:correct -- data/omics/method-type-corrections-20261012/corrections.csv <review.md>`. This checks each row's old value against the store, applies the edits and writes each record's `changed_by` provenance. `records -- change` is not needed for these records.
2. Set the approved claims and sources to their reviewed status, then `npm run records -- add data/omics/method-type-corrections-20261012/batch.jsonl data/omics/method-type-corrections-20261012`.
3. Run the tests, the type check and a data build.

Changing configuration tags changes the `evidence_sha256` of the active mappings that include those configurations, because that hash covers configurations. Judgement, summary and baseline pins do not cover configurations, so they are unaffected.

## Summary of changes

246 records: 43 from the review's first table (records that affect a same-data answer) and 203 from its second.

| Previous | New | Records |
| --- | --- | --- |
| none | foundation_model | 100 |
| none | supervised_machine_learning | 64 |
| conventional_pipeline | supervised_machine_learning | 35 |
| none | conventional_pipeline | 23 |
| specialist | conventional_pipeline | 21 |
| specialist | supervised_machine_learning | 2 |
| supervised_machine_learning | conventional_pipeline | 1 |

## Source checks and decisions

### EricScript

Tagged supervised_machine_learning. The correction cites a new source record, `method-type-corrections-20261012-source-benelli2012`.

- Crossref: doi:10.1093/bioinformatics/bts617, Bioinformatics 28(24):3232-3239, 2012-12-01. Authors Benelli, Pescucci, Marseglia, Severgnini, Torricelli and Magi. Crossref lists no licence.
- Europe PMC: PMID 23093608. Not in PMC.
- Unpaywall: bronze. The publisher page says "All rights reserved".
- Section 2.6: "To produce a single score, we trained an AdaBoost classifier on the aforementioned scores". Section 2.6.4: the classifier is "trained with synthetic data" and gives the "EricScore".
- OUP returns HTTP 403 to scripted downloads. The recorded hash is therefore of the article text as rendered in Chrome, as the record's `hash_scope` says.

### MSAlign

The review made this tag conditional on checking the source, so the source was checked first: arXiv 2605.19752v2, SHA-256 `a31d1167b0ded72f64717881dd6cba0946a56b495d76f169d8e44115c3266fda`, CC BY 4.0.

- Evidence: the abstract and Section 3 (p.4) describe "two frozen foundation models (DreaMS for mass spectra and MolDeBERTa for molecules)" with trained MLP adapters. Appendix B.1 (p.18) describes the training.
- Outcome: all three named records are tagged foundation_model.
- MSAlign score fusion (Section 3, p.5) is a seven-score ensemble with weights fitted on validation data. Only two of its four alignment scorers use both foundation encoders. Recording it as a distinct model is an identity change, so it is left for a separate change.

### HECTOR

Tagged conventional_pipeline. The source was checked first: medRxiv v1 full-text HTML, SHA-256 `dcc0287f20ebb8a2fca1927bd5cf50776ccea9e6099f379e997d8bec77d663bf`, CC BY 4.0.

- Evidence: Materials and Methods, "Engine Design and ENIGMA V1.2 Implementation". HECTOR assigns evidence codes against VCEP-defined thresholds, then combines them with the ACMG/AMP rules and a point-based system.
- BayesDel and SpliceAI scores are inputs to HECTOR. HECTOR itself is not trained.

### LSHVec

Tagged supervised_machine_learning. The method paper itself was not read: the ACM BCB 2021 version (doi:10.1145/3459930.3469521) returned HTTP 403.

- What was read instead: the authors' bioRxiv preprint 10.1101/726729v1, CC BY-NC-ND 4.0, SHA-256 `33721591b8f0162505764406b603ba17dcb934b27e9b90db7ded6b1f3dcc97de`. It is added as `method-type-corrections-20261012-source-shi2019-lshvec`.
- Section 3.2: k-mer embeddings learned with fastText skip-gram, without supervision.
- Section 3.3: "taxonomy classification is supervised learning", using a softmax network trained on labelled reads.
- Section 3 labels the read classifier "(unsupervised)", which contradicts Section 3.3.
- The 2021 version may differ from the preprint. The reviewer should decide whether the preprint meets the review's condition.

### CPPC submission rows (per named method)

Tags come from the CPPC paper (PMC13228547): its main-text Methods and Supplementary Note S1. Table S2 itself has no method descriptions.

- conventional_pipeline: row 18 (GO_knn) and row 19 (LowExp).
- foundation_model: row 5 (scBERT), with a supervised regressor on top.
- supervised_machine_learning: rows 2, 3, 4, 6, 7, 8, 9, 12, 16, 17, 21, 22, 23 and 24.
- Unresolved and left untyped: rows 10, 11, 13, 14, 15 and 20. Each has only a note that it is similar to another method, with no description of what it did.

Rows 2, 4, 5, 6, 7, 8, 9, 12, 16, 22 and 24 work in two steps: gene features first, then a predictor. The predictor was chosen by cross-validation from nearest-neighbour, kernel ridge and bagging regressors, and the source does not say which one gave each best model. So supervised_machine_learning is the best-supported tag for these rows, not a certain one, and each of their notes says so.

Rows 3 and 23 are not two-step:

- Row 3 trains an MLP regressor directly.
- Row 23 learns its own transformation matrices. Its note also records that an undescribed alternative method was used for challenge 2.
- Row 17's note says its random forest only selects genes.
- Row 24's note says it used different methods for the two challenges.

Only the `submission-row-*` records named in the review were changed. The `ucc-research-config-cppc-reimplemented-row-*` records are also untyped and were left as they are.

### ProteinGym AMFR (per method, from the proposer's report)

83 of the 97 configurations are tagged, following `data/omics/use-case-baselines-20261012/report.md`.

- 80 foundation_model. S2F-MSA, S3F-MSA and UniRep evotuned are tagged with their parent models.
- 3 supervised_machine_learning: VESPA, VESPAl and VespaG.
- 14 left untyped because the proposer did not classify them: DeepSequence (2), EVE (2), TranceptEVE (3), EVmutation, GEMME, RSALOR, Site-independent, SiteRM, WaveNet and ESCOTT.
- Conflict for the reviewer: ProteinMPNN is tagged foundation_model as proposed, but one existing ProteinMPNN configuration elsewhere in the store is supervised_machine_learning.

### Other notes

- PROVEAN: the SIFT row's evidence says "The same applies to PROVEAN", so `somatic-oncogenicity-20261009-method-provean` and its two configurations are included. The reviewer can drop them if that row's record IDs are meant literally.
- The rows the review marked optional are applied: the ichorCNA-TF logistic regression, and the Drost splice-predictor consensus with its four configurations.
- These rows are tagged as the review proposed but deserve a second look:
  - The 24 Feng configurations. The review did not read the Feng source.
  - The 4 AlphaGenome configurations among them. `catalog-model-alphagenome` is tagged foundation_model.
  - FoldBench, and the CIViC and EGFR language-model rows. None of these was source-checked.

## Not changed

- The other Samarakoon Parabricks configurations (`-parabricks-4xa100`, `-4xl4`, `-8xh100`) and `model-execution-20261009-config-oconnell2023-aws-gpu2` with its siblings (`-aws-gpu4`, `-aws-gpu8`, `-dgx-gpu2/4/8`, `-gcp-a2-gpu2/4/8`). The review says to split each into one configuration per caller before tagging. Only `samarakoon2025-parabricks-4-3-0-1-8xh100`, which runs DeepVariant only, was retagged.
- The method records `ctdnameth-20261009-method-celfeer`, `-method-uxm`, `-method-houseman-cp` and `-method-epidish-rpc` stay specialist. The review named only their Sun and Giuili configurations. CIBERSORT is unchanged, as the review says.

## Missing links, listed and not added

These are left for a separate change.

- `configuration_of` `cnv-20261009-method-dragen` on `amp-config-dragen42-cnv-sv` and `amp-config-dragen42-phase4-runtime`.
- `configuration_of` `uc20260930-model-jores-plant-promoter-cnn` on `agront-2024-fig3e-method-cnn-jores-et-al-promoter-strength-maize-protoplasts` and `-tobacco-leaves`.
- No method link, and the review gives no target, on `uc-clinical-20260930-enigma-v10-manual`, `uc-clinical-20260930-oncovi-prior-mtb` and the 24 Feng configurations.
- Baseline configurations with no `configuration_of` link. None of them is in a comparison with a machine-learning row.
  - `amp-oncology-rna-20261007-issue-10-config-strelka2`.
  - `amp-oncology-rna-20261007-nch-config-star-fusion`, `-nch-config-arriba`, `-issue-11-config-star-fusion` and `-issue-11-config-arriba`.
  - `model-execution-20261009-config-oconnell2023-aws-c6i-8xlarge` and `-gcp-n2-standard-32`, which should link to `model-execution-20261009-method-gatk-best-practices-cpu`.
  - `amp-oncology-rna-20261007-issue-12-config-fraser-2021-article-implementation`, which should link to `rna-splicing-20261009-method-fraser`.
  - `amp-20261007-rna-pathogens-configuration`. There is no SURPI+ record to link to.

## Effect on same-data answers

### Method

`deriveUseCaseInputs` was run twice on in-memory copies of the store. The first copy is the current store. The second has `corrections.csv` applied with the repository's `applyCorrection`, plus the batch records, and passes `validateRecords`. Each result was scored with the website rule:

- A comparison is one presentation group, or one protocol when the protocol has no group, over active mappings.
- A row is a baseline row when its configuration, or that configuration's first `configuration_of`, `family` or `variant_of` target, is in the baseline's `method_ids`.
- A machine-learning row is any other row tagged foundation_model or supervised_machine_learning.

The counts before the edits match the review's "Same-data ML" column for all 26 use cases.

### Results

| Use case | Before | After | What changes |
| --- | --- | --- | --- |
| Cell-type annotation transfer | 0 | 2 | scTab: logistic regression next to scGPT, UCE, CellTypist, XGBoost, MLP, CIForm and scTab. Abdelaal Baron: scmap-cell and linear SVM next to scPred. The Abdelaal brain protocol still has no machine-learning row. |
| Mass spectrum shortlisting | 0 | 3 | DeepSets next to Emb-Cos, JESTR, MSAlign and MSAlign score fusion, on all three MSAlign v2 protocols |
| Plant promoter reporters | 0 | 2 | GC and motif linear regression next to the Jores CNN, on both protocols |
| Rhodopsin wavelength transfer | 0 | 5 | BLASSO next to RhoMax and RhoMax + retinal, on all five splits |
| Tumour RNA fusion | 0 | 2 | STAR-Fusion and Arriba next to EricScript, in the two Tamura groups (four protocols). The Kim 2025 leukaemia comparison still has no machine-learning row. |
| UTR translation | 0 | 2 | k-mer random forests next to FramePool and Optimus 5-Prime, on both protocols |
| Regulatory variant follow-up | 1 | 2 | MPRAbc K562: ABC next to ENCODE-rE2G and the MPRAbc models. The answer was already yes. |

The other 19 use cases keep their counts. Phenotype perturbation selection gains typed CPPC rows but still has no random-selection row.

### Gap sentences

None of the review's 10 gap sentences becomes false. Each was checked against the baseline methods matched in every comparison after the edits.

- DNA pathogens, RNA pathogens, model execution, ctDNA methylation, phenotype perturbation selection and unresolved reanalysis: there is still no machine-learning row next to any baseline method.
- CNV: the only machine-learning comparison is still the Zhang 2026 classification, against AnnotSV and ClassifyCNV. ExomeDepth and CNVnator have none.
- Somatic oncogenicity: none next to OncoVI on its four protocols. The machine-learning comparisons cover SIFT only.
- Patient RNA splicing: none next to FRASER or OUTRIDER.
- Structural hypotheses: none next to ClusPro on the four BM5 protocols. DiffDock-L joins the ligand comparison.

The review added no gap sentence to the six use cases where the only obstacle was a tag, so nothing needs removing. Its conditional fusion sentence was never added. If the EricScript retag is approved, the review asks for the fusion use case to say that this comparison is an alignment caller with a learned score filter, not a learned caller. That text change is not in this batch.

## Remaining gaps

- The Benelli 2012 hash is of rendered text, not of publisher bytes.
- The LSHVec tag rests on the 2019 preprint.
- FoldBench, the CIViC and EGFR language-model rows, the Feng configurations and the ProteinGym AMFR tags have not been source-checked.
- Six CPPC rows and 14 ProteinGym AMFR configurations remain untyped.
- The branch is based on `origin/claude/use-case-baselines`. `origin/main` is one commit ahead of the merge base and touches none of these records. It has not been merged, because nothing is committed yet.

## Change list

Every staged edit, in `corrections.csv` order.

| Record | Previous | New | Evidence |
| --- | --- | --- | --- |
| `ucc-research-config-sctab-scgpt-ft` | none | foundation_model | scTab Methods: fine-tuned scGPT and frozen scGPT embeddings; catalog-model-scgpt configurations are foundation_model |
| `ucc-research-config-sctab-scgpt-zero` | none | foundation_model | scTab Methods: fine-tuned scGPT and frozen scGPT embeddings; catalog-model-scgpt configurations are foundation_model |
| `ucc-research-config-sctab-uce` | none | foundation_model | scTab Methods: UCE embeddings with a linear probe; cell-type-20261009-config-wu2025-uce-onclass is foundation_model |
| `ucc-research-config-sctab-celltypist` | none | supervised_machine_learning | scTab Methods: each classifier is trained on labelled cells |
| `ucc-research-config-sctab-ciform` | none | supervised_machine_learning | scTab Methods: each classifier is trained on labelled cells |
| `ucc-research-config-sctab-mlp` | none | supervised_machine_learning | scTab Methods: each classifier is trained on labelled cells |
| `ucc-research-config-sctab-sctab` | none | supervised_machine_learning | scTab Methods: each classifier is trained on labelled cells |
| `ucc-research-config-sctab-xgboost` | none | supervised_machine_learning | scTab Methods: each classifier is trained on labelled cells |
| `ucc-research-config-sctab-linear` | none | supervised_machine_learning | scTab Methods: each classifier is trained on labelled cells |
| `ucc-research-config-abdelaal-svm-no-rejection` | none | supervised_machine_learning | Abdelaal et al. 2019: supervised classifiers trained on a labelled reference |
| `ucc-research-config-abdelaal-svm-rejection` | none | supervised_machine_learning | Abdelaal et al. 2019: supervised classifiers trained on a labelled reference |
| `ucc-research-config-abdelaal-scpred` | none | supervised_machine_learning | Abdelaal et al. 2019: supervised classifiers trained on a labelled reference |
| `ucc-research-config-abdelaal-scmapcell` | none | conventional_pipeline | Abdelaal et al. 2019: scmap-cell projects cells onto a reference by similarity, with no trained classifier |
| `uc20260930-msalign-v2-config-deepset` | none | supervised_machine_learning | MassSpecGym Supplementary: DeepSets and FFN are trained fingerprint predictors; Emb-Cos and JESTR are trained embedding models |
| `uc20260930-msalign-v2-config-emb-cos` | none | supervised_machine_learning | MassSpecGym Supplementary: DeepSets and FFN are trained fingerprint predictors; Emb-Cos and JESTR are trained embedding models |
| `uc20260930-msalign-v2-config-jestr` | none | supervised_machine_learning | MassSpecGym Supplementary: DeepSets and FFN are trained fingerprint predictors; Emb-Cos and JESTR are trained embedding models |
| `msalign-2026-table3-method-deepsets` | none | supervised_machine_learning | MassSpecGym Supplementary: DeepSets and FFN are trained fingerprint predictors; Emb-Cos and JESTR are trained embedding models |
| `msalign-2026-table3-method-emb-cos` | none | supervised_machine_learning | MassSpecGym Supplementary: DeepSets and FFN are trained fingerprint predictors; Emb-Cos and JESTR are trained embedding models |
| `msalign-2026-table3-method-ffn` | none | supervised_machine_learning | MassSpecGym Supplementary: DeepSets and FFN are trained fingerprint predictors; Emb-Cos and JESTR are trained embedding models |
| `msalign-2026-table3-method-jestr` | none | supervised_machine_learning | MassSpecGym Supplementary: DeepSets and FFN are trained fingerprint predictors; Emb-Cos and JESTR are trained embedding models |
| `msalign-2026-table3-method-sail` | none | supervised_machine_learning | MassSpecGym Supplementary: DeepSets and FFN are trained fingerprint predictors; Emb-Cos and JESTR are trained embedding models |
| `uc20260930-jores-config-maize-protoplasts-cnn` | none | supervised_machine_learning | Jores et al. 2021 p849: convolutional neural network |
| `uc20260930-jores-config-tobacco-leaves-cnn` | none | supervised_machine_learning | Jores et al. 2021 p849: convolutional neural network |
| `uc20260930-jores-config-maize-protoplasts-gc-motif-linear` | none | conventional_pipeline | Jores et al. 2021 p849: linear regression on GC content and the maximum PWM match score |
| `uc20260930-jores-config-tobacco-leaves-gc-motif-linear` | none | conventional_pipeline | Jores et al. 2021 p849: linear regression on GC content and the maximum PWM match score |
| `uc20260930-rhomax-config-rhomax` | none | supervised_machine_learning | RhoMax Methods: a graph neural network trained on structures |
| `uc20260930-rhomax-config-rhomax-retinal` | none | supervised_machine_learning | RhoMax Methods: a graph neural network trained on structures |
| `uc20260930-rhomax-config-blasso` | none | supervised_machine_learning | RhoMax: BLASSO is "a first attempt to utilize machine learning" (Bayesian LASSO) |
| `uc20260930-framepool-config-framepool-50` | none | supervised_machine_learning | FramePool Methods: convolutional networks trained on the MPRA library |
| `uc20260930-framepool-config-framepool-100` | none | supervised_machine_learning | FramePool Methods: convolutional networks trained on the MPRA library |
| `uc20260930-framepool-config-framepool-combined` | none | supervised_machine_learning | FramePool Methods: convolutional networks trained on the MPRA library |
| `uc20260930-framepool-config-optimus-50` | none | supervised_machine_learning | FramePool Methods: convolutional networks trained on the MPRA library |
| `uc20260930-framepool-config-optimus-100` | none | supervised_machine_learning | FramePool Methods: convolutional networks trained on the MPRA library |
| `uc20260930-framepool-config-3mer-random-forest` | none | supervised_machine_learning | FramePool Methods: "we also trained random forest models which use k-mer counts as input features" |
| `uc20260930-framepool-config-4mer-random-forest` | none | supervised_machine_learning | FramePool Methods: "we also trained random forest models which use k-mer counts as input features" |
| `uc20260930-framepool-config-5mer-frame-forest` | none | supervised_machine_learning | FramePool Methods: "we also trained random forest models which use k-mer counts as input features" |
| `uc20260930-framepool-config-frame-forest-4mer` | none | supervised_machine_learning | FramePool Methods: "we also trained random forest models which use k-mer counts as input features" |
| `uc20260930-framepool-config-frame-forest-hyperopt` | none | supervised_machine_learning | FramePool Methods: "we also trained random forest models which use k-mer counts as input features" |
| `rna-fusion-20261009-method-ericscript` | conventional_pipeline | supervised_machine_learning | Benelli et al. 2012 section 2.6: "we trained an AdaBoost classifier"; section 2.6.4: the classifier, trained with synthetic data, gives the EricScore that ranks candidate fusions |
| `rna-fusion-20261009-config-tamura2026-ericscript` | conventional_pipeline | supervised_machine_learning | Benelli et al. 2012 section 2.6: "we trained an AdaBoost classifier"; section 2.6.4: the classifier, trained with synthetic data, gives the EricScore that ranks candidate fusions |
| `uc-clinical-20260930-method-bayesdel` | none | supervised_machine_learning | Matches the other 7 BayesDel configurations; Ramadane 2025 calls BayesDel a meta-predictor |
| `uc-clinical-20260930-bayesdel-enigma` | none | supervised_machine_learning | Matches the other 7 BayesDel configurations; Ramadane 2025 calls BayesDel a meta-predictor |
| `uc-clinical-20260930-bayesdel-pejaver-generic` | none | supervised_machine_learning | Matches the other 7 BayesDel configurations; Ramadane 2025 calls BayesDel a meta-predictor |
| `uc-clinical-20260930-enigma-v10-manual` | none | conventional_pipeline | Manual criteria-based curation (record description) |
| `uc-clinical-20260930-method-oncovi` | none | conventional_pipeline | OncoVI Methods: "an IF-ELSE implementation" of the points-based SOP |
| `uc-clinical-20260930-oncovi-study` | none | conventional_pipeline | OncoVI Methods: "an IF-ELSE implementation" of the points-based SOP |
| `uc-clinical-20260930-oncovi-prior-mtb` | none | conventional_pipeline | OncoVI Methods: "an IF-ELSE implementation" of the points-based SOP |
| `somatic-oncogenicity-20261009-method-sift` | specialist | conventional_pipeline | Chen et al. 2020 Table 1: SIFT uses a position-specific scoring matrix |
| `somatic-oncogenicity-20261009-config-chen2020-sift` | specialist | conventional_pipeline | Chen et al. 2020 Table 1: SIFT uses a position-specific scoring matrix |
| `somatic-oncogenicity-20261009-config-chen2020-sift4g` | specialist | conventional_pipeline | Chen et al. 2020 Table 1: SIFT uses a position-specific scoring matrix |
| `somatic-oncogenicity-20261009-config-lee2026-sift` | specialist | conventional_pipeline | Chen et al. 2020 Table 1: SIFT uses a position-specific scoring matrix |
| `somatic-oncogenicity-20261009-config-lee2026-sift4g` | specialist | conventional_pipeline | Chen et al. 2020 Table 1: SIFT uses a position-specific scoring matrix |
| `somatic-oncogenicity-20261009-method-provean` | specialist | conventional_pipeline | Chen et al. 2020 Table 1: PROVEAN uses a delta alignment score |
| `somatic-oncogenicity-20261009-config-chen2020-provean` | specialist | conventional_pipeline | Chen et al. 2020 Table 1: PROVEAN uses a delta alignment score |
| `somatic-oncogenicity-20261009-config-lee2026-provean` | specialist | conventional_pipeline | Chen et al. 2020 Table 1: PROVEAN uses a delta alignment score |
| `uc-clinical-20260930-method-exomiser` | none | conventional_pipeline | Other Exomiser configurations; Yuan et al. 2022 Table 2 classes Exomiser by phenotype comparison |
| `uc-clinical-20260930-exomiser-v14` | none | conventional_pipeline | Other Exomiser configurations; Yuan et al. 2022 Table 2 classes Exomiser by phenotype comparison |
| `uc-clinical-20260930-talos-default` | none | conventional_pipeline | Other Talos configurations; Kaschta 2026 |
| `uc-clinical-20260930-talos-strict` | none | conventional_pipeline | Other Talos configurations; Kaschta 2026 |
| `uc-clinical-20260930-talos-monthly` | none | conventional_pipeline | Other Talos configurations; Kaschta 2026 |
| `amp-config-dragen42-cnv-sv` | none | conventional_pipeline | Other DRAGEN configurations (cnv-20261009-method-dragen) are conventional_pipeline |
| `amp-config-dragen42-phase4-runtime` | none | conventional_pipeline | Other DRAGEN configurations (cnv-20261009-method-dragen) are conventional_pipeline |
| `model-execution-20261009-config-samarakoon2025-parabricks-4-3-0-1-8xh100` | conventional_pipeline | supervised_machine_learning | Samarakoon et al. 2025 Supplementary Table S4: Parabricks DeepVariant only; model-execution-20261011-model-deepvariant is supervised_machine_learning |
| `uc-clinical-20260930-civic-gpt5-alone` | none | foundation_model | Record names and descriptions: GPT-5, ChatGPT Agent Mode and Qwen3-Reranker-8B are large pretrained language models used without task training |
| `uc-clinical-20260930-civic-gpt5-mcp` | none | foundation_model | Record names and descriptions: GPT-5, ChatGPT Agent Mode and Qwen3-Reranker-8B are large pretrained language models used without task training |
| `uc-clinical-20260930-civic-agent-mode` | none | foundation_model | Record names and descriptions: GPT-5, ChatGPT Agent Mode and Qwen3-Reranker-8B are large pretrained language models used without task training |
| `ucc-clinical-egfr-config-qwen3-reranker-8b` | none | foundation_model | Record names and descriptions: GPT-5, ChatGPT Agent Mode and Qwen3-Reranker-8B are large pretrained language models used without task training |
| `ucc-clinical-egfr-config-medcpt-ft` | none | supervised_machine_learning | Record description: MedCPT cross-encoder fine-tuned on the CIViC-Fact training data |
| `catalog-model-kraken2` | specialist | conventional_pipeline | Its configurations are conventional_pipeline; minimizer database lookup (record description) |
| `ctdnameth-20261009-method-methatlas` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-method-celfie` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-sun2024-methatlas` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-sun2024-celfie` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-sun2024-celfeer` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-sun2024-uxm` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-giuili2025-methatlas` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-giuili2025-celfie` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-giuili2025-uxm` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-giuili2025-houseman-eq` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-giuili2025-houseman-ineq` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnameth-20261009-config-giuili2025-epidish-rpc` | specialist | conventional_pipeline | Sun et al. 2024 Background: deconvolution by non-negative least squares (MethAtlas) and expectation-maximisation (CelFiE) fitting |
| `ctdnafrag-20261009-config-wang2026-ichorcna-tf-logistic-regression` | conventional_pipeline | supervised_machine_learning | Wang et al. 2026 Results: ichorCNA tumour fraction fed to a one-feature logistic regression (ichorCNA-TF) |
| `lit-genomics-20261011-dnalongbench-config-abc` | supervised_machine_learning | conventional_pipeline | DNALongBench Methods, "Expert Model": ABC from DNase-seq, H3K27ac and Hi-C, with no training step |
| `amp-feng-20261007-config-qtl-eqtl-enformer-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-eqtl-enformer-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-eqtl-sei-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-eqtl-sei-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-eqtl-alphagenome-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-ipaqtl-enformer-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-ipaqtl-enformer-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-ipaqtl-sei-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-ipaqtl-sei-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-ipaqtl-alphagenome-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-paqtl-enformer-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-paqtl-enformer-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-paqtl-sei-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-paqtl-sei-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-paqtl-alphagenome-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-sqtl-enformer-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-sqtl-enformer-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-sqtl-sei-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-sqtl-sei-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-qtl-sqtl-alphagenome-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-variant-enformer-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-variant-enformer-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-variant-sei-hidden-states` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `amp-feng-20261007-config-variant-sei-output-tracks` | conventional_pipeline | supervised_machine_learning | The store's Enformer and Sei model records (regulatory-variant-20261009-model-enformer, regulatory-variant-20261009-model-sei) are supervised_machine_learning |
| `lit-structure-20261011-lipp-config-diffdock-l` | specialist | supervised_machine_learning | LiPP: "AI-based docking tool", "Trained on complexes in PDBbind before 2019" |
| `catalog-model-diffdock-l` | specialist | supervised_machine_learning | LiPP: "AI-based docking tool", "Trained on complexes in PDBbind before 2019" |
| `ucc-research-config-mprabc-abc` | none | conventional_pipeline | MPRAbc Introduction: ABC is "a mathematical framework" |
| `ucc-research-config-mprabc-re2g` | none | supervised_machine_learning | MPRAbc: "trained within the ENCODE-rE2G framework" |
| `ucc-research-config-mprabc-full` | none | supervised_machine_learning | MPRAbc: "trained within the ENCODE-rE2G framework" |
| `ucc-research-config-mprabc-megamap` | none | supervised_machine_learning | MPRAbc: "trained within the ENCODE-rE2G framework" |
| `ucc-research-config-mprabc-mpralegnet` | none | supervised_machine_learning | MPRAbc: "trained within the ENCODE-rE2G framework" |
| `ucc-research-config-mprabc-sei` | none | supervised_machine_learning | MPRAbc: "trained within the ENCODE-rE2G framework" |
| `ucc-docking-cluspro-bm5-2020-config-others` | none | conventional_pipeline | ClusPro BM5: FFT rigid-body docking |
| `ucc-docking-cluspro-bm5-2020-config-enzyme-balanced` | none | conventional_pipeline | ClusPro BM5: FFT rigid-body docking |
| `ucc-research-config-foldbench-af3` | none | foundation_model | Matches other AlphaFold 3 and Chai-1 configurations |
| `ucc-research-config-foldbench-boltz1` | none | foundation_model | Matches other AlphaFold 3 and Chai-1 configurations |
| `ucc-research-config-foldbench-chai1` | none | foundation_model | Matches other AlphaFold 3 and Chai-1 configurations |
| `ucc-research-config-foldbench-helixfold3` | none | foundation_model | Matches other AlphaFold 3 and Chai-1 configurations |
| `ucc-research-config-foldbench-protenix` | none | foundation_model | Matches other AlphaFold 3 and Chai-1 configurations |
| `agront-2024-fig3e-method-agront-promoter-strength-maize-protoplasts` | none | foundation_model | AgroNT is a pretrained genomic language model |
| `agront-2024-fig3e-method-agront-promoter-strength-tobacco-leaves` | none | foundation_model | AgroNT is a pretrained genomic language model |
| `agront-2024-fig3e-method-cnn-jores-et-al-promoter-strength-maize-protoplasts` | none | supervised_machine_learning | The Jores et al. 2021 CNN |
| `agront-2024-fig3e-method-cnn-jores-et-al-promoter-strength-tobacco-leaves` | none | supervised_machine_learning | The Jores et al. 2021 CNN |
| `rna-splicing-20261009-method-splice-predictor-consensus` | conventional_pipeline | supervised_machine_learning | A vote over four trained predictors (SpliceAI, Pangolin, SPiP and SQUIRLS) |
| `rna-splicing-20261009-config-drost2025-at-least-1` | conventional_pipeline | supervised_machine_learning | A vote over four trained predictors (SpliceAI, Pangolin, SPiP and SQUIRLS) |
| `rna-splicing-20261009-config-drost2025-at-least-2` | conventional_pipeline | supervised_machine_learning | A vote over four trained predictors (SpliceAI, Pangolin, SPiP and SQUIRLS) |
| `rna-splicing-20261009-config-drost2025-at-least-3` | conventional_pipeline | supervised_machine_learning | A vote over four trained predictors (SpliceAI, Pangolin, SPiP and SQUIRLS) |
| `rna-splicing-20261009-config-drost2025-at-least-4` | conventional_pipeline | supervised_machine_learning | A vote over four trained predictors (SpliceAI, Pangolin, SPiP and SQUIRLS) |
| `rewire-mfass-matched-v1-configuration-s0` | none | supervised_machine_learning | SpliceAI and Pangolin (configuration_of links) |
| `rewire-mfass-matched-v1-configuration-s1` | none | supervised_machine_learning | SpliceAI and Pangolin (configuration_of links) |
| `rewire-mfass-matched-v1-configuration-p0` | none | supervised_machine_learning | SpliceAI and Pangolin (configuration_of links) |
| `rewire-mfass-matched-v1-configuration-p1` | none | supervised_machine_learning | SpliceAI and Pangolin (configuration_of links) |
| `rewire-local-20260920-configuration-flip2-train-mean` | none | conventional_pipeline | Fixed training-mean and composition-ridge probes (record descriptions) |
| `rewire-local-20260920-configuration-flip2-composition` | none | conventional_pipeline | Fixed training-mean and composition-ridge probes (record descriptions) |
| `rewire-local-20260921-configuration-composition22` | none | conventional_pipeline | Fixed training-mean and composition-ridge probes (record descriptions) |
| `rewire-local-20260921-configuration-esm2-35m` | none | foundation_model | Frozen ESM-2 embeddings with a ridge probe |
| `rewire-local-20260921-configuration-esm2-8m` | none | foundation_model | Frozen ESM-2 embeddings with a ridge probe |
| `uc20260930-proteingym-amfr-config-aido-protein-rag-16b` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-carp-38m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-carp-600k` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-carp-640m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-carp-76m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm-1b` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm-1v-ensemble` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm-1v-single` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm-c-300m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm-c-600m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm-if1` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-150m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-15b` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-35m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-3b` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-650m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-8m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-esm3-open-1-4b` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-mif` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-mif-st` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-msa-transformer-ensemble` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-msa-transformer-single` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-mulan` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-poet-200m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen2-base` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen2-l` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen2-m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen2-s` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen2-xl` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen3-112m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen3-1b` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen3-219m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen3-339m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen3-3b` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-progen3-762m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-prosst-k-1024` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-prosst-k-128` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-prosst-k-20` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-prosst-k-2048` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-prosst-k-4096` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-prosst-k-512` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-proteinmpnn` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protgpt2` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protriever` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-ensemble` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-k-10-h-1280` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-k-10-h-512` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-k-10-h-768` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-k-20-h-1280` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-k-20-h-512` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-k-20-h-768` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-k-30-h-1280` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-k-30-h-512` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-protssn-k-30-h-768` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-rita-l` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-rita-m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-rita-s` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-rita-xl` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-s2f` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-s2f-msa` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-s3f` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-s3f-msa` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-saprot-35m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-saprot-650m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-tranception-l` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-tranception-l-no-retrieval` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-tranception-m` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-tranception-m-no-retrieval` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-tranception-s` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-tranception-s-no-retrieval` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-unirep` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-unirep-evotuned` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-venusrem` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-xtrimopglm-100b-int4` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-xtrimopglm-10b-mlm` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-xtrimopglm-1b-clm` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-xtrimopglm-1b-mlm` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-xtrimopglm-3b-clm` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-xtrimopglm-3b-mlm` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-xtrimopglm-7b-clm` | none | foundation_model | Proposer's report, ProteinGym AMFR: protein language and structure-conditioned models fit foundation_model |
| `uc20260930-proteingym-amfr-config-vespa` | none | supervised_machine_learning | Proposer's report, ProteinGym AMFR: VESPA, VESPAl and VespaG are supervised on embeddings |
| `uc20260930-proteingym-amfr-config-vespag` | none | supervised_machine_learning | Proposer's report, ProteinGym AMFR: VESPA, VESPAl and VespaG are supervised on embeddings |
| `uc20260930-proteingym-amfr-config-vespal` | none | supervised_machine_learning | Proposer's report, ProteinGym AMFR: VESPA, VESPAl and VespaG are supervised on embeddings |
| `uc20260930-msalign-v2-config-msalign` | none | foundation_model | MSAlign arXiv 2605.19752v2 abstract and Section 3 "Foundation model alignment" (p.4): aligns "two frozen foundation models (DreaMS for mass spectra and MolDeBERTa for molecules)" through trained MLP adapters |
| `uc20260930-msalign-v2-config-msalign-score-fusion-overbar` | none | foundation_model | MSAlign arXiv 2605.19752v2 abstract and Section 3 "Foundation model alignment" (p.4): aligns "two frozen foundation models (DreaMS for mass spectra and MolDeBERTa for molecules)" through trained MLP adapters |
| `msalign-2026-table3-method-msalign` | none | foundation_model | MSAlign arXiv 2605.19752v2 abstract and Section 3 "Foundation model alignment" (p.4): aligns "two frozen foundation models (DreaMS for mass spectra and MolDeBERTa for molecules)" through trained MLP adapters |
| `uc-clinical-20261005-hector-v1-2-config` | none | conventional_pipeline | HECTOR medRxiv v1, Materials and Methods, "Engine Design and ENIGMA V1.2 Implementation": evidence codes assigned against VCEP-defined thresholds and combined by ACMG/AMP rules and a point-based system; BayesDel and SpliceAI scores are inputs, HECTOR itself is not trained |
| `rna-pathogen-20261009-method-lshvec` | conventional_pipeline | supervised_machine_learning | Shi and Chen 2019 bioRxiv 10.1101/726729v1, Section 3.3 Taxonomy Classification (p.3): "taxonomy classification is supervised learning"; a one-layer softmax network trained on labelled reads over fastText skip-gram k-mer embeddings (Section 3.2) |
| `rna-pathogen-20261009-config-meyer2022-lshvec` | conventional_pipeline | supervised_machine_learning | Shi and Chen 2019 bioRxiv 10.1101/726729v1, Section 3.3 Taxonomy Classification (p.3): "taxonomy classification is supervised learning"; a one-layer softmax network trained on labelled reads over fastText skip-gram k-mer embeddings (Section 3.2) |
| `ucc-research-config-cppc-submission-row-18` | none | conventional_pipeline | CPPC Supplementary Note S1, GO_knn: the weighted average of the cell state proportions of the three most similar training perturbations; main-text Methods: "does not use an explicit predictor" |
| `ucc-research-config-cppc-submission-row-19` | none | conventional_pipeline | CPPC Supplementary Note S1, LowExp: proportions taken from the state annotations of the 5,000 training cells with the lowest expression of the gene |
| `ucc-research-config-cppc-submission-row-5` | none | foundation_model | CPPC Supplementary Note S1, scBERT: "extracts pretrained human gene embeddings from scBERT", described as "a large-scale pretrained deep language model" |
| `ucc-research-config-cppc-submission-row-2` | none | supervised_machine_learning | CPPC Supplementary Note S1, PPI_Weighted: features averaged over STRING-network neighbours, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-4` | none | supervised_machine_learning | CPPC Supplementary Note S1, 14Features: seven expression statistics on control and perturbed cells, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-6` | none | supervised_machine_learning | CPPC Supplementary Note S1, scVI: gene embeddings from an LDVAE trained on the challenge data, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-7` | none | supervised_machine_learning | CPPC Supplementary Note S1, Expression_Conditioned: each gene represented by its expression across training conditions, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-8` | none | supervised_machine_learning | CPPC Supplementary Note S1, Exon: exon-length summary statistics, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-9` | none | supervised_machine_learning | CPPC Supplementary Note S1, Gene2Vec: pretrained gene2vec gene embeddings, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-12` | none | supervised_machine_learning | CPPC Supplementary Note S1, 5Features: expression summary statistics and cell-state marker expression, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-16` | none | supervised_machine_learning | CPPC Supplementary Note S1, scETM: gene embeddings from scETM trained on the challenge data, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-22` | none | supervised_machine_learning | CPPC Supplementary Note S1, GO-node2vec: Node2Vec embeddings of the gene ontology, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-24` | none | supervised_machine_learning | CPPC Supplementary Note S1, GeneVector: pretrained GeneVector gene embeddings, then a fitted predictor |
| `ucc-research-config-cppc-submission-row-3` | none | supervised_machine_learning | CPPC Supplementary Note S1, GWPS_K562_H2M: "An MLP regressor with a single hidden layer of latent dimension 10 is then trained" |
| `ucc-research-config-cppc-submission-row-17` | none | supervised_machine_learning | CPPC Supplementary Note S1, "Implementation of additional methods": scTenifoldNet virtual knockout, then "trains a random forest classifier" to select genes |
| `ucc-research-config-cppc-submission-row-21` | none | supervised_machine_learning | CPPC Supplementary Note S1, Interv: LASSO cell-state classification and local LiNGAM regression |
| `ucc-research-config-cppc-submission-row-23` | none | supervised_machine_learning | CPPC Supplementary Note S1, Matrix_Completion: learns transformation matrices by minimising the Frobenius norm |
