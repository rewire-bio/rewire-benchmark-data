"""Unit tests for comparison grouping by aggregation and scoring conditions in kb/discrepancies.py
and scripts/kg/contradictions.py (the two derivations must stay identical)."""
from __future__ import annotations

import ast
import json
import sqlite3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "kb"))

import discrepancies  # noqa: E402


class ConditionsAndAggregation(unittest.TestCase):
    def test_parity_between_kb_and_kg_ignored_condition_keys(self):
        tree = ast.parse((ROOT / "scripts" / "kg" / "contradictions.py").read_text("utf-8"))
        kg_keys = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "IGNORED_CONDITION_KEYS" for t in node.targets):
                if isinstance(node.value, ast.Call) and node.value.args:
                    kg_keys = frozenset(ast.literal_eval(node.value.args[0]))
        self.assertEqual(discrepancies.IGNORED_CONDITION_KEYS, kg_keys)

    def test_condition_key_normalization(self):
        self.assertEqual(discrepancies.condition_key(None), "")
        self.assertEqual(discrepancies.condition_key({}), "")
        self.assertEqual(discrepancies.condition_key({"participant_id": "425s", "submission": "T1201TS425_1", "tp": 10}), "")
        a = discrepancies.condition_key({"participant_id": "425s", "threshold": "0.5", "round": "CASP16"})
        b = discrepancies.condition_key({"round": "CASP16", "threshold": "0.5", "submission_id": "sub-9", "clashes": 2})
        self.assertEqual(a, b)
        self.assertEqual(a, '{"round":"CASP16","threshold":"0.5"}')
        self.assertEqual(discrepancies.condition_key("held-out chromosomes"), "held-out chromosomes")

    def test_distinct_conditions_and_aggregation_stay_in_separate_groups(self):
        db = sqlite3.connect(":memory:")
        self.addCleanup(db.close)
        db.executescript("""
            CREATE TABLE record (id TEXT PRIMARY KEY, kind TEXT, name TEXT, description TEXT, status TEXT, facets TEXT, attribute_order TEXT, extra TEXT, top_extra TEXT);
            CREATE TABLE link (from_id TEXT, position INTEGER, relation TEXT, to_id TEXT, extra TEXT);
            CREATE TABLE record_source (record_id TEXT, position INTEGER, source_id TEXT);
            CREATE TABLE source_study (source_id TEXT, study_id TEXT);
        """)
        for table, cols in discrepancies.COLUMNS.items():
            col_names = ["id TEXT PRIMARY KEY"]
            if table == "system":
                col_names += ["parent_id TEXT", "root_id TEXT"]
            elif table == "evaluation":
                col_names += ["origin TEXT", "adaptation TEXT", "system_id TEXT", "assessment_id TEXT"]
            elif table == "source":
                col_names += ["doi TEXT", "url TEXT", "retrieved_at TEXT"]
            elif table == "observation":
                col_names += ["metric TEXT", "direction TEXT", "unit TEXT", "value REAL", "value_text TEXT", "printed_value TEXT",
                              "metric_qualifier TEXT", "aggregation TEXT", "scoring_conditions TEXT", "source_locator TEXT", "evaluation_id TEXT", "study_id TEXT"]
            seen = {c.split()[0] for c in col_names}
            for _, col, sql_t in cols:
                if col not in seen:
                    seen.add(col)
                    col_names.append(f"{col} {sql_t}")
            db.execute(f"CREATE TABLE {table} ({', '.join(col_names)})")

        for rec in [
            ("src-1", "source", "S1", "d", "source_checked", "{}", "[]", "{}", "{}"),
            ("m1", "model", "Model 1", "d", "source_checked", "{}", "[]", "{}", "{}"),
            ("m2", "model", "Model 2", "d", "source_checked", "{}", "[]", "{}", "{}"),
            ("p1", "protocol", "Protocol 1", "d", "source_checked", "{}", "[]", "{}", "{}"),
            ("d1", "dataset", "Dataset 1", "d", "source_checked", "{}", "[]", "{}", "{}"),
        ]:
            db.execute("INSERT INTO record VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rec)
        db.execute("INSERT INTO source (id, doi, url, retrieved_at) VALUES ('src-1', '10.1/s1', 'https://example.org/s1', '2026-01-01')")
        db.execute("INSERT INTO source_study VALUES ('src-1', 'doi:10.1/s1')")

        rows = [
            ("e1", "m1", "0.9", "median", {"threshold": 0.5, "participant_id": "a"}),
            ("e2", "m2", "0.7", "median", {"threshold": 0.5, "participant_id": "b"}),
            ("e3", "m1", "0.4", "mean", {"threshold": 0.5, "participant_id": "c"}),
            ("e4", "m2", "0.8", "mean", {"threshold": 0.5, "participant_id": "d"}),
            ("e5", "m1", "0.6", "median", {"threshold": 0.9, "submission": "x"}),
            ("e6", "m2", "0.5", "median", {"threshold": 0.9, "submission": "y"}),
        ]
        for i, (eid, mid, val, agg, cond) in enumerate(rows):
            rid = f"r-{i}"
            db.execute("INSERT INTO record VALUES (?, 'evaluation', ?, 'd', 'source_checked', '{}', '[]', '{}', '{}')", (eid, eid))
            db.execute("INSERT INTO record VALUES (?, 'result', ?, 'd', 'source_checked', '{}', '[]', '{}', '{}')", (rid, rid))
            db.execute("INSERT INTO evaluation (id, origin, system_id, assessment_id) VALUES (?, 'author_reported', ?, 'p1')", (eid, mid))
            db.execute("INSERT INTO link VALUES (?, 0, 'system', ?, NULL)", (eid, mid))
            db.execute("INSERT INTO link VALUES (?, 1, 'assessment', 'p1', NULL)", (eid,))
            db.execute("INSERT INTO link VALUES (?, 2, 'data', 'd1', NULL)", (eid,))
            db.execute("INSERT INTO link VALUES (?, 0, 'evaluation', ?, NULL)", (rid, eid))
            db.execute("INSERT INTO record_source VALUES (?, 0, 'src-1')", (rid,))
            db.execute(
                "INSERT INTO observation (id, metric, direction, unit, value, value_text, aggregation, scoring_conditions, evaluation_id) "
                "VALUES (?, 'auroc', 'higher', 'unitless', ?, ?, ?, ?, ?)",
                (rid, float(val), val, agg, "\x00" + json.dumps(cond), eid),
            )

        g = discrepancies.Graph(db)
        ix = discrepancies.Index(g, {"https://benchmarks.rewire.it/vocab/metric/auroc": discrepancies.HIGHER})
        items = discrepancies.comparisons(ix)
        self.assertEqual(len(items), 3)
        self.assertEqual(
            {(c.aggregation, c.conditions, float(c.value_a), float(c.value_b)) for c in items},
            {
                ("median", '{"threshold":0.5}', 0.9, 0.7),
                ("mean", '{"threshold":0.5}', 0.4, 0.8),
                ("median", '{"threshold":0.9}', 0.6, 0.5),
            },
        )


if __name__ == "__main__":
    unittest.main()
