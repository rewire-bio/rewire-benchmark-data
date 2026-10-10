"""QA fixes #88(b) and #89, 2026-10-10. Run from the worktree root:
python3 -I apply_fixes.py <notes-dir> <scratch-dir>

#88(b): strip a trailing citation suffix from method and model descriptions, after checking
that every cited author-year source is in source_ids. #89: rewrite three CNV judgement reasons.
Records are edited in place by replacing the exact JSON-encoded string in their line, so no
other byte of the store changes. One metadata-correction claim per changed field goes to
<notes-dir>/batch.jsonl; a change list goes to <scratch-dir>/changes.json.
"""
import hashlib, json, re, sys

NOTES, SCRATCH = sys.argv[1], sys.argv[2]
DATE = "2026-10-10"
SUFFIX = re.compile(r"\((?:[A-Z][a-z]+ et al\.|[A-Z][a-z]+) \d{4}[a-z]? (?:Table|Supp)[^)]*\)\.?$")
CITE = re.compile(r"([A-Z][a-z]+)(?: et al\.)? (\d{4})")


def enc(s):
    return json.dumps(s, ensure_ascii=False)


def replace_in_line(line, old, new):
    o, n = enc(old), enc(new)
    assert line.count(o) == 1, "old text not found exactly once"
    return line.replace(o, n)


sources = {}
for l in open("data/entities/sources.jsonl"):
    r = json.loads(l)
    sources[r["id"]] = r


def source_matches(sid, author, year):
    r = sources[sid]
    a = r["attributes"]
    hay = " ".join([sid, r["name"], str(a.get("version", "")), str(a.get("url", "")), str(a.get("doi", ""))])
    return author.lower() in sid.lower() and year in hay


changes, corrections = [], []


def correction(rec, field, old, new, why, locator):
    h = hashlib.sha256(f"{rec['id']}|{field}".encode()).hexdigest()[:20]
    corrections.append({
        "id": f"metadata-correction-qa-20261010-{h}", "kind": "claim", "name": f"{rec['name']}: {field}",
        "description": why, "status": "needs_review", "facets": {}, "source_ids": rec["source_ids"],
        "links": [{"relation": "subject", "target_id": rec["id"]}],
        "attributes": {"field": field, "previous_value": old, "value": new, "source_locator": locator,
                       "review": {"method": ["automated-source-review"], "reviewer": ["claude"],
                                  "reviewer_note": "Claude (Opus 5.5) QA agent for issues #88 and #89; not an independent review",
                                  "date": DATE, "note": why + " Pending independent review."}}})


# ---------------------------------------------------------------- #88(b)
WHY88 = "Remove the trailing citation suffix from the description (issue #88). The citation remains in source_ids; the sentence is otherwise unchanged."
left = []
for path in ("data/entities/methods.jsonl", "data/entities/models.jsonl"):
    lines = open(path).read().split("\n")
    for i, line in enumerate(lines):
        if not line:
            continue
        r = json.loads(line)
        d = r.get("description", "")
        m = SUFFIX.search(d)
        if not m:
            continue
        suffix = m.group(0)
        cited = CITE.findall(suffix)
        missing = [(a, y) for a, y in cited if not any(source_matches(s, a, y) for s in r["source_ids"])]
        if missing:
            cands = [sid for sid in sources for a, y in missing if source_matches(sid, a, y)]
            assert len(cands) == 1, (r["id"], missing, cands)
            raise SystemExit(f"{r['id']}: cited source missing from source_ids; candidate {cands}")
        new = d[: m.start()].rstrip()
        if not new.endswith("."):
            new += "."
        if "(" in new and re.search(r"\([A-Z][a-z]+(?: et al\.)? \d{4}", new):
            left.append({"id": r["id"], "note": "An inner citation remains mid-sentence; only the trailing suffix was removed."})
        lines[i] = replace_in_line(line, d, new)
        assert json.loads(lines[i])["description"] == new
        changes.append({"id": r["id"], "kind": r["kind"], "field": "description", "old": d, "new": new, "issue": 88, "cited": [f"{a} {y}" for a, y in cited]})
        correction(r, "description", d, new, WHY88, f"Record description; suffix '{suffix}'")
    open(path, "w").write("\n".join(lines))

# ---------------------------------------------------------------- #89
DLV = ("Not shown: the article's Results text and its Supplemental Table 3 disagree on whether CNVnator detected 1-5 kb events and on which caller had the lowest precision. "
       "The values here are recorded as printed in the tables, but they are not shown until that conflict is resolved.")
REASONS = {
    "use-case-mapping-cnv-20261009-delavega2025-hg002": DLV,
    "use-case-mapping-cnv-20261009-delavega2025-coriell-panel": (
        "Not shown: the article's Results text and its Supplemental Table 3 disagree on whether CNVnator detected 1-5 kb events and on which caller had the lowest precision. "
        "The conflict is in the HG002 table, not in this panel table, but it applies to the whole article, so these precision values are not shown until it is resolved."),
    "use-case-mapping-cnv-20261009-nardone2025-hg002-deletions": (
        "Not shown: the paper states the read depth and aligner behind Table S1 inconsistently (25x with bwa-mem2 in Methods, the DRAGEN pipeline in Results, 30x reads in Data Availability), "
        "and its text and Table S1 disagree for inGAP at 5,000-9,999 bp. The table values are recorded, but they are not compared with other HG002 tables until this is resolved."),
}
WHY89 = "Rewrite the held reason as a reader-facing caveat without workflow language (issue #89), using only facts in the claim and its source's evidence concerns."
path = "data/evidence/claims.jsonl"
lines = open(path).read().split("\n")
pins = {}
for i, line in enumerate(lines):
    if not line:
        continue
    r = json.loads(line)
    if r["id"] in REASONS:
        a = r["attributes"]
        pins[r["id"]] = "pins" in a
        old = a["reason"]
        lines[i] = replace_in_line(line, old, REASONS[r["id"]])
        after = json.loads(lines[i])
        assert after["attributes"]["reason"] == REASONS[r["id"]]
        after["attributes"]["reason"] = old
        assert after == r, "a field other than reason changed"
        changes.append({"id": r["id"], "kind": "claim", "field": "attributes.reason", "old": old, "new": REASONS[r["id"]], "issue": 89})
        correction(r, "attributes.reason", old, REASONS[r["id"]], WHY89, "Judgement claim attributes.reason")
assert len(pins) == 3
open(path, "w").write("\n".join(lines))

corrections.sort(key=lambda c: c["id"])
with open(f"{NOTES}/batch.jsonl", "w") as f:
    for c in corrections:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
json.dump({"changes": changes, "left_note": left, "pins_present": pins}, open(f"{SCRATCH}/changes.json", "w"), indent=1, ensure_ascii=False)
print("issue 88 changed:", sum(c["issue"] == 88 for c in changes), "issue 89 changed:", sum(c["issue"] == 89 for c in changes),
      "corrections:", len(corrections), "inner citations left:", len(left), "claims with pins:", sum(pins.values()))
