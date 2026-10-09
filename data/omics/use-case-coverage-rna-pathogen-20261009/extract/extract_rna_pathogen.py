"""Deterministic extraction of RNA pathogen-detection workflow comparisons into a records batch.

Usage: python3 -I extract_rna_pathogen.py <download-dir> <batch-dir>

<download-dir> holds the pinned downloads in the layout recorded in retrieval-log.md. The
script reads the XLSX cell XML and article XML with the standard library only, asserts every
row and column label it relies on, and writes batch.jsonl (store form), claims.csv and
extract/judgements.json. printed_value is the cell text for text cells and the shortest
decimal that round-trips to the stored number for numeric cells.
"""
import csv, hashlib, json, math, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

DL, BATCH = sys.argv[1], sys.argv[2]
P = "rna-pathogen-20261009"
UC = "use-case-diagnostic-rna-pathogen-detection"
UC_NAME = "Select an RNA pathogen-detection workflow for diagnostic testing"
DATE = "2026-10-09"
FACETS = {"areas": ["microbes-communities"], "contexts": ["clinical_research"]}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
XLSX_NOTE = ("Extracted by deterministic parse of the pinned XLSX cell XML (extract/extract_rna_pathogen.py), with row and "
             "column labels asserted. printed_value is the cell text, or the shortest decimal that round-trips to the stored "
             "number; displayed spreadsheet formatting was not applied. Pending independent review.")
records, claims_rows = [], []

PATHS = {
    "carbo_xml": f"{DL}/dl-PMC8953373/article.xml",
    "carbo_supp": f"{DL}/dl-carbo-medrxiv-supp/media-1.xlsx",
    "devries_xml": f"{DL}/dl-ennngs-medrxiv/source.xml",
    "devries_supp": f"{DL}/dl-ennngs-medrxiv-supp/media-1.xlsx",
    "meyer_xml": f"{DL}/dl-PMC9007738/article.xml",
    "meyer_supp": f"{DL}/dl-cami2-esm/moesm3.xlsx",
}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids, "links": links or [],
         "attributes": attributes or {}}
    records.append(r)
    return r


def review(note=XLSX_NOTE, method=("deterministic-table-parse",)):
    return {"method": list(method), "reviewer": ["claude"],
            "reviewer_note": "Claude (Opus 5.5) research agent, the extractor; no independent or human review claimed",
            "date": DATE, "note": note}


def need(got, expected, where):
    if got != expected:
        raise SystemExit(f"Label check failed at {where}: expected {expected!r}, got {got!r}")


# ---------------------------------------------------------------- XLSX reader (stdlib)
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def workbook(path):
    """{sheet name: {cell ref: (text, is_number)}}"""
    z = zipfile.ZipFile(path)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            ss.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for sh in wb.find("m:sheets", NS):
        tgt = rels[sh.get("{%s}id" % NS["r"])].lstrip("/")
        tgt = tgt if tgt.startswith("xl/") else "xl/" + tgt
        cells = {}
        for c in ET.fromstring(z.read(tgt)).iter("{%s}c" % NS["m"]):
            v, t = c.find("m:v", NS), c.get("t")
            if t == "s" and v is not None:
                cells[c.get("r")] = (ss[int(v.text)], False)
            elif t == "inlineStr":
                cells[c.get("r")] = ("".join(x.text or "" for x in c.iter("{%s}t" % NS["m"])), False)
            elif t in ("str", "e") and v is not None:
                cells[c.get("r")] = (v.text or "", False)
            elif v is not None:
                cells[c.get("r")] = (v.text, True)
        out[sh.get("name")] = cells
    return out


def printed_numeric(cell):
    """(printed_value, numeric_value) for an XLSX cell."""
    text, is_num = cell
    if is_num:
        f = float(text)
        s = repr(f)
        if s.endswith(".0"):
            s = s[:-2]
        if "e" in s or "E" in s:
            s = format(Decimal(s), "f")
        return s, format(Decimal(s), "f")
    t = text.strip()
    if re.fullmatch(r"-?\d+(\.\d+)?", t):
        return text, format(Decimal(t), "f")
    return text, None


def txt(e):
    return " ".join("".join(e.itertext()).split())


# ---------------------------------------------------------------- record helpers
def result(id_, eval_id, source_id, locator, cell, metric, direction, unit, qualifier=None, unit_detail=None,
           extra=None, note=XLSX_NOTE, printed=None, numeric="auto"):
    if printed is None:
        pv, nv = printed_numeric(cell)
    else:
        pv, nv = printed, None
    if numeric != "auto":
        nv = numeric
    attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": pv, "numeric_value": nv,
             "source_locator": locator, "missing_metadata": {"uncertainty": {"reason": "unreported"}}}
    if qualifier:
        attrs["metric_qualifier"] = qualifier
    if unit_detail:
        attrs["unit_detail"] = unit_detail
    if extra:
        attrs.update(extra)
    attrs["review"] = review(note)
    rec(id_, "result", f"{eval_id.replace(P + '-eval-', '')} {metric}" + (f" ({qualifier})" if qualifier else ""),
        "Reported measurement transcribed from the pinned source. Not independently reproduced.", [source_id],
        [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claims_rows.append([id_, source_id, locator, pv, "result"])


def claim(id_, subject, field, value, source_id, locator):
    rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", [source_id],
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator,
         "review": review("Transcribed from the pinned source text. Pending independent review.", ("transcription",))}, facets={})
    claims_rows.append([id_, source_id, locator, value, "claim"])


def evaluation(id_, name, system, protocol, dataset, source_ids, origin, comparison, locator, extra=None):
    attrs = {"origin": origin, "protocol": protocol, "version": f"Primary source as retrieved {DATE}",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    attrs.update(extra or {})
    rec(id_, "evaluation", name, "Published RNA metagenomic pathogen-detection comparison; transcribed, not reproduced.",
        source_ids, [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
                     {"relation": "data", "target_id": dataset}], attrs)


def method(key, name, description, source_id, locator, kind="method", access=None):
    id_ = f"{P}-{'service' if kind == 'service' else 'method'}-{key}"
    attrs = {"reported_name": name, "entity_level": "service" if kind == "service" else "method"}
    if kind == "method":
        attrs["source_locator"] = locator
        attrs["missing_metadata"] = {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}
    if access:
        attrs["access"] = access
    rec(id_, kind, name, description, [source_id], [], attrs, facets={**FACETS, "method_types": ["conventional_pipeline"]})
    return id_


def configuration(id_, name, description, of, source_ids, reported_name, locator, version=None, version_missing=None,
                  parameters=None):
    attrs = {"reported_name": reported_name, "source_locator": locator, "foundation_model_eligible": False}
    if version:
        attrs["version"] = version
    else:
        attrs["missing_metadata"] = {"version": version_missing}
    if parameters:
        attrs["parameters"] = parameters
    rec(id_, "configuration", name, description, source_ids, [{"relation": "configuration_of", "target_id": of}], attrs,
        facets={**FACETS, "method_types": ["conventional_pipeline"]})


def source(id_, name, url, artifact_url, path, version, retrieved, doi, status_pub, licence, venue, year, locator,
           media_type, extra=None):
    attrs = {"url": url, "artifact_url": artifact_url, "version": version, "retrieved_at": retrieved,
             "artifact_sha256": sha(path), "doi": doi, "publication_status": status_pub, "licence": licence,
             "media_type": media_type, "venue": venue, "year": year, "source_locator": locator}
    attrs.update(extra or {})
    rec(id_, "source", name, "Primary source retrieved and hashed for the RNA pathogen-detection use-case pass.", [], [], attrs)


XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
# ================================================================= sources
S_CARBO, S_CARBO_SUPP = f"{P}-source-carbo2022", f"{P}-source-carbo2022-supp"
S_DEV, S_DEV_SUPP = f"{P}-source-devries2021", f"{P}-source-devries2021-supp"
S_MEY, S_MEY_SUPP = f"{P}-source-meyer2022", f"{P}-source-meyer2022-supp"
source(S_CARBO, "Performance of Five Metagenomic Classifiers for Virus Pathogen Detection Using Respiratory Samples from a Clinical Cohort",
       "https://doi.org/10.3390/pathogens11030340", f"{EPMC}/PMC8953373/fullTextXML", PATHS["carbo_xml"],
       "Pathogens 11(3):340, published 2022-03-11; PMC8953373 full-text XML", "2026-10-09T20:06:32Z",
       "10.3390/pathogens11030340", "peer_reviewed", "CC-BY-4.0", "Pathogens", 2022,
       "Licence from the Europe PMC record (cc by) and the article XML", "application/xml")
source(S_CARBO_SUPP, "Carbo et al. medRxiv preprint v1, Supplementary Tables 1 and 2",
       "https://doi.org/10.1101/2022.01.21.22269647",
       "https://www.medrxiv.org/content/medrxiv/early/2022/01/21/2022.01.21.22269647/DC1/embed/media-1.xlsx",
       PATHS["carbo_supp"], "medRxiv 2022.01.21.22269647 version 1 (2022-01-21), supplementary file media-1.xlsx",
       "2026-10-09T20:16:56Z", "10.1101/2022.01.21.22269647", "preprint", "CC-BY-ND-4.0", "medRxiv", 2022,
       "Licence from the medRxiv API record for version 1 (cc_by_nd)", XLSX,
       {"limitations": ["Supplement of the preprint. The published article's supplement (MDPI s1, same table titles) could not be retrieved: Europe PMC returned a truncated zip twice, MDPI returned HTTP 403 and PMC returned a browser challenge. Whether the values differ is not known."]})
source(S_DEV, "Benchmark of thirteen bioinformatic pipelines for metagenomic virus diagnostics using datasets from clinical samples",
       "https://doi.org/10.1101/2021.05.04.21256618",
       "https://www.medrxiv.org/content/early/2021/05/08/2021.05.04.21256618.source.xml", PATHS["devries_xml"],
       "medRxiv 2021.05.04.21256618 version 1 (2021-05-08), JATS XML; published as J Clin Virol 141:104908 (doi:10.1016/j.jcv.2021.104908)",
       "2026-10-09T20:15:27Z", "10.1101/2021.05.04.21256618", "preprint", "CC-BY-NC-ND-4.0", "medRxiv", 2021,
       "Licence from the JATS <license> element", "application/xml",
       {"limitations": ["Preprint version. The published version (PMC7615111, CC BY) could not be retrieved: Europe PMC full-text XML returned HTTP 500 twice and the publisher, Europe PMC PDF, UCL and Leiden repository copies returned HTTP 403 or an access-blocked page.",
                        "Tables 1 and 2 of the preprint are images; they were not transcribed."]})
source(S_DEV_SUPP, "de Vries et al. medRxiv preprint v1, Supplementary Tables 2-4",
       "https://doi.org/10.1101/2021.05.04.21256618",
       "https://www.medrxiv.org/content/medrxiv/early/2021/05/08/2021.05.04.21256618/DC1/embed/media-1.xlsx",
       PATHS["devries_supp"], "medRxiv 2021.05.04.21256618 version 1, supplementary file media-1.xlsx (sheets SuppS2, SuppS3, SuppS4)",
       "2026-10-09T20:15:56Z", "10.1101/2021.05.04.21256618", "preprint", "CC-BY-NC-ND-4.0", "medRxiv", 2021,
       "Licence of the preprint (JATS <license> element)", XLSX,
       {"evidence_concerns": [{
           "source_id": S_DEV_SUPP,
           "message": "Supplementary Table 2 has 14 pipeline rows, including 'DIAMOND pipeline 3A (see table 1)' with no summary values, while the Methods say 13 pipelines were used and that DAMIAN (not DIAMOND) was run by two participants as pipelines A and B; only one DAMIAN row is printed. The Abstract gives the lowest sample-level sensitivity as 80% (10/13), but 10/13 is 76.9% and Results and Supplementary Table 2 give 77% (10/13); 80% matches the lowest hit-level value (12/15) in Supplementary Table 4. Values are recorded as printed.",
           "source_locator": "Supplementary Table 2 rows 18-32 (A18, A28) and column S; Methods 'Bioinformatic pipelines'; Abstract Results; Results 'Detection of PCR targeted viral pathogens; sensitivity' paragraph 1",
           "artifact_sha256": sha(PATHS["devries_supp"]), "reviewed_at": "2026-10-09T20:30:00Z",
           "review_method": "ai-assisted-source-review"}]})
source(S_MEY, "Critical Assessment of Metagenome Interpretation: the second round of challenges",
       "https://doi.org/10.1038/s41592-022-01431-4", f"{EPMC}/PMC9007738/fullTextXML", PATHS["meyer_xml"],
       "Nature Methods 19(4):429, published 2022-04-08; PMC9007738 full-text XML", "2026-10-09T20:21:44Z",
       "10.1038/s41592-022-01431-4", "peer_reviewed", "CC-BY-4.0", "Nature Methods", 2022,
       "Licence statement in the article XML <license> element: Creative Commons Attribution 4.0", "application/xml")
source(S_MEY_SUPP, "Meyer et al. 2022, Supplementary Tables 1-40",
       "https://doi.org/10.1038/s41592-022-01431-4",
       "https://static-content.springer.com/esm/art%3A10.1038%2Fs41592-022-01431-4/MediaObjects/41592_2022_1431_MOESM3_ESM.xlsx",
       PATHS["meyer_supp"], "41592_2022_1431_MOESM3_ESM.xlsx (Supplementary Tables), as linked from the article XML <supplementary-material id=\"MOESM3\">",
       "2026-10-09T20:18:45Z", "10.1038/s41592-022-01431-4", "peer_reviewed", "CC-BY-4.0", "Nature Methods", 2022,
       "Article licence (Creative Commons Attribution 4.0) covers the supplementary information", XLSX,
       {"evidence_concerns": [{
           "source_id": S_MEY_SUPP,
           "message": "Supplementary Table 39 gives Bracken v2.2 as predicting the causal pathogen (yes) and Bracken v2.5 as not (no). The article text (Results, 'Clinical pathogen prediction: a concept challenge') says the reverse: Bracken v.2.5 correctly identified CCHFV as causal, and Bracken v.2.2 identified orthonairovirus but not as the causal pathogen. Table values are recorded.",
           "source_locator": "Supplementary Table 39 rows 3-4 (B3:C4) versus Results 'Clinical pathogen prediction: a concept challenge' paragraph 1",
           "artifact_sha256": sha(PATHS["meyer_supp"]), "reviewed_at": "2026-10-09T20:30:00Z",
           "review_method": "ai-assisted-source-review"}]})

# ================================================================= Carbo et al. 2022
carbo = workbook(PATHS["carbo_supp"])
need(list(carbo), ["Suppl table 1-Species", "Suppl table 1-Genus", "Suppl table 1-Family", "Suppl table 2"], "Carbo sheet names")
sp = carbo["Suppl table 1-Species"]
need(sp["A1"][0], "Supplementary Table 1. Overview of performance characteristics for the classifieres benchmarked in this study, at species (sheet 1), genus (sheet 2), and family level (sheet 3).", "Carbo S1 title")
HEAD0 = ["#", "Tool", "Informedness", "AUC", "SN (ROC)", "SL (ROC)", "PPV (ROC)", "NPV (ROC)", "LR slope", "LR intercept", "LR r2, %", "Taxa"]
TOOLS = {"Centrifuge", "CLARK", "Kaiju", "Kraken2", "GD"}
PRE = {"incl. human reads": "incl-human", "excl. human reads": "excl-human", "excl. human reads and normalized": "excl-human-norm"}
PRE_TEXT = {"incl-human": "all trimmed reads (human reads included)",
            "excl-human": "human reads removed (Bowtie2 to GRCh38) before classification",
            "excl-human-norm": "human reads removed, and assigned read counts normalised by target genome length"}
# blocks: (sheet, protocol key, label cell, header row, first data row, column offset letters)
COLS1 = "ABCDEFGHIJKLM"
COLS2 = ["P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB"]
BLOCKS = []
for (lab, hdr) in [("A7", 8), ("A17", 18), ("A27", 28)]:
    BLOCKS.append(("Suppl table 1-Species", "species-cutoff-0", lab, hdr, list(COLS1), "Taxa with reads >0"))
for (lab, hdr) in [("P7", 8), ("P17", 18), ("P27", 28)]:
    BLOCKS.append(("Suppl table 1-Species", "species-cutoff-10", lab, hdr, COLS2, "Taxa with reads >10"))
for sheet, level in [("Suppl table 1-Genus", "genus"), ("Suppl table 1-Family", "family")]:
    for (lab, hdr) in [("A4", 5), ("A14", 15), ("A24", 25)]:
        BLOCKS.append((sheet, f"{level}-cutoff-0", lab, hdr, list(COLS1), "Taxa with reads >0"))
need([sp["A5"][0], sp["P5"][0], sp["A6"][0], sp["P6"][0]], ["SPECIES LEVEL", "SPECIES LEVEL", "cut-off 0 reads", "cut-off 10 reads"], "Carbo species headers")
for sheet, level in [("Suppl table 1-Genus", "GENUS LEVEL"), ("Suppl table 1-Family", "FAMILY LEVEL")]:
    need([carbo[sheet]["A1"][0], carbo[sheet]["A2"][0]], [level, "cut-off 0 reads"], f"Carbo {sheet} headers")

CARBO_METHODS = {
    "Centrifuge": method("centrifuge", "Centrifuge", "Read classifier using a Burrows-Wheeler transform and FM-index of reference sequences.", S_CARBO, "Section 2.6.1; Table 2"),
    "CLARK": method("clark", "CLARK", "Discriminative k-mer read classifier.", S_CARBO, "Section 2.6.2; Table 2"),
    "Kaiju": method("kaiju", "Kaiju", "Amino-acid-level read classifier using six-frame translation and maximum exact matches.", S_CARBO, "Section 2.6.3; Table 2"),
    "Kraken2": "catalog-model-kraken2",
    "GD": method("genome-detective", "Genome Detective", "Hosted virus identification pipeline: DIAMOND read binning, de novo assembly, BLAST and alignment-based assignment.", S_CARBO,
                 "Section 2.6.5; Table 2", kind="service", access="Commercial web application, free to use (Table 2 'License')"),
}
CV = {"Centrifuge": ("1.0.4", "Viral NCBI RefSeq genomes downloaded 2020-12-27; one label per read (lowest common ancestor) instead of the default five", "Section 2.5; 2.6.1; Table 2 column 'Centrifuge'"),
      "CLARK": ("1.2.6.1", "Viral NCBI RefSeq genomes downloaded 2020-12-27; default execution mode", "Section 2.5; 2.6.2; Table 2 column 'Clark'"),
      "Kaiju": ("1.7.3", "Viral NCBI RefSeq genomes downloaded 2020-12-27; greedy mode, up to five mismatches", "Section 2.5; 2.6.3; Table 2 column 'Kaiju' and footnote"),
      "Kraken2": ("2.0.8-beta", "Viral NCBI RefSeq genomes downloaded 2020-12-27", "Section 2.5; 2.6.4; Table 2 column 'Kraken 2'"),
      "GD": ("1.126 (Table 2); Section 2.5 gives its own database as generated 2020-03-03, version 1.130", "Genome Detective's own database; reads pre-trimmed with Trimmomatic as for the other tools", "Section 2.5; 2.6.5; Table 2 column 'GenomeDetective'")}
TOOL_NAME = {"Centrifuge": "Centrifuge", "CLARK": "CLARK", "Kaiju": "Kaiju", "Kraken2": "Kraken2", "GD": "Genome Detective"}
CC = {}
for tool in ["Centrifuge", "CLARK", "Kaiju", "Kraken2", "GD"]:
    for pre in ["incl-human", "excl-human", "excl-human-norm"]:
        cid = f"{P}-config-carbo2022-{tool.lower() if tool != 'GD' else 'genome-detective'}-{pre}"
        CC[(tool, pre)] = cid
        v, params, loc = CV[tool]
        configuration(cid, f"{TOOL_NAME[tool]}, {PRE_TEXT[pre]} (Carbo et al. 2022)",
                      f"{TOOL_NAME[tool]} on Trimmomatic-trimmed reads, {PRE_TEXT[pre]}.", CARBO_METHODS[tool], [S_CARBO, S_CARBO_SUPP],
                      TOOL_NAME[tool], loc + "; Section 2.3 (pre-processing)", version=v,
                      parameters=f"{params}. Pre-processing: Trimmomatic v0.36 trimming, adapter clipping and low-complexity filtering; {PRE_TEXT[pre]}.")
C_DATA = f"{P}-data-carbo2022-copd-nasal-washes"
rec(C_DATA, "dataset", "Nasal washings from COPD patients with respiratory complaints, metagenomic sequencing and 13-target respiratory PCR panel (Carbo et al. 2022)",
    "88 clinical metagenomic datasets with 1144 PCR results as reference.", [S_CARBO], [],
    {"version": "As described in Carbo et al. 2022 (NCBI SRA SRX6713943-SRX6714030, human reads removed)", "accession": "NCBI SRA SRX6713943-SRX6714030",
     "population": "88 nasal washings from 63 patients with COPD suspected of respiratory infection; 13 respiratory virus PCR targets per sample, 24 positive and 1120 negative PCR results. All targets are RNA viruses (rhinovirus/enterovirus, parainfluenza 1-4, influenza A and B, coronaviruses NL63, 229E, HKU1/OC43, metapneumovirus, RSV).",
     "assay": "EAV and PhHV-1 internal controls; MagNAPure 96 total nucleic acid extraction; NEBNext Ultra II Directional RNA library with a protocol for RNA and DNA in one tube; NextSeq 500, about 10 million 150 bp paired-end reads per sample",
     "split": "No split; whole cohort", "denominator": 1144,
     "source_locator": "Sections 2.1-2.2; Table 1; Data Availability Statement"})
C_PROT = {}
C_LABEL = {"species-cutoff-0": ("Species level, read-count cut-off 0", 1), "species-cutoff-10": ("Species level, read-count cut-off 10", 2),
           "genus-cutoff-0": ("Genus level, read-count cut-off 0", 3), "family-cutoff-0": ("Family level, read-count cut-off 0", 4)}
for key, (label, order) in C_LABEL.items():
    pid = f"{P}-protocol-carbo2022-{key}"
    C_PROT[key] = pid
    rec(pid, "protocol", f"Respiratory virus detection against PCR, {label.lower()} (Carbo et al. 2022 Supplementary Table 1)",
        "Per-classifier detection of 13 PCR-tested respiratory viruses in 88 nasal washings, scored against 1144 PCR results.", [S_CARBO, S_CARBO_SUPP],
        [{"relation": "uses_data", "target_id": C_DATA}],
        {"protocol": ("ROC curves over the read count used as the cut-off for a positive result (1000 steps from one read to the maximum per PCR target and sample); "
                      "sensitivity (SN), selectivity (SL, specificity), PPV and NPV at the ROC-selected point, AUC, and the ROC distance to the error-free point, against 24 positive and 1120 negative PCR results; "
                      "linear regression of assigned read counts against PCR Ct values. "
                      f"Assignment at {label.split(',')[0].lower()}; the supplement labels this block '{label.split(', ')[1]}' without further definition."),
         "version": f"Supplementary Table 1, {label}", "denominator": 1144,
         "source_locator": "Section 2.7; Supplementary Table 1 sheet notes (rows 1-3)",
         "limitations": ["Single cohort; 24 PCR-positive results.", "The meaning of the 0 and 10 read cut-offs alongside the ROC-selected threshold is not defined beyond the sheet note.",
                         "Out-of-panel viruses are not scored."],
         "missing_metadata": {"uncertainty": {"reason": "unreported"}}})
C_COMP = {"dataset_version": "SRX6713943-SRX6714030", "split": "Whole cohort", "population": "88 samples, 1144 PCR results (24 positive)",
          "inputs": "Trimmed NextSeq 150 bp paired-end reads", "adaptation": "Viral RefSeq database built 2020-12-27 (Genome Detective: own database)",
          "metric_implementation": "Authors' ROC analysis over read-count cut-offs", "aggregation": "All PCR targets pooled", "budget": None}
C_EVALS = {}
roc_checked = roc_anomalous = 0
for sheet, key, lab, hdr, cols, taxa_head in BLOCKS:
    ws = carbo[sheet]
    pre = PRE[ws[lab][0]]
    need([ws[f"{c}{hdr}"][0] for c in cols], HEAD0 + [taxa_head], f"Carbo {sheet} header row {hdr}")
    seen = set()
    for r in range(hdr + 1, hdr + 6):
        tool = ws[f"{cols[1]}{r}"][0]
        need(tool in TOOLS, True, f"Carbo {sheet} {cols[1]}{r} tool label")
        seen.add(tool)
        ev = f"{P}-eval-carbo2022-{key}-{CC[(tool, pre)].split('-config-carbo2022-')[1]}"
        C_EVALS[(key, tool, pre)] = ev
        level_label = C_LABEL[key][0]
        evaluation(ev, f"{TOOL_NAME[tool]}, {PRE_TEXT[pre]}: {level_label.lower()} (Carbo et al. 2022)", CC[(tool, pre)], C_PROT[key], C_DATA,
                   [S_CARBO, S_CARBO_SUPP], "independent_paper", C_COMP, f"Supplementary Table 1 sheet '{sheet}', block '{ws[lab][0]}', row {r}",
                   extra={"source_label": f"Row rank '#' as printed: {ws[cols[0] + str(r)][0]}"})
        claims_rows.append([ev, S_CARBO_SUPP, f"Supplementary Table 1 sheet '{sheet}', {cols[0]}{r} ('#')", ws[cols[0] + str(r)][0], "evaluation_attribute"])
        base = f"Supplementary Table 1 sheet '{sheet}', block '{ws[lab][0]}'"
        vals = {}
        spec = [(2, "Informedness", "roc-distance", "lower", "unitless", None, None, "roc-distance"),
                (3, "AUC", "auroc", "higher", "unitless", "ROC over read-count cut-offs", None, "auc"),
                (4, "SN (ROC)", "recall", "higher", "fraction", "at the ROC-selected read-count cut-off", None, "sensitivity"),
                (5, "SL (ROC)", "specificity", "higher", "fraction", "at the ROC-selected read-count cut-off; printed as selectivity (SL)", None, "specificity"),
                (6, "PPV (ROC)", "precision", "higher", "fraction", "at the ROC-selected read-count cut-off", None, "ppv"),
                (7, "NPV (ROC)", "negative-predictive-value", "higher", "fraction", "at the ROC-selected read-count cut-off", None, "npv"),
                (8, "LR slope", "regression-slope", "unknown", "unitless", "linear regression between assigned read count and PCR Ct value", None, "lr-slope"),
                (9, "LR intercept", "regression-intercept", "unknown", "unitless", "linear regression between assigned read count and PCR Ct value", None, "lr-intercept"),
                (10, "LR r2, %", "pearson-r-squared", "higher", "percent", "assigned read count against PCR Ct value", None, "lr-r2"),
                (11, "Taxa", "count", "unknown", "count", "PCR target taxa scored at this level", "taxa", "taxa"),
                (12, taxa_head, "count", "unknown", "count", f"PCR target taxa with assigned reads ({taxa_head.split('with ')[1]})", "taxa", "taxa-with-reads")]
        for ci, col_label, metric, direction, unit, qual, udet, slug in spec:
            ref = f"{cols[ci]}{r}"
            cell = ws[ref]
            pv, nv = printed_numeric(cell)
            extra = {}
            if col_label == "Informedness":
                extra["source_label"] = "Informedness (column label; Section 2.7 defines it as the ROC distance to the error-free point (0,1))"
            if metric in ("recall", "specificity", "precision", "negative-predictive-value") and nv is not None and Decimal(nv) > 1:
                extra["source_anomaly"] = (f"Printed {pv} for a quantity bounded by 0 and 1; probably 1.0000 with the decimal point lost. "
                                           "numeric_value left null; the value is not interpreted.")
                nv = None
            vals[col_label] = (pv, nv)
            result(f"{ev}-{slug}".replace("-eval-", "-result-"), ev, S_CARBO_SUPP, f"{base}, cell {ref}, row '{tool}', column '{col_label}'",
                   cell, metric, direction, unit, qualifier=qual, unit_detail=udet, extra=extra or None, numeric=nv)
        sn, sl, d = vals["SN (ROC)"][1], vals["SL (ROC)"][1], vals["Informedness"][1]
        if sn is None or sl is None:
            roc_anomalous += 1
        else:
            if abs(math.hypot(1 - float(sn), 1 - float(sl)) - float(d)) > 0.0006:
                raise SystemExit(f"ROC distance check failed for {sheet} {tool} row {r}")
            roc_checked += 1
    need(seen, TOOLS, f"Carbo {sheet} block {lab} tools")
claim(f"{P}-claim-carbo2022-roc-distance-label", C_PROT["species-cutoff-0"], "metric_label",
      "The Supplementary Table 1 column headed 'Informedness' holds the ROC distance to the error-free point: Section 2.7 defines it so, and for every row with in-range sensitivity and selectivity the printed value equals sqrt((1 - SN)^2 + (1 - SL)^2) within rounding.",
      S_CARBO, "Section 2.7 paragraph 1; Supplementary Table 1, column 'Informedness'")
claim(f"{P}-claim-carbo2022-human-read-removal", C_PROT["species-cutoff-0"], "effect_of_host_read_removal",
      "Removing human reads before classification gave comparable sensitivity for all classifiers except CLARK, whose sensitivity fell at species and genus level; selectivity mostly increased, except for Kaiju and Kraken2 at family level.",
      S_CARBO, "Section 3.1 paragraph 1")

# ================================================================= de Vries et al. 2021 (ENNGS)
dev = workbook(PATHS["devries_supp"])
s2, s4 = dev["SuppS2 Target viruses"], dev["SuppS4 Additional findings"]
need(s2["A1"][0], "Supplementary table 2. Read counts, genome coverage (% or nt), and sensitivity of PCR positive target viruses detected by mNGS per classification tool (details of the pipeline can be found in table 1)", "ENNGS S2 title")
need(s2["R3"][0], "Number of samples correctly positive (mixed infections counted as single) out of 13 samples*", "ENNGS S2 R3")
need(s2["S3"][0], "Overall sensitivity [%], sample level", "ENNGS S2 S3")
TCOLS = list("CDEFGHIJKLMNOPQ")
SAMPLE_OF = {"C": 1, "D": 2, "E": 3, "F": 4, "G": 5, "H": 6, "I": 7, "J": 8, "K": 9, "L": 10, "M": 11, "N": 11, "O": 12, "P": 13, "Q": 13}
SPEC_OF = {c: s2[f"{c}5"][0].strip() for c in "CDEFGHIJKLMOP"}
SPEC_OF.update({"N": SPEC_OF["M"], "Q": SPEC_OF["P"]})
need([s2[f"{c}8"][0].strip() for c in TCOLS], ["HHV-6(A)", "HHV-6(B)", "Enterovirus", "EBV", "Mumps", "CoV-OC43", "Astrovirus VA1", "Inf-A", "PIV-3",
                                               "CoV-NL63", "CoV-NL63", "CoV-HKU-1", "CoV-HKU-1", "Adeno-virus", "EBV"], "ENNGS S2 target row 8")
need([s2[f"{c}4"][0] for c in "CDEFGHIJKLMOP"], [str(i) for i in range(1, 14)], "ENNGS S2 sample numbers row 4")
DNA_TARGETS = {"HHV-6(A)", "HHV-6(B)", "EBV", "Adeno-virus"}
S2_ROWS = [(13, "Centrifuge"), (18, "DAMIAN"), (23, "DIAMOND"), (28, "DIAMOND pipeline 3A (see table 1)"), (33, "DNAstar"), (38, "FEVIR"),
           (43, "Genome Detective"), (48, "Jovian"), (53, "MetaMIC"), (59, "MetaMix"), (64, "One Codex"), (69, "RIEMS"), (74, "Taxonomer"), (79, "VirMet")]
for r, name in S2_ROWS:
    need(s2[f"A{r}"][0].strip(), name, f"ENNGS S2 A{r}")
    need("Read count" in s2[f"B{r}"][0], True, f"ENNGS S2 B{r}")
S4_ROWS = [(10, "Centrifuge"), (15, "DAMIAN"), (17, "DIAMOND"), (20, "DNAstar"), (23, "FEVIR"), (25, "Genome Detective"), (29, "Jovian"),
           (31, "MetaMIC"), (32, "metaMix"), (37, "One Codex"), (38, "RIEMS"), (40, "Taxonomer"), (42, "VirMet")]
need(s4["A1"][0], "Supplementary table 4. Additional viral findings reported for each pipeline per sample. Highlighted are viruses with negative PCR results available.", "ENNGS S4 title")
S4_HEAD = {"O": "Number of additional viral mNGS hits with negative PCR reprsult (FP* see manuscript text for comments e.g. on index hopping)",
           "P": "TP (viral mNGS hits with positive PCR result, mixed infections counted as double, out of 15 positive PCRs)",
           "Q": "FN (number of PCR-positive hits not reported by mNGS)", "R": "Total mNGS hits with PCR data available (TP+FP)",
           "S": "Positive predictive value (PPV) [%]", "T": "Sensitivity [%], hit level"}
for c, h in S4_HEAD.items():
    need(s4[f"{c}5"][0], h, f"ENNGS S4 {c}5")
for r, name in S4_ROWS:
    need(s4[f"A{r}"][0].strip(), name, f"ENNGS S4 A{r}")
need(s4["C44"][0], "*Rotavirus was detected in the negative run control", "ENNGS S4 C44 footnote")

DEV_KEY = {"Centrifuge": "centrifuge", "DAMIAN": "damian", "DIAMOND": "diamond", "DNAstar": "dnastar", "FEVIR": "fevir",
           "Genome Detective": "genome-detective", "Jovian": "jovian", "MetaMIC": "metamic", "MetaMix": "metamix", "metaMix": "metamix",
           "One Codex": "one-codex", "RIEMS": "riems", "Taxonomer": "taxonomer", "VirMet": "virmet"}
COMMERCIAL = {"DNAstar", "Genome Detective", "One Codex", "Taxonomer"}
DEV_M = {"Centrifuge": CARBO_METHODS["Centrifuge"], "Genome Detective": CARBO_METHODS["GD"]}
for name, desc, kind, access in [
        ("DAMIAN", "Viral metagenomics pipeline (reference 26-27 of the source).", "method", None),
        ("DIAMOND", "Protein-level read alignment used as the classifier in a laboratory pipeline.", "method", None),
        ("DNAstar", "Commercial sequence analysis software (DNASTAR, Madison, WI, USA).", "method", "Commercial software (Results 'Metagenomic pipeline characteristics')"),
        ("FEVIR", "Viral metagenomics pipeline (reference 30 of the source).", "method", None),
        ("Jovian", "Viral metagenomics pipeline (reference 32 of the source).", "method", None),
        ("MetaMIC", "Viral metagenomics pipeline (reference 33 of the source).", "method", None),
        ("MetaMix", "Bayesian mixture-model read assignment with posterior probabilities of species presence (references 34-35 of the source).", "method", None),
        ("One Codex", "Hosted k-mer based classification platform (One Codex, San Francisco, USA).", "service", "Commercial web-based platform (Results 'Metagenomic pipeline characteristics')"),
        ("RIEMS", "Pipeline combining several established tools for pathogen detection (references 37-38 of the source).", "method", None),
        ("Taxonomer", "Hosted nucleotide and protein k-mer read assignment (Utah, USA).", "service", "Commercial web-based platform (Results 'Metagenomic pipeline characteristics')"),
        ("VirMet", "Viral metagenomics pipeline (reference 40 of the source).", "method", None)]:
    DEV_M[name] = method(DEV_KEY[name], name if name != "DNAstar" else "DNASTAR", desc, S_DEV, "Methods 'Bioinformatic pipelines'; Results 'Metagenomic pipeline characteristics'", kind=kind, access=access)
DEV_C = {}
for r, name in S2_ROWS:
    base = "DIAMOND" if name.startswith("DIAMOND") else name
    slug = "diamond-pipeline-3a" if name.startswith("DIAMOND pipeline") else DEV_KEY[base]
    cid = f"{P}-config-devries2021-{slug}"
    DEV_C[name] = cid
    configuration(cid, f"{name.replace(' (see table 1)', '')} as run by an ENNGS laboratory (de Vries et al. 2021)",
                  f"{name.replace(' (see table 1)', '')} as used at a participating diagnostic laboratory, with its own reference database and reporting criteria.",
                  DEV_M[base], [S_DEV, S_DEV_SUPP], name.replace(" (see table 1)", ""), f"Supplementary Table 2 cell A{r}; Methods 'Bioinformatic pipelines'",
                  version_missing={"reason": "unextracted", "note": "Pipeline details are in Table 1, which is an image in the preprint and was not transcribed"},
                  parameters="Own reference database and reporting criteria of the participating laboratory (Table 1, not transcribed)")
DEV_C["metaMix"] = DEV_C["MetaMix"]
D_DATA = f"{P}-data-devries2021-ennngs-13-clinical"
rec(D_DATA, "dataset", "ENNGS benchmark: 13 clinical metagenomic datasets with RT-PCR results (de Vries et al. 2021)",
    "Raw untrimmed datasets from patients with encephalitis, respiratory disease or fever, shared with all participants.", [S_DEV, S_DEV_SUPP], [],
    {"version": "Datasets as shared for the ENNGS benchmark (https://veb.lumc.nl/CliniMG)", "access": "Public download at https://veb.lumc.nl/CliniMG; part also via the COMPARE Data Hub",
     "population": "13 samples: CSF (4), brain biopsy (3), nasopharyngeal swab (3), nasal washing (1), BAL (1), plasma (1); 15 PCR-positive targets (two mixed infections), 10 RNA viruses and 5 DNA viruses (HHV-6A, HHV-6B, EBV twice, adenovirus).",
     "assay": "Brain biopsies: TruSeq stranded mRNA, NextSeq 500 81 bp paired; other samples: total nucleic acid with EAV and PhHV controls, NEBNext Ultra directional RNA library adapted for DNA and RNA, NextSeq 500 or NovaSeq 6000 150 bp paired; three CSF samples with vertebrate-virus capture probes; human reads removed with Bowtie2 2.3.4",
     "split": "No split", "denominator": 13,
     "source_locator": "Methods 'Datasets' paragraphs 1-3 and 'Data sharing'; Supplementary Table 2 rows 4-9"})
DP1, DP2 = f"{P}-protocol-devries2021-sample-level", f"{P}-protocol-devries2021-hit-level"
rec(DP1, "protocol", "Detection of RT-PCR-positive viruses per sample, with assigned read counts (de Vries et al. 2021 Supplementary Table 2)",
    "Each laboratory pipeline's read count for each PCR-positive target and the number of the 13 samples correctly positive.", [S_DEV, S_DEV_SUPP],
    [{"relation": "uses_data", "target_id": D_DATA}],
    {"protocol": "Participants analysed the same raw datasets blinded with their own pipelines, databases and reporting criteria. A sample counts as correctly positive when the PCR-positive virus is reported (mixed infections counted as one); sensitivity is the share of the 13 samples. Read counts are as reported, not normalised.",
     "version": "Supplementary Table 2", "denominator": 13, "source_locator": "Methods 'Bioinformatic pipelines' and 'Performance characteristics'; Supplementary Table 2",
     "limitations": ["13 samples; 5 of 15 targets are DNA viruses.", "Reference databases and reporting criteria differ by laboratory.", "Specimen types mixed (CSF, brain, respiratory, plasma)."],
     "missing_metadata": {"uncertainty": {"reason": "unreported"}}})
rec(DP2, "protocol", "Virus hits against RT-PCR: true and false positives, PPV and hit-level sensitivity (de Vries et al. 2021 Supplementary Table 4)",
    "Each pipeline's reported viral hits scored against available RT-PCR results, including additional viruses with negative PCR.", [S_DEV, S_DEV_SUPP],
    [{"relation": "uses_data", "target_id": D_DATA}],
    {"protocol": "TP: reported hit with a positive PCR (mixed infections counted as two; 15 positive PCRs). FP: additional reported viral hit with a negative PCR result. FN: PCR-positive hit not reported. PPV = TP / (TP + FP); sensitivity = TP / 15. Hits without PCR data are not scored.",
     "version": "Supplementary Table 4, columns O-T", "denominator": 15,
     "source_locator": "Results 'Additional virus hits and positive predictive value'; Supplementary Table 4 header row 5",
     "limitations": ["False positives are counted only where a negative PCR exists; most additional hits have no PCR result.",
                     "The authors note that FP hits may be real (PCR primer mismatch) or index hopping or reagent contaminants.",
                     "Rotavirus was detected in the negative run control (Supplementary Table 4 footnote)."],
     "missing_metadata": {"uncertainty": {"reason": "unreported"}}})
D_COMP = {"dataset_version": "ENNGS 13 shared datasets", "split": "No split", "population": "13 samples, 15 PCR-positive targets",
          "inputs": "Raw untrimmed FASTQ, human reads removed before sharing", "adaptation": "Each laboratory's own database and reporting criteria",
          "metric_implementation": "Organisers' scoring of reported hits against RT-PCR", "aggregation": "All samples", "budget": None}
for r, name in S2_ROWS:
    base = "DIAMOND" if name.startswith("DIAMOND") else name
    origin = "independent_paper" if base in COMMERCIAL or base == "Centrifuge" else ("unreported" if base == "DAMIAN" else "author_reported")
    lim = {"independent_paper": "Commercial or public tool run by a participating laboratory.",
           "author_reported": "Pipeline developed or adapted at a participating laboratory's site (Results 'Metagenomic pipeline characteristics'), whose staff co-author the paper.",
           "unreported": "Open-source pipeline run by participating laboratories; whether they developed it is not stated."}[origin]
    cid = DEV_C[name]
    ev = f"{P}-eval-devries2021-sample-{cid.split('-config-devries2021-')[1]}"
    extra = {"limitations": [lim]}
    if name.startswith("DIAMOND pipeline"):
        extra["limitations"].append("Row label 'DIAMOND pipeline 3A' conflicts with the Methods, which name DAMIAN as the pipeline run by two participants (A and B); no summary columns are printed for this row.")
    evaluation(ev, f"{name.replace(' (see table 1)', '')}: sample-level detection (ENNGS)", cid, DP1, D_DATA, [S_DEV, S_DEV_SUPP], origin, D_COMP,
               f"Supplementary Table 2 rows {r}-{r + 4}", extra=extra)
    for c in TCOLS:
        target = s2[f"{c}8"][0].strip()
        smp = SAMPLE_OF[c]
        q = f"reads assigned to PCR-positive {target}, sample {smp} ({SPEC_OF[c]})"
        ex = {"label_scope": "DNA virus target" if target in DNA_TARGETS else "RNA virus target"}
        result(f"{P}-result-devries2021-sample-{cid.split('-config-devries2021-')[1]}-reads-{c.lower()}", ev, S_DEV_SUPP,
               f"Supplementary Table 2, cell {c}{r}, row '{name}' read count, column sample {smp} ({target})", s2[f"{c}{r}"],
               "count", "unknown", "count", qualifier=q, unit_detail="reads (read pairs or single reads as labelled in column B), not normalised", extra=ex)
    if f"R{r}" in s2:
        result(f"{P}-result-devries2021-sample-{cid.split('-config-devries2021-')[1]}-correct", ev, S_DEV_SUPP,
               f"Supplementary Table 2, cell R{r}, row '{name}', column 'Number of samples correctly positive ... out of 13 samples*'", s2[f"R{r}"],
               "true-positive-count", "higher", "count", qualifier="samples correctly positive out of 13, mixed infections counted once", unit_detail="samples")
        result(f"{P}-result-devries2021-sample-{cid.split('-config-devries2021-')[1]}-sensitivity", ev, S_DEV_SUPP,
               f"Supplementary Table 2, cell S{r}, row '{name}', column 'Overall sensitivity [%], sample level'", s2[f"S{r}"],
               "recall", "higher", "percent", qualifier="sample level, 13 samples")
for r, name in S4_ROWS:
    base = "MetaMix" if name == "metaMix" else name
    origin = "independent_paper" if base in COMMERCIAL or base == "Centrifuge" else ("unreported" if base == "DAMIAN" else "author_reported")
    cid = DEV_C[name]
    ev = f"{P}-eval-devries2021-hit-{cid.split('-config-devries2021-')[1]}"
    evaluation(ev, f"{base}: virus hits against RT-PCR (ENNGS)", cid, DP2, D_DATA, [S_DEV, S_DEV_SUPP], origin, D_COMP,
               f"Supplementary Table 4 row {r}")
    for c, metric, direction, unit, qual, udet, slug in [
            ("O", "false-positive-count", "lower", "count", "additional viral hits with a negative PCR result", "virus hits", "fp"),
            ("P", "true-positive-count", "higher", "count", "hits with a positive PCR result, out of 15", "virus hits", "tp"),
            ("Q", "false-negative-count", "lower", "count", "PCR-positive hits not reported", "virus hits", "fn"),
            ("R", "count", "unknown", "count", "hits with PCR data available (TP + FP)", "virus hits", "hits-with-pcr"),
            ("S", "precision", "higher", "percent", "positive predictive value, hits with PCR data", None, "ppv"),
            ("T", "recall", "higher", "percent", "hit level, 15 PCR-positive hits", None, "sensitivity")]:
        result(f"{P}-result-devries2021-hit-{cid.split('-config-devries2021-')[1]}-{slug}", ev, S_DEV_SUPP,
               f"Supplementary Table 4, cell {c}{r}, row '{name}', column '{S4_HEAD[c]}'", s4[f"{c}{r}"], metric, direction, unit,
               qualifier=qual, unit_detail=udet)
claim(f"{P}-claim-devries2021-negative-control", DP2, "contamination_signal",
      "Rotavirus A was reported in sample cs10 by most pipelines and was also detected in the negative run control, which was not given to participants. Additional viruses reported by several pipelines included RD114 retrovirus, feline leukemia virus and bovine viral diarrhea virus (likely fetal bovine serum contaminants).",
      S_DEV_SUPP, "Supplementary Table 4 column C and footnote C44; Results 'Additional virus hits and positive predictive value' paragraph 1")

# ================================================================= Meyer et al. 2022 (CAMI II)
mey = workbook(PATHS["meyer_supp"])
t39 = mey["S Table 39"]
need(t39["A1"][0].strip(), "Supplementary Table 39: Results of the clinical pathogen prediction challenge.", "CAMI S Table 39 title")
need([t39[f"{c}2"][0] for c in "ABCD"], ["Software", "Causal pathogen in submitted list of taxa", "Predicted causal pathogen", "Reproducibility"], "CAMI S Table 39 header")
SUBS = ["Bracken v2.2", "Bracken v2.5", "LSHVec", "MetaPhlAn v2.2.0", "MetaPhlAn v2.9.14", "MetaPhyler v1.25", "NSSAC (full genome)",
        "NSSAC (assembly)", "Pathoscope v2.0.7", "CCMetagen v1.1.3"]
need([t39[f"A{r}"][0] for r in range(3, 13)], SUBS, "CAMI S Table 39 software rows")
M_M = {"Bracken": method("bracken", "Bracken", "Bayesian re-estimation of abundance from Kraken read assignments.", S_MEY, "Supplementary Table 39"),
       "LSHVec": method("lshvec", "LSHVec", "Read embedding with locality-sensitive hashing for taxonomic classification.", S_MEY, "Supplementary Table 39"),
       "MetaPhlAn": "catalog-model-metaphlan",
       "MetaPhyler": method("metaphyler", "MetaPhyler", "Marker-gene taxonomic profiler.", S_MEY, "Supplementary Table 39"),
       "NSSAC": method("nssac", "NSSAC", "Submission labelled NSSAC (full genome or assembly based); the method is not described in the source.", S_MEY, "Supplementary Table 39"),
       "Pathoscope": method("pathoscope", "PathoScope", "Read-reassignment pathogen identification from alignments.", S_MEY, "Supplementary Table 39"),
       "CCMetagen": method("ccmetagen", "CCMetagen", "Metagenomic classifier using KMA alignment to reference databases (reference 49 of the source).", S_MEY, "Supplementary Table 39; Results reference 49")}
M_DATA = f"{P}-data-meyer2022-cami2-clinical-pathogen"
rec(M_DATA, "dataset", "CAMI II clinical pathogen challenge: blood metagenome from a patient with haemorrhagic fever",
    "One short-read metagenome provided with a modified case report; causal pathogen Crimean-Congo haemorrhagic fever orthonairovirus (CCHFV).", [S_MEY], [],
    {"version": "CAMI II pathogen challenge dataset (688 MB paired-end MiSeq)", "population": "One blood sample; CCHFV sequences previously found and confirmed by PCR (Ct 27.4); human reads replaced by reads from the same regions of the 1000 Genomes data.",
     "split": "Single sample", "denominator": 1, "source_locator": "Methods 'Challenge datasets' paragraph 5"})
MP = f"{P}-protocol-meyer2022-causal-pathogen"
rec(MP, "protocol", "Identify all pathogens and the causal pathogen in one clinical blood metagenome (CAMI II clinical pathogen challenge)",
    "Each submission's list of taxa and predicted causal pathogen, compared with CCHFV.", [S_MEY, S_MEY_SUPP], [{"relation": "uses_data", "target_id": M_DATA}],
    {"protocol": "Participants received the metagenome and a case description and submitted all pathogens found and the one most likely to cause the symptoms. Scored as whether CCHFV appears in the submitted taxa and whether it is the predicted causal pathogen.",
     "version": "Supplementary Table 39", "denominator": 1, "source_locator": "Results 'Clinical pathogen prediction: a concept challenge'; Methods 'Challenge datasets' paragraph 5 and 'Challenge organization'",
     "limitations": ["One sample; the causal role of CCHFV is the most plausible explanation, not clinically proven (Methods).",
                     "Submissions were manually curated and not reproducible.", "No false-positive or contamination scoring is printed; the number of taxa per submission is in Supplementary Fig. 16 only."],
     "missing_metadata": {"uncertainty": {"reason": "inapplicable", "note": "Single categorical outcome per submission"}}})
for i, sub in enumerate(SUBS):
    r = i + 3
    fam = sub.split(" ")[0]
    ver = sub.split(" v")[1] if " v" in sub else None
    slug = re.sub(r"[^a-z0-9]+", "-", sub.lower()).strip("-")
    cid = f"{P}-config-meyer2022-{slug}"
    configuration(cid, f"{sub} (CAMI II pathogen challenge submission)", f"{sub} as submitted to the CAMI II clinical pathogen challenge.", M_M[fam],
                  [S_MEY_SUPP], sub, f"Supplementary Table 39 cell A{r}", version=ver,
                  version_missing=None if ver else {"reason": "unreported", "note": "No version printed in Supplementary Table 39"})
    ev = f"{P}-eval-meyer2022-{slug}"
    evaluation(ev, f"{sub}: CAMI II clinical pathogen challenge", cid, MP, M_DATA, [S_MEY, S_MEY_SUPP], "unreported",
               {"dataset_version": "CAMI II pathogen challenge dataset", "split": "Single sample", "population": "One blood metagenome",
                "inputs": "Paired-end MiSeq reads with human reads replaced", "adaptation": "Submitter's own database and curation",
                "metric_implementation": "Organisers' comparison with CCHFV", "aggregation": "Single sample", "budget": None},
               f"Supplementary Table 39 row {r}", extra={"reproduction_note": f"Reproducibility as printed: {t39[f'D{r}'][0]}"})
    claims_rows.append([ev, S_MEY_SUPP, f"Supplementary Table 39 cell D{r}, row '{sub}', column 'Reproducibility'", t39[f"D{r}"][0], "evaluation_attribute"])
    for c, qual, s in [("B", "CCHFV (causal pathogen) present in the submitted list of taxa", "in-list"),
                       ("C", "submitted causal-pathogen prediction is CCHFV", "predicted-causal")]:
        pv = t39[f"{c}{r}"][0]
        need(pv in ("yes", "no"), True, f"CAMI S Table 39 {c}{r}")
        result(f"{P}-result-meyer2022-{slug}-{s}", ev, S_MEY_SUPP, f"Supplementary Table 39 cell {c}{r}, row '{sub}', column '{t39[c + '2'][0]}'",
               None, "success-rate", "higher", "unitless", qualifier=qual, printed=pv,
               extra={"criterion": f"{qual}; categorical yes/no outcome on one sample, so numeric_value is null"})

# ================================================================= relevance judgements
JUDGEMENTS = []
CONSTRAINTS = ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
               "Do not combine these results with another protocol's results; specimens, databases and scoring rules differ between sources."]


def judgement(short, pid, pname, relevance, endpoint, rationale, limitations, cites, group, title, headline, stratum=None, order=None):
    jid = f"use-case-mapping-rna-pathogen-20261009-{short}"
    attrs = {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": relevance, "endpoint": endpoint, "rationale": rationale,
             "constraints": CONSTRAINTS, "limitations": limitations,
             "citation_locators": [{"source_id": s, "locator": l} for s, l in cites],
             "source_locator": "; ".join(f"{s}: {l}" for s, l in cites), "revision": 1,
             "reason": "Recorded from the RNA pathogen-detection use-case pass 2026-10-09 (data/omics/use-case-coverage-rna-pathogen-20261009). Draft until an independent review.",
             "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum:
        attrs["stratum_label"], attrs["stratum_order"] = stratum, order
    rec(jid, "claim", f"Relevance of {pname} to \"{UC_NAME}\"", rationale, sorted({s for s, _ in cites}),
        [{"relation": "subject", "target_id": UC}], attrs, facets={})
    JUDGEMENTS.append({"judgement_id": jid, "protocol_id": pid, "relevance": relevance, "comparison_group": group,
                       **({"stratum_label": stratum, "stratum_order": order} if stratum else {})})


for key, (label, order) in C_LABEL.items():
    direct = not key.startswith("family")
    judgement(f"carbo2022-{key}", C_PROT[key], f"respiratory virus detection against PCR, {label.lower()} (Carbo et al. 2022)",
              "direct" if direct else "proxy",
              f"Sensitivity, selectivity (specificity), PPV, NPV, AUC and ROC distance against 1144 respiratory PCR results for Centrifuge, CLARK, Kaiju, Kraken2 and Genome Detective, each with human reads kept, removed, or removed with genome-length normalisation; {label.lower()}",
              ("Five classifiers on the same 88 respiratory specimens scored against a 13-target RNA respiratory virus PCR panel, with and without host read removal, measure detection and spurious calls in the use case's intended specimen. "
               + ("Species and genus assignment correspond to reportable pathogen identifications." if direct else
                  "Family-level assignment is proxy evidence because it does not identify the pathogen at a reportable level.")),
              ["Single cohort of COPD nasal washings; 24 PCR-positive results.", "Values come from the preprint supplement; the published supplement could not be retrieved.",
               "Four cells print 10000 for a fraction (probably 1.0000); their numeric values are left null.",
               "The column labelled 'Informedness' is the ROC distance (Section 2.7)."],
              [(S_CARBO_SUPP, f"Supplementary Table 1, {label}"), (S_CARBO, "Sections 2.3-2.7, 3.1; Table 2")],
              "carbo2022-respiratory", "Five classifiers against a respiratory PCR panel (Carbo et al. 2022)", "recall", label, order)
judgement("devries2021-sample-level", DP1, "sample-level detection by 14 laboratory pipelines (ENNGS, de Vries et al. 2021)", "proxy",
          "Number of 13 clinical samples correctly positive, sample-level sensitivity and reported read counts for each PCR-positive target, for 13 pipelines (14 rows) run by European clinical virology laboratories",
          "The same clinical datasets analysed blind by each laboratory's own pipeline measure detection, including low-abundance targets and mixed infections. It is proxy evidence because 5 of 15 targets are DNA viruses, specimens include CSF, brain and plasma, and each laboratory used its own database and reporting rules.",
          ["13 samples; 5 of 15 PCR-positive targets are DNA viruses.", "Specimen types mixed; respiratory samples are 5 of 13.",
           "Preprint supplement; the published version could not be retrieved; Table 1 (pipeline details) is an image and was not transcribed.",
           "Row 'DIAMOND pipeline 3A' conflicts with the Methods (DAMIAN run by two participants); evidence concern on the supplement source."],
          [(S_DEV_SUPP, "Supplementary Table 2"), (S_DEV, "Methods; Results 'Detection of PCR targeted viral pathogens; sensitivity'")],
          "devries2021-ennngs", "Thirteen laboratory pipelines on 13 clinical datasets (ENNGS, de Vries et al. 2021)", "recall", "Sample level", 1)
judgement("devries2021-hit-level", DP2, "virus-hit PPV and sensitivity of 13 laboratory pipelines (ENNGS, de Vries et al. 2021)", "proxy",
          "True positives, false positives (additional hits with a negative PCR), false negatives, PPV and hit-level sensitivity for 13 pipelines on 13 clinical datasets",
          "Counting additional reported viruses that have a negative PCR result measures how each pipeline separates real detections from background, which is the second half of the use-case question. It is proxy evidence because few additional hits have PCR data, samples are mixed DNA and RNA and mixed specimen types, and databases differ by laboratory.",
          ["False positives are counted only where a negative PCR exists.", "Rotavirus in the negative run control shows reagent or cross-sample contamination that participants could not see.",
           "Preprint supplement; published version not retrieved."],
          [(S_DEV_SUPP, "Supplementary Table 4, columns O-T"), (S_DEV, "Results 'Additional virus hits and positive predictive value'")],
          "devries2021-ennngs", "Thirteen laboratory pipelines on 13 clinical datasets (ENNGS, de Vries et al. 2021)", "precision", "Virus hit level", 2)
judgement("meyer2022-cami2-pathogen", MP, "the CAMI II clinical pathogen challenge (Meyer et al. 2022)", "proxy",
          "Whether each of 10 submissions listed CCHFV among the pathogens found, and whether it named CCHFV as the causal pathogen, in one blood metagenome",
          "Identifying an RNA virus as the causal pathogen among all taxa in a real clinical blood metagenome bears on detection and on separating a real finding from background. It is proxy evidence: one sample, a blood specimen outside the use case's respiratory scope, manually curated and non-reproducible submissions, and a table that conflicts with the text on the two Bracken versions.",
          ["One blood sample; outside the respiratory specimen scope.", "Submissions manually curated, not reproducible.",
           "Supplementary Table 39 and the Results text disagree on which Bracken version predicted the causal pathogen (evidence concern)."],
          [(S_MEY_SUPP, "Supplementary Table 39"), (S_MEY, "Results 'Clinical pathogen prediction: a concept challenge'; Methods 'Challenge datasets'")],
          "meyer2022-cami2-pathogen", "Causal RNA virus in a blood metagenome (CAMI II, Meyer et al. 2022)", "success-rate")

# ================================================================= write
records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
if len(ids) != len(set(ids)):
    raise SystemExit("Duplicate IDs: " + ", ".join(k for k, v in Counter(ids).items() if v > 1))
with open(f"{BATCH}/batch.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claims_rows.sort(key=lambda r: (r[0], r[2]))
with open(f"{BATCH}/claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
with open(f"{BATCH}/extract/judgements.json", "w", encoding="utf-8") as f:
    json.dump(JUDGEMENTS, f, indent=2, ensure_ascii=False)
print(json.dumps(Counter(r["kind"] for r in records), sort_keys=True), "roc_checked", roc_checked, "roc_anomalous", roc_anomalous)
