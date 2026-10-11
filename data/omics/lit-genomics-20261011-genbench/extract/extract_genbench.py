"""GenBench (Liu et al., arXiv 2406.01627 v2): Tables 3-8 and 10 from the PDF text layer.

Usage: python3 -I extract_genbench.py <paper.pdf> <pdftotext -layout output> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256

pdf, txt, folder = sys.argv[1:4]
SHA = sha256(pdf)
assert SHA == "24105d26b25a6adf7509334b041d44e145d5006dfedf87e812e12138fa154f12", SHA
URL = "https://arxiv.org/pdf/2406.01627v2"
L = open(txt).read().split("\n")

b = Batch(folder, "lit-genomics-20261011-genbench")
SRC = b.source("lit-genomics-20261011-genbench-source-liu2024", "GenBench: A Benchmarking Suite for Systematic Evaluation of Genomic Foundation Models", {
    "url": "https://arxiv.org/abs/2406.01627v2", "artifact_url": URL, "version": "arXiv 2406.01627 version 2",
    "retrieved_at": "2026-10-11T01:42:08Z", "artifact_sha256": SHA, "publication_status": "preprint",
    "missing_metadata": {"licence": {"reason": "unreported", "note": "No licence stated on the PDF; arXiv default distribution licence assumed only for reading; not archived"}},
    "media_type": "application/pdf",
    "limitations": ["Preprint (2024), outside the search window; extracted for the suite completeness check.",
                    "Tables report 'Top-1' scores; the paper does not define Top-1 (for classification it reads as ordinary top-1 accuracy).",
                    "The NeurIPS checklist answers that error bars are reported, but no table prints any.",
                    "Table 3 is called short-range in its caption and long-range in Section 4.2.",
                    "The Table 8 caption names 3 models while the table has 5 columns of models.",
                    "Table 4 rows for multi-dataset tasks are means of the Table 10 dataset rows.",
                    "Many short-range datasets repeat GUE and Genomic Benchmarks tasks under GenBench's own fine-tuning."]})
SIDS = [SRC]
REV = lambda loc: extraction_review(["pdf-text-parse"], "Parsed the pdftotext -layout text of the pinned arXiv PDF with tools/extract_genbench.py; header model names and row labels asserted per table. " + loc, SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "genbench"), "GenBench", "Benchmark suite of short- and long-range genomic tasks for fine-tuned genomic foundation models.", SIDS,
                 {"entity_level": "suite", "version": "arXiv v2", "task": "Genomic sequence classification and regression", "scope_note": "Tables 3-8 and 10.", "source_locator": "Tables 2-10"})
FAM = {"HyenaDNA": "regulatory-variant-20261009-model-hyenadna", "DNABERT": "lit-genomics-20261011-gfmbench-model-dnabert", "DNABERT2": "discovery-model-dnabert-2",
       "GENA-LM": "regulatory-variant-20261009-model-gena-lm", # Table 9: 29 layers, width 1024, 498M parameters is the NT-v2 500M architecture (NT-v1 500M has 24 layers, width 1280).
       "NT": "catalog-model-nt-v2", "Nucleotide Transformer": "catalog-model-nt-v2",
       "Caduceus": "regulatory-variant-20261009-model-caduceus", "SpliceAI": "discovery-model-spliceai"}
PARAMS = {"HyenaDNA": "6.6M", "DNABERT": "86.1M", "DNABERT2": "117M", "GENA-LM": "113M", "NT": "498M", "Nucleotide Transformer": "498M", "Caduceus": "7.9M"}
new = {}
def family(m):
    if m in FAM:
        return FAM[m]
    desc = {"CNN": "Convolutional baseline trained from scratch in GenBench.", "DeepSTARR": "DeepSTARR enhancer activity CNN.", "Orca": "Orca 3D genome structure model."}[m]
    if m not in new:
        new[m] = b.entity("model", b.rid("model", m), m if m != "CNN" else "GenBench CNN baseline", desc, SIDS,
                          {"reported_name": m, "entity_level": "family", "source_locator": "Table captions", "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record"}}},
                          method_types=["supervised_machine_learning"])
    return new[m]
cfgs = {}
def config(m):
    k = "NT" if m == "Nucleotide Transformer" else m
    if k not in cfgs:
        fm = k in PARAMS
        cfgs[k] = b.entity("configuration", b.rid("config", k), f"{k} (GenBench)", f"{k} as fine-tuned in GenBench.", SIDS,
            {"reported_name": m, "foundation_model_eligible": fm, "parameters": (f"{PARAMS[k]} parameters (Table 9); fine-tuned 100 epochs, AdamW, cosine decay" if fm else "Trained for the task"),
             "access_reuse": "Public checkpoint" if fm else "Not stated", "source_locator": "Table 9; table headers",
             "missing_metadata": {"version": {"reason": "unreported", "note": "Checkpoint name not printed; parameter count only"}}},
            method_types=["foundation_model"] if fm else ["supervised_machine_learning"], links=[{"relation": "configuration_of", "target_id": family(m)}])
    return cfgs[k]
protos, datas = {}, {}
# Table 2: task type, training size, testing size, length, as printed.
TABLE2 = {"Mouse Enhancers": ("Binary classification", "968", "242", "500"), "Coding vs Intergenomic": ("Binary classification", "75K", "25K", "500"),
          "Human vs Worm": ("Binary classification", "75K", "25K", "500"), "Human Enhancers Cohn": ("Binary classification", "20K", "7K", "500"),
          "Human Enhancers Ensembl": ("Binary classification", "123K", "3K", "500"), "Human Ensembl Regulatory": ("Multi-class classification", "231K", "57K", "500"),
          "Human Nontata Promoters": ("Binary classification", "27K", "9K", "500"), "Human OCR Ensembl": ("Binary classification", "14K", "35K", "500"),
          "Drosophila Enhancers Prediction": ("Regression", "402K", "41K", "128"), "Human Core Promoter Detection": ("Binary classification", "95K", "12K", "70"),
          "Human Transcription Factor Prediction": ("Binary classification", "128K", "5K", "30"), "Human Promoter Detection": ("Binary classification", "95K", "12K", "70"),
          "Human Splice Site Detection": ("Multi-class classification", "36K", "5K", "80"), "Mouse Transcription Factor Prediction": ("Binary classification", "80K", "10K", "30"),
          "Yeast Epigenetic Marks Prediction": ("Binary classification", "230K", "29K", "128"), "Virus Covid Variant Classification": ("Multi-class classification", "73K", "9K", "256"),
          "Splice Site Prediction": ("Multi-class classification", "146K", "16K", "15K"), "Species Classification": ("Multi-class classification", "1K", "500", "80M"),
          "Promoters Prediction": ("Binary classification", "41K", "12K", "8K"), "Genomic Structure Prediction": ("Regression", "21", "3", "256M"),
          "Bulk RNA Prediction": ("Regression", "23K", "990", "196K")}
def table2_row(key):
    if key.startswith("drosophila"): return "Drosophila Enhancers Prediction"
    if key.startswith("long-splice"): return "Splice Site Prediction"
    if key.startswith("genome-structure"): return "Genomic Structure Prediction"
    if key == "bulk-rna-expression": return "Bulk RNA Prediction"
    base = key.split("-", 1)[1]
    for t in sorted(TABLE2, key=len, reverse=True):
        if base == t or base.startswith(t + "-"):
            return t
    raise KeyError(key)
SAME = {"short-Mouse Enhancers": "reported-dataset-f0bf60a62ad7c3"}
def proto(key, name, metric, unit, loc):
    if key not in protos:
        row = table2_row(key)
        typ, tr, te, ln = TABLE2[row]
        same = SAME.get(key) or ("reported-dataset-8e9488896becd4" if key.startswith("short-Human Core Promoter Detection") else None)
        datas[key] = b.entity("dataset", b.rid("data", key), f"GenBench {name}", f"GenBench dataset {name}: {typ.lower()}, sequence length {ln}.", SIDS,
                              {"population": f"Table 2 row '{row}': {typ}; training size {tr}, testing size {te}, length {ln} (as printed; task-level sizes)",
                               "split": "GenBench train and test split (Table 2)", "source_locator": f"Table 2, row '{row}'", "missing_metadata": {"version": {"reason": "unreported"}}},
                              links=[{"relation": "same_data_as", "target_id": same}] if same else ())
        protos[key] = b.entity("protocol", b.rid("protocol", key), f"GenBench {name}", f"GenBench task {name}.", SIDS,
                               {"protocol": "Fine-tuning per dataset; 'Top-1' score as printed (not defined in the source).", "version": "arXiv v2", "metric": metric, "metric_direction": "higher", "unit": unit,
                                "limitations": ["'Top-1' is not defined in the source; no uncertainty printed."], "source_locator": loc},
                               links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": datas[key]}])
    return protos[key], datas[key]
def cell(table, key, name, model, col, v, metric, direction, unit, q=None, pmetric=None, loc_extra=""):
    p, d = proto(key, name, pmetric or metric, unit, table)
    c = config(model)
    ev = b.rid("eval", "NT" if model == "Nucleotide Transformer" else model, key)
    if ev not in b.ids:
        b.evaluation(ev, f"{model} on GenBench {name}", SIDS, c, p, d, "independent_paper",
                     {"protocol_id": p, "dataset_version": None, "split": "GenBench split", "population": None, "inputs": "DNA sequence", "adaptation": "Fine-tuned" if model in PARAMS else "Trained",
                      "metric_implementation": None, "aggregation": "Top-1 as printed (undefined)", "budget": None}, f"{table}, row '{name}', column '{model}'")
    loc = f"{table}, row '{name}', column '{col}'" + loc_extra
    rid = b.rid("result", "NT" if model == "Nucleotide Transformer" else model, key, metric if pmetric else None)
    if v == "-":
        b.result(rid, f"{model} {name} {col}", SRC, SIDS, ev, v, metric, direction, unit, loc, REV(loc), qualifier=q,
                 value_missing={"reason": "unavailable", "note": "Printed '-'; the text says attention-based models failed to converge on this task"})
    else:
        b.result(rid, f"{model} {name} {col}", SRC, SIDS, ev, v, metric, direction, unit, loc, REV(loc), qualifier=q)

def seg(start, end):
    s = next(i for i, l in enumerate(L) if l.lstrip("\x0c ").startswith(start))
    e = next(i for i in range(s + 1, len(L)) if L[i].strip("\x0c ").startswith(end))
    return L[s:e]
def rows(segment, ncols):
    out = []
    for l in segment:
        m = re.match(r"^\s*(\S.*?)\s{2,}((?:-?\d+\.\d+\s+){" + str(ncols - 1) + r"}-?\d+\.\d+)\s*$", l)
        if m:
            out.append((m.group(1).strip(), m.group(2).split()))
    return out

# Table 3
r3 = rows(seg("Table 3:", "Table 4:"), 6)
assert [r[0] for r in r3] == ["dev", "hk", "Mean"], r3
for name, vals in r3:
    for m, v in zip(["HyenaDNA", "DNABERT2", "GENA-LM", "Nucleotide Transformer", "Caduceus", "DeepSTARR"], vals):
        cell("Table 3", f"drosophila-enhancer-activity-{name}", f"Drosophila enhancer activity ({name})", m, m, v, "pearson-correlation", "higher", "unitless",
             q="mean of dev and hk as printed" if name == "Mean" else None)
# Table 4
# Single-dataset tasks whose Table 10 row repeats the Table 4 cells exactly; recorded once, from Table 4.
SINGLE10 = {"Human Splice Site Detection", "Virus Covid Variant Classification"}
T4 = ["Mouse Enhancers", "Coding vs Intergenomic", "Human vs Worm", "Human Enhancers Cohn", "Human Enhancers Ensembl", "Human Ensembl Regulatory", "Human Nontata Promoters",
      "Human OCR Ensembl", "Human Core Promoter Detection", "Human Transcription Factor Prediction", "Human Promoter Detection", "Human Splice Site Detection",
      "Mouse Transcription Factor Prediction", "Yeast Epigenetic Marks Prediction", "Virus Covid Variant Classification"]
r4 = rows(seg("Table 4:", "6"), 7)
assert [r[0] for r in r4] == T4, [r[0] for r in r4]
for name, vals in r4:
    multi = name in ("Human Core Promoter Detection", "Human Transcription Factor Prediction", "Human Promoter Detection", "Mouse Transcription Factor Prediction", "Yeast Epigenetic Marks Prediction")
    for m, v in zip(["HyenaDNA", "DNABERT", "DNABERT2", "GENA-LM", "NT", "Caduceus", "CNN"], vals):
        cell("Table 4", f"short-{name}", name, m, m, v, "accuracy", "higher", "fraction", q="task-level value as printed in Table 4" + ("; mean of the Table 10 dataset rows" if multi else ""),
             loc_extra="; also Table 10" if name in SINGLE10 else "")
# Table 5
r5 = rows(seg("Table 5:", "Table 6:"), 6)
assert [r[0] for r in r5] == ["Splice donar", "Splice acceptor", "Mean"], r5
for name, vals in r5:
    for m, v in zip(["HyenaDNA", "DNABERT2", "GENA-LM", "Nucleotide Transformer", "Caduceus", "SpliceAI"], vals):
        cell("Table 5", f"long-splice-{name}", f"Long-range splice site prediction ({name})", m, m, v, "auroc", "higher", "unitless", q="mean of donor and acceptor as printed" if name == "Mean" else None)
# Table 6
r6 = rows(seg("Table 6:", "which boasts"), 5)
assert [r[0] for r in r6] == ["Species Classification", "Promoters Prediction"], r6
for name, vals in r6:
    for m, v in zip(["HyenaDNA", "DNABERT2", "GENA-LM", "Nucleotide Transformer", "Caduceus"], vals):
        cell("Table 6", f"long-{name}", f"Long-range {name}", m, m, v, "accuracy", "higher", "fraction")
# Table 7: Pearson and MSE per model; dashes for models that did not converge
s7 = seg("Table 7:", "Table 8:")
r7 = []
for l in s7:
    m = re.match(r"^\s*(H1-ESC|HFF)\s+(.*)$", l)
    if m:
        r7.append((m.group(1), m.group(2).split()))
assert [r[0] for r in r7] == ["H1-ESC", "HFF"] and all(len(v) == 12 for _, v in r7), r7
for name, vals in r7:
    for i, m in enumerate(["Orca", "HyenaDNA", "Caduceus", "DNABERT2", "GENA-LM", "NT"]):
        cell("Table 7", f"genome-structure-{name}", f"Genomic structure prediction ({name})", m, f"{m} Pearson", vals[2 * i], "pearson-correlation", "higher", "unitless", pmetric="pearson-correlation")
        cell("Table 7", f"genome-structure-{name}", f"Genomic structure prediction ({name})", m, f"{m} MSE", vals[2 * i + 1], "mean-squared-error", "lower", "unitless", pmetric="pearson-correlation")
# Table 8
s8 = seg("Table 8:", "7")
r8 = [l.split() for l in s8 if l.strip().startswith("Bulk")]
assert len(r8) == 1 and len(r8[0]) == 11, r8
for i, m in enumerate(["HyenaDNA", "Caduceus", "DNABERT2", "Nucleotide Transformer", "GENA-LM"]):
    cell("Table 8", "bulk-rna-expression", "Bulk RNA expression", m, f"{m} Spearman", r8[0][1 + 2 * i], "spearman-correlation", "higher", "unitless", pmetric="spearman-correlation")
    cell("Table 8", "bulk-rna-expression", "Bulk RNA expression", m, f"{m} MSE", r8[0][2 + 2 * i], "mean-squared-error", "lower", "unitless", pmetric="spearman-correlation")
# Table 10: task label may sit on its own line or share a dataset row
s10 = seg("Table 10:", "Where Dnx")
out = []
TASKS10 = ["Human Core Promoter Detection", "Human Transcription Factor Prediction", "Human Promoter Detection", "Human Splice Site Detection",
           "Mouse Transcription Factor Prediction", "Yeast Epigenetic Marks Prediction", "Virus Covid Variant Classification"]
for l in s10:
    m = re.match(r"^\s*(?:(" + "|".join(map(re.escape, TASKS10)) + r")\s+)?(\S+)\s+((?:\d+\.\d+\s+){6}\d+\.\d+)\s*$", l)
    if m:
        out.append((m.group(1), m.group(2), m.group(3).split()))
assert len(out) == 28, len(out)
# Task labels sit mid-block in the layout, so rows are assigned by the printed dataset order, which is asserted.
EXPECT = {"Human Core Promoter Detection": ["all", "notata", "tata"], "Human Transcription Factor Prediction": ["0", "1", "2", "3", "4"],
          "Human Promoter Detection": ["all", "notata", "tata"], "Human Splice Site Detection": ["Reconstructed"], "Mouse Transcription Factor Prediction": ["0", "1", "2", "3", "4"],
          "Yeast Epigenetic Marks Prediction": ["H3", "H3K14ac", "H3K36me3", "H3K4me1", "H3K4me2", "H3K4me3", "H3K79me3", "H3K9ac", "H4", "H4ac"], "Virus Covid Variant Classification": ["Covid"]}
flat = [(ds, vals) for _, ds, vals in out]
names = [ds for ds, _ in flat]
expected = [(t, ds) for t in TASKS10 for ds in EXPECT[t]]
assert names == [ds for _, ds in expected], names
for (t, ds), (ds2, vals) in zip(expected, flat):
    if t in SINGLE10:
        continue
    for m, v in zip(["HyenaDNA", "DNABERT", "DNABERT2", "GENA-LM", "Nucleotide Transformer", "Caduceus", "CNN"], vals):
        cell("Table 10", f"short-{t}-{ds}", f"{t}, dataset {ds}", m, m, v, "accuracy", "higher", "fraction")
print(json.dumps(b.write()))
