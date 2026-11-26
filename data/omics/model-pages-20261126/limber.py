"""Add a profile and a run guide to the LIMBER model record. Run from the data repo root."""
import json, sys
RID = "intake-384-20261124-model-limber"
GH = "intake-384-20261124-source-github-ziyaow1010-limber-github"
HF = "intake-384-20261124-source-ziyao1010-limber-hugging-face"
PAPER = "intake-384-20261124-source-limber-a-hybrid-rna-foundation-model-for-predicting-and-unde"
README = "README.md at commit 72a328a"
def ev(locator, ids=(GH,)): return {"source_ids": list(ids), "source_locator": locator}
profile = {
  "summary": "LIMBER is an RNA language model for non-coding RNA. It reads an RNA sequence one nucleotide at a time and returns per-nucleotide embeddings and masked-token predictions, which the authors use for secondary-structure prediction, RNA family classification and mutational fitness scoring.",
  "summary_source_ids": [GH, PAPER],
  "summary_source_locator": f"{README}: Overview and Quick start; preprint abstract",
  "sections": [
    {"title": "How it works",
     "body": "LIMBER stacks two kinds of layer in a repeating Transformer, Transformer, Mamba pattern. The Transformer layers use bidirectional self-attention, which relates any two positions directly; the authors link this to the long-range coupling that base pairing leaves in a sequence. The Mamba layers are selective state-space layers that process the sequence in order. The model is pretrained by masked language modelling: 15% of nucleotide positions are selected, and of those 80% are replaced by a mask token, 10% by a random nucleotide and 10% left unchanged. Tokenisation is one token per nucleotide over a 10-token vocabulary; T is mapped to U and any other symbol to N.",
     **ev(f"{README}: Overview; Model zoo; Tokenization; Pretraining")},
    {"title": "Versions and reproducibility",
     "body": "Five LIMBER sizes are released, from 10.2M to 664.3M parameters, with size-matched pure-Transformer and pure-Mamba models trained on the same data. The README counts 25 checkpoints in one Hugging Face repository, one subfolder per model, including data-fraction, training-epoch and shape ablations. A result should name the subfolder it used: LIMBER-macro, LIMBER-meso and LIMBER-nano differ in depth and width, not only in size. The Hugging Face repository was at revision d2d6ae6 when read on 2026-11-26.",
     **ev(f"{README}: Model zoo; Hugging Face file listing at revision d2d6ae6", (GH, HF))},
    {"title": "What the authors report",
     "body": "The authors fine-tuned LIMBER and each baseline themselves under one protocol. They report a median flexible F1 of 0.895 on bpRNA TS0 and 0.816 on Rivas TestSetB for LIMBER-macro, and 99.2% accuracy on the 13-class nRC benchmark. On IRES identification and 5'UTR mean ribosome load, RiNALMo-giga scores higher than LIMBER-macro on most metrics in the same tables. These are author-reported figures and are not yet recorded as results in this database.",
     **ev(f"{README}: Results tables for secondary structure, nRC, IRES and mean ribosome load")},
  ],
  "facts": [
    {"label": "Model type", "value": "RNA masked language model (encoder only)", "status": "source_checked", **ev(f"{README}: Overview; Pretraining")},
    {"label": "Architecture", "value": "Hybrid encoder that interleaves bidirectional Transformer layers and Mamba state-space layers in a repeating Transformer, Transformer, Mamba pattern. Mamba layers use a 16-dimensional state, convolution width 4 and expansion factor 4.", "status": "source_checked", **ev(f"{README}: Overview; Model zoo")},
    {"label": "Inputs", "value": "RNA sequence, one token per nucleotide (A, U, C, G, N). DNA input is accepted with T mapped to U.", "status": "source_checked", **ev(f"{README}: Tokenization")},
    {"label": "Outputs", "value": "Masked-token logits over the nucleotide vocabulary and per-nucleotide embeddings (1,280 dimensions for LIMBER-macro); the first position is a pooled sequence representation.", "status": "source_checked", **ev(f"{README}: Quick start")},
    {"label": "Parameters", "value": "LIMBER-macro 664.3M (33 layers, hidden size 1,280); LIMBER-meso 303.6M (15 layers, 1,280); LIMBER-nano 91.7M (18 layers, 640); LIMBER-50M 49.3M; LIMBER-10M 10.2M.", "status": "source_checked", **ev(f"{README}: Model zoo table")},
    {"label": "Training data", "value": "RNAcentral, deduplicated by exact sequence to 40,498,819 sequences, with a fixed held-out validation set. Sequences longer than 1,022 nucleotides are randomly cropped each epoch.", "status": "source_checked", **ev(f"{README}: Pretraining, Corpus")},
    {"label": "Known versions", "value": "LIMBER-macro, LIMBER-meso, LIMBER-nano, LIMBER-50M and LIMBER-10M, plus ablation checkpoints (corpus fractions, intermediate epochs, shape and convolution-width variants) and Transformer-only and Mamba-only controls at 100M, 300M and 650M.", "status": "source_checked", **ev(f"{README}: Model zoo; Hugging Face file listing at revision d2d6ae6", (GH, HF))},
    {"label": "Training cutoff", "value": "The RNAcentral release used for pretraining is not stated. The README links the current release directory.", "status": "unreported", **ev(f"{README}: Data table")},
    {"label": "Context limits", "value": "1,022 nucleotides. Position embeddings cover 1,026 tokens.", "status": "source_checked", **ev(f"{README}: Tokenization; LIMBER-macro/model_config.json max_position_embeddings", (GH, HF))},
    {"label": "Weights licence", "value": "No licence is stated on the Hugging Face repository as read on 2026-11-26: the model card metadata has no licence field.", "status": "unreported", **ev("Hugging Face model card metadata at revision d2d6ae6", (HF,))},
    {"label": "Code licence", "value": "No licence file is present in the GitHub repository at commit 72a328a, and GitHub reports no licence for it.", "status": "unreported", **ev("Repository root listing at commit 72a328a")},
    {"label": "Access", "value": "Code: https://github.com/ziyaow1010/LIMBER. Weights: https://huggingface.co/Ziyao1010/LIMBER, not gated, one subfolder per model.", "status": "source_checked", **ev(f"{README}: Model zoo; Hugging Face repository", (GH, HF))},
  ],
  "strengths": [
    {"text": "Every size was pretrained by the authors on the same corpus with the same optimiser, alongside Transformer-only and Mamba-only controls, so differences between variants can be attributed to architecture, size, data or training length one at a time.", **ev(f"{README}: Scaling behaviour; Model zoo")},
    {"text": "The repository includes probes that read secondary structure, family relatedness and mutational fitness from the pretrained model without fine-tuning.", **ev(f"{README}: What pretraining alone produces")},
  ],
  "limitations": [
    {"text": "Sequences longer than 1,022 nucleotides cannot be read whole, which excludes most messenger RNAs and long non-coding RNAs at full length.", **ev(f"{README}: Tokenization")},
    {"text": "All reported comparisons, including the baseline scores, come from the authors' own fine-tuning runs. No independent evaluation is recorded here.", **ev(f"{README}: Results")},
    {"text": "Neither the code nor the weights carry a stated licence, so terms of reuse are unknown.", **ev("Repository root listing at commit 72a328a; Hugging Face model card metadata at revision d2d6ae6", (GH, HF))},
    {"text": "The Mamba layers depend on the mamba-ssm and causal-conv1d packages, and the quick start moves tensors to a CUDA device. CPU-only use is not described.", **ev(f"{README}: Quick start")},
  ],
  "diagram": {
    "title": "LIMBER workflow",
    "steps": ["RNA sequence", "One token per nucleotide (T mapped to U)", "Repeating blocks: Transformer, Transformer, Mamba", "Per-nucleotide embeddings", "Masked-token logits, or a task head for structure, classification or regression"],
    "caption": "Data flow as described in the repository. The number of blocks and the hidden size depend on the checkpoint.",
    **ev(f"{README}: Overview; Model zoo; Quick start")},
  "coverage": "reviewed",
  "gaps": [
    "The preprint was not read in full for this profile; statements rest on the repository README and the Hugging Face repository.",
    "Hardware needed for inference is not stated. The README reports the training hardware only.",
    "The author-reported benchmark figures are not yet recorded as results.",
  ],
  "review": {"method": "automated_source_review", "date": "2026-11-26",
             "note": "Written from the repository README at commit 72a328a, the repository root listing, and the Hugging Face repository listing and LIMBER-macro model_config.json at revision d2d6ae6, each fetched on 2026-11-26. The README was last pushed on 2026-11-05, before the stored source was retrieved on 2026-11-24. No command was executed and no human review is claimed."},
}
run_guide = {
  "record_id": RID,
  "summary": "Install the dependencies, download LIMBER-macro from Hugging Face and run one forward pass to get embeddings for an RNA sequence.",
  "status": "source_reviewed_not_executed",
  "prerequisites": [
    "Python 3.10 or later with PyTorch 2.x.",
    "An NVIDIA GPU with CUDA: the quick start moves tensors to a CUDA device and the Mamba layers need the mamba-ssm and causal-conv1d packages. The memory needed is not stated; LIMBER-macro has 664.3M parameters.",
    "Network access to huggingface.co for the weights. No licence is stated for the code or the weights.",
  ],
  "steps": [
    {"title": "Get the code at the reviewed commit",
     "shell": "git clone https://github.com/ziyaow1010/LIMBER.git\ncd LIMBER\ngit checkout --detach 72a328aaa52a46a8916496eddb2feff86933a1d3",
     "explanation": "Checkout wrapper: the detached commit is the revision this guide was read from. The repository does not publish tagged releases.",
     **ev("Repository at commit 72a328a")},
    {"title": "Install the dependencies",
     "shell": "pip install torch transformers safetensors huggingface_hub\npip install causal-conv1d mamba-ssm",
     "explanation": "The second line installs the packages the Mamba layers require.",
     **ev(f"{README}: Quick start")},
    {"title": "Download LIMBER-macro and run a forward pass",
     "shell": "python scripts/load_hybrid650.py --seq GGGCUAUUAGCUCAGUUGGUUAGAGCGCACCCCUGAUAAGGGUGAGGUCGCUGAUUCGAAUUCAGCAUAGCCCA",
     "explanation": "The script downloads the LIMBER-macro checkpoint and runs it on the given sequence. Without --seq it uses a built-in example.",
     **ev(f"{README}: Quick start")},
    {"title": "Get embeddings from Python",
     "shell": "python - <<'PY'\nimport torch\nfrom scripts.load_hybrid650 import load_hybrid, encode, embed\n\nmodel, _ = load_hybrid()\nids = torch.tensor([encode(\"GGGCUAUUAGCUCAGUUGG\")]).cuda()\nlogits = model(input_ids=ids, attention_mask=torch.ones_like(ids)).logits\nh = embed(model, ids)\nprint(logits.shape, h.shape)\nPY",
     "explanation": "The README's Python example, wrapped in a heredoc so it can be pasted into a shell. Run it from the repository root.",
     **ev(f"{README}: Quick start")},
  ],
  "outputs": [
    "Masked-token logits of shape [1, L+2, 10].",
    "Per-nucleotide embeddings of shape [1, L+2, 1280]; position 0 is the pooled sequence representation.",
  ],
  "limitations": [
    "These commands were read from the repository and have not been executed by Rewire.",
    "Other checkpoints load through HybridMambaConfig and HybridMambaForMaskedLM with the model_config.json in their subfolder; this guide covers LIMBER-macro only.",
    "Sequences longer than 1,022 nucleotides must be cropped or split before encoding.",
  ],
  "source_ids": [GH],
  "review": {"method": "official_repository_review", "date": "2026-11-26"},
}
path = "data/entities/models.jsonl"
lines = open(path).read().split("\n"); done = False
for i, line in enumerate(lines):
    if f'"id":"{RID}"' in line:
        rec = json.loads(line); a = rec["attributes"]
        a["profile"] = profile; a["run_guide"] = run_guide
        a["missing_metadata"]["licence"] = {"note": "No licence file in the GitHub repository at commit 72a328a and no licence field in the Hugging Face model card at revision d2d6ae6, as read on 2026-11-26.", "reason": "unreported"}
        rec["attributes"] = {k: a[k] for k in sorted(a)}
        lines[i] = json.dumps(rec, ensure_ascii=False, separators=(",", ":")); done = True
assert done; open(path, "w").write("\n".join(lines))
