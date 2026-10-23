"""Mechanical steps of a batch review, so agents do not hand-write them.

  python3 scripts/omics/batch.py check-values <batch> <source-id>=<artifact> ...
      For every result, find the row named in its source_locator in the pinned artifact and
      check that printed_value appears in that row. Writes <batch>/value-check.tsv.
  python3 scripts/omics/batch.py table <artifact> "<Table 3>"
      Print one table of an artifact as TSV, with the column each cell was placed in.
  python3 scripts/omics/batch.py hash <batch> [<source-id>=<artifact> ...]
      Check each artifact against its source record's artifact_sha256, then write the
      `files` and `source_artifacts` hashes into <batch>/review.json, keeping its other fields.

Artifacts are PMC/JATS XML (tables read from <tr> rows) or text (a PDF text layer from
pdftotext -layout, rows read as lines). The value check confirms the printed string is in the
named row. For XML it also checks the named column (`in_cell`). For text it parses the table:
columns are the character positions the value cells of every body line share, and a column is
named only when its header lines up with it without guessing. Where the locator's column (and
sub-column) matches one named column, the value must be in that cell (`in_cell`, else
`wrong_column`); otherwise the check falls back to the row (`in_row`). Because every cell is
extracted it also flags a value claimed by more results in a row than the row prints
(`overclaimed_in_row`). Values left at `in_row` still need the reviewer's sampled check.
"""
import hashlib
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

LOCATOR = re.compile(r'^(?P<prefix>Appendix |Supplementary |Extended Data )?(?P<table>Table [A-Z]?\d+[a-z]?)\b.*?row ["\'](?P<row>[^"\']+)["\']'
                     r'(?:.*?col(?:umn)? ["\'](?P<col>[^"\']+)["\'])?(?:.*?sub-col(?:umn)? ["\'](?P<sub>[^"\']+)["\'])?')
WINDOW = 150  # text lines searched on each side of a table caption, which may sit above or below the rows
SLACK = 4  # characters a header may sit off its column in a text layer
# A cell that reads as a value: a number (signed, bracketed, with units after it), a dash or N/A.
NUMERIC = re.compile(r"[-+±<>~≈]?\s?\(?[-+±]?\d|[-—]+$|n/?a$")


def norm(text):
    text = unicodedata.normalize("NFKC", text).replace("−", "-").replace("–", "-")
    return re.sub(r"\s+", " ", text).strip().lower()


def squash(text):
    """Comparison key that ignores spacing, which XML markup (superscripts, line breaks) adds."""
    return re.sub(r"\s+", "", norm(text))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_batch(folder):
    return [json.loads(line) for line in (Path(folder) / "batch.jsonl").read_text().splitlines() if line.strip()]


def parse_pairs(pairs):
    out = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"expected <source-id>=<artifact>, got {pair!r}")
        key, path = pair.split("=", 1)
        out[key] = Path(path)
    return out


def xml_tables(path):
    """{normalised table label: [row cells, ...]} from a JATS article."""
    tables = {}
    for wrap in ET.parse(path).iter():
        if not str(wrap.tag).endswith("table-wrap"):
            continue
        label = next((" ".join(e.itertext()) for e in wrap.iter() if str(e.tag).endswith("label")), "")
        rows = [[norm(" ".join(c.itertext())) for c in tr if str(c.tag).endswith(("td", "th"))]
                for tr in wrap.iter() if str(tr.tag).endswith("tr")]
        tables[norm(label).rstrip(".")] = rows
    return tables


def after_label(line, row):
    """The tokens after `row` where it occurs as whole tokens in `line`, or None.

    Two-column layouts put a table row after unrelated text on the same line, so the
    label can sit anywhere; only what follows it is the row's cells."""
    have, want = tokens(line), tokens(row)
    for i in range(len(have) - len(want) + 1):
        if have[i:i + len(want)] == want:
            return " ".join(have[i + len(want):])
    return None


def text_rows(lines, table, row):
    """Cells after `row` on lines within WINDOW of a caption for `table`, above or below it."""
    caption = re.compile(r"(^|\s)" + re.escape(norm(table)) + r"\b[:.]")
    hits = []
    for i, line in enumerate(lines):
        if caption.search(line):
            for l in lines[max(0, i - WINDOW):i + 1 + WINDOW]:
                cells = after_label(l, row)
                if cells is not None and cells not in hits:
                    hits.append(cells)
    return hits


def tokens(row_text):
    return row_text.split(" ")


# Text-layer tables. pdftotext -layout places each cell at its printed horizontal position and
# separates cells by two or more spaces, so a column is a run of character positions that the
# value cells of every body line share. The parser only names a column when the header text
# lines up with it without guessing; anything less leaves the column unnamed, and the value
# check falls back to the row.

def fold(text):
    """norm() without collapsing spaces, so character positions survive."""
    return unicodedata.normalize("NFKC", text).replace("−", "-").replace("–", "-").lower()


def chunks(line):
    """[(start, end, text)] of the runs of a line separated by two or more spaces."""
    return [(m.start(), m.end(), m.group()) for m in re.finditer(r"\S+(?: \S+)*", line)]


def is_prose(text):
    return sum(bool(re.fullmatch(r"[a-z]{3,}", w.strip(".,;:()[]\"'“”"))) for w in text.split()) >= 4


def body_row(line):
    """(label chunks, value chunks) of a table body line, or None if it is not one.

    Values are the chunks after the last one that does not read as a value; prose beside the
    table on a two-column page is dropped first."""
    parts = [c for c in chunks(line) if not is_prose(c[2])]
    last = max((i for i, c in enumerate(parts) if not NUMERIC.match(fold(c[2]))), default=-1)
    if len(parts) - last - 1 < 2:
        return None
    return parts[:last + 1], parts[last + 1:]


def caption_lines(lines, table, prefix=""):
    """Indices of lines that start a caption for `table` (not a prose mention of it)."""
    want = (prefix or "").strip().lower()
    want = "" if want == "appendix" else want
    pattern = re.compile(r"(?:^\s*|\s{2})(supplementary |extended data |appendix )?"
                         + re.escape(fold(table)) + r"[:.]\s*\S")
    out = []
    for i, line in enumerate(lines):
        m = pattern.search(fold(line))
        if m and ((m.group(1) or "").strip().replace("appendix", "") == want):
            out.append(i)
    return out


def overlap(a, b):
    return min(a[1], b[1]) - max(a[0], b[0])


def gap(a, b):
    return max(a[0] - b[1], b[0] - a[1], 0)


def parse_text_table(lines, table, prefix=""):
    """The table captioned `table` in a text layer, or (None, reason).

    Returns ({"columns": [(start, end)], "names": [[header parts, top first] or None],
    "rows": [(line index, label chunks, {column: cell text})]}, None)."""
    found = []
    for c in caption_lines(lines, table, prefix):
        found += [s for s in (rows_below(lines, c), rows_above(lines, c)) if s is not None]
    if not found:
        return None, "no table body found next to the caption"
    if len(set(found)) > 1:
        return None, "more than one table body next to captions for this label"
    start = found[0]
    top, bottom = start, start
    while top - 1 >= 0 and block_line(lines, top - 1, -1):
        top -= 1
    while bottom + 1 < len(lines) and block_line(lines, bottom + 1, 1):
        bottom += 1
    body = [(i, body_row(lines[i])) for i in range(top, bottom + 1)]
    data = [(i, r) for i, r in body if r is not None]
    if len(data) < 2:
        return None, "fewer than two body rows"
    columns = []
    for s, e, _ in sorted(c for _, (_, values) in data for c in values):
        if columns and s < columns[-1][1]:
            columns[-1] = (columns[-1][0], max(columns[-1][1], e))
        else:
            columns.append((s, e))
    rows = []
    for i, r in body:
        label, values = r if r is not None else ([c for c in chunks(lines[i])], [])
        cells = {}
        for c in values:
            col = next(k for k, span in enumerate(columns) if overlap(span, c) > 0)
            if col in cells:
                return None, f"two cells of line {i + 1} fall in one column"
            cells[col] = norm(c[2])
        # A row labelled by a number ("Ensemble Size 1") has no text label; its first cell is the label.
        rows.append((i, label or values[:1], cells))
    names = header_names(lines, top, columns, [(i, r) for i, r in data])
    return {"columns": columns, "names": names, "rows": rows}, None


def rows_below(lines, c):
    """First body line after a caption, if only caption text and blank lines come between."""
    for i in range(c + 1, min(len(lines), c + 25)):
        if body_row(lines[i]) is not None:
            return i
    return None


def rows_above(lines, c):
    """Last body line just above a caption (at most one blank line between)."""
    for i in (c - 1, c - 2):
        if i >= 0 and body_row(lines[i]) is not None:
            return i
        if i >= 0 and lines[i].strip():
            return None
    return None


def caption_like(line):
    return re.match(r"\s*(supplementary |extended data |appendix )?(table|figure|fig\.) [a-z]?\d+[a-z]?[:.]", fold(line))


def block_line(lines, i, step):
    """Whether line i continues a table body: a body line, a one-chunk row label or a single blank line."""
    line = lines[i]
    if caption_like(line):
        return False
    if not line.strip():
        nxt = i + step
        return 0 <= nxt < len(lines) and bool(lines[nxt].strip())
    if body_row(line) is not None:
        return True
    parts = chunks(line)
    return len(parts) == 1 and not is_prose(parts[0][2])


def header_names(lines, top, columns, data):
    """Header text over each value column, from the lines directly above the body.

    The lowest header line names each column. If it holds exactly one item per column, items
    and columns pair up in order (an item is a chunk, or for a chunk that spans several columns,
    a word with any following symbols such as "(%)" or "(↑)"). Otherwise only chunks that sit
    over exactly one column name it. Higher lines are group labels, given to the columns
    whose header they overlap or nearly touch."""
    header, i = [], top - 1
    if i >= 0 and not lines[i].strip():
        i -= 1
    while i >= 0 and lines[i].strip() and len(header) < 3:
        line = lines[i]
        if caption_like(line) or body_row(line) is not None or any(is_prose(c[2]) for c in chunks(line)):
            break
        header.append(line)
        i -= 1
    names = [None] * len(columns)
    if not header:
        return names
    first = columns[0][0]
    leaf = [c for c in chunks(header[0]) if c[1] > first - SLACK]
    spans = [None] * len(columns)
    for slack in (0, SLACK):
        items = split_items(leaf, columns, slack)
        if len(items) == len(columns):
            break
    if len(items) == len(columns):
        if all(overlap(it, (col[0] - SLACK, col[1] + SLACK)) > 0 for it, col in zip(items, columns)):
            spans = [it[:2] for it in items]
            names = [[it[2]] for it in items]
    else:
        claimed = {}
        for c in leaf:
            hit = [k for k, col in enumerate(columns) if overlap(c, (col[0] - SLACK, col[1] + SLACK)) > 0]
            if len(hit) > 1:
                hit = [k for k, col in enumerate(columns) if overlap(c, col) > 0] or hit
                hit = hit if len(hit) == 1 and " " not in c[2] else hit + [None]
            if not hit:
                near = sorted((gap(c, col), k) for k, col in enumerate(columns))
                if near[0][0] <= SLACK and (len(near) == 1 or near[1][0] > near[0][0]):
                    hit = [near[0][1]]
                else:
                    return [None] * len(columns)
            for k in hit:
                if k is not None:
                    claimed.setdefault(k, []).append(c if len(hit) == 1 else None)
        for k, cs in claimed.items():
            if len(cs) == 1 and cs[0] is not None:
                spans[k], names[k] = cs[0][:2], [cs[0][2]]
    for line in header[1:]:
        groups = [c for c in chunks(line) if c[1] > first - SLACK]
        for k, name in enumerate(names):
            if name is None or not groups:
                continue
            near = sorted((gap(g, spans[k]), n) for n, g in enumerate(groups))
            if near[0][0] <= SLACK and (len(near) == 1 or near[1][0] > near[0][0]):
                name.insert(0, groups[near[0][1]][2])
    return [[norm(p) for p in n] if n else None for n in names]


def split_items(leaf, columns, slack):
    """Header items of a line: each chunk, except that a chunk reaching over two or more columns
    (widened by `slack`) splits into words, each keeping any symbols that follow it ("(%)")."""
    items = []
    for c in leaf:
        if sum(overlap(c, (col[0] - slack, col[1] + slack)) > 0 for col in columns) < 2:
            items.append(c)
            continue
        for n, m in enumerate(re.finditer(r"\S+", c[2])):
            w = (m.start() + c[0], m.end() + c[0], m.group())
            if n and not re.search(r"\w", w[2]):
                items[-1] = (items[-1][0], w[1], items[-1][2] + " " + w[2])
            else:
                items.append(w)
    return items


def column_index(names, col):
    """The one column whose header, or the lower part of it, reads `col`; else None."""
    want = squash(col)
    hits = [k for k, n in enumerate(names) if n and any(squash(" ".join(n[i:])) == want for i in range(len(n)))]
    return hits[0] if len(hits) == 1 else None


def label_matches(label, row):
    """Whether consecutive label chunks of a body line read exactly `row`."""
    texts = [squash(c[2]) for c in label]
    return any("".join(texts[i:j]) == squash(row) for i in range(len(texts)) for j in range(i + 1, len(texts) + 1))


def check_values(folder, artifacts):
    records = read_batch(folder)
    cache = {}
    for sid, path in artifacts.items():
        if path.suffix == ".xml":
            cache[sid] = ("xml", xml_tables(path))
        else:
            raw = path.read_text(errors="replace").splitlines()
            cache[sid] = ("text", ([norm(l) for l in raw], raw, {}))
    rows_out, claims = [], {}
    for rec in records:
        if rec.get("kind") != "result":
            continue
        a = rec["attributes"]
        printed, loc = a.get("printed_value"), a.get("source_locator") or ""
        sid = next((s for s in rec.get("source_ids", []) if s in cache), None)
        m = LOCATOR.match(loc)
        if a.get("derivation"):
            status = "skipped_derived"
        elif printed is None:
            status = "skipped_no_printed_value"
        elif sid is None:
            status = "no_artifact_given"
        elif not m:
            status = "locator_not_parsed"
        else:
            table, row, value = m["table"], norm(m["row"]), norm(printed)
            kind, data = cache[sid]
            column = None
            if kind == "xml":
                body = data.get(norm(table))
                matched = [r for r in body or [] if r and squash(r[0]) == squash(row)]
                candidates = [" ".join(r) for r in matched] if body is not None else None
                if body and m["col"]:
                    header = [squash(c) for c in body[0]]
                    if squash(m["col"]) in header:
                        idx = header.index(squash(m["col"]))
                        column = [r[idx] for r in matched if idx < len(r)]
            else:
                lines, raw, parsed = data
                candidates = text_rows(lines, table, row)
                key = ((m["prefix"] or "").strip(), table)
                if key not in parsed:
                    parsed[key] = parse_text_table(raw, table, m["prefix"])[0]
                parsed_table = parsed[key]
                idx = None
                if parsed_table and m["col"]:
                    heading = m["col"] + (" " + m["sub"] if m["sub"] else "")
                    idx = column_index(parsed_table["names"], heading)
                if idx is not None:
                    matched = [r for r in parsed_table["rows"] if label_matches(r[1], row)]
                    if matched:
                        column = [r[2].get(idx, "") for r in matched]
            if candidates is None:
                status = "table_not_found"
            elif not candidates:
                status = "row_not_found"
            else:
                # Printed values may span tokens ("0.66 ± 0.02"); match as a token sequence.
                want = tokens(value)
                hit = [c for c in candidates
                       if any(tokens(c)[i:i + len(want)] == want for i in range(len(tokens(c))))]
                status = "in_row" if hit else "not_in_row"
                if hit:
                    claims.setdefault((sid, table, row, value), (candidates, []))[1].append(len(rows_out))
                if hit and column is not None:
                    # XML keeps cells apart, and a parsed text table places them by column, so the
                    # named column can be checked too. A text cell may hold more than the printed
                    # value ("6.2 (1.7)" for 6.2), so match it as a token sequence there.
                    if kind == "xml":
                        ok = any(squash(c) == squash(value) for c in column)
                    else:
                        ok = any(tokens(c)[i:i + len(want)] == want for c in column for i in range(len(tokens(c))))
                    status = "in_cell" if ok else "wrong_column"
        rows_out.append([rec["id"], status, printed or "", loc])
    # Every cell of a table is extracted, so a value claimed by more results than the row
    # prints it is a misread: usually a value copied from a neighbouring column.
    # A row label can repeat (blocks within one table), so count over every line carrying it.
    for (_, _, _, value), (lines, idxs) in claims.items():
        want = tokens(value)
        printed_times = sum(tokens(l)[i:i + len(want)] == want for l in lines for i in range(len(tokens(l))))
        if len(idxs) > printed_times:
            for i in idxs:
                if rows_out[i][1] == "in_row":
                    rows_out[i][1] = "overclaimed_in_row"
    counts = {}
    for r in rows_out:
        counts[r[1]] = counts.get(r[1], 0) + 1
    report = Path(folder) / "value-check.tsv"
    report.write_text("id\tstatus\tprinted_value\tsource_locator\n" +
                      "".join("\t".join(r) + "\n" for r in rows_out))
    return counts, report


def hash_batch(folder, artifacts):
    folder = Path(folder)
    sources = {r["id"]: r for r in read_batch(folder) if r.get("kind") == "source"}
    problems = []
    for sid, path in artifacts.items():
        expected = (sources.get(sid) or {}).get("attributes", {}).get("artifact_sha256")
        if expected is None:
            problems.append(f"{sid}: no source record with artifact_sha256 in batch.jsonl")
        elif sha256(path) != expected:
            problems.append(f"{sid}: {path} hashes to {sha256(path)}, source record says {expected}")
    if problems:
        raise SystemExit("artifact check failed:\n  " + "\n  ".join(problems))
    receipt_path = folder / "review.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        "schema_version": "1.0", "method": None, "review_methods": [], "reviewer": None,
        "reviewed_at": None, "scope": None, "limitations": [], "errors": []}
    receipt["files"] = {str(p.relative_to(folder)): sha256(p) for p in sorted(folder.rglob("*"))
                        if p.is_file() and p.name != "review.json" and "__pycache__" not in p.parts}
    receipt["source_artifacts"] = {sid: r["attributes"]["artifact_sha256"] for sid, r in sorted(sources.items())
                                   if r.get("attributes", {}).get("artifact_sha256")}
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    missing = [k for k in ("method", "reviewer", "reviewed_at", "scope") if not receipt.get(k)]
    return receipt, missing


def print_table(path, label):
    """Print a table of an artifact as TSV: header names, then one line per body line."""
    m = re.match(r"(?i)(?P<prefix>Appendix |Supplementary |Extended Data )?(?P<table>Table [A-Z]?\d+[a-z]?)$", label.strip())
    if not m:
        raise SystemExit(f"expected a label like 'Table 3' or 'Supplementary Table 4', got {label!r}")
    path = Path(path)
    if path.suffix == ".xml":
        rows = xml_tables(path).get(norm(m["table"]))
        if rows is None:
            raise SystemExit(f"{label} not found")
        for r in rows:
            print("\t".join(r))
        return 0
    lines = path.read_text(errors="replace").splitlines()
    parsed, reason = parse_text_table(lines, m["table"], m["prefix"])
    if parsed is None:
        raise SystemExit(f"{label}: {reason}; check values by row only")
    print("\t".join(["line", "row"] + [" / ".join(n) if n else "?" for n in parsed["names"]]))
    for i, label_chunks, cells in parsed["rows"]:
        if not label_chunks and not cells:
            continue
        print("\t".join([str(i + 1), " ".join(norm(c[2]) for c in label_chunks)]
                        + [cells.get(k, "") for k in range(len(parsed["columns"]))]))
    return 0


def main(argv):
    if len(argv) == 3 and argv[0] == "table":
        return print_table(argv[1], argv[2])
    if len(argv) < 2 or argv[0] not in ("check-values", "hash"):
        raise SystemExit(__doc__)
    command, folder, artifacts = argv[0], argv[1], parse_pairs(argv[2:])
    if command == "check-values":
        counts, report = check_values(folder, artifacts)
        print(json.dumps(counts, sort_keys=True))
        print(f"wrote {report}")
        return 0 if set(counts) <= {"in_cell", "in_row", "skipped_derived"} else 1
    receipt, missing = hash_batch(folder, artifacts)
    print(f"hashed {len(receipt['files'])} files and {len(receipt['source_artifacts'])} source artifacts")
    if missing:
        print("review.json still needs: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
