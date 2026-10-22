"""Independent reviewer check (edwards2026assayloop). Usage: python3 -I <this> <layout.txt> <part.jsonl> [out.tsv].
Written by the review agent, separately from extract/edwards2026assayloop.py: re-parse Table 1 and Supplementary Table 4 from the
pdftotext -layout text layer and compare every result's printed_value with the cell
its source_locator names (row, group, preceding row, column)."""
import json, re, sys, collections

layout, part = sys.argv[1], sys.argv[2]
out = open(sys.argv[3], "w", encoding="utf-8") if len(sys.argv) > 3 else None
if out: out.write("id\tstatus\tprinted_value\tcell_value\ttable\tlayout_line\tcolumn\n")
lines = open(layout, encoding="utf-8").read().split("\n")

NUM = r"-?\d+(?:\.\d+)?"

def parse(start_pat, header_pat, groups, ncols, stop_pat):
    i = next(k for k, l in enumerate(lines) if re.search(start_pat, l))
    h = next(k for k in range(i, i + 40) if re.search(header_pat, lines[k]))
    rows, group, prev = [], None, None
    for k in range(h + 1, h + 120):
        l = lines[k].strip()
        if re.search(stop_pat, l):
            break
        if not l:
            continue
        if l in groups:
            group, prev = l, None
            continue
        m = re.match(r"^(.*?)\s+((?:%s\s+){%d}%s)$" % (NUM, ncols - 1, NUM), l)
        if not m:
            continue
        label = re.sub(r"\s+", " ", m.group(1)).strip()
        vals = m.group(2).split()
        rows.append(dict(group=group, label=label, prev=prev, vals=vals, line=k + 1))
        prev = label
    return rows

T1_GROUPS = ["Base LLMs", "AssayLLM (Ours)", "Adaptive Experimental Design Methods",
             "Agent Harnesses", "AssayFormer (Ours)", "AssayLoop (Ours)"]
t1 = parse(r"Table 1: Performance comparison", r"^Method\s+EF", T1_GROUPS, 8, r"^\d+$")
t1_cols = ["EF (↑)", "nAUC (%)(↑)", "FH (%)(↑)", "SF (%)(↓)", "%ess (%)", "EP-B", "EP-S", "EP-D"]
s4 = parse(r"Supplementary Table 4: Full", r"Method\s+EF\s+nAUC", T1_GROUPS + ["Ablations"], 10, r"^\x0c?D\s+Implementation")
s4_cols = ["EF", "nAUC (%)", "Frac. hits (%)", "Shortfall (%)", "Ess. (%)", "Vendi (%)", "Path. Ov.", "EP-B", "EP-S", "EP-D"]
print("Table 1 rows", len(t1), "S4 rows", len(s4))

def norm(s):
    return re.sub(r"\s+", "", s).lower()

rs = [json.loads(l) for l in open(part)]
res = [r for r in rs if r["kind"] == "result"]
evals = {r["id"]: r for r in rs if r["kind"] == "evaluation"}
stat = collections.Counter()
bad = []
cells_used = collections.Counter()
by_eval = collections.defaultdict(list)
for r in res:
    a = r["attributes"]
    loc = a["source_locator"]
    m = re.match(r'^(Table 1|Supplementary Table 4), row "(.*?)" \(group \'(.*?)\'(?:, the row directly under \'(.*?)\')?\), column "(.*?)"$', loc)
    if not m:
        stat["unparsed"] += 1; bad.append((r["id"], "unparsed", loc)); continue
    tab, label, group, prev, col = m.groups()
    rows, cols = (t1, t1_cols) if tab == "Table 1" else (s4, s4_cols)
    cand = [x for x in rows if norm(x["label"]) == norm(label) and x["group"] == group and (prev is None or norm(x["prev"] or "") == norm(prev))]
    if len(cand) != 1:
        stat["row_ambiguous_or_missing"] += 1; bad.append((r["id"], f"rows={len(cand)}", loc)); continue
    if col not in cols:
        stat["col_missing"] += 1; bad.append((r["id"], "col", loc)); continue
    v = cand[0]["vals"][cols.index(col)]
    cells_used[(tab, cand[0]["line"], col)] += 1
    ok = v == a["printed_value"] and float(a["numeric_value"]) == float(v)
    stat["match" if ok else "mismatch"] += 1
    if out: out.write(f"{r['id']}\t{'match' if ok else 'mismatch'}\t{a['printed_value']}\t{v}\t{tab}\t{cand[0]['line']}\t{col}\n")
    if not ok:
        bad.append((r["id"], f"cell={v} printed={a['printed_value']} numeric={a['numeric_value']}", loc))
    ev = [l["target_id"] for l in r["links"] if l["relation"] == "evaluation"][0]
    by_eval[ev].append((tab, cand[0]["label"], cand[0]["line"], col))

print(dict(stat))
print("cells used more than once:", [k for k, v in cells_used.items() if v > 1])
for b in bad[:40]:
    print(b)
# every evaluation should cite a single row per table
for ev, cs in by_eval.items():
    rowsets = {(t, l) for t, _, l, _ in cs}
    if len({t for t, l in rowsets}) != len(rowsets):
        print("eval uses >1 row of one table:", ev, rowsets)
    if len(cs) != 10 or len({c for *_, c in cs}) != 10:
        print("eval metric count off:", ev, len(cs))
# duplicate printings: confirm equality of every repeated run between T1 and S4 and inside S4
shared = [0, 1, 2, 3, 4, 7, 8, 9]

print("--- relaxed T1 to S4 cross-check ---")
n = 0
for x in t1:
    if x["label"] == "w/o labels":
        m = [y for y in s4 if y["label"] == "- hit labels" and norm(y["prev"] or "") == norm(x["prev"] or "")]
    else:
        m = [y for y in s4 if norm(y["label"]) == norm(x["label"]) and y["group"] == x["group"]]
    if len(m) != 1:
        print("unmatched", x["label"], len(m)); continue
    if [m[0]["vals"][i] for i in shared] != x["vals"]:
        print("differ", x["label"])
    else:
        n += 1
print("T1 rows equal to S4 in 8 shared cols:", n, "of", len(t1))
pairs = [("Qwen3.6-27B", "Qwen3.6-27B (base)"), ("AssayFormer (Random)", "AssayFormer (random embs.)"),
         ("AssayFormer (BPMF)", "+ BPMF Embeddings"), ("BPMF + GRPO", "+ GRPO (= AssayFormer)")]
for a_, b_ in pairs:
    A = [y for y in s4 if norm(y["label"]) == norm(a_)]
    B = [y for y in s4 if norm(y["label"]) == norm(b_)]
    print(a_, "|", b_, len(A), len(B), A and B and A[0]["vals"] == B[0]["vals"])
# any other S4 rows with identical values?
c = collections.Counter(tuple(y["vals"]) for y in s4)
print("S4 identical value rows:", [[y["label"] for y in s4 if tuple(y["vals"]) == k] for k, v in c.items() if v > 1])
