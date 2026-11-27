"""Check that a rebuilt layer registry agrees with the one it replaces.

Usage: python3 scripts/omics/layers/compare-registry.py <registry before> [<registry after>]

A layer is derived from an object's bytes by tools whose output can change between versions
(pdftotext above all). A rebuild on a machine with a different version would rewrite thousands of
rows and nothing would say so. This compares the two files row by row: a row both hold must be
equal apart from `source_ids` and `store`, which are copied from the archive manifest and change
when the manifest does. Rows only one file holds are counted and allowed. Exits 1 on any other
difference, so the caller can refuse to commit the rebuild.
"""
import json
import sys

COPIED = ("source_ids", "store")


def read(path):
    rows = {}
    for line in open(path):
        if line.strip():
            record = json.loads(line)
            rows[(record["object_sha256"], record["layer_sha256"], record.get("container_path"))] = record
    return rows


def main():
    before = read(sys.argv[1])
    after = read(sys.argv[2] if len(sys.argv) > 2 else "data/omics/layers/registry.jsonl")
    differ = []
    for key in before.keys() & after.keys():
        a = {k: v for k, v in before[key].items() if k not in COPIED}
        b = {k: v for k, v in after[key].items() if k not in COPIED}
        if a != b:
            differ.append(key)
    objects_before = {key[0] for key in before}
    objects_after = {key[0] for key in after}
    gone = [key for key in before.keys() - after.keys() if key[0] in objects_after]
    print(f"rows in both {len(before.keys() & after.keys())}, new {len(after.keys() - before.keys())}, "
          f"objects dropped {len(objects_before - objects_after)}, rows that changed {len(differ)}, "
          f"rows lost from an object still held {len(gone)}")
    for key in (differ + gone)[:10]:
        print("  ", key)
    if differ or gone or objects_before - objects_after:
        print("The rebuilt registry does not agree with the committed one.")
        sys.exit(1)


if __name__ == "__main__":
    main()
