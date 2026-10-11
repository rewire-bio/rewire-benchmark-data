"""Kim et al. 2025 (Ann Lab Med 46(3), doi:10.3343/alm.2025.0300): Arriba-based whole RNA-seq fusion detection
against conventional diagnostics in 101 acute leukaemia patients. Every cell of Table 2 and the
performance figures printed in Results and Discussion.

Usage: python3 -I extract_fusion_leukaemia.py <article.xml> <batch-folder>
"""
import sys, os, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, FUSION_UC

xml, folder = sys.argv[1:3]
SHA = sha256(xml)
assert SHA == "4d3a6d48fc107763bffe18ff7dbcb6ab97b86757e69ff89ae595f3243f30bad1", SHA
t = open(xml, encoding="utf-8").read()
tw = [m.group(0) for m in re.finditer(r"<table-wrap\b.*?</table-wrap>", t, re.S)]
t2 = next(x for x in tw if "Fusion genes detected using conventional diagnostics and RNA-seq" in x)
cells = lambda r: [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip() for c in re.findall(r"<t[dh]\b.*?</t[dh]>", r, re.S)]
rows = [cells(r) for r in re.findall(r"<tr\b.*?</tr>", t2, re.S)]
assert rows[0][3:] == ["Number of fusions detected using conventional diagnostics", "Number of fusions detected using RNA-seq", "Concordance, %"], rows[0]
section, data = None, []
for r in rows[1:]:
    if len(r) == 1:
        section = r[0]; continue
    assert len(r) == 6, r
    data.append((section, [re.sub(r"\s+", "", r[0])] + r[1:]))
assert len(data) == 26, len(data)
assert sum(int(r[3]) for s, r in data) == 48 and sum(int(r[4]) for s, r in data if int(r[3]) > 0) == 40 and sum(int(r[4]) for s, r in data if int(r[3]) == 0) == 12
body = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t)))
TEXT = {
    "concordance": ("The overall concordance rate between RNA-seq and conventional diagnostics was 80.8%.", "80.8%", "percent-agreement", "higher", "overall, 104 fusion detection results in 101 patients",
                    "Results 'Fusion gene detection performance of RNA-seq compared with that of conventional diagnostic methods' paragraph 1"),
    "sensitivity": ("Of the 48 fusion genes detected using conventional diagnostics, RNA-seq helped identify 40 and missed eight (83.3% sensitivity)", "83.3%", "recall", "higher", "overall, 48 fusions detected by conventional diagnostics",
                    "Results 'Fusion gene detection performance of RNA-seq compared with that of conventional diagnostic methods' paragraph 1"),
    "one-minus-specificity": ("among 56 fusion-negative results based on conventional diagnostics, RNA-seq helped identify 12 fusion genes (21.4%, reflecting 1 – specificity)", "21.4%", "false-positive-rate", "lower", "overall, 56 fusion-negative results by conventional diagnostics; RNA-seq-only fusions counted as errors, though the authors describe several as well-known recurrent fusions and confirmed one by RT-PCR and Sanger sequencing",
                              "Results 'Fusion gene detection performance of RNA-seq compared with that of conventional diagnostic methods' paragraph 1"),
    "sensitivity-aml": ("with a fusion detection sensitivity of 83.3%, comparable across AML (86.4%) and B-ALL (87.0%)", "86.4%", "recall", "higher", "AML patients, fusions detected by conventional diagnostics", "Discussion paragraph 2"),
    "sensitivity-b-all": ("with a fusion detection sensitivity of 83.3%, comparable across AML (86.4%) and B-ALL (87.0%)", "87.0%", "recall", "higher", "B-ALL patients, fusions detected by conventional diagnostics", "Discussion paragraph 2"),
}
for k, (quote, *_rest) in TEXT.items():
    assert quote in body, k

URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13071280/fullTextXML"
b = Batch(folder, "rna-fusion-leukaemia-20261011", ["rna-transcriptomes"])
SRC = b.source("rna-fusion-leukaemia-20261011-source-kim2025", "Detection of Fusion Genes Using RNA Sequencing in Acute Leukemia", {
    "url": "https://doi.org/10.3343/alm.2025.0300", "artifact_url": URL, "version": "Annals of Laboratory Medicine 46(3), epub 2025-10-16; PMC13071280 full-text XML",
    "retrieved_at": "2026-10-11T21:37:42Z", "artifact_sha256": SHA, "doi": "10.3343/alm.2025.0300", "publication_status": "peer_reviewed",
    "licence": "CC-BY-NC-4.0", "media_type": "application/xml"}, "Primary source retrieved and hashed for the 2026-10-11 oncology use-case literature pass.")
SIDS = [SRC]
def REV(loc, how):
    return extraction_review([how], ("Parsed table-wrap 'Table 2' of the pinned article XML with extract/extract_fusion_leukaemia.py; header, section and row count asserted, and column sums checked against the 48, 40 and 12 printed in Results. "
                                     if how == "deterministic-table-parse" else "Sentence asserted verbatim in the pinned article XML by extract/extract_fusion_leukaemia.py. ") + loc, SHA, URL)

METHOD = "rna-fusion-20261009-method-arriba"
CFG = b.entity("configuration", b.rid("config", "arriba-2-4-0-igv-review"), "STAR 2.7.7a and Arriba v2.4.0 high-confidence calls with manual IGV review (Kim et al. 2025)",
    "Whole RNA-seq fusion workflow as run in the cited clinical comparison.", SIDS,
    {"reported_name": "Arriba", "version": "v2.4.0", "foundation_model_eligible": False,
     "parameters": "Trimmomatic 0.39; STAR 2.7.7a to GRCh37; Arriba v2.4.0 keeping high-confidence in-frame fusions and high-confidence fusions involving MECOM, IGH, IGK, IGL, TRA, TRB, TRD or TRG; every call manually checked in IGV 2.16.0",
     "access_reuse": "Public open-source software plus manual review", "source_locator": "Methods 'RNA-seq and fusion gene detection'"},
    method_types=["conventional_pipeline"], links=[{"relation": "configuration_of", "target_id": METHOD}])
DATA = b.entity("dataset", b.rid("data", "smc-acute-leukaemia"), "Samsung Medical Center acute leukaemia bone-marrow whole RNA-seq, 101 patients (2022-2023)",
    "Diagnostic bone-marrow aspirates of 101 patients with acute leukaemia (54 AML, 37 B-ALL, 8 T-ALL, 2 MPAL) with karyotyping, FISH or multiplex RT-PCR results.", SIDS,
    {"population": "101 patients, September 2022 to September 2023; 104 fusion detection results", "assay": "Illumina Stranded mRNA Prep, NextSeq 550Dx or NovaSeq 6000, 2 x 150 bp; median 90 million reads (range 14 to 1,021 million)",
     "split": "Retrospective clinical cohort", "source_locator": "Methods 'Patients and samples', 'RNA-seq and fusion gene detection'; Table 1",
     "missing_metadata": {"accession": {"reason": "unreported"}, "version": {"reason": "inapplicable"}}})
LIM = ["One workflow (Arriba with manual review) compared with conventional diagnostics; no other caller is evaluated, so this is not a caller comparison.",
       "Truth is conventional diagnostics (karyotyping, FISH, multiplex RT-PCR), which miss some fusions: the 12 RNA-seq-only fusions count against specificity, although the authors describe several as well-known recurrent fusions and confirmed one of them (MLLT10::UBE2L6) by RT-PCR and Sanger sequencing (Figure 1); validation was attempted only for novel or rare fusions with residual sample.",
       "Missed fusions are attributed by the authors to low blast proportion, subclonality, poor aspirates, complex rearrangements or enhancer hijacking, not to the caller alone.",
       "Single centre, acute leukaemia only (adult and paediatric); 48 conventional-positive fusions; no interval estimates.",
       "Every call was manually reviewed in IGV, so the false-call burden of raw Arriba output is not measured.",
       "Per-patient results (Supplemental Data Tables S2 and S3) and Supplemental Figure S1 were not retrieved; the AML (86.4%) and B-ALL (87.0%) sensitivities are printed only in the Discussion, without denominators."]
PROTO = b.entity("protocol", b.rid("protocol", "conventional-diagnostics"), "Acute leukaemia whole RNA-seq fusion detection against conventional diagnostics (Kim et al. 2025)",
    "Per-fusion and overall detection of fusions by Arriba-based whole RNA-seq compared with karyotyping, FISH and multiplex RT-PCR.", SIDS,
    {"protocol": "Each patient's fusion status by conventional diagnostics (karyotyping, FISH, multiplex RT-PCR HemaVision) compared with RNA-seq calls; sensitivity over conventional-positive fusions, 1 - specificity over conventional-negative results, and overall concordance over 104 results.",
     "version": "Table 2; Results 'Fusion gene detection performance of RNA-seq compared with that of conventional diagnostic methods'", "metric": "recall", "denominator": 48,
     "limitations": LIM, "source_locator": "Methods 'Conventional diagnostics', 'Statistical analysis'; Table 2; Results"},
    links=[{"relation": "uses_data", "target_id": DATA}])
EV = b.evaluation(b.rid("eval", "arriba", "conventional-diagnostics"), "Arriba v2.4.0 with IGV review against conventional diagnostics in 101 acute leukaemia patients (Kim et al. 2025)", SIDS, CFG, PROTO, DATA, "independent_paper",
    {"protocol_id": PROTO, "dataset_version": None, "split": "Retrospective cohort", "population": "101 patients with acute leukaemia", "inputs": "Bone-marrow whole RNA-seq, 2 x 150 bp",
     "adaptation": None, "metric_implementation": "Fusion-level agreement with conventional diagnostics", "aggregation": "Pooled over patients; per-fusion counts in Table 2", "budget": None},
    "Table 2; Results paragraph 1 of the performance section", missing={"comparison.adaptation": {"reason": "inapplicable"}})
for s, r in data:
    g = r[0]; sec = {"Fusion genes detected using conventional diagnostics": "conventional-positive", "Fusion genes detected using conventional diagnostics with unspecified partner genes": "conventional-positive, partner unspecified",
                     "Fusion genes detected using RNA-seq only": "RNA-seq only"}[s]
    gid = re.sub(r"[^A-Za-z0-9]+", "-", g.replace("α", "A").replace("?", "unspecified").replace("†", "")).strip("-")
    for col, label, metric, d, unit, ud in ((3, "Number of fusions detected using conventional diagnostics", "count", "unknown", "count", "counted entity: patients with this fusion by conventional diagnostics"),
                                           (4, "Number of fusions detected using RNA-seq", "true-positive-count" if sec != "RNA-seq only" else "count", "higher" if sec != "RNA-seq only" else "unknown", "count", "counted entity: patients with this fusion called by RNA-seq"),
                                           (5, "Concordance, %", "percent-agreement", "higher", "percent", None)):
        loc = f"Table 2, section '{s}', row '{g}', column '{label}'"
        extra = {"printed_value_basis": "Cell text as printed"}
        undefined = col == 5 and sec == "RNA-seq only"
        if undefined:
            extra["undefined_reason"] = "Printed 0 for fusions with no conventional detection; agreement is not defined for these rows"
        b.result(b.rid("result", gid, ["conv", "rnaseq", "concordance"][col - 3]), f"{g} {label}", SRC, SIDS, EV, r[col], metric, d, unit, loc, REV(loc, "deterministic-table-parse"),
                 qualifier=f"{g} ({sec}; {r[1]})", unit_detail=ud, extra=extra,
                 **({"numeric": False, "value_missing": {"reason": "inapplicable", "note": "Concordance is not defined for fusions with no conventional detection; the table prints 0"}} if undefined else {}))
for k, (quote, printed, metric, d, qual, where) in TEXT.items():
    loc = f"{where}: '{quote}'"
    b.result(b.rid("result", "arriba", k), f"Arriba RNA-seq vs conventional diagnostics {k}", SRC, SIDS, EV, printed, metric, d, "percent", loc, REV(loc, "transcription"), qualifier=qual)
JUDGE = b.judgement(FUSION_UC, "Select a tumour RNA fusion-detection workflow", PROTO, "Acute leukaemia whole RNA-seq against conventional diagnostics (Kim et al. 2025)", SIDS, "direct",
    "Sensitivity, 1 - specificity and concordance of an Arriba-based whole RNA-seq workflow with manual review against karyotyping, FISH and RT-PCR, overall, by subtype and per fusion",
    "Real patient specimens scored against orthogonal clinical assays, not against the workflow's own calls, measure the sensitivity the use case asks about without the ascertainment bias the use case names as a gap; only one workflow is evaluated.",
    LIM, [{"source_id": SRC, "locator": "Methods 'RNA-seq and fusion gene detection', 'Statistical analysis'; Table 2; Results 'Fusion gene detection performance of RNA-seq compared with that of conventional diagnostic methods'; Discussion paragraphs 2-3"}],
    "kim2025-leukaemia", "Arriba whole RNA-seq against conventional diagnostics in acute leukaemia (Kim et al. 2025)", "Acute leukaemia, 101 patients", 1, "recall")
print(SHA, b.write())
