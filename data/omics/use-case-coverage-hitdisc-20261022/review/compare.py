"""Independent check of every result in the hit-discovery batch against the pinned sources.

Builds its own reference grids (myparse_shen.py for the JATS tables, myparse_xlsx.py for sheet S8,
plain text search for the Kim et al. body-text values), then compares each result record's
printed_value, numeric_value and locator against the reference. Reports every mismatch.
"""

import os

# Paths are configurable so the review can be rerun anywhere.
SOURCES_ROOT = os.environ.get("HITDISC_SOURCES", "sources")
BATCH_DIR = os.environ.get("HITDISC_BATCH_DIR", "data/omics/use-case-coverage-hitdisc-20261022")
import json
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myparse_shen
import myparse_xlsx

SCR = SOURCES_ROOT
BATCH = os.path.join(BATCH_DIR, "batch.jsonl")


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("_{", "").replace("^{", "").replace("}", "")
    s = s.replace("α", "a").replace(" ", "").replace(" ", "")
    s = re.sub(r"[\s'\"()_]", "", s).lower()
    return s


def strip_fn(label):
    """Drop a trailing single-letter footnote marker from a row label."""
    m = re.match(r"^(.*?)([a-f])$", label)
    return m.group(1) if m else label


# ---------------------------------------------------------------- Shen tables
shen = myparse_shen.parse(SOURCES_ROOT + "/PMC12704515.xml")

# Table 1 / 3: flat row label -> {column -> value}
def flat_table(lab):
    d = shen[lab]
    cols = d["cols"][1:]
    out = {}
    for rowlabel, vals in d["rows"]:
        if not vals:
            continue
        assert len(vals) == len(cols), (lab, rowlabel, len(vals), len(cols))
        out[norm(rowlabel)] = dict(zip([norm(c) for c in cols], vals))
        out[norm(strip_fn(rowlabel))] = out[norm(rowlabel)]
    return out, [norm(c) for c in cols]


T1, T1COLS = flat_table("Table 1")
T3, T3COLS = flat_table("Table 3")
T4, T4COLS = flat_table("Table 4")

# Table 2 is two blocks headed 'Protenix' and 'AF3'
T2 = {}
_blk = None
_t2cols = [norm(c) for c in shen["Table 2"]["cols"][1:]]
for rowlabel, vals in shen["Table 2"]["rows"]:
    if not vals:
        if rowlabel.strip():
            _blk = norm(rowlabel)
        continue
    assert len(vals) == len(_t2cols)
    T2[(_blk, norm(rowlabel))] = dict(zip(_t2cols, vals))

# Table 5: method column spans two sample-count rows
T5 = {}
_t5cols = [norm(c) for c in shen["Table 5"]["cols"][2:]]  # drop Method and Number of samples
_method = None
for rowlabel, vals in shen["Table 5"]["rows"]:
    if rowlabel in ("1", "5"):          # continuation row: sample count in the label slot
        nsamp, cells = rowlabel, vals
        meth = _method
        cont = True
    else:
        _method = rowlabel
        meth = rowlabel
        nsamp, cells = vals[0], vals[1:]
        cont = False
    assert len(cells) == len(_t5cols), (rowlabel, len(cells), len(_t5cols))
    T5[(norm(meth), nsamp, cont)] = dict(zip(_t5cols, cells))

# ---------------------------------------------------------------- sheet S8
s8 = myparse_xlsx.read_sheet(SOURCES_ROOT + "/supp/ci5c02441_si_002.xlsx", "S8")
s8rows = {}
s8hdr = {}
for ref, d in s8.items():
    m = re.match(r"([A-Z]+)(\d+)$", ref)
    col, rn = m.group(1), int(m.group(2))
    if rn == 1:
        s8hdr[col] = d["raw"]
    else:
        s8rows.setdefault(rn, {})[col] = d
BY_WF = {}
for rn, cells in s8rows.items():
    wf = cells.get("B")
    if wf is None:
        continue
    BY_WF[str(int(float(wf["raw"])))] = cells

# ---------------------------------------------------------------- Kim body text
kim_raw = open(SOURCES_ROOT + "/PMC13657626.xml", encoding="utf-8").read()
kim_text = re.sub(r"<[^>]+>", "", kim_raw)
kim_text = unicodedata.normalize("NFKC", kim_text)
kim_text = re.sub(r"\s+", " ", kim_text)
assert "<table-wrap" not in kim_raw, "Kim XML unexpectedly contains a table-wrap"

# ---------------------------------------------------------------- compare
recs = [json.loads(l) for l in open(BATCH)]
results = [r for r in recs if r["kind"] == "result"]
problems = []
checked = 0
rows_out = []


def record(rid, where, printed, ref, ok, note=""):
    global checked
    checked += 1
    rows_out.append({"id": rid, "where": where, "printed": printed, "reference": ref,
                     "ok": ok, "note": note})
    if not ok:
        problems.append((rid, where, printed, ref, note))


for r in results:
    a = r["attributes"]
    loc = a["source_locator"]
    pv = a["printed_value"]
    tbl = a.get("source_table")
    if tbl in ("Table 1", "Table 3"):
        m = re.match(r"Table (1|3), row '(.+)', column '(.+)' \((Mean|Med)\)$", loc)
        if not m:
            record(r["id"], loc, pv, None, False, "locator did not parse")
            continue
        src = T1 if m.group(1) == "1" else T3
        key = norm(m.group(2))
        col = norm(m.group(3) + m.group(4))
        ref = src.get(key, {}).get(col)
        record(r["id"], loc, pv, ref, ref is not None and ref == pv)
    elif tbl == "Table 2":
        m = re.match(r"Table 2, (Protenix|AF3) block, row '(.+)', column '(.+)' \((Mean|Med)\)$", loc)
        if not m:
            record(r["id"], loc, pv, None, False, "locator did not parse")
            continue
        ref = T2.get((norm(m.group(1)), norm(m.group(2))), {}).get(norm(m.group(3) + m.group(4)))
        record(r["id"], loc, pv, ref, ref is not None and ref == pv)
    elif tbl == "Table 4":
        m = re.match(r"Table 4, row '(.+)', column '(.+)' \((EF1%|NEF1%)\)$", loc)
        if not m:
            record(r["id"], loc, pv, None, False, "locator did not parse")
            continue
        ref = T4.get(norm(m.group(1)), {}).get(norm(m.group(2) + m.group(3)))
        record(r["id"], loc, pv, ref, ref is not None and ref == pv)
    elif tbl == "Table 5":
        m = re.match(r"Table 5, row '(.+)' \(Number of samples = (1|5)\), column '(.+)'$", loc)
        if not m:
            record(r["id"], loc, pv, None, False, "locator did not parse")
            continue
        rowlab, nsamp, colname = m.group(1), m.group(2), m.group(3)
        cont = rowlab.startswith("(row continued")
        if cont:
            # continuation row: identify the method from the evaluation it hangs off
            ev = next(x for x in recs if x["id"] == r["links"][0]["target_id"])
            cfg = next(x for x in recs
                       if x["id"] == next(l["target_id"] for l in ev["links"]
                                          if l["relation"] == "system"))
            meth = cfg["attributes"]["reported_name"]
            meth = re.sub(r"\s*\(.*", "", meth)
        else:
            meth = rowlab
        cand = [v for (mm, ns, cc), v in T5.items()
                if ns == nsamp and cc == cont and norm(mm) == norm(meth)]
        ref = cand[0].get(norm(colname)) if len(cand) == 1 else None
        record(r["id"], loc, pv, ref, ref is not None and ref == pv,
               "" if ref is not None else f"no unique T5 row for {meth!r} n={nsamp} cont={cont}")
    elif tbl == "Table S8":
        m = re.match(r"Sheet 'S8', row with Workflow = (\d+), column ([A-T]) \('(.*)'\)$", loc)
        if not m:
            m2 = re.match(r"Sheet 'S8', row with Workflow = (\d+), column ([A-T])\b.*$", loc)
            if not m2:
                record(r["id"], loc, pv, None, False, "locator did not parse")
                continue
            wf, col, hdr = m2.group(1), m2.group(2), None
        else:
            wf, col, hdr = m.group(1), m.group(2), m.group(3)
        cell = BY_WF.get(wf, {}).get(col)
        if cell is None:
            record(r["id"], loc, pv, None, False, "cell absent from sheet S8")
            continue
        ok = cell["round"] == pv and a.get("raw_xml_value") == cell["raw"]
        note = ""
        hdr_expected = s8hdr.get(col)
        if hdr == "(unnamed final column)" and hdr_expected is None:
            hdr = None
        if hdr is not None and norm(hdr) != norm(hdr_expected or ""):
            ok = False
            note = f"header mismatch: locator says {hdr!r}, sheet says {hdr_expected!r}"
        record(r["id"], loc, pv, cell["round"], ok, note)
    elif r["source_ids"] == ["hitdisc-20261022-source-kim2026"]:
        m = re.search(r"printed in the body text as '(.+)'$", loc)
        if not m:
            record(r["id"], loc, pv, None, False, "locator did not parse")
            continue
        printed_string = unicodedata.normalize("NFKC", m.group(1))
        present = printed_string in kim_text
        # the numeric part must equal printed_value
        num = re.search(r"[\d.]+", printed_string).group(0)
        record(r["id"], loc, pv, printed_string if present else None,
               present and (num == pv or printed_string == pv),
               "" if present else "printed string not found in pinned body text")
    else:
        record(r["id"], loc, pv, None, False, "unclassified result")

print(f"results checked: {checked}")
print(f"mismatches: {len(problems)}")
for p in problems[:60]:
    print("  MISMATCH", p)

json.dump(rows_out, open(SCR + "/compare_rows.json", "w"), indent=0)

# ---- numeric_value consistency
numprob = []
for r in results:
    a = r["attributes"]
    pv, nv = a["printed_value"], a.get("numeric_value")
    if nv is None:
        numprob.append((r["id"], "numeric_value null", pv))
        continue
    pvnum = re.search(r"-?[\d.]+", pv)
    pvnum = pvnum.group(0) if pvnum else pv
    try:
        if float(nv) != float(pvnum):
            numprob.append((r["id"], "numeric != printed", pv, nv))
    except ValueError:
        numprob.append((r["id"], "unparseable", pv, nv))
    else:
        pass
print(f"numeric_value problems: {len(numprob)}")
for p in numprob[:20]:
    print("  ", p)
