#!/usr/bin/env python3
"""Copy corrected `attributes.review` objects from batch.jsonl into the canonical store.

Needed because two defects in the review objects were found after the batch had been added:
every record carried the PDF's hash and URL in `review.artifact_sha256` and
`review.retrieval_url`, which is wrong for the three HTML source records and for the access
claim whose only source is the announcement page; and the shared method note for descriptive
records claimed a locator-by-locator re-read that had not been done in full. The note now says
what was done, and review/check_claim_quotes.py does the part that was missing.

Only `attributes.review` is replaced, in place, so each stored line keeps its own key order.
`npm run records -- change` must be run afterwards, to rehash the records and append the
provenance entry; this script does not touch provenance.

Usage: python3 apply_store_changes.py <batch.jsonl> [<store root>]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

STORE_GLOBS = ("data/entities/*.jsonl", "data/evidence/*/*.jsonl")


def main(batch: Path, root: Path) -> int:
    wanted = {}
    for line in batch.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if "review" in record["attributes"]:
            wanted[record["id"]] = record["attributes"]["review"]

    changed: list[str] = []
    for pattern in STORE_GLOBS:
        for path in sorted(root.glob(pattern)):
            lines = path.read_text().splitlines()
            out: list[str] = []
            touched = False
            for line in lines:
                record = json.loads(line)
                review = wanted.get(record["id"])
                if review is not None and record["attributes"].get("review") != review:
                    record["attributes"]["review"] = review
                    line = json.dumps(record, separators=(",", ":"), ensure_ascii=False)
                    changed.append(record["id"])
                    touched = True
                out.append(line)
            if touched:
                path.write_text("".join(f"{line}\n" for line in out))
    print(f"{len(changed)} records updated in the store")
    ids = Path(__file__).with_name("changed-record-ids.txt")
    ids.write_text("\n".join(sorted(changed)) + "\n")
    print(f"wrote {ids.name}; pass these to npm run records -- change")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else ".")))
