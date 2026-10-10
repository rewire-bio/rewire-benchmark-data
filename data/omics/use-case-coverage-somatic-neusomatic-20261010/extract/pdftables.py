"""Read the F1 tables of NeuSomatic 2022 Additional file 2 from `pdftotext -bbox` word boxes.

The column headers are rotated, so the layout text does not keep them in column order. Columns are fixed instead by
the x-centres of the numbers in the first data row, and each header word is assigned to the nearest column.
"""
import html, re, subprocess

TOOLS = ["VarDict", "SomaticSniper", "MuSE", "DRAGEN", "Octopus-RF", "Octopus-hard", "MuTect2", "Lancet", "Strelka2"]
MODELS = ["DREAM3", "SEQC-WGS-Spike", "SEQC-WGS-GT-50", "SEQC-WGS-GT50-SpikeWGS10"]
GROUPS = ["NeuSomatic-S", "NeuSomatic"]
ROW = re.compile(r"(WGS|SPP|LBP)_\S+|Average")
WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>')


def pages(pdf):
    out = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    return [[(float(a), float(b), float(c), float(d), html.unescape(e)) for a, b, c, d, e in WORD.findall(p)]
            for p in re.split(r"<page ", out)[1:]]


def table(words, label, next_label=None):
    """Return (columns, sections) for the table titled 'Table <label>' on this page."""
    def title_y(lab):
        for w in words:
            if w[4] == "Table" and any(abs(x[1] - w[1]) < 1 and x[4] == lab and w[2] < x[0] < w[2] + 10 for x in words):
                return w[1]
        return None
    y0 = title_y(label)
    assert y0 is not None, label
    y1 = title_y(next_label) if next_label else None
    ws = [w for w in words if w[1] > y0 + 1 and (y1 is None or w[1] < y1 - 1)]
    lines = {}
    for w in sorted(ws, key=lambda w: (w[1], w[0])):
        key = next((k for k in lines if abs(k - w[1]) < 1.5), w[1])
        lines.setdefault(key, []).append(w)
    data = [(y, sorted(l)) for y, l in sorted(lines.items()) if ROW.fullmatch(sorted(l)[0][4])]
    assert data, label
    first_y = data[0][0]
    cells = [w for w in data[0][1] if re.fullmatch(r"[\d.]+|-", w[4])]
    centres = [(w[0] + w[2]) / 2 for w in cells]
    assert len(centres) == 17, (label, len(centres))
    head = [w for w in ws if w[1] < first_y - 1]
    group_x = {}
    for g in GROUPS:
        hits = [w for w in head if w[4] == g]
        assert len(hits) == 1, (label, g, hits)
        group_x[g] = hits[0][0]
    cols = [None] * 17
    for w in head:
        if w[4] in TOOLS or w[4] in MODELS:
            c = (w[0] + w[2]) / 2
            i = min(range(17), key=lambda k: abs(centres[k] - c))
            assert abs(centres[i] - c) < 8, (label, w, centres[i])
            if w[4] in MODELS:
                grp = "NeuSomatic" if w[0] >= group_x["NeuSomatic"] - 3 else "NeuSomatic-S"
                assert w[0] >= group_x["NeuSomatic-S"] - 3, (label, w)
                name = f"{grp} {w[4]}"
            else:
                name = w[4]
            assert cols[i] is None, (label, i, cols[i], name)
            cols[i] = name
    assert None not in cols, (label, cols)
    marks = sorted((w[1], w[4]) for w in ws if w[4] in ("SNVs", "INDELs"))
    sections = {}
    for y, l in data:
        sec = [m for m in marks if m[0] < y]
        assert sec, (label, y)
        kind = sec[-1][1]
        texts = [w for w in l if not re.fullmatch(r"[\d.]+|-", w[4])]
        nums = [w for w in l if re.fullmatch(r"[\d.]+|-", w[4])]
        assert len(nums) == 17, (label, [w[4] for w in l])
        row = {}
        for w in nums:
            c = (w[0] + w[2]) / 2
            i = min(range(17), key=lambda k: abs(centres[k] - c))
            assert abs(centres[i] - c) < 6 and cols[i] not in row, (label, w)
            row[cols[i]] = w[4]
        sections.setdefault(kind, []).append(([w[4] for w in texts], row))
    return cols, sections
