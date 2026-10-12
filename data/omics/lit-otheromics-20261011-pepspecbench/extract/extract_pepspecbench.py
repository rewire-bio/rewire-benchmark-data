"""Li, Zhong and Xia 2026, "PepSpecBench: A Unified Evaluation Benchmark for Peptide Tandem Mass Spectrometry
Prediction" (arXiv:2605.01945v1).

Tables 2, 4 and 14 from the arXiv HTML rendering of v1. The Table 4 'ID (SA)' column repeats the Table 2 SA
values and is not extracted again (see research.md).

Usage: python3 -I extract_pepspecbench.py <arxiv-html> <arxiv-pdf> <batch-folder>
"""
import sys, os, re, json, html as htmllib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, finalise, sha256, slug, num

html_path, pdf_path, folder = sys.argv[1], sys.argv[2], sys.argv[3]
SHA = sha256(html_path)
SHA_PDF = sha256(pdf_path)
URL = "https://arxiv.org/html/2605.01945v1"
assert SHA == "af7ed6d4470f0d4f60fccbe55103e72b19c258e53f9dd26c0c0e152a2ef18d81", SHA
assert SHA_PDF == "98da8c16b5ab6c5e8ec225f0807ff2b9143fbb0f4d34cef0f3aa79c9b738a2de", SHA_PDF

P = "lit-otheromics-20261011-pepspecbench"
b = Batch(folder, P, areas=["proteins-complexes"])
SRC = b.source(P + "-source-yang2026",  # review P1: first author Zhiwen Yang
                "PepSpecBench: A Unified Evaluation Benchmark for Peptide Tandem Mass Spectrometry Prediction", {
    "url": "https://arxiv.org/abs/2605.01945v1", "artifact_url": URL,
    "version": "arXiv:2605.01945v1 (submitted 2026-05-03), arXiv HTML rendering",
    "version_note": "The PDF of the same version (https://arxiv.org/pdf/2605.01945v1) was also retrieved, SHA-256 " + SHA_PDF + "; values were read from the HTML tables.",
    "retrieved_at": "2026-10-11T21:27:08Z", "artifact_sha256": SHA, "doi": "10.48550/arXiv.2605.01945",
    "publication_status": "preprint", "licence": "arXiv.org perpetual non-exclusive licence 1.0 (no reuse licence); not archived",
    "media_type": "text/html",
    "limitations": [
        "The arXiv HTML is generated from the LaTeX source and may be regenerated; the hash describes one retrieval.",
        "PROSPECT PredFull in-domain SA is printed as 0.204 in Table 2 and 0.203 in Table 4 (ID column); Table 14 gives 0.2035. Table 2 SAS 0.797 implies SA 0.203.",
        "Bold marks (best per source) are not recorded.",
    ]})
SIDS = [SRC]

def review(loc):
    return extraction_review(["deterministic-table-parse"],
        "Parsed the <td> cells of the pinned arXiv HTML table with extract/extract_pepspecbench.py; row label and column header taken from the same table. " + loc, SHA, URL)

H = open(html_path, encoding="utf8").read()
def clean(t):
    t = re.sub(r"<annotation[^>]*>.*?</annotation>", "", t, flags=re.S)
    t = re.sub(r'<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>', lambda m: " " + m.group(1) + " ", t, flags=re.S)
    return " ".join(htmllib.unescape(re.sub("<[^>]+>", "", t)).split())
def table(tid):
    m = re.search(r'<table id="' + re.escape(tid) + r'" class="ltx_tabular[^"]*">(.*?)</table>', H, re.S)
    return [[clean(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)] for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S)]

MODELS = {"Prosit": ("Prosit", "Prosit GRU encoder-decoder fragment intensity predictor (about 2.5M parameters)."),
          "Prosit Trans.": ("Prosit Transformer", "Prosit Transformer fragment intensity predictor (about 86M parameters)."),
          "Prosit Tran.": ("Prosit Transformer", None),
          "AlphaPeptDeep": ("AlphaPeptDeep", "AlphaPeptDeep modular Transformer fragment intensity predictor (about 1.8M parameters)."),
          "AlphaPep.": ("AlphaPeptDeep", None),
          "PredFull": ("PredFull", "PredFull residual CNN full-spectrum predictor with squeeze-excitation (about 8.2M parameters)."),
          "UniSpec": ("UniSpec", "UniSpec attention-based fragment dictionary model (about 12M parameters)."),
          "FastSpel": ("FastSpel", "FastSpel lightweight linear spectrum predictor (about 50K parameters), used as a lower-bound reference.")}
DESC = {v[0]: v[1] for v in MODELS.values() if v[1]}
fam = {}
def family(name):
    if name not in fam:
        rid = b.rid("model", name)
        b.entity("model", rid, name, DESC[name], SIDS,
                 {"reported_name": name, "entity_level": "family", "source_locator": "Section 3.2 'Baseline Models and Space Alignment'",
                  "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the retrained setup is on the configuration"}}},
                 method_types=["conventional_pipeline"] if name == "FastSpel" else ["supervised_machine_learning"])
        fam[name] = rid
    return fam[name]

SOURCES = {"MassIVE-KB": "massive-kb", "PROSPECT": "prospect"}
cfgs = {}
def config(label, train):
    name = MODELS[label][0]
    key = (name, train)
    if key not in cfgs:
        rid = b.rid("config", name, "trained", SOURCES[train])
        b.entity("configuration", rid, f"{name} retrained on {train} (PepSpecBench)",
                 f"{name} retrained by the PepSpecBench authors on the {train} backbone-disjoint training split (500k spectra).", SIDS,
                 {"reported_name": label, "foundation_model_eligible": False,
                  "parameters": f"Retrained on the {train}-Mini backbone-disjoint training split (500k/50k/50k train/validation/test); outputs projected to the shared canonical b/y fragment space; hyperparameters in Appendix Table 12",
                  "training_setting": f"Trained on {train}", "access_reuse": "Benchmark data at https://huggingface.co/datasets/Chris-young-2004/PepSpecBench; model code not stated",
                  "source_locator": "Section 3.2; Appendix E and Table 12",
                  "missing_metadata": {"version": {"reason": "unreported", "note": "No model or code version is printed"}}},
                 method_types=["conventional_pipeline"] if name == "FastSpel" else ["supervised_machine_learning"],
                 links=[{"relation": "configuration_of", "target_id": family(name)}])
        cfgs[key] = rid
    return cfgs[key]

BENCH = b.entity("benchmark", b.rid("benchmark", "pepspecbench"), "PepSpecBench",
    "Benchmark for peptide MS/MS fragment intensity prediction with harmonised PROSPECT and MassIVE-KB subsets, backbone-disjoint splits, a shared canonical fragment-ion evaluation space and a cross-species out-of-distribution suite.",
    SIDS, {"entity_level": "suite", "version": "v1 (arXiv:2605.01945v1)", "task": "Peptide tandem mass spectrum (fragment intensity) prediction",
           "scope_note": "Peptide length 6-40, precursor charge 1-6, PTMs UNIMOD 1, 4 and 35. In-domain: PROSPECT-Mini and MassIVE-KB-Mini, 500k/50k/50k spectra each. OOD: seven 20k-spectrum subsets over five species from ProteomeXchange (MaxQuant 1% FDR); zero-shot transfer.",
           "source_locator": "Sections 3.1-3.3; Appendix C", "limitations": ["Preprint; six models all retrained by the benchmark authors."]})

DATA = {"massive-kb": ("MassIVE-KB-Mini test split", "MassIVE-KB v1 human subset, 50k test spectra, backbone-disjoint from training; natural PTM distribution."),
        "prospect": ("PROSPECT-Mini test split", "PROSPECT (ProteomeTools) 50k test spectra, backbone-disjoint from training; 50% unmodified and 50% PTM."),
        "e-coli": ("E. coli OOD subsets (both sources aggregated)", "E. coli OOD spectra from PXD014877 and PXD027742, aggregated in Table 4."),
        "c-elegans": ("C. elegans OOD subset", "C. elegans OOD spectra from PXD014877 (20k)."),
        "a-thaliana": ("A. thaliana OOD subset", "A. thaliana OOD spectra from PXD014877 (20k)."),
        "yeast": ("Yeast OOD subset", "Yeast OOD spectra (20k)."),
        "hela": ("HeLa OOD subset", "Human HeLa cancer cell spectra from PXD027742 (20k), an intra-species domain shift.")}
data_ids = {k: b.entity("dataset", b.rid("data", k), f"PepSpecBench {v[0]}", v[1], SIDS,
                        {"version": "PepSpecBench v1", "split": "Test" if k in SOURCES.values() else "Out-of-distribution evaluation (zero-shot)",
                         "source_locator": "Table 1; Appendix C.1 and C.6"}) for k, v in DATA.items()}

MET = {"SAS": ("spectral-angle-similarity", "higher"), "SA": ("spectral-angle", "lower"), "PCC": ("pearson-correlation", "higher")}
protos = {}
def protocol(dk, col):
    key = (dk, col)
    if key not in protos:
        metric, direction = MET[col]
        ood = dk not in SOURCES.values()
        protos[key] = b.entity("protocol", b.rid("protocol", dk, col), f"PepSpecBench {DATA[dk][0]}, median {col}",
            ("Zero-shot out-of-distribution transfer: models trained on one in-domain source are scored without adaptation" if ood else "In-domain test on the backbone-disjoint split")
            + f"; median {col} over spectra in the shared canonical fragment space.", SIDS,
            {"protocol": f"Predict fragment intensities for each spectrum, project to the shared canonical b/y space, mask invalid positions, compute {col} per spectrum and take the median.",
             "version": "PepSpecBench v1", "metric": metric, "metric_direction": direction, "unit": "unitless",
             "metric_qualifier": "median over spectra, shared canonical fragment space",
             "source_locator": "Section 3.3 (metrics and evaluation protocol); " + ("Table 4" if ood else "Table 2"),
             "limitations": ["Preprint.", "Medians, not means."] + (["OOD results depend on the training source; compare only within one training source."] if ood else [])},
            links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data_ids[dk]}])
    return protos[key]

def evaluation(label, train, dk, col, loc):
    c = config(label, train)
    p = protocol(dk, col)
    e = b.rid("eval", MODELS[label][0], "trained", SOURCES[train], dk, col)
    if e not in b.ids:
        b.evaluation(e, f"{MODELS[label][0]} (trained on {train}) on {DATA[dk][0]}, {col}", SIDS, c, p, data_ids[dk], "independent_paper",
                     {"protocol_id": p, "dataset_version": "PepSpecBench v1", "split": "Backbone-disjoint test" if dk in SOURCES.values() else "OOD (zero-shot)",
                      "population": None, "inputs": "Peptide sequence with PTMs, precursor charge and NCE",
                      "adaptation": f"Retrained on {train}; no adaptation to the evaluation set", "metric_implementation": f"{col} in the shared canonical fragment space",
                      "aggregation": "Median over spectra", "budget": None}, loc)
    return e

def res(rid_parts, name, e, printed, col, loc, row_i, table, qualifier=None, unc=None, numeric=None):
    metric, direction = MET[col]
    b.result(b.rid("result", *rid_parts), name, SRC, SIDS, e, printed, metric, direction, "unitless", loc,
             review(f"{table} body row {row_i}."), qualifier=qualifier or "median over spectra, shared canonical fragment space",
             uncertainty=unc, numeric=numeric)

# Table 2
t2 = table("S4.T2.5")
assert t2[0] == ["", "MassIVE-KB", "PROSPECT"], t2[0]
assert t2[1] == ["Model", "SAS \\uparrow", "SA \\downarrow", "PCC \\uparrow", "SAS \\uparrow", "SA \\downarrow", "PCC \\uparrow"], t2[1]
assert len(t2) == 8
for i, row in enumerate(t2[2:], 1):
    assert len(row) == 7, row
    for (train, dk), (col, v) in zip([("MassIVE-KB", "massive-kb")] * 3 + [("PROSPECT", "prospect")] * 3, zip(["SAS", "SA", "PCC"] * 2, row[1:])):
        loc = f"Table 2, row '{row[0]}', column group '{train}', column '{col}'"
        e = evaluation(row[0], train, dk, col, loc)
        res([MODELS[row[0]][0], "trained", SOURCES[train], dk, col, "t2"], f"{MODELS[row[0]][0]} {train} in-domain {col}", e, v, col, loc, i, "Table 2")

# Table 4: two blocks; species cells are 'SA/SAS'
t4 = table("S4.T4.6")
block, n4 = None, 0
SPECIES = {"E. coli": "e-coli", "C. elegans": "c-elegans", "A. thaliana": "a-thaliana", "Yeast": "yeast", "HeLa": "hela"}
for i, row in enumerate(t4):
    if len(row) == 1:
        block = {"MassIVE-KB Trained": "MassIVE-KB", "PROSPECT Trained": "PROSPECT"}[row[0]]
        continue
    if row[0] == "Model":
        assert row == ["Model", "ID (SA)", "E. coli", "C. elegans", "A. thaliana", "Yeast", "HeLa"], row
        hdr, ri = row, 0
        continue
    ri += 1
    assert len(row) == 7, row
    for sp, cell in zip(hdr[2:], row[2:]):
        sa, sas = cell.split("/")
        dk = SPECIES[sp]
        for col, v in (("SA", sa), ("SAS", sas)):
            loc = f"Table 4, block '{block} Trained', row '{row[0]}', column '{sp}' ({'first' if col == 'SA' else 'second'} value of SA / SAS)"
            e = evaluation(row[0], block, dk, col, loc)
            res([MODELS[row[0]][0], "trained", SOURCES[block], dk, col, "t4"], f"{MODELS[row[0]][0]} {block}-trained {sp} {col}", e, v.strip(), col, loc, ri, "Table 4")
            n4 += 1
assert n4 == 2 * 6 * 5 * 2, n4

# Table 14: median SA with 95% bootstrap CI (1000 resamples over 50k test spectra)
t14 = table("A6.T14.5")
assert t14[0] == ["Source", "Model", "Med. SA", "95% CI (lo)", "95% CI (hi)"], t14[0]
src = None
for i, row in enumerate(t14[1:], 1):
    if len(row) == 5:
        src, row = row[0], row[1:]
    assert len(row) == 4, row
    train, dk = src, SOURCES[src]
    loc = f"Table 14, source '{src}', row '{row[0]}', column 'Med. SA'"
    e = evaluation(row[0], train, dk, "SA", loc)
    unc = {"type": "confidence_interval", "lower": row[2], "upper": row[3], "level": 0.95, "method": "bootstrap", "resamples": 1000,
           "printed": f"{row[2]} to {row[3]}", "source_column": "95% CI (lo), 95% CI (hi)",
           "note": "Table 14 caption: 95% bootstrap CI, 1000 resamples over 50k test spectra."}
    res([MODELS[row[0]][0], "trained", SOURCES[train], dk, "SA", "t14"], f"{MODELS[row[0]][0]} {train} in-domain median SA (Table 14)", e, row[1], "SA", loc, i, "Table 14",
        qualifier="median over spectra, shared canonical fragment space; four-decimal value with 95% bootstrap CI (Table 14)", unc=unc)

finalise(b.records, "reviewer-ro-2",
         "Re-downloaded the arXiv HTML and PDF and matched their SHA-256. An independent html.parser read of Tables 2, 4 and 14 compared all 168 cells (value, metric, direction, training source, configuration, OOD protocol and Table 14 CI bounds) with no mismatch; a seeded sample of 42 cells was read against the rendered PDF pages and all matched.")

counts = b.write()
print(json.dumps(counts))
