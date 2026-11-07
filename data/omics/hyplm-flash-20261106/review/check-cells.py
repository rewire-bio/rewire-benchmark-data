"""Reviewer check of the HyPLM-Flash tables, independent of extract/parse.py and check_cells.py.

Reads the pdftotext -layout text layer, finds each table by caption, takes the column order from
the printed header line, splits each body row into its printed cells, and compares every cell with
batch.jsonl by the column the locator names. Also re-does the two arithmetic constraints, PPL
against exp(NLL) and each Table 5 average against the mean of its five categories, and reports any
printed cell the batch does not record.
"""
import json
import math
import re
import sys

TXT, BATCH = sys.argv[1], sys.argv[2]
lines = open(TXT).read().splitlines()

T3_MODELS = ["ESM-2 650M", "ESM C 600M", "E1-600M", "AMPLIFY-350M", "DPLM-650M", "ProtBERT",
             "ESM-2 3B", "ESM-2 15B", "ESM C 6B", "HyPLM-Flash"]
T3_COLS = ["Held-out UniRef proteins, NLL", "Held-out UniRef proteins, PPL",
           "Recent PDB chains, NLL", "Recent PDB chains, PPL"]
T5_ROWS = ["VespaG", "VESPA", "DPLM-3B†", "E1-600M†", "E1-300M†", "ESM2 (650M)", "DPLM-650M†",
           "HyPLM-Flash†", "ESM C 6B†", "ESM-1v (ensemble)", "ESM-C (300M)", "ESM2 (3B)",
           "ESM-C (600M)", "E1-150M†"]
T5_COLS = ["Activity", "Binding", "Expression", "Organismal fitness", "Stability", "Average"]
T6_MODELS = ["ESM-2 650M", "ESM-1b", "ESM C 600M", "E1-600M", "AMPLIFY-350M", "DPLM-650M",
             "HyPLM-Flash"]
T7_MODELS = ["ESM3-open", "ProtBERT", "ProtT5-XL", "Ankh-base", "Ankh3-large", "xTrimoPGLM-1B"]
NUM = r"[−-]?\d+\.\d+|–"

cells = {}


def caption(prefix):
    return next(i for i, l in enumerate(lines) if l.startswith(prefix))


def row_values(lo, hi, label, count):
    """The printed numbers of the one body line that starts with `label`."""
    pat = re.compile(r"^\s*(?:\d+\s+)?" + re.escape(label) + r"(?!\S)")
    hits = []
    for l in lines[lo:hi]:
        if pat.match(l):
            vals = re.findall(NUM, l[pat.match(l).end():])
            if len(vals) == count:
                hits.append(vals)
    assert len(hits) == 1, (label, count, hits)
    return hits[0]


# Table 3: ten models, four numbers each. The label and its first value share a text run on one
# row ("AMPLIFY-350M 1.743"), which is why the count is asserted rather than the layout trusted.
c3 = caption("Table 3: Masked-residue likelihood")
for model in T3_MODELS:
    vals = row_values(c3, c3 + 22, model, 4)
    for col, v in zip(T3_COLS, vals):
        cells[("Table 3", model, col)] = v
    for nll, ppl in ((vals[0], vals[1]), (vals[2], vals[3])):
        lo = math.exp(float(nll) - 0.0005) - 0.005
        hi = math.exp(float(nll) + 0.0005) + 0.005
        assert lo - 1e-9 <= float(ppl) <= hi + 1e-9, ("PPL != exp(NLL)", model, nll, ppl)

# Table 5: fourteen ranked rows, six numbers each, and the average must be the mean of five.
c5 = caption("Table 5: Top of the ProteinGym")
for label in T5_ROWS:
    vals = row_values(c5, c5 + 26, label, 6)
    for col, v in zip(T5_COLS, vals):
        cells[("Table 5", label, col)] = v
    mean = sum(float(v) for v in vals[:5]) / 5
    assert abs(mean - float(vals[5])) <= 0.001 + 1e-9, ("average != mean", label, mean, vals[5])

# Tables 6 and 7: one row per task, one column per model.
for prefix, models in (("Table 6: All tasks, part 1", T6_MODELS),
                       ("Table 7: All tasks, part 2", T7_MODELS)):
    cap = caption(prefix)
    table = prefix.split(":")[0]
    header = next(l for l in lines[cap:cap + 6] if l.lstrip().startswith("Task"))
    for model in models:
        assert model in header, (table, model, header)
    # Body rows: a task label, a metric label, then one value per model.
    seen = 0
    for l in lines[cap:cap + 60]:
        vals = re.findall(NUM, l)
        if len(vals) != len(models):
            continue
        label = l[:l.index(vals[0])] if vals[0] in l else ""
        task = re.sub(r"\s{2,}.*$", "", label.strip())
        if not task:
            continue
        for model, v in zip(models, vals):
            cells[(table, task, model)] = v
        seen += 1
    assert seen == 32, (table, "task rows found", seen)

loc = re.compile(r"^(Table \d+), row '([^']+)', column '([^']+)'")
checked = bad = 0
recorded = set()
for line in open(BATCH):
    r = json.loads(line)
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    m = loc.match(a["source_locator"])
    if not m:
        continue
    key = (m[1], m[2], m[3])
    recorded.add(key)
    if key not in cells:
        print("NO SUCH CELL", r["id"], key)
        bad += 1
        continue
    want = cells[key].replace("−", "-")
    got = a["printed_value"].replace("−", "-")
    if got != want:
        print("MISMATCH", r["id"], "| record", repr(got), "| source", repr(want))
        bad += 1
    checked += 1
print(f"checked {checked} table cells, {bad} problems")
unrec = sorted(k for k, v in cells.items() if k not in recorded and v != "–")
print(f"printed numeric cells of these tables not recorded: {len(unrec)}")
for k in unrec:
    print("  unrecorded", k, "=", cells[k])
