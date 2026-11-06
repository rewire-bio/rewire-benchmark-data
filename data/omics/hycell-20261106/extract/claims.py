"""Descriptive claims for HyCell, one number (or none) per claim."""

from assess import BENCHMARK
from evidence import REVIEW
from models import MODEL
from sources import (B, SRC_CITATION, SRC_LICENSE, SRC_NOTICE, SRC_README, SRC_REPO, SRC_REPORT,
                     SRC_SIDECAR, record)

R, M, N, X = [SRC_REPORT], [SRC_README], [SRC_NOTICE], [SRC_SIDECAR]

MODEL_CLAIMS = [
    ("parameters", R + X, "parameter_count", "16.1 million parameters in total (weights.json: "
     "16,108,766).", "Table 1 'Parameters'; weights.json n_parameters"),
    ("transformer-parameters", R, "architecture", "The transformer has 4.8 million parameters.",
     "Table 1 'Parameters'; Section 2.2"),
    ("gene-table-parameters", R, "architecture", "The gene embedding table, shared by encoder and "
     "decoder, has 9.4 million parameters.", "Table 1 'Parameters'"),
    ("layers", R, "architecture", "Six transformer layers.", "Section 2.2; Table 1 'Encoder'"),
    ("width", R, "architecture", "Model width 256.", "Section 2.2; Table 1 'Encoder'"),
    ("heads", R, "architecture", "Four attention heads.", "Section 2.2; Table 1 'Encoder'"),
    ("swiglu-width", R, "architecture", "SwiGLU feed-forward width 704.", "Section 2.2"),
    ("set-encoding", R, "architecture", "A cell is an unordered set of gene tokens with no "
     "positional encoding; bidirectional attention over sets packed without padding.",
     "Sections 2.1 and 2.2"),
    ("embedding-dimension", R + M, "outputs", "The embedding is a 512-dimensional linear projection "
     "of the final [CLS] state.", "Section 2.2; Table 1 'Embedding'"),
    ("decoded-expression", M, "outputs", "The decoder returns expected expression in counts per "
     "10,000 over the genes it is given, using the code for an unknown dataset and donor.",
     "README 'Decode'"),
    ("finetuned-predictions", M, "outputs", "A fine-tuned annotator returns cell-type predictions "
     "for a query.", "README 'Fine-tune'"),
    ("vocabulary", R, "inputs", "The gene vocabulary has 36,495 human genes.",
     "Section 2.1; Table 1 'Input'"),
    ("protein-coding", R, "inputs", "The vocabulary includes the 20,080 protein-coding genes.",
     "Section 2.1"),
    ("expressed-genes", R, "inputs", "Up to 818 expressed genes enter a cell's set.",
     "Section 2.1; Table 1 'Input'"),
    ("measured-zeros", R, "inputs", "Measured zeros are added in number equal to a quarter of the "
     "expressed genes, drawn only from genes measured in at least 90% of training datasets.",
     "Section 2.1"),
    ("max-tokens", R, "inputs", "With the [CLS] token, a set has at most 1,024 tokens.",
     "Section 2.1"),
    ("input-rules", M, "inputs", "Raw integer human counts; genes are matched by Ensembl id, "
     "otherwise by symbol, genes outside the vocabulary are dropped and duplicates summed. All "
     "measured genes must be passed, not a highly-variable subset, because measured zeros are "
     "drawn from the genes present in the input.", "README 'Inputs'"),
    ("training-tokens", R + X, "training", "Trained for 6.4 x 10^10 tokens (weights.json: "
     "64,000,195,776).", "Section 2.5; weights.json training_tokens"),
    ("training-time", R, "training", "Training took 9.9 hours on two NVIDIA H20 GPUs.",
     "Section 2.5; Table 1 'Training'"),
    ("training-steps", R, "training", "246,197 steps of 262,144 tokens.", "Section 2.5"),
    ("cell-presentations", R + X, "training", "About one pass over the training cells: 78.2 million "
     "cell presentations (weights.json: 78,201,849).", "Section 2.5; weights.json"),
    ("census-release", R + N, "training_data", "Human primary cells with raw counts from the CZ "
     "CELLxGENE Census release of 8 November 2025.", "Section 2.5; NOTICE item 1"),
    ("corpus-cells", R, "training_data", "The corpus before removal is 95.0 million cells from 555 "
     "datasets.", "Section 2.5"),
    ("training-cells", R, "training_data", "79.5 million training cells from 532 datasets remain "
     "after removing the evaluation and development data.", "Section 2.5; Table 1 'Data'"),
    ("validation-cells", R, "training_data", "20,000 validation cells.", "Section 2.5"),
    ("development-set", R, "training_evaluation_overlap", "A separate development set of eight "
     "tissues, used for all design choices, was also removed from the corpus; its tissues are not "
     "named.", "Section 2.5"),
    ("dataset-code-entries", R + X, "architecture", "The decoder's dataset code has 555 entries, the "
     "Census count before removal, while training used 532 datasets; the report does not say what "
     "the 23 other entries hold.", "Section 2.3; Table 1 'Conditioning'; weights.json n_datasets"),
    ("donor-code-entries", R, "architecture", "The donor code has 12,533 entries.",
     "Section 2.3; Table 1 'Conditioning'"),
    ("labels-in-training", R, "training", "Batch and donor information is used only in training, "
     "and no cell-type labels are used in pretraining.", "Abstract; Section 2; README 'Method'"),
    ("licence-code", [SRC_LICENSE, SRC_CITATION] + N, "licence", "Apache-2.0, through the repository "
     "LICENSE's default for Tencent-authored materials; NOTICE, CITATION.cff and pyproject.toml say "
     "so, and no package LICENSE exists. No file names the weights explicitly.",
     "Repository LICENSE opening paragraph; NOTICE; CITATION.cff; pyproject.toml"),
    ("licence-data", N, "licence", "The training data and the gene vocabulary drawn from the Census "
     "are CC BY 4.0 and keep their own terms; so do the 512 scIB lung test cells shipped in "
     "tests/data.", "NOTICE items 1 and 2"),
    ("release-date", [SRC_REPO], "release_date", "Announced in the repository README on 2026-11-02.",
     "Repository README.md news entry dated 2026-11-02"),
    ("developer", R, "developer", "Released by Tencent Hunyuan; the report is by the 'Hyra Team'.",
     "Report title page; repository README"),
    ("reproducibility", M, "reproducibility", "On a CUDA GPU with flash-attn the package reproduces "
     "the scored embeddings bit for bit, verified on all seven evaluation atlases (167,804 cells).",
     "README 'Reproducibility'"),
    ("reproducibility-cpu", M, "reproducibility", "Without flash-attn, PyTorch attention gives the "
     "same embeddings up to rounding, with per-cell cosine similarity above 0.9999.",
     "README 'Reproducibility'"),
    ("throughput-gpu", M, "throughput", "About 1,500 cells per second on one NVIDIA H20 for atlases "
     "of 40,000 cells, including reading the file and tokenisation. Approximate and on unnamed "
     "atlases, so not recorded as a result.", "README 'Recorded result', final paragraph"),
    ("throughput-cpu", M, "throughput", "About 13 cells per second on CPU with 16 threads.",
     "README 'Install'"),
    ("finetune-time", R, "training", "Fine-tuning takes one to three minutes on one H20 for 10,000 "
     "to 31,000 reference cells.", "Section 5"),
    ("donor-level-properties", R + M, "scope", "HyCell embeds every cell on its own and is trained "
     "to discount donor and dataset effects; the report says properties shared by all cells of a "
     "donor, such as sex or disease state, are better read from embeddings aggregated per donor or "
     "sample.", "Section 6; README 'Embed'"),
]
