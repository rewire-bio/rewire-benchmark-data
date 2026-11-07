#!/usr/bin/env python3
"""Apply the HyCell review's rulings and corrections to batch.jsonl."""
import json
import sys

PATH = sys.argv[1]
recs = [json.loads(l) for l in open(PATH, encoding="utf-8")]
by_id = {r["id"]: r for r in recs}
changed = {}


def note(key):
    changed[key] = changed.get(key, 0) + 1


P = "hycell-20261106-protocol-"
AGG = {
    P + "annotation-transfer-lr":
        "Macro-F1 averaged over the held-out batches of an atlas; per atlas, or the "
        "unweighted mean over the seven atlases",
    P + "annotation-transfer-knn":
        "Macro-F1 averaged over the held-out batches of an atlas; per atlas, or the "
        "unweighted mean over the seven atlases",
    P + "annotation-finetuned":
        "Macro-F1 averaged over the held-out batches of an atlas; Table 5 prints it per "
        "atlas for four of the seven atlases and prints no mean over atlases",
    P + "cd4-split-ari":
        "One value over the 2,778 CD4 T cells of the cross-tissue immune atlas, not "
        "averaged over donors",
    P + "cd4-split-nmi-chemistry":
        "One value over the 2,778 CD4 T cells of the cross-tissue immune atlas, not "
        "averaged over donors",
    P + "cd4-split-ari-within-donor":
        "Computed within each donor and averaged over the 12 donors of the cross-tissue "
        "immune atlas",
    P + "gd-t-split-ari":
        "Over the gamma-delta T and tissue-resident CD8 T cells of the cross-tissue immune "
        "atlas; the report prints neither their number nor whether the value is pooled over "
        "donors or averaged within them",
    P + "pseudotime-stage-spearman":
        "One value over the 3,751 cells of the four B-cell to plasma-cell states of the "
        "cross-tissue immune atlas",
    P + "pseudotime-stage-spearman-donor-mean":
        "Computed per donor and averaged over the 12 donors of the cross-tissue immune atlas",
    P + "decoder-fold-change-spearman":
        "One value over the 12,879 genes detected in at least 1% of either state",
    P + "donor-consistency-plasma":
        "Mean over the donors of the cross-tissue immune atlas of each donor's correlation "
        "with the program of the other donors",
    P + "donor-consistency-monocyte":
        "Mean over the donors of the cross-tissue immune atlas of each donor's correlation "
        "with the program of the other donors",
    P + "donor-consistency-cd4":
        "Mean over the donors of the cross-tissue immune atlas of each donor's correlation "
        "with the program of the other donors",
}

PER_CELL = ("Frozen zero-shot embedding of each cell on its own, released weights and default "
            "inference settings, no batch, donor or cell-type labels at inference")
LABEL_TRAINED = PER_CELL + "; the model was pretrained with cell-type labels"

for r in recs:
    a = r["attributes"]

    # A. aggregation that the source does not state (ruling on the downstream protocols)
    if r["kind"] == "protocol" and r["id"] in AGG:
        assert a["aggregation"] == "Per atlas, or the unweighted mean over the seven atlases"
        a["aggregation"] = AGG[r["id"]]
        note("protocol aggregation")
    if r["kind"] == "evaluation":
        c = a["comparison"]
        if c["protocol_id"] in AGG:
            assert c["aggregation"] == "Per atlas, or the unweighted mean over the seven atlases"
            c["aggregation"] = AGG[c["protocol_id"]]
            note("evaluation aggregation")

        # B. ruling 3: label pretraining is not an inference-time adaptation
        if c["adaptation"] == LABEL_TRAINED:
            c["adaptation"] = PER_CELL
            note("evaluation adaptation unified")

    # C. locators that name a column the source does not print under that name
    for obj in (a, a.get("comparison") or {}):
        loc = obj.get("source_locator")
        if not isinstance(loc, str):
            continue
        new = loc
        if new.startswith("Table 3,") and "column 'S'" in new:
            new = new.replace("column 'S'", "column 'Score S'")
        if new.startswith("Figure 1b,") and "column 'Tahoe-x1 (70M)'" in new:
            new = new.replace("column 'Tahoe-x1 (70M)'", "column 'Tahoe-x1'")
        if new != loc:
            obj["source_locator"] = new
            note("locator corrected")

# D. a provenance note about Stack copied onto three unrelated models
STACK_CLAUSE = ("; the store's Stack entries are challenge submissions, not the model")
for mid in ("hycell-20261106-model-scimilarity", "hycell-20261106-model-tahoe-x1",
            "hycell-20261106-model-transcriptformer"):
    pn = by_id[mid]["attributes"]["provenance_note"]
    assert STACK_CLAUSE in pn, mid
    by_id[mid]["attributes"]["provenance_note"] = pn.replace(STACK_CLAUSE, "")
    note("provenance note corrected")

# E. licence: NOTICE licenses HyCell as a whole, and the README places the weights in the package
LIC = ("Apache-2.0 for the code and weights. The hycell NOTICE opens \"HyCell / Copyright (C) "
       "2026 Tencent. Licensed under the Apache License, Version 2.0; see the LICENSE file at "
       "the root of this repository\", the package README's License section says Apache-2.0 and "
       "states that the weights are part of the package, and CITATION.cff and pyproject.toml "
       "give Apache-2.0; the repository LICENSE's default for Tencent-authored materials backs "
       "all of them. No file names the weights file itself, and the package ships no LICENSE of "
       "its own. The training data (CZ CELLxGENE Census, release of 8 November 2025) and the "
       "gene vocabulary drawn from it are CC BY 4.0 and keep their own terms.")
by_id["hycell-20261106-model-hycell"]["attributes"]["licence"] = LIC
note("model licence wording")

lc = by_id["hycell-20261106-claim-hycell-licence-code"]["attributes"]
lc["value"] = ("Apache-2.0. NOTICE licenses HyCell under the Apache License, Version 2.0, "
               "pointing at the repository LICENSE; the README's License section says the same "
               "and states that the weights are part of the package; CITATION.cff and "
               "pyproject.toml give Apache-2.0. The package ships no LICENSE of its own, and no "
               "file names the weights file itself, so the weights are covered as part of "
               "HyCell under the repository LICENSE's default for Tencent-authored materials.")
lc["source_locator"] = ("NOTICE opening lines; README 'License' and 'Install'; CITATION.cff; "
                        "pyproject.toml; repository LICENSE opening paragraph")
note("licence claim wording")

# F. protocol descriptions generated from the slug
DESC = {
    P + "cd4-split-ari":
        "Split the CD4 T cells of the cross-tissue immune atlas into two groups by k-means on "
        "an embedding and score the agreement with the naive-effector annotation.",
    P + "cd4-split-ari-within-donor":
        "Score the same naive-effector CD4 T-cell split within each donor, where sequencing "
        "chemistry no longer varies.",
    P + "cd4-split-nmi-chemistry":
        "Score how far the two-group CD4 T-cell split of an embedding follows the sequencing "
        "chemistry instead of the cell state.",
    P + "gd-t-split-ari":
        "Split gamma-delta T cells from tissue-resident CD8 T cells by k-means on an embedding "
        "and score the agreement with the annotation.",
    P + "decoder-fold-change-spearman":
        "Compare the fold change the HyCell decoder reads out between plasma cells and naive B "
        "cells with the fold change of the counts.",
    P + "pseudotime-stage-spearman":
        "Order B cells into plasma cells by diffusion pseudotime on an embedding and correlate "
        "the ordering with the differentiation stage over all cells.",
    P + "pseudotime-stage-spearman-donor-mean":
        "Correlate the same diffusion-pseudotime ordering with the differentiation stage within "
        "each donor and average over donors.",
}
for pid, d in DESC.items():
    assert by_id[pid]["description"].startswith("Measure:"), pid
    by_id[pid]["description"] = d
    by_id[pid]["attributes"]["protocol"] = d
    note("protocol description rewritten")

# G. the held-out claim is stated for HyCell only
LIMIT = ("The seven atlases are stated to be excluded from HyCell's pretraining corpus. The "
         "report does not say whether the ten published comparators were pretrained on cells "
         "of these atlases, and several are trained on CELLxGENE data, so the comparison is not "
         "shown to be held out for them.")
for rid in ("hycell-20261106-benchmark-held-out-atlases",):
    by_id[rid]["attributes"]["limitations"].append(LIMIT)
    note("benchmark limitation added")
by_id["hycell-20261106-source-report"]["attributes"]["limitations"].append(LIMIT)
note("source limitation added")
# only the protocols that actually score the published comparators
COMPARATOR_PROTOCOLS = [
    P + s for s in ("composite-score", "bio-conservation", "batch-correction",
                    "annotation-transfer-lr", "annotation-transfer-knn", "cd4-split-ari",
                    "cd4-split-ari-within-donor", "cd4-split-nmi-chemistry", "gd-t-split-ari",
                    "pseudotime-stage-spearman", "pseudotime-stage-spearman-donor-mean")]
for pid in COMPARATOR_PROTOCOLS:
    by_id[pid]["attributes"]["limitations"].append(LIMIT)
    note("protocol limitation added")

# H. the review object on every result and claim, and source_checked everywhere
REVIEW = {
    "method": ["independent-cell-check", "deterministic-table-parse", "pdf-text-parse",
               "source-hash-verification"],
    "method_note": (
        "Independent review pass by a different agent from the extractor. All nine pinned "
        "artifacts were re-downloaded at commit 0dcc533c and their SHA-256 checked against the "
        "source records, including the 64,439,816-byte weights, whose hash also equals the "
        "weights_sha256 the sidecar publishes; pdftotext -layout on the re-downloaded PDF "
        "reproduced the archived text layer byte for byte. npm run batch -- check-values was "
        "rerun over the whole batch against that text layer and reproduced the extractor's "
        "value-check.tsv exactly (60 in_cell, 96 in_row, 67 locator_not_parsed, no not_in_row, "
        "wrong_column or overclaimed_in_row). All 198 cells of Tables 3, 4 and 5 and of Figure "
        "1b were then re-read by column position with a reviewer script written for this pass, "
        "which finds each table by its own printed header line and indexes the cell by column, "
        "so Table 4's Immune column cannot be read from Table 3; every printed value matched. "
        "Figure 1b's column identity was fixed two independent ways: its Mean row matches Table "
        "3's Bio column for exactly one assignment of six models, and pdftotext -raw prints the "
        "rotated headers as plain words in that same order. The 36 arithmetic identities (S "
        "against its printed weights for all 12 rows, Table 3's S against the mean of Table 4 "
        "for all 12, and Figure 1b's column means and Mean row against Table 3's Bio for all "
        "six) were recomputed and all hold. The 25 prose values were checked by hand against "
        "the sentence each locator names, including the system each number belongs to. Each "
        "claim was re-read against the passage its locator names."),
    "reviewer": ["claude"],
    "reviewer_note": (
        "Claude research agent; no human review claimed. Reviewed by a different agent from "
        "the one that extracted the batch. Transcription checked against the pinned source; "
        "nothing was reproduced and no value was recomputed."),
    "date": "2026-11-06",
    "reviewed_at": "2026-11-06T00:00:00Z",
    "artifact_sha256": "dc2cacf87ffae8525e81fede1b01f261d3a49cece9061465c36ad1fac6680a28",
    "retrieval_url": ("https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/"
                      "0dcc533cc9f8f76c90ecbfe944df816b6672328a/AI4Science/hycell/paper/"
                      "HyCell_Technical_Report.pdf"),
}
README_SHA = "cd2eb7ae932124cacf9875b0ed1c48504b3e95b8e36169520bd1fe83cc0eecde"
README_URL = ("https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/"
              "0dcc533cc9f8f76c90ecbfe944df816b6672328a/AI4Science/hycell/README.md")

for r in recs:
    if r["kind"] in ("result", "claim"):
        rev = dict(REVIEW)
        srcs = r.get("source_ids") or []
        if "hycell-20261106-source-report" not in srcs:
            rev["artifact_sha256"] = README_SHA if (
                "hycell-20261106-source-model-readme" in srcs) else rev["artifact_sha256"]
            rev["retrieval_url"] = README_URL if (
                "hycell-20261106-source-model-readme" in srcs) else rev["retrieval_url"]
        r["attributes"]["review"] = rev
        note("review object filled")
    r["status"] = "source_checked"

# the one number the report prints twice
dup = by_id["hycell-20261106-result-bio-conservation-hycell-cross-tissue-immune"]
dup["attributes"]["review"] = dict(dup["attributes"]["review"])
dup["attributes"]["review"]["note"] = (
    "Section 3.2 'Embedding structure' restates this value as 0.63 against PCA's 0.49. The "
    "rounded restatement is not stored a second time; PCA's 0.49 is, because Figure 1b has no "
    "PCA column.")
note("duplicate-printing note")

with open(PATH, "w", encoding="utf-8") as fh:
    for r in recs:
        fh.write(json.dumps(r, sort_keys=True) + "\n")

for k, v in sorted(changed.items()):
    print("%4d  %s" % (v, k))
