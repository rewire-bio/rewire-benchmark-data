#!/usr/bin/env python3
"""Apply the independent review to data/omics/ladon-20261115/batch.jsonl.

Three changes, all of them rulings of the review pass:

  1. every record's `attributes.review` is replaced with the reviewer's object,
  2. every `needs_review` record becomes `source_checked` (the ClinBench
     benchmark stays `discovered`: nothing was extracted from it),
  3. one scoped `evidence_concerns` entry is added to the Figure 6 web source,
     withholding the T-effector / IFN-gamma response AUROC from automatic
     comparison because one of the six trials it averages is in-sample,
  4. the two configurations that combine Ladon with BMRetriever-7B gain a
     `uses_model` link to Ladon, so that both members of the combination are
     named as members and not only the clinical one.

The file is rewritten in its own format: sorted by ID, one compact JSON object
per line with sorted keys and non-ASCII characters kept as themselves.

Usage: python3 apply_review.py <batch.jsonl>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PDF_SHA256 = "64edf7c3c956c50a65aa01a0dcaa13f0cfef28ab4373ecfd50c431e67143893c"
PDF_URL = (
    "https://zenodo.org/api/records/24157116/files/"
    "Ladon-An-RNA-Foundation-Model-for-Predicting-Patient-Outcomes.pdf/content"
)
FIG06_SHA256 = "afa0d46855e1c3b15efa9a6cca8c621d4314ad445dd7777216e62c7ac646629f"
DATE = "2026-11-15"
REVIEWED_AT = "2026-11-15T23:30:00Z"

REVIEWER_NOTE = (
    "Claude review agent, independent of the extractor; no human review claimed. "
    "Transcription was checked against the pinned sources, which is not reproduction: "
    "nothing was rerun and no value was recomputed."
)

RESULT_METHOD_NOTE = (
    "Independent review pass. The Zenodo PDF was re-downloaded and its SHA-256 and MD5 "
    "checked against the source record and the Zenodo file checksum; the three HTML sources "
    "were refetched and all three hashes matched. The report prints no tables, so "
    "npm run batch -- check-values cannot place any locator and reports locator_not_parsed "
    "for all 101 results; value-check.tsv is kept as that record. All 101 were therefore "
    "re-read by review/check_figure_labels.py, written for this pass and using neither of "
    "the extractor's scripts: it reads the word-level geometry of a pdftotext -bbox-layout "
    "run and places every cell by its x and y coordinates, so each value is tied to the row "
    "whose label it sits beside and to the column or panel whose printed header it sits "
    "under, rather than to a line of a -layout text layer or a character offset. Figure 2's "
    "three panels and Figure 17's two columns were resolved by clustering the value "
    "positions and ordering the clusters by the printed headers; every printed 95% interval "
    "was matched to the result's uncertainty bounds. 113 checks, no disagreement. Three "
    "arithmetic constraints were re-derived: Figure 17's five per-lineage Pearson r values "
    "average to the bottom chart's overall r for both Ladon (0.872 against a printed 0.87) "
    "and CIBERSORT (0.594 against 0.600), which independently fixes which of the two "
    "numbers in each lineage label is Ladon's; Figure 2's pan-cancer bar differs from the "
    "mean of its two transfer bars, as the caption requires; and Figure 14's in-figure "
    "top-5% label agrees with the page 27 prose. A manual sample was read by eye from the "
    "-layout text layer: all 24 Figure 2 cells, all 14 Figure 3 OS and PFS values, all 10 "
    "Figure 18 AUCs with their intervals, and the Figure 5, 11, 12a, 13 and 17 readouts, "
    "with column and panel assignment checked in each. Figure 2's 24 cells, Figure 3's 14 "
    "and Figure 18's 10 AUCs and intervals were confirmed a third time against the facet "
    "and row keys of the authors' own figure pages."
)

DESCRIPTIVE_METHOD_NOTE = (
    "Independent review pass. All 216 non-result records were checked by "
    "review/check_claim_quotes.py, written for this pass, which looks for every quoted phrase "
    "and every number a record states in the text of the sources that record cites: the pinned "
    "PDF's pdftotext -layout text layer, and for records citing them the announcement page and "
    "the Figure 6 page, whose embedded DATA object is searched as text rather than stripped as "
    "script. 182 quoted phrases and 1,136 numbers; three were not found by search and each was "
    "then read by hand and accepted, with the reason recorded in review/claim-quote-check.tsv "
    "(a sum the field itself labels as the extractor's, a row label the text layer breaks across "
    "two lines, and a locator joining a panel's two printed header lines with a comma). "
    "Pages 6 to 10, 12, 13, 15 to 17, 19, 20, 24 to 28, 33, 35 and 39 were read in full, and "
    "these were checked against the records in particular: the trial, endpoint and patient "
    "counts of pages 12, 13 and 15 against the dataset and dataset-subset records; the fitting "
    "procedures of pages 12 and 13 against each configuration; the geometric-mean and "
    "size-weighted aggregations of page 13 against the Figure 3 and Figure 5 protocols; the "
    "reimplementation sentence on page 39 against the CIBERSORT and DWLS method records; and the "
    "bootstrap statements on pages 28 and 39 against the stored uncertainty methods and resample "
    "counts. Pages the records cite but that were not read line by line (pages 11, 14, 18, 22, "
    "29, 38 and 40 to 43) are covered by the quote and number check alone."
)

SOURCE_METHOD_NOTE = (
    "Independent review pass. Each pinned artifact was re-retrieved at review time and its "
    "SHA-256 recomputed: the Zenodo PDF matched (and its MD5 matched the Zenodo file "
    "checksum), and the three HTML artifacts matched byte for byte, although all three are "
    "mutable and the hash describes one retrieval. The PDF text layer regenerated with "
    "pdftotext 26.08.0 -layout reproduced the SHA-256 the source record's version_note "
    "states, so the text every value was read from is provably derived from the pinned bytes."
)

# shared/omics/attribute-registry.ts declares no `review` attribute for `task`, so a task
# record carries none; the review of a task's definition is recorded on its protocols.
KINDS_WITHOUT_REVIEW = {"task", "evaluator", "service"}

RESULT_METHODS = ["independent-cell-check", "pdf-text-parse", "source-hash-verification"]
DESCRIPTIVE_METHODS = ["pdf-text-parse", "source-hash-verification", "automated-source-review"]
SOURCE_METHODS = ["source-hash-verification", "automated-source-review"]

# Records whose review carries a finding of its own, beyond the shared note.
NOTES = {
    "ladon-20261115-result-fig18-ladon-deconvolution-dfci-ibc-her2-pos": (
        "Figure 18 prints 0.73 and the page 34 prose prints 0.74 for the same AUC. Confirmed "
        "as one value rounded two ways, not two values: the figure page holds 0.735 and "
        "renders it with toFixed(2), which gives 0.73 because 0.735 is below 0.735 in binary "
        "floating point, while the prose rounds half up. The figure's value is stored, the "
        "locator names the figure, and attributes.source_discrepancy records the conflict. No "
        "evidence concern: the difference is 0.005 against a printed interval of [0.50, 0.93]."
    ),
    "ladon-20261115-result-fig5-ladon-plus-trials": (
        "Which training stage the legend belongs to is the one assignment the PDF's geometry "
        "cannot settle, because the three legend values sit on a single line below the panel. "
        "Checked against the authors' own Figure 5 page, whose third stage, 'TCGA + non-trial "
        "cohorts + other clinical trials', holds 0.6355716 for Ladon; its equal-trial mean, "
        "0.630, is a different number, so the stored value is the size-weighted mean the "
        "caption and the protocol describe."
    ),
    "ladon-20261115-result-fig5-dge-plus-trials": (
        "Stage assignment checked against the authors' Figure 5 page: the third stage holds "
        "0.5954244 for DGE, against an equal-trial mean of 0.583."
    ),
    "ladon-20261115-result-fig5-hallmark-gsea-plus-trials": (
        "Stage assignment checked against the authors' Figure 5 page: the third stage holds "
        "0.5784649 for Hallmark GSEA, against an equal-trial mean of 0.567."
    ),
    "ladon-20261115-result-fig4-ladon-plus-clinical-oak-os": (
        "The caption's 'fitting the risk predictor on other cohorts' matches the page 13 "
        "Methods for the combined trial predictor, so the assignment to that configuration is "
        "the best-supported reading; the caption does not say it is the same fitted predictor "
        "and the result keeps that caveat."
    ),
    "ladon-20261115-result-fig6-t-effector-ifn-gamma-response": (
        "The value is correctly transcribed, but one of the six trials it averages, POPLAR, is "
        "the trial the signature was derived on, which the Figure 6 page states. An "
        "evidence_concerns entry on that source withholds this result from automatic "
        "comparison; the printed value is kept."
    ),
    "ladon-20261115-result-fig17-ladon-pearson": (
        "The top panels' comparator identity was checked twice: the page 34 caption says "
        "'(CIBERSORT by default)', and the five per-lineage first values average to this "
        "0.87 while the second values average to CIBERSORT's 0.60."
    ),
}

CONCERN = {
    "applies_to": ["ladon-20261115-result-fig6-t-effector-ifn-gamma-response"],
    "artifact_sha256": FIG06_SHA256,
    "message": (
        "The T-effector / IFN-gamma response AUROC is an equal mean over six trials, and one "
        "of the six, POPLAR, is the trial the signature was derived on: this page states 'The "
        "T-effector signature was derived on POPLAR, so its POPLAR result is in-sample.' One "
        "sixth of the stored mean is therefore a training-set score. Nothing in the "
        "evaluation's comparison fields records it, and the report's own Figure 6 text does "
        "not state it, so a reader comparing this mean with a T-effector / IFN-gamma AUROC "
        "measured out of sample would be comparing unlike numbers. The printed value is kept "
        "as published and this entry withholds it from automatic comparison. It covers that "
        "one result: the other nine Figure 6 results, the protocol and the method record are "
        "not affected, and the per-trial values are not stored."
    ),
    "review_method": "independent-cell-check",
    "reviewed_at": REVIEWED_AT,
    "source_id": "ladon-20261115-source-web-fig06",
    "source_locator": (
        "Embedded DATA object, master.panel_f.rows, row 'T-effector / IFN-γ', field 'note'"
    ),
}


# A configuration carrying `combination_rule` must name every member of the combination with
# `uses_model` (rbs:CombinedConfiguration in data/ontology/shapes.ttl, minCount 2). Both of these
# combine Ladon's score with BMRetriever-7B's but named only BMRetriever-7B, which also left
# scripts/kg/contradictions.py free to compare the combination against Ladon alone.
COMBINATION_MEMBER = {
    "ladon-20261115-config-ladon-clinical-transfer-cox": "ladon-20261115-model-ladon",
    "ladon-20261115-config-ladon-clinical-trial-survival": "ladon-20261115-model-ladon",
}


def artifact_of(record: dict, sources: dict[str, tuple[str, str]]) -> tuple[str, str]:
    """The artifact this record's review was checked against, as (sha256, url).

    A source record is checked against its own bytes, not the PDF's. Everything else is checked
    against the PDF when it cites it, and otherwise against the first source it does cite: the
    only such record here is the access claim, whose sole source is the announcement page.
    """
    if record["kind"] == "source":
        return sources[record["id"]]
    if "ladon-20261115-source-zenodo-pdf" in record["source_ids"]:
        return PDF_SHA256, PDF_URL
    for source_id in record["source_ids"]:
        if source_id in sources:
            return sources[source_id]
    raise AssertionError(f"{record['id']}: no source with an artifact hash")


def review_for(record: dict, sources: dict[str, tuple[str, str]]) -> dict:
    kind = record["kind"]
    if kind == "result":
        methods, method_note = RESULT_METHODS, RESULT_METHOD_NOTE
    elif kind == "source":
        methods, method_note = SOURCE_METHODS, SOURCE_METHOD_NOTE
    else:
        methods, method_note = DESCRIPTIVE_METHODS, DESCRIPTIVE_METHOD_NOTE
    sha256, url = artifact_of(record, sources)
    review = {
        "artifact_sha256": sha256,
        "date": DATE,
        "method": methods,
        "method_note": method_note,
        "retrieval_url": url,
        "reviewed_at": REVIEWED_AT,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
    }
    note = NOTES.get(record["id"])
    if note:
        review["note"] = note
    elif kind == "result":
        review["note"] = "Printed label re-read from the pinned PDF by coordinates; it matched."
    elif kind == "source":
        review["note"] = "Artifact re-retrieved at review time; hash matched the source record."
    else:
        review["note"] = "Re-read at the locator this record names; it matched."
    return review


def main(path: Path) -> int:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    sources = {
        r["id"]: (
            r["attributes"]["artifact_sha256"],
            r["attributes"].get("retrieval_url") or r["attributes"]["url"],
        )
        for r in records
        if r["kind"] == "source" and r["attributes"].get("artifact_sha256")
    }
    promoted = 0
    members_added = 0
    for record in records:
        member = COMBINATION_MEMBER.get(record["id"])
        if member and not any(
            l["relation"] == "uses_model" and l["target_id"] == member for l in record["links"]
        ):
            record["links"].append({"relation": "uses_model", "target_id": member})
            record["links"].sort(key=lambda l: (l["relation"], l["target_id"]))
            members_added += 1
        if record["kind"] not in KINDS_WITHOUT_REVIEW:
            record["attributes"]["review"] = review_for(record, sources)
        if record["status"] == "needs_review":
            record["status"] = "source_checked"
            promoted += 1
        if record["id"] == CONCERN["source_id"]:
            existing = record["attributes"].get("evidence_concerns", [])
            messages = [e.get("message") for e in existing if isinstance(e, dict)]
            if CONCERN["message"] not in messages:
                record["attributes"]["evidence_concerns"] = existing + [CONCERN]
    records.sort(key=lambda r: r["id"])
    path.write_text(
        "".join(
            json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
            for r in records
        )
    )
    print(f"{len(records)} records rewritten, {promoted} promoted to source_checked")
    print(f"evidence concerns on {CONCERN['source_id']}: 1, scoped to {CONCERN['applies_to']}")
    print(f"combination members added: {members_added}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
