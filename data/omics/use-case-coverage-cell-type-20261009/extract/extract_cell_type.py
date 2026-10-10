"""Deterministic extraction of Wu et al. 2025 (scFM-Bench) cross-atlas annotation transfer tables into a records batch.

Usage: python3 -I extract_cell_type.py <article.xml> <MOESM3.xlsx> <batch-dir>

Reads the pinned article XML and Additional file 3 (XLSX cell XML, standard library), asserts
every label it relies on in Supplementary Tables S2 and S3, and writes batch.jsonl (store
form), claims.csv and extract/judgements.json. printed_value is the shortest decimal that
round-trips to the stored number.
"""
import csv, hashlib, json, re, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

XML, XLSX, BATCH = sys.argv[1:4]
P = "cell-type-20261009"
UC = "use-case-cell-type-annotation-transfer"
UC_NAME = "Transfer cell-type annotations to a new dataset"
DATE = "2026-10-09"
FACETS = {"areas": ["cells-tissues"], "contexts": ["research"]}
NOTE = ("Extracted by deterministic parse of the pinned XLSX cell XML (extract/extract_cell_type.py), with row and column "
        "labels asserted. printed_value is the shortest decimal that round-trips to the stored number. Pending independent review.")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
records, claims_rows = [], []


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def need(got, expected, where):
    if got != expected:
        raise SystemExit(f"Label check failed at {where}: expected {expected!r}, got {got!r}")


def workbook(path):
    z = zipfile.ZipFile(path)
    ss = ["".join(t.text or "" for t in si.iter("{%s}t" % NS["m"]))
          for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for sh in wb.find("m:sheets", NS):
        tgt = rels[sh.get("{%s}id" % NS["r"])].lstrip("/")
        tgt = tgt if tgt.startswith("xl/") else "xl/" + tgt
        cells = {}
        for c in ET.fromstring(z.read(tgt)).iter("{%s}c" % NS["m"]):
            v, t = c.find("m:v", NS), c.get("t")
            if v is not None:
                cells[c.get("r")] = (ss[int(v.text)], False) if t == "s" else (v.text, t not in ("str", "e"))
        out[sh.get("name")] = cells
    return out


def printed_numeric(cell):
    text, is_num = cell
    if not is_num:
        raise SystemExit(f"Expected a number, got {text!r}")
    s = repr(float(text))
    if s.endswith(".0"):
        s = s[:-2]
    return s, format(Decimal(s), "f")


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids, "links": links or [],
         "attributes": attributes or {}}
    records.append(r)
    return r


def review(note=NOTE, method=("deterministic-table-parse",)):
    return {"method": list(method), "reviewer": ["claude"],
            "reviewer_note": "Claude (Opus 5.5) research agent, the extractor; no independent or human review claimed",
            "date": DATE, "note": note}


def claim(id_, subject, field, value, source_id, locator):
    rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", [source_id],
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator,
         "review": review("Transcribed from the pinned article XML. Pending independent review.", ("transcription",))}, facets={})
    claims_rows.append([id_, source_id, locator, value, "claim"])


# ================================================================= sources
S_ART, S_SUPP = f"{P}-source-wu2025", f"{P}-source-wu2025-supp"
root = ET.parse(XML).getroot()
lic = " ".join("".join(next(root.iter("license")).itertext()).split())
need("Attribution-NonCommercial-NoDerivatives 4.0" in lic, True, "article licence")
for sid, name, art_url, path, version, retrieved, media in [
        (S_ART, "Biology-driven insights into the power of single-cell foundation models",
         "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12492631/fullTextXML", XML,
         "Genome Biology 26:334, published 2025-10-03; PMC12492631 full-text XML", "2026-10-09T21:22:13Z", "application/xml"),
        (S_SUPP, "Wu et al. 2025, Additional file 3 (Supplementary Tables S1-S13)",
         "https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-025-03781-6/MediaObjects/13059_2025_3781_MOESM3_ESM.xlsx", XLSX,
         "13059_2025_3781_MOESM3_ESM.xlsx (38,926 bytes), as linked from the article XML <supplementary-material id=\"MOESM3\">",
         "2026-10-09T21:22:24Z", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")]:
    rec(sid, "source", name, "Primary source retrieved and hashed for the cell-type annotation transfer use-case pass.", [], [],
        {"url": "https://doi.org/10.1186/s13059-025-03781-6", "artifact_url": art_url, "version": version, "retrieved_at": retrieved,
         "artifact_sha256": sha(path), "doi": "10.1186/s13059-025-03781-6", "publication_status": "peer_reviewed",
         "licence": "CC-BY-NC-ND-4.0", "media_type": media, "venue": "Genome Biology", "year": 2025,
         "source_locator": "Licence statement in the article XML <license> element; the article licence covers its additional files",
         **({"evidence_concerns": [{
             "source_id": S_SUPP,
             "message": "Results 'Cross-dataset validation' paragraph 4 says logit aggregation outperforms majority voting in Accuracy@1 while majority voting achieves higher macro-F1. Supplementary Tables S2 and S3 print the reverse in both directions: majority voting has the higher Accuracy@1 (0.758 vs 0.753; 0.83 vs 0.82) and logit aggregation the higher macro-F1 (0.163 vs 0.119; 0.285 vs 0.28). Table values are recorded.",
             "source_locator": "Supplementary Table S2 rows 27-28 and Table S3 rows 27-28 versus Results 'Cross-dataset validation' paragraph 4",
             "artifact_sha256": sha(XLSX), "reviewed_at": "2026-10-09T21:30:00Z", "review_method": "ai-assisted-source-review"}]} if sid == S_SUPP else {})})

# ================================================================= tables
wb = workbook(XLSX)
TITLES = {"Table S2": ("Table S2. Performance of single models and ensemble strategies in transferring annotations from the Tabula Sapiens dataset to the HLCA dataset.", "ts-to-hlca", "Tabula Sapiens", "HLCA"),
          "Table S3": ("Table S3. Performance of single models and ensemble strategies in transferring annotations from the HLCA dataset to the Tabula Sapiens dataset.", "hlca-to-ts", "HLCA", "Tabula Sapiens")}
SINGLE = {"LangCell", "Geneformer", "UCE", "scFoundation", "scGPT", "scCello"}
parsed = {}
for sheet, (title, key, ref, query) in TITLES.items():
    t = wb[sheet]
    need(t["A1"][0], title, f"{sheet} title")
    need([t["A2"][0], t["B2"][0], t["C2"][0]], ["Model", "Accuracy@1", "Macro-F1"], f"{sheet} header")
    need([t["A3"][0], t["A10"][0], t["A26"][0]], ["Individual model", "Pairwise ensemble", "Full ensemble"], f"{sheet} section labels")
    rows = []
    for r in list(range(4, 10)) + list(range(11, 26)) + [27, 28]:
        rows.append((r, t[f"A{r}"][0], t[f"B{r}"], t[f"C{r}"]))
    need(f"A29" in t, False, f"{sheet} ends at row 28")
    need({x[1] for x in rows[:6]}, SINGLE, f"{sheet} individual models")
    pairs = {frozenset(x[1].split(" + ")) for x in rows[6:21]}
    need(len(pairs), 15, f"{sheet} 15 distinct pairs")
    need(all(len(p) == 2 and p <= SINGLE for p in pairs), True, f"{sheet} pairs drawn from the six models")
    need([x[1] for x in rows[21:]], ["Logit aggregation", "Majority voting"], f"{sheet} full ensembles")
    parsed[sheet] = rows
# cross-checks against the text (Results 'Cross-dataset validation' paragraph 3)
gs = {x[1]: x for x in parsed["Table S2"]}
need(printed_numeric(gs["scGPT"][2])[0], "0.674", "S2 scGPT Accuracy@1 vs text 67.4%")
need(printed_numeric(gs["Geneformer + scGPT"][2])[0], "0.756", "S2 Geneformer + scGPT Accuracy@1 vs text 75.6%")

for sheet in parsed:
    full = {x[1]: x for x in parsed[sheet][21:]}
    need(float(full["Majority voting"][2][0]) > float(full["Logit aggregation"][2][0]), True, f"{sheet} majority voting has the higher Accuracy@1 (evidence concern)")
    need(float(full["Logit aggregation"][3][0]) > float(full["Majority voting"][3][0]), True, f"{sheet} logit aggregation has the higher macro-F1 (evidence concern)")

# ================================================================= systems
MODEL = {"scGPT": "catalog-model-scgpt", "scFoundation": "catalog-model-scfoundation", "Geneformer": "catalog-model-geneformer"}
for key, name, desc in [("uce", "UCE (Universal Cell Embeddings)", "Single-cell foundation model producing cell embeddings from protein-embedded gene tokens (Table 1)."),
                        ("langcell", "LangCell", "Single-cell foundation model pretrained on cell-text pairs, initialised from Geneformer (Table 1)."),
                        ("sccello", "scCello", "Single-cell foundation model pretrained with cell-ontology alignment losses (Table 1).")]:
    mid = f"{P}-model-{key}"
    rec(mid, "model", name, desc, [S_ART], [],
        {"reported_name": name, "entity_level": "family", "source_locator": "Table 1",
         "missing_metadata": {"version": {"reason": "unreported", "note": "Checkpoint not named in the article text read"}}},
        facets={**FACETS, "method_types": ["foundation_model"]})
    MODEL[{"uce": "UCE", "langcell": "LangCell", "sccello": "scCello"}[key]] = mid
ENS = f"{P}-method-logit-ensemble"
rec(ENS, "method", "Ensemble of scFM embedding classifiers", "Combines OnClass classifiers trained on different scFM embeddings by summing logits (pairwise and full) or by majority voting (full).",
    [S_ART], [], {"reported_name": "Pairwise ensemble / Full ensemble", "entity_level": "method",
                  "source_locator": "Results 'Cross-dataset validation' paragraphs 3-4",
                  "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; members are on configurations"}}},
    facets={**FACETS, "method_types": ["foundation_model"]})
ONCLASS = "OnClass bilinear classifier on zero-shot cell embeddings, trained on 20% of the reference (StratifiedShuffleSplit 2:8, then 90/10 train/validation)"
CFG = {}
for m in sorted(SINGLE):
    cid = f"{P}-config-wu2025-{m.lower()}-onclass"
    CFG[m] = cid
    rec(cid, "configuration", f"{m} zero-shot embeddings with OnClass (Wu et al. 2025)", f"OnClass classifier on {m} cell embeddings.", [S_ART, S_SUPP],
        [{"relation": "configuration_of", "target_id": MODEL[m]}],
        {"reported_name": m, "source_locator": "Supplementary Tables S2-S3 column 'Model'; Methods 'OnClass' and 'Batch integration and cell type annotation'",
         "foundation_model_eligible": True, "parameters": ONCLASS,
         "missing_metadata": {"version": {"reason": "unreported", "note": "Model checkpoint not named in the article text read; parameter counts are in Table 1"}}},
        facets={**FACETS, "method_types": ["foundation_model"]})
def cfg_key(label):
    """Configuration identity: a pair is the same configuration whichever order the table prints it in."""
    return " + ".join(sorted(label.split(" + "), key=str.lower)) if " + " in label else label


for sheet in parsed:
    for r, label, _, _ in parsed[sheet][6:]:
        key = cfg_key(label)
        if key in CFG:
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
        if " + " in key:
            members = key.split(" + ")
            params = f"Sum of the output logits of the {members[0]} and {members[1]} OnClass classifiers, then softmax"
        else:
            members = sorted(SINGLE)
            params = ("Sum of the output logits of all six OnClass classifiers, then softmax" if key == "Logit aggregation"
                      else "Majority vote over the six OnClass classifiers' predictions")
        cid = f"{P}-config-wu2025-ensemble-{slug}"
        CFG[key] = cid
        links = [{"relation": "configuration_of", "target_id": ENS}] + [{"relation": "uses_model", "target_id": MODEL[x]} for x in members]
        rec(cid, "configuration", f"Ensemble {key} (Wu et al. 2025)", f"Ensemble of OnClass classifiers: {key}.", [S_ART, S_SUPP], links,
            {"reported_name": key, "source_locator": "Supplementary Tables S2-S3 column 'Model' Results 'Cross-dataset validation' paragraphs 3-4",
             "foundation_model_eligible": True, "parameters": params,
             "missing_metadata": {"version": {"reason": "inapplicable", "note": "An ensemble of the listed configurations"}}},
            facets={**FACETS, "method_types": ["foundation_model"]})

# ================================================================= datasets, protocols, evaluations, results
DATA = {"HLCA": (f"{P}-data-wu2025-hlca-core", "HLCA core (CELLxGENE), 37 leaf cell types after processing",
                 "585 K cells from healthy lung across 107 individuals; label column 'cell_type'; 37 leaf cell types kept after removing non-leaf terms and types with fewer than 10 cells"),
        "Tabula Sapiens": (f"{P}-data-wu2025-tabula-sapiens", "Tabula Sapiens (CELLxGENE), 120 leaf cell types after processing",
                           "483 K cells from 24 tissues across 15 donors; label column 'cell_ontology_class'; 120 leaf cell types kept after the same processing")}
for k, (did, name, pop) in DATA.items():
    rec(did, "dataset", name, "Public atlas used as reference or query for annotation transfer; labels are the atlas annotations.", [S_ART], [],
        {"version": "CELLxGENE collection as downloaded by the authors (Table 2)", "population": pop,
         "split": "Reference model trained on a 20% stratified split; query test set is every cell of the 14 cell types shared by the two atlases",
         "source_locator": "Table 2; Methods 'Batch integration and cell type annotation' paragraphs 1-3"})
PROT, JUDGEMENTS = {}, []
for order, (sheet, (title, key, ref, query)) in enumerate(TITLES.items(), start=1):
    pid = f"{P}-protocol-wu2025-{key}"
    did = DATA[query][0]
    rec(pid, "protocol", f"Cross-atlas annotation transfer, {ref} to {query}, 14 shared cell types (Wu et al. 2025 {sheet})",
        f"Classifier trained on the {ref} reference applied to all {query} cells of the 14 cell types shared by both atlases.", [S_ART, S_SUPP],
        [{"relation": "uses_data", "target_id": did}],
        {"protocol": (f"Zero-shot cell embeddings from each scFM feed an OnClass classifier trained on the {ref} intra-dataset split; the trained model is applied "
                      f"unchanged to every {query} cell of the 14 shared leaf cell types. Accuracy@1 is the share of cells whose top label is correct; macro-F1 averages F1 over cell types. Labels are the atlases' own annotations."),
         "version": sheet, "source_locator": "Results 'Cross-dataset validation'; Methods 'Batch integration and cell type annotation' paragraph 3; 'Standard benchmarking metrics'",
         "limitations": ["Atlas annotations are the truth labels; they are not independent of curation choices.",
                         "Only the 14 shared cell types are scored; no rejection of unshared types is measured in these tables.",
                         "Baselines (logistic regression, scVI, HVG) are reported only in Fig. 3b, not in the tables.",
                         "Macro-F1 is much lower than accuracy (0.08-0.28), reflecting poor transfer to rare types (Results)."],
         "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "One run per configuration printed"}}})
    PROT[sheet] = pid
    for r, label, acc, f1 in parsed[sheet]:
        cid = CFG[cfg_key(label)]
        slug = cid.split("-config-wu2025-")[1]
        ev = f"{P}-eval-wu2025-{key}-{slug}"
        rec(ev, "evaluation", f"{label}: {ref} to {query} transfer (Wu et al. 2025)", "Published annotation transfer benchmark; transcribed, not reproduced.",
            [S_ART, S_SUPP], [{"relation": "system", "target_id": cid}, {"relation": "assessment", "target_id": pid}, {"relation": "data", "target_id": did}],
            {"origin": "independent_paper", "protocol": pid, "version": f"Primary source as retrieved {DATE}",
             "comparison": {"protocol_id": pid, "dataset_version": "CELLxGENE downloads (Table 2)", "split": "Reference 20% stratified training split; query all shared-type cells",
                            "population": "14 shared leaf cell types", "inputs": "Zero-shot scFM cell embeddings", "adaptation": "OnClass classifier trained on the reference; scFM frozen",
                            "metric_implementation": "Accuracy@1 and macro-F1 over shared types", "aggregation": "All query cells of shared types", "budget": None},
             "source_locator": f"{sheet} row {r}", "source_label": f"Row label as printed: {label}",
             "limitations": ["The source does not state that any author developed the evaluated scFMs; origin is recorded as independent_paper on that basis."]})
        for cell, col, metric, qual, rslug in [(acc, "B", "top-1-accuracy", "Accuracy@1 over cells of the 14 shared cell types", "accuracy-at-1"),
                                               (f1, "C", "macro-f1", "over the 14 shared cell types", "macro-f1")]:
            pv, nv = printed_numeric(cell)
            rid = f"{P}-result-wu2025-{key}-{slug}-{rslug}"
            loc = f"{sheet}, cell {col}{r}, row '{label}', column '{'Accuracy@1' if col == 'B' else 'Macro-F1'}'"
            rec(rid, "result", f"{label} {ref} to {query} {metric}", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                [S_SUPP], [{"relation": "evaluation", "target_id": ev}],
                {"metric": metric, "metric_direction": "higher", "unit": "fraction", "printed_value": pv, "numeric_value": nv, "metric_qualifier": qual,
                 "source_locator": loc, "missing_metadata": {"uncertainty": {"reason": "unreported"}}, "review": review()}, facets={})
            claims_rows.append([rid, S_SUPP, loc, pv, "result"])
    jid = f"use-case-mapping-cell-type-20261009-wu2025-{key}"
    rationale = ("Six single-cell foundation models and their ensembles transfer labels from one atlas to another on the same query cells, scored by macro-F1, which is the cross-study transfer comparison the use case asks for. "
                 "It is proxy evidence: the truth labels are atlas annotations (use-case exclusion), only the 14 shared cell types are scored so rejection of unsupported populations is not measured in these tables, and the conventional baselines appear only in a figure.")
    attrs = {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": "proxy",
             "endpoint": f"Accuracy@1 and macro-F1 for OnClass on six scFM embeddings, 15 pairwise and 2 full ensembles, transferring labels from {ref} to {query} on the 14 shared cell types",
             "rationale": rationale,
             "constraints": ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                             "Do not combine these results with another protocol's results; label sets, splits and classifiers differ between sources.",
                             "Prefer macro-F1 to accuracy here; accuracy is dominated by abundant cell types."],
             "limitations": ["Atlas labels as truth; no independent marker or expert validation.",
                             "No unknown-population rejection in the tables; the novel-type AUROC and AUPRC results are figure-only (Fig. S22).",
                             "Conventional baselines (logistic regression, scVI) only in Fig. 3b.", "Zero-shot embeddings with one classifier (OnClass); no fine-tuning."],
             "citation_locators": [{"source_id": S_SUPP, "locator": sheet}, {"source_id": S_ART, "locator": "Results 'Cross-dataset validation'; Methods"}],
             "source_locator": f"{S_SUPP}: {sheet}; {S_ART}: Results 'Cross-dataset validation' and Methods", "revision": 1,
             "reason": "Recorded from the cell-type annotation transfer use-case pass 2026-10-09 (data/omics/use-case-coverage-cell-type-20261009). Draft until an independent review.",
             "comparison_group": "wu2025-cross-atlas", "comparison_title": "Cross-atlas label transfer with foundation-model embeddings (Wu et al. 2025)",
             "headline_metric": "macro-f1", "stratum_label": f"{ref} to {query}", "stratum_order": order}
    rec(jid, "claim", f"Relevance of cross-atlas annotation transfer, {ref} to {query} (Wu et al. 2025) to \"{UC_NAME}\"", rationale, [S_ART, S_SUPP],
        [{"relation": "subject", "target_id": UC}], attrs, facets={})
    JUDGEMENTS.append({"judgement_id": jid, "protocol_id": pid, "relevance": "proxy", "comparison_group": "wu2025-cross-atlas",
                       "stratum_label": f"{ref} to {query}", "stratum_order": order})
claim(f"{P}-claim-wu2025-macro-f1-gap", PROT["Table S2"], "accuracy_versus_macro_f1",
      "Although cross-dataset accuracy scores are all above 0.6, macro-F1 scores are much lower, which the authors read as poor handling of shifts in cell-type proportions and of rare subpopulations.",
      S_ART, "Results 'Cross-dataset validation' paragraph 2")
claim(f"{P}-claim-wu2025-scvi-gene-match", PROT["Table S2"], "baseline_gene_overlap",
      "The scVI baseline (figure only) depends on the reference HVGs being present in the query: 99.95% matched from HLCA to Tabula Sapiens but 71.35% from Tabula Sapiens to HLCA, where scVI fell short of all scFMs.",
      S_ART, "Results 'Cross-dataset validation' paragraph 2")

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
if len(ids) != len(set(ids)):
    raise SystemExit("Duplicate IDs: " + ", ".join(k for k, v in Counter(ids).items() if v > 1))
with open(f"{BATCH}/batch.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claims_rows.sort(key=lambda r: (r[0], r[2]))
with open(f"{BATCH}/claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
with open(f"{BATCH}/extract/judgements.json", "w", encoding="utf-8") as f:
    json.dump(JUDGEMENTS, f, indent=2, ensure_ascii=False)
print(json.dumps(Counter(r["kind"] for r in records), sort_keys=True))
