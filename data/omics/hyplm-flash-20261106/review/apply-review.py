"""Apply the independent review's rulings to batch.jsonl.

The frozen extractor commit (b4c9fbf3ce7851ff4fd72fd5ac03f3ee49bca67e) built batch.jsonl with
extract/build.py. This script is the record of what the review changed on top of that output:

    python3 -I data/omics/hyplm-flash-20261106/extract/build.py <report.pdf> batch.jsonl
    python3 -I data/omics/hyplm-flash-20261106/review/apply-review.py batch.jsonl

Every change is argued in docs/reviews/2026-11-06-hyplm-flash.md with the source or contract text
that decides it.
"""
import json
import sys

PATH = sys.argv[1]
REVIEWED_AT = "2026-11-06T00:00:00Z"
ARTIFACT = "d81d88a415a91c2b00d8e97513a90c03ccffd857ec75033fa7de77227dea1710"
URL = ("https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/"
       "0dcc533cc9f8f76c90ecbfe944df816b6672328a/AI4Science/hyplm_flash/HyPLM_Technical_Report.pdf")

REVIEW = {
    "method": ["independent-cell-check", "deterministic-table-parse", "pdf-text-parse",
               "source-hash-verification"],
    "method_note": (
        "Independent review pass. All six pinned artifacts were re-downloaded at the pinned commit "
        "and their SHA-256 checked against the source records; pdftotext -layout reproduced the "
        "archived text layer byte for byte. npm run batch -- check-values was run over the whole "
        "batch (value-check.tsv). The 469 recorded cells of Tables 3, 5, 6 and 7 were then re-read "
        "by a reviewer script written for this pass, which takes each table's column order from its "
        "printed header line and splits every body row by printed cell, without using "
        "extract/parse.py; every printed value and column matched. The two arithmetic constraints "
        "were re-derived independently rather than taken from the extractor's checker: each Table 3 "
        "perplexity against exp of its NLL over the NLL's own rounding interval, and each Table 5 "
        "average against the mean of its five categories. Column assignment in Tables 6 and 7 is "
        "anchored outside those tables, by Table 3's NLL values and by Figure 3a's and Table 5's "
        "ProteinGym values, and the four printed paired differences reconcile with the Table 6 "
        "ProteinGym row. The 15 locators check-values cannot parse, four Figure 3a bar labels and "
        "eleven prose values, were read by hand against the text layer; in Figure 3a each bar label "
        "and its value share one line. extract/check_cells.py was rerun and reproduces "
        "cell-check.tsv."),
    "reviewer": ["claude"],
    "reviewer_note": (
        "Claude research agent; no human review claimed. Reviewed by a different agent from the one "
        "that extracted the batch. Transcription checked against the pinned source; nothing was "
        "reproduced and no value was recomputed."),
    "reviewed_at": REVIEWED_AT,
    "artifact_sha256": ARTIFACT,
    "retrieval_url": URL,
}

records = [json.loads(line) for line in open(PATH) if line.strip()]
by_id = {r["id"]: r for r in records}
log = []


def note(message):
    log.append(message)


# 1. The ProteinGym tie. Section 4.1 is the most misreadable statement in this source, and the
#    batch put it only in result `claim_scope`. That field is declared for a result but one other
#    result in the whole store uses it, no display or comparison path reads it, and its established
#    use is a benchmark-research audit field (shared/omics/benchmark-research.ts). Meanwhile all 17
#    ProteinGym zero-shot results share one metric_qualifier, so comparisons rank them freely. The
#    tie therefore goes where a reader of a result meets it: the protocol's limitations. claim_scope
#    stays as the per-result marker.
proto = by_id["hyplm-flash-20261106-protocol-proteingym-zero-shot"]["attributes"]
assert len(proto["limitations"]) == 1, proto["limitations"]
proto["limitations"].append(
    "The order of these values is not a ranking of the models. Section 4.1 states that "
    "HyPLM-Flash's differences to ESM-2 650M (-0.006, 95% interval [-0.025, 0.010]), ESM C 600M "
    "(+0.003, [-0.015, 0.019]), DPLM-650M (-0.001, [-0.019, 0.015]) and E1-600M (-0.011, [-0.029, "
    "0.005]) 'are not significant, and neither are those to ESM-2 3B, ESM-2 15B and ESM C 6B'. "
    "Eight of the values under this protocol, spanning 0.403 to 0.420, therefore sit inside one "
    "statistical tie, and the four printed paired differences recorded under "
    "hyplm-flash-20261106-protocol-proteingym-paired-difference are the records that establish it. "
    "No interval is printed for any single value here.")
note("ruling 4: the Section 4.1 tie added to the proteingym-zero-shot protocol's limitations, "
     "where a reader of a result reaches it; claim_scope left on the 12 results that carry it")

# 2. Figure 1b's won and lost labels. The denominator is undefined against the report's 32 tasks
#    and one row contradicts it, and only the ESM-2 650M pair said so. A reader of any other pair
#    would take "21 of 35" at face value.
CAVEAT = (" Figure 1's axis reads 'of 35' but the report never defines its 35 task splits against "
          "the 32 tasks of Tables 6 and 7, and the won and lost labels of the ESM-2 650M row sum "
          "to 34 while the other seven rows sum to 35, so the denominator is not established. "
          "Appendix A also records that three regression splits are left out of Figure 1 "
          "altogether.")
touched = 0
for r in records:
    if r["kind"] != "claim" or "figure1b" not in r["id"]:
        continue
    value = r["attributes"]["value"]
    if "of 35" not in value and "sum to 34" not in value:
        r["attributes"]["value"] = value.rstrip() + CAVEAT
        touched += 1
note(f"ruling 6: the undefined denominator and the ESM-2 650M arithmetic added to {touched} of the "
     f"16 Figure 1b claims; the ESM-2 650M pair already carried it")

# 3. ProteinGym's split and dataset version. Table 4 prints "217 assays" for ProteinGym
#    substitutions with no train/valid/test, so "Test split as printed in Table 4" is wrong for
#    these 56 evaluations, and the identity the reuse of the stored 217-assay v1.3 subset rests on
#    was recorded nowhere on the evaluation. docs/collection.md: a comparison field the source does
#    not state is null, which blocks automatic comparison.
fixed = 0
for r in records:
    if r["kind"] != "evaluation" or "proteingym" not in r["id"]:
        continue
    comparison = r["attributes"]["comparison"]
    comparison["split"] = (
        "No train, validation or test split: ProteinGym substitutions is scored zero-shot over all "
        "its assays, and Table 4 prints '217 assays' in place of split sizes.")
    comparison["dataset_version"] = (
        "ProteinGym v1.3, 217 substitution assays (Table 4). Table 5's caption cites ProteinGym "
        "repository commit 144fe22 for the published leaderboard rows it quotes; the report does "
        "not separately state the commit of the authors' own assay files.")
    fixed += 1
note(f"question 1: split and dataset_version corrected on {fixed} ProteinGym evaluations, which "
     f"had claimed a Table 4 test split that table does not print for this task")

# 4. Record the review on every result and claim, and mark the reviewed records source_checked.
reviewed = 0
for r in records:
    if r["kind"] in ("result", "claim"):
        r["attributes"]["review"] = dict(REVIEW)
        reviewed += 1
    r["status"] = "source_checked"
note(f"review object written on {reviewed} results and claims; all {len(records)} records set to "
     f"source_checked")

records.sort(key=lambda r: r["id"])
with open(PATH, "w") as out:
    for r in records:
        out.write(json.dumps(r, sort_keys=True) + "\n")
for line in log:
    print(line)
