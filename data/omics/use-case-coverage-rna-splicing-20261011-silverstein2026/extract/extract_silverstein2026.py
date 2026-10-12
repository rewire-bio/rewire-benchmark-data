"""Extract Silverstein et al. 2026 (medRxiv 10.64898/2026.01.27.26344940 v1) Table S9 into batch records.

Usage: python3 -I extract_silverstein2026.py <article.source.xml> <media-3.xlsx> <batch folder>
Reads every cell of Supplementary Table S9 (sheet 'Table S9', A1:J10) with a stdlib OOXML reader, asserts the
header and row labels, and writes needs_review records. Values are formula results stored in the workbook; the
printed value is the shortest round-trip decimal of the stored double (the cells use the General format).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import finalize_review, refresh_coverage, Batch, extraction_review, judgement, sha256, shortest
from ooxml import read_sheets

ARTICLE, XLSX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ARTICLE_SHA = "8b987ac49f086adc0a191522436529a70f243505f7dda9926786004e15b4601c"
XLSX_SHA = "3d137444b13225cf1223ad73758fdfcb4b5f772263e0aafd827d8ca57ca00120"
ARTICLE_URL = "https://www.medrxiv.org/content/early/2026/01/28/2026.01.27.26344940.source.xml"
XLSX_URL = "https://www.medrxiv.org/content/medrxiv/early/2026/01/28/2026.01.27.26344940/DC3/embed/media-3.xlsx?download=true"
assert sha256(ARTICLE) == ARTICLE_SHA and sha256(XLSX) == XLSX_SHA

P = "rna-splicing-20261011-silverstein2026"
b = Batch(OUT, P, areas=["rna-transcriptomes"])
SRC_A, SRC_X = P + "-source-article", P + "-source-tables-s1-s10"
SRCS = [SRC_A, SRC_X]
UC = "use-case-patient-rna-splicing-validation"
UC_NAME = "Select a patient-RNA splicing-variant validation workflow"

# review correction 2
S7_CONFLICT = ("Table S7 true-negative rows do not reproduce Table S9 rows 7 and 8: read as in Tables S3, S4 and S8 ('YES' = no outlier), Table S7 gives OUTRIDER 8 of 9 "
               "negative samples without outliers (Table S9: 4) and OUTRIDER + GTEx 1 of 6 (Table S9: 1 of 5). The prose rates (56% and 83%) match Table S9 for OUTRIDER "
               "and Table S7 for OUTRIDER + GTEx.")
b.source(SRC_A, "Benchmarking RNA-seq Tools for Real-World Diagnostic Applications (Silverstein et al., medRxiv 2026)", {
    "url": "https://doi.org/10.64898/2026.01.27.26344940",
    "artifact_url": ARTICLE_URL,
    "version": "medRxiv preprint version 1, posted 2026-01-28; JATS source XML",
    "retrieved_at": "2026-10-11T21:38:32Z",
    "artifact_sha256": ARTICLE_SHA,
    "doi": "10.64898/2026.01.27.26344940",
    "publication_status": "preprint",
    "licence": "CC0-1.0",
    "media_type": "application/xml",
    "limitations": [
        "Preprint, not peer reviewed.",
        "Table 1 is an image in the source XML and was not read.",
        "Per-tissue recall values in Results ('Recall rate of splice tools identifies ensemble strategy as most sensitive') come from Figure 2A and prose; they are not in Table S9 and were not extracted.",
    ],
    "retrieval_note": "medRxiv returned HTTP 429 (rate limit) on the first attempt; the second attempt succeeded.",
})
b.source(SRC_X, "Silverstein et al. 2026 Supplemental Tables S1-S10 (medRxiv media-3.xlsx)", {
    "url": "https://doi.org/10.64898/2026.01.27.26344940",
    "artifact_url": XLSX_URL,
    "version": "medRxiv preprint version 1 supplement DC3 (file 344940_file09.xlsx in the JATS XML)",
    "retrieved_at": "2026-10-11T21:38:52Z",
    "artifact_sha256": XLSX_SHA,
    "doi": "10.64898/2026.01.27.26344940",
    "publication_status": "preprint",
    "licence": "CC0-1.0",
    "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "limitations": [
        "Table S9 values are spreadsheet formulas over the TP, FN, TN and FP cells of the same row; the stored results are recorded.",
        "Tables S3 to S5 list 22 true-negative rows (6 muscle, 3 fibroblast, 13 cycloheximide-treated fibroblast); Results and Table S9 use 21 true-negative samples.",
        "Results ('True negative analysis reveals high false positive rates') give an OUTRIDER + GTEx false-positive rate of 83%; Table S9 row 8 (TN 1, FP 4) implies 4 of 5 (80%).",
        "Table S9 gives LeafcutterMD 67 positives (TP 0 + FN 67) while FRASER, run on the same three tissue sets, has 68 (TP 21 + FN 47).",
        "Cell I6 (LeafcutterMD F1) holds a typed 0 rather than the row formula; with precision and recall both 0 the F1 formula would be undefined.",
        S7_CONFLICT,
    ],
})

sheets = read_sheets(XLSX)
s9 = sheets["Table S9"]
HEAD = ["Tool", "True Positives", "False Negatives", "True Negatives", "False Positives", "Accuracy", "Precision", "Recall", "F1", "MCC"]
assert [s9[c + "1"][0] for c in "ABCDEFGHIJ"] == HEAD
ROWS = ["rMATS", "MINTIE", "FRASER", "FRASER2.0", "LeafcutterMD", "OUTRIDER", "OUTRIDER + GTEx", "ANEVA-H", "MAE"]
assert [s9[f"A{r}"][0] for r in range(2, 11)] == ROWS
assert not any(k for k in s9 if int("".join(ch for ch in k if ch.isdigit())) > 10)

# Datasets and protocols ------------------------------------------------------------------------------------------
DATA = b.rid("data", "nih-neuromuscular-diagnosed-rnaseq")
b.entity("dataset", DATA, "NIH neuromuscular diagnosed RNA-seq truth set (Silverstein et al. 2026)",
         "RNA-seq from 97 previously diagnosed samples of patients with pediatric neuromuscular disease: 76 true-positive samples from 68 probands with confirmed aberrant RNA events and 21 true-negative samples with pathogenic variants not expected to change RNA.",
         SRCS, {
             "version": "As published (dbGaP phs001272.v2.p1)",
             "assay": "Short-read RNA-seq of skeletal muscle, cultured fibroblasts and cycloheximide-treated fibroblasts, sequenced in small batches over 14 years with mixed stranded and unstranded libraries; GTEx v10 pipeline, STAR v2.7.10a, GRCh38 (GENCODE 39)",
             "population": "97 diagnosed samples; 68 true-positive splicing variants (16 muscle, 7 fibroblast, 45 cycloheximide-treated fibroblast), 15 expression true-positive genes and 8 allelic-imbalance true-positive genes; 21 true-negative samples. Tool cohorts mixed diagnosed and undiagnosed samples by tissue (muscle n=71, fibroblast n=37, cycloheximide-treated fibroblast n=79).",
             "split": "No split; retrospective detection of known events",
             "reuse_restrictions": "Controlled access through dbGaP phs001272.v2.p1",
             "source_locator": "Methods 'Patient Recruitment', 'RNA-seq Alignment', 'True Positive Definition', 'True Negative Definition' and 'One vs All Splice Tools'; Results 'Truth set selection'; Tables S3 to S8; Data Availability",
         })

COMMON_LIMITS = [
    "The authors did not develop rMATS-turbo, MINTIE, FRASER, LeafcutterMD, OUTRIDER or the DROP MAE module. ANEVA-h is the authors' own method: two of its authors (K. R. Ganapathy and S. Silverstein) are the first and third authors of reference 36, the ANEVA-h preprint, so the ANEVA-H row is recorded as author_reported.",
    "Positives are counted per known event or gene, negatives per true-negative sample: a negative sample with any reported outlier counts as one false positive. Accuracy, precision and MCC therefore mix event-level and sample-level units (Methods 'True Positive and Negative Detection').",
    # review correction 3
    "Variants with clinically interpretable mechanisms were selected; the authors state this favours clearly defined events and likely underestimates tool sensitivity, and that binary outlier scoring of negatives may overestimate false-positive rates and lowers MCC (Discussion, limitations paragraph).",
    "Retrospective study of a single centre's neuromuscular cohort; no confidence intervals are printed.",
]

PROTOCOLS = {
    "splicing": dict(
        name="Recovery of known pathogenic splicing events and outlier calls in true-negative samples, patient RNA-seq (Silverstein et al. Table S9, splicing tools)",
        desc="Each aberrant-splicing caller is scored on known pathogenic splicing events (exact coordinate match) and on true-negative samples (any outlier is a false positive), aggregated across the tissue sets the tool was run on.",
        protocol="Run FRASER and LeafcutterMD (one versus all, by tissue cohort: muscle, fibroblast, cycloheximide-treated fibroblast), FRASER2.0 (muscle only) and rMATS-turbo and MINTIE (each patient against ten GTEx tissue-matched controls; muscle and fibroblast only), all at FDR 5%. A true positive is an exact coordinate match to the validated splice event; a true-negative sample is correct only if no outlier is reported. Table S9 aggregates true positives and negatives across tissue types and derives accuracy, precision, recall, F1 and MCC.",
        locator="Table S9 rows 2 to 6; Methods 'One vs All Splice Tools', 'Case vs Control Splice Tools', 'True Positive and Negative Detection' and 'Performance Metrics'",
        limits=["Denominators differ by tool: rMATS and MINTIE 23 positives (muscle and fibroblast), FRASER 68 and LeafcutterMD 67 (three tissue sets), FRASER2.0 16 (muscle only).",
                "Splicing true positives require at least 3 split reads supporting the novel junction in manual IGV review, so events invisible in the RNA-seq data are not counted."],
        relevance="direct", headline="recall", stratum="Aberrant-splicing callers", order=1),
    "expression": dict(
        name="Recovery of known expression-outlier genes and outlier calls in true-negative samples, patient RNA-seq (Silverstein et al. Table S9, OUTRIDER)",
        desc="OUTRIDER with and without 100 GTEx muscle controls, scored on known loss-of-function expression genes and on true-negative samples.",
        protocol="Run OUTRIDER one versus all through DROP v1.2.2 at FDR 1% on each tissue cohort, and a second muscle run with 100 GTEx muscle controls added. A true positive is the known gene among reported outliers; a true-negative sample is correct only if no outlier is reported.",
        locator="Table S9 rows 7 and 8; Methods 'Expression Tools' and 'True Positive and Negative Detection'; Table S7",
        limits=["OUTRIDER + GTEx was run on muscle only (14 positives); OUTRIDER on muscle and fibroblast (15 positives)."],
        relevance="proxy", headline="recall", stratum="Expression-outlier caller", order=2),
    "allelic-imbalance": dict(
        name="Recovery of known allelic-imbalance genes and outlier calls in true-negative samples, patient muscle RNA-seq (Silverstein et al. Table S9, ANEVA-H and MAE)",
        desc="Gene-level ANEVA-H and variant-level DROP MAE, scored on known monoallelic loss-of-function events and on true-negative samples, muscle with matched DNA variant calls.",
        protocol="Restrict to 59 muscle samples with exome or genome VCFs. Run the DROP MAE module (v1.4.0, allelic threshold 70) and ANEVA-h (phASER gene-level ASE, ANEVA-DOT test, GTEx v8 muscle reference, BH FDR < 0.05). A true positive requires the correct rare variant (MAE) or gene (ANEVA-H); a true-negative sample is correct only if no outlier is reported.",
        locator="Table S9 rows 9 and 10; Methods 'Allelic Imbalance Tools' and 'True Positive and Negative Detection'; Table S8",
        limits=["Eight true-positive genes and five or six true-negative samples; MAE reports TN 0 and FP 5, ANEVA-H TN 1 and FP 4."],
        relevance="proxy", headline="recall", stratum="Allelic-imbalance callers", order=3),
}
PROT_ID = {}
for key, p in PROTOCOLS.items():
    pid = b.rid("protocol", key)
    PROT_ID[key] = pid
    b.entity("protocol", pid, p["name"], p["desc"], SRCS, {
        "protocol": p["protocol"], "version": "Table S9 (medRxiv v1 supplement)", "source_locator": p["locator"],
        "limitations": p["limits"] + COMMON_LIMITS + ([S7_CONFLICT] if key == "expression" else []),
    }, links=[{"relation": "uses_data", "target_id": DATA}])

# Methods and configurations --------------------------------------------------------------------------------------
NEW_METHODS = {
    "mintie": ("MINTIE", "Reference-free detection of novel splice and structural variants in patient RNA-seq against a control set.", "c22"),
    "aneva-h": ("ANEVA-h", "Haplotype-level allelic-expression outlier test (ANEVA-DOT applied to phASER gene-level allelic expression).", "c36"),
    "drop-mae": ("DROP MAE module", "Variant-level mono-allelic expression detection module of the DROP pipeline.", "c24"),
}
METHOD_ID = {"rmats": "rna-splicing-20261009-method-rmats-turbo", "fraser": "rna-splicing-20261009-method-fraser",
             "leafcutter": "rna-splicing-20261009-method-leafcuttermd", "outrider": "rna-splicing-20261009-method-outrider"}
for key, (name, desc, ref) in NEW_METHODS.items():
    METHOD_ID[key] = b.rid("method", key)
    b.entity("method", METHOD_ID[key], name, desc, SRCS, {
        "reported_name": name, "entity_level": "method",
        "source_locator": f"Methods 'Computational Tools' to 'Allelic Imbalance Tools'; reference {ref.lstrip('c')}",
        "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the version used is on the configuration"}},
    }, method_types=["conventional_pipeline"])

CONFIGS = [
    # row label, key, method, protocol, version, parameters, locator, origin, population
    ("rMATS", "rmats", "rmats", "splicing", "v4.1.2",
     "Each patient against ten GTEx tissue-matched controls; --novelSS --allow-clipping; -mel 700; FDR 5%; all five MATS event files assessed",
     "Methods 'Case vs Control Splice Tools'", "independent_paper", "23 known splicing events (16 muscle, 7 fibroblast); 9 true-negative samples (6 muscle, 3 fibroblast)"),
    ("MINTIE", "mintie", "mintie", "splicing", "v0.4.1",
     "FASTQ against ten GTEx tissue-matched controls; splice_motif_mismatch = 3; FDR 5%; splice-related outliers only",
     "Methods 'Case vs Control Splice Tools'", "independent_paper", "23 known splicing events (16 muscle, 7 fibroblast); 9 true-negative samples (6 muscle, 3 fibroblast)"),
    ("FRASER", "fraser", "fraser", "splicing", "DROP v1.2.2",
     "One versus all by tissue cohort (muscle n=71, fibroblast n=37, CHX fibroblast n=79); default parameters; FDR 5%; stranded and unstranded libraries combined",
     "Methods 'One vs All Splice Tools'", "independent_paper", "68 known splicing events (16 muscle, 7 fibroblast, 45 CHX fibroblast); 21 true-negative samples"),
    ("FRASER2.0", "fraser2-0", "fraser", "splicing", "DROP v1.4.0",
     "FRASER 2.0 one versus all, muscle cohort only; standard settings; FDR 5%",
     "Methods 'One vs All Splice Tools'; Results 'Recall rate of splice tools'", "independent_paper", "16 known splicing events (muscle); 6 true-negative samples (muscle)"),
    ("LeafcutterMD", "leafcuttermd", "leafcutter", "splicing", "v0.2.9",
     "One versus all by tissue cohort; LeafCutter intron clusters (min 50 split reads per cluster, max intron 500 kb); groups with >= 20 reads; FDR 5%",
     "Methods 'One vs All Splice Tools'", "independent_paper", "67 known splicing events per Table S9 (three tissue sets); 21 true-negative samples"),
    ("OUTRIDER", "outrider", "outrider", "expression", "DROP v1.2.2",
     "One versus all by tissue cohort; recommended parameters; FDR 1%",
     "Methods 'Expression Tools'", "independent_paper", "15 known expression-outlier genes (14 muscle, 1 fibroblast); 9 true-negative samples"),
    ("OUTRIDER + GTEx", "outrider-plus-gtex", "outrider", "expression", "DROP v1.2.2",
     "Muscle cohort plus 100 GTEx muscle control samples; recommended parameters; FDR 1%",
     "Methods 'Expression Tools'; Table S2", "independent_paper", "14 known expression-outlier genes (muscle); 5 true-negative samples per Table S9"),
    ("ANEVA-H", "aneva-h", "aneva-h", "allelic-imbalance", "ANEVA-DOT R package (version unreported)",
     "phASER v1.1.1 gene-level ASE from EAGLE v2.4.1-phased genotypes; ANEVADOT_test with default parameters; GTEx v8 muscle reference (706 samples); >= 10 reads per gene; BH FDR < 0.05",
     "Methods 'Allelic Imbalance Tools'", "author_reported", "8 known allelic-imbalance genes (muscle with VCFs); 5 true-negative samples"),
    ("MAE", "mae", "drop-mae", "allelic-imbalance", "DROP v1.4.0",
     "MAE module with allelic balance threshold 70 instead of 80; standard parameters",
     "Methods 'Allelic Imbalance Tools'", "independent_paper", "8 known allelic-imbalance genes (muscle with VCFs); 5 true-negative samples"),
]
METRICS = {  # column: (metric, direction, unit, unit_detail)
    "B": ("true-positive-count", "higher", "count", "known events (splicing) or genes (expression, allelic imbalance) detected"),
    "C": ("false-negative-count", "lower", "count", "known events or genes not detected"),
    "D": ("true-negative-count", "higher", "count", "true-negative samples with no reported outlier"),
    "E": ("false-positive-count", "lower", "count", "true-negative samples with at least one reported outlier"),
    "F": ("accuracy", "higher", "fraction", None),
    "G": ("precision", "higher", "fraction", None),
    "H": ("recall", "higher", "fraction", None),
    "I": ("f1-score", "higher", "fraction", None),
    "J": ("matthews-correlation-coefficient", "higher", "unitless", None),
}
QUAL = "positives per known event or gene, negatives per true-negative sample; aggregated across the tissue sets each tool was run on (Table S9)"
METHOD_NOTE = ("Read sheet 'Table S9' of the pinned workbook with a stdlib OOXML reader (extract/ooxml.py); header row A1:J1 and "
               "tool labels A2:A10 asserted; printed_value is the shortest round-trip decimal of the stored cell value.")

for r, (label, key, method, prot, version, params, mloc, origin, population) in enumerate(CONFIGS, start=2):
    assert s9[f"A{r}"][0] == label
    cfg = b.rid("config", key)
    b.entity("configuration", cfg, f"{label} (Silverstein et al. 2026)", f"{label} as run in the Silverstein et al. 2026 benchmark.", SRCS, {
        "reported_name": label, "foundation_model_eligible": False, "version": version, "parameters": params,
        "access_reuse": "Open-source tool; run by the authors on the NIH Biowulf cluster",
        "source_locator": mloc + "; Table S9 row label",
    }, method_types=["conventional_pipeline"], links=[{"relation": "configuration_of", "target_id": METHOD_ID[method]}])
    ev = b.rid("eval", key)
    b.evaluation(ev, f"{label} on the NIH neuromuscular diagnosed RNA-seq truth set ({prot})", SRCS, cfg, PROT_ID[prot], DATA, origin, {
        "dataset_version": "NIH neuromuscular diagnosed RNA-seq truth set (dbGaP phs001272.v2.p1), as published",
        "split": "No split", "population": population,
        "inputs": "Patient tissue RNA-seq aligned with STAR to GRCh38 (GTEx v10 pipeline); tool-specific controls as in parameters",
        "adaptation": None, "metric_implementation": "Spreadsheet formulas over TP, FN, TN and FP (Table S9); MCC from the binary confusion matrix",
        "aggregation": "Sum over tissue sets", "budget": None,
    }, f"Table S9 row {r} ('{label}')", missing={"comparison.adaptation": {"reason": "inapplicable", "note": "No model training or tuning on the truth set"}})
    for col, (metric, direction, unit, unit_detail) in METRICS.items():
        raw, formula, style = s9[f"{col}{r}"]
        printed = shortest(raw)
        rv = extraction_review(["deterministic-table-parse"], METHOD_NOTE, XLSX_SHA, XLSX_URL)
        rv["note"] = ("Extracted, not reviewed. Formula in the cell: " + (formula or "none (typed value)") +
                      ". The review-evidence pass must re-check this cell against the pinned artifact.")
        b.result(b.rid("result", key, metric), f"{label} {metric} (Silverstein et al. Table S9)", SRC_X, SRCS, ev, printed,
                 metric, direction, unit, f"Table S9 (sheet 'Table S9') cell {col}{r}, row '{label}', column '{HEAD['ABCDEFGHIJ'.index(col)]}'",
                 rv, qualifier=QUAL, unit_detail=unit_detail,
                 extra={"raw_xml_value": raw, "workbook_number_format": "General"})

# Descriptive claim ---------------------------------------------------------------------------------------------
b.claim(b.rid("claim", "known-diagnoses-detected"), "Silverstein et al.: tools detected 28 of 68 known diagnoses",
        "Across splicing, expression and allelic-imbalance tools, 28 of 68 known diagnoses with RNA events were detected.",
        DATA, SRCS, {"field": "known_diagnoses_detected", "value": "28 of 68 known diagnoses with aberrant RNA events (41%) detected across all tool analyses; splicing tools 24 of 68; allelic imbalance found 4 not found by other tools",
                     "source_locator": "Abstract Results; Results 'Poor predictive performance across tools' paragraph 1; Discussion paragraph 2; Results 'Recall rate of allelic imbalance highlights ANEVA-H' paragraph 1"}, source_id=SRC_A)

# Use-case judgements ---------------------------------------------------------------------------------------------
GROUP, TITLE = "silverstein2026-neuromuscular", "RNA-seq tools on known diagnoses and true-negative samples, neuromuscular patient RNA-seq (Silverstein et al. 2026)"
RATIONALE = {
    "splicing": "Direct: patient muscle and fibroblast RNA-seq, several splicing callers on the same diagnosed samples, scored on recovery of known pathogenic splicing events and on outlier calls in true-negative samples; it is known-event recovery, not diagnostic yield.",
    "expression": "Proxy: expression-outlier recovery of known loss-of-function genes in the same patient RNA-seq, which supports but does not identify splice-altering variants.",
    "allelic-imbalance": "Proxy: allelic-imbalance recovery of known monoallelic loss-of-function genes in patient muscle RNA-seq with matched DNA variants; a complementary RNA signal, not splicing detection.",
}
ENDPOINT = {
    "splicing": "Per-tool TP, FN, TN and FP counts with accuracy, precision, recall, F1 and MCC for rMATS-turbo, MINTIE, FRASER, FRASER2.0 and LeafcutterMD on known pathogenic splicing events and true-negative samples",
    "expression": "TP, FN, TN and FP counts with accuracy, precision, recall, F1 and MCC for OUTRIDER with and without 100 GTEx controls",
    "allelic-imbalance": "TP, FN, TN and FP counts with accuracy, precision, recall, F1 and MCC for ANEVA-H and the DROP MAE module",
}
links = []
for key, p in PROTOCOLS.items():
    cid, _ = judgement(b, UC, UC_NAME, PROT_ID[key], p["name"], SRCS,
                       [{"source_id": SRC_X, "locator": p["locator"].split(";")[0]}, {"source_id": SRC_A, "locator": p["locator"].split(";", 1)[1].strip()}],
                       p["relevance"], ENDPOINT[key], RATIONALE[key],
                       ["Inspect every linked evaluation's source locator and population before citing a result.",
                        "Do not combine this mapping's evaluations with any other protocol's results; truth sets, inputs and metrics differ between sources.",
                        "Compare tools only where their populations match; Table S9 denominators differ by tool."],
                       p["limits"] + COMMON_LIMITS + ["Preprint (medRxiv v1), not peer reviewed."] + ([S7_CONFLICT] if key == "expression" else []),
                       p["headline"], GROUP, TITLE, p["stratum"], p["order"],
                       "Recorded from the 2026-10-11 use-case literature pass (data/omics/use-case-coverage-rna-splicing-20261011-silverstein2026); pending independent review.")
    if key != "expression":  # review correction 1: the expression judgement is held, so no assessed_by link
        links.append({"use_case": UC, "relation": "assessed_by", "target_id": PROT_ID[key], "judgement_claim": cid})

import json
# review correction 1: the expression judgement, both OUTRIDER evaluations and their 18 results stay needs_review
HELD = [PROT_ID["expression"].replace(P + "-protocol-", "use-case-mapping-" + P + "-")] + [
    r["id"] for r in b.records if r["id"] in (P + "-eval-outrider", P + "-eval-outrider-plus-gtex")
    or (r["kind"] == "result" and r["links"][0]["target_id"] in (P + "-eval-outrider", P + "-eval-outrider-plus-gtex"))]
assert len(HELD) == 21, len(HELD)
finalize_review(b, {
    "use-case-mapping-" + P + "-splicing": [P + "-eval-" + k for k in ("fraser", "fraser2-0", "leafcuttermd", "mintie", "rmats")],
    "use-case-mapping-" + P + "-allelic-imbalance": [P + "-eval-aneva-h", P + "-eval-mae"],
}, held=HELD, held_reason="Table S7 true-negative rows conflict with Table S9 rows 7 and 8 for OUTRIDER and OUTRIDER + GTEx.")
counts = b.write({"use-case-links.json": json.dumps({"note": "Proposed assessed_by links to add to the use_case record after the judgement claims are reviewed. Not applied by the extractor.", "links": links}, indent=1) + "\n"})
refresh_coverage(OUT)
print(json.dumps(counts))
