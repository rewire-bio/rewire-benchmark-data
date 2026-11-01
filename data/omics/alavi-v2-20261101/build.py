"""Build the Alavi 2026 v2 batch: the rerun AlphaGenome rows of Tables III and IV (issue #213).

Usage: python3 -I build.py <v2 full.pdf> <batch folder>

bioRxiv posted version 2 of 10.64898/2026.10.02.756289 on 2026-10-31, after the author fixed the 1-base
coordinate offset in the AlphaGenome scripts (upstream issue #2). Version 2 replaces v1's three AlphaGenome
rows (either module, splice scorer, junction scorer) with four (composite, splice-site usage, splice-sites,
splice-junctions). Every other cell of Tables III and IV is unchanged from v1; this script asserts that
against the stored v1 results, and writes new records only for the four AlphaGenome rows.

Runs `pdftotext -layout` (poppler 26.08.0) on the pinned PDF, finds the value rows by token pattern, asserts
13 rows per table and the row-label fragments around each row, and checks bracketed percentages against
counts and the accuracy and PPV columns against the row's own counts. Records are written needs_review;
review.py records the review.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

PDF, OUT = sys.argv[1], sys.argv[2]
SHA = "07bd32fffc1b31c222d43b0b18c213928e3fe111cc71c02fe2f95e64e6f7a798"
URL = "https://www.biorxiv.org/content/10.64898/2026.10.02.756289v2.full.pdf"
assert hashlib.sha256(open(PDF, "rb").read()).hexdigest() == SHA
TODAY = "2026-11-01"
text = subprocess.run(["pdftotext", "-layout", PDF, "-"], capture_output=True, text=True, check=True).stdout.split("\n")

V1 = "rna-splicing-20261011-alavi2026"
V1_SRC = V1 + "-source-article"
P = "rna-splicing-20261101-alavi2026-v2"
SRC = P + "-source-article"
SUPP = P + "-source-supplementary-tables"
CODE = P + "-source-scoring-scripts"
COMMIT = "2a3875de6635d3c9b51c71c8018d23df0df98d37"
REPO = "https://github.com/marcel-2c8/splicing-model-eval-2026"
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
EXTRACTOR_NOTE = ("Claude agent for the 2026-11-01 Alavi v2 pass (issue #213); extraction only, not a review. "
                  "No human review claimed.")

records = []


def add(rec):
    assert rec["id"] not in {r["id"] for r in records}, rec["id"]
    records.append(rec)
    return rec["id"]


def store(kind_glob):
    out = {}
    for path in glob.glob(kind_glob):
        for line in open(path):
            r = json.loads(line)
            out[r["id"]] = r
    return out


STORE = {**store("data/entities/*.jsonl"), **store("data/evidence/*/*.jsonl")}

# Sources -------------------------------------------------------------------------------------------------
add({"id": SRC, "kind": "source",
     "name": "Probing Genomic Foundation Models with Splice-Variant Perturbations (Alavi, bioRxiv 2026, version 2)",
     "description": "Version 2 of the Alavi 2026 preprint, posted with rerun AlphaGenome results after the 1-base coordinate offset in its scripts was fixed.",
     "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
     "attributes": {
         "url": "https://doi.org/10.64898/2026.10.02.756289",
         "artifact_url": URL,
         "version": "bioRxiv preprint version 2, posted 2026-10-31; full-text PDF (12 pages)",
         "retrieved_at": "2026-11-01T14:45:27Z",
         "artifact_sha256": SHA,
         "doi": "10.64898/2026.10.02.756289",
         "publication_status": "preprint",
         "licence": "CC-BY-NC-ND-4.0",
         "media_type": "application/pdf",
         "limitations": [
             "Preprint, not peer reviewed; single author (712 North Inc.), no funding; none of the evaluated models was developed by the author.",
             "The bioRxiv JATS XML of version 2 holds metadata only, so the tables were read from the PDF text layer.",
             "Not archived in the batch: CC BY-NC-ND licence; hash and locators only.",
             "Only the AlphaGenome rows of Tables III and IV changed from version 1. Every other cell is printed as in version 1, so the version 1 results stand and the count and percentage mismatches recorded on the version 1 source persist.",
             "Version 2 drops version 1's 'either module' AlphaGenome row, so the version 1 either-module results have no successor.",
             "Methods A still describes the 76 multi-gene positives as substitutions within canonical splice sites of 65 genes; Supplemental Table VI of the version 2 supplement lists the same variants as version 1, of which 26 are at canonical ±1,2 positions.",
             "Methods D says variants were pathogenic 'if their composite score was greater than or equal to 2.60 or their splice-site usage score greater than or equal to 0.93'. Tables III and IV print the composite and splice-site usage as separate rows, which are recorded here as two configurations with one threshold each.",
         ],
         "hash_scope": "SHA-256 of one retrieval of the bioRxiv PDF, downloaded in a browser on 2026-11-01 (bioRxiv refused the scripted request). bioRxiv stamps the PDF when serving it (ModDate D:20261101144527 in this copy), so later retrievals differ.",
         "retrieval_note": "The 2026-11-01 scripted request returned a 17-byte response instead of the PDF; the copy used was downloaded in a browser.",
     }})

add({"id": SUPP, "kind": "source",
     "name": "Alavi 2026 supplementary materials, version 2 (Zenodo 23784751): per-variant model classifications",
     "description": "Version 2 of the Alavi 2026 supplementary archive, holding Supplemental Tables IV to VI as workbooks with the rerun AlphaGenome classifications.",
     "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
     "attributes": {
         "url": "https://doi.org/10.5281/zenodo.23784751",
         "doi": "10.5281/zenodo.23784751",
         "version": "supplementary_materials_alavi_2026_v02.zip, Zenodo record 23784751 (new version of record 23105803), created 2026-10-29",
         "retrieved_at": "2026-11-01T14:42:00Z",
         "artifact_sha256": "4652a256f70c8bde80fbc0408c914b951652b6435a78ad2d1107ab40a014bbac",
         "artifact_format": "ZIP archive of three Office Open XML workbooks and a README",
         "artifact_url": "https://zenodo.org/api/records/23784751/files/supplementary_materials_alavi_2026_v02.zip/content",
         "publication_status": "official_project_source",
         "licence": "CC BY-NC-ND 4.0",
         "limitations": [
             "Author-deposited supplementary data, not peer reviewed.",
             "Per-variant classifications only, not scores or thresholds, so the printed sensitivities and specificities cannot be recomputed from it.",
             "Supplemental Table VI gives the same multi-gene composition as version 01 (classify-table-vi.py of the 2026-10-23 dispute batch, output identical): 26 canonical ±1,2, 35 near-splice intronic and 15 exonic positives; 107 benign.",
             "CC BY-NC-ND 4.0 forbids redistributing the workbooks, so they are not stored in this repository.",
         ],
     }})

add({"id": CODE, "kind": "source",
     "name": "Alavi 2026 AlphaGenome scoring scripts at commit 2a3875de (marcel-2c8/splicing-model-eval-2026)",
     "description": "The author's AlphaGenome scoring scripts after the 1-base coordinate fix, pinned to a commit; the repository was renamed from Probing-genomic-foundation-models-2026.",
     "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
     "attributes": {
         "url": f"{REPO}/tree/{COMMIT}/models/2_alphagenome",
         "artifact_url": f"https://raw.githubusercontent.com/marcel-2c8/splicing-model-eval-2026/{COMMIT}/models/2_alphagenome/2c8_alphagenome_merged_splicing_scorer.py",
         "version": f"marcel-2c8/splicing-model-eval-2026 commit {COMMIT} (2026-10-31)",
         "retrieved_at": "2026-11-01T14:48:00Z",
         "artifact_sha256": "84b4887ca3b44a6600d6a02046ab6de9d2f78c49592f82b16221d32fa5160516",
         "publication_status": "official_project_source",
         "licence": "CC BY-NC-ND 4.0",
         "media_type": "text/x-python",
         "hash_scope": "SHA-256 of 2c8_alphagenome_merged_splicing_scorer.py at the commit. The other two scripts at the same commit: 2c8_alphagenome_splicescorer.py 0c425043d31e02b1ca6fe0ce1120051352a0b2eae2571e70ce4f05f14114c151, 2c8_alphagenome_junctionscorer.py 9f260b27b06670505a903e8695ce020ac7432acd640a7041823d47c762bfbcec.",
         "limitations": [
             "All three scripts pass the 1-based VCF position to genome.Variant (splicescorer line 156, junctionscorer line 182, merged scorer line 225). The fixes are commits da0cf43e and 4a5c9163 (2026-10-23); the merged scorer was added in 102a107f (2026-10-30). Upstream issue #2 was closed on 2026-10-31.",
             "The scripts write scores only; the classification thresholds are applied downstream and are taken from the preprint's Methods D.",
         ],
     }})

# Configurations ------------------------------------------------------------------------------------------
VERSION = f"Google Cloud API (research access), version not printed; scripts at {REPO} commit {COMMIT[:8]}"
CONFIGS = [  # printed label, key, parameters, v1 configuration it reruns (or None)
    ("ALPHAGENOME COMPOSITE", "alphagenome-composite",
     "Composite splicing score following AlphaGenome's splicing_variant_scoring notebook: weighted sum of the maximum SPLICE_SITES (weight 1.0), SPLICE_SITE_USAGE (1.0) and SPLICE_JUNCTIONS (0.2) variant scores over a 1,048,576-bp interval centred on the variant; threshold >= 2.60",
     None),
    ("ALPHAGENOME SPLICE-SITE USAGE", "alphagenome-splice-site-usage",
     "SPLICE_SITE_USAGE variant score from the composite scoring run, evaluated on its own; threshold >= 0.93",
     None),
    ("ALPHAGENOME SPLICE-SITES", "alphagenome-splice-sites",
     "Custom predict_variant routine on the SPLICE_SITES output over a 1,048,576-bp interval: largest loss and gain in splice-site probability per track within ±500 bp of the variant on four strand-specific donor and acceptor tracks; maximum absolute difference across tracks; threshold >= 0.32",
     "splice-scorer"),
    ("ALPHAGENOME SPLICE-JUNCTIONS", "alphagenome-splice-junctions",
     "Custom predict_variant routine on the SPLICE_JUNCTIONS output over a 131,072-bp interval (±65,536 bp): per junction, the tissue track with the largest absolute log fold change ln(Alt + 1e-8) - ln(Ref + 1e-8); threshold >= 2.63",
     "junction-scorer"),
]
CFG = {}
for label, key, params, _ in CONFIGS:
    CFG[label] = f"{P}-config-{key}"
    name = label.title().replace("Alphagenome", "AlphaGenome") + " (Alavi 2026 v2)"
    add({"id": CFG[label], "kind": "configuration", "name": name,
         "description": f"AlphaGenome scored with the {label.split(' ', 1)[1].lower()} output and a grid-searched threshold, as configured in Alavi 2026 version 2.",
         "status": "needs_review", "facets": {**FACETS, "method_types": ["supervised_machine_learning"]},
         "source_ids": [SRC, CODE], "links": [{"relation": "configuration_of", "target_id": "catalog-model-alphagenome"}],
         "attributes": {"reported_name": label, "foundation_model_eligible": False, "version": VERSION, "parameters": params,
                        "access_reuse": "Google DeepMind Research Access program API",
                        "source_locator": "Methods D 'AlphaGenome'; Tables III and IV row label"}})

# Tables --------------------------------------------------------------------------------------------------
TOK = re.compile(r"\d+ \(\d+(?:\.\d+)? ?%\)|\d+(?:\.\d+)?%")
ROWS = ["SPLICEAI", "ALPHAGENOME COMPOSITE", "ALPHAGENOME SPLICE-SITE USAGE", "ALPHAGENOME SPLICE-SITES",
        "ALPHAGENOME SPLICE-JUNCTIONS", "BORZOI (32-BP)", "BORZOI (128-BP)", "NTV3 650M POST", "NTV3 650M PRE",
        "EVO2 40B (W/O HU. ID.)", "EVO2 40B (HU. ID.)", "GENOS 10B", "GENOS CLINVAR"]
V1_LABEL = {"EVO2 40B (W/O HU. ID.)": "EVO2 40B (W/O HU. IDENT.)", "EVO2 40B (HU. ID.)": "EVO2 40B (HU. IDENT.)",
            "GENOS CLINVAR": "GENOS 10B CLINVAR"}
COLS = ["Accuracy", "PPV", "Type I error", "Specificity", "Sensitivity", "Type II error", "Positive mutations", "Positive VUS"]
PAGE = {"III": 6, "IV": 9}


def rows_for(table, ncells):
    i = [k for k, l in enumerate(text) if l.strip() == table][0]
    out = [(k, TOK.findall(text[k])) for k in range(i, i + 70) if len(TOK.findall(text[k])) == ncells]
    assert len(out) == 13, (table, len(out))
    for n, ((k, _), label) in enumerate(zip(out, ROWS)):
        # a label is printed on the value line or split over the lines either side of it
        window = " ".join(text[k - 1:k + 2]).upper()
        for frag in label.replace("(", " ").replace(")", " ").split():
            assert frag in window, (table, label, frag)
    return [cells for _, cells in out]


TABLES = {"III": rows_for("TABLE III", 8), "IV": rows_for("TABLE IV", 6)}

# Every non-AlphaGenome cell must equal the stored v1 result.
v1_cells = {}
for r in STORE.values():
    if r["kind"] == "result" and r["id"].startswith(V1 + "-result-"):
        m = re.match(r"Table (III|IV), row '([^']+)', column '([^']+)'", r["attributes"]["source_locator"])
        v1_cells[(m.group(1), m.group(2), m.group(3))] = r["attributes"]["printed_value"]
unchanged = 0
for t, rows in TABLES.items():
    for label, cells in zip(ROWS, rows):
        if label.startswith("ALPHAGENOME"):
            continue
        for col, cell in zip(COLS, cells):
            assert v1_cells[(t, V1_LABEL.get(label, label), col)] == cell, (t, label, col, cell)
            unchanged += 1
assert unchanged == 126, unchanged

PROTS = {  # protocol key: table, columns
    "opa1-evaluation": ("III", list(range(6))),
    "opa1-extended-positive-calls": ("III", [6, 7]),
    "multigene": ("IV", list(range(6))),
}
DATA_FOR = {"opa1-evaluation": "opa1-evaluation-sets", "opa1-extended-positive-calls": "opa1-extended-corpus", "multigene": "multigene"}
N = {"III": {"benign": 79, "splicing": 49, "mutations": 306, "vus": 69}, "IV": {"benign": 107, "splicing": 76}}
COLMETRIC = {  # column: metric, direction, qualifier, unit_detail, denominator key
    "Accuracy": ("accuracy", "higher", None, None, None),
    "PPV": ("precision", "higher", None, None, None),
    "Type I error": ("false-positive-rate", "lower", "type I error: false positives as a share of the benign set", "Cell prints the count of false positives with the percentage of the benign set in brackets; numeric_value is the percentage", "benign"),
    "Specificity": ("specificity", "higher", None, "Cell prints the count of true negatives with the percentage in brackets; numeric_value is the percentage", "benign"),
    "Sensitivity": ("recall", "higher", None, "Cell prints the count of true positives with the percentage in brackets; numeric_value is the percentage", "splicing"),
    "Type II error": ("proportion", "lower", "type II error: false negatives as a share of the splicing set (false-negative rate)", "Cell prints the count of false negatives with the percentage of the splicing set in brackets; numeric_value is the percentage", "splicing"),
    "Positive mutations": ("proportion", "unknown", "share of 306 further OPA1 pathogenic substitutions called splice-altering", "Cell prints the count called positive with the percentage of 306 in brackets; numeric_value is the percentage", "mutations"),
    "Positive VUS": ("proportion", "unknown", "share of 69 OPA1 VUS substitutions called splice-altering", "Cell prints the count called positive with the percentage of 69 in brackets; numeric_value is the percentage", "vus"),
}
METHOD_NOTE = ("pdftotext -layout (poppler 26.08.0) on the pinned PDF; value rows found by token pattern, 13 rows per table "
               "and row-label fragments asserted; printed cell text kept exactly; bracketed percentages checked against "
               "counts, and accuracy and PPV checked against the row's counts; the 126 non-AlphaGenome cells asserted "
               "equal to the stored version 1 results.")
checks = []
RERUNS = []
for pkey, (t, cols) in PROTS.items():
    prot = f"{V1}-protocol-{pkey}"
    data = f"{V1}-data-{DATA_FOR[pkey]}"
    template = STORE[f"{V1}-eval-{pkey}-spliceai"]
    for label, key, _, rerun_of in CONFIGS:
        cells = TABLES[t][ROWS.index(label)]
        counts = {}
        ev = f"{P}-eval-{pkey}-{key}"
        name = STORE[data]["name"]
        add({"id": ev, "kind": "evaluation",
             "name": f"{label.title().replace('Alphagenome', 'AlphaGenome')} on {name} (Alavi 2026 v2)",
             "description": "Published comparison transcribed from the pinned source; not reproduced.",
             "status": "needs_review", "facets": FACETS, "source_ids": [SRC],
             "links": [{"relation": "system", "target_id": CFG[label]}, {"relation": "assessment", "target_id": prot},
                       {"relation": "data", "target_id": data}],
             "attributes": {"origin": "independent_paper", "protocol": prot, "version": "Primary source version 2 as retrieved " + TODAY,
                            "comparison": dict(template["attributes"]["comparison"]),
                            "source_locator": f"Table {t} row '{label}'",
                            "missing_metadata": {"comparison.budget": {"reason": "unreported"}}}})
        for ci in cols:
            col, cell = COLS[ci], cells[ci]
            metric, direction, qual, udet, den = COLMETRIC[col]
            m = re.fullmatch(r"(\d+) \((\d+(?:\.\d+)?) ?%\)", cell)
            if m:
                numeric = m.group(2)
                counts[col] = int(m.group(1))
                expect = 100 * int(m.group(1)) / N[t][den]
                assert abs(expect - float(numeric)) <= 0.051, (t, label, col, cell, expect)
            else:
                numeric = cell.rstrip("%")
            colkey = col.lower().replace(" ", "-")
            attrs = {"metric": metric, "metric_direction": direction, "unit": "percent", "printed_value": cell,
                     "source_locator": f"Table {t}, row '{label}', column '{col}' (PDF page {PAGE[t]} of 12)",
                     "review": {"method": ["pdf-text-parse"], "method_note": METHOD_NOTE, "reviewer": ["claude"],
                                "reviewer_note": EXTRACTOR_NOTE, "date": TODAY, "artifact_sha256": SHA, "retrieval_url": URL,
                                "note": "Extracted, not reviewed."},
                     "numeric_value": numeric, "missing_metadata": {"uncertainty": {"reason": "unreported"}}}
            if qual:
                attrs["metric_qualifier"] = qual
            if udet:
                attrs["unit_detail"] = udet
            links = [{"relation": "evaluation", "target_id": ev}]
            rid = f"{P}-result-{pkey}-{key}-{colkey}"
            if rerun_of:
                # No supersedes link: the release drops any record linking to a disputed one
                # (publicRecords in scripts/omics/schema.ts), and the v1 values must stay disputed.
                old = f"{V1}-result-{pkey}-alphagenome-{rerun_of}-{colkey}"
                assert STORE[old]["status"] == "disputed", old
                RERUNS.append((rid, old))
            add({"id": rid,
                 "kind": "result", "name": f"{label.title().replace('Alphagenome', 'AlphaGenome')} {col} (Alavi 2026 v2 Table {t})",
                 "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                 "status": "needs_review", "facets": {}, "source_ids": [SRC], "links": links, "attributes": attrs})
        if t in ("III", "IV") and "Specificity" in counts:
            tn, tp = counts["Specificity"], counts["Sensitivity"]
            acc = 100 * (tn + tp) / (N[t]["benign"] + N[t]["splicing"])
            ppv = 100 * tp / (tp + counts["Type I error"])
            checks.append((t, label, cells[0], f"{acc:.1f}%", cells[1], f"{ppv:.1f}%"))
for t, label, acc_p, acc_c, ppv_p, ppv_c in checks:
    assert float(acc_p.rstrip("%")) == float(acc_c.rstrip("%")), (t, label, acc_p, acc_c)
    assert float(ppv_p.rstrip("%")) == float(ppv_c.rstrip("%")), (t, label, ppv_p, ppv_c)

# Discrepancy review, revision 3 ---------------------------------------------------------------------------
REV2 = STORE["discrepancy-review-20261023-alavi-alphagenome-splicing-corrected"]
assert REV2["attributes"]["revision"] == 2
new_evals = sorted(r["id"] for r in records if r["kind"] == "evaluation")
new_results = sorted(r["id"] for r in records if r["kind"] == "result")
old_evals = sorted(l["target_id"] for l in REV2["links"] if "alphagenome" in l["target_id"])
assert len(old_evals) == 9 and len(new_results) == 56
add({"id": "discrepancy-review-20261101-alavi-alphagenome-splicing-rerun", "kind": "claim",
     "name": "Alavi 2026 AlphaGenome splicing discrepancy: corrected values added from the revised preprint",
     "description": "Version 2 of Alavi 2026 reruns AlphaGenome with the coordinate fix. Its 56 AlphaGenome results are added; 28 of them rerun a version 1 scorer and replace its disputed results.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC, CODE, V1_SRC],
     "links": [{"relation": "subject", "target_id": e} for e in old_evals + new_evals],
     "attributes": {
         "field": "discrepancy_review",
         "discrepancy_id": REV2["attributes"]["discrepancy_id"],
         "previous_ids": REV2["attributes"]["previous_ids"],
         "revision": 3,
         "value": "confirmed-error",
         "action": "corrected-records",
         "date": TODAY,
         "rationale": (
             "Version 2 of the preprint (posted 2026-10-31) prints AlphaGenome rows rerun with the 1-based position. "
             "It replaces version 1's three AlphaGenome rows with four: the composite score of AlphaGenome's splicing "
             "notebook, splice-site usage, splice-sites and splice-junctions. The splice-sites and splice-junctions rows "
             "rerun version 1's splice scorer and junction scorer scripts (the junction score now uses a natural-log fold "
             "change and both thresholds were re-tuned), so their 28 results replace the disputed version 1 results, which stay disputed and out of the release. "
             "The composite and splice-site usage rows are new configurations. Version 1's either-module row has no "
             "successor and stays disputed. The other models' cells are unchanged from version 1."),
         "investigation_url": "https://github.com/rewire-bio/rewire-benchmark-data/issues/213",
         "report_url": "https://github.com/marcel-2c8/splicing-model-eval-2026/issues/2",
         "reported_on": "2026-10-19",
         "upstream_response": (
             "The author committed the coordinate fix to both scripts on 2026-10-23 (da0cf43e, 4a5c9163), added a merged "
             "splicing scorer on 2026-10-30 (102a107f), posted the rerun as bioRxiv version 2 on 2026-10-31 and closed "
             "issue #2 the same day. The repository was renamed to splicing-model-eval-2026."),
         "resolved_by": [SRC] + new_results,
         "source_locator": (f"{SRC}: Tables III and IV, AlphaGenome rows; Methods D. {CODE}: commit {COMMIT}, "
                            "models/2_alphagenome. Upstream issue #2 state and closing date from the GitHub API."),
         "review": {"method": ["automated-source-review", "ai-assisted-source-review"], "reviewer": ["claude"],
                    "reviewer_note": EXTRACTOR_NOTE, "date": TODAY,
                    "method_note": "Read version 2 Tables III and IV and Methods D, the scripts at the pinned commit, and the issue and commit history through the GitHub API.",
                    "note": "Drafted, not reviewed."},
     }})

os.makedirs(OUT, exist_ok=True)
assert len(RERUNS) == 28
with open(os.path.join(OUT, "supersession.tsv"), "w") as f:
    f.write("version_2_result\tversion_1_result_rerun\n")
    for row in sorted(RERUNS):
        f.write("\t".join(row) + "\n")
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in sorted(records, key=lambda r: r["id"]):
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
counts = {}
for r in records:
    counts[r["kind"]] = counts.get(r["kind"], 0) + 1
print(json.dumps(dict(sorted(counts.items()))), "unchanged v1 cells:", unchanged, "count checks:", len(checks))
