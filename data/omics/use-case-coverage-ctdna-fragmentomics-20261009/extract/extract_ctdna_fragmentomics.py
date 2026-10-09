"""Deterministic extraction of plasma cfDNA fragmentomics comparison tables into a records batch.

Usage: python3 -I extract_ctdna_fragmentomics.py <download-dir> <batch-dir>

Reads the pinned tables and asserts every row and column label it depends on:
  - Hou et al. 2024 (Adv Sci) article Table 1 (JATS XML, all cells)
  - Hou et al. 2024 Supporting Information workbook, sheets S2 and S3 (all cells)
  - Wang et al. 2026 (Sci Adv, UNITE) Data file S2, sheets STATS_xgb_x1-x6 and STATS_lr (all cells)
Writes batch.jsonl and claims.csv in the store form (single-meaning relations, declared attributes).
printed_value is the number as printed: the leading number of a text cell (the full cell text is kept
in printed_source_cell or raw_xml_value) or the shortest round-trip decimal of a General-format cell.
"""
import csv, hashlib, json, os, re, sys
import xml.etree.ElementTree as ET
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
P = "ctdnafrag-20261009"
UC = "use-case-plasma-ctdna-fragmentomics"
DATE = "2026-10-09"
CLIN = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
DELFI_DATA = "amp-20261007-ctdna-fragmentomics-dataset"
records, claim_rows = [], []


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": CLIN if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def shortest(raw):
    s = repr(float(raw))
    if s.endswith(".0"):
        s = s[:-2]
    if "e" in s or "E" in s:
        s = format(Decimal(s), "f")
    return s


def expect(got, value, where):
    if got != value:
        raise SystemExit(f"{where}: expected {value!r}, found {got!r}")


# ---------------------------------------------------------------- sources
def source(id_, name, url, artifact_url, version, retrieved_at, path, doi, status, licence, media_type, extra=None):
    attrs = {"url": url, "artifact_url": artifact_url, "version": version, "retrieved_at": retrieved_at,
             "artifact_sha256": sha(path), "doi": doi, "publication_status": status, "licence": licence,
             "media_type": media_type, "source_locator": "Full artifact bytes; per-result locators on each result"}
    attrs.update(extra or {})
    rec(id_, "source", name, "Primary source retrieved and hashed for the plasma ctDNA fragmentomics use-case pass.",
        [], attributes=attrs)


S_HOU = f"{P}-source-hou2024"
S_HOU_T = f"{P}-source-hou2024-supporting-information"
S_UNI = f"{P}-source-wang2026"
S_UNI_T = f"{P}-source-wang2026-data-file-s2"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
HOU_XML = f"{DL}/hou2024/PMC11321639.xml"
HOU_X = f"{DL}/hou2024-supp/s001.xlsx"
UNI_XML = f"{DL}/unite/PMC13353424.xml"
UNI_ZIP = f"{DL}/unite-supp/sciadv.ady9432_data_files_s1_and_s2.zip"
UNI_X = f"{DL}/unite-supp/x/ady9432_data_file_s2.xlsx"

source(S_HOU, "Systematically Evaluating Cell-Free DNA Fragmentation Patterns for Cancer Diagnosis and Enhanced Cancer Detection via Integrating Multiple Fragmentation Patterns",
       "https://doi.org/10.1002/advs.202308243", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11321639/fullTextXML",
       "Advanced Science 11(30):e2308243, published 2024-06-17; PMC11321639 full-text XML", "2026-10-09T20:27:02Z",
       HOU_XML, "10.1002/advs.202308243", "peer_reviewed", "CC-BY-4.0", "application/xml",
       {"archive_sha256": sha(f"{BATCH}/artifacts/hou2024-article.xml.gz"),
        "archive_note": "gzip -n -9 copy of the exact bytes in artifacts/hou2024-article.xml.gz (CC BY 4.0)"})
source(S_HOU_T, "Hou et al. 2024, Supporting Information workbook (Tables S1-S15)",
       "https://doi.org/10.1002/advs.202308243", "https://pmc-oa-opendata.s3.amazonaws.com/PMC11321639.1/ADVS-11-2308243-s001.xlsx",
       "ADVS-11-2308243-s001.xlsx, PMC open-access copy PMC11321639.1", "2026-10-09T20:20:39Z",
       HOU_X, "10.1002/advs.202308243", "peer_reviewed", "CC-BY-4.0", XLSX,
       {"archive_sha256": sha(f"{BATCH}/artifacts/hou2024-supporting-information.xlsx.gz"),
        "archive_note": "gzip -n -9 copy of the exact bytes in artifacts/hou2024-supporting-information.xlsx.gz (CC BY 4.0)",
        "evidence_concerns": [{
            "source_id": S_HOU_T,
            "message": ("Table S2 and Table S9 disagree on the sensitivity of the same SVM models on the same data. For every one of the "
                        "ten PANCAN patterns, the Table S9 SVM 'Sensitivity @95% specificity' equals the Table S2 'Sensitivity @85% "
                        "specificity' (for example length 0.6033 in S9 D3 and S2 E3; S2 D3 prints 0.5210), and the Table S9 SVM values "
                        "at 85% appear nowhere in Table S2. The AUC columns agree with each other and with article Table 1. SVM is "
                        "the stated primary classifier (Methods P41, Discussion P21). In Table S2 the LIHC rows print identical values "
                        "at 95% and 85% specificity for nine of ten patterns (D84:E92), and in Table S9 the WPS logistic-regression row "
                        "repeats the OCF logistic-regression row (C45:E45 equals C35:E35). Values are recorded as printed; which "
                        "sensitivity columns are correct is not resolved."),
            "source_locator": "Supporting Information sheet S2 C3:E92 versus sheet S9 C3:E52; S2 D84:E92; S9 rows 35 and 45",
            "artifact_sha256": sha(HOU_X),
            "reviewed_at": "2026-10-09T20:45:00Z",
            "review_method": "ai-assisted-source-review"}]})
source(S_UNI, "A scalable deep-learning framework for cancer detection using cell-free DNA shallow whole-genome sequencing",
       "https://doi.org/10.1126/sciadv.ady9432", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13353424/fullTextXML",
       "Science Advances 12(28):eady9432, published 2026-07-10; PMC13353424 full-text XML", "2026-10-09T20:27:02Z",
       UNI_XML, "10.1126/sciadv.ady9432", "peer_reviewed", "CC-BY-4.0", "application/xml",
       {"archive_sha256": sha(f"{BATCH}/artifacts/wang2026-article.xml.gz"),
        "archive_note": "gzip -n -9 copy of the exact bytes in artifacts/wang2026-article.xml.gz (CC BY 4.0)"})
source(S_UNI_T, "Wang et al. 2026, Data file S2 (model scores and summary statistics)",
       "https://doi.org/10.1126/sciadv.ady9432", "https://pmc-oa-opendata.s3.amazonaws.com/PMC13353424.1/sciadv.ady9432_data_files_s1_and_s2.zip",
       "ady9432_data_file_s2.xlsx inside sciadv.ady9432_data_files_s1_and_s2.zip, PMC open-access copy PMC13353424.1",
       "2026-10-09T20:23:13Z", UNI_ZIP, "10.1126/sciadv.ady9432", "peer_reviewed", "CC-BY-4.0", "application/zip",
       {"artifact_member": "ady9432_data_file_s2.xlsx",
        "hash_scope": f"artifact_sha256 is the zip as served; the member ady9432_data_file_s2.xlsx has SHA-256 {sha(UNI_X)}",
        "archive_note": "Not archived: the 7.1 MB zip is a stable PMC open-access object and is pinned by hash; archiving it would add bulk without new information."})


def review_note(path, url, how):
    return {"method": ["deterministic-table-parse"], "reviewer": ["claude"], "date": DATE,
            "reviewer_note": "Claude (Opus 5.5) extraction agent; extraction record, not an independent review",
            "artifact_sha256": sha(path), "retrieval_url": url,
            "note": how + " Pending independent review."}


def ci(lower, upper, printed_text, note=None):
    u = {"type": "confidence_interval", "lower": lower, "upper": upper, "level": 0.95, "printed": printed_text}
    if note:
        u["note"] = note
    return u


def result(id_, eval_id, source_ids, locator, pv, metric, qualifier, unit, review, uncertainty=None, extra=None):
    attrs = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": "higher", "unit": unit,
             "printed_value": pv, "numeric_value": format(Decimal(pv), "f"), "source_locator": locator, "review": review}
    if uncertainty:
        attrs["uncertainty"] = uncertainty
    else:
        attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
    attrs.update(extra or {})
    rec(id_, "result", f"{eval_id.replace(P + '-eval-', '')} {metric} ({qualifier})",
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        source_ids, [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claim_rows.append([id_, source_ids[-1], locator, pv, "result"])


def evaluation(id_, name, config, protocol, dataset, source_ids, origin, comparison, locator, limitations=None, missing=None):
    attrs = {"origin": origin, "protocol": protocol, "version": "Primary source as retrieved 2026-10-09",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    if limitations:
        attrs["limitations"] = limitations
    if missing:
        attrs["missing_metadata"] = missing
    rec(id_, "evaluation", name, "Published comparison; transcribed, not reproduced.", source_ids,
        [{"relation": "system", "target_id": config}, {"relation": "assessment", "target_id": protocol},
         {"relation": "data", "target_id": dataset}], attrs)


def method(key, name, description, source_ids, mtypes, locator):
    rec(f"{P}-method-{key}", "method", name, description, source_ids,
        attributes={"reported_name": name, "entity_level": "method", "source_locator": locator,
                    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
        facets={**CLIN, "method_types": list(mtypes)})
    return f"{P}-method-{key}"


def configuration(id_, name, method_id, source_ids, reported, locator, mtypes, extra=None, version=None, version_note=None):
    attrs = {"reported_name": reported, "foundation_model_eligible": False, "source_locator": locator}
    if version:
        attrs["version"] = version
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": version_note or "No version of this configuration is printed"}}
    attrs.update(extra or {})
    rec(id_, "configuration", name, "Configuration as run in the cited comparison.", source_ids,
        [{"relation": "configuration_of", "target_id": method_id}], attrs, facets={**CLIN, "method_types": list(mtypes)})


def claim(id_, subject, field, value, source_ids, locator, path, url):
    rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", source_ids,
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator,
         "review": {"method": ["transcription"], "reviewer": ["claude"], "date": DATE,
                    "reviewer_note": "Claude (Opus 5.5) extraction agent; extraction record, not an independent review",
                    "artifact_sha256": sha(path), "retrieval_url": url,
                    "note": "Hand transcription from the article text. Pending independent review."}},
        facets={})
    claim_rows.append([id_, source_ids[-1], locator, value, "claim"])


# ================================================================ Hou et al. 2024
HOU_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11321639/fullTextXML"
HOU_X_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC11321639.1/ADVS-11-2308243-s001.xlsx"
PATTERNS = {  # printed label: (key, name, description, reference as cited in Hou et al. P4)
    "length": ("fragment-length", "Fragment length distribution", "Proportions of fragments in 10 bp length intervals.", "ref 34"),
    "PFE": ("pfe", "Promoter fragmentation entropy (PFE)", "Shannon entropy of fragment length proportions per region.", "ref 54"),
    "FSR": ("fsr", "Fragment size ratio (FSR)", "Short, medium and long fragment proportions per region.", "ref 58"),
    "FSD": ("fsd", "Fragment size distribution (FSD)", "Fragment proportions in 5 bp length intervals per chromosome arm or chromosome.", "ref 58"),
    "coverage": ("fragment-coverage", "Fragment coverage (fragment midpoint counts)", "Number of fragment midpoints per region.", "ref 32"),
    "end": ("fragment-end-count", "Fragment endpoint counts", "Number of fragment endpoints per region (preferred end coordinates).", "ref 59"),
    "OCF": ("ocf", "Orientation-aware cell-free fragmentation (OCF)", "Difference in upstream and downstream fragment end counts around region centres.", "ref 32"),
    "IFS": ("ifs", "Integrated fragmentation score (IFS)", "Fragment count weighted by mean fragment length per region.", "ref 10"),
    "WPS": ("wps", "Windowed protection score (WPS)", "Nucleosome protection score from fully and partially spanning fragments in a 120 bp window.", "ref 44"),
    "EDM": ("end-motif", "Fragment 5' end motif (4-mer)", "Proportions of the 256 5' end 4-mers per chromosome.", "ref 42"),
    "DELFI": ("delfi", "DELFI fragmentation profile", "Short-to-long fragment ratios in 5 Mb bins (Cristiano et al. 2019).", "ref 45"),
}
HM = {k: method(v[0], v[1], v[2] + f" Defined in Hou et al. {v[3]}; the method record names the feature definition, not an implementation.",
                [S_HOU], ["specialist"], f"Hou et al. 2024 Introduction P4 and Experimental Section P29-P39 ({v[3]})")
      for k, v in PATTERNS.items()}

hou = ET.parse(HOU_XML).getroot()
tw = [t for t in hou.iter("table-wrap") if t.get("id") == "advs8741-tbl-0001"][0]
txt = lambda e: " ".join("".join(e.itertext()).split())
expect(txt(tw.find("caption")), "Comparison of cfDNA fragmentation patterns across various scenarios (AUC).", "Hou Table 1 caption")
rows = [[txt(c) for c in tr] for tr in tw.iter("tr")]
expect(rows[0], ["", "open chromatin region", "after PCA degradation", "definition as per the original publication"], "Hou Table 1 header")
t1_labels = ["length", "PFE", "FSR", "FSD", "coverage", "end", "OCF", "IFS", "WPS", "EDM", "DELFI"]
expect([r[0] for r in rows[1:]], t1_labels, "Hou Table 1 row labels")
CELL = re.compile(r"^(?:(?P<label>[a-z0-9 ]+?) )?(?P<v>[01]\.\d{4}) \((?P<lo>[01]\.\d{4})–(?P<hi>[01]\.\d{4})\)$")
SETTINGS = {1: ("open-chromatin", "open chromatin regions"), 2: ("pca", "open chromatin regions after PCA dimension reduction"),
            3: ("original", "region definition of the original publication")}

D = {}
D["jiang"] = f"{P}-data-hou2024-jiang2018-lihc"
D["zhou"] = f"{P}-data-hou2024-zhou2022-lihc"
D["lucas"] = f"{P}-data-hou2024-mathios2021-lucas"
D["mathios-ind"] = f"{P}-data-hou2024-mathios2021-independent"
DATA_LOC = "Hou et al. 2024 Experimental Section 'Cell-Free DNA Whole Genome Sequencing Data and Preprocessing' (P24-P25)"
for key, name, pop, total in (
        ("jiang", "Jiang et al. 2018 plasma WGS, 90 liver cancer and 135 non-cancer (as used by Hou et al. 2024)",
         "225 samples: 32 healthy, 67 hepatitis B, 36 cirrhosis and 90 liver cancer; fragment files from FinaleDB", 225),
        ("zhou", "Zhou et al. 2022 plasma WGS, 8 liver cancer and 8 healthy (as used by Hou et al. 2024)",
         "16 samples: 8 healthy and 8 liver cancer; fragment information from the original paper", 16),
        ("lucas", "Mathios et al. 2021 LUCAS cohort, 129 lung cancer and 158 non-cancer (as used by Hou et al. 2024)",
         "287 samples: 91 healthy, 67 benign and 129 lung cancer; BAM files from EGA EGAD00001007796", 287),
        ("mathios-ind", "Mathios et al. 2021 independent lung cohort, 46 lung cancer and 385 healthy (as used by Hou et al. 2024)",
         "431 samples: 385 healthy and 46 lung cancer; BAM files from EGA EGAD00001007796", 431)):
    rec(D[key], "dataset", name, "Plasma cfDNA whole-genome sequencing cohort reanalysed by Hou et al. 2024.", [S_HOU],
        attributes={"version": "As reanalysed by Hou et al. 2024 (GRCh37)", "population": pop, "total": total,
                    "assay": "Plasma cfDNA whole-genome sequencing", "source_locator": DATA_LOC})

PR = {}
PR["t1"] = f"{P}-protocol-hou2024-cristiano-pancan-cv-auc"
rec(PR["t1"], "protocol", "Hou et al. 2024 pan-cancer vs healthy, Cristiano cohort, 10 x 10-fold cross-validation (Table 1 AUC)",
    "One SVM per fragmentation pattern and feature setting on the DELFI 2019 cohort.", [S_HOU],
    [{"relation": "uses_data", "target_id": DELFI_DATA}],
    {"protocol": ("Compute each fragmentation pattern for every sample, train a support vector machine (scikit-learn defaults) per "
                  "pattern and feature setting to separate 208 cancer patients (seven types) from 215 healthy individuals, and "
                  "report ROC-AUC with 95% CI over 10 repeats of 10-fold cross-validation."),
     "version": "Hou et al. 2024 Table 1; Methods P41 and P44", "metric": "auroc", "metric_direction": "higher",
     "limitations": ["Internal cross-validation on one cohort (the DELFI 2019 cohort), not an independent validation.",
                     "AUC only; no sensitivity at a declared specificity in Table 1.",
                     "Fragment files taken from FinaleDB rather than the original BAM files."],
     "source_locator": "Article Table 1; Experimental Section P41, P44"})
PR["cris"] = f"{P}-protocol-hou2024-cristiano-cv-sensitivity"
PR["jiang"] = f"{P}-protocol-hou2024-jiang-lihc-cv-sensitivity"
PR["zhou"] = f"{P}-protocol-hou2024-zhou-lihc-independent"
PR["lucas"] = f"{P}-protocol-hou2024-mathios-lucas-independent"
PR["mathios-ind"] = f"{P}-protocol-hou2024-mathios-independent"
SENS_LIM = ["Supporting Information Table S2 sensitivity columns conflict with Table S9 for the same models (source evidence concern).",
            "Ten fragmentation patterns restricted to open chromatin regions, one SVM each; no tumour-fraction stratification."]
for key, name, data, proto, loc, extra_lim in (
        ("cris", "Hou et al. 2024 Cristiano cohort cross-validation, pan-cancer and seven cancer types (Table S2)", DELFI_DATA,
         "Pan-cancer and per-cancer-type SVMs against the 215 healthy individuals; 10 repeats of 10-fold cross-validation.",
         "Supporting Information Table S2 rows 3-82", ["Per-cancer-type groups are small (12 to 54 patients)."]),
        ("jiang", "Hou et al. 2024 Jiang cohort cross-validation, liver cancer (Table S2)", D["jiang"],
         "Liver cancer SVM; 10 repeats of 10-fold cross-validation.", "Supporting Information Table S2 rows 83-92",
         ["The control group for the LIHC model (healthy only or all non-cancer) is not stated in the table.",
          "Nine of ten rows print identical sensitivity at 95% and 85% specificity."]),
        ("zhou", "Hou et al. 2024 independent validation, Zhou et al. liver cancer cohort (Table S3)", D["zhou"],
         "SVM trained on all Jiang et al. samples, applied to the Zhou et al. cohort.", "Supporting Information Table S3 rows 3-12",
         ["Eight cancers and eight controls; each sensitivity step is 0.125."]),
        ("lucas", "Hou et al. 2024 independent validation, Mathios et al. LUCAS cohort (Table S3)", D["lucas"],
         "SVM trained on Cristiano et al. lung cancer samples and controls, applied to the LUCAS cohort.", "Supporting Information Table S3 rows 13-22",
         ["LUCAS includes 67 benign-nodule patients among the non-cancer group.", "Training set has 12 lung cancer patients."]),
        ("mathios-ind", "Hou et al. 2024 independent validation, Mathios et al. independent lung cohort (Table S3)", D["mathios-ind"],
         "SVM trained on Cristiano et al. lung cancer samples and controls, applied to the Mathios et al. independent cohort.",
         "Supporting Information Table S3 rows 23-32", ["Training set has 12 lung cancer patients."])):
    rec(PR[key], "protocol", name, "Fragmentation pattern comparison by Hou et al. 2024.", [S_HOU, S_HOU_T],
        [{"relation": "uses_data", "target_id": data}],
        {"protocol": proto + " Report ROC-AUC and sensitivity at 95% and at 85% specificity.",
         "version": "Hou et al. 2024 Supporting Information; Methods P41, P44, P45", "metric": "auroc", "metric_direction": "higher",
         "limitations": SENS_LIM + extra_lim, "source_locator": f"{loc}; Experimental Section P41, P44, P45"})

# configurations: one per pattern and feature setting
CFG = {}
for i, label in enumerate(t1_labels, start=1):
    for col, (skey, sname) in SETTINGS.items():
        cell = rows[i][col]
        if cell == "/":
            continue
        m = CELL.match(cell)
        if not m:
            raise SystemExit(f"Hou Table 1 unparsed cell {label} col {col}: {cell!r}")
        region = m.group("label") if col == 3 else None
        cid = f"{P}-config-hou2024-{PATTERNS[label][0]}-{skey}"
        CFG[(label, skey)] = cid
        configuration(cid, f"{PATTERNS[label][1]}, {sname}{' (' + region + ')' if region else ''}, SVM (Hou et al. 2024)",
                      HM[label], [S_HOU], label, f"Article Table 1 row '{label}', column '{rows[0][col]}'; Experimental Section P29-P41",
                      ["supervised_machine_learning"],
                      extra={"parameters": f"Feature setting: {sname}{'; region printed as ' + repr(region) if region else ''}. "
                                           "Classifier: scikit-learn support vector machine with default parameters.",
                             "source_label": label},
                      version_note="Hou et al. re-implementation; no software version or code commit is printed")

hou_t1_review = review_note(HOU_XML, HOU_URL, "Extracted by deterministic parse of the article JATS XML table-wrap advs8741-tbl-0001 "
                            "(extract/extract_ctdna_fragmentomics.py) with header and row labels asserted; the full cell text is in printed_source_cell.")
for i, label in enumerate(t1_labels, start=1):
    for col, (skey, sname) in SETTINGS.items():
        cell = rows[i][col]
        if cell == "/":
            continue
        m = CELL.match(cell)
        ev = f"{P}-eval-hou2024-t1-{PATTERNS[label][0]}-{skey}"
        evaluation(ev, f"{label} ({sname}), pan-cancer vs healthy AUC", CFG[(label, skey)], PR["t1"], DELFI_DATA, [S_HOU],
                   "independent_paper",
                   {"dataset_version": "Cristiano et al. 2019 cohort, fragment files from FinaleDB", "split": "10 repeats of 10-fold cross-validation",
                    "population": "208 cancer patients (seven types) vs 215 healthy individuals", "inputs": f"{label} features, {sname}",
                    "adaptation": "SVM trained per fold", "metric_implementation": None, "aggregation": "Mean over repeats with 95% CI", "budget": None},
                   f"Article Table 1 row '{label}', column '{rows[0][col]}'",
                   limitations=["Feature definition from an earlier publication, re-implemented by Hou et al.; not the original authors' code."],
                   missing={"comparison.metric_implementation": {"reason": "unreported"}})
        result(f"{P}-result-hou2024-t1-{PATTERNS[label][0]}-{skey}-auroc", ev, [S_HOU],
               f"Article Table 1 (advs8741-tbl-0001), row '{label}', column '{rows[0][col]}'",
               m.group("v"), "auroc", "pan-cancer vs healthy; mean of 10 x 10-fold cross-validation", "unitless", hou_t1_review,
               ci(m.group("lo"), m.group("hi"), f"{m.group('lo')}–{m.group('hi')}"),
               extra={"printed_source_cell": cell})

claim(f"{P}-claim-hou2024-classifier", PR["t1"], "metric_implementation",
      "Models were built with scikit-learn support vector machines with default parameters (XGBoost from the xgboost library for the comparison models); evaluation used 10 repeats of 10-fold cross-validation, with AUC and sensitivity at 95% and 85% specificity as the primary metrics.",
      [S_HOU], "Experimental Section 'Classification Model Construction' (P41) and 'Classification Model Evaluation' (P44-P45)", HOU_XML, HOU_URL)

# Supporting Information S2 and S3
hx = rawxlsx.read(HOU_X)
s2, s3 = hx["S2"], hx["S3"]
expect(s2["A1"], "Table S2. Performance of the fragmentation patterns (within the open chromatin regions) on the datasets of Cristiano et al. and Jiang et al.", "S2 A1")
expect(s3["A1"], "Table S3. Performance of the fragmentation patterns (within the open chromatin regions) on the datasets of Zhou et al. and Mathios et al.", "S3 A1")
HDR = ["AUC", "Sensitivity @95% specificity", "Sensitivity @85% specificity"]
for sh, first, name in ((s2, "Cancer type", "S2"), (s3, "Data set", "S3")):
    expect([sh["A2"], sh["B2"], sh["C2"], sh["D2"], sh["E2"]], [first, "Fragmentation pattern"] + HDR, f"{name} header")
pat10 = t1_labels[:10]
groups2 = ["PANCAN", "BRCA", "CHOL", "CRC", "STAD", "NSCLC", "OV", "PAAD", "LIHC"]
for g, grp in enumerate(groups2):
    r0 = 3 + 10 * g
    expect(s2[f"A{r0}"], grp, f"S2 A{r0}")
    for k, lab in enumerate(pat10):
        expect(s2[f"B{r0 + k}"], lab, f"S2 B{r0 + k}")
        if k and f"A{r0 + k}" in s2:
            raise SystemExit(f"S2 A{r0 + k} unexpectedly filled")
if len(s2) != 1 + 5 + 90 * 4 + 9 or "A93" in s2 or "B93" in s2:
    raise SystemExit(f"Unexpected S2 extent: {len(s2)} cells")
groups3 = ["Zhou et al. dataset (LIHC)", "Mathios et al. LUCAS dataset (LUNG)", "Mathios et al. independent dataset (LUNG)"]
for g, grp in enumerate(groups3):
    for k, lab in enumerate(pat10):
        r = 3 + 10 * g + k
        expect(s3[f"A{r}"], grp, f"S3 A{r}")
        expect(s3[f"B{r}"], lab, f"S3 B{r}")
if len(s3) != 1 + 5 + 30 * 5 or "A33" in s3:
    raise SystemExit(f"Unexpected S3 extent: {len(s3)} cells")

S2CELL = re.compile(r"^\s*(?P<v>[01]\.\d{4}) \(95 CI: (?P<lo>[01]\.\d{4}) - (?P<hi>[01]\.\d{4})\)?$")
METRIC = {"C": ("auroc", "unitless", "AUC"), "D": ("sensitivity-at-95-percent-specificity", "fraction", "Sensitivity @95% specificity"),
          "E": ("sensitivity-at-85-percent-specificity", "fraction", "Sensitivity @85% specificity")}
GROUP_NAME = {"PANCAN": "pan-cancer", "BRCA": "breast cancer", "CHOL": "cholangiocarcinoma", "CRC": "colorectal cancer",
              "STAD": "gastric cancer", "NSCLC": "lung cancer", "OV": "ovarian cancer", "PAAD": "pancreatic cancer", "LIHC": "liver cancer"}
CRIS_N = {"PANCAN": 208, "BRCA": 54, "CHOL": 26, "CRC": 27, "STAD": 27, "NSCLC": 12, "OV": 28, "PAAD": 34}
s2_review = review_note(HOU_X, HOU_X_URL, "Extracted by deterministic parse of the pinned XLSX cell XML (extract/rawxlsx.py) with sheet "
                        "title, header and row labels asserted. Text cells hold the value and its 95% CI; printed_value is the leading "
                        "number and raw_xml_value the full stored text.")
s3_review = review_note(HOU_X, HOU_X_URL, "Extracted by deterministic parse of the pinned XLSX cell XML (extract/rawxlsx.py) with sheet "
                        "title, header and row labels asserted. Numeric General-format cells; printed_value is the shortest "
                        "round-trip decimal of the stored value and raw_xml_value the stored text.")
for lab in pat10:
    cfg = CFG[(lab, "open-chromatin")]
    k = pat10.index(lab)
    # S2: Cristiano (eight groups) and Jiang (LIHC)
    ev_c = f"{P}-eval-hou2024-s2-{PATTERNS[lab][0]}-cristiano"
    evaluation(ev_c, f"{lab} (open chromatin), Cristiano cohort cross-validation", cfg, PR["cris"], DELFI_DATA, [S_HOU, S_HOU_T],
               "independent_paper",
               {"dataset_version": "Cristiano et al. 2019 cohort, fragment files from FinaleDB", "split": "10 repeats of 10-fold cross-validation",
                "population": "Pan-cancer (208) and each of seven cancer types vs 215 healthy individuals", "inputs": f"{lab} features in open chromatin regions",
                "adaptation": "SVM trained per fold and per comparison", "metric_implementation": None, "aggregation": "Mean with 95% CI", "budget": None},
               f"Supporting Information Table S2, row '{lab}' in each of groups PANCAN to PAAD",
               missing={"comparison.metric_implementation": {"reason": "unreported"}})
    ev_j = f"{P}-eval-hou2024-s2-{PATTERNS[lab][0]}-jiang-lihc"
    evaluation(ev_j, f"{lab} (open chromatin), Jiang cohort liver cancer cross-validation", cfg, PR["jiang"], D["jiang"], [S_HOU, S_HOU_T],
               "independent_paper",
               {"dataset_version": "Jiang et al. 2018 cohort, fragment files from FinaleDB", "split": "10 repeats of 10-fold cross-validation",
                "population": "90 liver cancer patients vs non-cancer controls of the Jiang et al. cohort", "inputs": f"{lab} features in open chromatin regions",
                "adaptation": "SVM trained per fold", "metric_implementation": None, "aggregation": "Mean with 95% CI", "budget": None},
               f"Supporting Information Table S2, row {83 + k}",
               missing={"comparison.metric_implementation": {"reason": "unreported"}})
    for g, grp in enumerate(groups2):
        r = 3 + 10 * g + k
        for col, (metric, unit, head) in METRIC.items():
            raw = s2[f"{col}{r}"]
            m = S2CELL.match(raw)
            if not m:
                raise SystemExit(f"S2 {col}{r} unparsed: {raw!r}")
            ev = ev_j if grp == "LIHC" else ev_c
            qual = (f"{GROUP_NAME[grp]} vs healthy; mean of 10 x 10-fold cross-validation" if grp != "LIHC"
                    else "liver cancer vs controls; mean of 10 x 10-fold cross-validation")
            extra = {"raw_xml_value": raw}
            if grp in CRIS_N:
                extra["denominator_note"] = f"{CRIS_N[grp]} cancer patients and 215 healthy individuals (article P24)"
            if grp == "LIHC" and col in "DE" and lab != "length":
                extra["source_anomaly"] = "Sensitivity at 95% and at 85% specificity are printed identical in this row (and in eight other LIHC rows)."
            note = "Closing bracket missing in the printed cell." if not raw.rstrip().endswith(")") else None
            result(f"{P}-result-hou2024-s2-{PATTERNS[lab][0]}-{grp.lower()}-{metric.replace('sensitivity-at-', 'sens').replace('-percent-specificity', '')}",
                   ev, [S_HOU, S_HOU_T], f"Supporting Information sheet S2, {col}{r}; group '{grp}'; row '{lab}'; column '{head}'",
                   m.group("v"), metric, qual, unit, s2_review, ci(m.group("lo"), m.group("hi"), f"95 CI: {m.group('lo')} - {m.group('hi')}", note),
                   extra=extra)
    # S3: three independent validations
    for g, (dkey, grp) in enumerate(zip(("zhou", "lucas", "mathios-ind"), groups3)):
        r = 3 + 10 * g + k
        ev = f"{P}-eval-hou2024-s3-{PATTERNS[lab][0]}-{dkey}"
        evaluation(ev, f"{lab} (open chromatin), independent validation on {grp}", cfg, PR[dkey], D[dkey], [S_HOU, S_HOU_T], "independent_paper",
                   {"dataset_version": D[dkey], "split": "Independent validation (trained on another cohort)",
                    "population": {"zhou": "8 liver cancer vs 8 healthy", "lucas": "129 lung cancer vs 158 non-cancer (91 healthy, 67 benign)",
                                   "mathios-ind": "46 lung cancer vs 385 healthy"}[dkey],
                    "inputs": f"{lab} features in open chromatin regions", "adaptation": "SVM trained on the training cohort, applied unchanged",
                    "metric_implementation": None, "aggregation": "Single validation run; no interval printed", "budget": None},
                   f"Supporting Information Table S3, row {r}", missing={"comparison.metric_implementation": {"reason": "unreported"}})
        for col, (metric, unit, head) in METRIC.items():
            raw = s3[f"{col}{r}"]
            qual = {"zhou": "liver cancer vs healthy; independent validation",
                    "lucas": "lung cancer vs non-cancer; independent validation",
                    "mathios-ind": "lung cancer vs healthy; independent validation"}[dkey]
            result(f"{P}-result-hou2024-s3-{PATTERNS[lab][0]}-{dkey}-{metric.replace('sensitivity-at-', 'sens').replace('-percent-specificity', '')}",
                   ev, [S_HOU, S_HOU_T], f"Supporting Information sheet S3, {col}{r}; data set '{grp}'; row '{lab}'; column '{head}'",
                   shortest(raw), metric, qual, unit, s3_review, extra={"raw_xml_value": raw})

# ================================================================ Wang et al. 2026 (UNITE), Data file S2
UNI_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC13353424.1/sciadv.ady9432_data_files_s1_and_s2.zip"
ux = rawxlsx.read(UNI_X)
toc = ux["Table of Contents"]
expect(toc["A2"], "STATS_lr", "UNITE TOC A2"); expect(toc["B2"], "Summary stats of ichorCNA-TF models trained in different TF categories", "UNITE TOC B2")
expect(toc["A4"], "STATS_xgb_x1-x6", "UNITE TOC A4"); expect(toc["B4"], "summary stats of XGBoost models during cross-validation (5-fold CV, 10 repeats)", "UNITE TOC B4")
STAT_HDR = ["ichorcna_strat", "feat", ".metric", "mean", "median", "sd", "ci_95_lower", "ci_95_upper", "sem_lower", "sem_upper"]
COLS = "ABCDEFGHIJ"
STRATA = {"[0, 0.03]": ("tf-0-3pct", "ichorCNA tumour fraction 0 to 0.03", 1),
          "(0.03, 0.1]": ("tf-3-10pct", "ichorCNA tumour fraction above 0.03 to 0.1", 2),
          "(0.1, 1]": ("tf-over-10pct", "ichorCNA tumour fraction above 0.1", 3),
          "all": ("tf-all", "all tumour fractions", 4)}
FOLD = "mean of 50 outer test folds (5-fold cross-validation, 10 repeats)"
XM = {"AUROC": ("auroc", "unitless", FOLD), "AUPRC": ("auprc", "unitless", FOLD),
      "Sensitivity": ("recall", "fraction", "default classification threshold; " + FOLD),
      "Specificity": ("specificity", "fraction", "default classification threshold; " + FOLD),
      "F1": ("f1-score", "fraction", "default classification threshold; " + FOLD),
      "Accuracy": ("accuracy", "fraction", "default classification threshold; " + FOLD)}
LM = {"test_auroc": XM["AUROC"], "test_auprc": XM["AUPRC"], "test_sensitivity": XM["Sensitivity"], "test_specificity": XM["Specificity"],
      "test_f1": XM["F1"], "test_acc": XM["Accuracy"], "test_ppv": ("precision", "fraction", "default classification threshold; " + FOLD),
      "test_sen_95spe": ("sensitivity-at-95-percent-specificity", "fraction", FOLD),
      "test_sen_98spe": ("sensitivity-at-98-percent-specificity", "fraction", FOLD),
      "test_sen_99spe": ("sensitivity-at-99-percent-specificity", "fraction", FOLD),
      "test_acc_95spe": ("accuracy", "fraction", "threshold giving 95% specificity; " + FOLD),
      "test_acc_98spe": ("accuracy", "fraction", "threshold giving 98% specificity; " + FOLD),
      "test_acc_99spe": ("accuracy", "fraction", "threshold giving 99% specificity; " + FOLD),
      "test_f1_95spe": ("f1-score", "fraction", "threshold giving 95% specificity; " + FOLD),
      "test_f1_98spe": ("f1-score", "fraction", "threshold giving 98% specificity; " + FOLD),
      "test_f1_99spe": ("f1-score", "fraction", "threshold giving 99% specificity; " + FOLD)}
FEATS = {"All": ("all", "All five feature types (UNITE-XGB, model X6)"), "Length": ("len", "Fragment length (Len)"),
         "SD": ("sd", "SD of fragment length counts across 5 Mb bins (SD)"), "CNV": ("cna", "Copy number aberration (CNA)"),
         "C/T": ("ct", "5' C/T motif ratio per bin (C/T)"), "S/L": ("sl", "Short/long fragment length ratio per bin (S/L)")}

M_UNI = method("unite-xgb", "UNITE fragmentomic feature framework (XGBoost)",
               "XGBoost cancer-vs-healthy classifiers on shallow WGS fragmentomic features (fragment length, SD of length counts, short/long ratio, C/T end-motif ratio, copy number) computed per 5 Mb bin.",
               [S_UNI], ["supervised_machine_learning"], "Wang et al. 2026 Introduction P5; Methods 'UNITE-XGB and DELFI-XGB models training and testing' (P49)")
M_ICHOR = method("ichorcna", "ichorCNA", "Copy-number-based tumour fraction estimation from ultra-low-pass WGS (Adalsteinsson et al. 2017).",
                 [S_UNI], ["conventional_pipeline"], "Wang et al. 2026 Results P17; Methods P40, P47 (ref 58)")
UCFG = {}
for f, (fk, fname) in FEATS.items():
    UCFG[f] = f"{P}-config-wang2026-unite-xgb-{fk}"
    configuration(UCFG[f], f"UNITE XGBoost, {fname} (Wang et al. 2026)", M_UNI, [S_UNI, S_UNI_T], f,
                  "Data file S2 sheet STATS_xgb_x1-x6 column 'feat'; Methods P49", ["supervised_machine_learning"],
                  extra={"parameters": f"Features: {fname}. XGBoost with nested cross-validation (StratifiedGroupKFold, randomized grid search); keras v3.3.3 and scikit-learn v1.4.2.",
                         "source_label": f},
                  version_note="No UNITE release or code commit is printed for these cross-validation models")
UCFG["TF"] = f"{P}-config-wang2026-ichorcna-tf-logistic-regression"
configuration(UCFG["TF"], "ichorCNA tumour fraction with logistic regression (ichorCNA-TF, Wang et al. 2026)", M_ICHOR, [S_UNI, S_UNI_T], "TF",
              "Data file S2 sheet STATS_lr column 'feat'; Methods P47", ["conventional_pipeline"],
              extra={"parameters": "ichorCNA-inferred tumour fraction as the only input to a logistic regression binary classifier; nested cross-validation as for UNITE-XGB; keras v3.3.3 and scikit-learn v1.4.2."},
              version_note="The ichorCNA version is not printed in the inspected text")

D_UNI = f"{P}-data-wang2026-unite-cross-validation"
rec(D_UNI, "dataset", "UNITE cross-validation set: shallow WGS plasma cfDNA, 458 healthy and 1,232 cancer samples",
    "Pooled public and newly sequenced plasma sWGS data used for cross-validation in Wang et al. 2026.", [S_UNI],
    attributes={"version": "Wang et al. 2026 (Science Advances 12:eady9432) sample selection",
                "population": ("1,690 plasma samples after quality control (458 healthy, 1,232 cancer from 26 types) pooled from new LUCID and OV04 "
                               "data, EGA and FinaleDB, including the Cristiano et al. 2019 cohort; split 70:30 by study, cancer type and TF stratum "
                               "into 1,237 cross-validation and 453 held-out samples. Cancers stratified by ichorCNA tumour fraction: [0, 0.03] 736, "
                               "(0.03, 0.1] 239, (0.1, 0.2] 121, (0.2, 1] 136."),
                "split": "1,237 cross-validation samples; 5-fold cross-validation repeated 10 times within them", "total": 1690,
                "assay": "Plasma cfDNA shallow whole-genome sequencing, downsampled to 0.1x",
                "scope_note": "Overlaps the stored DELFI 2019 cohort (amp-20261007-ctdna-fragmentomics-dataset), which is one of the pooled studies.",
                "source_locator": "Wang et al. 2026 Introduction P5; Results P6, P9, P12; Methods P39-P40; Fig. 2 legend"})

UPR = {}
for s, (sk, sname, order) in STRATA.items():
    UPR[s] = f"{P}-protocol-wang2026-unite-cv-{sk}"
    rec(UPR[s], "protocol", f"UNITE cross-validation, cancers with {sname} vs healthy (Wang et al. 2026)",
        "Tumour-fraction-stratified cross-validation of fragmentomic feature sets and an ichorCNA tumour-fraction classifier.",
        [S_UNI, S_UNI_T], [{"relation": "uses_data", "target_id": D_UNI}],
        {"protocol": (f"Restrict cancer samples to those with {sname} (healthy controls unchanged), train each model in nested "
                      "cross-validation (5 outer folds, 10 repeats, StratifiedGroupKFold so no patient is in both training and test folds) "
                      "and summarise each metric over the 50 outer test folds."),
         "version": "Wang et al. 2026 Data file S2 sheets STATS_xgb_x1-x6 and STATS_lr; Methods P47, P49",
         "metric": "auroc", "metric_direction": "higher",
         "limitations": ["Cross-validation within one pooled set of public and new data; not the held-out or unseen test sets.",
                         "Tumour fraction strata are defined by ichorCNA, which is also the input of the ichorCNA-TF comparator.",
                         "Author-reported by the UNITE developers; the DELFI-XGB comparator is reported only in text and figures."],
         "source_locator": f"Data file S2 rows with ichorcna_strat '{s}'; Results P12-P13, P18; Methods P47, P49"})

uni_review = review_note(UNI_ZIP, UNI_URL, "Extracted by deterministic parse of the pinned XLSX cell XML of ady9432_data_file_s2.xlsx "
                         "(extract/rawxlsx.py) with headers, strata, feature and metric labels asserted. Each row's mean is the value; "
                         "ci_95_lower and ci_95_upper are the uncertainty; median, sd and the sem bounds are in source_cells. General-format "
                         "cells; printed_value is the shortest round-trip decimal of the stored value.")
for sheet, mapping, nrows in (("STATS_xgb_x1-x6", XM, 145), ("STATS_lr", LM, 65)):
    cells = ux[sheet]
    expect([cells[f"{c}1"] for c in COLS], STAT_HDR, f"{sheet} header")
    if f"A{nrows + 1}" in cells or f"A{nrows}" not in cells:
        raise SystemExit(f"{sheet} extent changed")
    evs = {}
    for r in range(2, nrows + 1):
        strat, feat, met = cells[f"A{r}"], cells[f"B{r}"], cells[f"C{r}"]
        if strat not in STRATA or met not in mapping or (feat not in FEATS and feat != "TF"):
            raise SystemExit(f"{sheet} row {r} unexpected labels {strat!r} {feat!r} {met!r}")
        cfg = UCFG[feat]
        key = (feat, strat)
        if key not in evs:
            fk = FEATS[feat][0] if feat in FEATS else "ichorcna-tf"
            evs[key] = f"{P}-eval-wang2026-{fk}-{STRATA[strat][0]}"
            evaluation(evs[key], f"{'UNITE XGBoost ' + FEATS[feat][1] if feat in FEATS else 'ichorCNA-TF logistic regression'}, {STRATA[strat][1]}",
                       cfg, UPR[strat], D_UNI, [S_UNI, S_UNI_T], "author_reported" if feat in FEATS else "independent_paper",
                       {"dataset_version": "Wang et al. 2026 cross-validation set", "split": "Nested 5-fold cross-validation, 10 repeats",
                        "population": f"Healthy controls vs cancers with {STRATA[strat][1]}",
                        "inputs": (FEATS[feat][1] if feat in FEATS else "ichorCNA tumour fraction") + " from 0.1x sWGS",
                        "adaptation": "Model trained per outer fold with inner hyperparameter search", "metric_implementation": None,
                        "aggregation": "Mean, median, SD, 95% CI and SEM over 50 outer test folds", "budget": None},
                       f"Data file S2 sheet {sheet}, rows with feat '{feat}' and ichorcna_strat '{strat}'",
                       limitations=None if feat in FEATS else ["Comparator built by the UNITE authors from ichorCNA output; ichorCNA itself was not developed by them."],
                       missing={"comparison.metric_implementation": {"reason": "unreported", "note": "Metric code not described beyond the metric names"}})
        metric, unit, qual = mapping[met]
        mean, lo, hi = cells[f"D{r}"], cells[f"G{r}"], cells[f"H{r}"]
        mk = met.lower().replace("test_", "").replace("_", "-")
        result(f"{P}-result-wang2026-{evs[key].split('-eval-wang2026-')[1]}-{mk}", evs[key], [S_UNI, S_UNI_T],
               f"Data file S2 sheet {sheet}, row {r} (feat '{feat}', ichorcna_strat '{strat}', .metric '{met}'), column D 'mean'",
               shortest(mean), metric, f"cancers with {STRATA[strat][1]} vs healthy; {qual}", unit, uni_review,
               ci(shortest(lo), shortest(hi), f"ci_95_lower {shortest(lo)}, ci_95_upper {shortest(hi)}",
                  "Interval over the 50 outer test folds as printed in columns G and H"),
               extra={"raw_xml_value": mean, "source_label": met,
                      **({"source_anomaly": ("The same sheet prints AUROC 1, sensitivity 1 and specificity 1 for this model and stratum "
                                             "(rows 39, 48, 49), so a value of 0 or a constant at a fixed-specificity threshold is not "
                                             "consistent with them; the fixed-specificity metrics look undefined for this stratum.")}
                         if feat == "TF" and strat == "(0.1, 1]" and met.endswith("spe") else {}),
                      "source_cells": [f"E{r} median {shortest(cells[f'E{r}'])}", f"F{r} sd {shortest(cells[f'F{r}'])}",
                                       f"I{r} sem_lower {shortest(cells[f'I{r}'])}", f"J{r} sem_upper {shortest(cells[f'J{r}'])}"]})

claim(f"{P}-claim-wang2026-tf-strata", UPR["all"], "stratification",
      "Healthy controls (n = 458) form one category; cancers are stratified by ichorCNA tumour fraction into [0, 0.03] (n = 736), (0.03, 0.1] (n = 239), (0.1, 0.2] (n = 121) and (0.2, 1] (n = 136). Models are trained and tested within each category; the [0, 0.03] category has 861 training samples (325 healthy, 536 cancer).",
      [S_UNI], "Results P9 and P12", UNI_XML, "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13353424/fullTextXML")

# ================================================================ relevance judgements
J = "use-case-mapping-ctdna-fragmentomics-20261009"
CONSTRAINTS = ["Inspect every linked evaluation's source locator and preserved conflicts before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; cohorts, features, classifiers and validation designs differ between sources."]


def judgement(short, protocol, relevance, endpoint, rationale, limitations, sources, cites, group, title, metric, label, order):
    rec(f"{J}-{short}", "claim", f"Relevance of {protocol} to \"Select a plasma ctDNA fragmentomics detection workflow\"",
        rationale, sources, [{"relation": "subject", "target_id": UC}],
        {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance, "endpoint": endpoint,
         "rationale": rationale, "constraints": CONSTRAINTS, "limitations": limitations,
         "citation_locators": [{"source_id": s, "locator": loc} for s, loc in cites],
         "source_locator": "; ".join(f"{s}: {loc}" for s, loc in cites), "revision": 1,
         "reason": "Add primary-source cfDNA fragmentomics comparison evidence from the plasma ctDNA fragmentomics use-case pass 2026-10-09.",
         "comparison_group": group, "comparison_title": title, "headline_metric": metric,
         **({"stratum_label": label, "stratum_order": order} if label else {})}, facets={})


judgement("hou2024-pattern-auc", PR["t1"], "proxy",
          "Pan-cancer vs healthy ROC-AUC on the DELFI 2019 cohort for ten fragmentation patterns in open chromatin regions, with and without PCA, five patterns under their original region definitions and a DELFI re-implementation",
          "Compares fragmentomic feature definitions on the same plasma samples with the same classifier, but reports AUC from internal cross-validation rather than sensitivity at a fixed false-positive rate, and no tumour-fraction stratum.",
          ["Internal 10 x 10-fold cross-validation on one cohort", "AUC only", "Re-implementations by Hou et al., not the original tools",
           "Same cohort as the existing DELFI judgement"],
          [S_HOU], [(S_HOU, "Table 1; Experimental Section P24, P29-P45")],
          "hou2024-pattern-auc", "Fragmentation patterns compared on the DELFI 2019 cohort (Hou et al. 2024, Table 1)", "auroc", None, None)
for order, (key, label) in enumerate((("cris", "DELFI 2019 cohort, cross-validation"), ("jiang", "Jiang 2018 liver cohort, cross-validation"),
                                      ("zhou", "Zhou 2022 liver cohort, independent"), ("lucas", "Mathios 2021 LUCAS lung cohort, independent"),
                                      ("mathios-ind", "Mathios 2021 independent lung cohort, independent")), start=1):
    judgement(f"hou2024-{key}", PR[key], "proxy",
              f"ROC-AUC and sensitivity at 95% and 85% specificity of ten fragmentation patterns (open chromatin regions, SVM): {label}",
              "Reports sensitivity at fixed specificity for several fragmentomic feature definitions on the same plasma samples, including independent cohorts, but at 95% and 85% rather than the 98% to 99% specificity of a screening setting, with no tumour-fraction stratum, and the sensitivity columns conflict with another table of the same file.",
              SENS_LIM + ["Re-implementations by Hou et al., not the original tools"],
              [S_HOU, S_HOU_T], [(S_HOU, "Experimental Section P24-P45"), (S_HOU_T, "Tables S2 and S3")],
              "hou2024-sensitivity", "Fragmentation patterns at fixed specificity across cohorts (Hou et al. 2024, Tables S2-S3)",
              "sensitivity-at-95-percent-specificity", label, order)
for s, (sk, sname, order) in STRATA.items():
    judgement(f"wang2026-{sk}", UPR[s], "proxy",
              f"Cross-validated ROC-AUC, AUPRC and default-threshold metrics of five fragmentomic feature sets and their combination (UNITE-XGB), and of an ichorCNA tumour-fraction classifier with sensitivity at 95%, 98% and 99% specificity, for cancers with {sname} vs healthy",
              ("Measures detection of tumour-derived plasma DNA within a low ichorCNA tumour-fraction stratum, the use case's main constraint, on the same samples for each feature set; fixed-specificity sensitivity is printed only for the ichorCNA comparator."
               if s == "[0, 0.03]" else
               "Same comparison in a higher or unstratified tumour-fraction stratum; it shows how feature rankings change with tumour fraction rather than performance at realistic low fractions."),
              ["Cross-validation, not the held-out or unseen test sets", "Fixed-specificity sensitivity only for the ichorCNA-TF comparator in the extracted sheets",
               "Strata defined by ichorCNA, which can misclassify low-fraction samples", "Author-reported by the UNITE developers"],
              [S_UNI, S_UNI_T], [(S_UNI, "Results P9-P18; Methods P39-P49"), (S_UNI_T, "Sheets STATS_xgb_x1-x6 and STATS_lr")],
              "wang2026-tf-strata", "Fragmentomic feature sets by ichorCNA tumour fraction (Wang et al. 2026, UNITE)", "auroc", sname, order)

# ---------------------------------------------------------------- write
records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
if len(ids) != len(set(ids)):
    from collections import Counter as C
    raise SystemExit(f"Duplicate IDs: {[k for k, v in C(ids).items() if v > 1][:5]}")
with open(os.path.join(BATCH, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(BATCH, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    for row in sorted(claim_rows):
        w.writerow(row)
from collections import Counter
print(Counter(r["kind"] for r in records), len(records))
