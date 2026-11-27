#!/usr/bin/env python3
"""Make the Nucleotide Transformer v2 profile describe the family the record stands for.

  python3 data/omics/nt-v2-family-profile-20261127/build.py <repo-root> <out-dir>

Family facts cite docs/nucleotide_transformer.md (evidence-official-657e83427ab59f3aec83, lines
34 to 37 and 106 to 109 of the pinned file); facts from the 50M model card now say so.
"""
import hashlib
import json
import sys
from pathlib import Path

ID = "catalog-model-nt-v2"
DOCS = "evidence-official-657e83427ab59f3aec83"
CARD = "evidence-official-4abb9affb1a9e5438c91"
FAMILY = "docs/nucleotide_transformer.md: NT-v2 model list and pretraining notes"
root, out = Path(sys.argv[1]), Path(sys.argv[2])
raw = next(l for l in (root / "data/entities/models.jsonl").read_text().splitlines() if json.loads(l)["id"] == ID)
rec = json.loads(raw)
p = rec["attributes"]["profile"]
facts = {f["label"]: f for f in p["facts"]}


def family(fact, value):
    assert fact["value"] != value
    fact.update(value=value, source_ids=[DOCS], source_locator=FAMILY)


p["sections"][1]["body"] = (
    "Nucleotide Transformer v2 is a family of four checkpoints, of 50M, 100M, 250M and 500M parameters, all pretrained "
    "on the multispecies dataset. Facts taken from a model card describe the 50M checkpoint's card. Source conflict "
    "retained: the 50M model card describes 1,000-token pretraining, while the official NT-v2 documentation describes "
    "2,048-token capacity. Token and base counts must be stated separately.")
family(facts["Parameters"], "Four checkpoints: 50M, 100M, 250M and 500M parameters.")
family(facts["Known versions"], "50M_multi_species_v2, 100M_multi_species_v2, 250M_multi_species_v2 and 500M_multi_species_v2.")
facts["Training data"].update(
    value="All v2 checkpoints were pretrained on the multispecies dataset: 300B tokens for the 50M and 100M models and 1T "
          "tokens for the 250M and 500M models. The 50M model card reports 850 reference genomes, excluding plants and "
          "viruses, and 174B source nucleotides. Source corpus size is distinct from repeated training exposure.",
    source_ids=[DOCS, CARD], source_locator=f"{FAMILY}; 50M model card README.md: Training data")
facts["Access"]["value"] = ("Model card and usage examples of the 50M checkpoint: "
                            "https://huggingface.co/InstaDeepAI/nucleotide-transformer-v2-50m-multi-species")
facts["Weights licence"]["value"] = "CC-BY-NC-SA-4.0 as declared in the 50M checkpoint's model card."
p["limitations"][0]["text"] = ("Token length is not identical to base-pair length: ambiguous bases consume individual tokens. "
                               "Facts from the 50M model card describe that checkpoint, not every size.")
text = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
line = {"id": ID, "base_sha256": hashlib.sha256(raw.encode()).hexdigest(), "sha256": hashlib.sha256(text.encode()).hexdigest(), "record": rec}
(out / "changes.jsonl").write_text(json.dumps(line, ensure_ascii=False, separators=(",", ":")) + "\n")
print("1 record")
