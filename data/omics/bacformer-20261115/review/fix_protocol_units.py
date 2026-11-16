"""Second review pass: the 14 protocols printed on a 0 to 100 scale still carried unit percent.

apply_review.py changed the unit concept on the 168 results but not on the protocols that govern
them, which left a protocol declaring `percent` over results declaring `unitless`. The ruling and
the reason are the same, the scope note of `unitless` in data/vocab/unit.ttl, so the same change is
applied here. The three strain-clustering protocols are printed on a 0 to 1 scale and were already
`unitless`.

The batch was already in the store when this was found, so the change is made in the canonical file
and in batch.jsonl together, and recorded with `npm run records -- change`.

Usage: python3 -I fix_protocol_units.py <store protocols.jsonl> <batch.jsonl>
"""

import json
import sys


def fix(path):
    records = [json.loads(l) for l in open(path) if l.strip()]
    changed = []
    for r in records:
        a = r.get("attributes", {})
        if (r["kind"] == "protocol" and r["id"].startswith("bacformer-20261115-")
                and a.get("unit") == "percent"):
            a["unit"] = "unitless"
            a["unit_detail"] = "printed x100"
            changed.append(r["id"])
    with open(path, "w") as fh:
        for r in records:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    return changed


def main(argv):
    store, batch = fix(argv[0]), fix(argv[1])
    if sorted(store) != sorted(batch):
        raise SystemExit(f"store changed {sorted(store)} but batch changed {sorted(batch)}")
    for rid in sorted(store):
        print(rid)
    print(f"{len(store)} protocols changed in both the store and batch.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
