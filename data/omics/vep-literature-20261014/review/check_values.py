"""Independent value check for vep-literature-20261014 (review, 2026-10-14).

Usage: python3 -I review/check_values.py <download-dir> [--json <report.json>]

<download-dir> holds the re-downloaded artifacts under these names:
  PMC12016141.xml, MOESM2.xlsx, dms_spearman.csv, clin_zs_sub.csv, clin_sup_sub.csv, clin_zs_indel.csv

Written by the reviewer; it does not import or copy extract/extract_vep.py or extract/ooxml.py. It
re-parses the workbook (zip of sheet XML, stdlib ElementTree) and the four ProteinGym CSVs (csv
module), then for every result in batch.jsonl compares printed_value, numeric_value, raw cell
value, locator (sheet, cell, row label, column header, CSV line), metric, qualifier, direction,
unit, uncertainty, coverage and the evaluation's protocol, dataset and configuration label. It also
checks that every value cell in the extracted columns has exactly one result. Exit status 1 if any
check fails.
"""
import csv
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

BATCH_DIR = Path(__file__).resolve().parent.parent
REPO = BATCH_DIR.parent.parent.parent
P = "vep-lit-20261014-"
HASHES = {
    "PMC12016141.xml": "1735ee461ef192d9de67c914e9ad73d72d8aa255ea0e3479eb68cd8631d99fa2",
    "MOESM2.xlsx": "1b0d792d1a5d3daa95545a7973cabb131c45e42c952e7e5a447a72deef1d1e70",
    "dms_spearman.csv": "ee61a7c09efbfbd8d9a6c9355092c798032a578fa58c6f6256b5da8778555fd4",
    "clin_zs_sub.csv": "fbe453d1aaa6c30a1d0adf610f7fc23c36044a8e2548b178d316777383f8fe93",
    "clin_sup_sub.csv": "f2e38aeac2624d87e7a35a5b16bd580de62c24db36973848e1d94ac3ce510359",
    "clin_zs_indel.csv": "98a532c0e2c3d4720b73b7c05cf0dcf0419438c326761aaae3b788799f5aa836",
}
PG_PATHS = {
    "benchmarks/DMS_zero_shot/substitutions/Spearman/Summary_performance_DMS_substitutions_Spearman.csv": "dms_spearman.csv",
    "benchmarks/clinical_zero_shot/substitutions/AUC/Summary_performance_clinical_substitutions_AUC.csv": "clin_zs_sub.csv",
    "benchmarks/clinical_supervised/substitutions/AUC/Summary_performance_clinical_substitutions_AUC.csv": "clin_sup_sub.csv",
    "benchmarks/clinical_zero_shot/indels/AUC/Summary_performance_clinical_indels_AUC.csv": "clin_zs_indel.csv",
}

# Expected protocol, dataset and qualifier per (sheet, column), written from the legends and Methods.
WIN = "average pairwise win rate against all other VEPs, |Spearman| with DMS"
LIVESEY = {
    ("Table S3", "rank_score"): ("livesey2025-dms-all", WIN + " on shared variants, 36 human DMS sets"),
    ("Table S3", "top_5_winrate"): ("livesey2025-dms-all", "average pairwise win rate against the five top-ranked VEPs (column top_5_winrate; the five are not listed in the table), |Spearman| with DMS on shared variants, 36 human DMS sets"),
    ("Table S5", "rank_score_direct"): ("livesey2025-dms-direct", WIN + " on shared variants, direct DMS assays only"),
    ("Table S5", "rank_score_indirect"): ("livesey2025-dms-indirect", WIN + " on shared variants, indirect DMS assays only"),
    ("Table S6", "rank_score"): ("livesey2025-dms-snv", WIN + " on shared variants, SNV-accessible substitutions only"),
    ("Table S7", "rank_score"): ("livesey2025-dms-snv-filled", WIN + ", SNV-accessible substitutions, missing predictions filled with the VEP's most benign score"),
    ("Table S8", "rank_score"): ("livesey2025-clinical-auroc", "average pairwise win rate against all other VEPs, per-protein AUROC on shared variants, ClinVar P/LP versus gnomAD v4.1 missense, proteins with at least 10 of each"),
}
S8_LABEL_TO_CONFIG_LABEL = {"CPT": "CPT-1", "fathmm-XF": "FathmmXF"}

PG_DMS_QUAL = "ProteinGym zero-shot DMS substitutions, "
PG_DMS = {
    "Average_Spearman": "mean over selection types of the per-type mean over proteins of assay-level Spearman (all 217 assays)",
    **{f"Function_{k}": f"{v} assays: mean over proteins of assay-level Spearman" for k, v in
       [("Activity", "Activity"), ("Binding", "Binding"), ("Expression", "Expression"),
        ("OrganismalFitness", "Organismal fitness"), ("Stability", "Stability")]},
    **{f"{k}_MSA_depth": f"{k} MSA depth proteins: mean over proteins of assay-level Spearman" for k in ("Low", "Medium", "High")},
    **{f"Taxa_{k}": f"{v} proteins: mean over proteins of assay-level Spearman" for k, v in
       [("Human", "Human"), ("Other_Eukaryote", "Other eukaryote"), ("Prokaryote", "Prokaryote"), ("Virus", "Virus")]},
    **{f"Depth_{k}": f"variants with {v}: mean over protein and selection-type groups of assay-level Spearman" for k, v in
       [("1", "1 substitution"), ("2", "2 substitutions"), ("3", "3 substitutions"), ("4", "4 substitutions"), ("5+", "5 or more substitutions")]},
}
PG_CLIN = {
    "clin_zs_sub.csv": ("proteingym-clinical-zero-shot-substitutions-auc-144fe22", "ProteinGym clinical substitutions, zero-shot, Average_AUC over proteins", True),
    "clin_sup_sub.csv": ("proteingym-clinical-supervised-substitutions-auc-144fe22", "ProteinGym clinical substitutions, supervised clinical predictors, Average_AUC over proteins", True),
    "clin_zs_indel.csv": ("proteingym-clinical-zero-shot-indels-auc-144fe22", "ProteinGym clinical indels, zero-shot, Average_AUC over proteins", False),
}

# ---- workbook reader ----------------------------------------------------------------------------
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def col_number(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def read_workbook(path):
    z = zipfile.ZipFile(path)
    shared = ["".join(t.text or "" for t in si.iter(M + "t")) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(M + "si")]
    rels = {e.get("Id"): e.get("Target") for e in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    styles = ET.fromstring(z.read("xl/styles.xml"))
    custom = {e.get("numFmtId"): e.get("formatCode") for e in styles.iter(M + "numFmt")}
    xf_fmt = [xf.get("numFmtId") for xf in styles.find(M + "cellXfs").findall(M + "xf")]
    out = {}
    for s in ET.fromstring(z.read("xl/workbook.xml")).iter(M + "sheet"):
        target = rels[s.get(R_ID)].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        cells = {}
        for c in ET.fromstring(z.read(target)).iter(M + "c"):
            v = c.find(M + "v")
            if v is None:
                continue
            m = re.fullmatch(r"([A-Z]+)(\d+)", c.get("r"))
            fid = xf_fmt[int(c.get("s", "0"))]
            cells[(int(m.group(2)), col_number(m.group(1)))] = {
                "ref": c.get("r"),
                "text": shared[int(v.text)] if c.get("t") == "s" else v.text,
                "is_string": c.get("t") in ("s", "str"),
                "formula": c.find(M + "f") is not None,
                "format": "General" if fid == "0" else custom.get(fid, "builtin " + fid),
            }
        out[s.get("name")] = cells
    return out


def shortest(raw):
    """Shortest decimal that round-trips to the same IEEE double (Python repr), without a trailing .0."""
    s = repr(float(raw))
    assert "e" not in s and "inf" not in s and "nan" not in s, raw
    return s[:-2] if s.endswith(".0") else s


# ---- main ---------------------------------------------------------------------------------------
def main():
    dl = Path(sys.argv[1])
    report_path = Path(sys.argv[sys.argv.index("--json") + 1]) if "--json" in sys.argv else None
    failures, checked = [], {"livesey": 0, "pg_dms": 0, "pg_clinical": 0}

    def fail(rid, msg):
        failures.append({"id": rid, "problem": msg})

    for name, sha in HASHES.items():
        got = hashlib.sha256((dl / name).read_bytes()).hexdigest()
        if got != sha:
            fail(name, f"artifact SHA-256 {got} != {sha}")
    records = [json.loads(line) for line in (BATCH_DIR / "batch.jsonl").read_text().splitlines()]
    by_id = {r["id"]: r for r in records}
    store_configs = {}
    for line in (REPO / "data/entities/configurations.jsonl").read_text().splitlines():
        r = json.loads(line)
        store_configs[r["id"]] = r
    sources = {r["id"]: r for r in records if r["kind"] == "source"}
    for sid, s in sources.items():
        a = s["attributes"]
        path = next((p for p in PG_PATHS if a["url"].endswith(p)), None)
        name = PG_PATHS[path] if path else ("MOESM2.xlsx" if a["url"].endswith(".xlsx") else "PMC12016141.xml")
        if a["artifact_sha256"] != HASHES[name]:
            fail(sid, "source record hash differs from re-downloaded artifact")

    def config_of(result):
        ev = by_id[result["links"][0]["target_id"]]
        links = {}
        for link in ev["links"]:
            links.setdefault(link["relation"], []).append(link["target_id"])
        assert all(len(v) == 1 for k, v in links.items() if k in ("system", "assessment", "data")), ev["id"]
        cid = links["system"][0]
        cfg = by_id.get(cid) or store_configs.get(cid)
        return ev, cfg, links["assessment"][0], links["data"][0]

    results = [r for r in records if r["kind"] == "result"]
    seen_cells = set()

    # Livesey and Marsh workbook
    wb = read_workbook(dl / "MOESM2.xlsx")
    headers = {name: {c: cell["text"] for (row, c), cell in cells.items() if row == 1} for name, cells in wb.items()}
    loc_re = re.compile(r"Supplementary Material 2, sheet '(Table S\d)', cell ([A-Z]+)(\d+) \(row '(.+)', column '(.+)'\)$")
    label_to_config = {}
    for r in results:
        a = r["attributes"]
        m = loc_re.match(a["source_locator"])
        if not m:
            continue
        checked["livesey"] += 1
        sheet, col_letters, row, label, column = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
        col = col_number(col_letters)
        cells = wb[sheet]
        cell = cells.get((row, col))
        if cell is None:
            fail(r["id"], "locator cell is empty")
            continue
        seen_cells.add((sheet, row, col))
        if cells[(row, 1)]["text"] != label:
            fail(r["id"], f"row label is {cells[(row, 1)]['text']!r}, locator says {label!r}")
        if headers[sheet].get(col) != column:
            fail(r["id"], f"column header is {headers[sheet].get(col)!r}, locator says {column!r}")
        if cell["is_string"] or cell["formula"]:
            fail(r["id"], "cell is a string or formula")
        if a.get("raw_xml_value") != cell["text"]:
            fail(r["id"], f"raw_xml_value {a.get('raw_xml_value')} != cell {cell['text']}")
        if a.get("workbook_number_format") != cell["format"]:
            fail(r["id"], "number format differs")
        if a["printed_value"] != shortest(cell["text"]):
            fail(r["id"], f"printed_value {a['printed_value']} != shortest round-trip {shortest(cell['text'])}")
        if a["numeric_value"] != a["printed_value"] or Decimal(a["numeric_value"]) != Decimal(shortest(cell["text"])):
            fail(r["id"], "numeric_value differs from printed value")
        if not 0 <= float(cell["text"]) <= 100:
            fail(r["id"], "win rate outside 0-100")
        expected = LIVESEY.get((sheet, column))
        if expected is None:
            fail(r["id"], f"unexpected column {sheet}/{column}")
            continue
        protocol, qualifier = expected
        if (a["metric"], a["unit"], a["metric_direction"], a.get("metric_qualifier")) != ("pairwise-win-rate", "percent", "higher", qualifier):
            fail(r["id"], "metric, unit, direction or qualifier differs")
        if "uncertainty" in a or a.get("missing_metadata", {}).get("uncertainty", {}).get("reason") != "unreported":
            fail(r["id"], "uncertainty should be absent with reason unreported")
        proteins_col = next((c for c, h in headers[sheet].items() if h == "proteins"), None)
        cov = a.get("coverage")
        if proteins_col and column != "top_5_winrate":
            want = int(cells[(row, proteins_col)]["text"])
            eligible = 819 if sheet == "Table S8" else 36
            if not cov or (cov["scored"], cov["eligible"]) != (want, eligible):
                fail(r["id"], f"coverage {cov} != proteins {want} of {eligible}")
        elif cov:
            fail(r["id"], "coverage present where the extraction keeps none (no proteins column, or top_5_winrate)")
        ev, cfg, assessment, data = config_of(r)
        if assessment != P + "protocol-" + protocol:
            fail(r["id"], f"assessment {assessment} != {protocol}")
        want_data = P + ("dataset-livesey2025-clinvar-gnomad-819" if sheet == "Table S8" else "dataset-livesey2025-dms-36")
        if data != want_data:
            fail(r["id"], f"data link {data} != {want_data}")
        if ev["attributes"]["origin"] != "independent_paper":
            fail(r["id"], "Livesey evaluation origin is not independent_paper")
        cfg_label = S8_LABEL_TO_CONFIG_LABEL.get(label, label) if sheet == "Table S8" else label
        if cfg["attributes"].get("reported_name") != cfg_label:
            fail(r["id"], f"configuration reported_name {cfg['attributes'].get('reported_name')!r} != {cfg_label!r}")
        if label_to_config.setdefault(cfg_label, cfg["id"]) != cfg["id"]:
            fail(r["id"], f"label {cfg_label} maps to two configurations")
        if sheet == "Table S8" and label in S8_LABEL_TO_CONFIG_LABEL and "source_anomaly" not in a:
            fail(r["id"], "mapped S8 label lacks source_anomaly")

    for sheet, column in LIVESEY:
        col = next(c for c, h in headers[sheet].items() if h == column)
        rows = [row for (row, c) in wb[sheet] if c == col and row > 1]
        for row in rows:
            if (sheet, row, col) not in seen_cells:
                fail(f"{sheet}!{wb[sheet][(row, col)]['ref']}", "value cell has no result")
    if checked["livesey"] != len(seen_cells):
        fail("livesey", "two results point at the same cell")

    # ProteinGym CSVs
    pg_rows = {}
    for path, name in PG_PATHS.items():
        with open(dl / name, newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader)
            rows = {}
            for row in reader:
                rows[reader.line_num] = row
            pg_rows[path] = (header, rows)
    pg_re = re.compile(r"(benchmarks/\S+\.csv) line (\d+), row '(.+)', column '(.+)'$")
    pg_seen = set()
    for r in results:
        a = r["attributes"]
        m = pg_re.match(a["source_locator"])
        if not m:
            continue
        path, line, label, column = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        header, rows = pg_rows[path]
        name = PG_PATHS[path]
        row = rows.get(line)
        if row is None or len(row) != len(header):
            fail(r["id"], "CSV line missing or ragged")
            continue
        values = dict(zip(header, row))  # the duplicated Model_rank header keeps its last (empty) cell; unused here
        if values["Model_name"] != label:
            fail(r["id"], f"Model_name {values['Model_name']!r} != {label!r}")
        if column not in header:
            fail(r["id"], f"no column {column}")
            continue
        pg_seen.add((path, line, column))
        printed = row[header.index(column)]
        if a["printed_value"] != printed:
            fail(r["id"], f"printed_value {a['printed_value']} != {printed}")
        if a["numeric_value"] != printed or not re.fullmatch(r"-?\d+(\.\d+)?", printed):
            fail(r["id"], f"numeric_value {a['numeric_value']} != {printed}")
        ev, cfg, assessment, data = config_of(r)
        reported = cfg["attributes"].get("reported_name") if cfg else None
        if reported != label:
            fail(r["id"], f"configuration reported_name {reported!r} != {label!r}")
        if name == "dms_spearman.csv":
            checked["pg_dms"] += 1
            want = ("spearman-correlation", "unitless", "higher", PG_DMS_QUAL + PG_DMS.get(column, "?"))
            if assessment != "rewire-proteingym-v1-3-dms-substitutions":
                fail(r["id"], f"assessment {assessment}")
            if cfg["attributes"].get("version") != "144fe22b07dfaeec2b366f2346203a9838a55b4c":
                fail(r["id"], "configuration is not the 144fe22 snapshot")
            u = a.get("uncertainty")
            if column == "Average_Spearman":
                se = values["Bootstrap_standard_error_Spearman"]
                if not u or (u["type"], u["value"], u["printed"], u.get("resamples"), u.get("source_column")) != (
                        "standard_error", se, se, 10000, "Bootstrap_standard_error_Spearman"):
                    fail(r["id"], f"uncertainty {u} != bootstrap SE {se}")
            elif u or a.get("missing_metadata", {}).get("uncertainty", {}).get("reason") not in ("unreported", "inapplicable"):
                fail(r["id"], "category column should carry no uncertainty")
        else:
            checked["pg_clinical"] += 1
            protocol, qualifier, has_se = PG_CLIN[name]
            want = ("auroc", "unitless", "higher", qualifier)
            if column != "Average_AUC":
                fail(r["id"], f"unexpected column {column}")
            if assessment != P + "protocol-" + protocol:
                fail(r["id"], f"assessment {assessment} != {protocol}")
            u = a.get("uncertainty")
            if has_se:
                se = values["Bootstrap_standard_error_AUC"]
                if not u or (u["type"], u.get("value"), u.get("printed"), u.get("source_column")) != (
                        "unresolved_spread", se, se, "Bootstrap_standard_error_AUC"):
                    fail(r["id"], f"uncertainty {u} != bootstrap column {se}")
            elif u:
                fail(r["id"], "indel file has no bootstrap column, but uncertainty is set")
        if (a["metric"], a["unit"], a["metric_direction"], a.get("metric_qualifier")) != want:
            fail(r["id"], f"metric fields {(a['metric'], a['unit'], a['metric_direction'], a.get('metric_qualifier'))} != {want}")
    for path, (header, rows) in pg_rows.items():
        cols = list(PG_DMS) if PG_PATHS[path] == "dms_spearman.csv" else ["Average_AUC"]
        for line, row in rows.items():
            for column in cols:
                if row[header.index(column)] != "" and (path, line, column) not in pg_seen:
                    fail(f"{path}:{line}:{column}", "value cell has no result")

    # Every result was matched by one of the two locator patterns; every evaluation has a result.
    total = sum(checked.values())
    if total != len(results):
        fail("batch", f"{len(results) - total} results with an unrecognised locator")
    with_results = {r["links"][0]["target_id"] for r in results}
    for r in records:
        if r["kind"] == "evaluation" and r["id"] not in with_results:
            fail(r["id"], "evaluation without results")

    # claims.csv agrees with the records
    with open(BATCH_DIR / "claims.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    claim_rows = {row["record_id"]: row for row in rows}
    for r in results:
        row = claim_rows.get(r["id"])
        if not row or row["printed_value"] != r["attributes"]["printed_value"] or row["locator"] != r["attributes"]["source_locator"]:
            fail(r["id"], "claims.csv row missing or different")

    summary = {"results": len(results), "checked": checked, "failures": len(failures)}
    print(json.dumps(summary))
    for f in failures[:50]:
        print(json.dumps(f))
    if report_path:
        report_path.write_text(json.dumps({"summary": summary, "failures": failures}, indent=1) + "\n")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
