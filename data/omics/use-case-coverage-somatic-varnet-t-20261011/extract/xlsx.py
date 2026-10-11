"""Minimal stdlib reader for .xlsx sheets: returns rows as lists of cell strings."""
import re, zipfile, html
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
import xml.etree.ElementTree as ET

def sheets(path):
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rmap = {r.get('Id'): r.get('Target') for r in rels}
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS + 'si'):
            ss.append(''.join(t.text or '' for t in si.iter(NS + 't')))
    out = {}
    for s in wb.iter(NS + 'sheet'):
        rid = s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        target = rmap[rid].lstrip('/')
        target = target if target.startswith('xl/') else 'xl/' + target
        out[s.get('name')] = (z, target, ss)
    return out

def col_index(ref):
    letters = re.match(r'[A-Z]+', ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1

def rows(sheet):
    z, target, ss = sheet
    root = ET.fromstring(z.read(target))
    out = []
    for row in root.iter(NS + 'row'):
        cells = {}
        for c in row.iter(NS + 'c'):
            v = c.find(NS + 'v'); t = c.get('t')
            if t == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter(NS + 't'))
            elif v is None:
                val = ''
            elif t == 's':
                val = ss[int(v.text)]
            else:
                val = v.text
            cells[col_index(c.get('r'))] = val
        if cells:
            out.append([cells.get(i, '') for i in range(max(cells) + 1)])
        else:
            out.append([])
    return out
