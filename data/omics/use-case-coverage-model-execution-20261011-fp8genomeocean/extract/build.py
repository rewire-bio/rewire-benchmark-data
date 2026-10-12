"""Build batch.jsonl for Yu et al. 2026 (FP8 inference on GenomeOcean), Tables 3 and 4.

Usage: python3 -I build.py <preprint.pdf>

Both tables are parsed from the `pdftotext -layout` text of the pinned bioRxiv PDF with row labels and
column counts asserted. bioRxiv stamps each download, so the PDF bytes differ between retrievals; the
script checks the SHA-256 of the text layer, which was identical across two downloads.
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
PDF_SHA = "ca54817d1f1a308f09bd3022e56cf6f8b86a875b110da0a38fe31236e39ca076"
TEXT_SHA = "bec6e695ce46c4ebd6692e01a1a93167e212dffbb97b6558f1da88b1eb453501"
SRC = P + "source-yu2026-fp8-genomeocean"
SOURCES = [SRC]
FAMILY = "lit-genomics-20261011-geneb-model-genomeocean"

pdf = sys.argv[1]
text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
assert hashlib.sha256(text.encode()).hexdigest() == TEXT_SHA, "text layer differs from the pinned retrieval"

records, claims = [], []
src = source(SRC, "FP8 Inference in Genomic Foundation Models: Theoretical vs. Realized Speedups on GenomeOcean",
             "https://doi.org/10.64898/2026.08.09.743676",
             "https://www.biorxiv.org/content/10.64898/2026.08.09.743676v1.full.pdf",
             "bioRxiv preprint version 1, posted 2026-08-14 (PDF footer); bioRxiv API date 2026-08-18", "2026-10-11T21:42:49Z",
             PDF_SHA, "10.64898/2026.08.09.743676", "preprint", "CC-BY-4.0", "application/pdf",
             "Preprint retrieved and hashed for the diagnostic genomics execution literature pass (2026-10-11).")
src["attributes"]["hash_scope"] = (
    "bioRxiv stamps each PDF download, so artifact_sha256 describes one retrieval (a second download differed in 40 bytes). "
    f"The pdftotext -layout text layer (poppler) of both downloads has SHA-256 {TEXT_SHA}.")
records.append(src)

FAC = {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["foundation_model"]}
HW = {"description": "One NVIDIA H100 SXM5 GPU, 80 GB HBM3 (Section 2.2)"}
CFG = {}
def config(key, size, precision, engine, note):
    cid = f"{P}config-yu2026-genomeocean-{size.lower()}-{key}"
    CFG[(size, key)] = cid
    records.append(entity(cid, "configuration", f"GenomeOcean-{size}, {precision}, {engine} (Yu et al. 2026)", note, SOURCES,
                          {"reported_name": f"{size} {precision}", "foundation_model_eligible": True, "version": f"GenomeOcean-{size}",
                           "parameters": {"100M": "100M parameters", "500M": "500M parameters", "4B": "4B parameters"}[size],
                           "access_reuse": "Checkpoint release not stated in this source; benchmarking code at https://github.com/jgi-genomeocean/genomeocean_efficiency (not pinned)",
                           "hardware": HW, "protocol": note,
                           "source_locator": "Sections 2.1-2.4; Table 1; Table 2"},
                          [("configuration_of", FAMILY)], facets=FAC))
for size in ("100M", "500M", "4B"):
    config("bf16-embedding", size, "BF16", "PyTorch embedding extraction", "Protocol A baseline: BF16 weights, single causal forward pass, mean-pooled final-layer hidden states.")
    config("fp8-weights-embedding", size, "FP8 (E4M3) static weights", "PyTorch with FBGEMM", "Protocol A: static FP8 E4M3 weight quantization with FBGEMM kernels; output embeddings in BF16; no calibration fine-tuning.")
config("bf16-vllm", "4B", "BF16", "vLLM generation", "Protocol B baseline: BF16 autoregressive generation in vLLM.")
config("fp8-kv-vllm", "4B", "FP8 KV cache", "vLLM generation", "Protocol B.1: FP8 E4M3 KV cache with dynamic per-tensor scaling; weights and activations BF16.")
config("w8a8-fp8-kv-vllm", "4B", "W8A8 plus FP8 KV cache", "vLLM generation", "Protocol B.2: FP8 KV cache plus FP8 weights (static) and activations (dynamic); lm_head stays BF16.")

DA = P + "data-yu2026-gtdb-binning"
DB = P + "data-yu2026-gtdb-bacteria-96"
records += [
    entity(DA, "dataset", "GTDB genome fragments for metagenomic binning, 20 of a pre-sampled pool of 50 bacterial genomes per trial (Yu et al. 2026)",
           "Fragments of about one million tokens per genome: 5,000 bp for the 100M and 500M models and 50,000 bp for the 4B model.", SOURCES,
           {"population": "20 genomes per trial sampled from a pool of 50 GTDB bacterial genomes; a representative 20-genome sample is listed in Table 5",
            "split": "Five trials with random seeds 42-46", "source_locator": "Section 2.5 'Metagenomic binning (Protocol A)'; Section 2.7; Table 5",
            "missing_metadata": {"version": {"reason": "unreported", "note": "GTDB release not stated"}}}),
    entity(DB, "dataset", "96 GTDB Bacteria genome sequences bounded to 102,400 tokens (Yu et al. 2026)",
           "Fixed sequence set for sliding-window perplexity and generation benchmarks.", SOURCES,
           {"population": "96 microbial genome sequences sampled from GTDB Bacteria", "split": "Fixed set; throughput, power and efficiency over five trials",
            "source_locator": "Section 2.5 'GTDB Bacteria sequence likelihood (Protocol B)'; Section 2.7",
            "missing_metadata": {"version": {"reason": "unreported", "note": "GTDB release not stated"}}}),
]

PA = P + "protocol-yu2026-genomeocean-embedding-fp8"
PB = P + "protocol-yu2026-genomeocean-generation-fp8"
LIM_A = ["Author-reported: two authors are at the DOE Joint Genome Institute, which develops GenomeOcean; no competing-interest statement is printed.",
         "Microbial genomes and a metagenomic-binning fidelity check, not human diagnostic sequence; the paper says the fidelity metrics are benchmark-specific (Section 4.4).",
         "Throughput is measured at one fixed batch size per model scale, which is not printed.",
         "Peak VRAM is printed without spread; throughput and ARI are mean and standard deviation over five trials.",
         "One GPU type (H100 SXM5); the paper says results for other GPUs and engines need their own evaluation."]
LIM_B = [LIM_A[0], "Microbial genomes (96 GTDB Bacteria sequences) and a perplexity check, not human diagnostic sequence; the paper says perplexity measures sequence-likelihood preservation, not the biological function of generated sequences (Section 4.4).",
         "Throughput, power and efficiency are mean and standard deviation over five trials; perplexity standard deviation reflects sequence-level heterogeneity across 96 fixed sequences, not trial-to-trial variation.",
         "Generation and embedding use different engines, so their absolute throughputs are not comparable (Section 2.4).",
         "Peak memory for generation is not printed in Table 4.", LIM_A[4]]
records += [
    entity(PA, "protocol", "GenomeOcean embedding extraction throughput, peak VRAM and binning fidelity, BF16 versus FP8 weights (Yu et al. 2026 Table 3)",
           "Embedding extraction on one H100 at three model scales with BF16 and FP8 weights.", SOURCES,
           {"protocol": "Single causal forward pass over batched tokenized fragments; final-layer states mean-pooled. Throughput in input tokens per second at a fixed batch size per scale; peak memory from torch.cuda.max_memory_allocated(); embeddings clustered with DBSCAN (hyperparameters tuned on BF16) and scored by ARI against species labels.",
            "version": "Table 3", "metric": "inference-throughput", "limitations": LIM_A,
            "memory_measurement": "torch.cuda.max_memory_allocated() (Section 2.6)", "random_seeds": "42-46",
            "source_locator": "Sections 2.3-2.7; Table 3"},
           [("uses_data", DA)]),
    entity(PB, "protocol", "GenomeOcean-4B autoregressive generation throughput, power, energy efficiency and perplexity, BF16 versus FP8 (Yu et al. 2026 Table 4)",
           "Autoregressive generation in vLLM on one H100 with three precision configurations.", SOURCES,
           {"protocol": "Token-by-token generation with vLLM; throughput in generated tokens per second; GPU power from NVML at 100 ms intervals, efficiency as throughput per mean watt; sliding-window perplexity with 10,240-token context and 2,560-token stride on 96 GTDB sequences.",
            "version": "Table 4", "metric": "inference-throughput", "limitations": LIM_B, "random_seeds": "42-46",
            "source_locator": "Sections 2.3-2.7; Table 4"},
           [("uses_data", DB)]),
]

def evaluation(cid, pid, did, label, locator, split):
    eid = cid.replace("-config-", "-eval-")
    records.append(entity(eid, "evaluation", label, "Published inference benchmark; transcribed, not reproduced.", SOURCES,
                          {"origin": "author_reported", "protocol": pid, "version": "Primary source as retrieved 2026-10-11",
                           "comparison": {"protocol_id": pid, "dataset_version": None, "split": split,
                                          "population": "GTDB bacterial genomes", "inputs": "Tokenized DNA sequence",
                                          "adaptation": "None (pretrained checkpoint, post-training quantization only)",
                                          "metric_implementation": None, "aggregation": "Mean and standard deviation over five trials",
                                          "budget": "One NVIDIA H100 SXM5 80 GB GPU"},
                           "source_locator": locator,
                           "missing_metadata": {"comparison.dataset_version": {"reason": "unreported"}, "comparison.metric_implementation": {"reason": "unreported", "note": "Batch sizes not printed"}}},
                          [("system", cid), ("assessment", pid), ("data", did)]))
    return eid

REV = extraction_review(["pdf-text-parse"],
    "Deterministic parse of `pdftotext -layout` text of the pinned preprint PDF (extract/build.py), with row labels, precision labels and column counts asserted.",
    "Extraction only; pending independent review.")
MINUS = lambda s: s.replace("−", "-")

def sd(printed_sd, n, scope):
    return {"type": "standard_deviation", "value": printed_sd.replace(",", ""), "printed": "± " + printed_sd, "n": n, "scope": scope}

def add(eid, rid, name, metric, direction, unit, printed, numeric, qualifier, locator, detail=None, unc=None, missing=None):
    records.append(result(rid, name, SOURCES, eid, metric, direction, unit, printed, numeric, locator, REV,
                          qualifier=qualifier, unit_detail=detail, uncertainty=unc, missing=missing))
    claims.append((rid, SRC, locator, printed, "pdf-text-layer"))

# Table 3.
t3 = text[text.index("Table 3: Protocol A embedding extraction"):]
t3 = t3[:t3.index("BF16, improves throughput")]
rows = re.findall(r"^\s*(100M|500M|4B)\s+(BF16|FP8 \(E4M3\))\s+([\d,]+) ± ([\d,]+)\s+(\S+)\s+([\d.]+)\s+([\d.]+) ± ([\d.]+)\s*$", t3, re.M)
assert [(r[0], r[1]) for r in rows] == [(s, p) for s in ("100M", "500M", "4B") for p in ("BF16", "FP8 (E4M3)")], rows
FIVE = "Five trials with random seeds 42-46"
for size, prec, thr, thr_sd, change, vram, ari, ari_sd in rows:
    key = "bf16-embedding" if prec == "BF16" else "fp8-weights-embedding"
    cid = CFG[(size, key)]
    eid = evaluation(cid, PA, DA, f"GenomeOcean-{size} {prec} embedding extraction (Yu et al. 2026)", f"Table 3 row '{size} {prec}'", "Five trials, seeds 42-46")
    base = eid.replace("-eval-", "-result-")
    loc = lambda col: f"Table 3, row Model '{size}', Precision '{prec}', column '{col}'"
    add(eid, base + "-throughput", f"yu2026 GenomeOcean-{size} {prec} embedding throughput", "inference-throughput", "higher", "sample-per-second",
        f"{thr} ± {thr_sd}", thr.replace(",", ""), "Embedding extraction; input tokens per second", loc("Throughput (tok/s)"),
        "tokens per second (input tokens), printed tok/s", sd(thr_sd, 5, FIVE))
    if change != "–":
        add(eid, base + "-throughput-change", f"yu2026 GenomeOcean-{size} {prec} throughput change", "throughput-change", "higher", "percent",
            change, MINUS(change).rstrip("%").lstrip("+"), "Embedding extraction; relative to the BF16 baseline of the same model scale", loc("Change"))
    else:
        assert prec == "BF16"
    add(eid, base + "-peak-vram", f"yu2026 GenomeOcean-{size} {prec} peak VRAM", "peak-memory", "lower", "gigabyte", vram, vram,
        "Embedding extraction; peak GPU memory allocated", loc("Peak VRAM (GB)"), "GB as printed; torch.cuda.max_memory_allocated()")
    add(eid, base + "-ari", f"yu2026 GenomeOcean-{size} {prec} DBSCAN ARI", "adjusted-rand-index", "higher", "unitless",
        f"{ari} ± {ari_sd}", ari, "DBSCAN clustering of embeddings against GTDB species labels", loc("DBSCAN ARI"), None, sd(ari_sd, 5, FIVE))

# Table 4.
t4 = text[text.index("Table 4: Protocol B generation benchmarks"):]
t4 = t4[:t4.index("3.3 Autoregressive Decoding")]
rows = re.findall(r"^\s*(Baseline|B\.1|B\.2)\s+(BF16|FP8 KV-Cache|W8A8 \+ FP8 KV-Cache)\s+([\d.]+) ± ([\d.]+)\s+([\d.]+) ± ([\d.]+)\s+([\d.]+) ± ([\d.]+)\s+([\d.]+) ± ([\d.]+)\s*$", t4, re.M)
assert [r[0] for r in rows] == ["Baseline", "B.1", "B.2"], rows
KEY = {"Baseline": "bf16-vllm", "B.1": "fp8-kv-vllm", "B.2": "w8a8-fp8-kv-vllm"}
for proto, scheme, thr, thr_sd, pw, pw_sd, eff, eff_sd, ppl, ppl_sd in rows:
    cid = CFG[("4B", KEY[proto])]
    eid = evaluation(cid, PB, DB, f"GenomeOcean-4B {scheme} generation (Yu et al. 2026)", f"Table 4 row '{proto} {scheme}'", "Five trials, seeds 42-46; perplexity on 96 fixed sequences")
    base = eid.replace("-eval-", "-result-")
    loc = lambda col: f"Table 4, row Protocol '{proto}', Quantization Scheme '{scheme}', column '{col}'"
    add(eid, base + "-throughput", f"yu2026 GenomeOcean-4B {scheme} generation throughput", "inference-throughput", "higher", "sample-per-second",
        f"{thr} ± {thr_sd}", thr, "Autoregressive generation; generated tokens per second", loc("Throughput (tok/s)"),
        "tokens per second (generated tokens), printed tok/s", sd(thr_sd, 5, FIVE))
    add(eid, base + "-power", f"yu2026 GenomeOcean-4B {scheme} power", "power-draw", "lower", "watt", f"{pw} ± {pw_sd}", pw,
        "Autoregressive generation; mean steady-state GPU power from NVML", loc("Power (W)"), None, sd(pw_sd, 5, FIVE))
    add(eid, base + "-efficiency", f"yu2026 GenomeOcean-4B {scheme} energy efficiency", "energy-efficiency", "higher", "sample-per-joule",
        f"{eff} ± {eff_sd}", eff, "Autoregressive generation; generated tokens per second per watt", loc("Efficiency (tok/W)"),
        "tokens per second per watt, printed tok/W", sd(eff_sd, 5, FIVE))
    add(eid, base + "-perplexity", f"yu2026 GenomeOcean-4B {scheme} perplexity", "perplexity", "lower", "unitless", f"{ppl} ± {ppl_sd}", ppl,
        "Sliding-window perplexity on 96 GTDB Bacteria sequences (10,240-token context, 2,560-token stride)", loc("Perplexity (± SD)"), None,
        sd(ppl_sd, 96, "Standard deviation across 96 fixed sequences (sequence-level heterogeneity, not trial-to-trial variation)"))

CONSTRAINTS = ["Inspect every linked evaluation's source locator before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; hardware, inputs, software versions and timing boundaries differ between sources."]
cites = [{"source_id": SRC, "locator": "Sections 2.2-2.7; Tables 3 and 4; Funding Statement and Author Contributions"}]
records.append(judgement("use-case-mapping-model-execution-20261011-yu2026-genomeocean-embedding-fp8", PA,
    "GenomeOcean embedding extraction throughput and peak VRAM, BF16 versus FP8 (Yu et al. 2026)", SOURCES, "proxy",
    "Embedding throughput (tokens per second, mean and SD over five trials), peak GPU memory and binning ARI for GenomeOcean-100M, -500M and -4B in BF16 and FP8 on one H100",
    "Measures inference throughput and peak GPU memory of a genomic foundation model at three sizes and two precisions on stated hardware, with spread over five trials, which no previously linked source does. Proxy: microbial genomes rather than diagnostic human data, an embedding workload rather than a diagnostic pipeline, and author-reported by the model's developing institute.",
    CONSTRAINTS, LIM_A, cites, "yu2026-genomeocean-fp8", "GenomeOcean inference on one H100, BF16 versus FP8 (Yu et al. 2026)", "Embedding extraction", 1, "inference-throughput"))
records.append(judgement("use-case-mapping-model-execution-20261011-yu2026-genomeocean-generation-fp8", PB,
    "GenomeOcean-4B generation throughput, power and energy efficiency, BF16 versus FP8 (Yu et al. 2026)", SOURCES, "proxy",
    "Generation throughput, GPU power and tokens per watt (mean and SD over five trials) and perplexity for GenomeOcean-4B with BF16, FP8 KV cache and W8A8 plus FP8 KV cache in vLLM on one H100",
    "Measures generation throughput, power draw and energy efficiency of a genomic foundation model under three precision settings on stated hardware. Proxy: sequence generation is not a diagnostic workflow step, the sequences are microbial, and the study is author-reported.",
    CONSTRAINTS, LIM_B, cites, "yu2026-genomeocean-fp8", "GenomeOcean inference on one H100, BF16 versus FP8 (Yu et al. 2026)", "Generation (4B)", 2, "inference-throughput"))

n = write(BATCH, records, claims)
print(n, "records;", sum(r["kind"] == "result" for r in records), "results")
