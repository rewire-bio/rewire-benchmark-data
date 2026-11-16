"""Apply the independent review to data/omics/bioemu2-20261115/batch.jsonl.

build.py writes the extraction state of the batch (SHA-256
4e40c0c17e77b781c00b90eb27d48e25dd24aff077f650901762a3c63e4bf516). This script turns that
into the reviewed state: it corrects five source locators the review found pointing at the
wrong sentence, paragraph or section heading, and replaces every record's `review` object with
the review pass's own method, reviewer and date. The extractor's transcription note is kept
under "Extraction:" inside `note`, with the review's own observation appended where it has one.

Running it twice is safe: the locator fixes are keyed on the text they replace and are skipped
once applied, and the review objects are written absolutely.

Run from the repository root:
    python3 -I data/omics/bioemu2-20261115/review/apply-review.py
"""

import json
import pathlib

BATCH = pathlib.Path(__file__).resolve().parent.parent
BATCH_FILE = BATCH / "batch.jsonl"
PREFIX = "bioemu2-20261115-"
DATE = "2026-11-15"
REVIEWED_AT = "2026-11-15T23:40:00Z"
REVIEWER = ["claude"]
REVIEWER_NOTE = (
    "Claude review agent (independent of the extractor); no human review claimed. Transcription "
    "was checked against the pinned bytes. Nothing was reproduced, no model was run and no value "
    "was recomputed."
)

HASHES = (
    "Review: all thirteen artifacts were re-retrieved from their recorded URLs on 2026-11-15 and "
    "every SHA-256 matched its source record, and each archived gzip under artifacts/ "
    "decompresses to those same bytes."
)

TABLE_NOTE = (
    HASHES + " The reviewer parsed the model card's two printed tables again from the "
    "re-retrieved file, without using extract/parse_model_card.py, and compared all nine model "
    "summary rows and all twelve training data rows cell by cell with the claims: no "
    "disagreement. The en dash in the training dates cell and the markdown links in the related "
    "assets cell are the only places where the claim respells the cell."
)
TEXT_NOTE = (
    HASHES + " The claim was then read at the location its source_locator names in the "
    "re-retrieved bytes. Claims that quote the source were also matched mechanically against the "
    "normalised artifact text; claims that reflow a table cell, join two sentences or strip "
    "markdown were read by eye at the locator and their wording checked against it."
)
SOURCE_NOTE = (
    HASHES + " The Hugging Face API listing is the one mutable artifact: its counters happened to "
    "be unchanged at review time, so its bytes still matched, which is not expected to hold later."
)
RECORD_NOTE = (
    HASHES + " Every attribute of this record was read against the artifact and locator it names, "
    "and every missing_metadata reason was checked to be genuinely unstated in the pinned sources. "
    "No pinned artifact prints a numeric evaluation value, which the review confirmed "
    "independently by reading all thirteen, so the batch correctly holds no evaluation or result."
)

# Locators the review found pointing at the wrong sentence, paragraph or section.
LOCATOR_FIXES = {
    "claim-tested-gpus-readme": (
        "System requirements, third sentence",
        "System requirements, fourth sentence",
    ),
    "claim-propagation-lag-range": (
        "Opening paragraphs, third paragraph",
        "Opening paragraphs, second paragraph",
    ),
    "claim-outputs-are-hypotheses": (
        "Usage: Out-of-scope use cases, paragraph after the list; Technical requirements and "
        "integration guidance, second sentence",
        "Usage: Out-of-scope use cases, paragraph after the list; Technical requirements and "
        "integration guidance, second paragraph, second sentence",
    ),
    "claim-notices-other-third-party": (
        "NOTICES.md, PyTorch3D, torch_scatter, NVIDIA Fold-CP, OpenMM and geostd sections",
        "NOTICES.md, PyTorch3D rotation helpers, torch_scatter-derived code, NVIDIA "
        "Fold-CP-derived code and OpenMM patches sections; Stereochemistry reference data "
        "section for the geostd nucleotide link parameters and notice",
    ),
    "claim-usage-recommendation": (
        "Usage: Out-of-scope use cases, closing paragraphs",
        "Usage: Out-of-scope use cases, the paragraph beginning BioEmu-2 is released for "
        "research purposes",
    ),
}

# What the review has to add to a record's note, beyond the extractor's own.
REVIEW_ADDENDA = {
    "claim-tested-gpus-readme":
        "The locator said the third sentence of the section; the sentence quoted is the fourth, "
        "and the review corrected it.",
    "claim-propagation-lag-range":
        "The locator said the third of the opening paragraphs; there are two, and the text is in "
        "the second, which the review corrected.",
    "claim-outputs-are-hypotheses":
        "The locator said the second sentence of the technical requirements section, which is "
        "the one about the repository README; the quoted sentence is the second of that section's "
        "second paragraph, and the review corrected the locator. The model card writes that "
        "sentence as 'computational hypotheses rather than experimentally validated measurements "
        "and should be assessed'; the value drops 'rather than experimentally validated "
        "measurements', which the claim's first sentence already states.",
    "claim-notices-other-third-party":
        "NOTICES.md has no geostd heading: the geostd nucleotide link parameters and the "
        "Lawrence Berkeley National Laboratory notice are in the Stereochemistry reference data "
        "section, and the review rewrote the locator to the headings the file prints.",
    "claim-usage-recommendation":
        "The locator said the closing paragraphs; the value is the one paragraph beginning "
        "'BioEmu-2 is released for research purposes', and the review narrowed the locator to it. "
        "The section's final paragraph, about weighing the limitations per use case, is not part "
        "of this claim.",
    "claim-notices-lgpl-components":
        "'Two distributed files are not under MIT' is the extractor's summary of the two notice "
        "sections. NOTICES.md scopes the LGPL-3.0 to the monlib section of stereo_chemistry.yaml, "
        "not to the whole file, which the value states, and licenses mdtraj_patcher.py itself "
        "under LGPL-3.0 or later.",
    "claim-model-card-publication":
        "The review repeated the byte comparison: the Hugging Face README is the repository "
        "MODEL_CARD.md preceded by a four-line YAML front matter block setting license: mit, and "
        "nothing else differs.",
    "claim-checkpoint-digest":
        "The Hugging Face API listing for the same revision publishes the same digest and size "
        "in siblings[].lfs, so two pinned publisher artifacts agree on them. The checkpoint bytes "
        "were still not downloaded, so the digest remains the publisher's.",
    "claim-largest-systems-embedded":
        "These are token capacities on named hardware, not an evaluation metric; the throughput "
        "figures in the same section are linked images with no printed numbers.",
    "claim-evaluation-folding":
        "The Boltz-1 test set is named without a version, split or target count, no baseline is "
        "named, and no value is printed, so the review created no protocol and linked no dataset.",
    "config-checkpoint-bioemu2-preview":
        "checkpoint_sha256 holds the digest published in the Git LFS pointer, which the Hugging "
        "Face API listing for the same revision repeats in siblings[].lfs.sha256. The review "
        "accepted it, with weights_sha256 left unextracted: no record in this batch rests on the "
        "checkpoint bytes, so hashing the 2 GB file is a gap for a batch that runs the model.",
    "model-bioemu-2":
        "The review kept entity_level at family: the model summary table prints no version row, "
        "and the evaluation methodology says the same checkpoint was used for every benchmark "
        "without naming it. A fresh grep of data/entities and data/evidence found no earlier "
        "BioEmu record and no BioEmu identifier of any kind, so the absent family link is right.",
}

MODE_ADDENDUM = (
    "The review kept this mode as a configuration linked configuration_of the model rather than "
    "nesting it under the checkpoint configuration: the sources attribute the modes to BioEmu2 "
    "and to the command line, not to the bioemu2-preview weights file."
)


def table_claim(record: dict) -> bool:
    locator = record["attributes"].get("source_locator", "")
    return "Model summary table, row" in locator or "Training data table, row" in locator


def main() -> int:
    records = [json.loads(line) for line in BATCH_FILE.open(encoding="utf-8")]
    fixed = 0
    for record in records:
        short = record["id"][len(PREFIX):]
        attributes = record["attributes"]
        if short in LOCATOR_FIXES:
            old, new = LOCATOR_FIXES[short]
            if attributes.get("source_locator") == old:
                attributes["source_locator"] = new
                fixed += 1
            elif attributes.get("source_locator") != new:
                raise SystemExit(f"{record['id']}: unexpected source_locator, not corrected")

        review = dict(attributes.get("review") or {})
        extraction_note = review.get("note")
        if record["kind"] == "source":
            method, method_note = ["source-hash-verification"], SOURCE_NOTE
        elif record["kind"] == "claim":
            if table_claim(record):
                method = ["independent-cell-check", "deterministic-table-parse",
                          "source-hash-verification"]
                method_note = TABLE_NOTE
            else:
                method = ["independent-cell-check", "source-hash-verification"]
                method_note = TEXT_NOTE
        else:
            method = ["independent-cell-check", "source-hash-verification"]
            method_note = RECORD_NOTE

        addendum = REVIEW_ADDENDA.get(short)
        if short.startswith("config-mode-"):
            addendum = " ".join(filter(None, [addendum, MODE_ADDENDUM]))
        note_parts = []
        if extraction_note:
            note_parts.append("Extraction: " + extraction_note.strip())
        if addendum:
            note_parts.append("Review: " + addendum.strip())
        else:
            note_parts.append("Review: checked at the locator named here; nothing to change.")

        review.update({
            "method": method,
            "method_note": method_note,
            "reviewer": REVIEWER,
            "reviewer_note": REVIEWER_NOTE,
            "date": DATE,
            "reviewed_at": REVIEWED_AT,
            "note": " ".join(note_parts),
        })
        attributes["review"] = review

    records.sort(key=lambda r: r["id"])
    with BATCH_FILE.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"applied review to {len(records)} records, corrected {fixed} locators")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
