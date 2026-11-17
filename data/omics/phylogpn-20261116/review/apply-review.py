#!/usr/bin/env python3
"""Write the review pass into batch.jsonl: review objects, the two rulings on the
cross-source leads, the protocol's task-link exemption, the supersedes link on the
legacy duplicate result, and the metadata-correction claims for the stored-record
changes this review makes.

Idempotent: running it twice gives the same bytes.

Usage:
  python3 -I apply-review.py <batch.jsonl>
"""

import json
import sys

DATE = "2026-11-16"
XML_SHA = "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224"
SUPP_SHA = "b4885d288e03ae976acafb2b6b1c3837572dce224c8803715f4d329966ba65f4"
SPRINGER_SHA = "31d3954fe7909256c70099ca0153500b1ab4c72314208e825dbd298276d4f0e7"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11908359/fullTextXML"
SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11908359/supplementaryFiles"
SPRINGER_URL = "https://link.springer.com/chapter/10.1007/978-3-031-90252-9_7"
REVIEW_DOC = "docs/reviews/2026-11-16-phylogpn.md"
REVIEWER_NOTE = ("Claude review agent (independent of the extractor); no human review claimed. "
                 "Transcription was checked against the pinned sources; nothing was reproduced.")

CELL_METHOD_NOTE = (
    "Independent review pass by a different agent from the extractor, on the extraction frozen at "
    "batch.jsonl SHA-256 fbf8f6410ec0063a5e7beea4b0c8842052cafe5d26be31d70cbe9e341dce4903. The pinned "
    "Europe PMC full text XML was re-retrieved and its SHA-256 matched the stored source record byte "
    "for byte. All 124 results were re-read by review/reread.py, written for this pass, which parses "
    "the two table-wrap elements with xml.etree, keys every cell by its printed row label and column "
    "header, and does not use extract/parse_tables.py or extract/tables.json. For each result it "
    "checks the printed value, the numeric value, the metric concept against the column header's own "
    "parenthetical (MCC, AUPRC, AUROC) or the Table 1 caption, the direction, the unit, that "
    "uncertainty and denominator are recorded as unreported, that each locator resolves to exactly "
    "one cell, that no cell is claimed twice and that every printed cell has exactly one result; and "
    "it checks each evaluation's row-to-configuration assignment against a mapping written "
    "independently from the paper. review/controls.py shows the check rejects a swapped value, a "
    "value shifted one column, a row label shifted one row, and a zero recorded for a printed N/A "
    "cell. The six printed N/A cells were read in the raw markup; no result, no evaluation and no "
    "zero stands in for them. npm run batch -- check-values reported 124 in_cell and reproduced "
    "value-check.tsv byte for byte. A manual sample of ten rows, 70 cells, including the three "
    "asterisked cells and one row from each family-best row, was read by eye in the raw markup "
    "(review/manual-sample.txt). review/family-best.py recomputed all 35 compiled Table 2 cells "
    "against the BEND results already in the store.")

PROSE_METHOD_NOTE = (
    "Independent review pass by a different agent from the extractor. Each field was re-read against "
    "the pinned artifact at the recorded locator: the Europe PMC full text XML, whose SHA-256 was "
    "re-checked, and, where the record cites it, the supplement PDF, whose member hash was re-checked "
    "inside a third, differently hashed Europe PMC zip. No number in these records comes from a figure.")


def methods(record):
    kind = record["kind"]
    sids = record.get("source_ids") or []
    if kind in ("result", "evaluation"):
        return ["independent-cell-check", "deterministic-table-parse", "source-hash-verification"]
    base = ["transcription", "source-hash-verification"]
    if "phylogpn-20261116-source-supplement" in sids or record["id"] == "phylogpn-20261116-source-supplement":
        base.insert(1, "pdf-text-parse")
    if kind == "source":
        base = ["automated-source-review"] + base[1:]
    return base


def artifact(record):
    sids = record.get("source_ids") or []
    if record["id"] == "phylogpn-20261116-source-supplement":
        return SUPP_SHA, SUPP_URL
    if record["id"] == "phylogpn-20261116-source-springer-chapter":
        return SPRINGER_SHA, SPRINGER_URL
    if "phylogpn-2025" in sids:
        return XML_SHA, XML_URL
    if "phylogpn-20261116-source-supplement" in sids:
        return SUPP_SHA, SUPP_URL
    if "phylogpn-20261116-source-springer-chapter" in sids:
        return SPRINGER_SHA, SPRINGER_URL
    return XML_SHA, XML_URL


NOTES = {
    "phylogpn-20261116-source-supplement": (
        "Re-retrieved on 2026-11-16. The Europe PMC supplementaryFiles zip came back with a third "
        "distinct hash, 16291039db97b7b7183bc3e4747f99ad6804750ce4e189ec79625125c9f5e451, and the "
        "member NIHPP2503.03773v1-supplement-1.pdf inside it matched the pinned "
        "b4885d288e03ae976acafb2b6b1c3837572dce224c8803715f4d329966ba65f4 exactly. hash_scope "
        "describes the artifact correctly. The archived copy in artifacts/ decompresses to the same "
        "hash, and the gzip file itself matches the recorded archive_sha256."),
    "phylogpn-20261116-source-springer-chapter": (
        "Re-retrieved on 2026-11-16 and the page differed in bytes again, giving a third hash "
        "(8949d32ae1aa060215a0c9a33b4220426122c40301ae8d559e04a24ecf603247), so hash_scope is right "
        "that the hash describes one retrieval. The page's own citation metadata was read for this "
        "review: LNBI volume 15647, citation_firstpage 99, citation_lastpage 117, First Online "
        "25 April 2025, RECOMB conference series, the five authors, and 'This is a preview of "
        "subscription content'. Crossref agrees (book-chapter, pages 99-117, published online "
        "2025-04-25), and so does Europe PMC's own core record for PMCID:PMC11908359, which carries "
        "PMID 40093357, the chapter DOI and licence cc by-nc-nd although its TITLE and DOI search "
        "index returns no hits. No value in this batch comes from this page."),
    "phylogpn-20261116-claim-preprint-licence": (
        "The pinned XML prints 'This work is licensed under a Creative Commons "
        "Attribution-NonCommercial-NoDerivatives 4.0 International License'. Europe PMC's core "
        "record for this article independently gives licence 'cc by-nc-nd'. Applied to the stored "
        "source record phylogpn-2025 by this review, with "
        "metadata-correction-phylogpn-2025-licence keeping the previous state."),
    "phylogpn-20261116-claim-version-of-record": (
        "Checked against the Springer chapter page's citation metadata, Crossref and Europe PMC's "
        "core record for PMCID:PMC11908359, which all give the same chapter, volume, page range, "
        "first-online date and DOI. Applied to the stored source record phylogpn-2025 by this "
        "review, with metadata-correction-phylogpn-2025-version-note keeping the previous state. "
        "publication_status stays 'preprint' because the pinned artifact is the preprint."),
}

GENA_DISCREPANCY = (
    "The printed 0.84 is above both GENA-LM values BEND prints in its main results table, GENA-LM "
    "BERT 0.76 and GENA-LM BigBird 0.82, so it is not the best result among the models of this "
    "family as the caption's rule states. Reviewed on 2026-11-16 against two renditions of BEND: "
    "the ICLR 2024 proceedings PDF this store pins as evidence-expansion-bend-final-f709b6be, and "
    "the arXiv rendition arXiv:2311.12570 retrieved on 2026-11-16 (SHA-256 "
    "bfb40a6afe8028a52ea6c810bba3729510f1e768cc1288026b46e458df2d4ec9). Both print 0.76 and 0.82, "
    "and no subset of the GENA-LM family reproduces all seven printed cells of this row, while the "
    "DNABERT, HyenaDNA and Nucleotide Transformer rows each have one that does. The printed value "
    "stands as printed and is not corrected. The review added an evidence concern to phylogpn-2025 "
    "naming this result, so it is withheld from automatic comparison until the upstream value is "
    "settled.")

NT_DISCREPANCY = (
    "The printed 0.54 is the stored NT-MS value from BEND's main results table, while the stored "
    "NT-H value is 0.55, so it is not the maximum over every Nucleotide Transformer model BEND "
    "scored. Reviewed on 2026-11-16 and resolved: taking the best result over the multi-genome "
    "Nucleotide Transformer models alone, leaving out NT-H, BEND's human-reference-only checkpoint, "
    "reproduces all seven printed cells of this row exactly ({NT-MS, NT-V2} and "
    "{NT-MS, NT-1000G, NT-V2} both do, and no subset including NT-H does). The family this paper "
    "applied the caption's rule to therefore appears not to include NT-H. Recorded as a difference "
    "in how the family is defined, not an error; the printed value stands and no evidence concern "
    "was added.")

TASK_LINK_EXEMPTION = (
    "No task or benchmark in the store covers ClinVar pathogenicity classification across these "
    "variant classes: the only candidates are the per-class legacy silos such as "
    "reported-task-ed3dd3b83c4505, which are needs_review and whose own attributes say structured "
    "extraction is pending. Left unlinked on purpose, as "
    "lu-hetero-20261019-protocol-clinvar-variant-type-auroc is, so the discrepancy rules treat its "
    "scope as unknown rather than guess at a shared task (#208). Reviewed 2026-11-16.")


def review_object(record):
    sha, url = artifact(record)
    note = NOTES.get(record["id"])
    if note is None:
        if record["kind"] in ("result", "evaluation"):
            note = (f"Cell re-read at {record['attributes'].get('source_locator')} in the pinned JATS "
                    "XML by review/reread.py; the printed value, the numeric value, the metric taken "
                    "from the printed column header, the direction, the unit and the row-to-"
                    "configuration assignment all matched.")
        else:
            note = (f"Re-read against the pinned source at {record['attributes'].get('source_locator')}; "
                    "no change.")
    return {
        "method": methods(record),
        "method_note": CELL_METHOD_NOTE if record["kind"] in ("result", "evaluation") else PROSE_METHOD_NOTE,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
        "date": DATE,
        "artifact_sha256": sha,
        "retrieval_url": url,
        "note": note,
    }


def correction(suffix, name, subject, field, previous, value, locator, note, source_ids):
    return {
        "id": f"metadata-correction-{suffix}",
        "kind": "claim",
        "name": name,
        "description": ("Record change made by the 2026-11-16 PhyloGPN review; the previous value is "
                        "kept here and historical releases keep it too."),
        "status": "source_checked",
        "facets": {"areas": ["dna-genomes"], "contexts": ["research"]},
        "source_ids": source_ids,
        "links": [{"relation": "subject", "target_id": subject}],
        "attributes": {
            "field": field,
            "previous_value": previous,
            "value": value,
            "source_locator": locator,
            "review": {
                "method": ["automated-source-review", "source-hash-verification"],
                "method_note": ("Change applied by the independent review of the PhyloGPN batch and "
                                f"recorded in {REVIEW_DOC}. The previous value was read from the "
                                "stored record before the change."),
                "reviewer": ["claude"],
                "reviewer_note": REVIEWER_NOTE,
                "date": DATE,
                "note": note,
            },
        },
    }


VERSION_NOTE_VALUE = (
    "Published as a peer-reviewed conference paper: Albors C., Li J.C., Benegas G., Ye C., Song Y.S., "
    "A Phylogenetic Approach to Genomic Language Modeling, Research in Computational Molecular Biology "
    "(RECOMB 2025), Lecture Notes in Computer Science (LNBI) volume 15647, pages 99-117, first online "
    "25 April 2025, doi 10.1007/978-3-031-90252-9_7. The pinned artifact remains the preprint, so "
    "publication_status stays 'preprint'; the version of record is paywalled and was not compared with "
    "the preprint.")

CORRECTIONS = [
    correction(
        "phylogpn-2025-licence", "phylogpn-2025: attributes.licence", "phylogpn-2025",
        "attributes.licence",
        "absent; missing_metadata.licence held {\"reason\": \"unextracted\"}",
        "CC BY-NC-ND 4.0",
        "Permissions statement of the PMC deposit of arXiv:2503.03773v1, in the pinned full text XML",
        "The XML prints 'This work is licensed under a Creative Commons "
        "Attribution-NonCommercial-NoDerivatives 4.0 International License'. Europe PMC's core record "
        "for PMCID:PMC11908359 independently gives licence 'cc by-nc-nd'. The missing_metadata entry "
        "for licence was removed with the fill.",
        ["phylogpn-2025"]),
    correction(
        "phylogpn-2025-version-note", "phylogpn-2025: attributes.version_note", "phylogpn-2025",
        "attributes.version_note", "absent", VERSION_NOTE_VALUE,
        "Springer chapter page citation metadata (series, volume, citation_firstpage, "
        "citation_lastpage, First Online); Crossref 10.1007/978-3-031-90252-9_7; Europe PMC core "
        "record for PMCID:PMC11908359",
        "Applies phylogpn-20261116-claim-version-of-record to the stored record so a reader of the "
        "preprint source finds the version of record. publication_status is unchanged.",
        ["phylogpn-20261116-source-springer-chapter", "phylogpn-2025"]),
    correction(
        "phylogpn-2025-status", "phylogpn-2025: status", "phylogpn-2025",
        "status", "discovered", "source_checked",
        "Pinned full text XML re-retrieved 2026-11-16; SHA-256 "
        "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224",
        "The record was still 'discovered' although it is the source every result in this batch "
        "cites. This review re-retrieved its artifact, matched the pinned hash byte for byte, read "
        "its tables, prose, permissions statement and footnotes, and filled attributes.review, so "
        "'source_checked' is what the record now describes. It is not 'reproduced': nothing was rerun.",
        ["phylogpn-2025"]),
    correction(
        "phylogpn-2025-evidence-concerns", "phylogpn-2025: attributes.evidence_concerns",
        "phylogpn-2025", "attributes.evidence_concerns", "absent",
        "One scoped entry naming phylogpn-20261116-result-t2-chromatin-gena-lm: Table 2's GENA-LM "
        "Chromatin Accessibility cell, printed 0.84, is above every GENA-LM value BEND prints in its "
        "main results table, so it is withheld from automatic comparison. The printed value is kept.",
        "Table 2, row 'GENA-LM', column 'Chromatin Accessibility (AUROC)'",
        "The concern names one result and nothing else, so the rest of the source stays usable and "
        "the other 123 results are unaffected.",
        ["phylogpn-2025", "evidence-expansion-bend-final-f709b6be"]),
    correction(
        "phylogpn-2025-supersedes-duplicate", "phylogpn-2025: links", "phylogpn-2025",
        "links",
        "No links.",
        "One link: supersedes evidence-expansion-p2-phylogpn-2025-807f3a26cbfa",
        "Both source records carry artifact_sha256 "
        "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224 and the same Europe PMC "
        "fullTextXML artifact URL",
        "Two source records pinned the same bytes for the same paper. This review re-retrieved the "
        "artifact and reproduced that hash, so they are the same bytes. phylogpn-2025 is the record "
        "every result and claim cites and the one the catalogue keeps, so it supersedes the duplicate "
        "rather than the other way round.",
        ["phylogpn-2025"]),
    correction(
        "evidence-expansion-p2-phylogpn-2025-status",
        "evidence-expansion-p2-phylogpn-2025-807f3a26cbfa: status",
        "evidence-expansion-p2-phylogpn-2025-807f3a26cbfa",
        "status", "source_checked", "superseded",
        "Both source records carry artifact_sha256 "
        "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224",
        "A duplicate source record for the same bytes as phylogpn-2025. It supports no result; the "
        "only record citing it is the legacy task reported-task-ed3dd3b83c4505, which cites "
        "phylogpn-2025 as well, so nothing is withdrawn by retiring it. docs/collection.md asks for "
        "duplicate source records to be dealt with because they make the graph harder to use. Its "
        "source_ids on that legacy task were left in place: rewriting a needs_review silo record "
        "belongs with the ruling on b2-phylogpn-2025's other three silo records.",
        ["phylogpn-2025"]),
    correction(
        "b2-phylogpn-2025-status", "b2-phylogpn-2025: status", "b2-phylogpn-2025",
        "status", "source_checked", "superseded",
        "Table 1, row '3’ UTR', column 'PhyloGPN'",
        "The legacy record holds the same cell and the same value, 0.94, as "
        "phylogpn-20261116-result-t1-utr3-phylogpn, which now supersedes it. The legacy record has "
        "metric_direction 'unknown', which is wrong for an AUROC, no metric qualifier, and hangs off "
        "three needs_review silo records. The value is not edited and the record is kept, as "
        "lit-007 and lit-008 were when the DNALongBench batch replaced them.",
        ["phylogpn-2025"]),
]


def main():
    path = sys.argv[1]
    records = [json.loads(line) for line in open(path)]
    records = [r for r in records if not r["id"].startswith("metadata-correction-")]
    by_id = {r["id"]: r for r in records}

    for record in records:
        attrs = record["attributes"]
        if "review" in attrs or record["kind"] in ("result", "evaluation", "claim", "source"):
            attrs["review"] = review_object(record)

    # Rulings on the two cross-source leads.
    by_id["phylogpn-20261116-result-t2-chromatin-gena-lm"]["attributes"]["source_discrepancy"] = GENA_DISCREPANCY
    by_id["phylogpn-20261116-result-t2-expression-vep-nucleotide-transformer"]["attributes"][
        "source_discrepancy"] = NT_DISCREPANCY

    # The protocol has no task link, so the task-link ratchet needs a reason.
    by_id["phylogpn-20261116-protocol-clinvar-llr-auroc"]["attributes"][
        "task_link_exemption"] = TASK_LINK_EXEMPTION

    # Retire the legacy duplicate result.
    new_result = by_id["phylogpn-20261116-result-t1-utr3-phylogpn"]
    if not any(l["relation"] == "supersedes" for l in new_result["links"]):
        new_result["links"].append({"relation": "supersedes", "target_id": "b2-phylogpn-2025"})

    # Both claims that proposed stored-record fills were applied by this review.
    for claim_id in ("phylogpn-20261116-claim-preprint-licence",
                     "phylogpn-20261116-claim-version-of-record"):
        by_id[claim_id]["status"] = "source_checked"

    records.extend(CORRECTIONS)
    records.sort(key=lambda r: r["id"])
    with open(path, "w") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} records to {path}")


if __name__ == "__main__":
    main()
