"""Independent reviewer check of Tables 6, 7, 8 and 9 of the HyInv report.

Re-reads the pinned text layer by row label, splits the printed cells by position, and compares
every cell with batch.jsonl including the column the locator names. Does not import the
extractor's code.
"""
import json
import re
import sys

TXT, BATCH = sys.argv[1], sys.argv[2]
lines = open(TXT).read().splitlines()

NUM = r"[-+−]?[\d,]+\.?\d*"
BRACKET = r"[-+−]?[\d,]+\.?\d*\s*\[[^\]]*\]"

ROWS6 = ["HyInv", "ProteinZero V2 (ESM2)", "ProteinZero V2 (ESM1)", "ProteinMPNN grouped",
         "ProteinMPNN", "LigandMPNN", "ProteinMPNN (low-noise, grouped)", "PiFold",
         "LM-Design 650M", "CMLM", "DPLM-2 3B", "Native"]
COLS6 = ["CATH4.3 test", "CATH4.2 test", "TS500", "TS50", "RecentPDB", "RecentPDB, Boltz2", "RecentPDB, Protenix2"]
# Table 7 prints the ten baselines three times, under three different column groups.
ROWS7 = [r for r in ROWS6 if r not in ("HyInv", "Native")]
BLOCKS7 = [["CATH4.3 test", "CATH4.2 test", "TS500"],
           ["TS50", "RecentPDB, ESMFold2", "RecentPDB, Boltz2"],
           ["RecentPDB, Protenix2"]]
ROWS8 = ["Decoupled draft, Td = 0.6 (HyInv default)", "Decoupled draft, Td = 0.3",
         "Top-p 0.9", "Min-p 0.1"]
COLS8 = ["Development", "CATH4.3 test", "RecentPDB"]
ROWS9 = ["Subset 1", "Subset 2", "Subset 3", "Whole development panel"]

cells = {}


def body(label, pattern, lo, hi):
    pat = re.compile(r"(?:^|\s)" + re.escape(label) + r"\s+(" + pattern + r")\s*$")
    return [m.group(1) for l in lines[lo:hi] for m in [pat.search(l)] if m]


# Table 6: one line per method, seven numbers.
cap6 = next(i for i, l in enumerate(lines) if l.startswith("Table 6:"))
for row in ROWS6:
    hits = body(row, rf"(?:{NUM}\s+){{6}}{NUM}", cap6, cap6 + 25)
    assert len(hits) == 1, (row, hits)
    vals = hits[0].split()
    assert len(vals) == 7, (row, vals)
    for col, v in zip(COLS6, vals):
        cells[("Table 6", row, col)] = v

# Table 7: three groups of column headers; each baseline appears once per group, in order.
cap7 = next(i for i, l in enumerate(lines) if l.startswith("Table 7:"))
for row in ROWS7:
    hits = body(row, rf"(?:{BRACKET}\s+)*{BRACKET}", cap7 - 60, cap7 + 60)
    assert len(hits) == 3, (row, hits)
    for block, hit in zip(BLOCKS7, hits):
        vals = [v.strip() for v in re.findall(BRACKET, hit)]
        assert len(vals) == len(block), (row, block, vals)
        for col, v in zip(block, vals):
            cells[("Table 7", row, col)] = re.sub(r"\s+", " ", v)

# Table 8: three bracketed intervals per row.
cap8 = next(i for i, l in enumerate(lines) if l.startswith("Table 8:"))
for row in ROWS8:
    hits = body(row, rf"(?:{BRACKET}\s+){{2}}{BRACKET}", cap8, cap8 + 12)
    assert len(hits) == 1, (row, hits)
    vals = [re.sub(r"\s+", " ", v.strip()) for v in re.findall(BRACKET, hits[0])]
    assert len(vals) == 3, (row, vals)
    for col, v in zip(COLS8, vals):
        cells[("Table 8", row, col)] = v

# Table 9: chains, targets, clusters, one interval, then a yes/no verdict.
cap9 = next(i for i, l in enumerate(lines) if l.startswith("Table 9:"))
for row in ROWS9:
    hits = body(row, rf"[\d ,]+\s+\d+\s+({BRACKET})\s+(yes|no)", cap9, cap9 + 12)
    pat = re.compile(r"(?:^|\s)" + re.escape(row) + r"\s+[\d ,]+?\s+\d+\s+(" + BRACKET + r")\s+(yes|no)\s*$")
    hits = [(m.group(1), m.group(2)) for l in lines[cap9:cap9 + 12] for m in [pat.search(l)] if m]
    assert len(hits) == 1, (row, hits)
    cells[("Table 9", row, "S@D difference")] = re.sub(r"\s+", " ", hits[0][0].strip())
    cells[("Table 9", row, "Lower end >= -0.002")] = hits[0][1]

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
    printed = re.sub(r"\s+", " ", a["printed_value"]).replace("−", "-")
    want = cells[key].replace("−", "-")
    if printed != want:
        print("MISMATCH", r["id"], "| record", repr(printed), "| source", repr(want))
        bad += 1
    checked += 1
print(f"checked {checked} table cells, {bad} problems")
unrec = [(k, v) for k, v in cells.items() if k not in recorded]
print(f"printed cells of these tables not recorded: {len(unrec)}")
for k, v in sorted(unrec):
    print("  unrecorded", k, "=", v)
