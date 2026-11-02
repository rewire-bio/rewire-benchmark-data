"""Record the review of the Enchant v3 batch (docs/reviews/2026-11-02-enchant-v3.md).

Usage: python3 -I review.py <batch folder>

Run after build.py, which asserts every quoted figure against the pinned pages. Sets the sources to
source_checked and adds a review block. The model stays discovered, as issue #229 asks: it is listed, with a
source-linked profile, and no performance is claimed. The extractor and the reviewer were the same agent.
"""
import json
import os
import sys

OUT = sys.argv[1]
REVIEW = {"method": ["source-hash-verification", "automated-source-review", "ai-assisted-source-review"],
          "reviewer": ["claude"],
          "reviewer_note": "Claude agent; no human review claimed. Extractor and reviewer were the same agent in the same session.",
          "date": "2026-11-02",
          "method_note": ("The three pages re-fetched on 2026-11-02 with identical SHA-256; build.py asserts each quoted "
                          "figure and statement against the page text. Figure 7 rendered from its SVG and read; not extracted."),
          "note": "Descriptive records only; no result. Verdict in docs/reviews/2026-11-02-enchant-v3.md."}
recs = [json.loads(l) for l in open(os.path.join(OUT, "batch.jsonl"))]
for r in recs:
    r["status"] = "discovered" if r["kind"] == "model" else "source_checked"
    r["attributes"]["review"] = dict(REVIEW)
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(f"{len(recs)} records reviewed")
