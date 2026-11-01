"""Record the independent review of an AlphaGenome-evidence batch (docs/reviews/2026-11-01-alphagenome-atlas-lu-brandes.md).

Usage: python3 -I review.py <batch folder> <atlas|lu>

The reviewer did not extract either batch. Sets every record to source_checked and replaces the extraction
review on results and claims with the review block; the extraction method note is kept.
"""
import json
import os
import sys

OUT, WHICH = sys.argv[1], sys.argv[2]
DATED = "docs/reviews/2026-11-01-alphagenome-atlas-lu-brandes.md"
REVIEWER_NOTE = ("Independent Claude review agent for PR #214, 2026-11-01; did not extract this batch; "
                 "no human review claimed.")
CHECKS = {
    "atlas": {
        "table": (["source-hash-verification", "deterministic-table-parse", "independent-cell-check", "automated-source-review"],
                  "Re-parsed Table S2 from a pdftotext -raw text layer of a 2026-11-01 retrieval and matched all 70 cells, "
                  "with numeric value and metric, to the stored values."),
        "text": (["source-hash-verification", "independent-cell-check", "automated-source-review"],
                 "Checked that the value is printed inside the quoted sentence or legend entry and that the quote occurs in "
                 "the pdftotext text of a 2026-11-01 retrieval; rare-disease recalls read against the paragraph on page 7."),
    },
    "lu": {
        "figure": (["source-hash-verification", "rendered-source-visual-check", "independent-cell-check"],
                   "Compared every bar label, row order, N and %P with an independent 300 dpi render of page 8 "
                   "(column 3 also at 400 dpi) or a 150 dpi render of page 21 of a 2026-11-01 retrieval."),
    },
}
HASH_NOTE = ("The 2026-11-01 retrieval is stamped differently from the pinned bytes (different SHA-256); re-running the "
             "extractor on it, with only the hash assertion relaxed, reproduced batch.jsonl byte for byte.")

recs = [json.loads(l) for l in open(os.path.join(OUT, "batch.jsonl"))]
for r in recs:
    r["status"] = "source_checked"
    a = r["attributes"]
    if r["kind"] not in ("result", "claim") or "review" not in a:
        continue
    old = a["review"]
    loc = a.get("source_locator", "")
    if WHICH == "atlas":
        method, note = CHECKS["atlas"]["table" if loc.startswith("Table S2") else "text"]
    else:
        method, note = CHECKS["lu"]["figure"]
    if r["kind"] == "claim":
        method = ["source-hash-verification", "automated-source-review", "scope-review"]
        note = "Checked the claim's statements against the cited pages of a 2026-11-01 retrieval."
    a["review"] = {"method": method, "method_note": old.get("method_note", ""), "reviewer": ["claude"],
                   "reviewer_note": REVIEWER_NOTE, "date": "2026-11-01",
                   "artifact_sha256": old["artifact_sha256"], "retrieval_url": old["retrieval_url"],
                   "note": f"{note} {HASH_NOTE} Verdict in {DATED}."}
# Review correction: task links required by the rules v4 ratchet (scripts/omics/check-task-links.ts, #208).
TRAITGYM = "lit-genomics-20261011-traitgym-benchmark-traitgym"
NO_TASK = ("No task or benchmark in the store covers {what}; left unlinked on purpose so the discrepancy rules "
           "treat its scope as unknown rather than guess (#208). Reviewed 2026-11-01.")
EXEMPT = {
    "ag-atlas-20261019-protocol-clinvar-snv-by-consequence-auprc": "ClinVar pathogenicity of noncoding and all-consequence SNVs",
    "ag-atlas-20261019-protocol-table-s2-clinvar": "ClinVar pathogenicity of SNVs and indels across consequences",
    "ag-atlas-20261019-protocol-table-s2-ncvar": "ncVar noncoding pathogenic variants",
    "ag-atlas-20261019-protocol-table-s2-sge": "saturation genome editing functional classes",
    "ag-atlas-20261019-protocol-sge-pooled-snv-auprc": "saturation genome editing functional classes",
    "ag-atlas-20261019-protocol-sge-pooled-all-variants-auprc": "saturation genome editing functional classes",
    "ag-atlas-20261019-protocol-rare-complex-trait-snv-auprc": "rare variants associated with complex traits",
    "ag-atlas-20261019-protocol-gregor-recall-top50": "ranking causal variants within rare-disease genomes",
    "ag-atlas-20261019-protocol-dnm1-active-variant-ap": "a single-gene splice-variant case study",
    "lu-hetero-20261019-protocol-clinvar-variant-type-auroc": "ClinVar pathogenicity across all variant types",
}
for r in recs:
    if r["kind"] != "protocol":
        continue
    if "traitgym" in r["id"] and not any(l["relation"] == "part_of" for l in r["links"]):
        r["links"].append({"relation": "part_of", "target_id": TRAITGYM})
    elif r["id"] in EXEMPT:
        r["attributes"]["task_link_exemption"] = NO_TASK.format(what=EXEMPT[r["id"]])
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(f"{len(recs)} records set to source_checked")
