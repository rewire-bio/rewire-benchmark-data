"""Build the Qin et al. 2025 (NAIAD, PMLR 267) part from the pinned PDF's text layer.

Usage: python3 -I qin2025naiad.py <pdftotext -layout text of qin25g.pdf> <out.jsonl>

The text layer is made with `pdftotext -layout qin25g.pdf` from the PDF whose SHA-256 is
SHA below. Every table cell is read from the text layer; row labels, column counts and the
number of rows are asserted, so a different layer fails rather than shifting values.
Tables 2 and 3 are also checked against each other: marginal gain (Appendix D) is
(P4 - P0) / 4, and every row of one dataset must imply the same P0.
"""
import json
import re
import sys
from fractions import Fraction

SHA = "983b2da8aed78f0aced27053301c15f0f67ebd0fac706435bb6800e309dd64eb"
URL = "https://raw.githubusercontent.com/mlresearch/v267/main/assets/qin25g/qin25g.pdf"
PAGE = "https://proceedings.mlr.press/v267/qin25g.html"
RETRIEVED = "2026-10-22T13:57:27Z"
P = "pheno-20261022-qin2025"
SRC = f"{P}-source-pmlr"
FACETS = {"areas": ["cells-tissues"], "contexts": ["research"]}
NOTE_WHO = "Claude (Opus 5.5) extraction agent; no human review claimed. Extraction only, not yet independently reviewed."

DATASETS = ["Norman", "Simpson", "Horlbeck K562", "Horlbeck Jurkat"]
DKEY = {"Norman": "norman2019", "Simpson": "simpson2023", "Horlbeck K562": "horlbeck2018-k562",
        "Horlbeck Jurkat": "horlbeck2018-jurkat"}
NUM = r"\d+(?:\.\d+)?"
CELL = re.compile(rf"({NUM}) \(({NUM})\)")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def table_block(lines, caption, n_after=40):
    idx = [i for i, l in enumerate(lines) if l.strip().startswith(caption)]
    assert len(idx) == 1, (caption, idx)
    return lines[idx[0] + 1: idx[0] + 1 + n_after]


def find_row(block, pattern, count=1):
    rx = re.compile(r"^\s*" + pattern + r"\s+")
    rows = [l for l in block if rx.match(l)]
    assert len(rows) >= count, (pattern, rows)
    return [rx.sub("", r, count=1) for r in rows[:count]]


def plain_values(rest, n):
    toks = rest.split()
    vals = toks[:n]
    for v in vals:
        assert re.fullmatch(NUM, v), (rest, vals)
    return vals


def se_cells(rest, n):
    cells = CELL.findall(rest)
    assert len(cells) == n, (rest, cells)
    return cells


# ---------------------------------------------------------------- parse
def parse(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    t = {}
    # Table 2 and 3: four acquisition rows, four datasets, no uncertainty.
    for tab, cap in (("2", "Table 2. Number of top 200"), ("3", "Table 3. Marginal gain")):
        block = table_block(lines, cap, 12)
        assert any(re.match(r"^\s*Norman\s+Simpson\s+Horlbeck K562\s+Horlbeck Jurkat", l) for l in block), tab
        t[tab] = {r: plain_values(find_row(block, re.escape(r))[0], 4)
                  for r in ["Uniform", "MPE", "UCB", "Uncertainty"]}
    # Consistency of Tables 2 and 3: (P4 - P0)/4 with one P0 per dataset.
    for j, d in enumerate(DATASETS):
        p0 = {Fraction(t["2"][r][j]) - 4 * Fraction(t["3"][r][j]) for r in t["2"]}
        assert len(p0) == 1, (d, p0)
    # Table 4: model x method rows with SE.
    block = table_block(lines, "Table 4. Number of top 200", 10)
    t["4"] = {}
    for m in ["NAIAD", "RECOVER"]:
        for a in ["Uniform", "MPE", "UCB"]:
            t["4"][(m, a)] = se_cells(find_row(block, rf"{m}\s+{a}")[0], 4)
    assert len(t["4"]) == 6
    # Table 5: ensemble size rows; columns MPE, Uniform for each dataset.
    block = table_block(lines, "Table 5. Number of top 200", 8)
    t["5"] = {k: se_cells(find_row(block, k)[0], 8) for k in ["1", "3", "5", "7"]}
    # Table 7: Norman only, rounds 0-4.
    block = table_block(lines, "Table 7. Number of top 200", 8)
    t["7"] = {}
    for m, a in [("NAIAD", "MPE"), ("RECOVER", "MPE"), ("GEARS", "MPE"), ("NAIAD", "Uniform")]:
        t["7"][(m, a)] = se_cells(find_row(block, rf"{m}\s+{a}")[0], 5)
    # Table 8: beta rows plus Uniform.
    block = table_block(lines, "Table 8. Number of top 200", 16)
    t["8"] = {}
    for b in ["0", "0.25", "0.5", "0.75", "1", "1.5", "2", "5", "10", "25", "Uniform"]:
        t["8"][b] = se_cells(find_row(block, re.escape(b))[0], 4)
    # Table 1 (gene frequency 4 and 20) and Table 6 (gene frequency 10): RMSE x 10^-2.
    models = ["Linear", "MLP", "GEARS", "RECOVER", "NAIAD"]
    block = table_block(lines, "Table 1. Root mean square error", 14)
    t["1"] = {}
    for m in models:
        rows = [l for l in block if re.match(rf"^\s*(?:(?:4|20)\s+)?{m}\s+{NUM} \(", l)]
        assert len(rows) == 2, (m, rows)
        for freq, row in zip(["4", "20"], rows):
            rest = re.sub(rf"^\s*(?:(?:4|20)\s+)?{m}\s+", "", row)
            t["1"][(freq, m)] = se_cells(rest, 4)
    gf = [l for l in block if re.match(r"^\s*(4|20)\s+GEARS", l)]
    assert [l.split()[0] for l in gf] == ["4", "20"], gf
    block = table_block(lines, "Table 6. RMSE of five models", 8)
    t["6"] = {}
    for m in models:
        rows = [l for l in block if re.match(rf"^\s*(?:10\s+)?{m}\s+{NUM} \(", l)]
        assert len(rows) == 1, (m, rows)
        t["6"][("10", m)] = se_cells(re.sub(rf"^\s*(?:10\s+)?{m}\s+", "", rows[0]), 4)
    return t


# ---------------------------------------------------------------- records
def review(note):
    return {"method": ["source-hash-verification", "pdf-text-parse"], "reviewer": ["claude"],
            "reviewer_note": NOTE_WHO, "date": "2026-10-22", "artifact_sha256": SHA, "retrieval_url": URL,
            "method_note": "Read from the pdftotext -layout text layer of the pinned PDF by "
                           "data/omics/use-case-refresh-phenotype-20261022/extract/qin2025naiad.py, which asserts "
                           "row labels, cell counts per row and the Table 2/Table 3 arithmetic.",
            "note": note}


def rec(id_, kind, name, description, attributes, links=(), facets=None):
    return {"id": id_, "kind": kind, "name": name, "description": description, "status": "needs_review",
            "facets": FACETS if facets is None else facets, "source_ids": [SRC], "links": list(links),
            "attributes": attributes}


def build(t):
    out = []
    add = out.append
    # Source
    add(rec(SRC, "source",
            "Qin et al. 2025, Active Learning for Efficient Discovery of Optimal Combinatorial Perturbations (ICML 2025, PMLR 267)",
            "NAIAD, an active-learning framework for choosing which two-gene combinations to measure next, evaluated by replaying four fully measured combinatorial CRISPR viability screens.",
            {"url": PAGE, "artifact_url": URL, "retrieval_url": URL,
             "version": "Proceedings of the 42nd ICML, PMLR 267:50363-50383, 2025; proceedings PDF qin25g.pdf. The arXiv preprint 2411.12010 was not read.",
             "venue": "Proceedings of the 42nd International Conference on Machine Learning (PMLR 267)", "year": 2025,
             "retrieved_at": RETRIEVED, "artifact_sha256": SHA, "publication_status": "peer_reviewed",
             "media_type": "application/pdf",
             "code_url": "https://github.com/NeptuneBio/NAIAD/tree/9207e9e855e865160a196a6989392f6db622b0d6",
             "code_licence": "Apache-2.0 according to the GitHub repository metadata on 2026-10-22; the repository contents were not read.",
             "extraction_method": "pdftotext -layout text layer, parsed by extract/qin2025naiad.py",
             "archive_note": "Not archived in the batch: the PDF prints 'Copyright 2025 by the author(s)' and no reuse licence. The artifact_sha256 pins the bytes that were read; the text layer is kept outside the repository.",
             "source_locator": "Full artifact; per-record locators on each record",
             "limitations": [
                 "Tables 2 and 3 print no uncertainty and do not say how many replicates they summarise. Their values differ from Table 4 for the same model and acquisition function by more than rounding (MPE on Horlbeck Jurkat: 161 in Table 2, 150.0 (4.0) in Table 4).",
                 "Table 7 and Table 4 agree for NAIAD MPE and RECOVER MPE on Norman at round 4 but differ for NAIAD Uniform (93.7 (0.7) in Table 7, 93.3 (0.7) in Table 4).",
                 "Table 8 prints Uniform on Norman as 93.3 (2.9), the same mean as Table 4 with a different standard error.",
                 "The ensemble size behind Tables 2 to 4, 7 and 8 is not stated; no row of Table 5 equals the Table 4 values.",
                 "Figures 3, 4, 5, 7, 8 and 9 print no values; the drug-combination results (Section 5.4, Figure 5) are not extracted."],
             "missing_metadata": {"doi": {"reason": "unreported", "note": "PMLR proceedings carry no DOI; the arXiv DOI belongs to the preprint, which was not read."},
                                  "licence": {"reason": "unreported", "note": "The PDF prints 'Copyright 2025 by the author(s)' and no licence."}},
             "review": review("Retrieved and hashed by the extraction agent; hash matches the search pass digest.")},
            facets=FACETS))

    # Methods
    methods = {
        "naiad": ("NAIAD", "Active-learning framework that predicts the phenotype of a two-gene perturbation from over-parameterised single-gene effects plus learned gene embeddings whose size grows with the training set, and uses an ensemble of these models with an acquisition function to choose the next combinations to measure.",
                  ["supervised_machine_learning"], "Section 3.1 (Eq. 1), Section 3.3, Appendix C", "Code at github.com/NeptuneBio/NAIAD (Software and Data)"),
        "recover": ("RECOVER", "Sequential model optimisation framework for combination screens that combines single-perturbation representations with a bilinear operator, predicts the non-additive (Bliss) component, and estimates uncertainty with deep ensembles to choose the next combinations.",
                    ["supervised_machine_learning"], "Section 2 (RECOVER, Bertin et al. 2023); Appendix B 'RECOVER adaptation'", None),
        "linear-pair": ("Linear regression on single-gene effects", "Linear regression that predicts a two-gene perturbation's phenotype from the two single-gene effects, with two coefficients and an intercept.",
                        ["conventional_pipeline"], "Appendix B 'Linear model'", None),
        "mlp-gene-embedding": ("MLP on summed gene embeddings", "Multi-layer perceptron that sums 128-dimensional learned embeddings of the two perturbed genes and projects the sum to a single phenotype value.",
                               ["supervised_machine_learning"], "Appendix B 'Multi-layer perceptron (MLP)'", None),
    }
    mid = {}
    for k, (name, desc, mt, loc, access) in methods.items():
        mid[k] = f"{P}-method-{k}"
        a = {"reported_name": name.split(" ")[0] if k in ("naiad", "recover") else name, "entity_level": "method",
             "source_locator": loc,
             "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; settings are on configurations"}},
             "provenance_note": {"naiad": "The paper's own method.",
                                 "recover": "Described from Qin et al. 2025, who adapted RECOVER (Bertin et al. 2023) from drugs to genes; the RECOVER paper was not read.",
                                 "linear-pair": "Comparator defined by Qin et al. 2025 for this paper.",
                                 "mlp-gene-embedding": "Comparator defined by Qin et al. 2025 for this paper."}[k],
             "review": review("Description written from the cited section.")}
        if access:
            a["access"] = access
        add(rec(mid[k], "method", name, desc, a, facets={**FACETS, "method_types": mt}))
    mid["gears"] = "catalog-model-gears"  # existing store record, reused

    # Datasets
    dinfo = {
        "Norman": ("Norman et al. 2019 combinatorial CRISPRa in K562, gene-level viability (as processed by Qin et al. 2025)", "CRISPR activation", "K562", 112, 6328),
        "Simpson": ("Simpson et al. 2023 combinatorial CRISPRi in K562, gene-level viability (as processed by Qin et al. 2025)", "CRISPR interference", "K562", 543, 147658),
        "Horlbeck K562": ("Horlbeck et al. 2018 combinatorial CRISPRi in K562, gene-level viability (as processed by Qin et al. 2025)", "CRISPR interference", "K562", 448, 100576),
        "Horlbeck Jurkat": ("Horlbeck et al. 2018 combinatorial CRISPRi in Jurkat T cells, gene-level viability (as processed by Qin et al. 2025)", "CRISPR interference", "Jurkat T cells", 437, 95703),
    }
    did = {}
    for d, (name, mod, cell, genes, combos) in dinfo.items():
        did[d] = f"{P}-data-{DKEY[d]}-viability"
        add(rec(did[d], "dataset", name,
                f"Symmetric pairwise {mod} screen in {cell}: {combos:,} unique two-gene combinations of {genes} genes, each scored as gene-level log-fold change in cell viability against negative controls.",
                {"version": "Gene-level viability (gamma) computed by Qin et al. 2025, Appendix A.1, from the published screen",
                 "assay": f"Bulk combinatorial {mod} screen; phenotype is the log-fold change in cell viability relative to negative-control treatments, averaged over all guide pairs targeting a gene pair",
                 "context": cell, "species": "Homo sapiens",
                 "population": f"{combos:,} unique gene combinations involving {genes} genes", "total": combos,
                 "label_semantics": "Continuous viability effect per gene pair. Single-gene effects come from guide pairs of one targeting and one non-targeting guide.",
                 "scope_note": "Used both as the candidate pool and as ground truth: the 200 strongest measured pairs in the whole screen are the targets of the active-learning protocol.",
                 "source_locator": "Appendix A.1; Section 4.2 (combination counts)",
                 "missing_metadata": {"accession": {"reason": "unreported", "note": "The paper cites the screens but prints no accession or processed-file location."}},
                 "review": review("Transcribed from Appendix A.1.")}))

    # Protocols
    al = f"{P}-protocol-al-top200"
    add(rec(al, "protocol",
            "Retrospective active learning on a fully measured two-gene CRISPR viability screen: top-200 gene pairs found by round 4",
            "Starting from a uniformly sampled seed set shared by all acquisition functions, a model ensemble is retrained each round on the measured pairs acquired so far and an acquisition function picks the next batch; the score counts how many of the screen's 200 strongest measured pairs are among the 200 strongest of the measured-plus-predicted values.",
            {"protocol": "Round 0 trains on a uniformly sampled seed set (100 pairs for Norman, 500 for Simpson and both Horlbeck screens). In each of 4 further rounds the trained ensemble predicts every unmeasured pair, the acquisition function selects 100 (Norman) or 500 (others) more pairs whose measured values are revealed from the screen, and the model is retrained. Acquisition functions: Uniform, Maximum Predicted Effect (MPE), Upper Confidence Bound (UCB, residual from a linear model plus ensemble standard deviation, kappa = 1), Uncertainty (ensemble standard deviation) and Mean-UCB (alpha times ensemble mean plus beta times ensemble standard deviation).",
             "procedure": "Fraction Discovered (Appendix D): after training in round i, predictions for all unseen pairs are concatenated with the measured values of the seen pairs to form X_i; X_i,P is the top P values of X_i, Y_i,P the top P measured values across all samples, and P_i = |X_i,P ∩ Y_i,P|. Tables 2, 4, 5, 7 and 8 print P_i at P = 200; Table 3 prints the marginal gain (P_4 - P_0)/4.",
             "version": "Qin et al. 2025, PMLR 267, Sections 4.3 and 5.3, Appendices C and D",
             "metric": "true-positive-count", "metric_direction": "higher", "unit": "count",
             "unit_detail": "gene pairs, out of the 200 strongest measured pairs",
             "metric_definition": "P_200 = number of the 200 strongest measured gene pairs in the whole screen that are among the 200 strongest values of the combined set of measured (acquired) and predicted (unacquired) pairs. Pairs counted as found need not have been measured.",
             "denominator": 200,
             "task": "Choose which two-gene combinations to measure next so that the strongest combinations are identified with few measurements",
             "selection": "Candidate pool is every pair in the screen; the seed set is drawn uniformly and shared by all acquisition functions",
             "replicates": "Tables 4, 5, 7 and 8: three cross-fold replicates with standard error printed. Tables 2 and 3: not stated.",
             "random_seeds": "Not stated",
             "scope_note": "Retrospective replay over already-measured screens; no new experiment is run. 'Strongest' is not defined by sign: Appendix C.2 says MPE selects the highest absolute predicted effects, and Appendix D says top P values.",
             "limitations": [
                 "A pair counts as discovered when it is in the top 200 of the measured-plus-predicted ranking, so the count mixes pairs actually measured with pairs only predicted; it is not the number of strong pairs among those tested.",
                 "Ground truth is the 200 strongest measured viability effects in the same screen, not an independently confirmed phenotype or a significance threshold; the 200 are 3.2% of Norman's 6,328 pairs and 0.14% to 0.21% of the other screens.",
                 "The measurement budget differs by screen (500 pairs of 6,328 for Norman; 2,500 of 95,703 to 147,658 for the others).",
                 "Single-gene effects of every gene are available to the model throughout.",
                 "All values come from the NAIAD authors, who also adapted RECOVER and GEARS to this setting.",
                 "The paper does not define a cross-fold replicate for the active-learning experiments."],
             "source_locator": "Section 4.3; Section 5.3; Appendix C; Appendix D 'Fraction Discovered' and 'Marginal Gain'",
             "publication_status": "peer_reviewed",
             "review": review("Protocol text transcribed from Sections 4.3 and 5.3 and Appendices C and D.")},
            links=[{"relation": "uses_data", "target_id": did[d]} for d in DATASETS]))
    ds = f"{P}-protocol-downsampling-rmse"
    add(rec(ds, "protocol",
            "Combination phenotype prediction from small training sets: test RMSE at fixed average gene frequency",
            "Models are trained on a subsample of measured gene pairs sized so that each gene is seen on average 4, 10 or 20 times, and scored by RMSE of predicted pair viability on a 30% held-out test set.",
            {"protocol": "Training sets are subsampled so that Gene Occurrence = 2N/M (N training combinations, M unique genes) is about 4, 10 or 20; 10% of each dataset is used for validation and 30% for testing. Root mean squared error of predicted viability on the test pairs.",
             "version": "Qin et al. 2025, PMLR 267, Sections 4.2 and 5.2; Table 1; Appendix Table 6",
             "metric": "root-mean-squared-error", "metric_direction": "lower", "unit": "unitless",
             "unit_detail": "printed x 10^-2 (column header 'Dataset RMSE (×10−2)'), RMSE of gene-level log-fold-change viability",
             "replicates": "Three cross-fold replicates; standard error printed",
             "task": "Predict the viability effect of unseen two-gene perturbations",
             "limitations": ["Training sizes per dataset for each gene frequency are not printed with Table 1; Table 9 lists an approximate training-set size per average times seen, which may be the same schedule.",
                             "This is prediction accuracy over all held-out pairs, not selection of pairs to test."],
             "source_locator": "Section 4.2; Section 5.2; Table 1 caption; Table 6 caption",
             "publication_status": "peer_reviewed",
             "review": review("Protocol text transcribed from Sections 4.2 and 5.2.")},
            links=[{"relation": "uses_data", "target_id": did[d]} for d in DATASETS]))

    # Configurations
    cfg = {}
    cname = {}

    def config(key, name, of, reported, selection, mt, own, params, loc, desc):
        cid = f"{P}-config-{key}"
        a = {"reported_name": reported, "configuration_type": "paper_evaluation" if own else "reported_configuration",
             "foundation_model_eligible": False,
             "version": "As run by Qin et al. 2025 (PMLR 267); no release or commit is printed",
             "access_reuse": "NAIAD code at https://github.com/NeptuneBio/NAIAD (Apache-2.0 per GitHub metadata); the commit used for the paper is not stated" if of == mid["naiad"]
             else "Run by Qin et al. 2025; their code for this comparator is not separately identified",
             "parameters": params, "source_locator": loc,
             "provenance_note": "The paper's own method." if own and of == mid["naiad"] else "Configuration run by Qin et al. 2025 in this comparison.",
             "review": review("Settings transcribed from the cited sections.")}
        if selection:
            a["selection"] = selection
        cfg[key] = cid
        cname[key] = name
        add(rec(cid, "configuration", name, desc, a, links=[{"relation": "configuration_of", "target_id": of}],
                facets={**FACETS, "method_types": mt}))

    acq = {"Uniform": "Uniform acquisition: pairs added each round are sampled uniformly (Mean-UCB with alpha = beta = 0, Appendix C.5)",
           "MPE": "Maximum Predicted Effect acquisition: pairs with the highest absolute ensemble-mean prediction (Appendix C.2)",
           "UCB": "UCB acquisition from RECOVER: residual from a linear model plus kappa times ensemble standard deviation, kappa = 1 (Appendix C.4)",
           "Uncertainty": "Uncertainty acquisition: pairs with the highest ensemble standard deviation (Appendix C.1)"}
    sl = "seed set of uniformly sampled pairs shared by all acquisition functions"
    for a_ in ["Uniform", "MPE", "UCB", "Uncertainty"]:
        config(f"naiad-{slug(a_)}", f"NAIAD with {a_} acquisition", mid["naiad"], f"NAIAD, {a_}", acq[a_],
               ["supervised_machine_learning"], True,
               f"NAIAD ensemble with adaptive gene-embedding size (Table 9 schedule), retrained each round; {sl}. Ensemble size not stated.",
               "Tables 2 to 4 row labels; Section 5.3; Appendix C", f"NAIAD ensemble retrained each round, with the next pairs chosen by {a_} acquisition.")
    for a_ in ["Uniform", "MPE", "UCB"]:
        config(f"recover-{slug(a_)}", f"RECOVER (gene adaptation) with {a_} acquisition", mid["recover"], f"RECOVER, {a_}", acq[a_],
               ["supervised_machine_learning"], False,
               "RECOVER adapted to genes: bilinear projection of 128-dimensional gene embeddings, trained on gene-Bliss scores and converted back to viability; learning rate 0.1 (Appendix B, F).",
               "Table 4 and Table 7 row labels; Appendix B 'RECOVER adaptation'",
               f"RECOVER adapted to gene pairs and retrained each round, with the next pairs chosen by {a_} acquisition.")
    config("gears-mpe", "GEARS with MPE acquisition", mid["gears"], "GEARS, MPE", acq["MPE"], ["specialist"], False,
           "GEARS with the original settings for cell-viability prediction; for bulk screens without single-cell data, synthetic Perturb-seq matrices with each gene drawn from N(0, 1) were generated (Appendix B); package default hyperparameters (Appendix F).",
           "Table 7 row 'GEARS MPE'; Appendix B 'GEARS'", "GEARS retrained each round on a bulk viability screen, with the next pairs chosen by MPE acquisition.")
    for n in ["1", "3", "5", "7"]:
        for a_ in ["MPE", "Uniform"]:
            config(f"naiad-{slug(a_)}-ensemble-{n}", f"NAIAD with {a_} acquisition, ensemble of {n}", mid["naiad"], f"NAIAD, {a_}, ensemble size {n}",
                   acq[a_], ["supervised_machine_learning"], True,
                   f"NAIAD ensemble of {n} model{'s' if n != '1' else ''} with adaptive gene-embedding size; {sl}.",
                   f"Table 5, row '{n}', columns '{a_}'", f"NAIAD ensemble of {n} retrained each round, with the next pairs chosen by {a_} acquisition.")
    for b in ["0", "0.25", "0.5", "0.75", "1", "1.5", "2", "5", "10", "25"]:
        config(f"naiad-mean-ucb-beta-{slug(b)}", f"NAIAD with Mean-UCB acquisition, beta = {b}", mid["naiad"], f"NAIAD, Mean-UCB, β = {b}",
               f"Mean-UCB acquisition: score = alpha x ensemble mean + beta x ensemble standard deviation, beta = {b} (Appendix C.5); alpha for Table 8 is not stated",
               ["supervised_machine_learning"], True, f"NAIAD ensemble with adaptive gene-embedding size; {sl}.",
               f"Table 8, row '{b}'; Appendix C.5", f"NAIAD ensemble retrained each round, with the next pairs chosen by Mean-UCB acquisition at beta = {b}.")
    pred = {"Linear": ("linear-pair", "Linear regression on single-gene effects", ["conventional_pipeline"], True,
                       "Three parameters: two coefficients for the single-gene effects and an intercept (Appendix B)."),
            "MLP": ("mlp-gene-embedding", "MLP on summed gene embeddings", ["supervised_machine_learning"], True,
                    "128-dimensional gene embeddings summed and projected to one value; learning rate 0.01, batch size 1024, linear schedule with 10% warm-up, weight decay 0 (Appendix B, F)."),
            "GEARS": ("gears", "GEARS", ["specialist"], False,
                      "Original settings for cell-viability prediction; synthetic Perturb-seq matrices with each gene drawn from N(0, 1) for bulk screens (Appendix B); package default hyperparameters (Appendix F)."),
            "RECOVER": ("recover", "RECOVER (gene adaptation)", ["supervised_machine_learning"], False,
                        "Bilinear projection of 128-dimensional gene embeddings, trained on gene-Bliss scores and converted back to viability; learning rate 0.1 (Appendix B, F)."),
            "NAIAD": ("naiad", "NAIAD", ["supervised_machine_learning"], True,
                      "Adaptive gene-embedding size by average gene frequency (Table 9); learning rate 0.01, batch size 1024, linear schedule with 10% warm-up, weight decay 0 (Appendix F).")}
    for m, (k, name, mt, own, params) in pred.items():
        config(f"{k}-prediction", f"{name}, trained once on a downsampled set", mid[k], m, None, mt, own and k == "naiad",
               params, f"Table 1 and Table 6, row '{m}'; Appendix B",
               f"{name} trained once on a subsample of measured pairs to predict the viability of held-out pairs.")
    # Linear and MLP were built by the paper's authors: author_reported, but they are comparators.
    # ---------------------------------------------------------------- evaluations and results
    budgets = {"Norman": "100 uniformly sampled seed pairs, then 100 acquired pairs in each of 4 rounds (500 measured pairs at round 4)",
               "Simpson": "500 uniformly sampled seed pairs, then 500 acquired pairs in each of 4 rounds (2,500 measured pairs at round 4)"}
    budgets["Horlbeck K562"] = budgets["Horlbeck Jurkat"] = budgets["Simpson"]
    pops = {d: f"{dinfo[d][4]:,} two-gene combinations of {dinfo[d][3]} genes" for d in DATASETS}
    q_round = "the screen's 200 strongest measured gene pairs found among the 200 strongest measured-plus-predicted values, round {r} of active learning"
    counts = {"evaluation": 0, "result": 0}

    def evaluation(group, gname, key, d, protocol, origin, aggregation, adaptation, loc, extra=None, missing=None):
        eid = f"{P}-eval-{group}-{key}-{DKEY[d]}"
        is_al = protocol == al
        comp = {"protocol_id": protocol,
                "dataset_version": "Gene-level viability as processed in Qin et al. 2025 Appendix A.1",
                "split": "No held-out split; the whole screen is both the candidate pool and the ground truth" if is_al
                else "Downsampled training set; 10% validation and 30% test",
                "population": pops[d],
                "inputs": "Single-gene viability effects of every gene, plus the measured viability of pairs acquired so far" if is_al
                else "Single-gene viability effects and the measured viability of the training pairs",
                "adaptation": adaptation,
                "metric_implementation": "P_i = |X_i,P ∩ Y_i,P| at P = 200 (Appendix D)" if is_al else "RMSE of predicted pair viability on the test set",
                "aggregation": aggregation,
                "budget": budgets[d] if is_al else None}
        a = {"origin": origin, "protocol": protocol, "version": "Qin et al. 2025, PMLR 267 proceedings PDF",
             "comparison": comp, "evaluation_group_id": f"qin2025-{group}", "evaluation_group_name": gname,
             "retrospective": True, "source_locator": loc,
             "review": review("Evaluation fields transcribed from the table caption and Sections 4.2 to 5.3.")}
        mm = dict(missing or {})
        if aggregation is None:
            mm["aggregation"] = {"reason": "unreported", "note": "The table prints no error and does not state how many runs or replicates it summarises."}
        if not is_al:
            mm["budget"] = {"reason": "inapplicable", "note": "Single training run on a fixed subsample; no acquisition budget."}
        if mm:
            a["missing_metadata"] = mm
        if extra:
            a.update(extra)
        if origin == "independent_paper":
            a["limitations"] = ["Run by the NAIAD authors on their own adaptation of this method, not by its developers."]
        counts["evaluation"] += 1
        system = cfg[key]
        add(rec(eid, "evaluation", f"{cname[key]} on {d} ({gname})", "Published comparison; transcribed, not reproduced.", a,
                links=[{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
                       {"relation": "data", "target_id": did[d]}]))
        return eid

    def result(eid, suffix, printed, numeric, metric, qualifier, unit, unit_detail, direction, loc, se=None, note=""):
        a = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": direction, "unit": unit,
             "unit_detail": unit_detail, "printed_value": printed, "numeric_value": numeric, "source_locator": loc,
             "review": review(note or "Value read from the text layer; not yet checked by a separate reviewer.")}
        if se is None:
            a["missing_metadata"] = {"uncertainty": {"reason": "unreported", "note": "The table prints no error and does not state the number of runs."}}
        else:
            a["uncertainty"] = {"type": "standard_error", "value": se, "printed": f"({se})", "n": 3,
                                "scope": "three cross-fold replicates", "note": "Caption: error is SE across three cross-fold replicates"}
        counts["result"] += 1
        add(rec(f"{eid.replace('-eval-', '-result-')}-{suffix}", "result", f"{eid.split('-eval-')[1]} {suffix}",
                "Reported measurement transcribed from the pinned source. Not independently reproduced.", a,
                links=[{"relation": "evaluation", "target_id": eid}], facets={}))

    AGG3 = "Three cross-fold replicates with standard error printed; the caption does not name the point statistic"
    tp = ("true-positive-count", "count", "gene pairs, out of the 200 strongest measured pairs", "higher")
    # Tables 2 and 3
    for r_, key in [("Uniform", "naiad-uniform"), ("MPE", "naiad-mpe"), ("UCB", "naiad-ucb"), ("Uncertainty", "naiad-uncertainty")]:
        for j, d in enumerate(DATASETS):
            eid = evaluation("table2-3", "Tables 2 and 3, acquisition functions with NAIAD", key, d, al, "author_reported", None,
                             f"NAIAD ensemble; {r_} acquisition", f"Tables 2 and 3, row '{r_}', column '{d}'")
            v = t["2"][r_][j]
            result(eid, "top200-round4", v, v, tp[0], q_round.format(r=4), tp[1], tp[2], tp[3],
                   f'Table 2, row "{r_}", column "{d}"')
            v = t["3"][r_][j]
            result(eid, "marginal-gain-round4", v, v, "count",
                   "marginal gain (P_4 - P_0)/4 in the screen's 200 strongest measured gene pairs found, round 0 to round 4",
                   "count", "top-200 gene pairs per round", "higher", f'Table 3, row "{r_}", column "{d}"',
                   note="Value read from the text layer. Check: Table 2 minus 4 x Table 3 gives one round-0 count per dataset across all four rows (88, 36, 37, 69).")
    # Table 4
    for (m, a_), cells in t["4"].items():
        key = f"{m.lower()}-{slug(a_)}"
        for j, d in enumerate(DATASETS):
            eid = evaluation("table4", "Table 4, NAIAD against RECOVER by acquisition function", key, d, al,
                             "author_reported" if m == "NAIAD" else "independent_paper", AGG3,
                             f"{m} ensemble; {a_} acquisition", f"Table 4, row '{m} {a_}', column '{d}'")
            v, se = cells[j]
            result(eid, "top200-round4", f"{v} ({se})", v, tp[0], q_round.format(r=4), tp[1], tp[2], tp[3],
                   f'Table 4, row "{m} {a_}", column "{d}"', se)
    # Table 5
    for n, cells in t["5"].items():
        for j, d in enumerate(DATASETS):
            for k, a_ in enumerate(["MPE", "Uniform"]):
                key = f"naiad-{slug(a_)}-ensemble-{n}"
                eid = evaluation("table5", "Table 5, NAIAD ensemble size", key, d, al, "author_reported", AGG3,
                                 f"NAIAD ensemble of {n}; {a_} acquisition", f"Table 5, row '{n}', column '{d} {a_}'",
                                 extra={"ensemble_size": int(n)})
                v, se = cells[2 * j + k]
                result(eid, "top200-round4", f"{v} ({se})", v, tp[0], q_round.format(r=4), tp[1], tp[2], tp[3],
                       f'Table 5, Ensemble Size row "{n}", column "{d} {a_}"', se)
    # Table 7
    for (m, a_), cells in t["7"].items():
        key = f"{m.lower()}-{slug(a_)}"
        eid = evaluation("table7", "Table 7, NAIAD, RECOVER and GEARS over rounds on Norman", key, "Norman", al,
                         "author_reported" if m == "NAIAD" else "independent_paper", AGG3,
                         f"{m}; {a_} acquisition", f"Table 7, row '{m} {a_}'")
        for r in range(5):
            v, se = cells[r]
            result(eid, f"top200-round{r}", f"{v} ({se})", v, tp[0], q_round.format(r=r), tp[1], tp[2], tp[3],
                   f'Table 7, row "{m} {a_}", column "Round {r}"', se)
    # Table 8
    for b, cells in t["8"].items():
        key = "naiad-uniform" if b == "Uniform" else f"naiad-mean-ucb-beta-{slug(b)}"
        for j, d in enumerate(DATASETS):
            eid = evaluation("table8", "Table 8, Mean-UCB beta with NAIAD", key, d, al, "author_reported", AGG3,
                             "NAIAD ensemble; " + ("Uniform acquisition" if b == "Uniform" else f"Mean-UCB acquisition, beta = {b}"),
                             f"Table 8, row '{b}', column '{d}'")
            v, se = cells[j]
            result(eid, "top200-round4", f"{v} ({se})", v, tp[0], q_round.format(r=4), tp[1], tp[2], tp[3],
                   f'Table 8, row "{b}", column "{d}"', se)
    # Tables 1 and 6
    for m in ["Linear", "MLP", "GEARS", "RECOVER", "NAIAD"]:
        k = pred[m][0]
        own = m in ("Linear", "MLP", "NAIAD")
        for j, d in enumerate(DATASETS):
            eid = evaluation("table1-6", "Tables 1 and 6, RMSE at fixed gene frequency", f"{k}-prediction", d, ds,
                             "author_reported" if own else "independent_paper", AGG3, f"{m} trained once on the downsampled set",
                             f"Table 1 and Table 6, row '{m}', column '{d}'")
            for tab, freq in [("1", "4"), ("6", "10"), ("1", "20")]:
                v, se = t[tab][(freq, m)][j]
                result(eid, f"rmse-gene-frequency-{freq}", f"{v} ({se})", v, "root-mean-squared-error",
                       f"test RMSE of pair viability, training set with each gene seen about {freq} times on average",
                       "unitless", "printed x 10^-2", "lower",
                       f'Table {tab}, Gene Frequency {freq} block, row "{m}", column "{d}"', se)

    # Claims
    def claim(key, subject, field, value, loc):
        add(rec(f"{P}-claim-{key}", "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.",
                {"field": field, "value": value, "source_locator": loc,
                 "review": review("Transcribed from the cited section.")},
                links=[{"relation": "subject", "target_id": subject}], facets={}))
    claim("naiad-architecture", mid["naiad"], "architecture",
          "Y_i+j = phi([Y_i, Y_j] W1) A1^T + f(phi(W2 X_i), phi(W2 X_j)) A2^T: an over-parameterised encoding of the two single-gene effects plus a permutation-invariant (summed) combination of learned gene embeddings; the embedding dimension is increased on a fixed schedule as the average number of times each gene is seen grows.",
          "Section 3.1, Eq. 1; Section 3.2; Table 9")
    claim("naiad-input-requirement", mid["naiad"], "input_requirement",
          "Assumes the individual effect of each gene on the phenotype is known; the current model cannot predict combinations involving genes whose single-gene effect is unseen.",
          "Section 6, Discussion and Conclusion")
    claim("naiad-code", mid["naiad"], "code_availability", "Source code at https://github.com/NeptuneBio/NAIAD.",
          "Abstract; Software and Data")
    claim("naiad-hardware", mid["naiad"], "hardware", "All model training was done on a single Paperspace A100-80G server with 100 GB of RAM.",
          "Appendix E")
    claim("recover-gene-adaptation", mid["recover"], "adaptation",
          "Adapted from drugs to genes by a bilinear projection that combines 128-dimensional gene embeddings; trained to predict the gene equivalent of Bliss scores (measured viability minus the product of single-gene viabilities) and converted back to viability.",
          "Appendix B, 'RECOVER adaptation'")
    return out, counts


def main():
    t = parse(sys.argv[1])
    records, counts = build(t)
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), "duplicate IDs"
    assert counts == {"evaluation": 140, "result": 212}, counts
    records.sort(key=lambda r: r["id"])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(len(records), counts)


if __name__ == "__main__":
    main()
