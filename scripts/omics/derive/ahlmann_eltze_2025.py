"""Per-model means from the Source Data of Ahlmann-Eltze, Huber and Anders 2025 (Nature Methods,
doi:10.1038/s41592-025-02772-6), for Fig. 1a, Fig. 2a, Extended Data Fig. 2a and Extended Data
Fig. 8a.

The legends say "The horizontal red lines show the mean per model". Each Source Data row is one
held-out perturbation in one test-training split; the sheet labels held-out rows "test" or "val",
and the Fig. 1 legend's 62 doubles per split equals the two together, so both are pooled. The
mean is the arithmetic mean of the stored cell values over those rows, per model (and per dataset
for Fig. 2), computed exactly and rounded half to even to 3 decimal places. Rows with no value
(the "no change" Pearson delta, which the Extended Data Fig. 2 legend says could not be
calculated) are counted and left out.

The script reads the workbooks with the standard library only, checks each file's SHA-256 and
every row count it relies on, and checks that the Extended Data sheets repeat the main-figure
rows. It writes one JSON object per value, sorted.

Usage: python3 -I scripts/omics/derive/ahlmann_eltze_2025.py <folder with MOESM3.xlsx, MOESM4.xlsx,
MOESM6.xlsx and MOESM10.xlsx> [output.json]
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree

SHA256 = {
    "MOESM3": "c9bd4d688b8ca8a3d3846593da3bab80cc2e65dbdbdc251a96b2bdcd05b75081",
    "MOESM4": "2ccfa7239c195f329e1632b51510adebfd493e0a5a7427a0f012e078e0e59c35",
    "MOESM6": "1f05ffc452445de659d9b0bb4b05c673892ce7a4f2657ea3098a7904f95f24b3",
    "MOESM10": "040dae4985b4461817b96eb807390c8fe3f2c115523f4dfcb7692485aa0734e3",
}
MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PLACES = 3

NORMAN_METHODS = ["additive_model", "cpa", "gears", "geneformer", "no_change", "scbert", "scfoundation", "scgpt", "uce"]
SINGLE_METHODS = ["gears", "geneformer", "lpm_selftrained", "mean", "scbert", "scgpt", "uce"]
SINGLE_ROWS = {"adamson": 48, "replogle_k562_essential": 262, "replogle_rpe1_essential": 413}

# (target, workbook, sheet, column, rows per method and dataset, methods without a value)
TARGETS = [
    ("fig1a", "MOESM3", "Panel A", "l2", {"norman_from_scfoundation": 310}, NORMAN_METHODS, set()),
    ("ed2a", "MOESM6", "Panel A", "r2_delta", {"norman_from_scfoundation": 310}, NORMAN_METHODS, {"no_change"}),
    ("fig2a", "MOESM4", "Panel A", "l2", SINGLE_ROWS, SINGLE_METHODS, set()),
    ("ed8a", "MOESM10", "Panel A", "r2_delta", SINGLE_ROWS, SINGLE_METHODS, set()),
]


def sheet_rows(path: Path, sheet: str) -> list[dict[str, str | None]]:
    """Rows of one worksheet as {header: cell text}; a cell with no value is None."""
    with zipfile.ZipFile(path) as z:
        workbook = ElementTree.fromstring(z.read("xl/workbook.xml"))
        rel_id = next(s.get(f"{REL}id") for s in workbook.iter(f"{MAIN}sheet") if s.get("name") == sheet)
        rels = ElementTree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target = next(r.get("Target") for r in rels if r.get("Id") == rel_id)
        root = ElementTree.fromstring(z.read(f"xl/{target}"))
        assert not any(n == "xl/sharedStrings.xml" for n in z.namelist()), "expected inline strings only"
    table = []
    for row in root.iter(f"{MAIN}row"):
        cells = {}
        for c in row:
            column = re.match(r"[A-Z]+", c.get("r")).group()
            if c.get("t") == "inlineStr":
                cells[column] = "".join(t.text or "" for t in c.iter(f"{MAIN}t"))
            else:
                v = c.find(f"{MAIN}v")
                cells[column] = None if v is None else v.text
        table.append(cells)
    header = table[0]
    return [{header[col]: row.get(col) for col in header} for row in table[1:]]


def round_half_even(value: Fraction, places: int) -> str:
    scaled = value * 10**places
    floor = scaled.numerator // scaled.denominator
    remainder = scaled - floor
    if remainder > Fraction(1, 2) or (remainder == Fraction(1, 2) and floor % 2 == 1):
        floor += 1
    sign = "-" if floor < 0 else ""
    digits = str(abs(floor)).rjust(places + 1, "0")
    return f"{sign}{digits[:-places]}.{digits[-places:]}"


def main(folder: Path) -> list[dict]:
    for name, expected in SHA256.items():
        actual = hashlib.sha256((folder / f"{name}.xlsx").read_bytes()).hexdigest()
        assert actual == expected, f"{name}.xlsx has sha256 {actual}, expected {expected}"
    sheets = {(w, s): sheet_rows(folder / f"{w}.xlsx", s) for w in SHA256 for s in ["Panel A"]}
    # The Extended Data Panel A sheets repeat the main-figure rows exactly.
    assert sheets[("MOESM6", "Panel A")] == sheets[("MOESM3", "Panel A")], "MOESM6 Panel A differs from MOESM3 Panel A"
    assert sheets[("MOESM10", "Panel A")] == sheets[("MOESM4", "Panel A")], "MOESM10 Panel A differs from MOESM4 Panel A"
    out = []
    for target, workbook, sheet, column, per_dataset, methods, valueless in TARGETS:
        rows = sheets[(workbook, sheet)]
        assert len(rows) == len(methods) * sum(per_dataset.values()), f"{target}: {len(rows)} rows"
        assert {r["train"] for r in rows} == {"test", "val"}, f"{target}: unexpected train labels"
        counts = Counter((r["dataset_name"], r["method"]) for r in rows)
        assert counts == Counter({(d, m): n for d, n in per_dataset.items() for m in methods}), f"{target}: row counts differ"
        for dataset in per_dataset:
            for method in methods:
                group = [r for r in rows if r["dataset_name"] == dataset and r["method"] == method]
                values = [Fraction(Decimal(r[column])) for r in group if r[column] is not None]
                missing = len(group) - len(values)
                if method in valueless:
                    assert not values, f"{target} {dataset} {method}: expected no values"
                else:
                    assert not missing, f"{target} {dataset} {method}: {missing} rows without a value"
                mean = sum(values, Fraction(0)) / len(values) if values else None
                out.append({
                    "target": target, "workbook": workbook, "sheet": sheet, "dataset": dataset, "method": method,
                    "column": column, "row_count": len(group), "rows_with_value": len(values),
                    "splits": sorted({r["seed"] for r in group}),
                    "value": None if mean is None else round_half_even(mean, PLACES),
                })
    return sorted(out, key=lambda r: (r["target"], r["dataset"], r["method"]))


if __name__ == "__main__":
    results = main(Path(sys.argv[1]))
    text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in results)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(text)
    else:
        sys.stdout.write(text)
