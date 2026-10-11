"""Add the reviewed assessed_by links proposed in a batch's use-case-links.json to the use_case records.

Usage: python3 -I add_use_case_links.py <repo-root> <batch-folder>
Edits data/entities/use-cases.jsonl in place, keeping the store's line format. Record the edit with
`npm run records -- change <review> <batch> <use-case-id>`.
"""
import json, os, sys

root, folder = sys.argv[1:3]
fmt = lambda r: json.dumps(r, separators=(",", ":"), ensure_ascii=False)
links = json.load(open(os.path.join(folder, "use-case-links.json")))["links"]
path = os.path.join(root, "data/entities/use-cases.jsonl")
lines = open(path, encoding="utf-8").read().split("\n")
for i, line in enumerate(lines):
    if not line:
        continue
    r = json.loads(line)
    mine = [l for l in links if l["use_case"] == r["id"]]
    if not mine:
        continue
    assert fmt(r) == line, r["id"]
    for l in mine:
        link = {"relation": l["relation"], "target_id": l["target_id"]}
        assert link not in r["links"], link
        r["links"].append(link)
    lines[i] = fmt(r)
    print("linked", r["id"], [l["target_id"] for l in mine])
open(path, "w", encoding="utf-8").write("\n".join(lines))
