"""Build batch.jsonl and claims.csv for the Kendiukhov 2026 AUROC differences (BMC Genomics 27:634).

Usage: python3 -I extract_delta.py <article.pdf> <repository-root> <batch-folder>

The article's central Objective B numbers are AUROC differences printed in the running text. The
first extraction (gfm-guides-20261014-kendiukhov2026) left them out for want of a metric concept.
Each value below was transcribed by hand. The script asserts the PDF hash (the archived copy in
data/omics/gfm-guides-20261014-kendiukhov2026/artifacts/), that each quoted fragment, which contains
the printed value, occurs on the stated page of the pdftotext reading-order output after collapsing
whitespace, and that every reused record exists in the store.
"""
import csv, glob, hashlib, json, os, re, subprocess, sys
from collections import Counter

PDF_SHA = "4c1699cb964ae588117a6737f5e9e189eb9a5ef5ff78568d2a99e7a13d6608fe"
PDF_URL = "https://bmcgenomics.biomedcentral.com/counter/pdf/10.1186/s12864-026-12965-8.pdf"
P = "gfm-guides-20261014-kendiukhov2026"
SRC = f"{P}-source-article"
DATE = "2026-10-14"
FACETS = {"areas": ["single-cell", "biological-networks"], "contexts": ["research"]}
NOTE = ("Extraction agent for rewire-benchmark-data issue #163 (metric concepts for the genomic foundation model guide "
        "evidence); extraction only, not a review. Pending an independent review-evidence pass.")

pdf, repo, out = sys.argv[1], sys.argv[2], sys.argv[3]
assert hashlib.sha256(open(pdf, "rb").read()).hexdigest() == PDF_SHA, "article PDF hash mismatch"
text = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True, check=True).stdout
PAGES = [re.sub(r"\s+", " ", p).replace("- ", "-") for p in text.split("\f")]

store = {}
for path in glob.glob(os.path.join(repo, "data/entities/*.jsonl")) + glob.glob(os.path.join(repo, "data/evidence/*/*.jsonl")):
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        store[r["id"]] = r

records, claims_rows = [], []


def rec(id_, kind, name, description, attributes, links=(), facets=None, source_ids=(SRC,)):
    assert id_ not in store, id_
    records.append({"id": id_, "kind": kind, "name": name, "description": description, "status": "needs_review",
                    "facets": FACETS if facets is None else facets, "source_ids": list(source_ids),
                    "links": [{"relation": a, "target_id": b} for a, b in links], "attributes": attributes})
    return id_


def existing(id_):
    assert id_ in store, id_
    return id_


ACCESS = "Analysis code github.com/Biodyn-AI/biomechinterp-framework and Zenodo 10.5281/zenodo.18701417; not pinned to a commit in the article"
LR_METHOD = existing(f"{P}-method-gene-level-logistic-regression")
GENEFORMER = existing("catalog-model-geneformer")

# ---------------------------------------------------------------- new configurations: the augmented logistic regressions
CFG_ATT = rec(f"{P}-config-gene-level-lr-plus-attention", "configuration",
              "Gene-level logistic regression plus attention edge (Kendiukhov 2026)",
              "Logistic regression on mean expression, variance and dropout rate of the candidate target gene plus the Geneformer V2-316M attention edge score between the perturbed gene and the candidate, 5-fold GroupKFold by perturbation.",
              {"reported_name": "gene-level plus attention", "foundation_model_eligible": False,
               "representation": "Gene-level features of the candidate target plus one Geneformer V2-316M attention edge score",
               "training_setting": "Fitted under 5-fold GroupKFold by perturbation on each dataset",
               "parameters": "Attention layer used for the edge feature not stated in the article",
               "access_reuse": ACCESS,
               "source_locator": "Page 8 'No incremental pairwise value on the perturbation-target prediction task', paragraph 1; page 16 'Confound decomposition'",
               "missing_metadata": {"version": {"reason": "inapplicable", "note": "Defined in the article"}}},
              links=[("configuration_of", LR_METHOD), ("uses_model", GENEFORMER)],
              facets={**FACETS, "method_types": ["supervised_machine_learning"]})
CFG_COR = rec(f"{P}-config-gene-level-lr-plus-correlation", "configuration",
              "Gene-level logistic regression plus correlation edge (Kendiukhov 2026)",
              "Logistic regression on mean expression, variance and dropout rate of the candidate target gene plus the absolute Spearman correlation between the perturbed gene and the candidate, 5-fold GroupKFold by perturbation.",
              {"reported_name": "gene-level plus correlation", "foundation_model_eligible": False,
               "representation": "Gene-level features of the candidate target plus one absolute Spearman correlation edge score",
               "training_setting": "Fitted under 5-fold GroupKFold by perturbation on each dataset",
               "access_reuse": ACCESS,
               "source_locator": "Page 8 'No incremental pairwise value on the perturbation-target prediction task', paragraph 1; page 16 'Confound decomposition'",
               "missing_metadata": {"version": {"reason": "inapplicable", "note": "Defined in the article"}}},
              links=[("configuration_of", LR_METHOD)],
              facets={**FACETS, "method_types": ["supervised_machine_learning"]})
CFG_ATT_UNSTATED = existing(f"{P}-config-geneformer-v2-316m-attention-layer-unstated")

# ---------------------------------------------------------------- new protocol and subset: RPE1 restricted to 2,000 HVGs
PROTO_HVG = rec(f"{P}-protocol-pf-rpe1-crispri-hvg2000", "protocol",
                "Perturbation-first AUROC, RPE1 CRISPRi restricted to the top 2,000 HVGs (Kendiukhov 2026)",
                "As the RPE1 CRISPRi protocol, with the evaluation universe restricted to the top 2,000 highly variable genes to match the K562 protocol.",
                {"protocol": "As the RPE1 CRISPRi perturbation-first protocol, but restricted to the top 2,000 HVGs (matching the K562 protocol) instead of 3,309 genes with perturbation genes forced in.",
                 "version": "BMC Genomics 27:634",
                 "metric_implementation": "Per-perturbation AUROC for classifying differentially expressed targets; summary across perturbations not stated",
                 "source_locator": "Page 10, 'Context-dependent attention-correlation relationship'",
                 "limitations": ["Single run; no repeat across seeds reported.", "Only the attention advantage over correlation is printed; the absolute AUROCs are not."]},
                links=[("part_of", existing(f"{P}-benchmark-perturbation-target-prediction"))])
DS_HVG = rec(f"{P}-data-rpe1-crispri-418-hvg2000", "dataset_subset",
             "Replogle genome-scale CRISPRi, RPE1, 418 perturbations with the top 2,000 HVGs (Kendiukhov 2026)",
             "Replogle et al. 2022 CRISPRi Perturb-seq in RPE1 cells restricted to the top 2,000 highly variable genes; 418 perturbations evaluable in that universe.",
             {"split": "No train/test split for edge AUROC", "source_dataset_label": "Replogle CRISPRi (RPE1)", "scored_count": 418,
              "source_locator": "Page 10, 'Context-dependent attention-correlation relationship'",
              "missing_metadata": {"version": {"reason": "unreported"}}})

# ---------------------------------------------------------------- evaluations
EVAL_NAMES = {}


def evaluation(cfg, proto, ds, template_eval, origin, unstated_split=False, locator=None, inputs=None):
    cfg_slug = cfg.removeprefix(f"{P}-config-")
    eid = f"{P}-eval-{proto.removeprefix(f'{P}-protocol-')}-{ds.removeprefix(f'{P}-data-')}-{cfg_slug}"
    if eid in EVAL_NAMES:
        return eid
    t = store[template_eval]["attributes"]
    comp = dict(t["comparison"])
    comp["protocol_id"] = proto
    if inputs is not None:
        comp["inputs"] = inputs
    missing = dict(t["missing_metadata"])
    if unstated_split:  # the template's split does not apply
        comp["split"] = None
        missing["comparison.split"] = {"reason": "unreported", "note": "The cross-validation scheme of the incremental test on matched pairs is not restated"}
    cfg_name = (store[cfg]["name"] if cfg in store else next(r["name"] for r in records if r["id"] == cfg)).removesuffix(" (Kendiukhov 2026)")
    ds_name = (store[ds]["name"] if ds in store else next(r["name"] for r in records if r["id"] == ds)).removesuffix(" (Kendiukhov 2026)")
    EVAL_NAMES[eid] = f"{cfg_name} on {ds_name}"
    rec(eid, "evaluation", EVAL_NAMES[eid], "Published comparison transcribed from the pinned source; not reproduced.",
        {"origin": origin, "protocol": proto, "version": "BMC Genomics 27:634 as retrieved 2026-10-14", "comparison": comp,
         "source_locator": locator or t["source_locator"], "missing_metadata": missing},
        links=[("system", cfg), ("assessment", proto), ("data", ds)])
    return eid


LR = existing(f"{P}-protocol-incremental-value-lr")
PF_K562 = existing(f"{P}-protocol-pf-k562-crispri")
PF_RPE1 = existing(f"{P}-protocol-pf-rpe1-crispri")
T_LR = existing(f"{P}-eval-incremental-value-lr-k562-crispri-280-gene-level-logistic-regression")
T_PF_K562 = existing(f"{P}-eval-pf-k562-crispri-k562-crispri-280-spearman-edge")
T_PF_RPE1 = existing(f"{P}-eval-pf-rpe1-crispri-rpe1-crispri-1251-spearman-edge")
K280, R1167, R1251 = (existing(f"{P}-data-k562-crispri-280"), existing(f"{P}-data-rpe1-crispri-1167"), existing(f"{P}-data-rpe1-crispri-1251"))
KPM = existing(f"{P}-data-k562-crispri-propensity-matched")

Q_INC = ("{feature} minus gene-level features only (gene-level logistic regression); cross-validated AUROC over perturbation-gene "
         "pairs, 5-fold GroupKFold by perturbation")
Q_ADV = ("Geneformer V2-316M attention edge minus absolute Spearman correlation edge (per-perturbation attention advantage); "
         "per-perturbation AUROC for DE targets, summary over perturbations not stated")
BOOT = "Methods 'Statistical framework': bootstrap CIs use 200 iterations with perturbation-level resampling unless otherwise noted"


def ci(lower, upper, printed, note=BOOT):
    return {"type": "confidence_interval", "lower": lower, "upper": upper, "level": 0.95, "method": "bootstrap",
            "printed": printed, "note": note}


# (config, protocol, data, template evaluation, origin, eval overrides, printed, numeric, page, locator, fragment, qualifier, uncertainty)
VALUES = [
    (CFG_ATT, LR, K280, T_LR, "author_reported", {}, "−0.0004", "-0.0004", 8,
     "Page 8, 'No incremental pairwise value on the perturbation-target prediction task', paragraph 1, sentence 2",
     "adding attention yields ∆AUROC = −0.0004 [−0.001, 0.000]", Q_INC.format(feature="Gene-level features plus attention edge"),
     ci("-0.001", "0.000", "[−0.001, 0.000]", BOOT + "; Fig. 4B caption: 'Bootstrap ∆AUROC distribution (n = 100)'")),
    (CFG_COR, LR, K280, T_LR, "author_reported", {}, "−0.002", "-0.002", 8,
     "Page 8, 'No incremental pairwise value on the perturbation-target prediction task', paragraph 1, sentence 2",
     "adding correlation yields ∆AUROC = −0.002 [−0.005, 0.000]", Q_INC.format(feature="Gene-level features plus correlation edge"),
     ci("-0.005", "0.000", "[−0.005, 0.000]", BOOT + "; Fig. 4B caption: 'Bootstrap ∆AUROC distribution (n = 100)'")),
    (CFG_ATT, LR, KPM, T_LR, "author_reported",
     {"split": None, "locator": "Page 9, paragraph 1 (continuing 'No incremental pairwise value'), sentence 3"},
     "−0.000", "-0.000", 9,
     "Page 9, paragraph 1 (continuing 'No incremental pairwise value'), sentence 3",
     "add zero incremental value over gene-level features (∆AUROC = −0.000; 95% CI: [−0.000, +0.000]",
     "Gene-level features plus attention edge minus gene-level features only (logistic regression); AUROC over propensity-matched perturbation-gene pairs (k = 5 negatives per positive)",
     {"type": "confidence_interval", "lower": "-0.000", "upper": "0.000", "level": 0.95, "printed": "95% CI: [−0.000, +0.000]",
      "note": "Interval type printed as '95% CI' without naming bootstrap; " + BOOT}),
    (CFG_ATT, LR, R1167, T_LR, "author_reported", {"locator": "Page 10, 'Cross-cell-type generalisation of confound pattern', item (ii)"},
     "+0.0001", "0.0001", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (ii)",
     "adding attention yields ∆AUROC = +0.0001 [95% CI: +0.0001, +0.0001]", Q_INC.format(feature="Gene-level features plus attention edge"),
     {"type": "confidence_interval", "lower": "0.0001", "upper": "0.0001", "level": 0.95, "printed": "[95% CI: +0.0001, +0.0001]",
      "note": "Interval type printed as '95% CI' without naming bootstrap; " + BOOT}),
    (CFG_COR, LR, R1167, T_LR, "author_reported", {"locator": "Page 10, 'Cross-cell-type generalisation of confound pattern', item (ii)"},
     "−0.0006", "-0.0006", 10,
     "Page 10, 'Cross-cell-type generalisation of confound pattern', item (ii)",
     "while adding correlation yields ∆AUROC = −0.0006", Q_INC.format(feature="Gene-level features plus correlation edge"), None),
    (CFG_ATT_UNSTATED, PF_K562, K280, T_PF_K562, "independent_paper", {"locator": "Page 10, 'Context-dependent attention-correlation relationship'"},
     "+0.060", "0.060", 10,
     "Page 10, 'Context-dependent attention-correlation relationship', sentence beginning 'Bootstrap 95% CIs on the per-perturbation attention advantage'",
     "K562 (∆ = +0.060 [+0.040, +0.080])", Q_ADV + "; K562 CRISPRi",
     ci("0.040", "0.080", "Bootstrap 95% CIs ... (∆ = +0.060 [+0.040, +0.080])")),
    (CFG_ATT_UNSTATED, PF_RPE1, R1251, T_PF_RPE1, "independent_paper", {},
     "+0.090", "0.090", 10,
     "Page 10, 'Context-dependent attention-correlation relationship', sentence beginning 'Bootstrap 95% CIs on the per-perturbation attention advantage'",
     "RPE1 (∆ = +0.090 [+0.079, +0.101]", Q_ADV + "; RPE1 CRISPRi",
     ci("0.079", "0.101", "Bootstrap 95% CIs ... (∆ = +0.090 [+0.079, +0.101])")),
    (CFG_ATT_UNSTATED, PROTO_HVG, DS_HVG, T_PF_RPE1, "independent_paper",
     {"locator": "Page 10, 'Context-dependent attention-correlation relationship'",
      "inputs": "Control-cell expression and DE labels of the perturbation dataset; evaluation universe restricted to the top 2,000 HVGs (matching the K562 protocol)"},
     "+0.168", "0.168", 10,
     "Page 10, 'Context-dependent attention-correlation relationship', sentence beginning 'A methodological asymmetry'",
     "increases the attention advantage (∆ = +0.168, n = 418", Q_ADV + "; RPE1 CRISPRi restricted to the top 2,000 HVGs", None),
]

for cfg, proto, ds, template, origin, over, printed, numeric, page, loc, fragment, qual, unc in VALUES:
    assert fragment in PAGES[page - 1], (page, fragment)
    assert printed in fragment, (printed, fragment)
    eid = evaluation(cfg, proto, ds, template, origin, unstated_split="split" in over, locator=over.get("locator"),
                     inputs=over.get("inputs"))
    rid = eid.replace("-eval-", "-result-") + "-auroc-difference"
    full_loc = f"{loc}: '{fragment}'"
    attrs = {"metric": "auroc-difference", "metric_direction": "higher", "unit": "unitless",
             "printed_value": printed, "numeric_value": numeric, "metric_qualifier": qual, "source_locator": full_loc,
             "review": {"method": ["pdf-text-parse", "transcription"],
                        "method_note": "Hand transcription from the article text; extract/extract_delta.py asserts that the quoted fragment, which contains the printed value, occurs on the stated page of the pdftotext output of the pinned PDF.",
                        "reviewer": ["claude"], "reviewer_note": NOTE, "date": DATE,
                        "artifact_sha256": PDF_SHA, "retrieval_url": PDF_URL,
                        "note": "Extracted, not reviewed. printed_value keeps the source's sign characters (U+2212 minus); numeric_value uses ASCII. The review-evidence pass must re-check this value against the pinned PDF."}}
    if unc:
        attrs["uncertainty"] = unc
    else:
        attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
    rec(rid, "result", f"{EVAL_NAMES[eid]}: AUROC difference", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        attrs, links=[("evaluation", eid)], facets={})
    claims_rows.append([rid, SRC, full_loc, printed, "result"])

# the methods sentence that defines the metric
assert "AUROC differences (∆AUROC) for incremental-value tests" in PAGES[15], "page 16 definition"

for r in records:  # the store keeps missing_metadata keys sorted (normalizeAttributes)
    if "missing_metadata" in r["attributes"]:
        r["attributes"]["missing_metadata"] = dict(sorted(r["attributes"]["missing_metadata"].items()))
records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids))
with open(os.path.join(out, "batch.jsonl"), "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(out, "claims.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(sorted(claims_rows))
counts = Counter(r["kind"] for r in records)
assert counts["result"] == 8, counts
print(dict(sorted(counts.items())))
