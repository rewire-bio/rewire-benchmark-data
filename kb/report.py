"""Say what one source adds to the knowledge base and where it disagrees with the others.

Usage: python3 kb/report.py <source id> [--db kb/build/kb.sqlite]

Prints, for the study the source belongs to: what it measured, which of its numbers can be set
beside another study's (same model or method, same setting or protocol, same metric), where those
numbers differ, and which pairs of models it orders differently from other studies. Run
kb/curate.py first: the settings are what make results from different papers comparable.
"""
import argparse
import sqlite3

SHARED = """
WITH mine AS (
  SELECT COALESCE(ps.setting_id, o.assessment_id) AS place, o.root_id, o.root_name, o.metric, min(o.value) AS lowest, max(o.value) AS highest
  FROM observation_v o LEFT JOIN protocol_setting ps ON ps.protocol_id = o.assessment_id AND ps.grade IN ('same', 'near') AND (ps.metric IS NULL OR ps.metric = o.metric)
  WHERE o.study_id = :study AND o.value IS NOT NULL GROUP BY 1, 2, 4),
others AS (
  SELECT COALESCE(ps.setting_id, o.assessment_id) AS place, o.root_id, o.metric, count(DISTINCT o.study_id) AS studies, min(o.value) AS lowest, max(o.value) AS highest
  FROM observation_v o LEFT JOIN protocol_setting ps ON ps.protocol_id = o.assessment_id AND ps.grade IN ('same', 'near') AND (ps.metric IS NULL OR ps.metric = o.metric)
  WHERE o.study_id != :study AND o.value IS NOT NULL AND o.origin != 'paper_compilation' GROUP BY 1, 2, 3)
SELECT mine.place, mine.root_name, mine.metric, mine.lowest, mine.highest, others.studies, others.lowest, others.highest
FROM mine JOIN others USING (place, root_id, metric) ORDER BY max(abs(mine.highest - others.lowest), abs(others.highest - mine.lowest)) DESC
"""
REVERSED = """
WITH cell AS (SELECT setting_id, root_id, root_name, metric, study_id, highest FROM setting_cell_v),
pair AS (SELECT a.setting_id, a.metric, a.study_id, a.root_id AS a, b.root_id AS b, a.root_name AS a_name, b.root_name AS b_name, a.highest > b.highest AS a_ahead
         FROM cell a JOIN cell b ON a.setting_id = b.setting_id AND a.metric = b.metric AND a.study_id = b.study_id AND a.root_id < b.root_id WHERE a.highest != b.highest)
SELECT mine.setting_id, mine.metric, mine.a_name, mine.b_name, mine.a_ahead, count(*) AS other_studies
FROM pair mine JOIN pair other ON other.setting_id = mine.setting_id AND other.metric = mine.metric AND other.a = mine.a AND other.b = mine.b
     AND other.study_id != mine.study_id AND other.a_ahead != mine.a_ahead
WHERE mine.study_id = :study GROUP BY 1, 2, 3, 4, 5 ORDER BY 6 DESC
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_id")
    parser.add_argument("--db", default="kb/build/kb.sqlite")
    args = parser.parse_args()
    db = sqlite3.connect(args.db)
    row = db.execute("SELECT ss.study_id, r.name FROM source_study ss JOIN record r ON r.id = ss.source_id WHERE ss.source_id = ?", (args.source_id,)).fetchone()
    if not row:
        raise SystemExit(f"No source {args.source_id}")
    study = {"study": row[0]}
    results, models, tests = db.execute("SELECT count(*), count(DISTINCT root_id), count(DISTINCT assessment_id) FROM observation_v WHERE study_id = :study", study).fetchone()
    print(f"# {row[1]}\n\nStudy `{row[0]}`: {results} results for {models} models or methods on {tests} tests.\n")
    shared = db.execute(SHARED, study).fetchall()
    print(f"## Numbers another study also reports: {len(shared)}\n")
    if shared:
        print("| Setting or protocol | Model | Metric | This study | Other studies | Their range |\n| --- | --- | --- | --- | --- | --- |")
        for place, name, metric, low, high, studies, other_low, other_high in shared[:40]:
            ours = f"{low:g}" if low == high else f"{low:g} to {high:g}"
            theirs = f"{other_low:g}" if other_low == other_high else f"{other_low:g} to {other_high:g}"
            print(f"| {place} | {name} | {metric} | {ours} | {studies} | {theirs} |")
    reversed_pairs = db.execute(REVERSED, study).fetchall()
    print(f"\n## Pairs it orders differently from another study: {len(reversed_pairs)}\n")
    for setting, metric, a, b, a_ahead, others in reversed_pairs[:40]:
        first, second = (a, b) if a_ahead else (b, a)
        print(f"- {setting}, {metric}: this study puts {first} ahead of {second}; {others} other {'study does' if others == 1 else 'studies do'} the opposite.")


if __name__ == "__main__":
    main()
