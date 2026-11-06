"""Build data/omics/hycell-20261106/batch.jsonl from the pinned report and README.

Usage: python3 -I build.py <HyCell_Technical_Report.pdf> <README.md> <output path>
"""

import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import evidence
import evidence2
from assess import benchmark, datasets
from claims2 import build_claims
from models import configurations, models
from parse import parse
from protocols import protocols
from sources import sources
from sources2 import sources2

README_SHA = "cd2eb7ae932124cacf9875b0ed1c48504b3e95b8e36169520bd1fe83cc0eecde"


def check_readme(readme, parsed):
    """The README's two tables repeat the report; assert every repeated cell."""
    import hashlib
    raw = open(readme, "rb").read()
    assert hashlib.sha256(raw).hexdigest() == README_SHA, "README hash"
    text = raw.decode()
    names = {"HyCell": "HyCell", "Stack": "Stack (batch-grouped inference)",
             "SCimilarity": "SCimilarity (trained with cell-type labels)",
             "scFoundation": "scFoundation", "UCE": "UCE", "PCA": "PCA of the counts"}
    for model, shown in names.items():
        line = next(l for l in text.splitlines() if l.startswith("| ") and shown in l
                    and re.search(r"0\.\d{3}", l))
        values = re.findall(r"0\.\d{3}", line)
        t3 = parsed["table3"][model]
        assert values == [t3[c] for c in ["S", "Bio", "Batch", "LR", "kNN"]], (model, values)
    for atlas, row in parsed["table5"].items():
        line = next(l for l in text.splitlines() if l.startswith(f"| {atlas} |"))
        assert re.findall(r"0\.\d{3}", line) == [row["Fine-tuned"], row["Frozen + LR"],
                                                  row["Frozen + kNN"]], atlas
    assert "0.735" in text and "0.736" in text and "0.676" in text


def main(pdf, readme, out_path):
    parsed = parse(pdf)
    check_readme(readme, parsed)
    o = evidence.build(parsed)
    evidence2.build(parsed, o)
    records = (sources() + sources2() + models() + configurations() + benchmark() + datasets()
               + protocols() + o.records + build_claims())
    dupes = [i for i, n in collections.Counter(r["id"] for r in records).items() if n > 1]
    assert not dupes, dupes
    records.sort(key=lambda r: r["id"])
    with open(out_path, "w") as handle:
        for item in records:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"{len(records)} records to {out_path}")
    for kind, n in sorted(collections.Counter(r["kind"] for r in records).items()):
        print(f"  {kind}: {n}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
