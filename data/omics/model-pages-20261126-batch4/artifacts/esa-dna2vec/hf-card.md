---
library_name: transformers
license: mit
pipeline_tag: sentence-similarity
---

# DNA2Vec: Transformer-Based DNA Sequence Embedding

This repository provides an implementation of `dna2vec`, a transformer-based model designed for DNA sequence embeddings. It includes both the Hugging Face (`hf_model`) and a locally trained model (`local_model`). The model can be used for DNA sequence alignment, classification, and other genomic applications.

## Model Overview

DNA sequence alignment is an essential genomic task that involves mapping short DNA reads to the most probable locations within a reference genome. Traditional methods rely on genome indexing and efficient search algorithms, while recent advances leverage transformer-based models to encode DNA sequences into vector representations. 

The `dna2vec` framework introduces a **Reference-Free DNA Embedding (RDE) Transformer model**, which encodes DNA sequences into a shared vector space, allowing for efficient similarity search and sequence alignment.

### Key Features:
- **Transformer-based architecture** trained on genomic data.
- **Reference-free embeddings** that enable efficient sequence retrieval.
- **Contrastive loss for self-supervised training**, ensuring robust sequence similarity learning.
- **Support for Hugging Face and custom-trained local models**.
- **Efficient search through a DNA vector store**, reducing genome-wide alignment to a local search.

## Model Details

### Model Architecture
The transformer model consists of:
- **12 attention heads**
- **6 encoder layers**
- **Embedding dimension:** 1020
- **Vocabulary size:** 10,000
- **Cosine similarity-based sequence matching**
- **Dropout:** 0.1
- **Training: Cosine Annealing learning rate scheduling**

## Installation

To use the model, install the required dependencies:

```bash
pip install transformers torch
```

## Usage

### Load Hugging Face Model

```python
from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn as nn

def load_hf_model():
    hf_model = AutoModel.from_pretrained("roychowdhuryresearch/dna2vec", trust_remote_code=True)
    hf_tokenizer = AutoTokenizer.from_pretrained("roychowdhuryresearch/dna2vec", trust_remote_code=True)
    
    class AveragePooler(nn.Module):
        def forward(self, last_hidden, attention_mask):
            return (last_hidden * attention_mask.unsqueeze(-1)).sum(1) / attention_mask.sum(-1).unsqueeze(-1)
    
    hf_model.pooler = AveragePooler()
    return hf_model, hf_tokenizer, hf_model.pooler
```
###Using the Model
    Once the model is loaded, you can use it to obtain embeddings for DNA sequences:
    
```python
def get_embedding(dna_sequence):
    model, tokenizer, pooler = load_hf_model()
    tokenized_input = tokenizer(dna_sequence, return_tensors="pt", padding=True)
    with torch.no_grad():
        output = model(**tokenized_input)
    embedding = pooler(output.last_hidden_state, tokenized_input.attention_mask)
    return embedding.numpy()

# Example usage
dna_seq = "ATGCGTACGTAGCTAGCTAGC"
embedding = get_embedding(dna_seq)
print("Embedding shape:", embedding.shape)
```

## Training Details

### Dataset
The training data consists of DNA sequences sampled from various chromosomes across species. The dataset covers **approximately 2% of the human genome**, ensuring generalization across different sequences. Reads are generated using **ART MiSeq** simulation, with variations in insertion and deletion rates.

### Training Procedure
- **Self-Supervised Learning:** Contrastive loss-based training.
- **Dynamic Length Sequences:** DNA fragments of length 800-2000 with reads sampled in [150, 500].
- **Noise Augmentation:** 1-5% random base substitutions in 40% of training reads.
- **Batch Size:** 16 with gradient accumulation.

## Evaluation

The model was evaluated against traditional aligners (Bowtie-2) and other Transformer-based baselines (DNABERT-2, HyenaDNA). The evaluation metrics include:
- **Alignment Recall:** >99% for high-quality reads.
- **Cross-Species Transfer:** Successfully aligns sequences from different species, including *Thermus Aquaticus* and *Rattus Norvegicus*.

## Citation

If you use this model, please cite:

```bibtex
@article{10.1093/bioinformatics/btaf041,
    author = {Holur, Pavan and Enevoldsen, K C and Rajesh, Shreyas and Mboning, Lajoyce and Georgiou, Thalia and Bouchard, Louis-S and Pellegrini, Matteo and Roychowdhury, Vwani},
    title = {Embed-Search-Align: DNA Sequence Alignment using Transformer models},
    journal = {Bioinformatics},
    pages = {btaf041},
    year = {2025},
    month = {02},
    issn = {1367-4811},
    doi = {10.1093/bioinformatics/btaf041},
    url = {https://doi.org/10.1093/bioinformatics/btaf041},
    eprint = {https://academic.oup.com/bioinformatics/advance-article-pdf/doi/10.1093/bioinformatics/btaf041/61778456/btaf041.pdf},
}
```

For more details, check the [full paper](https://arxiv.org/abs/2309.11087v6).
