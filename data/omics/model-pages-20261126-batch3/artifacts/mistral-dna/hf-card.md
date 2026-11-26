---
license: apache-2.0
tags:
- pretrained
- mistral
- DNA
---

# Model Card for Mistral-DNA-v1-138M-hg38 (Mistral for DNA)

The Mistral-DNA-v1-138M-hg38 Large Language Model (LLM) is a pretrained generative DNA sequence model with 138M parameters. 
It is derived from Mixtral-8x7B-v0.1 model, which was simplified for DNA: the number of layers and the hidden size were reduced. 
The model was pretrained using 10kb DNA sequences from the hg38 human genome assembly. 

## Model Architecture

Like Mixtral-8x7B-v0.1, it is a transformer model, with the following architecture choices:
- Grouped-Query Attention
- Sliding-Window Attention
- Byte-fallback BPE tokenizer
- Mixture of Experts

## Load the model from huggingface:

```
import torch
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("RaphaelMourad/Mistral-DNA-v1-138M-hg38", trust_remote_code=True) 
model = AutoModel.from_pretrained("RaphaelMourad/Mistral-DNA-v1-138M-hg38", trust_remote_code=True)
```

## Calculate the embedding of a DNA sequence

```
DNAseq = "TGATGATTGGCGCGGCTAGGATCGGCT"
inputs = tokenizer(DNAseq, return_tensors = 'pt')["input_ids"]
hidden_states = model(inputs)[0] # [1, sequence_length, 256]

# embedding with max pooling
embedding_max = torch.max(hidden_states[0], dim=0)[0]
print(embedding_max.shape) # expect to be 256
```

## Troubleshooting

Ensure you are utilizing a stable version of Transformers, 4.34.0 or newer.

## Notice

Mistral-DNA-v1-138M-hg38 is a pretrained base model for DNA.

## Contact
 
Raphaël Mourad. raphael.mourad@univ-tlse3.fr
