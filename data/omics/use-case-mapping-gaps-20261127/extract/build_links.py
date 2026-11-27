#!/usr/bin/env python3
"""Build relevance-judgement claims and use-case changes for batch use-case-mapping-gaps-20261127.

  python3 data/omics/use-case-mapping-gaps-20261127/extract/build_links.py <repo-root> <out-dir> [--check]

Follows data/omics/use-case-variant-links-20261123/extract/build_links.py: each link names an
existing protocol, every evaluation listed as reviewed passes the same evidence gates
(shared/omics/use-cases.ts evaluationBlocker), and the use case gains an assessed_by link.
The candidates come from kb/curation/use_case_mapping_candidates.jsonl
(docs/reviews/2026-11-27-use-case-mapping-gaps.md).
"""
import hashlib
import json
import sys
from pathlib import Path

NOW = "2026-11-27T18:00:00Z"
REVIEW_DOC = "docs/reviews/use-cases/use-case-mapping-gaps-2026-11-27.md"
REVIEWER_NOTE = (
    "Claude checked each protocol's scope against the use case's question, endpoint and exclusions, and "
    "verified the evaluation gates and source hashes in the store. The agent that drafted the link also "
    "reviewed it, so this is not the second-worker review docs/use-cases.md requires. No human "
    "scientific review; an independent verification pass is required before merge."
)

CELL = "use-case-cell-type-annotation-transfer"
MASS = "use-case-mass-spectrum-molecule-shortlisting"
PHENO = "use-case-phenotype-perturbation-selection"

CELL_LIMITS = ["Labels come from the atlas or study annotation, which the use case notes are not infallible ground truth."]
MASS_LIMITS = ["Recall depends on the candidate pool; compare rows only within one pool and split."]

# (use case, protocol, headline metric, relevance, endpoint, rationale, constraints, limitations)
LINKS = [
    (CELL, "hycell-20261106-protocol-annotation-transfer-knn", "macro-f1", "proxy",
     "Macro F1 of cell-type labels transferred to a held-out batch by a 15-nearest-neighbour classifier on each model's embedding",
     "Labels from a reference are transferred to a held-out batch and scored against its annotation, the use case's labelling task. Proxy, as the store's other annotation-transfer protocols are: it scores embeddings through a fixed classifier and has no unassigned class.",
     ["Compare rows only within this protocol: the classifier is fixed and the models differ only in their embedding."],
     CELL_LIMITS + ["No unassigned group is scored, so recognising unsupported cell populations is not measured."]),
    (CELL, "hycell-20261106-protocol-annotation-transfer-lr", "macro-f1", "proxy",
     "Macro F1 of cell-type labels transferred to a held-out batch by a logistic-regression classifier on each model's embedding",
     "The same transfer as the 15-nearest-neighbour protocol with a logistic-regression classifier. Proxy for the same reasons.",
     ["Compare rows only within this protocol."],
     CELL_LIMITS + ["No unassigned group is scored."]),
    (CELL, "hycell-20261106-protocol-annotation-finetuned", "macro-f1", "proxy",
     "Macro F1 of cell-type labels predicted for a held-out batch after fine-tuning on the labelled other batches",
     "Fine-tuned annotation of a held-out batch, scored against its labels. Proxy: one study, one model family, no unassigned class.",
     ["One fine-tuned configuration per model; compare rows only within this protocol."],
     CELL_LIMITS),
    (CELL, "scfoundation-2024-supp-table4-task-zheng68k", "macro-f1", "proxy",
     "Macro F1 of cell-type annotation on the Zheng68K subset used in scFoundation Supplementary Table 4",
     "Supervised cell-type annotation scored by macro F1, the same kind of comparison as the Chen et al. annotation protocols this use case maps as proxy.",
     ["The split manifest is not published; compare rows only within this protocol."],
     CELL_LIMITS),
    (CELL, "scfoundation-2024-supp-table4-task-segerstolpe", "macro-f1", "proxy",
     "Macro F1 of cell-type annotation on the Segerstolpe pancreas subset used in scFoundation Supplementary Table 4",
     "Supervised cell-type annotation scored by macro F1, as for Zheng68K.",
     ["The split manifest is not published; compare rows only within this protocol."],
     CELL_LIMITS),
    (CELL, "ucc-research-protocol-sctab-donor-bootstrap", "macro-f1", "proxy",
     "Macro F1 on donor-held-out known cell labels, ontology-adjusted, over seeded fits with a donor bootstrap (scTab Supplementary Table 1b)",
     "The donor-bootstrap companion of the scTab seeded-fit protocol this use case already maps as proxy.",
     ["Keep apart from the scTab seeded-fit rows: the bootstrap changes the estimate's denominator."],
     CELL_LIMITS + ["No whole-study, disease-shift or unknown-type conclusion, as the protocol states."]),
    (MASS, "lit-otheromics-20261011-msgwild-protocol-mass-retrieval-hit-rate-5", "top-5-accuracy", "proxy",
     "Hit rate@5 of MassSpecGym mass-based retrieval on the test fold",
     "The Hit rate@5 column of the same MassSpecGym in the Wild table whose Hit rate@1 and @20 columns this use case maps as proxy.",
     ["Mass-based candidate pool; compare only within MassSpecGym's test fold."], MASS_LIMITS),
    (MASS, "lit-otheromics-20261011-msgwild-protocol-mass-retrieval-mces-1", "top-1-mces", "proxy",
     "MCES@1 of MassSpecGym mass-based retrieval on the test fold: structural distance of the top candidate to the true molecule",
     "The MCES@1 column of the same table; a shortlisting endpoint that credits near misses.",
     ["MCES is a distance, lower is better; do not pool with hit rates."], MASS_LIMITS),
] + [
    (MASS, f"msalign-2026-table3-task-{pool}-no-formula-r-{k}", f"top-{k}-accuracy", "proxy",
     f"Recall@{k} of retrieval from 256 mass-matched PubChem candidates per spectrum with no formula, on {label}",
     f"The formula-free {label} column of the MSAlign Table 3 whose MassSpecGym formula-free columns this use case maps as proxy. Formula-conditioned columns stay out, as the use case's exclusions require.",
     [f"{label} only; the domain differs from MassSpecGym and rows are not pooled across pools."], MASS_LIMITS)
    for pool, label in (("nplib1", "NPLIB1"), ("spectraverse", "Spectraverse")) for k in (1, 5, 20)
] + [
    (PHENO, "pheno-20261022-protocol-song2025-simple-hit-classification", "f1-score", "proxy",
     "F1 of yes/no predictions that a stated CRISPR perturbation of a gene in a cell line produces a stated phenotype, against high-confidence BioGRID-ORCS hits",
     "A system predicts whether perturbing a named gene produces the phenotype, which is the choice the use case makes. Proxy, as the retrospective AssayBench-Loop protocol is: no prospective selection under a budget.",
     ["Retrospective; labels are each screen's own hit call."],
     ["Four BioGRID-ORCS screens; hits include common-essential genes."]),
    (PHENO, "pheno-20261022-protocol-song2025-difficult-hit-classification", "f1-score", "proxy",
     "F1 of yes/no predictions that a CRISPR knockout produces a complex phenotype, on balanced queries from two late-2024 screen publications",
     "The harder companion of the simple benchmark, on screens published after most models' training data.",
     ["Retrospective; two systems only."],
     ["Two screen publications; balanced queries do not reflect a real screen's hit rate."]),
]
def load_store(root: Path):
    records = {}
    raw_lines = {}
    for pat in ("data/entities/*.jsonl", "data/evidence/evaluations/*.jsonl", "data/evidence/results/*.jsonl"):
        for f in sorted(root.glob(pat)):
            for line in f.read_text().splitlines():
                if not line:
                    continue
                d = json.loads(line)
                records[d["id"]] = d
                raw_lines[d["id"]] = line
    prov = {}
    for f in sorted((root / "data/provenance/records").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if not line:
                continue
            d = json.loads(line)
            prov[d["id"]] = d
    return records, raw_lines, prov


def scoped_concern_targets(records: dict) -> set[str]:
    targets = set()
    for r in records.values():
        if r["kind"] == "source":
            for item in r["attributes"].get("evidence_concerns") or []:
                if isinstance(item, dict) and item.get("applies_to"):
                    for tid in item["applies_to"]:
                        targets.add(tid)
    return targets


def build(root: Path):
    records, raw_lines, prov = load_store(root)
    scoped = scoped_concern_targets(records)

    whole_concerned = set()
    for r in records.values():
        if r["kind"] == "source":
            for item in r["attributes"].get("evidence_concerns") or []:
                if isinstance(item, str) or (isinstance(item, dict) and not item.get("applies_to")):
                    whole_concerned.add(r["id"])

    def clean_source(sid: str) -> bool:
        s = records.get(sid)
        return bool(s and s["kind"] == "source" and s["status"] in ("source_checked", "reproduced") and sid not in whole_concerned)

    evals_by_proto = {}
    results_by_eval = {}
    for r in records.values():
        if r["kind"] == "evaluation":
            for l in r["links"]:
                if l["relation"] == "assessment":
                    evals_by_proto.setdefault(l["target_id"], []).append(r)
        elif r["kind"] == "result":
            for l in r["links"]:
                if l["relation"] == "evaluation":
                    results_by_eval.setdefault(l["target_id"], []).append(r)

    batch_claims = []
    batch_claims = []
    uc_additions = {}
    for uc_id, proto_id, hmetric, relevance, endpoint, rationale, constraints, limits in LINKS:
        proto = records[proto_id]
        assert proto["kind"] == "protocol" and proto["status"] == "source_checked", proto_id
        if not all(clean_source(s) for s in proto["source_ids"]):
            print(f"skip {proto_id}: a protocol source is unchecked or carries an evidence concern", file=sys.stderr)
            continue
        clean_evs = []
        for e in sorted(evals_by_proto.get(proto_id, []), key=lambda x: x["id"]):
            if e["status"] not in ("source_checked", "reproduced"):
                continue
            cfgs = [records.get(l["target_id"]) for l in e["links"] if l["relation"] == "system"
                    and records.get(l["target_id"], {}).get("kind") == "configuration"]
            if not cfgs or any(c["status"] not in ("source_checked", "reproduced") or any(not clean_source(s) for s in c["source_ids"]) for c in cfgs):
                continue
            dts = [records.get(l["target_id"]) for l in e["links"] if l["relation"] == "data"]
            if any(not d or d["kind"] not in ("dataset", "dataset_subset") or d["status"] in ("disputed", "excluded", "superseded")
                   or any(not clean_source(s) for s in d["source_ids"]) for d in dts):
                continue
            rows = [r for r in results_by_eval.get(e["id"], []) if r["status"] in ("source_checked", "reproduced")]
            if not rows or any(any(not clean_source(s) for s in (r["source_ids"] + e["source_ids"])) for r in rows):
                continue
            assessments = [records.get(l["target_id"]) for l in e["links"] if l["relation"] == "assessment"]
            base_path = ([e["id"]] + [l["target_id"] for l in e["links"] if l["relation"] in ("system", "assessment", "data")]
                         + [l["target_id"] for a in assessments if a for l in a["links"] if l["relation"] == "part_of"])
            if any(pid in scoped for r in rows for pid in ([r["id"]] + base_path)):
                continue
            clean_evs.append(e["id"])
        if not clean_evs:
            print(f"skip {proto_id}: no evaluation passes the gates", file=sys.stderr)
            continue
        locator = proto["attributes"].get("source_locator", "See protocol record")
        attrs = {
            "field": f"links:assessed_by:{proto_id}", "value": proto_id, "relevance": relevance,
            "endpoint": endpoint, "rationale": rationale, "constraints": constraints, "limitations": limits,
            "citation_locators": [{"source_id": s, "locator": locator} for s in proto["source_ids"][:2]],
            "source_locator": locator, "headline_metric": hmetric,
            "reason": "Use-case mapping gaps pass, 27 November 2026 (docs/reviews/2026-11-27-use-case-mapping-gaps.md).",
            "review": {"method": ["scope-review", "source-hash-verification"], "reviewer": ["claude"],
                       "reviewer_note": REVIEWER_NOTE, "reviewed_at": NOW,
                       "note": f"Scope and evaluation gates checked for {len(clean_evs)} evaluations against {REVIEW_DOC}."},
            "reviewed_evaluations": clean_evs,
        }
        batch_claims.append({"id": f"use-case-mapping-20261127-{proto_id}", "kind": "claim",
                             "name": f"Relevance of {proto_id} to {uc_id}", "description": rationale, "status": "source_checked",
                             "facets": {}, "source_ids": proto["source_ids"], "links": [{"relation": "subject", "target_id": uc_id}],
                             "attributes": attrs})
        uc_additions.setdefault(uc_id, []).append(proto_id)
    changes = []
    for uc_id, proto_ids in uc_additions.items():
        uc = json.loads(raw_lines[uc_id])
        base_sha = hashlib.sha256(raw_lines[uc_id].encode("utf-8")).hexdigest()
        assert prov[uc_id]["sha256"] == base_sha
        existing = {(l["relation"], l["target_id"]) for l in uc["links"]}
        for pid in proto_ids:
            if ("assessed_by", pid) not in existing:
                uc["links"].append({"relation": "assessed_by", "target_id": pid})
        new_line = json.dumps(uc, ensure_ascii=False, separators=(",", ":"))
        changes.append({"id": uc_id, "base_sha256": base_sha, "sha256": hashlib.sha256(new_line.encode("utf-8")).hexdigest(), "record": uc})
    return sorted(batch_claims, key=lambda c: c["id"]), changes


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--check"]
    root, out_dir = Path(args[0]), Path(args[1])
    claims, changes = build(root)
    text = "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in claims)
    batch_file = out_dir / "batch.jsonl"
    if "--check" in sys.argv:
        assert batch_file.read_text() == text, "batch.jsonl differs from rebuild"
        print(f"{len(claims)} claims verified against rebuild")
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        batch_file.write_text(text)
        (out_dir / "changes.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) + "\n" for c in changes))
        print(f"Wrote {len(claims)} claims and {len(changes)} changes to {out_dir}")
