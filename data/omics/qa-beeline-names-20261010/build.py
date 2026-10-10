"""Make the BEELINE protocol names readable (rewire-benchmark-data#92), in place, and record each change.

Usage, from the repository root:
  python3 -I data/omics/qa-beeline-names-20261010/build.py           apply the change and write the notes
  python3 -I data/omics/qa-beeline-names-20261010/build.py --check   check the store against batch.jsonl

The original values are read from data/entities/protocols.jsonl at git HEAD, so applying is repeatable
until the change is committed. Targets are the BEELINE protocols whose name ends in a JSON object:
  - 44 Figure 5 protocols ending in {"reference_network":...,"gene_selection":...}: the name becomes
    "<prefix> · <reference_network> network, <gene_selection> genes";
  - 10 Figure 2 and Figure 4 protocols ending in " · {}": that suffix is dropped.
In each target the panel titles "<old name>: <metric>" become "<new name>: <metric>". In the 44 Figure 5
protocols, the caveat text "Input conditions: {...}" becomes "Input conditions: <reference_network> network,
<gene_selection> genes"; in the 10 empty-object protocols the sentence "Input conditions: {}." is dropped
from each caveat, and a caveat left empty is removed (its claim records value ""). The protocol description carries the same
"Input conditions" sentence and is changed the same way (added in review). Only the changed lines of protocols.jsonl are
rewritten; every other line is kept byte for byte. One metadata-correction claim is written per changed field. The --check
comparison of batch.jsonl ignores claim status and review, which the reviewer sets.
"""
import glob, hashlib, json, os, re, subprocess, sys

D = os.path.dirname(os.path.abspath(__file__))
STORE = "data/entities/protocols.jsonl"
NOTE = ("Make the text readable: replace the embedded JSON object with text built from the same values "
        "(rewire-benchmark-data#92). The values stay structured in attributes.conditions of the protocol's "
        "evaluations. Historical releases retain the previous value.")
FIG5 = re.compile(r'^(BEELINE 2020 Figure 5 · [^·]+) · (\{"reference_network":"[^"]*","gene_selection":"[^"]*"\})$')
EMPTY = re.compile(r"^(BEELINE 2020 Figure [24] · [^·]+) · \{\}$")


def dump(r):
    return json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n"


def expect(ok, where):
    if not ok:
        raise SystemExit(where)


head = subprocess.run(["git", "show", f"HEAD:{STORE}"], capture_output=True, text=True, check=True).stdout.splitlines(True)
original = [json.loads(line) for line in head]

evals = {}
for f in glob.glob("data/evidence/*.jsonl"):
    for line in open(f, encoding="utf-8"):
        e = json.loads(line)
        if e["kind"] == "evaluation":
            for link in e["links"]:
                if link["relation"] == "assessment":
                    evals.setdefault(link["target_id"], []).append(e)


def plan(i, r):
    """Return the edited record and a list of (field, previous, value) for a target, or None."""
    m5, m0 = FIG5.match(r["name"]), EMPTY.match(r["name"])
    if not (m5 or m0):
        expect("{" not in r["name"] or not r["name"].startswith("BEELINE"), f"unexpected BEELINE name form: {r['id']}")
        return None
    expect(dump(r) == head[i], f"line does not round-trip, refusing to rewrite: {r['id']}")
    new = json.loads(json.dumps(r))
    changes = []
    if m5:
        v = json.loads(m5.group(2))
        readable = f"{v['reference_network']} network, {v['gene_selection']} genes"
        new["name"] = f"{m5.group(1)} · {readable}"
        for e in evals.get(r["id"], []):
            c = e["attributes"].get("conditions", {})
            expect((c.get("reference_network"), c.get("gene_selection")) == (v["reference_network"], v["gene_selection"]),
                   f"evaluation conditions differ from the name: {e['id']}")
    else:
        new["name"] = m0.group(1)
    changes.append(("name", r["name"], new["name"]))
    desc = r["description"]
    if m5 and m5.group(2) in desc:
        new["description"] = desc.replace(f"Input conditions: {m5.group(2)}.", f"Input conditions: {readable}.")
    elif m0 and "Input conditions: {}." in desc:
        new["description"] = " ".join(desc.replace("Input conditions: {}.", "").split())
    expect("{" not in new["description"], f"description form not recognised: {r['id']}")
    if new["description"] != desc:
        changes.append(("description", desc, new["description"]))
    for k, panel in enumerate(new["attributes"].get("comparison_panels", [])):
        expect(panel["title"].startswith(r["name"] + ": "), f"panel title does not start with the name: {r['id']} panel {k}")
        old = panel["title"]
        panel["title"] = new["name"] + old[len(r["name"]):]
        changes.append((f"attributes.comparison_panels[{k}].title", old, panel["title"]))
        kept = []
        for j, caveat in enumerate(panel.get("caveats", [])):
            if m5 and m5.group(2) in caveat:
                text = caveat.replace(f"Input conditions: {m5.group(2)}.", f"Input conditions: {readable}.")
            elif m0 and "Input conditions: {}." in caveat:
                # the empty object carries no information; the real conditions are on the evaluations
                text = " ".join(caveat.replace("Input conditions: {}.", "").split())
            else:
                kept.append(caveat)
                continue
            expect(text != caveat and "{" not in text, f"caveat form not recognised: {r['id']}")
            changes.append((f"attributes.comparison_panels[{k}].caveats[{j}]", caveat, text))
            if text:
                kept.append(text)
        if "caveats" in panel:
            panel["caveats"] = kept
    return new, changes


plans = {}
for i, r in enumerate(original):
    p = plan(i, r)
    if p:
        plans[r["id"]] = (i, r, *p)
fig5 = [k for k, (_, r, _, _) in plans.items() if FIG5.match(r["name"])]
expect(len(plans) == 54 and len(fig5) == 44, f"expected 54 targets (44 Figure 5), found {len(plans)} ({len(fig5)})")
names = [p[2]["name"] for p in plans.values()] + [r["name"] for r in original if r["id"] not in plans]
expect(len(set(names)) == len(names), "new protocol names are not unique")

claims = []
for pid, (_, r, new, changes) in sorted(plans.items()):
    for field, prev, value in changes:
        cid = "metadata-correction-" + hashlib.sha256(f"{pid}:{field}:qa-beeline-20261010".encode()).hexdigest()[:20]
        label = "name" if field == "name" else field.removeprefix("attributes.").replace("comparison_panels", "panel")
        claims.append({"id": cid, "kind": "claim", "name": f"{new['name']}: {label}", "description": NOTE, "status": "needs_review",
                       "facets": r["facets"], "source_ids": r["source_ids"], "links": [{"relation": "subject", "target_id": pid}],
                       "attributes": {"field": field, "previous_value": prev, "value": value,
                                      "source_locator": r["attributes"].get("source_locator", ""),
                                      "review": {"method": ["automated-source-review"], "reviewer": ["claude"],
                                                 "reviewed_at": "2026-10-10T08:30:00Z", "note": NOTE}}})
expect(len({c["id"] for c in claims}) == len(claims), "claim ID collision")

if "--check" not in sys.argv:
    out = [dump(plans[r["id"]][2]) if r["id"] in plans else line for r, line in zip(original, head)]
    open(STORE, "w", encoding="utf-8").write("".join(out))
    with open(os.path.join(D, "batch.jsonl"), "w", encoding="utf-8") as f:
        for c in sorted(claims, key=lambda c: c["id"]):
            f.write(dump(c))
    # changes.md keeps its hand-written notes above the marker; the table below it is regenerated
    md = os.path.join(D, "changes.md")
    marker = "## Old and new names\n"
    notes = open(md, encoding="utf-8").read().split(marker)[0] if os.path.exists(md) else ""
    with open(md, "w", encoding="utf-8") as f:
        f.write(notes + marker + "\n| Protocol | Old name | New name |\n| --- | --- | --- |\n")
        for pid, (_, r, new, _) in sorted(plans.items(), key=lambda kv: kv[1][1]["name"]):
            f.write(f"| `{pid}` | `{r['name']}` | {new['name']} |\n")

# checks against the store as it now is
current = open(STORE, encoding="utf-8").read().splitlines(True)
expect(len(current) == len(head), "line count changed")
changed = [i for i, (a, b) in enumerate(zip(head, current)) if a != b]
expect(sorted(changed) == sorted(p[0] for p in plans.values()), "changed lines are not exactly the 54 targets")
for pid, (i, r, new, _) in plans.items():
    expect(current[i] == dump(new), f"store line differs from the planned record: {pid}")
    expect("{" not in new["name"] and all("{" not in p["title"] and not any("Input conditions: {" in c for c in p.get("caveats", []))
                                          for p in new["attributes"].get("comparison_panels", [])), f"braces left: {pid}")
    got = json.loads(current[i])
    expect({k: v for k, v in got.items() if k not in ("name", "description", "attributes")} == {k: v for k, v in r.items() if k not in ("name", "description", "attributes")},
           f"fields other than name, description and attributes changed: {pid}")
batch = [json.loads(line) for line in open(os.path.join(D, "batch.jsonl"), encoding="utf-8")]
def unreviewed(c):
    c = json.loads(json.dumps(c))
    c.pop("status", None)
    c["attributes"].pop("review", None)
    return json.dumps(c, sort_keys=True)


expect(sorted(unreviewed(c) for c in batch) == sorted(unreviewed(c) for c in claims), "batch.jsonl is stale")
kinds = {}
for _, _, _, ch in plans.values():
    for field, _p, _ in ch:
        k = field if field in ("name", "description") else ("title" if field.endswith(".title") else
                                            "caveat removed" if not _ else "caveat")
        kinds[k] = kinds.get(k, 0) + 1
print(f"{len(plans)} protocols changed ({len(fig5)} Figure 5, {len(plans) - len(fig5)} empty-object); "
      f"{len(claims)} claims {kinds}; {sum(len(evals.get(k, [])) for k in fig5)} evaluations checked; "
      f"unchanged lines {len(head) - len(changed)}")
