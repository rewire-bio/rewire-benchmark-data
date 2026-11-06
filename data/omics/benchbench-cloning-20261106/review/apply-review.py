"""Apply the independent review's rulings to batch.jsonl.

The frozen extractor commit (36414d4) built batch.jsonl with build.py. This script records what the
review changed on top of that output:

    python3 -I data/omics/benchbench-cloning-20261106/build.py <paper.pdf> batch.jsonl
    python3 -I data/omics/benchbench-cloning-20261106/review/apply-review.py batch.jsonl

Each change is argued in docs/reviews/2026-11-06-benchbench-cloning.md with the deciding text.
"""
import json
import sys

PATH = sys.argv[1]
REVIEWED_AT = "2026-11-06T00:00:00Z"
ARTIFACT = "6f5044b1bbbd81ad86b23cb536e2cae6428e0d9126f11546041355518febdc39"
URL = "https://arxiv.org/pdf/2610.33355v1"

REVIEW = {
    "method": ["independent-cell-check", "deterministic-table-parse", "pdf-text-parse",
               "source-hash-verification"],
    "method_note": (
        "Independent review pass. All three pinned artifacts were re-downloaded and their SHA-256 "
        "checked against the source records; the archived gzipped text layer matches its recorded "
        "hash and decompresses byte for byte to a pdftotext -layout run on the refetched PDF. The "
        "repository 404 was rechecked at review time on both the web page and the GitHub REST API. "
        "npm run batch -- check-values reproduced the extractor's figures. All 224 results were "
        "then re-read by a reviewer script written for this pass, which locates each table body by "
        "its own printed header line rather than by caption proximity, takes the column order from "
        "that header and splits each row on runs of two or more spaces, without using "
        "extract/parse_tables.py or extract/check_tables.py; every printed value and every printed "
        "interval matched its own field. Three arithmetic constraints were re-derived "
        "independently: each Table G2 column sums to the printed top-effort construct-design "
        "numerator over 75, each Table G1 Solved-at-least-once count over 50 equals the printed "
        "pass@10, and every Table D2 aggregate equals (50 x protocol + 15 x construct) / 65. The "
        "1/75 grid check that identifies the single off-grid rate was recomputed over all 24 lanes "
        "using each printed value's own rounding window."),
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


# 1. The off-grid 31.9%. The batch stored it with source_anomaly and source_warnings, which
#    docs/record-contract.md says are "notes for readers and do not block": so as extracted the
#    value still supports automatic comparison. Two independent signals point at a transcription
#    fault in the paper rather than a real value: it is the only one of the 24 printed construct
#    rates with no integer numerator in its rounding window over 75, and its interval is
#    byte-identical to the same system's top-effort interval. That is the "conflicting tables"
#    case docs/collection.md gives for an evidence concern. The printed value is kept unchanged;
#    the concern is scoped to this one result, so the lane's aggregate, which is 15.8 whether the
#    rate is 31.9 or 32.0, and every other record stay usable.
ANOMALY = "benchbench-cloning-20261106-result-gemini-4-argon-low-construct-design"
assert ANOMALY in by_id
paper = by_id["benchbench-cloning-20261106-source-arxiv-v1"]["attributes"]
paper.setdefault("evidence_concerns", []).append({
    "source_id": "benchbench-cloning-20261106-source-arxiv-v1",
    "message": (
        "Table D2's construct-design rate for Gemini 4 Argon at low effort, 31.9%, cannot be a mean "
        "of binary outcomes over the stated 15 tasks times 5 attempts: no integer numerator over 75 "
        "falls in its rounding window [23.8875, 23.9625], while all 23 other printed construct "
        "rates do. Its printed 95% interval [10.7, 52.0] is also byte-identical to the same "
        "system's top-effort interval. The two signals together indicate a transcription fault in "
        "the paper rather than a measured value, and the paper prints nothing that resolves it: the "
        "lane's aggregate is 15.8 under either 31.9 or 32.0, and Table G2's per-task solves are "
        "top-effort only. The printed value is kept as published and this entry withholds it from "
        "automatic comparison; the lane's other results are not covered."),
    "source_locator": "Table D2, row 'Gemini 4 Argon' tier 'low' effort 'low', column "
                      "'Construct design % [95% CI]'",
    "artifact_sha256": ARTIFACT,
    "review_method": "independent-cell-check",
    "reviewed_at": REVIEWED_AT,
    "applies_to": [ANOMALY],
})
note("question 3: evidence concern on the paper source scoped to the single off-grid 31.9% result, "
     "because source_warnings does not block comparison")

# 2. The protocol-development denominator. Appendix B states the attempt budget ("Each system
#    completed 10 attempts per protocol-development task"), so 500 is the stated number of
#    attempts and belongs in coverage.eligible. What the paper never states is the denominator of
#    the rate, and for the only two systems where the budget and the graded count differ the
#    printed value does not reveal which was used: 31/500 = 6.200 and 31/498 = 6.225 both print as
#    6.2, and 20/500 = 4.000 and 20/496 = 4.032 both print as 4.0. The batch's limitation presented
#    the /500 arithmetic as evidence; it is not evidence for these two.
proto = by_id["benchbench-cloning-20261106-protocol-protocol-development-pass-rate"]["attributes"]
old = next(l for l in proto["limitations"] if l.startswith("The stated denominator is 500"))
proto["limitations"][proto["limitations"].index(old)] = (
    "Appendix B states the attempt budget, 10 attempts for each of the 50 protocol-development "
    "tasks, so 500 attempts were planned per lane. The paper never states the denominator of the "
    "pass rate. For the six systems whose graded count is 500 the two readings coincide. For the "
    "two where they differ the printed rate does not distinguish them: Grok 4.7 passed 31 of 498 "
    "graded, and 31/500 = 6.200 and 31/498 = 6.225 both print as 6.2; Gemini 3.8 Flash passed 20 of "
    "496 graded, and 20/500 = 4.000 and 20/496 = 4.032 both print as 4.0. Whether ungraded attempts "
    "count as failures or are dropped is therefore unresolved, and Table E2 separately records 548 "
    "recorded attempts for Grok 4.7 and 501 for Kimi K3 against a budget of 500, which the paper "
    "does not explain. Tables E1 and E2 are top-effort only, so no graded count is published for "
    "the other 16 lanes.")
fixed = 0
for rid, graded, passed, alt in (
        ("benchbench-cloning-20261106-result-grok-4-7-xhigh-protocol-development", 498, 31, "6.225"),
        ("benchbench-cloning-20261106-result-gemini-3-8-flash-high-protocol-development", 496, 20,
         "4.032")):
    a = by_id[rid]["attributes"]
    cov = a["coverage"]
    assert cov["scored"] == graded and cov["eligible"] == 500, (rid, cov)
    cov["note"] = (
        f"Table E1 prints {graded} graded attempts and {passed} passed; Table E2 prints "
        f"{'548' if graded == 498 else '500'} recorded and "
        f"{'50' if graded == 498 else '4'} unscored. Appendix B's budget is 500 attempts. The "
        f"printed rate does not say which denominator was used: {passed}/500 and {passed}/{graded} "
        f"= {alt} both round to the printed value.")
    a.setdefault("source_warnings", []).append(
        f"Denominator not established: the paper's budget is 500 attempts but only {graded} were "
        f"graded, and the printed rate rounds the same way over either. Do not treat this value as "
        f"a rate over {graded} or over 500 without the paper's grading rule.")
    fixed += 1
note(f"question 4: the protocol limitation now distinguishes the stated attempt budget from the "
     f"unstated rate denominator, and {fixed} results carry a warning because the printed value "
     f"rounds the same way over 500 and over their graded count")

# 3. The reasoning-effort clause in metric_qualifier. Every result's qualifier ended with the
#    vendor's own spelling of the effort setting, so two systems at the same tier did not share a
#    qualifier and could not be compared: max, high and xhigh are three vendors' names for the top
#    of three settings. Comparisons key on metric, qualifier, unit and direction, so that blocked
#    the top-effort cross-system comparison the benchmark exists to make, and the paper's own
#    Table 2 is exactly that comparison. This is a comparison-blocking defect, not a wording
#    preference.
#
#    The tier is not inferred: Table D2 prints a Tier column (low, mid, top) for all 24 lanes, and
#    the captions of Tables G1 and G2 say "at top effort". The vendor label is not lost either; each
#    configuration carries it in its name, description, version, hyperparameters, provenance_note
#    and source_locator, so a reader of a result reaches both the tier and the vendor setting.
LOW = "; low reasoning tier, the lowest of this system's three settings"
MID = "; mid reasoning tier, the middle of this system's three settings"
TOP = "; top reasoning tier, the highest of this system's three settings"
# Longest suffixes first: the bare "; <label> reasoning effort" forms are substrings of the
# parenthesised ones, so the parenthesised forms must be replaced before them.
TIER_SUFFIXES = [
    ("; low reasoning effort (low of this system's three settings)", LOW),
    ("; high reasoning effort (mid of this system's three settings)", MID),
    ("; medium reasoning effort (mid of this system's three settings)", MID),
    ("; high reasoning effort (top of this system's three settings)", TOP),
    ("; max reasoning effort (top of this system's three settings)", TOP),
    ("; xhigh reasoning effort (top of this system's three settings)", TOP),
    # Tables G1 and G2 are top effort only, which both captions state.
    ("; high reasoning effort", TOP),
    ("; max reasoning effort", TOP),
    ("; xhigh reasoning effort", TOP),
]
retiered = {LOW: 0, MID: 0, TOP: 0}
for r in records:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    q = a["metric_qualifier"]
    for old, new in TIER_SUFFIXES:
        if q.endswith(old):
            a["metric_qualifier"] = q[: -len(old)] + new
            retiered[new] += 1
            break
    else:
        raise AssertionError(f"no effort clause recognised on {r['id']}: {q[-70:]!r}")
assert retiered == {LOW: 24, MID: 24, TOP: 176}, retiered
keys = {(r["attributes"]["metric"], r["attributes"]["unit"], r["attributes"]["metric_direction"],
         r["attributes"]["metric_qualifier"]) for r in records if r["kind"] == "result"}
note(f"effort qualifier: the vendor label replaced by the printed tier on all 224 results "
     f"({retiered[LOW]} low, {retiered[MID]} mid, {retiered[TOP]} top), cutting the distinct "
     f"comparability keys from 36 to {len(keys)} so that systems at one tier compare")

# 3. configuration_type. All 24 configurations carried "default", which is not a concept in
#    data/vocab/configuration-type.ttl, so npm run records -- add rejects the batch. The scheme
#    offers paper_evaluation ("a configuration of the paper's own method evaluated in that paper"),
#    reported_configuration ("as reported in a source, typically a comparator") and pipeline. None
#    fits: these are third-party systems run as subjects by a benchmark paper, neither the paper's
#    own method nor a quoted comparator. The field is optional, and the closest precedent in the
#    store leaves it unset for the same shape, agent harness plus LLM backend from a benchmark paper
#    (lit-agents-20261013-biomlbench-config-*). So it is removed rather than guessed.
dropped = 0
for r in records:
    if r["kind"] == "configuration":
        assert r["attributes"].pop("configuration_type", None) == "default", r["id"]
        dropped += 1
note(f"configuration_type \"default\" removed from {dropped} configurations: not a concept in the "
     f"vocabulary, and no existing concept fits a third-party system run as a benchmark subject")

# 3. Record the review on every result and claim. Status needs no change: the extractor had
#    already set source_checked on 752 of the 756 records, which notes.md contradicts ("every
#    record is needs_review") and which it had not earned at extraction time. After this pass the
#    status is true of those records, so it stands. The four evaluator records keep discovered:
#    they carry no source_locator, so there is no place in the paper against which their
#    descriptions could be said to have been checked.
reviewed = 0
for r in records:
    if r["kind"] in ("result", "claim"):
        r["attributes"]["review"] = dict(REVIEW)
        reviewed += 1
left = [r["id"] for r in records if r["status"] != "source_checked"]
assert all(r["kind"] == "evaluator" for r in records if r["id"] in left), left
note(f"review object written on {reviewed} results and claims; {len(left)} evaluator records left "
     f"at discovered because they carry no source_locator; no other status changed")

records.sort(key=lambda r: r["id"])
with open(PATH, "w") as out:
    for r in records:
        out.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
for line in log:
    print(line)
