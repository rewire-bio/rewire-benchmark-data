"""Build data/omics/hyplm-flash-20261106/batch.jsonl from the pinned report.

Usage: python3 -I build.py <path to HyPLM_Technical_Report.pdf> <output path>
The PDF is refetchable at the pinned commit; parse.py refuses any other bytes.
"""

import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rows
import rows2
from claims2 import build_claims
from entities import configurations, models, sources
from entities2 import entities2
from parse import parse


def main(pdf_path, out_path):
    parsed = parse(pdf_path)
    evidence, seen = rows.build(parsed)
    rows2.build(parsed, evidence, seen)
    records = sources() + models() + configurations() + entities2() + evidence + build_claims()
    ids = [r["id"] for r in records]
    dupes = [i for i, n in collections.Counter(ids).items() if n > 1]
    assert not dupes, dupes
    records.sort(key=lambda r: r["id"])
    with open(out_path, "w") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"{len(records)} records to {out_path}")
    for kind, n in sorted(collections.Counter(r["kind"] for r in records).items()):
        print(f"  {kind}: {n}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
