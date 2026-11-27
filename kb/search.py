"""Free-text search over the records in kb.sqlite, ranked as rdf-kg-mcp's search tool ranks them.

The scoring is rdf-kg-mcp's (src/rdf_kg_mcp/search.py at v0.4.0), copied so that the agents get
the same hits from the database as from the graph:

  words      Case folded runs of letters and digits, with one English suffix stripped (ing, ed,
             es, e, s) when four characters remain. A query word matches an indexed word whole, or
             as the prefix of a longer one (weight 0.6) when it has four characters or more.
  squashed   A name is also indexed as one term of its letters and digits only, matched whole
             against the query squashed whole and per space-separated chunk: "ESM2" finds "ESM-2".
  fields     BM25F-like with k1 1.2 and b 0.75: name 3, description 1, text attributes 1.
  rarity     The score is multiplied by log(1 + documents / size of the record's rarest class),
             squared, so a model or use case ranks above the many results that repeat a word.
  diversity  No class takes more than three of the leading places.

What is indexed is what the graph indexes: the name and description of every public record, the
text attributes the bundle declares for search (reported_name, task, question, search_terms) on
the kinds the attribute registry declares them for, and the label of each discrepancy in
discrepancies.json. A record's classes are its kind's classes in data/ontology/mapping.json with
their rb: superclasses from data/ontology/rb.ttl, as the graph's inferred types give them.
"""
from __future__ import annotations

import bisect
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RB = "https://benchmarks.rewire.it/vocab#"
FIELD_WEIGHTS = {"label": 3.0, "alias": 2.0, "description": 1.0, "text": 1.0}
SQUASHED_FIELDS = {"label": "label_squashed", "alias": "alias_squashed"}
SQUASHED_NAMES = {squashed: name for name, squashed in SQUASHED_FIELDS.items()}
SQUASH_MARK = "\x00"
PREFIX_WEIGHT = 0.6
MIN_PREFIX = 4
RARITY_EXPONENT = 2.0
PER_CLASS_LEAD = 3
K1 = 1.2
B = 0.75
_WORD = re.compile(r"[^\W_]+")
_SUFFIXES = ("ing", "ed", "es", "e", "s")
# Attributes the bundle's manifest declares as search text, and the kinds the attribute registry
# (shared/omics/attribute-registry.ts) declares each for. On any other kind they are not exported.
TEXT_ATTRIBUTES = {
    "reported_name": {"configuration", "dataset", "method", "model", "pipeline", "service"},
    "task": {"benchmark", "configuration", "evaluator", "protocol", "task"},
    "question": {"use_case"},
    "search_terms": {"use_case"},
}


def stem(word: str) -> str:
    for suffix in _SUFFIXES:
        if len(word) - len(suffix) >= 4 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def words(text: str) -> list[str]:
    return [stem(w) for w in _WORD.findall(text.casefold())]


def squash(text: str) -> str:
    return "".join(_WORD.findall(text.casefold()))


def squashed_terms(text: str) -> list[str]:
    chunks = [text, *text.split()]
    return [SQUASH_MARK + term for term in dict.fromkeys(squash(c) for c in chunks) if term]


def classes_of_kinds(root: Path = ROOT) -> dict[str, list[str]]:
    """Each record kind's classes, as prefixed names: the mapped types, then rb: superclasses."""
    mapping = json.loads((root / "data" / "ontology" / "mapping.json").read_text("utf-8"))
    supers: dict[str, list[str]] = {}
    for match in re.finditer(r"^(rb:\w+) a owl:Class ; rdfs:subClassOf ([^;\n]+);", (root / "data" / "ontology" / "rb.ttl").read_text("utf-8"), re.M):
        supers[match.group(1)] = [c.strip() for c in match.group(2).split(",") if c.strip().startswith("rb:")]
    out = {}
    for kind, entry in mapping["classes"].items():
        found = list(entry["types"])
        for cls in found:
            found += [s for s in supers.get(cls, []) if s not in found]
        out[kind] = found
    out["relevance_judgement"] = ["rb:RelevanceJudgement", "rb:Claim"]
    return out


def discrepancy_classes(finding: dict) -> list[str]:
    if finding.get("resolved"):
        return ["rb:Discrepancy", "rb:ResolvedDiscrepancy"]
    return ["rb:Discrepancy", "rb:" + "".join(part.title() for part in finding["rule"].split("-"))]


class _Doc:
    __slots__ = ("lengths", "rarity", "group")

    def __init__(self) -> None:
        self.lengths: dict[str, int] = {}
        self.rarity = 1.0
        self.group = ""


class SearchIndex:
    """An inverted index from word stems to record IDs and per-field term counts."""

    def __init__(self) -> None:
        self.postings: dict[str, dict[str, dict[str, int]]] = defaultdict(dict)
        self.docs: dict[str, _Doc] = {}
        self.average: dict[str, float] = {}
        self.types: dict[str, list[str]] = {}
        self.labels: dict[str, str] = {}
        self._terms: list[str] = []

    def add(self, key: str, field: str, text: str) -> None:
        tokens = words(text)
        if not tokens:
            return
        doc = self.docs.setdefault(key, _Doc())
        self._add(key, doc, field, tokens)
        if field in SQUASHED_FIELDS:
            self._add(key, doc, SQUASHED_FIELDS[field], [SQUASH_MARK + squash(text)])

    def _add(self, key: str, doc: _Doc, field: str, tokens: list[str]) -> None:
        doc.lengths[field] = doc.lengths.get(field, 0) + len(tokens)
        for token in tokens:
            counts = self.postings[token].setdefault(key, {})
            counts[field] = counts.get(field, 0) + 1

    def finish(self) -> None:
        totals: Counter[str] = Counter()
        counts: Counter[str] = Counter()
        for doc in self.docs.values():
            for name, length in doc.lengths.items():
                totals[name] += length
                counts[name] += 1
        self.average = {name: totals[name] / counts[name] for name in totals}
        sizes: Counter[str] = Counter()
        for key in self.docs:
            for cls in self.types.get(key) or [""]:
                sizes[cls] += 1
        n = max(1, len(self.docs))
        for key, doc in self.docs.items():
            doc.group = min(self.types.get(key) or [""], key=lambda c: (sizes[c], c))
            doc.rarity = math.log(1 + n / sizes[doc.group])
        self._terms = sorted(self.postings)

    def _expand(self, term: str) -> list[tuple[str, float]]:
        matches = [(term, 1.0)] if term in self.postings else []
        if len(term) < MIN_PREFIX or term.startswith(SQUASH_MARK):
            return matches
        i = bisect.bisect_right(self._terms, term)
        while i < len(self._terms) and self._terms[i].startswith(term):
            matches.append((self._terms[i], PREFIX_WEIGHT))
            i += 1
        return matches

    def score(self, text: str) -> tuple[dict[str, float], dict[str, set]]:
        scores: dict[str, float] = defaultdict(float)
        matched: dict[str, set] = defaultdict(set)
        n = max(1, len(self.docs))
        for query_term in dict.fromkeys([*words(text), *squashed_terms(text)]):
            for term, weight in self._expand(query_term):
                posting = self.postings[term]
                idf = math.log(1 + (n - len(posting) + 0.5) / (len(posting) + 0.5))
                for key, fields in posting.items():
                    doc = self.docs[key]
                    total = 0.0
                    for name, tf in fields.items():
                        norm = 1 - B + B * doc.lengths[name] / self.average[name]
                        original = SQUASHED_NAMES.get(name, name)
                        total += FIELD_WEIGHTS.get(original, 1.0) * tf * (K1 + 1) / (tf + K1 * norm)
                        matched[key].add(original)
                    scores[key] += weight * idf * total
        for key in scores:
            scores[key] *= self.docs[key].rarity ** RARITY_EXPONENT
        return scores, matched

    def rank(self, scores: dict[str, float]) -> list[str]:
        ordered = sorted(scores, key=lambda key: (-scores[key], key))
        seen: Counter[str] = Counter()
        lead, rest = [], []
        for key in ordered:
            group = self.docs[key].group
            (lead if seen[group] < PER_CLASS_LEAD else rest).append(key)
            seen[group] += 1
        return lead + rest


def build(db, public: set[str], report: list[dict], text_literals) -> SearchIndex:
    """The index over the public records of an open kb.sqlite and the findings of a report.
    Keys are full IRIs. text_literals(value) gives the literals the exporter writes for a text
    attribute value (one per list item)."""
    from migrate import COLUMNS, TABLE_OF
    from queries import node

    index = SearchIndex()
    kinds = classes_of_kinds()
    for record_id, kind, name, description in db.execute("SELECT id, kind, name, description FROM record"):
        if record_id not in public:
            continue
        key = node(record_id)
        index.types[key] = list(kinds[kind])
        if isinstance(name, str) and name != "":
            index.labels[key] = name
            index.add(key, "label", name)
        if isinstance(description, str) and description != "":
            index.add(key, "description", description)
    # A claim backing a use case's assessed_by link is a relevance judgement.
    for record_id, in db.execute("SELECT id FROM claim WHERE field LIKE 'links:assessed_by:%'"):
        key = node(record_id)
        if key in index.types and "rb:RelevanceJudgement" not in index.types[key]:
            index.types[key] += [c for c in kinds["relevance_judgement"] if c not in index.types[key]]
    for table, columns in COLUMNS.items():
        typed = [(a, c) for a, c, _ in columns if a in TEXT_ATTRIBUTES]
        wanted = [k for k, t in TABLE_OF.items() if t == table and any(k in TEXT_ATTRIBUTES[a] for a in TEXT_ATTRIBUTES)]
        if not wanted:
            continue
        select = ", ".join(["t.id", "r.kind", "r.extra", *(f"t.{c}" for _, c in typed)])
        query = f"SELECT {select} FROM {table} t JOIN record r ON r.id = t.id WHERE r.kind IN ({', '.join('?' * len(wanted))})"
        for record_id, kind, extra, *values in db.execute(query, wanted):
            if record_id not in public:
                continue
            attributes = {a: v for a, v in json.loads(extra).items() if a in TEXT_ATTRIBUTES}
            for (attribute, _), value in zip(typed, values):
                if value is not None:
                    attributes[attribute] = json.loads(value[1:]) if isinstance(value, str) and value.startswith("\x00") else value
            key = node(record_id)
            for attribute, value in attributes.items():
                if kind in TEXT_ATTRIBUTES[attribute]:
                    for literal in text_literals(value):
                        index.add(key, "text", literal)
    for finding in report:
        key = node(finding["id"])
        index.types[key] = discrepancy_classes(finding)
        if finding.get("label"):
            index.labels[key] = finding["label"]
            index.add(key, "label", finding["label"])
    index.finish()
    return index
