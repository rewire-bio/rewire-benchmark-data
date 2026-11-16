#!/usr/bin/env python3
"""Compare review/manual-transcription.tsv with the batch records.

The manual file was typed by eye from the rendered pages before any comparison.
This script matches each transcribed cell to the result whose source_locator
names that row and column, so a result sitting on the wrong row or column fails
here as well as in check_values_independent.py.

Usage: python3 -I cmp_manual.py <batch.jsonl> <manual-transcription.tsv>
"""

import json
import re
import sys

LOC_TABLE = re.compile(
    r"^Supplementary Table 3, row '(?P<row>.+)', column '(?P<col>.+)' \(PDF page 23\)$"
)
LOC_FIG4 = re.compile(r"^Fig\. 4b, row '(?P<row>.+)', printed bar label \(PDF page 7\)$")


def main():
    batch, manual = sys.argv[1], sys.argv[2]
    records = [json.loads(l) for l in open(batch)]

    by_cell, by_bar = {}, {}
    for r in records:
        if r["kind"] != "result":
            continue
        a = r["attributes"]
        m = LOC_TABLE.match(a["source_locator"])
        if m:
            key = (m["row"], m["col"])
            assert key not in by_cell, f"two results for cell {key}"
            by_cell[key] = r
            continue
        m = LOC_FIG4.match(a["source_locator"])
        if m:
            assert m["row"] not in by_bar, f"two results for bar {m['row']}"
            by_bar[m["row"]] = r

    problems, checked = [], 0
    seen_cells, seen_bars = set(), set()
    for line in open(manual):
        if line.startswith("#") or line.startswith("source\t") or not line.strip():
            continue
        kind, row, col, value = line.rstrip("\n").split("\t")
        checked += 1
        if kind == "suppl-table-3":
            seen_cells.add((row, col))
            r = by_cell.get((row, col))
            if r is None:
                problems.append(f"no result for cell {row!r} / {col!r}")
                continue
            a = r["attributes"]
            mean = value.split(" ")[0]
            if a["printed_source_cell"] != value:
                problems.append(
                    f"{row!r}/{col!r}: transcribed {value!r}, record has "
                    f"{a['printed_source_cell']!r}"
                )
            if a["printed_value"] != mean or a["numeric_value"] != mean:
                problems.append(
                    f"{row!r}/{col!r}: transcribed mean {mean}, record has "
                    f"{a['printed_value']}/{a['numeric_value']}"
                )
        elif kind == "fig-4b":
            seen_bars.add(row)
            r = by_bar.get(row)
            if r is None:
                problems.append(f"no result for Fig. 4b bar {row!r}")
                continue
            a = r["attributes"]
            if a["printed_value"] != value or a["numeric_value"] != value:
                problems.append(
                    f"Fig. 4b {row!r}: transcribed {value}, record has "
                    f"{a['printed_value']}/{a['numeric_value']}"
                )
        else:
            problems.append(f"unknown source {kind!r}")

    for key in sorted(set(by_cell) - seen_cells):
        problems.append(f"result for cell {key} was not transcribed")
    for key in sorted(set(by_bar) - seen_bars):
        problems.append(f"result for Fig. 4b bar {key!r} was not transcribed")

    print(f"{checked} transcribed values compared; {len(problems)} problems")
    for p in problems:
        print("  " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
