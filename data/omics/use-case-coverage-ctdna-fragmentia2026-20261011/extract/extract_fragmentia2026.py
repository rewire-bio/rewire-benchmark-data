"""Deterministic extraction of the ULP-WGS fragmentomics comparison in Table S5 of the Fragmentia-AI paper (Cell Reports Medicine 2026).

Usage: python3 -I extract_fragmentia2026.py <download-dir> <batch-dir>

Reads two pinned artifacts:
  - the article, PMC13400139 full-text JATS XML (10.1016/j.xcrm.2026.102866)
  - Document S1 (mmc1.pdf, Figures S1-S9 and Tables S1-S6), through its text layer (pdftotext -layout, poppler 26.08.0,
    written beside it as mmc1.txt)
Every cell of Table S5 is extracted: AUC and the printed p value against Fragmentia-AI for six fragmentomic feature sets
under three classifiers, and the Fragmentia-AI AUC. Asserts the caption, header, feature and classifier labels and the
article sentences that describe the comparison. Writes batch.jsonl, claims.csv and use-case-links.json.

Depends on ctdnalit-20261011-helzer2025-method-griffin (batch use-case-coverage-ctdna-helzer2025-20261011), which must be
added to the store first, and on the stored ctdnafrag-20261009-method-delfi.

Corrections from the independent review (docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md) are applied here
and marked with their review item (A2, F1 to F3); B.finalize applies the review to every record.
"""
import os, re, sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (Batch, UC_FRAG, Q_FRAG, sha, expect)  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
B = Batch("ctdnalit-20261011-fragmentia2026", "2026-10-11")
P = B.P
XML, PDF, TXT = f"{DL}/fraglm/PMC13400139.xml", f"{DL}/fraglm/mmc1.pdf", f"{DL}/fraglm/mmc1.txt"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13400139/fullTextXML"
SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13400139/supplementaryFiles?includeInlineImage=false"
S_ART, S_S1 = f"{P}-source-article", f"{P}-source-document-s1"
SRC = [S_ART, S_S1]
GRIFFIN, DELFI = "ctdnalit-20261011-helzer2025-method-griffin", "ctdnafrag-20261009-method-delfi"

# ---------------------------------------------------------------- article checks
root = ET.parse(XML).getroot()
FLAT = " ".join(" ".join("".join(p.itertext()).split()) for p in root.iter("p"))
for frag in (
        "we conducted a rigorous head-to-head benchmarking study against six established non-mutation-based fragmentomic methods: DELFI, Griffin, FRAGMA, FDI, nucleosome, and subnucleosome features.",
        "we implemented the feature extraction pipelines for each method and applied them to the exact same ULP-WGS training and validation cohorts used for Fragmentia-AI",
        "we trained each feature set using three distinct machine learning architectures: random forest, XGBoost, and deep learning",
        "As detailed in Table S5, Fragmentia-AI achieved an AUC of 0.9561, statistically outperforming every other method tested.",
        "achieving a maximum AUC of 0.935 (via XGBoost); however, Fragmentia-AI still demonstrated a statistically significant improvement over this best-case baseline (p = 0.014)",
        "We trained a separate instance of Fragmentia-AI exclusively on the ULP-WGS dataset",
        "The WGS-trained model achieved an AUC of 0.956 on a held-out WGS validation set (Figure S7B)",
        "While a performance gap exists compared to the same-platform baseline (AUC 0.97 vs. 0.84)",
        "Plasma samples from 1,245 noncancer individuals and 2,004 patients across 17 cancer types were collected and subjected to ULP-WGS (Table S4).",
        "are employees of Nanjing Geneseeq Technology Inc.",
        "the entire architecture, comprising the DNABERT-2 backbone and the attention-based MIL classifier, was trained concurrently in an end-to-end manner"):
    expect(frag in FLAT, True, f"article sentence: {frag[:60]}")

# ---------------------------------------------------------------- Table S5
lines = open(TXT, encoding="utf-8").read().splitlines()
cap = [i for i, l in enumerate(lines) if l.startswith("Table S5. Comparison of Fragmentia-AI with other cfDNA features/models using ULP-WGS data.")]
expect(len(cap), 1, "Table S5 caption")
end = [i for i in range(cap[0], cap[0] + 60) if lines[i].startswith("Table S6.")]
expect(len(end), 1, "Table S6 caption after S5")
body = lines[cap[0] + 1:end[0]]
head = " ".join(" ".join(l.split()) for l in body[:12])
for word in ("P value", "Performance", "Feature", "Model", "(AUC)", "(Compared with", "Fragmentia-AI)"):
    expect(word in head, True, f"Table S5 header word {word!r}")
ROW = re.compile(r"^\s*(?:(Griffin|DELFI|FRAGMA|FDI|Nucleosome|Subnucleosome|cfDNA sequence)\s{2,})?"
                 r"(Random Forest|XGBoost|Deep Learning|Fragmentia-AI)\s{2,}(\d\.\d+)(?:\s{2,}(<?\d\.\d+))?\s*$")
LABEL = re.compile(r"^\s*(Griffin|DELFI|FRAGMA|FDI|Nucleosome|Subnucleosome)\s*$")
rows, labels = [], []
for i, l in enumerate(body):
    m = ROW.match(l)
    if m:
        rows.append({"line": cap[0] + 2 + i, "feature": m.group(1), "model": m.group(2), "auc": m.group(3), "p": m.group(4)})
    elif LABEL.match(l):
        labels.append((len(rows), LABEL.match(l).group(1)))
expect(len(rows), 19, "Table S5 rows")
FEATURES = ["Griffin", "DELFI", "FRAGMA", "FDI", "Nucleosome", "Subnucleosome"]
# each feature label sits on one of its three rows or on a line between them
for k, feat in enumerate(FEATURES):
    blk = rows[3 * k:3 * k + 3]
    expect([r["model"] for r in blk], ["Random Forest", "XGBoost", "Deep Learning"], f"{feat} classifiers")
    inline = [r for r in blk if r["feature"]]
    between = [n for n, f in labels if f == feat]
    expect(([r["feature"] for r in inline] == [feat] and not between) or (not inline and len(between) == 1 and 3 * k < between[0] < 3 * k + 3),
           True, f"{feat} label placement")
    for r in blk:
        r["feature"] = feat
        expect(r["p"] is not None, True, f"{feat} {r['model']} p value")
last = rows[18]
expect((last["feature"], last["model"], last["auc"], last["p"]), ("cfDNA sequence", "Fragmentia-AI", "0.9561", None), "Fragmentia-AI row")

# ---------------------------------------------------------------- sources
B.source(S_ART, "Toward generalizable prediction of cancer signal using a cell-free DNA language model",
         "Primary source retrieved and hashed for the 2026-10-11 plasma ctDNA literature pass.",
         {"url": "https://doi.org/10.1016/j.xcrm.2026.102866", "artifact_url": XML_URL,
          "version": "Cell Reports Medicine, published 2026-06-12; Europe PMC full-text JATS XML of PMC13400139",
          "retrieved_at": "2026-10-11T21:41:11Z", "artifact_sha256": sha(XML), "doi": "10.1016/j.xcrm.2026.102866",
          "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml",
          "source_locator": ("Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> "
                             "element in document order in this JATS XML, front matter included."),  # review A2
          "archive_note": "Not archived in the batch: CC BY-NC-ND 4.0. The artifact_sha256 pins the bytes that were read.",
          "scope_note": ("Developer study: ten authors are employees of Nanjing Geneseeq Technology Inc., which sequenced the samples "
                         "and developed Fragmentia-AI. The baseline feature pipelines were re-implemented by the authors.")})
B.source(S_S1, "Fragmentia-AI paper, Document S1 (Figures S1-S9 and Tables S1-S6)",
         "Supplementary PDF retrieved and hashed for the 2026-10-11 plasma ctDNA literature pass.",
         {"url": "https://doi.org/10.1016/j.xcrm.2026.102866", "artifact_url": SUPP_URL,
          "version": "mmc1.pdf (Document S1) from the Europe PMC supplementary files of PMC13400139",
          "retrieved_at": "2026-10-11T21:41:12Z", "artifact_sha256": sha(PDF), "doi": "10.1016/j.xcrm.2026.102866",
          "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/pdf",
          "artifact_member": "mmc1.pdf",
          "hash_scope": "artifact_sha256 is the mmc1.pdf member of the zip bundle served by Europe PMC; the bundle's own bytes vary between downloads",
          "retrieval_note": "cell.com returned 403 and the PMC bin URL 404 on 2026-10-11; Europe PMC serves the supplementary files as a zip bundle.",
          "archive_note": "Not archived: CC BY-NC-ND 4.0.",
          "extraction_method": "pdftotext -layout (poppler 26.08.0) text layer, parsed by extract/extract_fragmentia2026.py"})

# ---------------------------------------------------------------- dataset, protocol
D = f"{P}-data-ulp-wgs"
B.rec(D, "dataset", "Geneseeq pan-cancer 0.1x ULP-WGS plasma cohort (2,004 cancers, 1,245 non-cancer)",
      "Plasma cfDNA ultra-low-pass whole-genome sequencing at 0.1x of 2,004 patients with 17 cancer types and 1,245 non-cancer individuals.", SRC,
      attributes={"version": "Fragmentia-AI paper Table S4 cohort", "total": 3249, "positives": 2004, "negatives": 1245,
                  "population": ("17 cancer types (breast 97, cervical 80, colorectal 188, oesophageal 95, gastric 128, head and neck 93, kidney 74, "
                                 "liver/cholangiocarcinoma 245, lung 133, melanoma 124, ovarian 242, pancreatic 95, prostate 100, sarcoma 122, "
                                 "thyroid 47, urothelial 78, uterine 63; stages I-IV) and 1,245 non-cancer individuals"),
                  "assay": "PCR-free libraries, ultra-low-pass whole-genome sequencing at 0.1x",
                  "scope_note": "Retrospective, multi-centre, sequenced by Nanjing Geneseeq; data access not stated as public.",
                  "source_locator": "Results P39; STAR Methods P80, P83; Table S4"})
PR = f"{P}-protocol-ulp-wgs-heldout-auc"
LIM = ["Developer study: Geneseeq employees developed Fragmentia-AI, re-implemented every baseline and ran every arm.",
       "The training/validation split of the ULP-WGS cohort and the number of held-out samples are not stated.",
       "The test behind the printed p values is not named.",
       "Retrospective case-control cohort; AUC only, no sensitivity at a fixed specificity and no tumour-fraction stratum for this comparison.",
       "Results P43 calls the same-platform baseline AUC 0.97 in one sentence and 0.956 in another.",
       ("The cohort has 1,245 non-cancer controls, the same number as the training cohort of the Fragmentia-AI WGS paper "
        "(Molecular Biomedicine 2026, Table S1) from the same company, so the two studies may share samples; neither paper says.")]  # review F3
B.rec(PR, "protocol", "Fragmentia-AI paper: ULP-WGS cancer vs non-cancer AUC on a held-out validation set, six feature sets x three classifiers",
      "Fragmentia-AI trained on ULP-WGS and six re-implemented fragmentomic feature sets, each with random forest, XGBoost and a deep learning classifier, scored on the same held-out ULP-WGS validation set.",
      SRC, [{"relation": "uses_data", "target_id": D}],
      {"protocol": ("Feature pipelines for DELFI, Griffin, FRAGMA, FDI, nucleosome and subnucleosome features were re-implemented and "
                    "applied to the same ULP-WGS training and validation cohorts as Fragmentia-AI; each feature set trained with random "
                    "forest, XGBoost and deep learning; cancer vs non-cancer AUC on the held-out validation set; p values against Fragmentia-AI."),
       "version": "Fragmentia-AI paper, Table S5 (Document S1); Results P43-P44",
       "metric": "auroc", "metric_direction": "higher", "limitations": LIM,
       "missing_metadata": {"heldout_validation": {"reason": "unreported", "note": "Split and sample counts not printed"}},
       "source_locator": "Table S5; Results P43-P44"})

# ---------------------------------------------------------------- methods and configurations
FEAT = {  # label: (key, method id or None, name, description, citation)
    "Griffin": ("griffin", GRIFFIN, None, None, "refs 14-18"),
    "DELFI": ("delfi", DELFI, None, None, "refs 14-18"),
    "FRAGMA": ("fragma", None, "FRAGMA (feature set as named in the Fragmentia-AI paper)", None, "refs 14-18"),
    "FDI": ("fdi", None, "FDI (feature set as named in the Fragmentia-AI paper)", None, "refs 14-18"),
    "Nucleosome": ("nucleosome", None, "Nucleosome features (as named in the Fragmentia-AI paper)", None, "refs 14-18"),
    "Subnucleosome": ("subnucleosome", None, "Subnucleosome features (as named in the Fragmentia-AI paper)", None, "refs 14-18"),
}
CLF = {"Random Forest": "random-forest", "XGBoost": "xgboost", "Deep Learning": "deep-learning"}
CFG = {}
for label, (key, mid, name, desc, cite) in FEAT.items():
    if mid is None:
        mid = f"{P}-method-{key}"
        B.method(mid, name, (f"Non-mutation fragmentomic feature set printed as '{label}' and cited among references 14-18 of the "
                             "Fragmentia-AI paper. The paper does not describe how the features are computed."),
                 [S_ART], ["specialist"], f"Results P44 ({cite})", reported=label)
    for clf, ck in CLF.items():
        CFG[(label, clf)] = f"{P}-config-{key}-{ck}"
        B.configuration(CFG[(label, clf)], f"{label} features with {clf} (Fragmentia-AI paper re-implementation)", mid, SRC,
                        f"{label} / {clf}", "Table S5 row; Results P44", ["supervised_machine_learning"],
                        "Re-implemented by the Fragmentia-AI authors; no code or version for the baselines is printed",
                        f"{label} feature extraction from 0.1x ULP-WGS reads; {clf} classifier trained on the ULP-WGS training cohort")
M_FA = f"{P}-method-fragmentia-ai"
B.method(M_FA, "Fragmentia-AI",
         ("cfDNA language model: reference-genome sequences of individual fragments (with 6 bp flanks, at most 250 bp) are BPE-tokenised "
          "and encoded by a DNABERT-2 transformer, and attention-based multiple-instance learning aggregates fragments into a sample-level "
          "cancer score; trained end to end."),
         [S_ART], ["foundation_model"], "STAR Methods P84-P94; Figure 1")
CFG[("cfDNA sequence", "Fragmentia-AI")] = f"{P}-config-fragmentia-ai-ulp-wgs"
B.configuration(CFG[("cfDNA sequence", "Fragmentia-AI")], "Fragmentia-AI trained on ULP-WGS (separate instance)", M_FA, SRC,
                "Fragmentia-AI (cfDNA sequence)", "Table S5 last row; Results P43", ["foundation_model"],
                "Source code deposited on GitHub (yangxu21/Prediction-of-Cancer-Signal-Using-Cell-Free-DNA-Language-Model); trained weights not stated as released",
                ("DNABERT-2 architecture with LoRA on the Wqkv layers, trained end to end with an attention-based MIL classifier on the "
                 "ULP-WGS training cohort; the paper does not name the pretrained weights, if any, that initialise it"),  # review F2
                fm=True, version_note="No commit or weight release is printed for the ULP-WGS instance")

# ---------------------------------------------------------------- evaluations and results
REV = B.review(["pdf-text-parse"], PDF, SUPP_URL,
               "Extracted by deterministic parse of the PDF text layer (pdftotext -layout) with caption, header words, feature and "
               "classifier labels and row count asserted.")
for r in rows:
    key = (r["feature"], r["model"])
    fk = FEAT[r["feature"]][0] if r["feature"] in FEAT else "fragmentia-ai"
    ck = CLF.get(r["model"], "ulp-wgs")
    ev = f"{P}-eval-{fk}-{ck}" if fk != "fragmentia-ai" else f"{P}-eval-fragmentia-ai-ulp-wgs"
    # Review F1: baselines re-implemented by Geneseeq, who did not develop them, are independent_paper.
    B.evaluation(ev, f"{r['feature']} / {r['model']} on the ULP-WGS held-out validation set (Fragmentia-AI paper)", CFG[key], PR, D, SRC,
                 "author_reported" if fk == "fragmentia-ai" else "independent_paper",
                 {"dataset_version": "Fragmentia-AI paper ULP-WGS cohort", "split": None,
                  "population": "Cancer vs non-cancer, held-out ULP-WGS validation set (size not printed)",
                  "inputs": "0.1x ULP-WGS plasma cfDNA reads", "adaptation": "Trained on the ULP-WGS training cohort",
                  "metric_implementation": None, "aggregation": "Single held-out validation set", "budget": None},
                 f"Table S5, row '{r['feature']}' / '{r['model']}' (text layer line {r['line']})",
                 limitations=["Baseline re-implemented and run by the developer of the compared model."] if fk != "fragmentia-ai" else None,
                 missing={"comparison.split": {"reason": "unreported", "note": "Training/validation split of the ULP-WGS cohort not printed"},
                          "comparison.metric_implementation": {"reason": "unreported"}, "comparison.budget": {"reason": "inapplicable"}})
    extra = {"reported_p_value": f"{r['p']}, against Fragmentia-AI (Table S5 column 'P value (Compared with Fragmentia-AI)'; test not named)"} if r["p"] else {}
    B.result(f"{ev.replace('-eval-', '-result-')}-auroc", ev, SRC,
             f"Table S5, row '{r['feature']}' / '{r['model']}', column 'Performance (AUC)'", r["auc"], "auroc",
             "cancer vs non-cancer, held-out ULP-WGS validation set", "unitless", REV, extra=extra)

# ---------------------------------------------------------------- judgement
J = "use-case-mapping-ctdna-lit-20261011-fragmentia2026"
jid = f"{J}-ulp-wgs-heldout"
B.judgement(jid, UC_FRAG, Q_FRAG, PR, "proxy",
            "Cancer vs non-cancer AUC on a held-out 0.1x ULP-WGS validation set for a cfDNA language model and six re-implemented fragmentomic feature sets (DELFI, Griffin, FRAGMA, FDI, nucleosome, subnucleosome), each with three classifiers",
            ("Compares a fragment-level language model with established fragmentomic feature sets on the same plasma WGS samples. "
             "Proxy: AUC only, with no sensitivity at a fixed false-positive rate and no tumour-fraction stratum; the developer "
             "re-implemented and ran every baseline, and the held-out split is not described."),
            ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
             "Do not combine with other protocols' results; the cohort, depth and classifiers differ.",
             "The p values are as printed; the test is not named."],
            LIM, [(S_ART, "Results P39-P44; STAR Methods P80-P94"), (S_S1, "Table S5; Table S4")],
            "Add the ULP-WGS fragmentomics comparison in Table S5 of the Fragmentia-AI paper (Cell Reports Medicine 2026), retrieved 2026-10-11.",
            "fragmentia2026-ulp-wgs", "cfDNA language model vs fragmentomic feature sets on 0.1x ULP-WGS (Fragmentia-AI paper, Table S5)",
            "auroc")
B.finalize("Re-downloaded the pinned artifacts and matched their SHA-256 (the mmc1.pdf member of the Europe PMC bundle); compared "
           "all 19 Table S5 AUCs and 18 p values with a table transcribed for this review from the layout text (the extractor's "
           "script was not run).",
           ["source-hash-verification", "pdf-text-parse", "independent-cell-check"],
           {jid: [r["id"] for r in B.records if r["kind"] == "evaluation"]})
B.write(BATCH, [{"use_case": UC_FRAG, "relation": "assessed_by", "target_id": PR, "judgement_claim": jid}])
