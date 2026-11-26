---
license: mit
tags:
- biology
- transformers
- Feature Extraction
- bioRxiv 2025.01.23.634452
---

**This is repository for MutBERT-Human-Ref (no mutation data)**.

## Introduction

This is the official pre-trained model introduced in MutBERT: Probabilistic Genome Representation Improves Genomics Foundation Models.

We sincerely appreciate the Tochka-Al team for the ruRoPEBert implementation, which serves as the base of MutBERT development.

MutBERT is a transformer-based genome foundation model trained only on Human genome.

## Model Source

- Repository: [MutBERT](https://github.com/ai4nucleome/mutBERT)
- Paper: [MutBERT: Probabilistic Genome Representation Improves Genomics Foundation Models](https://www.biorxiv.org/content/10.1101/2025.01.23.634452v1)

## Usage

### Load tokenizer and model

```python
from transformers import AutoTokenizer, AutoModel

model_name = "CompBioDSA/MutBERT-Human-Ref"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
```

The default attention is flash attention("sdpa"). If you want use basic attention, you can replace it with "eager". Please refer to [here](https://huggingface.co/CompBioDSA/MutBERT/blob/main/modeling_mutbert.py#L438).

### Get embeddings

```python
import torch
import torch.nn.functional as F

from transformers import AutoTokenizer, AutoModel

model_name = "CompBioDSA/MutBERT-Human-Ref"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True)

dna = "ATCGGGGCCCATTA"
inputs = tokenizer(dna, return_tensors='pt')["input_ids"]

mut_inputs = F.one_hot(inputs, num_classes=len(tokenizer)).float().to("cpu")  # len(tokenizer) is vocab size
last_hidden_state = model(mut_inputs).last_hidden_state   # [1, sequence_length, 768]
# or: last_hidden_state = model(mut_inputs)[0]        # [1, sequence_length, 768]

# embedding with mean pooling
embedding_mean = torch.mean(last_hidden_state[0], dim=0)
print(embedding_mean.shape) # expect to be 768

# embedding with max pooling
embedding_max = torch.max(last_hidden_state[0], dim=0)[0]
print(embedding_max.shape) # expect to be 768
```

### Using as a Classifier

```python
from transformers import AutoModelForSequenceClassification

model_name = "CompBioDSA/MutBERT-Human-Ref"
model = AutoModelForSequenceClassification.from_pretrained(model_name, trust_remote_code=True, num_labels=2)
```

### With RoPE scaling

Allowed types for RoPE scaling are: `linear` and `dynamic`. To extend the model's context window you need to add rope_scaling parameter.

If you want to scale your model context by 2x:

```python
model_name = "CompBioDSA/MutBERT-Human-Ref"
model = AutoModel.from_pretrained(model_name,
                                  trust_remote_code=True,
                                  rope_scaling={'type': 'dynamic','factor': 2.0}
                                  ) # 2.0 for x2 scaling, 4.0 for x4, etc..
```
