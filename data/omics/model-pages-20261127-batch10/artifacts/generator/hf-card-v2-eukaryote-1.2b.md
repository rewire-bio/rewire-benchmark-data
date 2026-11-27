---
library_name: transformers
license: mit
pipeline_tag: text-generation
tags:
- biology
- genomics
- long-context
arxiv: 2502.07272
---

# GENERator-v2-eukaryote-1.2b-base model

## **Important Notice**
If you are using **GENERator** for sequence generation, please ensure that the length of each input sequence is a multiple of **6**. This can be achieved by either:  
1. Padding the sequence on the left with `'A'` (**left padding**);  
2. Truncating the sequence from the left (**left truncation**).  

This requirement arises because **GENERator** employs a 6-mer tokenizer. If the input sequence length is not a multiple of **6**, the tokenizer will append an `'<oov>'` (out-of-vocabulary) token to the end of the token sequence. This can result in uninformative subsequent generations, such as repeated `'AAAAAA'`.  

We apologize for any inconvenience this may cause and recommend adhering to the above guidelines to ensure accurate and meaningful generation results.

## Abouts
In this repository, we present GENERator-v2, a generative genomic foundation with enhanced performance in eukaryotic domain. More technical details are provided in the GENERator-v2 [technical report](https://www.biorxiv.org/content/10.64898/2026.01.27.702015v1).

Python scripts for downstream analysis are available on Github: [https://github.com/GenerTeam/GENERator](https://github.com/GenerTeam/GENERator).

## How to use
### Example 1: Sequence Generation

```python

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "GenerTeam/GENERator-v2-eukaryote-1.2b-base",
    attn_implementation="flash_attention_2",
    trust_remote_code=True,
    dtype=torch.bfloat16,
).cuda().eval()

tokenizer = AutoTokenizer.from_pretrained(
    "GenerTeam/GENERator-v2-eukaryote-1.2b-base",
    trust_remote_code=True,
)

# Define input sequences.
sequences = [
    "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG",
    "ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT"
]

# Truncate each sequence to the nearest multiple of 6
processed_sequences = ["<s>" + seq[len(seq)%6:] for seq in sequences]

# Tokenize the sequences
inputs = tokenizer(
    processed_sequences,
    add_special_tokens=False,
    return_tensors="pt",
    padding=True,
    padding_side="left",
).to("cuda")

# Generate the sequences
with torch.inference_mode():
    outputs = model.generate(**inputs, max_new_tokens=32, do_sample=False)

# Decode the generated sequences
decoded_sequences = tokenizer.batch_decode(outputs, skip_special_tokens=True)

# Print the decoded sequences
print(decoded_sequences)
```

### Example 2: Embedding Extraction

```python

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "GenerTeam/GENERator-v2-eukaryote-1.2b-base",
    attn_implementation="flash_attention_2",
    trust_remote_code=True,
    dtype=torch.bfloat16,
).cuda().eval()

tokenizer = AutoTokenizer.from_pretrained(
    "GenerTeam/GENERator-v2-eukaryote-1.2b-base",
    trust_remote_code=True,
)

# Define input sequences.
sequences = [
    "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG",
    "ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT"
]

# Truncate each sequence to the nearest multiple of 6
processed_sequences = ["<s>" + seq[len(seq)%6:] + "<s>" for seq in sequences]

# Tokenize the sequences
inputs = tokenizer(
    processed_sequences,
    add_special_tokens=False,
    return_tensors="pt",
    padding=True,
    padding_side="right",
).to("cuda")

with torch.inference_mode():
    outputs = model(**inputs, output_hidden_states=True)

hidden_states = outputs.hidden_states[-1]
attention_mask = inputs["attention_mask"]

# Option 1: Separator embedding (last <s> token)
separator_indices = attention_mask.sum(dim=1) - 1
separator_embeddings = hidden_states[torch.arange(hidden_states.size(0)), separator_indices, :]

# Option 2: Content token embedding (last DNA token)
last_dna_indices = attention_mask.sum(dim=1) - 2
content_embeddings = hidden_states[torch.arange(hidden_states.size(0)), last_dna_indices, :]

# Option 3: Mean pooling over all tokens
expanded_mask = attention_mask.unsqueeze(-1).expand(hidden_states.size()).to(torch.float32)
sum_embeddings = torch.sum(hidden_states * expanded_mask, dim=1)
mean_embeddings = sum_embeddings / expanded_mask.sum(dim=1)

# Output
print("Separator (Last <s> Token) Embeddings:", separator_embeddings)
print("Content (Last DNA Token) Embeddings:", content_embeddings)
print("Mean Pooling Embeddings:", mean_embeddings)

# ============================================================================
# The choice depends on your downstream task requirements
# - Separator embeddings and mean pooling embeddings capture species-level information.
# - Content embeddings capture more localized gene-level information (e.g., strand, codon phase).
# - More details are provided in GENERator-v2 tech report.
# ============================================================================

```

### Example 3: Sequence Scoring

```python

import torch
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "GenerTeam/GENERator-v2-eukaryote-1.2b-base",
    attn_implementation="flash_attention_2",
    trust_remote_code=True,
    dtype=torch.bfloat16,
).cuda().eval()

# Sequence length does not need to be a multiple of 6
sequences = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGAT"

with torch.no_grad():
    bp_probs, actual_probs = model.score_sequence(sequences)

print(bp_probs.shape)      # [sequence_length, 4]
print(actual_probs.shape)  # [sequence_length]

# bp_probs[i] = [P(A), P(T), P(C), P(G)] at position i (i ranges 0 ... len(seq)-1)
# actual_probs[i] = probability assigned to the actual base in the input sequence

# model.score_sequence() can also take a list of multiple inputs 
reference = "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
perturbed = "ATCGATCGATCGATCGATCGATCGCAGCAGCAGCAGATCG"

with torch.no_grad():
    bp_probs, actual_probs = model.score_sequence([reference, perturbed])

scores = [torch.log(p.clamp_min(1e-12)).mean().item() for p in actual_probs]

print(f"Log-Likelihood of Reference Sequence: {scores[0]:.4f}")
print(f"Log-Likelihood of Perturbed Sequence: {scores[1]:.4f}")
print(f"Reference is preferred: {scores[0] > scores[1]}")

```

## Citation
```
@article {li2026generator2,
    author = {Li, Qiuyi and Zhan, Zhihao and Feng, Shikun and Zhu, Yiheng and He, Yuan and Wu, Wei and Shi, Zhenghang and Wang, Shengjie and Hu, Zongyong and Yang, Zhao and Li, Jiaoyang and Tang, Jian and Liu, Haiguang and Qin, Tao},
    title = {GENERator-v2: Reconciling Coarse Tokenization with Single-Nucleotide Resolution in Genomic Language Modeling},
    elocation-id = {2026.01.27.702015},
    year = {2026},
    doi = {10.64898/2026.01.27.702015},
    publisher = {Cold Spring Harbor Laboratory},
    URL = {https://www.biorxiv.org/content/early/2026/05/04/2026.01.27.702015},
    journal = {bioRxiv}
}

@article{wu2025generator,
  title={GENERator: a long-context generative genomic foundation model},
  author={Wu, Wei and Li, Qiuyi and Li, Mingyang and Fu, Kun and Feng, Fuli and Ye, Jieping and Xiong, Hui and Wang, Zheng},
  journal={arXiv preprint arXiv:2502.07272},
  year={2025}
}

```