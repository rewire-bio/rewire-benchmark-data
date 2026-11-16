#!/usr/bin/env python3
"""Apply the GPN-Star review pass to data/omics/gpn-star-20261116/batch.jsonl.

Writes the review object on every record and applies the five corrections the
review made. The batch is not yet in the store, so corrections are edits to
batch.jsonl and need no metadata-correction claim.

Usage: python3 -I apply_review.py <batch.jsonl>
"""

import json
import sys

BATCH = sys.argv[1]
DATE = "2026-11-16"
REVIEWED_AT = "2026-11-16T01:30:00Z"

ART_SHA = "d7dfe801bad2a0a23478753147af2320bc31c8b37ee50d66f1a1af8385e9005d"
SI_SHA = "3f7e8f71710bb63ec5ff032e697b6ef85f0d6d74411a31865fed73a757c7fc9e"
BIORXIV_SHA = "ec829bce7b9192a6a396f29d4ab90ac5de6c4903232bdf9328eb1c53e626af7a"
HF_SHA = "4e8141d673c18e6ab131eba8e1cbef7f29aa4403d5a4864218b06b90d07b275d"
AAP_SHA = "97f61ec05d4ace41692549290db3faf019ce869459459d2c5694bf54e16d0996"

ART_URL = "https://www.nature.com/articles/s41586-026-11005-5.pdf"
SI_URL = (
    "https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-026-11005-5/"
    "MediaObjects/41586_2026_11005_MOESM1_ESM.pdf"
)
BIORXIV_URL = (
    "https://www.biorxiv.org/content/biorxiv/early/2025/09/21/2025.09.21.677619.full.pdf"
)
HF_URL = "https://huggingface.co/api/collections/songlab/gpn-star-68c0c055acc2ee51d5c4f129"

REVIEWER_NOTE = (
    "Claude review agent (independent of the extractor); no human review claimed. "
    "Values were checked against the pinned artifacts; nothing was reproduced and no "
    "value was recomputed."
)

METHOD_NOTE = (
    "Independent review pass of 2026-11-16. All four pinned artifacts were re-retrieved. "
    "The Nature article PDF, the Supplementary Information PDF and the Hugging Face "
    "collection API JSON each hashed to the value on their source record. The bioRxiv "
    "PDF did not and cannot: two downloads minutes apart gave "
    "b3e4d729d3363c16fb6b6cb99e4e18ffadb01b48614dba910480fb96f42b3d73 and "
    "47f87f72baf93793177d3e40f70f43f03ac5d3050bbc5244f655e92041c7db4a, differing from "
    "each other in 34 bytes, all of them download-time stamps (XMP ModifyDate and "
    "MetadataDate, the xmpMM DocumentID and InstanceID, the document /ModDate and the "
    "second element of the trailer /ID); the page count, the CreationDate of "
    "2025-09-21 and the pdftotext -layout text layer are identical across downloads. "
    "No value in this batch comes from the preprint. "
    "npm run batch -- check-values reproduced the extractor's figures exactly: 12 "
    "in_cell, 44 in_row, 16 locator_not_parsed, no not_in_row, no wrong_column and no "
    "overclaimed_in_row (value-check.tsv). All 72 results were then re-read by "
    "review/check_values_independent.py, written for this pass and importing nothing "
    "from extract/build.py. Supplementary Table 3 is printed rotated, so that script "
    "reads the page's word bounding boxes rather than a text dump: it recovers the "
    "seven column bands from the header words' y extents, pairing each 'Finemapped' "
    "header with whichever of 'coding' and 'non-coding' overlaps it, clusters the body "
    "words into eight row bands by x centre, and places every numeric token in the cell "
    "whose column centre is nearest, rejecting any token that is more than 45 per cent "
    "of a column pitch from its nearest column or less than 25 per cent of a pitch "
    "clear of the runner-up. Column order is therefore a measured property of the page "
    "and not an assumption, which is the check extract/build.py could not make: it "
    "asserted the column order positionally. Results are matched to cells through each "
    "source_locator's text, not through record IDs. Fig. 4b's 12 bar labels were "
    "required to be the first number printed after their series label on the same line, "
    "and the four rare variant counts were matched against the two sentences that print "
    "them, with the capture position fixing which count belongs to DeepRVAT with "
    "GPN-Star annotations and which to the original method. Result: 68 in cell, 4 in "
    "sentence, 0 failures (review/value-check-independent.tsv). Two negative controls "
    "confirm the checker is a cell check and not a row check: exchanging two ClinVar "
    "values between rows and moving a Fig. 4b label onto another series both fail "
    "(review/control-swap.tsv), and shifting a value into a neighbouring column of its "
    "own row fails and names the column that actually holds it, including across the "
    "Finemapped coding / OMIM and Finemapped coding / Finemapped non-coding boundaries "
    "(review/control-shift.tsv). Independently of both scripts, all 56 cells of "
    "Supplementary Table 3 and all 12 Fig. 4b labels were transcribed by hand from the "
    "pages rendered at 190 dpi with pdftoppm, into review/manual-transcription.tsv, and "
    "compared by review/cmp_manual.py: 68 values, 0 problems. That hand pass is what "
    "settles the column assignment the repository checker could only place at row "
    "level. The 12 descriptive claims were read against the pinned PDFs and the "
    "collection JSON."
)

RESULT_METHODS = [
    "independent-cell-check",
    "deterministic-table-parse",
    "pdf-text-parse",
    "rendered-source-visual-check",
    "source-hash-verification",
]
TEXT_METHODS = ["transcription", "pdf-text-parse", "source-hash-verification"]
HASH_METHODS = ["source-hash-verification"]

SOURCE_ART = {
    "gpn-star-20261116-source-nature-2026": (ART_SHA, ART_URL),
    "gpn-star-20261116-source-nature-si": (SI_SHA, SI_URL),
    "gpn-star-20261116-source-biorxiv-v1": (BIORXIV_SHA, BIORXIV_URL),
    "gpn-star-20261116-source-hf-collection": (HF_SHA, HF_URL),
}

SOURCE_NOTES = {
    "gpn-star-20261116-source-nature-2026":
        "Re-downloaded 2026-11-16 and matched the pinned hash byte for byte. Confirmed "
        "to be the version of record: the running footer reads 'Nature | Vol 659 | 5 "
        "November 2026' on every article page and the pagination is 141-150, with no "
        "accelerated article preview banner.",
    "gpn-star-20261116-source-nature-si":
        "Re-downloaded 2026-11-16 and matched the pinned hash byte for byte. 57 pages; "
        "Supplementary Table 3 is on PDF page 23 as the locators say.",
    "gpn-star-20261116-source-biorxiv-v1":
        "Re-downloaded twice on 2026-11-16. Neither download reproduced the pinned hash "
        "or matched the other, because bioRxiv restamps the PDF container on every "
        "request; the 34 differing bytes are all download-time metadata and the text "
        "layer is identical. The pinned hash is kept, as the review skill requires, and "
        "hash_scope now says what it describes. No value in this batch comes from this "
        "source.",
    "gpn-star-20261116-source-hf-collection":
        "Re-retrieved 2026-11-16 and matched the pinned hash. The collection is mutable "
        "and carries no revision, so the match is a statement about this retrieval, not "
        "a guarantee. The response lists 32 items, 8 of them models, whose repository "
        "ids are exactly those in gpn-star-20261116-claim-released-checkpoints.",
}

# Records whose values were read from the Supplementary Information rather than
# the article.
def artifact_for(record):
    ids = record.get("source_ids") or []
    if record["kind"] == "source":
        return SOURCE_ART[record["id"]]
    loc = str(record.get("attributes", {}).get("source_locator") or "")
    if "gpn-star-20261116-source-nature-si" in ids and (
        "Supplementary" in loc or "gpn-star-20261116-source-nature-2026" not in ids
    ):
        return SI_SHA, SI_URL
    if "gpn-star-20261116-source-hf-collection" in ids and len(ids) == 1:
        return HF_SHA, HF_URL
    return ART_SHA, ART_URL


KIND_NOTES = {
    "result": "Re-read independently of extract/build.py; see method_note for the three "
              "passes and the two negative controls.",
    "evaluation": "The system, assessment and data links and the comparison fields were "
                  "checked against the source text the locator names; every null "
                  "comparison field was confirmed unstated there.",
    "protocol": "The split, scored set and metric were checked against the Supplementary "
                "Information's Evaluation Benchmarks section and the table or figure "
                "caption the locator names.",
    "configuration": "Identity, version and access were checked against the figure or "
                     "table row and the Compared models list; no checkpoint was assigned "
                     "that the source does not name.",
    "dataset": "Construction, controls and release were checked against the Evaluation "
               "Benchmarks bullet the locator names.",
    "benchmark": "Scope checked against the paper's own benchmark list.",
    "method": "Checked against the Results paragraph and Methods the locator names.",
    "claim": "Read against the pinned artifact at the locator given; every quoted number "
             "was located in the source text.",
    "source": None,
}


def review_for(record):
    sha, url = artifact_for(record)
    kind = record["kind"]
    obj = {
        "artifact_sha256": sha,
        "date": DATE,
        "method": HASH_METHODS if kind == "source"
        else RESULT_METHODS if kind == "result"
        else TEXT_METHODS,
        "method_note": METHOD_NOTE,
        "note": SOURCE_NOTES[record["id"]] if kind == "source" else KIND_NOTES[kind],
        "retrieval_url": url,
        "reviewed_at": REVIEWED_AT,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
    }
    return obj


FIG3E_LIMITATION = (
    "Figs. 2 and 3, Fig. 4a,c,d, Fig. 5b-d and Extended Data Figs. 1-10 print no "
    "performance values for the compared models. One statistic is printed inside a "
    "panel and was missed at extraction: Fig. 3e prints 'r = 0.47, P = 0.0072' for the "
    "Pearson correlation between log effective polygenicity and the difference in "
    "heritability enrichment between GPN-Star (P) and (M) across 27 traits, restated in "
    "the Supplementary Notes. It characterises the model rather than scoring it against "
    "a ground truth and is not extracted as a result; the Supplementary Notes also give "
    "a range, Spearman's rho 0.31-0.34, for the raw scores against Roulette mutation "
    "rate estimates on chromosome 22. Fig. 4b and Fig. 5a carry printed value labels; "
    "only Fig. 4b is extracted here, because Fig. 5a's labels can be assigned to a "
    "species and a score only by grouping them by position and taking the bar order "
    "from the legend."
)

STALE_PIN_LIMITATION = (
    "The store already holds vep-uc-20261014-source-gpn-star for the same article URL, "
    "pinned on 2026-10-14 to the accelerated article preview PDF "
    "(97f61ec05d4ace41692549290db3faf019ce869459459d2c5694bf54e16d0996). That URL now "
    "serves this final version of record, whose bytes differ. Checked at review: the "
    "Internet Archive's capture of the article page on 2026-10-21 carries "
    "citation_firstpage 1 and citation_lastpage 10 with no volume, which is the preview "
    "state, while this PDF is paginated 141-150 in volume 659; the stored hash is "
    "therefore a correct pin of a different artifact and nothing stored is wrong. The "
    "two records are linked with companion_of from the preview to this version of "
    "record, placed on the stored record by npm run records -- change, rather than with "
    "supersedes."
)

BIORXIV_HASH_SCOPE = (
    "SHA-256 of one download. bioRxiv restamps the PDF container on every request, so "
    "no refetch reproduces it: two downloads on 2026-11-16 gave "
    "b3e4d729d3363c16fb6b6cb99e4e18ffadb01b48614dba910480fb96f42b3d73 and "
    "47f87f72baf93793177d3e40f70f43f03ac5d3050bbc5244f655e92041c7db4a. The 34 bytes "
    "that differ are the XMP ModifyDate and MetadataDate, the xmpMM DocumentID and "
    "InstanceID, the document /ModDate and the second element of the trailer /ID. The "
    "68 pages, the CreationDate of 2025-09-21 and the pdftotext -layout text layer are "
    "identical across downloads, so the article is stable even though the container is "
    "not."
)

PHASTCONS_P_NOTE = (
    "The Supplementary Information gives the download URL for PhastCons (P) as "
    "phyloPPrimates.bigWig, which names phyloP rather than phastCons. Its own footnote "
    "says 'The track name is misleading, but the documentation confirms it is indeed "
    "PhastCons', so this is the track the authors intended and not a source error. The "
    "same bullet says 43 primates, where PhyloP (P) is given as 243."
)

PRINTED_VALUES_TAIL = (
    " One statistic inside a panel is an exception to this and was missed at "
    "extraction: Fig. 3e prints r = 0.47 and P = 0.0072 for the correlation between "
    "trait polygenicity and the enrichment difference between GPN-Star (P) and (M). It "
    "is a property of the models' relationship to each other rather than a score against "
    "a ground truth, so no result is recorded for it."
)


def main():
    records = [json.loads(l) for l in open(BATCH, encoding="utf-8")]
    by_id = {r["id"]: r for r in records}
    changes = []

    nature = by_id["gpn-star-20261116-source-nature-2026"]
    before = len(nature["links"])
    nature["links"] = [
        l for l in nature["links"]
        if not (l["relation"] == "supersedes"
                and l["target_id"] == "vep-uc-20261014-source-gpn-star")
    ]
    assert len(nature["links"]) == before - 1
    changes.append("dropped the supersedes link on the Nature source record")
    lims = nature["attributes"]["limitations"]
    assert len(lims) == 2 and lims[0].startswith("Figs. 2 and 3")
    lims[0] = FIG3E_LIMITATION
    lims[1] = STALE_PIN_LIMITATION
    changes.append("rewrote both limitations on the Nature source record")

    bio = by_id["gpn-star-20261116-source-biorxiv-v1"]
    assert "hash_scope" not in bio["attributes"]
    bio["attributes"]["hash_scope"] = BIORXIV_HASH_SCOPE
    changes.append("added hash_scope to the bioRxiv source record")

    pc = by_id["gpn-star-20261116-config-fig4b-phastcons-p"]
    assert "model_identity_note" not in pc["attributes"]
    pc["attributes"]["model_identity_note"] = PHASTCONS_P_NOTE
    changes.append("recorded the misleading PhastCons (P) track name and its footnote")

    scope = by_id["gpn-star-20261116-claim-printed-values-scope"]
    assert "Fig. 3e" not in scope["attributes"]["value"]
    scope["attributes"]["value"] += PRINTED_VALUES_TAIL
    changes.append("recorded Fig. 3e's printed statistic on the printed-values claim")

    for r in records:
        r["attributes"]["review"] = review_for(r)

    with open(BATCH, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"{len(records)} records rewritten with the review object")
    for c in changes:
        print("  " + c)


if __name__ == "__main__":
    main()
