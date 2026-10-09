"""Deterministic extraction of RNA fusion caller comparison tables into a records batch.

Usage: python3 -I extract_rna_fusion.py <pinned-dir> <batch-dir>

<pinned-dir> holds the pinned artifacts under the names in ARTIFACTS. The script checks each SHA-256, reads the
tables, asserts every row and column label it depends on, and writes batch.jsonl and claims.csv in the current
store shape. The supplementary PDF is read with `pdftotext -layout` (poppler); its version is printed. Nothing
is marked reviewed.
"""
import csv, hashlib, json, os, re, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

PINNED, BATCH = sys.argv[1], sys.argv[2]
P = "rna-fusion-20261009"
UC = "use-case-tumour-rna-fusion-detection"
FACETS = {"areas": ["rna-transcriptomes"], "contexts": ["clinical_research"]}
TODAY = "2026-10-09"
ARTIFACTS = {
    "tamura2026-article.xml": "540cf971970ad98557f3d4511f09c3f06a1b4359fe9276a25e29e731e36c0fc1",
    "tamura2026-supplementary-information.pdf": "f18ada098fd03b0842c63a8ab9d13002e1876b006243e42c640a118ea3ab3275",
    "lin2026-article.xml": "8cc3b4bca5e2fe9b068a1e891366854d974f3df3102425959e600b9ea19f87b6",
}
records, claims_rows, judgements = [], [], []


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
    "tp": dict(metric="true-positive-count", metric_direction="higher", unit="count"),
    "fp": dict(metric="false-positive-count", metric_direction="lower", unit="count"),
    "fn": dict(metric="false-negative-count", metric_direction="lower", unit="count"),
    "tpr": dict(metric="recall", metric_direction="higher", unit="fraction"),
    "ppv": dict(metric="precision", metric_direction="higher", unit="fraction"),
    "f1": dict(metric="f1-score", metric_direction="higher", unit="fraction"),
    "spec": dict(metric="specificity", metric_direction="higher", unit="fraction"),
}


def result(id_, eval_id, source_ids, artifact_sha, url, locator, printed, metric, qualifier, how, unit_detail=None):
    attrs = {**METRIC[metric], "metric_qualifier": qualifier, "printed_value": printed, "source_locator": locator,
             "missing_metadata": {"uncertainty": {"reason": "unreported"}},
             "review": {**review_note(how), "artifact_sha256": artifact_sha, "retrieval_url": url}}
    if unit_detail:
        attrs["unit_detail"] = unit_detail
    if printed == "na":
        attrs["numeric_value"] = None
        attrs["undefined_reason"] = "Printed 'na': the source footnote says PPV is undefined because its denominator is 0; F1 is then also undefined."
    else:
        t = printed.replace(",", "")
        assert re.fullmatch(r"\d+(\.\d+)?", t), printed
        attrs["numeric_value"] = format(Decimal(t), "f")
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
    rec(id_, "evaluation", name, "Published fusion caller comparison; transcribed, not reproduced.", source_ids,
        [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
         {"relation": "data", "target_id": dataset}], attrs)


METHODS = {}
METHOD_INFO = {
    "arriba": ("Arriba", "STAR-based fusion detection with artefact filters."),
    "fusioncatcher": ("FusionCatcher", "Fusion finder combining several aligners."),
    "star-fusion": ("STAR-Fusion", "Fusion detection from STAR chimeric alignments (Trinity CTAT)."),
    "jaffa": ("JAFFA", "Fusion detection by alignment to transcript references; JAFFA-direct for short reads, JAFFAL for long reads."),
    "pizzly": ("Pizzly", "Fusion detection from kallisto pseudoalignment."),
    "genomon": ("Genomon fusion", "STAR-based fusion detection in the Genomon pipeline."),
    "ericscript": ("EricScript", "Fusion detection from BWA alignment to the transcriptome."),
    "trinityfusion": ("TrinityFusion", "Fusion detection from de novo Trinity assembly, in modes D, UC and C."),
    "infusion": ("InFusion", "Bowtie2-based fusion detection."),
    "starchip": ("STARChip", "Fusion and circular RNA detection from STAR chimeric output."),
    "fusionseeker": ("FusionSeeker", "Long-read fusion detection by clustering split alignments."),
    "longgf": ("LongGF", "Long-read fusion detection from minimap2 alignments and a GTF."),
    "fusilli": ("FUSILLI", "Long-read fusion detection focused on B-ALL fusion genes (developed by the authors of Lin et al. 2026)."),
}


def method(key, source_ids, method_types=("conventional_pipeline",), extra=None):
    mid = f"{P}-method-{key}"
    if mid in METHODS:
        for s in source_ids:
            if s not in METHODS[mid]["source_ids"]:
                METHODS[mid]["source_ids"].append(s)
        return mid
    name, desc = METHOD_INFO[key]
    attrs = {"reported_name": name, "entity_level": "method", "source_locator": "Tool lists and table row labels of the cited sources",
             "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}
    if extra:
        attrs.update(extra)
    METHODS[mid] = rec(mid, "method", name, desc, list(source_ids), [], attrs, facets={**FACETS, "method_types": list(method_types)})
    return mid


def judgement(short, protocol, protocol_name, source_ids, relevance, endpoint, rationale, constraints, limitations,
              locators, group, title, headline, stratum=None, order=None):
    cid = f"use-case-mapping-{P}-{short}"
    attrs = {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance,
             "endpoint": endpoint, "rationale": rationale, "constraints": constraints, "limitations": limitations,
             "revision": 1,
             "reason": "Add primary-source fusion caller comparison evidence from the tumour RNA fusion use-case pass (2026-10-09).",
             "citation_locators": [{"source_id": s, "locator": l} for s, l in locators],
             "source_locator": "; ".join(f"{s}: {l}" for s, l in locators),
             "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum is not None:
        attrs["stratum_label"] = stratum
        attrs["stratum_order"] = order
    rec(cid, "claim", f"Relevance of {protocol_name} to \"Select a tumour RNA fusion-detection workflow\"", rationale, source_ids,
        [{"relation": "subject", "target_id": UC}], attrs, facets={})
    judgements.append(cid)


CONSTRAINTS = ["Inspect every linked evaluation's source locator before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; truth sets, specimens, sequencing and caller versions differ between sources."]

# =============================================================================================
# A. Tamura et al. 2026, NPJ Precision Oncology 10:199, Supplementary Tables 1, 3 and 5
# =============================================================================================
A_ART, A_SUP = f"{P}-source-tamura2026", f"{P}-source-tamura2026-supplementary"
A_SRC = [A_ART, A_SUP]
A_SUP_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41698-026-01397-y/MediaObjects/41698_2026_1397_MOESM1_ESM.pdf"
A_SUP_SHA = ARTIFACTS["tamura2026-supplementary-information.pdf"]
rec(A_ART, "source", "Comparison of gene fusion detection algorithms reveals frequently overlooked driver fusions in hematologic malignancies",
    "Primary source retrieved and hashed for the tumour RNA fusion use-case pass.", [], [],
    {"url": "https://doi.org/10.1038/s41698-026-01397-y", "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13230599/fullTextXML",
     "version": "NPJ Precision Oncology 10:199, published 2026-04-04; PMC13230599 full-text XML",
     "retrieved_at": "2026-10-09T20:37:17Z", "artifact_sha256": ARTIFACTS["tamura2026-article.xml"],
     "doi": "10.1038/s41698-026-01397-y", "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0",
     "media_type": "application/xml"})
rec(A_SUP, "source", "Tamura et al. 2026, Supplementary Information (Supplementary Tables 1-12)",
    "Supplementary PDF with per-algorithm detection statistics.", [], [],
    {"url": "https://doi.org/10.1038/s41698-026-01397-y", "artifact_url": A_SUP_URL,
     "version": "41698_2026_1397_MOESM1_ESM.pdf as served by the publisher",
     "retrieved_at": "2026-10-09T20:37:37Z", "artifact_sha256": A_SUP_SHA,
     "doi": "10.1038/s41698-026-01397-y", "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0",
     "media_type": "application/pdf"})

version = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr.splitlines()[0]
print(version)
text = subprocess.run(["pdftotext", "-layout", os.path.join(PINNED, "tamura2026-supplementary-information.pdf"), "-"],
                      capture_output=True, text=True, check=True).stdout
lines = [l.replace("\f", "").rstrip() for l in text.split("\n")]  # splitlines() would also split at form feeds
A_HOW = (f"Extracted by deterministic parse of the pinned supplementary PDF text layer ({version}, -layout) in "
         "extract/extract_rna_fusion.py, with table titles, sub-table headings, column headers and algorithm labels asserted. "
         "printed_value is the cell as printed, including thousands separators.")


def find(prefix, start=0):
    for i in range(start, len(lines)):
        if lines[i].strip().startswith(prefix):
            return i
    raise AssertionError(prefix)


ALGS = ["Arriba", "FusionCatcher", "STAR-Fusion", "JAFFA-direct", "Pizzly", "Genomon", "EricScript",
        "TrinityFusion-D", "TrinityFusion-UC", "TrinityFusion-C", "InFusion", "STARChip"]
ALG_METHOD = {"Arriba": "arriba", "FusionCatcher": "fusioncatcher", "STAR-Fusion": "star-fusion", "JAFFA-direct": "jaffa",
              "Pizzly": "pizzly", "Genomon": "genomon", "EricScript": "ericscript", "TrinityFusion-D": "trinityfusion",
              "TrinityFusion-UC": "trinityfusion", "TrinityFusion-C": "trinityfusion", "InFusion": "infusion", "STARChip": "starchip"}
t1 = find("Supplementary Table 1. List of 12 gene fusion detection algorithms.", 1390)
hdr1 = next(i for i in range(t1, t1 + 8) if lines[i].split()[:3] == ["Algorithm", "Alignment", "method"])
T1 = {}
for k, alg in enumerate(ALGS):
    row = lines[hdr1 + 1 + k]
    assert row.startswith(alg + " "), (alg, row)
    cols = re.split(r"\s{2,}", row.strip())
    if len(cols) == 4 and cols[3].rsplit(" ", 1)[-1] in ("Default", "Recommended"):
        cols = cols[:3] + cols[3].rsplit(" ", 1)  # aligner and parameter columns run together in the text layer
    assert cols[0] == alg and len(cols) == 5 and cols[4] in ("Default", "Recommended"), cols
    T1[alg] = {"alignment": cols[1], "version": cols[2], "aligner": cols[3], "parameters": cols[4]}
A_CONF = {}
for alg in ALGS:
    mid = method(ALG_METHOD[alg], [A_ART])
    info = T1[alg]
    A_CONF[alg] = rec(f"{P}-config-tamura2026-{alg.lower()}", "configuration", f"{alg} {info['version']} (Tamura et al. 2026)",
                      f"{alg} as run in the cited comparison.", A_SRC, [{"relation": "configuration_of", "target_id": mid}],
                      {"reported_name": alg, "version": info["version"], "foundation_model_eligible": False,
                       "protocol": (f"{info['parameters']} parameters; alignment method {info['alignment']}"
                                    + (f"; aligner {info['aligner']}" if info["aligner"] != "---" else "")
                                    + "; GRCh38; filtered output used where available"),
                       "source_locator": "Supplementary Table 1; Methods 'Detection of gene fusions by each algorithm'"},
                      facets={**FACETS, "method_types": ["conventional_pipeline"]})["id"]

A_DATA = {
    "conventional": rec(f"{P}-data-tamura2026-ccle-heme-conventional", "dataset",
                        "CCLE haematologic malignancy cell lines, conventional RNA-seq (170 cell lines)",
                        "Conventional RNA-seq input in Tamura et al. 2026.", A_SRC, [],
                        {"population": "170 haematologic cancer cell lines from CCLE (DepMap 22Q1 lineage Blood, Lymphocyte or Plasma cell with RNA-seq)",
                         "split": "All 170 cell lines", "source_locator": "Methods 'Conventional RNA-seq'; Supplementary Table 2",
                         "missing_metadata": {"version": {"reason": "unreported"}}})["id"],
    "targeted": rec(f"{P}-data-tamura2026-heme-targeted", "dataset",
                    "Haematologic cancer cell lines, hybridisation-capture targeted RNA-seq (26 cell lines)",
                    "Targeted RNA-seq cell-line input in Tamura et al. 2026.", A_SRC, [],
                    {"population": "26 cell lines profiled with the authors' custom capture RNA assay (44 fusion-target genes, 32 SV genes, IG/TCR genes, 134 fusion junctions)",
                     "split": "All 26 cell lines", "source_locator": "Methods 'Targeted RNA-seq'; Supplementary Table 6",
                     "missing_metadata": {"version": {"reason": "unreported"}}})["id"],
}
SUBS = [
    ("Supplementary Table 3. Detection statistics of all gene fusions for each gene fusion detection", "all", True),
    ("Supplementary Table 5. Detection statistics of driver gene fusions for each gene fusion", "driver", False),
]
HEAD3 = ["Algorithm", "Size", "of", "truth", "set", "True", "positive", "False", "positive", "False", "negative", "True",
         "positive", "rate", "Positive", "predictive", "value", "F1"]
HEAD5 = HEAD3[:1] + HEAD3[5:]
order = {"all": 0, "driver": 0}
for title, scope, has_truth in SUBS:
    t = find(title, 1600)
    for assay in ("conventional", "targeted"):
        label = {"conventional": "Conventional RNA-seq of cell lines", "targeted": "Targeted RNA-seq of cell lines"}[assay]
        h = find(label, t)
        assert lines[h + 1].split() == (HEAD3 if has_truth else HEAD5), lines[h + 1]
        order[scope] += 1
        pid = f"{P}-protocol-tamura2026-{scope}-{assay}"
        if scope == "all":
            pname = f"All fusions, {assay} RNA-seq of haematologic cell lines, consensus truth (Tamura et al. 2026 Supplementary Table 3)"
            ptxt = ("Truth: fusion-cell line pairs detected by at least four algorithms other than the one evaluated (TrinityFusion modes count as one vote); "
                    "false positives: fusions detected by that algorithm alone; TPR, PPV and F1 by standard formulas.")
            lims = ["Truth is consensus among the other algorithms, without orthogonal validation except for driver fusions, so it favours callers that agree with the majority.",
                    "False positives are fusions called by one algorithm only; some may be real.",
                    "Truth-set size differs by algorithm (printed per row).",
                    "Haematologic cell lines only; not solid tumours or clinical specimens."]
        else:
            n = {"conventional": 61, "targeted": 24}[assay]
            pname = f"Driver fusions, {assay} RNA-seq of haematologic cell lines, validated truth (Tamura et al. 2026 Supplementary Table 5)"
            ptxt = (f"Truth: {n} driver fusion-cell line pairs from a curated list of 202 haematologic driver fusions, each reported in the literature or confirmed by RT-PCR and Sanger sequencing; "
                    "false positives: listed driver fusions detected by one algorithm only.")
            lims = ["Driver fusions in haematologic cell lines only; sensitivity for other fusions and tumour types is not measured.",
                    "Truth pairs were first selected among calls by at least four algorithms (plus a few literature-reported pairs), so fusions missed by most callers are under-represented.",
                    "Few false positives are possible by construction, so precision is less informative than sensitivity (Results paragraph 4).",
                    "Haematologic cell lines only; not solid tumours or clinical specimens."]
        rec(pid, "protocol", pname, f"Per-algorithm TP, FP, FN, TPR, PPV and F1 for {scope} fusions on {assay} RNA-seq.", A_SRC,
            [{"relation": "uses_data", "target_id": A_DATA[assay]}],
            {"protocol": ptxt + " Default or recommended parameters, GRCh38.",
             "version": f"{title.split('.')[0]}, '{label}'", "metric": "recall", "limitations": lims,
             "source_locator": f"{title.split('.')[0]}, sub-table '{label}'; Methods 'Comparison of detection algorithms'"}
            | ({"denominator": n} if scope == "driver" else {}))
        for k, alg in enumerate(ALGS):
            row = lines[h + 2 + k].split()
            assert row[0] == alg and len(row) == (8 if has_truth else 7), (scope, assay, row)
            vals = row[1:]
            eid = f"{P}-eval-tamura2026-{alg.lower()}-{scope}-{assay}"
            extra = None
            if has_truth:
                extra = {"denominator": int(vals[0].replace(",", ""))}
                claims_rows.append([eid, A_SUP, f"{title.split('.')[0]}, '{label}', row '{alg}', column 'Size of truth set'", vals[0], "evaluation"])
                vals = vals[1:]
            evaluation(eid, f"{alg} on {scope} fusions, {assay} RNA-seq (Tamura et al. 2026)", A_CONF[alg], pid, A_DATA[assay], A_SRC,
                       "independent_paper",
                       {"dataset_version": None, "split": "All cell lines", "population": f"{'170' if assay == 'conventional' else '26'} cell lines",
                        "inputs": f"{assay.capitalize()} RNA-seq FASTQ, GRCh38", "adaptation": None,
                        "metric_implementation": "Gene pair and orientation match after HGNC alias resolution (Methods)",
                        "aggregation": "Pooled over fusion-cell line pairs", "budget": None},
                       f"{title.split('.')[0]}, '{label}', row '{alg}'",
                       missing={"comparison.dataset_version": {"reason": "unreported"}}, extra=extra)
            for v, (m, col) in zip(vals, [("tp", "True positive"), ("fp", "False positive"), ("fn", "False negative"),
                                          ("tpr", "True positive rate"), ("ppv", "Positive predictive value"), ("f1", "F1")]):
                result(f"{P}-result-tamura2026-{alg.lower()}-{scope}-{assay}-{METRIC[m]['metric']}", eid, A_SRC, A_SUP_SHA, A_SUP_URL,
                       f"{title.split('.')[0]}, '{label}', row '{alg}', column '{col}' (PDF page text)", v, m,
                       f"{scope} fusions, {assay} RNA-seq of cell lines", A_HOW,
                       "counted entity: fusion-cell line pairs" if m in ("tp", "fp", "fn") else None)
        rel = "direct" if scope == "driver" else "proxy"
        judgement(f"tamura2026-{scope}-{assay}", pid, pname, A_SRC, rel,
                  f"TP, FP, FN, TPR, PPV and F1 for {scope} fusions on {assay} RNA-seq of haematologic cell lines for 12 algorithms",
                  ("Validated driver fusions in cancer cell lines directly measure each caller's sensitivity for clinically relevant fusions, "
                   "run by a group that developed none of the 12 algorithms." if scope == "driver" else
                   "Shows the false-positive burden of each caller on real RNA-seq, but against a consensus truth set built from the other callers, so it is proxy evidence for accuracy."),
                  CONSTRAINTS, lims, [(A_SUP, f"{title.split('.')[0]}, '{label}'"), (A_ART, "Methods 'Comparison of detection algorithms'; Results")],
                  f"tamura2026-{scope}", ("Validated driver fusions in haematologic cell lines (Tamura et al. 2026)" if scope == "driver"
                                         else "All fusions against a consensus truth set (Tamura et al. 2026)"),
                  "recall" if scope == "driver" else "f1-score", stratum=f"{assay.capitalize()} RNA-seq", order=order[scope])
    note_line = next(l for l in lines[t:t + 60] if "“na” indicates an undefined PPV" in l)
    assert "denominator being 0" in note_line

# =============================================================================================
# B. Lin et al. 2026, Journal of Molecular Diagnostics 28(5):406, Tables 3 and 6
# =============================================================================================
B_ART = f"{P}-source-lin2026"
B_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13197905/fullTextXML"
B_SHA = ARTIFACTS["lin2026-article.xml"]
rec(B_ART, "source", "Long-Read Whole-Transcriptome Sequencing and Selective Gene Panel Profiling Enable Sensitive Detection of Fusion Oncogenes in Pediatric B-Cell Acute Lymphoblastic Leukemia",
    "Primary source retrieved and hashed for the tumour RNA fusion use-case pass.", [], [],
    {"url": "https://doi.org/10.1016/j.jmoldx.2026.01.007", "artifact_url": B_URL,
     "version": "Journal of Molecular Diagnostics 28(5):406, published 2026-02-10; PMC13197905 full-text XML",
     "retrieved_at": "2026-10-09T20:38:17Z", "artifact_sha256": B_SHA, "doi": "10.1016/j.jmoldx.2026.01.007",
     "publication_status": "peer_reviewed", "licence": "CC-BY-NC-4.0", "media_type": "application/xml"})
art = ET.parse(os.path.join(PINNED, "lin2026-article.xml"))
tx = lambda e: " ".join(" ".join(e.itertext()).split())
B_HOW = ("Extracted by deterministic parse of Tables 3 and 6 (table-wrap tbl3, tbl6) in the pinned article XML "
         "(extract/extract_rna_fusion.py), with captions, headers and algorithm labels asserted. printed_value is the cell text.")
B_CALLERS = {"FusionSeeker": ("fusionseeker", "GitHub install (Maggi-Chen/FusionSeeker), nanopore mode, Ensembl 104 GTF, hg38 minimap2 BAM"),
             "JAFFAL": ("jaffa", "docker://davidsongroup/jaffa:latest via apptainer, all confidence levels kept, local reformat qin=33"),
             "LongGF": ("longgf", "GitHub install (WGLab/LongGF) adapted for RefSeq GTF, minimap2 BAM sorted by read name; parameters in Supplemental Table S3"),
             "FUSILLI": ("fusilli", "Authors' tool; minimap2 PAF and B-ALL gene BED; at least two supporting reads")}
B_CONF = {}
for alg, (mkey, proto) in B_CALLERS.items():
    mid = method(mkey, [B_ART])
    B_CONF[alg] = rec(f"{P}-config-lin2026-{alg.lower()}", "configuration", f"{alg} on nanopore cDNA reads (Lin et al. 2026)",
                      f"{alg} as run in the cited comparison.", [B_ART], [{"relation": "configuration_of", "target_id": mid}],
                      {"reported_name": alg, "foundation_model_eligible": False, "protocol": proto,
                       "source_locator": f"Materials and Methods '{alg}' and 'Data Preprocessing'",
                       "missing_metadata": {"version": {"reason": "unreported", "note": "No release number printed; installation source and access dates only"}}},
                      facets={**FACETS, "method_types": ["conventional_pipeline"]})["id"]
B_DATA = rec(f"{P}-data-lin2026-ball-nanopore", "dataset", "Paediatric B-ALL nanopore PCR-cDNA whole-transcriptome sequencing (UNC, St Jude, ECOG-ACRIN)",
             "Long-read input in Lin et al. 2026.", [B_ART], [],
             {"population": "High-depth cohort: 51 samples (27 with a known B-ALL fusion), mean 11.2 M reads; low-depth cohort: 119 sequencing runs of 68 samples (79 runs with a known fusion), mean 1.4 M reads",
              "assay": "ONT PCR-cDNA barcoding, R9.4.1 flow cells, Guppy high-accuracy base calling",
              "split": "Two cohorts; the high-depth cohort is a subset of the low-depth samples",
              "source_locator": "Materials and Methods 'Samples', 'Library Preparation', 'Fusion Performance Evaluations'; Tables 1-2",
              "missing_metadata": {"version": {"reason": "unreported"}}})["id"]
HEADB = ["Algorithm", "Sensitivity (recall)", "Specificity", "Precision", "F1"]
for k, (tid, depth, cap) in enumerate([("tbl3", "high-depth", "High-Depth Fusion Caller Comparison"),
                                       ("tbl6", "low-depth", "Low-Depth Fusion Caller Comparison")]):
    tab = next(t for t in art.iter("table-wrap") if t.get("id") == tid)
    assert tx(tab.find("caption")) == cap
    rows = [[tx(c) for c in tr if c.tag in ("td", "th")] for tr in tab.iter("tr")]
    assert rows[0] == HEADB and [r[0] for r in rows[1:]] == list(B_CALLERS), rows
    pid = f"{P}-protocol-lin2026-{depth}"
    n = {"high-depth": "51 samples, 27 with a known B-ALL fusion", "low-depth": "119 sequencing runs, 79 with a known B-ALL fusion"}[depth]
    lims = ["One caller (FUSILLI) was developed by the authors; the others were run by them.",
            "Per-sample classification by the dominant B-ALL fusion only; secondary fusions are not scored.",
            "Truth is the clinical genomic subtype from cytogenetics, FISH and short-read RNA-seq (CICERO, FusionCatcher and manual review).",
            "Paediatric B-ALL only; PAX5::ZCCHC7 excluded from scoring.",
            "Caller versions are not printed."]
    rec(pid, "protocol", f"Paediatric B-ALL nanopore WTS, {depth} cohort, dominant-fusion classification (Lin et al. 2026 Table {tid[-1]})",
        f"Per-sample sensitivity, specificity, precision and F1 of four long-read fusion callers, {depth} cohort.", [B_ART],
        [{"relation": "uses_data", "target_id": B_DATA}],
        {"protocol": ("The dominant detected B-ALL fusion (most supporting reads) is compared with the sample's known fusion subtype. TP: concordant; "
                      "TN: no fusion and none detected; FN: known fusion and none detected; FP: a B-ALL fusion detected that does not match or in a fusion-negative sample."),
         "version": f"Table {tid[-1]}", "metric": "recall", "limitations": lims,
         "source_locator": f"Table {tid[-1]}; Materials and Methods 'Fusion Performance Evaluations'"})
    for r in rows[1:]:
        alg = r[0]
        eid = f"{P}-eval-lin2026-{alg.lower()}-{depth}"
        evaluation(eid, f"{alg} on paediatric B-ALL nanopore WTS, {depth} (Lin et al. 2026)", B_CONF[alg], pid, B_DATA, [B_ART],
                   "author_reported" if alg == "FUSILLI" else "independent_paper",
                   {"dataset_version": None, "split": depth, "population": n, "inputs": "Nanopore PCR-cDNA reads",
                    "adaptation": None, "metric_implementation": "Dominant-fusion per-sample classification (Methods)",
                    "aggregation": "Per sample or sequencing run", "budget": None},
                   f"Table {tid[-1]}, row '{alg}'", missing={"comparison.dataset_version": {"reason": "unreported"}})
        for v, (m, col) in zip(r[1:], [("tpr", "Sensitivity (recall)"), ("spec", "Specificity"), ("ppv", "Precision"), ("f1", "F1")]):
            result(f"{P}-result-lin2026-{alg.lower()}-{depth}-{METRIC[m]['metric']}", eid, [B_ART], B_SHA, B_URL,
                   f"Table {tid[-1]}, row '{alg}', column '{col}'", v, m, f"per-sample dominant B-ALL fusion, {depth} cohort", B_HOW)
    judgement(f"lin2026-{depth}", pid, f"Paediatric B-ALL long-read fusion calling, {depth} (Lin et al. 2026)", [B_ART], "direct",
              f"Per-sample sensitivity, specificity, precision and F1 for FusionSeeker, JAFFAL, LongGF and FUSILLI on nanopore WTS, {depth} cohort",
              ("Real patient leukaemia samples with clinically established fusion subtypes directly measure long-read fusion callers' sensitivity and "
               "false calls; three comparators were run by the authors of the fourth."),
              CONSTRAINTS, lims, [(B_ART, f"Table {tid[-1]}; Materials and Methods 'Fusion Performance Evaluations'")],
              "lin2026-longread", "Long-read fusion callers in paediatric B-ALL (Lin et al. 2026)", "recall",
              stratum={"high-depth": "High depth (11.2 M reads)", "low-depth": "Low depth (1.4 M reads)"}[depth], order=k + 1)

rec(f"{P}-claim-lin2026-runtime", "claim", "computational_cost: long-read fusion callers (Lin et al. 2026)",
    "Descriptive fact transcribed from the pinned source.", [B_ART], [{"relation": "subject", "target_id": f"{P}-protocol-lin2026-high-depth"}],
    {"field": "computational_cost",
     "value": ("Table 5 (high-depth cohort, averages): FusionSeeker 50 min 26 s real time and 30.01 GB RAM; JAFFAL 96 min 7 s and 45.31 GB, including its own alignment; "
               "LongGF 10 min 22 s and 8.88 GB; FUSILLI 1 min 45 s and 2.13 GB; minimap2 alignment, needed by all but JAFFAL, 157 min 55 s and 31.75 GB."),
     "source_locator": "Table 5 and footnote", "review": review_note("Hand transcription from Table 5 of the article XML.")}, facets={})
claims_rows.append([f"{P}-claim-lin2026-runtime", B_ART, "Table 5 and footnote", "50 Minutes 26 seconds; 96 Minutes 7 seconds; 10 Minutes 22 seconds; 1 Minute 45 seconds; 157 Minutes 55 seconds", "claim"])
t5 = next(t for t in art.iter("table-wrap") if t.get("id") == "tbl5")
assert "1 Minute 45 seconds" in tx(t5) and "45.31" in tx(t5) and "157 Minutes 55 seconds" in tx(t5)

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
