"""Carry discrepancy reviews forward when a rule change gives their findings new IDs.

  python scripts/kg/migrate-discrepancy-ids.py <asserted.nq> <previous discrepancies.json> <batch dir> <date>

Derives the discrepancies of the asserted graph with the current rules. For every accepted
discrepancy_review claim whose finding no longer fires, it looks in the previous release's
discrepancies.json for that finding's systems and outlier (or party) sources, and in the new
findings for an ordering finding of the same two systems whose studies include the study those
sources now belong to. If there is exactly one, it writes the next revision of the claim with the
same state and resolution, naming the new ID and listing the old one in previous_ids, to
<batch>/batch.jsonl, and a table of every decision to <batch>/migration.tsv.

Two old IDs cannot both be forwarded to one new finding: their revision 1 claims would collide.
When several match, the chain with the most revisions (then the lowest ID) is carried forward and
the others are left to retire as resolved findings, which requires them to be settled. An
unsettled claim with no match is reported, and the script exits non-zero.
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
import contradictions  # noqa: E402

ORDERING = ("ordering-reversal", "two-study-conflict")


def main(asserted_path: str, previous_path: str, batch: str, date: str) -> int:
    asserted = build.load_asserted(Path(asserted_path))
    ontology = build.load_ontology()
    inferred = build.infer(asserted, ontology)
    index = contradictions.Index(asserted, inferred, ontology)
    result = contradictions.derive(asserted, inferred, ontology)
    live = {d["id"]: d for d in result.report if not d["resolved"]}
    previous = {d["id"]: d for d in json.loads(Path(previous_path).read_text("utf-8"))["discrepancies"]}

    claims: dict[str, list[dict]] = {}
    for path in sorted(glob.glob(str(build.ROOT / "data" / "evidence" / "claims" / "*.jsonl"))):
        for line in open(path, encoding="utf-8"):
            record = json.loads(line)
            attributes = record["attributes"]
            if attributes.get("field") == contradictions.REVIEW_FIELD and record["status"] in ("source_checked", "reproduced"):
                claims.setdefault(attributes["discrepancy_id"], []).append(record)
    for chain in claims.values():
        chain.sort(key=lambda r: (r["attributes"].get("revision") or 0, r["id"]))

    def study_key(source: str) -> str | None:
        node = contradictions.URIRef(contradictions.ID + source)
        return index.study_keys.get(index.study.get(node)) if node in index.study else None

    proposals: dict[str, list[str]] = {}
    rows, problems = [], []
    for old, chain in sorted(claims.items()):
        if old in live:
            continue
        state = chain[-1]["attributes"]["value"]
        before = previous.get(old)
        if before is None:
            rows.append((old, "", state, "not in the previous release; left as is"))
            continue
        keys = {study_key(s) for s in before["outlier_sources"] + before.get("party_sources", [])} - {None}
        matches = [d for d in live.values() if d["rule"] in ORDERING and sorted(d["systems"]) == sorted(before["systems"])
                   and keys & {s["key"] for s in d["studies"] if s["role"] in ("outlier", "party")}]
        if len(matches) != 1:
            why = f"{len(matches)} matching findings; retires as resolved"
            rows.append((old, "", state, why))
            if state not in contradictions.TERMINAL_STATES:
                problems.append(f"{old} ({state}): {why}, but it is not settled")
            continue
        proposals.setdefault(matches[0]["id"], []).append(old)

    out = []
    for new, olds in sorted(proposals.items()):
        if new in claims:
            for old in olds:
                rows.append((old, new, claims[old][-1]["attributes"]["value"], "new finding already has a review; retires"))
            continue
        keep = max(olds, key=lambda old: (len(claims[old]), [-ord(c) for c in old]))
        for old in olds:
            if old != keep:
                state = claims[old][-1]["attributes"]["value"]
                rows.append((old, new, state, f"also matches; {keep} is carried forward and this one retires"))
                if state not in contradictions.TERMINAL_STATES:
                    problems.append(f"{old} ({state}) matches {new} with {keep}, but only one can be carried forward")
        last = claims[keep][-1]
        record = json.loads(json.dumps(last))
        revision = (last["attributes"].get("revision") or 1) + 1
        record["id"] = f"{last['id'].rsplit('-r', 1)[0] if last['id'].rsplit('-r', 1)[-1].isdigit() else last['id']}-r{revision}"
        record["description"] = (f"Review of {new}, revision {revision}: {last['attributes']['value']}. Discrepancy rules "
                                 f"version 4 gave {keep} a new ID ({live[new]['rule']}); the state and resolution are "
                                 "carried forward unchanged.")
        attributes = record["attributes"]
        attributes.update({"discrepancy_id": new, "revision": revision, "previous_ids": [keep], "date": date})
        attributes.pop("action", None)
        review = dict(attributes.get("review") or {})
        review["date"] = date
        review["note"] = ("Carried forward by scripts/kg/migrate-discrepancy-ids.py when rules version 4 re-keyed the "
                          f"finding; the evidence and decision are those of {last['id']}.")
        attributes["review"] = review
        out.append(record)
        rows.append((keep, new, attributes["value"], f"carried forward as {record['id']}"))

    folder = Path(batch)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "batch.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in out), "utf-8")
    (folder / "migration.tsv").write_text("old_id\tnew_id\tstate\tdecision\n" + "".join("\t".join(r) + "\n" for r in rows), "utf-8")
    print(f"{len(out)} claims carried forward, {len(rows) - len(out)} other decisions; see {folder / 'migration.tsv'}")
    for problem in problems:
        print("problem:", problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:]))
