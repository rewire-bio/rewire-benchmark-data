#!/usr/bin/env python3
"""Apply the verification's tie changes from ties.json.

  python3 data/omics/use-case-pages-verified-20261127/extract/ties.py <repo-root> <out-dir>

Withdrawn judgements get status excluded and the reason, and their assessed_by link is removed.
Regraded judgements get the new grade and reason. Each tie is named test by test in ties.json; no
pattern selects a test. Writes ties-changes.jsonl, ties-batch.jsonl (new judgements), repin.txt.
"""
import glob
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = "2026-11-28T09:00:00Z"
REVIEW_DOC = "docs/reviews/use-cases/use-case-pages-verified-2026-11-28.md"
REVIEWER_NOTE = ("Claude applied the independent verification's verdicts (agent verify-mappings) test by test. "
                 "No human scientific review; the verifier re-checks the changed judgements.")
spec = importlib.util.spec_from_file_location("pages", HERE.parents[1] / "use-case-pages-20261127/extract/build.py")
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)


def main(root: Path, out: Path):
    s = json.loads((HERE / "ties.json").read_text())
    records, raw, prov = pages.gaps.load_store(root)
    for f in glob.glob(str(root / "data/evidence/claims/*.jsonl")):
        for line in open(f):
            raw[json.loads(line)["id"]] = line.rstrip("\n")
    changed, new, repin = {}, [], []
    cur = lambda rid: changed.get(rid) or json.loads(raw[rid])
    cid = lambda slug, pid: f"use-case-mapping-20261127-{slug}-{pid}"
    for slug, pids, reason in s["withdraw"]:
        for pid in pids:
            c = cur(cid(slug, pid))
            assert c["status"] == "source_checked", pid
            c["status"] = "excluded"
            c["attributes"]["reason"] = reason
            changed[c["id"]] = c
            uc = cur(f"use-case-{slug}")
            before = len(uc["links"])
            uc["links"] = [l for l in uc["links"] if not (l["relation"] == "assessed_by" and l["target_id"] == pid)]
            assert len(uc["links"]) == before - 1, pid
            changed[uc["id"]] = uc
    for slug, grade, pids, reason in s["regrade"]:
        for pid in pids:
            c = cur(cid(slug, pid))
            assert c["status"] == "source_checked", pid
            c["attributes"]["relevance"] = grade
            c["attributes"]["rationale"] = reason
            c["description"] = reason
            changed[c["id"]] = c
            repin.append(c["id"])
    for slug, pid, reason in s["reason"]:
        c = cur(cid(slug, pid))
        c["attributes"]["rationale"] = reason
        c["description"] = reason
        changed[c["id"]] = c
        repin.append(c["id"])
    scoped = pages.gaps.scoped_concern_targets(records)
    whole = {r["id"] for r in records.values() if r["kind"] == "source"
             for i in (r["attributes"].get("evidence_concerns") or []) if isinstance(i, str) or (isinstance(i, dict) and not i.get("applies_to"))}
    clean = lambda t: bool((x := records.get(t)) and x["kind"] == "source" and x["status"] in ("source_checked", "reproduced") and t not in whole)
    ev, res = {}, {}
    for r in records.values():
        if r["kind"] == "evaluation":
            for l in r["links"]:
                if l["relation"] == "assessment":
                    ev.setdefault(l["target_id"], []).append(r)
        elif r["kind"] == "result":
            for l in r["links"]:
                if l["relation"] == "evaluation":
                    res.setdefault(l["target_id"], []).append(r)
    for slug, pid, grade, reason in s["add"]:
        proto = records[pid]
        evs = pages.eligible_evaluations(records, clean, scoped, ev, res, pid)
        assert evs and proto["status"] == "source_checked", pid
        locator = proto["attributes"].get("source_locator") or "See the protocol record"
        new.append({"id": cid(slug, pid), "kind": "claim", "name": f"Relevance of {pid} to use-case-{slug}", "description": reason,
                    "status": "source_checked", "facets": {}, "source_ids": proto["source_ids"],
                    "links": [{"relation": "subject", "target_id": f"use-case-{slug}"}],
                    "attributes": {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": grade,
                                   "endpoint": proto["description"], "rationale": reason,
                                   "constraints": [f"Compare rows only within this protocol: {proto['name']}."],
                                   "limitations": list(proto["attributes"].get("limitations", []))[:3] or ["One held-out split of one landscape."],
                                   "citation_locators": [{"source_id": t, "locator": locator} for t in proto["source_ids"][:2]],
                                   "source_locator": locator, "reason": f"Verification fixes, 28 November 2026 ({REVIEW_DOC}).",
                                   "review": {"method": ["scope-review", "source-hash-verification"], "reviewer": ["claude"],
                                              "reviewer_note": REVIEWER_NOTE, "reviewed_at": NOW,
                                              "note": f"Scope and evaluation gates checked for {len(evs)} evaluations against {REVIEW_DOC}."},
                                   "reviewed_evaluations": evs}})
        uc = cur(f"use-case-{slug}")
        uc["links"].append({"relation": "assessed_by", "target_id": pid})
        changed[uc["id"]] = uc
    lines = []
    for rid, rec in sorted(changed.items()):
        base = hashlib.sha256(raw[rid].encode()).hexdigest()
        assert prov[rid]["sha256"] == base, rid
        text = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
        lines.append(json.dumps({"id": rid, "base_sha256": base, "sha256": hashlib.sha256(text.encode()).hexdigest(), "record": rec},
                                ensure_ascii=False, separators=(",", ":")))
    (out / "ties-changes.jsonl").write_text("".join(l + "\n" for l in lines))
    (out / "ties-batch.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in new))
    (out / "repin.txt").write_text("".join(r + "\n" for r in repin))
    print(f"{len(lines)} changed records, {len(new)} new judgements, {len(repin)} to re-pin")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
