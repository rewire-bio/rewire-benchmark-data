---
datasets:
- tattabio/OMG
license: apache-2.0
---

# gLM2_150M

gLM2 is a mixed-modality genomic language model, trained on the [`OMG Dataset`](https://huggingface.co/datasets/tattabio/OMG).
The model encodes a genomic scaffold with both both amino-acid and DNA tokens. 

gLM2 is trained at two scales: 150M and 650M parameters (available at [`tattabio/gLM2_650M`](https://huggingface.co/tattabio/gLM2_650M)).

See [https://github.com/TattaBio/gLM2](https://github.com/TattaBio/gLM2) for inference scripts.

### Model Description

gLM2 is a transformer encoder trained with the masked language modeling objective.  
It encodes a genomic contig as a sequence of protein coding sequences (CDS) and DNA inter-genic sequences (IGS).  
CDS elements are tokenized using per-amino acid tokens, and IGS elements are tokenized using per-nucleotide tokens.


- To encode the genomic strand, we prepended each genomic element with a special token, either `<+>` or `<->` to indicate the positive and negative strands.
- To avoid collision between amino acid and nucleotide tokens, the tokenizer expects all amino acids to be uppercase, and all nucleotides to be lowercase.

UPDATE(09/2024): We updated the model with longer context length (4096 tokens vs. 2048 tokens) and per-nucleotide IGS tokenization instead of BPE.

## Getting Started


```python
import torch
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained('tattabio/gLM2_150M', torch_dtype=torch.bfloat16, trust_remote_code=True).cuda()
tokenizer = AutoTokenizer.from_pretrained('tattabio/gLM2_150M', trust_remote_code=True)

# A contig with two proteins and an inter-genic sequence.
# NOTE: Nucleotides should always be lowercase, and prepended with `<+>`.
sequence = "<+>MALTKVEKRNRIKRRVRGKISGTQASPRLSVYKSNK<+>aatttaaggaa<->MLGIDNIERVKPGGLELVDRLVAVNRVTKVTKGGRAFGFSAIVVVGNED"

# Tokenize the sequence.
encodings = tokenizer([sequence], return_tensors='pt')

# Extract embeddings.
with torch.no_grad():
    embeddings = model(encodings.input_ids.cuda(), output_hidden_states=True).last_hidden_state

```

### Training Data

gLM2 is trained on the [`OMG`](https://huggingface.co/datasets/tattabio/OMG) dataset.
To improve the dataset balance and remove near-duplicate examples, the data is tokenized and pruned by applying Semantic Deduplication [SemDedup](https://arxiv.org/abs/2303.09540).  
We use an embedding distance threshold of 2e-3, resulting in 49% of the dataset being pruned. 

## Training Details

- Pretraining tokens: 315B
- Context length: 4096
- Masking rate: 30%
- Learning rate: 1e-3
- Optimizer: AdamW (betas = (0.9, 0.95))
- Mixed precision training: bfloat16
- Weight decay: 0.1


## Citation

**BioRxiv:**
[https://www.biorxiv.org/content/10.1101/2024.08.14.607850](https://www.biorxiv.org/content/10.1101/2024.08.14.607850)

**BibTeX:**

```@article {Cornman2024.08.14.607850,
	author = {Cornman, Andre and West-Roberts, Jacob and Camargo, Antonio Pedro and Roux, Simon and Beracochea, Martin and Mirdita, Milot and Ovchinnikov, Sergey and Hwang, Yunha},
	title = {The OMG dataset: An Open MetaGenomic corpus for mixed-modality genomic language modeling},
	elocation-id = {2024.08.14.607850},
	year = {2024},
	doi = {10.1101/2024.08.14.607850},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2024/08/17/2024.08.14.607850},
	eprint = {https://www.biorxiv.org/content/early/2024/08/17/2024.08.14.607850.full.pdf},
	journal = {bioRxiv}
}