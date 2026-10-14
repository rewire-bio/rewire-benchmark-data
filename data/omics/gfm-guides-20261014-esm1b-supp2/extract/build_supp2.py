"""Build the gfm-guides-20261014-esm1b-supp2 batch: the parts of Brandes et al. 2023 Supplementary
Table 2 that the first extraction (gfm-guides-20261014-esm1b) left out.

Usage (python3 -I):
  build_supp2.py <st2.xlsx> <brandes.xml> <si.pdf> <repository-root> <batch-dir>

Inputs are the archived artifacts in data/omics/gfm-guides-20261014-esm1b/artifacts/ (gunzipped).
The script asserts every input hash and reads, with a stdlib OOXML reader:

- sheets 'Table_of_results_ClinVar' and 'Table_of_results_HGMD', columns E-I (head to head against
  ESM1b on the variants both methods score) for all 45 comparators, with the header row, the
  'Contents' definitions of those columns, the 'included' flag and the exclusion notes asserted;
- sheet 'Table_of_results_indels' (in-frame indels, ROC-AUC overall and by indel type);
- sheet 'Table_of_results_stop_gains' (stop-gains, ROC-AUC by NMD status).

'NaN' cells are not values and produce no result. Benchmark sizes are checked against the article
text and the Supplementary Information. Every reused record must exist in the store; every new ID
must not.
"""
import csv, glob, hashlib, html, json, os, re, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter

XLSX, XML, SIPDF, REPO, OUT = sys.argv[1:6]
XLSX_SHA = "093c32e4156a801c0dd809a437c87818a4f1d04df92e037cf40222471a3e72e2"
XML_SHA = "919ca366369efbe7e0880565192de127375edddedb1aa43ad023dec612bb4a04"
SI_SHA = "30f1c2713875c7cec40f0beee19864840bc55326ddf68918841f93f8bb897c2a"
XLSX_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-023-01465-0/MediaObjects/41588_2023_1465_MOESM3_ESM.xlsx"
DATE = "2026-10-14"
P = "gfm-guides-20261014-esm1b"
S_ART, S_ST2, S_SI = f"{P}-source-brandes2023-article", f"{P}-source-brandes2023-supplementary-table-2", f"{P}-source-brandes2023-supplementary-information"
ESM1B_MODEL = "uc20260930-model-esm-1b"
NOTE = ("Extraction agent for rewire-benchmark-data issue #163 (Brandes et al. 2023 Supplementary Table 2 follow-up); "
        "extraction only, not a review. Pending an independent review-evidence pass.")
FAC = {"areas": ["dna-genomes", "protein-function"], "contexts": ["clinical_research"]}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


assert sha(XLSX) == XLSX_SHA and sha(XML) == XML_SHA and sha(SIPDF) == SI_SHA, "input hash mismatch"

# ------------------------------------------------------------------ store
store = {}
for path in glob.glob(os.path.join(REPO, "data/entities/*.jsonl")) + glob.glob(os.path.join(REPO, "data/evidence/*/*.jsonl")):
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        store[r["id"]] = r


def existing(id_):
    assert id_ in store, id_
    return id_


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
contents = sheets["Contents"]["A1"]
for definition in [
        "head2head_VEP_auc_AUROC: ROC-AUC performance of the evaluated method when compared head to head against ESM1b",
        "head2head_ESM1b_auc_AUROC: ROC-AUC performance of ESM1b when compared head to head against the evaluated method",
        "head2head_VEP_auc_Balanced_AUPRC: Balanced PRC-AUC performance of the evaluated method when compared head to head against ESM1b",
        "head2head_ESM1b_auc_Balanced_AUPRC: Balanced PRC-AUC performance of ESM1b when compared head to head against the evaluated method",
        "head2head_n_variants: Number of variants in the head-to-head comparison",
        "AUC_indels: ROC-AUC performance of the evaluated method on all indels",
        "AUC_ins: ROC-AUC performance of the evaluated method on insertions",
        "AUC_del: ROC-AUC performance of the evaluated method on deletions",
        "AUC_delins: ROC-AUC performance of the evaluated method on delins variants (i.e. indels that aren’t pure insertions or deletions)",
        "AUC_no_NMD: ROC-AUC performance of the evaluated method on stop gain variants that are expected to not undergo NMD (according to the 50bp rule)",
        "AUC_NMD: ROC-AUC performance of the evaluated method on stop gain variants that are expected to undergo NMD (according to the 50bp rule)",
        "AUC_ALL: ROC-AUC performance of the evaluated method on all stop gain variants"]:
    assert definition in contents, definition


def shortest(v):
    return repr(float(v))


xml = open(XML, encoding="utf-8").read()
flat = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml)))
si_text = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-layout", SIPDF, "-"], capture_output=True, text=True, check=True).stdout)
assert "the distribution of ESM1b effect scores over 1,679 benign and 1,791 pathogenic in-frame indels from ClinVar" in flat
assert "partitioning of the 3,470 in-frame indels into deletions, insertions and deletion–insertion combinations (delins)" in flat
assert "(1) not undergo NMD (3,672 pathogenic and 147 benign variants), (2) undergo NMD (32,362 pathogenic and 198 benign variants) or (3) all stop-gain variants (36,034 pathogenic and 345 benign variants)" in flat
assert "32,441 pathogenic and 198 benign variants expected to lead to NMD, and 36,113 pathogenic and 345 benign variants overall" in flat
assert "the final indel benchmark included 1,679 benign and 1,791 pathogenic variants" in si_text
assert "The remaining dataset included 36,034 pathogenic and 345 benign stop-gain variants" in si_text
assert "ClinVar’s FTP site on January 24, 2023" in si_text
assert "All head-to-head comparisons were statistically significant with P < 0.001" in flat

records, claims_rows = [], []


def add(rec):
    assert rec["id"] not in store, rec["id"]
    records.append(rec)
    return rec["id"]


def review(locator_note):
    return {"method": ["deterministic-table-parse"], "reviewer": ["claude"], "reviewer_note": NOTE, "date": DATE,
            "artifact_sha256": XLSX_SHA, "retrieval_url": XLSX_URL,
            "method_note": f"Read the pinned workbook with the stdlib OOXML reader in extract/build_supp2.py; {locator_note}",
            "note": "Extracted, not reviewed. printed_value is the shortest round-trip decimal of the number stored in the cell. The review-evidence pass must re-check this cell against the pinned workbook."}


def result(rid, name, ev, metric, qual, raw, sheet, ref, row_label, column, locator_note):
    pv = shortest(raw)
    loc = f"Supplementary Table 2 sheet '{sheet}' cell {ref}, row '{row_label}', column '{column}'"
    add({"id": rid, "kind": "result", "name": name,
         "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
         "status": "needs_review", "facets": {}, "source_ids": [S_ST2], "links": [{"relation": "evaluation", "target_id": ev}],
         "attributes": {"printed_value": pv, "numeric_value": pv, "metric": metric, "metric_direction": "higher", "unit": "unitless",
                        "metric_qualifier": qual, "source_locator": loc, "raw_xml_value": raw,
                        "printed_value_basis": "Shortest round-trip decimal of the number stored in the workbook cell",
                        "missing_metadata": {"uncertainty": {"reason": "unreported"}},
                        "review": review(locator_note)}})
    claims_rows.append([rid, S_ST2, loc, pv, "result"])


# =================================================================== head-to-head
ESM1B_CFG = existing(f"{P}-config-esm1b")
INCLUDED = {  # label -> existing configuration slug
    "EVE": "eve", "SIFT": "sift", "PROVEAN": "provean", "SIFT4G": "sift4g", "MutationAssessor": "mutationassessor", "MTBAN": "mtban",
    "phyloP (vertebrate)": "phylop-vertebrate", "LRT": "lrt", "SiPhy": "siphy", "GERP++": "gerp",
    "phastCons (vertebrate)": "phastcons-vertebrate", "GenoCanyon": "genocanyon", "phyloP (mammalian)": "phylop-mammalian",
    "phastCons (mammalian)": "phastcons-mammalian", "phastCons (primate)": "phastcons-primate", "phyloP (primate)": "phylop-primate",
    "bStatistic": "bstatistic", "fitCons": "fitcons"}
EXCLUDED = {  # label -> (slug, method record, description)
    "BayesDel (no AF)": ("bayesdel-no-af", "uc-clinical-20260930-method-bayesdel", "BayesDel deleteriousness score without allele-frequency features: precomputed scores from dbNSFP 4.3a."),
    "BayesDel (with AF)": ("bayesdel-with-af", "uc-clinical-20260930-method-bayesdel", "BayesDel deleteriousness score with allele-frequency features: precomputed scores from dbNSFP 4.3a."),
    "CADD": ("cadd", "somatic-oncogenicity-20261009-method-cadd", "CADD: precomputed missense scores from dbNSFP 4.3a."),
    "ClinPred": ("clinpred", "somatic-oncogenicity-20261009-method-clinpred", "ClinPred: precomputed scores from dbNSFP 4.3a."),
    "DANN": ("dann", "somatic-oncogenicity-20261009-method-dann", "DANN: precomputed scores from dbNSFP 4.3a."),
    "DEOGEN2": ("deogen2", "somatic-oncogenicity-20261009-method-deogen2", "DEOGEN2: precomputed scores from dbNSFP 4.3a."),
    "Eigen": ("eigen", "somatic-oncogenicity-20261009-method-eigen", "Eigen: precomputed scores from dbNSFP 4.3a."),
    "Eigen-PC": ("eigen-pc", "somatic-oncogenicity-20261009-method-eigen", "Eigen-PC, the principal-component version of Eigen: precomputed scores from dbNSFP 4.3a."),
    "FATHMM": ("fathmm", "somatic-oncogenicity-20261009-method-fathmm", "FATHMM: precomputed scores from dbNSFP 4.3a."),
    "FATHMM-MKL": ("fathmm-mkl", "somatic-oncogenicity-20261009-method-fathmm-mkl", "FATHMM-MKL: precomputed scores from dbNSFP 4.3a."),
    "FATHMM-XF": ("fathmm-xf", "somatic-oncogenicity-20261009-method-fathmm-xf", "FATHMM-XF: precomputed scores from dbNSFP 4.3a."),
    "LIST-S2": ("list-s2", "somatic-oncogenicity-20261009-method-list-s2", "LIST-S2: precomputed scores from dbNSFP 4.3a."),
    "M-CAP": ("m-cap", "somatic-oncogenicity-20261009-method-m-cap", "M-CAP: precomputed scores from dbNSFP 4.3a."),
    "MPC": ("mpc", "somatic-oncogenicity-20261009-method-mpc", "MPC: precomputed scores from dbNSFP 4.3a."),
    "MVP": ("mvp", "somatic-oncogenicity-20261009-method-mvp", "MVP: precomputed scores from dbNSFP 4.3a."),
    "MetaLR": ("metalr", "somatic-oncogenicity-20261009-method-metalr", "MetaLR: precomputed scores from dbNSFP 4.3a."),
    "MetaRNN": ("metarnn", "somatic-oncogenicity-20261009-method-metarnn", "MetaRNN: precomputed scores from dbNSFP 4.3a."),
    "MetaSVM": ("metasvm", "somatic-oncogenicity-20261009-method-metasvm", "MetaSVM: precomputed scores from dbNSFP 4.3a."),
    "MutPred": ("mutpred", "somatic-oncogenicity-20261009-method-mutpred", "MutPred: precomputed scores from dbNSFP 4.3a."),
    "MutationTaster": ("mutationtaster", "somatic-oncogenicity-20261009-method-mutationtaster", "MutationTaster: precomputed scores from dbNSFP 4.3a."),
    "Polyphen2 (HDIV)": ("polyphen2-hdiv", "somatic-oncogenicity-20261009-method-polyphen2", "PolyPhen-2 HumDiv-trained model: precomputed scores from dbNSFP 4.3a."),
    "Polyphen2 (HVAR)": ("polyphen2-hvar", "somatic-oncogenicity-20261009-method-polyphen2", "PolyPhen-2 HumVar-trained model: precomputed scores from dbNSFP 4.3a."),
    "PrimateAI": ("primateai", "somatic-oncogenicity-20261009-method-primateai", "PrimateAI: precomputed scores from dbNSFP 4.3a."),
    "REVEL": ("revel", "somatic-oncogenicity-20261009-method-revel", "REVEL: precomputed scores from dbNSFP 4.3a."),
    "VARITY_ER": ("varity-er", "somatic-oncogenicity-20261009-method-varity", "VARITY_ER, the VARITY model for extremely rare variants: precomputed scores, not from dbNSFP."),
    "VARITY_R": ("varity-r", "somatic-oncogenicity-20261009-method-varity", "VARITY_R, the VARITY model for rare variants: precomputed scores, not from dbNSFP."),
    "VEST4": ("vest4", "somatic-oncogenicity-20261009-method-vest4", "VEST4: precomputed scores from dbNSFP 4.3a."),
}
assert len(INCLUDED) == 18 and len(EXCLUDED) == 27

# method types: copy what the store's existing configurations of the same method use
mtypes_of = {}
for r in store.values():
    if r["kind"] == "configuration":
        for link in r["links"]:
            if link["relation"] == "configuration_of" and r["facets"].get("method_types"):
                mtypes_of.setdefault(link["target_id"], r["facets"]["method_types"])

H2H_HEAD = ["vep_name", "AUC_AUROC", "AUC_Balanced_AUPRC", "n_var", "head2head_VEP_auc_AUROC", "head2head_ESM1b_auc_AUROC",
            "head2head_VEP_auc_Balanced_AUPRC", "head2head_ESM1b_auc_Balanced_AUPRC", "head2head_n_variants", "included", "note"]
H2H_ROWS = {}
NOTES = {}
for key, sheet in [("clinvar", "Table_of_results_ClinVar"), ("hgmd", "Table_of_results_HGMD")]:
    cells = sheets[sheet]
    assert [cells[f"{c}1"] for c in "ABCDEFGHIJK"] == H2H_HEAD, sheet
    assert cells["A2"] == "ESM1b" and "E2" not in cells
    rows = {}
    for r in range(3, 48):
        label = cells[f"A{r}"]
        flag = cells[f"J{r}"]
        assert flag == ("1" if label in INCLUDED else "0"), (sheet, r, label, flag)
        if label in EXCLUDED:
            NOTES.setdefault(label, set()).add(cells[f"K{r}"].strip())
        vals = [cells[f"{c}{r}"] for c in "EFGHI"]
        assert all(re.fullmatch(r"\d+\.\d+(e-?\d+)?", v) for v in vals), (sheet, r, vals)
        rows[label] = (r, vals)
    assert f"A48" not in cells, sheet
    assert set(rows) == set(INCLUDED) | set(EXCLUDED), sheet
    H2H_ROWS[key] = rows
for label, notes in NOTES.items():
    assert len(notes) == 1, (label, notes)  # same exclusion note on both sheets

# new configurations for the 27 methods excluded from the paper's main comparison
CONF = {label: existing(f"{P}-config-{slug}") for label, slug in INCLUDED.items()}
for label, (slug, method, desc) in EXCLUDED.items():
    existing(method)
    varity = label.startswith("VARITY")
    CONF[label] = add({
        "id": f"{P}-config-{slug}", "kind": "configuration", "name": f"{label} (Brandes et al. 2023 head-to-head comparison)",
        "description": desc, "status": "needs_review",
        "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"],
                   "method_types": mtypes_of.get(method, ["supervised_machine_learning"])},
        "source_ids": [S_ART, S_ST2], "links": [{"relation": "configuration_of", "target_id": method}],
        "attributes": {
            "reported_name": label,
            **({"missing_metadata": {"version": {"reason": "unreported", "note": "VARITY is not in dbNSFP; the score file is not stated"}}}
               if varity else {"version": "dbNSFP 4.3a"}),
            "parameters": "VARITY scores (not from dbNSFP); source file not stated" if varity else "dbNSFP 4.3a score",
            "foundation_model_eligible": False,
            "training_overlap": f"Excluded from the paper's main clinical comparison; Supplementary Table 2 note: '{next(iter(NOTES[label]))}'",
            "source_locator": f"Supplementary Table 2 column vep_name '{label}' and column 'note'; Methods 'Other VEP methods'",
            "provenance_note": "Scored head to head against ESM1b in Brandes et al. 2023 Supplementary Table 2 only; not part of the 19-method comparison in Fig. 2e,f.",
        }})

DATA = {"clinvar": existing(f"{P}-data-clinvar-missense-eve-portal"), "hgmd": existing(f"{P}-data-hgmd-dm-vs-gnomad-common-missense")}
BENCH_MISSENSE = existing(f"{P}-benchmark-brandes2023-clinical-missense")
H2H_PROTO = {}
for key, label in [("clinvar", "ClinVar"), ("hgmd", "HGMD/gnomAD")]:
    H2H_PROTO[key] = add({
        "id": f"{P}-protocol-{key}-head-to-head", "kind": "protocol",
        "name": f"{label} missense pathogenicity, ESM1b head to head with one other method on the variants both score (Brandes et al. 2023 Fig. 2f, Supplementary Table 2)",
        "description": f"Global ROC-AUC and balanced PRC-AUC of ESM1b and one other method, each on the {label} variants that both methods score.",
        "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ART, S_ST2],
        "links": [{"relation": "part_of", "target_id": BENCH_MISSENSE}, {"relation": "uses_data", "target_id": DATA[key]}],
        "attributes": {
            "protocol": "Scores used directly (no training on these labels). For each comparator, restrict the labelled set to the variants with both an ESM1b and a comparator score; compute global ROC-AUC and balanced PRC-AUC (downsample to equal pathogenic and benign counts at 80% of the minority class, mean over 100 repeats) for both methods on that set.",
            "version": f"Supplementary Table 2 sheet 'Table_of_results_{'ClinVar' if key == 'clinvar' else 'HGMD'}', columns head2head_*",
            "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
            "limitations": [
                "Benchmark built by the ESM1b workflow's authors (author-reported for ESM1b).",
                "Each comparator has its own variant set, so comparator values are comparable only with the ESM1b value on the same set, not with each other.",
                "27 of the 45 comparators were excluded from the paper's main comparison because they were trained on clinical databases or use allele frequency; their head-to-head values are inflated by that overlap. The reason is in each configuration's training_overlap.",
            ],
            "source_locator": "Results 'ESM1b outperforms other VEP methods over clinical and experimental benchmarks', paragraph beginning 'In addition to EVE, we compared ESM1b to 44 other VEP methods'; Methods 'AUC metrics for pathogenicity classification'; Supplementary Table 2 'Contents' (header definitions)",
        }})

H2H_METRICS = [("auroc", "E", "F", "head2head_VEP_auc_AUROC", "head2head_ESM1b_auc_AUROC", "global ROC-AUC over the variants both methods score; zero-shot"),
               ("auprc", "G", "H", "head2head_VEP_auc_Balanced_AUPRC", "head2head_ESM1b_auc_Balanced_AUPRC",
                "balanced PRC-AUC over the variants both methods score: mean over 100 random downsamples to equal pathogenic and benign counts (80% of the minority class); zero-shot")]
for key, sheet in [("clinvar", "Table_of_results_ClinVar"), ("hgmd", "Table_of_results_HGMD")]:
    dname = "ClinVar" if key == "clinvar" else "HGMD/gnomAD"
    for label, (row, vals) in sorted(H2H_ROWS[key].items(), key=lambda kv: kv[1][0]):
        slug = INCLUDED.get(label) or EXCLUDED[label][0]
        n = int(float(vals[4]))
        assert float(vals[4]) == n
        sub = add({"id": f"{P}-data-{key}-h2h-{slug}", "kind": "dataset_subset",
                   "name": f"{dname} missense variants scored by both ESM1b and {label} (Brandes et al. 2023)",
                   "description": f"The {n:,} variants of the {dname} missense benchmark that have both an ESM1b and a {label} score.",
                   "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ST2],
                   "links": [{"relation": "used_in", "target_id": H2H_PROTO[key]}],
                   "attributes": {"split": "Whole labelled set restricted to variants scored by both methods",
                                  "scored_count": n, "source_dataset_label": dname,
                                  "subset_scope": f"Variants with both ESM1b and {label} scores",
                                  "source_locator": f"Supplementary Table 2 sheet '{sheet}' cell I{row}, row '{label}', column 'head2head_n_variants'",
                                  "missing_metadata": {"version": {"reason": "unreported", "note": "Download dates of the EVE-portal ClinVar file and HGMD release not printed"}}}})
        for side, system, origin in [("vep", CONF[label], "independent_paper"), ("esm1b", ESM1B_CFG, "author_reported")]:
            who = label if side == "vep" else "ESM1b"
            ev = add({"id": f"{P}-eval-{key}-h2h-{slug}-{side}", "kind": "evaluation",
                      "name": f"{who} on {dname} missense, head to head {'against ESM1b' if side == 'vep' else 'against ' + label} (Brandes et al. 2023)",
                      "description": "Published comparison transcribed from the pinned source; not reproduced.",
                      "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ST2, S_ART],
                      "links": [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": H2H_PROTO[key]},
                                {"relation": "data", "target_id": sub}],
                      "attributes": {
                          "origin": origin, "protocol": H2H_PROTO[key], "version": "Supplementary Table 2 as retrieved 2026-10-14",
                          "comparison": {"protocol_id": H2H_PROTO[key], "dataset_version": None,
                                         "split": f"Variants scored by both ESM1b and {label}",
                                         "population": f"{n} variants (head2head_n_variants)",
                                         "inputs": "Precomputed per-variant scores", "adaptation": "zero-shot",
                                         "metric_implementation": "Global ROC-AUC; balanced PRC-AUC averaged over 100 balanced downsamples",
                                         "aggregation": "Pooled over variants", "budget": None},
                          "denominator": n,
                          "source_locator": f"Supplementary Table 2 sheet '{sheet}' row {row} ('{label}'), columns E-I",
                          "missing_metadata": {"comparison.dataset_version": {"reason": "unreported", "note": "Download dates of the EVE-portal ClinVar file and HGMD release not printed"},
                                               "comparison.budget": {"reason": "inapplicable", "note": "Precomputed scores"}},
                      }})
            for metric, vcol, ecol, vhead, ehead, qual in H2H_METRICS:
                col, head = (vcol, vhead) if side == "vep" else (ecol, ehead)
                raw = sheets[sheet][f"{col}{row}"]
                result(f"{P}-result-{key}-h2h-{slug}-{side}-{metric}",
                       f"{who} {dname} {'ROC-AUC' if metric == 'auroc' else 'balanced PRC-AUC'} (head to head, {label} variant set)",
                       ev, metric, qual, raw, sheet, f"{col}{row}", label, head,
                       "header row A1:K1, the 'Contents' column definitions, the included flag of every row and the set of 45 comparator labels asserted.")

# =================================================================== indels and stop-gains
BENCH_MR = add({"id": f"{P}-benchmark-brandes2023-clinvar-multiresidue", "kind": "benchmark",
                "name": "Brandes et al. 2023 ClinVar in-frame indel and stop-gain pathogenicity benchmarks",
                "description": "ROC-AUC of ESM1b-based scores, CADD and simple baselines for pathogenic versus benign ClinVar in-frame indels and stop-gain variants.",
                "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ART, S_ST2, S_SI], "links": [],
                "attributes": {"entity_level": "suite", "version": "Nature Genetics 2023 version of record",
                               "task": "Pathogenicity classification of in-frame indels and stop-gain variants",
                               "scope_note": "Two ClinVar-derived labelled sets built by the authors. Only CADD among published predictors is compared on indels, because most indel predictors are trained on ClinVar; no published predictor is compared on stop-gains.",
                               "source_locator": "Results 'ESM1b can predict the effects of multiresidue variants' and Fig. 4 legend; Methods 'Generalized effect scores for indels and stop-gain variants', 'Baseline scores of indel and stop-gain variant effects'; Supplementary Methods 'Indels and stop gain ClinVar benchmarks'"}})
D_INDEL = add({"id": f"{P}-data-clinvar-inframe-indels", "kind": "dataset",
               "name": "ClinVar in-frame indels, pathogenic vs benign (Brandes et al. 2023)",
               "description": "1,791 pathogenic and 1,679 benign in-frame insertions, deletions and deletion-insertions with at least one ClinVar gold star, mapped to RefSeq protein sequences.",
               "status": "needs_review", "facets": dict(FAC), "source_ids": [S_SI, S_ART], "links": [],
               "attributes": {"version": "ClinVar variant_summary.txt.gz downloaded 2023-01-24 (GRCh38)",
                              "split": "Whole labelled set; no training on labels",
                              "population": "ClinVar in-frame indels with at least one gold star; 17 with mismatching RefSeq sequences and 24 duplicates or with non-standard amino acids removed",
                              "denominator": 3470,
                              "source_locator": "Supplementary Methods 'Indels and stop gain ClinVar benchmarks' paragraph 1; Fig. 4a,b legend"}})
D_STOP = add({"id": f"{P}-data-clinvar-stop-gains", "kind": "dataset",
              "name": "ClinVar stop-gain variants, pathogenic vs benign (Brandes et al. 2023)",
              "description": "36,034 pathogenic and 345 benign stop-gain variants with at least one ClinVar gold star and RefSeq exon annotations, split by whether the 50 bp rule predicts nonsense-mediated decay.",
              "status": "needs_review", "facets": dict(FAC), "source_ids": [S_SI, S_ART], "links": [],
              "attributes": {"version": "ClinVar variant_summary.txt.gz downloaded 2023-01-24 (GRCh38)",
                             "split": "Whole labelled set; no training on labels",
                             "population": "ClinVar stop-gain variants with at least one gold star; 110 without exon annotations removed",
                             "denominator": 36379,
                             "denominator_warning": "The Methods ('AUC metrics for pathogenicity classification', stop-gain bootstrap paragraph) give 32,441 pathogenic NMD variants and 36,113 pathogenic overall; the Fig. 4d legend and the Supplementary Methods give 32,362 and 36,034.",
                             "source_locator": "Supplementary Methods 'Indels and stop gain ClinVar benchmarks' paragraph 2; Fig. 4d legend; Methods 'AUC metrics for pathogenicity classification', paragraph on bootstrapping the stop-gain ROC-AUC"}})
SUBS = {}
for slug, parent, name, desc, scope in [
        ("insertions", D_INDEL, "ClinVar in-frame insertions", "The pure insertions among the ClinVar in-frame indels.", "AUC_ins"),
        ("deletions", D_INDEL, "ClinVar in-frame deletions", "The pure deletions among the ClinVar in-frame indels.", "AUC_del"),
        ("delins", D_INDEL, "ClinVar in-frame deletion-insertions", "The ClinVar in-frame indels that are neither pure insertions nor pure deletions.", "AUC_delins"),
        ("no-nmd", D_STOP, "ClinVar stop-gains not expected to undergo NMD", "Stop-gain variants for which the 50 bp rule predicts no nonsense-mediated decay: 3,672 pathogenic and 147 benign.", "AUC_no_NMD"),
        ("nmd", D_STOP, "ClinVar stop-gains expected to undergo NMD", "Stop-gain variants for which the 50 bp rule predicts nonsense-mediated decay: 32,362 pathogenic and 198 benign in the Fig. 4d legend (32,441 pathogenic in the Methods).", "AUC_NMD")]:
    base = "clinvar-inframe-indels" if parent == D_INDEL else "clinvar-stop-gains"
    attrs = {"split": "Whole labelled set; no training on labels", "subset_scope": desc,
             "source_dataset_label": "ClinVar in-frame indels" if parent == D_INDEL else "ClinVar stop-gains",
             "source_locator": f"Supplementary Table 2 'Contents', column {scope}; " + ("Fig. 4b legend (right panel)" if parent == D_INDEL else "Fig. 4d legend; Methods 'AUC metrics for pathogenicity classification', paragraph on bootstrapping the stop-gain ROC-AUC"),
             "missing_metadata": {"version": {"reason": "inapplicable", "note": "Subset of the parent dataset"}}}
    if slug == "no-nmd":
        attrs["positive_count"] = 3672
        attrs["scored_count"] = 3819
    elif parent == D_INDEL:
        attrs["missing_metadata"]["scored_count"] = {"reason": "unreported", "note": "Per-type counts are shown only in the Fig. 4b pie chart"}
    else:
        attrs["missing_metadata"]["scored_count"] = {"reason": "conflicting", "note": "32,560 by the Fig. 4d legend, 32,639 by the Methods"}
    SUBS[slug] = add({"id": f"{P}-data-{base}-{slug}", "kind": "dataset_subset", "name": f"{name} (Brandes et al. 2023)",
                      "description": desc, "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ST2, S_ART, S_SI],
                      "links": [], "attributes": attrs})
P_INDEL = add({"id": f"{P}-protocol-clinvar-inframe-indels", "kind": "protocol",
               "name": "ClinVar in-frame indel pathogenicity, ROC-AUC (Brandes et al. 2023 Fig. 4b, Supplementary Table 2)",
               "description": "Global ROC-AUC of each indel score for pathogenic versus benign ClinVar in-frame indels, over all indels and by indel type.",
               "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ART, S_ST2],
               "links": [{"relation": "part_of", "target_id": BENCH_MR}, {"relation": "uses_data", "target_id": D_INDEL}],
               "attributes": {"protocol": "Scores used directly (no training on these labels); every method scored on the same 3,470 indels. ESM1b scores are pseudo-log-likelihood ratios between mutated and wild-type sequences; baselines score sequence dissimilarity.",
                              "version": "Supplementary Table 2 sheet 'Table_of_results_indels'",
                              "metric": "auroc", "metric_direction": "higher", "unit": "unitless", "denominator": 3470,
                              "limitations": ["Benchmark built by the ESM1b workflow's authors (author-reported for ESM1b and the baselines).",
                                              "CADD is the only published predictor compared; the others that score indels are trained on ClinVar.",
                                              "Per-type ROC-AUCs are printed only for the three ESM1b PLLR scores where available and CADD; the workbook leaves the other cells 'NaN'."],
                              "source_locator": "Results 'ESM1b can predict the effects of multiresidue variants', paragraph beginning 'We compared ESM1b to other models'; Methods 'Generalized effect scores for indels and stop-gain variants' and 'Baseline scores of indel and stop-gain variant effects'; Supplementary Table 2 'Contents'"}})
P_STOP = add({"id": f"{P}-protocol-clinvar-stop-gains", "kind": "protocol",
              "name": "ClinVar stop-gain pathogenicity by NMD status, ROC-AUC (Brandes et al. 2023 Fig. 4d, Supplementary Table 2)",
              "description": "ROC-AUC of each stop-gain score for pathogenic versus benign ClinVar stop-gains, on variants the 50 bp rule predicts to escape or undergo nonsense-mediated decay, and on all.",
              "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ART, S_ST2],
              "links": [{"relation": "part_of", "target_id": BENCH_MR}, {"relation": "uses_data", "target_id": D_STOP}],
              "attributes": {"protocol": "Scores used directly (no training on these labels). The ESM1b stop-gain score is the lowest missense LLR in the region lost after the new stop codon; baselines are the number and percentage of residues lost and the binary 50 bp NMD rule.",
                             "version": "Supplementary Table 2 sheet 'Table_of_results_stop_gains'",
                             "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
                             "limitations": ["Benchmark built by the ESM1b workflow's authors (author-reported for ESM1b and the baselines).",
                                             "Classes are highly imbalanced (345 benign of 36,379).",
                                             "Fig. 4d plots the mean of 20 bootstrap iterations, each sampling 140 pathogenic and 140 benign variants; whether the workbook values are those means or ROC-AUCs on the whole sets is not stated.",
                                             "The 50 bp rule gives binary labels, so only its all-variant ROC-AUC is printed."],
                             "source_locator": "Results 'ESM1b can predict the effects of multiresidue variants', paragraph beginning 'Stop-gain variant effects can be predicted'; Methods 'Generalized effect scores for indels and stop-gain variants', 'Baseline scores of indel and stop-gain variant effects' and 'AUC metrics for pathogenicity classification' (stop-gain bootstrap paragraph); Supplementary Table 2 'Contents'"}})

ESM_PARAMS = "esm1b_t33_650M_UR50S; sequences longer than 1,022 amino acids scored on a 1,022-residue window around the variant"
NEW_SYS = {
    "ESM1b-aPLLR": add({"id": f"{P}-config-esm1b-apllr", "kind": "configuration", "name": "ESM1b absolute-valued PLLR indel score (Brandes et al. 2023)",
                        "description": "ESM-1b in-frame indel score: the absolute value of the pseudo-log-likelihood ratio between the mutated and wild-type protein sequences, so likelihood gains and losses both count as damaging.",
                        "status": "needs_review", "facets": {"areas": ["protein-function"], "contexts": ["clinical_research"], "method_types": ["foundation_model"]},
                        "source_ids": [S_ART, S_ST2], "links": [{"relation": "configuration_of", "target_id": existing(ESM1B_MODEL)}],
                        "attributes": {"reported_name": "ESM1b-aPLLR", "version": "esm1b_t33_650M_UR50S", "parameters": ESM_PARAMS + "; |PLL(mut) - PLL(WT)|",
                                       "foundation_model_eligible": True, "source_locator": "Methods 'Generalized effect scores for indels and stop-gain variants' paragraph 3; Supplementary Table 2 sheet 'Table_of_results_indels' row 'ESM1b-aPLLR'"}}),
    "ESM1b-PLLR": add({"id": f"{P}-config-esm1b-pllr", "kind": "configuration", "name": "ESM1b PLLR indel score (Brandes et al. 2023)",
                       "description": "ESM-1b in-frame indel score: the pseudo-log-likelihood of the mutated protein sequence minus that of the wild-type sequence.",
                       "status": "needs_review", "facets": {"areas": ["protein-function"], "contexts": ["clinical_research"], "method_types": ["foundation_model"]},
                       "source_ids": [S_ART, S_ST2], "links": [{"relation": "configuration_of", "target_id": ESM1B_MODEL}],
                       "attributes": {"reported_name": "ESM1b-PLLR", "version": "esm1b_t33_650M_UR50S", "parameters": ESM_PARAMS + "; PLL(mut) - PLL(WT) ('vanilla' PLLR)",
                                      "foundation_model_eligible": True, "source_locator": "Methods 'Generalized effect scores for indels and stop-gain variants' paragraphs 1-3; Supplementary Table 2 sheet 'Table_of_results_indels' row 'ESM1b-PLLR'"}}),
    "ESM1b-wPLLR": add({"id": f"{P}-config-esm1b-wpllr", "kind": "configuration", "name": "ESM1b weighted PLLR indel score (Brandes et al. 2023)",
                        "description": "ESM-1b in-frame indel score: the pseudo-log-likelihoods of the mutated and wild-type sequences each divided by sequence length before subtraction, to correct for indel size.",
                        "status": "needs_review", "facets": {"areas": ["protein-function"], "contexts": ["clinical_research"], "method_types": ["foundation_model"]},
                        "source_ids": [S_ART, S_ST2], "links": [{"relation": "configuration_of", "target_id": ESM1B_MODEL}],
                        "attributes": {"reported_name": "ESM1b-wPLLR", "version": "esm1b_t33_650M_UR50S", "parameters": ESM_PARAMS + "; PLL(mut)/L(mut) - PLL(WT)/L(WT)",
                                       "foundation_model_eligible": True, "source_locator": "Methods 'Generalized effect scores for indels and stop-gain variants' paragraph 3; Supplementary Table 2 sheet 'Table_of_results_indels' row 'ESM1b-wPLLR'"}}),
    "ESM1b-minLLR": add({"id": f"{P}-config-esm1b-minllr", "kind": "configuration", "name": "ESM1b minimum-LLR stop-gain score (Brandes et al. 2023)",
                         "description": "ESM-1b stop-gain score: the lowest missense log-likelihood ratio among all possible missense variants in the protein region lost after the new stop codon.",
                         "status": "needs_review", "facets": {"areas": ["protein-function"], "contexts": ["clinical_research"], "method_types": ["foundation_model"]},
                         "source_ids": [S_ART, S_ST2], "links": [{"relation": "configuration_of", "target_id": ESM1B_MODEL}],
                         "attributes": {"reported_name": "ESM1b-minLLR", "version": "esm1b_t33_650M_UR50S",
                                        "parameters": "esm1b_t33_650M_UR50S missense LLRs over the whole protein (sliding windows above 1,022 amino acids); minimum over the lost region",
                                        "foundation_model_eligible": True, "source_locator": "Methods 'Generalized effect scores for indels and stop-gain variants' paragraph 4; Supplementary Table 2 sheet 'Table_of_results_stop_gains' row 'ESM1b-minLLR'"}}),
    "CADD": add({"id": f"{P}-config-cadd-indels", "kind": "configuration", "name": "CADD in-frame indel scores (Brandes et al. 2023)",
                 "description": "CADD deleteriousness scores for in-frame indels.",
                 "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"],
                                                      "method_types": mtypes_of.get("somatic-oncogenicity-20261009-method-cadd", ["supervised_machine_learning"])},
                 "source_ids": [S_ART, S_ST2], "links": [{"relation": "configuration_of", "target_id": existing("somatic-oncogenicity-20261009-method-cadd")}],
                 "attributes": {"reported_name": "CADD", "foundation_model_eligible": False,
                                "training_overlap": "The article says CADD, unlike most indel predictors, was not directly trained on ClinVar",
                                "source_locator": "Results 'ESM1b can predict the effects of multiresidue variants', paragraph beginning 'We compared ESM1b to other models'; Supplementary Table 2 sheet 'Table_of_results_indels' row 'CADD'",
                                "missing_metadata": {"version": {"reason": "unreported", "note": "The CADD version and score source for indels are not stated; dbNSFP holds SNV scores only"}}}}),
}
LEV = existing("flip-method-levenshtein")
for label, slug, name, desc in [
        ("Alignment", "pairwise-alignment-score", "Pairwise alignment score (indel baseline)", "Scores an in-frame indel by the global alignment score between the wild-type and mutated protein sequences (match 2, mismatch -1); lower similarity means more likely damaging."),
        ("BlastP", "blastp-score", "BlastP score (indel baseline)", "Scores an in-frame indel by the BlastP alignment score between the wild-type and mutated protein sequences, with BLOSUM62 substitution scores and gap penalties."),
        ("num. AA lost", "residues-lost-count", "Number of residues lost (stop-gain baseline)", "Scores a stop-gain variant by the number of amino acids lost after the new stop codon."),
        ("pct. AA lost", "residues-lost-fraction", "Percentage of residues lost (stop-gain baseline)", "Scores a stop-gain variant by the percentage of the wild-type protein length lost after the new stop codon."),
        ("50bp rule", "nmd-50bp-rule", "50 bp rule for nonsense-mediated decay", "Labels a stop-gain variant as triggering nonsense-mediated decay when the new stop codon lies more than 50 base pairs upstream of the last exon junction in the coding region; a binary score.")]:
    NEW_SYS[label] = add({"id": f"{P}-method-{slug}", "kind": "method", "name": name, "description": desc, "status": "needs_review",
                          "facets": {"areas": ["protein-function"] if "AA" in label or label in ("Alignment", "BlastP") else ["dna-genomes"],
                                     "contexts": ["clinical_research"], "method_types": ["conventional_pipeline"]},
                          "source_ids": [S_ART], "links": [],
                          "attributes": {"reported_name": label, "entity_level": "method",
                                         "source_locator": "Methods 'Baseline scores of indel and stop-gain variant effects'",
                                         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Baseline defined in the article's Methods"}}}})
NEW_SYS["Edit distance"] = LEV

ORIGIN = {"CADD": "independent_paper"}
for sheet, proto, dataset, head, cols, rows in [
        ("Table_of_results_indels", P_INDEL, D_INDEL, ["method", "AUC_indels", "AUC_ins", "AUC_del", "AUC_delins"],
         [("B", "AUC_indels", None, "all in-frame indels"), ("C", "AUC_ins", "insertions", "insertions"),
          ("D", "AUC_del", "deletions", "deletions"), ("E", "AUC_delins", "delins", "deletion-insertions")],
         ["ESM1b-aPLLR", "ESM1b-PLLR", "ESM1b-wPLLR", "CADD", "Alignment", "BlastP", "Edit distance"]),
        ("Table_of_results_stop_gains", P_STOP, D_STOP, ["method", "AUC_no_NMD", "AUC_NMD", "AUC_ALL"],
         [("B", "AUC_no_NMD", "no-nmd", "stop-gains not expected to undergo NMD (50 bp rule)"),
          ("C", "AUC_NMD", "nmd", "stop-gains expected to undergo NMD (50 bp rule)"), ("D", "AUC_ALL", None, "all stop-gains")],
         ["ESM1b-minLLR", "num. AA lost", "pct. AA lost", "50bp rule"])]:
    cells = sheets[sheet]
    assert [cells[f"{c}1"] for c in "ABCDE"[:len(head)]] == head, sheet
    assert [cells[f"A{r}"] for r in range(2, 2 + len(rows))] == rows, sheet
    assert f"A{2 + len(rows)}" not in cells, sheet
    for i, label in enumerate(rows):
        r = 2 + i
        system = NEW_SYS[label]
        sys_slug = system.split("-config-")[-1] if "-config-" in system else system.split("-method-")[-1]
        for col, colname, subslug, scope in cols:
            raw = cells[f"{col}{r}"]
            if raw == "NaN":
                continue
            assert re.fullmatch(r"\d+\.\d+", raw), (sheet, col, r, raw)
            data = SUBS[subslug] if subslug else dataset
            dslug = data.removeprefix(f"{P}-data-")
            eid = f"{P}-eval-{dslug}-{sys_slug}"
            if eid not in {x["id"] for x in records}:
                add({"id": eid, "kind": "evaluation",
                     "name": f"{label} on {scope} (Brandes et al. 2023)",
                     "description": "Published comparison transcribed from the pinned source; not reproduced.",
                     "status": "needs_review", "facets": dict(FAC), "source_ids": [S_ST2, S_ART],
                     "links": [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": proto},
                               {"relation": "data", "target_id": data}],
                     "attributes": {"origin": ORIGIN.get(label, "author_reported"), "protocol": proto,
                                    "version": "Supplementary Table 2 as retrieved 2026-10-14",
                                    "comparison": {"protocol_id": proto, "dataset_version": "ClinVar variant_summary downloaded 2023-01-24",
                                                   "split": "Whole labelled set", "population": None,
                                                   "inputs": "Wild-type and mutated protein sequences (ESM1b and sequence baselines); variant coordinates (CADD, 50 bp rule)",
                                                   "adaptation": "zero-shot", "metric_implementation": "ROC-AUC",
                                                   "aggregation": None, "budget": None},
                                    "source_locator": f"Supplementary Table 2 sheet '{sheet}' row {r} ('{label}')",
                                    "missing_metadata": {"comparison.population": {"reason": "unreported", "note": "Class counts per subset are not all printed"},
                                                         "comparison.aggregation": {"reason": "unreported", "note": "Whether the value is pooled over the whole set or a bootstrap mean is not stated" if proto == P_STOP else "Pooling over variants is implied but not stated for the workbook values"},
                                                         "comparison.budget": {"reason": "inapplicable", "note": "Precomputed scores"}}}})
            result(f"{eid.replace('-eval-', '-result-')}-auroc", f"{label} ROC-AUC on {scope}", eid, "auroc",
                   f"ROC-AUC, pathogenic versus benign ClinVar {scope}; zero-shot", raw, sheet, f"{col}{r}", label, colname,
                   f"header row and the {len(rows)} method labels in column A asserted; 'NaN' cells skipped.")

# ------------------------------------------------------------------ write
for r in records:  # the store keeps missing_metadata keys sorted (normalizeAttributes)
    if "missing_metadata" in r["attributes"]:
        r["attributes"]["missing_metadata"] = dict(sorted(r["attributes"]["missing_metadata"].items()))
records.sort(key=lambda r: r["id"])
assert len({r["id"] for r in records}) == len(records)
with open(os.path.join(OUT, "batch.jsonl"), "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(OUT, "claims.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(sorted(claims_rows))
counts = Counter(r["kind"] for r in records)
print(dict(sorted(counts.items())))
h2h = sum(1 for r in records if r["kind"] == "result" and "-h2h-" in r["id"])
assert h2h == 360 and counts["result"] == 360 + 26, (h2h, counts["result"])
