# Issue #88 placeholder descriptions, batch B, 2026-10-11

Scope: 57 of the 167 placeholder records in `qa-descriptions-20261011/scan.md`:
- the 26 catalogue candidates ("Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.");
- the 16 language models ("Language model identity as reported in this source ...");
- the 7 scFoundation Table 4 pipelines ("... cell-type annotation pipeline reported in the primary table");
- the 2 FoldBench models ("... represented by its exact FoldBench configuration");
- the 6 TAPE records ("Method identity as printed in the historical TAPE leaderboard").

51 are changed. The other 6, all language models, have no findable primary source and are left unchanged (gaps.md).

The method is the same as batch A: one functional sentence from the primary source, no provenance in the description, and the old text kept in a metadata-correction claim. `build.py` reads the original lines from origin/main, writes `models.jsonl`, `methods.jsonl` and `pipelines.jsonl` in place and regenerates `batch.jsonl`; `--check` verifies without writing. Only `description` and `source_ids` change.

`batch.jsonl` holds 63 records, all `needs_review`: 12 new sources and 51 correction claims.

Integrated together with batches a to e on 2026-10-11, after independent review: see `review.json` in this folder and `docs/reviews/2026-10-11-description-batches-a-e.md`. The records are now `source_checked`. Before review: `records -- add` and `records -- change` were not yet run. In a throwaway copy of origin/main, adding the batch, applying `build.py` and recording the 51 changes passed SHACL, `records check` (45,667 records) and the source-identity, attribute and evidence-completion tests. The copy was deleted.

## Catalogue candidates

Each of the 26 has a reviewed profile (`attributes.profile`: automated source review, 2026-09-16 or 2026-09-23) whose `summary` is a functional sentence tied to pinned primary sources: the paper, the official README and the model card. Its `summary_source_ids` are already in the record's `source_ids`. The description is that summary, word for word, except for Boltz-2, whose summary covers the Boltz family ("Boltz predicts biomolecular complex structures; Boltz-2 also predicts binding affinity.") and is restated about Boltz-2 alone.

I re-downloaded all 80 summary sources on 2026-10-11:
- 72 reproduce their pins. 52 matched as listed; 20 more matched once the Hugging Face `/blob/` page URL was replaced by its `/resolve/` raw-file URL, which is what the pins hash.
- The other 8:
  - Europe PMC full texts that return different bytes today: Kraken2 (PMC6883579), MetaPhlAn (PMC10635831), AlphaGenome (PMC12851941) and ProkBERT (PMC10810988). Each of these records also has a README or model card among its summary sources that does reproduce.
  - Two Europe PMC supplementary archives (ProteinMPNN, AlphaGenome) that timed out partway through (8 to 11 MB received).
  - The Chai-1 technical report, whose pin is of browser-extracted text, as its `hash_scope` says.
  - The scGPT bioRxiv preprint, which bioRxiv refused (17-byte response).

None of the 26 descriptions rests only on a source that failed to reproduce. The reviewer may still want to confirm the four Europe PMC texts.

## Sources added

Each artifact was retrieved on 2026-10-11 and hashed. Only Europe PMC REST, the arXiv API and anthropic.com were used; no email or other personal identifier was sent.

| Source | Artifact | Licence |
| --- | --- | --- |
| `qa-descriptions-20261011-b-source-claude3` | Anthropic, "The Claude 3 Model Family: Opus, Sonnet, Haiku", with the Claude 3.5 addenda (PDF) | Not stated |
| `qa-descriptions-20261011-b-source-gpt-4o` | arXiv:2410.21276, GPT-4o System Card | CC BY 4.0 |
| `qa-descriptions-20261011-b-source-o1` | arXiv:2412.16720, OpenAI o1 System Card | CC BY 4.0 |
| `qa-descriptions-20261011-b-source-gpt-oss` | arXiv:2508.10925, gpt-oss-120b & gpt-oss-20b Model Card | CC BY 4.0 |
| `qa-descriptions-20261011-b-source-llama3` | arXiv:2407.21783, The Llama 3 Herd of Models | arXiv non-exclusive |
| `qa-descriptions-20261011-b-source-qwen2` | arXiv:2407.10671, Qwen2 Technical Report | arXiv non-exclusive |
| `qa-descriptions-20261011-b-source-actinn` | Europe PMC MED/31359028 | Not stated |
| `qa-descriptions-20261011-b-source-celltypist` | Europe PMC MED/35549406 | CC BY |
| `qa-descriptions-20261011-b-source-scanpy` | Europe PMC MED/29409532 | CC BY |
| `qa-descriptions-20261011-b-source-scanvi` | Europe PMC MED/33491336 | CC BY |
| `qa-descriptions-20261011-b-source-scbert` | Europe PMC PPR/PPR428747 (bioRxiv preprint) | Not stated |
| `qa-descriptions-20261011-b-source-singlecellnet` | Europe PMC MED/31377170 | Not stated |

Existing sources re-downloaded for the other groups: `ucc-research-source-foldbench-paper`, `evidence-expansion-evidence-discovery-final-tape-6ee0c3e6` (the TAPE paper), `coverage-source-scfoundation-supp` and `evidence-official-9863509ad10b824dc96b` (scFoundation preprint). All four match their pins. The TAPE paper is added to the six TAPE records' `source_ids`.

## Changed records

### Catalogue candidates (description from the reviewed profile summary)

#### `catalog-model-alphagenome`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: AlphaGenome predicts regulatory activity and variant effects from long DNA sequences, with outputs for expression, splicing, chromatin and contact maps.
- Sources: `catalog-source-alphagenome`, `evidence-official-578439da3f3a3a476b7f`, `evidence-official-56e5abfb5f12f1cd3b20`, `evidence-official-bc0327ef2ea6107e1773`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-578439da3f3a3a476b7f, evidence-official-56e5abfb5f12f1cd3b20, evidence-official-bc0327ef2ea6107e1773: Paper: Unifying DNA sequence-to-function model and Discussion; README.md: Model weights and licensing; Supplementary Methods: Model (p.9), ENCODE RNA-seq Data (p.3), Contact maps

#### `catalog-model-boltz-2`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: Boltz-2 predicts biomolecular complex structures and binding affinity.
- Sources: `catalog-source-boltz-2`, `evidence-official-f780521ccebbb0691f9e`, `evidence-official-5a9e55abdf288d9dd8da`, `evidence-official-39a15ed8072aeea14a22`, `evidence-official-734117ed8501eb26fefc`, `evidence-official-7cb8cb7f091536b92c11`, `evidence-official-bd6ec1f819e22f075c32`
- Locator: Reviewed profile summary (2026-09-23): evidence-official-f780521ccebbb0691f9e, evidence-official-5a9e55abdf288d9dd8da, evidence-official-39a15ed8072aeea14a22, evidence-official-734117ed8501eb26fefc, evidence-official-7cb8cb7f091536b92c11, evidence-official-bd6ec1f819e22f075c32: src/boltz/model/models/boltz2.py: Boltz2.__init__, forward, PairformerModule, AtomDiffusion and AffinityModule; docs/prediction.md: affinity outputs; Boltz-2 report Sections 2 Data, 3 Architecture, 4 Training and 6 Limitations

#### `catalog-model-chai-1`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: Chai-1 predicts the structures of biomolecular complexes containing proteins, nucleic acids and small molecules.
- Sources: `catalog-source-chai-1`, `evidence-official-affbe2d511ff2a80f457`, `evidence-official-b91fc1ec601eec6598c3`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-affbe2d511ff2a80f457, evidence-official-b91fc1ec601eec6598c3: Chai-1 Technical Report v1 (9 September 2024), Sections 2.1, 2.7–2.8 and 4.1–4.3; current repository README Licence

#### `catalog-model-diffdock-l`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: DiffDock-L places small-molecule ligands in protein structures using a diffusion docking model.
- Sources: `catalog-source-diffdock-l`, `evidence-official-fa7a6c37148223466dee`, `evidence-official-fffd4026cb8f4018fe2e`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-fa7a6c37148223466dee, evidence-official-fffd4026cb8f4018fe2e: DiffDock-L paper Section 5.1 and Figure 3; official README: February 2024 update and License

#### `catalog-model-dnabert-2`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: DNABERT-2 learns DNA representations that can be adapted to genomic prediction tasks.
- Sources: `catalog-source-dnabert-2`, `evidence-official-7267eabca7c4a7945878`, `evidence-official-2cf0a41fec83ee9c5cc9`, `evidence-official-96b5c3a31a50f7c259d6`, `evidence-official-a48ae27aa000bdab7442`, `evidence-official-3aa749d3205c0a768b22`
- Locator: Reviewed profile summary (2026-09-23): evidence-official-7267eabca7c4a7945878, evidence-official-2cf0a41fec83ee9c5cc9, evidence-official-96b5c3a31a50f7c259d6, evidence-official-a48ae27aa000bdab7442, evidence-official-3aa749d3205c0a768b22: DNABERT-2 paper Sections 3.2, 4.1 and 5.2 (Further Pre-Training); official model card and implementation README; official DNABERT-2-117M checkpoint LICENSE at revision 7bce263b15377fc15361f52cfab88f8b586abda0

#### `catalog-model-esm-2`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: ESM-2 is a family of protein sequence encoders that produce representations for downstream protein analyses.
- Sources: `catalog-source-esm-2`, `evidence-official-29d4b229a3aa426a6dfb`, `evidence-official-d7e5c63feb0e0e627625`, `evidence-official-28fc17fbe0c1d99da219`
- Locator: Reviewed profile summary (2026-09-23): evidence-official-29d4b229a3aa426a6dfb, evidence-official-d7e5c63feb0e0e627625, evidence-official-28fc17fbe0c1d99da219: ESM README: Pre-trained Models and Main models; official facebook/esm2_t33_650M_UR50D README licence metadata and config.json

#### `catalog-model-esmfold`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: ESMFold predicts protein structures directly from amino-acid sequence using ESM-2 representations.
- Sources: `catalog-source-esmfold`, `evidence-official-29d4b229a3aa426a6dfb`, `evidence-official-fa53ab621979fb5f37c8`, `evidence-official-867f2d1dcb4084248daa`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-29d4b229a3aa426a6dfb, evidence-official-fa53ab621979fb5f37c8, evidence-official-867f2d1dcb4084248daa: ESM README: ESMFold Structure Prediction; official facebook/esmfold_v1 model card and config.json esmfold_config

#### `catalog-model-evo-2`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: Evo 2 models and generates DNA over long contexts at single-nucleotide resolution.
- Sources: `catalog-source-evo-2`, `evidence-official-a248990b44d481814f47`, `evidence-official-849b751ed4bf88622749`, `evidence-official-b8df803e8f55324a4eb5`, `evidence-official-8717ffb993cc8f7eddec`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-a248990b44d481814f47, evidence-official-849b751ed4bf88622749, evidence-official-b8df803e8f55324a4eb5, evidence-official-8717ffb993cc8f7eddec: Evo 2 paper: architecture, training, and data, Figure 1 and Discussion; official checkpoints table and evo2_7b licence metadata

#### `catalog-model-gears`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: GEARS predicts transcriptional responses to single- and multi-gene perturbations from single-cell perturbation screens.
- Sources: `catalog-source-gears`, `evidence-official-c037e3419c04936262a0`, `evidence-official-b5e81b2c497214b18f8a`, `evidence-official-f464cd407a6a9d031720`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-c037e3419c04936262a0, evidence-official-b5e81b2c497214b18f8a, evidence-official-f464cd407a6a9d031720: GEARS paper Methods: Overview, Gene coexpression graph encoder, GO graph, Cross-gene effects and gene-specific decoder; gears/model.py: GEARS_Model

#### `catalog-model-geneformer`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: Geneformer represents single-cell transcriptomes as ranked genes and learns contextual gene and cell representations.
- Sources: `catalog-source-geneformer`, `evidence-official-d3d9afa5c6172982ed01`, `evidence-official-f60303c5eaa60ed9c77a`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-d3d9afa5c6172982ed01, evidence-official-f60303c5eaa60ed9c77a: README.md: Model Description, pretrained model list, Application, Installation and licence frontmatter

#### `catalog-model-kraken2`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: Kraken 2 assigns taxonomic labels to sequence reads by consulting a reference-derived minimizer database.
- Sources: `catalog-source-kraken2`, `evidence-official-40f46dc4b9fcc306773b`, `evidence-official-33fe0374c8ebbc2c7294`, `evidence-official-9ba2b6dc494c7b6df951`, `evidence-official-1f756fefa823dd402b0f`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-40f46dc4b9fcc306773b, evidence-official-33fe0374c8ebbc2c7294, evidence-official-9ba2b6dc494c7b6df951, evidence-official-1f756fefa823dd402b0f: docs/MANUAL.markdown: Introduction, Standard Kraken 2 Database, Classification and Confidence scoring

#### `catalog-model-metagene-1`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: METAGENE-1 is an autoregressive DNA/RNA sequence model trained on wastewater metagenomic data.
- Sources: `catalog-source-metagene-1`, `evidence-official-8e894fc6d180746a1808`, `evidence-official-f71e6c488025a4d82997`, `evidence-official-a6b46962aae5cfc348c6`, `evidence-official-b554679ea1503ce3d9f6`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-8e894fc6d180746a1808, evidence-official-f71e6c488025a4d82997, evidence-official-a6b46962aae5cfc348c6, evidence-official-b554679ea1503ce3d9f6: README.md: Model Overview and Usage; config.json; config.json: model_type, hidden_size, num_hidden_layers, num_attention_heads, vocab_size and sequence-length fields; official pretraining train/config_hub/pretrain/genomicsllama.yml: train.max_seq_length

#### `catalog-model-metaphlan`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: MetaPhlAn profiles microbial community composition from shotgun metagenomic reads using clade-specific marker genes.
- Sources: `catalog-source-metaphlan`, `evidence-official-72fdaed158e4ff851fbe`, `evidence-official-37f825d1226e59cbbfbf`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-72fdaed158e4ff851fbe, evidence-official-37f825d1226e59cbbfbf: README.md: description; MetaPhlAn 4 paper: Building the expanded SGB catalog and Discussion

#### `catalog-model-mimic`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: MIMIC represents DNA, RNA, protein and associated molecular measurements in a shared multimodal model.
- Sources: `catalog-source-mimic`, `evidence-official-af8da643e933eae36a68`, `evidence-official-4565e66fdeb787b99afa`, `evidence-official-c14c0e6a0fdbe1479658`, `evidence-official-0ffe1031786a71400ffd`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-af8da643e933eae36a68, evidence-official-4565e66fdeb787b99afa, evidence-official-c14c0e6a0fdbe1479658, evidence-official-0ffe1031786a71400ffd: MIMIC paper Section 3 and Discussion; official model-card Architecture and License; config.json num_input_tokens and num_target_tokens

#### `catalog-model-mrna-fm`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: mRNA-FM encodes coding RNA with codon-level tokens to produce representations for downstream analysis.
- Sources: `catalog-source-mrna-fm`, `evidence-official-fd8e332abdf04a75195b`, `evidence-official-e17e3864c464d981afc7`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-fd8e332abdf04a75195b, evidence-official-e17e3864c464d981afc7: README.md: Foundation Models table and mRNA-FM quick-start example

#### `catalog-model-nt-v2`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: Nucleotide Transformer v2 represents DNA using an encoder pretrained on multiple species.
- Sources: `catalog-source-nt-v2`, `evidence-official-4abb9affb1a9e5438c91`, `evidence-official-6b79ddfdd330693bf4fb`, `evidence-official-18d8f4d5fc3f6616922d`, `evidence-official-657e83427ab59f3aec83`, `evidence-official-56f02d45976d011d80aa`, `evidence-official-4920952f9b3c4b8909a0`, `evidence-official-aadbeb0f10ec55d34f5f`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-4abb9affb1a9e5438c91, evidence-official-6b79ddfdd330693bf4fb, evidence-official-18d8f4d5fc3f6616922d, evidence-official-657e83427ab59f3aec83, evidence-official-56f02d45976d011d80aa, evidence-official-4920952f9b3c4b8909a0, evidence-official-aadbeb0f10ec55d34f5f: README.md: Model Summary, Training data and licence metadata; config.json; Nucleotide Transformer paper Methods: Architecture and Training (v2); source conflict with 50M card retained

#### `catalog-model-pangolin`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: Pangolin predicts splice-site strength and changes caused by genetic variants.
- Sources: `catalog-source-pangolin`, `evidence-official-eaf3efab8850672f44e4`, `evidence-official-de1ee43bdd6f04de9850`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-eaf3efab8850672f44e4, evidence-official-de1ee43bdd6f04de9850: Paper: Deep neural network architecture and Generating training and test sets; README.md: Usage

#### `catalog-model-prokbert`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: ProkBERT is a family of microbial DNA encoders used for sequence representation, promoter prediction and phage identification.
- Sources: `catalog-source-prokbert`, `evidence-official-2efbfaba5a1c09f4f7fa`, `evidence-official-965600234c25fbd104c8`, `evidence-official-ee6e270af125ddf16eb3`, `evidence-official-5e268f31f0347fc5564c`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-2efbfaba5a1c09f4f7fa, evidence-official-965600234c25fbd104c8, evidence-official-ee6e270af125ddf16eb3, evidence-official-5e268f31f0347fc5564c: ProkBERT paper Section 2.1.2 and Table 1; official ProkBERT-mini card: Model Description and licence metadata

#### `catalog-model-proteinmpnn`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: ProteinMPNN designs amino-acid sequences for a supplied protein backbone.
- Sources: `catalog-source-proteinmpnn`, `evidence-official-ea568a52ea3ab476db6a`, `evidence-official-7b6fdf915d9c6950ad0d`, `evidence-official-019aff235ae2c3cf29d6`, `evidence-official-92b0ae57a020cbc40fe7`, `evidence-official-0b8003691827eb09b0a4`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-ea568a52ea3ab476db6a, evidence-official-7b6fdf915d9c6950ad0d, evidence-official-019aff235ae2c3cf29d6, evidence-official-92b0ae57a020cbc40fe7, evidence-official-0b8003691827eb09b0a4: ProteinMPNN paper: main-text model development; training/README.md: multi-chain training set, list.csv and cluster manifests; protein_mpnn_utils.py: ProteinMPNN; Supplementary Materials: Methods for training multi-chain models / Training data

#### `catalog-model-rhofold`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: RhoFold+ predicts RNA three-dimensional structures from RNA sequence with alignment information.
- Sources: `catalog-source-rhofold`, `evidence-official-955922130ff85a74fa18`, `evidence-official-8b4e1bd487c21cda9862`, `evidence-official-3e1890c3652bc5c150f7`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-955922130ff85a74fa18, evidence-official-8b4e1bd487c21cda9862, evidence-official-3e1890c3652bc5c150f7: Paper: Automated end-to-end platform, Large-scale pretraining dataset, Efficient development of a self-distillation dataset, Feature processing with Rhoformer and Data availability; README.md: Usage; official cuhkaih/rhofold card licence metadata

#### `catalog-model-rna-fm`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: RNA-FM learns contextual representations of RNA nucleotides for downstream RNA analyses.
- Sources: `catalog-source-rna-fm`, `evidence-final-model-rna-fm-paper`, `evidence-official-fd8e332abdf04a75195b`, `evidence-official-e17e3864c464d981afc7`
- Locator: Reviewed profile summary (2026-09-23): evidence-official-fd8e332abdf04a75195b, evidence-official-e17e3864c464d981afc7: README.md: Quick Start, embedding examples and RNA foundation model comparison table

#### `catalog-model-scfoundation`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: scFoundation produces contextual cell and gene representations from gene-expression measurements.
- Sources: `catalog-source-scfoundation`, `evidence-official-bfbc8babf3630ddb3ed7`, `evidence-official-7972ce2bdd6a5e40d8ad`, `evidence-official-9863509ad10b824dc96b`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-bfbc8babf3630ddb3ed7, evidence-official-7972ce2bdd6a5e40d8ad, evidence-official-9863509ad10b824dc96b: June 15 2023 scFoundation manuscript: Results pre-training framework; Methods Data collection, Embedding, Encoder, Decoder and Read-depth-aware pre-training; official model README

#### `catalog-model-scgpt`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: scGPT learns representations of single-cell molecular measurements and supports task-specific adaptation.
- Sources: `catalog-source-scgpt`, `evidence-official-0e4dac85aa0e0ff1d4b2`, `evidence-official-d8e2d4f2e752370b6565`, `evidence-official-efa6ec9d886a21534a20`
- Locator: Reviewed profile summary (2026-09-23): evidence-official-0e4dac85aa0e0ff1d4b2, evidence-official-d8e2d4f2e752370b6565, evidence-official-efa6ec9d886a21534a20: May 2023 scGPT preprint Sections 4.1–4.3 and 4.8; current scgpt/model/model.py and README pretrained model table; README.md: Pretrained scGPT Model Zoo, whole-human row

#### `catalog-model-scvi`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: scVI models single-cell RNA counts with a probabilistic latent-variable model that accounts for observed covariates.
- Sources: `catalog-source-scvi`, `evidence-official-550f6719c2f22f4d57b3`, `evidence-official-0cbab80c2d1769287a1f`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-550f6719c2f22f4d57b3, evidence-official-0cbab80c2d1769287a1f: docs/user_guide/models/scvi.md: Preliminaries, Generative process, Inference and Limitations

#### `catalog-model-spliceai`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: SpliceAI annotates sequence variants with predicted splice acceptor and donor changes.
- Sources: `catalog-source-spliceai`, `evidence-official-864a2c5ea6e61aa310f9`, `evidence-official-ded281404bd1a0f3fdb7`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-864a2c5ea6e61aa310f9, evidence-official-ded281404bd1a0f3fdb7: Jaganathan et al., Cell 2019, STAR Methods: SpliceAI architecture and Model training and testing (pp. e2–e3); README.md: usage and License

#### `catalog-model-vina`

- Old: Existing candidate catalogue entry; exact checkpoint and metadata require primary-source review.
- New: AutoDock Vina searches for ligand conformations and poses in a molecular docking problem.
- Sources: `catalog-source-vina`, `evidence-official-23e72f7e93a0a633ab2b`
- Locator: Reviewed profile summary (2026-09-16): evidence-official-23e72f7e93a0a633ab2b: README.md: introduction, feature list, license and Citations

### Language models

#### `tgtval-20261009-model-claude-3-5-sonnet`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Large multimodal model from Anthropic, an evolution of the Claude 3 family with improved coding and visual processing.
- Sources: `tgtval-20261009-source-roohani2025`, `qa-descriptions-20261011-b-source-claude3`
- Locator: qa-descriptions-20261011-b-source-claude3: Claude 3.5 Sonnet Model Card Addendum, section 1 Introduction ('Claude 3.5 Sonnet offers improved capabilities, including better coding and visual processing. Since it is an evolution of the Claude 3 model family')

#### `tgtval-20261009-model-claude-3-haiku`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Large multimodal model with vision capabilities, the fastest and least expensive of Anthropic's Claude 3 family.
- Sources: `tgtval-20261009-source-roohani2025`, `qa-descriptions-20261011-b-source-claude3`
- Locator: qa-descriptions-20261011-b-source-claude3: model card abstract, p.1 ('Claude 3 Haiku, our fastest and least expensive model')

#### `tgtval-20261009-model-claude-3-opus`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Large multimodal model with vision capabilities, the most capable of Anthropic's Claude 3 family.
- Sources: `tgtval-20261009-source-roohani2025`, `qa-descriptions-20261011-b-source-claude3`
- Locator: qa-descriptions-20261011-b-source-claude3: model card abstract, p.1 ('Claude 3 Opus, our most capable offering'; 'All new models have vision capabilities')

#### `tgtval-20261009-model-claude-3-sonnet`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Large multimodal model with vision capabilities in Anthropic's Claude 3 family, positioned between Opus and Haiku in skills and speed.
- Sources: `tgtval-20261009-source-roohani2025`, `qa-descriptions-20261011-b-source-claude3`
- Locator: qa-descriptions-20261011-b-source-claude3: model card abstract, p.1 ('Claude 3 Sonnet, which provides a combination of skills and speed')

#### `tgtval-20261009-model-gpt-4o`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Autoregressive omni model from OpenAI, trained end to end across text, vision and audio, that accepts text, audio, image and video input and generates text, audio and image output.
- Sources: `tgtval-20261009-source-roohani2025`, `qa-descriptions-20261011-b-source-gpt-4o`
- Locator: qa-descriptions-20261011-b-source-gpt-4o: abstract

#### `tgtval-20261009-model-gpt-oss-120b`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Open-weight reasoning model from OpenAI with a mixture-of-experts Transformer architecture, trained by large-scale distillation and reinforcement learning.
- Sources: `tgtval-20261009-source-debrouwer2026`, `qa-descriptions-20261011-b-source-gpt-oss`
- Locator: qa-descriptions-20261011-b-source-gpt-oss: abstract

#### `tgtval-20261009-model-llama-3-1-8b`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Language model in Meta's Llama 3 herd, which natively supports multilinguality, coding, reasoning and tool use.
- Sources: `tgtval-20261009-source-gupta2025`, `qa-descriptions-20261011-b-source-llama3`
- Locator: qa-descriptions-20261011-b-source-llama3: abstract ('a herd of language models that natively support multilinguality, coding, reasoning, and tool usage')

#### `tgtval-20261009-model-o1-mini`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Model in OpenAI's o1 series, trained with large-scale reinforcement learning to reason using a chain of thought before answering.
- Sources: `tgtval-20261009-source-roohani2025`, `qa-descriptions-20261011-b-source-o1`
- Locator: qa-descriptions-20261011-b-source-o1: abstract ('The o1 model series is trained with large-scale reinforcement learning to reason using chain of thought')

#### `tgtval-20261009-model-o1-preview`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Model in OpenAI's o1 series, trained with large-scale reinforcement learning to reason using a chain of thought before answering.
- Sources: `tgtval-20261009-source-roohani2025`, `qa-descriptions-20261011-b-source-o1`
- Locator: qa-descriptions-20261011-b-source-o1: abstract ('The o1 model series is trained with large-scale reinforcement learning to reason using chain of thought')

#### `tgtval-20261009-model-qwen-2-7b`

- Old: Language model identity as reported in this source. Unspecified versions are not assumed equal to other papers.
- New: Language model in the Qwen2 series, a suite of foundational and instruction-tuned language models from 0.5 to 72 billion parameters.
- Sources: `tgtval-20261009-source-gupta2025`, `qa-descriptions-20261011-b-source-qwen2`
- Locator: qa-descriptions-20261011-b-source-qwen2: abstract

### scFoundation Table 4 pipelines

#### `scfoundation-2024-supp-table4-method-actinn`

- Old: ACTINN cell-type annotation pipeline reported in the primary table; fitting/configuration details unextracted.
- New: Cell-type classifier for single-cell RNA-seq that trains a neural network with three hidden layers on datasets with predefined cell types and predicts cell types in other datasets.
- Sources: `coverage-source-scfoundation-supp`, `qa-descriptions-20261011-b-source-actinn`
- Locator: qa-descriptions-20261011-b-source-actinn: abstractText; coverage-source-scfoundation-supp: Supplementary Table 4 (cell type annotation on Zheng68K and Segerstolpe)

#### `scfoundation-2024-supp-table4-method-celltypist`

- Old: CellTypist cell-type annotation pipeline reported in the primary table; fitting/configuration details unextracted.
- New: Machine-learning tool for rapid cell-type annotation of single-cell RNA-seq data.
- Sources: `coverage-source-scfoundation-supp`, `qa-descriptions-20261011-b-source-celltypist`
- Locator: qa-descriptions-20261011-b-source-celltypist: abstractText ('CellTypist, a machine learning tool for rapid and precise cell type annotation'); coverage-source-scfoundation-supp: Supplementary Table 4

#### `scfoundation-2024-supp-table4-method-scanpy`

- Old: Scanpy cell-type annotation pipeline reported in the primary table; fitting/configuration details unextracted.
- New: Python toolkit for single-cell gene expression analysis, with methods for preprocessing, visualisation, clustering, trajectory inference and differential expression testing.
- Sources: `coverage-source-scfoundation-supp`, `qa-descriptions-20261011-b-source-scanpy`
- Locator: qa-descriptions-20261011-b-source-scanpy: abstractText; coverage-source-scfoundation-supp: Supplementary Table 4

#### `scfoundation-2024-supp-table4-method-scanvi`

- Old: scANVI cell-type annotation pipeline reported in the primary table; fitting/configuration details unextracted.
- New: Semi-supervised variant of scVI, a deep generative model of single-cell transcriptomics, that uses existing cell-state annotations to label cells in new datasets.
- Sources: `coverage-source-scfoundation-supp`, `qa-descriptions-20261011-b-source-scanvi`
- Locator: qa-descriptions-20261011-b-source-scanvi: abstractText ('scANVI, a semi-supervised variant of scVI designed to leverage existing cell state annotations'); coverage-source-scfoundation-supp: Supplementary Table 4

#### `scfoundation-2024-supp-table4-method-scbert`

- Old: scBERT cell-type annotation pipeline reported in the primary table; fitting/configuration details unextracted.
- New: Transformer model, pretrained on unlabelled single-cell RNA-seq data in the manner of BERT, that is fine-tuned to annotate cell types.
- Sources: `coverage-source-scfoundation-supp`, `qa-descriptions-20261011-b-source-scbert`
- Locator: qa-descriptions-20261011-b-source-scbert: abstractText; coverage-source-scfoundation-supp: Supplementary Table 4

#### `scfoundation-2024-supp-table4-method-scfoundation`

- Old: scFoundation cell-type annotation pipeline reported in the primary table; fitting/configuration details unextracted.
- New: Cell-type annotation with scFoundation, a model that produces contextual cell and gene representations from gene-expression measurements.
- Sources: `coverage-source-scfoundation-supp`, `evidence-official-9863509ad10b824dc96b`
- Locator: catalog-model-scfoundation profile summary (evidence-official-9863509ad10b824dc96b: Results pre-training framework; Methods Embedding, Encoder, Decoder); coverage-source-scfoundation-supp: Supplementary Table 4

#### `scfoundation-2024-supp-table4-method-singlecellnet`

- Old: SingleCellNet cell-type annotation pipeline reported in the primary table; fitting/configuration details unextracted.
- New: Tool that classifies query single-cell RNA-seq data by comparison with reference single-cell RNA-seq data, across platforms and species.
- Sources: `coverage-source-scfoundation-supp`, `qa-descriptions-20261011-b-source-singlecellnet`
- Locator: qa-descriptions-20261011-b-source-singlecellnet: title and abstractText; coverage-source-scfoundation-supp: Supplementary Table 4

### FoldBench models

#### `ucc-research-model-helixfold3`

- Old: All-atom structure model represented by its exact FoldBench configuration.
- New: Open-source reproduction of AlphaFold 3 that predicts the all-atom structures of biomolecular complexes.
- Sources: `ucc-research-source-foldbench-paper`, `ucc-research-source-foldbench-supp`
- Locator: ucc-research-source-foldbench-paper: Introduction ('the training code and datasets of AlphaFold 3 are not publicly available ... several open-source reproductions such as Boltz-1, Protenix, Chai-1 and HelixFold 3 have emerged'; 'five recent all-atom predictors')

#### `ucc-research-model-protenix`

- Old: All-atom structure model represented by its exact FoldBench configuration.
- New: Open-source reproduction of AlphaFold 3 that predicts the all-atom structures of biomolecular complexes.
- Sources: `ucc-research-source-foldbench-paper`, `ucc-research-source-foldbench-supp`
- Locator: ucc-research-source-foldbench-paper: Introduction (as for HelixFold 3)

### TAPE records

#### `discovery-model-tape-bepler`

- Old: Method identity as printed in the historical TAPE leaderboard.
- New: Protein language model of Bepler et al. as benchmarked in TAPE: a two-layer bidirectional language model followed by three bidirectional LSTMs with 512 hidden units, trained by next-token prediction.
- Sources: `src-discovery-songlab-cal-tape`, `evidence-official-028db5eeb224def23456`, `evidence-official-1aae5efd1b27ae9c761a`, `evidence-official-3cec54ed6ded9cb0a092`, `evidence-official-044ad0df4e4fe48a2125`, `evidence-official-12d43bf3076a93fc4ee7`, `evidence-official-c303652f3d79132a00c2`, `evidence-official-116dfd8f61e04b51c148`, `evidence-official-362b9cef071111dfe343`, `evidence-expansion-evidence-discovery-final-tape-6ee0c3e6`
- Locator: evidence-expansion-evidence-discovery-final-tape-6ee0c3e6: Models and Experimental Setup, Architectures and Training

#### `discovery-model-tape-lstm`

- Old: Method identity as printed in the historical TAPE leaderboard.
- New: Protein language model in the TAPE benchmark: two three-layer LSTMs with 1,024 hidden units for the forward and backward directions, pretrained by next-token prediction.
- Sources: `src-discovery-songlab-cal-tape`, `evidence-official-028db5eeb224def23456`, `evidence-official-1aae5efd1b27ae9c761a`, `evidence-official-3cec54ed6ded9cb0a092`, `evidence-official-044ad0df4e4fe48a2125`, `evidence-official-12d43bf3076a93fc4ee7`, `evidence-official-c303652f3d79132a00c2`, `evidence-official-362b9cef071111dfe343`, `evidence-expansion-evidence-discovery-final-tape-6ee0c3e6`
- Locator: evidence-expansion-evidence-discovery-final-tape-6ee0c3e6: Models and Experimental Setup, Architectures and Training

#### `discovery-model-tape-one-hot`

- Old: Method identity as printed in the historical TAPE leaderboard.
- New: Baseline featurisation in the TAPE benchmark that encodes the protein's amino-acid sequence one-hot, with no learned representation.
- Sources: `src-discovery-songlab-cal-tape`, `evidence-official-028db5eeb224def23456`, `evidence-official-1aae5efd1b27ae9c761a`, `evidence-official-3cec54ed6ded9cb0a092`, `evidence-official-044ad0df4e4fe48a2125`, `evidence-official-12d43bf3076a93fc4ee7`, `evidence-official-c303652f3d79132a00c2`, `evidence-official-362b9cef071111dfe343`, `evidence-expansion-evidence-discovery-final-tape-6ee0c3e6`
- Locator: evidence-expansion-evidence-discovery-final-tape-6ee0c3e6: Models and Experimental Setup, Baselines ('a one-hot encoding of the input amino acid sequence, which provides a simple baseline')

#### `discovery-model-tape-resnet`

- Old: Method identity as printed in the historical TAPE leaderboard.
- New: Protein language model in the TAPE benchmark: a dilated residual network of 35 blocks, each with two convolutional layers of 256 filters, kernel size 9 and dilation rate 2, pretrained by masked-token prediction.
- Sources: `src-discovery-songlab-cal-tape`, `evidence-official-028db5eeb224def23456`, `evidence-official-1aae5efd1b27ae9c761a`, `evidence-official-3cec54ed6ded9cb0a092`, `evidence-official-044ad0df4e4fe48a2125`, `evidence-official-12d43bf3076a93fc4ee7`, `evidence-official-c303652f3d79132a00c2`, `evidence-official-362b9cef071111dfe343`, `evidence-expansion-evidence-discovery-final-tape-6ee0c3e6`
- Locator: evidence-expansion-evidence-discovery-final-tape-6ee0c3e6: Models and Experimental Setup, Architectures and Training

#### `discovery-model-tape-transformer`

- Old: Method identity as printed in the historical TAPE leaderboard.
- New: Protein language model in the TAPE benchmark: a 12-layer Transformer with 512 hidden units and 8 attention heads (about 38 million parameters), pretrained by masked-token prediction.
- Sources: `src-discovery-songlab-cal-tape`, `evidence-official-028db5eeb224def23456`, `evidence-official-1aae5efd1b27ae9c761a`, `evidence-official-3cec54ed6ded9cb0a092`, `evidence-official-044ad0df4e4fe48a2125`, `evidence-official-12d43bf3076a93fc4ee7`, `evidence-official-c303652f3d79132a00c2`, `evidence-official-362b9cef071111dfe343`, `evidence-expansion-evidence-discovery-final-tape-6ee0c3e6`
- Locator: evidence-expansion-evidence-discovery-final-tape-6ee0c3e6: Models and Experimental Setup, Architectures and Training

#### `discovery-model-tape-unirep`

- Old: Method identity as printed in the historical TAPE leaderboard.
- New: Protein language model of Alley et al. (UniRep) as benchmarked in TAPE: a unidirectional multiplicative LSTM with 1,900 hidden units, trained by next-token prediction.
- Sources: `src-discovery-songlab-cal-tape`, `evidence-official-028db5eeb224def23456`, `evidence-official-1aae5efd1b27ae9c761a`, `evidence-official-3cec54ed6ded9cb0a092`, `evidence-official-044ad0df4e4fe48a2125`, `evidence-official-12d43bf3076a93fc4ee7`, `evidence-official-c303652f3d79132a00c2`, `evidence-official-362b9cef071111dfe343`, `evidence-expansion-evidence-discovery-final-tape-6ee0c3e6`
- Locator: evidence-expansion-evidence-discovery-final-tape-6ee0c3e6: Models and Experimental Setup, Architectures and Training


## For the reviewer

- o1-preview and o1-mini get the same sentence: the o1 System Card abstract describes the series, not each model separately.
- The scFoundation pipeline says only that scFoundation is used for cell-type annotation. The published paper's methods, which would say how its embeddings were classified, are not open access, and the pinned preprint predates the annotation experiments (gaps.md).
- The Scanpy pipeline describes the toolkit. Which Scanpy procedure produced the Table 4 annotation is not stated in the pinned sources (gaps.md).
- HelixFold 3 and Protenix share one sentence. FoldBench, their only pinned source, describes them together.
- Then set the 63 batch records to `source_checked` with a review block, or correct them in `build.py` and rerun it.

## Integration, after review

Add the batch first, because the edited records cite the new sources:

```
npm run records -- add data/omics/qa-descriptions-20261011-b/batch.jsonl data/omics/qa-descriptions-20261011-b
npm run records -- change data/omics/qa-descriptions-20261011-b/review.md data/omics/qa-descriptions-20261011-b <the 51 record IDs>
```

The 51 IDs are the `subject` links of the claims in `batch.jsonl`.
