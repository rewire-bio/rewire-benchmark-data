"""Ludaic and Elofsson 2026, "Limits of deep-learning-based RNA prediction methods" (NAR, gkag813).

Main Tables 2-5 from the PMC XML; Supplementary Tables S6, S7 and S15 from the supplementary PDF text layer.

Usage: python3 -I extract_rna3d.py <fulltext.xml> <supplement.pdf> <batch-folder>
Needs pdftotext (poppler) on PATH.
"""
import sys, os, re, json, subprocess
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, finalise, sha256, slug, num

xml_path, pdf_path, folder = sys.argv[1], sys.argv[2], sys.argv[3]
SHA = sha256(xml_path)
SHA_S = sha256(pdf_path)
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13501138/fullTextXML"
URL_S = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13501138/supplementaryFiles"
assert SHA == "02043b4a3edbb62101f6abbca56c896a63fa5c7dc0c3956c58164daff015ad1f", SHA
assert SHA_S == "0e26a301a5b5c39a0e2dfaa092760d6099345dcb9e0545e23b730374f39d463c", SHA_S

P = "lit-rna-20261011-rna3d"
b = Batch(folder, P, areas=["rna-transcriptomes", "protein-structure"])
SRC = b.source(P + "-source-ludaic2026", "Limits of deep-learning-based RNA prediction methods", {
    "url": "https://doi.org/10.1093/nar/gkag813", "artifact_url": URL,
    "version": "Nucleic Acids Research 2026, gkag813 (issue date 2026-08-01); PMC13501138 full-text XML",
    "retrieved_at": "2026-10-11T21:27:03Z", "artifact_sha256": SHA, "doi": "10.1093/nar/gkag813",
    "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml",
    "code_url": "https://github.com/iammarcol/RNA-Benchmark",
    "limitations": [
        "Tables 2 and 3 print identical GDT-TS, INF and lDDT means for DRfold and DeepFoldRNA (0.559, 0.736, 0.481 easy; 0.436, 0.617, 0.361 hard) while their TM-scores differ. The per-target columns for the two methods in Supplementary Tables S3-S5 are also identical, so the duplication is upstream of the means. Not resolved from the source.",
        "Table 3 prints INF 0.668 for RF2NA on the hard set; the mean of the RF2NA column of Supplementary Table S3 (hard rows) is 0.608 by the extractor's own check. Not resolved from the source.",
        "The tables print bold, underline and italic marks for statistical ties (Wilcoxon signed-rank test); the XML carries no formatting, so those marks are not recorded.",
    ]})
SRC_S = b.source(P + "-source-ludaic2026-supplement", "Limits of deep-learning-based RNA prediction methods: Supplementary Data", {
    "url": "https://doi.org/10.1093/nar/gkag813", "artifact_url": URL_S,
    "version": "gkag813_supplemental_file.pdf from the Europe PMC supplementary files archive for PMC13501138",
    "retrieved_at": "2026-10-11T21:28:04Z", "artifact_sha256": SHA_S, "doi": "10.1093/nar/gkag813",
    "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/pdf",
    "limitations": ["Read through the pdftotext -layout text layer; values were transcribed from the text layer, not from page renders.",
                    # review D4
                    "Supplementary Table S7 prints 37.78% for AF3 GDT-TS on the hard set; Supplementary Table S4 gives 19 of 49 targets (38.78%). The DRfold and DeepFoldRNA per-target INF, GDT-TS and lDDT columns of Supplementary Tables S3-S5 are identical."]})
SIDS = [SRC]
SIDS_S = [SRC_S, SRC]

def review_xml(loc):
    return extraction_review(["deterministic-table-parse"],
        "Parsed the <td> cells of the pinned PMC XML table with extract/extract_rna3d.py; row label and column header taken from the same table. " + loc, SHA, URL)

def review_pdf(loc):
    return extraction_review(["pdf-text-parse"],
        "Parsed the pdftotext -layout text of the pinned supplementary PDF with extract/extract_rna3d.py; method order taken from the printed header row. " + loc, SHA_S, URL_S)

root = ET.fromstring(open(xml_path, "rb").read())
tables = {}
for tw in root.iter("table-wrap"):
    lab = " ".join("".join(tw.find("label").itertext()).split()).rstrip(".")
    rows = [[" ".join("".join(c.itertext()).split()) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
    tables[lab] = rows

# Supplementary Table S1 versions (printed in the supplement).
VERSIONS = {"AF3": "3.0.1", "Boltz-1": "0.4.1", "Chai-1": "0.6.1", "DeepFoldRNA": "1.0", "DRfold": "commit pre-release-4-g9586990",
            "HF3": "HelixFold3/73cd80b-hpc1", "NuFold": "commit 169a618", "RhoFold+": "0.0.1", "RF2NA": "commit f761af2", "trRosettaRNA": "1.0"}
FULL = {"AF3": "AlphaFold3", "Boltz-1": "Boltz-1", "Chai-1": "Chai-1", "DeepFoldRNA": "DeepFoldRNA", "DRfold": "DRfold", "HF3": "HelixFold3",
        "NuFold": "NuFold", "RhoFold+": "RhoFold+", "RF2NA": "RosettaFoldNA", "trRosettaRNA": "trRosettaRNA"}
EXISTING = {"AF3": "discovery-model-alphafold-3", "Boltz-1": "discovery-model-boltz", "Chai-1": "catalog-model-chai-1",
            "HF3": "ucc-research-model-helixfold3", "RhoFold+": "catalog-model-rhofold"}
NEW = {"NuFold": "NuFold RNA 3D structure prediction method built on the AlphaFold architecture with RNA-specific inputs (Table 1).",
       "RF2NA": "RoseTTAFoldNA (RF2NA): three-track network that predicts protein and nucleic acid structures and complexes (Table 1).",
       "trRosettaRNA": "trRosettaRNA: MSA and pair representations fed into the RNAformer transformer, followed by 3D folding (Table 1).",
       "DRfold": "DRfold: ab initio RNA structure prediction that combines end-to-end learning with deep geometrical potentials (Table 1).",
       "DeepFoldRNA": "DeepFoldRNA: RNA structure prediction from deep self-attention networks with gradient-based folding (Table 1)."}
GENERAL = ("AF3", "Boltz-1", "Chai-1", "HF3")

def canon(label):
    return {"Chai": "Chai-1"}.get(label, label)

fam = {}
def family(m):
    if m in EXISTING:
        return EXISTING[m]
    if m not in fam:
        rid = b.rid("model", FULL[m])
        b.entity("model", rid, FULL[m], NEW[m], SIDS,
                 {"reported_name": FULL[m], "entity_level": "family", "source_locator": "Table 1 row '" + {"RF2NA": "RosettaFoldNA(RF2NA)"}.get(m, m) + "'",
                  "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the version run is on the configuration"}}},
                 method_types=["specialist"])
        fam[m] = rid
    return fam[m]

cfg = {}
def config(m):
    if m not in cfg:
        rid = b.rid("config", m, "ludaic2026")
        b.entity("configuration", rid, f"{FULL[m]} {VERSIONS[m]} (Ludaic and Elofsson 2026 RNA benchmark run)",
                 f"{FULL[m]} run by Ludaic and Elofsson with default settings on their 2026 RNA structure benchmark.", SIDS_S,
                 {"reported_name": m, "version": VERSIONS[m],
                  "parameters": "Default settings; one NVIDIA DGX-A100 GPU; shared MSAs (rMSA against RNAcentral and NCBI nt for RNA, MMseqs2 on the ColabFold databases for protein) supplied where the method accepts custom MSAs; five models generated with the same seed and the top-ranked model analysed (native ranking score, else mean pLDDT, else the first or only model)",
                  "access_reuse": "Not stated in the source beyond the software version; see the method's own release",
                  "foundation_model_eligible": m in GENERAL,
                  "source_locator": "Supplementary Table S1 row '" + {"AF3": "AlphaFold 3", "HF3": "HelixFold3", "RF2NA": "RosettaFoldNA"}.get(m, m) + "'; Methods 'Model generation'"},
                 method_types=["foundation_model"] if m in GENERAL else ["specialist"],
                 links=[{"relation": "configuration_of", "target_id": family(m)}])
        cfg[m] = rid
    return cfg[m]

BENCH = b.entity("benchmark", b.rid("benchmark", "ludaic2026"), "Ludaic and Elofsson 2026 RNA structure benchmark",
    "Independent benchmark of ten deep learning methods on non-redundant monomeric RNAs and RNA-RNA and RNA-protein complexes released after the methods' training cut-offs, split into easy and hard sets by structural similarity to the PDB training data.",
    SIDS, {"entity_level": "suite", "version": "Published 2026 (PDB entries downloaded January 2026)",
           "task": "RNA 3D structure prediction for monomers and complexes",
           "scope_note": "79 monomeric RNAs after excluding three long targets that DRfold and DeepFoldRNA did not produce (Methods); 158 complex structures. Easy/hard split for monomers: maximum RNA-align TM-score to the PDB training data at a 0.5 cut-off; for complexes: an RNA or protein chain with TM-score >= 0.7 to a pre-cut-off complex is easy.",
           "source_locator": "Methods 'Benchmark dataset' and 'Model generation'; Results sections on monomers and complexes",
           "limitations": ["The authors developed none of the benchmarked methods.", "Means only; per-target scores are in Supplementary Tables S2-S5 and S9-S14."]})

DATA = {
    "monomer-easy": ("Monomeric RNA easy set", "Monomeric RNAs with maximum RNA-align TM-score to the PDB training data at or above the 0.5 cut-off (easy). 30 targets in Supplementary Tables S2-S4; 29 in Table S5 (lDDT).", "Easy (structurally similar to training data)"),
    "monomer-hard": ("Monomeric RNA hard set", "Monomeric RNAs below the 0.5 TM-score similarity cut-off (hard). 49 targets in Supplementary Tables S2-S4; 47 in Table S5 (lDDT).", "Hard (structurally dissimilar to training data)"),
    "complex-easy": ("RNA complex easy set", "RNA-RNA and RNA-protein complexes with an RNA or protein chain at TM-score >= 0.7 to a complex in the PDB before the cut-off date (easy).", "Easy"),
    "complex-hard": ("RNA complex hard set", "RNA-RNA and RNA-protein complexes with no chain at TM-score >= 0.7 to a pre-cut-off PDB complex (hard).", "Hard"),
    "complex-all": ("RNA complex set, easy and hard combined", "All 158 RNA complex structures, easy and hard sets processed together for the per-interface DockQ analysis.", "Easy and hard combined"),
}
data_ids = {}
for k, (name, desc, split) in DATA.items():
    data_ids[k] = b.entity("dataset", b.rid("data", k), f"Ludaic and Elofsson 2026 {name}", desc, SIDS,
                           {"version": "PDB entries released after the training cut-offs, downloaded January 2026, plus CASP16 RNA targets",
                            "split": split, "source_locator": "Methods 'Benchmark dataset'; Results 'Performance of structure prediction methods on monomeric RNAs' and '... RNA complexes'"})

METRICS = {  # column -> (metric concept, direction, unit, qualifier, unit_detail)
    "TM-score": ("tm-score", "higher", "unitless", None, None),
    "GDT-TS": ("gdt-ts", "higher", "unitless", None, None),
    "INF": ("interaction-network-fidelity", "higher", "unitless", None, None),
    "lDDT": ("lddt", "higher", "unitless", None, None),
    "DockQ": ("dockq", "higher", "unitless", None, None),
    "F1": ("f1-score", "higher", "unitless", "interface residues (atom within 5 A of the partner chain)", None),
    "iRMSD": ("capri-interface-rmsd", "lower", "angstrom", None, "Unit not printed in Tables 4-5; DockQ reports iRMSD in angstroms"),
    "LRMSD": ("capri-ligand-rmsd", "lower", "angstrom", None, "Unit not printed in Tables 4-5; DockQ reports LRMSD in angstroms"),
    "fnat": ("fnat", "higher", "unitless", None, None),
}
IMPL = {"TM-score": "RNA-align TM-score for monomers; US-align TM-score (-mm 1 -ter 0) for complexes",
        "GDT-TS": "RNAdvisor", "INF": "RNAdvisor", "lDDT": "RNAdvisor",
        "DockQ": "DockQ (overall score averaged over interfaces)", "F1": "Interface residue F1 computed by the authors (Methods 'Model evaluation')",
        "iRMSD": "DockQ", "LRMSD": "DockQ", "fnat": "DockQ"}

protos = {}
def protocol(subset, col, kind="mean"):
    key = (subset, col, kind)
    if key in protos:
        return protos[key]
    metric, direction, unit, qual, ud = METRICS.get(col, (None, None, None, None, None))
    if kind == "mean":
        name = f"Ludaic and Elofsson 2026 {DATA[subset][0]}, mean {col}"
        proc = f"Top-ranked model per target scored against the experimental structure (trimmed to resolved residues); mean {col} over the {DATA[subset][0].lower()}"
    elif kind == "success":
        name = f"Ludaic and Elofsson 2026 {DATA[subset][0]}, {col} success rate"
        proc = f"Percentage of targets whose model exceeds the CASP16 success threshold for {col} (TM-score > 0.45, GDT-TS > 0.45, INF > 0.75, lDDT > 0.75)"
        metric, direction, unit = "success-rate", "higher", "percent"
    else:  # interface DockQ by interface type
        name = f"Ludaic and Elofsson 2026 {col} interfaces, mean per-interface DockQ"
        proc = f"Mean DockQ over individual {col} interfaces (IF-DockQ), easy and hard complexes combined"
        metric, direction, unit = "dockq", "higher", "unitless"
    attrs = {"protocol": proc, "version": "Ludaic and Elofsson 2026", "metric": metric, "metric_direction": direction, "unit": unit,
             "source_locator": {"mean": "Tables 2-5; Methods 'Model evaluation'", "success": "Supplementary Tables S6-S7; Results first section", "if": "Supplementary Table S15; Results 'Performance of structure prediction for RNA-RNA and RNA-protein complexes'"}[kind],
             "limitations": ["Independent benchmark; the authors developed none of the methods.",
                             "Easy and hard are defined by structural similarity to the PDB training data and differ for monomers and complexes."]}
    if kind == "mean":
        attrs["metric_implementation"] = IMPL[col]
    if qual and kind == "mean":
        attrs["metric_qualifier"] = qual
    pid = b.entity("protocol", b.rid("protocol", subset, kind, col), name, proc + ".", SIDS if kind == "mean" else SIDS_S, attrs,
                   links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data_ids[subset]}])
    protos[key] = pid
    return pid

def cell(table, m, subset, col, printed, kind, locator, review, sids, row_i):
    m = canon(m)
    c = config(m)
    p = protocol(subset, col, kind)
    e = b.rid("eval", m, subset, kind, col)
    if kind == "mean":
        agg, impl = "Mean over targets", IMPL[col]
    elif kind == "success":
        agg, impl = "Percentage of targets above the CASP16 threshold", "CASP16 thresholds: TM-score > 0.45, GDT-TS > 0.45, INF > 0.75, lDDT > 0.75"
    else:
        agg, impl = "Mean over interfaces of this type", "DockQ per interface (IF-DockQ)"
    b.evaluation(e, f"{FULL[m]} on {DATA[subset][0]} ({col}{', success rate' if kind == 'success' else ''})", sids, c, p, data_ids[subset], "independent_paper",
                 {"protocol_id": p, "dataset_version": "PDB after training cut-offs, downloaded January 2026", "split": DATA[subset][2],
                  "population": None, "inputs": "Sequence plus shared externally supplied MSAs where the method accepts them",
                  "adaptation": "Default settings, no retraining; top-ranked of five models", "metric_implementation": impl,
                  "aggregation": agg, "budget": None}, locator)
    if kind == "mean":
        metric, direction, unit, qual, ud = METRICS[col]
    elif kind == "success":
        metric, direction, unit, qual, ud = "success-rate", "higher", "percent", f"{col} above the CASP16 threshold", None
    else:
        metric, direction, unit, qual, ud = "dockq", "higher", "unitless", f"mean per-interface DockQ, {col} interfaces", None
    rid = b.rid("result", m, subset, kind, col)
    n = num(printed)
    assert n is not None, (table, m, col, printed)
    b.result(rid, f"{FULL[m]} {DATA[subset][0]} {col}" + (" success rate" if kind == "success" else ""), sids[0], sids, e, printed, metric, direction, unit,
             locator, review(f"{table} body row {row_i}."), qualifier=qual, unit_detail=ud)

# Main tables 2-5
for lab, subset, cols in [("Table 2", "monomer-easy", ["TM-score", "GDT-TS", "INF", "lDDT"]),
                          ("Table 3", "monomer-hard", ["TM-score", "GDT-TS", "INF", "lDDT"]),
                          ("Table 4", "complex-easy", ["DockQ", "F1", "iRMSD", "LRMSD", "fnat", "TM-score"]),
                          ("Table 5", "complex-hard", ["DockQ", "F1", "iRMSD", "LRMSD", "fnat", "TM-score"])]:
    t = tables[lab]
    assert t[0][1:] == cols, (lab, t[0])
    body = t[1:]
    assert len(body) == (10 if subset.startswith("monomer") else 4), (lab, len(body))
    for i, row in enumerate(body, 1):
        assert len(row) == len(cols) + 1, row
        for col, v in zip(cols, row[1:]):
            cell(lab, row[0], subset, col, v, "mean", f"{lab}, row '{row[0]}', column '{col}'", review_xml, SIDS, i)

# Supplementary tables from the PDF text layer
txt = subprocess.run(["pdftotext", "-layout", pdf_path, "-"], capture_output=True, text=True, check=True).stdout
lines = txt.split("\n")
def block(start_pat, end_pat):
    s = next(i for i, l in enumerate(lines) if re.search(start_pat, l))
    e = next(i for i, l in enumerate(lines) if i > s and re.search(end_pat, l))
    return lines[s:e]
PDF_ORDER = ["AF3", "Boltz-1", "Chai-1", "DeepFoldRNA", "DRfold", "HF3", "NuFold", "RhoFold+", "RF2NA", "trRosettaRNA"]
PDF_NAME = {"HF3": "HelixFold3", "RF2NA": "RosettaFoldNA"}
for lab, subset, end in [("Table S6", "monomer-easy", r"Table S7\."), ("Table S7", "monomer-hard", r"Table S8\.")]:
    blk = block(lab + r"\.", end)
    hdr = next(l for l in blk if "AF3" in l and "trRosettaRNA" in l).split()
    assert hdr == ["AF3", "Boltz-1", "Chai-1", "DeepFoldRNA", "DRfold", "HelixFold3", "NuFold", "RhoFold+", "RosettaFoldNA", "trRosettaRNA"], hdr
    seen = []
    for l in blk:
        parts = l.split()
        if parts and parts[0] in ("TM-score", "GDT-TS", "INF", "lDDT"):
            col, vals = parts[0], parts[1:]
            assert len(vals) == 10 and all(v.endswith("%") for v in vals), l
            seen.append(col)
            for m, v in zip(PDF_ORDER, vals):
                cell(lab, m, subset, col, v, "success", f"Supplementary {lab}, row '{col}', column '{PDF_NAME.get(m, m)}'", review_pdf, SIDS_S, len(seen))
    assert seen == ["TM-score", "GDT-TS", "INF", "lDDT"], seen
blk = block(r"Table S15\.", r"Supplementary Figures")
hdr = next(l for l in blk if "AF3" in l).split()
assert hdr == ["AF3", "Boltz-1", "HF3", "RF2NA"], hdr
n15 = 0
for l in blk:
    m_ = re.match(r"^\s*(RNA-protein|RNA-RNA)\s+(.*)$", l)
    if m_:
        vals = m_.group(2).split()
        assert len(vals) == 4, l
        n15 += 1
        for m, v in zip(hdr, vals):
            cell("Table S15", m, "complex-all", m_.group(1), v, "if", f"Supplementary Table S15, row '{m_.group(1)}', column '{m}'", review_pdf, SIDS_S, n15)
assert n15 == 2

# Review D1-D3: result-level disputes, so the rest of the source stays comparable.
D1 = ["Ludaic and Elofsson 2026 print identical INF, GDT-TS and lDDT for DRfold and DeepFoldRNA in Tables 2-3, and the per-target columns of Supplementary Tables S3-S5 are identical for every target, while their TM-scores differ. At least one method's values are not its own; not resolved from the source."]
disputed = {f"{P}-result-{m}-monomer-{s}-{a}-{x}": D1 for m in ("drfold", "deepfoldrna") for s in ("easy", "hard")
            for a in ("mean", "success") for x in ("gdt-ts", "inf", "lddt")}
disputed[f"{P}-result-rf2na-monomer-hard-mean-inf"] = ["Table 3 prints INF 0.668 for RF2NA on the hard set; the mean of the RF2NA column of Supplementary Table S3 over the 49 hard targets is 0.608. Recorded as printed; not resolved from the source."]
disputed[f"{P}-result-af3-monomer-hard-success-gdt-ts"] = ["Supplementary Table S7 prints 37.78% for AF3 GDT-TS on the hard set, which is not a whole number of the 49 hard targets; Supplementary Table S4 has 19 of 49 AF3 targets above the 0.45 threshold (38.78%). Recorded as printed; not resolved from the source."]
assert len(disputed) == 26
recs = {r["id"]: r for r in b.records}
assert recs[f"{P}-result-rf2na-monomer-hard-mean-inf"]["attributes"]["printed_value"] == "0.668"
assert recs[f"{P}-result-af3-monomer-hard-success-gdt-ts"]["attributes"]["printed_value"].startswith("37.78")
PDF_TABLES = ("Supplementary Table S6,", "Supplementary Table S7,", "Supplementary Table S15,")
finalise(b.records, "reviewer-ro-1",
         "Re-fetched the PMC XML and the supplementary PDF and matched their SHA-256. An independent parse of Tables 2-5 and Supplementary Tables S6, S7 and S15 (pdftotext -layout and -raw) matched all 216 printed and numeric values and locators; 42 cells were also checked by hand. Success rates in S6-S7 were recomputed from S2-S5 as a consistency check, not as a derivation.",
         disputed=disputed,
         methods=lambda r: ["source-hash-verification", "pdf-text-parse", "independent-cell-check"] if r["attributes"]["source_locator"].startswith(PDF_TABLES)
                           else ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"])

counts = b.write()
print(json.dumps(counts), sum(1 for r in b.records if r["kind"] == "result"))
