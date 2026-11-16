#!/usr/bin/env python3
"""Apply the review pass to batch.jsonl.

Two descriptive corrections and a review object on every result and claim.
Rewrites batch.jsonl in place, preserving its serialisation byte for byte for
every untouched record.

    python3 -I review/apply_review.py --batch batch.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys

DATE = "2026-11-15"
REVIEWED_AT = "2026-11-15T00:00:00Z"
REVIEWER = ["claude"]
REVIEWER_NOTE = (
    "Claude (Opus 5) review agent, independent of the agent that extracted this batch; "
    "no human review claimed. Transcription was checked against the pinned sources; "
    "nothing was reproduced and no value was recomputed."
)

RESULT_METHOD_NOTE = (
    "Independent review pass. All thirteen pinned artifacts were re-retrieved on "
    "2026-11-15 and every SHA-256 checked against its source record; the ten archived "
    "gzipped artifacts were each decompressed and hash-checked against the raw "
    "artifact_sha256, and each .gz against its archive_sha256. The eight table cells "
    "were then re-read by a reviewer script written for this pass "
    "(review/check_values.py), which finds the 'Measured design efficiency' section by "
    "its own heading, asserts the four printed header cells and the four row labels, "
    "requires each value to be printed to two decimals, splits the comparator cells on "
    "the printed middle dot, and does not import or reuse "
    "extract/parse_efficiency_table.py. Each stored printed_value, numeric_value, "
    "denominator, metric, unit, metric_direction and conditioning arm was compared "
    "against that parse and against the archived benchmarks/summary.csv, which prints "
    "the same quantity per 10 GPU-minutes: every card value equals its summary.csv "
    "unique_per_10_gpu_min times six at the printed precision, each row's attempts "
    "equals its targets times 200, and each cell's arm equals the dataset column of the "
    "summary.csv row behind it. The reviewer script also re-derived which summary.csv "
    "row each cell must come from, confirming that every RFD4 cell is the "
    "rfd4_proteina_high row and every comparator cell the highest non-RFD4 "
    "unique_per_10_gpu_min in that panel and criterion. All eight cells were in "
    "addition read by eye against the card, column assignment included, since there are "
    "only eight. Results are in review/value-check.tsv: 8 of 8 in_cell, no mismatch. "
    "npm run batch -- check-values was not run and does not apply: it reads JATS XML "
    "tables or a pdftotext -layout text layer, and this table is a Markdown table in a "
    "model card."
)

RESULT_NOTE_COMMON = (
    "Every null and every missing_metadata entry on this result was checked against the "
    "sources and is genuinely unstated: no GPU model is named for the benchmark runs, no "
    "seed is published, and the passing-cluster count behind the rate is in "
    "benchmarks/source_data.csv, which this batch did not retrieve, so numerator is "
    "absent. No uncertainty is printed for any cell. The metric and unit concepts "
    "passing-design-clusters-per-accelerator-hour and count-per-hour were reviewed "
    "against data/vocab/metric.ttl and data/vocab/unit.ttl and both were accepted as "
    "genuinely missing; the metric was added to data/vocab/metric.ttl in this pass."
)

RFD4_RESULT_NOTE = (
    " This is an RFD4-Proteina cell. The card's scope note above the table was checked "
    "verbatim and the value is attached to "
    "rfd4-proteina-20261115-config-previous-release-high-thinking, not to the 2026-10-19 "
    "release; benchmarks/provenance.json and benchmarks/METHODS.md name no checkpoint for "
    "any cohort, so the card's scope note is the only statement tying the table to a "
    "checkpoint pair and it is faithfully recorded."
)

COMPARATOR_RESULT_NOTE = (
    " This is a comparator cell. The printed method name was checked against the card and "
    "against the label column of the summary.csv row behind it, and the comparator "
    "configuration carries no model record because no primary source for the method was "
    "retrieved."
)

CLAIM_METHOD_NOTE = (
    "Independent review pass. All thirteen pinned artifacts were re-retrieved on "
    "2026-11-15 and every SHA-256 checked against its source record; the ten archived "
    "gzipped artifacts decompress to those bytes. Every sentence of this claim was read "
    "back against the locator it names in the re-retrieved artifact, and each statement "
    "attributed to a source was matched to that source's own wording. Preprint claims "
    "were checked against a pdftotext -layout text layer of the version 3 PDF retrieved "
    "at its versioned URL."
)

# ---------------------------------------------------------------- corrections

AME_OLD = (
    "Fixed-ligand conditioning. The methods supplement states that 'partially fixed' "
    "refers to ligand conditioning and that catalytic motif constraints are present in "
    "both conditions."
)
AME_NEW = (
    "Fixed-ligand conditioning, the arm the packet labels mcsa_fixed. The methods "
    "supplement's only statement about the degree of fixing is that AME compares "
    "partially to fully fixed ligand, not fully unfixed."
)

AME_DESC_OLD = (
    "Mean over targets of structurally distinct computational passers per GPU-hour on "
    "the frozen project benchmark atomic motif enzyme target set, 37 tasks, under "
    "fixed-ligand conditioning. the methods supplement states that 'partially fixed' "
    "refers to ligand conditioning and that catalytic motif constraints are present in "
    "both conditions., with 200 original attempts per target."
)
AME_DESC_NEW = (
    "Mean over targets of structurally distinct computational passers per GPU-hour on "
    "the frozen project benchmark atomic motif enzyme target set, 37 tasks, under "
    "fixed-ligand conditioning, with 200 original attempts per target."
)

INPUTS_OLD = (
    "Annotated CIF structures or text-based YAML or JSON design specifications. The "
    "annotations carry the conditions: fixed motifs, hotspots, burial, hydrogen bonds "
    "and coordinate groups."
)
INPUTS_NEW = (
    "Annotated CIF structures or text-based YAML or JSON design specifications. The "
    "annotations carry the conditions; the repository README lists fixed motifs, "
    "hotspots, burial, hydrogen bonds and more."
)

# ------------------------------------------------------- per-record extra notes

CLAIM_NOTES = {
    "claim-previous-pair-identity": (
        "Ruling for the reviewer question this claim records. The claim's two candidates "
        "are stated faithfully and the configuration's checkpoint stays absent with "
        "reason conflicting, because the table names no checkpoint. The weight of the "
        "source text does narrow it: release-checkpoints.json's policy key says the "
        "2026-10-19 release 'changes the latent dimension (16 -> 32) and residue "
        "vocabulary (33 -> 147 classes), so its components are not interchangeable with "
        "the previous release's', which makes the previous release the 16-dimension, "
        "33-class pair in the card's 'Previous release' column rather than the 2026-10-15 "
        "pair, which the card says 'has the same architecture' as 2026-10-19; the "
        "checkpoints reference confirms this by giving the current release autoencoder's "
        "own training recipe as configs/releases/ae/2026_10_15_unified_biomolecule.yaml. "
        "The October 9, 2026 benchmark freeze also predates both dated October pairs. "
        "That is a narrowing, not a statement the sources make, so no record asserts it."
    ),
    "claim-inputs": (
        "Corrected in this pass. The value named 'coordinate groups' as an annotation "
        "type; the phrase occurs in the sources only in benchmarks/METHODS.md, about how "
        "motif RMSD is scored, and that file is not among this claim's sources. The value "
        "now follows the repository README's own list, 'fixed motifs, hotspots, burial, "
        "hydrogen bonds, and more'. Previous value: " + INPUTS_OLD
    ),
    "claim-lineage": (
        "Ruling for the reviewer question this claim records. A claim is right and no "
        "graph edge should be added. The only source for the lineage is an announcement "
        "that says RFD4-Proteina 'is the next generation of RFdiffusion' and is built "
        "'upon previous models, including RFdiffusion, RFdiffusion2, and RFdiffusion3, "
        "and incorporating advances from NVIDIA's Proteina model'. variant_of asserts a "
        "shared architecture the announcement does not describe and the technical sources "
        "do not support: the preprint's architecture is a latent flow-matching model over "
        "a learned biomolecular autoencoder, not a variant of RFdiffusion's. supersedes "
        "means record replacement in this store, and discovery-model-rfdiffusion is a "
        "live family-level record that this release does not replace. The claim keeps the "
        "statement and its target_id without asserting either relation."
    ),
    "claim-conditioning-differences": (
        "Ruling for the comparability question. The conditioning difference is preserved "
        "in three places: each arm is its own protocol with the arm in "
        "allowed_information, each evaluation repeats it in comparison.inputs, and each "
        "result repeats it in conditioning. The two protein-binding cells sit on "
        "ppi_backbone and ppi_all_atom and the two DNA cells on dna_unfixed and "
        "dna_fixed, so comparison.protocol_id and comparison.inputs both differ for those "
        "rows and shared/omics/catalogue-query.ts marks them incompatible. The "
        "small-molecule and enzyme cells do share a protocol, which is correct: "
        "summary.csv puts both printed methods of each of those rows in the same dataset "
        "arm (studio_figure_2c_unfixed and mcsa_fixed) under the same criterion, and "
        "their summary.csv timing_note is per_attempt on both sides, so no timing-basis "
        "asymmetry separates them either. All eight are in any case withheld from "
        "automatic comparison while comparison.budget and comparison.dataset_version are "
        "null. No scoped evidence_concerns entry is needed: the author-run origin, the "
        "packet's own statement that it does not assert all models were equally optimized, "
        "and the disclosed per-method adaptations are already carried on the protocols, "
        "the configurations and the evaluations."
    ),
    "claim-pass-criteria": (
        "Checked cell by cell against all five rows of the 'Common AF3 scoring' table, "
        "including that the Atomic Motif Enzyme row's PAE bound is printed as strictly "
        "below 1.5 A where the other rows print at most, and that the small-molecule "
        "criterion recorded is sm_binder rather than the looser historical disco "
        "criterion."
    ),
    "claim-efficiency-table-scope": (
        "The blockquote was checked verbatim against the re-retrieved card and the "
        "provenance keys against the re-retrieved benchmarks/provenance.json. "
        "benchmarks/METHODS.md and benchmarks/provenance.json name no checkpoint for any "
        "cohort: METHODS.md says the 'exact schedule/checkpoint comes from each native "
        "config' and that 'executed receipts, not the newest README, identify what each "
        "cohort actually ran', and the native configs are not in the packet. So the "
        "benchmark files do not themselves say which pair the table describes; they do "
        "not contradict the card's scope note either, and the card's scope note is what "
        "the batch records."
    ),
    "claim-preprint-status": (
        "The version 3 PDF was re-retrieved at both its versioned URL and the unversioned "
        "latest URL: both gave 13,781,188 bytes with SHA-256 "
        "b581fc10da53e94b263c36a7871906f10ba6559f993c02e08f8b3de6b1d0347e, which is the "
        "hash preprint-versions.json declares for version 3, so that internal consistency "
        "check holds and the latest pointer currently serves version 3. pdfinfo reports "
        "101 pages and the title page states the CC BY 4.0 licence and that the preprint "
        "has not been peer reviewed. Version 3 does print result tables this batch does "
        "not extract (S11, S15, S16, S18, S22, S28, S29); none of them prints any of the "
        "eight efficiency values, so no stored value needs re-sourcing to the preprint. "
        "Recorded as a gap for a follow-up batch, not extracted here."
    ),
    "claim-flow-training": (
        "Checked against Section S4.2 and Table S12 of the re-retrieved version 3 PDF. "
        "Table S11 independently gives the release-scale (K = 4) total as about 18,000 "
        "GPU-hours, consistent with the 16,000 plus 2,000 this claim records."
    ),
    "claim-autoencoder-training": (
        "Checked against Section S4.2 and Table S14 of the re-retrieved version 3 PDF, "
        "which gives the autoencoder's own crop size as 256 tokens, global batch size 512 "
        "and approximate GPU-hours 4,000, and against the checkpoints reference for the "
        "400k steps and the 32 latent channels."
    ),
    "claim-tested-hardware": (
        "The macOS and Windows statement is the repository README's own line under 'System "
        "requirements'; the model card does not make it. Both sources are on the claim."
    ),
}

RESULT_EXTRA = {
    "result-alphaprotein-novo-codesign-atomic-motif-enzyme": (
        " The conditioning sentence on this result was corrected in this pass: it "
        "attributed to the methods supplement a statement that catalytic motif "
        "constraints are present in both conditions, which appears in none of the "
        "sources. The supplement's only statement about the degree of fixing is that AME "
        "compares partially to fully fixed ligand, not fully unfixed."
    ),
    "result-rfd4-proteina-high-thinking-atomic-motif-enzyme": (
        " The conditioning sentence on this result was corrected in this pass: it "
        "attributed to the methods supplement a statement that catalytic motif "
        "constraints are present in both conditions, which appears in none of the "
        "sources. The supplement's only statement about the degree of fixing is that AME "
        "compares partially to fully fixed ligand, not fully unfixed."
    ),
}

CARD = "source-hf-model-card"
PREPRINT = "source-preprint-v3"
PRIORITY = [CARD, PREPRINT, "source-github-readme", "source-hf-benchmark-methods"]


def pick_source(source_ids, sources):
    for suffix in PRIORITY:
        for sid in source_ids:
            if sid.endswith(suffix):
                return sources[sid]
    return sources[sorted(source_ids)[0]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    args = ap.parse_args()

    lines = open(args.batch, encoding="utf-8").read().splitlines()
    records = [json.loads(line) for line in lines]
    sources = {r["id"]: r for r in records if r["kind"] == "source"}

    counts = {"ame_text": 0, "ame_desc": 0, "inputs": 0, "result": 0, "claim": 0}

    for rec in records:
        # --- correction 1: the invented AME conditioning sentence
        blob = json.dumps(rec, sort_keys=True, separators=(", ", ": "), ensure_ascii=False)
        if AME_DESC_OLD in blob:
            blob = blob.replace(json.dumps(AME_DESC_OLD)[1:-1], json.dumps(AME_DESC_NEW)[1:-1])
            counts["ame_desc"] += 1
        if AME_OLD in blob:
            counts["ame_text"] += blob.count(AME_OLD)
            blob = blob.replace(json.dumps(AME_OLD)[1:-1], json.dumps(AME_NEW)[1:-1])
        rec.clear()
        rec.update(json.loads(blob))

    for rec in records:
        attrs = rec["attributes"]

        # --- correction 2: claim-inputs
        if rec["id"].endswith("claim-inputs") and attrs.get("value") == INPUTS_OLD:
            attrs["value"] = INPUTS_NEW
            counts["inputs"] += 1

        if rec["kind"] not in ("result", "claim"):
            continue

        src = pick_source(rec["source_ids"], sources)
        key = rec["id"].replace("rfd4-proteina-20261115-", "")

        if rec["kind"] == "result":
            is_rfd4 = "column 'RFD4-Proteina, high thinking'" in attrs["source_locator"]
            note = RESULT_NOTE_COMMON + (
                RFD4_RESULT_NOTE if is_rfd4 else COMPARATOR_RESULT_NOTE
            )
            note += RESULT_EXTRA.get(key, "")
            method = [
                "independent-cell-check",
                "deterministic-table-parse",
                "source-hash-verification",
            ]
            method_note = RESULT_METHOD_NOTE
            counts["result"] += 1
        else:
            note = (
                "Every statement in this claim was found at the locator it names in the "
                "re-retrieved artifact."
            )
            extra = CLAIM_NOTES.get(key)
            if extra:
                note += " " + extra
            method = ["independent-cell-check", "source-hash-verification"]
            if any(sid.endswith(PREPRINT) for sid in rec["source_ids"]):
                method.append("pdf-text-parse")
            method_note = CLAIM_METHOD_NOTE
            counts["claim"] += 1

        attrs["review"] = {
            "artifact_sha256": src["attributes"]["artifact_sha256"],
            "date": DATE,
            "method": method,
            "method_note": method_note,
            "note": note,
            "retrieval_url": src["attributes"]["retrieval_url"],
            "reviewed_at": REVIEWED_AT,
            "reviewer": REVIEWER,
            "reviewer_note": REVIEWER_NOTE,
        }

    with open(args.batch, "w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(
                json.dumps(rec, sort_keys=True, separators=(", ", ": "), ensure_ascii=False)
            )
            handle.write("\n")

    print(counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
