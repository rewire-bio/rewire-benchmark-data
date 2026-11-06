"""Apply the independent review's rulings to batch.jsonl.

The frozen extractor commit (2da41a749f4b0d2c03076edab37086d824794ea6) built batch.jsonl with
extract/build.py. This script is the record of what the review changed on top of that output, in
order. Run it on the extractor's batch.jsonl to reproduce the reviewed bytes:

    python3 -I data/omics/hyinv-20261106/extract/build.py <report.pdf> batch.jsonl
    python3 -I data/omics/hyinv-20261106/review/apply-review.py batch.jsonl

Every change is listed in docs/reviews/2026-11-06-hyinv.md with the source text that decides it.
"""
import json
import sys

PATH = sys.argv[1]
REVIEWED_AT = "2026-11-06T00:00:00Z"
ARTIFACT = "0f10b390be399c341d1f7497c5a3ca0ac857ce78172c4732bdc86a9c66e46419"
URL = ("https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/"
       "0dcc533cc9f8f76c90ecbfe944df816b6672328a/AI4Science/hyinv/HyInv_Technical_Report.pdf")

# Panels whose chains Appendix C and Appendix G leave with possible training overlap. The latency
# backbones are not a scored panel, so the overlap concern does not reach them.
OVERLAP_DATA = [
    "hyinv-20261106-data-cath42-test",
    "hyinv-20261106-data-cath43-test",
    "hyinv-20261106-data-cath43-validation",
    "hyinv-20261106-data-cath43-validation-subset-1",
    "hyinv-20261106-data-cath43-validation-subset-2",
    "hyinv-20261106-data-cath43-validation-subset-3",
    "hyinv-20261106-data-de-novo-backbones",
    "hyinv-20261106-data-recentpdb",
    "hyinv-20261106-data-ts50",
    "hyinv-20261106-data-ts500",
]
# The protocols whose results Appendix D.2's statement is about: scTM and the paired scTM
# difference at each method's own single published setting.
DIVERSITY_PROTOCOLS = [
    "hyinv-20261106-protocol-sctm-boltz2",
    "hyinv-20261106-protocol-sctm-difference-boltz2",
    "hyinv-20261106-protocol-sctm-difference-esmfold2",
    "hyinv-20261106-protocol-sctm-difference-protenix2",
    "hyinv-20261106-protocol-sctm-esmfold2",
    "hyinv-20261106-protocol-sctm-protenix2",
]
# The protocols measured on weights other than the released checkpoint.
WEIGHTS_PROTOCOLS = [
    "hyinv-20261106-protocol-design-latency-h20",
    "hyinv-20261106-protocol-design-speedup-vs-proteinmpnn-h20",
    "hyinv-20261106-protocol-sctm-fixed-diversity-bf16-minus-reference",
]

REVIEW = {
    "method": ["independent-cell-check", "deterministic-table-parse", "pdf-text-parse",
               "source-hash-verification"],
    "method_note": (
        "Independent review pass. The pinned PDF was re-downloaded at the pinned commit and its "
        "SHA-256 checked against the source record; pdftotext -layout reproduced the archived text "
        "layer byte for byte. npm run batch -- check-values was run over the whole batch against "
        "that text layer (value-check.tsv). The 170 cells of Tables 6, 7, 8 and 9 and the 290 cells "
        "of the Figure 14 and Figure 15 matrices were then re-read by a reviewer script that finds "
        "each row by its printed label and splits the printed cells by position, written for this "
        "pass without using the extractor's parser; every printed value and column matched. Column "
        "assignment in Figure 14 was confirmed against the labelled columns of Table 2 and against "
        "Section 5.2's prose figures; Figure 15's rests on its caption 'Same layout as Figure 14'. "
        "Table 1, Figure 4a and the eleven prose values were read by hand against the text layer. "
        "Each claim was re-read against the passage its locator names."),
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


# 1. Table 1 prints bare numbers; its units are in the column headings ("128 designs (ms)",
#    "10,000 designs (s)"). printed_value is the string exactly as printed, so the unit comes off.
#    The 10,000-design column is printed in seconds, which five results recorded as milliseconds.
fixed_printed = fixed_unit = 0
for r in records:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    loc = a.get("source_locator", "")
    if not loc.startswith("Table 1,"):
        continue
    printed = a["printed_value"]
    for suffix, unit in ((" ms", "millisecond"), (" s", "second")):
        if printed.endswith(suffix):
            a["printed_value"] = printed[: -len(suffix)]
            column = loc.split("column '", 1)[1].split("'", 1)[0]
            request = a["unit_detail"].split("; ", 1)[1]
            a["unit_detail"] = (f"Printed as '{a['printed_value']}' under the column heading "
                                f"'{column}'; {request}")
            fixed_printed += 1
            if a["unit"] != unit:
                a["unit"] = unit
                fixed_unit += 1
            break
note(f"Table 1: {fixed_printed} printed values stripped of a unit the cell does not print, "
     f"{fixed_unit} units corrected to second")

# 2. Appendix A states the resample count only for the paired differences of Tables 6 and 7
#    ("the percentile interval of 10,000 resamples") and for the gain at fixed diversity over the
#    unmodified sampler ("an interval from 1,000 draws"). No count is printed for Table 9 or for
#    Appendix D.3, so theirs is removed rather than carried over.
res_fixed = res_dropped = 0
for r in records:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    unc = a.get("uncertainty")
    if not isinstance(unc, dict) or "resamples" not in unc:
        continue
    loc = a.get("source_locator", "")
    if loc.startswith("Table 8,"):
        unc["resamples"] = 1000
        unc["note"] = ("95% interval over CATH topology clusters, over chains on RecentPDB; "
                       "Appendix A states the interval comes from 1,000 draws in which all points "
                       "of all curves are recomputed from one cluster resample.")
        res_fixed += 1
    elif loc.startswith("Table 9,") or loc.startswith("Appendix D.3"):
        del unc["resamples"]
        unc["note"] = (unc.get("note", "").rstrip(".") +
                       ". The report does not state how many resamples this interval comes from.")
        res_dropped += 1
note(f"uncertainty: {res_fixed} Table 8 resample counts set to the printed 1,000, "
     f"{res_dropped} unstated resample counts removed (Table 9, Appendix D.3)")

# 3. Table 9's printed verdict column ("Lower end >= -0.002") is the report's own pass rule read
#    off the interval in the same row, not a quantity measured on a panel. It stays recorded, in
#    the uncertainty note, but it comes out of metric_qualifier: a qualifier distinguishes a class,
#    setting, scope, cutoff or aggregation, and comparisons require the same qualifier, so a
#    per-row verdict there would stop four rows of one table sharing a qualifier for no reason of
#    measurement.
verdicts = 0
for r in records:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    if not a.get("source_locator", "").startswith("Table 9,"):
        continue
    marker = "; the report's printed verdict on whether the lower interval end is"
    if marker in a["metric_qualifier"]:
        a["metric_qualifier"] = a["metric_qualifier"].split(marker)[0]
        verdicts += 1
note(f"Table 9: printed verdict removed from {verdicts} metric qualifiers and kept in the "
     f"uncertainty note, so the four rows share a qualifier")

# 4. Table 7 prints three RecentPDB columns ("RecentPDB, ESMFold2", "RecentPDB, Boltz2",
#    "RecentPDB, Protenix2"). A locator naming only 'RecentPDB' does not say which.
loc_fixed = 0
for r in records:
    a = r["attributes"]
    loc = a.get("source_locator", "")
    if loc.startswith("Table 7,") and "column 'RecentPDB'" in loc:
        a["source_locator"] = loc.replace("column 'RecentPDB'", "column 'RecentPDB, ESMFold2'")
        loc_fixed += 1
note(f"Table 7: {loc_fixed} locators disambiguated to the printed column name 'RecentPDB, ESMFold2'")

# 5. Scope each evidence concern. docs/collection.md: applies_to is left out only when the whole
#    source is unreliable, and an entry without it withholds every record citing the source,
#    including the licence and architecture claims and any use case citing it for context.
report = by_id["hyinv-20261106-source-report"]
concerns = report["attributes"]["evidence_concerns"]
assert len(concerns) == 3, len(concerns)
concerns[0]["applies_to"] = OVERLAP_DATA
concerns[0]["reviewed_at"] = REVIEWED_AT
concerns[1]["applies_to"] = DIVERSITY_PROTOCOLS
concerns[1]["reviewed_at"] = REVIEWED_AT
concerns[1]["message"] = (
    "The ten baselines are single published settings at one temperature each, so their design-set "
    "diversity differs from HyInv's: on CATH4.3 test HyInv samples at diversity 0.331 against 0.093 "
    "for PiFold, 0.104 for CMLM, 0.144 for LM-Design 650M and 0.000 for DPLM-2 3B, which decodes by "
    "argmax. Appendix D.2 states that these four differences are not at matched diversity, and "
    "Appendix A states that even for the closest baselines the comparisons are 'close to, but not "
    "exactly at, equal diversity', the largest offset of 0.016 being worth at most 0.0011 scTM at "
    "the development slope. The scTM and scTM difference results of the protocols named here must "
    "not be read as a matched-diversity ranking. The results read at a stated diversity level "
    "(Tables 8 and 9 and Appendix D.3) are not covered by this entry, because they are the ones the "
    "report reads on a fitted curve at a fixed diversity; nor are the recovery, diversity, pLDDT, "
    "scRMSD and lDDT results, whose protocols carry the same single-setting caveat in their own "
    "limitations and whose metric qualifiers say the value is at each method's own setting.")
concerns[2]["applies_to"] = WEIGHTS_PROTOCOLS
concerns[2]["reviewed_at"] = REVIEWED_AT
note("source concerns: all three scoped with applies_to (10 panel datasets and subsets; "
     "6 scTM and scTM-difference protocols; 3 protocols measured on other weights)")

# 6. The pinned bytes were produced after the date the report prints. Both dates are facts about
#    the same artifact, so the printed date stays in version and the production date is recorded
#    beside it rather than as a concern: it does not make any value unreliable.
report["attributes"]["version_note"] = (
    "Page 1 of the report prints the date 2026-10-14, which is the date issue #232 records and the "
    "one kept in version. The pinned PDF's own metadata gives CreationDate and ModDate "
    "D:20261030105208+08'00' (2026-10-30 02:52 UTC), produced by pdfTeX-1.40.25, so the bytes that "
    "carry artifact_sha256 were typeset sixteen days after the printed date. No earlier PDF of this "
    "report is published at or before the pinned commit, so the two dates cannot be compared "
    "against another version of the bytes, and nothing in the batch rests on either date beyond "
    "naming the report.")
note("report source: version_note records the printed date 2026-10-14 against the PDF's "
     "CreationDate of 2026-10-30")

# 7. Record the review on every result and claim, and mark the reviewed records source_checked.
reviewed = 0
for r in records:
    if r["kind"] in ("result", "claim"):
        r["attributes"]["review"] = dict(REVIEW)
        reviewed += 1
    r["status"] = "source_checked"
note(f"review object written on {reviewed} results and claims; all "
     f"{len(records)} records set to source_checked")

records.sort(key=lambda r: r["id"])
with open(PATH, "w") as out:
    for r in records:
        out.write(json.dumps(r, sort_keys=True) + "\n")
for line in log:
    print(line)
