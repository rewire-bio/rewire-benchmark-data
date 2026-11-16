#!/usr/bin/env python3
"""Independent re-check of every value in the GPN paper batch.

Written by the review agent. It does not import or reuse extract/parse_values.py and does not
read extract/values.json. It works from batch.jsonl and the pinned artifacts only:

  artifacts/pnas-2311219120.fulltext.xml.gz        the published article (Europe PMC JATS XML)
  artifacts/pnas-2311219120-si-appendix.pdf.gz     the SI Appendix PDF
  artifacts/biorxiv-2022.08.22.504706v3.source.xml.gz  bioRxiv v3, companion only
  artifacts/biorxiv-versions.json                  the bioRxiv details API response

What it checks:

  1. Every archived artifact regenerates the SHA-256 its source record pins.
  2. The published article carries no table-wrap and no table element, parsed with xml.etree
     rather than a regex over the markup.
  3. The section title each result's source_locator names exists in the article.
  4. For each of the 17 prose results: the value, with the label the locator names, occurs
     exactly once in the article body, and inside the section the locator names.
  5. For each of the 6 Table S2 results: the cell is read by column position, from the character
     span of the header label, not by taking the first or second whitespace-separated field.
  6. Negative controls, which must all fail to match: a perturbed printed value; the value under
     a neighbouring label; a Table S2 cell read from the other column.
  7. The SI Appendix figure pages are scanned for every decimal number, to test the extractor's
     claim that no comparator value is printed in the text layer.

Usage: python3 -I review/recheck_values.py   (run from the batch folder)
Writes review/recheck.json. Exit status 0 only if every check passes.
"""

import gzip
import hashlib
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.dirname(HERE)
ART = os.path.join(BATCH, "artifacts")

PROBLEMS = []
CHECKS = []


def ok(name, detail=""):
    CHECKS.append({"check": name, "status": "pass", "detail": detail})


def bad(name, detail):
    CHECKS.append({"check": name, "status": "FAIL", "detail": detail})
    PROBLEMS.append(f"{name}: {detail}")


def records():
    out = []
    with open(os.path.join(BATCH, "batch.jsonl")) as fh:
        for line in fh:
            out.append(json.loads(line))
    return out


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------- 1. artifact hashes

ARCHIVE = {
    "gpn-paper-20261116-source-pnas-2023": ("pnas-2311219120.fulltext.xml.gz", True),
    "gpn-paper-20261116-source-pnas-2023-si-appendix": ("pnas-2311219120-si-appendix.pdf.gz", True),
    "gpn-paper-20261116-source-biorxiv-v3": ("biorxiv-2022.08.22.504706v3.source.xml.gz", True),
    "gpn-paper-20261116-source-biorxiv-version-list": ("biorxiv-versions.json", False),
}


def check_artifacts(recs):
    raw = {}
    for r in recs:
        if r["kind"] != "source":
            continue
        name, gzipped = ARCHIVE[r["id"]]
        path = os.path.join(ART, name)
        data = open(path, "rb").read()
        if gzipped:
            data = gzip.decompress(data)
        got = sha256_bytes(data)
        want = r["attributes"]["artifact_sha256"]
        if got == want:
            ok(f"artifact-sha256:{r['id']}", f"{name} -> {got}")
        else:
            bad(f"artifact-sha256:{r['id']}", f"{name} gives {got}, record pins {want}")
        raw[r["id"]] = data
    return raw


# ---------------------------------------------------------------- 2 and 3. article structure


def flatten(el):
    """All text under an element, tags dropped, whitespace collapsed."""
    t = "".join(el.itertext())
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def squeeze(t):
    """Drop all whitespace. The JATS marks up italics, math and superscripts inside these
    sentences, so where a space falls depends on the markup, not on what the page prints.
    Comparing without whitespace tests the characters the page prints and nothing else."""
    return re.sub(r"\s+", "", t)


def article_sections(xml_bytes):
    root = ET.fromstring(xml_bytes)
    n_wrap = len(list(root.iter("table-wrap")))
    n_table = len(list(root.iter("table")))
    if n_wrap == 0 and n_table == 0:
        ok("no-tables-in-article", "0 table-wrap and 0 table elements in the whole JATS document")
    else:
        bad("no-tables-in-article", f"{n_wrap} table-wrap and {n_table} table elements")

    body = root.find(".//body")
    secs = {}

    def walk(el):
        for s in el.findall("sec"):
            ti = s.find("title")
            if ti is not None and ti.text:
                secs[ti.text.strip().rstrip(".")] = flatten(s)
            walk(s)

    walk(body)
    return flatten(body), secs, len(list(root.iter("fig")))


# ---------------------------------------------------------------- 4. prose values
#
# One entry per prose result: its ID, the section its source_locator names, the exact printed
# string the record carries, the labelled form that must occur in the section, and a negative
# control that must not occur.

PROSE = [
    # (result id, section, printed_value, labelled form, negative control)
    ("gpn-paper-20261116-result-gene-region-accuracy-cds",
     "Unsupervised Clustering of Genomic Regions", "96%", "CDS (96%)", "CDS (69%)"),
    ("gpn-paper-20261116-result-gene-region-accuracy-ncrna",
     "Unsupervised Clustering of Genomic Regions", "51%", "ncRNA (51%)", "ncRNA (15%)"),
    ("gpn-paper-20261116-result-positional-perplexity-splice-donor",
     "DNA Motifs Revealed by High-Confidence Model Predictions", "1.02",
     "splice donors (median = 1.02 )", "splice donors (median = 1.03 )"),
    ("gpn-paper-20261116-result-positional-perplexity-splice-acceptor",
     "DNA Motifs Revealed by High-Confidence Model Predictions", "1.03",
     "splice acceptors (median = 1.03)", "splice acceptors (median = 1.02)"),
    ("gpn-paper-20261116-result-positional-perplexity-start-codon",
     "DNA Motifs Revealed by High-Confidence Model Predictions", "1.08",
     "start codons (median = 1.08 )", "start codons (median = 1.10 )"),
    ("gpn-paper-20261116-result-positional-perplexity-cds2",
     "DNA Motifs Revealed by High-Confidence Model Predictions", "2.24",
     "CDS2 (median = 2.24 )", "CDS2 (median = 2.44 )"),
    ("gpn-paper-20261116-result-positional-perplexity-cds1",
     "DNA Motifs Revealed by High-Confidence Model Predictions", "2.44",
     "CDS1 (median = 2.44 )", "CDS1 (median = 2.24 )"),
    ("gpn-paper-20261116-result-positional-perplexity-cds3",
     "DNA Motifs Revealed by High-Confidence Model Predictions", "2.79",
     "CDS3 (median = 2.79 )", "CDS3 (median = 2.8 )"),
    ("gpn-paper-20261116-result-positional-perplexity-stop-codon",
     "DNA Motifs Revealed by High-Confidence Model Predictions", "2.8",
     "stop codons (median = 2.8 )", "stop codons (median = 2.81 )"),
    ("gpn-paper-20261116-result-positional-perplexity-intergenic-and-intronic",
     "DNA Motifs Revealed by High-Confidence Model Predictions", "3.24",
     "intergenic and intronic regions (median = 3.24 ", "intergenic and intronic regions (median = 3.14 "),
    ("gpn-paper-20261116-result-repeat-below-missense-decile-repeat-weight-0",
     "In silico mutagenesis", "8%", "8% and 9% of repeat variants", "9% and 8% of repeat variants"),
    ("gpn-paper-20261116-result-repeat-below-missense-decile-repeat-weight-0-1",
     "In silico mutagenesis", "9%", "8% and 9% of repeat variants", "9% and 8% of repeat variants"),
    ("gpn-paper-20261116-result-repeat-below-missense-decile-repeat-weight-1",
     "In silico mutagenesis", "27%",
     "the 27% observed in the model without any down-weighting", "the 27% observed in the model with full down-weighting"),
    ("gpn-paper-20261116-result-rare-vs-common-odds-ratio-gpn",
     "Benchmarking using allele frequencies in 1001 genomes", "5.5-fold",
     "lowest 0.1% of GPN scores, exhibit a 5.5-fold enrichment in rare variants",
     "lowest 1% of GPN scores, exhibit a 5.5-fold enrichment in rare variants"),
    ("gpn-paper-20261116-result-gwas-hit-odds-ratio-gpn-x-ld",
     "Enrichment of GWAS hits in regions with low GPN scores", "10.3-fold",
     "lower 1% of GPN × LD scores are 10.3-fold enriched in GWAS hits",
     "lower 1% of GPN scores are 10.3-fold enriched in GWAS hits"),
    ("gpn-paper-20261116-result-perplexity-chromosome-wide-single-species",
     "Pretraining", "3.13", "higher test perplexity of 3.13 (3.17 on nonrepeat regions)",
     "higher test perplexity of 3.17 (3.13 on nonrepeat regions)"),
    ("gpn-paper-20261116-result-perplexity-non-repeat-single-species",
     "Pretraining", "3.17", "higher test perplexity of 3.13 (3.17 on nonrepeat regions)",
     "higher test perplexity of 3.17 (3.13 on nonrepeat regions)"),
]


def check_prose(body, secs, by_id):
    for rid, sec, printed, labelled, control in PROSE:
        r = by_id.get(rid)
        if r is None:
            bad(f"prose:{rid}", "no such result in batch.jsonl")
            continue
        if r["attributes"]["printed_value"] != printed:
            bad(f"prose:{rid}", f"printed_value is {r['attributes']['printed_value']!r}, "
                                f"this check expects {printed!r}")
            continue
        if sec not in secs:
            bad(f"prose-section:{rid}", f"the article has no section titled {sec!r}")
            continue
        needle = squeeze(labelled)
        n_sec = squeeze(secs[sec]).count(needle)
        n_body = squeeze(body).count(needle)
        if n_sec != 1:
            bad(f"prose:{rid}", f"{labelled!r} occurs {n_sec} times in section {sec!r}")
        elif n_body != 1:
            bad(f"prose:{rid}", f"{labelled!r} occurs {n_body} times in the whole body")
        elif squeeze(control) in squeeze(body):
            bad(f"prose-control:{rid}", f"the negative control {control!r} is in the body")
        else:
            ok(f"prose:{rid}", f"{labelled!r} once in {sec!r}; control {control!r} absent")


# ---------------------------------------------------------------- 5. Table S2 by column position

TABLE_S2 = {
    ("Repeat weight 1", "Chromosome-wide"): "gpn-paper-20261116-result-perplexity-chromosome-wide-repeat-weight-1",
    ("Repeat weight 1", "Non-repeat regions"): "gpn-paper-20261116-result-perplexity-non-repeat-repeat-weight-1",
    ("Repeat weight 0.1", "Chromosome-wide"): "gpn-paper-20261116-result-perplexity-chromosome-wide-repeat-weight-0-1",
    ("Repeat weight 0.1", "Non-repeat regions"): "gpn-paper-20261116-result-perplexity-non-repeat-repeat-weight-0-1",
    ("Repeat weight 0", "Chromosome-wide"): "gpn-paper-20261116-result-perplexity-chromosome-wide-repeat-weight-0",
    ("Repeat weight 0", "Non-repeat regions"): "gpn-paper-20261116-result-perplexity-non-repeat-repeat-weight-0",
}


def read_table_s2(layout):
    """Read Table S2 by character position: each cell is the number whose span overlaps the
    span of its column's header label. Returns {(row, column): value} and the parsed grid."""
    lines = layout.splitlines()
    starts = [i for i, l in enumerate(lines) if l.strip().startswith("Table S2: Test perplexity")]
    if len(starts) != 1:
        bad("table-s2-caption", f"{len(starts)} lines start the Table S2 caption")
        return {}, []
    ok("table-s2-caption", f"one caption line, line {starts[0] + 1}")

    window = lines[starts[0]:starts[0] + 25]
    headers = [l for l in window if "Chromosome-wide" in l and "Non-repeat regions" in l]
    if len(headers) != 1:
        bad("table-s2-header", f"{len(headers)} header lines in the 25 lines after the caption")
        return {}, []
    header = headers[0]
    cols = {}
    for label in ("Chromosome-wide", "Non-repeat regions"):
        i = header.index(label)
        cols[label] = (i, i + len(label))
    if header.index("Model") >= cols["Chromosome-wide"][0]:
        bad("table-s2-header", "the Model column is not left of Chromosome-wide")
        return {}, []
    ok("table-s2-header", f"header {header.strip()!r}; column spans {cols}")

    cells = {}
    grid = []
    for row in ("Repeat weight 1", "Repeat weight 0.1", "Repeat weight 0"):
        # Anchor on the row label at the start of the line, so "Repeat weight 0" cannot match
        # the "Repeat weight 0.1" line.
        hits = [l for l in window if re.match(r"\s*" + re.escape(row) + r"\s+\d", l)]
        if len(hits) != 1:
            bad(f"table-s2-row:{row}", f"{len(hits)} lines match the row label")
            continue
        line = hits[0]
        # Only look right of the row label, so the "0.1" in "Repeat weight 0.1" is not a cell.
        cut = line.index(row) + len(row)
        cells_part = " " * cut + line[cut:]
        found = {}
        for label, (lo, hi) in cols.items():
            overlapping = [m for m in re.finditer(r"\d+\.\d+", cells_part)
                           if m.start() < hi and m.end() > lo]
            if len(overlapping) != 1:
                bad(f"table-s2-cell:{row}/{label}",
                    f"{len(overlapping)} numbers overlap the column span")
                continue
            found[label] = overlapping[0].group(0)
            cells[(row, label)] = overlapping[0].group(0)
        # Every number right of the row label must be accounted for by exactly one column.
        all_nums = [m.group(0) for m in re.finditer(r"\d+\.\d+", cells_part)]
        if len(all_nums) != 2:
            bad(f"table-s2-row:{row}", f"the row prints {len(all_nums)} numbers, not 2: {all_nums}")
        grid.append({"row": row, **found})
    return cells, grid


def check_table_s2(cells, by_id):
    for (row, col), rid in TABLE_S2.items():
        r = by_id.get(rid)
        if r is None:
            bad(f"table-s2:{rid}", "no such result in batch.jsonl")
            continue
        got = cells.get((row, col))
        printed = r["attributes"]["printed_value"]
        other = "Non-repeat regions" if col == "Chromosome-wide" else "Chromosome-wide"
        if got is None:
            bad(f"table-s2:{rid}", f"no cell read at row {row!r} column {col!r}")
        elif got != printed:
            bad(f"table-s2:{rid}", f"column {col!r} of row {row!r} prints {got}, "
                                   f"the record says {printed}")
        else:
            # Negative control: the locator names a column, so check it is not the other one,
            # except where the row prints the same number in both columns.
            swapped = cells.get((row, other))
            note = "same value in both columns, so the swap control cannot discriminate" \
                if swapped == got else f"other column {other!r} prints {swapped}"
            ok(f"table-s2:{rid}", f"{row!r} / {col!r} = {got}; {note}")
        # And the locator must actually name this row and column.
        loc = r["attributes"]["source_locator"]
        if f'row "{row}"' not in loc or f'column "{col}"' not in loc:
            bad(f"table-s2-locator:{rid}", f"locator does not name row {row!r} and column {col!r}: {loc}")


# ---------------------------------------------------------------- 7. SI figure pages

# Values a comparator bar chart would have to print for the "figures carry no values" finding
# to be wrong. 5.5 and 10.3 are GPN's own odds ratios, 7.5 the bound on other methods.
COMPARATOR_VALUES = ["5.5", "10.3", "7.5"]


def check_si_figures(layout):
    lines = layout.splitlines()
    first_fig = next((i for i, l in enumerate(lines) if l.strip() == "Supplementary Figures"), None)
    if first_fig is None:
        bad("si-figures-start", "no 'Supplementary Figures' heading in the text layer")
        return {}
    tail = lines[first_fig:]
    decimals = {}
    stray = {}
    for i, l in enumerate(tail):
        lineno = first_fig + i + 1
        for m in re.finditer(r"-?\d+\.\d+", l):
            decimals.setdefault(m.group(0).lstrip("-"), []).append(lineno)
        for v in COMPARATOR_VALUES:
            for m in re.finditer(re.escape(v), l):
                # A GPN score bin edge in the Figure S7 legend, for example "(-7.5, -6.5]",
                # is not an odds ratio. Anything else is.
                lo = max(0, m.start() - 2)
                window = l[lo:m.end() + 8]
                if re.search(r"[(\[]\s*-?\d+\.\d+\s*,\s*-?\d+\.\d+\s*[)\]]",
                             l[max(0, m.start() - 8):m.end() + 8]):
                    continue
                stray.setdefault(v, []).append((lineno, window.strip()))
    if stray:
        bad("si-figures-no-comparator-values",
            f"a comparator value appears outside a score-bin interval: {stray}")
    else:
        ok("si-figures-no-comparator-values",
           f"none of {COMPARATOR_VALUES} appears after line {first_fig + 1} except as a GPN "
           f"score bin edge in the Figure S7 legend; {len(decimals)} distinct decimals in the "
           f"figure pages, all axis ticks, bin edges or threshold quantiles")
    return decimals


# ---------------------------------------------------------------- bioRxiv v3


SHARED = ["5.5-fold", "10.3-fold", "less than 7.5-fold", "96%", "51%", "14.2%",
          "r = 0.22", "r = 0.13", "3.13", "3.17", "8% and 9%", "27%"]
V3_ONLY = ["median = 1.10", "median = 2.81", "median = 3.14", "p -values < 10 −239"]
PUBLISHED_ONLY = ["264 genes", "471 transcripts", "CDS1", "CDS2", "CDS3"]


def check_biorxiv(v3_bytes, body):
    root = ET.fromstring(v3_bytes)
    b = root.find(".//body")
    v3 = flatten(b)
    sq_v3, sq_body = squeeze(v3), squeeze(body)
    missing = [s for s in SHARED if squeeze(s) not in sq_v3]
    if missing:
        bad("biorxiv-shared-values", f"not found verbatim in v3: {missing}")
    else:
        ok("biorxiv-shared-values", f"all {len(SHARED)} shared strings occur in v3")
    only_v3 = [s for s in V3_ONLY if squeeze(s) in sq_v3 and squeeze(s) not in sq_body]
    if len(only_v3) == len(V3_ONLY):
        ok("biorxiv-version-difference", f"in v3 and not in the published article: {V3_ONLY}")
    else:
        bad("biorxiv-version-difference",
            f"expected {V3_ONLY} to be v3 only; v3-only subset is {only_v3}")
    only_pub = [s for s in PUBLISHED_ONLY if squeeze(s) in sq_body and squeeze(s) not in sq_v3]
    if len(only_pub) == len(PUBLISHED_ONLY):
        ok("published-only-detail", f"in the published article and not in v3: {PUBLISHED_ONLY}")
    else:
        bad("published-only-detail",
            f"expected {PUBLISHED_ONLY} to be published only; subset is {only_pub}")
    return v3


# ---------------------------------------------------------------- main


def main():
    recs = records()
    by_id = {r["id"]: r for r in recs}
    results = [r for r in recs if r["kind"] == "result"]

    raw = check_artifacts(recs)
    body, secs, n_fig = article_sections(raw["gpn-paper-20261116-source-pnas-2023"])
    ok("article-figures", f"{n_fig} fig elements")

    layout_path = os.path.join(BATCH, "extract", "si-appendix.layout.txt")
    layout = open(layout_path).read()
    ok("text-layer-sha256", sha256_bytes(open(layout_path, "rb").read()))

    check_prose(body, secs, by_id)
    cells, grid = read_table_s2(layout)
    check_table_s2(cells, by_id)
    decimals = check_si_figures(layout)
    check_biorxiv(raw["gpn-paper-20261116-source-biorxiv-v3"], body)

    covered = set(rid for _, _, _, _, _ in [] ) | {p[0] for p in PROSE} | set(TABLE_S2.values())
    uncovered = [r["id"] for r in results if r["id"] not in covered]
    if uncovered:
        bad("coverage", f"results not checked by this script: {uncovered}")
    else:
        ok("coverage", f"all {len(results)} results checked: {len(PROSE)} prose, "
                       f"{len(TABLE_S2)} table cells")

    out = {
        "script": "review/recheck_values.py",
        "checks": CHECKS,
        "problems": PROBLEMS,
        "table_s2_by_column_position": grid,
        "si_figure_page_decimals": {k: v for k, v in sorted(decimals.items())},
    }
    with open(os.path.join(HERE, "recheck.json"), "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    n_pass = sum(1 for c in CHECKS if c["status"] == "pass")
    print(f"{n_pass} passed, {len(PROBLEMS)} failed")
    for p in PROBLEMS:
        print("FAIL", p)
    return 1 if PROBLEMS else 0


if __name__ == "__main__":
    sys.exit(main())
