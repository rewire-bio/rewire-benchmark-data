"""Reviewer's independent check of song2025virtualcrispr.jsonl against the pdftotext -layout text layer.
Tables are re-parsed by fixed line ranges with asserted headers and row labels; each value is
taken from its own column, so column assignment is checked."""
import json, re, sys
txt, part = sys.argv[1], sys.argv[2]
L = open(txt).read().splitlines()
recs = [json.loads(l) for l in open(part)]
by = {r['id']: r for r in recs}

def right(line, start=58):
    return line[start:] if len(line) > start else ''

# Table 1: right column, lines 129..156 (1-based), header 'Model F1 Score FPR'
t1 = {}
i1 = next(i for i, l in enumerate(L) if right(l).split() == ['Model', 'F1', 'Score', 'FPR'])
seg = [right(l) for l in L[i1:i1 + 30]]
assert any(l.lstrip().startswith('Table 1: Performance on the Simple') for l in (right(x) for x in L[i1:i1 + 32]))
assert seg[0].split() == ['Model', 'F1', 'Score', 'FPR'], seg[0]
for s in seg[1:]:
    m = re.match(r'\s*(\S.*?)\s{2,}(\d\.\d\d(?: ± \d\.\d\d)?)\s{2,}(\d\.\d\d(?: ± \d\.\d\d)?)\s*$', s)
    if m:
        t1[m[1]] = {'F1 Score': m[2], 'FPR': m[3]}
assert len(t1) == 18, sorted(t1)
# Table 2: lines 205..209
i2 = next(i for i, l in enumerate(L) if l.split()[:3] == ['Model', 'AUROC', 'AUPRC'])
assert L[i2 + 6].startswith('Table 2: Performance on the Difficult')
h = L[i2].split()
assert h == ['Model', 'AUROC', 'AUPRC', 'F1', 'FPR', 'PPV', 'NPV', 'Sens.', 'Spec.'], h
t2 = {}
for i in (i2 + 1, i2 + 2, i2 + 3):
    parts = re.split(r'\s{2,}', L[i].strip())
    assert len(parts) == 9, parts
    t2[parts[0]] = dict(zip(h[1:], parts[1:]))
spread = L[i2 + 4].split()
assert len(spread) == 6 and all(s.startswith('±') for s in spread)
t2_spread = dict(zip(['F1', 'FPR', 'PPV', 'NPV', 'Sens.', 'Spec.'], spread))
# Table 8
i8 = next(i for i, l in enumerate(L) if l.split()[:4] == ['Model', 'Few-shot', 'CoT', 'F1'])
h8 = ['F1', 'FPR', 'PPV', 'NPV', 'Sensitivity', 'Specificity']
t8 = {}
for l in L[i8 + 1:i8 + 12]:
    parts = re.split(r'\s{2,}', l.strip())
    assert len(parts) == 9, parts
    t8[(parts[0], parts[1], parts[2])] = dict(zip(h8, parts[3:]))
assert len(t8) == 11 and L[i8 + 13].startswith('Table 8:')

metric_cols = {'f1-score': ('F1 Score', 'F1', 'F1'), 'false-positive-rate': ('FPR', 'FPR', 'FPR'),
               'precision': (None, 'PPV', 'PPV'), 'negative-predictive-value': (None, 'NPV', 'NPV'),
               'recall': (None, 'Sens.', 'Sensitivity'), 'specificity': (None, 'Spec.', 'Specificity'),
               'auroc': (None, 'AUROC', None), 'auprc': (None, 'AUPRC', None)}
LOC = re.compile(r'^(?P<table>Table \d+)[^"]*row "(?P<row>[^"]+)", column "(?P<col>[^"]+)"$')
out, bad = [], 0
for r in recs:
    if r['kind'] != 'result':
        continue
    a = r['attributes']
    m = LOC.match(a['source_locator'])
    assert m, a['source_locator']
    t, row, col = m['table'], m['row'], m['col']
    if t == 'Table 1':
        cell = t1[row][col]; idx = 0
    elif t == 'Table 2':
        cell = t2[row][col]; idx = 1
    else:
        key = tuple(re.split(r' (?=\d-shot|N/A|[NY]$)', row))
        key = (key[0], key[1], key[2]) if len(key) == 3 else None
        cell = t8[key][col]; idx = 2
    ok_col = metric_cols[a['metric']][idx] == col
    ok_val = cell == a['printed_value'] or (cell == 'N/A' and a['printed_value'] == 'N/A')
    num = cell.split(' ±')[0]
    ok_num = (a['numeric_value'] is None and cell == 'N/A') or a['numeric_value'] == num
    u = a.get('uncertainty')
    if ' ± ' in cell:
        ok_unc = u and u['value'] == cell.split('± ')[1] and u['type'] == 'standard_deviation'
    elif t == 'Table 2' and row.startswith('GPT-4o') and cell != 'N/A':
        ok_unc = u and '±' + u['value'] == t2_spread[col] and u['type'] == 'unresolved_spread'
    else:
        ok_unc = u is None
    st = 'ok' if all([ok_col, ok_val, ok_num, ok_unc]) else f'BAD col={ok_col} val={ok_val} num={ok_num} unc={ok_unc}'
    bad += st != 'ok'
    out.append((r['id'], st, cell, a['printed_value'], a['source_locator']))
for o in out:
    print('\t'.join(map(str, o)))
print('checked', len(out), 'bad', bad, file=sys.stderr)

# Internal consistency: FPR = 1 - specificity, F1 from PPV and sensitivity
for k, v in t8.items():
    f, fpr, ppv, sens, spec = (float(v[c]) for c in ('F1', 'FPR', 'PPV', 'Sensitivity', 'Specificity'))
    assert abs(fpr - (1 - spec)) < 0.011, k
    assert abs(2 * ppv * sens / (ppv + sens) - f) < 0.015, (k, 2 * ppv * sens / (ppv + sens), f)
for k, v in t2.items():
    assert abs(float(v['FPR']) - (1 - float(v['Spec.']))) < 0.011, k
g = [float(v['F1']) for k, v in t8.items() if k[0] == 'GPT-4o']
fp = [float(v['FPR']) for k, v in t8.items() if k[0] == 'GPT-4o']
print('Table 8 GPT-4o mean F1 %.3f FPR %.3f; Table 1 GPT-4o %s' % (sum(g) / 10, sum(fp) / 10, t1['GPT-4o']), file=sys.stderr)
import statistics
print('Table 8 GPT-4o sd F1 %.3f (sample) %.3f (pop); FPR %.3f / %.3f' % (statistics.stdev(g), statistics.pstdev(g), statistics.stdev(fp), statistics.pstdev(fp)), file=sys.stderr)
print('Random rows equal: T1', t1['Random Baseline'], 'T8', t8[('Random', 'N/A', 'N/A')], file=sys.stderr)
# Random baseline expectation: pooled 41.3% versus per-screen hit proportions (Table 3)
screens = {'1837': (423, 140), '1885': (343, 139), '1835': (243, 76), '1733': (166, 130)}
G = sum(g for g, _ in screens.values()); H = sum(h for _, h in screens.values()); N = G - H
p = H / G
print('pooled p=%.4f: sens=PPV=F1=FPR=%.3f, spec=NPV=%.3f' % (p, p, 1 - p), file=sys.stderr)
tp = sum(h / g * h for g, h in screens.values()); fpn = sum(h / g * (g - h) for g, h in screens.values())
sens = tp / H; ppv = tp / (tp + fpn); fpr = fpn / N; npv = (N - fpn) / (N - fpn + H - tp)
print('per-screen p: sens=%.3f PPV=%.3f F1=%.3f FPR=%.3f spec=%.3f NPV=%.3f' % (sens, ppv, 2 * sens * ppv / (sens + ppv), fpr, 1 - fpr, npv), file=sys.stderr)

# Identity: result -> evaluation -> configuration -> model; protocol and qualifier match the table
T7 = {}
i7 = next(i for i, l in enumerate(L) if l.split() == ['Model', 'Alias', 'Model', 'Version'])
for l in L[i7 + 1:i7 + 18]:
    a7, v7 = l.split()
    T7[a7] = v7
alias = {'GPT-3.5-turbo': 'GPT-3.5'}
nid = 0
for r in recs:
    if r['kind'] != 'result':
        continue
    a = r['attributes']
    ev = by[next(l['target_id'] for l in r['links'] if l['relation'] == 'evaluation')]
    cfg = by.get(next(l['target_id'] for l in ev['links'] if l['relation'] == 'system'))
    prot = next(l['target_id'] for l in ev['links'] if l['relation'] == 'assessment')
    m = LOC.match(a['source_locator']); t, row = m['table'], m['row']
    want_prot = 'difficult' if t == 'Table 2' else 'simple'
    probs = []
    if want_prot not in prot or want_prot.capitalize() not in a['metric_qualifier']:
        probs.append('protocol/qualifier')
    if t in ('Table 1', 'Table 2'):
        if cfg['attributes']['reported_name'] not in (row, row.replace(' (prompting)', '')):
            probs.append('config name %s' % cfg['attributes']['reported_name'])
    else:
        model, fs, cot = re.split(r' (?=\d-shot|N/A|[NY]$)', row)
        if model == 'GPT-4o' and not (f'Few-shot: {fs};' in cfg['attributes']['parameters'] and f'CoT: {cot}.' in cfg['attributes']['parameters']):
            probs.append('table 8 params')
    rn = cfg['attributes']['reported_name']
    v = T7.get(alias.get(rn, rn))
    if v and cfg['attributes'].get('model_version') != v:
        probs.append('version %s vs %s' % (cfg['attributes'].get('model_version'), v))
    if probs:
        nid += 1; print('IDENTITY', r['id'], probs, file=sys.stderr)
print('identity problems', nid, file=sys.stderr)
