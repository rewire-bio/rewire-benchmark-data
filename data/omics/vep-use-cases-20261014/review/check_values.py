"""Independent value check for vep-use-cases-20261014 (review, 2026-10-14).

Usage: python3 -I review/check_values.py <download-dir> [<batch.jsonl>]

<download-dir> holds the re-downloaded artifacts named by source record ID:
  vep-uc-20261014-source-pejaver2022  (Europe PMC fullTextXML for PMC9748256)
  vep-uc-20261014-source-bergquist2025  (PMC article page for PMC12208618)

Written by the reviewer; it does not import or copy extract/build_batch.py or extract/pmc_html.py.
Pejaver et al. 2022 Tables 2 and 3 are read with ElementTree from the table-wrap elements tbl2 and
tbl3; Bergquist et al. 2025 Table 1 with html.parser from the page's only <table>. Header rows and
row labels are asserted. For every cell it derives the expected result independently:

- printed_value: the cell text, whitespace-trimmed.
- numeric_value: None for a not-reached cell and the indeterminate range; the operand of a one-sided
  cell; for a two-sided interval, the end on the weaker side. The weaker side is found from the
  tool's score orientation (pathogenic-high or pathogenic-low), read from the row's one-sided cells:
  a PP3 interval's weaker end is its lower end for a pathogenic-high tool, its upper end otherwise;
  a BP4 interval the opposite. (The extractor instead compares with the next-stronger cell.)
- metric, unit, unit_detail, metric_direction, metric_qualifier, source_locator, the evaluation's
  configuration (reported_name equals the row label), protocol and dataset, and the uncertainty
  object or its missing reason.

It also checks that every cell has exactly one result and that claims.csv agrees with the batch.
Exit status 1 if any check fails.
"""
import csv
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

BATCH_DIR = Path(__file__).resolve().parent.parent
P = "vep-uc-20261014-"
PEJ = P + "source-pejaver2022"
BERG = P + "source-bergquist2025"
PEJ_SHA = "a78c7bcaacb0ccb72291264bbe7c1f9a16867b0c6207dcbb45c3c59a14af6b3b"
BERG_SHA = "4fe954451167b5a5717a4c37f4054432e1f02fb59862d0fb909edb525e6bb8e2"

PEJ_ROWS = ["BayesDel", "CADD", "EA", "FATHMM", "GERP++", "MPC", "MutPred2", "PhyloP",
            "PolyPhen2", "PrimateAI", "REVEL", "SIFT", "VEST4"]
PEJ_COLS = [("BP4", "Very Strong"), ("BP4", "Strong"), ("BP4", "Moderate"), ("BP4", "Supporting"),
            ("PP3", "Supporting"), ("PP3", "Moderate"), ("PP3", "Strong"), ("PP3", "Very Strong")]
BERG_ROWS = ["BayesDel", "MutPred2", "REVEL", "VEST4", "AlphaMissense", "ESM1b", "VARITY_R"]
BERG_HEAD = ["Strong (−4)", "(−3)", "Moderate (−2)", "Supporting (−1)", "Indeterminate (0)",
             "Supporting (+1)", "Moderate (+2)", "(+3)", "Strong (+4)"]
BERG_QUAL = ["BP4 Strong", "BP4 3 points", "BP4 Moderate", "BP4 Supporting", "Indeterminate (0 points)",
             "PP3 Supporting", "PP3 Moderate", "PP3 3 points", "PP3 Strong"]
T3_ROWS = ["SIFT", "PolyPhen-2", "CADD"]
T3_CONFIG = {"SIFT": "sift", "PolyPhen-2": "polyphen2", "CADD": "cadd"}

errors = []


def fail(msg):
    errors.append(msg)


def text(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def dec(s):
    return s.replace("−", "-").strip()


def orientation(cells, sides):
    """'high' if higher scores are pathogenic, from the row's one-sided cells."""
    votes = set()
    for c, side in zip(cells, sides):
        if c.startswith("≥"):
            votes.add("high" if side == "PP3" else "low")
        elif c.startswith("≤"):
            votes.add("low" if side == "PP3" else "high")
    if len(votes) != 1:
        raise SystemExit(f"cannot determine orientation from {cells}")
    return votes.pop()


def expected_numeric(cell, side, orient):
    if cell in ("–", "-") or side == "0":
        return None, "none"
    if cell[0] in "≤≥":
        return dec(cell[1:]), "one-sided"
    m = re.fullmatch(r"([\[(])\s*(\S+),\s*(\S+)\s*([\])])", cell)
    if not m:
        return dec(cell), "single"
    lo, hi = dec(m.group(2)), dec(m.group(3))
    assert Decimal(lo) < Decimal(hi), cell
    weak_low = (side == "PP3") == (orient == "high")
    return (lo if weak_low else hi), "two-sided"


def pejaver_tables(path):
    root = ET.parse(path).getroot()
    tw = {t.get("id"): t for t in root.iter("table-wrap")}
    t2, t3 = tw["tbl2"], tw["tbl3"]
    assert text(t2.find("label")) == "Table 2" and text(t3.find("label")) == "Table 3"
    rows2 = [[text(c) for c in tr] for tr in t2.iter("tr")]
    assert rows2[0] == ["Method", "Benign (BP4)", "Pathogenic (PP3)"], rows2[0]
    assert rows2[1] == [s for _, s in PEJ_COLS], rows2[1]
    body2 = rows2[2:]
    assert [r[0] for r in body2] == PEJ_ROWS, [r[0] for r in body2]
    assert all(len(r) == 9 for r in body2)
    foot = text(t2.find("table-wrap-foot"))
    assert foot.startswith("A “–” implies that the given tool did not meet"), foot
    rows3 = [[text(c) for c in tr] for tr in t3.iter("tr")]
    assert rows3[0] == ["Method", "Pathogenicity score threshold", "lr+", "Evidence strength",
                        "Fraction of predicted pathogenic variants in the gnomAD set"], rows3[0]
    assert [r[0] for r in rows3[1:]] == T3_ROWS
    return body2, rows3[1:]


class Table(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.rows = []
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.depth += 1
        if self.depth and tag == "tr":
            self.rows.append([])
        if self.depth and tag in ("td", "th"):
            self.cell = ""

    def handle_endtag(self, tag):
        if tag == "table":
            self.depth -= 1
        if self.depth and tag in ("td", "th") and self.cell is not None:
            self.rows[-1].append(re.sub(r"\s+", " ", self.cell).strip())
            self.cell = None

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data


def bergquist_table(path):
    page = Path(path).read_text(encoding="utf-8")
    assert page.count("<table") == 1
    assert "All methods calibrated in this study are indicated in bold." in page
    p = Table()
    p.feed(page)
    assert p.rows[0] == ["Method", "Benign (BP4)", "Indeterminate (0)", "Pathogenic (PP3)"], p.rows[0]
    assert p.rows[1] == [h for h in BERG_HEAD if h != "Indeterminate (0)"], p.rows[1]
    body = p.rows[2:]
    assert [r[0] for r in body] == BERG_ROWS, [r[0] for r in body]
    assert all(len(r) == 10 for r in body)
    return body


def main():
    dl = Path(sys.argv[1])
    batch = Path(sys.argv[2]) if len(sys.argv) > 2 else BATCH_DIR / "batch.jsonl"
    for sid, sha in ((PEJ, PEJ_SHA), (BERG, BERG_SHA)):
        b = (dl / sid).read_bytes()
        if sid == BERG:
            b = re.sub(rb'(<meta name="ncbi_phid" content=")[^"]*"', rb'\1"', b)
            b = re.sub(rb'(name="csrfmiddlewaretoken" value=")[^"]*"', rb'\1"', b)
        assert hashlib.sha256(b).hexdigest() == sha, sid

    recs = [json.loads(l) for l in batch.open()]
    by = {r["id"]: r for r in recs}
    results = [r for r in recs if r["kind"] == "result"]
    seen = {}

    def ev_of(r):
        ids = [l["target_id"] for l in r["links"] if l["relation"] == "evaluation"]
        assert len(ids) == 1
        return by[ids[0]]

    def link(rec, rel):
        ids = [l["target_id"] for l in rec["links"] if l["relation"] == rel]
        assert len(ids) == 1, (rec["id"], rel)
        return ids[0]

    def find(locator, source):
        hits = [r for r in results if r["attributes"]["source_locator"] == locator and r["source_ids"] == [source]]
        if len(hits) != 1:
            fail(f"{locator}: {len(hits)} results")
            return None
        seen[hits[0]["id"]] = seen.get(hits[0]["id"], 0) + 1
        return hits[0]

    def check(r, field, want):
        got = r["attributes"].get(field)
        if got != want:
            fail(f"{r['id']}: {field} {got!r} != {want!r}")

    def check_eval(r, label, protocol, dataset, origin=None):
        ev = ev_of(r)
        cfg = by.get(link(ev, "system"))
        if not cfg or cfg["attributes"].get("reported_name") != label:
            fail(f"{r['id']}: configuration {cfg and cfg['attributes'].get('reported_name')!r} != {label!r}")
        if link(ev, "assessment") != protocol:
            fail(f"{r['id']}: protocol {link(ev, 'assessment')}")
        if link(ev, "data") != dataset:
            fail(f"{r['id']}: dataset {link(ev, 'data')}")
        if ev["attributes"]["protocol"] != protocol or ev["attributes"]["comparison"]["protocol_id"] != protocol:
            fail(f"{ev['id']}: protocol attribute")

    body2, body3 = pejaver_tables(dl / PEJ)
    clinvar = P + "dataset-pejaver2022-clinvar2019"
    for row in body2:
        label, cells = row[0], row[1:]
        orient = orientation(cells, [s for s, _ in PEJ_COLS])
        for cell, (side, strength) in zip(cells, PEJ_COLS):
            col = f"{'Benign (BP4)' if side == 'BP4' else 'Pathogenic (PP3)'}: {strength}"
            r = find(f"Table 2, row '{label}', column '{col}'", PEJ)
            if not r:
                continue
            num, shape = expected_numeric(cell, side, orient)
            check(r, "printed_value", cell)
            check(r, "numeric_value", num)
            check(r, "metric", "evidence-strength-score-interval")
            check(r, "unit", "unitless")
            check(r, "unit_detail", f"{label} score")
            check(r, "metric_direction", "unknown")
            check(r, "metric_qualifier", f"{side} {strength}, ClinGen SVI calibration (Pejaver et al. 2022)")
            want_missing = ({"uncertainty": {"reason": "inapplicable", "note": "Strength not reached"}}
                            if num is None else
                            {"uncertainty": {"reason": "unextracted", "note": "One-sided confidence intervals are in Table S1, not retrieved"}})
            check(r, "missing_metadata", want_missing)
            if "uncertainty" in r["attributes"]:
                fail(f"{r['id']}: unexpected uncertainty")
            check_eval(r, label, P + "protocol-pejaver2022-intervals", clinvar)

    for row in body3:
        label, threshold, lr, strength, frac = row
        m = re.fullmatch(r"(\S+) \((\S+), (\S+)\)", lr)
        assert m and strength == "not met"
        cfg_label = "PolyPhen2" if label == "PolyPhen-2" else label
        r = find(f"Table 3, row '{label}', column 'lr +'", PEJ)
        if r:
            check(r, "printed_value", m.group(1))
            check(r, "numeric_value", m.group(1))
            check(r, "printed_source_cell", lr)
            check(r, "metric", "likelihood-ratio")
            check(r, "unit", "unitless")
            check(r, "metric_direction", "higher")
            check(r, "metric_qualifier", f"local positive likelihood ratio at the developer threshold ({threshold}), PP3 Supporting requires 2.406")
            check(r, "criterion", f"Evidence strength column: '{strength}'")
            u = r["attributes"].get("uncertainty", {})
            if (u.get("type"), u.get("level"), u.get("lower"), u.get("upper"), u.get("printed")) != (
                    "confidence_interval", 0.95, m.group(2), m.group(3), f"({m.group(2)}, {m.group(3)})"):
                fail(f"{r['id']}: uncertainty {u}")
            check_eval(r, cfg_label, P + "protocol-pejaver2022-developer-threshold-lr", clinvar)
        r = find(f"Table 3, row '{label}', column 'Fraction of predicted pathogenic variants in the gnomAD set'", PEJ)
        if r:
            check(r, "printed_value", frac)
            check(r, "numeric_value", frac)
            check(r, "metric", "proportion")
            check(r, "unit", "fraction")
            check(r, "metric_direction", "unknown")  # set in review; the extractor had "lower"
            check(r, "denominator", 363894)
            check(r, "metric_qualifier", "gnomAD-set variants predicted pathogenic at the developer threshold")
            check_eval(r, cfg_label, P + "protocol-pejaver2022-developer-threshold-gnomad-fraction",
                       P + "dataset-pejaver2022-gnomad")

    body1 = bergquist_table(dl / BERG)
    sides = ["BP4"] * 4 + ["0"] + ["PP3"] * 4
    for row in body1:
        label, cells = row[0], row[1:]
        orient = orientation(cells, sides)
        for cell, side, head, qual in zip(cells, sides, BERG_HEAD, BERG_QUAL):
            r = find(f"Table 1, row '{label}', column '{head}'", BERG)
            if not r:
                continue
            num, shape = expected_numeric(cell, side, orient)
            check(r, "printed_value", cell)
            check(r, "numeric_value", num)
            check(r, "metric", "evidence-strength-score-interval")
            check(r, "unit", "unitless")
            check(r, "unit_detail", f"{label} score")
            check(r, "metric_direction", "unknown")
            check(r, "metric_qualifier", f"{qual}, ClinGen SVI calibration, points scale (Bergquist et al. 2025)")
            unc = r["attributes"].get("missing_metadata", {}).get("uncertainty", {}).get("reason")
            want = "inapplicable" if cell == "-" else ("unextracted", "unreported")
            if (unc not in want) if isinstance(want, tuple) else (unc != want):
                fail(f"{r['id']}: uncertainty reason {unc}")
            check_eval(r, label, P + "protocol-bergquist2025-point-intervals", clinvar)

    n_cells = 13 * 8 + 3 * 2 + 7 * 9
    for rid in (r["id"] for r in results):
        if seen.get(rid) != 1:
            fail(f"{rid}: matched {seen.get(rid, 0)} cells")
    if len(results) != n_cells:
        fail(f"{len(results)} results for {n_cells} cells")

    with (BATCH_DIR / "claims.csv").open() as f:
        rows = {row["record_id"]: row for row in csv.DictReader(f)}
    for r in results:
        row = rows.get(r["id"])
        if not row or row["printed_value"] != r["attributes"]["printed_value"] or r["source_ids"][0] not in row["source_id"]:
            fail(f"{r['id']}: claims.csv disagrees")

    print(f"{len(results)} results checked against {n_cells} source cells; {len(errors)} errors")
    for e in errors:
        print("  " + e)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
