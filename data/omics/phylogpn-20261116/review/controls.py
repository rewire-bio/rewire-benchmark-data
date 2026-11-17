#!/usr/bin/env python3
"""Negative controls for review/reread.py.

Each control writes a mutated copy of batch.jsonl to a temporary directory and runs
reread.py against it. A control passes when reread.py exits non-zero and its output
names the record that was mutated. Nothing under the batch folder is changed.

Usage:
  python3 -I controls.py <fulltext.xml.gz> <batch.jsonl> <scratch-dir>
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

CONTROLS = [
    # (name, record id, what to change)
    ("swapped values within a row",
     "phylogpn-20261116-result-t1-utr3-phylogpn",
     {"printed_value": "0.63", "numeric_value": "0.63"}),
    ("value shifted one column",
     "phylogpn-20261116-result-t2-histone-phylogpn",
     {"source_locator": "Table 2, row 'PhyloGPN', column 'CpG Methylation (AUROC)'"}),
    ("row label shifted one row",
     "phylogpn-20261116-result-t1-missense-caduceus",
     {"source_locator": "Table 1, row 'Noncoding', column 'Caduceus'"}),
    ("a printed N/A cell recorded as zero",
     "phylogpn-20261116-result-t2-chromatin-gpn-msa-zero-control",
     None),  # handled below: this result does not exist, so the control adds one
]


def run(xml_path, batch_path, out_path):
    result = subprocess.run(
        [sys.executable, "-I", os.path.join(HERE, "reread.py"), xml_path, out_path],
        capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def main():
    xml_path, batch_path, scratch = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(scratch, exist_ok=True)
    records = [json.loads(line) for line in open(batch_path)]

    baseline_path = os.path.join(scratch, "baseline.jsonl")
    with open(baseline_path, "w") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
    code, out = run(xml_path, batch_path, baseline_path)
    print(f"[baseline] exit {code} (expected 0)")
    if code != 0:
        print(out)
        sys.exit("baseline copy does not pass; the controls prove nothing")

    failures = []
    for index, (name, rid, patch) in enumerate(CONTROLS):
        mutated = json.loads(json.dumps(records))
        if patch is None:
            # Add a result for a cell the paper prints as N/A, with a zero value.
            template = next(r for r in mutated
                            if r["id"] == "phylogpn-20261116-result-t2-histone-gpn-msa")
            fake = json.loads(json.dumps(template))
            fake["id"] = rid
            fake["attributes"]["printed_value"] = "0.00"
            fake["attributes"]["numeric_value"] = "0.00"
            fake["attributes"]["source_locator"] = (
                "Table 2, row 'GPN-MSA', column 'Chromatin Accessibility (AUROC)'")
            mutated.append(fake)
        else:
            target = next(r for r in mutated if r["id"] == rid)
            target["attributes"].update(patch)
        out_path = os.path.join(scratch, f"control-{index}.jsonl")
        with open(out_path, "w") as handle:
            for record in mutated:
                handle.write(json.dumps(record) + "\n")
        code, out = run(xml_path, batch_path, out_path)
        caught = code != 0 and rid in out
        print(f"[control {index}] {name}: exit {code}, record named: {rid in out} "
              f"-> {'CAUGHT' if caught else 'MISSED'}")
        for line in out.splitlines():
            if rid in line or "PROBLEMS" in line or "printed" in line and "no result" in line:
                print(f"    {line.strip()}")
        if not caught:
            failures.append(name)

    if failures:
        sys.exit(f"controls not caught: {failures}")
    print("\nEvery control was caught.")


if __name__ == "__main__":
    main()
