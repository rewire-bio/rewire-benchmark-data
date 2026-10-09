"""Deterministic extraction of somatic missense oncogenicity predictor comparisons into a records batch.

Usage: python3 -I extract_somatic_oncogenicity.py <pinned-dir> <batch-dir>

<pinned-dir> holds the pinned artifacts under the names in ARTIFACTS. The script checks each SHA-256, reads the
tables, asserts every row and column label it depends on, and writes batch.jsonl and claims.csv in the current
store shape. Nothing is marked reviewed.
"""
import csv, hashlib, json, os, re, sys
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402

PINNED, BATCH = sys.argv[1], sys.argv[2]
P = "somatic-oncogenicity-20261009"
UC = "use-case-somatic-small-variant-oncogenicity"
UC_NAME = "Assess somatic small-variant oncogenicity"
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
TODAY = "2026-10-09"
ARTIFACTS = {
    "chen2020-article.xml": "fef52f70c3a0ff3f82902f87080933c220e12274787de6309b41ee283daf8b8e",
    "chen2020-additional-file-1.xlsx": "483840c2546f42b3517bcbcd583a3af083df45470e35e4955eda260a19152b09",
    "chen2020-additional-file-9.xlsx": "64b284aefb768c963a5e7079594d3bb7173ef3a5a5e6b0936d0a78126f25440c",
    "chen2020-additional-file-10.xlsx": "b9c41136f45b38533312baa4abfe2923390861c4e49d4d91c6d0275a85222294",
    "chen2020-additional-file-21.xlsx": "47c4d461085334b017994d1846ceb06d6e44e7be369ecd2ecfe00620d6a0f7f5",
    "chen2020-additional-file-22.xlsx": "21ed28f45eee2149e88dff6b75680c99001c4b6daa9805cc9e473d2300ae117a",
    "lee2026-preprint-full-text.html": "1b4dfadc861c6b8dbecde6ebb5efdb5ab7203bcf6f1b4e06edc70e167e7050e9",
    "lee2026-oncocal-tool-performance.tsv": "8f5a81078482c8010b83bba6225e9707980a3a7cebbb2ca00ed8b155ad34c3b5",
}
records, claims_rows = [], []


def sha256(data):
    return hashlib.sha256(data).hexdigest()


for name, digest in ARTIFACTS.items():
    got = sha256(open(os.path.join(PINNED, name), "rb").read())
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


METRIC = {
    "accuracy": dict(metric="accuracy", metric_direction="higher", unit="fraction"),
    "sensitivity": dict(metric="recall", metric_direction="higher", unit="fraction"),
    "specificity": dict(metric="specificity", metric_direction="higher", unit="fraction"),
    "ppv": dict(metric="precision", metric_direction="higher", unit="fraction"),
    "npv": dict(metric="negative-predictive-value", metric_direction="higher", unit="fraction"),
    "auroc": dict(metric="auroc", metric_direction="higher", unit="fraction"),
    "auprc": dict(metric="auprc", metric_direction="higher", unit="fraction"),
}


def result(id_, eval_id, source_ids, artifact_sha, url, locator, printed, metric, qualifier, how, extra=None):
    attrs = {**METRIC[metric], "metric_qualifier": qualifier, "printed_value": printed,
             "numeric_value": format(Decimal(printed), "f"), "source_locator": locator,
             "review": {**review_note(how), "artifact_sha256": artifact_sha, "retrieval_url": url}}
    if extra:
        attrs.update(extra)
    if "uncertainty" not in attrs:
        attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
    rec(id_, "result", f"{eval_id.removeprefix(P + '-eval-')} {METRIC[metric]['metric']} ({qualifier})",
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        source_ids, [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claims_rows.append([id_, source_ids[-1], locator, printed, "result"])


def evaluation(id_, name, system, protocol, dataset, source_ids, origin, comparison, locator, missing=None, extra=None):
    attrs = {"origin": origin, "protocol": protocol, "version": f"Primary source as retrieved {TODAY}",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    if missing:
        attrs["missing_metadata"] = missing
    if extra:
        attrs.update(extra)
    rec(id_, "evaluation", name, "Published comparison of variant effect predictors; transcribed, not reproduced.", source_ids,
        [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
         {"relation": "data", "target_id": dataset}], attrs)


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


# Method families; several printed labels map to one family.
FAMILY = {
    "Polyphen2_HDIV": "polyphen2", "Polyphen2_HVAR": "polyphen2", "SIFT": "sift", "SIFT4G": "sift",
    "Eigen": "eigen", "Eigen-PC": "eigen", "Eigen-raw_coding": "eigen", "Eigen-PC-raw_coding": "eigen",
    "CTAT-cancer": "ctat", "CTAT-population": "ctat", "FATHMM-cancer": "fathmm", "FATHMM-disease": "fathmm",
    "FATHMM-MKL": "fathmm-mkl", "FATHMM-XF": "fathmm-xf", "fathmm-XF_coding": "fathmm-xf",
    "CADD": "cadd", "CADD_raw": "cadd", "MutationTaster2": "mutationtaster", "MutationTaster": "mutationtaster",
    "BayesDel_addAF": "bayesdel", "BayesDel_noAF": "bayesdel", "MisFit_D": "misfit", "MisFit_S": "misfit",
    "VARITY_ER": "varity", "VARITY_ER_LOO": "varity", "VARITY_R": "varity", "VARITY_R_LOO": "varity",
    "MutPred": "mutpred", "MutPred2": "mutpred",
    "GERP_92_mammals": "gerp", "GERPpp_RS": "gerp",
    "phyloP100way_vertebrate": "phylop", "phyloP17way_primate": "phylop", "phyloP470way_mammalian": "phylop",
    "phastCons100way_vertebrate": "phastcons", "phastCons17way_primate": "phastcons", "phastCons470way_mammalian": "phastcons",
}
FAMILY_NAME = {"polyphen2": "PolyPhen-2", "sift": "SIFT", "eigen": "Eigen", "ctat": "CTAT (cancer and population ensembles)",
               "fathmm": "FATHMM", "fathmm-mkl": "FATHMM-MKL", "fathmm-xf": "FATHMM-XF", "cadd": "CADD",
               "mutationtaster": "MutationTaster", "bayesdel": "BayesDel", "misfit": "MisFit", "varity": "VARITY",
               "mutpred": "MutPred", "gerp": "GERP", "phylop": "phyloP", "phastcons": "phastCons"}
CONSERVATION = {"gerp", "phylop", "phastcons", "bstatistic"}
CANCER_SPECIFIC = {"CHASM", "CanDrA", "CTAT-cancer", "FATHMM-cancer", "TransFIC"}
METHODS = {}


def method(label, source_ids):
    fam = FAMILY.get(label, slug(label))
    mid = f"{P}-method-{fam}"
    if mid in METHODS:
        for s in source_ids:
            if s not in METHODS[mid]["source_ids"]:
                METHODS[mid]["source_ids"].append(s)
        return mid, fam
    name = FAMILY_NAME.get(fam, label)
    kind = ("Conservation score used as a predictor" if fam in CONSERVATION else
            "Variant effect predictor for missense variants")
    METHODS[mid] = rec(mid, "method", name, f"{kind}.", list(source_ids), [],
                       {"reported_name": name, "entity_level": "method", "source_locator": "Algorithm lists of the cited sources",
                        "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; score sources are on configurations"}}},
                       facets={**FACETS, "method_types": ["conventional_pipeline"] if fam in CONSERVATION else ["supervised_machine_learning"]})
    return mid, fam


ALIGNMENT_HEURISTIC = {"sift", "provean", "lrt", "mutationassessor", "list-s2", "fathmm", "integrated-fitcons", "genocanyon", "bstatistic"}
UNSUPERVISED = {"popeve", "eigen", "primateai-unsupervised"}


def mtype(label, fam):
    """Broad method type; a judgement made here from each tool's published design, recorded for review."""
    if fam in CONSERVATION or fam in ALIGNMENT_HEURISTIC:
        return ["conventional_pipeline"]
    if label == "ESM1b":
        return ["foundation_model"]
    if fam in UNSUPERVISED:
        return ["specialist"]
    return ["supervised_machine_learning"]


judgements = []


def judgement(short, protocol, protocol_name, source_ids, relevance, endpoint, rationale, constraints, limitations,
              locators, group, title, headline, stratum=None, order=None):
    cid = f"use-case-mapping-{P}-{short}"
    attrs = {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance,
             "endpoint": endpoint, "rationale": rationale, "constraints": constraints, "limitations": limitations,
             "revision": 1,
             "reason": "Add primary-source predictor comparison evidence from the somatic oncogenicity use-case pass (2026-10-09).",
             "citation_locators": [{"source_id": s, "locator": l} for s, l in locators],
             "source_locator": "; ".join(f"{s}: {l}" for s, l in locators),
             "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum is not None:
        attrs["stratum_label"] = stratum
        attrs["stratum_order"] = order
    rec(cid, "claim", f"Relevance of {protocol_name} to \"{UC_NAME}\"", rationale, source_ids,
        [{"relation": "subject", "target_id": UC}], attrs, facets={})
    judgements.append(cid)


CONSTRAINTS = ["Inspect every linked evaluation's source locator before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; truth sets, negatives, thresholds and predictor versions differ between sources."]

# =============================================================================================
# A. Chen et al. 2020, Genome Biology 21:43, Additional files 1, 9, 10, 21 and 22
# =============================================================================================
A_ART = f"{P}-source-chen2020"
A_ESM = "https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-020-01954-z/MediaObjects/13059_2020_1954_MOESM{n}_ESM.xlsx"
rec(A_ART, "source", "Comprehensive assessment of computational algorithms in predicting cancer driver mutations",
    "Primary source retrieved and hashed for the somatic oncogenicity use-case pass.", [], [],
    {"url": "https://doi.org/10.1186/s13059-020-01954-z", "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7033911/fullTextXML",
     "version": "Genome Biology 21:43, published 2020-02-20; PMC7033911 full-text XML", "retrieved_at": "2026-10-09T20:45:50Z",
     "artifact_sha256": ARTIFACTS["chen2020-article.xml"], "doi": "10.1186/s13059-020-01954-z",
     "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml"})
A_FILES = {}
for n, when, desc in [(1, "2026-10-09T20:47:19Z", "Default prediction categories of 17 algorithms"),
                      (9, "2026-10-09T20:46:04Z", "Performance metrics of 33 algorithms, median-score threshold, benchmark 2 (OncoKB)"),
                      (10, "2026-10-09T20:46:14Z", "Performance metrics of 17 algorithms, default categories, benchmark 2 (OncoKB)"),
                      (21, "2026-10-09T20:46:04Z", "Performance metrics of 33 algorithms, median-score threshold, benchmark 5 (cell viability)"),
                      (22, "2026-10-09T20:46:15Z", "Performance metrics of 17 algorithms, default categories, benchmark 5 (cell viability)")]:
    sid = f"{P}-source-chen2020-additional-file-{n}"
    A_FILES[n] = sid
    rec(sid, "source", f"Chen et al. 2020, Additional file {n}: {desc}", "Supplementary workbook as served by the publisher.", [], [],
        {"url": "https://doi.org/10.1186/s13059-020-01954-z", "artifact_url": A_ESM.format(n=n),
         "version": f"13059_2020_1954_MOESM{n}_ESM.xlsx", "retrieved_at": when,
         "artifact_sha256": ARTIFACTS[f"chen2020-additional-file-{n}.xlsx"], "doi": "10.1186/s13059-020-01954-z",
         "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
         "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
A_HOW = ("Extracted by deterministic parse of the pinned XLSX cell XML (extract/extract_somatic_oncogenicity.py with "
         "extract/rawxlsx.py), with the sheet name, column headers and algorithm labels asserted. Each cell prints "
         "'mean (lower-upper)'; printed_value is the mean as printed and the bracketed range is kept in uncertainty.")

art = ET.parse(os.path.join(PINNED, "chen2020-article.xml"))
tx = lambda e: " ".join(" ".join(e.itertext()).split())
tab1 = next(t for t in art.iter("table-wrap") if t.get("id") == "Tab1")
T1 = {}
for tr in tab1.iter("tr"):
    cells = [tx(c) for c in tr if c.tag in ("td", "th")]
    if cells and cells[0] != "Classifier":
        T1[cells[0]] = {"features": cells[1], "method": cells[2]}
assert len(T1) == 33, len(T1)
cat = rawxlsx.read(os.path.join(PINNED, "chen2020-additional-file-1.xlsx"))["Additional file 1"]
assert [cat["A1"], cat["B1"], cat["C1"], cat["D1"].strip()] == ["Algorithm", "Categories or Thresholds", "Positive category", "Negative category"]
CATS = {cat[f"A{r}"]: (cat[f"C{r}"], cat[f"D{r}"]) for r in range(2, 40) if f"A{r}" in cat}
SCORE_SOURCE = {"CHASM": "CRAVAT web server v5.2.4", "CanDrA": "CanDrA download (MD Anderson)", "TransFIC": "TransFIC web server",
                "FATHMM-cancer": "FATHMM cancer web server", "CTAT-cancer": "Principal component of TransFIC, FATHMM, CHASM and CanDrA computed by the authors",
                "CTAT-population": "Principal component of SIFT, PolyPhen2, MutationAssessor and VEST computed by the authors"}
A_CONF = {}


def chen_config(label):
    if label in A_CONF:
        return A_CONF[label]
    mid, fam = method(label, [A_ART])
    src = SCORE_SOURCE.get(label, "dbNSFP v4.0")
    attrs = {"reported_name": label, "version": f"Scores from {src}", "foundation_model_eligible": False,
             "protocol": f"{T1[label]['method']}; features: {T1[label]['features']}",
             "source_locator": "Table 1; Methods 'Inter-correlation analysis among algorithms'"}
    if label in CATS:
        attrs["configuration"] = {"default_positive_category": CATS[label][0], "default_negative_category": CATS[label][1].strip()}
    A_CONF[label] = rec(f"{P}-config-chen2020-{slug(label)}", "configuration", f"{label} (Chen et al. 2020)",
                        f"{label} scores as used in the cited comparison.", [A_ART], [{"relation": "configuration_of", "target_id": mid}],
                        attrs, facets={**FACETS, "method_types": mtype(label, fam)})["id"]
    return A_CONF[label]


A_DATA = {
    "oncokb": rec(f"{P}-data-chen2020-oncokb", "dataset", "OncoKB-annotated somatic missense mutations (oncogenic versus likely neutral)",
                  "Benchmark 2 truth set in Chen et al. 2020.", [A_ART], [],
                  {"population": "Methods: 816 oncogenic, 1,384 likely oncogenic and 421 likely neutral mutations (271 inconclusive excluded); Results: 773 oncogenic and 497 likely neutral used in the main comparison",
                   "split": "400 positives and 400 negatives drawn at random, 100 times, for the binary metrics",
                   "source_locator": "Results 'Benchmark 2'; Methods 'OncoKB annotation benchmark' and 'Calculation of five evaluation metrics'",
                   "missing_metadata": {"version": {"reason": "unreported", "note": "OncoKB download date or release not stated"},
                                        "population_detail": {"reason": "conflicting", "note": "Counts differ between Results and Methods; which positive set the binary metrics used is not stated"}}})["id"],
    "viability": rec(f"{P}-data-chen2020-cell-viability", "dataset", "Missense mutations with Ba/F3 and MCF10A cell viability calls (published and new)",
                     "Benchmark 5 truth set in Chen et al. 2020.", [A_ART], [],
                     {"population": "797 published and 164 new missense mutations; positives activating, inactivating, inhibitory or non-inhibitory in either cell model; negatives neutral in both",
                      "split": "400 positives and 400 negatives drawn at random, 100 times, for the binary metrics",
                      "source_locator": "Results 'Benchmark 5'; Methods 'In vitro cell viability assay benchmark'",
                      "missing_metadata": {"version": {"reason": "unreported"}}})["id"],
}
HEAD = ["Algorithm", "Accuracy (±2σ)", "Sensitivity (±2σ)", "Specificity (±2σ)", "PPV (±2σ)", "NPV (±2σ)"]
COLS = ["A", "B", "C", "D", "E", "F"]
MKEYS = ["accuracy", "sensitivity", "specificity", "ppv", "npv"]
CELL = re.compile(r"^(\d\.\d\d) \((\d\.\d\d)-(\d\.\d\d)\)$")
SPECS = [(9, "oncokb", "median", 33), (10, "oncokb", "default", 17), (21, "viability", "median", 33), (22, "viability", "default", 17)]
GROUP = {"oncokb": ("chen2020-oncokb", "OncoKB oncogenic versus likely neutral (Chen et al. 2020)"),
         "viability": ("chen2020-cell-viability", "Cell viability assay drivers versus neutral (Chen et al. 2020)")}
ORDER = {"median": 1, "default": 2}
for n, bench, thr, nrows in SPECS:
    sheet = rawxlsx.read(os.path.join(PINNED, f"chen2020-additional-file-{n}.xlsx"))
    assert list(sheet) == [f"Additional_file_{n}"], list(sheet)
    cells = sheet[f"Additional_file_{n}"]
    assert [cells[f"{c}1"] for c in COLS] == HEAD, [cells.get(f"{c}1") for c in COLS]
    assert f"A{nrows + 2}" not in cells and f"A{nrows + 1}" in cells, (n, nrows)
    src = [A_ART, A_FILES[n]]
    pid = f"{P}-protocol-chen2020-{bench}-{thr}"
    bname = {"oncokb": "OncoKB oncogenic versus likely neutral", "viability": "cell viability drivers versus neutral"}[bench]
    tname = {"median": "median-score threshold", "default": "default categorical calls"}[thr]
    lims = ["Binary metrics are means over 100 random draws of 400 positives and 400 negatives; the bracketed range is printed as plus or minus two standard deviations, not a confidence interval.",
            "Predictor scores date from dbNSFP v4.0 and 2019 web servers; current releases (for example AlphaMissense, CHASMplus, BoostDM) are not included."]
    if thr == "median":
        lims.append("The threshold is each algorithm's median score on the benchmark, which is not available when classifying a new variant; it measures ranking, not a usable operating point.")
    else:
        lims.append("Only 17 algorithms provide default categories, mostly germline deleteriousness tools; cancer-specific tools other than CanDrA and FATHMM-disease are absent.")
    if bench == "oncokb":
        lims += ["OncoKB annotations are biased towards known, often actionable cancer genes (Discussion).",
                 "Some predictors were trained on known cancer mutations, so performance on literature-curated drivers may be inflated."]
    else:
        lims += ["Functional calls come from the authors' own Ba/F3 and MCF10A screens; a growth effect in either cell model counts as positive.",
                 "Activating and inactivating variants are pooled, so oncogene and tumour-suppressor mechanisms are not separated."]
    rec(pid, "protocol", f"{bname.capitalize()}, {tname} (Chen et al. 2020 Additional file {n})",
        f"Accuracy, sensitivity, specificity, PPV and NPV of {nrows} predictors using {tname}.", src,
        [{"relation": "uses_data", "target_id": A_DATA[bench]}],
        {"protocol": (f"Binary predictions by {tname}"
                      + (" (each algorithm's median score on the benchmark)" if thr == "median" else " (categories in Additional file 1)")
                      + " compared with the truth labels with reportROC; 400 positives and 400 negatives sampled 100 times; mean and two standard deviations reported."),
         "version": f"Additional file {n}", "metric": "accuracy", "limitations": lims,
         "source_locator": f"Additional file {n}; Methods 'Calculation of five evaluation metrics based on categorical predictions'"})
    for r in range(2, nrows + 2):
        label = cells[f"A{r}"]
        assert label in T1, label
        cid = chen_config(label)
        eid = f"{P}-eval-chen2020-{slug(label)}-{bench}-{thr}"
        evaluation(eid, f"{label} on {bname}, {tname} (Chen et al. 2020)", cid, pid, A_DATA[bench], src, "independent_paper",
                   {"dataset_version": None, "split": "100 random draws of 400 positives and 400 negatives",
                    "population": "400 positives and 400 negatives per draw", "inputs": "Missense SNV scores", "adaptation": None,
                    "metric_implementation": "reportROC (R)", "aggregation": "Mean over 100 draws", "budget": None},
                   f"Additional file {n}, row {r} ('{label}')", missing={"comparison.dataset_version": {"reason": "unreported"}})
        for c, m in zip(COLS[1:], MKEYS):
            raw = cells[f"{c}{r}"]
            mm = CELL.match(raw)
            assert mm, (n, c, r, raw)
            unc = {"type": "confidence_interval", "lower": mm.group(2), "upper": mm.group(3), "printed": f"({mm.group(2)}-{mm.group(3)})",
                   "resamples": 100,
                   "note": "Column header '(±2σ)': mean plus or minus two standard deviations over 100 random draws (Methods). Not a formal confidence interval; no level set."}
            result(f"{P}-result-chen2020-{slug(label)}-{bench}-{thr}-{METRIC[m]['metric']}", eid, src, ARTIFACTS[f"chen2020-additional-file-{n}.xlsx"],
                   A_ESM.format(n=n), f"Additional file {n} (sheet 'Additional_file_{n}'), {c}{r}; Algorithm '{label}'; column '{HEAD[COLS.index(c)]}'",
                   mm.group(1), m, f"{bname}, {tname}", A_HOW, {"uncertainty": unc, "printed_source_cell": raw})
    grp, title = GROUP[bench]
    judgement(f"chen2020-{bench}-{thr}", pid, f"{bname}, {tname} (Chen et al. 2020)", src, "direct",
              f"Accuracy, sensitivity, specificity, PPV and NPV for {nrows} predictors on {bname} using {tname}",
              ("Somatic missense mutations labelled by " + ("expert literature curation (OncoKB)" if bench == "oncokb" else "cell viability assays")
               + ", with somatic or assay-neutral negatives rather than germline-benign labels; directly measures how well each predictor separates drivers from non-drivers. "
               "The authors developed none of the predictors."),
              CONSTRAINTS, lims, [(A_FILES[n], f"Additional file {n}"), (A_ART, f"Results 'Benchmark {2 if bench == 'oncokb' else 5}'; Methods")],
              grp, title, "accuracy", stratum={"median": "Median-score threshold", "default": "Default categories"}[thr], order=ORDER[thr])

# =============================================================================================
# B. Lee 2026, bioRxiv preprint 10.64898/2026.07.16.739080 v1, OncoCal repository tables/tool_performance.tsv
# =============================================================================================
B_PP, B_TAB = f"{P}-source-lee2026", f"{P}-source-lee2026-oncocal-tool-performance"
COMMIT = "40b7770f2a768ba800c4f4c6b48e2bfe967ed14a"
B_TAB_URL = f"https://raw.githubusercontent.com/tjdrnjsqpf/oncocal/{COMMIT}/tables/tool_performance.tsv"
rec(B_PP, "source", "An openly licensed benchmark and per-gene calibration map for missense pathogenicity predictors on activating cancer drivers",
    "Preprint retrieved and hashed for the somatic oncogenicity use-case pass.", [], [],
    {"url": "https://doi.org/10.64898/2026.07.16.739080", "artifact_url": "https://www.biorxiv.org/content/10.64898/2026.07.16.739080v1.full",
     "version": "bioRxiv 2026.07.16.739080 v1, posted 2026-07-23; full-text HTML page", "retrieved_at": "2026-10-09T20:48:19Z",
     "artifact_sha256": ARTIFACTS["lee2026-preprint-full-text.html"], "doi": "10.64898/2026.07.16.739080",
     "publication_status": "preprint", "licence": "CC-BY-4.0", "media_type": "text/html",
     "hash_scope": "SHA-256 of one retrieval of the full-text HTML page, which is mutable (site chrome, metrics). The PDF request returned HTTP 429."})
rec(B_TAB, "source", "OncoCal repository, tables/tool_performance.tsv (per-tool AUROC and AUPRC by gene role)",
    "Result table released with the preprint in the author's repository, pinned to a commit.", [], [],
    {"url": "https://github.com/tjdrnjsqpf/oncocal", "artifact_url": B_TAB_URL,
     "version": f"commit {COMMIT} (2026-07-11)", "retrieved_at": "2026-10-09T20:48:49Z",
     "artifact_sha256": ARTIFACTS["lee2026-oncocal-tool-performance.tsv"], "publication_status": "official_project_source",
     "licence": "MIT (repository licence)", "media_type": "text/tab-separated-values", "code_url": "https://github.com/tjdrnjsqpf/oncocal"})
B_SRC = [B_PP, B_TAB]
B_HOW = ("Extracted by deterministic parse of the pinned TSV (extract/extract_somatic_oncogenicity.py), with the header, the three "
         "group labels and 49 tools per group asserted. printed_value is the field text as written in the file.")
pp = open(os.path.join(PINNED, "lee2026-preprint-full-text.html"), encoding="utf8").read()
assert "Across all 49 tools, 42 (86%) achieved a lower AUROC for oncogene" in re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", pp))
lines = open(os.path.join(PINNED, "lee2026-oncocal-tool-performance.tsv"), encoding="utf8").read().rstrip("\n").split("\n")
assert lines[0].split("\t") == ["tool", "group", "n", "pos", "AUROC", "AUPRC"], lines[0]
rows = [l.split("\t") for l in lines[1:]]
assert len(rows) == 147 and all(len(r) == 6 for r in rows)
GROUPS = ["all", "oncogene", "TSG"]
tools = [r[0] for r in rows if r[1] == "all"]
assert len(tools) == 49 and all(sorted(r[0] for r in rows if r[1] == g) == sorted(tools) for g in GROUPS)
bdid = rec(f"{P}-data-lee2026-cgc-missense", "dataset", "Missense variants in 768 Cancer Gene Census genes with open oncogenicity labels",
           "Benchmark data in Lee 2026.", B_SRC, [],
           {"population": ("20,815 unique protein-level entries (3,922 positive). Positives: cancerhotspots residues, CIViC oncogenic, or COSMIC recurrence of at least 10 samples; "
                           "negatives: ClinVar benign or likely benign, or gnomAD allele frequency of at least 0.001. Gene role from CIViC variant mechanism where available, otherwise CGC gene role."),
            "split": "Whole labelled set per tool (tool-specific coverage; n and positives printed per row)",
            "source_locator": "Preprint Results first section and Methods 'Labels'; OncoCal data/README.md",
            "missing_metadata": {"version": {"reason": "unreported", "note": "CIViC nightly, ClinVar and cancerhotspots v2 download dates not stated; COSMIC v104; dbNSFP 5.3.1a"}}})["id"]
B_CONF = {}
for gi, g in enumerate(GROUPS):
    gname = {"all": "all genes", "oncogene": "oncogenes (gain of function)", "TSG": "tumour suppressors (loss of function)"}[g]
    pid = f"{P}-protocol-lee2026-{slug(g)}"
    lims = ["Negatives are ClinVar benign or likely benign and gnomAD common variants, that is germline-benign labels; the use case does not accept these as automatic somatic negatives.",
            "Many supervised tools were trained on ClinVar labels, so the ClinVar-benign negatives overlap their training data.",
            "Preprint by a single author, not peer reviewed; the analysis code is in the linked repository.",
            "Scores are dbNSFP 5.3.1a rank scores; tool coverage differs, so each row has its own n and positives.",
            "No uncertainty is printed in this table; the preprint text gives a best-tool AUROC of 0.871 (VARITY_R) in one place and 0.874 in another, so values may depend on the variant subset."]
    if g != "all":
        lims.append("Gene role uses CGC gene-level roles where variant-level CIViC mechanism is missing, so some variants may be assigned the wrong mechanism.")
    rec(pid, "protocol", f"CGC missense oncogenicity, {gname} (Lee 2026, OncoCal tool_performance.tsv)",
        f"AUROC and AUPRC of 49 predictor and conservation scores on {gname}.", B_SRC, [{"relation": "uses_data", "target_id": bdid}],
        {"protocol": "Each dbNSFP 5.3.1a rank score is used directly to rank labelled variants; AUROC and AUPRC are computed per tool on the variants it scores, for all genes and by gene role.",
         "version": f"tables/tool_performance.tsv rows with group '{g}'", "metric": "auroc", "limitations": lims,
         "source_locator": f"OncoCal tables/tool_performance.tsv at {COMMIT[:12]}, group '{g}'; preprint S1 Table and Fig 1A"})
    for r in rows:
        if r[1] != g:
            continue
        tool = r[0]
        if tool not in B_CONF:
            mid, fam = method(tool, [B_PP])
            B_CONF[tool] = rec(f"{P}-config-lee2026-{slug(tool)}", "configuration", f"{tool} rank score, dbNSFP 5.3.1a (Lee 2026)",
                               f"{tool} as scored in the cited benchmark.", B_SRC, [{"relation": "configuration_of", "target_id": mid}],
                               {"reported_name": tool, "version": "dbNSFP 5.3.1a rank score (GRCh38)", "foundation_model_eligible": tool == "ESM1b",
                                "source_locator": "OncoCal tool_performance.tsv column 'tool'; preprint Methods 'Features'"},
                               facets={**FACETS, "method_types": mtype(tool, fam)})["id"]
        eid = f"{P}-eval-lee2026-{slug(tool)}-{slug(g)}"
        evaluation(eid, f"{tool} on CGC missense, {gname} (Lee 2026)", B_CONF[tool], pid, bdid, B_SRC, "independent_paper",
                   {"dataset_version": None, "split": "Whole labelled set", "population": f"{r[2]} variants, {r[3]} positive",
                    "inputs": "dbNSFP rank score", "adaptation": None, "metric_implementation": None,
                    "aggregation": "Pooled over variants", "budget": None},
                   f"tool_performance.tsv row ('{tool}', '{g}')",
                   missing={"comparison.dataset_version": {"reason": "unreported"}, "comparison.metric_implementation": {"reason": "unextracted", "note": "Repository code not inspected"}},
                   extra={"denominator": int(r[2]), "positive_count": int(r[3])})
        claims_rows.append([eid, B_TAB, f"tool_performance.tsv row ('{tool}', '{g}'), columns 'n' and 'pos'", f"{r[2]}; {r[3]}", "evaluation"])
        for val, m, col in ((r[4], "auroc", "AUROC"), (r[5], "auprc", "AUPRC")):
            result(f"{P}-result-lee2026-{slug(tool)}-{slug(g)}-{m}", eid, B_SRC, ARTIFACTS["lee2026-oncocal-tool-performance.tsv"], B_TAB_URL,
                   f"OncoCal tables/tool_performance.tsv at commit {COMMIT[:12]}, row tool '{tool}', group '{g}', column '{col}'",
                   val, m, f"CGC missense, {gname}", B_HOW)
    judgement(f"lee2026-{slug(g)}", pid, f"CGC missense oncogenicity, {gname} (Lee 2026)", B_SRC, "proxy",
              f"AUROC and AUPRC of 49 predictor and conservation scores on CGC missense variants, {gname}",
              ("Compares many predictors, including AlphaMissense, ESM1b and popEVE, separately for oncogene and tumour-suppressor variants, "
               "the mechanism split the use case asks for; proxy because its negatives are germline-benign labels and it is an unreviewed preprint."),
              CONSTRAINTS, lims, [(B_TAB, f"group '{g}'"), (B_PP, "Results first section; Methods 'Labels' and 'Features'")],
              "lee2026-cgc-mechanism", "Predictors by gene mechanism on CGC missense variants (Lee 2026 preprint)", "auroc",
              stratum={"all": "All genes", "oncogene": "Oncogenes (GOF)", "TSG": "Tumour suppressors (LOF)"}[g], order=gi + 1)

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
