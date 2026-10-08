# Prioritising variants for splicing experiments: bounded evidence research, 2026-10-08

Case 13 of 17 in the evidence programme ([rewire-benchmark-data #3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3); benchmark programme [rewire-benchmarks #25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), items B339 and BL339). Use case `use-case-splicing-follow-up`, slug `splicing-follow-up`, title "Prioritise variants for splicing experiments". The article issue is [rewire.it #339](https://github.com/rewire-bio/rewire.it/issues/339) ("[Article plan] Choosing a model for splicing follow-up experiments"). The mapping was read from the #339 body, from `data/omics/use-cases/inputs.json` and from the B339 and BL339 entries in #25.

Starting commit: producer `main` a8ca87ad7048e4744fa72c4aedd8dfd0311af575 (reviewed case 12 merge). No catalogue, mapping, definition, release, builder, test or generated file was changed, and the twelve preceding dossiers are untouched. Baseline hashes: `data/omics/use-cases/inputs.json` `59980e455a2608490a126a5770314b9897426f89db61d5ea7111eb0dd8bac0cd`; `data/omics/use-case-coverage-20260930/experimental/records.jsonl` `6630893bbdadd66616583c5deb4dabd468460a920f7fa83be8de2d1d69554731`; `data/omics/amp-coverage-20261007/existing-c/inventory.json` `b3a79c51c96d988b0882bd0f73d1201297790b1b847818da9ea6416a3c8c4873`.

No model, predictor or pipeline was run or trained, no neural weights were downloaded, no model or pickle file was opened, no restricted or patient-level data was obtained, nothing was paid for, bypassed or requested, and nobody was contacted. Inspection was documentary only: JSON, Markdown, HTML and XML were opened as text. Times are UTC request starts from the ignored `workbench/splicing-20261008/raw2/retrieval-log.tsv` and `queries.tsv`. This is a research intake awaiting root review, CI and merge. It claims no execution, replication or clinical validation. A pre-existing ignored directory `workbench/codex-splicing-review-20261008` was left untouched.

## Disposition in brief

1. The stored evidence is adequate for the current decision and is unchanged. The pinned matched-study `report.json` was re-fetched; its bytes equal the stored copy (SHA256 `259eb542313914b9114c21b62891f022c0ec0d9e3337196b8d7b2c6d5ae54ef3`), as do the stored `manifest-v1.json`, `provenance.json`, `verification.json` and exclusion verification. All 16 stored matched-study results (S0, S1, P0, P1 by P@100, recall@100, AP, AUROC), and the six stored historical v2 values read, equal the source values digit for digit (section "Verification").
2. What the evidence measures: ranking of held-out MFASS SNVs by exon-recognition change in an artificial minigene reporter, by SpliceAI and Pangolin run in genomic context under one declared annotation. It is not patient RNA, not pathogenicity and not diagnostic yield.
3. The new finding of this pass is a July 2026 preprint that benchmarks four predictors on the whole public MFASS table (27,733 labelled SNVs). It is a different population (27,733 labelled variants against the 8,297 scored held-out subset) and scoring protocol from the matched study. Its numbers are not reproduced in this dossier and must not be combined with, or used to adjust, the stored results. It is not peer reviewed, and its code and scores were not audited.
4. Other recent work found is a different endpoint or population (other minigene datasets, ClinVar sets, RNA-seq cohorts, ClinGen guidance on using splicing evidence). It supports the existing limitations and adds no result that changes the decision.
5. Source conflicts are recorded and left unresolved (section 6). None changes a stored value.
6. Disposition: docs-only. No scientific record, mapping or definition change is needed. Optional extensions are future work, declined for the current intake, and are not pending required work. The focused planning gap was reviewed and posted by Codex as [rewire-benchmarks #39](https://github.com/rewire-bio/rewire-benchmarks/issues/39), linked to #25, #3 and #339. The ignored `workbench/splicing-20261008/benchmark-issue-draft.md` is the pre-posting version; the posted body is authoritative.

## Existing inventory (unchanged)

Definition (`inputs.json`): decision "inspect the matched MFASS configurations and their limitations before selecting a method and designing validation in the intended experimental setting". Inputs: human SNVs with alleles, assembly and gene/transcript context; the intended experimental endpoint and the number of variants that can be followed up. Exclusions: indels and other variant types; patient-RNA effects, pathogenicity, diagnostic yield and treatment decisions; pooling the matched study with historical MFASS runs. Nine evidence gaps are recorded. How published releases and rewire-database consume the records is outside this review and was not inspected.

Mappings for this use case (four, all active, all relevance `proxy`):

| Mapping | Protocol | Scope |
|---|---|---|
| `use-case-mapping-splicing-mfass-matched-v1` | `rewire-mfass-matched-v1-protocol` | S0, S1, P0, P1 on one scored population |
| `use-case-mapping-20260930-339-25925e279972` | `rewire-mfass-v2` | historical k-mer plus position baseline and training-prior control only |
| `use-case-mapping-amp-20261007-feng-splice-acceptor` | `amp-feng-20261007-protocol-splice-acceptor` | DNA foundation-model acceptor sequence classification, a different endpoint |
| `use-case-mapping-amp-20261007-feng-splice-donor` | `amp-feng-20261007-protocol-splice-donor` | same, donor |

DNABERT2 is a pipeline, not an exact configuration, and stays outside the exact mapping. It was not re-examined here.

## Verification of stored values and population against the original reports

Source: `rewire-bio/rewire-benchmarks` at revision `093fd1ae198c80ce34408d84d6543bca4fc538f2`, `benchmarks/mfass/results/matched-annotation-v1/`. Fetched 2026-10-08T11:57:20Z to 11:57:21Z, all HTTP 200:

| File | SHA256 | Equals stored copy in `data/omics/reviewed/mfass-matched-annotation-v1/` |
|---|---|---|
| `report.json` (29,614 bytes) | `259eb542313914b9114c21b62891f022c0ec0d9e3337196b8d7b2c6d5ae54ef3` | Yes |
| `manifest-v1.json` | `3fce70dd0bd96cb92d9d0e41287f31e62ddc4ecb8d188615093a873e952433e8` | Yes |
| `provenance.json` | `6304e9625e793f24cccdc2669d092e6cdcc7a508a7f789967e726816fffde062` | Yes |
| `verification.json` | `13356c3f1bd7055b11cc0ab1b2b86a7ee586c51d0c984fad6e39ce8948d662fa` | Yes |
| `README.md` | `8f1c5e7d39ab634fef15f6392f7b06d5dc05f28dae439074665a995c9929fb1f` | not stored |

Exclusion verification (commit `4be7a98e2553fa2378c29625b13eb3e8ac2e58fb`, `docs/mfass-matched-study-exclusions/verification.json`, 11:58:27Z) has SHA256 `5d2099db4cf6f01432fd88c7db949da89ab9917940705fd0eaa1fb7c9354d46a`, equal to the stored copy.

Matched population, from `/conditions/*/coverage`, `/conditions/*/metrics` and the exclusion verification: denominator 8,324 held-out variants; 8,297 scored in each of S0, S1, P0 and P1; 27 unscored in each (23 assembly-orientation mismatches, 4 outside the canonical transcript span); 314 positives scored (of 315) in 460 scored groups (of 463). The scored-ID hash is `89b5568e2d819b892ba5e6db680d85e41224d6a69fec4b09a85c5075cade39d8` in all three contrasts and in the exclusion verification, so the four conditions share one scored set. Missing scores are coverage gaps, not negative predictions.

Stored results (inventory `data/omics/amp-coverage-20261007/existing-c/inventory.json`) against `report.json` `/conditions/{S0,S1,P0,P1}/metrics/*`, compared as exact decimal strings and as binary64 values. All 16 match, each with eligible 8,324, scored 8,297 and missing 27.

| Condition | P@100 | Recall@100 | AP | AUROC | Tie state at the 100th score |
|---|---|---|---|---|---|
| S0 (SpliceAI 1.3.1, mask 0) | 0.63 | 0.20063694267515925 | 0.29537139738069396 | 0.8035576794956798 | 1 tied, 1 slot |
| S1 (SpliceAI, mask 1) | 0.65 | 0.2070063694267516 | 0.3125881842529626 | 0.8148394159244446 | 2 tied, 2 slots |
| P0 (Pangolin 5cf94b8 plus per-gene mask patch, mask False) | 0.65 | 0.2070063694267516 | 0.3886980279221367 | 0.8763341447710142 | 1 tied, 1 slot |
| P1 (Pangolin, mask True) | 0.66 | 0.21019108280254778 | 0.4106314557636091 | 0.8725933133386153 | 3 tied, 2 slots |

Ties come from `/conditions/*/ties`; the registered tie break is a label-independent permutation. The report README states that any label-independent tie order gives P1 a P@100 of 0.65 or 0.66, so the P1 minus P0 P@100 difference is +0.00 or +0.01. The S1 minus S0 and P0 minus S0 P@100 values do not depend on tie order (README, "Reading the results"). Condition intervals are not recorded (stored `uncertainty` is null). The three paired contrasts (S1 minus S0, P1 minus P0, P0 minus S0; 2,000 whole-group bootstrap draws, seed 20260914) are intervals on differences, not on any one condition. For P@100 two lower bounds are exactly 0.0 and one is -0.0326; the README explains that P@100 moves in steps of about 0.01 so many draws give exactly zero. Nine intervals are unadjusted, the test outcomes had been inspected earlier, and the README labels the study exploratory and not confirmatory. The review of the original run was automated (Claude) with later computational Codex checks; none is human review or independent reproduction.

Codex independently fetched the report, manifest, provenance, verification and README from the exact `093fd1ae…` revision (all archived files equal in bytes), the prior training-prior report (3,946 bytes, SHA256 `89e06a2f…`) and the prior README (2,988 bytes, SHA256 `2115525b…`), matching this worker, and independently checked the four condition metrics, the three paired contrasts, the ties and the exclusion JSON. It also independently re-fetched the Pangolin paper XML (118,521 bytes, SHA256 `c51d34f0bc17ffd34ee5c7caf4bbf627edd9f75f57497c8d6b133f405ec4c307`) and the Smith and Kitzman XML (206,841 bytes, SHA256 `5aceff067af63ab59400ade7dd7db563a16fc7f4d6db6fa55d5b34689f7a0769`), with hashes equal to those recorded here.

Historical v2 values read: `baseline-kmer-position-v2.json` at `bee9133b83f3aedaf2bbb9013f1875515845607e` (SHA256 `9a0b78674cc714177fec6e8c487588d6186d4fe93d6d7dbcb48bed6858885e15`, 11:58:29Z) gives P@100 0.61, AP 0.2864167459589237, AUROC 0.7779498064677238 on 8,324 of 8,324 variants (315 positives, 463 groups), equal to the stored records (the AP precision correction in `data/omics/audits/mfass-ap-correction.json` is consistent with the source). The training-prior report at `1663d1f04b2bbd6dfcff77fea78129d30b0de191` (`research/mfass-null-2026-09-21/evidence/training-prior.report.json`, 3,946 bytes, fetched 11:58:28Z, SHA256 `89e06a2f7229f16b980254a6589eb808ec89137018388db98719beb72324f56a`, recomputed from the saved bytes in this correction pass) gives AUROC 0.5, AP 0.037842383469485825, P@100 0.04 with all 8,324 scores tied; its README states the 4 of 100 reflects one fixed tie break and is not an estimate of chance yield. These match the stored `mfass-prior` records. The historical population has no assembly-orientation exclusions and different annotations, so it is a separate comparison group.

Relationship between the populations (from the training-prior README): the corrected MFASS cohort has 27,733 labelled variants, split into 19,409 training (735 positives) and 8,324 held-out (315 positives). The matched study scores a subset of the held-out part.

The upstream MFASS issue on the assembly finding, [KosuriLab/MFASS #1](https://github.com/KosuriLab/MFASS/issues/1), was re-read at 11:58:28Z: state open, created 2026-09-25T11:14:58Z, 0 comments. Author confirmation is therefore still not established. The repository `KosuriLab/MFASS` shows no licence in the GitHub API (11:58:28Z to 12:01:08Z); reuse terms for the cohort are unreported, consistent with the matched README, which withholds cohort reference bases for that reason.

## Search log (exact, dated)

Europe PMC REST search (`/europepmc/webservices/rest/search`, JSON), request starts on 2026-10-08. Results were screened by title and abstract, and full text was fetched only for sources used.

| ID | Time (UTC) | Exact query | Hits | Outcome |
|---|---|---|---|---|
| E1 | 11:58:41Z | `(TITLE:"SpliceAI" OR TITLE:"Pangolin" OR TITLE:"MFASS") AND (TITLE:"benchmark" OR TITLE:"evaluation" OR TITLE:"performance" OR TITLE:"assess" OR TITLE:"validation" OR TITLE:"comparison") AND PUB_YEAR:[2024 TO 2026]` | 6 | One relevant preprint (PPR1286688); the others are animal pangolin papers or an unrelated tissue workflow |
| E2 | 11:58:41Z | `(TITLE_ABS:"splicing" OR TITLE_ABS:"splice") AND (TITLE_ABS:"MFASS" OR TITLE_ABS:"massively parallel splicing assay" OR TITLE_ABS:"minigene") AND (TITLE_ABS:"SpliceAI" OR TITLE_ABS:"deep learning" OR TITLE_ABS:"prediction") AND PUB_YEAR:[2023 TO 2026]` | 117 | First 25 screened: mostly single-gene minigene studies; PPR1286688, the Canson et al. preprint (PPR1177159) and SeqSplice kept |
| E3 | 11:58:43Z | `(TITLE_ABS:"splice" OR TITLE_ABS:"splicing") AND (TITLE_ABS:"variant effect prediction" OR TITLE_ABS:"splice prediction" OR TITLE_ABS:"splicing prediction") AND (TITLE_ABS:"benchmark" OR TITLE_ABS:"benchmarking" OR TITLE_ABS:"systematic evaluation") AND PUB_YEAR:[2024 TO 2026]` | 3 | PLoS One 2026 SpliceAI reimplementation comparison (PMC13170886) |
| E4 | 11:58:43Z | `(TITLE:"OpenSpliceAI" OR TITLE:"SpliceTransformer" OR TITLE:"SpliceVarDB" OR TITLE:"AlphaGenome" OR TITLE:"splice-site prediction" OR TITLE:"splicing prediction") AND PUB_YEAR:[2024 TO 2026]` | 43 | First 25 screened. AlphaGenome Nature paper kept; Nat Genet 2026 review recorded (no access beyond abstract); regulatory-only AlphaGenome applications and plant or splice-site-only models excluded |
| E5 | 11:58:45Z | `(TITLE_ABS:"splice" OR TITLE_ABS:"splicing") AND (TITLE_ABS:"RNA-seq" OR TITLE_ABS:"patient RNA" OR TITLE_ABS:"transcriptome") AND (TITLE_ABS:"SpliceAI" OR TITLE_ABS:"Pangolin") AND (TITLE_ABS:"diagnostic" OR TITLE_ABS:"rare disease" OR TITLE_ABS:"yield") AND PUB_YEAR:[2023 TO 2026]` | 6 | Genome Med 2024 heart RNA-seq model (PMC11476204) read; others are different cohorts, not read |
| E6 | 11:58:45Z | `(TITLE_ABS:"splicing" OR TITLE_ABS:"splice") AND (TITLE_ABS:"saturation" OR TITLE_ABS:"massively parallel" OR TITLE_ABS:"MaveDB" OR TITLE_ABS:"high-throughput") AND (TITLE_ABS:"SpliceAI" OR TITLE_ABS:"Pangolin") AND PUB_YEAR:[2024 TO 2026]` | 4 | SeqSplice (Genome Res 2025, PMC12401047) |
| D1 to D9 | 11:59:47Z to 11:59:56Z | DOI or title lookups (`DOI:"10.1016/j.molcel.2018.10.037"`, `10.1016/j.cell.2018.12.015`, `10.1186/s13059-022-02664-4`, `10.1186/s13059-023-03144-z`, `10.1002/humu.24212`, `10.1038/s41467-024-53088-6`, a ClinGen splicing title query, `TITLE:"OpenSpliceAI"`, `TITLE:"SpliceVarDB"`) | 1 to 2 each | Metadata and licences resolved |
| W | not run by this worker | No web search engine query was run in this pass. The review reports a root web query at about 11:56Z on 2026-10-08, `SpliceAI Pangolin MFASS benchmark splicing variant prediction 2026 minigene annotation`, which surfaced the same SpliceConsensus preprint and repository and one further candidate, a minigene workflow (DOI 10.1136/jmg-2026-111675). That candidate was not retrieved or read by this worker, so its content, endpoint and relevance are unknown and it is not used | | |

Inclusion rule: a primary source that evaluates splice predictors against a functional or patient-RNA label, defines the MFASS or related assay, supplies licence or access facts for a method, or gives guidance on how splicing evidence enters variant interpretation. Excluded by scope: pure splice-site (sequence-label) classifiers, plant and non-human work, regulatory-only AlphaGenome applications, and single-family case reports. Titles and abstracts only, not read: the Nature Genetics 2026 review of splicing prediction (10.1038/s41588-026-02629-4), the Walker et al. ClinGen guidance (abstract only; AJHG 2023, 10.1016/j.ajhg.2023.06.002), the original MFASS paper (Europe PMC full text returned HTTP 500 at 12:00:30Z; not retried by that route), the Research Square preprint of Canson et al. (abstract only), and the remaining E2, E4 and E5 hits beyond those listed. Findings are bounded to these queries; no global absence or novelty claim is made.

## Findings

### 1. What is being labelled (distinctions)

- MFASS assays exon recognition in a minigene reporter in cells: each variant has a measured change in an exon inclusion index, and the benchmark label is a binary splice-disrupting call (Pangolin paper and the preprint describe the cut-off as a decrease of at least 0.5). It is a reporter outcome in one construct and cellular context.
- The matched study scores genomic context: SpliceAI and Pangolin read about the variant's surrounding genome sequence under one GENCODE 44 canonical transcript per gene, a shared GRCh38 FASTA and a 50-base distance. The prediction target (change in splice-site use) and the label (change in exon inclusion in a minigene) are related but different, as Smith and Kitzman also state for SpliceAI and Pangolin versus exon-inclusion tools.
- Patient RNA, transcript choice, tissue and pathogenicity are separate. The Smith and Kitzman discussion says a splicing defect found bioinformatically or experimentally still needs a separate pathogenicity step because the same inclusion change can matter differently across genes. ClinGen SVI guidance (Walker et al., abstract only) treats RNA splicing assay results and computational predictions as distinct evidence types with their own recommended use.
- Canson et al. (Research Square preprint, 2026-04-14, abstract only, not peer reviewed) report that traditional minigene RT-PCR results and patient-derived RNA results agree substantially but not completely, and that most of the massively parallel splicing assays they reviewed could not separate aberrant from natural splicing events. This is relevant to the reporter-to-patient step and is recorded from the abstract only, without its counts.
- None of this evidence gives a patient-level classification, a diagnostic yield or a recommendation.

### 2. The July 2026 MFASS benchmark preprint (new; separate population)

Znabu, Atif, Devkota, Alemu and Jackfin, "A Reproducible MFASS Benchmark of Splice-Disruption Predictors Reveals a Shared Exon-Interior Blind Spot", bioRxiv doi 10.64898/2026.07.21.739871, first public 2026-07-26 (Europe PMC), version 1, CC BY. Full HTML fetched 11:59:28Z (156,370 bytes, SHA256 `f5097b24e9ebf1eabe4369fe9931f9dbaa400552422ee762d60c04edcf8584f1`). Not peer reviewed.

- Population: 27,733 labelled MFASS SNVs. By the training-prior README this equals all labelled variants (19,409 training plus 8,324 held-out). The matched study uses only the 8,297 scored variants of the held-out part. The populations differ, and the preprint reports no fixed-budget (top-100) endpoint in the text read; whether it examined one is not audited.
- Models and scoring: SpliceAI, Pangolin and SpliceTransformer run with released weights through a third-party orchestration tool, MMSplice through its VCF interface, SPANR from precomputed MFASS scores. Each output is reduced to one disruption magnitude. Scoring uses the variant's real hg38 context. SpliceAI variants with no annotated gene were given a delta of zero; the authors report a sensitivity analysis restricted to nonzero SpliceAI scores. MMSplice is scored on a reconstructed single-cassette exon context, which the authors say likely understates it. Tissue-aware tools are used tissue-agnostically.
- Result as stated, qualitatively: the authors report Pangolin as the strongest of the four modern tools on their MFASS scoring, and all above an older baseline. They report that a simple consensus of the deep-learning scores, on an exon-grouped split, does not meaningfully improve on the best single tool, and that detection is weaker for variants away from the splice site, with a share of disrupting variants missed by every tool. These are source-reported under the authors' own protocol and were not independently validated here. Their figures are not reproduced because the methods and tables were not audited and are not needed for the exact use case.
- Limits stated by the authors: the predictors were trained on genomic and transcriptomic data and may have encountered the wild-type splice sites of these exons during training, so the authors call it a realistic rather than fully held-out benchmark; MFASS is a single-context minigene assay; the work is "not a claim of clinical validation". This statement concerns possible exposure of wild-type sequence and annotated sites. It does not say that MFASS test labels or the tested variants were in any predictor's training data, and no such exposure was audited here either way. Separately, the authors' consensus model was trained and tested on an exon-grouped split of the table; that governs only the consensus, not the three underlying predictors. The same possible wild-type site exposure applies in principle to the matched study and is not audited in this dossier. No claim about leakage is made.
- Access and reuse: code, per-tool scores and figures are said to be at `github.com/brhanufen/spliceconsensus` (MIT per the GitHub API, 12:01:07Z) with a Zenodo archive (doi 10.5281/zenodo.20948820). The repository and archive were not downloaded or audited here. Exact source commit, score files and whether the labels file redistributes MFASS data are unknown. MFASS cohort reuse terms are unreported (see above).
- Applicability: the preprint compares models on the whole table, with no matched annotation, no registered tie order, and a different score reduction for each tool. Its ties, coverage and exclusions at a fixed review budget are not reported in the text read. It reports full coverage of its variants, with minus-strand alleles normalised and SpliceAI variants outside an annotated gene set to zero. Because its population, zero-imputation and normalisation differ from the matched study, and equivalent row handling was not audited, it is unknown whether any of the 23 assembly-orientation exclusions correspond to rows it scored, or how. No cause is asserted for any numeric difference from the matched study.

### 3. Same assay, different protocols: why results are not pooled

| Source | Population and scoring (as stated by the authors) | Metric type |
|---|---|---|
| Matched study (this repo) | 8,297 of 8,324 held-out; genomic context; GENCODE 44 canonical transcripts; one score per variant over genes and sites | AP, AUROC and fixed-budget precision |
| Znabu et al. preprint | 27,733 labelled; hg38 context; its own score reduction per tool; SpliceAI zero-imputed outside annotated genes | AP, AUROC |
| Zeng and Li, Genome Biol 2022 (PMC9022248) | 27,733 variants; GRCh37 sequences; mean of an exon's 5' and 3' site scores; maximum across tissues | AUPRC |
| AlphaGenome paper, Nature 2026 (PMC12851941) | MFASS rare variants; processing is in the paper's methods, which were not read in full | auPRC |

The sources differ in population, assembly, annotation, score definition and metric. Each reports its own result under its own protocol as stated by its authors; none was independently validated here. The table shows that a single "Pangolin on MFASS" number does not exist, and no figure from another protocol should be placed beside the stored values. Their figures are deliberately not reproduced. For AlphaGenome the stored note in `docs/omics/alphagenome-2026-results.md` already treats the author's MFASS protocol as separate from rewire MFASS v2, and this review agrees.

### 4. Other benchmarks and resources (scope and access only)

| Source | What it is | Relevance and limits |
|---|---|---|
| Smith and Kitzman, Genome Biol 2023, PMC10734170, CC BY | Eight predictors against saturation massively parallel splicing assays and a BRCA1 saturation genome-editing set; not MFASS | Reports lower agreement for exonic than intronic variants, SpliceAI and Pangolin among the best, and large effects of gene-model annotation and score cut-off. Supports the matched-annotation design and the transfer caution |
| Riepe et al., Hum Mutat 2021, PMC8360004, CC BY-NC | Benchmark of deep-learning splice tools on functional splice assays | Retrieved but not read beyond metadata; no MFASS mention found by text search |
| SpliceTransformer, Nat Commun 2024, PMC11500173, CC BY-NC-ND | A tissue-specific splicing model | No MFASS mention found in the retrieved text; its performance on this endpoint is unknown from this source |
| OpenSpliceAI, eLife 2025, PMC12575001, CC BY | Re-implementation of SpliceAI for retraining; GitHub licence GPL-3.0 | No MFASS mention found. Independent comparison against the original is in the next row |
| PLoS One 2026, PMC13170886 | Original SpliceAI, OpenSpliceAI and CI-SpliceAI on several non-MFASS datasets | Reports similar behaviour on large canonical-site sets, a difference on deep intronic variants, and that default thresholds are poorly calibrated for deep intronic variants. Not an MFASS result |
| SpliceVarDB, Am J Hum Genet 2024, PMC11480807, CC BY | Database of experimentally assayed splicing variants, including MFASS-derived data by its own description | A candidate source for an independent cohort check, but overlap with MFASS and with predictor training sets is not audited here |
| Lesurf et al., Genome Med 2024, PMC11476204, CC BY | Myocardial RNA-seq plus genome sequencing; heart-specific splice model | Patient-tissue RNA with tissue-specific gene expression; compared with SpliceAI alone in a small proband validation set. Shows that tissue and cohort context change the problem, and is not transferable to MFASS |
| SeqSplice, Genome Res 2025, PMC12401047, CC BY | Multiplexed minigene assay for BRCA1 and BRCA2 isoforms | A minigene method with isoform-level readout, unlike a single inclusion index |
| Nat Genet 2026 review (10.1038/s41588-026-02629-4) | Review of AI splicing prediction | Abstract only; not read in full |

### 5. Code, data, weights and licences (kept separate)

| Item | Paper | Code | Data | Weights |
|---|---|---|---|---|
| SpliceAI | Cell 2019; full text not retrieved here | GitHub API reports the repository archived (retrieved 12:01:06Z) and licence "Other"; the LICENSE file (12:01:12Z) states source under PolyForm Strict 1.0.0 and models under CC BY-NC 4.0 for academic and non-commercial use | Training data per the paper, not examined | Non-commercial licence as above |
| Pangolin | Genome Biol 2022, CC BY | GPL-3.0 (GitHub API, 12:01:07Z); the matched study uses a per-gene masking patch, not upstream, recorded in its manifest | Training data per the paper, not examined | Licence of the weight files not separately established in this pass |
| OpenSpliceAI | eLife 2025, CC BY | GPL-3.0 | not examined | not examined |
| AlphaGenome | Nature 2026, open access | Apache-2.0 for `alphagenome_research` (GitHub API, 12:01:08Z). The paper states non-commercial use through an API and says source code, weights and some evaluation data are in that repository | Public data manifest in the paper's Supplementary Table 2, not obtained | The paper says weights are released there; terms of use of the weights and the API were not read |
| SpliceTransformer | Nat Commun 2024, CC BY-NC-ND | not examined | not examined | not examined |
| MFASS | Mol Cell 2019, full text not retrieved | `KosuriLab/MFASS` has no licence in the GitHub API | Reuse terms unreported | n/a |
| Matched study | exploratory report | Code and patch in `rewire-benchmarks` at the pinned revision | Predictions public; cohort alleles withheld in the public copies | n/a |
| Znabu et al. preprint | CC BY | MIT per GitHub API; not audited | scores said to be released; not audited | n/a |

No weights were downloaded. Whether any licence permits the intended Rewire use of a specific weight file is not decided here.

### 6. Explicit source conflicts, left unresolved

1. Pangolin on MFASS: the Pangolin paper, the AlphaGenome paper and the preprint each report a result for this assay under different scoring and populations (section 3). The reasons for the size of the differences are not established and no cause is asserted. This is a protocol difference to keep separate, not an endpoint conflict affecting a stored value.
2. Treatment of the assembly issue: the matched study excludes 23 variants as assembly-orientation mismatches and keeps them unscored. The preprint reports scoring all variants and says minus-strand alleles were normalised before scoring. Whether its handling is equivalent to the matched study's finding is not established. The upstream issue is open with no comment.

Not a conflict, but a pairing to keep straight: 8,324 variants, 315 positives and 463 groups describe the full held-out set, and 8,297, 314 and 460 describe the scored subset. The difference is the 27 exclusions. (A difference in how sources name the first author of the MFASS paper is a citation-formatting matter, not a result conflict, and the DOI and title identify the paper.)

### 7. Access, failed access and uncertainty

- Failed access, tried once and not repeated by the same route: Europe PMC full text for the bioRxiv preprint by its preprint ID (HTTP 500, 11:58:57Z; the bioRxiv HTML was then retrieved successfully); Europe PMC full text for PMC6599603, the MFASS paper (HTTP 500, 12:00:30Z). No challenge page was solved or bypassed.
- Not examined: the Zenodo archive and GitHub repository of the preprint, any supplementary tables of the papers, AlphaGenome methods for the MFASS protocol, and any overlap between predictor training data and MFASS exons, variants or labels. No leakage claim is made or denied.
- Uncertainty: the stored results have no per-condition intervals. Only the three paired contrasts have intervals, and those are unadjusted. The preprint's intervals are bootstrap intervals of AP, stated by the authors, and were not recomputed.

## Existing evidence versus the benchmark question

| Question | What stored evidence supports | What it does not |
|---|---|---|
| Which of S0, S1, P0, P1 ranks held-out MFASS reporter-disrupting SNVs best on one shared population? | AP and AUROC point values and three paired contrasts on 8,297 variants; Pangolin above SpliceAI in AP and AUROC without masking | A winner for the top 100 (P@100 differences not established; P1 tie-sensitive); condition intervals; effect of architecture alone |
| Does a simple control matter? | Historical v2 k-mer plus position baseline and a constant prior on 8,324 variants, kept separate | A paired comparison with the matched specialists on one population |
| Do newer predictors (SpliceTransformer, OpenSpliceAI, AlphaGenome) fit this question? | Reported by others on other protocols or populations, qualitatively only (sections 2 to 4) | Any ranking under the matched protocol, with the same annotation, tie handling and exclusions |
| Is there evidence for patient RNA, a different tissue or a diagnostic use? | Not in these records. Separate use case `patient-rna-splicing-validation` (rewire-benchmark-data #12, article #379) | All of it |

## Intake disposition

Docs-only. The 16 matched-study values and six historical values equal the immutable sources, the four mappings are correctly scoped as proxy evidence, and every limitation found is already stored or recorded here. No stored value, mapping or definition needs correction, and no scientific execution or human validation is required to close the intake.

Declined for the current intake (future work only; none is pending, and none is needed to close the case): (a) adding the preprint's whole-table results to the catalogue, which would add numeric records and would need an additive reviewed release, proposed only if ever wanted; (b) a corrected-input rerun if the upstream assembly finding is confirmed, which would be a new version; (c) running newer predictors, an optional comparator for any future study.

The planning gap, now posted as #39, addresses the B339 first milestone as it applies to this exact case: an independent reporter, exon or minigene-type study, or an eligible experimental cohort, with a prospective shortlist at a stated capacity and matched controls, ties and exclusions. Patient RNA is a separate use case (rewire-benchmark-data #12) and is not required here. The closed matched analysis (#19) used MFASS test outcomes that had already been inspected, so a fresh test must use data not seen in that way. Whether a suitable independent dataset exists was not established here; SpliceVarDB and the saturation assays in Smith and Kitzman are unaudited candidate sources only.

Deduplication: on 2026-10-08 from 12:01:16Z the title and body of all open and closed issues in `rewire-bio/rewire-benchmarks`, `rewire-benchmark-data`, `rewire-database` and `rewire.it` were searched for splic*, MFASS, SpliceAI, Pangolin, B339, BL339, minigene, "exon recognition", "tie order" and "patient RNA". Related items found: benchmarks #1, #11 and #19 (closed, historical and matched MFASS work), benchmarks #25 (parent, item B339, whose first milestone asks for an independent RNA-assay cohort and a frozen population before scoring), #30 (open, plans AMP priority execution and says not to repeat the MFASS study), benchmark-data #3 and #12 (parent programme and the patient-RNA use case), database #65 and #97, and rewire.it #339, #365, #366, #379. No existing issue is a focused gap for an independent reporter or exon study with a fixed-capacity shortlist and matched controls; #25 only names it as a milestone. This session's own search found no focused B339 child before posting. Codex independently repeated the deduplication over the bodies of all open and closed issues in the four repositories (304 issues in rewire.it) before posting [rewire-benchmarks #39](https://github.com/rewire-bio/rewire-benchmarks/issues/39), whose parent is #25 and which links #25, #3 and #339. The ignored `workbench/splicing-20261008/benchmark-issue-draft.md` is the pre-posting version; the posted body is authoritative. The case intake is complete as documentation only once Codex review, CI and merge are done; none of those is claimed here, and completion adds no execution and no clinical validation.

## Source hashes (SHA256 of fetched bytes)

| Source | Retrieved (UTC, 2026-10-08) | Bytes | SHA256 |
|---|---|---|---|
| Matched `report.json` | 11:57:20Z | 29,614 | `259eb542313914b9114c21b62891f022c0ec0d9e3337196b8d7b2c6d5ae54ef3` (equals stored) |
| Matched `manifest-v1.json` | 11:57:20Z | 21,012 | `3fce70dd0bd96cb92d9d0e41287f31e62ddc4ecb8d188615093a873e952433e8` (equals stored) |
| Matched `provenance.json` | 11:57:21Z | 10,534 | `6304e9625e793f24cccdc2669d092e6cdcc7a508a7f789967e726816fffde062` (equals stored) |
| Matched `verification.json` | 11:57:21Z | 14,614 | `13356c3f1bd7055b11cc0ab1b2b86a7ee586c51d0c984fad6e39ce8948d662fa` (equals stored) |
| Matched `README.md` | 11:57:21Z | 12,011 | `8f1c5e7d39ab634fef15f6392f7b06d5dc05f28dae439074665a995c9929fb1f` |
| Exclusion verification | 11:58:27Z | 1,990 | `5d2099db4cf6f01432fd88c7db949da89ab9917940705fd0eaa1fb7c9354d46a` (equals stored) |
| Training-prior README | 11:58:28Z | 2,988 | `2115525b87c4a4f44b0c7f3e6ff41aca3aa2b2cd5ffe0590c633e210bb559fe5` |
| Training-prior report | 11:58:28Z | 3,946 | `89e06a2f7229f16b980254a6589eb808ec89137018388db98719beb72324f56a` |
| MFASS v2 baseline JSON | 11:58:29Z | 1,877 | `9a0b78674cc714177fec6e8c487588d6186d4fe93d6d7dbcb48bed6858885e15` (equals the hash in the AP correction record) |
| `docs/mfass.md` at `f80cef7` | 11:58:28Z | 9,103 | `53f2d58c152be488bf1c7a322a4a09574e0c87192e9eac19aa1f780f8eb6559c` (context only) |
| Upstream MFASS issue 1 (API) | 11:58:28Z | 8,402 | `968f574f507478926d643f8ccb49d89a48e4f02ae7ed8fa549a25d2c3d541cdf` |
| Preprint core record (Europe PMC) | 11:58:57Z | 3,165 | `7c7c9c88b007564f390662520178a03dfde11d12e2eded04c3c22e58eb257e23` |
| Preprint bioRxiv HTML | 11:59:28Z | 156,370 | `f5097b24e9ebf1eabe4369fe9931f9dbaa400552422ee762d60c04edcf8584f1` |
| PLoS One 2026, PMC13170886 XML | 11:59:07Z | 159,910 | `dffe74cee7782cbdfdbc9423cf00f0a846b3d720b90b10e9732d6f768c485176` |
| SeqSplice, PMC12401047 XML | 11:59:08Z | 144,841 | `030e87824b76f2243d53a19b00b1098fcb47161f13c60fa4124b8cb95092b402` |
| Lesurf et al., PMC11476204 XML | 11:59:08Z | 199,434 | `ace043dfa773b8e399c31b64954270f62c9142408bcaa9e5ea8132a687150959` |
| AlphaGenome, PMC12851941 XML | 11:59:17Z | 189,148 | `50d10530afd474d85702813bc9c9e5431406515e44f3425d64603fdb647fee13` |
| Nat Genet review core record | 11:59:17Z | 5,360 | `73bcd4379bedb285ff5619a0a73c5257f4eaa7327a171674c522cab03fd1409f` |
| Canson et al. preprint core record | 11:59:18Z | 4,799 | `6cc1d6c00bb5adbbc072499040fe4288954eae735c58e561445d4b511cc695af` |
| Pangolin, PMC9022248 XML | 12:00:02Z | 118,521 | `c51d34f0bc17ffd34ee5c7caf4bbf627edd9f75f57497c8d6b133f405ec4c307` |
| Smith and Kitzman, PMC10734170 XML | 12:00:03Z | 206,841 | `5aceff067af63ab59400ade7dd7db563a16fc7f4d6db6fa55d5b34689f7a0769` |
| Riepe et al., PMC8360004 XML | 12:00:04Z | 185,439 | `595be5360a9d3d421c4d4b6adda30175b4048e1aa0b563eb7afd2b7850277112` |
| SpliceTransformer, PMC11500173 XML | 12:00:16Z | 243,114 | `ff8b49965c73338aabfa4f2369feb0976ab737067c24a36a70cc9b124cce2337` |
| OpenSpliceAI, PMC12575001 XML | 12:00:16Z | 399,066 | `01d82a32bd3268078894f517784e090c7fcccc36d40c3237712e03bcf9872d05` |
| SpliceVarDB, PMC11480807 XML | 12:00:17Z | 129,531 | `97236fb406630caede35582fa3167a500f814a44a43a3cb76a1cd184123213e4` |
| SpliceAI LICENSE | 12:01:12Z | not recorded | not recorded (read, not saved) |

The full list, including the failed requests, is in the ignored `workbench/splicing-20261008/raw2/retrieval-log.tsv`; saved sources are under `workbench/splicing-20261008/{raw,raw2,src,epmc}`. GitHub issue searches were made with `gh issue list --search` and are not hashed.
