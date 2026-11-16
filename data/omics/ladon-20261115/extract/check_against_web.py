"""Second check of extract/figures.json against the data embedded in the web report's figures.

The web version of the report (https://www.blank.bio/ladon-technical-report) draws each figure
in an iframe whose page carries the plotted numbers as a JavaScript object literal. This script
does not execute that JavaScript. It reads the numbers with regular expressions, rounds them to
the precision printed in the PDF, and compares them with the values parse_figures.py read from
the PDF text layer. A match confirms row and column assignment for figures whose text layer
scatters values across lines (Figure 2). The embedded values are not stored as results.

Usage:
  python3 -I extract/check_against_web.py extract/figures.json <dir with fig02..fig18 html> > extract/web-check.txt

Iframe files checked (SHA-256 of the retrieval on 2026-11-15):
  fig02-generalization.html        269d9eb489aaecbbb9acbf56ba2802f71912f0c8e91df1a501ffa86638d63277
  fig03-hazard-ratios.html         d4ffa349a3b469432b2392fb31595f61fbf58df81c1fadcb438f5a1cb361dfaa
  fig05-training-data-size.html    b0be9f34e66b5ff2e05c27536503dc5afb71f064c51713274b5c5559e8a69b60
  fig06-response-prediction.html   afa0d46855e1c3b15efa9a6cca8c621d4314ad445dd7777216e62c7ac646629f
  fig17-pbmc-benchmark.html        6e4aedb5eba8c9461b3372af578e7f9c54b33bcc0acd8ec37eec17b410780876
  fig18-breast-pcr.html            151786784a08e88f5683d17644613684409b2364ed4c8ab67ae12772b03df632
"""

import hashlib
import json
import os
import re
import sys
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

EXPECTED = {
    "fig02-generalization.html": "269d9eb489aaecbbb9acbf56ba2802f71912f0c8e91df1a501ffa86638d63277",
    "fig03-hazard-ratios.html": "d4ffa349a3b469432b2392fb31595f61fbf58df81c1fadcb438f5a1cb361dfaa",
    "fig05-training-data-size.html": "b0be9f34e66b5ff2e05c27536503dc5afb71f064c51713274b5c5559e8a69b60",
    "fig06-response-prediction.html": "afa0d46855e1c3b15efa9a6cca8c621d4314ad445dd7777216e62c7ac646629f",
    "fig17-pbmc-benchmark.html": "6e4aedb5eba8c9461b3372af578e7f9c54b33bcc0acd8ec37eec17b410780876",
    "fig18-breast-pcr.html": "151786784a08e88f5683d17644613684409b2364ed4c8ab67ae12772b03df632",
}

rows_out = []


def num(x):
    return Decimal(x if not x.startswith(".") else "0" + x)


def agrees(raw, printed):
    """True if the embedded value rounds to the printed value, half-up or half-even."""
    places = Decimal(1).scaleb(-len(printed.split(".")[1])) if "." in printed else Decimal(1)
    v = num(raw)
    return str(v.quantize(places, ROUND_HALF_UP)) == printed or str(v.quantize(places, ROUND_HALF_EVEN)) == printed


def binary_float(raw, printed):
    """JavaScript toFixed rounds the binary double, so 0.735 prints as 0.73."""
    places = len(printed.split(".")[1]) if "." in printed else 0
    return f"{float(num(raw)):.{places}f}" == printed


def compare(fig, row, col, raw, printed):
    if agrees(raw, printed):
        status = "agree"
    elif binary_float(raw, printed):
        status = "agree only under binary float rounding (decimal rounding gives a different last digit)"
    else:
        status = "DIFFER"
    rows_out.append((fig, row, col, printed, raw, status))


def data_block(html):
    i = html.index("const DATA=")
    return html[i : html.index("window.FIGURE_DATA", i)]


def main(figs_json, d):
    figs = json.load(open(figs_json, encoding="utf-8"))
    for name, sha in EXPECTED.items():
        got = hashlib.sha256(open(os.path.join(d, name), "rb").read()).hexdigest()
        assert got == sha, (name, got)
    read = lambda n: open(os.path.join(d, n), encoding="utf-8").read()

    # Figure 2: means per method and facet.
    b = data_block(read("fig02-generalization.html"))
    key = {"Ladon + clinical covariates": "ladon_clinical", "Ladon": "ladon", "Differential gene expression": "dge",
           "Hallmark GSEA": "gsea", "Isoform TPM": "isoform_tpm", "Clinical covariates (BMRetriever)": "clin_bmr7b",
           "BulkRNABert": "bulkrnabert", "BulkFormer": "bulkformer"}
    facet = {"TCGA → CPTAC": "tcga>cptac", "CPTAC → TCGA": "cptac>tcga", "Pan-Cancer": "mean2"}
    for r in figs["fig2"]:
        for col, printed in r["values"].items():
            m = re.search(r'kind:"mean",method:"%s",facet:"%s",value:([\d.]+)' % (key[r["row"]], re.escape(facet[col])), b)
            compare("fig2", r["row"], col, m.group(1), printed)

    # Figure 3: geometric means, OS rows then PFS rows.
    b = data_block(read("fig03-hazard-ratios.html"))
    os_part, pfs_part = b.split("pfs_rows:")
    lab = {"Ladon + clinical covariates": "Ladon + clinical text", "Ladon": "Ladon", "Differential gene expression": "DGE signature",
           "TPM · matched TCGA": "TPM · matched TCGA", "Clinical covariates (BMRetriever)": "Clinical text alone",
           "BulkRNABert": "BulkRNABert", "BulkFormer": "BulkFormer"}
    for r in figs["fig3"]:
        m = re.search(r'label:"%s",role:"[a-z]+",value:([\d.]+)' % re.escape(lab[r["row"]]), os_part)
        compare("fig3", r["row"], "OS", m.group(1), r["values"]["OS"])
        m = re.search(r'label:"%s",value:([\d.]+)' % re.escape(lab[r["row"]]), pfs_part)
        compare("fig3", r["row"], "PFS", m.group(1), r["values"]["PFS"])

    # Figure 5: the third stage, size-weighted value (not equal_trial_mean).
    b = data_block(read("fig05-training-data-size.html"))
    stage = b[b.index('name:"TCGA + non-trial cohorts + other clinical trials"') :]
    k5 = {"Ladon": "Ladon", "DGE": "DGE", "Hallmark GSEA": "GSEA"}
    for r in figs["fig5"]:
        m = re.search(r"%s:\{value:([\d.]+)" % k5[r["row"]], stage)
        compare("fig5", r["row"], "+ trials", m.group(1), r["values"]["+ trials"])

    # Figure 6: mean AUROC is the value after each row's trials array.
    b = data_block(read("fig06-response-prediction.html"))
    k6 = {"Ladon": "Ladon", "Differential gene expression": "Differential gene expression", "Gene TPM": "Gene TPM · academic only",
          "PD-L1 mRNA": "PD-L1 mRNA", "T-effector / IFN-γ": "T-effector / IFN-γ", "IMPRES": "IMPRES", "TIDE": "TIDE",
          "Clinical covariates (BMRetriever)": "Clinical text alone", "BulkRNABert": "BulkRNABert", "BulkFormer": "BulkFormer"}
    for r in figs["fig6"]:
        m = re.search(r'\{label:"%s",.*?trials:\[[^\]]*\],value:([\d.]+)' % re.escape(k6[r["row"]]), b)
        compare("fig6", r["row"], "Response AUROC", m.group(1), r["values"]["Response AUROC"])

    # Figure 17: accuracy summary per method.
    h = read("fig17-pbmc-benchmark.html")
    for r in figs["fig17_accuracy"]:
        seg = h[h.index('label:"%s",category:' % r["row"]) :]
        m = re.search(r'"mean r":\{value:([\d.]+)', seg)
        compare("fig17", r["row"], "Pearson r", m.group(1), r["values"]["Pearson r"])
        m = re.search(r'"mean pairwise order accuracy":\{value:([\d.]+)', seg)
        compare("fig17", r["row"], "Pairwise ordering accuracy", m.group(1), r["values"]["Pairwise ordering accuracy"])

    # Figure 18: AUC and CI per group, cohort and predictor.
    h = read("fig18-breast-pcr.html")
    grp = {"ER+/HER2−": "ER+/HER2-", "HER2+": "HER2+"}
    for r in figs["fig18"]:
        seg = h[h.index('group:"%s",cohort:"%s"' % (grp[r["group"]], r["cohort"])) :]
        label = "Ladon" if r["row"] == "Ladon deconvolution" else r["row"]
        seg = seg[seg.index('label:"%s' % label) :]
        m = re.search(r"auc:([\d.]+),ci:\[([\d.]+),([\d.]+)\]", seg)
        compare("fig18", f'{r["cohort"]} {r["group"]} {r["row"]}', "AUC", m.group(1), r["values"]["AUC"])
        compare("fig18", f'{r["cohort"]} {r["group"]} {r["row"]}', "CI lower", m.group(2), r["values"]["ci"][0])
        hi = m.group(3) if "." in m.group(3) else m.group(3) + ".00"
        compare("fig18", f'{r["cohort"]} {r["group"]} {r["row"]}', "CI upper", hi, r["values"]["ci"][1])

    for row in rows_out:
        print("\t".join(row))
    differ = [r for r in rows_out if r[-1] == "DIFFER"]
    float_only = [r for r in rows_out if r[-1].startswith("agree only")]
    print(f"# {len(rows_out)} values compared, {len(differ)} differ, {len(float_only)} agree only under binary float rounding")
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
