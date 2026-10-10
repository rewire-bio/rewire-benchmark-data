"""Deterministic extraction of the Csendes et al. 2025 perturbation-response benchmark into a records batch.

Usage: python3 -I extract_perturbation.py <article.xml> <supplement.xlsx> <batch-dir>

Reads the pinned article XML and Supplementary Material 4 (XLSX cell XML, standard library),
asserts every label it relies on, and writes batch.jsonl (store form), claims.csv and
extract/judgements.json. printed_value is the shortest decimal that round-trips to the stored
number (the workbook stores 15-17 significant digits); display formatting was not applied.
"""
import csv, hashlib, json, re, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

XML, XLSX, BATCH = sys.argv[1:4]
P = "perturbation-response-20261009"
UC = "use-case-genetic-perturbation-response"
UC_NAME = "Assess models for genetic perturbation experiments"
DATE = "2026-10-09"
FACETS = {"areas": ["cells-tissues"], "contexts": ["research"]}
NOTE = ("Extracted by deterministic parse of the pinned XLSX cell XML (extract/extract_perturbation.py), with row and column "
        "labels asserted. printed_value is the shortest decimal that round-trips to the stored number; display formatting "
        "was not applied. Pending independent review.")
records, claims_rows = [], []
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def need(got, expected, where):
    if got != expected:
        raise SystemExit(f"Label check failed at {where}: expected {expected!r}, got {got!r}")


def workbook(path):
    z = zipfile.ZipFile(path)
    ss = [("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
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
            if v is None:
                continue
            cells[c.get("r")] = (ss[int(v.text)], False) if t == "s" else (v.text, t not in ("str", "e"))
        out[sh.get("name")] = cells
    return out


def printed_numeric(cell):
    text, is_num = cell
    if not is_num:
        raise SystemExit(f"Expected a number, got text {text!r}")
    s = repr(float(text))
    if s.endswith(".0"):
        s = s[:-2]
    if "e" in s or "E" in s:
        s = format(Decimal(s), "f")
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


def claim(id_, subject, field, value, source_id, locator, method=("transcription",), note="Transcribed from the pinned source. Pending independent review."):
    rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", [source_id],
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator, "review": review(note, method)}, facets={})
    claims_rows.append([id_, source_id, locator, value, "claim"])


# ================================================================= sources
S_ART, S_SUPP = f"{P}-source-csendes2025", f"{P}-source-csendes2025-supp"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
for sid, name, art_url, path, version, retrieved, media in [
        (S_ART, "Benchmarking foundation cell models for post-perturbation RNA-seq prediction", f"{EPMC}/PMC12016270/fullTextXML", XML,
         "BMC Genomics 26:393, published 2025-04-23; PMC12016270 full-text XML", "2026-10-09T20:58:48Z", "application/xml"),
        (S_SUPP, "Csendes et al. 2025, Supplementary Material 4 (Supplementary Tables 1-3)", f"{EPMC}/PMC12016270/supplementaryFiles", XLSX,
         "12864_2025_11600_MOESM4_ESM.xlsx from the Europe PMC supplementary bundle (hash is of the workbook; the bundle zip is rebuilt per request)",
         "2026-10-09T20:58:56Z", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")]:
    rec(sid, "source", name, "Primary source retrieved and hashed for the genetic perturbation response use-case pass.", [], [],
        {"url": "https://doi.org/10.1186/s12864-025-11600-2", "artifact_url": art_url, "version": version, "retrieved_at": retrieved,
         "artifact_sha256": sha(path), "doi": "10.1186/s12864-025-11600-2", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
         "media_type": media, "venue": "BMC Genomics", "year": 2025,
         "source_locator": "Licence from the Europe PMC record (cc by) and the article XML <license> element; the article licence covers its supplementary material"})

root = ET.parse(XML).getroot()
lic = " ".join("".join(next(root.iter("license")).itertext()).split())
need("Creative Commons Attribution 4.0" in lic, True, "article licence")

# ================================================================= tables
wb = workbook(XLSX)
need(list(wb)[:3], ["Supplementary Table 1", "Supplementary Table 2", "Supplementary Table 3"], "sheet names")
t1, t2 = wb["Supplementary Table 1"], wb["Supplementary Table 2"]
need([t1[c][0] for c in ("A1", "B1", "C1", "D1")], ["Dataset", "Train perturbations", "Validation perturbations", "Test perturbations"], "S1 header")
need([t1[f"A{r}"][0] for r in range(2, 6)], ["adamson", "norman", "replogle_k562", "replogle_rpe1"], "S1 rows")
need([t1[c][0] for c in ("B7", "C7", "D7", "E7")], ["combo_seen0", "combo_seen1", "combo_seen2", "unseen_single"], "S1 Norman subgroup header")
need([t1["A8"][0], t1["A9"][0]], ["Validation", "Test"], "S1 Norman subgroup rows")
H2 = ["dataset", "model", "Pearson", "Pearson DE", "Pearson Delta ", "Pearson Delta DE", "Pearson Delta DE (based on Wilcoxon)", "Pearson Delta DE without KOd gene"]
need([t2[f"{c}1"][0] for c in "ABCDEFGH"], H2, "S2 header")
DATASETS = ["Adamson", "Norman", "Replogle_K562", "Replogle_RPE1"]
MODELS = ["RF_go", "RF_scElmo", "RF_scFoundation", "RF_scGPT", "EN_go", "EN_scElmo", "EN_scFoundation", "EN_scGPT",
          "KNN_go", "KNN_scElmo", "KNN_scFoundation", "KNN_scGPT", "mean", "scGPT", "scFoundation"]
for di, ds in enumerate(DATASETS):
    for mi, m in enumerate(MODELS):
        r = 2 + di * 15 + mi
        need((t2[f"A{r}"][0], t2[f"B{r}"][0]), (ds, m), f"S2 row {r}")
need(f"A62" in t2, False, "S2 has 60 data rows")
for ds in DATASETS:
    for m in ("scGPT", "scFoundation"):
        r = 2 + DATASETS.index(ds) * 15 + MODELS.index(m)
        need(f"G{r}" in t2, False, f"S2 G{r} blank for {m} (no Wilcoxon value printed)")
# text cross-check (Results paragraph 6): Train Mean, scGPT, scFoundation and RF_go Pearson Delta
TEXT = {"mean": ["0.711", "0.557", "0.373", "0.628"], "scGPT": ["0.641", "0.554", "0.327", "0.596"],
        "scFoundation": ["0.552", "0.459", "0.269", "0.471"], "RF_go": ["0.739", "0.586", "0.480", "0.648"]}
for m, vals in TEXT.items():
    for di, v in enumerate(vals):
        r = 2 + di * 15 + MODELS.index(m)
        need(f"{float(t2[f'E{r}'][0]):.3f}", v, f"S2 E{r} against Results paragraph 6 ({m}, {DATASETS[di]})")

# ================================================================= methods and configurations
SCGPT, SCFOUND = "catalog-model-scgpt", "catalog-model-scfoundation"
M = {}
for key, name, desc in [
        ("random-forest", "Random forest regression on perturbed-gene features", "scikit-learn random forest regressor mapping a feature embedding of the perturbed gene(s) to the pseudo-bulk post-perturbation expression profile."),
        ("elastic-net", "Elastic net regression on perturbed-gene features", "scikit-learn elastic net regression mapping a feature embedding of the perturbed gene(s) to the pseudo-bulk post-perturbation expression profile."),
        ("knn", "k-nearest-neighbours regression on perturbed-gene features", "scikit-learn k-nearest-neighbours regressor mapping a feature embedding of the perturbed gene(s) to the pseudo-bulk post-perturbation expression profile."),
        ("train-mean", "Train Mean baseline", "Predicts, for every test perturbation, the mean post-perturbation pseudo-bulk expression over all training perturbations.")]:
    M[key] = f"{P}-method-{key}"
    rec(M[key], "method", name, desc, [S_ART], [],
        {"reported_name": name, "entity_level": "method", "source_locator": "Results 'Benchmarking of post-perturbation RNA-seq prediction methods' paragraph 4; Methods 'Baseline models'",
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
        facets={**FACETS, "method_types": ["conventional_pipeline"]})
FEAT = {"go": "Gene Ontology term matrix (decoupler) reduced to 256 principal components",
        "scElmo": "scELMO GPT-3.5 gene embeddings reduced to 256 principal components",
        "scFoundation": "scFoundation pretrained gene embeddings reduced to 256 principal components",
        "scGPT": "scGPT pretrained gene embeddings reduced to 256 principal components"}
TUNE = {"RF": ("random-forest", "n_estimators"), "EN": ("elastic-net", "l1_ratio"), "KNN": ("knn", "k neighbours")}
CFG = {}
for m in MODELS:
    slug = m.lower().replace("_", "-")
    cid = f"{P}-config-csendes2025-{slug}"
    CFG[m] = cid
    if "_" in m:
        algo, feat = m.split("_")
        mkey, hp = TUNE[algo]
        of, ver = M[mkey], "scikit-learn 1.5.2"
        params = f"Features: {FEAT[feat]} of the perturbed gene (summed for combinations); target: pseudo-bulk expression; {hp} tuned on the validation set"
        desc = f"{algo} regression with {feat} features of the perturbed gene."
        mtype = "conventional_pipeline"
    elif m == "mean":
        of, ver, params = M["train-mean"], None, "Mean post-perturbation pseudo-bulk expression over all training perturbations; identical prediction for every test perturbation"
        desc, mtype = "Train Mean baseline: the mean training response predicted for every test perturbation.", "conventional_pipeline"
    elif m == "scGPT":
        of, ver, params = SCGPT, "scGPT v0.2.1 fork, commit 7301b51", "Pretrained scGPT fine-tuned per dataset for 15 epochs (best validation epoch), default hyperparameters (dimension 512, 12 layers, 8 heads), cell-gears v0.0.1 data processing"
        desc, mtype = "Pretrained scGPT fine-tuned on each benchmark dataset, as reproduced by the authors.", "foundation_model"
    else:
        of, ver, params = SCFOUND, "scFoundation repository commit 69b0710", "Pretrained scFoundation gene embeddings as input to GEARS, fine-tuned per dataset for 10 epochs with effective batch size 32"
        desc, mtype = "scFoundation embeddings in GEARS, fine-tuned on each benchmark dataset, as reproduced by the authors.", "foundation_model"
    attrs = {"reported_name": m, "source_locator": "Supplementary Table 2 column 'model'; Methods 'Foundation models' and 'Baseline models'",
             "foundation_model_eligible": mtype == "foundation_model", "parameters": params}
    if ver:
        attrs["version"] = ver
    else:
        attrs["missing_metadata"] = {"version": {"reason": "inapplicable", "note": "A computed baseline with no software version"}}
    rec(cid, "configuration", f"{m} (Csendes et al. 2025)", desc, [S_ART, S_SUPP], [{"relation": "configuration_of", "target_id": of}], attrs,
        facets={**FACETS, "method_types": [mtype]})

# ================================================================= datasets and protocols
DS_INFO = {
    "Adamson": ("adamson", "Adamson et al. 2016 Perturb-seq, K562 CRISPRi single perturbations", "68,603 single cells, single-gene CRISPRi", 2),
    "Norman": ("norman", "Norman et al. 2019 Perturb-seq, K562 CRISPRa single and double perturbations", "91,205 single cells, single and dual CRISPRa", 3),
    "Replogle_K562": ("replogle_k562", "Replogle et al. 2022 genome-wide Perturb-seq subset, K562 CRISPRi", "162,751 single cells, single-gene CRISPRi", 4),
    "Replogle_RPE1": ("replogle_rpe1", "Replogle et al. 2022 genome-wide Perturb-seq subset, RPE1 CRISPRi", "162,733 single cells, single-gene CRISPRi", 5)}
PROT = {}
for ds, (s1key, dname, cells, s1row) in DS_INFO.items():
    slug = ds.lower().replace("_", "-")
    did = f"{P}-data-csendes2025-{slug}"
    tr, va, te = (t1[f"{c}{s1row}"][0] for c in "BCD")
    rec(did, "dataset", f"{dname} (GEARS processing, Csendes et al. 2025)", "Perturb-seq dataset processed with cell-gears v0.0.1 and split by perturbation as in the GEARS publication.",
        [S_ART, S_SUPP], [],
        {"version": "cell-gears v0.0.1 processing; GEARS perturbation-exclusive split", "population": f"{cells}; {tr} train, {va} validation and {te} test perturbations (Supplementary Table 1)",
         "split": "Perturbation exclusive: unseen perturbations (or, for Norman, unseen combinations) in the test set", "denominator": int(te),
         "source_locator": f"Results 'Benchmarking of post-perturbation RNA-seq prediction methods' paragraph 2; Methods 'Benchmark datasets'; Supplementary Table 1 row '{s1key}'"})
    claims_rows.append([did, S_SUPP, f"Supplementary Table 1 row '{s1key}', columns B-D", f"{tr}; {va}; {te}", "dataset_attribute"])
    pid = f"{P}-protocol-csendes2025-{slug}-pex"
    PROT[ds] = (pid, did)
    rec(pid, "protocol", f"{dname}: unseen-perturbation expression prediction (Csendes et al. 2025 Supplementary Table 2)",
        "Pseudo-bulk Pearson correlations between predicted and observed post-perturbation expression for unseen perturbations, in raw and control-subtracted space.",
        [S_ART, S_SUPP], [{"relation": "uses_data", "target_id": did}],
        {"protocol": ("Single-cell predictions are averaged per perturbation and compared with the observed pseudo-bulk profile. Pearson: raw expression. "
                      "Pearson Delta: perturbed minus control expression. DE variants use the top 20 differentially expressed genes from the GEARS publication (t-test), "
                      "the top 20 by Wilcoxon test, or the top 20 with the CRISPR target gene(s) removed."),
         "version": f"Supplementary Table 2 rows for '{ds}'", "denominator": int(te),
         "source_locator": "Results 'Benchmarking of post-perturbation RNA-seq prediction methods' paragraph 3; Methods 'Model evaluation'",
         "limitations": ["One split per dataset; no seeds or spread printed.",
                         "Raw-expression Pearson is near 1 for every model and the authors do not consider it meaningful (Results paragraph 5).",
                         "Low perturbation-specific variance in these datasets limits how well they separate models (Results 'Limited perturbation diversity biases benchmarking outcomes')."],
         "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Single values per model and dataset"}}})
n = t1
claim(f"{P}-claim-csendes2025-norman-subgroups", PROT["Norman"][0], "norman_test_subgroups",
      f"Norman validation perturbations: combo_seen0 {n['B8'][0]}, combo_seen1 {n['C8'][0]}, combo_seen2 {n['D8'][0]}, unseen_single {n['E8'][0]}; test perturbations: combo_seen0 {n['B9'][0]}, combo_seen1 {n['C9'][0]}, combo_seen2 {n['D9'][0]}, unseen_single {n['E9'][0]}.",
      S_SUPP, "Supplementary Table 1 rows 7-9", method=("deterministic-table-parse",), note=NOTE)
claim(f"{P}-claim-csendes2025-target-gene-in-de", PROT["Norman"][0], "pearson_delta_de_target_gene",
      "The CRISPR target gene of a perturbation was frequently among the top 20 DE genes; since scGPT's perturbation token is tied to the gene token, predicting the target gene's change is close to trivial, and removing target genes from the top 20 lowered scGPT's Pearson Delta DE.",
      S_ART, "Results 'Benchmarking of post-perturbation RNA-seq prediction methods' paragraph 8")

# ================================================================= evaluations and results
COLS = [("C", "Pearson", "pearson-correlation", "raw expression, pseudo-bulk, all genes", "pearson"),
        ("D", "Pearson DE", "pearson-correlation", "raw expression, top 20 DE genes (t-test, GEARS list)", "pearson-de"),
        ("E", "Pearson Delta ", "pearson-delta", None, "pearson-delta"),
        ("F", "Pearson Delta DE", "pearson-delta", "top 20 DE genes (t-test, GEARS list)", "pearson-delta-de"),
        ("G", "Pearson Delta DE (based on Wilcoxon)", "pearson-delta", "top 20 DE genes (Wilcoxon test)", "pearson-delta-de-wilcoxon"),
        ("H", "Pearson Delta DE without KOd gene", "pearson-delta", "top 20 DE genes (t-test) excluding the CRISPR target gene(s)", "pearson-delta-de-no-target")]
for di, ds in enumerate(DATASETS):
    pid, did = PROT[ds]
    for mi, m in enumerate(MODELS):
        r = 2 + di * 15 + mi
        ev = f"{P}-eval-csendes2025-{ds.lower().replace('_', '-')}-{m.lower().replace('_', '-')}"
        own = m not in ("scGPT", "scFoundation")
        lim = (["Baseline constructed by the authors, who conclude that baselines beat the foundation models."] if own else
               ["Third-party foundation model fine-tuned and run by the authors, not by its developers."])
        rec(ev, "evaluation", f"{m} on {ds} (Csendes et al. 2025)", "Published perturbation-response benchmark; transcribed, not reproduced.",
            [S_ART, S_SUPP], [{"relation": "system", "target_id": CFG[m]}, {"relation": "assessment", "target_id": pid}, {"relation": "data", "target_id": did}],
            {"origin": "author_reported" if own else "independent_paper", "protocol": pid, "version": f"Primary source as retrieved {DATE}",
             "comparison": {"protocol_id": pid, "dataset_version": "cell-gears v0.0.1", "split": "GEARS perturbation-exclusive split",
                            "population": "test perturbations (Supplementary Table 1)", "inputs": "Control cells plus perturbation identity (foundation models); perturbed-gene features (baselines)",
                            "adaptation": "Fine-tuned or trained per dataset with validation-set selection", "metric_implementation": "Pseudo-bulk Pearson correlations as in the scGPT publication",
                            "aggregation": "Mean over test perturbations", "budget": None},
             "source_locator": f"Supplementary Table 2 row {r}", "limitations": lim})
        for col, label, metric, qual, slug in COLS:
            ref = f"{col}{r}"
            if ref not in t2:
                continue
            pv, nv = printed_numeric(t2[ref])
            attrs = {"metric": metric, "metric_direction": "higher", "unit": "unitless", "printed_value": pv, "numeric_value": nv,
                     "source_locator": f"Supplementary Table 2, cell {ref}, row '{ds} / {m}', column '{label.strip()}'",
                     "missing_metadata": {"uncertainty": {"reason": "unreported"}}, "review": review()}
            if qual:
                attrs["metric_qualifier"] = qual
            rid = f"{ev}-{slug}".replace("-eval-", "-result-")
            rec(rid, "result", f"{m} on {ds} {metric}" + (f" ({qual})" if qual else ""),
                "Reported measurement transcribed from the pinned source. Not independently reproduced.", [S_SUPP],
                [{"relation": "evaluation", "target_id": ev}], attrs, facets={})
            claims_rows.append([rid, S_SUPP, attrs["source_locator"], pv, "result"])

# ================================================================= judgements
JUDGEMENTS = []
for order, ds in enumerate(DATASETS, start=1):
    pid, _ = PROT[ds]
    label = {"Adamson": "Adamson (K562 CRISPRi)", "Norman": "Norman (K562 CRISPRa, singles and pairs)",
             "Replogle_K562": "Replogle K562 (CRISPRi)", "Replogle_RPE1": "Replogle RPE1 (CRISPRi)"}[ds]
    jid = f"use-case-mapping-perturbation-response-20261009-csendes2025-{ds.lower().replace('_', '-')}"
    rationale = ("Two foundation models and thirteen simple controls (a Train Mean predictor and random forest, elastic net and kNN regressors on four perturbed-gene feature sets) are scored on the same unseen perturbations, "
                 "which is the methods-and-controls comparison the use case asks for. It is proxy evidence: expression-prediction scores do not establish mechanism or experimental prioritisation (use-case exclusion), and the comparison is the authors' own baselines against reproduced foundation models.")
    attrs = {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": "proxy",
             "endpoint": f"Pearson correlation of predicted versus observed expression change (Pearson Delta), plus raw-expression and top-20-DE variants, for scGPT, scFoundation, Train Mean and 12 feature-based regressors on unseen perturbations, {label}",
             "rationale": rationale,
             "constraints": ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                             "Do not combine these results with another protocol's results; splits, gene subsets and metric implementations differ between sources.",
                             "Use Pearson Delta rather than raw Pearson to compare models; raw Pearson is near 1 for all of them."],
             "limitations": ["One split per dataset; no seeds or spread printed.",
                             "Baselines built by the authors; scGPT and scFoundation reproduced by the authors rather than their developers.",
                             "Datasets have low perturbation-specific variance (Results, second section), so differences between models are small.",
                             "Top-20 DE metrics include the CRISPR target gene unless stated, which favours scGPT (claim)."],
             "citation_locators": [{"source_id": S_SUPP, "locator": f"Supplementary Table 2 rows for '{ds}'"},
                                   {"source_id": S_ART, "locator": "Results 'Benchmarking of post-perturbation RNA-seq prediction methods'; Methods"}],
             "source_locator": f"{S_SUPP}: Supplementary Table 2 rows for '{ds}'; {S_ART}: Results and Methods", "revision": 1,
             "reason": "Recorded from the genetic perturbation response use-case pass 2026-10-09 (data/omics/use-case-coverage-perturbation-response-20261009). Draft until an independent review.",
             "comparison_group": "csendes2025-perturbseq", "comparison_title": "Foundation models against simple controls on unseen perturbations (Csendes et al. 2025)",
             "headline_metric": "pearson-delta", "stratum_label": label, "stratum_order": order}
    rec(jid, "claim", f"Relevance of unseen-perturbation expression prediction on {label} (Csendes et al. 2025) to \"{UC_NAME}\"", rationale,
        [S_ART, S_SUPP], [{"relation": "subject", "target_id": UC}], attrs, facets={})
    JUDGEMENTS.append({"judgement_id": jid, "protocol_id": pid, "relevance": "proxy", "comparison_group": "csendes2025-perturbseq",
                       "stratum_label": label, "stratum_order": order})

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
