"""The named graph queries for the product questions, answered from kb.sqlite.

Usage:
  python3 kb/queries.py --list
  python3 kb/queries.py <query name> [--param name=value ...] [--db kb/build/kb.sqlite]
                        [--use-cases FILE] [--discrepancies FILE] [--format json|table]
  python3 kb/queries.py search|describe_resource|dataset_info [--param name=value ...]
                        [--db kb/build/kb.sqlite] [--discrepancies FILE]

Each named query of the graph bundle (scripts/kg/build.py NAMED_QUERIES: the four discrepancy
queries and the five of scripts/kg/product_queries.py) has a function here with the same
parameters, returning rows as dicts with the columns the SPARQL query selects, in the same order.
The comparison with the graph is kb/tools/compare_queries.py.

Records holds the three rdf-kg-mcp tools the agents call besides the queries: search (ranked as
rdf-kg-mcp ranks, see kb/search.py), describe_resource (one record with its links out and in, by
name) and dataset_info. They print one JSON object rather than rows.

The graph the SPARQL queries read is replaced by the same facts taken from the database:

  public records  As in kb/discrepancies.py: the graph holds only public records.
  attributes      As the exporter writes them (scripts/kg/export.ts), and only for the kinds the
                  attribute registry declares them for (DECLARED).
  within          The transitive closure of part_of and parent links, the one inferred fact read.
  release         What the release serves (scripts/kg/release_graph.py): from the release's
                  use-cases.json, the evaluations behind each active direct or proxy judgement
                  and each use case's baseline methods; from the records, the run receipts.
                  The default file is the one `npm run omics:release` writes for the release in
                  public/omics/manifest.json; a published release has it as the asset
                  public.omics.releases.<id>.use-cases.json.gz of serving/<id>. Without one
                  nothing is served and only run receipts are known, as in a bundle built before
                  a release is cut: rank_for_use_case then returns no rows.
  derived         The discrepancy queries read discrepancies.json as the derived graph holds it.
  findings        The unsettled discrepancies each result takes part in, from discrepancies.json
                  (kb/discrepancies.py writes it). Without --discrepancies they are found from the
                  database first, which adds about ten seconds.

Values: IRIs in full, text and dates by their lexical form, numbers from a record as Decimal,
counts and ranks as int, flags as bool, an unbound column as None. A column built with
GROUP_CONCAT lists its items sorted, separated by spaces, and is None when there are none, as
the graph store gives it.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discrepancies import canonical_decimal, concept, iri as encoded_iri, js_string  # noqa: E402
from migrate import COLUMNS, TABLE_OF  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ID = "https://benchmarks.rewire.it/id/"
PREFIXES = {
    "id": ID, "rb": "https://benchmarks.rewire.it/vocab#", "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "dcterms": "http://purl.org/dc/terms/", "schema": "https://schema.org/",
}
CHECKED = (concept("status", "source_checked"), concept("status", "reproduced"))
DIRECT, PROXY = concept("relevance", "direct"), concept("relevance", "proxy")
HIGHER, LOWER = concept("direction", "higher"), concept("direction", "lower")
PERCENT = concept("unit", "percent")
INDEPENDENT = concept("origin", "independent_paper")
SETTLED = {"explained", "confirmed-error", "false-positive"}

# Attributes the queries read: how the exporter writes each, and the record kinds the attribute
# registry (shared/omics/attribute-registry.ts) declares it for. An attribute on any other kind is
# not in the graph.
DECLARED = {
    "comparison_group": ("text", {"claim"}),
    "stratum_order": ("integer", {"claim"}),
    "stratum_label": ("text", {"claim"}),
    "headline_metric": ("concept:metric", {"claim"}),
    "relevance": ("concept:relevance", {"claim"}),
    "field": ("text", {"claim"}),
    "value": ("text", {"claim", "result"}),
    "date": ("date", {"claim"}),
    "run_recipes": ("json", {"benchmark", "protocol"}),
    "depth_tier": ("integer", {"benchmark", "method", "model", "use_case"}),
    "reported_name": ("text", {"configuration", "dataset", "method", "model", "pipeline", "service"}),
    "numeric_value": ("decimal", {"claim", "result"}),
    "metric": ("concept:metric", {"claim", "protocol", "result", "task"}),
    "metric_qualifier": ("text", {"protocol", "result", "task"}),
    "unit": ("concept:unit", {"claim", "protocol", "result"}),
    "metric_direction": ("concept:direction", {"claim", "protocol", "result", "task"}),
    "origin": ("concept:origin", {"evaluation"}),
    "source_locator": ("text", {"baseline", "benchmark", "claim", "configuration", "dataset", "dataset_subset", "evaluation",
                                "method", "model", "pipeline", "protocol", "result", "source", "task"}),
    "doi": ("text", {"source"}),
    "url": ("iri", {"dataset_subset", "source"}),
    "retrieved_at": ("datetime", {"source"}),
    "artifact_sha256": ("text", {"source"}),
    "version": ("text", {"benchmark", "configuration", "dataset", "dataset_subset", "evaluation", "evaluator", "method",
                         "model", "pipeline", "protocol", "service", "source", "task"}),
}
# The review object of any record (data/ontology/mapping.json "review").
REVIEW = {"method": ("reviewMethod", "concept:review-method"), "reviewer": ("reviewedBy", "concept:agent"),
          "actor": ("reviewedBy", "concept:agent"), "date": ("reviewDate", "date"), "reviewed_at": ("reviewedAt", "datetime")}
LINKS = ("system", "assessment", "evaluation", "subject", "configuration_of", "family", "variant_of", "part_of", "parent",
         "companion_of", "assessed_by", "source")
PARENT = ("configuration_of", "family", "variant_of")


# Characters encodeURI leaves alone. A string of only these, with no escape, is its own IRI.
PLAIN = re.compile(r"^[A-Za-z0-9;,/?:@&=+$\-_.!~*'()#]*$")


@lru_cache(maxsize=None)
def iri(value: str) -> str:
    """An IRI as the exporter writes it (encodeURI of decodeURI)."""
    return value if PLAIN.match(value) else encoded_iri(value)


def node(record_id: str) -> str:
    return iri(ID + record_id)


def expand(value: str) -> str:
    """A full IRI, <IRI>, a prefixed name, or a bare record ID, as a full IRI."""
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    if re.match(r"^https?://", value):
        return value
    prefix, _, rest = value.partition(":")
    if rest and prefix in PREFIXES:
        return PREFIXES[prefix] + rest
    return node(value)


def canonical_json(value) -> str:
    """JSON with object keys sorted and JavaScript number formatting (canonicalJson in export.ts)."""
    if isinstance(value, list):
        return "[" + ",".join(canonical_json(v) for v in value) + "]"
    if isinstance(value, dict):
        keys = sorted(value, key=lambda k: k.encode("utf-16-be"))
        return "{" + ",".join(f"{json.dumps(k, ensure_ascii=False)}:{canonical_json(value[k])}" for k in keys) + "}"
    if isinstance(value, bool) or value is None:
        return json.dumps(value)
    if isinstance(value, float):
        return js_string(value)
    return json.dumps(value, ensure_ascii=False)


DATETIME = re.compile(r"^(-?\d{4,}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?(Z|[+-]\d\d:\d\d)?$")


def xsd_datetime(text: str) -> str:
    """The canonical form the graph store gives a date-time: no trailing zeros in the seconds
    and Z for a zero offset. Text that is not a date-time is kept as it is."""
    match = DATETIME.match(text)
    if not match:
        return text
    stamp, fraction, zone = match.groups()
    fraction = (fraction or "").rstrip("0")
    zone = "Z" if zone in ("Z", "+00:00", "-00:00") else zone or ""
    return f"{stamp}{'.' + fraction if fraction else ''}{zone}"


def literals(value, how: str) -> list:
    """The objects the exporter writes for one attribute value: IRIs and lexical forms, a Decimal
    for a valid decimal, an int for a valid integer."""
    if how == "json":
        return [canonical_json(value)]
    out = []
    for item in value if isinstance(value, list) else [value]:
        if item is None or isinstance(item, (dict, list)):
            continue
        text = js_string(item)
        if how.startswith("concept:"):
            out.append(iri(concept(how.split(":", 1)[1], text)))
        elif how == "iri":
            if re.match(r"^https?://", text):
                out.append(iri(text))
        elif how == "decimal":
            decimal = canonical_decimal(text)
            out.append(Decimal(decimal) if decimal is not None else text)
        elif how == "integer":
            out.append(int(text) if re.fullmatch(r"[-+]?\d+", text) else text)
        elif how == "datetime" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            out.append(xsd_datetime(text))
        else:
            out.append(text)
    return out


def severity_rank(severity: str) -> int:
    """The ?rank the discrepancy queries order by: high, medium, then anything else."""
    return {"high": 0, "medium": 1}.get(severity, 2)


def concat(items) -> str | None:
    """GROUP_CONCAT(DISTINCT ...; separator=" "), with the items sorted."""
    return " ".join(sorted(set(items))) or None


def load_report(path: str | None, db_path: str) -> dict:
    """discrepancies.json, or the same found from the database when no file is given."""
    if path:
        return json.loads(Path(path).read_text("utf-8"))
    import discrepancies as d
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    graph = d.Graph(db)
    db.close()
    return {"release_id": None, "discrepancies": d.derive(
        graph, d.default_directions(ROOT / "data" / "vocab" / "metric.ttl"), d.load_rules(ROOT)).report}


def public_ids(rows, sources, links) -> set[str]:
    """The records the graph holds: not excluded or disputed, a result only once checked, and
    nothing that cites or links to a record left out. rows are (id, kind, name, status)."""
    refs: dict[str, set[str]] = defaultdict(set)
    for record_id, source_id in sources:
        refs[source_id].add(record_id)
    for from_id, _, to_id in links:
        refs[to_id].add(from_id)
    blocked = {r for r, kind, _, status in rows if status in ("excluded", "disputed")
               or (kind == "result" and status not in ("source_checked", "reproduced", "superseded"))}
    queue = list(blocked)
    while queue:
        for dependent in refs.get(queue.pop(), ()):
            if dependent not in blocked:
                blocked.add(dependent)
                queue.append(dependent)
    return {r for r, *_ in rows} - blocked


class KB:
    """The facts the named queries read, loaded once from kb.sqlite and the release files."""

    def __init__(self, db_path: str = "kb/build/kb.sqlite", use_cases: str | None = None,
                 discrepancies: str | None = None):
        db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        rows = db.execute("SELECT id, kind, name, status FROM record").fetchall()
        sources = db.execute("SELECT record_id, source_id FROM record_source ORDER BY record_id, position").fetchall()
        links = db.execute("SELECT from_id, relation, to_id FROM link ORDER BY from_id, position").fetchall()
        public = public_ids(rows, sources, links)

        self.kind: dict[str, str] = {}
        self.label: dict[str, str] = {}
        self.status: dict[str, str] = {}
        out: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
        for record_id, kind, name, status in rows:
            if record_id in public:
                s = node(record_id)
                self.kind[s] = kind
                if isinstance(name, str) and name != "":
                    self.label[s] = name
                if status:
                    self.status[s] = iri(concept("status", status))
        for record_id, source_id in sources:
            if record_id in public:
                out["source"][node(record_id)].add(node(source_id))
        for from_id, relation, to_id in links:
            if from_id in public and relation in LINKS:
                out[relation][node(from_id)].add(node(to_id))
        for table, columns in COLUMNS.items():
            typed = [(a, c) for a, c, _ in columns if a in DECLARED]
            kinds = [k for k, t in TABLE_OF.items() if t == table]
            select = ", ".join(["t.id", "r.kind", "r.extra", *(f"t.{c}" for _, c in typed)])
            query = f"SELECT {select} FROM {table} t JOIN record r ON r.id = t.id WHERE r.kind IN ({', '.join('?' * len(kinds))})"
            for record_id, kind, extra, *values in db.execute(query, kinds):
                if record_id not in public:
                    continue
                attributes = json.loads(extra)
                for (attribute, _), value in zip(typed, values):
                    if value is not None:
                        attributes[attribute] = json.loads(value[1:]) if isinstance(value, str) and value.startswith("\x00") else value
                s = node(record_id)
                for attribute, value in attributes.items():
                    how, kinds_declared = DECLARED.get(attribute, (None, ()))
                    if kind in kinds_declared:
                        out[attribute][s].update(literals(value, how))
                review = attributes.get("review")
                if isinstance(review, dict):
                    for key, (predicate, how) in REVIEW.items():
                        if key in review:
                            out[predicate][s].update(literals(review[key], how))
                if kind == "claim" and str(attributes.get("field", "")).startswith("links:assessed_by:"):
                    out["judgement"][s].add(True)
        db.close()
        self.out = {p: {s: sorted(o, key=str) for s, o in by.items()} for p, by in out.items()}
        self.inv: dict[str, dict[str, list]] = {}
        for p in ("subject", "evaluation", "system", "assessment", *PARENT):
            inverse = defaultdict(list)
            for s, objects in self.out.get(p, {}).items():
                for o in objects:
                    inverse[o].append(s)
            self.inv[p] = {o: sorted(subjects) for o, subjects in inverse.items()}
        self.within = self._within()
        self._release(use_cases)
        self._findings(discrepancies, db_path)

    def objects(self, s: str | None, p: str) -> list:
        return self.out.get(p, {}).get(s, [])

    def first(self, s: str | None, p: str):
        found = self.objects(s, p)
        return found[0] if found else None

    def subjects(self, p: str, o: str) -> list:
        return self.inv[p].get(o, [])

    def checked(self, s: str) -> bool:
        return self.status.get(s) in CHECKED

    def _within(self) -> dict[str, set]:
        step: dict[str, set] = defaultdict(set)
        for relation in ("part_of", "parent"):
            for s, objects in self.out.get(relation, {}).items():
                step[s].update(objects)
        closure = {}
        for start in step:
            seen, stack = set(), list(step[start])
            while stack:
                o = stack.pop()
                if o not in seen:
                    seen.add(o)
                    stack.extend(step.get(o, ()))
            closure[start] = seen
        return closure

    def _release(self, path: str | None) -> None:
        """The release graph of scripts/kg/release_graph.py. Entries that name a record the graph
        does not hold are skipped and counted; release_graph.py refuses the whole file instead."""
        self.served: dict[str, set] = defaultdict(set)
        self.served_of: dict[str, set] = defaultdict(set)
        self.baselines: dict[str, set] = defaultdict(set)
        self.receipts: dict[str, set] = defaultdict(set)
        self.release_id = None
        self.skipped = 0
        for record, recipes in self.out.get("run_recipes", {}).items():
            for literal in recipes:
                for recipe in json.loads(literal):
                    for step in recipe.get("instructions", []):
                        receipt = step.get("validation_receipt") or {}
                        source = node(str(receipt.get("source_id", "")))
                        if step.get("status") == "executed" and receipt.get("scope") == "full_protocol" and self.kind.get(source) == "source":
                            self.receipts[record].add(source)
        self.receipt_sources = set().union(*self.receipts.values()) if self.receipts else set()
        if not path:
            return
        artifact = json.loads(Path(path).read_text("utf-8"))
        self.release_id = artifact.get("release_id")
        for mapping in artifact.get("mappings", []):
            if mapping.get("lifecycle") != "active" or mapping.get("relevance") not in ("direct", "proxy"):
                continue
            judgement = node(mapping["id"])
            if not self.first(judgement, "judgement"):
                self.skipped += 1
                continue
            for evaluation_id in mapping.get("evaluation_ids", []):
                evaluation = node(evaluation_id)
                if self.kind.get(evaluation) == "evaluation":
                    self.served[judgement].add(evaluation)
                else:
                    self.skipped += 1
        for use_case in artifact.get("use_cases", []):
            uc = node(use_case["id"])
            method_ids = (use_case.get("baseline") or {}).get("method_ids", [])
            if method_ids and self.kind.get(uc) != "use_case":
                self.skipped += 1
                continue
            for method_id in method_ids:
                if node(method_id) in self.kind:
                    self.baselines[uc].add(node(method_id))
                else:
                    self.skipped += 1
        for judgement, evaluations in self.served.items():
            for evaluation in evaluations:
                self.served_of[evaluation].add(judgement)

    def _findings(self, path: str | None, db_path: str) -> None:
        report = load_report(path, db_path)["discrepancies"]
        self.report = report
        self.findings: dict[str, set] = defaultdict(set)
        for finding in report:
            if finding["review_state"] in SETTLED:
                continue
            for key in ("outlier_results", "consensus_results", "party_results"):
                for result in finding.get(key) or []:
                    self.findings[node(result)].add(node(finding["id"]))

    # ---- shared pieces of the queries ----

    def receipt(self, result: str) -> str | None:
        """The lowest run-receipt source the result or its evaluation cites."""
        cited = set(self.objects(result, "source"))
        for evaluation in self.objects(result, "evaluation"):
            cited.update(self.objects(evaluation, "source"))
        found = sorted(cited & self.receipt_sources)
        return found[0] if found else None

    def parent(self, config: str) -> str | None:
        found = [p for relation in PARENT for p in self.objects(config, relation)]
        return max(found) if found else None

    def open_findings(self, result: str) -> str | None:
        return concat(self.findings.get(result, ()))

    def served_judgements(self, use_case: str) -> list[dict]:
        """One row per served judgement of the use case and value of its optional fields."""
        rows = []
        for j in self.subjects("subject", use_case):
            if not self.served.get(j):
                continue
            for rel in self.objects(j, "relevance"):
                groups = self.objects(j, "comparison_group") or [None]
                for cg in groups:
                    combos = [(None, None, None)]
                    if cg is not None:
                        combos = [(o, l, h) for o in self.objects(j, "stratum_order") or [None]
                                  for l in self.objects(j, "stratum_label") or [None]
                                  for h in self.objects(j, "headline_metric") or [None]]
                    for order, label, head in combos:
                        g = cg if cg is not None else j[len(ID):] if j.startswith(ID) else ""
                        key = f"{1000000 + (order if isinstance(order, int) else 0)}|{j}"
                        rows.append({"j": j, "rel": rel, "cg": cg, "ord": order, "lab": label, "hm": head, "g": g, "key": key})
        return rows

    def comparisons(self, use_case: str) -> list[dict]:
        """COMPARISONS: one row per comparison with its first judgement, layout, relevance and metric."""
        groups: dict[str, list] = defaultdict(list)
        for row in self.served_judgements(use_case):
            groups[row["g"]].append(row)
        out = []
        for g, members in groups.items():
            first_key = min(r["key"] for r in members)
            first_head = min(r["key"] if r["hm"] is not None else "~" for r in members)
            j0 = first_key.split("|", 1)[1]
            strata = len({r["j"] for r in members}) > 1 or sum(r["lab"] is not None for r in members) > 0
            direct = min(1 if r["rel"] == DIRECT else 0 for r in members)
            head_judgement = first_head.split("|", 1)[1] if "|" in first_head else ""
            chosen = self.objects(head_judgement, "headline_metric") if use_case in self.objects(head_judgement, "subject") else []
            heads = chosen or [self.common_metric(members)]
            for head in heads:
                out.append({"g": g, "j0": j0, "strata": strata, "direct": direct, "head": head})
        return out

    def common_metric(self, members: list[dict]) -> str | None:
        """The metric most reviewed results of the comparison report (the lowest IRI on a tie)."""
        counts: dict[str, set] = defaultdict(set)
        for row in members:
            for evaluation in self.served[row["j"]]:
                for result in self.subjects("evaluation", evaluation):
                    if self.checked(result):
                        for metric in self.objects(result, "metric"):
                            counts[metric].add(result)
        if not counts:
            return None
        most = max(len(v) for v in counts.values())
        return min(m for m, v in counts.items() if len(v) == most)

    def ranked_rows(self, use_case: str) -> list[dict]:
        """ROWS: the ranked column of every comparison, one valued result per configuration."""
        out = []
        for comp in self.comparisons(use_case):
            j0, head, strata = comp["j0"], comp["head"], comp["strata"]
            if head is None:
                continue
            qualifier = None
            lowered = []
            for e in self.served[j0]:
                for r in self.subjects("evaluation", e):
                    if self.checked(r) and head in self.objects(r, "metric"):
                        lowered += [q.lower() for q in self.objects(r, "metric_qualifier")] or [""]
            if lowered:
                qualifier = min(lowered)
            column: dict[str, list] = defaultdict(list)
            for e in self.served[j0]:
                for c in self.objects(e, "system"):
                    if self.kind.get(c) != "configuration":
                        continue
                    for r in self.subjects("evaluation", e):
                        if not (self.checked(r) and head in self.objects(r, "metric")):
                            continue
                        quals = self.objects(r, "metric_qualifier") or [None]
                        if strata or (qualifier is not None and any((q.lower() if q is not None else "") == qualifier for q in quals)):
                            column[c].append((e, r))
            for c, cells in column.items():
                last = max(e for e, _ in cells)
                first_result = min(r for e, r in cells if e == last)
                last_served = max(e for e in self.served[j0] if c in self.objects(e, "system"))
                if strata and last != last_served:
                    continue
                for v in self.objects(first_result, "numeric_value"):
                    for u in self.objects(first_result, "unit") or [None]:
                        knowns = [d for d in self.objects(first_result, "metric_direction") if d in (HIGHER, LOWER)] or [None]
                        for known in knowns:
                            if not isinstance(v, Decimal):
                                sort = None if u == PERCENT else v
                            else:
                                sort = v / 100 if u == PERCENT else v
                            out.append({"g": comp["g"], "direct": comp["direct"], "head": head, "c": c, "e": last,
                                        "r": first_result, "v": v, "u": u, "sort": sort, "known": known})
        return out

    def chosen(self, use_case: str, rows: list[dict]) -> tuple[str, str] | None:
        """CHOSEN: the comparison the use case is ranked on, and its direction."""
        baselines = self.baselines.get(use_case, set())
        stats = {}
        for row in rows:
            key = (row["g"], row["direct"])
            s = stats.setdefault(key, {"configs": set(), "stated": "", "baseline": 0})
            s["configs"].add(row["c"])
            s["stated"] = max(s["stated"], row["known"] or "")
            c = row["c"]
            if any(b == c or b in [p for rel in PARENT for p in self.objects(c, rel)] for b in baselines):
                s["baseline"] = 1
        ranked = [(-direct, -len(s["configs"]), -s["baseline"], g, s["stated"])
                  for (g, direct), s in stats.items() if len(s["configs"]) >= 2 and s["stated"]]
        if not ranked:
            return None
        best = min(ranked)
        return best[3], best[4]

    # ---- the named queries ----

    def rank_for_use_case(self, use_case: str) -> list[dict]:
        use_case = expand(use_case)
        rows = self.ranked_rows(use_case)
        chosen = self.chosen(use_case, rows)
        if chosen is None:
            return []
        g, direction = chosen
        mine = [r for r in rows if r["g"] == g]
        judgements = self.served_judgements(use_case)
        relevant = len({r["g"] for r in judgements})
        evaluated: dict[str, set] = defaultdict(set)
        for row in judgements:
            for e in self.served[row["j"]]:
                for c in self.objects(e, "system"):
                    if self.kind.get(c) == "configuration":
                        evaluated[self.parent(c) or c].add(row["g"])
        ranked: dict[tuple, dict] = {}
        for row in mine:
            better = 0
            unknown = row["sort"] is None or isinstance(row["sort"], str)
            for other in mine:
                a, b = other["sort"], row["sort"]
                if not isinstance(a, Decimal) or not isinstance(b, Decimal):
                    unknown = True
                    continue
                better += (a < b) if direction == LOWER else (a > b)
            if unknown:
                continue
            c, e, r = row["c"], row["e"], row["r"]
            label = self.label.get(c)
            if label is None:
                continue
            tool = self.parent(c) or c
            receipt = self.receipt(r)
            for protocol in self.objects(e, "assessment"):
                for reported in self.objects(c, "reported_name") or [None]:
                    for origin in self.objects(e, "origin") or [None]:
                        out = {
                            "rank": better + 1, "configuration": c, "name": reported if reported is not None else label,
                            "tool": tool, "value": row["v"], "unit": row["u"], "result": r, "evaluation": e,
                            "origin": origin, "independent": origin == INDEPENDENT,
                            "reviewStatus": "reproduced" if receipt else "source_checked", "receipt": receipt,
                            "evaluated": len(evaluated.get(tool, ())), "relevant": relevant,
                            "openFindings": self.open_findings(r), "comparison": g, "protocol": protocol,
                            "relevance": DIRECT if row["direct"] == 1 else PROXY, "metric": row["head"], "direction": direction,
                        }
                        ranked[tuple(map(str, out.values()))] = out
        return sorted(ranked.values(), key=lambda o: (o["rank"], o["name"].lower(), o["configuration"]))

    def evidence(self, use_case: str | None, protocol_level: bool) -> dict:
        """Counts behind the gaps: served evaluations, studies, and whether any is independent or
        directly relevant, per use case or per use case and protocol."""
        found: dict[tuple, dict] = {}
        for j, evaluations in self.served.items():
            for uc in self.objects(j, "subject"):
                if use_case is not None and uc != use_case:
                    continue
                for rel in self.objects(j, "relevance"):
                    for e in evaluations:
                        keys = [(uc, p) for p in self.objects(e, "assessment")] if protocol_level else [(uc,)]
                        independent = 1 if INDEPENDENT in self.objects(e, "origin") else 0
                        studies = set()
                        for r in self.subjects("evaluation", e):
                            if not self.checked(r):
                                continue
                            for src in self.objects(r, "source"):
                                studies.update(self.study(src))
                        for key in keys:
                            s = found.setdefault(key, {"e": set(), "studies": set(), "independent": 0, "direct": 0})
                            s["e"].add(e)
                            s["studies"] |= studies
                            s["independent"] = max(s["independent"], independent)
                            s["direct"] = max(s["direct"], 1 if rel == DIRECT else 0)
        return found

    def study(self, source: str) -> set:
        dois = self.objects(source, "doi")
        papers = self.objects(source, "companion_of")
        out = set()
        for doi in dois or [None]:
            for paper in papers or [None]:
                for paper_doi in (self.objects(paper, "doi") if paper else []) or [None]:
                    out.add(doi.lower() if doi is not None else paper_doi.lower() if paper_doi is not None
                            else paper if paper is not None else source)
        return out

    def gaps(self, use_case: str | None = None, tier: int | str | None = None, level: str | None = None) -> list[dict]:
        use_case = expand(use_case) if use_case else None
        tier = int(tier) if tier is not None else None
        by_use_case = self.evidence(use_case, False)
        by_protocol = self.evidence(use_case, True)
        rows = []
        for uc in sorted(s for s, k in self.kind.items() if k == "use_case"):
            name = self.label.get(uc)
            if name is None or (use_case is not None and uc != use_case):
                continue
            for depth in self.objects(uc, "depth_tier") or [None]:
                if tier is not None and (depth if depth is not None else -1) != tier:
                    continue
                if level in (None, "use_case"):
                    s = by_use_case.get((uc,))
                    evaluations, studies = (len(s["e"]), len(s["studies"])) if s else (0, 0)
                    for gap in ("no_direct_evidence", "single_source", "no_independent_result"):
                        if ((gap == "no_direct_evidence" and (s["direct"] if s else 0) == 0)
                                or (gap == "single_source" and studies == 1)
                                or (gap == "no_independent_result" and evaluations > 0 and s["independent"] == 0)):
                            rows.append({"useCase": uc, "useCaseName": name, "depthTier": depth, "level": "use_case",
                                         "protocol": None, "protocolName": None, "gap": gap,
                                         "evaluations": evaluations, "studies": studies})
                if level in (None, "protocol"):
                    for protocol in self.objects(uc, "assessed_by"):
                        protocol_name = self.label.get(protocol)
                        if protocol_name is None:
                            continue
                        s = by_protocol.get((uc, protocol))
                        evaluations, studies = (len(s["e"]), len(s["studies"])) if s else (0, 0)
                        for gap in ("no_served_evidence", "single_source", "no_independent_result"):
                            if ((gap == "no_served_evidence" and evaluations == 0)
                                    or (gap == "single_source" and studies == 1)
                                    or (gap == "no_independent_result" and evaluations > 0 and s["independent"] == 0)):
                                rows.append({"useCase": uc, "useCaseName": name, "depthTier": depth, "level": "protocol",
                                             "protocol": protocol, "protocolName": protocol_name, "gap": gap,
                                             "evaluations": evaluations, "studies": studies})
        rows.sort(key=lambda r: (r["level"] != "use_case", r["useCase"], r["protocol"] or "", r["gap"]))
        return rows

    def recipe_for(self, subject: str) -> list[dict]:
        subject = expand(subject)
        with_recipes = self.out.get("run_recipes", {})
        records = [subject] if subject in with_recipes else []
        records += sorted(r for r in with_recipes if subject in self.within.get(r, ()))
        records += sorted(r for r in self.within.get(subject, ()) if r in with_recipes)
        rows = []
        for record in records:
            name = self.label.get(record)
            if name is None:
                continue
            receipts = [s for s in sorted(self.receipts.get(record, ())) if s in self.label] or [None]
            for recipes in with_recipes[record]:
                for receipt in receipts:
                    extras = [(None, None, None)]
                    if receipt:
                        extras = [(u, v, d) for u in self.objects(receipt, "url") or [None]
                                  for v in self.objects(receipt, "version") or [None]
                                  for d in self.objects(receipt, "retrieved_at") or [None]]
                    for url, version, date in extras:
                        rows.append({"record": record, "recordName": name, "storeRecipes": recipes,
                                     "fullProtocolReceipt": receipt, "receiptName": self.label.get(receipt) if receipt else None,
                                     "receiptUrl": url, "receiptRevision": version, "receiptDate": date})
        rows.sort(key=lambda r: (r["record"], r["fullProtocolReceipt"] is not None, r["fullProtocolReceipt"] or ""))
        return rows

    def results_for_model(self, model: str) -> list[dict]:
        model = expand(model)
        configurations = sorted({model, *(c for rel in PARENT for c in self.subjects(rel, model))})
        rows = {}
        for c in configurations:
            label = self.label.get(c)
            if label is None:
                continue
            for e in self.subjects("system", c):
                if not self.checked(e):
                    continue
                use_cases = concat({uc for j in self.served_of.get(e, ()) for uc in self.objects(j, "subject")})
                for protocol in self.objects(e, "assessment"):
                    for r in self.subjects("evaluation", e):
                        if not self.checked(r):
                            continue
                        receipt = self.receipt(r)
                        for metric in self.objects(r, "metric"):
                            for value in self.objects(r, "numeric_value"):
                                for reported in self.objects(c, "reported_name") or [None]:
                                    for qualifier in self.objects(r, "metric_qualifier") or [None]:
                                        for unit in self.objects(r, "unit") or [None]:
                                            for direction in self.objects(r, "metric_direction") or [None]:
                                                for origin in self.objects(e, "origin") or [None]:
                                                    row = {
                                                        "configuration": c, "name": reported if reported is not None else label,
                                                        "protocol": protocol, "protocolName": self.label.get(protocol),
                                                        "metric": metric, "metricQualifier": qualifier, "value": value,
                                                        "unit": unit, "direction": direction, "result": r, "evaluation": e,
                                                        "origin": origin, "independent": origin == INDEPENDENT,
                                                        "reviewStatus": "reproduced" if receipt else "source_checked",
                                                        "receipt": receipt, "useCases": use_cases,
                                                        "openFindings": self.open_findings(r),
                                                    }
                                                    rows[tuple(map(str, row.values()))] = row
        return sorted(rows.values(), key=lambda r: (r["protocol"], r["metric"], r["metricQualifier"] is not None,
                                                    r["metricQualifier"] or "", r["configuration"], r["result"]))

    def provenance(self, result: str) -> list[dict]:
        result = expand(result)
        if self.kind.get(result) != "result":
            return []
        empty = dict.fromkeys(["step", "record", "name", "locator", "url", "doi", "retrieved", "sha256", "status",
                               "reviewedBy", "reviewMethod", "date", "field", "value"])
        rows = []
        for record in self.objects(result, "source"):
            for locator in self.objects(result, "source_locator"):
                if record not in self.label or record not in self.status:
                    continue
                for url in self.objects(record, "url") or [None]:
                    for doi in self.objects(record, "doi") or [None]:
                        for retrieved in self.objects(record, "retrieved_at") or [None]:
                            for sha in self.objects(record, "artifact_sha256") or [None]:
                                rows.append({**empty, "step": "source", "record": record, "name": self.label[record],
                                             "locator": locator, "url": url, "doi": doi, "retrieved": retrieved,
                                             "sha256": sha, "status": self.status[record]})
        for record in sorted({result, *self.objects(result, "evaluation")}):
            if record not in self.label or record not in self.status:
                continue
            by = concat(self.objects(record, "reviewedBy"))
            method = concat(self.objects(record, "reviewMethod"))
            dates = {d for d in self.objects(record, "reviewDate")} or {None}
            at = self.objects(record, "reviewedAt") or [None]
            for date in sorted({d if d is not None else a for d in dates for a in at}, key=lambda d: (d is not None, d or "")):
                rows.append({**empty, "step": "review", "record": record, "name": self.label[record],
                             "status": self.status[record], "reviewedBy": by, "reviewMethod": method, "date": date})
        for record in self.subjects("subject", result):
            if record not in self.label or record not in self.status:
                continue
            for field in self.objects(record, "field"):
                for value in self.objects(record, "value") or [None]:
                    for locator in self.objects(record, "source_locator") or [None]:
                        for review_date in self.objects(record, "reviewDate") or [None]:
                            for action_date in self.objects(record, "date") or [None]:
                                rows.append({**empty, "step": "claim", "record": record, "name": self.label[record],
                                             "status": self.status[record], "field": field, "value": value, "locator": locator,
                                             "date": action_date if action_date is not None else review_date})
        step_rank = {"source": 0, "review": 1, "claim": 2}
        rows.sort(key=lambda r: (step_rank[r["step"]], r["date"] is not None, r["date"] or "", r["record"]))
        return rows

    # ---- the discrepancy queries (scripts/kg/build.py NAMED_QUERIES), from discrepancies.json ----

    def finding_rows(self, finding: dict) -> dict:
        """The derived-graph facts of one finding that the queries select."""
        return {"discrepancy": node(finding["id"]), "severity": finding["severity"],
                "state": iri(concept("discrepancy-state", finding["review_state"])),
                "rule": iri(concept("discrepancy-rule", finding["rule"])) if finding["rule"] else None,
                "scope": finding["scope"], "summary": finding["summary"]}

    def open_discrepancies(self, severity: str | None = None) -> list[dict]:
        rows = []
        for finding in self.report:
            # A resolved finding has no rule or scope, which the query requires.
            if finding["review_state"] in SETTLED or finding["rule"] is None or finding["scope"] is None:
                continue
            if severity is not None and finding["severity"] != severity:
                continue
            f = self.finding_rows(finding)
            rows.append({k: f[k] for k in ("discrepancy", "severity", "state", "rule", "scope", "summary")})
        return sorted(rows, key=lambda r: (severity_rank(r["severity"]), r["discrepancy"]))

    def discrepancies_for_system(self, system: str) -> list[dict]:
        system = expand(system)
        rows = []
        for finding in self.report:
            systems = {node(s) for s in finding["systems"]}
            if system not in systems:
                continue
            f = self.finding_rows(finding)
            for other in sorted(systems - {system}):
                rows.append({"discrepancy": f["discrepancy"], "other": other, "otherName": self.label.get(other),
                             "severity": f["severity"], "state": f["state"], "summary": f["summary"]})
        return sorted(rows, key=lambda r: (severity_rank(r["severity"]), r["discrepancy"]))

    def discrepancy_history(self, discrepancy: str) -> list[dict]:
        """Only the current ID has actions: an ID listed in previous_ids returns nothing."""
        discrepancy = expand(discrepancy)
        rows = []
        for finding in self.report:
            if node(finding["id"]) != discrepancy:
                continue
            for action in finding["actions"]:
                url = action.get("report_url") or action.get("investigation_url")
                rows.append({
                    "revision": action["revision"],
                    "actionType": iri(concept("discrepancy-action", action["action"])) if action["action"] else None,
                    "state": iri(concept("discrepancy-state", action["state"])), "date": action["date"],
                    "url": iri(url) if url else None, "nextCheck": action.get("next_check"),
                    "claim": node(action["claim_id"]),
                })
        return sorted(rows, key=lambda r: r["revision"])

    def result_on(self) -> dict[str, set]:
        """rb:resultOn: a result to the protocol, task or benchmark its evaluation was assessed on."""
        if not hasattr(self, "_result_on"):
            self._result_on = defaultdict(set)
            for result, evaluations in self.out.get("evaluation", {}).items():
                for evaluation in evaluations:
                    self._result_on[result].update(self.objects(evaluation, "assessment"))
        return self._result_on

    def contested_results_for_use_case(self, use_case: str) -> list[dict]:
        use_case = expand(use_case)
        protocols = set(self.objects(use_case, "assessed_by"))
        if not protocols:
            return []
        on = self.result_on()
        rows = {}
        for finding in self.report:
            if finding["review_state"] in SETTLED:
                continue
            f = self.finding_rows(finding)
            for role, key in (("outlier", "outlier_results"), ("consensus", "consensus_results"), ("party", "party_results")):
                for result in map(node, finding.get(key) or []):
                    if on.get(result, set()) & protocols:
                        row = {"result": result, "role": role, "discrepancy": f["discrepancy"], "severity": f["severity"],
                               "state": f["state"], "summary": f["summary"]}
                        rows[(result, role, f["discrepancy"])] = row
        return sorted(rows.values(), key=lambda r: (severity_rank(r["severity"]), r["discrepancy"], r["role"], r["result"]))

    def run(self, name: str, **params) -> list[dict]:
        spec = QUERIES[name]
        unknown = set(params) - {p["name"] for p in spec["params"]}
        if unknown:
            raise ValueError(f"unknown parameter(s) for {name}: {', '.join(sorted(unknown))}")
        missing = [p["name"] for p in spec["params"] if p.get("required") and params.get(p["name"]) is None]
        if missing:
            raise ValueError(f"parameter(s) required for {name}: {', '.join(missing)}")
        return getattr(self, name)(**{k: v for k, v in params.items() if v is not None})


LOCAL_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$|^$")


class Records:
    """The record tools the agents used from rdf-kg-mcp: search, describe_resource and
    dataset_info, answered from kb.sqlite and discrepancies.json. Nothing is loaded until a
    tool needs it; the search index is built on the first search (about five seconds)."""

    def __init__(self, db_path: str = "kb/build/kb.sqlite", discrepancies: str | None = None):
        self.db_path = db_path
        self.discrepancies_path = discrepancies
        self.db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        mapping = json.loads((ROOT / "data" / "ontology" / "mapping.json").read_text("utf-8"))
        prefixes = {**mapping["prefixes"], **PREFIXES, "skos": "http://www.w3.org/2004/02/skos/core#"}
        self.prefixes = prefixes
        self.namespaces = sorted(((ns, p) for p, ns in prefixes.items()), key=lambda x: -len(x[0]))
        self.kind_class = {kind: entry["types"][0] for kind, entry in mapping["classes"].items()}

    def compact(self, value: str) -> str:
        """A prefixed name where one fits, as rdf-kg-mcp writes IDs and classes."""
        for ns, prefix in self.namespaces:
            if value.startswith(ns) and LOCAL_NAME.match(value[len(ns):]):
                return f"{prefix}:{value[len(ns):]}"
        return f"<{value}>"

    def full(self, value: str) -> str:
        value = value.strip()
        prefix, _, rest = value.partition(":")
        if rest and prefix in self.prefixes and not rest.startswith("//"):
            return self.prefixes[prefix] + rest
        return expand(value)

    @property
    def report(self) -> dict:
        if not hasattr(self, "_report"):
            self._report = load_report(self.discrepancies_path, self.db_path)
        return self._report

    @property
    def public(self) -> set[str]:
        if not hasattr(self, "_public"):
            self._public = public_ids(self.db.execute("SELECT id, kind, name, status FROM record").fetchall(),
                                      self.db.execute("SELECT record_id, source_id FROM record_source").fetchall(),
                                      self.db.execute("SELECT from_id, relation, to_id FROM link").fetchall())
        return self._public

    @property
    def index(self):
        if not hasattr(self, "_index"):
            import search as s
            self._index = s.build(self.db, self.public, self.report["discrepancies"], lambda v: literals(v, "text"))
        return self._index

    def search(self, text: str, types: list[str] | str | None = None, limit: int = 20, offset: int = 0) -> dict:
        """Records and discrepancies ranked by how well text matches their names, descriptions and
        search text. types limits the results to these classes (prefixed names or IRIs, such as
        rb:Model) or record kinds (model)."""
        import search as s
        if not s.words(text):
            raise ValueError("text must contain at least one letter or digit")
        if isinstance(types, str):
            types = [t for t in types.split(",") if t.strip()]
        wanted = [self.kind_class.get(t.strip(), None) or self.compact(self.full(t)) for t in types or []]
        limit, offset = min(max(1, int(limit)), 200), max(0, int(offset))
        index = self.index
        scores, matched = index.score(text)
        if wanted:
            scores = {k: v for k, v in scores.items() if set(wanted) & set(index.types.get(k, ()))}
        ranked = index.rank(scores)
        results = []
        for key in ranked[offset:offset + limit]:
            classes = index.types.get(key, [])
            kind = next((k for k, c in self.kind_class.items() if classes and c == classes[0]), None)
            results.append({"id": self.compact(key), "iri": key, "label": index.labels.get(key),
                            "kind": kind or ("discrepancy" if "rb:Discrepancy" in classes else None),
                            "types": sorted(classes), "score": round(scores[key], 3), "matched": sorted(matched[key])})
        return {"query": text, "types": wanted, "total": len(ranked), "offset": offset, "results": results}

    def name_of(self, record_id: str) -> tuple[str | None, str | None]:
        row = self.db.execute("SELECT kind, name FROM record WHERE id = ?", (record_id,)).fetchone()
        return (row[0], row[1]) if row else (None, None)

    def describe_resource(self, iri: str, direction: str = "both", limit: int = 50, offset: int = 0) -> dict:
        """One record as the store holds it, with the name and kind of every record it cites or
        links to, the records that cite or link to it (paged; limit and offset apply to these),
        and the discrepancies it takes part in."""
        from migrate import rebuild
        if direction not in ("out", "in", "both"):
            raise ValueError("direction must be 'out', 'in' or 'both'")
        target = self.full(iri)
        record_id = target[len(ID):] if target.startswith(ID) else target
        limit, offset = min(max(0, int(limit)), 500), max(0, int(offset))
        out: dict = {"id": record_id, "iri": node(record_id)}
        finding = next((f for f in self.report["discrepancies"] if f["id"] == record_id), None)
        if finding is not None:
            return {**out, "kind": "discrepancy", "public": True, "discrepancy": finding}
        if self.db.execute("SELECT 1 FROM record WHERE id = ?", (record_id,)).fetchone() is None:
            return {**out, "found": False, "note": "No record has this ID. Use search to find records by name."}
        record = rebuild(self.db, record_id)
        out.update(kind=record["kind"], name=record.get("name"), public=record_id in self.public)
        if direction in ("out", "both"):
            out["record"] = record
            out["sources"] = [{"id": s, "kind": k, "name": n} for s in record["source_ids"] for k, n in [self.name_of(s)]]
            out["links_out"] = [{"relation": link["relation"], "id": link["target_id"], "kind": k, "name": n}
                                for link in record["links"] for k, n in [self.name_of(link["target_id"])]]
        if direction in ("in", "both"):
            incoming = self.db.execute(
                """SELECT relation, from_id, kind, name FROM (
                     SELECT l.relation, l.from_id, r.kind, r.name FROM link l JOIN record r ON r.id = l.from_id WHERE l.to_id = ?
                     UNION ALL
                     SELECT 'cites', rs.record_id, r.kind, r.name FROM record_source rs JOIN record r ON r.id = rs.record_id WHERE rs.source_id = ?)
                   ORDER BY relation, from_id""", (record_id, record_id)).fetchall()
            counts = Counter(relation for relation, *_ in incoming)
            out["links_in"] = {"total": len(incoming), "by_relation": dict(sorted(counts.items())), "offset": offset,
                               "links": [{"relation": r, "id": i, "kind": k, "name": n} for r, i, k, n in incoming[offset:offset + limit]]}
        roles = []
        for f in self.report["discrepancies"]:
            for role, key in (("system", "systems"), ("outlier", "outlier_results"), ("consensus", "consensus_results"),
                              ("party", "party_results"), ("outlier source", "outlier_sources"),
                              ("consensus source", "consensus_sources"), ("party source", "party_sources")):
                if record_id in (f.get(key) or []):
                    roles.append({"id": f["id"], "role": role, "label": f["label"], "severity": f["severity"],
                                  "state": f["review_state"]})
        out["discrepancies"] = roles
        return out

    def dataset_info(self) -> dict:
        """What the agents print when they start: the release the discrepancies are for, when the
        database was built, and how many records of each kind it holds."""
        db_file = Path(self.db_path)
        kinds = dict(self.db.execute("SELECT kind, count(*) FROM record GROUP BY kind ORDER BY kind").fetchall())
        report = self.report
        findings = report["discrepancies"]
        return {
            "dataset": "rewire-benchmark-data",
            "release_id": report.get("release_id"),
            "database": str(db_file),
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(db_file.stat().st_mtime)),
            "records": sum(kinds.values()),
            "public_records": len(self.public),
            "records_by_kind": kinds,
            "links": self.db.execute("SELECT count(*) FROM link").fetchone()[0],
            "source_citations": self.db.execute("SELECT count(*) FROM record_source").fetchone()[0],
            "discrepancies": {"total": len(findings), "open": sum(f["review_state"] not in SETTLED for f in findings),
                              "schema_version": report.get("schema_version")},
            "queries": list(QUERIES),
            "tools": list(TOOLS),
        }


TOOLS = {
    "search": {
        "title": "Records ranked by how well text matches their names, descriptions and search text",
        "params": [{"name": "text", "type": "string", "required": True}, {"name": "types", "type": "list"},
                   {"name": "limit", "type": "integer"}, {"name": "offset", "type": "integer"}],
    },
    "describe_resource": {
        "title": "One record with its fields, attributes, sources, links out and in, and discrepancies",
        "params": [{"name": "iri", "type": "iri", "required": True}, {"name": "direction", "type": "string"},
                   {"name": "limit", "type": "integer"}, {"name": "offset", "type": "integer"}],
    },
    "dataset_info": {"title": "The release, the database and its record counts", "params": []},
}


QUERIES = {
    "open_discrepancies": {
        "title": "Open discrepancies between studies, most severe first",
        "params": [{"name": "severity", "type": "string"}],
        "columns": ["discrepancy", "severity", "state", "rule", "scope", "summary"],
        "order_keys": ["rank:severity", "discrepancy"],
    },
    "discrepancies_for_system": {
        "title": "Discrepancies, settled or not, that compare a model or method",
        "params": [{"name": "system", "type": "iri", "required": True}],
        "columns": ["discrepancy", "other", "otherName", "severity", "state", "summary"],
        "order_keys": ["rank:severity", "discrepancy"],
    },
    "discrepancy_history": {
        "title": "Follow-up history of a discrepancy, in revision order",
        "params": [{"name": "discrepancy", "type": "iri", "required": True}],
        "columns": ["revision", "actionType", "state", "date", "url", "nextCheck", "claim"],
        "order_keys": ["revision"],
    },
    "contested_results_for_use_case": {
        "title": "Results on a use case's protocols that an unsettled discrepancy rests on",
        "params": [{"name": "use_case", "type": "iri", "required": True}],
        "columns": ["result", "role", "discrepancy", "severity", "state", "summary"],
        "order_keys": ["rank:severity", "discrepancy", "role", "result"],
    },
    "rank_for_use_case": {
        "title": "Ranked configurations for a use case, on its one comparable protocol",
        "params": [{"name": "use_case", "type": "iri", "required": True}],
        "columns": ["rank", "configuration", "name", "tool", "value", "unit", "result", "evaluation", "origin", "independent",
                    "reviewStatus", "receipt", "evaluated", "relevant", "openFindings", "comparison", "protocol", "relevance",
                    "metric", "direction"],
        "order_keys": ["rank", "lcase:name", "configuration"],
    },
    "gaps": {
        "title": "Evidence gaps for use cases and their protocols",
        "params": [{"name": "use_case", "type": "iri"}, {"name": "tier", "type": "integer"}, {"name": "level", "type": "string"}],
        "columns": ["useCase", "useCaseName", "depthTier", "level", "protocol", "protocolName", "gap", "evaluations", "studies"],
        "order_keys": ["level", "useCase", "protocol", "gap"],
    },
    "recipe_for": {
        "title": "Run recipes and run receipts recorded for a benchmark, protocol or model",
        "params": [{"name": "subject", "type": "iri", "required": True}],
        "columns": ["record", "recordName", "storeRecipes", "fullProtocolReceipt", "receiptName", "receiptUrl",
                    "receiptRevision", "receiptDate"],
        "order_keys": ["record", "fullProtocolReceipt"],
    },
    "results_for_model": {
        "title": "Reviewed results for a model, method, pipeline or configuration",
        "params": [{"name": "model", "type": "iri", "required": True}],
        "columns": ["configuration", "name", "protocol", "protocolName", "metric", "metricQualifier", "value", "unit",
                    "direction", "result", "evaluation", "origin", "independent", "reviewStatus", "receipt", "useCases",
                    "openFindings"],
        "order_keys": ["protocol", "metric", "metricQualifier", "configuration", "result"],
    },
    "provenance": {
        "title": "Sources, locator, capture and review history of one result",
        "params": [{"name": "result", "type": "iri", "required": True}],
        "columns": ["step", "record", "name", "locator", "url", "doi", "retrieved", "sha256", "status", "reviewedBy",
                    "reviewMethod", "date", "field", "value"],
        "order_keys": ["step", "date", "record"],
    },
}


def default_use_cases() -> str | None:
    manifest = Path("public/omics/manifest.json")
    if not manifest.exists():
        return None
    path = Path("public/omics/releases") / json.loads(manifest.read_text("utf-8"))["release_id"] / "use-cases.json"
    return str(path) if path.exists() else None


def plain(value):
    """A value for JSON: a Decimal as a number when that loses nothing, else as text."""
    if isinstance(value, Decimal):
        f = float(value)
        return f if Decimal(repr(f)) == value else str(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Answer a named graph query from kb.sqlite.")
    parser.add_argument("query", nargs="?")
    parser.add_argument("--list", action="store_true", help="list the queries and their parameters")
    parser.add_argument("--param", action="append", default=[], metavar="NAME=VALUE")
    parser.add_argument("--db", default="kb/build/kb.sqlite")
    parser.add_argument("--use-cases", help="the release's use-cases.json, which says what the release serves "
                        "(default: public/omics/releases/<release in public/omics/manifest.json>/use-cases.json)")
    parser.add_argument("--discrepancies", help="discrepancies.json from kb/discrepancies.py")
    parser.add_argument("--format", choices=("json", "table"), default="json")
    args = parser.parse_args()
    if args.list or not args.query:
        for name, spec in {**QUERIES, **TOOLS}.items():
            params = ", ".join(f"{p['name']} ({p['type']}{', required' if p.get('required') else ''})" for p in spec["params"])
            print(f"{name}: {spec['title']}. Parameters: {params or 'none'}")
        return
    if args.query not in QUERIES and args.query not in TOOLS:
        parser.error(f"unknown query {args.query}; see --list")
    params = dict(p.split("=", 1) for p in args.param)
    if args.query in TOOLS:
        known = {p["name"] for p in TOOLS[args.query]["params"]}
        if set(params) - known:
            parser.error(f"unknown parameter(s) for {args.query}: {', '.join(sorted(set(params) - known))}")
        started = time.time()
        answer = getattr(Records(args.db, discrepancies=args.discrepancies), args.query)(**params)
        print(f"{args.query} in {time.time() - started:.1f} s", file=sys.stderr)
        print(json.dumps(answer, indent=1, ensure_ascii=False))
        return
    if args.use_cases is None:
        args.use_cases = default_use_cases()
        if args.use_cases is None:
            print("warning: no use-cases.json given or found, so nothing is served: rank_for_use_case returns no rows "
                  "and gaps reports no evidence", file=sys.stderr)
    started = time.time()
    kb = KB(args.db, use_cases=args.use_cases, discrepancies=args.discrepancies)
    loaded = time.time()
    if kb.skipped:
        print(f"warning: {kb.skipped} entries of {args.use_cases} name records this database does not hold as public "
              "records of that kind; the file is probably for another release", file=sys.stderr)
    rows = kb.run(args.query, **params)
    print(f"{len(rows)} rows; loaded in {loaded - started:.1f} s, query {time.time() - loaded:.2f} s", file=sys.stderr)
    columns = QUERIES[args.query]["columns"]
    if args.format == "json":
        print(json.dumps([{c: plain(r[c]) for c in columns} for r in rows], indent=1, ensure_ascii=False))
        return
    vocab = "https://benchmarks.rewire.it/vocab/"
    short = lambda v: "" if v is None else "id:" + v[len(ID):] if str(v).startswith(ID) else v[len(vocab):] if str(v).startswith(vocab) else str(plain(v))
    text = [[short(r[c]) for c in columns] for r in rows]
    widths = [min(60, max([len(c)] + [len(t[i]) for t in text])) for i, c in enumerate(columns)]
    print("  ".join(c.ljust(w) for c, w in zip(columns, widths)))
    for t in text:
        print("  ".join(v[:w].ljust(w) for v, w in zip(t, widths)))


if __name__ == "__main__":
    main()
