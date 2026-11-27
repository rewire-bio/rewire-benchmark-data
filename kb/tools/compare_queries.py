"""Compare kb/queries.py with the named SPARQL queries of a published graph bundle.

The inputs, for a release <id> cut from commit <sha> (for example 2026-11-26-36acdf5e0cfa, 8601f82):

  gh release download kg/<id> -D kb/build/oracle                 # bundle tarball, discrepancies.json
  mkdir -p kb/build/oracle/bundle && tar -xzf kb/build/oracle/kg-<id>.tar.gz -C kb/build/oracle/bundle
  gh release download serving/<id> -D kb/build/oracle -p 'public.omics.releases.<id>.use-cases.json.gz'
  gunzip -c kb/build/oracle/public.omics.releases.<id>.use-cases.json.gz > kb/build/oracle/use-cases.json
  mkdir -p kb/build/oracle-store && git archive <sha> data | tar -x -C kb/build/oracle-store
  (cd kb/build/oracle-store && python3 ../../migrate.py --out ../oracle.sqlite)

Then (pyoxigraph is the engine rdf-kg-mcp serves the bundle with):

  uvx --with 'pyoxigraph>=0.5.11,<0.6' python3 kb/tools/compare_queries.py

First the facts the queries read are compared one by one: the public records, rb:within, the
release graph, the unsettled findings and every attribute literal the queries use. Then each
named query is run with many parameter sets.

The bundle's files are bulk-loaded once into an on-disk store next to the bundle (store/), and
each SPARQL answer is cached as JSON (answers/), so a rerun only repeats the SQLite side. Each
query runs as rdf-kg-mcp runs it: the bundle's prefixes, the union of all graphs as the default
graph, and parameters put in the way bind_params does.

Last, search: the records it indexes and their classes are compared with the subjects and types
rdf-kg-mcp indexes, and every gold pair of scripts/kg/search-gold.rq is searched, with recall at 3
and 5 printed per bucket (about four minutes). `--only search` runs only this part.

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


def number(value: Decimal) -> Decimal:
    """One form per number, so that 0.90 and 0.9, or -0.0 and 0, compare equal."""
    return value.normalize() if value != 0 else Decimal(0)


def norm_sparql(cell):
    if cell is None:
        return None
    if "iri" in cell:
        return cell["iri"]
    if "literal" in cell:
        if cell["datatype"] in NUMERIC:
            try:
                return number(Decimal(cell["literal"]))
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
        return number(Decimal(value))
    if isinstance(value, float):
        return number(Decimal(repr(value)))
    return value


def split_concat(row: dict, columns: set) -> dict:
    return {k: (tuple(sorted(v.split(" "))) if k in columns and isinstance(v, str) and v else v) for k, v in row.items()}


LITERALS = {
    "rb:retrievedAt": "retrieved_at", "rb:reviewDate": "reviewDate", "rb:reviewedAt": "reviewedAt", "rb:date": "date",
    "mls:hasValue": "numeric_value", "rb:stratumOrder": "stratum_order", "rb:depthTier": "depth_tier", "rb:value": "value",
    "rb:metricQualifier": "metric_qualifier", "rb:doi": "doi", "schema:url": "url", "schema:version": "version",
    "rb:reviewedBy": "reviewedBy", "rb:reviewMethod": "reviewMethod", "rb:headlineMetric": "headline_metric",
    "rb:comparisonGroup": "comparison_group", "rb:reportedName": "reported_name", "rb:claimField": "field",
    "rb:origin": "origin", "rb:metric": "metric", "rb:unit": "unit", "rb:metricDirection": "metric_direction",
    "rb:relevance": "relevance", "rb:artifactSha256": "artifact_sha256", "rb:stratumLabel": "stratum_label",
    "rb:runRecipes": "run_recipes",
}


def check_inputs(store, manifest, kb) -> list[str]:
    """Compare the facts kb/queries.py loads with the graph's, one predicate at a time."""
    import pyoxigraph as ox
    graph = "https://benchmarks.rewire.it/graph/"
    pairs = lambda sparql: {(r[0].value, cell(r[1])) for r in store.query(sparql, prefixes=manifest["prefixes"], use_default_graph_as_union=True)}
    cell = lambda t: t.value if isinstance(t, ox.NamedNode) else str(norm_sparql({"literal": t.value, "datatype": t.datatype.value}))
    flat = lambda facts: {(s, str(o) if not isinstance(o, Decimal) else str(number(o))) for s, os in facts.items() for o in os}
    record = lambda s: "/" not in s[len(queries.ID):]
    checks = {
        "public records": (
            {(s, o) for s, o in pairs(f"SELECT DISTINCT ?s ?t WHERE {{ GRAPH <{graph}asserted> {{ ?s a ?t }} FILTER(STRSTARTS(STR(?s), STR(id:))) }}") if record(s)},
            None),
        "rb:within": (pairs(f"SELECT ?s ?o WHERE {{ GRAPH <{graph}inferred> {{ ?s rb:within ?o }} }}"), flat(kb.within)),
        "rb:assessedBy": (pairs("SELECT ?s ?o WHERE { ?s rb:assessedBy ?o }"), flat(kb.out.get("assessed_by", {}))),
        "rb:resultOn": (pairs("SELECT ?s ?o WHERE { ?s rb:resultOn ?o }"), flat(kb.result_on())),
        "rb:servedEvaluation": (pairs(f"SELECT ?s ?o WHERE {{ GRAPH <{graph}release> {{ ?s rb:servedEvaluation ?o }} }}"), flat(kb.served)),
        "rb:servedBaseline": (pairs(f"SELECT ?s ?o WHERE {{ GRAPH <{graph}release> {{ ?s rb:servedBaseline ?o }} }}"), flat(kb.baselines)),
        "rb:runReceipt": (pairs(f"SELECT ?s ?o WHERE {{ GRAPH <{graph}release> {{ ?s rb:runReceipt ?o }} }}"), flat(kb.receipts)),
        "unsettled findings": (pairs(f"""SELECT ?r ?f WHERE {{ GRAPH <{graph}derived> {{
              {{ ?f rb:outlierResult ?r }} UNION {{ ?f rb:consensusResult ?r }} UNION {{ ?f rb:partyResult ?r }}
              ?f rb:reviewState ?state . FILTER(?state NOT IN (<https://benchmarks.rewire.it/vocab/discrepancy-state/explained>,
              <https://benchmarks.rewire.it/vocab/discrepancy-state/confirmed-error>, <https://benchmarks.rewire.it/vocab/discrepancy-state/false-positive>)) }} }}"""),
            flat(kb.findings)),
    }
    public = checks["public records"][0]
    checks["public records"] = ({s for s, _ in public}, set(kb.kind))
    for predicate, key in LITERALS.items():
        found = pairs(f"SELECT ?s ?o WHERE {{ GRAPH <{graph}asserted> {{ ?s {predicate} ?o }} }}")
        checks[predicate] = ({(s, o) for s, o in found if record(s)}, flat(kb.out.get(key, {})))
    problems = []
    for name, (theirs, ours) in checks.items():
        status = "same" if theirs == ours else "DIFFERENT"
        print(f"{status:9} input {name}: graph {len(theirs)}, sqlite {len(ours)}")
        if theirs != ours:
            problems.append(f"{name}: only graph {sorted(theirs - ours, key=str)[:3]}, only sqlite {sorted(ours - theirs, key=str)[:3]}")
            print(f"    {problems[-1]}")
    return problems


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
    if key.startswith("rank:"):
        return queries.severity_rank(row[key[5:]])
    if key.startswith("lcase:"):
        value = row[key[6:]]
        return value.lower() if isinstance(value, str) else value
    return row[key]


def discrepancy_sets(report: list[dict], use_cases: list[str], db_path: str) -> list[tuple[str, dict]]:
    """Every severity, systems in many findings and in few, systems of settled and resolved
    findings, every discrepancy with a review history and some without, every use case, and
    parameters that should give no rows: a configuration, a previous ID, records of other kinds."""
    import sqlite3
    from collections import Counter
    sets = [("open_discrepancies", {})] + [("open_discrepancies", {"severity": s}) for s in ("high", "medium", "low", "none")]
    counts = Counter(s for f in report for s in f["systems"])
    systems = [s for s, _ in counts.most_common(8)] + [s for s, n in sorted(counts.items()) if n == 1][:4]
    systems += [s for f in report if f["review_state"] != "open" for s in f["systems"]]
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    systems += [r[0] for r in db.execute(
        "SELECT from_id FROM link WHERE relation = 'configuration_of' AND to_id = ? ORDER BY from_id LIMIT 1", (systems[0],))]
    db.close()
    systems += [use_cases[0], "no-such-record"]
    sets += [("discrepancies_for_system", {"system": s}) for s in dict.fromkeys(systems)]
    histories = [f["id"] for f in report if f["actions"]] + [f["id"] for f in report if not f["actions"]][:3]
    histories += [p for f in report for p in f["previous_ids"]][:2] + [systems[0]]
    sets += [("discrepancy_history", {"discrepancy": d}) for d in dict.fromkeys(histories)]
    sets += [("contested_results_for_use_case", {"use_case": u}) for u in use_cases + [systems[0]]]
    return sets


def parameter_sets(db_path: str, report: list[dict]) -> list[tuple[str, dict]]:
    """Realistic parameters: every use case, models with many and few results, benchmarks,
    protocols and results, and records that are not of the kind a query expects."""
    import sqlite3
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    one = lambda sql, *a: [r[0] for r in db.execute(sql, a)]
    use_cases = one("SELECT id FROM record WHERE kind = 'use_case' ORDER BY id")
    sets = discrepancy_sets(report, use_cases, db_path)
    sets += [("rank_for_use_case", {"use_case": u}) for u in use_cases]
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


def check_search_inputs(store, manifest, records) -> list[str]:
    """The records search indexes and their classes, against the subjects rdf-kg-mcp indexes
    (any label, description or declared search text outside the ontology graph) and their types."""
    import pyoxigraph as ox
    ontology = ox.NamedNode(manifest["graphs"]["ontology"])
    predicates = [*manifest["label_predicates"], "rdfs:comment", "skos:definition", "obo:IAO_0000115", "dcterms:description",
                  *manifest.get("search", {}).get("text_predicates", [])]
    prefixes = {**manifest["prefixes"], "skos": "http://www.w3.org/2004/02/skos/core#", "obo": "http://purl.obolibrary.org/obo/"}
    full = lambda name: prefixes[name.split(":", 1)[0]] + name.split(":", 1)[1]
    theirs = set()
    for predicate in dict.fromkeys(map(full, predicates)):
        for quad in store.quads_for_pattern(None, ox.NamedNode(predicate), None):
            if quad.graph_name != ontology and isinstance(quad.object, ox.Literal) and quad.object.value.strip():
                theirs.add(quad.subject.value)
    index = records.index
    ours = set(index.docs)
    problems = []
    status = "same" if theirs == ours else "DIFFERENT"
    print(f"{status:9} input search documents: graph {len(theirs)}, sqlite {len(ours)}")
    if theirs != ours:
        problems.append(f"search documents: only graph {sorted(theirs - ours)[:3]}, only sqlite {sorted(ours - theirs)[:3]}")
        print(f"    {problems[-1]}")
    rdf_type = ox.NamedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    wrong = []
    for subject in sorted(theirs & ours):
        graph_types = {records.compact(q.object.value) for q in store.quads_for_pattern(ox.NamedNode(subject), rdf_type, None)}
        if graph_types != set(index.types.get(subject, ())):
            wrong.append((subject, sorted(graph_types), index.types.get(subject)))
    status = "same" if not wrong else "DIFFERENT"
    print(f"{status:9} input search classes of {len(theirs & ours)} documents")
    if wrong:
        problems.append(f"search classes differ for {len(wrong)}: {wrong[:3]}")
        print(f"    {problems[-1]}")
    return problems


# rdf-kg-mcp itself finds 97.0% of the gold pairs of bundle 2026-11-26-36acdf5e0cfa in its top 5.
SEARCH_FLOOR = 0.95


def search_gold(store, records, misses: int = 5) -> int:
    """Run scripts/kg/search-gold.rq on the bundle and search the database for each pair, as
    rdf-kg-mcp's scripts/search_recall.py does: the expected record's class as the types filter,
    and the query's own record dropped before ranking. Prints recall at 3 and 5 by bucket."""
    fields = ("bucket", "query", "expected", "type", "self")
    pairs = []
    for solution in store.query((ROOT / "scripts" / "kg" / "search-gold.rq").read_text("utf-8"), use_default_graph_as_union=True):
        row = {f: solution[f].value for f in fields if solution[f] is not None}
        if all(row.get(k) for k in ("bucket", "query", "expected")):
            pairs.append(tuple(row.get(f) for f in fields))
    pairs = list(dict.fromkeys(pairs))
    started = time.time()
    hits: dict[str, list] = {}
    for bucket, text, expected, cls, own in pairs:
        found = records.search(text, types=[cls] if cls else None, limit=6)["results"]
        iris = [r["iri"] for r in found if r["iri"] != own]
        rank = iris.index(expected) + 1 if expected in iris[:5] else None
        h = hits.setdefault(bucket, [0, 0, 0, []])
        h[0] += 1
        h[1] += rank is not None and rank <= 3
        h[2] += rank is not None
        if rank is None and len(h[3]) < misses:
            h[3].append(f"{text!r} for {records.compact(expected)}")
    for bucket, (n, at3, at5, missed) in sorted(hits.items()):
        print(f"search    {bucket}: {n} pairs, expected record in the top 3 for {at3}, top 5 for {at5}")
        for m in missed:
            print(f"    missed {m}")
    total = sum(h[0] for h in hits.values())
    found = sum(h[2] for h in hits.values())
    print(f"search    all gold pairs: {total}; top 3 {sum(h[1] for h in hits.values())}, top 5 {found}; "
          f"{time.time() - started:.0f} s")
    if found < SEARCH_FLOOR * total:
        print(f"DIFFERENT search finds fewer than {SEARCH_FLOOR:.0%} of the gold pairs in its top 5")
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", default="kb/build/oracle/bundle")
    parser.add_argument("--db", default="kb/build/oracle.sqlite")
    parser.add_argument("--use-cases", default="kb/build/oracle/use-cases.json")
    parser.add_argument("--discrepancies", default="kb/build/oracle/discrepancies.json")
    parser.add_argument("--only", help="run only these queries (names separated by commas; search for the search checks)")
    parser.add_argument("--load-only", action="store_true")
    args = parser.parse_args()
    bundle = Path(args.bundle)
    store, manifest = open_store(bundle)
    if args.load_only:
        return
    kb = queries.KB(args.db, use_cases=args.use_cases, discrepancies=args.discrepancies)
    failures = len(check_inputs(store, manifest, kb))
    summary: dict[str, list] = {}
    for name, params in parameter_sets(args.db, kb.report):
        if args.only and name not in args.only.split(","):
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
    if not args.only or "search" in args.only.split(","):
        records = queries.Records(args.db, discrepancies=args.discrepancies)
        failures += len(check_search_inputs(store, manifest, records))
        failures += search_gold(store, records)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
