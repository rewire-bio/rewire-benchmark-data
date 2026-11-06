"""Build data/omics/hyinv-20261106/batch.jsonl from the pinned sources.

Usage: python3 -I build.py <path to HyInv_Technical_Report.pdf> <output path>

The PDF is not committed: refetch it from the pinned commit
(https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/0dcc533cc9f8f76c90ecbfe944df816b6672328a/AI4Science/hyinv/HyInv_Technical_Report.pdf)
and parse.py will refuse any file whose SHA-256 is not the pinned one.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claims import claims
from entities import entities
from evidence import evidence
from parse import parse


def main(pdf_path, out_path):
    records = entities() + evidence(parse(pdf_path)) + claims()
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), "duplicate record ids"
    records.sort(key=lambda r: r["id"])
    with open(out_path, "w") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    counts = {}
    for item in records:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1
    print(f"{len(records)} records to {out_path}")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
