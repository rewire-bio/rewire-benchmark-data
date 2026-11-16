"""Parse the two printed tables in the pinned BioEmu-2 model card.

Reads the archived copy of MODEL_CARD.md at commit 6d1ca744fa8ed285edafae7b98da65205bf00fd3,
checks its SHA-256, parses the "Model summary" and "Training data" tables, asserts every
expected row label, and writes extract/model-card-tables.json.

Run from the repository root:
    python3 -I data/omics/bioemu2-20261115/extract/parse_model_card.py
"""

import gzip
import hashlib
import json
import pathlib

BATCH = pathlib.Path(__file__).resolve().parent.parent
ARTIFACT = BATCH / "artifacts" / "repo_MODEL_CARD.md.gz"
OUT = BATCH / "extract" / "model-card-tables.json"

EXPECTED_SHA256 = "5f62c8cee0e5c364bdbbc3a5ae0359acdeca1c6c4e5e5119aad9aae2ce80f451"

SUMMARY_ROWS = [
    "Developer",
    "Model architecture",
    "Parameters",
    "Inputs",
    "Outputs",
    "Training dates",
    "Release date",
    "License",
    "Related assets",
]

TRAINING_ROWS = [
    "PDB, Boltz-1 preprocessed",
    "MSR_cath2",
    "MSR_cath3",
    "MSR_cath_dimers",
    "MSR_heterodimers",
    "MSR_pdbbind2020",
    "MSR_pdbbind2020_apo_free",
    "MSR_megasim_merge",
    "AFDB monomer",
    "AFDB homodimer multiconformation",
    "AFDB heterodimer multiconformation",
    "Teddymer",
]


def read_artifact() -> str:
    raw = gzip.open(ARTIFACT, "rb").read()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_SHA256, f"artifact hash {digest} != {EXPECTED_SHA256}"
    return raw.decode("utf-8")


def split_row(line: str) -> list[str]:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return [cell.strip("*").strip() for cell in cells]


def parse_table(lines: list[str], start: int) -> tuple[list[str], list[list[str]], int]:
    """Parse the markdown table whose header line is at index start."""
    header = split_row(lines[start])
    assert set(lines[start + 1].replace("|", "").replace("-", "").strip()) == set(), (
        f"expected a separator row after the header, found {lines[start + 1]!r}"
    )
    rows = []
    index = start + 2
    while index < len(lines) and lines[index].lstrip().startswith("|"):
        rows.append(split_row(lines[index]))
        index += 1
    return header, rows, index


def find_table(lines: list[str], section: str) -> tuple[list[str], list[list[str]]]:
    """Parse the first table after the named heading, and only before the next heading."""
    section_index = next(i for i, line in enumerate(lines) if line.strip() == section)
    index = section_index + 1
    while index < len(lines):
        line = lines[index].lstrip()
        assert not line.startswith("#"), f"no table between {section!r} and the next heading"
        if line.startswith("|"):
            header, rows, _ = parse_table(lines, index)
            return header, rows
        index += 1
    raise AssertionError(f"no table found after {section!r}")


def main() -> None:
    text = read_artifact()
    lines = text.splitlines()

    summary_header, summary_rows = find_table(lines, "## Model summary")
    assert summary_header == ["Field", "Value"], summary_header
    labels = [row[0] for row in summary_rows]
    assert labels == SUMMARY_ROWS, labels
    summary = {row[0]: row[1] for row in summary_rows}

    training_header, training_rows = find_table(lines, "## Training data")
    assert training_header == ["Dataset", "Modality", "Train sequences/systems"], training_header
    training_labels = [row[0] for row in training_rows]
    assert training_labels == TRAINING_ROWS, training_labels
    training = [
        {"dataset": row[0], "modality": row[1], "train_sequences_systems": row[2]}
        for row in training_rows
    ]
    assert len(training) == 12, len(training)

    tables = {
        "artifact": "MODEL_CARD.md at commit 6d1ca744fa8ed285edafae7b98da65205bf00fd3",
        "artifact_sha256": EXPECTED_SHA256,
        "model_summary": summary,
        "training_data": training,
    }
    OUT.write_text(json.dumps(tables, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT} with {len(summary)} summary rows and {len(training)} training rows")


if __name__ == "__main__":
    main()
