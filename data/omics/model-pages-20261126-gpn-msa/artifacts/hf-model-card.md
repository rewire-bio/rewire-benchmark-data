---
license: mit
tags:
- dna
- language-model
- variant-effect-prediction
- biology
- genomics
datasets:
- songlab/gpn-msa-sapiens-dataset
- songlab/multiz100way
---
# GPN-MSA trained on humans and 89 other vertebrates
For more information check out our [paper](https://www.nature.com/articles/s41587-024-02511-w) and [repository](https://github.com/songlab-cal/gpn).

## Loading
```python
import gpn.model
from transformers import AutoModelForMaskedLM

model = AutoModelForMaskedLM.from_pretrained("songlab/gpn-msa-sapiens")
```

## Hyperparameters
`multiz100way/89/128/64/True/defined.phastCons.percentile-75_0.05_0.001/medium/0.1/42/30000/True/True/True`