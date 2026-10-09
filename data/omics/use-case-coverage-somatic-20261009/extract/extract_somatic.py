"""Deterministic extraction of somatic SNV and indel caller comparison tables into a records batch.

Usage: python3 -I extract_somatic.py <download-dir> <batch-dir>

<download-dir> holds the pinned artifacts under the names listed in ARTIFACTS. The script checks
their SHA-256, reads the tables cell by cell, asserts every row and column label it depends on,
and writes batch.jsonl and claims.csv in the current store shape (single-meaning relations,
declared attributes). printed_value is the shortest round-trip decimal of the stored cell value;
the raw stored text is kept in raw_xml_value. Nothing is marked reviewed.
"""
import csv, hashlib, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402
import rawxls  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
P = "somatic-20261009"
UC = "use-case-tumour-dna-somatic-variant-detection"
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
TODAY = "2026-10-09"
ARTIFACTS = {
    "wang2020-article.xml": "5f4e6b16675a3a6587f7999792ef479a059851ea8f7a31b4a954901aced5a8b1",
    "wang2020-supplementary-tables.xlsx": "b9b5c68c7f78ff16863f64bb414394fd7b7dcd600795532aab30e39cd8d39c81",
    "guille2025-article.xml": "2c6fc6f329f7ebea34889de5f0cc8dff2d0d90b9a8dc3192ddac0949281c9827",
    "guille2025-table-s7.xls": "735470fcb1ae7c3578ab3efefe12fde4b73bac279a1e7185950e5c2c0f1073f2",
    "guille2025-supplementary-methods.docx": "222509b8ec4b47b0278d6ea504291dba07a615c2fa23e3aaef600ea6aaf39709",
}
records, claims_rows = [], []


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


for name, digest in ARTIFACTS.items():
    got = sha256(os.path.join(DL, name))
    assert got == digest, f"{name}: {got} != pinned {digest}"


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,254}", id_), id_
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def printed(raw):
    """Shortest round-trip decimal of a stored number."""
    f = float(raw)
    s = repr(f)
    if s.endswith(".0"):
        s = s[:-2]
    if "e" in s or "E" in s:
        s = format(Decimal(s), "f")
    return s, format(Decimal(s), "f")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def review_note(how):
    return {"method": ["deterministic-table-parse"], "reviewer": ["claude"],
            "reviewer_note": "Extracting Claude (Opus 5.5) research agent; not a review. No human review claimed.",
            "date": TODAY,
            "note": f"{how} Pending independent review."}


METRIC = {
    "count": dict(metric="count", metric_direction="unknown", unit="count",
                  unit_detail="counted entity: somatic variant calls reported by the configuration"),
    "recall": dict(metric="recall", metric_direction="higher", unit="fraction"),
    "precision": dict(metric="precision", metric_direction="higher", unit="fraction"),
    "f1": dict(metric="f1-score", metric_direction="higher", unit="fraction"),
}


def result(id_, eval_id, source_ids, artifact_sha, retrieval_url, locator, raw, metric, qualifier, how, extra=None):
    pv, nv = printed(raw)
    attrs = {**METRIC[metric], "metric_qualifier": qualifier, "printed_value": pv, "numeric_value": nv,
             "raw_xml_value": raw, "source_locator": locator,
             "missing_metadata": {"uncertainty": {"reason": "unreported"}},
             "review": {**review_note(how), "artifact_sha256": artifact_sha, "retrieval_url": retrieval_url}}
    if extra:
        attrs.update(extra)
    rec(id_, "result", f"{eval_id.removeprefix(P + '-eval-')} {METRIC[metric]['metric']} ({qualifier})",
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        source_ids, [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claims_rows.append([id_, source_ids[-1], locator, pv, "result"])


def evaluation(id_, name, system, protocol, dataset, source_ids, origin, comparison, locator, missing=None, extra=None):
    attrs = {"origin": origin, "protocol": protocol, "version": f"Primary source as retrieved {TODAY}",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    if missing:
        attrs["missing_metadata"] = missing
    if extra:
        attrs.update(extra)
    rec(id_, "evaluation", name, "Published somatic caller comparison; transcribed, not reproduced.", source_ids,
        [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
         {"relation": "data", "target_id": dataset}], attrs)


METHODS = {}


def method(key, name, description, reported_name, method_types, source_ids, extra=None):
    mid = f"{P}-method-{key}"
    if mid in METHODS:
        for s in source_ids:
            if s not in METHODS[mid]["source_ids"]:
                METHODS[mid]["source_ids"].append(s)
        return mid
    attrs = {"reported_name": reported_name, "entity_level": "method",
             "source_locator": "Tool lists and table row labels of the cited sources",
             "missing_metadata": {"version": {"reason": "inapplicable",
                                              "note": "Family record; versions are on configurations"}}}
    if extra:
        attrs.update(extra)
    METHODS[mid] = rec(mid, "method", name, description, list(source_ids), [],
                       attrs, facets={**FACETS, "method_types": method_types})
    return mid


judgements = []


def judgement(short, protocol, protocol_name, source_ids, relevance, endpoint, rationale, constraints, limitations,
              locators, group, title, headline, stratum=None, order=None):
    cid = f"use-case-mapping-{P}-{short}"
    attrs = {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance,
             "endpoint": endpoint, "rationale": rationale, "constraints": constraints, "limitations": limitations,
             "revision": 1,
             "reason": "Add primary-source protocol evidence from the somatic SNV and indel use-case pass (2026-10-09).",
             "citation_locators": [{"source_id": s, "locator": l} for s, l in locators],
             "source_locator": "; ".join(f"{s}: {l}" for s, l in locators),
             "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum is not None:
        attrs["stratum_label"] = stratum
        attrs["stratum_order"] = order
    rec(cid, "claim", f"Relevance of {protocol_name} to \"Select a tumour DNA somatic variant-calling workflow\"",
        rationale, source_ids, [{"relation": "subject", "target_id": UC}], attrs, facets={})
    judgements.append({"claim_id": cid, "protocol_id": protocol, "relevance": relevance,
                       "comparison_group": group, "stratum_label": stratum})


# ---------------------------------------------------------------------------------------------
# Wang et al. 2020, Sci Rep 10:12898 (SomaticCombiner), Supplementary Tables S1 and S2
# ---------------------------------------------------------------------------------------------
W_ART = f"{P}-source-wang2020"
W_TAB = f"{P}-source-wang2020-tables"
W_SRC = [W_ART, W_TAB]
W_TAB_URL = ("https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-020-69772-8/"
             "MediaObjects/41598_2020_69772_MOESM3_ESM.xlsx")
W_ART_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7393490/fullTextXML"
W_SHA = ARTIFACTS["wang2020-supplementary-tables.xlsx"]
W_HOW = ("Extracted by deterministic parse of the pinned XLSX cell XML (extract/extract_somatic.py with "
         "extract/rawxlsx.py), with the sheet title, column headers, dataset labels and configuration labels "
         "asserted. printed_value is the shortest round-trip decimal of the stored double; raw_xml_value keeps "
         "the stored text. Spreadsheet display formatting was not applied.")

rec(W_ART, "source",
    "SomaticCombiner: improving the performance of somatic variant calling based on evaluation tests and a consensus approach",
    "Primary source retrieved and hashed for the tumour somatic SNV and indel use-case pass.", [], [],
    {"url": "https://doi.org/10.1038/s41598-020-69772-8", "artifact_url": W_ART_URL,
     "version": "Scientific Reports 10:12898, published 2020-07-30; PMC7393490 full-text XML",
     "retrieved_at": "2026-10-09T20:00:37Z", "artifact_sha256": ARTIFACTS["wang2020-article.xml"],
     "doi": "10.1038/s41598-020-69772-8", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/xml"})
rec(W_TAB, "source", "Wang et al. 2020, Supplementary Tables (somatic caller performance)",
    "Supplementary workbook with per-dataset caller performance; Tables S1 (WGS SNVs) and S2 (WGS indels) extracted.",
    [], [],
    {"url": "https://doi.org/10.1038/s41598-020-69772-8", "artifact_url": W_TAB_URL,
     "version": "41598_2020_69772_MOESM3_ESM.xlsx (Supplementary Tables S1-S9) as served by the publisher",
     "retrieved_at": "2026-10-09T20:00:59Z", "artifact_sha256": W_SHA,
     "doi": "10.1038/s41598-020-69772-8", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})

wb = rawxlsx.read(os.path.join(DL, "wang2020-supplementary-tables.xlsx"))
assert list(wb)[:2] == ["S1 WGS SNVs", "S2 WGS INDELs"], list(wb)
S1, S2 = wb["S1 WGS SNVs"], wb["S2 WGS INDELs"]
assert S1["A1"].startswith("Table S1.  The performance comparisons for eight WGS datasets."), S1["A1"]
assert S2["A1"].startswith("Table S2.  The performance comparisons of INDEL calling for five WGS datasets."), S2["A1"]
HEAD = {"A3": "Dataset", "B3": "True Count", "C3": "Caller", "D3": " Count", "E3": " Recall",
        "F3": " Precision", "G3": " F1"}
for sheet in (S1, S2):
    for ref, text in HEAD.items():
        assert sheet[ref] == text, (ref, sheet[ref])

# Truth counts printed in article Table 1 (WGS datasets): SNVs / INDELs
TABLE1 = {"DREAM Set1": ("3537", None), "DREAM Set2": ("4332", None), "DREAM Set3": ("7903", "7991"),
          "DREAM Set4": ("16315", "14230"), "CLL": ("1319", "134"), "AML": ("1342", None),
          "COLO": ("35543", "446"), "MB": ("1263", "347")}

DATASETS = {
    "DREAM Set1": dict(key="dream-set1", short="DREAM synthetic set 1", name="ICGC-TCGA DREAM synthetic set 1 (WGS)",
                       assay="Simulated tumour-normal WGS from the DREAM challenge (mutations added with a read simulator, reference 19); 27.89x normal, 27.89x tumour",
                       context="Synthetic, 100% tumour cellularity", cov="27.89/27.89"),
    "DREAM Set2": dict(key="dream-set2", short="DREAM synthetic set 2", name="ICGC-TCGA DREAM synthetic set 2 (WGS)",
                       assay="Simulated tumour-normal WGS from the DREAM challenge; 34.06x normal, 34.05x tumour",
                       context="Synthetic, 80% tumour cellularity", cov="34.06/34.05"),
    "DREAM Set3": dict(key="dream-set3", short="DREAM synthetic set 3", name="ICGC-TCGA DREAM synthetic set 3 (WGS)",
                       assay="Simulated tumour-normal WGS from the DREAM challenge; 34.23x normal, 34.19x tumour",
                       context="Synthetic, 100% tumour cellularity, with subclonality", cov="34.23/34.19"),
    "DREAM Set4": dict(key="dream-set4", short="DREAM synthetic set 4", name="ICGC-TCGA DREAM synthetic set 4 (WGS)",
                       assay="Simulated tumour-normal WGS from the DREAM challenge; 30.02x normal, 29.92x tumour",
                       context="Synthetic, 80% tumour cellularity, with subclonality", cov="30.02/29.92"),
    "CLL": dict(key="cll", short="CLL tumour", name="Chronic lymphocytic leukaemia tumour-normal WGS with curated somatic calls",
                assay="Real tumour-normal WGS (EGAD00001001858), FASTQs from several centres concatenated, Novoalign v3.00.05 to hg19; 40.90x normal, 32.47x tumour",
                context="Real tumour; curated high-confidence somatic call set from the cited benchmark study (reference 31)", cov="40.90/32.47"),
    "AML": dict(key="aml", short="AML tumour", name="Acute myeloid leukaemia tumour-normal WGS with platinum somatic list",
                assay="Real tumour-normal WGS (dbGaP phs000159; runs SRR2470200 and SRR2177258), downloaded BAMs; 126.90x normal, 320.91x tumour",
                context="Real tumour; 'platinum' list of validated somatic sites from the cited study (reference 32)", cov="126.90/320.91"),
    "COLO": dict(key="colo829", short="COLO829 cell line", name="COLO829 metastatic melanoma cell line tumour-normal WGS with curated somatic calls",
                 assay="Cell line tumour-normal WGS (dbGaP phs000932; runs SRR3184219 and SRR3184215), downloaded BAMs; 82.94x normal, 92.82x tumour",
                 context="Cancer cell line; curated high-confidence somatic call set from the cited study (reference 33)", cov="82.94/92.82"),
    "MB": dict(key="mb", short="MB brain tumour", name="Malignant paediatric cerebellar brain tumour (MB) tumour-normal WGS with curated somatic calls",
               assay="Real tumour-normal WGS (EGAD00001001859), FASTQs from several centres concatenated, Novoalign v3.00.05 to hg19; 271.70x normal, 305.62x tumour",
               context="Real tumour; curated high-confidence somatic call set from the cited benchmark study (reference 31)", cov="271.70/305.62"),
}
SNV_ORDER = ["DREAM Set1", "DREAM Set2", "DREAM Set3", "DREAM Set4", "CLL", "AML", "MB", "COLO"]
INDEL_ORDER = ["DREAM Set3", "DREAM Set4", "CLL", "MB", "COLO"]

SNV_ROWS = ["MuSE ", "VarDict (bcbio)", "VarDict (standalone)", "LoFreq", "SomaticSniper ", "Strelka", "VarScan",
            "MuTect", "MuTect2", "4callers(voting>=3) ", "4callers(voting>=2) ", "7callers(voting>=4) ",
            "7callers(voting>=3) ", "NeuSomatic_Lowqual ", "NeuSomatic_Pass "]
INDEL_ROWS = ["VarDict (bcbio)", "VarDict (standalone)", "LoFreq ", "Strelka ", "VarScan ", "MuTect2 ",
              "3callers (>=2)", "3callers (>=1)", "5callers (>=3)", "5callers (>=2)", "NeuSomatic_Pass ",
              "NeuSomatic_Lowqual "]

VOTE_SNV4 = "LoFreq, MuSE, MuTect2 and Strelka"
VOTE_SNV7 = "LoFreq, MuSE, MuTect2, SomaticSniper, Strelka, VarDict and VarScan"
VOTE_IND3 = "LoFreq, MuTect2 and Strelka"
VOTE_IND5 = "LoFreq, MuTect2, Strelka, VarDict and VarScan"
NEU_PROTOCOL = ("Ensemble mode: Ensemble.tsv from SomaticSeq.Wrapper.sh over MuTect2, MuSE, Strelka, SomaticSniper, "
                "VarDict and VarScan VCFs, then prediction with model NeuSomatic_v0.1.3_ensemble_DREAM3.pth")
CALLER_SOURCE_LOC = "Methods, Somatic variant calling paragraph 1 and 2"

WCONF = {
    # label: (config key, display name, method key, version, protocol text, method_types)
    "MuSE": ("muse", "MuSE v1.0rc", "muse", "v1.0rc", "Option -G for WGS", ["conventional_pipeline"]),
    "VarDict (bcbio)": ("vardict-bcbio", "VarDict through bcbio-nextgen v1.1.5", "vardict",
                        "VarDict v1.6.0 run through bcbio-nextgen v1.1.5",
                        "WGS calling through bcbio-nextgen; the authors used this row for comparisons in the Results",
                        ["conventional_pipeline"]),
    "VarDict (standalone)": ("vardict-standalone", "VarDict v1.6.0 standalone", "vardict", "v1.6.0",
                             "Standalone package; var2vcf_paired.pl -P 0.9 -m 4.25 -f 0.01 -M with the bcbio filter expression",
                             ["conventional_pipeline"]),
    "LoFreq": ("lofreq", "LoFreq v2.1.3.1", "lofreq", "v2.1.3.1", "Default settings or author instructions",
               ["conventional_pipeline"]),
    "SomaticSniper": ("somaticsniper", "SomaticSniper v1.0.5.0", "somaticsniper", "v1.0.5.0",
                      "Default settings or author instructions", ["conventional_pipeline"]),
    "Strelka": ("strelka", "Strelka v2.7.1", "strelka", "v2.7.1", "Default settings or author instructions",
                ["conventional_pipeline"]),
    "VarScan": ("varscan", "VarScan v2.3.9", "varscan", "v2.3.9", "Somatic calling with the somatic post-processing steps",
                ["conventional_pipeline"]),
    "MuTect": ("mutect", "MuTect v1.1.7", "mutect", "v1.1.7", "dbSNP v138 and COSMIC v80 supplied for WGS",
               ["conventional_pipeline"]),
    "MuTect2": ("mutect2-gatk3-7", "MuTect2 (GATK v3.7-0)", "mutect2", "GATK v3.7-0",
                "dbSNP v138 and COSMIC v80 supplied for WGS", ["conventional_pipeline"]),
    "4callers(voting>=3)": ("vote-4callers-min3", "Majority vote, 4 SNV callers, at least 3 agree", "majority-vote", None,
                            f"Majority voting over {VOTE_SNV4}; a call needs at least 3 callers", ["conventional_pipeline"]),
    "4callers(voting>=2)": ("vote-4callers-min2", "Majority vote, 4 SNV callers, at least 2 agree", "majority-vote", None,
                            f"Majority voting over {VOTE_SNV4}; a call needs at least 2 callers", ["conventional_pipeline"]),
    "7callers(voting>=4)": ("vote-7callers-min4", "Majority vote, 7 SNV callers, at least 4 agree", "majority-vote", None,
                            f"Majority voting over {VOTE_SNV7}; a call needs at least 4 callers", ["conventional_pipeline"]),
    "7callers(voting>=3)": ("vote-7callers-min3", "Majority vote, 7 SNV callers, at least 3 agree", "majority-vote", None,
                            f"Majority voting over {VOTE_SNV7}; a call needs at least 3 callers", ["conventional_pipeline"]),
    "3callers (>=2)": ("vote-3callers-min2", "Majority vote, 3 indel callers, at least 2 agree", "majority-vote", None,
                       f"Majority voting over {VOTE_IND3}; a call needs at least 2 callers", ["conventional_pipeline"]),
    "3callers (>=1)": ("vote-3callers-min1", "Union of 3 indel callers (at least 1)", "majority-vote", None,
                       f"Voting over {VOTE_IND3}; a call needs at least 1 caller", ["conventional_pipeline"]),
    "5callers (>=3)": ("vote-5callers-min3", "Majority vote, 5 indel callers, at least 3 agree", "majority-vote", None,
                       f"Majority voting over {VOTE_IND5}; a call needs at least 3 callers", ["conventional_pipeline"]),
    "5callers (>=2)": ("vote-5callers-min2", "Majority vote, 5 indel callers, at least 2 agree", "majority-vote", None,
                       f"Voting over {VOTE_IND5}; a call needs at least 2 callers", ["conventional_pipeline"]),
    "NeuSomatic_Lowqual": ("neusomatic-lowqual", "NeuSomatic v0.2.1 ensemble mode, DREAM3 model, all calls",
                           "neusomatic", "v0.2.1; model NeuSomatic_v0.1.3_ensemble_DREAM3.pth",
                           NEU_PROTOCOL + "; row NeuSomatic_Lowqual (read here as calls including those flagged low quality; the label is not defined in the source)",
                           ["supervised_machine_learning"]),
    "NeuSomatic_Pass": ("neusomatic-pass", "NeuSomatic v0.2.1 ensemble mode, DREAM3 model, PASS calls",
                        "neusomatic", "v0.2.1; model NeuSomatic_v0.1.3_ensemble_DREAM3.pth",
                        NEU_PROTOCOL + "; row NeuSomatic_Pass (read here as PASS-filtered calls; the label is not defined in the source)",
                        ["supervised_machine_learning"]),
}
METHOD_INFO = {
    "muse": ("MuSE", "Somatic point mutation caller using a Markov substitution model with a sample-specific error model.", "MuSE"),
    "vardict": ("VarDict", "Variant caller for tumour-normal and single-sample data.", "VarDict"),
    "lofreq": ("LoFreq", "Low-frequency variant caller with a somatic mode.", "LoFreq"),
    "somaticsniper": ("SomaticSniper", "Somatic point mutation caller.", "SomaticSniper"),
    "strelka": ("Strelka", "Illumina small-variant caller with a tumour-normal somatic mode (cited versions 2.7.1 and 2.9.2).", "Strelka"),
    "varscan": ("VarScan", "Heuristic somatic and germline variant caller (VarScan 2 releases).", "VarScan"),
    "mutect": ("MuTect", "Broad Institute somatic point mutation caller (version 1).", "MuTect"),
    "mutect2": ("Mutect2", "GATK somatic SNV and indel caller using local assembly.", "MuTect2"),
    "majority-vote": ("Majority-vote consensus of somatic callers",
                      "Ensemble that keeps a variant when at least a set number of the listed callers report it.",
                      "majority voting"),
    "neusomatic": ("NeuSomatic", "Convolutional neural network somatic SNV and indel caller.", "NeuSomatic"),
}
CONFIG_IDS = {}


def wang_config(label):
    ckey, name, mkey, version, protocol, mtypes = WCONF[label]
    cid = f"{P}-config-wang2020-{ckey}"
    if cid in CONFIG_IDS:
        return cid
    mname, mdesc, mreported = METHOD_INFO[mkey]
    mid = method(mkey, mname, mdesc, mreported, mtypes, W_SRC)
    attrs = {"reported_name": label, "protocol": protocol, "foundation_model_eligible": False,
             "source_locator": f"{CALLER_SOURCE_LOC}; Table S1/S2 row label '{label}'"}
    missing = {}
    if version:
        attrs["version"] = version
    else:
        missing["version"] = {"reason": "inapplicable", "note": "Ensemble of the listed caller versions; no separate version"}
    if mkey == "majority-vote":
        attrs["method_role"] = "Authors' own consensus approach evaluated alongside the individual callers"
    if missing:
        attrs["missing_metadata"] = missing
    rec(cid, "configuration", f"{name} (Wang et al. 2020)", f"{label} as run in the cited comparison.", W_SRC,
        [{"relation": "configuration_of", "target_id": mid}], attrs,
        facets={**FACETS, "method_types": mtypes})
    CONFIG_IDS[cid] = label
    return cid


def wang_dataset(label):
    d = DATASETS[label]
    did = f"{P}-data-wang2020-{d['key']}"
    if any(r["id"] == did for r in records):
        return did
    snv, indel = TABLE1[label]
    attrs = {"assay": d["assay"], "context": d["context"],
             "split": "Single tumour-normal pair; whole dataset evaluated",
             "population": f"Truth: {snv} SNVs" + (f", {indel} indels" if indel else "; no high-confidence indel set"),
             "source_locator": "Table 1; Results 'Datasets for evaluation'; Methods 'Data collection' and 'Primary analysis'",
             "missing_metadata": {"version": {"reason": "unreported", "note": "Truth-set release version not stated beyond the cited studies and download locations"}}}
    if label.startswith("DREAM"):
        attrs["accession"] = "Synapse syn312572 (BAMs) and syn2177211 (truth sets)"
    rec(did, "dataset", d["name"], "Benchmark tumour-normal pair and truth set used in Wang et al. 2020.", W_SRC, [], attrs)
    return did


def cell(sheet, ref):
    return sheet.get(ref)


def wang_table(sheet, sheet_name, order, rows, vt):
    vt_label = {"snv": "SNVs", "indel": "indels"}[vt]
    qual = {"snv": "snv only", "indel": "indel only"}[vt]
    r = 4
    for di, ds in enumerate(order):
        assert cell(sheet, f"A{r}").strip() == ds, (sheet_name, r, cell(sheet, f"A{r}"))
        truth = cell(sheet, f"B{r}")
        expect = TABLE1[ds][0 if vt == "snv" else 1]
        assert truth == expect, (ds, truth, expect)
        did = wang_dataset(ds)
        d = DATASETS[ds]
        pid = f"{P}-protocol-wang2020-{d['key']}-{vt}"
        synthetic = ds.startswith("DREAM")
        limitations = [
            "Single tumour-normal pair; no replicate or interval estimates.",
            "Truth set completeness is unclear, especially for low-VAF sites (Results 'Datasets for evaluation'); precision against an incomplete truth set is a lower bound." if not synthetic
            else "Synthetic tumour made by spiking simulated mutations into real reads; may not reproduce real tumour artefacts.",
            "Caller versions are those listed in Methods (for example MuTect2 from GATK v3.7-0, Strelka v2.7.1); later releases may behave differently.",
        ]
        if ds == "DREAM Set3":
            limitations.append("The NeuSomatic model used (NeuSomatic_v0.1.3_ensemble_DREAM3.pth) is named for DREAM stage 3, so the NeuSomatic rows on this dataset may not be held out.")
        rec(pid, "protocol", f"{d['short']} somatic {vt_label}, WGS (Wang et al. 2020 Table {'S1' if vt == 'snv' else 'S2'})",
            f"Per-caller recall, precision and F1 for somatic {vt_label} on one WGS tumour-normal pair.", W_SRC,
            [{"relation": "uses_data", "target_id": did}],
            {"protocol": ("Callers run on the tumour-normal pair with default settings or author instructions; calls compared "
                          "with the truth set by the DREAM challenge evaluator.py. Recall = detected true variants / true variants; "
                          "precision = detected true variants / all calls."),
             "version": f"Supplementary {sheet_name}, dataset '{ds}'",
             "metric_implementation": "evaluator.py from Sage-Bionetworks/ICGC-TCGA-DREAM-Mutation-Calling-challenge-tools (commit not stated)",
             "denominator": int(truth), "limitations": limitations,
             "source_locator": f"Supplementary Tables workbook sheet '{sheet_name}', rows for dataset '{ds}'; Methods 'Variant calling comparisons'"})
        for k, label in enumerate(rows):
            rr = r + k
            got = cell(sheet, f"C{rr}")
            assert got == label, (sheet_name, rr, got, label)
            if k > 0:
                assert cell(sheet, f"A{rr}") is None and cell(sheet, f"B{rr}") is None, (sheet_name, rr)
            clabel = label.strip()
            cid = wang_config(clabel)
            ckey = WCONF[clabel][0]
            eid = f"{P}-eval-wang2020-{ckey}-{d['key']}-{vt}"
            is_vote = WCONF[clabel][2] == "majority-vote"
            evaluation(eid, f"{clabel} on {ds} {vt_label} (Wang et al. 2020)", cid, pid, did, W_SRC,
                       "author_reported" if is_vote else "independent_paper",
                       {"dataset_version": None, "split": "Single tumour-normal pair",
                        "population": f"{truth} truth {vt_label}",
                        "inputs": f"Tumour-normal WGS, {d['cov']}x normal/tumour",
                        "adaptation": None,
                        "metric_implementation": "DREAM challenge evaluator.py",
                        "aggregation": "Pooled over the whole genome of one pair", "budget": None},
                       f"Supplementary Tables workbook sheet '{sheet_name}', row {rr} (dataset '{ds}', caller '{clabel}')",
                       missing={"comparison.dataset_version": {"reason": "unreported"}})
            for col, metric in (("D", "count"), ("E", "recall"), ("F", "precision"), ("G", "f1")):
                raw = cell(sheet, f"{col}{rr}")
                assert raw is not None and re.fullmatch(r"[0-9.E+-]+", raw), (sheet_name, col, rr, raw)
                header = HEAD[f"{col}3"].strip()
                result(f"{P}-result-wang2020-{ckey}-{d['key']}-{vt}-{METRIC[metric]['metric']}", eid, W_SRC, W_SHA,
                       W_TAB_URL,
                       f"Supplementary Tables workbook sheet '{sheet_name}', {col}{rr}; dataset '{ds}'; caller '{clabel}'; column '{header}'",
                       raw, metric, qual, W_HOW)
        # Judgement
        locs = [(W_TAB, f"Sheet '{sheet_name}', rows {r}-{r + len(rows) - 1}"),
                (W_ART, "Table 1; Methods 'Data collection', 'Somatic variant calling' and 'Variant calling comparisons'")]
        if synthetic:
            rationale = (f"Simulated tumour-normal WGS from the DREAM challenge with a known spike-in truth set; directly measures "
                         f"somatic {vt_label[:-1]} detection by individual callers and consensus approaches on one pair.")
        else:
            rationale = (f"Real tumour-normal WGS scored against a curated high-confidence somatic call set; directly measures "
                         f"somatic {vt_label[:-1]} detection by individual callers and consensus approaches, with truth completeness unknown.")
        judgement(f"wang2020-{d['key']}-{vt}", pid, f"{ds} somatic {vt_label} WGS (Wang et al. 2020)", W_SRC, "direct",
                  f"Recall, precision, F1 and call count for somatic {vt_label} on {ds} WGS for "
                  f"{len(rows)} caller and consensus configurations",
                  rationale,
                  ["Inspect every linked evaluation's source locator before citing a result.",
                   "Do not combine this mapping's evaluations with any other protocol's results; truth sets, inputs and caller versions differ between sources."],
                  limitations, locs,
                  f"wang2020-wgs-{vt}", f"WGS somatic {vt_label} by dataset (Wang et al. 2020)", "f1-score",
                  stratum=ds.replace("COLO", "COLO829"), order=di + 1)
        r += len(rows)
    assert cell(sheet, f"A{r}") is None and cell(sheet, f"C{r}") is None, (sheet_name, "extra rows", r)
    assert not any(int(re.match(r"[A-Z]+(\d+)", k).group(1)) >= r for k in sheet), (sheet_name, "cells beyond table")


wang_table(S1, "S1 WGS SNVs", SNV_ORDER, SNV_ROWS, "snv")
wang_table(S2, "S2 WGS INDELs", INDEL_ORDER, INDEL_ROWS, "indel")

rec(f"{P}-claim-wang2020-neusomatic-dream3-model", "claim", "training_overlap: NeuSomatic configurations (Wang et al. 2020)",
    "Descriptive fact transcribed from the pinned source.", W_SRC,
    [{"relation": "subject", "target_id": f"{P}-config-wang2020-neusomatic-pass"}],
    {"field": "training_overlap",
     "value": "NeuSomatic v0.2.1 was run in ensemble mode with the pretrained model NeuSomatic_v0.1.3_ensemble_DREAM3.pth on the WGS datasets, which include DREAM set 3.",
     "source_locator": "Methods, Somatic variant calling paragraph 2; Table 1",
     "review": review_note("Hand transcription from the article XML text.")}, facets={})
claims_rows.append([f"{P}-claim-wang2020-neusomatic-dream3-model", W_ART, "Methods, Somatic variant calling paragraph 2; Table 1",
                    "NeuSomatic v0.2.1 ensemble mode with model NeuSomatic_v0.1.3_ensemble_DREAM3.pth on WGS datasets including DREAM set 3", "claim"])



# ---------------------------------------------------------------------------------------------
# Guille et al. 2025, Brief Bioinform 26(1):bbae697, Supplementary Table S7 (validation sample)
# ---------------------------------------------------------------------------------------------

G_ART = f"{P}-source-guille2025"
G_S7 = f"{P}-source-guille2025-table-s7"
G_SM = f"{P}-source-guille2025-supplementary-methods"
G_SRC = [G_ART, G_S7]
G_ART_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11790059/fullTextXML"
G_SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11790059/supplementaryFiles"
G_SHA = ARTIFACTS["guille2025-table-s7.xls"]
G_HOW = ("Extracted by deterministic parse of the pinned legacy XLS (BIFF8) workbook with a standard-library "
         "reader (extract/rawxls.py, called by extract/extract_somatic.py), with the title, column headers, row "
         "labels, vote counts, categories and variant types asserted. printed_value is the shortest round-trip "
         "decimal of the stored double; raw_xml_value keeps that stored value as text (the file is BIFF, not XML). "
         "Spreadsheet display formatting was not applied.")
SUPP_NOTE = ("Retrieved as one member of the Europe PMC supplementaryFiles zip. The zip is assembled per request "
             "(member timestamps equal the request time), so only the member file hash is pinned.")

rec(G_ART, "source",
    "A benchmarking study of individual somatic variant callers and voting-based ensembles for whole-exome sequencing",
    "Primary source retrieved and hashed for the tumour somatic SNV and indel use-case pass.", [], [],
    {"url": "https://doi.org/10.1093/bib/bbae697", "artifact_url": G_ART_URL,
     "version": "Briefings in Bioinformatics 26(1):bbae697, published online 2025-01-18; PMC11790059 full-text XML",
     "retrieved_at": "2026-10-09T19:56:52Z", "artifact_sha256": ARTIFACTS["guille2025-article.xml"],
     "doi": "10.1093/bib/bbae697", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/xml"})
rec(G_S7, "source", "Guille et al. 2025, Supplementary Table S7 (validation dataset)",
    "Per-caller and retained-ensemble performance on the SEQC2 validation sample.", [], [],
    {"url": "https://doi.org/10.1093/bib/bbae697", "artifact_url": G_SUPP_URL,
     "version": "tables7_bbae697.xls inside the Europe PMC supplementary files bundle for PMC11790059",
     "retrieved_at": "2026-10-09T20:08:20Z", "artifact_sha256": G_SHA, "artifact_member": "tables7_bbae697.xls",
     "hash_scope": "SHA-256 of tables7_bbae697.xls. " + SUPP_NOTE,
     "doi": "10.1093/bib/bbae697", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/vnd.ms-excel"})
rec(G_SM, "source", "Guille et al. 2025, supplementary methods (caller command lines)",
    "Command lines and parameters used for each caller.", [], [],
    {"url": "https://doi.org/10.1093/bib/bbae697", "artifact_url": G_SUPP_URL,
     "version": "supplementary_methods_bbae697.docx inside the Europe PMC supplementary files bundle for PMC11790059",
     "retrieved_at": "2026-10-09T20:08:20Z", "artifact_sha256": ARTIFACTS["guille2025-supplementary-methods.docx"],
     "artifact_member": "supplementary_methods_bbae697.docx",
     "hash_scope": "SHA-256 of supplementary_methods_bbae697.docx. " + SUPP_NOTE,
     "doi": "10.1093/bib/bbae697", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"})

# Article Table 1: caller, version, link and licence footnote
art = ET.parse(os.path.join(DL, "guille2025-article.xml"))
tx = lambda e: " ".join(" ".join(e.itertext()).split())
tb1 = next(t for t in art.iter("table-wrap") if t.get("id") == "TB1")
rows = [[tx(c) for c in tr if c.tag in ("td", "th")] for tr in tb1.iter("tr")]
assert rows[0] == ["Type of algorithm", "Variant caller", "Version", "Type of variant", "Keep for ensemble", "Link", "Ref"], rows[0]
TB1 = {r[1]: dict(algorithm=r[0], version=r[2], variant_type=r[3], link=r[5]) for r in rows[1:]}
assert len(TB1) == 20 and tx(tb1.find("table-wrap-foot")) == "a Commercial license (trial version)", tx(tb1.find("table-wrap-foot"))
# Article Table 2: the SEQC2-FD validation sample
tb2 = next(t for t in art.iter("table-wrap") if t.get("id") == "TB2")
rows2 = [[tx(c) for c in tr if c.tag in ("td", "th")] for tr in tb2.iter("tr")]
FD = next(r for r in rows2 if r[0] == "SEQC2-FD")
assert FD == ["SEQC2-FD", "Illumina HiSeq 4000", "HCC1395 (WES_FD_T_1)", "https://www.ncbi.nlm.nih.gov/sra/SRX4728489",
              "1160", "50", "76x", "23.49", "4.73E−03", "6.67E−04"], FD
# Supplementary methods: NeuSomatic checkpoint and DeepSomatic model type, asserted from the docx text
docx = zipfile.ZipFile(os.path.join(DL, "guille2025-supplementary-methods.docx")).read("word/document.xml").decode()
paras = ["".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).strip() for p in re.findall(r"<w:p[ >].*?</w:p>", docx, flags=re.S)]
assert "--checkpoint /opt/neusomatic/neusomatic/models/NeuSomatic_v0.1.4_standalone_SEQC-WGS-GT50-SpikeWGS10.pth \\" in paras
assert "--model_type=WGS \\" in paras
assert "configureStrelkaSomaticWorkflow.py –exome \\" in paras

GT = {
    # S7 label: (Table 1 caller name, method key, config key, method types)
    "FreeBayes": ("FreeBayes", "freebayes", "freebayes", ["conventional_pipeline"]),
    "Lofreq": ("Lofreq", "lofreq", "lofreq", ["conventional_pipeline"]),
    "Muse": ("Muse", "muse", "muse", ["conventional_pipeline"]),
    "Mutect": ("Mutect", "mutect", "mutect", ["conventional_pipeline"]),
    "Mutect2": ("Mutect2", "mutect2", "mutect2", ["conventional_pipeline"]),
    "SomaticSniper": ("SomaticSniper", "somaticsniper", "somaticsniper", ["conventional_pipeline"]),
    "Strelka": ("Strelka", "strelka", "strelka", ["conventional_pipeline"]),
    "Vardict": ("Vardict", "vardict", "vardict", ["conventional_pipeline"]),
    "Varscan2": ("Varscan2", "varscan", "varscan2", ["conventional_pipeline"]),
    "Seurat": ("Seurat", "seurat", "seurat", ["conventional_pipeline"]),
    "Lancet": ("Lancet", "lancet", "lancet", ["conventional_pipeline"]),
    "Shimmer": ("Shimmer", "shimmer", "shimmer", ["conventional_pipeline"]),
    "Virmid": ("Virmid", "virmid", "virmid", ["conventional_pipeline"]),
    "Pindel": ("Pindel", "pindel", "pindel", ["conventional_pipeline"]),
    "Scalpel": ("Scalpel", "scalpel", "scalpel", ["conventional_pipeline"]),
    "DeepSomatic-WES": ("DeepSomatic", "deepsomatic", "deepsomatic", ["supervised_machine_learning"]),
    "NeuSomatic": ("NeuSomatic", "neusomatic", "neusomatic", ["supervised_machine_learning"]),
    "VarNet": ("VarNet", "varnet", "varnet", ["supervised_machine_learning"]),
}
METHOD_INFO.update({
    "freebayes": ("FreeBayes", "Haplotype-based variant caller, used here with tumour-normal filtering.", "FreeBayes"),
    "seurat": ("Seurat (TGen somatic caller)", "Somatic variant caller from TGen.", "Seurat"),
    "lancet": ("Lancet", "Somatic SNV and indel caller using localised colored de Bruijn graphs.", "Lancet"),
    "shimmer": ("Shimmer", "Somatic SNV caller for matched tumour-normal pairs.", "Shimmer"),
    "virmid": ("Virmid", "Somatic SNV caller that estimates normal contamination of the tumour sample.", "Virmid"),
    "pindel": ("Pindel", "Pattern-growth indel caller, used here with tumour-normal filtering.", "Pindel"),
    "scalpel": ("Scalpel", "Micro-assembly indel caller with a somatic mode.", "Scalpel"),
    "deepsomatic": ("DeepSomatic", "Deep-learning somatic small-variant caller built on DeepVariant.", "DeepSomatic"),
    "varnet": ("VarNet", "Deep-learning somatic SNV and indel caller.", "VarNet"),
})
G_CONF = {}


def guille_config(label):
    t1, mkey, ckey, mtypes = GT[label]
    info = TB1[t1]
    cid = f"{P}-config-guille2025-{ckey}"
    if cid in G_CONF:
        return cid
    mname, mdesc, mreported = METHOD_INFO[mkey]
    access = f"Download location listed in Guille et al. 2025 Table 1: {info['link']}"
    mid = method(mkey, mname, mdesc, mreported, mtypes, [G_ART], extra={"access": access})
    if "access" not in METHODS[mid]["attributes"]:
        METHODS[mid]["attributes"]["access"] = access
    if G_ART not in METHODS[mid]["source_ids"]:
        METHODS[mid]["source_ids"].append(G_ART)
    protocol = (f"Paired tumour-normal WES calling restricted to target regions; command line and parameters in the "
                f"supplementary methods (section '#{ {'DeepSomatic': 'DeepSomatic', 'Vardict': 'VarDict', 'Lofreq': 'LoFreq'}.get(t1, t1) }')")
    attrs = {"reported_name": label, "version": info["version"], "protocol": protocol,
             "foundation_model_eligible": False,
             "source_locator": f"Table 1 row '{t1}'; Supplementary Table S7 row label '{label}'; supplementary methods"}
    if label == "DeepSomatic-WES":
        attrs["model_identity_note"] = ("Table S7 labels the row 'DeepSomatic-WES', but the supplementary methods command "
                                        "uses --model_type=WGS. Which model produced the Table S7 values is not resolved.")
    if label == "NeuSomatic":
        attrs["checkpoint"] = "NeuSomatic_v0.1.4_standalone_SEQC-WGS-GT50-SpikeWGS10.pth"
        attrs["training_overlap"] = ("The checkpoint named in the supplementary methods is a SEQC2 HCC1395 WGS model; the "
                                     "validation sample is HCC1395 WES, so the evaluation may not be held out.")
    if label == "Strelka":
        attrs["model_identity_note"] = "Table 1 prints 'Strelka' version 2.9.2; command configureStrelkaSomaticWorkflow.py --exome."
    rec(cid, "configuration", f"{label} {info['version']} (Guille et al. 2025)", f"{label} as run in the cited comparison.",
        [G_ART, G_SM, G_S7], [{"relation": "configuration_of", "target_id": mid}], attrs,
        facets={**FACETS, "method_types": mtypes})
    G_CONF[cid] = label
    return cid


ENSEMBLES = {
    "Lofreq-Muse-Mutect2-SomaticSniper-Strelka-Lancet": ("vote-6snv-min3", "3", "6", "Best-Comb-SNV"),
    "Muse-Mutect2-Strelka": ("vote-3snv-min2", "2", "3", "Comb-Cost-Effective"),
    "Mutect2-Strelka-Pindel-Varscan2": ("vote-4indel-min2", "2", "4", "Best-Comb-INDEL"),
    "Mutect2-Strelka-Varscan2": ("vote-3indel-min2", "2", "3", "Comb-Cost-Effective"),
}


def guille_ensemble(label):
    ckey, votes, ntools, categ = ENSEMBLES[label]
    cid = f"{P}-config-guille2025-{ckey}"
    if cid in G_CONF:
        return cid
    mid = method("majority-vote", *METHOD_INFO["majority-vote"], ["conventional_pipeline"], [G_ART])
    if G_ART not in METHODS[mid]["source_ids"]:
        METHODS[mid]["source_ids"].append(G_ART)
    members = label.split("-")
    rec(cid, "configuration", f"Vote ensemble {', '.join(members)}, at least {votes} agree (Guille et al. 2025)",
        f"Voting ensemble '{label}' retained by the authors ({categ}).", [G_ART, G_S7],
        [{"relation": "configuration_of", "target_id": mid}],
        {"reported_name": label, "foundation_model_eligible": False,
         "protocol": f"A variant is called when at least {votes} of the {ntools} member callers report it; member caller versions as in Table 1",
         "method_role": "Authors' own retained ensemble, selected on the four development datasets and then applied to the validation sample",
         "selection": f"Table S7 category '{categ}'",
         "source_locator": f"Supplementary Table S7 row '{label}'; Results 'Evaluation of the ensemble approach' and 'Validation'",
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Ensemble of the listed caller versions"}}},
        facets={**FACETS, "method_types": ["conventional_pipeline"]})
    G_CONF[cid] = label
    return cid


S7 = rawxls.read(os.path.join(DL, "guille2025-table-s7.xls"))
assert list(S7) == ["Results"], list(S7)
S7 = S7["Results"]
assert S7["A1"] == "Table S7. Performance of individual somatic variant callers and retained best combinations in the validation dataset", S7["A1"]
G_HEAD = ["Tools", "Nb_Vote", "P", "TP", "FP", "TPR", "FPR", "F1", "PPV", "Nb_Tools", "Categ", "Type of variant "]
for i, h in enumerate(G_HEAD):
    assert S7[f"{'ABCDEFGHIJKL'[i]}3"] == h, (i, S7[f"{'ABCDEFGHIJKL'[i]}3"])
SNV_LABELS = ["FreeBayes", "Lofreq", "Muse", "Mutect", "Mutect2", "SomaticSniper", "Strelka", "Vardict", "Varscan2",
              "Seurat", "Lancet", "Shimmer", "Virmid", "DeepSomatic-WES", "NeuSomatic", "VarNet",
              "Lofreq-Muse-Mutect2-SomaticSniper-Strelka-Lancet", "Muse-Mutect2-Strelka"]
INDEL_LABELS = ["FreeBayes", "Lofreq", "Mutect2", "Strelka", "Vardict", "Pindel", "Scalpel", "Varscan2", "Seurat",
                "Lancet", "DeepSomatic-WES", "NeuSomatic", "VarNet", "Mutect2-Strelka-Pindel-Varscan2",
                "Mutect2-Strelka-Varscan2"]
G_METRICS = [("D", "tp"), ("E", "fp"), ("F", "recall"), ("G", "fpr"), ("H", "f1"), ("I", "precision")]
METRIC.update({
    "tp": dict(metric="true-positive-count", metric_direction="higher", unit="count",
               unit_detail="counted entity: truth-set variants detected"),
    "fp": dict(metric="false-positive-count", metric_direction="lower", unit="count",
               unit_detail="counted entity: calls not in the truth set"),
    "fpr": dict(metric="false-positive-rate", metric_direction="lower", unit="fraction"),
})
G_COLNAME = {"D": "TP", "E": "FP", "F": "TPR", "G": "FPR", "H": "F1", "I": "PPV"}

gdid = f"{P}-data-guille2025-seqc2-fd-wes"
rec(gdid, "dataset", "SEQC2 HCC1395/HCC1395BL WES, Fudan replicate (WES_FD_T_1), high-confidence regions",
    "Validation sample in Guille et al. 2025.", [G_ART],
    [], {"assay": "WES, Illumina HiSeq 4000 per Table 2 (Methods: 76x sample from a different platform, Fudan University); 76x; duplication rate 23.49%",
         "accession": "SRA SRX4728489 (Table 2); Methods name run SRR7890879",
         "context": "HCC1395 triple-negative breast cancer cell line with HCC1395BL matched normal; SEQC2 high-confidence somatic call set restricted to high-confidence regions",
         "population": "Truth: 1160 SNVs and 50 indels (Table 2; Table S7 column P)",
         "split": "Held-out validation sample; not used to select the ensembles",
         "source_locator": "Table 2 row 'SEQC2-FD'; Methods 'SEQC2 dataset'",
         "missing_metadata": {"version": {"reason": "unreported", "note": "Methods point to the SEQC2 'release/latest' folder; the call-set version is not printed"},
                              "population_detail": {"reason": "unreported", "note": "Matched normal run for the validation sample and the post-alignment procedure used for Table S7 are not stated"}}})

g_order = 0
r = 4
for vt, labels, truth in (("snv", SNV_LABELS, "1160"), ("indel", INDEL_LABELS, "50")):
    vt_label = {"snv": "SNVs", "indel": "indels"}[vt]
    qual = {"snv": "snv only", "indel": "indel only"}[vt]
    g_order += 1
    pid = f"{P}-protocol-guille2025-seqc2-fd-wes-{vt}"
    lims = ["Single WES sample of one cell line; no replicate or interval estimates.",
            f"Small truth set ({truth} {vt_label}) in high-confidence regions." if vt == "indel" else
            "Truth limited to SEQC2 high-confidence regions within the exome.",
            "Ensembles were chosen on the four development datasets by the same authors; the individual callers were not tuned on this sample.",
            "Post-alignment procedure for Table S7 is not stated (Table S1-S2 compare four procedures on the development datasets).",
            "NeuSomatic used a SEQC2 HCC1395 WGS checkpoint (supplementary methods), so its row may not be held out."]
    rec(pid, "protocol", f"SEQC2 HCC1395 WES validation sample, somatic {vt_label} (Guille et al. 2025 Table S7)",
        f"Per-caller and retained-ensemble TP, FP, recall, false-positive rate, precision and F1 for somatic {vt_label}.",
        [G_ART, G_S7], [{"relation": "uses_data", "target_id": gdid}],
        {"protocol": ("bwa mem alignment, callers run in paired tumour-normal mode on target regions, calls compared with "
                      "the SEQC2 truth set in high-confidence regions. TPR = TP/(TP+FN), PPV = TP/(TP+FP), F1 = 2TP/(2TP+FP+FN)."),
         "version": f"Supplementary Table S7, Type of variant '{'SNV' if vt == 'snv' else 'INDEL'}'",
         "denominator": int(truth), "limitations": lims,
         "missing_metadata": {"metric_implementation": {"reason": "unreported", "note": "Comparison tool for matching calls to the truth set is not named; FPR denominator is not defined"}},
         "source_locator": "Supplementary Table S7; Methods 'Evaluation and metrics' and 'SEQC2 dataset'"})
    first = r
    for label in labels:
        assert S7[f"A{r}"] == label, (r, S7[f"A{r}"], label)
        assert S7[f"C{r}"] == truth, (r, S7[f"C{r}"])
        assert S7[f"L{r}"] == ("SNV" if vt == "snv" else "INDEL"), (r, S7[f"L{r}"])
        if label in ENSEMBLES:
            ckey, votes, ntools, categ = ENSEMBLES[label]
            assert (S7[f"B{r}"], S7[f"J{r}"], S7[f"K{r}"]) == (votes, ntools, categ), (r, S7[f"B{r}"], S7[f"J{r}"], S7[f"K{r}"])
            cid = guille_ensemble(label)
            origin = "author_reported"
        else:
            cat = "Neural Network" if GT[label][3] == ["supervised_machine_learning"] else "Classic"
            assert (S7[f"B{r}"], S7[f"J{r}"], S7[f"K{r}"]) == ("NA", "1", cat), (r, S7[f"B{r}"], S7[f"J{r}"], S7[f"K{r}"])
            cid = guille_config(label)
            ckey = GT[label][2]
            origin = "independent_paper"
        eid = f"{P}-eval-guille2025-{ckey}-seqc2-fd-wes-{vt}"
        evaluation(eid, f"{label} on SEQC2 HCC1395 WES validation {vt_label} (Guille et al. 2025)", cid, pid, gdid,
                   [G_ART, G_S7], origin,
                   {"dataset_version": None, "split": "Held-out validation sample",
                    "population": f"{truth} truth {vt_label} in high-confidence regions",
                    "inputs": "Tumour-normal WES, 76x tumour (Table 2), bwa mem alignment",
                    "adaptation": None, "metric_implementation": None,
                    "aggregation": "Pooled over the target regions of one pair", "budget": None},
                   f"Supplementary Table S7 row {r} (Tools '{label}', Type of variant '{S7[f'L{r}']}')",
                   missing={"comparison.dataset_version": {"reason": "unreported"},
                            "comparison.metric_implementation": {"reason": "unreported"}})
        for col, metric in G_METRICS:
            raw = S7[f"{col}{r}"]
            assert re.fullmatch(r"[0-9.e+-]+", raw), (col, r, raw)
            result(f"{P}-result-guille2025-{ckey}-seqc2-fd-wes-{vt}-{METRIC[metric]['metric']}", eid, [G_ART, G_S7], G_SHA,
                   G_SUPP_URL,
                   f"Supplementary Table S7 (tables7_bbae697.xls, sheet 'Results'), {col}{r}; Tools '{label}'; column '{G_COLNAME[col]}'",
                   raw, metric, qual, G_HOW)
        r += 1
    locs = [(G_S7, f"Sheet 'Results', rows {first}-{r - 1}"),
            (G_ART, "Table 1; Table 2 row 'SEQC2-FD'; Methods 'SEQC2 dataset' and 'Evaluation and metrics'; Results 'Validation'"),
            (G_SM, "Command lines per caller")]
    judgement(f"guille2025-seqc2-fd-wes-{vt}", pid, f"SEQC2 HCC1395 WES validation somatic {vt_label} (Guille et al. 2025)",
              [G_ART, G_S7, G_SM], "direct",
              f"TP, FP, recall, false-positive rate, precision and F1 for somatic {vt_label} on a held-out SEQC2 HCC1395 WES "
              f"sample for {len(labels) - 2} individual callers and 2 retained voting ensembles",
              (f"A real tumour-normal cell-line WES pair scored against the SEQC2 high-confidence somatic call set; directly "
               f"measures somatic {vt_label[:-1]} detection by classic and deep-learning callers and two voting ensembles, run "
               f"by an academic group that did not develop the individual callers."),
              ["Inspect every linked evaluation's source locator before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; truth sets, inputs and caller versions differ between sources.",
               "The ensemble rows were selected by the authors on other datasets; treat them as the authors' own method."],
              lims, locs, "guille2025-seqc2-fd-wes", "SEQC2 HCC1395 WES validation sample (Guille et al. 2025)", "f1-score",
              stratum=vt_label.capitalize(), order=g_order)
assert all(int(re.match(r"[A-Z]+(\d+)", k).group(1)) < r for k in S7), "cells beyond the table"

rec(f"{P}-claim-guille2025-neusomatic-checkpoint", "claim", "training_overlap: NeuSomatic configuration (Guille et al. 2025)",
    "Descriptive fact transcribed from the pinned source.", [G_SM],
    [{"relation": "subject", "target_id": f"{P}-config-guille2025-neusomatic"}],
    {"field": "checkpoint",
     "value": "NeuSomatic was called with --checkpoint NeuSomatic_v0.1.4_standalone_SEQC-WGS-GT50-SpikeWGS10.pth.",
     "source_locator": "Supplementary methods, section '#NeuSomatic', call.py command",
     "review": review_note("Hand transcription from the supplementary methods DOCX text.")}, facets={})
claims_rows.append([f"{P}-claim-guille2025-neusomatic-checkpoint", G_SM, "Supplementary methods, section '#NeuSomatic', call.py command",
                    "--checkpoint NeuSomatic_v0.1.4_standalone_SEQC-WGS-GT50-SpikeWGS10.pth", "claim"])
rec(f"{P}-claim-guille2025-deepsomatic-model-type", "claim", "model_type: DeepSomatic configuration (Guille et al. 2025)",
    "Descriptive fact transcribed from the pinned source.", [G_SM, G_S7],
    [{"relation": "subject", "target_id": f"{P}-config-guille2025-deepsomatic"}],
    {"field": "model_type",
     "value": "The supplementary methods run run_deepsomatic with --model_type=WGS, while Table S7 labels the row DeepSomatic-WES.",
     "source_locator": "Supplementary methods, section '#DeepSomatic'; Supplementary Table S7 rows 17 and 32",
     "review": review_note("Hand transcription from the supplementary methods DOCX text and the Table S7 row labels.")}, facets={})
claims_rows.append([f"{P}-claim-guille2025-deepsomatic-model-type", G_SM, "Supplementary methods, section '#DeepSomatic'; Supplementary Table S7 rows 17 and 32",
                    "--model_type=WGS; row label DeepSomatic-WES", "claim"])

# ---------------------------------------------------------------------------------------------
os.makedirs(BATCH, exist_ok=True)
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), "duplicate ids"
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
