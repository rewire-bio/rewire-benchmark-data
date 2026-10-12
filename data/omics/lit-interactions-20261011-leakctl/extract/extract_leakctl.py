"""PLABench (Wang and Cheng, bioRxiv 10.64898/2026.09.17.752433v1): Tables 2, 3 and 4.

Usage: python3 -I extract_leakctl.py <biorxiv-pdf> <pdftotext -layout output> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, reviewed_review, source_review, mark_reviewed, sha256, slug, num

pdf_path, txt_path, folder = sys.argv[1], sys.argv[2], sys.argv[3]
SHA = sha256(pdf_path)
TXT_SHA = sha256(txt_path)
URL = "https://www.biorxiv.org/content/10.64898/2026.09.17.752433v1.full.pdf"
assert SHA == "5fba9691f7d0777d19dabc66144e5c23d40e430de4919f97b92e4d50fb397281", SHA

P = "lit-interactions-20261011-leakctl"
b = Batch(folder, P, areas=["molecular-interactions"])
SRC = b.source(P + "-source-wang2026", "Leakage-controlled benchmarking reveals generalization limits of deep learning for protein-ligand binding affinity prediction", {
    "url": "https://doi.org/10.64898/2026.09.17.752433", "artifact_url": URL,
    "version": "bioRxiv 10.64898/2026.09.17.752433v1 (posted 2026-09-23); 30-page PDF",
    "retrieved_at": "2026-10-11T21:28:04Z", "artifact_sha256": SHA, "doi": "10.64898/2026.09.17.752433",
    "publication_status": "preprint", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/pdf",
    "code_url": "https://doi.org/10.5281/zenodo.22782934",
    "limitations": [
        "bioRxiv adds a per-request banner, so the PDF hash describes this one retrieval.",
        "Values were read from the pdftotext (poppler 26.08.0) layout text layer, SHA-256 " + TXT_SHA + ". The licence (CC BY-NC-ND) is respected by not archiving the PDF or its text in the repository.",
        "Bold marking of the best value per column is not carried by the text layer and is not recorded.",
    ]})
SIDS = [SRC]
REVIEW = lambda loc: extraction_review(["pdf-text-parse"],
    "Parsed the pdftotext -layout text layer of the pinned bioRxiv PDF with extract/extract_leakctl.py; row labels and the number of numeric cells per row asserted. " + loc,
    SHA, URL)

lines = open(txt_path, encoding="utf-8").read().split("\n")

EXISTING = {"DeepDTA": "identity-model-deepdta", "Boltz2": "catalog-model-boltz-2"}
NEW = {
    "LLF": ("model", "LLF sequence-based protein-ligand affinity model (multi-stream GCN and CNN keeping local features; Table 1).", ["supervised_machine_learning"]),
    "MixingDTA": ("model", "MixingDTA: meta-ensemble affinity model using MolFormer and ESM3 features (Table 1).", ["foundation_model"]),
    "Graph_RG": ("model", "Graph_RG: two-stream graph transformer, ligand pose-free structure-based affinity model (Table 1).", ["supervised_machine_learning"]),
    "FlowDock": ("model", "FlowDock: conditional flow-matching docking and affinity model built on ESMFold and NeuralPLexer components (Table 1).", ["foundation_model"]),
    "FLOWR.ROOT": ("model", "FLOWR.ROOT: SE(3)-equivariant flow-matching model with joint structure, affinity and confidence heads (Table 1).", ["foundation_model"]),
    "MFE": ("model", "MFE: multimodal extraction model combining 3D CNN, GVP-GNN and ProtTrans features (Table 1).", ["supervised_machine_learning"]),
    "LCDD-team": ("model", "LCDD-team: three-stream GPS graph transformer affinity model from the CASP16 LCDD team (Table 1).", ["supervised_machine_learning"]),
}
fam_ids = {}
def fam_id(f):
    if f in EXISTING:
        return EXISTING[f]
    if f not in fam_ids:
        kind, desc, mt = NEW[f]
        rid = b.rid(kind, f)
        b.entity(kind, rid, f, desc, SIDS, {"reported_name": f, "entity_level": "family", "source_locator": "Table 1",
                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the evaluated setup is on the configuration"}}},
                 method_types=mt)
        fam_ids[f] = rid
    return fam_ids[f]

# Six structure-based and three sequence-based models (Results, line 'six structure-based: Boltz2, FLOWR.ROOT, Graph_RG, LCDD-team, FlowDock, MFE').
CATEGORY = {"DeepDTA": "sequence-based", "LLF": "sequence-based", "MixingDTA": "sequence-based", "Graph_RG": "structure-based",
            "Boltz2": "structure-based", "FlowDock": "structure-based", "FLOWR.ROOT": "structure-based", "MFE": "structure-based",
            "LCDD-team": "structure-based"}
MT = {"DeepDTA": ["supervised_machine_learning"], "LLF": ["supervised_machine_learning"], "MixingDTA": ["foundation_model"],
      "Graph_RG": ["supervised_machine_learning"], "Boltz2": ["foundation_model"], "FlowDock": ["foundation_model"],
      "FLOWR.ROOT": ["foundation_model"], "MFE": ["supervised_machine_learning"], "LCDD-team": ["supervised_machine_learning"]}
# FlowDock is by Morehead and Cheng (ref. 7); Cheng is the senior author of this benchmark.
ORIGIN = lambda m: "author_reported" if m == "FlowDock" else "independent_paper"

configs = {}
def config(model, setting):
    key = (model, setting)
    if key in configs:
        return configs[key]
    rid = b.rid("config", model, setting)
    if setting == "davis-kiba":
        params = "Retrained by the benchmark authors on Davis or KIBA under each split (warm: 5-fold CV on an 80/20 split; cold splits: two-stage protocol from MixingDTA, five fold models evaluated on a fixed test set and aggregated)"
    else:
        params = ("Published checkpoint applied without retraining; co-folds its own complex from sequence and SMILES, so the supplied structures are not consumed"
                  if model == "Boltz2" else "Published checkpoint applied without retraining; given AlphaFold3-predicted complex structures")
        if model in ("DeepDTA", "LLF", "MixingDTA"):
            params = "Sequence-based model as trained by the benchmark authors (Methods); applied to CASP16 and ChEMBL35 without retraining on them"
    attrs = {"reported_name": model, "foundation_model_eligible": MT[model] == ["foundation_model"], "parameters": params,
             "source_locator": "Table 1; Methods; " + ("Table 2" if setting == "davis-kiba" else "Tables 3 and 4"),
             "access_reuse": "Not stated per model in the source; see each model's release",
             "missing_metadata": {"version": {"reason": "unreported", "note": "No checkpoint version printed"}}}
    name = f"{model} ({'retrained on Davis and KIBA' if setting == 'davis-kiba' else 'CASP16 and ChEMBL35 evaluation'}, PLABench)"
    b.entity("configuration", rid, name, f"{model} as evaluated in PLABench ({CATEGORY[model]}).", SIDS, attrs,
             method_types=MT[model], links=[{"relation": "configuration_of", "target_id": fam_id(model)}])
    configs[key] = rid
    return rid

BENCH = b.entity("benchmark", b.rid("benchmark", "plabench"), "PLABench",
    "Leakage-controlled, target-centric benchmark of protein-ligand binding affinity prediction: Davis and KIBA under warm, cold-target and cold-drug splits, CASP16 ligand series L1000 and L3000, and a ChEMBL35 test set filtered against the training data of the evaluated models.",
    SIDS, {"entity_level": "suite", "version": "bioRxiv v1 (2026-09-23)", "task": "Protein-ligand binding affinity prediction and target-centric ligand ranking",
           "scope_note": "Tables 2-4 extracted. Figure-only analyses (input pose accuracy ladder, interaction counts, per-target Kendall tau) not extracted.",
           "source_locator": "Abstract; Figure 1; Tables 1-4"})

# Metrics: printed header -> (concept, direction, unit, unit_detail)
AFF_UNIT = ("unit-unreported", "Error in the affinity scale of the dataset (Davis and CASP16 pKd; KIBA score); the table prints no unit")
METRICS = {
    "MSE": ("mean-squared-error", "lower") + AFF_UNIT,
    "RMSE": ("root-mean-squared-error", "lower") + AFF_UNIT,
    "Pearson": ("pearson-correlation", "higher", "unitless", None),
    "Spearman": ("spearman-correlation", "higher", "unitless", None),
    "Kendall": ("kendall-tau", "higher", "unitless", None),
    "rm2": ("modified-squared-correlation", "higher", "unitless", None),
    "CI": ("concordance-index", "higher", "unitless", None),
}

datas, protos = {}, {}
def dataset(key, name, desc, version, split, loc, population=None):
    attrs = {"version": version, "split": split, "source_locator": loc}
    if population:
        attrs["population"] = population
    datas[key] = b.entity("dataset", b.rid("data", key), name, desc, SIDS, attrs)

def protocol(key, name, desc, proc, loc, lim):
    protos[key] = b.entity("protocol", b.rid("protocol", key), name, desc, SIDS,
        {"protocol": proc, "version": "PLABench bioRxiv v1", "limitations": lim, "source_locator": loc},
        links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": datas[key]}])

COMMON_LIM = ["Metrics are computed over all test pairs of the set (Methods, 'Evaluation metrics'); per-target averaging is not stated for these tables.",
              "Only one value per cell is printed; no uncertainty is reported in Tables 2-4."]
SPLITS = {"Warm split": ("warm", "random partition (warm split) as established by MixingDTA"),
          "Cold-target": ("cold-target", "cold-target split: test proteins unseen in training and validation"),
          "Cold-drug": ("cold-drug", "cold-drug split: test ligands unseen in training and validation")}
for ds, ds_desc in (("Davis", "Davis kinase binding affinities (pKd)"), ("KIBA", "KIBA kinase inhibitor bioactivities (unified KIBA score)")):
    for split_label, (sk, sdesc) in SPLITS.items():
        key = f"{ds}-{sk}"
        dataset(key, f"{ds} {sk} test set (PLABench)", f"{ds_desc}, {sdesc}.", f"{ds} as split by MixingDTA (PLABench)", sdesc, "Table 2; Methods 'Datasets'")
        protocol(key, f"PLABench {ds}, {sk} split", f"Affinity regression on {ds}, {sdesc}; models retrained by the benchmark authors.",
                 f"{ds} {sk} test set; MSE, RMSE, Pearson, Spearman, rm2 and CI as printed in Table 2", f"Table 2, '{ds}' columns, strategy '{split_label}'",
                 COMMON_LIM + ["Only the three sequence-based models (DeepDTA, LLF, MixingDTA) were retrained on Davis and KIBA."])
for series, target, n in (("L1000", "chymase", 17), ("L3000", "autotaxin", 123)):
    key = f"casp16-{series}"
    dataset(key, f"CASP16 ligand affinity series {series} ({target})", f"CASP16 pharmaceutical affinity series {series}, {target} ligands with experimental affinities.",
            "CASP16 protein-ligand affinity challenge", "Full series", "Table 3; Figure 2", population=f"{n} ligands ({target})")
    protocol(key, f"PLABench CASP16 {series} affinity", f"Affinity prediction on CASP16 series {series}; structure-based models given the same AlphaFold3-predicted complex structures.",
             f"CASP16 {series} series; MSE, RMSE, Pearson, Spearman, rm2 and CI as printed in Table 3", f"Table 3, '{series}' columns",
             COMMON_LIM + ["Structure-based models received AlphaFold3-predicted structures, not crystal structures (Results).",
                           "Affinities in this series have a narrow high-affinity range, which the authors note makes RMSE and ranking metrics disagree."])
dataset("chembl35", "PLABench ChEMBL35 leakage-controlled test set", "ChEMBL v35 test set curated by Shimizu et al., with ligands of ECFP4 Tanimoto similarity >= 0.85 to any training molecule of the nine models removed and targets with at least 10 compounds kept.",
        "ChEMBL v35 (PLABench filter)", "Held-out test set", "Results 'Large-scale pretraining...'; Table 4", population="4,862 complexes across 71 target proteins")
protocol("chembl35", "PLABench ChEMBL35 leakage-controlled affinity", "Affinity prediction on the leakage-controlled ChEMBL35 set; no retraining.",
         "ChEMBL35 filtered test set; MSE, RMSE, Pearson, Spearman, Kendall, rm2 and CI as printed in Table 4", "Table 4",
         COMMON_LIM + ["The text describes this set as target-centric but does not state whether Table 4 pools all complexes or averages over targets."])

NUM = r"-?\d+\.\d+"
def numbers(ln):
    return re.findall(r"(?<![\w.])" + NUM + r"(?![\w.])", ln)

def find(prefix, after=0):
    for i in range(after, len(lines)):
        if lines[i].strip().startswith(prefix):
            return i
    raise ValueError(prefix)

def add(table, model, setting, key, metric_label, printed, ln, colname):
    c = config(model, setting)
    e = b.rid("eval", model, key)
    if e not in b.ids:
        b.evaluation(e, f"{model} on PLABench {key}", SIDS, c, protos[key], datas[key], ORIGIN(model),
                     {"protocol_id": protos[key], "dataset_version": "PLABench bioRxiv v1", "split": key, "population": None,
                      "inputs": "Protein sequence and ligand SMILES" if CATEGORY[model] == "sequence-based" or model == "Boltz2" else "AlphaFold3-predicted protein-ligand complex structure",
                      "adaptation": "Retrained by the benchmark authors" if setting == "davis-kiba" else "Published model applied without retraining",
                      "metric_implementation": "As defined in Methods, 'Evaluation metrics'", "aggregation": None, "budget": None},
                     f"{table} row '{model}'" + (f", column group '{colname}'" if colname else ""))
    concept, direction, unit, udetail = METRICS[metric_label]
    loc = f"{table}, row '{model}', {colname + ', ' if colname else ''}column '{metric_label}' (text-layer line {ln})"
    b.result(b.rid("result", model, key, metric_label), f"{model} {key} {metric_label}", SRC, SIDS, e, printed, concept, direction, unit, loc,
             REVIEW(f"{table}, text-layer line {ln}."), qualifier=f"PLABench {key}", unit_detail=udetail)

# Table 2
t2 = find("Table 2 | Performance comparison of different models on Davis and KIBA")
t2e = find("Notes:", t2)
m2 = ["MSE", "RMSE", "Pearson", "Spearman", "rm2", "CI"]
rows = []
for i in range(t2, t2e):
    ln = lines[i]
    nums = numbers(ln)
    toks = ln.split()
    model = next((m for m in ("DeepDTA", "LLF", "MixingDTA") if m in toks), None)
    if model:
        assert len(nums) == 12, (i, ln)
        rows.append((i + 1, model, ln, nums))
assert [r[1] for r in rows] == ["DeepDTA", "LLF", "MixingDTA"] * 3, rows
order = list(SPLITS)
for k, (ln, model, raw, nums) in enumerate(rows):
    split_label = order[k // 3]
    if model == "LLF":
        assert split_label in raw, (split_label, raw)
    sk = SPLITS[split_label][0]
    for ds, chunk in (("Davis", nums[:6]), ("KIBA", nums[6:])):
        for mlab, v in zip(m2, chunk):
            add("Table 2", model, "davis-kiba", f"{ds}-{sk}", mlab, v, ln, f"strategy '{split_label}', dataset '{ds}'")

# Table 3
MODELS = ["Boltz2", "FlowDock", "FLOWR.ROOT", "Graph_RG", "LCDD-team", "MFE", "DeepDTA", "LLF", "MixingDTA"]
t3 = find("Table 3 | Performance comparison of different models on the CASP16 dataset")
t3e = find("Notes:", t3)
seen = []
for i in range(t3, t3e):
    toks = lines[i].split()
    if toks and toks[0] in MODELS:
        nums = numbers(lines[i])
        assert len(nums) == 12, (i, lines[i])
        seen.append(toks[0])
        for series, chunk in (("L1000", nums[:6]), ("L3000", nums[6:])):
            for mlab, v in zip(m2, chunk):
                add("Table 3", toks[0], "casp16-chembl35", f"casp16-{series}", mlab, v, i + 1, f"series '{series}'")
assert seen == MODELS, seen

# Table 4
t4 = find("Table 4 | Performance comparison of different models on the ChEMBL35 dataset")
t4e = find("Notes:", t4)
m4 = ["MSE", "RMSE", "Pearson", "Spearman", "Kendall", "rm2", "CI"]
seen = []
for i in range(t4, t4e):
    toks = lines[i].split()
    if toks and toks[0] in MODELS:
        nums = numbers(lines[i])
        assert len(nums) == 7, (i, lines[i])
        seen.append(toks[0])
        for mlab, v in zip(m4, nums):
            add("Table 4", toks[0], "casp16-chembl35", "chembl35", mlab, v, i + 1, None)
assert seen == MODELS, seen

# ---------------------------------------------------------------------------
# Corrections from the independent review (reviewer-mi-2, 2026-10-11), applied
# verbatim. Labels L1 to L7 are the reviewer's.
# ---------------------------------------------------------------------------
REVIEWER_NOTE = ("Claude review agent reviewer-mi-2, independent of the extractor "
                 "lit-microbial-interactions; no human review claimed")
by_id = {r["id"]: r for r in b.records}
SEQ = ("DeepDTA", "LLF", "MixingDTA")

# L1: the sequence models were retrained on PDBbind v2020 before CASP16 and ChEMBL35.
L1_ADAPT = ("Retrained by the benchmark authors on the PDBbind v2020 refined set (4,465 training, 497 "
            "validation complexes; longest single chain)")
L1_PARAMS = ("Retrained by the benchmark authors on the PDBbind v2020 refined set (CASF and CSAR overlaps and "
             "censored entries removed; 4,465 training and 497 validation complexes; random 90/10 split with "
             "early stopping; longest single chain); applied to CASP16 and ChEMBL35 without further training "
             "(Methods, 'PDBbind v2020 dataset')")
n = 0
for model in SEQ:
    for key in ("casp16-L1000", "casp16-L3000", "chembl35"):
        e = by_id[b.rid("eval", model, key)]["attributes"]
        e["comparison"]["adaptation"] = L1_ADAPT
        e.get("missing_metadata", {}).pop("comparison.adaptation", None)
        if not e.get("missing_metadata"):
            e.pop("missing_metadata", None)
        n += 1
    by_id[b.rid("config", model, "casp16-chembl35")]["attributes"]["parameters"] = L1_PARAMS
assert n == 9, n

# L2: the source conflicts with itself about whether MFE was retrained.
L2_NOTE = ("Results (lines 78-80) say structure-based models used official pretrained checkpoints; Data "
           "availability (line 542) lists retrained MFE checkpoints")
for key in ("casp16-L1000", "casp16-L3000", "chembl35"):
    e = by_id[b.rid("eval", "MFE", key)]["attributes"]
    e["comparison"]["adaptation"] = None
    e.setdefault("missing_metadata", {})["comparison.adaptation"] = {"reason": "conflicting", "note": L2_NOTE}
    e["missing_metadata"] = dict(sorted(e["missing_metadata"].items()))
cfg = by_id[b.rid("config", "MFE", "casp16-chembl35")]["attributes"]
cfg["parameters"] = cfg["parameters"] + ". " + L2_NOTE

# L3: the populations are stated in the source.
L3 = {"casp16-L1000": "17 ligands (chymase, CASP16 series L1000)",
      "casp16-L3000": "123 ligands (autotaxin, CASP16 series L3000)",
      "chembl35": "4,862 ligand-target pairs across 71 targets"}
n = 0
for model in MODELS:
    for key, pop in L3.items():
        e = by_id[b.rid("eval", model, key)]["attributes"]
        e["comparison"]["population"] = pop
        e.get("missing_metadata", {}).pop("comparison.population", None)
        if not e.get("missing_metadata"):
            e.pop("missing_metadata", None)
        n += 1
assert n == 27, n

# L4: the protocol limitations contradicted each other about pooling.
L4_CHEMBL = ("Methods ('Evaluation metrics') define each metric over N target-ligand pairs, but the source does "
             "not state whether Table 4 pools all 4,862 pairs or averages per-target values.")
L4_CASP = ("Each series is a single target; Figure 2 states that each tau is computed over all ligands of a "
           "series, and Methods define the metrics over all test pairs.")
for key, text in (("chembl35", L4_CHEMBL), ("casp16-L1000", L4_CASP), ("casp16-L3000", L4_CASP)):
    lims = by_id[protos[key]]["attributes"]["limitations"]
    assert lims[0].startswith("Metrics are computed over all test pairs"), lims[0]
    lims[0] = text

# L5: the cold-split aggregation is stated, though the function is not.
L5 = ("Predictions of the five fold models on one fixed test set aggregated (Methods lines 389-394); the "
      "aggregation function is not stated")
n = 0
for model in SEQ:
    for ds in ("Davis", "KIBA"):
        for sk in ("cold-target", "cold-drug"):
            e = by_id[b.rid("eval", model, f"{ds}-{sk}")]["attributes"]
            e["comparison"]["aggregation"] = L5
            e.get("missing_metadata", {}).pop("comparison.aggregation", None)
            if not e.get("missing_metadata"):
                e.pop("missing_metadata", None)
            n += 1
assert n == 12, n

# L6: unit_detail missed ChEMBL35 and read "error" for a squared quantity.
L6_CHEMBL = ("ChEMBL35 Kd, Ki or IC50 affinities (EC50 excluded; Methods lines 445-450); the scale and unit are "
             "not printed")
n_c, n_o = 0, 0
for r in b.records:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    if a["metric"] not in ("mean-squared-error", "root-mean-squared-error"):
        continue
    squared = a["metric"] == "mean-squared-error"
    if r["id"].endswith("-chembl35-mse") or r["id"].endswith("-chembl35-rmse"):
        a["unit_detail"] = ("Squared error; " + L6_CHEMBL) if squared else L6_CHEMBL
        n_c += 1
    elif squared:
        assert a["unit_detail"].startswith("Error in"), a["unit_detail"]
        a["unit_detail"] = "Squared error in" + a["unit_detail"][len("Error in"):]
        n_o += 1
assert (n_c, n_o) == (18, 36), (n_c, n_o)

# L7: the Boltz-2 inference settings and the standardised dataset sizes are printed.
cfg = by_id[b.rid("config", "Boltz2", "casp16-chembl35")]["attributes"]
cfg["parameters"] = cfg["parameters"] + (". 10 structural samples, affinity scored on the highest-ipTM pose, "
                                         "500 sampling steps, 5 recycling steps (Methods lines 437-439)")
L7_DATA = {"Davis": "Standardised Davis: 25,772 pairs, 379 unique sequences, 68 ligands (Methods lines 363-369)",
           "KIBA": "TDC KIBA: 117,657 pairs, 229 proteins, 2,068 ligands (Methods lines 382-384)"}
n = 0
for ds, pop in L7_DATA.items():
    for sk in ("warm", "cold-target", "cold-drug"):
        by_id[datas[f"{ds}-{sk}"]]["attributes"]["population"] = pop
        n += 1
assert n == 6, n

R_METHODS = ["source-hash-verification", "pdf-text-parse", "independent-cell-check", "rendered-source-visual-check"]
R_NOTE = ("Re-downloaded the bioRxiv PDF: its hash differs because of the per-request banner, but the "
          "pdftotext -layout text layer hashes exactly to the recorded value, so the content checked is the "
          "content extracted. Parsed all 279 cells (Table 2: 108, Table 3: 108, Table 4: 63) with an "
          "independent parser, mapping every result through its evaluation, configuration and protocol to a "
          "model, split and metric cell: all 279 printed and numeric values and all locator line numbers "
          "match, with no cell missed. Read 44 sampled values covering all three tables and all nine models "
          "from rendered pages 6, 10 and 12: 44 of 44 match. claims.csv rows, printed values and locators "
          "equal the batch.")
for r in b.records:
    if r["kind"] == "result":
        old = r["attributes"]["review"]
        r["attributes"]["review"] = reviewed_review(R_METHODS, R_NOTE, REVIEWER_NOTE, SHA, URL,
                                                    old["method_note"], R_NOTE)
by_id[SRC]["attributes"]["review"] = source_review(
    REVIEWER_NOTE,
    "PDF re-downloaded; the per-request bioRxiv banner changes the PDF hash, so the pdftotext -layout text "
    "layer was rehashed instead and matches the recorded text-layer hash.")
mark_reviewed(b)

counts = b.write()
print(json.dumps(counts))
