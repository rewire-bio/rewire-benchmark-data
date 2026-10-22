"""Independent re-parse of a sheet of ci5c02441_si_002.xlsx (CACHE #3 Supporting Information).

Reads the OOXML parts directly: no openpyxl, and no reuse of the extractor's build_batch.py.
Prints the sheet as a JSON grid of {cell_ref: {"t": type, "raw": stored string, "round": shortest
round-tripping decimal}}.
"""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RELNS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
ODOC = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def shared_strings(z):
    try:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    out = []
    for si in root.findall(NS + "si"):
        out.append("".join(t.text or "" for t in si.iter(NS + "t")))
    return out


def sheet_path(z, name):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.get("Id"): r.get("Target") for r in rels}
    for sh in wb.iter(NS + "sheet"):
        if sh.get("name") == name:
            tgt = relmap[sh.get(ODOC + "id")]
            return "xl/" + tgt.lstrip("/").replace("xl/", "", 1) if not tgt.startswith("xl/") else tgt
    raise KeyError(name)


def sheet_names(z):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    return [sh.get("name") for sh in wb.iter(NS + "sheet")]


def roundtrip(raw):
    """Shortest decimal that round-trips to the stored double."""
    try:
        d = float(raw)
    except ValueError:
        return raw
    if d == int(d) and abs(d) < 1e15:
        return str(int(d))
    return repr(d)


def read_sheet(path, name):
    z = zipfile.ZipFile(path)
    ss = shared_strings(z)
    sp = sheet_path(z, name)
    root = ET.fromstring(z.read(sp))
    grid = {}
    for row in root.iter(NS + "row"):
        for c in row.findall(NS + "c"):
            ref = c.get("r")
            t = c.get("t")
            v = c.find(NS + "v")
            isel = c.find(NS + "is")
            if t == "s" and v is not None:
                val = ss[int(v.text)]
                grid[ref] = {"t": "str", "raw": val, "round": val}
            elif t == "inlineStr" and isel is not None:
                val = "".join(x.text or "" for x in isel.iter(NS + "t"))
                grid[ref] = {"t": "str", "raw": val, "round": val}
            elif v is not None:
                raw = v.text
                grid[ref] = {"t": t or "n", "raw": raw, "round": roundtrip(raw)}
            else:
                pass  # genuinely empty cell: not recorded
    return grid


if __name__ == "__main__":
    z = zipfile.ZipFile(sys.argv[1])
    print("sheets:", sheet_names(z), file=sys.stderr)
    g = read_sheet(sys.argv[1], sys.argv[2])
    json.dump(g, open(sys.argv[3], "w"), indent=0, ensure_ascii=False)
    # print as a grid
    rows = {}
    for ref, d in g.items():
        m = re.match(r"([A-Z]+)(\d+)", ref)
        rows.setdefault(int(m.group(2)), {})[m.group(1)] = d
    for rn in sorted(rows):
        cells = rows[rn]
        print(rn, {k: cells[k]["round"] for k in sorted(cells, key=lambda s: (len(s), s))})
