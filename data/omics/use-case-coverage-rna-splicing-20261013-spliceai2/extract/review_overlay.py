"""Apply the independent review of 2026-10-13 to batch.jsonl written by build_batch.py.

Usage: python3 -I extract/review_overlay.py <batch folder>

Sets every record to source_checked, replaces the review block of each result and claim with
the reviewer's, and lists the reviewed evaluations on each relevance judgement. Values are not
touched; the corrections themselves are in build_batch.py (review corrections 1 to 7).
"""
import json
import os
import sys

folder = sys.argv[1]
path = os.path.join(folder, "batch.jsonl")
records = [json.loads(line) for line in open(path, encoding="utf-8")]
P = "rna-splicing-20261013-spliceai2-"
DATE = "2026-10-13"
REVIEW = "docs/reviews/use-cases/spliceai2-2026-10-13.md"
REVIEWER_NOTE = ("Claude (Opus 5.5) research agent, independent reviewer; did not extract this batch; "
                 "no human review claimed")
NOTE = (f"Checked against the pinned source by the independent reviewer; verdict and correction list in {REVIEW} "
        "and this batch's review.json. Developer-reported value, not reproduced.")

ED2 = ("Reviewer's own pdftotext -layout parse of Extended Data Fig. 2 (page 52): the four model rows of the top block, "
       "17 values each, matched one-to-one to the 68 stored results by model, panel and stratum; page rendered at 110 dpi "
       "and column labels read (All, Exon, Near intronic, Deep intronic; All, Exon, Intron). The All column agrees with the "
       "Fig. 1d bar labels on the rendered page 11.")
BARS = ("Bar label read on the reviewer's render of the page at 120 dpi and in the text layer; bar order and colours "
        "checked against the panel legend (SpliceAI, Pangolin, AlphaGenome, SpliceAI2).")
TEXT = "Sentence located in the reviewer's own pdftotext output of the pinned PDF; printed value and its context re-read."

evals_by_protocol = {}
for r in records:
    if r["kind"] == "evaluation":
        proto = next(l["target_id"] for l in r["links"] if l["relation"] == "assessment")
        evals_by_protocol.setdefault(proto, []).append(r["id"])

for r in records:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] not in ("result", "claim"):
        continue
    old = a["review"]
    loc = a.get("source_locator", "")
    if r["kind"] == "result":
        if "Extended Data Fig. 2" in loc:
            method, note = ["pdf-text-parse", "independent-cell-check", "rendered-source-visual-check"], ED2
        elif loc.startswith(("Fig. 3c", "Fig. 3f", "Fig. 4g")):
            method, note = ["pdf-text-parse", "independent-cell-check", "rendered-source-visual-check"], BARS
        else:
            method, note = ["pdf-text-parse", "independent-cell-check"], TEXT
    elif a.get("field", "").startswith("links:assessed_by:"):
        proto = a["value"]
        a["reviewed_evaluations"] = sorted(evals_by_protocol[proto])
        method = ["scope-review", "independent-cell-check"]
        note = ("Judged against the use case's question, inputs and output in data/entities/use-cases.jsonl and the existing "
                "judgements for the same use case; endpoint, limitations and every evaluation on the protocol re-read in the pinned PDF.")
    elif r["id"].endswith("claim-licence"):
        method = ["source-hash-verification", "independent-cell-check"]
        note = "LICENSE and README re-downloaded at commit 1dcd2a1; SHA-256 values match; quoted terms re-read."
    elif r["id"].endswith("claim-training-data"):
        method = ["source-hash-verification", "pdf-text-parse", "independent-cell-check"]
        note = ("Supplementary Table 1 re-downloaded (SHA-256 matches) and its Homo_sapiens and Total rows re-read; "
                "main-text sentence located in the reviewer's pdftotext output.")
    else:
        method = ["pdf-text-parse", "independent-cell-check"]
        note = TEXT
    extraction = old.get("method_note")
    a["review"] = {
        "method": method,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "artifact_sha256": old["artifact_sha256"],
        "retrieval_url": old["retrieval_url"],
        "method_note": note,
        "note": NOTE + (f" Extraction method: {extraction}" if extraction else ""),
    }

with open(path, "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(len(records), "records reviewed")
