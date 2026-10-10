"""Deterministic extraction of the SEQC2 whole-genome F1 tables of Sahraeian et al. 2022 (NeuSomatic) into a records batch.

Usage: python3 -I extract_neusomatic.py <pinned-dir> <batch-dir>

<pinned-dir> holds the pinned artifacts named in ARTIFACTS. The script checks each SHA-256 and reads Additional file 2
Tables S2, S3 and S4 from `pdftotext -bbox` word boxes (poppler; pdftables.py next to this script). The rotated column
headers are matched to columns by position, and every printed Average row is checked against the mean of its column.
It writes batch.jsonl and claims.csv in the current store shape. Nothing is marked reviewed.
"""
import csv, hashlib, json, os, re, subprocess, sys
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdftables  # noqa: E402

PINNED, BATCH = sys.argv[1], sys.argv[2]
P = "somatic-neusomatic-20261010"
UC = "use-case-tumour-dna-somatic-variant-detection"
UC_NAME = "Select a tumour DNA somatic variant-calling workflow"
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
TODAY = "2026-10-10"
ARTIFACTS = {
    "sahraeian2022-article.xml": "78dbe540c2558585bc7537e0e6563706fdaa329b2708e5dc82b77074379b4a6e",
    "sahraeian2022-additional-file-2.pdf": "10a109d80f6f49446ea84bd9f7f6b31c20d634516c8666376ac8a8f51f3236d0",
}
records, claims_rows, judgements = [], [], []
for name, digest in ARTIFACTS.items():
    got = hashlib.sha256(open(os.path.join(PINNED, name), "rb").read()).hexdigest()
    assert got == digest, f"{name}: {got} != pinned {digest}"
POPPLER = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr.splitlines()[0]


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,254}", id_), id_
    r = {"id": id_, "kind": kind, "name": name[:500], "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


tx = lambda e: " ".join(" ".join(e.itertext()).split())

# ---------------------------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------------------------
art = ET.parse(os.path.join(PINNED, "sahraeian2022-article.xml"))
assert tx(art.find(".//article-meta//article-title")) == ("Achieving robust somatic mutation detection with deep learning models "
                                                          "derived from reference data sets of a cancer sample")
COI = tx(next(s for s in art.iter("sec") if s.find("title") is not None and tx(s.find("title")) == "Competing interests"))
assert "filed a patent application on NeuSomatic" in COI, COI
SRC = f"{P}-source-sahraeian2022"
rec(SRC, "source", "Achieving robust somatic mutation detection with deep learning models derived from reference data sets of a cancer sample",
    "Primary source retrieved and hashed for the NeuSomatic SEQC2 follow-up to the somatic variant detection use-case pass.", [], [],
    {"url": "https://doi.org/10.1186/s13059-021-02592-9", "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8740374/fullTextXML",
     "version": "Genome Biology 23:12, published 2022-01-07; PMC8740374 full-text XML", "retrieved_at": "2026-10-10T06:04:11Z",
     "artifact_sha256": ARTIFACTS["sahraeian2022-article.xml"], "doi": "10.1186/s13059-021-02592-9", "publication_status": "peer_reviewed",
     "licence": "CC-BY-4.0", "media_type": "application/xml"})
SUP = f"{P}-source-sahraeian2022-additional-file-2"
SUP_URL = "https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-021-02592-9/MediaObjects/13059_2021_2592_MOESM2_ESM.pdf"
SUP_SHA = ARTIFACTS["sahraeian2022-additional-file-2.pdf"]
rec(SUP, "source", "Sahraeian et al. 2022, Additional file 2: Supplementary Tables S1-S10 (13059_2021_2592_MOESM2_ESM.pdf)",
    "Supplementary PDF as served by the publisher.", [], [],
    {"url": "https://doi.org/10.1186/s13059-021-02592-9", "artifact_url": SUP_URL, "version": "13059_2021_2592_MOESM2_ESM.pdf",
     "retrieved_at": "2026-10-10T06:04:16Z", "artifact_sha256": SUP_SHA, "doi": "10.1186/s13059-021-02592-9",
     "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/pdf"})
IDS = [SRC, SUP]

# ---------------------------------------------------------------------------------------------
# Methods and configurations
# ---------------------------------------------------------------------------------------------
M = "somatic-20261009-method-"
METHOD = {"VarDict": M + "vardict", "SomaticSniper": M + "somaticsniper", "MuSE": M + "muse", "MuTect2": M + "mutect2", "Lancet": M + "lancet",
          "Strelka2": M + "strelka", "DRAGEN": "cnv-20261009-method-dragen", "NeuSomatic": M + "neusomatic"}
OCTOPUS = rec(f"{P}-method-octopus", "method", "Octopus", "Haplotype-based germline and somatic small-variant caller.", [SRC], [],
              {"reported_name": "Octopus", "entity_level": "method", "source_locator": "Methods 'Somatic mutation detection algorithms'",
               "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
              facets={**FACETS, "method_types": ["conventional_pipeline"]})["id"]
METHOD["Octopus-RF"] = METHOD["Octopus-hard"] = OCTOPUS
VERSION = {"MuTect2": "4.beta.6", "SomaticSniper": "1.0.5.0", "Lancet": "1.0.7", "Strelka2": "2.8.4", "MuSE": "v1.0rc", "VarDict": "v1.5.1",
           "DRAGEN": "v3.7.5", "Octopus-RF": "v0.7.4", "Octopus-hard": "v0.7.4", "NeuSomatic": "0.1.4"}
PROTOCOL = {
    "SomaticSniper": "Parameters -q 1 -Q 15 -s 1e-05; PASS calls",
    "Lancet": "Parameters -cov-thr 10 -cov-ratio 0.005 -max-indel-len 50 -e 0.005; PASS calls",
    "VarDict": "Default or manual-recommended parameters; PASS calls with Somatic status",
    "DRAGEN": "Somatic pipeline with systematic-noise BED files built from each group of normal samples (DRAGEN v3.7 manual)",
    "Octopus-hard": "Hard filtering; PASS calls with SOMATIC status",
    "Octopus-RF": "Random forest filtering; PASS calls with SOMATIC status",
}
# Training data per NeuSomatic model (Additional file 2 Table S1; Methods 'Training data sets and models').
TRAIN = {
    "DREAM3": ("ICGC-TCGA DREAM Challenge Stage 3 in silico tumour-normal data (spiked SNVs and indels, five purity settings, 50% of the genome); "
               "trained by the NeuSomatic developers in earlier work. No SEQC2 data."),
    "SEQC-WGS-Spike": ("In silico tumours made by spiking about 92K SNVs and 22K indels into HCC1395BL WGS replicates and pairing each with a "
                       "distinct HCC1395BL replicate: eight pairs from four sites (40x-95x) and two merged Illumina NovaSeq pairs (about 220x and "
                       "170x), each also with a 5% tumour-contaminated normal; 20 pairs, whole genome. No HCC1395 truth mutations, but reads of the "
                       "SEQC2 normal replicates across the whole genome, including the evaluation half."),
    "SEQC-WGS-GT-50": ("Real HCC1395/HCC1395BL WGS replicate pairs with the SEQC2 truth set: seven pairs from six centres (HiSeq and NovaSeq, 40x-95x) "
                       "and one pair of about 390x merged from nine Illumina NovaSeq replicates, each also as 95% pure normal and 10% tumour "
                       "purity mixtures; 24 pairs, in 50% of the high-confidence genome. The other 50% is the evaluation region."),
    "SEQC-WGS-GT50-SpikeWGS10": "All SEQC-WGS-GT-50 training candidates plus 10% of the SEQC-WGS-Spike candidates.",
}
CONF = {}
COLS = pdftables.TOOLS + [f"{g} {m}" for g in pdftables.GROUPS for m in pdftables.MODELS]
for col in COLS:
    cid = f"{P}-config-sahraeian2022-{slug(col)}"
    links, attrs, types = [], {"reported_name": col, "foundation_model_eligible": False}, ["conventional_pipeline"]
    if col.startswith("NeuSomatic"):
        grp, model = col.split(" ", 1)
        links.append({"relation": "configuration_of", "target_id": METHOD["NeuSomatic"]})
        attrs["version"] = VERSION["NeuSomatic"]
        attrs["checkpoint"] = f"{model} model ({'standalone' if grp == 'NeuSomatic-S' else 'ensemble'} mode), as named in Additional file 2 Table S1"
        attrs["training_overlap"] = TRAIN[model]
        if grp == "NeuSomatic":
            attrs["protocol"] = ("Ensemble mode: alignment-scanning candidates plus calls from MuTect2, SomaticSniper, Strelka2, MuSE and VarDict as extra "
                                 "input channels; preprocessing -scan_maf 0.01 -min_mapq 10 -snp_min_af 0.03 -snp_min_bq 15 -snp_min_ao 3 -ins_min_af 0.02 -del_min_af 0.02")
            links += [{"relation": "uses_model", "target_id": METHOD[t]} for t in ("MuTect2", "SomaticSniper", "Strelka2", "MuSE", "VarDict")]
        else:
            attrs["protocol"] = ("Standalone mode: alignment-scanning candidates only; preprocessing -scan_maf 0.01 -min_mapq 10 -snp_min_af 0.03 "
                                 "-snp_min_bq 15 -snp_min_ao 3 -ins_min_af 0.02 -del_min_af 0.02")
        types = ["supervised_machine_learning"]
        name = f"{col} model (Sahraeian et al. 2022)"
    else:
        links.append({"relation": "configuration_of", "target_id": METHOD[col]})
        attrs["version"] = VERSION.get(col)
        attrs["protocol"] = PROTOCOL.get(col, "Default or manual-recommended parameters; PASS calls")
        if col == "Octopus-RF":
            attrs["training_overlap"] = ("Results say the random forest filter was trained on the SEQC-WGS-GT50-SpikeWGS10 training data (HCC1395 truth "
                                         "mutations in the other 50% of the genome plus HCC1395BL spike-ins); Methods call it 'the pretrained random forest model'.")
            types = ["conventional_pipeline", "supervised_machine_learning"]
        name = f"{col} {VERSION[col]} (Sahraeian et al. 2022)"
    attrs = {k: v for k, v in attrs.items() if v is not None}
    attrs["source_locator"] = "Methods 'Somatic mutation detection algorithms'; Additional file 2 Table S1 and Tables S2-S4 column headers"
    rec(cid, "configuration", name, f"{col} as run in the cited comparison.", IDS, links, attrs, facets={**FACETS, "method_types": types})
    CONF[col] = cid
SEQC2_TRAINED = {c for c in COLS if c.startswith("NeuSomatic") and "DREAM3" not in c} | {"Octopus-RF"}
AUTHOR = {c for c in COLS if c.startswith("NeuSomatic")} | {"Octopus-RF"}

# ---------------------------------------------------------------------------------------------
# Tables S2, S3 and S4
# ---------------------------------------------------------------------------------------------
PAGES = pdftables.pages(os.path.join(PINNED, "sahraeian2022-additional-file-2.pdf"))
TABLES = {
    "S2": dict(page=1, next=None, key="wgs", title="F1-score (%) performance of different somatic mutation detection methods and network trained models on the WGS data set",
               data_name="SEQC2 HCC1395/HCC1395BL WGS replicate pairs from multiple sequencing centres",
               population="21 tumour-normal WGS replicate pairs (labels WGS_<site>_T/N_<n>, site codes EA, FD, IL, LL, NC, NS, NV) on HiSeq X Ten, HiSeq 4000 and NovaSeq",
               topic="sequencing centre and platform", stratum_group="neusomatic2022-seqc2-wgs-centres",
               title_short="Sequencing centre and platform (SEQC2 HCC1395 WGS replicates)",
               rows="replicate pair", note="Results say 21 replicates from six sequencing centres; the row labels carry seven site codes."),
    "S3": dict(page=2, next=None, key="titration", title="F1-score (%) performance of different somatic mutation detection methods and network trained models on the tumor-normal titration data set",
               data_name="SEQC2 tumour-normal titration: HCC1395 gDNA mixed with HCC1395BL gDNA at 5-100% tumour purity, 10x-300x WGS",
               population="42 purity-coverage pairs (5, 10, 20, 50, 75 and 100% tumour at 10x, 30x, 50x, 80x, 100x, 200x and 300x, pure normal) and 5 pairs at 80x with a 95% pure normal (10-100% tumour)",
               topic="tumour purity, coverage and normal contamination", stratum_group="neusomatic2022-seqc2-titration",
               title_short="Tumour purity, coverage and normal contamination (SEQC2 HCC1395 titration)", rows="purity-coverage pair", note=None),
    "S4": dict(page=3, next="S5", key="library-prep", title="F1-score (%) performance of different somatic mutation detection methods and network trained models on the library-preparation data set",
               data_name="SEQC2 HCC1395/HCC1395BL library-preparation replicates (TruSeq-Nano and Nextera Flex, 1-100 ng DNA)",
               population="6 tumour-normal WGS pairs: TruSeq-Nano and Nextera Flex libraries from 1, 10 and 100 ng DNA",
               topic="library preparation and DNA input", stratum_group="neusomatic2022-seqc2-library-prep",
               title_short="Library preparation and DNA input (SEQC2 HCC1395)", rows="library pair", note=None),
}
text = subprocess.run(["pdftotext", "-layout", os.path.join(PINNED, "sahraeian2022-additional-file-2.pdf"), "-"], capture_output=True, text=True, check=True).stdout
flat = " ".join(text.split())
for lab, t in TABLES.items():
    assert f"Table {lab} - {t['title']}" in flat, lab
HOW = (f"Parsed from the pinned PDF word boxes (pdftotext -bbox, {POPPLER}) by extract/extract_neusomatic.py; columns fixed by position (see retrieval-log.md); column means match the printed Average row.")
EVAL_REGION = ("All callers and models were scored on the 50% of the SEQC2 high-confidence genome held out from SEQC-WGS-GT-50 training (about 1.4 Gb; "
               "about 21K truth SNVs and 1.3K truth indels), against SEQC2 HighConf and MedConf calls (v1.0), LowConf calls blacklisted and ambiguous private calls excluded")
LIMS_COMMON = [
    "Developer paper: the NeuSomatic authors trained and selected every NeuSomatic model and the Octopus random forest filter, and chose the comparator settings.",
    "One cell-line pair (HCC1395/HCC1395BL). The SEQC2 truth set was built by the consortium from multiple callers and replicates with a SomaticSeq classifier, and has a 5% VAF and 50x depth detection limit; private calls outside it that were deemed ambiguous were excluded from scoring (Methods 'Evaluation process').",
    "Models trained on SEQC2 HCC1395 data (NeuSomatic and NeuSomatic-S SEQC-WGS-Spike, SEQC-WGS-GT-50 and SEQC-WGS-GT50-SpikeWGS10, and Octopus-RF) are scored on the same cell line and truth set; only the genomic region is held out. The use case excludes callers evaluated only with a model built from the test cell line.",
    "SEQC-WGS-GT50-SpikeWGS10 was chosen as the default NeuSomatic model from these same evaluations (Results 'Analysis of different model-building strategies').",
    "Only F1 is printed; no precision, recall or uncertainty in these tables.",
    "Caller versions are from 2017-2021 (for example MuTect2 4.beta.6, Strelka2 2.8.4).",
]
TABLE_FLAG = {
    "S2": ("The SEQC2-trained models were trained on WGS replicate pairs from this replicate set (seven pairs from six centres plus a merged NovaSeq pair; "
           "spike-in models on HCC1395BL replicates from four sites). The paper does not say which of the 21 pairs, so any row may be a training replicate "
           "scored in the held-out half of the genome."),
    "S3": "The titration libraries are not described as training data; the cell line, truth set and evaluation region are shared with training.",
    "S4": "The library-preparation replicates are not described as training data; the cell line, truth set and evaluation region are shared with training.",
}


def num(text):
    assert re.fullmatch(r"\d+(\.\d+)?", text), text
    return format(Decimal(text), "f")


proposed_exclusions = []
for lab, t in TABLES.items():
    cols, secs = pdftables.table(PAGES[t["page"]], lab, t["next"])
    assert cols == COLS, (lab, cols)
    assert list(secs) == ["SNVs", "INDELs"], (lab, list(secs))
    n_rows = len(secs["SNVs"]) - 1
    assert [r[0] for r in secs["SNVs"]] == [r[0] for r in secs["INDELs"]], lab
    for kind, rows in secs.items():
        assert rows[-1][0] == ["Average"], (lab, rows[-1][0])
        for col in COLS:
            vals = [float(r[1][col]) for r in rows[:-1] if r[1][col] != "-"]
            if vals:
                assert len(vals) == n_rows and abs(sum(vals) / len(vals) - float(rows[-1][1][col])) <= 0.051, (lab, kind, col)
    did = rec(f"{P}-data-sahraeian2022-{t['key']}", "dataset", t["data_name"], f"Tumour-normal data used in Additional file 2 Table {lab}.", IDS, [],
              {"population": t["population"], "split": "Evaluation region: the 50% of the SEQC2 high-confidence genome held out from SEQC-WGS-GT-50 training",
               "assay": "Paired tumour-normal whole-genome sequencing, Trimmomatic, BWA-MEM 0.7.15, Picard MarkDuplicates", "accession": "NCBI SRA SRP162370",
               "source_locator": f"Additional file 2 Table {lab} row labels; Results; Methods 'SEQC2 tumor-normal sequencing data and ground truth' and 'Evaluation process'",
               "missing_metadata": {"version": {"reason": "unreported", "note": "Truth set is SEQC2 v1.0; data release not otherwise stated"}}})["id"]
    for kind in ("SNVs", "INDELs"):
        vt = "snv" if kind == "SNVs" else "indel"
        pid = f"{P}-protocol-sahraeian2022-{t['key']}-{vt}"
        lims = LIMS_COMMON + [TABLE_FLAG[lab]] + ([t["note"]] if t["note"] else [])
        if vt == "indel":
            lims.append("SomaticSniper and MuSE do not call indels ('-' in the table).")
        pname = f"SEQC2 HCC1395 {t['topic']}, {kind[:-1] if kind == 'SNVs' else 'indel'} F1 (Sahraeian et al. 2022 Table {lab})"
        rec(pid, "protocol", pname, f"{kind[:-1] if kind == 'SNVs' else 'Indel'} F1 per {t['rows']} for nine callers and eight NeuSomatic models.", IDS,
            [{"relation": "uses_data", "target_id": did}],
            {"protocol": f"Paired tumour-normal calling of each {t['rows']}; PASS calls scored by exact match. {EVAL_REGION}.",
             "version": f"Additional file 2 Table {lab}", "metric": "f1-score", "limitations": lims,
             "source_locator": f"Additional file 2 Table {lab} ({kind} section); Methods 'Evaluation process'"})
        evals = []
        for col in COLS:
            cells = [r[1][col] for r in secs[kind]]
            if all(c == "-" for c in cells):
                assert vt == "indel" and col in ("SomaticSniper", "MuSE"), (lab, kind, col)
                continue
            assert "-" not in cells, (lab, kind, col)
            eid = f"{P}-eval-sahraeian2022-{slug(col)}-{t['key']}-{vt}"
            attrs = {"origin": "author_reported" if col in AUTHOR else "independent_paper", "protocol": pid,
                     "version": f"Primary source as retrieved {TODAY}",
                     "comparison": {"protocol_id": pid, "dataset_version": None, "split": "Held-out 50% of the high-confidence genome",
                                    "population": t["population"], "inputs": "Tumour and matched normal WGS BAM files (BWA-MEM)",
                                    "adaptation": None, "metric_implementation": "F1 (%) of PASS calls against the SEQC2 truth set, exact match",
                                    "aggregation": f"Per {t['rows']}, plus the printed average over {n_rows}", "budget": None},
                     "source_locator": f"Additional file 2 Table {lab}, column '{col}', {kind} section",
                     "missing_metadata": {"comparison.dataset_version": {"reason": "unreported"}}}
            if col in SEQC2_TRAINED:
                attrs["evidence_overlap"] = f"Model trained on SEQC2 HCC1395 data. {TABLE_FLAG[lab]}"
                proposed_exclusions.append({"id": eid, "reason": f"{col} was trained on SEQC2 HCC1395 data and is scored on the same cell line and truth set. {TABLE_FLAG[lab]}"})
            elif col.startswith("NeuSomatic"):
                attrs["evidence_overlap"] = "DREAM3 model: trained on DREAM Challenge Stage 3 in silico data, not on SEQC2 data. Developer model."
            rec(eid, "evaluation", f"{col} on {t['data_name'].split(':')[0]}, {kind} (Sahraeian et al. 2022)",
                "Published somatic caller comparison; transcribed, not reproduced.", IDS,
                [{"relation": "system", "target_id": CONF[col]}, {"relation": "assessment", "target_id": pid}, {"relation": "data", "target_id": did}], attrs)
            evals.append(eid)
            for labels, row in secs[kind]:
                avg = labels == ["Average"]
                pair = "Average" if avg else f"{labels[0]} vs {labels[1]}"
                assert avg or len(labels) == 2, labels
                rid = f"{P}-result-sahraeian2022-{slug(col)}-{t['key']}-{vt}-{'average' if avg else slug(labels[0] + '-' + labels[1])}"
                qual = (f"{kind}, average over the {n_rows} {t['rows']}s as printed" if avg else f"{kind}, tumour {labels[0]} with normal {labels[1]}")
                loc = f"Additional file 2 Table {lab}, {kind} section, row '{pair}', column '{col}'"
                ra = {"metric": "f1-score", "metric_direction": "higher", "unit": "percent", "metric_qualifier": qual,
                      "printed_value": row[col], "numeric_value": num(row[col]), "source_locator": loc,
                      "missing_metadata": {"uncertainty": {"reason": "unreported"}},
                      "review": {"method": ["deterministic-table-parse"], "reviewer": ["claude"],
                                 "reviewer_note": "Extracting Claude (Opus 5.5) research agent; not a review. No human review claimed.",
                                 "date": TODAY, "note": f"{HOW} Pending independent review.", "artifact_sha256": SUP_SHA, "retrieval_url": SUP_URL}}
                if avg:
                    ra["scope_note"] = "Printed average of the rows above; matches their mean to 0.05."
                rec(rid, "result", f"{col} {t['key']} {vt} F1, {pair}", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                    IDS, [{"relation": "evaluation", "target_id": eid}], ra, facets={})
                claims_rows.append([rid, SUP, loc, row[col], "result"])
        order = 1 if vt == "snv" else 2
        jid = f"use-case-mapping-{P}-{t['key']}-{vt}"
        excl = [e for e in evals if any(x["id"] == e for x in proposed_exclusions)]
        rationale = (f"Paired tumour-normal WGS of the SEQC2 reference cell line with a consortium truth set shows how {kind[:-1] if vt == 'snv' else 'indel'} "
                     f"calling accuracy of conventional callers and NeuSomatic models changes with {t['topic']}, which is the regime question the use case asks.")
        ja = {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": "direct",
              "endpoint": f"{kind[:-1] if vt == 'snv' else 'Indel'} F1 (%) per {t['rows']} and on average for {len(evals)} caller configurations, scored on the held-out half of the SEQC2 high-confidence genome",
              "rationale": rationale,
              "constraints": ["Inspect every linked evaluation's source locator before citing a result.",
                              "Do not combine this mapping's evaluations with any other protocol's results; truth sets, regions and caller versions differ between sources.",
                              f"Exclude the {len(excl)} evaluations of models trained on SEQC2 HCC1395 data (listed in the batch coverage.json) before comparing callers; they are kept as transcribed."],
              "limitations": lims, "revision": 1,
              "reason": "Add the SEQC2 whole-genome caller comparisons of Sahraeian et al. 2022 Additional file 2 (NeuSomatic follow-up, 2026-10-10).",
              "citation_locators": [{"source_id": SUP, "locator": f"Additional file 2 Tables S1 and {lab}"},
                                    {"source_id": SRC, "locator": "Results; Methods 'Training data sets and models', 'Somatic mutation detection algorithms' and 'Evaluation process'"}],
              "source_locator": f"{SUP}: Additional file 2 Tables S1 and {lab}; {SRC}: Results and Methods",
              "comparison_group": t["stratum_group"], "comparison_title": f"{t['title_short']} (Sahraeian et al. 2022)", "headline_metric": "f1-score",
              "stratum_label": "SNVs" if vt == "snv" else "Indels", "stratum_order": order}
        rec(jid, "claim", f"Relevance of {pname} to \"{UC_NAME}\"", rationale, IDS, [{"relation": "subject", "target_id": UC}], ja, facets={})
        judgements.append(jid)

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
print(Counter(r["kind"] for r in records), len(proposed_exclusions))
