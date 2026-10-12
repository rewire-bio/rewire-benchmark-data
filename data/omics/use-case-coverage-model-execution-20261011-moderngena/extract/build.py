"""Build batch.jsonl for Aspidova et al. 2026 (ModernGENA), Appendix B Table 2 (inference efficiency).

Usage: python3 -I build.py <preprint.pdf>

Parsed from the `pdftotext -layout` text of the pinned bioRxiv PDF with model labels, sequence lengths and
cell counts asserted. bioRxiv stamps each download, so the text layer hash is checked as well as the bytes.
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
PDF_SHA = "238ab9916d54b419bf31fd79ecf146d654eb6574d3b441aa2043d39632e709fa"
TEXT_SHA = "ebaf0541c173359940737efde2c15d4ab4aa37d7cc323b3922a818feb5be6b4b"
SRC = P + "source-aspidova2026-moderngena"
SOURCES = [SRC]

pdf = sys.argv[1]
assert hashlib.sha256(open(pdf, "rb").read()).hexdigest() == PDF_SHA, "PDF differs from the pinned retrieval"
text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
assert hashlib.sha256(text.encode()).hexdigest() == TEXT_SHA

records, claims = [], []
src = source(SRC, "Back to BERT in 2026: ModernGENA as a Strong, Efficient Baseline for DNA Foundation Models",
             "https://doi.org/10.64898/2026.04.21.719816",
             "https://www.biorxiv.org/content/10.64898/2026.04.21.719816v1.full.pdf",
             "bioRxiv preprint version 1, posted 2026-04-23", "2026-10-11T21:39:38Z",
             PDF_SHA, "10.64898/2026.04.21.719816", "preprint", "CC-BY-4.0", "application/pdf",
             "Preprint retrieved and hashed for the diagnostic genomics execution literature pass (2026-10-11).")
src["attributes"]["hash_scope"] = ("bioRxiv stamps each PDF download, so artifact_sha256 describes one retrieval; retrieved_at is the file's "
                                   f"modification time. The pdftotext -layout text layer has SHA-256 {TEXT_SHA}. A second download "
                                   "at 21:43Z was refused with HTTP 429.")
src["attributes"]["evidence_concerns"] = [{
    "source_id": SRC,
    "message": "Appendix B Table 2 and Figure 1 (axis 'Inference speed (tokens/s)') give throughput in tokens/s, but the printed values are inconsistent with the printed batch sizes: ModernGENA base (FA2 + autocast bf16) at L = 256 prints 552.44 tokens/s with a batch of 3,631 sequences (929,536 tokens), about 28 minutes per batch, and ModernGENA base without FA2 at L = 8192 prints 71.15 tokens/s with a batch of 92 (753,664 tokens), about 2.9 hours per batch, against a stated pretraining throughput of 1.33M tokens/s on eight A100 GPUs (Section 3.2.4). The unit or scale of the throughput column is unclear. Batch sizes share the table. Values are recorded as printed.",
    "source_locator": "Appendix B Table 2 (page 9); Figure 1 (page 4); Section 3.2.4",
    "artifact_sha256": "238ab9916d54b419bf31fd79ecf146d654eb6574d3b441aa2043d39632e709fa",
    "reviewed_at": "2026-10-12T07:50:32Z",
    "review_method": "automated-source-review",
}]
records.append(src)

FAC = {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["foundation_model"]}
MG = P + "model-moderngena"
records.append(entity(MG, "model", "ModernGENA", "BERT-style DNA language model built on the ModernBERT backbone with a 32k BPE vocabulary.",
                      SOURCES, {"reported_name": "ModernGENA", "entity_level": "family",
                                "access": "Checkpoints for ModernGENA base and large on Hugging Face (DNA language models collection)",
                                "source_locator": "Abstract; Sections 3.1-3.2; Appendix A Table 1",
                                "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; sizes are on configurations"}}},
                      facets=FAC))
ROWS = [
    ("ModernGENA base (FA2 + autocast bf16) (135M)", "moderngena-base-fa2-bf16", MG, "ModernGENA base", "135M parameters", "FlashAttention 2 with bf16 autocast", "author_reported"),
    ("ModernGENA base (135M)", "moderngena-base", MG, "ModernGENA base", "135M parameters", "Standard inference configuration", "author_reported"),
    ("GENA base (110M)", "gena-base", "regulatory-variant-20261009-model-gena-lm", "GENA-LM base", "110M parameters", "As provided", "author_reported"),
    ("DNABERT-2 (117M)", "dnabert-2", "discovery-model-dnabert-2", "DNABERT-2", "117M parameters", "As provided", "independent_paper"),
    ("NTv2 (100M)", "ntv2-100m", "catalog-model-nt-v2", "Nucleotide Transformer v2 100M", "100M parameters", "As provided", "independent_paper"),
    ("ModernGENA large (FA2 + autocast bf16) (377M)", "moderngena-large-fa2-bf16", MG, "ModernGENA large", "377M parameters", "FlashAttention 2 with bf16 autocast", "author_reported"),
    ("ModernGENA large (377M)", "moderngena-large", MG, "ModernGENA large", "377M parameters", "Standard inference configuration", "author_reported"),
    ("GENA large (336M)", "gena-large", "regulatory-variant-20261009-model-gena-lm", "GENA-LM large", "336M parameters", "As provided", "author_reported"),
    ("NTv2 (250M)", "ntv2-250m", "catalog-model-nt-v2", "Nucleotide Transformer v2 250M", "250M parameters", "As provided", "independent_paper"),
]
LENGTHS = ["256", "512", "1024", "2048", "4096", "8192"]

t = text[text.index("Table 2: Inference efficiency evaluation."):]
t = t[:t.index("A PPENDIX C.")]
assert re.search(r"256\s+512\s+1024\s+2048\s+4096\s+8192", t)

PID = P + "protocol-aspidova2026-a100-inference-throughput"
DID = P + "data-aspidova2026-fixed-length-sequences"
LIM = [
    "Author-reported: the authors develop ModernGENA and GENA-LM; DNABERT-2 and NTv2 were run by them.",
    "The printed tokens/s values are inconsistent with the printed batch sizes and the stated pretraining throughput (1.33M tokens/s on eight A100s, Section 3.2.4); the source carries an evidence concern, and values are kept as printed.",
    "Inputs are fixed-length sequences whose content is not described; throughput does not depend on biology, but the input source is not stated.",
    "Throughput is the mean of 10 timing runs; no spread is printed.",
    "Models tokenize differently (BPE, 6-mer), so the same token length covers different numbers of base pairs.",
    "GENA base and large print no values from 1,024 tokens upwards.",
]
records += [
    entity(DID, "dataset", "Fixed-length token sequences of 256 to 8,192 tokens (Aspidova et al. 2026)", "Inputs for the inference-efficiency benchmark; content not described.",
           SOURCES, {"population": "Fixed-length sequences at L = 256, 512, 1024, 2048, 4096 and 8192 tokens", "split": "Not applicable (timing only)",
                     "source_locator": "Section 3.4; Appendix B",
                     "missing_metadata": {"accession": {"reason": "unreported", "note": "Sequence source not stated"}, "version": {"reason": "unreported"}}}),
    entity(PID, "protocol", "DNA language model inference throughput and maximum batch size on one A100 80 GB by sequence length (Aspidova et al. 2026 Table 2)",
           "Maximum batch size that fits in memory and mean throughput over 10 timing runs for nine encoder configurations.", SOURCES,
           {"protocol": "For each sequence length L, the maximum batch size that fits in memory is found by exponential growth until an error, then binary search; throughput in tokens/s is averaged over 10 timing runs at that batch size on one NVIDIA A100 (80 GB).",
            "version": "Appendix B Table 2", "metric": "inference-throughput", "limitations": LIM,
            "source_locator": "Section 3.4; Appendix B Table 2"},
           [("uses_data", DID)]),
]

REV = extraction_review(["pdf-text-parse"],
    "Deterministic parse of `pdftotext -layout` text of the pinned preprint PDF (extract/build.py), with model labels, the six sequence-length headers and twelve cells per row asserted.",
    "Extraction only; pending independent review.")
lines = {}
for line in t.splitlines():
    for label, *_ in ROWS:
        if line.strip().startswith(label):
            lines[label] = line.strip()[len(label):].split()
assert set(lines) == {r[0] for r in ROWS}, set(lines)
for label, key, model, reported, params, setting, origin in ROWS:
    cells = lines[label]
    assert len(cells) == 12, (label, cells)
    cid = f"{P}config-aspidova2026-{key}"
    cname = {"ntv2-100m": "NTv2 (100M)", "ntv2-250m": "NTv2 (250M)"}.get(key, label.rsplit(' (', 1)[0])  # review M2
    records.append(entity(cid, "configuration", f"{cname} on one A100 80 GB (Aspidova et al. 2026)", setting, SOURCES,
                          {"reported_name": label, "foundation_model_eligible": True, "parameters": params, "version": reported,
                           "hardware": {"description": "One NVIDIA A100 80 GB GPU (Section 3.4)"}, "protocol": setting,
                           "access_reuse": "Public pretrained checkpoint" if model == MG else "Pretrained checkpoint; access not stated in this source", "source_locator": f"Appendix B Table 2 row '{label}'"},
                          [("configuration_of", model)], facets=FAC))
    eid = f"{P}eval-aspidova2026-{key}"
    records.append(entity(eid, "evaluation", f"{label} inference throughput on one A100 (Aspidova et al. 2026)",
                          "Published inference benchmark; transcribed, not reproduced.", SOURCES,
                          {"origin": origin, "protocol": PID, "version": "Primary source as retrieved 2026-10-11",
                           "comparison": {"protocol_id": PID, "dataset_version": None, "split": "Fixed-length inputs, L = 256 to 8192 tokens",
                                          "population": "Fixed-length token sequences", "inputs": "Token sequences",
                                          "adaptation": "None (pretrained encoder, forward pass only)",
                                          "metric_implementation": "Maximum batch size by exponential growth and binary search; mean of 10 timing runs",
                                          "aggregation": "Mean of 10 timing runs per model and length", "budget": "One NVIDIA A100 80 GB GPU"},
                           "source_locator": f"Appendix B Table 2 row '{label}'",
                           "missing_metadata": {"comparison.dataset_version": {"reason": "unreported"}}},
                          [("system", cid), ("assessment", PID), ("data", DID)]))
    for i, L in enumerate(LENGTHS):
        bs, tps = cells[2 * i], cells[2 * i + 1]
        if bs == "–":
            assert tps == "–" and key.startswith("gena-")
            continue
        for col, val, metric, unit, detail, short in (
                ("bs", bs, "maximum-batch-size", "count", "sequences per batch", "max-batch-size"),
                ("tokens/s", tps, "inference-throughput", "sample-per-second", "printed tokens/s; see the protocol limitation on scale", "throughput")):
            rid = f"{P}result-aspidova2026-{key}-l{L}-{short}"
            loc = f"Appendix B Table 2 (page 9), row '{label}', sequence length L = {L}, column '{col}'"
            records.append(result(rid, f"aspidova2026 {label} L={L} {col}", SOURCES, eid, metric, "higher", unit, val, val, loc, REV,
                                  qualifier=f"Encoder forward pass on one A100 80 GB; sequence length {L} tokens", unit_detail=detail,
                                  missing={"reason": "unreported", "note": "Mean of 10 timing runs; spread not printed"} if short == "throughput" else None))
            claims.append((rid, SRC, loc, val, "pdf-text-layer"))

records.append(judgement("use-case-mapping-model-execution-20261011-aspidova2026-a100-inference-throughput", PID,
    "DNA language model inference throughput and maximum batch size on one A100 (Aspidova et al. 2026)", SOURCES, "proxy",
    "Maximum batch size and mean inference throughput by sequence length (256 to 8,192 tokens) for ModernGENA, GENA-LM, DNABERT-2 and NTv2 encoders on one A100 80 GB",
    "Compares the inference throughput and memory-bound batch size of several genomic foundation models on the same stated GPU across input lengths, which bears on whether a team's hardware can run such a model at the needed throughput. Proxy: a timing benchmark of forward passes, not a diagnostic workflow, author-reported for two of the four families, and with a printed throughput unit that is inconsistent with its batch sizes (source evidence concern).",
    ["Inspect every linked evaluation's source locator before citing a result.",
     "Do not combine this mapping's evaluations with any other protocol's results; hardware, inputs, software versions and timing boundaries differ between sources.",
     "Compare throughput only within this table; the printed scale is uncertain."],
    LIM, [{"source_id": SRC, "locator": "Section 3.3-3.4; Appendix B Table 2"}],
    "aspidova2026-a100-inference", "DNA language model inference throughput on one A100 (Aspidova et al. 2026)", None, None, "inference-throughput"))

n = write(BATCH, records, claims)
print(n, "records;", sum(r["kind"] == "result" for r in records), "results")
