"""Independent review sign-off for feng-dna-fm-20261014 (2026-10-14).

Usage: python3 -I review/signoff.py <Europe PMC fullTextXML> <MOESM3_ESM.xlsm> <MOESM1_ESM.pdf> <repo-root>

Re-checks the three pinned artifacts by SHA-256. Re-parses Tables 2, 3, 5 and 6 of the article XML and
Supplementary Data 1, 2, 4 and 6 of the workbook with its own code (it does not import
extract/extract_feng.py), and asserts that every result, dataset, evaluation link and baseline-CNN claim
matches the source and the stored Feng records. Then sets every record to source_checked, writes the
review objects and writes batch.jsonl back. It refuses to run unless batch.jsonl is the exact
extractor output that was reviewed. <repo-root> is read, never written.
"""
import glob
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BATCH = HERE / "batch.jsonl"
BATCH_SHA_BEFORE = "5fe089b7c42e129bf31214c477a39fb12a543fb8f13100fd42405347ab58a055"
XML_SHA = "5d8ca9bcf88cc1b38ad667906a2e4699b1aefa6d31c6f49259784930353f3202"
XLSM_SHA = "4804c801e0e054eca5f776617c18a6a0cb31d6ce3d2a7a52f70e4dda5b3abd7a"
PDF_SHA = "373f59b825c9e2bc51a0f122a9e2653f427c492727fbf73768cc9af02d094a15"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12663285/fullTextXML"
XLSM_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-65823-8/MediaObjects/41467_2025_65823_MOESM3_ESM.xlsm"
PDF_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-65823-8/MediaObjects/41467_2025_65823_MOESM1_ESM.pdf"
REVIEWED_AT = "2026-10-14T15:00:00Z"
P = "feng-dna-fm-20261014-"
AMP = "amp-feng-20261007-"
SRC = "evidence-expansion-dna-foundation-models-2025-5d8ca9bc"
SRC_SD = "feng-dna-fm-20261013-source-supplementary-data"
SRC_SI = "feng-dna-fm-20261013-source-supplementary-information"
REVIEWER_NOTE = ("Independent Claude (Opus 5.5) review agent for PR #157, separate from the extraction agent for issue #142 "
                 "that built this batch. Automated review only; no human review claimed. Transcription, not reproduction.")

xml_path, xlsm_path, pdf_path, root = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
for path, want in ((xml_path, XML_SHA), (xlsm_path, XLSM_SHA), (pdf_path, PDF_SHA)):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == want, f"{path} hash mismatch"
assert hashlib.sha256(BATCH.read_bytes()).hexdigest() == BATCH_SHA_BEFORE, "batch.jsonl is not the reviewed extractor output"
records = [json.loads(l) for l in BATCH.read_text().splitlines()]
by_id = {r["id"]: r for r in records}
assert len(records) == 698 and all(r["status"] == "needs_review" for r in records)

store = {}
for f in glob.glob(str(root / "data" / "entities" / "**" / "*.jsonl"), recursive=True) + \
        glob.glob(str(root / "data" / "evidence" / "**" / "*.jsonl"), recursive=True):
    for line in open(f, encoding="utf-8"):
        r = json.loads(line)
        store[r["id"]] = r
assert not set(by_id) & set(store), "batch IDs already in the store"
store_results_by_eval = {}
for r in store.values():
    if r["kind"] == "result":
        for l in r["links"]:
            if l["relation"] == "evaluation":
                store_results_by_eval.setdefault(l["target_id"], []).append(r)


def get(rid):
    return by_id.get(rid) or store[rid]


def links(rec):
    return {l["relation"]: l["target_id"] for l in rec["links"]}


# ---- Article tables -------------------------------------------------------------------------
xml_root = ET.parse(xml_path).getroot()


def txt(el):
    return " ".join("".join(el.itertext()).split())


def table(tid):
    tw = next(t for t in xml_root.iter("table-wrap") if t.get("id") == tid)
    trs = list(tw.iter("tr"))
    return [[(txt(c), c.find("bold") is not None) for c in tr if c.tag in ("td", "th")] for tr in trs]


results = [r for r in records if r["kind"] == "result"]
by_loc = {r["attributes"]["source_locator"]: r for r in results}
assert len(by_loc) == len(results) == 305
MODELS = ["DNABERT-2", "NT-v2", "HyenaDNA", "Caduceus-Ph", "GROVER"]
CKPT = {"DNABERT-2": "DNABERT-2, its only published checkpoint", "NT-v2": "NT-v2-500M", "HyenaDNA": "Hyena-160K",
        "Caduceus-Ph": "Caduceus-Ph-131K", "GROVER": "GROVER, its only published checkpoint"}
FOOT = "Bolded: higher than at least two other AUCs, p < 0.01."
STORED_CELLS = {("Table 3", "Human 5mC", "Caduceus-Ph"): "lit-001", ("Table 3", "Human 5mC", "NT-v2"): "lit-002"}
seen, row_protocol, row_dataset = set(), {}, {}
for tid, tlabel, skip_rows in (("Tab2", "Table 2", {"Promoter Arabidopsis NonTATA", "Promoter Arabidopsis TATA"}), ("Tab3", "Table 3", set())):
    rows = table(tid)
    assert [c[0] for c in rows[0]] == ["Data"] + MODELS
    for cells in rows[1:]:
        label = cells[0][0]
        if label in skip_rows:
            continue
        for (val, bold), model in zip(cells[1:], MODELS):
            if (tlabel, label, model) in STORED_CELLS:
                assert store[STORED_CELLS[(tlabel, label, model)]]["attributes"]["printed_value"] == val
                continue
            loc = f"{tlabel}, row '{label}', column '{model}'." + (f" Printed in bold (table footnote: '{FOOT}')." if bold else "")
            r = by_loc[loc]
            a = r["attributes"]
            assert (a["printed_value"], a["numeric_value"], a["metric"], a["unit"], a["metric_direction"], a["metric_qualifier"]) == \
                (val, val, "auroc", "unitless", "higher", f"task: {label.lower()}"), r["id"]
            assert r["source_ids"] == [SRC] and "uncertainty" not in a, r["id"]
            ev = by_id[links(r)["evaluation"]]
            el = links(ev)
            assert ev["attributes"]["origin"] == "independent_paper" and ev["attributes"]["comparison"]["protocol_id"] == el["assessment"]
            cfg = by_id[el["system"]]
            assert cfg["attributes"]["reported_name"] == model and cfg["attributes"]["checkpoint"].startswith(CKPT[model]), cfg["id"]
            assert "random forest" in cfg["attributes"]["head"] and "not label-free" in by_id[el["assessment"]]["attributes"]["scope_note"]
            assert row_protocol.setdefault((tlabel, label), el["assessment"]) == el["assessment"]
            assert row_dataset.setdefault((tlabel, label), el["data"]) == el["data"]
            seen.add(r["id"])
assert len(seen) == 128

# ---- Workbook -------------------------------------------------------------------------------
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
z = zipfile.ZipFile(xlsm_path)
shared = ["".join(t.text or "" for t in si.iter(NS + "t")) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(NS + "si")]
wb = ET.fromstring(z.read("xl/workbook.xml"))
rels = {e.get("Id"): e.get("Target") for e in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}


def sheet(name):
    s = next(s for s in wb.iter(NS + "sheet") if s.get("name") == name)
    t = rels[s.get(RID)]
    x = ET.fromstring(z.read(t if t.startswith("xl/") else "xl/" + t.lstrip("/")))
    out = []
    for row in x.iter(NS + "row"):
        vals = {}
        for c in row.iter(NS + "c"):
            v = c.find(NS + "v")
            if v is not None:
                vals[re.match(r"[A-Z]+", c.get("r")).group(0)] = (shared[int(v.text)] if c.get("t") == "s" else v.text, c.get("r"))
        out.append(vals)
    return out


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


# Table label -> workbook label, by normalising case, punctuation and the "Human " prefix of 5mC/6mA.
def wb_key(label):
    k = norm(label)
    return {"human5mc": "5mc", "human6ma": "6ma"}.get(k, k)


d1 = {norm(r["A"][0]): r["B"][0] for r in sheet("Data 1")[1:] if "A" in r}
d2 = {norm(r["A"][0]): r["B"][0] for r in sheet("Data 2")[1:] if "A" in r}
d6 = {norm(r["A"][0]): {k: v[0] for k, v in r.items()} for r in sheet("Data 6")[1:] if "A" in r}

# Supplementary Note 2 flags, read from the PDF text (pages 3-4) by the reviewer.
SN2_NO = {f"Mouse TFBS {i}" for i in range(1, 6)}
for (tlabel, label), ds_id in row_dataset.items():
    sd = d6[wb_key(label)]
    if ds_id == "reported-dataset-463197d6a98b99":
        note = by_id[row_protocol[(tlabel, label)]]["attributes"]["scope_note"]
        assert f"{sd['E']} training and {sd['F']} test sequences, {sd['G']} positive/negative" in note
        continue
    a = by_id[ds_id]["attributes"]
    pos, neg = map(int, sd["G"].split("/"))
    assert (a["positives"], a["negatives"], a["total"]) == (pos, neg, pos + neg), ds_id
    assert f"{sd['E']} training and {sd['F']} test sequences" in a["split"] and a["test_denominator"].startswith(f"{sd['F']} test"), ds_id
    assert f"median {sd['B']} bp (range {sd['C']}-{sd['D']} bp)" in a["population"], ds_id
    scope = a.get("scope_note", "")
    assert ("do not sum" in scope) == (pos + neg != int(sd["E"]) + int(sd["F"])), ds_id
    assert ("not fully relying on experimental" in scope) == (label in SN2_NO), ds_id
    assert ("'Unknown'" in scope) == label.startswith("Yeast"), ds_id
    assert ("example of a human epigenetic task" in scope) == label.endswith("4mC"), ds_id
    assert ("computational predictions" in scope) == (label.split()[0] in ("A.Thaliana", "C.Elegans", "D.Melanogaster")), ds_id

cnn = [r for r in records if r["id"].startswith(P + "claim-cnn-")]
assert len(cnn) == 26
models_set = lambda s: sorted(x.strip() for x in s.split(","))
for c in cnn:
    a = c["attributes"]
    key = norm(re.search(r"row '([^']+)'", a["source_locator"]).group(1))
    m = re.search(r"p<0\.01\): (.+?)\. Supplementary Data 2 lists the models that significantly outperformed the CNN: (.+?)\. ", a["value"])
    assert models_set(m.group(1)) == models_set(d1[key]) and models_set(m.group(2)) == models_set(d2[key]), c["id"]
    assert links(c)["subject"] in row_protocol.values()

# ---- Supplementary Data 4 -------------------------------------------------------------------
t5 = {r[0][0]: r[1][0] for r in table("Tab5")[1:]}
t6rows = table("Tab6")[1:13]
t6 = {}
for i, r in enumerate(t6rows):
    r = r[1:] if i == 0 else r
    t6[r[0][0]] = dict(zip(["eQTL", "sQTL", "paQTL", "ipaQTL"], [c[0] for c in r[1:]]))
GROUPS = {1: "chromosomes 3, 6, 9, 12, 16, 18, 19, 21", 2: "chromosomes 2, 5, 11, 14, 17, 20, 22, X", 3: "chromosomes 1, 4, 7, 8, 10, 13, 15"}
BLOCKS = {"Pathogenic variants vs common": ("variant", None), "eQTL": ("qtl-eqtl", "eQTL"), "sQTL": ("qtl-sqtl", "sQTL"),
          "paQTL": ("qtl-paqtl", "paQTL"), "ipaQTL": ("qtl-ipaqtl", "ipaQTL")}
d4 = sheet("Data 4")
block, header, n_sd4, group_evals = None, None, 0, set()
for row in d4:
    a = row.get("A", ("", ""))[0]
    if a in BLOCKS:
        block, header = a, None
        continue
    if a == "Model name":
        header = row
        continue
    if not a:
        continue
    key, col = BLOCKS[block]
    # Table 5/6 row for this workbook label: the short HyenaDNA row is printed as "HyenaDNA".
    table_label = next(k for k in (t5 if col is None else t6) if norm(k.rstrip("*")) == norm(a.replace("-160K", "")))
    mean_printed = t5[table_label] if col is None else t6[table_label][col]
    old_ev_id = AMP + f"eval-{key}-" + re.sub(r"[^a-z0-9]+", "-", table_label.rstrip("*").lower()).strip("-")
    old_ev = store[old_ev_id]
    (mean_res,) = [x for x in store_results_by_eval[old_ev_id] if x["attributes"]["metric"] == "auroc"]
    assert mean_res["attributes"]["printed_value"] == mean_printed, old_ev_id
    vals = []
    for g, c in ((1, "B"), (2, "C"), (3, "D")):
        raw, ref = row[c]
        shown = repr(float(raw))
        assert re.fullmatch(r"0\.\d{1,4}", shown) and abs(float(raw) - float(shown)) < 1e-12, raw
        vals.append(Decimal(shown))
        loc_prefix = f"Supplementary Data 4 (workbook sheet 'Data 4'), block '{block}', row '{a}', column '{header[c][0]}' (cell {ref})."
        (r,) = [x for loc, x in by_loc.items() if loc.startswith(loc_prefix)]
        ra = r["attributes"]
        assert (ra["printed_value"], ra["numeric_value"], ra["metric"], ra["unit"], ra["metric_direction"]) == (shown, shown, "auroc", "unitless", "higher"), r["id"]
        assert ra["metric_qualifier"] == f"{mean_res['attributes']['metric_qualifier']}; outer test group {g} only ({GROUPS[g]}), not averaged", r["id"]
        assert r["source_ids"] == [SRC_SD], r["id"]
        new_ev = by_id[links(r)["evaluation"]]
        assert new_ev["id"] != old_ev_id and new_ev["id"].startswith(P + "eval-sd4-")
        assert {k: v for k, v in links(new_ev).items()} == {k: v for k, v in links(old_ev).items() if k in ("system", "assessment", "data")}, new_ev["id"]
        nc, oc = new_ev["attributes"]["comparison"], old_ev["attributes"]["comparison"]
        assert {k: v for k, v in nc.items() if k != "aggregation"} == {k: v for k, v in oc.items() if k != "aggregation"}
        assert nc["aggregation"].startswith("Per outer chromosome test group") and new_ev["attributes"]["origin"] == old_ev["attributes"]["origin"]
        group_evals.add(new_ev["id"])
        n_sd4 += 1
    assert abs(sum(vals) / 3 - Decimal(mean_printed)) <= Decimal("0.00015"), (old_ev_id, vals, mean_printed)
assert n_sd4 == 177 and len(group_evals) == 59

counts = {}
for r in records:
    counts[r["kind"]] = counts.get(r["kind"], 0) + 1
assert counts == {"claim": 27, "configuration": 128, "dataset": 25, "evaluation": 187, "protocol": 26, "result": 305}, counts
inv = by_id[P + "claim-not-extracted"]
assert {"relation": "supersedes", "target_id": "feng-dna-fm-20261013-claim-not-extracted"} in inv["links"]

# ---- Review blocks --------------------------------------------------------------------------
TABLE_NOTE = ("Re-downloaded the Europe PMC XML and matched the pinned SHA-256. Parsed Tables 2 and 3 with a separate ElementTree parser "
              "(review/signoff.py) and checked printed value, numeric value, metric, qualifier, unit, direction, locator (including bold "
              "marking), and the linked configuration, checkpoint, protocol and dataset.")
SD4_NOTE = ("Re-downloaded the Supplementary Data workbook and matched the pinned SHA-256. Read sheet 'Data 4' with a separate parser "
            "(review/signoff.py) and checked the cell, printed and numeric value, qualifier, and that the result's evaluation has the same "
            "configuration, protocol and dataset as the stored Table 5/6 evaluation, whose printed mean is within rounding of the mean of the three groups.")
CNN_NOTE = ("Re-downloaded the Supplementary Data workbook and matched the pinned SHA-256. Read sheets 'Data 1' and 'Data 2' with a separate "
            "parser (review/signoff.py) and checked both model lists for this row.")
for r in records:
    r["status"] = "source_checked"
    a = r["attributes"]
    old = a.get("review")
    if r["kind"] == "result":
        sd4 = r["id"].startswith(P + "result-sd4-")
        sha, url = (XLSM_SHA, XLSM_URL) if sd4 else (XML_SHA, XML_URL)
        assert old["artifact_sha256"] == sha
        extra = old["note"].split("pinned artifact. ", 1)[1] if "pinned artifact. " in old["note"] else ""
        a["review"] = {"method": ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
                       "method_note": SD4_NOTE if sd4 else TABLE_NOTE, "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
                       "reviewed_at": REVIEWED_AT, "artifact_sha256": sha, "retrieval_url": url,
                       "note": ("Extracted by extract/extract_feng.py (deterministic parse). Independent review: value, metric and identity "
                                "match the source. " + extra).strip()}
    elif r["kind"] == "claim" and r["id"].startswith(P + "claim-cnn-"):
        assert old["artifact_sha256"] == XLSM_SHA
        a["review"] = {"method": ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
                       "method_note": CNN_NOTE, "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
                       "reviewed_at": REVIEWED_AT, "artifact_sha256": XLSM_SHA, "retrieval_url": XLSM_URL,
                       "note": "Independent review: both model lists match the workbook row. The CNN's own AUC is not printed."}
    elif r["kind"] == "claim":
        assert r["id"] == P + "claim-not-extracted"
        a["review"] = {"method": ["source-hash-verification", "ai-assisted-source-review", "pdf-text-parse"],
                       "method_note": ("Checked against the article XML tables and figures, all 11 pages of the Supplementary Information PDF "
                                       "(pdftotext -layout) and the seven workbook sheets."),
                       "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "reviewed_at": REVIEWED_AT,
                       "artifact_sha256": XML_SHA, "retrieval_url": XML_URL,
                       "note": "Independent review: the inventory matches the parts of the source not held as records after this batch."}
    else:
        assert old is None, r["id"]
    if isinstance(a.get("missing_metadata"), dict):
        a["missing_metadata"] = dict(sorted(a["missing_metadata"].items()))

records.sort(key=lambda r: r["id"])
BATCH.write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in records))
print("signed off", len(records), "records;", hashlib.sha256(BATCH.read_bytes()).hexdigest())
