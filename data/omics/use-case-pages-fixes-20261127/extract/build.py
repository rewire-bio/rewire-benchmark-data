#!/usr/bin/env python3
"""Build batch use-case-pages-fixes-20261127 from spec.json.

  python3 data/omics/use-case-pages-fixes-20261127/extract/build.py <repo-root> <out-dir>

Withdraws judgements that a test-by-test reading put outside their use case (claim status excluded,
assessed_by link removed), regrades three, adds an exclusion, links further protocols, and adds the
viral and microbial sequence classification use case. Writes batch.jsonl (new records),
changes.jsonl (changed records), regraded.txt (claims to re-pin) and applied.jsonl.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = "2026-11-27T23:00:00Z"
REVIEW_DOC = "docs/reviews/use-cases/use-case-pages-fixes-2026-11-27.md"
spec = importlib.util.spec_from_file_location("pages", HERE.parents[1] / "use-case-pages-20261127/extract/build.py")
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)
REVIEW = {"method": ["scope-review", "source-hash-verification"], "reviewer": ["claude"], "reviewer_note": pages.REVIEWER_NOTE, "reviewed_at": NOW}


def claim_lines(root):
    out = {}
    for f in sorted((root / "data/evidence/claims").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            out[json.loads(line)["id"]] = line
    return out


def build(root: Path):
    s = json.loads((HERE / "spec.json").read_text())
    records, raw, prov = pages.gaps.load_store(root)
    claims = claim_lines(root)
    raw.update(claims)
    scoped = pages.gaps.scoped_concern_targets(records)
    whole = {r["id"] for r in records.values() if r["kind"] == "source"
             for item in (r["attributes"].get("evidence_concerns") or [])
             if isinstance(item, str) or (isinstance(item, dict) and not item.get("applies_to"))}
    clean = lambda sid: bool((x := records.get(sid)) and x["kind"] == "source" and x["status"] in ("source_checked", "reproduced") and sid not in whole)
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

    changed, new, applied, regraded = {}, [], [], []

    def current(rid):
        return changed.get(rid) or json.loads(raw[rid])

    slug_of = lambda uc: uc[len("use-case-"):]
    w = s["withdraw"]
    for pid in w["protocols"]:
        cid = f"use-case-mapping-20261127-{slug_of(w['use_case'])}-{pid}"
        c = current(cid)
        c["status"] = "excluded"
        c["attributes"]["reason"] = w["reason"]
        changed[cid] = c
        uc = current(w["use_case"])
        uc["links"] = [l for l in uc["links"] if not (l["relation"] == "assessed_by" and l["target_id"] == pid)]
        changed[w["use_case"]] = uc
    g = s["regrade"]
    for pid in g["protocols"]:
        cid = f"use-case-mapping-20261127-{slug_of(g['use_case'])}-{pid}"
        c = current(cid)
        c["attributes"]["relevance"] = g["to"]
        c["attributes"]["rationale"] = g["reason"]
        c["description"] = g["reason"]
        changed[cid] = c
        regraded.append(cid)
    x = s["add_exclusion"]
    uc = current(x["use_case"])
    if x["text"] not in uc["attributes"]["exclusions"]:
        uc["attributes"]["exclusions"].append(x["text"])
    changed[x["use_case"]] = uc

    case = s["new_use_case"]
    new_id = f"use-case-{case['slug']}"
    new_links = [a for a in s["add_links"] if a["use_case"] == new_id]
    for a in s["add_links"]:
        pid = a["protocol"]
        proto = records[pid]
        assert proto["kind"] == "protocol" and proto["status"] == "source_checked" and all(clean(t) for t in proto["source_ids"]), pid
        evs = pages.eligible_evaluations(records, clean, scoped, ev, res, pid)
        assert evs, pid
        locator = proto["attributes"].get("source_locator") or "See the protocol record"
        cid = f"use-case-mapping-20261127-{slug_of(a['use_case'])}-{pid}"
        new.append({"id": cid, "kind": "claim", "name": f"Relevance of {pid} to {a['use_case']}", "description": a["reason"],
                    "status": "source_checked", "facets": {}, "source_ids": proto["source_ids"],
                    "links": [{"relation": "subject", "target_id": a["use_case"]}],
                    "attributes": {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": a["relevance"],
                                   "endpoint": proto["description"], "rationale": a["reason"],
                                   "constraints": [f"Compare rows only within this protocol: {proto['name']}."],
                                   "limitations": list(proto["attributes"].get("limitations", []))[:3] or ["One study's evaluation; see the use case's evidence gaps."],
                                   "citation_locators": [{"source_id": t, "locator": locator} for t in proto["source_ids"][:2]],
                                   "source_locator": locator, "reason": f"Use case fixes, 27 November 2026 ({REVIEW_DOC}).",
                                   "review": {**REVIEW, "note": f"Scope and evaluation gates checked for {len(evs)} evaluations against {REVIEW_DOC}."},
                                   "reviewed_evaluations": evs}})
        applied.append({"use_case": a["use_case"], "test": pid, "claim": cid, "relevance": a["relevance"], "reason": a["reason"],
                        "evaluations": len(evs), "passage": {"record": pid, "field": "description", "text": proto["description"]},
                        "source_locator": locator})
        if a["use_case"] != new_id:
            uc = current(a["use_case"])
            if not any(l["relation"] == "assessed_by" and l["target_id"] == pid for l in uc["links"]):
                uc["links"].append({"relation": "assessed_by", "target_id": pid})
            changed[a["use_case"]] = uc
    integ = current("use-case-single-cell-data-integration")
    gaps = integ["attributes"]["evidence_gaps"]
    gaps[0] = s["integration_gap"]
    changed["use-case-single-cell-data-integration"] = integ

    sources = sorted({t for a in new_links for t in records[a["protocol"]]["source_ids"]})
    new.insert(0, {
        "id": new_id, "kind": "use_case", "name": case["name"], "description": case["question"], "status": "source_checked",
        "facets": {"areas": [case["area"]], "contexts": ["research"]}, "source_ids": sources,
        "links": [{"relation": "assessed_by", "target_id": a["protocol"]} for a in sorted(new_links, key=lambda a: a["protocol"])],
        "attributes": {"depth_tier": 3, "slug": case["slug"], "question": case["question"], "intended_users": case["intended_users"],
                       "decision": case["decision"], "inputs": case["inputs"], "output": case["output"], "setting": case["setting"],
                       "exclusions": case["exclusions"],
                       "clinical_scope": "Research only. Nothing recorded here supports a clinical or diagnostic decision.",
                       "evidence_gaps": case["evidence_gaps"], "search_terms": case["search_terms"],
                       "citation_locators": [{"source_id": t, "locator": records[t]["attributes"].get("source_locator") or "See the source record"} for t in sources[:4]],
                       "review": {**REVIEW, "note": f"Written from the benchmark and protocol records and reviewed against {REVIEW_DOC}."}}})

    changes = []
    for rid, rec in sorted(changed.items()):
        base = hashlib.sha256(raw[rid].encode()).hexdigest()
        assert prov[rid]["sha256"] == base, rid
        line = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
        changes.append({"id": rid, "base_sha256": base, "sha256": hashlib.sha256(line.encode()).hexdigest(), "record": rec})
    return new, changes, applied, regraded


if __name__ == "__main__":
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    new, changes, applied, regraded = build(root)
    (out / "batch.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in new))
    (out / "changes.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) + "\n" for c in changes))
    (out / "applied.jsonl").write_text("".join(json.dumps(a, ensure_ascii=False) + "\n" for a in applied))
    (out / "regraded.txt").write_text("".join(c + "\n" for c in regraded))
    print(f"{len(new)} new records, {len(changes)} changed records, {len(regraded)} regraded claims")
