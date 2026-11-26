"""Add four pinned sources, a profile and a run guide to the GPN-MSA model record.

Run from the repository root:
  python3 data/omics/model-pages-20261126-gpn-msa/build.py sources   # writes batch.jsonl
  npm run records -- add data/omics/model-pages-20261126-gpn-msa/batch.jsonl data/omics/model-pages-20261126-gpn-msa
  python3 data/omics/model-pages-20261126-gpn-msa/build.py model     # edits the model record
  npm run records -- change docs/reviews/2026-11-26-gpn-msa-model-page.md data/omics/model-pages-20261126-gpn-msa gfm-guides-20261014-gpnmsa-model-gpn-msa
"""
import hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).parent
RID = "gfm-guides-20261014-gpnmsa-model-gpn-msa"
README = "gfm-guides-20261014-gpnmsa-source-gpn-readme"
DOC = "gfm-guides-20261014-gpnmsa-source-gpn-msa-doc"
P = "model-pages-20261126-gpn-msa-source-"
CARD, CONFIG, API, CLI = P + "hf-model-card", P + "hf-config", P + "hf-api", P + "gpn-cli"
COMMIT = "dc5fd287599f2955a79d010bca0e0f7f8178c67e"
REV = "4a7d4f75449cb2abd560b2af024d76f99233c6db"
HF = "https://huggingface.co/songlab/gpn-msa-sapiens"

def sha(name): return hashlib.sha256((HERE / "artifacts" / name).read_bytes()).hexdigest()

def source(id_, name, description, file, artifact_url, url, version, media_type):
    return {"id": id_, "kind": "source", "name": name, "description": description, "status": "discovered",
            "facets": {"areas": ["dna-genomes"], "contexts": ["research"]}, "source_ids": [], "links": [],
            "attributes": {"artifact_sha256": sha(file), "artifact_url": artifact_url, "media_type": media_type,
                           "publication_status": "official_project_source", "retrieved_at": "2026-11-26T15:40:00Z",
                           "url": url, "version": version}}

SOURCES = [
    source(CARD, "songlab/gpn-msa-sapiens model card at revision 4a7d4f75", "Hugging Face model card of the published GPN-MSA checkpoint, pinned to a revision.",
           "hf-model-card.md", f"{HF}/raw/{REV}/README.md", HF, f"Hugging Face revision {REV}", "text/markdown"),
    source(CONFIG, "songlab/gpn-msa-sapiens config.json at revision 4a7d4f75", "Model configuration file of the published GPN-MSA checkpoint, pinned to a revision.",
           "hf-config.json", f"{HF}/raw/{REV}/config.json", HF, f"Hugging Face revision {REV}", "application/json"),
    source(API, "Hugging Face metadata for songlab/gpn-msa-sapiens, as served on 2026-11-26", "Hugging Face API response for the checkpoint: revision, licence field, gating and the parameter count read from the safetensors file.",
           "hf-api.json", "https://huggingface.co/api/models/songlab/gpn-msa-sapiens?expand[]=safetensors&expand[]=sha&expand[]=cardData&expand[]=gated", HF, "As served on 2026-11-26; the response may change", "application/json"),
    source(CLI, "songlab-cal/gpn docs/getting-started/cli.md at commit dc5fd287", "Command-line guide in the official GPN repository, pinned to a commit.",
           "cli.md", f"https://raw.githubusercontent.com/songlab-cal/gpn/{COMMIT}/docs/getting-started/cli.md", "https://github.com/songlab-cal/gpn", f"git commit {COMMIT}", "text/markdown"),
]

def ev(locator, *ids): return {"source_ids": list(ids), "source_locator": locator}

PROFILE = {
  "summary": "GPN-MSA is a DNA language model that scores human single-nucleotide variants genome-wide. It reads a window of the human genome together with the aligned sequence of other vertebrates, and scores a variant by how much less likely the alternate allele is than the reference. Its developers now mark it as deprecated in favour of GPN-Star.",
  "summary_source_ids": [DOC, CARD, CLI],
  "summary_source_locator": "docs/models/gpn-msa.md, opening paragraph; model card title; cli.md, GPN section on the output score",
  "sections": [
    {"title": "How it works",
     "body": "The published checkpoint is a 12-layer Transformer encoder (hidden size 768, 12 attention heads) trained as a masked language model. Each position is given the human nucleotide and the aligned nucleotides of the other species in the whole-genome alignment as auxiliary features, so the model predicts a masked human base from its sequence context and from what other vertebrates carry at the same site. A variant's score is the alternate-minus-reference log-likelihood ratio at its position, averaged over the forward and reverse-complement orientations. Negative values mean the alternate allele is less likely than the reference under the model.",
     **ev("config.json: architectures, num_hidden_layers, hidden_size, num_attention_heads, n_aux_features; cli.md: GPN and GPN-MSA sections on the output score; model card title", CONFIG, CLI, CARD)},
    {"title": "Versions and reproducibility",
     "body": "One human checkpoint is published, songlab/gpn-msa-sapiens, trained on humans and 89 other vertebrates. The repository supports inference from it and no longer maintains GPN-MSA training or dataset construction. Inference needs a local alignment store whose target assembly, species count, species order and preprocessing match the checkpoint. Genome-wide hg38 scores are published as a dataset, so most uses do not need to run the model. A result should say whether it used the published scores or ran inference, and with which window size.",
     **ev("docs/models/gpn-msa.md: opening paragraph, Quick start, Published assets; model card title", DOC, CARD)},
  ],
  "facts": [
    {"label": "Model type", "value": "Masked DNA language model over a multispecies whole-genome alignment", "status": "source_checked", **ev("docs/models/gpn-msa.md, opening paragraph", DOC)},
    {"label": "Architecture", "value": "Transformer encoder (GPNRoFormerForMaskedLM): 12 layers, hidden size 768, 12 attention heads, feed-forward size 3,072, with 445 auxiliary alignment features per position.", "status": "source_checked", **ev("config.json", CONFIG)},
    {"label": "Inputs", "value": "A window of the human reference genome with the aligned bases of the other species, read from a local alignment store. Variant scoring takes biallelic single-nucleotide variants with one-based positions.", "status": "source_checked", **ev("cli.md: GPN-MSA section; GPN section on VEP inputs", CLI)},
    {"label": "Outputs", "value": "A raw, uncalibrated log-likelihood ratio per variant; masked-nucleotide logits; or embeddings averaged over a centre window.", "status": "source_checked", **ev("cli.md: GPN-MSA section", CLI)},
    {"label": "Parameters", "value": "85,749,510 (85.7M), counted from the published safetensors file.", "status": "source_checked", **ev("Hugging Face API response, safetensors.total", API)},
    {"label": "Training data", "value": "Humans and 89 other vertebrates from the 100-way vertebrate whole-genome alignment (songlab/multiz100way); prepared human training regions are published as songlab/gpn-msa-sapiens-dataset.", "status": "source_checked", **ev("Model card title and datasets field; docs/models/gpn-msa.md: Alignment and training inputs", CARD, DOC)},
    {"label": "Known versions", "value": "One published checkpoint, songlab/gpn-msa-sapiens, read at revision 4a7d4f75.", "status": "source_checked", **ev("docs/models/gpn-msa.md: Model and evaluations; Hugging Face API response, sha", DOC, API)},
    {"label": "Training cutoff", "value": "Not extracted. The documentation read does not date the alignment or the training run.", "status": "unextracted", **ev("docs/models/gpn-msa.md, all sections", DOC)},
    {"label": "Context limits", "value": "The window size is chosen at inference and must be even. The documentation read does not state the window the checkpoint was trained with; the configuration allows up to 1,536 positions.", "status": "unextracted", **ev("cli.md: GPN-MSA section; config.json max_position_embeddings", CLI, CONFIG)},
    {"label": "Weights licence", "value": "MIT, as declared in the model card.", "status": "source_checked", **ev("Model card metadata, license field", CARD)},
    {"label": "Code licence", "value": "MIT", "status": "source_checked", **ev("README.md: Development and help", README)},
    {"label": "Access", "value": "Weights: https://huggingface.co/songlab/gpn-msa-sapiens, not gated. Code: pip install gpn, from https://github.com/songlab-cal/gpn. Genome-wide scores: https://huggingface.co/datasets/songlab/gpn-msa-hg38-scores.", "status": "source_checked", **ev("docs/models/gpn-msa.md: Published assets; README.md: Quick start; Hugging Face API response, gated", DOC, README, API)},
  ],
  "strengths": [
    {"text": "Genome-wide hg38 variant scores are published, so a variant can be looked up without a GPU, an alignment download or any inference.", **ev("docs/models/gpn-msa.md: Genome-wide predictions", DOC)},
    {"text": "The model is small at 85.7M parameters, and code and weights are both MIT licensed.", **ev("Hugging Face API response, safetensors.total; model card metadata; README.md", API, CARD, README)},
  ],
  "limitations": [
    {"text": "The developers have deprecated GPN-MSA in favour of GPN-Star. The maintained package runs inference from the published checkpoint but does not support training it.", **ev("docs/models/gpn-msa.md, opening paragraph; README.md: Model families table", DOC, README)},
    {"text": "Running inference needs a local whole-genome alignment store that matches the checkpoint. The command-line tool does not download it.", **ev("cli.md: GPN-MSA section", CLI)},
    {"text": "Variant scoring covers biallelic single-nucleotide variants only, and the score is uncalibrated.", **ev("cli.md: GPN section on VEP inputs and output score", CLI)},
    {"text": "The model depends on an alignment for both training and inference, so it cannot score sequence that is absent from the alignment.", **ev("README.md: Model families table", README)},
  ],
  "diagram": {
    "title": "GPN-MSA workflow",
    "steps": ["Human genome window around the variant", "Aligned bases from 89 other vertebrates at each position", "12-layer Transformer encoder", "Probability of each nucleotide at the masked position", "Score: log-likelihood of alternate minus reference, averaged over both strands"],
    "caption": "Data flow for variant scoring as described in the repository documentation and the checkpoint configuration.",
    **ev("docs/models/gpn-msa.md; cli.md: GPN-MSA section; config.json; model card title", DOC, CLI, CONFIG, CARD)},
  "coverage": "reviewed",
  "gaps": [
    "The paper was not re-read for this profile. The training window size, training cutoff and benchmark results are not stated in the documentation read.",
    "Hardware needed for inference is not stated in the documentation read.",
    "The size of the alignment download is not stated in the documentation read.",
  ],
  "review": {"method": "automated_source_review", "date": "2026-11-26",
             "note": "Written from the repository README, docs/models/gpn-msa.md and docs/getting-started/cli.md at commit dc5fd287, and from the Hugging Face model card, config.json and API metadata at revision 4a7d4f75, each fetched on 2026-11-26. The README and the model page file match the hashes already stored for them. No command was executed and no human review is claimed."},
}

RUN_GUIDE = {
  "record_id": RID,
  "summary": "Look up published GPN-MSA scores, or install the gpn package, load the published checkpoint and score your own variants against a local alignment store.",
  "status": "source_reviewed_not_executed",
  "prerequisites": [
    "For most uses no run is needed: genome-wide hg38 scores are published at https://huggingface.co/datasets/songlab/gpn-msa-hg38-scores.",
    "Python with pip. The repository badge names Python 3.13.",
    "For your own inference: a local GPN-MSA alignment store in Zarr format that matches the checkpoint in target assembly, species count, species order and preprocessing. The processed 100-way alignment is published at https://huggingface.co/datasets/songlab/multiz100way. Its size and the hardware needed are not stated in the documentation read.",
    "Variants as biallelic single-nucleotide variants with one-based positions, in Parquet, CSV, TSV or VCF.",
  ],
  "steps": [
    {"title": "Install the package with inference dependencies",
     "shell": "pip install \"gpn[inference]\"",
     "explanation": "The inference extra is required for the file-backed commands.",
     **ev("cli.md: Installation", CLI)},
    {"title": "Load the published checkpoint in Python",
     "shell": "python - <<'PY'\nfrom gpn import register_auto_classes\nfrom transformers import AutoModelForMaskedLM\n\nregister_auto_classes(\"msa\")\nmodel = AutoModelForMaskedLM.from_pretrained(\"songlab/gpn-msa-sapiens\")\nprint(model.config.num_hidden_layers, model.config.hidden_size)\nPY",
     "explanation": "The documentation's quick start, wrapped in a heredoc, with a print of two configuration values added to confirm the load.",
     **ev("docs/models/gpn-msa.md: Quick start", DOC)},
    {"title": "Score variants",
     "shell": "gpn msa vep \\\n  --input-path variants.parquet \\\n  --msa-path LOCAL_MSA_PATH \\\n  --window-size WINDOW_SIZE \\\n  --model-path songlab/gpn-msa-sapiens \\\n  --output-path scores.parquet",
     "explanation": "Replace LOCAL_MSA_PATH with the path to the alignment store and WINDOW_SIZE with an even number. The documentation read does not give the window size for this checkpoint. The reference allele must match the alignment at each position or inference stops.",
     **ev("cli.md: GPN-MSA section", CLI)},
  ],
  "outputs": [
    "scores.parquet with a score column: the raw alternate-minus-reference log-likelihood ratio, averaged over both strand orientations. Negative means the alternate is less likely than the reference.",
  ],
  "limitations": [
    "These commands were read from the repository and have not been executed by Rewire.",
    "GPN-MSA is deprecated by its developers in favour of GPN-Star and supports inference only.",
    "The window size for the published checkpoint is not given in the documentation read, and scores depend on it.",
  ],
  "source_ids": [DOC, CLI],
  "review": {"method": "official_repository_review", "date": "2026-11-26"},
}

def dump(rec): return json.dumps(rec, ensure_ascii=False, separators=(",", ":"))

if sys.argv[1] == "sources":
    (HERE / "batch.jsonl").write_text("\n".join(dump(s) for s in SOURCES) + "\n")
elif sys.argv[1] == "model":
    path = pathlib.Path("data/entities/models.jsonl"); lines = path.read_text().split("\n"); done = False
    for i, line in enumerate(lines):
        if f'"id":"{RID}"' in line:
            rec = json.loads(line)
            rec["source_ids"] = rec["source_ids"] + [s["id"] for s in SOURCES if s["id"] not in rec["source_ids"]]
            rec["attributes"]["profile"] = PROFILE          # appended: existing key order is kept
            rec["attributes"]["run_guide"] = RUN_GUIDE
            lines[i] = dump(rec); done = True
    assert done; path.write_text("\n".join(lines))
