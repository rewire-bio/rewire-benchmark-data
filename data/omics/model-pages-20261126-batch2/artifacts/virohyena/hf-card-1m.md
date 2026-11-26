---
license: apache-2.0
pipeline_tag: text-generation
---

# ViroHyena

**ViroHyena** is a Hyena-based nucleotide language model pre-trained on the **ViroBlend** corpus, a 216 Mbp mixed pretraining dataset with source-wise stratified sampling to balance human reference, multi-species genomes, and viral in-domain sequences.

The model was introduced as a baseline in the paper [ViroBench: Benchmarking Nucleotide Foundation Models on Viral Genomics Tasks](https://huggingface.co/papers/2605.25388).

- **Repository:** [https://github.com/QIANJINYDX/ViroBench](https://github.com/QIANJINYDX/ViroBench)
- **Project Page:** [https://sii-agi4s.github.io/ViroBench/](https://sii-agi4s.github.io/ViroBench/)

## Model Configurations
| Model | Params | d_model | Layers |
|---|---:|---:|---:|
| ViroHyena-436K | 0.436M | 128 | 2 |
| ViroHyena-1.6M | 1.6M | 256 | 2 |
| ViroHyena-6.6M | 6.6M | 256 | 8 |
| ViroHyena-253M | 253M | 1024 | 20 |

## ViroBench
ViroBench is a comprehensive diagnostic benchmark for viral sequence modeling, designed to evaluate models across two critical dimensions:
- **Understanding Axis**: Taxonomy classification and host prediction.
- **Biosecurity Axis**: Genome modeling and CDS completion (risk-aware generation diagnostics).

## Citation
```bibtex
@article{ye2026virobench,
  title={ViroBench: Benchmarking Nucleotide Foundation Models on Viral Genomics Tasks},
  author={Ye, Dongxin and Hu, Fang and Hu, Han and Hu, Shu and Tan, Yang and Ouyang, Wanli and Li, Stan Z and Cui, Jie and Dong, Nanqing},
  journal={arXiv preprint arXiv:2605.25388},
  year={2026}
}
```
```