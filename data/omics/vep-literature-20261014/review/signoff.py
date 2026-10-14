"""Independent review sign-off for vep-literature-20261014 (2026-10-14).

Usage: python3 -I review/signoff.py <download-dir>

Run review/check_values.py on the same <download-dir> first; this script refuses to run unless
batch.jsonl is the exact extractor output that was checked (commit b0ff762). It applies the
corrections listed in docs/reviews/vep-literature-2026-10-14-review.md, sets every record to
source_checked, writes the review objects and writes batch.jsonl and coverage.json back.
"""
import hashlib
import json
import sys
from pathlib import Path

BATCH_DIR = Path(__file__).resolve().parent.parent
BATCH = BATCH_DIR / "batch.jsonl"
BATCH_SHA_BEFORE = "96b3318f89b08edad03e56cb376f86c7d67bad6a64fc4e286f539052e63299c9"
REVIEWED_AT = "2026-10-14T15:30:00Z"
REVIEW_DOC = "docs/reviews/vep-literature-2026-10-14-review.md"
P = "vep-lit-20261014-"
REVIEWER_NOTE = ("Claude review agent; no human review claimed. Independent Claude (Opus 5.5) review agent, separate from "
                 "the extraction agent that built this batch. Automated review only. Transcription, not reproduction.")

XML_SHA = "1735ee461ef192d9de67c914e9ad73d72d8aa255ea0e3479eb68cd8631d99fa2"
XLSX_SHA = "1b0d792d1a5d3daa95545a7973cabb131c45e42c952e7e5a447a72deef1d1e70"
README_SHA = "321487a8de52c6cfa647a658f61150dd72e0acb0125470524fb94d1f8b23321a"
PG_PAPER_SHA = "a58110e02c3efc8395c534d48630f577c3d45e90d48198b7f9989cf52600b045"
PG_REF_SHA = "a8f498011532a74aa9fe556a50555a75e928c5837d19c06a87592ae04049b308"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12016141/fullTextXML"
README_URL = "https://raw.githubusercontent.com/OATML-Markslab/ProteinGym/144fe22b07dfaeec2b366f2346203a9838a55b4c/README.md"
PG_PAPER = "profile-protocol-proteingym-paper-xml-a58110e0"
PG_REF = "profile-protocol-proteingym-reference-files-dms-substitutions-csv-a8f49801"
PG_PAPER_LOC = ("ProteinGym NeurIPS 2023 paper (PMC10723403): 'Clinical datasets' (zero-shot and supervised benchmarks), "
                "Appendix A.3.2 'Clinical datasets', Appendix 'Limitations' ('Bias', 'Circularity')")

dl = Path(sys.argv[1])
for name, sha in (("PMC12016141.xml", XML_SHA), ("MOESM2.xlsx", XLSX_SHA), ("README.md", README_SHA),
                  ("PMC10723403.xml", PG_PAPER_SHA), ("DMS_substitutions.csv", PG_REF_SHA)):
    assert hashlib.sha256((dl / name).read_bytes()).hexdigest() == sha, f"{name} hash mismatch"
assert hashlib.sha256(BATCH.read_bytes()).hexdigest() == BATCH_SHA_BEFORE, "batch.jsonl is not the reviewed extractor output"
records = [json.loads(line) for line in BATCH.read_text().splitlines()]
by_id = {r["id"]: r for r in records}
assert len(records) == 3364 and all(r["status"] == "needs_review" for r in records)


def links(r, relation):
    return [l["target_id"] for l in r["links"] if l["relation"] == relation]


def assessment(ev):
    return links(ev, "assessment")[0]


# ---- Corrections --------------------------------------------------------------------------------
# 1. ProteinGym leaderboard rows: origin author_reported -> unreported (who generated each model's scores is not stated).
ORIGIN_NOTE = ("Origin set to unreported in review: ProteinGym computed the metric with its own scripts, but the summary "
               "file does not say who generated each model's scores (the README says new baselines are added with scores "
               "supplied by the requester, and others are scored by the maintainers), and most models are not by the "
               "ProteinGym authors. author_reported would wrongly mark most rows as developer-reported; paper_compilation "
               "would wrongly mark them as copied from earlier papers.")
pg_evals = [r for r in records if r["kind"] == "evaluation" and r["id"].startswith(P + "eval-pg-")]
assert len(pg_evals) == 145 and all(r["attributes"]["origin"] == "author_reported" for r in pg_evals)
pg_eval_ids = {r["id"] for r in pg_evals}
for r in pg_evals:
    r["attributes"]["origin"] = "unreported"

# 2. fitCons: the paper does not say which dbNSFP fitCons score was used; do not assign it to integrated_fitCons.
fitcons_cfg = by_id[P + "config-livesey2025-fitcons"]
assert links(fitcons_cfg, "configuration_of") == ["somatic-oncogenicity-20261009-method-integrated-fitcons"]
fitcons_cfg["links"] = [{"relation": "configuration_of", "target_id": P + "method-fitcons"}]
fitcons_cfg["attributes"]["version"] = ("dbNSFP 4.2 (Table S2 'Source'; Methods 'VEPs'); which dbNSFP fitCons score "
                                        "(integrated or one of the cell-type scores) is not stated")
template = by_id[P + "method-igemme"]
fitcons_method = {
    "id": P + "method-fitcons",
    "kind": "method",
    "name": "fitCons (score unspecified)",
    "description": ("fitCons fitness-consequence scores as listed by Livesey and Marsh 2025 (Table S2 'fitCons', population-free, "
                    "from dbNSFP 4.2). dbNSFP carries an integrated fitCons score and cell-type fitCons scores; the paper does "
                    "not say which was used, so this record is not merged with somatic-oncogenicity-20261009-method-integrated-fitcons."),
    "status": "needs_review",
    "facets": {"areas": ["dna-genomes", "proteins-complexes"], "contexts": ["research", "clinical_research"], "method_types": ["specialist"]},
    "source_ids": [P + "source-livesey2025-supplementary-2", P + "source-livesey2025-article"],
    "links": [],
    "attributes": {
        "reported_name": "fitCons",
        "entity_level": "family",
        "source_locator": "Supplementary Material 2, Table S2 row 30 ('fitCons'); Methods 'VEPs'",
        "missing_metadata": {"version": {"reason": "unreported", "note": "Which dbNSFP 4.2 fitCons score was used is not stated"}},
        "review": dict(template["attributes"]["review"]),
    },
}
records.append(fitcons_method)
by_id[fitcons_method["id"]] = fitcons_method

# 3. Clinical protocol: record the 83 versus 85 count discrepancy.
clin = by_id[P + "protocol-livesey2025-clinical-auroc"]
clin["attributes"]["limitations"].append(
    "The text says 83 VEPs were tested (46 clinical-trained, 31 population-free, 6 population-tuned; Results and Fig. 3 legend) and "
    "that CPT-1 outperforms 38 of 48 clinical-trained VEPs (Discussion); Table S8 has 85 rows, including 'CADD' and 'COSMIS', which "
    "have no Table S2 row. The rank scores are those printed against the 85 columns of Table S8; the discrepancy is not explained.")

# 4. ProteinGym clinical protocols: replace the unsourced label sentence with the paper's own description.
PG_LABELS = ("The ProteinGym paper describes the clinical substitution set as ClinVar labels processed as in EVE (Frazer et al. 2021) "
             "and the indel set as short in-frame ClinVar indels (up to 3 amino acids, frameshifts filtered out) with common gnomAD "
             "indels as benign pseudocontrols, because 84% of ClinVar indel annotations are pathogenic. The paper describes the "
             "2023 release; whether the sets behind the 144fe22 files are unchanged is not stated.")
for pid in ("protocol-proteingym-clinical-zero-shot-substitutions-auc-144fe22",
            "protocol-proteingym-clinical-supervised-substitutions-auc-144fe22",
            "protocol-proteingym-clinical-zero-shot-indels-auc-144fe22"):
    a = by_id[P + pid]["attributes"]
    old = "Clinical labels come from ClinVar-type assertions; overlap with any model's training data is not assessed in the file."
    if old in a["limitations"]:
        a["limitations"][a["limitations"].index(old)] = PG_LABELS
    else:  # the supervised protocol states its overlap caveat instead
        a["limitations"].insert(-1, PG_LABELS)
    by_id[P + pid]["source_ids"].append(PG_PAPER)

# 5. Judgements: add the sources' truth-set and circularity caveats and the use case's own exclusions.
TRANSCRIBED = "Transcribed from the source; no reproduction by Rewire and no human scientific review."
LM_CLINICAL = [
    "The negative class is gnomAD v4.1 missense variants not classed pathogenic ('putatively benign'); the authors note it will include "
    "unclassified pathogenic variants, particularly in recessive and incomplete-penetrance genes (Results).",
    "VEPs that use allele frequency as a feature likely benefit from circularity, because frequency is used to classify variants as benign "
    "(Discussion); the gnomAD negative class reduces but does not remove this.",
    "No training variants were removed; the authors attribute most of the clinical-trained VEPs' advantage over the DMS ranking to "
    "circularity (Results, Fig. 4).",
    "AUROC is computed per protein, so the ranking does not test whether scores are comparable across genes.",
    "The text says 83 VEPs; Table S8 prints 85 rows (see the protocol's limitations).",
]
PG_CLINICAL_COMMON = [
    "Clinical labels are biased towards heavily studied proteins, such as well-known cancer genes, and towards European ancestry "
    "(ProteinGym paper, Limitations).",
    "Evolutionary conservation is one of the criteria used to classify ClinVar variants, so even zero-shot models are not free of "
    "circularity (ProteinGym paper, Limitations).",
    "Per-protein AUC averaged over proteins does not test whether scores are comparable across genes.",
    "The ProteinGym paper describes the 2023 clinical sets; whether the sets behind the 144fe22 files are unchanged is not stated.",
]
PG_SUPERVISED = [
    "Performance is reported on all available ClinVar labels, so supervised methods whose training data overlap these labels are "
    "likely overestimated; models trained on population frequencies leak further, because most ClinVar benign labels rest on "
    "observed frequency (ProteinGym paper, 'Clinical datasets', supervised benchmark).",
]
PG_INDEL = [
    "Benign indels are common gnomAD indels used as pseudocontrols, because 84% of ClinVar indel annotations are pathogenic; the task "
    "partly separates pathogenic from common variants (ProteinGym paper, 'Clinical datasets' and Appendix A.3.2).",
    "Only short in-frame indels (up to 3 amino acids) are included; frameshifts were filtered out (Appendix A.3.2).",
]
RARE_EXCLUSION = ("The use case excludes balanced pathogenic/benign classification as a measure of case-level diagnostic performance; "
                  "this protocol is variant-level classification and does not measure recovery of causal variants in cases or review effort.")
BRCA_GENES_PG = "Whether BRCA1 or BRCA2 is among the clinical proteins is not stated in the summary files."
DMS_CROSS_GENE = ("Correlation is assessed within each protein, so the ranking does not test whether scores are comparable across genes; "
                  "the authors report that DMS and clinical rankings agree closely for population-free and population-tuned VEPs "
                  "(Pearson r 0.978 and 0.994) and less for clinical-trained VEPs (Results, Fig. 4).")

UC = "use-case-mapping-vep-lit-20261014-"
judgement_updates = {
    UC + "brca1-brca2-germline-interpretation-livesey2025-clinical-auroc": {
        "replace": {"Clinical-trained VEPs likely inflated by circularity.": None}, "add": LM_CLINICAL},
    UC + "rare-disease-candidate-ranking-livesey2025-clinical-auroc": {
        "replace": {"No training variants were removed; clinical-trained VEPs are likely inflated by circularity (Results, Fig. 4).": None,
                    "The negative class is gnomAD missense variants, not confirmed benign variants.": None},
        "add": LM_CLINICAL + [RARE_EXCLUSION]},
    UC + "brca1-brca2-germline-interpretation-proteingym-clinical-supervised-substitutions-auc-144fe22": {
        "replace": {"Supervised predictors' training labels overlap ClinVar; circularity is not controlled.": None},
        "add": PG_SUPERVISED + PG_CLINICAL_COMMON + [BRCA_GENES_PG], "paper": True},
    UC + "brca1-brca2-germline-interpretation-proteingym-clinical-zero-shot-substitutions-auc-144fe22": {
        "replace": {"Only 13 models listed.": "Only 13 models are listed in this file at 144fe22; the file's completeness is not stated."},
        "add": PG_CLINICAL_COMMON + [BRCA_GENES_PG], "paper": True},
    UC + "rare-disease-candidate-ranking-proteingym-clinical-supervised-substitutions-auc-144fe22": {
        "replace": {"Training-label overlap with the benchmark is not removed, so supervised scores can be inflated by circularity.": None},
        "add": PG_SUPERVISED + PG_CLINICAL_COMMON + [RARE_EXCLUSION], "paper": True},
    UC + "rare-disease-candidate-ranking-proteingym-clinical-zero-shot-substitutions-auc-144fe22": {
        "replace": {}, "add": PG_CLINICAL_COMMON + [RARE_EXCLUSION], "paper": True},
    UC + "rare-disease-candidate-ranking-proteingym-clinical-zero-shot-indels-auc-144fe22": {
        "replace": {}, "add": PG_INDEL + PG_CLINICAL_COMMON + [RARE_EXCLUSION], "paper": True,
        "rationale": ("Proxy: discrimination of pathogenic short in-frame indels bears on prioritising indel candidates, which most "
                      "missense predictors cannot score. It does not measure causal-variant recovery in cases.")},
}
for suffix in ("dms-all", "dms-direct", "dms-indirect", "dms-snv", "dms-snv-filled"):
    judgement_updates[UC + "rare-disease-candidate-ranking-livesey2025-" + suffix] = {"replace": {}, "add": [DMS_CROSS_GENE]}

for cid, upd in judgement_updates.items():
    a = by_id[cid]["attributes"]
    lim = a["limitations"]
    assert lim[-1] == TRANSCRIBED, cid
    for old, new in upd["replace"].items():
        i = lim.index(old)
        if new is None:
            lim.pop(i)
        else:
            lim[i] = new
    lim[-1:-1] = [x for x in upd["add"] if x not in lim]
    if "rationale" in upd:
        assert "frameshift" in a["rationale"]
        a["rationale"] = upd["rationale"]
    if upd.get("paper"):
        by_id[cid]["source_ids"].append(PG_PAPER)
        a["citation_locators"].append({"source_id": PG_PAPER, "locator": PG_PAPER_LOC})

stab = by_id[UC + "protein-stability-rewire-proteingym-v1-3-dms-substitutions"]["attributes"]
old = "The stability assays are mostly one high-throughput proteolysis study; the number of stability assays is not printed in the summary file."
stab["limitations"][stab["limitations"].index(old)] = (
    "The Stability column averages 66 stability assays on 66 proteins, 64 of them from one cDNA-display proteolysis study "
    "(Tsuboyama), including the AMFR assay this use case already cites; it is not independent of that evidence "
    "(reference_files/DMS_substitutions.csv at 144fe22, coarse_selection_type 'Stability').")
stab["constraints"].append(
    "Only the result whose metric_qualifier names Stability assays bears on this use case; the other 17 results on each evaluation "
    "address activity, binding, expression, organismal fitness or mixed endpoints, which the use case excludes.")
by_id[UC + "protein-stability-rewire-proteingym-v1-3-dms-substitutions"]["source_ids"].append(PG_REF)
stab["citation_locators"].append({"source_id": PG_REF, "locator": "reference_files/DMS_substitutions.csv, rows with coarse_selection_type 'Stability' (66 rows; first_author Tsuboyama in 64)"})

# ---- Review objects -----------------------------------------------------------------------------
evals_by_protocol = {}
for r in records:
    if r["kind"] == "evaluation":
        evals_by_protocol.setdefault(assessment(r), []).append(r["id"])

RESULT_NOTE_LM = ("Re-downloaded the Springer workbook and matched the pinned SHA-256. review/check_values.py re-read the sheet XML "
                  "with its own parser and checked printed value (shortest round-trip decimal of the General-format cell), numeric value, "
                  "raw cell, cell reference, row label, column header, metric, qualifier, unit, direction, coverage and the linked "
                  "configuration, protocol and dataset; all 667 workbook results matched.")
RESULT_NOTE_PG = ("Re-downloaded the CSV from raw.githubusercontent.com at 144fe22 and matched the pinned SHA-256. review/check_values.py "
                  "re-read it with the csv module and checked printed and numeric value, CSV line, Model_name, column, metric, "
                  "qualifier, unit, direction, uncertainty and the linked configuration and protocol; all 1,794 ProteinGym results matched.")

for r in records:
    a = r["attributes"]
    old = a.get("review") or {}
    r["status"] = "source_checked"
    review = {"reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE, "reviewed_at": REVIEWED_AT}  # the store keeps reviewed_at, not date
    for key in ("artifact_sha256", "retrieval_url"):
        if key in old:
            review[key] = old[key]
    if r["kind"] == "result":
        workbook = old["artifact_sha256"] == XLSX_SHA
        review.update(method=["source-hash-verification", "deterministic-table-parse", "independent-cell-check"],
                      method_note=RESULT_NOTE_LM if workbook else RESULT_NOTE_PG,
                      note="Extracted by extract/extract_vep.py; independently re-checked by review/check_values.py. "
                           + ("Hand-checked sample in the dated review. " if workbook else "")
                           + ("The source anomaly on this result was checked against Tables S2, S3 and S8 and the text." if "source_anomaly" in a else
                              "Value, metric and identity match the source."))
    elif r["kind"] == "claim" and a["field"].startswith("links:assessed_by:"):
        protocol = a["value"]
        a["reviewed_evaluations"] = sorted(evals_by_protocol[protocol])
        review.update(method=["ai-assisted-source-review", "scope-review"],
                      method_note=("Checked the endpoint against the use case's question, inputs, exclusions and setting in "
                                   "data/entities/use-cases.jsonl; checked each limitation against the cited sources; listed every "
                                   "evaluation on the protocol in reviewed_evaluations after review/check_values.py matched its results."),
                      note=f"Judgement drafted by the extraction agent and revised in review ({REVIEW_DOC}). Proxy is justified; see the dated review.")
        r["description"] = "Relevance judgement drafted by the extraction agent; independently reviewed, automated review only."
    elif r["kind"] == "claim":
        review.update(method=["ai-assisted-source-review", "scope-review"],
                      method_note="Checked against the workbook legends and sheet list, Figures 1-4 and Data availability in the article XML.",
                      note="Correct; the AUPRC ranking is Fig. S5 in Results (Methods says Fig. S4), and both are figure-only.")
    elif r["kind"] == "evaluation":
        review.update(method=["source-hash-verification", "deterministic-table-parse", "scope-review"],
                      method_note="Links, origin and comparison fields checked against the source and the linked protocol; results checked by review/check_values.py.",
                      note=ORIGIN_NOTE if r["id"] in pg_eval_ids else ("Origin independent_paper checked: no VEP reference in the workbook's References sheet "
                                                                       "lists Livesey or Marsh (one DMS dataset, PAX6, reference 5, is co-authored by Livesey)."))
    elif r["kind"] == "source":
        review.update(method=["source-hash-verification", "ai-assisted-source-review"],
                      method_note="Re-downloaded from the recorded URL on 2026-10-14 and matched the SHA-256; URL, version, licence and limitations checked.",
                      note="Hash matches.")
    else:
        review.update(method=["ai-assisted-source-review", "scope-review"],
                      method_note="Descriptive fields, identity links and missing-metadata reasons checked against the cited sources.",
                      note="Checked; see the dated review for rulings on identity and method type.")
    if r["kind"] == "dataset_subset":
        review["artifact_sha256"], review["retrieval_url"] = README_SHA, README_URL  # counts come from the README, not the CSV
    if r["id"] == P + "config-livesey2025-fitcons":
        review["note"] = "Relinked in review from integrated_fitCons to a new family-level fitCons method; the paper does not say which fitCons score was used."
    if r["id"] == P + "method-fitcons":
        review["note"] = "Added in review; see the dated review."
        review["artifact_sha256"] = XLSX_SHA
    a["review"] = review

records.sort(key=lambda r: r["id"])
BATCH.write_text("".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) + "\n" for r in records))

cov_path = BATCH_DIR / "coverage.json"
cov = json.loads(cov_path.read_text())
cov["status"] = "reviewed (docs/reviews/vep-literature-2026-10-14-review.md)"
cov["record_counts"]["method"] = 28
cov["new_ids_added_in_review"] = [P + "method-fitcons"]
cov_path.write_text(json.dumps(cov, indent=2, ensure_ascii=False) + "\n")
print(len(records), hashlib.sha256(BATCH.read_bytes()).hexdigest())
