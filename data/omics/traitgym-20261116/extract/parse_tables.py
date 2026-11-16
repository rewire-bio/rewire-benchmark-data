#!/usr/bin/env python3
"""Parse the printed tables of the TraitGym preprint into TSVs.

Input: the ``pdftotext -layout`` text layer of the bioRxiv v2 PDF
(https://www.biorxiv.org/content/10.1101/2025.02.11.637758v2.full.pdf).

bioRxiv stamps every download, so the PDF bytes differ between retrievals and the
PDF SHA-256 on the source record pins one retrieval only. The text layer is stable
across retrievals, so this script asserts the text layer's SHA-256 instead.

Every table is parsed by splitting body lines on runs of two or more spaces, with the
expected row labels, column headers and cell counts asserted. Nothing is read from a
figure. Usage:

    python3 extract/parse_tables.py <paper.txt> [--out extract]
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

TEXT_SHA256 = "23ae4d67751f1092e5cc2da66b52091fa9bbc3ec59310f06bc65be28f93c5097"

SPLIT = re.compile(r"\s{2,}")
NUMBER = re.compile(r"^\d+(?:\.\d+)?$")


def cells(line: str) -> list[str]:
    return [c for c in SPLIT.split(line.strip()) if c]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def body(lines: list[str], caption: str, first: str, count: int) -> list[list[str]]:
    """Split the table that follows `caption` into cells.

    `caption` must occur on exactly one line. `first` is a substring of the table's
    first line (its column header), which separates the table from a caption that
    wraps onto further lines. `count` non-blank lines are then taken, starting at
    that first line, and the count is asserted.
    """
    starts = [i for i, line in enumerate(lines) if caption in line]
    require(len(starts) == 1, f"expected one line containing {caption!r}, found {len(starts)}")
    heads = [i for i, line in enumerate(lines[starts[0]:starts[0] + 12], starts[0]) if first in line]
    require(len(heads) == 1,
            f"expected one line containing {first!r} just after {caption!r}, found {len(heads)}")
    out: list[list[str]] = []
    i = heads[0]
    while len(out) < count:
        require(i < len(lines), f"ran out of lines after {caption!r}")
        if lines[i].strip():
            out.append(cells(lines[i]))
        i += 1
    return out


# ---------------------------------------------------------------- Table 1

def table_1(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table 1: Number of variants and traits in TraitGym.", "Dataset", 3)
    require(rows[0] == ["Dataset", "Putatively causal variants", "Total variants", "Traits"],
            f"Table 1 header: {rows[0]}")
    out = []
    for expected, row in zip(("Mendelian traits", "Complex traits"), rows[1:]):
        require(row[0] == expected, f"Table 1 row label: {row}")
        require(len(row) == 4, f"Table 1 row width: {row}")
        out.append({"dataset": row[0], "causal_variants": row[1],
                    "total_variants": row[2], "traits": row[3]})
    return out


# ---------------------------------------------------------------- Table 2

TABLE_2_MODELS = ("Enformer", "Sei", "Borzoi", "GPN-MSA", "NT", "HyenaDNA", "Caduceus",
                  "SpeciesLM", "AIDO.DNA", "Evo2", "GPN-Promoter", "CADD", "phastCons", "phyloP")


def table_2(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table 2: Benchmarked models.", "Dependencies", 23)
    out: list[dict[str, str]] = []
    for row in rows:
        if not row:
            continue
        # The GPN-Promoter row prints its first "No" one space after the model name,
        # so split that first cell on the model name rather than on whitespace.
        if row[0] not in TABLE_2_MODELS:
            head = row[0].split()
            if len(head) == 2 and head[0] in TABLE_2_MODELS:
                row = [head[0], head[1]] + row[1:]
            else:
                continue
        require(len(row) == 8, f"Table 2 row width: {row}")
        out.append({"model": row[0], "functional_genomics": row[1], "alignment": row[2],
                    "population_data": row[3], "params": row[4], "context_size": row[5],
                    "extracted_features": row[6], "source": row[7]})
    require([r["model"] for r in out] == list(TABLE_2_MODELS),
            f"Table 2 models: {[r['model'] for r in out]}")
    return out


# ---------------------------------------------------------------- Table 4

TABLE_4_ROWS = (
    ("Mendelian traits", "Alignment", "ZooVerPhyloP", "0.673", "Conservation in mammals"),
    ("Mendelian traits", "Functional genomics", "EncodetotalRNA-max", "0.348", "Max. RNA-seq level"),
    ("Mendelian traits", "Population data", "(-) Freq100bp", "0.509", "# common variants within 100bp"),
    ("Complex traits", "Alignment", "ZooPriPhyloP", "0.225", "Conservation in primates"),
    ("Complex traits", "Functional genomics", "EncodeDNase-max", "0.145", "Max. DNase-seq level"),
    ("Complex traits", "Population data", "(-) Freq10000bp", "0.131", "# common variants within 10kb"),
)


def table_4(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table 4: Top CADD features in different categories.", "Dataset", 7)
    require(rows[0] == ["Dataset", "Category", "Feature", "AUPRC", "Description"],
            f"Table 4 header: {rows[0]}")
    dataset = ""
    out = []
    for row in rows[1:]:
        if len(row) == 5:
            dataset = row[0]
            category, feature, auprc, description = row[1:]
        else:
            require(len(row) == 4, f"Table 4 row width: {row}")
            category, feature, auprc, description = row
        require(NUMBER.match(auprc), f"Table 4 AUPRC not numeric: {row}")
        out.append({"dataset": dataset, "category": category, "feature": feature,
                    "auprc": auprc, "description": description})
    require(tuple(tuple(r.values()) for r in out) == TABLE_4_ROWS, f"Table 4 cells: {out}")
    return out


# ---------------------------------------------------------------- Table 5

TABLE_5_TRAITS = ("Beta-thalassemia", "Hemophilia B", "Hypercholesterolemia-1",
                  "Monocyte count", "Hemoglobin A1c", "High density lipoprotein cholesterol")


def table_5(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table 5: Top three tissue/cell types for different traits", "Tissue/cell type/cell line", 21)
    require(rows[0] == ["Trait", "Tissue/cell type/cell line", "AUPRC"], f"Table 5 header: {rows[0]}")
    dataset = ""
    trait = ""
    rank = 0
    out = []
    for row in rows[1:]:
        if len(row) == 1:
            require(row[0] in ("Mendelian traits", "Complex traits"), f"Table 5 group: {row}")
            dataset = row[0]
            continue
        if len(row) == 3:
            trait, tissue, auprc = row
            rank = 1
        else:
            require(len(row) == 2, f"Table 5 row width: {row}")
            tissue, auprc = row
            rank += 1
        require(NUMBER.match(auprc), f"Table 5 AUPRC not numeric: {row}")
        out.append({"dataset": dataset, "trait": trait, "tissue": tissue,
                    "rank": str(rank), "auprc": auprc})
    require(len(out) == 18, f"Table 5 cells: {len(out)}")
    require(tuple(dict.fromkeys(r["trait"] for r in out)) == TABLE_5_TRAITS,
            f"Table 5 traits: {[r['trait'] for r in out]}")
    require(all(r["rank"] in ("1", "2", "3") for r in out), "Table 5 ranks")
    return out


# ---------------------------------------------------------------- Table S4

TABLE_S4_ROWS = (
    ("Mendelian traits", "(-) TSS distance", "0.115"),
    ("Complex traits", "(-) TSS distance", "0.104"),
    ("Complex traits", "MAF", "0.101"),
    ("Complex traits", "(-) LD score", "0.104"),
)


def table_s4(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table S4: Global AUPRC of matched features", "Dataset", 5)
    require(rows[0] == ["Dataset", "Feature", "AUPRC"], f"Table S4 header: {rows[0]}")
    out = []
    for row in rows[1:]:
        require(len(row) == 3, f"Table S4 row width: {row}")
        require(NUMBER.match(row[2]), f"Table S4 AUPRC not numeric: {row}")
        out.append({"dataset": row[0], "feature": row[1], "auprc": row[2]})
    require(tuple(tuple(r.values()) for r in out) == TABLE_S4_ROWS, f"Table S4 cells: {out}")
    return out


# ---------------------------------------------------------------- Table S5

def table_s5(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table S5: Hugging Face Hub models.", "Hugging Face Hub path", 7)
    require(rows[0] == ["Model", "Hugging Face Hub path"], f"Table S5 header: {rows[0]}")
    out = []
    for row in rows[1:]:
        require(len(row) == 2, f"Table S5 row width: {row}")
        out.append({"model": row[0], "hub_path": row[1]})
    require([r["model"] for r in out] ==
            ["GPN-MSA", "NT", "HyenaDNA", "Caduceus", "SpeciesLM", "AIDO.DNA"],
            f"Table S5 models: {out}")
    return out


# ---------------------------------------------------------------- Table S6

def table_s6(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table S6: GPN-Promoter training hyperparameters", "Window size", 13)
    out = []
    for row in rows:
        require(len(row) == 2, f"Table S6 row width: {row}")
        out.append({"hyperparameter": row[0], "value": row[1]})
    require(out[0] == {"hyperparameter": "Window size", "value": "512"}, f"Table S6 first row: {out[0]}")
    return out


# ---------------------------------------------------------------- Table S8

S8_COLUMNS = ("LLR", "abs(LLR)", "L2 dist.", "Cosine dist.", "Inner prod.")
S8_MODELS = ("GPN-MSA", "GPN-Promoter", "NT", "HyenaDNA", "Caduceus", "SpeciesLM",
             "AIDO.DNA", "Evo2 1B", "Evo2 7B", "Evo2 40B")


def table_s8(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table S8: AUPRC for different gLM zero-shot scores.", "Cosine dist.", 22)
    require(tuple(rows[0]) == S8_COLUMNS, f"Table S8 header: {rows[0]}")
    require(rows[1] == ["Dataset", "Model"], f"Table S8 stub header: {rows[1]}")
    dataset = ""
    out = []
    for row in rows[2:]:
        if len(row) == 7:
            dataset, model = row[0], row[1]
            values = row[2:]
        else:
            require(len(row) == 6, f"Table S8 row width: {row}")
            model = row[0]
            values = row[1:]
        require(all(NUMBER.match(v) for v in values), f"Table S8 non-numeric cell: {row}")
        for column, value in zip(S8_COLUMNS, values):
            out.append({"dataset": dataset, "model": model, "score": column, "auprc": value})
    require(len(out) == 100, f"Table S8 cells: {len(out)}")
    for dataset in ("Mendelian traits", "Complex traits"):
        got = tuple(dict.fromkeys(r["model"] for r in out if r["dataset"] == dataset))
        require(got == S8_MODELS, f"Table S8 {dataset} models: {got}")
    return out


# ---------------------------------------------------------------- Table S9

S9_MODELS = ("GPN-MSA", "GPN-Promoter", "NT", "HyenaDNA", "Caduceus", "SpeciesLM",
             "AIDO.DNA", "Evo 2 1B", "Evo 2 7B", "Evo 2 40B")


def table_s9(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table S9: Selected zero-shot approach for each gLM.", "Mendelian traits", 11)
    require(rows[0] == ["Mendelian traits", "Complex traits"], f"Table S9 header: {rows[0]}")
    out = []
    for row in rows[1:]:
        require(len(row) == 3, f"Table S9 row width: {row}")
        out.append({"model": row[0], "mendelian_traits": row[1], "complex_traits": row[2]})
    require(tuple(r["model"] for r in out) == S9_MODELS, f"Table S9 models: {out}")
    require(all(r[k] in S8_COLUMNS for r in out for k in ("mendelian_traits", "complex_traits")),
            f"Table S9 approaches not among the Table S8 columns: {out}")
    return out


# ---------------------------------------------------------------- Table S10

def table_s10(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table S10: Number of overlapping variants with CADD training set.", "CADD training positives", 5)
    require(rows[0] == ["CADD training positives", "CADD training negatives"],
            f"Table S10 header: {rows[0]}")
    out = []
    for row in rows[1:]:
        require(len(row) == 3, f"Table S10 row width: {row}")
        out.append({"set": row[0], "cadd_training_positives": row[1],
                    "cadd_training_negatives": row[2]})
    require([r["set"] for r in out] == ["Mendelian traits positives", "Mendelian traits negatives",
                                        "Complex traits positives", "Complex traits negatives"],
            f"Table S10 rows: {out}")
    return out


# ---------------------------------------------------------------- Table S11

S11_COLUMNS = ("Borzoi", "GPN-MSA", "CADD", "Ensemble")
S11_MENDELIAN = ("Hyperferritinemia", "Beta-thalassemia", "Pulmonary fibrosis", "Hemophilia B",
                 "Cartilage-hair hypoplasia", "Preaxial polydactyly II", "Hypercholesterolemia-1",
                 "Dwarfism (MOPD1)")
S11_COMPLEX = ("Adult height", "Platelet count", "Estimated heel bone mineral density",
               "Mean corpuscular volume", "Monocyte count", "Hemoglobin A1c",
               "Albumin/Globulin ratio", "High density lipoprotein cholesterol",
               "Estimated glomerular filtration rate (cystain C)", "Alkaline phosphatase",
               "Gamma-glutamyl transferase", "FEV1/FVC ratio", "Pulse pressure", "Calcium",
               "Albumin", "Body mass index", "Balding Type 4", "Blood clot in the leg")


def table_s11(lines: list[str]) -> list[dict[str, str]]:
    rows = body(lines, "Table S11: AUPRC for selected traits", "Ensemble", 1 + 1 + 8 + 1 + 18)
    require(tuple(rows[0]) == S11_COLUMNS, f"Table S11 header: {rows[0]}")
    dataset = ""
    out = []
    for row in rows[1:]:
        if len(row) == 1:
            require(row[0] in ("Mendelian traits", "Complex traits"), f"Table S11 group: {row}")
            dataset = row[0]
            continue
        # A long trait name can run into the first value column, so take the last four
        # cells as the values and everything before them as the trait name.
        require(len(row) >= 5, f"Table S11 row width: {row}")
        trait = "  ".join(row[:-4]).strip()
        values = row[-4:]
        require(all(NUMBER.match(v) for v in values), f"Table S11 non-numeric cell: {row}")
        for column, value in zip(S11_COLUMNS, values):
            out.append({"dataset": dataset, "trait": trait, "system": column, "auprc": value})
    mendelian = tuple(dict.fromkeys(r["trait"] for r in out if r["dataset"] == "Mendelian traits"))
    complex_ = tuple(dict.fromkeys(r["trait"] for r in out if r["dataset"] == "Complex traits"))
    require(mendelian == S11_MENDELIAN, f"Table S11 Mendelian traits: {mendelian}")
    require(complex_ == S11_COMPLEX, f"Table S11 complex traits: {complex_}")
    require(len(out) == 104, f"Table S11 cells: {len(out)}")
    return out


TABLES = {
    "table-1": table_1,
    "table-2": table_2,
    "table-4": table_4,
    "table-5": table_5,
    "table-s4": table_s4,
    "table-s5": table_s5,
    "table-s6": table_s6,
    "table-s8": table_s8,
    "table-s9": table_s9,
    "table-s10": table_s10,
    "table-s11": table_s11,
}


def parse_all(text_path: pathlib.Path) -> dict[str, list[dict[str, str]]]:
    raw = text_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == TEXT_SHA256,
            f"text layer SHA-256 {digest} does not match the pinned {TEXT_SHA256}")
    lines = raw.decode("utf-8").splitlines()
    return {name: fn(lines) for name, fn in TABLES.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", type=pathlib.Path, help="pdftotext -layout text layer")
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path(__file__).parent)
    args = parser.parse_args()
    tables = parse_all(args.text)
    for name, rows in tables.items():
        path = args.out / f"{name}.tsv"
        header = list(rows[0])
        with path.open("w", encoding="utf-8") as handle:
            handle.write("\t".join(header) + "\n")
            for row in rows:
                handle.write("\t".join(row[key] for key in header) + "\n")
        print(f"{path}: {len(rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
