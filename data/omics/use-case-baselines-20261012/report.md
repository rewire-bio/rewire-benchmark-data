# Proposed use-case baselines, 2026-10-12

Draft baseline claims for the 26 use cases in `data/entities/use-cases.jsonl`, for independent review (issue #121, `docs/use-cases.md` "Baselines"). Each claim in `batch.jsonl` is `needs_review` and has no review or pins.

## How this was done

- Baselines were chosen from the store: the configurations scored on each use case's active mappings (`deriveUseCaseInputs` in `shared/omics/use-cases.ts`), their `facets.method_types`, the collection plan's `baselines` text, the linked sources and the earlier use-case reviews. Where the evidence was thin I used general knowledge of the field, and say so in the decision notes.
- I did not re-read source artifacts. Each cited source was checked only to exist with status `source_checked` and no evidence concerns. The reviewer should confirm that each source supports the rationale as worded.
- "Same-data ML comparison" means an active mapping's protocol has a configuration whose `configuration_of` target is a baseline method and another configuration tagged `foundation_model` or `supervised_machine_learning`. Links by `uses_model` are not counted (see tumour DNA).
- Validation: the batch passes the validators `records -- add` runs before writing (record schema, vocabularies, declared attributes, derivations, `validateRecords` on store plus batch), and `deriveUseCaseInputs` runs on store plus batch with no error and publishes no baseline. A simulation that marks each claim `source_checked` and pins it with `claimPins` publishes all 26, so every method exists and every source is clean. I did not run the SHACL step (`npm run kg:shapes`) because of memory limits; `records -- add` runs it and restores the store if it fails. No store file was changed.
- Scratch scripts and intermediate files are in the session scratchpad under `baseline-proposer/` (dump, analysis, batch and report generators).

## Summary

| Use case | Baseline | Same-data ML comparison |
| --- | --- | --- |
| brca1-brca2-germline-interpretation | BayesDel under the ENIGMA specification | Yes (4 protocols) |
| cell-type-annotation-transfer | scmap-cell, linear SVM and logistic regression | No under current tags; yes once tagged |
| cnv-detection-characterisation | ExomeDepth, CNVnator, AnnotSV and ClassifyCNV | Yes, for classification only (3 protocols) |
| diagnostic-dna-pathogen-identification | Kraken2 and minimap2 with MEGAN-LR | No |
| diagnostic-genomics-model-execution | GATK Best Practices on CPU | No |
| diagnostic-rna-pathogen-detection | Kraken2 and Centrifuge | No |
| egfr-nsclc-actionability-resistance-evidence | BM25 keyword retrieval | Yes (1 protocol) |
| genetic-perturbation-response | Training mean, no change, additive and linear models | Yes (5 protocols) |
| mass-spectrum-molecule-shortlisting | MassSpecGym DeepSets fingerprint baseline | No under current tags; yes once tagged |
| patient-rna-splicing-validation | FRASER and OUTRIDER, with a MaxEntScan-based splice-site vote | Yes, for DNA prediction only (4 protocols) |
| phenotype-perturbation-selection | Random selection | No |
| plant-promoter-reporters | GC and motif linear regression | No under current tags; yes once tagged |
| plasma-ctdna-fragmentomics | ichorCNA | Yes (4 protocols) |
| plasma-ctdna-methylation | MethAtlas and CelFiE deconvolution | No under current tags |
| protein-variant-stability | FoldX and Rosetta | Yes (12 protocols) |
| rare-disease-candidate-ranking | Exomiser and PhenIX | Yes (6 protocols) |
| regulatory-variant-gene-follow-up | Distance to TSS and Activity-by-Contact | Yes (1 protocol) |
| rhodopsin-wavelength-transfer | BLASSO rhodopsin predictor | No under current tags; yes once tagged |
| somatic-small-variant-oncogenicity | ClinGen/CGC/VICC rules (OncoVI) and SIFT | Yes, for SIFT only (7 protocols) |
| splicing-follow-up | MaxEntScan | Yes (3 protocols) |
| structural-hypotheses-experiments | AutoDock Vina and ClusPro docking | Yes, for ligands only (2 protocols) |
| therapeutic-target-validation | Random and pathway-based selection | Yes (1 protocol) |
| tumour-dna-somatic-variant-detection | Mutect2 and Strelka2 | Yes (31 protocols) |
| tumour-rna-fusion-detection | STAR-Fusion and Arriba | No under current tags |
| unresolved-rare-disease-reanalysis | Manual expert reanalysis and Exomiser | No |
| utr-translation-baselines | k-mer random forest | No under current tags; yes once tagged |

14 use cases already have a same-data comparison. 5 have one in the evidence that the store cannot see because the ML configurations are untyped. The rest need the evidence-gap sentence, or new evidence.

## Per use case

### brca1-brca2-germline-interpretation

Which evidence-support methods improve BRCA1/BRCA2 variant review without increasing serious classification errors?

| | |
| --- | --- |
| Claim | `use-case-baseline-brca1-brca2-germline-interpretation` |
| Baseline | BayesDel under the ENIGMA specification |
| Method IDs | `uc-clinical-20260930-method-bayesdel` (BayesDel) |
| Rationale | The ClinGen ENIGMA BRCA1/BRCA2 specification uses BayesDel with fixed thresholds as its computational evidence (PP3/BP4), so a new predictor must beat it to change a classification. BayesDel is a naive Bayes score combining conservation and other predictors: a simple trained model, not a pre-machine-learning method. |
| Sources | `uc-clinical-20260930-source-enigma` (Evidence-based recommendations for gene-specific ACMG/AMP variant classification from the ), `brca-20261009-source-ramadane2025` (ACMG/AMP interpretation of BRCA1 missense variants: Structure-informed scores add evidence) |
| Collection plan baselines | Manual criteria-based review using the same evidence cutoff and ClinGen ENIGMA specification |
| Baseline scored on | 8 active protocols |
| Same-data ML comparison | Yes. BayesDel and AlphaMissense (Ramadane-Morchadi 2025); BayesDel and some 40 supervised predictors (Cubuk 2021). Caveat: the BayesDel configurations on these protocols are themselves tagged supervised_machine_learning. Protocols: `brca-20261009-protocol-cubuk2021-brca1`, `brca-20261009-protocol-cubuk2021-brca2`, `brca-20261009-protocol-ramadane2025-binary`, `brca-20261009-protocol-ramadane2025-pp3-bp4` |
| Proposed gap text | None needed. |
| Decision notes | Reviewer decision needed. BayesDel is what the VCEP specification uses, so it is the reference a new predictor must beat, but it is a trained naive Bayes score, not pre-machine-learning. A strictly pre-ML alternative is Align-GVGD, but its BRCA1/2 calibration overlaps the classifications it is tested on (Cubuk Discussion, recorded in the 2026-10-09 review), or a conservation score such as SIFT or phyloP. The full comparator in the collection plan, manual ENIGMA criteria review, has no method record. |
| Untyped configurations | 8 (listed in the appendix) |

Tag and link issues:

- BayesDel is tagged three ways: the method record has no method_types; the two ENIGMA configurations (`uc-clinical-20260930-bayesdel-enigma`, `uc-clinical-20260930-bayesdel-pejaver-generic`) have none; the Cubuk and Ramadane-Morchadi configurations are supervised_machine_learning. BayesDel is a naive Bayes score trained on labelled variants (Feng 2017), so supervised_machine_learning fits the vocabulary definition; the two ENIGMA configurations should match.
- Align-GVGD and the conservation scores (GERP, phyloP, phastCons, SiPhy, Grantham) are tagged specialist, which does not say whether they are learned. They are not trained classifiers; conventional_pipeline would let the website treat them as pre-ML rows.
- Six other configurations are untyped and unlinked: ENIGMA v1.0 manual curation, VarSome vs CanVIG-UK, Integrated VarCall, ACMG/AMP with SVI (t2), HECTOR, ENIGMA VCEP v1.1.0 (t3). Manual and rule-based ones fit conventional_pipeline; HECTOR (rule-based classifier under the ENIGMA specification) likewise, pending a source check.

### cell-type-annotation-transfer

Which annotation workflow can label my new dataset reliably and recognise unsupported cell populations?

| | |
| --- | --- |
| Claim | `use-case-baseline-cell-type-annotation-transfer` |
| Baseline | scmap-cell, linear SVM and logistic regression |
| Method IDs | `ucc-research-method-abdelaal-scmapcell` (scmapcell), `ucc-research-method-abdelaal-svm-linear` (SVM (linear kernel), scikit-learn), `ucc-research-method-linear` (Optimized linear logistic regression) |
| Rationale | Apart from manual marker-based annotation, which has no record, there is no pre-machine-learning annotation method; the field's simplest established comparators are nearest-reference projection (scmap-cell) and linear classifiers on expression. Abdelaal et al. 2019 found the linear SVM among the most accurate of 22 methods, and scTab uses tuned logistic regression as its reference. |
| Sources | `ucc-research-source-abdelaal-2019-paper` (A comparison of automatic cell identification methods for single-cell RNA sequencing data), `ucc-research-source-sctab-paper` (scTab: Scaling cross-tissue single-cell annotation models) |
| Collection plan baselines | Marker-based and nearest-reference annotation; Appropriate pinned Azimuth, CellTypist or scANVI workflows; Embeddings with a simple classifier where applicable |
| Baseline scored on | 3 active protocols |
| Same-data ML comparison | No under current tags; yes once tagged. `ucc-research-protocol-sctab-seed` scores logistic regression with scGPT (fine-tuned and frozen) and UCE embeddings, but all nine configurations there are untyped. `ucc-research-protocol-abdelaal-baron-human-intra` scores SVM and scmap-cell with scPred, also untyped. |
| Proposed gap text | Do not add the gap sentence; it would be false. Tag the scTab configurations instead (below), and the comparison appears. |
| Decision notes | Linear SVM and logistic regression are supervised classifiers, so under the vocabulary they are machine learning. They are named because nothing simpler is measured: the field's pre-ML practice, manual marker-based annotation, has no record. |
| Untyped configurations | 13 (listed in the appendix) |

Tag and link issues:

- 13 untyped configurations. `ucc-research-config-sctab-scgpt-ft` and `ucc-research-config-sctab-scgpt-zero` should be foundation_model (other configurations of `catalog-model-scgpt` are); `ucc-research-config-sctab-uce` foundation_model (UCE is tagged foundation_model in the Wu 2025 configurations).
- CellTypist, logistic regression, XGBoost, MLP, CIForm, scTab, scPred and the two linear SVM configurations: supervised_machine_learning (each is trained on labelled cells). scmap-cell: conventional_pipeline (nearest-reference projection with no training step).

### cnv-detection-characterisation

Which workflow detects and characterises copy-number changes accurately and helps an analyst assess the evidence?

| | |
| --- | --- |
| Claim | `use-case-baseline-cnv-detection-characterisation` |
| Baseline | ExomeDepth, CNVnator, AnnotSV and ClassifyCNV |
| Method IDs | `rare-reanalysis-20261009-method-exomedepth` (ExomeDepth), `cnv-20261009-method-cnvnator` (CNVnator), `cnv-20261011-zhang2026-method-annotsv` (AnnotSV), `cnv-20261011-zhang2026-method-classifycnv` (ClassifyCNV) |
| Rationale | ExomeDepth (exome) and CNVnator (genome) are long-established read-depth callers using statistical models of coverage, and AnnotSV and ClassifyCNV apply the 2020 ACMG/ClinGen CNV scoring rules. Detection and classification are separate steps, so each has its own reference. |
| Sources | `cnv-20261009-source-gabrielaite2021` (A Comparison of Tools for Copy-Number Variation Detection in Germline Whole Exome and Whol), `cnv-20261011-zhang2026-source-article` (Can automated copy number variation pathogenicity prediction tools replace manual review u) |
| Collection plan baselines | The conventional/author-introduced workflow measured in the linked primary source(s). |
| Baseline scored on | 11 active protocols |
| Same-data ML comparison | Yes, for classification only. AnnotSV and ClassifyCNV against dbCNV, X-CNV and MarCNV-ISV on the three Zhang 2026 protocols. No learned CNV caller is measured beside ExomeDepth or CNVnator. Protocols: `cnv-20261011-zhang2026-protocol-five-category`, `cnv-20261011-zhang2026-protocol-three-category-deletions`, `cnv-20261011-zhang2026-protocol-three-category-duplications` |
| Proposed gap text | No machine-learning CNV caller has been compared with ExomeDepth or CNVnator on the same data in the linked evidence. |
| Decision notes | Four methods because the use case covers two steps. A reviewer may prefer to keep only the detection pair and record classification separately. |
| Untyped configurations | 1 (listed in the appendix) |

Tag and link issues:

- `amp-config-dragen42-cnv-sv` is untyped and has no configuration_of link; other DRAGEN configurations are conventional_pipeline under `cnv-20261009-method-dragen`.

### diagnostic-dna-pathogen-identification

Which DNA sequencing classification workflow detects clinically relevant pathogens and handles contamination or organisms absent from the reference?

| | |
| --- | --- |
| Claim | `use-case-baseline-diagnostic-dna-pathogen-identification` |
| Baseline | Kraken2 and minimap2 with MEGAN-LR |
| Method IDs | `catalog-model-kraken2` (Kraken2), `dna-pathogen-20261009-method-minimap2` (minimap2), `dna-pathogen-20261009-method-megan-lr` (MEGAN-LR) |
| Rationale | Kraken2 is the most widely used exact k-mer classifier, and alignment to a curated reference (minimap2, with MEGAN-LR for long reads) is the most accurate established approach in the linked benchmarks. Both assign reads by sequence matching against a reference database. |
| Sources | `dna-pathogen-20261009-source-portik2022` (Evaluation of taxonomic classification and profiling methods for long-read shotgun metagen), `dna-pathogen-20261009-source-hall2024` (Pangenome databases improve host removal and mycobacteria classification from clinical met) |
| Collection plan baselines | The conventional/author-introduced workflow measured in the linked primary source(s). |
| Baseline scored on | 12 active protocols |
| Same-data ML comparison | No. The baseline is scored on 12 active protocols (Portik 2022, Hall and Coin 2024, Tisza 2026), but no configuration in this use case is tagged foundation_model or supervised_machine_learning. |
| Proposed gap text | No machine-learning method has been compared with Kraken2 and minimap2 with MEGAN-LR on the same data in the linked evidence. |
| Decision notes | Issue #121 proposes alignment-based classification alone. Kraken2 is added because it is measured on every linked benchmark and is the most widely used classifier; alignment is the more accurate reference in Portik 2022. MetageNN and BERTax (issue #121) would close the gap once ingested. |
| Untyped configurations | 0 (listed in the appendix) |

### diagnostic-genomics-model-execution

Which eligible model configuration and execution workflow can meet a diagnostic genomics team's resource, throughput and reproducibility constraints?

| | |
| --- | --- |
| Claim | `use-case-baseline-diagnostic-genomics-model-execution` |
| Baseline | GATK Best Practices on CPU |
| Method IDs | `model-execution-20261009-method-gatk-best-practices-cpu` (GATK best-practice germline pipeline (CPU)) |
| Rationale | The CPU GATK best-practice germline pipeline is the reference that accelerated and model-based workflows are timed and costed against. It is an alignment and statistical calling pipeline with no trained neural network. |
| Sources | `model-execution-20261009-source-samarakoon2025` (Benchmarking accelerated next-generation sequencing analysis pipelines), `model-execution-20261009-source-oconnell2023` (Accelerating genomic workflows using NVIDIA Parabricks) |
| Collection plan baselines | The conventional/author-introduced workflow measured in the linked primary source(s). |
| Baseline scored on | 5 active protocols |
| Same-data ML comparison | No. The GATK CPU pipeline is scored on the five Samarakoon 2025 protocols with Parabricks, DRAGEN and Sentieon, all tagged conventional_pipeline. GenomeOcean is scored only on its own FP8 protocols. |
| Proposed gap text | No machine-learning method has been compared with GATK Best Practices on CPU on the same data in the linked evidence. |
| Decision notes | On `model-execution-20261009-protocol-samarakoon2025-dv` the CPU configuration and the Parabricks configurations all run DeepVariant, so retagging would show the same model on CPU and GPU, not an ML-versus-baseline comparison. Keep the gap sentence even after retagging. |
| Untyped configurations | 1 (listed in the appendix) |

Tag and link issues:

- Parabricks configurations on the DeepVariant protocols (`model-execution-20261009-protocol-samarakoon2025-dv`, `-dv-version-h100`, `model-execution-20261009-protocol-oconnell2023-deepvariant`) are tagged conventional_pipeline but run DeepVariant, a convolutional network (`model-execution-20261011-model-deepvariant` is supervised_machine_learning).
- The two O'Connell 2023 CPU configurations (`model-execution-20261009-config-oconnell2023-aws-c6i-8xlarge`, `-gcp-n2-standard-32`) have no configuration_of link, so they will not be marked as baseline rows. `amp-config-dragen42-phase4-runtime` is untyped and unlinked.

### diagnostic-rna-pathogen-detection

Which RNA sequencing workflow detects RNA pathogens reliably in the intended specimen and distinguishes real detections from host/background contamination?

| | |
| --- | --- |
| Claim | `use-case-baseline-diagnostic-rna-pathogen-detection` |
| Baseline | Kraken2 and Centrifuge |
| Method IDs | `catalog-model-kraken2` (Kraken2), `rna-pathogen-20261009-method-centrifuge` (Centrifuge) |
| Rationale | Kraken2 (exact k-mer matching) and Centrifuge (FM-index matching) are the established read classifiers measured most often in the linked virus benchmarks. Nucleotide alignment to NCBI nt (SURPI+, CZ ID), the clinical laboratory workflow, has no method record. |
| Sources | `rna-pathogen-20261009-source-carbo2022` (Performance of Five Metagenomic Classifiers for Virus Pathogen Detection Using Respiratory), `rna-pathogen-20261009-source-devries2021` (Benchmark of thirteen bioinformatic pipelines for metagenomic virus diagnostics using data) |
| Collection plan baselines | The conventional/author-introduced workflow measured in the linked primary source(s). |
| Baseline scored on | 9 active protocols |
| Same-data ML comparison | No. Kraken2 and Centrifuge are scored on 9 active protocols (Carbo 2022, de Vries 2021, Tisza 2026); every configuration in the use case is conventional_pipeline. |
| Proposed gap text | No machine-learning method has been compared with Kraken2 and Centrifuge on the same data in the linked evidence. |
| Decision notes | Issue #121 proposes nucleotide alignment to NCBI nt (SURPI+, CZ ID). Neither has a method record, and the UCSF SURPI+ configuration (`amp-20261007-rna-pathogens-configuration`) has no configuration_of link, so it cannot be named. If records are added, SURPI+ is the better clinical baseline and this claim should be revised. |
| Untyped configurations | 0 (listed in the appendix) |

Tag and link issues:

- `rna-pathogen-20261009-method-lshvec` (LSHVec) is tagged conventional_pipeline but learns k-mer embeddings (locality-sensitive hashing followed by a skip-gram style model); supervised_machine_learning or foundation_model, after checking Meyer 2022. It shares no protocol with the baseline, so the answer above does not change.

### egfr-nsclc-actionability-resistance-evidence

Which systems retrieve correctly scoped sensitivity and resistance evidence for advanced EGFR-mutant NSCLC?

| | |
| --- | --- |
| Claim | `use-case-baseline-egfr-nsclc-actionability-resistance-evidence` |
| Baseline | BM25 keyword retrieval |
| Method IDs | `egfrnsclc-20261009-method-trec2020-pm-ascfda` (TREC 2020 PM system of team ASCFDA) |
| Rationale | BM25 ranking of abstracts by query-term frequency is the standard lexical retrieval baseline in the TREC Precision Medicine track, which neural rerankers must beat. The ASCFDA record stands for its submitted bm25 run; BM25 itself has no method record. |
| Sources | `egfrnsclc-20261009-source-trec2020-pm-overview` (Overview of the TREC 2020 Precision Medicine Track) |
| Collection plan baselines | Versioned knowledgebase lookup plus conventional manual primary-source review |
| Baseline scored on | 1 active protocols |
| Same-data ML comparison | Yes. On TREC 2020 PM Phase 1, ASCFDA's bm25 run against monoT5, duoT5 (h2oloo), CSIROmed, PINGAN NLP and UoGTr runs. This is abstract retrieval for precision-medicine topics, not EGFR-specific evidence scoping. Protocols: `egfrnsclc-20261009-protocol-trec2020-pm-phase1-relevance` |
| Proposed gap text | None needed. |
| Decision notes | The collection plan names knowledgebase lookup plus manual review. The CIViC protocols use CIViC as the reference, so CIViC is the truth there, not a competing method. BM25 is the pre-ML retrieval method actually measured. The method record is a TREC team (`egfrnsclc-20261009-method-trec2020-pm-ascfda`), which the website will mark as a whole; it has only the bm25 run, so that is safe today. A `BM25` method record would be cleaner; none exists. |
| Untyped configurations | 5 (listed in the appendix) |

Tag and link issues:

- Five untyped configurations: the three CIViC configurations (GPT-5 alone, GPT-5 with CIViC MCP, ChatGPT Agent Mode) and `ucc-clinical-egfr-config-qwen3-reranker-8b` should be foundation_model; `ucc-clinical-egfr-config-medcpt-ft` (fine-tuned cross-encoder) supervised_machine_learning or foundation_model.

### genetic-perturbation-response

Which prediction methods and controls should I test before using expression predictions to plan genetic perturbation experiments?

| | |
| --- | --- |
| Claim | `use-case-baseline-genetic-perturbation-response` |
| Baseline | Training mean, no change, additive and linear models |
| Method IDs | `perturbation-response-20261009-method-train-mean` (Train Mean baseline), `perturbation-ahlmann-20261011-method-no-change` (No change baseline), `perturbation-ahlmann-20261011-method-additive` (Additive baseline for double perturbations), `perturbation-ahlmann-20261011-method-linear-model` (Linear perturbation model (Ahlmann-Eltze et al. 2025)) |
| Rationale | There is no pre-machine-learning method for predicting expression responses; the established comparators are simple statistical controls: the training mean, no change, the sum of single-perturbation effects and a linear model. Benchmarks report that foundation models often do not beat them. |
| Sources | `perturbation-response-20261009-source-csendes2025` (Benchmarking foundation cell models for post-perturbation RNA-seq prediction), `perturbation-ahlmann-20261011-source-article` (Deep-learning-based gene perturbation effect prediction does not yet outperform simple lin) |
| Collection plan baselines | (none) |
| Baseline scored on | 5 active protocols |
| Same-data ML comparison | Yes. Training mean against scGPT and scFoundation on the four Csendes 2025 protocols; no-change, additive and linear models against CPA, GEARS, Geneformer, scBERT, scFoundation, scGPT and UCE on Norman double perturbations (Ahlmann-Eltze 2025). Protocols: `perturbation-ahlmann-20261011-protocol-norman-double`, `perturbation-response-20261009-protocol-csendes2025-adamson-pex`, `perturbation-response-20261009-protocol-csendes2025-norman-pex`, `perturbation-response-20261009-protocol-csendes2025-replogle-k562-pex`, `perturbation-response-20261009-protocol-csendes2025-replogle-rpe1-pex` |
| Proposed gap text | None needed. |
| Untyped configurations | 16 (listed in the appendix) |

Tag and link issues:

- 16 untyped configurations from GEARS 2023, PertEval-scFM and PerturBench, none linked to a method record: CPA, CPA + KG, GEARS (two), Biolord, SAMS-VAE, Decoder, LA, MLP baseline should be supervised_machine_learning; CPA (scGPT) and LA (scGPT) foundation_model; No Perturb, Mean baseline and Linear conventional_pipeline.
- `perturbation-response-20261009-method-random-forest`, `-elastic-net` and `-knn` configurations are tagged conventional_pipeline, but each is a regressor trained on perturbation data; the vocabulary's supervised_machine_learning definition fits.

### mass-spectrum-molecule-shortlisting

Which retrieval configurations merit validation when molecular formula is unknown and a researcher can examine only a short list of candidate structures?

| | |
| --- | --- |
| Claim | `use-case-baseline-mass-spectrum-molecule-shortlisting` |
| Baseline | MassSpecGym DeepSets fingerprint baseline |
| Method IDs | `uc20260930-model-massspecgym-deepsets-fingerprint-predictor` (MassSpecGym DeepSets fingerprint predictor) |
| Rationale | The linked evidence has no pre-machine-learning retrieval method, such as spectral library search or combinatorial fragmentation. The simplest established comparator is the benchmark's own DeepSets fingerprint predictor, a small neural network that ranks candidates by predicted-fingerprint similarity. |
| Sources | `part2-massspecgym-arxiv-v1` (MassSpecGym: A benchmark for the discovery and identification of molecules) |
| Collection plan baselines | (none) |
| Baseline scored on | 3 active protocols |
| Same-data ML comparison | No under current tags; yes once tagged. The DeepSets baseline shares the three MSAlign v2 protocols with Emb-Cos, JESTR and MSAlign, all untyped. The four MSAlign Table 3 protocols have DeepSets configurations with no configuration_of link, so the baseline is not marked there. |
| Proposed gap text | Do not add the gap sentence as written. The baseline is itself a small neural network, so the honest gap is: "No pre-machine-learning retrieval method, such as spectral library search or in silico fragmentation, has been measured on the same data in the linked evidence." |
| Decision notes | No meaningful pre-ML method is measured. Spectral library search, MetFrag or a random-candidate control would be the pre-ML references; none has a record. |
| Untyped configurations | 11 (listed in the appendix) |

Tag and link issues:

- All 11 configurations are untyped. DeepSets, FFN, Emb-Cos, JESTR, SAIL and MSAlign are trained neural models: supervised_machine_learning (MSAlign may be foundation_model; check the MSAlign source).
- The six `msalign-2026-table3-method-*` configurations have no configuration_of link; link them to the existing model records.

### patient-rna-splicing-validation

Which DNA/RNA evidence workflow identifies splice-altering variants for inherited-disorder follow-up when patient RNA and tissue-specific context are available?

| | |
| --- | --- |
| Claim | `use-case-baseline-patient-rna-splicing-validation` |
| Baseline | FRASER and OUTRIDER, with a MaxEntScan-based splice-site vote |
| Method IDs | `rna-splicing-20261009-method-fraser` (FRASER), `rna-splicing-20261009-method-outrider` (OUTRIDER), `rna-splicing-20261011-fortier2026-method-legacy-ensemble` (Legacy Ensemble (N-of-4 vote, VarSeq)) |
| Rationale | On patient RNA, FRASER (splicing) and OUTRIDER (expression) are the established outlier tests, run in the DROP workflow; they fit count distributions after an unsupervised denoising step and are not trained on labelled variants. On DNA, the established clinical prediction is a vote across splice-site motif scorers led by MaxEntScan, which deep-learning predictors such as SpliceAI are compared with. |
| Sources | `amp-oncology-rna-20261007-source-pmc7822922` (Detection of aberrant splicing events in RNA-seq data using FRASER), `rna-splicing-20261011-fortier2026-source-article` (Analyzing the performance of deep learning splice prediction algorithms (Fortier, Rudy and) |
| Collection plan baselines | The conventional/author-introduced workflow measured in the linked primary source(s). |
| Baseline scored on | 9 active protocols |
| Same-data ML comparison | Yes, for DNA prediction only. The MaxEntScan-based Legacy Ensemble against SpliceAI, OpenSpliceAI and CI-SpliceAI on the four Fortier 2026 protocols. FRASER and OUTRIDER are never scored beside a learned method. Protocols: `rna-splicing-20261011-fortier2026-protocol-barbosa-deep-intronic`, `rna-splicing-20261011-fortier2026-protocol-ci-spliceai-benchmark`, `rna-splicing-20261011-fortier2026-protocol-riepe`, `rna-splicing-20261011-fortier2026-protocol-spip` |
| Proposed gap text | No machine-learning method has been compared with FRASER or OUTRIDER on the same patient RNA data in the linked evidence. |
| Decision notes | The use case asks about DNA and RNA evidence, so both references are named. FRASER and OUTRIDER use an autoencoder or PCA to remove confounders; that step is unsupervised, so conventional_pipeline is defensible, but a reviewer may disagree. |
| Untyped configurations | 0 (listed in the appendix) |

Tag and link issues:

- `rna-splicing-20261009-method-splice-predictor-consensus` (at least N of SpliceAI, Pangolin, SPiP and SQUIRLS) is tagged conventional_pipeline, but every input is a trained predictor; supervised_machine_learning fits.
- `amp-oncology-rna-20261007-issue-12-config-fraser-2021-article-implementation` has no configuration_of link to `rna-splicing-20261009-method-fraser`.

### phenotype-perturbation-selection

Which genetic perturbations should I test to produce a defined cellular response?

| | |
| --- | --- |
| Claim | `use-case-baseline-phenotype-perturbation-selection` |
| Baseline | Random selection |
| Method IDs | `tgtval-20261009-method-random-selection` (Random selection) |
| Rationale | There is no pre-machine-learning method for choosing perturbations to reach a defined cell state; the established comparator is random selection from the candidate set, a statistical control. No linked evidence for this use case measures it. |
| Sources | `tgtval-20261009-source-roohani2025` (BioDiscoveryAgent: An AI Agent for Designing Genetic Perturbation Experiments) |
| Collection plan baselines | Random candidate selection and mean-response/no-change controls; Linear or other simple statistical response models; Nearest measured perturbation |
| Baseline scored on | 0 active protocols |
| Same-data ML comparison | No. Random selection is not measured on either CPPC protocol. All 21 configurations are untyped CPPC submission rows with no method links. |
| Proposed gap text | No machine-learning method has been compared with random selection on the same data in the linked evidence. |
| Decision notes | No pre-ML method exists for this question. The claim names the simplest established control, which the linked evidence does not measure; a reviewer may prefer to hold the claim until a source measures it. |
| Untyped configurations | 21 (listed in the appendix) |

Tag and link issues:

- 21 untyped CPPC configurations. Named rows include scBERT and scVI (foundation_model or supervised_machine_learning), GeneVector, scETM, scTenifoldNet, GO-node2vec and Matrix_completion (learned), and GO_knn, PPI_Weighted and LowExp (simple rules). Unnamed rows need the CPPC write-up.

### plant-promoter-reporters

What evidence supports choosing a sequence model for predicting plant core-promoter strength in the intended reporter assay?

| | |
| --- | --- |
| Claim | `use-case-baseline-plant-promoter-reporters` |
| Baseline | GC and motif linear regression |
| Method IDs | `uc20260930-method-jores-gc-and-motif-linear-regression` (Jores GC and motif linear regression) |
| Rationale | Linear regression on GC content and known core-promoter motifs is the simple sequence model the plant STARR-seq study reports alongside its CNN. It is the simplest established comparator for predicting promoter strength. |
| Sources | `uc20260930-source-jores-2021` (Jores et al. 2021 plant core promoter models) |
| Collection plan baselines | (none) |
| Baseline scored on | 2 active protocols |
| Same-data ML comparison | No under current tags; yes once tagged. The GC and motif linear regression shares both Jores protocols (maize protoplasts, tobacco leaves) with the Jores CNN, which is untyped. |
| Proposed gap text | Do not add the gap sentence; tag the CNN instead. |
| Untyped configurations | 8 (listed in the appendix) |

Tag and link issues:

- 8 untyped configurations: the two Jores CNN configurations and the two AgroNT-figure CNN configurations should be supervised_machine_learning; the two AgroNT configurations foundation_model; the two linear-regression configurations conventional_pipeline.
- The four `agront-2024-fig3e-method-*` configurations have no configuration_of link.

### plasma-ctdna-fragmentomics

Which fragmentomics workflow detects tumour-derived plasma DNA under realistic low tumour fractions and fixed false-positive constraints?

| | |
| --- | --- |
| Claim | `use-case-baseline-plasma-ctdna-fragmentomics` |
| Baseline | ichorCNA |
| Method IDs | `ctdnafrag-20261009-method-ichorcna` (ichorCNA) |
| Rationale | ichorCNA estimates tumour fraction from genome-wide copy number in shallow plasma sequencing with a hidden Markov model and no training on cancer labels. It is the established non-learned reference that fragmentomic classifiers are compared with. |
| Sources | `ctdnafrag-20261009-source-wang2026` (A scalable deep-learning framework for cancer detection using cell-free DNA shallow whole-) |
| Collection plan baselines | The conventional/author-introduced workflow measured in the linked primary source(s). |
| Baseline scored on | 4 active protocols |
| Same-data ML comparison | Yes. ichorCNA against the UNITE XGBoost framework on the four Wang 2026 tumour-fraction strata. Protocols: `ctdnafrag-20261009-protocol-wang2026-unite-cv-tf-0-3pct`, `ctdnafrag-20261009-protocol-wang2026-unite-cv-tf-3-10pct`, `ctdnafrag-20261009-protocol-wang2026-unite-cv-tf-all`, `ctdnafrag-20261009-protocol-wang2026-unite-cv-tf-over-10pct` |
| Proposed gap text | None needed. |
| Decision notes | ichorCNA estimates tumour fraction rather than calling cancer, so it is a reference for the signal, not a matched detection classifier. Many single fragment features (FSR, WPS, end motifs) are tagged supervised_machine_learning because each feeds a classifier in Hou 2024; that seems right but a reviewer should confirm. |
| Untyped configurations | 0 (listed in the appendix) |

Tag and link issues:

- `amp-20261007-ctdna-fragmentomics-configuration` (DELFI 2019) has no configuration_of link to `ctdnafrag-20261009-method-delfi`.

### plasma-ctdna-methylation

Which measured methylation workflow detects tumour-derived plasma DNA and, where separately supported, identifies tissue of origin?

| | |
| --- | --- |
| Claim | `use-case-baseline-plasma-ctdna-methylation` |
| Baseline | MethAtlas and CelFiE deconvolution |
| Method IDs | `ctdnameth-20261009-method-methatlas` (MethAtlas (meth_atlas)), `ctdnameth-20261009-method-celfie` (CelFiE) |
| Rationale | Reference-based deconvolution, by non-negative least squares (MethAtlas) or expectation-maximisation (CelFiE), is the established way to estimate tissue contributions to plasma DNA without a trained classifier. Sun et al. 2024 compare both with newer methods on the same mixtures. |
| Sources | `ctdnameth-20261009-source-sun2024` (Systematic evaluation of methylation-based cell type deconvolution methods for plasma cell) |
| Collection plan baselines | The conventional/author-introduced workflow measured in the linked primary source(s). |
| Baseline scored on | 5 active protocols |
| Same-data ML comparison | No under current tags. MethAtlas and CelFiE are scored on Sun 2024 and Giuili 2025 (DecoNFlow) deconvolution protocols beside other deconvolution methods, all tagged specialist. The GRAIL, SPOT-MAS, Zeng and CpGPT classifiers are on other protocols. If CIBERSORT (support vector regression) is retagged supervised_machine_learning, the two Giuili 2025 tumour-fraction protocols (`ctdnameth-20261009-protocol-giuili2025-rrbs-tt-tumour-fraction-lod`, `-wgbs-tt-tumour-fraction-lod`) would compare it with MethAtlas and CelFiE. |
| Proposed gap text | No machine-learning method has been compared with MethAtlas and CelFiE deconvolution on the same data in the linked evidence. Add this only if CIBERSORT is not retagged; a CIBERSORT comparison is a weak test of machine learning, so the page should say what it is. |
| Decision notes | This covers tissue of origin. For cancer detection the linked evidence has no pre-ML method; every detection configuration is a trained classifier. |
| Untyped configurations | 1 (listed in the appendix) |

Tag and link issues:

- The deconvolution methods are tagged specialist, which does not separate fitted from learned. MethAtlas (non-negative least squares), CelFiE and CelFEER (expectation-maximisation), EpiDISH RPC, Houseman CP and UXM fit conventional_pipeline; CIBERSORT (support vector regression) fits supervised_machine_learning.
- `amp-config-cfmethyl-stacked-2022` (stacked ensemble) is untyped; supervised_machine_learning.

### protein-variant-stability

What evidence supports ranking protein substitutions by folding stability, and what must be validated before choosing a method?

| | |
| --- | --- |
| Claim | `use-case-baseline-protein-variant-stability` |
| Baseline | FoldX and Rosetta |
| Method IDs | `protein-stability-20261009-method-foldx` (FoldX), `protein-stability-20261009-method-rosetta` (Rosetta) |
| Rationale | FoldX and Rosetta compute stability changes from empirical and physics-based energy functions on a structure, and are the long-standing references in stability benchmarks. Their energy terms have a few weights fitted to measurements, but they are not models trained end to end on stability labels. |
| Sources | `protein-stability-20261009-source-pancotti2022` (Predicting protein stability changes upon single-point mutation: a thorough comparison of ) |
| Collection plan baselines | (none) |
| Baseline scored on | 12 active protocols |
| Same-data ML comparison | Yes. FoldX or Rosetta against supervised and language-model predictors on 12 protocols (Chu 2024, Dieckhaus 2024, Pancotti 2022). Protocols: `protein-stability-20261009-protocol-chu2024-acetyltransferase`, `protein-stability-20261009-protocol-chu2024-bgl3`, `protein-stability-20261009-protocol-chu2024-bglb`, `protein-stability-20261009-protocol-chu2024-lipase-esta`, `protein-stability-20261009-protocol-chu2024-mega-scale`, `protein-stability-20261009-protocol-chu2024-methyltransferase`, `protein-stability-20261009-protocol-chu2024-pten`, `protein-stability-20261009-protocol-dieckhaus2024-fireprot`, `protein-stability-20261009-protocol-dieckhaus2024-megascale`, `protein-stability-20261009-protocol-dieckhaus2024-s669`, `protein-stability-20261009-protocol-dieckhaus2024-ssym`, `protein-stability-20261009-protocol-pancotti2022-s669` |
| Proposed gap text | None needed. |
| Untyped configurations | 99 (listed in the appendix) |

Tag and link issues:

- 99 untyped configurations, 97 of them on `uc20260930-proteingym-amfr-protocol` (ProteinGym AMFR). Protein language and structure-conditioned models (ESM-1b, ESM-1v, ESM-2, ESMC, ESM3, ESM-IF1, ProGen2, ProGen3, RITA, ProtGPT2, Tranception, CARP, xTrimoPGLM, SaProt, ProSST, ProtSSN, PoET, MSA Transformer, MIF, MIF-ST, MULAN, Unirep, S2F, S3F, AIDO Protein-RAG, Protriever, VenusREM, ProteinMPNN) fit foundation_model; VESPA, VESPAl and VespaG are supervised on embeddings.
- EVmutation, GEMME, ESCOTT, RSALOR, SiteRM and the site-independent model are alignment statistics: conventional_pipeline. The seeded random control is conventional_pipeline.
- EVE, DeepSequence, Wavenet and TranceptEVE are per-family generative models trained without labels. None of the four vocabulary concepts fits them well; this may need a new concept (unsupervised generative model) rather than forcing one.

### rare-disease-candidate-ranking

Which methods recover causal variants and genes within a realistic laboratory review budget?

| | |
| --- | --- |
| Claim | `use-case-baseline-rare-disease-candidate-ranking` |
| Baseline | Exomiser and PhenIX |
| Method IDs | `uc-clinical-20260930-method-exomiser` (Exomiser), `rare-ranking-20261009-method-phenix` (PhenIX) |
| Rationale | Exomiser, with its PhenIX phenotype mode, is the established open prioritiser in diagnostic laboratories. It filters variants by frequency, inheritance and predicted effect and ranks genes by ontology similarity between patient and disease phenotypes, combined in a simple logistic score rather than a model trained end to end on diagnoses. |
| Sources | `rare-ranking-20261009-source-yuan2022` (Evaluation of phenotype-driven gene prioritization methods for Mendelian diseases), `rare-ranking-20261009-source-yuan2024` (Refined preferences of prioritizers improve intelligent diagnosis for Mendelian diseases) |
| Collection plan baselines | Conventional filtering and phenotype/pedigree-aware review with pinned versions; An appropriate pinned Exomiser configuration without the added model |
| Baseline scored on | 7 active protocols |
| Same-data ML comparison | Yes. Exomiser or PhenIX against AMELIE, DeepPVP, GADO, HANRD, Phenolyzer and Xrare (Yuan 2022, 2024) and against GPT-4 (Kafkas 2025). Protocols: `rare-ranking-20261009-protocol-kafkas2025-clinvar-gene-sets`, `rare-ranking-20261009-protocol-kafkas2025-pavs-gene-sets`, `rare-ranking-20261009-protocol-yuan2022-ddd-singleton-default`, `rare-ranking-20261009-protocol-yuan2022-kmcgd-singleton-default`, `rare-ranking-20261009-protocol-yuan2024-ddd-parameter-protocols`, `rare-ranking-20261009-protocol-yuan2024-kgd-parameter-protocols` |
| Proposed gap text | None needed. |
| Untyped configurations | 3 (listed in the appendix) |

Tag and link issues:

- `uc-clinical-20260930-exomiser-v14`, `uc-clinical-20260930-talos-default` and `uc-clinical-20260930-talos-strict` are untyped; other configurations of both methods are conventional_pipeline.
- On `amp-feng-20261007-protocol-pathogenic-common-variant-classification`, Enformer and Sei configurations (hidden states and output tracks) are tagged conventional_pipeline. Both are supervised deep models (`regulatory-variant-20261009-model-enformer` and `-model-sei` are supervised_machine_learning).

### regulatory-variant-gene-follow-up

Which variants, regulatory elements and genes should I perturb to explain a disease-associated locus?

| | |
| --- | --- |
| Claim | `use-case-baseline-regulatory-variant-gene-follow-up` |
| Baseline | Distance to TSS and Activity-by-Contact |
| Method IDs | `regulatory-variant-20261009-method-distance-to-tss` (Distance to TSS baseline), `ucc-research-method-mprabc-abc` (Activity-by-Contact (ABC)) |
| Rationale | Choosing the nearest gene and the Activity-by-Contact score (element activity times 3D contact) are the established non-learned rules for linking elements to genes. Learned linkers such as ENCODE-rE2G are judged by how much they improve on them. |
| Sources | `regulatory-variant-20261009-source-gschwind2026` (An encyclopedia of human enhancer-gene regulatory interactions), `ucc-research-source-mprabc` (MPRA-informed modeling improves context-specific enhancer-gene regulatory interactions) |
| Collection plan baselines | Distance-based variant/gene or enhancer/gene selection where applicable; ABC, ENCODE-rE2G or scE2G for compatible element-gene linking tasks; Sequence predictors compared only on the allele-effect outputs they produce |
| Baseline scored on | 2 active protocols |
| Same-data ML comparison | Yes. Distance to TSS and ABC against ENCODE-rE2G, EPIraction and EpiMap on `regulatory-variant-20261009-protocol-gschwind2026-heldout-weighted`. On `ucc-research-protocol-mprabc-k562`, ABC is beside ENCODE-rE2G and MPRabc, but all are untyped there. Protocols: `regulatory-variant-20261009-protocol-gschwind2026-heldout-weighted` |
| Proposed gap text | None needed. |
| Decision notes | This baseline covers element-gene linking. For allele-effect prediction, the conservation scores (phyloP, phastCons) and CADD are the established comparators; a reviewer may want them named too. |
| Untyped configurations | 6 (listed in the appendix) |

Tag and link issues:

- On the four QTL discrimination protocols, 20 Enformer, Sei and AlphaGenome configurations (hidden states and output tracks) are tagged conventional_pipeline; all three are supervised deep models.
- The six MPRabc K562 configurations are untyped: ABC conventional_pipeline; ENCODE-rE2G and the MPRabc variants supervised_machine_learning.
- `lit-genomics-20261011-dnalongbench-config-abc` (ABC in DNALongBench) is tagged supervised_machine_learning, but ABC is a fixed score of element activity times contact frequency; conventional_pipeline, unless DNALongBench fits a model on top of it (check the source).

### rhodopsin-wavelength-transfer

Which sequence-based configurations merit testing before selecting rhodopsins with different absorption wavelengths in a new wild-type background?

| | |
| --- | --- |
| Claim | `use-case-baseline-rhodopsin-wavelength-transfer` |
| Baseline | BLASSO rhodopsin predictor |
| Method IDs | `uc20260930-method-blasso-rhodopsin-predictor` (BLASSO rhodopsin predictor) |
| Rationale | Bayesian LASSO regression on amino-acid physicochemical features is the established sequence-based wavelength predictor that newer models are compared with. It is a sparse linear statistical model. |
| Sources | `uc20260930-source-rhomax-2024` (RhoMax 2024 primary article) |
| Collection plan baselines | (none) |
| Baseline scored on | 5 active protocols |
| Same-data ML comparison | No under current tags; yes once tagged. BLASSO shares all five RhoMax protocols with RhoMax and RhoMax + retinal, which are untyped. |
| Proposed gap text | Do not add the gap sentence; tag RhoMax instead. |
| Untyped configurations | 8 (listed in the appendix) |

Tag and link issues:

- 8 untyped configurations: RhoMax (two) supervised_machine_learning, pending a check of the RhoMax article; BLASSO conventional_pipeline (a sparse linear model; supervised_machine_learning is also defensible, which would make the baseline an ML row); the two ESM-2 ridge probes foundation_model; composition ridge and training mean conventional_pipeline.

### somatic-small-variant-oncogenicity

Which methods help classify somatic SNVs and small indels while preserving uncertainty and the relevant gene mechanism?

| | |
| --- | --- |
| Claim | `use-case-baseline-somatic-small-variant-oncogenicity` |
| Baseline | ClinGen/CGC/VICC rules (OncoVI) and SIFT |
| Method IDs | `uc-clinical-20260930-method-oncovi` (Oncogenicity Variant Interpreter (OncoVI)), `somatic-oncogenicity-20261009-method-sift` (SIFT) |
| Rationale | Somatic oncogenicity is classified by the ClinGen/CGC/VICC points-based standard, which OncoVI applies as fixed rules. For the computational evidence step, SIFT, which scores substitutions by conservation in homologous sequences, is the long-standing pre-machine-learning predictor. |
| Sources | `uc-clinical-20260930-source-oncovi` (Oncogenicity Variant Interpreter (OncoVI) Supports Harmonized Somatic Variant Interpretati), `somatic-oncogenicity-20261009-source-chen2020` (Comprehensive assessment of computational algorithms in predicting cancer driver mutations) |
| Collection plan baselines | ClinGen/CGC/VICC criteria-based review under a pinned specification; A relevant specialised predictor assessed only within its actual output scope |
| Baseline scored on | 11 active protocols |
| Same-data ML comparison | Yes, for SIFT only. SIFT against some 30 supervised predictors and ESM-1b on the Chen 2020 and Lee 2026 protocols. OncoVI is scored alone on its four protocols. Protocols: `somatic-oncogenicity-20261009-protocol-chen2020-oncokb-default`, `somatic-oncogenicity-20261009-protocol-chen2020-oncokb-median`, `somatic-oncogenicity-20261009-protocol-chen2020-viability-default`, `somatic-oncogenicity-20261009-protocol-chen2020-viability-median`, `somatic-oncogenicity-20261009-protocol-lee2026-all`, `somatic-oncogenicity-20261009-protocol-lee2026-oncogene`, `somatic-oncogenicity-20261009-protocol-lee2026-tsg` |
| Proposed gap text | No machine-learning method has been compared with the OncoVI criteria-based classification on the same data in the linked evidence. |
| Decision notes | OncoVI is a 2026 implementation of the ClinGen/CGC/VICC standard. The standard itself, applied by experts, is the reference; OncoVI stands for it because it has a record. |
| Untyped configurations | 2 (listed in the appendix) |

Tag and link issues:

- `uc-clinical-20260930-oncovi-study` and `uc-clinical-20260930-oncovi-prior-mtb` are untyped; conventional_pipeline.
- SIFT, PROVEAN, MutationAssessor, LRT, GERP, phyloP, phastCons, GenoCanyon, Integrated_fitCons, bStatistic, LIST-S2, CTAT and TransFIC are tagged specialist; they are not trained classifiers, so conventional_pipeline would be clearer.
- popEVE (a deep generative model combined with ESM-1v) and MisFit (a trained deep model) are tagged specialist; they should be foundation_model or supervised_machine_learning.

### splicing-follow-up

Which evaluated configurations can inform selection of human SNVs for follow-up splicing experiments?

| | |
| --- | --- |
| Claim | `use-case-baseline-splicing-follow-up` |
| Baseline | MaxEntScan |
| Method IDs | `splicing-follow-up-20261009-method-maxentscan` (MaxEntScan) |
| Rationale | MaxEntScan scores splice-site strength with a maximum-entropy model of the donor and acceptor motifs, and is the long-standing reference in diagnostic splice prediction. Splicing assay benchmarks compare deep-learning predictors against it. |
| Sources | `splicing-follow-up-20261009-source-riepe2021` (Benchmarking deep learning splice prediction tools using functional splice assays), `splicing-follow-up-20261009-source-smith2023` (Benchmarking splice variant prediction algorithms using massively parallel splicing assays) |
| Collection plan baselines | (none) |
| Baseline scored on | 3 active protocols |
| Same-data ML comparison | Yes. MaxEntScan against SpliceAI, MMSplice, SPANR, SpliceRover, NNSPLICE, GeneSplicer, DSSP and CADD on the three Riepe 2021 protocols. Smith and Kitzman 2023 (MFASS) does not score MaxEntScan. Protocols: `splicing-follow-up-20261009-protocol-riepe2021-abca4-di`, `splicing-follow-up-20261009-protocol-riepe2021-abca4-ncss`, `splicing-follow-up-20261009-protocol-riepe2021-mybpc3-ncss` |
| Proposed gap text | None needed. |
| Untyped configurations | 6 (listed in the appendix) |

Tag and link issues:

- `discovery-model-spliceai` and `catalog-model-spliceai` (and the two Pangolin records) look like duplicate model records; MFASS-matched SpliceAI configurations under the discovery record are untyped or specialist, those under the catalogue record supervised_machine_learning.
- The corrected k-mer/position baseline and the training class prior configurations are untyped; conventional_pipeline.

### structural-hypotheses-experiments

Which predicted interfaces or structures are reliable enough to guide my next experiment?

| | |
| --- | --- |
| Claim | `use-case-baseline-structural-hypotheses-experiments` |
| Baseline | AutoDock Vina and ClusPro docking |
| Method IDs | `catalog-model-vina` (AutoDock Vina), `ucc-docking-cluspro-bm5-2020-method` (ClusPro rigid-body docking) |
| Rationale | Physics-based docking is the established way to model complexes before co-folding: AutoDock Vina for ligands and ClusPro rigid-body docking for protein-protein pairs. Both search poses and rank them with scoring functions rather than learned structure models. |
| Sources | `evidence-expansion-p2-lipp-2026-6ff34f2f709a` (The LiPP Benchmark Set for Modeling Lipid-Protein Complexes: Comparison of Co-Folding and ), `ucc-docking-cluspro-bm5-2020-source` (Performance and its limits in rigid body protein-protein docking) |
| Collection plan baselines | Suitable template modelling or docking for the specified complex class; Conventional mutation or construct selection for experimental-utility comparisons |
| Baseline scored on | 6 active protocols |
| Same-data ML comparison | Yes, for ligands only. AutoDock Vina against AlphaFold 3, Chai-1 and RoseTTAFold All-Atom on the two LiPP protocols. ClusPro is scored alone on its four BM5 protocols. Protocols: `lit-structure-20261011-lipp-protocol-pb-valid-lipp-test-36`, `lit-structure-20261011-lipp-protocol-rmsd-lipp-test-36` |
| Proposed gap text | No machine-learning method has been compared with ClusPro docking on the same protein-protein data in the linked evidence. |
| Decision notes | The collection plan also names template modelling, which has no method record. |
| Untyped configurations | 7 (listed in the appendix) |

Tag and link issues:

- `catalog-model-diffdock-l` (DiffDock-L) is tagged specialist but is a trained diffusion model; supervised_machine_learning. It shares the LiPP protocols with Vina.
- The two ClusPro configurations are untyped (conventional_pipeline). The five FoldBench configurations are untyped; AlphaFold 3, Boltz-1 and Chai-1 are foundation_model elsewhere, and HelixFold 3 and Protenix are the same class.

### therapeutic-target-validation

Which targets should I test to change a defined disease-relevant phenotype?

| | |
| --- | --- |
| Claim | `use-case-baseline-therapeutic-target-validation` |
| Baseline | Random and pathway-based selection |
| Method IDs | `tgtval-20261009-method-random-selection` (Random selection), `tgtval-20261009-method-human-pathway-selection` (Human pathway-based selection) |
| Rationale | There is no pre-machine-learning method for choosing which targets to perturb; the established comparators are random selection and genes chosen from relevant pathways. Agent and Bayesian optimisation methods are judged by how many more hits they find than these. |
| Sources | `tgtval-20261009-source-roohani2025` (BioDiscoveryAgent: An AI Agent for Designing Genetic Perturbation Experiments), `tgtval-20261009-source-gupta2025` (LLMs for Bayesian Optimization in Scientific Domains: Are We There Yet?) |
| Collection plan baselines | Genetics-only and expression-only rankings; Simple dependency ranking or conventional evidence aggregation |
| Baseline scored on | 1 active protocols |
| Same-data ML comparison | Yes. Random and pathway-based selection against BioDiscoveryAgent, LLMs and Bayesian optimisation acquisition functions on `tgtval-20261009-protocol-roohani2025-hitratio-round5`. Protocols: `tgtval-20261009-protocol-roohani2025-hitratio-round5` |
| Proposed gap text | None needed. |
| Decision notes | The collection plan names genetics-only and expression-only rankings and dependency ranking; none of these is measured or has a record. |
| Untyped configurations | 21 (listed in the appendix) |

Tag and link issues:

- 21 untyped CPPC configurations (as in phenotype-perturbation-selection).
- `tgtval-20261009-method-embedding-knn` and `-oracle-knn` are tagged conventional_pipeline; kNN on learned embeddings is closer to supervised_machine_learning. Check the source.

### tumour-dna-somatic-variant-detection

Which calling or rescoring workflow reliably detects tumour SNVs and small indels under the available sequencing and normal-sample regime?

| | |
| --- | --- |
| Claim | `use-case-baseline-tumour-dna-somatic-variant-detection` |
| Baseline | Mutect2 and Strelka2 |
| Method IDs | `somatic-20261009-method-mutect2` (Mutect2), `somatic-20261009-method-strelka` (Strelka) |
| Rationale | Mutect2 and Strelka2 are the most widely used tumour-normal callers and the reference in somatic benchmarks. Both call variants with statistical models of read evidence, not learned classifiers. |
| Sources | `somatic-20261009-source-wang2020` (SomaticCombiner: improving the performance of somatic variant calling based on evaluation ), `somatic-20261009-source-guille2025` (A benchmarking study of individual somatic variant callers and voting-based ensembles for ) |
| Collection plan baselines | The conventional/author-introduced workflow measured in the linked primary source(s). |
| Baseline scored on | 34 active protocols |
| Same-data ML comparison | Yes. Mutect2 or Strelka2 against NeuSomatic, DeepSomatic, ClairS-TO, VarNet, VarNet-T and DeepSom on 31 protocols. Protocols: `somatic-20261009-protocol-guille2025-seqc2-fd-wes-indel`, `somatic-20261009-protocol-guille2025-seqc2-fd-wes-snv`, `somatic-20261009-protocol-wang2020-aml-snv`, `somatic-20261009-protocol-wang2020-cll-indel`, `somatic-20261009-protocol-wang2020-cll-snv`, `somatic-20261009-protocol-wang2020-colo829-indel`, `somatic-20261009-protocol-wang2020-colo829-snv`, `somatic-20261009-protocol-wang2020-dream-set1-snv`, `somatic-20261009-protocol-wang2020-dream-set2-snv`, `somatic-20261009-protocol-wang2020-dream-set4-indel`, `somatic-20261009-protocol-wang2020-dream-set4-snv`, `somatic-20261009-protocol-wang2020-mb-indel`, `somatic-20261009-protocol-wang2020-mb-snv`, `somatic-clairs-to-20261011-protocol-illumina-colo829-indel`, `somatic-clairs-to-20261011-protocol-illumina-colo829-snv`, `somatic-hg008-20261011-protocol-all-region-overall`, `somatic-hg008-20261011-protocol-primary-indel`, `somatic-hg008-20261011-protocol-primary-overall`, `somatic-hg008-20261011-protocol-primary-snv`, `somatic-neusomatic-20261010-protocol-sahraeian2022-library-prep-indel`, `somatic-neusomatic-20261010-protocol-sahraeian2022-library-prep-snv`, `somatic-neusomatic-20261010-protocol-sahraeian2022-titration-indel`, `somatic-neusomatic-20261010-protocol-sahraeian2022-titration-snv`, `somatic-neusomatic-20261010-protocol-sahraeian2022-wgs-indel`, `somatic-neusomatic-20261010-protocol-sahraeian2022-wgs-snv`, `somatic-varnet-t-20261011-protocol-colo829-indel`, `somatic-varnet-t-20261011-protocol-colo829-snv`, `somatic-varnet-t-20261011-protocol-low-tmb-snv`, `somatic-varnet-t-20261011-protocol-pcawg-snv`, `somatic-varnet-t-20261011-protocol-seqc2-indel`, `somatic-varnet-t-20261011-protocol-seqc2-snv` |
| Proposed gap text | None needed. |
| Untyped configurations | 0 (listed in the appendix) |

Tag and link issues:

- `amp-oncology-rna-20261007-issue-10-config-strelka2` and `-config-lancet` have no configuration_of link, so the Strelka2 row on the Lancet virtual-tumour protocol will not be marked as a baseline.
- The NeuSomatic ensemble configurations (for example `somatic-neusomatic-20261010-config-sahraeian2022-neusomatic-dream3`) carry uses_model links to Mutect2 and Strelka. If the website marks baseline rows by any link rather than configuration_of only, these ML rows would be marked as baselines. The figures above use configuration_of only.

### tumour-rna-fusion-detection

Which RNA-sequencing workflow detects and prioritises tumour gene fusions with useful sensitivity and a manageable false-positive review burden?

| | |
| --- | --- |
| Claim | `use-case-baseline-tumour-rna-fusion-detection` |
| Baseline | STAR-Fusion and Arriba |
| Method IDs | `rna-fusion-20261009-method-star-fusion` (STAR-Fusion), `rna-fusion-20261009-method-arriba` (Arriba) |
| Rationale | STAR-Fusion and Arriba are the most widely used short-read fusion callers and the reference in comparisons. Both detect chimeric reads from STAR alignment and remove artefacts with rule-based filters. |
| Sources | `rna-fusion-20261009-source-tamura2026` (Comparison of gene fusion detection algorithms reveals frequently overlooked driver fusion) |
| Collection plan baselines | The conventional/author-introduced workflow measured in the linked primary source(s). |
| Baseline scored on | 5 active protocols |
| Same-data ML comparison | No under current tags. STAR-Fusion and Arriba are scored on five protocols; every fusion caller is tagged conventional_pipeline. If EricScript is retagged, the four Tamura 2026 protocols would compare it with STAR-Fusion and Arriba. |
| Proposed gap text | No machine-learning method has been compared with STAR-Fusion and Arriba on the same data in the linked evidence. Add this only if EricScript stays conventional; if it is retagged, the comparison is a classifier-filtered caller, not a learned caller, and the page should say so. |
| Untyped configurations | 0 (listed in the appendix) |

Tag and link issues:

- EricScript (`rna-fusion-20261009-method-ericscript` and `rna-fusion-20261009-config-tamura2026-ericscript`) is tagged conventional_pipeline. Issue #121 says it scores candidates with an AdaBoost classifier (Tamura Supplementary Tables 3 and 5). I have not re-read the source to confirm.
- deFuse has no method record, so its tag cannot be corrected here.
- The STAR-Fusion and Arriba configurations on the two EnFusion protocols (`amp-oncology-rna-20261007-nch-config-*`, `amp-oncology-rna-20261007-issue-11-config-*`) have no configuration_of link, so they will not be marked as baseline rows.

### unresolved-rare-disease-reanalysis

Which reanalysis methods find new diagnoses or reduce review effort when given the same updated information?

| | |
| --- | --- |
| Claim | `use-case-baseline-unresolved-rare-disease-reanalysis` |
| Baseline | Manual expert reanalysis and Exomiser |
| Method IDs | `reanalysis-kaschta-20261010-method-manual-diagnostic-reanalysis` (Manual diagnostic reanalysis by laboratory experts), `uc-clinical-20260930-method-exomiser` (Exomiser) |
| Rationale | Reanalysis is judged against laboratory experts repeating the review with updated information, a manual workflow rather than an algorithm. Exomiser rerun on updated annotations is the established automated comparator. |
| Sources | `reanalysis-kaschta-20261010-source-kaschta2026` (Automated versus manual reanalysis in rare disease genomics), `rare-reanalysis-20261009-source-vestito2024` (Efficient reinterpretation of rare disease cases using Exomiser) |
| Collection plan baselines | Refreshed conventional analysis with the same updated information; The original unresolved cohort for programme-level incremental yield, reported separately |
| Baseline scored on | 3 active protocols |
| Same-data ML comparison | No. Manual reanalysis is scored against Talos (Kaschta 2026) and Exomiser on its own; Talos is rule-based and tagged conventional_pipeline. No learned method is in the use case. |
| Proposed gap text | No machine-learning method has been compared with manual expert reanalysis or Exomiser on the same data in the linked evidence. |
| Decision notes | The comparator is a manual workflow. Talos is an automated rule-based method and could be named instead of or beside Exomiser; I kept Exomiser because it is the longer-established tool and the collection plan names refreshed conventional analysis. |
| Untyped configurations | 4 (listed in the appendix) |

Tag and link issues:

- Four untyped configurations (`uc-clinical-20260930-talos-monthly`, `-talos-default`, `-talos-strict`, `-exomiser-v14`); other configurations of both methods are conventional_pipeline.

### utr-translation-baselines

Before training a more complex model of reporter translation, which sequence-only controls should be measured on the same held-out data?

| | |
| --- | --- |
| Claim | `use-case-baseline-utr-translation-baselines` |
| Baseline | k-mer random forest |
| Method IDs | `uc20260930-method-k-mer-count-random-forest` (k-mer count random forest), `uc20260930-method-frame-aware-k-mer-random-forest` (Frame-aware k-mer random forest) |
| Rationale | There is no pre-machine-learning predictor of reporter translation; the simplest established comparators are the training mean and composition models, which have no method records, and random forests on k-mer counts. The FramePool study reports the k-mer forests as its non-deep baselines. |
| Sources | `uc20260930-source-framepool-2021` (FramePool 2021 primary article) |
| Collection plan baselines | (none) |
| Baseline scored on | 2 active protocols |
| Same-data ML comparison | No under current tags; yes once tagged. The k-mer random forests share both FramePool protocols with FramePool and Optimus 5-Prime, which are untyped. |
| Proposed gap text | Do not add the gap sentence; tag the configurations instead. |
| Decision notes | The use case asks which sequence-only controls to measure. The training mean and composition ridge controls are the true simplest comparators but have no method records (their configurations are unlinked). A random forest is a supervised learner, so once tagged the baseline rows will also be ML rows. |
| Untyped configurations | 12 (listed in the appendix) |

Tag and link issues:

- 12 untyped configurations: FramePool and Optimus 5-Prime (five) supervised_machine_learning (convolutional networks); the five k-mer random forests supervised_machine_learning; training-mean and composition ridge conventional_pipeline.

## Cross-cutting findings

### Methods without records

These are the right baseline, or part of it, but have no method or model record, so no claim can name them:

- Manual ClinGen ENIGMA criteria-based review (BRCA1/BRCA2). Its configuration `uc-clinical-20260930-enigma-v10-manual` has no method link.
- SURPI+ and CZ ID nucleotide alignment to NCBI nt (RNA pathogens). The UCSF SURPI+ configuration is unlinked.
- BM25 as a method (EGFR); the claim uses the ASCFDA TREC team record instead.
- Manual marker-based annotation, Azimuth (cell types).
- Spectral library search, MetFrag, a random-candidate control (mass spectra).
- Template-based structure modelling (structural hypotheses).
- Training-mean and composition-ridge controls as methods (UTR, rhodopsin, splicing follow-up): only unlinked configurations exist.
- deFuse (fusion): no record, so its tag cannot be corrected.
- Genetics-only, expression-only and dependency rankings (target validation).

### New sources that would help

No source records were added. These would strengthen claims or close gaps:

- Haas et al. 2019, Genome Biology, doi:10.1186/s13059-019-1842-9 (23 fusion callers including STAR-Fusion, Arriba, EricScript and deFuse): the benchmark that establishes STAR-Fusion and Arriba as the reference.
- Feng 2017 (BayesDel) and Parsons et al. 2024 (ENIGMA VCEP specification paper), to support the BRCA rationale beyond the stored ENIGMA source.
- MetageNN (doi:10.1186/s12859-024-05760-3) and BERTax (doi:10.1073/pnas.2122636119), the same-data ML comparisons for DNA pathogens named in issue #121.
- Adalsteinsson et al. 2017 (ichorCNA) and Moss et al. 2018 (MethAtlas), if the reviewer wants the rationale to cite the method papers rather than the benchmarks that measure them.

### How the website should match baseline rows

NeuSomatic ensemble configurations have `uses_model` links to Mutect2 and Strelka, because they take those callers' output as input. If baseline rows are matched on every link, these ML rows would be marked as baselines. Match on `configuration_of` only. Several baseline configurations have no `configuration_of` link at all (Strelka2 and Lancet on the Lancet virtual-tumour protocol, STAR-Fusion and Arriba on the EnFusion protocols, the O'Connell CPU configurations, the MSAlign Table 3 DeepSets rows, the FRASER 2021 configuration), so they will not be marked until linked.

### Baselines that are machine learning under the vocabulary

For BRCA1/BRCA2 (BayesDel), cell types (linear SVM, logistic regression), mass spectra (DeepSets) and UTR translation (k-mer random forests), the named baseline is itself a trained model under the `supervised_machine_learning` definition, because no pre-ML method is measured. Once tagged, the website will show baseline rows that are also ML rows. A reviewer should decide whether that is acceptable or whether these use cases should state that no pre-ML baseline exists.

### Vocabulary

`specialist` says a method is task-specific but not whether it is learned, so the website cannot tell a conservation score from a trained classifier. Many baseline-candidate methods carry only `specialist` (SIFT, GERP, phyloP, MethAtlas, CelFiE, UXM, Align-GVGD). Per-family generative models (EVE, DeepSequence, TranceptEVE) fit none of the four concepts. Both may need a vocabulary change rather than per-record retagging.

## Appendix: untyped configurations in each use case's comparisons

Configurations on the use case's mappings (active, draft or withheld) with no `facets.method_types`. "Suggested" is filled only where other configurations of the same method or model are tagged; the per-use-case notes above give suggestions for the rest.

### brca1-brca2-germline-interpretation (8)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc-clinical-20260930-bayesdel-enigma` | BayesDel with ENIGMA BRCA gene-specific score categories | `uc-clinical-20260930-method-bayesdel` | `uc-clinical-20260930-enigma-brca1-protocol` | supervised_machine_learning | 7 other configuration(s) of uc-clinical-20260930-method-bayesdel are tagged supervised_machine_learning |
| `uc-clinical-20260930-bayesdel-pejaver-generic` | BayesDel generic Pejaver evidence thresholds in ENIGMA comparison | `uc-clinical-20260930-method-bayesdel` | `uc-clinical-20260930-enigma-brca2-generic-protocol` | supervised_machine_learning | 7 other configuration(s) of uc-clinical-20260930-method-bayesdel are tagged supervised_machine_learning |
| `uc-clinical-20260930-enigma-v10-manual` | ClinGen ENIGMA v1.0 manual criteria-based curation | none | `uc-clinical-20260930-enigma-pilot-protocol` |  |  |
| `uc-clinical-20261005-so-2024-varsome-canvig-config` | VarSome vs. CanVIG-UK three-category concordance comparison | none | `uc-clinical-20261005-so-2024-protocol` |  |  |
| `uc-clinical-20261005-hu-2026-integrated-varcall-config` | Integrated VarCall model (combined SGE functional data) | none | `uc-clinical-20261005-hu-2026-protocol` |  |  |
| `uc-clinical-20261005-benet-pages-acmg-svi-config` | ACMG/AMP classification system with SVI recommendations (t2) | none | `uc-clinical-20261005-benet-pages-t2-protocol` |  |  |
| `uc-clinical-20261005-hector-v1-2-config` | HECTOR automated classifier (ENIGMA V1.2 specification) | none | `uc-clinical-20261005-hector-erepo-protocol` |  |  |
| `uc-clinical-20261005-benet-pages-enigma-vcep-config` | ENIGMA BRCA1/BRCA2 VCEP specification v1.1.0 (t3) | none | `uc-clinical-20261005-benet-pages-t3-protocol` |  |  |

### cell-type-annotation-transfer (13)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `ucc-research-config-sctab-celltypist` | CellTypist - scTab Table 1 | `scfoundation-2024-supp-table4-method-celltypist` | `ucc-research-protocol-sctab-seed` |  |  |
| `ucc-research-config-sctab-ciform` | CIForm - scTab Table 1 | `ucc-research-method-ciform` | `ucc-research-protocol-sctab-seed` |  |  |
| `ucc-research-config-sctab-linear` | Optimized linear logistic regression - scTab Table 1 | `ucc-research-method-linear` | `ucc-research-protocol-sctab-seed` |  |  |
| `ucc-research-config-sctab-mlp` | MLP - scTab Table 1 | `ucc-research-method-mlp` | `ucc-research-protocol-sctab-seed` |  |  |
| `ucc-research-config-sctab-scgpt-ft` | scGPT fine-tuned - scTab Table 1 | `catalog-model-scgpt` | `ucc-research-protocol-sctab-seed` | foundation_model | 8 other configuration(s) of catalog-model-scgpt are tagged foundation_model |
| `ucc-research-config-sctab-scgpt-zero` | scGPT frozen embeddings + logistic regression - scTab Table 1 | `catalog-model-scgpt` | `ucc-research-protocol-sctab-seed` | foundation_model | 8 other configuration(s) of catalog-model-scgpt are tagged foundation_model |
| `ucc-research-config-sctab-sctab` | scTab - scTab Table 1 | `ucc-research-method-sctab` | `ucc-research-protocol-sctab-seed` |  |  |
| `ucc-research-config-sctab-uce` | UCE frozen embeddings + classifier - scTab Table 1 | `ucc-research-method-uce` | `ucc-research-protocol-sctab-seed` |  |  |
| `ucc-research-config-sctab-xgboost` | XGBoost - scTab Table 1 | `ucc-research-method-xgboost` | `ucc-research-protocol-sctab-seed` |  |  |
| `ucc-research-config-abdelaal-scmapcell` | scmapcell - Abdelaal et al. 2019 Table 1 | `ucc-research-method-abdelaal-scmapcell` | `ucc-research-protocol-abdelaal-baron-human-intra` |  |  |
| `ucc-research-config-abdelaal-scpred` | scPred - Abdelaal et al. 2019 Table 1 | `ucc-research-method-abdelaal-scpred` | `ucc-research-protocol-abdelaal-baron-human-intra` |  |  |
| `ucc-research-config-abdelaal-svm-no-rejection` | SVM (no rejection) - Abdelaal et al. 2019 Table 1 | `ucc-research-method-abdelaal-svm-linear` | `ucc-research-protocol-abdelaal-baron-human-intra` |  |  |
| `ucc-research-config-abdelaal-svm-rejection` | SVMrejection - Abdelaal et al. 2019 Table 1 | `ucc-research-method-abdelaal-svm-linear` | `ucc-research-protocol-abdelaal-baron-human-intra` |  |  |

### cnv-detection-characterisation (1)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `amp-config-dragen42-cnv-sv` | DRAGEN 4.2 CNV+SV configuration | none | `amp-protocol-hg002-cnv-1-5kb` |  |  |

### diagnostic-genomics-model-execution (1)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `amp-config-dragen42-phase4-runtime` | DRAGEN 4.2 on Phase4 SKY-6200 | none | `amp-protocol-dragen-hg002-phase4-total-runtime` |  |  |

### egfr-nsclc-actionability-resistance-evidence (5)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc-clinical-20260930-civic-agent-mode` | ChatGPT Agent Mode, 2-7 March 2026 CIViC evaluation | `uc-clinical-20260930-pipeline-civic-retrieval` | `uc-clinical-20260930-civic-retrieval-protocol` |  |  |
| `uc-clinical-20260930-civic-gpt5-alone` | GPT-5 2025-08-07 alone, CIViC March 2026 | `uc-clinical-20260930-pipeline-civic-retrieval` | `uc-clinical-20260930-civic-retrieval-protocol` |  |  |
| `uc-clinical-20260930-civic-gpt5-mcp` | GPT-5 2025-08-07 with CIViC MCP, March 2026 | `uc-clinical-20260930-pipeline-civic-retrieval` | `uc-clinical-20260930-civic-retrieval-protocol` |  |  |
| `ucc-clinical-egfr-config-medcpt-ft` | Fine-tuned MedCPT cross-encoder (passage retrieval) | none | `ucc-clinical-egfr-protocol-civicfact-v3-retrieval` |  |  |
| `ucc-clinical-egfr-config-qwen3-reranker-8b` | Qwen3-Reranker-8B (pretrained, not fine-tuned) | none | `ucc-clinical-egfr-protocol-civicfact-v3-retrieval` |  |  |

### genetic-perturbation-response (16)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `gears-2023-supp-table6-method-cpa` | CPA | none | `gears-2023-supp-table6-task-mse` |  |  |
| `gears-2023-supp-table6-method-cpa-plus-kg` | CPA + KG | none | `gears-2023-supp-table6-task-mse` |  |  |
| `gears-2023-supp-table6-method-gears` | GEARS | none | `gears-2023-supp-table6-task-mse` |  |  |
| `gears-2023-supp-table6-method-no-perturb` | No Perturb | none | `gears-2023-supp-table6-task-mse` |  |  |
| `perteval-scfm-2025-method-gears` | GEARS (trained from scratch, no pretrained weights) | none | `perteval-scfm-2025-protocol-norman-single-2000hvg-auspc` |  |  |
| `perteval-scfm-2025-method-mean-baseline` | Mean baseline (context mean, no perturbation-specific effect) | none | `perteval-scfm-2025-protocol-norman-single-2000hvg-auspc` |  |  |
| `perteval-scfm-2025-method-mlp-baseline` | MLP baseline (raw control expression + gene co-expression input, Eq. 3) | none | `perteval-scfm-2025-protocol-norman-single-2000hvg-auspc` |  |  |
| `perturbench-method-biolord` | Biolord* | none | `lit-cells-networks-20261011-perturbench-v4-protocol-frangieh21` |  |  |
| `perturbench-method-cpa` | CPA* | none | `lit-cells-networks-20261011-perturbench-v4-protocol-frangieh21` |  |  |
| `perturbench-method-cpa-noadv` | CPA* (noAdv) | none | `lit-cells-networks-20261011-perturbench-v4-protocol-frangieh21` |  |  |
| `perturbench-method-cpa-scgpt` | CPA* (scGPT) | none | `lit-cells-networks-20261011-perturbench-v4-protocol-frangieh21` |  |  |
| `perturbench-method-decoder` | Decoder | none | `lit-cells-networks-20261011-perturbench-v4-protocol-frangieh21` |  |  |
| `perturbench-method-la` | LA | none | `lit-cells-networks-20261011-perturbench-v4-protocol-frangieh21` |  |  |
| `perturbench-method-la-scgpt` | LA (scGPT) | none | `lit-cells-networks-20261011-perturbench-v4-protocol-frangieh21` |  |  |
| `perturbench-method-linear` | Linear | none | `lit-cells-networks-20261011-perturbench-v4-protocol-frangieh21` |  |  |
| `perturbench-method-sams-vae` | SAMS-VAE* | none | `lit-cells-networks-20261011-perturbench-v4-protocol-frangieh21` |  |  |

### mass-spectrum-molecule-shortlisting (11)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc20260930-msalign-v2-config-deepset` | DeepSet [MSAlign v2] | `uc20260930-model-massspecgym-deepsets-fingerprint-predictor` | `uc20260930-msalign-v2-protocol-massspecgym-mces-formula-free` |  |  |
| `uc20260930-msalign-v2-config-emb-cos` | Emb-Cos [MSAlign v2] | `uc20260930-model-emb-cos` | `uc20260930-msalign-v2-protocol-massspecgym-mces-formula-free` |  |  |
| `uc20260930-msalign-v2-config-jestr` | JESTR [MSAlign v2] | `uc20260930-model-jestr` | `uc20260930-msalign-v2-protocol-massspecgym-mces-formula-free` |  |  |
| `uc20260930-msalign-v2-config-msalign` | MSAlign [MSAlign v2] | `discovery-model-msalign` | `uc20260930-msalign-v2-protocol-massspecgym-mces-formula-free` |  |  |
| `uc20260930-msalign-v2-config-msalign-score-fusion-overbar` | MSAlign score fusion (overbar) [MSAlign v2] | `discovery-model-msalign` | `uc20260930-msalign-v2-protocol-massspecgym-mces-formula-free` |  |  |
| `msalign-2026-table3-method-deepsets` | DeepSets | none | `msalign-2026-table3-task-massspecgym-formula-split-no-formula-r-1` |  |  |
| `msalign-2026-table3-method-emb-cos` | Emb-Cos | none | `msalign-2026-table3-task-massspecgym-formula-split-no-formula-r-1` |  |  |
| `msalign-2026-table3-method-ffn` | FFN | none | `msalign-2026-table3-task-massspecgym-formula-split-no-formula-r-1` |  |  |
| `msalign-2026-table3-method-jestr` | JESTR | none | `msalign-2026-table3-task-massspecgym-formula-split-no-formula-r-1` |  |  |
| `msalign-2026-table3-method-msalign` | MSAlign | none | `msalign-2026-table3-task-massspecgym-formula-split-no-formula-r-1` |  |  |
| `msalign-2026-table3-method-sail` | SAIL | none | `msalign-2026-table3-task-massspecgym-formula-split-no-formula-r-1` |  |  |

### phenotype-perturbation-selection (21)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `ucc-research-config-cppc-submission-row-11` | CPPC original submission row 11 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-12` | CPPC original submission row 12 (5Features) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-13` | CPPC original submission row 13 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-14` | CPPC original submission row 14 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-15` | CPPC original submission row 15 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-16` | CPPC original submission row 16 (scETM) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-17` | CPPC original submission row 17 (scTenifoldNet) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-18` | CPPC original submission row 18 (GO_knn) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-19` | CPPC original submission row 19 (LowExp) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-2` | CPPC original submission row 2 (PPI_Weighted) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-20` | CPPC original submission row 20 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-21` | CPPC original submission row 21 (interv) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-22` | CPPC original submission row 22 (GO-node2vec) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-23` | CPPC original submission row 23 (Matrix_completion) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-24` | CPPC original submission row 24 (GeneVector) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-3` | CPPC original submission row 3 (GWPS_K562 (H2M)) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-4` | CPPC original submission row 4 (14Features) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-5` | CPPC original submission row 5 (scBERT) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-6` | CPPC original submission row 6 (scVI) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-7` | CPPC original submission row 7 (Expression_Conditioned) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-pooled-nominations` | CPPC submitted-method nomination campaign | none | `ucc-research-protocol-cppc-prospective-selection` |  |  |

### plant-promoter-reporters (8)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc20260930-jores-config-maize-protoplasts-cnn` | Jores maize-protoplasts cnn | `uc20260930-model-jores-plant-promoter-cnn` | `uc20260930-jores-protocol-maize-protoplasts` |  |  |
| `uc20260930-jores-config-maize-protoplasts-gc-motif-linear` | Jores maize-protoplasts gc-motif-linear | `uc20260930-method-jores-gc-and-motif-linear-regression` | `uc20260930-jores-protocol-maize-protoplasts` |  |  |
| `uc20260930-jores-config-tobacco-leaves-cnn` | Jores tobacco-leaves cnn | `uc20260930-model-jores-plant-promoter-cnn` | `uc20260930-jores-protocol-tobacco-leaves` |  |  |
| `uc20260930-jores-config-tobacco-leaves-gc-motif-linear` | Jores tobacco-leaves gc-motif-linear | `uc20260930-method-jores-gc-and-motif-linear-regression` | `uc20260930-jores-protocol-tobacco-leaves` |  |  |
| `agront-2024-fig3e-method-agront-promoter-strength-maize-protoplasts` | AgroNT: promoter strength, maize protoplasts | none | `agront-2024-fig3e-task-maize-protoplasts-a-thaliana` |  |  |
| `agront-2024-fig3e-method-cnn-jores-et-al-promoter-strength-maize-protoplasts` | CNN (Jores et al.): promoter strength, maize protoplasts | none | `agront-2024-fig3e-task-maize-protoplasts-a-thaliana` |  |  |
| `agront-2024-fig3e-method-agront-promoter-strength-tobacco-leaves` | AgroNT: promoter strength, tobacco leaves | none | `agront-2024-fig3e-task-tobacco-leaves-a-thaliana` |  |  |
| `agront-2024-fig3e-method-cnn-jores-et-al-promoter-strength-tobacco-leaves` | CNN (Jores et al.): promoter strength, tobacco leaves | none | `agront-2024-fig3e-task-tobacco-leaves-a-thaliana` |  |  |

### plasma-ctdna-methylation (1)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `amp-config-cfmethyl-stacked-2022` | cfMethyl-Seq stacked ensemble (2022) | none | `amp-protocol-cfmethyl-randomsplit-detection` |  |  |

### protein-variant-stability (99)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc20260930-proteingym-amfr-config-aido-protein-rag-16b` | AIDO Protein-RAG (16B) [ProteinGym 144fe22b snapshot] | `uc20260930-model-aido-protein-rag` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-carp-38m` | CARP (38M) [ProteinGym 144fe22b snapshot] | `uc20260930-model-carp` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-carp-600k` | CARP (600K) [ProteinGym 144fe22b snapshot] | `uc20260930-model-carp` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-carp-640m` | CARP (640M) [ProteinGym 144fe22b snapshot] | `uc20260930-model-carp` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-carp-76m` | CARP (76M) [ProteinGym 144fe22b snapshot] | `uc20260930-model-carp` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-deepsequence-ensemble` | DeepSequence (ensemble) [ProteinGym 144fe22b snapshot] | `uc20260930-model-deepsequence` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-deepsequence-single` | DeepSequence (single) [ProteinGym 144fe22b snapshot] | `uc20260930-model-deepsequence` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-escott` | ESCOTT [ProteinGym 144fe22b snapshot] | `uc20260930-model-escott` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-esm-1b` | ESM-1b [ProteinGym 144fe22b snapshot] | `uc20260930-model-esm-1b` | `uc20260930-proteingym-amfr-protocol` | foundation_model | 2 other configuration(s) of uc20260930-model-esm-1b are tagged foundation_model |
| `uc20260930-proteingym-amfr-config-esm-1v-ensemble` | ESM-1v (ensemble) [ProteinGym 144fe22b snapshot] | `discovery-model-esm-1v` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-esm-1v-single` | ESM-1v (single) [ProteinGym 144fe22b snapshot] | `discovery-model-esm-1v` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-esm-c-300m` | ESM-C (300M) [ProteinGym 144fe22b snapshot] | `discovery-model-esmc` | `uc20260930-proteingym-amfr-protocol` | foundation_model | 8 other configuration(s) of discovery-model-esmc are tagged foundation_model |
| `uc20260930-proteingym-amfr-config-esm-c-600m` | ESM-C (600M) [ProteinGym 144fe22b snapshot] | `discovery-model-esmc` | `uc20260930-proteingym-amfr-protocol` | foundation_model | 8 other configuration(s) of discovery-model-esmc are tagged foundation_model |
| `uc20260930-proteingym-amfr-config-esm-if1` | ESM-IF1 [ProteinGym 144fe22b snapshot] | `discovery-model-esm-if1` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-esm2-150m` | ESM2 (150M) [ProteinGym 144fe22b snapshot] | `discovery-model-esm-2` | `uc20260930-proteingym-amfr-protocol` | foundation_model | 2 other configuration(s) of discovery-model-esm-2 are tagged foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-15b` | ESM2 (15B) [ProteinGym 144fe22b snapshot] | `discovery-model-esm-2` | `uc20260930-proteingym-amfr-protocol` | foundation_model | 2 other configuration(s) of discovery-model-esm-2 are tagged foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-35m` | ESM2 (35M) [ProteinGym 144fe22b snapshot] | `discovery-model-esm-2` | `uc20260930-proteingym-amfr-protocol` | foundation_model | 2 other configuration(s) of discovery-model-esm-2 are tagged foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-3b` | ESM2 (3B) [ProteinGym 144fe22b snapshot] | `discovery-model-esm-2` | `uc20260930-proteingym-amfr-protocol` | foundation_model | 2 other configuration(s) of discovery-model-esm-2 are tagged foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-650m` | ESM2 (650M) [ProteinGym 144fe22b snapshot] | `discovery-model-esm-2` | `uc20260930-proteingym-amfr-protocol` | foundation_model | 2 other configuration(s) of discovery-model-esm-2 are tagged foundation_model |
| `uc20260930-proteingym-amfr-config-esm2-8m` | ESM2 (8M) [ProteinGym 144fe22b snapshot] | `discovery-model-esm-2` | `uc20260930-proteingym-amfr-protocol` | foundation_model | 2 other configuration(s) of discovery-model-esm-2 are tagged foundation_model |
| `uc20260930-proteingym-amfr-config-esm3-open-1-4b` | ESM3 open (1.4B) [ProteinGym 144fe22b snapshot] | `discovery-model-esm3` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-eve-ensemble` | EVE (ensemble) [ProteinGym 144fe22b snapshot] | `uc20260930-model-eve` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-eve-single` | EVE (single) [ProteinGym 144fe22b snapshot] | `uc20260930-model-eve` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-evmutation` | EVmutation [ProteinGym 144fe22b snapshot] | `uc20260930-method-evmutation` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-gemme` | GEMME [ProteinGym 144fe22b snapshot] | `uc20260930-method-gemme` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-mif` | MIF [ProteinGym 144fe22b snapshot] | `uc20260930-model-mif` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-mif-st` | MIF-ST [ProteinGym 144fe22b snapshot] | `uc20260930-model-mif-st` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-msa-transformer-ensemble` | MSA Transformer (ensemble) [ProteinGym 144fe22b snapshot] | `uc20260930-model-msa-transformer` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-msa-transformer-single` | MSA Transformer (single) [ProteinGym 144fe22b snapshot] | `uc20260930-model-msa-transformer` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-mulan` | MULAN [ProteinGym 144fe22b snapshot] | `uc20260930-model-mulan` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-poet-200m` | PoET (200M) [ProteinGym 144fe22b snapshot] | `uc20260930-model-poet` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen2-base` | Progen2 Base [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen2` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen2-l` | Progen2 L [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen2` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen2-m` | Progen2 M [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen2` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen2-s` | Progen2 S [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen2` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen2-xl` | Progen2 XL [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen2` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen3-112m` | Progen3 112m [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen3` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen3-1b` | Progen3 1B [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen3` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen3-219m` | Progen3 219m [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen3` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen3-339m` | Progen3 339m [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen3` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen3-3b` | Progen3 3B [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen3` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-progen3-762m` | Progen3 762m [ProteinGym 144fe22b snapshot] | `uc20260930-model-progen3` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-prosst-k-1024` | ProSST (K=1024) [ProteinGym 144fe22b snapshot] | `uc20260930-model-prosst` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-prosst-k-128` | ProSST (K=128) [ProteinGym 144fe22b snapshot] | `uc20260930-model-prosst` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-prosst-k-20` | ProSST (K=20) [ProteinGym 144fe22b snapshot] | `uc20260930-model-prosst` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-prosst-k-2048` | ProSST (K=2048) [ProteinGym 144fe22b snapshot] | `uc20260930-model-prosst` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-prosst-k-4096` | ProSST (K=4096) [ProteinGym 144fe22b snapshot] | `uc20260930-model-prosst` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-prosst-k-512` | ProSST (K=512) [ProteinGym 144fe22b snapshot] | `uc20260930-model-prosst` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-proteinmpnn` | ProteinMPNN [ProteinGym 144fe22b snapshot] | `discovery-model-proteinmpnn` | `uc20260930-proteingym-amfr-protocol` | supervised_machine_learning | 1 other configuration(s) of discovery-model-proteinmpnn are tagged supervised_machine_learning |
| `uc20260930-proteingym-amfr-config-protgpt2` | ProtGPT2 [ProteinGym 144fe22b snapshot] | `uc20260930-model-protgpt2` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protriever` | Protriever [ProteinGym 144fe22b snapshot] | `uc20260930-model-protriever` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-ensemble` | ProtSSN (ensemble) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-k-10-h-1280` | ProtSSN (k=10, h=1280) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-k-10-h-512` | ProtSSN (k=10, h=512) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-k-10-h-768` | ProtSSN (k=10, h=768) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-k-20-h-1280` | ProtSSN (k=20, h=1280) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-k-20-h-512` | ProtSSN (k=20, h=512) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-k-20-h-768` | ProtSSN (k=20, h=768) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-k-30-h-1280` | ProtSSN (k=30, h=1280) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-k-30-h-512` | ProtSSN (k=30, h=512) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-protssn-k-30-h-768` | ProtSSN (k=30, h=768) [ProteinGym 144fe22b snapshot] | `uc20260930-model-protssn` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-rita-l` | RITA L [ProteinGym 144fe22b snapshot] | `uc20260930-model-rita` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-rita-m` | RITA M [ProteinGym 144fe22b snapshot] | `uc20260930-model-rita` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-rita-s` | RITA S [ProteinGym 144fe22b snapshot] | `uc20260930-model-rita` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-rita-xl` | RITA XL [ProteinGym 144fe22b snapshot] | `uc20260930-model-rita` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-rsalor` | RSALOR [ProteinGym 144fe22b snapshot] | `uc20260930-method-rsalor` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-s2f` | S2F [ProteinGym 144fe22b snapshot] | `uc20260930-model-s2f` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-s2f-msa` | S2F-MSA [ProteinGym 144fe22b snapshot] | `uc20260930-model-s2f-msa` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-s3f` | S3F [ProteinGym 144fe22b snapshot] | `uc20260930-model-s3f` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-s3f-msa` | S3F-MSA [ProteinGym 144fe22b snapshot] | `uc20260930-model-s3f-msa` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-saprot-35m` | SaProt (35M) [ProteinGym 144fe22b snapshot] | `uc20260930-model-saprot` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-saprot-650m` | SaProt (650M) [ProteinGym 144fe22b snapshot] | `uc20260930-model-saprot` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-site-independent` | Site-Independent [ProteinGym 144fe22b snapshot] | `uc20260930-method-site-independent` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-siterm` | SiteRM [ProteinGym 144fe22b snapshot] | `uc20260930-model-siterm` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-trancepteve-l` | TranceptEVE L [ProteinGym 144fe22b snapshot] | `uc20260930-model-trancepteve` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-trancepteve-m` | TranceptEVE M [ProteinGym 144fe22b snapshot] | `uc20260930-model-trancepteve` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-trancepteve-s` | TranceptEVE S [ProteinGym 144fe22b snapshot] | `uc20260930-model-trancepteve` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-tranception-l` | Tranception L [ProteinGym 144fe22b snapshot] | `uc20260930-model-tranception` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-tranception-l-no-retrieval` | Tranception L no retrieval [ProteinGym 144fe22b snapshot] | `uc20260930-model-tranception` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-tranception-m` | Tranception M [ProteinGym 144fe22b snapshot] | `uc20260930-model-tranception` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-tranception-m-no-retrieval` | Tranception M no retrieval [ProteinGym 144fe22b snapshot] | `uc20260930-model-tranception` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-tranception-s` | Tranception S [ProteinGym 144fe22b snapshot] | `uc20260930-model-tranception` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-tranception-s-no-retrieval` | Tranception S no retrieval [ProteinGym 144fe22b snapshot] | `uc20260930-model-tranception` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-unirep` | Unirep [ProteinGym 144fe22b snapshot] | `uc20260930-model-unirep` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-unirep-evotuned` | Unirep evotuned [ProteinGym 144fe22b snapshot] | `uc20260930-model-unirep-evotuned` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-venusrem` | VenusREM [ProteinGym 144fe22b snapshot] | `uc20260930-model-venusrem` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-vespa` | VESPA [ProteinGym 144fe22b snapshot] | `uc20260930-model-vespa` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-vespag` | VespaG [ProteinGym 144fe22b snapshot] | `uc20260930-model-vespag` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-vespal` | VESPAl [ProteinGym 144fe22b snapshot] | `uc20260930-model-vespal` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-wavenet` | Wavenet [ProteinGym 144fe22b snapshot] | `uc20260930-model-wavenet` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-xtrimopglm-100b-int4` | xTrimoPGLM-100B-int4 [ProteinGym 144fe22b snapshot] | `uc20260930-model-xtrimopglm` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-xtrimopglm-10b-mlm` | xTrimoPGLM-10B-MLM [ProteinGym 144fe22b snapshot] | `uc20260930-model-xtrimopglm` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-xtrimopglm-1b-clm` | xTrimoPGLM-1B-CLM [ProteinGym 144fe22b snapshot] | `uc20260930-model-xtrimopglm` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-xtrimopglm-1b-mlm` | xTrimoPGLM-1B-MLM [ProteinGym 144fe22b snapshot] | `uc20260930-model-xtrimopglm` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-xtrimopglm-3b-clm` | xTrimoPGLM-3B-CLM [ProteinGym 144fe22b snapshot] | `uc20260930-model-xtrimopglm` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-xtrimopglm-3b-mlm` | xTrimoPGLM-3B-MLM [ProteinGym 144fe22b snapshot] | `uc20260930-model-xtrimopglm` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `uc20260930-proteingym-amfr-config-xtrimopglm-7b-clm` | xTrimoPGLM-7B-CLM [ProteinGym 144fe22b snapshot] | `uc20260930-model-xtrimopglm` | `uc20260930-proteingym-amfr-protocol` |  |  |
| `rewire-local-20260920-configuration-proteingym-esm2` | ESM-2 8M masked-marginal scoring (ProteinGym v1.3 AMFR substitution assay) | none | `rewire-protocol-proteingym-amfr-v13` |  |  |
| `rewire-local-20260921-configuration-proteingym-random` | Seeded random ranking control (ProteinGym v1.3 AMFR substitution assay) | none | `rewire-protocol-proteingym-amfr-random-v13` |  |  |

### rare-disease-candidate-ranking (3)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc-clinical-20260930-talos-default` | Talos default filtering, 2026 study | `uc-clinical-20260930-method-talos` | `uc-clinical-20260930-talos-rgp-singleton-protocol` | conventional_pipeline | 2 other configuration(s) of uc-clinical-20260930-method-talos are tagged conventional_pipeline |
| `uc-clinical-20260930-talos-strict` | Talos strict phenotype-match filtering, 2026 study | `uc-clinical-20260930-method-talos` | `uc-clinical-20260930-talos-rgp-singleton-protocol` | conventional_pipeline | 2 other configuration(s) of uc-clinical-20260930-method-talos are tagged conventional_pipeline |
| `uc-clinical-20260930-exomiser-v14` | Exomiser v14 default, Talos 2026 comparison | `uc-clinical-20260930-method-exomiser` | `uc-clinical-20260930-exomiser-acg-protocol` | conventional_pipeline | 87 other configuration(s) of uc-clinical-20260930-method-exomiser are tagged conventional_pipeline |

### regulatory-variant-gene-follow-up (6)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `ucc-research-config-mprabc-abc` | Activity-by-Contact (ABC) - K562 published comparison | `ucc-research-method-mprabc-abc` | `ucc-research-protocol-mprabc-k562` | conventional_pipeline | ABC is a fixed activity times contact score; the Gschwind 2026 ABC configuration is conventional_pipeline, the DNALongBench one supervised_machine_learning (see notes) |
| `ucc-research-config-mprabc-full` | MPRabc - K562 published comparison | `ucc-research-method-mprabc-full` | `ucc-research-protocol-mprabc-k562` |  |  |
| `ucc-research-config-mprabc-megamap` | MPRabc megamap Hi-C - K562 published comparison | `ucc-research-method-mprabc-megamap` | `ucc-research-protocol-mprabc-k562` |  |  |
| `ucc-research-config-mprabc-mpralegnet` | MPRabc (MPRALegNet only; no Sei) - K562 published comparison | `ucc-research-method-mprabc-mpralegnet` | `ucc-research-protocol-mprabc-k562` |  |  |
| `ucc-research-config-mprabc-re2g` | ENCODE-rE2G - K562 published comparison | `ucc-research-method-mprabc-re2g` | `ucc-research-protocol-mprabc-k562` | supervised_machine_learning | 1 other configuration(s) of ucc-research-method-mprabc-re2g are tagged supervised_machine_learning |
| `ucc-research-config-mprabc-sei` | MPRabc (Sei only; no MPRALegNet) - K562 published comparison | `ucc-research-method-mprabc-sei` | `ucc-research-protocol-mprabc-k562` |  |  |

### rhodopsin-wavelength-transfer (8)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc20260930-rhomax-config-blasso` | BLASSO (RhoMax paper eV-trained comparator) | `uc20260930-method-blasso-rhodopsin-predictor` | `uc20260930-rhomax-protocol-split-3` |  |  |
| `uc20260930-rhomax-config-rhomax` | RhoMax | `uc20260930-model-rhomax` | `uc20260930-rhomax-protocol-split-3` |  |  |
| `uc20260930-rhomax-config-rhomax-retinal` | RhoMax + retinal | `uc20260930-model-rhomax` | `uc20260930-rhomax-protocol-split-3` |  |  |
| `rewire-local-20260920-configuration-flip2-composition` | Amino-acid composition + fixed ridge (FLIP2 Rhomax by_wild_type) | none | `rewire-protocol-flip2-rhomax-by-wild-type-v1` |  |  |
| `rewire-local-20260920-configuration-flip2-train-mean` | Training-mean control (FLIP2 Rhomax by_wild_type) | none | `rewire-protocol-flip2-rhomax-by-wild-type-v1` |  |  |
| `rewire-local-20260921-configuration-composition22` | Protein composition + fixed ridge probe (FLIP2 Rhomax by_wild_type) | none | `rewire-protocol-flip2-rhomax-by-wild-type-v1` |  |  |
| `rewire-local-20260921-configuration-esm2-35m` | ESM-2 35M frozen residue-mean embeddings + fixed ridge (Rewire) (FLIP2 Rhomax by_wild_type) | none | `rewire-protocol-flip2-rhomax-by-wild-type-v1` |  |  |
| `rewire-local-20260921-configuration-esm2-8m` | ESM-2 8M frozen residue-mean embeddings + fixed ridge (Rewire) (FLIP2 Rhomax by_wild_type) | none | `rewire-protocol-flip2-rhomax-by-wild-type-v1` |  |  |

### somatic-small-variant-oncogenicity (2)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc-clinical-20260930-oncovi-study` | OncoVI 2026 publication configuration | `uc-clinical-20260930-method-oncovi` | `uc-clinical-20260930-oncovi-expert-protocol` |  |  |
| `uc-clinical-20260930-oncovi-prior-mtb` | Historical Erlangen MTB protein-function interpretation | none | `uc-clinical-20260930-oncovi-expert-protocol` |  |  |

### splicing-follow-up (6)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `rewire-model-baseline-kmer-position-v2` | Corrected k-mer / position baseline | none | `rewire-mfass-v2` |  |  |
| `rewire-local-20260921-configuration-mfass-prior` | Training class prior / majority (MFASS v2 canonical held-out split) | none | `rewire-mfass-v2` |  |  |
| `rewire-mfass-matched-v1-configuration-p0` | Pangolin 1.0.2 + per-gene masking patch · mask False (P0) | `discovery-model-pangolin` | `rewire-mfass-matched-v1-protocol` | supervised_machine_learning | 1 other configuration(s) of discovery-model-pangolin are tagged supervised_machine_learning |
| `rewire-mfass-matched-v1-configuration-p1` | Pangolin 1.0.2 + per-gene masking patch · mask True (P1) | `discovery-model-pangolin` | `rewire-mfass-matched-v1-protocol` | supervised_machine_learning | 1 other configuration(s) of discovery-model-pangolin are tagged supervised_machine_learning |
| `rewire-mfass-matched-v1-configuration-s0` | SpliceAI 1.3.1 · mask 0 (S0) | `discovery-model-spliceai` | `rewire-mfass-matched-v1-protocol` | specialist | 1 other configuration(s) of discovery-model-spliceai are tagged specialist |
| `rewire-mfass-matched-v1-configuration-s1` | SpliceAI 1.3.1 · mask 1 (S1) | `discovery-model-spliceai` | `rewire-mfass-matched-v1-protocol` | specialist | 1 other configuration(s) of discovery-model-spliceai are tagged specialist |

### structural-hypotheses-experiments (7)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `ucc-docking-cluspro-bm5-2020-config-others` | ClusPro BM5 Table1 others | `ucc-docking-cluspro-bm5-2020-method` | `ucc-docking-cluspro-bm5-2020-protocol-others-top10` |  |  |
| `ucc-docking-cluspro-bm5-2020-config-enzyme-balanced` | ClusPro BM5 Table1 enzyme-balanced | `ucc-docking-cluspro-bm5-2020-method` | `ucc-docking-cluspro-bm5-2020-protocol-enzyme-top30` |  |  |
| `ucc-research-config-foldbench-af3` | AlphaFold 3 - FoldBench published inference | `discovery-model-alphafold-3` | `ucc-research-protocol-foldbench-protein-protein` | foundation_model | 12 other configuration(s) of discovery-model-alphafold-3 are tagged foundation_model |
| `ucc-research-config-foldbench-boltz1` | Boltz-1 - FoldBench published inference | `discovery-model-boltz` | `ucc-research-protocol-foldbench-protein-protein` | foundation_model | 1 other configuration(s) of discovery-model-boltz are tagged foundation_model |
| `ucc-research-config-foldbench-chai1` | Chai-1 - FoldBench published inference | `catalog-model-chai-1` | `ucc-research-protocol-foldbench-protein-protein` | foundation_model | 2 other configuration(s) of catalog-model-chai-1 are tagged foundation_model |
| `ucc-research-config-foldbench-helixfold3` | HelixFold 3 - FoldBench published inference | `ucc-research-model-helixfold3` | `ucc-research-protocol-foldbench-protein-protein` |  |  |
| `ucc-research-config-foldbench-protenix` | Protenix - FoldBench published inference | `ucc-research-model-protenix` | `ucc-research-protocol-foldbench-protein-protein` |  |  |

### therapeutic-target-validation (21)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `ucc-research-config-cppc-submission-row-11` | CPPC original submission row 11 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-12` | CPPC original submission row 12 (5Features) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-13` | CPPC original submission row 13 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-14` | CPPC original submission row 14 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-15` | CPPC original submission row 15 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-16` | CPPC original submission row 16 (scETM) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-17` | CPPC original submission row 17 (scTenifoldNet) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-18` | CPPC original submission row 18 (GO_knn) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-19` | CPPC original submission row 19 (LowExp) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-2` | CPPC original submission row 2 (PPI_Weighted) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-20` | CPPC original submission row 20 (unnamed method) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-21` | CPPC original submission row 21 (interv) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-22` | CPPC original submission row 22 (GO-node2vec) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-23` | CPPC original submission row 23 (Matrix_completion) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-24` | CPPC original submission row 24 (GeneVector) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-3` | CPPC original submission row 3 (GWPS_K562 (H2M)) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-4` | CPPC original submission row 4 (14Features) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-5` | CPPC original submission row 5 (scBERT) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-6` | CPPC original submission row 6 (scVI) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-submission-row-7` | CPPC original submission row 7 (Expression_Conditioned) | none | `ucc-research-protocol-cppc-challenge2-original` |  |  |
| `ucc-research-config-cppc-pooled-nominations` | CPPC submitted-method nomination campaign | none | `ucc-research-protocol-cppc-prospective-selection` |  |  |

### unresolved-rare-disease-reanalysis (4)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc-clinical-20260930-talos-monthly` | Talos monthly iterative reanalysis with clinical confirmation | `uc-clinical-20260930-method-talos` | `uc-clinical-20260930-reanalysis-programme-protocol` | conventional_pipeline | 2 other configuration(s) of uc-clinical-20260930-method-talos are tagged conventional_pipeline |
| `uc-clinical-20260930-talos-default` | Talos default filtering, 2026 study | `uc-clinical-20260930-method-talos` | `uc-clinical-20260930-talos-acg-full-protocol` | conventional_pipeline | 2 other configuration(s) of uc-clinical-20260930-method-talos are tagged conventional_pipeline |
| `uc-clinical-20260930-talos-strict` | Talos strict phenotype-match filtering, 2026 study | `uc-clinical-20260930-method-talos` | `uc-clinical-20260930-talos-acg-full-protocol` | conventional_pipeline | 2 other configuration(s) of uc-clinical-20260930-method-talos are tagged conventional_pipeline |
| `uc-clinical-20260930-exomiser-v14` | Exomiser v14 default, Talos 2026 comparison | `uc-clinical-20260930-method-exomiser` | `uc-clinical-20260930-exomiser-acg-protocol` | conventional_pipeline | 87 other configuration(s) of uc-clinical-20260930-method-exomiser are tagged conventional_pipeline |

### utr-translation-baselines (12)

| Configuration | Name | Method or model | Protocol | Suggested | Evidence |
| --- | --- | --- | --- | --- | --- |
| `uc20260930-framepool-config-3mer-random-forest` | 3mer_random_forest | `uc20260930-method-k-mer-count-random-forest` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `uc20260930-framepool-config-4mer-random-forest` | 4mer_random_forest | `uc20260930-method-k-mer-count-random-forest` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `uc20260930-framepool-config-5mer-frame-forest` | 5mer_frame_forest | `uc20260930-method-frame-aware-k-mer-random-forest` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `uc20260930-framepool-config-frame-forest-4mer` | frame_forest (4mer) | `uc20260930-method-frame-aware-k-mer-random-forest` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `uc20260930-framepool-config-frame-forest-hyperopt` | frame_forest_hyperopt | `uc20260930-method-frame-aware-k-mer-random-forest` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `uc20260930-framepool-config-framepool-100` | FramePool 100 | `uc20260930-model-framepool` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `uc20260930-framepool-config-framepool-50` | FramePool 50 | `uc20260930-model-framepool` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `uc20260930-framepool-config-framepool-combined` | FramePool Combined | `uc20260930-model-framepool` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `uc20260930-framepool-config-optimus-100` | Optimus 100 | `uc20260930-model-optimus-5-prime` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `uc20260930-framepool-config-optimus-50` | Optimus 50 | `uc20260930-model-optimus-5-prime` | `uc20260930-framepool-protocol-random-25-100nt` |  |  |
| `rewire-local-20260920-configuration-mrnabench-composition` | Sequence composition + RidgeCV (mRNABench Sample designed MRL) | none | `rewire-protocol-mrnabench-designed-mrl-v1` |  |  |
| `rewire-local-20260920-configuration-mrnabench-train-mean` | Training-mean control (mRNABench Sample designed MRL) | none | `rewire-protocol-mrnabench-designed-mrl-v1` |  |  |

