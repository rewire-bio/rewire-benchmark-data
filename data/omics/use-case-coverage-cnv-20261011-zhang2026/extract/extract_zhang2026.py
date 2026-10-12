"""Extract Zhang, Zhang and Chen 2026 (Global Medical Genetics 13:100096) Tables 3 and 4 into batch records.

Usage: python3 -I extract_zhang2026.py <PMC13018948 fullTextXML> <batch folder>
Parses both tables from the pinned Europe PMC article XML, asserts captions, headers and row labels, and writes
needs_review records.
"""
import json, os, sys
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, finalize_review, judgement, refresh_coverage, sha256

XML, OUT = sys.argv[1], sys.argv[2]
SHA = "a0810a8bff1ab3d2603a4832a56291cc182c8530aa8dffc6ac5318abd989ada0"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13018948/fullTextXML"
assert sha256(XML) == SHA

P = "cnv-20261011-zhang2026"
b = Batch(OUT, P, areas=["dna-genomes"])
SRC = P + "-source-article"
UC = "use-case-cnv-detection-characterisation"
UC_NAME = "Select a copy-number variant detection and characterisation workflow"

b.source(SRC, "Can automated copy number variation pathogenicity prediction tools replace manual review under the ACMG framework? A clinical validation (Zhang, Zhang and Chen, Global Medical Genetics 2026)", {
    "url": "https://doi.org/10.1016/j.gmg.2026.100096",
    "artifact_url": URL,
    "version": "Global Medical Genetics 13:100096 (2026), published online 2026-03-06; PMC13018948 full-text XML",
    "retrieved_at": "2026-10-11T21:36:59Z",
    "artifact_sha256": SHA,
    "doi": "10.1016/j.gmg.2026.100096",
    "publication_status": "peer_reviewed",
    "licence": "CC-BY-NC-ND-4.0",
    "media_type": "application/xml",
    "limitations": [
        "Methods 'Data analysis' list AUC-ROC, specificity, sensitivity, PPV, FPR and F1 but do not say how the five-category results in Table 3 are averaged across classes.",
        "Supplementary Table S1 (MarCNV-ISV conservative and progressive modes) was not retrieved.",
        "The benchmark dataset is not public ('available from the corresponding author on reasonable request').",
        "Not archived in the batch: CC BY-NC-ND licence; hash and locators only.",
        # review correction 3
        "The Abstract gives ClassifyCNV VUS accuracy 95.33%; Table 4 prints 94.92% (duplications) and 95.74% (deletions), which with the Table 2 class sizes (886 and 329) pool to about 95.1%.",
        "Two Table 4 deletion cells are not a whole-number share of the Table 2 class size (AnnotSV P 95.16% of 287 P and LP deletions; MarCNV-ISV VUS 89.86% of 329 VUS deletions); the other 28 cells are.",
    ],
})

root = ET.parse(XML).getroot()
def txt(e): return " ".join("".join(e.itertext()).split())
TW = {tw.get("id"): tw for tw in root.iter("table-wrap")}
def rows(tid):
    return [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in TW[tid].iter("tr")]

TOOLS = [  # label, key, version, method type, parameters
    ("AnnotSV", "annotsv", "v3.5.2", "conventional_pipeline", "ACMG rule-based scoring; run from GitHub or the official web interface per the original instructions"),
    ("ClassifyCNV", "classifycnv", None, "conventional_pipeline", "ACMG rule-based scoring; run per the original instructions"),
    ("dbCNV", "dbcnv", None, "supervised_machine_learning", "XGBoost five-category labels; mapped to 1 to 5 for AUC-ROC"),
    ("MarCNV-ISV", "marcnv-isv", None, "supervised_machine_learning", "Balanced mode (best overall of the conservative, balanced and progressive modes; others in Supplementary Table S1)"),
    ("X-CNV", "x-cnv", None, "supervised_machine_learning", "XGBoost score and classification; run per the original instructions"),
]
DESC = {
    "annotsv": "Rule-based ACMG CNV annotation and classification tool.",
    "classifycnv": "Rule-based ACMG CNV classification tool.",
    "dbcnv": "XGBoost CNV pathogenicity classifier.",
    "marcnv-isv": "Hybrid framework combining rule-based ACMG evidence with the ISV machine-learning model.",
    "x-cnv": "XGBoost CNV pathogenicity predictor.",
}
CFG = {}
for label, key, version, mt, params in TOOLS:
    mid = b.rid("method", key)
    b.entity("method", mid, label, DESC[key], [SRC], {
        "reported_name": label, "entity_level": "method", "source_locator": "Table 1; Methods 'Screening and acquisition of automated CNV prediction models'",
        "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the version used is on the configuration"}},
    }, method_types=[mt])
    CFG[label] = b.rid("config", key)
    attrs = {"reported_name": label, "foundation_model_eligible": False, "parameters": params + "; input CNV coordinates lifted from hg19 to hg38",
             "access_reuse": "Obtained from GitHub or the official web interface (Methods 'Model operation and results collection')",
             "source_locator": "Table 1; Methods 'Model operation and results collection'"}
    if version:
        attrs["version"] = version
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "Table 1 prints a version for AnnotSV only"}}
    b.entity("configuration", CFG[label], f"{label} (Zhang et al. 2026)", f"{label} as run by Zhang et al. 2026.", [SRC], attrs,
             method_types=[mt], links=[{"relation": "configuration_of", "target_id": mid}])

DATA = b.rid("data", "expert-acmg-cnv-benchmark")
b.entity("dataset", DATA, "Expert-classified ACMG CNV benchmark (Zhang et al. 2026, 3,031 CNVs)",
         "CNVs with ACMG five-category classifications from five published clinical studies and an internal CNV-seq laboratory set, deduplicated and lifted to hg38.",
         [SRC], {"version": "As assembled by Zhang et al. 2026 (not public)",
                 "population": "3,031 CNVs: 2,125 duplications (1,026 B, 22 LB, 886 VUS, 57 LP, 134 P) and 906 deletions (277 B, 13 LB, 329 VUS, 59 LP, 228 P); sources a Brazilian neurodevelopmental cohort, spontaneous-abortion studies, prenatal VUS follow-up, a 3,429-amniocentesis CNV-seq cohort, a paediatric epilepsy genome cohort and the authors' internal CNV-seq cases (December 2019 to November 2025)",
                 "split": "No split; whole set scored", "reuse_restrictions": "Available from the corresponding author on reasonable request",
                 "source_locator": "Table 2; Methods 'Establishing a clinical CNV benchmark dataset'; Results 'Dataset overview'; Data availability"})

COMMON = ["Reference labels are expert ACMG classifications, a semi-quantitative standard with known inter-reviewer variability (Discussion paragraph 5).",
          "The set is enriched for pregnancy-loss and prenatal cases and is imbalanced (benign is about half of the duplications), which the authors say affects the metrics (Discussion paragraphs 5 and 6).",
          "Classification of already detected CNVs from their coordinates; no read data or detection step is evaluated.",
          "Some training sets of the evaluated tools (ClinVar, ClinGen, DGV) may overlap the published cohorts used as reference; the paper does not test this."]
PROTS = {
    "five-category": dict(name="ACMG five-category CNV pathogenicity classification against expert labels (Zhang et al. Table 3)",
        protocol="Run each tool on the 3,031 CNVs and compare its five-category output (benign, likely benign, VUS, likely pathogenic, pathogenic) with the expert classification; report accuracy, sensitivity, specificity, PPV, FPR, F1 and MCC.",
        locator="Table 3; Methods 'Data analysis'; Results 'Comparative analysis of clinical metrics'",
        limits=["How the five-class metrics are averaged across classes is not stated."]),
    "three-category-duplications": dict(name="Three-category CNV classification, per-class agreement on duplications (Zhang et al. Table 4, DUP)",
        protocol="Merge benign with likely benign and pathogenic with likely pathogenic; for the 2,125 duplications report, per reference class (B, VUS, P), the share of CNVs the tool assigns to that class (printed as 'Accuracy').",
        locator="Table 4 rows 'DUP' B, VUS, P; Results 'Analysis of three-category performance'", limits=[]),
    "three-category-deletions": dict(name="Three-category CNV classification, per-class agreement on deletions (Zhang et al. Table 4, DEL)",
        protocol="As for duplications, on the 906 deletions.",
        locator="Table 4 rows 'DEL' B, VUS, P; Results 'Analysis of three-category performance'", limits=[]),
}
# review correction 2: appended to all three protocols and all three judgements
DBCNV = ("Two of the three authors (X. Zhang and D. Chen) are authors of dbCNV (reference 24), developed in the same laboratory, so the dbCNV rows are author_reported. "
         "dbCNV's original test set was that laboratory's internal dataset, and this benchmark includes the laboratory's internal CNV-seq cases (December 2019 to November 2025); "
         "overlap is not tested. The paper declares no competing interests.")
PID = {}
for key, p in PROTS.items():
    PID[key] = b.rid("protocol", key)
    b.entity("protocol", PID[key], p["name"], p["protocol"], [SRC], {"protocol": p["protocol"], "version": p["locator"].split(";")[0],
             "source_locator": p["locator"], "limitations": p["limits"] + COMMON + [DBCNV]}, links=[{"relation": "uses_data", "target_id": DATA}])

EVAL = {}
POP = {"five-category": "3,031 CNVs (2,125 duplications, 906 deletions)", "three-category-duplications": "2,125 duplications",
       "three-category-deletions": "906 deletions"}
for key in PROTS:
    for label, tkey, *_ in TOOLS:
        EVAL[(key, label)] = b.rid("eval", key, tkey)
        b.evaluation(EVAL[(key, label)], f"{label} on the expert-classified ACMG CNV benchmark ({key.replace('-', ' ')})", [SRC], CFG[label], PID[key], DATA,
                     "author_reported" if label == "dbCNV" else "independent_paper", {"dataset_version": "As assembled by Zhang et al. 2026", "split": "No split", "population": POP[key],
                                           "inputs": "CNV coordinates (hg38) and type", "adaptation": None,
                                           "metric_implementation": "Microsoft Excel 2021 (Methods 'Data analysis')" if key == "five-category" else "Share of reference-class CNVs assigned to the same merged class",
                                           "aggregation": None if key == "five-category" else "Per reference class", "budget": None},
                     f"Table {'3' if key == 'five-category' else '4'} column or row '{label}'",
                     missing={"comparison.adaptation": {"reason": "inapplicable", "note": "Published tools run as distributed"},
                              **({"comparison.aggregation": {"reason": "unreported", "note": "Averaging across the five classes not stated"}} if key == "five-category" else {})})

METHOD_NOTE = "Parsed the pinned PMC13018948 article XML (table-wrap elements) with a stdlib reader; caption, header and row labels asserted; printed cell text kept exactly."
# Table 3
t3 = rows("tbl0015")
assert txt(TW["tbl0015"].find("label")) == "Table 3" and txt(TW["tbl0015"].find("caption")) == "Performance characteristics of each model."
assert t3[0] == ["Model", "Accuracy (%)", "Sensitivity (%)", "Specificity (%)", "PPV*(%)", "FPR*(%)", "F1(%)", "MCC*"], t3[0]
assert [r[0] for r in t3[1:]] == [t[0] for t in TOOLS]
M3 = [("accuracy", "higher", "percent"), ("recall", "higher", "percent"), ("specificity", "higher", "percent"), ("precision", "higher", "percent"),
      ("false-positive-rate", "lower", "percent"), ("f1-score", "higher", "percent"), ("matthews-correlation-coefficient", "higher", "unitless")]
Q3 = "ACMG five-category classification; averaging across classes not stated"
for r in t3[1:]:
    for (metric, direction, unit), col, cell in zip(M3, t3[0][1:], r[1:]):
        b.result(b.rid("result", "five-category", r[0], metric), f"{r[0]} {col} (Zhang et al. Table 3)", SRC, [SRC], EVAL[("five-category", r[0])],
                 cell, metric, direction, unit, f"Table 3, row '{r[0]}', column '{col}'",
                 extraction_review(["deterministic-table-parse"], METHOD_NOTE, SHA, URL), qualifier=Q3)
# Table 4
t4 = rows("tbl0020")
assert txt(TW["tbl0020"].find("label")) == "Table 4" and txt(TW["tbl0020"].find("caption")) == "Accuracy of the adjusted data from each model across different datasets."
assert t4[0] == ["Category", "AnnotSV (%)", "ClassifyCNV (%)", "dbCNV (%)", "MarCNV-ISV (%)", "X-CNV (%)"], t4[0]
labels4 = [r[:-5] for r in t4[1:]]
assert labels4 == [["DUP*", "B*"], ["VUS*"], ["P*"], ["DEL*", "B*"], ["VUS*"], ["P*"]], labels4
CLS = {"B*": "benign (benign and likely benign merged)", "VUS*": "variant of uncertain significance", "P*": "pathogenic (pathogenic and likely pathogenic merged)"}
for i, r in enumerate(t4[1:]):
    group = "three-category-duplications" if i < 3 else "three-category-deletions"
    cls = r[-6]
    for tool, cell in zip([t[0] for t in TOOLS], r[-5:]):
        b.result(b.rid("result", group, tool, cls.rstrip("*").lower()), f"{tool} {('DUP' if i < 3 else 'DEL')} {cls.rstrip('*')} (Zhang et al. Table 4)", SRC, [SRC],
                 EVAL[(group, tool)], cell, "recall", "higher", "percent",
                 f"Table 4, block '{'DUP' if i < 3 else 'DEL'}', row '{cls.rstrip('*')}', column '{tool} (%)'",
                 extraction_review(["deterministic-table-parse"], METHOD_NOTE, SHA, URL),
                 qualifier=f"per-class recall for reference class {CLS[cls]}, three-category scheme; printed as 'Accuracy'")

# Judgements
links = []
for order, key in enumerate(PROTS, start=1):
    cid, _ = judgement(
        b, UC, UC_NAME, PID[key], PROTS[key]["name"], [SRC], [{"source_id": SRC, "locator": PROTS[key]["locator"]}], "proxy",
        ("Accuracy, sensitivity, specificity, PPV, FPR, F1 and MCC" if key == "five-category" else "Per-class agreement") +
        " of AnnotSV, ClassifyCNV, dbCNV, MarCNV-ISV and X-CNV against expert ACMG classifications" + ("" if key == "five-category" else f" ({POP[key]})"),
        "Proxy: automated pathogenicity classification of already detected CNVs bears on the characterisation and analyst-assessment part of the question, but no detection from sequencing reads is evaluated and the reference is expert ACMG labelling.",
        ["Inspect every linked evaluation's source locator before citing a result.",
         "Do not combine this mapping's evaluations with detection results from other protocols; the endpoint is classification, not detection."],
        PROTS[key]["limits"] + COMMON + [DBCNV],
        "accuracy" if key == "five-category" else "recall", "zhang2026-cnv-classification", "Automated ACMG CNV classification tools against expert labels (Zhang et al. 2026)",
        {"five-category": "Five-category classification", "three-category-duplications": "Three-category, duplications", "three-category-deletions": "Three-category, deletions"}[key], order,
        "Recorded from the 2026-10-11 use-case literature pass (data/omics/use-case-coverage-cnv-20261011-zhang2026); pending independent review.")
    links.append({"use_case": UC, "relation": "assessed_by", "target_id": PID[key], "judgement_claim": cid})

finalize_review(b, {  # reviewed_evaluations as listed by reviewer-scnv
    "use-case-mapping-" + P + "-" + key: [P + "-eval-" + key + "-" + t for t in ("annotsv", "classifycnv", "dbcnv", "marcnv-isv", "x-cnv")] for key in PROTS})
counts = b.write({"use-case-links.json": json.dumps({"note": "Proposed assessed_by links to add to the use_case record after the judgement claims are reviewed. Not applied by the extractor.", "links": links}, indent=1) + "\n"})
refresh_coverage(OUT)
print(json.dumps(counts))
