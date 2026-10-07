# Mass-spectrum molecule shortlisting: bounded evidence research, 2026-10-07

Case 5 of 17 (rewire-benchmark-data [#3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3)), covering `use-case-mass-spectrum-molecule-shortlisting` (rewire.it [#335](https://github.com/rewire-bio/rewire.it/issues/335), programme items B335/BL335 in rewire-benchmarks [#25](https://github.com/rewire-bio/rewire-benchmarks/issues/25)).

This is a docs-only research dossier. It changes no scientific catalogue data and no release: no catalogue record, mapping, definition, build or release was made or proposed by this pass. The worker did not post any issue; rewire-benchmarks #31 was separately reviewed and posted. The worker made no staging, commit, push or PR. The pass started from producer commit `cf271df`. Before this correction the branch was fast-forwarded to producer main `b103b6691954221a53af546e75aaf5a5fce6e762`, which includes a concurrent AMP evidence release. That work is untouched. On the fast-forwarded main the seven mappings of this use case are unchanged.

## Method and constraints

- Local extraction only: `curl`, `pdftotext`, and Python run with `-I` on cached bytes. No scientific model was executed, trained or evaluated. No paid access, access bypass or outreach.
- Every request, including failed ones, is in a request log written at fetch time: `workbench/msms-shortlisting-20261007/primary/retrieval-log.tsv` (UTC time, URL, status, SHA-256 of the body). Times below come from that log unless stated.
- Web search queries were run through a search tool. Individual query times were not logged, so the search log gives a window bounded by adjacent logged fetches, except batch D, whose start was logged.
- Archives were extracted into their own new directories and read only with `python3 -I` scripts kept in `workbench/msms-shortlisting-20261007/scripts/`.
- Scripts behind the derived numbers: `inspect_massspecgym_zenodo.py`, `inspect_candidate_uniqueness.py`, `verify_table3_against_catalogue.py`; outputs sit next to them under `workbench/msms-shortlisting-20261007/`. The candidate-list description was independently recomputed by the root review (`workbench/codex-msms-review-20261007/candidate-independent-check.json`).
- Every negative statement in this document is bounded to the sources named, the pinned repository, the inspected Zenodo records and the dated search below. None is a claim of global absence.

## Disposition summary

1. Numeric transcription. All 108 v1 and 81 v2 Table 3 cell transcriptions in the catalogue match the inspected primary PDFs (`table3-verification.json`, zero mismatches), and the PDF hashes match the historic artifacts. This verifies transcription only. It does not verify run counts, spread definitions, checkpoint identity or split identity, which remain open limitations below.
2. The audit's open item "v1-specific URL returned HTTP406" was not reproduced: `https://arxiv.org/pdf/2605.19752v1` returned HTTP 200 on 2026-10-07 with bytes whose SHA-256 equals the historic artifact hash. The historic record's `url` and `retrieval_url` still point at the unversioned URL, which now serves v2. No byte or value needs to change.
3. Source findings below sharpen how the existing evidence should be read (target-present candidate sets, candidate-list structure, evaluation risks documented in 2026, unquantified pretraining overlap). They change no value.
4. Disposition: docs-only completion of this bounded pass. The disposition permits publication of the reviewed dossier as documentation; it does not forbid a documentation PR. The existing MSAlign v1 and v2 tables already supply the quantitative evidence. No catalogue records, mappings or definition changes are proposed. The existing immutable reviewed releases cover the quantitative intake and release scope of this pass. A dossier correction alone does not justify a new scientific release. Earlier optional additions (a mapping link and new numeric rows) were withdrawn.
5. Focused execution gap: rewire-benchmarks [#31](https://github.com/rewire-bio/rewire-benchmarks/issues/31) ("B335 - Freeze candidate-pool and target-absence tests for formula-free MS/MS retrieval") is already posted, open, and links #25, #3 and B335. It was not recreated. Its reviewed body is `/tmp/rewire-b335-reviewed-gap-20261007.md`.

## Starting inventory (numeric transcription re-verified)

Definition `use-case-mass-spectrum-molecule-shortlisting` (reviewed 2026-09-30T21:54:30Z, `automated_source_review`) has seven active mappings, all with relevance `proxy`.

| Mapping id | Protocol | Evaluations | Source record |
|---|---|---|---|
| `use-case-mapping-msms-formula-no-formula-r1` | `msalign-2026-table3-task-massspecgym-formula-split-no-formula-r-1` | 6 | `evidence-official-760ab2fa8c396aeb796c` (v1) |
| `use-case-mapping-msms-formula-no-formula-r20` | `...formula-split-no-formula-r-20` | 6 | same |
| `use-case-mapping-msms-mces-no-formula-r1` | `...mces-split-no-formula-r-1` | 6 | same |
| `use-case-mapping-msms-mces-no-formula-r20` | `...mces-split-no-formula-r-20` | 6 | same |
| `use-case-mapping-20260930-335-b1e55d78e4a8` | `uc20260930-msalign-v2-protocol-massspecgym-formula-formula-free` | 5 | `uc20260930-source-msalign-v2` |
| `use-case-mapping-20260930-335-7acc50652955` | `uc20260930-msalign-v2-protocol-massspecgym-mces-formula-free` | 5 | same |
| `use-case-mapping-20260930-335-c58cfe791948` | `uc20260930-msalign-v2-protocol-spectraverse-formula-free` | 5 | same |

The v1 mappings hold six formula-free configurations (FFN, DeepSets, JESTR, Emb-Cos, SAIL, MSAlign) at Recall@1 and Recall@20 on the MassSpecGym formula and MCES splits. The v2 mappings hold five (DeepSet, JESTR, Emb-Cos, MSAlign, MSAlign score fusion) at Recall@1, @5 and @20 with printed spreads, on MassSpecGym formula, MassSpecGym MCES and Spectraverse. The v1 records for NPLIB1, Spectraverse and Recall@5 exist in `data/omics/reviewed/model-coverage-tables-2026-09-23/records.jsonl` but are not mapped to this use case. The v2 formula-oracle rows are recorded but excluded from the mappings.

| Check | Result |
|---|---|
| v1 PDF `https://arxiv.org/pdf/2605.19752v1`, retrieved 2026-10-07T14:47:38Z | HTTP 200, 1,345,640 bytes, SHA-256 `7395a55141ee7916741b7d9e6d4f42a1d3a03217a36ce6824ac3ff48afd4f26f`, equal to the catalogue `artifact_sha256` for `evidence-official-760ab2fa8c396aeb796c` |
| v2 PDF `.../2605.19752v2`, retrieved 14:47:42Z, and the unversioned URL at 14:47:33Z | HTTP 200, SHA-256 `a31d1167b0ded72f64717881dd6cba0946a56b495d76f169d8e44115c3266fda`, equal to `uc20260930-source-msalign-v2`. The unversioned URL still serves v2 |
| arXiv listing (abs page and API, 14:47:29Z and 14:47:52Z) | Two versions: v1 Tue 19 May 2026 12:19:35 UTC, v2 Fri 25 Sep 2026 16:44:43 UTC |
| Table 3 v1, 4 blocks x 3 rows x 9 columns | 108 cells parsed from `pdftotext -layout`; all 108 equal the `printed_value` of the matching catalogue result |
| Table 3 v2, 3 blocks x 3 rows x 9 columns | 81 cells parsed; all 81 equal the catalogue `numeric_value` and `reported_spread` |

The 2026-09-30 audit recorded an HTTP 406 for a v1 request. This pass used a descriptive User-Agent (`rewire-benchmark-data-research/1.0`). The cause of the earlier 406 was not diagnosed and the old request form was not repeated.

## Dated search log (all 2026-10-07)

Tools: search tool in standard and extended modes for discovery; direct `curl` for primary bytes.

| Batch | Window (UTC) | Query | Mode |
|---|---|---|---|
| A | 14:50:31 to 14:50:46 | MassSpecGym benchmark discovery identification molecules NeurIPS 2024 retrieval candidates MCES split | standard |
| A | same | Small molecule retrieval from tandem mass spectrometry: what are we optimizing for? arXiv 2602.16507 | standard |
| A | same | MS/MS molecule retrieval benchmark 2026 candidate set true structure absent database generalization instrument shift | extended |
| B | 14:52:42 to 14:53:13 | DreaMS Self-supervised learning of molecular representations from millions of tandem mass spectra Nature Biotechnology 2026 GeMS MassIVE pretraining | standard |
| B | same | Spectraverse comprehensive curation harmonization small molecule MS/MS libraries Skinnider bioRxiv | standard |
| B | same | CASMI 2022 contest results small molecule identification machine learning blind challenge Schymanski evaluation 2025 2026 | standard |
| C | 14:53:50 to 14:54:44 | MSAlign DreaMS MolDeBERTa molecule retrieval MassSpecGym independent reproduction OR comparison 2026 | extended |
| C | same | MassSpecGym v1.5 leaderboard retrieval hit rate DreaMS MS/MS 2026 | standard |
| C | same | prospective experimental validation machine learning MS/MS structure annotation retrieval confirmed with authentic standards 2026 candidate ranking false discovery rate | extended |
| D | starts 14:59:33 (logged) | open-world molecular retrieval mass spectra target molecule not in candidate database rejection abstention benchmark | extended |
| D | same | cross-instrument OR cross-laboratory generalization MS/MS structure annotation deep learning held-out instrument evaluation 2026 | extended |
| D | same | NPLIB1 MIST Goldman Annotating metabolite mass spectra with domain-inspired chemical formula transformers Nature Machine Intelligence retrieval PubChem candidates | standard |

Direct retrievals: arXiv abs, PDF, HTML and e-print for the MSAlign versions and the other arXiv papers; GitHub API and raw files for `KrzakalaPaul/MSAlign-NeurIPS2026` (pinned at commit `c2ef425b68749052a17b9cdd5f5f11709322654e`), `pluskal-lab/MassSpecGym` and `pluskal-lab/DreaMS`; Zenodo and Hugging Face record APIs; bioRxiv, PMC, Nature and the Fiehn Lab CASMI 2022 page; `gh` reads of rewire-benchmarks and rewire.it issues.

Inclusion: primary papers, code or data releases about molecule retrieval or identification from MS/MS under candidate sets, or about evaluating such retrieval, dated about 2024 to 2026, with Methods and Results read beyond the abstract where retrievable without authentication.

Exclusion: formula-conditioned methods as comparators for a formula-free use case (MIST, FLARE, MVP, and SpecBridge's MassSpecGym track, which uses formula-filtered pools); de novo generation; spectrum simulation; spectral-library matching tools; MS2 identifiability prediction before fragmentation; microbial MALDI-TOF identification. These follow the exclusions in the use-case definition.

This was a time-boxed pass. It does not establish that no other relevant literature exists.

## Findings, by source (full-text status stated)

### 1. MSAlign, arXiv 2605.19752 v1 and v2 (full text of both PDFs read, plus the v2-era code and data release)

Authors Krzakala, Melo, Lancon, Laclau, Flamary, Thevenot, d'Alche-Buc. arXiv licence CC BY 4.0 for both versions (abs pages).

v1 and v2 report different numbers for configurations with the same names.

| Item | v1 (19 May 2026) | v2 (25 Sep 2026, NeurIPS 2026 format, with a reviewer-rebuttal acknowledgement) |
|---|---|---|
| Title | MSAlign: Aligning Molecule and Mass Spectra Foundation Models for Metabolite Identification | MSAlign: Aligning Molecule and Mass Spectra representations for Metabolite Identification |
| Molecule encoder in MSAlign | ChemBERTa (cited as ChemBERTa-2, arXiv 2209.01712). Fig. 1 says 92M parameters, pretrained on 110M SMILES. Checkpoint not named | MolDeBERTa (`SaeedLab/MolDeBERTa-base-123M-mtr`) |
| Datasets | NPLIB1, MassSpecGym (formula and MCES splits), Spectraverse | MassSpecGym (formula and MCES), Spectraverse |
| Formula-free comparators | FFN, DeepSets, JESTR, Emb-Cos, SAIL, MSAlign | DeepSet, JESTR, Emb-Cos, MSAlign, MSAlign with late score fusion (overbar in the table) |
| Formula-conditioned | MIST, FLARE, MSAlign+Filter | MIST, MVP, FLARE, MSAlign+Filter with fusion |
| Spread in Table 3 | none; number of runs not stated | standard deviation; the caption says "over 3 random splitting of the dataset"; the divisor is not stated |
| MassSpecGym formula split | one value per cell; split seed and run count not stated | 3 random seeds of the formula grouping (Section 5.1) |
| MassSpecGym MCES split | "original MCES split"; run count not stated | Section 5.1: two variants with validation and test swapped; Table 3 caption says 3 splittings |
| Separate Gaussian mass-error score fusion | none stated | present as scorers in the fusion variant |

Table 3 is on page 7 of both PDFs. Example cells, MassSpecGym formula split R@1: MSAlign 53.8 (v1) and 47.5 +/- 3.4 (v2); DeepSets 22.2 and 4.7 +/- 0.6; JESTR 20.0 and 13.9 +/- 0.5; Emb-Cos 41.2 and 42.7 +/- 3.0. MCES split R@1: MSAlign 16.2 and 19.0 +/- 3.2; Emb-Cos 12.3 and 12.6 +/- 0.2. These pairs are listed to show that the versions differ, not to rank them.

Protocol facts read from the text (v1 Section 5.1 and Appendices A and B; v2 Sections 5.1 and 5.2 and Appendices A and B):

- Candidates follow the MassSpecGym protocol. The MSAlign text says candidates are retrieved from PubChem within 10 ppm of the target mass, prioritising compounds sampled from databases of decreasing metabolite relevance, with K = 256 per spectrum. The target is in every set. v2 Appendix B.2 states "each full candidate set C(s_i) includes the target m_i".
- Training uses 128 candidates per spectrum (v1 Table 6, v2 Table 8). Evaluation uses the full list.
- Formula-free means formula is not an input. The formula split groups train, validation and test by chemical formula. The MCES split is the MassSpecGym split (minimum MCES distance 10 between folds).
- v1 Table 2 and v2 Table 2 report a sliced-Wasserstein shift measure on different scales. The authors argue the formula split is the more realistic deployment trade-off. That is an author argument.
- DeepSets uses Fourier features and 50 epochs instead of the original setting (Section 5.1 of both versions).
- Metadata: v1 Appendix B.1 says precursor mass is already incorporated in DreaMS "by adding it as a peak with fixed intensity 1.1", and adduct and collision energy are added as learned embeddings. That is the paper's description. The pinned current `preprocessing/encode_dreams.py` (SHA-256 `e22d38daf322250dd580f9809c9645f092ba0fce12fe1443e249b513dcd6af0d`) reads `precursor_mz` and passes it to `SpectrumPreprocessor`. That code is not asserted to describe the v1 pipeline. The v1 and v2 difference above concerns only the separate Gaussian mass-error scorers, not whether mass information enters the encoder.
- Hyperparameters differ between versions (v1 Table 6: 24,000 steps on MassSpecGym, shared dimension 1024; v2 Table 8: 20,000 steps for MCES, 30,000 for formula, shared dimension 512).
- Spread: v2 Table 3 gives standard deviation without a divisor. A v2 ablation table (Table 11) says "sample standard deviation over the three MassSpecGym formula test splits"; that wording is for that table and is not extended to Table 3 or to the MCES values.
- Both checklists say code, splits and checkpoints "will be released upon publication".
- v1 Table 8 metadata ablation on the MassSpecGym formula split: "Both" R@1 53.83, "None" 51.67.

Code and data release (checked 2026-10-07):

- Repository `KrzakalaPaul/MSAlign-NeurIPS2026`, MIT, created 2026-09-25, last push 2026-09-25, five commits, head `c2ef425b68749052a17b9cdd5f5f11709322654e`. No issues. The README clone command names `KrzakalaPaul/MSAlign`, not this repository.
- Zenodo record 22830464, "MSAlign Datasets, splits and candidate maps", published 2026-09-18, CC BY 4.0, open access. Two archives:
  - `massspecgym.zip`: 1,078,913,065 bytes, SHA-256 `6dbe62b0e69232ea63993cc92dc0126989c82aee286c00f0f837cd35b8cd91f1`, MD5 `96e8b1885cf4120aaef93154ce809cbd` (matches the record). Download started 14:50:31Z; the finish time was not recorded.
  - `spectraverse.zip`: 2,237,587,937 bytes, SHA-256 `71a07e8336e0169e4d085e927823fd4ff4661aa45df675585480b654c3e81d9e`, MD5 `729425411e4e5da92902782918116dbb` (matches the record). Download started about 14:58Z. Completion was observed around 15:12Z by the root review; an exact finish time is not claimed.
- Not found in the pinned repository tree or the inspected Zenodo record: trained checkpoint files. The Zenodo record lists only the two data archives. The README rebuilds everything from scratch and gives runtime as `[TODO: add runtime]`. The README links `DATA.md`, which returned 404 at the pinned commit (14:49:27Z, not retried). The README arXiv badge label reads `2505.22109` while its link points to `2605.19752`. This does not show that checkpoints exist or do not exist elsewhere.
- Frozen encoders in the code: DreaMS via `PreTrainedModel.from_name("DreaMS_embedding")` with DreaMS pinned to commit `dbec3a0b514a99e5056cfccde4559fda8cfe8129`; MolDeBERTa `SaeedLab/MolDeBERTa-base-123M-mtr`.

Evaluator rules in the pinned code (`models/MSAlign/losses.py`, `eval.py`):

- Candidate 0 is the target (`mask_logits` raises if candidate 0 is invalid). Padded candidates score minus infinity.
- Rank is `1 + (number of negatives with score >= target)`, so a tie ranks against the target, and every listed negative counts, duplicates included. Recall@k is the mean over test spectra of `rank <= k`.
- `eval.py` writes `n_test` next to the metrics. The papers do not print it.
- README: "Results across splits are macro-averaged." MCES uses `mces_1` and `mces_2`.

Candidate construction in the pinned code (`prepare_candidates.py`, `download.py`, `process_smiles.py`):

- Spectraverse candidates are built locally. `prepare_candidates.py` reads `unique_smiles.csv`, computes `mass_labeled` from those structures, sets `query_mass = mass_labeled[idx]` and inserts `query_smiles` as candidate 0. It then adds structures within 10 ppm of that mass from pools `1M`, `4M`, `118M` in that order, deduplicated by SMILES string, randomly sampled without replacement when a pool exceeds the cap, capped at 256. This is target-derived benchmark mass. It is not a deployment workflow that converts a measured precursor m/z with charge and adduct. It is described only for this inspected local construction and is not generalised to the imported official MassSpecGym candidates or to any unverified v1 pipeline.
- MassSpecGym candidates are not built by that function. `download.py` fetches the official `MassSpecGym_retrieval_candidates_mass.json` from the Hugging Face dataset and re-normalises it (`canonical=True`, `isomeric=False`, `sanitize=True`). `process_smiles.py` normalises the ground-truth SMILES.
- Formula split: unique formulas are shuffled and cut 90%, 5%, 5%, so spectrum counts per fold vary with the seed. MCES split: the MassSpecGym `fold` column is copied, and `mces_2` swaps validation and test.
- The released MassSpecGym and Spectraverse `metadata.csv` files have no instrument column (MassSpecGym columns: fold, collision energy, adduct, precursor m/z, SMILES, index; Spectraverse: adduct, precursor m/z, collision energy, SMILES, index). Rejoining instrument type from an upstream file, and any instrument-stratified evaluation, were not attempted in this pass.

### 2. MassSpecGym, Bushuiev et al., NeurIPS 2024 Datasets and Benchmarks, arXiv 2410.23326 (full text read: main text, appendix, datasheet)

Cached v1 (SHA-256 `82176d50...`, equal to the catalogue source `part2-massspecgym-arxiv-v1`) and v3 (14 Feb 2025). Table 3 is identical in v1 and v3.

- Retrieval task: rank up to 256 candidates by mass (main track) or by formula (bonus track). "We limit |C| <= 256 candidates per spectrum, sampled randomly if more molecules with the same mass are available." Candidates are drawn iteratively from a 1M set of biological and environmental molecules, then a 4M diverse set, then PubChem 118M (downloaded 2024-05-31), until the cap is reached. A cap of 256 is not 256 distinct chemical structures.
- Identity counts in the appendix column table (Appendix Table 1, v1 and v3): 231,104 spectra, 31,602 distinct SMILES strings, 28,929 distinct 2D InChIKeys. MSAlign v1 Table 12 and v2 Table 7 report 28,936 "unique molecules" for MassSpecGym (its own normalisation), and the released `unique_smiles.csv` has 28,936 data rows. The released candidate map has 29,307 keys. These identity schemes were not reconciled and should not be mixed.
- Data scope: positive electrospray ionisation only, adducts [M+H]+ and [M+Na]+ only. About 98% of spectra carry an Orbitrap or QTOF instrument annotation (not every spectrum). About 53% have normalised collision energy. Sources are MassBank, MoNA, GNPS and an in-house Orbitrap ID-X library; filtering steps are in the appendix.
- Split: single-linkage clustering on MCES distance with threshold 10, stratified by instrument type, collision energy, adduct and molecule frequency.
- Metrics: hit rate at k with 99.9% bootstrap confidence intervals (20,000 resamples). The paper reports a Random control, Fingerprint FFN, DeepSets, DeepSets + Fourier features and MIST in the mass track. The catalogue already holds these as reviewed records (`data/omics/reviewed/benchmark-evidence-2026.jsonl`, protocol `paper-protocol-a18b4bc79049513fb7`, status `needs_review`). They are not mapped to this use case, and no mapping is proposed here.
- MIST in the mass track ran with ground-truth formulas. The original paper does not say so; MassSpecGym issue #52 (closed) and a footnote in De Waele et al. state it. Those rows are formula-conditioned.
- Licence: MIT for code and dataset (datasheet 5.6, Hugging Face card). The datasheet states third parties imposed no restrictions; per-library licences were not itemised in the text read.

### 3. MassSpecGym in the Wild, Liu et al., arXiv 2606.19624 v1, 17 Jun 2026 (full text read: Sections 1 to 7, Appendices A.1 to A.4)

CC BY 4.0. Audit of papers reporting MassSpecGym results before 1 May 2026. It reports evaluation issues in at least 17 of the 26 papers that reported MassSpecGym benchmark results in the first year. Its Figure 1 covers a broader set of 34 papers that used MassSpecGym, eight of them as a dataset rather than a benchmark. It releases MassSpecGym v1.5 (repository merge 2026-05-08, commit `f259fe3780`).

- Canonicalisation shortcut (Section 5.1, Table 3, Appendix A.4). In v1 the ground-truth SMILES keep repository formatting while candidates are RDKit-canonical, so a model can recognise the differently formatted string. Example (1) is a DreaMS spectral encoder with an adapter aligned to a frozen ChemBERTa encoder. It uses spectra, and it scored 82.41 (81.46-83.33)% hit rate@1 inflated against 6.70 (6.09-7.35)% corrected. The audit attributes the gap to the formatting artifact. The SMILES-classifier example (3) and the PubChem-order and chiral-atom rankers (4, 5) are spectrum-blind. These results show evaluation risks. They do not prove the exact cause of any result in any MSAlign version.
- Table 3 lists these rows after the block headed "Retrieval Task w/ Bonus (i.e., Formula Known)", and the classifier example names the formula candidate file. The track for the other artifact rows is not stated separately. The Hugging Face card for v1.5 says the v1.5 mass-filtered candidate file has "the same candidates as in v1 but with SMILES standardized using RDKit", and that the main file's SMILES column was re-standardised from "the PubChem-standardized form used in v1". The card does not say which side of each v1 file carried the formatting difference.
- Ranking-bias shortcut (Section 5.2): ranking candidates by PubChem default order with no spectrum gives 49.98 (48.72-51.20)% hit rate@1 on the formula-known set. The authors treat candidate-pool bias as an open design problem and cite Gupta and Skinnider.
- Formula leakage (Section 4.3): on the mass track, filtering to the true formula raises a random baseline from 0.43 (0.29-0.61)% to 12.98 (12.15-13.83)% hit rate@1. Formula-aware models must not be mixed into a formula-free track.
- Pretraining and simulator leakage (Sections 4.1, 4.2): v1.5 releases data-safe retrained versions of MIST-CF, ICEBERG and DreaMS. The paper text read does not state what overlap the original DreaMS had with the test set.
- Recommendations: 99.9% bootstrap confidence intervals; mask the spectrum and confirm performance degrades; uniform RDKit canonicalisation.
- Open MassSpecGym issues checked 2026-10-07: #56 (3,438 entries have at least one duplicate; maintainers confirmed an unintended filtering failure, and 1,189 entries with identical peaks and different SMILES were unexplained), #71 (collision-energy imputation concern in the v1.5 ICEBERG row), #72 (the leaderboard service is suspended).

### 4. Gupta and Skinnider, "Confronting spurious evaluations of computational methods in small molecule mass spectrometry", bioRxiv 10.64898/2026.05.03.722532 v1, 2026-05-06 (full text read; not peer reviewed; CC BY-NC-ND 4.0)

- A model that never sees a spectrum, trained to separate ground-truth structures from candidates on the MassSpecGym training set, "correctly identifies the ground-truth structure for 9.5% of the MS/MS spectra in MassSpecGym" (Discussion, page 7; the Results text on page 2 words the same figure as candidate sets). This is the authors' result for their model, runs, candidate files and test population.
- Use here: it motivates a matched spectrum-blind control in any Rewire evaluation. It does not establish what fraction of MSAlign's recall depends on candidate-pool bias. Models, runs, pools and populations differ, so no subtraction or cross-paper ranking is made.
- Qualitative points: effective candidate-set sizes in MassSpecGym are sometimes below 256 (duplicate tautomers, stereoisomers, isotopologues, implausible fragments); PubChem-derived candidate sets for Spectraverse are larger and a spectrum-blind model still performs above random; a chemical-language-model decoy generator reduces that advantage. Supplementary figures were not transcribed. These points are contextual and are not new intake.

### 5. De Waele, Wydmuch, Dembczynski, Kotlowski, Waegeman, "Small molecule retrieval from tandem mass spectrometry: what are we optimizing for?", arXiv 2602.16507 v1, 18 Feb 2026 (full text read: main text and appendices B to D; CC BY 4.0; code `github.com/gdewael/ms-mole`, not pinned or inspected)

- Official MassSpecGym split: test 17,556 spectra over 2,998 molecules; validation 19,429 spectra over 3,185; training 194,119 over 22,746.
- Table 1 reports retrieval for several loss functions with SD over 5 model runs on equal-mass and equal-formula candidates. It is the source MSAlign cites for Emb-Cos (v1 reference 15, v2 reference 17), so it is the originators' own measurement, not an independent group's. No values are compared with MSAlign here.
- Appendix D, Table 5: MassSpecGym equal-mass sets have a maximum of 256 and an average of 252.8 candidates; equal-formula sets average 212.1. Because candidates are drawn first from the 1M and 4M sets, the authors say "in practice most negatives come from the first two sets", that models trained on these negatives may perform well mainly within metabolite and exposome space, and that open-world tasks are different.

### 6. Jurgens, De Waele, Rakhshaninejad, Waegeman, "When should we trust the annotation? Selective prediction for molecular structure retrieval from mass spectra", arXiv 2603.10950 v2, 10 Aug 2026 (main text and Appendix C and D.6 read; CC BY 4.0; code `github.com/mkjuergens/Selective-MSMS`)

- Scope of the main results: risk-coverage analysis on MassSpecGym with a fingerprint MLP and a transformer on formula-filtered candidate sets (Section 2.6). Hit rates fall with candidate-set size when sizes vary.
- Appendix D.6 ("Alternative candidate sets") adds two settings. First, the formula-trained ensembles are evaluated on matched capped and uncapped formula-based PubChem pools; about 59% of the uncapped formula pools exceed 256 candidates, some exceed 20,000, retrieval becomes harder and the ordering of scoring functions stays similar. Second, a separately trained and evaluated MLP uses precursor-mass-filtered candidates (within 10 ppm of the query mass inferred from precursor m/z, charge and adduct). Nearly all mass-filtered sets reach the cap, so candidate count carries no information, and the authors conclude that total retrieval uncertainty is robust across candidate definitions while candidate-size and rank-stability criteria depend on pool construction. Qualitative use only; no numbers are taken.
- Limitations section: "the evaluated MassSpecGym candidate sets include the reference structure by construction. Selective prediction when the true molecule is absent from the candidate pool remains an important open-world setting." Risk-controlled coverage is under an exchangeability assumption.

### 7. Rakhshaninejad, De Waele, Jurgens, Waegeman, "Reliable Molecular Retrieval from Mass Spectra using Conformal Prediction", bioRxiv 10.64898/2026.03.12.711424 v1, 2026-03-16 (abstract, introduction and Section 2.5, pages 6 to 7, read; results not transcribed; CC BY 4.0)

- Section 2.5 builds candidate sets by "sampling molecules that match the precursor mass of the query spectrum up to a maximum of 256 candidates". It states the evaluation assumes the true molecule belongs to the candidate set.
- It studies three scenarios (matched, partly shifted, fully out-of-distribution). Conformal coverage guarantees hold under exchangeability of calibration and test samples. A calibration and test mismatch is not covered by the guarantee, and the paper reports larger sets under shift.

### 8. DreaMS, Bushuiev et al., Nature Biotechnology 44:630-640 (online 2025-05-23), DOI 10.1038/s41587-025-02663-3 (open-access article text and supplement cached; relevant sections read)

- Pretrained on GeMS-A10, 24 million unannotated MS/MS spectra mined from MassIVE GNPS, with masked-peak and retention-order objectives. Article CC BY 4.0. Code MIT (GitHub licence endpoint; Zenodo 13843034). Weights: Zenodo record 10997887 (published 2024-04-19, CC BY 4.0; `embedding_model.ckpt` and `ssl_model.ckpt`). The MSAlign code loads `from_name("DreaMS_embedding")`; its mapping to a file was not verified.
- The contrastive fine-tuning used 5,500 MoNA molecules. The article text read does not state whether MassSpecGym or Spectraverse test spectra or molecules were removed from GeMS pretraining. MassSpecGym spectra come from public repositories that GeMS also mines, so overlap is possible and unquantified in the sources read.

### 9. Spectraverse (Gupta et al., ACS, CC BY 4.0, PMC12903054; Zenodo 19927403 v1.0.2) and the MSAlign Spectraverse archive

- Library of 488,630 spectra from 44,237 unique molecules in the paper (v1.0.1, Zenodo 17870921). Instrument type is mapped to QTOF, Orbitrap and ion trap or unspecified; low-resolution QQQ spectra were removed. Positive and negative modes and many adducts are present. Zenodo 19927403 is CC BY 4.0 and also hosts mass-based and formula-based candidate files that MSAlign does not use.
- Bounded inspection of `spectraverse.zip` (hash and listing verified; only `metadata.csv`, `unique_smiles.csv` and `formula_seed1` to `formula_seed3` split files extracted; the 600 MB candidate map `256_candidates_by_mass/map.json` was not read): the metadata has 488,630 rows and the columns `adduct`, `precursor_mz`, `collision_energy`, `smiles`, `unique_smiles_idx` (no instrument column). `unique_smiles.csv` has 44,302 rows. MSAlign v2 Table 7 gives 488,797 pairs and 44,307 molecules. Three different counts (paper, archive, MSAlign table) are therefore not reconciled.
- Released formula seeds 1, 2, 3, test spectra (unique SMILES): 26,679 (2,403); 25,693 (2,276); 27,012 (2,183). Training and test folds share no SMILES string in these files. These are descriptions of released files. They do not prove the scoring denominators or checkpoints behind published numbers.

### 10. Context only: other 2026 work reviewed (primary links; no numbers taken)

- Giné et al., J Am Soc Mass Spectrom 37(7):1550-1561, [PMC13329996](https://pmc.ncbi.nlm.nih.gov/articles/PMC13329996/) (CC BY 4.0): embedding-based retrieval from a larger structure database at several mass tolerances. Different task, database and splits. It indicates that accuracy depends on mass tolerance and hence on pool size.
- CASMI 2022, [Fiehn Lab results page](https://fiehnlab.ucdavis.edu/casmi/casmi-2022-results): a blind challenge scored on correct 2D structures. It is not a prospective clinical identification study, it does not report an authenticated outcome for any MSAlign configuration, and this pass does not assume its targets were absent from every candidate pool.
- SpecBridge, [arXiv 2601.17204](https://arxiv.org/abs/2601.17204): its MassSpecGym track uses formula-filtered pools, so it is formula-conditioned and excluded. Its pool-size sweep on Spectraverse is relevant background. The unversioned PDF URL returned 404 (14:56:21Z); the `v1` URL worked.
- Yoo et al., [arXiv 2602.00547](https://arxiv.org/abs/2602.00547): different dataset, split and pool, and its description of the MassSpecGym pool does not match the MassSpecGym paper. No code link was found. Not a protocol match.
- MIST, JESTR, FLARE, MVP and de novo or simulation papers: context only.

## Endpoint, denominator, split, baseline and reuse analysis

| Question | What the sources reviewed establish | Status |
|---|---|---|
| Endpoint | Recall@k of the true structure among at most 256 mass-matched candidates. Not identification, not de novo, not a calibrated probability, not a clinical endpoint | Confirmed in sources read |
| Shortlist size | 1, 5, 20 reported (v1 mappings use 1 and 20; v2 mappings use 1, 5, 20) | Confirmed |
| Target presence | The target is candidate 0 in the pinned code and in the released candidate files checked. The papers state it. Jurgens et al. and Rakhshaninejad et al. also assume it. No target-absent measurement was found in the sources reviewed | Confirmed within sources reviewed |
| Pool construction | Official MassSpecGym pools: 1M, then 4M, then PubChem 118M, capped at 256. MSAlign's Spectraverse pools: local construction from the same three pools with target-derived mass (above) | Confirmed for the inspected code and papers |
| Candidate lists in the released MassSpecGym archive | 29,307 target-first lists, 12 to 256 entries, normalised non-isomeric SMILES. For `mces_1` test (17,556 spectra) the mean listed size is 253.88 and the mean distinct size is 238.95, and 92.27% of those spectra have a list with at least one duplicate string. These are descriptions of released files, not established scoring denominators or distinct-chemistry counts | Derived here; recomputed by the root review |
| Mass and formula | The formula split affects fold assignment only. Formula is not a model input for the formula-free configurations. Mass information enters through the pool filter and, per the v1 text, as a DreaMS input peak. Gaussian mass-error scorers are a separate v2 fusion component | Confirmed within sources read |
| Instrument and chemistry | MassSpecGym: positive ESI, [M+H]+ and [M+Na]+, curated reference spectra of known compounds. Spectraverse adds negative mode and more adducts. The released metadata files have no instrument column. Upstream rejoin and stratified evaluation were not performed | Confirmed; not performed |
| Domain shift | MCES split larger shift than formula split in both versions, on different scales | Confirmed |
| Splits and leakage | Molecule-disjoint folds by construction (no shared SMILES strings in the checked released split files for `mces_1`, `mces_2`, MassSpecGym formula seeds 1 to 3, Spectraverse formula seeds 1 to 3). Pretraining overlap of DreaMS and the molecule encoders with test data is unquantified in the sources read | Open |
| Denominators | Not printed in the MSAlign papers. Released-file counts (not scoring denominators): MassSpecGym `mces_1` test 17,556 spectra, `mces_2` test 19,429; MassSpecGym formula seeds 1, 2, 3 test 10,648, 11,148, 11,461; Spectraverse formula seeds 1, 2, 3 test 26,679, 25,693, 27,012. Whether released seeds are the published seeds rests on the README and is unverified | Derived; linkage unverified |
| Uncertainty | v1: none printed. v2: standard deviation, divisor not stated in Table 3, over 3 splittings or two MCES variants. MassSpecGym original: Table 3 prints 99.9% confidence intervals from 20,000 bootstrap resamples; the caption does not establish the resampling unit, and molecule-cluster resampling was not established in this review. Bootstrap by unique molecule is reported by none of the sources read | Confirmed |
| Controls and baselines | MassSpecGym reports a Random control; FFN and DeepSets appear in MassSpecGym and MSAlign; Emb-Cos originates with De Waele et al. A matched spectrum-blind control is motivated by Gupta and Skinnider and by Liu et al. A standalone mass-error ranking is not reported separately in MSAlign | Confirmed within sources read |
| Checkpoint and evaluator identity | Evaluator is in the pinned code. DreaMS weights and MolDeBERTa are named. No MSAlign checkpoint was found in the pinned repository or inspected Zenodo record. v1 molecule-encoder checkpoint is not named | Open |

Licence and access metadata, retrieved 2026-10-07. Paper, code, data and weight licences are separate. This table records the metadata observed. It does not assess legal consequences for derived embeddings, fine-tuned weights or redistribution.

| Asset | Licence metadata observed | Notes |
|---|---|---|
| MSAlign paper v1, v2 | CC BY 4.0 (arXiv abs page) | |
| MSAlign code | MIT (GitHub licence endpoint at pinned commit) | |
| MSAlign data archives (Zenodo 22830464) | CC BY 4.0 (record metadata) | Underlying spectra come from MassSpecGym (MIT) and Spectraverse (CC BY 4.0) |
| MassSpecGym data and code | MIT | Datasheet states no third-party restrictions; per-library licences not itemised |
| MolDeBERTa weights | Hugging Face API tag `license:cc-by-nc-nd-4.0` | The MSAlign README instructs accepting model terms and setting `HF_TOKEN`; the API returned `gated: false` at retrieval. Both observations are recorded and not reconciled |
| ChemBERTa-2 13M variant (v2 ablation only) | Apache-2.0 tag (`Derify/ChemBERTa_augmented_pubchem_13m`) | v1's checkpoint identity is not stated |
| DreaMS weights and article | CC BY 4.0 | Code MIT |
| Gupta and Skinnider preprint | CC BY-NC-ND 4.0 | |
| De Waele; Jurgens; Rakhshaninejad; Liu | CC BY 4.0 | |

## Explicit unresolved conflicts and bounded limitations

1. v1 source labelling. The historic record labels `2605.19752v1` but its URL serves v2. Hash and version label are consistent with each other and with the explicit v1 URL. The URL fields were not corrected, and the earlier 406 is undiagnosed.
2. v2 Table 3 caption against Section 5.1 for MCES. The caption says "3 random splitting". Section 5.1 and the Table 2 caption describe two validation/test-swapped variants. The released code and archive (`mces_1`, `mces_2`, verified as an exact swap) are consistent with two variants, but two released files do not prove how the published spread was calculated. The contradiction stays unresolved. The divisor of the standard deviation is not stated for Table 3.
3. v1 against v2 values. Same configuration names, different numbers, a different MSAlign encoder, hyperparameters, baselines and seeds. No source read reconciles them. The catalogue keeps them in separate protocols.
4. v1 MCES-split FFN and DeepSets cells. The v1 values (2.54 / 7.59 / 20.00 and 5.24 / 12.58 / 28.21) equal the MassSpecGym paper's published Fingerprint FFN and DeepSets + Fourier features values to printed precision. The v1 text says all baselines except MIST were re-implemented and DeepSets trained for 50 epochs. Whether these cells are re-runs or copied values is not established.
5. Evaluation risks and MSAlign. Liu et al. show candidate formatting and candidate-pool shortcuts affecting other models on MassSpecGym files, including a DreaMS-based aligner. MSAlign v1 and v2 state RDKit canonicalisation, and the pinned v2-era code normalises ground truth and candidates. A v1 implementation was not found in the sources inspected, so the v1 pipeline is unverified. That is not proof that no v1 implementation exists, and the audit does not establish the cause of any MSAlign result. Candidate-pool bias that canonicalisation does not remove remains a reason for a matched spectrum-blind control.
6. Pretraining overlap. DreaMS (24M MassIVE spectra) and the molecule encoders may have seen test spectra or molecules. MassSpecGym v1.5 ships retrained DreaMS, but no source read quantifies the overlap for the public weights MSAlign uses.
7. Release artefacts. No checkpoint, `DATA.md` or runtime was found in the pinned repository and inspected Zenodo record; the README badge label and link disagree. Evaluator, split and candidate files are available; trained models were not found in those sources.
8. Denominators and checkpoints. Released split files and archive counts do not prove the exact published scoring denominators, run counts or checkpoints. The archive date (2026-09-18) postdates v1 and precedes v2.
9. Spectraverse counts. Paper (488,630 spectra, 44,237 molecules), archive (488,630 metadata rows, 44,302 `unique_smiles.csv` rows) and MSAlign Table 7 (488,797 pairs, 44,307 molecules) differ. No source read explains it.
10. Independent replication. None was found in the dated search. v1 and v2 are one group's work.
11. Target absence and abstention. No source reviewed measures retrieval when the true structure is missing or reports false nomination. Two 2026 papers name it as an open setting. The execution gap is tracked in rewire-benchmarks #31.
12. v1 molecule-encoder identity. v1 names ChemBERTa and gives 92M parameters pretrained on 110M SMILES but no checkpoint. v2's ablation lists ChemBERTa-13M. Which checkpoint produced the v1 MSAlign cells is not stated.
13. Instrument strata. Not available in the released metadata. An upstream join was not attempted.

## Answers to the #335 evidence-discovery checklist

| Item | Result within this pass |
|---|---|
| Follow code and data links; verify downloadable | Code (MIT) and data (CC BY 4.0) downloadable. Both archives' size, MD5 and SHA-256 recorded. No checkpoint found in the pinned repository or inspected Zenodo record. `DATA.md` returned 404 |
| Record current paper version and difference from v1 | Done |
| Split manifests, candidate rules, neutral-mass conversion, ionisation, duplicate handling, target identity | Split and candidate rules from pinned code. The inspected local construction takes mass from the target structure. Adduct and ionisation enter as metadata. Released MassSpecGym lists contain duplicate normalised strings. Target identity is the normalised non-isomeric canonical SMILES |
| Inventory independent library or instrument datasets | NPLIB1 (v1 only) and Spectraverse. Instrument-held-out evaluation was not performed and no upstream rejoin was attempted |
| Extract Table 3 with denominators and provenance | Values re-verified. Released-file counts recorded; scoring denominators not established |
| Track pretraining overlap | Unresolved (item 6) |

## Scope boundary

- Every quantitative value in the sources above is a retrospective prediction on library reference spectra with known structures. None is an authenticated identification outcome, a prospective experimental result or a clinical performance estimate.
- Target-present shortlist recall is not an identification probability and not a clinical outcome. No replication, checkpoint identity check, target-absence evaluation or external validation was performed in this pass.

## Bounded access notes

- `https://arxiv.org/pdf/2601.17204` returned 404 at 14:56:21Z; `.../2601.17204v1` worked at 14:56:40Z (a different request, not a repeat).
- `DATA.md` at the pinned commit returned 404 (14:49:27Z), not retried.
- Rakhshaninejad results, Gupta and Skinnider supplementary figures and the Spectraverse candidate map were not read. De Waele's code repository was not inspected.
- rewire-database issues #31 and #40 and profile issues #106 and #167 were not read.
- Wait shells that matched themselves with `pgrep` were stopped after the transfer completed; the corrected approach uses the actual process handle.

## Cached source bytes (git-ignored)

All under `workbench/msms-shortlisting-20261007/`. Request times and full SHA-256 are in `primary/retrieval-log.tsv`. Hashes for every cached file except the two archives and the extracted files are in `primary/SHA256SUMS.txt`; extracted key files have their own sums files. Key items:

| Path | Source | UTC retrieval | SHA-256 |
|---|---|---|---|
| `primary/msalign/msalign-pdf-v1.body` | arxiv.org/pdf/2605.19752v1 | 2026-10-07T14:47:38Z | `7395a55141ee7916741b7d9e6d4f42a1d3a03217a36ce6824ac3ff48afd4f26f` |
| `primary/msalign/msalign-pdf-v2.body` | arxiv.org/pdf/2605.19752v2 | 14:47:42Z | `a31d1167b0ded72f64717881dd6cba0946a56b495d76f169d8e44115c3266fda` |
| `primary/msalign/text/v1.txt`, `v2.txt` | `pdftotext -layout` of the PDFs | derived | not hashed |
| `primary/msalign/msalign-html-v1.body`, `-v2.body` | arxiv.org/html/2605.19752v1, v2 | 14:48:08Z, 14:48:04Z | `27eafb0a...`, `1e0ddf62...` |
| `primary/msalign/msalign-src-v1.body`, `-v2.body` | arxiv.org/e-print | 14:48:17Z, 14:48:12Z | `58093e3b...`, `cf8db9db...` |
| `primary/msalign-code/` | GitHub API and raw files at commit `c2ef425b...` | 14:49:06Z to 15:02:53Z | per file in log; `src/preprocessing_encode_dreams.py` `e22d38daf322250dd580f9809c9645f092ba0fce12fe1443e249b513dcd6af0d` |
| `primary/zenodo/*.body` | Zenodo record APIs 22830464, 19927403, 17870921 | 14:50:18Z to 14:50:23Z | per file in log |
| `primary/zenodo-data-massspecgym/massspecgym.zip` | Zenodo record 22830464 file | download start 14:50:31Z | `6dbe62b0e69232ea63993cc92dc0126989c82aee286c00f0f837cd35b8cd91f1` |
| `primary/spectraverse-zip/spectraverse.zip` | Zenodo record 22830464 file | download start about 14:58Z | `71a07e8336e0169e4d085e927823fd4ff4661aa45df675585480b654c3e81d9e` |
| `primary/extracted-massspecgym/`, `primary/extracted-spectraverse/` | selected members of the archives | derived | `SHA256SUMS-key-files.txt` in each |
| `primary/lit/massspecgym-pdf-v1.body`, `-v3.body` | arxiv.org/pdf/2410.23326v1, v3 | 15:01:48Z, 15:01:53Z | `82176d50e8947c8b9baa2a0d91493f5680c0e4c7e25a2266ff7879f48a58c40c`, `5b77461f33ad974d6fa4faa36393bbc71241101b1a0528edc2d0bcc93a1afb97` |
| `primary/lit/itw-pdf-v1.body` | arxiv.org/pdf/2606.19624v1 | 14:50:59Z | `81c23b4035c50661c77594fde0071798a13692cfb4f6b5ddb56e73587efa9fea` |
| `primary/lit/dewaele-pdf.body` | arxiv.org/pdf/2602.16507 | 14:51:08Z | `c298ff38ce146a885bf6bb769ab9ac03758eb2e233b8ad5a25b2af3576d17ed1` |
| `primary/lit/gupta-biorxiv-pdf.body` | biorxiv.org 722532v1 full PDF | 14:52:33Z | `1601a3705fcea7623cd7888c216684b7315c9e33662f400aab79cf94a0cf6544` |
| `primary/lit/crossinst-pdf.body` | arxiv.org/pdf/2602.00547 | 14:51:16Z | `de9992e94559f95277e2e408235a6fbbfde0fb709b538c156516026af2c21613` |
| `primary/lit2/dreams-nature.body`, `dreams-esm.body` | nature.com article and supplement | 14:53:13Z, 14:53:17Z | `b22ae3fe...`, `e93f8ec0...` |
| `primary/lit2/spectraverse-pmc.body`, `casmi2022.body` | PMC12903054; Fiehn Lab page | 14:53:47Z, 14:53:50Z | `2cafcfb7...`, `6d432659...` |
| `primary/lit3/selective-pdf.body` | arxiv.org/pdf/2603.10950 | 14:54:49Z | `ee5ebbb4e86e8368450dca6e6bd48c6520fa061d4b4d3414a23ea6dd9e2982ca` |
| `primary/lit3/conformal-pdf.body`, `featurization-pmc.body` | bioRxiv PDF; PMC13329996 | 14:54:53Z, 14:55:03Z | `bfcf1618...`, `0ebb75fa...` |
| `primary/lit4/specbridge-pdf-v1.body` | arxiv.org/pdf/2601.17204v1 | 14:56:40Z | `8ec7f0b4...` |
| `primary/models/*.body` | Hugging Face and Zenodo model and dataset API records | 14:58:33Z to 14:58:42Z | per file in log |
| `issues/rewire-benchmarks-issues-all-logged.json`, `issues/rewire.it-335.json` | `gh issue list` and `gh issue view` | 15:06:01Z, 14:58:18Z | `1fd76ef7...`, `a3f4d5f0...` |

## Review

Automated source review with local extraction only. No skills, substitute agents or scientific model execution. Corrected after independent review; the corrected draft awaits independent review. Intake note: `workbench/msms-shortlisting-20261007/intake-plan.md` (git-ignored).
