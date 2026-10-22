"""Reviewer's edits to parts/song2025virtualcrispr.jsonl (independent review, 2026-10-22).

Run once on the extractor's frozen part (SHA-256 892dc268da3d3db8c662550c3a8a47f19c53f03bab153552cc3a8fe15eafd96b); the edits are idempotent.
Rulings and reasons are in notes/song2025virtualcrispr.md under "Review".

  python3 review/song2025virtualcrispr_apply.py parts/song2025virtualcrispr.jsonl
"""
import json
import re
import sys

PART = sys.argv[1]
SHA = "6c53ffec88444768fbb5c1a65031c096f07b3d9ac48de8163bc8f47d0d51205c"
URL = "https://aclanthology.org/2025.bionlp-1.30.pdf"
DATE = "2026-10-22"
SID = "pheno-20261022-source-song2025"
REVIEWER_NOTE = "Claude (Opus 5.5) review agent, independent of the extractor; no human review claimed"

recs = [json.loads(l) for l in open(PART) if l.strip()]
by = {r["id"]: r for r in recs}
assert len(recs) == 210


def fix_locator(text):
    """Double-quoted row and column labels (docs/collection.md), and Table 8 rows named by
    their Model, Few-shot and CoT cells so the row is unique in the text layer."""
    text = re.sub(r"Appendix Table 8, row 'GPT-4o' / '([^']*)' / CoT '([NY])'", r'Table 8, row "GPT-4o \1 \2"', text)
    text = re.sub(r"Appendix Table 8, row 'GPT-4o', Few-shot '([^']*)', CoT '([NY])'", r'Table 8, row "GPT-4o \1 \2"', text)
    text = re.sub(r"Appendix Table 8, row 'Random'", 'Table 8, row "Random N/A N/A"', text)
    return re.sub(r"(row|column) '([^']*)'", r'\1 "\2"', text)


def add_limitation(rec, text):
    lims = rec["attributes"].setdefault("limitations", [])
    if text not in lims:
        lims.append(text)


for r in recs:
    a = r["attributes"]
    if "source_locator" in a:
        a["source_locator"] = fix_locator(a["source_locator"])
    for occ in a.get("source_occurrences") or []:
        occ["locator"] = fix_locator(occ["locator"])

# 1. Training-set release is not printed in Section 3; v1.1.16 is stated for the benchmark (Section 2.1).
train = by["pheno-20261022-data-song2025-orcs-training"]["attributes"]
train["version"] = "BioGRID-ORCS (release not stated for the training set; the benchmark uses v1.1.16, Section 2.1)"
train["missing_metadata"]["version"] = {
    "reason": "unreported",
    "note": "Section 3 says 'From the BioGRID-ORCS database'; only the benchmark source is given as v1.1.16 (Section 2.1)"}
claim = by["pheno-20261022-claim-song2025-training-data"]["attributes"]
claim["value"] = ("Trained on 1,678 BioGRID-ORCS screens in human or mouse cells (from an initial pool of 1,924; "
                  "about 22.6 million gene-level results; 7.74% hits under the high-confidence definition), "
                  "with 5 screens held out for validation. The ORCS release used for training is not stated.")
simple_claim = by["pheno-20261022-claim-song2025-simple-from-orcs"]["attributes"]
simple_claim["value"] = ("The Simple Benchmark's four screens come from BioGRID-ORCS v1.1.16, the database the "
                         "embedding classifier is also trained on (the training release is not stated); the authors "
                         "evaluate the classifier only on the Difficult Benchmark 'to mitigate potential bias from "
                         "dataset similarity'. Only prompted LLMs are scored on the Simple Benchmark.")
for cid in ("pheno-20261022-config-song2025-embedding-classifier-raw",
            "pheno-20261022-config-song2025-embedding-classifier-summary"):
    by[cid]["attributes"]["training_setting"] = (
        "Trained on 1,678 BioGRID-ORCS screens in human or mouse cells (release not stated), "
        "5 screens held out for validation")

# 2. 'Pooled' is not stated in the source.
by["pheno-20261022-data-song2025-simple"]["attributes"]["assay"] = "CRISPR activation and knockout screens harmonised by BioGRID-ORCS"
by["pheno-20261022-data-song2025-difficult"]["attributes"]["assay"] = "CRISPR knockout screens"
by["pheno-20261022-data-song2025-simple"]["attributes"]["missing_metadata"]["positives"]["note"] = (
    "Only the 41.3% hit fraction and per-screen hit counts are printed, not a benchmark total. "
    "The Table 3 hit counts (140, 139, 76, 130) sum to 485 of 1,175, which matches 41.3%.")

# 3. Random baseline: the pooled rate is the extractor's reading; the printed values fit per-screen rates.
rnd_cfg = by["pheno-20261022-config-song2025-random-simple"]["attributes"]
rnd_cfg["parameters"] = (
    "Hit probability 'weighted by the overall proportion of actual hits in the specific benchmark dataset being "
    "evaluated' (Appendix A.2). The paper does not say whether one pooled rate (41.3%) or each screen's own rate is "
    "used; see the source's evidence concern.")
rnd_eval = by["pheno-20261022-eval-song2025-random-simple"]
rnd_eval["attributes"]["comparison"]["metric_implementation"] = (
    "Random hit/no-hit predictions scored against the labels with the same metrics as the prompted models")
add_limitation(rnd_eval, "A classifier comparator, not random selection at a budget: it assigns hit or no-hit to every query and nothing is ranked or shortlisted.")
add_limitation(rnd_eval, "Printed only for the Simple Benchmark; Table 2 (Difficult) has no random row.")
add_limitation(rnd_eval, "The printed values fit a hit rate set per screen better than one pooled 41.3% rate, so the baseline may use each screen's hit proportion; see the source's evidence concern.")

# 4. Embedding classifier evaluations: inputs and limitations.
for eid in ("pheno-20261022-eval-song2025-embedding-classifier-raw-difficult",
            "pheno-20261022-eval-song2025-embedding-classifier-summary-difficult"):
    ev = by[eid]
    ev["attributes"]["comparison"]["inputs"] = (
        "Text of the perturbation method, gene symbol, cell line and phenotype, each embedded with "
        "text-embedding-3-large (raw text, or a GPT-4o summary for Summ. Emb.) and concatenated")
    add_limitation(ev, "F1, FPR, PPV, NPV, sensitivity and specificity use a Youden's J threshold; the paper does not say whether it was chosen on the validation screens or on the test queries. If on the test queries these values are optimistic. AUROC and AUPRC do not depend on the threshold.")
    add_limitation(ev, "Trained on BioGRID-ORCS author hit calls; scoring it on other ORCS-derived benchmarks (for example AssayBench) would need a screen-level overlap check against its training screens.")
diff = by["pheno-20261022-protocol-song2025-difficult-hit-classification"]["attributes"]
diff["limitations"] = [
    l if not l.startswith("The Youden's J threshold") else
    "The Youden's J threshold is chosen on predicted probabilities; the paper does not say whether it was set on the validation set or on the test set. Threshold-dependent metrics (F1, FPR, PPV, NPV, sensitivity, specificity) may be optimistic for the embedding classifier; AUROC and AUPRC are not affected."
    for l in diff["limitations"]]

# 5. Evidence concern on the source: random baseline description versus printed values.
src = by[SID]["attributes"]
concern = {
    "source_id": SID,
    "message": (
        "Appendix A.2 describes the random baseline as predicting hit with probability equal to 'the overall "
        "proportion of actual hits in the specific benchmark dataset'. With one pooled rate (485 of 1,175 = 41.3%, "
        "Table 3) the expected PPV, sensitivity, F1 and FPR are all about 0.41 and specificity and NPV about 0.59. "
        "Table 8 prints PPV 0.47, sensitivity 0.46, F1 0.47, FPR 0.36, specificity 0.64 and NPV 0.63. With each "
        "screen's own hit rate (Table 3) the expected values are 0.47, 0.47, 0.47, 0.37, 0.63 and 0.63, which match. "
        "One draw at the pooled rate would need sensitivity about 2 standard errors above and FPR about 3 below "
        "expectation at once. The baseline therefore probably uses per-screen hit rates, which is information a "
        "screen designer would not have before the screen. The expected values were computed by the reviewer from "
        "Table 3 counts and are not stored as results. Treat the random row as a per-screen-prevalence classifier, "
        "not a matched random-selection comparator."),
    "source_locator": "Appendix A.2; Table 3; Table 1, row \"Random Baseline\"; Table 8, row \"Random N/A N/A\"",
    "artifact_sha256": SHA,
    "review_date": DATE,
}
concerns = src.setdefault("evidence_concerns", [])
if not any(c["message"] == concern["message"] for c in concerns):
    concerns.append(concern)

# 6. Review blocks and status.
RESULT_METHOD_NOTE = (
    "Re-downloaded the PDF from the retrieval URL and matched its SHA-256; the regenerated pdftotext -layout text "
    "layer is byte-identical to the extractor's. Read every cell with a separate parser written for this review "
    "(review/song2025virtualcrispr_verify.py), with table headers, row labels and column positions asserted, so the "
    "column is checked as well as the row; the extractor script was not imported or run. Checked printed and numeric "
    "value, locator, metric, unit, direction, uncertainty, and the linked evaluation, configuration, Table 7 model "
    "version and protocol. Tables 1, 2 and 8 were also rendered from the PDF (pdftoppm) and compared by eye with the parsed rows, including the column under which each '±' value sits in Table 2. batch.py check-values returns row_not_found for these locators because Table 1 sits in "
    "the right-hand text column and Tables 2 and 8 print their captions below the rows.")
for r in recs:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] == "result":
        note = []
        loc = a["source_locator"]
        if loc.startswith("Table 1") and a.get("uncertainty"):
            note.append("Table 1 '±' is the standard deviation across prompting strategies (caption 'mean and std. dev.'); the ten Table 8 GPT-4o rows have mean F1 0.472 and FPR 0.223 and standard deviation about 0.06, which matches the Table 1 GPT-4o row. n per model is not printed.")
        if loc.startswith("Table 2") and a.get("uncertainty"):
            note.append("Table 2 '±' line below the GPT-4o row; the statistic is not named, kept as unresolved_spread.")
        if a.get("printed_value") == "N/A":
            note.append("Cell prints N/A; the caption says AUROC and AUPRC are undefined for binary outputs.")
        if "random" in r["id"]:
            note.append("Random baseline: see the source's evidence concern on per-screen versus pooled hit rate.")
            if a.get("source_occurrences"):
                note.append("Same value printed in Table 1 and Table 8; stored once.")
        if "embedding-classifier" in r["id"] and a["metric"] not in ("auroc", "auprc"):
            note.append("Threshold-dependent: Youden's J threshold, selection data not stated.")
        a["review"] = {
            "method": ["source-hash-verification", "pdf-text-parse", "independent-cell-check", "rendered-source-visual-check"],
            "method_note": RESULT_METHOD_NOTE,
            "reviewer": ["claude"],
            "reviewer_note": REVIEWER_NOTE,
            "date": DATE,
            "artifact_sha256": SHA,
            "retrieval_url": URL,
            "note": " ".join(note) or "Matches the source cell.",
        }
    elif r["kind"] == "claim":
        a["review"] = {
            "method": ["source-hash-verification", "ai-assisted-source-review"],
            "method_note": "Read the cited sections of the pinned PDF text layer and checked the claim's wording against them.",
            "reviewer": ["claude"],
            "reviewer_note": REVIEWER_NOTE,
            "date": DATE,
            "artifact_sha256": SHA,
            "retrieval_url": URL,
            "note": {
                "pheno-20261022-claim-song2025-training-data": "Reviewer removed 'v1.1.16' and added the initial pool of 1,924: Section 3 does not state the training release.",
                "pheno-20261022-claim-song2025-simple-from-orcs": "Reviewer reworded: the training release is not stated, and the authors' reason is quoted from Section 3.",
                "pheno-20261022-claim-song2025-leakage-control": "Matches Section 2.1 item (2) and Section 3. The paper asserts post-cutoff selection but prints no model cutoff dates.",
                "pheno-20261022-claim-song2025-stated-purpose": "Matches the Abstract ('thereby prioritizing experiments'), Section 5 and Limitations and Future Work ('Conduct in vitro validation').",
            }[r["id"]],
        }

# Sanity checks.
for r in recs:
    if r["kind"] == "result":
        a = r["attributes"]
        assert a["metric_direction"] == ("lower" if a["metric"] == "false-positive-rate" else "higher"), r["id"]
        assert '"' in a["source_locator"] and "'" not in a["source_locator"], r["id"]

with open(PART, "w") as f:
    f.write("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in recs))
print("wrote", len(recs), "records")
