import collections, glob, json, sys

batch = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8')]
mine = {r['id'] for r in batch if r['kind'] == 'result'}

print('=== this batch: metric x unit x printed form ===')
rows = collections.defaultdict(list)
for r in batch:
    if r['kind'] != 'result':
        continue
    a = r['attributes']
    p = str(a['printed_value'])
    form = 'with %' if p.endswith('%') else ('0-1' if abs(float(p.rstrip('%'))) <= 1 else '>1')
    rows[(a['metric'], a['unit'], form)].append(r['id'])
for (m, u, f), ids in sorted(rows.items()):
    print(f'  {m:20} {u:10} printed {f:8} n={len(ids):3}  e.g. {ids[0].replace("poisk-20261115-result-","")}')
print('  unit_detail present on:',
      [r['id'] for r in batch if r['kind'] == 'result' and r['attributes'].get('unit_detail')] or 'none')

print()
print('=== store-wide convention for the metrics this batch uses ===')
metrics = sorted({r['attributes']['metric'] for r in batch if r['kind'] == 'result'})
store = collections.defaultdict(collections.Counter)
for fn in glob.glob('data/evidence/results/*.jsonl'):
    for l in open(fn, encoding='utf-8'):
        r = json.loads(l)
        if r['id'] in mine:
            continue
        a = r.get('attributes', {})
        if a.get('metric') in metrics:
            store[a['metric']][a.get('unit')] += 1
for m in metrics:
    print(f'  {m:20} {dict(store[m]) if store[m] else "not used elsewhere in the store"}')

print()
print('=== store-wide: how AUROC and other normalised scores are stored (the cited 4403 to 9) ===')
for m in ('auroc', 'auprc', 'spearman', 'matthews-correlation-coefficient', 'cohens-d'):
    c = collections.Counter()
    for fn in glob.glob('data/evidence/results/*.jsonl'):
        for l in open(fn, encoding='utf-8'):
            r = json.loads(l)
            if r['id'] in mine:
                continue
            a = r.get('attributes', {})
            if a.get('metric') == m:
                c[a.get('unit')] += 1
    print(f'  {m:34} {dict(c) or "absent"}')
