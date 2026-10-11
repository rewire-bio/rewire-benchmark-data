# Issue #88 placeholder descriptions, batch A, 2026-10-11

Scope: 59 of the 167 placeholder records in `qa-descriptions-20261011/scan.md`:
- the 49 mRNABench linear-probe pipelines ("Named representation or feature baseline with a task-specific linear probe ...");
- the 8 methods described as "Named prediction method identified in the cited primary source";
- the 2 models described as "Base method introduced by <author> (<year>)" (DeepAffinity, DeepDTA).

Method, as in qa-descriptions-20261010:
- one sentence saying what the method does, from its primary source;
- no provenance in the description;
- the old text kept in a metadata-correction claim.

The old texts here carry no provenance worth moving: the source is already in `source_ids` and `source_locator`.

`build.py` reads the original lines from origin/main, applies the changes, writes `methods.jsonl` (8 lines), `models.jsonl` (2) and `pipelines.jsonl` (49), and regenerates `batch.jsonl`. `build.py --check` repeats the checks without writing. Only `description` and `source_ids` change, and the script asserts that.

`batch.jsonl` holds 62 records, all `needs_review`: 3 new sources and 59 correction claims.

Integrated together with batches a to e on 2026-10-11, after independent review: see `review.json` in this folder and `docs/reviews/2026-10-11-description-batches-a-e.md`. The records are now `source_checked`. Before review: `records -- add` and `records -- change` were not yet run. In a throwaway copy of origin/main, adding the batch, applying `build.py` and recording the 59 changes passed SHACL, `records check` (45,666 records) and the source-identity, attribute and evidence-completion tests. The copy was deleted. The first attempt at that trial was refused by SHACL with no violation printed. A clean rerun with identical inputs passed, and I could not reproduce the refusal.

## The mRNABench template

The 49 pipelines share one source, `expansion-p3-mrnabench-2025`, whose Section 4.3 says each model is evaluated by "training a linear classifier on frozen embeddings" with "transcript-level embeddings by averaging over per-nucleotide embeddings". Appendix A, "Overview of Evaluated Models", gives a row per model family and per checkpoint.

Each description is:

> Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from `<checkpoint>`, a `<family>` checkpoint `[<what the table says about this checkpoint>]`; `<family>` is `<the table's family description>`.

What differs between records is the base model (checkpoint and family) and the checkpoint note. The probe target is each mRNABench task, so the template says "trained per mRNABench task" rather than naming one target. The three naive baselines use the same probe wording with the features or untrained Mamba that Appendix A describes. Parameter counts and context lengths are left to the checkpoint names and the source table.

## Sources

Each artifact was re-downloaded on 2026-10-11 and hashed. Only Europe PMC REST, arXiv and the pinned GitHub URLs were used; no email or other personal identifier was sent.

| Source | Artifact | SHA-256 against the pin |
| --- | --- | --- |
| `expansion-p3-mrnabench-2025` | Europe PMC full text PMC12265608 | Matches |
| `run-doc-proteingym-readme-md-144fe22b` | ProteinGym README at 144fe22b | Matches |
| `profile-protocol-proteingym-paper-xml-a58110e0` | Europe PMC full text PMC10723403 | Matches (`a58110e0...`). Another record, `expansion-p3-proteingym-2023`, pins the same URL at `4519641f...`, which today's download does not reproduce, so this batch cites the record that does. |
| `uc20260930-source-rhomax-2024` | Europe PMC full text PMC11200256 | Matches |
| `uc20260930-source-framepool-2021` | Europe PMC full text PMC8136849 | Matches |
| `uc20260930-source-jores-2021` | Jores et al. 2021 PDF | Matches |
| `source-label-deepaffinity-arxiv-97d6e3ae` | arXiv 1806.07537v2 PDF | Matches |
| `source-label-deepdta-arxiv-3c368fed` | arXiv 1801.10193v2 PDF | Matches |
| `qa-descriptions-20261011-a-source-hopf2017` (new) | Europe PMC core record MED/28092658 | New pin `6a91a293...`; no licence in the record. The full text (PMC5383098) is not open access. |
| `qa-descriptions-20261011-a-source-gemme2019` (new) | Europe PMC core record MED/31406981 | New pin `64051ec6...`; CC BY-NC |
| `qa-descriptions-20261011-a-source-rsalor2025` (new) | Europe PMC preprint record PPR974202 | New pin `a2850ec4...`; CC BY-NC-ND; bioRxiv preprint |

## Changed records

### The other 10 records

#### `identity-model-deepaffinity`

- Old: Base method introduced by Karimi et al. (2019). Evaluated configurations, retrained weights and their scores are separate records.
- New: Semi-supervised deep learning model that predicts compound-protein affinity from a compound SMILES string and a structure-annotated protein sequence, using recurrent encoders followed by convolutional layers.
- Sources: `source-label-deepaffinity-arxiv-97d6e3ae`, `source-label-deepaffinity-readme-debca4c9`
- Locator: source-label-deepaffinity-arxiv-97d6e3ae: abstract, p.1 ('a semi-supervised deep learning model that unifies recurrent and convolutional neural networks'); §§2.2-2.4; the record's reviewed profile summary

#### `identity-model-deepdta`

- Old: Base method introduced by Öztürk et al. (2018). Evaluated configurations, retrained weights and their scores are separate records.
- New: Deep learning model that predicts drug-target binding affinity from a ligand SMILES string and a protein sequence, using a separate one-dimensional convolutional encoder for each.
- Sources: `source-label-deepdta-arxiv-3c368fed`, `source-label-deepdta-readme-a546a843`
- Locator: source-label-deepdta-arxiv-3c368fed: abstract, p.1 ('a deep-learning based model that uses only sequence information of both targets and drugs ... modeling of protein sequences and compound 1D representations with convolutional neural networks'); the record's reviewed profile summary

#### `uc20260930-method-blasso-rhodopsin-predictor`

- Old: Named prediction method identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Bayesian LASSO regression that predicts a rhodopsin's absorption wavelength from predefined physicochemical features of the amino acids in its sequence, without using its three-dimensional structure.
- Sources: `uc20260930-source-rhomax-2024`
- Locator: uc20260930-source-rhomax-2024: Introduction (the approach of Inoue et al. 'utilizes the Bayesian LASSO ... based on predefined physicochemical features of amino acids. This approach does not take into account the geometric three-dimensional (3D) structure'); Comparison to Previous Methods

#### `uc20260930-method-evmutation`

- Old: Named prediction method identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Unsupervised statistical model, fitted to a multiple sequence alignment of the protein family, that predicts mutation effects while explicitly capturing dependencies between residue positions.
- Sources: `uc20260930-source-proteingym-amfr-spearman`, `qa-descriptions-20261011-a-source-hopf2017`, `profile-protocol-proteingym-paper-xml-a58110e0`
- Locator: qa-descriptions-20261011-a-source-hopf2017: abstractText ('EVmutation, an unsupervised statistical method for predicting the effects of mutations that explicitly captures residue dependencies between positions'); profile-protocol-proteingym-paper-xml-a58110e0: Baselines (alignment-based models 'are trained on Multiple Sequence Alignments')

#### `uc20260930-method-frame-aware-k-mer-random-forest`

- Old: Named prediction method identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Random forest whose input is the k-mer counts of the sequence computed separately for each of the three reading frames, trained on the same MPRA training set as FramePool50.
- Sources: `uc20260930-source-framepool-2021`, `uc20260930-source-framepool-s4`
- Locator: uc20260930-source-framepool-2021: Methods, Random forest models ('the framed_forest model. This random forest takes as input the k-mer-counts for each frame (giving a vector of length 3*(4^k))'); S7 Fig caption

#### `uc20260930-method-gemme`

- Old: Named prediction method identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Global epistatic model that predicts mutational effects by modelling the evolutionary history of the natural sequences in a protein family's alignment, with a few interpretable parameters.
- Sources: `uc20260930-source-proteingym-amfr-spearman`, `qa-descriptions-20261011-a-source-gemme2019`
- Locator: qa-descriptions-20261011-a-source-gemme2019: abstractText ('predicts mutational outcomes by explicitly modeling the evolutionary history of natural sequences ... GEMME uses only a few biologically meaningful and interpretable parameters'); run-doc-proteingym-readme-md-144fe22b: baselines table, row GEMME (MSA)

#### `uc20260930-method-jores-gc-and-motif-linear-regression`

- Old: Named prediction method identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Linear model that predicts plant core promoter strength from the promoter's GC content and its maximum motif scores for six core promoter elements and 72 consensus transcription-factor binding motifs.
- Sources: `uc20260930-source-jores-2021`
- Locator: uc20260930-source-jores-2021: Methods, Computational modelling of promoter strength ('a linear model for predicting promoter strength on the basis of the promoter's GC content and its maximum motif score for six core promoter elements ... and 72 consensus TF-binding motifs')

#### `uc20260930-method-k-mer-count-random-forest`

- Old: Named prediction method identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Random forest whose input is a fixed-length vector of the sequence's 3-mer or 4-mer counts, with no reading-frame information, trained on the same MPRA training set as FramePool50.
- Sources: `uc20260930-source-framepool-2021`, `uc20260930-source-framepool-s4`
- Locator: uc20260930-source-framepool-2021: Methods, Random forest models ('random forest models which use k-mer counts as input features ... 3mer_random_forest and 4mer_random_forest'); S7 Fig caption ('offers no frame information')

#### `uc20260930-method-rsalor`

- Old: Named prediction method identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Evolutionary score that predicts mutational effects from the log-odds ratio of wild-type and mutant residue frequencies in related proteins, scaled by the residue's relative solvent accessibility.
- Sources: `uc20260930-source-proteingym-amfr-spearman`, `qa-descriptions-20261011-a-source-rsalor2025`
- Locator: qa-descriptions-20261011-a-source-rsalor2025: abstractText ('a simple evolutionary score, based on the log-odd ratio (LOR) of wild-type and mutated residue frequencies in evolutionary related proteins, when scaled by the residue's relative solvent accessibility (RSA)'); run-doc-proteingym-readme-md-144fe22b: baselines table, row RSALOR (MSA & Structure)

#### `uc20260930-method-site-independent`

- Old: Named prediction method identified in the cited primary source. Exact fitted configurations and scores are separate records.
- New: Alignment-based model, fitted to a multiple sequence alignment of the protein family, that predicts mutation effects from each position separately, without the dependencies between positions that EVmutation adds.
- Sources: `uc20260930-source-proteingym-amfr-spearman`, `qa-descriptions-20261011-a-source-hopf2017`, `profile-protocol-proteingym-paper-xml-a58110e0`
- Locator: profile-protocol-proteingym-paper-xml-a58110e0: Baselines ('Alignment-based models, such as site-independent and EVmutation models [Hopf et al., 2017] ... are trained on Multiple Sequence Alignments'); qa-descriptions-20261011-a-source-hopf2017: abstractText (EVmutation 'explicitly captures residue dependencies between positions'; most methods 'do not consider the interdependencies of residues')

### The 49 mRNABench pipelines

Old text, the same for all 49: "Named representation or feature baseline with a task-specific linear probe; the complete evaluated pipeline is distinct from its underlying model."

Source for all 49: `expansion-p3-mrnabench-2025`. Locator: expansion-p3-mrnabench-2025: Appendix A, Overview of Evaluated Models (family and variant rows; naive baselines paragraph); Section 4.3, Linear Probing ('training a linear classifier on frozen embeddings'; 'averaging over per-nucleotide embeddings').

| Record | New description |
| --- | --- |
| `…-aido-rna-1b600m` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from aido-rna-1b600m, an AIDO.RNA checkpoint; AIDO.RNA is a Transformer RNA model trained on 42 million non-coding RNAs from RNAcentral. |
| `…-aido-rna-1b600m-cds` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from aido-rna-1b600m-cds, an AIDO.RNA checkpoint domain-adapted for mRNA on coding sequences; AIDO.RNA is a Transformer RNA model trained on 42 million non-coding RNAs from RNAcentral. |
| `…-aido-rna-650m` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from aido-rna-650m, an AIDO.RNA checkpoint; AIDO.RNA is a Transformer RNA model trained on 42 million non-coding RNAs from RNAcentral. |
| `…-aido-rna-650m-cds` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from aido-rna-650m-cds, an AIDO.RNA checkpoint domain-adapted for mRNA on coding sequences; AIDO.RNA is a Transformer RNA model trained on 42 million non-coding RNAs from RNAcentral. |
| `…-dnabert-s` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from dnabert-s, a DNABERT-S checkpoint; DNABERT-S is a Transformer DNA model trained by contrastive learning on prokaryotic genomes. |
| `…-dnabert2` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from dnabert2, a DNABERT2 checkpoint; DNABERT2 is a Transformer DNA model trained on a multispecies dataset with byte-pair-encoding tokens. |
| `…-ernierna` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from ernierna, an ERNIE-RNA checkpoint; ERNIE-RNA is a Transformer RNA model pretrained on 20 million non-coding RNAs with structural information added as attention-mask biases. |
| `…-ernierna-ss` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from ernierna-ss, an ERNIE-RNA checkpoint fine-tuned on secondary structure; ERNIE-RNA is a Transformer RNA model pretrained on 20 million non-coding RNAs with structural information added as attention-mask biases. |
| `…-evo-1-131k-base` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from evo-1-131k-base, an Evo checkpoint trained with extended context; Evo is a StripedHyena DNA model trained autoregressively on the OpenGenome dataset. |
| `…-evo-1-5-8k-base` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from evo-1.5-8k-base, an Evo checkpoint trained on an Evo 1 dataset enlarged by 50%; Evo is a StripedHyena DNA model trained autoregressively on the OpenGenome dataset. |
| `…-evo-1-8k-base` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from evo-1-8k-base, an Evo checkpoint that is the base model; Evo is a StripedHyena DNA model trained autoregressively on the OpenGenome dataset. |
| `…-evo2-1b-base` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from evo2-1b-base, an Evo 2 checkpoint trained as a base model on a mixture of genomic regions including mRNA; Evo 2 is a StripedHyena2 DNA model trained autoregressively on OpenGenome2, 9 trillion nucleotides across all domains of life. |
| `…-evo2-7b` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from evo2-7b, an Evo 2 checkpoint with extended context, trained on long genomic sequences; Evo 2 is a StripedHyena2 DNA model trained autoregressively on OpenGenome2, 9 trillion nucleotides across all domains of life. |
| `…-evo2-7b-base` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from evo2-7b-base, an Evo 2 checkpoint trained as a base model on a mixture of genomic regions including mRNA; Evo 2 is a StripedHyena2 DNA model trained autoregressively on OpenGenome2, 9 trillion nucleotides across all domains of life. |
| `…-helix-mrna` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from helix-mrna, a Helix-mRNA checkpoint; Helix-mRNA is an mRNA foundation model with a Mamba2 and Transformer hybrid backbone trained on 26 million mRNAs from eukaryotic and viral species. |
| `…-hyenadna-large-1m` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from hyenadna-large-1m, a HyenaDNA checkpoint; HyenaDNA is a Hyena DNA model trained autoregressively on the human reference genome. |
| `…-hyenadna-medium-160k` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from hyenadna-medium-160k, a HyenaDNA checkpoint; HyenaDNA is a Hyena DNA model trained autoregressively on the human reference genome. |
| `…-hyenadna-medium-450k` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from hyenadna-medium-450k, a HyenaDNA checkpoint; HyenaDNA is a Hyena DNA model trained autoregressively on the human reference genome. |
| `…-hyenadna-small-32k` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from hyenadna-small-32k, a HyenaDNA checkpoint; HyenaDNA is a Hyena DNA model trained autoregressively on the human reference genome. |
| `…-hyenadna-tiny-16k-d128` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from hyenadna-tiny-16k-d128, a HyenaDNA checkpoint; HyenaDNA is a Hyena DNA model trained autoregressively on the human reference genome. |
| `…-mrna-fm` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from mrna-fm, an RNA-FM checkpoint trained on 45 million coding-only sequences (the mRNA-FM variant); RNA-FM is a Transformer RNA foundation model pretrained on 23 million non-coding RNAs. |
| `…-naive-4` | Linear probe, trained per mRNABench task, on hand-made sequence features (all k-mers of size three to seven and GC content), with no learned model. |
| `…-naive-6` | Linear probe, trained per mRNABench task, on hand-made sequence features (all k-mers of size three to seven, GC content, CDS length and exon count), with no learned model. |
| `…-naive-mamba` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from an untrained three-layer Mamba with 64 hidden dimensions and random initial weights. |
| `…-nt-2-5b-1000g` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from nt-2.5b-1000g, a Nucleotide Transformer checkpoint trained on the 1000 Genomes Project; the Nucleotide Transformer is a Transformer DNA model on 6-mer tokens. |
| `…-nt-2-5b-multi-species` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from nt-2.5b-multi-species, a Nucleotide Transformer checkpoint trained on 850 genomes; the Nucleotide Transformer is a Transformer DNA model on 6-mer tokens. |
| `…-nt-500m-1000g` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from nt-500m-1000g, a Nucleotide Transformer checkpoint trained on the 1000 Genomes Project; the Nucleotide Transformer is a Transformer DNA model on 6-mer tokens. |
| `…-nt-500m-human-ref` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from nt-500m-human-ref, a Nucleotide Transformer checkpoint trained on the human reference genome; the Nucleotide Transformer is a Transformer DNA model on 6-mer tokens. |
| `…-nt-v2-100m-multi-species` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from nt-v2-100m-multi-species, a Nucleotide Transformer checkpoint from the v2 series, which uses RoPE and GLUs, trained on multiple species; the Nucleotide Transformer is a Transformer DNA model on 6-mer tokens. |
| `…-nt-v2-250m-multi-species` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from nt-v2-250m-multi-species, a Nucleotide Transformer checkpoint from the v2 series, which uses RoPE and GLUs, trained on multiple species; the Nucleotide Transformer is a Transformer DNA model on 6-mer tokens. |
| `…-nt-v2-500m-multi-species` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from nt-v2-500m-multi-species, a Nucleotide Transformer checkpoint from the v2 series, which uses RoPE and GLUs, trained on multiple species; the Nucleotide Transformer is a Transformer DNA model on 6-mer tokens. |
| `…-nt-v2-50m-multi-species` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from nt-v2-50m-multi-species, a Nucleotide Transformer checkpoint from the v2 series, which uses RoPE and GLUs, trained on multiple species; the Nucleotide Transformer is a Transformer DNA model on 6-mer tokens. |
| `…-orthrus-base-4` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from orthrus-base-4, an Orthrus checkpoint; Orthrus is a Mamba mRNA foundation model pretrained by contrastive learning on mRNA splice isoforms and orthologs. |
| `…-orthrus-large-6` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from orthrus-large-6, an Orthrus checkpoint pretrained with splice and codon tracks; Orthrus is a Mamba mRNA foundation model pretrained by contrastive learning on mRNA splice isoforms and orthologs. |
| `…-orthrus-mlm` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from orthrus-mlm, an Orthrus checkpoint; Orthrus is a Mamba mRNA foundation model pretrained by contrastive learning on mRNA splice isoforms and orthologs. |
| `…-rinalmo` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from rinalmo, a RiNALMo checkpoint; RiNALMo is a Transformer RNA model trained on 36 million non-coding RNAs. |
| `…-rna-fm` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from rna-fm, an RNA-FM checkpoint; RNA-FM is a Transformer RNA foundation model pretrained on 23 million non-coding RNAs. |
| `…-rnabert` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from rnabert, an RNABERT checkpoint; RNABERT is a Transformer RNA model pretrained with masked language modelling and a structural alignment objective on 80,000 non-coding RNAs. |
| `…-rnaernie` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from rnaernie, an RNAErnie checkpoint; RNAErnie is a Transformer RNA model pretrained on 23 million non-coding RNAs with motif-level masking. |
| `…-rnamsm` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from rnamsm, an RNA-MSM checkpoint; RNA-MSM is a Transformer RNA model trained on multiple sequence alignments of about 8 million non-coding RNAs. |
| `…-splicebert-h-510nt` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from splicebert-h-510nt, a SpliceBERT checkpoint trained only on human sequences; SpliceBERT is a Transformer mRNA model trained on 2 million vertebrate mRNAs. |
| `…-splicebert-v-1024nt` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from splicebert-v-1024nt, a SpliceBERT checkpoint; SpliceBERT is a Transformer mRNA model trained on 2 million vertebrate mRNAs. |
| `…-splicebert-v-510nt` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from splicebert-v-510nt, a SpliceBERT checkpoint with a 510-nucleotide context; SpliceBERT is a Transformer mRNA model trained on 2 million vertebrate mRNAs. |
| `…-utrbert-3mer` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from utrbert-3mer, a 3'UTRBERT checkpoint with a 3-mer tokenizer; 3'UTRBERT is a Transformer mRNA model pretrained on the 3' UTRs of 100,000 human mRNAs. |
| `…-utrbert-4mer` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from utrbert-4mer, a 3'UTRBERT checkpoint with a 4-mer tokenizer; 3'UTRBERT is a Transformer mRNA model pretrained on the 3' UTRs of 100,000 human mRNAs. |
| `…-utrbert-5mer` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from utrbert-5mer, a 3'UTRBERT checkpoint with a 5-mer tokenizer; 3'UTRBERT is a Transformer mRNA model pretrained on the 3' UTRs of 100,000 human mRNAs. |
| `…-utrbert-6mer` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from utrbert-6mer, a 3'UTRBERT checkpoint with a 6-mer tokenizer; 3'UTRBERT is a Transformer mRNA model pretrained on the 3' UTRs of 100,000 human mRNAs. |
| `…-utrlm-mrl` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from utrlm-mrl, a UTR-LM checkpoint trained for mean ribosome loading; UTR-LM is a Transformer mRNA model pretrained on random and endogenous 5' UTR sequences from various species. |
| `…-utrlm-te-el` | Linear probe, trained per mRNABench task, on frozen embeddings averaged over nucleotides from utrlm-te-el, a UTR-LM checkpoint trained for translation efficiency and expression level; UTR-LM is a Transformer mRNA model pretrained on random and endogenous 5' UTR sequences from various species. |

## For the reviewer

- **Site-Independent.** No pinned source defines it in its own words. The ProteinGym paper groups it with EVmutation as an alignment-based model trained on MSAs, citing Hopf et al. 2017. The Hopf abstract contrasts EVmutation, which "explicitly captures residue dependencies between positions", with methods that do not. "Predicts mutation effects from each position separately" rests on that contrast and on the model's name. Reject it if that is too thin, and the record moves to the gaps file.
- **orthrus-mlm.** mRNABench Appendix A does not describe this checkpoint; it appears only in the results tables. Its description therefore says only that it is an Orthrus checkpoint (see gaps.md).
- **hyenadna-tiny-16k-d128.** Appendix A lists it as `hyenadna-tiny-16k`; the results tables use the `-d128` name.
- Check each of the 10 non-mRNABench sentences against its quoted locator, and spot-check the mRNABench rows against Appendix A.
- Then set the 62 batch records to `source_checked` with a review block, or correct them in `build.py` and rerun it.

## Integration, after review

Add the batch first, because 4 edited records cite the new sources:

```
npm run records -- add data/omics/qa-descriptions-20261011-a/batch.jsonl data/omics/qa-descriptions-20261011-a
npm run records -- change data/omics/qa-descriptions-20261011-a/review.md data/omics/qa-descriptions-20261011-a <the 59 record IDs>
```

The 59 IDs are the `subject` links of the claims in `batch.jsonl`.
