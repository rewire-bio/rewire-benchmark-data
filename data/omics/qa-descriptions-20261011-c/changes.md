# Issue #88 placeholder descriptions, batch C, 2026-10-11

Scope: 47 of the 167 placeholder records in `qa-descriptions-20261011/scan.md`:

- the 35 records with "Identity as reported in this paper. Unspecified versions are not assumed equivalent to other papers.";
- the 6 remaining "Method identity used in the scTab comparison." methods (the other 6 records in that scan group are the TAPE records, changed in batch B);
- the 6 "Method or ablation in the primary-source enhancer-gene benchmark." methods.

41 records are changed. The other 6 are the `excluded` model records in the "Identity as reported" group; they are skipped and listed below.

The method is the same as batches A and B: one functional sentence from the record's primary source, no provenance in the description, and the old text kept in a metadata-correction claim. `build.py` reads the original lines from origin/main, writes `methods.jsonl` and `pipelines.jsonl` in place and regenerates `batch.jsonl`; `--check` verifies without writing. Only `description` changes: no record gains or loses a source, because every description rests on a source the record already cites.

`batch.jsonl` holds 41 records, all `needs_review`: 41 correction claims and no new sources.

Integrated together with batches a to e on 2026-10-11, after independent review: see `review.json` in this folder and `docs/reviews/2026-10-11-description-batches-a-e.md`. The records are now `source_checked`. Before review: `records -- add` and `records -- change` were not yet run. In a throwaway copy of origin/main, adding the batch, applying `build.py` and recording the 41 changes passed SHACL, `records check` (45,645 records) and the canonical-store, attribute, profile, source-identity and evidence-completion tests. Typecheck and the data build also passed, on a run of the same store edits made before the correction claims' `source_locator` strings were reflowed onto one line; the rerun after that edit was stopped part way because the machine ran out of disk space, so the reviewer may want to run `npm run build` once. The copy was deleted.

## Sources

No source records are added. Every source used was re-downloaded on 2026-10-11 and compared against its pin. Only Europe PMC REST, static-content.springer.com and the publisher URL already recorded for the ESM2 OFS paper were used; no email or other personal identifier was sent.

- 22 of the 27 paper sources behind the 29 "Identity as reported" pipelines reproduce their `artifact_sha256` (two papers each cover two pipelines), as do all three scTab and MPRabc sources (`ucc-research-source-mprabc`, `ucc-research-source-sctab-paper`, `ucc-research-source-sctab-supp`).
- 5 Europe PMC full texts return different bytes today: `clape-smb-2024` (PMC11542454), `gsmformer-ppi-2026` (PMC12873117), `scatac-llmda-2026` (PMC13132462), `arsenal-regulatory-dna-2026` (PMC12889687) and `spin-protein-function-2026` (PMC12970593). These are the same non-byte-stable Europe PMC renderings seen in batch B. For each of the five, the sentence used comes from the abstract in the copy retrieved on 2026-10-11, and the pinned bytes could not be reproduced for comparison; the reviewer may want to confirm those five abstracts.

## Record-by-record changes

Every row below is one record. "Locator" is the `source_locator` of its correction claim.

### "Identity as reported in this paper" pipelines (29)

For these records the description follows the record's own reviewed profile (`attributes.profile`, automated source review 2026-09-16): the `summary` sentence and the "Architecture / procedure" fact, both already tied to the pinned primary source. Where the record is one configuration among several in the same paper, the sentence names what differs, and the extra paper section read for that clause is listed in the locator.

#### `reported-model-0829aff5471d4b` Stacking-Auto

- Old: Identity as reported in this paper. Unspecified versions are not assumed equivalent to other papers.
- New: Sequence-based enhancer-location stage of the Hi-Enhancer framework: DNABERT-2 extracts DNA sequence features and a stacking ensemble built with AutoGluon predicts enhancer labels.
- Source: `hi-enhancer-2025`. Locator adds: Abstract/Results.

#### `reported-model-1a67087ac262c5` Nucleotide Transformer + NN (middle)

- New: Classifies gene fusion breakpoints from 10 kbp DNA windows using frozen Nucleotide Transformer embeddings, concatenating the middle embedding at the breakpoint of each sequence and training a small neural-network classifier on it.
- Source: `fusion-breakpoint-foundation-models-2026`. The "middle" label is the paper's own: it extracts the embedding at the breakpoint and concatenates the two sequences' middle embeddings, as against the mean-pooling variant.

#### `reported-model-1be5c4b7c52a41` scVI + scANVI

- New: Probabilistic single-cell comparator in the scaLR study: variational autoencoders infer low-dimensional cell representations and the scANVI stage uses annotation labels for cell-type prediction.
- Source: `scalr-2025`. The description stays at the level the scaLR paper describes this comparator, which is the source of the result.

#### `reported-model-2894d253c5e8a8` CUPID Data-aug-Avg

- New: Predicts pairwise non-coding RNA interactions from sequence alone, with GenerRNA embeddings average-pooled over each molecule and fed to a feed-forward classifier trained on the augmented pairs.
- Source: `cupid-rna-interactions-2026`. "Data-aug-Avg" is the paper's label for data augmentation with average pooling.

#### `reported-model-3f850c08d76410` DEBFold

- New: Predicts RNA secondary structure in two stages: convolutional encoding and decoding with self-attention over the one-hot sequence and existing thermodynamic tool predictions estimates per-base scores, which then constrain free-energy minimisation.
- Source: `debfold-2024`.

#### `reported-model-40ce004270dee4` ESM2 OFS pseudo-perplexity

- New: Estimates protein fitness from the negative pseudo-perplexity of a sequence, approximated in a single unmasked forward pass by an ensemble of eight multilayer perceptrons that predict the ESM-2 650M masked residue profiles.
- Source: `esm2-ofs-fitness-2025` (publisher PDF, hash reproduces). Section III states the eight-MLP ensemble, the ESM-2 650M profile target and that pseudo-perplexity is inversely related to fitness so its negative serves as the estimate.

#### `reported-model-41ae49bb40ed8e` ProteinBERT LLM-encoding model

- New: mRNA-protein interaction predictor that encodes the RNA-binding protein with ProteinBERT embeddings and feeds them to the study's attention-based prediction framework alongside the RNA representation.
- Source: `mrna-protein-diversity-2026`. This is the "language model-derived encoding" arm of the paper's three encoding strategies.

#### `reported-model-4921459942b45f` ESM-2 650M embeddings + classifier

- New: Chimeric antibody-deamidation predictor: a global module of ESM-2 650M embeddings of the full antibody sequence is concatenated with a local windowed-sequence module and classified by a dense head.
- Source: `antibody-deamidation-plm-2024`. The paper names the checkpoint (esm2_t33_650m_UR50D) and keeps an "ESM-2 only, without the local module" comparator separate from this chimeric model.

#### `reported-model-49bc768f46b366` CATHe2 + ProstT5

- New: Classifies protein domains into CATH superfamilies with a feed-forward network over ProstT5 amino-acid embeddings and 3Di structural-alphabet embeddings.
- Source: `cathe2-2025`.

#### `reported-model-4ce8cae0f2eafc` TCINet + HTRS

- New: Metagenomic pathogen identification pipeline: TCINet turns sequencing reads into taxonomic embeddings and sparse abundance estimates with uncertainty, and the HTRS post-inference module enforces taxonomic constraints and recalibrates confidence.
- Source: `metagenomic-pathogens-2025`.

#### `reported-model-57dbab30462150` CLAPE-SMB with ESM-2

- New: Predicts small-molecule-binding residues from sequence alone, using frozen esm2_t33_650M_UR50D residue embeddings with a contrastive-learning binding-site predictor.
- Source: `clape-smb-2024` (Europe PMC text differs from its pin; the sentence is in the abstract, and the checkpoint is in Methods/Sequence embedding as recorded in the profile).

#### `reported-model-60455ff7cc0c15` scRegNet (Geneformer backbone)

- New: Predicts gene-regulatory links by combining context-aware gene representations from the pretrained Geneformer single-cell foundation model with graph-based representations learned from known regulatory interactions.
- Source: `scregnet-2025`. The paper's framework description is shared; the backbone is what differs between this record and the scBERT one.

#### `reported-model-67ea6bd77b2ed1` ESM2_AMPS

- New: Predicts binary protein-protein interactions from ESM-2 representations of sequence segments fused by a transformer encoder; AMPS is the segment-feature variant of the framework.
- Source: `esm2-amp-2025`. The abstract distinguishes ESM2_AMPS (segment features) from ESM2_AMP_CSE.

#### `reported-model-688eb780ef7d2e` PC-mer + LR

- New: Metagenomic classification baseline in which PC-mer encodes nucleotide physicochemical properties as a compressed k-mer feature vector and an L2-regularised logistic-regression classifier assigns taxa.
- Source: `pc-mer-2024`. The L2 regularisation is from the paper's classifier list; the compression by a factor of 2^k is from the abstract.

#### `reported-model-6c0bc8d297cc7a` DiffDock-NMDN

- New: End-to-end blind docking and virtual screening protocol: DiffDock samples ligand poses, the normalised mixture density network score selects a pose, and an interaction module estimates binding affinity.
- Source: `nmdn-2025`.

#### `reported-model-73ae07fb5be204` GSMFormer-PPI + ProstT5

- New: Predicts protein-protein interactions from three modalities: MaSIF surface descriptors, graph convolutions over the 3D structure, and ProstT5 residue embeddings as graph node features, fused by a transformer encoder.
- Source: `gsmformer-ppi-2026` (Europe PMC text differs from its pin; the three modalities and the fusion are in the abstract, and the per-residue embeddings as node features are in Methods/Model architecture). ProstT5 is the embedding choice for this row, as against the paper's ESM-2, ProtT5 and one-hot comparators.

#### `reported-model-7ad28cd57f5f5b` ERNIE-RNA + CoBRA

- New: Predicts small-molecule-binding nucleotides from sequence, feeding residue-level ERNIE-RNA embeddings to a multilayer-perceptron binary classifier with no structural input.
- Source: `cobra-rna-binding-2026`.

#### `reported-model-7cf2f9951e1dba` scaLR

- New: Low-resource single-cell annotation platform: it trains on feature subsets to rank gene importance, retrains the final model on the top-K features, and batches samples across CPUs to limit memory.
- Source: `scalr-2025`.

#### `reported-model-86393c76dd8fa9` MegSite + ESM3

- New: Predicts nucleic-acid-binding residues by fusing multimodal ESM3 sequence, structure and function embeddings with ESM-MSA features through cross-attention, alongside an equivariant graph network over the residue contact map.
- Source: `megsite-2025`.

#### `reported-model-89f5a8f309fa18` scRegNet (scBERT backbone)

- New: Predicts gene-regulatory links by combining context-aware gene representations from the pretrained scBERT single-cell foundation model with graph-based representations learned from known regulatory interactions.
- Source: `scregnet-2025`.

#### `reported-model-8ad3e0cefde796` Vaxign-DL + ESM

- New: Predicts bacterial protective antigens with a deep classifier over 1,280 ESM-derived sequence features combined with the 509 biological and biomedical features of Vaxign-DL.
- Source: `vaxign-esm-2024`. Both counts are the paper's.

#### `reported-model-8cb3dd4e9f5b10` Lazypipe-nt

- New: Automated assembly and taxonomic-profiling pipeline for virus discovery in sequencing libraries; the nt variant assigns contigs by querying them with Centrifuge against the NCBI nucleotide collection.
- Source: `lazypipe-2020`. The paper defines Lazypipe-nt as exactly that alternative mapping strategy.

#### `reported-model-a0db32ae53e5ed` scLLMDA

- New: Annotates scATAC-seq cell types within one modality: DNABERT-2 encodes peak sequences, accessibility values complete the cell representation, and a graph neural network aligns reference and query similarity graphs by domain adaptation.
- Source: `scatac-llmda-2026` (Europe PMC text differs from its pin; the abstract carries the pipeline, and Materials and methods names DNABERT-2 as the DNA language model).

#### `reported-model-d6a7fa854437e8` scGPT + residual geometry

- New: Adds geometric features of the scGPT residual stream, including centred cosine similarity between gene vectors and PCA projections, to an expression baseline for predicting transcription-factor-target links.
- Source: `single-cell-residual-geometry-2026`. The feature set named is the one in the paper's comparison table (raw cosine, centred cosine, PCA-64 centred cosine, multi-layer bundle).

#### `reported-model-df0efcc0346224` binding-affinity meta-model

- New: Predicts ligand-protein binding affinity by combining empirical docking scores and sequence-based deep-learning predictions in a learned meta-model, optionally with physicochemical properties or molecular descriptors.
- Source: `ligand-affinity-meta-model-2024`.

#### `reported-model-e4710b1c3facf2` ESM-2 embedding + paper classifier

- New: ESM-2-only feature configuration of a clathrin-identification study: 1,280-dimensional ESM-2 embeddings feed an LSTM classifier, separately from the fused multi-model PLM-CLA predictor.
- Source: `clathrin-plm-2025`. The paper's "individual feature embeddings" section gives the 1,280 dimensions, the per-PLM LSTM models and the separate Fusion result; the record's linked result is the ESM-2 row.

#### `reported-model-ee1ae8162c7d67` ARSENAL+ChromBPNet

- New: Supervised chromatin-accessibility and regulatory-variant predictor in which embeddings from ARSENAL, a short-context masked DNA language model trained with motif-discovery regularisation, are added to ChromBPNet inputs.
- Source: `arsenal-regulatory-dna-2026` (Europe PMC text differs from its pin; the sentence is in the abstract). This source is a preprint, which the record's profile already notes.

#### `reported-model-f8f0257b98749a` SPIN + ESM2-35M

- New: Classifies proteins into family-specific functional classes with an ESM2-35M backbone whose first six encoder layers are frozen, adapting a question-answering architecture to locate a domain span and classify the selected region.
- Source: `spin-protein-function-2026` (Europe PMC text differs from its pin; the function-classification purpose is in the abstract and the six frozen of twelve layers are in 2.1 SPIN architecture). The record's name says "ESM2-35M", which the architecture section confirms.

#### `reported-model-fdac4c1ec8a433` ProtT5 embeddings + ensemble classifier

- New: Identifies protein-protein interaction sites from ProtT5 residue embeddings together with further sequence feature descriptors, classified by an ensemble of BiLSTM and capsule-network models.
- Source: `protein-binding-sites-2023`. The Introduction names ProtT5 as the feature extractor, the eleven additional descriptors and the BiLSTM plus capsule-network ensemble.

### scTab comparison methods (6)

These method records have no profile, so each description is one sentence from the scTab paper (`ucc-research-source-sctab-paper`), which they already cite. The per-record training settings stay on the configuration records, where they already are.

| Record | New description |
| --- | --- |
| `ucc-research-method-sctab` | Scalable implementation of the TabNet architecture adapted to single-cell data: expression is size-factor normalised and log1p transformed, and observation-wise feature attention selects the genes used for cell-type classification. |
| `ucc-research-method-ciform` | Transformer-based cell-type annotation model for single-cell RNA-seq, benchmarked against scTab. |
| `ucc-research-method-linear` | Logistic-regression cell-type classifier implemented to train on the full corpus with a cross-entropy loss, as the study's optimised linear baseline. |
| `ucc-research-method-mlp` | Multi-layer perceptron cell-type classifier previously proposed for single-cell annotation, used as a nonlinear baseline. |
| `ucc-research-method-xgboost` | Gradient-boosted tree classifier for tabular data, used as a nonlinear cell-type annotation baseline. |
| `ucc-research-method-uce` | Linear probe on Universal Cell Embeddings: a logistic-regression cell-type classifier is fitted to the precomputed frozen UCE embeddings hosted by CELLxGENE. |

CIForm, MLP and XGBoost are described only as far as the scTab paper describes them: it is the source of the results, and it introduces each in one clause. Their own papers would say more, but the records are the identities used in this comparison.

### MPRabc enhancer-gene methods (6)

All six cite `ucc-research-source-mprabc` and are described from it.

| Record | New description |
| --- | --- |
| `ucc-research-method-mprabc-abc` | Predicts enhancer-gene pairs with a score that combines a measure of element activity, such as histone acetylation, with the 3D contact frequency between the element and candidate genes. |
| `ucc-research-method-mprabc-re2g` | Supervised enhancer-gene prediction workflow that extends the Activity-by-Contact model, fitting a logistic-regression model on CRISPR-perturbation labels. |
| `ucc-research-method-mprabc-full` | Extends ENCODE-rE2G for enhancer-gene prediction by adding MPRALegNet-predicted log2(RNA/DNA) activity and Sei-derived regulatory features to its default DNase-seq and H3K27ac feature set, fitted with L2-regularised logistic regression. |
| `ucc-research-method-mprabc-megamap` | The MPRabc enhancer-gene model fitted with megamap Hi-C, an integration of Hi-C experiments across multiple tissues, in place of the standard Hi-C contact data. |
| `ucc-research-method-mprabc-mpralegnet` | Ablation of MPRabc that adds only the MPRALegNet-predicted MPRA activity features to ENCODE-rE2G, leaving out the Sei-derived regulatory features. |
| `ucc-research-method-mprabc-sei` | Ablation of MPRabc that adds only the Sei-derived regulatory features to ENCODE-rE2G, leaving out the MPRALegNet MPRA-activity features. |

The four ablation and variant sentences follow the paper's own list of ablations, "(i) ENCODE-rE2G, (ii) MPRabc (MPRALegNet only; no Sei), (iii) MPRabc (Sei only; no MPRALegNet), and (iv) full MPRabc", and its statement that both megamap and standard Hi-C versions exist.

## Skipped

The 6 `excluded` model records in the "Identity as reported" group are left unchanged, since excluded records are not published:

| Record | Name | Source |
| --- | --- | --- |
| `reported-model-0330736fd30b81` | Cellpose baseline | `kidney-cell-segmentation-2025` |
| `reported-model-e36efde25a6bf1` | Cellpose + easy 100% | `kidney-cell-segmentation-2025` |
| `reported-model-74844d9e698bcd` | Claude 3 Opus | `llm-cell-identification-2025` |
| `reported-model-91d4548437068f` | GPT-4 | `llm-cell-identification-2025` |
| `reported-model-f325d139514c74` | Claude 3.5 Sonnet | `anndictionary-2025` |
| `reported-model-f53062b0ae4285` | GPT-4o | `anndictionary-2025` |

No record in this batch went to `gaps.md`: every one has a source that describes its method.
