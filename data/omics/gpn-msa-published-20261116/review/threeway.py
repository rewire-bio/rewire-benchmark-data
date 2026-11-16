#!/usr/bin/env python3
"""Three-way diff: reviewer OCR reading vs stored results vs extractor comparison.tsv."""
import json
import sys

ROOT = "/Users/timrichardson/Documents/projects/personal/blog/wt/entities-20261115"
SP = "/private/tmp/claude-501/-Users-timrichardson-Documents-projects-personal-blog/2b3e629e-c97e-4855-9278-c3793c720747/scratchpad/review-gpnmsa-pub"

# 1. reviewer reading, keyed by (row label, column index 0..7)
ocr = {}
row_order = []
for line in open(SP + "/reviewer-reading-extended-data-table-1.tsv"):
    parts = line.rstrip("\n").split("\t")
    label, vals = parts[0], parts[1:]
    assert len(vals) == 8, (label, vals)
    row_order.append(label)
    for i, v in enumerate(vals):
        ocr[(label, i)] = v

# 2. stored results
stored = {}
import glob
ALL = sorted(glob.glob(ROOT + "/data/evidence/results/*.jsonl"))
allres = []
for fn in ALL:
    for line in open(fn):
        if line.strip():
            allres.append(json.loads(line))
for r in allres:
    rid = r.get("id", "")
    if rid.startswith("gfm-guides-20261014-gpnmsa-result-ablation-"):
        stored[rid] = r

# 3. extractor comparison
comp = {}
with open(ROOT + "/data/omics/gpn-msa-published-20261116/extract/comparison.tsv") as fh:
    hdr = fh.readline().rstrip("\n").split("\t")
    for line in fh:
        f = dict(zip(hdr, line.rstrip("\n").split("\t")))
        comp[f["stored_result_id"]] = f

# map OCR row label -> the row text the extractor used, and column index -> (column, seed)
COLS = [("ClinVar", "mean"), ("ClinVar", "max"), ("COSMIC", "mean"), ("COSMIC", "max"),
        ("OMIM", "mean"), ("OMIM", "max"), ("gnomAD", "mean"), ("gnomAD", "max")]

# build (row,col,seed) -> stored id from the extractor's own comparison file, but verify
# the row/column labels against the OCR labels rather than trusting the mapping blindly.
by_rcs = {}
for rid, f in comp.items():
    if f["row"].startswith("DMS"):
        continue
    by_rcs[(f["row"], f["column"], f["seed_aggregate"])] = rid

def norm(s):
    return s.replace("’", "'").replace("‘", "'").strip()

print("rows read by OCR: %d" % len(row_order))
print("stored ablation results: %d" % len(stored))
print("comparison rows (non-DMS): %d" % len(by_rcs))
print()

problems = []
checked = 0
for label in row_order:
    for i, (col, seed) in enumerate(COLS):
        key = None
        for (r, c, s) in by_rcs:
            if norm(r) == norm(label) and c == col and s == seed:
                key = (r, c, s)
                break
        if key is None:
            problems.append("NO COMPARISON ROW for %r / %s / %s" % (label, col, seed))
            continue
        rid = by_rcs[key]
        mine = ocr[(label, i)]
        rec = stored.get(rid)
        if rec is None:
            problems.append("NO STORED RECORD %s" % rid)
            continue
        store_printed = str(rec["attributes"].get("printed_value"))
        store_numeric = rec["attributes"].get("numeric_value")
        ext_stored = comp[rid]["stored_value_biorxiv_v2"]
        ext_pub = comp[rid]["published_value_extended_data_table_1"]
        checked += 1
        if mine != store_printed:
            problems.append("OCR vs STORED printed_value: %s ocr=%s stored=%s" % (rid, mine, store_printed))
        if store_numeric is None:
            problems.append("STORED numeric_value is null: %s" % rid)
        elif abs(float(mine) - float(store_numeric)) > 1e-9:
            problems.append("OCR vs STORED numeric_value: %s ocr=%s stored=%s" % (rid, mine, store_numeric))
        if mine != ext_pub:
            problems.append("OCR vs EXTRACTOR published: %s ocr=%s ext=%s" % (rid, mine, ext_pub))
        if ext_stored != store_printed:
            problems.append("EXTRACTOR stored col vs STORED record: %s ext=%s stored=%s" % (rid, ext_stored, store_printed))
        if comp[rid]["differs"] != "no":
            problems.append("EXTRACTOR marked differs=%s for %s" % (comp[rid]["differs"], rid))

print("cells checked three ways: %d" % checked)
print("problems: %d" % len(problems))
for p in problems:
    print("  " + p)

# did the comparison cover every stored result citing the preprint source?
cited = []
for r in allres:
    if "gfm-guides-20261014-gpnmsa-source-biorxiv-v2" in (r.get("source_ids") or []):
        cited.append(r["id"])
print()
print("stored results citing the preprint source: %d" % len(cited))
print("in comparison.tsv: %d" % len([c for c in cited if c in comp]))
missing = [c for c in cited if c not in comp]
print("not in comparison.tsv: %d %s" % (len(missing), missing))
extra = [c for c in comp if c not in cited]
print("in comparison.tsv but not citing that source: %d %s" % (len(extra), extra))
