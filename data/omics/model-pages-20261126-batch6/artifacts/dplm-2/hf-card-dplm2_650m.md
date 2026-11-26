---
license: apache-2.0
library_name: transformers
tags:
- biology
- protein-language-model
- protein-generation
- protein-structure
- diffusion
- esm
- pytorch
- arxiv:2410.13782
- arxiv:2504.11454
datasets:
- airkingbd/pdb_swissprot
---

# DPLM-2 650M

DPLM-2 is a multimodal diffusion protein language model for jointly modeling,
understanding, and generating protein sequences and structures. It extends the
discrete diffusion protein language model family from sequence-only protein
language modeling to sequence-structure modeling, enabling protein
sequence-structure co-generation and conditional generation tasks such as
folding, inverse folding, and motif scaffolding.

This repository contains the 650M-parameter DPLM-2 checkpoint. For the official
implementation, installation instructions, generation scripts, training
configuration, and evaluation utilities, see the
[bytedance/dplm](https://github.com/bytedance/dplm) repository.

## Model Details

- **Model type:** Multimodal discrete diffusion protein language model
- **Checkpoint:** `airkingbd/dplm2_650m`
- **Architecture:** ESM-style transformer for DPLM-2 (`EsmForDPLM2`)
- **Scale:** 650M parameters, 33 transformer layers, hidden size 1280, 20
  attention heads
- **Vocabulary:** 8,229 tokens, covering amino-acid tokens, structure tokens,
  and special tokens
- **Base initialization:** DPLM-2 training is initialized from a pretrained DPLM
  sequence model to transfer evolutionary knowledge from large-scale sequence
  pretraining
- **Structure tokenizer:** Uses the DPLM structure tokenizer
  (`airkingbd/struct_tokenizer`) for structure-token based modeling and PDB
  reconstruction
- **License:** Apache-2.0
- **Paper:** [DPLM-2: A Multimodal Diffusion Protein Language Model](https://arxiv.org/abs/2410.13782)

## Quick Start

Install the official DPLM codebase and dependencies:

```bash
git clone --recursive https://github.com/bytedance/dplm.git
cd dplm

conda create -n dplm python=3.9 pip
conda activate dplm
bash scripts/install.sh
```

Load the pretrained DPLM-2 checkpoint:

```python
from byprot.models.dplm2 import MultimodalDiffusionProteinLanguageModel as DPLM2

dplm2 = DPLM2.from_pretrained("airkingbd/dplm2_650m").cuda()
dplm2 = dplm2.eval()
```

### Sequence-Structure Co-Generation

The official repository provides `generate_dplm2.py` for co-generation. The
default DPLM-2 sampling strategy is `annealing@2.0:0.1`, which starts with high
sampling temperature for diversity and anneals to a lower temperature for
designability.

```bash
model_name=dplm2_650m
sampling_strategy=annealing@2.0:0.1
output_dir=generation-results/${model_name}

python generate_dplm2.py \
    --model_name airkingbd/${model_name} \
    --task co_generation \
    --sampling_strategy ${sampling_strategy} \
    --num_seqs 50 \
    --max_iter 500 \
    --seq_lens 100 200 300 400 500 \
    --saveto ${output_dir}
```

Generated sequences and structures are saved under
`generation-results/dplm2_650m/co_generation`. The official repository also
includes evaluation utilities for TM-score, RMSD, diversity, and related
structure metrics.

### Forward Folding

DPLM-2 can generate structures conditioned on input amino-acid sequences. The
official scripts use deterministic argmax decoding for 100 diffusion iterations:

```bash
model_name=dplm2_650m
output_dir=generation-results/${model_name}

python generate_dplm2.py \
    --model_name airkingbd/${model_name} \
    --task folding \
    --input_fasta_path data-bin/cameo2022/aatype.fasta \
    --max_iter 100 \
    --unmasking_strategy deterministic \
    --sampling_strategy argmax \
    --saveto ${output_dir}
```

For custom sequences, provide a FASTA file via `--input_fasta_path`.

### Inverse Folding

DPLM-2 can predict amino-acid sequences conditioned on tokenized protein
structures:

```bash
model_name=dplm2_650m
output_dir=generation-results/${model_name}

python generate_dplm2.py \
    --model_name airkingbd/${model_name} \
    --task inverse_folding \
    --input_fasta_path data-bin/cameo2022/struct.fasta \
    --max_iter 100 \
    --unmasking_strategy deterministic \
    --sampling_strategy argmax \
    --saveto ${output_dir}
```

To use a custom structure, first tokenize PDB files with the structure tokenizer:

```bash
python src/byprot/utils/protein/tokenize_pdb.py \
    --input_pdb_folder /path/to/your/input/structure \
    --output_dir /path/to/your/input/structure/tokenized_protein
```

Then pass the generated `struct.fasta` to `generate_dplm2.py`.

### Motif Scaffolding

DPLM-2 supports multimodal motif scaffolding by conditioning on both the
sequence and structure tokens of the motif and co-generating the scaffold
sequence and structure:

```bash
model_name=dplm2_650m
output_dir=./generation-results/${model_name}/motif_scaffold

python run/scaffold_generate_dplm2.py \
    --model_name airkingbd/${model_name} \
    --num_seqs 100 \
    --saveto ${output_dir}
```

See the official repository for required motif data preparation and evaluation
steps.

## Training Data and Training Procedure

DPLM-2 is trained on experimental structures from PDB and AF2-predicted
structures from SwissProt. The authors provide the preprocessed training dataset
on Hugging Face as
[airkingbd/pdb_swissprot](https://huggingface.co/datasets/airkingbd/pdb_swissprot).

The official DPLM repository describes the following training setup for
`dplm2_650m`:

- Initialize from the pretrained DPLM checkpoint `airkingbd/dplm_650m`
- Use a warm-up training strategy for structure data scarcity
- Use LoRA to limit large parameter shifts during multimodal training
- Use `airkingbd/struct_tokenizer` for structure tokenization

The experiment configuration is available in the official repository at
`configs/experiment/dplm2/dplm2_650m.yaml`.

## Evaluation Summary

The DPLM repository reports DPLM-2 results on multiple protein generation and
understanding tasks. Selected 650M-scale results include:

- **Forward folding:** On the reported CAMEO 2022 split, DPLM-2 obtains RMSD
  7.70 and TM-score 0.79; on the reported PDB date split, it obtains RMSD 5.30
  and TM-score 0.83.
- **Motif scaffolding:** DPLM-2 succeeds on 18/24 benchmark cases with average
  success rate 0.29 under the repository's motif consistency and overall
  quality criteria.
- **Representation learning:** DPLM-2 provides structure-aware representations
  and is evaluated on downstream protein prediction tasks including
  thermostability, protein-protein interaction, metal ion binding, EC, GO, and
  DeepLoc benchmarks.

For full tables, baselines, metrics, and evaluation details, refer to the
[DPLM-2 paper](https://arxiv.org/abs/2410.13782), the
[DPLM-2.1 paper](https://arxiv.org/abs/2504.11454), and the official
[bytedance/dplm](https://github.com/bytedance/dplm) repository.

## Citation

If you use this checkpoint, please cite the DPLM and DPLM-2 papers:

```bibtex
@inproceedings{wang2024dplm,
  title={Diffusion Language Models Are Versatile Protein Learners},
  author={Wang, Xinyou and Zheng, Zaixiang and Ye, Fei and Xue, Dongyu and Huang, Shujian and Gu, Quanquan},
  booktitle={International Conference on Machine Learning},
  year={2024}
}

@inproceedings{wang2025dplm2,
  title={DPLM-2: A Multimodal Diffusion Protein Language Model},
  author={Wang, Xinyou and Zheng, Zaixiang and Ye, Fei and Xue, Dongyu and Huang, Shujian and Gu, Quanquan},
  booktitle={International Conference on Learning Representations},
  year={2025}
}

@inproceedings{hsieh2025dplm2_1,
  title={Elucidating the Design Space of Multimodal Protein Language Models},
  author={Hsieh, Cheng-Yen and Wang, Xinyou and Zhang, Daiheng and Xue, Dongyu and Ye, Fei and Huang, Shujian and Zheng, Zaixiang and Gu, Quanquan},
  booktitle={International Conference on Machine Learning},
  year={2025}
}
```

## Acknowledgements

DPLM builds on and acknowledges prior work and resources including ByProt,
EvoDiff, SaProt, ESM, LM-Design, EigenFold, MultiFlow, FrameFlow, and
OpenFold-related structure modeling utilities. See the official repository for
the complete acknowledgements and implementation details.
