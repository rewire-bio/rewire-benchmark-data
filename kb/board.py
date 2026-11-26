"""Estimate a leaderboard for each use case from results that were never measured side by side.

Usage: python3 kb/board.py [--db kb/build/kb.sqlite] [--out kb/build/boards] [--use-case <slug>]

Two papers rarely run the same test on the same models, so their numbers cannot be put in one
column. What can be compared is the order inside one study: when a study measures two models on
the same test with the same metric, it says which did better. This program collects those
within-study verdicts across every test a use case is assessed by, and fits one ranking to them.

How a board is built

1. A comparison group is one study's results on one test: same protocol, data, metric, unit,
   qualifier, aggregation and scoring conditions. Only results inside a group are compared.
2. In a group a model's value is its best configuration. Results marked disputed, excluded or
   superseded, results copied from another paper, and metrics with no stated direction are left out.
3. For each pair of models, each study gives one verdict: the share of its groups in which the
   first beat the second. A study with 500 groups counts as much as a study with one.
4. A Bradley-Terry model is fitted to the verdicts: each model gets a strength such that the chance
   one beats another is its strength over the sum of the two. One imagined draw against an average
   model is added for every model, so a model with a single win is not ranked first.

What a row says

  studies       how many studies compared this model with any other on the board
  opponents     how many other models it was compared with directly
  basis         "several studies" (2 or more), "one study", so a reader can see how much rests on it

The ranking is an estimate. It answers "given every head to head comparison we hold, what order is
most consistent with them", not "what would happen if all were run on one test".
"""
import argparse
import collections
import json
import math
import os
import sqlite3

GROUP_QUERY = """
SELECT o.study_id, o.assessment_id, o.metric, o.unit, o.metric_qualifier, o.aggregation, o.scoring_conditions,
       (SELECT group_concat(to_id, ' ') FROM (SELECT to_id FROM link WHERE from_id = o.evaluation_id AND relation = 'data' ORDER BY to_id)) AS data,
       o.root_id, o.root_name, o.direction, o.value
FROM link l JOIN observation_v o ON o.assessment_id = l.to_id
WHERE l.from_id = ? AND l.relation = 'assessed_by' AND o.value IS NOT NULL AND o.direction IN ('higher', 'lower')
  AND o.status NOT IN ('disputed', 'excluded', 'superseded') AND o.origin != 'paper_compilation' AND o.root_id IS NOT NULL
"""


def verdicts(db, use_case_id):
    """For each pair of models and each study, the share of the study's groups the first model won."""
    groups = collections.defaultdict(dict)
    names = {}
    for study, assessment, metric, unit, qualifier, aggregation, conditions, data, root, name, direction, value in db.execute(GROUP_QUERY, (use_case_id,)):
        names[root] = name
        key = (study, assessment, metric, unit, qualifier, aggregation, conditions, data, direction)
        best = groups[key].get(root)
        if best is None or (value > best if direction == "higher" else value < best):
            groups[key][root] = value
    per_study = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for key, values in groups.items():
        study, direction = key[0], key[-1]
        roots = sorted(values)
        for i, a in enumerate(roots):
            for b in roots[i + 1:]:
                cell = per_study[(a, b, study)]
                cell[2] += 1
                if values[a] == values[b]:
                    cell[0] += 0.5
                    cell[1] += 0.5
                elif (values[a] > values[b]) == (direction == "higher"):
                    cell[0] += 1
                else:
                    cell[1] += 1
    wins = collections.defaultdict(float)
    studies = collections.defaultdict(set)
    opponents = collections.defaultdict(set)
    comparisons = collections.Counter()
    for (a, b, study), (a_won, b_won, n) in per_study.items():
        wins[(a, b)] += a_won / n
        wins[(b, a)] += b_won / n
        for x, y in ((a, b), (b, a)):
            studies[x].add(study)
            opponents[x].add(y)
            comparisons[x] += n
    return names, wins, studies, opponents, comparisons


def fit(models, wins, rounds=200):
    """Bradley-Terry strengths by the usual iteration, with one imagined draw against an average model."""
    strength = {m: 1.0 for m in models}
    games = collections.defaultdict(float)
    for (a, b), w in wins.items():
        games[(a, b)] += w
        games[(b, a)] += w
    neighbours = collections.defaultdict(set)
    for a, b in games:
        neighbours[a].add(b)
    for _ in range(rounds):
        new = {}
        for m in models:
            won = 0.5 + sum(wins.get((m, o), 0.0) for o in neighbours[m])
            denominator = 1.0 / (strength[m] + 1.0) + sum(games[(m, o)] / (strength[m] + strength[o]) for o in neighbours[m])
            new[m] = won / denominator
        mean = math.exp(sum(math.log(v) for v in new.values()) / len(new))
        strength = {m: v / mean for m, v in new.items()}
    return strength


def board(db, use_case_id):
    names, wins, studies, opponents, comparisons = verdicts(db, use_case_id)
    models = sorted(studies)
    if len(models) < 2:
        return []
    strength = fit(models, wins)
    rows = []
    for m in sorted(models, key=lambda m: -strength[m]):
        rows.append({
            "model_id": m, "name": names[m], "strength": round(strength[m], 3),
            "studies": len(studies[m]), "opponents": len(opponents[m]), "comparisons": comparisons[m],
            "basis": "several studies" if len(studies[m]) >= 2 else "one study",
        })
    for position, row in enumerate(rows, 1):
        row["position"] = position
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="kb/build/kb.sqlite")
    parser.add_argument("--out", default="kb/build/boards")
    parser.add_argument("--use-case")
    args = parser.parse_args()
    db = sqlite3.connect(args.db)
    os.makedirs(args.out, exist_ok=True)
    for use_case_id, slug in db.execute("SELECT id, slug FROM use_case ORDER BY slug").fetchall():
        if args.use_case and slug != args.use_case:
            continue
        rows = board(db, use_case_id)
        with open(os.path.join(args.out, slug + ".json"), "w") as handle:
            json.dump({"use_case": slug, "method": "bradley-terry over within-study verdicts", "rows": rows}, handle, indent=1, ensure_ascii=False)
        several = sum(r["basis"] == "several studies" for r in rows)
        print(f"{slug}: {len(rows)} models ranked, {several} of them compared in several studies")
        if args.use_case:
            for r in rows[:25]:
                print(f"  {r['position']:>3}  {r['name'][:40]:<40} {r['strength']:>8}  studies {r['studies']}  opponents {r['opponents']}  {r['basis']}")


if __name__ == "__main__":
    main()
