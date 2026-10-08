# Ranking substitutions by folding stability for a target construct: bounded evidence research, 2026-10-08

Case 8 of 17 in the evidence programme ([rewire-benchmark-data #3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3); benchmark programme [rewire-benchmarks #25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), items B337 and BL337). Use case `use-case-protein-stability`, slug `protein-variant-stability`. The article issue is [rewire.it #337](https://github.com/rewire-bio/rewire.it/issues/337) ("[Article plan] Choosing models for protein variant stability"). It was resolved from repository evidence: `docs/omics/use-case-coverage-2026-09-30.md` links #337 to this use case, the 30 September audit comment on #337 describes the same mapping, and the issue body ends with "Use-case ID: `use-case-protein-stability`". The body has no `rewire-use-case-article-plan:` marker, only the `rewire-benchmark-development:2026-10-01` block.

Starting commit: producer `main` 0ad02f6f20d9b5481f96cfdd897074033b3cc1b1. No catalogue, mapping, definition, release, builder, test or generated file was changed. No model was run, trained or downloaded; no weights were fetched; no access was paid for, bypassed or requested. Times are UTC request starts from `workbench/protein-stability-20261008/retrieval-log.tsv` and `search-log.tsv` (ignored workbench). This is a research intake awaiting independent review, not a completed case.

## Disposition in brief

1. The existing immutable AMFR evidence stands (hashes below). It is on a mixed cohort and does not answer the article's singles-only question.
2. No singles-only AMFR number for any method was found in the stored records, the official ProteinGym table or the sources read here. The local ESM-2 8M and seed-0 random runs are separate protocols with no matched comparison.
3. The local ESM-2 8M result is one checkpoint size. In the official table the other ESM-2 sizes score higher on this assay, so it should not be read as a result for ESM-2 in general.
4. ProteinGym's stability panel was selected using observed evolutionary-model success. That limits what the panel can say about method classes (section 2). The direction and size of any resulting bias are not established.
5. AMFR (4G3O) is in the training list of ThermoMPNN's published Megascale split. Other Tsuboyama-trained models need their own target-specific audit.
6. In the bounded queries, no prospective prespecified-budget comparison of the requested method classes (language-model, evolutionary, physics-based) was found. Retrospective fixed-fraction and threshold-based measures exist.
7. Disposition: docs-only. No quantitative addendum is proposed. Codex posted the focused execution gap as [rewire-benchmarks #34](https://github.com/rewire-bio/rewire-benchmarks/issues/34) (reviewed body: fixed-budget stabilising yield and recall with threshold base rate and seeded random distribution, per-method inputs and delta definition, comparator training-set audit, coverage with doubles in a separate track, an independently selected panel, AMFR kept exploratory; planning only, no execution authorised).

## Existing inventory (unchanged)

Definition (`data/omics/use-cases/inputs.json`, `use-case-protein-stability`): decision "inspect the available AMFR assay results as a narrow example, then identify the missing singles-only comparison and validation required for the target protein and endpoint". Setting: 47-residue `AMFR_HUMAN_Tsuboyama_2023_4G3O`, ProteinGym v1.3, 2,972 variants (820 singles, 2,152 doubles). Exclusions: whole-protein function, cellular activity, organismal fitness and clinical pathogenicity; generalisation to other proteins or ESM-2 checkpoints; treating the mixed cohort as a matched singles comparison. Planned work is `blocked`.

Mappings: `use-case-mapping-protein-stability-amfr-esm2` (protocol `rewire-protocol-proteingym-amfr-v13`), `use-case-mapping-protein-stability-amfr-random` (protocol `rewire-protocol-proteingym-amfr-random-v13`) and `use-case-mapping-20260930-337-fa51fe46268a` (protocol `uc20260930-proteingym-amfr-protocol`, 97 official evaluations).

Stored results, protocols kept apart (all on the 2,972-variant mixed cohort, one run or seed each, no interval):

| Item | Local ESM-2 8M | Local seeded random |
|---|---|---|
| Configuration | `esm2_t6_8M_UR50D`, wild-type-context masked marginals summed over substituted sites, CPU, one thread; checkpoint SHA256 `46f002a9870c9bdecd0ea887acb1f9a38a6b561e8f8bf8a6990b679b9d31b928` | SHA256(seed:variant ID), seed 0 |
| Scored / eligible | 2,972 / 2,972 | 2,972 / 2,972 |
| Spearman, AUC, MCC, NDCG, Top_recall | -0.209, 0.394, -0.139, 0.440, 0.057 | 0.008, 0.514, 0.019, 0.526, 0.087 |
| Training overlap | unreported | none |

Locators and hashes (re-fetched 2026-10-08):

- ESM-2 report: [`research/local-runs-2026-09-20/proteingym-esm2/report.json`](https://github.com/rewire-bio/rewire-benchmarks/blob/ca73fa47136d182f2d4ddb083d084712198fc0e2/research/local-runs-2026-09-20/proteingym-esm2/report.json) at benchmarks commit `ca73fa47136d182f2d4ddb083d084712198fc0e2`, SHA256 `6a14b3866141d5779c76da8071d85c73b7cce0dc4e101c93122706873e847d26` (fetch 08:17:18). Values above are at `/protocol_results/per_assay/AMFR_HUMAN_Tsuboyama_2023_4G3O/metrics`. The random-control values were taken from the stored records `rewire-local-20260921-result-proteingym-random-*` and were not re-fetched from a receipt.
- ProteinGym reference file `reference_files/DMS_substitutions.csv` at commit `144fe22b07dfaeec2b366f2346203a9838a55b4c`, SHA256 `a8f498011532a74aa9fe556a50555a75e928c5837d19c06a87592ae04049b308`, row `DMS_index` = `DMS_sub_13`.
- Official Spearman table `benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv` at the same commit, SHA256 `f432423b87f79ac9778dfac86e3d95be041d246bc618dc0a406b35b0b7466437`, row `DMS ID` = `AMFR_HUMAN_Tsuboyama_2023_4G3O`; 97 model columns re-counted. Columns used here: `Site-Independent` 0.358, `EVmutation` 0.418, `ESM2 (8M)` -0.209, `ESM2 (35M)` 0.286, `ESM2 (150M)` 0.321, `ESM2 (650M)` 0.261, `ESM2 (3B)` 0.297, `ESM2 (15B)` 0.260. These are mixed-cohort values, and the columns have different inputs (sequence, alignment, structure), so they are not a like-for-like ranking. The `ESM2 (8M)` value equals the local run to three decimals; the stored evaluation keeps `published_score_reproduction: false` and nothing is changed.
- ProteinGym commit `144fe22b` is the head of `main` (committed 2026-03-25) and release `PG_v1.3` is the latest per its README.
- Tsuboyama primary full text (Europe PMC XML, fetch 08:13:58) SHA256 `3e759e2b4dc8140b6805d021c0c50ebbb543012efba5f0c701a54c072ab934ee`.

Doubles are 2,152 of 2,972 rows (72.4%) over seven site pairs, per the pilot plan. That is a row majority; whether doubles dominate a rank correlation was not examined.

The planned singles-only protocol (`docs/research/proteingym-amfr-pilot-2026-09-25/`) is exploratory, blocked at gates G0, G3 and G4, and has no result. Its plan states that AMFR mixed-cohort labels and results were seen before it was written and that label columns were not read for the singles. A singles-only decomposition of published scores is therefore deferred; no new execution is done here. The 25 September search did not locate an AMFR plmc model with verified provenance; that search was not repeated here.

## Search log (exact, dated)

Seven web searches in two batches; the remainder was direct retrieval (Europe PMC, GitHub API, Zenodo API, bioRxiv PDF, ProteinGym raw files). Batch times are the UTC clock reading taken immediately before each batch; queries inside a batch were sent together and are not individually timed. The retrieval log with per-request times is in the ignored workbench (`retrieval-log.tsv`); the exact queries are reproduced here so they survive checkout.

| ID | Batch start (UTC) | Mode | Exact query | Outcome |
|---|---|---|---|---|
| S1 | 2026-10-08T08:13:36Z | standard | `Tsuboyama 2023 mega-scale cDNA display proteolysis folding stability Nature 10.1038/s41586-023-06328-6` | primary confirmed, PMC10412457 |
| S2 | 2026-10-08T08:13:36Z | standard | `ProteinGym stability benchmark Tsuboyama zero-shot substitutions ESM-2 EVmutation 2026` | NeurIPS 2023 paper, repository |
| S3 | 2026-10-08T08:13:36Z | standard | `protein stability ddG prediction benchmark data leakage held-out proteins homology ThermoMPNN RaSP Stability Oracle` | candidates; split details read in primaries |
| S4 | 2026-10-08T08:13:36Z | extended | `2026 benchmark protein stability variant effect prediction mega-scale dataset homology-split top-k stabilizing mutations` | UniStab (PMC13458449) and others as candidates |
| S5 | 2026-10-08T08:18:04Z | standard | `zero-shot protein language model ESM-2 masked marginals folding stability Tsuboyama ddG Spearman compared with Rosetta FoldX evolutionary model` | no head-to-head retrieved |
| S6 | 2026-10-08T08:18:04Z | standard | `Beltran 2025 Nature site-saturation mutagenesis 500 human protein domains abundance PCA stability data availability` | Nature 2025, Zenodo 14356805 (summary level only) |
| S7 | 2026-10-08T08:18:04Z | extended | `prospective validation computational stabilizing mutation prediction hit rate experimental stability, top-ranked designs measured, protein language model vs FoldX Rosetta` | no prospective equal-budget comparison retrieved |

Inclusion rule: a primary source that reports measured stability (or a stability change) or a method evaluated against such measurements, with enough split, baseline or population detail to judge a ranking claim. Seen only as snippets or abstracts and not assessed: JanusDDG, ESMtherm, ABYSSAL, StableESM, DDGun, DVE-stability. Findings are bounded to these queries; no global absence or novelty claim is made.

Access events handled once each: a guessed bioRxiv DOI returned an unrelated paper and was discarded; the Rocklin-lab May 2026 press item returned HTTP 403 on two hosts and on WebFetch, so the Zenodo record and the preprint were read instead; the bioRxiv details API returned HTTP 500 (version 1 was taken from the PDF footer "posted May 20, 2026"); one duplicate cluster-file fetch is in the log.

## Findings

### 1. Tsuboyama et al. 2023 (assay primary)

Nature 620:434-444, [10.1038/s41586-023-06328-6](https://doi.org/10.1038/s41586-023-06328-6), PMC10412457, CC BY 4.0. Results, Discussion and Methods were read; Supplementary Notes and extended-data figures were not retrieved.

**What is measured.** cDNA display proteolysis with trypsin and chymotrypsin; K50 per sequence from sequencing counts under a Bayesian single-turnover model; ΔG from K50, an inferred unfolded-state K50,U and a universal folded-state K50,F. The authors state the assumptions (cooperative folding, equilibrium, accurate K50,U, cleavage that releases the cDNA, rates in range) and failure modes (cleavage from folded states, disulfide cross-linking, aggregation). This is proteolysis-inferred stability, not function, fitness or pathogenicity.

**Units, sign, range.** kcal/mol. The model equations refer ΔG to unfolding at pH 7.4 and 298 K (an inferred model reference); the caption of Extended Data Fig. 3 ("Relationship between offset in Fig. 1g and assay temperature") in the primary text (Europe PMC XML, SHA256 `3e759e2b4dc8140b6805d021c0c50ebbb543012efba5f0c701a54c072ab934ee`, read from the Codex root copy `workbench/codex-protein-review-20261008/tsuboyama.xml`) states "our measurements were all conducted in PBS at room temperature (approximately 22 °C)". The actual assay conditions and the model reference temperature are therefore distinct. Higher ΔG is more stable. The explicit ΔΔG equation is in the supplementary notes, which were not retrieved. The sign is taken from the Results statement that the median ΔΔG is -0.59 kcal/mol, "indicating that the wild type is typically more stable than an alternative amino acid", so negative ΔΔG is destabilising. ProteinGym keeps this sign (`raw_DMS_directionality` 1). The dynamic range is about -1 to 5 kcal/mol and values are clipped to it. The reported confidence intervals reflect sequencing counts only.

**Populations.** Only dataset 3 has tabulated ΔΔG (datasets 2 and 3 are quality-filtered scans); low-quality values are replaced by "-" in the `_ML` columns. Domains with wild-type ΔG above 4.75 kcal/mol (group 1) may not resolve stabilising variants. Double mutants were chosen by hand (polar interactions) or by a contact program with a random subset of common contacts, so doubles are not a random sample of interactions.

**Base rate and design comparator.** The authors report 2,600 mutations raising stability by at least 1 kcal/mol, a stabilising fraction of about 0.2% to 0.6% across protein types (Fig. 6a; population: filtered Tsuboyama scans; threshold: +1 kcal/mol in this source's sign). This is a base rate of a threshold in that population, not a hit rate for any method. For PROSS (727 designs on 172 domains with wild-type ΔG below 4 kcal/mol) the mean stability gain was 0.6 +/- 1.0 kcal/mol, and a single designed mutation averaged 0.2 +/- 0.5 (both are standard deviations across designs or mutations). The authors compare PROSS with the best single designed mutation, which it matched, and with the two best added together, which it did not. It evaluates a design method, not a ranking method.

**Evolution versus stability.** The authors fit a model relating stability to wild-type amino acid probability on 90 non-redundant natural proteins and conclude that evolutionary usage is shaped by factors other than stability (offsets for solubility, synthesis cost and function are discussed). This is why sequence-likelihood scores need separate validation as stability rankings.

**Access and reuse.** Zenodo [7992926](https://zenodo.org/records/7992926), version `v2_230420`, CC BY 4.0 (metadata fetch 08:14:06); the record asks users to register their use, which was not done; large files were not downloaded. Pipeline code `Rocklin-Lab/cdna-display-proteolysis-pipeline`: no licence reported by the GitHub API. The 30 September gap stays open: the Zenodo checksums cover zips, not the ProteinGym per-assay CSV (`dd911d925eca79329a496eb6cb7b181ab448e15db244daf1c1f9c01e8a704c2a`).

### 2. ProteinGym (benchmark primary and metadata)

Notin et al., NeurIPS 2023 Datasets and Benchmarks (PDF fetch 08:15:00, SHA256 `a3b08cc4a6befd64620cf0f287d78d55a36dc2639955f52c5655f83833c50104`; appendix "Processing of large thermostability dataset", `cache/pg-neurips-pdf/text.txt` lines 1768-1773) and the repository above; Zenodo [15293562](https://zenodo.org/records/15293562) (MIT), code MIT.

**Panel selection.** The paper says the Tsuboyama assays were restricted to non-redundant natural domains and that assays were removed "where none of the tested evolutionary models had a Spearman correlation above 0.2". So inclusion depended on observed evolutionary-model performance on the assay. Limitation: any comparison of method classes on this panel is conditioned on that selection, and a comparison that is meant to generalise needs an independent, unselected panel. The direction and magnitude of any bias were not established here. The 2023 text reports 65 thermostability assays; the current reference file lists 64 Tsuboyama assays and 66 `Stability` assays in total (the other two are not Tsuboyama). The difference and whether the current assays satisfy the same filter were not checked.

**AMFR entry.** `DMS_total_number_mutants` 2,972 = 820 singles + 2,152 multiples; `selection_assay` Stability; `selection_type` cDNA display proteolysis; `raw_DMS_phenotype_name` `ddG_ML_float`; `DMS_binarization_method` median with cutoff -1.5047; alignment `AMFR_HUMAN_2023-08-07_b04.a2m` (`MSA_num_seqs` 17,787, `MSA_N_eff` 1,245.9, `MSA_num_cov` 41). Binary metrics (AUC, MCC) therefore split the assay at its median, not at a stabilising threshold. Top_recall uses the top 10% of measured values, so a random ranking is expected near 0.10.

**Metrics.** Spearman, AUC, MCC, NDCG, top-10% recall; assays are averaged within function types and then across five types. The published standard errors are cross-model bootstrap errors over proteins, not intervals for one assay. The zero-shot setting has no split. The supervised cross-validation schemes (random, contiguous, modulo) are mutation- or position-level folds.

### 3. What the existing numbers can and cannot support

- Populations: the local ESM-2 run, the local random run and the official AMFR table all use the same mixed 2,972-variant cohort. The two local runs are distinct protocols, and the official table is a retrospective within-assay comparison on that shared cohort with heterogeneous method inputs. None is a matched singles comparison or a prospective fixed-budget test, and the planned singles study has no result. Differences between them are not evaluated winners.
- Chance variability: one seed, no interval. A random Spearman of 0.008 shows one ranking near zero, not the spread of random rankings on 47 positions.
- Equal-budget yield: Top_recall is a top-fraction recovery measure (top 10% of measured values captured by the top 10% of scores, mixed cohort). With a fixed fraction of a fixed cohort it fixes a shortlist size, but it is a retrospective mixed-cohort measure, not a prospective test with a prespecified budget for a target protein.
- Checkpoint and alignment: the ESM-2 checkpoint is hashed; alignment-based methods have no run here.

### 4. Specialist and supervised predictors: protocols, overlap, sign

These are candidate controls for a target construct. None was run. Each row describes the authors' own protocol.

| Source | Evaluation described by the authors | Held-out protocol (authors') |
|---|---|---|
| ThermoMPNN, Dieckhaus et al., PNAS 2024 ([PMC10861915](https://pmc.ncbi.nlm.nih.gov/articles/PMC10861915/)) | Single substitutions on Megascale data; transfer learning from pretrained ProteinMPNN with a trained head. A variant with ProteinMPNN unfrozen is reported as "Added fine-tuning" in Table 1; which variant the released model uses was not checked | MMseqs2 clusters at 25% identity, whole clusters assigned to train/val/test (239/31/28 proteins), homologue-free external sets |
| RaSP, Blaabjerg et al., eLife 2023 ([PMC10266766](https://pmc.ncbi.nlm.nih.gov/articles/PMC10266766/)) | Network trained on Rosetta-computed ΔΔG, checked against experiments | Structure training set filtered at 30% identity; experimental checks on selected proteins and public sets; reports failure of antisymmetry |
| Stability Oracle, Diaz et al., Nat Commun 2024 ([PMC11266546](https://pmc.ncbi.nlm.nih.gov/articles/PMC11266546/)) | Structure-based classifier of stabilising mutations | 30% identity splits; the authors argue mutation-, residue- and protein-level splits leak and that Pearson and RMSE do not suit finding stabilising mutations |
| UniStab, Chem. Sci. 2026 ([PMC13458449](https://pmc.ncbi.nlm.nih.gov/articles/PMC13458449/)) | ESM2-3B with a folding trunk; singles, doubles, indels; reports top-k% accuracy | Methods say it reuses ThermoMPNN's 25% clustering strategy; its actual train/test membership for 4G3O was not verified |
| SaProtΔG and ESM3ΔG, Cho et al., bioRxiv v1 posted 2026-05-20 ([10.64898/2026.05.19.726285](https://doi.org/10.64898/2026.05.19.726285); abstract, Results, legends read) | Absolute ΔG for 60 to 80 residue domains from a new MGnify Stability dataset; also compared on ThermoMPNN's Megascale test set | Training sequences below 30% identity to the authors' test set; on the ThermoMPNN test set 9 of 28 proteins exceed 0.3 identity to the authors' training set and are analysed separately. Preprint, CC BY-NC-ND. Data Zenodo [19411306](https://zenodo.org/records/19411306) (CC BY 4.0, access form); weights not accessed |
| Degn et al. 2025 ([10.1101/2025.03.28.645695](https://doi.org/10.1101/2025.03.28.645695)) | Rosetta, FoldX, RaSP, DDGun, ThermoMPNN on balanced subsets with AlphaFold2 inputs | Authors report lower performance on balanced subsets and after removing training-set homologues; preprint, not peer reviewed |

The authors' identity cutoffs (25% or 30%) are protocol choices of each paper, not guarantees of independence for another target.

**Training overlap for AMFR (4G3O).** ThermoMPNN's `dataset_splits/mega_splits.pkl` (commit `370f76ec62bd929f7425e311d8df04a0d094990f`, SHA256 `9e06230fe8febd8f07f8fab374f153328d4bdde20b78de15ead93b39e61ca1eb`) was inspected with `pickletools.genops`, which parses opcodes and executes nothing. The first key, `train`, is followed by a list of 239 distinct `.pdb` names (opcodes between the `train` key and the `val` key are only `EMPTY_LIST`, `MARK`, `APPENDS`, `MEMOIZE` and string opcodes) and that list contains `4G3O.pdb`; the count matches the paper's 239 training proteins. The pinned loader (`datasets.py` at the same commit, lines 78 to 79, 111 to 118) loads this file and treats it as "a dict with keys train/val/test and items holding FULL PDB names for a given split". `4G3O.pdb` also occurs in the later `cv_train_0` list. So, for ThermoMPNN's published split, 4G3O is a training protein. This was not cross-checked against `data_all/training/mega_train.csv` (not downloaded) or by unpickling. It says nothing about other models: any Tsuboyama-trained or MGnify-trained model needs an audit of its own training set against the target, and UniStab's and Cho et al.'s actual membership for AMFR is unverified.

**Sign and threshold, as explicit in the sources read.**

| Source | Explicit statement found |
|---|---|
| Tsuboyama / ProteinGym | Higher ΔG and `DMS_score` are more stable; median ΔΔG -0.59 means wild type is typically more stable. ΔΔG equation not retrieved |
| UniStab | "ΔΔG < 0 denoting increased stability" |
| Degn et al. (Fig. 5 legend) | Positive value is destabilising, negative stabilising |
| ThermoMPNN, Stability Oracle | A stabilising threshold of ΔΔG below -0.5 kcal/mol is stated; an explicit ΔΔG definition was not extracted |

Each comparison table must record, per source, the ΔΔG definition, sign, units and threshold, verified from that source.

### 5. Stability versus function and clinical meaning

Tsuboyama states that evolutionary usage and stability differ (section 1). A 2026 bioRxiv preprint, Deconvolving mutation effects on stability and function with disentangled protein language models ([PMC12889624](https://pmc.ncbi.nlm.nih.gov/articles/PMC12889624/)), was read at introduction level only. Beltran et al., Nature 2025 ([PMC11754108](https://pmc.ncbi.nlm.nih.gov/articles/PMC11754108/); data Zenodo [14356805](https://zenodo.org/records/14356805), CC BY 4.0) measures cellular abundance, a proxy that also reflects expression and degradation; it was read at summary level only. None of the sources read shows that AMFR stability predicts function or pathogenicity. The use-case exclusions stand.

### 6. Equal-budget candidate yield versus correlation

Almost every source reports correlation; few report ranking at the top (ProteinGym Top_recall, UniStab top-k% accuracy, Stability Oracle precision and recall, ThermoMPNN positive predictive value). Where they do, thresholds, test populations and base rates differ and are not reported side by side with a random-selection rate, so those values cannot be compared across sources or with random selection. In the bounded queries, no prospective prespecified-budget comparison of the requested method classes (language-model, evolutionary, physics-based) on a new protein was found; retrospective fixed-fraction and threshold-based measures exist. A search-result snippet cited a pooled FoldX success rate; the paper's abstract (Buß et al., [PMC6158775](https://pmc.ncbi.nlm.nih.gov/articles/PMC6158775/)) was read and the figure was not verified, so it is not used.

## Endpoint separation

| Source | Rank correlation with measured stability | Stable-variant classification | Top-k or top-fraction recovery | Absolute ΔG | Prospective measurement of a shortlist |
|---|---|---|---|---|---|
| Local ESM-2 8M, local random (AMFR, mixed) | Yes | AUC, MCC at median cutoff | Top_recall (top 10%) | | |
| Official 97 AMFR columns (mixed) | Yes | | | | |
| ThermoMPNN | Yes | Positive predictive value | | | |
| Stability Oracle | Yes | Precision, recall, AUROC | | | |
| UniStab | Yes | AUROC, AUPRC, F1, MCC | top-k% accuracy | | |
| SaProtΔG / ESM3ΔG | Yes | Yes | | Yes | |
| PROSS in Tsuboyama | | | | | Measured gain of designs (design method, not a ranking comparison) |

Transfer axes: unseen protein or cluster (ThermoMPNN, UniStab, Cho et al., Stability Oracle, each with its own cutoff) versus randomly held-out variants (ProteinGym supervised folds). Unseen combination: ProteinGym doubles, UniStab double-mutant sets. Measurement conditions are dataset-specific: the Tsuboyama assay is in vitro, with proteolysis in PBS at room temperature and ΔG referenced by the model to pH 7.4 and 298 K; the curated literature sets (for example Fireprot, S669, ThermoMutDB) and the other Cho et al. panels (thermophilicity, nanobody melting temperature, designs) have conditions that were not extracted here.

## Method-choice implications for a target construct

Conditions on the evidence, not a winner.

1. Fix the endpoint first: a ranking by measured ΔΔG, or a shortlist at a fixed budget with a stated threshold. They need different metrics and base rates.
2. Report singles and doubles separately, with scored and eligible counts per method and a common covered population.
3. Include controls: a seeded random distribution rather than one seed; the label-free site-independent evolutionary score and the full coevolution model if an alignment exists; a physics baseline; and, if a structure exists, a supervised predictor whose training set has been audited against the target.
4. Treat language-model scores as sequence likelihoods; name the checkpoint. AMFR shows size-to-size differences (section Existing inventory).
5. Claims about a new protein need held-out proteins, not held-out variants, and an independent, unselected panel for claims about method classes.
6. Do not move from stability to function or disease without a separate endpoint.

## Dedup of existing issues (open and closed, titles and bodies)

All issues listed at 2026-10-08T08:12:49Z with `--state all` were searched for proteingym, amfr, stability, tsuboyama, evcouplings, evmutation, esm-2/esm2 and the slug (rewire-benchmarks 15, rewire-benchmark-data 11, rewire-database 23, rewire.it 304).

| Issue | State | Relevance |
|---|---|---|
| rewire.it #337 | open | Article plan; one comment (30 September audit) |
| rewire-benchmarks #25 | open | Tracker; B337 and BL337: complete the planned pilot, declare singles separately, then register untouched proteins and a decision-endpoint protocol |
| rewire-benchmarks #13 | closed 2026-09-25 | Generic conventional-baseline triage; no AMFR execution |
| rewire-database #40 | closed 2026-09-25 | Pilot plan only |
| rewire-benchmark-data #3 | open | Programme tracker |
| rewire.it #114, #244, #299 | closed | ESM-2 profile, ProteinGym profile, variant-effect article; no stability execution scope |

No B337 execution issue exists (B334, B335, B336, B343, B345, B348 and B349 do). Codex then posted [rewire-benchmarks #34](https://github.com/rewire-bio/rewire-benchmarks/issues/34), linked to #25, programme #3 and rewire.it #337. Its reviewed scope is the one above; it does not restate the pilot plan's gates and makes no claim about any particular model's training membership or about panel bias.

## Access and reuse (separately)

| Item | Paper | Code | Data | Weights |
|---|---|---|---|---|
| Tsuboyama | CC BY 4.0 | pipeline repo, no licence in API | Zenodo 7992926, CC BY 4.0, registration requested | none |
| ProteinGym | NeurIPS PDF | MIT | Zenodo 15293562, MIT | none (model scores only) |
| ESM-2 | not re-read | `facebookresearch/esm` MIT, archived | UniRef50 | checkpoint URL in the stored receipt; not downloaded |
| EVcouplings / plmc | not re-read | EVcouplings MIT (Yale CNS `.inp` files excepted); plmc MIT | none for AMFR located by the 25 September search | none |
| ThermoMPNN | PNAS | MIT | splits in repo | in repo; not downloaded |
| RaSP | eLife | Apache-2.0 | in repo | in repo; not downloaded |
| Cho et al. 2026 | bioRxiv CC BY-NC-ND | repository not inspected | Zenodo 19411306 CC BY 4.0, access form | Hugging Face; not accessed |
| Beltran 2025 | Nature | not checked | Zenodo 14356805 CC BY 4.0 | none |

## Unresolved or unretrieved

- Singles-only AMFR scores for any method (deferred; see the pilot-plan note above).
- Whether the current 64 Tsuboyama assays satisfy the original selection filter, and why 65 became 64.
- Upstream authentication of the AMFR bytes.
- Cross-check of the ThermoMPNN split against the training CSV, and training membership of 4G3O in other models' splits.
- The Tsuboyama supplementary ΔΔG equation, the Cho et al. supplement, the Rocklin-lab press item (HTTP 403).
- Explicit ΔΔG definitions in the ThermoMPNN and Stability Oracle papers; UniStab top-k values; PROSTATA, SPURS and ThermoMPNN-D primaries.
- Beltran 2025 and the disentangled-language-model preprint beyond summary level.
- Prospective prespecified-budget comparisons of the requested method classes: none found by these bounded queries.
- Provenance of an AMFR plmc model (not rechecked).

## Intake disposition for independent review

- Docs-only. No change to definition, mappings, records, releases or builder. No new quantitative record proposed.
- Optional later items, each needing an owner decision: record 4G3O split membership after checking against the training CSV; a singles-only decomposition of published scores.
- Focused gap issue: posted by Codex as rewire-benchmarks #34 (not by this worker); the earlier ignored draft is superseded by the reviewed body.
- Bounded case disposition: docs-only, ready for Codex review; waiting for PR, CI and merge. Nothing is complete until then.

## Changed paths

- Added `docs/omics/evidence-research/protein-variant-stability-2026-10-08.md`.
- Ignored, untracked: `workbench/protein-stability-20261008/` (`intake-plan.md`, logs, `sources.tsv`, `cache-SHA256SUMS`, `cache/`, `scripts/`).
