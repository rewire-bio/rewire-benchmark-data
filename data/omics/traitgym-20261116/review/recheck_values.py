#!/usr/bin/env python3
"""Independent re-read of every value in batch traitgym-20261116.

Written for the review pass, not reused from extract/. The extractor's
parse_tables.py splits body lines on runs of two or more spaces. This script
instead fixes a character-column band per table column, taken from the start
offset of each column header token in the pinned text layer, and assigns a
numeric token to a column only when the token's own character span starts in
that band. Column assignment is therefore checked directly for every cell,
including the 36 that `batch -- check-values` could only place in a row.

Usage:
  python3 recheck_values.py <paper.txt> <batch.jsonl> [--controls]
"""

from __future__ import annotations

import hashlib
import json
import re
import sys

TEXT_SHA256 = "23ae4d67751f1092e5cc2da66b52091fa9bbc3ec59310f06bc65be28f93c5097"

NUM = re.compile(r"-?\d+\.\d+|-?\d+")


def tokens(line: str) -> list[tuple[int, int, str]]:
    return [(m.start(), m.end(), m.group()) for m in re.finditer(r"\S+", line)]


def find_line(lines: list[str], needle: str, start: int = 0) -> int:
    for i in range(start, len(lines)):
        if needle in lines[i]:
            return i
    raise AssertionError(f"line not found: {needle!r}")


def numeric_cells(line: str) -> list[tuple[int, str]]:
    """Numeric tokens of a body line with their start offsets."""
    out = []
    for s, _e, t in tokens(line):
        if NUM.fullmatch(t):
            out.append((s, t))
    return out


def assign(cells: list[tuple[int, str]], bands: list[tuple[int, str]], tol: int = 2) -> dict[str, str]:
    """Map numeric tokens to column names by start offset. Exact, no nearest-match.

    Numeric tokens left of the first column band belong to the row label
    ("Balding Type 4", "Evo2 40B") and are ignored. Anything from the value zone
    onwards must start inside exactly one band, so a value sitting in a
    neighbouring column is an error rather than a nearest-match.
    """
    zone = bands[0][0] - 6
    out: dict[str, str] = {}
    for start, tok in cells:
        if start < zone:
            continue
        hit = [name for base, name in bands if abs(start - base) <= tol]
        assert len(hit) == 1, f"token {tok!r} at col {start} matched columns {hit} (bands {bands})"
        assert hit[0] not in out, f"two values for column {hit[0]}: {out.get(hit[0])} and {tok}"
        out[hit[0]] = tok
    return out


def band_from_header(line: str, headers: list[str]) -> list[tuple[int, str]]:
    """Column start offsets taken from the first token of each header label."""
    toks = tokens(line)
    bands = []
    for h in headers:
        first = h.split()[0]
        match = [s for s, _e, t in toks if t == first]
        assert len(match) == 1, f"header {h!r} first token {first!r} found {len(match)} times"
        bands.append((match[0], h))
    return bands


# --------------------------------------------------------------------------
# table readers. each returns {(row-key tuple): {column: printed value}}
# --------------------------------------------------------------------------

def read_s8(lines: list[str]) -> dict:
    h = find_line(lines, "Table S8: AUPRC for different gLM zero-shot scores")
    colline = find_line(lines, "abs(LLR)", h)
    bands = band_from_header(lines[colline], ["LLR", "abs(LLR)", "L2 dist.", "Cosine dist.", "Inner prod."])
    assert [b[0] for b in bands] == [59, 71, 88, 102, 122], bands
    models = ["GPN-MSA", "GPN-Promoter", "NT", "HyenaDNA", "Caduceus", "SpeciesLM",
              "AIDO.DNA", "Evo2 1B", "Evo2 7B", "Evo2 40B"]
    out: dict = {}
    dataset = None
    i = find_line(lines, "Dataset", colline)
    while True:
        i += 1
        line = lines[i]
        if not line.strip():
            if out and len(out) == 20:
                break
            continue
        toks = tokens(line)
        if toks and toks[0][0] == 8:  # dataset label column
            label = " ".join(t for _s, _e, t in toks if _s < 30)
            assert label in ("Mendelian traits", "Complex traits"), label
            dataset = label
        # model label begins at column 35
        mod = " ".join(t for s, _e, t in toks if 34 <= s < 55)
        assert mod in models, f"unexpected model label {mod!r} on line {i}"
        cells = assign(numeric_cells(line), bands)
        assert len(cells) == 5, (dataset, mod, cells)
        out[(dataset, mod)] = cells
        if len(out) == 20:
            break
    assert sorted({d for d, _m in out}) == ["Complex traits", "Mendelian traits"]
    for d in ("Mendelian traits", "Complex traits"):
        assert [m for dd, m in out if dd == d] == models, d
    return out


def read_s11(lines: list[str]) -> dict:
    h = find_line(lines, "Table S11: AUPRC for selected traits")
    colline = find_line(lines, "Ensemble", h)
    bands = band_from_header(lines[colline], ["Borzoi", "GPN-MSA", "CADD", "Ensemble"])
    assert [b[0] for b in bands] == [79, 92, 111, 124], bands
    out: dict = {}
    dataset = None
    i = colline
    blanks = 0
    while blanks < 3:
        i += 1
        line = lines[i]
        if not line.strip():
            blanks += 1
            continue
        blanks = 0
        label = " ".join(t for s, _e, t in tokens(line) if s < 70)
        if label in ("Mendelian traits", "Complex traits"):
            dataset = label
            continue
        cells = assign(numeric_cells(line), bands)
        assert len(cells) == 4, (dataset, label, cells)
        assert dataset is not None
        out[(dataset, label)] = cells
    return out


def read_t4(lines: list[str]) -> dict:
    h = find_line(lines, "Table 4: Top CADD features in different categories")
    colline = find_line(lines, "Description", h)
    bands = band_from_header(lines[colline], ["AUPRC"])
    assert bands == [(85, "AUPRC")], bands
    out: dict = {}
    dataset = None
    i = colline
    seen_blank = 0
    while seen_blank < 2:
        i += 1
        line = lines[i]
        if not line.strip():
            seen_blank += 1
            continue
        seen_blank = 0
        toks = tokens(line)
        ds = " ".join(t for s, _e, t in toks if s < 32)
        if ds:
            assert ds in ("Mendelian traits", "Complex traits"), ds
            dataset = ds
        category = " ".join(t for s, _e, t in toks if 32 <= s < 57)
        feature = " ".join(t for s, _e, t in toks if 57 <= s < 84)
        cells = assign(numeric_cells(line), bands)
        assert len(cells) == 1, (dataset, feature, cells)
        out[(dataset, category, feature)] = cells
    return out


def read_t5(lines: list[str]) -> dict:
    h = find_line(lines, "Table 5: Top three tissue/cell types for different traits")
    colline = find_line(lines, "Tissue/cell", h)
    bands = band_from_header(lines[colline], ["AUPRC"])
    assert bands == [(113, "AUPRC")], bands
    out: dict = {}
    dataset = None
    trait = None
    i = colline
    seen_blank = 0
    while seen_blank < 2:
        i += 1
        line = lines[i]
        if not line.strip():
            seen_blank += 1
            continue
        seen_blank = 0
        toks = tokens(line)
        left = " ".join(t for s, _e, t in toks if s < 70)
        tissue = " ".join(t for s, _e, t in toks if 70 <= s < 110)
        if left in ("Mendelian traits", "Complex traits"):
            assert not tissue
            dataset = left
            continue
        if left:
            trait = left
        cells = assign(numeric_cells(line), bands)
        assert len(cells) == 1, (dataset, trait, tissue, cells)
        assert tissue, (dataset, trait, line)
        out[(dataset, trait, tissue)] = cells
    return out


def read_s4(lines: list[str]) -> dict:
    h = find_line(lines, "Table S4: Global AUPRC of matched features")
    colline = find_line(lines, "Dataset", h)
    bands = band_from_header(lines[colline], ["AUPRC"])
    assert bands == [(94, "AUPRC")], bands
    # the AUPRC column is right-shifted from its header on the body lines
    bands = [(98, "AUPRC")]
    out: dict = {}
    i = colline
    seen_blank = 0
    while seen_blank < 2:
        i += 1
        line = lines[i]
        if not line.strip():
            seen_blank += 1
            continue
        seen_blank = 0
        toks = tokens(line)
        dataset = " ".join(t for s, _e, t in toks if s < 65)
        feature = " ".join(t for s, _e, t in toks if 65 <= s < 95)
        assert dataset in ("Mendelian traits", "Complex traits"), dataset
        cells = assign(numeric_cells(line), bands)
        assert len(cells) == 1, (dataset, feature, cells)
        out[(dataset, feature)] = cells
    return out


# --------------------------------------------------------------------------
# locator parsing and comparison
# --------------------------------------------------------------------------

LOC_S11 = re.compile(r'^Table S11, row "(?P<row>.+)", column "(?P<col>.+)" \(page 28\)$')
LOC_T5 = re.compile(r'^Table 5, trait "(?P<trait>.+)", row "(?P<row>.+)", column "AUPRC" \(page 13\)$')
LOC_T4 = re.compile(r'^Table 4, row "(?P<row>.+)", column "AUPRC" \(page 12\)$')
LOC_S4 = re.compile(r'^Table S4, (?P<dataset>Mendelian|Complex) traits row "(?P<row>.+)", column "AUPRC" \(page 22\)$')


def lookup(loc: str, tables: dict) -> tuple[str, str]:
    """Return (printed value found in the source, how the cell was located)."""
    m = LOC_S11.match(loc)
    if m:
        row, col = m.group("row"), m.group("col")
        hits = [(d, cells) for (d, r), cells in tables["s11"].items() if r == row]
        assert len(hits) == 1, f"row {row!r} matched {len(hits)} S11 rows"
        d, cells = hits[0]
        return cells[col], f"S11 {d} / {row} / column band of {col}"
    m = LOC_T5.match(loc)
    if m:
        trait, tissue = m.group("trait"), m.group("row")
        hits = [(d, cells) for (d, t, ti), cells in tables["t5"].items() if t == trait and ti == tissue]
        assert len(hits) == 1, f"{trait}/{tissue} matched {len(hits)} T5 rows"
        d, cells = hits[0]
        return cells["AUPRC"], f"T5 {d} / {trait} / {tissue} / AUPRC band"
    m = LOC_T4.match(loc)
    if m:
        feat = m.group("row")
        hits = [(d, c, cells) for (d, c, f), cells in tables["t4"].items() if f == feat]
        assert len(hits) == 1, f"feature {feat!r} matched {len(hits)} T4 rows"
        d, c, cells = hits[0]
        return cells["AUPRC"], f"T4 {d} / {c} / {feat} / AUPRC band"
    m = LOC_S4.match(loc)
    if m:
        ds, feat = m.group("dataset") + " traits", m.group("row")
        cells = tables["s4"][(ds, feat)]
        return cells["AUPRC"], f"S4 {ds} / {feat} / AUPRC band"
    raise AssertionError(f"unparsed locator: {loc}")


def main() -> int:
    text_path, batch_path = sys.argv[1], sys.argv[2]
    controls = "--controls" in sys.argv

    raw = open(text_path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    assert got == TEXT_SHA256, f"text layer hash {got} != pinned {TEXT_SHA256}"
    lines = raw.decode("utf-8").split("\n")

    tables = {
        "s8": read_s8(lines),
        "s11": read_s11(lines),
        "t4": read_t4(lines),
        "t5": read_t5(lines),
        "s4": read_s4(lines),
    }
    counts = {k: sum(len(v) for v in t.values()) for k, t in tables.items()}
    print("cells parsed:", counts, "total", sum(counts.values()))
    assert counts == {"s8": 100, "s11": 104, "t4": 6, "t5": 18, "s4": 4}, counts

    with open("/dev/stdout", "w") as _:
        pass

    results = [json.loads(l) for l in open(batch_path) if '"kind":"result"' in l or '"kind": "result"' in l]
    results = [r for r in results if r["kind"] == "result"]
    assert len(results) == 132, len(results)

    rows = []
    bad = 0
    for r in sorted(results, key=lambda r: r["id"]):
        a = r["attributes"]
        loc = a["source_locator"]
        found, how = lookup(loc, tables)
        ok_printed = found == a["printed_value"]
        ok_numeric = float(found) == float(a["numeric_value"])
        status = "ok" if (ok_printed and ok_numeric) else "MISMATCH"
        if status != "ok":
            bad += 1
        rows.append((r["id"], status, a["printed_value"], a["numeric_value"], found, how, loc))

    with open("review/recheck-values.tsv", "w") as f:
        f.write("id\tstatus\tstored_printed\tstored_numeric\tsource_cell\tcolumn_assignment\tlocator\n")
        for row in rows:
            f.write("\t".join(row) + "\n")
    print(f"results checked: {len(rows)}, mismatches: {bad}")

    # every parsed cell of the four extracted tables must be claimed by exactly one result
    claimed = {}
    for r in results:
        loc = r["attributes"]["source_locator"]
        claimed[loc] = claimed.get(loc, 0) + 1
    assert all(v == 1 for v in claimed.values()), [k for k, v in claimed.items() if v != 1]
    assert len(claimed) == 132, len(claimed)
    print("locators distinct:", len(claimed))

    # S8 reading written before the extractor's file was opened
    mine = {}
    with open("review/s8-reviewer-reading.tsv") as f:
        hdr = f.readline().rstrip("\n").split("\t")[2:]
        for line in f:
            p = line.rstrip("\n").split("\t")
            mine[(p[0], p[1])] = dict(zip(hdr, p[2:]))
    diff = [(k, c, mine[k][c], tables["s8"][k][c])
            for k in mine for c in hdr if mine[k][c] != tables["s8"][k][c]]
    print(f"S8 hand reading vs column-band parse: {len(mine)*5} cells, {len(diff)} differences", diff or "")
    assert not diff

    if controls:
        print("\n-- negative controls --")
        # control 1: swap two values within one S11 row
        t = {k: dict(v) for k, v in tables["s11"].items()}
        key = ("Mendelian traits", "Hyperferritinemia")
        t[key]["Borzoi"], t[key]["GPN-MSA"] = t[key]["GPN-MSA"], t[key]["Borzoi"]
        tb = dict(tables, s11=t)
        caught = 0
        for r in results:
            a = r["attributes"]
            try:
                found, _ = lookup(a["source_locator"], tb)
            except AssertionError:
                caught += 1
                continue
            if found != a["printed_value"]:
                caught += 1
        print(f"control 1 (two values swapped in one S11 row): {caught} results rejected (expect 2)")
        assert caught == 2, caught

        # control 2: shift one row's values one column left in the parsed text
        shifted = lines[:]
        i = find_line(shifted, 'Hemoglobin A1c')
        j = find_line(shifted, 'Hemoglobin A1c', i + 1)
        while "0.475" not in shifted[j]:
            j = find_line(shifted, 'Hemoglobin A1c', j + 1)
        before = shifted[j]
        # move every numeric token 13 characters left: into the neighbouring band
        head = before[:79]
        nums = [t for _s, t in numeric_cells(before)]
        shifted[j] = head + "".join(n.ljust(13) for n in nums)[:-13] + " " * 13
        try:
            read_s11(shifted)
            raise SystemExit("control 2 FAILED: column-shifted row parsed without error")
        except AssertionError as exc:
            print(f"control 2 (one S11 row's values shifted one column left): rejected at parse: {exc}")

        # control 3: a value moved into a neighbouring column band but still in the row
        t = {k: dict(v) for k, v in tables["s11"].items()}
        key = ("Complex traits", "Adult height")
        t[key]["CADD"] = t[key]["GPN-MSA"]
        tb = dict(tables, s11=t)
        caught = sum(1 for r in results
                     if lookup(r["attributes"]["source_locator"], tb)[0] != r["attributes"]["printed_value"])
        print(f"control 3 (GPN-MSA value copied into the CADD column): {caught} results rejected (expect 1)")
        assert caught == 1, caught

    print("\nOK" if bad == 0 else "\nMISMATCHES FOUND")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
