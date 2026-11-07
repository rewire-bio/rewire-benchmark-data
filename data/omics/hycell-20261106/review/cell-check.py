#!/usr/bin/env python3
"""Independent column-position check of HyCell batch results against the PDF text layer.

Written by the reviewer. Does not import or reuse the extractor's parse.py / check_cells.py.
Builds table models directly from pdftotext -layout output, keyed by (table, row, column),
then checks every result whose locator names a table cell.
"""
import json
import re
import sys
from decimal import Decimal

LAYOUT = sys.argv[1]
BATCH = sys.argv[2]

lines = open(LAYOUT, encoding="utf-8").read().split("\n")


def find(pat, start=0):
    rx = re.compile(pat)
    for i in range(start, len(lines)):
        if rx.search(lines[i]):
            return i
    raise AssertionError("not found: " + pat)


# ---------------------------------------------------------------- Table 3
i = find(r"^\s*Model\s+Params\s+Cells\s+Score S\s+Bio\s+Batch\s+LR\s+kNN\s*$")
T3_COLS = ["Params", "Cells", "Score S", "Bio", "Batch", "LR", "kNN"]
t3 = {}
t3_order = []
for ln in lines[i + 1:]:
    s = ln.strip()
    if not s:
        if t3:
            break
        continue
    parts = s.split()
    # row label may be several words: cells are the trailing 7 tokens
    cells = parts[-7:]
    label = " ".join(parts[:-7])
    assert len(cells) == 7, (label, cells)
    t3[label] = dict(zip(T3_COLS, cells))
    t3_order.append(label)
assert len(t3) == 12, t3_order

# ---------------------------------------------------------------- Table 4
i = find(r"^\s*Model\s+Immune\s+Pancreas\s+Lung\s+PBMC\s+Brain\s+Cross-tissue\s+AIDA\s*$")
T4_COLS = ["Immune", "Pancreas", "Lung", "PBMC", "Brain", "Cross-tissue", "AIDA"]
t4 = {}
t4_order = []
for ln in lines[i + 1:]:
    s = ln.strip()
    if not s:
        if t4:
            break
        continue
    parts = s.split()
    cells = parts[-7:]
    label = " ".join(parts[:-7])
    t4[label] = dict(zip(T4_COLS, cells))
    t4_order.append(label)
assert len(t4) == 12, t4_order
assert t3_order == t4_order, (t3_order, t4_order)

# ---------------------------------------------------------------- Table 5
i = find(r"^\s*Atlas\s+Batches\s+Fine-tuned\s+Frozen \+ LR\s+Frozen \+ kNN\s*$")
T5_COLS = ["Batches", "Fine-tuned", "Frozen + LR", "Frozen + kNN"]
t5 = {}
t5_order = []
for ln in lines[i + 1:]:
    s = ln.strip()
    if not s:
        if t5:
            break
        continue
    parts = s.split()
    cells = parts[-4:]
    label = " ".join(parts[:-4])
    t5[label] = dict(zip(T5_COLS, cells))
    t5_order.append(label)
assert t5_order == ["Pancreas", "Lung", "PBMC", "Immune"], t5_order

# ------------------------------------------------------- Figure 1b heatmap
# Rows are printed as: <atlas label> then six values, between the Figure 1a
# axis block and the Figure 1 caption. Column identity is established below.
F1B_ROWS = ["Immune", "Pancreas", "Lung", "PBMC", "Brain", "Cross-tissue immune",
            "AIDA", "Mean"]
cap = find(r"^Figure 1: HyCell and ten published")
f1b = {}
f1b_order = []
ROWRX = re.compile(r"(Cross-tissue immune|Immune|Pancreas|Lung|PBMC|Brain|AIDA|Mean)"
                   r"\s+((?:0\.\d{3}\s+){5}0\.\d{3})\s*$")
for ln in lines[:cap]:
    m = ROWRX.search(ln.rstrip())
    if m:
        assert m.group(1) not in f1b, m.group(1)
        f1b[m.group(1)] = m.group(2).split()
        f1b_order.append(m.group(1))
assert f1b_order == F1B_ROWS, f1b_order

# Column identity, established two independent ways.
# (1) the Mean row must equal Table 3 "Bio" for exactly one ordering of six models
f1b_models_from_mean = []
for v in f1b["Mean"]:
    hits = [m for m in t3_order if t3[m]["Bio"] == v]
    assert len(hits) == 1, (v, hits)
    f1b_models_from_mean.append(hits[0])
# (2) the pdftotext -raw text layer prints the rotated headers as words
RAW = sys.argv[3]
rawtxt = open(RAW, encoding="utf-8").read()
# In -raw mode the rotated headers print as plain words on their own lines,
# between the Figure 1a legend and the first heatmap row.
rawlines = rawtxt.split("\n")
a = rawlines.index("batch-grouped inference")
b = next(k for k in range(a, len(rawlines))
         if re.match(r"^Immune(?: 0\.\d{3}){6}$", rawlines[k]))
raw_headers = [s.strip() for s in rawlines[a + 1:b] if s.strip()]
F1B_COLS = raw_headers
# the two methods must agree once Table 3's glued superscript and the (70M) suffix
# are removed from the Table 3 labels
T3_TO_PLAIN = {'HyCell': 'HyCell', 'Stackb': 'Stack', 'SCimilarityl': 'SCimilarity',
               'scFoundation': 'scFoundation', 'UCE': 'UCE',
               'Tahoe-x1 (70M)': 'Tahoe-x1', 'TranscriptFormer': 'TranscriptFormer',
               'scGPT': 'scGPT', 'Geneformer V2': 'Geneformer V2',
               'STATE-SE': 'STATE-SE', 'scPRINTl': 'scPRINT', 'PCA': 'PCA'}
assert set(T3_TO_PLAIN) == set(t3_order)
norm = [T3_TO_PLAIN[m] for m in f1b_models_from_mean]
assert norm == raw_headers, (norm, raw_headers)

# ------------------------------------------------------- arithmetic identities
W = {"Bio": Decimal("0.3"), "Batch": Decimal("0.2"),
     "LR": Decimal("0.25"), "kNN": Decimal("0.25")}
arith = []
for m in t3_order:
    s = sum(W[c] * Decimal(t3[m][c]) for c in W)
    arith.append((m, "S from weights", t3[m]["Score S"], str(s),
                  abs(s - Decimal(t3[m]["Score S"])) <= Decimal("0.0005")))
    mean4 = sum(Decimal(t4[m][c]) for c in T4_COLS) / 7
    arith.append((m, "T3 S = mean of T4", t3[m]["Score S"], str(round(mean4, 4)),
                  abs(mean4 - Decimal(t3[m]["Score S"])) <= Decimal("0.0005")))
PLAIN_TO_T3 = {v: k for k, v in T3_TO_PLAIN.items()}
for j, mp in enumerate(F1B_COLS):
    m = PLAIN_TO_T3[mp]
    colmean = sum(Decimal(f1b[r][j]) for r in F1B_ROWS[:-1]) / 7
    arith.append((m, "F1b column mean = F1b Mean", f1b["Mean"][j], str(round(colmean, 4)),
                  abs(colmean - Decimal(f1b["Mean"][j])) <= Decimal("0.0005")))
    arith.append((m, "F1b Mean = T3 Bio", t3[m]["Bio"], f1b["Mean"][j],
                  t3[m]["Bio"] == f1b["Mean"][j]))

# ---------------------------------------------------------------- results
recs = [json.loads(l) for l in open(BATCH, encoding="utf-8")]
results = [r for r in recs if r["kind"] == "result"]

RX_T = re.compile(r"^Table (\d), row '([^']+)'(?: \([^)]*\))?, column '([^']+)'")
RX_F = re.compile(r"^Figure 1b, row '([^']+)', column '([^']+)'")

checked, failed, unparsed = 0, [], []
rows_out = []
for r in results:
    loc = r["attributes"]["source_locator"]
    pv = r["attributes"]["printed_value"]
    nv = r["attributes"].get("numeric_value")
    m = RX_T.match(loc)
    got = None
    where = None
    if m:
        tn, row, col = m.group(1), m.group(2), m.group(3)
        tbl = {"3": t3, "4": t4, "5": t5}.get(tn)
        if tbl is None:
            unparsed.append((r["id"], loc))
            continue
        if col == "S" and tn == "3":
            col = "Score S"
        if row not in tbl:
            failed.append((r["id"], loc, pv, "row not found"))
            continue
        if col not in tbl[row]:
            failed.append((r["id"], loc, pv, "column not found"))
            continue
        got = tbl[row][col]
        where = "Table " + tn
    else:
        m = RX_F.match(loc)
        if not m:
            unparsed.append((r["id"], loc))
            continue
        row, col = m.group(1), m.group(2)
        colkey = {'Tahoe-x1 (70M)': 'Tahoe-x1'}.get(col, col)
        if colkey not in F1B_COLS:
            failed.append((r["id"], loc, pv, "column %r not a Figure 1b column" % col))
            continue
        if row not in f1b:
            failed.append((r["id"], loc, pv, "row not found"))
            continue
        got = f1b[row][F1B_COLS.index(colkey)]
        where = "Figure 1b"
    checked += 1
    rows_out.append((r["id"], "placed_in_cell" if got == pv else "MISMATCH", pv, got,
                     where, loc))
    if got != pv:
        failed.append((r["id"], loc, pv, "cell prints %s" % got))
    elif nv is not None and Decimal(nv) != Decimal(pv):
        failed.append((r["id"], loc, pv, "numeric_value %s" % nv))

with open(sys.argv[4], "w", encoding="utf-8") as fh:
    fh.write("id\tstatus\tprinted_value\tcell_at_named_column\ttable\tsource_locator\n")
    for row in sorted(rows_out):
        fh.write("\t".join(row) + "\n")
    for rid, loc in sorted(unparsed):
        fh.write("\t".join((rid, "prose_locator_checked_by_hand", "", "", "", loc)) + "\n")

print("Table 3 rows:", t3_order)
print("Table 4 rows match Table 3:", t3_order == t4_order)
print("Table 5 rows:", t5_order)
print("Figure 1b columns from Mean-row identity:", F1B_COLS)
print("Figure 1b headers in -raw order:        ", raw_headers)
print("column identity agrees:", F1B_COLS == raw_headers)
print()
bad = [a for a in arith if not a[4]]
print("arithmetic identities: %d checked, %d failed" % (len(arith), len(bad)))
for a in bad:
    print("  FAIL", a)
print()
print("cell-position checks: %d of %d results checked, %d failed, %d locators not a table/figure cell"
      % (checked, len(results), len(failed), len(unparsed)))
for f in failed:
    print("  FAIL", f)
print()
print("locators not checked here (%d):" % len(unparsed))
for u in unparsed:
    print("   ", u[1])
