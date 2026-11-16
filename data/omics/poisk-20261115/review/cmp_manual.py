import json, re, sys

man = {}
for l in open(sys.argv[1], encoding='utf-8'):
    if l.startswith('#') or l.startswith('table\t'):
        continue
    t, row, col, val = l.rstrip('\n').split('\t')
    man[(int(t), row, col)] = val
print('hand-transcribed cells:', len(man))

PLAIN = re.compile(r'^Table (\d), row "(.+?)", column "(.+?)"(?:, sub-column "(.+?)")?$')
CURLY = re.compile('^Table (\\d), row “(.+?)”, column “(.+?)”(?:, sub-column “(.+?)”)?$')

rec = {}
seen_style = set()
for l in open(sys.argv[2], encoding='utf-8'):
    r = json.loads(l)
    if r.get('kind') != 'result':
        continue
    loc = r['attributes']['source_locator']
    m = PLAIN.match(loc)
    if m:
        seen_style.add('plain')
    else:
        m = CURLY.match(loc)
        if m:
            seen_style.add('curly')
    if not m:
        continue
    t, row, col, sub = int(m.group(1)), m.group(2), m.group(3), m.group(4)
    if t in (2, 7):
        rec[(t, row, sub or col)] = (
            str(r['attributes']['printed_value']),
            str(r['attributes'].get('numeric_value')),
            r['id'],
        )
print('locator quote styles seen:', sorted(seen_style))
print('records in Tables 2 and 7:', len(rec))
print('hand cells with no record:', [k for k in man if k not in rec])
print('records with no hand cell:', [k for k in rec if k not in man])
print('printed_value mismatches:',
      [(k, man[k], rec[k]) for k in man if k in rec and man[k] != rec[k][0]])
nbad = []
for k, (p, n, i) in rec.items():
    pv = p.rstrip('%')
    exp = float(pv) / 100 if p.endswith('%') else float(pv)
    if abs(float(n) - exp) > 1e-12:
        nbad.append((i, p, n, 'expected ' + repr(exp)))
print('numeric_value disagreements:', nbad)
