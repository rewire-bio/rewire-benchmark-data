---
license: mit
library_name: pytorch
tags:
- dna
- genomics
- reverse-complement
- equivariance
- tokenization
- biology
---

# MirrorDNA (mirrordna-tiny)

The main model: shared-weight convolutional encoder, symmetric router.

MirrorDNA is a lightweight DNA language model with a learned tokenizer that is exactly equivariant to the reverse
complement: a symmetric boundary router cuts a sequence and its reverse complement into mirror-image chunks for every
value of the parameters, so both strands of the same DNA get the same tokens.
This model is exactly strand-equivariant.

- Paper: *Learning Strand-Equivariant Tokenizations of DNA with MirrorDNA* 
- Code: https://github.com/NIRJHOR-DATTA/MirrorDNA
- Parameters: 2.35M
- Pretraining: masked language modelling on hg38 (Basenji/Enformer training intervals), 1,024-bp windows,
  2^20 bases per step for 10,000 steps (10.5B bases), 15% of bases masked.

## Usage

```python
import json, sys, torch
from huggingface_hub import snapshot_download

path = snapshot_download("nirjhor123/mirrordna-tiny")
sys.path.insert(0, path)
import rcchunk as rk                                   # the model code is stored with the weights

cfg = json.load(open(f"{path}/config.json"))
model = rk.build(cfg["variant"], cfg["model"])
from safetensors.torch import load_file
model.load_state_dict(load_file(f"{path}/model.safetensors"))
model.eval()

x = torch.from_numpy(rk.encode("ACGT" * 256)).long()[None]   # [batch, length]; A,C,G,T,N = 0..4
out = model(x, decode=False)
out["cut"]                                  # chunk boundaries (gap j = between base j and j+1)
model.pooled_features(out)                  # strand-invariant sequence features
model.pooled_features(out, oriented=True)   # orientation-aware features, for strand-dependent labels
```

Fine-tuning scripts, the benchmarks and every analysis of the paper are in the GitHub repository.

## Intended use and limitations

A research model for DNA sequence classification and regression, mainly with fine-tuning. It was pretrained on the
human genome only, with 1-kb windows, and is small; larger models are more accurate on several benchmarks (see the
paper). Strand-invariant features suit labels that do not depend on the strand; for strand-dependent labels
(promoters, splice sites, gene orientation) use the orientation-aware features.

## Citation

```
will be added soon
```

