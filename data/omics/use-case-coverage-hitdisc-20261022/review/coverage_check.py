"""Cell-coverage check: does the batch cover every printed cell of the tables it claims, exactly once?

Independent of the extractor. Builds the full cell set from my own parse and compares with the
set of (table, row, column) locators in batch.jsonl.
"""

import os

# Paths are configurable so the review can be rerun anywhere.
SOURCES_ROOT = os.environ.get("HITDISC_SOURCES", "sources")
BATCH_DIR = os.environ.get("HITDISC_BATCH_DIR", "data/omics/use-case-coverage-hitdisc-20261022")
import json
import re
import sys
import collections
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myparse_shen
import myparse_xlsx

SCR = SOURCES_ROOT
BATCH = os.path.join(BATCH_DIR, "batch.jsonl")

shen = myparse_shen.parse(SOURCES_ROOT + "/PMC12704515.xml")
ref = set()
for lab in ["Table 1", "Table 3", "Table 4"]:
    d = shen[lab]
    for rowlabel, vals in d["rows"]:
        for ci, v in enumerate(vals):
            if v.strip():
                ref.add((lab, rowlabel, ci))
blk = None
for rowlabel, vals in shen["Table 2"]["rows"]:
    if not vals:
        if rowlabel.strip():
            blk = rowlabel
        continue
    for ci, v in enumerate(vals):
        if v.strip():
            ref.add(("Table 2", blk + "/" + rowlabel, ci))
meth = None
for rowlabel, vals in shen["Table 5"]["rows"]:
    if rowlabel in ("1", "5"):
        cells = vals
        key = (meth, rowlabel, True)
    else:
        meth = rowlabel
        cells = vals[1:]
        key = (meth, vals[0], False)
    for ci, v in enumerate(cells):
        if v.strip():
            ref.add(("Table 5", key, ci))

s8 = myparse_xlsx.read_sheet(SOURCES_ROOT + "/supp/ci5c02441_si_002.xlsx", "S8")
s8rows, hdr = {}, {}
for r, d in s8.items():
    m = re.match(r"([A-Z]+)(\d+)$", r)
    c, rn = m.group(1), int(m.group(2))
    (hdr if rn == 1 else s8rows.setdefault(rn, {}))[c] = d
OWN = list("DEFGHIJ")
MERGED = list("LMNOPQRST")
for rn, cells in s8rows.items():
    wf = str(int(float(cells["B"]["raw"])))
    for c in OWN + MERGED:
        cell = cells.get(c)
        if cell is not None and cell["raw"] != "":
            ref.add(("S8", wf, c))

# ---- the batch's own cell set
recs = [json.loads(l) for l in open(BATCH)]
got = collections.Counter()
COLIDX = {("auroc", "Mean"): 0, ("auroc", "Med"): 1, ("bedroc", "Mean"): 2, ("bedroc", "Med"): 3,
          ("ef0.5", "Mean"): 4, ("ef0.5", "Med"): 5, ("ef1", "Mean"): 6, ("ef1", "Med"): 7,
          ("ef5", "Mean"): 8, ("ef5", "Med"): 9}
T4COL = {("ESR_ago", "EF1%"): 0, ("ESR_ago", "NEF1%"): 1, ("ESR_antago", "EF1%"): 2,
         ("ESR_antago", "NEF1%"): 3, ("PPARG", "EF1%"): 4, ("PPARG", "NEF1%"): 5,
         ("TP53", "EF1%"): 6, ("TP53", "NEF1%"): 7, ("MAPK1", "EF1%"): 8, ("MAPK1", "NEF1%"): 9,
         ("Average", "EF1%"): 10, ("Average", "NEF1%"): 11}
T5COL = {"a2a": 0, "ar": 1, "cdk2": 2, "ctsk": 3, "hdac2": 4, "Average": 5}


def colidx(colname, agg):
    c = colname.lower().replace("α", "a")
    if c.startswith("auroc"):
        k = "auroc"
    elif c.startswith("bedroc"):
        k = "bedroc"
    elif c.startswith("ef0.5"):
        k = "ef0.5"
    elif c.startswith("ef1"):
        k = "ef1"
    elif c.startswith("ef5"):
        k = "ef5"
    else:
        raise KeyError(colname)
    return COLIDX[(k, agg)]


unparsed = []
t5method = {}
for r in recs:
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    loc, tbl = a["source_locator"], a.get("source_table")
    if tbl in ("Table 1", "Table 3"):
        m = re.match(r"Table (1|3), row '(.+)', column '(.+)' \((Mean|Med)\)$", loc)
        got[(f"Table {m.group(1)}", m.group(2), colidx(m.group(3), m.group(4)))] += 1
    elif tbl == "Table 2":
        m = re.match(r"Table 2, (Protenix|AF3) block, row '(.+)', column '(.+)' \((Mean|Med)\)$", loc)
        got[("Table 2", m.group(1) + "/" + m.group(2), colidx(m.group(3), m.group(4)))] += 1
    elif tbl == "Table 4":
        m = re.match(r"Table 4, row '(.+)', column '(.+)' \((EF1%|NEF1%)\)$", loc)
        got[("Table 4", m.group(1), T4COL[(m.group(2), m.group(3))])] += 1
    elif tbl == "Table 5":
        m = re.match(r"Table 5, row '(.+)' \(Number of samples = (1|5)\), column '(.+)'$", loc)
        rowlab, nsamp, colname = m.groups()
        cont = rowlab.startswith("(row continued")
        ev = next(x for x in recs if x["id"] == r["links"][0]["target_id"])
        cfg = next(x for x in recs if x["id"] == next(l["target_id"] for l in ev["links"]
                                                      if l["relation"] == "system"))
        meth = re.sub(r"\s*\((?!without).*", "", cfg["attributes"]["reported_name"])
        got[("Table 5", (meth, nsamp, cont), T5COL[colname])] += 1
    elif tbl == "Table S8":
        m = re.match(r"Sheet 'S8', row with Workflow = (\d+), column ([A-T])\b", loc)
        got[("S8", m.group(1), m.group(2))] += 1
    else:
        unparsed.append(loc)

print("reference cells:", len(ref))
print("batch cells:", sum(got.values()), " distinct:", len(got))
print("duplicated:", [k for k, v in got.items() if v > 1])
print("in batch but not in reference:", sorted(set(got) - ref)[:20])
print("in reference but not in batch:", sorted(str(x) for x in (ref - set(got)))[:20])
print("non-table results (expected 9):", len(unparsed))
