# LncRFM

RNA representation learning with structure-aware pretraining and pair-aware
bidirectional fusion.

## Installation

```bash
conda env create -f environment.yml
conda activate lncrfm
pip install --no-build-isolation causal-conv1d==1.4.0 mamba-ssm==2.2.2
pip install -e .
```

The environment uses Python 3.10 and PyTorch with CUDA 11.8. Building the
state-space kernels requires a matching CUDA toolkit.

## Weights and data

| Asset | Format |
|---|---|
| [LncRFM pretrained weights](https://zenodo.org/records/24356997) | Safetensors, tokenizer and model configuration |
| [LncCorpus](https://zenodo.org/records/24344559) | Parquet: `seq`, `connects` |
| [LncBench](https://zenodo.org/records/24345986) | Parquet: `sequence`, `label`, `split` |

Place the extracted weights in `checkpoints/lncrfm_pretrained/`.
LncCorpus structure partners use 1-based nucleotide indices, with 0 for an
unpaired base and the original leading/trailing boundary slots.

## Model loading and inference

```python
from pathlib import Path
import json
import torch
from lncrfm import get_lncrfm, get_tokenizer

checkpoint = Path("checkpoints/lncrfm_pretrained")
options = json.loads((checkpoint / "model_config.json").read_text())["factory_kwargs"]
tokenizer = get_tokenizer(
    tokenizer_file=str(checkpoint / "tokenizer.json"),
    max_length=options["max_length"],
)
model = get_lncrfm(
    **options,
    tokenizer=tokenizer,
    from_pretrained=str(checkpoint),
    dtype=torch.float32,
    device="cuda",
).eval()

inputs = tokenizer("[CLS] A U G [MASK] C [SEP]", return_tensors="pt").to("cuda")
with torch.no_grad():
    outputs = model(**inputs)
print(outputs.logits.argmax(dim=-1))
```

## Model test

```bash
python test_model.py --checkpoint checkpoints/lncrfm_pretrained
python test_model.py --checkpoint checkpoints/lncrfm_pretrained --device cuda --train-step
```

The CPU case checks architecture and strict checkpoint loading. The CUDA case
also checks the pretrained forward pass and one training step with synthetic
RNA. It does not save updated weights or use real datasets.

## Pretraining

```bash
LNCRFM_CORPUS_ROOT=/path/to/LncCorpus NPROC_PER_NODE=4 bash pretrain.sh
```

The launcher uses FP32, per-device batch size 20, gradient accumulation 2,
learning rate 2e-6 and 300,000 steps. It reads the released Parquet shards
directly and retains their training/held-out membership. `python main.py --help` lists the options.

## Downstream learning

Task entry points are `LncDowntask/finetune_*.py`. Pass a released Parquet file
with `--data_file`. The reader uses `sequence`, `label` and `split` directly;
`validation` maps to `val`. Sample order and split membership are preserved.
The model architecture and tokenizer are read from the checkpoint directory.

```bash
python LncDowntask/finetune_iloclnc_reference.py \
  --model_backend lncrfm \
  --finetune_scheme adapter --freeze_encoder --no_eval_test_each_epoch \
  --from_pretrained checkpoints/lncrfm_pretrained \
  --data_file LncBench/iLoc-lncRNA_D1.parquet --output_dir outputs/iloc
```

| Dataset | Training entry point (`LncDowntask/`) |
|---|---|
| lnc_binary | `finetune_lnc_binary_reference.py` |
| RNAErnie-lncRNA | `finetune_lncrna_hm_reference.py` |
| iLoc-lncRNA_D1 / D2 | `finetune_iloclnc_reference.py` |
| lncATLAS-Localization | `finetune_lncatlas_binary_reference.py` |
| lncATLAS-RCI | `finetune_lncatlas_rci_reference.py` |
| Disease | `finetune_lncbook_disease_reference.py` |
| Expression | `finetune_lncbook_function5_reference.py` |
| POSTAR3-UPF1 | `finetune_postar3_top10_binary_reference.py` |
| mRNA-DMS | `finetune_human_mrna_dms.py` |
| mRNA-Structure | `finetune_human_mrna_structure.py` |
| 5UTR-MRL | `finetune_5utr_mrl_reference.py` |
| RiNALMo-Splice | `finetune_splice_site_reference.py --task_name donor` or `acceptor` |

Expression labels follow this order: normal tissue/cell line, organ development,
preimplantation embryo, cell differentiation, subcellular localization.
Splice labels contain `site` and `value`; the entry point uses the requested site.
DMS labels are per-base values, and structure labels are base-pair index lists.
RNAChallenge and lncRNA-Structure contain test data only and are used with a
trained task head. All datasets can also be read directly:

```python
from LncDowntask.lncbench_data import load_lncbench

splits = load_lncbench("LncBench/RNAChallenge.parquet")
test_records = splits["test"]
```

Set `LNCRFM_DATA_ROOT` for task data and `LNCRFM_CHECKPOINT` for weights.
Each entry point lists its training and evaluation options with `--help`.

## Comparison methods

[RNA-FM](https://github.com/ml4bio/RNA-FM),
[structRFM](https://huggingface.co/heqin-zhu/structRFM),
[RNAErnie](https://huggingface.co/multimolecule/rnaernie),
[SpliceBERT](https://huggingface.co/multimolecule/splicebert),
[UTR-LM](https://huggingface.co/multimolecule/utrlm-te_el),
[RiNALMo micro](https://huggingface.co/multimolecule/rinalmo-micro) and
[LncRNA-BERT](https://github.com/luukromeijn/lncRNA-Py).

## Acknowledgements and related work

State-space kernels and block utilities build on
[Mamba](https://github.com/state-spaces/mamba). The bidirectional backbone
follows the [Hydra](https://github.com/goombalab/hydra) /
[HydraRNA](https://github.com/GuipengLi/HydraRNA) design. The structure-aware
masking collator is adapted from
[RNAErnie2](https://github.com/CatIIIIIIII/RNAErnie2). Tokenization and training
use [Hugging Face](https://github.com/huggingface/transformers) libraries.

Hydra / HydraRNA: Copyright (c) 2025 goombalab; Copyright (c) 2025 GPL.
License terms: [LICENSE](LICENSE).
