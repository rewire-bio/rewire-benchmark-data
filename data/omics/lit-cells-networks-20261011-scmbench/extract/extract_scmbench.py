"""SCMBench (Wang et al., Nature Communications 2026, doi:10.1038/s41467-026-72570-x): integration accuracy overall scores per dataset from
Supplementary Data 2 (MOESM4), sheets 'paired_inte_overall' and 'unpaired_inte_overall', read from the sheet XML.

Usage: python3 -I extract_scmbench.py <MOESM4.xlsx> <MOESM3.xlsx> <PMC13342640.xml> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, finalise
from xlsx_cells import sheet_cells

sd2, sd1, art, folder = sys.argv[1:5]
H = {sd2: "77582bcc906fed343de12c2b2ed7443e94f5d11bf93b7f3862a37c5099015443", sd1: "7287a457b1e856742a90043e96dc57b667210b28a8228d4d9a6de5d7156ecfb9",
     art: "7aa2dbf1fc26bd602bf26e52c1061f91358a1c6cb389f57edc0ebfb0edc64f57"}
for p, h in H.items():
    assert sha256(p) == h, p
ESM = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-026-72570-x/MediaObjects/"
RET = "2026-10-11T21:38:51Z"
B = "lit-cells-networks-20261011-scmbench"
b = Batch(folder, B, areas=["single-cell"])
COMMON = {"doi": "10.1038/s41467-026-72570-x", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "retrieved_at": RET, "year": 2026, "venue": "Nature Communications"}
ART = b.source(B + "-source-article", "SCMBench: benchmarking domain-specific and foundation models for single-cell multi-omics data integration", dict(COMMON, **{
    "url": "https://doi.org/10.1038/s41467-026-72570-x", "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13342640/fullTextXML",
    "version": "Published article, Nature Communications 2026 (PMC13342640.1)", "artifact_sha256": H[art], "media_type": "application/xml",
    "limitations": ["The authors developed the FM-scVI adapter strategy; all other methods are third-party."]}))
SD2 = b.source(B + "-source-sd2", "SCMBench Supplementary Data 2 (integration results)", dict(COMMON, **{
    "url": ESM + "41467_2026_72570_MOESM4_ESM.xlsx", "version": "Supplementary Data 2 (MOESM4) of the published article", "artifact_sha256": H[sd2],
    "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    # Reviewer cn-2: S1 replaces the first concern's message; S2 adds the third concern (verbatim).
    "evidence_concerns": [{"source_id": B + "-source-sd2", "message": "Sheet 'unpaired_inte_overall' has no header for column H. Each H cell is the formula =AVERAGE(Bn:Gn), the mean of the dataset cells with values. Rows with a blank Yao cell (bindSC, scMoMaT, scGPT_zero, Pamona, scFoundation, Geneformer) average five datasets and the other rows six, so column H values are not comparable across all rows.",
                           "source_locator": "Supplementary Data 2, sheet 'unpaired_inte_overall', row 1 and column H", "artifact_sha256": H[sd2], "review_date": "2026-10-12"},
                          {"source_id": B + "-source-sd2", "message": "'FM-scVI' is a different foundation model per dataset ('the best-performing foundation model combined with scVI, which varies across datasets', Fig. 2 legend), so its rows do not describe one fixed configuration.",
                           "source_locator": "Article Fig. 2 legend; Supplementary Data 2 'FM-scVI' rows", "artifact_sha256": H[art], "review_date": "2026-10-11"},
                          {"source_id": B + "-source-sd2", "message": "In sheet 'paired_inte_overall' the scGPT row is scored on 10x-Multiome-Pbmc10k only; its Overall cell G20 (=AVERAGE(B20:F20)) is that single value, not a five-dataset mean, so it is not comparable with the other Overall values.",
                           "source_locator": "Supplementary Data 2, sheet 'paired_inte_overall', cell G20", "artifact_sha256": "77582bcc906fed343de12c2b2ed7443e94f5d11bf93b7f3862a37c5099015443", "review_date": "2026-10-12"}]}))
SD1 = b.source(B + "-source-sd1", "SCMBench Supplementary Data 1 (methods and datasets)", dict(COMMON, **{
    "url": ESM + "41467_2026_72570_MOESM3_ESM.xlsx", "version": "Supplementary Data 1 (MOESM3) of the published article", "artifact_sha256": H[sd1],
    "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}))
SIDS = [ART, SD2]

BENCH = b.entity("benchmark", b.rid("benchmark", "scmbench"), "SCMBench",
    "Benchmark of 19 domain-specific models and four single-cell foundation models (scGPT, UCE, Geneformer, scFoundation) for paired and unpaired single-cell multi-omics (RNA and ATAC) integration, scored on integration accuracy, biomarker detection, trajectory conservation and batch correction.",
    [ART, SD1], {"entity_level": "suite", "version": "Nature Communications 2026", "task": "Single-cell multi-omics data integration",
                 "scope_note": "Foundation models receive scATAC-seq as MAESTRO gene activity scores, a non-standard input for RNA-pretrained models (Methods).",
                 "source_locator": "Abstract; Fig. 1; Methods; Supplementary Data 1-2"})

# Method rows in Supplementary Data 1, sheet 'Method' (reference URLs), and how they are labelled in Supplementary Data 2.
existing = {"scVI": "catalog-model-scvi", "UCE": "cell-type-20261009-model-uce", "scGPT": "catalog-model-scgpt", "scGPT_zero": "catalog-model-scgpt",
            "scFoundation": "catalog-model-scfoundation", "Geneformer": "catalog-model-geneformer"}
FMS = {"UCE", "scGPT", "scGPT_zero", "scFoundation", "Geneformer"}
sd1cells = sheet_cells(sd1, "Method")
methods_sd1 = {}
for r in range(2, 61):
    v = sd1cells.get(f"A{r}")
    if v:
        methods_sd1[v[0].strip()] = (r, sd1cells.get(f"H{r}", ("",))[0], sd1cells.get(f"G{r}", ("",))[0])
assert len(methods_sd1) == 23, sorted(methods_sd1)
ALIAS = {"MOFA": "MoFA"}
fam, cfgs = {}, {}


def system(label):
    if label in cfgs:
        return cfgs[label]
    base = ALIAS.get(label, label)
    if label == "FM-scVI":
        cfgs[label] = b.entity("configuration", b.rid("config", "fm-scvi"), "FM-scVI (SCMBench adapter)",
            "SCMBench authors' adapter: embeddings from a foundation model fed to scVI; the foundation model is the best one per dataset (scGPT on PBMC-10k, adapted UCE on Ma-2020, per the Fig. 2 legend).",
            [ART, SD2], {"reported_name": "FM-scVI", "foundation_model_eligible": True, "training_setting": "Foundation model embeddings with an scVI integration module",
                         "source_locator": "Fig. 2 legend; Results on FM adaptation", "limitations": ["The underlying foundation model differs by dataset."],
                         "missing_metadata": {"version": {"reason": "unreported"}}}, method_types=["foundation_model"],
            links=[{"relation": "uses_model", "target_id": "catalog-model-scgpt"}, {"relation": "uses_model", "target_id": "cell-type-20261009-model-uce"}])
        return cfgs[label]
    if label in existing:
        target = existing[label]
    else:
        row, ref, year = methods_sd1[base]
        if base not in fam:
            fam[base] = b.entity("method", b.rid("method", base), base, f"Single-cell multi-omics integration method ({year}) evaluated in SCMBench." + (f" Reference: {ref.strip()}" if ref else ""),
                                 [SD1], {"reported_name": base, "entity_level": "method", "source_locator": f"Supplementary Data 1, sheet 'Method', row {row}",
                                         "missing_metadata": {"version": {"reason": "unreported"}}}, method_types=["specialist"])
        target = fam[base]
    mode = {"scGPT": "scGPT as printed in the paired results (only PBMC-10k scored); fine-tuned or zero-shot mode not stated in the sheet",
            "scGPT_zero": "scGPT zero-shot embeddings per omic"}.get(label, "default or tuned hyperparameters per the SCMBench setup")
    cfgs[label] = b.entity("configuration", b.rid("config", label), f"{label} (SCMBench)", f"{label} as run in SCMBench: {mode}.", [ART, SD2], {
        "reported_name": label, "foundation_model_eligible": label in FMS, "hyperparameters": "Defaults for R methods and methods without explicit hyperparameters; tuned otherwise (Methods 'Hyperparameter tuning')",
        "source_locator": "Supplementary Data 2 method rows; Methods 'Benchmarking setup'", "missing_metadata": {"version": {"reason": "unreported"}}},
        method_types=["foundation_model"] if label in FMS else ["specialist"], links=[{"relation": "configuration_of", "target_id": target}])
    return cfgs[label]


DS = {"10x-Multiome-Pbmc10k": "10x Multiome PBMC-10k (human, paired)", "Chen-2019": "SHARE-seq mouse cortex Chen-2019 (paired)",
      "Ma-2020-batch-53": "SHARE-seq mouse skin Ma-2020, batch 53 (paired, the Methods sample each batch to 2,500 cells for the batch-effect experiments and do not say whether this sheet uses the sampled batches)", "Ma-2020-batch-54": "SHARE-seq mouse skin Ma-2020, batch 54 (paired, the Methods sample each batch to 2,500 cells for the batch-effect experiments and do not say whether this sheet uses the sampled batches)",
      "Ma-2020-batch-55": "SHARE-seq mouse skin Ma-2020, batch 55 (paired, the Methods sample each batch to 2,500 cells for the batch-effect experiments and do not say whether this sheet uses the sampled batches)", "Yao": "Yao-2021 mouse MOp scRNA-seq and snATAC-seq (unpaired)"}
for i in range(1, 6):
    DS[f"Muto-2021-batch-{i}"] = f"Muto-2021 human kidney snRNA-seq and snATAC-seq, batch {i} (unpaired, the Methods sample each batch to 2,500 cells for the batch-effect experiments and do not say whether this sheet uses the sampled batches)"
DS["paired-overall"] = "All five paired dataset splits (mean)"
DS["unpaired-overall"] = "All six unpaired dataset splits (mean)"
data_ids = {k: b.entity("dataset_subset", b.rid("data", k), f"{k} (SCMBench)", v + ".", [ART, SD1], {"source_dataset_label": k, "source_locator": "Fig. 1b; Supplementary Data 1, sheet 'Dataset'",
            "missing_metadata": {"version": {"reason": "unreported"}}}) for k, v in DS.items()}
PROTO = {}
for kind in ("paired", "unpaired"):
    PROTO[kind] = b.entity("protocol", b.rid("protocol", kind, "integration-accuracy"), f"SCMBench {kind} RNA-ATAC integration accuracy",
        f"Integrate {kind} scRNA-seq and scATAC-seq; score the joint embedding by the mean of mean average precision, normalised mutual information, average silhouette width and ARI of cell type labels (integration accuracy overall score).",
        [ART, SD2], {"protocol": f"{kind.capitalize()} multi-omics integration; per-dataset overall score is the mean of MAP, NMI, ASW and ARI ('The overall score represents the mean of these four integration accuracy metrics', Results).",
                     "version": "Nature Communications 2026", "metric": "scmbench-integration-accuracy", "metric_direction": "higher", "unit": "unitless",
                     "limitations": ["Single run per method and dataset; no spread printed.", "Foundation models receive ATAC as gene activity scores (MAESTRO)."],
                     "source_locator": "Results 'Benchmarking data integration on both paired and unpaired datasets'; Fig. 2e-f; Supplementary Data 2"},
        links=[{"relation": "part_of", "target_id": BENCH}])
REV = lambda loc, raw: extraction_review(["deterministic-table-parse"], f"Read the cell from the sheet XML of the pinned workbook with extract_scmbench.py (stored value {raw}, General format); row labels and headers asserted. " + loc, H[sd2], ESM + "41467_2026_72570_MOESM4_ESM.xlsx")


def canon(raw):
    """The stored double at 15 significant digits, the precision a spreadsheet displays for a General-format cell."""
    return format(float(raw), ".15g")


# Across-dataset means over fewer datasets (reviewer cn-2, S3).
PARTIAL_MEAN = {("paired", "scGPT"): "mean of MAP, NMI, ASW and ARI; across-dataset mean over 10x-Multiome-Pbmc10k only"}
for m in ("bindSC", "scMoMaT", "scGPT_zero", "Pamona", "scFoundation", "Geneformer"):
    PARTIAL_MEAN[("unpaired", m)] = "mean of MAP, NMI, ASW and ARI; mean across the five Muto-2021 batches (Yao not scored)"
evals, n = {}, 0
for kind, sheet, cols, nrows in (("paired", "paired_inte_overall", ["10x-Multiome-Pbmc10k", "Chen-2019", "Ma-2020-batch-53", "Ma-2020-batch-54", "Ma-2020-batch-55", "Overall"], 22),
                                 ("unpaired", "unpaired_inte_overall", ["Yao"] + [f"Muto-2021-batch-{i}" for i in range(1, 6)] + [None], 17)):
    cells = sheet_cells(sd2, sheet)
    letters = "BCDEFGH"
    hdr = [cells.get(f"{L}1", (None,))[0] for L in letters[:len(cols)]]
    assert hdr == cols, (sheet, hdr)
    for row in range(2, 2 + nrows):
        label = cells[f"A{row}"][0]
        sysid = system(label)
        for L, col in zip(letters, cols):
            c = cells.get(f"{L}{row}")
            if c is None:
                continue  # blank cell: method not run on this dataset
            raw, t, fmt, formula = c
            assert t is None and fmt == "General", (sheet, L, row, c)
            dkey = col if col not in ("Overall", None) else f"{kind}-overall"
            key = (sysid, kind, dkey)
            if key not in evals:
                evals[key] = b.evaluation(b.rid("eval", kind, dkey, label), f"{label} on SCMBench {kind} integration, {dkey}", SIDS, sysid, PROTO[kind], data_ids[dkey],
                    "author_reported" if label == "FM-scVI" else "independent_paper",
                    {"protocol_id": PROTO[kind], "dataset_version": None, "split": "Per dataset or batch as in Supplementary Data 2; whether batch splits use the 2,500-cell samples is not stated", "population": None,
                     "inputs": "scRNA-seq counts and scATAC-seq peaks (gene activity scores for foundation models)", "adaptation": None,
                     "metric_implementation": "SCMBench integration accuracy (MAP, NMI, ASW, ARI)",
                     "aggregation": "Mean of four metrics" + ("; mean across datasets" if dkey.endswith("overall") else ""), "budget": None},
                    f"Supplementary Data 2, sheet '{sheet}', row {row} '{label}'")
            loc = f"Supplementary Data 2, sheet '{sheet}', cell {L}{row} (row '{label}', column '{col or 'unlabelled column H'}')"
            extra = {"raw_xml_value": raw, "workbook_number_format": fmt, "source_cells": [f"'{sheet}'!{L}{row}"],
                     "printed_value_basis": "Stored number of a General-format cell at 15 significant digits (raw XML value kept in raw_xml_value); visible spreadsheet precision depends on column width."
                                            + (" The cell is a formula; its cached value is recorded." if formula else "")}
            q = "mean of MAP, NMI, ASW and ARI"
            if dkey.endswith("overall"):
                q = PARTIAL_MEAN.get((kind, label), q + "; mean across datasets")
            b.result(b.rid("result", kind, dkey, label), f"{label} SCMBench {kind} integration accuracy, {dkey}", SD2, SIDS, evals[key], canon(raw),
                     "scmbench-integration-accuracy", "higher", "unitless", loc, REV(loc, raw), qualifier=q, numeric=raw, extra=extra)
            n += 1
    assert cells.get(f"A{2 + nrows}") is None, (sheet, cells.get(f"A{2 + nrows}"))
# Paired: 22 rows x 6 columns, less 4 blank scGPT cells; unpaired: 17 rows x 7 columns, less 6 blank Yao cells.
assert n == 128 + 113, n
finalise(b, "reviewer-cn-2", "2026-10-12T08:44:00Z",
         "raw XML value, numeric value, printed value, locator, metric, unit, direction and linked configuration, protocol and dataset checked by the reviewer's own read of the sheet XML and a hand check of 40 values against the cell grid.",
         "Artifact re-downloaded and SHA-256 matched; the archived gzip copy matches.")
print(json.dumps(b.write()))
