"""Mechanical steps of a batch review, so agents do not hand-write them.

  python3 scripts/omics/batch.py check-values <batch> <source-id>=<artifact> ...
      For every result, find the row named in its source_locator in the pinned artifact and
      check that printed_value appears in that row. Writes <batch>/value-check.tsv.
  python3 scripts/omics/batch.py hash <batch> [<source-id>=<artifact> ...]
      Check each artifact against its source record's artifact_sha256, then write the
      `files` and `source_artifacts` hashes into <batch>/review.json, keeping its other fields.

Artifacts are PMC/JATS XML (tables read from <tr> rows) or text (a PDF text layer from
pdftotext -layout, rows read as lines). The value check confirms the printed string is in the
named row. For XML it also checks the named column (`in_cell`). For text it cannot, but because
every cell is extracted it flags a value claimed by more results in a row than the row prints
(`overclaimed_in_row`), which catches most values copied from a neighbouring column. Column
assignment for text layers still needs the reviewer's sampled check.
"""
import hashlib
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

LOCATOR = re.compile(r'^(?:Appendix |Supplementary |Extended Data )?(?P<table>Table [A-Z]?\d+[a-z]?)\b.*?row ["\'](?P<row>[^"\']+)["\']'
                     r'(?:.*?col(?:umn)? ["\'](?P<col>[^"\']+)["\'])?')
WINDOW = 150  # text lines searched on each side of a table caption, which may sit above or below the rows


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


def check_values(folder, artifacts):
    records = read_batch(folder)
    cache = {}
    for sid, path in artifacts.items():
        if path.suffix == ".xml":
            cache[sid] = ("xml", xml_tables(path))
        else:
            cache[sid] = ("text", [norm(l) for l in path.read_text(errors="replace").splitlines()])
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
                candidates = text_rows(data, table, row)
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
                    # XML keeps cells apart, so the named column can be checked too.
                    status = "in_cell" if any(squash(c) == squash(value) for c in column) else "wrong_column"
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


def main(argv):
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
