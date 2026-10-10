"""Independent review edits for the #88(b) and #89 QA fixes, 2026-10-10. Run from the worktree root after apply_fixes.py:
python3 -I data/omics/qa-suffix-reasons-20261010/review_edits.py

Replaces four field values in place (exact JSON string replacement, as apply_fixes.py does), updates the matching
metadata-correction claims' `value`, and records the independent review on all 33 correction claims.
"""
import json

NOTES = "data/omics/qa-suffix-reasons-20261010"
DATE = "2026-10-10"
SEI = "regulatory-variant-20261009-model-sei"
EDITS = {
    SEI: ("description",
          "Supervised sequence model pretrained on 21,907 chromatin profiling datasets (Tang et al. 2025 Results), built from residual dilated convolutions.",
          "Supervised sequence model built from residual dilated convolutions and pretrained on 21,907 chromatin profiling datasets."),
    "use-case-mapping-cnv-20261009-delavega2025-hg002": ("attributes.reason",
          "Not shown: the article's Results text and its Supplemental Table 3 disagree on whether CNVnator detected 1-5 kb events and on which caller had the lowest precision. "
          "The values here are recorded as printed in the tables, but they are not shown until that conflict is resolved.",
          "Not shown: the article's Results text and its Supplemental Table 3 disagree on whether CNVnator detected 1 to 5 kb events and on which caller had the lowest precision. "
          "The values here are recorded as printed in the tables, but they are not shown until that conflict is resolved."),
    "use-case-mapping-cnv-20261009-delavega2025-coriell-panel": ("attributes.reason",
          "Not shown: the article's Results text and its Supplemental Table 3 disagree on whether CNVnator detected 1-5 kb events and on which caller had the lowest precision. "
          "The conflict is in the HG002 table, not in this panel table, but it applies to the whole article, so these precision values are not shown until it is resolved.",
          "Not shown: the article's Results text and its Supplemental Table 3 disagree on whether CNVnator detected 1 to 5 kb events and on which caller had the lowest precision. "
          "The conflict is in the HG002 table, not in this panel table, but it is recorded against the whole article, so these precision values are not shown until it is resolved."),
    "use-case-mapping-cnv-20261009-nardone2025-hg002-deletions": ("attributes.reason",
          "Not shown: the paper states the read depth and aligner behind Table S1 inconsistently (25x with bwa-mem2 in Methods, the DRAGEN pipeline in Results, 30x reads in Data Availability), "
          "and its text and Table S1 disagree for inGAP at 5,000-9,999 bp. The table values are recorded, but they are not compared with other HG002 tables until this is resolved.",
          "Not shown: the paper states the read depth and aligner behind Table S1 inconsistently (reads subsampled to 25x and aligned with bwa-mem2 for preliminary evaluations in Methods, "
          "the DRAGEN pipeline in Results, 30x reads in Data Availability), and its text and Table S1 disagree for inGAP at 5,000 to 9,999 bp. "
          "The table values are recorded as printed, but they are not shown until this is resolved."),
}
enc = lambda s: json.dumps(s, ensure_ascii=False)

for path in ("data/entities/models.jsonl", "data/evidence/claims.jsonl"):
    lines = open(path).read().split("\n")
    for i, line in enumerate(lines):
        if not line:
            continue
        rid = json.loads(line)["id"]
        if rid in EDITS:
            field, old, new = EDITS[rid]
            assert line.count(enc(old)) == 1, rid
            before = json.loads(line)
            lines[i] = line.replace(enc(old), enc(new))
            after = json.loads(lines[i])
            if field == "description":
                assert after["description"] == new
                after["description"] = old
            else:
                assert after["attributes"]["reason"] == new
                after["attributes"]["reason"] = old
            assert after == before, rid
    open(path, "w").write("\n".join(lines))

NOTE = "Separate Claude review agent, independent of the QA agent that made the change; no human review claimed"
recs = [json.loads(l) for l in open(f"{NOTES}/batch.jsonl")]
for c in recs:
    subject = c["links"][0]["target_id"]
    a = c["attributes"]
    if subject in EDITS:
        assert a["value"] == EDITS[subject][1]
        a["value"] = EDITS[subject][2]
    edited = subject in EDITS
    if subject == SEI:
        c["description"] = ("Remove the trailing citation suffix from the description (issue #88), and reorder the sentence so that the inner "
                            "citation to Tang et al. 2025 also leaves the text. Both cited sources remain in source_ids.")
    if a["field"] == "description":
        method_note = ("Compared previous_value with origin/main and value with the working tree; confirmed that only the trailing citation "
                       "was removed and that every author and year it cited has a source in source_ids.")
    else:
        method_note = ("Compared previous_value with origin/main and value with the working tree; checked every fact in the new reason against "
                       "the claim's endpoint and limitations and the evidence_concerns of its sources.")
    c["status"] = "source_checked"
    a["review"] = {
        "method": ["automated-source-review"], "method_note": method_note, "reviewer": ["claude"], "reviewer_note": NOTE,
        "date": DATE,
        "note": (c["description"] + (" Wording revised at independent review; see data/omics/qa-suffix-reasons-20261010/review.md."
                                     if edited else " Independent review 2026-10-10: correct as made.")),
    }
with open(f"{NOTES}/batch.jsonl", "w") as f:
    for c in recs:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
print("edited", len(EDITS), "claims reviewed", len(recs))
