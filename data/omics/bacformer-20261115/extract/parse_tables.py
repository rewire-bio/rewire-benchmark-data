#!/usr/bin/env python3
"""Parse the benchmark tables of the Bacformer preprint (bioRxiv 2025.07.20.665723v3).

Input is the archived `pdftotext -layout` text layer of the pinned PDF
(artifacts/biorxiv-665723v3-text-layer.txt.gz). The script refuses to run if the
text layer does not match the recorded SHA-256.

Each table is located by its own printed caption line. Only the lines between the
previous caption (or the "SUPPLEMENTARY TABLES" heading) and that caption are
searched, so a figure legend or a neighbouring table cannot supply a row. Every
expected row label is asserted, in the printed order, and every row must print
exactly as many "mean +/- sd" cells as the table has value columns.

Usage: python3 extract/parse_tables.py [text-layer.gz] [out.json]
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
DEFAULT_OUT = HERE / "tables.json"

# SHA-256 of the decompressed `pdftotext -layout` text layer of the pinned PDF.
TEXT_SHA256 = "86636e89b167d7304b3a83ee7f159cad0a9bdbe97019588ce836087b8fe3b0b2"

# Row labels in the order each table prints them. The twelve benchmarked systems appear in two
# different printed orders: Tables S1 and S14 list Evo and Evo-2 second and third, while Tables
# S13, S16 and S18 list them fifth and sixth. Both orders are asserted as printed.
BENCH_12_A = [
    "Mistral-DNA",
    "Evo",
    "Evo-2",
    "DNABERT-2",
    "Nucleotide Transformer",
    "ProkBERT",
    "ProtBERT",
    "ESM-2",
    "ESM-C",
    "gLM2",
    "Bacformer",
    "Bacformer Large",
]
BENCH_12_B = [
    "Mistral-DNA",
    "DNABERT-2",
    "Nucleotide Transformer",
    "ProkBERT",
    "Evo",
    "Evo-2",
    "ESM-2",
    "ESM-C",
    "ProtBERT",
    "gLM2",
    "Bacformer",
    "Bacformer Large",
]

TABLES = [
    {
        "key": "S1",
        "caption": "Table S1. Overall operon identification performance across methods.",
        "columns": ["AUROC", "AUPRC"],
        "rows": BENCH_12_A,
    },
    {
        "key": "S12",
        "caption": "Table S12. Clustering performance across species-level genome clustering",
        "columns": ["ARI", "NMI", "ASW"],
        "rows": ["gLM2", "ProtBERT", "ESM-2", "ESM-C", "Bacformer", "Bacformer Large"],
    },
    {
        "key": "S13",
        "caption": "Table S13. Protein–protein interaction performance on held-out genomes.",
        "columns": ["Zero-shot AUROC", "Zero-shot AUPRC", "Finetuned AUROC", "Finetuned AUPRC"],
        "rows": [
            "Mistral-DNA",
            "DNABERT-2",
            "Nucleotide Transformer",
            "ProkBERT",
            "Evo",
            "Evo-2",
            "ESM-2",
            "ESM-C",
            "ProtBERT",
            "gLM2",
            "Bacformer",
            "Bacformer Large",
        ],
    },
    {
        "key": "S14",
        "caption": "Table S14. Performance on gene–essentiality prediction.",
        "columns": ["AUROC", "AUPRC"],
        "rows": BENCH_12_A,
    },
    {
        "key": "S16",
        "caption": "Table S16. Overall phenotypic traits prediction performance across all phenotypes.",
        "columns": ["AUROC", "AUPRC"],
        "rows": BENCH_12_B,
    },
    {
        "key": "S18",
        "caption": "Table S18. Performance (percent, higher is better) on antibiotic-resistance prediction tasks",
        "columns": ["Binary AUROC", "Binary AUPRC", "Regression R2", "Regression Pearson"],
        "rows": BENCH_12_B,
    },
]

CELL = r"\d+\.\d+\s*±\s*\d+\.\d+"
ROW = re.compile(rf"^\s*(?P<label>[A-Za-z][A-Za-z0-9 .\-]*?)\s\s+(?P<cells>{CELL}(?:\s\s+{CELL})*)\s*$")
CAPTION_LINE = re.compile(r"^\s*Table S\d+\.")
SUPP_HEADING = re.compile(r"^\s*SUPPLEMENTARY TABLES\s*$")


def load_text(path: Path) -> list[str]:
    raw = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != TEXT_SHA256:
        raise SystemExit(f"text layer SHA-256 {digest} does not match the pinned {TEXT_SHA256}")
    return raw.decode("utf-8").splitlines()


def caption_index(lines: list[str], caption: str) -> int:
    hits = [i for i, line in enumerate(lines) if caption in " ".join(line.split())]
    if len(hits) != 1:
        raise SystemExit(f"expected one caption line for {caption!r}, found {len(hits)}")
    return hits[0]


def block_start(lines: list[str], caption_at: int) -> int:
    """First line of the table body: just after the previous caption or the section heading."""
    for i in range(caption_at - 1, -1, -1):
        if CAPTION_LINE.match(lines[i]) or SUPP_HEADING.match(lines[i]):
            return i + 1
    return 0


def parse_table(lines: list[str], spec: dict) -> dict:
    caption_at = caption_index(lines, spec["caption"])
    start = block_start(lines, caption_at)
    want = len(spec["columns"])
    found: list[tuple[str, list[str]]] = []
    for line in lines[start:caption_at]:
        match = ROW.match(line)
        if not match:
            continue
        label = " ".join(match.group("label").split())
        cells = [" ".join(cell.split()) for cell in re.split(r"\s\s+", match.group("cells").strip())]
        if len(cells) != want:
            continue
        found.append((label, cells))
    labels = [label for label, _ in found]
    if labels != spec["rows"]:
        raise SystemExit(
            f"{spec['key']}: row labels do not match the expected printed order\n"
            f"  parsed:   {labels}\n  expected: {spec['rows']}"
        )
    rows = []
    for label, cells in found:
        parsed_cells = []
        for column, printed in zip(spec["columns"], cells):
            mean, sd = [part.strip() for part in printed.split("±")]
            parsed_cells.append(
                {
                    "column": column,
                    "printed_value": printed,
                    "mean": mean,
                    "standard_deviation": sd,
                }
            )
        rows.append({"label": label, "cells": parsed_cells})
    return {"key": spec["key"], "caption_line": " ".join(lines[caption_at].split()), "columns": spec["columns"], "rows": rows}


def main() -> None:
    text_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TEXT
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    lines = load_text(text_path)
    tables = {spec["key"]: parse_table(lines, spec) for spec in TABLES}
    cells = sum(len(row["cells"]) for table in tables.values() for row in table["rows"])
    expected = sum(len(spec["rows"]) * len(spec["columns"]) for spec in TABLES)
    if cells != expected:
        raise SystemExit(f"parsed {cells} cells, expected {expected}")
    out_path.write_text(json.dumps({"text_layer_sha256": TEXT_SHA256, "cells": cells, "tables": tables}, indent=1) + "\n")
    print(f"parsed {cells} cells from {len(tables)} tables into {out_path}")


if __name__ == "__main__":
    main()
