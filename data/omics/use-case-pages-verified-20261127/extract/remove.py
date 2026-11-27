#!/usr/bin/env python3
"""Remove two use cases that were added on this branch and never released, with their judgements.

  python3 data/omics/use-case-pages-verified-20261127/extract/remove.py <repo-root>

The records came from batch use-case-pages-20261127 and no release has served them, so they are
taken out with their provenance lines rather than withdrawn: the release guard concerns only
judgements a previous release served. Writes removed.jsonl with every removed record's id and kind.
"""
import glob
import json
import sys
from pathlib import Path

USE_CASES = ("use-case-rna-sequence-property-prediction", "use-case-gene-regulatory-network-inference")
root = Path(sys.argv[1])
prov = {}
for f in glob.glob(str(root / "data/provenance/records/*.jsonl")):
    for line in open(f):
        d = json.loads(line)
        prov[d["id"]] = d
doomed = set(USE_CASES)
for f in glob.glob(str(root / "data/evidence/claims/*.jsonl")):
    for line in open(f):
        d = json.loads(line)
        if any(l["relation"] == "subject" and l["target_id"] in USE_CASES for l in d["links"]):
            doomed.add(d["id"])
for rid in doomed:
    assert prov[rid]["added_in"] == "data/omics/use-case-pages-20261127", (rid, prov[rid]["added_in"])
removed = []
for pattern in ("data/entities/use-cases.jsonl", "data/evidence/claims/*.jsonl", "data/provenance/records/*.jsonl"):
    for f in glob.glob(str(root / pattern)):
        lines = open(f).read().splitlines()
        keep = []
        for line in lines:
            d = json.loads(line)
            if d["id"] in doomed:
                if "kind" in d:
                    removed.append({"id": d["id"], "kind": d["kind"]})
                continue
            keep.append(line)
        if len(keep) != len(lines):
            open(f, "w").write("".join(l + "\n" for l in keep))
out = root / "data/omics/use-case-pages-verified-20261127/removed.jsonl"
out.write_text("".join(json.dumps(r) + "\n" for r in sorted(removed, key=lambda r: r["id"])))
print(f"removed {len(removed)} records")
