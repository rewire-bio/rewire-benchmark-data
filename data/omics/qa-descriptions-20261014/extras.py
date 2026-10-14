"""Issue #88, after merging origin/main into #158: write extras-corrections.csv for the records that
arrived after the change tables were written (#157 Feng remaining tables, #160 VEP literature pass)
and that `npm run records -- descriptions` flags.

- Configurations: build.py's generator, then review-fixes.py's rules applied to its output, so
  the new rows follow the reviewed rules (no commit written as a version, no repeated label, no
  source commentary, "no settings beyond its name are recorded" where the label carries the
  settings). The previous description moves to provenance_note verbatim.
- Methods: new sentences from primary sources, with evidence, in systems-researched-extras.jsonl.

  python3 -I data/omics/qa-descriptions-20261014/extras.py
  npm run records:correct -- data/omics/qa-descriptions-20261014/extras-corrections.csv docs/reviews/2026-10-14-functional-descriptions.md
Run from the repository root. Each row checks the old value.
"""
import csv
import importlib.util
import json
import re

HERE = "data/omics/qa-descriptions-20261014"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


review = load("review_fixes", f"{HERE}/review-fixes.py")
build = review.build

# The VEP literature configurations record where their scores came from in `version`, which
# build.py writes out as settings. Two more rules in the reviewer's spirit:
# - score-source: say the configuration is precomputed scores from dbNSFP, the tool's own download
#   or ProteinGym, without the download URL or remarks such as "release not stated".
# - snapshot-commit: a ProteinGym clinical summary label ("[ProteinGym 144fe22 clinical summary]")
#   is dropped from the subject and the commit is written as the scores' commit, as review-fixes.py
#   does for the substitution summaries.
PG_TAG = re.compile(r"\s*\[ProteinGym [0-9a-f]{7} clinical summary\]$")
PG_COMMIT = re.compile(r"ProteinGym commit ([0-9a-f]{40})")
DBNSFP = re.compile(r"^dbNSFP (\d[\w.]*)")


def fix_score_source(record, records, new):
    version = record["attributes"].get("version")
    if not isinstance(version, str):
        return new, []
    named = dict(record, name=PG_TAG.sub("", record["name"]))
    _, subject = review.subject_of(named, records)
    commit = PG_COMMIT.search(version)
    if PG_TAG.search(record["name"]) and commit:
        db = DBNSFP.match(version)
        tail = f" ({db.group(0)} scores)" if db else ""
        return f"{subject}, from the ProteinGym clinical reference scores at commit {commit.group(1)[:8]}{tail}.", ["snapshot-commit"]
    if DBNSFP.match(version):
        return f"{subject}: precomputed scores from {DBNSFP.match(version).group(0)}.", ["score-source"]
    if version.startswith("Predictions from the ProteinGym website"):
        return f"{subject}: scores from the ProteinGym reference score files; no ProteinGym release or settings beyond its name are recorded.", ["score-source"]
    if version.startswith("Predictions obtained from See referenced paper"):
        return f"{subject}: scores computed as described in the method's own paper; no settings beyond its name are recorded.", ["score-source"]
    if version.startswith("Predictions obtained from http"):
        return f"{subject}: scores from the tool's own published code or score files; no release or settings beyond its name are recorded.", ["score-source"]
    return new, []


GENERATED = ("Generated from the record's own name, links and attributes by "
             f"{HERE}/build.py with the rules of review-fixes.py ({{rules}}); "
             "the previous description is kept in attributes.provenance_note.")


def main():
    records = build.read_store()
    build.BENCHMARK_WORDS.update(build.norm(r["name"]) for r in records.values()
                                 if r["kind"] == "benchmark" and len(build.norm(r["name"])) >= 5)
    assessed = build.assessments(records)
    systems = {}
    for line in open(f"{HERE}/systems-researched-extras.jsonl"):
        row = json.loads(line)
        systems[row["id"]] = row
    rows, missing, failures = [], [], []
    for rid in build.flagged():
        r = records[rid]
        if r.get("status") == "excluded":
            continue
        if r["kind"] == "configuration":
            generated = build.configuration_description(r, records, assessed)
            new, rules = review.fix_configuration(r, records, generated)
            new, more = fix_score_source(r, records, new)
            if more:
                rules = [x for x in rules if x != "dropped-settings"] + more
            note = r["description"]
            evidence = GENERATED.format(rules=", ".join(["build.py"] + rules))
        elif rid in systems:
            s = systems[rid]
            assert s["old_description"] == r["description"], rid
            new, note = s["new_description"], s["provenance_note"]
            evidence = f"{s['evidence_url']} {s['evidence_locator']}".strip() + f": \"{s['evidence_quote']}\""
        else:
            missing.append(rid)
            continue
        if build.bad(new):
            failures.append(f"{rid}: {new}")
            continue
        rows.append({"record_id": rid, "field": "description", "old_value": r["description"], "new_value": new, "evidence": evidence})
        current = r["attributes"].get("provenance_note")
        if note and note != current:
            rows.append({"record_id": rid, "field": "attributes.provenance_note", "old_value": current or "",
                         "new_value": note if not current else f"{current} {note}", "evidence": evidence})
    if failures:
        raise SystemExit("generated descriptions still carry provenance:\n" + "\n".join(failures))
    if missing:
        raise SystemExit(f"no new description for {len(missing)} records: {missing}")
    with open(f"{HERE}/extras-corrections.csv", "w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=["record_id", "field", "old_value", "new_value", "evidence"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len({r['record_id'] for r in rows})} records, {len(rows)} rows")


if __name__ == "__main__":
    main()
