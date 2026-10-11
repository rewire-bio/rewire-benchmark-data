"""López-Cade et al. 2025 (Biomolecules 15:1532): every cell of Table 1 (synthetic WES, three callers).

Usage: python3 -I extract_wes_synthetic.py <article.xml> <batch-folder>
Parses table-wrap 'Table 1' of the pinned Europe PMC XML and asserts the header and row labels.
"""
import sys, os, re, html, gzip
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, SOMATIC_UC

xml, folder = sys.argv[1:3]
SHA = sha256(xml)
assert SHA == "0d115f3cebe36ed4a0d078b459f7e083a32ceaa5e447f8eefe2dbde38cae863f", SHA
t = open(xml, encoding="utf-8").read()
tw = [m.group(0) for m in re.finditer(r"<table-wrap\b.*?</table-wrap>", t, re.S)]
assert len(tw) == 1
cells = lambda r: [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh]\b.*?</t[dh]>", r, re.S)]
rows = [cells(r) for r in re.findall(r"<tr\b.*?</tr>", tw[0], re.S)]
HDR = ["Caller", "Total Truth", "Total Query", "TP", "FP", "FN", "Recall", "Precision"]
assert rows[0] == HDR, rows[0]
assert [r[0] for r in rows[1:]] == ["Mutect2", "FreeBayes", "Strelka2"]
for r in rows[1:]:
    assert r[1] == "4709"

os.makedirs(os.path.join(folder, "artifacts"), exist_ok=True)
ARCH = os.path.join(folder, "artifacts", "PMC12650410.xml.gz")
with open(ARCH, "wb") as f:
    with gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as g:
        g.write(open(xml, "rb").read())

URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12650410/fullTextXML"
b = Batch(folder, "somatic-wes-synthetic-20261011", ["dna-genomes"])
SRC = b.source("somatic-wes-synthetic-20261011-source-lopezcade2025", "Comparative Evaluation of Mutect2, Strelka2, and FreeBayes for Somatic SNV Detection in Synthetic and Clinical Whole-Exome Sequencing Data", {
    "url": "https://doi.org/10.3390/biom15111532", "artifact_url": URL, "version": "Biomolecules 15(11):1532, published 2025-10-30; PMC12650410 full-text XML",
    "retrieved_at": "2026-10-11T21:37:40Z", "artifact_sha256": SHA, "doi": "10.3390/biom15111532", "publication_status": "peer_reviewed",
    "licence": "CC-BY-4.0", "media_type": "application/xml"}, "Primary source retrieved and hashed for the 2026-10-11 oncology use-case literature pass.")
SIDS = [SRC]
REVIEW = lambda loc: extraction_review(["deterministic-table-parse"], "Parsed table-wrap 'Table 1' of the pinned article XML with extract/extract_wes_synthetic.py; header and caller labels asserted. " + loc, SHA, URL)

DATA = b.entity("dataset", b.rid("data", "bamsurgeon-wes"), "BAMSurgeon synthetic tumour-normal WES with 4,709 COSMIC SNVs (López-Cade et al. 2025)",
    "Synthetic whole-exome tumour-normal pair: 4,709 of 10,000 randomly selected COSMIC SNVs inserted with BAMSurgeon 1.4.1 into a variant-free BAM; the paired germline BAM has no inserted mutations.", SIDS,
    {"population": "One synthetic tumour-normal pair; 4,709 inserted SNVs (BAMSurgeon parameters --mindepth 50 --maxdepth 500 --minmutreads 5)",
     "assay": "Synthetic WES BAMs processed with nf-core/sarek 3.5.0 (BWA-MEM, GRCh38)", "split": "Single synthetic evaluation sample",
     "source_locator": "Methods 2.3 'Generation of Synthetic Data with Known Somatic SNVs' and 2.4 'Variant Calling and Bioinformatic Workflow'; Table 1 'Total Truth'",
     "missing_metadata": {"version": {"reason": "unreported"}, "accession": {"reason": "unavailable", "note": "Synthetic data available from the corresponding author on request (Data Availability Statement)"}}})
PROTO = b.entity("protocol", b.rid("protocol", "bamsurgeon-wes-snv"), "Synthetic WES tumour-normal pair, 4,709 inserted COSMIC SNVs (López-Cade et al. 2025 Table 1)",
    "Recall and precision of PASS somatic SNV calls from three callers run with nf-core/sarek default settings.", SIDS,
    {"protocol": "Tumour-normal calling with nf-core/sarek 3.5.0 default parameters; recall = TP/(TP+FN), precision = TP/(TP+FP) against the inserted SNVs.",
     "version": "Table 1", "metric": "recall", "denominator": 4709,
     "limitations": ["One synthetic WES pair; BAMSurgeon inserts SNVs into real reads but does not model tumour artefacts, so almost no false positives are expected (Discussion).",
                     "SNVs only; indels not evaluated.",
                     "Callers run with nf-core/sarek 3.5.0 defaults and no tuning; no custom panel of normals was specified, and sarek's default GATK GRCh38 panel of normals was applied to Mutect2 (Discussion).",
                     "Mutect2 is reported as 'version 2.2', which is not a GATK release number; the GATK version is not stated.",
                     "FreeBayes row is internally inconsistent: TP 1,908 plus FN 2,314 is 4,222, not the 4,709 printed as Total Truth, and the printed recall 0.4519 equals 1,908/4,222, whereas 1,908/4,709 is 0.4052. Mutect2 and Strelka2 rows sum to 4,709. The source does not say which value is wrong.",
                     "Authors are from the clinical group that generated the patient samples; they did not develop the callers."],
     "source_locator": "Table 1; Methods 2.4 'Variant Calling and Bioinformatic Workflow' and 'Performance Evaluation'; Discussion"},
    links=[{"relation": "uses_data", "target_id": DATA}])
VER = {"Mutect2": None, "Strelka2": "2.9.10", "FreeBayes": "1.3.6"}
FAM = {"Mutect2": "somatic-20261009-method-mutect2", "Strelka2": "somatic-20261009-method-strelka", "FreeBayes": "somatic-20261009-method-freebayes"}
METRICS = [("Total Query", "count", "unknown", "count", "counted entity: PASS SNV calls"),
           ("TP", "true-positive-count", "higher", "count", "counted entity: inserted SNVs called"),
           ("FP", "false-positive-count", "lower", "count", "counted entity: calls not among the inserted SNVs"),
           ("FN", "false-negative-count", "lower", "count", "counted entity: inserted SNVs not called"),
           ("Recall", "recall", "higher", "fraction", None), ("Precision", "precision", "higher", "fraction", None)]
EVALS = []
for r in rows[1:]:
    c = r[0]
    attrs = {"reported_name": c, "foundation_model_eligible": False,
             "parameters": "nf-core/sarek 3.5.0 default parameters; FreeBayes has no PASS filter, so the authors kept calls with QUAL >= 1, SAF > 0, SAR > 0, RPL > 1 and RPR > 1 (Methods 'Variant Calling and Bioinformatic Workflow')" if c == "FreeBayes" else "nf-core/sarek 3.5.0 default parameters, tumour-normal mode, PASS SNVs",
             "access_reuse": "Public open-source software", "source_locator": "Methods 2.4 'Variant Calling and Bioinformatic Workflow'"}
    if VER[c]:
        attrs["version"] = VER[c]
    else:
        attrs["missing_metadata"] = {"version": {"reason": "conflicting", "note": "Printed as 'Mutect2 (version 2.2)', which is not a GATK release; GATK version not stated"}}
    cfg = b.entity("configuration", b.rid("config", c), f"{c}{' ' + VER[c] if VER[c] else ''} via nf-core/sarek 3.5.0 (López-Cade et al. 2025)", f"{c} as run in the cited comparison.", SIDS, attrs,
                   method_types=["conventional_pipeline"], links=[{"relation": "configuration_of", "target_id": FAM[c]}])
    ev = b.evaluation(b.rid("eval", c, "bamsurgeon-wes-snv"), f"{c} on the synthetic WES pair (López-Cade et al. 2025)", SIDS, cfg, PROTO, DATA, "independent_paper",
        {"protocol_id": PROTO, "dataset_version": None, "split": "Single synthetic pair", "population": "4,709 inserted SNVs", "inputs": "Synthetic tumour and normal WES BAMs",
         "adaptation": None, "metric_implementation": "Match of PASS SNV calls to the inserted SNV list", "aggregation": "Single pair", "budget": None},
        f"Table 1, row '{c}'", missing={"comparison.adaptation": {"reason": "inapplicable", "note": "Default parameters"}})
    EVALS.append(ev)
    for (col, metric, d, unit, ud), printed in zip(METRICS, r[2:]):
        loc = f"Table 1, row '{c}', column '{col}'"
        b.result(b.rid("result", c, "bamsurgeon-wes-snv", col), f"{c} synthetic WES SNV {col}", SRC, SIDS, ev, printed, metric, d, unit, loc, REVIEW(loc),
                 qualifier="SNV only, synthetic WES" + ((", total filtered calls" if c == "FreeBayes" else ", total PASS calls") if col == "Total Query" else ""),
                 unit_detail=("counted entity: filtered SNV calls" if (c == "FreeBayes" and col == "Total Query") else ud))
FB = b.rid("eval", "FreeBayes", "bamsurgeon-wes-snv")
JUDGE = b.judgement(SOMATIC_UC, "Select a tumour DNA somatic variant-calling workflow", PROTO, "Synthetic WES tumour-normal SNVs (López-Cade et al. 2025 Table 1)", SIDS, "proxy",
    "Recall and precision of Mutect2, Strelka2 and FreeBayes PASS SNV calls on a BAMSurgeon synthetic WES tumour-normal pair",
    "Proxy, not direct: the inputs and endpoint match the use case (tumour-normal WES, per-caller precision and recall), but the tumour is synthetic, with SNVs inserted into otherwise clean reads, so precision is near 1 by construction and recall mostly reflects default filtering of inserted low-VAF variants.",
    next(x for x in b.records if x["id"] == PROTO)["attributes"]["limitations"],
    [{"source_id": SRC, "locator": "Table 1; Methods 2.3 'Generation of Synthetic Data with Known Somatic SNVs', 2.4 'Variant Calling and Bioinformatic Workflow', 'Performance Evaluation'; Discussion"}],
    "lopezcade2025-wes-synthetic", "Three callers on a synthetic WES pair (López-Cade et al. 2025)", "Synthetic WES, SNVs", 1, "recall")
jrec = next(x for x in b.records if x["id"] == JUDGE)
jrec["attributes"]["excluded_evaluations"] = [{"id": FB, "reason": "Table 1 row is internally inconsistent: TP plus FN is 4,222, not the 4,709 truth variants, and the printed recall uses 4,222 as denominator."}]
print(SHA, b.write())
