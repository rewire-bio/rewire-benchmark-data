"""Deterministic extraction of germline pipeline execution benchmarks (runtime, cost, speedup) into a records batch.

Usage: python3 -I extract_model_execution.py <pinned-dir> <batch-dir>

<pinned-dir> holds the pinned artifacts under the names in ARTIFACTS. The script checks each SHA-256,
reads the tables, asserts every row and column label it depends on, and writes batch.jsonl and claims.csv
in the current store shape. Supplementary PDF text is read with `pdftotext -layout` (poppler); its version
is printed. Nothing is marked reviewed.
"""
import csv, hashlib, json, os, re, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
P = "model-execution-20261009"
UC = "use-case-diagnostic-genomics-model-execution"
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
TODAY = "2026-10-09"
ARTIFACTS = {
    "samarakoon2025-article.xml": "07e69d06f103dffdc5183eaf63e3e6ca84838c9209117a42fb6b1f96982e43c4",
    "samarakoon2025-supplementary-data.zip": "a828608e459ec1fe57828e9b4fbce228e9507b8686eecedac323f45fd4c3cc07",
    "oconnell2023-article.xml": "1d9c27beb3780a153bc6d80817bf098539e5c605107da0e88f34d6e0d56f3e4f",
}
SUPP_PDF = "Publication-ready_Supplementary materials-20250404.pdf"
SUPP_PDF_SHA = "5fbee07d1a14336e909daf2c6fdd3b26af4c252fae135c033a84c596b2a5d7db"
records, claims_rows, judgements = [], [], []


def sha256(data):
    return hashlib.sha256(data).hexdigest()


for name, digest in ARTIFACTS.items():
    got = sha256(open(os.path.join(DL, name), "rb").read())
    assert got == digest, f"{name}: {got} != pinned {digest}"


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,254}", id_), id_
    assert len(name) <= 500, name
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def decimal_of(text):
    """Numeric value of a printed number: thousands separators and spaces removed, Unicode minus read as '-'."""
    t = text.replace("−", "-").replace(" ", "").replace(",", "")
    assert re.fullmatch(r"-?\d+(\.\d+)?", t), text
    return format(Decimal(t), "f")


def review_note(how):
    return {"method": ["deterministic-table-parse"], "reviewer": ["claude"],
            "reviewer_note": "Extracting Claude (Opus 5.5) research agent; not a review. No human review claimed.",
            "date": TODAY, "note": f"{how} Pending independent review."}


METRIC = {
    "runtime-min": dict(metric="runtime", metric_direction="lower", unit="minute"),
    "runtime-h": dict(metric="runtime", metric_direction="lower", unit="hour"),
    "cost": dict(metric="compute-cost", metric_direction="lower", unit="us-dollar"),
    "speedup": dict(metric="speedup", metric_direction="higher", unit="unitless"),
    "saving": dict(metric="cost-saving", metric_direction="higher", unit="percent"),
}


def result(id_, eval_id, source_ids, artifact_sha, url, locator, printed, metric, qualifier, how, extra=None):
    attrs = {**METRIC[metric], "metric_qualifier": qualifier, "printed_value": printed,
             "numeric_value": decimal_of(printed), "source_locator": locator,
             "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Single recorded run per cell; no repeats or intervals printed"}},
             "review": {**review_note(how), "artifact_sha256": artifact_sha, "retrieval_url": url}}
    if extra:
        attrs.update(extra)
    rec(id_, "result", f"{eval_id.removeprefix(P + '-eval-')} {METRIC[metric]['metric']} ({qualifier})"[:500],
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
    rec(id_, "evaluation", name, "Published pipeline execution benchmark; transcribed, not reproduced.", source_ids,
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
             "source_locator": "Methods and table labels of the cited sources",
             "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}
    if extra:
        attrs.update(extra)
    METHODS[mid] = rec(mid, "method", name, description, list(source_ids), [], attrs,
                       facets={**FACETS, "method_types": method_types})
    return mid


DRAGEN_METHOD = "cnv-20261009-method-dragen"  # existing record, reused


def config(cid, name, description, source_ids, method_id, attrs, method_types=("conventional_pipeline",)):
    links = [{"relation": "configuration_of", "target_id": method_id}] if method_id else []
    rec(cid, "configuration", name, description, source_ids, links,
        {"foundation_model_eligible": False, **attrs}, facets={**FACETS, "method_types": list(method_types)})
    return cid


def judgement(short, protocol, protocol_name, source_ids, relevance, endpoint, rationale, constraints, limitations,
              locators, group, title, headline, stratum=None, order=None):
    cid = f"use-case-mapping-{P}-{short}"
    attrs = {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance,
             "endpoint": endpoint, "rationale": rationale, "constraints": constraints, "limitations": limitations,
             "revision": 1,
             "reason": "Add primary-source execution benchmark evidence from the diagnostic genomics execution use-case pass (2026-10-09).",
             "citation_locators": [{"source_id": s, "locator": l} for s, l in locators],
             "source_locator": "; ".join(f"{s}: {l}" for s, l in locators),
             "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum is not None:
        attrs["stratum_label"] = stratum
        attrs["stratum_order"] = order
    rec(cid, "claim", f"Relevance of {protocol_name} to \"Select an execution workflow for large-scale diagnostic genomics\"",
        rationale, source_ids, [{"relation": "subject", "target_id": UC}], attrs, facets={})
    judgements.append(cid)


CONSTRAINTS = ["Inspect every linked evaluation's source locator before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; hardware, inputs, software versions and timing boundaries differ between sources."]

# =============================================================================================
# A. Samarakoon et al. 2025, Bioinformatics Advances 5:vbaf085, Supplementary Tables S3 and S4
# =============================================================================================
A_ART, A_SUP = f"{P}-source-samarakoon2025", f"{P}-source-samarakoon2025-supplement"
A_SRC = [A_ART, A_SUP]
A_ART_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12092081/fullTextXML"
A_SUP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12092081/supplementaryFiles"
SUPP_NOTE = ("Retrieved inside the Europe PMC supplementaryFiles zip, which is assembled per request; the publisher's "
             "inner zip and the PDF it holds are pinned.")
rec(A_ART, "source", "Benchmarking accelerated next-generation sequencing analysis pipelines",
    "Primary source retrieved and hashed for the diagnostic genomics execution use-case pass.", [], [],
    {"url": "https://doi.org/10.1093/bioadv/vbaf085", "artifact_url": A_ART_URL,
     "version": "Bioinformatics Advances 5(1):vbaf085, published 2025-05-15; PMC12092081 full-text XML",
     "retrieved_at": "2026-10-09T20:20:45Z", "artifact_sha256": ARTIFACTS["samarakoon2025-article.xml"],
     "doi": "10.1093/bioadv/vbaf085", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/xml"})
rec(A_SUP, "source", "Samarakoon et al. 2025, supplementary materials (Tables S1-S4, supplementary texts)",
    "Supplementary PDF with per-sample runtimes for CPU-only, Parabricks and DRAGEN pipelines.", [], [],
    {"url": "https://doi.org/10.1093/bioadv/vbaf085", "artifact_url": A_SUP_URL,
     "version": f"'{SUPP_PDF}' inside vbaf085_supplementary_data.zip",
     "retrieved_at": "2026-10-09T20:25:01Z", "artifact_sha256": SUPP_PDF_SHA, "artifact_member": SUPP_PDF,
     "hash_scope": (f"SHA-256 of the PDF. The publisher zip vbaf085_supplementary_data.zip that contains it has SHA-256 "
                    f"{ARTIFACTS['samarakoon2025-supplementary-data.zip']}. " + SUPP_NOTE),
     "doi": "10.1093/bioadv/vbaf085", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/pdf"})

z = zipfile.ZipFile(os.path.join(DL, "samarakoon2025-supplementary-data.zip"))
assert z.namelist() == [SUPP_PDF], z.namelist()
pdf = z.read(SUPP_PDF)
assert sha256(pdf) == SUPP_PDF_SHA
pdf_path = os.path.join(BATCH, ".supp.pdf")
os.makedirs(BATCH, exist_ok=True)
open(pdf_path, "wb").write(pdf)
version = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr.splitlines()[0]
print(version)
text = subprocess.run(["pdftotext", "-layout", pdf_path, "-"], capture_output=True, text=True, check=True).stdout
os.remove(pdf_path)
lines = [l.replace("\f", "").rstrip() for l in text.split("\n")]  # splitlines() would also split at form feeds
A_HOW = (f"Extracted by deterministic parse of the pinned supplementary PDF text layer ({version}, -layout) in "
         "extract/extract_model_execution.py, with table titles, sub-table headings, column headers and sample labels "
         "asserted. printed_value is the number as printed.")


def find(label, start=0):
    for i in range(start, len(lines)):
        if lines[i].strip() == label:
            return i
    raise AssertionError(f"missing line: {label}")


SAMPLES = ["NA12812", "NA12778", "NA12843", "NA12829", "NA12890", "NA12891", "NA12878", "NA12877", "NA12892", "NA12889"]
COV = {"NA12878": "47.55", "NA12891": "47.09", "NA12892": "50.50", "NA12877": "49.88", "NA12889": "52.80",
       "NA12890": "42.58", "NA12778": "9.82", "NA12812": "9.35", "NA12829": "13.63", "NA12843": "10.14"}
t1 = find("Supplementary Table S1: Benchmark datasets used in the study")
for s, c in COV.items():
    row = next(l for l in lines[t1:t1 + 30] if l.split()[:1] == [s])
    assert row.split()[1] == c, (s, row)
COLS = ["CPU", "L4", "A100", "H100", "DRAGEN"]
s3 = find("Supplementary Table S3: Runtime performance metrics")
SUBTABLES = [
    ("a) Read mapping", "mapping", "read mapping stage", "Read mapping", "Read mapping and alignment refinement", SAMPLES),
    ("b.1) Variant calling via HC or DRAGEN GSVC", "hc", "HaplotypeCaller or DRAGEN GSVC calling stage", "HaplotypeCaller or GSVC calling", "Variant calling with GATK or Parabricks HaplotypeCaller, or DRAGEN GSVC", SAMPLES),
    ("b.2). Variant calling via DV", "dv", "DeepVariant calling stage", "DeepVariant calling", "Variant calling with DeepVariant (CPU or Parabricks); not run on DRAGEN", SAMPLES),
    ("c.) Total processing time: Read mapping & HC or DRAGEN GSVC", "total", "total of read mapping and HaplotypeCaller or DRAGEN GSVC", "Mapping plus HaplotypeCaller or GSVC", "Read mapping plus HaplotypeCaller or DRAGEN GSVC, summed by the authors", sorted(SAMPLES)),
]
caption = ("Processing times (minutes) for 10 WGS samples across pipeline stages: (a) read")
assert any(l.startswith(caption) for l in lines[s3:s3 + 70]), "S3 caption"

adid = f"{P}-data-samarakoon2025-wgs-10"
rec(adid, "dataset", "Ten WGS samples: six Illumina Platinum pedigree high-coverage and four 1000 Genomes phase 3 low-coverage",
    "Input FASTQ used for the runtime benchmark in Samarakoon et al. 2025.", A_SRC, [],
    {"population": "; ".join(f"{s} {COV[s]}x" for s in SAMPLES),
     "assay": "Illumina paired-end WGS FASTQ (Platinum pedigree CEPH; 1000 Genomes phase 3 low coverage); GRCh38 no-alt analysis set reference",
     "split": "All ten samples; one run per sample and configuration",
     "source_locator": "Supplementary Table S1; Methods 2.1",
     "missing_metadata": {"version": {"reason": "unreported", "note": "Download date or release of each FASTQ is not stated"}}})

A_HW = {
    "CPU": ("cpu-epyc7702", "CPU-only best-practice pipeline on AMD EPYC 7702 (UiO HPC)",
            "BWA, SAMtools and GATK release 4.0.3.0 (MarkDuplicates, BaseRecalibrator, ApplyBQSR, HaplotypeCaller) or DeepVariant; parameters from nf-core/sarek",
            "AMD EPYC 7702 (64 cores), 128-256 GB RAM, GPFS storage, Fox HPC cluster at the University of Oslo, nodes not exclusive", "gatk-cpu"),
    "L4": ("parabricks-4xl4", "NVIDIA Parabricks on 4 NVIDIA L4 GPUs (GCP G2)",
           "Parabricks fq2bam, ApplyBQSR, HaplotypeCaller or DeepVariant", "4 NVIDIA L4 (24 GB, 96 GB GPU memory in total), 192 GB RAM, GPFS, Google Cloud G2 VM, no NVLink; host CPU per GPU type not stated (Table S2 lists AMD EPYC 7702 for the Parabricks pipeline)", "parabricks"),
    "A100": ("parabricks-4xa100", "NVIDIA Parabricks on 4 NVIDIA A100 GPUs (UiO HPC)",
             "Parabricks fq2bam, ApplyBQSR, HaplotypeCaller or DeepVariant", "4 NVIDIA A100 (40 GB), AMD EPYC 7702, 412 GB RAM, GPFS, UiO HPC node, no NVLink", "parabricks"),
    "H100": ("parabricks-8xh100", "NVIDIA Parabricks on 8 NVIDIA H100 GPUs (GCP A3)",
             "Parabricks fq2bam, ApplyBQSR, HaplotypeCaller or DeepVariant", "8 NVIDIA H100 (80 GB, 640 GB GPU memory in total), 1,872 GB RAM, GPFS, Google Cloud A3 VM, NVLink; host CPU per GPU type not stated", "parabricks"),
    "DRAGEN": ("dragen42-server-v2", "Illumina DRAGEN v4.2 on DRAGEN server V2",
               "DRAGEN mapping, DRAGStr calibration and Germline Small Variant Caller (GSVC)", "2 Intel Xeon Gold 6126 (48 threads), 256 GB RAM, local NVMe SSD, CentOS 7", None),
}
PB_VERSION_NOTE = ("Methods 2.3 states Parabricks version 4.3.0-1; Supplementary Table S4 calls 4.1.0-1 'the version "
                   "implemented in our Parabricks pipeline', and its 4.1.0-1 values equal the Table S3 b.2 H100 values.")
A_CONF = {}
for col, (key, name, software, hw, mkey) in A_HW.items():
    cid = f"{P}-config-samarakoon2025-{key}"
    attrs = {"reported_name": col, "protocol": software, "hardware": {"description": hw},
             "source_locator": "Supplementary Table S2; Methods 2.2-2.5; Table S3 column header"}
    if col == "CPU":
        mid = method("gatk-best-practices-cpu", "GATK best-practice germline pipeline (CPU)",
                     "CPU workflow of BWA alignment, GATK duplicate marking, base recalibration and HaplotypeCaller, with DeepVariant as an alternative caller.",
                     "CPU-only pipeline", ["conventional_pipeline"], [A_ART])
        attrs["version"] = "GATK release 4.0.3.0"
        attrs["missing_metadata"] = {"packages": {"reason": "unreported", "note": "BWA, SAMtools and DeepVariant versions are not stated"}}
    elif mkey == "parabricks":
        mid = method("parabricks", "NVIDIA Parabricks", "GPU-accelerated implementations of alignment, GATK steps and variant callers.",
                     "Parabricks", ["conventional_pipeline"], [A_ART])
        attrs["missing_metadata"] = {"version": {"reason": "conflicting", "note": PB_VERSION_NOTE}}
    else:
        mid = DRAGEN_METHOD
        attrs["version"] = "DRAGEN software v4.2"
    A_CONF[col] = config(cid, f"{name} (Samarakoon et al. 2025)", f"{col} column of Supplementary Table S3.", A_SRC, mid, attrs)

a_order = 0
for heading, skey, stage, stratum, protocol_text, order in SUBTABLES:
    a_order += 1
    h = find(heading, s3)
    assert lines[h + 1].split() == ["Sample"] + COLS, (heading, lines[h + 1])
    pid = f"{P}-protocol-samarakoon2025-{skey}"
    lims = ["One run per sample and configuration; no repeats or variance printed.",
            "Hardware differs between columns (CPU cluster, two GCP VMs, an HPC GPU node and a DRAGEN server), so differences mix software and hardware.",
            "CPU-only nodes were shared with other users; GCP VMs ran in a multi-tenant environment (Table S2 notes)."]
    if skey == "dv":
        lims.append("DRAGEN has no DeepVariant stage; its column prints NA and has no evaluation.")
    if skey == "total":
        lims.append("Total is the sum of read mapping and HaplotypeCaller or GSVC stages; DeepVariant is excluded. The NA12778 L4 total (117.59) does not equal its stage values (26.02 + 5.92).")
    if skey == "mapping":
        lims.append("DRAGEN mapping time was assembled from three process logs because its processes run concurrently (Methods 2.4).")
    rec(pid, "protocol", f"WGS germline pipeline wall-clock, {stage} (Samarakoon et al. 2025 Table S3{heading[:3].strip(').')})",
        f"Wall-clock minutes for the {stage} on ten WGS samples, CPU-only versus Parabricks on three GPU types versus DRAGEN.",
        A_SRC, [{"relation": "uses_data", "target_id": adid}],
        {"protocol": f"{protocol_text}. Real (wall-clock) time measured per stage from FASTQ input (Methods 2.6).",
         "version": f"Supplementary Table S3 sub-table '{heading}'", "unit": "minute", "metric": "runtime",
         "limitations": lims, "denominator": 10,
         "missing_metadata": {"replicates": {"reason": "unreported"}},
         "source_locator": f"Supplementary Table S3, sub-table '{heading}'"})
    for j, s in enumerate(order):
        row = lines[h + 2 + j].split()
        assert row and row[0] == s and len(row) == 6, (heading, j, lines[h + 2 + j])
    for col_i, col in enumerate(COLS):
        cells = [lines[h + 2 + j].split()[1 + col_i] for j in range(len(order))]
        if all(c == "NA" for c in cells):
            assert skey == "dv" and col == "DRAGEN"
            continue
        eid = f"{P}-eval-samarakoon2025-{A_HW[col][0]}-{skey}"
        evaluation(eid, f"{A_HW[col][1]}, {stage} (Samarakoon et al. 2025)", A_CONF[col], pid, adid, A_SRC,
                   "independent_paper",
                   {"dataset_version": None, "split": "Ten WGS samples", "population": "10 samples, 9.35x to 52.80x",
                    "inputs": "Paired-end WGS FASTQ, GRCh38", "adaptation": None,
                    "metric_implementation": "Wall-clock time per stage (Methods 2.6)",
                    "aggregation": "One value per sample", "budget": A_HW[col][3]},
                   f"Supplementary Table S3 '{heading}', column '{col}'",
                   missing={"comparison.dataset_version": {"reason": "unreported"}})
        for j, s in enumerate(order):
            v = cells[j]
            extra = None
            if skey == "total" and col == "L4" and s == "NA12778":
                extra = {"source_discrepancy": "Printed total 117.59 does not equal the printed stage values for NA12778 on L4 (mapping 26.02 plus HaplotypeCaller 5.92 = 31.94); every other total in the table equals its stage sum. Value kept as printed."}
            result(f"{P}-result-samarakoon2025-{A_HW[col][0]}-{skey}-{s.lower()}", eid, A_SRC, SUPP_PDF_SHA, A_SUP_URL,
                   f"Supplementary Table S3 '{heading}', row '{s}', column '{col}' (PDF page text)",
                   v, "runtime-min", f"{stage}; sample {s} ({COV[s]}x)", A_HOW, extra)
    judgement(f"samarakoon2025-{skey}", pid, f"WGS pipeline wall-clock, {stage} (Samarakoon et al. 2025)", A_SRC, "direct",
              f"Wall-clock minutes for the {stage} on ten WGS samples for "
              + ("CPU-only GATK, Parabricks on L4, A100 and H100 GPUs, and DRAGEN v4.2" if skey != "dv" else "CPU-only DeepVariant and Parabricks DeepVariant on L4, A100 and H100 GPUs"),
              ("Directly measures the runtime of complete germline WGS pipeline stages on the same input across CPU, GPU and "
               "FPGA execution set-ups, the resource and throughput endpoint of the use case; run by a group that did not develop "
               "either accelerated platform."),
              CONSTRAINTS, lims, [(A_SUP, f"Supplementary Table S3 '{heading}'"), (A_ART, "Methods 2.1-2.6; Results 3.1")],
              "samarakoon2025-wgs-stages", "WGS germline pipeline stages on CPU, GPU and DRAGEN (Samarakoon et al. 2025)",
              "runtime", stratum=stratum, order=a_order)

# Table S4: Parabricks DeepVariant version comparison on H100
s4 = find("Supplementary Table S4: Parabricks DV v4.1.0-1 vs v4.3.0-1 on H100")
hdr = next(i for i in range(s4, s4 + 20) if lines[i].split() == ["Sample", "ID", "DV.v4.1.0-1", "DV.v4.3.0-1"])
S4_ROWS = ["NA12878", "NA12890", "NA12892"]
pid4 = f"{P}-protocol-samarakoon2025-dv-version-h100"
lims4 = ["Three high-coverage samples, one run each.", "Version 4.3.0-1 was slower on all three samples; the authors do not give a cause."]
rec(pid4, "protocol", "Parabricks DeepVariant v4.1.0-1 versus v4.3.0-1 on 8 H100 GPUs (Samarakoon et al. 2025 Table S4)",
    "Wall-clock minutes for Parabricks DeepVariant under two software versions on the same hardware and samples.", A_SRC,
    [{"relation": "uses_data", "target_id": adid}],
    {"protocol": "Parabricks DeepVariant run on 8 H100 GPUs (GCP A3) with version 4.1.0-1 and version 4.3.0-1 on three samples.",
     "version": "Supplementary Table S4", "unit": "minute", "metric": "runtime", "denominator": 3, "limitations": lims4,
     "source_locator": "Supplementary Table S4"})
cid43 = config(f"{P}-config-samarakoon2025-parabricks-4-3-0-1-8xh100", "NVIDIA Parabricks DeepVariant v4.3.0-1 on 8 H100 GPUs (Samarakoon et al. 2025)",
               "DV.v4.3.0-1 column of Supplementary Table S4.", A_SRC, f"{P}-method-parabricks",
               {"reported_name": "Parabricks DV.v4.3.0-1", "version": "4.3.0-1", "protocol": "Parabricks DeepVariant",
                "hardware": {"description": A_HW["H100"][3]}, "source_locator": "Supplementary Table S4 column header"})
for col_i, (label, cid, ckey) in enumerate([("DV.v4.1.0-1", A_CONF["H100"], "parabricks-8xh100"),
                                            ("DV.v4.3.0-1", cid43, "parabricks-4-3-0-1-8xh100")]):
    eid = f"{P}-eval-samarakoon2025-{ckey}-dv-version"
    evaluation(eid, f"Parabricks {label} on 8 H100 GPUs (Samarakoon et al. 2025 Table S4)", cid, pid4, adid, A_SRC,
               "independent_paper",
               {"dataset_version": None, "split": "Three samples", "population": "NA12878, NA12890, NA12892",
                "inputs": "Paired-end WGS FASTQ, GRCh38", "adaptation": None,
                "metric_implementation": "Wall-clock time of the DeepVariant stage", "aggregation": "One value per sample",
                "budget": A_HW["H100"][3]},
               f"Supplementary Table S4, column 'Parabricks {label}'", missing={"comparison.dataset_version": {"reason": "unreported"}})
    for j, s in enumerate(S4_ROWS):
        row = lines[hdr + 1 + j].split()
        assert row[0] == s and len(row) == 3, row
        result(f"{P}-result-samarakoon2025-{ckey}-dv-version-{s.lower()}", eid, A_SRC, SUPP_PDF_SHA, A_SUP_URL,
               f"Supplementary Table S4, row '{s}', column 'Parabricks {label}' (PDF page text)",
               row[1 + col_i], "runtime-min", f"DeepVariant calling stage; sample {s} ({COV[s]}x)", A_HOW)
judgement("samarakoon2025-dv-version-h100", pid4, "Parabricks DeepVariant version comparison on H100 (Samarakoon et al. 2025)",
          A_SRC, "direct", "Wall-clock minutes for Parabricks DeepVariant v4.1.0-1 and v4.3.0-1 on the same 8 H100 GPUs and three samples",
          "Directly measures how a software version change alone alters runtime on fixed hardware and input, a reproducibility and planning concern for execution workflows.",
          CONSTRAINTS, lims4, [(A_SUP, "Supplementary Table S4")], "samarakoon2025-dv-version",
          "Parabricks DeepVariant version change on fixed hardware (Samarakoon et al. 2025)", "runtime")

# descriptive claims
A_COST_LOC = "Supplementary Text 03, Table 2 'Cost comparison summary'"
t3 = find("Supplementary Text 03. Table 2: Cost comparison summary")
assert any("4.01 USD" in l for l in lines[t3:t3 + 12]) and any("48.77" in l for l in lines[t3:t3 + 12])
assert any("642 USD" in l for l in lines[t3:t3 + 25]) and any("12 000 USD" in l for l in lines[t3:t3 + 30])
rec(f"{P}-claim-samarakoon2025-cost-summary", "claim", "cost_estimate: Samarakoon et al. 2025 execution set-ups",
    "Descriptive fact transcribed from the pinned source.", [A_SUP], [{"relation": "subject", "target_id": f"{P}-protocol-samarakoon2025-total"}],
    {"field": "cost_estimate",
     "value": ("Authors' estimates, not per-run measurements: a GCP VM with four L4 GPUs costs 4.01 USD per hour and a GCP spot VM with eight H100 GPUs 48.77 USD per hour; "
               "Parabricks on HPC A100 GPUs is estimated at 31,200 USD per GPU with 5-year maintenance and 642 USD per 100,000 gigabases; "
               "a DRAGEN server is about 90,000 USD with 3 years of support plus a Level-1 annual licence of 12,000 USD for 100,000 gigabases. Disk costs are excluded."),
     "source_locator": A_COST_LOC, "review": review_note("Hand transcription from the supplementary PDF text layer.")}, facets={})
claims_rows.append([f"{P}-claim-samarakoon2025-cost-summary", A_SUP, A_COST_LOC, "4.01 USD/h; 48.77 USD/h; 642 USD per 100,000 GB; ~90,000 USD + 12,000 USD", "claim"])
rec(f"{P}-claim-samarakoon2025-parabricks-version", "claim", "version: Parabricks configurations (Samarakoon et al. 2025)",
    "Descriptive fact transcribed from the pinned source.", A_SRC, [{"relation": "subject", "target_id": A_CONF["H100"]}],
    {"field": "version", "value": PB_VERSION_NOTE, "source_locator": "Methods 2.3; Supplementary Table S4 introduction and rows",
     "review": review_note("Hand transcription from the article XML and supplementary PDF text.")}, facets={})
claims_rows.append([f"{P}-claim-samarakoon2025-parabricks-version", A_SUP, "Methods 2.3; Supplementary Table S4", "4.3.0-1 (Methods) versus 4.1.0-1 (Table S4)", "claim"])

# =============================================================================================
# B. O'Connell et al. 2023, BMC Bioinformatics 24:221, Table 1
# =============================================================================================
B_ART = f"{P}-source-oconnell2023"
B_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10230726/fullTextXML"
B_SHA = ARTIFACTS["oconnell2023-article.xml"]
rec(B_ART, "source", "Accelerating genomic workflows using NVIDIA Parabricks",
    "Primary source retrieved and hashed for the diagnostic genomics execution use-case pass.", [], [],
    {"url": "https://doi.org/10.1186/s12859-023-05292-2", "artifact_url": B_URL,
     "version": "BMC Bioinformatics 24:221, published 2023-05-31; PMC10230726 full-text XML",
     "retrieved_at": "2026-10-09T20:20:46Z", "artifact_sha256": B_SHA, "doi": "10.1186/s12859-023-05292-2",
     "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml"})
B_HOW = ("Extracted by deterministic parse of Table 1 (table-wrap Tab1) in the pinned article XML "
         "(extract/extract_model_execution.py), with the header, platform, pipeline, VM-type and variant-caller labels asserted; "
         "blank Platform and Variant-caller cells inherit the row above, as the table layout shows. printed_value is the cell text.")
art = ET.parse(os.path.join(DL, "oconnell2023-article.xml"))
tx = lambda e: " ".join(" ".join(e.itertext()).split())
tab = next(t for t in art.iter("table-wrap") if t.get("id") == "Tab1")
assert tx(tab.find("caption")) == "Results of benchmarking for AWS, GCP and NVIDIA DGX workflow runs"
foot = tx(tab.find("table-wrap-foot"))
assert foot == ("AWS results presented here are for the p3 family with the NVIDIA Tesla V100 GPU, results for the p4 family "
                "with the A100 GPU are shown in Additional file 1 : Table S1"), foot
rows = [[tx(c) for c in tr if c.tag in ("td", "th")] for tr in tab.iter("tr")]
HEAD = ["Platform", "Pipeline", "VM-type", "Variant-caller", "Time (min)", "Time (h)", "Cost ($)", "Fold acceleration", "% cost-savings"]
assert rows[0] == HEAD, rows[0]
body = rows[1:]
assert len(body) == 66, len(body)
CALLERS = ["DeepVariant", "HaplotypeCaller", "LoFreq", "Muse", "Mutect2", "SomaticSniper"]
VM_SEQ = ["C6i.8xlarge", "GPU2", "GPU4", "GPU8", None, "GPU2", "GPU4", "GPU8", "GPU2", "GPU4", "GPU8"]
PLAT_SEQ = ["AWS", "", "", "", "GCP", "", "", "", "DGX", "", ""]
B_CONF_SPEC = [
    ("aws-c6i-8xlarge", "CPU tools on AWS c6i.8xlarge", "AWS c6i.8xlarge: Intel Xeon Ice Lake 8375C, 32 vCPUs, 64 GiB RAM, 800 GB EBS", None),
    ("aws-gpu2", "Parabricks 3.7.0-1, 2 GPUs on AWS", "AWS GPU machine, 2 GPUs (Table 1 footnote: p3 family, NVIDIA Tesla V100)", "parabricks"),
    ("aws-gpu4", "Parabricks 3.7.0-1, 4 GPUs on AWS", "AWS GPU machine, 4 GPUs (Table 1 footnote: p3 family, NVIDIA Tesla V100)", "parabricks"),
    ("aws-gpu8", "Parabricks 3.7.0-1, 8 GPUs on AWS", "AWS GPU machine, 8 GPUs (Table 1 footnote: p3 family, NVIDIA Tesla V100)", "parabricks"),
    ("gcp-n2-standard-32", "CPU tools on GCP n2-standard-32", "GCP n2-standard-32: Intel Xeon Cascade Lake, 32 vCPUs, 128 GB RAM", None),
    ("gcp-a2-gpu2", "Parabricks 3.7.0-1, 2 A100 GPUs on GCP a2-highgpu", "GCP a2-highgpu: 2 NVIDIA A100, 24 vCPUs, 170 GB RAM", "parabricks"),
    ("gcp-a2-gpu4", "Parabricks 3.7.0-1, 4 A100 GPUs on GCP a2-highgpu", "GCP a2-highgpu: 4 NVIDIA A100, 48 vCPUs, 340 GB RAM", "parabricks"),
    ("gcp-a2-gpu8", "Parabricks 3.7.0-1, 8 A100 GPUs on GCP a2-highgpu", "GCP a2-highgpu: 8 NVIDIA A100, 96 vCPUs, 680 GB RAM", "parabricks"),
    ("dgx-gpu2", "Parabricks 3.7.0-1, 2 A100 GPUs on NVIDIA DGX A100", "DGX A100 node (8 A100, 64-core AMD Rome, 1 TB RAM); 2 GPUs used, max memory 300 GB", "parabricks"),
    ("dgx-gpu4", "Parabricks 3.7.0-1, 4 A100 GPUs on NVIDIA DGX A100", "DGX A100 node; 4 GPUs used, max memory 300 GB", "parabricks"),
    ("dgx-gpu8", "Parabricks 3.7.0-1, 8 A100 GPUs on NVIDIA DGX A100", "DGX A100 node; 8 GPUs used, max memory 300 GB", "parabricks"),
]
AWS_GPU_NOTE = ("Table 1 footnote says the AWS GPU rows are the p3 family with V100 GPUs, but Results 'GPU performance across "
                "cloud platforms' paragraph 2 attributes the AWS savings printed in Table 1 (for example 63% for HaplotypeCaller "
                "with 4 GPUs) to the p4 machine with A100 GPUs and the p3 results to Additional file 1 Table S1.")
B_CONF = []
for key, name, hw, mkey in B_CONF_SPEC:
    attrs = {"reported_name": name, "hardware": {"description": hw},
             "source_locator": "Table 1 VM-type column; Methods 'GCP configuration', 'AWS configuration', 'DGX configuration'"}
    if mkey:
        mid = method("parabricks", "NVIDIA Parabricks", "GPU-accelerated implementations of alignment, GATK steps and variant callers.",
                     "Parabricks", ["conventional_pipeline"], [B_ART])
        attrs["version"] = "Parabricks v. 3.7.0-1"
        attrs["protocol"] = "Parabricks Germline Pipeline, DeepVariant Germline Pipeline, mutectcaller, somaticsniper_workflow, muse or lofreq, by protocol"
        if key.startswith("aws"):
            attrs["model_identity_note"] = AWS_GPU_NOTE
    else:
        mid = None
        attrs["protocol"] = ("Snakemake v6.6.1 CPU workflows matching the Parabricks steps: bwa mem 0.7.15, Samtools, GATK 4.2.0.0 and "
                             "HaplotypeCaller 4.2.0.0 or DeepVariant 1.1.0; Mutect2 4.2.0.0, SomaticSniper 1.0.5.0, LoFreq 2.1, MuSE 2.0 (single thread)")
        attrs["version"] = "HaplotypeCaller 4.2.0.0; DeepVariant 1.1.0; Mutect2 4.2.0.0; SomaticSniper 1.0.5.0; LoFreq 2.1; MuSE 2.0"
    B_CONF.append(config(f"{P}-config-oconnell2023-{key}", f"{name} (O'Connell et al. 2023)", f"{name} as run in Table 1.",
                         [B_ART], mid, attrs))

B_DATA = {
    "germline": rec(f"{P}-data-oconnell2023-hg002-30x", "dataset", "HG002 (GIAB) WGS FASTQ down-sampled to 30x, precisionFDA Truth Challenge V2",
                    "Germline input in O'Connell et al. 2023.", [B_ART], [],
                    {"population": "One sample, HG002, down-sampled to 30x with Samtools v1.9; GRCh38 from the GATK reference bundle",
                     "split": "Single sample, one recorded run per configuration",
                     "source_locator": "Methods 'Sampling and algorithms' paragraph 1",
                     "missing_metadata": {"version": {"reason": "unreported"}}})["id"],
    "somatic": rec(f"{P}-data-oconnell2023-hg002-somatosim", "dataset", "Synthetic tumour BAM: HG002 30x with 198 SNVs added by SomatoSim v1.0.0",
                   "Somatic input in O'Connell et al. 2023.", [B_ART], [],
                   {"population": "HG002 30x BAM after MarkDuplicates and BQSR, with 198 SNVs at random VAF 0.001-0.4 from ICGC donor DO32536 sites",
                    "split": "Single synthetic tumour, one recorded run per configuration",
                    "source_locator": "Methods 'Sampling and algorithms' paragraph 3",
                    "missing_metadata": {"version": {"reason": "unreported"},
                                         "population_detail": {"reason": "unreported", "note": "The matched normal used by the somatic callers is not described"}}})["id"],
}
COLMAP = [(4, "runtime-min", "Time (min)"), (5, "runtime-h", "Time (h)"), (6, "cost", "Cost ($)"),
          (7, "speedup", "Fold acceleration"), (8, "saving", "% cost-savings")]
EMPTY = {"–", "_"}
b_order = 0
for ci, caller in enumerate(CALLERS):
    block = body[ci * 11:(ci + 1) * 11]
    pipeline = "Germline" if caller in ("DeepVariant", "HaplotypeCaller") else "Somatic"
    assert block[0][1] == pipeline and block[0][3] == caller, block[0]
    for k, r in enumerate(block):
        assert r[0] == PLAT_SEQ[k], (caller, k, r)
        if k:
            assert r[1] == "" and r[3] == "", (caller, k, r)
        if VM_SEQ[k]:
            assert r[2] == VM_SEQ[k], (caller, k, r)
        else:
            assert r[2] in ("n2-32", "N2-32", "N2_32"), r
        if k >= 8:
            assert all(r[c] in EMPTY for c in (6, 7, 8)), r
    b_order += 1
    did = B_DATA["germline" if pipeline == "Germline" else "somatic"]
    pid = f"{P}-protocol-oconnell2023-{caller.lower()}"
    lims = ["One recorded run per configuration (Methods: 'we recorded the time of our final workflow run'); no repeats printed.",
            "Costs are on-demand cloud prices at the time of the study and exclude storage and licences; DGX rows have no cost.",
            "Authors are from Deloitte Consulting, an NVIDIA, AWS and Google alliance partner (Competing interests).",
            AWS_GPU_NOTE]
    if pipeline == "Germline":
        lims.append("Germline pipelines run from FASTQ to unfiltered VCF; accuracy is not reported.")
    else:
        lims.append("Somatic callers run from a prepared BAM; accuracy on the 198 added SNVs is not reported.")
    if caller == "Mutect2":
        lims.append("Results 'CPU baseline across cloud platforms' gives AWS Mutect2 CPU as 16.9 h; Table 1 prints 6.91 h.")
    rec(pid, "protocol", f"{caller} execution on CPU and GPU cloud and DGX machines (O'Connell et al. 2023 Table 1)",
        f"Wall-clock time, on-demand cost, speedup and cost saving for {caller} on CPU machines and 2, 4 or 8 GPUs.", [B_ART],
        [{"relation": "uses_data", "target_id": did}],
        {"protocol": (f"{pipeline} {caller} workflow timed end to end on each machine; fold acceleration and % cost-savings are relative to "
                      "the CPU machine on the same cloud platform."),
         "version": f"Table 1 rows for Variant-caller '{caller}'", "metric": "runtime", "unit": "minute",
         "limitations": lims, "source_locator": f"Table 1, rows {ci * 11 + 1}-{ci * 11 + 11} (Variant-caller '{caller}')"})
    for k, r in enumerate(block):
        ckey = B_CONF_SPEC[k][0]
        eid = f"{P}-eval-oconnell2023-{ckey}-{caller.lower()}"
        plat = ["AWS"] * 4 + ["GCP"] * 4 + ["DGX"] * 3
        evaluation(eid, f"{caller} on {B_CONF_SPEC[k][1]} (O'Connell et al. 2023)", B_CONF[k], pid, did, [B_ART],
                   "independent_paper",
                   {"dataset_version": None, "split": "Single sample", "population": "HG002 30x" if pipeline == "Germline" else "HG002 30x synthetic tumour",
                    "inputs": "FASTQ" if pipeline == "Germline" else "BAM", "adaptation": None,
                    "metric_implementation": "Workflow wall-clock; cost from on-demand hourly price", "aggregation": "Single run",
                    "budget": B_CONF_SPEC[k][2]},
                   f"Table 1, row {ci * 11 + k + 1} ({plat[k]}, {r[2]}, {caller})",
                   missing={"comparison.dataset_version": {"reason": "unreported"}})
        for col, metric, header in COLMAP:
            v = r[col]
            if v in EMPTY:
                continue
            qual = {"runtime-min": "workflow wall-clock, printed in minutes", "runtime-h": "workflow wall-clock, printed in hours",
                    "cost": "on-demand cloud cost per sample", "speedup": f"relative to the CPU machine on {plat[k]}",
                    "saving": f"relative to the CPU machine on {plat[k]}"}[metric]
            result(f"{P}-result-oconnell2023-{ckey}-{caller.lower()}-{METRIC[metric]['metric']}" + ("-hours" if metric == "runtime-h" else ""),
                   eid, [B_ART], B_SHA, B_URL, f"Table 1, row {ci * 11 + k + 1} ({plat[k]}, {r[2]}, {caller}), column '{header}'",
                   v, metric, qual, B_HOW)
    judgement(f"oconnell2023-{caller.lower()}", pid, f"{caller} CPU and GPU execution (O'Connell et al. 2023)", [B_ART], "direct",
              f"Wall-clock time, cost per sample, speedup and cost saving for {caller} on CPU and 2, 4 and 8 GPU machines on AWS, GCP and a DGX",
              ("Directly measures the runtime and cloud cost of one workflow on the same input across CPU and GPU machine types; "
               "authors are an NVIDIA alliance partner but did not develop Parabricks or the callers."),
              CONSTRAINTS, lims, [(B_ART, f"Table 1 rows for '{caller}'; Methods 'Sampling and algorithms' and configuration sections")],
              f"oconnell2023-{pipeline.lower()}", f"{pipeline} callers on CPU and GPU cloud machines (O'Connell et al. 2023)",
              "runtime", stratum=caller, order=b_order if pipeline == "Germline" else b_order - 2)

# ---------------------------------------------------------------------------------------------
# =============================================================================================
# C. Franzoso et al. 2025, Clinical and Translational Science 18:e70416, Supplementary Tables S1-S2
# =============================================================================================
C_ART, C_S2 = f"{P}-source-franzoso2025", f"{P}-source-franzoso2025-table-s2"
C_SRC = [C_ART, C_S2]
C_ART_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12627752/fullTextXML"
C_SUP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12627752/supplementaryFiles"
C_PIN = {"franzoso2025-article.xml": "65ddebf128fb41ddf2c2d7d29094871bdeded0ae0c8c4c89acb29884c65f4d38",
         "franzoso2025-table-s1.xlsx": "b221919e435217c607ff426d80fc5718c7f4d3e0fbaa6261cf13e8c5b7ae0f4e",
         "franzoso2025-table-s2.xlsx": "0b32a6146536f820e547ed5ac458ae789477358dbfdf339a634a9b78e6c60bd7"}
for name, digest in C_PIN.items():
    assert sha256(open(os.path.join(DL, name), "rb").read()) == digest, name
rec(C_ART, "source", "Rapid NGS Analysis on Google Cloud Platform: Performance Benchmark and User Tutorial",
    "Primary source retrieved and hashed for the diagnostic genomics execution use-case pass.", [], [],
    {"url": "https://doi.org/10.1111/cts.70416", "artifact_url": C_ART_URL,
     "version": "Clinical and Translational Science 18(11):e70416, published 2025-11-18; PMC12627752 full-text XML",
     "retrieved_at": "2026-10-09T20:22:39Z", "artifact_sha256": C_PIN["franzoso2025-article.xml"], "doi": "10.1111/cts.70416",
     "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml"})
rec(C_S2, "source", "Franzoso et al. 2025, Table S2 (runtime and costs per sample) and Table S1 (sample identifiers)",
    "Supplementary workbooks with per-sample runtime and cost for Sentieon DNASeq and Parabricks Germline on GCP.", [], [],
    {"url": "https://doi.org/10.1111/cts.70416", "artifact_url": C_SUP_URL,
     "version": "CTS-18-e70416-s002.xlsx (Table S2) inside the Europe PMC supplementary files bundle for PMC12627752",
     "retrieved_at": "2026-10-09T20:26:38Z", "artifact_sha256": C_PIN["franzoso2025-table-s2.xlsx"],
     "artifact_member": "CTS-18-e70416-s002.xlsx",
     "hash_scope": ("SHA-256 of CTS-18-e70416-s002.xlsx. Table S1 (CTS-18-e70416-s001.xlsx) from the same bundle has SHA-256 "
                    f"{C_PIN['franzoso2025-table-s1.xlsx']} and is used only to assert sample identifiers. "
                    "The bundle is assembled per request, so only member hashes are pinned."),
     "doi": "10.1111/cts.70416", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})

t1 = rawxlsx.read(os.path.join(DL, "franzoso2025-table-s1.xlsx"))["Sheet1"]
assert t1["A2"] == "DATASET" and t1["B2"] == "IDENTIFIER" and t1["C2"] == "SIZE (GB)", t1
S1ROWS = {t1[f"B{r}"]: (t1[f"A{r}"], t1[f"C{r}"]) for r in range(3, 13)}
WES = [k for k, v in S1ROWS.items() if v[0] == "exome"]
WGS = [k for k, v in S1ROWS.items() if v[0] == "genome"]
assert len(WES) == 5 and len(WGS) == 5
z2 = zipfile.ZipFile(os.path.join(DL, "franzoso2025-table-s2.xlsx"))
styles = z2.read("xl/styles.xml").decode()
xfs = re.findall(r"<xf [^>]*>", re.search(r"<cellXfs[^>]*>(.*?)</cellXfs>", styles, re.S).group(1))
sheet_xml = z2.read("xl/worksheets/sheet1.xml").decode()
style_of = {m.group(1): int(m.group(2)) for m in re.finditer(r'<c r="([A-Z]+\d+)" s="(\d+)"', sheet_xml)}
t2 = rawxlsx.read(os.path.join(DL, "franzoso2025-table-s2.xlsx"))["Sheet1"]
assert t2["A1"] == "Table S2: Runtime and costs for each of the samples analysed. ", repr(t2["A1"])
assert [t2["A2"], t2["B2"], t2["C2"], t2["D2"]] == ["ID", "Software", "Runtime (h/m/s)", "Cost ($)"]
C_HOW = ("Extracted by deterministic parse of the pinned XLSX cell XML (extract/extract_model_execution.py with "
         "extract/rawxlsx.py), with the title, headers, sample identifiers (checked against Table S1) and software labels "
         "asserted. Runtime cells use built-in number format 21 (h:mm:ss); printed_value is that rendering of the stored "
         "day fraction and numeric_value is the same duration in seconds. Cost printed_value is the shortest round-trip "
         "decimal of the stored double.")


def hms(raw):
    secs = Decimal(raw) * 86400
    whole = int(secs.to_integral_value())
    assert abs(secs - whole) < Decimal("0.001"), raw
    return f"{whole // 3600}:{whole % 3600 // 60:02d}:{whole % 60:02d}", str(whole)


def shortest(raw):
    s = repr(float(raw))
    return s[:-2] if s.endswith(".0") else s


C_VM = {
    "Sentieon": ("sentieon-dnaseq-202308-gcp-64vcpu", "Sentieon DNASeq v202308 on a GCP VM with 64 vCPUs and 57 GB memory",
                 "64 vCPUs, 57 GB memory, no GPU; baseline cost 1.79 USD per hour", "v202308",
                 ("sentieon-dnaseq", "Sentieon DNASeq", "CPU-optimised germline pipeline reimplementing BWA alignment, duplicate marking, base recalibration and haplotype-based calling.", "Sentieon DNASeq")),
    "Parabricks": ("parabricks-germline-4-0-1-1-gcp-t4", "NVIDIA Parabricks Germline v4.0.1-1 on a GCP VM with 48 vCPUs, 58 GB memory and 1 T4 GPU",
                   "48 vCPUs, 58 GB memory, 1 NVIDIA T4 GPU; baseline cost 1.65 USD per hour", "v4.0.1-1",
                   ("parabricks", "NVIDIA Parabricks", "GPU-accelerated implementations of alignment, GATK steps and variant callers.", "Parabricks")),
}
C_CONF = {}
for label, (ckey, name, hw, ver, (mkey, mname, mdesc, mrep)) in C_VM.items():
    mid = method(mkey, mname, mdesc, mrep, ["conventional_pipeline"], [C_ART])
    if mkey == "sentieon-dnaseq":
        METHODS[mid]["attributes"]["access"] = "Commercial software; the article notes licensing fees are not included in the costs (Discussion paragraph 10)"
    C_CONF[label] = config(f"{P}-config-franzoso2025-{ckey}", f"{name} (Franzoso et al. 2025)", f"{label} rows of Table S2.", C_SRC, mid,
                           {"reported_name": label, "version": ver, "hardware": {"description": hw},
                            "protocol": "Default parameters and steps: alignment, duplicate marking, base recalibration and variant calling, FASTQ to VCF",
                            "source_locator": "Methods 'Design of the Benchmark' paragraph 1 and 'Cloud Deployment Design and Implementation' paragraph 3"})
ANOMALY = {("ERR1955532", "Sentieon"): "Printed 0:03:21; Results 'Software Runtimes' paragraph 2 gives a Sentieon WGS range of 3 to 3.8 h, so this cell may have been entered as minutes and seconds instead of hours and minutes. Kept as printed.",
           ("ERR1955539", "Parabricks"): "Printed 0:04:41; Results 'Software Runtimes' paragraph 2 gives a Parabricks WGS range of 4.1 to 4.7 h, so this cell may have been entered as minutes and seconds instead of hours and minutes. Kept as printed."}
c_order = 0
r = 3
for kind, ids, ddesc in (("wes", WES, "Five WES samples (Twist Core Exome, Illumina NextSeq 500, 2x75 bp) from an HLH-like syndrome study"),
                         ("wgs", WGS, "Five WGS samples from Illumina's Polaris project (HiSeq X, 150 bp reads)")):
    c_order += 1
    did = rec(f"{P}-data-franzoso2025-{kind}", "dataset", ddesc, f"{kind.upper()} input FASTQ in Franzoso et al. 2025.", C_SRC, [],
              {"population": "; ".join(f"{i} ({S1ROWS[i][1]} GB FASTQ)" for i in ids),
               "split": "Five samples, one run per sample and pipeline", "accession": ", ".join(ids),
               "source_locator": "Table S1; Methods 'Samples and Data Availability'",
               "missing_metadata": {"version": {"reason": "unreported"}}})["id"]
    pid = f"{P}-protocol-franzoso2025-{kind}-gcp"
    lims = ["One run per sample and pipeline; no repeats.",
            "The two VMs were chosen for similar hourly cost (1.79 and 1.65 USD), not similar hardware.",
            "Costs exclude the Sentieon licence fee (Discussion paragraph 10).",
            "Accuracy of the calls is not reported."]
    if kind == "wgs":
        lims.append("Two runtime cells (ERR1955532 Sentieon 0:03:21, ERR1955539 Parabricks 0:04:41) disagree with the WGS ranges in Results and are flagged on the results.")
    rec(pid, "protocol", f"{kind.upper()} FASTQ-to-VCF runtime and cost on GCP, Sentieon versus Parabricks (Franzoso et al. 2025 Table S2)",
        f"Elapsed runtime and cost per sample for two ultra-rapid germline pipelines on cost-matched GCP VMs, {kind.upper()} samples.",
        C_SRC, [{"relation": "uses_data", "target_id": did}],
        {"protocol": "Each pipeline run from raw FASTQ to VCF with default parameters on its own GCP VM; start and end times and cost from GCP monitoring (Ops Agent).",
         "version": f"Table S2 rows for the {kind.upper()} samples", "metric": "runtime", "denominator": 5, "limitations": lims,
         "missing_metadata": {"metric_implementation": {"reason": "unreported", "note": "How cost per sample was computed from the GCP billing is not stated"}},
         "source_locator": "Table S2; Methods 'Data Collection and Analysis'"})
    rows = {}
    for s in ids:
        for label in ("Sentieon", "Parabricks"):
            assert (t2[f"A{r}"], t2[f"B{r}"]) == (s, label), (r, t2[f"A{r}"], t2[f"B{r}"])
            rows[(s, label)] = r
            r += 1
    for label in ("Sentieon", "Parabricks"):
        ck = C_VM[label][0]
        eid = f"{P}-eval-franzoso2025-{ck}-{kind}"
        evaluation(eid, f"{label} on GCP, {kind.upper()} samples (Franzoso et al. 2025)", C_CONF[label], pid, did, C_SRC,
                   "independent_paper",
                   {"dataset_version": None, "split": "Five samples", "population": f"{len(ids)} {kind.upper()} samples",
                    "inputs": "Raw FASTQ", "adaptation": None, "metric_implementation": "GCP monitoring start and end times; GCP cost",
                    "aggregation": "One value per sample", "budget": C_VM[label][2]},
                   f"Table S2 rows for {kind.upper()} samples, Software '{label}'",
                   missing={"comparison.dataset_version": {"reason": "unreported"}})
        for s in ids:
            rr = rows[(s, label)]
            assert style_of[f"C{rr}"] == 5 and 'numFmtId="21"' in xfs[5], (rr, style_of.get(f"C{rr}"))
            pv, nv = hms(t2[f"C{rr}"])
            attrs = {"metric": "runtime", "metric_direction": "lower", "unit": "second", "metric_qualifier": f"FASTQ to VCF; sample {s}",
                     "printed_value": pv, "numeric_value": nv, "raw_xml_value": t2[f"C{rr}"],
                     "workbook_number_format": "built-in 21 (h:mm:ss)",
                     "printed_value_basis": "Rendering of the stored day fraction in the cell's h:mm:ss number format; numeric_value is seconds",
                     "source_locator": f"Table S2 (CTS-18-e70416-s002.xlsx), C{rr}; ID '{s}'; Software '{label}'; column 'Runtime (h/m/s)'",
                     "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Single run per cell"}},
                     "review": {**review_note(C_HOW), "artifact_sha256": C_PIN["franzoso2025-table-s2.xlsx"], "retrieval_url": C_SUP_URL}}
            if (s, label) in ANOMALY:
                attrs["source_anomaly"] = ANOMALY[(s, label)]
            rid = f"{P}-result-franzoso2025-{ck}-{s.lower()}-runtime"
            rec(rid, "result", f"franzoso2025 {label} {s} runtime", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                C_SRC, [{"relation": "evaluation", "target_id": eid}], attrs, facets={})
            claims_rows.append([rid, C_S2, attrs["source_locator"], pv, "result"])
            cost = t2[f"D{rr}"]
            cattrs = {"metric": "compute-cost", "metric_direction": "lower", "unit": "us-dollar",
                      "metric_qualifier": f"GCP cost per sample, FASTQ to VCF; sample {s}",
                      "printed_value": shortest(cost), "numeric_value": format(Decimal(shortest(cost)), "f"), "raw_xml_value": cost,
                      "source_locator": f"Table S2 (CTS-18-e70416-s002.xlsx), D{rr}; ID '{s}'; Software '{label}'; column 'Cost ($)'",
                      "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Single run per cell"}},
                      "review": {**review_note(C_HOW), "artifact_sha256": C_PIN["franzoso2025-table-s2.xlsx"], "retrieval_url": C_SUP_URL}}
            cid_ = f"{P}-result-franzoso2025-{ck}-{s.lower()}-compute-cost"
            rec(cid_, "result", f"franzoso2025 {label} {s} compute cost", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                C_SRC, [{"relation": "evaluation", "target_id": eid}], cattrs, facets={})
            claims_rows.append([cid_, C_S2, cattrs["source_locator"], cattrs["printed_value"], "result"])
    judgement(f"franzoso2025-{kind}", pid, f"{kind.upper()} runtime and cost on GCP, Sentieon versus Parabricks (Franzoso et al. 2025)", C_SRC,
              "direct", f"Elapsed FASTQ-to-VCF runtime and GCP cost per sample for Sentieon DNASeq v202308 and Parabricks Germline v4.0.1-1 on five {kind.upper()} samples",
              ("Directly measures runtime and cost per sample for two ultra-rapid germline pipelines on cost-matched cloud machines, "
               "framed for hospital diagnostic use; independent academic group with no declared conflicts."),
              CONSTRAINTS, lims, [(C_S2, f"Table S2 rows for the {kind.upper()} samples"), (C_ART, "Methods; Results 'Software Runtimes' and 'Costs'")],
              "franzoso2025-gcp", "Sentieon versus Parabricks on cost-matched GCP machines (Franzoso et al. 2025)", "runtime",
              stratum=kind.upper(), order=c_order)
assert f"A{r}" not in t2, ("extra rows", r)

ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), [i for i, c in Counter(ids).items() if c > 1]
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
