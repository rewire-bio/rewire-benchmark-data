"""Write parts/use-case.jsonl for the phenotype-perturbation-selection refresh (2026-10-22)."""
import json, sys, glob, copy

WT = sys.argv[1]
B = f"{WT}/data/omics/use-case-refresh-phenotype-20261022"
UC = "use-case-phenotype-perturbation-selection"
UC_NAME = "Select perturbations for a defined cellular response"
AUTHOR = ("Drafted by the Claude (Opus 5.5) judgement agent in the evidence-pass workflow for issue #184 "
          "(batch data/omics/use-case-refresh-phenotype-20261022); no human review claimed.")

P_LOOP = "ucpheno-20261022-protocol-edwards2026-assaybench-loop-test-10x100"
P_AL = "pheno-20261022-qin2025-protocol-al-top200"
P_RMSE = "pheno-20261022-qin2025-protocol-downsampling-rmse"
S_LOOP = "ucpheno-20261022-source-edwards2026"
S_QIN = "pheno-20261022-qin2025-source-pmlr"

def find(path_glob, rid):
    for f in glob.glob(path_glob):
        for line in open(f):
            if f'"id":"{rid}"' in line or f'"id": "{rid}"' in line:
                return json.loads(line)
    raise SystemExit(f"missing {rid}")

# Every protocol judged must exist in a reviewed part.
parts = {}
for f in glob.glob(f"{B}/parts/*.jsonl"):
    if f.endswith("use-case.jsonl"):
        continue
    for line in open(f):
        r = json.loads(line)
        parts[r["id"]] = r
for pid in (P_LOOP, P_AL, P_RMSE, S_LOOP, S_QIN):
    assert parts[pid]["status"] == "source_checked", pid
for sid in (S_LOOP, S_QIN):
    assert not parts[sid]["attributes"].get("evidence_concerns"), sid

# ---------- use case: updated copy of the stored record ----------
uc = find(f"{WT}/data/entities/use-cases.jsonl", UC)
orig = copy.deepcopy(uc)
a = uc["attributes"]
for pid in (P_LOOP, P_AL, P_RMSE):
    uc["links"].append({"relation": "assessed_by", "target_id": pid})
old_gap = "No machine-learning method has been compared with random selection on the same data in the linked evidence."
gaps = [g for g in a["evidence_gaps"] if g != old_gap]
assert len(gaps) == len(a["evidence_gaps"]) - 1
gaps += [
    "Matched random comparisons are retrospective only. AssayBench-Loop replays 20 screens with one random draw and prints no uncertainty; NAIAD's uniform arm still ranks pairs with the model, so the yield of testing randomly chosen pairs is not reported.",
    "No prospective comparison of a model shortlist against random or conventional selection at the same budget.",
    "The retrospective comparisons (AssayBench-Loop, NAIAD) were run by the developers of one of the compared methods; no independent replication.",
    "Retrospective hits are each screen's own significance call. In AssayBench-Loop many recovered hits are common-essential genes, and the paper does not address whether the language models saw the test screens' publications in pre-training.",
    "Combination evidence covers four two-gene viability screens only, gives the model every single-gene effect, and counts predicted as well as measured pairs as found.",
]
a["evidence_gaps"] = gaps
for t in ["active learning", "adaptive experimental design", "combinatorial perturbation", "hit enrichment"]:
    if t not in a["search_terms"]:
        a["search_terms"].append(t)
a["collection_plan"]["next_step"] = (
    "Find or commission a prospective comparison of a model shortlist against random selection from the same candidate "
    "universe at the same budget, and a retrospective comparison run by someone other than the methods' developers. "
    "The 22 October 2026 pass found matched random comparisons only in retrospective replays (AssayBench-Loop, NAIAD). "
    "Obtain qualified scientific review."
)
a["evidence_checked"] = {
    "date": "2026-10-22",
    "cutoff_date": "2026-10-22",
    "records": [
        "data/omics/search-ledger.jsonl",
        "docs/reviews/use-cases/phenotype-perturbation-selection-2026-10-22.md",
    ],
}
# Pinned fields must not change, so existing reviewed judgements and the baseline stay active.
for k in ("status", "name", "description", "facets"):
    assert uc[k] == orig[k], k
for k in ("question", "decision", "inputs", "output", "exclusions", "setting", "clinical_scope", "intended_users"):
    assert a[k] == orig["attributes"][k], k

def judgement(rid, protocol, relevance, endpoint, rationale, description, constraints, limitations, locators, source_ids, headline=None):
    p = parts[protocol]
    attrs = {
        "field": f"links:assessed_by:{protocol}",
        "value": protocol,
        "relevance": relevance,
        "endpoint": endpoint,
        "rationale": rationale,
        "constraints": constraints,
        "limitations": limitations,
        "revision": 1,
        "reason": "Add relevance judgement for a protocol extracted in the 2026-10-22 refresh (issue #184). " + AUTHOR,
        "citation_locators": [{"source_id": s, "locator": l} for s, l in locators],
        "source_locator": "; ".join(f"{s}: {l}" for s, l in locators),
    }
    if headline:
        attrs["headline_metric"] = headline
    return {
        "id": rid, "kind": "claim",
        "name": f"Relevance of {p['name']} to \"{UC_NAME}\"",
        "description": description,
        "status": "needs_review", "facets": {}, "source_ids": source_ids,
        "links": [{"relation": "subject", "target_id": UC}],
        "attributes": attrs,
    }

loop_desc = ("The closest stored evidence to the use case's comparison question: every policy picks from the same gene pool for the same "
             "screens at the same 1,000-gene budget and is scored on hits found against a random policy on those screens. Proxy, because "
             "the screens are replayed with historical labels, a hit is each screen's own significance call, and the test screens were "
             "chosen with a performance floor for the best language model.")
j_loop = judgement(
    "use-case-mapping-phenotype-20261022-edwards2026-assaybench-loop", P_LOOP, "proxy",
    "Hit enrichment factor over the random expectation, fraction of each screen's hits found, normalised cumulative-hit AUC, shortfall "
    "and share of common-essential hits after 10 rounds of 100 genes, mean over 20 genome-wide CRISPR screens published after 2021, for "
    "53 configurations: one random draw, a prior-hit baseline, Screen-kNN, random forests, third-party adaptive design methods (BPMF, "
    "MAML, BioBO, Probability-of-Hit, Transformer + DAgger), language models used directly with and without hit labels, agent harnesses, "
    "and the authors' AssayFormer, AssayLLM and AssayLoop handoffs",
    loop_desc + " Every row, including the third-party methods, the language models and the random draw, was run by the authors of "
    "AssayFormer and AssayLoop with their own prompts and history format. It covers single genes in screens whose phenotype is set by "
    "each source study, not a response the user prespecifies, and no combinations.",
    loop_desc,
    [
        "Compare configurations only within this protocol; do not pool with the CPPC, NAIAD or AssayBench protocols. The test screens are drawn from AssayBench, so agreement with the AssayBench evaluations is not independent.",
        "Random is one draw of the random policy, not its expectation. EF is defined against the random expectation, so a random policy scores about 1 by construction; fraction of hits found and nAUC are the columns where the random row adds information.",
        "The rows without hit labels are the authors' label ablation under the same protocol inputs; read them against their labelled arm, not as a separate benchmark.",
        "EP-B, EP-S, EP-D, Vendi and pathway-overlap values are breadth diagnostics, not hit yield, and the three EP scopes are not comparable with each other.",
        "Inspect every linked evaluation's source locator and limitations before citing a result.",
    ],
    [
        "Retrospective: labels are historical screen calls, and the authors state the policies remain to be validated prospectively in a live experimental loop.",
        "20 test screens and means only: Table 1 and Supplementary Table 4 print no uncertainty, and the number of runs per row is unreported.",
        "Test screens were filtered for genome-wide coverage, at least 50 hits, hit rate below 15% and a best-LLM AnDCG@100 of at least 0.05, which favours screens whose hits a language model can name.",
        "The temporal split is relative to the 1,349 training screens; the paper does not say whether the test screens or their publications predate the language models' training data.",
        "Many recovered hits are DepMap common-essential genes (18.6% for the random draw, 99.1% for the prior-hit baseline), so part of any enrichment can reflect generic fitness genes rather than the screen's specific phenotype.",
        "Author-run: AssayFormer, AssayLLM and AssayLoop are the authors' methods, and the authors also ran every comparator; third-party rows are the authors' runs, not those methods' own published results.",
        "The random policy's sampling universe (the shared gene pool or each screen's library) is not stated.",
        "Preprint (arXiv v1), not peer reviewed.",
    ],
    [(S_LOOP, "Table 1 and caption; Supplementary Table 4; Methods 4.2 and 4.3; Appendix H; Discussion (limitations)")],
    [S_LOOP],
    headline="hit-enrichment-factor",
)

al_desc = ("The only stored evidence on choosing which gene combinations to test: acquisition strategies compared at a fixed number of "
           "measured pairs from a shared seed set. Proxy, because the count includes strong pairs the model only predicted, the truth is "
           "the 200 largest viability effects in the same screen, and the screens are replayed rather than tested.")
j_al = judgement(
    "use-case-mapping-phenotype-20261022-qin2025-al-top200", P_AL, "proxy",
    "Number of each screen's 200 strongest measured gene pairs that fall in the top 200 of the measured-plus-predicted ranking after "
    "four rounds of active learning (and by round, ensemble size and UCB weight), on four fully measured two-gene CRISPR viability "
    "screens (Norman, Simpson, Horlbeck K562, Horlbeck Jurkat), for NAIAD, RECOVER and GEARS under uniform, maximum-predicted-effect, "
    "UCB, uncertainty and mean-UCB acquisition",
    al_desc + " The use case's setting says combinations need their own protocol, and this is one. The uniform arm is NAIAD (or "
    "RECOVER) trained on randomly chosen pairs and still ranks every pair with the model, so it is a random-acquisition control, not "
    "the yield of testing randomly chosen pairs that the collection plan's random baseline would give.",
    al_desc,
    [
        "Cite Table 4 (three replicates with standard error) for round-4 comparisons. Table 2 and Table 3 are separate runs with no stated run count and differ from Table 4 by more than rounding.",
        "Compare only within one screen; the budget and the share of pairs in the top 200 differ by screen.",
        "Do not compare this count with AssayBench-Loop's fraction of hits found or with any count of tested hits.",
        "Do not treat the Uniform rows as the use case's random-selection baseline.",
        "Inspect every linked evaluation's source locator and limitations before citing a result.",
    ],
    [
        "Retrospective replay over already-measured screens; no new experiment.",
        "A pair counts as found when it is in the top 200 of the measured-plus-predicted ranking, whether or not it was measured.",
        "Viability phenotype only; 'strongest' is by magnitude with no sign or significance threshold.",
        "Budgets differ: 500 measured pairs of 6,328 for Norman, 2,500 of 95,703 to 147,658 for the other screens.",
        "The model is given every gene's single-gene effect, so combinations involving a gene with an unmeasured single effect are not covered.",
        "Author-reported: NAIAD is the authors' method, and they adapted and ran RECOVER (from drugs to genes) and GEARS (on synthetic expression input).",
        "At most three cross-fold replicates, which the paper does not define for active learning; Table 7 and Table 4 disagree by 0.4 on one Norman cell.",
    ],
    [(S_QIN, "Sections 4.3 and 5.3; Table 2; Table 3; Table 4; Tables 5, 7 and 8; Appendices C and D")],
    [S_QIN],
    headline="true-positive-count",
)

rmse_desc = ("Outside scope. Prediction error averaged over all held-out pairs measures how well combination effects are predicted, "
             "not which pairs to test under a budget; the same paper's active-learning protocol is linked separately for that. Recorded "
             "so these errors are not read as selection performance.")
j_rmse = judgement(
    "use-case-mapping-phenotype-20261022-qin2025-downsampling-rmse", P_RMSE, "outside_scope",
    "Test RMSE (x10^-2) of predicted two-gene viability on a 30% held-out set after training on subsamples in which each gene appears "
    "on average 4, 10 or 20 times, for NAIAD, RECOVER, GEARS, a linear model and an MLP (not shown as evidence)",
    rmse_desc, rmse_desc,
    ["Do not cite these RMSE values as evidence of which combinations to test."],
    [
        "Author-reported: the NAIAD authors ran every model, adapting RECOVER and GEARS to this setting.",
        "Training-set sizes per gene frequency are not printed with Table 1.",
    ],
    [(S_QIN, "Sections 4.2 and 5.2; Table 1; Table 6")],
    [S_QIN],
)

# ---------- summary: updated copy of the stored summary claim ----------
summ = find(f"{WT}/data/evidence/claims/*.jsonl", "use-case-summary-phenotype-perturbation-selection")
text = (
    "The evidence comes from one prospective challenge and two retrospective replays, and they point in different directions. "
    "In the Cancer Immunotherapy Data Science Challenge, scored prospectively in mouse T cells, the 20 original Challenge 2 submissions "
    "had a top-k overlap AUC of 0.452 to 0.566, with 17 of the 20 between 0.50 and 0.57; a random ordering is expected to score 0.5. "
    "That score is not a ROC AUC, and the genes it scores were drawn from the leading Challenge 1 nominations. In the follow-up, two "
    "nominated targets exceeded the Screen 1 targets on the immune checkpoint blockade objective; the source reports 61 nominations, 57 "
    "selected targets, 59 screen-2 genes and 50 perturbations passing quality control without reconciling them, so no success fraction "
    "follows. AssayBench-Loop replays 20 genome-wide CRISPR screens published after 2021, with each policy choosing 10 rounds of 100 "
    "genes. One random draw found 4.9% of each screen's hits on average (enrichment 1.04 over the random expectation). Language models "
    "used directly as the policy, with hit labels, reached enrichment of 1.39 to 4.81, BPMF 4.49, and the authors' combinations of a "
    "language model with their AssayFormer up to 5.67, finding 27.7% of hits. Many recovered hits are common-essential genes: 30.1% for "
    "that row, 18.6% for the random draw and 99.1% for a baseline that picks earlier screens' hits. The authors ran every row, and no "
    "uncertainty is printed. For two-gene combinations, NAIAD's replay of four viability screens counted how many of each screen's 200 "
    "strongest pairs the model ranked in its top 200 after four rounds: 143.0, 141.7, 99.7 and 150.0 when it acquired the pairs with the "
    "largest predicted effect, against 93.3, 70.3, 38.7 and 81.3 when it acquired pairs uniformly at random (means of three replicates). "
    "That count includes pairs the model predicted but never measured, and the uniform arm still uses the model's ranking, so it is not "
    "the yield of testing random pairs. The challenge and the replays differ in endpoint, setting and who ran them, so their results "
    "cannot be compared directly. No source compares a model shortlist with random selection prospectively at the same budget."
)
for ch in "—–→":
    assert ch not in text
sa = summ["attributes"]
new_sources = summ["source_ids"] + [S_LOOP, S_QIN]
summ = {
    "id": summ["id"], "kind": "claim", "name": summ["name"], "description": summ["description"],
    "status": "needs_review", "facets": {}, "source_ids": new_sources, "links": summ["links"],
    "attributes": {
        "field": "summary",
        "value": text,
        "source_locator": sa["source_locator"] + "; " + S_LOOP + ": Table 1, rows 'Random', 'GPT-5.6 Sol', 'BPMF [41]', 'Gemini-3.1-Pro → AssayFormer' and 'Prior hit baseline', "
            "columns 'EF', 'FH (%)' and '%ess (%)'; Supplementary Table 4, Base LLMs group, column 'EF'; "
            + S_QIN + ": Table 4, rows 'NAIAD MPE' and 'NAIAD Uniform'",
        "revision": 2,
        "reason": "Revised in the 2026-10-22 refresh (issue #184) to add the AssayBench-Loop and NAIAD evidence; the CPPC text is kept "
                  "as reviewed on 2026-10-10. " + AUTHOR,
    },
}

out = [uc, j_loop, j_al, j_rmse, summ]
with open(f"{B}/parts/use-case.jsonl", "w") as fh:
    for r in sorted(out, key=lambda r: r["id"]):
        fh.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print(len(out), "records")
