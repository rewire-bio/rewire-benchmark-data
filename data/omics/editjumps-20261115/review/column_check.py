#!/usr/bin/env python3
"""Independent column-assignment check for the EditJumps batch.

Written by the review agent, not the extractor. It does not reuse extract/tables.py
or extract/check_tables.py, and it never matches a value against row text.

Two independent column models are built for Tables 1, 2 and 4:

  pdf   the pdftotext -layout text layer. Tables 2 and 4 print right-aligned
        columns, so every printed field is assigned to a column by clustering
        field right edges across the whole table and checking each row puts
        exactly one field in each cluster. Table 1's lower block runs its
        columns together (93.86 and 30.28 are one space apart), so right edges
        are useless there and the assignment is by ordinal position of the
        field within the row instead.
  html  the arXiv HTML rendering, parsed as a cell grid. Column identity comes
        from the table markup, not from spacing.

A stored result is accepted only when both models return its printed value at
the column its source_locator names, in the block its source_locator names.

Four negative controls mutate the source grids and must be rejected:
  swap-adjacent-columns, shift-row-left, swap-sub-columns, swap-blocks.

Usage:
  python3 -I review/column_check.py <layout.txt> <arxiv-html.html> <batch.jsonl>
"""

import html as htmlmod
import json
import re
import sys
import unicodedata

# ---------------------------------------------------------------- helpers


def norm(s):
    """Normalise a label for comparison: unicode form, spacing, quotes."""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("−", "-").replace("–", "-").replace("—", "-")
    s = s.replace("’", "'")
    # the PDF prints INCREMENT where the markup uses GREEK CAPITAL LETTER DELTA
    s = s.replace("∆", "Δ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def squash(s):
    """Canonical key for a row or column label: no spacing, no LaTeX echo."""
    s = norm(s)
    s = re.sub(r"\\[A-Za-z]+", "", s)
    return re.sub(r"\s+", "", s)


def normval(s):
    """Normalise a printed value: strip LaTeX echo, unify minus and dashes."""
    s = norm(s)
    s = s.replace("±", "+-")
    # the HTML renderer echoes the LaTeX after the rendered text: "84.3 84.3"
    parts = s.split()
    half = len(parts) // 2
    if len(parts) % 2 == 0 and parts[:half] == parts[half:]:
        s = " ".join(parts[:half])
    return s


def isdash(s):
    return normval(s) in {"-", "--"}


# ---------------------------------------------------------------- pdf layer


def fields(line):
    """Split a printed line into fields: runs of text separated by 2+ spaces.

    Returns (start, end, text) with end exclusive, so `end` is the right edge.
    """
    out = []
    for m in re.finditer(r"\S(?:.*?\S)?(?=\s{2,}|$)", line):
        if m.group().strip():
            out.append((m.start(), m.end(), m.group().strip()))
    return out


def tokens(line):
    out = []
    for m in re.finditer(r"\S+", line):
        out.append((m.start(), m.end(), m.group()))
    return out


def cluster_right_edges(rows, ncols, tol=2):
    """Cluster field right edges of data rows into exactly ncols columns."""
    edges = sorted(e for r in rows for (_s, e, _t) in r)
    groups = []
    for e in edges:
        if groups and e - groups[-1][-1] <= tol:
            groups[-1].append(e)
        else:
            groups.append([e])
    if len(groups) != ncols:
        raise AssertionError(
            "expected %d right-edge clusters, found %d: %s"
            % (ncols, len(groups), [g[0] for g in groups])
        )
    return [(min(g) - tol, max(g) + tol) for g in groups]


def assign_by_right_edge(row, windows):
    """Place each field of a row in the column window holding its right edge."""
    cells = [None] * len(windows)
    for (_s, e, text) in row:
        hit = [i for i, (lo, hi) in enumerate(windows) if lo <= e <= hi]
        if len(hit) != 1:
            raise AssertionError("field %r right edge %d matches %r" % (text, e, hit))
        if cells[hit[0]] is not None:
            raise AssertionError("two fields in column %d: %r" % (hit[0], text))
        cells[hit[0]] = text
    return cells


def pdf_tables(path):
    lines = open(path, encoding="utf-8").read().split("\n")

    # ---- Table 2: right-aligned, two family blocks, ten metric columns.
    t2_rows = {}
    block = None
    hdr_line = None
    for i, line in enumerate(lines):
        if line.strip().startswith("method") and "prof." in line and "cov." in line:
            hdr_line = i
            break
    assert hdr_line is not None, "Table 2 header not found"
    # The printed heading tokens run together (MMD ends at 46, KL starts at 47),
    # so the heading line cannot be split into columns by spacing. What it can
    # do is fix the left-to-right ORDER: the first token of each heading must
    # appear in the heading line in the order the columns are printed. That
    # order is checked against the HTML markup in cross_check().
    t2_hdr_tokens = tokens(lines[hdr_line]) + tokens(lines[hdr_line + 1])

    data = []
    for line in lines[hdr_line + 1:]:
        st = line.strip()
        if not st:
            if data:
                break
            continue
        if st in ("ty1", "her2vh"):
            block = st
            continue
        if st.startswith("A ") or st.startswith("Table"):
            break
        if block is None:
            continue
        fs = fields(line)
        label = norm(fs[0][2])
        data.append((block, label, fs[1:]))
    assert len(data) == 16, "Table 2: expected 16 data rows, got %d" % len(data)

    windows = cluster_right_edges([d[2] for d in data], 10)
    for block, label, fs in data:
        t2_rows[(block, label)] = assign_by_right_edge(fs, windows)
    t2_order_pdf = None  # named from the markup, order checked in cross_check

    # ---- Table 1: two blocks, four metrics x two sub-columns, by ordinal.
    t1_hdr = None
    for i, line in enumerate(lines):
        if "edits/seq" in line and "diversity" in line and "MMD" in line:
            t1_hdr = i
            break
    assert t1_hdr is not None, "Table 1 header not found"
    grouped = []
    for s, e, t in tokens(lines[t1_hdr]):
        if grouped and s - grouped[-1][1] <= 1:
            grouped[-1] = (grouped[-1][0], e, grouped[-1][2] + " " + t)
        else:
            grouped.append((s, e, t))
    metrics = [norm(t) for (_s, _e, t) in grouped]
    metrics = [m for m in metrics if m not in ("↓",)]
    metrics = [re.sub(r"\s*↓$", "", m) for m in metrics]
    subs = [norm(t) for (_s, _e, t) in tokens(lines[t1_hdr + 1])][1:]
    assert len(metrics) == 4 and len(subs) == 8, (metrics, subs)
    t1_order = [(metrics[i // 2], subs[i]) for i in range(8)]

    t1_rows = {}
    block = None
    for line in lines[t1_hdr + 2:]:
        st = line.strip()
        if not st:
            if t1_rows:
                break
            continue
        if st.startswith("ours —") or st.startswith("ours —"):
            block = "upper"
            continue
        if st.startswith("the original"):
            block = "lower"
            continue
        if block is None:
            continue
        toks = [t for (_s, _e, t) in tokens(line)]
        nums = [t for t in toks if re.fullmatch(r"-?\d+(?:\.\d+)?", t)]
        label = norm(" ".join(toks[: len(toks) - len(nums)]))
        if len(nums) != 8:
            break
        t1_rows[(block, label)] = nums

    assert len(t1_rows) == 12, "Table 1: expected 12 data rows, got %d" % len(t1_rows)

    # ---- Table 4: two columns, right-aligned.
    t4_hdr = None
    for i, line in enumerate(lines):
        if "EditJumps (Ours)" in line and "EvoFlows (Published)" in line:
            t4_hdr = i
            break
    assert t4_hdr is not None, "Table 4 header not found"
    t4_data = []
    for line in lines[t4_hdr + 1:]:
        if not line.strip():
            if t4_data:
                break
            continue
        fs = fields(line)
        if len(fs) != 3:
            break
        t4_data.append((squash(fs[0][2]), fs[1:]))
    assert len(t4_data) == 4, "Table 4: expected 4 rows, got %d" % len(t4_data)
    w4 = cluster_right_edges([d[1] for d in t4_data], 2)
    t4_rows = {label: assign_by_right_edge(fs, w4) for label, fs in t4_data}

    return {
        "t1": (t1_order, t1_rows),
        "t2": (t2_order_pdf, t2_rows),
        "t4": (["EditJumps (Ours)", "EvoFlows (Published)"], t4_rows),
    }, t2_hdr_tokens


# ---------------------------------------------------------------- html layer


def html_grid(src, tid):
    m = re.search(r'<table[^>]*id="%s"[^>]*>' % re.escape(tid), src)
    start = m.end()
    body = src[start: src.index("</table>", start)]
    # LaTeXML repeats every formula as its LaTeX source inside <annotation>.
    body = re.sub(r"<annotation\b[^>]*>.*?</annotation>", " ", body, flags=re.S)
    rows = []
    for rm in re.finditer(r"<tr\b[^>]*>(.*?)</tr>", rm_body(body), re.S):
        cells = []
        for cm in re.finditer(r"<t([dh])\b([^>]*)>(.*?)</t\1>", rm.group(1), re.S):
            text = htmlmod.unescape(re.sub(r"<[^>]+>", " ", cm.group(3)))
            cs = re.search(r'colspan="(\d+)"', cm.group(2))
            cells.append((norm(text), int(cs.group(1)) if cs else 1))
        rows.append(cells)
    return rows


def rm_body(body):
    return body


def html_tables(path):
    src = open(path, encoding="utf-8").read()

    # Table 1
    g = html_grid(src, "S3.T1.2.1")
    metrics = [c for c, _ in g[0][1:]]
    metrics = [re.sub(r"\s*\\?downarrow.*$", "", m).replace("↓", "").strip() for m in metrics]
    metrics = [re.sub(r"\\times 10\^\{3\}", "", m).strip() for m in metrics]
    subs = [c for c, _ in g[1][1:]]
    t1_order = [(metrics[i // 2], subs[i]) for i in range(8)]
    t1_rows, block = {}, None
    for row in g[2:]:
        if len(row) == 1 and row[0][1] > 1:
            block = "upper" if row[0][0].startswith("ours") else "lower"
            continue
        t1_rows[(block, norm(row[0][0]))] = [normval(c) for c, _ in row[1:]]

    # Table 2
    g = html_grid(src, "A1.T2.5")
    t2_order = []
    for c, _ in g[0][1:]:
        c = re.sub(r"\\times 10\^\{\d\}", "", c)
        c = c.replace("× 10 3", "").replace("× 10 2", "")
        c = norm(c.replace("\\Delta", ""))
        t2_order.append(c.replace("Δ H", "ΔH"))
    t2_rows, block = {}, None
    for row in g[1:]:
        if len(row) == 1 and row[0][1] > 1:
            block = row[0][0]
            continue
        if not row or row[0][0] == "":
            continue
        t2_rows[(block, norm(row[0][0]))] = [normval(c) for c, _ in row[1:]]

    # Table 4
    g = html_grid(src, "A5.T4.8")
    t4_order = [norm(c) for c, _ in g[0][1:]]
    t4_rows = {}
    for row in g[1:]:
        t4_rows[squash(row[0][0])] = [normval(c) for c, _ in row[1:]]

    return {"t1": (t1_order, t1_rows), "t2": (t2_order, t2_rows), "t4": (t4_order, t4_rows)}


# ---------------------------------------------------------------- locators

LOC_T2 = re.compile(r'^Table 2, family block "([^"]+)", row "([^"]+)", column "([^"]+)"$')
LOC_T1 = re.compile(
    r'^Table 1, (upper|lower) block, row "([^"]+)", column "([^"]+)", sub-column "([^"]+)"$'
)
LOC_T4 = re.compile(r'^Table 4, row "([^"]+)", column "([^"]+)"$')


def lookup(model, loc):
    """Return the value the model holds at the column the locator names."""
    m = LOC_T2.match(loc)
    if m:
        block, row, col = m.group(1), norm(m.group(2)), norm(m.group(3))
        order, rows = model["t2"]
        if col not in order:
            return ("no-such-column", col, order)
        return ("ok", rows[(block, row)][order.index(col)])
    m = LOC_T1.match(loc)
    if m:
        block, row = m.group(1), norm(m.group(2))
        key = (norm(m.group(3)).replace("×103", "").strip(), norm(m.group(4)))
        order, rows = model["t1"]
        norm_order = [(re.sub(r"×\s*10\s*3", "", a).strip(), b) for a, b in order]
        if key not in norm_order:
            return ("no-such-column", key, norm_order)
        return ("ok", rows[(block, row)][norm_order.index(key)])
    m = LOC_T4.match(loc)
    if m:
        row, col = squash(m.group(1)), norm(m.group(2))
        order, rows = model["t4"]
        if col not in order:
            return ("no-such-column", col, order)
        return ("ok", rows[row][order.index(col)])
    return ("unparsed-locator", loc, None)


# ---------------------------------------------------------------- controls


def mutate(model, kind):
    """Return a deep copy of the model with one deliberate column error."""
    out = {}
    for t, (order, rows) in model.items():
        out[t] = (list(order), {k: list(v) for k, v in rows.items()})
    if kind == "swap-adjacent-columns":
        order, rows = out["t2"]
        i, j = order.index("KL pos."), order.index("KL pool.")
        r = rows[("ty1", "EditJumps")]
        r[i], r[j] = r[j], r[i]
    elif kind == "shift-row-left":
        order, rows = out["t2"]
        r = rows[("her2vh", "Evotune")]
        rows[("her2vh", "Evotune")] = r[1:] + [r[0]]
    elif kind == "swap-sub-columns":
        order, rows = out["t1"]
        r = rows[("lower", "EvoFlows")]
        r[2], r[3] = r[3], r[2]
    elif kind == "swap-blocks":
        order, rows = out["t1"]
        a = rows[("upper", "EvoDiff-MSA")]
        b = rows[("lower", "EvoDiff-MSA")]
        rows[("upper", "EvoDiff-MSA")], rows[("lower", "EvoDiff-MSA")] = b, a
    else:
        raise ValueError(kind)
    return out


# ---------------------------------------------------------------- main


def compare(results, model, label):
    bad, unparsed = [], []
    for rid, printed, loc in results:
        status, got = lookup(model, loc)[0], lookup(model, loc)[1]
        if status == "unparsed-locator":
            unparsed.append((rid, loc))
            continue
        if status != "ok":
            bad.append((rid, loc, "column not in %s header: %r" % (label, got)))
            continue
        if normval(got) != normval(printed):
            bad.append((rid, loc, "%s holds %r, record prints %r" % (label, got, printed)))
    return bad, unparsed


def main():
    layout, htmlpath, batch = sys.argv[1], sys.argv[2], sys.argv[3]
    pdf, t2_hdr_tokens = pdf_tables(layout)
    web = html_tables(htmlpath)

    # Table 2's printed headings run together, so the PDF fixes the column
    # ORDER and the markup supplies the names. Check the order here: the first
    # word of each heading must appear in the printed heading lines with
    # strictly increasing start positions, in the markup's column order.
    hdr_order_problem = []
    pos = -1
    for name in web["t2"][0]:
        first = norm(name).split()[0]
        hits = [s0 for (s0, _e, t) in t2_hdr_tokens if norm(t) == first and s0 > pos]
        if not hits:
            hdr_order_problem.append("heading %r not printed after column %d" % (name, pos))
            continue
        pos = min(hits)
    pdf["t2"] = (list(web["t2"][0]), pdf["t2"][1])

    # the two models must agree with each other before either is used
    cross = []
    for t in ("t1", "t2", "t4"):
        po, pr = pdf[t]
        ho, hr = web[t]
        for key in sorted(set(pr) | set(hr), key=str):
            if key not in pr or key not in hr:
                cross.append("%s row %r in only one model" % (t, key))
                continue
            for i, (a, b) in enumerate(zip(pr[key], hr[key])):
                if normval(a) != normval(b) and not (isdash(a) and isdash(b)):
                    cross.append("%s %r col %d: pdf %r html %r" % (t, key, i, a, b))

    results = []
    for line in open(batch, encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") != "result":
            continue
        a = r["attributes"]
        results.append((r["id"], a["printed_value"], a["source_locator"]))

    bad_pdf, unparsed = compare(results, pdf, "pdf")
    bad_html, _ = compare(results, web, "html")

    print("results in batch:            %d" % len(results))
    print("locators this check parses:  %d" % (len(results) - len(unparsed)))
    print("not a table locator:         %d" % len(unparsed))
    for p in hdr_order_problem:
        cross.append("t2 printed heading order: " + p)
    print("pdf vs html grid differences: %d" % len(cross))
    for c in cross:
        print("  CROSS", c)
    print("mismatches against pdf columns:  %d" % len(bad_pdf))
    for b in bad_pdf:
        print("  PDF ", b)
    print("mismatches against html columns: %d" % len(bad_html))
    for b in bad_html:
        print("  HTML", b)
    for rid, loc in unparsed:
        print("  SKIP", rid, "|", loc)

    print("\nnegative controls (each must be rejected):")
    ok = True
    for kind in (
        "swap-adjacent-columns",
        "shift-row-left",
        "swap-sub-columns",
        "swap-blocks",
    ):
        for name, model in (("pdf", pdf), ("html", web)):
            bad, _ = compare(results, mutate(model, kind), name)
            verdict = "rejected (%d mismatches)" % len(bad) if bad else "NOT REJECTED"
            if not bad:
                ok = False
            print("  %-24s %-5s %s" % (kind, name, verdict))

    failed = bool(cross or bad_pdf or bad_html) or not ok
    print("\nVERDICT:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
