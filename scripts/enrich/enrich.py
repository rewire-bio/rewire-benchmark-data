"""Fill in records from checked content files, in batches.

The loop this tool serves is described in docs/knowledge-base.md. In short: research agents write
one content file (spec.json) per record, with a passage copied from a saved source behind every
statement; check_spec.py confirms the passages; verifier agents judge whether the statements
follow; this tool turns the checked files into store changes.

Run from the repository root.

  python3 scripts/enrich/enrich.py select <work dir> --tier 1 --count 25
      Pick the model records most in need of a page (no profile, most results first, one record
      per name) and write a folder with input.json for each, plus the brief and the checker.
      The research agents work in that folder.

  python3 scripts/enrich/enrich.py prepare <work dir> <batch name> [--replace]
      Check every content file and write data/omics/<batch name>/ with the source records to
      add (batch.jsonl), the content files (specs/), the fetched files that may be stored
      (artifacts/) and the planned record changes (models.json). --replace rewrites a profile a
      record already has, for corrections.

  npm run records -- add data/omics/<batch name>/batch.jsonl data/omics/<batch name>
      Skip when batch.jsonl is empty.

  python3 scripts/enrich/enrich.py models <batch name>
      Apply the planned changes to data/entities/models.jsonl.

  npm run records -- change docs/reviews/<review>.md data/omics/<batch name> <record ids>
  npx tsx scripts/enrich/validate.ts <batch name>
  python3 scripts/enrich/scorecard.py --write
"""
import hashlib, json, pathlib, re, shutil, subprocess, sys

def dump(o): return json.dumps(o, ensure_ascii=False, separators=(",", ":"))
def norm(s): return re.sub(r"\s+", " ", s).strip()

def prepare(specs_dir, batch):
    specs_dir = pathlib.Path(specs_dir); out = pathlib.Path("data/omics") / batch
    (out / "specs").mkdir(parents=True, exist_ok=True); (out / "artifacts").mkdir(exist_ok=True)
    existing, pinned = set(), {}
    for l in open("data/entities/sources.jsonl"):
        if l.strip():
            r = json.loads(l); existing.add(r["id"])
            if r["attributes"].get("artifact_sha256"): pinned.setdefault((r["attributes"]["artifact_sha256"], r["attributes"].get("url")), r["id"])
    # Licence strings a source record may carry: the reviewed rows of the licence map.
    # Rows that record an owner ruling or a spelling are for strings a metadata service serves, not for records.
    mapped = set()
    for l in open("data/archive/licence-map.tsv"):
        cells = l.rstrip("\n").split("\t")
        if l.strip() and not l.startswith("#") and not (cells[4:] and cells[4].startswith(("Owner ruling", "Read as a spelling"))): mapped.add(cells[0])
    models = {}
    for l in open("data/entities/models.jsonl"):
        if l.strip(): r = json.loads(l); models[r["id"]] = r
    sources, plan, skipped = [], {}, []
    for d in sorted(p for p in specs_dir.iterdir() if p.is_dir()):
        sp = d / "spec.json"
        if not sp.is_file(): skipped.append((d.name, "no spec.json")); continue
        ok = subprocess.run([sys.executable, "-I", str(specs_dir / "check_spec.py"), str(d)], capture_output=True, text=True)
        spec = json.loads(sp.read_text())
        if ok.returncode != 0 or "profile" not in spec: skipped.append((d.name, (ok.stdout.strip().splitlines() or ["no profile"])[0])); continue
        rid = spec["record_id"]; rec = models[rid]; slug = re.sub(r"^\d+-", "", d.name)
        if rec["attributes"].get("profile") and "--replace" not in sys.argv: skipped.append((d.name, "record already has a profile")); continue
        idmap = {}
        for s in spec["sources"]:
            sid = f"{batch}-{slug}-source-" + re.sub(r"[^a-z0-9]+", "-", s["key"].lower()).strip("-"); idmap["@" + s["key"]] = sid
            b = (d / s["file"]).read_bytes(); assert hashlib.sha256(b).hexdigest() == s["sha256"]
            # The same bytes at the same address are one source: cite the record that already pins them.
            if (s["sha256"], s["url"]) in pinned:
                idmap["@" + s["key"]] = pinned[(s["sha256"], s["url"])]; continue
            assert sid not in existing, sid
            pinned[(s["sha256"], s["url"])] = sid
            attrs = {"artifact_sha256": s["sha256"], "artifact_url": s["artifact_url"], "media_type": s["media_type"],
                     "publication_status": "official_project_source", "retrieved_at": s["retrieved_at"], "url": s["url"], "version": s["version"]}
            if s.get("licence") in mapped: attrs["licence"] = s["licence"]
            sources.append({"id": sid, "kind": "source", "name": s["name"], "description": s["description"], "status": "discovered",
                            "facets": {"areas": rec["facets"].get("areas", []), "contexts": rec["facets"].get("contexts", ["research"])},
                            "source_ids": [], "links": [], "attributes": attrs})
            if s["store_bytes"]:
                (out / "artifacts" / slug).mkdir(exist_ok=True); shutil.copy(d / s["file"], out / "artifacts" / slug / pathlib.Path(s["file"]).name)
        def ev(o):
            o = dict(o); o.pop("quotes", None); o["source_ids"] = [idmap.get(i, i) for i in o["source_ids"]]; return o
        p = spec["profile"]
        profile = {"summary": p["summary"], "summary_source_ids": [idmap.get(i, i) for i in p["summary_source_ids"]], "summary_source_locator": p["summary_source_locator"],
                   "sections": [ev(s) for s in p["sections"]], "facts": [ev(f) for f in p["facts"]],
                   "strengths": [ev(s) for s in p["strengths"]], "limitations": [ev(s) for s in p["limitations"]]}
        if p.get("diagram"): profile["diagram"] = ev(p["diagram"])
        profile.update({"coverage": p["coverage"], "gaps": p["gaps"], "review": p["review"]})
        guide = None
        if spec.get("run_guide"):
            g = spec["run_guide"]
            guide = {"record_id": rid, "summary": g["summary"], "status": "source_reviewed_not_executed", "prerequisites": g["prerequisites"],
                     "steps": [ev(s) for s in g["steps"]], "outputs": g["outputs"], "limitations": g["limitations"],
                     "source_ids": [idmap.get(i, i) for i in g["source_ids"]], "review": {"method": "official_repository_review", "date": p["review"]["date"]}}
        plan[rid] = {"slug": slug, "new_source_ids": [idmap["@" + s["key"]] for s in spec["sources"]], "profile": profile, "run_guide": guide,
                     "notes": spec.get("notes", ""), "no_run_guide_reason": spec.get("no_run_guide_reason", "")}
        shutil.copy(sp, out / "specs" / f"{slug}.json")
    (out / "batch.jsonl").write_text("".join(dump(s) + "\n" for s in sources))
    (out / "models.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"{len(plan)} models, {len(sources)} sources; skipped: {skipped}")

def apply_models(batch):
    out = pathlib.Path("data/omics") / batch; plan = json.loads((out / "models.json").read_text())
    path = pathlib.Path("data/entities/models.jsonl"); lines = path.read_text().split("\n"); done = set()
    for i, line in enumerate(lines):
        if not line.strip(): continue
        rid = line[7:line.index('"', 7)]
        if rid in plan:
            rec = json.loads(line); assert rec["id"] == rid; e = plan[rid]
            rec["source_ids"] = rec["source_ids"] + [s for s in e["new_source_ids"] if s not in rec["source_ids"]]
            rec["attributes"]["profile"] = e["profile"]            # a new key is appended; an existing one keeps its place
            if e["run_guide"]: rec["attributes"]["run_guide"] = e["run_guide"]
            lines[i] = dump(rec); done.add(rid)
    assert done == set(plan), set(plan) - done
    path.write_text("\n".join(lines)); print(" ".join(sorted(done)))

def select(work, tier, count):
    """Write an input folder per model: Tier `tier`, no profile, one record per name, most results first."""
    import collections, glob
    work = pathlib.Path(work); work.mkdir(parents=True, exist_ok=True)
    here = pathlib.Path(__file__).parent
    shutil.copy(here / "check_spec.py", work / "check_spec.py"); shutil.copy(here / "briefs" / "model-page.md", work / "BRIEF.md")
    load = lambda path: [json.loads(l) for l in open(path) if l.strip()]
    sources = {s["id"]: s for s in load("data/entities/sources.jsonl")}
    models = load("data/entities/models.jsonl")
    parent = {}
    for c in load("data/entities/configurations.jsonl"):
        for link in c.get("links", []):
            if link["relation"] in ("configuration_of", "variant_of", "family", "uses_model"): parent[c["id"]] = link["target_id"]
    system = {}
    for path in glob.glob("data/evidence/evaluations/*.jsonl"):
        for e in load(path):
            for link in e.get("links", []):
                if link["relation"] == "system": system[e["id"]] = link["target_id"]
    results = collections.Counter()
    for path in glob.glob("data/evidence/results/*.jsonl"):
        for r in load(path):
            for link in r.get("links", []):
                if link["relation"] == "evaluation" and link["target_id"] in system:
                    s = system[link["target_id"]]; results[parent.get(s, s)] += 1
    names = collections.Counter(m["name"] for m in models)
    todo = [m for m in models if m["attributes"].get("depth_tier") == tier and "profile" not in m["attributes"] and names[m["name"]] == 1]
    todo.sort(key=lambda m: -results[m["id"]])
    for n, m in enumerate(todo[:count], 1):
        slug = re.sub(r"[^a-z0-9]+", "-", m["name"].lower()).strip("-"); d = work / f"{n:02d}-{slug}"; (d / "artifacts").mkdir(parents=True, exist_ok=True)
        keep = ("reported_name", "entity_level", "identity_scope", "access", "licence", "training_data", "source_locator")
        (d / "input.json").write_text(json.dumps({"record_id": m["id"], "slug": slug, "name": m["name"], "description": m["description"], "facets": m["facets"],
            "attributes": {k: v for k, v in m["attributes"].items() if k in keep},
            "existing_sources": [{"id": s, "name": sources[s]["name"], "url": sources[s]["attributes"].get("url"), "artifact_url": sources[s]["attributes"].get("artifact_url"),
                                  "note": "already in the store; may be a benchmark paper or the model's own source"} for s in m["source_ids"]]}, indent=1))
        print(f"{n:02d}-{slug}\t{results[m['id']]} results")
    print(f"{min(count, len(todo))} of {len(todo)} Tier {tier} models without a profile; names on two records are left out")

if __name__ == "__main__":
    arg = lambda flag, default: int(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default
    {"select": lambda: select(sys.argv[2], arg("--tier", 1), arg("--count", 25)),
     "prepare": lambda: prepare(sys.argv[2], sys.argv[3]), "models": lambda: apply_models(sys.argv[2])}[sys.argv[1]]()
