#!/usr/bin/env python3
"""Independent second parse of the BenchBench-Cloning tables, by column geometry.

extract/parse_tables.py reads each row with one anchored regex, so column assignment
follows from the order of the groups in that regex. This script does not use those
regexes. It tokenises each body line into (character offset, token) pairs, clusters the
offsets into columns across the rows of a table, and then checks that the value stored for
column j really sits in the j-th column cluster. A value can therefore not have been taken
from a neighbouring column without this disagreeing.

It also audits how much the repository's `batch -- check-values` pass is worth here.
That check reports `in_row` for a text layer, meaning the printed string was found
somewhere in the named row. Where the same string occurs more than once in a row, or where
a figure prints a row with the same label and the same number, an `in_row` pass is not
evidence of the right cell. The audit counts both cases so the reviewer knows which
results rest on the geometry check alone.

Usage: python3 extract/check_tables.py   (run from the batch folder)
"""

import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.dirname(HERE)
TEXT = os.path.join(BATCH, "artifacts", "arxiv-2610.33355v1.layout.txt.gz")
TABLES = os.path.join(HERE, "tables.json")

TOKEN = re.compile(r"\S+")
NUMBER = re.compile(r"^-?[0-9][0-9,]*(?:\.[0-9]+)?%?$")


def lines():
    with gzip.open(TEXT, "rt", encoding="utf-8") as handle:
        return handle.read().split("\n")


def caption_line(all_lines, label):
    hits = [i for i, line in enumerate(all_lines)
            if re.match(r"^\s*" + re.escape(label) + r":", line)]
    assert len(hits) == 1, f"{label}: {len(hits)} caption lines"
    return hits[0]


def body(all_lines, label, row_labels):
    """The body lines of a table: the lines above its caption that start with a row label."""
    end = caption_line(all_lines, label)
    earlier = [i for i, line in enumerate(all_lines)
               if i < end and re.match(r"^\s*(Table|Figure) [0-9A-G]+[0-9]*:", line)]
    start = (max(earlier) + 1) if earlier else 0
    out = []
    for i in range(start, end):
        line = all_lines[i]
        for row_label in row_labels:
            if re.match(r"^\s*" + re.escape(row_label) + r"(\s|$)", line):
                out.append((i, row_label, line))
                break
    return out


def numeric_cells(line, label):
    """(offset, token) of every numeric token after the row label."""
    after = re.match(r"^\s*" + re.escape(label), line).end()
    return [(m.start(), m.group()) for m in TOKEN.finditer(line)
            if m.start() >= after and NUMBER.match(m.group().strip("[],"))]


def header_spans(all_lines, header_index, labels):
    """Character spans of the named header labels, each running to the next label's start.

    This is the second, independent route to a cell: the regex parse in
    extract/parse_tables.py fixes columns by the order of groups in one anchored row
    regex, while this fixes them by where the printed column heading sits on the page.
    """
    header = all_lines[header_index]
    starts = []
    cursor = 0
    for label in labels:
        at = header.index(label, cursor)
        starts.append(at)
        cursor = at + len(label)
    spans = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(header) + 400
        spans.append((start, end))
    return spans


def tokens_in_span(line, span, label):
    """Numeric tokens of `line` whose first character falls inside `span`."""
    after = re.match(r"^\s*" + re.escape(label), line).end()
    start, end = span
    out = []
    for m in TOKEN.finditer(line):
        if m.start() < max(after, start) or m.start() >= end:
            continue
        token = m.group().strip("[],")
        if NUMBER.match(token):
            out.append(token)
    return out


def main():
    all_lines = lines()
    with open(TABLES, encoding="utf-8") as handle:
        tables = json.load(handle)["tables"]

    problems = []
    checked = 0

    def check(where, got, want):
        nonlocal checked
        checked += 1
        if got != want:
            problems.append(f"{where}: geometry gives {got!r}, regex parse gives {want!r}")

    # ---- Table D2: every cell, located by where its column heading sits on the page.
    systems = [row["system"] for row in tables["table_b1"]]
    d2_caption = caption_line(all_lines, "Table D2")
    d2_header = next(i for i in range(d2_caption - 1, 0, -1)
                     if "Protocol dev. % [95% CI]" in all_lines[i])
    d2_spans = header_spans(all_lines, d2_header, [
        "Protocol dev. % [95% CI]", "Construct design % [95% CI]",
        "Aggregate % [95% CI]", "Proto ($)", "Const ($)",
    ])
    d2_rows = body(all_lines, "Table D2", systems)
    assert len(d2_rows) == 24, f"Table D2: found {len(d2_rows)} body rows"

    by_lane = {}
    for row in tables["table_d2"]:
        by_lane.setdefault(row["system"], []).append(row)
    seen = {}
    for _, row_label, line in d2_rows:
        seen.setdefault(row_label, []).append(line)
    for system, lane_lines in seen.items():
        assert len(lane_lines) == 3, f"Table D2: {system} has {len(lane_lines)} rows"
        for lane_row, line in zip(by_lane[system], lane_lines):
            where = f"Table D2 {system} {lane_row['effort']}"
            for span, key in zip(d2_spans[:3], ("protocol_development", "construct_design",
                                                "aggregate")):
                got = tokens_in_span(line, span, system)
                check(f"{where} {key}", got, lane_row[key])
            for span, key in zip(d2_spans[3:], ("protocol_cost_usd", "construct_cost_usd")):
                check(f"{where} {key}", tokens_in_span(line, span, system), [lane_row[key]])

    # ---- Table G1: every cell, located the same way.
    g1_caption = caption_line(all_lines, "Table G1")
    g1_header = next(i for i in range(g1_caption - 1, 0, -1)
                     if "pass@1 % [95% CI]" in all_lines[i])
    g1_spans = header_spans(all_lines, g1_header, [
        "pass@1 % [95% CI]", "pass@5 % [95% CI]", "pass@10 % [95% CI]",
        "Solved \u22651", "Solved all", "Note",
    ])
    g1_rows = body(all_lines, "Table G1", systems)
    assert len(g1_rows) == 8, f"Table G1: found {len(g1_rows)} body rows"
    g1_by_system = {row["system"]: row for row in tables["table_g1"]}
    for _, system, line in g1_rows:
        row = g1_by_system[system]
        for span, key in zip(g1_spans[:3], ("pass_at_1", "pass_at_5", "pass_at_10")):
            check(f"Table G1 {system} {key}", tokens_in_span(line, span, system), row[key])
        for span, key in zip(g1_spans[3:5], ("solved_at_least_once", "solved_all")):
            check(f"Table G1 {system} {key}", tokens_in_span(line, span, system),
                  [str(row[key])])

    # ---- Table G2: all 120 per-task cells, by column geometry.
    task_names = [row["task"] for row in tables["table_g2"]]
    g2_rows = body(all_lines, "Table G2", task_names)
    assert len(g2_rows) == 15, f"Table G2: found {len(g2_rows)} body rows"
    g2_offsets = []
    for _, task, line in g2_rows:
        after = re.match(r"^\s*" + re.escape(task), line).end()
        g2_offsets += [m.start() for m in re.finditer(r"[0-5]/5", line) if m.start() >= after]
    g2_offsets.sort()
    g2_clusters = []
    for offset in g2_offsets:
        if g2_clusters and offset - g2_clusters[-1][-1] <= 6:
            g2_clusters[-1].append(offset)
        else:
            g2_clusters.append([offset])
    assert len(g2_clusters) == 8, f"Table G2: {len(g2_clusters)} columns, expected 8"
    g2_centres = [sum(c) / len(c) for c in g2_clusters]
    g2_by_task = {row["task"]: row for row in tables["table_g2"]}
    for _, task, line in g2_rows:
        row = g2_by_task[task]
        after = re.match(r"^\s*" + re.escape(task), line).end()
        cells = [(m.start(), m.group()) for m in re.finditer(r"[0-5]/5", line)
                 if m.start() >= after]
        for centre, system in zip(g2_centres, systems):
            hits = [tok for off, tok in cells if abs(off - centre) <= 8]
            check(f"Table G2 {task!r} {system}", hits, [f"{row['solves'][system]}/5"])

    # ---- Audit: how much is an `in_row` value-check pass worth for each stored result?
    audit = {"row_value_unique": 0, "row_value_repeated": 0,
             "figure_row_same_label_and_value": 0}
    ambiguous = []

    def row_audit(where, line, label, value):
        after = re.match(r"^\s*" + re.escape(label), line).end()
        occurrences = len(re.findall(re.escape(value), line[after:]))
        if occurrences > 1:
            audit["row_value_repeated"] += 1
            ambiguous.append(f"{where}: '{value}' occurs {occurrences} times in its own row")
        else:
            audit["row_value_unique"] += 1
        # A figure row carrying the same label and the same number.
        for i, other in enumerate(all_lines):
            if other is line or other.strip() == "":
                continue
            if re.match(r"^\s*" + re.escape(label) + r"(\s|$)", other) and value in other:
                if other != line:
                    audit["figure_row_same_label_and_value"] += 1
                    ambiguous.append(
                        f"{where}: line {i + 1} also starts with '{label}' and contains "
                        f"'{value}'"
                    )
                    break

    for line_no, system, line in d2_rows:
        for lane_row in by_lane[system]:
            if line not in seen[system]:
                continue
        idx = seen[system].index(line)
        lane_row = by_lane[system][idx]
        for key in ("protocol_development", "construct_design", "aggregate"):
            row_audit(f"Table D2 {system} {lane_row['effort']} {key}",
                      line, system, lane_row[key][0])
    for line_no, system, line in g1_rows:
        row = g1_by_system[system]
        for key in ("pass_at_5", "pass_at_10"):
            row_audit(f"Table G1 {system} {key}", line, system, row[key][0])
        for key in ("solved_at_least_once", "solved_all"):
            row_audit(f"Table G1 {system} {key}", line, system, str(row[key]))

    print(f"geometry check: {checked} cells compared")
    if problems:
        print(f"{len(problems)} disagreement(s):")
        for problem in problems:
            print("  " + problem)
        return 1
    print("  no disagreement with the regex parse")
    print("\nvalue-check audit for the 104 results the repository check left at in_row:")
    for key, value in audit.items():
        print(f"  {key}: {value}")
    if ambiguous:
        print("  cases where an in_row pass alone is not evidence of the right cell:")
        for case in ambiguous:
            print("    " + case)
    return 0


if __name__ == "__main__":
    sys.exit(main())
