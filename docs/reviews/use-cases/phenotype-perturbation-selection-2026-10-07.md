# Perturbation selection for a defined cellular response: bounded evidence research, 2026-10-07

Case 6 of 17 in the evidence programme ([rewire-benchmark-data #3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3); benchmark programme [rewire-benchmarks #25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), items B348 and BL348). Use case `use-case-phenotype-perturbation-selection`, slug `phenotype-perturbation-selection`. The article issue is [rewire.it #348](https://github.com/rewire-bio/rewire.it/issues/348) ("[Article plan] Choosing models for perturbations for a defined response"). It was resolved from repository evidence: `docs/omics/use-case-coverage-2026-09-30.md` links #348 to this use case, and the issue body carries the marker `rewire-use-case-article-plan:phenotype-perturbation-selection`.

Starting commit: producer `main` a41f7d73b7508cdf1245a6190f80764e1e1e9191. No catalogue, mapping, definition, release, builder, test or generated file was changed. No model was run, trained or downloaded. All times are UTC and are request start times from `workbench/perturbation-selection-20261007/retrieval-log.tsv` and `search-log.tsv` (ignored workbench).

## Disposition in brief

1. The existing immutable evidence (one prospective campaign and the Challenge 2 ranking score, both from the Cancer Immunotherapy Data Science Challenge, "CPPC") still stands. Re-fetched bytes match the 30 September audit: the full-text XML (`6c98a7d0...`), the pinned code README (`4c4cdf5c...`) and Table S2 (`ed480039...`). All 53 existing numeric results that cite Table S2 cells were re-checked against the workbook and none differs.
2. The denominator conflict (61 / 57 / 59 / 50) is not resolved. The counts 69, 57, 50 and the library count 61 are each described by primary bytes (below); the abstract's 61 and the README's 59 are not explained. No success fraction is computed here or implied.
3. No source read here evaluates a fixed-budget genetic-perturbation shortlist prospectively against random or conventional selection. The other sources are retrospective proxies, kept as separate endpoints.
4. Disposition: docs-only. The existing immutable evidence suffices; no new quantitative addendum is proposed. The B348 execution gap was posted by Codex after full open and closed dedup as [rewire-benchmarks #32](https://github.com/rewire-bio/rewire-benchmarks/issues/32), linked to #25, programme #3 and rewire.it #348. The ignored workbench draft is the pre-posting version.

## Existing inventory (unchanged)

Mappings for this use case in `data/omics/use-cases/inputs.json`: `use-case-mapping-20260930-348-15b6eed3fb55` (Challenge 2 original submissions, custom top-k overlap AUC, 20 evaluations, relevance direct) and `use-case-mapping-20260930-348-910458dfd409` (prospective nomination campaign, evaluation `ucc-research-eval-cppc-nominated-target-outcome`, hits Dimt1 and Ndufv2, relevance direct, denominator null). Records are in `data/omics/use-case-coverage-20260930/research/records.jsonl`. The 30 September log says the Table S2 comparison was extracted as numeric cells only and that no uncertainty is printed. Nothing below contradicts those records. The AMP worktree re-verified one CPPC cell for a different use case; it was read only.

## Search log (exact, dated)

Thirteen web-search queries in four batches, three Europe PMC search queries (all HTTP 503), and two PubMed queries. Times are batch or call starts; queries within one parallel batch are not individually timed. The first four queries carried a stray "Q1".."Q4" prefix by mistake; results stayed on topic. Full text in `search-log.tsv`.

| Time (UTC) | Tool | Query (abridged) | Outcome |
|---|---|---|---|
| 17:52:10 | web | Q1 inverse perturbation prediction benchmark, desired cell state, prospective | PerturBench, PertReason; no new selection endpoint |
| 17:52:10 | web | Q2 Perturb-seq prioritization ML hit rate, random selection, prospective | AssayBench-Loop/AssayLoop, ITERPERT, sequential OED |
| 17:52:10 | web | Q3 Virtual Cell Challenge 2025 metrics and baseline limits | secondary pages; Arc primary fetched later |
| 17:52:10 | web | Q4 Frangieh Perturb-CITE-seq SCP1064 | secondary pages; primary fetched directly |
| 17:52:24 | web | Q5 AssayLoop; Q6 AssayBench; Q7 (extended) Perturb-seq prospective nominated knockouts | confirmed arXiv 2609.11877, 2605.10876; no additional prospective-hit paper |
| 17:54:14 | web | Q8 GEARS desired-phenotype ranking; Q9 (extended) in silico screen validated T-cell hits; Q10 ITERPERT active learning | GEARS (case 4); "Closing the loop" preprint; ITERPERT excluded |
| 17:56:52 | web | Q11 (extended) TF or gene knockouts shifting T-cell state, validated; Q12 pertTF; Q13 Arc wrap-up (domain-limited) | CPPC again; resources and expression endpoints only |
| 18:00:29 to 18:00:36 | Europe PMC REST | Q14, Q14b, Q15b (boolean topic queries) | HTTP 503 each time; not repeated |
| 18:00:42 | PubMed esearch | Q16 (prospective ML-nominated CRISPR hits): 0 results. Q17 (virtual cell or perturbation prediction benchmark, phenotype or hit): 11 results | all 11 titles excluded: image phenotyping, reviews, expression or morphology prediction (SPARCS, Pop-Corn, pertTF and others); titles only |

Inclusion rule: a primary source that reports (a) measured genetic-perturbation outcomes for a phenotype or state objective and (b) a ranking or selection evaluated against them. Exclusion: expression reconstruction only, information-gain design with no hit objective, reviews, chemical perturbation. Findings are bounded to these queries.

## Findings

### 1. CPPC (primary source for the existing records)

Zhang, Schwartz, Mutaher, Olajide, Pritykin, Ashenberg, Hacohen, Uhler. bioRxiv [10.64898/2026.05.21.726863](https://doi.org/10.64898/2026.05.21.726863), version 1 posted 2026-05-22, PMC13228547, PMID 42239045. bioRxiv API at 17:52:44: version 1 only, `published` NA. Read in full: Results, Discussion, Methods (JATS XML from Europe PMC, 17:49:06) and the equations from the XML. Also read: Tables S1, S2, S3, and Note S1 (8 pages; searched for hyperparameter and run details, not read line by line); the pinned README, the GEO series record and guide reference files, and two pinned notebooks.

**System and decision.** Mouse in vivo: Cas9 x OT-I naive CD8 T cells, B16-OVA melanoma, tumour-infiltrating cells harvested at day 14, five states (progenitor, effector, terminal exhausted, cycling, other). Screen 1: 73 expert-chosen genes (70 curated plus 3 essential), 257 guides, 71,393 cells, 31,009 after QC. Screen 2: follow-up of algorithm nominations, 75,227 cells, 25,738 after QC.

**Objectives.** From the XML equations, with state order (progenitor a, effector b, terminal exhausted c, cycling d, other e): ICB objective f = a_i if d_i >= 0.05, else 0. CAR-T objective f = a_i/a_0 + b_i/b_0 - c_i/c_0 + d_i/d_0 if d_i >= 0.05, else 0. Control proportions in Screen 1 are (0.0675, 0.2097, 0.3134, 0.3921, 0.0173). A third, lower-confidence-bound objective (Challenge 3 winner) uses cell counts and was applied only after the screen.

**Candidate universe and nomination.** Challenge 2 asked for predictions on 15,006 previously untested genes (15,077 expressed minus 71). Nominations came from the Challenge 1 winning teams, not from a random or genome-wide draw. In Table S1 (sheet Screen2) each of nine team labels T1 to T9 appears for exactly six genes per objective (54 per objective; 67 distinct team-tagged genes; 32 retained genes are tagged for both objectives). That is consistent with a six-genes-per-team-per-objective budget, but the text does not state the rule. Two genes (Actg1, Tmsb10) are marked "Additionally added with late submissions" with no team.

**Denominator ledger (the 61 / 57 / 59 / 50 conflict).** Counts as described by primary bytes:

| Count | What it counts | Source |
|---|---|---|
| 69 | gene rows in Table S1 sheet Screen2 (67 team-tagged plus 2 late additions) | media-2.xlsx, rows 2 to 70 |
| 12 | of those flagged "Excluded (proteasome and ribosomal families)" | same sheet, notes column |
| 57 | 69 minus 12; matches Results ("57 target genes") and GEO design text ("57 target genes ... 3 guides per gene") | Results; GEO series record |
| 57 | genes with at least one post-QC cell in the author-run notebook output (identical gene set to the 57 above; 21,122 perturbed plus 4,616 NT cells = 25,738, equal to the Methods post-QC total) | pinned `data_screen2/split/split_anndata.ipynb`, cell 5 output |
| 50 | genes with at least 10 cells (the stated Screen 2 cutoff); seven fall below: Aurkb 1, Hspa8 1, Fcf1 2, Nol9 5, Tars2 5, Utp6 7, Wdr36 7 | Methods; same notebook, cell 6 output |
| 61 | distinct targeted genes in the Screen 2 guide reference (61 genes x 3 guides plus 30 non-targeting = 213 guides; plus 23 hashtag features) = the 57 above plus Actb, Psmb2, Rpl24, Rps18 | GEO `feature_reference_screen2_.csv.gz` |
| 61 | "top 61 genes nominated" in the abstract | abstract |
| 59 | "targeting 59 genes (screen 2)" in the README | pinned README |

What this ledger does and does not settle. Each count is described independently by the artifact cited. The abstract's 61 matches the number of targeted genes in the guide reference, but Table S1 lists 69 nominations and the four additional library genes are not retained nominations (Rpl24 and Rps18 are flagged excluded; Actb and Psmb2 are not in the sheet). The Screen 1 library also has a gene not listed in Table S1 (Eif4a3). The role of such library genes is not stated in the sources read. The README's 59 is unexplained. This dossier does not claim that the abstract's 61 or the README's 59 is reconciled, and no success fraction should be computed from any of these counts. Which denominator a hit rate would use is a protocol choice.

**Hit definition and the Table S3 filter.** Results state that Dimt1 and Ndufv2 have a higher ICB objective than all targets tested in Screen 1 (Figure 5A, B). That is a comparison against the 73-gene expert panel, not against a random or null draw. The notebook gives Ndufv2 28 cells and Dimt1 13 cells, against 4,616 non-targeting cells. No interval for either proportion is printed in the text read. Table S3 (media-4.xlsx) has "filtered Screen 2" ICB and CAR-T lists of 46 genes. Dimt1 is absent from both filtered lists and appears only in the unfiltered lists (rank 2 for ICB, rank 6 for CAR-T). The 46 listed gene symbols coincide with the notebook genes having at least 28 cells only after case normalisation: raw symbols differ for B430305j03rik (Table S3) against B430305J03Rik (notebook) and Mt-co3 against mt-Co3. This is an association in the data, not a stated or code-established filter, and it differs from the 10-cell statement in Methods. Pinned `data_screen2/notebooks/score_perturbations.ipynb` (`fb597411...`) contains explicit conditions: cell 8 builds `df_subset` with at least 26 cells per gene, and cell 11 applies cycling at least 0.05 for the ICB list. Its saved cell 11 output has 47 genes and includes Tfpt (27 cells), whereas the Table S3 filtered lists have 46 and exclude Tfpt. So the saved notebook output does not reproduce the Table S3 list exactly. The saved cell 13 CAR-T output (48 entries, including NT) also does not align with the current cell 13 source. These output and source discrepancies are observed; their cause is not diagnosed, and the exact published pipeline is not established. I did not execute or reconstruct the notebook, and I do not assume the split notebook and scoring notebook share the same cells or data state. The at-least-28 association is therefore not a filter mechanism, and the complete published scoring pipeline, and its relation to the Methods 10-cell statement, stay unresolved. The Dimt1 claim depends on that filter. Ndufv2 is rank 1 in the filtered ICB and CAR-T lists and in the unfiltered ICB list only; in the unfiltered CAR-T list it is rank 5.

**Baselines and comparators.** Discussion: most algorithm-proposed genes scored lower than the 73 expert-selected Screen 1 genes. There is no matched-budget random arm, no conventional-method arm in the prospective campaign, and no viability, selectivity or efficacy endpoint. The prospective result pools nominations from nine teams; it does not isolate any single method.

**Custom ranking AUC (Challenge 2).** Per the Methods text: fraction of the ground-truth top-k that appears in the predicted top-k, plotted against k/K over the K tested genes, area under the curve; expected 0.5 for a random ranking. It is computed within the nominated, Challenge-1-selected set only. Final score per submission is the minimum of two averages (filtered and unfiltered Screen 2) over three objectives. This is not ROC AUROC, not a hit rate and not efficacy. Table S2 column D has 20 numeric scores from 0.4517 to 0.5656 (17 above 0.5), no uncertainty. Column J (author reimplementation, post-hoc best model, trained on Screen 1 including the seven former Challenge 1 holdouts) has 13 numeric scores from 0.4803 to 0.6289 (11 above 0.5). Original and reimplemented scores must stay separate. Reimplementation: five runs per method with standard deviation shown in Figure 5C (figure only; not numerically extracted here).

**Splits and transfer.** Unseen gene: yes, Screen 2 genes are absent from Screen 1 (the 3-guide target sets do not overlap). Held-out response (Challenge 1): seven random held-out knockouts, three for validation and four for final ranking (Ets1, Fosb, Mafk, Stat3); cross-validation benchmark 6 folds x 5 repeats on 59 Screen 1 perturbations and 5 folds on 50 Screen 2 perturbations. Unseen combination: none (single knockouts only). New cellular context: none for selection; a public dataset in a different protocol (180 TFs, activated cells, day 7) is used only for the response-prediction benchmark. Training overlap: Challenge 1 winners saw Screen 1; selection of nominees used their Challenge 1 predictions; Screen 2 ranking evaluation re-trains on all of Screen 1.

**Independent units and guide efficacy.** Guides per gene: 3. Cells are pooled across mice; Screen 2 used hashtags per mouse (the guide reference lists 23 hashtag features; the number of mice is not stated in the text read). No per-mouse or per-guide analysis and no guide knockout efficacy readout were found in the text read. Supplementary figures S1 to S7 were not retrieved separately.

**Access and reuse (separately).**

| Item | Terms found |
|---|---|
| Paper | CC BY-NC-ND 4.0 (XML licence element; bioRxiv API `cc_by_nc_nd`) |
| Supplement | no separate licence stated; Table S2 contains named contacts and emails, which must not be copied into records |
| Code | repository `uhlerlab/cancer_immunotherapy_data_science_challenge`, pinned 283328a9b8af (still `main` head on 2026-10-07, last commit 2026-07-06); no repository licence (GitHub API `license` null; only a vendored scTenifoldpy LICENSE in the tree) |
| Data | GEO GSE327731 (public 2026-04-15, updated 2026-07-15); the record states no licence; GEO terms not read. Screen 2 `h5ad` is 2.49 GB and the RAW tar 2.25 GB; neither was downloaded |
| Weights | none identified for winning methods; the tree holds scETM checkpoint files (not downloaded); winning teams' code is in Google Drive (Document S1; not accessed) |

**Applicability.** Direct for the narrow decision "which mouse CD8 T-cell knockouts shift state composition toward a prespecified objective", with the limits above. Proxy for any other cell system, phenotype, guide set, combination or context.

### 2. AssayBench (retrospective hit ranking from screen descriptions; separate endpoint)

De Brouwer, Edwards et al. (Genentech), arXiv [2605.10876](https://arxiv.org/abs/2605.10876) v1, 2026-05-11 (main text read from the PDF; appendices searched, not read in full). Task (Section 3 of the extracted text): given a free-text screen description, return a ranked list of 100 genes; primary metric AnDCG@100, scored against hit labels harmonised from published BioGRID ORCS screens. Split (Section 2.3): temporal by publication year, 1,349 training, 218 validation and 334 test entries, plus 19 later "LaTest" screens. The held-out unit is the screen, not the gene, so this is retrospective recovery of published hits across screens, not prospective selection and not an unseen-gene split within one screen. The authors discuss possible memorisation by language models (Section 5.5). Terms: paper arXiv CC BY 4.0; code MIT (`Genentech/AssayBench`, head 552008a7 on 2026-09-30); Hugging Face dataset card MIT (revision fa2ed419), upstream BioGRID terms not verified; no weights. Applicability: proxy.

### 3. AssayBench-Loop and AssayLoop (retrospective adaptive hit discovery)

Edwards, De Brouwer et al. (Genentech), arXiv [2609.11877](https://arxiv.org/abs/2609.11877) v1, 2026-09-10. Problem formulation (extracted-text lines 147 to 165, with Fig. 2A): a policy selects a batch B_t of b genes in each of T rounds, observes their hit labels, and "the goal is to maximize the total number of discovered hits within the fixed budget T x b". This is adaptive hit discovery under a fixed experimental budget, so it is a hit-yield endpoint and not an information-gain endpoint; it matches the use-case decision except that the policy receives feedback between rounds, which is a separate protocol (one-shot shortlist versus sequential feedback) and not a reason to exclude it. Budget and splits: T = 10 rounds of b = 100 genes (1,000 acquisitions per screen; Fig. 2A caption); 1,389 screens split 1,349 training, 20 validation and 20 test (Fig. 2B; Section 4.2; Appendix A). Validation and test screens were filtered for genome-wide coverage, signal and a minimum language-model baseline score (Appendix A, criteria 1 to 5), so the test set is not a random sample. The held-out unit is the screen and labels are historical, so it is retrospective; the authors state that prospective validation was not done (Discussion). I did not establish the number of runs or intervals (Table 1 reports means over the 20 test screens). Terms: arXiv CC BY 4.0; code MIT (`Genentech/AssayLoop`, head e7251afa); AssayFormer weights on Hugging Face (`Genentech/assayformer`, revision 4927703e, card licence MIT; not downloaded). Applicability: retrospective proxy for prospective phenotype hit validation.

### 4. "Closing the loop" (retrospective hit classification; proxy)

Pershad, Bick and colleagues, bioRxiv [10.1101/2025.07.08.663754](https://doi.org/10.1101/2025.07.08.663754), PMC12265564, preprint, Europe PMC licence "cc by-nc-nd". Results sections "Benchmarking open-loop in silico perturbation predictions" and "Closing the loop": genes are predicted to shift T-cell activation in silico and classified against flow-cytometry hits from the Schmidt et al. CRISPRa and CRISPRi screens; metrics are PPV, sensitivity, specificity and ROC AUROC, which are different from top-k selection yield and from the CPPC custom AUC. The closed-loop model is fine-tuned on Perturb-seq data from the same Schmidt et al. study that supplies the flow ground truth (Methods, "Fine-tuning with T cell Perturbseq data"; Data Availability); the fine-tuning genes were excluded from evaluation, but the study and experimental system are shared. Hit counts and the significance rule were not retrieved. Applicability: proxy.

### 5. Frangieh et al. Perturb-CITE-seq (candidate data, not a selection evaluation)

Nature Genetics 2021, [10.1038/s41588-021-00779-1](https://doi.org/10.1038/s41588-021-00779-1), PMC8376399 (PMC HTML; the Europe PMC XML route returned 500). The paper reports a screen of 248 immune-evasion signature genes in one patient-derived melanoma model and evaluates no selection. Processed data are listed under Single Cell Portal SCP1064; downloads returned HTTP 401 and no sign-in was attempted; raw data are under controlled access (Data availability). The repository `klarman-cell-observatory/Perturb-CITE-Seq` has no licence in the GitHub API. Replicate structure, guide completeness and protein-readout hit definitions were not checked. Not usable as a benchmark panel until access and terms are confirmed.

### 6. Reviewed but not counted as selection evidence

Case 4 sources (Systema, PertEval-scFM, PerturBench, scPerturBench, Miller et al.; see `genetic-perturbation-response-2026-10-07.md`) address expression reconstruction and are not re-read here. GEARS (PMC11180609, text searched only) ranks gene pairs by genetic-interaction subtype in Norman data, a retrospective combination proxy owned by case 4. The Arc Virtual Cell Challenge 2025 wrap-up page (fetched 17:57:10) describes expression-based scoring (DES, PDS, MAE); the page text read has no hit-selection endpoint. ITERPERT and sequential optimal experimental design (Lyle et al.) choose perturbations to improve model accuracy and have no phenotype-hit objective; they were not read beyond abstracts. Genome-scale CD4+ T-cell Perturb-seq (bioRxiv 2025.12.23.696273), perturb-SHARE-seq TF screens (2026.04.20.718569) and pertTF (2026.03.12.711379) were seen at abstract level only and are not assessed here.

## Endpoint separation

| Source | Response or state-proportion prediction | Expression reconstruction | Custom ranking area | Retrospective hit ranking, enrichment or classification | Prospective phenotype hits |
|---|---|---|---|---|---|
| CPPC Challenge 1 | Yes (five state proportions, L1 error) | | | | |
| CPPC Challenge 2 | | | Yes (custom AUC, not ROC) | | |
| CPPC Screen 2 campaign | | | | | Yes (two named hits against the Screen 1 expert panel; pooled nominations) |
| AssayBench | | | | Yes (screens as units) | |
| AssayLoop | | | | Yes (adaptive, fixed budget, hit yield) | |
| Closing the loop | | | | Yes (PPV, AUROC) | |
| Case 4 sources, Arc challenge | | Yes | | | |
| ITERPERT | model-accuracy design, no hit objective | | | | |

Transfer axes: unseen gene is present in CPPC Screen 2 (and, within one study, in "Closing the loop"); unseen screen is the held-out unit in AssayBench and AssayLoop, not a matched candidate population. The core CPPC selection evidence is single-gene with no new cellular context. GEARS combination ranking remains a separate case 4 proxy.

## Unresolved or unretrieved

- README 59, the meaning of the abstract's 61, and which of 69, 61, 57, 50 or 46 would serve as a hit denominator.
- Why Table S3 "filtered" lists hold 46 genes and omit Dimt1, and how that relates to the Methods 10-cell statement. No pinned pipeline reproducing the published Table S3 lists is established, despite explicit at-least-26 and cycling conditions in the scoring notebook.
- Dimt1 rests on 13 cells; no interval printed. Mouse number, per-mouse and per-guide consistency, guide knockout efficacy: not found in text read; supplementary figures S1 to S7 not retrieved.
- Cell counts come from author-run notebook output, not recomputed from the 2.49 GB `h5ad`; Document S1 team code (Google Drive) and large repository data not accessed.
- Numerical Figure 5C means and standard deviations not extracted.
- AssayBench and AssayLoop: appendices and tables not read in full; interval and run-count reporting not established; the repositories are newer than the v1 papers.
- "Closing the loop" supplementary tables; Frangieh supplementary tables, SCP1064 terms and replicate structure.
- The literature search is bounded to the queries above; this dossier makes no claim about studies outside them.

## Bounded access failures

| Time (UTC) | Request | Result | Next approach |
|---|---|---|---|
| 17:49:44 | Europe PMC supplementary ZIP | stopped at 180 s with 6,391,315 bytes, no valid ZIP | retried 17:53:27 with 570 s limit: HTTP 500 |
| 17:54:56 | `europepmc.org/articles/PMC13228547/bin/media-3.xlsx` | HTTP 403 | bioRxiv `DC3/embed/media-3.xlsx`: HTTP 200, hash identical to 30 September |
| 17:55:59 | Europe PMC XML for Frangieh | HTTP 500 | PMC HTML: HTTP 200 |
| 17:56:34, 17:56:38 | SCP1064 download and stream | HTTP 401 | stopped; no authentication attempted |
| 18:00:29 to 18:00:36 | Europe PMC search (3 queries) | HTTP 503 | PubMed esearch |

## Cached bytes (ignored workbench `workbench/perturbation-selection-20261007/cache/`)

SHA-256 (all as retrieved 2026-10-07): CPPC XML `6c98a7d0f0ab7abff1c76a7f184382a10ca82c39b34879b83d205a994412aa22`; Note S1 `80ee7ad255296a5650247f06bb1915af12adf6644c2b619417d6940e77368e9b`; Table S1 `ecd9edabc11a3a58eb9d471b775172729c6c2837f75fe715af58e4c211e1a9d5`; Table S2 `ed480039c8008fdfcedaa50a8248d32df6068a9230a18ab6953ada5535865105`; Table S3 `474f84e719d7fefe73d371e9427c2cc14419402f97f255414b12b7c2a9f8636e`; bioRxiv API `7854c77e56ad1881b1e436ea16263897ce0037b289f036aca94fc913dc5fd415`; README `4c4cdf5c4e13502f6caa73f38b2be191a7cd2b3d601aef72a81a6d1223681f66`; screen 1 guide reference `d220dc609f7dc12b1341c7533acafe4ea736605b912188cb52d21c514ed472e3`; screen 2 guide reference `819d0ebecfbecfa73a93f7a424acea5dc513eca1f44e7acec69d2807b3cbbe1c`; GEO series text `04bc34ec64bc81487f75b7a4e051e79f06ee6a24d78c365e5616a0261ef671ff`; split notebook `7c1c6e52e0054026b2cc233bc29fa8b61c492de9e57ed40455aaff5889c33ce7`; scoring notebook `fb5974114381edc56e04acdea70686ee2f494b1cf54329ed9b8e509d3b6b87b6`; repository tree `e0e83bf049df5a340faa4d8c685ef1da36b670ef270a8aff3ccd1d3d0a151d34`; AssayBench PDF `805b402c28e0daa186415af202e04df56bf0cd7c7b1f872a6db170ee3c6c623d`; AssayLoop PDF `adcaaa5b7f9bd0e3bc1f91d94d26c8d4924c5c0b3064b6625c01ba92c6eaef28`; Closing-the-loop XML `e8762dd5a15d6785a98058d8b0700114a5f9355a7174b672279c1ffe159d6469`; Frangieh PMC HTML `d9db4763936c2774c13e2a36be6d67635a109d660ac2f79280d52ad62aca7189`; SCP1064 study metadata `abd92c4981c7afcf9a248b34933165ed1f4d76f1cc4acb52338f1a1235191151`; Arc page `82936795c79db9ff71b922f1cd1a3a10867e49b2ca14d33c8c6cedddd5fcf1c3`; GEARS XML `6e9a8f4a2b8ccbc9aa46c43a34701b687f71b797048adf27aae2a99d9e2dcad9`. The hashes of the Table S2 workbook, the CPPC XML and the README equal the 30 September audit values.

Scripts: `scripts/fetch.py`, `fetch_long.sh`, `jats2txt.py`, `xlsx_dump.py` (ignored workbench). Derived tables used above are reproducible from the cached bytes with those scripts.

## Review status

Automated source reading by the Sonnet evidence worker. Codex independently checked the primary CPPC XML and hashes, all 53 Table S2 cell-cited results, the Table S1 counts, the pinned notebook outputs and the guide-reference counts. No independent human scientific review, no model execution, no outreach. Disposition: docs-only.
