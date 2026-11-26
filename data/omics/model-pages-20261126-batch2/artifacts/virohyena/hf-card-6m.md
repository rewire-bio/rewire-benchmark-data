---
license: apache-2.0
pipeline_tag: text-generation
tags:
- biology
- genomics
- nucleotide
---

# ViroHyena-6.6M

**ViroHyena** is a Hyena-based nucleotide language model introduced in the paper [ViroBench: Benchmarking Nucleotide Foundation Models on Viral Genomics Tasks](https://huggingface.co/papers/2605.25388). 

This specific checkpoint is the **6.6M parameter** version. It was pre-trained on the **ViroBlend** corpus, a 216 Mbp mixed pretraining dataset using source-wise stratified sampling to balance human reference, multi-species genomes, and viral in-domain sequences.

## Resources
- **Paper:** [ViroBench: Benchmarking Nucleotide Foundation Models on Viral Genomics Tasks](https://huggingface.co/papers/2605.25388)
- **Repository:** [GitHub - ViroBench](https://github.com/QIANJINYDX/ViroBench)

## Model Configurations
| Model | Params | d_model | Layers |
|---|---:|---:|---:|
| ViroHyena-436K | 0.436M | 128 | 2 |
| ViroHyena-1.6M | 1.6M | 256 | 2 |
| **ViroHyena-6.6M** | **6.6M** | **256** | **8** |
| ViroHyena-253M | 253M | 1024 | 20 |

## Biosecurity & Responsible Use
This model was developed for biological understanding and measurement research. As noted in the project documentation:
- **Do NOT** use this model to design, optimize, synthesize, or operationalize harmful biological agents.
- Follow all applicable laws, institutional policies, and biosafety regulations.
- If you release checkpoints or generation outputs, consider controlled access and red-teaming protocols.

## Citation
```bibtex
@article{ye2026virobench,
  title={ViroBench: Benchmarking Nucleotide Foundation Models on Viral Genomics Tasks},
  author={Ye, Dongxin and Hu, Fang and Hu, Han and Hu, Shu and Tan, Yang and Ouyang, Wanli and Li, Stan Z and Cui, Jie and Dong, Nanqing},
  journal={arXiv preprint arXiv:2605.25388},
  year={2026}
}
```