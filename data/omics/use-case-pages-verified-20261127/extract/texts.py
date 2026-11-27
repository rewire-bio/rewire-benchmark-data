#!/usr/bin/env python3
"""Write the corrected text of each new use case from texts.json into a records change.

  python3 data/omics/use-case-pages-verified-20261127/extract/texts.py <repo-root> <out-dir>

Top-level fields (name, description) and attributes are replaced as given; nothing else changes.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
root, out = Path(sys.argv[1]), Path(sys.argv[2])
texts = json.loads((HERE / "texts.json").read_text())
raw = {json.loads(l)["id"]: l.rstrip("\n") for l in (root / "data/entities/use-cases.jsonl").read_text().splitlines()}
lines = []
for slug, fields in sorted(texts.items()):
    rid = f"use-case-{slug}"
    rec = json.loads(raw[rid])
    for key, value in fields.items():
        if key in ("name", "description"):
            rec[key] = value
        else:
            rec["attributes"][key] = value
    text = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
    lines.append(json.dumps({"id": rid, "base_sha256": hashlib.sha256(raw[rid].encode()).hexdigest(),
                             "sha256": hashlib.sha256(text.encode()).hexdigest(), "record": rec}, ensure_ascii=False, separators=(",", ":")))
(out / "texts-changes.jsonl").write_text("".join(l + "\n" for l in lines))
print(len(lines), "use cases")
