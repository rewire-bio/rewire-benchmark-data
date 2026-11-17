"""Parse Tables 1 and 2 of the PhyloGPN preprint from its pinned JATS XML.

Usage: python3 -I extract/parse_tables.py <artifact.xml|artifact.xml.gz> [out.json]

The artifact is the Europe PMC full text XML of PMC11908359 (arXiv:2503.03773v1), pinned on
source record `phylogpn-2025` with SHA-256 807f3a26...4224. The hash of the uncompressed XML is
asserted here, so a different retrieval stops the parse instead of producing records.

Every row label, every column header and the shape of each table are asserted. Table 2 prints
`N/A` where a model was not evaluated on a task; those cells are reported separately and never
become results.
"""

import gzip
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET

ARTIFACT_SHA256 = "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224"

T1_COLUMNS = ["Class", "PhyloGPN", "Caduceus", "Nucleotide Transformer", "HyenaDNA", "GPN-MSA"]
T1_ROWS = [
    "3’ UTR",
    "5’ UTR",
    "Downstream of Transcript",
    "Intronic",
    "Missense",
    "Noncoding",
    "Splice Acceptor",
    "Splice Donor",
    "Start Codon",
    "Stop Lost",
    "Synonymous",
    "Upstream of Transcript",
]
T2_COLUMNS = [
    "Model",
    "Gene Finding (MCC)",
    "Enhancer Annotation (AUPRC)",
    "Chromatin Accessibility (AUROC)",
    "Histone Modification (AUROC)",
    "CpG Methylation (AUROC)",
    "Expression VEP (AUROC)",
    "Disease VEP (AUROC)",
]
T2_ROWS = [
    "PhyloGPN",
    "PhyloGPN-X",
    "Caduceus",
    "DNABERT",
    "GENA-LM",
    "HyenaDNA",
    "Nucleotide Transformer",
    "GPN-MSA",
    "GPN-MSA (LLR)",
    "Expert Method",
    "",  # the label row naming the expert method used for each column; its first cell is empty
]
VALUE = re.compile(r"^-?\d\.\d\d\*?$")


def read_bytes(path):
    raw = open(path, "rb").read()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    return raw


def cell_text(cell):
    return re.sub(r"\s+", " ", "".join(cell.itertext())).strip()


def tables(raw):
    root = ET.fromstring(raw)
    out = {}
    for wrap in root.iter():
        if not str(wrap.tag).endswith("table-wrap"):
            continue
        label = None
        for child in wrap.iter():
            if str(child.tag).endswith("label"):
                label = cell_text(child).rstrip(".")
                break
        rows = []
        for tr in wrap.iter():
            if not str(tr.tag).endswith("tr"):
                continue
            cells = [cell_text(c) for c in tr if str(c.tag).endswith(("td", "th"))]
            if any(cells):
                rows.append(cells)
        out[label] = rows
    return out


def grid(rows, columns, labels, name):
    assert rows[0] == columns, f"{name}: header {rows[0]!r} != {columns!r}"
    body = rows[1:]
    got = [r[0] for r in body]
    assert got == labels, f"{name}: row labels {got!r} != {labels!r}"
    for r in body:
        assert len(r) == len(columns), f"{name}: row {r[0]!r} has {len(r)} cells, expected {len(columns)}"
    return {r[0]: dict(zip(columns[1:], r[1:])) for r in body}


def main():
    path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "extract/tables.json"
    raw = read_bytes(path)
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == ARTIFACT_SHA256, f"artifact sha256 {digest} != {ARTIFACT_SHA256}"

    found = tables(raw)
    t1 = grid(found["Table 1"], T1_COLUMNS, T1_ROWS, "Table 1")
    t2 = grid(found["Table 2"], T2_COLUMNS, T2_ROWS, "Table 2")

    # Table 1: every cell is a printed AUROC.
    values_1 = [v for row in t1.values() for v in row.values()]
    assert len(values_1) == 60, f"Table 1 has {len(values_1)} cells, expected 60"
    assert all(VALUE.match(v) for v in values_1), f"Table 1 has a non-numeric cell: {values_1}"

    # Table 2: the last row is the expert-method label row, not data.
    experts = t2.pop("")
    expert_labels = list(experts.values())
    assert expert_labels == [
        "(Augustus)",
        "(Enformer)",
        "(Basset)",
        "(Basset)",
        "(Basset)",
        "(DeepSEA)",
        "(DeepSEA)",
    ], f"unexpected expert label row: {expert_labels!r}"
    cells_2 = [(row, col, v) for row, cols in t2.items() for col, v in cols.items()]
    assert len(cells_2) == 70, f"Table 2 has {len(cells_2)} data cells, expected 70"
    na = [(r, c) for r, c, v in cells_2 if v == "N/A"]
    assert len(na) == 6, f"Table 2 has {len(na)} N/A cells, expected 6: {na}"
    numeric = [(r, c, v) for r, c, v in cells_2 if v != "N/A"]
    assert len(numeric) == 64, f"Table 2 has {len(numeric)} printed values, expected 64"
    assert all(VALUE.match(v) for _, _, v in numeric), "Table 2 has an unparsed cell"

    payload = {
        "artifact": path,
        "artifact_sha256": digest,
        "table_1": {"columns": T1_COLUMNS, "rows": t1},
        "table_2": {"columns": T2_COLUMNS, "rows": t2, "expert_labels": dict(zip(T2_COLUMNS[1:], expert_labels))},
        "table_2_not_applicable": na,
    }
    with open(out_path, "w") as handle:
        json.dump(payload, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    print(f"Table 1: {len(values_1)} cells; Table 2: {len(numeric)} values, {len(na)} N/A -> {out_path}")


if __name__ == "__main__":
    main()
