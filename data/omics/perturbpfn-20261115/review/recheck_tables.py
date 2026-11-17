"""Reviewer re-read of every Table 1, 2 and 3 cell in batch.jsonl, written for the review pass.

Independent of extract/parse_tables.py and extract/check_tables.py: it does not import them and
does not split rows on runs of spaces. Instead it takes each table's column spans from the
character offsets of its own printed header line, finds every numeric token in each body line with
its character offset, and assigns the token to the column whose header span centre is nearest, then
asserts that assignment is one to one and in printed order. A value copied from a neighbouring
column therefore fails on geometry, not only on order.

Cells are matched to records through each result's source_locator text, not through its ID, so a
record whose locator names the wrong row or column fails. For each result it checks printed_value,
numeric_value, the row's system (through the result's evaluation) and the uncertainty printed in
the Table 2 time column.

Usage: python3 -I data/omics/perturbpfn-20261115/review/recheck_tables.py <text-layer.txt>
The text layer must be a `pdftotext -layout` run of the PDF whose SHA-256 is
42191efa04b45ca04b2be38b51ea374cd9bf891efe2399d331fec9eaeab200b1.
"""
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

BATCH = Path(__file__).resolve().parent.parent
NUM = re.compile(r"-?\d+\.\d+")

# Row label to the record ID suffix of the system the row's evaluation must name.
SCIPLEX_SYSTEM = {
    "RF X-Learner": "config-rf-x-learner-sciplex",
    "CondOT": "config-condot-sciplex",
    "MLP": "config-mlp-shift-sciplex",
    "GIM": "config-gim-sciplex",
    "Naive": "method-naive-lower-dose",
    "Observational": "method-no-change",
    "PerturbPFN": "config-perturbpfn-step3100",
}
GENERNIB_SYSTEM = {
    "Pearson corr.": "method-pearson-grn",
    "PPCOR": "method-ppcor",
    "GRNBoost2": "method-grnboost2",
    "PORTIA": "method-portia",
    "SCENIC": "method-scenic",
    "PerturbPFN": "config-perturbpfn-step3100-genernib-panels",
}


def header_columns(line: str, names: list[str]) -> list[tuple[str, float]]:
    """Each column name and the centre of where it is printed, in character offsets."""
    out, at = [], 0
    for name in names:
        start = line.index(name, at)
        out.append((name, start + len(name) / 2))
        at = start + len(name)
    assert len(out) == len(names), names
    return out


def assign(line: str, columns: list[tuple[str, float]], expected: list[str], start: int = 0) -> dict[str, str]:
    """Numeric tokens of a body line, each put in the nearest header column by geometry."""
    tokens = [(m.group(0), m.start() + len(m.group(0)) / 2) for m in NUM.finditer(line, start)]
    assert len(tokens) == len(expected), (line, tokens, expected)
    placed = {}
    for (text, centre), want in zip(tokens, expected):
        name = min(columns, key=lambda c: abs(c[1] - centre))[0]
        assert name == want, f"token {text} at {centre} fell in {name}, not {want}: {line}"
        placed[name] = text
    assert list(placed) == expected, (placed, expected)
    return placed


def main(text_path: str) -> None:
    raw = Path(text_path).read_bytes()
    print("text layer sha256", hashlib.sha256(raw).hexdigest())
    lines = unicodedata.normalize("NFC", raw.decode("utf-8")).split("\n")

    records = [json.loads(line) for line in (BATCH / "batch.jsonl").read_text().splitlines()]
    results = {r["id"]: r for r in records if r["kind"] == "result"}
    evals = {r["id"]: r for r in records if r["kind"] == "evaluation"}
    system_of = {}
    for rid, record in results.items():
        ev = evals[next(l["target_id"] for l in record["links"] if l["relation"] == "evaluation")]
        system_of[rid] = next(l["target_id"] for l in ev["links"] if l["relation"] == "system")

    by_locator = {}
    for rid, record in results.items():
        locator = record["attributes"]["source_locator"]
        assert locator not in by_locator, locator
        by_locator[locator] = rid
    unseen = set(results)
    checked = 0

    def take(locator: str, printed: str, numeric: str, system_suffix: str) -> None:
        nonlocal checked
        rid = by_locator.get(locator)
        assert rid, f"no result has locator {locator!r}"
        a = results[rid]["attributes"]
        assert a["printed_value"] == printed, (rid, a["printed_value"], printed)
        assert a["numeric_value"] == numeric, (rid, a["numeric_value"], numeric)
        assert system_of[rid].endswith(system_suffix), (rid, system_of[rid], system_suffix)
        unseen.discard(rid)
        checked += 1

    def body(start: int, label: str) -> str:
        hits = [i for i in range(start, start + 12) if lines[i].strip().startswith(label)]
        assert len(hits) == 1, (label, hits)
        return lines[hits[0]]

    # --- Table 1: three blocks of label and value pairs, three rows -------------------
    t1 = next(i for i, l in enumerate(lines) if l.strip().startswith("Table 1: In-prior latent recovery"))
    blocks = header_columns(lines[t1 + 3], ["Graph", "Target", "Strength / Response"])
    t1_rows = [
        [("Graph", "AUROC ↑"), ("Target", "AUROC ↑"), ("Strength / Response", "|ψ| ratio →1")],
        [("Graph", "AUPRC ↑"), ("Target", "AUPRC ↑"), ("Strength / Response", "∆ cosine ↑")],
        [("Graph", "Proj. F1 ↑"), ("Target", "F1 ↑"), ("Strength / Response", "Obs. NLL ↓")],
    ]
    for offset, row in enumerate(t1_rows):
        line = lines[t1 + 4 + offset]
        at = 0
        for block, label in row:
            start = line.index(label, at)
            at = start + len(label)
            # The label itself must sit under its block header.
            near = min(blocks, key=lambda c: abs(c[1] - (start + len(label) / 2)))[0]
            assert near == block, (label, near, block, line)
            m = NUM.match(line[at:].lstrip())
            assert m, (label, line)
            take(f"Table 1, block '{block}', row \"{label}\"", m.group(0), m.group(0),
                 "config-perturbpfn-step3100")
            at += len(line[at:]) - len(line[at:].lstrip()) + len(m.group(0))
        assert not NUM.search(line[at:]), (line, at)

    # Section 4.1 prose value.
    prose = [i for i, l in enumerate(lines) if "lower F1 of 0.6287" in l]
    assert len(prose) == 1, prose
    assert "straight-through top-k gate used by the" in lines[prose[0] - 1]
    take("Section 4.1 'Results', sentence 'The straight-through top-k gate used by the decoder "
         "obtains a lower F1 of 0.6287'", "0.6287", "0.6287", "config-perturbpfn-step3100")

    # --- Table 2 ----------------------------------------------------------------------
    t2 = next(i for i, l in enumerate(lines) if l.strip().startswith("Table 2: Runtime per protocol"))
    t2_names = ["Model", "Time (s) / protocol", "ŝMD ↑", "ŝr ↑", "ŝW2 ↑", "Avg. ŝ / rank"]
    t2_cols = header_columns(lines[t2 + 4], t2_names)
    score_cols = ["ŝMD ↑", "ŝr ↑", "ŝW2 ↑", "Avg. ŝ / rank"]

    def time_cell(line: str, label: str) -> tuple[str | None, str | None, int]:
        """The printed time and spread of a Table 2 row, and where the time column ends.

        The time and the "/" that stands for no time must both fall in the time column."""
        at = line.index(label) + len(label)
        m = re.match(r"\s+(\d+\.\d+) ± (\d+\.\d+)", line[at:])
        if m:
            centre = at + m.start(1) + len(m.group(1)) / 2
            assert min(t2_cols, key=lambda c: abs(c[1] - centre))[0] == "Time (s) / protocol", line
            return m.group(1), m.group(2), at + m.end()
        slash = re.match(r"(\s+/)(\s|$)", line[at:])
        assert slash, line[at:]
        centre = at + slash.end(1) - 0.5
        assert min(t2_cols, key=lambda c: abs(c[1] - centre))[0] == "Time (s) / protocol", line
        return None, None, at + slash.end(1)

    def scores(line: str, locator_prefix: str, system: str, start: int = 0) -> None:
        placed = assign(line, t2_cols, score_cols, start)
        for name in score_cols[:3]:
            take(f"{locator_prefix}, column '{name}'", placed[name], placed[name], system)
        avg = placed["Avg. ŝ / rank"]
        m = re.search(re.escape(avg) + r" \((#\d)\)", line)
        assert m, line
        take(f"{locator_prefix}, column 'Avg. ŝ / rank', score before the bracket", avg, avg, system)
        take(f"{locator_prefix}, column 'Avg. ŝ / rank', bracketed rank",
             f"({m.group(1)})", m.group(1).lstrip("#"), system)
        # The printed overall score is the equal-weight mean of the three printed columns.
        mean = sum(float(placed[n]) for n in score_cols[:3]) / 3
        assert abs(mean - float(avg)) <= 0.00006, (locator_prefix, mean, avg)

    for label in ["RF X-Learner", "CondOT", "MLP", "GIM", "Naive", "Observational"]:
        line = body(t2 + 5, label)
        system = SCIPLEX_SYSTEM[label]
        value, spread, end = time_cell(line, label)
        locator = f"Table 2, row '{label}', column 'Time (s) / protocol'"
        if value:
            take(locator, value, value, system)
            unc = results[by_locator[locator]]["attributes"]["uncertainty"]
            assert unc["value"] == spread and unc["printed"] == f"± {spread}", (locator, unc, spread)
            assert unc["type"] == "standard_deviation", locator
        else:
            # The row prints "/" for the time, so there must be no runtime result for it.
            assert locator not in by_locator, locator
        scores(line, f"Table 2, row '{label}'", system, end)

    amort = body(t2 + 5, "PerturbPFN (amortized)")
    icl = body(t2 + 5, "PerturbPFN (ICL only)")
    for label, line in (("PerturbPFN (amortized)", amort), ("PerturbPFN (ICL only)", icl)):
        value, spread, end = time_cell(line, label)
        locator = f"Table 2, row '{label}', column 'Time (s) / protocol'"
        take(locator, value, value, "config-perturbpfn-step3100")
        unc = results[by_locator[locator]]["attributes"]["uncertainty"]
        assert unc["value"] == spread and unc["type"] == "standard_deviation", (locator, unc)
        # Neither runtime row prints a score of its own.
        assert not NUM.search(line, end), line
    # The PerturbPFN scores sit on their own line between the two runtime rows.
    between = lines.index(amort) + 1
    assert lines.index(icl) == between + 1, (lines.index(amort), lines.index(icl))
    scores(lines[between], "Table 2, unlabelled score line printed between the rows "
           "'PerturbPFN (amortized)' and 'PerturbPFN (ICL only)'", "config-perturbpfn-step3100")

    # --- Table 3 ----------------------------------------------------------------------
    t3 = next(i for i, l in enumerate(lines) if "Table 3: GeneRNIB 300BCG GRN recovery" in l)
    t3_names = ["Model", "GS-F1", "TFB-F1", "R-Prec.", "R-Recall", "VC"]
    t3_cols = header_columns(lines[t3 + 1], t3_names)
    for label, system in GENERNIB_SYSTEM.items():
        line = body(t3 + 2, label)
        placed = assign(line, t3_cols, t3_names[1:])
        for name in t3_names[1:]:
            take(f"Table 3, row '{label}', column '{name}'", placed[name], placed[name], system)

    assert not unseen, sorted(unseen)
    print(f"re-read {checked} of {len(results)} results by header geometry; none left unchecked")


if __name__ == "__main__":
    main(sys.argv[1])
