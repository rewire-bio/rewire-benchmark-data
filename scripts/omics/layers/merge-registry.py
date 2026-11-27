"""Add newly archived objects to the layer registry without re-deriving the rows it already holds.

Usage: python3 scripts/omics/layers/merge-registry.py <registry before> <unsupported before>

Run after `npm run layers -- build` has rewritten data/omics/layers/ on a machine whose tools may
differ from the ones the committed rows were made with. pdftotext output changes between
versions, so a full rebuild on such a machine rewrites rows that were right. This keeps every row
of an object the registry already held, as committed, and takes the rebuilt rows only for objects
that are new. Each row records the tool and version that made it.

Two fields of a kept row are copied from the archive manifest and so are taken from the rebuild:
`source_ids` and `store`. An object the manifest no longer holds is dropped.
"""
import json
import sys

REGISTRY = "data/omics/layers/registry.jsonl"
UNSUPPORTED = "data/omics/layers/unsupported.jsonl"
COPIED = ("source_ids", "store")


def read(path):
    return [json.loads(line) for line in open(path) if line.strip()]


def write(path, rows):
    with open(path, "w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def merge(before, after, sort_key):
    held = {row["object_sha256"] for row in before}
    current = {}
    for row in after:
        current.setdefault(row["object_sha256"], row)
    kept = []
    for row in before:
        fresh = current.get(row["object_sha256"])
        if fresh is None:
            continue
        kept.append({**row, **{field: fresh[field] for field in COPIED if field in fresh and field in row}})
    added = [row for row in after if row["object_sha256"] not in held]
    return sorted(kept + added, key=sort_key), len(kept), len(added)


def main():
    registry, kept, added = merge(read(sys.argv[1]), read(REGISTRY),
                                  lambda r: (r["layer_sha256"], r["object_sha256"], r.get("container_path") or ""))
    write(REGISTRY, registry)
    print(f"registry: {kept} rows kept as committed, {added} rows added for new objects")
    # An object with no layer yet in the committed registry may gain rows in `unsupported` too.
    before = read(sys.argv[2])
    after = read(UNSUPPORTED)
    in_registry_before = {row["object_sha256"] for row in read(sys.argv[1])}
    known = {row["object_sha256"] for row in before} | in_registry_before
    present = {row["object_sha256"] for row in after} | {row["object_sha256"] for row in registry}
    unsupported = [row for row in before if row["object_sha256"] in present] + [row for row in after if row["object_sha256"] not in known]
    write(UNSUPPORTED, sorted(unsupported, key=lambda r: (r["object_sha256"], r.get("container_path") or "")))
    print(f"unsupported: {len(unsupported)} rows")


if __name__ == "__main__":
    main()
