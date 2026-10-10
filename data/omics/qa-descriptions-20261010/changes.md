# Issue #88a: functional descriptions, 2026-10-10

Scope: the 44 model records whose description began "Named prediction model family identified in the cited primary source" and the 11 pipeline records whose description contained "not a new execution".

Changed: 54 records (models.jsonl and pipelines.jsonl, edited in place: `description`, `source_ids`, and for pipelines `attributes.source_locator`). Unchanged: 1. New sources: 40. Correction claims: 54. All new records are in `batch.jsonl`.

Reviewer corrections, 2026-10-10: 11 descriptions were corrected, the README and mRNABench sources were replaced by the existing store records `run-doc-proteingym-readme-md-144fe22b` and `expansion-p3-mrnabench-2025`, and every record in `batch.jsonl` is now `source_checked`. See `review.md`; the entries below show the corrected text.

Not done here: `records -- change` (the provenance hashes of the 54 edited records are stale until it is run) and `records -- add` for `batch.jsonl`. In a scratch copy of the store, adding `batch.jsonl` and then recording the 54 changes passed validation and `records check`.

Provenance handling: neither `model_identity_note` nor `scope_note` is declared for model or pipeline records. The pipelines' old text ('Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution') was appended to `attributes.source_locator`. The models' old text was generic and named no source, so nothing was moved; each correction claim keeps it as `previous_value`.

Every description was written from the source text listed for it: the record's existing source re-fetched and matched to its pinned SHA-256 (MIMIC HTML, MSAlign PDF, FramePool XML, Jores PDF, RhoMax XML), the ProteinGym README at the pinned commit, or the original model paper's abstract (Europe PMC core record or arXiv API entry), pinned as a new source. VESPAl and the S2F/S3F-MSA variants use full text (VESPA PMC8716573; S3F arXiv HTML).

## Unchanged

| Record | Reason |
| --- | --- |
| `mimic-2026-mrnabench-method-dilated-resnet` | No retrieved source describes it: MIMIC cites only mRNABench for this row, and the mRNABench abstract does not describe the Dilated ResNet baseline; the mRNABench full text is not available through Europe PMC. |

Reviewer note: the mRNABench full text is available. The store already pins it as `expansion-p3-mrnabench-2025` (Europe PMC PMC12265608, CC BY 4.0), and its baselines section describes the supervised Dilated ResNet. See `review.md`.

## Changed records

### `mimic-2026-mrnabench-method-aido-rna` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from AIDO.RNA, an RNA foundation model pretrained on 42 million non-coding RNA sequences at single-nucleotide resolution, with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-aido-rna` (https://doi.org/10.1101/2024.11.28.625345)
- Correction claim: `metadata-correction-bdafb91cb6941c564b19`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `mimic-2026-mrnabench-method-dnabert-s` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from DNABERT-S, a genome model built on DNABERT-2 and trained with contrastive objectives to give species-aware DNA embeddings, with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-dnabert-s` (https://doi.org/10.1093/bioinformatics/btaf188)
- Correction claim: `metadata-correction-fc12c1a3ce9302723533`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `mimic-2026-mrnabench-method-dnabert2` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from DNABERT-2, a genome foundation model that tokenises DNA with byte pair encoding instead of k-mers, with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-dnabert2` (https://arxiv.org/abs/2306.15006v2)
- Correction claim: `metadata-correction-b13d281dd497e8554c37`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `mimic-2026-mrnabench-method-ernie-rna` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from ERNIE-RNA, an RNA language model based on a modified BERT with a base-pairing restriction, with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-ernie-rna` (https://doi.org/10.1038/s41467-025-64972-0)
- Correction claim: `metadata-correction-c4a6639a15b0138c2bb7`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `mimic-2026-mrnabench-method-evo2` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from Evo 2, a DNA foundation model trained on 9.3 trillion base pairs from all domains of life with a context of up to 1 million nucleotides, with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-evo2` (https://doi.org/10.1101/2025.02.18.638918)
- Correction claim: `metadata-correction-b3e37a3de3e9650701cb`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `mimic-2026-mrnabench-method-hyenadna` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from HyenaDNA, a genomic foundation model built on Hyena implicit convolutions and pretrained on the human reference genome with single-nucleotide tokens and contexts of up to 1 million tokens, with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-hyenadna` (https://arxiv.org/abs/2306.15794v2)
- Correction claim: `metadata-correction-8ef00afda16c979fc554`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `mimic-2026-mrnabench-method-nt-v2` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from a Nucleotide Transformer model reported as NT-v2, from a family of transformer DNA foundation models (50 million to 2.5 billion parameters, integrating information from 3,202 human genomes and 850 genomes of other species), with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-nt-v2` (https://doi.org/10.1038/s41592-024-02523-z)
- Correction claim: `metadata-correction-f089d399899322c2b49d`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `mimic-2026-mrnabench-method-orthrus` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from Orthrus, a Mamba-based mature RNA foundation model pretrained with a contrastive objective over splice isoforms and orthologous transcripts, with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-orthrus` (https://doi.org/10.1038/s41592-026-03064-3)
- Correction claim: `metadata-correction-537009fffad931e39f1d`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `mimic-2026-mrnabench-method-rinalmo` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from RiNALMo, an RNA language model pretrained on 36 million non-coding RNA sequences, with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-rinalmo` (https://doi.org/10.1038/s41467-025-60872-5)
- Correction claim: `metadata-correction-3935e0ad3b37f81f3821`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `mimic-2026-mrnabench-method-splicebert` (pipeline)

- Old: Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution.
- New: mRNABench evaluation of mature mRNA embeddings from SpliceBERT, a language model pretrained by masked language modelling on primary RNA sequences from 72 vertebrates, with task scores quoted from prior work in MIMIC Table S11.
- Sources: `coverage-source-mimic-2026-v1-html`; `expansion-p3-mrnabench-2025` (https://pmc.ncbi.nlm.nih.gov/articles/PMC12265608/); `qa-descriptions-20261010-source-splicebert` (https://doi.org/10.1093/bib/bbae163)
- Correction claim: `metadata-correction-51bc8bd036adadd6a826`
- Moved to `attributes.source_locator`: "Prior mRNABench evaluated pipeline, quoted in MIMIC Table S11; not a new execution"

### `uc20260930-model-aido-protein-rag` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Retrieval-augmented protein language model from the AIDO.Protein-RAG work, which combines a pretrained protein language model with retrieved multiple sequence alignments; ProteinGym lists AIDO with alignment and structure inputs and scores it as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-aido-protein-rag` (https://doi.org/10.1101/2024.12.02.626519)
- Correction claim: `metadata-correction-a4c117065febb0fe8997`

### `uc20260930-model-carp` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Convolutional protein language model pretrained by masked language modelling on protein sequences, scored in ProteinGym as a zero-shot single-sequence substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-carp` (https://doi.org/10.1016/j.cels.2024.01.008)
- Correction claim: `metadata-correction-6c29cd67ac588974bbf0`

### `uc20260930-model-deepsequence` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Latent-variable deep generative model of a protein family's sequences, learned without labels from evolutionary sequence data, that predicts mutation effects; ProteinGym scores it as a zero-shot baseline from a multiple sequence alignment.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-deepsequence` (https://doi.org/10.1038/s41592-018-0138-4)
- Correction claim: `metadata-correction-1c47d5f0a442b49be205`

### `uc20260930-model-emb-cos` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Contrastive model that learns a shared embedding space for molecules and MS/MS spectra with candidate InfoNCE to retrieve a metabolite's structure from its spectrum among candidate molecules, without pretrained encoders or score fusion.
- Sources: `uc20260930-source-msalign-v2`
- Correction claim: `metadata-correction-23c20679e089d2f790ed`

### `uc20260930-model-escott` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Missense effect predictor that ProteinGym lists with multiple sequence alignment and structure inputs under the PRESCOTT reference, which describes an epistatic and structural model of missense effects that also uses population allele frequencies; scored as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-escott` (https://doi.org/10.1101/2024.02.03.24302219)
- Correction claim: `metadata-correction-a280a8ff576340bee112`

### `uc20260930-model-esm-1b` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Deep contextual protein language model trained without labels on 250 million protein sequences, whose learned representations support mutational-effect prediction; ProteinGym scores it as a zero-shot single-sequence substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-esm-1b` (https://doi.org/10.1073/pnas.2016239118)
- Correction claim: `metadata-correction-1deba6d03b0b6339f801`

### `uc20260930-model-eve` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Deep generative model of sequence variation across organisms that predicts the effects and pathogenicity of protein variants without labels; ProteinGym scores it as a zero-shot alignment-based substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-eve` (https://doi.org/10.1038/s41586-021-04043-8)
- Correction claim: `metadata-correction-faf45d7de1dfad0cadaa`

### `uc20260930-model-flare` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Contrastive spectrum-to-molecule retrieval model that follows MVP with a stronger spectra encoder using subformula peak annotation and a richer similarity; it needs the target's molecular formula.
- Sources: `uc20260930-source-msalign-v2`
- Correction claim: `metadata-correction-1f15046079bf4a4f2e91`

### `uc20260930-model-framepool` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Neural network with frame pooling that predicts mean ribosome load, a proxy for translation efficiency, from 5' UTR sequences of any length.
- Sources: `uc20260930-source-framepool-2021`
- Correction claim: `metadata-correction-b949cf76a35b544309d0`

### `uc20260930-model-jestr` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Contrastive model that matches MS/MS spectra to candidate molecules for metabolite retrieval, pretrained with batch InfoNCE and fine-tuned with candidate InfoNCE.
- Sources: `uc20260930-source-msalign-v2`
- Correction claim: `metadata-correction-21828ff913eebfab5ff8`

### `uc20260930-model-jores-plant-promoter-cnn` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Convolutional neural network that predicts plant core promoter strength, measured by STARR-seq in tobacco leaves or maize protoplasts, directly from promoter sequence.
- Sources: `uc20260930-source-jores-2021`
- Correction claim: `metadata-correction-b5ebf8f4b338c3ca8f55`

### `uc20260930-model-massspecgym-deepsets-fingerprint-predictor` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: DeepSets fingerprint prediction baseline from MassSpecGym that predicts a molecular fingerprint from an MS/MS spectrum to rank candidate molecules (Fourier-feature variant in MSAlign).
- Sources: `uc20260930-source-msalign-v2`
- Correction claim: `metadata-correction-b0e6889e1dcfa527b0bd`

### `uc20260930-model-mif` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Masked inverse folding model, a structured graph neural network that reconstructs corrupted protein sequences conditioned on the backbone structure, scored in ProteinGym as a zero-shot structure-based substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-mif` (https://doi.org/10.1093/protein/gzad015)
- Correction claim: `metadata-correction-8ec3da6d5ad0d57d0eb5`

### `uc20260930-model-mif-st` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Masked inverse folding model with sequence transfer, which feeds the outputs of a pretrained sequence-only protein masked language model into a structure-conditioned graph neural network, scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `qa-descriptions-20261010-source-mif` (https://doi.org/10.1093/protein/gzad015)
- Correction claim: `metadata-correction-70b29a27bb77d7237765`

### `uc20260930-model-mist` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Spectrum-to-molecule retrieval model that pretrains on fingerprint prediction, fine-tunes with contrastive learning and augments its data with a forward model that simulates spectra; it needs the target's molecular formula.
- Sources: `uc20260930-source-msalign-v2`
- Correction claim: `metadata-correction-84a0757aba386bf79aaf`

### `uc20260930-model-msa-transformer` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Protein language model that takes a multiple sequence alignment as input, interleaving row and column attention, trained by masked language modelling across many protein families; ProteinGym scores it as a zero-shot alignment-based substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-msa-transformer` (https://doi.org/10.1101/2021.02.12.430858)
- Correction claim: `metadata-correction-9abc27593c299dc510f5`

### `uc20260930-model-mulan` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Multimodal protein language model that fuses a pretrained sequence encoder with a parameter-efficient adapter for angle-based structure encoding, scored in ProteinGym as a zero-shot substitution baseline from sequence and structure.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-mulan` (https://doi.org/10.1093/bioadv/vbaf117)
- Correction claim: `metadata-correction-d4e06f404463d43d21ea`

### `uc20260930-model-mvp` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Contrastive spectrum-to-molecule retrieval model that extends JESTR with multiple views (fingerprint, graph, spectra and consensus spectra); it needs the target's molecular formula.
- Sources: `uc20260930-source-msalign-v2`
- Correction claim: `metadata-correction-afae73ae45bdc4a0829b`

### `uc20260930-model-optimus-5-prime` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Convolutional neural network that predicts mean ribosome load from 5' UTR sequence, trained on massively parallel reporter assays of random 5' UTRs and limited by position-specific weights to the lengths seen in training.
- Sources: `uc20260930-source-framepool-2021`
- Correction claim: `metadata-correction-01bf5de6ca7da933d8a8`

### `uc20260930-model-poet` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Autoregressive transformer that models whole protein families as sequences of sequences and scores or generates variants conditioned on homologous sequences, scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-poet` (https://arxiv.org/abs/2306.06156v3)
- Correction claim: `metadata-correction-52f32d842c008a716878`

### `uc20260930-model-progen2` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Suite of protein language models of up to 6.4 billion parameters trained on sequence datasets drawn from over a billion proteins, which generate sequences and predict fitness without fine-tuning; ProteinGym scores it as a zero-shot single-sequence substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-progen2` (https://doi.org/10.1016/j.cels.2023.10.002)
- Correction claim: `metadata-correction-d07cca550523d5ebb924`

### `uc20260930-model-progen3` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Family of sparse generative protein language models of up to 46 billion parameters pretrained on 1.5 trillion amino-acid tokens for sequence generation and fitness prediction, scored in ProteinGym as a zero-shot single-sequence substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-progen3` (https://doi.org/10.1101/2025.04.15.649055)
- Correction claim: `metadata-correction-b92380ac01f7c7747038`

### `uc20260930-model-prosst` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Transformer protein language model that combines the residue sequence with quantized structure tokens through disentangled attention, pretrained by masked language modelling, scored in ProteinGym as a zero-shot substitution baseline from sequence and structure.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-prosst` (https://doi.org/10.1101/2024.04.15.589672)
- Correction claim: `metadata-correction-60b514e1f652a5203a27`

### `uc20260930-model-protgpt2` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Deep unsupervised language model trained on protein sequences that generates de novo protein sequences, scored in ProteinGym as a zero-shot single-sequence substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-protgpt2` (https://doi.org/10.1038/s41467-022-32007-7)
- Correction claim: `metadata-correction-46d0b40f1618a5ccbf55`

### `uc20260930-model-protriever` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: End-to-end differentiable framework that learns to retrieve homologous protein sequences by vector search while training for fitness prediction, scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `qa-descriptions-20261010-source-protriever` (https://arxiv.org/abs/2506.08954v1)
- Correction claim: `metadata-correction-67d00ce30aa9b3f1f8e5`

### `uc20260930-model-protssn` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Pre-trained model that combines sequential and geometric encoders of protein primary and tertiary structure to score variant effects zero-shot, a ProteinGym substitution baseline from sequence and structure.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-protssn` (https://doi.org/10.7554/elife.98033)
- Correction claim: `metadata-correction-9f6b5341efae933c1478`

### `uc20260930-model-rhomax` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Graph neural network that predicts the maximum absorption wavelength of a microbial rhodopsin from its AlphaFold2-predicted 3D structure.
- Sources: `uc20260930-source-rhomax-2024`
- Correction claim: `metadata-correction-772cbc718fc144ee85b5`

### `uc20260930-model-rita` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Suite of autoregressive generative transformer models for protein sequences, up to 1.2 billion parameters trained on UniRef-100, scored in ProteinGym as a zero-shot single-sequence substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-rita` (https://arxiv.org/abs/2205.05789v2)
- Correction claim: `metadata-correction-47136ee23f5fe22dab2f`

### `uc20260930-model-s2f` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Sequence-Structure Fitness model that feeds ESM-2-650M outputs as node features to a Geometric Vector Perceptron structure encoder to predict protein fitness zero-shot, scored in ProteinGym as a substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `qa-descriptions-20261010-source-s3f-html` (https://arxiv.org/abs/2412.01108v1)
- Correction claim: `metadata-correction-6e2dc9192e4487ea185b`

### `uc20260930-model-s2f-msa` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Ensemble of the Sequence-Structure Fitness model (S2F) with EVE alignment-based predictions by summing their z-scores, scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `qa-descriptions-20261010-source-s3f-html` (https://arxiv.org/abs/2412.01108v1)
- Correction claim: `metadata-correction-fd745ded82f174135851`

### `uc20260930-model-s3f` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Sequence-Structure-Surface Fitness model that combines protein language model sequence representations with Geometric Vector Perceptron encoders of the backbone and surface to predict protein fitness zero-shot, scored in ProteinGym as a substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-s3f` (https://arxiv.org/abs/2412.01108v1); `qa-descriptions-20261010-source-s3f-html` (https://arxiv.org/abs/2412.01108v1)
- Correction claim: `metadata-correction-7b52813f1b702eada378`

### `uc20260930-model-s3f-msa` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Ensemble of the Sequence-Structure-Surface Fitness model (S3F) with EVE alignment-based predictions by summing their z-scores, scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `qa-descriptions-20261010-source-s3f-html` (https://arxiv.org/abs/2412.01108v1)
- Correction claim: `metadata-correction-102402a7e64e766758e1`

### `uc20260930-model-saprot` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Protein language model trained on about 40 million protein sequences and structures using a structure-aware vocabulary that combines residue tokens with Foldseek structure tokens, scored in ProteinGym as a zero-shot substitution baseline from sequence and structure.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-saprot` (https://doi.org/10.1101/2023.10.01.560349)
- Correction claim: `metadata-correction-3fd78ea427c0c5f0c2e5`

### `uc20260930-model-siterm` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Independent-sites phylogenetic model that estimates an amino acid substitution rate matrix for each column of a multiple sequence alignment and uses it for variant effect prediction, scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-siterm` (https://europepmc.org/article/MED/40487750)
- Correction claim: `metadata-correction-2e8c6225b616c92562a4`

### `uc20260930-model-trancepteve` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Hybrid of a family-agnostic autoregressive transformer and family-specific alignment-based models that relies more on the alignment models as alignment depth grows, scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-trancepteve` (https://doi.org/10.1101/2022.12.07.519495)
- Correction claim: `metadata-correction-cc91b6abc30f9835e6f4`

### `uc20260930-model-tranception` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Autoregressive transformer protein language model that can retrieve homologous sequences at inference to predict the fitness of substitutions, multiple mutants and indels; ProteinGym scores it with and without retrieval as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-tranception` (https://arxiv.org/abs/2205.13760v1)
- Correction claim: `metadata-correction-64e879f8e75018b07409`

### `uc20260930-model-unirep` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Deep learning representation of protein sequences learned from unlabeled amino-acid sequences, on which simple models predict stability and mutant function, scored in ProteinGym as a zero-shot single-sequence substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-unirep` (https://doi.org/10.1038/s41592-019-0598-1)
- Correction claim: `metadata-correction-c68b33ce0013676feedf`

### `uc20260930-model-unirep-evotuned` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Evo-tuned variant of UniRep, a protein sequence representation learned from unlabeled amino-acid sequences, which ProteinGym lists as using a multiple sequence alignment for evo-tuning and scores as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-unirep` (https://doi.org/10.1038/s41592-019-0598-1)
- Correction claim: `metadata-correction-56300357b3ef9e92a304`

### `uc20260930-model-venusrem` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Retrieval-enhanced protein language model that captures local amino acid interactions for mutation effect prediction, scored in ProteinGym as a zero-shot substitution baseline from alignment and structure inputs.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-venusrem` (https://doi.org/10.1093/bioinformatics/btaf189)
- Correction claim: `metadata-correction-ce01de4d719d625c7bb5`

### `uc20260930-model-vespa` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Logistic regression ensemble that predicts single amino acid variant effects without alignments from protein language model embeddings, combining predicted conservation, BLOSUM62 scores and language-model mask reconstruction probabilities; scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-vespa` (https://doi.org/10.1007/s00439-021-02411-y)
- Correction claim: `metadata-correction-8ebcc5e2421399e0dc29`

### `uc20260930-model-vespag` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Missense variant effect predictor that feeds protein language model embeddings to a minimal deep learning model trained on GEMME predictions for 39 million human variants, scored in ProteinGym as a substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `qa-descriptions-20261010-source-vespag` (https://doi.org/10.1093/bioinformatics/btae621)
- Correction claim: `metadata-correction-1079a7cee220b632f6e7`

### `uc20260930-model-vespal` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Light version of VESPA that predicts single amino acid variant effects from predicted conservation and BLOSUM62 scores only, without the language-model substitution probabilities, scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `qa-descriptions-20261010-source-vespa-full` (https://doi.org/10.1007/s00439-021-02411-y)
- Correction claim: `metadata-correction-7527b96f9938e64b7b45`

### `uc20260930-model-wavenet` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Alignment-free autoregressive deep generative model of protein sequences adapted from natural language processing that predicts missense and indel effects, scored in ProteinGym as a zero-shot substitution baseline.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-wavenet` (https://doi.org/10.1038/s41467-021-22732-w)
- Correction claim: `metadata-correction-e03c5d8f8b5464d2b7c9`

### `uc20260930-model-xtrimopglm` (model)

- Old: Named prediction model family identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Family of protein language models, scaled up to 100 billion parameters, pretrained jointly with autoencoding and autoregressive objectives for protein understanding and generation; ProteinGym scores several sizes as zero-shot single-sequence substitution baselines.
- Sources: `uc20260930-source-proteingym-amfr-spearman`; `run-doc-proteingym-readme-md-144fe22b` (https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md); `qa-descriptions-20261010-source-xtrimopglm` (https://doi.org/10.1038/s41592-025-02636-z)
- Correction claim: `metadata-correction-ea93ee446262ea488a8b`

## New sources

| Source ID | URL | SHA-256 |
| --- | --- | --- |
| `qa-descriptions-20261010-source-aido-protein-rag` | https://doi.org/10.1101/2024.12.02.626519 | `600401528a99b20a4a7c7bccf55ddf85f93bd3f50b24817e490b0ca64b4da722` |
| `qa-descriptions-20261010-source-aido-rna` | https://doi.org/10.1101/2024.11.28.625345 | `8a90c7c124402e1e89d38f485050b43de832db0682c43fd494ee40d694dffcb6` |
| `qa-descriptions-20261010-source-carp` | https://doi.org/10.1016/j.cels.2024.01.008 | `68e3e9f21b77774911d973330d658ce6dafd42634337718da56c24a780caf90d` |
| `qa-descriptions-20261010-source-deepsequence` | https://doi.org/10.1038/s41592-018-0138-4 | `8bfdae12466ae575e49c7404951670e7d7abe4979ce73ea470cfc784c2104da5` |
| `qa-descriptions-20261010-source-dnabert-s` | https://doi.org/10.1093/bioinformatics/btaf188 | `05d8e8c6f7821f4cddda7dd44349d8fab9fea1c91a3250ff7ae36b170e43ebf0` |
| `qa-descriptions-20261010-source-dnabert2` | https://arxiv.org/abs/2306.15006v2 | `0677624320848eb58c8500875ca3cbd4188ea8df2582e3dcf88a8623b99e8433` |
| `qa-descriptions-20261010-source-ernie-rna` | https://doi.org/10.1038/s41467-025-64972-0 | `6f259d649d3df86eb84f71044e5c253cb0b66c37ae6baf5de915932d967c9f02` |
| `qa-descriptions-20261010-source-escott` | https://doi.org/10.1101/2024.02.03.24302219 | `6a1a9c75ac7aa399e3812f9ccd5b85c80f69823df6c9467c87a7fe1cb92cbca4` |
| `qa-descriptions-20261010-source-esm-1b` | https://doi.org/10.1073/pnas.2016239118 | `59850211909f62201e41e520d345370ccc0de854697c2ad534dbdb3780f8fe53` |
| `qa-descriptions-20261010-source-eve` | https://doi.org/10.1038/s41586-021-04043-8 | `2adfed31d79ba75bd2ecb32ab8ffedc7a9d99e7b5e21091ccb058db2132ba81b` |
| `qa-descriptions-20261010-source-evo2` | https://doi.org/10.1101/2025.02.18.638918 | `ab65a131aa7ac7f648df4887875a9c3b1bd39cd9ae35d12546b4a6f77e4e2876` |
| `qa-descriptions-20261010-source-hyenadna` | https://arxiv.org/abs/2306.15794v2 | `25d27dc1ee289555f5fbaacb1ffdbe9c78a1c2a06fd305b9f134f8d346ff9e71` |
| `qa-descriptions-20261010-source-mif` | https://doi.org/10.1093/protein/gzad015 | `ab79533d43d38092bef109811d152e0ca07770fadd8b9a18b0d4d56881704996` |
| `qa-descriptions-20261010-source-msa-transformer` | https://doi.org/10.1101/2021.02.12.430858 | `d1bcaa01d5167374fbb01716d792bd8207c6e974bdd53409486e2bd2ab07a2d0` |
| `qa-descriptions-20261010-source-mulan` | https://doi.org/10.1093/bioadv/vbaf117 | `4b095839a0fbaa1a45ec7098fa30c44cc2199dca195153b9b3d10edee5e24bca` |
| `qa-descriptions-20261010-source-nt-v2` | https://doi.org/10.1038/s41592-024-02523-z | `94fd1bf1c8ac29a4d037b6f9bdc7eda76a47f1d1efa67082b7074f7a219e817a` |
| `qa-descriptions-20261010-source-orthrus` | https://doi.org/10.1038/s41592-026-03064-3 | `034ea6203ceabdd648e25bbb718ab4fa5ddd86720a7535d89a1a3883c67db9ef` |
| `qa-descriptions-20261010-source-poet` | https://arxiv.org/abs/2306.06156v3 | `b2ee8fe768676746f5f6d0881ecc7d1ee590ce1ccf16edf640b215bb66e4424b` |
| `qa-descriptions-20261010-source-progen2` | https://doi.org/10.1016/j.cels.2023.10.002 | `1bc888c2fe5cf8137c4cbc17eaa6e1f8fa49fd50804563d17406c3af0c6de305` |
| `qa-descriptions-20261010-source-progen3` | https://doi.org/10.1101/2025.04.15.649055 | `7502fc11dfdc2010705519b527f87b39503facd5ca2c2fb9e6353da767e6bc72` |
| `qa-descriptions-20261010-source-prosst` | https://doi.org/10.1101/2024.04.15.589672 | `efcc6e8cd6905ee2d3de5ae096bfeb2388dad798a4dc9a75c19746f5a77f1bbd` |
| `qa-descriptions-20261010-source-protgpt2` | https://doi.org/10.1038/s41467-022-32007-7 | `90fccf89e2600cc576108d6a6ded86f9577c4a20dae8a60b06b35c7ba8dc287f` |
| `qa-descriptions-20261010-source-protriever` | https://arxiv.org/abs/2506.08954v1 | `3ad6bd5b92e7a688bac5b00b5e426cd63aff988a24fc38a593bfa2319bb4f843` |
| `qa-descriptions-20261010-source-protssn` | https://doi.org/10.7554/elife.98033 | `402d694e5ab074a2b2dcea3c88b742d6a2269311f274bd699dbaacce12df463a` |
| `qa-descriptions-20261010-source-rinalmo` | https://doi.org/10.1038/s41467-025-60872-5 | `e9c58b7facff44a129edf7c942747be63d0263b00ce0cca3d7d4183a96d2987a` |
| `qa-descriptions-20261010-source-rita` | https://arxiv.org/abs/2205.05789v2 | `5251a8da98fb5a9811e27a81f8581fc415038b4a8b8bc9be9f951c8a903ce90e` |
| `qa-descriptions-20261010-source-s3f` | https://arxiv.org/abs/2412.01108v1 | `2fdfced916db0418fdbe0188747b1c8e3c1b0832aec6569642ffcdc97b4ae551` |
| `qa-descriptions-20261010-source-s3f-html` | https://arxiv.org/abs/2412.01108v1 | `9906e21b676729f27185a9554001d06455ceb588e889520f8b9a52f010048dda` |
| `qa-descriptions-20261010-source-saprot` | https://doi.org/10.1101/2023.10.01.560349 | `48426a94544faf887d6873bbb24304275c20cc41501cf2af99939ca24a147b83` |
| `qa-descriptions-20261010-source-siterm` | https://europepmc.org/article/MED/40487750 | `16e588f151dd7baebc624ed95cc203d4774759edd8db9c8ffbdc6be02e50e8da` |
| `qa-descriptions-20261010-source-splicebert` | https://doi.org/10.1093/bib/bbae163 | `08d1dce96c933d04a7633bedd5707373ad380029bf833ee20663a6921a773ff1` |
| `qa-descriptions-20261010-source-trancepteve` | https://doi.org/10.1101/2022.12.07.519495 | `854b5c8a5184b9ecaf975e27d204eb8f406dec95a69c463080b4c295bd349d27` |
| `qa-descriptions-20261010-source-tranception` | https://arxiv.org/abs/2205.13760v1 | `80f3bc0828013c7d03bd5879a5e226413b6940f61f40df9cd01b1c7c49ae9a7e` |
| `qa-descriptions-20261010-source-unirep` | https://doi.org/10.1038/s41592-019-0598-1 | `a634d5a0b076d1af23b9fdb68f64740c80cdcd2917e9fca9610c954e9105d643` |
| `qa-descriptions-20261010-source-venusrem` | https://doi.org/10.1093/bioinformatics/btaf189 | `294088af49705af2018234ede027e446697df8864d61a0b9c1a8ed65563d39b5` |
| `qa-descriptions-20261010-source-vespa` | https://doi.org/10.1007/s00439-021-02411-y | `3726920644abcdda3cc6365916de5ef0adb508610aabdfdeb4c6af66e48c271f` |
| `qa-descriptions-20261010-source-vespa-full` | https://doi.org/10.1007/s00439-021-02411-y | `042095fb9da6f1a9ed623768fbb86212af6b8d2b78949d9038f966bf65bd8e8b` |
| `qa-descriptions-20261010-source-vespag` | https://doi.org/10.1093/bioinformatics/btae621 | `aee9ee5fdec1550f270d03b2f75f8813ff88e3a8ecddefa6688b6710d3ab3429` |
| `qa-descriptions-20261010-source-wavenet` | https://doi.org/10.1038/s41467-021-22732-w | `31773ed84b9e14d337e38e61035b4d02f4ea2b4d5c2e084b32e13deccbffc8bf` |
| `qa-descriptions-20261010-source-xtrimopglm` | https://doi.org/10.1038/s41592-025-02636-z | `ba6635bd9dfe9b86a579b0b4fa319c776b69e6fe110039ee66a1c889e454e581` |
