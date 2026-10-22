# Literature search: lead optimisation, ranking analogues by binding affinity

Scope: lane `interactions`, proposed use case `lead-optimisation-affinity-ranking` (rewire-benchmark-data #178).
Search window cutoff 2026-10-22. Budget 25 queries; 24 used, logged as 23 ledger entries
`search-leadopt-20261022-s1` to `-s23` (`-s18` covers two GitHub API endpoints in one step). Two of the 24
were failures (bioRxiv HTTP 403, Europe PMC HTTP 500), both recorded as gaps rather than as absence of
evidence. Searcher: Claude research agent; no human review claimed.

Endpoint this pass was looking for: **correlation and error against measured affinities for analogues of the
same hit, within one target's congeneric series.** A correlation pooled across unrelated targets is recorded
below as a proxy and labelled as such.

No result, evaluation or use-case records were created. This is a search and screen pass only.

## Candidates worth extracting

### C1. Boltz-2 preprint supplement (developer-reported)

| Field | Value |
| --- | --- |
| Primary source | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12262699/supplementaryFiles` -> `NIHPP2025.06.14.659707v1-supplement-1.pdf` |
| Version / DOI | bioRxiv v1 posted 2025-06-18, doi 10.1101/2025.06.14.659707; supplement PDF SHA-256 `be867a5d92add8b223d47d882a4213ad489741f3e4d5081a0901a54370342569`; the page banner states CC BY 4.0 |
| Exact tables | Table 11 (OpenFE subset of the FEP+ benchmark); Table 12 (4-target subset, includes a per-method `time` column); Table 14 (CASP16 competition against the top-6 participants); Table 15 (hit-to-lead validation set); Table 16 (8 blinded Recursion assays). All in appendix E.2 |
| Series or target set | T11: OpenFE subset of the Ross 2023 FEP+ benchmark, 876 protein-ligand complexes. T12: CDK2, TYK2, JNK1, P38; 87 neutral compounds curated in the protein-ligand-benchmark (Hahn 2022), ligand set attributed to "Chen et al., 2023". T14: CASP16 L1000 chymase and L3000 autotaxin |
| Measured endpoint and units | Measured affinities of the Ross 2023 collection (Kd, Ki, IC50 converted to kcal/mol); CASP16 is IC50 |
| Per-target or pooled | **Target-averaged.** Columns are labelled "target avg.", meaning the mean of per-series values. The per-series values themselves are not printed (scatter plots only, Figure 12) |
| FEP arm on the same series | **Yes.** T11: OpenFE and FEP+. T12: OpenFE, FEP+, ABFE, FMO, MM/PBSA, Chemgauss4 |
| Stated leakage control | `mmseqs easy-cluster --min-seq-id 0.9 --cov-mode 0 -c 0.01`; any training protein in a cluster shared with a validation or test protein is removed. Not applied to CASP16 (released after the training cutoff) or to the Recursion assays (proprietary). Compound-level check in Figure D.2.1; max Tanimoto to training 0.41 (L1000), 0.59 (L3000) |
| Authors developed the method | **Yes** (Boltz developers) |

Printed values, for orientation during extraction:

- Table 11, OpenFE subset: Boltz-2 Pearson 0.62 and Kendall tau 0.46 (target avg.); Boltz-2 ipTM -0.07 / -0.05;
  GAT 0.28 / 0.20; BACPI 0.29 / 0.19; OpenFE 0.63 / 0.47; FEP+ 0.72 / 0.53.
- Table 12, 4-target subset, with the paper's own compute column: Boltz-2 0.66 / 0.48 at 20 GPU seconds;
  Boltz-2 ipTM 0.04 / 0.09 at 5 GPU seconds; BACPI 0.14 / 0.09; GAT 0.40 / 0.28; OpenFE 0.66 / 0.51 at
  6-12 GPU hours; FEP+ 0.78 / 0.63 with time printed as "-"; ABFE 0.75 / 0.54 at above 20 GPU hours;
  FMO 0.55 / 0.38 at 2-10 CPU minutes; MM/PBSA 0.18 / 0.16 at 10-15 CPU minutes; Chemgauss4 0.26 / 0.17 at
  20-30 CPU seconds.
- Table 14, CASP16: Boltz-2 0.65 / 0.45 against the best participant LG016 at 0.54 / 0.42.

### C2. Ross et al. 2023, the FEP+ baseline

| Field | Value |
| --- | --- |
| Primary source | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10576784/fullTextXML`, *Communications Chemistry* 6:222 |
| Version / DOI | doi 10.1038/s42004-023-01019-9; PMC10576784; CC BY 4.0; XML SHA-256 `f371d2e373306588d11b695b8de21b253a90293d6a15884f635bcf927bdebb1d` |
| Exact tables | Table 3 (FEP+ accuracy beside experimental reproducibility); Table 2 (the data sets, their proteins and compound counts); Table 1 (the assay-reproducibility survey) |
| Series or target set | The assembled public FEP benchmark: FEP+ R-group (8 proteins, 199 compounds), charge-change (53), OPLS stress (114), water displacement (76), fragments (79), macrocycles (34), scaffold-hopping, Merck sets and others; over 50 targets and over 1200 ligands of congeneric series |
| Measured endpoint and units | Kd, Ki and IC50 converted to relative binding free energies in kcal/mol, under the paper's stated assumption that IC50, Ki and Kd **ratios** are interchangeable |
| Per-target or pooled | Table 3 prints weighted averages over series (weight = compounds, or edges for the edgewise errors) with bootstrap 95% CIs. Per-system values are in the Supplementary Results and in the repository, not in the paper's tables |
| FEP arm on the same series | **It is the FEP arm.** FEP+ pairwise RMSE 1.25 [1.17, 1.33] kcal/mol, pairwise MUE 0.98 [0.91, 1.05], edgewise RMSE 1.17 [1.08, 1.25], edgewise MUE 0.91 [0.84, 0.98], R² 0.56 [0.51, 0.60], Kendall tau 0.51 [0.48, 0.55]. The experimental-survey column (pairwise RMSE 0.91, MUE 0.67, R² 0.79, tau 0.71) is the achievable ceiling |
| Stated leakage control | Not applicable: no training. **The FEP+ protocol was tuned per system after observing the error against experiment, so this is a maximum-attainable rather than prospective baseline.** |
| Authors developed the method | **Yes** (Schrödinger authors evaluating FEP+) |

### C3. Gilson et al. 2025, CASP16 protein-ligand assessment

| Field | Value |
| --- | --- |
| Primary source | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750038/fullTextXML`, *Proteins* |
| Version / DOI | doi 10.1002/prot.70061; PMC12750038; CC BY; cover date January 2026; retrieved 2026-10-22 |
| Exact tables | Table 1 (systems, affinity counts, affinity ranges). The affinity ranking results are in figures, with the headline values in the text |
| Series or target set | CASP16 L1000 chymase (17 affinities, range 1-400 nM) and L3000 autotaxin (stage 1: 123, stage 2: 93; range 1 nM-10 µM), both contributed by F. Hoffmann-La Roche |
| Measured endpoint and units | IC50 |
| Per-target or pooled | Per-target Kendall tau per group, in figures. Official per-target results: `https://predictioncenter.org/casp16/results.cgi?tr_type=ligand` |
| FEP arm on the same series | No FEP arm. Participants used a mix of ML and physics methods, not separated into arms in the assessment |
| Stated leakage control | Blind challenge; affinities withheld until after submission. Stage 2 supplied experimental structures and did **not** improve affinity accuracy |
| Authors developed the method | **No** (independent assessors) |

Headline values: maximum Kendall tau achieved across participants 0.42, against an estimated achievable
ceiling of about 0.73 derived by resampling with an assumed IC50 error of a factor of 3 (0.66 kcal/mol), with
a 2 kcal/mol variant also reported.

### C4. Warren et al. 2025, AEV-PLIG

| Field | Value |
| --- | --- |
| Primary source | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11807228/fullTextXML`, *Communications Chemistry* |
| Version / DOI | doi 10.1038/s42004-025-01428-y; PMC11807228; PMID 39922899; CC BY 4.0 |
| Exact tables | Table 1, columns "FEP benchmark: wmPCC, wmKτ", with 95% CIs, for RF-score (0.29 / 0.18), Pafnucy (0.26 / 0.18), OnionNet-2 (0.27 / ...), AEV-PLIG and its augmented variants; Table 2 (training and benchmark data sets) |
| Series or target set | The Ross 2023 FEP benchmark, described by these authors as over 50 unique protein targets and over 1200 ligands |
| Measured endpoint and units | Measured affinities of the Ross 2023 collection, kcal/mol |
| Per-target or pooled | Weighted mean over series (same weighting as Ross 2023), with 95% CIs. Per-series values are not printed in Table 1 |
| FEP arm on the same series | **Yes**, quoted on the same benchmark: FEP+ wmPCC 0.68, wmKτ 0.49, against AEV-PLIG 0.41 / 0.26 rising to 0.59 / 0.42 with augmented training data, at about 400,000 times lower cost |
| Stated leakage control | Training complexes removed by ECFP6 Tanimoto above 0.9 to any test-set ligand; "hard overlap" (same system present in both) removed for the other benchmarks |
| Authors developed the method | **Yes** for AEV-PLIG; the FEP+ arm is quoted from Ross 2023 |

Extraction warning: these FEP+ cells (Pearson 0.68, tau 0.49) are **not** the same cells as Ross 2023 Table 3
(R² 0.56, tau 0.51). Different metric, and probably a different subset. Do not conflate them in a record.

### C5. Shimizu et al. 2026, Chem-Bio Informatics Journal

| Field | Value |
| --- | --- |
| Primary source | `https://www.jstage.jst.go.jp/article/cbij/26/0/26_11/_html/-char/en` |
| Version / DOI | doi 10.1273/cbij.26.11; *Chem-Bio Informatics Journal* volume 26; CC BY 4.0; supplemental data doi 10.5281/zenodo.18669539 |
| Exact tables | Figure 4 (per-target Pearson r and MAE, 99 targets, 95% CI bars); Figure 5 (per target class); Figure 2 (calculation time per compound per target); Table 1; Supplemental Data S4-S10 |
| Series or target set | External benchmark built from ChEMBL v35: 356 targets, 10,933 compounds; 99 targets in the per-target accuracy analysis |
| Measured endpoint and units | **pChEMBL pooled across Ki, Kd, IC50, EC50, XC50, AC50, ED50 and potency**, median over duplicate compound-target pairs. Not one assay type |
| Per-target or pooled | **Per-target**, but figure-only; the per-target rows are in the supplemental data, so values are computable under the repository's derivation rule |
| FEP arm on the same series | No |
| Stated leakage control | Dataset constructed to have no overlap with Boltz-2 training data (ChEMBL v35 after the cutoff). Error does not correlate with target sequence identity (r = -0.046) or with compound similarity |
| Authors developed the method | **No.** Independent, and it also measures compute: original Boltz-2 against NVIDIA NIM 1.2.0 on one A100 80GB, NIM about 60-90% faster, MAE about 0.9 either way |

Limit that decides its status: the per-target sets are ChEMBL target sets, not congeneric series, so this
measures within-target ranking over heterogeneous chemotypes with mixed assay endpoints. Strong proxy, not
direct evidence for the use case.

### C6. Wan, Zhang, Xue and Coveney 2026

| Field | Value |
| --- | --- |
| Primary source | `https://arxiv.org/abs/2603.05532` (HTML full text at `https://arxiv.org/html/2603.05532v1`) |
| Version / DOI | arXiv:2603.05532v1, submitted 2026-03-02; doi 10.48550/arXiv.2603.05532 |
| Exact tables | Figures 4, 5 and 7 (Boltz-2 ΔG against ESMACS ΔG; two-run reproducibility; top-100 subset). **No printed results table found** in the HTML version |
| Series or target set | 3CLPro (16,780 compounds, screened from ZINC15 and MCULE) and TNKS2 (21,702 compounds, REINVENT-generated from 27 known actives) |
| Measured endpoint and units | **None.** The reference is a computed ESMACS free energy, not a measured affinity. Boltz-2 output is converted from log10(IC50) with (6 - log10 IC50) * 1.364 |
| Per-target or pooled | Single target per data set, so within-target, but method against method |
| FEP arm on the same series | ESMACS (ensemble end-state free energy), not relative FEP |
| Stated leakage control | Not stated as a train/test control; the compounds are screened or generated libraries |
| Authors developed the method | **No** (independent of the Boltz developers) |

Usable only as a limit-setting source: regression towards the centre in the Boltz-2 affinity predictions, and
no significant correlation against fine-grained ESMACS on the top 100 compounds.

## Question 1: are per-series numbers recoverable for C1, or are the averages all we can honestly record?

**For Boltz-2 itself: no. Only the target-averaged values can honestly be recorded from what this pass
retrieved.** The reasoning, with each step's evidence:

- The supplement's columns are labelled "target avg.". The per-series values behind them are not printed
  anywhere in the supplement. Figure 12 shows per-assay scatter plots for the **validation** set, not for the
  FEP+ subsets, and prints no numbers; the repository's rules forbid reading values off a figure by eye.
- No supplementary data file of Boltz-2 per-complex predictions was found. The Europe PMC supplementary-files
  endpoint returned exactly one supplement PDF plus figure images. There is no workbook, no CSV, no per-edge
  table.
- The Boltz repository's own affinity evaluation outputs would be the route, and the search snippet for
  `github.com/jwohlwend/boltz` said the FEP+, CASP16 and MF-PCBA affinity predictions and evaluation scripts
  were listed as "coming soon". That is a search snippet, a lead, unverified against the repository, and it is
  the one check worth making before extraction. Record it as the open question, not as a finding.
- The protein-ligand-benchmark repository (`openforcefield/protein-ligand-benchmark`) and the Schrödinger
  repository hold the **experimental** affinities and the series definitions, and the Schrödinger repository
  additionally holds FEP+ per-edge results (MIT, releases v1.0 and v2.0). So per-series values are recoverable
  for the **baselines**, and for OpenFE through the Zenodo per-transformation TSVs. They are not recoverable
  for Boltz-2. Combining published per-series FEP+ numbers with Boltz-2 series-averages would mix two
  granularities in one comparison and must not be done.

**What that means for the use case's evidence status.** This is a distinction worth stating carefully, because
it is not the usual pooled-correlation problem. A "target avg." Pearson is the **mean of per-series Pearson
values**, each computed inside one target's series. It is not a correlation pooled over unrelated targets, and
it does not get the flattering inflation that pooling produces. So C1 and C4 are **direct evidence on the use
case's endpoint, at series-average granularity**, not proxy evidence. What is lost is resolution, not validity:
the records can support "on average over these congeneric series, method X ranked analogues this well", and
cannot support "method X would have ranked your series this well", nor any statement about variance across
series. C5, by contrast, is genuinely proxy: per-target but not congeneric, and pooling assay types.

Two consequences for the records: the evaluation's `comparison` fields must carry the series-average
aggregation explicitly (the metric qualifier should say the value is a mean over targets, as the source
labels it), and the use-case definition should state that no reviewed source in the store publishes per-series
affinity-ranking values for any ML method, which is itself the gap worth recording.

## What the store already covers

Confirmed by `git grep` and by reading the records.

- **PLABench, Wang 2026** (`lit-interactions-20261011-leakctl-source-wang2026`, doi 10.64898/2026.09.17.752433,
  CC BY-NC-ND): protocols `-protocol-casp16-l1000`, `-protocol-casp16-l3000`, `-protocol-chembl35`, the six
  Davis and KIBA warm, cold-drug and cold-target protocols, datasets for each, and configurations for Boltz2,
  DeepDTA, FlowDock, FLOWR.ROOT, Graph_RG, LCDD-team, LLF, MFE and MixingDTA. The two CASP16 protocols are the
  same two series as C1 Table 14 and C3, and their recorded limits already say that each series is a single
  target, that metrics are computed over all ligands of a series, that structure-based models received
  AlphaFold3 structures rather than crystal structures, that no uncertainty is printed, and that the L1000
  affinity range is narrow. The ChEMBL35 protocol's recorded limit says the source does not state whether
  Table 4 pools all 4,862 pairs or averages per target. The benchmark's `scope_note` records that the
  figure-only per-target Kendall tau analysis was **not** extracted.
- **Davis and KIBA DeepDTA holdout protocols** (`lit-interactions-20261011-plmdta-protocol-davis-deepdta-holdout`,
  `-kiba-deepdta-holdout`): pooled across targets. Proxy at best for this use case.
- **CASF-2016** scoring, ranking and docking protocols (`paper-protocol-31d4bca49fb09d2e6f`,
  `paper-protocol-0c5a1c5ef6896a2d96`, `paper-protocol-9e3344661a0f282e5e`) on PDBbind-2016. The ranking power
  protocol is within-target over small PDBbind clusters, not congeneric medicinal-chemistry series. Proxy.
- `catalog-task-ligand-affinity` and `catalog-model-boltz-2` exist and are reusable.
- **The Boltz-2 preprint is already a source record**, `expansion-p3-boltz2` (doi 10.1101/2025.06.14.659707,
  Europe PMC full-text XML PMC12262699, SHA-256 `20b1c6f0b64317b8585834a5513905e133806ccb4f2917595ce4252c8ee37515`),
  but **no evaluation, result or claim record cites it**. The XML snapshot contains the main text, figure
  captions and Table 1 only; Tables 11 to 16 are not in it. Extracting C1 therefore needs a **new source
  record for the supplement PDF**, alongside the existing XML record.

What the store does **not** hold, confirmed by grep over `data/entities/`: any record at all for FEP, FEP+,
OpenFE, ABFE, MM/PBSA, FMO, Chemgauss4 or any free-energy method, and no record for the Ross 2023 benchmark,
the protein-ligand-benchmark, the Merck FEP set or the CASP16 affinity assessment. The FEP baseline has to be
built from C2, C3 and the blocked OpenFE paper's primary sources.

## Sources that could not be retrieved, and licence blockers

| Source | Why it matters | Status |
| --- | --- | --- |
| Baumann, Horton, Henry, Travitz, Ries, Gowers, Swenson, Pulido et al., "Large-Scale Collaborative Assessment of Binding Free Energy Calculations for Drug Discovery Using OpenFE", *J. Chem. Inf. Model.*, published 2026-06-08, doi 10.1021/acs.jcim.6c00089 | The primary for the OpenFE arm of C1 Tables 11 and 12, and the open-source FEP baseline the use case needs | **Access blocker.** Europe PMC records PMC13555741 with `isOpenAccess: N`; `fullTextXML` returns HTTP 500; Crossref lists three ACS licence policies and no open licence; a preprint was searched for and not found. Not retrieved |
| bioRxiv full PDF of the Boltz-2 preprint, `https://www.biorxiv.org/content/10.1101/2025.06.14.659707v2.full.pdf` | Would be the single-file primary for Tables 11-16 | HTTP 403 from bioRxiv. Worked around via the Europe PMC supplementary-files endpoint, which yields the same appendix as a supplement PDF (C1). The v2 main-text PDF is still not retrieved, so C1's version line is bioRxiv **v1** as deposited in PMC, not v2 |
| Schindler et al. 2020, Merck FEP benchmark, *J. Chem. Inf. Model.* 60, 5457-5474; preprint doi 10.26434/chemrxiv.11364884.v1; data at `github.com/MCompChem/fep-benchmark` | A named FEP benchmark set with congeneric series on 8 pharmaceutical targets | Not retrieved. The journal DOI was not confirmed: the citation and the preprint DOI come from search snippets only, which are leads. Ross 2023 Table 2 already includes the Merck sets inside its assembled benchmark, so the Ross route may make a separate Merck record unnecessary |
| Hahn et al. 2022, "Best practices for constructing, preparing, and evaluating protein-ligand binding affinity benchmarks [article v1.0]", *Living Journal of Computational Molecular Science*; repository `openforcefield/protein-ligand-benchmark` | Defines the 4-target subset used in C1 Table 12 and the series definitions | Not retrieved. A preprint at arXiv 2105.06222 appeared as a search lead and was not fetched |
| Wu, Koenig, Boresch and Cossins 2025, ABFE protocol, doi 10.1021/acs.jctc.5c00861 (also ChemRxiv `chemrxiv-2025-q08ld`, arXiv 2508.19385) | The ABFE arm of C1 Table 12, and the method behind the prospective TYK2 validation | Not retrieved. JCTC, licence unknown |
| "Chen et al., 2023", cited by the Boltz-2 supplement as the source of the 87 neutral compounds in the 4-target subset | Needed to define the series for C1 Table 12 | **Unresolved citation.** The reference list contains more than one 2023 Chen entry and neither is a congeneric-series paper. Do not guess the identity |
| OpenFE per-transformation data on Zenodo, for example doi 10.5281/zenodo.17936667 ("OpenFF 2.2.1 Relative Binding Free Energy Benchmarks", Alibay, 2025-12-14, CC BY 4.0; per-system ddG TSVs plus `{system}_ref.csv` reference values taken from Ross 2023) and the project docs at `industrybenchmarks2024.readthedocs.io` (state that inputs come from the v2.0 release of the Schrödinger set and that FEP+ results are included) | A retrievable, openly licensed route to per-system OpenFE values on the same series, while the JCIM paper is blocked | Metadata retrieved; files not downloaded or hashed. These are force-field benchmark runs deposited by one author, **not** the published OpenFE industry benchmark result. Do not present them as such |
| Schrödinger benchmark data repository `github.com/schrodinger/public_binding_free_energy_benchmark` | The per-system data and FEP+ results behind C2 | Releases confirmed by the GitHub API: v1.0 and v2.0, both published 2023-06-26, licence MIT, last push 2023-06-26. Ross 2023 states its results use v1.0; the OpenFE study used v2.0. Files not downloaded or hashed |
| Horton 2025, `blog.omsf.io/the-free-energy-of-everything-benchmarking-openfe` | The source the Boltz-2 supplement itself cites for its OpenFE arm | **Excluded as a lead.** A blog post is not a primary source under the repository's rules, however load-bearing the Boltz-2 tables make it. Its claims (that FEP+ outperforms OpenFE overall, that FEP+ settings were tuned per system while OpenFE used defaults, and that the Schrödinger public set covers 59 systems, 876 unique ligands and about 1,200 transformations) must come from doi 10.1021/acs.jcim.6c00089 before any record rests on them |

**Licence position.** The benchmark data is open: MIT for the Schrödinger repository, CC BY for C2, C3, C4, C5
and the Zenodo OpenFE records, CC BY 4.0 as stated on the Boltz-2 supplement pages. Two blockers remain.
First, the OpenFE assessment paper itself is behind an ACS paywall. Second, **running** FEP+ needs a commercial
Schrödinger licence, so the FEP+ arm can only ever be recorded from published values, never re-run here; the
same applies to the FMO code (in-house) and to Chemgauss4, OMEGA and Spruce (OpenEye, commercial). Record the
FEP+ compute cost as unreported rather than inferring it: no retrieved source prints it, and Table 12's FEP+
time cell is "-".

## Caveats the Boltz-2 supplement states in its own words

Carry these onto any record extracted from C1, since the paper states them itself:

- The FEP+ arm shows "the maximum attainable accuracy of current (commercial) FEP simulations by manually
  adjusting the protocol ... to the system at hand after observing the error with respect to the experiment".
- The ABFE arm "may also represent an optimistic estimate of its prospective performance given that the
  protocol was optimized based this dataset".
- The OpenFE arm is automated with a fixed protocol, and its cited source in the supplement is a blog post.
- Tables 11 and 12 print one value per cell with no uncertainty. Bootstrap standard errors exist only as error
  bars in Figure 6, which has no printed values.
- The paper's "over 1,000 times faster" claim against FEP is not backed by a measured FEP+ cost in the same
  table.

## What this search did not cover

- No systematic sweep of Europe PMC, PubMed, bioRxiv or arXiv by query. Four web searches plus targeted
  retrieval of named primaries. Recall against the affinity-prediction literature is unknown.
- No search for MM/GBSA or docking-score comparators on congeneric series beyond what C1 Table 12 happens to
  include, although #178 names them as the cheaper comparators to record.
- No coverage of other recent affinity models on these series: Chai-2, NeuralPLexer, Umol, SurfDock,
  co-folding models other than Boltz, or active-learning workflows. Only the baselines that C1, C4 and C5
  chose for themselves.
- **No check of whether the 876-complex OpenFE subset and the 87-compound 4-target subset overlap**, which
  they partly must, since both derive from the Ross 2023 collection. Any pass that extracts both tables has to
  state that the two rows are not independent.
- Leakage literature was screened by one query. Three candidates were noted and not retrieved: PDBbind
  CleanSplit / "Resolving data bias improves generalization in binding affinity prediction" (PMC12552120), the
  GEMS preprint (doi 10.1101/2024.12.09.627482), and a DAVIS-completeness preprint (arXiv 2512.00708) that
  quantifies Boltz-2 train and test overlap at 100% sequence identity and Tanimoto 1.0. None was screened
  against its primary. A LIT-PCBA leakage audit (arXiv 2507.21404) was noted and set aside as virtual
  screening rather than affinity ranking.
- The Boltz-2 figure-only material was not read by eye: Figure 6 (bootstrap error bars), Figure 12 (per-assay
  scatter plots) and Figure D.2.1 (compound-similarity dependence) carry no printed values.
- CASP16 per-group per-target Kendall tau values were not extracted. They are in figures; the official
  per-target results file at predictioncenter.org was not downloaded.
- The `github.com/jwohlwend/boltz` repository was not checked for released affinity predictions and evaluation
  scripts. This is the one outstanding check that could turn C1 from series-average into per-series evidence
  (see Question 1 above).

## Honest answer to the question behind the use case

A same-series comparison of an ML affinity predictor against free-energy calculation **does exist** in the
published literature, on measured affinities, in at least two places: the Boltz-2 supplement Tables 11 and 12
(C1), and AEV-PLIG Table 1 (C4). Both run on the Ross 2023 congeneric-series collection, both report
target-averaged or series-weighted correlation and ranking, and both carry an FEP arm on the same series.

Three caveats decide how much weight the use case can put on them. Both are reported by the developers of the
ML method being promoted. Both take the FEP+ arm from Ross 2023, whose protocol was tuned per system after
seeing the experimental error, which inflates the baseline being compared against. And neither prints
per-series values, only averages over series, so the question "would this method have ranked **my** series
correctly" cannot be answered from the printed tables, only the question "on average across these series".

No fully independent evaluation of an ML predictor against FEP on the same measured congeneric series was
found in this pass. C5 is independent and per-target but has no FEP arm and pools assay types. C6 is
independent and single-target but has no measured affinities at all. The blind comparison that comes closest
to a neutral read is C3, where the best CASP16 participant reached Kendall tau = 0.42 against an estimated
achievable ceiling of about 0.73, and where supplying experimental structures did not help: that gap is the
honest frame for every number above.

## Files written by this pass

- `data/omics/search-ledger.jsonl`: 23 entries appended, `search-leadopt-20261022-s1` to `-s23`; 611 lines total.
- `data/omics/scope-audit.jsonl`: 8 rows appended; 585 lines total.
- Committed as `973c98d` on `claude/uc-leadopt`, not pushed.
- Retrieved artifacts kept under
  `/private/tmp/claude-501/-Users-timrichardson-Documents-projects-personal-blog/0d3cb31f-8729-462e-a6d2-d4a49d218584/scratchpad/dl/`,
  notably `b2supp/NIHPP2025.06.14.659707v1-supplement-1.pdf` (the appendix tables), `ross2023.xml`,
  `casp16aff.xml`, `aevplig.xml` and `shimizu.html`.
