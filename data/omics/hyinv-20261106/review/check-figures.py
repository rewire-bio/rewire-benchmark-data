"""Independent reviewer check of the Figure 14 and Figure 15 matrices.

Reads the pdftotext -layout text layer, finds the body lines of each figure by row label,
splits the numbers into three blocks of five, and compares every cell with batch.jsonl.
Written for the review pass; does not import the extractor's code.
"""
import json
import re
import sys

TXT, BATCH = sys.argv[1], sys.argv[2]
COLS = ["CATH4.3 test", "CATH4.2 test", "TS500", "TS50", "RecentPDB"]
ROWS = ["HyInv", "ProteinZero V2 (ESM2)", "ProteinZero V2 (ESM1)", "ProteinMPNN grouped",
        "ProteinMPNN", "LigandMPNN", "ProteinMPNN (low-noise, grouped)", "PiFold",
        "LM-Design 650M", "CMLM", "DPLM-2 3B", "Native"]
FIGS = {14: ["scTM", "Recovery", "Diversity"], 15: ["pLDDT", "scRMSD", "CA-lDDT"]}

lines = open(TXT).read().splitlines()
caption = {n: next(i for i, l in enumerate(lines) if l.startswith(f"Figure {n}:")) for n in FIGS}
# Figure 14's body sits above its caption; Figure 15's body sits above its own caption and
# below Figure 14's. Take the window between the previous caption and this one.
bounds = {14: (caption[14] - 40, caption[14]), 15: (caption[14], caption[15])}

parsed = {}
for fig, (lo, hi) in bounds.items():
    for row in ROWS:
        pat = re.compile(r"(?:^|\s)" + re.escape(row) + r"\s+((?:[-–\d.]+\s+){14}[-–\d.]+)\s*$")
        hits = [m.group(1).split() for l in lines[lo:hi] for m in [pat.search(l)] if m]
        assert len(hits) == 1, (fig, row, hits)
        cells = hits[0]
        assert len(cells) == 15, (fig, row, cells)
        for b, block in enumerate(FIGS[fig]):
            for c, col in enumerate(COLS):
                parsed[(fig, block, row, col)] = cells[b * 5 + c]

loc = re.compile(r"^Figure (\d+), '([^']+)' block, row '([^']+)', column '([^']+)'")
checked = bad = 0
for line in open(BATCH):
    r = json.loads(line)
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    m = loc.match(a["source_locator"])
    if not m:
        continue
    key = (int(m[1]), m[2], m[3], m[4])
    if key not in parsed:
        print("NO SUCH CELL", r["id"], key)
        bad += 1
        continue
    want = parsed[key]
    if a["printed_value"] != want:
        print("MISMATCH", r["id"], "record", a["printed_value"], "source", want)
        bad += 1
    if a["numeric_value"] is not None and float(a["numeric_value"]) != float(want):
        print("NUMERIC MISMATCH", r["id"], a["numeric_value"], want)
        bad += 1
    checked += 1

# Which printed cells are not recorded at all?
recorded = set()
for line in open(BATCH):
    r = json.loads(line)
    if r["kind"] == "result":
        m = loc.match(r["attributes"]["source_locator"])
        if m:
            recorded.add((int(m[1]), m[2], m[3], m[4]))
missing = [(k, v) for k, v in parsed.items() if k not in recorded]
print(f"checked {checked} figure cells, {bad} problems")
print(f"printed figure cells not recorded: {len(missing)}")
for k, v in sorted(missing, key=lambda x: (x[0][0], x[0][1], x[0][2])):
    print("  unrecorded", k, "=", v)
