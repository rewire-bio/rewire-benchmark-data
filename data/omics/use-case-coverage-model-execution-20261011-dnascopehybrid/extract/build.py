"""Build batch.jsonl for Hu et al. 2026 (DNAscope Hybrid, Frontiers in Bioinformatics), Table 2.

Usage: python3 -I build.py <PMC12813096 full-text XML>

Parsed from the table-wrap of the pinned article XML with the header and row labels asserted.
"""
import hashlib
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ucx import entity, extraction_review, judgement, result, source, write  # noqa: E402

BATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "model-execution-20261011-"
XML_SHA = "b138dd8976f01b4ff50f72669dea3a7062f564a9cb359417aad0dc72a8b6c859"
SRC = P + "source-hu2026-dnascope-hybrid"
SOURCES = [SRC]

xml = open(sys.argv[1], "rb").read()
assert hashlib.sha256(xml).hexdigest() == XML_SHA
xml = xml.decode()

records, claims = [], []
records.append(source(SRC, "A novel and accelerated method for integrated alignment and variant calling from short and long reads",
                      "https://doi.org/10.3389/fbinf.2025.1691056", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12813096/fullTextXML",
                      "Frontiers in Bioinformatics 5:1691056, published 2026-01-05; PMC12813096 full-text XML", "2026-10-11T21:42:46Z", XML_SHA,
                      "10.3389/fbinf.2025.1691056", "peer_reviewed", "CC-BY-4.0", "application/xml",
                      "Primary article retrieved and hashed for the diagnostic genomics execution literature pass (2026-10-11)."))

tw = re.search(r'<table-wrap id="T2".*?</table-wrap>', xml, re.S).group(0)
assert "Compute resource benchmark for DNAscope pipelines" in tw
cell = lambda c: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip()
rows = [[cell(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)] for tr in re.findall(r"<tr>(.*?)</tr>", tw, re.S)]
assert rows[0] == ["Pipeline", "DNAscope Hybrid", "DNAscope LongRead", "DNAscope (short reads)"], rows[0]
assert [r[0] for r in rows[1:]] == ["Dataset", "Alignment (min)", "Preprocessing (min)", "Variant calling (min)", "Total runtime (min)",
                                    "Core-hours", "On-demand ($)", "Spot ($)"], rows

FAC = {"areas": ["dna-genomes"], "contexts": ["clinical_research"], "method_types": ["conventional_pipeline"]}
METHOD = P + "method-sentieon-dnascope"
records.append(entity(METHOD, "method", "Sentieon DNAscope", "Sentieon germline variant-calling pipelines (DNAscope for short reads, DNAscope LongRead, DNAscope Hybrid) running on CPUs.",
                      SOURCES, {"reported_name": "DNAscope", "entity_level": "method", "access": "Commercial licensed software",
                                "source_locator": "Introduction; Methods; Table 3",
                                "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
                      facets=FAC))
HW = {"description": "Azure Standard HB120rs v3: 120 vCPUs, 456 GiB memory, 512 GB premium SSD (Table 2 caption)"}
PIPES = [
    ("DNAscope Hybrid", "dnascope-hybrid", "10× PB + 35× ILMN", "10x PacBio HiFi plus 35x Illumina", "SNP, indel, SV and CNV"),
    ("DNAscope LongRead", "dnascope-longread-pb", "30× PB", "30x PacBio HiFi", "SNP, indel and SV"),
    ("DNAscope (short reads)", "dnascope-short-read", "30× ILMN", "30x Illumina", "SNP, indel and CNV"),
]
PID = P + "protocol-hu2026-dnascope-azure-compute"
LIM = [
    "Author-reported by the software vendor: all authors were employed by Sentieon Inc.",
    "The three pipelines run on different inputs (hybrid, long-read and short-read data at different depths), so the table is not a like-for-like comparison.",
    "The sample behind Table 2 is not named; the study's data are GIAB HG002 to HG004 (PacBio Revio and precisionFDA Truth Challenge V2 Illumina).",
    "One value per pipeline is printed; the number of runs behind it is not stated and no spread is printed. The Sentieon software version is not stated for Table 2.",
    "Costs are Azure on-demand and spot prices and exclude the Sentieon licence.",
    "The LongRead and short-read runtimes were previously published in a Microsoft blog post (Results 'Compute resource benchmark').",
]
records.append(entity(PID, "protocol", "FASTQ-to-VCF runtime, core-hours and Azure cost of three Sentieon DNAscope pipelines on one 120-vCPU instance (Hu et al. 2026 Table 2)",
                      "Runtime by stage, core-hours and compute cost for DNAscope Hybrid, DNAscope LongRead and DNAscope short-read pipelines.", SOURCES,
                      {"protocol": "Alignment, preprocessing and variant calling from FASTQ on an Azure Standard HB120rs v3 instance; runtime by stage in minutes, total core-hours, on-demand and spot compute cost.",
                       "version": "Table 2", "metric": "runtime", "limitations": LIM, "source_locator": "Results 'Compute resource benchmark'; Table 2"},
                      [("uses_data", f"{P}data-hu2026-{k}") for _, k, *_ in PIPES], facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"]}))
REV = extraction_review(["deterministic-table-parse"],
    "Deterministic parse of the Table 2 table-wrap in the pinned article XML (extract/build.py), with header and row labels asserted.",
    "Extraction only; pending independent review.")
ROWSPEC = {
    "Alignment (min)": ("runtime", "lower", "minute", "alignment stage", "alignment", None),
    "Preprocessing (min)": ("runtime", "lower", "minute", "preprocessing stage", "preprocessing", None),
    "Variant calling (min)": ("runtime", "lower", "minute", "variant calling stage", "variant-calling", None),
    "Total runtime (min)": ("runtime", "lower", "minute", "total, FASTQ to VCF", "total-runtime", None),
    "Core-hours": ("cpu-time", "lower", "hour", "total, FASTQ to VCF", "core-hours", "core-hours"),
    "On-demand ($)": ("compute-cost", "lower", "us-dollar", "Azure on-demand price, FASTQ to VCF", "on-demand-cost", "printed $"),
    "Spot ($)": ("compute-cost", "lower", "us-dollar", "Azure spot price, FASTQ to VCF", "spot-cost", "printed $"),
}
for col, (label, key, dataset_label, dataset_text, outputs) in enumerate(PIPES, start=1):
    assert rows[1][col] == dataset_label, rows[1]
    did = f"{P}data-hu2026-{key}"
    records.append(entity(did, "dataset", f"{dataset_text} WGS input for {label} (Hu et al. 2026 Table 2)", "Input reads for the compute benchmark.", SOURCES,
                          {"population": f"{dataset_text} whole-genome reads; sample not named for Table 2", "split": "One value; number of runs not stated",
                           "source_locator": "Table 2 row 'Dataset'; Methods 'Datasets used in this study'",
                           "missing_metadata": {"accession": {"reason": "unreported", "note": "Sample not named for Table 2"}, "version": {"reason": "unreported"}}},
                          facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"]}))
    cid = f"{P}config-hu2026-{key}-azure-hb120rs-v3"
    records.append(entity(cid, "configuration", f"Sentieon {label} on Azure HB120rs v3 (Hu et al. 2026)", f"{label} pipeline; outputs {outputs}.", SOURCES,
                          {"reported_name": label, "foundation_model_eligible": False, "hardware": HW, "protocol": f"{label} pipeline from FASTQ; outputs {outputs}",
                           "access_reuse": "Commercial licensed software", "source_locator": "Table 2 caption and column '" + label + "'",
                           "missing_metadata": {"version": {"reason": "unreported", "note": "Sentieon release not stated for Table 2"}}},
                          [("configuration_of", METHOD)], facets=FAC))
    eid = f"{P}eval-hu2026-{key}-azure"
    records.append(entity(eid, "evaluation", f"{label} compute benchmark on Azure (Hu et al. 2026)", "Published pipeline execution benchmark; transcribed, not reproduced.", SOURCES,
                          {"origin": "author_reported", "protocol": PID, "version": "Primary source as retrieved 2026-10-11",
                           "comparison": {"protocol_id": PID, "dataset_version": None, "split": "One value; number of runs not stated", "population": f"{dataset_text} WGS (sample not named)",
                                          "inputs": "FASTQ", "adaptation": None, "metric_implementation": None, "aggregation": "One value per pipeline; number of runs not stated",
                                          "budget": "One Azure Standard HB120rs v3 instance (120 vCPUs)"},
                           "source_locator": f"Table 2 column '{label}'",
                           "missing_metadata": {"comparison.dataset_version": {"reason": "unreported"},
                                                "comparison.metric_implementation": {"reason": "unreported", "note": "How runtime and cost were measured is not stated"}}},
                          [("system", cid), ("assessment", PID), ("data", did)], facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"]}))
    for row in rows[2:]:
        metric, direction, unit, qual, short, detail = ROWSPEC[row[0]]
        printed = row[col]
        rid = f"{P}result-hu2026-{key}-{short}"
        loc = f"Table 2, row '{row[0]}', column '{label}'"
        records.append(result(rid, f"hu2026 {label} {row[0]}", SOURCES, eid, metric, direction, unit, printed, printed, loc, REV,
                              qualifier=f"{qual}; {dataset_text}", unit_detail=detail))
        claims.append((rid, SRC, loc, printed, "xml-table"))

records.append(judgement("use-case-mapping-model-execution-20261011-hu2026-dnascope-azure-compute", PID,
    "Runtime, core-hours and Azure cost of three Sentieon DNAscope pipelines (Hu et al. 2026)", SOURCES, "proxy",
    "Stage runtimes, total runtime, core-hours and Azure on-demand and spot cost for DNAscope Hybrid (10x PacBio plus 35x Illumina), DNAscope LongRead (30x PacBio) and DNAscope (30x Illumina) on one 120-vCPU instance",
    "Gives per-genome runtime, CPU time and cloud cost for CPU-only long-read and hybrid germline pipelines on stated hardware, which no previously linked source covers. Proxy: vendor-reported values with an unstated number of runs, an unnamed sample, different inputs per pipeline, no stated software version and no licence cost.",
    ["Inspect every linked evaluation's source locator before citing a result.",
     "Do not combine this mapping's evaluations with any other protocol's results; hardware, inputs, software versions and timing boundaries differ between sources.",
     "Do not read the three columns as a ranking: each pipeline has different input data."],
    LIM, [{"source_id": SRC, "locator": "Results 'Compute resource benchmark'; Table 2; Conflict of interest"}],
    "hu2026-dnascope-azure", "Sentieon DNAscope pipelines on one Azure instance (Hu et al. 2026)", None, None, "runtime"))

n = write(BATCH, records, claims)
print(n, "records;", sum(r["kind"] == "result" for r in records), "results")
