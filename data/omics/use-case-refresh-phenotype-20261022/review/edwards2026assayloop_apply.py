"""Apply the 2026-10-22 independent review of parts/edwards2026assayloop.jsonl.

Run once from the repository root: python3 -I <this file>. Rulings and reasons are in
notes/edwards2026assayloop.md under "Review".
"""
import json

PART = "data/omics/use-case-refresh-phenotype-20261022/parts/edwards2026assayloop.jsonl"
SHA = "adcaaa5b7f9bd0e3bc1f91d94d26c8d4924c5c0b3064b6625c01ba92c6eaef28"
URL = "https://arxiv.org/pdf/2609.11877v1"
DATE = "2026-10-22"
PRE = "ucpheno-20261022-"
REVIEWER_NOTE = ("Claude (Opus 5.5) review agent in the evidence-pass workflow, independent of the "
                 "extraction agent; no human review claimed")

RESULT_METHOD_NOTE = (
    "Re-hashed the pinned PDF (SHA-256 matches the source record). Ran scripts/omics/batch.py check-values "
    "on the pdftotext -layout text layer: 470 in_row, 60 row_not_found (the last six Supplementary Table 4 "
    "rows sit beyond the script's 80-line caption window). A separate reviewer script "
    "(review/edwards2026assayloop-check.py) re-parsed Table 1 (26 rows) and Supplementary Table 4 (57 rows), "
    "resolved each locator to one cell by group, row label, the row above it for repeated labels, and column "
    "position, and matched 530 of 530 printed and numeric values, with no cell used twice. It also confirmed "
    "that all 26 Table 1 rows equal their Supplementary Table 4 printings in the 8 shared columns and that the "
    "four repeated Supplementary Table 4 runs are identical. A seeded sample of 36 results, plus every row of "
    "the Base LLM, Adaptive Experimental Design and Ablations blocks, was compared by eye with the rendered PDF "
    "pages 8 and 31, including column order. Metric definitions, arrows and aggregation were checked against "
    "the captions, Methods 4.3 and Appendix H."
)
RESULT_METHODS = ["source-hash-verification", "pdf-text-parse", "independent-cell-check",
                  "rendered-source-visual-check", "scope-review"]
OVERFLOW_ROWS = {"assayformer-ef-terminal-grpo", "assayformer-svd-grpo", "assayformer-mf-grpo",
                 "assayformer-mf-sphere-grpo", "assayformer-genept-pca-grpo", "assayformer-k562-pca-grpo"}


rows = [json.loads(l) for l in open(PART, encoding="utf-8")]
changed = []
for r in rows:
    a = r["attributes"]
    rid = r["id"]
    r["status"] = "source_checked"
    if r["kind"] == "result":
        prior = a.get("review", {}).get("note", "")
        notes = []
        ev = [l["target_id"] for l in r["links"] if l["relation"] == "evaluation"][0]
        evs = ev.replace(PRE + "eval-edwards2026-", "")
        if evs in OVERFLOW_ROWS:
            notes.append("check-values returned row_not_found (row beyond its caption window); the reviewer parse "
                         "and the rendered page 31 confirm the value and column.")
        if rid.endswith(("-random-epb", "-random-eps", "-random-epd")) and evs == "random":
            notes.append("Figure 5 shows Random EP-B 21.7, EP-S 56.4 and EP-D 81.6, computed for the expected "
                         "composition of a uniform draw (Figure 5 caption); the table value is the single draw "
                         "the Table 1 caption describes. The table value is stored.")
        if rid == PRE + "result-edwards2026-assayloop-gemini-3-1-pro-eps":
            notes.append("Figure 5 prints EP-S 46.7 for AssayLoop (EP-B 18.4 and EP-D 70.4 match this run); the "
                         "tables print 46.6. The table value is stored; the 0.1 gap is unexplained.")
        a["review"] = {
            "method": RESULT_METHODS,
            "reviewer": ["claude"],
            "reviewer_note": REVIEWER_NOTE,
            "date": DATE,
            "artifact_sha256": SHA,
            "retrieval_url": URL,
            "method_note": RESULT_METHOD_NOTE,
            "note": " ".join([prior.strip(), "Independent review: printed value, numeric value, locator, metric, "
                              "qualifier, unit, direction and the linked configuration, protocol and test split "
                              "match the source."] + notes).strip(),
        }
        q = a.get("metric_qualifier", "")
        if a["metric"] == "effective-number-of-groups":
            cov = a.setdefault("coverage", {})
            if q.startswith("EP-D"):
                cov["note"] = ("One value pooled over the 20 test screens (Appendix H), not a per-screen mean as the "
                               "Table 1 caption says of all metrics. Appendix H also excludes sample sets with fewer "
                               "annotated genes than the rarefaction size; how many is not reported.")
            else:
                cov["note"] = ("Appendix H excludes batches or screens with fewer annotated genes than the "
                               "rarefaction size; how many were excluded is not reported.")
        changed.append(rid)
    elif r["kind"] == "claim":
        a["review"] = {
            "method": ["source-hash-verification", "ai-assisted-source-review"],
            "reviewer": ["claude"],
            "reviewer_note": REVIEWER_NOTE,
            "date": DATE,
            "artifact_sha256": SHA,
            "retrieval_url": URL,
            "note": "Independent review: value checked against the text at the stated locator in the text layer.",
        }
        changed.append(rid)
    elif rid == PRE + "config-edwards2026-random":
        a["parameters"] = ("One draw of the random policy, not its expected value; whether it samples from the "
                           "candidate pool G or the screen library is not stated")
        r["description"] = "Configuration of Random policy: " + a["parameters"] + "."
        changed.append(rid)
    elif rid in (PRE + "eval-edwards2026-rf-greedy", PRE + "eval-edwards2026-rf-ucb"):
        a["origin"] = "author_reported"
        a["limitations"] = ["Uncited, undescribed random-forest baseline constructed and run by the AssayLoop "
                            "authors (Supplementary Table 4 row label only); recorded as the authors' own "
                            "baseline, like Random, Prior hit and Screen-kNN."]
        changed.append(rid)
    elif rid == PRE + "data-edwards2026-assaybench-loop-test":
        r["links"] = [l for l in r["links"] if l["relation"] != "same_data_as"]
        a["limitations"] = [x for x in a["limitations"] if not x.startswith("The same_data_as link")] + [
            "Not linked same_data_as to tgtval-20261009-data-assaybench-test: the 20 screens are a selected "
            "subset of AssayBench's post-2021 test pool (Methods 4.2), not the same data, and their identities "
            "(Supplementary Table 2) were not matched to AssayBench entries."]
        changed.append(rid)

with open(PART, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(len(rows), "records written;", len(changed), "with field changes beyond status")
