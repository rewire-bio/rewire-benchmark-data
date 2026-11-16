"""Apply the independent review's rulings to batch.jsonl.

Run after review/recheck_tables.py has passed on the frozen extraction (batch.jsonl SHA-256
1b50664da2bfe60287cbe48e3b996d562f6c5594539bb07a06f46505560a12ca):

    python3 -I data/omics/perturbpfn-20261115/review/apply_review.py

Each change is argued in docs/reviews/2026-11-15-perturbpfn.md with the deciding source text.
"""
import json
from pathlib import Path

BATCH = Path(__file__).resolve().parent.parent
PATH = BATCH / "batch.jsonl"
FROZEN = "1b50664da2bfe60287cbe48e3b996d562f6c5594539bb07a06f46505560a12ca"
REVIEWED_AT = "2026-11-15T00:00:00Z"
ARTIFACT = "42191efa04b45ca04b2be38b51ea374cd9bf891efe2399d331fec9eaeab200b1"
URL = "https://arxiv.org/pdf/2607.23447v1"

REVIEW = {
    "method": ["independent-cell-check", "deterministic-table-parse", "pdf-text-parse",
               "source-hash-verification"],
    "method_note": (
        "Independent review pass. Both pinned artifacts were re-downloaded and their SHA-256 "
        "checked against the source records, the mutable abstract page included, and both matched. "
        "A pdftotext -layout run (poppler 26.08.0) on the refetched PDF is byte for byte the "
        "contents of the archived gzipped text layer, so the archive is provably derived from the "
        "pinned bytes. npm run batch -- check-values reproduced the extractor's figures exactly "
        "(64 in_cell, 11 in_row, 6 locator_not_parsed, no wrong_column and no "
        "overclaimed_in_row) and wrote the same value-check.tsv. All 81 results were then re-read "
        "by review/recheck_tables.py, written for this pass and using neither "
        "extract/parse_tables.py nor extract/check_tables.py: it takes each table's column spans "
        "from the character offsets of that table's own printed header line, assigns every numeric "
        "token on a body line to the column whose header centre is nearest, and matches cells to "
        "records through each result's source_locator text rather than its ID, checking "
        "printed_value, numeric_value, the printed spread and the system the result's evaluation "
        "names. Two negative controls confirmed it fails on a swapped pair of values and on a cell "
        "shifted into the neighbouring column. A manual check of 16 cells covered column "
        "assignment in all three tables, including Table 2's unlabelled PerturbPFN score line, "
        "Table 1's third label and value pair on each of its three rows, and Table 3's middle "
        "columns. The printed overall score was re-derived as the equal-weight mean of each row's "
        "three normalised columns. The 54 descriptive records were read against Sections 2 to 5, "
        "Appendices A to E and Tables 4 to 8 of the pinned PDF."),
    "reviewer": ["claude"],
    "reviewer_note": (
        "Claude review agent (independent of the extractor); no human review claimed. Transcription "
        "was checked against the pinned source; nothing was reproduced and no value was "
        "recomputed."),
    "reviewed_at": REVIEWED_AT,
    "artifact_sha256": ARTIFACT,
    "retrieval_url": URL,
}

records = [json.loads(line) for line in PATH.read_text().splitlines() if line.strip()]
by_id = {r["id"]: r for r in records}
log = []

# 1. same_data_as on the Sci-Plex subset. The relation is for dataset subsets holding identical
#    data (shared/omics/relations.ts: "Informational data reuse"; the plasma ctDNA review of
#    2026-10-09 states the rule and the phenotype-perturbation review of 2026-10-22 removed a link
#    for a selected subset). This subset is four HDAC inhibitors in three cell lines with GIM
#    preprocessing and 50 marker genes per protocol, held out by dose (Appendix D.1 and D.2); the
#    two stored PerturBench records are covariate-transfer splits to a held-out cell line. The
#    measurements share a parent experiment but the data are not the same, so the links go and the
#    shared provenance is stated in prose instead.
subset = by_id["perturbpfn-20261115-data-sciplex-hdac-3x4"]
removed = [l["target_id"] for l in subset["links"] if l["relation"] == "same_data_as"]
assert sorted(removed) == ["lit-cells-networks-20261011-perturbench-v4-data-srivatsan20",
                           "perturbench-dataset-srivatsan20"], removed
subset["links"] = [l for l in subset["links"] if l["relation"] != "same_data_as"]
assert "reuse_note" not in subset["attributes"]
subset["attributes"]["reuse_note"] = (
    "Drawn from the same experiment as the store's two PerturBench Srivatsan20 subsets, "
    "lit-cells-networks-20261011-perturbench-v4-data-srivatsan20 and "
    "perturbench-dataset-srivatsan20, which are covariate-transfer splits to a held-out cell line "
    "over PerturBench's own compound selection. This is a different slice of those measurements: "
    "four HDAC inhibitors in three cell lines, GIM preprocessing, 50 marker genes per protocol and "
    "a dose holdout. No same_data_as link is recorded, because that relation is for subsets whose "
    "data are identical.")
log.append(f"removed {len(removed)} same_data_as links from the Sci-Plex subset and stated the "
           f"shared Srivatsan 2020 provenance in reuse_note instead")

# 2. Record the review on every record and raise its status. Every record in this batch carries a
#    source_locator and every one was checked against the pinned PDF at that locator, so none is
#    left at needs_review.
assert all(r["status"] == "needs_review" for r in records), "expected a frozen unreviewed batch"
assert all("source_locator" in r["attributes"] for r in records), "a record has no source_locator"
for r in records:
    r["attributes"]["review"] = dict(REVIEW)
    r["status"] = "source_checked"
log.append(f"review object written and status set to source_checked on all {len(records)} records")

records.sort(key=lambda r: r["id"])
with open(PATH, "w") as out:
    for r in records:
        out.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
print(f"frozen input sha256 expected {FROZEN}")
for line in log:
    print(line)
