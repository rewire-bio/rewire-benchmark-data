"""Extract the remaining decision-relevant Feng et al. 2025 tables (issue rewire-benchmark-data#19).

Usage:
  python3 -I extract/extract_feng.py <epmc.xml> <MOESM3_ESM.xlsm> <MOESM1_ESM.pdf> <gtex_hyena.py> <batch-folder>

Reads the pinned Europe PMC article XML (main Tables 1 and 4, Methods) and the pinned Supplementary
Data workbook (Supplementary Data 1, 2 and 6). Asserts every artifact hash, row label and column
header before writing. All records are written with status needs_review; the review-evidence pass
signs them off. Existing Feng records (prefix amp-feng-20261007-) are reused, never changed.
"""
import csv, hashlib, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET

TODAY = "2026-10-13"
RETRIEVED_AT = "2026-10-13T14:08:10Z"
P = "feng-dna-fm-20261013"
SRC = "evidence-expansion-dna-foundation-models-2025-5d8ca9bc"
SRC_SD = P + "-source-supplementary-data"
SRC_SI = P + "-source-supplementary-information"
SRC_SCRIPT = P + "-source-gtex-hyena-script"
SRC_README = "evidence-reported-dna-foundation-models-2025-readme-md"
UC_REG = "use-case-regulatory-variant-gene-follow-up"

XML_SHA = "5d8ca9bcf88cc1b38ad667906a2e4699b1aefa6d31c6f49259784930353f3202"
SD_SHA = "4804c801e0e054eca5f776617c18a6a0cb31d6ce3d2a7a52f70e4dda5b3abd7a"
SI_SHA = "373f59b825c9e2bc51a0f122a9e2653f427c492727fbf73768cc9af02d094a15"
SCRIPT_SHA = "a9ab37677da4340d3d5ea3b7516d71bf4e60d7cb2eab39eb954584d738ed2788"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12663285/fullTextXML"
SD_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-65823-8/MediaObjects/41467_2025_65823_MOESM3_ESM.xlsm"
SI_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-65823-8/MediaObjects/41467_2025_65823_MOESM1_ESM.pdf"
COMMIT = "3f4c81ce066f3c47422a83466b085aac1a6be902"
SCRIPT_URL = f"https://raw.githubusercontent.com/ChongWuLab/dna_foundation_benchmark/{COMMIT}/job_scripts/gtex_hyena.py"

EXTRACTOR_NOTE = ("Claude (Opus 5.5) extraction agent for rewire-benchmark-data#19; extraction only, not a review. "
                  "Pending an independent review-evidence pass.")
AREAS = ["dna-genomes"]
MODELS = ["DNABERT-2", "NT-v2", "HyenaDNA", "Caduceus-Ph", "GROVER"]

# Table 1 checkpoints named in Methods, "Model configuration selection".
T1_CHECKPOINT = {"NT-v2": "NT-v2-500M", "HyenaDNA": "Hyena-160K", "Caduceus-Ph": "Caduceus-Ph-131K",
                 "DNABERT-2": "DNABERT-2, its only published checkpoint", "GROVER": "GROVER, its only published checkpoint"}
CHECKPOINT_LOCATOR = "Methods, 'Model configuration selection' paragraph"

# Table 1 rows already in the store (amp-feng-20261007 batch); not re-extracted.
T1_EXISTING = {"Acceptor": "amp-feng-20261007-protocol-splice-acceptor", "Donor": "amp-feng-20261007-protocol-splice-donor"}
T2_EXISTING = {"Promoter Arabidopsis NonTATA": "amp-feng-20261007-protocol-promoter-nontata",
               "Promoter Arabidopsis TATA": "amp-feng-20261007-protocol-promoter-tata"}

# Table 1 label -> Supplementary Data 1/2/6 label (the workbook spells some names differently).
SD_LABEL = {
    "DNase I Hypersensitive": "DNase I Hypersensitive", "Human TFBS 1": "Human TFBS 1", "Human TFBS 2": "Human TFBS 2",
    "Human TFBS 3": "Human TFBS 3", "Human TFBS 4": "Human TFBS 4", "Human TFBS 5": "Human TFBS 5",
    "Promoter GM12878": "Promoter GM12878", "Promoter HUVEC": "Promoter HUVEC", "Promoter Hela-S3": "Promoter Hela-S3",
    "Promoter NHEK": "Promoter NHEK", "Acceptor": "Acceptors", "Coding": "Coding", "Donor": "Donors",
    "Enhancer": "Enhancer", "Enhancer Cohn": "Enhancer Cohn", "Enhancer Ensembl": "Enhancer Ensembl",
    "Open chromatin region": "Open Chromatin Region", "Promoter All 300 bps": "Promoter All 300bps",
    "Promoter All 70 bps": "Promoter All 70bps", "Promoter NonTATA 251 bps": "Promoter NonTATA 251bps",
    "Promoter NonTATA 300 bps": "Promoter NonTATA 300bps", "Promoter NonTATA 70 bps": "Promoter NonTATA 70bps",
    "Promoter TATA 300 bps": "Promoter TATA 300bps", "Promoter TATA 70 bps": "Promoter TATA 70bps",
    "Promoter Arabidopsis NonTATA": "Promoter Arabidopsis NonTATA", "Promoter Arabidopsis TATA": "Promoter Arabidopsis TATA",
}

# Dataset origin, from Supplementary Note 1 (Supplementary Information PDF, pages 1-2).
ORIGIN = {
    "DNase I Hypersensitive": "DNase I hypersensitive site detection set (Supplementary Note 1; original source cited in the main text)",
    "Promoter GM12878": "Promoter identification set for cell line GM12878 (Supplementary Note 1, promoter identification in multiple species)",
    "Promoter HUVEC": "Promoter identification set for HUVEC (Supplementary Note 1, promoter identification in multiple species)",
    "Promoter Hela-S3": "Promoter identification set for HeLa-S3 (Supplementary Note 1, promoter identification in multiple species)",
    "Promoter NHEK": "Promoter identification set for NHEK (Supplementary Note 1, promoter identification in multiple species)",
    "Coding": "Genomic Benchmarks demo_coding_vs_intergenomic_seqs (Supplementary Note 1)",
    "Enhancer": "NT-v2 benchmark enhancer sequence prediction set (Supplementary Note 1, NT-v2 Section A 4.3)",
    "Enhancer Cohn": "Genomic Benchmarks human_enhancers_cohn (Supplementary Note 1)",
    "Enhancer Ensembl": "Genomic Benchmarks human_enhancers_ensembl (Supplementary Note 1)",
    "Open chromatin region": "Genomic Benchmarks human_ocr_ensembl (Supplementary Note 1)",
    "Promoter NonTATA 251 bps": "Genomic Benchmarks human_nontata_promoters (Supplementary Note 1)",
}
for i in range(1, 6):
    ORIGIN[f"Human TFBS {i}"] = "DNABERT-2 (GUE) human transcription factor binding site prediction set (Supplementary Note 1)"
for lab in ["Promoter All 300 bps", "Promoter NonTATA 300 bps", "Promoter TATA 300 bps"]:
    ORIGIN[lab] = "DNABERT-2 (GUE) human promoter detection set, 300 bp (Supplementary Note 1)"
for lab in ["Promoter All 70 bps", "Promoter NonTATA 70 bps", "Promoter TATA 70 bps"]:
    ORIGIN[lab] = "DNABERT-2 (GUE) human core promoter detection set, 70 bp (Supplementary Note 1)"

# Supplementary Note 2: datasets not fully relying on experimental evidence or gold-standard sources.
NOT_EXPERIMENTAL = {"Enhancer"}

SPLIT_RULE = ("Original predefined split retained where clearly defined; otherwise a random 70:30 train/test split. "
              "DNABERT-2/NT-v2 benchmark datasets are re-split 70:30 keeping class proportions unless the source states an exception. "
              "Random forest hyperparameters tuned by fivefold cross-validation. No whole-chromosome holdout (Methods).")
T1_SCOPE = ("Frozen last-layer mean token embeddings from each pretrained model, scored by a supervised random forest classifier "
            "fitted for this exact task (not label-free prediction). " + SPLIT_RULE)


def slug(s):
    s = s.lower().replace("+", " plus ").replace("’", "").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def num(printed):
    t = printed.strip().replace("−", "-")
    return t if re.fullmatch(r"-?\d+(\.\d+)?", t) else None


# ---------------------------------------------------------------- source readers
def read_xml_tables(path):
    t = open(path, encoding="utf-8").read()
    t = re.sub(r'xmlns(:\w+)?="[^"]*"', "", t)
    t = re.sub(r"<(/?)\w+:", r"<\1", t)
    t = re.sub(r'\s\w+:\w+="[^"]*"', "", t)
    root = ET.fromstring(t)
    txt = lambda e: " ".join("".join(e.itertext()).split())
    tables = {}
    for tw in root.iter("table-wrap"):
        rows = []
        for tr in tw.iter("tr"):
            cells = []
            for c in tr:
                if c.tag in ("td", "th"):
                    cells.append({"text": txt(c), "bold": c.find("bold") is not None})
            rows.append(cells)
        tables[tw.get("id")] = {"caption": txt(tw.find("caption")), "rows": rows}
    return tables


def read_workbook(path):
    z = zipfile.ZipFile(path)
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    ss = ["".join(t.text or "" for t in si.iter("{%s}t" % ns["m"]))
          for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sheets = {}
    for s in wb.find("m:sheets", ns):
        rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        sh = ET.fromstring(z.read("xl/" + rels[rid].replace("/xl/", "")))
        rows = []
        for row in sh.iter("{%s}row" % ns["m"]):
            vals = {}
            for c in row.findall("m:c", ns):
                v = c.find("m:v", ns)
                if v is None:
                    continue
                col = re.match(r"[A-Z]+", c.get("r")).group(0)
                vals[col] = ss[int(v.text)] if c.get("t") == "s" else v.text
            rows.append(vals)
        sheets[s.get("name")] = rows
    return sheets


# ---------------------------------------------------------------- record builders
class Batch:
    def __init__(self):
        self.records, self.ids, self.rows = [], set(), []

    def add(self, rec):
        assert rec["id"] not in self.ids, rec["id"]
        self.ids.add(rec["id"])
        mm = rec["attributes"].get("missing_metadata")
        if mm:
            rec["attributes"]["missing_metadata"] = dict(sorted(mm.items()))
        self.records.append(rec)
        return rec["id"]

    def entity(self, kind, id, name, description, attrs, source_ids=(SRC,), method_types=None, links=()):
        facets = {"areas": AREAS, "contexts": ["research"]}
        if method_types:
            facets["method_types"] = method_types
        return self.add({"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
                         "facets": facets, "source_ids": list(source_ids), "links": list(links), "attributes": attrs})

    def claim(self, id, name, subject, attrs, source_ids):
        self.rows.append([id, source_ids[0], attrs.get("source_locator", ""), str(attrs.get("value", ""))[:200], "claim"])
        return self.add({"id": id, "kind": "claim", "name": name, "description": "Descriptive fact transcribed from the pinned source.",
                         "status": "needs_review", "facets": {}, "source_ids": list(source_ids),
                         "links": [{"relation": "subject", "target_id": subject}], "attributes": attrs})


def extraction_review(method_note, sha, url):
    return {"method": ["deterministic-table-parse"], "method_note": method_note, "reviewer": ["claude"],
            "reviewer_note": EXTRACTOR_NOTE, "date": TODAY, "artifact_sha256": sha, "retrieval_url": url,
            "note": "Extracted, not reviewed. The review-evidence pass must re-check this cell against the pinned artifact."}


def main(xml_path, sd_path, si_path, script_path, out):
    for path, want in ((xml_path, XML_SHA), (sd_path, SD_SHA), (si_path, SI_SHA), (script_path, SCRIPT_SHA)):
        got = sha256(path)
        assert got == want, f"{path}: {got} != {want}"
    tables = read_xml_tables(xml_path)
    wb = read_workbook(sd_path)
    b = Batch()

    # ------------------------------------------------------------ sources
    common = {"doi": "10.1038/s41467-025-65823-8", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
              "url": "https://doi.org/10.1038/s41467-025-65823-8", "retrieved_at": RETRIEVED_AT}
    b.entity("source", SRC_SD, "Benchmarking DNA foundation models for genomic and genetic tasks: Supplementary Data 1-6",
             "Supplementary Data workbook of Feng et al. 2025 (Nature Communications 16:10780), retrieved and hashed for rewire-benchmark-data#19.",
             dict(common, artifact_url=SD_URL, artifact_sha256=SD_SHA, media_type="application/vnd.ms-excel.sheet.macroEnabled.12",
                  version="Nature Communications 16, 10780 (2025); Supplementary Data 1-6 workbook (MOESM3, .xlsm)",
                  limitations=["Supplementary Data 1 and 2 list, per dataset, which models the baseline CNN significantly beat and which beat the CNN (one-sided DeLong p<0.01). The CNN's own AUC values are not printed anywhere in the article or supplement.",
                               "Supplementary Data 6 gives Enhancer Ensembl the same training and test sizes as Enhancer and a three-class label distribution, although Table 1 reports it as a binary AUC task."]),
             source_ids=())
    b.entity("source", SRC_SI, "Benchmarking DNA foundation models for genomic and genetic tasks: Supplementary Information",
             "Supplementary Information PDF of Feng et al. 2025 (Nature Communications 16:10780), retrieved and hashed for rewire-benchmark-data#19.",
             dict(common, artifact_url=SI_URL, artifact_sha256=SI_SHA, media_type="application/pdf",
                  version="Nature Communications 16, 10780 (2025); Supplementary Information PDF (MOESM1, 11 pages)",
                  limitations=["The main text places the TAD region at about token positions 300-700; the Supplementary Fig. 2 caption (page 11) says about 200-600.",
                               "The main text cites the gene-expression hyperparameter grid as Supplementary Table 6; the PDF prints it as Supplementary Table 5 (Supplementary Table 6 is the sequence-classification grid)."]),
             source_ids=())
    b.entity("source", SRC_SCRIPT, "ChongWuLab/dna_foundation_benchmark job_scripts/gtex_hyena.py",
             "Author job script for HyenaDNA gene-expression embeddings, pinned to a commit for rewire-benchmark-data#19.",
             {"url": f"https://github.com/ChongWuLab/dna_foundation_benchmark/blob/{COMMIT}/job_scripts/gtex_hyena.py",
              "artifact_url": SCRIPT_URL, "artifact_sha256": SCRIPT_SHA, "version": COMMIT, "retrieved_at": RETRIEVED_AT,
              "publication_status": "official_project_source", "licence": "MIT", "media_type": "text/x-python"},
             source_ids=())

    # ------------------------------------------------------------ supplementary data lookups
    def sheet_map(name, ncols):
        rows = wb[name]
        return {r["A"].strip(): r for r in rows[1:] if "A" in r}

    sd1, sd2, sd6 = sheet_map("Data 1", 2), sheet_map("Data 2", 2), sheet_map("Data 6", 8)
    assert wb["Data 1"][0] == {"A": "Dataset", "B": "Baseline CNN Performs Better Than"}
    assert wb["Data 2"][0] == {"A": "Dataset", "B": "Models that Outperform Baseline CNN"}
    assert wb["Data 6"][0]["E"] == "Training Size" and wb["Data 6"][0]["F"] == "Testing Size"
    assert wb["Data 6"][0]["G"] == "Label Distribution (Positive/Negative)"

    # ------------------------------------------------------------ Table 1
    t1 = tables["Tab1"]
    assert t1["caption"].startswith("The AUC results for binary sequence classification tasks on human genome")
    assert [c["text"] for c in t1["rows"][0]] == ["Data"] + MODELS
    body = t1["rows"][1:]
    assert len(body) == 24, len(body)
    t1_new = 0
    for row in body:
        label = row[0]["text"]
        assert label in SD_LABEL, label
        if label in T1_EXISTING:
            continue
        cells = row[1:]
        assert len(cells) == 5
        s = slug(label)
        sd = sd6[SD_LABEL[label]]
        train, test = int(sd["E"]), int(sd["F"])
        ds_attrs = {
            "population": ORIGIN[label] + f"; sequence length median {sd['B']} bp (range {sd['C']}-{sd['D']} bp) per Supplementary Data 6.",
            "split": SPLIT_RULE + f" Supplementary Data 6: {train} training and {test} test sequences.",
            "test_denominator": f"{test} test sequences (Supplementary Data 6, row '{SD_LABEL[label]}', column 'Testing Size')",
            "species": "Homo sapiens",
            "source_locator": f"Supplementary Data 6, row '{SD_LABEL[label]}'; Supplementary Note 1",
            "missing_metadata": {"version": {"reason": "unextracted", "note": "Upstream dataset release not stated in the article."}},
        }
        notes = []
        if "G" in sd:
            pos, neg = (int(x) for x in sd["G"].split("/"))
            ds_attrs["positives"], ds_attrs["negatives"] = pos, neg
            ds_attrs["total"] = pos + neg
            if pos + neg != train + test:
                notes.append(f"Supplementary Data 6 label counts ({pos}/{neg}) do not sum to training plus test size ({train + test}).")
        else:
            notes.append(f"Supplementary Data 6 prints a multi-class label distribution ({sd['H']}) and the same sizes as the Enhancer dataset, although Table 1 reports a binary AUC. The printed sizes are kept as printed.")
        if label in NOT_EXPERIMENTAL:
            notes.append("Supplementary Note 2 marks this dataset as not fully relying on experimental evidence or gold-standard sources.")
        if notes:
            ds_attrs["scope_note"] = " ".join(notes)
        ds = b.entity("dataset", f"{P}-dataset-t1-{s}", f"Feng {label} dataset",
                      f"{ORIGIN[label]}; as used in Feng et al. 2025 Table 1.", ds_attrs, source_ids=(SRC, SRC_SD, SRC_SI))
        proto = b.entity("protocol", f"{P}-protocol-t1-{s}", f"Feng {label} sequence classification",
                         "Table 1 human sequence classification; Feng et al. 2025 source-reported protocol.",
                         {"scope_note": T1_SCOPE, "task": f"{label} sequence classification (AUC)", "version": "Table 1",
                          "metric": "auroc", "metric_direction": "higher",
                          "comparison_limit": "Within-row comparison only: rows differ in source dataset, sequence length and split."},
                         source_ids=(SRC, SRC_SD))
        for model, cell in zip(MODELS, cells):
            ms = slug(model)
            cattrs = {"foundation_model_eligible": True, "head": "Supervised random forest fitted separately for this task",
                      "reported_name": model, "representation": "Frozen last-layer mean token embeddings", "task": f"{label} classification",
                      "missing_metadata": {"head_revision": {"reason": "unextracted"},
                                           "version": {"reason": "unreported", "note": "Immutable checkpoint revision is not stated in the article."}}}
            if model in T1_CHECKPOINT:
                cattrs["checkpoint"] = T1_CHECKPOINT[model] + " (" + CHECKPOINT_LOCATOR + ")"
            cfg = b.entity("configuration", f"{P}-config-t1-{s}-{ms}", f"{model} ({label} classification)",
                           f"{model} ({label} classification); Feng et al. 2025 source-reported, task-scoped configuration.",
                           cattrs, method_types=["foundation_model"])
            ev = b.entity("evaluation", f"{P}-eval-t1-{s}-{ms}", f"{model} {label} evaluation",
                          f"{model} {label} sequence-classification evaluation; Feng et al. 2025. Transcribed, not reproduced.",
                          {"origin": "independent_paper", "protocol": "Table 1, frozen embeddings + task-specific random forest classifier",
                           "comparison": {"adaptation": "Frozen pretrained representation plus a supervised random-forest classifier head fitted for this exact task",
                                          "aggregation": None, "budget": None, "dataset_version": None,
                                          "inputs": f"DNA sequence windows for {label} classification", "metric_implementation": None,
                                          "population": ds_attrs["population"], "protocol_id": proto, "split": ds_attrs["split"]},
                           "missing_metadata": {"budget": {"reason": "unextracted", "note": "Not extracted; no execution"},
                                                "metric_implementation": {"reason": "unreported", "note": "Exact scoring implementation beyond AUC is unreported."},
                                                "version": {"reason": "unextracted"}}},
                          links=[{"relation": "assessment", "target_id": proto}, {"relation": "system", "target_id": cfg},
                                 {"relation": "data", "target_id": ds}])
            printed = cell["text"]
            n = num(printed)
            assert n is not None, (label, model, printed)
            bold = " Printed in bold (caption: higher than at least two other AUCs, p < 0.01, one-sided DeLong)." if cell["bold"] else ""
            loc = f"Table 1, row '{label}', column '{model}'.{bold}"
            rid = f"{P}-result-t1-{s}-{ms}-auc"
            b.rows.append([rid, SRC, loc, printed, "result"])
            b.add({"id": rid, "kind": "result", "name": f"{model} {label} AUC",
                   "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                   "status": "needs_review", "facets": {}, "source_ids": [SRC], "links": [{"relation": "evaluation", "target_id": ev}],
                   "attributes": {"metric": "auroc", "metric_direction": "higher", "unit": "unitless", "printed_value": printed,
                                  "numeric_value": n, "metric_qualifier": f"task: {label.lower()}", "source_locator": loc,
                                  "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Table 1 prints point AUCs only."}},
                                  "review": extraction_review("Deterministic parse of the pinned Europe PMC XML table cells (table id Tab1), header and row labels asserted.", XML_SHA, XML_URL)}})
            t1_new += 1
    assert t1_new == 110, t1_new

    # ------------------------------------------------------------ CNN comparator claims (Supplementary Data 1 and 2)
    t1_protocols = {row[0]["text"]: (T1_EXISTING.get(row[0]["text"]) or f"{P}-protocol-t1-{slug(row[0]['text'])}") for row in body}
    t1_protocols.update(T2_EXISTING)
    for label, proto in sorted(t1_protocols.items()):
        key = SD_LABEL[label]
        beaten, better = sd1[key]["B"].strip(), sd2[key]["B"].strip()
        table = "Table 2" if label in T2_EXISTING else "Table 1"
        value = (f"Baseline CNN trained from scratch on {label}: Supplementary Data 1 lists the DNA foundation models the CNN significantly outperformed "
                 f"(one-sided DeLong p<0.01): {beaten}. Supplementary Data 2 lists the models that significantly outperformed the CNN: {better}. "
                 f"The CNN's AUC is not printed, so it has no result record; the foundation-model AUCs are in {table}.")
        b.claim(f"{P}-claim-cnn-{slug(label)}", f"reported_finding: {proto}", proto,
                {"field": "reported_finding", "value": value,
                 "source_locator": f"Supplementary Data 1 and Supplementary Data 2, row '{key}'",
                 "review": extraction_review("Deterministic parse of the pinned Supplementary Data workbook sheets 'Data 1' and 'Data 2'; row label asserted.", SD_SHA, SD_URL)},
                [SRC_SD, SRC])

    # ------------------------------------------------------------ Table 4 (gene expression)
    t4 = tables["Tab4"]
    assert t4["caption"].startswith("Overall performance of DNA foundation models in gene expression prediction using random forest regression")
    assert [c["text"] for c in t4["rows"][0]] == ["Model", "Input Sequence Length", "Average Prediction Correlation", "Average Prediction MSE"]
    t4_rows = [[c["text"] for c in r] for r in t4["rows"][1:]]
    expected = ["DNABERT-2", "NT-v2", "HyenaDNA", "Caduceus-Ph", "GROVER", "HyenaDNA-450K*", "Caduceus-Ph Long Sequence Input*", "Enformer*"]
    assert [r[0] for r in t4_rows] == expected, [r[0] for r in t4_rows]

    access = ("Individual-level GTEx v8 whole-genome sequences and expression are protected human-participant data: per the Data availability statement, raw "
              "individual WGS must be requested through the GTEx Protected Data Access portal, and the processed expression benchmark is not "
              "deposited with the other processed datasets on Hugging Face. Only aggregated GTEx releases are public.")
    repro = (f"Reproduction requires approved GTEx protected access, the per-model GPU environments described in the author README (pinned at {COMMIT}), "
             "and scheduler-style job scripts that take a job index and placeholder dataset and checkpoint paths. The pinned job_scripts/gtex_hyena.py "
             "reads 'long_seqs_by_gene', centre-crops to 6000 bp and writes to an output folder named 'cadph_long'; which script settings produced each "
             "Table 4 row cannot be confirmed from the repository. Not attempted by Rewire.")
    gtex_scope = ("Per-gene regression of covariate-corrected GTEx v8 whole-blood expression (residuals after regressing sex, PEER factors and genotype "
                  "principal components) on frozen zero-shot embeddings of each subject's phased sequence around the transcription start site. One "
                  "random forest regressor per gene; subjects split 75:25 into training and test; fivefold cross-validation on MSE for hyperparameter "
                  "tuning. Pearson correlation and MSE between predicted and observed expression are computed per gene and averaged across genes. "
                  "Random forest was chosen over XGBoost because it was better for every model (Supplementary Table 3). Supervised on expression labels; "
                  "not label-free prediction.")
    short_ds = b.entity("dataset", f"{P}-dataset-gtex-wb-expression-6kb", "Feng GTEx v8 whole-blood expression, TSS +/- 3 kb",
                        "Subject-specific phased sequences (TSS +/- 3,000 bp) and covariate-corrected whole-blood expression for GTEx v8; Feng et al. 2025.",
                        {"population": "GTEx v8 whole blood: 610 subjects, 21,004 genes. Each subject's phased SNVs and indels from WGS VCFs are inserted into GRCh38 to give both alleles of a ~6,000 bp window centred on the TSS.",
                         "split": "Per gene, subjects split 75:25 into training and test; fivefold cross-validation within training for tuning.",
                         "access": access, "private_data_not_included": True, "species": "Homo sapiens",
                         "source_locator": "Methods, 'Gene expression prediction datasets' (paragraphs 1 and 3) and 'Gene expression prediction benchmark'; Data availability",
                         "missing_metadata": {"version": {"reason": "unreported", "note": "GTEx v8; the exact GTEx file versions used are not stated."}}})
    long_ds = b.entity("dataset", f"{P}-dataset-gtex-wb-expression-long-768", "Feng GTEx v8 whole-blood expression, TSS +/- 98 kb, 768 genes",
                       "Subject-specific phased sequences (TSS +/- 98 kb) for a random 768-gene subset of GTEx v8 whole blood; Feng et al. 2025.",
                       {"population": "GTEx v8 whole blood, 610 subjects; 1,000 randomly selected genes reduced to 768 after excluding genes absent from the whole-blood data or whose TSS +/- 98 kb window exceeds the chromosome.",
                        "split": "Per gene, subjects split 75:25 into training and test; fivefold cross-validation within training for tuning.",
                        "access": access, "private_data_not_included": True, "species": "Homo sapiens",
                        "source_locator": "Methods, 'Gene expression prediction datasets' (paragraphs 2 and 3); Table 4 footnote",
                        "missing_metadata": {"version": {"reason": "unreported", "note": "GTEx v8; the exact GTEx file versions used are not stated."}}})
    short_p = b.entity("protocol", f"{P}-protocol-gtex-wb-expression-6kb", "Feng GTEx whole-blood expression prediction, all genes, 6 kb input",
                       "Table 4 gene-expression prediction on all 21,004 genes with ~6 kb input; Feng et al. 2025 source-reported protocol.",
                       {"scope_note": gtex_scope, "task": "Subject-level gene expression prediction from personal sequence (average per-gene Pearson correlation and MSE)",
                        "version": "Table 4, rows without asterisk", "access_note": access, "reproducibility_note": repro,
                        "comparison_limit": "Not comparable with the long-input rows: those cover a 768-gene subset (Table 4 footnote).",
                        "hyperparameters": "Random forest grid: n_estimators 100, 200, 500; max_depth None, 5, 10 (printed as Supplementary Table 5; the main text cites it as Supplementary Table 6)."},
                       source_ids=(SRC, SRC_SI, SRC_README, SRC_SCRIPT))
    long_p = b.entity("protocol", f"{P}-protocol-gtex-wb-expression-long-768", "Feng GTEx whole-blood expression prediction, 768 genes, long input",
                      "Table 4 gene-expression prediction on the 768-gene long-context subset; Feng et al. 2025 source-reported protocol.",
                      {"scope_note": gtex_scope, "task": "Subject-level gene expression prediction from personal sequence with long input (average per-gene Pearson correlation and MSE)",
                       "version": "Table 4, asterisked rows", "access_note": access, "reproducibility_note": repro,
                       "comparison_limit": "Only the three asterisked rows share this 768-gene population. Short-input models on the same genes appear only in Supplementary Table 4 (HyenaDNA and Caduceus-Ph).",
                       "hyperparameters": "Random forest grid: n_estimators 100, 200, 500; max_depth None, 5, 10 (printed as Supplementary Table 5; the main text cites it as Supplementary Table 6)."},
                      source_ids=(SRC, SRC_SI, SRC_README, SRC_SCRIPT))
    t4_meta = {
        "DNABERT-2": ("dnabert-2", 6000, "DNABERT-2, its only published checkpoint", True),
        "NT-v2": ("nt-v2", 6000, "NT-v2-500M", True),
        "HyenaDNA": ("hyenadna", 6000, None, True),
        "Caduceus-Ph": ("caduceus-ph", 6000, "Caduceus-Ph-131K", True),
        "GROVER": ("grover", 2048, "GROVER, its only published checkpoint", True),
        "HyenaDNA-450K*": ("hyenadna-450k", None, "Hyena-450K", True),
        "Caduceus-Ph Long Sequence Input*": ("caduceus-ph-long-sequence-input", None, "Caduceus-Ph-131K", True),
        "Enformer*": ("enformer", None, None, False),
    }
    for r in t4_rows:
        name, length, corr, mse = r
        ms, bp, ckpt, fm = t4_meta[name]
        is_long = name.endswith("*")
        proto, ds = (long_p, long_ds) if is_long else (short_p, short_ds)
        model = name.rstrip("*")
        miss = {"head_revision": {"reason": "unextracted"},
                "version": {"reason": "unreported", "note": "Immutable checkpoint revision is not stated in the article."}}
        cattrs = {"foundation_model_eligible": fm, "head": "Supervised random forest regressor fitted per gene",
                  "reported_name": name, "task": "GTEx whole-blood gene expression prediction",
                  "representation": ("Enformer final hidden state, mean-pooled over all regions, computed per phased allele and the two allele embeddings averaged (Methods, Gene expression prediction benchmark)." if name == "Enformer*" else "Frozen zero-shot embeddings computed per phased allele and the two averaged (Methods, Gene expression prediction benchmark). Token pooling for this task is not stated; the pinned HyenaDNA author script mean-pools tokens."),
                  "limitations": [f"Input length printed as '{length}'."]}
        if bp:
            cattrs["actual_input_bp"] = bp
        else:
            miss["actual_input_bp"] = {"reason": "unreported", "note": f"Printed as '{length}'; the exact base-pair count is not printed in Table 4."}
        if name == "GROVER":
            cattrs["limitations"].append("GROVER uses the centre-cropped 2,048 bp of the 6 kb window (Gene expression prediction section).")
        if ckpt:
            cattrs["checkpoint"] = ckpt + " (" + CHECKPOINT_LOCATOR + ")"
        elif name == "HyenaDNA":
            miss["checkpoint"] = {"reason": "unreported", "note": "Methods name Hyena-160K as the default and Hyena-450K for gene-expression prediction; the 6,000 bp HyenaDNA row is not tied to either."}
        if name == "Enformer*":
            cattrs["limitations"].append("Printed with an asterisk; Enformer is a supervised sequence-to-expression model used as a comparator, not one of the paper's DNA foundation models. Official PyTorch implementation (Methods).")
        cattrs["missing_metadata"] = miss
        cfg = b.entity("configuration", f"{P}-config-gtex-{ms}", f"{model} (GTEx whole-blood expression prediction)",
                       f"{name} (GTEx whole-blood expression prediction); Feng et al. 2025 source-reported, task-scoped configuration.",
                       cattrs, method_types=["foundation_model"] if fm else ["supervised_machine_learning"])
        ev = b.entity("evaluation", f"{P}-eval-gtex-{ms}", f"{model} GTEx whole-blood expression evaluation",
                      f"{name} gene-expression prediction evaluation; Feng et al. 2025. Transcribed, not reproduced.",
                      {"origin": "independent_paper", "protocol": "Table 4, frozen embeddings + per-gene random forest regression",
                       "comparison": {"adaptation": "Frozen pretrained representation plus a supervised random-forest regressor fitted per gene",
                                      "aggregation": "Mean across genes of the per-gene test-set metric", "budget": None, "dataset_version": None,
                                      "inputs": f"Subject-specific phased sequence centred on the TSS, {length} input",
                                      "metric_implementation": None,
                                      "population": "768-gene long-context subset, 610 subjects" if is_long else "All 21,004 genes, 610 subjects",
                                      "protocol_id": proto, "split": "Per gene, subjects split 75:25; fivefold cross-validation for tuning"},
                       "missing_metadata": {"budget": {"reason": "unextracted", "note": "Not extracted; no execution"},
                                            "metric_implementation": {"reason": "unreported"},
                                            "version": {"reason": "unextracted"}}},
                      links=[{"relation": "assessment", "target_id": proto}, {"relation": "system", "target_id": cfg},
                             {"relation": "data", "target_id": ds}])
        for metric, printed, direction, unit, qual, col in (
                ("pearson-correlation", corr, "higher", "unitless", "mean across genes of per-gene Pearson correlation between predicted and observed expression", "Average Prediction Correlation"),
                ("mean-squared-error", mse, "lower", "unit-unreported", "mean across genes of per-gene MSE of covariate-corrected expression", "Average Prediction MSE")):
            n = num(printed)
            assert n is not None
            loc = f"Table 4, row '{name}', column '{col}'"
            rid = f"{P}-result-gtex-{ms}-{'pearson' if metric.startswith('pearson') else 'mse'}"
            b.rows.append([rid, SRC, loc, printed, "result"])
            b.add({"id": rid, "kind": "result", "name": f"{model} GTEx whole-blood expression {'average correlation' if metric.startswith('pearson') else 'average MSE'}",
                   "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                   "status": "needs_review", "facets": {}, "source_ids": [SRC], "links": [{"relation": "evaluation", "target_id": ev}],
                   "attributes": {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed, "numeric_value": n,
                                  "metric_qualifier": qual, "source_locator": loc,
                                  "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Table 4 prints averages only; per-gene spread is shown only as a histogram (Fig. 3)."}},
                                  "review": extraction_review("Deterministic parse of the pinned Europe PMC XML table cells (table id Tab4), header and row labels asserted.", XML_SHA, XML_URL)}})

    b.claim(f"{P}-claim-gtex-short-finding", f"reported_finding: {short_p}", short_p,
            {"field": "reported_finding",
             "value": ("Average Pearson correlation between predicted and observed expression was 0.114 to 0.123 across the 6 kb models; the authors read this as "
                       "limited information for predicting subject-specific tissue-level expression. Caduceus-Ph and HyenaDNA had the highest average correlations "
                       "and significantly outperformed DNABERT-2 and GROVER (paired Wilcoxon signed-rank). A subset of genes reached correlations above 0.4 and up to 0.9."),
             "source_locator": "Results, 'Gene expression prediction', paragraphs 2 and 3; Methods, 'Gene expression prediction benchmark' (Wilcoxon test)",
             "review": extraction_review("Hand transcription of the cited paragraphs of the pinned Europe PMC XML.", XML_SHA, XML_URL)},
            [SRC])
    b.claim(f"{P}-claim-gtex-long-finding", f"reported_finding: {long_p}", long_p,
            {"field": "reported_finding",
             "value": ("Among long-input models, HyenaDNA-450K was significantly better than Enformer (p < 0.01) and Enformer was similar to Caduceus-Ph. On the same "
                       "768 genes, extending the input improved HyenaDNA (average correlation 0.122 short versus 0.137 long, two-sided Wilcoxon p = 0.0005) "
                       "but not Caduceus-Ph (0.124 versus 0.127, p = 0.975)."),
             "source_locator": "Results, 'Gene expression prediction', paragraph 2; Supplementary Table 4",
             "review": extraction_review("Hand transcription of the cited paragraph of the pinned Europe PMC XML and Supplementary Table 4 of the pinned Supplementary Information PDF (rendered page 7).", XML_SHA, XML_URL)},
            [SRC, SRC_SI])

    # ------------------------------------------------------------ TAD (no numeric result exists)
    tad_ds = b.entity("dataset", f"{P}-dataset-tad-imr90-6kb", "Feng IMR90 TAD-centred and background sequences",
                      "1,500 TAD-centred and 1,500 random background 6,000 bp human reference genome sequences; Feng et al. 2025.",
                      {"population": "IMR90 TAD boundary regions (2,400 bp, Basenji Hi-C insulation files following the Enformer workflow) filtered to the top 5% boundary strength; 1,500 strongest selected and centred in 6,000 bp windows, plus 1,500 random 6,000 bp background windows.",
                       "positives": 1500, "negatives": 1500, "species": "Homo sapiens",
                       "source_locator": "Methods, 'TAD region dataset'",
                       "missing_metadata": {"version": {"reason": "unreported"}}})
    tad_p = b.entity("protocol", f"{P}-protocol-tad-attention-nt-v2", "Feng TAD recognition from NT-v2 attention",
                     "TAD recognition analysis of NT-v2 self-attention; Feng et al. 2025. Qualitative; no score is printed.",
                     {"scope_note": ("Attention matrices from all NT-v2 layers and heads are averaged over the 1,500 TAD-centred and the 1,500 background sequences and the "
                                     "two averages are compared over the central 400 tokens. No classifier is trained and no metric is reported, so the protocol has no "
                                     "evaluations. Only NT-v2 was analysed: the other models lack accessible attention or support too short an input."),
                      "task": "Inspect whether frozen self-attention recognises TAD boundaries without fine-tuning",
                      "version": "Results 'TAD region recognition'; Methods 'TAD region recognition benchmark'",
                      "missing_metadata": {"metric": {"reason": "inapplicable", "note": "Qualitative heatmap comparison; no metric is defined."}}},
                     links=[{"relation": "uses_data", "target_id": tad_ds}])
    b.claim(f"{P}-claim-tad-finding", f"reported_finding: {tad_p}", tad_p,
            {"field": "reported_finding",
             "value": ("The difference between average NT-v2 attention for TAD-centred and background sequences showed no distinct pattern: values were near zero "
                       "apart from the diagonal. The authors conclude that NT-v2 self-attention does not recognise TAD boundaries without fine-tuning. The heatmap "
                       "is Supplementary Fig. 2 (Supplementary Information page 11)."),
             "source_locator": "Results, 'TAD region recognition', paragraph 2; Supplementary Fig. 2 (Supplementary Information page 11)",
             "review": extraction_review("Hand transcription of the cited paragraph of the pinned Europe PMC XML.", XML_SHA, XML_URL)},
            [SRC, SRC_SI])

    # ------------------------------------------------------------ coverage claim on the article source
    b.claim(f"{P}-claim-not-extracted", f"tables_not_extracted: {SRC}", SRC,
            {"field": "tables_not_extracted",
             "value": ("Not extracted as results: Table 2 rows other than the two Arabidopsis promoter rows (bacterial promoters, human vs worm, mouse TFBS); "
                       "Table 3 except the Human 5mC Caduceus-Ph and NT-v2 cells (human 6mA, yeast histone marks, 4mC in six species); Supplementary Tables 1-4 "
                       "(pooling counts, multi-class accuracy, random forest vs XGBoost, short vs long input); Supplementary Data 3 (top genes), 4 (per-chromosome-group "
                       "AUCs behind Tables 5 and 6) and 5 (HyenaDNA re-pretraining); Supplementary Tables 5-8 (hyperparameter grids, embedding dimensions) and Supplementary Fig. 1 (classifier comparison); Figures 2-4 including runtime. These are outside the human diagnostic and "
                       "regulatory use cases or repeat main-table values at another aggregation."),
             "source_locator": "Tables 2-3; Supplementary Tables 1-8 and Supplementary Fig. 1; Supplementary Data 3-5; Figures 2-4",
             "review": extraction_review("Inventory of the pinned article XML, Supplementary Information PDF and Supplementary Data workbook.", XML_SHA, XML_URL)},
            [SRC, SRC_SI, SRC_SD])

    # ------------------------------------------------------------ use-case relevance judgements (needs_review)
    common_lims = [
        "Labels are covariate-corrected whole-blood expression of GTEx subjects, not allele-specific or endogenous perturbation effects, and not in the user's cell type.",
        "Each model's representation is frozen; a random forest is fitted per gene on expression labels, so this measures how much expression variation the embedding plus a supervised head explains, not a label-free variant-effect score.",
        "Individual-level GTEx data are protected (GTEx Protected Data Access application); the benchmark cannot be rerun from public data.",
        "Transcribed from the paper; Feng et al. did not develop the models (independent_paper). No reproduction by Rewire and no human scientific review.",
        "The authors call overall performance modest and say the findings should be considered preliminary indicators (Results, Gene expression prediction, last paragraph).",
        "Subjects are split 75:25 within each gene; no loci, genes or studies are held out, which the use case's validation requirements ask for.",
    ]
    for proto, stratum, order, extra, evs in (
            (short_p, "All 21,004 genes, ~6 kb input", 1, ["GROVER uses a 2,048 bp centre crop, so its input differs from the other four rows.", "The ~6 kb TSS-centred window leaves out distal regulatory elements."],
             [f"{P}-eval-gtex-{m}" for m in ("dnabert-2", "nt-v2", "hyenadna", "caduceus-ph", "grover")]),
            (long_p, "768-gene subset, long input", 2, ["768 randomly selected genes only; not comparable with the all-gene rows.", "Enformer is a supervised expression model used as a comparator.", "Caduceus-Ph used the central 131 kb; HyenaDNA-450K and Enformer used the 196 kb window (Methods)."],
             [f"{P}-eval-gtex-{m}" for m in ("hyenadna-450k", "caduceus-ph-long-sequence-input", "enformer")])):
        b.claim(f"use-case-mapping-{P}-{proto.split(P + '-protocol-')[1]}", f"Relevance of {proto} to \"Select regulatory variants and genes for functional follow-up\"",
                UC_REG,
                {"field": f"links:assessed_by:{proto}", "value": proto, "relevance": "proxy",
                 "endpoint": "Average per-gene Pearson correlation and MSE between predicted and observed whole-blood expression across GTEx subjects, from frozen embeddings of each subject's phased TSS-centred sequence plus a per-gene random forest",
                 "rationale": ("Proxy: tests whether a model's sequence representation captures inter-individual cis-sequence effects on expression, which bears on "
                               "allele-effect prediction for a locus. It does not score individual variants, link elements to genes or measure perturbation outcomes, "
                               "which the use case needs."),
                 "constraints": ["Inspect every linked evaluation's source locator before citing a result.",
                                 "Do not combine this mapping's evaluations with any other protocol's results.",
                                 "Compare rows only within this protocol."],
                 "limitations": common_lims + extra,
                 "citation_locators": [{"source_id": SRC, "locator": "Table 4; Methods, 'Gene expression prediction datasets' and 'Gene expression prediction benchmark'; Data availability"}],
                 "source_locator": f"{SRC}: Table 4",
                 "headline_metric": "pearson-correlation",
                 "comparison_group": "feng-gtex-expression", "comparison_title": "Feng et al. GTEx whole-blood expression prediction",
                 "stratum_label": stratum, "stratum_order": order,
                 "reason": "Add a relevance judgement for the Feng et al. gene-expression protocol (rewire-benchmark-data#19).",
                 "reviewed_evaluations": evs},
                [SRC])

    # ------------------------------------------------------------ write
    os.makedirs(out, exist_ok=True)
    recs = sorted(b.records, key=lambda r: r["id"])
    for r in recs:
        if r["kind"] == "claim" and r["attributes"]["field"].startswith("links:assessed_by:"):
            r["attributes"].pop("reviewed_evaluations")  # the reviewer fills this
    with open(os.path.join(out, "batch.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    with open(os.path.join(out, "claims.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        for row in sorted(b.rows):
            w.writerow(row)
    counts = {}
    for r in recs:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main(*sys.argv[1:6])
