# Choosing rhodopsins or mutations to assay for a wavelength shift: bounded evidence research, 2026-10-08

Case 11 of 17 in the evidence programme ([rewire-benchmark-data #3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3); benchmark programme [rewire-benchmarks #25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), items B338 and BL338). Use case `use-case-rhodopsin-wavelength-transfer`, slug `rhodopsin-wavelength-transfer`, title "Assess rhodopsin wavelength prediction across sequence backgrounds". The article issue is [rewire.it #338](https://github.com/rewire-bio/rewire.it/issues/338) ("[Article plan] Choosing models for rhodopsin wavelength transfer"). It was resolved from repository evidence: `docs/omics/use-case-coverage-2026-09-30.md` links #338 to this title, the 30 September audit comment on #338 describes the same mapping, the issue body ends with "Use-case ID: `use-case-rhodopsin-wavelength-transfer`" and carries the `rewire-benchmark-development:2026-10-01` block for B338 and BL338, and `data/omics/amp-coverage-20261007/existing-b/research.md` links the same issue.

Starting commit: producer `main` 7b56891ff433133668be6f597a735d468e746618 (reviewed case 10 merge). No catalogue, mapping, definition, release, builder, test or generated file was changed, and the ten preceding dossiers are untouched. No model was run, trained or downloaded; no checkpoint, serialized model or restricted data was fetched; no access was paid for, bypassed or requested; downloaded code was not executed. Times are UTC request starts from the ignored `workbench/rhodopsin-20261008/` logs. This is a research intake awaiting root review, CI and merge; human scientific review is outstanding. It claims no new execution, replication or experimental validation.

## Independent review receipt

Independent root checks, all source-byte audits and not model execution: (a) a fresh Inoue Supplementary Data 1 workbook (327,518 bytes, SHA256 `55cd5d17b29a5ec50a377c23a0827b52d25d1d670dbddfacce97fd27419b39b0`), exact-sequence joined (884 rows, 878 unique sequences) to a fresh FLIP2 gzip, confirmed fit 584 rows from five WT groups (KR2 181, GR 134, GPR 126, BR 97, NpSRII 46), validation 116 rows from 34 groups and test 184 rows from 36 groups, with no exact sequence mapping to more than one WT label and fit and test WT labels separate; (b) a fresh ordinary curl of the design-preprint PDF (2,590,127 bytes, SHA256 `7328a4321d835cc0e0bef1cba30f190182ebf847fd688ddae4b121f81c42d1af`) matched this session's PDF, and its Methods and results confirmed the 490 nm target, seven selected by sequence distance, five forwarded by structure-confidence score, four cloned and about 410 nm reported. The root's normal-client HTTP 403 followed by an ordinary-curl HTTP 200 is recorded without any claim about the server's cause or any bypass. The narrowed distinctions below are unchanged: the five split files cannot establish the overlap of the paper's four test sets; a shared 884-row pool does not show that a particular RhoMax checkpoint was trained on every label; no correction history for any source was found or claimed; units, source conflicts and denominators are preserved as stated.

Independent root receipts (ignored `workbench/codex-rhodopsin-review-20261008/`) were compared with the files fetched in this session. Five files are byte-identical by SHA256: RhoMax XML (PMC11200256, 120,146 bytes), Inoue 2021 XML (PMC7979833, 159,582 bytes), the FLIP2 Rhomax gzip (18,449 bytes), Rhobot-Screen XML (PMC13445694, 190,731 bytes) and OPTICS XML (PMC13286010, 144,423 bytes). The hashes are given in full below. The root's Table 1 verification (60 numeric cells) and its confirmation of the Inoue counts (65 selected, 39 measurable, 32 red-shifted, 6 blue-shifted, 1 unchanged) agree with this dossier.

## Disposition in brief

1. The existing immutable evidence stands and is adequate for the current decision. The FLIP2 Rhomax counts (884 rows; 584 fit, 116 validation, 184 test) are re-confirmed from the archived file and the FLIP2 paper. The 60 RhoMax Table 1 cells match the stored values.
2. The stored local results were not re-fetched or re-run in this case. The values below are labelled as the previously reviewed stored claims. Both ESM-2 probes have negative Spearman on the 184 test rows while the composition controls are positive; this is one fixed-setting run per configuration with no interval, and it names no general winner.
3. FLIP2 states that the fit set is the five most common wild types (WT) and that 34 and 36 WT go to validation and test. The test WT are separated from fit WT by label only; homology between them was not measured.
4. The RhoMax repository holds five split files, whereas the paper reports four splits. The files are not mapped to the paper's splits, so nothing about the paper's four test sets (which WT, how many, how much they overlap, which five-minus-one were used) is inferred from the files.
5. Prospective evidence exists but not a matched-budget comparison. Inoue et al. 2021: 65 genes selected, 39 gave a measurable colour, 32 of those 39 red-shifted, 6 blue-shifted, 1 unchanged. The comparator is an assumed 0.50 null in a binomial test, not a randomized arm. A June 2026 preprint designed four proton-pump rhodopsins with a model whose authors describe training on a curated 884-rhodopsin set (read in full text; section 5). No exact training-file byte audit was done, so identity with the FLIP2 and Inoue 884 rows is not asserted.
6. In the bounded queries, no matched-budget comparison of sequence-only, structure-based and language-model methods on a new background was retrieved. This is not a global absence claim.
7. Disposition: docs-only. No scientific record, mapping or definition change is needed now. Optional quantitative extensions are future work, collected in the focused planning issue [rewire-benchmarks #37](https://github.com/rewire-bio/rewire-benchmarks/issues/37), posted by Codex after the reviewed dossier.

## Existing inventory (unchanged)

Definition (`data/omics/use-cases/inputs.json`, `use-case-rhodopsin-wavelength-transfer`): decision "use the existing held-out-background evaluations to choose controls and exact model configurations for a new, prospectively held-out spectral-tuning experiment". Setting: one complete FLIP2 Rhomax `by_wild_type` split, 584 training, 116 unused validation and 184 test records, endpoint peak absorption wavelength in nm. Exclusions include activation efficiency, expression, photostability, cellular function, zero-shot likelihood scoring, alternative pooling and fine-tuning not run. Planned work is empty. Nine evidence gaps are recorded, four of them 30 September audit notes (RhoMax splits not pooled with FLIP2, standard deviation is error dispersion, no prospective calibration or hit rate, Tables 2 and 3 not ingested).

Mappings: `use-case-mapping-rhodopsin-wavelength-rhomax-fixed-probes` (protocol `rewire-protocol-flip2-rhomax-by-wild-type-v1`, five evaluations) and the RhoMax mappings for split 1 to 4 and the printed mean (`uc20260930-rhomax-protocol-*`, with RhoMax, RhoMax plus retinal and BLASSO evaluations from source `uc20260930-source-rhomax-2024`). The AMP intake lists 6 protocols, 20 evaluations and 70 results, 69 numeric; the non-numeric one is the undefined training-mean Spearman, which is a valid outcome for constant predictions, not a missing value.

Stored FLIP2 Rhomax results (previous review; one run each, fixed settings, no interval; 184 of 184 eligible test rows scored; validation labels unused; not re-fetched here):

| Configuration | Spearman | NDCG (full ranking) | Training overlap field in the stored record |
|---|---|---|---|
| Training mean | undefined (constant predictions) | 0.9207 | none (no pretraining) |
| 40-feature composition + ridge | 0.4182 | 0.9548 | none |
| 22-feature composition + ridge | 0.4180 | 0.9548 | none |
| ESM-2 8M frozen residue-mean + ridge | -0.1464 | 0.8965 | unreported; UniRef50 pretraining may overlap |
| ESM-2 35M frozen residue-mean + ridge | -0.2218 | 0.9073 | unreported; UniRef50 pretraining may overlap |

Stored report SHA256 values: 35M `29d7c0ae7f47d45861a769eb8813bf8c650c9a95b3a6821c524b216b0b907ef0`, 8M `d6df9e916e77872112571b404265e918276974c79dcbe25721b3eca0eae4e51a`, 22-feature `2071ac2487d56df4150109b944a42944ed12e1398d00899c054580f709921317`, training mean `eb89260f6e138bb9ae2fdf3b882a87fdf8aeabd54a0ac6f17a73f5671c96b4d8`, 40-feature `abd08d3f493428d06f43740c94e268575d755560e72120c73b294127acb395e6` (commits `ca73fa47136d182f2d4ddb083d084712198fc0e2` for training mean and 40-feature, `1663d1f04b2bbd6dfcff77fea78129d30b0de191` for the others). The stored dataset record pins `source_csv_sha256` `8e78f6a16cd5298131dca83130d4b94cc0ab4ae9c699460880441c19a65f656f`, `source_sha256` `7c6d2f02cb89310378ac9897c321fbbd909fb0757ac88803dcce84f5f6b05ce3` and `prepared_rows_sha256` `d86fe3926529df72649f4638ffa0d89ec62460d831ceb62ad47ff86249469a12`. The 35M checkpoint was chosen after the 8M outcome was seen. NDCG is near 0.9 for every row including the constant control, so it does not separate these configurations; the stored note already says so. The negative ESM-2 rank correlations are results of these two frozen-embedding ridge probes and say nothing about ESM-2 in general or about other uses of its representations.

RhoMax Table 1 (author-reported absolute error in nm with the standard deviation of the absolute error, medians separately; source `uc20260930-source-rhomax-2024`, XML SHA256 `93814dd95c40cb109d592c2917728dc568c0445571e08180b188e726a4bd8f19`, re-fetched 2026-10-08T10:26:26Z and unchanged; eV values are stored beside them):

| Row | RhoMax median | RhoMax mean ± SD | RhoMax + retinal median | RhoMax + retinal mean ± SD | BLASSO median | BLASSO mean ± SD |
|---|---|---|---|---|---|---|
| split 1 | 5.20 | 8.85 ± 10.5 | 6.14 | 10.29 ± 12.2 | 9.94 | 10.58 ± 8.4 |
| split 2 | 3.40 | 7.28 ± 10.2 | 7.95 | 10.24 ± 9.3 | 13.55 | 13.89 ± 13.0 |
| split 3 | 5.32 | 8.98 ± 10.9 | 5.85 | 9.99 ± 11.6 | 10.12 | 10.10 ± 7.0 |
| split 4 | 13.40 | 16.68 ± 14.6 | 23.74 | 23.33 ± 13.7 | 25.70 | 25.02 ± 15.1 |
| printed mean row | 6.83 | 10.45 ± 11.6 | 10.92 | 13.46 ± 11.7 | 14.83 | 14.90 ± 10.9 |

The printed "mean" row equals the unweighted average of the four split rows (for example RhoMax median (5.20 + 3.40 + 5.32 + 13.40) / 4 = 6.83). It is a summary of four split results, not a pooled median over test sequences and not an independent experiment. The abstract says more than half of test sequences were within 0.03 eV and the Discussion says within five nanometres; three of the four split medians in Table 1 exceed 5 nm, and no pooled or per-sequence distribution was in the text read. The statements are kept as the authors' words and are not reconciled.

Units and training configuration. The paper's comparison section says the BLASSO model of Inoue et al. was originally trained in nanometres and that the authors "updated the code to support eV training"; its loss section defines the RhoMax loss as absolute error in nanometres, and a separate section says eV is the better unit and that results are given in both. The stored evaluation names call the BLASSO configuration an "eV-trained comparator". The sources read do not state, for each reported nm or eV column, which unit the model was trained in or whether one column is a conversion of the other. The exact per-unit training configuration is therefore uncertain, and both units are preserved as separately reported values.

## Search log (exact, dated)

Nine web searches in three batches, one Europe PMC structured query, one independent root search, and direct retrieval (Europe PMC XML, Zenodo API, GitHub API and raw files, PMLR, bioRxiv PDFs, publisher supplement). Batch times are the UTC clock reading taken immediately before each batch; queries inside a batch were sent together. Per-request fetch times and SHA256 values are in the ignored `retrieval-log.tsv`.

| ID | Batch start (UTC) | Mode | Exact query | Outcome |
|---|---|---|---|---|
| S1 | 2026-10-08T10:26:09Z | standard | `RhoMax rhodopsin absorption maximum prediction deep learning Journal of Chemical Information and Modeling 2024 10.1021/acs.jcim.4c00467` | primary confirmed, PMC11200256 |
| S2 | 2026-10-08T10:26:09Z | standard | `FLIP2 protein fitness landscape benchmark Rhomax by_wild_type rhodopsin absorption wavelength` | FLIP2 (ICML 2026, PMLR 306 didi26a); full text read |
| S3 | 2026-10-08T10:26:09Z | standard | `Karasuyama 2018 colour tuning rules predicting absorption wavelengths microbial rhodopsins data-driven machine learning Scientific Reports` | PMC6197263 |
| S4 | 2026-10-08T10:26:09Z | extended | `2025 2026 protein language model opsin rhodopsin lambda max prediction experimental validation novel spectral shift` | animal-opsin database and tool papers; no language-model plus measurement study |
| S5 | 2026-10-08T10:29:31Z | standard | `giant virus channelrhodopsin red-shifted machine learning model absorption maximum functional characterization bioRxiv 2025` | bioRxiv 2025.09.16.676488 |
| S6 | 2026-10-08T10:29:31Z | standard | `Accessible and Robust Machine Learning Approaches to Improve the Opsin Genotype-Phenotype Map bioRxiv 2025 phylogenetic non-independence` | bioRxiv 2025.08.22.671864 |
| S7 | 2026-10-08T10:29:31Z | extended | `microbial rhodopsin absorption wavelength prediction ESM embeddings OR "protein language model" OR transformer new rhodopsin spectral tuning 2025 2026` | no embedding-based wavelength study retrieved |
| S8 | 2026-10-08T10:30:20Z | standard | `ESM-2 embeddings OR zero-shot likelihood opsin lambda max OR "absorption maximum" prediction rhodopsin benchmark held-out family` | nothing relevant |
| S9 | 2026-10-08T10:30:20Z | standard | `machine learning designed rhodopsin mutants red-shifted experimentally validated hit rate absorption maximum 2024 2025 channelrhodopsin library` | Inoue 2021, giant-virus preprint |
| E1 | 2026-10-08T10:31:48Z | Europe PMC REST | `(TITLE_ABS:"rhodopsin" OR TITLE_ABS:"opsin" OR TITLE_ABS:"channelrhodopsin") AND (TITLE_ABS:"absorption maximum" OR TITLE_ABS:"absorption maxima" OR TITLE_ABS:"absorption wavelength" OR TITLE_ABS:"lambda max" OR TITLE_ABS:"λmax" OR TITLE_ABS:"spectral tuning") AND (TITLE_ABS:"machine learning" OR TITLE_ABS:"deep learning" OR TITLE_ABS:"language model" OR TITLE_ABS:"prediction") AND PUB_YEAR:[2024 TO 2026]` | 11 hits; Rhobot-Screen and journal OPTICS added |
| C1 | not recorded (independent root search; rough root time about 10:24:59Z to 10:27Z, not an exact request timestamp) | root web search | `rhodopsin wavelength prediction RhoMax benchmark new sequence backgrounds 2026` | candidate preprint "AI-enabled rhodopsin design for blue-light enhanced bacterial growth", DOI 10.64898/2026.06.29.735265v1, Europe PMC PPR1262821 |

Retrieval of the C1 candidate. The root reported HTTP 403 for `https://www.biorxiv.org/content/10.64898/2026.06.29.735265v1.full` with an ordinary client at about 10:27Z, after a web open also failed. The root's Europe PMC DOI search succeeded for metadata only. In this session a different ordinary path, the publisher PDF URL `https://www.biorxiv.org/content/10.64898/2026.06.29.735265v1.full.pdf`, returned HTTP 200 at 2026-10-08T10:40:22Z (SHA256 `7328a4321d835cc0e0bef1cba30f190182ebf847fd688ddae4b121f81c42d1af`, 2,590,127 bytes, 32 pages). No access control was bypassed. The Europe PMC DOI metadata record was also re-fetched at 10:40Z (SHA256 `29f8849a8e00131e0737a31417e1c3a14262fd2f1190c43af677fd948de10661`, identical to the root copy). Main text, Methods and discussion were read; supplementary information was not.

Inclusion rule: a primary source that reports a curated or measured wavelength label set, a prediction method evaluated against it, or a prospective measurement of selected or designed sequences, with enough split, assay or denominator detail to judge a transfer claim. Seen only as titles, snippets or abstracts and not assessed: Bedbrook et al. 2019, the ChR024 structure preprint (10.1101/2025.09.16.675330), the BCSJ 2026 review (HTTP 403 on fetch, not retried by another route), two 2026 Research Square preprints returned by E1 on conservation-divergence spectra and a protein language model (relevance not assessed), a JINR 2025 poster abstract and a 2025 Chrimson computational paper. Not read: RhoMax supplementary information, Inoue 2021 Supplementary Data 2 to 7, Karasuyama 2018 Supplementary Table 1 and its source-report list. Findings are bounded to these queries; no global absence or novelty claim is made.

## Findings

### 1. The label set: one lab-curated microbial table behind FLIP2, RhoMax and Inoue 2021

FLIP2's `rhomax/README.md` (Zenodo v3, SHA256 `a966bc2c519732861c85a6f7105268f0329e503fc9104c0b966d565314c80d28`) names the dataset as the Inoue et al. 2021 Communications Biology supplementary workbook ("Lab generated; first hand"). The workbook ([Supplementary Data 1](https://static-content.springer.com/esm/art%3A10.1038%2Fs42003-021-01878-9/MediaObjects/42003_2021_1878_MOESM3_ESM.xlsx), SHA256 `55cd5d17b29a5ec50a377c23a0827b52d25d1d670dbddfacce97fd27419b39b0`, also held byte-identical by the root) has 884 rows. The RhoMax repository workbook `excel/data.xlsx` (OpsiGen commit `a7f6ac3b302235fe22d972388d633d9bfdb439b8`, SHA256 `40f85bdd01b8f8fcbd2056dc7eddb7ad1fc4453b8f9e9406c5e18ea7965a27a3`) matches it row for row on name, wild type, sequence, wavelength and method columns. FLIP2 and RhoMax both describe 75 microbial (type I) wild types and their variants, 884 sequences in total. The three works therefore share one pool of labelled rows.

What a label is. A row is a mixed-source, mixed-method absorption maximum of an expressed, retinal-bound protein, in nm. Karasuyama et al. 2018 (Sci Rep 8:15580, PMC6197263) compiled literature values and the authors' own measurements by hydroxylamine bleaching of membranes from expressing cells or by purified protein, and deliberately excluded regenerated crude-membrane bacteriorhodopsin mutants whose values disagreed with purple-membrane values. Inoue 2021 added newly reported genes and measured candidates by hydroxylamine bleaching of E. coli membrane fractions. The workbook's `Method` column is mostly blank and its abbreviations are not defined in the text read. Temperature and illumination details for the stored labels were not extracted. Preprocessing choices that shape the domain include the restriction to transmembrane-region or retinal-pocket residues, per-subfamily base wavelengths, and the exclusion of candidates identical to a training sequence.

### 2. FLIP2 Rhomax by_wild_type (benchmark primary and archived file)

FLIP2 (Didi et al., ICML 2026, PMLR 306:24724-24777, [page](https://proceedings.mlr.press/v306/didi26a.html); PDF SHA256 `8a32ea5ce795c0790be7927a5c7698543c53dbf59fbd3be60c9b0bfabff707fb`; Zenodo [18433203](https://zenodo.org/records/18433203) v3, CC BY 4.0, 2026-01-30). Its Methods describe the Rhomax landscape as 884 variants from 75 microbial rhodopsin sequences with the task of predicting peak absorption wavelength, and the split as "Train on the 5 most common wild types and their variants; validate on 34 wild types and their variants; test on 36 wild types and their variants", with similar mean wavelength in each part.

Archived file `rhomax/by_wild_type.csv.gz`: gzip SHA256 `2d4bda268708bf2e161735bf77dd7ec503c233b42d4f4ab1abb3090eae6b6755`, 18,449 bytes (root copy identical); MD5 `286781669d083104cc399ae8a561afc5` equals the Zenodo-listed MD5; decompressed SHA256 `8e78f6a16cd5298131dca83130d4b94cc0ab4ae9c699460880441c19a65f656f` equals the stored `source_csv_sha256`. The stored `source_sha256` `7c6d2f02cb89310378ac9897c321fbbd909fb0757ac88803dcce84f5f6b05ce3` does not equal the gzip SHA256; what bytes it covers is unknown and no explanation is offered. Columns are `sequence`, `target`, `set` and `validation`; the file has no wild-type column. Counts: 584 fit rows (`set` train, `validation` false), 116 validation rows (`set` train, `validation` true), 184 test rows, 884 in total.

What this means for a transfer claim. The stored measurement fits on rows from the five most common wild types and scores rows from 36 other wild-type labels. Separation is by wild-type label only. Sequence homology between fit and test sequences was not measured, and the stored local record says the split is not a claim of homology separation. A rank correlation over the 184 pooled test rows mixes between-background and within-background ordering, and no per-background or per-distance result is stored. A natural-wild-type transfer test of this kind is a different endpoint from predicting the shift caused by a single point mutation within one background.

FLIP2 reports other configurations on the same partition under its own protocol (its Table A15). They are kept as separate protocols and not as a ranking of the stored local probes: for example one-hot ridge Spearman 0.327, ESM2-650M zero-shot likelihood -0.177 and CARP-640M likelihood 0.379. FLIP2 itself states that pLM choice is task dependent, that wild-type-split zero-shot performance can differ strongly between test sets and the full dataset, and that simple ridge models often match fine-tuned pLMs. The stored record describes the upstream published baseline as one-hot with target scaling on train plus validation rows and distinguishes it from the local train-only extension.

### 3. RhoMax (geometric model, original splits)

Sela, Church, Schapiro, Schneidman-Duhovny, J Chem Inf Model 2024, 64:4630-4639, [10.1021/acs.jcim.4c00467](https://doi.org/10.1021/acs.jcim.4c00467), PMC11200256, CC BY 4.0. Methods, Results, Discussion and Table 1 were read; Table 2 (feature ablations on split 1) and Table 3 (no attention layer) were seen and not ingested, as in the 30 September audit.

Inputs. AlphaFold2 structures (ColabFold, no templates) restricted to the 24 residues around the retinal, atom graph with distance-threshold edges; the plus-retinal variant copies the retinal from the closest homologue. The stored FLIP2 probes are sequence-only, so the inputs and protocols differ, and no AlphaFold2 exposure audit was done.

Paper splits (authors' text): four train/test splits, each with 65 wild types in train and 10 in test chosen randomly, with mutants kept with their wild type; test sizes differ because variant counts per wild type differ; the split does not guarantee similar wavelength distributions; accuracy is said to correlate with the similarity of train and test wavelength distributions. The paper reports the lowest accuracy on its split 4, whose test set is described as mostly red-shifted.

Repository split files (inventory only). The Data Availability statement names [dina-lab3D/OpsiGen](https://github.com/dina-lab3D/OpsiGen) (branch `colab`, head `a7f6ac3b302235fe22d972388d633d9bfdb439b8`, 2024-08-05; no licence reported by the GitHub API). `excel/splits/` contains `train0` to `train4` and `test0` to `test4` (each 65 and 10 wild-type names) and `train_all` and `test_all` (identical lists of 75 names, SHA256 `269ad539af28681f65c57265eb9b28318e7d96be83e6ef8e4835c8f16318265b`). That is five splits, not four. Test-file SHA256: test0 `448bfdc62cc672008feb0b42233a26651b8c53a6bbbbc0fdaafbbb1314b5d1e9`, test1 `34720103feaa4d5ad9545c11d3a3ac47dd90950c26b91b0f08373c41ff29adb6`, test2 `1eec0f392fc1b81626016cb262c9ccd5e5d0d20f9a834ebae2a234e869883b84`, test3 `225d857a5b8f0c7b632cbf7529cae820ea34eab42b9646b4ab3f6bbcd3e7b5ed`, test4 `d3ceca9dba734fb8b4226fd601a2d3d247c646f0c8b9ed1c2a29d3fd474b734c`. Train-file SHA256: train0 `6c4a88b0bd1ba4d05b9779c7607b5eac8e1d7eeb7e6860fc567fda79de8b0427`, train1 `64430e720a7348f55b80cafbed4007f1981f54f05b9cd6be8782eabf4b3152c9`, train2 `f5aa8af4afba1d06b8c68b4d819d6e84e8e17b67e93cf4d3b333ece0c3f1b0b5`, train3 `47a989581b5e11c437810db9e81a54abd2230d7631e3aa9a67a767dffd0bc712`, train4 `9ddaac522abfd3c92c18e6094ba2b35a08f29732875e382bb8ca05ca1e6583fe`. Within the files, each test list is disjoint from its own train list, and a given wild type can be in the test list of one file and the train list of another.

The paper does not say which of the five files correspond to its four reported splits, in which order, or whether one was dropped, and the repository does not either. No mapping is inferred, including from file contents or from which file looks red-shifted. Consequently, properties observed in the five files (for example that test lists of different files share wild types) are properties of those files only and are not carried to the paper's four test sets, to the printed mean row, or to any claim about which wild types were scored. The paper-level summary above and the file inventory are kept separate. This inventory is source metadata and cannot fill the exact-paper-protocol split-manifest gap recorded in the catalogue.

Other facts. The repository contains a pickled model (`predict/model_pickel`); it was not downloaded or inspected, so the training membership of any deployed checkpoint is unknown. The paper has no prospective experiment and reports no uncertainty beyond the standard deviation of the absolute error.

### 4. Training-label overlap and pretraining exposure (kept separate)

Three different things must not be merged.

1. Known: the Inoue 2021 screening model was fitted on all 884 rows (the paper states the training set as 884 sequences), so the FLIP2 test rows are part of that model's training data.
2. RhoMax: the paper's scores come from wild-type-grouped splits of the same 884-row pool, so each reported score comes from a model that did not see that split's test wild types. The shared pool does not show that any particular RhoMax model or checkpoint was fitted on every FLIP2 test label. Which rows the released or deployed checkpoint was fitted on was not inspected.
3. Unlabeled pretraining exposure of language models (for example ESM-2 and UniRef50) is a separate question. The stored records say overlap is unreported and the definition lists it as unresolved. This case did not look up sequence-database membership, did not run any model and infers no leakage or exposure effect.

Within FLIP2, the three parts share no wild-type label by construction. Whether other models named in the sources (the 2025 giant-virus model, the June 2026 design model, FLIP2's language-model comparators) were fitted on these rows is stated only where the source says so (section 5).

### 5. Prospective and experimental evidence (qualitative)

**Inoue et al. 2021 (Commun Biol 4:362, PMC7979833, CC BY 4.0; XML SHA256 `23672d74e7eb8d4f616433268896a0c3ac9b53ef87fcde3f75254b3df6f3d8f6`, fetched 10:29:09Z; independent root copy identical, retrieved 10:27:05Z).** A Bayesian sparse linear model trained on the 884 rows scored bacterial and archaeal ion-pump candidates without an identical training sequence and expressed 65 selected genes in E. coli with retinal. Of the 65, 39 gave substantial colour and had a wavelength measured by hydroxylamine bleaching; 26 did not. Measured against a per-subfamily base wavelength, 32 of the 39 were red-shifted, 6 blue-shifted and 1 unchanged. Four distinct denominators apply: 32 of 39 is conditioned on a measurable result; 32 of 65 is the count per selected gene; the 26 non-measurable genes are an expression outcome, not a spectral negative and not a measured miss; and the base wavelength is defined by the authors per subfamily. The authors compare 32 of 39 with an assumed random probability of 0.50 in a binomial test and state the real random rate is at most 0.50 by their choice of base wavelength. No random arm was measured, so this is discovery evidence for a shortlist, not a matched-arm yield comparison. Ion-transport assays on the largest red-shifts are function endpoints, not wavelength endpoints. The bioRxiv version (posted 2020-04-23, SHA256 `b1a096fa0b0d394952933759454ae6f31b00af087d4e78794dd96d4e12e5aae6`) reports different candidate and selection counts (66 selected, 40 coloured); the journal numbers are used, and the cause of the change was not established.

**June 2026 design preprint (found by the root search C1; Saeed et al., "AI-enabled rhodopsin design for blue-light enhanced bacterial growth", bioRxiv 10.64898/2026.06.29.735265v1, posted 2026-06-30, not peer reviewed, CC BY-NC 4.0).** Read from the PDF described above. The authors describe an in silico pipeline: a genetic algorithm proposes sequences, a stacked LASSO and gradient-boosted regressor predicts wavelength, and a sequence-plausibility filter keeps proton-pump-like candidates. The authors describe the regressor as trained on a curated set of 884 microbial rhodopsins, citing the same curated source; this dossier did not audit the training file, so exact row identity with the FLIP2 and Inoue 884 rows and the trained membership of any row are not asserted. The preprint itself notes that the table contains dense clusters of closely related variants that can inflate shuffled cross-validation, and reports tail-held-out and wild-type-grouped cross-validation as additional checks. Candidates were designed far from the training sequences. Selection for the laboratory was by sequence distance and a structure-confidence score among filter-passing candidates, not by ranking predicted wavelength; seven were chosen, five went forward and four were cloned and expressed. All four designed proteins were measured by hydroxylamine bleaching of E. coli membrane fractions, at about 410 nm in the authors' account, and promoted growth of Cupriavidus necator under blue light. The text describes the genetic-algorithm target for the selected runs as 490 nm and notes that measured values were bluer than predicted. This is a prospective experimental test of a design pipeline, with no measured random or baseline arm and no held-out-background wavelength-error comparison. It is also a function-bearing endpoint (growth) separate from wavelength. Supplementary information was not read. Its numbers are not promoted.

**Other microbial work (qualitative).** A bioRxiv preprint (2025.09.16.676488, posted 2025-09-17, CC BY-NC 4.0, not peer reviewed; PDF SHA256 `e9f83174649941ff76a868ffc5abecd4d78af2fc102810ac7a866dce5ff2b204`) applied an elastic-net model to new channelrhodopsin homologues and tested a small selected set in mammalian cells; the text reports expression failures for a majority of the selected genes, with inconsistent counts in two places, and reports photocurrent and kinetics endpoints for its top gene that are separate from wavelength. Rhobot-Screen (BMC Biol 2026, PMC13445694, CC BY-NC-ND 4.0; XML SHA256 `f1269abe19f8761622541903ee7236298b9887f3ba96bc382f39527d7e69608e`, fetched 10:31:55Z; root copy identical, independently fetched 10:33:29Z) describes an automated 96-well platform that measures wavelength by hydroxylamine bleaching without purification, demonstrated on single substitutions at three colour-switch sites of one proton pump, with some variants unmeasurable because of low expression. It is an experimental capability, not a prediction benchmark; its variants were not compared with the training table. None of these is used for a number here.

### 6. Animal (type II) opsins: separate scope

The use-case definition, FLIP2 Rhomax and RhoMax are microbial only. Animal opsin work uses different databases, labels and checks and is outside this use case. The Visual Physiology Opsin Database (VPOD; GigaScience 2024, PMC11512451, CC BY 4.0) and OPTICS (bioRxiv 2025.08.22.671864, SHA256 `0c87719b9d82ae3efcec5fcc05eabd514331a4cbb999cbbc31edbbe7f267ac90`; journal Mol Biol Evol 2026, PMC13286010, XML SHA256 `8ea79e9f1db30b0935028758ae07e341d4eed73539d8a59bb2dd127a6f287b58`, fetched 10:32:02Z; root copy identical, independently fetched 10:33:29Z) compile heterologously expressed animal opsin wavelengths, add physiologically measured values, and argue that ordinary random cross-validation overestimates generalisation because related sequences are not independent. The authors link published sequences to in vivo wavelengths using a match threshold on the model's own prediction, a label-source rule that selects retained labels by model agreement; the threshold and counts differ between the preprint and the journal version. Nothing read links a microbial-trained wavelength model to animal opsins or the reverse, and no animal-opsin number is used in this dossier.

## Endpoint separation

| Source | Absorption-maximum regression | Transfer to unseen WT or family | Uncertainty reported | Fixed-budget shift-hit yield | Function or kinetics |
|---|---|---|---|---|---|
| Stored FLIP2 local probes (previous review) | Spearman, NDCG on 184 rows | unseen WT labels, fit on five | none | none | none |
| FLIP2 paper | Spearman, NDCG | same partition | seed spread for fine-tuned runs only | none | none |
| RhoMax / BLASSO | absolute error in nm and eV | four reported WT-group splits | standard deviation of the absolute error (error dispersion, not parameter or run variability, not calibration) | none | none |
| Karasuyama 2018 | mean error on one held-out family (KR2 group) | one named family | none beyond mean error | none | none |
| Inoue 2021 | predictive mean and variance | candidates not identical to training | Bayesian predictive distribution; coverage not evaluated here | 32 of 39 measurable, 32 of 65 selected; no measured random arm | ion transport for the largest shifts |
| June 2026 design preprint | cross-validation variants | designed far from training | not extracted | no baseline arm; selection not by predicted rank | growth under blue light |
| Rhobot-Screen | measured wavelength of single variants | one background | replicate spread | not a prediction test | animal module is a different readout |

Units and signs: FLIP2 uses nm; RhoMax reports nm and eV (energy scales inversely to wavelength, so a red shift lowers eV); Inoue 2021 reports signed gain in nm against a per-subfamily base wavelength; Rhobot-Screen reports signed energy change. A shift hit needs the base wavelength, sign, unit and tolerance fixed before two sources are compared. Expression failures are not spectral outcomes.

## Method-choice implications for a target construct

Conditions on the evidence, not a winner.

1. Fix the endpoint first: absolute wavelength in a new background, rank within a candidate pool, or a shortlist hit above a stated shift from a named base wavelength. They need different metrics and denominators.
2. Name the population: microbial or animal; natural wild types, point variants of one background, or chimeras; expression host, retinal supply, assay method and conditions. Do not mix heterologous and in vivo labels without a stated rule.
3. Keep free controls: the training mean (rank correlation undefined, so report error), composition ridge and one-hot ridge.
4. Treat structure-based and sequence-only inputs as separate tracks.
5. Claims about a new background need held-out backgrounds not used for fitting, a stated identity measure and the number of backgrounds. A pool of five fit backgrounds and many test backgrounds with few rows each limits what a pooled correlation shows.
6. For shortlists, register the budget, criterion and how unexpressed constructs are counted, and compare with a measured random or base-rate arm.
7. Language-model scores are likelihoods or embeddings; name the checkpoint and report unresolved pretraining exposure rather than assuming it either way.
8. Do not move from absorption maximum to pumping, gating, kinetics, expression, photostability or optogenetic suitability without a separate endpoint.

## Dedup of existing issues (open and closed, titles and bodies)

All issues listed at 2026-10-08T10:25:35Z with `--state all` (rewire-benchmarks 18, rewire-benchmark-data 11, rewire-database 23, rewire.it 304; comments included) were searched for rhodops, rhomax, opsin, flip2, wavelength, spectral, optogen, channelrhodops, bacteriorhodops, the slug, B338, BL338 and #338.

| Issue | State | Relevance |
|---|---|---|
| rewire.it #338 | open | Article plan; two comments (30 September emphasis, 30 September audit) |
| rewire-benchmarks #25 | open | Tracker; B338 and BL338 (target-wavelength selection and calibrated uncertainty on independent backgrounds). Not a focused equivalent |
| rewire-benchmark-data #3 | open | Programme tracker; parent only |
| rewire.it #351, #365 | open | Article series and AMP coverage trackers |
| rewire-database #27 | open | Roadmap; mentions FLIP2 and Rhomax |
| rewire.it #260 | closed | FLIP2 benchmark article; no wavelength execution scope |
| rewire.it #71, #266, #335; rewire-benchmarks #31 | mixed | Keyword hits only (profiles, MS/MS) |

No B338 execution or planning issue exists in rewire-benchmarks (B334, B335, B336, B337, B341, B343, B345, B347, B348 and B349 do). Parent #25 is not a focused equivalent. After the all-state title and body dedup, Codex posted the focused planning issue [rewire-benchmarks #37](https://github.com/rewire-bio/rewire-benchmarks/issues/37) (B338). It links rewire-benchmarks #25, rewire-benchmark-data #3 and rewire.it #338, authorises planning only, acknowledges the prospective discovery evidence above and makes no blanket novelty or absence claim. The ignored `issue-B338-draft.md` is the superseded worker draft; #37 is the reviewed body.

## Access and reuse (separately)

| Item | Paper | Code | Data | Weights |
|---|---|---|---|---|
| Inoue 2021, Karasuyama 2018, RhoMax, VPOD, OPTICS (journal) | CC BY 4.0 | OpsiGen: no licence reported by the GitHub API | Inoue Supplementary Data 1 (Springer); VPOD on GitHub | OpsiGen has a pickled model, not downloaded |
| FLIP2 | PMLR proceedings (licence not extracted) | not inspected | Zenodo 18433203 v3, CC BY 4.0 | none (third-party pLM checkpoints) |
| 2025 giant-virus and 2026 design preprints | CC BY-NC 4.0, not peer reviewed | not checked | supplements not read | none |
| Rhobot-Screen | CC BY-NC-ND 4.0 | not checked | source data not retrieved | none |
| ESM-2 | not re-read | not touched | UniRef50 | not downloaded |

## Unresolved or unretrieved

- Mapping of the paper's four RhoMax splits to the five repository files, and therefore the exact paper-protocol split manifest and per-split test sizes.
- RhoMax supplementary information, Inoue 2021 Supplementary Data 2 to 7 (including the genes that did not express), Karasuyama 2018 Supplementary Table 1 and its source reports, the meaning of the `Method` abbreviations, the supplement of the June 2026 design preprint.
- Per-unit training configuration of the nm and eV columns in RhoMax Table 1.
- Pairwise sequence identity between FLIP2 fit and test sequences; sequence-database membership relevant to language-model pretraining; AlphaFold2 exposure.
- Per-sequence RhoMax errors and predictions; training membership of any deployed RhoMax checkpoint.
- Scope of the stored `source_sha256` of the Zenodo CSV; differences between preprint and journal versions of Inoue 2021 and OPTICS.
- BCSJ 2026 review (HTTP 403), Bedbrook 2019, the ChR024 structure preprint and the two Research Square preprints.
- A matched-budget comparison of sequence-only, structure-based and language-model methods on a new background: none retrieved by these bounded queries.

## Intake disposition

- Docs-only for this bounded intake. The existing immutable comparison (the five stored FLIP2 evaluations and the 60 RhoMax Table 1 cells, with their recorded limits) is adequate for the current decision, and no new scientific record, mapping or definition change is needed now.
- Earlier optional record ideas (a derived wild-type composition record, a prospective-counts protocol, a split-file inventory record) are withdrawn from this intake. Any such additions are future extensions that belong to the planning issue below, not unresolved work, and require no approval to leave the case as it is.
- Focused gap issue: posted by Codex as [rewire-benchmarks #37](https://github.com/rewire-bio/rewire-benchmarks/issues/37) (planning only, no execution authorised); not posted by this worker.
- The case awaits root review, CI and merge; human scientific review is outstanding. Nothing is complete until then. No benchmark execution or laboratory validation is implied.

## Changed paths

- Added `docs/omics/evidence-research/rhodopsin-wavelength-transfer-2026-10-08.md`.
- Ignored, untracked: `workbench/rhodopsin-20261008/` (`intake-plan.md`, `issue-B338-draft.md`, `retrieval-log.tsv`, `search-log.tsv`, `cache-SHA256SUMS`, `cache/`, `scripts/`). The root's `workbench/codex-rhodopsin-review-20261008/` was read only.
