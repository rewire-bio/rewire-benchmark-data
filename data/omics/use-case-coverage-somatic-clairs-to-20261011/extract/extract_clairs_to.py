"""Chen et al. 2025 (ClairS-TO, Nature Communications, doi:10.1038/s41467-025-64547-z): every cell of Supplementary Tables 2a, 2b, 7a and 7b.

Usage: python3 -I extract_clairs_to.py <article.xml> <supplementary-information.pdf> <source-data.xlsx> <batch-folder>
printed_value comes from the text layer of the Supplementary Information PDF (pdftotext -layout); each
row is matched in order to the authors' Source Data sheet of the same table, and every number is asserted
equal to the Source Data value at the printed precision. Row labels come from the Source Data sheet.
"""
import sys, os, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, num, SOMATIC_UC
import xlsx

xml, pdf, sd, folder = sys.argv[1:5]
XML_SHA, PDF_SHA, SD_SHA = sha256(xml), sha256(pdf), sha256(sd)
assert XML_SHA == "6b5e5262df96467010d539e919c7a52aac3e49c616b3eeb403d1865dcb173b8a", XML_SHA
assert PDF_SHA == "806cd47423031495bf00543d7e3e3abad3f93fc4ee3ee2a7a570c335227f5603", PDF_SHA
assert SD_SHA == "4347c74fe0ce2ed04b1ac40d28bd4f8885c77f628e911a7027a275b1234828f8", SD_SHA
text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
ROW = re.compile(r"\b(SNV|Indel)\s+(\d\.\d+)\s+(\d\.\d+)\s+(\d\.\d+)\s+(\d\.\d+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$")

def section(start, end):
    s = text.index(start); e = text.index(end, s)
    return [m.groups() for m in (ROW.search(l) for l in text[s:e].splitlines()) if m]

pdf_rows = {"2": section("Supplementary Table 2. Performance on ONT COLO829 and HCC1395", "Supplementary Table 3. Performance"),
            "7": section("Supplementary Table 7. Performance on PacBio and Illumina", "Supplementary Table 8. Indel")}
assert len(pdf_rows["2"]) == 42 and len(pdf_rows["7"]) == 20, {k: len(v) for k, v in pdf_rows.items()}
sheets = xlsx.sheets(sd)

def sd_rows(name):
    out, ds, caller, cov = [], None, None, None
    rows = xlsx.rows(sheets[name])
    hdr = rows[3]
    assert hdr[1:12] == ["Dataset", "Caller", "Tumor \ncoverage", "Type", "AUPRC", "Precision", "Recall", "F1-score", "TP", "FP", "FN"], hdr
    for r in rows[4:]:
        if len(r) < 12 or not r[5]:
            continue
        ds = r[1] or ds; caller = (r[2] or caller); cov = r[3] or cov
        out.append((ds, caller.replace("\n", " "), cov, r[4], r[5:12]))
    return out

sd = {"2": sd_rows("Supplementary Table 2"), "7a": sd_rows("Supplementary Table 7a"), "7b": sd_rows("Supplementary Table 7b")}
assert len(sd["2"]) == 42 and len(sd["7a"]) == 8 and len(sd["7b"]) == 12
pairs = [("2a" if i < 24 else "2b", p, s) for i, (p, s) in enumerate(zip(pdf_rows["2"], sd["2"]))] + \
        [("7a" if i < 8 else "7b", p, s) for i, (p, s) in enumerate(zip(pdf_rows["7"], sd["7a"] + sd["7b"]))]
COLS = ["AUPRC", "Precision", "Recall", "F1-score", "TP", "FP", "FN"]
for t, p, (ds, caller, cov, typ, vals) in pairs:
    assert p[0] == typ, (t, p, typ)
    for printed, v in zip(p[1:], vals):
        a = float(num(printed)); bval = float(v)
        dp = len(printed.split(".")[1]) if "." in printed else 0
        assert abs(a - bval) <= 0.5 * 10 ** -dp + 1e-12, (t, caller, cov, typ, printed, v)
assert [s[1] for t, p, s in pairs if t == "2a"][::6] == ["ClairS-TO SS", "ClairS-TO SSRS", "Clair3", "DeepSomatic"]
assert sorted({s[0] for t, p, s in pairs if t == "2b"}) == ["HCC1395"] and sorted({s[1] for t, p, s in pairs if t == "2b"}) == ["Clair3", "ClairS-TO SS", "ClairS-TO SSRS"]
assert [s[1] for t, p, s in pairs if t == "7b"][::2] == ["ClairS-TO SS", "ClairS-TO SSRS", "DeepSomatic", "Mutect2", "Octopus", "Pisces"]

XURL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12579226/fullTextXML"
PURL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-64547-z/MediaObjects/41467_2025_64547_MOESM1_ESM.pdf"
SURL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-64547-z/MediaObjects/41467_2025_64547_MOESM6_ESM.xlsx"
b = Batch(folder, "somatic-clairs-to-20261011", ["dna-genomes"])
DESC = "Primary source retrieved and hashed for the 2026-10-11 oncology use-case literature pass."
COMMON = {"doi": "10.1038/s41467-025-64547-z", "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0"}
ART = b.source("somatic-clairs-to-20261011-source-chen2025", "ClairS-TO: a deep-learning method for long-read tumor-only somatic small variant calling",
    {"url": "https://doi.org/10.1038/s41467-025-64547-z", "artifact_url": XURL, "version": "Nature Communications, published 2025-10-31; PMC12579226 full-text XML",
     "retrieved_at": "2026-10-11T21:37:39Z", "artifact_sha256": XML_SHA, "media_type": "application/xml", **COMMON}, DESC)
SUP = b.source("somatic-clairs-to-20261011-source-chen2025-supplementary", "ClairS-TO Supplementary Information (Supplementary Tables 1-8 and command lines)",
    {"url": "https://doi.org/10.1038/s41467-025-64547-z", "artifact_url": PURL, "version": "Supplementary Information PDF (41467_2025_64547_MOESM1_ESM.pdf) of the published article",
     "retrieved_at": "2026-10-11T21:37:53Z", "artifact_sha256": PDF_SHA, "media_type": "application/pdf", **COMMON}, DESC)
SDS = b.source("somatic-clairs-to-20261011-source-chen2025-source-data", "ClairS-TO Source Data workbook",
    {"url": "https://doi.org/10.1038/s41467-025-64547-z", "artifact_url": SURL, "version": "Source Data file (41467_2025_64547_MOESM6_ESM.xlsx) of the published article",
     "retrieved_at": "2026-10-11T21:38:10Z", "artifact_sha256": SD_SHA, "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", **COMMON},
    "Authors' Source Data workbook, used only to confirm the identity of each printed table row; retrieved and hashed for the 2026-10-11 oncology use-case literature pass.")
SIDS = [ART, SUP, SDS]

def REVIEW(loc):
    return extraction_review(["pdf-text-parse"], "Parsed the text layer of the pinned Supplementary Information PDF (pdftotext -layout, version 26.08.0) with extract/extract_clairs_to.py; each printed row was matched in order to the authors' Source Data sheet for the same table, whose row labels give the caller, coverage and type, and every printed number was asserted equal to the Source Data value at the printed precision. " + loc,
                             PDF_SHA, PURL)

TRUTH = {"COLO829": "NYGC COLO829 somatic truth (42,993 SNVs, 985 indels before filtering)",
         "HCC1395": "SEQC2 HCC1395 HighConf and MedConf calls in high-confidence regions (39,447 SNVs, 1,602 indels before filtering)"}
DATA = {}
for key, name, desc, assay in [
        ("ont-colo829", "COLO829 tumour ONT R10.4.1 WGS (ClairS-TO benchmark)", "COLO829 metastatic melanoma cell line, tumour reads only, Oxford Nanopore R10.4.1, 101.8x, subsampled to 75x, 50x and 25x.", "ONT R10.4.1 WGS (EPI2ME Labs), minimap2 to GRCh38"),
        ("ont-hcc1395", "HCC1395 tumour ONT R10.4.1 WGS (ClairS-TO benchmark)", "HCC1395 breast cancer cell line, tumour reads only, Oxford Nanopore R10.4.1, 79.5x, subsampled to 75x, 50x and 25x.", "ONT R10.4.1 WGS (UCSC and Google), minimap2 to GRCh38"),
        ("pacbio-colo829", "COLO829 tumour PacBio HiFi Revio WGS (ClairS-TO benchmark)", "COLO829 tumour reads only, PacBio HiFi Revio, 60.7x, used at 50x.", "PacBio HiFi Revio WGS, pbmm2 to GRCh38"),
        ("illumina-colo829", "COLO829 tumour Illumina NovaSeq 6000 WGS (ClairS-TO benchmark)", "COLO829 tumour reads only, Illumina NovaSeq 6000, 234.4x, used at 50x.", "Illumina NovaSeq 6000 WGS (dbGaP), BWA-MEM to GRCh38")]:
    cell = key.split("-")[1].upper()
    DATA[key] = b.entity("dataset", b.rid("data", key), name, desc, SIDS,
        {"population": "One cancer cell line, tumour sample only (no matched normal used by the callers)", "assay": assay,
         "split": "Held out from ClairS-TO training (SS: synthetic HG001/HG002 or HG003/HG004; SSRS: plus HCC1937, HCC1954, H1437 and H2009)",
         "scope_note": "Truth: " + TRUTH[cell] + "; a truth variant is kept only if coverage is at least 4, at least 3 reads support the alternative allele and VAF is at least 0.05",
         "source_locator": "Results 'Benchmarking datasets and evaluation' paragraph 1; Supplementary Table 1a",
         "missing_metadata": {"version": {"reason": "unreported", "note": "Data releases are named by provider only"}}})

LIM_ALL = ["Developer paper: the authors developed ClairS-TO and its SS and SSRS models (author_reported); Clair3, also run here, comes from the same group. Comparators were run by the authors with their recommended settings.",
           "Tumour-only calling of cell lines; the truth sets were derived from tumour-normal data and are filtered to variants with coverage at least 4, at least 3 alternative reads and VAF at least 0.05, so very low-VAF variants are not scored.",
           "Precision, recall and F1 are at the best achievable F1 over the caller's quality threshold, chosen on the test data (Figure 2 legend); AUPRC summarises the whole curve. Neither is an operating point fixed in advance.",
           "Clair3 is a germline caller; its calls were treated as somatic after removing those tagged by ClairS-TO's panels of normals.",
           "Single sample per dataset; no interval estimates.",
           "Comparator versions are old relative to the paper (DeepSomatic 1.7.0 run from the 'latest' container; Mutect2 4.2.6.1; Octopus 0.7.4; Pisces 5.3.0)."]
LIM_ALL = LIM_ALL + ["Competing interests: the senior author (R.L.) receives research funding from ONT."]
DENOM = {("ont-colo829", "SNV"): 37533, ("ont-colo829", "Indel"): 585, ("ont-hcc1395", "SNV"): 32212, ("ont-hcc1395", "Indel"): 1356,
         ("pacbio-colo829", "SNV"): 39086, ("pacbio-colo829", "Indel"): 610}
PROTOS = {}
SPEC = [("ont-colo829", "2a", "ONT COLO829 tumour-only, 25x to 75x", "Supplementary Table 2a"),
        ("ont-hcc1395", "2b", "ONT HCC1395 tumour-only, 25x to 75x", "Supplementary Table 2b"),
        ("pacbio-colo829", "7a", "PacBio HiFi COLO829 tumour-only, 50x", "Supplementary Table 7a"),
        ("illumina-colo829", "7b", "Illumina COLO829 tumour-only, 50x", "Supplementary Table 7b")]
for key, t, label, loc in SPEC:
    for typ in ("SNV", "Indel"):
        extra = []
        if key == "ont-hcc1395":
            extra.append("DeepSomatic is not scored on HCC1395 because HCC1395 was in its training data (Results).")
        if key == "illumina-colo829":
            extra.append("Short-read comparators (DeepSomatic WGS_TUMOR_ONLY, Mutect2 with gnomAD germline resource, Octopus, Pisces) were run in tumour-only mode; the panel-of-normals and filtering choices for each are in the Supplementary Information command lines.")
            extra.append("TP + FN is not identical across callers (SNV 40,232, but 40,230 for Pisces; indel 715, but 714 for Mutect2 and 713 for Octopus), so the scored truth set differs slightly between rows; the source does not explain this.")
        if "colo829" in key:
            extra.append("Whether the DeepSomatic 1.7.0 models were trained with COLO829 data is not stated in the source.")
        if (key, typ) in DENOM:
            extra.append("The denominator is TP + FN after the authors' truth filter; it is the same for every caller in this table.")
        PROTOS[(key, typ)] = b.entity("protocol", b.rid("protocol", key, typ), f"{label}, somatic {'SNVs' if typ == 'SNV' else 'indels'} (Chen et al. 2025 {loc})",
            f"Tumour-only somatic {'SNV' if typ == 'SNV' else 'indel'} calling scored by AUPRC and by precision, recall and F1 at the best-F1 threshold, with TP, FP and FN counts.", SIDS,
            {"protocol": "Each caller is run on the tumour BAM alone; calls are compared with the filtered cell-line truth set using som.py (hap.py 0.3.12) and ClairS-TO compare_vcf, which the authors cross-checked. Precision, recall and F1 are reported at the quality threshold giving the best F1.",
             "version": f"{loc}, Type '{typ}'", "metric": "f1-score", "limitations": LIM_ALL + extra,
             **({"denominator": DENOM[(key, typ)]} if (key, typ) in DENOM else {}),
             "source_locator": f"{loc}; Results 'Benchmarking datasets and evaluation'; Methods 'Benchmarking'; Supplementary Information 'Command lines used'"},
            links=[{"relation": "uses_data", "target_id": DATA[key]}])

METHOD_CLAIRS_TO = b.entity("method", b.rid("method", "clairs-to"), "ClairS-TO", "Deep-learning tumour-only somatic small-variant caller that combines an affirmative and a negational neural network, with panels of normals and hard filters.", [ART],
    {"reported_name": "ClairS-TO", "entity_level": "method", "source_locator": "Results 'Overview of ClairS-TO'; Methods",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}, method_types=["supervised_machine_learning"])
METHOD_CLAIR3 = b.entity("method", b.rid("method", "clair3"), "Clair3", "Deep-learning germline small-variant caller.", [ART],
    {"reported_name": "Clair3", "entity_level": "method", "source_locator": "Results 'Benchmarking datasets and evaluation'",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}, method_types=["supervised_machine_learning"])
METHOD_PISCES = b.entity("method", b.rid("method", "pisces"), "Pisces", "Illumina somatic and germline small-variant caller for short reads.", [ART],
    {"reported_name": "Pisces", "entity_level": "method", "source_locator": "Results 'Performance on short-read data'; reference 14",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}, method_types=["conventional_pipeline"])
FAM = {"ClairS-TO SS": METHOD_CLAIRS_TO, "ClairS-TO SSRS": METHOD_CLAIRS_TO, "Clair3": METHOD_CLAIR3, "DeepSomatic": "somatic-20261009-method-deepsomatic",
       "Mutect2": "somatic-20261009-method-mutect2", "Octopus": "somatic-neusomatic-20261010-method-octopus", "Pisces": METHOD_PISCES}
VER = {"ClairS-TO SS": "v0.4.0", "ClairS-TO SSRS": "v0.4.0", "Clair3": "v1.0.8", "DeepSomatic": "v1.7.0", "Mutect2": "GATK v4.2.6.1", "Octopus": "v0.7.4", "Pisces": "v5.3.0"}
PARAMS = {
    "ClairS-TO SS": "Model trained on synthetic tumours only (GIAB HG001/HG002 for ONT; HG003/HG004 for PacBio and Illumina); default panels of normals (gnomAD r2.1, dbSNP v138, 1000 Genomes PoN, CoLoRSdb) and hard filters; short-read runs omit long-read-specific filters",
    "ClairS-TO SSRS": "SS model fine-tuned on four real cancer cell lines (HCC1937, HCC1954, H1437, H2009); default panels of normals and hard filters; short-read runs omit long-read-specific filters",
    "Clair3": "Germline caller run on the tumour BAM (ONT model r1041_e82_400bps_sup_v420); calls tagged by ClairS-TO's panels of normals removed, the rest treated as somatic",
    "DeepSomatic": "Tumour-only model for the platform (ONT_TUMOR_ONLY, PACBIO_TUMOR_ONLY or WGS_TUMOR_ONLY) with default PoN filtering; Docker image tag 'latest', reported as v1.7.0",
    "Mutect2": "Tumour-only mode with the af-only gnomAD germline resource, then FilterMutectCalls",
    "Octopus": "Tumour-only run with the authors' recommended settings (Supplementary Information command lines)",
    "Pisces": "Tumour-only run with the authors' recommended settings (Supplementary Information command lines)"}
CFG = {}
def config(caller, platform):
    k = (caller, platform)
    if k not in CFG:
        mt = ["conventional_pipeline"] if caller in ("Mutect2", "Octopus", "Pisces") else ["supervised_machine_learning"]
        CFG[k] = b.entity("configuration", b.rid("config", caller, platform), f"{caller} {VER[caller]}, tumour-only, {platform} (Chen et al. 2025)",
            f"{caller} as run on {platform} tumour-only data in the cited comparison.", SIDS,
            {"reported_name": caller, "version": VER[caller], "foundation_model_eligible": False, "parameters": PARAMS[caller],
             "access_reuse": "Public open-source software and released models" if caller not in ("Pisces",) else "Public software (Illumina)",
             "source_locator": "Supplementary Information 'Command lines used'; Supplementary Tables 2 and 7 row labels"},
            method_types=mt, links=[{"relation": "configuration_of", "target_id": FAM[caller]}])
    return CFG[k]

PLATFORM = {"2a": "ONT", "2b": "ONT", "7a": "PacBio HiFi", "7b": "Illumina"}
KEY = {"2a": "ont-colo829", "2b": "ont-hcc1395", "7a": "pacbio-colo829", "7b": "illumina-colo829"}
LOC = {"2a": "Supplementary Table 2a", "2b": "Supplementary Table 2b", "7a": "Supplementary Table 7a", "7b": "Supplementary Table 7b"}
METRICS = [("AUPRC", "auprc", "higher", "fraction", None), ("Precision", "precision", "higher", "fraction", None), ("Recall", "recall", "higher", "fraction", None),
           ("F1-score", "f1-score", "higher", "fraction", None),
           ("TP", "true-positive-count", "higher", "count", "counted entity: truth variants called"),
           ("FP", "false-positive-count", "lower", "count", "counted entity: calls not in the truth set"),
           ("FN", "false-negative-count", "lower", "count", "counted entity: truth variants not called")]
EVALS = {}
for t, p, (ds, caller, cov, typ, vals) in pairs:
    key = KEY[t]; proto = PROTOS[(key, typ)]
    cfg = config(caller, PLATFORM[t])
    eid = b.rid("eval", caller, key, typ)
    if eid not in b.ids:
        origin = "author_reported" if caller.startswith("ClairS-TO") or caller == "Clair3" else "independent_paper"
        b.evaluation(eid, f"{caller} on {key} tumour-only {typ} (Chen et al. 2025)", SIDS, cfg, proto, DATA[key], origin,
            {"protocol_id": proto, "dataset_version": None, "split": "Held-out cell line", "population": f"{ds} tumour sample",
             "inputs": f"{PLATFORM[t]} tumour reads only", "adaptation": None,
             "metric_implementation": "som.py (hap.py 0.3.12) and ClairS-TO compare_vcf; precision, recall and F1 at the best-F1 quality threshold",
             "aggregation": "Single sample per coverage level", "budget": None},
            f"{LOC[t]}, rows '{caller}'", missing={"comparison.adaptation": {"reason": "inapplicable", "note": "Pre-trained models used without retraining on the test cell line"}})
        EVALS.setdefault((key, typ), []).append(eid)
    for (col, metric, d, unit, ud), printed in zip(METRICS, p[1:]):
        locator = f"{LOC[t]}, Dataset '{ds}', Caller '{caller}', Tumor coverage '{cov}', Type '{typ}', column '{col}'"
        qual = f"{'SNV' if typ == 'SNV' else 'indel'} only, tumour-only, {cov} tumour coverage" + (", at the best-F1 threshold" if col in ("Precision", "Recall", "F1-score", "TP", "FP", "FN") else "")
        b.result(b.rid("result", caller, key, typ, cov, metric), f"{caller} {key} {typ} {cov} {metric}", SUP, SIDS, eid, printed, metric, d, unit, locator,
                 REVIEW(locator), qualifier=qual, unit_detail=ud)

UCN = "Select a tumour DNA somatic variant-calling workflow"
STRATA = {("ont-colo829", "SNV"): ("ONT COLO829, SNVs", 1), ("ont-colo829", "Indel"): ("ONT COLO829, indels", 2),
          ("ont-hcc1395", "SNV"): ("ONT HCC1395, SNVs", 3), ("ont-hcc1395", "Indel"): ("ONT HCC1395, indels", 4),
          ("pacbio-colo829", "SNV"): ("PacBio COLO829, SNVs", 5), ("pacbio-colo829", "Indel"): ("PacBio COLO829, indels", 6),
          ("illumina-colo829", "SNV"): ("Illumina COLO829, SNVs", 7), ("illumina-colo829", "Indel"): ("Illumina COLO829, indels", 8)}
JUDGE = {}
for (key, typ), proto in PROTOS.items():
    lims = next(r for r in b.records if r["id"] == proto)["attributes"]["limitations"]
    stratum, order = STRATA[(key, typ)]
    JUDGE[(key, typ)] = b.judgement(SOMATIC_UC, UCN, proto, f"{stratum} tumour-only calling (Chen et al. 2025)", SIDS, "proxy",
        f"AUPRC, and precision, recall, F1, TP, FP and FN at the best-F1 threshold, for tumour-only somatic {'SNV' if typ == 'SNV' else 'indel'} calling by the callers in {LOC[[k for k, v in KEY.items() if v == key][0]]}",
        "Proxy, not direct: the endpoint matches (per-caller precision, recall and F1 on held-out cell lines with consortium truth sets), but the callers used tumour reads only, whereas this use case's inputs include a matched normal and its exclusions list tumour-only calling. Linked as the closest evidence for users without a matched normal.",
        lims, [{"source_id": SUP, "locator": f"{LOC[[k for k, v in KEY.items() if v == key][0]]}; 'Command lines used'"},
               {"source_id": ART, "locator": "Results 'Benchmarking datasets and evaluation', 'Performance on short-read data'; Methods 'Benchmarking'; Figure 2 legend"}],
        "chen2025-clairs-to", "Tumour-only callers on cell lines (Chen et al. 2025, ClairS-TO developers)", stratum, order, "f1-score")
print(XML_SHA, PDF_SHA, SD_SHA, b.write())
if len(sys.argv) > 5:
    import json
    json.dump({"evaluations": {f"{k[0]}|{k[1]}": v for k, v in EVALS.items()}, "judgements": {f"{k[0]}|{k[1]}": v for k, v in JUDGE.items()}}, open(sys.argv[5], "w"), indent=1)
