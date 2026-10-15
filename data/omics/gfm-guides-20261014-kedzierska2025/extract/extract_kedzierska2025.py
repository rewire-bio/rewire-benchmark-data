"""Build batch.jsonl and claims.csv for Kedzierska et al. 2025 (Genome Biology 26:101).

Usage: python3 -I extract_kedzierska2025.py <additional-file-1.xlsx> <article.pdf> <batch-folder>

Reads the pinned Additional file 1 workbook with the stdlib OOXML reader (ooxml.py), asserts its
SHA-256, the sheet titles, the header rows and every row label, and transcribes every cell of the
whole-dataset score columns of sheets TableS6 and TableS7 (ASW, NMI, ARI, Batch integration, PCR)
and every cell of the rank sheets TableS3, TableS4 and TableS5. Two values printed in the article
text (page 5) are checked against the pdftotext output of the pinned PDF.
"""
import csv, hashlib, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ooxml import read_sheets  # noqa: E402

XLSX_SHA = "7adee1211206c4071981a402617c293048baeeeaf415b68ecd13383678003b5e"
PDF_SHA = "8efcc5fcb2e35b9a04b1ee9e03581e20fffeb5521a4a4c748a6f9b34f7d3c47f"
XLSX_URL = "https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-025-03574-x/MediaObjects/13059_2025_3574_MOESM1_ESM.xlsx"
PDF_URL = "https://genomebiology.biomedcentral.com/counter/pdf/10.1186/s13059-025-03574-x.pdf"
P = "gfm-guides-20261014-kedzierska2025"
SRC_ART = f"{P}-source-article"
SRC_XLSX = f"{P}-source-additional-file-1"
DATE = "2026-10-14"
FACETS = {"areas": ["single-cell"], "contexts": ["research"]}
REVIEWER_NOTE = ("Collector agent issue-129 for the 2026-10-14 genomic foundation model guide fixes; "
                 "extraction only, not a review. Pending an independent review-evidence pass.")

xlsx, pdf, out = sys.argv[1], sys.argv[2], sys.argv[3]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


assert sha(xlsx) == XLSX_SHA, "workbook hash mismatch"
assert sha(pdf) == PDF_SHA, "article PDF hash mismatch"
sheets = read_sheets(xlsx)
pdf_text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
pages = pdf_text.split("\f")

records, claims_rows = [], []


def rec(id_, kind, name, description, attributes, links=(), facets=None, source_ids=(SRC_ART,)):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": "needs_review",
         "facets": FACETS if facets is None else facets, "source_ids": list(source_ids),
         "links": [{"relation": a, "target_id": b} for a, b in links], "attributes": attributes}
    records.append(r)
    return r


def cell(sheet, ref):
    v = sheets[sheet].get(ref)
    return None if v is None else v[0]


def general(raw):
    """Excel 'General' display of a stored number: shortest decimal, no trailing '.0'."""
    f = float(raw)
    s = repr(f)
    if s.endswith(".0"):
        s = s[:-2]
    return s


# ---------------------------------------------------------------- sources
art_review = {"method": ["source-hash-verification"], "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE}
rec(SRC_ART, "source", "Zero-shot evaluation reveals limitations of single-cell foundation models (Kedzierska et al. 2025, Genome Biology 26:101)",
    "Publisher PDF of the article, retrieved and hashed for the 2026-10-14 genomic foundation model guide fixes (issue rewire-benchmark-data#129).",
    {"url": "https://doi.org/10.1186/s13059-025-03574-x", "artifact_url": PDF_URL,
     "version": "Version of record, Genome Biology 26:101, published 2025-04-18",
     "retrieved_at": "2026-10-14T12:01:07Z", "artifact_sha256": PDF_SHA, "doi": "10.1186/s13059-025-03574-x",
     "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/pdf",
     "venue": "Genome Biology", "year": 2025,
     "limitations": [
         "The headline comparisons (Fig. 1B average BIO score, Fig. 1E average batch score, Fig. 2 reconstruction) are figures without printed values; the per-dataset scores are in Additional file 1.",
         "All five evaluation datasets were chosen by the authors; Tabula Sapiens and Immune were in scGPT pretraining and part of Pancreas in Geneformer pretraining (Additional file 1, sheet TableS2).",
     ],
     "review": art_review}, source_ids=())
rec(SRC_XLSX, "source", "Kedzierska et al. 2025, Additional file 1 (Supplementary Tables S1-S7, xlsx)",
    "Supplementary workbook of the article, retrieved from the publisher (Springer static content) and hashed for the 2026-10-14 genomic foundation model guide fixes.",
    {"url": "https://doi.org/10.1186/s13059-025-03574-x", "artifact_url": XLSX_URL,
     "version": "Additional file 1 (13059_2025_3574_MOESM1_ESM.xlsx) of the version of record",
     "retrieved_at": "2026-10-14T12:01:36Z", "artifact_sha256": XLSX_SHA, "doi": "10.1186/s13059-025-03574-x",
     "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
     "limitations": [
         "Each model has two columns under one merged header: a single value and a value with a bracketed range. Neither column is labelled; the caption says scores were calculated on the whole dataset and in 10 repeats on 10% subsamples. Only the single-value (whole-dataset) columns are extracted.",
     ],
     "evidence_concerns": [
         {"source_id": SRC_XLSX,
          "message": "The workbook numbers its tables differently from the article's Additional file 1 caption. Workbook TableS1 = dataset overview (caption S7); TableS2 = sources and pretraining overlap (caption S3); TableS3 = ranks of median scores (caption S2); TableS4 = average ranking (caption S4); TableS5 = UMAP average ranking (caption S6); TableS6 = embedding scores (caption S1); TableS7 = UMAP scores (caption S5). The in-sheet titles match the workbook sheet names. Locators use the workbook sheet names.",
          "source_locator": "Workbook sheet names and cell A1/B1 titles; article page 10, 'Supplementary information', Additional file 1 caption",
          "artifact_sha256": XLSX_SHA, "review_date": DATE},
         {"source_id": SRC_XLSX,
          "message": "Which of the two columns per model holds the whole-dataset score and which the 10-repeat subsample summary is not labelled; the single-value column is read as the whole-dataset score. The central statistic and the range type of the bracketed column are not stated.",
          "source_locator": "Sheets TableS6 and TableS7, row 2 merged headers C2:D2 to Q2:R2; captions in cell A1",
          "artifact_sha256": XLSX_SHA, "review_date": DATE},
     ],
     "review": art_review}, source_ids=())

# ---------------------------------------------------------------- benchmark, protocols
BENCH = f"{P}-benchmark-zero-shot-scfm"
rec(BENCH, "benchmark", "Zero-shot cell embedding evaluation of single-cell foundation models (Kedzierska et al. 2025)",
    "Zero-shot cell embeddings from scGPT (four variants) and Geneformer compared with 2,000 highly variable genes, Harmony and scVI on five human scRNA-seq datasets, scored for cell-type separation and batch mixing with scIB metrics, plus a check of each model's pretraining reconstruction objective.",
    {"entity_level": "suite", "version": "Genome Biology 26:101 (2025)",
     "task": "Zero-shot cell embedding for cell-type clustering and batch integration",
     "scope_note": "Five datasets (Pancreas, PBMC 12k, PBMC 95k, Immune, Tabula Sapiens) plus a Pancreas (8k) row; foundation models used without training, baselines fitted on each dataset.",
     "source_locator": "Pages 3-5 'Results and discussion'; pages 7-10 'Methods'; Additional file 1"},
    source_ids=(SRC_ART, SRC_XLSX))

METRIC_IMPL = ("scib 1.0.4. ASW of cell-type labels rescaled to [0, 1]; NMI and ARI on Louvain clusters at the resolution "
               "with the highest NMI out of 20; batch integration = 1 minus absolute batch silhouette per cell type, averaged; "
               "PCR = change in variance explained by batch between the original data and the embedding (Methods, pages 9-10).")
PROTO_EMB = f"{P}-protocol-cell-embedding"
PROTO_UMAP = f"{P}-protocol-umap-embedding"
PROTO_REC = f"{P}-protocol-geneformer-reconstruction"
rec(PROTO_EMB, "protocol", "Kedzierska et al. 2025 cell embedding scoring, full embedding dimensions",
    "Cell embeddings (or the 2,000-HVG expression matrix) of each dataset scored for cell-type separation (ASW, NMI, ARI, AvgBIO) and batch mixing (batch integration ASW, PCR, average batch score) in the full embedding dimensions.",
    {"protocol": "Embed each whole dataset; compute scIB metrics against the dataset's cell-type and batch labels in the full embedding dimensions.",
     "version": "Genome Biology 26:101", "metric_implementation": METRIC_IMPL, "unit": "unitless",
     "limitations": ["One run on each whole dataset; spread across 10 repeats of 10% subsamples is printed separately and not extracted.",
                     "scVI and Harmony are trained on each target dataset; scGPT and Geneformer are not trained on it."],
     "source_locator": "Pages 9-10 'Biological preservation scores', 'Batch mixing scores'; Additional file 1 sheet TableS6"},
    links=[("part_of", BENCH)], source_ids=(SRC_ART, SRC_XLSX))
rec(PROTO_UMAP, "protocol", "Kedzierska et al. 2025 cell embedding scoring after UMAP projection",
    "As the full-dimension protocol, but the scIB metrics are computed on the UMAP projection of each embedding.",
    {"protocol": "Project each embedding with UMAP, then compute the same scIB metrics against cell-type and batch labels.",
     "version": "Genome Biology 26:101", "metric_implementation": METRIC_IMPL, "unit": "unitless",
     "limitations": ["UMAP parameters are not stated in the article."],
     "source_locator": "Page 4-5 'Results and discussion' (Additional file 1: Fig. S6A, Table S5); Additional file 1 sheet TableS7"},
    links=[("part_of", BENCH)], source_ids=(SRC_ART, SRC_XLSX))
rec(PROTO_REC, "protocol", "Kedzierska et al. 2025 Geneformer pretraining-objective reconstruction",
    "Geneformer run on all genes unmasked; Pearson correlation between the true input ranking and the predicted ranking, both scaled to 0-1, per cell.",
    {"protocol": "All genes unmasked as input; output sequence limited to the input length; Pearson correlation of true and predicted scaled rankings (Methods, page 10).",
     "version": "Genome Biology 26:101", "metric": "pearson-correlation", "metric_direction": "higher", "unit": "unitless",
     "source_locator": "Page 10 'Reconstructing gene expression'; page 5 'Results and discussion'"},
    links=[("part_of", BENCH)])

# ---------------------------------------------------------------- datasets
DATASETS = [  # label as printed in sheets TableS3-S7, slug, description
    ("Pancreas (16k)", "pancreas-16k", "Human pancreas cells combined from five studies (scIB benchmark file, Figshare 24539828): 16k cells, 14 labels, 6 batches."),
    ("Pancreas (8k)", "pancreas-8k", "Row labelled 'Pancreas (8k)' in the score sheets. The Methods say the authors also evaluated the Pancreas subset that does not overlap Geneformer pretraining (GEO GSE84133 excluded); the workbook does not state that this row is that subset."),
    ("PBMC (12k)", "pbmc-12k", "PBMCs from a healthy donor, from scvi-tools data.pbmc_dataset: 12k cells, 9 labels, 2 batches."),
    ("PBMC (95k)", "pbmc-95k", "PBMCs from a healthy donor (10x Genomics, Zheng et al. 2017): 95k cells, 10 labels, 1 batch. No batch metrics are reported for it."),
    ("Immune (330k)", "immune-330k", "Cross-tissue Immune Cell Atlas: immune cells from 16 tissues across 12 adult donors; 330k cells, 45 labels, 12 batches."),
    ("Tabula Sapiens (483k)", "tabula-sapiens-483k", "Tabula Sapiens (Figshare TabulaSapiens.h5ad.zip): cells from 24 tissues across 15 donors; 483k cells, 177 labels, 27 batches."),
]
DS = {}
for label, slug, desc in DATASETS:
    DS[label] = f"{P}-data-{slug}"
    rec(DS[label], "dataset_subset", f"{label} (Kedzierska et al. 2025)", desc,
        {"source_dataset_label": label, "split": "No split; each whole dataset is embedded and scored",
         "source_locator": "Additional file 1 sheet TableS1 (dataset overview) and TableS2 (sources); page 8-9 'Datasets'; page 11 'Data availability'",
         "missing_metadata": {"version": {"reason": "unreported"}}},
        links=[("used_in", PROTO_EMB), ("used_in", PROTO_UMAP)], source_ids=(SRC_ART, SRC_XLSX))
DS_ALL = f"{P}-data-evaluated-datasets"
rec(DS_ALL, "dataset_subset", "Evaluated datasets, aggregated (Kedzierska et al. 2025)",
    "The evaluated datasets taken together, for ranks of median or mean scores across datasets and the text summary of Geneformer reconstruction across datasets. Whether the Pancreas (8k) row enters the Table S3 medians is not stated.",
    {"split": "No split", "subset_scope": "Aggregate over the evaluated datasets as stated by the source",
     "source_locator": "Additional file 1 sheets TableS3, TableS4 column 'Average ranking', TableS5 column 'Average ranking'; page 5 'Results and discussion'",
     "missing_metadata": {"version": {"reason": "inapplicable", "note": "Aggregate of several datasets"}}},
    links=[("used_in", PROTO_EMB), ("used_in", PROTO_UMAP), ("used_in", PROTO_REC)], source_ids=(SRC_ART, SRC_XLSX))

# ---------------------------------------------------------------- methods and configurations
HVG_METHOD = f"{P}-method-hvg-selection"
rec(HVG_METHOD, "method", "Highly variable gene selection",
    "Uses the log-normalised expression of the most highly variable genes directly as the cell representation.",
    {"reported_name": "HVG", "entity_level": "method", "source_locator": "Page 8 'Models and baselines'",
     "missing_metadata": {"version": {"reason": "unreported"}}},
    facets={**FACETS, "method_types": ["conventional_pipeline"]})

GF_CHECKPOINT = "Geneformer code at commit 5d0082c (2023-11-21); 6 Transformer layers, 4 attention heads, pretrained on 27.4M human single-cell transcriptomes (Methods); cell embedding = average of gene embeddings"
CONFIGS = [
    # workbook label, slug, display, family target, method_types, attributes
    ("HVG", "hvg", "2,000 highly variable genes", HVG_METHOD, ["conventional_pipeline"],
     {"reported_name": "HVG", "foundation_model_eligible": False, "training_setting": "No training; 2,000 HVG of the log-normalised data",
      "representation": "Log-normalised expression of 2,000 highly variable genes", "missing_metadata": {"version": {"reason": "unreported", "note": "HVG selection flavour and software version not stated"}}}),
    ("Harmony", "harmony", "Harmony", "lit-cells-networks-20261011-scmbench-method-harmony", ["specialist"],
     {"reported_name": "Harmony", "foundation_model_eligible": False, "training_setting": "Fitted on each target dataset using its batch labels",
      "representation": "Harmony-adjusted embedding", "missing_metadata": {"version": {"reason": "unreported"}, "hyperparameters": {"reason": "unreported"}}}),
    ("scVI", "scvi", "scVI", "catalog-model-scvi", ["specialist"],
     {"reported_name": "scVI", "foundation_model_eligible": False, "training_setting": "Trained on each target dataset using its batch labels",
      "representation": "scVI latent embedding", "missing_metadata": {"version": {"reason": "unreported"}, "hyperparameters": {"reason": "unreported"}}}),
    ("scGPT random", "scgpt-random", "scGPT, randomly initialised", "catalog-model-scgpt", ["foundation_model"],
     {"reported_name": "scGPT random", "foundation_model_eligible": True, "training_setting": "No pretraining (random initialisation); zero-shot",
      "representation": "scGPT cell embedding", "version": "scGPT code 0.1.6 (2023-09-14)",
      "checkpoint": "Randomly initialised scGPT (no pretrained weights)", "access_reuse": "Evaluation code: github.com/microsoft/zero-shot-scfoundation (MIT), archived on Zenodo; not pinned to a commit in the article"}),
    ("scGPT kidney", "scgpt-kidney", "scGPT kidney", "catalog-model-scgpt", ["foundation_model"],
     {"reported_name": "scGPT kidney", "foundation_model_eligible": True, "training_setting": "Zero-shot; pretrained weights, no fine-tuning",
      "representation": "scGPT cell embedding", "version": "scGPT code 0.1.6 (2023-09-14)",
      "checkpoint": "scGPT pretrained on 814,000 kidney cells", "access_reuse": "Evaluation code: github.com/microsoft/zero-shot-scfoundation (MIT), archived on Zenodo; not pinned to a commit in the article"}),
    ("scGPT blood", "scgpt-blood", "scGPT blood", "catalog-model-scgpt", ["foundation_model"],
     {"reported_name": "scGPT blood", "foundation_model_eligible": True, "training_setting": "Zero-shot; pretrained weights, no fine-tuning",
      "representation": "scGPT cell embedding", "version": "scGPT code 0.1.6 (2023-09-14)",
      "checkpoint": "scGPT pretrained on 10.3 million blood and bone marrow cells", "access_reuse": "Evaluation code: github.com/microsoft/zero-shot-scfoundation (MIT), archived on Zenodo; not pinned to a commit in the article"}),
    ("scGPT human", "scgpt-human", "scGPT human", "catalog-model-scgpt", ["foundation_model"],
     {"reported_name": "scGPT human", "foundation_model_eligible": True, "training_setting": "Zero-shot; pretrained weights, no fine-tuning",
      "representation": "scGPT cell embedding", "version": "scGPT code 0.1.6 (2023-09-14)",
      "checkpoint": "scGPT pretrained on 33 million non-cancerous human cells (whole-human)", "access_reuse": "Evaluation code: github.com/microsoft/zero-shot-scfoundation (MIT), archived on Zenodo; not pinned to a commit in the article"}),
    ("Geneformer", "geneformer", "Geneformer", "catalog-model-geneformer", ["foundation_model"],
     {"reported_name": "Geneformer", "foundation_model_eligible": True, "training_setting": "Zero-shot; pretrained weights, no fine-tuning",
      "representation": "Mean of gene embeddings per cell", "version": "Geneformer commit 5d0082c (2023-11-21)",
      "checkpoint": GF_CHECKPOINT, "access_reuse": "Evaluation code: github.com/microsoft/zero-shot-scfoundation (MIT), archived on Zenodo; not pinned to a commit in the article"}),
]
CFG = {}
for label, slug, display, target, mtypes, attrs in CONFIGS:
    CFG[label] = f"{P}-config-{slug}"
    a = dict(attrs)
    a["source_locator"] = "Pages 7-8 'Models and baselines'; page 11 'Code availability'"
    rec(CFG[label], "configuration", f"{display} (Kedzierska et al. 2025)",
        f"{display} cell representation as evaluated zero-shot by Kedzierska et al. 2025." if a["foundation_model_eligible"]
        else f"{display} baseline as run by Kedzierska et al. 2025.",
        a, links=[("configuration_of", target)], facets={**FACETS, "method_types": mtypes})

# ---------------------------------------------------------------- evaluations
ADAPT = "scGPT and Geneformer zero-shot from pretrained weights (scGPT random: no pretraining); scVI and Harmony fitted on each dataset with batch labels; HVG computed from each dataset"
INPUTS = "Each dataset's expression matrix with cell-type and batch labels; 2,000 HVG standard across experiments"
EVALS = {}
EVAL_NAMES = {}


def evaluation(cfg_label, proto, data_id, data_label, aggregation, locator):
    key = (cfg_label, proto, data_id)
    if key in EVALS:
        return EVALS[key]
    pslug = {PROTO_EMB: "emb", PROTO_UMAP: "umap", PROTO_REC: "recon"}[proto]
    dslug = data_id.removeprefix(f"{P}-data-")
    eid = f"{P}-eval-{pslug}-{dslug}-{CFG[cfg_label].removeprefix(f'{P}-config-')}"
    pname = {PROTO_EMB: "cell embedding", PROTO_UMAP: "UMAP-projected embedding", PROTO_REC: "pretraining reconstruction"}[proto]
    EVAL_NAMES[eid] = f"{cfg_label} {pname} on {data_label} (Kedzierska et al. 2025)"
    rec(eid, "evaluation", EVAL_NAMES[eid],
        "Published comparison transcribed from the pinned source; not reproduced.",
        {"origin": "independent_paper", "protocol": proto, "version": "Genome Biology 26:101 and Additional file 1 as retrieved 2026-10-14",
         "comparison": {"protocol_id": proto, "dataset_version": None,
                        "split": "No split; each whole dataset embedded and scored",
                        "population": None, "inputs": INPUTS, "adaptation": ADAPT,
                        "metric_implementation": METRIC_IMPL if proto != PROTO_REC else "Pearson correlation of true and predicted scaled gene rankings (Methods page 10)",
                        "aggregation": aggregation, "budget": None},
         "source_locator": locator,
         "missing_metadata": {"comparison.dataset_version": {"reason": "unreported"},
                              "comparison.population": {"reason": "unreported"},
                              "comparison.budget": {"reason": "unreported"}}},
        links=[("system", CFG[cfg_label]), ("assessment", proto), ("data", data_id)],
        source_ids=(SRC_ART, SRC_XLSX) if proto != PROTO_REC else (SRC_ART,))
    EVALS[key] = eid
    return eid


RESULT_IDS = set()
AGG_ALL = "Across the evaluated datasets; each result states its ranking basis (Table S3: median score per metric; Tables S4 and S5: average ranking from mean scores)"


def result(eval_id, slug, metric, direction, printed, numeric, locator, qualifier, method_note, src_ids, artifact_sha, url, extra=None, unit_detail=None):
    rid = f"{eval_id.replace('-eval-', '-result-')}-{slug}"
    assert rid not in RESULT_IDS, rid
    RESULT_IDS.add(rid)
    a = {"metric": metric, "metric_direction": direction, "unit": "unitless", "printed_value": printed, "numeric_value": numeric,
         "metric_qualifier": qualifier, "source_locator": locator,
         "review": {"method": ["deterministic-table-parse"] if artifact_sha == XLSX_SHA else ["pdf-text-parse", "transcription"],
                    "method_note": method_note, "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE,
                    "artifact_sha256": artifact_sha, "retrieval_url": url,
                    "note": "Extracted, not reviewed. The review-evidence pass must re-check this value against the pinned artifact."},
         "missing_metadata": {"uncertainty": {"reason": "unreported"}}}
    if unit_detail:
        a["unit_detail"] = unit_detail
    if extra:
        a.update(extra)
    r = rec(rid, "result", f"{EVAL_NAMES[eval_id]}: {slug}", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
            a, links=[("evaluation", eval_id)], facets={}, source_ids=src_ids)
    claims_rows.append([rid, src_ids[-1], locator, printed, "result"])
    return r


def col_letter(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


# ---- score sheets TableS6 (full dimensions) and TableS7 (UMAP)
MODEL_COLS = [("HVG", "C"), ("Harmony", "E"), ("scVI", "G"), ("scGPT random", "I"), ("scGPT kidney", "K"),
              ("scGPT blood", "M"), ("scGPT human", "O"), ("Geneformer", "Q")]
METRIC_BLOCKS = [  # printed label, first row, last row, concept, extracted?
    ("ASW", 3, 8, "scib-asw-label", True), ("NMI", 9, 14, "normalized-mutual-information", True),
    ("ARI", 15, 20, "adjusted-rand-index", True), ("AvgBIO", 21, 26, None, False),
    ("Batch integration", 27, 31, "scib-asw-batch", True), ("PCR", 32, 36, "scib-pcr-batch", True),
    ("Average batch", 37, 41, None, False)]
BIO_ROWS = ["Pancreas (16k)", "Pancreas (8k)", "PBMC (12k)", "PBMC (95k)", "Immune (330k)", "Tabula Sapiens (483k)"]
BATCH_ROWS = ["Pancreas (16k)", "Pancreas (8k)", "PBMC (12k)", "Immune (330k)", "Tabula Sapiens (483k)"]
QUAL = {"scib-asw-label": "cell-type ASW", "normalized-mutual-information": "Louvain clusters at best-NMI resolution versus cell-type labels",
        "adjusted-rand-index": "Louvain clusters at best-NMI resolution versus cell-type labels",
        "scib-asw-batch": "batch integration score (batch ASW per cell type)", "scib-pcr-batch": "principal component regression on batch"}
SLUG = {"scib-asw-label": "asw-label", "normalized-mutual-information": "nmi", "adjusted-rand-index": "ari",
        "scib-asw-batch": "batch-integration", "scib-pcr-batch": "pcr"}
skipped = 0
for sheet, proto, title_start, space in [("TableS6", PROTO_EMB, "Table S6 Scores for cell embeddings generated by the models.", "full embedding dimensions"),
                                          ("TableS7", PROTO_UMAP, "Table S7 Scores for UMAP of the cell embeddings generated by the models.", "UMAP projection of the embedding")]:
    assert cell(sheet, "A1").startswith(title_start), (sheet, cell(sheet, "A1"))
    assert cell(sheet, "B2") == "Dataset"
    for label, col in MODEL_COLS:
        assert cell(sheet, f"{col}2") == label, (sheet, col, cell(sheet, f"{col}2"))
    for mlabel, r0, r1, concept, take in METRIC_BLOCKS:
        assert cell(sheet, f"A{r0}") == mlabel, (sheet, r0, cell(sheet, f"A{r0}"))
        rows = BIO_ROWS if r1 - r0 == 5 else BATCH_ROWS
        for i, ds in enumerate(rows):
            r = r0 + i
            assert cell(sheet, f"B{r}") == ds, (sheet, r, cell(sheet, f"B{r}"))
            for label, col in MODEL_COLS:
                raw = cell(sheet, f"{col}{r}")
                rng = cell(sheet, f"{chr(ord(col) + 1)}{r}")
                assert re.fullmatch(r"-?\d+(\.\d+)?", raw), (sheet, col, r, raw)
                assert re.fullmatch(r"-?\d\.\d{3} \(-?\d\.\d{3} - -?\d\.\d{3}\)", rng), (sheet, col, r, rng)
                if not take:
                    skipped += 1
                    continue
                printed = general(raw)
                loc = (f"Additional file 1, sheet '{sheet}' cell {col}{r}, metric block '{mlabel}', row '{ds}', column '{label}' "
                       f"(single-value column)")
                ev = evaluation(label, proto, DS[ds], ds, "Single dataset; whole-dataset score",
                                f"Additional file 1, sheet '{sheet}', column '{label}', row '{ds}'")
                result(ev, SLUG[concept], concept, "higher", printed, printed, loc,
                       f"{QUAL[concept]}; whole dataset; {space}",
                       f"Read sheet '{sheet}' of the pinned workbook with a stdlib OOXML reader (extract/ooxml.py); sheet title, model headers C2:Q2, metric labels in column A and dataset labels in column B asserted; printed_value is the Excel General display of the stored number.",
                       [SRC_XLSX], XLSX_SHA, XLSX_URL,
                       extra={"raw_xml_value": raw, "workbook_number_format": "General"})

# ---- rank sheets
RANK_MODELS_S3 = {"scVI": 3, "Harmony": 4, "HVG": 5, "scGPT\nblood": 6, "scGPT\nhuman": 7, "scGPT\nkidney": 8, "Geneformer": 9, "scGPT\nrandom": 10}
s3_cols = [("B", "Average BIO"), ("C", "ASW"), ("D", "ARI"), ("E", "NMI"), ("F", "Average batch"), ("G", "Batch integration"), ("H", "PCR")]
assert cell("TableS3", "B1").startswith("Table S3 Rankings of median scores across datasets.")
assert cell("TableS3", "A2") == "Model"
for col, lab in s3_cols:
    assert cell("TableS3", f"{col}2") == lab, (col, cell("TableS3", f"{col}2"))
for mlab, r in RANK_MODELS_S3.items():
    assert cell("TableS3", f"A{r}") == mlab, (r, cell("TableS3", f"A{r}"))
    cfg_label = mlab.replace("\n", " ")
    for col, lab in s3_cols:
        raw = cell("TableS3", f"{col}{r}")
        printed = general(raw)
        loc = f"Additional file 1, sheet 'TableS3' cell {col}{r}, row '{cfg_label}', column '{lab}'"
        ev = evaluation(cfg_label, PROTO_EMB, DS_ALL, "evaluated datasets", AGG_ALL,
                        "Additional file 1, sheets 'TableS3' and 'TableS4' (column 'Average ranking')")
        result(ev, "rank-median-" + re.sub(r"[^a-z]+", "-", lab.lower()).strip("-"), "rank", "lower", printed, printed, loc,
               f"rank of the median {lab} score across datasets among the eight representations (1 = best); full embedding dimensions",
               "Read sheet 'TableS3' of the pinned workbook with a stdlib OOXML reader; caption, header row A2:H2 and model labels A3:A10 asserted; printed_value is the Excel General display of the stored number.",
               [SRC_XLSX], XLSX_SHA, XLSX_URL, extra={"raw_xml_value": raw, "workbook_number_format": "General"},
               unit_detail="ordinal position among eight representations")

for sheet, proto, title_start, space in [("TableS4", PROTO_EMB, "Table S4 Average ranking for the evaluated models.", "full embedding dimensions"),
                                          ("TableS5", PROTO_UMAP, "Table S5 Average ranking for the UMAP embeddings", "UMAP projection of the embedding")]:
    assert cell(sheet, "B1").startswith(title_start), (sheet, cell(sheet, "B1"))
    heads = [("B", "Average ranking")] + [(c, d) for c, d in zip("CDEFG", BATCH_ROWS[:1] + ["PBMC (12k)", "PBMC (95k)", "Immune (330k)", "Tabula Sapiens (483k)"])]
    assert cell(sheet, "A2") == "Model"
    for col, lab in heads:
        assert cell(sheet, f"{col}2") == lab, (sheet, col, cell(sheet, f"{col}2"))
    for r in range(3, 11):
        mlab = cell(sheet, f"A{r}")
        assert mlab in CFG, (sheet, r, mlab)
        for col, lab in heads:
            raw = cell(sheet, f"{col}{r}")
            printed = general(raw)
            loc = f"Additional file 1, sheet '{sheet}' cell {col}{r}, row '{mlab}', column '{lab}'"
            if lab == "Average ranking":
                ev = evaluation(mlab, proto, DS_ALL, "evaluated datasets", AGG_ALL,
                                f"Additional file 1, sheet '{sheet}', column 'Average ranking'")
                q = f"overall average ranking across datasets, based on mean biological-conservation and batch-mixing scores (1 = best); {space}"
                slug = "rank-average-overall"
            else:
                ev = evaluation(mlab, proto, DS[lab], lab, "Single dataset; whole-dataset score",
                                f"Additional file 1, sheet '{'TableS6' if proto == PROTO_EMB else 'TableS7'}', column '{mlab}', row '{lab}'")
                q = f"rank among the eight representations by mean biological-conservation and batch-mixing scores on this dataset (1 = best); {space}"
                slug = "rank-average"
            result(ev, slug, "rank", "lower", printed, printed, loc, q,
                   f"Read sheet '{sheet}' of the pinned workbook with a stdlib OOXML reader; caption, header row A2:G2 and model labels A3:A10 asserted; printed_value is the Excel General display of the stored number.",
                   [SRC_XLSX], XLSX_SHA, XLSX_URL, extra={"raw_xml_value": raw, "workbook_number_format": "General"},
                   unit_detail="ordinal position among eight representations; ties share a rank")

# ---- article text, page 5
p5 = pages[4]
assert "Page 5 of 13" in p5
sentence = "with median and best correlations of 0.56 and 0.95, respectively, across datasets"
flat = re.sub(r"\s+", " ", p5)
assert "Geneformer’s gene ranking exhibits modest correlations with the actual true rank- ings, " + sentence in flat, "page 5 sentence not found"
ev = evaluation("Geneformer", PROTO_REC, DS_ALL, "evaluated datasets", "Median and best value across datasets", "Page 5, paragraph before Fig. 2 caption")
for slug, printed, q in [("pearson-median", "0.56", "Geneformer input versus predicted gene ranking, all genes unmasked; median across datasets"),
                         ("pearson-best", "0.95", "Geneformer input versus predicted gene ranking, all genes unmasked; best value across datasets")]:
    result(ev, slug, "pearson-correlation", "higher", printed, printed,
           "Page 5, 'Results and discussion', paragraph beginning 'Notably, scGPT without embeddings', sentence 2 ('median and best correlations of 0.56 and 0.95, respectively, across datasets')",
           q, "Hand transcription from the article text; the script asserts the sentence in the pdftotext -layout output of page 5 of the pinned PDF.",
           [SRC_ART], PDF_SHA, PDF_URL)

# ---------------------------------------------------------------- claims: pretraining overlap (TableS2)
assert cell("TableS2", "G2") == "Geneformer" and cell("TableS2", "H2") == "scGPT"
overlap = [("Pancreas (16k)", "G6", "E6", "yes", "Geneformer", "The Pancreas study GSE84133 (Baron et al.) was included in Geneformer pretraining; the other five Pancreas studies were not."),
           ("Tabula Sapiens (483k)", "H11", "A11", "yes", "scGPT", "Tabula Sapiens was included in the scGPT pretraining data (CELLxGENE May 2023 census)."),
           ("Immune (330k)", "H12", "A12", "yes", "scGPT", "The Immune (Cross-tissue Immune Cell Atlas) dataset was included in the scGPT pretraining data (CELLxGENE May 2023 census).")]
for ds, ref, labref, expect, model, value in overlap:
    assert cell("TableS2", ref) == expect, (ref, cell("TableS2", ref))
    cid = f"{DS[ds]}-claim-{model.lower()}-pretraining-overlap".replace("-data-", "-")
    loc = f"Additional file 1, sheet 'TableS2' cell {ref} (column '{model}', row '{cell('TableS2', labref).strip()}'); page 9 'Datasets'"
    rec(cid, "claim", f"{ds}: overlap with {model} pretraining (Kedzierska et al. 2025)", value,
        {"field": f"pretraining_overlap:{model}", "value": value, "source_locator": loc,
         "review": {"method": ["deterministic-table-parse"], "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "date": DATE,
                    "artifact_sha256": XLSX_SHA, "retrieval_url": XLSX_URL, "note": "Extracted, not reviewed."}},
        links=[("subject", DS[ds])], facets={}, source_ids=(SRC_ART, SRC_XLSX))
    claims_rows.append([cid, SRC_XLSX, loc, cell("TableS2", ref), "claim"])

# ---------------------------------------------------------------- write
records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids))
with open(os.path.join(out, "batch.jsonl"), "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claims_rows.sort()
with open(os.path.join(out, "claims.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
from collections import Counter
counts = Counter(r["kind"] for r in records)
print(dict(sorted(counts.items())), "skipped AvgBIO/Average batch cells:", skipped)
assert counts["result"] == 224 * 2 + 56 + 48 * 2 + 2, counts["result"]
