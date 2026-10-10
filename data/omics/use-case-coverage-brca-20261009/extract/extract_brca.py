"""Deterministic extraction of BRCA1/BRCA2 in silico evidence comparisons into a records batch.

Usage: python3 -I extract_brca.py <pinned-dir> <batch-dir>

<pinned-dir> holds the pinned artifacts named in ARTIFACTS. The script checks each SHA-256, reads the workbook cells
with rawxlsx.py (next to this script) and the tables from the JATS XML, asserts every sheet, header, row label and
caption it depends on, and writes batch.jsonl and claims.csv in the current store shape. Nothing is marked reviewed.
"""
import csv, hashlib, json, math, os, re, sys
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402

PINNED, BATCH = sys.argv[1], sys.argv[2]
P = "brca-20261009"
UC = "use-case-brca1-brca2-germline-interpretation"
UC_NAME = "Interpret BRCA1/BRCA2 germline variants"
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
TODAY = "2026-10-09"
ARTIFACTS = {
    "cubuk2021-article.xml": "ea6391e04f5f01353bb611fd45437f21c531848cf3e93b288bdc52494efc90ae",
    "cubuk2021-supplementary-tables.xlsx": "02df1b0dbf916d598dd8278ba45091022bf78c5722ac13a07d5b1b70d64dc179",
    "ramadane2025-article.xml": "cd089e7c621818f457f54f93c37cc1b9d535e531212b1aaf431fcbdd733bbda1",
}
records, claims_rows, judgements = [], [], []
for name, digest in ARTIFACTS.items():
    got = hashlib.sha256(open(os.path.join(PINNED, name), "rb").read()).hexdigest()
    assert got == digest, f"{name}: {got} != pinned {digest}"


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,254}", id_), id_
    r = {"id": id_, "kind": kind, "name": name[:500], "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def review_note(how):
    return {"method": ["deterministic-table-parse"], "reviewer": ["claude"],
            "reviewer_note": "Extracting Claude (Opus 5.5) research agent; not a review. No human review claimed.",
            "date": TODAY, "note": f"{how} Pending independent review."}


def num(text):
    t = text.replace("−", "-").replace("–", "-").lstrip("+")
    assert re.fullmatch(r"-?(\d+\.?\d*|\.\d+)", t), text
    return format(Decimal(t.rstrip(".") if t.endswith(".") else t), "f")


def result(id_, eval_id, source_ids, sha, url, locator, printed, metric, direction, unit, qualifier, how, name, extra=None):
    attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "metric_qualifier": qualifier,
             "printed_value": printed, "numeric_value": num(printed), "source_locator": locator,
             "review": {**review_note(how), "artifact_sha256": sha, "retrieval_url": url}}
    if extra:
        attrs.update(extra)
    if "uncertainty" not in attrs and "uncertainty" not in attrs.get("missing_metadata", {}):
        attrs.setdefault("missing_metadata", {})["uncertainty"] = {"reason": "unreported"}
    rec(id_, "result", name, "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        source_ids, [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claims_rows.append([id_, source_ids[-1], locator, printed, "result"])


def evaluation(id_, name, system, protocol, dataset, source_ids, origin, comparison, locator, missing=None, extra=None):
    attrs = {"origin": origin, "protocol": protocol, "version": f"Primary source as retrieved {TODAY}",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    if missing:
        attrs["missing_metadata"] = missing
    if extra:
        attrs.update(extra)
    rec(id_, "evaluation", name, "Published in silico evidence comparison for BRCA1/BRCA2 missense variants; transcribed, not reproduced.",
        source_ids, [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
                     {"relation": "data", "target_id": dataset}], attrs)


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower().replace("++", "pp")).strip("-")


def judgement(short, protocol, protocol_name, source_ids, relevance, endpoint, rationale, limitations, locators, group, title, headline,
              stratum=None, order=None):
    cid = f"use-case-mapping-{P}-{short}"
    attrs = {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance, "endpoint": endpoint,
             "rationale": rationale,
             "constraints": ["Inspect every linked evaluation's source locator before citing a result.",
                             "Do not combine this mapping's evaluations with any other protocol's results; truth sets, variant filters, thresholds and score versions differ between sources.",
                             "Scores are evidence inputs to a gene-specific ACMG/AMP review, not complete classifications."],
             "limitations": limitations, "revision": 1,
             "reason": "Add primary-source in silico evidence comparisons against BRCA1/BRCA2 functional truth sets from the BRCA use-case pass (2026-10-09).",
             "citation_locators": [{"source_id": s, "locator": l} for s, l in locators],
             "source_locator": "; ".join(f"{s}: {l}" for s, l in locators),
             "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum is not None:
        attrs["stratum_label"] = stratum
        attrs["stratum_order"] = order
    rec(cid, "claim", f"Relevance of {protocol_name} to \"{UC_NAME}\"", rationale, source_ids,
        [{"relation": "subject", "target_id": UC}], attrs, facets={})
    judgements.append(cid)


def source(sid, title, doi, artifact_url, version, when, sha, media, licence="CC-BY-4.0", extra=None):
    attrs = {"url": f"https://doi.org/{doi}", "artifact_url": artifact_url, "version": version, "retrieved_at": when,
             "artifact_sha256": sha, "doi": doi, "publication_status": "peer_reviewed", "licence": licence, "media_type": media}
    if extra:
        attrs.update(extra)
    rec(sid, "source", title, "Primary source retrieved and hashed for the BRCA1/BRCA2 germline interpretation use-case pass.", [], [], attrs)
    return sid


# Methods. Existing records are reused: BayesDel from main; the others from the reviewed somatic oncogenicity and
# protein stability batches (those batches must be integrated first). The rest are new family-level records.
MAIN = {"bayesdel": "uc-clinical-20260930-method-bayesdel"}
ONCO = {k: f"somatic-oncogenicity-20261009-method-{k}" for k in (
    "alphamissense", "cadd", "chasm", "clinpred", "dann", "eigen", "fathmm", "fathmm-mkl", "genocanyon", "gerp",
    "integrated-fitcons", "lrt", "m-cap", "metalr", "metasvm", "mutationassessor", "mutationtaster", "mutpred", "mvp",
    "phastcons", "phylop", "polyphen2", "primateai", "provean", "revel", "sift", "vest4")}
STAB = {"foldx": "protein-stability-20261009-method-foldx"}
NEW = {  # family: (name, method type, description)
    "align-gvgd": ("Align-GVGD", "specialist", "Grantham variation and deviation over a protein multiple sequence alignment."),
    "condel": ("Condel", "specialist", "Weighted consensus of missense predictors."),
    "gavin": ("GAVIN", "specialist", "Gene-specific allele-frequency and CADD-threshold classifier."),
    "grantham": ("Grantham score", "specialist", "Physicochemical distance between the reference and alternate amino acids."),
    "meta-snp": ("Meta-SNP", "supervised_machine_learning", "Random-forest meta-predictor over PANTHER, PhD-SNP, SIFT and SNAP."),
    "mlp-badmut": ("MLP (badmut)", "supervised_machine_learning", "Meta-predictor over conservation scores and published missense predictors (generesearch.ru badmut service)."),
    "msc": ("Mutation significance cutoff (MSC)", "specialist", "Gene-specific score thresholds for CADD, PolyPhen-2 and SIFT."),
    "panther-psep": ("PANTHER", "specialist", "Protein family hidden Markov model score for substitutions."),
    "phd-snpg": ("PhD-SNPg", "supervised_machine_learning", "Sequence-profile classifier for single-nucleotide variants."),
    "pmut": ("PMut", "supervised_machine_learning", "Neural-network missense pathogenicity predictor."),
    "pon-p2": ("PON-P2", "supervised_machine_learning", "Random-forest missense pathogenicity predictor."),
    "predictsnp": ("PredictSNP", "specialist", "Majority-vote consensus of missense predictors."),
    "rfpred": ("rfPred", "supervised_machine_learning", "Random-forest meta-predictor over SIFT, PolyPhen-2, LRT, phyloP and MutationTaster."),
    "siphy": ("SiPhy", "specialist", "Phylogenetic conservation score."),
    "snap2": ("SNAP2", "supervised_machine_learning", "Neural-network predictor of functional effect of substitutions."),
    "suspect": ("SuSPect", "supervised_machine_learning", "Support vector machine combining sequence, structure and network features."),
}
METHOD_TYPE = {  # method types of the reused records, for configuration facets
    "bayesdel": "supervised_machine_learning", "foldx": "conventional_pipeline", "eigen": "specialist", "fathmm": "specialist",
    "genocanyon": "specialist", "gerp": "specialist", "integrated-fitcons": "specialist", "lrt": "specialist",
    "mutationassessor": "specialist", "phastcons": "specialist", "phylop": "specialist", "provean": "specialist", "sift": "specialist"}
METHODS = {}


def method(fam, source_id):
    if fam in MAIN:
        return MAIN[fam]
    if fam in ONCO:
        return ONCO[fam]
    if fam in STAB:
        return STAB[fam]
    mid = f"{P}-method-{fam}"
    if mid in METHODS:
        if source_id not in METHODS[mid]["source_ids"]:
            METHODS[mid]["source_ids"].append(source_id)
        return mid
    name, mtype, desc = NEW[fam]
    METHODS[mid] = rec(mid, "method", name, desc, [source_id], [],
                       {"reported_name": name, "entity_level": "method", "source_locator": "Supplementary Table 1 and Supplementary Table 5 of Cubuk et al. 2021",
                        "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; score sources are on configurations"}}},
                       facets={**FACETS, "method_types": [mtype]})
    return mid


def mtype(fam):
    return [NEW[fam][1]] if fam in NEW else [METHOD_TYPE.get(fam, "supervised_machine_learning")]


tx = lambda e: " ".join(" ".join(e.itertext()).split())

# =============================================================================================
# A. Cubuk et al. 2021, Genetics in Medicine 23(11):2096, Supplementary Tables 3, 5, 6 and 9 (BRCA1 and BRCA2 columns)
# =============================================================================================
A_ART = source(f"{P}-source-cubuk2021", "Clinical likelihood ratios and balanced accuracy for 44 in silico tools against multiple large-scale functional assays of cancer susceptibility genes",
               "10.1038/s41436-021-01265-z", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8553612/fullTextXML",
               "Genetics in Medicine 23(11):2096, published 2021-07-06; PMC8553612 full-text XML", "2026-10-09T21:18:04Z",
               ARTIFACTS["cubuk2021-article.xml"], "application/xml")
A_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41436-021-01265-z/MediaObjects/41436_2021_1265_MOESM3_ESM.xlsx"
A_SHA = ARTIFACTS["cubuk2021-supplementary-tables.xlsx"]
A = source(f"{P}-source-cubuk2021-supplementary-tables", "Cubuk et al. 2021, Supplementary tables 1-13 (41436_2021_1265_MOESM3_ESM.xlsx)",
           "10.1038/s41436-021-01265-z", A_URL, "41436_2021_1265_MOESM3_ESM.xlsx", "2026-10-09T21:18:15Z", A_SHA,
           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
A_IDS = [A_ART, A]
book = rawxlsx.read(os.path.join(PINNED, "cubuk2021-supplementary-tables.xlsx"))
assert {"SupTable3_Variant_Breakdowns", "SupTable5_Tool_Thresholds", "SupTable6_Tool_Counts", "SupTable7_Prediction_Measures",
        "SupTable9_Likelihood_Ratios"} <= set(book), sorted(book)
t3, t5, t6, t7, t9 = (book[s] for s in ("SupTable3_Variant_Breakdowns", "SupTable5_Tool_Thresholds", "SupTable6_Tool_Counts",
                                        "SupTable7_Prediction_Measures", "SupTable9_Likelihood_Ratios"))
# Definitions: PLR = TPR/FPR; the source's "negative likelihood ratio" = TNR/FNR (a likelihood ratio for benignity).
assert t7["A17"] == "Positive likelihood ratio (LR)=" and t7["F17"] == "or = (TP/total_DEL_true)/(FP/total_TOL_true)", (t7["A17"], t7["F17"])
assert t7["A18"] == "Negative likelihood ratio (LR)=" and t7["F18"] == "or = (TN/total_TOL_true)/(FN/total_DEL_true)", (t7["A18"], t7["F18"])
# Truth-set sizes (Supplementary Table 3).
assert [t3.get(c) for c in ("B1", "C1", "D1")] == ["Variant group", "BRCA1", "BRCA2"]
assert (t3["B8"], t3["B9"], t3["B10"]) == ("ASSAY DEL", "ASSAY TOL", "TOTAL")
TRUTH = {"brca1": {"del": int(t3["C8"]), "tol": int(t3["C9"]), "total": int(t3["C10"])},
         "brca2": {"del": int(t3["D8"]), "tol": int(t3["D9"]), "total": int(t3["D10"])}}
assert TRUTH == {"brca1": {"del": 371, "tol": 1270, "total": 1641}, "brca2": {"del": 64, "tol": 124, "total": 188}}, TRUTH
# Supplementary Table 9 header and Table 6 header.
H9 = {"A1": "tool", "F1": "BRCA1_positive_LR", "G1": "BRCA1_negative_LR", "H1": "BRCA2_positive_LR", "I1": "BRCA2_negative_LR"}
assert all(t9[k] == v for k, v in H9.items()), [t9[k] for k in H9]
H6 = {v: re.match(r"[A-Z]+", k).group() for k, v in t6.items() if re.fullmatch(r"[A-Z]+1", k)}
assert all(f"{g}_{f}" in H6 for g in ("BRCA1", "BRCA2") for f in ("TP", "FN", "FP", "TN", "total_DEL_true", "total_TOL_true", "total_all"))
ROWS9 = [t9[f"A{n}"] for n in range(2, 86)]
assert len(ROWS9) == 84 and f"A86" not in t9, len(ROWS9)
ROW6 = {t6[f"A{n}"]: n for n in range(2, 200) if f"A{n}" in t6}
assert set(ROW6) == set(ROWS9), set(ROW6) ^ set(ROWS9)
# Supplementary Table 5: analysis label to (row). Labels differ slightly from Tables 6 and 9.
ROW5 = {t5[f"B{n}"]: n for n in range(2, 88) if f"B{n}" in t5}
T5_LABEL = {"MetaSNP": "Meta-SNP", "fathmm-MKL_coding": "fathmm.MKL_coding", "MSC-CADD-based": "MSC_CADD", "MSC-PolyPhen2-based": "MSC_PolyPhen2",
            "MSC-SIFT-based": "MSC_SIFT", "PhD-SNPg-all": "PhD-SNPg_all", "PhD-SNPg-p005": "PhD-SNPg_p005", "Polyphen2_HDIV": "Polyphen2_HumDIV",
            "Polyphen2_HVAR": "Polyphen2_HumVAR", "VEST3_a": "VEST_a", "VEST3_b": "VEST_b", "VEST3_c": "VEST_c",
            "Combined-Revel_b-AND-MetaSNP": "Combined-Revel_b-AND-Meta-SNP", "Combined-PANTHER-AND-MetaSNP": "Combined-PANTHER-AND-Meta-SNP"}
# Table 9 label to method family (single tools) or component labels (combinations).
FAM = {"Revel": "revel", "MetaSNP": "meta-snp", "PMut": "pmut", "MutPred": "mutpred", "rfPred": "rfpred", "VEST3": "vest4", "VEST4": "vest4",
       "SNAP2": "snap2", "PANTHER": "panther-psep", "alignGVGD": "align-gvgd", "Eigen-PC": "eigen", "MutationAssessor": "mutationassessor",
       "SuSPect": "suspect", "MSC": "msc", "SIFT": "sift", "PROVEAN": "provean", "PredictSNP": "predictsnp", "PhD-SNPg": "phd-snpg",
       "Polyphen2": "polyphen2", "LRT": "lrt", "Grantham": "grantham", "ClinPred": "clinpred", "DANN": "dann", "MetaSVM": "metasvm",
       "phyloP100way": "phylop", "phyloP20way": "phylop", "BayesDEL": "bayesdel", "GERP++": "gerp", "phastCons100way": "phastcons",
       "phastCons20way": "phastcons", "primateAI": "primateai", "MLP": "mlp-badmut", "MutationTaster": "mutationtaster",
       "CADD": "cadd", "MetaLR": "metalr", "fathmm-MKL": "fathmm-mkl", "GenoCanyon": "genocanyon", "Gavin": "gavin",
       "Condel": "condel", "FATHMM": "fathmm", "CHASM": "chasm", "SiPhy": "siphy", "MVP": "mvp", "PON-P2": "pon-p2",
       "M-CAP": "m-cap", "Integrated": "integrated-fitcons"}
MSC_BASE = {"MSC-CADD-based": "cadd", "MSC-PolyPhen2-based": "polyphen2", "MSC-SIFT-based": "sift"}


def family(label):
    if label in MSC_BASE:
        return "msc"
    base = re.split(r"[_-](?=[a-z0-9]+$)|_", label)[0]
    for k in sorted(FAM, key=len, reverse=True):
        if label.startswith(k):
            return FAM[k]
    raise AssertionError(f"no family for {label} ({base})")


def t5_row(label):
    n = ROW5[T5_LABEL.get(label, label)]
    tool = next((t5.get(f"A{m}") for m in range(n, 1, -1) if t5.get(f"A{m}")), None)
    src = next((t5.get(f"D{m}") for m in range(n, 1, -1) if t5.get(f"D{m}")), None) if not label.startswith("Combined") else None
    return n, tool, " ".join(t5[f"C{n}"].split()), " ".join(src.split()) if src else None


assert all(t5.get(f"D{n}") for n in range(2, 74) if t5.get(f"A{n}")), "every single-tool group in Supplementary Table 5 names its score source"
A_HOW = ("Extracted by deterministic parse of the pinned XLSX cell XML (extract/extract_brca.py with extract/rawxlsx.py), with sheet "
         "names, column headers, row labels and the likelihood-ratio definitions in Supplementary Table 7 asserted. Cells print "
         "'value (lower-upper)'; printed_value is the value as printed and the whole cell is kept in printed_source_cell.")
A_GENES = {
    "brca1": dict(label="BRCA1", col_plr="F", col_blr="G", assay="HAP1 cell survival after saturation genome editing (Findlay et al. 2018)",
                  truth="HAP1 functional score above -0.748 tolerated, below -1.328 deleterious; intermediate scores excluded",
                  region="13 exons covering the RING and BRCT domains"),
    "brca2": dict(label="BRCA2", col_plr="H", col_blr="I", assay="Homology-directed repair (DR-GFP) assay of BRCA2 cDNA constructs in BRCA2-deficient V-C8 cells (Guidugli et al. 2014 and 2018; Richardson et al. 2021)",
                  truth="HDR score above 2.25 (95% probability of neutrality) tolerated, below 1.78 (95% probability of pathogenicity) deleterious",
                  region="DNA-binding domain (amino acids 2481-3186), 252 assayed missense variants"),
}
assert t5_row("BayesDEL_MaxAF_genespecific")[2].endswith("{order: BRCA1, BRCA2, TP53, MSH2, PTEN}")
CELL = re.compile(r"(\.?\d[\d.]*) \((\.?\d[\d.]*)-(\.?\d[\d.]*)\)")
A_LIMS_COMMON = [
    "Functional assay classes are the truth labels, used as proxies for pathogenic and benign; this is not a clinical classification endpoint.",
    "Each tool-threshold combination is a binary call; tools with an intermediate band, and the tool combinations, leave the discordant or intermediate variants out of the counts, so denominators differ between rows (Supplementary Table 6 total_all).",
    "Several tools were trained on ClinVar or HGMD variants, which may include assayed BRCA1/BRCA2 variants.",
    "Thresholds are the published or commonly used cut-offs listed in Supplementary Table 5, not calibrated for these genes, except the BayesDel gene-specific rows.",
    "The source's 'negative likelihood ratio' is TNR/FNR (Supplementary Table 7), stored here as benignity-likelihood-ratio. Its printed intervals have the same log-scale width as the positive likelihood ratio interval in the same row for all 168 BRCA1/BRCA2 cells, and are much narrower than intervals from the Supplementary Table 6 counts, so they are not recorded as structured uncertainty.",
    "Where a count in Supplementary Table 6 is zero, values are printed although the sheet note says such cells are blank; they match 0.5 added to every cell (Haldane correction) and are marked on the results.",
    "Score versions are given only as the score source (ANNOVAR dbNSFP release or web server, Supplementary Table 5); web servers may have changed since.",
]
def counts(label, g):
    n = ROW6[label]
    return {f: int(t6[f"{H6[g.upper() + '_' + f]}{n}"]) for f in ("TP", "FN", "FP", "TN", "total_DEL_true", "total_TOL_true", "total_all")}


ZERO_FN = {g: sum(counts(l, g)["FN"] == 0 for l in ROWS9) for g in A_GENES}
A_DATA, A_PROTO = {}, {}
for g, meta in A_GENES.items():
    tr = TRUTH[g]
    A_DATA[g] = rec(f"{P}-data-cubuk2021-{g}-functional", "dataset",
                    f"{meta['label']} functional truth set: {tr['total']} missense variants classed deleterious or tolerated by {meta['assay'].split(' (')[0]}",
                    f"{meta['label']} missense variants with a functional class, as assembled by Cubuk et al. 2021.", A_IDS, [],
                    {"population": f"{tr['total']} missense variants ({tr['del']} deleterious, {tr['tol']} tolerated) in {meta['region']}; start gain or loss, nonsense, splice-region flanking and intermediate or conflicting variants excluded",
                     "assay": meta["assay"], "split": "Whole truth set; no training", "denominator": tr["total"],
                     "source_locator": "Supplementary Table 2 and Supplementary Table 3; Methods 'Generation of functional truth sets'",
                     "missing_metadata": {"version": {"reason": "unreported", "note": "Assay data release not stated"}}})["id"]
    pid = f"{P}-protocol-cubuk2021-{g}"
    lims = list(A_LIMS_COMMON)
    if g == "brca2":
        lims.append(f"Only {tr['del']} deleterious BRCA2 variants, all in the DNA-binding domain; {ZERO_FN[g]} of 84 rows have zero false negatives, so their benignity likelihood ratios rest on the zero-cell correction.")
    else:
        lims.append("BRCA1 variants come from the RING and BRCT domains only; the same saturation genome editing data underlie the ENIGMA BayesDel calibration and Ramadane-Morchadi et al. 2025.")
    rec(pid, "protocol", f"{meta['label']} functional truth set, binary in silico calls (Cubuk et al. 2021)",
        f"Positive likelihood ratio, likelihood ratio for benignity and false-negative count for 70 tool-threshold combinations and 14 concordance combinations against the {meta['label']} functional truth set.",
        A_IDS, [{"relation": "uses_data", "target_id": A_DATA[g]}],
        {"protocol": f"Each tool's score is dichotomised at the Supplementary Table 5 threshold into deleterious or tolerated and compared with the {meta['label']} functional class ({meta['truth']}). Likelihood ratios follow Supplementary Table 7.",
         "version": "Supplementary Tables 6 and 9", "metric": "likelihood-ratio", "limitations": lims, "denominator": tr["total"],
         "source_locator": f"Supplementary Tables 2, 3, 5, 6, 7 and 9 ({meta['label']} columns); Methods 'Statistical analysis'"})
    A_PROTO[g] = (pid, lims)

A_CONF = {}


def a_config(label):
    if label in A_CONF:
        return A_CONF[label]
    n5, tool, thresholds, src = t5_row(label)
    cid = f"{P}-config-cubuk2021-{slug(label)}"
    if label.startswith("Combined-"):
        parts = label.removeprefix("Combined-").split("-AND-")
        fams = [family(p) for p in parts]
        links = [{"relation": "uses_model", "target_id": method(f, A)} for f in dict.fromkeys(fams)]
        types = sorted({t for f in fams for t in mtype(f)})
        rec(cid, "configuration", f"Concordant calls of {' and '.join(parts)} (Cubuk et al. 2021)",
            "Consensus of the component tool-threshold calls; discordant variants are treated as VUS and left out.", A_IDS, links,
            {"reported_name": label, "foundation_model_eligible": False, "protocol": f"{thresholds} Components: {', '.join(parts)} at their Supplementary Table 5 thresholds.",
             "source_locator": f"Supplementary Table 5 row {n5} ('{t5[f'B{n5}']}')",
             "missing_metadata": {"version": {"reason": "inapplicable", "note": "Combination of the component configurations; versions are on those"}}},
            facets={**FACETS, "method_types": types})
    else:
        fam = family(label)
        links = [{"relation": "configuration_of", "target_id": method(fam, A)}]
        if label in MSC_BASE:
            links.append({"relation": "uses_model", "target_id": method(MSC_BASE[label], A)})
        attrs = {"reported_name": label, "foundation_model_eligible": False, "protocol": f"Discretisation: {thresholds}",
                 "source_locator": f"Supplementary Table 5 row {n5} ('{tool}', '{t5[f'B{n5}']}')"}
        if src and "dbnsfp" in src.lower():
            attrs["version"] = f"Scores from {src}"
        else:
            attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": f"Score source: {src}"}}
        rec(cid, "configuration", f"{label} (Cubuk et al. 2021)", f"{tool} scores dichotomised at the cited threshold.", A_IDS, links, attrs,
            facets={**FACETS, "method_types": mtype(fam)})
    A_CONF[label] = cid
    return cid


a_order = 0
for g, meta in A_GENES.items():
    pid, lims = A_PROTO[g]
    tr = TRUTH[g]
    eval_ids = []
    for n9, label in enumerate(ROWS9, start=2):
        c = counts(label, g)
        assert c["TP"] + c["FN"] == c["total_DEL_true"] <= tr["del"] and c["FP"] + c["TN"] == c["total_TOL_true"] <= tr["tol"], (label, g, c)
        assert c["total_DEL_true"] + c["total_TOL_true"] == c["total_all"], (label, g, c)
        zero = [f for f in ("TP", "FN", "FP", "TN") if c[f] == 0]
        cid = a_config(label)
        eid = f"{P}-eval-cubuk2021-{slug(label)}-{g}"
        evaluation(eid, f"{label} on the {meta['label']} functional truth set (Cubuk et al. 2021)", cid, pid, A_DATA[g], A_IDS, "independent_paper",
                   {"dataset_version": None, "split": "Whole truth set", "population": f"{c['total_all']} of {tr['total']} {meta['label']} truth-set variants with a deleterious or tolerated call",
                    "inputs": "Missense variant", "adaptation": None,
                    "metric_implementation": "Binary call at the Supplementary Table 5 threshold; PLR = TPR/FPR and likelihood ratio for benignity = TNR/FNR (Supplementary Table 7)",
                    "aggregation": "Pooled over variants", "budget": None},
                   f"Supplementary Table 9 row {n9} and Supplementary Table 6 row {ROW6[label]}, tool '{label}', {meta['label']} columns",
                   missing={"comparison.dataset_version": {"reason": "unreported"}})
        eval_ids.append(eid)
        anomaly = ({"source_anomaly": f"Supplementary Table 6 has a zero count ({', '.join(zero)}) for this tool and gene; the sheet note says such cells are blank, but a value is printed. It matches 0.5 added to every count (Haldane correction)."}
                   if zero else {})
        for kind, col in (("plr", meta["col_plr"]), ("blr", meta["col_blr"])):
            cell = t9[f"{col}{n9}"]
            m = CELL.fullmatch(cell)
            assert m, (label, g, cell)
            point, lo, hi = m.groups()
            loc = f"Supplementary Table 9 (sheet 'SupTable9_Likelihood_Ratios'), {col}{n9}; tool '{label}'; column '{t9[f'{col}1']}'"
            extra = {"printed_source_cell": cell, "denominator": c["total_all"],
                     "denominator_note": f"Variants with a deleterious or tolerated call (Supplementary Table 6 {meta['label']}_total_all); the truth set has {tr['total']}", **anomaly}
            if kind == "plr":
                extra["uncertainty"] = {"type": "confidence_interval", "printed": f"({lo}-{hi})", "lower": num(lo), "upper": num(hi),
                                        "note": "Interval level and method not printed."}
                result(f"{P}-result-cubuk2021-{slug(label)}-{g}-plr", eid, A_IDS, A_SHA, A_URL, loc, point, "likelihood-ratio", "higher", "unitless",
                       f"Positive likelihood ratio of a deleterious call (TPR/FPR), {meta['label']} functional truth set", A_HOW,
                       f"{label} {meta['label']} positive likelihood ratio", extra)
            else:
                extra["missing_metadata"] = {"uncertainty": {"reason": "conflicting", "note": f"Printed interval ({lo}-{hi}) has the same log-scale width as this row's positive likelihood ratio interval and is not consistent with the Supplementary Table 6 counts; kept in printed_source_cell only."}}
                result(f"{P}-result-cubuk2021-{slug(label)}-{g}-blr", eid, A_IDS, A_SHA, A_URL, loc, point, "benignity-likelihood-ratio", "higher", "unitless",
                       f"Source 'negative likelihood ratio' (TNR/FNR): likelihood ratio for benignity of a tolerated call, {meta['label']} functional truth set", A_HOW,
                       f"{label} {meta['label']} likelihood ratio for benignity", extra)
        fn_col = H6[f"{meta['label']}_FN"]
        result(f"{P}-result-cubuk2021-{slug(label)}-{g}-false-negatives", eid, A_IDS, A_SHA, A_URL,
               f"Supplementary Table 6 (sheet 'SupTable6_Tool_Counts'), {fn_col}{ROW6[label]}; tool '{label}'; column '{meta['label']}_FN'",
               t6[f"{fn_col}{ROW6[label]}"], "false-negative-count", "lower", "count",
               f"Functionally deleterious {meta['label']} variants called tolerated", A_HOW,
               f"{label} {meta['label']} false negatives",
               {"denominator": c["total_DEL_true"], "denominator_note": f"Deleterious truth-set variants with a call (Supplementary Table 6 {meta['label']}_total_DEL_true); the truth set has {tr['del']}",
                "missing_metadata": {"uncertainty": {"reason": "inapplicable", "note": "Count"}}})
    a_order += 1
    judgement(f"cubuk2021-{g}", pid, f"{meta['label']} functional truth set, binary in silico calls (Cubuk et al. 2021)", A_IDS, "proxy",
              f"Positive likelihood ratio, likelihood ratio for benignity and false-negative count for 70 tool-threshold calls and 14 concordance combinations against {tr['total']:,} {meta['label']} missense variants with a functional class",
              (f"A large functional truth set for {meta['label']} shows how much evidence each tool's binary call gives toward pathogenicity or benignity, "
               "and how many functionally deleterious variants it would call tolerated, which is the serious error if computational evidence is applied as BP4. "
               "Functional class stands in for clinical classification, so this is proxy evidence."),
              lims, [(A, f"Supplementary Tables 3, 5, 6, 7 and 9 ({meta['label']} columns)"), (A_ART, "Methods 'Statistical analysis'; Results 'Positive and negative likelihood ratios'")],
              "cubuk2021-functional-truth", "Binary in silico calls against BRCA1 and BRCA2 functional truth sets (Cubuk et al. 2021)", "likelihood-ratio",
              stratum="BRCA1 saturation genome editing (RING and BRCT)" if g == "brca1" else "BRCA2 HDR assay (DNA-binding domain)", order=a_order)

# =============================================================================================
# B. Ramadane-Morchadi et al. 2025, American Journal of Human Genetics 112(5):993, Tables 1 and 2
# =============================================================================================
B_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12120176/fullTextXML"
B_SHA = ARTIFACTS["ramadane2025-article.xml"]
B = source(f"{P}-source-ramadane2025", "ACMG/AMP interpretation of BRCA1 missense variants: Structure-informed scores add evidence strength granularity to the PP3/BP4 computational evidence",
           "10.1016/j.ajhg.2024.12.011", B_URL, "American Journal of Human Genetics 112(5):993, published 2025; PMC12120176 full-text XML",
           "2026-10-09T21:18:06Z", B_SHA, "application/xml")
bt = ET.parse(os.path.join(PINNED, "ramadane2025-article.xml"))
assert tx(bt.find(".//article-meta//article-title")).startswith("ACMG/AMP interpretation of BRCA1 missense variants")
B_COI = tx(next(s for s in bt.iter("sec") if (s.find("title") is not None and tx(s.find("title")) == "Declaration of interests")))
assert "employee of Ambry Genetics" in B_COI, B_COI


def btable(tid):
    tw = next(x for x in bt.iter("table-wrap") if x.get("id") == tid)
    return tw, [[tx(c) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]


tw1, rows1 = btable("tbl1")
assert tx(tw1.find("caption")) == "PP3/BP4 computational evidence based on AlphaMissense, ΔΔG AF , ΔΔG PDB , or BayesDel at different benignity and pathogenicity cutoff thresholds"
assert rows1[0] == ["", "Benignity evidence (BP4)", "No bioinformatic code applicable", "Pathogenicity evidence (PP3)"], rows1[0]
assert rows1[1] == ["Threshold", "Evidence strength, log 2 LR (95% CI)", "Threshold", "Evidence strength, log 2 LR (95% CI)"], rows1[1]
FOOT1 = tx(tw1.find("table-wrap-foot"))
assert "a Generic thresholds as per AlphaMissense developers" in FOOT1 and "b FoldX5.0 predictions" in FOOT1 and "c BP4/PP3 BRCA1 VCEP thresholds" in FOOT1
tw2, rows2 = btable("tbl2")
assert tx(tw2.find("caption")) == "Diagnostic test evaluation"
assert rows2[0] == ["Threshold", "Sensitivity", "Specificity", "PPV", "NPV", "Accuracy"], rows2[0]
assert "discriminating MAVE LoF variants" in tx(tw2.find("table-wrap-foot"))
# Table 1: rows 2-9, with the tool label on the first row of each group (rowspan).
GROUPS1 = [("AM", 3), ("ΔΔG AF b", 2), ("ΔΔG PDB b", 2), ("BD", 1)]
B_TOOL = {"AM": ("alphamissense", "AlphaMissense", "am"), "ΔΔG AF b": ("foldx", "FoldX5.0 ΔΔG on AlphaFold2 models", "ddg-af"),
          "ΔΔG PDB b": ("foldx", "FoldX5.0 ΔΔG on experimental PDB structures", "ddg-pdb"), "BD": ("bayesdel", "BayesDel", "bayesdel")}
T1 = []
i = 2
for label, span in GROUPS1:
    for k in range(span):
        r = rows1[i]
        if k == 0:
            assert r[0] == label and len(r) == 6, r
            r = r[1:]
        assert len(r) == 5, r
        T1.append((label, i + 1, r))
        i += 1
assert i == len(rows1) == 10, len(rows1)
LR_CELL = re.compile(r"([+−]?\d+\.\d+) \(([+−]?\d+\.\d+) to ([+−]?\d+\.\d+)\)")
B_POP = "1,519 BRCA1 RING and BRCT missense variants: 337 LoF and 1,182 FUNC by MAVE score; 119 intermediate variants excluded"
B_DATA = rec(f"{P}-data-ramadane2025-brca1-mave", "dataset", "BRCA1 RING and BRCT missense variants with saturation genome editing functional class (Findlay et al. 2018), LoF versus FUNC",
             "MAVE dataset assembled by Ramadane-Morchadi et al. 2025 from Findlay et al. 2018.", [B], [],
             {"population": B_POP, "assay": "HAP1 cell survival after saturation genome editing (Findlay et al. 2018): FUNC score above -0.748, LoF below -1.328",
              "split": "Whole dataset; thresholds were chosen on the same variants", "denominator": 1519,
              "source_locator": "Material and methods paragraph 1; Results paragraph 5",
              "missing_metadata": {"version": {"reason": "unreported"}}})["id"]
B_LIMS_COMMON = [
    "LoF and FUNC functional classes stand in for pathogenic and benign; intermediate variants are excluded.",
    "AlphaMissense and ΔΔG thresholds were chosen by a trade-off process on the same 1,519 variants, so their evidence strengths are not held-out estimates.",
    "BayesDel thresholds are the BRCA1 VCEP specification, which was calibrated on functional data that overlap this dataset.",
    "BRCA1 RING and BRCT domains only.",
    "Three authors are employees of Ambry Genetics (Declaration of interests); several authors contribute to the ENIGMA BRCA1/2 VCEP.",
]
b_conf = {}


def b_config(label, ben, path):
    key = f"{B_TOOL[label][2]}-{slug(ben)}-{slug(path)}"
    if key in b_conf:
        return b_conf[key]
    fam, name, _ = B_TOOL[label]
    cid = f"{P}-config-ramadane2025-{key}"
    attrs = {"reported_name": name, "foundation_model_eligible": False,
             "protocol": f"BP4 if score {ben}, PP3 if score {path}, no computational code in between",
             "source_locator": "Table 1; Material and methods paragraphs 2-4"}
    if fam == "foldx":
        attrs["version"] = "FoldX5.0"
    elif fam == "alphamissense":
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "Pre-computed scores from the dm_alphamissense storage bucket"}}
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "Scores from dbNSFP through the Ensembl Variant Effect Predictor; releases not stated"}}
    rec(cid, "configuration", f"{name}, BP4 {ben} and PP3 {path} (Ramadane-Morchadi et al. 2025)", f"{name} with three-category PP3/BP4 thresholds.",
        [B], [{"relation": "configuration_of", "target_id": method(fam, B)}], attrs, facets={**FACETS, "method_types": mtype(fam)})
    b_conf[key] = cid
    return cid


B_HOW = ("Extracted by deterministic parse of the table in the pinned JATS XML (extract/extract_brca.py), with the caption, header "
         "rows, row labels and footnotes asserted. printed_value is the cell value without its footnote letter and interval; the whole cell "
         "is kept in printed_source_cell.")
p1 = f"{P}-protocol-ramadane2025-pp3-bp4"
lims1 = B_LIMS_COMMON + ["Log2 likelihood ratios come from an online calculator (gwiggins.shinyapps.io/lr_shiny); the interval method is not stated beyond 95% CI."]
rec(p1, "protocol", "BRCA1 MAVE PP3/BP4 evidence strength by score threshold (Ramadane-Morchadi et al. 2025 Table 1)",
    "Log2 likelihood ratio for BP4 and PP3 score ranges and the share of variants left with no computational code, for AlphaMissense, FoldX ΔΔG and BayesDel.",
    [B], [{"relation": "uses_data", "target_id": B_DATA}],
    {"protocol": "Variants are assigned BP4, no code, or PP3 by score thresholds; the likelihood ratio of each range for LoF versus FUNC is converted to log2 (Tavtigian points scale: 1, 2 and 4 are supporting, moderate and strong).",
     "version": "Table 1", "metric": "log2-likelihood-ratio", "limitations": lims1, "denominator": 1519,
     "source_locator": "Table 1; Material and methods paragraph 4; Results paragraphs 8-12"})
b_eval1 = []
for label, row_no, r in T1:
    ben, ben_cell, nocode, path, path_cell = r
    ben_t, path_t = re.sub(r" [a-c]$", "", ben), re.sub(r" [a-c]$", "", path)
    cid = b_config(label, ben_t, path_t)
    eid = f"{P}-eval-ramadane2025-{cid.removeprefix(P + '-config-ramadane2025-')}-pp3-bp4"
    evaluation(eid, f"{B_TOOL[label][1]}, BP4 {ben_t} and PP3 {path_t}, BRCA1 MAVE evidence strength (Ramadane-Morchadi et al. 2025)", cid, p1, B_DATA, [B],
               "independent_paper",
               {"dataset_version": None, "split": "Whole dataset", "population": B_POP, "inputs": "Missense variant (and structure for ΔΔG)",
                "adaptation": "Thresholds chosen on this dataset for AlphaMissense rows 2-3 and ΔΔG; developer thresholds for AlphaMissense row 1; VCEP thresholds for BayesDel",
                "metric_implementation": "Log2 likelihood ratio of LoF versus FUNC within each score range, with 95% CI", "aggregation": "Pooled over variants", "budget": None},
               f"Table 1, row {row_no} ('{label}' group)", missing={"comparison.dataset_version": {"reason": "unreported"}})
    b_eval1.append(eid)
    base = eid.removeprefix(P + "-eval-")
    for side, thr, cell, direction in (("bp4", ben_t, ben_cell, "lower"), ("pp3", path_t, path_cell, "higher")):
        m = LR_CELL.fullmatch(cell)
        assert m, cell
        col = "Benignity evidence (BP4)" if side == "bp4" else "Pathogenicity evidence (PP3)"
        result(f"{P}-result-{base}-{side}-log2-lr", eid, [B], B_SHA, B_URL, f"Table 1, row {row_no} ('{label}' group), column '{col}: Evidence strength, log 2 LR (95% CI)'",
               m.group(1), "log2-likelihood-ratio", direction, "unitless",
               f"{side.upper()} range (score {thr}), LoF versus FUNC", B_HOW, f"{B_TOOL[label][1]} {side.upper()} {thr} log2 likelihood ratio",
               {"printed_source_cell": cell, "score_category": thr, "denominator": 1519,
                "uncertainty": {"type": "confidence_interval", "level": 0.95, "printed": f"({m.group(2)} to {m.group(3)})", "lower": num(m.group(2)), "upper": num(m.group(3))}})
    assert re.fullmatch(r"\d+%", nocode), nocode
    result(f"{P}-result-{base}-no-code-proportion", eid, [B], B_SHA, B_URL, f"Table 1, row {row_no} ('{label}' group), column 'No bioinformatic code applicable'",
           nocode.rstrip("%"), "proportion", "lower", "percent", f"Variants with no computational code (score between {ben_t} and {path_t})", B_HOW,
           f"{B_TOOL[label][1]} share with no code, {ben_t} to {path_t}", {"printed_source_cell": nocode, "denominator": 1519})
judgement("ramadane2025-pp3-bp4", p1, "BRCA1 MAVE PP3/BP4 evidence strength by score threshold (Ramadane-Morchadi et al. 2025)", [B], "proxy",
          "Log2 likelihood ratio for BP4 and PP3 ranges, and the share of variants with no computational code, for AlphaMissense, FoldX ΔΔG and BayesDel on 1,519 BRCA1 missense variants",
          ("Shows, on one BRCA1 functional dataset, the ACMG/AMP evidence strength each score range would carry and how many variants would get no computational evidence, "
           "comparing AlphaMissense and structure-based ΔΔG with the BayesDel thresholds in the current BRCA1 VCEP specification. "
           "Functional class stands in for clinical classification, so this is proxy evidence."),
          lims1, [(B, "Table 1; Material and methods paragraphs 1-4; Results paragraphs 5-12")],
          "ramadane2025-pp3-bp4", "PP3/BP4 evidence strength for BRCA1 missense variants (Ramadane-Morchadi et al. 2025)", "log2-likelihood-ratio")

# Table 2: group header rows ('AM', 'ΔΔG AF a', ...) span all columns; blank spacer rows between.
T2_GROUP = {"AM": "AM", "ΔΔG AF a": "ΔΔG AF b", "ΔΔG PDB a": "ΔΔG PDB b", "BD": "BD"}
PAIR = {}  # (Table 1 label, PP3 threshold) -> BP4 threshold, to reuse the Table 1 configuration
for label, _, r in T1:
    PAIR[(label, re.sub(r" [a-c]$", "", r[3]).replace(".0", ""))] = re.sub(r" [a-c]$", "", r[0])
T2_COLS = [(1, "recall", "Sensitivity"), (2, "specificity", "Specificity"), (3, "precision", "PPV"),
           (4, "negative-predictive-value", "NPV"), (5, "accuracy", "Accuracy")]
PCT = re.compile(r"(\d+\.\d) \((\d+\.\d)–(\d+\.\d)\)")
p2 = f"{P}-protocol-ramadane2025-binary"
lims2 = B_LIMS_COMMON + ["Each row is a single binary cut at the PP3 threshold; variants below it count as predicted FUNC, so this does not describe the three-category use in Table 1.",
                         "Intervals were computed with the MedCalc online calculator; the method is not stated."]
rec(p2, "protocol", "BRCA1 MAVE LoF discrimination at the PP3 threshold (Ramadane-Morchadi et al. 2025 Table 2)",
    "Sensitivity, specificity, PPV, NPV and accuracy for discriminating LoF from FUNC BRCA1 missense variants at one threshold per tool.",
    [B], [{"relation": "uses_data", "target_id": B_DATA}],
    {"protocol": "Each score is dichotomised at its PP3 threshold; predicted LoF is compared with the MAVE LoF or FUNC class.",
     "version": "Table 2", "metric": "recall", "limitations": lims2, "denominator": 1519,
     "source_locator": "Table 2; Material and methods paragraph 4; Results paragraph 11"})
group = None
for row_no, r in enumerate(rows2, start=1):
    if row_no == 1 or r == [""]:
        continue
    if len(r) == 1:
        group, header = T2_GROUP[r[0]], r[0]
        continue
    assert len(r) == 6 and group, r
    thr = r[0]
    key = (group, thr.replace(".0", ""))
    assert key in PAIR, key
    cid = b_config(group, PAIR[key], next(re.sub(r" [a-c]$", "", x[2][3]) for x in T1 if x[0] == group and re.sub(r" [a-c]$", "", x[2][3]).replace(".0", "") == key[1]))
    eid = f"{P}-eval-ramadane2025-{cid.removeprefix(P + '-config-ramadane2025-')}-binary"
    evaluation(eid, f"{B_TOOL[group][1]} {thr}, BRCA1 MAVE LoF discrimination (Ramadane-Morchadi et al. 2025)", cid, p2, B_DATA, [B], "independent_paper",
               {"dataset_version": None, "split": "Whole dataset", "population": B_POP, "inputs": "Missense variant (and structure for ΔΔG)",
                "adaptation": f"Binary call at the PP3 threshold {thr} only", "metric_implementation": "Sensitivity, specificity, PPV, NPV and accuracy with 95% CI (MedCalc)",
                "aggregation": "Pooled over variants", "budget": None},
               f"Table 2, '{header}' group, row '{thr}'", missing={"comparison.dataset_version": {"reason": "unreported"}})
    base = eid.removeprefix(P + "-eval-")
    for col, metric, head in T2_COLS:
        cell = r[col]
        m = PCT.fullmatch(cell)
        assert m, cell
        pt, lo, hi = (float(x) for x in m.groups())
        extra = {"printed_source_cell": cell, "denominator": 1519,
                 "uncertainty": {"type": "confidence_interval", "level": 0.95, "printed": f"({m.group(2)}–{m.group(3)})", "lower": num(m.group(2)), "upper": num(m.group(3))}}
        if (pt - lo) > 3 * (hi - pt) or (hi - pt) > 3 * (pt - lo):
            extra["source_anomaly"] = (f"Printed interval is {pt - lo:.1f} points below and {hi - pt:.1f} above the estimate; every other interval in Table 2 is within a "
                                       "ratio of 1.5. The bound may be misprinted; it is recorded as printed.")
        result(f"{P}-result-{base}-{slug(head)}", eid, [B], B_SHA, B_URL, f"Table 2, '{header}' group, row '{thr}', column '{head}'", m.group(1), metric, "higher", "percent",
               f"LoF versus FUNC at {thr}", B_HOW, f"{B_TOOL[group][1]} {thr} {head}", extra)
judgement("ramadane2025-binary", p2, "BRCA1 MAVE LoF discrimination at the PP3 threshold (Ramadane-Morchadi et al. 2025)", [B], "proxy",
          "Sensitivity, specificity, PPV, NPV and accuracy for AlphaMissense, FoldX ΔΔG and BayesDel at their PP3 thresholds on 1,519 BRCA1 missense variants",
          ("Sensitivity and NPV at the PP3 cut show how many functionally abnormal BRCA1 variants each score would miss, the error that matters most for safe use of computational evidence. "
           "Functional class stands in for clinical classification, so this is proxy evidence."),
          lims2, [(B, "Table 2; Material and methods paragraph 4; Results paragraph 11")],
          "ramadane2025-binary", "Binary LoF discrimination for BRCA1 missense variants (Ramadane-Morchadi et al. 2025)", "recall")

# ---------------------------------------------------------------------------------------------
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), [i for i, c in Counter(ids).items() if c > 1]
os.makedirs(BATCH, exist_ok=True)
records.sort(key=lambda r: r["id"])
with open(os.path.join(BATCH, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claims_rows.sort()
with open(os.path.join(BATCH, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
print(Counter(r["kind"] for r in records))
