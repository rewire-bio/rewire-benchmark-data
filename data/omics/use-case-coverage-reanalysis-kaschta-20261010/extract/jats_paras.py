"""List body paragraphs of a JATS file with a stable locator: top-level section title, subsection title and paragraph number within the subsection (direct <p> children only)."""
import sys, xml.etree.ElementTree as ET
def txt(e): return ' '.join(''.join(e.itertext()).split())
def strip(tag): return tag.split('}')[-1]
def paras(root):
    out = []
    def walk(sec, path):
        n = 0
        for ch in sec:
            t = strip(ch.tag)
            if t == 'p':
                n += 1
                out.append((' > '.join(path), n, txt(ch)))
            elif t == 'sec':
                tt = [c for c in ch if strip(c.tag) == 'title']
                walk(ch, path + [txt(tt[0]) if tt else '?'])
    body = [e for e in root.iter() if strip(e.tag) == 'body'][0]
    walk(body, [])
    abs_ = [e for e in root.iter() if strip(e.tag) == 'abstract']
    for a in abs_:
        for i, p in enumerate([e for e in a.iter() if strip(e.tag) == 'p'], 1):
            out.insert(0, ('Abstract', i, txt(p)))
    return out
if __name__ == '__main__':
    root = ET.parse(sys.argv[1]).getroot()
    for path, n, s in paras(root):
        print(f'[{path} P{n}] {s}\n')
    for e in root.iter():
        if strip(e.tag) in ('fig', 'table-wrap'):
            cap = [c for c in e.iter() if strip(c.tag) == 'caption']
            print('CAPTION', e.get('id'), txt(cap[0]) if cap else '', '\n')
