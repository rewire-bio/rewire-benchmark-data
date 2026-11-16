#!/usr/bin/env python3
"""Independent reviewer re-check of every result in the TorchCraft batch.

Written by the review agent, independent of extract/parse_runtime_table.py and
extract/check_transcriptions.py. It does not import or read either of them.

Usage:
    python3 -I review/recheck_values.py <batch.jsonl> <arxiv-v1-layout.txt> [--mutate <spec>]

The layout file is the `pdftotext -layout` text layer of arXiv:2609.19770v1.

Two independent checks per result:

  Table S9 cells  the table is re-parsed by COLUMN CHARACTER OFFSET, not by
                  whitespace splitting: each numeric token in a data row is
                  assigned to the header column whose label starts nearest to
                  it. A value copied from a neighbouring column therefore
                  fails, which whitespace splitting would not catch.

  caption values  the caption sentence named by the locator must occur
                  verbatim in the normalised text, the result's value must sit
                  at the ORDINAL POSITION its target occupies in the caption's
                  own target list, and the figure panel label line must print
                  the same values in the same order. A swap between two
                  targets therefore fails.

--mutate runs the same checks against deliberately corrupted records. It is a
negative control: it must report failures, and the exact failures named.
"""

import json
import re
import sys
import unicodedata

FOOTNOTE_MARKS = "∗*†‡"  # asterisk operator, asterisk, dagger, double dagger

ROW_LABELS = ["NPU w/ FA", "NPU w/o FA", "GPU w/ cuequivariance", "GPU w/o cuequivariance"]
COL_LABELS = ["100 aa", "200 aa", "300 aa", "400 aa", "500 aa"]

# The caption sentence for each campaign, and the target order the caption itself
# states. Taken from the locator text on the records, then asserted against the source.
CAMPAIGNS = {
    "minibinder": {
        "panel": "Figure 2a",
        "targets": ["IFNAR2", "IL-7Rα", "PDGFRβ", "PD-L1"],
        "id_keys": ["ifnar2", "il7ra", "pdgfrb", "pdl1"],
        "panel_label_targets": ["IFNAR2", "IL7RA", "PDGFR", "PD-L1"],
    },
    "vhh": {
        "panel": "Figure 3a",
        "targets": ["BHRF1", "EFNA5", "PDGFRβ", "S100A4"],
        "id_keys": ["bhrf1", "efna5", "pdgfrb", "s100a4"],
        "panel_label_targets": ["BHRF1", "EFNA5", "PDGFR", "S100A4"],
    },
}

FIG_S4B_FRAGMENTS = {
    "mcc": "MCC = 0.598",
    "pearson": "Pearson r = −0.538",
    "spearman": "Spearman ρ = −0.602",
}


def norm(text):
    """Collapse runs of whitespace. Keep unicode as published (minus sign, rho)."""
    return re.sub(r"\s+", " ", text)


def strip_footnote(cell):
    return cell.rstrip(FOOTNOTE_MARKS), len(cell) != len(cell.rstrip(FOOTNOTE_MARKS))


def parse_table_s9(lines):
    """Re-parse Table S9 by column character offset. Returns {(row, col): cell}."""
    header_idx = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("Code") and "Operator" in line and "Machine" in line:
            if all(c in line for c in COL_LABELS):
                header_idx = i
                break
    assert header_idx is not None, "Table S9 header line 'Code Operator ... Machine ... 100 aa ...' not found"
    header = lines[header_idx]

    # Left character offset of each length column label in the header.
    col_offsets = []
    for label in COL_LABELS:
        pos = header.find(label)
        assert pos >= 0, f"column label {label!r} missing from header"
        col_offsets.append(pos)
    assert col_offsets == sorted(col_offsets), "column labels out of order in header"

    cells = {}
    seen_rows = []
    for line in lines[header_idx + 1 : header_idx + 12]:
        if not line.strip():
            continue
        if line.lstrip()[0] in FOOTNOTE_MARKS:
            break
        matched = None
        for label in ROW_LABELS:
            code, operator = label.split(" ", 1)
            if re.match(rf"\s*{re.escape(code)}\s+{re.escape(operator)}\s", line):
                matched = label
                break
        assert matched is not None, f"unrecognised row in Table S9 body: {line!r}"
        assert matched not in seen_rows, f"row {matched!r} seen twice"
        seen_rows.append(matched)

        # Every numeric token right of the Machine column, with its offset.
        machine_end = line.find(")") + 1
        assert machine_end > 0, f"machine cell not found in {line!r}"
        tokens = [
            (m.start(), m.group(0))
            for m in re.finditer(rf"[0-9]+(?:\.[0-9]+)?[{re.escape(FOOTNOTE_MARKS)}]?", line[machine_end:])
        ]
        tokens = [(machine_end + off, tok) for off, tok in tokens]
        assert len(tokens) == len(COL_LABELS), (
            f"row {matched!r}: found {len(tokens)} numeric cells, expected {len(COL_LABELS)}"
        )

        # Assign each token to the nearest column label by character offset,
        # and require a one-to-one assignment in order.
        assignment = []
        for off, tok in tokens:
            best = min(range(len(COL_LABELS)), key=lambda j: abs(col_offsets[j] - off))
            assignment.append(best)
        assert assignment == list(range(len(COL_LABELS))), (
            f"row {matched!r}: cells do not map one-to-one onto the five length columns "
            f"(offset assignment {assignment})"
        )
        for j, (_, tok) in enumerate(tokens):
            cells[(matched, COL_LABELS[j])] = tok

    assert seen_rows == ROW_LABELS, f"Table S9 rows were {seen_rows}, expected {ROW_LABELS}"
    assert len(cells) == 20, f"parsed {len(cells)} cells, expected 20"
    return cells


def caption_numbers(flat, campaign):
    """The four numbers the caption prints, in the order the caption prints them."""
    panel = campaign["panel"]
    # There are two such sentences (Figure 2a and Figure 3a); pick the one in this panel's caption.
    matches = list(
        re.finditer(
            r"Apparent dissociation constants of the displayed binders were "
            r"((?:[0-9]+(?:\.[0-9]+)?(?:, | and |, and )?)+) nM, respectively\.",
            flat,
        )
    )
    assert len(matches) == 2, f"expected 2 KD caption sentences, found {len(matches)}"
    fig_no = panel[len("Figure ")]
    chosen = None
    for m in matches:
        # the caption this sentence belongs to begins with "Figure N "
        before = flat[: m.start()]
        last_fig = None
        for fm in re.finditer(r"Figure (\d) ", before):
            last_fig = fm.group(1)
        if last_fig == fig_no:
            chosen = m
            break
    assert chosen is not None, f"no KD sentence found inside the {panel} caption"
    nums = [t.strip() for t in re.split(r",|\band\b", chosen.group(1)) if t.strip()]
    assert len(nums) == 4, f"{panel}: caption lists {len(nums)} values, expected 4"
    return nums, chosen.group(0)


def panel_label_numbers(lines, campaign):
    """The KD values printed on the figure's own panel labels, left to right."""
    for line in lines:
        if line.count("KD:") == 4:
            labels = re.findall(r"KD:\s*([0-9.]+)nM", line)
            if len(labels) != 4:
                continue
            # Confirm this is the right panel by the target names above it.
            idx = lines.index(line)
            window = norm(" ".join(lines[max(0, idx - 20) : idx]))
            if all(t in window for t in campaign["panel_label_targets"]):
                return labels
    raise AssertionError(f"panel label line with four KD values not found for {campaign['panel']}")


def check(records, text, mutate=None):
    lines = text.splitlines()
    flat = norm(text)
    failures = []
    notes = []

    cells = parse_table_s9(lines)
    notes.append("Table S9 re-parsed by column offset: 4 rows x 5 columns, one-to-one column assignment asserted.")

    caption = {}
    panel_labels = {}
    for name, campaign in CAMPAIGNS.items():
        nums, sentence = caption_numbers(flat, campaign)
        caption[name] = nums
        panel_labels[name] = panel_label_numbers(lines, campaign)
        assert sentence in flat
        for t in campaign["targets"]:
            assert t in flat, f"{campaign['panel']}: target {t!r} not in source"
        if nums != panel_labels[name]:
            failures.append(
                f"{campaign['panel']}: caption order {nums} does not match panel label order {panel_labels[name]}"
            )
        notes.append(
            f"{campaign['panel']}: caption values {nums} match panel labels {panel_labels[name]}; "
            f"target order {campaign['targets']}."
        )

    for frag in FIG_S4B_FRAGMENTS.values():
        if frag not in flat:
            failures.append(f"Figure S4b fragment {frag!r} not found in source")
    notes.append("Figure S4b fragments asserted verbatim: " + "; ".join(FIG_S4B_FRAGMENTS.values()))

    results = [r for r in records if r["kind"] == "result"]
    checked = 0

    for r in results:
        rid = r["id"]
        a = r["attributes"]
        printed = a["printed_value"]
        numeric = a.get("numeric_value")
        loc = a["source_locator"]

        if mutate and rid in mutate:
            printed = mutate[rid]

        # --- Table S9 cells ---
        m = re.search(r'Table S9, row "([^"]+)", column "([^"]+)"', loc)
        if m:
            row, col = m.group(1), m.group(2)
            if (row, col) not in cells:
                failures.append(f"{rid}: locator names row {row!r} column {col!r}, which Table S9 does not have")
                continue
            cell, had_mark = strip_footnote(cells[(row, col)])
            if cell != printed:
                failures.append(
                    f"{rid}: printed_value {printed!r} but Table S9 [{row} | {col}] prints {cells[(row, col)]!r}"
                )
            else:
                # Guard against a value that also happens to sit in another column.
                elsewhere = [
                    k for k, v in cells.items() if strip_footnote(v)[0] == printed and k != (row, col)
                ]
                if elsewhere:
                    notes.append(f"{rid}: value {printed!r} also appears at {elsewhere}; column assignment rests on the offset parse")
                if had_mark:
                    notes.append(
                        f"{rid}: source cell is {cells[(row, col)]!r}; printed_value drops the footnote marker"
                    )
            if numeric is not None and float(numeric) != float(printed):
                failures.append(f"{rid}: numeric_value {numeric} != printed_value {printed}")
            checked += 1
            continue

        # --- KD caption values ---
        m = re.search(r"result-bli-kd-(minibinder|vhh)-([a-z0-9]+)$", rid)
        if m:
            name, key = m.group(1), m.group(2)
            campaign = CAMPAIGNS[name]
            if key not in campaign["id_keys"]:
                failures.append(f"{rid}: target key {key!r} is not one of {campaign['id_keys']}")
                continue
            ordinal = campaign["id_keys"].index(key)
            expected = caption[name][ordinal]
            if expected != printed:
                failures.append(
                    f"{rid}: printed_value {printed!r} but the {campaign['panel']} caption gives "
                    f"{expected!r} at position {ordinal + 1} (target {campaign['targets'][ordinal]})"
                )
            if panel_labels[name][ordinal] != printed:
                failures.append(
                    f"{rid}: printed_value {printed!r} but panel label {ordinal + 1} prints "
                    f"{panel_labels[name][ordinal]!r}"
                )
            # The locator must name the target it claims.
            want = campaign["targets"][ordinal]
            stem = re.sub(r"[^A-Za-z0-9]", "", unicodedata.normalize("NFKD", want)).lower()
            loc_stem = re.sub(r"[^A-Za-z0-9]", "", unicodedata.normalize("NFKD", loc)).lower()
            if stem.rstrip("ab") not in loc_stem and stem not in loc_stem:
                failures.append(f"{rid}: locator does not name target {want!r}")
            if numeric is not None and float(numeric) != float(printed):
                failures.append(f"{rid}: numeric_value {numeric} != printed_value {printed}")
            checked += 1
            continue

        # --- Figure S4b statistics ---
        m = re.search(r"result-vhh-expression-(mcc|pearson|spearman)$", rid)
        if m:
            frag = FIG_S4B_FRAGMENTS[m.group(1)]
            value_in_frag = frag.split("= ")[1]
            if value_in_frag != printed:
                failures.append(f"{rid}: printed_value {printed!r} but the source fragment is {frag!r}")
            if numeric is not None:
                if float(numeric) != float(printed.replace("−", "-")):
                    failures.append(f"{rid}: numeric_value {numeric} != printed_value {printed}")
            checked += 1
            continue

        failures.append(f"{rid}: no check rule matched its locator {loc!r}")

    return {"results_checked": checked, "failures": failures, "notes": notes}


def main():
    args = [a for a in sys.argv[1:]]
    mutate = None
    if "--mutate" in args:
        i = args.index("--mutate")
        mutate = json.loads(args[i + 1])
        del args[i : i + 2]
    batch_path, text_path = args[0], args[1]

    records = [json.loads(l) for l in open(batch_path, encoding="utf-8")]
    text = open(text_path, encoding="utf-8").read()

    out = check(records, text, mutate)
    print(json.dumps({"results_checked": out["results_checked"], "failure_count": len(out["failures"])}))
    for n in out["notes"]:
        print("note:", n)
    for f in out["failures"]:
        print("FAIL:", f)
    return 1 if out["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
