"""Build the gfm-guides-20261014-esm1b batch from the pinned Brandes et al. 2023 artifacts.

Usage (python3 -I):
  build_esm1b.py <brandes.xml> <st2.xlsx> <si.pdf> <batch-dir>

Asserts every input hash, reads sheets 'Table_of_results_ClinVar' and 'Table_of_results_HGMD' of
Supplementary Table 2 with a stdlib OOXML reader (header row and the 19 included method labels
asserted), checks the four ROC-AUC values quoted in the Results text verbatim, and writes
batch.jsonl, claims.csv and gzip archives (mtime 0) of the three artifacts under artifacts/.
"""
import csv, gzip, hashlib, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter

XML, XLSX, SIPDF, OUT = sys.argv[1:5]
XML_SHA = "919ca366369efbe7e0880565192de127375edddedb1aa43ad023dec612bb4a04"
XLSX_SHA = "093c32e4156a801c0dd809a437c87818a4f1d04df92e037cf40222471a3e72e2"
SI_SHA = "30f1c2713875c7cec40f0beee19864840bc55326ddf68918841f93f8bb897c2a"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10484790/fullTextXML"
XLSX_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-023-01465-0/MediaObjects/41588_2023_1465_MOESM3_ESM.xlsx"
SI_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-023-01465-0/MediaObjects/41588_2023_1465_MOESM1_ESM.pdf"
DATE = "2026-10-14"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


assert sha(XML) == XML_SHA and sha(XLSX) == XLSX_SHA and sha(SIPDF) == SI_SHA, "input hash mismatch"

# ------------------------------------------------------------------ archives
os.makedirs(f"{OUT}/artifacts", exist_ok=True)
ARCH = {}
for src, name in [(XML, "brandes2023-pmc10484790.xml.gz"), (XLSX, "brandes2023-supplementary-table-2.xlsx.gz"),
                  (SIPDF, "brandes2023-supplementary-information.pdf.gz")]:
    raw = open(src, "rb").read()
    with open(f"{OUT}/artifacts/{name}", "wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw)
    ARCH[name] = sha(f"{OUT}/artifacts/{name}")

# ------------------------------------------------------------------ workbook
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def read_sheets(path):
    z = zipfile.ZipFile(path)
    shared = [("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
              for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for s in wb.find("m:sheets", NS):
        target = rels[s.get("{%s}id" % NS["r"])]
        root = ET.fromstring(z.read("xl/" + target.lstrip("/").replace("xl/", "")))
        cells = {}
        for c in root.iter("{%s}c" % NS["m"]):
            v = c.find("m:v", NS)
            if v is not None:
                cells[c.get("r")] = shared[int(v.text)] if c.get("t") == "s" else v.text
        out[s.get("name")] = cells
    return out


sheets = read_sheets(XLSX)
HEADER = ["vep_name", "AUC_AUROC", "AUC_Balanced_AUPRC", "n_var"]
INCLUDED = ["ESM1b", "EVE", "SIFT", "PROVEAN", "SIFT4G", "MutationAssessor", "MTBAN", "phyloP (vertebrate)", "LRT",
            "SiPhy", "GERP++", "phastCons (vertebrate)", "GenoCanyon", "phyloP (mammalian)", "phastCons (mammalian)",
            "phastCons (primate)", "phyloP (primate)", "bStatistic", "fitCons"]
TABLE = {}
for key, sheet, nvar in [("clinvar", "Table_of_results_ClinVar", "12095.0"), ("hgmd", "Table_of_results_HGMD", "12357.0")]:
    cells = sheets[sheet]
    assert [cells[f"{c}1"] for c in "ABCD"] == HEADER, sheet
    rows = {}
    for r in range(2, 48):
        label = cells[f"A{r}"]
        if f"B{r}" in cells:
            assert cells[f"D{r}"] == nvar, (sheet, r)
            assert r == 2 or cells[f"J{r}"] == "1", (sheet, r)
            rows[label] = (r, cells[f"B{r}"], cells[f"C{r}"])
        else:
            assert cells[f"J{r}"] == "0", (sheet, r)
    assert sorted(rows) == sorted(INCLUDED), (sheet, sorted(rows))
    TABLE[key] = rows


def shortest(v):
    # shortest round-trip decimal of the stored IEEE double
    return repr(float(v))


# ------------------------------------------------------------------ article text
xml = open(XML, encoding="utf-8").read()
flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml))
S1 = "ESM1b obtains a receiver operating characteristics\u2013area under the curve (ROC-AUC) score of 0.905 for distinguishing between the 19,925 pathogenic and 16,612 benign variants in ClinVar (across 2,765 genes), compared to 0.885 for EVE"
S2 = "On HGMD/gnomAD (with 27,754 disease-causing and 2,743 common variants across 1,991 genes), ESM1b obtains a ROC-AUC score of 0.897 compared to 0.882 for EVE"
assert S1 in flat and S2 in flat, "Results sentences"
assert "Over the set of variants reported by all 19 methods, ESM1b outperforms all other methods on both ClinVar and HGMD/gnomAD" in flat

# ------------------------------------------------------------------ records
P = "gfm-guides-20261014-esm1b"
S_ART, S_ST2, S_SI = f"{P}-source-brandes2023-article", f"{P}-source-brandes2023-supplementary-table-2", f"{P}-source-brandes2023-supplementary-information"
ESM1B_MODEL = "uc20260930-model-esm-1b"
EXTRACTOR_NOTE = ("Extraction agent for rewire-benchmark-data issue #129 (GPN-MSA and ESM-1b guide evidence); "
                  "extraction only, not a review. Pending an independent review-evidence pass.")
FAC = {"areas": ["dna-genomes", "protein-function"], "contexts": ["clinical_research"]}
records, claims_rows = [], []


def review(method, note, artifact, url, method_note=None):
    r = {"method": method, "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE, "date": DATE,
         "artifact_sha256": artifact, "retrieval_url": url, "note": note}
    if method_note:
        r["method_note"] = method_note
    return r


def add(rec):
    records.append(rec)
    return rec["id"]


COMMON_LIMITS = [
    "Benchmark built by the ESM1b workflow's authors (author-reported for ESM1b).",
    "Most other scores come from dbNSFP 4.3a; methods trained on clinical databases or using allele frequency are excluded from this comparison but reported head to head in Supplementary Table 2 (not extracted).",
]
for sid, name, url, sh, art, media, desc, loc, ret, extra in [
    (S_ART, "Genome-wide prediction of disease variant effects with a deep protein language model (Brandes et al., Nature Genetics 2023)",
     "https://doi.org/10.1038/s41588-023-01465-0", XML_SHA, XML_URL, "application/xml",
     "Peer-reviewed article, Europe PMC JATS full text (PMC10484790).",
     "Results 'ESM1b outperforms other VEP methods over clinical and experimental benchmarks' paragraphs 2 and 5; Methods 'ESM1b', 'AUC metrics for pathogenicity classification', 'Other VEP methods'",
     "2026-10-14T12:03:14Z", "brandes2023-pmc10484790.xml.gz"),
    (S_ST2, "Brandes et al. 2023 Supplementary Table 2: full benchmark evaluations of ESM1b and all other methods",
     XLSX_URL, XLSX_SHA, XLSX_URL, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
     "Publisher supplementary workbook (41588_2023_1465_MOESM3_ESM.xlsx).",
     "Sheets 'Contents', 'Table_of_results_ClinVar', 'Table_of_results_HGMD'",
     "2026-10-14T12:03:21Z", "brandes2023-supplementary-table-2.xlsx.gz"),
    (S_SI, "Brandes et al. 2023 Supplementary Information (Supplementary Table 1 and Methods)",
     SI_URL, SI_SHA, SI_URL, "application/pdf",
     "Publisher supplementary PDF (41588_2023_1465_MOESM1_ESM.pdf), used for dataset construction details.",
     "Supplementary Methods 'Clinical benchmarks of missense variants (ClinVar and HGMD/gnomAD)'",
     "2026-10-14T12:03:21Z", "brandes2023-supplementary-information.pdf.gz"),
]:
    attrs = {"url": url, "artifact_url": art, "doi": "10.1038/s41588-023-01465-0",
             "version": "Version of record, Nature Genetics 55, 1512-1522 (published 2023-08-10)",
             "retrieved_at": ret, "artifact_sha256": sh, "publication_status": "peer_reviewed",
             "licence": "CC BY 4.0", "media_type": media, "venue": "Nature Genetics", "year": 2023,
             "source_locator": loc,
             "archive_member": f"artifacts/{extra}",
             "archive_sha256": ARCH[extra],
             "review": review(["source-hash-verification"], "Retrieved once and hashed; not yet re-retrieved by a reviewer.", sh, art)}
    if sid == S_ART:
        attrs["limitations"] = [
            "The ROC-AUCs quoted in the Results for ESM1b versus EVE (0.905 and 0.885 on 36,537 ClinVar variants; 0.897 and 0.882 on 30,497 HGMD/gnomAD variants) do not match Supplementary Table 2's EVE head-to-head row (ESM1b 0.906018, EVE 0.885312 on 36,522 ClinVar variants; ESM1b 0.897926, EVE 0.883988 on 30,483 HGMD/gnomAD variants). The text values are extracted as printed; the head-to-head columns are not extracted.",
            "Figures 2e-h, 3 and Extended Data figures are not read; the values behind Figure 2e,f are in Supplementary Table 2.",
            "HGMD is a licensed resource; the HGMD/gnomAD benchmark cannot be rebuilt from public data.",
        ]
    records.append({"id": sid, "kind": "source", "name": name, "description": desc, "status": "needs_review",
                    "facets": dict(FAC), "source_ids": [], "links": [], "attributes": attrs})

BENCH = add({"id": f"{P}-benchmark-brandes2023-clinical-missense", "kind": "benchmark",
             "name": "Brandes et al. 2023 clinical missense pathogenicity benchmarks (ClinVar and HGMD/gnomAD)",
             "description": "Global ROC-AUC and balanced PRC-AUC of variant effect predictors for pathogenic versus benign missense variants on primary UniProt isoforms.",
             "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ART, S_ST2, S_SI], "links": [],
             "attributes": {
                 "entity_level": "suite", "version": "Nature Genetics 2023 version of record",
                 "task": "Missense variant pathogenicity classification",
                 "scope_note": "Two labelled sets (ClinVar; HGMD disease-causing versus gnomAD common). Extracted: the common-variant comparison of the 19 methods eligible for clinical benchmarking (Supplementary Table 2 columns AUC_AUROC and AUC_Balanced_AUPRC) and the ESM1b versus EVE ROC-AUCs quoted in the Results.",
                 "source_locator": "Results paragraphs 1, 2 and 5 of 'ESM1b outperforms other VEP methods...'; Supplementary Table 2 'Contents'",
             }})
D_CLINVAR = add({"id": f"{P}-data-clinvar-missense-eve-portal", "kind": "dataset",
                 "name": "ClinVar missense pathogenic vs benign, primary isoforms (Brandes et al. 2023, from the EVE portal)",
                 "description": "46,726 missense variants with ClinVar labels of at least one gold star across about 3,000 disease genes, downloaded from the EVE portal (includes variants not covered by EVE).",
                 "status": "needs_review", "facets": dict(FAC), "source_ids": [S_SI, S_ART], "links": [],
                 "attributes": {
                     "version": "ClinVar benchmark file from the EVE portal (evemodel.org); download date not printed",
                     "split": "Whole labelled set; ESM1b is unsupervised and comparator methods trained on clinical data are excluded",
                     "population": "Pathogenic versus benign ClinVar missense variants (at least one gold star) on primary UniProt isoforms",
                     "source_locator": "Supplementary Methods 'Clinical benchmarks of missense variants (ClinVar and HGMD/gnomAD)' paragraph 1; Data availability",
                 }})
D_HGMD = add({"id": f"{P}-data-hgmd-dm-vs-gnomad-common-missense", "kind": "dataset",
              "name": "HGMD disease-causing vs gnomAD common missense variants, primary isoforms (Brandes et al. 2023)",
              "description": "HGMD high-confidence disease-causing (DM) missense variants versus gnomAD v2.1.1 exome missense variants with MAF > 0.01; 92,942 variants (70,714 pathogenic, 22,228 benign) on primary UniProt isoforms.",
              "status": "needs_review", "facets": dict(FAC), "source_ids": [S_SI, S_ART], "links": [],
              "attributes": {
                  "version": "HGMD full dataset (access on request; release not printed); gnomAD v2.1.1 exomes (PASS, AN > 200,000)",
                  "split": "Whole labelled set",
                  "population": "HGMD DM missense variants versus gnomAD missense variants with MAF > 0.01, primary UniProt isoforms",
                  "denominator": 92942,
                  "access": "HGMD requires an access request; not public",
                  "source_locator": "Supplementary Methods 'Clinical benchmarks of missense variants (ClinVar and HGMD/gnomAD)' paragraphs 2-4",
              }})

PROTOS = {}
for key, data, label, nvar in [("clinvar", D_CLINVAR, "ClinVar", 12095), ("hgmd", D_HGMD, "HGMD/gnomAD", 12357)]:
    PROTOS[key] = add({"id": f"{P}-protocol-{key}-all-19-methods", "kind": "protocol",
                       "name": f"{label} missense pathogenicity, variants scored by all 19 eligible methods (Brandes et al. 2023 Fig. 2e-f, Supplementary Table 2)",
                       "description": f"Global ROC-AUC and balanced PRC-AUC on the {nvar:,} {label} variants with predictions from all 19 methods eligible for clinical benchmarking.",
                       "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ART, S_ST2],
                       "links": [{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data}],
                       "attributes": {
                           "protocol": "Scores used directly (no training on these labels). Global ROC-AUC treats all variants as one genome-wide task. Balanced PRC-AUC: downsample to equal pathogenic and benign counts (80% of the minority class), compute PRC-AUC, average over 100 repeats. Variant set restricted to variants scored by all 19 eligible methods.",
                           "version": f"Supplementary Table 2 sheet 'Table_of_results_{'ClinVar' if key == 'clinvar' else 'HGMD'}', n_var {nvar}",
                           "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
                           "denominator": nvar,
                           "limitations": COMMON_LIMITS + ["Balanced PRC-AUC results are recorded under the same protocol with metric auprc and their qualifier."],
                           "source_locator": "Methods 'AUC metrics for pathogenicity classification' paragraphs 1-2; Supplementary Table 2 'Contents' (header definitions) and column n_var",
                       }})
    PROTOS[key + "-eve"] = add({"id": f"{P}-protocol-{key}-esm1b-eve-shared", "kind": "protocol",
                                "name": f"{label} missense pathogenicity, ESM1b versus EVE on variants scored by both (Brandes et al. 2023 Fig. 2b, Results text)",
                                "description": f"Global ROC-AUC of ESM1b and EVE on the {label} variants scored by both, as quoted in the Results.",
                                "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ART],
                                "links": [{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data}],
                                "attributes": {
                                    "protocol": "Global ROC-AUC over the variants with both ESM1b and EVE scores.",
                                    "version": "Results text (Fig. 2b)",
                                    "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
                                    "denominator": 36537 if key == "clinvar" else 30497,
                                    "limitations": COMMON_LIMITS[:1] + ["Supplementary Table 2's EVE head-to-head row gives slightly different values and counts (see the article source's limitations)."],
                                    "source_locator": "Results 'ESM1b outperforms other VEP methods over clinical and experimental benchmarks' paragraph 2; Fig. 2b legend",
                                }})

# systems: (label, slug, target, method_types, origin, parameters)
DB = "dbNSFP 4.3a score"
SYSTEMS = [
    ("ESM1b", "esm1b", ESM1B_MODEL, "foundation_model", "author_reported", "esm1b_t33_650M_UR50S; missense effect score is the log-likelihood ratio of the alternate versus reference amino acid; proteins longer than 1,022 aa tiled with 1,022 aa windows overlapping by at least 511 aa and combined by a weighted average"),
    ("EVE", "eve", "uc20260930-model-eve", "specialist", "independent_paper", "EVE scores; source not stated beyond 'Other than ESM1b and EVE, ... dbNSFP'"),
    ("SIFT", "sift", "somatic-oncogenicity-20261009-method-sift", "conventional_pipeline", "independent_paper", DB),
    ("PROVEAN", "provean", "somatic-oncogenicity-20261009-method-provean", "conventional_pipeline", "independent_paper", DB),
    ("SIFT4G", "sift4g", "somatic-oncogenicity-20261009-method-sift", "conventional_pipeline", "independent_paper", DB),
    ("MutationAssessor", "mutationassessor", "somatic-oncogenicity-20261009-method-mutationassessor", "specialist", "independent_paper", DB),
    ("MTBAN", "mtban", None, "specialist", "independent_paper", "MTBAN scores (not from dbNSFP); source file not stated"),
    ("phyloP (vertebrate)", "phylop-vertebrate", "somatic-oncogenicity-20261009-method-phylop", "specialist", "independent_paper", DB + " (vertebrate)"),
    ("LRT", "lrt", "somatic-oncogenicity-20261009-method-lrt", "specialist", "independent_paper", DB),
    ("SiPhy", "siphy", "brca-20261009-method-siphy", "specialist", "independent_paper", DB),
    ("GERP++", "gerp", "somatic-oncogenicity-20261009-method-gerp", "specialist", "independent_paper", DB),
    ("phastCons (vertebrate)", "phastcons-vertebrate", "somatic-oncogenicity-20261009-method-phastcons", "specialist", "independent_paper", DB + " (vertebrate)"),
    ("GenoCanyon", "genocanyon", "somatic-oncogenicity-20261009-method-genocanyon", "specialist", "independent_paper", DB),
    ("phyloP (mammalian)", "phylop-mammalian", "somatic-oncogenicity-20261009-method-phylop", "specialist", "independent_paper", DB + " (mammalian)"),
    ("phastCons (mammalian)", "phastcons-mammalian", "somatic-oncogenicity-20261009-method-phastcons", "specialist", "independent_paper", DB + " (mammalian)"),
    ("phastCons (primate)", "phastcons-primate", "somatic-oncogenicity-20261009-method-phastcons", "specialist", "independent_paper", DB + " (primate)"),
    ("phyloP (primate)", "phylop-primate", "somatic-oncogenicity-20261009-method-phylop", "specialist", "independent_paper", DB + " (primate)"),
    ("bStatistic", "bstatistic", "somatic-oncogenicity-20261009-method-bstatistic", "specialist", "independent_paper", DB),
    ("fitCons", "fitcons", "somatic-oncogenicity-20261009-method-integrated-fitcons", "specialist", "independent_paper", DB + "; the three cell-line fitCons versions were excluded, so this is taken to be integrated fitCons"),
]
assert [s[0] for s in SYSTEMS] == INCLUDED

MTBAN = add({"id": f"{P}-method-mtban", "kind": "method", "name": "MTBAN",
             "description": "Missense variant effect predictor added by Brandes et al. alongside the dbNSFP methods (reference 63 of the article).",
             "status": "needs_review", "facets": {"areas": ["protein-function"], "contexts": ["clinical_research"], "method_types": ["specialist"]},
             "source_ids": [S_ART], "links": [],
             "attributes": {"reported_name": "MTBAN", "entity_level": "method",
                            "source_locator": "Methods 'Other VEP methods' paragraph 1",
                            "missing_metadata": {"version": {"reason": "unreported"}}}})

CONF = {}
for label, slug, target, mtype, origin, params in SYSTEMS:
    target = target or MTBAN
    cid = add({"id": f"{P}-config-{slug}", "kind": "configuration",
               "name": f"{label} (Brandes et al. 2023 clinical benchmarks)",
               "description": f"{label} as scored in the Brandes et al. 2023 clinical missense benchmarks.",
               "status": "needs_review",
               "facets": {"areas": ["protein-function"] if slug in ("esm1b", "eve", "mtban") else ["dna-genomes"],
                          "contexts": ["clinical_research"], "method_types": [mtype]},
               "source_ids": [S_ART, S_ST2], "links": [{"relation": "configuration_of", "target_id": target}],
               "attributes": {
                   "reported_name": label,
                   "version": "esm1b_t33_650M_UR50S" if slug == "esm1b" else ("dbNSFP 4.3a" if params.startswith(DB) else "not stated"),
                   "parameters": params,
                   "foundation_model_eligible": slug == "esm1b",
                   "source_locator": f"Supplementary Table 2 column vep_name '{label}'; Methods 'ESM1b' and 'Other VEP methods'",
               }})
    CONF[label] = (cid, origin)

for key, sheet in [("clinvar", "Table_of_results_ClinVar"), ("hgmd", "Table_of_results_HGMD")]:
    dname = "ClinVar" if key == "clinvar" else "HGMD/gnomAD"
    data = D_CLINVAR if key == "clinvar" else D_HGMD
    for label, slug, *_ in SYSTEMS:
        cid, origin = CONF[label]
        row, auroc, auprc = TABLE[key][label]
        ev = add({"id": f"{P}-eval-{key}-all-19-{slug}", "kind": "evaluation",
                  "name": f"{label} on {dname} missense, variants scored by all 19 methods (Brandes et al. 2023)",
                  "description": "Published comparison transcribed from the pinned source; not reproduced.",
                  "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ST2, S_ART],
                  "links": [{"relation": "system", "target_id": cid}, {"relation": "assessment", "target_id": PROTOS[key]},
                            {"relation": "data", "target_id": data}],
                  "attributes": {
                      "origin": origin, "protocol": PROTOS[key], "version": "Supplementary Table 2 as retrieved 2026-10-14",
                      "comparison": {"protocol_id": PROTOS[key], "dataset_version": None,
                                     "split": "Variants scored by all 19 eligible methods",
                                     "population": f"{12095 if key == 'clinvar' else 12357} variants (n_var)",
                                     "inputs": "Precomputed per-variant scores", "adaptation": "zero-shot",
                                     "metric_implementation": "Global ROC-AUC; balanced PRC-AUC averaged over 100 balanced downsamples",
                                     "aggregation": "Pooled over variants", "budget": None},
                      "denominator": 12095 if key == "clinvar" else 12357,
                      "source_locator": f"Supplementary Table 2 sheet '{sheet}' row {row} ('{label}')",
                      "missing_metadata": {"comparison.dataset_version": {"reason": "unreported", "note": "Download dates of the EVE-portal ClinVar file and HGMD release not printed"},
                                           "comparison.budget": {"reason": "inapplicable", "note": "Precomputed scores"}},
                  }})
        for metric, col, val, qual in [("auroc", "B", auroc, "global ROC-AUC over all variants; zero-shot"),
                                       ("auprc", "C", auprc, "balanced PRC-AUC: mean over 100 random downsamples to equal pathogenic and benign counts (80% of the minority class); zero-shot")]:
            pv = shortest(val)
            rid = f"{P}-result-{key}-all-19-{slug}-{metric}"
            loc = f"Supplementary Table 2 sheet '{sheet}' cell {col}{row}, row '{label}', column '{'AUC_AUROC' if col == 'B' else 'AUC_Balanced_AUPRC'}'"
            add({"id": rid, "kind": "result", "name": f"{label} {dname} {'ROC-AUC' if metric == 'auroc' else 'balanced PRC-AUC'} (all-19-methods variant set)",
                 "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                 "status": "needs_review", "facets": {}, "source_ids": [S_ST2],
                 "links": [{"relation": "evaluation", "target_id": ev}],
                 "attributes": {
                     "printed_value": pv, "numeric_value": pv, "metric": metric, "metric_direction": "higher", "unit": "unitless",
                     "metric_qualifier": qual, "source_locator": loc, "raw_xml_value": val,
                     "printed_value_basis": "Shortest round-trip decimal of the number stored in the workbook cell",
                     "missing_metadata": {"uncertainty": {"reason": "unreported"}},
                     "review": review(["deterministic-table-parse"],
                                      "Extracted, not reviewed. The review-evidence pass must re-check this cell against the pinned workbook.",
                                      XLSX_SHA, XLSX_URL,
                                      method_note="Read the pinned workbook with the stdlib OOXML reader in extract/build_esm1b.py; header A1:D1, n_var, the included flag and the 19 method labels are asserted."),
                 }})
            claims_rows.append([rid, S_ST2, loc, pv, "result"])

# text values: ESM1b vs EVE shared set
for key, sent, vals in [("clinvar", S1, [("ESM1b", "0.905"), ("EVE", "0.885")]),
                        ("hgmd", S2, [("ESM1b", "0.897"), ("EVE", "0.882")])]:
    dname = "ClinVar" if key == "clinvar" else "HGMD/gnomAD"
    data = D_CLINVAR if key == "clinvar" else D_HGMD
    n = 36537 if key == "clinvar" else 30497
    for label, pv in vals:
        cid, origin = CONF[label]
        slug = label.lower()
        ev = add({"id": f"{P}-eval-{key}-esm1b-eve-shared-{slug}", "kind": "evaluation",
                  "name": f"{label} on {dname} missense, ESM1b versus EVE shared variants (Brandes et al. 2023 Results)",
                  "description": "Published comparison transcribed from the pinned source; not reproduced.",
                  "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ART],
                  "links": [{"relation": "system", "target_id": cid}, {"relation": "assessment", "target_id": PROTOS[key + "-eve"]},
                            {"relation": "data", "target_id": data}],
                  "attributes": {
                      "origin": origin, "protocol": PROTOS[key + "-eve"], "version": "Article as retrieved 2026-10-14",
                      "comparison": {"protocol_id": PROTOS[key + "-eve"], "dataset_version": None,
                                     "split": "Variants scored by both ESM1b and EVE", "population": f"{n:,} variants",
                                     "inputs": "Precomputed per-variant scores", "adaptation": "zero-shot",
                                     "metric_implementation": "Global ROC-AUC", "aggregation": "Pooled over variants", "budget": None},
                      "denominator": n,
                      "source_locator": "Results 'ESM1b outperforms other VEP methods over clinical and experimental benchmarks' paragraph 2",
                      "missing_metadata": {"comparison.dataset_version": {"reason": "unreported"},
                                           "comparison.budget": {"reason": "inapplicable", "note": "Precomputed scores"}},
                  }})
        rid = f"{P}-result-{key}-esm1b-eve-shared-{slug}-auroc"
        anchor = "Comparing ESM1b and EVE as classifiers of variant pathogenicity" if key == "clinvar" else "On HGMD/gnomAD (with 27,754 disease-causing and 2,743 common variants"
        loc = f"Results 'ESM1b outperforms other VEP methods over clinical and experimental benchmarks' paragraph 2, sentence beginning '{anchor}'"
        add({"id": rid, "kind": "result", "name": f"{label} {dname} ROC-AUC (ESM1b and EVE shared variants)",
             "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
             "status": "needs_review", "facets": {}, "source_ids": [S_ART],
             "links": [{"relation": "evaluation", "target_id": ev}],
             "attributes": {
                 "printed_value": pv, "numeric_value": pv, "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
                 "metric_qualifier": "global ROC-AUC over all variants; zero-shot",
                 "source_locator": loc,
                 "missing_metadata": {"uncertainty": {"reason": "unreported"}},
                 "review": review(["transcription"],
                                  "Extracted, not reviewed. Supplementary Table 2's EVE head-to-head row prints different values and counts for the same comparison (see source limitations); reviewer to judge which to keep.",
                                  XML_SHA, XML_URL,
                                  method_note="Transcribed from the pinned JATS text; extract/build_esm1b.py asserts the sentence verbatim."),
             }})
        claims_rows.append([rid, S_ART, loc, pv, "result"])

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids))
with open(f"{OUT}/batch.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(f"{OUT}/claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    for row in sorted(claims_rows):
        w.writerow(row)
print(Counter(r["kind"] for r in records))
print(ARCH)
