"""Descriptive claims for HyPLM-Flash. Per the coordinator's ruling 11, each claim
holds one number (or none) under its own locator."""

from core import REVIEW
from entities import B, BENCHMARK, MODEL, SRC_LICENCE, SRC_README, SRC_REPO, SRC_REPORT, record

ENGINE = [f"{B}-source-engine-model", f"{B}-source-engine-graphs"]
R, M, L, P = [SRC_REPORT], [SRC_README], [SRC_LICENCE], [SRC_REPO]

# (slug, subject, sources, field, value, locator)
MODEL_CLAIMS = [
    ("parameters", R, "parameter_count", "652 million parameters in total (650M class).",
     "Section 2.1, final sentence"),
    ("layers", R, "architecture", "32 Transformer layers.", "Section 2.1, final sentence"),
    ("width", R, "architecture", "Model width 1,280.", "Section 2.1, final sentence"),
    ("heads", R, "architecture", "20 attention heads.", "Section 2.1, final sentence"),
    ("swiglu-width", R, "architecture", "SwiGLU feed-forward width 3,584.",
     "Section 2.1, final sentence"),
    ("max-length", R, "input_length", "Reads proteins of up to 8,190 residues in a single window.",
     "Section 2.1, final sentence; README 'Usage'"),
    ("vocabulary", R, "architecture", "Uses the 33-token alphabet of ESM-2 and a RoBERTa-style "
     "output head, so it can replace ESM-2 in existing pipelines.", "Section 2.1; Figure 2"),
    ("block-design", R, "architecture", "Bidirectional Transformer encoder with RMSNorm "
     "pre-normalisation, rotary position embeddings, per-head query-key normalisation and SwiGLU "
     "feed-forward layers, trained by masked language modelling.", "Section 2.1"),
    ("inputs", M, "inputs", "Protein amino-acid sequences, optionally with positions to mask. "
     "Input is upper-cased, whitespace removed and J converted to X; invalid characters raise an "
     "error.", "README 'Usage'"),
    ("embedding-dimension", M, "outputs", "Per-residue embeddings of dimension 1,280, or one pooled "
     "1,280-dimensional vector per protein, returned as CPU FP32 tensors without the special "
     "tokens.", "README 'Usage', encode examples"),
    ("logits", M, "outputs", "Masked-language-model logits of shape [L, 33] per sequence, for "
     "example for zero-shot masked-marginal mutation scoring.", "README 'Usage', logits example"),
    ("licence", L, "licence", "MIT. The LICENSE adds that third-party model weights, datasets and "
     "compatibility implementations retain their own licenses and attribution.",
     "AI4Science/hyplm_flash/LICENSE"),
    ("weights-size-install", M, "availability", "README 'Installation' gives the FP32 weights as "
     "2.6 GB, released as two shards in the repository's GitHub Releases.",
     "README 'Installation'"),
    ("weights-size-layout", M, "availability", "README 'Layout' gives the FP32 weights as 2.61 GB "
     "of safetensors fetched from the GitHub Release.", "README 'Layout'"),
    ("hardware", M, "availability", "Needs a CUDA GPU and Python 3.10+; Hopper GPUs such as the H20 "
     "or H100 are recommended. Uses FlashAttention-3 when installed, otherwise FlashAttention-2.",
     "README 'Installation'"),
    ("release-date", P, "release_date", "Announced in the repository README's news list on "
     "2026-11-02, with HyInv, as one of two protein models released with weights and code.",
     "Repository README.md news entry dated 2026-11-02"),
    ("developer", R, "developer", "Trained by Hyra 2.0, Tencent Hunyuan's research agent. Authors "
     "Haowei Lin, Cai Zhou and Xiangxin Zhou, all affiliated with Tencent Hunyuan.",
     "Abstract; 'Author Information'"),
    ("training-tokens", R, "training", "Trained on 726 billion tokens in total.",
     "Section 2.2 'Training compute'"),
    ("training-flops", R, "training", "2.8 x 10^21 training FLOPs by the 6ND estimate.",
     "Section 2.2 'Training compute'; Table 1"),
    ("data-ratio-esm2", R, "training", "0.73 times the training data of ESM-2 650M.",
     "Section 2.2 'Training compute'"),
    ("data-ratio-e1", R, "training", "5.5 times less training data than E1-600M (4.0 trillion "
     "tokens).", "Section 2.2 'Training compute'"),
    ("data-ratio-esmc", R, "training", "8.5 times less training data than ESM C 600M (6.2 trillion "
     "tokens).", "Section 2.2 'Training compute'"),
    ("pretraining-stage", R, "training", "Pretraining covers 713 billion tokens on crops of up to "
     "1,022 residues.", "Section 2.2 'Training stages'"),
    ("second-stage", R, "training", "A second stage of 13 billion tokens extends crops to 8,190 "
     "residues and adds auxiliary structure objectives used only during training.",
     "Section 2.2 'Training stages'"),
    ("structure-chains", R, "training_data", "The auxiliary structure objectives use 1.6 million "
     "chains with experimental or predicted structures.", "Section 2.2 'Training stages'"),
    ("corpus-sequences", R, "training_data", "The corpus holds 2.6 billion sequences (659 billion "
     "residues) from UniRef90 and UniRef50, MGnify90, UniParc and JGI IMG, kept at 30 to 8,192 "
     "residues.", "Section 2.2 'Data'"),
    ("metagenomic-share", R, "training_data", "Metagenomic and archival sequences supply about 80% "
     "of the training tokens.", "Section 2.2 'Data'"),
    ("overlap-exact", R, "training_evaluation_overlap", "Benchmark sequences used during "
     "development were removed from the corpus by exact match, including all ProteinGym wild types "
     "and variants. The report does not list which benchmarks, and exact-match removal does not "
     "remove near-identical homologs.", "Section 2.2 'Data'"),
    ("overlap-structures", R, "training_evaluation_overlap", "Structure chains with an MMseqs2 hit "
     "(E-value at most 10^-3, identity at least 30%) to the structure and likelihood test proteins "
     "or a ProteinGym wild type were removed before training.", "Section 2.2 'Training stages'"),
]
