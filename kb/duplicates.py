"""Possible duplicates of draft records, found in kb.sqlite with the rules rdf-kg-mcp's draft overlay
applies (src/rdf_kg_mcp/drafts.py at v0.4.0, DraftOverlay.possible_duplicates and name_overlap).

A draft is a record as the store writes it, the shape the intake agent gives draft_upsert. Only its
id, kind and name are read. For each draft the possible duplicates are, in this order:

  search     Search (kb/search.py, ranked as the graph ranks) for the draft's name, limited to the
             class of its kind when the kind is known and unfiltered otherwise, and look at the first
             20 hits. A hit counts if it matched on its name (not only on description or text
             attributes) and name_overlap of the two names is at least 0.5. The first 3 that count
             are kept, with their rank among those that count and their search score.
  same name  Every public record (and discrepancy, when the database is given a discrepancies file)
             whose squashed name equals the draft's: case folded letters and digits only, so
             "ESM-2", "esm 2" and "ESM2" are the same name. Any kind; records of the draft's kind
             first, then by ID; at most 10, with same_name_omitted counting the rest. A record
             found by both rules has match "same name, search".
  drafts     The other drafts of the same call, by ID: "same name" as above, or "near name" when
             name_overlap is at least 0.5.

name_overlap(a, b) is 1.0 when the squashed names are equal; otherwise the larger of the share of
a's words found in b and of b's words found in a. Words are search words (case folded runs of
letters and digits with one English suffix stripped), and a word is found when the other name
has it, or has a word that starts with it and the word has at least four letters.

The draft itself (its own ID) is never its own duplicate. The graph held only public records, so
only public records are candidates here too; "in" stays "release" so callers that read the
server's output need no change. A draft whose ID is missing or already in the database gets an
error instead, as the server refuses such a draft_upsert.
"""
from __future__ import annotations

import json
from pathlib import Path

from search import squash, words

SEARCH_HITS = 3
SEARCH_POOL = 20
MIN_NAME_COVERAGE = 0.5
MAX_SAME_NAME = 10


def name_overlap(a: str, b: str) -> float:
    if squash(a) == squash(b):
        return 1.0
    wa, wb = set(words(a)), set(words(b))
    if not wa or not wb:
        return 0.0

    def found(word: str, others: set[str]) -> bool:
        return word in others or (len(word) >= 4 and any(o.startswith(word) for o in others))

    return max(sum(found(w, wb) for w in wa) / len(wa), sum(found(w, wa) for w in wb) / len(wb))


class Duplicates:
    """The duplicate rules over one kb.queries.Records."""

    def __init__(self, records) -> None:
        self.records = records
        self._names: dict[str, list[str]] | None = None

    def kind_of(self, key: str) -> str | None:
        """The record kind of an indexed IRI; None for a discrepancy, as the graph gives no kind."""
        record_id = self.record_id(key)
        return self.records.name_of(record_id)[0] if record_id is not None else None

    def record_id(self, key: str) -> str | None:
        from queries import ID
        rest = key[len(ID):] if key.startswith(ID) else None
        return rest if rest and "/" not in rest else None

    @property
    def names(self) -> dict[str, list[str]]:
        """Squashed name to the IDs of the indexed records and discrepancies carrying it."""
        if self._names is None:
            names: dict[str, list[str]] = {}
            for key, label in self.records.index.labels.items():
                record_id = self.record_id(key)
                if record_id is not None and (squashed := squash(label)):
                    names.setdefault(squashed, []).append(record_id)
            self._names = names
        return self._names

    def possible(self, draft: dict, drafts: dict[str, dict]) -> tuple[list[dict], int]:
        label = draft.get("name")
        if not isinstance(label, str) or not squash(label):
            return [], 0
        own, kind = draft.get("id"), draft.get("kind")
        found: dict[str, dict] = {}
        known = isinstance(kind, str) and kind in self.records.kind_class
        try:
            hits = self.records.search(label, types=[kind] if known else None, limit=SEARCH_POOL)["results"]
        except ValueError:
            hits = []
        index = self.records.index
        rank = 0
        for hit in hits:
            record_id = self.record_id(hit["iri"])
            if record_id is None or record_id == own:
                continue
            names = [index.labels[hit["iri"]]] if hit["iri"] in index.labels else []
            if not {"label", "alias"} & set(hit["matched"]) or not any(
                    name_overlap(label, name) >= MIN_NAME_COVERAGE for name in names):
                continue
            rank += 1
            if rank > SEARCH_HITS:
                break
            found[record_id] = {"id": record_id, "in": "release", "kind": self.kind_of(hit["iri"]), "label": hit["label"],
                                "match": "search", "rank": rank, "score": hit["score"]}
        key = squash(label)
        same = [(self.kind_of(self._iri(rid)), rid) for rid in self.names.get(key, ()) if rid != own]
        same.sort(key=lambda pair: (pair[0] != kind, pair[1]))
        for found_kind, record_id in same[:MAX_SAME_NAME]:
            entry = found.setdefault(record_id, {"id": record_id, "in": "release", "kind": found_kind,
                                                 "label": index.labels.get(self._iri(record_id))})
            entry["match"] = "same name" if entry.get("match") is None else "same name, search"
        for record_id, other in sorted(drafts.items()):
            other_label = other.get("name")
            if record_id == own or not isinstance(other_label, str):
                continue
            if squash(other_label) == key:
                match = "same name"
            elif name_overlap(label, other_label) >= MIN_NAME_COVERAGE:
                match = "near name"
            else:
                continue
            found[record_id] = {"id": record_id, "in": "draft", "kind": other.get("kind"), "label": other_label, "match": match}
        return list(found.values()), max(0, len(same) - MAX_SAME_NAME)

    @staticmethod
    def _iri(record_id: str) -> str:
        from queries import node
        return node(record_id)

    def check(self, drafts: list[dict]) -> list[dict]:
        """One entry per draft, in the order given: {id, possible_duplicates, same_name_omitted
        (only when above 0)}, or {id, error} for a draft the server would refuse."""
        by_id: dict[str, dict] = {}
        out: list[dict] = []
        for draft in drafts:
            record_id = draft.get("id") if isinstance(draft, dict) else None
            if not isinstance(record_id, str) or not record_id:
                out.append({"id": record_id, "error": "record must have a non-empty string 'id'"})
            elif self.records.name_of(record_id)[0] is not None:
                out.append({"id": record_id, "error": f"{record_id} is already in the store; it can only be changed"})
            else:
                by_id[record_id] = draft
                out.append({"id": record_id})
        for entry in out:
            if "error" in entry:
                continue
            found, omitted = self.possible(by_id[entry["id"]], by_id)
            entry["possible_duplicates"] = found
            if omitted:
                entry["same_name_omitted"] = omitted
        return out


def read_drafts(value: str) -> list[dict]:
    """Drafts from a JSON object or list given inline, or from a file of JSON lines, a JSON list
    or one JSON object; "-" reads standard input."""
    import sys
    text = sys.stdin.read() if value == "-" else value if value.lstrip()[:1] in ("{", "[") else Path(value).read_text("utf-8")
    text = text.strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return parsed if isinstance(parsed, list) else [parsed]
