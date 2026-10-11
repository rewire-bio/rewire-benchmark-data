"""Review corrections L1 and L2 to records already in the store, and the approved assessed_by links.

Usage: python3 -I apply_store_changes.py <repo-root> <batch-folder>
Run after `records add` of this batch. Edits, in place and in the store's own line format:
- evidence-expansion-p2-lipp-2026-6ff34f2f709a: adds the limitations moved from the removed batch source (L1);
- lit-041 and lit-042: status superseded (L2; the new full-set results carry the supersedes links);
- use-case-structural-hypotheses-experiments: assessed_by links proposed in this batch's use-case-links.json.
Then writes corrections.jsonl with the metadata-correction claim for the source limitations. Record the
edits with `npm run records -- change <review> <batch> <ids>` and add corrections.jsonl with `records -- add`.
"""
import json, os, sys

root, folder = sys.argv[1:3]
fmt = lambda r: json.dumps(r, separators=(",", ":"), ensure_ascii=False)


def edit(path, rid, fn):
    lines = open(path, encoding="utf-8").read().split("\n")
    for i, line in enumerate(lines):
        if line.startswith('{"id":"%s",' % rid):
            r = json.loads(line)
            assert fmt(r) == line, f"{rid}: line does not round-trip"
            prev = json.loads(line)
            fn(r)
            lines[i] = fmt(r)
            open(path, "w", encoding="utf-8").write("\n".join(lines))
            return prev, r
    raise KeyError(rid)


lim = json.load(open(os.path.join(folder, "extract", "source-limitations.json")))
src_path = os.path.join(root, "data/entities/sources.jsonl")
prev, new = edit(src_path, lim["source_id"], lambda r: (r["attributes"].__setitem__("limitations", lim["limitations"]) if "limitations" not in r["attributes"] else (_ for _ in ()).throw(AssertionError("limitations already present"))))

res_path = os.path.join(root, "data/evidence/results.jsonl")
for rid, value in (("lit-041", "60.7"), ("lit-042", "46.8")):
    def sup(r, value=value):
        assert r["attributes"]["printed_value"] == value and r["status"] == "source_checked", r["id"]
        r["status"] = "superseded"
    edit(res_path, rid, sup)

links = json.load(open(os.path.join(folder, "use-case-links.json")))["links"]
uc_path = os.path.join(root, "data/entities/use-cases.jsonl")
for uc in sorted({l["use_case"] for l in links}):
    def add(r, uc=uc):
        for l in links:
            if l["use_case"] == uc:
                link = {"relation": l["relation"], "target_id": l["target_id"]}
                assert link not in r["links"]
                r["links"].append(link)
    edit(uc_path, uc, add)

claim = {
    "id": "metadata-correction-lit-structure-20261011-lipp-source-limitations",
    "kind": "claim",
    "name": "LiPP benchmark set source: attributes.limitations",
    "description": "Limitations moved onto the store's existing source record for these bytes when the batch's duplicate source record was removed (review correction L1), with the dash-cell count corrected (L3).",
    "status": "source_checked", "facets": {}, "source_ids": [lim["source_id"]],
    "links": [{"relation": "subject", "target_id": lim["source_id"]}],
    "attributes": {
        "field": "attributes.limitations",
        "previous_value": "absent",
        "value": json.dumps(lim["limitations"], ensure_ascii=False),
        "source_locator": "Tables 2 and 3 (dash cells and PoseBusters columns); Figures (not extracted)",
        "review": {"method": ["ai-assisted-source-review"],
                   "method_note": "Reviewer specified the move and the corrected dash count (4 in Table 2, 9 in Table 3) after re-parsing both tables from the pinned JATS XML.",
                   "reviewer": ["claude"],
                   "reviewer_note": "Claude review agent reviewer-ps-2, independent of the extractor lit-protein-structure; no human review claimed",
                   "date": "2026-10-11", "note": "Corrections L1 and L3 of the 2026-10-11 review; see review.md."}},
}
with open(os.path.join(folder, "corrections.jsonl"), "w") as f:
    f.write(fmt(claim) + "\n")
print("edited", lim["source_id"], "lit-041", "lit-042", sorted({l["use_case"] for l in links}))
