"""Parse Tables 1, 2 and 3 of PerturbPFN (arXiv:2607.23447v1) from the pdftotext -layout text layer.

Input: artifacts/arxiv-2607.23447v1.pdftotext-layout.txt.gz, made with
`pdftotext -layout` (poppler 26.08.0) from the PDF whose SHA-256 is
42191efa04b45ca04b2be38b51ea374cd9bf891efe2399d331fec9eaeab200b1.
Output: extract/tables.json. Every row label and column header is asserted.

Usage: python3 -I data/omics/perturbpfn-20261115/extract/parse_tables.py
"""
import gzip
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEXT = HERE.parent / "artifacts" / "arxiv-2607.23447v1.pdftotext-layout.txt.gz"
NUM = r"-?\d+\.\d+"

# NFC so that s plus a combining circumflex (U+0073 U+0302) matches the composed character.
lines = unicodedata.normalize("NFC", gzip.open(TEXT, "rt", encoding="utf-8").read()).split("\n")


def caption(prefix: str) -> int:
    hits = [i for i, line in enumerate(lines) if line.strip().startswith(prefix)]
    assert len(hits) == 1, (prefix, hits)
    return hits[0]


out = {}

# Table 1: three blocks of label/value pairs on three lines.
t1 = caption("Table 1: In-prior latent recovery")
header = lines[t1 + 3]
assert re.search(r"Graph\s+Target\s+Strength / Response", header), header
expected = [
    [("Graph", "AUROC ↑"), ("Target", "AUROC ↑"), ("Strength / Response", "|ψ| ratio →1")],
    [("Graph", "AUPRC ↑"), ("Target", "AUPRC ↑"), ("Strength / Response", "∆ cosine ↑")],
    [("Graph", "Proj. F1 ↑"), ("Target", "F1 ↑"), ("Strength / Response", "Obs. NLL ↓")],
]
t1_cells = []
for offset, row in enumerate(expected):
    line = lines[t1 + 4 + offset]
    pattern = r"\s+".join(re.escape(label) + r"\s+(" + NUM + ")" for _, label in row)
    m = re.fullmatch(r"\s*" + pattern + r"\s*", line)
    assert m, line
    for (block, label), value in zip(row, m.groups()):
        t1_cells.append({"block": block, "row_label": label, "printed_value": value, "line": t1 + 5 + offset})
assert len(t1_cells) == 9
out["table1"] = t1_cells

# Table 2: seven model rows; PerturbPFN prints one score row between its two runtime rows.
t2 = caption("Table 2: Runtime per protocol")
header = lines[t2 + 4]
assert re.fullmatch(r"\s*Model\s+Time \(s\) / protocol\s+ŝMD ↑\s+ŝr ↑\s+ŝW2 ↑\s+Avg\. ŝ / rank\s*", header), header
cols = ["sMD", "sr", "sW2"]
row_re = re.compile(
    r"\s*(?P<model>[A-Za-z][A-Za-z .-]*?)\s{2,}(?P<time>(?:\d+\.\d+ ± \d+\.\d+)|/)\s+"
    r"(?P<sMD>" + NUM + r")\s+(?P<sr>" + NUM + r")\s+(?P<sW2>" + NUM + r")\s+(?P<avg>" + NUM + r") \((?P<rank>#\d)\)\s*"
)
t2_rows = []
names = ["RF X-Learner", "CondOT", "MLP", "GIM", "Naive", "Observational"]
for k, name in enumerate(names):
    line = lines[t2 + 5 + k]
    m = row_re.fullmatch(line)
    assert m and m.group("model") == name, (name, line)
    row = {"model": name, "line": t2 + 6 + k, "time": m.group("time"), "avg": m.group("avg"), "rank": m.group("rank")}
    row.update({c: m.group(c) for c in cols})
    t2_rows.append(row)
amort = lines[t2 + 11]
scores = lines[t2 + 12]
icl = lines[t2 + 13]
m_a = re.fullmatch(r"\s*PerturbPFN \(amortized\)\s+(\d+\.\d+ ± \d+\.\d+)\s*", amort)
m_s = re.fullmatch(r"\s*(" + NUM + r")\s+(" + NUM + r")\s+(" + NUM + r")\s+(" + NUM + r") \((#\d)\)\s*", scores)
m_i = re.fullmatch(r"\s*PerturbPFN \(ICL only\)\s+(\d+\.\d+ ± \d+\.\d+)\s*", icl)
assert m_a and m_s and m_i, (amort, scores, icl)
t2_rows.append({
    "model": "PerturbPFN",
    "time_amortized": m_a.group(1), "time_amortized_line": t2 + 12,
    "time_icl_only": m_i.group(1), "time_icl_only_line": t2 + 14,
    "line": t2 + 13,
    "sMD": m_s.group(1), "sr": m_s.group(2), "sW2": m_s.group(3), "avg": m_s.group(4), "rank": m_s.group(5),
})
assert [r["rank"] for r in t2_rows] == ["#1", "#3", "#4", "#5", "#6", "#7", "#2"]
# The average column is the mean of the three normalised columns (Section 4.2, Appendix D.3).
for r in t2_rows:
    mean = sum(float(r[c]) for c in cols) / 3
    assert abs(mean - float(r["avg"])) <= 0.00006, (r["model"], mean, r["avg"])
out["table2"] = t2_rows

# Table 3: six rows, five metric columns.
t3 = caption("Table 3: GeneRNIB 300BCG GRN recovery")
header = lines[t3 + 1]
assert re.fullmatch(r"\s*Model\s+GS-F1\s+TFB-F1\s+R-Prec\.\s+R-Recall\s+VC\s*", header), header
t3_cols = ["GS-F1", "TFB-F1", "R-Prec.", "R-Recall", "VC"]
t3_rows = []
for k, name in enumerate(["Pearson corr.", "PPCOR", "GRNBoost2", "PORTIA", "SCENIC", "PerturbPFN"]):
    line = lines[t3 + 2 + k]
    m = re.fullmatch(r"\s*" + re.escape(name) + r"\s+" + r"\s+".join(["(" + NUM + ")"] * 5) + r"\s*", line)
    assert m, (name, line)
    row = {"model": name, "line": t3 + 3 + k}
    row.update(dict(zip(t3_cols, m.groups())))
    t3_rows.append(row)
out["table3"] = t3_rows

# Prose value used as a result: the top-k gate F1 in Section 4.1 Results.
gate = [i for i, line in enumerate(lines) if "straight-through top-k gate used by the" in line]
assert len(gate) == 1 and "lower F1 of 0.6287" in lines[gate[0] + 1], gate
out["prose"] = [{"key": "target_topk_gate_f1", "printed_value": "0.6287", "line": gate[0] + 2}]

(HERE / "tables.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print("table1", len(t1_cells), "table2 rows", len(t2_rows), "table3 rows", len(t3_rows))
