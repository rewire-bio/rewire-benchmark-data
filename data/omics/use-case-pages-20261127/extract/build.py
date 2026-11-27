#!/usr/bin/env python3
"""Build the new use cases and their relevance judgements for batch use-case-pages-20261127.

  python3 data/omics/use-case-pages-20261127/extract/build.py <repo-root> <out-dir> [--check]

use-cases.json holds each use case's text; links.json holds the rules that pick its protocols, with
one reason per rule. A protocol is linked only when it passes the evaluation gates of
shared/omics/use-cases.ts, checked here as data/omics/use-case-mapping-gaps-20261127 checks them.
Writes batch.jsonl (the use_case records and claims), changes.jsonl (empty: no existing record
changes) and applied.jsonl (one row per link with the protocol passage it rests on).
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = "2026-11-27T20:00:00Z"
BATCH = "data/omics/use-case-pages-20261127"
REVIEW_DOC = "docs/reviews/use-cases/use-case-pages-2026-11-27.md"
REVIEWER_NOTE = (
    "Claude wrote these from the benchmark and protocol records and their saved sources, checked every "
    "linked protocol against the use case's question and exclusions, and verified the evaluation gates "
    "in the store. Drafter and reviewer are the same agent, so this is not the second-worker review "
    "docs/use-cases.md requires. No human scientific review; an independent verification pass is needed."
)

spec = importlib.util.spec_from_file_location(
    "gaps", HERE.parents[1] / "use-case-mapping-gaps-20261127/extract/build_links.py")
gaps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gaps)


def eligible_evaluations(records, clean, scoped, evals_by_proto, results_by_eval, proto_id):
    """The evaluations on the protocol that can support an active judgement, by the same gates."""
    out = []
    for e in sorted(evals_by_proto.get(proto_id, []), key=lambda x: x["id"]):
        if e["status"] not in ("source_checked", "reproduced"):
            continue
        cfgs = [records.get(l["target_id"]) for l in e["links"] if l["relation"] == "system"
                and records.get(l["target_id"], {}).get("kind") == "configuration"]
        if not cfgs or any(c["status"] not in ("source_checked", "reproduced")
                           or any(not clean(s) for s in c["source_ids"]) for c in cfgs):
            continue
        data = [records.get(l["target_id"]) for l in e["links"] if l["relation"] == "data"]
        if any(not d or d["kind"] not in ("dataset", "dataset_subset")
               or d["status"] in ("disputed", "excluded", "superseded")
               or any(not clean(s) for s in d["source_ids"]) for d in data):
            continue
        rows = [r for r in results_by_eval.get(e["id"], []) if r["status"] in ("source_checked", "reproduced")]
        if not rows or any(any(not clean(s) for s in (r["source_ids"] + e["source_ids"])) for r in rows):
            continue
        assessments = [records.get(l["target_id"]) for l in e["links"] if l["relation"] == "assessment"]
        path = ([e["id"]] + [l["target_id"] for l in e["links"] if l["relation"] in ("system", "assessment", "data")]
                + [l["target_id"] for a in assessments if a for l in a["links"] if l["relation"] == "part_of"])
        if any(pid in scoped for r in rows for pid in ([r["id"]] + path)):
            continue
        out.append(e["id"])
    return out


def build(root: Path):
    records, raw_lines, prov = gaps.load_store(root)
    scoped = gaps.scoped_concern_targets(records)
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

    protocols = sorted(r["id"] for r in records.values() if r["kind"] == "protocol")
    cases = json.loads((HERE / "use-cases.json").read_text())
    rules = json.loads((HERE / "links.json").read_text())
    picked, skipped = {}, []
    for rule in rules:
        inc = [re.compile(p) for p in rule["include"]]
        exc = [re.compile(p) for p in rule["exclude"]]
        for pid in protocols:
            if not any(p.search(pid) for p in inc) or any(p.search(pid) for p in exc):
                continue
            key = (rule["slug"], pid)
            if key in picked:
                continue
            proto = records[pid]
            if proto["status"] != "source_checked" or not all(clean(s) for s in proto["source_ids"]):
                skipped.append((*key, "the protocol or one of its sources is unreviewed or carries an evidence concern"))
                continue
            evs = eligible_evaluations(records, clean, scoped, evals_by_proto, results_by_eval, pid)
            if not evs:
                skipped.append((*key, "no evaluation on it passes the gates"))
                continue
            picked[key] = (rule["relevance"], rule["reason"], evs)

    batch, applied = [], []
    for case in cases:
        uc_id = f"use-case-{case['slug']}"
        links = sorted(pid for (slug, pid) in picked if slug == case["slug"])
        sources = sorted({s for pid in links for s in records[pid]["source_ids"]})
        assert sources, f"{uc_id} has no cited source"
        batch.append({
            "id": uc_id, "kind": "use_case", "name": case["name"], "description": case["question"],
            "status": "source_checked", "facets": {"areas": [case["area"]], "contexts": ["research"]},
            "source_ids": sources,
            "links": [{"relation": "assessed_by", "target_id": pid} for pid in links],
            "attributes": {
                "depth_tier": 1 if case["area"] in ("dna-genomes", "rna-transcriptomes")
                              else 2 if case["area"] in ("proteins-complexes", "protein-function", "protein-structure") else 3,
                "slug": case["slug"], "question": case["question"], "intended_users": case["intended_users"],
                "decision": case["decision"], "inputs": case["inputs"], "output": case["output"],
                "setting": case["setting"], "exclusions": case["exclusions"],
                "clinical_scope": "Research only. Nothing recorded here supports a clinical or diagnostic decision.",
                "evidence_gaps": case["evidence_gaps"], "search_terms": case["search_terms"],
                "citation_locators": [{"source_id": s, "locator": records[s]["attributes"].get("source_locator") or "See the source record"}
                                      for s in sources[:4]],
                "review": {"method": ["scope-review", "source-hash-verification"],
                           "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
                           "reviewed_at": NOW,
                           "note": f"Written from the benchmark and protocol records and reviewed against {REVIEW_DOC}."},
            },
        })
        for pid in links:
            relevance, reason, evs = picked[(case["slug"], pid)]
            proto = records[pid]
            locator = proto["attributes"].get("source_locator") or "See the protocol record"
            batch.append({
                "id": f"use-case-mapping-20261127-{case['slug']}-{pid}", "kind": "claim",
                "name": f"Relevance of {pid} to {uc_id}", "description": reason, "status": "source_checked",
                "facets": {}, "source_ids": proto["source_ids"],
                "links": [{"relation": "subject", "target_id": uc_id}],
                "attributes": {
                    "field": f"links:assessed_by:{pid}", "value": pid, "relevance": relevance,
                    "endpoint": proto["description"], "rationale": reason,
                    "constraints": [f"Compare rows only within this protocol: {proto['name']}."],
                    "limitations": list(proto["attributes"].get("limitations", []))[:3]
                                   or ["One study's evaluation; see the use case's evidence gaps."],
                    "citation_locators": [{"source_id": s, "locator": locator} for s in proto["source_ids"][:2]],
                    "source_locator": locator,
                    "reason": f"New use case pass, 27 November 2026 ({REVIEW_DOC}).",
                    "review": {"method": ["scope-review", "source-hash-verification"],
                               "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
                               "reviewed_at": NOW,
                               "note": f"Scope and evaluation gates checked for {len(evs)} evaluations against {REVIEW_DOC}."},
                    "reviewed_evaluations": evs,
                },
            })
            applied.append({"use_case": uc_id, "test": pid, "claim": f"use-case-mapping-20261127-{case['slug']}-{pid}",
                            "relevance": relevance, "reason": reason, "evaluations": len(evs),
                            "passage": {"record": pid, "field": "description", "text": proto["description"]},
                            "source_locator": locator})
    return sorted(batch, key=lambda r: (r["kind"] != "use_case", r["id"])), applied, sorted(set(skipped))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--check"]
    root, out_dir = Path(args[0]), Path(args[1])
    batch, applied, skipped = build(root)
    text = "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in batch)
    cases = [r for r in batch if r["kind"] == "use_case"]
    if "--check" in sys.argv:
        assert (out_dir / "batch.jsonl").read_text() == text, "batch.jsonl differs from rebuild"
        print(f"{len(cases)} use cases and {len(batch) - len(cases)} claims verified against rebuild")
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "batch.jsonl").write_text(text)
        (out_dir / "applied.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in applied))
        for slug, pid, why in skipped:
            print(f"skip {slug}: {pid}: {why}", file=sys.stderr)
        print(f"Wrote {len(cases)} use cases and {len(batch) - len(cases)} claims to {out_dir}")
        for c in cases:
            print(f"  {c['id']}: {len(c['links'])} protocols")
