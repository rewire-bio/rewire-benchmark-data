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

# GENERator-eukaryote-1.2b-base model

## **Important Notice**
If you are using GENERator for **sequence generation**, please ensure that the length of each input sequence is a multiple of **6**. This can be achieved by either:  
1. Padding the sequence on the left with `'A'` (**left padding**);  
2. Truncating the sequence from the left (**left truncation**).  

This requirement arises because **GENERator** employs a 6-mer tokenizer. If the input sequence length is not a multiple of **6**, the tokenizer will append an `'<oov>'` (out-of-vocabulary) token to the end of the token sequence. This can result in uninformative subsequent generations, such as repeated `'AAAAAA'`.  

We apologize for any inconvenience this may cause and recommend adhering to the above guidelines to ensure accurate and meaningful generation results.

## Abouts
In this repository, we present GENERator, a generative genomic foundation model featuring a context length of 98k base pairs and 1.2B parameters, trained on an expansive dataset comprising 386 billion base pairs of eukaryotic DNA. Our evaluations demonstrate that the GENERator consistently achieves state-of-the-art performance across a wide spectrum of benchmarks, including [Genomic Benchmarks](https://huggingface.co/datasets/katielink/genomic-benchmarks/tree/main), [NT tasks](https://huggingface.co/datasets/InstaDeepAI/nucleotide_transformer_downstream_tasks_revised), and our newly proposed [Gener tasks](https://huggingface.co/GenerTeam).

Beyond benchmark performance, the GENERator adheres to the central dogma of molecular biology, accurately generating protein-coding DNA sequences that produce proteins structurally analogous to known families. Moreover, the GENERator showcases significant promise in sequence optimization, particularly in the design of enhancer sequences that regulate gene expression during various biological stages, highlighting its potential for a series of biologically significant tasks. Our findings position the GENERator as a vital resource for genomic research and biotechnological advancement.

For more technical details, please refer to our paper [GENERator: A Long-Context Generative Genomic Foundation Model](https://arxiv.org/abs/2502.07272). The code and implementation details are available on Github: [https://github.com/GenerTeam/GENERator](https://github.com/GenerTeam/GENERator).

## How to use
### Example 1: Sequence Generation

```python

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "GenerTeam/GENERator-eukaryote-1.2b-base",
    attn_implementation="flash_attention_2",
    trust_remote_code=True,
    dtype=torch.bfloat16,
).cuda().eval()

tokenizer = AutoTokenizer.from_pretrained(
    "GenerTeam/GENERator-eukaryote-1.2b-base",
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
    "GenerTeam/GENERator-eukaryote-1.2b-base",
    attn_implementation="flash_attention_2",
    trust_remote_code=True,
    dtype=torch.bfloat16,
).cuda().eval()

tokenizer = AutoTokenizer.from_pretrained(
    "GenerTeam/GENERator-eukaryote-1.2b-base",
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
    padding_side="right",
).to("cuda")

with torch.inference_mode():
    outputs = model(**inputs, output_hidden_states=True)

hidden_states = outputs.hidden_states[-1]
attention_mask = inputs["attention_mask"]

# Option 1: Last token embedding
last_token_indices = attention_mask.sum(dim=1) - 1
last_token_embeddings = hidden_states[torch.arange(hidden_states.size(0)), last_token_indices, :]

# Option 2: Mean pooling over all tokens
expanded_mask = attention_mask.unsqueeze(-1).expand(hidden_states.size()).to(torch.float32)
sum_embeddings = torch.sum(hidden_states * expanded_mask, dim=1)
mean_embeddings = sum_embeddings / expanded_mask.sum(dim=1)

# Output
print("Last Token Embeddings:", last_token_embeddings)
print("Mean Pooling Embeddings:", mean_embeddings)

# ============================================================================
# The choice depends on your downstream task requirements
# - Last token embeddings capture more localized gene-level information (e.g., strand, codon phase).
# - Mean pooling embeddings capture species-level information.
# ============================================================================

```

## Citation
```
@misc{wu2025generator,
      title={GENERator: A Long-Context Generative Genomic Foundation Model}, 
      author={Wei Wu and Qiuyi Li and Mingyang Li and Kun Fu and Fuli Feng and Jieping Ye and Hui Xiong and Zheng Wang},
      year={2025},
      eprint={2502.07272},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2502.07272}, 
}
```