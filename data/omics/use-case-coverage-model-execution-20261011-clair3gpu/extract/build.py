"""Build batch.jsonl for Zheng et al. 2026 (accelerated Clair3), Supplementary Tables 1-3.

Usage: python3 -I build.py <supplementary.pdf>

Supplementary Table 1 is parsed from the PDF text layer (pdftotext -layout). Supplementary Tables 2
and 3 are raster images in the PDF (pdfimages lists them on pages 2 and 3), so their cells were
transcribed by hand from 300 dpi renders and are written out below. Every record is needs_review.
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
SUPP_SHA = "feec482c5befbb44f93b82782b200a3abebaf7d81a0aad81e28de191be1523d9"
XML_SHA = "99ef4db5251a77e6fb9137aa3699b4dac93bdef2aff99de91c4d24ca5fc6a965"
ZIP_SHA = "b0df24a11fb7652c6d0f6f359c6f02ed2de092ea820e93c2c2841645aa2cf3c6"
SRC = P + "source-zheng2026-clair3"
SUPP = P + "source-zheng2026-clair3-supplement"
SOURCES = [SRC, SUPP]

pdf = sys.argv[1]
assert hashlib.sha256(open(pdf, "rb").read()).hexdigest() == SUPP_SHA, "supplement hash differs"
text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout

records, claims = [], []

records += [
    source(SRC, "Accelerated long-read variant calling with Clair3 for whole-genome sequencing",
           "https://doi.org/10.1093/bioinformatics/btag181",
           "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13141153/fullTextXML",
           "Bioinformatics 42(5), published 2026-04-10; PMC13141153 full-text XML", "2026-10-11T21:42:40Z",
           XML_SHA, "10.1093/bioinformatics/btag181", "peer_reviewed", "CC-BY-4.0", "application/xml",
           "Primary article retrieved and hashed for the diagnostic genomics execution literature pass (2026-10-11)."),
    source(SUPP, "Accelerated long-read variant calling with Clair3: Supplementary Data",
           "https://doi.org/10.1093/bioinformatics/btag181",
           "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13141153/supplementaryFiles",
           "btag181_supplementary_data.pdf from the Europe PMC supplementary files of PMC13141153", "2026-10-11T21:42:40Z",
           SUPP_SHA, "10.1093/bioinformatics/btag181", "peer_reviewed", "CC-BY-4.0", "application/pdf",
           "Supplementary PDF retrieved and hashed for the diagnostic genomics execution literature pass (2026-10-11)."),
]
records[1]["attributes"]["artifact_member"] = "btag181_supplementary_data.pdf"
records[1]["attributes"]["evidence_concerns"] = [{
    "source_id": SUPP,
    "message": "Supplementary Table 2 runtimes differ from the article's Results for what appear to be the same HG003 comparisons. ONT at 30x and 50x: Clair3 GPU 17 and 20 minutes in the table, 16 and 15 in Results 3.1.1; DeepVariant GPU 48 and 82 in the table, 106 to 128 in the text. PacBio Revio at 30x and 50x: Clair3 GPU 12 and 12 in the table, 23 and 21 in Results 3.1.2; DeepVariant GPU 40 and 53 in the table, 93 and 118 in the text. The table's Clair3 PacBio runtimes equal the macOS M3 Ultra runtime in Results 3.1.3, not the Linux RTX 4090 runtimes. The table and the Supplementary Notes commands give DeepVariant v1.10-beta; Results 3.1 say v1.8. Supplementary Table 3 DeepVariant ONT SNP precision, recall and F1 at 10x and 20x (97.58%, 92.35%, 94.89% and 99.32%, 99.02%, 99.17%) differ from Results 3.2 (97.34%, 92.17%, 94.68% and 98.75%, 98.79%, 98.79%), while the Clair3 values agree. Results 3.2 cite Supplementary Table 2 for the HG001 to HG007 comparison, which is Supplementary Table 4. The hardware, DeepVariant version and runs behind Supplementary Tables 2 and 3 are therefore uncertain. Supplementary Table 1 agrees with Results 3.1.4 except WhatsHap ONT 30x (723 seconds in the table, 724 in the text). Table values are recorded; text values are not.",
    "source_locator": "Supplementary Tables 1 to 3 (pages 2 and 3) versus article Results 3.1.1 to 3.1.4 and 3.2",
    "artifact_sha256": "feec482c5befbb44f93b82782b200a3abebaf7d81a0aad81e28de191be1523d9",
    "reviewed_at": "2026-10-12T07:50:32Z",
    "review_method": "automated-source-review",
}]
records[1]["attributes"]["retrieval_note"] = (
    f"Europe PMC supplementaryFiles zip (SHA-256 {ZIP_SHA}); artifact_sha256 is the PDF member. "
    "Supplementary Tables 2 and 3 are raster images in the PDF with no text layer.")

# Models (families) and configurations.
CLAIR3 = "somatic-clairs-to-20261011-method-clair3"  # existing record on main (review C1)
DV = P + "model-deepvariant"
FAC = {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["supervised_machine_learning"]}
records += [
    entity(DV, "model", "DeepVariant", "Deep-learning variant caller that classifies pileup images with a convolutional network.",
           [SRC], {"reported_name": "DeepVariant", "entity_level": "family",
                   "source_locator": "Introduction; Supplementary Notes 'Running DeepVariant'",
                   "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
           facets=FAC),
]
HW_T2 = ("Not stated in Supplementary Table 2. Methods 'Computational performance' say the GPU version was benchmarked with other "
         "callers on an NVIDIA GeForce RTX 4090 with two 12-core Intel Xeon Silver 4116 processors; Results 3.1.1 and 3.1.2 give the "
         "Figure 2a runs as a Linux system with one RTX 4090 and 32 CPU threads; Supplementary Figure 2 says Clair3 used one NVIDIA 4090 GPU.")
cfg = {
    "c3gpu": (P + "config-zheng2026-clair3-1-2-0-gpu", "Clair3 v1.2.0 GPU mode (Zheng et al. 2026)", CLAIR3, "Clair3 v1.2.0 (GPU mode)", "v1.2.0",
              "Clair3 v1.2.0 run with --use_gpu (Supplementary Notes command); parallel chunking, LongPhase phasing, in-memory haplotagging."),
    "dvgpu": (P + "config-zheng2026-deepvariant-1-10-beta-gpu", "DeepVariant v1.10-beta GPU mode (Zheng et al. 2026)", DV, "DeepVariant v1.10-beta (GPU mode)", "v1.10-beta",
              "google/deepvariant:v1.10-beta-gpu container, run_deepvariant with --model_type set to the platform (Supplementary Notes command)."),
    "c3acc": (P + "config-zheng2026-clair3-accuracy", "Clair3, accuracy runs (Zheng et al. 2026 Supplementary Table 3)", CLAIR3, "Clair3", None,
              "Final Clair3 output (pileup plus full-alignment calls) as labelled 'Clair3' in Supplementary Table 3."),
    "c3pile": (P + "config-zheng2026-clair3-pileup-accuracy", "Clair3 pileup-only calls (Zheng et al. 2026 Supplementary Table 3)", CLAIR3, "Clair3 pileup", None,
               "Clair3 pileup-model calls only, as labelled 'Clair3 pileup' in Supplementary Table 3."),
    "dvacc": (P + "config-zheng2026-deepvariant-accuracy", "DeepVariant, accuracy runs (Zheng et al. 2026 Supplementary Table 3)", DV, "DeepVariant", None,
              "DeepVariant as labelled in Supplementary Table 3."),
}
for key, (cid, name, model, reported, version, protocol) in cfg.items():
    attrs = {"reported_name": reported, "foundation_model_eligible": False,
             "access_reuse": "Open-source software" , "protocol": protocol}
    if version:
        attrs["version"] = version
        attrs["hardware"] = {"description": HW_T2}
        attrs["source_locator"] = "Supplementary Table 2 caller labels; Supplementary Notes command lines"
    else:
        attrs["missing_metadata"] = {"version": {"reason": "conflicting" if model == DV else "unreported",
                                                 "note": ("Supplementary Table 3 prints no version; Results 3.1 name DeepVariant v1.8 while Supplementary Table 2 and the Supplementary Notes commands use v1.10-beta"
                                                          if model == DV else "Supplementary Table 3 prints no version; the article evaluates Clair3 v1.2")}}
        attrs["source_locator"] = "Supplementary Table 3 caller labels"
    if model == DV and version:
        attrs["model_identity_note"] = "Results 3.1.1 and 3.1.2 call the DeepVariant runs v1.8; Supplementary Table 2 and the Supplementary Notes commands give v1.10-beta."
    records.append(entity(cid, "configuration", name, protocol, SOURCES, attrs, [("configuration_of", model)], facets=FAC))

# Datasets.
DS = {
    "ONT": (P + "data-zheng2026-hg003-ont-r1041", "GIAB HG003 whole genome, ONT R10.4.1 5 kHz (EPI2ME giab-2025.01), subsampled to 10x-50x",
            "ONT EPI2ME Labs HG001-HG007 R10.4.1 5kHz GRCh38 release giab-2025.01 (https://epi2me.nanoporetech.com/giab-2025.01)"),
    "PacBio": (P + "data-zheng2026-hg003-pacbio-revio", "GIAB HG003 whole genome, PacBio Revio (2022Q4 release), subsampled to 10x-50x",
               "PacBio Revio HG002-HG004 GRCh38 (https://downloads.pacbcloud.com/public/revio/2022Q4/)"),
}
for plat, (did, name, acc) in DS.items():
    records.append(entity(did, "dataset", name, "HG003 reads subsampled with samtools view -s to stated coverages; GIAB v4.2.1 truth on GRCh38.",
                          SOURCES, {"accession": acc, "population": "One GIAB sample (HG003, NA24149) at 10x, 20x, 30x, 40x and 50x coverage",
                                    "split": "HG003 is held out from Clair3 and DeepVariant training (Results 3.2)",
                                    "source_locator": "Supplementary Notes 'Data availability' and 'BAM subsampling'; Results 3.2",
                                    "missing_metadata": {"version": {"reason": "unreported", "note": "Release folder named; no file checksums given"}}}))

# Protocols.
LIM_COMMON = [
    "One value per configuration and coverage is printed; the number of runs behind it is not stated and no spread is printed.",
    "Author-reported: the authors develop Clair3; DeepVariant was run by them.",
]
protocols = {
    "res-ont": ("zheng2026-hg003-resource-ont", "HG003 ONT WGS variant-calling runtime, memory and I/O, Clair3 versus DeepVariant in GPU mode (Zheng et al. 2026 Supplementary Table 2)", "ONT", "runtime"),
    "res-pb": ("zheng2026-hg003-resource-pacbio", "HG003 PacBio Revio WGS variant-calling runtime, memory and I/O, Clair3 versus DeepVariant in GPU mode (Zheng et al. 2026 Supplementary Table 2)", "PacBio", "runtime"),
    "sub": ("zheng2026-hg003-clair3-stage-runtime", "Clair3 GPU workflow stage runtimes on HG003 ONT and PacBio WGS (Zheng et al. 2026 Supplementary Table 1)", None, "runtime"),
    "acc-ont": ("zheng2026-hg003-accuracy-ont", "HG003 ONT WGS small-variant accuracy against GIAB v4.2.1, Clair3 versus DeepVariant (Zheng et al. 2026 Supplementary Table 3)", "ONT", "f1-score"),
    "acc-pb": ("zheng2026-hg003-accuracy-pacbio", "HG003 PacBio Revio WGS small-variant accuracy against GIAB v4.2.1, Clair3 versus DeepVariant (Zheng et al. 2026 Supplementary Table 3)", "PacBio", "f1-score"),
}
PID = {k: P + "protocol-" + v[0] for k, v in protocols.items()}
plim = {
    "res-ont": LIM_COMMON + [
        "Hardware is not stated in Supplementary Table 2; the Methods give an NVIDIA GeForce RTX 4090 with two 12-core Intel Xeon Silver 4116 processors for the GPU benchmarks, and Results 3.1 describe the Figure 2a runs on one RTX 4090 with 32 CPU threads.",
        "Results 3.1.1 give different runtimes for what appear to be the same comparisons (Clair3 GPU 16 minutes at 30x and 15 at 50x; DeepVariant GPU 106 to 128 minutes) and name DeepVariant v1.8, while Supplementary Table 2 prints 17 and 20 minutes for Clair3 and 48 and 82 minutes for DeepVariant v1.10-beta.",
        "The Methods say runtime and memory were measured with the GNU time command, which reports host process memory, not GPU memory; how data movement was measured is not stated.",
        "Accuracy is printed in a separate table (Supplementary Table 3); the tables do not say they come from the same runs.",
    ],
    "res-pb": None,
    "sub": LIM_COMMON[:1] + [
        "Clair3 only; the stage columns show where time is spent, not a comparison with another caller.",
        "The table prints two phasing columns (LongPhase and WhatsHap); the printed total equals pileup calling plus LongPhase phasing plus full-alignment calling plus workflow control to within one second.",
        "Hardware is not stated in the table; the Methods give an NVIDIA GeForce RTX 4090 with two 12-core Intel Xeon Silver 4116 processors for the GPU benchmarks.",
    ],
    "acc-ont": LIM_COMMON + [
        "Results 3.2 quote DeepVariant values at 10x and 20x ONT (SNP F1 94.68% and 98.79%) that differ from Supplementary Table 3 (94.89% and 99.17%); the text and the table may describe different DeepVariant versions.",
        "No runtime is printed in this table.",
    ],
    "acc-pb": None,
}
plim["res-pb"] = [l.replace("Results 3.1.1 give different runtimes for what appear to be the same comparisons (Clair3 GPU 16 minutes at 30x and 15 at 50x; DeepVariant GPU 106 to 128 minutes) and name DeepVariant v1.8, while Supplementary Table 2 prints 17 and 20 minutes for Clair3 and 48 and 82 minutes for DeepVariant v1.10-beta.",
                            "Results 3.1.2 give different runtimes for what appear to be the same comparisons (Clair3 GPU 23 minutes at 30x and 21 at 50x; DeepVariant GPU 93 and 118 minutes) and name DeepVariant v1.8, while Supplementary Table 2 prints 12 minutes for Clair3 and 40 and 53 minutes for DeepVariant v1.10-beta.") for l in plim["res-ont"]]
plim["acc-pb"] = LIM_COMMON + [
    "Results 3.2 quote PacBio 10x values (Clair3 SNP F1 98.54%, indel 91.39%; DeepVariant 97.81% and 90.74%); the DeepVariant 10x values differ slightly from Supplementary Table 3 (97.80% and 91.08%).",
    "No runtime is printed in this table.",
]
plim["res-pb"].append("Supplementary Table 2 prints 12 minutes for Clair3 at 30x, 40x and 50x, which equals the macOS M3 Ultra runtime in Results 3.1.3 rather than the Linux RTX 4090 runtimes in Results 3.1.2.")
for k in plim:
    plim[k].append("The source has an unresolved evidence concern (Supplementary Tables 2 and 3 conflict with the Results text); see the source record.")
for k, (slugp, name, plat, metric) in protocols.items():
    uses = [DS[plat][0]] if plat else [DS["ONT"][0], DS["PacBio"][0]]
    attrs = {
        "protocol": {"res-ont": "Variant calling from aligned HG003 BAM to VCF at five coverages per platform; runtime, peak and average memory and total data movement per run.",
                     "sub": "Wall-clock time of each stage of the Clair3 GPU workflow on HG003 BAMs at 30x and 50x.",
                     "acc-ont": "VCF from each caller compared with GIAB v4.2.1 HG003 truth in the confident regions using hap.py 0.3.12 with the vcfeval engine, PASS calls only; precision, recall and F1 overall, for SNPs and for indels."}[
            {"res-pb": "res-ont", "acc-pb": "acc-ont"}.get(k, k)],
        "version": "Supplementary Table " + {"res-ont": "2", "res-pb": "2", "sub": "1", "acc-ont": "3", "acc-pb": "3"}[k],
        "metric": metric, "limitations": plim[k],
        "source_locator": "Supplementary Table " + {"res-ont": "2", "res-pb": "2", "sub": "1", "acc-ont": "3", "acc-pb": "3"}[k] + "; Supplementary Notes; Results 3.1-3.2",
    }
    if k.startswith("res"):
        attrs["memory_measurement"] = "GNU time (article Methods 'Computational performance')"
    records.append(entity(PID[k], "protocol", name, name, SOURCES, attrs, [("uses_data", d) for d in uses]))

# Evaluations and results.
def evaluation(cfg_key, prot_key, plat, origin, label, aggregation, locator):
    eid = f"{P}eval-zheng2026-{cfg[cfg_key][0].split('config-zheng2026-')[1]}-{protocols[prot_key][0].split('zheng2026-')[1]}" + ("" if prot_key != "sub" else "-" + plat.lower())
    comp = {"protocol_id": PID[prot_key], "dataset_version": None,
            "split": "HG003 subsampled to " + ("30x and 50x" if prot_key == "sub" else "10x, 20x, 30x, 40x and 50x"),
            "population": "One GIAB sample (HG003)", "inputs": "Aligned reads (BAM) and GRCh38 reference",
            "adaptation": None, "metric_implementation": None if prot_key != "acc-ont" and prot_key != "acc-pb" else "hap.py 0.3.12, vcfeval engine, PASS only",
            "aggregation": aggregation, "budget": "One value per caller and coverage; number of runs and hardware not stated in the table"}
    if comp["metric_implementation"] is None:
        comp["metric_implementation"] = None
    rec = entity(eid, "evaluation", label, "Published execution benchmark; transcribed, not reproduced.", SOURCES,
                 {"origin": origin, "protocol": PID[prot_key], "version": "Primary source as retrieved 2026-10-11",
                  "comparison": comp, "source_locator": locator,
                  "missing_metadata": {"comparison.dataset_version": {"reason": "unreported"}}},
                 [("system", cfg[cfg_key][0]), ("assessment", PID[prot_key]), ("data", DS[plat][0])])
    records.append(rec)
    return eid

def add_result(eid, rid, name, metric, direction, unit, printed, numeric, qualifier, locator, unit_detail, review, scope):
    records.append(result(rid, name, SOURCES, eid, metric, direction, unit, printed, numeric, locator, review,
                          qualifier=qualifier, unit_detail=unit_detail))
    claims.append((rid, SUPP, locator, printed, scope))

PARSE = extraction_review(["pdf-text-parse"],
    "Deterministic parse of `pdftotext -layout` text of the pinned supplementary PDF (extract/build.py), with the sample, platform, coverage and column order asserted.",
    "Extraction only; pending independent review.")
TRANS = extraction_review(["transcription", "rendered-source-visual-check"],
    "Supplementary Tables 2 and 3 are raster images (pdfimages lists one image each on pages 2 and 3), so cells were transcribed by hand from 300 dpi pdftoppm renders of the pinned PDF and read a second time at 110 dpi; both readings agreed.",
    "Extraction only; pending independent review. A reviewer should re-read every cell from a render of the pinned PDF.")

# Supplementary Table 1 (text layer).
m = re.search(r"Supplementary Table 1\..*?The runtime is calculated in second", text, re.S)
assert m, "Table 1 not found"
rows = re.findall(r"(\d0x)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", m.group(0))
assert [r[0] for r in rows] == ["30x", "50x", "30x", "50x"], rows
T1_COLS = [("Pileup calling", "pileup calling stage"), ("LongPhase for variant phasing", "LongPhase variant phasing stage"),
           ("or WhatHap for variant phasing", "WhatsHap variant phasing stage (alternative to LongPhase)"),
           ("Full-alignment calling", "full-alignment calling stage"), ("Workflow control", "workflow control"),
           ("Total runtime", "total")]
for i, row in enumerate(rows):
    plat = "ONT" if i < 2 else "PacBio"
    platlabel = "ONT r10.4.1 5kHz" if plat == "ONT" else "PacBio Revio"
    if i % 2 == 0:
        eid = evaluation("c3gpu", "sub", plat, "author_reported", f"Clair3 v1.2.0 GPU stage runtimes, HG003 {plat} (Zheng et al. 2026)",
                         "One value per stage and coverage", f"Supplementary Table 1 rows for HG003 {platlabel}")
    for (col, q), val in zip(T1_COLS, row[1:]):
        rid = f"{P}result-zheng2026-clair3-stage-{plat.lower()}-{row[0]}-{q.split(' (')[0].replace(' ', '-').lower()}"
        loc = f"Supplementary Table 1, sample HG003, platform '{platlabel}', read coverage {row[0]}, column '{col}'"
        add_result(eid, rid, f"zheng2026 Clair3 GPU {plat} {row[0]} {q}", "runtime", "lower", "second", val, val,
                   f"Clair3 GPU workflow, {q}; HG003 {plat} {row[0]}", loc, "printed as seconds ('The runtime is calculated in second')", PARSE, "pdf-text-layer")

# Supplementary Table 2 (transcribed from the image).
T2 = {
    ("ONT", "c3gpu"): [("10x", "22", "45,935", "10,180", "137"), ("20x", "16", "56,643", "6,803", "175"), ("30x", "17", "57,901", "10,189", "222"),
                       ("40x", "18", "62,871", "6,260", "263"), ("50x", "20", "63,174", "8,096", "307")],
    ("ONT", "dvgpu"): [("10x", "39", "63,386", "42,331", "125"), ("20x", "60", "56,509", "46,861", "196"), ("30x", "48", "60,245", "46,810", "235"),
                       ("40x", "65", "65,320", "56,213", "289"), ("50x", "82", "69,633", "49,208", "346")],
    ("PacBio", "c3gpu"): [("10x", "14", "41,832", "6,781", "88"), ("20x", "13", "52,578", "5,758", "98"), ("30x", "12", "49,319", "8,034", "128"),
                          ("40x", "12", "46,024", "7,985", "125"), ("50x", "12", "55,095", "5,489", "139")],
    ("PacBio", "dvgpu"): [("10x", "34", "52,412", "39,789", "80"), ("20x", "40", "58,852", "45,697", "99"), ("30x", "40", "57,350", "42,140", "128"),
                          ("40x", "48", "66,953", "52,545", "126"), ("50x", "53", "58,773", "45,738", "155")],
}
T2_COLS = [("Runtime (minutes)", "runtime", "lower", "minute", None, "runtime"),
           ("Peak memory (MB)", "peak-memory", "lower", "megabyte", "MB as printed; the Methods say memory was measured with GNU time (host process memory)", "peak-memory"),
           ("Average memory (MB)", "mean-memory", "lower", "megabyte", "MB as printed; the Methods say memory was measured with GNU time (host process memory)", "mean-memory"),
           ("Total data movement IO (GB)", "data-io-volume", "lower", "gigabyte", "GB as printed", "io")]
for (plat, ck), rows in T2.items():
    pk = "res-ont" if plat == "ONT" else "res-pb"
    platlabel = "ONT r10.4.1 5kHz" if plat == "ONT" else "PacBio Revio"
    caller = cfg[ck][3]
    origin = "author_reported" if ck.startswith("c3") else "independent_paper"
    eid = evaluation(ck, pk, plat, origin, f"{caller}, HG003 {plat} runtime and memory (Zheng et al. 2026)",
                     "One value per coverage", f"Supplementary Table 2, platform '{platlabel}', caller '{caller}'")
    for cov, *vals in rows:
        for (col, metric, direction, unit, detail, short), val in zip(T2_COLS, vals):
            rid = f"{eid.replace('-eval-', '-result-')}-{cov}-{short}"
            loc = f"Supplementary Table 2 (image, page 2), sample 'HG003 WGS', platform '{platlabel}', caller '{caller}', read coverage {cov}, column '{col}'"
            add_result(eid, rid, f"zheng2026 {caller} {plat} {cov} {short}", metric, direction, unit, val, val.replace(",", ""),
                       f"Variant calling from BAM, whole run; HG003 {plat} {cov}", loc, detail, TRANS, "rendered-image")

# Supplementary Table 3 (transcribed from the image).
T3 = """
ONT 10x c3acc 94.78 92.11 93.42 96.42 96.05 96.23 81.78 66.08 73.09
ONT 10x c3pile 90.24 89.07 89.65 93.37 93.27 93.32 67.90 61.41 64.49
ONT 10x dvacc 95.36 88.64 91.88 97.58 92.35 94.89 78.74 64.19 70.72
ONT 20x c3acc 98.53 96.21 97.35 99.46 99.20 99.33 91.40 76.48 83.28
ONT 20x c3pile 96.50 95.20 95.85 98.60 98.76 98.68 81.17 71.76 76.18
ONT 20x dvacc 96.70 96.43 96.56 99.32 99.02 99.17 79.83 79.37 79.60
ONT 30x c3acc 99.03 96.92 97.96 99.74 99.42 99.58 93.77 80.42 86.58
ONT 30x c3pile 97.67 96.38 97.02 99.43 99.51 99.47 84.97 75.75 80.10
ONT 30x dvacc 97.22 97.70 97.46 99.72 99.68 99.70 81.78 84.62 83.17
ONT 40x c3acc 99.20 97.27 98.23 99.82 99.47 99.65 94.70 82.76 88.33
ONT 40x c3pile 97.94 96.88 97.41 99.63 99.71 99.67 86.08 78.19 81.95
ONT 40x dvacc 97.45 98.10 97.77 99.80 99.77 99.79 83.13 87.06 85.05
ONT 50x c3acc 99.28 97.57 98.41 99.85 99.55 99.70 95.15 84.51 89.52
ONT 50x c3pile 98.06 97.16 97.61 99.70 99.78 99.74 86.66 79.88 83.13
ONT 50x dvacc 97.58 98.30 97.94 99.84 99.79 99.81 83.92 88.44 86.12
PacBio 10x c3acc 98.57 96.66 97.61 99.22 97.86 98.54 94.24 88.71 91.39
PacBio 10x c3pile 97.40 95.43 96.41 98.93 97.33 98.13 87.26 82.89 85.02
PacBio 10x dvacc 98.45 95.41 96.91 99.26 96.37 97.80 93.19 89.07 91.08
PacBio 20x c3acc 99.59 99.28 99.43 99.83 99.58 99.70 98.06 97.34 97.70
PacBio 20x c3pile 99.12 98.95 99.04 99.77 99.68 99.73 94.95 94.16 94.55
PacBio 20x dvacc 99.57 99.45 99.51 99.84 99.71 99.78 97.84 97.74 97.79
PacBio 30x c3acc 99.78 99.69 99.73 99.90 99.80 99.85 99.02 98.91 98.97
PacBio 30x c3pile 99.52 99.47 99.49 99.88 99.84 99.86 97.18 97.02 97.10
PacBio 30x dvacc 99.77 99.76 99.76 99.90 99.87 99.88 98.95 99.00 98.98
PacBio 40x c3acc 99.83 99.78 99.81 99.91 99.85 99.88 99.34 99.31 99.32
PacBio 40x c3pile 99.67 99.63 99.65 99.91 99.86 99.89 98.12 98.11 98.12
PacBio 40x dvacc 99.83 99.81 99.82 99.91 99.88 99.90 99.32 99.36 99.34
PacBio 50x c3acc 99.86 99.83 99.85 99.92 99.88 99.90 99.51 99.50 99.50
PacBio 50x c3pile 99.75 99.71 99.73 99.93 99.87 99.90 98.63 98.67 98.65
PacBio 50x dvacc 99.86 99.83 99.84 99.92 99.88 99.90 99.47 99.50 99.49
"""
T3_COLS = [(g, m) for g in ("Overall", "SNP", "Indel") for m in ("Precision", "Recall", "F1-score")]
METRIC = {"Precision": "precision", "Recall": "recall", "F1-score": "f1-score"}
t3_rows = [l.split() for l in T3.strip().splitlines()]
assert len(t3_rows) == 30 and all(len(r) == 12 for r in t3_rows)
evals = {}
for plat, cov, ck, *vals in t3_rows:
    pk = "acc-ont" if plat == "ONT" else "acc-pb"
    platlabel = "ONT r10.4.1 5kHz" if plat == "ONT" else "PacBio Revio"
    caller = cfg[ck][3]
    if (plat, ck) not in evals:
        origin = "author_reported" if ck.startswith("c3") else "independent_paper"
        evals[(plat, ck)] = evaluation(ck, pk, plat, origin, f"{caller}, HG003 {plat} small-variant accuracy (Zheng et al. 2026)",
                                       "One value per coverage and variant class", f"Supplementary Table 3, platform '{platlabel}', caller '{caller}'")
    eid = evals[(plat, ck)]
    for (group, col), val in zip(T3_COLS, vals):
        rid = f"{eid.replace('-eval-', '-result-')}-{cov}-{group.lower()}-{METRIC[col]}"
        loc = f"Supplementary Table 3 (image, page 3), platform '{platlabel}', read coverage {cov}, caller '{caller}', column '{group} {col}'"
        add_result(eid, rid, f"zheng2026 {caller} {plat} {cov} {group} {col}", METRIC[col], "higher", "percent", val + "%", val,
                   f"{group if group != 'Overall' else 'SNPs and indels'}; GIAB v4.2.1 HG003 confident regions; {plat} {cov}", loc, None, TRANS, "rendered-image")

# Descriptive claims.
records.append(entity(P + "claim-zheng2026-deepvariant-version", "claim", "version: DeepVariant runs (Zheng et al. 2026)",
                      "Descriptive fact transcribed from the pinned source.", SOURCES,
                      {"field": "version",
                       "value": "Supplementary Table 2 and the Supplementary Notes command lines give DeepVariant v1.10-beta (google/deepvariant:v1.10-beta and v1.10-beta-gpu); Results 3.1 compare 'DeepVariant v1.8 in CPU and GPU modes'. Supplementary Table 3 prints no version.",
                       "source_locator": "Supplementary Table 2 caller column; Supplementary Notes 'Running DeepVariant GPU version (v1.10-beta)' and 'Running DeepVariant CPU (v1.10-beta)'; Results 3.1.1 paragraph 1",
                       "review": extraction_review(["transcription"], "Read from the pinned article XML and supplementary PDF text.", "Extraction only; pending independent review.")},
                      [("subject", cfg["dvgpu"][0])], facets={}))
claims.append((P + "claim-zheng2026-deepvariant-version", SUPP, "Supplementary Table 2; Supplementary Notes; Results 3.1.1", "v1.10-beta / v1.8", "descriptive-claim"))

# Relevance judgements.
CONSTRAINTS = ["Inspect every linked evaluation's source locator before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; hardware, inputs, software versions and timing boundaries differ between sources."]
JUDGE = [
    ("res-ont", "proxy", "Runtime, peak and average memory and data movement per run for Clair3 v1.2.0 and DeepVariant v1.10-beta in GPU mode on HG003 ONT WGS at 10x to 50x",
     "Measures wall-clock runtime and peak memory of two deep-learning germline callers on one long-read genome across coverages, which bears on the resource and throughput part of the question for long-read workflows. Proxy rather than direct: the table does not state the hardware, the authors develop one of the two callers, the number of runs is not stated, and the runtimes disagree with those given in the Results text.",
     "zheng2026-hg003-resources", "Clair3 versus DeepVariant in GPU mode, runtime and memory on HG003 (Zheng et al. 2026)", "ONT", 1, "runtime"),
    ("res-pb", "proxy", "Runtime, peak and average memory and data movement per run for Clair3 v1.2.0 and DeepVariant v1.10-beta in GPU mode on HG003 PacBio Revio WGS at 10x to 50x",
     "Same measurement as the ONT protocol on PacBio Revio reads of the same sample. Proxy for the same reasons: unstated hardware, developer-run comparison, an unstated number of runs and runtimes that differ from the Results text.",
     "zheng2026-hg003-resources", "Clair3 versus DeepVariant in GPU mode, runtime and memory on HG003 (Zheng et al. 2026)", "PacBio Revio", 2, "runtime"),
    ("sub", "proxy", "Wall-clock time of each Clair3 v1.2.0 GPU workflow stage on HG003 ONT and PacBio WGS at 30x and 50x",
     "Shows which Clair3 stages dominate runtime on a long-read genome, which helps a team judge where its own hardware will limit throughput. Proxy: one caller, hardware not stated in the table, an unstated number of runs.",
     "zheng2026-clair3-stages", "Clair3 GPU workflow stage runtimes (Zheng et al. 2026)", None, None, "runtime"),
    ("acc-ont", "proxy", "Precision, recall and F1 for SNPs, indels and both against GIAB v4.2.1 HG003 for Clair3, Clair3 pileup-only and DeepVariant on ONT WGS at 10x to 50x",
     "Gives accuracy for the same sample, platform and coverages as the runtime and memory table, so a reader can set accuracy beside resource use, which no previously linked source allows. Proxy: the tables do not say they come from the same runs, the DeepVariant version is unclear, and accuracy is measured against a single GIAB sample in its confident regions.",
     "zheng2026-hg003-accuracy", "Clair3 versus DeepVariant small-variant accuracy on HG003 (Zheng et al. 2026)", "ONT", 1, "f1-score"),
    ("acc-pb", "proxy", "Precision, recall and F1 for SNPs, indels and both against GIAB v4.2.1 HG003 for Clair3, Clair3 pileup-only and DeepVariant on PacBio Revio WGS at 10x to 50x",
     "Accuracy for the PacBio Revio runs of the same sample and coverages as the runtime table. Proxy for the same reasons as the ONT accuracy protocol.",
     "zheng2026-hg003-accuracy", "Clair3 versus DeepVariant small-variant accuracy on HG003 (Zheng et al. 2026)", "PacBio Revio", 2, "f1-score"),
]
for k, rel, endpoint, rationale, group, title, label, order, headline in JUDGE:
    tnum = {"res-ont": "2", "res-pb": "2", "sub": "1", "acc-ont": "3", "acc-pb": "3"}[k]
    cites = [{"source_id": SUPP, "locator": f"Supplementary Table {tnum}; Supplementary Notes"},
             {"source_id": SRC, "locator": "Results 3.1-3.2; Conflict of interests; Data availability"}]
    records.append(judgement(f"use-case-mapping-model-execution-20261011-{protocols[k][0]}", PID[k], protocols[k][1].split(" (Zheng")[0] + " (Zheng et al. 2026)",
                             SOURCES, rel, endpoint, rationale, CONSTRAINTS, plim[k], cites, group, title, label, order, headline))

n = write(BATCH, records, claims)
print(n, "records;", sum(r["kind"] == "result" for r in records), "results")
