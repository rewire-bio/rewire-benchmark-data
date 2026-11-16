#!/usr/bin/env python3
"""Independent re-check of the RFD4-Proteina batch's eight results and its claims.

Written for the review pass. It does not import or reuse extract/parse_efficiency_table.py.
It re-derives the model card's efficiency table from the archived card with its own parser,
re-derives the per-10-GPU-minute panel from the archived summary.csv, and checks each stored
result against both.

Run from the batch folder:

    python3 -I review/check_values.py --batch batch.jsonl --artifacts artifacts \
        --out review/value-check.tsv
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import sys
from collections import defaultdict

# Printed row label on the card -> (summary.csv panel, summary.csv criterion)
ROW_TO_PANEL = {
    "Protein binders": ("ppi", "ppi"),
    "Small-molecule binders": ("small_molecule", "sm_binder"),
    "Atomic Motif Enzyme": ("ame", "ame"),
    "DNA binders": ("dna", "dna"),
}

# summary.csv `model` value for the RFD4 column
RFD4_MODEL_KEYS = {"rfd4_proteina_high"}

ATTEMPTS_PER_TARGET = 200
CARD_PER_HOUR_FROM_PER_10_MIN = 6  # 60 minutes / 10 minutes


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_gz(path: str) -> bytes:
    with open(path, "rb") as handle:
        raw = handle.read()
    return gzip.decompress(raw), sha256_bytes(raw)


def load_batch(path: str):
    records = {}
    order = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            records[rec["id"]] = rec
            order.append(rec["id"])
    return records, order


def find_source(records, suffix: str):
    for rec in records.values():
        if rec["kind"] == "source" and rec["id"].endswith(suffix):
            return rec
    raise SystemExit(f"no source record ending {suffix}")


def parse_card_table(card_text: str):
    """Parse the 'Measured design efficiency' table out of the model card.

    Returns (rows, scope_note_present, metric_line, attempts_sentence_present,
             conditioning_sentence).
    rows maps printed row label -> dict with targets, rfd4_printed, other_printed,
    other_label, and the raw cells.
    """
    start = card_text.find("## Measured design efficiency")
    if start < 0:
        raise SystemExit("card has no 'Measured design efficiency' heading")
    # the section runs to the next level-2 heading
    nxt = card_text.find("\n## ", start + 1)
    section = card_text[start : nxt if nxt > 0 else len(card_text)]

    scope = (
        "**These numbers were measured on the previous release pair**" in section
        and "should not be read as describing it" in section
    )
    metric_line = None
    for line in section.splitlines():
        if line.strip().startswith("The table uses one consistent high-thinking"):
            metric_line = line.strip()
    attempts = "There are 200 original attempts per target." in section
    conditioning = None
    for line in section.splitlines():
        if line.strip().startswith("Conditioning differs between some methods"):
            conditioning = line.strip()

    table_lines = [
        line.strip()
        for line in section.splitlines()
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    if len(table_lines) < 6:
        raise SystemExit(f"expected a 4-row table, found {len(table_lines)} pipe lines")

    def cells(line):
        return [c.strip() for c in line.strip().strip("|").split("|")]

    header = cells(table_lines[0])
    expected_header = [
        "Benchmark",
        "Targets",
        "RFD4-Proteína, high thinking",
        "Best other method in this comparison",
    ]
    if header != expected_header:
        raise SystemExit(f"unexpected header {header!r}")

    rows = {}
    for line in table_lines[2:]:
        cell = cells(line)
        if len(cell) != 4:
            raise SystemExit(f"row has {len(cell)} cells: {line!r}")
        label, targets, rfd4_cell, other_cell = cell
        rfd4_value = rfd4_cell.replace("*", "").strip()
        # comparator cells print "Name · value"
        if "·" not in other_cell:
            raise SystemExit(f"comparator cell has no middle dot: {other_cell!r}")
        other_label, other_value = (p.strip() for p in other_cell.rsplit("·", 1))
        if not re.fullmatch(r"\d+\.\d{2}", rfd4_value):
            raise SystemExit(f"RFD4 cell not printed to two decimals: {rfd4_cell!r}")
        if not re.fullmatch(r"\d+\.\d{2}", other_value):
            raise SystemExit(f"comparator cell not printed to two decimals: {other_cell!r}")
        rows[label] = {
            "targets": int(targets),
            "rfd4_printed": rfd4_value,
            "rfd4_cell": rfd4_cell,
            "other_printed": other_value,
            "other_label": other_label,
            "other_cell": other_cell,
        }

    if set(rows) != set(ROW_TO_PANEL):
        raise SystemExit(f"row labels {sorted(rows)} != {sorted(ROW_TO_PANEL)}")
    return rows, scope, metric_line, attempts, conditioning


def load_summary(csv_bytes: bytes):
    reader = csv.DictReader(io.StringIO(csv_bytes.decode("utf-8")))
    return list(reader)


def summary_index(rows):
    idx = defaultdict(list)
    for row in rows:
        idx[(row["panel"], row["criterion"])].append(row)
    return idx


def best_other(panel_rows):
    """Highest unique_per_10_gpu_min among rows whose model is not an RFD4 arm."""
    others = [r for r in panel_rows if not r["model"].startswith("rfd4")]
    if not others:
        return None
    return max(others, key=lambda r: float(r["unique_per_10_gpu_min"]))


def rfd4_high(panel_rows):
    for row in panel_rows:
        if row["model"] in RFD4_MODEL_KEYS:
            return row
    return None


def fmt2(value: float) -> str:
    return f"{value:.2f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    records, _ = load_batch(args.batch)
    findings = []

    card_src = find_source(records, "source-hf-model-card")
    summary_src = find_source(records, "source-hf-benchmark-summary")

    card_bytes, card_gz_hash = read_gz(f"{args.artifacts}/hf_README.md.gz")
    summary_bytes, summary_gz_hash = read_gz(f"{args.artifacts}/hf_benchmarks_summary.csv.gz")

    for src, payload, gz_hash, name in (
        (card_src, card_bytes, card_gz_hash, "model card"),
        (summary_src, summary_bytes, summary_gz_hash, "summary.csv"),
    ):
        attrs = src["attributes"]
        got = sha256_bytes(payload)
        if got != attrs["artifact_sha256"]:
            findings.append(f"{name}: artifact_sha256 mismatch, archive gives {got}")
        if gz_hash != attrs["archive_sha256"]:
            findings.append(f"{name}: archive_sha256 mismatch, gz gives {gz_hash}")

    card = card_bytes.decode("utf-8")
    rows, scope_ok, metric_line, attempts_ok, conditioning = parse_card_table(card)
    if not scope_ok:
        findings.append("card: previous-release scope note above the table not found")
    if not attempts_ok:
        findings.append("card: '200 original attempts per target' sentence not found")
    if metric_line is None or "Higher is better" not in metric_line:
        findings.append("card: metric line or direction statement not found")
    if conditioning is None:
        findings.append("card: conditioning-differs sentence not found")

    idx = summary_index(load_summary(summary_bytes))

    out_rows = []
    results = [r for r in records.values() if r["kind"] == "result"]
    if len(results) != 8:
        findings.append(f"batch holds {len(results)} results, expected 8")

    for result in sorted(results, key=lambda r: r["id"]):
        attrs = result["attributes"]
        locator = attrs["source_locator"]
        row_label = None
        for label in ROW_TO_PANEL:
            if f"row '{label}'" in locator:
                row_label = label
                break
        if row_label is None:
            findings.append(f"{result['id']}: locator names no known row: {locator}")
            continue
        is_rfd4 = "column 'RFD4-Proteina, high thinking'" in locator
        is_other = "column 'Best other method in this comparison'" in locator
        if is_rfd4 == is_other:
            findings.append(f"{result['id']}: locator does not name exactly one column")
            continue

        card_row = rows[row_label]
        card_value = card_row["rfd4_printed"] if is_rfd4 else card_row["other_printed"]

        panel, criterion = ROW_TO_PANEL[row_label]
        panel_rows = idx[(panel, criterion)]
        csv_row = rfd4_high(panel_rows) if is_rfd4 else best_other(panel_rows)
        if csv_row is None:
            findings.append(f"{result['id']}: no summary.csv row for {panel}/{criterion}")
            continue

        derived = fmt2(
            float(csv_row["unique_per_10_gpu_min"]) * CARD_PER_HOUR_FROM_PER_10_MIN
        )
        status = []
        if attrs["printed_value"] != card_value:
            status.append(f"PRINTED_MISMATCH(card={card_value})")
        if attrs["numeric_value"] != card_value:
            status.append(f"NUMERIC_MISMATCH(card={card_value})")
        if derived != card_value:
            status.append(f"CSV_CROSSCHECK_MISMATCH(csv*6={derived})")

        # the comparator cell must print the label the record keeps
        if is_other:
            if attrs.get("printed_source_cell") != card_row["other_cell"]:
                status.append(
                    f"CELL_TEXT_MISMATCH(card={card_row['other_cell']!r})"
                )
            if card_row["other_label"] != csv_row["label"].replace(
                " (fixed)", " (fixed DNA)"
            ) and card_row["other_label"] not in csv_row["label"]:
                status.append(
                    f"LABEL_CHECK(card={card_row['other_label']!r} csv={csv_row['label']!r})"
                )
        else:
            if attrs.get("printed_source_cell") != card_row["rfd4_cell"]:
                status.append(f"CELL_TEXT_MISMATCH(card={card_row['rfd4_cell']!r})")

        # denominator must be targets x 200 and match the card's Targets column
        expected_den = card_row["targets"] * ATTEMPTS_PER_TARGET
        if attrs.get("denominator") != expected_den:
            status.append(f"DENOMINATOR(expected={expected_den})")
        if int(csv_row["targets"]) != card_row["targets"]:
            status.append(
                f"TARGETS(csv={csv_row['targets']} card={card_row['targets']})"
            )
        if int(csv_row["attempts"]) != expected_den:
            status.append(f"ATTEMPTS(csv={csv_row['attempts']})")

        # metric, unit, direction
        if attrs.get("metric") != "passing-design-clusters-per-accelerator-hour":
            status.append(f"METRIC({attrs.get('metric')})")
        if attrs.get("unit") != "count-per-hour":
            status.append(f"UNIT({attrs.get('unit')})")
        if attrs.get("metric_direction") != "higher":
            status.append(f"DIRECTION({attrs.get('metric_direction')})")
        if "uncertainty" in attrs:
            status.append("UNCERTAINTY_PRESENT")
        if "numerator" in attrs:
            status.append("NUMERATOR_PRESENT")

        # the conditioning arm the record keeps must be the one summary.csv names
        evaluation = records[result["links"][0]["target_id"]]
        protocol = records[evaluation["attributes"]["protocol"]]
        arm = csv_row["dataset"]
        if f"'{arm}'" not in protocol["attributes"]["scope_note"]:
            status.append(
                f"ARM(csv={arm} protocol={protocol['id']})"
            )

        out_rows.append(
            {
                "result_id": result["id"],
                "row": row_label,
                "column": "rfd4" if is_rfd4 else "best_other",
                "stored_printed": attrs["printed_value"],
                "card_cell": card_row["rfd4_cell"] if is_rfd4 else card_row["other_cell"],
                "card_value": card_value,
                "csv_panel": f"{panel}/{criterion}",
                "csv_model": csv_row["model"],
                "csv_dataset": csv_row["dataset"],
                "csv_unique_per_10_min": csv_row["unique_per_10_gpu_min"],
                "csv_times_6": derived,
                "denominator": attrs.get("denominator"),
                "protocol": protocol["id"],
                "status": "in_cell" if not status else ";".join(status),
            }
        )

    fields = list(out_rows[0].keys()) if out_rows else ["result_id", "status"]
    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for row in out_rows:
            writer.writerow(row)

    # every RFD4 cell must be the row's RFD4-high row, and every comparator cell the
    # best non-RFD4 row, so that the card's own column headings are what was extracted
    for label, (panel, criterion) in ROW_TO_PANEL.items():
        panel_rows = idx[(panel, criterion)]
        high = rfd4_high(panel_rows)
        other = best_other(panel_rows)
        if high is None or other is None:
            findings.append(f"{label}: summary.csv lacks an RFD4-high or comparator row")
            continue
        if fmt2(float(high["unique_per_10_gpu_min"]) * 6) != rows[label]["rfd4_printed"]:
            findings.append(f"{label}: RFD4 cell does not equal rfd4_proteina_high x 6")
        if fmt2(float(other["unique_per_10_gpu_min"]) * 6) != rows[label]["other_printed"]:
            findings.append(
                f"{label}: comparator cell is not the best non-RFD4 row x 6"
            )

    print(f"results checked: {len(out_rows)}")
    bad = [r for r in out_rows if r["status"] != "in_cell"]
    print(f"results with a problem: {len(bad)}")
    for row in bad:
        print(f"  {row['result_id']}: {row['status']}")
    print(f"other findings: {len(findings)}")
    for finding in findings:
        print(f"  {finding}")
    print(f"wrote {args.out}")
    return 1 if (bad or findings) else 0


if __name__ == "__main__":
    sys.exit(main())
