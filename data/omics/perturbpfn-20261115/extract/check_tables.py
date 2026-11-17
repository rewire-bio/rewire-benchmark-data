"""Second, independent read of every table cell in batch.jsonl.

Splits each table line of the archived text layer on runs of two or more spaces and indexes the
cell by the position of its column in the printed header, so a value taken from a neighbouring
column fails. Checks printed_value, numeric_value and the evaluation each result belongs to.

Usage: python3 -I data/omics/perturbpfn-20261115/extract/check_tables.py
"""
import gzip
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
BATCH = HERE.parent
lines = unicodedata.normalize("NFC", gzip.open(BATCH / "artifacts" / "arxiv-2607.23447v1.pdftotext-layout.txt.gz", "rt").read()).split("\n")
records = [json.loads(l) for l in (BATCH / "batch.jsonl").read_text().splitlines()]
results = {r["id"]: r for r in records if r["kind"] == "result"}
evals = {r["id"]: r for r in records if r["kind"] == "evaluation"}


def cells(line):
    return re.split(r"\s{2,}", line.strip())


def find(label_re):
    hits = [i for i, l in enumerate(lines) if re.match(r"\s*" + label_re + r"(\s{2,}|$)", l)]
    assert len(hits) == 1, (label_re, hits)
    return hits[0]


checked = 0


def expect(result_id, printed, system_suffix):
    global checked
    r = results.pop(result_id)
    a = r["attributes"]
    assert a["printed_value"] == printed, (result_id, a["printed_value"], printed)
    num = re.sub(r"[()#]", "", printed)
    assert a["numeric_value"] == num, (result_id, a["numeric_value"], num)
    ev = evals[[l["target_id"] for l in r["links"] if l["relation"] == "evaluation"][0]]
    system = [l["target_id"] for l in ev["links"] if l["relation"] == "system"][0]
    assert system.endswith(system_suffix), (result_id, system, system_suffix)
    checked += 1


# Table 2: header columns Model | Time | sMD | sr | sW2 | Avg/rank
P = "perturbpfn-20261115-result-sciplex-"
t2 = {"RF X-Learner": ("rf-x-learner", "config-rf-x-learner-sciplex"), "CondOT": ("condot", "config-condot-sciplex"),
      "MLP": ("mlp", "config-mlp-shift-sciplex"), "GIM": ("gim", "config-gim-sciplex"),
      "Naive": ("naive", "method-naive-lower-dose"), "Observational": ("observational", "method-no-change")}
for label, (key, system) in t2.items():
    c = cells(lines[find(re.escape(label))])
    assert c[0] == label and len(c) == 6, c
    if c[1] != "/":
        expect(P + key + "-runtime", c[1].split(" ± ")[0], system)
        assert results.get(P + key + "-runtime") is None
    for col, name in ((2, "smd"), (3, "sr"), (4, "sw2")):
        expect(P + f"{key}-{name}", c[col], system)
    score, rank = c[5].split(" ")
    expect(P + f"{key}-avg-score", score, system)
    expect(P + f"{key}-rank", rank, system)
amort = find(re.escape("PerturbPFN (amortized)"))
icl = find(re.escape("PerturbPFN (ICL only)"))
assert icl == amort + 2
expect(P + "perturbpfn-runtime-amortized", cells(lines[amort])[1].split(" ± ")[0], "config-perturbpfn-step3100")
expect(P + "perturbpfn-runtime-icl-only", cells(lines[icl])[1].split(" ± ")[0], "config-perturbpfn-step3100")
c = cells(lines[amort + 1])
assert len(c) == 4, c
for col, name in ((0, "smd"), (1, "sr"), (2, "sw2")):
    expect(P + f"perturbpfn-{name}", c[col], "config-perturbpfn-step3100")
score, rank = c[3].split(" ")
expect(P + "perturbpfn-avg-score", score, "config-perturbpfn-step3100")
expect(P + "perturbpfn-rank", rank, "config-perturbpfn-step3100")

# Table 3
G = "perturbpfn-20261115-result-genernib-300bcg-"
hdr = cells(lines[find(r"Model\s+GS-F1")])
assert hdr == ["Model", "GS-F1", "TFB-F1", "R-Prec.", "R-Recall", "VC"], hdr
keys = {"GS-F1": "gs-f1", "TFB-F1": "tfb-f1", "R-Prec.": "r-precision", "R-Recall": "r-recall", "VC": "vc"}
t3 = {"Pearson corr.": ("pearson", "method-pearson-grn"), "PPCOR": ("ppcor", "method-ppcor"),
      "GRNBoost2": ("grnboost2", "method-grnboost2"), "PORTIA": ("portia", "method-portia"),
      "SCENIC": ("scenic", "method-scenic"), "PerturbPFN": ("perturbpfn", "config-perturbpfn-step3100-genernib-panels")}
t3_lines = [i for i, l in enumerate(lines) if "Table 3: GeneRNIB" in l]
for label, (key, system) in t3.items():
    i = [j for j in range(t3_lines[0], t3_lines[0] + 9) if cells(lines[j])[0] == label]
    assert len(i) == 1, label
    c = cells(lines[i[0]])
    for col, h in enumerate(hdr[1:], start=1):
        expect(G + f"{key}-{keys[h]}", c[col], system)

# Table 1: three label/value pairs per line
I = "perturbpfn-20261115-result-in-prior-"
t1 = [i for i, l in enumerate(lines) if l.strip().startswith("Table 1: In-prior")][0]
grid = [cells(lines[t1 + 4 + k]) for k in range(3)]
names = [["graph-auroc", "target-auroc", "strength-ratio"], ["graph-auprc", "target-auprc", "response-shift-cosine"],
         ["graph-projected-f1", "target-f1", "observation-nll"]]
for row, keyrow in zip(grid, names):
    assert len(row) == 6, row
    for k, key in enumerate(keyrow):
        expect(I + key, row[2 * k + 1], "config-perturbpfn-step3100")
assert "0.6287" in lines[[i for i, l in enumerate(lines) if "top-k gate used by the" in l][0] + 1]
expect(I + "target-topk-gate-f1", "0.6287", "config-perturbpfn-step3100")

assert not results, sorted(results)
print(f"checked {checked} results by column position; none left unchecked")
