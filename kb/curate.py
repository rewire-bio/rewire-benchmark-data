"""Load the curation files into the knowledge base and create the comparison views.

Usage: python3 kb/curate.py [--db kb/build/kb.sqlite]

The record store says what each source reported. The curation files in kb/curation/ say what the
store never could: which protocols in different papers are the same test (settings), which
released checkpoint a system is (checkpoints), and which differences are worth a look (leads).

Tables
  setting            one test that different papers could run and get comparable numbers on
  protocol_setting   a protocol's place in a setting, graded same, near or related, with the stated differences
  checkpoint         one released set of weights: parameters and context as numbers, licences, addresses
  grounding          for one result: the exact system that was run (family, size, version, scoring variant) and
                     the subset of the data the number is for. Both are free text in the record store
  difference_review  what a review concluded about one difference between studies, and why
  lead               a disagreement someone or something has noticed, with its state

Views
  setting_observation_v   every result that falls in a setting, with its grade
  setting_cell_v          one row per setting, model or method, metric and study: the values that study reports
  setting_spread_v        settings where one model or method has values from two or more studies, and how far apart
  setting_pair_v          pairs of models that two or more studies both measured in a setting, and how each study orders them
  grounded_cell_v         as setting_cell_v, but one row per exact system and subset, for results that have grounding
  grounded_difference_v   the same exact system, setting, subset and metric with values from two or more studies that differ
  grounded_lead_v         those differences with the verdict a review gave each: lead, artefact or unresolved. A difference
                          no review covers shows as "not reviewed", which is how a new one is noticed
"""
import argparse
import json
import os
import sqlite3

TABLES = {
    "setting": ("kb/curation/settings.jsonl", ["id", "name", "definition", "cluster", "task_id", "basis"]),
    "protocol_setting": ("kb/curation/protocol_settings.jsonl", ["protocol_id", "setting_id", "grade", "metric", "differences", "why", "basis"]),
    "checkpoint": ("kb/curation/checkpoints.jsonl", ["id", "model_id", "checkpoint", "parameters", "context_length", "context_unit", "code_licence", "weights_licence", "code_url", "weights_url", "gated", "released", "evidence"]),
    "grounding": ("kb/curation/grounding.jsonl", ["observation_id", "system_key", "system_label", "system_basis", "adaptation", "subset", "subset_basis", "confidence"]),
    "difference_review": ("kb/curation/difference_reviews.jsonl", ["setting_id", "system_key", "subset", "metric", "verdict", "why", "basis"]),
    "lead": ("kb/curation/leads.jsonl", ["id", "setting_id", "kind", "model", "model_id", "metric", "values", "note", "state", "basis"]),
}
VIEWS = {
    "setting_observation_v": """
        SELECT ps.setting_id, ps.grade, o.*
        FROM protocol_setting ps JOIN observation_v o ON o.assessment_id = ps.protocol_id
        WHERE o.value IS NOT NULL AND o.status NOT IN ('disputed', 'excluded', 'superseded')
          AND (ps.metric IS NULL OR o.metric = ps.metric)""",
    "setting_cell_v": """
        SELECT setting_id, root_id, root_name, metric, study_id, min(grade) AS best_grade, count(*) AS results, min(value) AS lowest, max(value) AS highest
        FROM setting_observation_v WHERE grade IN ('same', 'near') GROUP BY setting_id, root_id, metric, study_id""",
    "setting_spread_v": """
        SELECT setting_id, root_id, root_name, metric, count(*) AS studies, min(lowest) AS lowest, max(highest) AS highest, max(highest) - min(lowest) AS spread
        FROM setting_cell_v GROUP BY setting_id, root_id, metric HAVING count(*) >= 2""",
    "setting_pair_v": """
        SELECT a.setting_id, a.metric, a.root_name AS first, b.root_name AS second, a.root_id AS first_id, b.root_id AS second_id,
               count(*) AS studies, sum(a.highest > b.highest) AS first_ahead, sum(a.highest < b.highest) AS second_ahead
        FROM setting_cell_v a JOIN setting_cell_v b ON a.setting_id = b.setting_id AND a.metric = b.metric AND a.study_id = b.study_id AND a.root_id < b.root_id
        GROUP BY a.setting_id, a.metric, a.root_id, b.root_id HAVING count(*) >= 2""",
    "grounded_cell_v": """
        SELECT so.setting_id, g.system_key, min(g.system_label) AS system_label, g.subset, so.metric, so.study_id, min(so.grade) AS best_grade,
               count(*) AS results, min(so.value) AS lowest, max(so.value) AS highest
        FROM setting_observation_v so JOIN grounding g ON g.observation_id = so.id
        WHERE so.grade IN ('same', 'near') AND g.system_key NOT LIKE '%unspecified' AND g.subset != 'unspecified'
        GROUP BY so.setting_id, g.system_key, g.subset, so.metric, so.study_id""",
    "grounded_difference_v": """
        SELECT setting_id, system_key, min(system_label) AS system_label, subset, metric, count(*) AS studies,
               min(lowest) AS lowest, max(highest) AS highest, max(highest) - min(lowest) AS spread
        FROM grounded_cell_v GROUP BY setting_id, system_key, subset, metric
        HAVING count(*) >= 2 AND max(highest) - min(lowest) > 0.005""",
    "grounded_lead_v": """
        SELECT d.*, COALESCE(r.verdict, 'not reviewed') AS verdict, r.why
        FROM grounded_difference_v d LEFT JOIN difference_review r
          ON r.setting_id = d.setting_id AND r.system_key = d.system_key AND r.subset = d.subset AND r.metric = d.metric""",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="kb/build/kb.sqlite")
    db = sqlite3.connect(parser.parse_args().db)
    for table, (path, columns) in TABLES.items():
        db.execute(f"DROP TABLE IF EXISTS {table}")
        db.execute(f"CREATE TABLE {table} ({', '.join(f'[{c}]' for c in columns)})")
        rows = [json.loads(line) for line in open(path) if line.strip()] if os.path.exists(path) else []
        db.executemany(f"INSERT INTO {table} VALUES ({', '.join('?' * len(columns))})",
                       [[json.dumps(r.get(c), ensure_ascii=False) if isinstance(r.get(c), (list, dict)) else r.get(c) for c in columns] for r in rows])
        print(f"{table}: {len(rows)}")
    missing = db.execute("SELECT count(*) FROM protocol_setting ps WHERE NOT EXISTS (SELECT 1 FROM record r WHERE r.id = ps.protocol_id)").fetchone()[0]
    unknown = db.execute("SELECT count(*) FROM checkpoint c WHERE NOT EXISTS (SELECT 1 FROM record r WHERE r.id = c.model_id)").fetchone()[0]
    if missing or unknown:
        raise SystemExit(f"{missing} protocol links and {unknown} checkpoints point at records that do not exist")
    for name, body in VIEWS.items():
        db.execute(f"DROP VIEW IF EXISTS {name}")
        db.execute(f"CREATE VIEW {name} AS {body}")
    db.commit()
    for label, query in [
        ("results in a setting", "SELECT count(*) FROM setting_observation_v"),
        ("model and setting combinations with two or more studies", "SELECT count(*) FROM setting_spread_v"),
        ("pairs of models measured together by two or more studies", "SELECT count(*) FROM setting_pair_v"),
        ("of those pairs, studies disagree on the order", "SELECT count(*) FROM setting_pair_v WHERE first_ahead > 0 AND second_ahead > 0"),
        ("results with an exact system and subset", "SELECT count(*) FROM grounding"),
        ("same exact system, setting, subset and metric, different value in another study", "SELECT count(*) FROM grounded_difference_v"),
        ("of those, judged a lead worth raising", "SELECT count(*) FROM grounded_lead_v WHERE verdict = 'lead'"),
        ("of those, not yet reviewed", "SELECT count(*) FROM grounded_lead_v WHERE verdict = 'not reviewed'"),
    ]:
        print(f"{label}: {db.execute(query).fetchone()[0]}")


if __name__ == "__main__":
    main()
