"""Reviewer check: does each claim's text appear in the artifact its source record names?

For every claim, split the value into sentences, normalise markdown and the characters the
batch deliberately respells, and look for each sentence in the normalised artifact text.
Reports any sentence not found, for manual reading.
"""

import json
import pathlib
import re
import sys

BATCH = pathlib.Path(sys.argv[1])
REFETCH = pathlib.Path(sys.argv[2])

ARTIFACT = {
    "bioemu2-20261115-source-model-card": "repo_MODEL_CARD.md",
    "bioemu2-20261115-source-readme": "repo_README.md",
    "bioemu2-20261115-source-notices": "repo_NOTICES.md",
    "bioemu2-20261115-source-licence": "repo_LICENSE",
    "bioemu2-20261115-source-pyproject": "repo_pyproject.toml",
    "bioemu2-20261115-source-docs-checkpoints": "repo_docs_checkpoints.md",
    "bioemu2-20261115-source-docs-sampling": "repo_docs_sampling.md",
    "bioemu2-20261115-source-docs-context-parallel": "repo_docs_context-parallel-sampling.md",
    "bioemu2-20261115-source-docs-propagation": "repo_docs_propagation.md",
    "bioemu2-20261115-source-hf-model-card": "hf_README.md",
    "bioemu2-20261115-source-hf-checkpoint-config": "hf_config.yaml",
    "bioemu2-20261115-source-hf-checkpoint-pointer": "hf_checkpoint_pointer.txt",
    "bioemu2-20261115-source-hf-revision-listing": "hf_api_revision.json",
}


def normalise(text: str) -> str:
    text = text.replace("–", " to ").replace("—", " ")
    text = text.replace("µs", " microsecond").replace("×", "x")
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # markdown links
    text = text.replace("**", "").replace("`", "").replace("*", "")
    text = re.sub(r"[\s]+", " ", text)
    return text.lower()


def sentences(value: str) -> list[str]:
    parts = re.split(r"(?<=[.;:]) +", value)
    return [p.strip() for p in parts if len(p.strip()) > 25]


records = [json.loads(line) for line in (BATCH / "batch.jsonl").open()]
texts = {
    sid: normalise((REFETCH / name).read_text(encoding="utf-8"))
    for sid, name in ARTIFACT.items()
}

missing = 0
for record in records:
    if record["kind"] != "claim":
        continue
    value = record["attributes"]["value"]
    pool = " || ".join(texts[sid] for sid in record["source_ids"])
    for sentence in sentences(value):
        needle = normalise(sentence).rstrip(".;: ")
        if needle not in pool:
            missing += 1
            print(f"NOT FOUND VERBATIM: {record['id']}")
            print(f"   locator: {record['attributes']['source_locator']}")
            print(f"   text: {needle[:200]}")
print(f"\nclaim sentences not found verbatim: {missing}")
