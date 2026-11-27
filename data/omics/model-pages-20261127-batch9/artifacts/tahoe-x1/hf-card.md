---
license: apache-2.0
datasets:
- tahoebio/Tahoe-100M
tags:
- biology
- single-cell
- RNA
- chemistry
- tahoebio
- pytorch
---

# Tahoe-x1

Tahoe-x1 is a family of perturbation-trained single-cell foundation models with up to 3 billion parameters, developed by Tahoe Therapeutics. Pretrained on 266 million single-cell transcriptomic profiles including the _Tahoe-100M_ perturbation compendium, Tahoe-x1 achieves state-of-the-art performance on cancer-relevant tasks with 3–30× higher compute efficiency than other cell-state models.

**Quick Links:**
- ✨ [**Blog Post**](https://www.tahoebio.ai/news/tahoe-x1-blog) - Read our announcement
- 📄 [**Preprint**](https://www.biorxiv.org/content/10.1101/2025.10.23.683759v1) - Read our preprint on bioRxiv
- 💻 [**GitHub Repository**](https://github.com/tahoebio/tahoe-x1) - Access the code
- 🎮 [**Interactive Demo**](https://huggingface.co/spaces/tahoebio/tx1-demo) - Try the model with no code required!

## 🤖 Model Sizes

We provide pretrained weights for three model sizes:

- **Tx1-70M**: ~70M parameters
- **Tx1-1B**: ~1.3B parameters
- **Tx1-3B**: ~3B parameters

## 🚀 Quickstart

Load a model directly from Hugging Face and generate cell embeddings:

```python
from tahoe_x1.model import ComposerTX
import scanpy as sc

# Load model from Hugging Face in a single line
# Options: "70m", "1b", or "3b"
model, vocab, model_cfg, collator_cfg = ComposerTX.from_hf(
    repo_id="tahoebio/Tahoe-x1",
    model_size="3b"
)

# Load your single-cell data
adata = sc.read_h5ad("your_data.h5ad")

# Generate embeddings (see tutorials for full example)
# Cell embeddings are stored in adata.obsm
```

### 📦 Installation

To use the models, install the `tahoex` package from GitHub:

```bash
# Clone the repository
git clone https://github.com/tahoebio/tahoe-x1
cd tahoe-x1

# Install using Docker (recommended) or uv
# See installation guide: https://github.com/tahoebio/tahoe-x1#installation
```

**Docker installation** provides better reproducibility and is recommended for the best experience. For native installation, use `uv` or `pip` for dependency management.

Model checkpoints and configs are automatically downloaded from this Hugging Face repository when using `ComposerTX.from_hf()`. Training data is hosted publicly on S3 (s3://tahoe-hackathon-data) and will be downloaded as needed.

## 📚 Tutorials

Please refer to the tutorials in the [GitHub repository](https://github.com/tahoebio/tahoe-x1/tree/main/tutorials) for detailed examples:

| Tutorial | Description | Link |
|----------|-------------|------|
| **Clustering Tutorial** | Cell clustering and UMAP visualization with Tahoe-x1 embeddings | [clustering_tutorial.ipynb](https://github.com/tahoebio/tahoe-x1/blob/main/tutorials/clustering_tutorial.ipynb) |
| **Training Tutorial** | Step-by-step guide to training and fine-tuning Tahoe-x1 models | [training_tutorial.ipynb](https://github.com/tahoebio/tahoe-x1/blob/main/tutorials/training_tutorial.ipynb) |

## 🧬 Generating Cell and Gene Embeddings

### Using Configuration Files

1. Create a configuration file (see `scripts/inference/configs/predict.yaml` in the [GitHub repo](https://github.com/tahoebio/tahoe-x1)):
```yaml
# Key configuration options:
#   - paths.hf_repo_id: Hugging Face repository (tahoebio/Tahoe-x1)
#   - paths.hf_model_size: model size (70m, 1b, or 3b)
#   - paths.adata_output: where to save AnnData output including embeddings
#   - predict.return_gene_embeddings: True (for extracting gene embeddings)
```
See the Clustering Tutorial for a full example of preparing input data and configuration files.
2. Run the embedding script:
```bash
python scripts/inference/predict_embeddings.py path/to/config.yaml

# Optional: override config values via command line
python scripts/inference/predict_embeddings.py path/to/config.yaml \
    --paths.model_name=tx --batch_size=128
```

### Advanced Usage

For memory-efficient gene embedding extraction over large datasets, use the lower-level API:

```python
from tahoex.tasks import get_batch_embeddings

cell_embs, gene_embs = get_batch_embeddings(
    adata=adata,
    model=model,
    vocab=vocab,
    model_cfg=model_cfg,
    collator_cfg=collator_cfg,
    return_gene_embeddings=True
)
```

Cell embeddings are saved to `adata.obsm` and gene embeddings to `adata.varm` (if `return_gene_embeddings=True`).

## 🏋️ Training and Fine-tuning

Tahoe-x1 models can be trained from scratch or fine-tuned on your own data. See the [GitHub repository](https://github.com/tahoebio/tahoe-x1) for detailed instructions.

### Quick Training Example

```bash
# Use the test configuration to train a small model on Tahoe-100M
composer scripts/train.py -f configs/test_config.yaml

# Fine-tune from a pretrained checkpoint
composer scripts/train.py -f configs/finetune_config.yaml \
    --load_path s3://tahoe-hackathon-data/MFM/ckpts/3b/
```

For more details on training infrastructure, datasets, and benchmarks, please visit the [GitHub repository](https://github.com/tahoebio/tahoe-x1).

## 📊 Model Details

### Architecture
- **Base Architecture**: Transformer-based encoder pretrained with masked language modeling (MLM)
- **Training Data**: 266M single-cell profiles from CellxGene, scBaseCamp, and Tahoe-100M
- **Training Infrastructure**: Built on MosaicML Composer with FlashAttention, FSDP, and mixed precision

### Benchmarks

Tahoe-x1 achieves state-of-the-art performance on cancer-relevant tasks:

- **DepMap Essentiality**: Predicting gene dependencies in cancer cell lines
- **MSigDB Hallmarks**: Recovering pathway memberships from gene embeddings
- **Cell-Type Classification**: Classifying cell types across multiple tissues
- **Perturbation Prediction**: Predicting transcriptional responses to perturbations

See the [paper](http://www.tahoebio.ai/news/tahoe-x1) for detailed benchmark results.

## 📄 Citation

If you use Tahoe-x1 in your research, please cite:

```bibtex
@article{gandhi2025tahoe,
  title        = {Tahoe-x1: Scaling Perturbation-Trained Single-Cell Foundation Models to 3 Billion Parameters},
  author       = {Gandhi, Shreshth and Javadi, Farnoosh and Svensson, Valentine and Khan, Umair and Jones, Matthew G. and Yu, Johnny and Merico, Daniele and Goodarzi, Hani and Alidoust, Nima},
  journal      = {bioRxiv},
  year         = {2025},
  doi          = {10.1101/2025.10.23.683759},
  url          = {https://www.biorxiv.org/content/10.1101/2025.10.23.683759v1},
  publisher    = {Cold Spring Harbor Laboratory}
}
```

## 📜 License

Model weights and code are released under the Apache 2.0 license.

## 📧 Contact

For questions or collaboration inquiries, please:
- Open an issue on [GitHub](https://github.com/tahoebio/tahoe-x1) or [HuggingFace](https://huggingface.co/tahoebio/Tahoe-x1)
- Email us at [admin@tahoebio.ai](mailto:admin@tahoebio.ai)

