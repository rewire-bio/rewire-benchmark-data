---
library_name: transformers
tags:
- biology
- bacteria
- prokaryotes
- genomics
- protein
- plm
- cplm
license: apache-2.0
metrics:
- accuracy
---

# bacformer-causal-MAG

Bacformer is a foundational model for bacterial genomics, modeling the whole bacterial genome as a sequence of proteins. 
Bacformer takes as input the set of proteins present in a genome, **ordered** by their positions on the chromosome and plasmid(s), and 
computes contextual protein representations with a transformer that conditions each protein on every other protein in the genome. 
Each protein is treated as a token; thus, Bacformer may be viewed as a **contextualized protein language model** that captures the protein–protein interactions 
underlying an organism’s phenotype.

Bacformer is pretrained to predict a masked (or next) protein *family* given the remaining proteins in the genome. 
The base model was trained on ~1.3 M diverse bacterial genomes comprising ~3 B protein sequences and can be adapted to a wide range of downstream tasks. 
See the [Bacformer models](https://huggingface.co/collections/macwiatrak/bacformer-681a17d6a77a928a1531def2) collection for all available checkpoints.

A key member of this collection is **bacformer-causal-MAG**, a 27M-parameter base transformer model trained on ~1.3M 
diverse metagenome-assembled genomes across more than 20k bacterial species and multiple environments.

All Bacformer variants embed protein sequences with a base protein language model by averaging the amino-acid token embeddings across each sequence. 
Bacformer uses [ESM-2 t12 35 M](https://huggingface.co/facebook/esm2_t12_35M_UR50D) as its base model.

- **Developed by:** University of Cambridge (Floto Lab) & EPFL (Brbić Lab), led by Maciej Wiatrak
- **License:** Apache 2.0

### Model Sources [optional]

- **Repository:** [https://github.com/macwiatrak/Bacformer](https://github.com/macwiatrak/Bacformer)
- **Paper:** TBA
  
## Usage

Install the `bacformer` package (see [https://github.com/macwiatrak/Bacformer](https://github.com/macwiatrak/Bacformer)). An end-to-end Python example demonstrating how to embed a genome with Bacformer is provided in the *tutorials* folder.

Below snippet shows how you can embed multiple protein sequences with `Bacformer`.

```python
import torch
from transformers import AutoModel
from bacformer.pp import protein_seqs_to_bacformer_inputs

device = "cuda:0"
model = AutoModel.from_pretrained("macwiatrak/bacformer-causal-MAG", trust_remote_code=True).to(device).eval().to(torch.bfloat16)

# Example input: a sequence of protein sequences
# in this case: 4 toy protein sequences
# Bacformer was trained with a maximum nr of proteins of 6000.
protein_sequences = [
    "MGYDLVAGFQKNVRTI",
    "MKAILVVLLG",
    "MQLIESRFYKDPWGNVHATC",
    "MSTNPKPQRFAWL",
]
# embed the proteins with ESM-2 to get average protein embeddings
inputs = protein_seqs_to_bacformer_inputs(
    protein_sequences,
    device=device,
    batch_size=128,  # the batch size for computing the protein embeddings
    max_n_proteins=6000,  # the maximum number of proteins Bacformer was trained with
)

# move the inputs to the device
inputs = {k: v.to(device) for k, v in inputs.items()}
# compute contextualized protein embeddings with Bacformer
with torch.no_grad():
    outputs = model(**inputs, return_dict=True)

print('last hidden state shape:', outputs["last_hidden_state"].shape)  # (batch_size, max_length, hidden_size)
print('genome embedding:', outputs.last_hidden_state.mean(dim=1).shape)  # (batch_size, hidden_size)
```

### Tutorials

We include a number of tutorials, see the [tutorials](https://github.com/macwiatrak/Bacformer) folder on the github repository.

## Training Details

### Training Data

**bacformer-causal-MAG** was pretrained on the **MAG corpus** 
(≈1.3 M metagenome-assembled genomes). 
The MAG set maximises environmental and taxonomic diversity and contains roughly 3B protein sequences.

### Training Procedure

#### Preprocessing

Each genome is represented as an ordered list of proteins. 
ranslated protein sequences were obtained from annotations or translated de novo when necessary. 
Proteins were ordered by genomic coordinates; for MAGs, proteins within each contig were ordered, and the contig order was randomised in every epoch.

The set of protein sequences in the genome are embedded with the base protein language model ([ESM-2 t12 35M](https://huggingface.co/facebook/esm2_t12_35M_UR50D)).
The protein embeddings computed by averaging the amino acid tokens in a protein sequence are used as protein tokens. 
Finally the protein tokens are fed into a transformer model.

During pretraining, we limit the maximum number of proteins in a genome to `6,000`, which covers whole bacterial genome in `>98%` of genomes present in out training corpus.


### Pretraining

#### Training objective
The model was optimised to predict the next protein given previous proteins present in the genome. As the number of protein is effectively unbound, we assigned each protein a discrete protein family index by performing 
unsupervised clustering on a set of proteins, resulting in `50k` distinct protein family clusters.
Importantly, the input to Bacformer are exact protein sequence and we only use the discrete protein family label in a final classification layer where predicting
the protein family of masked proteins. This allows the model to work on amino acid level tasks where even single mutations can change the phenotype of a genome.

The causal pretraining objective effectively predicts the protein family ID of the next protein given the embedding of the previous protein in the genome sequence.


#### Pretraining details
The initial pretraining on MAGs was trained on 4 A100 80GB NVIDIA GPUs, with an effective batch size of 32. The maximum sequence length of each protein
was set to `1,024` and the maximum number of proteins in a genome was set to `6,000`, which covers whole bacterial genome in `>98%` of genomes present in our training corpus.
The Adam optimizer [1] was used with a linear warmup learning rate schedule, with the number of warmup steps equal to `7,500`. The base learning rate of `0.00015` was used,
scaled by square root of number of GPUs (`lr = args.lr * np.sqrt(max(n_gpus, 1))`). We monitor the loss on the validation set as the measure of performance during training.


### Architecture

#### Input embeddings

The input embeddings are created by adding together 1) protein embeddings from a base protein language model (pLM) [ESM-2 t12 35M](https://huggingface.co/facebook/esm2_t12_35M_UR50D),
2) contig (token type) embeddings. The 1) are created by embedding a protein sequence with the pretrained base pLM model and taking the average of all amino acid
tokens in the sequence, resulting in a `D` dimensional vector. We embed all of the `N` proteins present in the whole bacterial genome resulting in a `N x D` matrix,
where `D` is the dimension of the base pLM model, here `480`. The protein embeddings are added together with the 2) contig embeddings. The contig embeddings
are learnable embeddings which represent the unique contigs present in the genome. As an example, if a genome is made up of `K` contigs, each containing a number of proteins,
each protein within the same contig will have the same contig embedding, which is different from the embeddings of different contigs.
Contig embeddings have been created to account for the fact that bacterial genomes are often made up of chromosome and plasmid(s) and are frequently collated by combining
multiple contigs together (metagenome assembled genomes).
The contig embeddings are initialised and train from scratch at the beginning of pretraining.

The genomic organisation is highly important for bacteria, to model it we employ **rotary positional embeddings** [2].

The input embeddings are ordered by their order on the contig/chromosome/plasmid. This [...]. Additionally, we include special tokens. Specifically, 1) `[CLS]` token 
at the start of the sequence, 2) `[SEP]` token between the contigs or chromosomes(s)/plasmid(s), 3) `[END]` token at the end of the genome. The example below show how does
the genome representation look like for complete genomes and MAGs.

**Complete genomes**
```
[CLS] [chromosome1_gene1] [chromosome2_gene2] ... [chromosomme1_geneN] [SEP] [plasmid1_gene1] ... [plasmid1_geneM] [END]
```

**Metagenome-assembled genome (MAG)**
```
[CLS] [contig1_gene1] ... [contig1_geneN] [SEP] [contig2_gene1] ... [contig2_geneM] [SEP] ... [contigZgeneV] [END]
```

#### Transformer backbone

The input embeddings are fed into a transformer, which computes protein representations conditional on other proteins present in the genome
by computing self-attention between them, resulting in **contextual protein embeddings**.

The transformer is 12 layer transformer with `hidden_dim=480` and is trained from scratch. Bacformer leverages the flash attention available in `pytorch>=2.2`.

#### Pretraining classification head

Bacformer is pretrained to predict masked or next protein family based on the other proteins present in the genome. Given the embedding from the last hidden state of
the transformer of masked or the previous protein, the classification head predicts the protein family. We predict protein family, rather than a protein, because the space of
possible proteins is effectively unbound. To get a discrete vocabulary of proteins, we we assigned each protein a discrete protein family index by performing 
unsupervised clustering on a set of proteins, resulting in `50k` distinct protein family clusters. Importantly, the input to Bacformer are 
exact protein sequences present in the whole bacterial genome, rather than protein family tokens. This allows the model to work on amino acid level tasks where even single mutations 
can change the phenotype of a genome, while still allowing for pretraining.

## Citation

```bibtex
@article{Wiatrak2025.07.20.665723,
	author = {Wiatrak, Maciej and Vi{\~n}as Torn{\'e}, Ramon and Ntemourtsidou, Maria and Dinan, Adam M. and Abelson, David C. and Arora, Divya and Brbi{\'c}, Maria and Weimann, Aaron and Floto, Rodrigo Andres},
	title = {A contextualised protein language model reveals the functional syntax of bacterial evolution},
	elocation-id = {2025.07.20.665723},
	year = {2025},
	doi = {10.1101/2025.07.20.665723},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2025/07/20/2025.07.20.665723},
	eprint = {https://www.biorxiv.org/content/early/2025/07/20/2025.07.20.665723.full.pdf},
	journal = {bioRxiv}
}
```

## Contact

In case of questions/issues or feature requests please raise an issue on github - https://github.com/macwiatrak/Bacformer.