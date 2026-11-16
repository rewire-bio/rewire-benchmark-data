#!/usr/bin/env python3
"""Independent re-read of every POISK result against the pinned PDF text layer.

Written for the review pass. It does not import or reuse extract/build_batch.py.

Unlike a row-level check, this assigns every printed cell to a column by its
character geometry in the `pdftotext -layout` text layer: each column's span is
taken from the label text in the table's own header line, each body value is
tokenised with its offsets, and a value is only accepted for a column when that
column's centre is the nearest one by a margin. A value copied from a
neighbouring column in the same row therefore fails, which is what the
repository's `check-values` cannot show for Tables 2 and 7.

Usage:
  python3 check_values_independent.py <layout.txt> <batch.jsonl> [out.tsv]
  python3 check_values_independent.py <layout.txt> <batch.jsonl> - --control swap
  python3 check_values_independent.py <layout.txt> <batch.jsonl> - --control shift

Exit code 0 when every result matches, 1 otherwise.
"""

import json
import re
import sys

LAYOUT_SHA256 = "e75c18130ca43770d2f0ed05ae96528759666c0e4fa08f7725f5a32b21187696"

ENGINES = [
    "AlphaFold-Multimer",
    "Boltz-2",
    "IntelliFold v2",
    "OpenFold3",
    "Protenix-v1",
    "Protenix-v2",
]

# Nearest-column tolerance and the margin the runner-up column must lose by,
# both in characters of the layout text.
TOL = 5
MARGIN = 3

VALUE_RE = re.compile(r"^[0-9][0-9.,]*%?$")


def span_of(line, label):
    """Character span of `label` in `line`, requiring exactly one occurrence."""
    hits = [m.start() for m in re.finditer(re.escape(label), line)]
    if len(hits) != 1:
        raise AssertionError(f"label {label!r} occurs {len(hits)} times in {line!r}")
    return (hits[0], hits[0] + len(label))


def centre(span):
    return (span[0] + span[1]) / 2.0


def find_one(lines, needle, lo=0, hi=None):
    hi = len(lines) if hi is None else hi
    needles = needle if isinstance(needle, (list, tuple)) else [needle]
    hits = [i for i in range(lo, hi) if all(n in lines[i] for n in needles)]
    if len(hits) != 1:
        raise AssertionError(f"{needles!r} found on {len(hits)} lines in [{lo},{hi})")
    return hits[0]


def row_line(lines, label, lo, hi):
    """The one body line whose first token block is `label`."""
    hits = []
    for i in range(lo, hi):
        s = lines[i]
        if label in s and s.strip().startswith(label):
            hits.append(i)
    if len(hits) != 1:
        raise AssertionError(f"row {label!r} on {len(hits)} lines in [{lo},{hi})")
    return hits[0]


def cells(line, label, columns):
    """Assign each printed value in `line` to a column by geometry.

    `columns` is a list of (name, span). Returns {name: (value, span)}.
    Raises if the token count differs from the column count, if a value is not
    nearest to the column in its own left-to-right position, or if the
    runner-up column is within MARGIN characters.
    """
    lab = span_of(line, label)
    toks = [
        (m.start(), m.end(), m.group())
        for m in re.finditer(r"\S+", line)
        if m.start() >= lab[1]
    ]
    bad = [t for t in toks if not VALUE_RE.match(t[2])]
    if bad:
        raise AssertionError(f"non-value tokens after row label {label!r}: {bad}")
    if len(toks) != len(columns):
        raise AssertionError(
            f"row {label!r}: {len(toks)} values for {len(columns)} columns: {toks}"
        )
    out = {}
    for i, (start, end, text) in enumerate(toks):
        c = centre((start, end))
        dists = sorted(
            (abs(c - centre(span)), name) for name, span in columns
        )
        nearest_d, nearest_name = dists[0]
        runner_d, runner_name = dists[1] if len(dists) > 1 else (1e9, None)
        want = columns[i][0]
        if nearest_name != want:
            raise AssertionError(
                f"row {label!r} value {text!r} at {start}: nearest column is "
                f"{nearest_name!r}, not the {i}th column {want!r}"
            )
        if nearest_d > TOL:
            raise AssertionError(
                f"row {label!r} value {text!r}: {nearest_d:.1f} chars from "
                f"column {want!r}, over the tolerance {TOL}"
            )
        if runner_d - nearest_d < MARGIN:
            raise AssertionError(
                f"row {label!r} value {text!r}: column {want!r} and "
                f"{runner_name!r} are not separated by {MARGIN} chars"
            )
        out[want] = (text, (start, end))
    return out


def parse_tables(lines):
    """Return {(table, row, column): printed_value} read by column geometry."""
    grid = {}

    # ---- Table 1 -----------------------------------------------------------
    cap = find_one(lines, "Table 1: Summary of benchmark performance for six structure prediction models")
    grp = find_one(lines, ["Cohen’s d", "Accuracy at", "1-in-50"], cap, cap + 20)
    sub = find_one(lines, ["ipTM", "ipSAE", "50% Pairs", "Top-1 Acc."], cap, cap + 20)
    t1_cols = []
    for group, label in [
        ("Cohen’s d", "ipTM"),
        ("Cohen’s d", "ipSAE"),
        ("Accuracy at", "50% Pairs"),
        ("1-in-50", "Top-1 Acc."),
    ]:
        sub_span = span_of(lines[sub], label)
        grp_span = span_of(lines[grp], group)
        # the group label must sit over its own sub-columns
        if not (grp_span[0] - 8 <= centre(sub_span) <= grp_span[1] + 8):
            raise AssertionError(
                f"Table 1: sub-column {label!r} is not under group {group!r}"
            )
        t1_cols.append((label, sub_span))
    for eng in ENGINES:
        i = row_line(lines, eng, sub, sub + 12)
        for col, (val, _) in cells(lines[i], eng, t1_cols).items():
            grid[(1, eng, col)] = val

    # ---- Table 2 -----------------------------------------------------------
    cap = find_one(lines, "Table 2: Epitope Recovery Rate by Engine")
    h1 = find_one(lines, "Epitope Recovery", cap + 1, cap + 8)
    h2 = find_one(lines, "Records (%)", cap + 1, cap + 8)
    s1 = span_of(lines[h1], "Epitope Recovery")
    s2 = span_of(lines[h2], "Records (%)")
    t2_cols = [("Epitope Recovery Records (%)", (min(s1[0], s2[0]), max(s1[1], s2[1])))]
    for eng in ENGINES:
        i = row_line(lines, eng, h2, h2 + 12)
        for col, (val, _) in cells(lines[i], eng, t2_cols).items():
            grid[(2, eng, col)] = val

    # ---- Table 7 -----------------------------------------------------------
    cap = find_one(lines, "Table 7: Pairwise binder-versus-decoy accuracy as a function of coverage")
    cov = find_one(lines, "Coverage", cap + 1, cap + 12)
    mod = find_one(lines, ["Model", "Ties"], cap + 1, cap + 12)
    pct = find_one(lines, ["100%", "75%", "50%", "25%", "10%"], cap + 1, cap + 12)
    ties_span = span_of(lines[mod], "Ties")
    cov_spans = [(lbl, span_of(lines[pct], lbl)) for lbl in ["100%", "75%", "50%", "25%", "10%"]]
    cov_group = span_of(lines[cov], "Coverage")
    # the Coverage group must span the five coverage columns and must not
    # reach the Ties column: that is what puts Ties outside the group.
    lo = min(s[0] for _, s in cov_spans)
    hi = max(s[1] for _, s in cov_spans)
    if not (lo - 2 <= centre(cov_group) <= hi + 2):
        raise AssertionError("Table 7: 'Coverage' is not centred over the five coverage columns")
    if cov_group[0] <= ties_span[1]:
        raise AssertionError("Table 7: 'Coverage' group reaches the 'Ties' column")
    t7_cols = [("Ties", ties_span)] + cov_spans
    for eng in ENGINES:
        i = row_line(lines, eng, pct, pct + 12)
        for col, (val, _) in cells(lines[i], eng, t7_cols).items():
            grid[(7, eng, col)] = val

    # ---- Table 8 -----------------------------------------------------------
    cap = find_one(lines, "Table 8: Top-1 accuracy (%) in the 1-in-50 screening simulation")
    hdr = find_one(lines, ["UniProt", "AF-M", "Prot-v1", "Prot-v2"], cap + 1, cap + 14)
    t8_cols = [
        (lbl, span_of(lines[hdr], lbl))
        for lbl in ["AF-M", "Boltz-2", "IF v2", "OF3", "Prot-v1", "Prot-v2"]
    ]
    body_lo = hdr + 1
    construct = [
        i
        for i in range(body_lo, body_lo + 40)
        if re.match(r"^\s+\d{1,2}\s+[A-Z][0-9A-Z]{5}\s", lines[i])
    ]
    if len(construct) != 27:
        raise AssertionError(f"Table 8: {len(construct)} construct rows, expected 27")
    for label, table_key in [
        ("Mean over targets", 8),
        ("SD across targets (pp)", "8-sd-targets"),
        ("SD across seeds (pp)", "8-sd-seeds"),
    ]:
        i = row_line(lines, label, body_lo, body_lo + 40)
        for col, (val, _) in cells(lines[i], label, t8_cols).items():
            grid[(table_key, label, col)] = val
    return grid


LOC_TABLE = re.compile(
    r"^Table (\d), row “(.+?)”, column “(.+?)”"
    r"(?:, sub-column “(.+?)”)?$"
)
LOC_TABLE_PLAIN = re.compile(
    r'^Table (\d), row "(.+?)", column "(.+?)"(?:, sub-column "(.+?)")?$'
)

# The six values the paper prints only in prose. Each entry is the sentence the
# locator names, the engine the value belongs to and its position in that
# sentence, read by hand from the text layer.
PROSE = {
    "poisk-20261115-result-protenix-v2-screen-1in50-top10": (
        "Protenix-v2 and IntelliFold\nv2 demonstrated comparable retrieval in broader rankings, placing the true binder in the Top-10 in\n54.7% and 56.0% of cases, respectively.",
        "54.7%",
        "first of the two values, matching the first engine named (Protenix-v2)",
    ),
    "poisk-20261115-result-intellifold-v2-screen-1in50-top10": (
        "Protenix-v2 and IntelliFold\nv2 demonstrated comparable retrieval in broader rankings, placing the true binder in the Top-10 in\n54.7% and 56.0% of cases, respectively.",
        "56.0%",
        "second of the two values, matching the second engine named (IntelliFold v2)",
    ),
    "poisk-20261115-result-consensus-k3-dockq-0-23-accuracy": (
        "When at least three models agree on a pose at a DockQ threshold of 0.23, the pairwise\naccuracy is 73.1% and covers 54.2% of the pairs.",
        "73.1%",
        "the value introduced by ‘the pairwise accuracy is’",
    ),
    "poisk-20261115-result-consensus-k3-dockq-0-23-coverage": (
        "When at least three models agree on a pose at a DockQ threshold of 0.23, the pairwise\naccuracy is 73.1% and covers 54.2% of the pairs.",
        "54.2%",
        "the value introduced by ‘covers’",
    ),
    "poisk-20261115-result-consensus-k3-dockq-0-80-accuracy": (
        "For instance, at k ≥ 3 and DockQ ≥ 0.80, accuracy reaches 96.8%.",
        "96.8%",
        "the value introduced by ‘accuracy reaches’",
    ),
    "poisk-20261115-result-consensus-k3-dockq-0-80-coverage": (
        "leaving only 3.0% of pairs eligible for classification at this stringent consensus level.",
        "3.0%",
        "the value introduced by ‘leaving only’",
    ),
}


def main():
    layout_path, batch_path = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else "-"
    control = None
    if "--control" in sys.argv:
        control = sys.argv[sys.argv.index("--control") + 1]

    import hashlib

    raw = open(layout_path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    if got != LAYOUT_SHA256:
        raise SystemExit(f"text layer sha256 {got} != pinned {LAYOUT_SHA256}")
    text = raw.decode("utf-8")
    lines = text.split("\n")
    flat = re.sub(r"\s+", " ", text)

    grid = parse_tables(lines)

    results = [
        json.loads(line)
        for line in open(batch_path, encoding="utf-8")
        if json.loads(line).get("kind") == "result"
    ]

    if control == "swap":
        a = next(r for r in results if r["id"] == "poisk-20261115-result-protenix-v2-pairwise-coverage-50-t7")
        b = next(r for r in results if r["id"] == "poisk-20261115-result-boltz-2-pairwise-coverage-50-t7")
        a["attributes"]["printed_value"], b["attributes"]["printed_value"] = (
            b["attributes"]["printed_value"],
            a["attributes"]["printed_value"],
        )
    elif control == "shift":
        # Table 7 AlphaFold-Multimer: take the 75% cell's value (0.643) and
        # claim it for the 50% column. Both are in the same row, so a
        # row-level check cannot see this.
        a = next(r for r in results if r["id"] == "poisk-20261115-result-alphafold-multimer-pairwise-coverage-50-t7")
        a["attributes"]["printed_value"] = "0.643"
        a["attributes"]["numeric_value"] = "0.643"
        # Table 2 Boltz-2: take the row below's value (56.5, IntelliFold v2).
        b = next(r for r in results if r["id"] == "poisk-20261115-result-boltz-2-epitope-recovery")
        b["attributes"]["printed_value"] = "56.5"
        b["attributes"]["numeric_value"] = "56.5"

    rows = []
    bad = 0
    for r in sorted(results, key=lambda r: r["id"]):
        a = r["attributes"]
        loc = a["source_locator"]
        printed = str(a["printed_value"])
        m = LOC_TABLE.match(loc) or LOC_TABLE_PLAIN.match(loc)
        if m:
            tno, row, col, subcol = m.group(1), m.group(2), m.group(3), m.group(4)
            key_col = subcol if subcol else col
            key = (int(tno), row, key_col)
            found = grid.get(key)
            if found is None:
                status, note = "column_not_found", f"no cell parsed at {key}"
            elif found == printed:
                status, note = "column_checked", "value sits in the named column by geometry"
            else:
                status, note = "mismatch", f"column holds {found!r}, record says {printed!r}"
        elif r["id"] in PROSE:
            sentence, value, which = PROSE[r["id"]]
            sent_flat = re.sub(r"\s+", " ", sentence)
            if sent_flat not in flat:
                status, note = "sentence_not_found", "locator sentence absent from the text layer"
            elif printed != value:
                status, note = "mismatch", f"sentence gives {value!r} as {which}, record says {printed!r}"
            else:
                status, note = "prose_checked", f"{which}; sentence present verbatim"
        else:
            status, note = "unhandled_locator", loc
        if status not in ("column_checked", "prose_checked"):
            bad += 1
        rows.append((r["id"], status, printed, loc, note))

    body = "id\tstatus\tprinted_value\tsource_locator\tnote\n" + "".join(
        "\t".join(x) + "\n" for x in rows
    )
    if out_path == "-":
        sys.stdout.write(body)
    else:
        open(out_path, "w", encoding="utf-8").write(body)

    counts = {}
    for _, status, _, _, _ in rows:
        counts[status] = counts.get(status, 0) + 1
    sys.stderr.write(json.dumps(counts, sort_keys=True) + "\n")
    sys.stderr.write(f"results: {len(rows)}, failing: {bad}\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
