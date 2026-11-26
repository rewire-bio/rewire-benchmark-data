---
license: apache-2.0
---

## Model Overview

PlantCaduceus is a DNA language model pre-trained on 16 Angiosperm genomes. Utilizing the [Caduceus](https://caduceus-dna.github.io/) and [Mamba](https://arxiv.org/abs/2312.00752) architectures and a masked language modeling objective, PlantCaduceus is designed to learn evolutionary conservation and DNA sequence grammar from 16 species spanning a history of 160 million years. We have trained a series of PlantCaduceus models with varying parameter sizes:

- **[PlantCaduceus_l20](https://huggingface.co/kuleshov-group/PlantCaduceus_l20)**: 20 layers, 384 hidden size, 20M parameters
- **[PlantCaduceus_l24](https://huggingface.co/kuleshov-group/PlantCaduceus_l24)**: 24 layers, 512 hidden size, 40M parameters
- **[PlantCaduceus_l28](https://huggingface.co/kuleshov-group/PlantCaduceus_l28)**: 28 layers, 768 hidden size, 112M parameters
- **[PlantCaduceus_l32](https://huggingface.co/kuleshov-group/PlantCaduceus_l32)**: 32 layers, 1024 hidden size, 225M parameters

**We would highly recommend using the largest model ([PlantCaduceus_l32](https://huggingface.co/kuleshov-group/PlantCaduceus_l32)) for the zero-shot score estimation.**

## How to use
```python
from transformers import AutoModel, AutoModelForMaskedLM, AutoTokenizer
import torch
model_path = 'kuleshov-group/PlantCaduceus_l32'
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = AutoModelForMaskedLM.from_pretrained(model_path, trust_remote_code=True, device_map=device)
model.eval()
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

sequence = "ATGCGTACGATCGTAG"
encoding = tokenizer.encode_plus(
            sequence,
            return_tensors="pt",
            return_attention_mask=False,
            return_token_type_ids=False
        )
input_ids = encoding["input_ids"].to(device)
with torch.inference_mode():
    outputs = model(input_ids=input_ids, output_hidden_states=True)
```

## Citation
```bibtex
@article{Zhai2025CrossSpecies,
  author       = {Zhai, Jingjing and Gokaslan, Aaron and Schiff, Yoni and Berthel, Alexander and Liu, Z. Y. and Lai, W. L. and Miller, Z. R. and Scheben, Armin and Stitzer, Michelle C. and Romay, Maria C. and Buckler, Edward S. and Kuleshov, Volodymyr},
  title        = {Cross-species modeling of plant genomes at single nucleotide resolution using a pretrained DNA language model},
  journal      = {Proceedings of the National Academy of Sciences},
  year         = {2025},
  volume       = {122},
  number       = {24},
  pages        = {e2421738122},
  doi          = {10.1073/pnas.2421738122},
  url          = {https://doi.org/10.1073/pnas.2421738122}
}
```

## Contact
Jingjing Zhai (jz963@cornell.edu)