"""Independent reviewer parse of Qin 2025 Tables 1-8 and comparison with the part file.
Maps each result to its cell through the evaluation's system and data links and the
metric qualifier, not through its source_locator, so column assignment is checked."""
import json, re, sys
txt, part = sys.argv[1], sys.argv[2]
L = open(txt).read().split("\n")
CELL = r"(\d+\.\d) \((\d+\.\d)\)"
COLS = ["Norman", "Simpson", "Horlbeck K562", "Horlbeck Jurkat"]
cells = {}
def grab(lineno, label_re, n, key):
    s = L[lineno - 1]
    m = re.match(r"\s*" + label_re + r"\s", s)
    assert m, (lineno, label_re, s)
    vals = re.findall(CELL, s[m.end():])
    assert len(vals) == n, (lineno, s, vals)
    return [f"{a} ({b})" for a, b in vals]
def find(after, pattern):
    for i in range(after, len(L)):
        if re.search(pattern, L[i]):
            return i + 1
    raise KeyError(pattern)
# Table 1
t1 = find(0, r"^Table 1\. Root mean square")
for off, (freq, model) in enumerate([(4, m) for m in ["Linear", "MLP", "GEARS", "RECOVER", "NAIAD"]] + [(20, m) for m in ["Linear", "MLP", "GEARS", "RECOVER", "NAIAD"]]):
    ln = t1 + 4 + off
    lab = (r"(?:\d+\s+)?" + model)
    v = grab(ln, lab, 4, None)
    if model == "GEARS":
        assert re.match(r"\s*%d\s+GEARS" % freq, L[ln - 1]), L[ln - 1]
    for c, x in zip(COLS, v): cells[("T1", freq, model, c)] = x
t6 = find(0, r"^Table 6\. RMSE")
for off, model in enumerate(["Linear", "MLP", "GEARS", "RECOVER", "NAIAD"]):
    ln = t6 + 4 + off
    v = grab(ln, r"(?:10\s+)?" + model, 4, None)
    if model == "Linear": assert re.match(r"\s*10\s+Linear", L[ln - 1])
    for c, x in zip(COLS, v): cells[("T1", 10, model, c)] = x
# Table 2 and 3: integers / decimals, left column only (right column is prose)
t2 = find(0, r"^Table 2\. Number of top 200")
for row in ["Uniform", "MPE", "UCB", "Uncertainty"]:
    ln = find(t2, r"^ %s\s+\d" % row)
    v = re.findall(r"\d+(?:\.\d+)?", L[ln - 1][:60])
    assert len(v) == 4, (L[ln - 1], v)
    for c, x in zip(COLS, v): cells[("T2", row, c)] = x
t3 = find(0, r"^Table 3\. Marginal gain")
for row in ["Uniform", "MPE", "UCB", "Uncertainty"]:
    ln = find(t3, r"^ %s\s+\d" % row)
    v = re.findall(r"\d+(?:\.\d+)?", L[ln - 1][:60])
    assert len(v) == 4, (L[ln - 1], v)
    for c, x in zip(COLS, v): cells[("T3", row, c)] = x
t4 = find(0, r"^Table 4\. Number of top 200")
for off, (mod, acq) in enumerate([("NAIAD", "Uniform"), ("RECOVER", "Uniform"), ("NAIAD", "MPE"), ("RECOVER", "MPE"), ("NAIAD", "UCB"), ("RECOVER", "UCB")]):
    v = grab(t4 + 3 + off, mod + r"\s+" + acq, 4, None)
    for c, x in zip(COLS, v): cells[("T4", mod, acq, c)] = x
t5 = find(0, r"^Table 5\. Number of top 200")
for off, ens in enumerate([1, 3, 5, 7]):
    v = grab(t5 + 4 + off, str(ens), 8, None)
    for i, c in enumerate(COLS):
        cells[("T5", ens, "MPE", c)] = v[2 * i]
        cells[("T5", ens, "Uniform", c)] = v[2 * i + 1]
t7 = find(0, r"^Table 7\. Number of top 200")
for off, (mod, acq) in enumerate([("NAIAD", "MPE"), ("RECOVER", "MPE"), ("GEARS", "MPE"), ("NAIAD", "Uniform")]):
    v = grab(t7 + 3 + off, mod + r"\s+" + acq, 5, None)
    for r, x in enumerate(v): cells[("T7", mod, acq, r)] = x
t8 = find(0, r"^Table 8\. Number of top 200")
for off, b in enumerate(["0", "0.25", "0.5", "0.75", "1", "1.5", "2", "5", "10", "25", "Uniform"]):
    v = grab(t8 + 6 + off, re.escape(b), 4, None)
    for c, x in zip(COLS, v): cells[("T8", b, c)] = x
print("cells parsed", len(cells), file=sys.stderr)

recs = [json.loads(l) for l in open(part)]
by = {r["id"]: r for r in recs}
DS = {"norman2019": "Norman", "simpson2023": "Simpson", "horlbeck2018-k562": "Horlbeck K562", "horlbeck2018-jurkat": "Horlbeck Jurkat"}
NAME = {"naiad": "NAIAD", "recover": "RECOVER", "gears": "GEARS", "linear-pair": "Linear", "mlp-gene-embedding": "MLP"}
ACQ = {"uniform": "Uniform", "mpe": "MPE", "ucb": "UCB", "uncertainty": "Uncertainty"}
out = []; bad = 0; used = set()
for r in recs:
    if r["kind"] != "result": continue
    a = r["attributes"]
    ev = by[[l["target_id"] for l in r["links"] if l["relation"] == "evaluation"][0]]
    el = {l["relation"]: l["target_id"] for l in ev["links"]}
    cfg = el["system"].replace("pheno-20261022-qin2025-config-", "")
    col = DS[el["data"].replace("pheno-20261022-qin2025-data-", "").replace("-viability", "")]
    g = ev["attributes"]["evaluation_group_id"]; q = a["metric_qualifier"]
    if g == "qin2025-table1-6":
        freq = int(re.search(r"about (\d+) times", q).group(1))
        key = ("T1", freq, NAME[cfg.replace("-prediction", "")], col)
    elif g == "qin2025-table2-3":
        key = ("T2" if a["metric"] == "true-positive-count" else "T3", ACQ[cfg.replace("naiad-", "")], col)
    elif g == "qin2025-table4":
        m, acq = cfg.split("-", 1); key = ("T4", NAME[m], ACQ[acq], col)
    elif g == "qin2025-table5":
        m = re.match(r"naiad-(mpe|uniform)-ensemble-(\d+)", cfg); key = ("T5", int(m.group(2)), ACQ[m.group(1)], col)
    elif g == "qin2025-table7":
        assert col == "Norman"
        m, acq = cfg.split("-", 1); rnd = int(re.search(r"round (\d)", q).group(1)); key = ("T7", NAME[m], ACQ[acq], rnd)
    elif g == "qin2025-table8":
        b = "Uniform" if cfg == "naiad-uniform" else cfg.replace("naiad-mean-ucb-beta-", "").replace("-", ".")
        key = ("T8", b, col)
    exp = cells.get(key); used.add(key)
    pv = a["printed_value"]; nv = a.get("numeric_value")
    unc = a.get("uncertainty") or {}
    ok = exp == pv
    enum = exp.split(" ")[0] if exp else None
    ok_n = nv is not None and enum is not None and float(nv) == float(enum)
    ok_u = True
    if "(" in (exp or ""):
        ok_u = unc.get("value") == exp.split("(")[1].rstrip(")") and unc.get("type") == "standard_error" and unc.get("n") == 3
    else:
        ok_u = not unc and "uncertainty" in (a.get("missing_metadata") or {})
    # round qualifier check for non-T7 al tables
    if g in ("qin2025-table2-3", "qin2025-table4", "qin2025-table5", "qin2025-table8") and a["metric"] == "true-positive-count":
        ok_q = "round 4" in q
    else:
        ok_q = True
    status = "match" if (ok and ok_n and ok_u and ok_q) else "MISMATCH"
    if status != "match": bad += 1
    out.append("\t".join([r["id"], status, str(key), pv, str(exp), str(nv), str(unc.get("value")), a["source_locator"]]))
print("id\tstatus\tcell\tprinted_value\texpected\tnumeric_value\tse\tsource_locator")
print("\n".join(out))
print("results", len(out), "mismatch", bad, "cells unused", sorted(set(cells) - used, key=str), file=sys.stderr)
