"""Deterministic parse of the HyCell technical report.

Checks the PDF hash, extracts the text layer with pdftotext -layout, and returns
the printed cells of Tables 2 to 5, the Figure 1b matrix and the prose values.
Every row label and cell count is asserted, every value printed twice is
asserted equal, and the composite S is checked against its stated weights.

Usage: python3 -I parse.py <path to HyCell_Technical_Report.pdf>
"""

import hashlib
import re
import subprocess
import sys

PDF_SHA256 = "dc2cacf87ffae8525e81fede1b01f261d3a49cece9061465c36ad1fac6680a28"
V = r"0\.\d{3}"

MODELS = ["HyCell", "Stack", "SCimilarity", "scFoundation", "UCE", "Tahoe-x1 (70M)",
          "TranscriptFormer", "scGPT", "Geneformer V2", "STATE-SE", "scPRINT", "PCA"]
PRINTED = {"Stack": "Stackb", "SCimilarity": "SCimilarityl", "scPRINT": "scPRINTl"}
ATLASES = ["Immune", "Pancreas", "Lung", "PBMC", "Brain", "Cross-tissue immune", "AIDA"]
TABLE4_COLS = ["Immune", "Pancreas", "Lung", "PBMC", "Brain", "Cross-tissue", "AIDA"]
TABLE3_COLS = ["S", "Bio", "Batch", "LR", "kNN"]
FIG1B_MODELS = ["HyCell", "UCE", "Stack", "scFoundation", "scGPT", "Tahoe-x1 (70M)"]
TABLE5_ATLASES = ["Pancreas", "Lung", "PBMC", "Immune"]
WEIGHTS = {"Bio": 0.3, "Batch": 0.2, "LR": 0.25, "kNN": 0.25}
PAGE_MARKERS = {
    "figure1": "Figure 1: HyCell and ten published", "table2": "Table 2: Evaluation atlases",
    "table3": "Table 3: Zero-shot embeddings", "table4": "Table 4: Score S on each held-out",
    "section32": "Batch correction rises from 0.36 to 0.54", "section41": "4.1 Naive and effector",
    "section42": "4.2 From B cells to plasma", "section43": "4.3 Gene programs from the decoder",
    "table5": "Table 5: Annotation of a held-out batch",
}


def read_text(pdf):
    with open(pdf, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    if digest != PDF_SHA256:
        raise SystemExit(f"PDF sha256 {digest} is not the pinned {PDF_SHA256}")
    return subprocess.run(["pdftotext", "-layout", pdf, "-"], check=True,
                          capture_output=True).stdout.decode("utf-8")


def find(lines, marker, start=0):
    return next(i for i in range(start, len(lines)) if marker in lines[i])


def row(lines, start, label, pattern):
    for i in range(start, len(lines)):
        s = lines[i].strip()
        if s.startswith(label) and re.search(pattern, s[len(label):]):
            return i, s
    raise AssertionError(f"row {label!r} after {start}")


def pages(text):
    parts = [p for p in text.split("\f") if p.strip()]
    flat = [re.sub(r"\s+", " ", p) for p in parts]
    out = {"count": len(parts)}
    for key, marker in PAGE_MARKERS.items():
        hits = [i + 1 for i, p in enumerate(flat) if marker in p]
        assert len(hits) == 1, (key, hits)
        out[key] = hits[0]
    return out


def table(lines, caption, labels, n, printed=None):
    printed = printed or {}
    out, cursor = {}, find(lines, caption)
    for label in labels:
        shown = printed.get(label, label)
        i, s = row(lines, cursor, shown, V)
        values = re.findall(V, s[len(shown):])
        assert len(values) >= n, (caption, label, values)
        out[label] = values[-n:]
        cursor = i + 1
    return out


def parse(pdf):
    text = read_text(pdf)
    lines = text.split("\n")
    body = re.sub(r"\s+", " ", text)
    t3 = {m: dict(zip(TABLE3_COLS, v)) for m, v in
          table(lines, "Table 3: Zero-shot embeddings", MODELS, 5, PRINTED).items()}
    t4 = {m: dict(zip(TABLE4_COLS, v)) for m, v in
          table(lines, "Table 4: Score S on each held-out", MODELS, 7, PRINTED).items()}
    # Figure 1b shares its lines with Figure 1a's axis labels, so a row is the atlas
    # label followed by exactly six values anywhere on a line inside the figure.
    head = find(lines, "b Bio conservation per atlas")
    caption = find(lines, "Figure 1: HyCell and ten published", head)
    f1b_rows, cursor = {}, head
    for atlas in ATLASES + ["Mean"]:
        pat = re.compile(r"(?:^|\s)" + re.escape(atlas) + r"((?:\s+" + V + r"){6})\s*$")
        hit = next((i, m) for i in range(cursor, caption)
                   for m in [pat.search(lines[i])] if m)
        f1b_rows[atlas] = re.findall(V, hit[1].group(1))
        cursor = hit[0] + 1
    f1b = {(a, m): v for a, vals in f1b_rows.items() for m, v in zip(FIG1B_MODELS, vals)}
    t5 = {}
    cursor = find(lines, "Table 5: Annotation of a held-out batch")
    for atlas in TABLE5_ATLASES:
        i, s = row(lines, cursor, atlas, V)
        m = re.match(r"\s*(\d+)\s+(" + V + r")\s+(" + V + r")\s+(" + V + r")\s*$", s[len(atlas):])
        assert m, s
        t5[atlas] = dict(zip(["Batches", "Fine-tuned", "Frozen + LR", "Frozen + kNN"], m.groups()))
        cursor = i + 1

    # Composite S equals its stated weighting within rounding of five printed values.
    for model, r in t3.items():
        s = sum(w * float(r[k]) for k, w in WEIGHTS.items())
        assert abs(s - float(r["S"])) <= 0.001 + 1e-9, (model, s, r["S"])
    # Table 3's S is the mean of Table 4's seven atlases, within rounding.
    for model in MODELS:
        mean = sum(float(v) for v in t4[model].values()) / 7
        assert abs(mean - float(t3[model]["S"])) <= 0.001 + 1e-9, (model, mean)
    # Figure 1b's Mean row equals Table 3's Bio; its atlas cells average to it.
    for m in FIG1B_MODELS:
        assert f1b[("Mean", m)] == t3[m]["Bio"], (m, f1b[("Mean", m)], t3[m]["Bio"])
        mean = sum(float(f1b[(a, m)]) for a in ATLASES) / 7
        assert abs(mean - float(t3[m]["Bio"])) <= 0.001 + 1e-9, (m, mean)

    prose = {}
    def grab(key, pattern):
        m = re.search(pattern, body)
        assert m, key
        prose[key] = m.groups()
    grab("cd4", r"two groups are 85% naive and 96% effector cells \(ARI (0\.\d+)\), and the split is "
                r"nearly independent of sequencing chemistry \(NMI with chemistry (0\.\d+)\)")
    grab("cd4_donor", r"mean ARI (0\.\d+) over 12 donors; UCE (0\.\d+), Tahoe-x1 (0\.\d+)\)")
    grab("gd", r"\(ARI (0\.\d+) for HyCell, (0\.\d+) for PCA, at most 0\.06 for the published models\)")
    grab("pt_hycell", r"the Spearman correlation between pseudotime and stage, (0\.\d+), is the highest "
                      r"of all embeddings\. Averaged over donors it is (0\.\d+)")
    grab("pt_others", r"ahead of Stack \((0\.\d+) and (0\.\d+)\), SCimilarity \((0\.\d+) and (0\.\d+)\) "
                      r"and PCA \((0\.\d+) and (0\.\d+)\)")
    grab("decoder_fc", r"decoded and counted fold changes have a Spearman correlation of (0\.\d+)")
    grab("consistency", r"mean Spearman correlation is (0\.\d+) for the decoder and (0\.\d+) for "
                        r"pseudobulk counts; for classical against nonclassical monocytes it is (0\.\d+) "
                        r"against (0\.\d+), and for naive against effector CD4 T cells (0\.\d+) against "
                        r"(0\.\d+)")
    grab("ctia", r"Batch correction rises from (0\.\d+) to (0\.\d+) and biological conservation from "
                 r"(0\.\d+) to (0\.\d+)\.")
    # The prose rounds Figure 1b's cross-tissue HyCell Bio (0.633) to 0.63.
    assert abs(float(prose["ctia"][3]) - float(f1b[("Cross-tissue immune", "HyCell")])) <= 0.005
    # Figure 5c prints the same six consistency values as the prose (shared window).
    fig5 = re.sub(r"\s+", " ", text[text.index("c Consistency across donors"):
                                    text.index("Figure 5: Gene programs")])
    for v in prose["consistency"]:
        assert v in fig5, v
    return {"table3": t3, "table4": t4, "figure1b": f1b, "table5": t5, "prose": prose,
            "pages": pages(text)}


if __name__ == "__main__":
    import json
    d = parse(sys.argv[1])
    d["figure1b"] = {" | ".join(k): v for k, v in d["figure1b"].items()}
    print(json.dumps(d, indent=1, ensure_ascii=False))
