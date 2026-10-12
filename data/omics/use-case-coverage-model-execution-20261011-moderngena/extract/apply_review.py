"""Record the independent review by reviewer-exec on a regenerated batch, as specified in review A2 of
docs/reviews/use-cases/diagnostic-genomics-model-execution-2026-10-12.md: status source_checked on every record,
the reviewer's review block on results, descriptive claims and judgement claims, and reviewed_evaluations on
each judgement.

Usage: python3 -I apply_review.py <batch-folder> <clair3gpu|moderngena|fp8genomeocean|genepi|dnascopehybrid>
Run after build.py, which writes every record as needs_review with an extraction-only review block.
"""
import csv
import json
import os
import sys

folder, key = sys.argv[1:3]
AT = "2026-10-12T07:50:32Z"
PARSE = ["source-hash-verification", "pdf-text-parse", "rendered-source-visual-check", "independent-cell-check"]
BIORXIV_TEXT = "Archived PDF matched the pinned SHA-256; a fresh bioRxiv download had the same text-layer SHA-256. "
METHOD = {
    "clair3gpu": (PARSE, "Re-downloaded the Europe PMC supplementaryFiles zip and matched the PDF member's SHA-256. Supplementary Table 1 parsed from pdftotext -layout with a separate review script; Supplementary Tables 2 and 3 read in full by the reviewer from the embedded image and a 250 dpi render of page 3, written down independently and compared cell by cell (350 cells). Article XML re-downloaded and matched."),
    "moderngena": (PARSE, BIORXIV_TEXT + "Appendix B Table 2 parsed from pdftotext -layout with a separate review script (108 cells, 16 dashes) and every row read against a 200 dpi render of page 9."),
    "fp8genomeocean": (PARSE, BIORXIV_TEXT + "Tables 3 and 4 parsed from pdftotext -layout with a separate review script, including every ± value, and every cell read against a 170 dpi render of page 8."),
    "genepi": (PARSE, "Re-downloaded the Europe PMC supplementaryFiles zip and matched the PDF member's SHA-256; article XML re-downloaded and matched. Table S1 parsed from pdftotext -layout with a separate review script, minutes recomputed from the printed hours and minutes, and every cell read against a 150 dpi render of page 7."),
    "dnascopehybrid": (["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
                       "Re-downloaded the Europe PMC article XML and matched its SHA-256. Table 2 parsed from the XML table cells with a separate review script and every cell read in the parsed output."),
}
VALUE_NOTE = ("Independent review 2026-10-12: printed value, numeric value, metric, qualifier, unit, direction, uncertainty, "
              "locator and configuration and protocol identity match the source. Transcribed, not reproduced.")
JUDGEMENT_REVIEW = {
    "method": ["source-hash-verification", "independent-cell-check", "scope-review"], "reviewer": ["claude"],
    "reviewer_note": "Claude (Opus 5.5) research agent uc-execution extracted and drafted; Claude (Opus 5.5) review agent reviewer-exec checked every value and this judgement against the pinned sources",
    "reviewed_at": AT,
    "note": "Bounded primary-source transcription with independent cell check and relevance review. No execution, reproduction, qualified human scientific review or clinical validation.",
}

path = os.path.join(folder, "batch.jsonl")
recs = [json.loads(l) for l in open(path)]
sources = {r["id"]: r for r in recs if r["kind"] == "source"}
value_source = {row["record_id"]: row["source_id"] for row in csv.DictReader(open(os.path.join(folder, "claims.csv")))}
evals_by_protocol = {}
for r in recs:
    if r["kind"] == "evaluation":
        evals_by_protocol.setdefault(r["attributes"]["protocol"], []).append(r["id"])
method, method_note = METHOD[key]
for r in recs:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] == "claim" and r["id"].startswith("use-case-mapping-"):
        excluded = {e["id"] for e in a.get("excluded_evaluations", [])}
        a["reviewed_evaluations"] = sorted(e for e in evals_by_protocol[a["value"]] if e not in excluded)
        a["review"] = dict(JUDGEMENT_REVIEW)
    elif r["kind"] in ("result", "claim"):
        src = sources[value_source[r["id"]]]["attributes"]
        a["review"] = {"method": method, "method_note": method_note, "reviewer": ["claude"],
                       "reviewer_note": "Claude (Opus 5.5) review agent reviewer-exec, independent of the extractor uc-execution; no human review claimed",
                       "reviewed_at": AT, "artifact_sha256": src["artifact_sha256"], "retrieval_url": src["artifact_url"],
                       "note": VALUE_NOTE}
with open(path, "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(folder, len(recs))
