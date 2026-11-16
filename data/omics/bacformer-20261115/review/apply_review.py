"""Apply the independent review's rulings to batch.jsonl.

Three kinds of edit:

1. Unit correction. The extractor recorded `unit` as `percent` for the 168 results printed on a
   0 to 100 scale. data/vocab/unit.ttl says the opposite in the scope note of `unitless`: "A
   unitless statistic printed x100 (MCC, R2, Spearman, AUC) stays unitless with unit_detail
   'printed x100'; percent would imply a proportion." The stored catalogue agrees, 4403 AUROC
   results unitless against 9 percent. The printed values, the numeric values and the spreads are
   untouched; only the unit concept and its detail change.

2. Version-differences correction. The claim, the version 2 source description and the version 3
   source limitation all said version 2 "prints different values for the same analyses". Both
   figures given as examples are in fact identical in the two versions, read from renders of
   version 2 pages 5 and 8. The assertion is replaced by what the sources support.

3. Review. Every record that can carry a `review` object gets the reviewer's own, replacing the
   extractor's, and every record moves to `source_checked`. Tasks cannot carry a review object
   (the attribute registry does not declare one for that kind), so they only change status.

Usage: python3 -I apply_review.py <batch.jsonl>
"""

import json
import sys

DATE = "2026-11-15"
REVIEWED_AT = "2026-11-15T23:55:00Z"
REVIEWER = ["claude"]
REVIEWER_NOTE = (
    "Claude (Opus 5) review agent, independent of the agent that extracted this batch; no human "
    "review claimed. Transcription was checked against the pinned sources. Nothing was reproduced "
    "and no value was recomputed."
)

TEXT_LAYER = "86636e89b167d7304b3a83ee7f159cad0a9bdbe97019588ce836087b8fe3b0b2"
PREPRINT_URL = "https://www.biorxiv.org/content/10.1101/2025.07.20.665723v3.full.pdf"

# Hash and retrieval URL of the artifact each source was checked against. For the version 3
# preprint this is the text layer, not the PDF: the container bytes differ on every download.
CHECKED = {
    "bacformer-20261115-source-preprint-v3": (TEXT_LAYER, PREPRINT_URL),
    "bacformer-20261115-source-preprint-v2": (
        "c10e034f5f5ca414fa5d958e9f71c5d0170e1d61d671643b49185094e853e564",
        "https://www.biorxiv.org/content/biorxiv/early/2025/08/13/2025.07.20.665723.full.pdf"),
    "bacformer-20261115-source-bacformer-readme": (
        "6e4fdabbd05c93ff63b0eb583ce6a9309eaa13998087cc32ddeaa6928025b235",
        "https://raw.githubusercontent.com/macwiatrak/Bacformer/"
        "61dca9537429b95365d73d72a3e11c207df1ed6c/README.md"),
    "bacformer-20261115-source-bacbench-readme": (
        "c9d28efef5b4cc30adbcc9de224c350100f5aa2a15a025beaf10dcdeb86cd93e",
        "https://raw.githubusercontent.com/macwiatrak/BacBench/"
        "64b7d45823b2ff2ef88458e3aa235caa461a12aa/README.md"),
    "bacformer-20261115-source-bacformer-licence": (
        "d7fe40bfc2a639daa18e4caf57fab7545ece94bd38fb181c1f5b780d3b8cfa01",
        "https://raw.githubusercontent.com/macwiatrak/Bacformer/"
        "61dca9537429b95365d73d72a3e11c207df1ed6c/LICENSE"),
    "bacformer-20261115-source-bacbench-licence": (
        "d7fe40bfc2a639daa18e4caf57fab7545ece94bd38fb181c1f5b780d3b8cfa01",
        "https://raw.githubusercontent.com/macwiatrak/BacBench/"
        "64b7d45823b2ff2ef88458e3aa235caa461a12aa/LICENSE"),
    "bacformer-20261115-source-hf-card-bacformer-masked-mag": (
        "d735d1b2c8caa57a9f6abf990a457b2aa084f626070e555d6c01ca4a46b6bf7c",
        "https://huggingface.co/macwiatrak/bacformer-masked-MAG/raw/"
        "340a08cf5d5cd7d9f1ffac9075cde733d108a82b/README.md"),
    "bacformer-20261115-source-hf-card-bacformer-masked-complete-genomes": (
        "02575bd9d4ae949e3c38a5a5890767b862c75bc2a20e84afa4a517bd2f067ff1",
        "https://huggingface.co/macwiatrak/bacformer-masked-complete-genomes/raw/"
        "d1c461f1db75902e6502e5ba7588ea1a4ea96b29/README.md"),
    "bacformer-20261115-source-hf-card-bacformer-large-masked-mag": (
        "3809ffe59057788ba942d697a085edcd8458edbf815a116018e38e721d1e788d",
        "https://huggingface.co/macwiatrak/bacformer-large-masked-MAG/raw/"
        "cb92cdf04e1b32993a19fdd9cf6f8f49efde2665/README.md"),
    "bacformer-20261115-source-hf-card-bacformer-large-masked-complete-genomes": (
        "19142e40c2aa69f1b3125fb7594cc8c6ea9f775e1878645583df21952c175596",
        "https://huggingface.co/macwiatrak/bacformer-large-masked-complete-genomes/raw/"
        "84f85c37a05e55559142b842c1569e265183b554/README.md"),
    "bacformer-20261115-source-hf-card-bacformer-causal-mag": (
        "a054cf81eb8ca4abac0ffd2063358fc97cc38ebcd7b7e945ff2cb026d7cde12c",
        "https://huggingface.co/macwiatrak/bacformer-causal-MAG/raw/"
        "e4c8d6dc4decaa88729ce3853b1f329fee3b4960/README.md"),
    "bacformer-20261115-source-hf-card-bacformer-causal-complete-genomes": (
        "048353f8367af281dd2a9d13404d9f4a257247bb308be3bfb578315e56c8047d",
        "https://huggingface.co/macwiatrak/bacformer-causal-complete-genomes/raw/"
        "6d2af6ac98f5aaf420ab33b475b891c8398e3bb9/README.md"),
    "bacformer-20261115-source-hf-card-bacformer-for-ppi-prediction": (
        "0336368f8274a5ed09f54cee8d56a851ecee96026d9f391a6735762c16608a60",
        "https://huggingface.co/macwiatrak/bacformer-for-ppi-prediction/raw/"
        "553108a6a1190d45fabea32e64b0ddf8755e6e0e/README.md"),
}

CELL_METHOD = ["independent-cell-check", "deterministic-table-parse", "pdf-text-parse",
               "source-hash-verification", "ai-assisted-source-review"]
TEXT_METHOD = ["transcription", "source-hash-verification", "ai-assisted-source-review"]

CELL_NOTE = (
    "Independent review pass. Every cell of the six benchmark tables was re-read by "
    "review/recheck_cells.py, written for this pass, which uses neither of the extractor's scripts "
    "and does not read the pdftotext -layout text layer they read. It takes the word bounding "
    "boxes pdftotext -bbox-layout emits for a freshly downloaded version 3 PDF, groups words into "
    "printed lines by their y coordinate, derives each table's column boundaries from the x extent "
    "of that table's own printed header words, and assigns every number to a column by where it "
    "sits on the page, so a value printed under one header cannot be read as a value of another. "
    "It asserts the printed row order, that every column of every row is filled, that each cell "
    "holds exactly a mean and a spread, that each cell prints its own plus-minus sign, and for "
    "Tables S13 and S18 that the group header sits geometrically over the two columns this review "
    "names after it. All 186 cells agreed on the printed value, the mean, the spread, the spread's "
    "printed string and its source column, with no disagreement, and the six tables print no cell "
    "the batch leaves unrecorded. Three negative controls (two cells of one row exchanged, one "
    "cell taking its neighbour's value, every Table S18 locator moved one column right) were all "
    "rejected, and the unmutated batch accepted; the log is review/negative-controls.txt. "
    "npm run batch -- check-values reproduced the extractor's figures exactly, 36 in_cell and 150 "
    "in_row with nothing else, against a text layer regenerated from a fresh download. A manual "
    "sample of 47 cells was then read by eye against the printed table bodies: 24 drawn with "
    "random.sample over all 186 at seed 20261115, all 18 cells of Table S12, and the eight Evo and "
    "Evo-2 cells of Tables S1 and S14, where the printed row order differs from the other tables. "
    "All matched, column assignment included."
)

UNIT_NOTE = (
    " The unit concept was changed from percent to unitless in this review, with unit_detail "
    "'printed x100'. data/vocab/unit.ttl says so in the scope note of unitless, and percent would "
    "assert that an AUROC, an R squared or a Pearson correlation is a proportion of items. The "
    "printed value, the numeric value and the spread are unchanged."
)

TABLE_NOTE = {
    "S1": "Operon identification, Table S1. The spread's scope is the Methods' own statement that "
          "performance is reported averaged across all five sequenced strains, so n = 5 is the "
          "source's figure and not an inference.",
    "S12": "Species-level genome clustering, Table S12. The bootstrap method and the 10 resamples "
           "over 80% of the data are the caption's own words. Printed on a 0 to 1 scale, so the "
           "unit stays unitless with no scale detail.",
    "S13": "Protein-protein interaction, Table S13. The zero-shot and finetuned column group was "
           "checked geometrically against the printed group header, not inferred from column "
           "order.",
    "S14": "Gene essentiality, Table S14. The caption prints a median, not a mean, and the "
           "metric qualifier says so.",
    "S16": "Phenotypic traits, Table S16. The caption says the spread is across 5 seeds while the "
           "Methods say the split was repeated across three independent runs. The source does not "
           "reconcile them, so the result carries the conflict as a warning, the uncertainty "
           "states both readings and no replicate count is asserted.",
    "S18": "Antibiotic resistance, Table S18. The denominators are the Methods' own counts, 37 "
           "antibiotics in the binary setting and 56 in the regression setting; Table S17 prints "
           "37 drug rows for the binary setting. The caption's wording 'Performance (percent, "
           "higher is better)' describes the printed scale and does not make these metrics "
           "proportions.",
}

# Extra observations this review adds to particular records.
EXTRA = {
    "bacformer-20261115-claim-bacformer-parameters-preprint-s9-27m":
        " Checked and left as printed. The two preprint figures look like two roundings of one "
        "number: Hugging Face serves a weight total of 50,852,241 for every base checkpoint, and "
        "the config at the pinned revision gives a protein-family head over 50,000 clusters at "
        "480 dimensions, so the head alone is 24,000,000 and the trunk is about 26.85M, which "
        "rounds to 27M and truncates to 26M. That is repository metadata and arithmetic, not a "
        "printed statement, so no record rests on it.",
    "bacformer-20261115-claim-bacformer-parameters-preprint-s11-26m":
        " Checked and left as printed. See the note on the Table S9 claim: the base model's two "
        "printed figures are consistent with one trunk of about 26.85M.",
    "bacformer-20261115-claim-bacformer-parameters-card-27m":
        " Checked and left as printed. The two Bacformer Large cards describe the base model as "
        "'Bacformer base (26M)' in their key-changes list and in a code comment, so 26M appears on "
        "those cards too; the four base cards print 27M in their prose, which is what this claim "
        "records.",
    "bacformer-20261115-claim-bacformer-large-parameters-preprint-332m":
        " Checked and left as printed. The coincidence with the ESM-C row of the same table does "
        "not by itself make it a copy: 30 layers at 960 dimensions with a four-fold feed-forward "
        "give 30 x 12 x 960 x 960 = 331,776,000, and the pinned config gives 30 layers and 960 "
        "dimensions, so 332M is consistent with the trunk size. Hugging Face serves a weight total "
        "of 431,765,841 for both large checkpoints, which neither 300M nor 332M accounts for once "
        "the 50,001-cluster head is subtracted. Repository metadata, so no record rests on it.",
    "bacformer-20261115-claim-bacformer-large-parameters-bacbench-27m":
        " Checked and left as printed, with no evidence concern. The BacBench Params column "
        "disagrees with the preprint for other models too (ProkBERT 27M against 26M, Nucleotide "
        "Transformer 250M against 235M, ProtBert 420M against 412M), so it reads as nominal model "
        "sizes rather than measured counts, and the Bacformer Large row repeats the Bacformer "
        "row's 27M while changing the dimension to 960. Nothing in the batch rests on this figure: "
        "it is recorded as one printed statement among nine, and a concern scoped to it would "
        "withhold the record of the disagreement itself.",
    "bacformer-20261115-claim-preprint-version-differences":
        " Corrected by this review. The claim asserted that version 2 prints different values for "
        "the same analyses and gave two examples. Both examples are identical in the two versions: "
        "version 2 page 5 prints 'almost 95% balanced accuracy across diverse genera' and page 8 "
        "prints '0.81 +/- 0.07 median AUROC across diverse genomes', the same as version 3. They "
        "were read from renders of those two pages at 200 dpi, because version 2's text layer "
        "mis-encodes digits: the rendered '0.81 +/- 0.07' appears in the text layer as "
        "'+.)! +/- +.+(' and the rendered '95%' as '*'%'. That confirms the extractor's warning "
        "about the text layer and refutes the conclusion drawn from it. What the sources do "
        "support is kept: version 2 nowhere mentions Bacformer Large, zero occurrences of "
        "'Bacformer Large' or 'Bacformer-L' in its text layer, where letters render correctly.",
    "bacformer-20261115-claim-strain-clustering-selection":
        " Checked and left as a claim and a protocol limitation, with no evidence concern. The "
        "selection applies identically to all six systems in Table S12, so it biases the level of "
        "every value and not their comparison with each other; it is a property of the protocol, "
        "which records it, rather than a defect that should withhold the table.",
    "bacformer-20261115-claim-phenotypic-seed-conflict":
        " Checked and left as a claim and a result-level warning, with no evidence concern. The "
        "conflict is about what the spread is taken over, not about the means, and the Methods' "
        "'three independent runs with different data splits' and the caption's '5 seeds' may not "
        "even denote the same quantity. A concern scoped to the two phenotypic-trait protocols "
        "would withhold all 24 Table S16 results from comparison over an unresolved footnote.",
}


EVAL_NOTE = (
    "Evaluation of one configuration on one protocol, carrying the single printed cell of its "
    "result. Its system, assessment and data links, its origin and its comparison fields were "
    "checked against the source alongside that cell."
)


def review_for(record, table_of_eval=None):
    kind = record["kind"]
    attrs = record["attributes"]
    sources = record.get("source_ids") or []
    primary = sources[0] if sources else None
    if kind == "source":
        primary = record["id"]
    sha, url = CHECKED.get(primary, (None, None))

    if kind in ("result", "evaluation"):
        table = attrs.get("source_table") or table_of_eval or ""
        note = TABLE_NOTE.get(table, "")
        if kind == "evaluation":
            note = (EVAL_NOTE + " " + note).strip()
        elif attrs.get("unit") == "unitless" and table != "S12":
            note += UNIT_NOTE
        return {
            "artifact_sha256": TEXT_LAYER,
            "date": DATE,
            "method": CELL_METHOD,
            "method_note": CELL_NOTE,
            "note": note.strip(),
            "retrieval_url": PREPRINT_URL,
            "reviewed_at": REVIEWED_AT,
            "reviewer": REVIEWER,
            "reviewer_note": REVIEWER_NOTE,
        }

    method = list(TEXT_METHOD)
    if primary in ("bacformer-20261115-source-preprint-v3",
                   "bacformer-20261115-source-preprint-v2"):
        method = ["transcription", "pdf-text-parse", "source-hash-verification",
                  "ai-assisted-source-review"]
    note = ("Statement re-read against the pinned artifact by a reviewer who did not extract this "
            "batch. Every artifact except the two preprint PDFs was downloaded again at review "
            "time and hashed to exactly the value its source record records, and is byte-identical "
            "to the copy kept in artifacts/.")
    if primary == "bacformer-20261115-source-preprint-v3":
        note = ("Statement re-read against the version 3 preprint. The PDF's container bytes "
                "differ on every download, so the artifact checked is its pdftotext -layout text "
                "layer, which two fresh downloads reproduce byte for byte and which the archived "
                "copy in artifacts/ decompresses to.")
    note += EXTRA.get(record["id"], "")
    return {
        "artifact_sha256": sha or TEXT_LAYER,
        "date": DATE,
        "method": method,
        "method_note": (
            "Independent review pass. Each source artifact was retrieved again at review time and "
            "its SHA-256 compared with the source record; the quoted statement was then read at "
            "the recorded locator and compared with the recorded value. Access states were "
            "rechecked rather than taken from notes.md."),
        "note": note.strip(),
        "retrieval_url": url or PREPRINT_URL,
        "reviewed_at": REVIEWED_AT,
        "reviewer": REVIEWER,
        "reviewer_note": REVIEWER_NOTE,
    }


OLD = "prints different values for the same analyses"


def main(argv):
    path = argv[0]
    records = [json.loads(l) for l in open(path) if l.strip()]
    counts = {"unit": 0, "review": 0, "status": 0, "version": 0}
    # An evaluation names no table of its own; take it from the result that cites it.
    table_of_eval = {}
    for r in records:
        if r["kind"] == "result":
            for link in r.get("links", []):
                if link["relation"] == "evaluation":
                    table_of_eval[link["target_id"]] = r["attributes"].get("source_table")

    for r in records:
        a = r.setdefault("attributes", {})

        if r["kind"] == "result" and a.get("unit") == "percent":
            a["unit"] = "unitless"
            a["unit_detail"] = "printed x100"
            if isinstance(a.get("uncertainty"), dict) and a["uncertainty"].get("unit") == "percent":
                a["uncertainty"]["unit"] = "unitless"
            counts["unit"] += 1

        if r["id"] == "bacformer-20261115-claim-preprint-version-differences":
            a["value"] = (
                "Version 3 (posted 17 August 2026) reports Bacformer Large, which version 2 "
                "(posted 13 August 2025) does not mention anywhere; the two versions are separate "
                "reports of the same study and their numbers must not be pooled. Where the two "
                "were compared, on the genus-level nearest-neighbour retrieval figure of almost "
                "95% balanced accuracy and the 0.81 plus or minus 0.07 median essentiality AUROC, "
                "both versions print the same figures")
            a["limitations"] = [
                "No systematic numeric comparison of version 2 against version 3 was made. "
                "Version 2's text layer mis-encodes digits, so only two of its pages were "
                "rendered and read; other figures may or may not differ.",
                "No value in this batch comes from version 2.",
            ]
            counts["version"] += 1
        if r["id"] == "bacformer-20261115-source-preprint-v2":
            r["description"] = ("The August 2025 version of the Bacformer preprint, which reports "
                                "the study before Bacformer Large was added.")
            a["review_artifact"] = ("Refetched PDF, SHA-256 "
                                    "af77c2be437b151b5e464f2f5078f6b97b95a29c2913affefc566337eecfbad4")
            a["review_artifact_matches_original_artifact_sha256"] = False
            counts["version"] += 1
        if r["id"] == "bacformer-20261115-source-preprint-v3":
            a["limitations"] = [
                "Preprint; not certified by peer review.",
                "Version 2 (posted 13 August 2025) does not include Bacformer Large; no value in "
                "this batch comes from it.",
                "The tables carry no per-cell counts for some aggregations, so several "
                "denominators stay unreported.",
                "bioRxiv regenerates this PDF on request, so its artifact_sha256 is one "
                "download's hash and no refetch reproduces it. The stable identity is the "
                "pdftotext -layout text layer, SHA-256 " + TEXT_LAYER + ".",
            ]
            a["review_artifact"] = ("artifacts/biorxiv-665723v3-text-layer.txt.gz, whose contents "
                                    "hash to " + TEXT_LAYER)
            a["review_artifact_matches_original_artifact_sha256"] = False
            counts["version"] += 1

        if r["kind"] != "task":
            a["review"] = review_for(r, table_of_eval.get(r["id"]))
            counts["review"] += 1
        if r["status"] != "source_checked":
            r["status"] = "source_checked"
            counts["status"] += 1

    records.sort(key=lambda r: r["id"])
    with open(path, "w") as fh:
        for r in records:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    print(json.dumps(counts, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
