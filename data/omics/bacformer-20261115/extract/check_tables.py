#!/usr/bin/env python3
"""Re-read the six benchmark tables by column position and compare with extract/tables.json.

This check does not use parse_tables.py. It finds each table's printed metric header line,
takes the character position of each metric label from that header, and assigns every
"mean +/- sd" cell in the rows below to the header column nearest to the cell's own character
position. A value copied from a neighbouring column therefore fails the comparison. Row labels
are read from the lines themselves, not from a list, so a missing or extra row also fails.

Usage: python3 extract/check_tables.py [text-layer.gz] [tables.json]
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_TEXT = HERE.parent / "artifacts" / "biorxiv-665723v3-text-layer.txt.gz"
DEFAULT_TABLES = HERE / "tables.json"
TEXT_SHA256 = "86636e89b167d7304b3a83ee7f159cad0a9bdbe97019588ce836087b8fe3b0b2"

# Caption text, the metric header labels in printed order, and the column names used in
# tables.json. Captions and headers are read from the pinned text layer.
SPECS = [
    {
        "key": "S1",
        "caption": "Table S1. Overall operon identification performance across methods.",
        "header": ["AUROC", "AUPRC"],
        "columns": ["AUROC", "AUPRC"],
    },
    {
        "key": "S12",
        "caption": "Table S12. Clustering performance across species-level genome clustering",
        "header": ["ARI", "NMI", "ASW"],
        "columns": ["ARI", "NMI", "ASW"],
    },
    {
        "key": "S13",
        "caption": "Table S13. Protein–protein interaction performance on held-out genomes.",
        "header": ["AUROC", "AUPRC", "AUROC", "AUPRC"],
        "columns": ["Zero-shot AUROC", "Zero-shot AUPRC", "Finetuned AUROC", "Finetuned AUPRC"],
    },
    {
        "key": "S14",
        "caption": "Table S14. Performance on gene–essentiality prediction.",
        "header": ["AUROC", "AUPRC"],
        "columns": ["AUROC", "AUPRC"],
    },
    {
        "key": "S16",
        "caption": "Table S16. Overall phenotypic traits prediction performance across all phenotypes.",
        "header": ["AUROC", "AUPRC"],
        "columns": ["AUROC", "AUPRC"],
    },
    {
        "key": "S18",
        "caption": "Table S18. Performance (percent, higher is better) on antibiotic-resistance prediction tasks",
        "header": ["AUROC", "AUPRC", "R2", "Pearson"],
        "columns": ["Binary AUROC", "Binary AUPRC", "Regression R2", "Regression Pearson"],
    },
]

CELL = re.compile(r"\d+\.\d+\s*±\s*\d+\.\d+")
LABEL = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 .\-]*?)\s\s+\d")


def load_text(path: Path) -> list[str]:
    raw = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != TEXT_SHA256:
        raise SystemExit(f"text layer SHA-256 {digest} does not match the pinned {TEXT_SHA256}")
    return raw.decode("utf-8").splitlines()


def header_positions(line: str, labels: list[str]) -> list[int]:
    """Character centre of each metric label on the header line, in printed order."""
    positions: list[int] = []
    cursor = 0
    for label in labels:
        at = line.find(label, cursor)
        if at < 0:
            raise SystemExit(f"header label {label!r} not found in {line!r}")
        positions.append(at + len(label) // 2)
        cursor = at + len(label)
    return positions


def read_table(lines: list[str], spec: dict) -> dict[tuple[str, str], str]:
    caption_at = [i for i, line in enumerate(lines) if spec["caption"] in " ".join(line.split())]
    if len(caption_at) != 1:
        raise SystemExit(f"{spec['key']}: expected one caption, found {len(caption_at)}")
    end = caption_at[0]
    header_at = None
    for i in range(end - 1, max(end - 60, -1), -1):
        stripped = " ".join(lines[i].split())
        if stripped == " ".join(spec["header"]) or stripped.endswith(" ".join(spec["header"])):
            header_at = i
            break
    if header_at is None:
        raise SystemExit(f"{spec['key']}: metric header {spec['header']} not found above the caption")
    centres = header_positions(lines[header_at], spec["header"])
    cells: dict[tuple[str, str], str] = {}
    for line in lines[header_at + 1 : end]:
        found = list(CELL.finditer(line))
        if not found:
            continue
        label_match = LABEL.match(line)
        if not label_match:
            raise SystemExit(f"{spec['key']}: value line without a row label: {line!r}")
        label = " ".join(label_match.group(1).split())
        for match in found:
            centre = (match.start() + match.end()) // 2
            index = min(range(len(centres)), key=lambda k: abs(centres[k] - centre))
            key = (label, spec["columns"][index])
            if key in cells:
                raise SystemExit(f"{spec['key']}: two values for {key}")
            cells[key] = " ".join(match.group(0).split())
    return cells


def main() -> None:
    text_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TEXT
    tables_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_TABLES
    lines = load_text(text_path)
    parsed = json.loads(tables_path.read_text())["tables"]
    checked = 0
    problems: list[str] = []
    for spec in SPECS:
        mine = read_table(lines, spec)
        theirs = {
            (row["label"], cell["column"]): cell["printed_value"]
            for row in parsed[spec["key"]]["rows"]
            for cell in row["cells"]
        }
        for key in sorted(set(mine) | set(theirs)):
            if mine.get(key) != theirs.get(key):
                problems.append(f"{spec['key']} {key}: column check {mine.get(key)!r} vs tables.json {theirs.get(key)!r}")
            else:
                checked += 1
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"column-position check agrees on all {checked} cells")


if __name__ == "__main__":
    main()
