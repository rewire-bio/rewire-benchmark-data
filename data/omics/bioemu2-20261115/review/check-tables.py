"""Independent reviewer parse of the two MODEL_CARD.md tables, compared with the claims."""
import json, pathlib, re, sys
BATCH = pathlib.Path(sys.argv[1]); REFETCH = pathlib.Path(sys.argv[2])
card = (REFETCH / "repo_MODEL_CARD.md").read_text(encoding="utf-8")
rows = [
    [c.strip() for c in line.strip().strip("|").split("|")]
    for line in card.splitlines()
    if line.startswith("|") and not re.fullmatch(r"\|[-| ]+\|", line.strip())
]
summary = {r[0]: r[1] for r in rows if len(r) == 2 and r[0] != "**Field**"}
training = {r[0]: (r[1], r[2]) for r in rows if len(r) == 3 and r[0] != "**Dataset**"}
print("summary rows:", len(summary), "training rows:", len(training))
recs = {json.loads(l)["id"]: json.loads(l) for l in (BATCH / "batch.jsonl").open()}
problems = 0
for rid, rec in recs.items():
    if rec["kind"] != "claim": continue
    a = rec["attributes"]; loc = a["source_locator"]; val = a["value"]
    m = re.search(r'Training data table, row "(.+?)"', loc)
    if m:
        name = m.group(1)
        if name not in training:
            print("ROW LABEL NOT IN TABLE:", rid, name); problems += 1; continue
        modality, count = training[name]
        expect = f"{name}: {count} train sequences/systems; modality {modality}"
        if val != expect:
            print("MISMATCH:", rid, "\n  claim:", val, "\n  table:", expect); problems += 1
        del training[name]
        continue
    m = re.search(r'Model summary table, row "(.+?)"', loc)
    if m:
        name = m.group(1)
        if name not in summary:
            print("SUMMARY ROW NOT IN TABLE:", rid, name); problems += 1; continue
        cell = summary.pop(name)
        norm = cell.replace("–", " to ").rstrip(".")
        norm = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", lambda mm: f"{mm.group(1)} at {mm.group(2)}", norm)
        if val.rstrip(".") != norm and val != cell.rstrip("."):
            print("SUMMARY MISMATCH:", rid, "\n  claim:", repr(val), "\n  cell: ", repr(cell)); problems += 1
print("training rows with no claim:", list(training))
print("summary rows with no claim:", list(summary))
print("problems:", problems)
