#!/usr/bin/env python3
"""Apply the independent review's rulings to batch.jsonl, deterministically.

Run from the repository root:
    python3 -I data/omics/torchcraft-20261115/review/apply_review.py

Every change is one named ruling. Re-running on an already-edited file is a no-op
for the review objects and asserts the ruling edits are already in place.
"""

import json
import sys

BATCH = "data/omics/torchcraft-20261115/batch.jsonl"

REVIEW_DATE = "2026-11-16"
REVIEWED_AT = "2026-11-16T01:05:00Z"
REVIEWER = ["claude"]
REVIEWER_NOTE = (
    "Claude (Opus 5) review agent, independent of the extractor; no human review claimed. "
    "Every pinned artifact was re-retrieved and hashed, and every stored value re-read against it. "
    "Nothing was reproduced: no design run, score, docking calculation or binding measurement was repeated, "
    "and no value was recomputed from source data."
)

PDF_SHA = "f8145b5b95552dd30996eda2940507c0f32d09adfc60f44f28458e7872788f21"
PDF_URL = "https://arxiv.org/pdf/2609.19770v1"
LAYOUT_SHA = "90f1da5f8a936766087beba0ade3f038f5b69504b9f581b42f2391f5640c5e6b"

SOURCE_ARTIFACTS = {
    "torchcraft-20261115-source-arxiv-v1": (PDF_SHA, PDF_URL),
    "torchcraft-20261115-source-arxiv-abs": (
        "cac39821a99125fe2f245a30d72d8f1465a3a99b784298ada10f68748b2236a0",
        "https://arxiv.org/abs/2609.19770v1",
    ),
    "torchcraft-20261115-source-project-site": (
        "fa95060dad51bd3e04278b48c7e3bc62c66f8f909db3871e654f79d5a98dcd3c",
        "https://torchx-cpl.github.io/",
    ),
    "torchcraft-20261115-source-torchx-readme": (
        "88da821dfed6d76a6d1d2efd1e3e124a18f35c07d6fdf45a8e374fc2c35fccf0",
        "https://raw.githubusercontent.com/Mingchenchen/TorchX/ebf9dc6676ecb1be505bc72f87de408995f0d8fd/README.md",
    ),
    "torchcraft-20261115-source-torchx-licence": (
        "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
        "https://raw.githubusercontent.com/Mingchenchen/TorchX/ebf9dc6676ecb1be505bc72f87de408995f0d8fd/LICENSE",
    ),
    "torchcraft-20261115-source-torchcraft-gpu-readme": (
        "77a6b7b67f29a7931e58e5ee2bcbaa5efa08a5ff33debd6d658f85ae305ec313",
        "https://raw.githubusercontent.com/Mingchenchen/TorchX/ebf9dc6676ecb1be505bc72f87de408995f0d8fd/torchcraft_gpu/README.md",
    ),
    # Per-retrieval page: the reviewer's own fetch hashed differently, see the ruling below.
    "torchcraft-20261115-source-huggingface-torchfold": (
        "39268aab20e07bb615c1b96c8eb5684686dc953036a7d062dec7684581fbdfcf",
        "https://huggingface.co/datasets/TorchX-CPL/TorchFold",
    ),
}

HASH_NOTE = (
    "All seven pinned artifacts were re-retrieved by the reviewer on 2026-11-16T00:08Z. Six came back "
    "byte-identical to the hash on their source record. The Hugging Face page did not, and cannot: three "
    "consecutive fetches gave three different hashes. Normalising its per-request hf-sanitized CSS class "
    "hashes leaves one further per-request difference, window.requestId, and the page also prints a "
    "download counter; with those normalised the markup is identical. Its licence tag, gate text and "
    "dataset card matched the recorded quotations word for word, so the page is a per-retrieval stamp, "
    "not a changed page. The pdftotext -layout text layer of the refetched PDF hashes to "
    + LAYOUT_SHA
    + ", the value the extractor recorded."
)

TABLE_NOTE = (
    "Re-read independently with data/omics/torchcraft-20261115/review/recheck_values.py, written for this "
    "review and using neither extract/parse_runtime_table.py nor extract/check_transcriptions.py. It locates "
    "the Table S9 header line in the refetched text layer and assigns every numeric cell in a body row to the "
    "length column whose header label starts nearest to it, asserting a one-to-one mapping, so a value taken "
    "from a neighbouring column fails where whitespace splitting would not. It asserted all four row labels, "
    "all five column headers and all twenty cells. Negative controls were rejected: a column-shifted value "
    "(the 200 aa cell given the 300 aa value) and a row-swapped value (NPU w/ FA given the NPU w/o FA value). "
    "The same twenty cells were then read independently out of the HTML table the official project site "
    "reprints and agreed cell for cell. npm run batch -- check-values cannot reach this table: its caption "
    "pattern (scripts/omics/batch.py, 'caption' regexes) requires a colon or full stop after the table label "
    "and the preprint prints 'Table S9 TorchCraft runtime benchmark' with neither, so it reports "
    "row_not_found for all twenty. " + HASH_NOTE
)

KD_NOTE = (
    "Read by hand from the figure caption, the body section and the figure's own panel labels in the refetched "
    "text layer, then re-checked with data/omics/torchcraft-20261115/review/recheck_values.py, written for this "
    "review. It asserts the caption sentence verbatim, takes the four values in the order the caption prints "
    "them, requires this result's value at the ordinal position its target holds in the caption's own target "
    "list, and requires the same order on the four KD panel labels. A negative control that swapped the IFNAR2 "
    "and IL-7Ra values was rejected on the caption order, the panel order and the numeric field. "
    "npm run batch -- check-values lists these eleven values as locator_not_parsed by design, because they are "
    "printed in captions and prose rather than in a table. " + HASH_NOTE
)

FIG_NOTE = (
    "Read by hand from the Supplementary Figure S4 caption in the refetched text layer, then re-checked with "
    "data/omics/torchcraft-20261115/review/recheck_values.py, which asserts the fragments 'MCC = 0.598', "
    "'Pearson r = −0.538' and 'Spearman ρ = −0.602' verbatim in the normalised text and matches each to "
    "its own result. A negative control that gave the MCC result the Pearson value was rejected. The caption "
    "prints the threshold as 6.309 and Appendix A.4.3.2 prints it as 6.31; both are recorded. "
    "npm run batch -- check-values lists these values as locator_not_parsed by design, because they are printed "
    "in a figure caption. " + HASH_NOTE
)

ENTITY_NOTE = (
    "Every quotation and locator on this record was re-read in the refetched artifact named by retrieval_url. "
    + HASH_NOTE
)

SOURCE_NOTE = "Re-retrieved and hashed by the reviewer. " + HASH_NOTE

TABLE_METHOD = ["independent-cell-check", "deterministic-table-parse", "pdf-text-parse", "source-hash-verification"]
CAPTION_METHOD = ["independent-cell-check", "transcription", "pdf-text-parse", "source-hash-verification"]
ENTITY_METHOD = ["transcription", "automated-source-review", "source-hash-verification"]
SOURCE_METHOD = ["source-hash-verification", "automated-source-review"]

# attribute-registry.ts declares no `review` field for these kinds, so the review of their
# text is recorded in the dated review and the receipt, not on the record.
NO_REVIEW_KINDS = {"task", "evaluator"}

# --- Rulings ---------------------------------------------------------------

# R1 TorchScore is not an independent evaluator: it carries the weights the designs were
# optimised against and scores supplied coordinates without refolding the sequence. The
# preprint states both (Appendix A.4.2, Figure 2f and Figure 3i captions). The extractor
# recorded the first half on three of the four pass-rate protocols and neither half on
# protocol-ligand-pocket-torchscore-pass-rate. Recorded on all four, in full.
TORCHSCORE_LIMITATION = (
    "Scored by TorchScore, which carries the same pretrained AlphaFold 3 weights the designs were "
    "optimised against and scores supplied coordinates without refolding the sequence, so it is not "
    "an independent check of the designs."
)
TORCHSCORE_PROTOCOLS = [
    "torchcraft-20261115-protocol-minibinder-torchscore-pass-rate",
    "torchcraft-20261115-protocol-vhh-torchscore-perplexity-pass-rate",
    "torchcraft-20261115-protocol-cyclic-peptide-pass-rate",
    "torchcraft-20261115-protocol-ligand-pocket-torchscore-pass-rate",
]
OLD_TORCHSCORE_LIMITATIONS = {
    "The evaluator uses the weights the TorchCraft designs were optimised against, which the preprint acknowledges.",
    "The evaluator uses the weights the TorchCraft designs were optimised against.",
}

# R2 ProteinMPNN identity. The preprint names ProteinMPNN with no version, checkpoint or
# weight set anywhere (its only other mention is the Science 2022 citation). The extractor
# linked catalog-model-proteinmpnn, which pins version v_48_020, so the link asserts a
# checkpoint the source does not state. discovery-model-proteinmpnn is the versionless
# family record and is what all three existing uses_model links in the store point at.
#    R2b ESM-2 identity. catalog-model-esm-2 is an alias_of discovery-model-esm-2, and
#    relations.ts defines alias_of as "same identity under another ID; never merges results",
#    so a dependency link to the alias is invisible to queries on the canonical record. All
#    twenty existing uses_model links to ESM-2 in the store point at discovery-model-esm-2,
#    which carries the same profile. The preprint names "ESM2-150M" with no checkpoint
#    revision, so the family record is right either way; only which of the two is used changes.
ALIAS_REDIRECTS = {
    "catalog-model-proteinmpnn": "discovery-model-proteinmpnn",
    "catalog-model-esm-2": "discovery-model-esm-2",
}
PROTEINMPNN_FROM = "catalog-model-proteinmpnn"
PROTEINMPNN_TO = "discovery-model-proteinmpnn"

# R3 The dissociation-constant concept's own definition requires the assay and the construct
# format in metric_qualifier, and its scope note says values from different assays or construct
# formats are not comparable. The extractor's qualifier named neither, and was identical for
# the minibinder and the VHH campaigns, which are different construct formats.
KD_QUALIFIERS = {
    "minibinder": (
        "apparent KD of a de novo minibinder, measured by biolayer interferometry with the binder "
        "immobilised and fitted with a 1:1 binding model, for one displayed representative design "
        "from a filtered and ranked pool, not a campaign hit rate"
    ),
    "vhh": (
        "apparent KD of a framework-conditioned VHH, measured by biolayer interferometry with the VHH "
        "immobilised and fitted with a 1:1 binding model, for one displayed representative design "
        "from a filtered and ranked pool, not a campaign hit rate"
    ),
}
KD_PROTOCOL_QUALIFIERS = {
    "torchcraft-20261115-protocol-bli-apparent-kd-minibinder": (
        "apparent KD of a de novo minibinder, measured by biolayer interferometry with the binder "
        "immobilised and fitted with a 1:1 binding model, for one displayed representative design, "
        "not a campaign hit rate"
    ),
    "torchcraft-20261115-protocol-bli-apparent-kd-vhh": (
        "apparent KD of a framework-conditioned VHH, measured by biolayer interferometry with the VHH "
        "immobilised and fitted with a 1:1 binding model, for one displayed representative design, "
        "not a campaign hit rate"
    ),
}

# R4 The 500 aa NPU cell without fused attention. The table caption derives every cell by
# dividing a batch-size-2 run by 2; the footnote says this one cell is a batch-size-1 run.
# The extractor's qualifier asserted both at once.
OOM_RESULT = "torchcraft-20261115-result-runtime-npu-no-fused-attention-500aa"
OOM_RESULT_QUALIFIER = (
    "wall-clock minutes per design at 500 residues, measured at batch size 1 because batch size 2 "
    "exceeded memory, not the batch-size-2 run divided by 2 that every other cell of the table reports"
)
OOM_PROTOCOL = "torchcraft-20261115-protocol-runtime-500aa"
OOM_PROTOCOL_QUALIFIER = (
    "wall-clock minutes per design at 500 residues, batch size 2 divided by 2, except the Ascend 910B "
    "run without fused attention, which is a batch-size-1 run"
)
OOM_PROTOCOL_LIMITATION = (
    "One of the four cells at this length, the Ascend 910B without fused attention, is a batch-size-1 run "
    "because batch size 2 exceeded memory, so it does not compare with the other three."
)

# R5 The Hugging Face page's variability is wider than per-request CSS class hashes.
HF_SOURCE = "torchcraft-20261115-source-huggingface-torchfold"
HF_OLD_LIMITATION = (
    "Mutable page whose markup carries per-request class hashes, so the hash describes one retrieval; "
    "a refetch on 2026-11-16T00:02Z changed only those hashes."
)
HF_NEW_LIMITATION = (
    "Mutable page that cannot be hashed stably: its markup carries per-request hf-sanitized CSS class "
    "hashes and a per-request window.requestId, and it prints a download counter. Three consecutive "
    "reviewer fetches gave three different hashes; with those per-request values normalised the markup "
    "was identical and the licence tag, gate text and dataset card matched the recorded quotations. The "
    "hash therefore describes one retrieval and is not a check on the page's content."
)


def primary_source(rec):
    if rec["kind"] == "source":
        return rec["id"]
    ids = rec.get("source_ids") or []
    if "torchcraft-20261115-source-arxiv-v1" in ids:
        return "torchcraft-20261115-source-arxiv-v1"
    for i in ids:
        if i in SOURCE_ARTIFACTS:
            return i
    return "torchcraft-20261115-source-arxiv-v1"


def review_for(rec):
    rid = rec["id"]
    src = primary_source(rec)
    sha, url = SOURCE_ARTIFACTS[src]

    if rec["kind"] == "result":
        if "result-runtime-" in rid:
            method, note = TABLE_METHOD, TABLE_NOTE
        elif "result-bli-kd-" in rid:
            method, note = CAPTION_METHOD, KD_NOTE
        else:
            method, note = CAPTION_METHOD, FIG_NOTE
    elif rec["kind"] == "source":
        method, note = SOURCE_METHOD, SOURCE_NOTE
    else:
        method, note = ENTITY_METHOD, ENTITY_NOTE

    return {
        "artifact_sha256": sha,
        "date": REVIEW_DATE,
        "method": method,
        "method_note": note,
        "retrieval_url": url,
        "reviewed_at": REVIEWED_AT,
        "reviewer": REVIEWER,
        "reviewer_note": REVIEWER_NOTE,
    }


def main():
    records = [json.loads(l) for l in open(BATCH, encoding="utf-8")]
    changes = []

    for rec in records:
        rid = rec["id"]
        a = rec["attributes"]

        # R1
        if rid in TORCHSCORE_PROTOCOLS:
            lims = [l for l in a.get("limitations", []) if l not in OLD_TORCHSCORE_LIMITATIONS]
            if TORCHSCORE_LIMITATION not in lims:
                lims.insert(1 if len(lims) > 1 else len(lims), TORCHSCORE_LIMITATION)
                changes.append(f"R1 {rid}: TorchScore shared-weights and no-refold limitation recorded")
            a["limitations"] = lims

        # R2 and R2b
        for link in rec.get("links", []):
            if link["target_id"] in ALIAS_REDIRECTS:
                old = link["target_id"]
                link["target_id"] = ALIAS_REDIRECTS[old]
                changes.append(f"R2 {rid}: {link['relation']} {old} -> {link['target_id']}")

        # R3
        if "result-bli-kd-minibinder-" in rid:
            if a["metric_qualifier"] != KD_QUALIFIERS["minibinder"]:
                a["metric_qualifier"] = KD_QUALIFIERS["minibinder"]
                changes.append(f"R3 {rid}: metric_qualifier names the assay and the construct format")
        elif "result-bli-kd-vhh-" in rid:
            if a["metric_qualifier"] != KD_QUALIFIERS["vhh"]:
                a["metric_qualifier"] = KD_QUALIFIERS["vhh"]
                changes.append(f"R3 {rid}: metric_qualifier names the assay and the construct format")
        if rid in KD_PROTOCOL_QUALIFIERS:
            if a["metric_qualifier"] != KD_PROTOCOL_QUALIFIERS[rid]:
                a["metric_qualifier"] = KD_PROTOCOL_QUALIFIERS[rid]
                changes.append(f"R3 {rid}: metric_qualifier names the assay and the construct format")

        # R4
        if rid == OOM_RESULT and a["metric_qualifier"] != OOM_RESULT_QUALIFIER:
            a["metric_qualifier"] = OOM_RESULT_QUALIFIER
            changes.append(f"R4 {rid}: metric_qualifier no longer claims both batch sizes")
        if rid == OOM_PROTOCOL:
            if a["metric_qualifier"] != OOM_PROTOCOL_QUALIFIER:
                a["metric_qualifier"] = OOM_PROTOCOL_QUALIFIER
                changes.append(f"R4 {rid}: metric_qualifier records the batch-size-1 exception")
            if OOM_PROTOCOL_LIMITATION not in a.get("limitations", []):
                a.setdefault("limitations", []).append(OOM_PROTOCOL_LIMITATION)
                changes.append(f"R4 {rid}: batch-size-1 exception recorded as a limitation")

        # R5
        if rid == HF_SOURCE:
            lims = [HF_NEW_LIMITATION if l == HF_OLD_LIMITATION else l for l in a.get("limitations", [])]
            if lims != a.get("limitations", []):
                changes.append(f"R5 {rid}: limitation names every per-request element, not only class hashes")
            a["limitations"] = lims

        # The reviewer's own review object replaces the extractor's on every record whose
        # kind declares one. shared/omics/attribute-registry.ts does not declare `review`
        # for `task` or `evaluator`, and records -- add rejects an undeclared attribute.
        if rec["kind"] in NO_REVIEW_KINDS:
            a.pop("review", None)
        else:
            a["review"] = review_for(rec)

    with open(BATCH, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    # Assertions: the rulings must be in place after the write.
    records = [json.loads(l) for l in open(BATCH, encoding="utf-8")]
    by_id = {r["id"]: r for r in records}
    for pid in TORCHSCORE_PROTOCOLS:
        assert TORCHSCORE_LIMITATION in by_id[pid]["attributes"]["limitations"], pid
    assert not any(
        l["target_id"] in ALIAS_REDIRECTS for r in records for l in r.get("links", [])
    ), "a link to a versioned or alias model record remains"
    assert sum(
        1 for r in records for l in r.get("links", []) if l["target_id"] == PROTEINMPNN_TO
    ) == 3, "expected three ProteinMPNN links"
    assert sum(
        1 for r in records for l in r.get("links", []) if l["target_id"] == "discovery-model-esm-2"
    ) == 1, "expected one ESM-2 link"
    assert by_id[OOM_RESULT]["attributes"]["metric_qualifier"] == OOM_RESULT_QUALIFIER
    assert HF_NEW_LIMITATION in by_id[HF_SOURCE]["attributes"]["limitations"]
    assert all(
        r["attributes"]["review"]["reviewer_note"] == REVIEWER_NOTE
        for r in records
        if r["kind"] not in NO_REVIEW_KINDS
    )
    assert all("review" not in r["attributes"] for r in records if r["kind"] in NO_REVIEW_KINDS)
    assert len(records) == 165, len(records)

    for c in changes:
        print(c)
    print(f"{len(changes)} ruling edits; review object rewritten on all {len(records)} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
