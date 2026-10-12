"""Ye et al. 2026, static GRN reconstruction from single-cell foundation models on BEELINE datasets (bioRxiv 10.64898/2026.05.17.725083 v1):
appendix Tables 4-7 (early precision ratio and AUPRC ratio, TF+500 and TF+1000) from the pdftotext -layout text of the pinned PDF.

Table 1 repeats the TF+500 mean and standard deviation rows of Tables 4 and 6 and is not extracted separately (see the evidence concern on the source).

Usage: pdftotext -layout <paper.pdf> <paper.txt>; python3 -I extract_ye2026.py <paper.pdf> <paper.txt> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, finalise

pdf, txt, folder = sys.argv[1:4]
SHA = sha256(pdf)
assert SHA == "a6c3aae569b1f1614c71569efb0692f15700aea473c64c7bc0bc660e81330dc7", SHA
URL = "https://www.biorxiv.org/content/10.64898/2026.05.17.725083v1.full.pdf"
B = "lit-cells-networks-20261011-ye2026grn"
b = Batch(folder, B, areas=["biological-networks", "single-cell"])
lines = open(txt, encoding="utf-8").read().replace("\f", "").split("\n")

SRC = b.source(B + "-source-ye2026", "Benchmarking Static Gene Regulatory Network Reconstruction and Dynamic Transition Probing in Single-Cell Foundation Models", {
    "url": "https://doi.org/10.64898/2026.05.17.725083", "artifact_url": URL, "version": "bioRxiv preprint version 1, posted 2026-05-20",
    "retrieved_at": "2026-10-11T21:36:31Z", "artifact_sha256": SHA, "doi": "10.64898/2026.05.17.725083", "publication_status": "preprint",
    "licence": "CC-BY-4.0", "media_type": "application/pdf",
    "hash_scope": "Exact bytes of one download. bioRxiv serves slightly different PDF bytes per download (41 bytes differed between two downloads 2 minutes apart; pdftotext output identical), so the gzip copy in artifacts/ is the reference.",
    "limitations": ["Preprint, not peer reviewed.", "One run per dataset; the printed spread is the standard deviation across the six datasets, not across runs.",
                    "The authors developed none of the evaluated models or baselines."],
    "evidence_concerns": [{"source_id": B + "-source-ye2026", "message": "Table 1 labels its middle reference column 'ChIP-seq' and the caption names cell-type-specific ChIP-seq, but its values equal the 'Nonspecific ChIP-seq' mean and std rows of Tables 4 and 6 (for example scGPT costok EPR 4.211±1.703), and Appendix B says cell-type-specific ChIP-seq is excluded from the main comparison. Table 1 is therefore not extracted; Tables 4-7 carry the reference labels.",
                           "source_locator": "Table 1 caption and column header; Tables 4 and 6, 'Nonspecific ChIP-seq' mean rows; Appendix B text before Table 4", "artifact_sha256": SHA, "review_date": "2026-10-11"},
                          {"source_id": B + "-source-ye2026", "message": "Table 6 is titled 'AUPR' and Table 7 'AUPRC', but both print ratios over a random predictor (values above 1), matching the 'AUPRC ratio' of Table 1; both are recorded as auprc-ratio.",
                           "source_locator": "Table 6 and Table 7 captions; Table 1 caption", "artifact_sha256": SHA, "review_date": "2026-10-11"},
                          # Reviewer cn-1, correction Y1 (verbatim).
                          {"source_id": "lit-cells-networks-20261011-ye2026grn-source-ye2026", "message": "Table 7 (TFs+1000 AUPRC) repeats Table 6 (TFs+500 AUPR) exactly in the GENIE3 column of the STRING, Cell-type-specific ChIP-seq and Nonspecific ChIP-seq blocks: all 18 dataset values and the three mean and std rows are identical (for example STRING hESC 1.6241, mean 3.301, std 2.244). Only the OmniPath block differs. Every other column, and GENIE3 in the EPR Tables 4 and 5, differs between the two gene sets, and the Table 6 values match Table 1. These 21 Table 7 GENIE3 values are likely a copy of the TFs+500 values and should not be compared.", "source_locator": "Table 7, column group 'ML', column 'GENIE3', blocks 'STRING', 'Cell-type-specific' and 'Nonspecific'; Table 6, same cells; Table 1, GENIE3 AUPRC ratio", "artifact_sha256": "a6c3aae569b1f1614c71569efb0692f15700aea473c64c7bc0bc660e81330dc7", "review_date": "2026-10-12"}]},
    description="bioRxiv PDF, retrieved and hashed for the 2026-10-11 networks-mechanistic literature pass.")
SIDS = [SRC]
REV = lambda loc: extraction_review(["pdf-text-parse"], "Parsed the pdftotext -layout text of the pinned PDF with extract_ye2026.py: rows of exactly 21 numbers taken in printed order, 8 rows (six datasets, mean, std) per reference block, dataset and reference labels asserted where printed, column headers asserted. " + loc, SHA, URL)

BENCH = b.entity("benchmark", b.rid("benchmark", "static-grn-fm"), "Static GRN reconstruction from single-cell foundation models (Ye et al. 2026)",
    "Zero-shot GRN reconstruction from six single-cell foundation models with three extraction strategies (token-embedding cosine, hidden-state cosine, attention) against GENIE3, DeepSEM and GRNBoost, on six BEELINE scRNA-seq datasets and four reference network types.",
    SIDS, {"entity_level": "suite", "version": "bioRxiv v1 (2026-05-20)", "task": "Gene regulatory network inference from single-cell expression",
           "scope_note": "Uses BEELINE datasets and preprocessing with TF-prioritised gene sets (TFs+500, TFs+1000); edges restricted to TF-target candidates and ranked by absolute weight.",
           "source_locator": "Sections 2.1-2.2; Appendix A-B; Tables 4-7"})

FM = {"scGPT": "catalog-model-scgpt", "scFoundation": "catalog-model-scfoundation", "Geneformer": "catalog-model-geneformer",
      "LangCell": "cell-type-20261009-model-langcell", "scCello": "cell-type-20261009-model-sccello", "scPRINT": None}
scprint = b.entity("model", b.rid("model", "scprint"), "scPRINT", "Single-cell foundation model pretrained on CELLxGENE data for gene network inference and expression denoising (Kalfon et al.).", SIDS,
                   {"reported_name": "scPRINT", "entity_level": "family", "source_locator": "Section 2.1; Table 3",
                    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}, method_types=["foundation_model"])
FM["scPRINT"] = scprint
deepsem = b.entity("method", b.rid("method", "deepsem"), "DeepSEM", "Deep generative structural equation model for GRN inference from scRNA-seq (Shu et al. 2021).", SIDS,
                   {"reported_name": "DeepSEM", "entity_level": "method", "source_locator": "Section 2.1; Appendix A.2",
                    "missing_metadata": {"version": {"reason": "unreported"}}}, method_types=["specialist"])
ML = {"GENIE3": "discovery-model-genie3", "DeepSEM": deepsem, "GRNboost": "discovery-model-grnboost"}
STRAT = {"costok": "cosine similarity of pretrained gene token embeddings (undirected)",
         "attn": "last-layer attention scores aggregated across heads and cells (directed)",
         "coshid": "cosine similarity of last-layer hidden states aggregated over cells (undirected)"}
# Checkpoints named in Appendix A.2 (reviewer cn-1, correction Y4); scFoundation and LangCell have none.
NO_RELEASE = {"reason": "unreported", "note": "No release or revision named"}
CHECKPOINT = {
    "scGPT": ("Whole-human checkpoint pretrained on 33 million normal human cells (Appendix A.2)", NO_RELEASE),
    "Geneformer": ("12-layer checkpoint, the larger of the 6- and 12-layer releases; Table 3 lists 30M pretraining cells (Appendix A.2; Table 3)", NO_RELEASE),
    "scCello": ("Default released pretrained checkpoint (Appendix A.2)", NO_RELEASE),
    "scPRINT": ("Default released pretrained checkpoint (Appendix A.2)", NO_RELEASE),
    "scFoundation": (None, {"reason": "unreported", "note": "Source names no checkpoint; Table 3 gives size, layers and pretraining cells"}),
    "LangCell": (None, {"reason": "unreported", "note": "Source names no checkpoint; Table 3 gives size, layers and pretraining cells"}),
}
GRNBOOST_DESC = "GRNBoost run by Ye et al. 2026 directly on each expression matrix with the default benchmark configuration, without pretrained representations. The paper cites GRNBoost2 and arboreto (Moerman et al. 2019, reference 12)."
cfgs = {}


def config(strategy, model):
    k = (strategy, model)
    if k in cfgs:
        return cfgs[k]
    if strategy == "ML":
        name = "GRNBoost (Ye et al. 2026 baseline)" if model == "GRNboost" else f"{model} (Ye et al. 2026 baseline)"
        desc = GRNBOOST_DESC if model == "GRNboost" else f"{model} run by Ye et al. 2026 directly on each expression matrix, without pretrained representations."
        cfgs[k] = b.entity("configuration", b.rid("config", model), name, desc, SIDS, {
            "reported_name": model, "foundation_model_eligible": False, "training_setting": "Inferred from each test expression matrix",
            "source_locator": "Section 2.1; Appendix A.2", "missing_metadata": {"version": {"reason": "unreported"}, "hyperparameters": {"reason": "unextracted"}}},
            method_types=["specialist"], links=[{"relation": "configuration_of", "target_id": ML[model]}])
    else:
        checkpoint, version = CHECKPOINT[model]
        attrs = {"reported_name": f"{model} {strategy}", "foundation_model_eligible": True, "training_setting": "Zero-shot; pretrained weights, no fine-tuning",
                 "representation": STRAT[strategy], "source_locator": "Section 2.2; Table 3; Appendix A.2"}
        if checkpoint:
            attrs["checkpoint"] = checkpoint
        attrs["missing_metadata"] = {"version": version}
        cfgs[k] = b.entity("configuration", b.rid("config", model, strategy), f"{model} {strategy} GRN (Ye et al. 2026)", f"{model} zero-shot GRN from {STRAT[strategy]}.", SIDS, attrs,
            method_types=["foundation_model"], links=[{"relation": "configuration_of", "target_id": FM[model]}])
    return cfgs[k]


COLS = [("costok", m) for m in FM] + [("attn", m) for m in FM] + [("coshid", m) for m in FM] + [("ML", m) for m in ML]
assert len(COLS) == 21
DATASETS = ["hESC", "hHep", "mDC", "mHSC-E", "mHSC-GM", "mHSC-L"]
REFS = [("STRING", "STRING"), ("Cell-type-specific", "cell-type-specific ChIP-seq"), ("Nonspecific", "non-specific ChIP-seq"), ("OmniPath", "OmniPath")]
REFNAME = {"STRING": "STRING functional interactions", "cell-type-specific ChIP-seq": "cell-type-specific ChIP-seq", "non-specific ChIP-seq": "non-specific ChIP-seq", "OmniPath": "OmniPath signalling and pathway interactions"}
SETTINGS = {"TF+500": "TFs+500", "TF+1000": "TFs+1000"}

data_ids = {}


def data(setting, ds):
    k = (setting, ds)
    if k not in data_ids:
        if ds == "mean":
            data_ids[k] = b.entity("dataset_subset", b.rid("data", setting, "six-datasets"), f"Six BEELINE datasets, {SETTINGS[setting]} (Ye et al. 2026)",
                f"All six BEELINE scRNA-seq datasets ({', '.join(DATASETS)}) with the {SETTINGS[setting]} gene set; results are means across datasets.", SIDS,
                {"split": "No train/test split; zero-shot network inference on each full expression matrix", "source_locator": "Section 2.1; Appendix A.1",
                 "missing_metadata": {"version": {"reason": "unreported"}}})
        else:
            data_ids[k] = b.entity("dataset_subset", b.rid("data", setting, ds), f"BEELINE {ds}, {SETTINGS[setting]} (Ye et al. 2026)",
                f"BEELINE {ds} scRNA-seq expression matrix preprocessed with the BEELINE protocol, restricted to all significant TFs plus the top {setting.split('+')[1]} most dynamically variable non-TF genes.", SIDS,
                {"split": "No train/test split; zero-shot network inference on the full expression matrix", "source_dataset_label": ds, "source_locator": "Section 2.1; Appendix A.1",
                 "missing_metadata": {"version": {"reason": "unreported"}}})
    return data_ids[k]


protos = {}


def proto(setting, ref):
    k = (setting, ref)
    if k not in protos:
        protos[k] = b.entity("protocol", b.rid("protocol", setting, ref), f"Ye et al. 2026 GRN reconstruction, {SETTINGS[setting]}, {ref} reference",
            f"Rank TF-target candidate edges by absolute weight; early precision ratio scores the top K edges (K = number of reference edges) and AUPRC ratio the full ranked list, each over a random predictor, against the {REFNAME[ref]} reference.", SIDS, {
            "protocol": f"{SETTINGS[setting]} gene set; candidate space restricted to reference TFs as sources and reference-set genes as targets; {ref} reference network; early precision and precision-recall over ranked edges (Appendix B.2).",
            "version": "bioRxiv v1", "metric": "early-precision-ratio", "metric_direction": "higher", "unit": "unitless",
            "limitations": ["One run per dataset; dataset-level spread only.", "Ratios over a random predictor depend on reference network density, so values are not comparable across references or gene sets."]
                           + (["The authors report near-random performance for every method on this reference and exclude it from the main comparison (Appendix B)."] if ref == "cell-type-specific ChIP-seq" else []),
            "source_locator": "Tables 4-7; Section 2.2; Appendix B.2"}, links=[{"relation": "part_of", "target_id": BENCH}])
    return protos[k]


def parse_table(title_re, next_re, header_names):
    s = next(i for i, l in enumerate(lines) if re.search(title_re, l))
    e = next(i for i in range(s + 1, len(lines)) if re.search(next_re, lines[i]))
    seg = lines[s:e]
    hdr = next(l for l in seg if "scFoundation" in l and "GENIE3" in l)
    assert hdr.split() == header_names, hdr.split()
    rows = []
    for l in seg:
        nums = re.findall(r"(?<![\w.])\d+\.\d+(?![\w.])", l)
        if len(nums) == 21:
            label = re.sub(r"(?<![\w.])\d+\.\d+(?![\w.])", "", l).split()
            rows.append((label, nums))
    assert len(rows) == 32, len(rows)
    return rows


H_A = ["scGPT", "scFoundation", "Geneformer", "Langcell", "scCello", "scPRINT"] * 3 + ["GENIE3", "DeepSEM", "GRNboost"]
H_B = ["scGPT", "scFoundation", "Geneformer", "Langcell", "scello", "scPRINT", "scGPT", "scFoundation", "Geneformer", "Langcell", "scCello", "scPRINT", "scGPT", "scFoundation", "Geneformer", "Langcell", "scello", "scPRINT", "GENIE3", "DeepSEM", "GRNboost"]
TABLES = [  # (table, title regex, next regex, header, setting, metric)
    (4, r"Table 4: Early precision ratio", r"Table 5:", H_A, "TF+500", "early-precision-ratio"),
    (5, r"Table 5: EPR Performance", r"Table 6:", H_B, "TF+1000", "early-precision-ratio"),
    (6, r"Table 6: AUPR Performance", r"Table 7:", H_B, "TF+500", "auprc-ratio"),
    (7, r"Table 7: AUPRC Performance", r"Table 8:", H_B, "TF+1000", "auprc-ratio"),
]
evals = {}
n = 0
for t, tre, nre, hdr, setting, metric in TABLES:
    rows = parse_table(tre, nre, hdr)
    for gi, (reflabel, ref) in enumerate(REFS):
        block = rows[gi * 8:(gi + 1) * 8]
        labels = [" ".join(r[0]) for r in block]
        expected = DATASETS + ["mean", "std"]
        for lab, exp in zip(labels, expected):
            # A printed label is the dataset code, optionally preceded by the reference label or a page number; the first hESC row of
            # Tables 4 and 6 prints its label on a separate line.
            assert lab == "" or lab.split()[-1] == exp, (t, reflabel, lab, exp)
        joined = " ".join(labels).lower()
        if reflabel != "Cell-type-specific":
            assert reflabel.lower() in joined, (t, reflabel, labels)
        else:
            assert "cell-type-specific" in joined, (t, labels)
        std = block[7][1]
        for di, ds in enumerate(DATASETS + ["mean"]):
            vals = block[di][1]
            for ci, (strategy, model) in enumerate(COLS):
                c = config(strategy, model)
                p = proto(setting, ref)
                d = data(setting, ds)
                key = (c, p, d)
                if key not in evals:
                    evals[key] = b.evaluation(b.rid("eval", setting, ref, ds if ds != "mean" else "six-datasets", c.replace(B + "-config-", "")),
                        f"{model} {strategy if strategy != 'ML' else ''} GRN on {ds if ds != 'mean' else 'six BEELINE datasets (mean)'}, {SETTINGS[setting]}, {ref}".replace("  ", " "),
                        SIDS, c, p, d, "independent_paper",
                        {"protocol_id": p, "dataset_version": None, "split": "No train/test split; networks inferred from each full expression matrix", "population": None,
                         "inputs": f"BEELINE-preprocessed expression matrix, {SETTINGS[setting]} gene set (token-embedding configurations use only the gene list)",
                         "adaptation": "Foundation models zero-shot from pretrained weights; GENIE3, DeepSEM and GRNBoost fitted to each expression matrix",
                         "metric_implementation": "Early precision ratio and AUPRC ratio over a random predictor (Appendix B.2)",
                         "aggregation": "Mean across the six datasets" if ds == "mean" else "Single dataset", "budget": None},
                        f"Tables {4 if setting == 'TF+500' else 5} and {6 if setting == 'TF+500' else 7}, block '{reflabel}', row '{ds}', column '{strategy} {hdr[ci]}'")
                loc = f"Table {t}, block '{reflabel}', row '{ds}', column group '{strategy}', column '{hdr[ci]}'"
                unc = {"type": "standard_deviation", "value": std[ci], "printed": std[ci], "n": 6, "scope": "across the six datasets (std row)",
                       "source_column": f"Table {t}, block '{reflabel}', row 'std', column '{hdr[ci]}'"} if ds == "mean" else None
                b.result(b.rid("result", setting, ref, ds if ds != "mean" else "six-datasets", c.replace(B + "-config-", ""), metric),
                         f"{model} {strategy} {ds} {ref} {SETTINGS[setting]} {metric}", SRC, SIDS, evals[key], vals[ci], metric, "higher", "unitless", loc, REV(loc),
                         qualifier=f"{SETTINGS[setting]} gene set; {ref} reference" + ("; mean across six datasets" if ds == "mean" else ""), uncertainty=unc)
                n += 1
assert n == 4 * 4 * 7 * 21, n

# Cross-check: Table 1 (TF+500 means) must equal the Table 4 and Table 6 mean rows for STRING and OmniPath, and its 'ChIP-seq' column the non-specific block.
t1s = next(i for i, l in enumerate(lines) if l.strip().startswith("Table 1: Performance on the TFs+500"))
t1 = [l for l in lines[t1s:t1s + 40] if re.search(r"\d\.\d{3}±\d\.\d{3}", l)]
assert len(t1) == 21, len(t1)
t1_scgpt_costok = re.findall(r"(\d\.\d{3})±", t1[0])
assert t1_scgpt_costok == ["6.568", "4.211", "2.387", "5.632", "3.002", "1.460"], t1_scgpt_costok
mean_of = lambda setting, ref, metric: [r for r in b.records if r["kind"] == "result" and r["attributes"]["metric"] == metric and f"-{setting.lower().replace('+', '-plus-')}-" in r["id"] and slugref(ref) in r["id"] and "six-datasets-scgpt-costok" in r["id"]]
slugref = lambda ref: re.sub(r"[^a-z0-9]+", "-", ref.lower()).strip("-")
chk = {(m, ref): mean_of("TF+500", ref, m)[0]["attributes"]["printed_value"] for m in ("early-precision-ratio", "auprc-ratio") for ref in ("STRING", "non-specific ChIP-seq", "OmniPath")}
assert [chk[("early-precision-ratio", r)] for r in ("STRING", "non-specific ChIP-seq", "OmniPath")] + [chk[("auprc-ratio", r)] for r in ("STRING", "non-specific ChIP-seq", "OmniPath")] == t1_scgpt_costok, chk

# Reviewer cn-1, Y1: the 21 Table 7 GENIE3 results in the duplicated blocks.
GENIE3_DUP = {f"{B}-result-tf-plus-1000-{ref}-{ds}-genie3-auprc-ratio": "Subject to the source evidence concern on Table 7 GENIE3 (duplicates Table 6)."
              for ref in ("string", "cell-type-specific-chip-seq", "non-specific-chip-seq")
              for ds in ("hesc", "hhep", "mdc", "mhsc-e", "mhsc-gm", "mhsc-l", "six-datasets")}
assert len(GENIE3_DUP) == 21
finalise(b, "reviewer-cn-1", "2026-10-12T08:40:00Z",
         "value, locator, metric, unit, direction, uncertainty and linked configuration, protocol and dataset checked by the reviewer's own parse of all Tables 4-7 cells and a hand check of 48 values against the rendered pages.",
         "Archived gzip copy unpacked and its SHA-256 matched; a fresh bioRxiv download was rate-limited (HTTP 429).", GENIE3_DUP)
print(json.dumps(b.write()))
