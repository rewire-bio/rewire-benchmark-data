"""Copy each archive object's source ids from the manifest into the layer registry.

Usage: python3 scripts/omics/layers/sync-source-ids.py

A registry row repeats the source ids of the object it was derived from. When a new source record
turns out to pin an object the archive already holds, the manifest row gains that source id and
the registry rows for the object must follow. `npm run layers -- build` does this too, but it
needs every object's bytes; this needs none, so the archive workflow can run it after each fetch.
It changes nothing else in a row and adds no row: layers for new objects still come from `build`.
"""
import glob
import json

REGISTRY = "data/omics/layers/registry.jsonl"


def main():
    sources = {}
    for path in glob.glob("data/archive/objects/*.jsonl"):
        for line in open(path):
            if line.strip():
                row = json.loads(line)
                sources[row["sha256"]] = sorted(row["source_ids"])
    out, changed = [], 0
    for line in open(REGISTRY).read().split("\n"):
        if not line.strip():
            out.append(line)
            continue
        record = json.loads(line)
        wanted = sources.get(record["object_sha256"])
        if wanted is not None and record["source_ids"] != wanted:
            record["source_ids"] = wanted
            line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
            changed += 1
        out.append(line)
    open(REGISTRY, "w").write("\n".join(out))
    print(f"{changed} registry rows updated")


if __name__ == "__main__":
    main()
