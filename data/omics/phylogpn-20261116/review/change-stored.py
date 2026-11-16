#!/usr/bin/env python3
"""The three stored-record changes the 2026-11-16 PhyloGPN review makes.

Run under the heavy lock, after `records -- add` for this batch and before
`records -- change`. It rewrites only the lines of the records it changes and leaves every
other byte of each file as it found it, because other agents write the same files tonight.
Idempotent: a second run reports "already applied" and writes nothing.

  phylogpn-2025                                    status, licence, version_note, review,
                                                   evidence_concerns, supersedes link
  evidence-expansion-p2-phylogpn-2025-807f3a26cbfa status -> superseded (duplicate bytes)
  b2-phylogpn-2025                                 status -> superseded (same cell, same value)

Usage: python3 -I change-stored.py <repo-root>
"""

import json
import os
import sys

XML_SHA = "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11908359/fullTextXML"
DATE = "2026-11-16"
DUPLICATE = "evidence-expansion-p2-phylogpn-2025-807f3a26cbfa"

VERSION_NOTE = (
    "Published as a peer-reviewed conference paper: Albors C., Li J.C., Benegas G., Ye C., Song Y.S., "
    "A Phylogenetic Approach to Genomic Language Modeling, Research in Computational Molecular Biology "
    "(RECOMB 2025), Lecture Notes in Computer Science (LNBI) volume 15647, pages 99-117, first online "
    "25 April 2025, doi 10.1007/978-3-031-90252-9_7. The pinned artifact remains the preprint, so "
    "publication_status stays 'preprint'; the version of record is paywalled and was not compared with "
    "the preprint.")

CONCERN = {
    "applies_to": ["phylogpn-20261116-result-t2-chromatin-gena-lm"],
    "artifact_sha256": XML_SHA,
    "message": (
        "Table 2's GENA-LM Chromatin Accessibility cell prints 0.84. The caption's rule is 'We report "
        "the best result among models in each family' and Section 4.2 says the row is reproduced from "
        "Marin et al. (BEND), but BEND's main results table prints 0.76 for GENA-LM BERT and 0.82 for "
        "GENA-LM BigBird in both the ICLR 2024 proceedings PDF pinned as "
        "evidence-expansion-bend-final-f709b6be and the arXiv rendition arXiv:2311.12570 retrieved on "
        "2026-11-16. No subset of the GENA-LM family reproduces all seven printed cells of the row, "
        "while the DNABERT, HyenaDNA and Nucleotide Transformer rows each have one that does, so the "
        "printed value is not the family best this paper says it reports and its origin is unknown. "
        "The printed value is kept as published; this entry withholds that one result from automatic "
        "comparison. The row's other six cells and the rest of the source are not covered."),
    "review_method": "independent-cell-check",
    "review_date": DATE,
    "source_id": "phylogpn-2025",
    "source_locator": "Table 2, row 'GENA-LM', column 'Chromatin Accessibility (AUROC)'",
}

REVIEW = {
    "method": ["automated-source-review", "independent-cell-check", "source-hash-verification"],
    "method_note": (
        "Independent review of the PhyloGPN batch. The artifact was re-retrieved from the recorded "
        "artifact_url on 2026-11-16 and its SHA-256 matched the stored value byte for byte. Its two "
        "tables were re-read cell by cell, its Methods, Results, Discussion, permissions statement and "
        "footnotes were read for the descriptive claims, and the Europe PMC core record for "
        "PMCID:PMC11908359 was read for the licence and the published-version metadata."),
    "reviewer": ["claude"],
    "reviewer_note": ("Claude review agent (independent of the extractor); no human review claimed. "
                      "Nothing was reproduced and no value was recomputed."),
    "date": DATE,
    "artifact_sha256": XML_SHA,
    "retrieval_url": XML_URL,
    "note": ("Reviewed with data/omics/phylogpn-20261116 and recorded in "
             "docs/reviews/2026-11-16-phylogpn.md. publication_status stays 'preprint': the pinned "
             "artifact is the preprint, and the version of record is named in version_note and pinned "
             "by phylogpn-20261116-source-springer-chapter."),
}


def patch(path, edits):
    """edits: {record id: function(record) -> bool changed}. Rewrites only matching lines."""
    with open(path, "rb") as handle:
        raw = handle.read()
    lines = raw.split(b"\n")
    done = {}
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        record = json.loads(line)
        edit = edits.get(record["id"])
        if edit is None:
            continue
        changed = edit(record)
        done[record["id"]] = changed
        if changed:
            lines[index] = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    missing = set(edits) - set(done)
    if missing:
        sys.exit(f"{path}: records not found: {sorted(missing)}")
    if any(done.values()):
        with open(path, "wb") as handle:
            handle.write(b"\n".join(lines))
    for rid, changed in sorted(done.items()):
        print(f"  {rid}: {'changed' if changed else 'already applied'}")


def edit_primary(record):
    attrs = record["attributes"]
    before = json.dumps(record, sort_keys=True)
    record["status"] = "source_checked"
    attrs["licence"] = "CC BY-NC-ND 4.0"
    attrs["version_note"] = VERSION_NOTE
    attrs["review"] = REVIEW
    attrs["evidence_concerns"] = [CONCERN]
    attrs.get("missing_metadata", {}).pop("licence", None)
    if not attrs.get("missing_metadata"):
        attrs.pop("missing_metadata", None)
    if not any(l["relation"] == "supersedes" and l["target_id"] == DUPLICATE
               for l in record["links"]):
        record["links"].append({"relation": "supersedes", "target_id": DUPLICATE})
    return json.dumps(record, sort_keys=True) != before


def set_superseded(record):
    if record["status"] == "superseded":
        return False
    record["status"] = "superseded"
    return True


def main():
    root = sys.argv[1]
    print("data/entities/sources.jsonl")
    patch(os.path.join(root, "data/entities/sources.jsonl"),
          {"phylogpn-2025": edit_primary, DUPLICATE: set_superseded})
    print("data/evidence/results/e.jsonl")
    patch(os.path.join(root, "data/evidence/results/e.jsonl"),
          {"b2-phylogpn-2025": set_superseded})


if __name__ == "__main__":
    main()
