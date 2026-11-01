"""Record the review of the Alavi 2026 v2 batch (docs/reviews/2026-11-01-alavi-v2-rerun.md).

Usage: python3 -I review.py <batch folder>

Run after build.py and check_cells.py. Sets every record to source_checked and replaces the extraction
review on results and the claim with the review block. The extractor and the reviewer were the same agent.
"""
import json
import os
import sys

OUT = sys.argv[1]
DATE = "2026-11-01"
SHA = "07bd32fffc1b31c222d43b0b18c213928e3fe111cc71c02fe2f95e64e6f7a798"
URL = "https://www.biorxiv.org/content/10.64898/2026.10.02.756289v2.full.pdf"
REVIEWER_NOTE = ("Claude agent for issue #213; no human review claimed. Extractor and reviewer were the same agent "
                 "in the same session.")
DATED = "docs/reviews/2026-11-01-alavi-v2-rerun.md"
RESULT_NOTE = ("Matched by two parses of the pinned PDF: pdftotext -layout in build.py and pdftotext -raw in "
               "check_cells.py (cell-check.tsv, 56 of 56). Count, percentage, accuracy and PPV arithmetic checked "
               f"for every row. Verdict in {DATED}.")

checks = {l.split("\t")[0]: l.rstrip("\n").split("\t")[6] for l in open(os.path.join(OUT, "cell-check.tsv")) if not l.startswith("id\t")}
recs = [json.loads(l) for l in open(os.path.join(OUT, "batch.jsonl"))]
reruns = dict(l.rstrip("\n").split("\t") for l in open(os.path.join(OUT, "supersession.tsv")) if not l.startswith("version_2"))
for r in recs:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] == "result":
        assert checks[r["id"]] == "match", r["id"]
        a["review"] = {"method": ["deterministic-table-parse", "source-hash-verification", "automated-source-review",
                                  "ai-assisted-source-review"],
                       "method_note": a["review"]["method_note"], "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
                       "date": DATE, "artifact_sha256": SHA, "retrieval_url": URL,
                       "note": RESULT_NOTE + (f" Replaces version 1 result {reruns[r['id']]}, which stays disputed and is not linked because the release drops records that link to disputed ones." if r["id"] in reruns else "")}
    elif r["kind"] == "claim":
        a["review"].update(reviewer_note=REVIEWER_NOTE,
                           note=("Checked that resolved_by names the version 2 source and its 56 AlphaGenome results, and that "
                                 "each of the 28 rows of supersession.tsv pairs a version 2 result with the disputed version 1 "
                                 f"result of the same protocol and column. Records a state change; nothing was reproduced. Verdict in {DATED}."))
assert len(checks) == sum(r["kind"] == "result" for r in recs) == 56
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(f"{len(recs)} records set to source_checked")
