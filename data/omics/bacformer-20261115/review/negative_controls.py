"""Negative controls for recheck_cells.py: prove the checker fails on planted errors.

A checker that passes tells you nothing until you know it can fail. This writes three mutated
copies of batch.jsonl, each carrying exactly one kind of planted error, runs recheck_cells.py on
each, and requires every one of them to be rejected.

  swapped-values      two cells of one row exchange their values, locators unchanged
  neighbour-value     one cell takes the value printed in the column beside it
  shifted-columns     every locator of one table names the column one to its right

Usage: python3 -I negative_controls.py <bbox.xml> <batch.jsonl> <work dir>
"""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def save(records, path):
    with open(path, "w") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def by_id(records, rid):
    for r in records:
        if r["id"] == rid:
            return r
    raise SystemExit(f"{rid} not in the batch")


def swapped_values(records):
    """Exchange the values of two cells printed in the same row of Table S13."""
    a = by_id(records, "bacformer-20261115-result-ppi-bacformer-zero-shot-auroc")
    b = by_id(records, "bacformer-20261115-result-ppi-bacformer-zero-shot-auprc")
    for key in ("printed_value", "numeric_value", "uncertainty"):
        a["attributes"][key], b["attributes"][key] = b["attributes"][key], a["attributes"][key]
    return records


def neighbour_value(records):
    """Give one Table S18 cell the value printed in the column beside it."""
    target = by_id(records, "bacformer-20261115-result-amr-bacformer-binary-auroc")
    source = by_id(records, "bacformer-20261115-result-amr-bacformer-binary-auprc")
    for key in ("printed_value", "numeric_value"):
        target["attributes"][key] = source["attributes"][key]
    return records


def shifted_columns(records):
    """Move every Table S18 locator one column to the right, keeping the values."""
    order = ["Binary AUROC", "Binary AUPRC", "Regression R2", "Regression Pearson"]
    for r in records:
        if r.get("kind") != "result":
            continue
        loc = r["attributes"]["source_locator"]
        if not loc.startswith("Table S18, "):
            continue
        for i, col in enumerate(order):
            if loc.endswith(f"column '{col}'"):
                r["attributes"]["source_locator"] = loc.replace(
                    f"column '{col}'", f"column '{order[(i + 1) % len(order)]}'")
                break
    return records


CONTROLS = {
    "swapped-values": swapped_values,
    "neighbour-value": neighbour_value,
    "shifted-columns": shifted_columns,
}


def main(argv):
    bbox, batch, work = argv[0], argv[1], Path(argv[2])
    work.mkdir(parents=True, exist_ok=True)
    failures = []
    for name, mutate in CONTROLS.items():
        path = work / f"batch-{name}.jsonl"
        save(mutate(load(batch)), path)
        run = subprocess.run([sys.executable, "-I", str(HERE / "recheck_cells.py"), bbox,
                              str(path)], capture_output=True, text=True)
        rejected = run.returncode != 0
        print(f"=== {name}: {'rejected' if rejected else 'ACCEPTED'} (exit {run.returncode})")
        for line in run.stdout.splitlines():
            if line.startswith("MISMATCH") or line.startswith("mismatches"):
                print("    " + line)
        if run.stderr.strip():
            print("    " + run.stderr.strip().splitlines()[-1])
        if not rejected:
            failures.append(name)
    clean = subprocess.run([sys.executable, "-I", str(HERE / "recheck_cells.py"), bbox, batch],
                           capture_output=True, text=True)
    print(f"=== unmutated batch: {'accepted' if clean.returncode == 0 else 'REJECTED'} "
          f"(exit {clean.returncode})")
    if clean.returncode != 0:
        failures.append("unmutated batch")
    if failures:
        print("control failed for: " + ", ".join(failures))
        return 1
    print("every planted error was rejected and the unmutated batch was accepted")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
