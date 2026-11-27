#!/usr/bin/env python3
"""Apply the second verification pass: tie changes from ties.json, text from fields.json, one model fix.

  python3 data/omics/use-case-mapping-second-pass-20261127/extract/build.py <repo-root> <out-dir>

Each judgement is found by its use case and test, named one by one in ties.json. Withdrawn judgements
get status excluded and the reason, and the use case loses the assessed_by link. fields.json replaces
exact text in a use case field ("old" must occur once) or prepends an item to a list field. Writes changes.jsonl and repin.txt: the
regraded and re-reasoned judgements, plus every active judgement of a use case whose pinned fields change.
"""
import glob
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINNED = {"question", "decision", "inputs", "output", "exclusions", "setting", "scope", "users"}
NT_V2 = "catalog-model-nt-v2"


def main(root: Path, out: Path):
    ties = json.loads((HERE / "ties.json").read_text())
    fields = json.loads((HERE / "fields.json").read_text())
    raw, recs = {}, {}
    for f in glob.glob(str(root / "data/entities/*.jsonl")) + glob.glob(str(root / "data/evidence/claims/*.jsonl")):
        for line in open(f):
            d = json.loads(line)
            raw[d["id"]], recs[d["id"]] = line.rstrip("\n"), d
    prov = {}
    for f in glob.glob(str(root / "data/provenance/records/*.jsonl")):
        for line in open(f):
            d = json.loads(line)
            prov[d["id"]] = d
    judgements = {}
    for d in recs.values():
        if d["kind"] == "claim" and d["attributes"].get("field", "").startswith("links:assessed_by:") and d["status"] == "source_checked":
            for l in d["links"]:
                if l["relation"] == "subject":
                    key = (l["target_id"], d["attributes"]["value"])
                    assert key not in judgements, key
                    judgements[key] = d["id"]
    changed, repin = {}, set()
    cur = lambda rid: changed.setdefault(rid, json.loads(raw[rid]))
    for slug, tests, reason in ties["withdraw"]:
        uc_id = f"use-case-{slug}"
        for t in tests:
            c = cur(judgements[(uc_id, t)])
            c["status"] = "excluded"
            c["attributes"]["reason"] = reason
            uc = cur(uc_id)
            n = len(uc["links"])
            uc["links"] = [l for l in uc["links"] if not (l["relation"] == "assessed_by" and l["target_id"] == t)]
            assert len(uc["links"]) == n - 1, t
    for slug, grade, tests, reason in ties["regrade"]:
        for t in tests:
            c = cur(judgements[(f"use-case-{slug}", t)])
            assert c["attributes"]["relevance"] != grade, t
            c["attributes"]["relevance"] = grade
            c["attributes"]["rationale"] = c["description"] = reason
            repin.add(c["id"])
    for slug, t, reason in ties["reason"]:
        c = cur(judgements[(f"use-case-{slug}", t)])
        c["attributes"]["rationale"] = c["description"] = reason
        repin.add(c["id"])
    for edit in fields:
        uc = cur(f"use-case-{edit['slug']}")
        if "prepend" in edit:
            uc["attributes"][edit["field"]].insert(0, edit["prepend"])
            continue
        holder = uc if edit["field"] in ("name", "description") else uc["attributes"]
        value = holder[edit["field"]]
        text = json.dumps(value, ensure_ascii=False)
        old, new = json.dumps(edit["old"], ensure_ascii=False)[1:-1], json.dumps(edit["new"], ensure_ascii=False)[1:-1]
        assert text.count(old) == 1, (edit["slug"], edit["old"][:60])
        holder[edit["field"]] = json.loads(text.replace(old, new))
        if edit["field"] in PINNED:
            for (uc_id, _), cid in judgements.items():
                if uc_id == uc["id"] and changed.get(cid, recs[cid])["status"] == "source_checked":
                    repin.add(cid)
    nt = cur(NT_V2)
    assert nt["attributes"].pop("version") == "50M multi-species"
    lines = []
    for rid, rec in sorted(changed.items()):
        base = hashlib.sha256(raw[rid].encode()).hexdigest()
        assert prov[rid]["sha256"] == base, rid
        text = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
        lines.append(json.dumps({"id": rid, "base_sha256": base, "sha256": hashlib.sha256(text.encode()).hexdigest(), "record": rec},
                                ensure_ascii=False, separators=(",", ":")))
    (out / "changes.jsonl").write_text("".join(l + "\n" for l in lines))
    (out / "repin.txt").write_text("".join(r + "\n" for r in sorted(repin)))
    print(f"{len(lines)} changed records, {len(repin)} to re-pin")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
