---
library_name: transformers
license: apache-2.0
---

## Using Caduceus
To use the pre-trained model for masked language modeling, use the following snippet:
```python
from transformers import AutoModelForMaskedLM, AutoTokenizer

# See the `Caduceus` collection page on the hub for list of available models.
model_name = "kuleshov-group/caduceus-ps_seqlen-131k_d_model-256_n_layer-16"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForMaskedLM.from_pretrained(model_name)
```

Alternatively, you can instantiate a model from scratch to train on your own data as follows:
```python
from transformers import AutoConfig, AutoModelForMaskedLM

# Add any config overrides here, see the `config.json` file on the hub for details.
config_overrides = {}
# See the `Caduceus` collection page on the hub for list of available models.
config = AutoConfig.from_pretrained(
 "kuleshov-group/caduceus-ps_seqlen-131k_d_model-256_n_layer-16",
 **config_overrides,
) 
model = AutoModelForMaskedLM.from_config(config)
```

## Model Details

This is the Caduceus-PS model with hidden dimension 256 and 16 MambaDNA layers.
This model is reverse complement (RC) equivariant and thus no RC data augmentation is required when training this model, either during pre-training or for downstream fine-tuning.
Note that the model hidden state will be **twice** that of a non-RC equivariant counterpart.
For downstream task training and inference, and to ensure RC **invariant** outputs at downstream time, one can either run the downstream model on the hidden state and its RC or one can take the hidden state and its RC and average them before passing to the downstream model.
To RC the hidden states, one can use: `hidden_states.flip(dim=(-2, -1))` which will flip along the sequence lenght and channel dimensions.

This model was pre-trained on the human reference genome with sequence length 131,072 for 50k steps (each step contained ~1M base pairs / tokens).

For more details, please see our paper: [Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling](https://arxiv.org/abs/2403.03234).

## Citation

Please cite our work using the bibtex below:

**BibTeX:**
```
@article{schiff2024caduceus,
  title={Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling},
  author={Schiff, Yair and Kao, Chia-Hsiang and Gokaslan, Aaron and Dao, Tri and Gu, Albert and Kuleshov, Volodymyr},
  journal={arXiv preprint arXiv:2403.03234},
  year={2024}
}
```

## Model Card Contact

Yair Schiff (yzs2@cornell.edu)