#!/usr/bin/env python3
"""Build data/omics/use-case-coverage-binder-20261022/batch.jsonl and claims.csv.

Run from this directory:  python3 build_batch.py

Deterministic: the batch is sorted by record ID and the script asserts the record
counts and the invariants that matter for review (every link target exists, every
result points at an evaluation, no result carries both a value and a missing
reason for the same field).
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import adaptyv
import alphaproteo
import bennett
import bindcraft
import usecase

OUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPECTED_KINDS = {
    "claim": 39,
    "configuration": 13,
    "dataset": 33,
    "evaluation": 148,
    "method": 2,
    "pipeline": 4,
    "protocol": 14,
    "result": 159,
    "source": 7,
    "use_case": 1,
}


def main():
    records = []
    for module in (alphaproteo, bindcraft, bennett, adaptyv, usecase):
        records.extend(module.build())

    by_id = {}
    for rec in records:
        if rec["id"] in by_id:
            raise SystemExit(f"duplicate record id: {rec['id']}")
        by_id[rec["id"]] = rec

    # Links must resolve, either inside the batch or to a reused store ID.
    reused = {
        "discovery-model-rfdiffusion",
        "discovery-model-proteinmpnn",
        "discovery-model-genie-3",
        "catalog-model-boltz-2",
    }
    for rec in records:
        for ln in rec["links"]:
            target = ln["target_id"]
            if target not in by_id and target not in reused:
                raise SystemExit(f"{rec['id']} links to unknown {target}")
        if rec["kind"] == "result":
            rel = [ln for ln in rec["links"] if ln["relation"] == "evaluation"]
            if len(rel) != 1:
                raise SystemExit(f"{rec['id']} must link exactly one evaluation")
        if rec["kind"] == "evaluation":
            for relation in ("system", "assessment", "data"):
                if len([ln for ln in rec["links"] if ln["relation"] == relation]) != 1:
                    raise SystemExit(f"{rec['id']} must link exactly one {relation}")
        # A field never has both a value and a missing reason.
        attrs = rec["attributes"]
        for field in attrs.get("missing_metadata", {}):
            if "." in field:
                head, tail = field.split(".", 1)
                holder = attrs.get(head)
                if isinstance(holder, dict) and holder.get(tail) is not None:
                    raise SystemExit(f"{rec['id']}: {field} has both a value and a missing reason")
            elif attrs.get(field) is not None:
                raise SystemExit(f"{rec['id']}: {field} has both a value and a missing reason")
        if rec["kind"] in ("result", "claim") and "review" not in attrs:
            raise SystemExit(f"{rec['id']} has no review block")
        if rec["status"] != "needs_review":
            raise SystemExit(f"{rec['id']} is not needs_review; this pass does not review its own work")

    counts = {}
    for rec in records:
        counts[rec["kind"]] = counts.get(rec["kind"], 0) + 1
    for kind, expected in EXPECTED_KINDS.items():
        if counts.get(kind) != expected:
            raise SystemExit(f"expected {expected} {kind} records, got {counts.get(kind)}")

    records.sort(key=lambda r: r["id"])

    batch_path = os.path.join(OUT_DIR, "batch.jsonl")
    with open(batch_path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    claims_path = os.path.join(OUT_DIR, "claims.csv")
    with open(claims_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        for rec in records:
            if rec["kind"] not in ("result", "claim"):
                continue
            attrs = rec["attributes"]
            printed = attrs.get("printed_value", attrs.get("value", ""))
            writer.writerow([
                rec["id"],
                ";".join(rec["source_ids"]),
                attrs.get("source_locator", ""),
                printed if len(printed) <= 400 else printed[:397] + "...",
                "extracted, not reviewed",
            ])

    print(f"wrote {len(records)} records to {batch_path}")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")


if __name__ == "__main__":
    main()
