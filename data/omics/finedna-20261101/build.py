"""Build the FineDNA batch: the FineDNA training corpus and the Carbon-X model it trained.

Usage: python3 -I build.py <FineDNA README.md> <Carbon-X README.md> <batch folder>

Both inputs are the Hugging Face cards pinned to a commit. FineDNA is a training corpus, not an evaluation set:
it holds the mid-training, SFT and RL data of Carbon-X. The store has no relation from a model to its training
data, so the model's training_data attribute names the dataset. Carbon-X's evaluation table is not extracted
in this batch. Records are written needs_review; review.py records the review.
"""
import hashlib
import json
import os
import sys

DATA_CARD, MODEL_CARD, OUT = sys.argv[1:4]
DATA_SHA = "a7cf5f42f5cc1474e9448996e2e610b04606d4c330b16d2d871cc4f5d0f822dd"
MODEL_SHA = "e57db655c2701442f280fa1c6570f548db958d98ca317d1129c0cf3a93ec59aa"
DATA_REV = "e918c3649ffc614684d10e46e1eb5ba41170e7f9"
MODEL_REV = "17de89165e25c49e7de4f845d0e5d464469de359"
for path, sha in ((DATA_CARD, DATA_SHA), (MODEL_CARD, MODEL_SHA)):
    assert hashlib.sha256(open(path, "rb").read()).hexdigest() == sha, path
data_text, model_text = open(DATA_CARD).read(), open(MODEL_CARD).read()
for phrase in ("514.30B tokens, of which the run read 302B", "203,923 conversations, 230.3M tokens",
               "98,433 prompts, 61.1M tokens", "FineDNA is released under the Apache 2.0 license",
               "| `mid_dna_mrna_splice` | 56,877,102 | 32.93B | 2.20% | 6.64B | 0.20 |",
               "| `variant_effect_prediction` | `bioreason` | 19,996 |", "| `sequence_classification` | `genomeqa` | 14,032 |",
               "excludes the prompts that model saw during SFT"):
    assert phrase in data_text, phrase
for phrase in ("14.8B-parameter decoder-only language model", "All training data was decontaminated against these benchmarks",
               "has **not been clinically validated**", "Splice-site and histone-mark questions remain weak (29.8% and 34.6% on GenomeQA)",
               "[Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B)"):
    assert phrase in model_text, phrase

P = "finedna-20261101"
FACETS = {"areas": ["dna-genomes"], "contexts": ["research"]}
records = []


def add(rec):
    records.append(rec)
    return rec["id"]


DATA_SRC = add({
    "id": f"{P}-source-finedna-card", "kind": "source",
    "name": "FineDNA dataset card (HuggingFaceBio/FineDNA on Hugging Face)",
    "description": "The Hugging Face dataset card of FineDNA, pinned to a repository commit; it documents every config, its size and its share of Carbon-X training.",
    "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
    "attributes": {
        "url": f"https://huggingface.co/datasets/HuggingFaceBio/FineDNA/tree/{DATA_REV}",
        "artifact_url": f"https://huggingface.co/datasets/HuggingFaceBio/FineDNA/resolve/{DATA_REV}/README.md",
        "version": f"HuggingFaceBio/FineDNA commit {DATA_REV} (last modified 2026-10-30)",
        "retrieved_at": "2026-11-01T14:41:00Z",
        "artifact_sha256": DATA_SHA,
        "publication_status": "official_project_source",
        "licence": "Apache-2.0",
        "media_type": "text/markdown",
        "limitations": [
            "A dataset card written by the dataset's authors, not a paper; no peer review and no preprint at retrieval.",
            "Token counts are estimated from a 2,000-document sample per config with the Carbon-X tokenizer (card, Mid-training).",
            "Found through a LinkedIn post by one of the authors; the post is not a source.",
        ],
    }})
MODEL_SRC = add({
    "id": f"{P}-source-carbon-x-card", "kind": "source",
    "name": "Carbon-X model card (HuggingFaceBio/Carbon-X on Hugging Face)",
    "description": "The Hugging Face model card of Carbon-X, pinned to a repository commit; it documents the architecture, the training stages and an evaluation table.",
    "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
    "attributes": {
        "url": f"https://huggingface.co/HuggingFaceBio/Carbon-X/tree/{MODEL_REV}",
        "artifact_url": f"https://huggingface.co/HuggingFaceBio/Carbon-X/resolve/{MODEL_REV}/README.md",
        "version": f"HuggingFaceBio/Carbon-X commit {MODEL_REV}",
        "retrieved_at": "2026-11-01T14:52:00Z",
        "artifact_sha256": MODEL_SHA,
        "publication_status": "official_project_source",
        "licence": "Apache-2.0",
        "media_type": "text/markdown",
        "limitations": [
            "Developer-reported model card, not a paper; no peer review at retrieval.",
            "The evaluation table (BioReason Coding, BioReason Non-SNV, GenomeQA, NextBase, FrontierVEP against frontier language models) was not extracted in this batch.",
        ],
    }})

add({
    "id": f"{P}-data-finedna", "kind": "dataset", "name": "FineDNA",
    "description": "Training corpus of the Carbon-X DNA language model for all three of its stages: mid-training on genomes, transcripts, biology text, English and instruction data, then supervised fine-tuning conversations and reinforcement-learning prompts.",
    "status": "needs_review", "facets": FACETS, "source_ids": [DATA_SRC, MODEL_SRC], "links": [],
    "attributes": {
        "reported_name": "FineDNA",
        "version": f"Hugging Face commit {DATA_REV}",
        "repository": "https://huggingface.co/datasets/HuggingFaceBio/FineDNA",
        "access": "Public download from Hugging Face; the mid-training configs total about 950 GB and are meant to be streamed.",
        "species": "Eukaryotes (fungi, protozoa, plants, invertebrates, mammals, other vertebrates) from GENERator; mRNA and prokaryote genomes (GTDB and IMG/PR) from OpenGenome2",
        "population": (
            "Mid-training: 23 configs, 514.30B tokens, of which Carbon-X read 302B by weighted sampling (DNA 55%, "
            "biology text 15%, English 20%, instruction data 10%). SFT: 203,923 conversations (230.3M tokens) in eight "
            "domains, including 57,254 variant-effect prediction rows. RL: 98,433 verifiable prompts (61.1M tokens) in "
            "eight task groups, including bioreason (19,996), vepqa (7,426) and genomeqa (14,032) prompts."),
        "split": "Training data only. Biology-text mid-training configs carry a validation split held out to track loss; the SFT and RL configs are training rows in trainer order.",
        "scope_note": (
            "A training corpus, not an evaluation set: no result in this store is measured on it. It is recorded so "
            "that training overlap can be checked for evaluations of Carbon-X and of models trained on the same "
            "upstream data. mid_dna_mrna_splice holds 56.9 million OpenGenome2 mRNA sequences with splice and promoter "
            "context, with splice-junction markers removed."),
        "reuse_restrictions": "Apache-2.0 for FineDNA; the mid-training configs come from GENERator, OpenGenome2, FineWeb-Edu, DCLM, FinePDFs-Edu, PubMed Central, bioRxiv, Biostars and Nemotron, which keep their own licences and terms.",
        "source_locator": f"{DATA_SRC}: stage table, Mid-training ('The mix', 'What is in it'), SFT ('Domains'), RL ('Task groups'), License",
    }})

add({
    "id": f"{P}-model-carbon-x", "kind": "model", "name": "Carbon-X",
    "description": "Carbon-X reads raw DNA inside a chat conversation and answers in English, predicting variant pathogenicity, classifying sequences and predicting the next bases.",
    "status": "needs_review", "facets": {**FACETS, "method_types": ["foundation_model"]}, "source_ids": [MODEL_SRC, DATA_SRC], "links": [],
    "attributes": {
        "reported_name": "Carbon-X",
        "entity_level": "checkpoint",
        "version": "HuggingFaceBio/Carbon-X",
        "checkpoint_revision": MODEL_REV,
        "licence": "Apache-2.0",
        "access": "Public weights on Hugging Face; 14.8B parameters in bfloat16, served with vLLM on a single 80 GB GPU.",
        "training_data": (
            f"FineDNA ({P}-data-finedna) for all three stages: 302B tokens of mid-training from Qwen3-14B, then SFT "
            "(HuggingFaceBio/Carbon-X-SFT) and GRPO reinforcement learning with verifiable rewards. The card states "
            "that all training data was decontaminated against its five evaluation benchmarks by whole-span DNA "
            "overlap, text n-gram overlap and sequence homology search."),
        "provenance_note": (
            "Decoder-only Transformer extended from Qwen3-14B with 5,515 DNA tokens (non-overlapping 6-mers); 40,960-token "
            "context. Built by Hugging Face, Zhongguancun Academy and the Telethon Institute of Genetics and Medicine "
            "(University of Naples Federico II). Not clinically validated; the card reports weak splice-site (29.8%) "
            "and histone-mark (34.6%) accuracy on GenomeQA."),
        "source_locator": f"{MODEL_SRC}: Model Summary, Key features, Training, Limitations",
    }})

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in sorted(records, key=lambda r: r["id"]):
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print({r["kind"]: sum(x["kind"] == r["kind"] for x in records) for r in records})
