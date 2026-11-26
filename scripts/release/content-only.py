"""Decide whether a release can reuse the discrepancies of the last knowledge-graph bundle.

Usage: python3 scripts/release/content-only.py <commit of the last kg/<id> release> [<head>]

Exits 0 when everything that changed since that commit is descriptive content the graph's
inference and discrepancy rules cannot see: a profile or run guide on a model record, sources
appended to a model's source list, new source records, batch folders, documents and the files a
release commit writes. Exits 1, with the reason, for anything else: any evaluation, result or
claim, any other entity file or field, a removed or edited source, the ontology, vocabularies,
code or workflows. The release then builds the graph as usual.

A nightly run of kg-release.yml rebuilds the bundle for the newest release and fails if its
discrepancies differ from the reused ones, so a wrong answer here is caught within a day.
"""
import json
import subprocess
import sys

ALLOWED_PREFIXES = ("data/provenance/", "data/omics/", "docs/", "website/")
MODELS = "data/entities/models.jsonl"
SOURCES = "data/entities/sources.jsonl"
DESCRIPTIVE = ("profile", "run_guide")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def records(ref: str, path: str) -> dict[str, dict]:
    return {r["id"]: r for r in (json.loads(line) for line in git("show", f"{ref}:{path}").splitlines() if line.strip())}


def without_description(record: dict) -> dict:
    rest = {k: v for k, v in record.items() if k not in ("attributes", "source_ids")}
    rest["attributes"] = {k: v for k, v in record["attributes"].items() if k not in DESCRIPTIVE}
    return rest


def reason(base: str, head: str) -> str | None:
    for name in git("diff", "--name-only", base, head).splitlines():
        if name in (MODELS, SOURCES) or name.startswith(ALLOWED_PREFIXES):
            continue
        return f"{name} changed"
    old, new = records(base, SOURCES), records(head, SOURCES)
    for key, record in old.items():
        if new.get(key) != record:
            return f"source {key} was removed or edited"
    old, new = records(base, MODELS), records(head, MODELS)
    if set(old) != set(new):
        return "a model record was added or removed"
    for key, before in old.items():
        after = new[key]
        if before == after:
            continue
        if without_description(before) != without_description(after):
            return f"model {key} changed outside its profile and run guide"
        if after["source_ids"][: len(before["source_ids"])] != before["source_ids"]:
            return f"model {key} lost or reordered a source"
    return None


if __name__ == "__main__":
    why = reason(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "HEAD")
    print(f"Graph reasoning needed: {why}." if why else "Only descriptive content changed: the last bundle's discrepancies can be reused.")
    sys.exit(1 if why else 0)
