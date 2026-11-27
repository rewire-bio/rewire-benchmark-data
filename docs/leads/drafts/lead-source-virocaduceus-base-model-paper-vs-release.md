# ViroCaduceus: paper says Caduceus-PS, the release uses Caduceus-Ph

Raise at: https://github.com/QIANJINYDX/ViroBench (issues)  
Register entry: `lead-source-virocaduceus-base-model-paper-vs-release`

The ViroBench paper (arXiv 2605.25388v1) describes the architecture ablation as:

> applying the same ViroBland pre-training strategy to DNABERT2 and Caduceus-PS, resulting in ViroDNABERT2 and ViroCaduceus

The released model YDXX/ViroCaduceus at Hugging Face revision 91cee3136ffd64602868a62bdb5f6b061b55e2c9 gives a different base. Its card gives the architecture as "Caduceus-Ph (`d_model=256`, Mamba backbone)", and `get_embedding.py` loads `BASE_MODEL = "kuleshov-group/caduceus-ph_seqlen-131k_d_model-256_n_layer-16"`.

Which base was ViroCaduceus trained from for the results in the paper? The answer changes what the architecture comparison shows.

This was found while compiling an independent database of benchmark results: <record page>
