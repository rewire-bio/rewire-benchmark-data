"""Classify the multi-gene test-set variants of Alavi 2026 by position.

The preprint describes its 65-gene test set as "76 functionally validated, spliceogenic
substitutions within the canonical splice sites of 65 genes". Supplemental Table VI of the
supplementary archive lists every variant with its HGVS coding coordinate, so the claim can
be checked. Reads the table from the archive member and writes composition.tsv.

Usage: python3 classify-table-vi.py Supplemental_Table_VI.xlsx > composition.tsv
Archive: https://doi.org/10.5281/zenodo.23105803
         supplementary_materials_alavi_2026_v01.zip
         sha256 1a064bbb2dc415cc9b7d1bfc42c9242ab4d9105220ef4d9e65792ef185d3cdb5
"""
import collections
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def cells(path):
    """Read the single worksheet as a list of column-letter dictionaries."""
    book = zipfile.ZipFile(path)
    strings = [
        "".join(t.text or "" for t in si.iter(NS + "t"))
        for si in ET.fromstring(book.read("xl/sharedStrings.xml")).findall(NS + "si")
    ]
    rows = []
    for row in ET.fromstring(book.read("xl/worksheets/sheet1.xml")).iter(NS + "row"):
        values = {}
        for cell in row:
            column = re.match(r"[A-Z]+", cell.get("r")).group(0)
            value = cell.find(NS + "v")
            if value is None:
                values[column] = ""
            elif cell.get("t") == "s":
                values[column] = strings[int(value.text)]
            else:
                values[column] = value.text
        rows.append(values)
    return rows[1:]


def offset(hgvs):
    """The intronic offset of a coding HGVS substitution, or None for an exonic one."""
    match = re.search(r"c\.[-*]?\d+([+-])(\d+)", hgvs)
    if not match:
        return None
    return int(match.group(2)) * (1 if match.group(1) == "+" else -1)


def position_class(hgvs):
    away = offset(hgvs)
    if away is None:
        return "exonic"
    if abs(away) <= 2:
        return "canonical +/-1,2"
    return "near-splice intronic beyond +/-2"


rows = cells(sys.argv[1])
groups = {
    "positive": [r for r in rows if r.get("F") in ("Donor", "Acceptor")],
    "benign": [r for r in rows if r.get("F") == "subst"],
}
print("group\tvariants\tgenes\tclass\tcount\toffsets")
for name, group in groups.items():
    classes = collections.Counter(position_class(r["E"]) for r in group)
    for label, count in sorted(classes.items()):
        offsets = sorted({offset(r["E"]) for r in group if position_class(r["E"]) == label} - {None})
        print(f"{name}\t{len(group)}\t{len({r['A'] for r in group})}\t{label}\t{count}\t"
              f"{','.join(str(o) for o in offsets)}")
print(f"all\t{len(rows)}\t{len({r['A'] for r in rows})}\ttotal\t{len(rows)}\t")
