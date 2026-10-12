# Method-type corrections: independent review, 2026-10-12

Batch: `data/omics/method-type-corrections-20261012/`. Its `report.md` is the preparer's account and describes the batch before this review. It applies the method-type tag fixes listed in the use-case baseline review (`docs/reviews/use-cases/baselines-2026-10-12.md`, "Method-type tag fixes for a separate reviewed PR"). The batch has a staged correction table (`corrections.csv`), one `metadata-correction-tags-20261012-*` claim per edit keeping the previous value, and new source records.

Reviewer: a separate Claude review agent that did not prepare the batch. No human review is claimed. Nothing was run or reproduced. This is a check of each edit against the baseline review, the store and, for a sample, the cited source.

## Outcome

- 246 edits were proposed. 245 are approved and applied with `npm run records:correct`; 1 is withdrawn (CPPC row 23, below).
- 26 of the approved claims were corrected before approval: the evidence locator in 11, the note in 12, and the cited sources in 25 (most in more than one way). No new value was changed except by the withdrawal.
- The two proposed source records are approved. One more source record was added for CPPC Supplementary Note S1, which the CPPC edits cite but no record pinned.
- All 248 batch records are `source_checked` and added with `npm run records -- add`.
- No judgement, summary or baseline is withheld by these edits, so nothing was re-pinned (see "Pins").
- Seven use cases change their same-data machine-learning-versus-baseline answer. One evidence-gap sentence was added (tumour RNA fusion). No existing gap sentence became false.

## How the check was done

1. Compared every row of `corrections.csv` with `origin/main` (168dce9) and the working store: each `old_value` is the record's only current method type, or empty where the record has none. All 246 matched. No record appears twice.
2. Matched every edited record to a row of the baseline review's two tag tables, or to a documented source check where the review made a row conditional (EricScript, MSAlign, HECTOR, LSHVec) or "per named method" (CPPC, ProteinGym AMFR). The only record outside the tables is PROVEAN (3 records), which the review names in the SIFT row ("The same applies to PROVEAN").
3. Checked that every claim's `previous_value`, `value` and `source_locator` match its CSV row, and that no claim or source ID already exists.
4. Checked each new value against the definitions in `data/vocab/method-type.ttl`. `foundation_model`: large model pretrained on broad data and adapted to downstream tasks; here this includes frozen embeddings with a fitted probe, as for the existing ESM-2 and UCE configurations. `supervised_machine_learning`: a task-specific model trained on labelled data. `conventional_pipeline`: an established non-foundation-model workflow with no trained component here (rules, lookup, alignment, deconvolution by least squares or EM, docking). `specialist` is no longer used for any of these records.
5. Re-retrieved the cited source for 97 edits across 21 sources (below), compared its SHA-256 with the source record and read the cited passage. The other 148 edits were checked against the store: the tags of the records the locator names and the record's own description.
6. Rebuilt the same-data comparison table from `deriveUseCaseInputs` with the rule used in the baseline review, before and after the edits.

## Sources and hashes

| Source | Edits | Hash | Passage checked |
| --- | --- | --- | --- |
| scTab (PMC11298532 XML) | 9 | matches | scGPT zero-shot: a logistic regression on frozen scGPT embeddings; UCE "evaluated ... in the linear probing setting"; CellTypist retrained; XGBoost, MLP, linear model |
| Abdelaal 2019 (PMC6734286 XML) | 4 | matches | Table 1: SVM (linear kernel), SVM rejection, scPred (SVM with radial kernel), scmapcell (kNN) |
| MSAlign v2 (arXiv 2605.19752v2) | 5 | matches | Abstract and Section 3: "two frozen foundation models (DreaMS ... and MolDeBERTa ...)" with MLP adapters; late score fusion; Baselines and Table 1 for DeepSets, JESTR, Emb-Cos |
| MSAlign v1 (arXiv 2605.19752v1) | 6 | matches | Section 5.1 Baselines and Table 1: FFN and DeepSets are fingerprint predictors; JESTR, Emb-Cos and SAIL use InfoNCE losses |
| MassSpecGym (arXiv 2410.23326v1) | (with the MSAlign rows) | matches | Section 4.1: Fingerprint FFN "employs a feedforward neural network to predict the Morgan fingerprint"; DeepSets |
| Jores 2021 (PDF) | 4 | matches | p849: "We initially used a linear regression model"; then "a machine learning approach using a convolutional neural network" |
| RhoMax 2024 (PMC11200256 XML) | 3 | matches | BLASSO: "A first attempt to utilize machine learning"; retrained "on the same data set splits"; GNN |
| FramePool 2021 (PMC8136849 XML) | 10 | matches | Optimus CNNs "were trained"; "random forest models on 3-mer and 4-mer counts" |
| Benelli 2012, EricScript (OUP page) | 2 | matches (see below) | Section 2.6: "we trained an AdaBoost classifier"; Section 2.6.4: trained with synthetic data, gives the EricScore |
| Ramadane 2025 (PMC12120176 XML) | 3 | matches | "the meta-predictor BayesDel" |
| OncoVI (PMC13269341 HTML) | 3 | live page, differs as expected | "On the basis of an IF-ELSE implementation" |
| Chen 2020 (PMC7033911 XML) | 8 | matches | Table 1: SIFT "Position-specific scoring matrix"; PROVEAN "Delta alignment score" |
| Sun 2024 (PMC11660681 XML) | 9 | matches | MethAtlas by NNLS; CelFiE by "an expectation-maximization (EM) algorithm"; CelFEER and UXM benchmarked |
| Wang 2026 (PMC13353424 XML) | 1 | matches | "ichorCNA-TF, which uses TF inferred by ichorCNA ... as input to a logistic regression binary classifier" |
| DNALongBench (PMC12627797 XML) | 1 | matches | the expert model is ABC, "which incorporates DNase-seq, H3K27ac ChIP-seq data, and a Hi-C matrix" |
| LiPP (PMC13292216 XML) | 2 | matches | "one AI-based docking tool (DiffDock-L)"; "Trained on complexes in PDBbind before 2019" |
| MPRAbc (PMC13232518 XML) | 6 | matches | ABC "is a mathematical framework"; MPRAbc "trained within the ENCODE-rE2G framework" |
| ClusPro BM5 (PMC7484347 HTML) | 2 | live page, differs as expected | FFT rigid-body docking |
| HECTOR (medRxiv v1 HTML) | 1 | live page, differs as expected | "Engine Design and ENIGMA V1.2 Implementation": VCEP thresholds, ACMG/AMP combining rules and points; BayesDel and SpliceAI are inputs |
| Shi and Chen 2019, LSHVec (bioRxiv v1 PDF) | 2 | differs; bioRxiv stamps each download | Section 3.3: "taxonomy classification is supervised learning"; one-layer softmax over k-mer embeddings |
| CPPC Note S1 and Table S2 (Europe PMC supplementary archive) | 16 | Table S2 member and article XML match; Note S1 had no record | Note S1, all named methods; Table S2 columns A to D and G to K |

Benelli et al. 2012 is "All rights reserved" (OUP). OUP refuses scripted downloads, so the article was rendered in Chrome and the `innerText` of `.article-body` hashed, as the source record's `hash_scope` describes. It gave the same 44,359 bytes and the same SHA-256. DOI, volume 28, issue 24, pages 3232-3239 and the dates match Crossref. Nothing from the article is archived; the batch holds only short quotations in locators.

The LSHVec preprint is CC-BY-NC-ND 4.0, as recorded. bioRxiv rewrites the PDF modification date on every download, so a re-download never reproduces `artifact_sha256`. The source's `hash_scope` now says so. DOI, posting date and authors match Crossref.

## Corrections made in review

| Records | Change | Reason |
| --- | --- | --- |
| `ucc-research-config-cppc-submission-row-23` | Withdrawn; stays untagged | Its only stored result is Table S2 cell D23 (Challenge 2). The Table S2 footnote "*" says "an alternative method was used for challenge 2". Note S1 describes Matrix_Completion, not that method, so the source does not say what produced the score. |
| 16 CPPC submission rows | Note rewritten; Note S1 source added | Note S1 describes the authors' reimplementation from the submitted write-ups and code. The batch's note read as if it described the submission. The write-ups themselves (Document S1, on Google Drive) were not read. |
| `ucc-research-config-cppc-submission-row-5` (scBERT) | Locator | "a large-scale pretrained deep language model" is the title of Note S1's reference 7, not Note S1's own text. |
| `uc20260930-msalign-v2-config-{deepset,emb-cos,jestr}`, `msalign-2026-table3-method-{deepsets,emb-cos,ffn,jestr,sail}` | Locator; MSAlign v1 and v2 sources added | The batch cited "MassSpecGym Supplementary" for Emb-Cos and JESTR, which MassSpecGym does not describe, and did not cover SAIL. They are described in MSAlign Table 1 and Baselines. |
| `ucc-research-config-abdelaal-scmapcell` | Locator; note | The quoted description was not in the source. Abdelaal Table 1 lists scmapcell as "kNN". `conventional_pipeline` is kept; `supervised_machine_learning` is also defensible, and it is a baseline row either way. |
| `lit-genomics-20261011-dnalongbench-config-abc` | Locator; MPRAbc source added | DNALongBench does not say ABC has "no training step". |
| `method-type-corrections-20261012-source-shi2019-lshvec` | `hash_scope` | Records that bioRxiv stamps each download. |

## Decisions on the conditional rows

- **EricScript**: approved as `supervised_machine_learning`. The candidate fusions are ranked by a trained AdaBoost score. EricScript is still an alignment-based caller; the fusion use case now says so (below).
- **MSAlign** (3 records): approved as `foundation_model`. MSAlign trains small adapters on two frozen foundation encoders. The score-fusion row combines several alignment scorers, two of which use both encoders. The `+Filter` variants (`uc20260930-msalign-v2-config-msalign-score-fusion-filter-overbar`, `msalign-2026-table3-method-msalign-plus-filter`) are not in the baseline review and stay untagged.
- **HECTOR**: approved as `conventional_pipeline`. It applies the ENIGMA criteria; its predictors are inputs.
- **LSHVec** (2 records): approved as `supervised_machine_learning`. Section 3 of the preprint labels the read classifier "(unsupervised)", which Section 3.3 contradicts; the claim notes this. The peer-reviewed ACM BCB 2021 version was not read.
- **CPPC** (16 of 23 submission rows): GO_knn and LowExp are `conventional_pipeline` (no fitted predictor). scBERT is `foundation_model` (frozen pretrained embeddings with a fitted regressor). PPI_Weighted, GWPS_K562_H2M, 14Features, scVI, Expression_Conditioned, Exon, Gene2Vec, 5Features, scETM, scTenifoldNet, Interv, GO-node2vec and GeneVector are `supervised_machine_learning`: a predictor is fitted on Screen 1 (main-text Methods, Figure 2A). scTenifoldNet is mixed (a random forest selects genes; proportions come from simulated knockouts). Rows 10, 11, 13, 14, 15 and 20 are not benchmarked and Table S2 says only that each is "similar to" Expression_Conditioned, so they stay untagged, as does row 23. The reimplemented-row configurations are not in the baseline review and are unchanged.
- **ProteinGym AMFR**: 83 of the 97 configurations are tagged from their model records, as the proposer's report sets out. These were checked against the store only; this comparison has no baseline row. The 14 per-family and alignment-based models (EVE, DeepSequence, EVmutation, GEMME, RSALOR, Site-Independent, SiteRM, TranceptEVE, Wavenet, ESCOTT) stay untagged, as the baseline review's gap on per-family models says. The preparer flagged that ProteinMPNN is tagged `foundation_model` here while one other ProteinMPNN configuration in the store is `supervised_machine_learning`. It is kept: ProteinGym uses it zero-shot, as it does ESM-IF1, which is also `foundation_model`. The inconsistency is listed under remaining gaps.

### Not checked against a source

These rest on the store and record descriptions only, as the baseline review already marked: BayesDel `method` link consistency, the manual ENIGMA curation, Exomiser, Talos, DRAGEN, the Samarakoon Parabricks DeepVariant configuration, the CIViC GPT-5 and Qwen3 configurations, MedCPT, Kraken2, the Giuili Houseman and EpiDISH configurations, the 24 Feng Enformer, Sei and AlphaGenome configurations (Feng not read; the store's Enformer, Sei and other AlphaGenome configurations are `supervised_machine_learning`), FoldBench, AgroNT, the Drost splice-predictor vote, the MFASS SpliceAI and Pangolin configurations, the Rewire FLIP2 probes and ESM-2 probes, and ProteinGym AMFR.

## Personal data

CPPC Table S2 columns E and F, and the contact sheet "Challenge 3", hold contributors' names and personal emails; column G holds personal submission links. None of their values appears anywhere in the repository (checked with `git grep` for every value). This review read Table S2 only from columns A to D and G to K and quotes none of G.

## Pins

Pins cover use cases, protocols, sources, evaluations, results and claims, not configurations, so a facet change cannot withhold a judgement, summary or baseline. `deriveUseCaseInputs` before and after the edits withholds the same mappings, all for reasons that predate this batch, and publishes all 26 baselines and the same 24 summaries. Nothing was re-pinned.

## Same-data machine-learning versus baseline

Comparisons with both a baseline row and a machine-learning row, by the rule in the baseline review:

| Use case | Before | After | Machine-learning rows that now count |
| --- | --- | --- | --- |
| Cell-type annotation transfer | 0 | 2 | scTab protocol: scGPT (fine-tuned and zero-shot), UCE, CellTypist, CIForm, MLP, scTab, XGBoost. Abdelaal Baron: scPred. |
| Mass spectrum shortlisting | 0 | 3 | Emb-Cos, JESTR, MSAlign and MSAlign score fusion on the three MSAlign v2 protocols |
| Plant promoter reporters | 0 | 2 | Jores CNN on both protocols |
| Regulatory variant follow-up | 1 | 2 | MPRAbc K562: ENCODE-rE2G, MPRAbc full, MEGAMAP, MPRALegNet and Sei models beside ABC |
| Rhodopsin wavelength transfer | 0 | 5 | RhoMax and RhoMax + retinal on all five splits |
| Tumour RNA fusion | 0 | 2 | EricScript on the Tamura all-fusion and driver-fusion comparisons |
| UTR translation | 0 | 2 | FramePool and Optimus 5-Prime on both protocols |

No other answer changes. In structural hypotheses, DiffDock-L now also counts in the lipid comparison, which already had a machine-learning row.

None of the 10 existing gap sentences becomes false. The six use cases that the baseline review left without a sentence because of tags now have a comparison. For tumour RNA fusion, the baseline review asked that the use case say what that comparison is, so this sentence was added to `evidence_gaps` with `records -- change`:

> The only machine-learning method compared with STAR-Fusion or Arriba on the same data in the linked evidence is EricScript (Tamura et al. 2026), an alignment-based caller that ranks its candidates with a trained AdaBoost score; no caller that learns fusion detection itself is compared.

## Remaining gaps

- The baseline review's other proposed fixes are not in this batch: `configuration_of` links for the DRAGEN, AgroNT-CNN and baseline configurations it lists, and splitting the multi-caller Samarakoon and O'Connell configurations.
- Method records `ctdnameth-20261009-method-{celfeer,uxm,houseman-cp,epidish-rpc}` remain `specialist` while their configurations are now `conventional_pipeline`.
- The original CPPC write-ups were not read, so the CPPC tags describe the authors' reimplementation of each submission.
- One ProteinMPNN configuration outside ProteinGym AMFR is `supervised_machine_learning`; the AMFR ones are `foundation_model`.
- `specialist` still does not say whether a method is learned.
