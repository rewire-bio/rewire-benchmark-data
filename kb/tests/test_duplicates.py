"""Tests for kb/duplicates.py on the real store.

Run after building the database (python3 kb/migrate.py):
  python3 -m unittest kb/tests/test_duplicates.py
KB_DB names another database, for example one built from a bundle's commit.

The expected answers are worked out here from plain SQL and a separate copy of the name rules, not
with the module's helpers. Search hits cannot be predicted without the ranking, so for them the
test checks the rules a hit must pass (matched on its name, enough words in common, at most three)
rather than which hits come back.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
import unittest
from pathlib import Path

KB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KB))
from duplicates import Duplicates, name_overlap  # noqa: E402
from queries import Records  # noqa: E402

DB = os.environ.get("KB_DB", str(KB / "build" / "kb.sqlite"))
PER_KIND = 20
WORD = re.compile(r"[^\W_]+")


def squashed(text: str) -> str:
    return "".join(WORD.findall(text.casefold()))


def stems(text: str) -> set[str]:
    out = set()
    for word in WORD.findall(text.casefold()):
        for suffix in ("ing", "ed", "es", "e", "s"):
            if len(word) - len(suffix) >= 4 and word.endswith(suffix):
                word = word[: -len(suffix)]
                break
        out.add(word)
    return out


def overlap(a: str, b: str) -> float:
    if squashed(a) == squashed(b):
        return 1.0
    wa, wb = stems(a), stems(b)
    if not wa or not wb:
        return 0.0
    share = lambda xs, ys: sum(x in ys or (len(x) >= 4 and any(y.startswith(x) for y in ys)) for x in xs) / len(xs)
    return max(share(wa, wb), share(wb, wa))


def draft_of(record: tuple, new_id: str, name: str | None = None) -> dict:
    record_id, kind, record_name, description = record
    return {"id": new_id, "kind": kind, "name": record_name if name is None else name, "description": description or "",
            "status": "discovered", "facets": {}, "source_ids": [], "links": [], "attributes": {}}


@unittest.skipUnless(Path(DB).exists(), f"no database at {DB}; run python3 kb/migrate.py")
class DuplicatesOnTheStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = Records(DB, discrepancies="none")
        cls.tool = Duplicates(cls.records)
        public = cls.records.public
        rows = [r for r in cls.records.db.execute("SELECT id, kind, name, description FROM record") if r[0] in public]
        cls.by_name: dict[str, list[tuple]] = {}
        for row in rows:
            if squashed(row[2] or ""):
                cls.by_name.setdefault(squashed(row[2]), []).append(row)
        by_kind: dict[str, list[tuple]] = {}
        for row in sorted(rows, key=lambda r: hashlib.sha256(r[0].encode()).hexdigest()):
            if squashed(row[2] or ""):
                by_kind.setdefault(row[1], []).append(row)
        cls.sample = [row for kind in sorted(by_kind) for row in by_kind[kind][:PER_KIND]]

    def expected_same_name(self, kind: str, name: str) -> list[tuple]:
        same = self.by_name.get(squashed(name), [])
        return sorted(same, key=lambda r: (r[1] != kind, r[0]))

    def check_hits(self, draft: dict, entry: dict) -> None:
        """Rules every reported duplicate must satisfy, whichever rule found it."""
        searched = [d for d in entry["possible_duplicates"] if "search" in d["match"]]
        self.assertEqual([d["rank"] for d in searched], list(range(1, len(searched) + 1)))
        self.assertLessEqual(len(searched), 3)
        for d in entry["possible_duplicates"]:
            self.assertNotEqual(d["id"], draft["id"])
            self.assertEqual(d["in"], "release")
            kind, label = self.records.name_of(d["id"])
            self.assertEqual((d["kind"], d["label"]), (kind, label))
            if "search" in d["match"]:
                self.assertGreaterEqual(overlap(draft["name"], label), 0.5, d)
            if "same name" in d["match"]:
                self.assertEqual(squashed(label), squashed(draft["name"]), d)

    def test_a_copy_under_a_new_id_reports_the_original(self) -> None:
        self.assertGreaterEqual(len(self.sample), 200)
        drafts = [draft_of(row, f"duplicate-probe-{i}") for i, row in enumerate(self.sample)]
        counts = {"drafts": len(drafts), "original reported": 0, "original beyond the cap of 10": 0,
                  "found by search too": 0}
        for row, draft in zip(self.sample, drafts):
            entry = self.tool.check([draft])[0]
            self.check_hits(draft, entry)
            same = self.expected_same_name(row[1], row[2])
            reported = {d["id"]: d for d in entry["possible_duplicates"]}
            for expected in same[:10]:
                self.assertIn(expected[0], reported, (draft["name"], expected))
                self.assertIn("same name", reported[expected[0]]["match"])
            self.assertEqual({d for d, e in reported.items() if "same name" in e["match"]}, {r[0] for r in same[:10]})
            self.assertEqual(entry.get("same_name_omitted", 0), max(0, len(same) - 10))
            if row[0] in reported:
                counts["original reported"] += 1
                counts["found by search too"] += reported[row[0]]["match"] == "same name, search"
            else:
                self.assertNotIn(row[0], [r[0] for r in same[:10]])
                counts["original beyond the cap of 10"] += 1
        print(f"\n{counts}", file=sys.stderr)
        self.assertEqual(counts["original reported"] + counts["original beyond the cap of 10"], len(drafts))

    def test_a_common_name_is_capped_at_ten_same_kind_first(self) -> None:
        common = [rows for rows in self.by_name.values() if len(rows) > 10 and len({r[1] for r in rows}) > 1]
        self.assertTrue(common)
        for rows in common[:20]:
            # The least common kind among them, so the ordering by kind is visible.
            kind = min({r[1] for r in rows}, key=lambda k: (sum(r[1] == k for r in rows), k))
            row = next(r for r in rows if r[1] == kind)
            entry = self.tool.check([draft_of(row, "duplicate-common")])[0]
            same = [d["id"] for d in entry["possible_duplicates"] if "same name" in d["match"]]
            expected = self.expected_same_name(kind, row[2])
            self.assertEqual(sorted(same), sorted(r[0] for r in expected[:10]))
            self.assertEqual(entry["same_name_omitted"], len(rows) - 10)
            self.assertTrue(all(r[1] == kind for r in expected[: sum(r[1] == kind for r in rows)]))

    def test_case_and_punctuation_do_not_hide_a_duplicate(self) -> None:
        variants = 0
        for i, row in enumerate(self.sample):
            if squashed(row[2]) == row[2]:
                continue
            name = squashed(row[2]).upper()
            entry = self.tool.check([draft_of(row, f"duplicate-variant-{i}", name)])[0]
            same = self.expected_same_name(row[1], row[2])
            if row[0] in [r[0] for r in same[:10]]:
                self.assertIn(row[0], [d["id"] for d in entry["possible_duplicates"]], name)
                variants += 1
        self.assertGreater(variants, 100)

    def test_a_name_no_record_shares_reports_nothing(self) -> None:
        for i, row in enumerate(self.sample):
            name = f"Qzxv{i:04d} Wkjhplom Vrrnq"
            entry = self.tool.check([draft_of(row, f"duplicate-none-{i}", name)])[0]
            self.assertEqual(entry["possible_duplicates"], [], name)
            self.assertNotIn("same_name_omitted", entry)

    def test_search_hits_need_half_the_words(self) -> None:
        # Two of the original's words among six of no record's: a third of the draft's words, and
        # often under half of the original's, so a search hit on them must pass name_overlap.
        checked = 0
        for i, row in enumerate(self.sample):
            if len(stems(row[2])) < 4:
                continue
            kept = " ".join(WORD.findall(row[2])[:2])
            name = f"{kept} Qzxv{i:04d} Wkjhplom Vrrnq Plokij Mnbvcx"
            draft = draft_of(row, f"duplicate-half-{i}", name)
            entry = self.tool.check([draft])[0]
            self.check_hits(draft, entry)
            checked += 1
        self.assertGreater(checked, 20)

    def test_other_drafts_of_the_call(self) -> None:
        drafts = [
            {"id": "draft-a", "kind": "model", "name": "Qzxv-Wkjh Plom"},
            {"id": "draft-b", "kind": "dataset", "name": "qzxvwkjh plom"},
            {"id": "draft-c", "kind": "model", "name": "Qzxv Wkjh Plom Vrrnq Ghtyu"},
            {"id": "draft-d", "kind": "model", "name": "Mnbvcx"},
        ]
        found = {e["id"]: [(d["id"], d["in"], d["kind"], d["match"]) for d in e["possible_duplicates"]]
                 for e in self.tool.check(drafts)}
        # All three of draft-a's words are in draft-c.
        self.assertEqual(found["draft-a"], [("draft-b", "draft", "dataset", "same name"), ("draft-c", "draft", "model", "near name")])
        # One of draft-b's two words is in draft-c, and "qzxv" starts "qzxvwkjh": half either way.
        self.assertEqual(found["draft-b"], [("draft-a", "draft", "model", "same name"), ("draft-c", "draft", "model", "near name")])
        self.assertEqual(found["draft-c"], [("draft-a", "draft", "model", "near name"), ("draft-b", "draft", "dataset", "near name")])
        self.assertEqual(found["draft-d"], [])

    def test_a_draft_the_server_would_refuse(self) -> None:
        row = self.sample[0]
        entry = self.tool.check([draft_of(row, row[0]), {"kind": "model", "name": "x"}])
        self.assertIn("already in the store", entry[0]["error"])
        self.assertIn("non-empty string", entry[1]["error"])


class NameOverlap(unittest.TestCase):
    def test_rules(self) -> None:
        self.assertEqual(name_overlap("ESM-2", "esm2"), 1.0)
        self.assertEqual(name_overlap("Evo 2", "Evo 2 7B"), 1.0)
        self.assertEqual(name_overlap("foo bar baz qux", "foo zzz"), 0.5)
        self.assertLess(name_overlap("alpha beta gamma", "alpha delta epsilon"), 0.5)
        self.assertEqual(name_overlap("Nucl", "Nucleotide Transformer"), 1.0)
        self.assertEqual(name_overlap("Nuc", "Nucleotide Transformer"), 0.0)
        self.assertEqual(name_overlap("splicing", "splice"), 1.0)
        self.assertEqual(name_overlap("", "x"), 0.0)
        for a, b in [("ESM-2", "esm2"), ("foo bar baz qux", "foo zzz"), ("Nucl", "Nucleotide Transformer"), ("splicing", "splice")]:
            self.assertEqual(name_overlap(a, b), overlap(a, b))


if __name__ == "__main__":
    unittest.main()
