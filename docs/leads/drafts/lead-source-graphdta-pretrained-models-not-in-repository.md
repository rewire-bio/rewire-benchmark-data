# Pre-trained GraphDTA models: where are they?

Raise at: https://github.com/thinng/GraphDTA (issues)  
Register entry: `lead-source-graphdta-pretrained-models-not-in-repository`

The GraphDTA paper (Bioinformatics, doi 10.1093/bioinformatics/btaa921) states in its abstract, under Availability of implementation:

> Related data, pre-trained models and source code are publicly available at https://github.com/thinng/GraphDTA.

The repository tree at commit 6162245c6776684b391d30610850fe7077478435, read through the GitHub API with `"truncated":false`, holds the data folds, the training scripts, `supplement.pdf` and four model definitions in `models/` (`gat.py`, `gat_gcn.py`, `gcn.py`, `ginconv.py`). It holds no `.model` file or other trained weights.

Are the pre-trained models published somewhere else, or were they removed from the repository at some point? A link would let others check the published figures without retraining.

This was found while compiling an independent database of benchmark results: <record page>
