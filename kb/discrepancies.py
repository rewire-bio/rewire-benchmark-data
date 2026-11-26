"""Find results from one study that disagree with results from other studies, from kb.sqlite.

Usage: python3 kb/discrepancies.py [--db kb/build/kb.sqlite] --release <release id> --out <path> [--root .]

This reads the database kb/migrate.py builds and writes discrepancies.json with the same findings,
IDs and fields as scripts/kg/contradictions.py, which runs over the RDF graph after OWL inference.
The rules, thresholds, keys and report are that script's; only the lookups differ. The graph is
replaced by the few facts the rules read, taken from the record, record_source and link tables
and the attribute columns:

  public records  The graph holds only public records (publicRecords in scripts/omics/schema.ts):
                  not excluded or disputed, results that are source_checked, reproduced or
                  superseded, and nothing whose sources or link targets are not public.
  within          The only inferred fact the rules use: the transitive closure of part_of and
                  parent links (rb:within in data/ontology/rb.ttl).
  values          As the exporter writes them (scripts/kg/export.ts): a url only if it starts with
                  http:// or https://, numbers as exact decimals, IRIs percent-encoded like
                  encodeURI, and one value per item of a list. Where the old script takes one
                  object of several (rdflib's Graph.value), this takes the lowest, which is the
                  first line of the sorted N-Quads file the graph was loaded from.

--root is the tree that holds data/ontology/discrepancy-rules.json, data/vocab/metric.ttl and
scripts/kg/fixtures/labelled-findings.json, by default the repository this file is in.

Rules, with thresholds in data/ontology/discrepancy-rules.json (see docs/discrepancies.md):

  ordering reversal  At least two other studies agree on which of systems A and B is better;
                     this study says the opposite. Each study counts once: its comparisons of
                     the pair become one verdict (A, B or split) before studies are counted.
  two-study conflict Only two studies give a verdict on the pair, and they disagree. There is
                     no consensus to stand out from, so neither is named the outlier.
  gap outlier        In a group of at least three studies of one metric on one protocol or task,
                     with a reference system that every study in the group measured (a named
                     baseline if there is one), this study's median relative difference between a
                     system and the reference lies outside the range of the others by more than a
                     margin. A group without such a reference is skipped.

A discrepancy's ID hashes a canonical key: rule, compared systems (after configuration, family
and alias resolution), anchor, metric and outlier study key, or for a two-study conflict both
study keys. The study key is the lowest DOI among the study's sources, else the lowest repository
URL, else the source retrieved first (tie-break: ID).

The exit status is 1 when review claims do not match the findings or a hand-reviewed finding
would be hidden, the checks the graph build fails on; the file is written either way.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import statistics
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from migrate import COLUMNS, TABLE_OF  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MUST_STAY_VISIBLE = ("real-error", "lead")

ID = "https://benchmarks.rewire.it/id/"
VOCAB = "https://benchmarks.rewire.it/vocab/"
REPOSITORY = re.compile(r"^https?://(?:github\.com|raw\.githubusercontent\.com)/([^/]+)/([^/#?]+)", re.I)


def concept(scheme: str, key: str) -> str:
    return f"{VOCAB}{scheme}/{key}"


HIGHER, LOWER, UNKNOWN = (concept("direction", k) for k in ("higher", "lower", "unknown"))
COPIED_ORIGIN = concept("origin", "paper_compilation")
CHECKED = {concept("status", "source_checked"), concept("status", "reproduced")}
DISPUTED = concept("status", "disputed")
SIZE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(k|m|b|t|thousand|million|billion|trillion)(?![a-z])", re.I)
SIZE_UNITS = {"k": 1e3, "thousand": 1e3, "m": 1e6, "million": 1e6, "b": 1e9, "billion": 1e9, "t": 1e12, "trillion": 1e12}
PUBLIC_STATES = ("investigating", "reported-upstream", "awaiting-correction", "confirmed-error")
REVIEW_FIELD = "discrepancy_review"
BASELINE_FIELD = "baseline"
WORKING_STATES = ("investigating", "reported-upstream", "awaiting-correction")
TERMINAL_STATES = ("explained", "confirmed-error", "false-positive")
STATES = {"open", *WORKING_STATES, *TERMINAL_STATES}
# The resolution fields of a review claim, and how each is written in the report.
RESOLUTION = {
    "investigation_url": "iri", "report_url": "iri", "reported_on": "date", "upstream_response": "text",
    "awaiting": "text", "expected_by": "date", "next_check": "date", "resolved_by": "iris", "rationale": "text",
}
SEVERITY = ["low", "medium", "high"]
MAX_STUDY_COMPARISONS = 200

# ---- The facts the rules read, as the graph export writes them ----

# Links read by the rules, by relation.
LINKS = ("system", "assessment", "data", "evaluation", "original_evaluation", "implemented_by", "family",
         "configuration_of", "alias_of", "uses_model", "part_of", "parent", "evaluates_task", "companion_of", "subject")
# Attributes read by the rules, and how the exporter writes each: a concept in a scheme, a web
# address, a record, a date-time, a decimal, JSON, or text.
ATTRIBUTES = {
    "doi": "text", "url": "iri", "retrieved_at": "datetime", "evidence_concerns": "json",
    "combination_rule": "text", "model_version": "text", "checkpoint": "text", "reported_name": "text",
    "numeric_value": "decimal", "metric": "concept:metric", "metric_direction": "concept:direction",
    "unit": "concept:unit", "metric_qualifier": "text", "split": "text", "origin": "concept:origin",
    "field": "text", "value": "text", "discrepancy_id": "text", "action": "concept:discrepancy-action",
    "revision": "text", "date": "text", "previous_ids": "text", "method_ids": "record",
    "investigation_url": "iri", "report_url": "iri", "reported_on": "text", "upstream_response": "text",
    "awaiting": "text", "expected_by": "text", "next_check": "text", "resolved_by": "record", "rationale": "text",
}
DECIMAL = re.compile(r"^([-+]?)(\d+)(?:\.(\d+))?(?:[eE]([-+]?\d+))?$")
URI_KEEP = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789;,/?:@&=+$-_.!~*'()#")
URI_RESERVED = frozenset(";/?:@&=+$,#")


def decode_uri(text: str) -> str:
    """JavaScript decodeURI: escapes of reserved characters stay escaped. Raises ValueError on a
    malformed escape."""
    out, i = [], 0
    while i < len(text):
        if text[i] != "%":
            out.append(text[i])
            i += 1
            continue
        escape = text[i:i + 3]
        if not re.fullmatch(r"%[0-9A-Fa-f]{2}", escape):
            raise ValueError(text)
        first = int(escape[1:], 16)
        if first < 0x80:
            out.append(escape if chr(first) in URI_RESERVED else chr(first))
            i += 3
            continue
        length = 2 if first >> 5 == 0b110 else 3 if first >> 4 == 0b1110 else 4 if first >> 3 == 0b11110 else 0
        if not length:
            raise ValueError(text)
        data = [first]
        for k in range(1, length):
            escape = text[i + 3 * k:i + 3 * k + 3]
            if not re.fullmatch(r"%[0-9A-Fa-f]{2}", escape):
                raise ValueError(text)
            data.append(int(escape[1:], 16))
        out.append(bytes(data).decode("utf-8"))
        i += 3 * length
    return "".join(out)


def iri(value: str) -> str:
    """An IRI as the exporter writes it: encodeURI(decodeURI(value)), or of the value itself when
    it does not decode."""
    try:
        value = decode_uri(value)
    except (ValueError, UnicodeDecodeError):
        pass
    return "".join(c if c in URI_KEEP else "".join(f"%{b:02X}" for b in c.encode("utf-8", "surrogatepass")) for c in value)


def node(record_id: str) -> str:
    return iri(ID + record_id)


def js_string(value) -> str:
    """String(value) in JavaScript, for the scalar types a record attribute holds."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if value.is_integer() and abs(value) < 1e21:
            return str(int(value))
        text = repr(value)
        if "e" in text:
            mantissa, exponent = text.split("e")
            exponent = int(exponent)
            if -7 < exponent < 21:
                return format(Decimal(text), "f")
            return f"{mantissa}e{'+' if exponent > 0 else '-'}{abs(exponent)}"
        return text
    return str(value)


def canonical_decimal(text: str) -> str | None:
    """The xsd:decimal lexical form the exporter writes (canonicalDecimal in export.ts)."""
    match = DECIMAL.match(text.strip())
    if not match:
        return None
    sign, whole, fraction, exponent = match.group(1), match.group(2), match.group(3) or "", match.group(4) or "0"
    digits = whole + fraction
    point = len(whole) + int(exponent)
    if point <= 0:
        digits = "0" * (1 - point) + digits
        point = 1
    if point > len(digits):
        digits += "0" * (point - len(digits))
    integer = re.sub(r"^0+(?=\d)", "", digits[:point])
    decimals = digits[point:]
    return f"{'-' if sign == '-' else ''}{integer}{'.' + decimals if decimals else ''}"


def exported(value, how: str) -> list:
    """The objects the exporter writes for one attribute value."""
    if how == "json":
        return [value]
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
        elif how == "record":
            out.append(node(text))
        elif how == "datetime":
            # A date-time literal reads back in rdflib's canonical form (isoformat).
            try:
                out.append(text if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) else datetime.fromisoformat(text).isoformat())
            except ValueError:
                out.append(text)
        else:
            out.append(text)
    return out


class Graph:
    """The public records' facts that the rules read. facts[predicate][subject] is the sorted set
    of objects; predicates are link relations, attribute keys, and "label", "status", "source"."""

    def __init__(self, db: sqlite3.Connection):
        rows = db.execute("SELECT id, kind, name, status FROM record").fetchall()
        refs: dict[str, set[str]] = defaultdict(set)
        for record_id, source_id in db.execute("SELECT record_id, source_id FROM record_source"):
            refs[source_id].add(record_id)
        for from_id, to_id in db.execute("SELECT from_id, to_id FROM link"):
            refs[to_id].add(from_id)
        blocked = {r for r, kind, _, status in rows if status in ("excluded", "disputed")
                   or (kind == "result" and status not in ("source_checked", "reproduced", "superseded"))}
        queue = list(blocked)
        while queue:
            for dependent in refs.get(queue.pop(), ()):
                if dependent not in blocked:
                    blocked.add(dependent)
                    queue.append(dependent)
        public = {r for r, *_ in rows} - blocked

        facts: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
        self.kind: dict[str, str] = {}
        for record_id, kind, name, status in rows:
            if record_id not in public:
                continue
            subject = node(record_id)
            self.kind[subject] = kind
            if isinstance(name, str) and name != "":
                facts["label"][subject].add(name)
            if status:
                facts["status"][subject].add(iri(concept("status", status)))
        for record_id, source_id in db.execute("SELECT record_id, source_id FROM record_source"):
            if record_id in public:
                facts["source"][node(record_id)].add(node(source_id))
        for from_id, relation, to_id in db.execute("SELECT from_id, relation, to_id FROM link"):
            if from_id in public and (relation in LINKS or relation == "source"):
                facts[relation][node(from_id)].add(node(to_id))
        for table, columns in COLUMNS.items():
            typed = [(attribute, column) for attribute, column, _ in columns if attribute in ATTRIBUTES]
            kinds = [k for k, t in TABLE_OF.items() if t == table]
            select = ", ".join(["t.id", "r.extra", *(f"t.{column}" for _, column in typed)])
            query = f"SELECT {select} FROM {table} t JOIN record r ON r.id = t.id WHERE r.kind IN ({', '.join('?' * len(kinds))})"
            for record_id, extra, *values in db.execute(query, kinds):
                if record_id not in public:
                    continue
                attributes = {k: v for k, v in json.loads(extra).items() if k in ATTRIBUTES}
                for (attribute, _), value in zip(typed, values):
                    if value is not None:
                        attributes[attribute] = json.loads(value[1:]) if isinstance(value, str) and value.startswith("\x00") else value
                subject = node(record_id)
                for attribute, value in attributes.items():
                    for item in exported(value, ATTRIBUTES[attribute]):
                        if ATTRIBUTES[attribute] == "json":
                            facts[attribute].setdefault(subject, []).append(item)
                        else:
                            facts[attribute][subject].add(item)
        self.facts = {p: {s: (o if isinstance(o, list) else sorted(o)) for s, o in by.items()} for p, by in facts.items()}
        self.public_ids = public

    def objects(self, subject: str | None, predicate: str) -> list:
        return self.facts.get(predicate, {}).get(subject, [])

    def value(self, subject: str | None, predicate: str):
        found = self.objects(subject, predicate)
        return found[0] if found else None

    def has(self, subject: str | None, predicate: str) -> bool:
        return bool(self.objects(subject, predicate))

    def pairs(self, predicate: str):
        for subject, objects in sorted(self.facts.get(predicate, {}).items()):
            for o in objects:
                yield subject, o

    def of_kind(self, kind: str) -> list[str]:
        return sorted(s for s, k in self.kind.items() if k == kind)


def default_directions(path: Path) -> dict[str, str]:
    """Metric concept IRI to its default direction IRI, from the metric scheme's Turtle file."""
    found = {}
    for block in re.split(r"\n\s*\n", path.read_text("utf-8")):
        subject = re.match(r"\s*(?::([^\s;]+)|<([^>]+)>)\s", block)
        direction = re.search(r"rb:defaultDirection\s+<([^>]+)>", block)
        if subject and direction:
            key = subject.group(1)
            found[concept("metric", key) if key is not None else subject.group(2)] = direction.group(1)
    return found


def within_closure(g: Graph) -> dict[str, set]:
    """rb:within: part_of and parent links, followed transitively."""
    step: dict[str, set] = defaultdict(set)
    for relation in ("part_of", "parent"):
        for s, o in g.pairs(relation):
            step[s].add(o)
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


# ---- From here the rules and the report follow scripts/kg/contradictions.py ----

def load_rules(root: Path = ROOT) -> dict:
    return json.loads((root / "data" / "ontology" / "discrepancy-rules.json").read_text("utf-8"))


@dataclass(frozen=True)
class Comparison:
    """Two systems' best values in one group of one study's results."""
    study: str
    protocol: str | None
    metric: str | None
    a: str
    b: str
    value_a: Decimal
    value_b: Decimal
    higher_is_better: bool
    results_a: tuple[str, ...]
    results_b: tuple[str, ...]
    reviewed: bool
    dataset: str | None = None
    unit: str | None = None
    qualifier: str = ""
    split: str = ""
    config_a: str | None = None
    config_b: str | None = None

    def better(self, tolerance: float) -> str | None:
        """The better system, or None for a tie within tolerance of the larger magnitude."""
        scale = max(abs(self.value_a), abs(self.value_b))
        if scale == 0 or abs(self.value_a - self.value_b) / scale <= Decimal(str(tolerance)):
            return None
        return self.a if (self.value_a > self.value_b) == self.higher_is_better else self.b

    def relative_gap(self, reference: str) -> float | None:
        """(system - reference) / |reference|, signed so that positive means the other system is
        better than the reference."""
        mine, theirs = (self.value_b, self.value_a) if reference == self.a else (self.value_a, self.value_b)
        if theirs == 0:
            return None
        gap = float((mine - theirs) / abs(theirs))
        return gap if self.higher_is_better else -gap


def local(n: str | None) -> str | None:
    return None if n is None else str(n).removeprefix(ID)


def concept_key(n: str | None) -> str | None:
    return None if n is None else str(n).rsplit("/", 1)[-1]


def finding_key(rule: str, systems: list[str], anchor: str | None, metric: str | None,
                outlier_study: str | None = None, studies: list[str] | None = None) -> dict:
    """The canonical key a discrepancy's ID hashes."""
    key = {"rule": rule, "systems": sorted(local(s) for s in systems), "anchor": local(anchor),
           "metric": concept_key(metric)}
    if studies is not None:
        key["studies"] = sorted(studies)
    else:
        key["outlier_study"] = outlier_study
    return key


def identifier(key: dict) -> str:
    canonical = json.dumps(key, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"discrepancy-{hashlib.sha256(canonical.encode()).hexdigest()[:16]}"


@dataclass
class Finding:
    """A discrepancy. For an outlier finding, `comparisons` are the outlier study's and `consensus`
    the other studies'. A two-study conflict has no outlier: `parties` are its two studies, in
    study-key order, and `comparisons` and `consensus` hold the first's and the second's."""
    rule: str
    a: str
    b: str
    outlier: str | None
    comparisons: list[Comparison]
    consensus: list[Comparison]
    numbers: dict = field(default_factory=dict)
    higher: str | None = None
    reference: str | None = None
    anchor: str | None = None
    metric: str | None = None
    pool: list[Comparison] = field(default_factory=list)
    gaps: dict[str, float] = field(default_factory=dict)
    parties: tuple[str, ...] = ()
    verdicts: dict[str, str | None] = field(default_factory=dict)


class Index:
    """Lookups over the public records that the rules need."""

    def __init__(self, g: Graph, directions: dict[str, str]):
        self.g = g
        self.directions = directions
        self._identity: dict[str, tuple[str, bool] | None] = {}
        self.within = within_closure(g)
        self.backed = self._backed_links()
        self.study = self._studies()
        self.study_keys = self._study_keys()
        self.excluded = self._excluded()
        self.baselines = self._baselines()

    def label(self, n: str) -> str:
        return str(self.g.value(n, "label") or str(n).removeprefix(ID))

    def _backed_links(self) -> set[tuple]:
        """(configuration, field) pairs backed by a checked claim, e.g. links:configuration_of:<id>."""
        backed = set()
        for claim, value in self.g.pairs("field"):
            if value.startswith("links:") and self.g.value(claim, "status") in CHECKED:
                for subject in self.g.objects(claim, "subject"):
                    backed.add((subject, value))
        return backed

    def _studies(self) -> dict[str, str]:
        """Sources that appear together on a result, share a DOI, or are files in one GitHub
        repository are one study, and so are sources joined by companion_of. A study is named by
        its lowest source."""
        parent: dict[str, str] = {}

        def find(n: str) -> str:
            parent.setdefault(n, n)
            while parent[n] != n:
                parent[n] = parent[parent[n]]
                n = parent[n]
            return n

        def union(a: str, b: str) -> None:
            first, second = sorted((find(a), find(b)))
            parent[second] = first

        for result in self.g.of_kind("result"):
            sources = self.g.objects(result, "source")
            for other in sources[1:]:
                union(sources[0], other)
            for source in sources:
                find(source)
        publications: dict[str, str] = {}
        for source in sorted(parent):
            keys = []
            if (doi := self.g.value(source, "doi")) is not None:
                keys.append(f"doi:{doi.lower()}")
            if match := REPOSITORY.match(self.g.value(source, "url") or ""):
                keys.append("github:" + "/".join(match.groups()).lower().removesuffix(".git"))
            for key in keys:
                union(publications.setdefault(key, source), source)
        for source, paper in self.g.pairs("companion_of"):
            union(source, paper)
        return {source: find(source) for source in parent}

    def _study_keys(self) -> dict[str, str]:
        """study: its stable key: lowest DOI, else lowest repository URL, else the source
        retrieved first (tie-break: ID)."""
        members: dict[str, list[str]] = defaultdict(list)
        for source, study in self.study.items():
            members[study].append(source)
        keys = {}
        for study, sources in members.items():
            dois = sorted(re.sub(r"^https?://(dx\.)?doi\.org/", "", d.strip(), flags=re.I).lower()
                          for s in sources for d in self.g.objects(s, "doi"))
            repositories = sorted(
                "https://github.com/" + "/".join(match.groups()).lower().removesuffix(".git")
                for s in sources if (match := REPOSITORY.match(self.g.value(s, "url") or "")))
            if dois:
                keys[study] = f"doi:{dois[0]}"
            elif repositories:
                keys[study] = f"repository:{repositories[0]}"
            else:
                first = min(sources, key=lambda s: (self.g.value(s, "retrieved_at") is None,
                                                    self.g.value(s, "retrieved_at") or "", s))
                keys[study] = f"source:{local(first)}"
        return keys

    def _excluded(self) -> dict[str, str]:
        """result: why it is left out: "disputed" (its status), or "concern" (a source's
        evidence_concerns entry covers it; the logic of shared/omics/concerns.ts)."""
        whole_sources, targets = set(), set()
        for source, entries in self.g.pairs("evidence_concerns"):
            for entry in entries if isinstance(entries, list) else [entries]:
                if isinstance(entry, str) and entry.strip():
                    whole_sources.add(source)
                    continue
                if not isinstance(entry, dict):
                    continue
                scoped = entry.get("applies_to")
                if isinstance(scoped, list) and scoped:
                    targets |= {ID + str(target) for target in scoped}
                else:
                    whole_sources.add(source)
        excluded = {}
        for result in self.g.of_kind("result"):
            if self.g.value(result, "status") == DISPUTED:
                excluded[result] = "disputed"
                continue
            evaluations = set(self.g.objects(result, "evaluation"))
            cited = set(self.g.objects(result, "source"))
            for evaluation in evaluations:
                cited |= set(self.g.objects(evaluation, "source"))
            if whole_sources & cited:
                excluded[result] = "concern"
                continue
            if not targets:
                continue
            path = {result}
            for evaluation in evaluations:
                path.add(evaluation)
                for relation in ("system", "assessment", "data"):
                    path |= set(self.g.objects(evaluation, relation))
                for assessment in self.g.objects(evaluation, "assessment"):
                    path |= set(self.g.objects(assessment, "part_of"))
            if path & targets:
                excluded[result] = "concern"
        return excluded

    def _baselines(self) -> set[str]:
        """Systems named as a baseline: what a baseline record is implemented by, and the methods a
        use case's baseline claim names."""
        named = {o for _, o in self.g.pairs("implemented_by")}
        for claim, value in self.g.pairs("field"):
            if value == BASELINE_FIELD:
                named |= set(self.g.objects(claim, "method_ids"))
        return {resolved[0] for system in named if (resolved := self.identity(system))}

    def identity(self, system: str | None) -> tuple[str, bool] | None:
        """The model or method a tested system stands for, and whether that link is reviewed."""
        if system is None:
            return None
        if system not in self._identity:
            self._identity[system] = self._resolve(system)
        return self._identity[system]

    def _resolve(self, system: str) -> tuple[str, bool] | None:
        if self.g.kind.get(system) != "configuration":
            target = self.g.value(system, "alias_of")
            return (target or system), True
        # A union, intersection or vote over other systems is a system of its own.
        if self.g.has(system, "combination_rule"):
            return system, True
        options = []
        for relation in ("configuration_of", "family"):
            for target in self.g.objects(system, relation):
                reviewed = (system, f"links:{relation}:{target.removeprefix(ID)}") in self.backed
                options.append((not reviewed, relation != "configuration_of", target, target, reviewed))
        if not options:
            return None
        *_, target, reviewed = min(options)
        return self.g.value(target, "alias_of") or target, reviewed

    def anchors(self, protocol: str | None) -> set:
        """The protocol, everything it sits within, and the tasks that any of those evaluate, with
        what they sit within."""
        if protocol is None:
            return set()
        found = {protocol, *self.within.get(protocol, ())}
        for n in list(found):
            for task in self.g.objects(n, "evaluates_task"):
                found |= {task, *self.within.get(task, ())}
        return found

    def unlinked(self, protocol: str | None) -> bool:
        """True when nothing places the protocol in a task, benchmark or suite."""
        return protocol is None or self.anchors(protocol) == {protocol}

    def members(self, system: str) -> set[str]:
        """The systems a combined configuration combines (its uses_model links), resolved."""
        if not self.g.has(system, "combination_rule"):
            return set()
        return {resolved[0] for member in self.g.objects(system, "uses_model") if (resolved := self.identity(member))}

    def size(self, system: str | None) -> float | None:
        """A configuration's model size, read from its name, version or checkpoint (650M, 1.6B)."""
        if system is None:
            return None
        for prop in ("label", "model_version", "checkpoint", "reported_name"):
            for value in self.g.objects(system, prop):
                if match := SIZE.search(str(value)):
                    return float(match.group(1)) * SIZE_UNITS[match.group(2).lower()]
        return None

    def direction(self, result: str) -> bool | None:
        direction = self.g.value(result, "metric_direction")
        if direction in (None, UNKNOWN):
            metric = self.g.value(result, "metric")
            direction = self.directions.get(metric) if metric is not None else None
        return True if direction == HIGHER else False if direction == LOWER else None


def decimal_of(text: str) -> Decimal:
    """The number a result's value reads back as: its canonical decimal form, or the raw text when
    the exporter wrote it as a plain literal. Raises InvalidOperation when it is not a number."""
    return Decimal(canonical_decimal(text) or text)


def comparisons(index: Index) -> list[Comparison]:
    """Every pair of systems in every group of one study's results. Each study uses one tested
    system per resolved model for all of its groups: the one with the most results in that study,
    then the larger model size, then the IRI. A combined system is never compared with one of its
    own members."""
    g = index.g
    rows = []
    for result in g.of_kind("result"):
        if result in index.excluded:
            continue
        evaluation = g.value(result, "evaluation")
        value = g.value(result, "numeric_value")
        sources = g.objects(result, "source")
        higher = index.direction(result)
        if evaluation is None or value is None or not sources or higher is None:
            continue
        if g.value(evaluation, "origin") == COPIED_ORIGIN or g.has(evaluation, "original_evaluation"):
            continue
        tested = g.value(evaluation, "system")
        resolved = index.identity(tested)
        if resolved is None:
            continue
        try:
            number = decimal_of(value)
        except InvalidOperation:
            continue
        protocol = g.value(evaluation, "assessment")
        key = (
            index.study[sources[0]], protocol, g.value(evaluation, "data"), g.value(result, "metric"),
            g.value(result, "unit"), str(g.value(result, "metric_qualifier") or ""),
            str(g.value(result, "split") or ""), higher,
        )
        rows.append((key, resolved[0], tested, number, result, resolved[1]))

    counts: dict[tuple, Counter] = defaultdict(Counter)
    for key, system, tested, *_ in rows:
        counts[(key[0], system)][tested] += 1
    chosen = {
        study_system: min(tested, key=lambda t: (-tested[t], -(index.size(t) or 0), str(t)))
        for study_system, tested in counts.items()
    }
    groups: dict[tuple, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for key, system, tested, number, result, reviewed in rows:
        if chosen[(key[0], system)] == tested:
            groups[key][system].append((number, result, reviewed))

    found = []
    for key, by_system in groups.items():
        study, protocol, dataset, metric, unit, qualifier, split, higher = key
        best = {}
        for system, items in by_system.items():
            value = (max if higher else min)(number for number, _, _ in items)
            best[system] = (value, tuple(sorted(r for n, r, _ in items if n == value)), all(rev for _, _, rev in items))
        for a in sorted(best):
            for b in sorted(best):
                if a < b and b not in index.members(a) and a not in index.members(b):
                    (va, ra, rev_a), (vb, rb_, rev_b) = best[a], best[b]
                    found.append(Comparison(study, protocol, metric, a, b, va, vb, higher, ra, rb_, rev_a and rev_b,
                                            dataset, unit, qualifier, split, chosen[(study, a)], chosen[(study, b)]))
    return found


def verdicts(items: list[Comparison], rules: dict) -> dict[str, str | None]:
    """Each study's answer for one pair of systems: the system that scored better in at least the
    verdict share of its untied comparisons, or None for a split. A study with fewer untied
    comparisons than the minimum gives no verdict and is left out."""
    r, tolerance = rules["verdict"], rules["tie_tolerance"]
    by_study: dict[str, list[str]] = defaultdict(list)
    for c in items:
        if (winner := c.better(tolerance)) is not None:
            by_study[c.study].append(winner)
    found = {}
    for study, winners in by_study.items():
        if len(winners) < r["min_comparisons"]:
            continue
        top, count = Counter(winners).most_common(1)[0]
        found[study] = top if count / len(winners) >= r["consistency"] else None
    return found


def ordering_reversals(pairs: dict, index: Index, rules: dict) -> list[Finding]:
    """Ordering findings, counted in studies rather than rows. With three or more studies taking a
    side, a study is an outlier when the others (at least the minimum number of studies) agree with
    each other at the consensus share and it says the opposite. With exactly two studies that
    disagree there is no consensus to stand out from, so they make one two-study conflict with no
    outlier. A split study takes no side, so it neither forms a party nor counts in the consensus."""
    r = rules["ordering_reversal"]
    tolerance = rules["tie_tolerance"]
    findings = []
    for (a, b), items in pairs.items():
        verdict = verdicts(items, rules)
        decided = {s: v for s, v in verdict.items() if v is not None}
        decisive = lambda study: [c for c in items if c.study == study and c.better(tolerance)]
        if len(decided) == 2:
            first, second = sorted(decided, key=lambda study: index.study_keys[study])
            if decided[first] != decided[second]:
                mine, theirs = decisive(first), decisive(second)
                findings.append(Finding(
                    "two-study-conflict", a, b, None, mine, theirs, pool=items, parties=(first, second), verdicts=verdict,
                    numbers={"studies": 2},
                ))
            continue
        for study in sorted(decided):
            others = {s: v for s, v in decided.items() if s != study}
            if len(others) < r["min_consensus_studies"]:
                continue
            for_a = sum(1 for v in others.values() if v == a)
            for_b = sum(1 for v in others.values() if v == b)
            if for_a == for_b:
                continue
            higher = a if for_a > for_b else b
            agreements = max(for_a, for_b)
            if agreements / len(others) < r["consensus_consistency"] or decided[study] == higher:
                continue
            mine = decisive(study)
            consensus = [c for c in items if c.study in others and c.better(tolerance)]
            findings.append(Finding(
                "ordering-reversal", a, b, study, mine, consensus, higher=higher, pool=items, verdicts=verdict,
                numbers={"outlier_comparisons": len(mine),
                         "outlier_reversals": sum(1 for c in mine if c.better(tolerance) != higher),
                         "consensus_comparisons": len(consensus),
                         "consensus_agreements": sum(1 for c in consensus if c.better(tolerance) == higher),
                         "consensus_studies": len(others), "consensus_study_agreements": agreements},
            ))
    return findings


def anchor_rank(index: Index, anchor: str) -> tuple:
    """Most specific first: a protocol, then a task, then a benchmark or suite; then by IRI."""
    kind = index.g.kind.get(anchor)
    return (0 if kind == "protocol" else 1 if kind == "task" else 2), str(anchor)


def gap_outliers(found: list[Comparison], index: Index, rules: dict) -> list[Finding]:
    """Per comparison group (a protocol, or a task or benchmark it sits within, and one metric),
    take a reference system every study in the group measured, preferring a named baseline. For
    each other system, compare each study's median relative gap to the reference with the other
    studies'. A pair and study that fire on several anchors keep the most specific one."""
    r = rules["gap_outlier"]
    groups: dict[tuple, list[Comparison]] = defaultdict(list)
    for c in found:
        for anchor in index.anchors(c.protocol):
            groups[(anchor, c.metric)].append(c)
    best: dict[tuple, Finding] = {}
    for (anchor, metric), items in sorted(groups.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
        measured: dict[str, set] = defaultdict(set)
        for c in items:
            measured[c.study] |= {c.a, c.b}
        if len(measured) < r["min_studies"]:
            continue
        shared = set.intersection(*measured.values())
        if not shared:
            continue
        reference = min(shared, key=lambda s: (s not in index.baselines, str(s)))
        for system in sorted(shared - {reference}):
            pair = [c for c in items if {c.a, c.b} == {system, reference}]
            gaps: dict[str, list[float]] = defaultdict(list)
            for c in pair:
                gap = c.relative_gap(reference)
                if gap is not None:
                    gaps[c.study].append(gap)
            if len(gaps) < r["min_studies"]:
                continue
            medians = {study: statistics.median(values) for study, values in gaps.items()}
            for study, median in sorted(medians.items()):
                rest = [m for s, m in medians.items() if s != study]
                low, high = min(rest), max(rest)
                miss = max(low - median, median - high)
                if miss <= r["margin"]:
                    continue
                key = (system, reference, metric, study)
                if key in best and anchor_rank(index, best[key].anchor) <= anchor_rank(index, anchor):
                    continue
                best[key] = Finding(
                    "gap-outlier", system, reference, study,
                    [c for c in pair if c.study == study], [c for c in pair if c.study != study],
                    reference=reference, anchor=anchor, metric=metric, pool=pair, gaps=medians,
                    numbers={"outlier_gap": median, "consensus_gap_min": low, "consensus_gap_max": high},
                )
    return [best[k] for k in sorted(best, key=lambda k: tuple(str(x) for x in k))]


def scope(finding: Finding, index: Index) -> tuple[str, list[str]]:
    """Whether the two sides measured the same protocol, the same task, different tasks, or cannot
    be told apart because a protocol on either side has no task, benchmark or suite link. Returns
    the scope and the unlinked protocols."""
    mine = {c.protocol for c in finding.comparisons}
    theirs = {c.protocol for c in finding.consensus}
    unlinked = sorted({p for p in mine | theirs if p is not None and index.unlinked(p)})
    if mine & theirs - {None}:
        return "same-protocol", unlinked
    near = set().union(*(index.anchors(p) for p in mine)) & set().union(*(index.anchors(p) for p in theirs))
    if near:
        return "same-task", unlinked
    if unlinked or None in mine | theirs:
        return "unknown", unlinked
    return "different-task", unlinked


def variant_mismatch(finding: Finding, index: Index) -> bool:
    """True when, for either system, the studies used configurations of different recorded sizes."""
    for system in (finding.a, finding.b):
        sizes = set()
        for c in finding.comparisons + finding.consensus:
            tested = c.config_a if system == c.a else c.config_b
            if (size := index.size(tested)) is not None:
                sizes.add(size)
        if len(sizes) > 1:
            return True
    return False


def severity(finding: Finding, where: str, reviewed: bool, mismatch: bool, rules: dict) -> str:
    """The highest level the scope allows, limited to medium unless enough independent studies form
    the consensus (always for the gap rule and two-study conflicts), then a step down each for
    unreviewed identity and a variant mismatch. Nothing steps a finding up."""
    r = rules["severity"]
    level = SEVERITY.index(r["cap_by_scope"][where])
    strong = (finding.rule == "ordering-reversal"
              and finding.numbers["consensus_studies"] >= r["high_min_consensus_studies"])
    if not strong:
        level = min(level, SEVERITY.index("medium"))
    level -= (not reviewed) + mismatch
    return SEVERITY[max(0, level)]


def listing(where: str, state: str) -> str:
    """public: shown on the contested page by default. review: listed for curation."""
    return "public" if where in ("same-protocol", "same-task") or state in PUBLIC_STATES else "review"


def comparison_json(c: Comparison, tolerance: float) -> dict:
    better = c.better(tolerance)
    return {
        "protocol": local(c.protocol), "dataset": local(c.dataset), "metric": concept_key(c.metric),
        "unit": concept_key(c.unit), "qualifier": c.qualifier or None, "split": c.split or None,
        "values": {local(c.a): float(c.value_a), local(c.b): float(c.value_b)},
        # The first of the results that share a system's best value.
        "results": {local(c.a): local(c.results_a[0]), local(c.b): local(c.results_b[0])},
        "higher": local(better),
    }


def studies_json(f: Finding, index: Index, tolerance: float, members_of: dict[str, list[str]]) -> list[dict]:
    """Every study that compared the finding's two systems: the outlier first (or a conflict's two
    parties), then the others by number of comparisons (most first) and key."""
    by_study: dict[str, list[Comparison]] = defaultdict(list)
    for c in f.pool:
        by_study[c.study].append(c)
    studies = []
    for study, items in by_study.items():
        items.sort(key=lambda c: tuple(str(x or "") for x in (c.protocol, c.dataset, c.metric, c.unit, c.qualifier, c.split)))
        winners = Counter(c.better(tolerance) for c in items)
        gap = f.gaps.get(study)
        used = {local(f.a): local(items[0].config_a if items[0].a == f.a else items[0].config_b),
                local(f.b): local(items[0].config_b if items[0].a == f.a else items[0].config_a)}
        studies.append({
            "key": index.study_keys[study],
            "role": "party" if study in f.parties else "outlier" if study == f.outlier else "consensus",
            "verdict": (local(f.verdicts[study]) if f.verdicts[study] else "split") if study in f.verdicts else None,
            "configurations": used,
            "source_ids": [local(s) for s in members_of[study]],
            "higher": {local(f.a): winners[f.a], local(f.b): winners[f.b]},
            "ties": winners[None],
            "gap": round(gap, 4) if gap is not None else None,
            "comparisons_total": len(items),
            "comparisons": [comparison_json(c, tolerance) for c in items[:MAX_STUDY_COMPARISONS]],
        })
    studies.sort(key=lambda s: (s["role"] == "consensus", -s["comparisons_total"], s["key"]))
    return studies


@dataclass
class Reviews:
    """Accepted discrepancy_review claims, as follow-up actions grouped by the discrepancy they
    decide after previous_ids are mapped forward."""
    actions: dict[str, list[dict]]
    previous: dict[str, list[str]]
    problems: list[str]


def reviews(index: Index) -> Reviews:
    """Checked discrepancy_review claims. Each claim is one action; the actions of one discrepancy
    ordered by revision are its history and the last one is where it stands. A claim's
    previous_ids map those IDs forward to its discrepancy_id."""
    g = index.g
    claims = []
    for claim, value in g.pairs("field"):
        if value != REVIEW_FIELD or g.value(claim, "status") not in CHECKED:
            continue
        target = g.value(claim, "discrepancy_id")
        state = str(g.value(claim, "value") or "")
        if target is None or state not in STATES:
            continue
        action = g.value(claim, "action")
        fields = {name: g.value(claim, name) for name in RESOLUTION}
        fields["resolved_by"] = g.objects(claim, "resolved_by")
        claims.append({
            "claim": claim, "target": target, "state": state, "revision": int(g.value(claim, "revision") or 0),
            "action": action.rsplit("/", 1)[-1] if action is not None else None,
            # The action's date: the claim's date attribute, else the day it was reported upstream.
            "date": g.value(claim, "date") or fields["reported_on"], "fields": fields,
            "previous_ids": sorted(g.objects(claim, "previous_ids")),
        })
    forward: dict[str, str] = {}
    problems = []
    for c in sorted(claims, key=lambda c: c["claim"]):
        for old in c["previous_ids"]:
            if forward.setdefault(old, c["target"]) != c["target"]:
                problems.append(f"{local(c['claim'])}: previous ID {old} is mapped to both {forward[old]} and {c['target']}")

    def resolve(identifier_: str) -> str:
        seen = {identifier_}
        while identifier_ in forward:
            identifier_ = forward[identifier_]
            if identifier_ in seen:
                problems.append(f"previous_ids form a cycle through {identifier_}")
                break
            seen.add(identifier_)
        return identifier_

    actions: dict[str, list[dict]] = defaultdict(list)
    for c in claims:
        actions[resolve(c["target"])].append(c)
    previous: dict[str, list[str]] = defaultdict(list)
    for old in sorted(forward):
        previous[resolve(old)].append(old)
    for target, items in actions.items():
        items.sort(key=lambda c: (c["revision"], c["claim"]))
        revisions = [c["revision"] for c in items]
        for revision in sorted({n for n in revisions if revisions.count(n) > 1}):
            problems.append(f"{target}: more than one accepted review claim has revision {revision}")
        dated = [c for c in items if c["date"] is not None]
        for earlier, later in zip(dated, dated[1:]):
            if str(later["date"]) < str(earlier["date"]):
                problems.append(f"{target}: revision {later['revision']} is dated {later['date']}, before revision "
                                f"{earlier['revision']} ({earlier['date']})")
    return Reviews(dict(actions), dict(previous), problems)


def action_json(c: dict) -> dict:
    fields = c["fields"]
    text = lambda name: str(fields[name]) if fields.get(name) is not None else None
    return {
        "revision": c["revision"], "claim_id": local(c["claim"]), "action": c["action"], "state": c["state"],
        "date": str(c["date"]) if c["date"] is not None else None,
        "rationale": text("rationale"), "investigation_url": text("investigation_url"), "report_url": text("report_url"),
        "upstream_response": text("upstream_response"), "awaiting": text("awaiting"),
        "expected_by": text("expected_by"), "next_check": text("next_check"),
        "resolved_by": [local(t) for t in fields["resolved_by"]],
    }


def resolution_json(history: list[dict]) -> dict:
    """The latest review claim's resolution fields that have a value."""
    resolution: dict = {}
    if history:
        review = history[-1]
        for name, kind in RESOLUTION.items():
            value = review["fields"].get(name)
            if not value:
                continue
            resolution[name] = [local(t) for t in value] if kind == "iris" else str(value)
    return resolution


def claimed_systems(index: Index, history: list[dict]) -> list[str]:
    """The models or methods a discrepancy's review claims are about: the tested systems of their
    subject results and evaluations, resolved like compared systems. Empty if there are more than two."""
    g = index.g
    systems = set()
    for c in history:
        for subject in g.objects(c["claim"], "subject"):
            if g.kind.get(subject) == "result":
                evaluations = g.objects(subject, "evaluation")
            elif g.kind.get(subject) == "evaluation":
                evaluations = [subject]
            else:
                continue
            for evaluation in evaluations:
                if resolved := index.identity(g.value(evaluation, "system")):
                    systems.add(resolved[0])
    return sorted(systems) if len(systems) <= 2 else []


def resolved_finding(target: str, history: list[dict], previous: list[str], index: Index) -> dict:
    """A settled discrepancy the rules no longer find (its results were disputed, say), kept so that
    its follow-up stays visible. Nothing records the rule, key or severity it last fired with, so
    the rule and key are null and the severity is low."""
    review = history[-1]
    systems = claimed_systems(index, history)
    names = " and ".join(index.label(s) for s in systems)
    label = f"{names}: resolved" if names else "Resolved discrepancy"
    rationale = review["fields"].get("rationale")
    summary = str(rationale) if rationale else f"Settled as {review['state']}; the rules no longer find this discrepancy."
    return {
        "id": target, "resolved": True, "rule": None, "label": label, "summary": summary, "severity": "low",
        "scope": None, "identity_basis": None, "review_state": review["state"], "review_claim": local(review["claim"]),
        "listing": "public", "variant_mismatch": False, "unlinked_protocols": [],
        "settled": True, "resolution": resolution_json(history), "systems": [local(s) for s in systems],
        "consensus_higher": None, "reference_system": None,
        "outlier_sources": [], "consensus_sources": [], "outlier_results": [], "consensus_results": [],
        "party_sources": [], "party_results": [], "numbers": {}, "previous_ids": previous, "key": None, "studies": [],
        "actions": [action_json(c) for c in history],
    }


@dataclass
class Derived:
    report: list[dict]
    excluded: dict[str, int]
    retired: list[str]
    problems: list[str]


def derive(g: Graph, directions: dict[str, str], rules: dict) -> Derived:
    """The discrepancies as JSON-ready dicts, in the order contradictions.py writes them."""
    index = Index(g, directions)
    found = comparisons(index)
    pairs: dict[tuple, list[Comparison]] = defaultdict(list)
    for c in found:
        pairs[(c.a, c.b)].append(c)
    findings = ordering_reversals(pairs, index, rules) + gap_outliers(found, index, rules)
    decided = reviews(index)
    members_of: dict[str, list[str]] = defaultdict(list)
    for source, study in sorted(index.study.items()):
        members_of[study].append(source)

    report = []
    tolerance = rules["tie_tolerance"]
    for f in findings:
        if f.rule == "two-study-conflict":
            key = finding_key(f.rule, [f.a, f.b], None, None, studies=[index.study_keys[p] for p in f.parties])
        else:
            key = finding_key(f.rule, [f.a, f.b], f.anchor, f.metric, index.study_keys[f.outlier])
        identifier_ = identifier(key)
        history = decided.actions.get(identifier_, [])
        review = history[-1] if history else None
        claim = review["claim"] if review else None
        state = review["state"] if review else "open"
        where, unlinked = scope(f, index)
        reviewed = all(c.reviewed for c in f.comparisons + f.consensus)
        mismatch = variant_mismatch(f, index)
        severity_ = severity(f, where, reviewed, mismatch, rules)
        listing_ = listing(where, state)
        members = lambda studies: sorted(s for study in studies for s in members_of[study])
        results = lambda items: sorted({r for c in items for r in c.results_a + c.results_b})
        if f.rule == "two-study-conflict":
            outlier_sources, consensus_sources, outlier_results, consensus_results = [], [], [], []
            party_sources, party_results = members(set(f.parties)), results(f.comparisons + f.consensus)
        else:
            outlier_sources = members({f.outlier})
            consensus_sources = members({c.study for c in f.consensus})
            outlier_results, consensus_results = results(f.comparisons), results(f.consensus)
            party_sources, party_results = [], []
        name_a, name_b = index.label(f.a), index.label(f.b)
        n = f.numbers
        if f.rule == "two-study-conflict":
            first, second = (index.label(p) for p in f.parties)
            label = f"{name_a} and {name_b}: {first} and {second} disagree"
            parts = []
            for party, items in zip(f.parties, (f.comparisons, f.consensus)):
                winner = f.verdicts[party]
                loser = f.b if winner == f.a else f.a
                wins = sum(1 for c in items if c.better(tolerance) == winner)
                parts.append(f"{index.label(party)} ranks {index.label(winner)} above {index.label(loser)} in {wins} of {len(items)} comparisons")
            summary = "; ".join(parts) + ". No other study gives a verdict, so neither is the outlier."
        elif f.rule == "ordering-reversal":
            study = index.label(f.outlier)
            top, bottom = (name_a, name_b) if f.higher == f.a else (name_b, name_a)
            label = f"{name_a} and {name_b}: {study} reverses the order"
            summary = (f"{study} ranks {bottom} above {top} in {n['outlier_reversals']} of {n['outlier_comparisons']} "
                       f"comparisons; {n['consensus_study_agreements']} of {n['consensus_studies']} other studies rank "
                       f"{top} above {bottom}.")
        else:
            study = index.label(f.outlier)
            label = f"{name_a} relative to {name_b}: {study} is outside the range of other studies"
            summary = (f"On {index.label(f.anchor)}, {study} reports {name_a} at a median relative difference of "
                       f"{n['outlier_gap']:+.2f} from {name_b}; other studies report {n['consensus_gap_min']:+.2f} to "
                       f"{n['consensus_gap_max']:+.2f}.")
        previous = decided.previous.get(identifier_, [])
        locals_ = lambda nodes: [local(x) for x in nodes]
        report.append({
            "id": identifier_, "resolved": False, "rule": f.rule, "label": label, "summary": summary, "severity": severity_,
            "scope": where, "identity_basis": "reviewed" if reviewed else "unreviewed", "review_state": state,
            "listing": listing_, "variant_mismatch": mismatch, "unlinked_protocols": locals_(unlinked),
            "review_claim": local(claim) if claim else None,
            "settled": state in TERMINAL_STATES,
            "resolution": resolution_json(history),
            "systems": locals_([f.a, f.b]),
            "consensus_higher": local(f.higher) if f.higher else None,
            "reference_system": local(f.reference) if f.reference else None,
            "outlier_sources": locals_(outlier_sources), "consensus_sources": locals_(consensus_sources),
            "outlier_results": locals_(outlier_results), "consensus_results": locals_(consensus_results),
            "party_sources": locals_(party_sources), "party_results": locals_(party_results),
            "numbers": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in n.items()},
            "previous_ids": previous,
            "key": key,
            "studies": studies_json(f, index, tolerance, members_of),
            "actions": [action_json(c) for c in history],
        })
    report.sort(key=lambda d: (-SEVERITY.index(d["severity"]), d["rule"], d["id"]))
    derived_ids = {d["id"] for d in report}
    retired, problems = [], list(decided.problems)
    for target, history in sorted(decided.actions.items()):
        if target in derived_ids:
            continue
        names = ", ".join(local(c["claim"]) for c in history)
        if history[-1]["state"] in TERMINAL_STATES:
            retired.append(target)
            report.append(resolved_finding(target, history, decided.previous.get(target, []), index))
        else:
            problems.append(f"review claim(s) {names} name {target}, which is not derived and is not settled; "
                            "if its ID changed, list the old ID in a claim's previous_ids")
    report.sort(key=lambda d: d["resolved"])
    excluded = Counter(index.excluded.values())
    return Derived(report, {"disputed": excluded["disputed"], "concern": excluded["concern"]}, retired, problems)


def labelled_problems(report: list[dict], path: Path) -> list[str]:
    """A hand-reviewed real error or lead (scripts/kg/fixtures/labelled-findings.json) that is
    missing or left off the public listing."""
    if not path.exists():
        return []
    by_id = {}
    for d in report:
        for identifier_ in [d["id"], *d.get("previous_ids", [])]:
            by_id.setdefault(identifier_, d)
    problems = []
    for entry in json.loads(path.read_text("utf-8"))["findings"]:
        unique = list({by_id[i]["id"]: by_id[i] for i in entry["ids"] if i in by_id}.values())
        if entry["label"] not in MUST_STAY_VISIBLE:
            continue
        if not unique:
            problems.append(f"{entry['name']} ({entry['label']}) no longer has a finding; list its old ID in previous_ids "
                            "or settle its review")
        for d in unique:
            if not d["resolved"] and d["listing"] != "public":
                problems.append(f"{entry['name']} ({entry['label']}) is {d['id']} on the {d['listing']} listing, not public")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="kb/build/kb.sqlite")
    parser.add_argument("--release", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()
    started = time.time()
    root = Path(args.root)
    rules = load_rules(root)
    db = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    g = Graph(db)
    db.close()
    result = derive(g, default_directions(root / "data" / "vocab" / "metric.ttl"), rules)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"schema_version": 5, "release_id": args.release, "rules": rules, "excluded": result.excluded,
         "discrepancies": result.report}, indent=2, ensure_ascii=False) + "\n", "utf-8")
    live = sum(not d["resolved"] for d in result.report)
    print(f"Wrote {live} discrepancies and {len(result.report) - live} resolved ones to {out} in {time.time() - started:.1f} s; "
          f"left out {result.excluded['disputed']} disputed results and {result.excluded['concern']} under an evidence concern.")
    problems = result.problems + labelled_problems(result.report, root / "scripts" / "kg" / "fixtures" / "labelled-findings.json")
    for problem in problems[:20]:
        print(f"  problem: {problem}", file=sys.stderr)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
