---
license: mit
datasets:
- MedRAG/textbooks
- MedRAG/pubmed
- MedRAG/statpearls
- mteb/raw_biorxiv
- mteb/raw_medrxiv
- ms_marco
- BMRetriever/biomed_retrieval_dataset
language:
- en
tags:
- medical
- biology
- retrieval
- LLM
---

This model has been finetuned following the approach described in the paper **BMRetriever: Tuning Large Language Models as Better Biomedical Text Retrievers**. The associated GitHub repository is available here https://github.com/ritaranx/BMRetriever.

This model has 7B parameters. See the paper [link](https://arxiv.org/abs/2404.18443) for details.


## Usage

Pre-trained models can be loaded through the HuggingFace transformers library:

```python
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("BMRetriever/BMRetriever-7B") 
tokenizer = AutoTokenizer.from_pretrained("BMRetriever/BMRetriever-7B") 
```

Then embeddings for different sentences can be obtained by doing the following:

```python
import torch
import torch.nn.functional as F

from torch import Tensor
from transformers import AutoTokenizer, AutoModel


def last_token_pool(last_hidden_states: Tensor,
                 attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        embedding = last_hidden[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden.shape[0]
        embedding = last_hidden[torch.arange(batch_size, device=last_hidden.device), sequence_lengths]
    return embedding

def get_detailed_instruct_query(task_description: str, query: str) -> str:
    return f'{task_description}\nQuery: {query}'

def get_detailed_instruct_passage(passage: str) -> str:
    return f'Represent this passage\npassage: {passage}'

# Each query must come with a one-sentence instruction that describes the task
task = 'Given a scientific claim, retrieve documents that support or refute the claim'
queries = [
    get_detailed_instruct_query(task, 'Cis-acting lncRNAs control the expression of genes that are positioned in the vicinity of their transcription sites.'),
    get_detailed_instruct_query(task, 'Forkhead 0 (fox0) transcription factors are involved in apoptosis.')
]

# No need to add instruction for retrieval documents
documents = [
    get_detailed_instruct_passage("Gene regulation by the act of long non-coding RNA transcription Long non-protein-coding RNAs (lncRNAs) are proposed to be the largest transcript class in the mouse and human transcriptomes. Two important questions are whether all lncRNAs are functional and how they could exert a function. Several lncRNAs have been shown to function through their product, but this is not the only possible mode of action. In this review we focus on a role for the process of lncRNA transcription, independent of the lncRNA product, in regulating protein-coding-gene activity in cis. We discuss examples where lncRNA transcription leads to gene silencing or activation, and describe strategies to determine if the lncRNA product or its transcription causes the regulatory effect."),
    get_detailed_instruct_passage("Noncoding transcription at enhancers: general principles and functional models. Mammalian genomes are extensively transcribed outside the borders of protein-coding genes. Genome-wide studies recently demonstrated that cis-regulatory genomic elements implicated in transcriptional control, such as enhancers and locus-control regions, represent major sites of extragenic noncoding transcription. Enhancer-templated transcripts provide a quantitatively small contribution to the total amount of cellular nonribosomal RNA; nevertheless, the possibility that enhancer transcription and the resulting enhancer RNAs may, in some cases, have functional roles, rather than represent mere transcriptional noise at accessible genomic regions, is supported by an increasing amount of experimental data. In this article we review the current knowledge on enhancer transcription and its functional implications.")
]
input_texts = queries + documents

max_length = 512

# Tokenize the input texts
batch_dict = tokenizer(input_texts, max_length=max_length-1, padding=True, truncation=True, return_tensors='pt')

# Important! Adding EOS token at the end
batch_dict['input_ids'] = [input_ids + [tokenizer.eos_token_id] for input_ids in batch_dict['input_ids']]
batch_dict = tokenizer.pad(batch_dict, padding=True, return_attention_mask=True, return_tensors='pt').to("cuda")

model.eval()
with torch.no_grad():
    outputs = model(**batch_dict)
    embeddings = last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
```

Then similarity scores between the different sentences are obtained with a dot product between the embeddings:

```python
scores = (embeddings[:2] @ embeddings[2:].T)
print(scores.tolist())
```

## Citation
If you find this repository helpful, please kindly consider citing the corresponding paper. Thanks!
```
@misc{xu2024bmretriever,
      title={BMRetriever: Tuning Large Language Models as Better Biomedical Text Retrievers}, 
      author={Ran Xu and Wenqi Shi and Yue Yu and Yuchen Zhuang and Yanqiao Zhu and May D. Wang and Joyce C. Ho and Chao Zhang and Carl Yang},
      year={2024},
      eprint={2404.18443},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```