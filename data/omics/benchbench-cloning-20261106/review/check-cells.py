"""Reviewer check of the BenchBench-Cloning tables, independent of extract/parse_tables.py and
extract/check_tables.py.

Each table's body sits above its own caption in this document, so bodies are located by their
header line rather than by caption proximity: that is the layout that makes the repository's own
table parser answer a Table G1 request with Table G2's body. Every row is split on runs of two or
more spaces, so a cell cannot be taken from a neighbouring column, and the column order comes from
the printed header.
"""
import json
import re
import sys

TXT, BATCH = sys.argv[1], sys.argv[2]
lines = open(TXT).read().splitlines()

SYSTEMS = ["GPT-6 Astra", "GPT-6.1 Sol", "Claude Opus 5.5", "Gemini 4 Argon", "Claude Mythos 5.1",
           "Grok 4.7", "Kimi K3", "Gemini 3.8 Flash"]
EFFORTS = {"GPT-6 Astra": ["low", "high", "max"], "GPT-6.1 Sol": ["low", "high", "max"],
           "Claude Opus 5.5": ["low", "high", "max"], "Gemini 4 Argon": ["low", "medium", "high"],
           "Claude Mythos 5.1": ["low", "high", "max"], "Grok 4.7": ["low", "high", "xhigh"],
           "Kimi K3": ["low", "medium", "high"], "Gemini 3.8 Flash": ["low", "medium", "high"]}
TASKS = ["Matched promoter panel", "GFP into EcoFlex vector", "Insulin intermediate construct",
         "Minimal-edit recoding", "Reporter choice from data", "Insulin two-chain constructs",
         "MPRA construct rebuild", "AG/AP1 chimera plasmid", "Detector choice from antibody data",
         "Alkaloid-pathway GoldenBraid set", "Tus/TerB HEK293 constructs",
         "Prime-assembly donor family", "Synthetic-chromosome locus edit",
         "Sodium-channel promoter repair", "Dual-luciferase frame panel"]
RATE = r"-?\d+\.\d\s*\[\s*-?\d+\.\d\s*,\s*-?\d+\.\d\s*\]"

cells = {}

# Table D2: body above the "Table D2:" caption, found by its own header line.
# Table 2 shares D2's column headings, so D2's header is the one that also has a Tier column.
d2_header = next(i for i, l in enumerate(lines)
                 if "Protocol dev. %" in l and "Aggregate %" in l and "Tier" in l)
t2_header = next(i for i, l in enumerate(lines)
                 if "Protocol dev. %" in l and "Aggregate %" in l and "Tier" not in l)
d2, tiers = {}, {}
for l in lines[d2_header + 1:d2_header + 30]:
    rates = re.findall(RATE, l)
    if len(rates) != 3:
        continue
    label = l[:l.index(rates[0].split("[")[0].strip())]
    parts = [p for p in re.split(r"\s{2,}", label.strip()) if p]
    system, tier, effort = parts[0], parts[1], parts[2]
    assert system in SYSTEMS, (system, l[:60])
    d2[(system, effort)] = [re.sub(r"\s+", " ", r) for r in rates]
    tiers[(system, effort)] = tier
assert len(d2) == 24, len(d2)

# Table 2: the same three rate columns for the eight top-effort lanes, no Tier column. The
# extractor asserts it duplicates D2's top rows cell for cell; that is checked here, not assumed.
t2 = {}
for l in lines[t2_header + 1:t2_header + 12]:
    rates = re.findall(RATE, l)
    if len(rates) != 3:
        continue
    system = next(s for s in SYSTEMS if l.strip().startswith(s))
    t2[system] = [re.sub(r"\s+", " ", r) for r in rates]
assert len(t2) == 8, len(t2)
for (system, effort), vals in d2.items():
    tier = [t for (sy, ef), t in tiers.items() if sy == system and ef == effort][0]
    for col, v in zip(["Protocol dev. % [95% CI]", "Construct design % [95% CI]",
                       "Aggregate % [95% CI]"], vals):
        cells[("Table D2", f"{system}|{tier}|{effort}", col)] = v

# Table G1: eight system rows, three rate columns then two integer counts.
g1_header = next(i for i, l in enumerate(lines) if "pass@1 %" in l and "Solved" in l)
g1 = {}
for l in lines[g1_header + 1:g1_header + 12]:
    rates = re.findall(RATE, l)
    if len(rates) != 3:
        continue
    system = next(s for s in SYSTEMS if l.strip().startswith(s))
    tail = l[l.index(rates[2]) + len(rates[2]):]
    counts = re.findall(r"\b\d+\b", tail.split("k =")[0])
    assert len(counts) == 2, (system, tail)
    g1[system] = rates + counts
assert len(g1) == 8, len(g1)
for system, vals in g1.items():
    for col, v in zip(["pass@1 % [95% CI]", "pass@5 % [95% CI]", "pass@10 % [95% CI]",
                       "Solved >=1", "Solved all"], vals):
        cells[("Table G1", system, col)] = re.sub(r"\s+", " ", v)

# Table G2: fifteen task rows, eight "n/5" cells each.
g2_start = next(i for i, l in enumerate(lines) if l.strip().startswith("Task") and "Astra" in l)
g2 = {}
for l in lines[g2_start:g2_start + 20]:
    solves = re.findall(r"\b\d/5\b", l)
    if len(solves) != 8:
        continue
    task = next((t for t in TASKS if l.strip().startswith(t)), None)
    assert task, l[:60]
    g2[task] = solves
assert len(g2) == 15, len(g2)
for task, vals in g2.items():
    for system, v in zip(SYSTEMS, vals):
        cells[("Table G2", task, system)] = v

# Independent arithmetic: each G2 column sums to the top-effort construct numerator over 75, and
# each G1 Solved>=1 over 50 equals the printed pass@10.
TOP = {"GPT-6 Astra": "max", "GPT-6.1 Sol": "max", "Claude Opus 5.5": "max",
       "Gemini 4 Argon": "high", "Claude Mythos 5.1": "max", "Grok 4.7": "xhigh",
       "Kimi K3": "high", "Gemini 3.8 Flash": "high"}
for n, system in enumerate(SYSTEMS):
    total = sum(int(g2[t][n][0]) for t in TASKS)
    printed = float(d2[(system, TOP[system])][1].split("[")[0])
    assert abs(total / 75 * 100 - printed) <= 0.05, (system, total, printed)
    solved = int(g1[system][3])
    at10 = float(g1[system][2].split("[")[0])
    assert abs(solved / 50 * 100 - at10) <= 0.05, (system, solved, at10)
print("arithmetic: all 8 G2 column sums match the printed construct rate over 75, "
      "and all 8 Solved>=1 over 50 match the printed pass@10")

LOC_D2 = re.compile(r"^(Table D2), row '([^']+)' tier '([^']+)' effort '([^']+)', column '([^']+)'")
LOC_OTHER = re.compile(r"^(Table (?:G1|G2)), row '([^']+)', column '([^']+)'")


def split_printed(text):
    """A printed rate cell as (value, interval) so each is compared against its own field."""
    m = re.match(r"\s*(-?\d+\.\d)\s*\[\s*(-?\d+\.\d)\s*,\s*(-?\d+\.\d)\s*\]\s*$", text)
    return (m.group(1), (m.group(2), m.group(3))) if m else (text.strip(), None)
checked = bad = 0
recorded = set()
for line in open(BATCH):
    r = json.loads(line)
    if r["kind"] != "result":
        continue
    a = r["attributes"]
    m = LOC_D2.match(a["source_locator"])
    key = (m[1], f"{m[2]}|{m[3]}|{m[4]}", m[5]) if m else None
    if key is None:
        m = LOC_OTHER.match(a["source_locator"])
        if not m:
            continue
        key = (m[1], m[2], m[3])
    recorded.add(key)
    if key not in cells:
        print("NO SUCH CELL", r["id"], key)
        bad += 1
        continue
    want, interval = split_printed(cells[key])
    got = a["printed_value"].strip()
    if got != want:
        print("MISMATCH", r["id"], "| record", repr(got), "| source", repr(want))
        bad += 1
    if interval:
        unc = a.get("uncertainty") or {}
        if (unc.get("lower"), unc.get("upper")) != interval:
            print("INTERVAL MISMATCH", r["id"], "| record",
                  (unc.get("lower"), unc.get("upper")), "| source", interval)
            bad += 1
    elif a.get("uncertainty"):
        print("UNEXPECTED INTERVAL", r["id"])
        bad += 1
    checked += 1
print(f"checked {checked} cells of Tables D2, G1 and G2; {bad} problems")
unrec = sorted(k for k in cells if k not in recorded)
print(f"printed cells of those tables not recorded: {len(unrec)}")
for k in unrec[:12]:
    print("  unrecorded", k, "=", cells[k])
