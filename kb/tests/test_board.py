"""Tests for kb/board.py on small synthetic boards. No database is needed:
  python3 -m unittest kb/tests/test_board.py

A board's input is a dict of comparison groups, {(study, test, direction): {model: value}}, and the
models' records, {model: {"name", "kind", "status"}}, as read_groups returns them.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import board  # noqa: E402


def model(name, kind="model", status="source_checked"):
    return {"name": name, "kind": kind, "status": status}


def groups_from(table):
    """{(study, test): {model: value}} with higher better, as board input."""
    return {(study, test, "higher"): dict(values) for (study, test), values in table.items()}


def ranked(groups, records):
    rows, left_out, counts = board.rank(groups, records)
    return {r["name"]: r for r in rows}, {x["name"]: x for x in left_out}, counts


class Fit(unittest.TestCase):
    def test_winner_is_stronger_and_finite(self):
        strength = board.fit({"s1": {("a", "b"): (1.0, 0.0)}})
        self.assertGreater(strength["a"], strength["b"])
        # The imagined draws keep one win from giving an infinite strength.
        self.assertLess(strength["a"], 10)

    def test_geometric_mean_is_one(self):
        strength = board.fit({"s1": {("a", "b"): (1.0, 0.0), ("b", "c"): (0.7, 0.3)}, "s2": {("a", "c"): (0.4, 0.6)}})
        product = 1.0
        for value in strength.values():
            product *= value
        self.assertAlmostEqual(product, 1.0, places=6)

    def test_draw_gives_equal_strength(self):
        strength = board.fit({"s1": {("a", "b"): (0.5, 0.5)}})
        self.assertAlmostEqual(strength["a"], strength["b"], places=6)

    def test_leaving_out_a_study_drops_its_verdicts(self):
        per_study = {"s1": {("a", "b"): (1.0, 0.0)}, "s2": {("a", "b"): (0.0, 1.0)}}
        self.assertGreater(board.fit(per_study, leave_out="s2")["a"], 1.0)
        self.assertLess(board.fit(per_study, leave_out="s1")["a"], 1.0)


class Verdicts(unittest.TestCase):
    def test_a_study_counts_once_however_many_groups(self):
        groups = groups_from({**{("s1", f"t{i}"): {"a": 2, "b": 1} for i in range(10)}, ("s2", "t"): {"a": 1, "b": 2}})
        per_study, opponents, by_study = board.verdicts(groups)
        self.assertEqual(per_study["s1"][("a", "b")], (1.0, 0.0))
        self.assertEqual(per_study["s2"][("a", "b")], (0.0, 1.0))
        self.assertEqual(by_study["a"], {"s1": 10, "s2": 1})
        strength = board.fit(per_study)
        self.assertAlmostEqual(strength["a"], strength["b"], places=6)

    def test_lower_is_better_and_ties_split(self):
        groups = {("s1", "t1", "lower"): {"a": 1, "b": 2}, ("s1", "t2", "lower"): {"a": 3, "b": 3}}
        per_study, _, _ = board.verdicts(groups)
        self.assertEqual(per_study["s1"][("a", "b")], (0.75, 0.25))


class Studies(unittest.TestCase):
    def test_study_names_sharing_a_part_are_one_study(self):
        groups = groups_from({("x + y", "t1"): {"a": 1, "b": 2}, ("y + z", "t2"): {"a": 1, "c": 2}, ("w", "t3"): {"b": 1, "c": 2}})
        merged = board.merge_studies(groups)
        self.assertEqual(sorted({study for study, _, _ in merged}), ["w", "x + y + z"])

    def test_same_group_in_merged_study_keeps_best_value(self):
        groups = groups_from({("x + y", "t"): {"a": 1}, ("y", "t"): {"a": 3, "b": 2}})
        merged = board.merge_studies(groups)
        self.assertEqual(merged[("x + y", "t", "higher")], {"a": 3, "b": 2})


class Duplicates(unittest.TestCase):
    def test_same_squashed_name_is_one_row(self):
        records = {"m2": model("ESM-2"), "m1": model("esm 2", kind="configuration"), "x": model("ESM-1b")}
        groups = groups_from({("s1", "t"): {"m2": 1, "m1": 3, "x": 2}})
        merged, record_ids = board.merge_duplicates(groups, records)
        self.assertEqual(merged[("s1", "t", "higher")], {"m2": 3, "x": 2})
        self.assertEqual(record_ids["m2"], ["m1", "m2"])

    def test_configurations_alone_are_not_merged_and_excluded_records_stay_apart(self):
        records = {"c1": model("Lookups", kind="configuration"), "c2": model("lookups", kind="configuration"),
                   "m": model("CADD"), "e": model("CADD", status="excluded")}
        groups = groups_from({("s1", "t"): {"c1": 1, "c2": 2, "m": 3, "e": 4}})
        merged, _ = board.merge_duplicates(groups, records)
        self.assertEqual(set(merged[("s1", "t", "higher")]), {"c1", "c2", "m", "e"})


class Rules(unittest.TestCase):
    def three_studies(self, extra=None):
        table = {("s1", "t"): {"a": 3, "b": 2, "c": 1}, ("s2", "t"): {"a": 3, "b": 2, "c": 1}, ("s3", "t"): {"a": 3, "b": 2, "c": 1}}
        table.update(extra or {})
        return groups_from(table)

    def test_consistent_order_gets_single_positions(self):
        rows, _, counts = ranked(self.three_studies(), {m: model(m) for m in "abc"})
        self.assertEqual([rows[m]["positions"] for m in "abc"], [[1, 1], [2, 2], [3, 3]])
        self.assertEqual(counts["ranked"], 3)
        for m in "abc":
            low, high = rows[m]["interval"]
            self.assertLessEqual(low, rows[m]["strength"])
            self.assertLessEqual(rows[m]["strength"], high)

    def test_order_that_one_study_reverses_shares_positions(self):
        groups = groups_from({("s1", "t"): {"a": 2, "b": 1}, ("s2", "t"): {"a": 2, "b": 1}, ("s3", "t"): {"a": 1, "b": 3}})
        rows, _, _ = ranked(groups, {"a": model("a"), "b": model("b")})
        self.assertEqual(rows["a"]["positions"], [1, 2])
        self.assertEqual(rows["b"]["positions"], [1, 2])

    def test_one_study_model_is_fitted_but_not_ranked(self):
        rows, left_out, counts = ranked(self.three_studies({("s1", "u"): {"a": 1, "solo": 9}}), {m: model(m) for m in ["a", "b", "c", "solo"]})
        self.assertNotIn("solo", rows)
        self.assertEqual(left_out["solo"]["reason"], board.ONE_STUDY)
        self.assertEqual(left_out["solo"]["study_ids"], ["s1"])
        self.assertEqual(counts["one_study"], 1)
        self.assertEqual(rows["a"]["opponents"], 3)

    def test_records_that_are_not_models_are_not_ranked(self):
        records = {"a": model("a"), "b": model("b", kind="method"), "c": model("c", kind="configuration")}
        rows, left_out, counts = ranked(self.three_studies(), records)
        self.assertEqual(sorted(rows), ["a", "b"])
        self.assertEqual(left_out["c"]["reason"], board.NOT_A_MODEL)
        self.assertEqual(counts["not_a_model"], 1)
        records["c"] = model("c", status="excluded")
        rows, left_out, _ = ranked(self.three_studies(), records)
        self.assertEqual(left_out["c"]["reason"], board.NOT_A_MODEL)

    def test_models_never_compared_with_the_main_group_are_not_ranked(self):
        extra = {("s4", "t"): {"x": 2, "y": 1}, ("s5", "t"): {"x": 2, "y": 1}}
        rows, left_out, counts = ranked(self.three_studies(extra), {m: model(m) for m in "abcxy"})
        self.assertEqual(sorted(rows), ["a", "b", "c"])
        self.assertEqual(left_out["x"]["reason"], board.NOT_CONNECTED)
        self.assertEqual(counts["not_connected"], 2)

    def test_fewer_than_two_rows_gives_an_empty_board(self):
        groups = groups_from({("s1", "t"): {"a": 2, "b": 1}, ("s2", "t"): {"a": 2, "c": 1}})
        rows, left_out, counts = ranked(groups, {m: model(m) for m in "abc"})
        self.assertEqual(rows, {})
        self.assertEqual(left_out["a"]["reason"], board.TOO_FEW)
        self.assertEqual(counts["models"], counts["one_study"] + counts["too_few"])
        self.assertIn("No ranking", board.summary(counts))

    def test_basis_flags_a_row_resting_mostly_on_one_study(self):
        groups = self.three_studies({("s1", f"u{i}"): {"a": 2, "b": 1} for i in range(14)})
        rows, _, _ = ranked(groups, {m: model(m) for m in "abc"})
        self.assertEqual(rows["b"]["basis"], "mostly one study")
        self.assertEqual(rows["c"]["basis"], "several studies")
        self.assertEqual(rows["b"]["studies"], {"s1": 16, "s2": 2, "s3": 2})
        self.assertEqual(rows["b"]["comparisons"], 20)

    def test_counts_add_up(self):
        groups = self.three_studies({("s1", "u"): {"a": 1, "solo": 2}, ("s4", "t"): {"x": 2, "y": 1}, ("s5", "t"): {"x": 2, "y": 1}})
        records = {m: model(m) for m in ["a", "b", "c", "solo", "x", "y"]}
        records["c"]["kind"] = "baseline"
        _, _, counts = ranked(groups, records)
        self.assertEqual(counts["models"], sum(counts[k] for k in ("ranked", "one_study", "not_a_model", "not_connected", "too_few")))
        self.assertEqual(counts["studies"], 5)
        self.assertEqual(counts["groups"], 6)


if __name__ == "__main__":
    unittest.main()
