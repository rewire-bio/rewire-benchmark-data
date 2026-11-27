# GVP hidden size: 100 scalar channels in the paper, 256 in the released configs

Raise at: https://github.com/DeepGraphLearning/S3F (issues)  
Register entry: `lead-source-s2f-gvp-hidden-size-paper-vs-config`

The S3F paper (arXiv 2412.01108v1) describes the structure encoder as:

> we utilize L = 5 layers of GVP, with d′ = 16 vector and d = 100 scalar hidden representations.

The evaluation configs in the repository at commit 2efab6adfb27b8b36f99059a355125ce181fdaf0, which are used with the released checkpoints, set `node_h_dim: [256, 16]` for both S2F (`config/evaluate/s2f.yaml`) and S3F (`config/evaluate/s3f.yaml`).

Which hidden size do the released checkpoints use, and which produced the parameter counts in the paper's Table 1?

This was found while compiling an independent database of benchmark results: <record page>
