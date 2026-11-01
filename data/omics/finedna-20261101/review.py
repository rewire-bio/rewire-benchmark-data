"""Record the review of the FineDNA batch (docs/reviews/2026-11-01-finedna.md).

Usage: python3 -I review.py <batch folder>

Run after build.py, which asserts every quoted figure against the pinned cards. Sets the four records to
source_checked and adds a review block. The extractor and the reviewer were the same agent.
"""
import json
import os
import sys

OUT = sys.argv[1]
REVIEW = {"method": ["source-hash-verification", "automated-source-review", "ai-assisted-source-review"],
          "reviewer": ["claude"],
          "reviewer_note": "Claude agent; no human review claimed. Extractor and reviewer were the same agent in the same session.",
          "date": "2026-11-01",
          "method_note": ("Both cards re-read at their pinned commits with SHA-256 checked; build.py asserts each quoted "
                          "count and statement against the card text."),
          "note": "Descriptive records only; no result. Verdict in docs/reviews/2026-11-01-finedna.md."}
recs = [json.loads(l) for l in open(os.path.join(OUT, "batch.jsonl"))]
for r in recs:
    r["status"] = "source_checked"
    if r["kind"] in ("source", "dataset", "model"):
        r["attributes"]["review"] = dict(REVIEW)
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(f"{len(recs)} records set to source_checked")
