"""Parse the printed figure labels of the Ladon technical report (Zenodo 10.5281/zenodo.24157116).

The report has no tables. Every stored value is a label printed inside a figure, a figure
caption or the prose next to it, and present in the PDF text layer. This script reads the
`pdftotext -layout` text layer of the pinned PDF, finds each figure by the page it is printed
on, asserts every row label in printed order, and writes extract/figures.json.

Usage:
  pdftotext -layout Ladon-An-RNA-Foundation-Model-for-Predicting-Patient-Outcomes.pdf ladon.layout.txt
  python3 -I extract/parse_figures.py ladon.layout.txt extract/figures.json

PDF SHA-256 64edf7c3c956c50a65aa01a0dcaa13f0cfef28ab4373ecfd50c431e67143893c (pdftotext 26.08.0).
"""

import json
import re
import sys

DEC = r"-?\d+\.\d+"


def pages(text):
    """Split the text layer on the running footer 'Ladon · Blank Bio · N / 47'."""
    out, cur = {}, []
    for line in text.replace("\f", "").split("\n"):
        m = re.search(r"Ladon · Blank Bio · (\d+) / 47", line)
        if m:
            out[int(m.group(1))] = cur
            cur = []
        else:
            cur.append(line)
    assert len(out) == 47, len(out)
    return out


def find(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if re.search(pattern, lines[i]):
            return i
    raise AssertionError(f"label not found: {pattern!r}")


def column(pos, bounds):
    for i, b in enumerate(bounds):
        if pos < b:
            return i
    return len(bounds)


def fig2(p):
    """Figure 2, page 6: eight rows x three panels (TCGA->CPTAC, CPTAC->TCGA, pan-cancer).

    Rows span several lines, so each row owns the lines from its label to the next label and
    each value is assigned to a panel by its character offset in the layout line."""
    lines = p[6]
    labels = [
        ("Ladon + clinical covariates", r"^\s+Ladon \+ clinical covariates\s+0\."),
        ("Ladon", r"^\s+Ladon\s+0\.\d\d"),
        ("Differential gene expression", r"^\s+Differential gene expression\s+‡"),
        ("Hallmark GSEA", r"^\s+Hallmark GSEA\s+‡"),
        ("Isoform TPM", r"^\s+Isoform TPM\s+0\."),
        ("Clinical covariates (BMRetriever)", r"^\s+Clinical covariates\s*$"),
        ("BulkRNABert", r"^\s+BulkRNABert\s+0\."),
        ("BulkFormer", r"^\s+BulkFormer\s+0\."),
    ]
    idx, start = [], 0
    for _, pat in labels:
        i = find(lines, pat, start)
        idx.append(i)
        start = i + 1
    end = find(lines, r"0\.5\s+0\.7\s+0\.9", start)
    assert "(BMRetriever)" in "".join(lines[idx[5] : idx[6]])
    panels = ["TCGA → CPTAC", "CPTAC → TCGA", "Pan-Cancer"]
    assert re.search(r"TCGA\s+→ CPTAC\s+CPTAC\s+→ TCGA\s+Pan-Cancer", "\n".join(lines[: idx[0]]))
    assert "Mean of 2 transfers" in "\n".join(lines[: idx[0]])
    rows = []
    for k, (name, _) in enumerate(labels):
        stop = idx[k + 1] if k + 1 < len(idx) else end
        cells = [None, None, None]
        for line in lines[idx[k] : stop]:
            for m in re.finditer(r"\b0\.\d\d\b", line):
                c = column(m.start(), [70, 105])
                assert cells[c] is None, (name, line)
                cells[c] = m.group(0)
        assert all(cells), (name, cells)
        rows.append({"row": name, "values": dict(zip(panels, cells))})
    return rows


def fig3(p):
    """Figure 3, page 7: seven rows, each printing 'OS x' then 'PFS y'."""
    lines = p[7]
    labels = [
        ("Ladon + clinical covariates", r"^\s+Ladon \+ clinical\s+OS"),
        ("Ladon", r"^\s+Ladon\s*$"),
        ("Differential gene expression", r"^\s+Differential gene\s+OS"),
        ("TPM · matched TCGA", r"^\s+TPM · matched TCGA\s*$"),
        ("Clinical covariates (BMRetriever)", r"^\s+Clinical covariates\s+OS"),
        ("BulkRNABert", r"^\s+BulkRNABert\s*$"),
        ("BulkFormer", r"^\s+BulkFormer\s*$"),
    ]
    start = 0
    for _, pat in labels:
        start = find(lines, pat, start) + 1
    first = find(lines, r"Ladon \+ clinical\s+OS")
    last = find(lines, r"Survival hazard ratio")
    vals = re.findall(r"\b(OS|PFS) (\d\.\d\d)\b", "\n".join(lines[first:last]))
    assert [v[0] for v in vals] == ["OS", "PFS"] * 7, vals
    return [
        {"row": labels[i][0], "values": {"OS": vals[2 * i][1], "PFS": vals[2 * i + 1][1]}}
        for i in range(7)
    ]


def fig4(p):
    """Figure 4 caption, page 8: Uno's C-index of Ladon + clinical covariates in OAK."""
    text = " ".join(" ".join(p[8]).split())
    m = re.search(r"score 699 OAK patients, fitting the risk predictor on other cohorts \(Uno’s C-index in OAK, (0\.\d\d)\)", text)
    assert m
    return [{"row": "Ladon + clinical covariates", "values": {"Uno C-index in OAK": m.group(1)}}]


def fig5(p):
    """Figure 5, page 9: legend printing the three methods' size-weighted mean Uno C-index."""
    lines = p[9]
    i = find(lines, r"^\s*Ladon (0\.\d{3})\s+DGE (0\.\d{3})\s+Hallmark GSEA (0\.\d{3})\s*$")
    m = re.search(r"Ladon (0\.\d{3})\s+DGE (0\.\d{3})\s+Hallmark GSEA (0\.\d{3})", lines[i])
    assert "+ trials" in "\n".join(lines[:i]) and "≈18k" in "\n".join(lines[:i])
    return [
        {"row": "Ladon", "values": {"+ trials": m.group(1)}},
        {"row": "DGE", "values": {"+ trials": m.group(2)}},
        {"row": "Hallmark GSEA", "values": {"+ trials": m.group(3)}},
    ]


def fig6(p):
    """Figure 6, page 10: ten rows, mean response AUROC over six trials."""
    lines = p[10]
    labels = [
        ("Ladon", r"^\s+Ladon\s+(0\.\d{3})\s*$"),
        ("Differential gene expression", r"^\s+Differential gene expression\s+(0\.\d{3})"),
        ("Gene TPM", r"^\s+Gene TPM\s+(0\.\d{3})"),
        ("PD-L1 mRNA", r"^\s+PD-L1 mRNA\s+(0\.\d{3})"),
        ("T-effector / IFN-γ", r"^\s+T-effector / IFN-\s+γ\s+(0\.\d{3})"),
        ("IMPRES", r"^\s+IMPRES\s+(0\.\d{3})"),
        ("TIDE", r"^\s+TIDE\s+(0\.\d{3})"),
        ("Clinical covariates (BMRetriever)", r"^\s+Clinical covariates \(BMRetriever\)\s+(0\.\d{3})"),
        ("BulkRNABert", r"^\s+BulkRNABert\s+(0\.\d{3})"),
        ("BulkFormer", r"^\s+BulkFormer\s+(0\.\d{3})"),
    ]
    rows, start = [], 0
    for name, pat in labels:
        i = find(lines, pat, start)
        rows.append({"row": name, "values": {"Response AUROC": re.search(pat, lines[i]).group(1)}})
        start = i + 1
    assert "Response AUROC" in "\n".join(lines[start:])
    return rows


def fig11(p):
    """Figure 11 readout, page 24: INSR in 166 stomach tumors."""
    text = "\n".join(p[24])
    m = re.search(
        r"r with measured: Ladon (0\.\d\d) \[(0\.\d\d), (0\.\d\d)\] · cohort-trained baseline (0\.\d\d) \[(0\.\d\d), (0\.\d\d)\]",
        text,
    )
    n = re.search(r"MAE, points: Ladon (\d+\.\d) · baseline (\d+\.\d) · cohort mean (\d+\.\d)", text)
    assert m and n
    return [
        {"row": "Ladon", "values": {"r": m.group(1), "r_ci": [m.group(2), m.group(3)], "MAE": n.group(1)},
         "printed": {"r": f"{m.group(1)} [{m.group(2)}, {m.group(3)}]"}},
        {"row": "cohort-trained baseline", "values": {"r": m.group(4), "r_ci": [m.group(5), m.group(6)], "MAE": n.group(2)},
         "printed": {"r": f"{m.group(4)} [{m.group(5)}, {m.group(6)}]"}},
        {"row": "cohort mean", "values": {"MAE": n.group(3)}},
    ]


def fig12(p):
    """Figure 12a, page 25: median Pearson r over 14,526 gene-cancer-type combinations."""
    lines = p[25]
    find(lines, r"^a 14,526 gene–cancer-type combinations across 1,572 held-out tumors")
    labels = [
        ("Ladon", r"^\s+Ladon\s+(0\.\d\d)\s*$"),
        ("Cohort-trained baseline", r"^\s+Cohort-trained baseline\s+(0\.\d\d)\s*$"),
        ("Linear model on public data", r"^\s+Linear model on public data\s+(0\.\d\d)\s*$"),
        ("Nearest public samples", r"^\s+Nearest public samples\s+(0\.\d\d)\s*$"),
    ]
    rows, start = [], 0
    for name, pat in labels:
        i = find(lines, pat, start)
        row = {"row": name, "values": {"median Pearson r": re.search(pat, lines[i]).group(1)}}
        if name != "Ladon":
            h = re.search(r"Ladon higher in (\d+\.\d)%", lines[i + 1])
            assert h, lines[i + 1]
            row["values"]["Ladon higher in"] = h.group(1) + "%"
        rows.append(row)
        start = i + 1
    return rows


def fig13(p):
    """Figure 13 right panel, pages 26: Pearson r between predicted and measured changes."""
    lines = p[26]
    top = find(lines, r"Pearson r between predicted and measured")
    bottom = find(lines, r"^Figure 13\.")
    order = []
    for line in lines[top + 2 : bottom]:
        for m in re.finditer(r"\b0\.\d\d\b", line):
            if m.start() > 110:
                order.append(m.group(0))
    block = "\n".join(lines[top:bottom])
    names = ["Ladon", "Organ average", "Nearest public samples", "Linear model on public data"]
    pos = [block.find("Ladon                             0.80"), block.find("Organ average"), block.find("Nearest public"), block.find("Linear model")]
    assert all(x >= 0 for x in pos) and pos == sorted(pos), pos
    assert len(order) == 4, order
    prose = " ".join(" ".join(p[26] + p[27]).split())
    assert "(Pearson correlation 0.80) than the organ-average lookup (0.68) or expression-based baselines (0.66–0.67)" in prose
    return [{"row": n, "values": {"Pearson r": v}} for n, v in zip(names, order)]


def fig14(p):
    """Figure 14 prose, page 27: share of the top 5% of genes with correctly predicted direction."""
    text = " ".join(" ".join(p[27]).split())
    m = re.search(
        r"Among the 5% of genes with the largest measured changes \(460 genes\), Ladon was correct for (\d+)% of genes "
        r"over time and (\d+)% between COVID-19 and healthy controls, compared with (\d+)% and (\d+)% for direct "
        r"quantification \(McNemar P = 0\.003 and P < 0\.001, respectively\)",
        text,
    )
    assert m
    fig = re.search(r"top 5% (\d+)% vs (\d+)%", "\n".join(p[27]))
    assert fig and fig.group(1) == m.group(2) and fig.group(2) == m.group(4)
    return [
        {"row": "Ladon", "values": {"Day 0 → 14": m.group(1) + "%", "COVID-19 vs healthy": m.group(2) + "%"}},
        {"row": "Isoform quantification from 10x reads", "values": {"Day 0 → 14": m.group(3) + "%", "COVID-19 vs healthy": m.group(4) + "%"}},
    ]


def fig17(p):
    """Figure 17, page 33: accuracy chart (six methods x two measures) and per-lineage r."""
    lines = p[33]
    labels = ["EPIC", "ABIS", "BayesPrism", "CIBERSORT", "DWLS", "Ladon"]
    acc, start = [], find(lines, r"Bulk RNA-seq\s+EPIC")
    for name in labels:
        pat = rf"\s{name}\s+(0\.\d\d)\s+(0\.\d\d)\s*$"
        i = find(lines, pat, start)
        m = re.search(pat, lines[i])
        acc.append({"row": name, "values": {"Pearson r": m.group(1), "Pairwise ordering accuracy": m.group(2)}})
        start = i + 1
    assert re.search(r"Pearson r\s+Pairwise ordering accuracy \(0\.5 = chance\)", "\n".join(lines[start : start + 3]))
    assert re.search(r"Ladon\s+CIBERSORT", "\n".join(lines))
    per = {}
    for lin in ["CD4 T", "CD8 T", "NK", "B/plasma", "Monocyte"]:
        m = re.search(re.escape(lin) + r"\s+r (0\.\d\d) (0\.\d\d)", "\n".join(lines))
        assert m, lin
        per[lin] = (m.group(1), m.group(2))
    lineage = [
        {"row": "Ladon", "values": {k: v[0] for k, v in per.items()}},
        {"row": "CIBERSORT", "values": {k: v[1] for k, v in per.items()}},
    ]
    return acc, lineage


def fig18(p):
    """Figure 18, page 35: pCR AUC with 95% CI in four external cohorts."""
    lines = p[35]
    cohorts = [
        ("ER+/HER2−", "ARTEMIS", r"ARTEMIS 35 patients, 3 pCR", ["Ladon deconvolution", r"Oncotype DX\*", r"MammaPrint\*"]),
        ("ER+/HER2−", "PBCP", r"PBCP 13 patients, 3 pCR", ["Ladon deconvolution", r"Oncotype DX\*", r"MammaPrint\*"]),
        ("HER2+", "PBCP", r"PBCP 18 patients, 11 pCR", ["Ladon deconvolution", "HER2 expression"]),
        ("HER2+", "DFCI IBC", r"DFCI IBC\s+22 patients, 9 pCR", ["Ladon deconvolution", "HER2 expression"]),
    ]
    assert find(lines, r"^ ER\+/HER2−\s*$") < find(lines, r"^ HER2\+\s*$")
    rows, start = [], 0
    for group, cohort, head, preds in cohorts:
        start = find(lines, head, start) + 1
        for pred in preds:
            pat = rf"^\s+{pred}\s+(\d\.\d\d) \[(\d\.\d\d), (\d\.\d\d)\]"
            i = find(lines, pat, start)
            m = re.search(pat, lines[i])
            rows.append({
                "group": group, "cohort": cohort, "row": pred.replace("\\", ""),
                "values": {"AUC": m.group(1), "ci": [m.group(2), m.group(3)]},
                "printed": f"{m.group(1)} [{m.group(2)}, {m.group(3)}]",
            })
            start = i + 1
    return rows


def main(src, out):
    text = open(src, encoding="utf-8").read()
    p = pages(text)
    acc, lineage = fig17(p)
    figs = {
        "fig2": fig2(p), "fig3": fig3(p), "fig4": fig4(p), "fig5": fig5(p), "fig6": fig6(p),
        "fig11": fig11(p), "fig12a": fig12(p), "fig13": fig13(p), "fig14": fig14(p),
        "fig17_accuracy": acc, "fig17_lineage": lineage, "fig18": fig18(p),
    }
    expected_rows = {"fig2": 8, "fig3": 7, "fig4": 1, "fig5": 3, "fig6": 10, "fig11": 3, "fig12a": 4,
                     "fig13": 4, "fig14": 2, "fig17_accuracy": 6, "fig17_lineage": 2, "fig18": 10}
    for k, n in expected_rows.items():
        assert len(figs[k]) == n, (k, len(figs[k]))
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(figs, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: len(v) for k, v in figs.items()}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
