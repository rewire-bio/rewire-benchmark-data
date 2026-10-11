"""GFMBench-API (Larey et al., bioRxiv 10.64898/2026.02.19.706811 v2): appendix Tables 1-5 from the PDF text layer.

Usage: python3 -I extract_gfmbench.py <paper.pdf> <pdftotext -layout output> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256

pdf, txt, folder = sys.argv[1:4]
SHA = sha256(pdf)
assert SHA == "df9934c88ee245b1e19e155174169d6b6da57ae07c1a04bbea7115423facdf72", SHA
URL = "https://www.biorxiv.org/content/10.64898/2026.02.19.706811v2.full.pdf"
lines = open(txt).read().split("\n")

b = Batch(folder, "lit-genomics-20261011-gfmbench")
SRC = b.source("lit-genomics-20261011-gfmbench-source-larey2026", "GFMBench-API: A Standardized Interface for Benchmarking Genomic Foundation Models", {
    "url": "https://doi.org/10.64898/2026.02.19.706811", "artifact_url": URL,
    "version": "bioRxiv preprint version 2, posted 2026-08-11", "retrieved_at": "2026-10-11T00:44:58Z", "artifact_sha256": SHA,
    "doi": "10.64898/2026.02.19.706811", "publication_status": "preprint", "licence": "CC-BY-4.0", "media_type": "application/pdf",
    "limitations": ["Preprint, not peer reviewed.", "Authors are at NVIDIA, which distributes the BioNeMo implementation of Evo2 used here; no model in the tables was developed by the authors."]})
SIDS = [SRC]
REV = lambda loc: extraction_review(["pdf-text-parse"], "Parsed the pdftotext -layout text of the pinned PDF with tools/extract_gfmbench.py: model rows matched by name, task labels assigned to fixed blocks of model rows in printed order, block and row counts asserted. " + loc, SHA, URL)

MODELS = {  # label -> (family id, configuration parameters)
    "DNA-BERT": (None, "About 110M parameters; Hugging Face checkpoint"),
    "DNABERT-2": ("discovery-model-dnabert-2", "About 117M parameters; Hugging Face checkpoint"),
    # Family record added by the GUANinE batch (lit-genomics-20261011-guanine), which must be added to the store first.
    "NTv3": ("lit-genomics-20261011-guanine-model-nucleotide-transformer-v3", "Nucleotide Transformer v3, about 8M parameters; Hugging Face checkpoint"),
    "Caduceus-Ps": ("regulatory-variant-20261009-model-caduceus", "About 7M parameters; Hugging Face checkpoint"),
    "Evo2": ("discovery-model-evo-2", "1B parameters; NVIDIA BioNeMo implementation"),
}
NEW = {"DNA-BERT": ("DNABERT", "DNABERT (first version) k-mer DNA language model.")}
fam = {}
def family(m):
    f = MODELS[m][0]
    if f:
        return f
    if m not in fam:
        name, desc = NEW[m]
        fam[m] = b.entity("model", b.rid("model", name), name, desc, SIDS,
                          {"reported_name": m, "entity_level": "family", "source_locator": "Benchmark Results section A 'Model Sourcing and Implementation'",
                           "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}, method_types=["foundation_model"])
    return fam[m]

cfgs = {}
def config(m, mode):
    k = (m, mode)
    if k not in cfgs:
        cfgs[k] = b.entity("configuration", b.rid("config", m, mode), f"{m} ({mode}, GFMBench-API)", f"{m} as evaluated in GFMBench-API, {mode}.", SIDS,
                           {"reported_name": m, "foundation_model_eligible": True, "parameters": MODELS[m][1] + f"; {mode}" + ("; full fine-tuning for 3 epochs" if mode == "full fine-tuning" else ("; frozen weights, linear classification head" if mode == "linear probing" else "")),
                            "access_reuse": "Public checkpoint (Hugging Face; Evo2 via NVIDIA BioNeMo)", "source_locator": "Benchmark Results sections A and B",
                            "missing_metadata": {"version": {"reason": "unreported", "note": "Checkpoint revision not printed; parameter count only"}}},
                           method_types=["foundation_model"], links=[{"relation": "configuration_of", "target_id": family(m)}])
    return cfgs[k]

BENCH = b.entity("benchmark", b.rid("benchmark", "gfmbench-api"), "GFMBench-API",
    "Python interface that wraps existing genomic tasks (GUE, VariantBenchmarks, LRB, BEND, TraitGym, SongLab ClinVar, BRCA1, VEP-eval, LOL-EVE) and a new ClinVar indel task behind one evaluation API.",
    SIDS, {"entity_level": "suite", "version": "Preprint v2 (2026-08-11)", "task": "Supervised classification and zero-shot variant effect prediction on DNA sequence",
           "scope_note": "Tasks are re-implementations of existing benchmarks with some changes, for example fixed test folds instead of cross-validation for VariantBenchmarks.",
           "source_locator": "Technical Methods; Appendix task descriptions; Tables 1-5"})

protos, datas = {}, {}
def task(name, kind):
    k = (name, kind)
    if k in protos:
        return protos[k], datas[name]
    if name not in datas:
        datas[name] = b.entity("dataset", b.rid("data", name), f"{name} test set (GFMBench-API)", f"{name} evaluation data as packaged in GFMBench-API.", SIDS,
                               {"split": "Test split as defined in GFMBench-API", "source_locator": "Appendix task descriptions",
                                "missing_metadata": {"version": {"reason": "unreported"}}})
    desc = {"supervised": "supervised classification; Accuracy, MCC, AUROC and AUPRC on the test set",
            "zs-embedding": "zero-shot; reference and alternate sequence embeddings compared by cosine similarity or L2 distance, scored by AUROC and AUPRC",
            "zs-mlm-llr": "zero-shot; masked log-likelihood ratio of alternate versus reference, scored by AUROC and AUPRC",
            "zs-ar-llr": "zero-shot; autoregressive log-likelihood ratio over mean predicted token probabilities, scored by AUROC and AUPRC"}[kind]
    protos[k] = b.entity("protocol", b.rid("protocol", name, kind), f"GFMBench-API {name}, {kind}", f"GFMBench-API task {name}: {desc}.", SIDS,
                         {"protocol": desc, "version": "GFMBench-API preprint v2",
                          "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
                          "limitations": ["Single run per cell; no uncertainty printed.", "The task re-implements an earlier benchmark and may not match the original split or scoring."]
                                         + (["Supervised protocols hold both the Table 1 full fine-tuning rows and the Table 2 Evo2 linear-probing rows; comparison.adaptation separates them."] if kind == "supervised" else []),
                          "source_locator": "Appendix Tables 1-5; task descriptions"},
                         links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": datas[name]}])
    return protos[k], datas[name]

def table_lines(start_pat, end_pat):
    s = next(i for i, l in enumerate(lines) if re.search(start_pat, l))
    e = next(i for i in range(s + 1, len(lines)) if re.search(end_pat, lines[i]))
    return lines[s:e]

NUM = r"(?:−?\d+\.\d+|0|NA)"
MODEL_RE = r"(DNA-BERT|DNABERT-2|NTv3|Caduceus-Ps|Evo2)"
def parse_blocks(seg, ncols, models_per_block, tasks_expected):
    model_rows, tasks = [], []
    for l in seg:
        m = re.match(r"^\s*(.*?)\s+" + MODEL_RE + r"\s+((?:" + NUM + r"\s+){" + str(ncols - 1) + r"}" + NUM + r")\s*$", l) or \
            re.match(r"^\s*()" + MODEL_RE + r"\s+((?:" + NUM + r"\s+){" + str(ncols - 1) + r"}" + NUM + r")\s*$", l)
        if m:
            if m.group(1).strip():
                tasks.append(m.group(1).strip())
            model_rows.append((m.group(2), m.group(3).split()))
        else:
            t = l.strip()
            if t and not re.match(r"^(Task|Table|AUROC|cient|L2 Distance|predicted|Larey|bioR|\(which|available|\d+\s+\|)", t) and "Model" not in t:
                tasks.append(t)
    assert len(model_rows) == models_per_block * len(tasks_expected), (len(model_rows), tasks)
    assert tasks == tasks_expected, tasks
    for i, t in enumerate(tasks):
        for m, vals in model_rows[i * models_per_block:(i + 1) * models_per_block]:
            yield t, m, vals

def emit(table, t, m, mode, kind, cols, vals, metric_map):
    p, d = task(t, kind)
    c = config(m, mode)
    ev = b.rid("eval", m, mode, t, kind)
    if ev not in b.ids:
        b.evaluation(ev, f"{m} on GFMBench-API {t} ({kind})", SIDS, c, p, d, "independent_paper",
                     {"protocol_id": p, "dataset_version": None, "split": "Test split", "population": None, "inputs": "DNA sequence windows; task-specific context length",
                      "adaptation": mode, "metric_implementation": "GFMBench-API task metrics", "aggregation": None, "budget": None}, f"{table}, task '{t}', model '{m}'")
    for col, v in zip(cols, vals):
        metric, q = metric_map[col]
        loc = f"{table}, task '{t}', row '{m}', column '{col}'"
        printed = v
        if v == "NA":
            # Printed NA: SNV metrics do not apply to indel tasks (Table 3 caption); not a measurement, so not recorded.
            continue
        anomaly = None
        if m == "Caduceus-Ps" and t == "Songlab ClinVar" and kind == "zs-embedding":
            anomaly = ("Caduceus-Ps on Songlab ClinVar prints AUROCs of 0.9333 and 0.8667 (14/15 and 13/15) with AUPRC about 0.99, while the other four models score "
                       "0.50-0.84 on the same task. This looks like a very small or failed evaluation subset; do not compare this cell with the other rows.")
        b.result(b.rid("result", m, mode, t, kind, col), f"{m} {t} {col}", SRC, SIDS, ev, printed, metric, "higher", "unitless", loc, REV(loc), qualifier=q,
                 numeric=v.replace("−", "-"), extra={"source_anomaly": anomaly} if anomaly else None)

T1_TASKS = ["GUE Transcription Factor", "GUE Promoter All", "GUE Splice Site", "Var Bench Coding Pathogenicity", "Var Bench Non Coding Pathogenicity",
            "Var Bench Expression", "Var Bench Common Vs Rare", "Var Bench meQTL", "Var Bench sQTL", "LRB Variant Effect Causal eQTL"]
SUP = {"Accuracy": ("accuracy", "test set"), "MCC": ("matthews-correlation-coefficient", "test set"), "AUROC": ("auroc", "test set"), "AUPRC": ("auprc", "test set")}
seg = table_lines(r"^Table 1\. Supervised", r"^Table 2\. Supervised")
n = 0
for t, m, vals in parse_blocks(seg, 4, 4, T1_TASKS):
    emit("Table 1", t, m, "full fine-tuning", "supervised", ["Accuracy", "MCC", "AUROC", "AUPRC"], vals, SUP); n += 1
assert n == 40

seg = table_lines(r"^Table 2\. Supervised", r"^\s*Larey et al\.")
rows2 = []
for l in seg:
    mm = re.match(r"^\s*(.+?)\s{2,}((?:" + NUM + r"\s+){3}" + NUM + r")\s*$", l)
    if mm:
        rows2.append((mm.group(1).strip(), mm.group(2).split()))
assert [r[0] for r in rows2] == [t for t in T1_TASKS if t != "Var Bench sQTL"], rows2
for t, vals in rows2:
    emit("Table 2", t, "Evo2", "linear probing", "supervised", ["Accuracy", "MCC", "AUROC", "AUPRC"], vals, SUP)

T3_TASKS = ["Bend Variant Effects Disease", "Bend Variant Effects Expression", "Songlab ClinVar", "TraitGym Complex", "TraitGym Mendelian",
            "LRB Variant Effect OMIM", "BRCA1", "VEP-eval", "ClinVar Indel Pathogenicity", "LOL-EVE"]
EMB = {"Cos AUROC": ("auroc", "zero-shot; cosine similarity of reference and alternate sequence embeddings"),
       "Cos AUPRC": ("auprc", "zero-shot; cosine similarity of reference and alternate sequence embeddings"),
       "L2 AUROC": ("auroc", "zero-shot; L2 distance of reference and alternate sequence embeddings"),
       "L2 AUPRC": ("auprc", "zero-shot; L2 distance of reference and alternate sequence embeddings"),
       "SNV Cos AUROC": ("auroc", "zero-shot; cosine similarity of embeddings at the SNV position"),
       "SNV Cos AUPRC": ("auprc", "zero-shot; cosine similarity of embeddings at the SNV position")}
seg = table_lines(r"^Table 3\. Zero-Shot Embedding", r"^12\s+\|")
# VEP-eval prints four models (no Evo2); every other task prints five.
model_rows, tasks = [], []
for l in seg:
    m = re.match(r"^\s*(.*?)\s+" + MODEL_RE + r"\s+((?:" + NUM + r"\s+){5}" + NUM + r")\s*$", l) or re.match(r"^\s*()" + MODEL_RE + r"\s+((?:" + NUM + r"\s+){5}" + NUM + r")\s*$", l)
    if m:
        model_rows.append((m.group(1).strip(), m.group(2), m.group(3).split()))
cur, k, out = None, 0, []
sizes = [5, 5, 5, 5, 5, 5, 5, 4, 5, 5]
assert len(model_rows) == sum(sizes), len(model_rows)
for t, size in zip(T3_TASKS, sizes):
    block = model_rows[k:k + size]; k += size
    labels = [r[0] for r in block if r[0]]
    assert labels == [t], (t, labels)
    for _, m, vals in block:
        emit("Table 3", t, m, "zero-shot", "zs-embedding", list(EMB), vals, EMB)

T4_TASKS = ["Bend Variant Effects Disease", "Bend Variant Effects Expression", "Songlab ClinVar", "TraitGym Complex", "TraitGym Mendelian", "LRB Variant Effect OMIM", "VEP-eval", "BRCA1"]
LLR = {"Msk LLR ROC": ("auroc", "zero-shot; masked log-likelihood ratio"), "Msk LLR PRC": ("auprc", "zero-shot; masked log-likelihood ratio")}
seg = table_lines(r"Table 4\. Zero-Shot Likelihood", r"^Table 5\.")
for t, m, vals in parse_blocks(seg, 2, 4, T4_TASKS):
    emit("Table 4", t, m, "zero-shot", "zs-mlm-llr", list(LLR), vals, LLR)

AR = {"Mean LLR ROC": ("auroc", "zero-shot; autoregressive log-likelihood ratio over mean token probabilities"), "Mean LLR PRC": ("auprc", "zero-shot; autoregressive log-likelihood ratio over mean token probabilities")}
seg = table_lines(r"^Table 5\. Zero-Shot Likelihood", r"^\s*Larey et al\.")
rows5 = []
for l in seg:
    mm = re.match(r"^\s*(.+?)\s{2,}(" + NUM + r")\s+(" + NUM + r")\s*$", l)
    if mm:
        rows5.append((mm.group(1).strip(), [mm.group(2), mm.group(3)]))
assert [r[0] for r in rows5] == ["Bend Variant Effects Disease", "Bend Variant Effects Expression", "Songlab ClinVar", "TraitGym Complex", "TraitGym Mendelian", "LRB Variant Effect OMIM", "BRCA1", "ClinVar Indel Pathogenicity", "LOL-EVE"], rows5
for t, vals in rows5:
    emit("Table 5", t, "Evo2", "zero-shot", "zs-ar-llr", list(AR), vals, AR)

print(json.dumps(b.write()))
