"""Deterministic parse of the HyPLM technical report tables.

Reads the pinned PDF, checks its SHA-256, extracts the text layer with
pdftotext -layout, and returns the printed cells of Tables 2, 3, 5, 6 and 7,
the bar labels of Figure 3a and the numbers the report prints in prose. Every
row label, metric label and cell count is asserted, the page of every table is
read from the form feeds, and every value the source prints twice is asserted
equal in both places.

Usage: python3 -I parse.py <path to HyPLM_Technical_Report.pdf>
"""

import hashlib
import re
import subprocess
import sys

PDF_SHA256 = "d81d88a415a91c2b00d8e97513a90c03ccffd857ec75033fa7de77227dea1710"

TASKS = [
    # (row label in Tables 6 and 7, metric label printed beside it)
    ("ProteinGym zero-shot", "Spearman ρ"),
    ("NLL, held-out UniRef panel", "NLL"),
    ("NLL, recent PDB chains", "NLL"),
    ("Secondary structure (CB513)", "Q3 accuracy"),
    ("Contacts, ProteinNet", "P@L/5, long range"),
    ("Contacts, CASP14", "P@L/5, long range"),
    ("Contacts, CASP15", "P@L/5, long range"),
    ("Remote homology (fold)", "accuracy"),
    ("EC, SaProt split", "Fmax"),
    ("EC, DeepFRI split", "Fmax"),
    ("GO-MF", "Fmax"),
    ("GO-BP", "Fmax"),
    ("GO-CC", "Fmax"),
    ("EC classification (DGEB)", "macro F1"),
    ("Arch retrieval (DGEB)", "MAP@5"),
    ("Localization, 10-class", "accuracy"),
    ("Localization, binary", "accuracy"),
    ("Metal-ion binding", "accuracy"),
    ("HumanPPI", "accuracy"),
    ("AAV two-vs-many", "Spearman ρ"),
    ("AAV low-vs-high", "Spearman ρ"),
    ("GB1 two-vs-rest", "Spearman ρ"),
    ("GB1 three-vs-rest", "Spearman ρ"),
    ("GB1 low-vs-high", "Spearman ρ"),
    ("Meltome human cell", "Spearman ρ"),
    ("Meltome mixed", "Spearman ρ"),
    ("Amylase one-to-many", "Spearman ρ"),
    ("Amylase by mutation count", "Spearman ρ"),
    ("Hydrolase to P06241", "Spearman ρ"),
    ("Fluorescence", "Spearman ρ"),
    ("Stability", "Spearman ρ"),
    ("Thermostability", "Spearman ρ"),
]
TABLE6_MODELS = ["ESM-2 650M", "ESM-1b", "ESM C 600M", "E1-600M", "AMPLIFY-350M",
                 "DPLM-650M", "HyPLM-Flash"]
TABLE7_MODELS = ["ESM3-open", "ProtBERT", "ProtT5-XL", "Ankh-base", "Ankh3-large",
                 "xTrimoPGLM-1B"]
TABLE3_MODELS = ["ESM-2 650M", "ESM C 600M", "E1-600M", "AMPLIFY-350M", "DPLM-650M",
                 "ProtBERT", "ESM-2 3B", "ESM-2 15B", "ESM C 6B", "HyPLM-Flash"]
TABLE5_ROWS = ["VespaG", "VESPA", "DPLM-3B†", "E1-600M†", "E1-300M†",
               "ESM2 (650M)", "DPLM-650M†", "HyPLM-Flash†", "ESM C 6B†",
               "ESM-1v (ensemble)", "ESM-C (300M)", "ESM2 (3B)", "ESM-C (600M)", "E1-150M†"]
TABLE5_COLUMNS = ["Activity", "Binding", "Expression", "Organismal fitness", "Stability",
                  "Average"]
FIGURE3A = ["DPLM-3B", "E1-600M", "E1-300M", "ESM-2 650M", "DPLM-650M", "HyPLM-Flash",
            "ESM C 6B", "ESM3-open", "ESM-2 3B", "ESM C 300M", "ESM C 600M", "ESM-2 15B",
            "E1-150M", "ESM-1b", "ESM-2 150M", "AMPLIFY-350M", "ProtBERT"]
TABLE2_MODELS = ["ESM-2 650M", "ESM C 600M", "E1-600M", "DPLM-650M", "ESM-1b",
                 "AMPLIFY-350M", "ESM3-open", "HyPLM-Flash"]
TABLE2_TASKS = ["Secondary structure (CB513)", "Contacts, ProteinNet", "Remote homology (fold)",
                "EC, SaProt split", "GO-MF", "Localization, 10-class", "AAV two-vs-many",
                "Amylase one-to-many", "Fluorescence", "Meltome mixed", "Stability"]
# The ten regression splits Appendix A uses for summary statistics: all thirteen
# regression rows except GB1 two-vs-rest, GB1 three-vs-rest and the hydrolase split.
REGRESSION_TEN = ["AAV two-vs-many", "AAV low-vs-high", "GB1 low-vs-high", "Meltome human cell",
                  "Meltome mixed", "Amylase one-to-many", "Amylase by mutation count",
                  "Fluorescence", "Stability", "Thermostability"]

PAGE_MARKERS = {
    "table1": "Table 1: Training data and compute",
    "table2": "Table 2: Frozen-representation tasks",
    "table3": "Table 3: Masked-residue likelihood",
    "table4": "Table 4: Evaluation tasks",
    "table5": "Table 5: Top of the ProteinGym zero-shot leaderboard",
    "table6": "Table 6: All tasks, part 1",
    "table7": "Table 7: All tasks, part 2",
    "figure3": "Figure 3: ProteinGym zero-shot fitness prediction",
    "section3": "the engine embeds 131,000 residues per second",
    "section41": "Its differences to ESM-2 650M",
    "section42": "Averaged over the ten regression splits",
    "appendixA": "A    Evaluation Protocols",
}

VALUE = r"[−-]?\d\.\d{3}"


def read_text(pdf_path):
    with open(pdf_path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    if digest != PDF_SHA256:
        raise SystemExit(f"PDF sha256 {digest} is not the pinned {PDF_SHA256}")
    return subprocess.run(["pdftotext", "-layout", pdf_path, "-"], check=True,
                          capture_output=True).stdout.decode("utf-8")


def clean(token):
    return token.replace(",", "").replace("−", "-")


def find(lines, marker, start=0):
    for index in range(start, len(lines)):
        if marker in lines[index]:
            return index
    raise AssertionError(f"marker {marker!r} not found")


def row(lines, start, label, pattern=None):
    """First line at or after `start` that begins with `label` (and matches pattern)."""
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith(label) and (pattern is None or re.search(pattern, stripped)):
            return index, stripped
    raise AssertionError(f"row {label!r} not found after line {start}")


def pages(text):
    parts = [part for part in text.split("\f") if part.strip()]
    out = {"count": len(parts)}
    for key, marker in PAGE_MARKERS.items():
        hits = [i + 1 for i, part in enumerate(parts) if marker in part]
        assert len(hits) == 1, (key, marker, hits)
        out[key] = hits[0]
    return out


def task_table(lines, caption, models, dashes_allowed):
    head = find(lines, caption)
    header = row(lines, head, "Task")[1]
    for model in models:
        assert model in header, (caption, model)
    out = {}
    cursor = head
    for label, metric in TASKS:
        index, stripped = row(lines, cursor, label, VALUE)
        tail = stripped[len(label):].strip()
        assert tail.startswith(metric), (label, metric, tail)
        cells = re.findall(VALUE + "|–", tail[len(metric):])
        assert len(cells) == len(models), (label, cells)
        for model, cell in zip(models, cells):
            if cell == "–":
                assert dashes_allowed, (label, model)
                continue
            out[(label, model)] = cell
        cursor = index + 1
    return out


def table3(lines):
    head = find(lines, "Table 3: Masked-residue likelihood")
    out = {}
    cursor = head
    for model in TABLE3_MODELS:
        index, stripped = row(lines, cursor, model, r"\d\.\d{3}")
        values = re.findall(r"\d\.\d{2,3}", stripped[len(model):])
        assert len(values) == 4, (model, values)
        nll_u, ppl_u, nll_p, ppl_p = values
        assert re.fullmatch(r"\d\.\d{3}", nll_u) and re.fullmatch(r"\d\.\d{3}", nll_p)
        assert re.fullmatch(r"\d\.\d{2}", ppl_u) and re.fullmatch(r"\d\.\d{2}", ppl_p)
        out[model] = {"nll_uniref": nll_u, "ppl_uniref": ppl_u,
                      "nll_pdb": nll_p, "ppl_pdb": ppl_p}
        cursor = index + 1
    return out


def table5(lines):
    head = find(lines, "Table 5: Top of the ProteinGym zero-shot leaderboard")
    out = {}
    cursor = head
    for label in TABLE5_ROWS:
        for i in range(cursor, len(lines)):
            m = re.match(r"\s*(\d+)\s+(.+?)\s{2,}(\d\.\d{3}(?:\s+\d\.\d{3}){5})\s*$", lines[i])
            if m and m.group(2) == label:
                index, rank, values = i, m.group(1), m.group(3).split()
                break
        else:
            raise AssertionError(f"Table 5 row {label!r} not found")
        out[label] = {"rank": rank, **dict(zip(TABLE5_COLUMNS, values))}
        cursor = index + 1
    assert out["HyPLM-Flash†"]["Average"] == "0.409"
    assert out["HyPLM-Flash†"]["rank"] == "8"
    return out


def figure3a(lines):
    head = find(lines, "a Zero-shot fitness, single-sequence PLMs")
    caption = find(lines, "Figure 3: ProteinGym zero-shot fitness prediction", head)
    bars = []
    for i in range(head, caption):
        m = re.match(r"\s*(\S.*?)\s{2,}(0\.\d{3})\b", lines[i])
        if m:
            bars.append((m.group(1), m.group(2)))
    assert [label for label, _ in bars] == FIGURE3A, bars
    return dict(bars)


def table2(lines):
    head = find(lines, "Table 2: Frozen-representation tasks")
    out = {}
    cursor = head
    for model in TABLE2_MODELS:
        index, stripped = row(lines, cursor, model, VALUE)
        cells = re.findall(VALUE, stripped[len(model):])
        assert len(cells) == len(TABLE2_TASKS), (model, cells)
        for task, cell in zip(TABLE2_TASKS, cells):
            out[(task, model)] = cell
        cursor = index + 1
    return out


def prose(text):
    body = re.sub(r"\s+", " ", text)
    out = {}
    m = re.search(r"On a common workload of 2,048 held-out proteins, the engine embeds "
                  r"([\d,]+) residues per second on one H20", body)
    assert m, "throughput sentence"
    out["throughput_int8"] = m.group(1)
    m = re.search(r"BF16 mode of the engine, which runs at ([\d,]+) residues per second", body)
    out["throughput_bf16"] = m.group(1)
    diffs = re.search(
        r"Its differences to ESM-2 650M \((\S+), 95% confidence interval \[(\S+), (\S+)\]\), "
        r"ESM C 600M \((\S+), \[(\S+), (\S+)\]\), DPLM-650M \((\S+), \[(\S+), (\S+)\]\) and "
        r"E1-600M \((\S+), \[(\S+), (\S+)\]\) are not significant", body)
    assert diffs, "paired-difference sentence"
    g = diffs.groups()
    out["paired"] = {
        model: {"value": g[3 * k], "lower": g[3 * k + 1], "upper": g[3 * k + 2]}
        for k, model in enumerate(["ESM-2 650M", "ESM C 600M", "DPLM-650M", "E1-600M"])
    }
    reg = re.search(r"Averaged over the ten regression splits used for summary statistics "
                    r"\(Appendix A\), it scores (\S+), the highest of these models, ahead of "
                    r"E1-600M \((\S+)\), ESM C 600M \((\S+)\), ESM-2 650M \((\S+)\) and the 4\.4 "
                    r"times larger ESM-2 3B \((\S+)\)\.", body)
    assert reg, "regression-average sentence"
    out["regression_average"] = dict(zip(
        ["HyPLM-Flash", "E1-600M", "ESM C 600M", "ESM-2 650M", "ESM-2 3B"], reg.groups()))
    ss = re.search(r"exceeded only by ESM3-open \((\S+)\) and ESM C 6B \((\S+)\) among all models",
                   body)
    assert ss, "secondary-structure sentence"
    out["ss_esm3_open"], out["ss_esm_c_6b"] = ss.groups()
    assert "0.406 on organismal fitness" in body
    assert "a precision at L/5 of 0.650 on ProteinNet, against 0.392 for ESM-2 650M, 0.434 for " \
           "ESM C 600M and 0.645 for E1-600M" in body
    assert "(1.148 against 1.327 and 1.162)" in body
    assert "reproduce the leaderboard to within 0.0025" in body
    return out


def parse(pdf_path):
    text = read_text(pdf_path)
    lines = text.split("\n")
    t6 = task_table(lines, "Table 6: All tasks, part 1", TABLE6_MODELS, dashes_allowed=False)
    t7 = task_table(lines, "Table 7: All tasks, part 2", TABLE7_MODELS, dashes_allowed=True)
    assert len(t6) == 224 and len(t7) == 180, (len(t6), len(t7))
    cells = {**t6, **t7}
    data = {
        "tasks": cells,
        "table3": table3(lines),
        "table5": table5(lines),
        "figure3a": figure3a(lines),
        "prose": prose(text),
        "pages": pages(text),
    }

    # Table 2 is a subset of Tables 6 and 7.
    for key, value in table2(lines).items():
        assert cells[key] == value, ("Table 2", key, value, cells.get(key))
    # Table 3 NLL repeats Tables 6 and 7 for the models those tables hold.
    for model, row_ in data["table3"].items():
        for column, task in [("nll_uniref", "NLL, held-out UniRef panel"),
                             ("nll_pdb", "NLL, recent PDB chains")]:
            if (task, model) in cells:
                assert cells[(task, model)] == row_[column], (model, column)
    # Figure 3a and the Table 5 averages repeat the ProteinGym cells they share.
    for label, value in data["figure3a"].items():
        if ("ProteinGym zero-shot", label) in cells:
            assert cells[("ProteinGym zero-shot", label)] == value, label
        dagger = label + "†"
        if dagger in data["table5"]:
            assert data["table5"][dagger]["Average"] == value, label
    # The printed paired differences equal the differences of the printed scores.
    hy = float(cells[("ProteinGym zero-shot", "HyPLM-Flash")])
    for model, d in data["prose"]["paired"].items():
        assert abs(hy - float(cells[("ProteinGym zero-shot", model)]) - float(clean(d["value"]))) \
            < 1e-9, model
    # The regression averages equal the mean of the ten splits for the models Table 6 holds.
    for model, value in data["prose"]["regression_average"].items():
        if model == "ESM-2 3B":
            continue
        mean = sum(float(cells[(t, model)]) for t in REGRESSION_TEN) / len(REGRESSION_TEN)
        assert abs(mean - float(value)) <= 0.0005 + 1e-9, (model, mean, value)
    assert data["prose"]["ss_esm3_open"] == cells[("Secondary structure (CB513)", "ESM3-open")]
    return data


if __name__ == "__main__":
    import json

    def plain(value):
        if isinstance(value, dict):
            return {" | ".join(k) if isinstance(k, tuple) else k: plain(v) for k, v in value.items()}
        return value

    print(json.dumps(plain(parse(sys.argv[1])), indent=1, ensure_ascii=False))
