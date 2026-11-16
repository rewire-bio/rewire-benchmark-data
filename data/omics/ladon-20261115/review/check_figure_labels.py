#!/usr/bin/env python3
"""Independent re-read of the 101 printed figure labels stored by the Ladon batch.

Written for the review pass. It does not use anything in extract/: where the
extractor read the `pdftotext -layout` text layer line by line and placed
Figure 2's cells by character offset, this script reads the word-level geometry
of `pdftotext -bbox-layout` and places every cell by its x and y coordinates.
Column and panel assignment therefore comes from where the label is printed on
the page, not from how many spaces precede it.

What it checks for each of the 101 results:

  1. the page its `source_locator` names holds the printed value,
  2. the value sits in the row whose label the locator names (y overlap),
  3. for multi-column figures, the value sits in the column or panel the
     locator names (x cluster, ordered by the printed column headers),
  4. a printed interval matches the result's `uncertainty` bounds,
  5. three arithmetic constraints that the figures imply (below).

Usage:
  python3 check_figure_labels.py <ladon.pdf> <batch.jsonl>

It shells out to `pdftotext -bbox-layout` itself, so the only input is the PDF
whose SHA-256 the source record pins.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

PDF_SHA256 = "64edf7c3c956c50a65aa01a0dcaa13f0cfef28ab4373ecfd50c431e67143893c"


@dataclass(frozen=True)
class Word:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def xc(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def yc(self) -> float:
        return (self.y0 + self.y1) / 2


def unescape(text: str) -> str:
    for src, dst in (
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&quot;", '"'),
        ("&apos;", "'"),
    ):
        text = text.replace(src, dst)
    return text


def read_pages(pdf: Path) -> list[list[Word]]:
    """One list of words per page, from the bbox-layout text layer."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "bbox.xml"
        subprocess.run(
            ["pdftotext", "-bbox-layout", str(pdf), str(out)],
            check=True,
            capture_output=True,
        )
        xml = out.read_text(encoding="utf-8", errors="replace")
    pages = []
    for page in re.findall(r"<page\b.*?</page>", xml, re.S):
        words = []
        for attrs, text in re.findall(r"<word ([^>]*)>(.*?)</word>", page, re.S):
            a = dict(re.findall(r"(\w+)=\"([^\"]*)\"", attrs))
            words.append(
                Word(
                    unescape(text).strip(),
                    float(a["xMin"]),
                    float(a["yMin"]),
                    float(a["xMax"]),
                    float(a["yMax"]),
                )
            )
        pages.append(words)
    return pages


def footer_page_number(words: list[Word]) -> int | None:
    """The page number the running footer prints, read back as a cross-check."""
    text = " ".join(w.text for w in words if w.y0 > 740)
    m = re.search(r"Blank Bio . (\d+) / 47", text)
    return int(m.group(1)) if m else None


NUMBER = re.compile(r"^[0-9]+(?:\.[0-9]+)?%?$")


def numbers(
    words: list[Word], y: tuple[float, float], xmin: float = 0.0, xmax: float = 1e9
) -> list[Word]:
    """Numeric words whose vertical centre falls in the band, left to right."""
    lo, hi = y
    hits = [
        w
        for w in words
        if NUMBER.match(w.text) and lo <= w.yc <= hi and w.x0 >= xmin and w.xc <= xmax
    ]
    return sorted(hits, key=lambda w: w.x0)


def find_label(
    words: list[Word],
    label: str,
    y: tuple[float, float] | None = None,
    with_values: int | None = None,
    value_pad: float = 6.0,
    value_x: tuple[float, float] = (0.0, 1e9),
) -> Word:
    """The first word of a printed label, matched as consecutive words on a line.

    `with_values` skips occurrences that do not have that many numeric words to
    their right in the same horizontal band. Both Figure 2 and Figure 6 print
    "Ladon" twice: once as a section heading with no bar and once as a data row.
    """
    parts = label.split()
    candidates = [w for w in words if w.text == parts[0]]
    if y:
        candidates = [w for w in candidates if y[0] <= w.y0 <= y[1]]
    for first in sorted(candidates, key=lambda w: (w.y0, w.x0)):
        row = sorted(
            (w for w in words if abs(w.yc - first.yc) < 6 and w.x0 >= first.x0),
            key=lambda w: w.x0,
        )
        if [w.text for w in row[: len(parts)]] != parts:
            continue
        if with_values is not None:
            end = max(row[len(parts) - 1].x1, value_x[0])
            if len(numbers(words, band(first, value_pad), xmin=end, xmax=value_x[1])) != with_values:
                continue
        return first
    raise AssertionError(f"label not found: {label!r}")


def band(anchor: Word, pad: float = 6.0) -> tuple[float, float]:
    return (anchor.y0 - pad, anchor.y1 + pad)


class Checker:
    def __init__(self, pages: list[list[Word]], records: dict[str, dict]):
        self.pages = pages
        self.records = records
        self.rows: list[tuple[str, str, str, str]] = []
        self.failures = 0

    def page(self, printed_number: int) -> list[Word]:
        words = self.pages[printed_number - 1]
        assert footer_page_number(words) == printed_number, (
            f"page {printed_number}: footer says {footer_page_number(words)}"
        )
        return words

    def record(self, rid: str, status: str, found: str, note: str = "") -> None:
        if status != "ok":
            self.failures += 1
        self.rows.append((rid, status, found, note))

    def check(self, rid: str, found: str | None, note: str = "") -> None:
        """Compare what the geometry read with what the record stores."""
        rec = self.records.get(rid)
        if rec is None:
            self.record(rid, "no_such_result", found or "", note)
            return
        printed = rec["attributes"]["printed_value"]
        if found is None:
            self.record(rid, "not_found", "", note)
        elif found == printed:
            self.record(rid, "ok", found, note)
        else:
            self.record(rid, "DIFFERS", found, f"record prints {printed!r}. {note}".strip())

    def check_interval(self, rid: str, lower: str, upper: str) -> None:
        rec = self.records.get(rid)
        if rec is None:
            return
        unc = rec["attributes"].get("uncertainty")
        if not unc:
            self.record(f"{rid}#ci", "no_uncertainty_stored", f"[{lower}, {upper}]")
            return
        if (unc.get("lower"), unc.get("upper")) == (lower, upper):
            self.record(f"{rid}#ci", "ok", f"[{lower}, {upper}]")
        else:
            self.record(
                f"{rid}#ci",
                "DIFFERS",
                f"[{lower}, {upper}]",
                f"record stores [{unc.get('lower')}, {unc.get('upper')}]",
            )


# Row labels in the order each figure prints them, with the result ID stem the
# batch uses. Written from the printed figure, not from the extractor's spec.
FIG2_ROWS = [
    ("Ladon + clinical", "ladon-plus-clinical-covariates"),
    ("Ladon", "ladon"),
    ("Differential gene expression", "differential-gene-expression"),
    ("Hallmark GSEA", "hallmark-gsea"),
    ("Isoform TPM", "isoform-tpm"),
    ("Clinical covariates", "clinical-covariates-bmretriever"),
    ("BulkRNABert", "bulkrnabert"),
    ("BulkFormer", "bulkformer"),
]
FIG2_PANELS = ["tcga-to-cptac", "cptac-to-tcga", "pan-cancer"]

FIG3_ROWS = [
    ("Ladon + clinical", "ladon-plus-clinical-covariates"),
    ("Ladon", "ladon"),
    ("Differential gene", "differential-gene-expression"),
    ("TPM · matched TCGA", "tpm-matched-tcga"),
    ("Clinical covariates", "clinical-covariates-bmretriever"),
    ("BulkRNABert", "bulkrnabert"),
    ("BulkFormer", "bulkformer"),
]

FIG6_ROWS = [
    ("Ladon", "ladon"),
    ("Differential gene expression", "differential-gene-expression"),
    ("Gene TPM", "gene-tpm"),
    ("PD-L1 mRNA", "pd-l1-mrna"),
    ("T-effector", "t-effector-ifn-gamma"),
    ("IMPRES", "impres"),
    ("TIDE", "tide"),
    ("Clinical covariates", "clinical-covariates-bmretriever"),
    ("BulkRNABert", "bulkrnabert"),
    ("BulkFormer", "bulkformer"),
]

FIG12A_ROWS = [
    ("Ladon", "ladon"),
    ("Cohort-trained baseline", "cohort-trained-baseline"),
    ("Linear model on public data", "linear-model-on-public-data"),
    ("Nearest public samples", "nearest-public-samples"),
]

FIG13_ROWS = [
    ("Ladon", "ladon"),
    ("Organ average", "organ-average"),
    ("Nearest public", "nearest-public-samples"),
    ("Linear model", "linear-model-on-public-data"),
]

FIG17_ROWS = [
    ("EPIC", "epic"),
    ("ABIS", "abis"),
    ("BayesPrism", "bayesprism"),
    ("CIBERSORT", "cibersort"),
    ("DWLS", "dwls"),
    ("Ladon", "ladon"),
]
FIG17_COLUMNS = ["pearson", "ordering"]

FIG17_LINEAGES = [
    ("CD4 T", "cd4-t"),
    ("CD8 T", "cd8-t"),
    ("NK", "nk"),
    ("B/plasma", "b-plasma"),
    ("Monocyte", "monocyte"),
]

FIG18_BLOCKS = [
    ("ARTEMIS", "artemis-er-pos-her2-neg", [
        ("Ladon deconvolution", "ladon-deconvolution"),
        ("Oncotype DX*", "oncotype-dx"),
        ("MammaPrint*", "mammaprint"),
    ]),
    ("PBCP", "pbcp-er-pos-her2-neg", [
        ("Ladon deconvolution", "ladon-deconvolution"),
        ("Oncotype DX*", "oncotype-dx"),
        ("MammaPrint*", "mammaprint"),
    ]),
    ("PBCP", "pbcp-her2-pos", [
        ("Ladon deconvolution", "ladon-deconvolution"),
        ("HER2 expression", "her2-expression"),
    ]),
    ("DFCI IBC", "dfci-ibc-her2-pos", [
        ("Ladon deconvolution", "ladon-deconvolution"),
        ("HER2 expression", "her2-expression"),
    ]),
]


def cluster_x(values: list[float], tolerance: float = 40.0) -> list[float]:
    """Group x positions into columns, returning each column's mean, left to right."""
    columns: list[list[float]] = []
    for x in sorted(values):
        if columns and x - columns[-1][-1] <= tolerance:
            columns[-1].append(x)
        else:
            columns.append([x])
    return [sum(c) / len(c) for c in columns]


def main(pdf: Path, batch: Path) -> int:
    digest = subprocess.run(
        ["shasum", "-a", "256", str(pdf)], check=True, capture_output=True, text=True
    ).stdout.split()[0]
    print(f"pdf sha256 {digest} {'matches' if digest == PDF_SHA256 else 'DOES NOT MATCH'} the source record")
    if digest != PDF_SHA256:
        return 2

    records = {}
    for line in batch.read_text().splitlines():
        rec = json.loads(line)
        if rec["kind"] == "result":
            records[rec["id"]] = rec
    print(f"{len(records)} result records in the batch")

    pages = read_pages(pdf)
    assert len(pages) == 47, f"{len(pages)} pages"
    c = Checker(pages, records)
    extra: list[str] = []

    # ---- Figure 2, page 6: eight rows, three panels placed by x. ----------
    p6 = c.page(6)
    headers = [find_label(p6, h) for h in ("TCGA", "CPTAC", "Pan-Cancer")]
    header_order = [h.text for h in sorted(headers, key=lambda w: w.x0)]
    assert header_order == ["TCGA", "CPTAC", "Pan-Cancer"], header_order
    # Row labels are taken in printed order, each below the previous one, so the
    # section headings ("Ladon", "Baselines") cannot stand in for a data row.
    fig2_anchors = []
    last_y = 0.0
    for label, stem in FIG2_ROWS:
        anchor = find_label(p6, label, y=(last_y + 1, 560), with_values=3, value_x=(160, 460))
        last_y = anchor.y0
        fig2_anchors.append((anchor, stem, label))
    panel_x = cluster_x(
        [w.xc for anchor, _, _ in fig2_anchors for w in numbers(p6, band(anchor), xmin=160, xmax=460)]
    )
    assert len(panel_x) == 3, f"figure 2 panels: {panel_x}"
    extra.append(
        f"figure 2 panel x centres {['%.0f' % x for x in panel_x]}, "
        f"headers in printed order {header_order}"
    )
    for anchor, stem, label in fig2_anchors:
        found = numbers(p6, band(anchor), xmin=160, xmax=460)
        for value in found:
            column = min(range(3), key=lambda i: abs(value.xc - panel_x[i]))
            c.check(f"ladon-20261115-result-fig2-{stem}-{FIG2_PANELS[column]}", value.text)
        if len(found) != 3:
            extra.append(f"figure 2 row {label!r}: {len(found)} values, not 3")

    # ---- Figure 3, page 7: OS and PFS printed as word pairs. --------------
    p7 = c.page(7)
    last_y = 0.0
    for label, stem in FIG3_ROWS:
        anchor = find_label(p7, label, y=(last_y + 1, 545))
        last_y = anchor.y0
        pairs = {}
        for key in ("OS", "PFS"):
            hits = sorted(
                (
                    w
                    for w in p7
                    if w.text == key
                    and anchor.y0 - 14 <= w.yc <= anchor.y1 + 14
                    and w.x0 > anchor.x0
                ),
                key=lambda w: w.x0,
            )
            value = None
            for hit in hits:
                after = numbers(p7, (hit.y0 - 3, hit.y1 + 3), xmin=hit.x1)
                if after:
                    value = after[0].text
                    break
            pairs[key] = value
        c.check(f"ladon-20261115-result-fig3-{stem}-os", pairs["OS"])
        c.check(f"ladon-20261115-result-fig3-{stem}-pfs", pairs["PFS"])

    # ---- Figure 4, page 8: the value is in the caption. -------------------
    p8 = c.page(8)
    caption = " ".join(w.text for w in sorted(p8, key=lambda w: (w.y0, w.x0)))
    m = re.search(r"Uno.s C-index in OAK, ([0-9.]+)\)", caption)
    c.check("ladon-20261115-result-fig4-ladon-plus-clinical-oak-os", m.group(1) if m else None)

    # ---- Figure 5, page 9: the legend line. -------------------------------
    p9 = c.page(9)
    stage_headers = [find_label(p9, h, y=(250, 275)) for h in ("Matched", "All", "+")]
    stage_order = [h.text for h in sorted(stage_headers, key=lambda w: w.x0)]
    assert stage_order == ["Matched", "All", "+"], stage_order
    extra.append(
        "figure 5 training-stage headers in printed order "
        f"{stage_order}; the legend values sit on one line below the panel and are not "
        "placed per stage by the PDF, so the stage they belong to is a reading of the text, "
        "not a geometric fact"
    )
    for label, stem in (("Ladon", "ladon"), ("DGE", "dge"), ("Hallmark GSEA", "hallmark-gsea")):
        anchor = find_label(p9, label, y=(290, 315))
        after = numbers(p9, band(anchor, 4), xmin=anchor.x1)
        c.check(f"ladon-20261115-result-fig5-{stem}-plus-trials", after[0].text if after else None)

    # ---- Figure 6, page 10: one value per row. ----------------------------
    p10 = c.page(10)
    last_y = 0.0
    for label, stem in FIG6_ROWS:
        anchor = find_label(p10, label, y=(last_y + 1, 355), with_values=1, value_x=(150, 300))
        last_y = anchor.y0
        found = numbers(p10, band(anchor, 6), xmin=150, xmax=300)
        c.check(f"ladon-20261115-result-fig6-{stem}-response", found[0].text if found else None)

    # ---- Figure 11, page 24: two readout lines. ---------------------------
    p24 = c.page(24)
    text24 = " ".join(w.text for w in sorted(p24, key=lambda w: (round(w.y0), w.x0)))
    m = re.search(
        r"r with measured: Ladon ([0-9.]+) \[([0-9.]+), ([0-9.]+)\] . cohort-trained baseline "
        r"([0-9.]+) \[([0-9.]+), ([0-9.]+)\]",
        text24,
    )
    assert m, "figure 11 r readout not found"
    c.check("ladon-20261115-result-fig11-ladon-insr-r", m.group(1))
    c.check_interval("ladon-20261115-result-fig11-ladon-insr-r", m.group(2), m.group(3))
    c.check("ladon-20261115-result-fig11-cohort-trained-baseline-insr-r", m.group(4))
    c.check_interval("ladon-20261115-result-fig11-cohort-trained-baseline-insr-r", m.group(5), m.group(6))
    m = re.search(
        r"MAE, points: Ladon ([0-9.]+) . baseline ([0-9.]+) . cohort mean ([0-9.]+)", text24
    )
    assert m, "figure 11 MAE readout not found"
    c.check("ladon-20261115-result-fig11-ladon-insr-mae", m.group(1))
    c.check("ladon-20261115-result-fig11-cohort-trained-baseline-insr-mae", m.group(2))
    c.check("ladon-20261115-result-fig11-cohort-mean-insr-mae", m.group(3))

    # ---- Figure 12a, page 25: four rows above the median-r axis. ----------
    p25 = c.page(25)
    last_y = 0.0
    for label, stem in FIG12A_ROWS:
        anchor = find_label(p25, label, y=(last_y + 1, 210), with_values=1, value_x=(200, 520))
        last_y = anchor.y0
        found = numbers(p25, band(anchor, 5), xmin=200, xmax=520)
        c.check(f"ladon-20261115-result-fig12a-{stem}", found[0].text if found else None)

    # ---- Figure 13, page 26: the right-hand panel. ------------------------
    p26 = c.page(26)
    last_y = 0.0
    for label, stem in FIG13_ROWS:
        # Pad 4, not 6: the right-hand panel's x-axis ticks (0.50 to 0.90) are
        # printed one line above the "Ladon" row and fall inside a wider band.
        anchor = find_label(
            p26, label, y=(last_y + 1, 530), with_values=1, value_pad=4, value_x=(430, 540)
        )
        last_y = anchor.y0
        found = numbers(p26, band(anchor, 4), xmin=430, xmax=540)
        c.check(f"ladon-20261115-result-fig13-{stem}", found[0].text if found else None)

    # ---- Figure 14, page 27: the prose sentence. --------------------------
    p27 = c.page(27)
    text27 = " ".join(w.text for w in sorted(p27, key=lambda w: (round(w.y0), w.x0)))
    m = re.search(
        r"Ladon was correct for ([0-9]+%) of genes over time and ([0-9]+%) between COVID-19 and "
        r"healthy controls, compared with ([0-9]+%) and ([0-9]+%) for direct quantification",
        text27,
    )
    assert m, "figure 14 prose not found"
    c.check("ladon-20261115-result-fig14-ladon-day0-14", m.group(1))
    c.check("ladon-20261115-result-fig14-ladon-covid-vs-healthy", m.group(2))
    c.check("ladon-20261115-result-fig14-isoform-quantification-from-10x-reads-day0-14", m.group(3))
    c.check("ladon-20261115-result-fig14-isoform-quantification-from-10x-reads-covid-vs-healthy", m.group(4))

    # ---- Figure 17, page 33: bottom chart, two columns placed by x. -------
    p33 = c.page(33)
    bottom = [w for w in p33 if w.y0 > 500]
    pearson_axis = find_label(bottom, "Pearson r")
    ordering_axis = find_label(bottom, "Pairwise ordering accuracy")
    assert pearson_axis.x0 < ordering_axis.x0, "figure 17 axis order"
    fig17_anchors = []
    last_y = 0.0
    for label, stem in FIG17_ROWS:
        anchor = find_label(bottom, label, y=(last_y + 1, 635), with_values=2, value_x=(250, 520))
        last_y = anchor.y0
        fig17_anchors.append((anchor, stem, label))
    col_x = cluster_x(
        [
            w.xc
            for anchor, _, _ in fig17_anchors
            for w in numbers(bottom, band(anchor, 5), xmin=250, xmax=520)
        ]
    )
    assert len(col_x) == 2, f"figure 17 columns: {col_x}"
    extra.append(
        f"figure 17 bottom column x centres {['%.0f' % x for x in col_x]}; "
        f"Pearson axis title at x {pearson_axis.x0:.0f}, pairwise-ordering axis title at "
        f"x {ordering_axis.x0:.0f}"
    )
    ladon_values: dict[str, float] = {}
    cibersort_values: dict[str, float] = {}
    for anchor, stem, label in fig17_anchors:
        found = numbers(bottom, band(anchor, 5), xmin=250, xmax=520)
        if len(found) != 2:
            extra.append(f"figure 17 row {label!r}: {len(found)} values, not 2")
        for value in found:
            column = min(range(2), key=lambda i: abs(value.xc - col_x[i]))
            rid = f"ladon-20261115-result-fig17-{stem}-{FIG17_COLUMNS[column]}"
            c.check(rid, value.text)
            if stem in ("ladon", "cibersort") and FIG17_COLUMNS[column] == "pearson":
                (ladon_values if stem == "ladon" else cibersort_values)["overall"] = float(value.text)

    # Figure 17 top panels: "r <Ladon> <CIBERSORT>" beside each lineage name.
    top = [w for w in p33 if w.y0 < 500]
    legend = [w.text for w in sorted((w for w in top if w.y0 < 120), key=lambda w: w.x0)]
    assert "Ladon" in legend and "CIBERSORT" in legend, legend
    assert legend.index("Ladon") < legend.index("CIBERSORT"), legend
    per_lineage: dict[str, tuple[float, float]] = {}
    for label, stem in FIG17_LINEAGES:
        anchor = find_label(top, label)
        r_marks = sorted(
            (w for w in top if w.text == "r" and abs(w.yc - anchor.yc) < 6 and w.x0 > anchor.x1),
            key=lambda w: w.x0,
        )
        assert r_marks, f"figure 17 lineage {label}: no 'r' label"
        found = numbers(top, (r_marks[0].y0 - 3, r_marks[0].y1 + 3), xmin=r_marks[0].x1)[:2]
        assert len(found) == 2, f"figure 17 lineage {label}: {[w.text for w in found]}"
        c.check(f"ladon-20261115-result-fig17-ladon-lineage-{stem}", found[0].text)
        c.check(f"ladon-20261115-result-fig17-cibersort-lineage-{stem}", found[1].text)
        per_lineage[stem] = (float(found[0].text), float(found[1].text))

    # ---- Figure 18, page 35: four cohort blocks, AUC with interval. -------
    p35 = c.page(35)
    cohort_y = []
    for cohort, _, _ in FIG18_BLOCKS:
        anchor = find_label(p35, cohort, y=(cohort_y[-1] + 1, 800) if cohort_y else None)
        cohort_y.append(anchor.y0)
    assert cohort_y == sorted(cohort_y), f"figure 18 cohort order: {cohort_y}"
    for (cohort, suffix, rows), y_top in zip(FIG18_BLOCKS, cohort_y):
        for label, stem in rows:
            anchor = find_label(p35, label, y=(y_top, y_top + 130))
            whole = sorted(
                (w for w in p35 if abs(w.yc - anchor.yc) < 5 and w.x0 >= anchor.x0),
                key=lambda w: w.x0,
            )
            after = whole[len(label.split()):]
            joined = " ".join(w.text for w in after)
            m = re.match(r"([0-9.]+) \[([0-9.]+), ([0-9.]+)\]", joined)
            rid = f"ladon-20261115-result-fig18-{stem}-{suffix}"
            if not m:
                c.check(rid, None, f"no AUC pattern beside {label!r} in {cohort}: {joined!r}")
                continue
            c.check(rid, m.group(1), f"cohort block {cohort}")
            c.check_interval(rid, m.group(2), m.group(3))

    # ---- Arithmetic constraints the figures imply. ------------------------
    # 1. Figure 17's five per-lineage r values should average to the bottom
    #    chart's overall Pearson r for the same method.
    for name, index, overall in (("Ladon", 0, ladon_values), ("CIBERSORT", 1, cibersort_values)):
        mean = sum(v[index] for v in per_lineage.values()) / len(per_lineage)
        printed = overall["overall"]
        ok = abs(mean - printed) < 0.01
        extra.append(
            f"figure 17 {name}: mean of five per-lineage r = {mean:.3f}, bottom chart prints "
            f"{printed:.2f} ({'consistent' if ok else 'INCONSISTENT'})"
        )
        if not ok:
            c.failures += 1
    # 2. Figure 2's pan-cancer panel is not the mean of the two transfer bars
    #    (the caption says it averages two pan-cancer C-indices), so check it
    #    is indeed different, which guards against a copied column.
    ladon_cells = {
        p: float(records[f"ladon-20261115-result-fig2-ladon-{p}"]["attributes"]["printed_value"])
        for p in FIG2_PANELS
    }
    transfer_mean = (ladon_cells["tcga-to-cptac"] + ladon_cells["cptac-to-tcga"]) / 2
    extra.append(
        f"figure 2 Ladon: transfer bars mean {transfer_mean:.3f}, pan-cancer bar "
        f"{ladon_cells['pan-cancer']:.2f}; the caption says the third panel averages the two "
        "pan-cancer C-indices, not the two bars, so these must differ"
    )
    if abs(transfer_mean - ladon_cells["pan-cancer"]) < 0.005:
        c.failures += 1
        extra.append("figure 2: pan-cancer equals the mean of the transfer bars, which the caption excludes")
    # 3. Figure 14's prose values must be the figure's own top-5% labels where
    #    the figure prints them.
    m = re.search(r"top 5% ([0-9]+%) vs ([0-9]+%)", text27)
    if m:
        extra.append(
            f"figure 14 in-figure label 'top 5% {m.group(1)} vs {m.group(2)}' against prose "
            f"COVID-19 contrast {records['ladon-20261115-result-fig14-ladon-covid-vs-healthy']['attributes']['printed_value']}"
            f" and {records['ladon-20261115-result-fig14-isoform-quantification-from-10x-reads-covid-vs-healthy']['attributes']['printed_value']}"
        )
        if (
            m.group(1)
            != records["ladon-20261115-result-fig14-ladon-covid-vs-healthy"]["attributes"]["printed_value"]
        ):
            c.failures += 1

    # ---- Report ----------------------------------------------------------
    checked = {r[0] for r in c.rows if not r[0].endswith("#ci")}
    missing = sorted(set(records) - checked)
    out = Path(__file__).with_name("figure-label-check.tsv")
    with out.open("w") as fh:
        fh.write("id\tstatus\tvalue_read_from_pdf\tnote\n")
        for row in c.rows:
            fh.write("\t".join(row) + "\n")
    print(f"wrote {out.name}: {len(c.rows)} checks, {c.failures} failing")
    print(f"results re-read: {len(checked)} of {len(records)}")
    if missing:
        print("NOT re-read by this script:")
        for rid in missing:
            print(f"  {rid}")
    print()
    for line in extra:
        print(f"note: {line}")
    return 1 if (c.failures or missing) else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
