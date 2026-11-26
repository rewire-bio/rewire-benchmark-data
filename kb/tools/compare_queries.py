"""Compare kb/queries.py with the named SPARQL queries of a published graph bundle.

Usage (pyoxigraph is the engine rdf-kg-mcp serves the bundle with):

  uvx --with 'pyoxigraph>=0.5.11,<0.6' python3 kb/tools/compare_queries.py \
      --bundle kb/build/oracle/bundle --db kb/build/oracle.sqlite \
      --use-cases kb/build/oracle/use-cases.json --discrepancies kb/build/oracle/discrepancies.json

The bundle's files are bulk-loaded once into an on-disk store next to the bundle (store/), and
each SPARQL answer is cached as JSON (answers/), so a rerun only repeats the SQLite side. Each
query runs as rdf-kg-mcp runs it: the bundle's prefixes, the union of all graphs as the default
graph, and parameters put in the way bind_params does.

Rows are compared after both sides are written in one form: IRIs in full, literals by their
lexical form (numbers compared as decimals), unbound as None. Where the query orders its rows,
the order of the ORDER BY keys must match and rows that tie on every key are compared as a set.
Lists inside a GROUP_CONCAT are compared as sets, because their item order is up to the engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "kb"))
import queries  # noqa: E402

GRAPH_FILES = (".nq", ".trig", ".nt", ".ttl", ".rdf", ".owl")
# Columns built with GROUP_CONCAT, by query.
CONCATENATED = {"rank_for_use_case": {"openFindings"}, "results_for_model": {"useCases", "openFindings"},
                "provenance": {"reviewedBy", "reviewMethod"}}


def open_store(bundle: Path):
    import pyoxigraph as ox
    manifest = json.loads((bundle / "manifest.json").read_text("utf-8"))
    path = bundle / "store"
    done = path / "LOADED"
    if done.exists():
        return ox.Store(str(path)), manifest
    started = time.time()
    store = ox.Store(str(path))
    for name, entry in manifest["files"].items():
        file = bundle / name
        if file.suffix not in GRAPH_FILES:
            continue
        fmt = {".nq": ox.RdfFormat.N_QUADS, ".trig": ox.RdfFormat.TRIG, ".nt": ox.RdfFormat.N_TRIPLES,
               ".ttl": ox.RdfFormat.TURTLE}.get(file.suffix, ox.RdfFormat.RDF_XML)
        graph = entry.get("graph")
        options = {} if fmt in (ox.RdfFormat.N_QUADS, ox.RdfFormat.TRIG) else {
            "to_graph": ox.NamedNode(graph) if graph else ox.DefaultGraph()}
        store.bulk_load(path=str(file), format=fmt, **options)
        print(f"  loaded {name}", file=sys.stderr)
    store.optimize()
    done.write_text("ok\n")
    print(f"Loaded the bundle into {path} in {time.time() - started:.0f} s", file=sys.stderr)
    return store, manifest


def sparql_answer(store, manifest, bundle: Path, name: str, params: dict) -> dict:
    """The rows of one named query, from the cache or the store."""
    key = hashlib.sha256(json.dumps([name, params], sort_keys=True).encode()).hexdigest()[:16]
    cache = bundle / "answers" / f"{name}-{key}.json"
    if cache.exists():
        return json.loads(cache.read_text("utf-8"))
    import pyoxigraph as ox
    query = next(q for q in manifest["queries"] if q["name"] == name)
    terms = {}
    for p in query.get("params", []):
        value = params.get(p["name"])
        if value is None:
            continue
        if p["type"] == "iri":
            terms[p["name"]] = str(ox.NamedNode(queries.expand(value)))
        elif p["type"] == "integer":
            terms[p["name"]] = str(int(value))
        else:
            terms[p["name"]] = str(ox.Literal(value))
    pattern = re.compile(r'"(?:[^"\\\n]|\\.)*"|<[^<>"{}|^`\\\s]*>|#[^\n]*|\$([A-Za-z_][A-Za-z0-9_]*)')
    sparql = pattern.sub(lambda m: terms.get(m.group(1), m.group(0)) if m.group(1) else m.group(0), query["sparql"])
    started = time.time()
    result = store.query(sparql, prefixes=manifest["prefixes"], use_default_graph_as_union=True)
    variables = [v.value for v in result.variables]
    rows = []
    for solution in result:
        row = {}
        for v in variables:
            term = solution[v]
            if term is None:
                row[v] = None
            elif isinstance(term, ox.NamedNode):
                row[v] = {"iri": term.value}
            elif isinstance(term, ox.Literal):
                row[v] = {"literal": term.value, "datatype": term.datatype.value}
            else:
                row[v] = {"other": str(term)}
        rows.append(row)
    answer = {"variables": variables, "rows": rows, "seconds": round(time.time() - started, 2)}
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(answer, ensure_ascii=False), "utf-8")
    return answer


NUMERIC = {"http://www.w3.org/2001/XMLSchema#" + t for t in ("decimal", "integer", "double", "float", "long", "int")}


def norm_sparql(cell):
    if cell is None:
        return None
    if "iri" in cell:
        return cell["iri"]
    if "literal" in cell:
        if cell["datatype"] in NUMERIC:
            try:
                return Decimal(cell["literal"]).normalize()
            except InvalidOperation:
                return cell["literal"]
        if cell["datatype"].endswith("#boolean"):
            return cell["literal"] == "true"
        return cell["literal"]
    return cell["other"]


def norm_sqlite(value):
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, (int, Decimal)):
        return Decimal(value).normalize()
    if isinstance(value, float):
        return Decimal(repr(value)).normalize()
    return value


def split_concat(row: dict, columns: set) -> dict:
    return {k: (tuple(sorted(v.split(" "))) if k in columns and isinstance(v, str) and v else v) for k, v in row.items()}


def compare(name: str, params: dict, answer: dict, mine: list[dict]) -> list[str]:
    columns = answer["variables"]
    spec = queries.QUERIES[name]
    problems = []
    if mine and list(mine[0]) != columns:
        problems.append(f"columns differ: {list(mine[0])} vs {columns}")
    concat = CONCATENATED.get(name, set())
    theirs = [split_concat({c: norm_sparql(r.get(c)) for c in columns}, concat) for r in answer["rows"]]
    ours = [split_concat({c: norm_sqlite(r.get(c)) for c in columns}, concat) for r in mine]
    as_key = lambda row: json.dumps([str(row[c]) for c in columns])
    if sorted(map(as_key, theirs)) != sorted(map(as_key, ours)):
        t, o = set(map(as_key, theirs)), set(map(as_key, ours))
        problems.append(f"rows differ: graph {len(theirs)}, sqlite {len(ours)}; only graph {len(t - o)}, only sqlite {len(o - t)}")
        left = [json.loads(k) for k in sorted(t - o)]
        right = [json.loads(k) for k in sorted(o - t)]
        for row in left[:4]:
            if right:
                nearest = max(right, key=lambda other: sum(a == b for a, b in zip(row, other)))
                differing = {c: (a, b) for c, a, b in zip(columns, row, nearest) if a != b}
                problems.append(f"  graph row {row[:2]}: differs from the nearest sqlite row in {differing}")
            else:
                problems.append(f"  only graph:  {row}")
        for row in right[:4] if not left else []:
            problems.append(f"  only sqlite: {row}")
        return problems
    order = spec.get("order_keys")
    if order:
        key_of = lambda row: json.dumps([str(order_key(row, k)) for k in order])
        if [key_of(r) for r in theirs] != [key_of(r) for r in ours]:
            problems.append("row order differs on the ORDER BY keys")
    return problems


def order_key(row: dict, key: str):
    if key.startswith("lcase:"):
        value = row[key[6:]]
        return value.lower() if isinstance(value, str) else value
    return row[key]


def parameter_sets(db_path: str) -> list[tuple[str, dict]]:
    """Realistic parameters: every use case, models with many and few results, benchmarks,
    protocols and results, and records that are not of the kind a query expects."""
    import sqlite3
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    one = lambda sql, *a: [r[0] for r in db.execute(sql, a)]
    use_cases = one("SELECT id FROM record WHERE kind = 'use_case' ORDER BY id")
    sets = [("rank_for_use_case", {"use_case": u}) for u in use_cases]
    sets.append(("rank_for_use_case", {"use_case": "esm2-t33-650m-ur50d"}))
    sets.append(("gaps", {}))
    for tier in (1, 2, 3):
        sets.append(("gaps", {"tier": tier}))
    for level in ("use_case", "protocol"):
        sets.append(("gaps", {"level": level}))
    for u in use_cases:
        sets.append(("gaps", {"use_case": u}))
    for u in ("use-case-brca1-brca2-germline-interpretation", "use-case-protein-variant-effect-prediction"):
        sets.append(("gaps", {"use_case": u, "level": "protocol", "tier": 1}))
        sets.append(("gaps", {"use_case": u, "level": "use_case", "tier": 2}))
    models = one("""SELECT e.system_id FROM evaluation e JOIN system s ON s.id = e.system_id GROUP BY s.root_id
                    ORDER BY count(*) DESC LIMIT 6""")
    models += one("SELECT s.root_id FROM evaluation e JOIN system s ON s.id = e.system_id GROUP BY s.root_id ORDER BY count(*) DESC LIMIT 20")
    models += one("SELECT id FROM system WHERE parent_id IS NULL AND id IN (SELECT to_id FROM link WHERE relation = 'variant_of') ORDER BY id LIMIT 5")
    models += one("SELECT id FROM record WHERE kind = 'pipeline' ORDER BY id LIMIT 3")
    models += ["esm2-t33-650m-ur50d", "catalog-model-alphagenome", "catalog-model-evo2", "use-case-splicing-follow-up"]
    for m in dict.fromkeys(models):
        sets.append(("results_for_model", {"model": m}))
    recipes = one("SELECT id FROM assessment WHERE run_recipes IS NOT NULL ORDER BY id")
    benchmarks = one("SELECT to_id FROM link WHERE relation IN ('part_of', 'parent') GROUP BY to_id ORDER BY count(*) DESC LIMIT 4")
    for s in dict.fromkeys(recipes + benchmarks + ["rewire-mfass-v2", "esm2-t33-650m-ur50d"]):
        sets.append(("recipe_for", {"subject": s}))
    results = one("SELECT id FROM record WHERE kind = 'result' AND status = 'reproduced' ORDER BY id LIMIT 3")
    results += one("""SELECT c.target_id FROM claim c JOIN record r ON r.id = c.id WHERE r.kind = 'claim'
                      AND c.target_id IN (SELECT id FROM observation) ORDER BY c.id LIMIT 4""")
    results += one("SELECT subject FROM (SELECT l.to_id AS subject FROM link l JOIN record r ON r.id = l.to_id WHERE l.relation = 'subject' AND r.kind = 'result' ORDER BY l.from_id LIMIT 30)")
    results += one("SELECT record_id FROM record_source rs JOIN record r ON r.id = rs.record_id WHERE r.kind = 'result' GROUP BY record_id HAVING count(*) > 1 ORDER BY record_id LIMIT 10")
    results += one("SELECT o.id FROM observation o JOIN record r ON r.id = o.evaluation_id WHERE r.extra LIKE '%reviewed_at%' ORDER BY o.id LIMIT 5")
    results += one("SELECT id FROM record WHERE kind = 'result' AND status = 'source_checked' ORDER BY id LIMIT 3")
    results += one("SELECT id FROM record WHERE kind = 'result' AND status = 'superseded' ORDER BY id LIMIT 2")
    results += ["rewire-result-pangolin-maskfalse-auroc", "esm2-t33-650m-ur50d"]
    for r in dict.fromkeys(results):
        sets.append(("provenance", {"result": r}))
    db.close()
    return sets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", default="kb/build/oracle/bundle")
    parser.add_argument("--db", default="kb/build/oracle.sqlite")
    parser.add_argument("--use-cases", default="kb/build/oracle/use-cases.json")
    parser.add_argument("--discrepancies", default="kb/build/oracle/discrepancies.json")
    parser.add_argument("--only", help="run only this query")
    parser.add_argument("--load-only", action="store_true")
    args = parser.parse_args()
    bundle = Path(args.bundle)
    store, manifest = open_store(bundle)
    if args.load_only:
        return
    kb = queries.KB(args.db, use_cases=args.use_cases, discrepancies=args.discrepancies)
    failures = 0
    summary: dict[str, list] = {}
    for name, params in parameter_sets(args.db):
        if args.only and name != args.only:
            continue
        answer = sparql_answer(store, manifest, bundle, name, params)
        started = time.time()
        mine = kb.run(name, **params)
        seconds = time.time() - started
        problems = compare(name, params, answer, mine)
        summary.setdefault(name, []).append((not problems, len(answer["rows"]), answer["seconds"], seconds))
        status = "same" if not problems else "DIFFERENT"
        print(f"{status:9} {name} {json.dumps(params)}: {len(answer['rows'])} rows (graph {answer['seconds']} s, sqlite {seconds:.2f} s)")
        for p in problems:
            print(f"    {p}")
        failures += bool(problems)
    print()
    for name, runs in summary.items():
        same = sum(r[0] for r in runs)
        print(f"{name}: {same} of {len(runs)} parameter sets equal; rows {sum(r[1] for r in runs)}; "
              f"graph {sum(r[2] for r in runs):.1f} s, sqlite {sum(r[3] for r in runs):.1f} s in total")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
