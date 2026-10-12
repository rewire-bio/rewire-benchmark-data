"""Liu, Bushuiev, Lightheart et al. 2026, "MassSpecGym in the Wild: Uncovering and Correcting Evaluation Pitfalls
in AI-Driven Molecule Discovery" (arXiv:2606.19624v1).

Tables 2, 3 and 9 from the arXiv HTML rendering of v1. Grey text (the paper's mark for leaking, inflated or
invalid results) is read from the cell style (--ltx-fg-color:#808080) and recorded on each configuration.

Usage: python3 -I extract_msgwild.py <arxiv-html> <arxiv-pdf> <batch-folder>
"""
import sys, os, re, json, html as htmllib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, finalise, sha256, slug, num

html_path, pdf_path, folder = sys.argv[1], sys.argv[2], sys.argv[3]
SHA = sha256(html_path)
SHA_PDF = sha256(pdf_path)
URL = "https://arxiv.org/html/2606.19624v1"
assert SHA == "47f329399853bdd2a513707b97271dfd8875271be383168effde1b0f13efb0d2", SHA
assert SHA_PDF == "81c23b4035c50661c77594fde0071798a13692cfb4f6b5ddb56e73587efa9fea", SHA_PDF

P = "lit-otheromics-20261011-msgwild"
b = Batch(folder, P, areas=["metabolomics"])
SRC = b.source(P + "-source-liu2026", "MassSpecGym in the Wild: Uncovering and Correcting Evaluation Pitfalls in AI-Driven Molecule Discovery", {
    "url": "https://arxiv.org/abs/2606.19624v1", "artifact_url": URL,
    "version": "arXiv:2606.19624v1 (submitted 2026-06-17), arXiv HTML rendering",
    "version_note": "The PDF of the same version (https://arxiv.org/pdf/2606.19624v1) was also retrieved, SHA-256 " + SHA_PDF + "; values were read from the HTML tables.",
    "retrieved_at": "2026-10-11T21:27:08Z", "artifact_sha256": SHA, "doi": "10.48550/arXiv.2606.19624",
    "publication_status": "preprint", "licence": "CC-BY-4.0", "media_type": "text/html",
    "limitations": [
        "The arXiv HTML is generated from the LaTeX source and may be regenerated; the hash describes one retrieval.",
        "Grey text marks results the authors consider leaking, inflated or invalid; the grey state was read from the HTML cell style.",
        "The top section of Table 3 and most rows of Table 9 repeat values reported in other papers; their bootstrap settings are those of the cited works.",
        # review M6
        "Authors include developers of MassSpecGym, DreaMS, MIST, MIST-CF, ICEBERG, DiffMS and FRIGID (Pluskal and Coley groups) and of JESTR, MVP and FLARE (Hassoun group); compiled rows for those methods repeat their developers' own results.",
    ]})
SIDS = [SRC]

def review(loc):
    return extraction_review(["deterministic-table-parse"],
        "Parsed the <td> cells of the pinned arXiv HTML table with extract/extract_msgwild.py; row label, column header and grey text style taken from the same table. " + loc, SHA, URL)

# --- tables from the HTML
H = open(html_path, encoding="utf8").read()
def clean(t):
    t = re.sub(r"<annotation[^>]*>.*?</annotation>", "", t, flags=re.S)
    t = re.sub(r'<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>', lambda m: " " + m.group(1) + " ", t, flags=re.S)
    t = re.sub(r'<cite class="ltx_cite[^"]*">.*?</cite>', "", t, flags=re.S)
    t = re.sub(r'<span class="ltx_note ltx_role_footnote">.*?</span></span></span>', "", t, flags=re.S)
    return " ".join(htmllib.unescape(re.sub("<[^>]+>", "", t)).split())
def table(prefix):
    m = re.search(r'<table id="' + re.escape(prefix) + r'" class="ltx_tabular[^"]*">(.*?)</table>', H, re.S)
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S):
        cells = []
        for attrs, inner in re.findall(r"<t[hd]([^>]*)>(.*?)</t[hd]>", tr, re.S):
            cells.append((clean(inner), "--ltx-fg-color:#808080" in inner, int((re.search(r'colspan="(\d+)"', attrs) or [0, 1])[1])))
        rows.append(cells)
    return rows

# --- identities
EXISTING = {"MIST": "uc20260930-model-mist", "JESTR": "uc20260930-model-jestr", "MVP": "uc20260930-model-mvp",
            "FLARE": "uc20260930-model-flare", "DreaMS": "discovery-model-dreams"}
NEW = {  # name -> (kind, description, method_types)
    "Random": ("method", "Random ranking or generation baseline.", ["conventional_pipeline"]),
    "Nearest Neighbor": ("method", "Nearest-neighbour spectral baseline, reimplemented by the MassSpecGym in the Wild authors.", ["conventional_pipeline"]),
    "DiffMS": ("model", "DiffMS: formula-conditioned discrete diffusion model that generates molecules from spectra via a MIST encoder.", ["supervised_machine_learning"]),
    "MolForge": ("model", "MolForge fingerprint-to-molecule decoder, used with a MIST spectrum encoder.", ["supervised_machine_learning"]),
    "ICEBERG": ("model", "ICEBERG forward spectrum simulation model, used for retrieval by scoring candidates against simulated spectra.", ["supervised_machine_learning"]),
    "FRIGID": ("model", "FRIGID diffusion-based molecular generation model from mass spectra.", ["supervised_machine_learning"]),
    "MSNovelist": ("model", "MSNovelist de novo structure generation from fingerprints.", ["supervised_machine_learning"]),
    "Spec2Mol": ("model", "Spec2Mol spectrum-to-molecule generation model.", ["supervised_machine_learning"]),
    "Neuraldecipher": ("model", "Neuraldecipher fingerprint-to-molecule decoder.", ["supervised_machine_learning"]),
    "MADGEN": ("model", "MADGEN mass-spectrum-guided de novo molecule generation.", ["supervised_machine_learning"]),
    "MS-BART": ("model", "MS-BART spectrum-to-molecule generation model.", ["foundation_model"]),
    "FOAM": ("model", "FOAM: DiffMS combined with PubChem candidates, as listed in Table 9.", ["supervised_machine_learning"]),
    "ChemBERTa": ("model", "ChemBERTa molecular language model.", ["foundation_model"]),
    "ChemFormer": ("model", "ChemFormer molecular language model.", ["foundation_model"]),
    "PubChem default ranking": ("method", "Spectrum-blind baseline that ranks candidates by the PubChem PUG-REST default retrieval order.", ["conventional_pipeline"]),
    "Chiral atom count ranking": ("method", "Spectrum-blind baseline that ranks candidates by the number of chiral atoms.", ["conventional_pipeline"]),
}
fam = {}
def family(name):
    if name in EXISTING:
        return EXISTING[name]
    if name not in fam:
        kind, desc, mt = NEW[name]
        rid = b.rid(kind, name)
        b.entity(kind, rid, name, desc, SIDS,
                 {"reported_name": name, "entity_level": "family" if kind == "model" else "method", "source_locator": "Tables 2, 3 and 9 row labels; Sections 4-6",
                  "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the setup is on the configuration"}}}, method_types=mt)
        fam[name] = rid
    return fam[name]

# row label -> (family, configuration name, origin, method types, note)
COMP = "paper_compilation"; AUTH = "author_reported"; IND = "independent_paper"
ROWS = {
    # Table 2 (mass-based retrieval; the authors' runs)
    ("T2", "Random"): ("Random", "Random ranking", AUTH, None),
    ("T2", "Random w/ ground-truth formula"): ("Random", "Random ranking among candidates filtered by the ground-truth formula", AUTH, "Grey: ground-truth formula leaks into the mass-based track."),
    ("T2", "MIST (MIST-CF top-1 formula)"): ("MIST", "MIST retrieval with MIST-CF top-1 predicted formula", AUTH, None),
    ("T2", "MIST (MIST-CF test-only top-1 formula)"): ("MIST", "MIST retrieval with top-1 formula from MIST-CF trained on test data only", AUTH, "Grey: formula annotator trained on test spectra."),
    ("T2", "MIST (MIST-CF train-test top-1 formula)"): ("MIST", "MIST retrieval with top-1 formula from MIST-CF trained on train and test data", AUTH, "Grey: formula annotator trained on test spectra."),
    ("T2", "MIST (ground-truth formula)"): ("MIST", "MIST retrieval with the ground-truth formula", AUTH, "Grey: ground-truth formula leaks into the mass-based track."),
    # Table 3 (formula-known retrieval bonus)
    # Review M1: the Random, DeepSets, Fingerprint FFN, DeepSets + Fourier and MIST vMassSpecGym rows of the top
    # section repeat MassSpecGym (arXiv:2410.23326v1) Table 3, already in the store; they are not extracted.
    ("T3", "JESTR"): ("JESTR", "JESTR", COMP, None),
    ("T3", "MVP"): ("MVP", "MVP", COMP, None),
    ("T3", "FLARE"): ("FLARE", "FLARE", COMP, None),
    ("T3", "Nearest Neighbor†"): ("Nearest Neighbor", "Nearest neighbour, reimplemented by the authors", IND, None),
    ("T3", "MIST vDiffMS"): ("MIST", "MIST, DiffMS checkpoint (vDiffMS)", COMP, "Grey: unreproducible MIST checkpoint (Section 6.1.2)."),
    ("T3", "DiffMS (generative retrieval)"): ("DiffMS", "DiffMS generative retrieval", COMP, "Grey: uses the unreproducible MIST vDiffMS encoder."),
    ("T3", "MIST+MolForge (generative retrieval)†"): ("MolForge", "MIST + MolForge generative retrieval, reimplemented by the authors", IND, "Grey: affected by the batched MIST padding-mask bug or the vDiffMS checkpoint (Section 6.1)."),
    ("T3", "ICEBERG (forward model retrieval)"): ("ICEBERG", "ICEBERG forward-model retrieval with imputed collision energies", AUTH, None),
    ("T3", "MIST vFRIGID"): ("MIST", "MIST, FRIGID checkpoint (vFRIGID)", COMP, None),
    ("T3", "FRIGID (generative retrieval)"): ("FRIGID", "FRIGID generative retrieval", COMP, None),
    ("T3", "(1) DreaMS + ChemBERTa Alignment (inflated)"): ("DreaMS", "DreaMS spectral encoder aligned to frozen ChemBERTa, original candidate canonicalization", AUTH, "Grey: exploits the SMILES canonicalization artifact."),
    ("T3", "(1) DreaMS + ChemBERTa Alignment (corrected)"): ("DreaMS", "DreaMS spectral encoder aligned to frozen ChemBERTa, corrected candidate canonicalization", AUTH, None),
    ("T3", "(2) ChemFormer Two-Stage Retrieval (inflated)"): ("ChemFormer", "ChemFormer two-stage retrieval, original candidate canonicalization", AUTH, "Grey: exploits the SMILES canonicalization artifact."),
    ("T3", "(2) ChemFormer Two-Stage Retrieval (corrected)"): ("ChemFormer", "ChemFormer two-stage retrieval, corrected candidate canonicalization", AUTH, None),
    ("T3", "(3) ChemBERTa SMILES classifier (inflated)"): ("ChemBERTa", "ChemBERTa SMILES classifier (spectrum-free), original candidate canonicalization", AUTH, "Grey: exploits the SMILES canonicalization artifact."),
    ("T3", "(3) ChemBERTa SMILES classifier (corrected)"): ("ChemBERTa", "ChemBERTa SMILES classifier (spectrum-free), corrected candidate canonicalization", AUTH, None),
    ("T3", "(4) PubChem default ranking"): ("PubChem default ranking", "PubChem default ranking (spectrum-blind)", AUTH, "Grey: spectrum-blind stress test."),
    ("T3", "(5) Ranking by num. of chiral atoms"): ("Chiral atom count ranking", "Ranking by number of chiral atoms (spectrum-blind)", AUTH, "Grey: spectrum-blind stress test."),
    # Table 9 (de novo with bonus)
    ("T9", "MIST + MSNovelist"): ("MSNovelist", "MIST + MSNovelist", COMP, None),
    ("T9", "Spec2Mol"): ("Spec2Mol", "Spec2Mol", COMP, None),
    ("T9", "MIST + Neuraldecipher"): ("Neuraldecipher", "MIST + Neuraldecipher", COMP, None),
    ("T9", "MADGEN"): ("MADGEN", "MADGEN", COMP, None),
    ("T9", "MS-BART"): ("MS-BART", "MS-BART", COMP, None),
    ("T9", "DiffMS"): ("DiffMS", "DiffMS", COMP, None),
    ("T9", "FOAM (DiffMS + PubChem)"): ("FOAM", "FOAM (DiffMS + PubChem)", COMP, None),
    ("T9", "MIST + MolForge† (corrected)"): ("MolForge", "MIST + MolForge, reimplemented by the authors, corrected", IND, None),
    ("T9", "MIST + MolForge† (inflated, batch size=24)"): ("MolForge", "MIST + MolForge, reimplemented by the authors, batched inference bug (batch size 24)", IND, "Grey: inflated by the batched inference bug."),
    ("T9", "FRIGID"): ("FRIGID", "FRIGID", COMP, None),
}
ORIGIN_NOTE = {COMP: "Value as reported in the cited work and repeated in this leaderboard table.",
               AUTH: "Run by the MassSpecGym in the Wild authors on a method or baseline from their own groups.",
               IND: "Reimplemented and run by the MassSpecGym in the Wild authors (dagger)."}

cfgs = {}
def config(table, label, grey):
    fam_name, cname, origin, note = ROWS[(table, label)]
    key = cname
    if key not in cfgs:
        rid = b.rid("config", cname)
        attrs = {"reported_name": label, "foundation_model_eligible": fam_name in ("DreaMS", "ChemBERTa", "ChemFormer", "MS-BART"),
                 "parameters": cname, "access_reuse": "Not stated in the source; see the cited work or https://github.com/pluskal-lab/MassSpecGym",
                 "source_locator": f"Table {table[1:]} row '{label}'",
                 "missing_metadata": {"version": {"reason": "unreported", "note": "Only the printed row label identifies the setup"}}}
        if note:
            attrs["limitations"] = [note + " Source marks this row in grey."]
        mt = NEW[fam_name][2] if fam_name in NEW else (["foundation_model"] if fam_name == "DreaMS" else ["supervised_machine_learning"])
        b.entity("configuration", rid, cname + " (MassSpecGym in the Wild)", f"{cname}, as listed in MassSpecGym in the Wild Table {table[1:]}.", SIDS, attrs,
                 method_types=mt,
                 links=[{"relation": "configuration_of", "target_id": family(fam_name)}])
        cfgs[key] = rid
    assert bool(note) == grey, (table, label, grey)
    return cfgs[key], origin

BENCH = "discovery-benchmark-massspecgym"
TASK = {"retrieval": "discovery-benchmark-massspecgym-molecule-retrieval", "denovo": "discovery-benchmark-massspecgym-de-novo-molecule-generation"}
DATA = {
    "T2": ("mass-retrieval", "MassSpecGym test fold, mass-based retrieval candidates", "MassSpecGym test fold (MCES-based split); candidates are PubChem structures matched on precursor mass (up to 256 per spectrum)."),
    "T3": ("formula-retrieval", "MassSpecGym test fold, formula-known retrieval candidates (bonus)", "MassSpecGym test fold; retrieval with bonus information: candidates restricted to the ground-truth molecular formula."),
    "T9": ("denovo-bonus", "MassSpecGym test fold, de novo generation with formula (bonus)", "MassSpecGym test fold; de novo generation with the ground-truth formula supplied."),
}
data_ids = {t: b.entity("dataset", b.rid("data", k), f"{n} (MassSpecGym in the Wild)", d, SIDS,
                        {"version": "MassSpecGym as used in each cited work; corrected rows use uniform RDKit canonicalization (MassSpecGym v1.5)",
                         "split": "Test fold", "source_locator": {"T2": "Table 2 caption; Section 4.3", "T3": "Table 3 caption and section headers", "T9": "Table 9 caption"}[t]})
            for t, (k, n, d) in DATA.items()}

# column header -> (metric, direction, unit, qualifier)
MET = {
    ("retrieval", "Hit rate@1"): ("top-1-accuracy", "higher", "percent", "retrieval"),
    ("retrieval", "Hit rate@5"): ("top-5-accuracy", "higher", "percent", "retrieval"),
    ("retrieval", "Hit rate@20"): ("top-20-accuracy", "higher", "percent", "retrieval"),
    ("retrieval", "MCES@1"): ("top-1-mces", "lower", "unitless", "retrieval"),
    ("denovo", "Top-1 Accuracy"): ("top-1-accuracy", "higher", "percent", "de novo, exact match"),
    ("denovo", "Top-1 MCES"): ("top-1-mces", "lower", "unitless", "de novo"),
    ("denovo", "Top-1 Tanimoto"): ("top-1-tanimoto", "higher", "unitless", "de novo"),
    ("denovo", "Top-10 Accuracy"): ("top-10-accuracy", "higher", "percent", "de novo, exact match"),
    ("denovo", "Top-10 MCES"): ("top-10-mces", "lower", "unitless", "de novo"),
    ("denovo", "Top-10 Tanimoto"): ("top-10-tanimoto", "higher", "unitless", "de novo"),
}
protos = {}
def protocol(t, kind, col):
    key = (t, col)
    if key not in protos:
        metric, direction, unit, qual = MET[(kind, col)]
        trackname = {"T2": "mass-based retrieval", "T3": "formula-known retrieval (bonus)", "T9": "de novo generation with formula (bonus)"}[t]
        protos[key] = b.entity("protocol", b.rid("protocol", DATA[t][0], col), f"MassSpecGym {trackname}, {col} (MassSpecGym in the Wild Table {t[1:]})",
            f"MassSpecGym {trackname} on the test fold, scored by {col}; mean over test spectra.", SIDS,
            {"protocol": f"MassSpecGym {trackname}; {col}", "version": "MassSpecGym as audited in arXiv:2606.19624v1",
             "metric": metric, "metric_direction": direction, "unit": unit, "metric_qualifier": qual,
             "source_locator": f"Table {t[1:]} column '{col}'; Appendix 'Confidence Intervals'",
             "limitations": ["Rows mix values copied from the literature with the authors' own runs; see each evaluation's origin.",
                             "Grey rows are results the authors consider leaking or inflated."]},
            links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "evaluates_task", "target_id": TASK[kind]}, {"relation": "uses_data", "target_id": data_ids[t]}])
    return protos[key]

GREY_T2_INPUTS = {
    ("T2", "Random w/ ground-truth formula"): "MS/MS spectrum, precursor mass and ground-truth formula (leaks into the mass-based track)",
    ("T2", "MIST (ground-truth formula)"): "MS/MS spectrum, precursor mass and ground-truth formula (leaks into the mass-based track)",
    ("T2", "MIST (MIST-CF test-only top-1 formula)"): "MS/MS spectrum and precursor mass; formula from a MIST-CF annotator trained on test spectra",
    ("T2", "MIST (MIST-CF train-test top-1 formula)"): "MS/MS spectrum and precursor mass; formula from a MIST-CF annotator trained on test spectra",
}
PCT = re.compile(r"^(-?\d+(?:\.\d+)?) \((-?\d+(?:\.\d+)?)\s*[-–]\s*(-?\d+(?:\.\d+)?)\)(%?)$")
def add(t, kind, label, grey, col, printed, row_i, section=None):
    c, origin = config(t, label, grey)
    p = protocol(t, kind, col)
    rlab = slug(ROWS[(t, label)][1])
    e = b.rid("eval", rlab, DATA[t][0], col)
    fam_name = ROWS[(t, label)][0]
    missing = {}
    # Review M3: only Table 3's "inflated" and "corrected" labels are about candidate canonicalization (Section 5.1).
    if t == "T3" and "corrected" in label:
        dataset_version = "Corrected candidate canonicalization (MassSpecGym v1.5)"
    elif t == "T3" and "inflated" in label:
        dataset_version = "Original MassSpecGym candidates"
    else:
        dataset_version = None
        if t == "T2" or (t == "T9" and fam_name == "MolForge"):
            missing["comparison.dataset_version"] = {"reason": "unreported", "note": "The table does not state the MassSpecGym candidate or canonicalization version"}
    # Review M4: Section 6.2 recommends the v1.5 metrics but does not say these tables used them.
    if origin == COMP:
        metric_implementation = "MassSpecGym metric as implemented in each work"
    else:
        metric_implementation = None
        missing["comparison.metric_implementation"] = {"reason": "unreported", "note": "Section 6.2 recommends the MassSpecGym v1.5 reference metrics; the tables do not state which implementation produced these values"}
    inputs = {"T2": "MS/MS spectrum and precursor mass", "T3": "MS/MS spectrum, precursor mass and ground-truth formula (bonus)", "T9": "MS/MS spectrum and ground-truth formula (bonus)"}[t]
    inputs = GREY_T2_INPUTS.get((t, label), inputs)  # review M5
    limitations = [ORIGIN_NOTE[origin]] + ([ROWS[(t, label)][3] + " Grey in the source."] if grey and ROWS[(t, label)][3] else [])
    if fam_name == "MolForge":  # review M7
        limitations.append("The MIST encoder in this pipeline was developed in the corresponding author's (Coley) group; the MolForge decoder was not.")
    b.evaluation(e, f"{ROWS[(t, label)][1]} on MassSpecGym {DATA[t][0]} ({col})", SIDS, c, p, data_ids[t], origin,
                 {"protocol_id": p, "dataset_version": dataset_version,
                  "split": "MassSpecGym test fold", "population": None, "inputs": inputs,
                  "adaptation": None, "metric_implementation": metric_implementation,
                  "aggregation": "Mean over test spectra", "budget": None},
                 f"Table {t[1:]} row '{label}', column '{col}'", missing=missing,
                 extra={"limitations": limitations})
    metric, direction, unit, qual = MET[(kind, col)]
    m = PCT.match(printed)
    unc, ud = None, None
    if m:
        val, lo, hi, pct = m.groups()
        unc = {"type": "confidence_interval", "lower": lo, "upper": hi, "printed": printed, "method": "bootstrap",
               "note": "Range printed in parentheses after the mean."}
        if origin == COMP and t == "T3":  # review M2: the Table 3 caption covers every bracketed value
            unc["level"] = 0.999
            unc["resamples"] = 20000
            unc["note"] = "Range printed in parentheses after the mean. Table 3 caption: 99.9% BCa bootstrap intervals over 20,000 resamples, stated for all bracketed values. Value repeated from the cited work; that work's own interval settings were not checked."
        elif origin == COMP:
            unc["note"] += " Value repeated from the cited work; its interval settings are not restated in this table."
        else:
            unc["level"] = 0.999
            unc["resamples"] = 20000
            unc["note"] += " Appendix 'Confidence Intervals': 99.9% bootstrap interval over 20,000 resamples of the test set."
        if unit == "percent" and not pct:
            ud = "Printed without a percent sign in Table 2; the values are percentages (hit rates)."
    else:
        val = printed.rstrip("%")
        assert num(val) is not None, printed
    loc = f"Table {t[1:]}" + (f", section '{section}'" if section else "") + f", row '{label}', column '{col}'"
    b.result(b.rid("result", rlab, DATA[t][0], col), f"{ROWS[(t, label)][1]} {col} ({DATA[t][0]})", SRC, SIDS, e, printed, metric, direction, unit,
             loc, review(f"Table {t[1:]} body row {row_i}." + (" Grey text in the source." if grey else "")), qualifier=qual, unit_detail=ud,
             uncertainty=unc, numeric=num(val))

# Table 2
t2 = table("S4.T2.6.1")
assert [c[0] for c in t2[0]] == ["Method", "Hit rate @1 \\uparrow", "Hit rate @5 \\uparrow", "Hit rate @ 20 \\uparrow", "MCES @ 1 \\downarrow"], t2[0]
cols2 = ["Hit rate@1", "Hit rate@5", "Hit rate@20", "MCES@1"]
assert len(t2) == 7
for i, row in enumerate(t2[1:], 1):
    label, grey = row[0][0], row[0][1]
    assert len(row) == 5 and all(c[1] == grey for c in row), row
    for col, cell in zip(cols2, row[1:]):
        add("T2", "retrieval", label, grey, col, cell[0], i)

# Table 3
t3 = table("S5.T3.8.1")
assert [c[0] for c in t3[0]] == ["Method", "Hit rate@1 \\uparrow", "Hit rate@5 \\uparrow", "Hit rate@20 \\uparrow", "MCES@1 \\downarrow"], t3[0]
M1_SECTION = "Reported Performance in Retrieval Task w/ Bonus (i.e., Formula Known)"
M1_ROWS = ["Random", "DeepSets", "Fingerprint FFN", "DeepSets + Fourier", "MIST vMassSpecGym"]
section, n3, skipped = None, 0, []
for i, row in enumerate(t3[1:], 1):
    if len(row) == 1:
        section = row[0][0]
        continue
    label = re.sub(r"\s*[\d\s]*ICEBERG is evaluated.*$", "", row[0][0]).strip()
    grey = row[0][1]
    if section == M1_SECTION and label in M1_ROWS:  # review M1
        skipped.append(label)
        continue
    assert len(row) == 5 and all(c[1] == grey for c in row), row
    for col, cell in zip(cols2, row[1:]):
        add("T3", "retrieval", label, grey, col, cell[0], i, section)
        n3 += 1
assert n3 == 18 * 4 and skipped == M1_ROWS, (n3, skipped)

# Table 9
t9 = None
for m_ in re.finditer(r'<table id="(A\d+\.T9[^"]*)" class="ltx_tabular', H):
    t9 = table(m_.group(1))
assert t9 is not None
assert [c[0] for c in t9[1]] == ["Model", "Accuracy \\uparrow", "MCES \\downarrow", "Tanimoto \\uparrow", "Accuracy \\uparrow", "MCES \\downarrow", "Tanimoto \\uparrow"], t9[1]
cols9 = ["Top-1 Accuracy", "Top-1 MCES", "Top-1 Tanimoto", "Top-10 Accuracy", "Top-10 MCES", "Top-10 Tanimoto"]
assert len(t9) == 12, len(t9)
for i, row in enumerate(t9[2:], 1):
    label, grey = row[0][0], row[0][1]
    assert len(row) == 7, row
    for col, cell in zip(cols9, row[1:]):
        add("T9", "denovo", label, grey, col, cell[0], i)

# --- relevance judgements for the mass-based retrieval protocols (Table 2), use case mass-spectrum-molecule-shortlisting
UC = "use-case-mass-spectrum-molecule-shortlisting"
GREY_T2 = [lab for (t, lab), v in ROWS.items() if t == "T2" and v[3]]
links = []
for order, col in enumerate(["Hit rate@1", "Hit rate@20"], 1):
    pid = protos[("T2", col)]
    evals = sorted(r["id"] for r in b.records if r["kind"] == "evaluation" and any(l["relation"] == "assessment" and l["target_id"] == pid for l in r["links"]))
    excluded = [{"id": b.rid("eval", slug(ROWS[("T2", lab)][1]), DATA["T2"][0], col),
                 "reason": "Grey in the source: " + ROWS[("T2", lab)][3] + " Not a valid formula-free result."} for lab in GREY_T2]
    assert all(e["id"] in evals for e in excluded) and len(evals) - len(excluded) == 2, evals
    cid = "use-case-mapping-" + P + "-mass-retrieval-" + slug(col)
    b.claim(cid, f'Relevance of MassSpecGym mass-based retrieval, {col} (MassSpecGym in the Wild Table 2) to "Shortlist molecular identities from tandem mass spectra"',
            f"MassSpecGym mass-based retrieval {col} as evidence for shortlisting candidate structures without a known formula.", UC, SIDS,
            {"field": "links:assessed_by:" + pid, "value": pid, "relevance": "proxy",
             "endpoint": f"{col} (mean over MassSpecGym test spectra, 99.9% bootstrap CI) for ranking the true structure among mass-matched PubChem candidates",
             # review M8: rationale, constraints and limitations as written by reviewer-ro-2
             "rationale": "Proxy, not direct. The mass-based track withholds the formula, which matches the use case's formula-free input and shortlist endpoint. MIST here takes the top-1 formula predicted from the spectrum by a MIST-CF retrained on the MassSpecGym training split only, and that formula is not used to filter candidates (Section 4.3), so the pipeline needs only the spectrum and precursor mass. This differs from the formula-conditioned MIST the use case excludes, which receives the true formula. Only two valid configurations are measured (random ranking and this MIST pipeline), and the candidate pool and split differ from the MSAlign settings the use case was built on.",
             "constraints": ["Use only the two non-grey evaluations; the grey rows leak ground-truth or test-trained formula information and are excluded.",
                             "Treat MIST with the MIST-CF top-1 formula as a two-model pipeline (formula annotator plus formula-aware retriever). Do not transfer its score to MIST given a known formula, or to MIST-CF checkpoints trained on test spectra.",
                             "Do not combine with the formula-known (bonus) retrieval results of Table 3 or with MSAlign's split-specific pools.",
                             "Compare within this table only; corrected MassSpecGym v1.5 candidate canonicalization may change other published values."],
             "limitations": ["Authors include the MIST, MIST-CF and MassSpecGym developers (author_reported).",
                             "Preprint (arXiv:2606.19624v1).",
                             "The true structure must be in the candidate set; not open-world identification.",
                             "Retrieval inherits the errors of the formula annotator; its formula accuracy is in Table 7, not extracted.",
                             "Table 8 reports a further non-grey variant (MIST-CF top-5 formulas, element-wise max), not extracted.",
                             "Values are percentages printed without a percent sign in Table 2."],
             "citation_locators": [{"source_id": SRC, "locator": f"Table 2, column '{col}'; Section 4.3; Appendix 'Confidence Intervals'"}],
             "source_locator": f"{SRC}: Table 2, column '{col}'",
             "headline_metric": {"Hit rate@1": "top-1-accuracy", "Hit rate@20": "top-20-accuracy"}[col],
             "reason": "Add a relevance judgement for the MassSpecGym in the Wild mass-based retrieval protocol from the 2026-10-11 other-omics literature pass.",
             "comparison_group": "massspecgym-in-the-wild-mass-retrieval", "comparison_title": "MassSpecGym in the Wild, mass-based retrieval (Table 2)",
             "stratum_label": col, "stratum_order": order, "excluded_evaluations": excluded,
             # review M8: the two non-grey evaluations the reviewer checked
             "reviewed_evaluations": [b.rid("eval", "random-ranking", DATA["T2"][0], col),
                                      b.rid("eval", "mist-retrieval-with-mist-cf-top-1-predicted-formula", DATA["T2"][0], col)]}, source_id=SRC)
    assert all(e in evals for e in b.records[-1]["attributes"]["reviewed_evaluations"])
    links.append({"use_case": UC, "relation": "assessed_by", "target_id": pid, "judgement_claim": cid})
LINKS = {"note": "Proposed assessed_by links to add to the use_case records after the judgement claims are reviewed. Not applied by the extractor.", "links": links}

n_m4 = sum(1 for r in b.records if r["kind"] == "evaluation" and r["attributes"].get("missing_metadata", {}).get("comparison.metric_implementation", {}).get("note"))
n_m3 = sum(1 for r in b.records if r["kind"] == "evaluation" and r["attributes"].get("missing_metadata", {}).get("comparison.dataset_version", {}).get("note"))
n_m7 = sum(1 for r in b.records if r["kind"] == "evaluation" and any("MolForge decoder" in x for x in r["attributes"]["limitations"]))
n_m2 = sum(1 for r in b.records if r["kind"] == "result" and r["attributes"]["source_locator"].startswith("Table 3") and r["attributes"].get("uncertainty", {}).get("level") is None)
# M7 names the 12 Table 9 MolForge evaluations of M3 plus 4 Table 3 ones: 16 in all.
assert (n_m4, n_m3, n_m7, n_m2) == (80, 36, 16, 0), (n_m4, n_m3, n_m7, n_m2)
finalise(b.records, "reviewer-ro-2",
         "Re-downloaded the arXiv HTML and PDF and matched their SHA-256. An independent html.parser read of Tables 2, 3 and 9 compared all 176 cells (printed and numeric values, CI bounds, grey state, metric, unit and direction) with no mismatch; a seeded sample of 40 cells was read against the rendered PDF pages and all matched.",
         judgement_note="Reviewer checked the endpoint against the use case's inputs, output and exclusions, the relevance rating and the limitations, the grey-row exclusions in the HTML parse and the rendered PDF, and every value on the protocol in the batch review. The rationale, constraints and limitations are the reviewer's text (review.md, M8).",
         # The approved assessed_by links need `records -- change`, which waits for owner approval.
         defer_judgements=True)

counts = b.write({"use-case-links.json": json.dumps(LINKS, indent=1) + "\n"})
print(json.dumps(counts))
