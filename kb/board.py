"""Estimate a leaderboard for each use case from results that were never measured side by side.

Usage: python3 kb/board.py [--db kb/build/kb.sqlite] [--out <file>]
                           [--manifest public/omics/manifest.json] [--use-case <slug>]

Without --manifest the boards go to kb/build/boards.json, for release "unreleased". With it they
name the release and its date, and go to public/omics/boards/<release_id>.json, which the release
packages for the website.

Two papers rarely run the same test on the same models, so their numbers cannot be put in one
column. What can be compared is the order inside one study: when a study measures two models on
the same test with the same metric, it says which did better. This program collects those
within-study verdicts across every test a use case is assessed by, and fits one ranking to them.
docs/boards.md describes the output for readers; the rules are stated here.

How a board is built

1. A comparison group is one study's results on one test: same protocol, data, metric, unit,
   qualifier, aggregation and scoring conditions. Only results inside a group are compared.
2. In a group a model's value is its best configuration. Results marked disputed, excluded or
   superseded, results copied from another paper, and metrics with no stated direction are left out.
3. Studies. A result's study can name several studies joined by " + " (its sources belong to more
   than one). Study names that share a part are one study, so one piece of work is counted once.
4. Duplicates. Records whose names are the same once case, spaces and punctuation are ignored
   are one row when at least one of them is a model record (rule 7): the row takes that model's
   lowest record id and lists every record id. So a configuration recorded with no parent but
   named exactly as a model counts as that model.
5. For each pair of models, each study gives one verdict: the share of its groups in which the
   first beat the second. A study with 500 groups counts as much as a study with one.
6. A Bradley-Terry model is fitted to the verdicts of every model: each model gets a strength such
   that the chance one beats another is its strength over the sum of the two, and the strengths are
   those that make the verdicts most likely. One imagined draw against a model of strength 1 is
   added for every model, so a model with a single win is not ranked first. Strengths are then
   scaled so their geometric mean is 1: that is the average model a row's strength refers to.

Which models get a row

7. Only records of kind model, method, pipeline or service, not excluded, get a row. A
   configuration with no parent model, a baseline built inside a benchmark or an excluded record
   still counts as an opponent in the fit, and is listed as "not a model record".
8. A model gets a row only when it was compared in at least two studies. A model compared in one
   study is listed as "one study": its place would be that study's table, with nothing to check
   it against.
9. Only models joined to the largest set of models that were compared with each other, directly
   or through others, get a row. Order between two sets that were never compared comes only from
   the imagined draws, so the rest are listed as "not compared with the main group".
10. A board with fewer than two rows has none, and says why in its summary. A lone model that
    passed rules 7 to 9 is listed as "no second model to rank".

How certain a row is

11. The fit is repeated once for every study left out. A row's interval is the lowest and highest
    strength it has across the full fit and those refits (in each refit, strengths are put on the
    full fit's scale by matching the geometric mean of the ranked models it contains).
12. Positions are ranges. Model A is placed above model B only when A is stronger than B in the
    full fit and in every refit that contains both, by more than 0.1 percent of strength each time,
    and no refit leaves the two in sets of models never compared with each other (their order there
    would come only from the imagined draws). A row's best position is one more than the number of
    models placed above it, and its worst is the number of ranked models less those placed below
    it. Models that no refit can separate share positions.
13. basis is "mostly one study" when one study gives 80 percent or more of a row's comparisons,
    and "several studies" otherwise.

What a row says

  strength      chance of beating an average model on the board, from the full fit
  interval      lowest and highest strength across the refits of rule 11
  positions     best and worst position, rule 12
  studies       study ids it was compared in, with the number of comparisons from each
  opponents     how many other models it was compared with directly
  comparisons   how many within-group pairwise comparisons it took part in

The ranking is an estimate. It answers "given every head to head comparison we hold, what order is
most consistent with them", not "what would happen if all were run on one test". It ranks at the
model, not the checkpoint, because results are not yet grounded to checkpoints for most use cases.
"""
import argparse
import collections
import json
import math
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search import squash  # noqa: E402

SCHEMA_VERSION = 1
METHOD = ("Models are ordered by a Bradley-Terry fit to which model did better inside each study's "
          "comparisons, with every study weighted equally.")
MODEL_KINDS = ("model", "method", "pipeline", "service")
MIN_STUDIES = 2
MOSTLY_ONE_STUDY = 0.8
# Log strengths closer than this are a tie: far above the fit's tolerance, far below any real gap.
SEPARATION = 1e-3
NOT_A_MODEL, ONE_STUDY, NOT_CONNECTED, TOO_FEW = "not a model record", "one study", "not compared with the main group", "no second model to rank"

GROUP_QUERY = """
SELECT o.study_id, o.assessment_id, o.metric, o.unit, o.metric_qualifier, o.aggregation, o.scoring_conditions,
       (SELECT group_concat(to_id, ' ') FROM (SELECT to_id FROM link WHERE from_id = o.evaluation_id AND relation = 'data' ORDER BY to_id)) AS data,
       o.root_id, o.root_name, o.direction, o.value
FROM link l JOIN observation_v o ON o.assessment_id = l.to_id
WHERE l.from_id = ? AND l.relation = 'assessed_by' AND o.value IS NOT NULL AND o.direction IN ('higher', 'lower')
  AND o.status NOT IN ('disputed', 'excluded', 'superseded') AND o.origin != 'paper_compilation' AND o.root_id IS NOT NULL
ORDER BY o.id
"""


def read_groups(db, use_case_id):
    """The use case's comparison groups as {(study, test key, direction): {root: best value}}, and the roots' records."""
    groups = collections.defaultdict(dict)
    records = {}
    for study, assessment, metric, unit, qualifier, aggregation, conditions, data, root, name, direction, value in db.execute(GROUP_QUERY, (use_case_id,)):
        records[root] = {"name": name}
        key = (study, (assessment, metric, unit, qualifier, aggregation, conditions, data), direction)
        best = groups[key].get(root)
        if best is None or (value > best if direction == "higher" else value < best):
            groups[key][root] = value
    for root, record in records.items():
        record["kind"], record["status"] = db.execute("SELECT kind, status FROM record WHERE id = ?", (root,)).fetchone()
    return dict(groups), records


def merge_studies(groups):
    """Rule 3: study names that share a part become one study, named by its sorted parts."""
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for study, _, _ in groups:
        parts = study.split(" + ")
        find(parts[0])
        for part in parts[1:]:
            a, b = find(parts[0]), find(part)
            if a != b:
                parent[max(a, b)] = min(a, b)
    members = collections.defaultdict(set)
    for part in list(parent):
        members[find(part)].add(part)
    name = {root: " + ".join(sorted(parts)) for root, parts in members.items()}
    merged = collections.defaultdict(dict)
    for (study, test, direction), values in groups.items():
        key = (name[find(study.split(" + ")[0])], test, direction)
        for root, value in values.items():
            best = merged[key].get(root)
            if best is None or (value > best if direction == "higher" else value < best):
                merged[key][root] = value
    return dict(merged)


def merge_duplicates(groups, records):
    """Rule 4: records with a model record's squashed name become that model, under the lowest id."""
    canonical = {}
    for root in sorted(records):
        record = records[root]
        if record["kind"] in MODEL_KINDS and record["status"] != "excluded":
            canonical.setdefault(squash(record["name"]), root)
    alias = {root: canonical.get(squash(record["name"]), root) for root, record in records.items() if record["status"] != "excluded"}
    merged = collections.defaultdict(dict)
    for (study, test, direction), values in groups.items():
        key = (study, test, direction)
        for root, value in values.items():
            canonical = alias.get(root, root)
            best = merged[key].get(canonical)
            if best is None or (value > best if direction == "higher" else value < best):
                merged[key][canonical] = value
    record_ids = collections.defaultdict(list)
    for root in sorted(records):
        record_ids[alias.get(root, root)].append(root)
    return dict(merged), dict(record_ids)


def verdicts(groups):
    """Rule 5: {study: {(a, b): (a's share of wins, b's share)}} with a < b, and per model counts."""
    tallies = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for (study, _, direction), values in sorted(groups.items(), key=lambda item: repr(item[0])):
        roots = sorted(values)
        for i, a in enumerate(roots):
            for b in roots[i + 1:]:
                cell = tallies[(study, a, b)]
                cell[2] += 1
                if values[a] == values[b]:
                    cell[0] += 0.5
                    cell[1] += 0.5
                elif (values[a] > values[b]) == (direction == "higher"):
                    cell[0] += 1
                else:
                    cell[1] += 1
    per_study = collections.defaultdict(dict)
    opponents = collections.defaultdict(set)
    by_study = collections.defaultdict(collections.Counter)
    for (study, a, b), (a_won, b_won, n) in sorted(tallies.items()):
        per_study[study][(a, b)] = (a_won / n, b_won / n)
        for x, y in ((a, b), (b, a)):
            opponents[x].add(y)
            by_study[x][study] += n
    return dict(per_study), dict(opponents), dict(by_study)


def fit(per_study, leave_out=None, start=None, tolerance=1e-6, sweeps=2000):
    """Rule 6: Bradley-Terry strengths that maximise the likelihood of the verdicts and the imagined
    draws, found by one Newton step per model in turn on log strength."""
    wins = collections.defaultdict(float)
    games = collections.defaultdict(float)
    for study, pairs in per_study.items():
        if study == leave_out:
            continue
        for (a, b), (a_won, b_won) in pairs.items():
            wins[a, b] += a_won
            wins[b, a] += b_won
            games[a, b] += 1.0
            games[b, a] += 1.0
    neighbours = collections.defaultdict(list)
    for a, b in sorted(games):
        neighbours[a].append((b, games[a, b]))
    models = sorted(neighbours)
    if not models:
        return {}
    won = {m: 0.5 + sum(wins[m, o] for o, _ in neighbours[m]) for m in models}
    theta = {m: math.log((start or {}).get(m, 1.0)) for m in models}
    for _ in range(sweeps):
        change = 0.0
        for m in models:
            t = theta[m]
            p = 1.0 / (1.0 + math.exp(-t))
            gradient, curvature = won[m] - p, p * (1.0 - p)
            for o, g in neighbours[m]:
                p = 1.0 / (1.0 + math.exp(theta[o] - t))
                gradient -= g * p
                curvature += g * p * (1.0 - p)
            # A step is capped so a model that won every game cannot overshoot in one sweep.
            step = max(-2.0, min(2.0, gradient / curvature))
            theta[m] = t + step
            change = max(change, abs(step))
        if change < tolerance:
            break
    mean = sum(theta.values()) / len(theta)
    return {m: math.exp(v - mean) for m, v in theta.items()}


def components(per_study):
    """Sets of models joined by comparisons, largest first (then by lowest id)."""
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for pairs in per_study.values():
        for a, b in pairs:
            parent[find(a)] = find(b)
    sets = collections.defaultdict(set)
    for m in list(parent):
        sets[find(m)].add(m)
    return sorted(sets.values(), key=lambda s: (-len(s), min(s)))


def chance(strength):
    return strength / (strength + 1.0)


def rank(groups, records):
    """Rules 3 to 13 over plain data: the rows, the models left out and the counts of one board."""
    groups = merge_studies(groups)
    groups, record_ids = merge_duplicates(groups, records)
    per_study, opponents, by_study = verdicts(groups)
    models = sorted(by_study)
    parts = components(per_study)
    main = parts[0] if parts else set()
    listed, left_out = [], []
    for m in models:
        record = records[m]
        if record["kind"] not in MODEL_KINDS or record["status"] == "excluded":
            reason = NOT_A_MODEL
        elif len(by_study[m]) < MIN_STUDIES:
            reason = ONE_STUDY
        elif m not in main:
            reason = NOT_CONNECTED
        else:
            listed.append(m)
            continue
        left_out.append({"model_id": m, "name": record["name"], "reason": reason, "study_ids": sorted(by_study[m])})
    counts = {"studies": len(per_study), "groups": sum(len(v) >= 2 for v in groups.values()), "models": len(models), "ranked": 0,
              "one_study": sum(x["reason"] == ONE_STUDY for x in left_out),
              "not_a_model": sum(x["reason"] == NOT_A_MODEL for x in left_out),
              "not_connected": sum(x["reason"] == NOT_CONNECTED for x in left_out), "too_few": 0}
    if len(listed) < 2:
        counts["too_few"] = len(listed)
        return [], left_out + [{"model_id": m, "name": records[m]["name"], "reason": TOO_FEW, "study_ids": sorted(by_study[m])}
                               for m in listed], counts
    full = fit(per_study)
    refits, parts_of = [], []
    for study in sorted(per_study):
        refit = fit(per_study, leave_out=study, start=full)
        present = [m for m in listed if m in refit]
        if present:
            shift = sum(math.log(full[m]) - math.log(refit[m]) for m in present) / len(present)
            refits.append({m: refit[m] * math.exp(shift) for m in present})
            rest = {s: pairs for s, pairs in per_study.items() if s != study}
            parts_of.append({m: i for i, part in enumerate(components(rest)) for m in part})
    order = sorted(listed, key=lambda m: (-full[m], records[m]["name"].lower(), m))

    def placed_above(a, b):
        if math.log(full[a] / full[b]) <= SEPARATION:
            return False
        for refit, part in zip(refits, parts_of):
            if a in refit and b in refit and (part[a] != part[b] or math.log(refit[a] / refit[b]) <= SEPARATION):
                return False
        return True

    above = collections.Counter()
    below = collections.Counter()
    for i, a in enumerate(order):
        for b in order[i + 1:]:
            if placed_above(a, b):
                above[b] += 1
                below[a] += 1
    rows = []
    for m in order:
        values = [full[m]] + [r[m] for r in refits if m in r]
        total = sum(by_study[m].values())
        rows.append({
            "model_id": m, "record_ids": record_ids[m], "name": records[m]["name"],
            "positions": [above[m] + 1, len(order) - below[m]],
            "strength": round(chance(full[m]), 3),
            "interval": [round(chance(min(values)), 3), round(chance(max(values)), 3)],
            "studies": dict(sorted(by_study[m].items())),
            "opponents": len(opponents[m]), "comparisons": total,
            "basis": "mostly one study" if max(by_study[m].values()) >= MOSTLY_ONE_STUDY * total else "several studies",
        })
    counts["ranked"] = len(rows)
    return rows, left_out, counts


def plural(n, one, many=None):
    return f"{n} {one if n == 1 else many or one + 's'}"


def summary(counts):
    if counts["ranked"]:
        text = (f"Ranks {counts['ranked']} models compared in two or more studies, from {plural(counts['groups'], 'comparison group')} "
                f"in {plural(counts['studies'], 'study', 'studies')}.")
    else:
        text = (f"No ranking: fewer than two models were compared in two or more studies "
                f"({plural(counts['groups'], 'comparison group')} in {plural(counts['studies'], 'study', 'studies')}).")
    extra = [f"{counts['one_study']} compared in one study only" if counts["one_study"] else "",
             f"{counts['not_a_model']} not model records" if counts["not_a_model"] else "",
             f"{counts['not_connected']} not compared with the main group" if counts["not_connected"] else "",
             f"{counts['too_few']} compared in two or more studies with no second such model" if counts["too_few"] else ""]
    extra = [e for e in extra if e]
    return text + (f" Not ranked: {', '.join(extra)}." if extra else "")


def study_sources(db, study_ids):
    """For each board study, its source record ids and DOIs, so every row can be traced."""
    out = {}
    for study in sorted(study_ids):
        sources = sorted(s for part in study.split(" + ")
                         for (s,) in db.execute("SELECT source_id FROM source_study WHERE study_id = ?", (part,)))
        dois = sorted({d for s in sources for (d,) in db.execute("SELECT doi FROM source WHERE id = ?", (s,)) if d and not d.startswith("\x00")})
        out[study] = {"source_ids": sources, "dois": dois}
    return out


def board(db, use_case_id, slug, title, release_id, released_at):
    groups, records = read_groups(db, use_case_id)
    rows, left_out, counts = rank(groups, records)
    studies = {s for row in rows for s in row["studies"]} | {s for x in left_out for s in x["study_ids"]}
    return {
        "use_case": slug, "use_case_id": use_case_id, "title": title,
        "release_id": release_id, "released_at": released_at,
        "method": METHOD, "summary": summary(counts), "counts": counts,
        "rows": rows, "not_ranked": left_out, "studies": study_sources(db, studies),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="kb/build/kb.sqlite")
    parser.add_argument("--out")
    parser.add_argument("--manifest", help="the release's public/omics/manifest.json, for its id and date")
    parser.add_argument("--use-case")
    args = parser.parse_args()
    if args.use_case and args.manifest:
        parser.error("--use-case writes one board, so it cannot write the release's file")
    release_id, released_at = "unreleased", None
    if args.manifest:
        with open(args.manifest) as handle:
            manifest = json.load(handle)
        release_id, released_at = manifest["release_id"], manifest["released_at"]
    out = args.out or (f"public/omics/boards/{release_id}.json" if args.manifest else "kb/build/boards.json")
    db = sqlite3.connect(args.db)
    boards = []
    for use_case_id, slug, title in db.execute("SELECT u.id, u.slug, r.name FROM use_case u JOIN record r ON r.id = u.id ORDER BY u.slug").fetchall():
        if args.use_case and slug != args.use_case:
            continue
        b = board(db, use_case_id, slug, title, release_id, released_at)
        boards.append(b)
        print(f"{slug}: {b['summary']}")
        if args.use_case:
            for r in b["rows"]:
                low, high = r["positions"]
                place = str(low) if low == high else f"{low}-{high}"
                print(f"  {place:>7}  {r['name'][:40]:<40} {r['strength']:>6} [{r['interval'][0]}, {r['interval'][1]}]"
                      f"  studies {len(r['studies'])}  opponents {r['opponents']}  {r['basis']}")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w") as handle:
        json.dump({"schema_version": SCHEMA_VERSION, "release_id": release_id, "released_at": released_at,
                   "method": METHOD, "boards": boards}, handle, indent=1, ensure_ascii=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
