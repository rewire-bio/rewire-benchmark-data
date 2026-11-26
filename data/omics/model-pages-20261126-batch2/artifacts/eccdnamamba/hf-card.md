---
license: apache-2.0
tags:
- medical
- biology
---



# eccDNAMamba  
**A Pre-Trained Model for Ultra-Long eccDNA Sequence Analysis**

---

### Model Overview
**eccDNAMamba** is a **bidirectional state-space model (SSM)** designed for efficient and topology-aware modeling of **extrachromosomal circular DNA (eccDNA)**.  
By combining **forward and reverse Mamba-2 encoders**, **motif-level Byte Pair Encoding (BPE)**, and a lightweight **head–tail circular augmentation**, it captures wrap-around dependencies in ultra-long (10–200 kbp) genomic sequences while maintaining linear-time scalability.  
The model provides strong performance across cancer-associated eccDNA prediction, copy-number level estimation, and real vs. pseudo-eccDNA discrimination tasks.

---

### Quick Start
```python
from transformers import AutoTokenizer, AutoModelForMaskedLM

tokenizer = AutoTokenizer.from_pretrained("eccdna/eccDNAMamba-1M")
model = AutoModelForMaskedLM.from_pretrained("eccdna/eccDNAMamba-1M")

sequence = "ATGCGTACGTTAGCGTACGT"
inputs = tokenizer(sequence, return_tensors="pt")
outputs = model(**inputs)

# Access logits or reconstruct masked spans
logits = outputs.logits
```

---

### Citation
```python
@inproceedings{
liu2025eccdnamamba,
title={ecc{DNAM}amba: A Pre-Trained Model for Ultra-Long ecc{DNA} Sequence Analysis},
author={Zhenke Liu and Jien Li and Ziqi Zhang},
booktitle={ICML 2025 Generative AI and Biology (GenBio) Workshop},
year={2025},
url={https://openreview.net/forum?id=56xKN7KJjy}
}