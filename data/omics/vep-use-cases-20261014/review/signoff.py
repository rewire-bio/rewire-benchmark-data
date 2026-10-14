"""Independent review sign-off for vep-use-cases-20261014 (2026-10-14).

Usage: python3 -I review/signoff.py

Run review/check_values.py first. This script refuses to run on anything but the extractor's
batch.jsonl (SHA-256 below). It applies the corrections listed in
docs/reviews/vep-use-cases-2026-10-14-review.md, sets the reviewed records to source_checked
(the 21 predictor records without results stay discovered), writes the review objects and
reviewed_evaluations, and writes batch.jsonl and coverage.json back.
"""
import glob
import hashlib
import json
from pathlib import Path

BATCH_DIR = Path(__file__).resolve().parent.parent
REPO = BATCH_DIR.parent.parent.parent
BATCH = BATCH_DIR / "batch.jsonl"
EXTRACTOR_SHA = "277d103f76bd9956f9d03bb902cb6ac27af99b88315050728d3cedc3c99c8f39"
REVIEW_DOC = "docs/reviews/vep-use-cases-2026-10-14-review.md"
REVIEWED_AT = "2026-10-14T16:00:00Z"
REVIEWER_NOTE = ("Claude review agent; no human review claimed. Independent Claude (Opus 5.5) review agent, separate from "
                 "the extraction agent that built this batch. Automated review only. Transcription, not reproduction.")
P = "vep-uc-20261014-"
TRANSCRIBED = "Transcribed from the source; no reproduction by Rewire and no human scientific review."

assert hashlib.sha256(BATCH.read_bytes()).hexdigest() == EXTRACTOR_SHA, "batch.jsonl is not the extractor's output"
records = [json.loads(line) for line in BATCH.open()]
by = {r["id"]: r for r in records}
assert len(records) == 295


def insert_before_last(lst, items):
    """Add limitations before the closing 'Transcribed ...' line."""
    assert lst[-1] == TRANSCRIBED
    return lst[:-1] + [i for i in items if i not in lst] + [TRANSCRIBED]


# 1. PMC article pages: record that the page is mutable and the hash describes these retrievals.
for r in records:
    a = r["attributes"]
    if r["kind"] == "source" and "pmc.ncbi.nlm.nih.gov" in a["url"]:
        old = "; a re-download hashes the same."
        assert old in a["hash_scope"]
        a["hash_scope"] = a["hash_scope"].replace(old, (
            ". The page is a mutable website: this hash describes the retrievals of 2026-10-14 (the collector's, and two by the "
            "reviewer, gave the same normalised hash); a later change to the page would change it."))

# 2. Origin of the carried-over Bergquist rows (ruling b).
for tool in ("bayesdel", "vest4"):
    ev = by[P + f"eval-bergquist2025-intervals-{tool}"]["attributes"]
    assert ev["origin"] == "independent_paper"
    ev["origin"] = "author_reported"
    ev["interpretation"] = (
        "All intervals are those of Pejaver et al. 2022, whose authors include this tool's developer; the 3-point and "
        "indeterminate intervals are added here (Table 1 caption). Origin set to author_reported in review so that the same "
        "calibration carries the same origin in both papers.")

# 3. Bergquist protocol limitations.
proto = by[P + "protocol-bergquist2025-point-intervals"]["attributes"]
proto["limitations"] = [l for l in proto["limitations"] if not l.startswith("V. Pejaver and P. Radivojac")] + [
    "V. Pejaver and P. Radivojac (MutPred2; Pejaver also REVEL) are authors. The BayesDel, MutPred2, REVEL and VEST4 rows "
    "come from Pejaver et al. 2022, whose authors include the developers of all four.",
    "Some of the previously calibrated tools did not reach the likelihood ratios expected for the 3-point intervals when the "
    "authors checked them (Results, Fig. 1B).",
    "The caption says Very Strong was never reached, but Pejaver et al. 2022 Table 2 gives a BP4 Very Strong interval for REVEL "
    "(≤0.003); here REVEL's Strong (−4) interval, ≤ 0.016, covers both.",
    "The authors state that this calibration shares the limitations of the previous study: representativeness of the data, "
    "potential circularities, prior probability estimation and gene- or disease-specific variability (Discussion).",
]

# 4. Bergquist uncertainty: the supplement was not retrieved, so not 'unreported'.
BERG_UNC = {"reason": "unextracted", "note": (
    "The main text prints no bounds for the thresholds; Figure 1 shows one-sided 95% bootstrap bounds as curves. The "
    "Supplementary Material PDF was not retrieved (PMC returned an HTML page on 2026-10-14).")}
for r in records:
    a = r["attributes"]
    if r["kind"] == "result" and r["source_ids"] == [P + "source-bergquist2025"] and a["printed_value"] != "-":
        assert a["missing_metadata"]["uncertainty"] == {"reason": "unreported"}
        a["missing_metadata"]["uncertainty"] = dict(BERG_UNC)

# 5. gnomAD fraction at developer thresholds: neither direction is better.
frac = by[P + "protocol-pejaver2022-developer-threshold-gnomad-fraction"]["attributes"]
frac["metric_direction"] = "unknown"
frac["limitations"] = [l for l in frac["limitations"] if not l.startswith("Lower is treated as better")] + [
    "Neither direction is better in itself: the authors compare the fraction with the 4.41% prior, and a fraction below the "
    "prior would not show a better tool (Results)."]
for tool in ("sift", "polyphen2", "cadd"):
    by[P + f"result-pejaver2022-devfraction-{tool}"]["attributes"]["metric_direction"] = "unknown"

# 6. Judgement limitations.
J = "use-case-mapping-vep-uc-20261014-"
PP = J + "missense-pp3-bp4-calibrated-evidence-"
PV = J + "protein-variant-effect-prediction-"


def lim(cid, items):
    a = by[cid]["attributes"]
    a["limitations"] = insert_before_last(a["limitations"], items)


lim(PP + "pejaver2022-intervals", [
    "Training variants were removed only for BayesDel, FATHMM, MPC, MutPred2, PolyPhen-2, REVEL and VEST4 (and the "
    "meta-predictors' constituents) where available; no removal is stated for the other six tools (Methods).",
    "Calibration variants may not represent the novel variants to be classified (Stenton et al. 2024, Table 1).",
])
bq = by[PP + "bergquist2025-point-intervals"]["attributes"]
bq["limitations"] = [l for l in bq["limitations"] if l != "MutPred2 and REVEL were co-developed by authors of Bergquist et al. 2025."]
lim(PP + "bergquist2025-point-intervals", [
    "MutPred2 and REVEL were co-developed by authors of Bergquist et al. 2025 (V. Pejaver, P. Radivojac). The BayesDel, "
    "MutPred2, REVEL and VEST4 rows are carried over from Pejaver et al. 2022, whose authors include the developers of all four.",
    "Some of the previously calibrated tools did not reach the likelihood ratios expected for the 3-point intervals (Results, Fig. 1B).",
    "The authors state that this calibration shares the previous study's limitations, including potential circularities and "
    "gene- or disease-specific variability (Discussion).",
    "VARITY was trained on ClinVar; each precomputed score comes from a model that excluded that variant (Materials and Methods).",
])
lim(PP + "pejaver2022-developer-threshold-lr", [
    "Evidence strength was judged on the point estimate of the likelihood ratio, not its confidence bound (Table 3 footnote).",
    "Labels are ClinVar classifications, which the authors assume were not driven by computational evidence (Stenton et al. 2024, Table 1).",
])
PG_EXTRA = [
    "Evolutionary conservation is one of the criteria used to classify ClinVar variants, so even zero-shot models are not free "
    "of circularity (ProteinGym paper, Limitations).",
    "Per-protein AUC averaged over proteins does not test whether scores are comparable across genes, which genome-wide "
    "thresholds assume.",
    "The ProteinGym paper describes the 2023 clinical sets; whether the sets behind the 144fe22 files are unchanged is not stated.",
]
lim(PP + "proteingym-clinical-zero-shot-substitutions-auc-144fe22", PG_EXTRA)
lim(PP + "proteingym-clinical-supervised-substitutions-auc-144fe22", PG_EXTRA)
BRCA_SCOPE = ("BRCA1 and BRCA2 are excluded from this use case because an expert-panel specification sets their thresholds; "
              "this protocol shows how the genome-wide thresholds behave in one well-studied gene, not in genes without a "
              "specification.")
for k in ("ramadane2025-pp3-bp4", "enigma-brca1-generic", "enigma-brca2-generic"):
    lim(PP + k, [BRCA_SCOPE])
DMS_TRAINED_OLD = "Several VEPs were trained on DMS data"
DMS_TRAINED = ("Five VEPs were trained on DMS data (Envision, CPT-1, DeMaSk, VARITY_R, VARITY_ER); the authors excluded their "
               "results for the proteins used to train them (Table S2), but other methods may have been tuned against DMS data "
               "without direct training, for example ESM-1v's model selection (Results, Discussion).")
for k in ("dms-all", "dms-direct", "dms-indirect", "dms-snv", "dms-snv-filled"):
    a = by[PV + "livesey2025-" + k]["attributes"]
    n = sum(l.startswith(DMS_TRAINED_OLD) for l in a["limitations"])
    assert n == 1
    a["limitations"] = [DMS_TRAINED if l.startswith(DMS_TRAINED_OLD) else l for l in a["limitations"]]
lim(PV + "rewire-proteingym-v1-3-dms-substitutions", [
    "Some leaderboard models were developed by ProteinGym's authors (for example EVE, Tranception and TranceptEVE).",
    "Assays come from proteins of many organisms; results for human proteins alone are not given in this summary.",
])

# 7. Key order: normalizeAttributes keeps missing_metadata sorted, so the stored record must be too.
for r in records:
    mm = r["attributes"].get("missing_metadata")
    if isinstance(mm, dict):
        r["attributes"]["missing_metadata"] = dict(sorted(mm.items()))

# 8. reviewed_evaluations for every judgement: all evaluations on the protocol, in the batch or the store.
store_evals = [json.loads(l) for f in sorted(glob.glob(str(REPO / "data/evidence/evaluations/*.jsonl"))) for l in open(f)]
all_evals = store_evals + [r for r in records if r["kind"] == "evaluation"]


def evals_on(protocol):
    return sorted({e["id"] for e in all_evals
                  if any(l["relation"] == "assessment" and l["target_id"] == protocol for l in e["links"])})


# 9. Statuses and review objects.
PEJ_SHA = by[P + "source-pejaver2022"]["attributes"]["artifact_sha256"]
BERG_SHA = by[P + "source-bergquist2025"]["attributes"]["artifact_sha256"]
VALUE_NOTE = ("Re-downloaded the source and matched the pinned SHA-256 (PMC page after blanking the two per-request tokens). "
              "review/check_values.py, written independently of the extractor, re-read the table and checked printed and "
              "numeric value, locator, metric, qualifier, unit, unit_detail, direction, uncertainty and the linked "
              "configuration, protocol and dataset; all 173 results matched.")
for r in records:
    a = r["attributes"]
    old = a.get("review") or {}
    review = {"reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "reviewed_at": REVIEWED_AT}  # reviewed_at, not date
    for key in ("artifact_sha256", "retrieval_url"):
        if key in old:
            review[key] = old[key]
    k = r["kind"]
    if k == "result":
        review.update(method=["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
                      method_note=VALUE_NOTE,
                      note="Extracted by extract/build_batch.py; independently re-checked by review/check_values.py. "
                           "Hand-checked sample in the dated review.")
    elif k == "claim" and a["field"].startswith("links:assessed_by:"):
        a["reviewed_evaluations"] = evals_on(a["value"])
        assert a["reviewed_evaluations"], r["id"]
        review.update(method=["ai-assisted-source-review", "scope-review"],
                      method_note=("Checked the endpoint against the use case's question, inputs, exclusions and output; "
                                   "checked each limitation and number against the cited sources, re-downloaded and "
                                   "hash-matched; listed every evaluation on the protocol in reviewed_evaluations (values of "
                                   "evaluations already in the store were checked by their own independent reviews)."),
                      note=f"Judgement drafted by the extraction agent and revised in review ({REVIEW_DOC}).")
        r["description"] = "Relevance judgement drafted by the extraction agent; independently reviewed, automated review only."
    elif k == "claim":
        review.update(method=["ai-assisted-source-review", "scope-review"],
                      method_note="Checked the method record, the rationale and the cited source lines.",
                      note="Baseline claim checked against docs/use-cases.md (best established pre-machine-learning method).")
    elif k == "use_case":
        review.update(method=["scope-review"],
                      method_note="Checked question, decision, inputs, output, setting, exclusions and evidence gaps against "
                                  "the cited sources and the linked protocols.",
                      note=f"Drafted by the extraction agent; reviewed in {REVIEW_DOC}.")
    elif k in ("method", "model"):
        review.update(method=["source-hash-verification", "ai-assisted-source-review"],
                      method_note="Re-downloaded the primary source and matched its SHA-256; checked name, description, "
                                  "access URLs (each found in the source text), version and method type against it.",
                      note="No fact taken from the AVE predictor list.")
    elif k == "source":
        review.update(method=["source-hash-verification"],
                      method_note="Re-downloaded on 2026-10-14 and matched the pinned SHA-256 (PMC pages after blanking "
                                  "the ncbi_phid and csrfmiddlewaretoken values, checked by an independent normaliser).",
                      note="Hash matches.")
    else:  # benchmark, dataset, protocol, configuration, evaluation
        review.update(method=["source-hash-verification", "ai-assisted-source-review"],
                      method_note="Checked against the Methods, table captions and author lists of the pinned sources.",
                      note="Checked; see the dated review for rulings on origin and carried-over rows.")
    a["review"] = review
    if k in ("method", "model") and r["id"] != P + "method-ea":
        assert r["status"] == "discovered"  # no results: stays discovered
    else:
        r["status"] = "source_checked"

BATCH.write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in records))

cov_path = BATCH_DIR / "coverage.json"
cov = json.loads(cov_path.read_text())
cov["status"] = f"reviewed ({REVIEW_DOC})"
cov_path.write_text(json.dumps(cov, indent=1, ensure_ascii=False) + "\n")
print("signed off", hashlib.sha256(BATCH.read_bytes()).hexdigest())
