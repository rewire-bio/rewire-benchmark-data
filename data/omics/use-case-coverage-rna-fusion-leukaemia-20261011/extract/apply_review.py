"""Record the independent review on a regenerated batch: status source_checked, review blocks on results,
sources and judgement claims, and reviewed_evaluations on each judgement.

Usage: python3 -I apply_review.py <batch-folder> <reviewer-id> <review-doc>
Run after the extractor, which writes every record as needs_review with an extraction-only review block.
"""
import sys, os, json

folder, reviewer, doc = sys.argv[1:4]
DATE, AT = "2026-10-11", "2026-10-11T23:30:00Z"
NOTE = f"Claude research agent {reviewer}, independent of the extractor uc-oncology; no human review claimed"
path = os.path.join(folder, "batch.jsonl")
recs = [json.loads(l) for l in open(path)]
evals_by_protocol = {}
for r in recs:
    if r["kind"] == "evaluation":
        p = next(l["target_id"] for l in r["links"] if l["relation"] == "assessment")
        evals_by_protocol.setdefault(p, []).append(r["id"])
for r in recs:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] == "result":
        ext = a["review"]
        a["review"] = {"method": ["source-hash-verification"] + ext["method"] + ["independent-cell-check"],
                       "method_note": "Independent re-retrieval and hash check; reviewer's own parser compared every table cell; stratified hand check against the rendered table or quoted sentence.",
                       "reviewer": ["claude"], "reviewer_note": NOTE, "date": DATE,
                       "artifact_sha256": ext["artifact_sha256"], "retrieval_url": ext["retrieval_url"],
                       "note": "Extraction: " + ext["method_note"] + f" Independent review {DATE}: value, locator, metric, unit, direction and linked configuration and protocol checked; corrections from the review applied by the extractor as listed in review.md ({doc})."}
    elif r["kind"] == "source":
        a["review"] = {"method": ["source-hash-verification"], "method_note": "Artifact re-retrieved or unpacked and SHA-256 matched.",
                       "reviewer": ["claude"], "reviewer_note": NOTE, "date": DATE}
    elif r["kind"] == "claim" and r["id"].startswith("use-case-mapping-"):
        excluded = {e["id"] for e in a.get("excluded_evaluations", [])}
        a["reviewed_evaluations"] = sorted(e for e in evals_by_protocol[a["value"]] if e not in excluded)
        a["review"] = {"method": ["ai-assisted-source-review", "scope-review"],
                       "method_note": "Reviewer checked the endpoint against the use case's inputs and output, the relevance rating and the limitations; every evaluation on the protocol had its values checked in the batch review. Corrections listed in review.md were applied by the extractor.",
                       "reviewer": ["claude"], "reviewer_note": NOTE, "reviewed_at": AT,
                       "note": f"Automated review; not human scientific review. See {doc}."}
with open(path, "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(folder, len(recs))
