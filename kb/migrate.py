"""Build the knowledge base as one SQLite file from the current record store.

Usage: python3 kb/migrate.py [--out kb/build/kb.sqlite] [--check]

This is a function of the store as it stands, so it can be run on every release while the old
pipeline keeps working. Nothing is re-extracted from sources.

Layout of the file it writes (the design is in docs/rebuild.md):

  record          one row per record of any kind: id, kind, name, description, status, facets,
                  and `extra`, the attributes that have no column of their own. Nothing is dropped.
  record_source   which sources a record cites, in order.
  link            every link between records, in order.
  <typed tables>  source, system, assessment, dataset, evaluation, observation, claim, use_case:
                  the attributes that are compared or queried, as typed columns.
  study           sources that are one piece of work (same DOI, or declared companions).
  observation_v   one row per result with its system, the model or method it resolves to, its
                  test, its study and its number: the table comparisons are made on.

--check rebuilds every record from the file and compares it with the store. A record passes when
its id, kind, name, description, status, facets, sources, links and every attribute come back
equal. That is the test of the migration: by meaning, not by bytes.
"""
import argparse
import glob
import json
import os
import sqlite3
import sys
import time

# Attributes that become typed columns, per table. Everything else stays in record.extra.
# (attribute, column, sql type). A json column holds the value as JSON text.
COLUMNS = {
    "source": [
        ("url", "url", "TEXT"), ("artifact_url", "artifact_url", "TEXT"), ("doi", "doi", "TEXT"),
        ("artifact_sha256", "sha256", "TEXT"), ("media_type", "media_type", "TEXT"), ("retrieved_at", "retrieved_at", "TEXT"),
        ("version", "version", "TEXT"), ("licence", "licence", "TEXT"), ("publication_status", "publication_status", "TEXT"),
    ],
    "system": [
        ("depth_tier", "tier", "INTEGER"), ("entity_level", "entity_level", "TEXT"), ("reported_name", "reported_name", "TEXT"),
        ("version", "version", "TEXT"), ("checkpoint", "checkpoint", "TEXT"), ("configuration_type", "configuration_type", "TEXT"),
        ("reported_configuration", "reported_configuration", "TEXT"), ("parameters", "parameters_text", "TEXT"),
        ("training_setting", "training_setting", "TEXT"), ("representation", "representation", "TEXT"), ("head", "head", "TEXT"),
        ("access", "access", "TEXT"), ("licence", "licence", "TEXT"), ("training_data", "training_data", "TEXT"),
        ("profile", "profile", "JSON"), ("run_guide", "run_guide", "JSON"),
    ],
    "assessment": [
        ("depth_tier", "tier", "INTEGER"), ("metric", "metric", "TEXT"), ("metric_direction", "direction", "TEXT"), ("unit", "unit", "TEXT"),
        ("metric_qualifier", "metric_qualifier", "TEXT"), ("aggregation", "aggregation", "TEXT"), ("protocol", "protocol_text", "TEXT"),
        ("dataset", "dataset_text", "TEXT"), ("task", "task_text", "TEXT"), ("version", "version", "TEXT"), ("splits", "splits", "TEXT"),
        ("scope_note", "scope_note", "TEXT"), ("profile", "profile", "JSON"), ("run_guide", "run_guide", "JSON"),
        ("run_recipes", "run_recipes", "JSON"), ("run_documentation", "run_documentation", "JSON"),
    ],
    "dataset": [("version", "version", "TEXT"), ("licence", "licence", "TEXT"), ("access", "access", "TEXT")],
    "evaluation": [
        ("origin", "origin", "TEXT"), ("protocol", "protocol_text", "TEXT"), ("version", "version", "TEXT"), ("adaptation", "adaptation", "TEXT"),
        ("conditions", "conditions", "JSON"), ("comparison", "comparison", "JSON"), ("source_locator", "source_locator", "TEXT"),
    ],
    "observation": [
        ("metric", "metric", "TEXT"), ("metric_direction", "direction", "TEXT"), ("unit", "unit", "TEXT"), ("unit_detail", "unit_detail", "TEXT"),
        ("numeric_value", "value_text", "TEXT"), ("printed_value", "printed_value", "TEXT"), ("metric_qualifier", "metric_qualifier", "TEXT"),
        ("aggregation", "aggregation", "TEXT"), ("scoring_conditions", "scoring_conditions", "JSON"), ("uncertainty", "uncertainty", "JSON"),
        ("source_locator", "source_locator", "TEXT"), ("source_table", "source_table", "TEXT"),
    ],
    "claim": [
        ("field", "field", "TEXT"), ("value", "value", "JSON"), ("previous_value", "previous_value", "JSON"), ("target_id", "target_id", "TEXT"),
        ("relevance", "relevance", "TEXT"), ("rationale", "rationale", "TEXT"), ("source_locator", "source_locator", "TEXT"),
    ],
    "use_case": [("depth_tier", "tier", "INTEGER"), ("slug", "slug", "TEXT"), ("question", "question", "TEXT"), ("decision", "decision", "TEXT")],
}
TABLE_OF = {
    "source": "source", "model": "system", "method": "system", "configuration": "system", "pipeline": "system", "service": "system", "baseline": "system",
    "benchmark": "assessment", "task": "assessment", "protocol": "assessment", "evaluator": "assessment",
    "dataset": "dataset", "dataset_subset": "dataset", "evaluation": "evaluation", "result": "observation", "claim": "claim", "use_case": "use_case",
}
# Links that say "this system is a form of that one"; followed to find the model or method a result belongs to.
PARENT_RELATIONS = ("configuration_of", "variant_of", "alias_of", "family")


def store_files():
    return sorted(glob.glob("data/entities/*.jsonl")) + sorted(glob.glob("data/evidence/*/*.jsonl"))


def read_records():
    for path in store_files():
        with open(path) as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)


def dumps(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def schema():
    out = [
        "CREATE TABLE record (id TEXT PRIMARY KEY, kind TEXT NOT NULL, name TEXT, description TEXT, status TEXT, facets TEXT, attribute_order TEXT NOT NULL, extra TEXT NOT NULL, top_extra TEXT) WITHOUT ROWID",
        "CREATE INDEX record_kind ON record (kind)",
        "CREATE TABLE record_source (record_id TEXT NOT NULL, position INTEGER NOT NULL, source_id TEXT NOT NULL, PRIMARY KEY (record_id, position)) WITHOUT ROWID",
        "CREATE INDEX record_source_source ON record_source (source_id)",
        "CREATE TABLE link (from_id TEXT NOT NULL, position INTEGER NOT NULL, relation TEXT NOT NULL, to_id TEXT NOT NULL, extra TEXT, PRIMARY KEY (from_id, position)) WITHOUT ROWID",
        "CREATE INDEX link_to ON link (to_id, relation)",
        "CREATE INDEX link_relation ON link (relation, from_id)",
    ]
    for table, columns in COLUMNS.items():
        typed = ", ".join(f"{column} {'TEXT' if sql == 'JSON' else sql}" for _, column, sql in columns)
        out.append(f"CREATE TABLE {table} (id TEXT PRIMARY KEY, {typed}) WITHOUT ROWID")
    out += [
        # Derived: filled after the records are loaded.
        "ALTER TABLE observation ADD COLUMN value REAL",
        "ALTER TABLE observation ADD COLUMN evaluation_id TEXT",
        "ALTER TABLE observation ADD COLUMN study_id TEXT",
        "ALTER TABLE evaluation ADD COLUMN system_id TEXT",
        "ALTER TABLE evaluation ADD COLUMN assessment_id TEXT",
        "ALTER TABLE system ADD COLUMN parent_id TEXT",
        "ALTER TABLE system ADD COLUMN root_id TEXT",
        "CREATE TABLE study (id TEXT PRIMARY KEY, sources INTEGER NOT NULL) WITHOUT ROWID",
        "CREATE TABLE source_study (source_id TEXT PRIMARY KEY, study_id TEXT NOT NULL) WITHOUT ROWID",
    ]
    return out


def load(db):
    for statement in schema():
        db.execute(statement)
    known = {"id", "kind", "name", "description", "status", "facets", "source_ids", "links", "attributes"}
    inserts = {table: f"INSERT INTO {table} (id, {', '.join(c for _, c, _ in cols)}) VALUES (?{', ?' * len(cols)})" for table, cols in COLUMNS.items()}
    count = 0
    for r in read_records():
        count += 1
        attributes = r.get("attributes") or {}
        table = TABLE_OF[r["kind"]]
        mapped = {a for a, _, _ in COLUMNS[table]}
        extra = {k: v for k, v in attributes.items() if k not in mapped}
        top_extra = {k: v for k, v in r.items() if k not in known}
        db.execute("INSERT INTO record VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            r["id"], r["kind"], r.get("name"), r.get("description"), r.get("status"), dumps(r["facets"]) if "facets" in r else None,
            dumps(list(attributes)), dumps(extra), dumps(top_extra) if top_extra else None))
        row = [r["id"]]
        for attribute, _, sql in COLUMNS[table]:
            value = attributes.get(attribute)
            if attribute not in attributes:
                row.append(None)
            elif sql == "JSON" or not isinstance(value, (str, int)) or isinstance(value, bool) or (sql == "INTEGER") != isinstance(value, int):
                # Kept exactly: a JSON column, or a value whose type is not the column's (a null, a number in a text field).
                row.append("\x00" + dumps(value))
            else:
                row.append(value)
        db.execute(inserts[table], row)
        db.executemany("INSERT INTO record_source VALUES (?, ?, ?)", [(r["id"], i, s) for i, s in enumerate(r.get("source_ids") or [])])
        db.executemany("INSERT INTO link VALUES (?, ?, ?, ?, ?)", [
            (r["id"], i, link["relation"], link["target_id"], dumps({k: v for k, v in link.items() if k not in ("relation", "target_id")}) or None)
            for i, link in enumerate(r.get("links") or [])])
    return count


def derive(db):
    """Fill the columns comparisons need. Each is a plain consequence of the loaded rows."""
    db.execute("UPDATE observation SET value = CAST(value_text AS REAL) WHERE value_text IS NOT NULL AND substr(value_text, 1, 1) != char(0) AND value_text GLOB '*[0-9]*'")
    db.execute("UPDATE observation SET evaluation_id = (SELECT to_id FROM link WHERE from_id = observation.id AND relation = 'evaluation' ORDER BY position LIMIT 1)")
    db.execute("UPDATE evaluation SET system_id = (SELECT to_id FROM link WHERE from_id = evaluation.id AND relation = 'system' ORDER BY position LIMIT 1), "
               "assessment_id = (SELECT to_id FROM link WHERE from_id = evaluation.id AND relation = 'assessment' ORDER BY position LIMIT 1)")
    parents = dict(db.execute(f"SELECT from_id, to_id FROM link WHERE relation IN ({', '.join('?' * len(PARENT_RELATIONS))}) ORDER BY from_id, position DESC", PARENT_RELATIONS))
    for system_id, in db.execute("SELECT id FROM system").fetchall():
        root, seen = system_id, set()
        while root in parents and root not in seen:
            seen.add(root)
            root = parents[root]
        db.execute("UPDATE system SET parent_id = ?, root_id = ? WHERE id = ?", (parents.get(system_id), root, system_id))
    # A study is every source that is one piece of work: the same DOI, or linked as companions.
    group = {}

    def find(x):
        while group.setdefault(x, x) != x:
            group[x] = group[group[x]]
            x = group[x]
        return x

    for source_id, doi in db.execute("SELECT id, doi FROM source"):
        find(source_id)
        if doi and not doi.startswith("\x00"):
            group[find(source_id)] = find("doi:" + doi.lower())
    for a, b in db.execute("SELECT from_id, to_id FROM link WHERE relation = 'companion_of'"):
        group[find(a)] = find(b)
    sizes = {}
    for source_id, in db.execute("SELECT id FROM source").fetchall():
        study = find(source_id)
        sizes[study] = sizes.get(study, 0) + 1
        db.execute("INSERT INTO source_study VALUES (?, ?)", (source_id, study))
    db.executemany("INSERT INTO study VALUES (?, ?)", sizes.items())
    # A result's study: its own sources', else its evaluation's. The lowest id names a group of studies.
    db.execute("""UPDATE observation SET study_id = COALESCE(
        (SELECT group_concat(study_id, ' + ') FROM (SELECT DISTINCT ss.study_id FROM record_source rs JOIN source_study ss ON ss.source_id = rs.source_id WHERE rs.record_id = observation.id ORDER BY ss.study_id)),
        (SELECT group_concat(study_id, ' + ') FROM (SELECT DISTINCT ss.study_id FROM record_source rs JOIN source_study ss ON ss.source_id = rs.source_id WHERE rs.record_id = observation.evaluation_id ORDER BY ss.study_id)))""")
    db.execute("CREATE INDEX observation_evaluation ON observation (evaluation_id)")
    db.execute("CREATE INDEX evaluation_system ON evaluation (system_id)")
    db.execute("CREATE INDEX evaluation_assessment ON evaluation (assessment_id)")
    db.execute("""CREATE VIEW observation_v AS
        SELECT o.id, o.metric, o.direction, o.unit, o.value, o.printed_value, o.metric_qualifier, o.aggregation, o.scoring_conditions, o.source_locator,
               r.status, o.study_id, e.id AS evaluation_id, e.origin, e.adaptation,
               e.system_id, s.root_id, sr.name AS system_name, rr.name AS root_name, rr.kind AS root_kind,
               e.assessment_id, ar.kind AS assessment_kind, ar.name AS assessment_name
        FROM observation o JOIN record r ON r.id = o.id
        JOIN evaluation e ON e.id = o.evaluation_id
        LEFT JOIN system s ON s.id = e.system_id LEFT JOIN record sr ON sr.id = e.system_id LEFT JOIN record rr ON rr.id = s.root_id
        LEFT JOIN record ar ON ar.id = e.assessment_id""")


def rebuild(db, record_id):
    """The record as the store holds it, read back from the file."""
    row = db.execute("SELECT id, kind, name, description, status, facets, attribute_order, extra, top_extra FROM record WHERE id = ?", (record_id,)).fetchone()
    rid, kind, name, description, status, facets, order, extra, top_extra = row
    table = TABLE_OF[kind]
    typed = db.execute(f"SELECT {', '.join(c for _, c, _ in COLUMNS[table])} FROM {table} WHERE id = ?", (rid,)).fetchone()
    values = json.loads(extra)
    for (attribute, _, _), value in zip(COLUMNS[table], typed):
        if value is not None:
            values[attribute] = json.loads(value[1:]) if isinstance(value, str) and value.startswith("\x00") else value
    record = {"id": rid, "kind": kind}
    for key, value in (("name", name), ("description", description), ("status", status)):
        if value is not None:
            record[key] = value
    if facets is not None:
        record["facets"] = json.loads(facets)
    record["source_ids"] = [s for s, in db.execute("SELECT source_id FROM record_source WHERE record_id = ? ORDER BY position", (rid,))]
    record["links"] = [{"relation": relation, "target_id": to, **(json.loads(more) if more else {})}
                       for relation, to, more in db.execute("SELECT relation, to_id, extra FROM link WHERE from_id = ? ORDER BY position", (rid,))]
    record["attributes"] = {key: values[key] for key in json.loads(order)}
    record.update(json.loads(top_extra) if top_extra else {})
    return record


def check(db):
    wrong = total = 0
    for original in read_records():
        total += 1
        back = rebuild(db, original["id"])
        expected = dict(original)
        expected.setdefault("source_ids", [])
        expected.setdefault("links", [])
        expected.setdefault("attributes", {})
        if back != expected:
            wrong += 1
            if wrong <= 5:
                keys = [k for k in set(back) | set(expected) if back.get(k) != expected.get(k)]
                print(f"  differs: {original['id']} in {keys}")
    in_file = db.execute("SELECT count(*) FROM record").fetchone()[0]
    print(f"Checked {total} records against the store: {wrong} differ; the file holds {in_file}.")
    return wrong == 0 and in_file == total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="kb/build/kb.sqlite")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    if os.path.exists(args.out):
        os.remove(args.out)
    started = time.time()
    db = sqlite3.connect(args.out)
    db.execute("PRAGMA journal_mode = OFF")
    db.execute("PRAGMA synchronous = OFF")
    count = load(db)
    derive(db)
    db.commit()
    print(f"Loaded {count} records into {args.out} in {time.time() - started:.0f} s ({os.path.getsize(args.out) / 1e6:.0f} MB).")
    ok = check(db) if args.check else True
    db.close()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
