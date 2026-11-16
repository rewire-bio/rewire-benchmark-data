"""Apply the POISK review pass to data/omics/poisk-20261115/batch.jsonl.

Writes the review object on every result and claim, applies the review's
corrections, and appends one metadata-correction claim per changed field.
"""

import hashlib
import json
import sys

BATCH = sys.argv[1]
REVIEW_DOC = "docs/reviews/2026-11-16-poisk.md"
DATE = "2026-11-16"
REVIEWED_AT = "2026-11-16T00:00:00Z"

LAYOUT_SHA = "e75c18130ca43770d2f0ed05ae96528759666c0e4fa08f7725f5a32b21187696"
PDF_SHA_RECORDED = "526def150fb5ae8f9ac4533efcf16c86e547e636cdb9bfba9a574cd1e2a2f924"
ZENODO_V101_SHA = "c1ee96e66dc4b8a694133aae0536dcc502c6d831b797d50337c002dd987505ee"
ZENODO_V11_SHA = "1b95773c269ca57f971f3b60c5df4558c48edc88b11580ca46e97a06e3d99981"
EXPLORER_SHA = "7795938b8f8bd488222d9a447f5148756029897d82acc127ef1babf158c46378"
JATS_SHA = "4ae08208acb49686958e1ad6a040494f3234ff7035b8cf41756b913ed6caa826"
V2_PDF_SHA = "aeaec593d7aa2d42382a49bd6fadbbccabaa6c084843ea1c7f0c91097dedb0c2"
V2_LAYOUT_SHA = "82a99bc2e061b7247cf65f7bc9450924b7af5be7ab3ef283d2284ba787ea629c"

REVIEWER_NOTE = (
    "Claude review agent (independent of the extractor); no human review claimed. "
    "Transcription was checked against the pinned source; nothing was reproduced and "
    "no value was recomputed."
)

METHOD_NOTE = (
    "Independent review pass. All five pinned artifacts were re-retrieved. The two Zenodo "
    "API responses, the explorer page and the bioRxiv v1 JATS XML all hashed to the values "
    "on their source records. The v1 PDF did not: three downloads on 2026-11-16 gave "
    "3389c1bf6d3654c5b2151a07fcfcefc67cf6f36e5f0facfc03c33521d8b84491 twice and "
    "d699fd680e3b0097ca80130c288e8d872773dc1e523044f4605e06fc4f89d9bc once, none equal to "
    "the recorded artifact_sha256, because bioRxiv regenerates the container on request. A "
    "pdftotext -layout run (poppler 26.08.0) on all three downloads gave the same text layer, "
    "byte for byte the contents of the archived artifacts/biorxiv-v1-layout.txt.gz, SHA-256 "
    + LAYOUT_SHA
    + ", so the archive is provably derived from the pinned article and is the artifact this "
    "review verified values against. npm run batch -- check-values reproduced the extractor's "
    "figures exactly (36 in_cell, 36 in_row, 6 locator_not_parsed, no wrong_column and no "
    "overclaimed_in_row) and wrote an identical value-check.tsv. All 78 results were then "
    "re-read by review/check_values_independent.py, written for this pass and importing nothing "
    "from extract/build_batch.py: it takes each table's column spans from the character offsets "
    "of the label text in that table's own printed header lines, assigns every numeric token on "
    "a body row to the column whose centre is nearest and rejects the row unless the token count "
    "matches the column count, the nearest column is the one in the token's own left-to-right "
    "position, and the runner-up column loses by at least three characters; it also checks that "
    "Table 1's sub-columns sit under their group labels and that Table 7's Coverage group does "
    "not reach the Ties column. Records are matched to cells through each result's source_locator "
    "text, not its ID. 72 results were checked in cell, including all 36 the repository parser "
    "could only place at row level, and the 6 prose values were checked against the sentence each "
    "locator names. Two negative controls confirmed the checker fails on a swapped pair of values "
    "and on a value shifted into a neighbouring column of the same row, which a row-level check "
    "passes. Independently of the script, all 42 printed cells of Tables 2 and 7 were transcribed "
    "by hand into review/manual-transcription.tsv and compared with the records, covering column "
    "assignment for every one of the 36 cells left unverified at extraction. Version 2 of the "
    "preprint, posted 2026-11-14, was retrieved (PDF SHA-256 "
    + V2_PDF_SHA
    + ", text layer "
    + V2_LAYOUT_SHA
    + "): every numeric token in it is identical to v1's apart from an added author affiliation "
    "and the two Zenodo record identifiers, so no stored value changes and the batch stays pinned "
    "to v1. The 40 descriptive claims were read against the pinned PDF text layer, both Zenodo "
    "API responses and the explorer page."
)


def review(artifact_sha, note=None, methods=None):
    obj = {
        "artifact_sha256": artifact_sha,
        "date": DATE,
        "method": methods
        or [
            "independent-cell-check",
            "deterministic-table-parse",
            "pdf-text-parse",
            "source-hash-verification",
        ],
        "method_note": METHOD_NOTE,
        "retrieval_url": "https://www.biorxiv.org/content/10.64898/2026.10.24.761513v1.full.pdf",
        "reviewed_at": REVIEWED_AT,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
    }
    if note:
        obj["note"] = note
    return obj


# Which artifact each claim was checked against, by claim ID suffix.
ZENODO_V11_CLAIMS = {
    "claim-v1-1-audit-verdicts",
    "claim-v1-1-chain-pair-labels",
    "claim-v1-1-folding-version",
    "claim-v1-1-licence",
    "claim-v1-1-row-count",
    "claim-v1-1-target-sequence-provenance",
}
ZENODO_V101_CLAIMS = {
    "claim-audit-verdict-tiers-v1-0-1",
    "claim-dataset-licence-v1-0-1",
}

PDF_NOT_STABLE_NOTE = (
    "Checked against the archived pdftotext -layout text layer of the pinned v1 PDF, SHA-256 "
    + LAYOUT_SHA
    + ". The PDF container itself is not byte-stable at bioRxiv, so the source record's "
    "artifact_sha256 (" + PDF_SHA_RECORDED + ") does not reproduce; the text layer does, from "
    "three independent downloads. The value was also confirmed against the version 2 PDF posted "
    "2026-11-14, whose tables print the same numbers."
)

GEOMETRY_NOTE = (
    "Column assignment re-checked from the character geometry of the table's own header line and "
    "independently transcribed by hand into review/manual-transcription.tsv. " + PDF_NOT_STABLE_NOTE
)

EPITOPE_IMPL = (
    "Geometric epitope contact: a record counts as recovered when at least one annotated epitope "
    "residue in the folded antigen construct has a heavy atom within 4 angstrom of an antibody "
    "heavy atom in the predicted complex. The paper states it as \"We counted a record as "
    "recovered when at least one annotated epitope residue had a heavy atom within 4Å of an "
    "antibody heavy atom\". No interface confidence score, ipSAE included, enters this endpoint."
)

CONSENSUS_IMPL = (
    "Cross-model pose agreement: DockQ scores are computed for the Fv-antigen interface of each "
    "model's predicted complex, and consensus is the stated number of models predicting the same "
    "pose above the stated DockQ threshold. The paper states the decision rule as \"For any given "
    "pair, a prediction was considered successful if the binder demonstrated structural agreement "
    "amongst more models than its decoy\". The pair is decided by which member has agreement "
    "among more models, not by an interface confidence score; ipSAE does not enter this endpoint."
)

NEW_HASH_SCOPE = (
    "One download of 2026-11-15. The PDF container is not byte-stable: bioRxiv regenerates it on "
    "request, so artifact_sha256 is that one download's hash and no refetch reproduces it. Three "
    "downloads on 2026-11-16 gave 3389c1bf6d3654c5b2151a07fcfcefc67cf6f36e5f0facfc03c33521d8b84491 "
    "twice and d699fd680e3b0097ca80130c288e8d872773dc1e523044f4605e06fc4f89d9bc once. All three "
    "yield the same pdftotext -layout text layer, SHA-256 " + LAYOUT_SHA + ", which is the "
    "article's stable identity, is archived gzipped in artifacts/biorxiv-v1-layout.txt.gz under "
    "archive_sha256, is what extract/build_batch.py asserts, and is what every stored value was "
    "read from."
)

NEW_V2_LIMITATION = (
    "A version 2 of this preprint was posted on 14 November 2026. It was retrieved during review: "
    "PDF SHA-256 " + V2_PDF_SHA + ", pdftotext -layout text layer SHA-256 " + V2_LAYOUT_SHA + ". "
    "Every numeric token in version 2 is identical to version 1's apart from an added author "
    "affiliation and the two Zenodo record identifiers, which change from 19883049 (dataset "
    "version 1.0.1) to 21775623 (version 1.1), so no value in this batch differs between the two "
    "versions. Every record stays pinned to version 1, which is the artifact the values were read "
    "from."
)

NEW_BYTE_LIMITATION = (
    "bioRxiv regenerates this PDF on request, so its artifact_sha256 is one download's hash and no "
    "refetch reproduces it. The stable identity is the pdftotext -layout text layer, SHA-256 "
    + LAYOUT_SHA
    + "."
)

NEW_V11_SCOPE_NOTE_TAIL = (
    " Relationship to version 1.0.1, after review: no link is recorded between the two dataset "
    "records. The releases do not hold the same data, so same_data_as, which states informational "
    "data reuse, does not apply: the Zenodo file lists give poisk_dataset.csv as 124,175,590 bytes "
    "with md5 1d663c6797f03466349c995b4e8a913a in version 1.0.1 and 234,128,089 bytes with md5 "
    "f0c1f098abf1756e4b9891aa4dc028ee here, and this record's own description says version 1.1 "
    "corrects errors found in version 1.0.1. supersedes is not recorded either, because version "
    "1.0.1 is still the release the published folding predictions were run against and is what "
    "every evaluation in this batch pins. The two releases share "
    "poisk_all_models_folding_metrics.zip, md5 9b56b7095d32c3c2357aa6d4fa3369f8, which "
    "claim-v1-1-folding-metrics-files records, and claim-v1-1-folding-version carries the release's "
    "own statement about which version the predictions were run against."
)

OPENFOLD3_PROVENANCE_TAIL = (
    " Checked against the store during review: no model record for this engine exists under any "
    "other ID, but the store does already hold it as an unparented configuration, "
    "esmfold2-2026-runs-n-poses-method-openfold3-msa, named \"OpenFold3 (MSA)\", whose links array "
    "is empty. That configuration should gain a family edge to this record; the edge is not made "
    "here because it changes a stored record outside this batch. discovery-model-openfold is "
    "OpenFold, a PyTorch implementation of AlphaFold 2 and AlphaFold-Multimer, and is not this "
    "engine."
)

records = [json.loads(l) for l in open(BATCH, encoding="utf-8")]
by_id = {r["id"]: r for r in records}
corrections = []


def correction(subject_id, field, previous_value, value, source_locator, note):
    digest = hashlib.sha256(
        f"{subject_id}|{field}|{REVIEW_DOC}".encode("utf-8")
    ).hexdigest()[:20]
    subject = by_id[subject_id]
    corrections.append(
        {
            "id": f"metadata-correction-{digest}",
            "kind": "claim",
            "name": f"{subject['name']}: {field}",
            "description": (
                "Correction made by the independent review of the POISK batch. The previous value "
                "is kept here."
            ),
            "status": "source_checked",
            "facets": {"areas": ["molecular-interactions", "proteins-complexes"]},
            "source_ids": subject["source_ids"],
            "links": [{"relation": "subject", "target_id": subject_id}],
            "attributes": {
                "field": field,
                "previous_value": previous_value,
                "value": value,
                "source_locator": source_locator,
                "review": review(LAYOUT_SHA, note=note),
            },
        }
    )


# ---------------------------------------------------------------- corrections
# 1 to 3: metric_implementation on three protocols whose endpoint does not use ipSAE.
for pid, impl, loc in [
    (
        "poisk-20261115-protocol-epitope-recovery",
        EPITOPE_IMPL,
        "Section 3.3.2, sentence beginning \"We counted a record as recovered\"; Table 2",
    ),
    (
        "poisk-20261115-protocol-consensus-pairwise-accuracy",
        CONSENSUS_IMPL,
        "Section 3.3.1, sentences beginning \"To test this, we calculated DockQ scores\" and "
        "\"For any given pair, a prediction was considered successful\"",
    ),
    (
        "poisk-20261115-protocol-consensus-pair-coverage",
        CONSENSUS_IMPL,
        "Section 3.3.1, sentences beginning \"To test this, we calculated DockQ scores\" and "
        "\"For any given pair, a prediction was considered successful\"",
    ),
]:
    proto = by_id[pid]
    old = proto["attributes"]["metric_implementation"]
    affected = sorted(
        r["id"]
        for r in records
        if r["kind"] == "evaluation"
        and any(l["relation"] == "assessment" and l["target_id"] == pid for l in r["links"])
    )
    correction(
        pid,
        "metric_implementation",
        old,
        impl,
        loc,
        "The protocol carried the full-Fv ipSAE implementation text, which describes a scoring "
        "step this endpoint does not use. Corrected on the protocol and, with the same text, in "
        "comparison.metric_implementation on the evaluations that assess it: "
        + ", ".join(affected)
        + ".",
    )
    proto["attributes"]["metric_implementation"] = impl
    for r in records:
        if r["id"] in affected:
            r["attributes"]["comparison"]["metric_implementation"] = impl

# 4: hash_scope on the manuscript source.
src = by_id["poisk-20261115-source-manuscript-v1"]
correction(
    src["id"],
    "hash_scope",
    src["attributes"]["hash_scope"],
    NEW_HASH_SCOPE,
    "Three downloads of https://www.biorxiv.org/content/10.64898/2026.10.24.761513v1.full.pdf on "
    "2026-11-16 and their pdftotext -layout output",
    "The recorded artifact_sha256 does not reproduce. It is not wrong about what was downloaded "
    "on 2026-11-15, so it is left as it stands; the field now says what the hash covers and names "
    "the text layer as the article's stable identity.",
)
src["attributes"]["hash_scope"] = NEW_HASH_SCOPE

# 5: limitations on the manuscript source (version 2 was retrievable after all).
old_limits = list(src["attributes"]["limitations"])
new_limits = []
for entry in old_limits:
    if entry.startswith("A version 2 of this preprint"):
        new_limits.append(NEW_V2_LIMITATION)
    else:
        new_limits.append(entry)
new_limits.append(NEW_BYTE_LIMITATION)
correction(
    src["id"],
    "limitations",
    json.dumps(old_limits, ensure_ascii=False),
    json.dumps(new_limits, ensure_ascii=False),
    "bioRxiv API details for 10.64898/2026.10.24.761513; "
    "https://www.biorxiv.org/content/10.64898/2026.10.24.761513v2.full.pdf",
    "The entry stating that version 2's full text was not available and its PDF not retrieved is "
    "false as of this review: the version 2 PDF was retrieved and compared. An entry on the PDF's "
    "byte instability was added.",
)
src["attributes"]["limitations"] = new_limits
src["attributes"]["review_artifact"] = (
    "pdftotext -layout text layer of three refetched v1 PDFs, all SHA-256 "
    + LAYOUT_SHA
    + ", byte-identical to the contents of artifacts/biorxiv-v1-layout.txt.gz"
)
src["attributes"]["review_artifact_format"] = "text/plain, pdftotext -layout output"
src["attributes"]["review_artifact_matches_original_artifact_sha256"] = False

# 6: the same_data_as link on dataset version 1.1.
ds = by_id["poisk-20261115-dataset-poisk-v1-1"]
old_links = json.dumps(ds["links"], ensure_ascii=False)
ds["links"] = [l for l in ds["links"] if l["relation"] != "same_data_as"]
correction(
    ds["id"],
    "links",
    old_links,
    json.dumps(ds["links"], ensure_ascii=False),
    "Zenodo records 19883049 and 21775623, file lists and description section 'Dataset Structure "
    "and Documentation'",
    "same_data_as states informational data reuse and the practice recorded in earlier reviews is "
    "that it requires identical data. The two releases hold different files: poisk_dataset.csv is "
    "124,175,590 bytes with md5 1d663c6797f03466349c995b4e8a913a in version 1.0.1 and 234,128,089 "
    "bytes with md5 f0c1f098abf1756e4b9891aa4dc028ee in version 1.1, which also states that it "
    "corrects errors found in version 1.0.1. The link was removed and no replacement edge was "
    "added, because version 1.0.1 is not superseded: it is still the release the published folding "
    "predictions were run against.",
)

# 7: scope_note on dataset version 1.1, recording the relationship the link used to assert.
old_scope = ds["attributes"]["scope_note"]
correction(
    ds["id"],
    "scope_note",
    old_scope,
    old_scope + NEW_V11_SCOPE_NOTE_TAIL,
    "Zenodo records 19883049 and 21775623, file lists and description sections 'Dataset Structure "
    "and Documentation' and 'Relationship to the folding predictions'",
    "States in the record what the removed same_data_as link used to assert, and why neither that "
    "relation nor supersedes is recorded. reuse_note is declared for dataset_subset only, so the "
    "note goes in scope_note.",
)
ds["attributes"]["scope_note"] = old_scope + NEW_V11_SCOPE_NOTE_TAIL

# 8: provenance_note on the OpenFold3 model record.
mdl = by_id["poisk-20261115-model-openfold3"]
old_prov = mdl["attributes"]["provenance_note"]
correction(
    mdl["id"],
    "provenance_note",
    old_prov,
    old_prov + OPENFOLD3_PROVENANCE_TAIL,
    "data/entities/configurations.jsonl, record "
    "esmfold2-2026-runs-n-poses-method-openfold3-msa; data/entities/models.jsonl, record "
    "discovery-model-openfold",
    "The store already holds this engine as an unparented configuration under another ID. The new "
    "family record is still the right record, and the pointer is recorded so the missing family "
    "edge is not lost.",
)
mdl["attributes"]["provenance_note"] = old_prov + OPENFOLD3_PROVENANCE_TAIL

# ------------------------------------------------- review object on each record
for r in records:
    if r["kind"] == "result":
        loc = r["attributes"]["source_locator"]
        if loc.startswith("Table 2") or loc.startswith("Table 7"):
            note = GEOMETRY_NOTE
        elif loc.startswith("Table"):
            note = (
                "Column assignment re-checked from the character geometry of the table's own "
                "header line. " + PDF_NOT_STABLE_NOTE
            )
        else:
            note = (
                "Prose value: checked against the sentence the locator names, present verbatim in "
                "the text layer, and against which engine or setting the sentence attaches it to. "
                + PDF_NOT_STABLE_NOTE
            )
        r["attributes"]["review"] = review(LAYOUT_SHA, note=note)
    elif r["kind"] == "claim":
        short = r["id"].replace("poisk-20261115-", "")
        if short in ZENODO_V11_CLAIMS:
            r["attributes"]["review"] = review(
                ZENODO_V11_SHA,
                note="Read against the re-retrieved Zenodo API response for record 21775623, "
                "which hashed to the value on its source record.",
                methods=["independent-cell-check", "automated-source-review",
                         "source-hash-verification"],
            )
        elif short in ZENODO_V101_CLAIMS:
            r["attributes"]["review"] = review(
                ZENODO_V101_SHA,
                note="Read against the re-retrieved Zenodo API response for record 19883049, "
                "which hashed to the value on its source record.",
                methods=["independent-cell-check", "automated-source-review",
                         "source-hash-verification"],
            )
        elif short == "claim-publication-status":
            r["attributes"]["review"] = review(
                EXPLORER_SHA,
                note="The re-retrieved explorer page hashed to the value on its source record and "
                "renders \"Read the paper ↗ · Accepted at NeurIPS 2026\" in its hero "
                "section, so \"Accepted at NeurIPS 2026\" is verbatim and the separator is "
                "transcribed. The bioRxiv API reports published \"NA\" for both versions and every "
                "page of the pinned PDF carries the not-certified-by-peer-review banner, so the "
                "source record's publication_status of preprint stands; the acceptance is a "
                "project-site statement and belongs here, not on the source.",
                methods=["independent-cell-check", "automated-source-review",
                         "source-hash-verification"],
            )
        elif short == "claim-v1-1-folding-metrics-files":
            r["attributes"]["review"] = review(
                ZENODO_V11_SHA,
                note="Checked against both re-retrieved Zenodo API responses: "
                "poisk_all_models_folding_metrics.zip is 19,209,963 bytes with md5 "
                "9b56b7095d32c3c2357aa6d4fa3369f8 in record 19883049 and in record 21775623, so "
                "the same archive is attached to both releases.",
                methods=["independent-cell-check", "automated-source-review",
                         "source-hash-verification"],
            )
        else:
            r["attributes"]["review"] = review(
                LAYOUT_SHA,
                note="Read against the archived pdftotext -layout text layer of the pinned v1 PDF. "
                + PDF_NOT_STABLE_NOTE,
            )

records.extend(corrections)
records.sort(key=lambda r: r["id"])
with open(BATCH, "w", encoding="utf-8") as fh:
    for r in records:
        fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

print(f"records: {len(records)} (added {len(corrections)} correction claims)")
for c in corrections:
    print("  ", c["id"], c["attributes"]["field"], "->", c["links"][0]["target_id"])
