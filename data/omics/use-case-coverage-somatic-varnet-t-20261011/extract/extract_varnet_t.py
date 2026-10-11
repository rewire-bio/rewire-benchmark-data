"""Krishnamachari et al. 2026 (VarNet-T, Nature Communications, doi:10.1038/s41467-026-71705-4): tumour-only
AUPRC tables, Supplementary Tables 1, 2 and 4.

Usage: python3 -I extract_varnet_t.py <article.xml> <supplementary-information.pdf> <source-data.xlsx> <batch-folder>
Supplementary Tables 1, 2 and 4 are read from the PDF text layer (physical pages 18, 19 and 21) and
checked cell by cell against the authors' Source Data sheets of the same names; the values printed in
Results are checked against Table 1.
"""
import sys, os, re, html, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, num, SOMATIC_UC
import xlsx

xml, pdf, sd, folder = sys.argv[1:5]
XML_SHA, PDF_SHA, SD_SHA = sha256(xml), sha256(pdf), sha256(sd)
assert XML_SHA == "b42db521781cd548b5ce0cf99233f8e790781fb5e8953fe733202009dd8367bb", XML_SHA
assert PDF_SHA == "c808b4361e17a64911a59ded81d9db04c7a3dd5ba95fb3e1e060a293182f2842", PDF_SHA
assert SD_SHA == "4a2deae733ff93a9ae0001053816d82fb60787b01646183c8d37fbc5a764cd17", SD_SHA
sheets = xlsx.sheets(sd)
clean = lambda s: s.replace("\xa0", " ").strip()
def short(v):
    """Source Data double at the three decimals every printed AUPRC in the paper uses (Supplementary Table 2 prints, for example, 0.750)."""
    return f"{float(v):.3f}"

T1 = [[clean(c) for c in r] for r in xlsx.rows(sheets["Supplementary Table 1"]) if any(r)]
assert T1[0][1:] == ["SEQC2", "", "COLO829"][:len(T1[0]) - 1] or T1[0][1] == "SEQC2", T1[0]
assert T1[1] == ["Method", "SNV", "INDEL", "SNV", "INDEL"], T1[1]
T1 = T1[2:]
M1 = ["VarNet-T", "DeepSom-BLCA", "DeepSom-LINC", "DeepSom-ESAD", "DeepSom-LAML", "DeepSom-GACA", "Deepsomatic (tumor-only)", "Mutect2 (tumor-only)", "ClairS-TO"]
assert [r[0] for r in T1] == M1, [r[0] for r in T1]
T4 = [[clean(c) for c in r] for r in xlsx.rows(sheets["Supplementary Table 4"]) if any(r)]
assert T4[0] == ["Method/Sample", "AML", "MBL", "CLL"], T4[0]
T4 = T4[1:]
assert [r[0] for r in T4] == M1
T2 = [[clean(c) for c in r] for r in xlsx.rows(sheets["Supplementary Table 2"]) if any(r)]
SAMPLES = ["DO15046", "DO14566", "DO38547", "DO38423", "DO6144", "DO1663", "DO804", "DO522", "DO41398", "DO41056"]
CANCER = {"DO15046": "head and neck", "DO14566": "head and neck", "DO38547": "stomach", "DO38423": "stomach", "DO6144": "breast", "DO1663": "breast",
          "DO804": "bladder", "DO522": "bladder", "DO41398": "uterine", "DO41056": "uterine"}
assert T2[1] == ["Method/Sample ID"] + SAMPLES
T2 = T2[2:]
M2 = ["VarNet-T", "Deepsomatic (tumor-only)", "Mutect2 (tumor-only)", "ClairS-TO (tumor-only)", "DeepSom-BLCA", "DeepSom-LINC", "DeepSom-ESAD", "DeepSom-LAML", "DeepSom-GACA"]
assert [r[0] for r in T2] == M2
# Supplementary Table 2 printed values from the PDF text layer
text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
s = text.index("Method/Sample ID    DO15046"); e = text.index("Supplementary Table 2: Area under", s)
nums = [re.findall(r"\b\d\.\d{3}\b", l) for l in text[s:e].splitlines()]
nums = [n for n in nums if len(n) == 10]
assert len(nums) == 9, len(nums)
PRINTED2 = {}
for m, row, pr in zip(M2, T2, nums):
    for smp, v, p in zip(SAMPLES, row[1:], pr):
        assert abs(float(v) - float(p)) < 5e-4, (m, smp, v, p)
        PRINTED2[(m, smp)] = p
def page(n):
    return subprocess.run(["pdftotext", "-f", str(n), "-l", str(n), "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
def page_rows(n, labels, ncol):
    out = {}
    for line in page(n).splitlines():
        for m in labels:
            if line.strip().startswith(m + " ") and re.fullmatch(r"\s*" + re.escape(m) + r"(\s+\d\.\d{3}){%d}\s*" % ncol, line):
                out[m] = re.findall(r"\d\.\d{3}", line)
    assert sorted(out) == sorted(labels), (n, sorted(out))
    return out
P1, P4 = page_rows(18, M1, 4), page_rows(21, M1, 3)
for rows_, pr in ((T1, P1), (T4, P4)):
    for r in rows_:
        for v, p in zip(r[1:], pr[r[0]]):
            assert abs(float(v) - float(p)) < 5e-4, (r[0], v, p)
body = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", open(xml, encoding="utf-8").read())))
for quote, cell in (("VarNet-T achieved AUPRC of 0.773 on SEQC2, compared to the second highest achieved by DeepSom-ESAD (0.577)", [("VarNet-T", 1, "0.773"), ("DeepSom-ESAD", 1, "0.577")]),
                    ("On COLO829, VarNet-T again achieved the best performing AUPRC of 0.656", [("VarNet-T", 3, "0.656")])):
    assert quote in body
    for m, col, v in cell:
        assert short(next(r for r in T1 if r[0] == m)[col]) == v

XURL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13243554/fullTextXML"
PURL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-026-71705-4/MediaObjects/41467_2026_71705_MOESM1_ESM.pdf"
SURL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-026-71705-4/MediaObjects/41467_2026_71705_MOESM6_ESM.xlsx"
b = Batch(folder, "somatic-varnet-t-20261011", ["dna-genomes"])
DESC = "Primary source retrieved and hashed for the 2026-10-11 oncology use-case literature pass."
COMMON = {"doi": "10.1038/s41467-026-71705-4", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0"}
ART = b.source("somatic-varnet-t-20261011-source-krishnamachari2026", "Improved tumor-only variant calling and mutation burden estimation with VarNet-T",
    {"url": "https://doi.org/10.1038/s41467-026-71705-4", "artifact_url": XURL, "version": "Nature Communications, published 2026-04-09; PMC13243554 full-text XML",
     "retrieved_at": "2026-10-11T21:37:39Z", "artifact_sha256": XML_SHA, "media_type": "application/xml", **COMMON}, DESC)
SUP = b.source("somatic-varnet-t-20261011-source-krishnamachari2026-supplementary", "VarNet-T Supplementary Information",
    {"url": "https://doi.org/10.1038/s41467-026-71705-4", "artifact_url": PURL, "version": "Supplementary Information PDF (41467_2026_71705_MOESM1_ESM.pdf), 28 pages",
     "retrieved_at": "2026-10-11T21:51:40Z", "artifact_sha256": PDF_SHA, "media_type": "application/pdf", **COMMON}, DESC)
SDS = b.source("somatic-varnet-t-20261011-source-krishnamachari2026-source-data", "VarNet-T Source Data workbook",
    {"url": "https://doi.org/10.1038/s41467-026-71705-4", "artifact_url": SURL, "version": "Source Data file (41467_2026_71705_MOESM6_ESM.xlsx)",
     "retrieved_at": "2026-10-11T21:51:40Z", "artifact_sha256": SD_SHA, "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", **COMMON}, DESC)
SIDS = [ART, SUP, SDS]
def REV_PDF(loc):
    return extraction_review(["pdf-text-parse"], "Parsed the Supplementary Table 2 rows from the text layer of the pinned Supplementary Information PDF (pdftotext -layout, version 26.08.0) with extract/extract_varnet_t.py and checked every cell against the Source Data sheet 'Supplementary Table 2'. " + loc, PDF_SHA, PURL)
def REV_SD(loc):
    return extraction_review(["pdf-text-parse"], "Parsed from the text layer of the pinned Supplementary Information PDF (physical pages 18 and 21; pdftotext -layout, version 26.08.0) with extract/extract_varnet_t.py; method labels asserted, every cell cross-checked against the authors' Source Data sheet of the same name, and the Results values 0.773, 0.577 and 0.656 checked. " + loc, PDF_SHA, PURL)

VARNET_T = b.entity("method", b.rid("method", "varnet-t"), "VarNet-T", "Weakly supervised deep-learning tumour-only somatic SNV and indel caller (convolutional networks) trained on high-confidence calls from 356 tumour-normal WGS pairs.", [ART],
    {"reported_name": "VarNet-T", "entity_level": "method", "source_locator": "Results 'Overview of approach'; Methods 'Training data', 'Model architecture'",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}, method_types=["supervised_machine_learning"])
DEEPSOM = b.entity("method", b.rid("method", "deepsom"), "DeepSom", "CNN-based filter for tumour-only somatic SNV calls on WGS, applied to Mutect2 tumour-only candidates; distributed with cancer-type-specific models.", [ART],
    {"reported_name": "DeepSom", "entity_level": "method", "source_locator": "Methods 'Implementation of tumor-only variant callers'; reference 10",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record"}}}, method_types=["supervised_machine_learning"])
CFGSPEC = {
    "VarNet-T": (VARNET_T, None, "Authors' model trained on 356 tumour-normal WGS pairs (colorectal, lymphoma, sarcoma, gastric, lung, thyroid, liver); gnomAD v4.1 and dbSNP 156 COMMON pre-filtering", ["supervised_machine_learning"]),
    "Mutect2 (tumor-only)": ("somatic-20261009-method-mutect2", None, "Tumour-only mode with gnomAD v4.1 germline resource and the GATK 1000g hg38 panel of normals; scored by TLOD", ["conventional_pipeline"]),
    "Deepsomatic (tumor-only)": ("somatic-20261009-method-deepsomatic", "v1.7.0", "Tumour-only model from the provided Docker container; scored by QUAL", ["supervised_machine_learning"]),
    "ClairS-TO": ("somatic-clairs-to-20261011-method-clairs-to", "v0.4.0", "Illumina SSRS model from the provided Docker image; scored by QUAL", ["supervised_machine_learning"]),
}
for m in ("BLCA", "LINC", "ESAD", "LAML", "GACA"):
    CFGSPEC[f"DeepSom-{m}"] = (DEEPSOM, None, f"Pre-trained DeepSom model {dict(BLCA='BLCA-US (bladder)', LINC='LINC-JP (liver)', ESAD='ESAD-UK (oesophageal adenocarcinoma)', LAML='TCGA-LAML (acute myeloid leukaemia)', GACA='GACA-CN (gastric)')[m]} on Mutect2 tumour-only candidates, with gnomAD and panel of normals; scored by cnn_score", ["supervised_machine_learning"])
CFG = {}
for name, (fam, ver, params, mt) in CFGSPEC.items():
    attrs = {"reported_name": name, "foundation_model_eligible": False, "parameters": params, "access_reuse": "Public software and models",
             "source_locator": "Methods 'Implementation of tumor-only variant callers'; Supplementary Tables 1, 2 and 4 row labels"}
    if ver:
        attrs["version"] = ver
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported"}}
    CFG[name] = b.entity("configuration", b.rid("config", name), f"{name}{' ' + ver if ver else ''}, tumour-only Illumina WGS (Krishnamachari et al. 2026)", f"{name} as run in the cited tumour-only comparison.", SIDS, attrs,
                         method_types=mt, links=[{"relation": "configuration_of", "target_id": fam}])
CFG["ClairS-TO (tumor-only)"] = CFG["ClairS-TO"]

LIM = ["Developer paper: the authors developed VarNet-T (and earlier VarNet); its rows are author_reported. Comparators were run by the authors.",
       "Tumour-only calling: the matched normal was used only to build the truth sets, not by the callers.",
       "Only AUPRC is extracted; the threshold-optimised best F1 values are shown in figures only.",
       "No interval estimates."]
DATA, PROTO = {}, {}
SCOPE = {"colo829": "Truth: TGen multi-institution COLO829 reference set, about 35,000 SNVs (Results 'Benchmarking on somatic reference datasets', 'Challenges in tumor samples with low somatic mutation burden'). This is a different truth set and sequencing run from Chen et al. 2025 (NYGC truth, 42,993 SNVs before filtering).",
         "seqc2": "Truth: SEQC2 consortium reference call set in its high-confidence regions, about 39,000 SNVs."}
V5 = "DeepSom's developers describe it as a caller of somatic SNVs (github.com/sergeyvilov/DeepSom repository description, checked 2026-10-11; not a pinned source); this source prints indel AUPRC for its models without explanation."
V6 = "COLO829 truth is the TGen reference set and the reads are EGA EGAD00001002142; Chen et al. 2025 used the NYGC truth set and other COLO829 sequencing, so COLO829 values from the two papers are not comparable (ClairS-TO Illumina SSRS v0.4.0 SNV AUPRC 0.6500 there, 0.270 here)."
DSPEC = {
    "seqc2": ("SEQC2 HCC1395 tumour Illumina HiSeq WGS (WGS_IL_T_1), high-confidence regions", "SEQC2 HCC1395 tumour WGS used tumour-only; truth is the SEQC2 high-confidence call set (about 39,000 SNVs).", "SRA SRX4728512 and related (Data availability)"),
    "colo829": ("COLO829 tumour Illumina WGS (TGen reference set)", "COLO829 melanoma cell line tumour WGS used tumour-only; truth is the multi-institution TGen reference set (about 35,000 SNVs).", "EGA EGAD00001002142"),
    "pcawg": ("PCAWG primary tumour WGS, ten samples from five cancer types not used in VarNet-T training", "Ten PCAWG primary tumours (breast, bladder, stomach, head and neck, uterine; 10k to 100k SNVs; at most 100x) used tumour-only; truth is the PCAWG expert-reviewed consensus calls.", "PCAWG donors DO6144, DO1663, DO522, DO804, DO38547, DO38423, DO14566, DO15046, DO41398, DO41056"),
    "low-tmb": ("ICGC CLL and medulloblastoma and an AML tumour WGS, downsampled to about 100x", "Low-mutation-burden tumours (about 1,200 truth SNVs each) used tumour-only: ICGC CLL and MBL benchmark samples and an AML sample, downsampled from about 300x.", "EGA EGAD00001001858 (CLL), EGAD00001001859 (MBL); AML from reference 21"),
}
for k, (name, desc, acc) in DSPEC.items():
    DATA[k] = b.entity("dataset", b.rid("data", k), name, desc, SIDS,
        {"population": desc.split(" used tumour-only")[0], "assay": "Illumina WGS aligned with BWA-MEM (bcbio-nextgen) to GRCh38", "accession": acc,
         "split": "Samples not used in VarNet-T training. The source says the five cancer types were not in the training cohorts, but the training cohort includes 38 gastric tumours and two test samples (DO38547, DO38423) are stomach adenocarcinomas." if k == "pcawg" else "Not used in VarNet-T training",
         **({"scope_note": SCOPE[k]} if k in SCOPE else {}),
         "source_locator": "Results 'Benchmarking on somatic reference datasets', 'Benchmarking using whole cancer genomes from PCAWG', 'Challenges in tumor samples with low somatic mutation burden'; Methods 'Sample processing and in silico dilutions', 'PCAWG benchmark samples'; Data availability",
         "missing_metadata": {"version": {"reason": "unreported"}}})
PSPEC = [("seqc2-snv", "seqc2", "SEQC2 HCC1395 tumour-only, SNVs", "Supplementary Table 1, column SEQC2 SNV", ["DeepSomatic's models were trained on SEQC2 data (Introduction), so its SEQC2 row is not held out."]),
         ("seqc2-indel", "seqc2", "SEQC2 HCC1395 tumour-only, indels", "Supplementary Table 1, column SEQC2 INDEL", ["DeepSomatic's models were trained on SEQC2 data (Introduction), so its SEQC2 row is not held out.", V5]),
         ("colo829-snv", "colo829", "COLO829 tumour-only, SNVs", "Supplementary Table 1, column COLO829 SNV", [V6]),
         ("colo829-indel", "colo829", "COLO829 tumour-only, indels", "Supplementary Table 1, column COLO829 INDEL", [V5, V6]),
         ("pcawg-snv", "pcawg", "PCAWG ten primary tumours, tumour-only SNVs", "Supplementary Table 2", ["Truth is PCAWG consensus calls, themselves produced by tumour-normal callers.", "Samples chosen with 10k to 100k SNVs; lower-burden tumours are covered only by the low-TMB protocol.",
                    "The source says the PCAWG cancer types were not used in training (Results; Methods 'PCAWG benchmark samples'), but its training cohort includes 38 gastric tumours (Methods 'Training data'); VarNet-T is not held out at cancer-type level for the two stomach samples DO38547 and DO38423.",
                    "DeepSom's BLCA-US and GACA-CN models were trained on ICGC projects of the same cancer types as the bladder (DO804, DO522) and stomach (DO38547, DO38423) test samples; the source does not say whether those donors were in DeepSom's training data."]),
         ("low-tmb-snv", "low-tmb", "Low-mutation-burden tumours (AML, MBL, CLL), tumour-only SNVs", "Supplementary Table 4", ["About 1,200 truth SNVs per sample; the same CLL, MBL and AML samples underlie the Wang et al. 2020 tumour-normal protocols already linked, but here they are downsampled and called tumour-only.",
                    "DeepSom-LAML was trained on TCGA acute myeloid leukaemia data (Methods; Discussion); whether this AML sample is in its training data is not stated."])]
for pk, dk, label, loc, extra in PSPEC:
    PROTO[pk] = b.entity("protocol", b.rid("protocol", pk), f"{label}, AUPRC (Krishnamachari et al. 2026 {loc.split(',')[0]})",
        f"Area under the precision-recall curve for tumour-only calling: {label}.", SIDS,
        {"protocol": "Tumour BAM only; each caller's score (VarNet-T score, Mutect2 TLOD, DeepSomatic QUAL, DeepSom cnn_score, ClairS-TO QUAL) is varied to trace a precision-recall curve against the truth set; AUPRC reported.",
         "version": loc, "metric": "auprc", "limitations": LIM + extra,
         "source_locator": f"{loc}; Methods 'Implementation of tumor-only variant callers' and 'Performance metrics'"},
        links=[{"relation": "uses_data", "target_id": DATA[dk]}])
EV = {}
def evaluation(m, pk):
    k = (m if m != "ClairS-TO (tumor-only)" else "ClairS-TO", pk)
    if k not in EV:
        origin = "author_reported" if m == "VarNet-T" else "independent_paper"
        EV[k] = b.evaluation(b.rid("eval", k[0], pk), f"{k[0]} on {pk} tumour-only (Krishnamachari et al. 2026)", SIDS, CFG[m], PROTO[pk], DATA[PSPEC[[p[0] for p in PSPEC].index(pk)][1]], origin,
            {"protocol_id": PROTO[pk], "dataset_version": None, "split": "Not in VarNet-T training", "population": None, "inputs": "Tumour Illumina WGS only",
             "adaptation": None, "metric_implementation": "AUPRC over the caller's own score", "aggregation": "Per sample", "budget": None},
            f"{PSPEC[[p[0] for p in PSPEC].index(pk)][3]}, row '{m}'", missing={"comparison.adaptation": {"reason": "inapplicable", "note": "Pre-trained models"}})
    return EV[k]
for r in T1:
    m = r[0]
    for col, pk in ((1, "seqc2-snv"), (2, "seqc2-indel"), (3, "colo829-snv"), (4, "colo829-indel")):
        ev = evaluation(m, pk)
        loc = f"Supplementary Table 1, row '{m}', column '{'SEQC2' if col < 3 else 'COLO829'} {'SNV' if col % 2 else 'INDEL'}'"
        b.result(b.rid("result", m, pk, "auprc"), f"{m} {pk} AUPRC", SUP, SIDS, ev, P1[m][col - 1], "auprc", "higher", "fraction", loc, REV_SD(loc),
                 qualifier=f"{'SNV' if col % 2 else 'indel'} only, tumour-only")
for m in M2:
    for smp in SAMPLES:
        ev = evaluation(m, "pcawg-snv")
        loc = f"Supplementary Table 2, row '{m}', column '{smp}'"
        b.result(b.rid("result", m, "pcawg", smp, "auprc"), f"{m} PCAWG {smp} AUPRC", SUP, SIDS, ev, PRINTED2[(m, smp)], "auprc", "higher", "fraction", loc, REV_PDF(loc),
                 qualifier=f"SNV only, tumour-only, PCAWG {smp} ({CANCER[smp]})")
for r in T4:
    m = r[0]
    for col, smp in ((1, "AML"), (2, "MBL"), (3, "CLL")):
        ev = evaluation(m, "low-tmb-snv")
        loc = f"Supplementary Table 4, row '{m}', column '{smp}'"
        b.result(b.rid("result", m, "low-tmb", smp, "auprc"), f"{m} {smp} AUPRC", SUP, SIDS, ev, P4[m][col - 1], "auprc", "higher", "fraction", loc, REV_SD(loc),
                 qualifier=f"SNV only, tumour-only, {smp} sample")

UCN = "Select a tumour DNA somatic variant-calling workflow"
CIT = [{"source_id": SUP, "locator": "Supplementary Tables 1, 2 and 4"}, {"source_id": SDS, "locator": "Sheets 'Supplementary Table 1', 'Supplementary Table 2', 'Supplementary Table 4'"},
       {"source_id": ART, "locator": "Results 'Benchmarking on somatic reference datasets', 'Benchmarking using whole cancer genomes from PCAWG'; Methods 'Implementation of tumor-only variant callers', 'PCAWG benchmark samples'; Competing interests"}]
JUDGE = {}
for i, (pk, dk, label, loc, extra) in enumerate(PSPEC):
    lims = next(x for x in b.records if x["id"] == PROTO[pk])["attributes"]["limitations"]
    j = b.judgement(SOMATIC_UC, UCN, PROTO[pk], f"{label} (Krishnamachari et al. 2026)", SIDS, "proxy",
        f"AUPRC of tumour-only callers (VarNet-T, five DeepSom models, DeepSomatic, Mutect2, ClairS-TO): {label}",
        "Proxy, not direct: per-caller AUPRC on real tumour and cell-line WGS with tumour-normal-derived truth sets is close to the use case's endpoint, but the callers used tumour reads only, whereas this use case's inputs include a matched normal and its exclusions list tumour-only calling; precision, recall and F1 are not extracted. Linked as the closest evidence for users without a matched normal.",
        lims, CIT, "krishnamachari2026-varnet-t", "Tumour-only callers on Illumina WGS (Krishnamachari et al. 2026, VarNet-T developers)", label, i + 1, "auprc")
    JUDGE[pk] = j
    if pk.startswith("seqc2"):
        next(x for x in b.records if x["id"] == j)["attributes"]["excluded_evaluations"] = [{"id": EV[("Deepsomatic (tumor-only)", pk)], "reason": "DeepSomatic was trained on SEQC2 HCC1395 data (Introduction), so it is not held out on this sample."}]
print(XML_SHA, PDF_SHA, SD_SHA, b.write())
if len(sys.argv) > 5:
    import json
    json.dump({"evaluations": {"|".join(k): v for k, v in EV.items()}, "judgements": JUDGE}, open(sys.argv[5], "w"), indent=1)
