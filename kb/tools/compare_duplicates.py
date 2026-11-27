"""Compare kb/duplicates.py with rdf-kg-mcp's draft_upsert on the same drafts.

The inputs, for a release <id> cut from commit <sha> (the bundle's GitHub release names it as its
target commit; for 2026-11-26-36acdf5e0cfa it is 8601f82):

  gh release download kg/<id> -D kb/build/oracle                 # bundle tarball, discrepancies.json
  mkdir -p kb/build/oracle/bundle && tar -xzf kb/build/oracle/kg-<id>.tar.gz -C kb/build/oracle/bundle
  mkdir -p kb/build/oracle-store && git archive <sha> data | tar -x -C kb/build/oracle-store
  (cd kb/build/oracle-store && python3 ../../migrate.py --out ../oracle.sqlite)

Then, in this order:

  python3 kb/tools/compare_duplicates.py drafts
  uv run --no-project --with 'rdf-kg-mcp @ git+https://github.com/rewire-bio/rdf-kg-mcp@v0.4.0' \\
      python3 kb/tools/compare_duplicates.py server
  python3 kb/tools/compare_duplicates.py compare

drafts writes the drafts, from the public records of the database: each sampled record under a new
ID with its own name, then with its name squashed and upper-cased, then with two of its words among
words no record has, then with a name no record has; and one batch of drafts whose names match each
other. server loads the bundle in memory as `serve --drafts` does, with the manifest's draft block,
and calls DraftOverlay.upsert, the function behind draft_upsert, on each draft alone, removing it
again; the batch is upserted whole and read back with diff(), as draft_export summarises it. compare
runs kb/duplicates.py on the same drafts over the database and the bundle's discrepancies.json and
compares every field: IDs, kinds, labels, match, rank, score, order and same_name_omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORACLE = ROOT / "kb" / "build" / "oracle"
PER_KIND = 20
BATCH = [
    {"id": "compare-batch-a", "kind": "model", "name": "Qzxv-Wkjh Plom"},
    {"id": "compare-batch-b", "kind": "dataset", "name": "qzxvwkjh plom"},
    {"id": "compare-batch-c", "kind": "model", "name": "Qzxv Wkjh Plom Vrrnq Ghtyu"},
    {"id": "compare-batch-d", "kind": "model", "name": "ESM2"},
    {"id": "compare-batch-e", "kind": "method", "name": "esm-2 fine tuned"},
]


def shell(record_id: str, kind: str, name: str) -> dict:
    return {"id": record_id, "kind": kind, "name": name, "description": "", "status": "discovered", "facets": {},
            "source_ids": [], "links": [], "attributes": {}}


def make_drafts(db_path: Path, out: Path) -> None:
    sys.path.insert(0, str(ROOT / "kb"))
    from queries import Records
    from search import squash, words
    records = Records(str(db_path), discrepancies="none")
    public = records.public
    by_kind: dict[str, list] = {}
    rows = records.db.execute("SELECT id, kind, name FROM record").fetchall()
    for record_id, kind, name in sorted(rows, key=lambda r: hashlib.sha256(r[0].encode()).hexdigest()):
        if record_id in public and squash(name or ""):
            by_kind.setdefault(kind, []).append((record_id, kind, name))
    sample = [row for kind in sorted(by_kind) for row in by_kind[kind][:PER_KIND]]
    drafts = []
    for i, (record_id, kind, name) in enumerate(sample):
        drafts.append({"case": "copy", "of": record_id, "draft": shell(f"compare-copy-{i}", kind, name)})
        drafts.append({"case": "squashed", "of": record_id, "draft": shell(f"compare-squashed-{i}", kind, squash(name).upper())})
        if len(words(name)) >= 4:
            kept = " ".join(name.split()[:2])
            drafts.append({"case": "half", "of": record_id,
                           "draft": shell(f"compare-half-{i}", kind, f"{kept} Qzxv{i:04d} Wkjhplom Vrrnq Plokij Mnbvcx")})
        drafts.append({"case": "none", "of": record_id, "draft": shell(f"compare-none-{i}", kind, f"Qzxv{i:04d} Wkjhplom Vrrnq")})
    drafts.append({"case": "batch", "batch": [shell(d["id"], d["kind"], d["name"]) for d in BATCH]})
    out.write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in drafts), "utf-8")
    print(f"{len(drafts)} cases from {len(sample)} records of {len(by_kind)} kinds in {out}")


def answer(entry: dict) -> dict:
    out = {"possible_duplicates": entry["possible_duplicates"]}
    if entry.get("same_name_omitted"):
        out["same_name_omitted"] = entry["same_name_omitted"]
    return out


def run_server(bundle: Path, drafts_file: Path, out: Path) -> None:
    from rdf_kg_mcp.bundle import cache_root, open_bundle
    from rdf_kg_mcp.drafts import DraftConfig, DraftOverlay
    from rdf_kg_mcp.graph import KnowledgeGraph, load_store
    opened = open_bundle(str(bundle), cache_root())
    kg = KnowledgeGraph(opened, load_store(opened, None))
    overlay = DraftOverlay(kg, DraftConfig.load(opened.manifest["draft"], kg))
    kg.search_index  # built at start-up by the server too
    answers = []
    for case in map(json.loads, drafts_file.read_text("utf-8").splitlines()):
        if "batch" in case:
            for draft in case["batch"]:
                overlay.upsert(draft)
            answers.append({entry["id"]: answer(entry) for entry in overlay.diff()["added"]})
            for draft in case["batch"]:
                overlay.remove(draft["id"])
        else:
            answers.append(answer(overlay.upsert(case["draft"])))
            overlay.remove(case["draft"]["id"])
    out.write_text("".join(json.dumps(a, ensure_ascii=False) + "\n" for a in answers), "utf-8")
    print(f"{len(answers)} answers from release {opened.version} in {out}")


def compare(db_path: Path, discrepancies: Path, drafts_file: Path, server_file: Path) -> int:
    sys.path.insert(0, str(ROOT / "kb"))
    from queries import Records
    records = Records(str(db_path), discrepancies=str(discrepancies))
    cases = [json.loads(line) for line in drafts_file.read_text("utf-8").splitlines()]
    server = [json.loads(line) for line in server_file.read_text("utf-8").splitlines()]
    if len(cases) != len(server):
        print(f"{len(cases)} cases but {len(server)} server answers; run server again", file=sys.stderr)
        return 2
    totals: dict[str, list[int]] = {}
    shown = 0
    for case, theirs in zip(cases, server):
        if "batch" in case:
            ours = {e["id"]: answer(e) for e in records.duplicates(case["batch"])}
        else:
            ours = answer(records.duplicates([case["draft"]])[0])
        same = ours == theirs
        counts = totals.setdefault(case["case"], [0, 0, 0])
        counts[0] += 1
        counts[1] += same
        if "of" in case:
            counts[2] += any(d["id"] == case["of"] for d in ours["possible_duplicates"])
        if not same and shown < 10:
            shown += 1
            print(f"differs: {json.dumps(case, ensure_ascii=False)}\n  kb:     {json.dumps(ours, ensure_ascii=False)}\n"
                  f"  server: {json.dumps(theirs, ensure_ascii=False)}")
    for name, (n, agreed, original) in totals.items():
        print(f"{name}: {agreed} of {n} drafts agree with the server; the original record is reported for {original}")
    return 0 if all(agreed == n for n, agreed, _ in totals.values()) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("step", choices=("drafts", "server", "compare"))
    parser.add_argument("--db", default=str(ROOT / "kb" / "build" / "oracle.sqlite"))
    parser.add_argument("--bundle", default=str(ORACLE / "bundle"))
    parser.add_argument("--discrepancies", default=str(ORACLE / "discrepancies.json"))
    parser.add_argument("--drafts", default=str(ORACLE / "duplicate-drafts.jsonl"))
    parser.add_argument("--answers", default=str(ORACLE / "duplicate-answers.jsonl"))
    args = parser.parse_args()
    if args.step == "drafts":
        make_drafts(Path(args.db), Path(args.drafts))
    elif args.step == "server":
        run_server(Path(args.bundle), Path(args.drafts), Path(args.answers))
    else:
        return compare(Path(args.db), Path(args.discrepancies), Path(args.drafts), Path(args.answers))
    return 0


if __name__ == "__main__":
    sys.exit(main())
