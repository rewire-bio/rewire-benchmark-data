"""Deterministic extraction of the CCGA substudy 1 classifier comparison into a records batch.

Usage: python3 -I extract_ctdna_jamshidi.py <download-dir> <batch-dir>

Reads one pinned PDF through its text layer (pdftotext -layout output beside it):
  Jamshidi et al. 2022, Cancer Cell 40:1537-1549, the publisher PDF deposited at the Francis Crick
  Institute figshare (10.25418/crick.21731870.v1)
  - Table 3: sensitivity at 98% specificity for ten classifiers on the training set (10-fold
    cross-validation) and the independent validation set, with 95% CI and TP/total
  - Results text: cancer signal origin accuracy for three classifiers on 127 jointly detected cancers
Asserts every row label, every value pattern, that each printed percentage matches its TP/total,
and the footnotes and sentences it relies on. Writes batch.jsonl and claims.csv in the store form.
"""
import csv, hashlib, json, os, re, sys
from decimal import Decimal, ROUND_HALF_UP

DL, BATCH = sys.argv[1], sys.argv[2]
P = "ctdnajam-20261010"
UC_METH, UC_FRAG = "use-case-plasma-ctdna-methylation", "use-case-plasma-ctdna-fragmentomics"
DATE = "2026-10-10"
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
records, claim_rows = [], []

PDF, TXT = f"{DL}/jamshidi2022/main.pdf", f"{DL}/jamshidi2022/main.txt"
URL = "https://ndownloader.figshare.com/files/38559380"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def expect(got, value, where):
    if got != value:
        raise SystemExit(f"{where}: expected {value!r}, found {got!r}")


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    records.append({"id": id_, "kind": kind, "name": name, "description": description, "status": status,
                    "facets": FACETS if facets is None else facets, "source_ids": source_ids,
                    "links": links or [], "attributes": attributes or {}})


S = f"{P}-source-jamshidi2022"
size = os.path.getsize(PDF)
rec(S, "source", "Evaluation of cell-free DNA approaches for multi-cancer early detection",
    "Primary source retrieved and hashed for the CCGA substudy 1 follow-up pass.", [],
    attributes={"url": "https://doi.org/10.1016/j.ccell.2022.10.022", "artifact_url": URL,
                "version": ("Cancer Cell 40(12):1537-1549.e12, published 2022-12-12; publisher PDF "
                            "(1-s2.0-S153561082200513X-main.pdf) as deposited by the Francis Crick Institute on figshare, "
                            "10.25418/crick.21731870.v1"),
                "retrieved_at": "2026-10-10T06:05:17Z", "artifact_sha256": sha(PDF), "publication_status": "peer_reviewed",
                "licence": "CC-BY-NC-ND-4.0", "media_type": "application/pdf", "doi": "10.1016/j.ccell.2022.10.022",
                "source_locator": "Full artifact bytes; per-record locators on each record",
                "access_and_reuse": "CC BY-NC-ND 4.0, printed on the first page of the article and on the figshare record.",
                "archive_note": (f"Not archived in the batch: the licence forbids commercial reuse and the PDF is {size:,} bytes. "
                                 "The artifact_sha256 pins the bytes that were read; figshare's computed MD5 for the file is "
                                 "6f51c7dc523d231b6c0ce268257bd3b8."),
                "retrieval_note": ("Not in PMC; Europe PMC has no full text or supplementary files; cell.com and ScienceDirect "
                                   "returned 403 and the Elsevier API returned 429. The Crick figshare deposit holds the "
                                   "publisher PDF of the version of record."),
                "extraction_method": "pdftotext -layout text layer, parsed by extract/extract_ctdna_jamshidi.py",
                "scope_note": ("Developer study: most authors are GRAIL employees with equity in Illumina, and several are "
                               "inventors on related GRAIL patent applications (Declaration of interests). All classifiers "
                               "were built and run by GRAIL. Samples are from CCGA (NCT02889978) substudy 1.")})

REVIEW = {"method": ["pdf-text-parse"], "reviewer": ["claude"], "date": DATE,
          "reviewer_note": "Claude (Opus 5.5) extraction agent; extraction record, not an independent review",
          "artifact_sha256": sha(PDF), "retrieval_url": URL,
          "note": "Extracted by deterministic parse of the PDF text layer (pdftotext -layout). Pending independent review."}


def result(id_, eval_id, locator, pv, numeric, metric, qualifier, unit, extra=None, ci=None):
    attrs = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": "higher", "unit": unit,
             "printed_value": pv, "numeric_value": numeric, "source_locator": locator, "review": REVIEW}
    if ci:
        attrs["uncertainty"] = ci
    else:
        attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
    attrs.update(extra or {})
    rec(id_, "result", f"{eval_id.replace(P + '-eval-', '')} {metric}",
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        [S], [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claim_rows.append([id_, S, locator, pv, "result"])


def claim(id_, subject, field, value, locator):
    rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", [S],
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator,
         "review": {**REVIEW, "method": ["transcription"],
                    "note": "Hand transcription from the source text. Pending independent review."}}, facets={})
    claim_rows.append([id_, S, locator, value, "claim"])


txt = open(TXT, encoding="utf-8").read()
lines = txt.splitlines()


FLAT = " ".join(txt.split())


def has(fragment, where):
    """Sentence check on the text layer with line breaks collapsed to single spaces."""
    expect(fragment in FLAT, True, where)


# ================================================================ Table 3
cap = [i for i, l in enumerate(lines) if l.startswith("Table 3. Performance metrics at 98% specificity for prototype cancer signal detection classifiers")]
expect(len(cap), 1, "Table 3 caption")
foot = [i for i in range(cap[0], cap[0] + 40) if lines[i].startswith("CI, confidence interval; N/A, not available")]
expect(len(foot), 1, "Table 3 footnote start")
PCT = r"(\d+(?:\.\d+)?)%([bc]?) \((\d+(?:\.\d+)?)%–(\d+(?:\.\d+)?)%\)"
ROW = re.compile(r"^(?:(WGBS|Targeted sequencing|WGS|All three|None)\s{2,})?\s*(.+?)\s{2,}(?:" + PCT + r"|N/Ad)\s{2,}(?:(\d+)/(\d+)|N/Ad)\s{2,}" + PCT + r"\s{2,}(\d+)/(\d+)$")
rows, assay = [], None
for l in lines[cap[0] + 1:foot[0]]:
    m = ROW.match(l.strip())
    if not m:
        continue
    g = m.groups()
    assay = g[0] or assay
    rows.append({"assay": assay, "label": g[1], "train": None if g[2] is None else (g[2], g[4], g[5]),
                 "train_n": None if g[6] is None else (int(g[6]), int(g[7])), "val": (g[8], g[10], g[11]),
                 "val_mark": g[9], "val_n": (int(g[12]), int(g[13]))})
LABELS = ["WG methylation", "SNV", "SNV-WBC", "SCNA", "SCNA-WBC", "fragment endpoints", "fragment lengths",
          "allelic imbalance", "pan-feature", "clinical data"]
expect([r["label"] for r in rows], LABELS, "Table 3 row labels")
expect([r["assay"] for r in rows], ["WGBS", "Targeted sequencing", "Targeted sequencing", "WGS", "WGS", "WGS", "WGS", "WGS",
                                    "All three", "None"], "Table 3 assay column")
expect([r["label"] for r in rows if r["train"] is None], ["pan-feature"], "Table 3 rows without training values")


def pct_matches(printed, num, den):
    p = Decimal(printed)
    places = Decimal(1).scaleb(p.as_tuple().exponent)
    return (Decimal(num * 100) / Decimal(den)).quantize(places, rounding=ROUND_HALF_UP) == p


for r in rows:
    for key, nkey in (("train", "train_n"), ("val", "val_n")):
        if r[key] is not None:
            expect(pct_matches(r[key][0], *r[nkey]), True, f"Table 3 {r['label']} {key} percentage against TP/total")
    expect(r["val_n"][1], 457 if r["label"] == "clinical data" else 464, f"Table 3 {r['label']} validation denominator")
    if r["train_n"]:
        expect(r["train_n"][1], 815 if r["label"] == "clinical data" else 833, f"Table 3 {r['label']} training denominator")
FOOT = " ".join(l.strip() for l in lines[foot[0]:foot[0] + 16])
for frag in ("the observed specificity for the training set was 97.9% (true negatives/total non-cancer samples: 548/560)",
             "(98.0% [540/551e] for the clinical data classifier)",
             "The observed specificity for the validation set was 97.8% for all classifiers (354/362 for all but clinical data; 350/358e for the clinical data classifier)",
             "p < 0.0001. The p values were computed only for the validation set and represent paired McNemar analysis versus WG methylation.",
             "p < 0.01."):
    expect(frag in FOOT, True, f"Table 3 footnote: {frag[:50]}")
for frag in ("A 98% specificity cutoff was determined post hoc for the training and validation sets.",
             "CIs shown in figures were binomial estimates of the 95% CIs computed using the standard Clopper-Pearson",
             "The fragment endpoint, fragment length, allelic imbalance, and pan-feature cancer signal detection classifiers, as well as the CSO classifiers were developed after",
             "The same ten-fold cross-validation strategy was used during training for all classifiers."):
    has(frag, f"Methods sentence: {frag[:50]}")

# ================================================================ cancer signal origin (Results text)
for frag in ("classifier accurately predicted CSO for 75% (95/127) of jointly",
             "rately predicted CSO for 41% (52/127) and 35% (44/127) of can-",
             "cancer signal detection classifiers (n = 127; see STAR Methods)",
             "where all three representative cancer signal detection classifiers detected a cancer signal at 98% specificity",
             "of the cancer versus non-cancer signal detection classifiers (WG methylation, SNV, and SCNA-WBC)",
             "stomach, thyroid, and uterus cancers, and was counted as a correct result in the calculation of accuracy and precision for the"):
    has(frag, f"CSO sentence: {frag[:50]}")
CSO = [("wg-methylation", "75%", 95), ("scna", "41%", 52), ("snv-wbc", "35%", 44)]
for _, pv, k in CSO:
    expect(pct_matches(pv[:-1], k, 127), True, f"CSO {pv} against {k}/127")

# ================================================================ datasets
D_TRAIN, D_VAL, D_CSO = f"{P}-data-ccga1-training", f"{P}-data-ccga1-validation", f"{P}-data-ccga1-validation-jointly-detected"
CCGA_SCOPE = ("Case-control: participants with cancer were enrolled before treatment, and non-cancer participants were enrolled "
              "from the same centres or regions in a ratio of about 3 to 7. Participants were randomised to training and "
              "validation sets in sequencing batches; the first four batches were women only. All assays were run on "
              "contemporaneous blood samples from the same participants. Sequencing data are not public.")
rec(D_TRAIN, "dataset", "CCGA substudy 1 training set (1,414 analysable participants)",
    "Training set of the first Circulating Cell-free Genome Atlas substudy, scored by 10-fold cross-validation.", [S],
    attributes={"version": "CCGA (NCT02889978) substudy 1, training set",
                "population": "1,414 analysable participants: 854 with cancer and 560 without cancer (Table 1); Table 3 scores 833 cancers and 560 non-cancers",
                "total": 1414, "positives": 854, "negatives": 560, "scope_note": CCGA_SCOPE,
                "source_locator": "Figure 1; Table 1; Table 3 and its footnote a; STAR Methods, study design and participants"})
rec(D_VAL, "dataset", "CCGA substudy 1 validation set (847 analysable participants)",
    "Independent validation set of the first Circulating Cell-free Genome Atlas substudy.", [S],
    attributes={"version": "CCGA (NCT02889978) substudy 1, validation set",
                "population": "847 analysable participants: 485 with cancer and 362 without cancer (Table 1); Table 3 scores 464 cancers and 362 non-cancers",
                "total": 847, "positives": 485, "negatives": 362, "scope_note": CCGA_SCOPE,
                "source_locator": "Figure 1; Table 1; Table 3 and its footnote a"})
rec(D_CSO, "dataset", "CCGA substudy 1 validation cancers detected by all three representative classifiers (127)",
    "Validation-set cancers that the three representative detection classifiers all called positive at 98% specificity.", [S],
    attributes={"version": "CCGA (NCT02889978) substudy 1, validation set subset",
                "population": "127 cancers, solid and haematologic",
                "total": 127,
                "scope_note": ("A subset chosen by detection, so it is enriched for high tumour fraction. The Results name the three "
                               "classifiers as WG methylation, SCNA and SNV-WBC; the Methods name them as WG methylation, SNV and "
                               "SCNA-WBC."),
                "source_locator": "Results, cancer signal origin prediction; STAR Methods, CSO prediction"})

# ================================================================ methods and configurations
CLS = {
    "WG methylation": ("wg-methylation", "WGBS", "Whole-genome methylation classifier (GRAIL prototype)",
                       "Removes fragments with methylation states common in non-cancer samples, keeps mostly hyper- or hypo-methylated fragments with at least 5 CpGs, scores their cancer likelihood by genome location, and classifies the top-ranked fragment likelihoods with kernel logistic regression.",
                       "STAR Methods, WGBS: WG methylation classifier"),
    "SNV": ("snv", "Targeted sequencing", "Small somatic variant classifier on a 507-gene panel (GRAIL prototype)",
            "Gene-level counts of variants expected to disrupt function and panel copy number, classified by elastic net logistic regression.",
            "STAR Methods, TS: SNV and SNV-WBC classifiers"),
    "SNV-WBC": ("snv-wbc", "Targeted sequencing", "Small somatic variant classifier with matched white-blood-cell background removal (GRAIL prototype)",
                "As the SNV classifier, after removing variants also found in the participant's white blood cells (clonal haematopoiesis).",
                "STAR Methods, TS: SNV and SNV-WBC classifiers"),
    "SCNA": ("scna", "WGS", "Somatic copy number classifier (GRAIL prototype)",
             "Read depth in 100 kb bins, normalised against technical controls and GC corrected, classified by a convolutional neural network.",
             "STAR Methods, WGS: SCNA and SCNA-WBC classifiers"),
    "SCNA-WBC": ("scna-wbc", "WGS", "Somatic copy number classifier with matched white-blood-cell correction (GRAIL prototype)",
                 "As the SCNA classifier, with white-blood-cell WGS at the same depth used to remove clonal haematopoiesis noise.",
                 "STAR Methods, WGS: SCNA and SCNA-WBC classifiers"),
    "fragment endpoints": ("fragment-endpoints", "WGS", "Fragment endpoint classifier (GRAIL prototype)",
                           "Counts of short (50-140 bp) fragments ending at cancer-enriched genome positions, found by hierarchical Bayesian modelling of non-cancer endpoint rates, classified by logistic regression.",
                           "STAR Methods, WGS: Fragment endpoints classifier"),
    "fragment lengths": ("fragment-lengths", "WGS", "Fragment length classifier (GRAIL prototype)",
                         "Per-bin (100 kb) geometric mean of the fragment-length likelihood ratio of cancer to non-cancer, normalised and GC corrected, classified by logistic regression on principal components.",
                         "STAR Methods, WGS: Fragment lengths classifier"),
    "allelic imbalance": ("allelic-imbalance", "WGS", "Allelic imbalance classifier (GRAIL prototype)",
                          "Deviation of observed allele counts from phased-haplotype expectations in 100 kb bins, summarised to chromosome arms and classified.",
                          "STAR Methods, WGS: Allelic imbalance classifier"),
    "pan-feature": ("pan-feature", "All three", "Pan-feature classifier over all cfDNA classifier scores (GRAIL prototype)",
                    "Gradient-boosted decision trees (XGBoost) over the output scores of the nine cfDNA feature classifiers, excluding the clinical classifier.",
                    "STAR Methods, Pan-feature classifier"),
    "clinical data": ("clinical-data", "None", "Clinical risk-factor classifier (no cfDNA)",
                      "Logistic regression on age, smoking status and family history of breast and ovarian cancer; a benchmark without cfDNA.",
                      "STAR Methods, Clinical classifier"),
}
ASSAY = {"WGBS": "Whole-genome bisulfite sequencing of cfDNA, about 30x",
         "Targeted sequencing": "Targeted sequencing of 507 genes in cfDNA (60,000x raw, 3,000x unique depth)",
         "WGS": "Whole-genome sequencing of cfDNA, about 30x",
         "All three": "Scores from the WGBS, targeted sequencing and WGS classifiers",
         "None": "Clinical data only"}
WBC = {"SNV-WBC": "; matched white-blood-cell targeted sequencing", "SCNA-WBC": "; matched white-blood-cell WGS at about 30x"}
CFG = {}
for label, (key, assay, name, desc, loc) in CLS.items():
    mid = f"{P}-method-{key}"
    rec(mid, "method", name, desc, [S],
        attributes={"reported_name": label, "entity_level": "method", "source_locator": loc,
                    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; settings are on configurations"}}},
        facets={**FACETS, "method_types": ["supervised_machine_learning"]})
    CFG[label] = f"{P}-config-{key}"
    rec(CFG[label], "configuration", f"{name}, CCGA substudy 1", "Configuration as run in the cited comparison.", [S],
        [{"relation": "configuration_of", "target_id": mid}],
        {"reported_name": label, "foundation_model_eligible": False, "source_locator": f"Table 2; {loc}",
         "parameters": ASSAY[assay] + WBC.get(label, ""),
         "missing_metadata": {"version": {"reason": "unreported", "note": "Prototype classifier; no release or commit is printed"}}},
        facets={**FACETS, "method_types": ["supervised_machine_learning"]})

# ================================================================ protocols
COMMON_LIM = [
    "Developer study: GRAIL designed the assays and classifiers, ran every arm, and reports the comparison.",
    "The 98% specificity threshold was set post hoc within each set, including the validation set, so it is not a threshold locked before validation.",
    "Case-control enrolment of clinically diagnosed cancers and matched non-cancer participants, not an intended-use screening population.",
    "Prototype assays; the targeted methylation test developed afterwards is a different assay and is not scored here.",
    "The fragment endpoints, fragment lengths, allelic imbalance and pan-feature classifiers were developed after validation blinding was lifted; the other classifiers were blinded.",
    "Table 3 scores 833 training and 464 validation cancers, against 854 and 485 analysable cancers in Table 1; the source does not explain the 21-sample difference in each set.",
    "Specificity was 97.9% (548/560) in training and 97.8% (354/362) in validation for every cfDNA classifier, slightly below the 98% target.",
]
PR_VAL, PR_TRAIN, PR_CSO = f"{P}-protocol-ccga1-validation-sens-98spec", f"{P}-protocol-ccga1-training-cv-sens-98spec", f"{P}-protocol-ccga1-validation-cso-accuracy"
METRIC_DEF = ("Share of cancer participants called positive at the score threshold that gives 98% specificity among the "
              "non-cancer participants of the same set. 95% CIs are Clopper-Pearson.")
rec(PR_VAL, "protocol", "CCGA substudy 1 validation set: cancer signal sensitivity at 98% specificity",
    "Ten classifiers trained on the training set and applied once to the independent validation set; sensitivity at a post hoc 98% specificity threshold.",
    [S], [{"relation": "uses_data", "target_id": D_VAL}],
    {"protocol": ("Each classifier is trained on the whole training set and locked, then scored on the 847-participant "
                  "validation set. The threshold is set post hoc to give 98% specificity in the validation non-cancer "
                  "participants. Paired McNemar tests compare each classifier with WG methylation on the same samples."),
     "version": "Jamshidi et al. 2022, Table 3 (validation columns); STAR Methods, statistical analysis and performance comparison",
     "metric": "sensitivity-at-98-percent-specificity", "metric_direction": "higher", "unit": "percent",
     "metric_definition": METRIC_DEF, "limitations": COMMON_LIM,
     "source_locator": "Table 3 and footnotes; STAR Methods, quantification and statistical analysis"})
rec(PR_TRAIN, "protocol", "CCGA substudy 1 training set: cancer signal sensitivity at 98% specificity under 10-fold cross-validation",
    "Nine classifiers scored on held-out folds of the training set; sensitivity at a post hoc 98% specificity threshold.",
    [S], [{"relation": "uses_data", "target_id": D_TRAIN}],
    {"protocol": ("10-fold cross-validation on the 1,414-participant training set; held-out fold scores are pooled and the "
                  "threshold set post hoc to give 98% specificity in the training non-cancer participants. The pan-feature "
                  "classifier has no training-set value."),
     "version": "Jamshidi et al. 2022, Table 3 (training columns)",
     "metric": "sensitivity-at-98-percent-specificity", "metric_direction": "higher", "unit": "percent",
     "metric_definition": METRIC_DEF,
     "limitations": COMMON_LIM + ["Cross-validated within the set used to design the classifiers; the fragment endpoint threshold tier was itself chosen to maximise sensitivity at 98% specificity in these folds."],
     "source_locator": "Table 3; STAR Methods, classifier descriptions"})
rec(PR_CSO, "protocol", "CCGA substudy 1 validation set: cancer signal origin accuracy among jointly detected cancers",
    "Three origin classifiers, one per assay, scored on the 127 validation cancers detected by all three representative detection classifiers.",
    [S], [{"relation": "uses_data", "target_id": D_CSO}],
    {"protocol": ("Each origin classifier predicts one of 13 labels (breast; cervix; colon/rectum; oesophagus; head/neck; "
                  "liver/bile duct/gallbladder; lung; lymphoma; plasma cell neoplasm; ovary; pancreas; kidney; other) for "
                  "the 127 jointly detected validation cancers. Accuracy is the share of correct labels."),
     "version": "Jamshidi et al. 2022, Results (cancer signal origin prediction), Figure 4; STAR Methods, CSO prediction",
     "metric": "accuracy", "metric_direction": "higher", "unit": "percent",
     "metric_definition": "Share of the 127 cancers whose predicted origin label matches the clinical diagnosis; a prediction of 'other' counts as correct for anus, unknown primary, melanoma, stomach, thyroid and uterus cancers.",
     "limitations": ["Developer study; origin classifiers were developed after validation blinding was lifted and are described as post hoc.",
                     "Scored only on cancers detected by all three detection classifiers, so the set favours high tumour fraction and contains no non-cancer participants.",
                     "The label 'other' covers six cancer types and counts as correct for them.",
                     "The Results and the Methods name different classifier triples for defining the jointly detected set (SCNA and SNV-WBC against SNV and SCNA-WBC).",
                     "No confidence interval is printed for these accuracies."],
     "source_locator": "Results, cancer signal origin prediction; Figure 4; STAR Methods, CSO prediction"})
claim(f"{P}-claim-observed-specificity", PR_VAL, "observed_specificity",
      "At the 98% target the observed specificity was 97.9% (548/560) in training and 97.8% (354/362) in validation for every "
      "cfDNA classifier; for the clinical data classifier it was 98.0% (540/551) and 97.8% (350/358), with fewer participants "
      "because of a missing clinical variable.", "Table 3 footnotes a and e")
claim(f"{P}-claim-targeted-methylation-lod", PR_VAL, "related_result",
      "Per-classifier clinical limits of detection (cTAF at 50% detection, 98% specificity) are shown only in Figure 3 and Figure "
      "S2. The text gives one value: the later targeted methylation test, on 559 solid-cancer participants of the second CCGA "
      "substudy validation set, had a clinical LOD of 1.3 x 10^-4 cTAF at 98% specificity (3.1 x 10^-4 at its reported 99.3% "
      "specificity), described as almost an order of magnitude better than the top classifiers here. That is a different "
      "assay on different samples and is not stored as a result.", "Results, clinical LOD from the second CCGA substudy; Figure 3 legend")
claim(f"{P}-claim-ctaf-predictor", PR_VAL, "headline_finding",
      "In a multivariate analysis of detection against log10(cTAF), cancer type and clinical stage, cTAF was the only significant "
      "predictor of classifier performance; without cTAF, stage became significant. cTAF accounted for 72% of the variance in "
      "WG methylation classifier scores.", "Results, cTAF; Table S1 and Figure S7 (supplement not extracted)")


def evaluation(id_, label, protocol, dataset, locator, comparison, lim=None):
    rec(id_, "evaluation", f"{label} on {next(r['name'] for r in records if r['id'] == protocol)}",
        "Published comparison; transcribed, not reproduced.", [S],
        [{"relation": "system", "target_id": CFG[label]}, {"relation": "assessment", "target_id": protocol},
         {"relation": "data", "target_id": dataset}],
        {"origin": "author_reported", "protocol": protocol, "version": "Primary source as retrieved 2026-10-10",
         "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator,
         "limitations": ["Run and reported by the assay developer (GRAIL)."] + (lim or [])})


POSTHOC = {"fragment endpoints", "fragment lengths", "allelic imbalance", "pan-feature"}
for r in rows:
    label, key = r["label"], CLS[r["label"]][0]
    lim = (["Developed after validation blinding was lifted."] if label in POSTHOC else []) + \
          (["Clinical data classifier scores fewer participants because of a missing clinical variable."] if label == "clinical data" else [])
    for split, prot, data, cols, n, pop in (
            ("validation", PR_VAL, D_VAL, r["val"], r["val_n"], "464 cancers and 362 non-cancers" if label != "clinical data" else "457 cancers and 358 non-cancers"),
            ("training", PR_TRAIN, D_TRAIN, r["train"], r["train_n"], "833 cancers and 560 non-cancers" if label != "clinical data" else "815 cancers and 551 non-cancers")):
        if cols is None:
            continue
        ev = f"{P}-eval-{split}-{key}"
        evaluation(ev, label, prot, data, f"Table 3, row '{label}', {split} set columns",
                   {"dataset_version": f"CCGA substudy 1 {split} set", "population": pop,
                    "split": "Independent validation set, classifier locked on the training set" if split == "validation" else "10-fold cross-validation within the training set",
                    "inputs": ASSAY[r["assay"]] + WBC.get(label, ""), "adaptation": "Trained on the CCGA substudy 1 training set",
                    "metric_implementation": "Sensitivity at a post hoc 98% specificity threshold; Clopper-Pearson 95% CI",
                    "aggregation": "Pooled over participants", "budget": None},
                   lim=lim)
        records[-1]["attributes"]["missing_metadata"] = {"comparison.budget": {"reason": "inapplicable"}}
        pv, lo, hi = cols
        extra = {"numerator": n[0], "denominator": n[1]}
        if split == "validation" and label != "WG methylation":
            mark = r["val_mark"]
            extra["reported_p_value"] = {"b": "p < 0.0001", "c": "p < 0.01"}.get(mark, "not marked (not significant at p < 0.01)") + \
                ", paired McNemar test against WG methylation (Table 3 footnotes b and c)"
        printed = f"{pv}%{r['val_mark'] if split == 'validation' else ''} ({lo}%–{hi}%)"
        result(f"{ev.replace('-eval-', '-result-')}-sensitivity", ev,
               f"Table 3, row '{label}', {split} set, sensitivity and TP/total cancer samples {n[0]}/{n[1]}",
               printed, pv, "sensitivity-at-98-percent-specificity", f"{split} set, post hoc 98% specificity threshold", "percent",
               extra=extra, ci={"type": "confidence_interval", "printed": f"{lo}%–{hi}%", "lower": lo, "upper": hi, "level": 0.95,
                                "method": "analytic", "note": "Clopper-Pearson exact binomial interval (STAR Methods, statistical analysis)", "n": n[1]})

CSO_CFG = {"wg-methylation": "WG methylation", "scna": "SCNA", "snv-wbc": "SNV-WBC"}
for key, pv, k in CSO:
    label = CSO_CFG[key]
    ev = f"{P}-eval-cso-{key}"
    evaluation(ev, label, PR_CSO, D_CSO, "Results, cancer signal origin prediction, paragraph 1",
               {"dataset_version": "CCGA substudy 1 validation set, jointly detected cancers", "population": "127 cancers",
                "split": "Independent validation set", "inputs": ASSAY[CLS[label][1]] + WBC.get(label, ""),
                "adaptation": "Separate multinomial origin classifier trained on the training set, using the detection classifier's features",
                "metric_implementation": "Share of correct origin labels; 'other' counted as correct for six cancer types",
                "aggregation": "Pooled over participants", "budget": None},
               lim=["Origin classifier developed after validation blinding was lifted."])
    records[-1]["attributes"]["missing_metadata"] = {"comparison.budget": {"reason": "inapplicable"}}
    result(f"{ev.replace('-eval-', '-result-')}-accuracy", ev, f"Results, cancer signal origin prediction: {pv} ({k}/127)",
           pv, pv[:-1], "accuracy", "cancer signal origin among 127 jointly detected validation cancers", "percent",
           extra={"numerator": k, "denominator": 127,
                  **({"reported_p_value": "p = 8 x 10^-9 against SCNA and p = 6.5 x 10^-12 against SNV-WBC, McNemar test"} if key == "wg-methylation" else {})})

# ================================================================ judgements
J = "use-case-mapping-ctdna-jamshidi-20261010"
OVERLAP = ("The CCGA samples are not public and none of the cohorts behind this use case's existing judgements comes from CCGA, "
           "so the samples do not overlap.")
CONSTRAINTS = ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; cohorts, assays and thresholds differ.",
               "The 98% specificity threshold was set post hoc within each set and is not a locked screening threshold."]


def judgement(short, uc, question, protocol, relevance, endpoint, rationale, limitations, locator, group, title, metric, label, order):
    rec(f"{J}-{short}", "claim", f"Relevance of {protocol} to \"{question}\"", rationale, [S],
        [{"relation": "subject", "target_id": uc}],
        {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance, "endpoint": endpoint,
         "rationale": rationale + " " + OVERLAP, "constraints": CONSTRAINTS, "limitations": limitations,
         "citation_locators": [{"source_id": S, "locator": locator}], "source_locator": f"{S}: {locator}", "revision": 1,
         "reason": "Add the CCGA substudy 1 same-sample comparison of cfDNA classifiers (Jamshidi et al. 2022), retrieved 2026-10-10.",
         "comparison_group": group, "comparison_title": title, "headline_metric": metric,
         "stratum_label": label, "stratum_order": order}, facets={})


QM = "Which measured methylation workflow detects tumour-derived plasma DNA and, where separately supported, identifies tissue of origin?"
QF = "Which fragmentomics workflow detects tumour-derived plasma DNA under realistic low tumour fractions and fixed false-positive constraints?"
G, T = "jamshidi2022-ccga1-detection", "CCGA substudy 1: ten cfDNA classifiers on the same participants at 98% specificity"
SENS = "sensitivity-at-98-percent-specificity"
judgement("meth-training-cv", UC_METH, QM, PR_TRAIN, "direct",
          "Sensitivity (95% CI, TP/total) at 98% specificity under 10-fold cross-validation on 833 cancers and 560 non-cancers for the whole-genome methylation classifier and eight other classifiers on the same participants",
          "Measures the use case's endpoint, all-stage cancer detection sensitivity at a declared specificity on plasma cfDNA, for a whole-genome bisulfite methylation classifier, alongside mutation, copy-number, fragment and clinical classifiers run on the same blood draws.",
          COMMON_LIM, "Table 3, training columns; STAR Methods", G, T, SENS, "Training set, 10-fold cross-validation", 1)
judgement("meth-validation", UC_METH, QM, PR_VAL, "direct",
          "Sensitivity (95% CI, TP/total) at 98% specificity on the independent validation set (464 cancers, 362 non-cancers) for the whole-genome methylation classifier and nine other classifiers, with paired McNemar tests against whole-genome methylation",
          "Measures the use case's endpoint on a held-out set: whole-genome methylation reached 34% (30%-39%) against 16% to 33% for single non-methylation cfDNA classifiers on the same participants. Developer-run, case-control, with a post hoc threshold.",
          COMMON_LIM, "Table 3, validation columns and footnotes", G, T, SENS, "Independent validation set", 2)
judgement("meth-cso", UC_METH, QM, PR_CSO, "proxy",
          "Cancer signal origin accuracy among 127 validation cancers detected by all three representative classifiers, for whole-genome methylation, copy-number and white-blood-cell-corrected variant origin classifiers",
          "A methylation-only tissue-of-origin result on patient plasma, compared with two non-methylation classifiers on the same cancers. Proxy evidence: scored only on cancers already detected by all three classifiers, with a lenient 'other' label, and developed after unblinding.",
          ["Scored only on 127 cancers detected by all three classifiers; no non-cancer participants.",
           "The label 'other' covers six cancer types and counts as correct for them.",
           "The Results and Methods name different classifier triples for the jointly detected set.",
           "Developer study; origin classifiers developed after validation blinding was lifted; no confidence intervals printed."],
          "Results, cancer signal origin prediction; STAR Methods, CSO prediction",
          "jamshidi2022-ccga1-cso", "CCGA substudy 1: cancer signal origin accuracy", "accuracy", "Jointly detected validation cancers", 1)
FRAG_LIM = COMMON_LIM + ["No sensitivity within tumour-fraction strata is printed; per-classifier clinical limits of detection by cTAF are in figures only."]
judgement("frag-training-cv", UC_FRAG, QF, PR_TRAIN, "proxy",
          "Sensitivity (95% CI, TP/total) at 98% specificity under 10-fold cross-validation for the fragment endpoint, fragment length and allelic imbalance classifiers from 30x cfDNA WGS, alongside copy-number, mutation, whole-genome methylation and clinical classifiers on the same participants",
          "Compares two fragmentomic classifiers with other cfDNA features on the same blood draws at a fixed false-positive rate. Proxy evidence: no tumour-fraction-stratified sensitivity is printed, the fragment classifiers were developed after unblinding, and the 98% threshold is post hoc.",
          FRAG_LIM, "Table 3, training columns; STAR Methods", G, T, SENS, "Training set, 10-fold cross-validation", 1)
judgement("frag-validation", UC_FRAG, QF, PR_VAL, "proxy",
          "Sensitivity (95% CI, TP/total) at 98% specificity on the independent validation set for the fragment endpoint (18%) and fragment length (29%) classifiers from 30x cfDNA WGS, against whole-genome methylation (34%) and other classifiers on the same participants",
          "A held-out same-sample comparison of fragmentomic classifiers with other cfDNA features at a fixed false-positive rate. Proxy evidence for the same reasons as the training result: no tumour-fraction strata, post hoc development of the fragment classifiers, post hoc threshold.",
          FRAG_LIM, "Table 3, validation columns and footnotes", G, T, SENS, "Independent validation set", 2)

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
expect(len(ids), len(set(ids)), "duplicate IDs")
with open(os.path.join(BATCH, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(BATCH, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    for row in sorted(claim_rows):
        w.writerow(row)
from collections import Counter
print(Counter(r["kind"] for r in records), len(records))
