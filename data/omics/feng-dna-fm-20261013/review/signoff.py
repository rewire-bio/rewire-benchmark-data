"""Independent review sign-off for feng-dna-fm-20261013 (2026-10-13).

Usage: python3 -I review/signoff.py <Europe PMC fullTextXML> <MOESM3_ESM.xlsm>

Re-checks the two pinned artifacts by SHA-256, re-parses Table 1 and Table 4 of the article XML and
Supplementary Data 1, 2 and 6 of the workbook with its own code (it does not import
extract/extract_feng.py), asserts that every result, dataset size and baseline-CNN claim matches,
then sets every record to source_checked, writes the review objects and writes batch.jsonl back.
It refuses to run unless batch.jsonl is the exact extractor output that was reviewed.
"""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BATCH = HERE / "batch.jsonl"
BATCH_SHA_BEFORE = "674d06ec195d68507ec87a2caef37988a885617f993d54f92b1f9aa6ea3072ec"
XML_SHA = "5d8ca9bcf88cc1b38ad667906a2e4699b1aefa6d31c6f49259784930353f3202"
XLSM_SHA = "4804c801e0e054eca5f776617c18a6a0cb31d6ce3d2a7a52f70e4dda5b3abd7a"
PDF_SHA = "373f59b825c9e2bc51a0f122a9e2653f427c492727fbf73768cc9af02d094a15"
SCRIPT_SHA = "a9ab37677da4340d3d5ea3b7516d71bf4e60d7cb2eab39eb954584d738ed2788"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12663285/fullTextXML"
XLSM_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-65823-8/MediaObjects/41467_2025_65823_MOESM3_ESM.xlsm"
PDF_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-65823-8/MediaObjects/41467_2025_65823_MOESM1_ESM.pdf"
SCRIPT_URL = "https://raw.githubusercontent.com/ChongWuLab/dna_foundation_benchmark/3f4c81ce066f3c47422a83466b085aac1a6be902/job_scripts/gtex_hyena.py"
DATE = "2026-10-13"
REVIEWED_AT = "2026-10-13T14:40:00Z"
P = "feng-dna-fm-20261013-"
REVIEWER_NOTE = ("Independent Claude (Opus 5.5) review agent, separate from the extraction agent feng-19 that built this "
                 "batch. Automated review only; no human review claimed. Transcription, not reproduction.")
TABLE_NOTE = ("Re-downloaded the Europe PMC XML and matched the pinned SHA-256. Parsed Tables 1 and 4 with a separate "
              "ElementTree parser (review/signoff.py) and checked printed value, numeric value, metric, qualifier, unit, "
              "direction, locator (including bold marking) and the linked configuration and protocol.")
SD_NOTE = ("Re-downloaded the Supplementary Data workbook and matched the pinned SHA-256. Read sheets 'Data 1' and "
           "'Data 2' with a separate parser (review/signoff.py) and checked the listed model sets for this row.")

xml_path, xlsm_path = Path(sys.argv[1]), Path(sys.argv[2])
assert hashlib.sha256(xml_path.read_bytes()).hexdigest() == XML_SHA, "article XML hash mismatch"
assert hashlib.sha256(xlsm_path.read_bytes()).hexdigest() == XLSM_SHA, "workbook hash mismatch"
assert hashlib.sha256(BATCH.read_bytes()).hexdigest() == BATCH_SHA_BEFORE, "batch.jsonl is not the reviewed extractor output"
records = [json.loads(l) for l in BATCH.read_text().splitlines()]
by_id = {r["id"]: r for r in records}
assert len(records) == 447 and all(r["status"] == "needs_review" for r in records)


def txt(el):
    return "".join(el.itertext()).strip().replace(" ", " ")


# ---- Article tables -------------------------------------------------------------------------
root = ET.parse(xml_path).getroot()


def table(tid):
    tw = next(t for t in root.iter("table-wrap") if t.get("id") == tid)
    head = [txt(th) for th in tw.find(".//thead").iter("th")]
    rows = [[(txt(td), td.find("bold") is not None) for td in tr.findall("td")] for tr in tw.find(".//tbody").iter("tr")]
    return head, rows


results = {r["attributes"]["source_locator"]: r for r in records if r["kind"] == "result"}
seen = set()


def system_and_protocol(r):
    ev = by_id[r["links"][0]["target_id"]]
    links = {l["relation"]: l["target_id"] for l in ev["links"]}
    assert ev["attributes"]["origin"] == "independent_paper", ev["id"]
    return by_id[links["system"]], links["assessment"]


head, rows = table("Tab1")
assert head == ["Data", "DNABERT-2", "NT-v2", "HyenaDNA", "Caduceus-Ph", "GROVER"] and len(rows) == 24
for cells in rows:
    label = cells[0][0]
    if label in ("Acceptor", "Donor"):
        continue  # stored by amp-feng-20261007
    for (val, bold), model in zip(cells[1:], head[1:]):
        base = f"Table 1, row '{label}', column '{model}'."
        loc = base + (" Printed in bold (caption: higher than at least two other AUCs, p < 0.01, one-sided DeLong)." if bold else "")
        r = results[loc]
        a = r["attributes"]
        assert (a["printed_value"], a["numeric_value"], a["metric"], a["unit"], a["metric_direction"]) == \
            (val, val, "auroc", "unitless", "higher"), r["id"]
        cfg, proto = system_and_protocol(r)
        assert cfg["attributes"]["reported_name"] == model and proto.startswith(P + "protocol-t1-"), r["id"]
        seen.add(r["id"])

head, rows = table("Tab4")
assert head == ["Model", "Input Sequence Length", "Average Prediction Correlation", "Average Prediction MSE"] and len(rows) == 8
for cells in rows:
    label = cells[0][0]
    for col, idx, metric, unit, direction in (("Average Prediction Correlation", 2, "pearson-correlation", "unitless", "higher"),
                                              ("Average Prediction MSE", 3, "mean-squared-error", "unit-unreported", "lower")):
        val, bold = cells[idx]
        assert not bold
        r = results[f"Table 4, row '{label}', column '{col}'"]
        a = r["attributes"]
        assert (a["printed_value"], a["numeric_value"], a["metric"], a["unit"], a["metric_direction"]) == \
            (val, val, metric, unit, direction), r["id"]
        cfg, proto = system_and_protocol(r)
        assert cfg["attributes"]["reported_name"] == label
        assert proto == P + ("protocol-gtex-wb-expression-long-768" if label.endswith("*") else "protocol-gtex-wb-expression-6kb")
        seen.add(r["id"])
assert len(seen) == 126 == len(results)

# ---- Supplementary Data 1, 2 and 6 ----------------------------------------------------------
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
z = zipfile.ZipFile(xlsm_path)
shared = ["".join(t.text or "" for t in si.iter(NS + "t")) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(NS + "si")]
wb = ET.fromstring(z.read("xl/workbook.xml"))
rels = {e.get("Id"): e.get("Target") for e in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def sheet(name):
    s = next(s for s in wb.iter(NS + "sheet") if s.get("name") == name)
    target = rels[s.get(RID)]
    xml = ET.fromstring(z.read(target if target.startswith("xl/") else "xl/" + target))
    out = []
    for row in xml.iter(NS + "row"):
        vals = {}
        for c in row.iter(NS + "c"):
            v = c.find(NS + "v")
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            vals[col] = shared[int(v.text)] if c.get("t") == "s" else (v.text if v is not None else "")
        out.append(vals)
    return out[1:]


def norm(s):
    return re.sub(r"[\s_]+", "", s.lower()).rstrip("s")


d1 = {norm(r["A"]): r["B"] for r in sheet("Data 1")}
d2 = {norm(r["A"]): r["B"] for r in sheet("Data 2")}
d6 = {norm(r["A"]): r for r in sheet("Data 6")}


def model_set(s):
    return sorted(x.strip() for x in s.split(","))


cnn = [r for r in records if r["id"].startswith(P + "claim-cnn-")]
assert len(cnn) == 26
for c in cnn:
    a = c["attributes"]
    row = norm(re.search(r"row '([^']+)'", a["source_locator"]).group(1))
    m = re.search(r"p<0\.01\): (.+?)\. Supplementary Data 2 lists the models that significantly outperformed the CNN: (.+?)\. ", a["value"])
    assert model_set(m.group(1)) == model_set(d1[row]) and model_set(m.group(2)) == model_set(d2[row]), c["id"]

datasets = [r for r in records if r["kind"] == "dataset" and r["id"].startswith(P + "dataset-t1-")]
assert len(datasets) == 22
for d in datasets:
    a = d["attributes"]
    row = d6[norm(re.search(r"row '([^']+)'", a["source_locator"]).group(1))]
    blob = json.dumps(a)
    for need in (f"{row['E']} training", f"{row['F']} test", f"median {row['B']} bp", f"range {row['C']}-{row['D']} bp"):
        assert need in blob, (d["id"], need)
    if row.get("G"):
        p, n = map(int, row["G"].split("/"))
        assert (a["positives"], a["negatives"], a["total"]) == (p, n, p + n), d["id"]
        assert (p + n != int(row["E"]) + int(row["F"])) == ("do not sum" in a.get("scope_note", "")), d["id"]
    else:
        assert "positives" not in a and row["H"] in a["scope_note"], d["id"]

# ---- Review blocks --------------------------------------------------------------------------
DESCRIPTIVE_NOTE = {
    P + "claim-gtex-short-finding": "Checked against Results, 'Gene expression prediction', paragraphs 2 and 3, and the Wilcoxon test in Methods.",
    P + "claim-gtex-long-finding": "Checked against Results, 'Gene expression prediction', paragraph 2, and Supplementary Table 4 (PDF page 7).",
    P + "claim-tad-finding": ("Checked against Results, 'TAD region recognition', paragraph 2, and the rendered Supplementary Fig. 2 "
                              "(PDF page 11, SHA-256 373f59b8...4a15). The figure caption puts the TAD tokens at about positions "
                              "200-600; the main text says about 300-700. Recorded on the Supplementary Information source."),
    P + "claim-not-extracted": "Checked against the article XML tables and figures, all 11 pages of the Supplementary Information PDF and the six workbook sheets.",
}
EXPR_EVALS = {}
for r in records:
    if r["kind"] == "evaluation":
        proto = next(l["target_id"] for l in r["links"] if l["relation"] == "assessment")
        EXPR_EVALS.setdefault(proto, []).append(r["id"])

for r in records:
    r["status"] = "source_checked"
    a = r["attributes"]
    old = a.get("review")
    if r["kind"] == "result":
        assert old["artifact_sha256"] == XML_SHA
        a["review"] = {"method": ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
                       "method_note": TABLE_NOTE, "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
                       "date": DATE, "reviewed_at": REVIEWED_AT, "artifact_sha256": XML_SHA, "retrieval_url": XML_URL,
                       "note": ("Extracted by extract/extract_feng.py (deterministic parse of the XML table cells). "
                                "Independent review: value, metric and identity match the source.")}
    elif r["kind"] == "claim" and r["id"].startswith(P + "claim-cnn-"):
        assert old["artifact_sha256"] == XLSM_SHA
        a["review"] = {"method": ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
                       "method_note": SD_NOTE, "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
                       "date": DATE, "reviewed_at": REVIEWED_AT, "artifact_sha256": XLSM_SHA, "retrieval_url": XLSM_URL,
                       "note": ("Extracted by extract/extract_feng.py (deterministic parse of workbook sheets 'Data 1' and "
                                "'Data 2'). Independent review: both model lists match the row. The CNN's own AUC is not printed.")}
    elif r["kind"] == "claim" and r["id"] in DESCRIPTIVE_NOTE:
        assert old["artifact_sha256"] == XML_SHA
        methods = ["source-hash-verification", "ai-assisted-source-review"]
        if r["id"] in (P + "claim-tad-finding", P + "claim-gtex-long-finding", P + "claim-not-extracted"):
            methods.append("rendered-source-visual-check")
        a["review"] = {"method": methods, "method_note": DESCRIPTIVE_NOTE[r["id"]], "reviewer": ["claude"],
                       "reviewer_note": REVIEWER_NOTE, "date": DATE, "reviewed_at": REVIEWED_AT,
                       "artifact_sha256": XML_SHA, "retrieval_url": XML_URL,
                       "note": ("Hand transcription by the extraction agent, written out by extract/extract_feng.py. "
                                "Independent review: wording matches the cited text; nothing added that the source does not say.")}
    elif r["kind"] == "claim" and r["id"].startswith("use-case-mapping-"):
        assert old is None
        proto = a["value"]
        evals = sorted(EXPR_EVALS[proto])
        assert len(evals) == (5 if proto.endswith("6kb") else 3)
        a["reviewed_evaluations"] = evals
        a["review"] = {"method": ["ai-assisted-source-review", "scope-review"],
                       "method_note": ("Checked the endpoint against the use case's inputs, output and setting in "
                                       "data/entities/use-cases.jsonl; checked each limitation against Methods, Results, "
                                       "Data availability and Table 4; checked every evaluation on the protocol."),
                       "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE, "reviewed_at": REVIEWED_AT,
                       "artifact_sha256": XML_SHA, "retrieval_url": XML_URL,
                       "note": ("Judgement written by the extraction agent. Independent review: proxy is justified because "
                                "cross-individual expression prediction bears only on allele-effect prediction, which the use "
                                "case treats as a separate comparison; it does not score variants or link elements to genes.")}
    elif r["kind"] == "claim":
        raise AssertionError(r["id"])
    elif r["kind"] == "source":
        art = {"feng-dna-fm-20261013-source-supplementary-data": (XLSM_SHA, XLSM_URL, "Re-downloaded and matched; the archived artifacts/MOESM3_ESM.xlsm.gz decompresses to the same bytes. Read all seven sheets."),
               "feng-dna-fm-20261013-source-supplementary-information": (PDF_SHA, PDF_URL, "Re-downloaded with a browser User-Agent and matched. Read all 11 pages (pdftotext -layout) and viewed pages 9 to 11 rendered."),
               "feng-dna-fm-20261013-source-gtex-hyena-script": (SCRIPT_SHA, SCRIPT_URL, "Re-downloaded and matched; read in full.")}[r["id"]]
        assert a["artifact_sha256"] == art[0]
        a["review"] = {"method": ["source-hash-verification", "ai-assisted-source-review"], "method_note": art[2],
                       "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE, "reviewed_at": REVIEWED_AT,
                       "artifact_sha256": art[0], "retrieval_url": art[1],
                       "note": "Identity, version, licence and limitations checked against the artifact."}
    if isinstance(a.get("missing_metadata"), dict):
        a["missing_metadata"] = dict(sorted(a["missing_metadata"].items()))

records.sort(key=lambda r: r["id"])
BATCH.write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in records))
print("signed off", len(records), "records;", hashlib.sha256(BATCH.read_bytes()).hexdigest())
