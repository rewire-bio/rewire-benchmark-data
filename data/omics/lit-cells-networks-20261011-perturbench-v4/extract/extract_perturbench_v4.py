"""PerturBench v4 (Wu et al., arXiv 2408.10609v4, NeurIPS 2025 Datasets and Benchmarks): result Tables 2-13 from the pinned arXiv HTML.

The store already holds Tables 2 and 3 of v1 (source evidence-expansion-perturbench-5c480456). Version 4 reruns every model over
5 seeds, changes the metric columns and adds the Jiang24, Frangieh21 and OP3 experiments and the mode-collapse tables, so all of its
result tables are extracted here as a separate source.

Usage: python3 -I extract_perturbench_v4.py <2408.10609v4.html> <batch-folder>
"""
import sys, os, re, html, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, judgement, write_links, finalise

page, folder = sys.argv[1:3]
SHA = sha256(page)
assert SHA == "b73f2644b129ca209b69812ad467d595e15c283f6cae5c3c9bbc5a4c5870996a", SHA
URL = "https://arxiv.org/html/2408.10609v4"
RETRIEVED = "2026-10-11T21:29:35Z"
B = "lit-cells-networks-20261011-perturbench-v4"
b = Batch(folder, B, areas=["single-cell"])

SRC = b.source(B + "-source-wu2025", "PerturBench: Benchmarking Machine Learning Models for Cellular Perturbation Analysis (arXiv v4)", {
    "url": "https://arxiv.org/abs/2408.10609v4", "artifact_url": URL,
    "version": "arXiv 2408.10609v4, posted 2025-10-24 (NeurIPS 2025 Datasets and Benchmarks Track version)",
    "retrieved_at": RETRIEVED, "artifact_sha256": SHA, "doi": "10.48550/arXiv.2408.10609", "publication_status": "preprint",
    "licence": "arXiv.org perpetual non-exclusive license 1.0", "media_type": "text/html",
    "hash_scope": "Exact bytes of the arXiv HTML rendering of v4 as retrieved; arXiv may regenerate HTML, so the hash describes this retrieval.",
    "limitations": ["Authors are at Altos Labs and developed the PerturBench platform and its baseline models (Linear, Latent Additive, Decoder); the published models (CPA, SAMS-VAE, Biolord, GEARS) were reimplemented or wrapped by the authors.",
                    "The arXiv record is a preprint version of the NeurIPS 2025 Datasets and Benchmarks paper; the proceedings version was not retrieved.",
                    "Table 4 caption says 70% of perturbations from 9 of 30 states are held out; Appendix D.4 'Jiang24 splits' describes 12 cytokine-cell line combinations. Not resolved here."]},
    description="arXiv HTML of PerturBench version 4, retrieved and hashed for the 2026-10-11 cells-spatial literature pass. Version 1 is already in the store as evidence-expansion-perturbench-5c480456.")
SIDS = [SRC]
BENCH = "discovery-benchmark-perturbench"

s = open(page, encoding="utf-8").read()
s = re.sub(r"<annotation[^>]*>.*?</annotation>", "", s, flags=re.S)
BOLD = {chr(0x1D7CE + i): str(i) for i in range(10)}


def text(x):
    t = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", x)).split())
    return "".join(BOLD.get(c, c) for c in t)


tables = {}
for m in re.finditer(r'<figure[^>]*class="[^"]*ltx_table[^"]*".*?</figure>', s, flags=re.S):
    f = m.group(0)
    cap = text(re.search(r"<figcaption.*?</figcaption>", f, flags=re.S).group(0))
    n = int(re.match(r"Table (\d+)", cap).group(1))
    rows = [[text(c) for c in re.findall(r"<t[dh][^>]*>.*?</t[dh]>", tr, flags=re.S)] for tr in re.findall(r"<tr.*?</tr>", f, flags=re.S)]
    tables[n] = (cap, rows)
assert sorted(tables) == list(range(1, 23)), sorted(tables)

# Configurations. Rows whose printed name matches a v1 configuration reuse it; v1 and v4 runs differ, which the evaluations record.
CFG = {"CPA ∗": "perturbench-method-cpa", "CPA ∗ (noAdv)": "perturbench-method-cpa-noadv", "CPA ∗ (scGPT)": "perturbench-method-cpa-scgpt",
       "SAMS-VAE ∗": "perturbench-method-sams-vae", "Biolord ∗": "perturbench-method-biolord", "BioLord ∗": "perturbench-method-biolord",
       "LA": "perturbench-method-la", "LA (scGPT)": "perturbench-method-la-scgpt", "Decoder": "perturbench-method-decoder",
       "DecoderOnly": "perturbench-method-decoder-cov", "Decoder (Cov)": "perturbench-method-decoder-cov", "Linear": "perturbench-method-linear"}
NEWCFG = {
    "SAMS-VAE ∗ (S)": ("SAMS-VAE* (S)", "SAMS-VAE as reimplemented by the PerturBench authors with the sparse mask and global latent variables removed (Section 3.2 and Section 5).", "Section 3.2; Section 5", ["supervised_machine_learning"], None),
    "GEARS": ("GEARS (PerturBench Norman19 run)", "GEARS trained and evaluated by the PerturBench authors with its public code and their HPO script on the PerturBench Norman19 split (Appendix D.5).", "Appendix D.5 'GEARS'", ["supervised_machine_learning"], "catalog-model-gears"),
    "DecoderOnly (+ perturbations)": ("DecoderOnly (+ perturbations)", "PerturBench Decoder-only baseline with cell line and perturbations as input (Appendix C.7.1; Figure C.2B), as named in the mode-collapse Table 12. The source does not say whether this is the 'Decoder' row of Tables 2 and 5.", "Appendix C.7, Table 12", ["supervised_machine_learning"], None),
}
cfg_new = {}


def config(label):
    if label in CFG:
        return CFG[label]
    if label not in cfg_new:
        name, desc, loc, mt, model = NEWCFG[label]
        links = [{"relation": "configuration_of", "target_id": model}] if model else []
        cfg_new[label] = b.entity("configuration", b.rid("config", name), name, desc, SIDS, {
            "reported_name": label, "source_locator": loc, "foundation_model_eligible": False,
            "hyperparameters": "Selected per dataset and task by Optuna HPO (at least 60 trials), then retrained with 5 seeds (Section 4.3)",
            "access_reuse": "Code in the PerturBench repository (github.com/altoslabs/perturbench)",
            "missing_metadata": {"version": {"reason": "unreported", "note": "No code commit is printed for the v4 runs"}}},
            method_types=mt, links=links)
    return cfg_new[label]


# Datasets and protocols.
DATA = {
    "srivatsan20": ("Srivatsan20 (PerturBench v4 covariate-transfer split)", "Srivatsan20 sci-Plex chemical perturbations in three cell lines (A549, K562, MCF-7), split by PerturBench v4 to test transfer to a held-out cell line.", "Table 1; Appendix D.4"),
    "norman19": ("Norman19 (PerturBench v4 combination split)", "Norman19 K562 CRISPRa single and dual gene perturbations, split by PerturBench v4 to predict held-out dual perturbations.", "Table 1; Appendix D.4"),
    "jiang24": ("Jiang24 (PerturBench v4 covariate-transfer split)", "Jiang24 genetic perturbations across cell lines and cytokine treatments, with 70% of perturbations held out in some states.", "Table 1; Table 4 caption; Appendix D.4 'Jiang24 splits'"),
    "frangieh21": ("Frangieh21 (PerturBench v4 co-culture split)", "Frangieh21 genetic perturbations in melanoma cells; 70% of perturbations in the co-culture condition held out.", "Table 1; Table 7 caption; Appendix D.4 'Frangieh21 splits'"),
    "op3": ("OP3 (PerturBench v4 split)", "OP3 small-molecule perturbations in primary PBMC cell types, split from the NeurIPS 2023 challenge train, public and private test partitions.", "Table 1; Appendix D.4 'OP3 splits'"),
}
data_ids = {k: b.entity("dataset_subset", b.rid("data", k), n, d, SIDS, {"split": d, "source_locator": loc,
            "missing_metadata": {"version": {"reason": "unreported"}, "test_count": {"reason": "unextracted", "note": "Per-split perturbation counts are in the authors' split notebooks, not printed in the tables"}}})
            for k, (n, d, loc) in DATA.items()}

PROTO = {
    "srivatsan20": ("covariate transfer to a held-out cell line on Srivatsan20", "Tables 2, 5"),
    "norman19": ("combination prediction of held-out dual perturbations on Norman19", "Tables 3, 6"),
    "jiang24": ("covariate transfer to held-out perturbations in held-out biological states on Jiang24", "Tables 4, 11"),
    "frangieh21": ("covariate transfer from mono-culture to co-culture on Frangieh21", "Tables 7, 8"),
    "op3": ("covariate transfer of small-molecule effects across PBMC cell types on OP3", "Tables 9, 10"),
}
protos = {}
for k, (desc, loc) in PROTO.items():
    protos[k] = b.entity("protocol", b.rid("protocol", k), f"PerturBench v4 {desc}", f"PerturBench v4 {desc}; mean and one standard deviation over 5 seeds of the best HPO configuration.", SIDS, {
        "protocol": f"{desc}. Hyperparameters chosen by Optuna HPO on RMSE + 0.1 x RMSE rank, then 5 training seeds; metrics computed on the held-out test perturbations.",
        "version": "PerturBench arXiv v4", "metric": "perturbench-cosine-logfc", "metric_direction": "higher", "unit": "fraction",
        "random_seeds": "5 seeds (Table 2 caption; Section 4.3)",
        "limitations": ["All models were trained and tuned by the PerturBench authors, who also developed the Linear, Latent Additive and Decoder baselines.",
                        "Metric columns differ between the main and additional tables; compare only within one metric."],
        "source_locator": loc}, links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data_ids[k]}])
for k, loc in (("srivatsan20", "Table 12; Appendix C.7.1-C.7.2"), ("frangieh21", "Table 13; Appendix C.7.3")):
    protos[k + "-collapse"] = b.entity("protocol", b.rid("protocol", k, "mode-collapse"), f"PerturBench v4 mode-collapse diagnostics on {k.capitalize()}",
        f"Mode-collapse diagnostics on the {k.capitalize()} covariate-transfer split: RMSE, RMSE rank, transposed rank and matrix distance between predicted and observed cosine similarity matrices.", SIDS, {
        "protocol": "Mode-collapse diagnostics in Appendix C.7. Single values without spread; the number of runs behind each value is not printed.",
        "version": "PerturBench arXiv v4", "metric": "perturbench-matrix-distance", "metric_direction": "lower", "unit": "unit-unreported",
        "limitations": ["No spread or seed count is printed for these tables; values differ from the 5-seed means for the same models in Tables 5 and 8."],
        "source_locator": loc}, links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data_ids[k]}])

METRIC = {  # column label -> (metric, direction, unit, qualifier, unit_detail)
    "Cosine LogFC": ("perturbench-cosine-logfc", "higher", "fraction", None, None),
    "Cosine logFC": ("perturbench-cosine-logfc", "higher", "fraction", None, None),
    "Cosine LogFC rank": ("perturbench-cosine-logfc-rank", "lower", "fraction", None, None),
    "MMD PCA": ("perturbench-energy-mmd", "lower", "unit-unreported", "PCA space: top 256 principal components fitted on the ground-truth test split", None),
    "MMD": ("perturbench-energy-mmd", "lower", "unit-unreported", "gene expression space", None),
    "DEG recall": ("recall", "higher", "fraction", "DEG recall: fraction of the top 20 ground-truth DEGs (scanpy t-scores against controls) recalled from predicted cells", None),
    "RMSE mean": ("perturbench-rmse-of-mean", "lower", "unit-unreported", None, "Expression units after PerturBench preprocessing; not printed"),
    "RMSE mean rank": ("perturbench-rmse-rank", "lower", "fraction", None, None),
    "RMSE mean transposed-rank": ("perturbench-rmse-transposed-rank", "lower", "fraction", None, None),
    "Matrix distance": ("perturbench-matrix-distance", "lower", "unit-unreported", None, "Frobenius norm of the difference between predicted and observed cosine similarity matrices"),
}
SUP = "⁻"


def parse_cell(cell):
    """'0.38 ± 6 × 10 − 3' -> (printed, mean, sd decimal string). '-' -> None."""
    if cell == "-":
        return None
    m = re.fullmatch(r"(\d+(?:\.\d+)?) ± (\d+) × 10 (−?) ?(\d+)", cell)
    if m:
        mant, neg, exp = int(m.group(2)), m.group(3), int(m.group(4))
        e = -exp if neg else exp
        sd = f"{mant * 10 ** e:.{max(0, -e)}f}" if e < 0 else str(mant * 10 ** e)
        return cell, m.group(1), sd
    m = re.fullmatch(r"(\d+(?:\.\d+)?) ± 0", cell)
    if m:
        return cell, m.group(1), "0"
    m = re.fullmatch(r"\d+(?:\.\d+)?", cell)
    if m:
        return cell, cell, None
    raise ValueError("unparsed cell " + repr(cell))


EXPECT = {  # table -> (protocol key, header, model rows)
    2: ("srivatsan20", ["Model", "Cosine LogFC", "Cosine LogFC rank", "MMD PCA", "DEG recall"], 11),
    3: ("norman19", ["Model", "Cosine logFC", "Cosine LogFC rank", "MMD PCA", "DEG recall"], 11),
    4: ("jiang24", ["Model", "Cosine logFC", "Cosine LogFC rank", "MMD PCA", "DEG recall"], 7),
    5: ("srivatsan20", ["Model", "RMSE mean", "RMSE mean rank", "MMD"], 11),
    6: ("norman19", ["Model", "RMSE mean", "RMSE mean rank", "MMD"], 11),
    7: ("frangieh21", ["Model", "Cosine logFC", "Cosine LogFC rank", "MMD PCA", "DEG recall"], 10),
    8: ("frangieh21", ["Model", "RMSE mean", "RMSE mean rank", "MMD"], 10),
    9: ("op3", ["Model", "Cosine LogFC", "Cosine LogFC rank", "MMD PCA", "DEG recall"], 8),
    10: ("op3", ["Model", "RMSE mean", "RMSE mean rank", "MMD"], 8),
    11: ("jiang24", ["Model", "RMSE mean", "RMSE mean rank", "MMD"], 7),
    12: ("srivatsan20-collapse", None, 5),
    13: ("frangieh21-collapse", None, 5),
}
COLLAPSE_COLS = ["RMSE mean", "RMSE mean rank", "RMSE mean transposed-rank", "Matrix distance"]
REV = lambda loc: extraction_review(["deterministic-table-parse"], "Parsed the pinned arXiv v4 HTML table markup with extract_perturbench_v4.py: header and row counts asserted per table, math-bold digits (best-in-column marks) normalised to plain digits, '± m × 10 − k' converted to a decimal standard deviation. " + loc, SHA, URL)

# Published models the authors reimplemented or wrapped; their own baselines and ablations stay author_reported.
INDEPENDENT = {"CPA ∗", "SAMS-VAE ∗", "Biolord ∗", "BioLord ∗", "GEARS"}
evals, counts = {}, {}
for t, (pk, header, nrows) in EXPECT.items():
    cap, rows = tables[t]
    if header:
        assert rows[0] == header, (t, rows[0])
        cols, body = header[1:], rows[1:]
    else:  # two-line header in Tables 12-13
        assert rows[0] == ["Model", "RMSE", "RMSE", "RMSE", "Matrix"] and rows[1] == ["mean", "mean rank", "mean transposed-rank", "distance"], (t, rows[:2])
        cols, body = COLLAPSE_COLS, rows[2:]
    assert len(body) == nrows, (t, len(body))
    for row in body:
        label, cells = row[0], row[1:]
        assert len(cells) == len(cols), (t, row)
        c = config(label)
        key = (c, pk)
        if key not in evals:
            eslug = "decoder" if label == "DecoderOnly" else c.replace("perturbench-method-", "").replace(B + "-config-", "")  # P1 keeps the evaluation ID
            evals[key] = b.evaluation(b.rid("eval", pk, eslug),
                f"{label} on PerturBench v4 {pk}", SIDS, c, protos[pk], data_ids[pk.replace("-collapse", "")],
                "independent_paper" if label in INDEPENDENT else "author_reported",
                {"protocol_id": protos[pk], "dataset_version": None, "split": DATA[pk.replace("-collapse", "")][1], "population": None,
                 "inputs": "Control cells with matched covariates and perturbation identity" + ("; scGPT whole-human cell embeddings as input" if "scGPT" in label else ""),
                 "adaptation": "Trained from scratch per dataset with HPO" + ("; frozen pretrained scGPT embeddings" if "scGPT" in label else ""),
                 "metric_implementation": "PerturBench evaluation module (Section 4.2)",
                 "aggregation": "Mean over 5 seeds" if "collapse" not in pk else None, "budget": "Optuna HPO, at least 60 trials"},
                f"Table {t}, row '{label}'")
        for col, cell in zip(cols, cells):
            loc = f"Table {t}, row '{label}', column '{col}'"
            p = parse_cell(cell)
            if p is None:
                continue  # printed '-': not run for this model (Section 4.2 notes DecoderOnly cannot give DEG recall)
            printed, mean, sd = p
            metric, direction, unit, q, ud = METRIC[col]
            unc = {"type": "standard_deviation", "value": sd, "printed": printed.split(" ± ")[1], "n": 5, "scope": "across 5 training seeds (Table 2 caption)"} if sd is not None and " ± " in printed else None
            b.result(b.rid("result", pk, label, col, f"t{t}"), f"{label} {pk} {col} (Table {t})", SRC, SIDS, evals[key], printed, metric, direction, unit,
                     loc, REV(loc), qualifier=q, unit_detail=ud, uncertainty=unc, numeric=mean)
            counts[t] = counts.get(t, 0) + 1

# Printed cells per table, excluding '-' (counted by hand from the rendered tables).
assert counts == {2: 37, 3: 37, 4: 27, 5: 30, 6: 30, 7: 35, 8: 28, 9: 31, 10: 24, 11: 21, 12: 20, 13: 20}, counts
UC, UCN = "use-case-genetic-perturbation-response", "Assess models for genetic perturbation experiments"
COMMON_LIM = ["The PerturBench authors trained and tuned every model themselves and developed the Linear, Latent Additive and Decoder baselines; CPA, SAMS-VAE, Biolord and GEARS are their reimplementations or wrappers.",
              "Preprint (arXiv v4 of the NeurIPS 2025 Datasets and Benchmarks paper); the proceedings version was not compared.",
              "Spread is one standard deviation over 5 training seeds of one HPO-selected configuration, not over data splits.",
              "Expression-prediction scores do not establish causal mechanism or experimental hit rates (use-case exclusion)."]
# Second constraint per protocol: reviewer cn-2's text (P3), verbatim.
CONS = lambda second: ["Inspect every linked evaluation's source locator before citing a result.", second,
                       "Do not combine these values with PerturBench v1 results (evidence-expansion-perturbench-5c480456): v4 reran the models and the numbers differ."]
SRCLOC = lambda t: [{"source_id": SRC, "locator": t}]
ev_for = lambda pk: [e for (c, p), e in evals.items() if p == pk]
links = [
    judgement(b, UC, protos["norman19"], "norman19", SIDS, "proxy",
              "Cosine similarity and rank of predicted log fold change, RMSE and RMSE rank of the mean expression profile, MMD and DEG recall for held-out K562 CRISPRa dual-gene perturbations (Norman19), for CPA, SAMS-VAE, Biolord, GEARS, Latent Additive (with and without scGPT embeddings), Decoder and Linear models",
              "The protocol compares perturbation-response models and simple baselines on the same held-out dual perturbations, which is the methods-and-controls comparison the use case asks for. It is proxy evidence because the endpoint is expression agreement, not experimental prioritisation.",
              CONS("Compare models only within one table column; MMD, MMD PCA and DEG recall are not printed ('-') for the CPA* (scGPT), LA (scGPT) and GEARS rows, and DEG recall is not printed for the Decoder row."),
              COMMON_LIM + ["GEARS rows have no MMD or DEG recall (printed '-')."], SRCLOC("Tables 3 and 6; Section 4.2; Appendix D.4-D.5"),
              "perturbench-cosine-logfc", "perturbench-v4", "PerturBench v4 (Wu et al., NeurIPS 2025 Datasets and Benchmarks)", "Norman19 dual perturbations (K562 CRISPRa)", 1, ev_for("norman19"), UCN),
    judgement(b, UC, protos["jiang24"], "jiang24", SIDS, "proxy",
              "Cosine similarity and rank of predicted log fold change, MMD, DEG recall and RMSE for held-out genetic perturbations in held-out cell line and cytokine states (Jiang24)",
              "The protocol tests whether models trained on some cell states predict genetic perturbation responses in other states, which bears on using predictions in a new cell system. Proxy: expression agreement only, and the held-out state definition is inconsistent between the table caption and the appendix.",
              CONS("Compare models only within one table column; DEG recall is not printed ('-') for the Decoder row."),
              COMMON_LIM + ["Table 4 caption (9 of 30 states held out) and Appendix D.4 (12 cytokine-cell line combinations) describe the held-out states differently.",
                            "The use case lists cross-cell-type transfer as outside the cited GEARS usage scope; this protocol tests transfer to held-out cell line and cytokine states and does not include GEARS, so it bears only on the use case's open question about performance in a new cell system."], SRCLOC("Tables 4 and 11; Appendix D.4 'Jiang24 splits'"),
              "perturbench-cosine-logfc", "perturbench-v4", "PerturBench v4 (Wu et al., NeurIPS 2025 Datasets and Benchmarks)", "Jiang24 held-out states (genetic perturbations)", 2, ev_for("jiang24"), UCN),
    judgement(b, UC, protos["frangieh21"], "frangieh21", SIDS, "proxy",
              "Cosine similarity and rank of predicted log fold change, MMD, DEG recall and RMSE for held-out genetic perturbations in melanoma co-culture, trained on all other perturbations, including the other culture conditions and the remaining 30% of co-culture perturbations (Frangieh21)",
              "The protocol asks models to transfer genetic perturbation effects to a more complex co-culture system, a question close to planning screens in a new context. Proxy: expression agreement only.",
              CONS("Compare models only within one table column; MMD, MMD PCA and DEG recall are not printed ('-') for the CPA* (scGPT) and LA (scGPT) rows, and DEG recall is not printed for the Decoder row."),
              COMMON_LIM, SRCLOC("Tables 7 and 8; Appendix D.4 'Frangieh21 splits'"),
              "perturbench-cosine-logfc", "perturbench-v4", "PerturBench v4 (Wu et al., NeurIPS 2025 Datasets and Benchmarks)", "Frangieh21 co-culture transfer (genetic perturbations)", 3, ev_for("frangieh21"), UCN),
]
write_links(folder, links)
finalise(b, "reviewer-cn-2", "2026-10-12T08:44:00Z",
         "value, uncertainty, locator, metric, unit, direction and linked configuration and protocol checked by the reviewer's own parse of all Tables 2-13 cells and a hand check of 48 values against the v4 PDF.",
         "Artifact re-downloaded from arXiv and SHA-256 matched.")
print(json.dumps(b.write()))
