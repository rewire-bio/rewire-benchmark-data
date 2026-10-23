"""Reviewer edits to parts/use-case.jsonl (independent review of the use-case record, judgements and summary).

Run once from the worktree root: python3 data/omics/use-case-refresh-phenotype-20261022/review/use-case_apply.py
Asserts the drafted text before changing it, so a second run fails instead of editing twice.
Also writes an updated copy of the stored baseline claim (rationale corrected) into the part.
"""
import json

B = "data/omics/use-case-refresh-phenotype-20261022"
PART = f"{B}/parts/use-case.jsonl"
REVIEWED_AT = "2026-10-22T18:00:00Z"
REVIEWER_NOTE = ("Claude (Opus 5.5) use-case review agent in the evidence-pass workflow for issue #184, independent of the "
                 "agent that drafted these judgements and the summary; no human review claimed")
DATED_REVIEW = "docs/reviews/use-cases/phenotype-perturbation-selection-2026-10-22.md"
S_LOOP = "ucpheno-20261022-source-edwards2026"
P_LOOP = "ucpheno-20261022-protocol-edwards2026-assaybench-loop-test-10x100"
P_AL = "pheno-20261022-qin2025-protocol-al-top200"

recs = [json.loads(l) for l in open(PART)]
by = {r["id"]: r for r in recs}

parts = {}
for f in ("edwards2026assayloop", "qin2025naiad"):
    for l in open(f"{B}/parts/{f}.jsonl"):
        r = json.loads(l)
        parts[r["id"]] = r


def evaluations_on(protocol):
    ids = sorted(r["id"] for r in parts.values() if r["kind"] == "evaluation"
                 and any(l["relation"] == "assessment" and l["target_id"] == protocol for l in r["links"]))
    for i in ids:
        e = parts[i]
        assert e["status"] == "source_checked", i
        conf = next(l["target_id"] for l in e["links"] if l["relation"] == "system")
        assert parts[conf]["status"] == "source_checked", conf
        res = [r for r in parts.values() if r["kind"] == "result" and any(l["target_id"] == i for l in r["links"])]
        assert res and all(r["status"] == "source_checked" for r in res), i
    return ids


# --- AssayBench-Loop judgement -------------------------------------------------------------------
j = by["use-case-mapping-phenotype-20261022-edwards2026-assaybench-loop"]
a = j["attributes"]
loop_evals = evaluations_on(P_LOOP)
assert len(loop_evals) == 53
old = "Test screens were filtered for genome-wide coverage, at least 50 hits, hit rate below 15% and a best-LLM AnDCG@100 of at least 0.05, which favours screens whose hits a language model can name."
i = a["limitations"].index(old)
a["limitations"][i] = (old[:-1] + "; the authors say the benchmark is not an unbiased sample of genome-wide CRISPR screens.")
a["reviewed_evaluations"] = loop_evals
a["review"] = {
    "method": ["source-hash-verification", "scope-review", "ai-assisted-source-review"],
    "reviewer": ["claude"],
    "reviewer_note": REVIEWER_NOTE,
    "reviewed_at": REVIEWED_AT,
    "note": ("Proxy confirmed: same candidate pool, screens and 10 x 100 budget for every policy with a random policy on the same screens, "
             "but a retrospective replay of historical hit calls, test screens filtered with a best-LLM floor (Methods 4.2, Appendix A), "
             "and every row run by the AssayLoop authors. Re-hashed the pinned PDF and searched its text layer for a training-cutoff or "
             "contamination statement; none found, so the pre-training limitation stands. Endpoint and the 53 evaluations checked against "
             "the reviewed part; all 53 kept, none excluded. Reviewer appended the authors' Appendix A caveat to the screen-selection "
             "limitation. Headline metric hit-enrichment-factor kept (the authors' primary metric); it needs the proposed concept in "
             f"data/vocab/metric.ttl. See {DATED_REVIEW}."),
}
a["revision"] = a.get("revision", 1)

# --- NAIAD active-learning judgement --------------------------------------------------------------
j = by["use-case-mapping-phenotype-20261022-qin2025-al-top200"]
a = j["attributes"]
al_evals = evaluations_on(P_AL)
assert len(al_evals) == 120
old = "Viability phenotype only; 'strongest' is by magnitude with no sign or significance threshold."
i = a["limitations"].index(old)
a["limitations"][i] = ("Viability phenotype only, with no significance threshold. Appendix D ranks the 'top P values' without saying "
                       "whether by sign or magnitude, while MPE acquires the pairs with the highest absolute predicted effect (Appendix C).")
a["reviewed_evaluations"] = al_evals
a["review"] = {
    "method": ["source-hash-verification", "scope-review", "ai-assisted-source-review"],
    "reviewer": ["claude"],
    "reviewer_note": REVIEWER_NOTE,
    "reviewed_at": REVIEWED_AT,
    "note": ("Proxy confirmed: combination selection at a fixed number of measured pairs from a shared uniform seed set, but the count "
             "includes predicted pairs (Appendix D), the truth is the 200 strongest measured effects in the same screen, and the replay is "
             "retrospective. Uniform accepted as a random-acquisition control inside the model's pipeline (Section 5.3; Appendix C.5), "
             "not the use case's random-selection baseline. All 120 evaluations kept: Table 2/3 runs have null aggregation, which blocks "
             "automatic comparison with Table 4, and the one GEARS row carries its synthetic-input caveat. Reviewer corrected the "
             f"'strongest by magnitude' limitation, which Appendix D does not state. See {DATED_REVIEW}."),
}

# --- NAIAD downsampling RMSE (outside scope) ------------------------------------------------------
j = by["use-case-mapping-phenotype-20261022-qin2025-downsampling-rmse"]
a = j["attributes"]
assert a["relevance"] == "outside_scope" and "reviewed_evaluations" not in a
a["review"] = {
    "method": ["source-hash-verification", "scope-review"],
    "reviewer": ["claude"],
    "reviewer_note": REVIEWER_NOTE,
    "reviewed_at": REVIEWED_AT,
    "note": ("Outside scope confirmed: test RMSE over all held-out pairs (Sections 4.2 and 5.2, Tables 1 and 6) measures prediction "
             "accuracy, not which pairs to test under a budget. Kept with its assessed_by link, following the store's outside-scope "
             "precedent, so the values are not read as selection performance. No reviewed_evaluations, as for other outside-scope "
             f"judgements; the source is clean. See {DATED_REVIEW}."),
}

# --- Summary ---------------------------------------------------------------------------------------
s = by["use-case-summary-phenotype-perturbation-selection"]
a = s["attributes"]
v = a["value"]
edits = [
    ("The evidence comes from one prospective challenge and two retrospective replays, and they point in different directions.",
     "The evidence comes from one prospective challenge and two retrospective replays, which measure different things."),
    ("and the authors' combinations of a language model with their AssayFormer up to 5.67, finding 27.7% of hits. "
     "Many recovered hits are common-essential genes: 30.1% for that row,",
     "and the authors' handoffs from a language model to their AssayFormer up to 5.67, with the Gemini-3.1-Pro handoff finding 27.7% "
     "of hits. Many recovered hits are common-essential genes: 30.1% for that handoff,"),
    ("The authors ran every row, and no uncertainty is printed.",
     "Test screens were kept only if the best language model already passed a performance floor on them, and the paper does not say "
     "whether the models saw the screens' publications in training. The authors ran every row, and no uncertainty is printed."),
    ("The challenge and the replays differ in endpoint, setting and who ran them, so their results cannot be compared directly.",
     "The challenge's submissions scored close to a random ordering, while in both replays the leading model-guided policies "
     "scored above the random or uniform arm; the two differ in endpoint, candidate set, setting and who ran them, so their results cannot be compared "
     "directly."),
]
for o, n in edits:
    assert v.count(o) == 1, o
    v = v.replace(o, n)
a["value"] = v
old_loc = "Table 1, rows 'Random', 'GPT-5.6 Sol', 'BPMF [41]', 'Gemini-3.1-Pro → AssayFormer' and 'Prior hit baseline', columns 'EF', 'FH (%)' and '%ess (%)';"
assert a["source_locator"].count(old_loc) == 1
a["source_locator"] = a["source_locator"].replace(
    old_loc,
    "Table 1, rows 'Random', 'GPT-5.6 Sol', 'BPMF [41]', 'Gemini-3.1-Pro → AssayFormer', 'GPT-5.6 Sol → AssayFormer' and "
    "'Prior hit baseline', columns 'EF', 'FH (%)' and '%ess (%)'; Methods 4.2 and Appendix A (test-screen criteria);")
s["status"] = "source_checked"
a["review"] = {
    "method": ["independent-cell-check", "ai-assisted-source-review"],
    "method_note": ("Matched every outcome number with the printed_value of a source_checked result in the reviewed parts (AssayLoop "
                    "random, base-LLM, BPMF, handoff and prior-hit rows; NAIAD Table 4 MPE and Uniform) and the CPPC range with the 20 "
                    "stored Challenge 2 results (0.4517 to 0.5656, 17 between 0.50 and 0.57). Design figures (20 screens, 10 rounds of "
                    "100 genes, top 200, four rounds) checked against the reviewed protocol records. Checked that both cited new sources "
                    "are source_checked with no evidence_concerns, that author-run comparisons and truth-set limits are named, and that "
                    "nothing is recommended."),
    "reviewer": ["claude"],
    "reviewer_note": REVIEWER_NOTE + "; the reviewer corrected the text",
    "reviewed_at": REVIEWED_AT,
    "note": ("Revision 2 under the same ID. Reviewer resolved the 5.67 tie (Gemini-3.1-Pro and GPT-5.6 Sol handoffs) by naming the "
             "Gemini handoff the 27.7% and 30.1% belong to, added the best-LLM screen-selection floor and the unaddressed pre-training "
             "exposure, and replaced 'point in different directions' with an explicit, non-comparative description of the contrast. "
             f"Descriptive only; no execution, human scientific review or clinical validation. See {DATED_REVIEW}."),
}

# --- Baseline claim (updated copy of the stored, reviewed record) ---------------------------------
base = None
for l in open("data/evidence/claims/1.jsonl"):
    if l.startswith('{"id":"use-case-baseline-phenotype-perturbation-selection"'):
        base = json.loads(l)
assert base and base["id"] not in by
ba = base["attributes"]
old = ("No evidence linked to this use case scores it: the CPPC protocols measure submitted methods only, and the benchmark's ranking "
       "metric only takes 0.5 as the value expected from a random ranking.")
assert ba["rationale"].endswith(old)
ba["rationale"] = ba["rationale"].replace(old, (
    "Among the evidence linked to this use case, only the retrospective AssayBench-Loop replay scores it, as one random draw on the same "
    "screens and budget as the other policies; the CPPC protocols measure submitted methods only, and the challenge's ranking metric "
    "only takes 0.5 as the value expected from a random ranking. NAIAD's uniform arm still ranks pairs with the model, so it is not "
    "this baseline."))
ba["review"] = {
    "method": ["source-hash-verification", "automated-source-review"],
    "reviewer": ["claude"],
    "reviewer_note": REVIEWER_NOTE + "; the reviewer corrected the rationale",
    "reviewed_at": REVIEWED_AT,
    "note": ("Rationale updated in the 2026-10-22 refresh (issue #184): the earlier text said no linked evidence scores random "
             "selection, which stops being true once the AssayBench-Loop judgement is active (its Random configuration is "
             "tgtval-20261009-method-random-selection). Value, method_ids and source_ids unchanged; the 2026-10-12 review "
             f"(docs/reviews/use-cases/baselines-2026-10-12.md) still covers them. See {DATED_REVIEW}."),
}
recs.append(base)

for jid in ("use-case-mapping-phenotype-20261022-edwards2026-assaybench-loop",
            "use-case-mapping-phenotype-20261022-qin2025-al-top200",
            "use-case-mapping-phenotype-20261022-qin2025-downsampling-rmse"):
    assert by[jid]["status"] == "needs_review"
    by[jid]["status"] = "source_checked"

with open(PART, "w") as fh:
    for r in sorted(recs, key=lambda r: r["id"]):
        fh.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(len(recs), "records;", len(loop_evals), "AssayLoop and", len(al_evals), "NAIAD evaluations reviewed")
