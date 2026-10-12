"""Protein embeddings for GNN-based PPI prediction (Briefings in Bioinformatics 2026, bbag313): Tables 5 and 6.

Usage: python3 -I extract_ppiemb.py <fulltext.xml> <batch-folder>
"""
import sys, os, json
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, reviewed_review, source_review, mark_reviewed, sha256, slug, num

xml_path, folder = sys.argv[1], sys.argv[2]
SHA = sha256(xml_path)
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13280947/fullTextXML"
assert SHA == "360d4f17b779e07f170c3f0c3755bfbfddd064831bf5a81d2642a4cfffd4866c", SHA

P = "lit-interactions-20261011-ppiemb"
b = Batch(folder, P, areas=["molecular-interactions", "proteins-complexes"])
SRC = b.source(P + "-source-bbag313", "The role of protein embeddings for protein-protein interaction prediction with graph neural networks", {
    "url": "https://doi.org/10.1093/bib/bbag313", "artifact_url": URL,
    "version": "Briefings in Bioinformatics 2026, bbag313; PMC13280947 full-text XML",
    "retrieved_at": "2026-10-11T21:27:23Z", "artifact_sha256": SHA, "doi": "10.1093/bib/bbag313",
    "publication_status": "peer_reviewed", "licence": "CC-BY-NC-4.0", "media_type": "application/xml",
    "limitations": [
        "The supplementary material (Tables S1-S7: datasets, original OGBl-ppa leaderboard values, embedding and GNN parameters) was not retrieved.",
        "No uncertainty, seeds or repeat counts are printed with Tables 5 and 6.",
    ],
    "evidence_concerns": [
        {"source_id": P + "-source-bbag313", "artifact_sha256": SHA, "source_locator": "Results and discussion, first paragraph; Tables 5 and 6",
         "message": "The text's summary does not match the tables: it lists ProtT5 among structure embeddings while the tables print ProstT5; it reports a GraphSAGE with DistMult result (+38% Hits@100 on HuRI) although DistMult is not a column; and the stated gains (for example ESM-2 with GraphSAGE +6% Hits@100 on OGBl-ppa) cannot be reproduced from the printed table values (GS random 0.0104, ESM-2 0.2421). Values are kept as printed; comparisons should rely on the tables only after a reviewer has judged this.",
         "reviewed_at": "2026-10-11T21:40:00Z", "review_method": "ai-assisted-source-review"}]})
SIDS = [SRC]
REVIEW = lambda loc: extraction_review(["deterministic-table-parse"],
    "Parsed the <td> cells of the pinned PMC XML with extract/extract_ppiemb.py; header rows and row lengths asserted. " + loc, SHA, URL)

root = ET.fromstring(open(xml_path, "rb").read())
tables = {}
for tw in root.iter("table-wrap"):
    lab = " ".join("".join(tw.find("label").itertext()).split())
    rows = [[" ".join("".join(c.itertext()).split()) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
    tables[lab] = rows

COLS = ["Random", "ESM-2", "ProtTrans", "ProGen2", "ESM-IF1", "ProstT5", "PiFold", "TransE", "ComplEx", "RDF2Vec", "Ensemble"]
GROUP = {"Random": "random initial features", "ESM-2": "sequence", "ProtTrans": "sequence", "ProGen2": "sequence",
         "ESM-IF1": "structure", "ProstT5": "structure", "PiFold": "structure", "TransE": "function (knowledge-graph embedding)",
         "ComplEx": "function (knowledge-graph embedding)", "RDF2Vec": "function (knowledge-graph embedding)", "Ensemble": "majority-vote ensemble"}
ARCH = {"GCN": "GCN", "GS": "GraphSAGE", "N-GCN": "NGNN with GCN", "N-GS": "NGNN with GraphSAGE",
        "N-GCN+S": "NGNN with GCN combined with SEAL", "N-GS+S": "NGNN with GraphSAGE combined with SEAL",
        "MLP": "MLP on concatenated protein embeddings (protein-only baseline, no network)"}

EXISTING = {"ESM-2": "discovery-model-esm-2", "ProGen2": "uc20260930-model-progen2", "ESM-IF1": "discovery-model-esm-if1"}
NEW_EMB = {
    "ProtTrans": ("model", "ProtTrans protein language model family (T5-based).", ["foundation_model"]),
    "ProstT5": ("model", "ProstT5 bilingual sequence and 3Di structure protein language model.", ["foundation_model"]),
    "PiFold": ("model", "PiFold graph-transformer inverse-folding model.", ["foundation_model"]),
    "TransE": ("method", "TransE translation-based knowledge-graph embedding method.", ["supervised_machine_learning"]),
    "ComplEx": ("method", "ComplEx semantic-matching knowledge-graph embedding method.", ["supervised_machine_learning"]),
    "RDF2Vec": ("method", "RDF2Vec random-walk knowledge-graph embedding method.", ["supervised_machine_learning"]),
}
emb_ids = {}
def emb_id(name):
    if name in EXISTING:
        return EXISTING[name]
    if name not in emb_ids:
        kind, desc, mt = NEW_EMB[name]
        rid = b.rid(kind, name)
        b.entity(kind, rid, name, desc, SIDS, {"reported_name": name, "entity_level": "family" if kind == "model" else "method",
                 "source_locator": "Experimental design; Table 5 and 6 column headers",
                 "missing_metadata": {"version": {"reason": "unreported", "note": "No checkpoint or version printed in the main text; parameters are in Supplementary Table S3, not retrieved"}}},
                 method_types=mt)
        emb_ids[name] = rid
    return emb_ids[name]

arch_ids = {}
def arch_id(a):
    if a not in arch_ids:
        rid = b.rid("method", ARCH[a] if a != "MLP" else "PPI MLP protein-only baseline")
        b.entity("method", rid, ARCH[a] if a != "MLP" else "MLP protein-only PPI baseline",
                 ("Graph neural network link predictor for PPI networks: " + ARCH[a] + "." if a != "MLP" else
                  "Binary PPI classifier: an MLP on concatenated protein embeddings, with no network information (ablation for RQ3)."),
                 SIDS, {"reported_name": a, "entity_level": "method", "source_locator": "Experimental design; Tables 5 and 6 row labels",
                        "missing_metadata": {"version": {"reason": "unreported", "note": "GNN parameters are in Supplementary Table S7, not retrieved"}}},
                 method_types=["supervised_machine_learning"])
        arch_ids[a] = rid
    return arch_ids[a]

ens_id = None
def ensemble_id():
    global ens_id
    if ens_id is None:
        ens_id = b.entity("method", b.rid("method", "majority-vote embedding ensemble"), "Majority-vote ensemble over protein embeddings (PPI)",
                          "Majority-vote ensemble aggregating predictions from models using the different protein representations.", SIDS,
                          {"reported_name": "Ensemble", "entity_level": "method", "source_locator": "Experimental design; Results and discussion",
                           "missing_metadata": {"version": {"reason": "inapplicable"}}}, method_types=["supervised_machine_learning"])
    return ens_id

configs = {}
def config(arch, col):
    key = (arch, col)
    if key in configs:
        return configs[key]
    rid = b.rid("config", arch, col)
    links = [{"relation": "configuration_of", "target_id": arch_id(arch)}]
    if col == "Ensemble":
        links.append({"relation": "uses_model", "target_id": ensemble_id()})
    elif col != "Random":
        links.append({"relation": "uses_model", "target_id": emb_id(col)})
    fm = col in ("ESM-2", "ProtTrans", "ProGen2", "ESM-IF1", "ProstT5", "PiFold")
    feat = {"Random": "randomly initialised node features (baseline)", "Ensemble": "majority vote across the representations"}.get(col, f"{col} protein embeddings ({GROUP[col]})")
    attrs = {"reported_name": f"{arch} / {col}", "foundation_model_eligible": fm,
             "parameters": f"{ARCH[arch]}; node features: {feat}. Leaderboard hyperparameters reproduced for OGBl-ppa (Experimental design).",
             "source_locator": f"Tables 5 and 6, row '{arch}', column '{col}'",
             "access_reuse": "Not stated in the source",
             "missing_metadata": {"version": {"reason": "unreported", "note": "Embedding and GNN parameters are in Supplementary Tables S3, S5-S7, not retrieved"}}}
    b.entity("configuration", rid, f"{ARCH[arch]} with {feat} (PPI embeddings study)", f"{ARCH[arch]} using {feat}, as evaluated for PPI prediction.", SIDS, attrs,
             method_types=["foundation_model"] if fm else ["supervised_machine_learning"], links=links)
    configs[key] = rid
    return rid

BENCH = b.entity("benchmark", b.rid("benchmark", "ppi-embedding-gnn-comparison"), "Protein embeddings for GNN PPI prediction (OGBl-ppa and HuRI)",
    "Comparison of sequence, structure and function protein embeddings as node features for graph neural network PPI link prediction on OGBl-ppa and HuRI, with a protein-only MLP ablation.",
    SIDS, {"entity_level": "suite", "version": "Briefings in Bioinformatics 2026, bbag313", "task": "Protein-protein interaction link prediction",
           "scope_note": "Tables 5 (Hits@100) and 6 (Accuracy). Supplementary leaderboard values (Table S2) not extracted.",
           "source_locator": "Experimental design; Tables 4-6"})

DATA = {"OGBl-ppa": ("ogbl-ppa", "Open Graph Benchmark ogbl-ppa protein association graph (576,289 nodes, 30,326,273 edges; STRING-derived, multi-species).", "576 289 nodes; 30 326 273 edges"),
        "HuRI": ("huri", "Human Reference Interactome (HuRI) PPI graph (8,248 nodes, 51,813 edges).", "8248 nodes; 51 813 edges")}
datas, protos = {}, {}
for ds, (key, desc, pop) in DATA.items():
    datas[ds] = b.entity("dataset", b.rid("data", key), f"{ds} PPI graph (embedding study)", desc, SIDS,
                         {"version": "As used in bbag313 (OGB release for OGBl-ppa)", "split": "Test edges as defined by the benchmark", "population": pop,
                          "source_locator": "Table 4; Datasets"})
    for metric, (concept, table) in {"Hits@100": ("hits-at-100", "Table 5"), "Accuracy": ("accuracy", "Table 6")}.items():
        protos[(ds, metric)] = b.entity("protocol", b.rid("protocol", key, metric), f"{ds} PPI link prediction, {metric} ({table})",
            f"PPI link prediction on {ds} with protein embeddings as GNN node features; {metric} as printed in {table}.", SIDS,
            {"protocol": f"{ds} PPI link prediction; {metric}", "version": "bbag313", "metric": concept, "metric_direction": "higher",
             "unit": "fraction", "limitations": [
                 "The authors ran every configuration; none of the embedding models is theirs.",
                 "No uncertainty or number of runs is printed.",
                 "The MLP row is a protein-only binary classifier on concatenated embeddings, not a GNN.",
                 "The text's summary of gains does not match the printed values; see the source's evidence concern."],
             "source_locator": f"{table}, block '{ds}'"},
            links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": datas[ds]}])

def parse(table, metric, concept):
    rows = tables[table]
    assert rows[0][:5] == ["", "", "", "Sequence", "Structure"] or rows[0][-4:] == ["Sequence", "Structure", "Function", "Ensemble"], rows[0]
    hdr = [c for c in rows[1] if c]
    assert hdr == COLS[:-1], hdr
    ds = None
    n = 0
    for i, row in enumerate(rows[2:], 3):
        cells = [c for c in row]
        if cells[0] in DATA:
            ds = cells[0]
            cells = cells[1:]
        elif cells[0] == "":
            cells = cells[1:]
        # One HuRI row is laid out without the leading empty cell and with a trailing empty cell instead.
        if cells and cells[-1] == "" and len(cells) == 13:
            cells = cells[:-1]
        arch, vals = cells[0], cells[1:]
        assert arch in ARCH, (table, i, row)
        assert len(vals) == 11, (table, i, row)
        for col, v in zip(COLS, vals):
            assert num(v) is not None, (table, i, col, v)
            c = config(arch, col)
            e = b.rid("eval", arch, col, DATA[ds][0], metric)
            b.evaluation(e, f"{ARCH[arch]} / {col} on {ds} ({metric})", SIDS, c, protos[(ds, metric)], datas[ds], "independent_paper",
                         {"protocol_id": protos[(ds, metric)], "dataset_version": "bbag313", "split": "Benchmark test edges", "population": None,
                          "inputs": f"PPI graph with {GROUP[col]} node features" if arch != "MLP" else f"Concatenated protein embeddings ({GROUP[col]})",
                          "adaptation": "Trained by the study authors", "metric_implementation": f"{metric} as printed", "aggregation": None, "budget": None},
                         f"{table}, block '{ds}', row '{arch}', column '{col}'")
            loc = f"{table}, block '{ds}', row '{arch}', column '{col}'"
            b.result(b.rid("result", arch, col, DATA[ds][0], metric), f"{arch} {col} {ds} {metric}", SRC, SIDS, e, v, concept, "higher", "fraction",
                     loc, REVIEW(f"{table} body row {i}."), qualifier=f"{ds} PPI link prediction")
            n += 1
    return n

n5 = parse("Table 5", "Hits@100", "hits-at-100")
n6 = parse("Table 6", "Accuracy", "accuracy")
assert n5 == n6 == 154, (n5, n6)
# ---------------------------------------------------------------------------
# Corrections from the independent review (reviewer-mi-2, 2026-10-11), applied
# verbatim. Labels P1 to P5 are the reviewer's.
# ---------------------------------------------------------------------------
REVIEWER_NOTE = ("Claude review agent reviewer-mi-2, independent of the extractor "
                 "lit-microbial-interactions; no human review claimed")
by_id = {r["id"]: r for r in b.records}

# P1: repeated runs exist, but only a table-wide maximum standard deviation is printed.
P1_LIM = ("No per-cell uncertainty or run count is printed; the footnote of Tables 5 and 6 gives only the "
          "table-wide maximum standard deviation (0.0711 OGBl-ppa, 0.0928 HuRI).")
for key in protos:
    lims = by_id[protos[key]]["attributes"]["limitations"]
    hits = [i for i, l in enumerate(lims) if l == "No uncertainty or number of runs is printed."]
    assert len(hits) == 1, lims
    lims[hits[0]] = P1_LIM
src_lims = by_id[SRC]["attributes"]["limitations"]
hits = [i for i, l in enumerate(src_lims) if l.startswith("No uncertainty, seeds or repeat counts")]
assert len(hits) == 1, src_lims
src_lims[hits[0]] = P1_LIM
n = 0
for r in b.records:
    if r["kind"] == "result":
        r["attributes"]["missing_metadata"]["uncertainty"]["note"] = (
            "Only a table-wide maximum SD is printed (Table 5/6 footnote)")
        n += 1
assert n == 308, n

# P2: the HuRI split was invented and its dataset version was a copy error.
huri = by_id[datas["HuRI"]]["attributes"]
huri["version"] = "HuRI as used in bbag313; release and file in Supplementary Table S1 (not retrieved)"
huri.pop("split", None)
huri["missing_metadata"] = {"split": {"reason": "unreported",
                                      "note": "Main text does not describe the HuRI train/test edge split"}}
by_id[datas["OGBl-ppa"]]["attributes"]["split"] = (
    "Not stated in the main text; leaderboard hyperparameters reproduced (Experimental design), so the OGB "
    "split is implied but not confirmed")
n = 0
for r in b.records:
    if r["kind"] == "evaluation" and r["attributes"]["protocol"].endswith(("-huri-hits-100", "-huri-accuracy")):
        a = r["attributes"]
        a["comparison"]["split"] = None
        a.setdefault("missing_metadata", {})["comparison.split"] = {"reason": "unreported"}
        a["missing_metadata"] = dict(sorted(a["missing_metadata"].items()))
        n += 1
assert n == 154, n

# P3: the majority-vote ensemble is the study authors' own construction.
n = 0
for r in b.records:
    if r["kind"] == "evaluation" and r["links"][0]["target_id"].endswith("-ensemble"):
        r["attributes"]["origin"] = "author_reported"
        n += 1
assert n == 28, n

# P4: the prose and the tables name the third structure embedding differently.
P4 = ("Tables 5 and 6 print ProstT5 under Structure; Experimental design names ProtT5 as the third structure "
      "embedding. Table label followed; Supplementary Table S3 not retrieved.")
model_note = by_id[emb_id("ProstT5")]["attributes"]["missing_metadata"]["version"]
model_note["note"] = model_note["note"].rstrip(".") + ". " + P4
n = 0
for r in b.records:
    if r["kind"] == "configuration" and r["id"].endswith("-prostt5"):
        note = r["attributes"]["missing_metadata"]["version"]
        note["note"] = note["note"].rstrip(".") + ". " + P4
        n += 1
assert n == 7, n

# P5: the random-feature baselines look far below the leaderboard the authors say they reproduced.
concerns = by_id[SRC]["attributes"]["evidence_concerns"]
assert len(concerns) == 1, concerns
concerns[0]["message"] = concerns[0]["message"] + (
    " Random-feature baselines on OGBl-ppa (GCN 0.0588, GS 0.0104 Hits@100) look far below the public OGB "
    "leaderboard values the authors say they reproduced (Supplementary Table S2, not retrieved; reviewer did "
    "not verify the leaderboard values).")

R_METHODS = ["source-hash-verification", "deterministic-table-parse", "independent-cell-check",
             "rendered-source-visual-check"]
R_NOTE = ("Re-downloaded the PMC full-text XML from the recorded Europe PMC URL and matched its SHA-256. "
          "Parsed all 308 cells (2 tables x 2 datasets x 7 rows x 11 columns) with an independent parser, "
          "mapping every result through its evaluation, configuration and protocol: all match and no cell was "
          "missed. The misaligned HuRI N-GCN row is laid out the same way in the XML and the PMC HTML, so "
          "reading its eleven values in column order is the only consistent reading. Read 42 values covering "
          "both tables, both datasets, all seven rows and all eleven columns from the PMC HTML rendering: "
          "42 of 42 match. The three prose-versus-table discrepancies were confirmed, and none of the six "
          "percentage gains in the first Results paragraph can be derived from Table 5.")
for r in b.records:
    if r["kind"] == "result":
        old = r["attributes"]["review"]
        r["attributes"]["review"] = reviewed_review(R_METHODS, R_NOTE, REVIEWER_NOTE, SHA, URL,
                                                    old["method_note"], R_NOTE)
by_id[SRC]["attributes"]["review"] = source_review(
    REVIEWER_NOTE, "Full-text XML re-downloaded from the recorded Europe PMC URL and its SHA-256 matched.")
mark_reviewed(b)

counts = b.write()
print(json.dumps(counts))
