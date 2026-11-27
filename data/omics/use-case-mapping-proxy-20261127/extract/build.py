#!/usr/bin/env python3
"""Build the proxy relevance judgements of batch use-case-mapping-proxy-20261127.

  python3 data/omics/use-case-mapping-proxy-20261127/extract/build.py <repo-root> <out-dir> [--check]

selection.json lists the candidates of kb/curation/use_case_mapping_candidates.jsonl applied at
proxy grade (the use case already maps the same kind of test at proxy, its exclusions do not name
the test, and the evaluation gates accept it), and the ones refused with the reason. Evaluations a
judgement does not cover are listed in excluded_evaluations with a reason. Writes batch.jsonl,
changes.jsonl and applied.jsonl.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = "2026-11-27T22:00:00Z"
REVIEW_DOC = "docs/reviews/use-cases/use-case-mapping-proxy-2026-11-27.md"
REVIEWER_NOTE = (
    "Claude checked each protocol against the use case's question, exclusions and the grade the use case "
    "already gives the same kind of test, and verified the evaluation gates in the store. Drafter and "
    "reviewer are the same agent, so this is not the second-worker review docs/use-cases.md requires. No "
    "human scientific review; an independent verification pass is needed."
)

spec = importlib.util.spec_from_file_location("pages", HERE.parents[1] / "use-case-pages-20261127/extract/build.py")
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)


def build(root: Path):
    records, raw_lines, prov = pages.gaps.load_store(root)
    scoped = pages.gaps.scoped_concern_targets(records)
    whole = {r["id"] for r in records.values() if r["kind"] == "source"
             for item in (r["attributes"].get("evidence_concerns") or [])
             if isinstance(item, str) or (isinstance(item, dict) and not item.get("applies_to"))}

    def clean(sid):
        s = records.get(sid)
        return bool(s and s["kind"] == "source" and s["status"] in ("source_checked", "reproduced") and sid not in whole)

    evals_by_proto, results_by_eval = {}, {}
    for r in records.values():
        if r["kind"] == "evaluation":
            for l in r["links"]:
                if l["relation"] == "assessment":
                    evals_by_proto.setdefault(l["target_id"], []).append(r)
        elif r["kind"] == "result":
            for l in r["links"]:
                if l["relation"] == "evaluation":
                    results_by_eval.setdefault(l["target_id"], []).append(r)

    selection = json.loads((HERE / "selection.json").read_text())
    claims, applied, additions = [], [], {}
    for item in selection["apply"]:
        uc_id, pid = item["use_case"], item["test"]
        proto = records[pid]
        assert proto["kind"] == "protocol" and proto["status"] == "source_checked", pid
        assert all(clean(s) for s in proto["source_ids"]), pid
        excluded = {e["id"] for e in item["excluded"]}
        evs = [e for e in pages.eligible_evaluations(records, clean, scoped, evals_by_proto, results_by_eval, pid) if e not in excluded]
        assert evs, pid
        locator = proto["attributes"].get("source_locator") or "See the protocol record"
        attrs = {
            "field": f"links:assessed_by:{pid}", "value": pid, "relevance": item["relevance"],
            "endpoint": proto["description"], "rationale": item["reason"],
            "constraints": [f"Compare rows only within this protocol: {proto['name']}."],
            "limitations": list(proto["attributes"].get("limitations", []))[:3]
                           or ["Proxy evidence: a related endpoint, not the use case's own."],
            "citation_locators": [{"source_id": s, "locator": locator} for s in proto["source_ids"][:2]],
            "source_locator": locator,
            "reason": f"Proxy candidates applied, 27 November 2026 ({REVIEW_DOC}).",
            "review": {"method": ["scope-review", "source-hash-verification"], "reviewer": ["claude"],
                       "reviewer_note": REVIEWER_NOTE, "reviewed_at": NOW,
                       "note": f"Scope and evaluation gates checked for {len(evs)} evaluations against {REVIEW_DOC}."},
            "reviewed_evaluations": evs,
        }
        if item["excluded"]:
            attrs["excluded_evaluations"] = item["excluded"]
        claim_id = f"use-case-mapping-20261127-proxy-{uc_id[len('use-case-'):]}-{pid}"
        claims.append({"id": claim_id, "kind": "claim", "name": f"Relevance of {pid} to {uc_id}",
                       "description": item["reason"], "status": "source_checked", "facets": {},
                       "source_ids": proto["source_ids"], "links": [{"relation": "subject", "target_id": uc_id}],
                       "attributes": attrs})
        applied.append({"use_case": uc_id, "test": pid, "claim": claim_id, "relevance": item["relevance"],
                        "reason": item["reason"], "evaluations": len(evs), "excluded_evaluations": len(item["excluded"]),
                        "passage": {"record": pid, "field": "description", "text": proto["description"]},
                        "source_locator": locator})
        additions.setdefault(uc_id, []).append(pid)

    changes = []
    for uc_id, pids in sorted(additions.items()):
        uc = json.loads(raw_lines[uc_id])
        base = hashlib.sha256(raw_lines[uc_id].encode("utf-8")).hexdigest()
        assert prov[uc_id]["sha256"] == base
        existing = {(l["relation"], l["target_id"]) for l in uc["links"]}
        for pid in pids:
            if ("assessed_by", pid) not in existing:
                uc["links"].append({"relation": "assessed_by", "target_id": pid})
        line = json.dumps(uc, ensure_ascii=False, separators=(",", ":"))
        changes.append({"id": uc_id, "base_sha256": base, "sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(), "record": uc})
    return sorted(claims, key=lambda c: c["id"]), changes, applied


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--check"]
    root, out = Path(args[0]), Path(args[1])
    claims, changes, applied = build(root)
    text = "".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) + "\n" for c in claims)
    if "--check" in sys.argv:
        assert (out / "batch.jsonl").read_text() == text, "batch.jsonl differs from rebuild"
        print(f"{len(claims)} claims verified against rebuild")
    else:
        (out / "batch.jsonl").write_text(text)
        (out / "changes.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) + "\n" for c in changes))
        (out / "applied.jsonl").write_text("".join(json.dumps(a, ensure_ascii=False) + "\n" for a in applied))
        print(f"Wrote {len(claims)} claims and {len(changes)} use-case changes to {out}")
