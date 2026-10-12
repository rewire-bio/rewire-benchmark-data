"""Build batch.jsonl for Marangoni et al. 2026 (GeNePi), Supplementary Table S1.

Usage: python3 -I build.py <GeNePi_SupplInfo_rev_bbag001.pdf>

Parsed from the `pdftotext -layout` text of the pinned supplementary PDF with the header and the five depth
rows asserted. Durations are printed as "17h", "1h 36m", "42 m"; numeric_value is the duration in minutes.
"""
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ucx import entity, extraction_review, judgement, result, source, write  # noqa: E402

BATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "model-execution-20261011-"
SUPP_SHA = "afa166a30320efd633cb28ddc91a05082854b0ef5e6593333c0ce9dbd2ae1bb9"
XML_SHA = "6251ae2946d56aff88ef3d11b717a3583f1c18ed45eef9064931f155ab6964e6"
ZIP_SHA = "05ea003358ddeb2ae2bb3dd5200a4e87541e798bccb61e96f177498f7b8e8140"
SRC = P + "source-marangoni2026-genepi"
SUPP = P + "source-marangoni2026-genepi-supplement"
SOURCES = [SRC, SUPP]

pdf = sys.argv[1]
assert hashlib.sha256(open(pdf, "rb").read()).hexdigest() == SUPP_SHA
text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout

records, claims = [], []
records += [
    source(SRC, "GeNePi: a graphics processing unit enhanced next-generation bioinformatics pipeline for whole-genome sequencing analysis",
           "https://doi.org/10.1093/bib/bbag001", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12832024/fullTextXML",
           "Briefings in Bioinformatics 27(1), published 2026-01-25; PMC12832024 full-text XML", "2026-10-11T21:42:44Z", XML_SHA,
           "10.1093/bib/bbag001", "peer_reviewed", "CC-BY-4.0", "application/xml",
           "Primary article retrieved and hashed for the diagnostic genomics execution literature pass (2026-10-11)."),
    source(SUPP, "GeNePi: Supplementary Information", "https://doi.org/10.1093/bib/bbag001",
           "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12832024/supplementaryFiles",
           "genepi_supplinfo_rev_bbag001.pdf from the Europe PMC supplementary files of PMC12832024", "2026-10-11T21:42:45Z", SUPP_SHA,
           "10.1093/bib/bbag001", "peer_reviewed", "CC-BY-4.0", "application/pdf",
           "Supplementary PDF retrieved and hashed for the diagnostic genomics execution literature pass (2026-10-11)."),
]
records[1]["attributes"]["artifact_member"] = "genepi_supplinfo_rev_bbag001.pdf"
records[1]["attributes"]["retrieval_note"] = f"Europe PMC supplementaryFiles zip (SHA-256 {ZIP_SHA}); artifact_sha256 is the PDF member."

FAC = {"areas": ["dna-genomes"], "contexts": ["clinical_research"], "method_types": ["conventional_pipeline"]}
CFGS = [
    ("CPU", "gatk-cpu", "model-execution-20261009-method-gatk-best-practices-cpu", "CPU-equivalent GATK germline pipeline on a CPU node (Marangoni et al. 2026)",
     "Two Intel Xeon 6242 CPUs, 192 GB RAM, two 500 GB HDDs, 10 GbE (CPU node, Supplementary S3.1)",
     "BWA-MEM alignment, samtools sort, MarkDuplicates, BaseQualityScoreRecalibration and ApplyBQSR, HaplotypeCaller, as in the NVIDIA documentation of the CPU equivalent", None, "independent_paper"),
    ("GPU-2xV100", "parabricks-4-3-0-2xv100", "model-execution-20261009-method-parabricks", "Parabricks germline v4.3.0 (GeNePi PB_germ) on 2 V100 GPUs (Marangoni et al. 2026)",
     "Two Xeon 6244 CPUs, 384 GB RAM, two NVIDIA Tesla V100-PCIE-32GB (Supplementary S3.1)",
     "GeNePi PB_germ module: Parabricks germline pipeline v4.3.0 (alignment to GRCh38, duplicate marking, BQSR, HaplotypeCaller)", "v4.3.0", "author_reported"),
    ("GPU-2xA100", "parabricks-4-3-0-2xa100", "model-execution-20261009-method-parabricks", "Parabricks germline v4.3.0 (GeNePi PB_germ) on 2 A100 GPUs (Marangoni et al. 2026)",
     "One Intel RX2540 M6 CPU, 48 cores, 395 GB RAM, two NVIDIA A100-PCIE-40GB (Supplementary S3.1)",
     "GeNePi PB_germ module: Parabricks germline pipeline v4.3.0", "v4.3.0", "author_reported"),
    ("GPU-4xA100", "parabricks-4-3-0-4xa100", "model-execution-20261009-method-parabricks", "Parabricks germline v4.3.0 (GeNePi PB_germ) on 4 A100 GPUs (Marangoni et al. 2026)",
     "Two AMD GX2460 M1 CPUs, 64 cores, four NVIDIA A100-PCIE-40GB (Supplementary S3.1)",
     "GeNePi PB_germ module: Parabricks germline pipeline v4.3.0", "v4.3.0", "author_reported"),
]
DID = P + "data-marangoni2026-wgs-depths"
PID = P + "protocol-marangoni2026-germline-runtime-by-depth"
LIM = [
    "Author-reported for the GPU rows: the authors built GeNePi, whose PB_germ module wraps Parabricks; no competing interests declared.",
    "The input sample is not named for Table S1; the depths (30x to 100x) are average read depths of human WGS data.",
    "One value per depth and hardware configuration is printed; the number of runs behind it is not stated and no spread is printed.",
    "Hardware differs between columns (different CPUs, RAM and GPU counts), so differences mix software and hardware.",
    "CPU runtimes are printed in whole hours.",
    "Accuracy of the calls is reported separately (synthetic and HG002 data), not beside runtime.",
    "Several numbers in the article's running text are missing from the XML (rendered as blank formulae), so the text cannot be checked against Table S1.",
    "The article states a 10- to 78-fold average acceleration over CPU (Discussion, citing Figure 2 and Supplementary Figure S11); the Table S1 ratios run from about 10 to 34, so the upper figure comes from runs not in Table S1.",
]
records += [
    entity(DID, "dataset", "Human WGS paired-end data at 30x, 40x, 50x, 60x and 100x average depth (Marangoni et al. 2026 Table S1)",
           "Input reads for the GeNePi PB_germ runtime benchmark.", SOURCES,
           {"population": "Human WGS at five average depths", "split": "One value per depth; number of runs not stated",
            "source_locator": "Supplementary S3.2 'PB germ Benchmark and CPU equivalent workflow'; Table S1",
            "missing_metadata": {"accession": {"reason": "unreported", "note": "Sample not named for Table S1"}, "version": {"reason": "unreported"}}},
           facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"]}),
    entity(PID, "protocol", "Germline FASTQ-to-VCF runtime by read depth, Parabricks v4.3.0 on V100 and A100 GPUs versus the CPU GATK equivalent (Marangoni et al. 2026 Table S1)",
           "Execution time of the GeNePi PB_germ module and its CPU equivalent at five depths.", SOURCES,
           {"protocol": "Parabricks germline pipeline v4.3.0 (alignment to GRCh38 through HaplotypeCaller) in the GeNePi PB_germ module, and the CPU-equivalent BWA-MEM plus GATK pipeline, run on HPC nodes; execution time per run.",
            "version": "Supplementary Table S1", "metric": "runtime", "limitations": LIM,
            "source_locator": "Supplementary S3.1-S3.2; Table S1"},
           [("uses_data", DID)], facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"]}),
]

m = re.search(r"Table S1\. Comparison of the execution time.*?\n(.*?)\n\s*8\s+Supporting Information", text, re.S)
assert m
body = m.group(1)
assert re.search(r"Avg\. Reads Depth\s+CPU\s+GPU-2xV100\s+GPU-2xA100\s+GPU-4xA100", body)
rows = re.findall(r"^\s*(\d+x)\s+(\d+h)\s+(\d+h \d+m)\s+(\d+h \d+m|\d+ m)\s+(\d+h \d+m|\d+m)\s*$", body, re.M)
assert [r[0] for r in rows] == ["30x", "40x", "50x", "60x", "100x"], rows

def minutes(s):
    h = re.search(r"(\d+)h", s)
    mm = re.search(r"(\d+) ?m", s)
    return str((int(h.group(1)) * 60 if h else 0) + (int(mm.group(1)) if mm else 0))

REV = extraction_review(["pdf-text-parse"],
    "Deterministic parse of `pdftotext -layout` text of the pinned supplementary PDF (extract/build.py), with the column header and five depth rows asserted; numeric_value converts the printed hours and minutes to minutes.",
    "Extraction only; pending independent review.")
for col_index, (col, key, method, name, hw, proto, version, origin) in enumerate(CFGS):
    cid = f"{P}config-marangoni2026-{key}"
    attrs = {"reported_name": col, "foundation_model_eligible": False, "hardware": {"description": hw}, "protocol": proto,
             "access_reuse": "GeNePi is open source; Parabricks is NVIDIA software", "source_locator": "Supplementary S3.1-S3.2; Table S1 column '" + col + "'"}
    if version:
        attrs["version"] = version
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "GATK and BWA versions not stated for the CPU equivalent"}}
    records.append(entity(cid, "configuration", name, proto, SOURCES, attrs, [("configuration_of", method)], facets=FAC))
    eid = f"{P}eval-marangoni2026-{key}"
    records.append(entity(eid, "evaluation", name.replace(" (Marangoni", ", runtime by depth (Marangoni"),
                          "Published pipeline execution benchmark; transcribed, not reproduced.", SOURCES,
                          {"origin": origin, "protocol": PID, "version": "Primary source as retrieved 2026-10-11",
                           "comparison": {"protocol_id": PID, "dataset_version": None, "split": "Five average depths, one value each; number of runs not stated",
                                          "population": "Human WGS at 30x to 100x", "inputs": "Paired-end FASTQ", "adaptation": None,
                                          "metric_implementation": None, "aggregation": "One value per depth",
                                          "budget": "Number of runs not stated; no fixed hardware budget, hardware is part of each configuration"},
                           "source_locator": f"Supplementary Table S1 column '{col}'",
                           "missing_metadata": {"comparison.dataset_version": {"reason": "unreported"},
                                                "comparison.metric_implementation": {"reason": "unreported", "note": "How execution time was measured is not stated"}}},
                          [("system", cid), ("assessment", PID), ("data", DID)], facets={"areas": ["dna-genomes"], "contexts": ["clinical_research"]}))
    for row in rows:
        depth, printed = row[0], row[1 + col_index]
        rid = f"{P}result-marangoni2026-{key}-{depth}-runtime"
        loc = f"Supplementary Table S1 (page 7), row 'Avg. Reads Depth' {depth}, column '{col}'"
        records.append(result(rid, f"marangoni2026 {col} {depth} runtime", SOURCES, eid, "runtime", "lower", "minute", printed, minutes(printed),
                              loc, REV, qualifier=f"Germline FASTQ to VCF; human WGS at {depth} average depth",
                              unit_detail="printed as hours and minutes; numeric_value in minutes"))
        claims.append((rid, SUPP, loc, printed, "pdf-text-layer"))

records.append(judgement("use-case-mapping-model-execution-20261011-marangoni2026-germline-runtime-by-depth", PID,
    "Germline runtime by read depth, Parabricks on V100 and A100 versus CPU GATK (Marangoni et al. 2026)", SOURCES, "direct",
    "FASTQ-to-VCF germline runtime of Parabricks v4.3.0 on 2 V100, 2 A100 and 4 A100 GPU nodes and of the CPU GATK equivalent at 30x, 40x, 50x, 60x and 100x WGS",
    "Directly measures how per-genome germline runtime scales with read depth for CPU and three GPU set-ups on stated HPC hardware, built by a regional genomics centre for routine WGS, which matches the resource and throughput part of the question. Limits: one unnamed sample per depth, an unstated number of runs per value and author-reported GPU rows.",
    ["Inspect every linked evaluation's source locator before citing a result.",
     "Do not combine this mapping's evaluations with any other protocol's results; hardware, inputs, software versions and timing boundaries differ between sources."],
    LIM, [{"source_id": SUPP, "locator": "Supplementary S3.1-S3.2; Table S1"}, {"source_id": SRC, "locator": "Results 'Benchmarking'; Figure 2; Competing interest"}],
    "marangoni2026-depth", "Parabricks on V100 and A100 versus CPU GATK by read depth (Marangoni et al. 2026)", None, None, "runtime"))

n = write(BATCH, records, claims)
print(n, "records;", sum(r["kind"] == "result" for r in records), "results")
