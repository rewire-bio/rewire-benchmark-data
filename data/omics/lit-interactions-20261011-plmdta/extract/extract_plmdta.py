"""PLM-GraphDTA (Marijan and Tanasijevic, bioRxiv 10.64898/2026.08.31.748056v1): Tables 2 and 3.

Usage: python3 -I extract_plmdta.py <biorxiv-pdf> <pdftotext -layout output> <batch-folder>

The ProstT5 family record is created by the lit-interactions-20261011-ppiemb batch, which must be
added to the store first.
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, reviewed_review, source_review, mark_reviewed, sha256, slug, num

pdf_path, txt_path, folder = sys.argv[1], sys.argv[2], sys.argv[3]
SHA = sha256(pdf_path)
TXT_SHA = sha256(txt_path)
URL = "https://www.biorxiv.org/content/10.64898/2026.08.31.748056v1.full.pdf"
assert SHA == "11b88d5ab2964b581430454d0d9e7848739819d52ec2e338e2a6412cbd259163", SHA

P = "lit-interactions-20261011-plmdta"
b = Batch(folder, P, areas=["molecular-interactions"])
SRC = b.source(P + "-source-marijan2026", "Comprehensive Evaluation of Protein Language Model Embeddings for Drug-Target Affinity Prediction", {
    "url": "https://doi.org/10.64898/2026.08.31.748056", "artifact_url": URL,
    "version": "bioRxiv 10.64898/2026.08.31.748056v1 (posted 2026-09-03); 24-page PDF",
    "retrieved_at": "2026-10-11T21:27:40Z", "artifact_sha256": SHA, "doi": "10.64898/2026.08.31.748056",
    "publication_status": "preprint", "licence": "CC-BY-NC-4.0", "media_type": "application/pdf",
    "code_url": "https://github.com/matija-marijan/PLM-GraphDTA",
    "limitations": [
        "bioRxiv adds a per-request banner, so the PDF hash describes this one retrieval.",
        "Values were read from the pdftotext (poppler 26.08.0) layout text layer, SHA-256 " + TXT_SHA + ". The PDF is not archived in the repository.",
        "Tables 2 and 3 print one PLM per drug backbone (the 5-fold CV winner); the per-PLM comparison (ESM2 8M/150M/650M, ESMC 300M/600M, DeepFRI, ProstT5) is in Appendix D figures and was not read.",
        "Cold-start results (Figures 4 and 5) are figures only and were not read.",
        "Italic and bold marking of best values is not carried by the text layer.",
    ]})
SIDS = [SRC]
REVIEW = lambda loc: extraction_review(["pdf-text-parse"],
    "Parsed the pdftotext -layout text layer of the pinned bioRxiv PDF with extract/extract_plmdta.py; each row's method, protein and drug representation and two values asserted. " + loc,
    SHA, URL)

lines = open(txt_path, encoding="utf-8").read().split("\n")

EXISTING = {"DeepDTA": "identity-model-deepdta", "ESMC 600M": "discovery-model-esmc", "ESM2 650M": "discovery-model-esm-2",
            "ProstT5": "lit-interactions-20261011-ppiemb-model-prostt5"}
NEW = {
    "KronRLS": ("method", "KronRLS: Kronecker regularised least squares on drug and target similarity kernels.", ["supervised_machine_learning"]),
    "SimBoost": ("method", "SimBoost: gradient-boosted trees on similarity, network and interaction features.", ["supervised_machine_learning"]),
    "GraphDTA": ("model", "GraphDTA: graph neural network drug encoder with a 1D-convolution protein encoder.", ["supervised_machine_learning"]),
    "PGraphDTA": ("model", "PGraphDTA: GraphDTA variant using protein language model embeddings (ESM-2 variant without contact maps used here).", ["foundation_model"]),
    "PLM-GraphDTA": ("model", "PLM-GraphDTA: GraphDTA drug encoders with frozen protein language model embeddings as the protein representation (this paper).", ["foundation_model"]),
    "DeepGraphDTA": ("model", "DeepGraphDTA: GraphDTA with a transposed-input 1D convolution protein encoder (this paper).", ["supervised_machine_learning"]),
}
fam_ids = {}
def fam_id(f):
    if f in EXISTING:
        return EXISTING[f]
    if f not in fam_ids:
        kind, desc, mt = NEW[f]
        rid = b.rid(kind, f)
        b.entity(kind, rid, f, desc, SIDS, {"reported_name": f, "entity_level": "family" if kind == "model" else "method",
                 "source_locator": "Section 3.3 'Baseline models'; Section 2; Tables 2 and 3",
                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the evaluated setup is on the configuration"}}},
                 method_types=mt)
        fam_ids[f] = rid
    return fam_ids[f]

OWN = ("PLM-GraphDTA", "DeepGraphDTA")
configs = {}
def config(method, prot, drug):
    key = (method, prot, drug)
    if key in configs:
        return configs[key]
    rid = b.rid("config", method, prot, drug)
    links = [{"relation": "configuration_of", "target_id": fam_id(method)}]
    if method in ("PLM-GraphDTA", "PGraphDTA"):
        links.append({"relation": "uses_model", "target_id": EXISTING[prot]})
    fm = method in ("PLM-GraphDTA", "PGraphDTA")
    attrs = {"reported_name": f"{method} ({prot}; {drug})", "foundation_model_eligible": fm,
             "parameters": f"Protein representation: {prot}; drug representation: {drug}" + (" (kernel size in brackets selected by 5-fold CV)" if method == "DeepGraphDTA" else ""),
             "source_locator": f"Tables 2 and 3, row '{method}' with protein '{prot}' and drug '{drug}'",
             "access_reuse": "Code, trained models and data at https://github.com/matija-marijan/PLM-GraphDTA (source abstract)" if method in OWN else "Not stated in the source",
             "missing_metadata": {"version": {"reason": "unreported", "note": "No checkpoint version printed"}}}
    b.entity("configuration", rid, f"{method} with {prot} protein and {drug} drug representation", f"{method} configuration as printed in Tables 2 and 3.", SIDS, attrs,
             method_types=["foundation_model"] if fm else (["conventional_pipeline"] if method in ("KronRLS",) else ["supervised_machine_learning"]), links=links)
    configs[key] = rid
    return rid

BENCH = b.entity("benchmark", b.rid("benchmark", "davis-kiba-dta-deepdta-split"), "Davis and KIBA drug-target affinity benchmark (DeepDTA split)",
    "Drug-target affinity regression on Davis and KIBA with the predefined DeepDTA training and test folds (5:1).", SIDS,
    {"entity_level": "suite", "version": "DeepDTA folds (Ozturk et al. 2018), as used in Marijan and Tanasijevic 2026",
     "task": "Drug-target binding affinity regression", "scope_note": "Holdout test fold results from Tables 2 and 3; cold-start results are figures only.",
     "source_locator": "Sections 3.1 and 3.4; Tables 2 and 3"})
datas, protos = {}, {}
for ds, desc, loc in (("Davis", "Davis kinase inhibitor selectivity dataset: 442 kinases, 68 inhibitors, 30,056 pairs; Kd log-transformed to pKd following He et al. 2017", "Section 3.1.1"),
                      ("KIBA", "KIBA kinase inhibitor bioactivity dataset filtered as in He et al. 2017: 2,111 drugs, 229 proteins, 118,254 KIBA scores", "Section 3.1.2")):
    datas[ds] = b.entity("dataset", b.rid("data", ds, "deepdta-holdout"), f"{ds} holdout test fold (DeepDTA split)", desc + "; predefined DeepDTA holdout test fold.", SIDS,
                         {"version": "DeepDTA repository data", "split": "Predefined DeepDTA holdout test fold (train:test 5:1)", "source_locator": loc + "; Section 3.4"})
    protos[ds] = b.entity("protocol", b.rid("protocol", ds, "deepdta-holdout"), f"{ds} drug-target affinity, DeepDTA holdout fold",
        f"Affinity regression on the {ds} DeepDTA holdout fold; CI and MSE as printed.", SIDS,
        {"protocol": f"{ds} DeepDTA holdout test fold; concordance index and MSE", "version": "DeepDTA split",
         "limitations": ["For the proposed models, values are the mean over 5 random seeds (Section 3.4.3); the source does not say whether baseline values were rerun or taken from earlier papers.",
                         "Rows are sorted by CI and only the selected PLM per drug backbone is shown."],
         "source_locator": "Table 2" if ds == "Davis" else "Table 3"},
        links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": datas[ds]}])

def find(prefix, after=0):
    for i in range(after, len(lines)):
        if lines[i].strip().startswith(prefix):
            return i
    raise ValueError(prefix)

ROW = re.compile(r"^\s*(KronRLS|GraphDTA|SimBoost|PGraphDTA|DeepDTA|PLM-GraphDTA|DeepGraphDTA)(?: \[[^\]]+\])?\s{2,}(.+?)\s{2,}(.+?)\s{2,}(\d\.\d{3})\s+(\d\.\d{3})\s*$")
for table, ds in (("Table 2", "Davis"), ("Table 3", "KIBA")):
    start = find(f"{table}: Affinity prediction performance comparison on the {ds} dataset")
    end = find("Note: Values in italics", start)
    hdr = lines[start + 2]
    assert "CI ↑" in hdr and "MSE ↓" in hdr, hdr
    rows = []
    for i in range(start, end):
        m = ROW.match(lines[i])
        if m:
            rows.append((i + 1,) + m.groups())
    assert len(rows) == 16, (table, len(rows))
    for (ln, method, prot, drug, ci, mse) in rows:
        prot, drug = prot.strip(), drug.strip()
        c = config(method, prot, drug)
        origin = "author_reported" if method in OWN else "unreported"
        e = b.rid("eval", method, prot, drug, ds)
        b.evaluation(e, f"{method} ({prot}; {drug}) on {ds}", SIDS, c, protos[ds], datas[ds], origin,
                     {"protocol_id": protos[ds], "dataset_version": "DeepDTA split", "split": "Holdout test fold", "population": None,
                      "inputs": "Protein sequence (padded or truncated to 1000 residues) and drug SMILES or graph",
                      "adaptation": "Trained on all five training folds" if method in OWN else None,
                      "metric_implementation": "CI and MSE as printed",
                      "aggregation": "Mean over 5 random seeds" if method in OWN else None, "budget": None},
                     f"{table} row '{method}', protein '{prot}', drug '{drug}'",
                     missing={"comparison.adaptation": {"reason": "unreported", "note": "Baseline training not described"}} if method not in OWN else None)
        for mlab, v, concept, direction, unit, ud in (("CI", ci, "concordance-index", "higher", "unitless", None),
                                                      ("MSE", mse, "mean-squared-error", "lower", "unit-unreported",
                                                       "Squared error in the dataset's affinity scale (Davis pKd; KIBA score); the table prints no unit")):
            loc = f"{table}, row '{method}' with protein '{prot}' and drug '{drug}', column '{mlab}' (text-layer line {ln})"
            b.result(b.rid("result", method, prot, drug, ds, mlab), f"{method} {prot} {drug} {ds} {mlab}", SRC, SIDS, e, v, concept, direction, unit, loc,
                     REVIEW(f"{table}, text-layer line {ln}."), qualifier=f"{ds} DeepDTA holdout fold", unit_detail=ud)

# ---------------------------------------------------------------------------
# Corrections from the independent review (reviewer-mi-2, 2026-10-11), applied
# verbatim. Labels D1 to D3 are the reviewer's.
# ---------------------------------------------------------------------------
REVIEWER_NOTE = ("Claude review agent reviewer-mi-2, independent of the extractor "
                 "lit-microbial-interactions; no human review claimed")
by_id = {r["id"]: r for r in b.records}

# D1: the Davis data are the Monteiro et al. 2022 corrected version, and Appendix A says every model
# was trained on it, which also settles the baselines' origin and adaptation.
davis = by_id[datas["Davis"]]["attributes"]
davis["version"] = ("Davis as corrected by Monteiro et al. 2022 (mutant sequences resolved; Appendix A), "
                    "DeepDTA folds")
by_id[datas["Davis"]]["description"] = by_id[datas["Davis"]]["description"] + (
    " Evaluated on the corrected version with mutant sequences resolved (Appendix A); not the commonly used "
    "DeepDTA repository sequences.")
D1_ADAPT = ("Trained by the study authors on the DeepDTA training folds of the corrected Davis set "
            "(Appendix A)")
n = 0
for r in b.records:
    if r["kind"] != "evaluation" or r["attributes"]["protocol"] != protos["Davis"]:
        continue
    if r["attributes"]["origin"] != "unreported":
        continue
    a = r["attributes"]
    a["origin"] = "independent_paper"
    a["comparison"]["adaptation"] = D1_ADAPT
    a.get("missing_metadata", {}).pop("comparison.adaptation", None)
    if not a.get("missing_metadata"):
        a.pop("missing_metadata", None)
    n += 1
assert n == 8, n
lims = by_id[protos["Davis"]]["attributes"]["limitations"]
assert lims[0].startswith("For the proposed models, values are the mean over 5 random seeds"), lims[0]
lims[0] = ("Proposed models: mean over 5 random seeds (Section 3.4.3). Appendix A states that all models, "
           "baselines included, were trained and evaluated on the corrected Davis set; the seed averaging of "
           "baselines is not stated.")

# D2: three KIBA baseline rows equal the values printed in Ozturk et al. 2018.
D2_NOTE = ("Printed values identical to Ozturk et al. 2018 (arXiv 1801.10193v2) KIBA table; likely copied, "
           "not rerun.")
n = 0
for model, prot, drug in (("KronRLS", "Similarity vector", "Similarity vector"),
                          ("SimBoost", "Similarity features", "Similarity features"),
                          ("DeepDTA", "1D conv.", "1D conv.")):
    a = by_id[b.rid("eval", model, prot, drug, "KIBA")]["attributes"]
    assert a["origin"] == "unreported", (model, a["origin"])
    entry = a["missing_metadata"]["comparison.adaptation"]
    entry["note"] = entry["note"] + ". " + D2_NOTE
    n += 1
assert n == 3, n
by_id[SRC]["attributes"]["evidence_concerns"] = [{
    "source_id": SRC,
    "message": ("Table 3 KIBA rows KronRLS, SimBoost and DeepDTA equal the values printed in Ozturk et al. "
                "2018, while the proposed models are 5-seed means; the rows may not share a training run or "
                "protocol. Do not compare these three rows against the proposed models automatically."),
    "source_locator": "Table 3, rows KronRLS, SimBoost, DeepDTA",
    "artifact_sha256": SHA, "reviewed_at": "2026-10-11T00:00:00Z", "review_method": "ai-assisted-source-review"}]
by_id[protos["KIBA"]]["attributes"]["limitations"].append(
    "Table 3 KIBA rows KronRLS, SimBoost and DeepDTA equal the values printed in Ozturk et al. 2018, while "
    "the proposed models are 5-seed means; the rows may not share a training run or protocol.")

# D3: versions that the source does print.
D3 = {b.rid("config", "PGraphDTA", "ESM2 650M", "GAT"): "ESM-2 650M, no contact maps (Section 3.3)"}
for cid, r in list(by_id.items()):
    if r["kind"] == "configuration" and "plm-graphdta-esmc-600m" in cid:
        D3[cid] = "ESMC 600M"
assert len(D3) == 5, sorted(D3)
for cid, version in D3.items():
    a = by_id[cid]["attributes"]
    a["version"] = version
    a.get("missing_metadata", {}).pop("version", None)
    if not a.get("missing_metadata"):
        a.pop("missing_metadata", None)

R_METHODS = ["source-hash-verification", "pdf-text-parse", "independent-cell-check",
             "rendered-source-visual-check"]
R_NOTE = ("Re-downloaded the bioRxiv PDF: its hash differs because of the per-request banner, but the "
          "pdftotext -layout text layer hashes exactly to the recorded value, so the content checked is the "
          "content extracted. Parsed all 32 rows and 64 cells with an independent parser, mapping every "
          "result through its evaluation, configuration and protocol: all match and no cell was missed. Read "
          "44 values covering both tables and every model family from rendered pages 10 and 11: 44 of 44 "
          "match, and the prose percentages (16.08, 0.89, 1.35 and 13.89 percent) follow from the printed "
          "cells. The three KIBA baseline rows were checked against the DeepDTA paper's own KIBA table, "
          "which is what the evidence concern records.")
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
