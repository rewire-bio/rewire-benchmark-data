"""Deterministic parse of the HyInv technical report tables.

Reads the pinned PDF, checks its SHA-256, extracts the text layer with
pdftotext -layout, and returns the printed cells of the tables and the two
numeric figures the batch uses. Every row label and column count is asserted,
so a different PDF or a different poppler layout fails rather than producing
silently shifted values.

Usage: python3 parse.py <path to HyInv_Technical_Report.pdf>
"""

import hashlib
import re
import subprocess
import sys

PDF_SHA256 = "0f10b390be399c341d1f7497c5a3ca0ac857ce78172c4732bdc86a9c66e46419"

PANELS_ESMFOLD2 = ["CATH4.3 test", "CATH4.2 test", "TS500", "TS50", "RecentPDB"]
TABLE6_COLUMNS = PANELS_ESMFOLD2 + ["RecentPDB Boltz2", "RecentPDB Protenix2"]

DESIGNED_ROWS = [
    "HyInv",
    "ProteinZero V2 (ESM2)",
    "ProteinZero V2 (ESM1)",
    "ProteinMPNN grouped",
    "ProteinMPNN",
    "LigandMPNN",
    "ProteinMPNN (low-noise, grouped)",
    "PiFold",
    "LM-Design 650M",
    "CMLM",
    "DPLM-2 3B",
]
TABLE6_ROWS = DESIGNED_ROWS + ["Native"]
BASELINE_ROWS = DESIGNED_ROWS[1:]


def read_text(pdf_path):
    with open(pdf_path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    if digest != PDF_SHA256:
        raise SystemExit(f"PDF sha256 {digest} is not the pinned {PDF_SHA256}")
    text = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8")
    return text


PAGE_MARKERS = {
    "table1": "Table 1: Inference time",
    "figure4a": "Figure 4: Inference time of HyInv and the baselines",
    "table6": "Table 6: scTM of every method",
    "table7": "Table 7: HyInv minus baseline",
    "table8": "Table 8: Gain of the decoupled sampler",
    "table9": "Table 9: BF16 path against the reference sampler",
    "figure14": "Figure 14: scTM, recovery and diversity of every method",
    "figure15": "Figure 15: pLDDT, scRMSD and lDDT of every method",
    "table10": "Table 10: Homology screen of the application panels",
    "proteinmpnn_curve": "+0.0146",
    "rl_ablation": "RL raises scTM",
    "de_novo_yield": "0.68 unfiltered and 0.38 filtered",
}


def pages(text):
    """Page number of each marker, and the page count, read from the form feeds."""
    parts = [part for part in text.split("\f") if part.strip()]
    out = {"count": len(parts)}
    for key, marker in PAGE_MARKERS.items():
        hits = [index + 1 for index, part in enumerate(parts) if marker in part]
        assert len(hits) == 1, (key, marker, hits)
        out[key] = hits[0]
    return out


def numbers(line):
    """Printed numeric tokens of a line, keeping the printed string."""
    return re.findall(r"[+−-]?\d[\d,]*(?:\.\d+)?", line)


def clean(token):
    return token.replace(",", "").replace("−", "-")


def row_line(lines, start, label):
    """The first line at or after `start` whose stripped text begins with `label`."""
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith(label):
            return index, stripped
    raise AssertionError(f"row {label!r} not found after line {start}")


def find(lines, marker, start=0):
    for index in range(start, len(lines)):
        if marker in lines[index]:
            return index
    raise AssertionError(f"marker {marker!r} not found")


def exact_rows(lines, start, labels):
    """Rows in the given order, each matched by its exact label prefix.

    Longer labels that share a prefix with a shorter one (ProteinMPNN and
    ProteinMPNN grouped) are matched in the printed order, so a row is never
    read twice.
    """
    out = []
    cursor = start
    for label in labels:
        index, stripped = row_line(lines, cursor, label)
        out.append((label, stripped))
        cursor = index + 1
    return out


def table1(lines):
    """Table 1: inference time. 5 systems x (148 res ms, 402 res ms, 10,000 s, speed-up)."""
    head = find(lines, "Table 1: Inference time.")
    assert "128 designs (ms)" in lines[head + 2] and "Speed-up" in lines[head + 2]
    assert "148 res." in lines[head + 3] and "vs ProteinMPNN" in lines[head + 3]
    labels = [
        "ProteinMPNN",
        "ProteinZero V2",
        "HyInv, FP32 reference sampler",
        "HyInv, exact FP32 path",
        "HyInv (BF16)",
    ]
    out = {}
    for offset, label in enumerate(labels):
        stripped = lines[head + 4 + offset].strip()
        assert stripped.startswith(label), (label, stripped)
        tail = stripped[len(label):]
        values = numbers(tail)
        speedup = re.search(r"([\d.]+)×", tail)
        if label == "ProteinMPNN":
            assert tail.rstrip().endswith("–"), tail
            assert len(values) == 3, values
            out[label] = {"ms_148": values[0], "ms_402": values[1], "s_10000": values[2]}
        else:
            assert speedup, tail
            assert len(values) == 4, values
            out[label] = {
                "ms_148": values[0],
                "ms_402": values[1],
                "s_10000": values[2],
                "speedup": speedup.group(1) + "×",
            }
    assert out["HyInv (BF16)"]["ms_402"] == "50.6"
    assert out["ProteinMPNN"]["ms_402"] == "2,907"
    return out


def figure4a(lines):
    """Figure 4a: time to design 128 sequences for a 402-residue backbone."""
    head = find(lines, "a Time to design 128 sequences (402 residues)")
    caption = find(lines, "Figure 4: Inference time of HyInv and the baselines.", head)
    labels = [
        "HyInv (BF16)",
        "HyInv, exact FP32 path",
        "HyInv reference sampler",
        "CMLM",
        "ProteinMPNN",
        "ProteinZero V2 (ESM2)",
        "ProteinZero V2 (ESM1)",
        "PiFold",
        "ProteinMPNN (low-noise, grouped)",
        "ProteinMPNN grouped",
        "LM-Design 650M",
        "LigandMPNN",
        "DPLM-2 3B",
    ]
    out = {}
    cursor = head
    for label in labels:
        index, stripped = row_line(lines, cursor, label)
        assert index < caption, (label, index)
        match = re.search(r"([\d,.]+)\s*(ms|s)\b", stripped[len(label):])
        assert match, stripped
        out[label] = {"value": match.group(1), "unit": match.group(2)}
        cursor = index + 1
    assert out["HyInv (BF16)"] == {"value": "50.6", "unit": "ms"}
    assert out["DPLM-2 3B"] == {"value": "996", "unit": "s"}
    return out


def table6(lines):
    """Table 6: scTM of every method on every panel and predictor."""
    head = find(lines, "Table 6: scTM of every method.")
    out = {}
    for label, stripped in exact_rows(lines, head, TABLE6_ROWS):
        values = numbers(stripped[len(label):])
        assert len(values) == 7, (label, values)
        for name, value in zip(TABLE6_COLUMNS, values):
            assert re.fullmatch(r"0\.\d{4}", value), (label, name, value)
            out[(label, name)] = value
    assert out[("HyInv", "CATH4.3 test")] == "0.8399"
    assert out[("Native", "RecentPDB Protenix2")] == "0.8419"
    return out


def table7(lines):
    """Table 7: HyInv minus baseline, scTM, in units of 1e-3 with a 95% interval."""
    head = find(lines, "Table 7: HyInv minus baseline, scTM.")
    blocks = [
        (["CATH4.3 test", "CATH4.2 test", "TS500"], head),
        (["TS50", "RecentPDB", "RecentPDB Boltz2"], None),
        (["RecentPDB Protenix2"], None),
    ]
    out = {}
    cursor = head
    for columns, _ in blocks:
        rows = exact_rows(lines, cursor, BASELINE_ROWS)
        for label, stripped in rows:
            cells = re.findall(
                r"([+−-]?[\d.]+)\s*\[\s*([+−-]?[\d.]+),\s*([+−-]?[\d.]+)\s*\]",
                stripped[len(label):],
            )
            assert len(cells) == len(columns), (label, columns, cells)
            for name, (point, lower, upper) in zip(columns, cells):
                out[(label, name)] = {
                    "printed": f"{point} [{lower}, {upper}]",
                    "value": clean(point),
                    "lower": clean(lower),
                    "upper": clean(upper),
                }
        cursor = row_line(lines, cursor, BASELINE_ROWS[-1])[0] + 1
    assert len(out) == 70, len(out)
    assert out[("ProteinMPNN", "CATH4.3 test")]["value"] == "+13.6"
    assert out[("DPLM-2 3B", "RecentPDB Protenix2")]["value"] == "+78.3"
    return out


def table8(lines):
    """Table 8: gain of the decoupled sampler over the unmodified sampler at equal diversity."""
    head = find(lines, "Table 8: Gain of the decoupled sampler")
    labels = [
        "Decoupled draft, Td = 0.6 (HyInv default)",
        "Decoupled draft, Td = 0.3",
        "Top-p 0.9",
        "Min-p 0.1",
    ]
    columns = ["Development", "CATH4.3 test", "RecentPDB"]
    out = {}
    for label, stripped in exact_rows(lines, head, labels):
        cells = re.findall(
            r"([+−-][\d.]+)\s*\[\s*([+−-][\d.]+),\s*([+−-][\d.]+)\s*\]",
            stripped[len(label):],
        )
        assert len(cells) == 3, (label, cells)
        for name, (point, lower, upper) in zip(columns, cells):
            out[(label, name)] = {
                "printed": f"{point} [{lower}, {upper}]",
                "value": clean(point),
                "lower": clean(lower),
                "upper": clean(upper),
            }
    assert out[("Decoupled draft, Td = 0.6 (HyInv default)", "CATH4.3 test")]["value"] == "+0.0078"
    return out


def table9(lines):
    """Table 9: BF16 path against the reference sampler on the development panel."""
    head = find(lines, "Table 9: BF16 path against the reference sampler")
    labels = ["Subset 1", "Subset 2", "Subset 3", "Whole development panel"]
    out = {}
    for label, stripped in exact_rows(lines, head, labels):
        tail = stripped[len(label):]
        match = re.search(
            r"([+−-][\d.]+)\s*\[\s*([+−-][\d.]+),\s*([+−-][\d.]+)\s*\]", tail
        )
        assert match, stripped
        # The whole-panel row prints its chain count as "1 529" (space as the
        # thousands separator), so digit groups are joined before counting.
        prefix = re.sub(r"(?<=\d) (?=\d{3}\b)", "", tail.split(match.group(0))[0])
        counts = numbers(prefix)
        assert len(counts) == 2, (label, counts)
        flag = tail.split(match.group(0))[1].strip()
        assert flag in ("yes", "no"), (label, flag)
        out[label] = {
            "targets": clean(counts[0]),
            "clusters": clean(counts[1]),
            "printed": f"{match.group(1)} [{match.group(2)}, {match.group(3)}]",
            "value": clean(match.group(1)),
            "lower": clean(match.group(2)),
            "upper": clean(match.group(3)),
            "lower_end_above_margin": flag,
        }
    assert out["Whole development panel"]["targets"] == "1529"
    assert out["Whole development panel"]["value"] == "-0.0001"
    return out


def figure14(lines):
    """Figure 14: scTM, recovery and diversity on the five ESMFold2 panels."""
    head = find(lines, "scTM ↑")
    assert "Recovery" in lines[head] and "Diversity" in lines[head]
    out = {"sctm": {}, "recovery": {}, "diversity": {}}
    for label, stripped in exact_rows(lines, head, TABLE6_ROWS):
        values = numbers(stripped[len(label):])
        if label == "Native":
            assert len(values) == 5, values
            assert stripped.count("–") == 10, stripped
            blocks = [values]
            keys = ["sctm"]
        else:
            assert len(values) == 15, (label, values)
            blocks = [values[0:5], values[5:10], values[10:15]]
            keys = ["sctm", "recovery", "diversity"]
        for key, block in zip(keys, blocks):
            for name, value in zip(PANELS_ESMFOLD2, block):
                assert re.fullmatch(r"0\.\d{3}", value), (label, key, name, value)
                out[key][(label, name)] = value
    assert out["diversity"][("HyInv", "CATH4.3 test")] == "0.331"
    assert out["diversity"][("DPLM-2 3B", "CATH4.3 test")] == "0.000"
    return out


def figure15(lines):
    """Figure 15: pLDDT, scRMSD and lDDT on the five ESMFold2 panels."""
    head = find(lines, "pLDDT ↑")
    assert "scRMSD (Å) ↓" in lines[head] and "lDDT ↑" in lines[head]
    out = {"plddt": {}, "scrmsd": {}, "lddt": {}}
    for label, stripped in exact_rows(lines, head, TABLE6_ROWS):
        values = numbers(stripped[len(label):])
        assert len(values) == 15, (label, values)
        for key, block in zip(
            ["plddt", "scrmsd", "lddt"], [values[0:5], values[5:10], values[10:15]]
        ):
            for name, value in zip(PANELS_ESMFOLD2, block):
                out[key][(label, name)] = value
    for (label, name), value in out["plddt"].items():
        assert re.fullmatch(r"\d\d\.\d", value), (label, name, value)
    for (label, name), value in out["scrmsd"].items():
        assert re.fullmatch(r"\d\.\d\d", value), (label, name, value)
    for (label, name), value in out["lddt"].items():
        assert re.fullmatch(r"0\.\d{3}", value), (label, name, value)
    assert out["plddt"][("HyInv", "CATH4.3 test")] == "83.3"
    assert out["scrmsd"][("Native", "RecentPDB")] == "5.53"
    return out


def table2_crosscheck(lines, t6, f14):
    """Table 2 prints a three-method subset at 3 decimal places. Assert it agrees."""
    head = find(lines, "Table 2: HyInv and the two reference baselines")
    labels = ["HyInv", "ProteinZero V2", "ProteinMPNN"]
    blocks = {}
    cursor = head
    for block in ["scTM", "sctm difference", "Sequence diversity", "Native sequence recovery"]:
        rows = exact_rows(lines, cursor, labels if block != "sctm difference" else labels[1:])
        blocks[block] = {label: numbers(stripped[len(label):]) for label, stripped in rows}
        cursor = row_line(lines, cursor, (labels if block != "sctm difference" else labels[1:])[-1])[0] + 1
    alias = {"ProteinZero V2": "ProteinZero V2 (ESM2)"}
    for block, metric in [
        ("scTM", "sctm"),
        ("Sequence diversity", "diversity"),
        ("Native sequence recovery", "recovery"),
    ]:
        for label, values in blocks[block].items():
            assert len(values) == 5, (block, label, values)
            row = alias.get(label, label)
            for name, value in zip(PANELS_ESMFOLD2, values):
                assert f14[metric][(row, name)] == value, (block, row, name, value)
    for label, values in blocks["scTM"].items():
        row = alias.get(label, label)
        for name, value in zip(PANELS_ESMFOLD2, values):
            assert rounds_to(t6[(row, name)], value), (row, name, value)
    return blocks


def rounds_to(four_places, three_places):
    """The 4-dp cell rounds to the 3-dp cell, either way at a half."""
    return abs(float(four_places) - float(three_places)) <= 0.0005 + 1e-9


def figure14_sctm_crosscheck(t6, f14):
    for (label, name), value in f14["sctm"].items():
        assert rounds_to(t6[(label, name)], value), (label, name, value)


def parse(pdf_path):
    text = read_text(pdf_path)
    lines = text.split("\n")
    page = pages(text)
    t6 = table6(lines)
    f14 = figure14(lines)
    figure14_sctm_crosscheck(t6, f14)
    table2_crosscheck(lines, t6, f14)
    data = {
        "table1": table1(lines),
        "figure4a": figure4a(lines),
        "table6": t6,
        "table7": table7(lines),
        "table8": table8(lines),
        "table9": table9(lines),
        "figure14": f14,
        "figure15": figure15(lines),
        "pages": page,
    }
    # Figure 4a repeats five of Table 1's 402-residue cells.
    repeats = {
        "HyInv (BF16)": "HyInv (BF16)",
        "HyInv, exact FP32 path": "HyInv, exact FP32 path",
        "HyInv reference sampler": "HyInv, FP32 reference sampler",
        "ProteinMPNN": "ProteinMPNN",
        "ProteinZero V2 (ESM2)": "ProteinZero V2",
    }
    for figure_label, table_label in repeats.items():
        assert data["figure4a"][figure_label]["unit"] == "ms"
        assert (
            data["figure4a"][figure_label]["value"] == data["table1"][table_label]["ms_402"]
        ), figure_label
    # Section 3.2 and Section 4 repeat three cells of Tables 8 and 9.
    body = " ".join(lines)
    assert "+0.0078 on CATH4.3 test and +0.0131 on RecentPDB" in body
    assert data["table8"][("Decoupled draft, Td = 0.6 (HyInv default)", "CATH4.3 test")]["value"] == "+0.0078"
    assert data["table8"][("Decoupled draft, Td = 0.6 (HyInv default)", "RecentPDB")]["value"] == "+0.0131"
    assert "differs from the reference sampler by −0.0001" in body
    return data


if __name__ == "__main__":
    import json

    def plain(value):
        if isinstance(value, dict):
            return {" | ".join(k) if isinstance(k, tuple) else k: plain(v) for k, v in value.items()}
        return value

    print(json.dumps(plain(parse(sys.argv[1])), indent=1))
