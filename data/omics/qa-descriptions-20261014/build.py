"""Issue #88: write corrections.csv, the change table that gives every model, method, pipeline,
service and configuration flagged by `npm run records -- descriptions` a functional description
and moves the provenance text to attributes.provenance_note.

- Models, methods, pipelines and services: rows come from systems-researched.jsonl (new
  sentences written from primary sources, with the evidence for each) and systems-split.jsonl
  (sourced functional text kept, provenance split off; written by split.py).
- Configurations: the description is generated from the record's own fields, so it says what the
  configuration is: its label, what it configures (configuration_of, uses_model or family links)
  and its recorded settings (parameters, training setting, representation and head,
  hyperparameters, reported configuration, checkpoint, version). Entries with no settings or
  links are described by the benchmark they were scored in. The previous description moves to
  provenance_note unchanged, so no text is lost.

Replay (from the repository root, after any change to the store layout):
  python3 -I data/omics/qa-descriptions-20261014/split.py
  python3 -I data/omics/qa-descriptions-20261014/build.py
  npm run records:correct -- data/omics/qa-descriptions-20261014/corrections.csv docs/reviews/2026-10-14-functional-descriptions.md
The table checks each old value, so it refuses to apply to records that changed since.
Then apply the review's fixes (review-fixes.py writes review-corrections.csv; see its docstring).
"""
import csv
import glob
import json
import re
import subprocess

HERE = "data/omics/qa-descriptions-20261014"
GENERATED = ("Generated from the record's own name, links and attributes by "
             f"{HERE}/build.py; the previous description is kept in attributes.provenance_note.")
SPLIT = "Sourced functional text kept from the reviewed description; provenance moved to attributes.provenance_note."


def read_store():
    records = {}
    for path in glob.glob("data/entities/*.jsonl") + glob.glob("data/evidence/**/*.jsonl", recursive=True):
        if "/results" in path:
            continue
        for line in open(path):
            r = json.loads(line)
            records[r["id"]] = r
    return records


def flagged():
    out = subprocess.run(["npm", "run", "-s", "records", "--", "descriptions", "--json"],
                         check=True, capture_output=True, text=True).stdout
    return sorted({p["id"] for p in json.loads(out)})


# The same patterns as shared/omics/descriptions.ts, used to clean generated text.
PROVENANCE = [
    r"\bas (run|evaluated|reported|scored|listed|used|printed|selected|submitted|implemented|benchmarked|quoted|trained and evaluated|evaluated and reported)\b.{0,60}?\b(in|on|by|to|for)\b",
    r"\bquoted (in|from)\b", r"\bnot a new(ly)?[- ](execution|executed)\b",
    r"\b(in|from) the cited (study|comparison|benchmark|source|paper|evaluation)\b",
    r"\(this (paper|source|study)\)|\bin this (paper|source)\b", r"\bsource-reported\b",
    r"\b(comparator reported by|evaluated by the [^.;]{1,60} authors\b|is the configuration evaluated in)",
    r"\b(cited in the source as|the method record names)\b",
    r"\bidentity as reported\b", r"\bsource-(reported|label(led)?) configuration\b", r"\bcandidate catalogue entry\b",
    r"^named prediction model family\b",
]
LOCATOR = re.compile(r"\s*\([^()]*\b(Table|Tables|Fig\.|Figure|Supplementary|Section|Introduction|Appendix|Methods|paragraph)\b[^()]*\)")
CITATION = re.compile(r"\s*\([^()]*(\bet al\.?|\b(19|20)\d\d\b)[^()]*\)")
LABEL_TAIL = re.compile(r"\s*[\(\[][^()\[\]]*(\bet al\b|\b(19|20)\d\d\b|\bTable\b|\bpaper\b|\bbenchmark\b|\bleaderboard\b|\bsnapshot\b|\bsubmission\b|\bstudy\b|\bevaluation\b|\bcomparison\b)[^()\[\]]*[\)\]]$", re.I)
JUNK = re.compile(r"''|\b(provenance is unresolved|comparator configuration|not specified|the source does not|printed in the source|not assumed|protocol pages specify|source reports|evaluated configuration|as named in|not printed|not inferred|unreported|not established|not identified|as printed|as listed|paper-specific|table-specific|retained|see linked)\b", re.I)


def bad(text):
    return any(re.search(p, text, re.I) for p in PROVENANCE) or LOCATOR.search(text) or CITATION.search(text)


def clean(text):
    """Drop locators and citations, then any sentence that is still provenance."""
    text = CITATION.sub("", LOCATOR.sub("", str(text).replace("et al.", "et al"))).strip()
    parts = [p.strip() for p in re.split(r"(?<=[.;])\s+", text) if p.strip()]
    parts = [p for p in parts if not bad(p) and not JUNK.search(p)]
    return " ".join(parts).strip().rstrip(".;,: ").strip()


BENCH_TAIL = re.compile(r"\s*\(([^()]*)\)$")
BENCHMARK_WORDS = set()


def label_of(record):
    label = clean_label(record["name"])
    m = BENCH_TAIL.search(label)
    if m and (re.search(r"bench|gym|flexms|in the wild", m.group(1), re.I) or any(w in norm(m.group(1)) for w in BENCHMARK_WORDS)):
        label = label[: m.start()].strip()
    return label


def clean_label(label):
    label = label.strip()
    while True:
        shorter = LABEL_TAIL.sub("", CITATION.sub("", LOCATOR.sub("", label))).strip()
        if shorter == label or not shorter:
            break
        label = shorter
    return re.sub(r"[†‡*]+", "", label).strip()


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def lower_first(s):
    # Names lead most settings (Illumina, RefSeq, GeoDock), so the source's casing is kept.
    return s


def benchmark_of(records, assessment_id, depth=0):
    r = records.get(assessment_id)
    if not r or depth > 4:
        return None
    if r["kind"] == "benchmark":
        return r
    for link in r["links"]:
        if link["relation"] in ("part_of", "parent", "evaluates_task"):
            found = benchmark_of(records, link["target_id"], depth + 1)
            if found:
                return found
    return None


def assessments(records):
    by_system = {}
    for r in records.values():
        if r["kind"] != "evaluation":
            continue
        systems = [l["target_id"] for l in r["links"] if l["relation"] == "system"]
        targets = [l["target_id"] for l in r["links"] if l["relation"] == "assessment"]
        for s in systems:
            by_system.setdefault(s, []).extend(targets)
    return by_system


# Records whose previous text did not reduce cleanly; each sentence is taken from that text.
OVERRIDES = {
    "perteval-scfm-2025-method-gears": "GEARS trained from scratch without pretrained weights, on train-test splits aligned with SPECTRA and with other parameters at their default values.",
    "perteval-scfm-2025-method-mean-baseline": "Predicts each cell's perturbation effect as the mean gene expression of all cells in the same context minus the cell's own expression.",
    "lit-cells-networks-20261011-ye2026grn-config-grnboost": "GRNBoost run directly on each test expression matrix with the default benchmark configuration, without pretrained representations.",
}

SETTING_KEYS = ["parameters", "training_setting", "representation", "head", "hyperparameters",
                "reported_configuration", "checkpoint", "protocol"]
TARGET_RELATIONS = ["configuration_of", "uses_model", "family"]


def settings_of(record, label, target_names):
    a = record["attributes"]
    seen, out = {norm(label), norm(record["name"]), *map(norm, target_names)}, []
    for key in SETTING_KEYS:
        value = a.get(key)
        if not isinstance(value, str):
            continue
        value = clean(value.split(". ")[0] if key != "parameters" else value)
        if key == "parameters":
            value = clean(re.split(r"(?<=\.)\s+", value)[0]) if value else value
        if not value or len(value) < 4 or norm(value) in seen or any(norm(value) in s for s in seen if len(norm(value)) > 6):
            continue
        if key == "reported_configuration" and (norm(value) in norm(record["name"]) or norm(value).startswith(norm(label))):
            continue
        seen.add(norm(value))
        out.append(lower_first(value))
        if len(out) == 2:
            break
    version = a.get("version")
    if isinstance(version, str) and len(version) <= 40 and not JUNK.search(version) and not bad(version) \
            and norm(version) not in norm(label) and not any(norm(version) in norm(s) for s in out):
        out.insert(0, f"version {version}" if re.match(r"^v?\d", version) else lower_first(version))
    return out


def residual(record, label, target_names):
    """The functional part of the previous description, if any is left once provenance goes."""
    text = record["description"].replace("et al.", "et al")
    text = re.sub(r",?\s*\bas (run|evaluated|reported|scored|listed|used|printed|selected|submitted|implemented|benchmarked|quoted|trained and evaluated)\b.*?(?=\.\s+(?-i:[A-Z])|\.$|[;:]|$)", "", text, flags=re.I)
    text = re.sub(r"\s*\b(evaluated|trained|run|implemented|scored|selected)\b[^.;]*?\bby the [^.;]*?authors\b[^.;]*", "", text, flags=re.I)
    text = clean(text).lstrip(" .,;:")
    if not text or len(text.split()) < 3:
        return None
    n = norm(text)
    if n in norm(label) or any(n in norm(t) for t in target_names) or norm(label) == n:
        return None
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    if words and len(words & set(re.findall(r"[a-z0-9]+", label.lower()))) / len(words) >= 0.7:
        return None
    text = re.split(r"(?<=\.)\s+(?-i:[A-Z])", text)[0].rstrip(".")
    return text


def configuration_description(record, records, assessed):
    if record["id"] in OVERRIDES:
        return OVERRIDES[record["id"]]
    label = label_of(record)
    targets = [records[l["target_id"]] for rel in TARGET_RELATIONS for l in record["links"]
               if l["relation"] == rel and l["target_id"] in records]
    target_names = []
    for t in targets:
        if clean_label(t["name"]) not in target_names:
            target_names.append(clean_label(t["name"]))
    benches = []
    for a in assessed.get(record["id"], []):
        b = benchmark_of(records, a)
        name = b["name"] if b else (records[a]["name"] if a in records else None)
        if name and name not in benches:
            benches.append(name)

    if record["id"].startswith("acquired-configuration") and not target_names:
        bench = benches[0] if benches else "the source benchmark"
        # Entry labels are free text chosen by participants, so they stay in the name only.
        return f"Entry in {bench}, identified only by its entry label; the model or method behind it is not identified."

    subject = label
    if target_names and not any(norm(t) in norm(label) or norm(label) in norm(t) for t in target_names):
        subject = f"{label}, a configuration of {' and '.join(target_names[:2])}"
    elif target_names and norm(label) == norm(target_names[0]):
        subject = f"Configuration of {target_names[0]}"
    settings = settings_of(record, label, target_names)
    lead = residual(record, label, target_names)
    if lead and any(norm(lead) in norm(x) or norm(x) in norm(lead) for x in settings):
        lead = None
    details = ([lead] if lead else []) + settings
    if details:
        text = f"{subject}: {details[0]}"
        for d in details[1:3]:
            if len(text) + len(d) > 280:
                break
            text += f"; {d}"
        if len(text) > 320:
            cut = text.rfind("; ", 0, 300)
            text = text[:cut] if cut > len(subject) + 20 else text[: text.rfind(" ", 0, 300)].rstrip(",;:")
        return text.rstrip(".") + "."
    if target_names:
        return f"{subject}; its settings are not recorded."
    if benches:
        return f"{label}, scored on {benches[0]}; its model version and settings are not identified."
    return f"{label}; its model version and settings are not identified."


def main():
    records = read_store()
    BENCHMARK_WORDS.update(norm(r["name"]) for r in records.values() if r["kind"] == "benchmark" and len(norm(r["name"])) >= 5)
    ids = flagged()
    assessed = assessments(records)
    systems = {}
    for name in ("systems-researched.jsonl", "systems-split.jsonl"):
        for line in open(f"{HERE}/{name}"):
            row = json.loads(line)
            systems[row["id"]] = row
    rows = []
    missing = []
    failures = []
    for rid in ids:
        r = records[rid]
        if r.get("status") == "excluded":
            continue
        if r["kind"] == "configuration":
            new = configuration_description(r, records, assessed)
            note = r["description"]
            evidence = GENERATED
        elif rid in systems:
            s = systems[rid]
            assert s["old_description"] == r["description"], rid
            new, note = s["new_description"], s["provenance_note"]
            evidence = (f"{s['evidence_url']} {s['evidence_locator']}".strip() + (f": \"{s['evidence_quote']}\"" if s["evidence_url"] else "")) or SPLIT
            if not s["evidence_url"]:
                evidence = SPLIT
        else:
            missing.append(rid)
            continue
        if bad(new):
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
        raise SystemExit(f"no new description for {len(missing)} records: {missing[:10]}")
    with open(f"{HERE}/corrections.csv", "w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=["record_id", "field", "old_value", "new_value", "evidence"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len({r['record_id'] for r in rows})} records, {len(rows)} rows")


if __name__ == "__main__":
    main()
