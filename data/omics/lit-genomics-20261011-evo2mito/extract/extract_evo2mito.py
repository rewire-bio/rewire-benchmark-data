"""Mathur and Sachidanandam, bioRxiv 10.64898/2026.03.10.710786 v1: Table 2, Evo2 versus mitochondrial variant-effect predictors.

Usage: python3 -I extract_evo2mito.py <paper.pdf> <pdftotext -layout output> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256

pdf, txt, folder = sys.argv[1:4]
SHA = sha256(pdf)
assert SHA == "8fe2977a11335823be19474b350b65d6d436c7674e92e96f81c9086df0dacf7d", SHA
URL = "https://www.biorxiv.org/content/10.64898/2026.03.10.710786v1.full.pdf"
lines = open(txt).read().split("\n")

b = Batch(folder, "lit-genomics-20261011-evo2mito", contexts=("research",))
SRC = b.source("lit-genomics-20261011-evo2mito-source-mathur2026", "Benchmarking DNA Foundation Models: Biological Blind Spots in Evo2 Variant-Effect Prediction", {
    "url": "https://doi.org/10.64898/2026.03.10.710786", "artifact_url": URL, "version": "bioRxiv preprint version 1, posted 2026-03-11",
    "retrieved_at": "2026-10-11T00:44:59Z", "artifact_sha256": SHA, "doi": "10.64898/2026.03.10.710786", "publication_status": "preprint",
    "licence": "CC-BY-4.0", "media_type": "application/pdf",
    "limitations": ["Preprint, not peer reviewed.", "The Evo2 checkpoint (size) used is not stated.",
                    "Comparator rows of Table 2 reproduce APOGEE 2 (Bianco et al. 2023, Nat Commun 14:5058) cross-validation results on a missense-only set (140 pathogenic, 1,734 neutral). They were not measured on this paper's test split and are not extracted; only the Evo2 row is recorded."],
    "evidence_concerns": [{"source_id": "lit-genomics-20261011-evo2mito-source-mathur2026",
                           "message": "Comparator rows reproduce APOGEE 2 (Bianco et al. 2023) cross-validation results on a missense-only set (140 pathogenic, 1,734 neutral). They were not measured on this paper's test split, so Table 2 does not compare like with like. Separately, Table 2 sensitivity/specificity 0.867/0.825 (balanced accuracy 0.846) versus Figure 2B and text 90.2%/85.0% (87.6%); the source does not explain the difference.",
                           "source_locator": "Section 3 Methods (comparison paragraph, reference 27); Table 2; Figure 2B legend; Section 4.3.1",
                           "artifact_sha256": SHA, "review_date": "2026-10-11"}]})
SIDS = [SRC]

s = next(i for i, l in enumerate(lines) if "Table 2: Comparison of Evo2" in l)
hdr = next(i for i in range(s, s + 10) if lines[i].strip().startswith("Method"))
cols = ["MCC", "Precision", "auPRC", "auROC", "Accuracy", "Balanced Acc.", "Sensitivity", "Specificity"]
assert re.split(r"\s{2,}", lines[hdr].strip()) == ["Method"] + cols, lines[hdr]
rows = []
for l in lines[hdr + 1:hdr + 12]:
    m = re.match(r"^\s*(.+?)\s{2,}((?:\d\.\d{3}\s+){7}\d\.\d{3})\s*$", l)
    if m:
        rows.append((m.group(1).strip(), m.group(2).split()))
assert [r[0] for r in rows] == ["Evo2 (Youden)", "APOGEE 2", "APOGEE 1", "COVEC WMV", "CAROL", "MetaSNP", "Condel", "MToolBox DS"], rows

data = b.entity("dataset", b.rid("data", "mtdna-test-split"), "Mitochondrial variant test split, MITOMAP pathogenic and ClinGen/ClinVar benign (Mathur and Sachidanandam 2026)",
                "130 confirmed disease-causing MITOMAP variants and 623 high-confidence benign variants (ClinGen frequency data and ClinVar), all variant types; split 70% calibration and 30% test.",
                SIDS, {"positives": 130, "negatives": 623, "split": "30% test set; threshold chosen by Youden index on the 70% calibration set",
                       "population": "Human mtDNA variants of all types (substitutions, insertions, deletions, multi-base)", "source_locator": "Section 3.1 'Mitochondrial Variant Dataset'; Methods threshold paragraph",
                       "missing_metadata": {"version": {"reason": "unreported", "note": "Database release dates not stated"}}})
proto = b.entity("protocol", b.rid("protocol", "mtdna-pathogenicity"), "Mitochondrial variant pathogenicity classification (Mathur and Sachidanandam 2026 Table 2)",
                 "Binary pathogenic versus benign classification of mtDNA variants.", SIDS,
                 {"protocol": "Evo2 zero-shot score: change in mean log-likelihood between alternate and reference windows; threshold by Youden index on the calibration set and applied to the test set.",
                  "version": "As published", "metric": "matthews-correlation-coefficient", "metric_direction": "higher", "unit": "unitless",
                  "limitations": ["Table 2 comparator rows reproduce APOGEE 2 cross-validation results on a different, missense-only variant set; they are not on this protocol and are not extracted.", "Table 2 and Figure 2B disagree on Evo2 sensitivity and specificity (see source evidence_concerns).", "Evo2 checkpoint not stated.", "Single split; no uncertainty printed."],
                  "source_locator": "Section 3 Methods; Table 2"}, links=[{"relation": "uses_data", "target_id": data}])

FAM = {"Condel": "brca-20261009-method-condel", "Evo2 (Youden)": "discovery-model-evo-2"}
DESC = {"APOGEE 2": "APOGEE 2 machine-learning predictor of mitochondrial missense variant pathogenicity.", "APOGEE 1": "APOGEE (first version) mitochondrial missense pathogenicity predictor.",
        "COVEC WMV": "COVEC weighted majority vote consensus predictor.", "CAROL": "CAROL consensus missense pathogenicity predictor.",
        "MetaSNP": "Meta-SNP consensus missense predictor.", "MToolBox DS": "MToolBox disease score for mitochondrial variants."}
METRIC = {"MCC": "matthews-correlation-coefficient", "Precision": "precision", "auPRC": "auprc", "auROC": "auroc", "Accuracy": "accuracy",
          "Balanced Acc.": "balanced-accuracy", "Sensitivity": "recall", "Specificity": "specificity"}
REV = extraction_review(["pdf-text-parse"], "Parsed the pdftotext -layout text of Table 2 (PDF page 10) with tools/extract_evo2mito.py; header and the eight row labels asserted.", SHA, URL)
# Comparator rows are quoted from the APOGEE 2 paper on a different variant set (review 2026-10-11); only the Evo2 row is recorded.
rows = [r for r in rows if r[0] == "Evo2 (Youden)"]
for label, vals in rows:
    fam = FAM.get(label)
    if not fam:
        fam = b.entity("method", b.rid("method", label), label, DESC[label], SIDS,
                       {"reported_name": label, "entity_level": "method", "source_locator": "Table 2 row label",
                        "missing_metadata": {"version": {"reason": "unreported"}}}, method_types=["supervised_machine_learning"])
    evo = label.startswith("Evo2")
    cfg = b.entity("configuration", b.rid("config", label), f"{label} (Mathur and Sachidanandam 2026)", f"{label} as reported in Table 2.", SIDS,
                   {"reported_name": label, "foundation_model_eligible": evo,
                    "parameters": "Zero-shot; mean log-likelihood difference, Youden threshold from the calibration set" if evo else "As reported in Table 2; settings not stated",
                    "access_reuse": "Public model weights" if evo else "Not stated in the source",
                    "source_locator": "Table 2 row label; Section 3 Methods", "missing_metadata": {"version": {"reason": "unreported", "note": "Evo2 checkpoint size not stated" if evo else "Predictor version not stated"}}},
                   method_types=["foundation_model"] if evo else ["supervised_machine_learning"], links=[{"relation": "configuration_of", "target_id": fam}])
    ev = b.evaluation(b.rid("eval", label), f"{label} on mtDNA pathogenicity test split", SIDS, cfg, proto, data,
                      "independent_paper" if evo else "unreported",
                      {"protocol_id": proto, "dataset_version": None, "split": "30% test set" if evo else None, "population": "mtDNA variants, MITOMAP pathogenic and ClinGen/ClinVar benign" if evo else None,
                       "inputs": "mtDNA sequence windows" if evo else None, "adaptation": "Zero-shot with calibrated threshold" if evo else None,
                       "metric_implementation": None, "aggregation": None, "budget": None}, f"Table 2 row '{label}'")
    for c, v in zip(cols, vals):
        loc = f"Table 2 (PDF page 10), row '{label}', column '{c}'"
        b.result(b.rid("result", label, c), f"{label} {c}", SRC, SIDS, ev, v, METRIC[c], "higher", "unitless" if c in ("MCC", "auPRC", "auROC") else "fraction", loc, REV,
                 qualifier="Youden threshold from calibration set" if evo and c not in ("auPRC", "auROC") else None)
print(json.dumps(b.write()))
