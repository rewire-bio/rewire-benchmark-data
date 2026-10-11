"""Grid parser for JATS table-wrap elements: expands rowspan and colspan."""
import re, xml.etree.ElementTree as ET


def _text(el):
    s = ''.join(el.itertext())
    s = s.replace(' ', ' ').replace('\xa0', ' ')
    return ' '.join(s.split())


def tables(xml_bytes):
    """Yield (label, caption, rows) for each table-wrap; rows is a list of lists of cell strings."""
    root = ET.fromstring(xml_bytes)
    out = []
    for tw in root.iter('table-wrap'):
        lab = tw.find('label')
        cap = tw.find('caption')
        grid = []
        for tbl in tw.iter('table'):
            occupied = {}
            r = 0
            for tr in tbl.iter('tr'):
                row = []
                c = 0
                while occupied.get((r, c)) is not None:
                    row.append(occupied[(r, c)]); c += 1
                for cell in tr:
                    if cell.tag not in ('td', 'th'):
                        continue
                    v = _text(cell)
                    rs = int(cell.get('rowspan', 1) or 1)
                    cs = int(cell.get('colspan', 1) or 1)
                    for dr in range(rs):
                        for dc in range(cs):
                            if dr == 0 and dc == 0:
                                continue
                            occupied[(r + dr, c + dc)] = v
                    for _ in range(cs):
                        row.append(v); c += 1
                    while occupied.get((r, c)) is not None:
                        row.append(occupied[(r, c)]); c += 1
                grid.append(row)
                r += 1
        out.append((_text(lab) if lab is not None else '', _text(cap) if cap is not None else '', grid))
    return out
