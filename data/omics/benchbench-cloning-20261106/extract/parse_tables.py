#!/usr/bin/env python3
"""Parse the BenchBench-Cloning tables from the pinned arXiv PDF text layer.

Input: artifacts/arxiv-2610.33355v1.layout.txt.gz, the `pdftotext -layout` text of
arXiv:2610.33355v1 (PDF SHA-256
6f5044b1bbbd81ad86b23cb536e2cae6428e0d9126f11546041355518febdc39).

Each table is located by its own caption line, and only the lines between the
previous caption and that caption are searched. Figures 2, 3, 6 and E1 print the
same numbers as Tables 2, G2 and E1, so a parse that scanned the whole document
could read a figure label instead of a table cell. Every row label is asserted.

Output: extract/tables.json.

Usage: python3 extract/parse_tables.py  (run from the batch folder)
"""

import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.dirname(HERE)
TEXT = os.path.join(BATCH, "artifacts", "arxiv-2610.33355v1.layout.txt.gz")
OUT = os.path.join(HERE, "tables.json")

TEXT_SHA256 = "c52ec41e171a81180ed0b9110e6ff26999740a73d7ecf2ab1fd600591357a616"

SYSTEMS = [
    "GPT-6 Astra",
    "GPT-6.1 Sol",
    "Claude Opus 5.5",
    "Gemini 4 Argon",
    "Claude Mythos 5.1",
    "Grok 4.7",
    "Kimi K3",
    "Gemini 3.8 Flash",
]

# Column order of the per-task tables (Table G2 and Figure 6).
TASK_TABLE_COLUMNS = [
    "GPT-6 Astra",
    "GPT-6.1 Sol",
    "Claude Opus 5.5",
    "Gemini 4 Argon",
    "Claude Mythos 5.1",
    "Grok 4.7",
    "Kimi K3",
    "Gemini 3.8 Flash",
]

CONSTRUCT_TASKS_G2 = [
    "Matched promoter panel",
    "GFP into EcoFlex vector",
    "Insulin intermediate construct",
    "Minimal-edit recoding",
    "Reporter choice from data",
    "Insulin two-chain constructs",
    "MPRA construct rebuild",
    "AG/AP1 chimera plasmid",
    "Detector choice from antibody data",
    "Alkaloid-pathway GoldenBraid set",
    "Tus/TerB HEK293 constructs",
    "Prime-assembly donor family",
    "Synthetic-chromosome locus edit",
    "Sodium-channel promoter repair",
    "Dual-luciferase frame panel",
]

CAPTION = re.compile(r"^\s*(Table|Figure) ([0-9A-G]+[0-9]*):")

CI = r"([0-9]+\.[0-9]) \[\s*([0-9]+\.[0-9]), ([0-9]+\.[0-9])\]"


def load_lines():
    with gzip.open(TEXT, "rt", encoding="utf-8") as handle:
        return handle.read().split("\n")


def caption_index(lines):
    """Line numbers (0-based) of every table and figure caption, in order."""
    found = []
    for i, line in enumerate(lines):
        match = CAPTION.match(line)
        if match:
            found.append((i, f"{match.group(1)} {match.group(2)}"))
    return found


def region(lines, captions, label):
    """Lines belonging to `label`: between the previous caption and this one.

    Returns (start, end, rows) with end exclusive at the caption line.
    """
    positions = [i for i, name in captions if name == label]
    assert len(positions) == 1, f"{label}: expected one caption, found {len(positions)}"
    end = positions[0]
    earlier = [i for i, _ in captions if i < end]
    start = (max(earlier) + 1) if earlier else 0
    return start, end, lines[start:end]


def one(rows, pattern, label, what):
    """The single line in `rows` matching `pattern`; fails if 0 or >1 match."""
    hits = [m for m in (pattern.match(r) for r in rows) if m]
    assert len(hits) == 1, f"{label}: {what}: expected 1 matching row, got {len(hits)}"
    return hits[0]


def parse_table_1(lines, captions):
    """Protocol-development task families: dominant constraint, task count, share."""
    _, _, rows = region(lines, captions, "Table 1")
    families = [
        ("Methylation state", "methylation-state"),
        ("Homology-directed and", "homology-directed-assembly"),
        ("Repeats and tandem", "repeats-and-tandem-arrays"),
        ("Backbone end chemistry", "backbone-end-chemistry"),
        ("Golden Gate / MoClo", "golden-gate-moclo"),
        ("GC-rich templates", "gc-rich-templates"),
        ("Recombination, CRISPR", "recombination-crispr-viral"),
        ("Counterselection", "counterselection"),
        ("Expression vectors and", "expression-vector-tag-exchange"),
    ]
    out = []
    for printed, slug in families:
        pattern = re.compile(
            r"^\s*" + re.escape(printed) + r"\s{2,}([0-9]+)\s+([0-9]+)%\s"
        )
        match = one(rows, pattern, "Table 1", printed)
        out.append(
            {
                "slug": slug,
                "label": printed,
                "tasks": int(match.group(1)),
                "share_percent": int(match.group(2)),
            }
        )
    total = one(
        rows, re.compile(r"^\s*Total\s+([0-9]+)\s+([0-9]+)%"), "Table 1", "Total"
    )
    assert int(total.group(1)) == 50, "Table 1: total task count is not 50"
    assert int(total.group(2)) == 100, "Table 1: total share is not 100%"
    assert sum(f["tasks"] for f in out) == 50, "Table 1: family counts do not sum to 50"
    assert (
        sum(f["share_percent"] for f in out) == 100
    ), "Table 1: family shares do not sum to 100"
    return out


def parse_table_2(lines, captions):
    """Performance by task set at top effort: protocol dev, construct design, aggregate."""
    _, _, rows = region(lines, captions, "Table 2")
    out = []
    for system in SYSTEMS:
        pattern = re.compile(
            r"^\s*"
            + re.escape(system)
            + r"\s+(low|medium|high|xhigh|max)\s+"
            + CI
            + r"\s+"
            + CI
            + r"\s+"
            + CI
            + r"\s*$"
        )
        match = one(rows, pattern, "Table 2", system)
        out.append(
            {
                "system": system,
                "effort": match.group(1),
                "protocol_development": list(match.group(2, 3, 4)),
                "construct_design": list(match.group(5, 6, 7)),
                "aggregate": list(match.group(8, 9, 10)),
            }
        )
    return out


def parse_table_a1(lines, captions):
    """Construct-design tasks: source, experimental records supplied, grading route."""
    _, _, rows = region(lines, captions, "Table A1")
    # (number, first printed line of the task name, full task name, grading route,
    #  whether the source study's experimental records are supplied)
    spec = [
        (1, "MPRA construct rebuild", "MPRA construct rebuild", "Deterministic", True),
        (2, "Matched promoter panel", "Matched promoter panel", "Deterministic", True),
        (3, "Sodium-channel promoter", "Sodium-channel promoter repair", "Deterministic", True),
        (4, "Detector choice from", "Detector choice from antibody data",
         "Deterministic + rubric judge", True),
        (5, "Reporter choice from data", "Reporter choice from data", "Deterministic", True),
        (6, "Dual-luciferase frame panel", "Dual-luciferase frame panel", "Deterministic", True),
        (7, "AG/AP1 chimera plasmid", "AG/AP1 chimera plasmid",
         "Deterministic + rubric judge", False),
        (8, "Synthetic-chromosome locus", "Synthetic-chromosome locus edit",
         "Deterministic + rubric judge", False),
        (9, "Alkaloid-pathway", "Alkaloid-pathway GoldenBraid set",
         "Deterministic + rubric judge", False),
        (10, "GFP into EcoFlex vector", "GFP into EcoFlex vector",
         "Deterministic + rubric judge", False),
        (11, "Prime-assembly donor family", "Prime-assembly donor family",
         "Deterministic + rubric judge", False),
        (12, "Tus/TerB HEK293 constructs", "Tus/TerB HEK293 constructs",
         "Deterministic + rubric judge", False),
        (13, "Minimal-edit recoding", "Minimal-edit recoding",
         "Deterministic + rubric judge", False),
        (14, "Insulin two-chain constructs", "Insulin two-chain constructs",
         "Deterministic + rubric judge", False),
        (15, "Insulin intermediate construct", "Insulin intermediate construct",
         "Deterministic + rubric judge", False),
    ]
    out = []
    for number, first_line, name, grading, has_records in spec:
        pattern = re.compile(
            r"^\s*"
            + str(number)
            + r"\s{2,}"
            + re.escape(first_line)
            + r"\s{2,}(.+?)\s{2,}(.+?)\s{2,}"
            + re.escape(grading)
            + r"\s*$"
        )
        match = one(rows, pattern, "Table A1", name)
        out.append(
            {
                "number": number,
                "task": name,
                "source_first_line": match.group(1).strip(),
                "records_first_line": match.group(2).strip(),
                "grading": grading,
                "experimental_records_supplied": has_records,
            }
        )
    judged = [r for r in out if r["grading"] == "Deterministic + rubric judge"]
    deterministic = [r for r in out if r["grading"] == "Deterministic"]
    assert len(judged) == 10, f"Table A1: expected 10 rubric-judged tasks, got {len(judged)}"
    assert len(deterministic) == 5, (
        f"Table A1: expected 5 deterministic-only tasks, got {len(deterministic)}"
    )
    assert sum(1 for r in out if r["experimental_records_supplied"]) == 6, (
        "Table A1: expected 6 tasks supplying experimental records"
    )
    assert {r["task"] for r in out} == set(CONSTRUCT_TASKS_G2), (
        "Table A1 and Table G2 name different construct-design tasks"
    )
    return out


def parse_table_b1(lines, captions):
    """Model and harness settings."""
    _, _, rows = region(lines, captions, "Table B1")
    expected = {
        "GPT-6 Astra": ("gpt-6-astra", "Codex CLI 0.156.1", "low / high / max"),
        "GPT-6.1 Sol": ("gpt-6.1-sol", "Codex CLI 0.156.1", "low / high / max"),
        "Claude Opus 5.5": (
            "claude-opus-5-5",
            "Claude Code 2.1.289",
            "low / high / max",
        ),
        "Gemini 4 Argon": (
            "gemini-4-argon",
            "Gemini CLI 0.63.0, in-sandbox proxy",
            "low / medium / high",
        ),
        "Claude Mythos 5.1": (
            "claude-mythos-5-1",
            "Claude Code 2.1.289",
            "low / high / max",
        ),
        "Grok 4.7": ("grok-4.7", "Grok Build 1.0.46", "low / high / xhigh"),
        "Kimi K3": ("moonshotai/Kimi-K3", "Pi 1.0.3", "low / medium / high"),
        "Gemini 3.8 Flash": (
            "gemini-3.8-flash",
            "Gemini CLI 0.63.0",
            "low / medium / high",
        ),
    }
    out = []
    for system in SYSTEMS:
        model_id, harness, settings = expected[system]
        pattern = re.compile(
            r"^\s*"
            + re.escape(system)
            + r"\s{2,}"
            + re.escape(model_id)
            + r"\s{2,}"
            + re.escape(harness)
            + r"\s{2,}(.+?)\s{2,}"
            + re.escape(settings)
            + r"\s*$"
        )
        match = one(rows, pattern, "Table B1", system)
        out.append(
            {
                "system": system,
                "model_id": model_id,
                "harness": harness,
                "access_route": match.group(1).strip(),
                "reasoning_settings": settings.split(" / "),
            }
        )
    return out


def parse_table_c1(lines, captions):
    """Judge agreement: trials graded, agreement, Cohen's kappa."""
    _, _, rows = region(lines, captions, "Table C1")
    slices = [
        ("All trials", "all-trials"),
        ("Tasks with experimental records (6)", "tasks-with-experimental-records"),
        ("Construction tasks (9)", "construction-tasks"),
        ("GPT-6 Astra", "gpt-6-astra"),
        ("GPT-6.1 Sol", "gpt-6.1-sol"),
        ("Claude Opus 5.5", "claude-opus-5-5"),
        ("Kimi K3", "kimi-k3"),
        ("Gemini 3.8 Flash", "gemini-3.8-flash"),
        ("Grok 4.7", "grok-4.7"),
    ]
    out = []
    for printed, slug in slices:
        pattern = re.compile(
            r"^\s*"
            + re.escape(printed)
            + r"\s{2,}([0-9]+)\s{2,}([0-9]+\.[0-9])%\s{2,}([0-9]+\.[0-9]+)\s*$"
        )
        match = one(rows, pattern, "Table C1", printed)
        out.append(
            {
                "slug": slug,
                "label": printed,
                "trials_graded": int(match.group(1)),
                "agreement_percent": match.group(2),
                "cohens_kappa": match.group(3),
            }
        )
    by_slug = {r["slug"]: r for r in out}
    assert by_slug["all-trials"]["trials_graded"] == 387, "Table C1: all trials != 387"
    assert (
        by_slug["tasks-with-experimental-records"]["trials_graded"]
        + by_slug["construction-tasks"]["trials_graded"]
        == 387
    ), "Table C1: task slices do not sum to the all-trials total"
    per_system = sum(
        r["trials_graded"]
        for r in out
        if r["slug"] not in {"all-trials", "tasks-with-experimental-records", "construction-tasks"}
    )
    assert per_system == 387, "Table C1: per-system slices do not sum to 387"
    return out


def parse_table_d1(lines, captions):
    """Token usage, cost and runtime per protocol-development attempt."""
    _, _, rows = region(lines, captions, "Table D1")
    out = []
    for system in SYSTEMS:
        pattern = re.compile(
            r"^\s*"
            + re.escape(system)
            + r"\s{2,}(low|medium|high|xhigh|max)\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)\s+"
            r"([0-9]+\.[0-9]+)\s+([0-9]+\.[0-9])\s+([0-9]+)\s+([0-9]+\.[0-9]+)\s*$"
        )
        hits = [m for m in (pattern.match(r) for r in rows) if m]
        assert len(hits) == 3, f"Table D1: {system}: expected 3 lanes, got {len(hits)}"
        for match in hits:
            out.append(
                {
                    "system": system,
                    "effort": match.group(1),
                    "input_k": match.group(2),
                    "cached_k": match.group(3),
                    "output_k": match.group(4),
                    "cost_per_attempt_usd": match.group(5),
                    "median_minutes": match.group(6),
                    "cap_hits": int(match.group(7)),
                    "design_cost_usd": match.group(8),
                }
            )
    assert len(out) == 24, "Table D1: expected 24 lanes"
    return out


def parse_table_d2(lines, captions):
    """Complete performance metrics across all 24 evaluated lanes."""
    _, _, rows = region(lines, captions, "Table D2")
    out = []
    for system in SYSTEMS:
        pattern = re.compile(
            r"^\s*"
            + re.escape(system)
            + r"\s{2,}(low|mid|top)\s+(low|medium|high|xhigh|max)\s+"
            + CI
            + r"\s+"
            + CI
            + r"\s+"
            + CI
            + r"\s+([0-9]+\.[0-9]+)\s+([0-9]+\.[0-9]+)\s*$"
        )
        hits = [m for m in (pattern.match(r) for r in rows) if m]
        assert len(hits) == 3, f"Table D2: {system}: expected 3 lanes, got {len(hits)}"
        tiers = [m.group(1) for m in hits]
        assert tiers == ["low", "mid", "top"], f"Table D2: {system}: tier order {tiers}"
        for match in hits:
            out.append(
                {
                    "system": system,
                    "tier": match.group(1),
                    "effort": match.group(2),
                    "protocol_development": list(match.group(3, 4, 5)),
                    "construct_design": list(match.group(6, 7, 8)),
                    "aggregate": list(match.group(9, 10, 11)),
                    "protocol_cost_usd": match.group(12),
                    "construct_cost_usd": match.group(13),
                }
            )
    assert len(out) == 24, "Table D2: expected 24 lanes"
    return out


def parse_table_e1(lines, captions):
    """First blocking failures by system for protocol-development tasks at top effort."""
    _, _, rows = region(lines, captions, "Table E1")
    columns = [
        "graded",
        "passed",
        "primer_design",
        "final_tube_not_single_product",
        "bench_step_failed",
        "wrong_sequence",
        "parser_rejected",
        "no_protocol",
    ]
    out = []
    for system in SYSTEMS:
        pattern = re.compile(
            r"^\s*" + re.escape(system) + r"\s{2,}" + r"\s+".join([r"([0-9]+)"] * 8) + r"\s*$"
        )
        match = one(rows, pattern, "Table E1", system)
        row = {"system": system}
        row.update({c: int(v) for c, v in zip(columns, match.groups())})
        assert (
            sum(row[c] for c in columns[1:]) == row["graded"]
        ), f"Table E1: {system}: category counts do not sum to the graded total"
        out.append(row)
    return out


def parse_table_e2(lines, captions):
    """Execution and grading statuses for protocol-development attempts."""
    _, _, rows = region(lines, captions, "Table E2")
    columns = [
        "recorded",
        "graded",
        "no_protocol",
        "time_cap",
        "refused",
        "parser_rejected",
        "unscored",
    ]
    out = []
    for system in SYSTEMS:
        pattern = re.compile(
            r"^\s*" + re.escape(system) + r"\s{2,}" + r"\s+".join([r"([0-9]+)"] * 7) + r"\s*$"
        )
        match = one(rows, pattern, "Table E2", system)
        row = {"system": system}
        row.update({c: int(v) for c, v in zip(columns, match.groups())})
        out.append(row)
    return out


def parse_table_f1(lines, captions):
    """Adjudication outcomes for construct-design submissions."""
    _, _, rows = region(lines, captions, "Table F1")
    outcomes = [
        ("Shipped grader result stands", "shipped-grader-result-stands"),
        ("A: passes after value-preserving re-expression of the", "a-value-preserving-re-expression"),
        ("A : engine source checks verify product and route as", "a-prime-engine-source-checks"),
        ("B: passes after manual verification of the engine", "b-manual-verification"),
        ("0: still fails after allowed re-expression", "zero-still-fails"),
        ("Unscored (harness failure)", "unscored-harness-failure"),
    ]
    out = []
    for printed, slug in outcomes:
        pattern = re.compile(
            r"^\s*" + re.escape(printed).replace(r"A\ :", r"A(?:′|\')?\s*:")
            + r"\s{2,}([0-9]+)\s{2,}([0-9]+)\s*$"
        )
        match = one(rows, pattern, "Table F1", printed)
        out.append(
            {
                "slug": slug,
                "label": printed,
                "top_tier_trials": int(match.group(1)),
                "all_lanes_trials": int(match.group(2)),
            }
        )
    total = one(
        rows,
        re.compile(r"^\s*Total\s{2,}([0-9]+)\s{2,}([0-9]+)\s*$"),
        "Table F1",
        "Total",
    )
    assert int(total.group(1)) == 600, "Table F1: top-tier total is not 600"
    assert int(total.group(2)) == 1800, "Table F1: all-lane total is not 1800"
    assert (
        sum(r["top_tier_trials"] for r in out) == 600
    ), "Table F1: top-tier outcomes do not sum to 600"
    assert (
        sum(r["all_lanes_trials"] for r in out) == 1800
    ), "Table F1: all-lane outcomes do not sum to 1800"
    return out


def parse_table_f3(lines, captions):
    """Judge threshold on the ten rubric-judged tasks at top effort."""
    _, _, rows = region(lines, captions, "Table F3")
    out = []
    for system in SYSTEMS:
        pattern = re.compile(
            r"^\s*" + re.escape(system) + r"\s{2,}([0-9]+)\s{2,}([0-9]+)\s{2,}([0-9]+)\s*$"
        )
        match = one(rows, pattern, "Table F3", system)
        out.append(
            {
                "system": system,
                "attempts_on_judged_tasks": int(match.group(1)),
                "passed_deterministic": int(match.group(2)),
                "judge_below_0_9": int(match.group(3)),
            }
        )
    total = one(
        rows,
        re.compile(r"^\s*Total\s{2,}([0-9]+)\s{2,}([0-9]+)\s{2,}([0-9]+)\s*$"),
        "Table F3",
        "Total",
    )
    assert [int(g) for g in total.groups()] == [400, 142, 34], "Table F3: totals changed"
    assert sum(r["attempts_on_judged_tasks"] for r in out) == 400, "Table F3: attempts != 400"
    assert sum(r["passed_deterministic"] for r in out) == 142, "Table F3: deterministic != 142"
    assert sum(r["judge_below_0_9"] for r in out) == 34, "Table F3: judge-below != 34"
    return out


def parse_table_g1(lines, captions):
    """Protocol-development pass@k and task coverage at top effort."""
    _, _, rows = region(lines, captions, "Table G1")
    out = []
    for system in SYSTEMS:
        pattern = re.compile(
            r"^\s*"
            + re.escape(system)
            + r"\s{2,}"
            + CI
            + r"\s+"
            + CI
            + r"\s+"
            + CI
            + r"\s+([0-9]+)\s+([0-9]+)\s*(.*?)\s*$"
        )
        match = one(rows, pattern, "Table G1", system)
        out.append(
            {
                "system": system,
                "pass_at_1": list(match.group(1, 2, 3)),
                "pass_at_5": list(match.group(4, 5, 6)),
                "pass_at_10": list(match.group(7, 8, 9)),
                "solved_at_least_once": int(match.group(10)),
                "solved_all": int(match.group(11)),
                "note": match.group(12),
            }
        )
    return out


def parse_table_g2(lines, captions):
    """Construct-design solves per task and system at top effort."""
    _, _, rows = region(lines, captions, "Table G2")
    out = []
    for task in CONSTRUCT_TASKS_G2:
        pattern = re.compile(
            r"^\s*" + re.escape(task) + r"\s{2,}" + r"\s+".join([r"([0-5])/5"] * 8) + r"\s*$"
        )
        match = one(rows, pattern, "Table G2", task)
        out.append(
            {
                "task": task,
                "solves": {
                    column: int(value)
                    for column, value in zip(TASK_TABLE_COLUMNS, match.groups())
                },
            }
        )
    assert len(out) == 15, "Table G2: expected 15 task rows"
    return out


def cross_checks(tables):
    """Arithmetic agreement between the tables, asserted rather than assumed."""
    checks = []

    # Table 2 is the eight top-tier rows of Table D2.
    top = {r["system"]: r for r in tables["table_d2"] if r["tier"] == "top"}
    for row in tables["table_2"]:
        d2 = top[row["system"]]
        assert row["effort"] == d2["effort"], f"{row['system']}: effort differs"
        for key in ("protocol_development", "construct_design", "aggregate"):
            assert row[key] == d2[key], f"{row['system']}: {key} differs between Tables 2 and D2"
    checks.append("Table 2 equals the eight top-tier rows of Table D2, cell for cell.")

    # Construct-design pass rate = sum of Table G2 solves / 75.
    for row in tables["table_2"]:
        solved = sum(t["solves"][row["system"]] for t in tables["table_g2"])
        expected = round(solved / 75 * 100, 1)
        printed = float(row["construct_design"][0])
        assert abs(expected - printed) < 0.06, (
            f"{row['system']}: Table G2 solves {solved}/75 give {expected}, "
            f"Table 2 prints {printed}"
        )
    checks.append(
        "Each system's Table 2 construct-design pass rate equals its Table G2 column "
        "sum over 75 attempts (15 tasks x 5)."
    )

    # Protocol-development pass rate = Table E1 passed / 500.
    e1 = {r["system"]: r for r in tables["table_e1"]}
    for row in tables["table_2"]:
        passed = e1[row["system"]]["passed"]
        expected = round(passed / 500 * 100, 1)
        printed = float(row["protocol_development"][0])
        assert abs(expected - printed) < 0.051, (
            f"{row['system']}: Table E1 passed {passed}/500 give {expected}, "
            f"Table 2 prints {printed}"
        )
    checks.append(
        "Each system's Table 2 protocol-development pass rate equals its Table E1 "
        "passed count over 500 recorded attempts (50 tasks x 10), including the two "
        "systems whose graded count is below 500."
    )

    # pass@10 = solved at least once / 50.
    for row in tables["table_g1"]:
        expected = round(row["solved_at_least_once"] / 50 * 100, 1)
        printed = float(row["pass_at_10"][0])
        assert abs(expected - printed) < 0.051, f"{row['system']}: pass@10 vs solved count"
    checks.append(
        "Each system's Table G1 pass@10 equals its 'Solved >=1' count over the 50 "
        "protocol-development tasks."
    )

    # Table G1 pass@1 repeats the Table 2 protocol-development column.
    g1 = {r["system"]: r for r in tables["table_g1"]}
    for row in tables["table_2"]:
        assert (
            g1[row["system"]]["pass_at_1"] == row["protocol_development"]
        ), f"{row['system']}: Table G1 pass@1 differs from Table 2"
    checks.append("Table G1 pass@1 repeats the Table 2 protocol-development column.")

    # Aggregate = (50 * protocol + 15 * construct) / 65, within printed rounding.
    worst = 0.0
    for row in tables["table_d2"]:
        protocol = float(row["protocol_development"][0])
        construct = float(row["construct_design"][0])
        aggregate = float(row["aggregate"][0])
        expected = (50 * protocol + 15 * construct) / 65
        worst = max(worst, abs(expected - aggregate))
    assert worst < 0.06, f"aggregate weighting off by {worst}"
    checks.append(
        "Every Table D2 aggregate equals (50 x protocol-development + 15 x "
        f"construct-design) / 65 to within {worst:.2f} points of the printed value, "
        "the residue of rounding the inputs."
    )

    # Granularity: protocol-development rates are multiples of 1/500, construct of 1/75.
    off_grid = []
    for row in tables["table_d2"]:
        protocol = float(row["protocol_development"][0])
        construct = float(row["construct_design"][0])
        if abs(round(protocol / 0.2) * 0.2 - protocol) > 0.001:
            off_grid.append((row["system"], row["effort"], "protocol_development", protocol))
        if abs(round(construct * 0.75) / 0.75 - construct) > 0.051:
            off_grid.append((row["system"], row["effort"], "construct_design", construct))
    checks.append(
        "Pass rates off the attempt grid (protocol development 1/500 = 0.2 points, "
        f"construct design 1/75 = 1.33 points): {off_grid or 'none'}"
    )

    # Table D1 and Table D2 report the same per-attempt costs.
    d1 = {(r["system"], r["effort"]): r for r in tables["table_d1"]}
    for row in tables["table_d2"]:
        key = (row["system"], row["effort"])
        assert (
            d1[key]["cost_per_attempt_usd"] == row["protocol_cost_usd"]
        ), f"{key}: protocol cost differs between Tables D1 and D2"
        assert (
            d1[key]["design_cost_usd"] == row["construct_cost_usd"]
        ), f"{key}: construct cost differs between Tables D1 and D2"
    checks.append(
        "Table D1 'Cost/attempt' and 'Design cost' equal Table D2 'Proto ($)' and "
        "'Const ($)' for all 24 lanes."
    )

    return checks, off_grid


def main():
    lines = load_lines()
    captions = caption_index(lines)
    tables = {
        "table_1": parse_table_1(lines, captions),
        "table_2": parse_table_2(lines, captions),
        "table_a1": parse_table_a1(lines, captions),
        "table_b1": parse_table_b1(lines, captions),
        "table_c1": parse_table_c1(lines, captions),
        "table_d1": parse_table_d1(lines, captions),
        "table_d2": parse_table_d2(lines, captions),
        "table_e1": parse_table_e1(lines, captions),
        "table_e2": parse_table_e2(lines, captions),
        "table_f1": parse_table_f1(lines, captions),
        "table_f3": parse_table_f3(lines, captions),
        "table_g1": parse_table_g1(lines, captions),
        "table_g2": parse_table_g2(lines, captions),
    }
    checks, off_grid = cross_checks(tables)
    payload = {
        "source": {
            "url": "https://arxiv.org/pdf/2610.33355v1",
            "pdf_sha256": "6f5044b1bbbd81ad86b23cb536e2cae6428e0d9126f11546041355518febdc39",
            "text_layer_sha256": TEXT_SHA256,
        },
        "tables": tables,
        "cross_checks": checks,
        "off_grid_values": off_grid,
    }
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1, sort_keys=True)
        handle.write("\n")
    for check in checks:
        print("ok:", check)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
