"""Check one model folder's spec.json. Usage: python3 -I check_spec.py <folder>. Exit 0 means it passes."""
import hashlib, json, pathlib, re, sys

d = pathlib.Path(sys.argv[1]); spec = json.loads((d / "spec.json").read_text()); inp = json.loads((d / "input.json").read_text())
errors = []
def err(m): errors.append(m)
def norm(s): return re.sub(r"\s+", " ", s).strip()

if spec.get("record_id") != inp["record_id"]: err("record_id does not match input.json")
texts = {}
keys = set()
for s in spec.get("sources", []):
    k = s.get("key", ""); keys.add(k)
    for f in ("key", "name", "description", "file", "artifact_url", "url", "version", "media_type", "sha256", "retrieved_at"):
        if not s.get(f): err(f"source {k}: missing {f}")
    if not isinstance(s.get("store_bytes"), bool): err(f"source {k}: store_bytes must be true or false")
    p = d / s.get("file", "")
    if not p.is_file(): err(f"source {k}: file not found {p}"); continue
    b = p.read_bytes()
    if hashlib.sha256(b).hexdigest() != s.get("sha256"): err(f"source {k}: sha256 does not match the file")
    texts[k] = norm(b.decode("utf-8", "replace"))
existing = {s["id"] for s in inp["existing_sources"]}
def check_ev(o, where, need_quote=True):
    ids = o.get("source_ids") or []
    if not ids: err(f"{where}: no source_ids")
    for i in ids:
        if i.startswith("@"):
            if i[1:] not in keys: err(f"{where}: unknown source key {i}")
        elif i not in existing: err(f"{where}: {i} is neither a @key nor an existing source id")
    if not o.get("source_locator"): err(f"{where}: no source_locator")
    qs = o.get("quotes") or []
    if need_quote and not qs: err(f"{where}: no quotes")
    for q in qs:
        k = (q.get("source") or "").lstrip("@")
        if k not in texts: err(f"{where}: quote source {q.get('source')} is not a fetched source"); continue
        if norm(q.get("text", "")) not in texts[k] or len(norm(q.get("text", ""))) < 8: err(f"{where}: quote not found verbatim in {k}: {q.get('text','')[:70]!r}")
p = spec.get("profile") or {}
for f in ("summary", "sections", "facts", "strengths", "limitations", "coverage", "gaps", "review"):
    if f not in p: err(f"profile: missing {f}")
if p.get("summary_source_ids") is None or not p.get("summary_source_locator"): err("profile: summary needs summary_source_ids and summary_source_locator")
if not p.get("summary_quotes"): err("profile: summary_quotes missing")
else: check_ev({"source_ids": p.get("summary_source_ids"), "source_locator": p.get("summary_source_locator"), "quotes": p["summary_quotes"]}, "profile.summary")
want = ["Model type", "Architecture", "Inputs", "Outputs", "Parameters", "Training data", "Known versions", "Training cutoff", "Context limits", "Weights licence", "Code licence", "Access"]
labels = [f.get("label") for f in p.get("facts", [])]
for w in want:
    if w not in labels: err(f"profile.facts: missing label {w!r}")
for i, f in enumerate(p.get("facts", [])):
    if f.get("status") not in ("source_checked", "unreported", "unextracted", "unavailable", "inapplicable"): err(f"fact {f.get('label')}: bad status")
    if not f.get("value"): err(f"fact {f.get('label')}: empty value")
    check_ev(f, f"fact {f.get('label')}", need_quote=f.get("status") == "source_checked")
for name in ("sections", "strengths", "limitations"):
    for i, o in enumerate(p.get(name, [])): check_ev(o, f"{name}[{i}]")
if not any(s.get("title") == "How it works" for s in p.get("sections", [])): err("sections: need one titled 'How it works'")
if p.get("diagram"):
    if not 2 <= len(p["diagram"].get("steps", [])) <= 8: err("diagram: 2 to 8 steps")
    check_ev(p["diagram"], "diagram")
if p.get("coverage") not in ("reviewed", "limited"): err("coverage must be reviewed or limited")
g = spec.get("run_guide")
if g is not None:
    for f in ("summary", "prerequisites", "steps", "outputs", "limitations", "source_ids"):
        if f not in g: err(f"run_guide: missing {f}")
    for i, st in enumerate(g.get("steps", [])):
        for f in ("title", "shell", "explanation"):
            if not st.get(f): err(f"run_guide.steps[{i}]: missing {f}")
        check_ev(st, f"run_guide.steps[{i}]")
elif not spec.get("no_run_guide_reason"): err("run_guide is null: give no_run_guide_reason")
blob = json.dumps(spec, ensure_ascii=False)
for bad in ("—", "–", "→"):
    if bad in json.dumps({k: v for k, v in spec.items() if k != "sources"} , ensure_ascii=False).replace(json.dumps([q for q in re.findall(r'"text": "(.*?)"', blob)], ensure_ascii=False), ""):
        pass
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("quotes", "summary_quotes", "shell", "sources"): continue
            walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, f"{path}[{i}]")
    elif isinstance(o, str):
        for bad, nm in (("—", "em dash"), ("–", "en dash"), ("→", "arrow")):
            if bad in o: err(f"{path}: contains an {nm}")
walk({"profile": p, "run_guide": g})
print("\n".join(errors) if errors else "OK"); sys.exit(1 if errors else 0)
