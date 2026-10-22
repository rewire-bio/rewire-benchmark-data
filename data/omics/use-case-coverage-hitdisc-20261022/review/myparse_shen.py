"""Independent re-parse of Shen et al. 2025 (PMC12704515) tables from the pinned JATS XML.

Written for the review pass. Does not import or reuse the extractor's build_batch.py.
Emits JSON: {table_label: {"caption":..., "cols":[...], "rows":[[rowlabel, [cells...]], ...],
"footnotes": {...}}}
"""
import json
import re
import sys
import xml.etree.ElementTree as ET


def text_of(el):
    """All text under el, tags stripped, whitespace collapsed."""
    parts = []
    for t in el.itertext():
        parts.append(t)
    s = "".join(parts)
    s = s.replace(" ", " ").replace(" ", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def sub_sup_text(el, keep_xref=False):
    """Like text_of but marks <sub>/<sup> so EF_{0.5%} headers stay distinguishable.

    keep_xref keeps footnote-marker text, so a row label reads 'Boltz-2 (Affinity)a' as printed.
    """
    out = []

    def walk(node):
        if node.text:
            out.append(node.text)
        for ch in node:
            tag = ch.tag
            if tag == "sub":
                out.append("_{" + sub_sup_text(ch, keep_xref) + "}")
            elif tag == "sup":
                out.append("^{" + sub_sup_text(ch, keep_xref) + "}")
            elif tag == "xref":
                if keep_xref:
                    out.append(text_of(ch))
            else:
                walk(ch)
            if ch.tail:
                out.append(ch.tail)

    walk(el)
    s = "".join(out).replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def parse(path):
    raw = open(path, "rb").read()
    root = ET.fromstring(raw)
    tables = {}
    for tw in root.iter("table-wrap"):
        label_el = tw.find("label")
        label = text_of(label_el) if label_el is not None else tw.get("id")
        cap = tw.find("caption")
        caption = text_of(cap) if cap is not None else None
        tbl = tw.find(".//table")
        if tbl is None:
            tables[label] = {"caption": caption, "cols": [], "rows": [], "footnotes": {}}
            continue

        # header: expand colspan/rowspan into a flat list of leaf column names
        thead = tbl.find("thead")
        header_rows = []
        if thead is not None:
            for tr in thead.findall("tr"):
                header_rows.append(tr.findall("th") + tr.findall("td"))
        # build a grid
        grid = {}
        maxcol = 0
        occupied = set()
        for ri, cells in enumerate(header_rows):
            ci = 0
            for c in cells:
                while (ri, ci) in occupied:
                    ci += 1
                cs = int(c.get("colspan", "1"))
                rs = int(c.get("rowspan", "1"))
                txt = sub_sup_text(c)
                for dr in range(rs):
                    for dc in range(cs):
                        occupied.add((ri + dr, ci + dc))
                        grid[(ri + dr, ci + dc)] = txt
                ci += cs
                maxcol = max(maxcol, ci)
        nhr = len(header_rows)
        cols = []
        for ci in range(maxcol):
            stack = []
            for ri in range(nhr):
                t = grid.get((ri, ci), "")
                if t and (not stack or stack[-1] != t):
                    stack.append(t)
            cols.append(" ".join(stack).strip())

        rows = []
        tbody = tbl.find("tbody")
        body_trs = tbody.findall("tr") if tbody is not None else []
        for tr in body_trs:
            cells = tr.findall("td") + tr.findall("th")
            if not cells:
                continue
            vals = [sub_sup_text(c) for c in cells]
            rows.append([sub_sup_text(cells[0], keep_xref=True), vals[1:]])

        fns = {}
        for fn in tw.iter("fn"):
            fid = fn.get("id") or ""
            lab = fn.find("label")
            key = text_of(lab) if lab is not None else fid
            body = text_of(fn)
            fns[key or fid] = body
        tables[label] = {
            "caption": caption,
            "cols": cols,
            "rows": rows,
            "footnotes": fns,
        }
    return tables


if __name__ == "__main__":
    t = parse(sys.argv[1])
    json.dump(t, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
    for lab, d in t.items():
        print(lab, "| cols:", len(d["cols"]), "| rows:", len(d["rows"]))
