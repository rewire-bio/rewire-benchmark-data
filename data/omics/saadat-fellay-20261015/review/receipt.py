"""Write review.json for saadat-fellay-20261015: the receipt fields and the SHA-256 of every other file in the batch folder.

Usage: python3 -I review/receipt.py  (run after review/review.py)
"""
import hashlib
import json
from pathlib import Path

BATCH_DIR = Path(__file__).resolve().parent.parent
RECEIPT = {
    "schema_version": "1.0",
    "method": "automated_source_review",
    "review_methods": ["source-hash-verification", "pdf-text-parse", "independent-cell-check",
                       "rendered-source-visual-check", "ai-assisted-source-review", "scope-review"],
    "reviewer": ("Claude review agent; no human review claimed. Independent Claude (Opus 5.5) review agent, separate from "
                 "the extraction agent that built this batch."),
    "reviewed_at": "2026-10-15T22:00:00Z",
    "scope": ("Independent review of saadat-fellay-20261015 (extraction commit fc3881f): 38 records (10 results, 10 evaluations, "
              "10 configurations, 3 protocols, 3 claims, 1 dataset, 1 source). Matched the PDF SHA-256 on the archived copy of the "
              "hand download. Reran extract/extract_saadat_fellay.py and matched batch.jsonl, claims.csv and coverage.json byte for "
              "byte. review/review.py, written independently, re-parsed the PDF text and asserted all 6 prose values and the setup "
              "sentences; the 4 Figure 1 legend values were read by the reviewer from the embedded image and all matched. "
              "Figures 3, 4 and 5 were viewed to check stage assignment and claim scope. All records set to source_checked."),
    "comparison": {"script": "review/review.py", "results_checked": 10, "mismatches": 0,
                   "by_locator": {"pdf-text": 6, "figure-1-raster-legend": 4}},
    "manual_sample": {"results": "all 10", "mismatches": 0},
    "limitations": [
        "Automated review by a Claude agent; not human scientific review and not reproduction of any result.",
        "No fresh download: OpenReview answers scripted requests with a bot challenge; the archived copy matched the pinned hash.",
        "Figure 1 values are printed text inside a raster image; checked by eye, not by a text parse.",
        "Plotted values in Figures 2-5 were viewed only to check scope and consistency; none is recorded as a result.",
    ],
    "corrections": [
        "NT 2.5B BF16 and 4-bit memory results: source_discrepancy extended with the Figure 5 bar heights (about 6.6 and 5.45 GB).",
        "Quantization protocol: limitation citing a nonexistent source evidence concern rewritten.",
        "Training-memory protocol: limitations on sequence-length unit and on LoRA versus full update.",
        "Pseudo-perplexity protocol: limitations on NT pseudo-perplexity above the 6-mer vocabulary size and the NT 2.5B scatter.",
        "Fine-tuning claim: limitations on what Figure 4 plots.",
    ],
    "errors": [],
    "review_document": "docs/reviews/saadat-fellay-2026-10-15-review.md",
    "batch_sha256_before_review": "e3702fd5d1fab507a375797133158722a15131ac982144e5153342a319e812d0",
    "source_artifacts": {
        "saadat-fellay-20261015-source-paper": "4bc2452110f280a7ba8baa4c7c28beac89769511019666bc77fc33af9b3bcd60",
    },
}

files = {}
for p in sorted(BATCH_DIR.rglob("*")):
    if p.is_file() and p.name != "review.json" and "__pycache__" not in p.parts:
        files[str(p.relative_to(BATCH_DIR))] = hashlib.sha256(p.read_bytes()).hexdigest()
RECEIPT["files"] = files
(BATCH_DIR / "review.json").write_text(json.dumps(RECEIPT, indent=2, ensure_ascii=False) + "\n")
print(len(files), files["batch.jsonl"])
