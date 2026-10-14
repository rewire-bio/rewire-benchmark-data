"""Minimal stdlib OOXML reader: sheet name -> {cell ref: (raw value text, formula text or None, style index)}."""
import zipfile, xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def read_sheets(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for s in wb.find("m:sheets", NS):
        target = rels[s.get("{%s}id" % NS["r"])]
        root = ET.fromstring(z.read("xl/" + target.lstrip("/").replace("xl/", "")))
        cells = {}
        for c in root.iter("{%s}c" % NS["m"]):
            v, f = c.find("m:v", NS), c.find("m:f", NS)
            if v is None:
                continue
            text = shared[int(v.text)] if c.get("t") == "s" else v.text
            formula = None if f is None else (f.text or f"shared formula (si={f.get('si')})")
            cells[c.get("r")] = (text, formula, c.get("s"))
        out[s.get("name")] = cells
    return out
