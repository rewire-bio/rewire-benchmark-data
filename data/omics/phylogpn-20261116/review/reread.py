#!/usr/bin/env python3
"""Independent re-read of every PhyloGPN batch result from the pinned JATS XML.

Written for the review pass. It does not import or run extract/parse_tables.py and
does not read extract/tables.json. It parses the two table-wrap elements with
xml.etree, keys every cell by (table label, row label, column header), and checks
each result's printed value, numeric value, metric, direction, unit, locator and
the row-to-configuration assignment of its evaluation.

Usage:
  python3 -I reread.py <fulltext.xml.gz|fulltext.xml> <batch.jsonl>
Exit code 0 only when every check passes.
"""

import gzip
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET

XML_SHA256 = "807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224"

# The row (Table 1: column; Table 2: row) each system label must resolve to.
# Written from reading the paper, not copied from the batch.
T1_COLUMN_SYSTEM = {
    "PhyloGPN": "phylogpn-20261116-config-phylogpn",
    "Caduceus": "phylogpn-20261116-config-caduceus-ps-131k",
    "Nucleotide Transformer": "phylogpn-20261116-config-nt-v2-500m-multi-species",
    "HyenaDNA": "phylogpn-20261116-config-hyenadna-medium-160k",
    "GPN-MSA": "phylogpn-20261116-config-gpn-msa-precomputed-llr",
}
T2_ROW_SYSTEM = {
    "PhyloGPN": "phylogpn-20261116-config-phylogpn",
    "PhyloGPN-X": "phylogpn-20261116-config-phylogpn-x",
    "Caduceus": "phylogpn-20261116-config-caduceus-largest-rce",
    "DNABERT": "phylogpn-20261116-config-dnabert-family-best",
    "GENA-LM": "phylogpn-20261116-config-gena-lm-family-best",
    "HyenaDNA": "phylogpn-20261116-config-hyenadna-family-best",
    "Nucleotide Transformer": "phylogpn-20261116-config-nucleotide-transformer-family-best",
    "GPN-MSA": "phylogpn-20261116-config-gpn-msa-bend-embeddings",
    "GPN-MSA (LLR)": "phylogpn-20261116-config-gpn-msa-bend-llr",
}
# The Expert Method row names its system per column in the row below it.
EXPERT_SYSTEM = {
    "Augustus": "bend-method-augustus",
    "Enformer": "bend-method-enformer",
    "Basset": "bend-method-basset",
    "DeepSEA": "bend-method-deepsea",
}
# Metric concept per Table 2 column, taken from the column header's parenthetical.
HEADER_METRIC = {
    "MCC": "matthews-correlation-coefficient",
    "AUPRC": "auprc",
    "AUROC": "auroc",
}
LOCATOR = re.compile(r"^Table (?P<table>[12]), row '(?P<row>[^']*)', column '(?P<col>[^']*)'$")


def norm(node):
    return " ".join("".join(node.itertext()).split())


def read_xml(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rb") as handle:
        raw = handle.read()
    got = hashlib.sha256(raw).hexdigest()
    if got != XML_SHA256:
        sys.exit(f"artifact sha256 {got} is not the pinned {XML_SHA256}")
    return raw


def parse_tables(raw):
    """Return {table label: {"header": [...], "rows": {label: {col: text}}, "order": [...]}}."""
    root = ET.fromstring(raw)
    wraps = root.findall(".//table-wrap")
    if len(wraps) != 2:
        sys.exit(f"expected 2 table-wrap elements, found {len(wraps)}")
    tables = {}
    for wrap in wraps:
        label = norm(wrap.find("label")).rstrip(".")
        caption = norm(wrap.find("caption"))
        trs = list(wrap.find(".//table").iter("tr"))
        header = None
        rows = {}
        order = []
        for tr in trs:
            cells = [c for c in tr if c.tag in ("th", "td")]
            texts = [norm(c) for c in cells]
            if header is None:
                if all(c.tag == "th" for c in cells) and len(cells) > 1:
                    header = texts
                continue
            if len(texts) == 1 or not texts[0]:
                continue  # spacer row, or the parenthesised expert-method name row
            if len(texts) != len(header):
                sys.exit(f"{label}: row {texts[0]!r} has {len(texts)} cells, header has {len(header)}")
            rows[texts[0]] = dict(zip(header[1:], texts[1:]))
            order.append(texts[0])
        tables[label] = {"header": header, "caption": caption, "rows": rows, "order": order}
    return tables


def expert_names(raw):
    """The parenthesised expert-method names printed under the Expert Method row."""
    root = ET.fromstring(raw)
    for wrap in root.findall(".//table-wrap"):
        if norm(wrap.find("label")).rstrip(".") != "Table 2":
            continue
        header = None
        prev_label = None
        for tr in wrap.find(".//table").iter("tr"):
            texts = [norm(c) for c in tr if c.tag in ("th", "td")]
            if header is None and len(texts) > 1:
                header = texts
                continue
            if texts and not texts[0] and prev_label == "Expert Method":
                return {
                    col: val.strip("()")
                    for col, val in zip(header[1:], texts[1:])
                    if val.startswith("(")
                }
            if texts:
                prev_label = texts[0]
    sys.exit("could not find the expert-method name row")


def main():
    xml_path, batch_path = sys.argv[1], sys.argv[2]
    raw = read_xml(xml_path)
    tables = parse_tables(raw)
    experts = expert_names(raw)
    records = [json.loads(line) for line in open(batch_path)]
    by_id = {r["id"]: r for r in records}
    results = [r for r in records if r["kind"] == "result"]
    evaluations = [r for r in records if r["kind"] == "evaluation"]

    problems = []
    checked = {"Table 1": 0, "Table 2": 0}
    seen_cells = set()

    for res in results:
        rid = res["id"]
        at = res["attributes"]
        match = LOCATOR.match(at.get("source_locator", ""))
        if not match:
            problems.append(f"{rid}: source_locator not parseable: {at.get('source_locator')!r}")
            continue
        table = f"Table {match.group('table')}"
        row, col = match.group("row"), match.group("col")
        tbl = tables[table]
        if row not in tbl["rows"]:
            problems.append(f"{rid}: {table} has no row {row!r}; rows are {tbl['order']}")
            continue
        if col not in tbl["rows"][row]:
            problems.append(f"{rid}: {table} row {row!r} has no column {col!r}")
            continue
        cell = tbl["rows"][row][col]
        key = (table, row, col)
        if key in seen_cells:
            problems.append(f"{rid}: cell {key} claimed by more than one result")
        seen_cells.add(key)
        checked[table] += 1

        if cell == "N/A":
            problems.append(f"{rid}: cell {key} prints N/A but a result exists")
            continue
        if at.get("printed_value") != cell:
            problems.append(f"{rid}: printed_value {at.get('printed_value')!r} != cell {cell!r}")
        bare = cell.rstrip("*")
        if at.get("numeric_value") != bare:
            problems.append(f"{rid}: numeric_value {at.get('numeric_value')!r} != {bare!r}")
        if cell.endswith("*") and "asterisk" not in json.dumps(at.get("source_warnings", "")).lower():
            problems.append(f"{rid}: cell prints an asterisk but source_warnings does not mention it")

        # Metric from the printed column header, not from the batch.
        if table == "Table 2":
            paren = re.search(r"\(([A-Z]+)\)$", col)
            want = HEADER_METRIC.get(paren.group(1)) if paren else None
        else:
            want = "auroc" if "Each entry is an AUROC" in tbl["caption"] else None
        if want is None:
            problems.append(f"{rid}: could not read a metric for column {col!r}")
        elif at.get("metric") != want:
            problems.append(f"{rid}: metric {at.get('metric')!r} != {want!r} from the column header")
        if at.get("metric_direction") != "higher":
            problems.append(f"{rid}: metric_direction {at.get('metric_direction')!r} is not 'higher'")
        if at.get("unit") != "unitless":
            problems.append(f"{rid}: unit {at.get('unit')!r} is not 'unitless'")
        for field in ("uncertainty", "denominator"):
            if field in at:
                problems.append(f"{rid}: {field} has a value; the tables print none")
            elif field not in at.get("missing_metadata", {}):
                problems.append(f"{rid}: {field} is neither a value nor a missing reason")

        # Row to configuration assignment, through the evaluation.
        links = [l for l in res["links"] if l["relation"] == "evaluation"]
        if len(links) != 1:
            problems.append(f"{rid}: {len(links)} evaluation links")
            continue
        ev = by_id.get(links[0]["target_id"])
        if ev is None:
            problems.append(f"{rid}: evaluation {links[0]['target_id']} not in the batch")
            continue
        if ev["attributes"].get("source_locator") != at["source_locator"]:
            problems.append(f"{rid}: evaluation locator differs from the result's")
        system = next((l["target_id"] for l in ev["links"] if l["relation"] == "system"), None)
        if table == "Table 1":
            want_system = T1_COLUMN_SYSTEM.get(col)
        elif row == "Expert Method":
            want_system = EXPERT_SYSTEM.get(experts.get(col, ""))
        else:
            want_system = T2_ROW_SYSTEM.get(row)
        if want_system is None:
            problems.append(f"{rid}: no expected system for {table} {row!r} / {col!r}")
        elif system != want_system:
            problems.append(f"{rid}: system {system!r} != expected {want_system!r}")

    # Every printed numeric cell must have exactly one result, and every N/A none.
    na_cells = []
    for table, tbl in tables.items():
        for row in tbl["order"]:
            for col in tbl["header"][1:]:
                cell = tbl["rows"][row][col]
                key = (table, row, col)
                if cell == "N/A":
                    na_cells.append(key)
                    if key in seen_cells:
                        problems.append(f"{key}: printed N/A but a result claims it")
                elif key not in seen_cells:
                    problems.append(f"{key}: printed {cell!r} but no result records it")
    if len(na_cells) != 6:
        problems.append(f"expected 6 printed N/A cells, found {len(na_cells)}: {na_cells}")

    # No result or evaluation may stand in for an N/A cell with a zero or an empty value.
    for res in results:
        at = res["attributes"]
        if at.get("numeric_value") in (None, "", "0", "0.0", "0.00"):
            problems.append(f"{res['id']}: numeric_value {at.get('numeric_value')!r}")
    na_pairs = {(r, c) for (_t, r, c) in na_cells}
    for ev in evaluations:
        match = LOCATOR.match(ev["attributes"].get("source_locator", ""))
        if match and (match.group("row"), match.group("col")) in na_pairs:
            problems.append(f"{ev['id']}: an evaluation exists for the N/A cell {match.groups()}")

    print(f"table-wrap elements: {len(tables)}")
    for table, tbl in tables.items():
        printed = sum(1 for row in tbl["order"] for col in tbl["header"][1:] if tbl["rows"][row][col] != "N/A")
        print(f"{table}: {len(tbl['order'])} rows x {len(tbl['header']) - 1} columns, "
              f"{printed} printed values, {checked[table]} results checked")
    print(f"printed N/A cells: {sorted(na_cells)}")
    print(f"results checked: {len(seen_cells)} of {len(results)}")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for problem in problems:
            print(f"  {problem}")
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
