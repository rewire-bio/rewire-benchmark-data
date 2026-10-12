"""Deterministic extraction of Table 3 of Xu and Feng 2026 (medRxiv): fine-tuned CpGPT against four classical classifiers
on plasma cfDNA targeted methylation (EpiPanGI Dx, GSE149438).

Usage: python3 -I extract_cpgpt2026.py <download-dir> <batch-dir>

Reads the pinned medRxiv PDF (version 1, 10.64898/2026.07.26.26358979) through its text layer (pdftotext -layout,
poppler 26.08.0, written beside it as cpgpt.txt). Every cell of Table 3 is extracted: mean validation AUROC, test AUROC
and test AUPRC with their 95% CIs for five models. Asserts the caption, header, model labels, footnote and the Results
sentences that quote the same values. Writes batch.jsonl, claims.csv and use-case-links.json.

Corrections from the independent review (docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md) are applied here
and marked with their review item (C1); B.finalize applies the review to every record. medRxiv regenerates this PDF, so
the pinned bytes cannot be downloaded again (review C1): the source keeps the hash of the bytes first read (PINNED_SHA),
and the review blocks carry the hash of the copy the script now reads, whose text layer matched every extracted value.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (Batch, UC_METH, Q_METH, sha, expect)  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
B = Batch("ctdnalit-20261011-cpgpt2026", "2026-10-11")
P = B.P
PDF, TXT = f"{DL}/cpgpt/cpgpt.full.pdf", f"{DL}/cpgpt/cpgpt.txt"
URL = "https://www.medrxiv.org/content/10.64898/2026.07.26.26358979v1.full.pdf"
S = f"{P}-source-preprint"
PINNED_SHA = "369746bfe0117866d294e01f49c6ffbfc2d177e347872030d6233e2e7366961e"  # retrieval 2026-10-11T21:49:59Z
SRC = [S]

lines = open(TXT, encoding="utf-8").read().splitlines()
FLAT = " ".join(" ".join(l.split()) for l in lines)
for frag in ("Three independent train-validation-test partitions were generated using split seeds 42, 123, and 456.",
             "The same split assignments were retained for CpGPT and all classical machine learning models to permit direct performance comparison.",
             "CpGPT was fine-tuned using the pretrained Cancer-100M checkpoint.",
             "cfDNA-derived DMR discovery was conducted using all 300 samples",
             "should not be interpreted as fully independent validation",
             "Because each approximately 10% test partition contained only a small number of",
             "Models were implemented in R using the caret framework",
             "which used targeted bisulfite sequencing to profile plasma cfDNA from patients with gastrointestinal cancers and non-cancer controls",
             "These comparisons were descriptive across the three split-runs.",
             "Mean test AUROCs were 0.9573 for SVM radial, 0.9420 for elastic net, 0.8460 for GBM, and 0.8408 for Random Forest.",
             "All rights reserved. No reuse allowed without permission."):
    expect(frag in FLAT, True, f"preprint sentence: {frag[:60]}")

cap = [i for i, l in enumerate(lines) if l.startswith("Table 3. Performance comparison between CpGPT and classical machine learning baselines")]
expect(len(cap), 1, "Table 3 caption")
expect(lines[cap[0] + 1].split(), ["Model", "Validation", "AUROC1", "Test", "AUROC1", "Test", "AUPRC1"], "Table 3 header")
VAL = re.compile(r"^\s*(?:(CpGPT|SVM radial|Elastic Net|GBM|Random)\s+)?(\d\.\d{4})\s+(\d\.\d{4})\s+(\d\.\d{4})\s*$")
CI = re.compile(r"^\s*(?:(CpGPT|SVM radial|Elastic Net|GBM|Forest)\s+)?\((\d\.\d{4})–(\d\.\d{4})\)\s+\((\d\.\d{4})–(\d\.\d{4})\)\s+\((\d\.\d{4})–(\d\.\d{4})\)\s*$")
body = lines[cap[0] + 2:cap[0] + 20]
rows, cur = [], None
for l in body:
    if l.strip() in ("CpGPT", "SVM radial", "Elastic Net", "GBM"):
        expect(cur is not None and "label" not in cur, True, f"label line {l.strip()!r} placement")
        cur["label"] = l.strip()
        continue
    m = VAL.match(l)
    if m:
        cur = {"vals": m.groups()[1:]}
        if m.group(1):
            cur["label"] = m.group(1)
        rows.append(cur)
        continue
    m = CI.match(l)
    if m:
        cur["ci"] = m.groups()[1:]
        if m.group(1):
            cur["label"] = (cur.get("label", "") + " " + m.group(1)).strip()
        continue
    if l.strip().startswith("Mean and 95% confidence interval"):
        break
expect([r["label"] for r in rows], ["CpGPT", "SVM radial", "Elastic Net", "GBM", "Random Forest"], "Table 3 model labels")
foot = [i for i in range(cap[0], cap[0] + 22) if "Mean and 95% confidence interval (CI) are summarized across three split-runs." in lines[i]]
expect(len(foot), 1, "Table 3 footnote")
expect("The 95% CIs were bounded to the valid metric range of 0 to 1." in lines[foot[0]], True, "Table 3 footnote bound")

# ---------------------------------------------------------------- records
B.source(S, "An Evaluation of DMR-Informed Fine-Tuning of Tissue Array-Pretrained CpGPT for Gastrointestinal Cancer Classification Using cfDNA Targeted Methylation",
         "Primary source retrieved and hashed for the 2026-10-11 plasma ctDNA literature pass.",
         {"url": "https://doi.org/10.64898/2026.07.26.26358979", "artifact_url": URL,
          "version": "medRxiv version 1, posted 2026-07-29", "retrieved_at": "2026-10-11T21:49:59Z", "artifact_sha256": PINNED_SHA,
          "doi": "10.64898/2026.07.26.26358979", "publication_status": "preprint",
          "licence": "All rights reserved; no reuse without permission (medRxiv display licence)", "media_type": "application/pdf",
          "source_locator": "Full artifact bytes; per-record locators on each record",
          "archive_note": "Not archived: no reuse licence. The artifact_sha256 pins the bytes that were read.",
          "hash_scope": ("artifact_sha256 describes one retrieval (2026-10-11T21:49:59Z). medRxiv regenerates this PDF: a reviewer "
                         "download on 2026-10-12 had 2,761,577 bytes, SHA-256 3d37b32e8ff782201ed8ee6677a01808d4f8c86eea70350a530dde7306cab7c9 "
                         "and PDF CreationDate 2026-10-11T20:08:12-07:00. The reviewer's copy's text layer matched every extracted value. "
                         "The licence does not allow archiving."),  # review C1
          "extraction_method": "pdftotext -layout (poppler 26.08.0) text layer, parsed by extract/extract_cpgpt2026.py",
          "scope_note": ("Two authors (University of Southern California; MicroTrace BioAI, Inc.) who did not develop CpGPT. They "
                         "fine-tuned the published CpGPT Cancer-100M checkpoint and built the classical baselines themselves. "
                         "Not peer reviewed.")})
D = f"{P}-data-epipangi-gse149438"
B.rec(D, "dataset", "EpiPanGI Dx plasma cfDNA targeted bisulfite methylation (GSE149438, 300 samples)",
      "Plasma cfDNA targeted bisulfite sequencing of 254 gastrointestinal cancers and 46 non-cancer controls from the EpiPanGI Dx study.", SRC,
      attributes={"version": "GEO GSE149438 as used by Xu and Feng 2026", "accession": "GSE149438", "total": 300, "positives": 254, "negatives": 46,
                  "population": "74 PDAC, 48 ESCC, 43 HCC, 40 CRC, 37 gastric and 12 oesophageal adenocarcinoma cancers, and 46 non-cancer controls",
                  "assay": "Targeted bisulfite sequencing of plasma cfDNA",
                  "scope_note": "Public data generated by the EpiPanGI Dx study, not by the evaluating authors.",
                  "source_locator": "Methods, data sources and study cohorts; Table 1"})
PR = f"{P}-protocol-dmr-informed-split-runs"
LIM = ["The 20,499 candidate CpGs were selected using cancer-versus-control labels of all 300 samples, including the later test partitions, so test performance is not independent of feature selection (stated by the authors).",
       "Each test partition is about 10% of 300 samples (roughly 30, with few controls); means and 95% CIs are over three split-runs only, bounded to 0-1.",
       "Clinically diagnosed gastrointestinal cancers against 46 non-cancer controls; not a screening population.",
       "Preprint, not peer reviewed; the authors call the model comparisons descriptive."]
B.rec(PR, "protocol", "Xu and Feng 2026: GI cancer vs non-cancer on GSE149438, three train-validation-test split-runs, DMR-informed CpG features",
      "Five classifiers on the same 20,499 DMR-informed CpG features and the same three train/validation/test partitions; mean over split-runs.", SRC,
      [{"relation": "uses_data", "target_id": D}],
      {"protocol": ("Three train-validation-test partitions (split seeds 42, 123, 456), identical for all models; model selection on "
                    "training and validation only; AUROC and AUPRC on the held-out test partition, and AUROC on the validation partition, "
                    "summarised as mean and 95% CI over the three split-runs."),
       "version": "Xu and Feng 2026 (medRxiv v1), Table 3; Methods, DMR-informed CpGPT fine-tuning and classical machine learning benchmarks",
       "metric": "auroc", "metric_direction": "higher", "limitations": LIM, "split_seeds": "42, 123, 456",
       "source_locator": "Table 3; Methods; Results"})
M_CPGPT, M_CLASS = f"{P}-method-cpgpt", f"{P}-method-caret-classifiers"
B.method(M_CPGPT, "CpGPT", "Transformer DNA methylation foundation model pretrained on methylation array data (developed by other authors); here fine-tuned for cfDNA classification.",
         SRC, ["foundation_model"], "Introduction; Methods, DMR-informed CpGPT fine-tuning")
B.method(M_CLASS, "Classical classifiers on DMR-informed CpG beta values (caret)", "SVM with radial kernel, elastic net logistic regression, gradient boosting machine and random forest, implemented with the R caret framework.",
         SRC, ["supervised_machine_learning"], "Methods, classical machine learning benchmarks", reported="classical machine learning baselines")
CFG = {"CpGPT": f"{P}-config-cpgpt-cancer-100m-dmr"}
B.configuration(CFG["CpGPT"], "CpGPT Cancer-100M fine-tuned on 20,499 DMR-informed CpGs", M_CPGPT, SRC, "CpGPT",
                "Methods, DMR-informed CpGPT fine-tuning; Table 3", ["foundation_model"],
                "Public pretrained checkpoint (Cancer-100M); fine-tuned weights and code to be released at publication or on request",
                "Learning rate 8e-6, condition-loss weight 3.0, dropout 0.02, weight decay 0.1, batch size 2, up to 4,000 steps, at most 10,000 CpGs per input",
                version="CpGPT Cancer-100M checkpoint", fm=True)
CL = {"SVM radial": "svm-radial", "Elastic Net": "elastic-net", "GBM": "gbm", "Random Forest": "random-forest"}
for label, key in CL.items():
    CFG[label] = f"{P}-config-{key}"
    B.configuration(CFG[label], f"{label} on 20,499 DMR-informed CpGs (caret)", M_CLASS, SRC, label,
                    "Methods, classical machine learning benchmarks; Table 3", ["supervised_machine_learning"],
                    "Built by the authors with open-source R packages; code to be released at publication or on request",
                    f"{label}; training-set median imputation, near-zero-variance filtering, centring and scaling; hyperparameters tuned within training/validation")
REV = B.review(["pdf-text-parse"], PDF, URL, "Extracted by deterministic parse of the PDF text layer (pdftotext -layout) with caption, header, model labels and footnote asserted.")
COLS = [("validation-auroc", "auroc", "validation partition, mean over three split-runs", "Validation AUROC"),
        ("test-auroc", "auroc", "held-out test partition, mean over three split-runs", "Test AUROC"),
        ("test-auprc", "auprc", "held-out test partition, mean over three split-runs", "Test AUPRC")]
for r in rows:
    label = r["label"]
    ev = f"{P}-eval-{'cpgpt' if label == 'CpGPT' else CL[label]}"
    B.evaluation(ev, f"{label} on GSE149438 DMR-informed split-runs (Xu and Feng 2026)", CFG[label], PR, D, SRC,
                 "independent_paper" if label == "CpGPT" else "author_reported",
                 {"dataset_version": "GSE149438 (EpiPanGI Dx), 300 samples", "split": "Three train-validation-test partitions (seeds 42, 123, 456), about 10% test",
                  "population": "254 GI cancers and 46 non-cancer controls", "inputs": "Beta values at 20,499 DMR-informed CpGs",
                  "adaptation": "Fine-tuned (CpGPT) or trained (classical) on each training partition",
                  "metric_implementation": None, "aggregation": "Mean and 95% CI over three split-runs, CI bounded to 0-1", "budget": None},
                 f"Table 3, row '{label}'",
                 missing={"comparison.metric_implementation": {"reason": "unreported"}, "comparison.budget": {"reason": "inapplicable"}})
    for (ck, metric, q, col), v, (lo, hi) in zip(COLS, r["vals"], zip(r["ci"][0::2], r["ci"][1::2])):
        B.result(f"{ev.replace('-eval-', '-result-')}-{ck}", ev, SRC, f"Table 3, row '{label}', column '{col}'", v, metric,
                 f"GI cancer vs non-cancer, {q}", "unitless", REV,
                 uncertainty={"type": "confidence_interval", "lower": lo, "upper": hi, "level": 0.95, "printed": f"({lo}–{hi})",
                              "note": "Across three split-runs, bounded to the valid range 0 to 1 (Table 3 footnote)"})
J = "use-case-mapping-ctdna-lit-20261011-cpgpt2026-split-runs"
B.judgement(J, UC_METH, Q_METH, PR, "proxy",
            "GI cancer vs non-cancer test AUROC and AUPRC (and validation AUROC), mean over three split-runs, for a fine-tuned methylation foundation model (CpGPT) and four classical classifiers on the same targeted bisulfite cfDNA features and partitions",
            ("Compares a methylation foundation model with conventional classifiers on the same plasma cfDNA methylation samples "
             "and splits. Proxy: AUROC without a declared specificity, very small test partitions, feature selection that saw the "
             "test samples, and an unreviewed preprint."),
            ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
             "Do not combine with other protocols' results; assay, cohort and features differ.",
             "Treat differences between models as descriptive: three split-runs of about 30 test samples each."],
            LIM, [(S, "Table 3; Methods; Results")],
            "Add the CpGPT versus classical-classifier comparison on cfDNA targeted methylation (Xu and Feng 2026, medRxiv), retrieved 2026-10-11.",
            "cpgpt2026-gse149438", "CpGPT vs classical classifiers on EpiPanGI Dx cfDNA methylation (Xu and Feng 2026)", "auroc")
B.finalize("The pinned bytes could not be re-verified: medRxiv regenerates this PDF, and a download on 2026-10-12 had a different "
           "SHA-256 (see the source's hash_scope). Compared all 15 Table 3 values and intervals, the asserted sentences and the "
           "footnote with the layout text of that copy, read for this review (the extractor's script was not run); all match.",
           ["pdf-text-parse", "independent-cell-check"], {J: [r["id"] for r in B.records if r["kind"] == "evaluation"]},
           claim_method=["independent-cell-check", "scope-review"], artifact={"artifact_sha256": sha(PDF), "retrieval_url": URL})
B.write(BATCH, [{"use_case": UC_METH, "relation": "assessed_by", "target_id": PR, "judgement_claim": J}])
