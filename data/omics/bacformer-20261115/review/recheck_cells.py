"""Independent re-read of every stored cell of the Bacformer batch, from PDF word geometry.

Written for the review pass. It does not use extract/parse_tables.py, extract/check_tables.py,
extract/tables.json or the pdftotext -layout text layer that those scripts read. Instead it reads
the word bounding boxes that pdftotext -bbox-layout emits for the pinned v3 PDF, groups words into
printed lines by their y coordinate, takes each table's column boundaries from the x extent of its
own printed header words, and assigns every numeric token to a column by where that token sits on
the page. A value printed under one header can therefore never be read as a value of another.

Usage:
  pdftotext -bbox-layout <v3.pdf> bbox.xml
  python3 -I recheck_cells.py bbox.xml <batch.jsonl>

Exit status is 0 only when every stored cell matches the cell its locator names, and every cell the
tables print is accounted for.
"""

import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/1999/xhtml}"

# The six benchmark tables, as printed: the caption that names each one, the row labels in the
# printed order, and the column headers in the printed left-to-right order. Row labels and header
# names are transcribed from the rendered pages by hand for this pass, not taken from the batch.
TABLES = {
    "S1": {
        "caption": "Table S1.",
        "rows": ["Mistral-DNA", "Evo", "Evo-2", "DNABERT-2", "Nucleotide Transformer", "ProkBERT",
                 "ProtBERT", "ESM-2", "ESM-C", "gLM2", "Bacformer", "Bacformer Large"],
        "columns": ["AUROC", "AUPRC"],
        "headers": ["AUROC", "AUPRC"],
    },
    "S12": {
        "caption": "Table S12.",
        "rows": ["gLM2", "ProtBERT", "ESM-2", "ESM-C", "Bacformer", "Bacformer Large"],
        "columns": ["ARI", "NMI", "ASW"],
        "headers": ["ARI", "NMI", "ASW"],
    },
    "S13": {
        "caption": "Table S13.",
        "rows": ["Mistral-DNA", "DNABERT-2", "Nucleotide Transformer", "ProkBERT", "Evo", "Evo-2",
                 "ESM-2", "ESM-C", "ProtBERT", "gLM2", "Bacformer", "Bacformer Large"],
        "columns": ["Zero-shot AUROC", "Zero-shot AUPRC", "Finetuned AUROC", "Finetuned AUPRC"],
        "headers": ["AUROC", "AUPRC", "AUROC", "AUPRC"],
        "groups": [("Zero-shot", [0, 1]), ("Finetuned", [2, 3])],
    },
    "S14": {
        "caption": "Table S14.",
        "rows": ["Mistral-DNA", "Evo", "Evo-2", "DNABERT-2", "Nucleotide Transformer", "ProkBERT",
                 "ProtBERT", "ESM-2", "ESM-C", "gLM2", "Bacformer", "Bacformer Large"],
        "columns": ["AUROC", "AUPRC"],
        "headers": ["AUROC", "AUPRC"],
    },
    "S16": {
        "caption": "Table S16.",
        "rows": ["Mistral-DNA", "DNABERT-2", "Nucleotide Transformer", "ProkBERT", "Evo", "Evo-2",
                 "ESM-2", "ESM-C", "ProtBERT", "gLM2", "Bacformer", "Bacformer Large"],
        "columns": ["AUROC", "AUPRC"],
        "headers": ["AUROC", "AUPRC"],
    },
    "S18": {
        "caption": "Table S18.",
        "rows": ["Mistral-DNA", "DNABERT-2", "Nucleotide Transformer", "ProkBERT", "Evo", "Evo-2",
                 "ESM-2", "ESM-C", "ProtBERT", "gLM2", "Bacformer", "Bacformer Large"],
        # "R2" prints as an R with a superscript 2, which the PDF carries as two words, so the
        # header word to match is "R".
        "columns": ["Binary AUROC", "Binary AUPRC", "Regression R2", "Regression Pearson"],
        "headers": ["AUROC", "AUPRC", "R", "Pearson"],
        "groups": [("Binary", [0, 1]), ("Regression", [2, 3])],
    },
}

NUMBER = re.compile(r"^\d+(?:\.\d+)?$")


def is_value(text):
    return bool(NUMBER.match(text)) or text in ("±", "+-", "±±")


def pages(path):
    """Words of every page, as (text, x_centre, y_centre, x_min, x_max)."""
    root = ET.parse(path).getroot()
    out = []
    for page in root.iter(f"{NS}page"):
        words = []
        for w in page.iter(f"{NS}word"):
            text = unicodedata.normalize("NFKC", (w.text or "")).strip()
            if not text:
                continue
            x0, x1 = float(w.get("xMin")), float(w.get("xMax"))
            y0, y1 = float(w.get("yMin")), float(w.get("yMax"))
            words.append((text, (x0 + x1) / 2, (y0 + y1) / 2, x0, x1))
        out.append(words)
    return out


def lines_of(words, tol=3.0):
    """Group words into printed lines by y centre, each line sorted left to right."""
    grouped = []
    for w in sorted(words, key=lambda w: (w[2], w[1])):
        if grouped and abs(w[2] - grouped[-1][0][2]) <= tol:
            grouped[-1].append(w)
        else:
            grouped.append([w])
    return [sorted(g, key=lambda w: w[1]) for g in grouped]


def find_table(all_pages, spec):
    """Locate one table: the page holding its caption, its header line and its body lines.

    The caption is found by its printed label. The header line is the nearest line above the
    caption that carries the table's printed metric header words in the printed order, and the
    body is everything between that header line and the caption.
    """
    want = spec["caption"].split()
    for page_number, words in enumerate(all_pages, start=1):
        lines = lines_of(words)
        cap_at = next((i for i, line in enumerate(lines)
                       if [w[0] for w in line][:2] == want), None)
        if cap_at is None:
            continue
        for i in range(cap_at - 1, -1, -1):
            hits = [w for w in lines[i] if w[0] in spec["headers"]]
            if [h[0] for h in hits] == spec["headers"]:
                return page_number, lines[i + 1:cap_at], hits, lines[i - 1] if i else []
        raise SystemExit(f"{' '.join(want)}: caption found on page {page_number} but no line above "
                         f"it carries the headers {spec['headers']}")
    raise SystemExit(f"{' '.join(want)}: caption not found in the PDF")


def column_bounds(header_words):
    """Midpoints between consecutive header word centres, as column boundaries."""
    centres = [w[1] for w in header_words]
    edges = [(centres[i] + centres[i + 1]) / 2 for i in range(len(centres) - 1)]
    return centres, edges


def column_of(x, centres, edges):
    for i, e in enumerate(edges):
        if x < e:
            return i
    return len(centres) - 1


def read_table(all_pages, name, spec):
    """Return {(row_label, column_name): printed cell text} read from word geometry."""
    page_number, body, header_words, above = find_table(all_pages, spec)
    centres, edges = column_bounds(header_words)

    # Where a table prints a group header over pairs of metric columns, check geometrically that
    # each group sits over the columns this script names after it, and over no other column.
    for group, idxs in spec.get("groups", []):
        hit = next((w for w in above if w[0] == group), None)
        if hit is None:
            raise SystemExit(f"{name}: no group header {group!r} on the line above the metrics")
        own = [column_of(c, centres, edges) for c in (min(centres[i] for i in idxs),
                                                      max(centres[i] for i in idxs))]
        if column_of(hit[1], centres, edges) not in idxs or own != [min(idxs), max(idxs)]:
            raise SystemExit(f"{name}: group header {group!r} at x={hit[1]:.1f} does not sit over "
                             f"columns {idxs}")

    cells = {}
    seen_rows = []
    plus_minus = {}
    for line in body:
        # A value token is a bare number or the plus-minus sign; everything else is part of the
        # row label. Row labels such as Evo-2 and ESM-2 carry digits but are never bare numbers.
        label = " ".join(w[0] for w in line if not is_value(w[0])).strip()
        numbers = [w for w in line if NUMBER.match(w[0])]
        signs = [w for w in line if w[0] == "±"]
        if label and not numbers:
            raise SystemExit(f"{name}: line {label!r} carries no value")
        if not label:
            # The plus-minus glyphs of a row sit on their own baseline, just below the row's
            # numbers, so they belong to the row last read. Record which column each one falls
            # in, so every cell can be checked to print its own sign.
            if not signs:
                continue
            if not seen_rows:
                raise SystemExit(f"{name}: plus-minus signs before the first row")
            for w in signs:
                plus_minus.setdefault(len(seen_rows) - 1, []).append(
                    column_of(w[1], centres, edges))
            continue
        if label not in spec["rows"]:
            raise SystemExit(f"{name}: unexpected row label {label!r}")
        buckets = {}
        for w in numbers:
            buckets.setdefault(column_of(w[1], centres, edges), []).append(w)
        if sorted(buckets) != list(range(len(spec["columns"]))):
            raise SystemExit(f"{name}: row {label!r} fills columns {sorted(buckets)}, not every "
                             f"column of {spec['columns']}")
        for idx, ws in buckets.items():
            ws = sorted(ws, key=lambda w: w[1])
            if len(ws) != 2:
                raise SystemExit(f"{name}: row {label!r} column {spec['columns'][idx]} holds "
                                 f"{[w[0] for w in ws]}, expected a mean and a spread")
            cells[(label, spec["columns"][idx])] = f"{ws[0][0]} ± {ws[1][0]}"
        for w in signs:
            plus_minus.setdefault(len(seen_rows), []).append(column_of(w[1], centres, edges))
        seen_rows.append(label)

    if seen_rows != spec["rows"]:
        raise SystemExit(f"{name}: row order read as {seen_rows}, printed order is {spec['rows']}")
    for i, label in enumerate(seen_rows):
        got = sorted(plus_minus.get(i, []))
        if got != list(range(len(spec["columns"]))):
            raise SystemExit(f"{name}: row {label!r} prints plus-minus signs in columns {got}, "
                             f"not one per column")
    expected = {(r, c) for r in spec["rows"] for c in spec["columns"]}
    if set(cells) != expected:
        raise SystemExit(f"{name}: cells read {sorted(set(cells) ^ expected)} do not match the grid")
    print(f"{name}: page {page_number}, {len(spec['rows'])} rows x {len(spec['columns'])} columns, "
          f"{len(cells)} cells read from word positions")
    return cells


def canon(s):
    """Compare printed strings up to the characters a PDF word split cannot preserve."""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("±", "+-").replace("−", "-")
    return re.sub(r"\s+", "", s)


LOCATOR = re.compile(r"^Table (S\d+), row '(.+)', column '(.+)'$")


def main(argv):
    bbox, batch = argv[0], argv[1]
    all_pages = pages(bbox)
    printed = {name: read_table(all_pages, name, spec) for name, spec in TABLES.items()}
    total = sum(len(v) for v in printed.values())

    records = [json.loads(l) for l in open(batch) if l.strip()]
    results = [r for r in records if r.get("kind") == "result"]
    problems = []
    claimed = set()
    for r in sorted(results, key=lambda r: r["id"]):
        a = r["attributes"]
        m = LOCATOR.match(a["source_locator"])
        if not m:
            problems.append(f"{r['id']}: locator not parsed: {a['source_locator']!r}")
            continue
        table, row, col = m.group(1), m.group(2), m.group(3)
        if table not in printed:
            problems.append(f"{r['id']}: unknown table {table}")
            continue
        key = (row, col)
        if key not in printed[table]:
            problems.append(f"{r['id']}: {table} prints no cell for row {row!r} column {col!r}")
            continue
        if (table,) + key in claimed:
            problems.append(f"{r['id']}: a second result claims {table} {key}")
        claimed.add((table,) + key)
        cell = printed[table][key]
        if canon(cell) != canon(a["printed_value"]):
            problems.append(f"{r['id']}: printed_value {a['printed_value']!r} but the cell under "
                            f"{table} row {row!r} column {col!r} prints {cell!r}")
            continue
        parts = re.split(r"\s*(?:±|\+-)\s*", canon(cell))
        mean = parts[0]
        sd = parts[1] if len(parts) > 1 else None
        if a.get("numeric_value") is not None and a["numeric_value"].lstrip("0") != mean.lstrip("0"):
            problems.append(f"{r['id']}: numeric_value {a['numeric_value']!r} is not the printed "
                            f"mean {mean!r}")
        unc = a.get("uncertainty") or {}
        if sd is not None:
            if unc.get("value") is None:
                problems.append(f"{r['id']}: the cell prints a spread {sd!r} but uncertainty.value "
                                "is absent")
            elif unc["value"].lstrip("0") != sd.lstrip("0"):
                problems.append(f"{r['id']}: uncertainty.value {unc.get('value')!r} is not the "
                                f"printed spread {sd!r}")
            if unc.get("printed") is not None and canon(unc["printed"]) != canon(cell):
                problems.append(f"{r['id']}: uncertainty.printed {unc['printed']!r} is not the cell "
                                f"{cell!r}")
        if unc.get("source_column") is not None and unc["source_column"] != col:
            problems.append(f"{r['id']}: uncertainty.source_column {unc['source_column']!r} is not "
                            f"the locator column {col!r}")

    counted = sum(1 for t in printed for k in printed[t]
                  if any(LOCATOR.match(r["attributes"]["source_locator"]) and
                         LOCATOR.match(r["attributes"]["source_locator"]).groups() == (t, k[0], k[1])
                         for r in results))
    print(f"cells printed by the six tables: {total}")
    print(f"results in the batch: {len(results)}")
    print(f"printed cells a result claims: {counted}")
    if counted != total:
        problems.append(f"{total - counted} printed cells are not recorded by any result")
    for p in problems:
        print("MISMATCH " + p)
    print(f"mismatches: {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
