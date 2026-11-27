"""Put the structured facts of the page batches onto the records.

Each model or benchmark page batch keeps a `structured` list in its content files
(data/omics/model-pages-*/specs/*.json and data/omics/benchmark-pages-*/specs/*.json): one entry per
released checkpoint of a model, or per task or track of a benchmark, each with the passages it was
read from. This tool turns them into the `checkpoints` attribute of model records and the
`benchmark_tasks` attribute of benchmark records. Run from the repository root.

  python3 scripts/enrich/structured.py plan <batch name>
      Read every batch in the order kb/curate.py uses (a later batch replaces an earlier one's list
      for the same record), tie each entry to the record's source records and write
      data/omics/<batch name>/changes.json. A record with an entry that cannot be tied to its
      sources is reported and left out.

  python3 scripts/enrich/structured.py apply <batch name>
      Write the planned attributes onto data/entities/models.jsonl and benchmarks.jsonl.

Then record the change with npm run records -- change, as for any batch.
"""
import glob, json, pathlib, re, sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "kb"))
from curate import STRUCTURED, batch_order  # noqa: E402

def dump(o): return json.dumps(o, ensure_ascii=False, separators=(",", ":"))

# Per kind: the content files, fields and attribute kb/curate.py uses, the record file and the batch
# plan file that scripts/enrich/enrich.py prepare wrote.
KINDS = {kind: (pattern, columns, attribute, records_file, plan_file)
         for kind, (pattern, _, columns, attribute), records_file, plan_file in [
             ("model", STRUCTURED["checkpoint"], "data/entities/models.jsonl", "models.json"),
             ("benchmark", STRUCTURED["benchmark_task"], "data/entities/benchmarks.jsonl", "benchmarks.json")]}
LABELS = {
    "checkpoint": "checkpoint name", "parameters": "parameters", "context_length": "context length",
    "context_unit": "context unit", "code_licence": "code licence", "weights_licence": "weights licence",
    "code_url": "code address", "weights_url": "weights address", "gated": "access terms", "released": "release date",
    "task": "task", "dataset": "dataset", "size": "size", "size_unit": "size unit", "split": "split",
    "primary_metric": "metric", "metric_direction": "metric direction", "results_url": "results address",
    "data_url": "data address", "data_licence": "data licence",
}
LICENCE_WORDS = {"mit": ["mit"], "apache": ["apache"], "gpl": ["general public license", "gpl"], "agpl": ["affero", "agpl"],
                 "lgpl": ["lesser general", "lgpl"], "bsd": ["bsd"], "cc": ["creative commons", "cc by", "cc-by", "cc0"],
                 "mpl": ["mozilla"], "unlicense": ["unlicense"], "openrail": ["openrail", "rail"], "llama": ["llama"]}

def norm(s): return re.sub(r"\s+", " ", str(s)).strip().lower()

def mentions(field, value, quote):
    """Whether a quoted passage states this value, so the locator can say what the passage is about."""
    q = norm(quote)
    if value is None: return False
    if field == "gated":
        return bool(re.search(r"\bgated\b|\bprivate\b|request access|access request|agree to|accept the|log in|licen[cs]e agreement", q))
    if isinstance(value, int):
        forms = {str(value), f"{value:,}"}
        for scale, unit in ((10**9, "b"), (10**6, "m"), (10**3, "k")):
            if value >= scale and value % (scale // 100) == 0:
                forms |= {f"{value / scale:g}{unit}", f"{value / scale:g} {unit}"}
        return any(re.search(rf"(?<![\d.])(?<!\d,){re.escape(f)}(?![\d.]?\d)(?!,\d)", q) for f in forms)
    v = norm(value)
    if field.endswith("_url"):
        v = re.sub(r"^https?://(www\.)?", "", v).rstrip("/")
        return v in q or v.split("/")[-1] in q.split("/") and len(v.split("/")[-1]) > 3
    if field.endswith("_licence"):
        if v in q: return True
        family = re.split(r"[-\s]", v)[0]
        return any(re.search(rf"\b{re.escape(w)}\b", q) for w in LICENCE_WORDS.get(family, []))
    if field == "released":
        return v in q
    if len(v) > 2 and v in q: return True
    # Free-text values are often a paraphrase: count the passage when it holds most of the value's words.
    words = set(re.findall(r"[a-z0-9]{4,}", v))
    return len(words) >= 2 and len(words & set(re.findall(r"[a-z0-9]{4,}", q))) >= 0.6 * len(words)

def locator(entry, files):
    """Which saved file each passage is in and which fields it states, in order of first quote."""
    by_source = {}
    for q in entry["quotes"]:
        by_source.setdefault(q["source"], []).append(q["text"])
    parts = []
    for key, texts in by_source.items():
        fields = [LABELS[f] for f in LABELS if f in entry and any(mentions(f, entry[f], t) for t in texts)]
        about = ", ".join(fields) if fields else "supporting passage"
        parts.append(f"{files[key]}: {about}")
    return "; ".join(parts)

def load(path): return {r["id"]: r for r in (json.loads(l) for l in open(path) if l.strip())}

def source_map(batch_dir, spec, plan, record, sources):
    """Spec source key ("@paper") to source record id, mirroring scripts/enrich/enrich.py prepare.

    prepare gives each spec source the id <batch>-<slug>-source-<key>, unless a source record already
    pinned the same bytes at the same address, in which case it cites that record. Its plan file lists
    the ids it chose (new_source_ids, in spec source order), so that list is read first and the derived
    id and the pinned bytes are fallbacks. An id is accepted only if it is a source record with the
    spec's SHA-256 and the record cites it. Keys that pass none of these are left out of the map."""
    batch, slug = batch_dir.name, plan["slug"]
    out = {}
    for i, s in enumerate(spec["sources"]):
        derived = f"{batch}-{slug}-source-" + re.sub(r"[^a-z0-9]+", "-", s["key"].lower()).strip("-")
        candidates = [plan["new_source_ids"][i], derived] + [
            sid for sid in record["source_ids"]
            if sources.get(sid, {}).get("attributes", {}).get("artifact_sha256") == s["sha256"]
            and sources[sid]["attributes"].get("url") == s["url"]]
        for sid in candidates:
            src = sources.get(sid)
            if src and src["attributes"].get("artifact_sha256") == s["sha256"] and sid in record["source_ids"]:
                out["@" + s["key"]] = sid
                break
    return out

def plan(batch):
    sources = load("data/entities/sources.jsonl")
    changes, left_out, counts = {}, [], {}
    for kind, (pattern, fields, attribute, records_file, plan_file) in KINDS.items():
        records = load(records_file)
        latest = {}
        for path in sorted(glob.glob(pattern), key=batch_order):
            spec = json.load(open(path))
            if spec.get("structured"):
                latest[spec["record_id"]] = pathlib.Path(path)
        for rid, path in latest.items():
            batch_dir = path.parent.parent
            spec = json.load(open(path))
            batch_plan = json.loads((batch_dir / plan_file).read_text())[rid]
            assert batch_plan["slug"] == path.stem, path
            ids = source_map(batch_dir, spec, batch_plan, records[rid], sources)
            files = {"@" + s["key"]: pathlib.PurePosixPath(s["file"]).name for s in spec["sources"]}
            value, problems = [], []
            for n, e in enumerate(spec["structured"], 1):
                cited = list(dict.fromkeys(q["source"] for q in e.get("quotes") or []))
                missing = [c for c in cited if c not in ids]
                if not cited: problems.append(f"entry {n} has no quoted passage")
                elif missing: problems.append(f"entry {n} cites {', '.join(missing)}, which has no source record on the record")
                else:
                    value.append({**{f: e[f] for f in fields}, "source_ids": list(dict.fromkeys(ids[c] for c in cited)),
                                  "source_locator": locator(e, files)})
            if problems:
                left_out.append({"record_id": rid, "content_file": str(path), "problems": problems})
                continue
            changes[rid] = {"kind": kind, "attribute": attribute, "content_file": str(path),
                            "tier": records[rid]["attributes"].get("depth_tier"), "value": value}
            counts.setdefault(kind, [0, 0]); counts[kind][0] += 1; counts[kind][1] += len(value)
    out = pathlib.Path("data/omics") / batch
    out.mkdir(parents=True, exist_ok=True)
    (out / "changes.json").write_text(json.dumps({"records": changes, "left_out": left_out}, ensure_ascii=False, indent=1) + "\n")
    for kind, (n, e) in counts.items(): print(f"{kind}: {n} records, {e} entries")
    for item in left_out: print(f"left out {item['record_id']}: {'; '.join(item['problems'])}")

def apply(batch):
    changes = json.loads((pathlib.Path("data/omics") / batch / "changes.json").read_text())["records"]
    done = set()
    for kind, (_, _, attribute, records_file, _) in KINDS.items():
        path = pathlib.Path(records_file); lines = path.read_text().split("\n")
        for i, line in enumerate(lines):
            if not line.strip(): continue
            rid = line[7:line.index('"', 7)]
            if changes.get(rid, {}).get("kind") == kind:
                rec = json.loads(line); assert rec["id"] == rid
                rec["attributes"][attribute] = changes[rid]["value"]  # a new key is appended; an existing one keeps its place
                lines[i] = dump(rec); done.add(rid)
        path.write_text("\n".join(lines))
    assert done == set(changes), set(changes) - done
    print(" ".join(sorted(done)))

if __name__ == "__main__":
    {"plan": plan, "apply": apply}[sys.argv[1]](sys.argv[2])
