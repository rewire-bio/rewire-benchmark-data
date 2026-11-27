#!/usr/bin/env python3
"""Add the missing configuration_of link to 36 configurations of batch amp-feng-20261007.

  python3 data/omics/amp-feng-parent-links-20261127/extract/build.py <repo-root> <out-dir> [--check]

Each configuration's reported_name names a model, and the configuration has no parent link. The
parent chosen for each name, and the evidence for it, is in PARENTS. Writes changes.jsonl (for
records -- change) and evidence.jsonl (one row per link).
"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

PARENTS = {
    "GROVER": ("lit-genomics-20261011-geneb-model-grover", "exact name",
               "The only record named GROVER of any system kind; 2 other configurations link to it."),
    "DNABERT-2": ("discovery-model-dnabert-2", "exact name",
                  "Two model records are named DNABERT-2; 33 configurations elsewhere in the store link to this one and 1 to catalog-model-dnabert-2. The four other exact matches are study-local pipeline records."),
    "HyenaDNA": ("regulatory-variant-20261009-model-hyenadna", "exact name",
                 "The only model record named HyenaDNA; 30 configurations elsewhere link to it. The other exact match is a study-local pipeline record (MIMIC mRNABench)."),
    "NT-v2": ("catalog-model-nt-v2", "alias",
              "No model record is named NT-v2; 27 of the 28 other NT-v2 configurations in the store (NTv2-50M to NTv2-500M) link to catalog-model-nt-v2, Nucleotide Transformer v2, and one to discovery-model-nucleotide-transformer. The two exact matches are study-local pipeline records."),
}
PARENT_RELATIONS = ("configuration_of", "family", "variant_of")


def build(root: Path):
    lines = {}
    for line in (root / "data/entities/configurations.jsonl").read_text().splitlines():
        lines[json.loads(line)["id"]] = line
    names = {}
    for f in ("models.jsonl", "pipelines.jsonl", "methods.jsonl"):
        for line in (root / "data/entities" / f).read_text().splitlines():
            d = json.loads(line)
            names[d["id"]] = (d["kind"], d["name"])
    changes, evidence = [], []
    for cid in sorted(lines):
        if not cid.startswith("amp-feng-20261007-config-"):
            continue
        rec = json.loads(lines[cid])
        reported = rec["attributes"].get("reported_name")
        if reported not in PARENTS:
            continue
        parent, basis, why = PARENTS[reported]
        assert parent in names, parent
        existing = [l for l in rec["links"] if l["relation"] in PARENT_RELATIONS]
        if existing and existing != [{"relation": "configuration_of", "target_id": parent}]:
            continue
        if not existing:
            rec["links"].append({"relation": "configuration_of", "target_id": parent})
        new = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
        changes.append({"id": cid, "base_sha256": hashlib.sha256(lines[cid].encode()).hexdigest(),
                        "sha256": hashlib.sha256(new.encode()).hexdigest(), "record": rec})
        evidence.append({"configuration": cid, "configuration_name": rec["name"], "reported_name": reported,
                         "parent": parent, "parent_kind": names[parent][0], "parent_name": names[parent][1],
                         "basis": basis, "why": why, "configuration_sources": rec["source_ids"]})
    return changes, evidence


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--check"]
    root, out = Path(args[0]), Path(args[1])
    changes, evidence = build(root)
    text = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in evidence)
    if "--check" in sys.argv:
        assert (out / "evidence.jsonl").read_text() == text, "evidence.jsonl differs from rebuild"
        print(f"{len(evidence)} links verified")
    else:
        (out / "changes.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) + "\n" for c in changes))
        (out / "evidence.jsonl").write_text(text)
        print(f"{len(changes)} links:", dict(collections.Counter(e["reported_name"] for e in evidence)))
