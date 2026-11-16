import json, sys, collections, itertools

recs = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8')]
by_id = {r['id']: r for r in recs}
results = [r for r in recs if r['kind'] == 'result']
protos = {r['id']: r for r in recs if r['kind'] == 'protocol'}
evals = {r['id']: r for r in recs if r['kind'] == 'evaluation'}

problems = []
rows = []
for r in sorted(results, key=lambda x: x['id']):
    a = r['attributes']
    ev_ids = [l['target_id'] for l in r['links'] if l['relation'] == 'evaluation']
    if len(ev_ids) != 1:
        problems.append((r['id'], 'evaluation links', ev_ids))
        continue
    ev = evals.get(ev_ids[0])
    if ev is None:
        problems.append((r['id'], 'evaluation not in batch', ev_ids))
        continue
    pr_ids = [l['target_id'] for l in ev['links'] if l['relation'] == 'assessment']
    pr = protos.get(pr_ids[0]) if pr_ids else None
    pa = pr['attributes'] if pr else {}
    rows.append(dict(
        id=r['id'],
        metric=a.get('metric'),
        p_metric=pa.get('metric'),
        direction=a.get('metric_direction'),
        p_direction=pa.get('metric_direction'),
        unit=a.get('unit'),
        p_unit=pa.get('unit'),
        denom=a.get('denominator'),
        p_denom=pa.get('denominator'),
        printed=str(a.get('printed_value')),
        numeric=str(a.get('numeric_value')),
        status=r.get('status'),
        unc=bool(a.get('uncertainty')),
        mm=sorted((a.get('missing_metadata') or {}).keys()),
        protocol=pr['id'] if pr else None,
    ))

print('results:', len(rows), 'link problems:', problems)

for k in ('metric', 'direction', 'unit', 'denom'):
    bad = [(x['id'], x[k], x['p_' + k]) for x in rows if x[k] != x['p_' + k]]
    print(f'\n{k} differs from protocol: {len(bad)}')
    for b in bad:
        print('  ', b)

# printed vs numeric consistency, unit aware
print('\nprinted/numeric consistency by unit:')
bad = []
for x in rows:
    p, n, u = x['printed'], x['numeric'], x['unit']
    pv = p.rstrip('%')
    try:
        pf, nf = float(pv), float(n)
    except ValueError:
        bad.append((x['id'], p, n, u, 'unparseable'))
        continue
    if u == 'percent':
        ok = abs(nf - pf) < 1e-9
    elif u in ('fraction', 'unitless'):
        ok = abs(nf - pf) < 1e-9
    else:
        ok = abs(nf - pf) < 1e-9
    if p.endswith('%') and u != 'percent':
        bad.append((x['id'], p, n, u, 'printed with % but unit is not percent'))
    elif not ok:
        bad.append((x['id'], p, n, u, 'numeric != printed'))
print(' problems:', bad if bad else 'none')

print('\nunit by protocol:')
for pid, g in sorted(itertools.groupby(sorted(rows, key=lambda x: (x['protocol'] or '')), key=lambda x: x['protocol']),
                     key=lambda t: t[0] or ''):
    g = list(g)
    print('  ', pid, collections.Counter(x['unit'] for x in g), 'n=' + str(len(g)),
          'metric=' + str(g[0]['metric']), 'denom=' + str(sorted({x['denom'] for x in g})))

print('\nstatus:', collections.Counter(x['status'] for x in rows))
print('with uncertainty:', sum(1 for x in rows if x['unc']))
print('missing_metadata keys:', collections.Counter(k for x in rows for k in x['mm']))
