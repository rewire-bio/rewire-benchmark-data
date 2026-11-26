---
license: mit
tags:
- dna
- language-model
- variant-effect-prediction
- biology
- genomics
datasets:
- songlab/genomes-brassicales-balanced-v1
---
# GPN trained on *Arabidopsis thaliana* and 7 other Brassicales
See https://github.com/songlab-cal/gpn for more details.

Basic usage:
```python
import gpn.model
from transformers import AutoModel, AutoModelForMaskedLM

model = AutoModel.from_pretrained("songlab/gpn-brassicales")
# or
model = AutoModelForMaskedLM.from_pretrained("songlab/gpn-brassicales")
```

## Some hparams:
* repeat_weight: 0.1
* lr: 120k at 1e-3 + 30k cosine decay