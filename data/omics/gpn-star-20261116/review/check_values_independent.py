#!/usr/bin/env python3
"""Independent re-read of every GPN-Star result, written for the review pass.

Imports nothing from extract/build.py. The three value sources are read in three
different ways, and each result is matched to a cell through the text of its
source_locator, never through a record ID.

1. Supplementary Table 3 (56 cells) is read from the PDF's own word bounding
   boxes (`pdftotext -bbox-layout`), not from a `-layout` text dump. The page is
   rotated, so the table's columns run down the page's y axis and its rows run
   across the x axis. Column spans come from the header words' y extents, row
   spans from the row-label words' x extents, and every numeric token is placed
   in the (row, column) cell its own centre falls in. That makes the column
   assignment a geometric fact about the page rather than an assumption about
   the order the headers were printed in, which is the check build.py could not
   make: it asserted the column order positionally.
2. Fig. 4b's 12 bar labels are read from the article text layer, requiring the
   value and its series label to be on the same line.
3. The four rare variant association counts are read from the sentence the
   locator names.

Usage:
  python3 -I check_values_independent.py <batch.jsonl> <moesm1.pdf> <nature.pdf> <out.tsv>
    [--mutate <result-id>=<printed_value> ...]

--mutate rewrites a result's printed value before checking, for negative controls.
Exit status is 0 only when every row passes.
"""

import hashlib
import json
import re
import subprocess
import sys

SI_SHA = "3f7e8f71710bb63ec5ff032e697b6ef85f0d6d74411a31865fed73a757c7fc9e"
ART_SHA = "d7dfe801bad2a0a23478753147af2320bc31c8b37ee50d66f1a1af8385e9005d"

SI_TABLE_PAGE = 23
ART_FIG4_PAGE = 7
ART_RVAT_PAGE = 5

# The seven column labels, as Supplementary Table 3 prints them. Order is NOT
# assumed; it is recovered from the page geometry and then asserted to be this.
COLUMNS = [
    "ClinVar",
    "COSMIC",
    "ProteinGym",
    "Finemapped coding",
    "OMIM",
    "Finemapped non-coding",
    "HGMD",
]

ROWS = [
    "GPN-Star default",
    "only use one target species (human)",
    "no evol. distance encoding",
    "no pooling into clades",
    "no species tree (no evol. distances, no clades)",
    "MSA Transformer-like architecture",
    "GPN-MSA (exclude 10 closest species)",
    "GPN-MSA (no species curation)",
]

WORD_RE = re.compile(
    r'<word xMin="([\d.-]+)" yMin="([\d.-]+)" xMax="([\d.-]+)" yMax="([\d.-]+)">(.*?)</word>'
)
CELL_RE = re.compile(r"^(\d\.\d{3})$")
PAREN_RE = re.compile(r"^\((\d\.\d{3})\)$")
UNESCAPE = [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&apos;", "'"), ("&quot;", '"')]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def words(pdf, page):
    out = subprocess.run(
        ["pdftotext", "-bbox-layout", "-f", str(page), "-l", str(page), pdf, "-"],
        check=True, capture_output=True, text=True,
    ).stdout
    ws = []
    for x0, y0, x1, y1, text in WORD_RE.findall(out):
        for a, b in UNESCAPE:
            text = text.replace(a, b)
        ws.append((float(x0), float(y0), float(x1), float(y1), text))
    return ws


def layout_pages(pdf):
    out = subprocess.run(
        ["pdftotext", "-layout", pdf, "-"], check=True, capture_output=True, text=True
    ).stdout
    return out.split("\f")


def column_spans(ws):
    """Recover the seven column bands from the rotated header words' y extents.

    The header is rotated, so a column's horizontal position on the rendered
    page is its y position in PDF space, and a column further right has a
    smaller y. The two 'Finemapped' headers are disambiguated by which of
    'coding' / 'non-coding' overlaps them in y.
    """
    band = [w for w in ws if 285.0 < (w[0] + w[2]) / 2 < 312.0 and w[4] != "22"]
    singles = {}
    finemapped = []
    qualifiers = {}
    for x0, y0, x1, y1, text in band:
        if text == "Finemapped":
            finemapped.append((y0, y1))
        elif text in ("coding", "non-coding"):
            qualifiers[text] = (y0, y1)
        else:
            singles[text] = (y0, y1)
    if sorted(singles) != sorted(["ClinVar", "COSMIC", "ProteinGym", "OMIM", "HGMD"]):
        raise SystemExit(f"unexpected single-word headers: {sorted(singles)}")
    if len(finemapped) != 2 or sorted(qualifiers) != ["coding", "non-coding"]:
        raise SystemExit("did not find the two Finemapped headers and their qualifiers")

    spans = dict(singles)
    for y0, y1 in finemapped:
        matched = [
            q for q, (qy0, qy1) in qualifiers.items() if not (qy1 < y0 or qy0 > y1)
        ]
        if len(matched) != 1:
            raise SystemExit(f"Finemapped header at y {y0}-{y1} matches {matched}")
        spans[f"Finemapped {matched[0]}"] = (min(y0, qualifiers[matched[0]][0]),
                                             max(y1, qualifiers[matched[0]][1]))

    order = sorted(spans, key=lambda c: -(spans[c][0] + spans[c][1]) / 2)
    if order != COLUMNS:
        raise SystemExit(f"header order from page geometry is {order}, expected {COLUMNS}")
    # Columns must not overlap in y, or the cell assignment below is ambiguous.
    for a, b in zip(order, order[1:]):
        if spans[a][0] <= spans[b][1]:
            raise SystemExit(f"columns {a} and {b} overlap in y")
    return spans, order


def row_bands(ws, body_x):
    """Cluster the body words into one band per table row by their x centre.

    The page is rotated, so a table row is a set of words sharing an x centre.
    A bold cell is typeset in a slightly different position, so the clustering
    uses a tolerance rather than an exact key.
    """
    body = sorted(
        (w for w in ws if (w[0] + w[2]) / 2 > body_x and w[4] != "22"),
        key=lambda w: (w[0] + w[2]) / 2,
    )
    bands = []
    for w in body:
        xc = (w[0] + w[2]) / 2
        if bands and xc - bands[-1][0][-1] <= 3.0:
            bands[-1][0].append(xc)
            bands[-1][1].append(w)
        else:
            bands.append(([xc], [w]))
    if len(bands) != len(ROWS):
        raise SystemExit(f"clustered {len(bands)} row bands, expected {len(ROWS)}")
    return [group for _, group in bands]


def read_table(pdf):
    ws = words(pdf, SI_TABLE_PAGE)
    spans, col_order = column_spans(ws)
    centres = {c: (spans[c][0] + spans[c][1]) / 2 for c in col_order}
    pitch = min(
        abs(centres[a] - centres[b]) for a, b in zip(col_order, col_order[1:])
    )
    # the body starts to the right of every header word, including the
    # second-line qualifiers "coding" and "non-coding"
    header_x = max(
        (w[0] + w[2]) / 2
        for w in ws
        if w[4] in ("ClinVar", "COSMIC", "ProteinGym", "Finemapped", "OMIM", "HGMD", "coding", "non-coding")
    )
    # row labels sit above the first column, beyond half a column pitch
    label_y = centres["ClinVar"] + pitch * 0.5

    cells = {}
    found_rows = []
    for group in row_bands(ws, header_x):
        label_words = sorted(
            (w for w in group if (w[1] + w[3]) / 2 > label_y), key=lambda w: -w[1]
        )
        label = " ".join(w[4] for w in label_words)
        found_rows.append(label)
        for x0, y0, x1, y1, text in group:
            if (y0 + y1) / 2 > label_y:
                continue
            mean, mx = CELL_RE.match(text), PAREN_RE.match(text)
            if not (mean or mx):
                raise SystemExit(f"row {label!r} holds a non-numeric body token {text!r}")
            yc = (y0 + y1) / 2
            ranked = sorted(col_order, key=lambda c: abs(yc - centres[c]))
            near, runner = ranked[0], ranked[1]
            d_near, d_run = abs(yc - centres[near]), abs(yc - centres[runner])
            if d_near > pitch * 0.45 or d_run - d_near < pitch * 0.25:
                raise SystemExit(
                    f"token {text!r} in row {label!r} at y {yc:.1f} is "
                    f"{d_near:.1f} from {near} and {d_run:.1f} from {runner}"
                )
            slot = cells.setdefault((label, near), {})
            kind = "mean" if mean else "max"
            if kind in slot:
                raise SystemExit(f"two {kind} tokens in cell {label} / {near}")
            slot[kind] = ((mean or mx).group(1), yc)

    if found_rows != ROWS:
        raise SystemExit(f"row labels from page geometry are {found_rows}, expected {ROWS}")
    if len(cells) != 56:
        raise SystemExit(f"found {len(cells)} cells, expected 56")
    out = {}
    for key, slot in cells.items():
        if set(slot) != {"mean", "max"}:
            raise SystemExit(f"cell {key} has {sorted(slot)}")
        if slot["mean"][1] <= slot["max"][1]:
            raise SystemExit(f"cell {key} prints its parenthesised value before its mean")
        out[key] = {"mean": slot["mean"][0], "max": slot["max"][0]}
    return out


LOC_TABLE = re.compile(
    r"^Supplementary Table 3, row '(?P<row>.+)', column '(?P<col>.+)' \(PDF page 23\)$"
)
LOC_FIG4 = re.compile(
    r"^Fig\. 4b, row '(?P<row>.+)', printed bar label \(PDF page 7\)$"
)
LOC_RVAT = re.compile(
    r"^Results, rare variant association testing paragraph \(PDF page 5\)$"
)

# The two sentences that print the rare variant counts. Each pattern is typed
# from the page, not copied from the records, and its two capture groups fix
# which count belongs to DeepRVAT with GPN-Star annotations and which to the
# original method. The page is set in two columns, so each pattern is matched
# against single lines of the text layer, not across them.
RVAT_SENTENCES = {
    "discovered": re.compile(
        r"average across runs, (\d+) genes compared with (\d+) from the original"
    ),
    "replicated": re.compile(r"age (\d+) compared with (\d+)\), indicating"),
}
# result id suffix -> (which sentence, which capture group, which system)
RVAT = {
    "rvat-discovered-gpn-star": ("discovered", 1, "gpn-star-20261116-method-deeprvat-plus-gpn-star"),
    "rvat-discovered-original": ("discovered", 2, "gpn-star-20261116-method-deeprvat"),
    "rvat-replicated-gpn-star": ("replicated", 1, "gpn-star-20261116-method-deeprvat-plus-gpn-star"),
    "rvat-replicated-original": ("replicated", 2, "gpn-star-20261116-method-deeprvat"),
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--mutate")]
    mutations = {}
    for i, a in enumerate(sys.argv[1:]):
        if a == "--mutate":
            k, _, v = sys.argv[2 + i].partition("=")
            mutations[k] = v
    batch, si_pdf, art_pdf, out_tsv = args[:4]

    assert sha256(si_pdf) == SI_SHA, "supplementary PDF hash does not match the source record"
    assert sha256(art_pdf) == ART_SHA, "article PDF hash does not match the source record"

    table = read_table(si_pdf)
    art = layout_pages(art_pdf)
    fig4 = art[ART_FIG4_PAGE - 1]
    rvat_page = art[ART_RVAT_PAGE - 1]

    records = [json.loads(l) for l in open(batch)]
    results = [r for r in records if r["kind"] == "result"]
    evals = {r["id"]: r for r in records if r["kind"] == "evaluation"}
    protos = {r["id"]: r for r in records if r["kind"] == "protocol"}
    configs = {r["id"]: r for r in records if r["kind"] == "configuration"}

    unknown = set(mutations) - {r["id"] for r in results}
    if unknown:
        raise SystemExit(f"--mutate names ids that are not results in this batch: {sorted(unknown)}")

    rows_out = []
    failures = 0
    seen_fig4 = set()
    for r in sorted(results, key=lambda r: r["id"]):
        a = r["attributes"]
        printed = mutations.get(r["id"], a["printed_value"])
        loc = a["source_locator"]
        ev = evals[[l["target_id"] for l in r["links"] if l["relation"] == "evaluation"][0]]
        proto_id = [l["target_id"] for l in ev["links"] if l["relation"] == "assessment"][0]
        sys_id = [l["target_id"] for l in ev["links"] if l["relation"] == "system"][0]
        status, detail = "FAIL", ""

        m = LOC_TABLE.match(loc)
        if m:
            key = (m["row"], m["col"])
            if key not in table:
                detail = f"locator names no cell of the table: {key}"
            else:
                cell = table[key]
                want_cell = f"{cell['mean']} ({cell['max']})"
                problems = []
                if printed != cell["mean"]:
                    problems.append(
                        f"printed_value {printed} is not the cell mean {cell['mean']}"
                        + (f"; that value is the column's {[c for c in COLUMNS if table.get((m['row'],c),{}).get('mean')==printed]} mean in this row"
                           if any(table.get((m["row"], c), {}).get("mean") == printed for c in COLUMNS) else "")
                    )
                if a.get("printed_source_cell") != want_cell:
                    problems.append(f"printed_source_cell {a.get('printed_source_cell')!r} != {want_cell!r}")
                if cell["max"] not in (a.get("source_statistic") or ""):
                    problems.append(f"source_statistic does not carry the max {cell['max']}")
                if a["numeric_value"] != cell["mean"]:
                    problems.append(f"numeric_value {a['numeric_value']} != {cell['mean']}")
                # the protocol the evaluation points at must name this column
                pname = protos[proto_id]["name"]
                expect = {
                    "ClinVar": "clinvar", "COSMIC": "cosmic", "ProteinGym": "proteingym",
                    "Finemapped coding": "finemapped-coding", "OMIM": "omim",
                    "Finemapped non-coding": "finemapped-noncoding", "HGMD": "hgmd",
                }[m["col"]]
                if expect not in proto_id:
                    problems.append(f"protocol {proto_id} does not match column {m['col']}")
                want_metric = "spearman-correlation" if m["col"] == "ProteinGym" else "auprc"
                if a["metric"] != want_metric:
                    problems.append(f"metric {a['metric']} != {want_metric} for column {m['col']}")
                if problems:
                    detail = "; ".join(problems)
                else:
                    status, detail = "in_cell", f"{want_cell} [{pname[:28]}]"
            rows_out.append((r["id"], "suppl-table-3", loc, printed, status, detail))
        elif LOC_FIG4.match(loc):
            label = LOC_FIG4.match(loc)["row"]
            # The value label must be the first token printed after the series
            # label on the same line of the figure; a line that names the series
            # without a number (panel d's legend) does not count.
            pat = re.compile(rf"(?<![\w)]){re.escape(label)}\s+(\d+\.\d)(?!\d)")
            hits = [
                (ln, pat.search(ln).group(1))
                for ln in fig4.splitlines()
                if pat.search(ln)
            ]
            if len(hits) != 1:
                detail = f"found {len(hits)} lines printing a number beside {label!r}"
            else:
                got = hits[0][1]
                if got != printed:
                    detail = f"line prints {got} beside {label!r}, record says {printed}"
                elif a["metric"] != "odds-ratio":
                    detail = f"metric {a['metric']} != odds-ratio"
                elif (label, got) in seen_fig4:
                    detail = "duplicate label/value pair"
                else:
                    seen_fig4.add((label, got))
                    status, detail = "in_cell", f"same line as {label!r}"
            rows_out.append((r["id"], "fig-4b", loc, printed, status, detail))
        elif LOC_RVAT.match(loc):
            tag = [k for k in RVAT if k in r["id"]]
            if len(tag) != 1:
                detail = f"result id does not name one rare variant count: {tag}"
            else:
                sentence, group, want_system = RVAT[tag[0]]
                pat = RVAT_SENTENCES[sentence]
                hits = [pat.search(ln) for ln in rvat_page.splitlines() if pat.search(ln)]
                if len(hits) != 1:
                    detail = f"{len(hits)} lines on page 5 match the {sentence} sentence"
                else:
                    want = hits[0].group(group)
                    other = hits[0].group(3 - group)
                    if printed != want:
                        detail = (
                            f"the {sentence} sentence gives {want} in position {group} "
                            f"and {other} in the other; record says {printed}"
                        )
                    elif a["metric"] != "count" or a["unit"] != "count":
                        detail = f"metric/unit {a['metric']}/{a['unit']} not count/count"
                    elif sys_id != want_system:
                        detail = f"system {sys_id} is not {want_system}"
                    else:
                        status = "in_sentence"
                        detail = hits[0].group(0)[:70]
            rows_out.append((r["id"], "rvat-prose", loc, printed, status, detail))
        else:
            rows_out.append((r["id"], "unparsed", loc, printed, "FAIL", "locator did not parse"))

        if rows_out[-1][4] == "FAIL":
            failures += 1

    with open(out_tsv, "w") as fh:
        fh.write("result_id\tsource\tlocator\tprinted_value\tstatus\tdetail\n")
        for row in rows_out:
            fh.write("\t".join(str(c) for c in row) + "\n")

    counts = {}
    for row in rows_out:
        counts[row[4]] = counts.get(row[4], 0) + 1
    print(f"{len(rows_out)} results checked: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if mutations:
        print("mutations applied: " + ", ".join(f"{k}={v}" for k, v in mutations.items()))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
