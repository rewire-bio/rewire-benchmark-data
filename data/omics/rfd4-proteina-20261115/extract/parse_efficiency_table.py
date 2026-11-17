#!/usr/bin/env python3
"""Parse the "Measured design efficiency" table from the pinned RFD4-Proteina model card.

Input: the gzipped model card archived in ../artifacts/hf_README.md.gz, whose uncompressed
bytes must hash to the artifact_sha256 on source rfd4-proteina-20261115-source-hf-model-card.

The parser locates the table by its own heading, asserts the four printed row labels and the
printed header cells, and writes extract/efficiency-table.json. It then cross-checks every
value against benchmarks/summary.csv from the same pinned revision: the card prints passers
per GPU-hour and summary.csv prints the same quantity per 10 GPU-minutes, so each card value
must equal its summary.csv row times six, to the card's two decimal places. The cross-check
also records which protocol row each card cell came from, which is how the conditioning of
each comparator row is established (ppi_backbone against ppi_all_atom, dna_unfixed against
dna_fixed).

Run: python3 -I extract/parse_efficiency_table.py
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import pathlib
import re
import sys
from decimal import ROUND_HALF_EVEN, Decimal

HERE = pathlib.Path(__file__).resolve().parent
ARTIFACTS = HERE.parent / "artifacts"

CARD_SHA256 = "38479d8e4c6e46ed7e1ec4ece0dd02c358ae46d73d56790c44be813201fd9b98"
SUMMARY_SHA256 = "5c6d525d988d0df7fecb74396f86401c1ddb4c31fa83f00b357ba77d855d8a10"

EXPECTED_HEADER = [
    "Benchmark",
    "Targets",
    "RFD4-Proteína, high thinking",
    "Best other method in this comparison",
]
EXPECTED_ROW_LABELS = ["Protein binders", "Small-molecule binders", "Atomic Motif Enzyme", "DNA binders"]

# Which summary.csv row each printed cell must reproduce. Taken from the printed row label and
# the printed comparator name, not guessed: the card names the comparator in the cell itself.
SUMMARY_ROWS = {
    ("Protein binders", "rfd4"): ("ppi", "RFD4-Proteina (high thinking)", "ppi"),
    ("Protein binders", "other"): ("ppi", "Proteina-Complexa", "ppi"),
    ("Small-molecule binders", "rfd4"): ("small_molecule", "RFD4-Proteina (high thinking)", "sm_binder"),
    ("Small-molecule binders", "other"): ("small_molecule", "BoltzGen", "sm_binder"),
    ("Atomic Motif Enzyme", "rfd4"): ("ame", "RFD4-Proteina (high thinking)", "ame"),
    ("Atomic Motif Enzyme", "other"): ("ame", "AlphaProtein-novo (Codesign)", "ame"),
    ("DNA binders", "rfd4"): ("dna", "RFD4-Proteina (high thinking)", "dna"),
    ("DNA binders", "other"): ("dna", "BoltzGen (fixed)", "dna"),
}


def read_archived(name: str, expected_sha256: str) -> str:
    raw = gzip.decompress((ARTIFACTS / f"{name}.gz").read_bytes())
    got = hashlib.sha256(raw).hexdigest()
    assert got == expected_sha256, f"{name}: sha256 {got} != pinned {expected_sha256}"
    return raw.decode("utf-8")


def split_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def strip_markup(cell: str) -> str:
    return re.sub(r"\*\*|__", "", cell).strip()


def parse_card_table(card: str) -> dict:
    heading = "## Measured design efficiency"
    start = card.index(heading)
    end = card.index("\n## ", start + len(heading))
    section = card[start:end]

    note = re.search(r"^> (.+?)(?:\n>?\s*\n|\n[^>])", section, re.S | re.M)
    assert note, "the scope note above the table was not found"
    note_text = " ".join(line.lstrip("> ").strip() for line in note.group(1).splitlines()).strip()
    assert "previous release pair" in note_text, note_text
    assert "October 9, 2026 frozen project benchmark" in note_text, note_text

    metric = re.search(r"\*\*Metric:\*\*\s*(.+?)\s*(?:Higher is better\.)", section, re.S)
    assert metric, "the printed metric definition was not found"
    metric_text = " ".join(metric.group(1).split()).rstrip(".")

    table = [line for line in section.splitlines() if line.strip().startswith("|")]
    assert len(table) == 6, f"expected a header, a rule and four rows, got {len(table)} table lines"
    header = [strip_markup(c) for c in split_row(table[0])]
    assert header == EXPECTED_HEADER, f"header {header!r} != {EXPECTED_HEADER!r}"
    assert set(split_row(table[1])[0]) <= set("-: "), f"row 2 is not the rule: {table[1]!r}"

    rows = []
    for line in table[2:]:
        cells = split_row(line)
        assert len(cells) == 4, f"expected four cells, got {cells!r}"
        label = strip_markup(cells[0])
        targets = strip_markup(cells[1])
        rfd4 = strip_markup(cells[2])
        other = strip_markup(cells[3])
        assert "·" in other, f"comparator cell has no printed separator: {other!r}"
        other_name, other_value = (part.strip() for part in other.split("·", 1))
        rows.append(
            {
                "benchmark_label": label,
                "targets_printed": targets,
                "rfd4_printed_value": rfd4,
                "rfd4_printed_cell": cells[2].strip(),
                "comparator_printed_name": other_name,
                "comparator_printed_value": other_value,
                "comparator_printed_cell": other,
            }
        )

    labels = [r["benchmark_label"] for r in rows]
    assert labels == EXPECTED_ROW_LABELS, f"row labels {labels!r} != {EXPECTED_ROW_LABELS!r}"
    for row in rows + []:
        for key in ("rfd4_printed_value", "comparator_printed_value"):
            assert re.fullmatch(r"\d+\.\d{2}", row[key]), f"{key} not printed to two decimals: {row[key]!r}"
        assert re.fullmatch(r"\d+", row["targets_printed"]), row["targets_printed"]

    attempts = re.search(r"There are (\d+) original attempts per target\.", section)
    assert attempts, "the printed attempts-per-target sentence was not found"

    return {
        "scope_note": note_text,
        "metric_definition": metric_text,
        "attempts_per_target": int(attempts.group(1)),
        "rows": rows,
        "conditioning_note": " ".join(
            re.search(r"(Conditioning differs between some methods:.*?)\n\n", section, re.S).group(1).split()
        ),
    }


def cross_check(table: dict, summary_csv: str) -> dict:
    rows = list(csv.DictReader(io.StringIO(summary_csv)))
    assert len(rows) == 52, f"summary.csv has {len(rows)} data rows, expected 52"
    index = {(r["panel"], r["label"].replace("\n", " ").strip(), r["criterion"]): r for r in rows}
    checks = {}
    for row in table["rows"]:
        label = row["benchmark_label"]
        for side, printed_key, name_key in (
            ("rfd4", "rfd4_printed_value", None),
            ("other", "comparator_printed_value", "comparator_printed_name"),
        ):
            panel, csv_label, criterion = SUMMARY_ROWS[(label, side)]
            if name_key:
                printed_name = row[name_key]
                assert csv_label.startswith(printed_name.split(" (")[0]), (
                    f"printed comparator {printed_name!r} does not match summary.csv label {csv_label!r}"
                )
            source_row = index[(panel, csv_label, criterion)]
            per_hour = (Decimal(source_row["unique_per_10_gpu_min"]) * 6).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_EVEN
            )
            printed = Decimal(row[printed_key])
            assert per_hour == printed, (
                f"{label} {side}: summary.csv gives {per_hour} per GPU-hour, card prints {printed}"
            )
            assert int(source_row["targets"]) == int(row["targets_printed"]), (
                f"{label}: summary.csv targets {source_row['targets']} != printed {row['targets_printed']}"
            )
            checks[f"{label}|{side}"] = {
                "summary_panel": panel,
                "summary_label": csv_label,
                "summary_criterion": criterion,
                "summary_protocol": source_row["protocol"],
                "summary_dataset": source_row["dataset"],
                "summary_unique_per_10_gpu_min": source_row["unique_per_10_gpu_min"],
                "summary_attempts": int(source_row["attempts"]),
                "recomputed_per_gpu_hour": str(per_hour),
            }
            assert int(source_row["attempts"]) == int(row["targets_printed"]) * table["attempts_per_target"], (
                f"{label}: attempts {source_row['attempts']} != targets x attempts per target"
            )
    return checks


def main() -> int:
    card = read_archived("hf_README.md", CARD_SHA256)
    summary_csv = read_archived("hf_benchmarks_summary.csv", SUMMARY_SHA256)
    table = parse_card_table(card)
    table["summary_cross_check"] = cross_check(table, summary_csv)
    table["inputs"] = {
        "model_card_sha256": CARD_SHA256,
        "summary_csv_sha256": SUMMARY_SHA256,
    }
    out = HERE / "efficiency-table.json"
    out.write_text(json.dumps(table, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out} with {len(table['rows'])} rows and {len(table['summary_cross_check'])} cross-checked cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
