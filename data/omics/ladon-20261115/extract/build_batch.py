"""Build data/omics/ladon-20261115/batch.jsonl from extract/figures.json and the decisions below.

Every numeric result comes from extract/figures.json, which parse_figures.py read from the
pdftotext -layout text layer of the pinned Zenodo PDF. Everything else (entities, protocols,
claims) is written here by hand from the same PDF, with a locator on each record.

Usage: python3 -I extract/build_batch.py   (run from data/omics/ladon-20261115)
"""

import json
import os

P = "ladon-20261115"
HERE = os.path.dirname(os.path.abspath(__file__))
FIG = json.load(open(os.path.join(HERE, "figures.json"), encoding="utf-8"))

PDF_SHA = "64edf7c3c956c50a65aa01a0dcaa13f0cfef28ab4373ecfd50c431e67143893c"
PDF_URL = "https://zenodo.org/api/records/24157116/files/Ladon-An-RNA-Foundation-Model-for-Predicting-Patient-Outcomes.pdf/content"
WEB_SHA = "f60c00508f8672048047477beb23b1e2ea9244abb099e863f68f3554ce05c97f"
BLOG_SHA = "53e62f1d679bc8f0063d49d6fd688e7fe7e0a520a4c34ac6c466810185ce0dfc"
FIG06_SHA = "afa0d46855e1c3b15efa9a6cca8c621d4314ad445dd7777216e62c7ac646629f"
RETRIEVED = "2026-11-15T20:29:10Z"
DATE = "2026-11-15"

S_PDF = f"{P}-source-zenodo-pdf"
S_WEB = f"{P}-source-web-report"
S_BLOG = f"{P}-source-blog"
S_FIG06 = f"{P}-source-web-fig06"

REVIEWER_NOTE = ("Claude (Opus 5.5) extraction agent; no human review claimed. Extraction only: a different "
                 "agent reviews this batch.")

AREAS = ["rna-transcriptomes"]
CLIN = ["clinical_research"]
RES = ["research"]

records = []


def rid(*parts):
    return "-".join([P, *parts])


def review(note, method=("pdf-text-parse", "source-hash-verification"), sha=PDF_SHA, url=PDF_URL, method_note=None):
    r = {
        "artifact_sha256": sha,
        "date": DATE,
        "method": list(method),
        "note": note,
        "retrieval_url": url,
        "reviewer": ["claude"],
        "reviewer_note": REVIEWER_NOTE,
    }
    if method_note:
        r["method_note"] = method_note
    return r


FIG_METHOD_NOTE = (
    "The report has no tables; this value is a label printed in a figure (or the caption or prose beside it) and "
    "present in the PDF text layer. Read by extract/parse_figures.py from the pdftotext -layout text layer of the "
    "pinned PDF, with every row label asserted in printed order and, for Figure 2, each value assigned to its panel "
    "by character offset. extract/check_against_web.py compared the value with the number embedded in the web "
    "report's figure (where one exists) after rounding."
)


def add(kind, id_, name, description, attributes, links=(), source_ids=(S_PDF,), facets=None, status="needs_review"):
    rec = {
        "attributes": attributes,
        "description": description,
        "facets": facets if facets is not None else {"areas": AREAS, "contexts": CLIN},
        "id": id_,
        "kind": kind,
        "links": [{"relation": r, "target_id": t} for r, t in links],
        "name": name,
        "source_ids": list(source_ids),
        "status": status,
    }
    records.append(rec)
    return id_


def missing(**kw):
    return {k: {"reason": v[0], "note": v[1]} for k, v in kw.items()}


ACCESS_NOTE = (
    "No model weights, code repository or model licence is published with the report. As checked on 2026-11-15, "
    "the GitHub organisation blankbio lists 0 public repositories and the Hugging Face organisation BlankBio lists 0 "
    "models. The report's conclusion (page 43) and the announcement invite readers to contact Blank Bio to use the "
    "model. Access terms are unresolved; contact the provider."
)

# --------------------------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------------------------
add("source", S_PDF, "Ladon: An RNA Foundation Model for Predicting Patient Outcomes (Zenodo PDF)",
    "The Blank Bio technical report introducing Ladon, a bulk RNA-seq foundation model, and its evaluations on survival, "
    "immunotherapy response, treatment benefit, isoform recovery and cell composition.",
    {
        "url": "https://doi.org/10.5281/zenodo.24157116",
        "retrieval_url": PDF_URL,
        "version": "Zenodo record 24157116 (version DOI 10.5281/zenodo.24157116; concept DOI 10.5281/zenodo.24157115), file "
                   "Ladon-An-RNA-Foundation-Model-for-Predicting-Patient-Outcomes.pdf, 47 pages, dated 12 November 2026",
        "doi": "10.5281/zenodo.24157116",
        "year": 2026,
        "publication_status": "official_project_source",
        "retrieved_at": RETRIEVED,
        "artifact_sha256": PDF_SHA,
        "media_type": "application/pdf",
        "licence": "Copyright (C) 2026 Blank Bio. All rights reserved. (Zenodo record, Rights field)",
        "code_licence": "None stated. The report links no code, weights or model licence.",
        "access_note": "Zenodo access_right is open, which covers downloading this PDF only. " + ACCESS_NOTE,
        "limitations": [
            "Company technical report deposited on Zenodo; not peer reviewed.",
            "The PDF is a print of an interactive web page. Per-trial values, p-values and confidence intervals that the web "
            "version shows on hover or in collapsed data tables are not printed in the PDF.",
            "All rights reserved: the PDF and its text layer are not archived in this repository.",
        ],
        "version_note": "Downloaded twice on 2026-11-15 (about 20:22Z and 20:29Z) with identical bytes; the MD5 matches the "
                        "Zenodo file checksum abc8168cf6059ee806b34ced791434fb. Values were read from a pdftotext 26.08.0 "
                        "-layout text layer, SHA-256 2f5a65a1e6b9830dd2aa1e0155865462c34a58451a230657f697d110b637bd6d.",
        "source_locator": "Whole document; title page (page 1) for authors, date and DOI",
        "review": review("PDF hash checked on two downloads; Zenodo metadata gives no licence field and the record page "
                         "Rights field reads 'Copyright (C) 2026 Blank Bio. All rights reserved.'",
                         method=("source-hash-verification", "automated-source-review")),
    }, source_ids=[S_PDF])

add("source", S_WEB, "Ladon Technical Report (web page)",
    "The interactive web version of the Ladon technical report, whose figures are drawn from data embedded in each figure page.",
    {
        "url": "https://www.blank.bio/ladon-technical-report",
        "version": "Page as served on 2026-11-15; HTTP Last-Modified Sun, 15 Nov 2026 07:37:48 GMT",
        "publication_status": "official_project_source",
        "retrieved_at": RETRIEVED,
        "artifact_sha256": WEB_SHA,
        "media_type": "text/html",
        "licence": "No licence stated on the page.",
        "limitations": [
            "Mutable web page; the hash describes one retrieval, although two retrievals on 2026-11-15 were byte-identical.",
            "Last modified on 15 November 2026, after the 12 November PDF. Its prose carries no number absent from the PDF.",
            "Used only to locate the figure pages; no value is taken from it.",
        ],
        "source_locator": "Whole page; figure iframes under assets/ladon-white-paper/",
        "review": review("Fetched twice with identical bytes. Prose compared with the PDF text layer: no number in the web "
                         "prose is missing from the PDF.", method=("source-hash-verification", "automated-source-review"),
                         sha=WEB_SHA, url="https://www.blank.bio/ladon-technical-report"),
    }, links=[("companion_of", S_PDF)], source_ids=[S_PDF])

add("source", S_BLOG, "Introducing Ladon (Blank Bio announcement)",
    "The Blank Bio announcement post for Ladon, which summarises the technical report and invites readers to contact the company.",
    {
        "url": "https://www.blank.bio/introducing-ladon",
        "version": "Post dated 12 November 2026, as served on 2026-11-15",
        "publication_status": "official_project_source",
        "retrieved_at": RETRIEVED,
        "artifact_sha256": BLOG_SHA,
        "media_type": "text/html",
        "licence": "No licence stated on the page.",
        "limitations": [
            "Mutable web page; the hash describes one retrieval, although two retrievals on 2026-11-15 were byte-identical.",
            "Announcement text; used only for access wording and for statements that differ from the report.",
        ],
        "source_locator": "Whole page",
        "review": review("Fetched twice with identical bytes.", method=("source-hash-verification", "automated-source-review"),
                         sha=BLOG_SHA, url="https://www.blank.bio/introducing-ladon"),
    }, links=[("companion_of", S_PDF)], source_ids=[S_PDF])

add("source", S_FIG06, "Ladon technical report, Figure 6 page (web)",
    "The web page that draws Figure 6 of the Ladon technical report, with the per-trial response AUROCs and comparator notes it embeds.",
    {
        "url": "https://www.blank.bio/assets/ladon-white-paper/fig06-response-prediction.html",
        "version": "Page as served on 2026-11-15",
        "publication_status": "official_project_source",
        "retrieved_at": RETRIEVED,
        "artifact_sha256": FIG06_SHA,
        "media_type": "text/html",
        "licence": "No licence stated on the page.",
        "limitations": [
            "Mutable web asset; the hash describes one retrieval, although two retrievals on 2026-11-15 were byte-identical.",
            "Used only for the comparator notes and row labels in its embedded DATA object, which the PDF does not print. "
            "Its per-trial AUROCs are not stored.",
        ],
        "source_locator": "Embedded DATA object, master.panel_f.rows",
        "review": review("Fetched twice with identical bytes. Read with regular expressions; the page's JavaScript was not executed.",
                         method=("source-hash-verification", "automated-source-review"), sha=FIG06_SHA,
                         url="https://www.blank.bio/assets/ladon-white-paper/fig06-response-prediction.html"),
    }, links=[("companion_of", S_PDF)], source_ids=[S_PDF])

# --------------------------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------------------------
M_LADON = add("model", rid("model-ladon"), "Ladon",
    "Transformer encoder-decoder pretrained by masked token reconstruction on isoform-level bulk RNA-seq profiles, whose "
    "embeddings feed outcome predictors for survival, treatment response and tumour characteristics.",
    {
        "entity_level": "family",
        "reported_name": "Ladon",
        "version": "As described in the 12 November 2026 technical report; no checkpoint, release or version name is given",
        "identity_scope": "Family level. The report evaluates several adaptations of the encoder (supervised mid-training on "
                          "survival or response labels, composition post-training, the pretrained encoder) and, in Figures 20 "
                          "and 21, several model sizes and training steps, without naming any checkpoint.",
        "training_data": "Millions of bulk RNA-seq samples (pages 1 and 2); the corpus, its sources and sample count are not "
                         "listed. Supervised mid-training uses disease stage, age, tumour grade, genomic alterations and "
                         "clinical outcomes (page 11).",
        "access": ACCESS_NOTE,
        "provenance_note": "Developer's own technical report; every result for this model is developer-reported and none is "
                           "reproduced here.",
        "missing_metadata": missing(
            checkpoint_revision=("unreported", "No checkpoint, version or hash is named; results are not assigned to a checkpoint."),
            licence=("unreported", "No model licence is stated. The report itself is 'All rights reserved'. Do not infer an open licence from the report's open download."),
        ),
        "source_locator": "Page 2, 'Introducing Ladon'; page 11, Methods 'Ladon representations'; page 43, Conclusion",
        "review": review("Identity kept at family level because no checkpoint is named."),
    }, facets={"areas": AREAS, "contexts": CLIN, "method_types": ["foundation_model"]})

M_BULKRNABERT = add("model", rid("model-bulkrnabert"), "BulkRNABert",
    "Transformer language model pretrained on bulk RNA-seq gene expression profiles, used to embed tumour transcriptomes for cancer prognosis.",
    {
        "entity_level": "family",
        "reported_name": "BulkRNABert",
        "version": "Published Hugging Face checkpoint (Gélard et al., 2025); the checkpoint name is not printed",
        "provenance_note": "Comparator in the Ladon report, run by Blank Bio with the published checkpoint and input processing.",
        "missing_metadata": missing(
            checkpoint_revision=("unreported", "The report says 'published Hugging Face checkpoint' without naming the repository or revision."),
        ),
        "source_locator": "Page 11, Comparators table, row 'BulkRNABert'; References (Gélard et al., 2025)",
        "review": review("Identity from the comparator table."),
    }, facets={"areas": AREAS, "contexts": RES, "method_types": ["foundation_model"]})

M_BULKFORMER = add("model", rid("model-bulkformer"), "BulkFormer",
    "Large foundation model for bulk transcriptomes whose embeddings are used as features for outcome prediction.",
    {
        "entity_level": "family",
        "reported_name": "BulkFormer",
        "version": "147M checkpoint (Kang et al., 2026)",
        "provenance_note": "Comparator in the Ladon report, run by Blank Bio.",
        "missing_metadata": missing(
            checkpoint_revision=("unreported", "Only the parameter count (147M) is printed; no repository or revision."),
        ),
        "source_locator": "Page 11, Comparators table, row 'BulkFormer'; References (Kang et al., 2026)",
        "review": review("Identity from the comparator table."),
    }, facets={"areas": AREAS, "contexts": RES, "method_types": ["foundation_model"]})

M_BMR = add("model", rid("model-bmretriever-7b"), "BMRetriever-7B",
    "Biomedical text embedding model with about seven billion parameters, used here to encode baseline clinical covariates written as text.",
    {
        "entity_level": "family",
        "reported_name": "BMRetriever-7B",
        "version": "BMRetriever-7B; no revision printed",
        "provenance_note": "Used by Blank Bio as the clinical-covariate encoder, alone as a baseline and combined with Ladon.",
        "missing_metadata": missing(
            checkpoint_revision=("unreported", "No repository or revision is printed, and the report gives no reference for BMRetriever."),
        ),
        "source_locator": "Page 11, Methods 'Clinical covariates'",
        "review": review("Identity from the Methods paragraph."),
    }, facets={"areas": AREAS, "contexts": CLIN, "method_types": ["foundation_model"]})

# --------------------------------------------------------------------------------------------
# Ladon configurations
# --------------------------------------------------------------------------------------------
NO_CKPT = missing(checkpoint_revision=("unreported", "The report names no checkpoint for this adaptation."))


def ladon_config(slug, name, description, version, head, training_setting, locator, extra=None, limitations=(), uses=()):
    attrs = {
        "configuration_type": "paper_evaluation",
        "reported_name": "Ladon",
        "model_version": "Unnamed; see version",
        "version": version,
        "head": head,
        "training_setting": training_setting,
        "access_reuse": ACCESS_NOTE,
        "provenance_note": "Configured and run by Blank Bio, the model's developer.",
        "missing_metadata": NO_CKPT,
        "source_locator": locator,
        "review": review("Configuration transcribed from the cited Methods text."),
    }
    if limitations:
        attrs["limitations"] = list(limitations)
    if extra:
        attrs.update(extra)
    links = [("configuration_of", M_LADON)] + [("uses_model", u) for u in uses]
    return add("configuration", rid("config", slug), name, description, attrs, links=links,
               facets={"areas": AREAS, "contexts": CLIN, "method_types": ["foundation_model"]})


C_TRANSFER = ladon_config(
    "ladon-transfer-cox", "Ladon, survival mid-trained, ridge Cox fitted on one cohort (TCGA/CPTAC transfer)",
    "Frozen Ladon encoder after survival-supervised mid-training, with a ridge-regularised Cox model fitted on standardised embeddings of the source cohort and applied unchanged to the target cohort.",
    "Encoder after supervised mid-training on survival outcomes from other cohorts plus disease stage, age and smoking status; TCGA and CPTAC outcome labels excluded from encoder supervision",
    "Ridge Cox with shared coefficients and a separate Breslow baseline hazard per source cohort; features standardised with source mean and SD; penalty chosen by five-fold CV stratified by cohort and event, maximising held-out partial likelihood",
    "Fitted on all source samples (TCGA or CPTAC), applied unchanged to the other dataset",
    "Pages 11 and 12, Methods 'Transfer between TCGA and CPTAC'")

C_TRANSFER_CLIN = ladon_config(
    "ladon-clinical-transfer-cox", "Ladon + clinical covariates, concatenated embeddings, ridge Cox (TCGA/CPTAC transfer)",
    "Concatenation of frozen survival-mid-trained Ladon embeddings and frozen BMRetriever-7B clinical-text embeddings, fitted with one ridge Cox model on the source cohort and applied unchanged to the target cohort.",
    "Same encoder state as the Ladon transfer configuration",
    "One ridge Cox model on the concatenated Ladon and BMRetriever-7B embeddings, fitted as in the Ladon transfer configuration",
    "Fitted on all source samples (TCGA or CPTAC), applied unchanged to the other dataset",
    "Page 12, Methods 'Transfer between TCGA and CPTAC', sentence beginning 'For Ladon + clinical covariates, we concatenate'",
    extra={"combination_rule": "Concatenate Ladon and BMRetriever-7B embeddings before fitting one Cox model"}, uses=[M_BMR])

C_TRIAL = ladon_config(
    "ladon-trial-survival-cox", "Ladon, survival mid-trained, ridge Cox fitted on TCGA and other trials (held-out trials)",
    "Frozen survival-supervised Ladon encoder with separate ridge Cox predictors for overall and progression-free survival, fitted on TCGA and the other clinical trials and applied to each held-out trial.",
    "Embeddings from the survival-supervised Ladon model",
    "Ridge Cox with shared coefficients and separate Breslow baseline hazards per TCGA project and trial-arm group; fixed penalty lambda = 0.3 selected once on TCGA; features standardised with training mean and SD; separate predictors for OS and PFS",
    "Fitted on TCGA and the other clinical trials; the evaluated trial is not used to fit its predictor",
    "Page 13, Methods 'Survival in held-out trials'")

C_TRIAL_CLIN = ladon_config(
    "ladon-clinical-trial-survival", "Ladon + clinical covariates, summed standardised risk scores (held-out trials)",
    "Equal-weight sum of the Ladon survival risk score and a BMRetriever-7B clinical-covariate risk score, each standardised within the evaluated trial and endpoint.",
    "Embeddings from the survival-supervised Ladon model",
    "Ladon ridge Cox score (lambda = 0.3) plus a clinical-covariate Cox score with cross-validated penalty, each standardised within trial and endpoint, summed with equal weights; Ladon alone in IMbrave150, which has no patient-specific clinical covariates",
    "Both component predictors fitted on TCGA and the other clinical trials",
    "Page 13, Methods 'Survival in held-out trials', paragraph beginning 'We fit a separate Cox predictor on the clinical-covariate embeddings'; page 14, first line",
    extra={"combination_rule": "Standardise the molecular and clinical risk scores within each evaluated trial and endpoint, then sum with equal weights"},
    limitations=["In IMbrave150 the combined predictor is Ladon alone, so the OS and PFS summaries for this configuration mix combined and Ladon-only scores."],
    uses=[M_BMR])

C_POOL = ladon_config(
    "ladon-pooled-cox-plus-trials", "Ladon, ridge Cox fitted on TCGA plus non-trial cohorts and other trials (training-pool study)",
    "Frozen Ladon encoder with a ridge Cox model fitted on the largest training pool of the labelled-cohort study: TCGA, non-trial cohorts and the other clinical trials.",
    "Fixed trained encoder; the report does not say which mid-training state is used in this study",
    "Ridge Cox, lambda = 0.3 selected once on TCGA, separate baseline hazards per TCGA project, additional cohort and trial-arm group, shared embedding coefficients",
    "TCGA, non-trial cohorts and other clinical trials, 17,378 to 17,929 samples; the evaluated trial is excluded",
    "Page 14, Methods 'Additional labeled cohorts' and the stage table, row '+ trials'",
    limitations=["The non-trial cohorts in the pool are not named."])

C_RESPONSE = ladon_config(
    "ladon-response-tabicl", "Ladon, response mid-trained, PCA 128 + TabICL v2 (held-out trial response)",
    "Mean-pooled embeddings of a response-mid-trained Ladon encoder reduced to 128 principal components and classified by TabICL v2 using labelled patients from academic cohorts and the other trials as in-context examples.",
    "Encoder after supervised mid-training that includes response labels from academic cohorts",
    "PCA to 128 components fitted on context patients only (centred, not scaled), combined with cancer-indication and treatment indicators; TabICL v2 classifier",
    "In-context examples: 1,419 patients from 33 academic cohorts plus patients from the other trials in the response benchmark; the evaluated trial is always excluded",
    "Pages 15 and 16, Methods 'Immunotherapy response'",
    limitations=["The 33 academic cohorts are not listed, so overlap between the mid-training response labels and any trial cannot be checked."])

C_ISOFORM = ladon_config(
    "ladon-isoform-imputation", "Ladon, pretrained encoder, isoform percentages imputed from gene-level counts",
    "Ladon given only gene-level expression of a sample and asked to impute each isoform's share of its gene's RNA.",
    "Pretrained model; pretraining excluded the TCGA cohorts and included the ENCODE4 and blood bulk reference libraries",
    "Model's own reconstruction of isoform-level abundances from gene-level input; no separate head is described",
    "No task-specific fitting is described",
    "Page 28, Methods 'Model input'",
    limitations=["Pretraining included the ENCODE4 and blood bulk reference libraries whose isoform estimates are the reference in Figures 13 and 14."])

C_DECONV = ladon_config(
    "ladon-deconvolution-pbmc", "Ladon, composition post-trained, PCA 64 + TabICL regressors (PBMC deconvolution)",
    "Composition-post-trained Ladon representations of synthetic bulks from four PBMC single-cell references, reduced to 64 principal components, with one TabICL regressor per lineage predicting its share in real bulk samples.",
    "Pretrained model post-trained on bulk transcriptomes (pretraining objective) and synthetic bulks from scBaseCount pseudobulks (pretraining plus linear composition objective); a random subset of single-cell studies, including the study paired with the PBMC test bulks, contributed no synthetic bulks",
    "Representation is the mean of encoder latent outputs; standardised and reduced to 64 principal components fitted on reference synthetic bulks; one TabICL regressor per lineage; shares clipped at zero and rescaled to sum to 1",
    "Trained on 2,000 synthetic bulks (500 per study) from four scBaseCount PBMC studies (SRP359840, SRP411630, SRP345080, SRP559768; 165 samples)",
    "Pages 38, 39 and 40, Methods 'Ladon post-training', 'Deconvolution model' and 'PBMC deconvolution benchmark'")

C_PCR = ladon_config(
    "ladon-composition-pcr", "Ladon deconvolution composition + L2 logistic regression (breast cancer pCR)",
    "Twelve-class composition inferred by composition-post-trained Ladon from a breast tumour single-cell atlas reference, fed to an L2-penalised logistic regression of pathological complete response fitted on TransNEO.",
    "Composition-post-trained Ladon, as in the PBMC deconvolution configuration",
    "Deconvolution model trained on 6,500 synthetic bulks (100 per tumour) from 65 treatment-naive tumours of the Xu et al. (2024) atlas, 12 classes; then scikit-learn 1.9.1 LogisticRegressionCV, L2, penalty by five-fold stratified CV on the 12 standardised class shares; patients scored by predicted log-odds",
    "Response model fitted on TransNEO separately for ER+/HER2- and HER2+ tumours, then applied unchanged to external cohorts",
    "Pages 34, 35 and 40, Methods 'Breast cancer response prediction'")

# --------------------------------------------------------------------------------------------
# Comparator configurations (external models) and methods
# --------------------------------------------------------------------------------------------
C_BULKRNABERT = add("configuration", rid("config-bulkrnabert-hf"), "BulkRNABert, published Hugging Face checkpoint (Ladon report comparator)",
    "BulkRNABert embeddings from the published Hugging Face checkpoint with its published input processing, used as features for the same outcome heads as Ladon.",
    {"configuration_type": "paper_evaluation", "reported_name": "BulkRNABert", "version": "Published Hugging Face checkpoint and input processing",
     "head": "Same head as Ladon in each experiment (source-fitted Cox, ridge Cox with lambda = 0.3, or PCA and TabICL)",
     "access_reuse": "Run by Blank Bio. The checkpoint repository is not named.",
     "provenance_note": "Comparator configured by Blank Bio, not by BulkRNABert's developers.",
     "missing_metadata": missing(checkpoint_revision=("unreported", "Repository and revision not printed.")),
     "source_locator": "Page 11, Comparators table; pages 12, 13 and 16 for the heads",
     "review": review("Configuration transcribed from the comparator table and Methods.")},
    links=[("configuration_of", M_BULKRNABERT)], facets={"areas": AREAS, "contexts": CLIN, "method_types": ["foundation_model"]})

C_BULKFORMER = add("configuration", rid("config-bulkformer-147m"), "BulkFormer 147M (Ladon report comparator)",
    "BulkFormer 147M embeddings used as features for the same outcome heads as Ladon.",
    {"configuration_type": "paper_evaluation", "reported_name": "BulkFormer", "version": "147M checkpoint",
     "head": "Same head as Ladon in each experiment (source-fitted Cox, ridge Cox with lambda = 0.3, or PCA and TabICL)",
     "access_reuse": "Run by Blank Bio. The checkpoint repository is not named.",
     "provenance_note": "Comparator configured by Blank Bio, not by BulkFormer's developers.",
     "missing_metadata": missing(checkpoint_revision=("unreported", "Repository and revision not printed.")),
     "source_locator": "Page 11, Comparators table; pages 12, 13 and 16 for the heads",
     "review": review("Configuration transcribed from the comparator table and Methods.")},
    links=[("configuration_of", M_BULKFORMER)], facets={"areas": AREAS, "contexts": CLIN, "method_types": ["foundation_model"]})

C_BMR = add("configuration", rid("config-bmretriever-7b-clinical"), "Clinical covariates encoded by BMRetriever-7B (Ladon report baseline)",
    "Baseline clinical covariates (age, sex, disease stage and, by cohort, histology, grade, performance status and prior treatment) written as text and embedded by BMRetriever-7B, used as features for the same outcome heads as Ladon.",
    {"configuration_type": "paper_evaluation", "reported_name": "Clinical covariates (BMRetriever)", "version": "BMRetriever-7B embeddings of clinical text",
     "head": "Same head as Ladon in each experiment; in the held-out trials the standalone baseline uses the fixed ridge penalty",
     "access_reuse": "Run by Blank Bio.",
     "provenance_note": "Baseline configured by Blank Bio.",
     "limitations": ["IMbrave150 has no patient-specific clinical covariates: no hazard ratio is estimable there and the response score is constant."],
     "missing_metadata": missing(checkpoint_revision=("unreported", "Repository and revision not printed.")),
     "source_locator": "Page 11, Methods 'Clinical covariates'; page 13; page 16",
     "review": review("Configuration transcribed from the Methods.")},
    links=[("configuration_of", M_BMR)], facets={"areas": AREAS, "contexts": CLIN, "method_types": ["foundation_model"]})


def method(slug, name, description, locator, mtype, reported_name=None, version=None, note=None, facets_ctx=CLIN):
    attrs = {
        "entity_level": "method",
        "reported_name": reported_name or name,
        "version": version or "As described in the Ladon technical report",
        "provenance_note": note or "Comparator implemented and run by Blank Bio in the Ladon technical report.",
        "source_locator": locator,
        "review": review("Definition transcribed from the cited Methods text."),
    }
    return add("method", rid("method", slug), name, description, attrs,
               facets={"areas": AREAS, "contexts": facets_ctx, "method_types": [mtype]})


M_DGE = method("dge-signature", "Differential gene expression signature (Ladon report)",
    "Risk or response signature built by selecting genes associated with the outcome and combining their standardised expression, with signature size chosen by cross-validation on training data.",
    "Page 11, Comparators table, row 'DGE'; page 16 for the response version", "supervised_machine_learning", reported_name="Differential gene expression")
M_GSEA = method("hallmark-gsea", "Hallmark GSEA pathway signature (Ladon report)",
    "Outcome signature built from enrichment scores of the 50 Hallmark gene programs instead of individual genes.",
    "Page 11, Comparators table, row 'Hallmark GSEA'", "supervised_machine_learning", reported_name="Hallmark GSEA")
M_ISOTPM = method("isoform-tpm", "Isoform TPM features (Ladon report)",
    "Isoform-level TPM values used directly as survival features, either with the source-fitted Cox model or reduced to 100 principal components with an elastic-net Cox model fitted on cancer-matched TCGA or CPTAC cohorts.",
    "Page 12, Methods 'Transfer between TCGA and CPTAC'; page 13, paragraph beginning 'The isoform-TPM baseline'", "supervised_machine_learning",
    reported_name="Isoform TPM; TPM · matched TCGA")
M_GENETPM = method("gene-tpm-academic", "Gene TPM features with academic-only context (Ladon report)",
    "Log2(TPM + 1) of 20,250 protein-coding genes reduced by PCA and classified by TabICL with academic cohorts alone as in-context examples.",
    "Page 16, paragraph beginning 'The gene-expression baseline uses'", "supervised_machine_learning", reported_name="Gene TPM")
M_PDL1 = method("pd-l1-mrna", "PD-L1 mRNA (CD274 expression)",
    "Uses CD274 gene expression directly as the response or benefit score, with no fitting.",
    "Page 16, sentence 'PD-L1 mRNA uses CD274 expression directly and requires no fitting'; page 22 for the benefit analysis", "conventional_pipeline",
    reported_name="PD-L1 mRNA")
M_TEFF = method("t-effector-ifng", "T-effector / IFN-gamma signature",
    "Published T-effector and interferon-gamma gene expression signature used as an immunotherapy response score.",
    "Figure 6 (page 10), row 'T-effector / IFN-γ'", "specialist", reported_name="T-effector / IFN-γ",
    version="Version and gene list not printed in the report")
M_IMPRES = method("impres", "IMPRES",
    "Published immuno-predictive score built from pairwise expression relations of immune checkpoint genes, used as a response score.",
    "Figure 6 (page 10), row 'IMPRES'", "specialist", version="Version not printed in the report")
M_TIDE = method("tide", "TIDE",
    "Published tumour immune dysfunction and exclusion score, sign-reversed so that higher values indicate expected response.",
    "Figure 6 (page 10), row 'TIDE'; web Figure 6 note on sign reversal", "specialist", version="Version not printed in the report")
M_COHORT_RIDGE = method("cohort-trained-isoform-ridge", "Cohort-trained isoform ridge baseline (Ladon report)",
    "Ridge regression of isoform percentages on principal components of log gene expression, plus a second step on the gene's own expression level, fitted on the target cohort's own isoform measurements by five-fold cross-validation.",
    "Page 29, paragraph beginning 'The cohort-trained baseline is a ridge regression'", "supervised_machine_learning", facets_ctx=RES)
M_COHORT_MEAN = method("cohort-mean-isoform", "Cohort mean isoform split",
    "Predicts every tumour's isoform split as the cohort's mean split.",
    "Figure 11 readout (page 24), 'cohort mean'", "conventional_pipeline", reported_name="cohort mean", facets_ctx=RES,
    note="Reference value printed in the Ladon technical report; its construction is not described beyond its name.")
M_PUB_RIDGE = method("public-ridge-isoform", "Public-reference ridge isoform baseline (Ladon report)",
    "Ridge regression from 100 principal components of standardised log expression of the 5,000 most variable genes to isoform percentages, fitted on every public reference sample.",
    "Page 28, Methods 'Public-reference baselines'", "supervised_machine_learning", reported_name="Linear model on public data", facets_ctx=RES)
M_NEAREST = method("nearest-public-samples", "Nearest public samples isoform baseline (Ladon report)",
    "Averages the isoform percentages of the nearest public reference samples by cosine distance in the public ridge baseline's principal component space.",
    "Page 28, Methods 'Public-reference baselines'", "conventional_pipeline", reported_name="Nearest public samples", facets_ctx=RES)
M_ORGAN = method("organ-average-lookup", "Organ-average isoform lookup",
    "Returns the mean isoform percentages of public reference samples labelled with the target organ.",
    "Page 28, Methods 'Public-reference baselines'", "conventional_pipeline", reported_name="Organ average", facets_ctx=RES)
M_KALLISTO = method("kallisto-pooled-10x", "Isoform quantification from pooled 10x reads (kallisto)",
    "Quantifies isoforms directly from a draw's pooled single-cell reads with kallisto.",
    "Pages 29 and 30, Methods 'Blood'", "conventional_pipeline", reported_name="Isoform quantification from 10x reads", facets_ctx=RES)
M_EPIC = method("epic", "EPIC (BRef reference)",
    "Deconvolution with constrained least squares on reference profiles from bulk RNA-seq of sorted cells, run with its BRef reference on TPM.",
    "Page 39, Methods 'Prior methods'", "conventional_pipeline", reported_name="EPIC", facets_ctx=RES)
M_ABIS = method("abis", "ABIS",
    "Robust linear regression of bulk expression on an RNA-seq signature of sorted immune cells.",
    "Page 39, Methods 'Prior methods'", "conventional_pipeline", reported_name="ABIS", facets_ctx=RES)
M_BAYESPRISM = method("bayesprism", "BayesPrism (single-cell PBMC references)",
    "Bayesian deconvolution of bulk counts against single-cell references, run with up to 50 cells per sample and lineage from the four PBMC references.",
    "Page 39, Methods 'Prior methods'", "conventional_pipeline", reported_name="BayesPrism", facets_ctx=RES)
M_CIBERSORT = method("cibersort-reimpl", "CIBERSORT reimplementation (Ladon report)",
    "Nu-support vector regression of z-scored gene TPM on a 1,000-gene signature of mean lineage CPM from the single-cell references, with negative weights set to zero.",
    "Page 39, Methods 'Prior methods'", "conventional_pipeline", reported_name="CIBERSORT", facets_ctx=RES,
    note="Reimplemented by Blank Bio from the published algorithm; not the original CIBERSORT software.")
M_DWLS = method("dwls-reimpl", "DWLS reimplementation (Ladon report)",
    "Dampened weighted least squares on gene CPM from a non-negative least-squares start, with weights 1/y^2, using the same 1,000-gene single-cell signature.",
    "Page 39, Methods 'Prior methods'", "conventional_pipeline", reported_name="DWLS", facets_ctx=RES,
    note="Reimplemented by Blank Bio from the published algorithm; not the original DWLS software.")
M_ONCO = method("oncotype-dx-surrogate", "Oncotype DX expression surrogate (genefu oncotypedx)",
    "Expression-based surrogate of the Oncotype DX recurrence score computed with the genefu oncotypedx function on log2(TPM + 1).",
    "Page 40, Methods 'Other baselines'", "conventional_pipeline", reported_name="Oncotype DX*")
M_MAMMA = method("mammaprint-surrogate", "MammaPrint expression surrogate (genefu gene70)",
    "Expression-based surrogate of the MammaPrint 70-gene signature computed with the genefu gene70 function on log2(TPM + 1).",
    "Page 40, Methods 'Other baselines'", "conventional_pipeline", reported_name="MammaPrint*")
M_ERBB2 = method("erbb2-expression", "HER2 expression (ERBB2 mRNA)",
    "Uses ERBB2 gene expression, log2(1 + TPM), directly as the response score.",
    "Page 40, Methods 'Other baselines'; Figure 18 caption", "conventional_pipeline", reported_name="HER2 expression")

# --------------------------------------------------------------------------------------------
# Benchmark (ClinBench) and tasks
# --------------------------------------------------------------------------------------------
B_CLIN = add("benchmark", rid("benchmark-clinbench"), "ClinBench (Blank Bio)",
    "Patient-level benchmark assembled by Blank Bio of 142 survival, treatment-response and patient and tumour characteristic prediction tasks from bulk RNA-seq, scored on frozen embeddings.",
    {
        "entity_level": "suite",
        "executable_suite": False,
        "version": "As described in the 12 November 2026 Ladon technical report",
        "task": "Survival ranking and classification from frozen RNA-seq embeddings",
        "split": "85 within-cohort tasks with three-fold cross-validation repeated five times; 57 cross-cohort survival tasks trained on the other cohorts of the same cancer type and evaluated on the held-out cohort",
        "scope_note": "142 tasks: 85 within-cohort tasks and 57 cross-cohort survival tasks; each held-out cohort counts as a separate task. "
                      "Survival is scored with Harrell's concordance index (elastic-net Cox) and classification with AUROC (logistic regression), "
                      "regularisation chosen by cross-validation on training data. The reported score is the unweighted mean over all 142 tasks. "
                      "Four feature representations are tried per checkpoint (raw, standardised, PCA 32, PCA 64) and the best is reported. "
                      "The gene-expression baseline uses the same tasks, splits and heads on log gene expression, PCA 32.",
        "limitations": [
            "The task list, cohorts, outcome definitions and splits are not published, so the benchmark cannot be rerun or checked.",
            "The 142 tasks are not 142 trials or 142 external cohorts: 85 are within-cohort cross-validation tasks.",
            "The report prints no ClinBench score; Figures 20 and 21 are images with no numbers in the text layer.",
            "Per checkpoint the best of four feature representations is reported, a selection on the evaluation tasks.",
        ],
        "missing_metadata": missing(split_manifest=("unavailable", "No task list or split manifest is published.")),
        "source_locator": "Page 41, paragraph beginning 'To assess whether a decrease in pre-training loss'; page 43, Methods 'Clinical benchmark'",
        "review": review("Definition transcribed from the Methods. No results extracted: Figures 20 and 21 print no values."),
    }, status="discovered")

T_SURV = add("task", rid("task-survival-prognosis"), "Survival prognosis from pretreatment bulk RNA-seq",
    "Rank patients by risk of death or progression from a bulk RNA-seq profile, with the predictor fitted on other cohorts or trials.",
    {"task_type": "survival risk ranking", "task": "Prognosis", "scope_note": "Covers the TCGA/CPTAC transfer (Figure 2), the held-out trial risk split (Figures 3 and 4) and the training-pool study (Figure 5).",
     "source_locator": "Pages 5 to 9 and Methods pages 11 to 15"})
T_RESP = add("task", rid("task-immunotherapy-response"), "Immunotherapy response from pretreatment bulk RNA-seq",
    "Classify RECIST complete or partial responders against other evaluable patients in the immunotherapy arm of a held-out trial from pretreatment bulk RNA-seq.",
    {"task_type": "binary response classification", "task": "Treatment response", "scope_note": "Figure 6. Response, not benefit: no control arm is used.",
     "source_locator": "Pages 9 and 10; Methods pages 15 and 16"})
T_BENEFIT = add("task", rid("task-treatment-benefit"), "Treatment benefit (predictive biomarker) from bulk RNA-seq",
    "Identify patients whose 12-month progression-free survival gains more from the experimental arm than from control in a randomised trial, separating predictive from prognostic signal.",
    {"task_type": "heterogeneous treatment effect estimation", "task": "Treatment benefit",
     "scope_note": "Figures 7, 8 and 9: a single retrospective analysis in POPLAR (atezolizumab against docetaxel). No result records: the printed numbers are recorded as claims.",
     "source_locator": "Pages 16 to 22"})
T_ISO = add("task", rid("task-isoform-recovery"), "Isoform usage recovery from gene-level expression",
    "Predict each isoform's share of its gene's RNA from gene-level counts, scored against isoform-level quantification of matched bulk RNA-seq.",
    {"task_type": "isoform proportion imputation", "task": "Isoform recovery",
     "scope_note": "Figures 11 to 14: TCGA tumours, ENCODE4 organ pairs from single-nucleus counts, and blood draws from single-cell counts.",
     "source_locator": "Pages 23 to 30"},
    facets={"areas": AREAS, "contexts": RES})
T_COMP = add("task", rid("task-cell-composition"), "Cell-type deconvolution of bulk RNA-seq with single-cell references",
    "Infer cell-lineage shares of a bulk RNA-seq sample using references built from single-cell data, scored against shares measured by single-cell RNA-seq of the same sample.",
    {"task_type": "deconvolution", "task": "Cell composition", "scope_note": "Figure 17 (PBMC).",
     "source_locator": "Pages 30 to 33; Methods pages 38 to 40"},
    facets={"areas": AREAS + ["single-cell"], "contexts": RES})
T_PCR = add("task", rid("task-pcr-prediction"), "Pathological complete response from inferred tumour composition",
    "Predict pathological complete response to neoadjuvant therapy in breast cancer from pretreatment bulk RNA-seq via inferred composition.",
    {"task_type": "binary response classification", "task": "Treatment response (neoadjuvant, breast)", "scope_note": "Figure 18.",
     "source_locator": "Pages 34 and 35; Methods page 40"})

# --------------------------------------------------------------------------------------------
# Datasets and subsets
# --------------------------------------------------------------------------------------------
UNREP_ACCESS = missing(accession=("unreported", "The report gives no accession or data release for this cohort."))


def dataset(slug, name, description, attrs, facets=None):
    a = {"source_locator": attrs.pop("source_locator"), "review": review("Cohort description transcribed from the cited text."), **attrs}
    return add("dataset", rid("data", slug), name, description, a, facets=facets)


D_TCGA = dataset("tcga", "TCGA bulk RNA-seq with clinical outcomes (as used in the Ladon report)",
    "The Cancer Genome Atlas tumour RNA-seq profiles with survival and clinical annotations, quantified at transcript level with kallisto.",
    {"version": "Not stated; isoforms from GENCODE 41 transcripts in the model vocabulary for the isoform analyses",
     "assay": "Bulk RNA-seq; kallisto transcript TPM", "species": "Homo sapiens", "context": "Cancer cohort study",
     "access": "Public consortium data; the report does not state the release or access route.",
     "missing_metadata": missing(accession=("unreported", "No release or data freeze is given.")),
     "source_locator": "Page 6; page 12 table; page 28, Methods 'Tumor cohorts'"})
D_CPTAC = dataset("cptac", "CPTAC bulk RNA-seq with clinical outcomes (as used in the Ladon report)",
    "Clinical Proteomic Tumor Analysis Consortium tumour RNA-seq profiles with survival annotations.",
    {"version": "Not stated", "assay": "Bulk RNA-seq", "species": "Homo sapiens", "context": "Cancer cohort study",
     "access": "Public consortium data (Li et al., 2023); the report does not state the release.",
     "missing_metadata": missing(accession=("unreported", "No release is given.")),
     "source_locator": "Page 6; page 12 table"})
D_TRIALS = dataset("held-out-trials", "Clinical trial pretreatment RNA-seq cohorts (Ladon report)",
    "Pretreatment tumour RNA-seq with survival and RECIST response outcomes from eight clinical trials: OAK, POPLAR, IMpower133, IMvigor010, IMvigor210, IMbrave150, IMmotion150 and IMmotion151.",
    {"version": "Not stated", "assay": "Bulk RNA-seq of pretreatment tumour samples", "species": "Homo sapiens", "context": "Randomised and single-arm oncology trials, analysed retrospectively",
     "access": "Not stated in the report.",
     "missing_metadata": missing(accession=("unreported", "The report does not say where the trial RNA-seq and outcome data came from or how they can be accessed.")),
     "source_locator": "Page 13 trial table; page 15 trial table"})
D_ENCODE = dataset("encode4", "ENCODE4 paired bulk and single-nucleus RNA-seq of donor organs",
    "ENCODE4 tissue samples with both bulk RNA-seq (isoform-quantified) and single-nucleus RNA-seq from the same donors.",
    {"version": "ENCODE4 (Kagda et al., 2025); file set not listed", "assay": "Bulk RNA-seq and single-nucleus RNA-seq (STARsolo GeneFull)", "species": "Homo sapiens",
     "context": "Reference tissue atlas", "access": "Public ENCODE portal; specific files not listed.",
     "missing_metadata": missing(accession=("unreported", "No ENCODE accessions are listed.")),
     "source_locator": "Page 26; page 29, Methods 'ENCODE4 organs'"}, facets={"areas": AREAS + ["single-cell"], "contexts": RES})
D_GIROUX = dataset("giroux2022-blood", "Giroux et al. 2022 COVID-19 blood cohort, paired bulk and single-cell RNA-seq",
    "Blood draws from a longitudinal COVID-19 study with PBMC bulk RNA-seq (GEO GSE206263) and single-cell RNA-seq of the same draws (GSE206283; SuperSeries GSE206284).",
    {"version": "GEO SuperSeries GSE206284", "accession": "GSE206263; GSE206283; GSE206284", "assay": "PBMC bulk RNA-seq and 10x single-cell RNA-seq", "species": "Homo sapiens",
     "context": "Longitudinal COVID-19 cohort and healthy controls", "access": "Public GEO accessions as listed in the report.",
     "source_locator": "Page 27; page 39, Methods 'PBMC deconvolution benchmark'"}, facets={"areas": AREAS + ["single-cell"], "contexts": RES})
D_SAMMUT = dataset("sammut2022-breast", "Sammut et al. 2022 breast cancer neoadjuvant cohorts (TransNEO, ARTEMIS, PBCP)",
    "Pretreatment breast tumour RNA-seq with ER and HER2 status and pathological response from the TransNEO, ARTEMIS and PBCP cohorts released with Sammut et al. (2022).",
    {"version": "Release of Sammut et al. (2022)", "assay": "Bulk RNA-seq of pretreatment biopsies", "species": "Homo sapiens",
     "context": "Neoadjuvant breast cancer cohorts and the ARTemis phase 3 trial", "access": "Released with Sammut et al. (2022); the report gives no accession.",
     "missing_metadata": missing(accession=("unreported", "No accession is given for this release.")),
     "source_locator": "Page 40, Methods 'Breast cancer response prediction', 'Cohorts'"})
D_IBC = dataset("gse207248-ibc", "DFCI inflammatory breast cancer pretreatment biopsies (GSE207248)",
    "Pretreatment biopsies of HER2-positive inflammatory breast cancer with RNA-seq and response from GEO GSE207248 (Pernas et al., 2022).",
    {"version": "GEO GSE207248", "accession": "GSE207248", "assay": "Bulk RNA-seq of pretreatment biopsies", "species": "Homo sapiens",
     "context": "HER2-positive inflammatory breast cancer, neoadjuvant therapy", "access": "Public GEO accession.",
     "source_locator": "Page 40, Methods 'Breast cancer response prediction', 'Cohorts'"})


def subset(slug, name, description, parent, scope, used_in, counts=None, limitations=(), locator="", same_as=()):
    a = {"source_dataset": parent, "subset_scope": scope, "version": "As described in the Ladon technical report",
         "split": "Evaluation only", "source_locator": locator, "review": review("Subset definition transcribed from the cited text.")}
    if counts:
        a.update(counts)
    if limitations:
        a["limitations"] = list(limitations)
    links = [("used_in", u) for u in used_in] + [("same_data_as", s) for s in same_as]
    return rid("data", slug), (name, description, a, links)


pending_subsets = []

# --------------------------------------------------------------------------------------------
# Protocols
# --------------------------------------------------------------------------------------------
UNO = "Uno's C-index with inverse-probability-of-censoring weights; tau at the 70th percentile of observed death times; censoring by reverse Kaplan-Meier on the full evaluation population"
WILCOXON = "Comparisons with Ladon use one-sided paired Wilcoxon signed-rank tests; p-values are unadjusted and exact values are shown only on hover in the web version"


def protocol(slug, name, description, task, data, attrs, part_of=None):
    a = {"version": "As described in the 12 November 2026 Ladon technical report", "review": review("Protocol transcribed from the cited Methods text."), **attrs}
    links = [("evaluates_task", task)] + [("uses_data", d) for d in data]
    if part_of:
        links.append(("part_of", part_of))
    return add("protocol", rid("protocol", slug), name, description, a, links=links)


PR = {}
PR["t2c"] = protocol("transfer-tcga-to-cptac", "Survival transfer TCGA to CPTAC, mean Uno C-index over six cancers",
    "Fit a survival predictor on TCGA and apply it unchanged to six CPTAC cancer cohorts, scoring Uno's C-index per cancer and averaging equally.",
    T_SURV, [rid("data", "cptac-transfer-targets")],
    {"metric": "concordance-index", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "Uno's C-index, survival endpoint not specified beyond 'survival', equal mean over six CPTAC target cancers, predictor fitted on TCGA",
     "metric_definition": UNO, "aggregation": "Equal mean of six cancer-specific C-indices",
     "procedure": "Features standardised with source mean and SD; predictor fitted on all TCGA source samples and applied unchanged to CPTAC",
     "heldout_test": ["TCGA and CPTAC outcome labels are excluded from Ladon's encoder supervision and validation monitoring (page 11)."],
     "scope_note": "Target cohorts: CPTAC clear-cell kidney, glioblastoma, lung squamous, lung adenocarcinoma, pancreatic and endometrial (1,128 patients). " + WILCOXON + ".",
     "limitations": ["Six cancers per direction; the two directions do not use the same cancers (CPTAC has lung squamous, TCGA has head and neck)."],
     "source_locator": "Figure 2 (page 6) and caption; pages 11 and 12, Methods 'Transfer between TCGA and CPTAC'"})
PR["c2t"] = protocol("transfer-cptac-to-tcga", "Survival transfer CPTAC to TCGA, mean Uno C-index over six cancers",
    "Fit a survival predictor on CPTAC and apply it unchanged to six TCGA cancer cohorts, scoring Uno's C-index per cancer and averaging equally.",
    T_SURV, [rid("data", "tcga-transfer-targets")],
    {"metric": "concordance-index", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "Uno's C-index, survival endpoint not specified beyond 'survival', equal mean over six TCGA target cancers, predictor fitted on CPTAC",
     "metric_definition": UNO, "aggregation": "Equal mean of six cancer-specific C-indices",
     "procedure": "Features standardised with source mean and SD; predictor fitted on all CPTAC source samples and applied unchanged to TCGA",
     "heldout_test": ["TCGA and CPTAC outcome labels are excluded from Ladon's encoder supervision and validation monitoring (page 11)."],
     "scope_note": "Target cohorts: TCGA glioblastoma, head and neck, clear-cell kidney, lung adenocarcinoma, pancreatic and endometrial (2,461 patients). " + WILCOXON + ".",
     "source_locator": "Figure 2 (page 6) and caption; pages 11 and 12, Methods 'Transfer between TCGA and CPTAC'"})
PR["pan"] = protocol("transfer-pan-cancer", "Survival transfer TCGA and CPTAC, pan-cancer Uno C-index, mean of two directions",
    "Compute one Uno's C-index across all target patients of each transfer direction, including pairs from different cancers, and average the two directions equally.",
    T_SURV, [rid("data", "tcga-cptac-transfer-both")],
    {"metric": "concordance-index", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "Uno's C-index, survival endpoint not specified beyond 'survival', pan-cancer (pairs across cancers counted), equal mean of the TCGA to CPTAC and CPTAC to TCGA transfers",
     "metric_definition": UNO, "aggregation": "Equal mean of two pan-cancer C-indices",
     "scope_note": "Wilcoxon tests for this panel pair the two transfer-level scores (page 12). " + WILCOXON + ".",
     "limitations": ["Pan-cancer pairs between different cancers reward separating cancers with different baseline survival, not only within-cancer risk."],
     "source_locator": "Figure 2 (page 6), third panel 'Pan-Cancer, Mean of 2 transfers'; page 12"})
PR["os_hr"] = protocol("trials-os-hazard-ratio", "Held-out trials, OS hazard ratio of higher- against lower-risk half, geometric mean over six trials",
    "Split each held-out trial's patients at the method's median predicted risk and estimate the overall-survival hazard ratio of the higher-risk half against the lower-risk half, then take the geometric mean over six trials.",
    T_SURV, [rid("data", "trials-os-six")],
    {"metric": "hazard-ratio", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "hazard ratio, higher-risk half against lower-risk half at the median predicted risk, overall survival, Cox stratified by treatment arm, Efron ties, full follow-up; equal-trial geometric mean over six trials",
     "metric_definition": "Unpenalised Cox model with a binary risk-group indicator, stratified by treatment arm; patients above the median form the higher-risk group",
     "aggregation": "Equal-trial geometric mean over OAK, POPLAR, IMpower133, IMvigor010, IMvigor210 and IMbrave150",
     "heldout_test": ["Each trial's survival predictor is fitted on TCGA and the other trials, not on the evaluated trial (pages 7 and 13)."],
     "scope_note": "Wilcoxon tests on log hazard ratios pair trials with estimable results for both methods. " + WILCOXON + ".",
     "limitations": ["A median-split hazard ratio measures separation between halves, not calibrated risk or treatment effect.",
                     "Retrospective analysis of completed trials; no prospective use is tested."],
     "source_locator": "Figure 3 (page 7) and caption; pages 13 and 14, Methods 'Survival in held-out trials'"})
PR["pfs_hr"] = protocol("trials-pfs-hazard-ratio", "Held-out trials, PFS hazard ratio of higher- against lower-risk half, geometric mean over three trials",
    "Split each held-out trial's patients at the method's median predicted risk and estimate the progression-free-survival hazard ratio of the higher-risk half against the lower-risk half, then take the geometric mean over three trials.",
    T_SURV, [rid("data", "trials-pfs-three")],
    {"metric": "hazard-ratio", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "hazard ratio, higher-risk half against lower-risk half at the median predicted risk, progression-free survival, Cox stratified by treatment arm, Efron ties, full follow-up; equal-trial geometric mean over three trials",
     "metric_definition": "Unpenalised Cox model with a binary risk-group indicator, stratified by treatment arm",
     "aggregation": "Equal-trial geometric mean over IMbrave150, IMmotion150 and IMmotion151",
     "heldout_test": ["Each trial's survival predictor is fitted on TCGA and the other trials (pages 7 and 13)."],
     "scope_note": WILCOXON + ".",
     "limitations": ["Three trials only.", "Retrospective analysis of completed trials."],
     "source_locator": "Figure 3 (page 7) and caption; pages 13 and 14"})
PR["oak"] = protocol("oak-os-uno", "OAK overall survival, Uno C-index of a predictor fitted on other cohorts",
    "Score the 699 RNA-profiled OAK patients with a risk predictor fitted on other cohorts and compute Uno's C-index for overall survival.",
    T_SURV, [rid("data", "trials-oak")],
    {"metric": "concordance-index", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "Uno's C-index, overall survival, OAK (699 patients), predictor fitted on other cohorts",
     "metric_definition": UNO, "aggregation": "Single trial",
     "limitations": ["One trial; the report prints no interval for this value."],
     "source_locator": "Figure 4 caption (page 8)"})
PR["pool"] = protocol("trials-os-uno-weighted", "Held-out trials, OS Uno C-index weighted by trial size, TCGA plus non-trial cohorts plus other trials training pool",
    "Fit a survival predictor on TCGA, non-trial cohorts and the other clinical trials, and score Uno's C-index for overall survival in each of six held-out trials, averaged with weights equal to the number of evaluated patients.",
    T_SURV, [rid("data", "trials-os-six")],
    {"metric": "concordance-index", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "Uno's C-index, overall survival, mean over six trials weighted by evaluated patients; training pool TCGA plus non-trial cohorts plus other trials (largest pool, about 18k samples)",
     "metric_definition": UNO, "aggregation": "Size-weighted mean of six trial-level C-indices",
     "heldout_test": ["The evaluated trial is excluded from fitting its outcome predictor (page 9 and page 15 stage table)."],
     "scope_note": "Only the final training stage prints values in the PDF legend; the two smaller pools are drawn but not printed. Stars in the figure mark unadjusted one-sided paired Wilcoxon p < 0.05 against Ladon.",
     "source_locator": "Figure 5 (page 9) legend and caption; pages 14 and 15, Methods 'Additional labeled cohorts'"})
PR["resp"] = protocol("trials-response-auroc", "Held-out trials, immunotherapy response AUROC, equal mean over six trials",
    "Classify RECIST complete or partial responders in the immunotherapy arms of six held-out trials from pretreatment RNA-seq, scoring AUROC within each trial and averaging the six trials equally.",
    T_RESP, [rid("data", "trials-response-six")],
    {"metric": "auroc", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "AUROC for RECIST complete or partial response against other evaluable responses, immunotherapy arms, equal mean over six held-out trials",
     "aggregation": "Equal mean of six trial-specific AUROCs (OAK, POPLAR, IMvigor210, IMmotion150, IMmotion151, IMbrave150)",
     "heldout_test": ["The evaluated trial is always excluded from the labelled in-context examples (pages 9 and 15)."],
     "allowed_information": "Pretreatment RNA-seq plus cancer-indication and treatment indicators; labelled context differs by method (see limitations)",
     "scope_note": WILCOXON + ".",
     "limitations": [
         "Reference-data asymmetry: Ladon's labelled context is 1,419 patients from 33 academic cohorts plus the other trials, and its encoder was mid-trained with academic response labels; the gene-TPM baseline uses academic cohorts alone as context (page 16).",
         "The T-effector / IFN-gamma signature was derived on POPLAR, so its POPLAR AUROC is in-sample (web Figure 6 note, not printed in the PDF).",
         "Response is not benefit: no control arm enters this analysis.",
     ],
     "source_locator": "Figure 6 (page 10) and caption; pages 15 and 16, Methods 'Immunotherapy response'"})
PR["insr_r"] = protocol("insr-stomach-pearson", "INSR isoform split in TCGA stomach tumours, Pearson r",
    "Predict the INSR isoform percentages of 166 TCGA stomach adenocarcinomas from gene-level expression and score the Pearson correlation with the measured percentages.",
    T_ISO, [rid("data", "tcga-stomach-insr")],
    {"metric": "pearson-correlation", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "Pearson r between predicted and measured INSR isoform percentages, 166 TCGA stomach tumours with INSR at least 10 TPM",
     "uncertainty_reporting": {"type": "confidence_interval", "level": 0.95, "method": "percentile bootstrap with predictions held fixed, tumours resampled", "resamples": 2000},
     "heldout_test": ["Pretraining excluded the TCGA cohorts (page 28)."],
     "source_locator": "Figure 11 (page 24) readout and caption; page 28, Methods 'Tumor cohorts' and 'Confidence intervals'"})
PR["insr_mae"] = protocol("insr-stomach-mae", "INSR isoform split in TCGA stomach tumours, mean absolute error",
    "Predict the INSR isoform percentages of 166 TCGA stomach adenocarcinomas from gene-level expression and score the mean absolute error in percentage points.",
    T_ISO, [rid("data", "tcga-stomach-insr")],
    {"metric": "mean-absolute-error", "metric_direction": "lower", "unit": "percent",
     "metric_qualifier": "mean absolute error of INSR isoform percentage, 166 TCGA stomach tumours",
     "heldout_test": ["Pretraining excluded the TCGA cohorts (page 28)."],
     "limitations": ["The caption says the readout gives 95% intervals, but no interval is printed for the MAE values."],
     "source_locator": "Figure 11 (page 24) readout 'MAE, points'"})
PR["iso3000"] = protocol("isoform-3000-gene-median-r", "Isoform variation in eight held-out TCGA cancer types, median Pearson r over gene and cancer-type pairs",
    "Predict isoform percentages from gene-level expression for 3,000 sampled multi-isoform genes in eight held-out cancer types and report the median over gene and cancer-type pairs of the Pearson r between centred predicted and measured percentages.",
    T_ISO, [rid("data", "tcga-isoform-eight-types")],
    {"metric": "pearson-correlation", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "median over 14,526 gene and cancer-type combinations (1,572 tumours) of Pearson r between predicted and measured isoform percentages, each isoform centred on its mean across tumours",
     "aggregation": "Median over gene and cancer-type pairs",
     "uncertainty_reporting": {"type": "confidence_interval", "level": 0.95, "method": "percentile bootstrap, 1,000 paired resamples of tumours and eligible genes within each cancer type", "resamples": 1000, "note": "The figure says the intervals are narrower than the symbols; no interval is printed."},
     "heldout_test": ["Pretraining excluded the TCGA cohorts (page 28)."],
     "source_locator": "Figure 12a (page 25) and caption; pages 28 and 29, Methods 'Tumor cohorts'"})
PR["encode"] = protocol("encode4-organ-pair-r", "ENCODE4 within-donor organ pairs, Pearson r of predicted against measured isoform change",
    "Predict isoform percentages from corrected single-nucleus gene counts of two organs of one donor and score the Pearson r between predicted and bulk-measured changes across 1,402 organ-pair comparisons.",
    T_ISO, [rid("data", "encode4-organ-pairs")],
    {"metric": "pearson-correlation", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "Pearson r between predicted and bulk-measured changes in isoform percentage, 1,402 within-donor organ-pair comparisons (837 GTEx-selected contrasts, 287 genes, seven donors)",
     "uncertainty_reporting": {"type": "confidence_interval", "level": 0.95, "method": "percentile bootstrap resampling genes with all their comparisons", "resamples": 500, "note": "Drawn as error bars; not printed."},
     "limitations": ["Ladon's pretraining included the ENCODE4 bulk reference libraries that supply the measured isoform split (page 28)."],
     "source_locator": "Figure 13 (page 26) right panel and caption; page 29, Methods 'ENCODE4 organs'"},)
PR["blood_t"] = protocol("blood-direction-day0-14", "Blood single-cell to isoform, direction accuracy for day 0 to day 14 change, top 5% of genes",
    "Predict the direction of the within-person change in main-isoform percentage from day 0 to day 14 from pooled single-cell gene counts, scored on the 5% of genes with the largest bulk-measured change.",
    T_ISO, [rid("data", "giroux-blood-draws")],
    {"metric": "accuracy", "metric_direction": "higher", "unit": "percent",
     "metric_qualifier": "share of the top 5% of genes (460) by measured isoform change whose predicted direction of change in main-isoform percentage matches the bulk reference; mean within-person change day 0 to day 14, nine people",
     "limitations": ["Ladon's pretraining included the blood bulk reference libraries (page 28).", "Exact two-sided McNemar test against direct quantification: P = 0.003 (page 30)."],
     "source_locator": "Page 27 prose 'Among the 5% of genes with the largest measured changes'; Figure 14 caption; page 30, Methods 'Blood'"})
PR["blood_c"] = protocol("blood-direction-covid-vs-healthy", "Blood single-cell to isoform, direction accuracy for COVID-19 against healthy draws, top 5% of genes",
    "Predict the direction of the difference in main-isoform percentage between 26 COVID-19 and four healthy draws from pooled single-cell gene counts, scored on the 5% of genes with the largest bulk-measured difference.",
    T_ISO, [rid("data", "giroux-blood-draws")],
    {"metric": "accuracy", "metric_direction": "higher", "unit": "percent",
     "metric_qualifier": "share of the top 5% of genes (460) by measured isoform change whose predicted direction of change in main-isoform percentage matches the bulk reference; 26 COVID-19 draws against four healthy draws",
     "limitations": ["Ladon's pretraining included the blood bulk reference libraries (page 28).", "Exact two-sided McNemar test against direct quantification: P < 0.001 (page 30).", "Four healthy draws only."],
     "source_locator": "Page 27 prose; Figure 14 'top 5% 70% vs 59%'; page 30, Methods 'Blood'"})
PR["pbmc_r"] = protocol("pbmc-mean-pearson", "PBMC deconvolution, Pearson r of inferred against measured shares, mean over five lineages",
    "Infer CD4 T, CD8 T, NK, B/plasma and monocyte shares of 35 PBMC bulk RNA-seq samples and score the Pearson r against shares measured by single-cell RNA-seq of the same draws, averaged over the five lineages.",
    T_COMP, [rid("data", "giroux-pbmc-bulk")],
    {"metric": "pearson-correlation", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "Pearson r between inferred and measured lineage shares across 35 PBMC bulks, mean over five lineages",
     "aggregation": "Mean over five lineages",
     "uncertainty_reporting": {"type": "confidence_interval", "level": 0.95, "method": "percentile bootstrap resampling donors with all their test bulks, same resamples for every method", "resamples": 2000, "note": "Drawn as bars; printed only in the web version's collapsed data table."},
     "heldout_test": ["The single-cell study paired with the PBMC test bulks contributed no synthetic bulks to post-training (page 38)."],
     "scope_note": "Single-cell-reference methods (Ladon, BayesPrism, CIBERSORT, DWLS) share the four scBaseCount PBMC references; EPIC and ABIS use their published references from bulk RNA-seq of sorted cells.",
     "source_locator": "Figure 17 (page 33) bottom chart, left panel; pages 39 and 40, Methods 'PBMC deconvolution benchmark'"})
PR["pbmc_o"] = protocol("pbmc-pairwise-ordering", "PBMC deconvolution, pairwise ordering accuracy, mean over five lineages",
    "Infer lineage shares of 35 PBMC bulk RNA-seq samples and score the fraction of sample pairs with different measured shares that are put in the right order, averaged over five lineages.",
    T_COMP, [rid("data", "giroux-pbmc-bulk")],
    {"metric": "concordance-index", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "pairwise ordering accuracy: fraction of pairs of test bulks with different measured lineage shares put in the measured order, ties in inferred shares counted as half; mean over five lineages; 0.5 is chance",
     "aggregation": "Mean over five lineages",
     "uncertainty_reporting": {"type": "confidence_interval", "level": 0.95, "method": "percentile bootstrap resampling donors", "resamples": 2000, "note": "Drawn as bars; printed only in the web version's collapsed data table."},
     "heldout_test": ["The single-cell study paired with the PBMC test bulks contributed no synthetic bulks to post-training (page 38)."],
     "source_locator": "Figure 17 (page 33) bottom chart, right panel; page 40, Methods 'Accuracy'"})
PR["pbmc_lin"] = protocol("pbmc-lineage-pearson", "PBMC deconvolution, per-lineage Pearson r of inferred against measured shares",
    "Infer the share of one lineage in 35 PBMC bulk RNA-seq samples and score the Pearson r against the share measured by single-cell RNA-seq of the same draws.",
    T_COMP, [rid("data", "giroux-pbmc-bulk")],
    {"metric": "pearson-correlation", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "Pearson r between inferred and measured share of one lineage across 35 PBMC bulks",
     "scope_note": "The PDF prints per-lineage values only for Ladon and the default comparator, CIBERSORT.",
     "source_locator": "Figure 17 (page 33) top panels, 'r' labels"})
PR["pcr_er"] = protocol("pcr-er-pos-her2-neg-auc", "Breast cancer pCR, ER+/HER2- external cohorts, AUC of a model fitted on TransNEO",
    "Apply a pCR model fitted on TransNEO ER+/HER2- tumours unchanged to an external ER+/HER2- cohort and score the AUC.",
    T_PCR, [rid("data", "artemis-er-pos"), rid("data", "pbcp-er-pos")],
    {"metric": "auroc", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "AUC for pathological complete response, ER+/HER2- tumours, model fitted on TransNEO and applied unchanged",
     "uncertainty_reporting": {"type": "confidence_interval", "level": 0.95, "method": "percentile bootstrap resampling each cohort's patients, single-class resamples discarded", "resamples": 2000},
     "limitations": ["Three pCR events per cohort, so the intervals are wide.", "Oncotype DX and MammaPrint rows are expression surrogates from genefu, not the clinical assays."],
     "source_locator": "Figure 18 (page 35); page 34 prose; page 40, Methods 'Breast cancer response prediction'"})
PR["pcr_her2"] = protocol("pcr-her2-pos-auc", "Breast cancer pCR, HER2+ external cohorts, AUC of a model fitted on TransNEO",
    "Apply a pCR model fitted on TransNEO HER2+ tumours unchanged to an external HER2+ cohort and score the AUC.",
    T_PCR, [rid("data", "pbcp-her2-pos"), rid("data", "dfci-ibc")],
    {"metric": "auroc", "metric_direction": "higher", "unit": "unitless",
     "metric_qualifier": "AUC for pathological complete response, HER2+ tumours, model fitted on TransNEO and applied unchanged",
     "uncertainty_reporting": {"type": "confidence_interval", "level": 0.95, "method": "percentile bootstrap resampling each cohort's patients, single-class resamples discarded", "resamples": 2000},
     "limitations": ["18 and 22 patients."],
     "source_locator": "Figure 18 (page 35); page 34 prose; page 40"})

# Subsets (need protocol IDs, so built after protocols)
for sid, (name, desc, a, links) in [
    subset("cptac-transfer-targets", "CPTAC six-cancer transfer target set (1,128 patients)", "CPTAC patients of six cancers used as targets for predictors fitted on TCGA.",
           D_CPTAC, "Glioblastoma, clear-cell kidney, lung squamous, lung adenocarcinoma, pancreatic and endometrial; 1,128 patients in the matched expression-responsive evaluation subset",
           [PR["t2c"]], {"eligible_count": 1128}, locator="Page 12 table, column 'CPTAC'"),
    subset("tcga-transfer-targets", "TCGA six-cancer transfer target set (2,461 patients)", "TCGA patients of six cancers used as targets for predictors fitted on CPTAC.",
           D_TCGA, "Glioblastoma, head and neck, clear-cell kidney, lung adenocarcinoma, pancreatic and endometrial; 2,461 patients",
           [PR["c2t"]], {"eligible_count": 2461}, locator="Page 12 table, column 'TCGA'"),
    subset("tcga-cptac-transfer-both", "TCGA and CPTAC transfer target sets combined (pan-cancer panel)", "Both transfer target sets, used for the pan-cancer C-index averaged over the two directions.",
           D_TCGA, "Union of the 2,461 TCGA and 1,128 CPTAC target patients (3,589 by extractor's sum; no combined count is printed); one pan-cancer C-index per direction",
           [PR["pan"]], None, locator="Figure 2 (page 6) third panel; page 12",
           same_as=[rid("data", "cptac-transfer-targets"), rid("data", "tcga-transfer-targets")],
           limitations=["Spans two datasets; recorded under TCGA with same_data_as links to both target sets."]),
    subset("trials-os-six", "Six held-out trials with overall survival", "OAK, POPLAR, IMpower133, IMvigor010, IMvigor210 and IMbrave150, evaluated for overall survival.",
           D_TRIALS, "OAK and POPLAR (non-small-cell lung), IMpower133 (small-cell lung), IMvigor010 and IMvigor210 (urothelial), IMbrave150 (hepatocellular)",
           [PR["os_hr"], PR["pool"]], locator="Page 13 trial table; Figure 5 caption",
           limitations=["Patient counts per trial are printed only for OAK (699) and POPLAR (192 RNA-profiled)."]),
    subset("trials-pfs-three", "Three held-out trials with progression-free survival", "IMbrave150, IMmotion150 and IMmotion151, evaluated for progression-free survival.",
           D_TRIALS, "IMbrave150 (hepatocellular), IMmotion150 and IMmotion151 (renal cell)", [PR["pfs_hr"]], locator="Page 13 trial table"),
    subset("trials-oak", "OAK RNA-profiled patients (699)", "The 699 RNA-profiled patients of the phase III OAK lung cancer trial.",
           D_TRIALS, "OAK, 699 patients, both arms", [PR["oak"]], {"eligible_count": 699}, locator="Figure 4 caption (page 8); page 20"),
    subset("trials-response-six", "Immunotherapy arms of six held-out trials with evaluable response", "Immunotherapy-treated patients with a designated pretreatment RNA sample and evaluable RECIST response in OAK, POPLAR, IMvigor210, IMmotion150, IMmotion151 and IMbrave150.",
           D_TRIALS, "Immunotherapy arms only; responders are complete or partial RECIST responses", [PR["resp"]], locator="Page 15 trial table and eligibility paragraph",
           limitations=["Patient and responder counts per trial are not printed."]),
    subset("tcga-stomach-insr", "TCGA stomach adenocarcinomas with INSR at least 10 TPM (166)", "TCGA stomach tumours with INSR expression of at least 10 TPM.",
           D_TCGA, "166 stomach tumours, INSR at least 10 TPM", [PR["insr_r"], PR["insr_mae"]], {"eligible_count": 166}, locator="Page 23 prose; page 28, Methods 'Tumor cohorts'"),
    subset("tcga-isoform-eight-types", "TCGA tumours of eight held-out cancer types for isoform recovery (1,572)", "Tumours of eight TCGA cancer types with 3,000 sampled multi-isoform genes, giving 14,526 gene and cancer-type combinations.",
           D_TCGA, "1,572 tumours; genes eligible in a cancer type with at least two modelled isoforms and at least 10 TPM in at least 80% of tumours; 3,000 genes sampled from 8,807 eligible",
           [PR["iso3000"]], {"eligible_count": 1572}, locator="Figure 12a (page 25); page 28",
           limitations=["The eight cancer types are not named."]),
    subset("encode4-organ-pairs", "ENCODE4 within-donor organ-pair isoform contrasts (1,402 comparisons)", "837 gene and tissue-pair contrasts across 287 genes, selected in GTEx, scored in every ENCODE4 donor with both tissues.",
           D_ENCODE, "1,402 comparisons across seven donors", [PR["encode"]], {"eligible_count": 1402}, locator="Page 29, Methods 'ENCODE4 organs'"),
    subset("giroux-blood-draws", "Giroux blood draws for isoform direction (35 draws, 17 people)", "35 blood draws from 17 people with single-cell reads pooled per draw and matched bulk RNA-seq as reference, 9,207 multi-isoform genes.",
           D_GIROUX, "35 draws; contrasts: day 0 to day 14 in nine people, and 26 COVID-19 against four healthy draws; top 5% of genes (460) by measured change",
           [PR["blood_t"], PR["blood_c"]], {"eligible_count": 35}, locator="Page 27; page 30, Methods 'Blood'",
           same_as=[rid("data", "giroux-pbmc-bulk")]),
    subset("giroux-pbmc-bulk", "Giroux PBMC bulk RNA-seq test set for deconvolution (35 bulks, 17 donors)", "35 PBMC bulk RNA-seq samples from 17 donors with single-cell RNA-seq of the same draws as composition labels.",
           D_GIROUX, "GSE206263 bulks; labels are each lineage's share of annotated-cell UMIs in GSE206283", [PR["pbmc_r"], PR["pbmc_o"], PR["pbmc_lin"]], {"eligible_count": 35},
           locator="Page 39, Methods 'PBMC deconvolution benchmark'"),
    subset("artemis-er-pos", "ARTEMIS ER+/HER2- patients (35, 3 pCR)", "ER+/HER2- patients of the ARTemis trial with pretreatment RNA-seq and pCR status.",
           D_SAMMUT, "35 patients, 3 pCR", [PR["pcr_er"]], {"eligible_count": 35, "positive_count": 3}, locator="Figure 18 (page 35), 'ARTEMIS 35 patients, 3 pCR'"),
    subset("pbcp-er-pos", "PBCP ER+/HER2- patients (13, 3 pCR)", "ER+/HER2- patients of the PBCP cohort with pretreatment RNA-seq and pCR status.",
           D_SAMMUT, "13 patients, 3 pCR", [PR["pcr_er"]], {"eligible_count": 13, "positive_count": 3}, locator="Figure 18 (page 35), 'PBCP 13 patients, 3 pCR'"),
    subset("pbcp-her2-pos", "PBCP HER2+ patients (18, 11 pCR)", "HER2+ patients of the PBCP cohort with pretreatment RNA-seq and pCR status.",
           D_SAMMUT, "18 patients, 11 pCR", [PR["pcr_her2"]], {"eligible_count": 18, "positive_count": 11}, locator="Figure 18 (page 35), 'PBCP 18 patients, 11 pCR'"),
    subset("dfci-ibc", "DFCI inflammatory breast cancer HER2+ patients (22, 9 pCR)", "HER2+ inflammatory breast cancer pretreatment biopsies with pCR status from GEO's response field.",
           D_IBC, "22 patients, 9 pCR", [PR["pcr_her2"]], {"eligible_count": 22, "positive_count": 9}, locator="Figure 18 (page 35), 'DFCI IBC 22 patients, 9 pCR'"),
]:
    add("dataset_subset", sid, name, desc, a, links=links)

# --------------------------------------------------------------------------------------------
# Evaluations and results
# --------------------------------------------------------------------------------------------
n_eval = 0


def comp(protocol_id, split, population, inputs, adaptation, aggregation, metric_impl, dataset_version=None, budget=None):
    return {"protocol_id": protocol_id, "dataset_version": dataset_version, "split": split, "population": population,
            "inputs": inputs, "adaptation": adaptation, "metric_implementation": metric_impl, "aggregation": aggregation, "budget": budget}


def evaluate(slug, name, system, protocol_id, data, comparison, locator, results, eval_limitations=(), coverage=None):
    """results: list of dicts with printed, metric, qualifier, direction, unit, locator, and optional uncertainty/coverage/notes."""
    eid = rid("eval", slug)
    prec = next(r for r in records if r["id"] == protocol_id)
    task = next(l["target_id"] for l in prec["links"] if l["relation"] == "evaluates_task")
    facets = next(r for r in records if r["id"] == task)["facets"]
    attrs = {
        "origin": "author_reported",
        "protocol": protocol_id,
        "comparison": comparison,
        "version": "Zenodo 10.5281/zenodo.24157116, PDF dated 12 November 2026",
        "source_locator": locator,
        "limitations": ["Developer-reported by Blank Bio, which built Ladon and ran every comparator; not reproduced by Rewire."] + list(eval_limitations),
        "review": review("Evaluation setup transcribed from the figure, caption and Methods.", method_note=FIG_METHOD_NOTE),
    }
    if coverage:
        attrs["coverage"] = coverage
    if task in (T_SURV, T_RESP, T_PCR):
        attrs["retrospective"] = True
    add("evaluation", eid, name, "Developer-reported evaluation transcribed from the pinned Ladon technical report; not reproduced.",
        attrs, links=[("system", system), ("assessment", protocol_id), ("data", data)], facets=facets)
    for k, r in enumerate(results):
        ra = {
            "printed_value": r["printed"],
            "numeric_value": r.get("numeric", r["printed"].rstrip("%")),
            "metric": r["metric"],
            "metric_qualifier": r["qualifier"],
            "metric_direction": r["direction"],
            "unit": r["unit"],
            "source_locator": r["locator"],
            "review": review(r.get("note", "Printed label read from the text layer."), method_note=FIG_METHOD_NOTE),
        }
        if r.get("unit_detail"):
            ra["unit_detail"] = r["unit_detail"]
        if r.get("uncertainty"):
            ra["uncertainty"] = r["uncertainty"]
        else:
            ra["missing_metadata"] = {"uncertainty": {"reason": r.get("unc_reason", "unreported"), "note": r.get("unc_note", "No interval is printed for this value.")}}
        if r.get("coverage") or coverage:
            ra["coverage"] = r.get("coverage") or coverage
        if r.get("limitations"):
            ra["limitations"] = r["limitations"]
        if r.get("source_discrepancy"):
            ra["source_discrepancy"] = r["source_discrepancy"]
        if r.get("rounding_note"):
            ra["rounding_note"] = r["rounding_note"]
        suffix = "" if len(results) == 1 else f"-{r['tag']}"
        add("result", rid("result", slug + suffix), f"{name}{'' if len(results) == 1 else ', ' + r['tag_name']}",
            "Developer-reported value transcribed from a figure label in the pinned Ladon technical report; not reproduced.",
            ra, links=[("evaluation", eid)], facets=facets)


SYS = {
    "Ladon + clinical covariates": None, "Ladon": None,
    "Differential gene expression": M_DGE, "DGE": M_DGE, "Hallmark GSEA": M_GSEA, "Isoform TPM": M_ISOTPM, "TPM · matched TCGA": M_ISOTPM,
    "Clinical covariates (BMRetriever)": C_BMR, "BulkRNABert": C_BULKRNABERT, "BulkFormer": C_BULKFORMER,
    "Gene TPM": M_GENETPM, "PD-L1 mRNA": M_PDL1, "T-effector / IFN-γ": M_TEFF, "IMPRES": M_IMPRES, "TIDE": M_TIDE,
}


def slugify(s):
    import re
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("γ", "gamma").replace("+", " plus ")).strip("-")


# Figure 2
fig2_sys = dict(SYS, **{"Ladon + clinical covariates": C_TRANSFER_CLIN, "Ladon": C_TRANSFER})
fig2_adapt = {
    C_TRANSFER: "Survival-mid-trained frozen encoder; ridge Cox on standardised embeddings fitted on all source samples",
    C_TRANSFER_CLIN: "Concatenated Ladon and BMRetriever-7B embeddings; one ridge Cox fitted on all source samples",
    M_DGE: "Gene signature fitted within the source cohort; signature size by training-data cross-validation",
    M_GSEA: "Hallmark pathway enrichment signature fitted within the source cohort",
    M_ISOTPM: "Isoform TPM features with the same source-fitted Cox procedure",
    C_BMR: "BMRetriever-7B clinical-text embeddings with the same source-fitted Cox procedure",
    C_BULKRNABERT: "BulkRNABert embeddings with the same source-fitted Cox procedure",
    C_BULKFORMER: "BulkFormer 147M embeddings with the same source-fitted Cox procedure",
}
panels = [("TCGA → CPTAC", "t2c", "tcga-to-cptac", rid("data", "cptac-transfer-targets"), "TCGA to CPTAC", "Fitted on TCGA, applied unchanged to six CPTAC cancers", "Equal mean of six cancer-specific C-indices"),
          ("CPTAC → TCGA", "c2t", "cptac-to-tcga", rid("data", "tcga-transfer-targets"), "CPTAC to TCGA", "Fitted on CPTAC, applied unchanged to six TCGA cancers", "Equal mean of six cancer-specific C-indices"),
          ("Pan-Cancer", "pan", "pan-cancer", rid("data", "tcga-cptac-transfer-both"), "pan-cancer", "Both directions; one pan-cancer C-index per direction", "Equal mean of two pan-cancer C-indices")]
for row in FIG["fig2"]:
    sysid = fig2_sys[row["row"]]
    for col, pkey, pslug, data, cname, split, agg in panels:
        printed = row["values"][col]
        evaluate(f"fig2-{slugify(row['row'])}-{pslug}", f"{row['row']}, survival transfer {cname}, Uno C-index", sysid, PR[pkey], data,
                 comp(PR[pkey], split, "Patients of the six target cancers with matched expression", "Bulk RNA-seq (or clinical text for the clinical baseline)",
                      fig2_adapt[sysid], agg, UNO, dataset_version="TCGA and CPTAC as used in the report (release not stated)"),
                 f"Figure 2 (page 6), row '{row['row']}', panel '{col}'",
                 [{"printed": printed, "metric": "concordance-index", "direction": "higher", "unit": "unitless",
                   "qualifier": None, "locator": f"Figure 2 (page 6), row '{row['row']}', panel '{col}' ('{ 'Mean of 2 transfers' if pkey == 'pan' else '6 cancer cohorts'}'), bar label",
                   "unc_note": "Dots and bars only; no interval is printed."}])

def fix_qualifiers():
    """Results without their own qualifier take the protocol's, so the wording lives in one place."""
    PROTO_QUAL = {r["id"]: r["attributes"].get("metric_qualifier") for r in records if r["kind"] == "protocol"}
    EVAL_PROTO = {r["id"]: r["attributes"]["protocol"] for r in records if r["kind"] == "evaluation"}
    for r in records:
        if r["kind"] == "result" and not r["attributes"].get("metric_qualifier"):
            e = r["links"][0]["target_id"]
            r["attributes"]["metric_qualifier"] = PROTO_QUAL[EVAL_PROTO[e]]


fix_qualifiers()

# Figure 3
fig3_sys = dict(SYS, **{"Ladon + clinical covariates": C_TRIAL_CLIN, "Ladon": C_TRIAL})
fig3_adapt = {
    C_TRIAL_CLIN: "Sum of standardised Ladon and clinical-covariate risk scores (Ladon alone in IMbrave150)",
    C_TRIAL: "Survival-supervised frozen encoder; ridge Cox, lambda = 0.3, fitted on TCGA and other trials",
    M_DGE: "DGE risk signature fitted on the training pool",
    M_ISOTPM: "Isoform TPM, 100 principal components, elastic-net Cox fitted on cancer-matched TCGA cohorts (CPTAC lung for IMpower133)",
    C_BMR: "Clinical-covariate embeddings, ridge Cox with the fixed penalty",
    C_BULKRNABERT: "BulkRNABert embeddings, ridge Cox, lambda = 0.3",
    C_BULKFORMER: "BulkFormer embeddings, ridge Cox, lambda = 0.3",
}
for row in FIG["fig3"]:
    sysid = fig3_sys[row["row"]]
    clin = row["row"].startswith("Clinical covariates")
    for ep, pkey, data, ntr in [("OS", "os_hr", rid("data", "trials-os-six"), 6), ("PFS", "pfs_hr", rid("data", "trials-pfs-three"), 3)]:
        scored = ntr - 1 if clin else ntr
        cov = {"scored": scored, "eligible": ntr, "unit": "trials",
               "note": "IMbrave150 has no patient-specific clinical covariates, so its clinical-only hazard ratio is not estimable." if clin else
                       ("IMbrave150 uses Ladon alone in the combined predictor." if sysid == C_TRIAL_CLIN else "All trials estimable.")}
        evaluate(f"fig3-{slugify(row['row'])}-{ep.lower()}", f"{row['row']}, held-out trials {ep} hazard ratio", sysid, PR[pkey], data,
                 comp(PR[pkey], "Held-out trial; predictor fitted on TCGA and the other trials", f"{ntr} trials with {ep} readouts",
                      "Pretreatment bulk RNA-seq (or clinical text for the clinical baseline)", fig3_adapt[sysid],
                      f"Equal-trial geometric mean over {ntr} trials", "Median split of predicted risk; unpenalised Cox with binary group indicator stratified by arm, Efron ties"),
                 f"Figure 3 (page 7), row '{row['row']}', label '{ep}'",
                 [{"printed": row["values"][ep], "metric": "hazard-ratio", "direction": "higher", "unit": "unitless", "qualifier": None,
                   "locator": f"Figure 3 (page 7), row '{row['row']}', label '{ep} {row['values'][ep]}'",
                   "unc_note": "Per-trial dots and a bar only; no interval is printed."}], coverage=cov)
fix_qualifiers()

# Figure 4
r4 = FIG["fig4"][0]
evaluate("fig4-ladon-plus-clinical-oak-os", "Ladon + clinical covariates, OAK overall survival, Uno C-index", C_TRIAL_CLIN, PR["oak"], rid("data", "trials-oak"),
         comp(PR["oak"], "Held-out trial; risk predictor fitted on other cohorts", "699 OAK patients", "Pretreatment bulk RNA-seq and clinical covariates",
              "Ladon combined with clinical covariates", "Single trial", UNO),
         "Figure 4 caption (page 8)",
         [{"printed": r4["values"]["Uno C-index in OAK"], "metric": "concordance-index", "direction": "higher", "unit": "unitless", "qualifier": None,
           "locator": "Figure 4 caption (page 8), '(Uno’s C-index in OAK, 0.61)'",
           "limitations": ["The caption says 'Ladon combined with clinical covariates' fitted on other cohorts; it does not say this is the same predictor as the Figure 3 combined row. Assigned to that configuration on that reading."]}])
fix_qualifiers()

# Figure 5
fig5_sys = {"Ladon": C_POOL, "DGE": M_DGE, "Hallmark GSEA": M_GSEA}
for row in FIG["fig5"]:
    sysid = fig5_sys[row["row"]]
    evaluate(f"fig5-{slugify(row['row'])}-plus-trials", f"{row['row']}, held-out trials OS Uno C-index, largest training pool", sysid, PR["pool"], rid("data", "trials-os-six"),
             comp(PR["pool"], "Held-out trial; fitted on TCGA, non-trial cohorts and other trials (17,378 to 17,929 samples)", "Six OS trials",
                  "Pretreatment bulk RNA-seq", "Ridge Cox, lambda = 0.3, on fixed Ladon embeddings" if sysid == C_POOL else "Signature fitted within the same training pool",
                  "Mean over six trials weighted by evaluated patients", UNO),
             "Figure 5 (page 9) legend",
             [{"printed": row["values"]["+ trials"], "metric": "concordance-index", "direction": "higher", "unit": "unitless", "qualifier": None,
               "locator": f"Figure 5 (page 9), legend '{row['row']} {row['values']['+ trials']}', training stage '+ trials' (about 18k samples)",
               "note": "The legend values match the third training stage in the web figure data (size-weighted value, not the equal-trial mean)."}])
fix_qualifiers()

# Figure 6
fig6_sys = dict(SYS, **{"Ladon": C_RESPONSE})
fig6_adapt = {
    C_RESPONSE: "Response-mid-trained encoder; PCA 128 on context patients; TabICL v2 with 1,419 academic-cohort patients plus the other trials as context",
    M_DGE: "Response signature fitted with five-fold CV within the context data",
    M_GENETPM: "Log2(TPM + 1) of 20,250 protein-coding genes, PCA, TabICL with academic cohorts alone as context",
    M_PDL1: "CD274 expression, no fitting",
    M_TEFF: "Published signature score", M_IMPRES: "Published score", M_TIDE: "Published score, sign-reversed",
    C_BMR: "Clinical-text embeddings, same PCA and TabICL procedure; constant score in IMbrave150",
    C_BULKRNABERT: "BulkRNABert embeddings, same PCA and TabICL procedure as Ladon",
    C_BULKFORMER: "BulkFormer embeddings, same PCA and TabICL procedure as Ladon",
}
for row in FIG["fig6"]:
    sysid = fig6_sys[row["row"]]
    lim = []
    if sysid == M_TEFF:
        lim = ["The web figure notes that this signature was derived on POPLAR, so its POPLAR AUROC is in-sample; the PDF does not say so."]
    if sysid in (M_IMPRES, M_TIDE):
        lim = ["The web figure notes that this score was developed on melanoma immunotherapy cohorts, outside these trials' setting."]
    if sysid == M_GENETPM:
        lim = ["Academic cohorts alone as context, whereas Ladon's context also includes the other trials (page 16)."]
    evaluate(f"fig6-{slugify(row['row'])}-response", f"{row['row']}, held-out trials immunotherapy response AUROC", sysid, PR["resp"], rid("data", "trials-response-six"),
             comp(PR["resp"], "Held-out trial; evaluated trial excluded from context", "Immunotherapy arms of six trials, evaluable RECIST response",
                  "Pretreatment bulk RNA-seq (or clinical text for the clinical baseline)", fig6_adapt[sysid], "Equal mean of six trial AUROCs", "AUROC within each trial"),
             "Figure 6 (page 10)",
             [{"printed": row["values"]["Response AUROC"], "metric": "auroc", "direction": "higher", "unit": "unitless", "qualifier": None,
               "locator": f"Figure 6 (page 10), row '{row['row']}', bar label", "unc_note": "Per-trial dots and a bar only; no interval is printed."}],
             eval_limitations=lim)
fix_qualifiers()

# Figure 11
CI_T = "percentile bootstrap with predictions held fixed, tumours resampled"
for row in FIG["fig11"]:
    sysid = {"Ladon": C_ISOFORM, "cohort-trained baseline": M_COHORT_RIDGE, "cohort mean": M_COHORT_MEAN}[row["row"]]
    adapt = {C_ISOFORM: "Gene-level expression in, isoform split imputed by the pretrained model", M_COHORT_RIDGE: "Ridge regression fitted on the cohort's own isoform measurements with five-fold cross-validation", M_COHORT_MEAN: "Cohort mean split"}[sysid]
    if "r" in row["values"]:
        lo, hi = row["values"]["r_ci"]
        evaluate(f"fig11-{slugify(row['row'])}-insr-r", f"{row['row']}, INSR isoform split in 166 stomach tumours, Pearson r", sysid, PR["insr_r"], rid("data", "tcga-stomach-insr"),
                 comp(PR["insr_r"], "Held-out cohort (TCGA excluded from pretraining)", "166 TCGA stomach tumours", "Gene-level expression", adapt, "Across tumours", "Pearson r"),
                 "Figure 11 (page 24) readout",
                 [{"printed": row["values"]["r"], "metric": "pearson-correlation", "direction": "higher", "unit": "unitless", "qualifier": None,
                   "locator": f"Figure 11 (page 24) readout 'r with measured', '{row['row']}'",
                   "uncertainty": {"type": "confidence_interval", "level": 0.95, "lower": lo, "upper": hi, "method": "bootstrap_percentile", "note": CI_T, "resamples": 2000, "printed": row["printed"]["r"]}}])
    evaluate(f"fig11-{slugify(row['row'])}-insr-mae", f"{row['row']}, INSR isoform split in 166 stomach tumours, MAE", sysid, PR["insr_mae"], rid("data", "tcga-stomach-insr"),
             comp(PR["insr_mae"], "Held-out cohort (TCGA excluded from pretraining)", "166 TCGA stomach tumours", "Gene-level expression", adapt, "Across tumours", "Mean absolute error"),
             "Figure 11 (page 24) readout",
             [{"printed": row["values"]["MAE"], "metric": "mean-absolute-error", "direction": "lower", "unit": "percent", "unit_detail": "percentage points of the gene's RNA ('MAE, points')",
               "qualifier": None, "locator": f"Figure 11 (page 24) readout 'MAE, points', '{row['row']}'",
               "unc_note": "The caption says intervals are given, but none is printed for MAE."}])
fix_qualifiers()

# Figure 12a
fig12_sys = {"Ladon": C_ISOFORM, "Cohort-trained baseline": M_COHORT_RIDGE, "Linear model on public data": M_PUB_RIDGE, "Nearest public samples": M_NEAREST}
for row in FIG["fig12a"]:
    sysid = fig12_sys[row["row"]]
    evaluate(f"fig12a-{slugify(row['row'])}", f"{row['row']}, isoform variation in eight held-out cancer types, median Pearson r", sysid, PR["iso3000"], rid("data", "tcga-isoform-eight-types"),
             comp(PR["iso3000"], "Held-out cancer types (TCGA excluded from pretraining)", "1,572 tumours, 14,526 gene and cancer-type combinations", "Gene-level expression",
                  {C_ISOFORM: "Pretrained model imputation", M_COHORT_RIDGE: "Ridge fitted on each cohort's own isoform measurements, five-fold CV",
                   M_PUB_RIDGE: "Ridge fitted on public reference", M_NEAREST: "Mean of 20 nearest public samples"}[sysid],
                  "Median over gene and cancer-type pairs", "Pearson r on centred percentages"),
             "Figure 12a (page 25)",
             [{"printed": row["values"]["median Pearson r"], "metric": "pearson-correlation", "direction": "higher", "unit": "unitless", "qualifier": None,
               "locator": f"Figure 12a (page 25), row '{row['row']}', point label",
               "unc_note": "The caption says the 95% bootstrap intervals are narrower than the symbols; no interval is printed."}])
fix_qualifiers()

# Figure 13
fig13_sys = {"Ladon": C_ISOFORM, "Organ average": M_ORGAN, "Nearest public samples": M_NEAREST, "Linear model on public data": M_PUB_RIDGE}
for row in FIG["fig13"]:
    sysid = fig13_sys[row["row"]]
    evaluate(f"fig13-{slugify(row['row'])}", f"{row['row']}, ENCODE4 organ-pair isoform change, Pearson r", sysid, PR["encode"], rid("data", "encode4-organ-pairs"),
             comp(PR["encode"], "Evaluation only", "1,402 within-donor organ-pair comparisons", "Corrected single-nucleus gene counts (organ label for the lookup)",
                  {C_ISOFORM: "Pretrained model imputation", M_ORGAN: "Mean split of public samples with the organ label", M_NEAREST: "Mean of 50 nearest public samples",
                   M_PUB_RIDGE: "Ridge fitted on public reference"}[sysid], "Pearson r across all comparisons", "Pearson r of predicted against measured change"),
             "Figure 13 (page 26) right panel",
             [{"printed": row["values"]["Pearson r"], "metric": "pearson-correlation", "direction": "higher", "unit": "unitless", "qualifier": None,
               "locator": f"Figure 13 (page 26), right panel, row '{row['row']}'; page 27 prose",
               "unc_note": "Drawn as error bars; no interval is printed."}])
fix_qualifiers()

# Figure 14
fig14_sys = {"Ladon": C_ISOFORM, "Isoform quantification from 10x reads": M_KALLISTO}
for row in FIG["fig14"]:
    sysid = fig14_sys[row["row"]]
    for col, pkey, tag in [("Day 0 → 14", "blood_t", "day0-14"), ("COVID-19 vs healthy", "blood_c", "covid-vs-healthy")]:
        evaluate(f"fig14-{slugify(row['row'])}-{tag}", f"{row['row']}, blood isoform direction accuracy, {tag.replace('-', ' ')}, top 5% of genes", sysid, PR[pkey], rid("data", "giroux-blood-draws"),
                 comp(PR[pkey], "Evaluation only", "460 genes (top 5% by measured change)", "Pooled single-cell reads per draw (gene counts per million for Ladon)",
                      "Pretrained model imputation from summed gene counts" if sysid == C_ISOFORM else "kallisto isoform estimates from the same pooled reads",
                      "Share of genes", "Sign agreement with the bulk-reference change"),
                 "Page 27 prose; Figure 14",
                 [{"printed": row["values"][col], "metric": "accuracy", "direction": "higher", "unit": "percent", "qualifier": None,
                   "locator": f"Page 27, paragraph beginning 'Finally, we analyzed 35 blood draws', value for '{row['row']}' ({'over time' if tag == 'day0-14' else 'between COVID-19 and healthy controls'})",
                   "coverage": {"scored": 460, "eligible": 460, "unit": "genes", "note": "Top 5% of 9,207 expressed multi-isoform genes"}}])
fix_qualifiers()

# Figure 17 accuracy
fig17_sys = {"EPIC": M_EPIC, "ABIS": M_ABIS, "BayesPrism": M_BAYESPRISM, "CIBERSORT": M_CIBERSORT, "DWLS": M_DWLS, "Ladon": C_DECONV}
fig17_adapt = {M_EPIC: "Published BRef reference from sorted-cell bulk RNA-seq, run on TPM", M_ABIS: "Published RNA-seq signature, robust linear regression",
               M_BAYESPRISM: "Four scBaseCount PBMC single-cell references", M_CIBERSORT: "1,000-gene signature from the four single-cell references",
               M_DWLS: "1,000-gene signature from the four single-cell references", C_DECONV: "Composition-post-trained Ladon, PCA 64, TabICL regressors trained on 2,000 synthetic bulks"}
for row in FIG["fig17_accuracy"]:
    sysid = fig17_sys[row["row"]]
    for col, pkey, tag, metric in [("Pearson r", "pbmc_r", "pearson", "pearson-correlation"), ("Pairwise ordering accuracy", "pbmc_o", "ordering", "concordance-index")]:
        evaluate(f"fig17-{slugify(row['row'])}-{tag}", f"{row['row']}, PBMC deconvolution, {col.lower()}", sysid, PR[pkey], rid("data", "giroux-pbmc-bulk"),
                 comp(PR[pkey], "Evaluation only", "35 PBMC bulks, 17 donors, five lineages", "PBMC bulk RNA-seq", fig17_adapt[sysid], "Mean over five lineages", col),
                 "Figure 17 (page 33) bottom chart",
                 [{"printed": row["values"][col], "metric": metric, "direction": "higher", "unit": "unitless", "qualifier": None,
                   "locator": f"Figure 17 (page 33), bottom chart, row '{row['row']}', column '{col}'",
                   "unc_reason": "unextracted", "unc_note": "95% intervals are drawn as bars; their values appear only in the web version's collapsed data table, not in the PDF."}])
fix_qualifiers()

# Figure 17 per-lineage
for row in FIG["fig17_lineage"]:
    sysid = fig17_sys[row["row"]]
    results = [{"printed": v, "metric": "pearson-correlation", "direction": "higher", "unit": "unitless",
                "qualifier": f"Pearson r between inferred and measured {lin} share across 35 PBMC bulks",
                "locator": f"Figure 17 (page 33), top panel '{lin}', label 'r {FIG['fig17_lineage'][0]['values'][lin]} {FIG['fig17_lineage'][1]['values'][lin]}', {'first' if row['row'] == 'Ladon' else 'second'} value ({row['row']})",
                "tag": slugify(lin), "tag_name": lin} for lin, v in row["values"].items()]
    evaluate(f"fig17-{slugify(row['row'])}-lineage", f"{row['row']}, PBMC deconvolution per-lineage Pearson r", sysid, PR["pbmc_lin"], rid("data", "giroux-pbmc-bulk"),
             comp(PR["pbmc_lin"], "Evaluation only", "35 PBMC bulks, 17 donors", "PBMC bulk RNA-seq", fig17_adapt[sysid], "Per lineage, no aggregation", "Pearson r"),
             "Figure 17 (page 33) top panels", results)

# Figure 18
fig18_sys = {"Ladon deconvolution": C_PCR, "Oncotype DX*": M_ONCO, "MammaPrint*": M_MAMMA, "HER2 expression": M_ERBB2}
fig18_data = {("ER+/HER2−", "ARTEMIS"): rid("data", "artemis-er-pos"), ("ER+/HER2−", "PBCP"): rid("data", "pbcp-er-pos"),
              ("HER2+", "PBCP"): rid("data", "pbcp-her2-pos"), ("HER2+", "DFCI IBC"): rid("data", "dfci-ibc")}
for row in FIG["fig18"]:
    sysid = fig18_sys[row["row"]]
    pkey = "pcr_er" if row["group"] == "ER+/HER2−" else "pcr_her2"
    grp = "ER+/HER2-" if pkey == "pcr_er" else "HER2+"
    lo, hi = row["values"]["ci"]
    extra = {}
    if row["cohort"] == "DFCI IBC" and sysid == C_PCR:
        extra = {"source_discrepancy": "Figure 18 prints 0.73 [0.50, 0.93]; the page 34 prose says 0.74. The web figure data holds 0.735, so the two are the same value rounded differently.",
                 "rounding_note": "Stored as printed in the figure (0.73); the prose rounds the same value to 0.74."}
    gtag = "er-pos-her2-neg" if pkey == "pcr_er" else "her2-pos"
    evaluate(f"fig18-{slugify(row['row'])}-{slugify(row['cohort'])}-{gtag}", f"{row['row']}, {row['cohort']} {grp}, pCR AUC", sysid, PR[pkey], fig18_data[(row["group"], row["cohort"])],
             comp(PR[pkey], "External cohort; model fitted on TransNEO", f"{row['cohort']} {grp} patients", "Pretreatment bulk RNA-seq",
                  {C_PCR: "Inferred 12-class composition, L2 logistic regression fitted on TransNEO", M_ONCO: "genefu oncotypedx on log2(TPM + 1), no fitting",
                   M_MAMMA: "genefu gene70 on log2(TPM + 1), no fitting", M_ERBB2: "ERBB2 log2(1 + TPM), no fitting"}[sysid], "Single cohort", "AUC"),
             "Figure 18 (page 35)",
             [{"printed": row["values"]["AUC"], "metric": "auroc", "direction": "higher", "unit": "unitless", "qualifier": None,
               "locator": f"Figure 18 (page 35), panel '{row['group'].replace('−', '-')}' cohort '{row['cohort']}', row '{row['row']}', column 'AUC [95% CI]'",
               "uncertainty": {"type": "confidence_interval", "level": 0.95, "lower": lo, "upper": hi, "method": "bootstrap_percentile", "note": "Percentile bootstrap resampling the cohort's patients; resamples with a single class discarded (page 39).",
                               "resamples": 2000, "printed": row["printed"]}, **extra}])
fix_qualifiers()

# --------------------------------------------------------------------------------------------
# Claims
# --------------------------------------------------------------------------------------------


def claim(slug, subject, field, value, locator, rationale=None, sources=(S_PDF,), limitations=(), sha=PDF_SHA, url=PDF_URL):
    a = {"field": field, "value": value, "source_locator": locator,
         "review": review("Transcribed from the cited text.", sha=sha, url=url, method=("pdf-text-parse", "source-hash-verification") if sha == PDF_SHA else ("automated-source-review", "source-hash-verification"))}
    if rationale:
        a["rationale"] = rationale
    if limitations:
        a["limitations"] = list(limitations)
    return add("claim", rid("claim", slug), f"Ladon report: {field.replace('_', ' ')}", "Descriptive fact transcribed from the pinned source with its own locator.",
               a, links=[("subject", subject)], source_ids=list(sources), facets={})


claim("architecture", M_LADON, "architecture", "3-billion-parameter transformer encoder-decoder", "Page 2, 'Introducing Ladon', first sentence")
claim("pretraining", M_LADON, "pretraining_objective",
      "Pretrained with masked token reconstruction on isoform-level sequences of millions of bulk RNA-seq samples; self-supervised, so unlabelled samples are used",
      "Page 2, 'Introducing Ladon'", limitations=["The pretraining corpus, its sources and its size beyond 'millions' are not listed."])
claim("mid-training", M_LADON, "supervised_mid_training",
      "Before downstream use the encoder is mid-trained to predict patient and tumour characteristics (disease stage, age, tumour grade, genomic alterations) alongside clinical outcomes; the prediction heads are then discarded and the encoder kept fixed",
      "Page 11, Methods 'Ladon representations'",
      rationale="Different experiments use different mid-trained or post-trained states (survival-supervised, response-supervised, composition post-trained, pretrained only), none named as a checkpoint.")
claim("access", M_LADON, "access", ACCESS_NOTE, "Page 43, Conclusion, last sentence; Zenodo record Rights field",
      rationale="Rechecked on 2026-11-15, not taken from the issue. Report availability on Zenodo is not a model licence.")
claim("access-blog", M_LADON, "access_offer",
      "The announcement offers 'Want to run Ladon on your cohorts? Tell us about your trial and what you want to predict. We'll pay for the RNA sequencing.' and a contact form; no download is offered",
      "Introducing Ladon, 'Work with us' panel", sources=[S_BLOG], sha=BLOG_SHA, url="https://www.blank.bio/introducing-ladon")
claim("no-checkpoint", M_LADON, "checkpoint_identity",
      "No checkpoint, model size per experiment or version is named. Figures 20 and 21 compare several model sizes and training steps, but are images with no values in the text layer",
      "Pages 41 to 43, Figures 20 and 21 and Methods 'Reconstruction loss' and 'Clinical benchmark'")
claim("statistics", S_PDF, "significance_testing",
      "Comparisons with Ladon use one-sided paired Wilcoxon signed-rank tests over six (or fewer) trials or cancers; p-values are unadjusted for multiple comparisons; stars mark p < 0.05 and exact values are available only on hover in the web version",
      "Page 11, Methods 'Statistics'; captions of Figures 5 and 6",
      rationale="Extractor note, not source text: with six paired units a one-sided Wilcoxon test cannot reach p < 0.05 unless Ladon wins in at least five of six; the PDF does not print which comparisons were starred in a way the text layer ties to rows.")
claim("dagger-unexplained", PR["t2c"], "figure_symbol",
      "In Figure 2 the rows 'Differential gene expression' and 'Hallmark GSEA' carry a double dagger (‡) that the PDF does not explain; it applies to all three panels",
      "Figure 2 (page 6), row labels")
claim("transfer-heldout", PR["t2c"], "held_out_protection",
      "TCGA and CPTAC outcome labels are excluded from Ladon's encoder supervision and validation monitoring; the mid-trained encoder is trained on survival outcomes from other cohorts",
      "Page 11, Methods 'Transfer between TCGA and CPTAC'",
      limitations=["Whether TCGA or CPTAC expression profiles were in the self-supervised pretraining corpus is not stated for this experiment; for the isoform experiments the report says pretraining excluded TCGA."])
claim("clinical-imbrave", C_TRIAL_CLIN, "imbrave150_handling",
      "IMbrave150 has no patient-specific clinical covariates; its clinical-only hazard ratio is not estimable, the clinical-only summaries cover five OS and two PFS trials, and the combined predictor uses Ladon alone for IMbrave150",
      "Pages 13 and 14, Methods 'Survival in held-out trials'")
claim("oak-medians", PR["oak"], "median_survival_split",
      "Splitting OAK at the median predicted risk of Ladon + clinical covariates gives median overall survival of 7.9 months in the higher-risk half (n = 349) and 15.5 months in the lower-risk half (n = 350); dashed predicted curves are calibrated using OAK outcomes",
      "Page 7 prose; Figure 4 (page 8) and caption",
      limitations=["The dashed predicted curves use OAK outcomes for calibration, so they are not out-of-sample predictions; the C-index (0.61) is the out-of-sample measure."])
claim("pool-transition", PR["pool"], "training_pool_confound",
      "The first transition in Figure 5, from cancer-matched cohorts to all TCGA, changes both the training data and the fitting procedure (unstratified elastic-net Cox to ridge Cox with per-project baseline hazards)",
      "Page 14, last sentence of 'Additional labeled cohorts'; stage table")
claim("response-context-asymmetry", PR["resp"], "reference_data_parity",
      "Ladon's in-context examples are 1,419 patients from 33 academic cohorts plus patients from the other trials, and its encoder was mid-trained with response labels from academic cohorts; the gene-expression (gene TPM) baseline uses academic cohorts alone as context. BulkRNABert, BulkFormer and BMRetriever 'use the same PCA and TabICL procedure as Ladon'; whether their context includes the other trials is not stated explicitly, nor which context the DGE signature is fitted in",
      "Pages 15 and 16, Methods 'Immunotherapy response'")
claim("response-blog-finetune", C_RESPONSE, "adaptation_description_conflict",
      "The announcement says 'We fine-tune Ladon on academic immunotherapy cohorts' and that Ladon 'significantly outperforms all baselines'. The report describes supervised mid-training with academic response labels followed by a frozen encoder, PCA and TabICL, and its tests are one-sided and unadjusted",
      "Introducing Ladon, section 'Ladon Predicts Response in Held-Out Clinical Trials'; report pages 11, 15 and 16",
      sources=[S_BLOG, S_PDF], sha=BLOG_SHA, url="https://www.blank.bio/introducing-ladon",
      rationale="Recorded so the announcement's wording is not read as a description of the method or as a multiplicity-adjusted finding.")
claim("teffector-in-sample", M_TEFF, "in_sample_trial",
      "The T-effector signature was derived on POPLAR, so its POPLAR result is in-sample",
      "Web Figure 6 page, DATA master.panel_f.rows, row 'T-effector / IFN-γ', field note", sources=[S_FIG06, S_PDF], sha=FIG06_SHA,
      url="https://www.blank.bio/assets/ladon-white-paper/fig06-response-prediction.html",
      rationale="The PDF does not print this note.")
claim("impres-setting", M_IMPRES, "development_setting",
      "IMPRES was developed on melanoma immunotherapy cohorts; these trials are outside that development setting",
      "Web Figure 6 page, DATA master.panel_f.rows, row 'IMPRES', field note", sources=[S_FIG06, S_PDF], sha=FIG06_SHA,
      url="https://www.blank.bio/assets/ladon-white-paper/fig06-response-prediction.html")
claim("tide-setting", M_TIDE, "development_setting",
      "TIDE was developed on melanoma anti-PD-1 / CTLA-4 cohorts; these trials are outside that development setting. The score is sign-reversed so higher values indicate expected response",
      "Web Figure 6 page, DATA master.panel_f.rows, row 'TIDE', field note", sources=[S_FIG06, S_PDF], sha=FIG06_SHA,
      url="https://www.blank.bio/assets/ladon-white-paper/fig06-response-prediction.html")
claim("genetpm-label", M_GENETPM, "web_label",
      "The web figure labels this row 'Gene TPM · academic only', confirming that its context is academic cohorts alone",
      "Web Figure 6 page, DATA master.panel_f.rows, label 'Gene TPM · academic only'", sources=[S_FIG06, S_PDF], sha=FIG06_SHA,
      url="https://www.blank.bio/assets/ladon-white-paper/fig06-response-prediction.html")
claim("benefit-design", T_BENEFIT, "analysis_design",
      "A benefit head on frozen Ladon embeddings estimates how the treatment-minus-control difference in 12-month PFS varies with molecular features (R-learning, Nie and Wager 2021), after a Ladon-derived score regresses out prognosis in both arms. Source trials: IMmotion150, IMmotion151, IMbrave150, OAK and IMpower133; five-fold cross-fitting with censoring-weighted logistic regression; ridge penalties 10^-4 to 10^3 chosen by leave-one-source-trial-out R-loss. Applied to POPLAR (atezolizumab against docetaxel)",
      "Page 18 and page 22, Methods 'Benefit learning and target evaluation'",
      limitations=["Retrospective, one target trial (POPLAR, 192 RNA-profiled patients), no interval or interaction test printed for the benefit separation."])
claim("benefit-gaps", T_BENEFIT, "poplar_12_month_pfs_gap",
      "Ladon score in POPLAR: 12-month PFS high-low gap 22.1 percentage points in the atezolizumab arm and 1.3 percentage points in the docetaxel arm; 28% against 6% progression-free at 12 months on atezolizumab, 14% against 13% on docetaxel. Patients at risk at month 0: atezolizumab high 43, low 52; docetaxel high 53, low 44",
      "Figure 8 (page 18), panel 'Ladon + TCGA' headers and at-risk tables; page 18 prose",
      rationale="Kept as a claim: no metric concept fits a difference in Kaplan-Meier proportions between score groups, and the analysis is a single retrospective trial.",
      limitations=["28 minus 6 is 22 and 14 minus 13 is 1, consistent with the printed gaps up to rounding of the Kaplan-Meier estimates.",
                   "Score groups use one whole-cohort median shared between arms."])
claim("benefit-comparators", T_BENEFIT, "comparator_gaps_printed",
      "The comparator panel of Figure 8 prints 12-month high-low gaps of -2.0 percentage points (atezolizumab) and -2.6 percentage points (docetaxel) for its default selection. The panel header lists PD-L1 mRNA, AP/T, Plasma-cell and TLS3 as toggles and the PDF does not mark which is selected; values for the other three comparators are not printed",
      "Figure 8 (page 19), comparator panel",
      rationale="The default is probably PD-L1 mRNA, the first toggle, but the PDF does not say so; not assigned to a comparator.")
claim("benefit-blog-sources", T_BENEFIT, "training_data_description_conflict",
      "The announcement says the POPLAR predictive score was built 'Using external data collected from academic cohorts and other immunotherapy trials'; the report's Methods list five trials (IMmotion150, IMmotion151, IMbrave150, OAK, IMpower133) as the benefit head's sources and name no academic cohorts",
      "Introducing Ladon, section 'Ladon Finds Robust Predictive Biomarkers From External Data'; report page 22",
      sources=[S_BLOG, S_PDF], sha=BLOG_SHA, url="https://www.blank.bio/introducing-ladon")
claim("association-counts", T_BENEFIT, "marker_association_counts",
      "Prose: of 304 marker-PFS associations significant before adjustment for Ladon prognosis, 24 remained significant (Benjamini-Hochberg within trial, arm and condition over 550 markers). Figure 7 prints '106 significant' and '0 retained' for its default trial selection; its toggle lists POPLAR, OAK and IMmotion151, while the Methods analyse four trials including IMmotion150; its caption says '550 total' although only markers significant before adjustment are displayed",
      "Page 17 prose; Figure 7 (page 17) and caption; page 20, Methods 'Association models and endpoints'",
      rationale="The figure's 106 and 0 are not tied to a named trial in the PDF, and the caption's 550 is the size of the screened marker family, not the number displayed.")
claim("fig9-unprinted", T_BENEFIT, "response_stratification",
      "Figure 9 shows objective response rates in high- and low-score groups of the POPLAR atezolizumab arm (87 of 95 patients with evaluable response) but prints no rate values",
      "Figure 9 (page 20) and caption")
claim("isoform-pretraining-overlap", T_ISO, "held_out_protection",
      "Pretraining excluded the TCGA cohorts and included the ENCODE4 and blood bulk reference libraries; Ladon received gene-level expression only",
      "Page 28, Methods 'Model input'",
      rationale="For Figures 13 and 14 the bulk isoform estimates used as ground truth come from libraries that were in pretraining; only the TCGA analyses (Figures 11 and 12) are held out from pretraining.")
claim("isoform-win-shares", PR["iso3000"], "ladon_higher_share",
      "Ladon's Pearson r is higher than the cohort-trained baseline's in 95.1% of the 14,526 gene and cancer-type combinations, and higher than the linear model on public data and the nearest public samples in 99.7% each",
      "Figure 12a (page 25), 'Ladon higher in' labels",
      rationale="Pairwise comparison shares, kept as claims rather than results of a single system.")
claim("isoform-five-genes", PR["iso3000"], "five_gene_comparison",
      "In the five-gene analysis (CD44, INSR, KRAS, MKNK2, TPM1 in the five cancer types where at least four are eligible) Ladon exceeded the cohort-trained baseline in all 21 gene and cancer-type combinations; Figure 12b prints no values",
      "Page 24 prose; Figure 12b (page 25)")
claim("blood-all-genes", T_ISO, "all_gene_direction_accuracy",
      "At the cutoff including all 9,207 expressed multi-isoform genes, Ladon's direction accuracy is 56% against 53% for direct quantification; the text does not say which of the two contrasts these values belong to",
      "Page 27, sentence 'Ladon nevertheless stayed ahead at every cutoff down to all 9,207 expressed multi-isoform genes (56% compared with 53%)'",
      rationale="Not stored as results because the contrast is not named.")
claim("pbmc-heldout", PR["pbmc_r"], "held_out_protection",
      "A random subset of single-cell studies contributed no synthetic bulks to post-training; these held-out studies included the single-cell study paired with the PBMC test bulks",
      "Page 38, Methods 'Ladon post-training'",
      limitations=["Whether the 35 PBMC bulks themselves were in the bulk pretraining corpus is not stated."])
claim("pcr-blog-trials", PR["pcr_er"], "cohort_description",
      "The announcement calls ARTEMIS and PBCP 'two additional trials'; the report treats the four external sets as cohorts from the Sammut et al. (2022) release and GEO GSE207248, with 35, 13, 18 and 22 patients",
      "Introducing Ladon, section 'Ladon Recovers Cell Composition Signal'; report Figure 18 and page 40", sources=[S_BLOG, S_PDF], sha=BLOG_SHA, url="https://www.blank.bio/introducing-ladon")
claim("clinbench-structure", B_CLIN, "task_structure",
      "142 tasks: 85 within-cohort tasks (three-fold cross-validation repeated five times) and 57 cross-cohort survival tasks (trained on the other cohorts of the same cancer type, evaluated on the held-out cohort); survival scored by Harrell's C, classification by AUROC; unweighted mean over all 142",
      "Page 43, Methods 'Clinical benchmark'")
claim("clinbench-no-values", B_CLIN, "printed_results",
      "No ClinBench score is printed: Figures 20 and 21 are images, the text layer carries no values, and the task list is not published",
      "Pages 41 and 42, Figures 20 and 21")

# --------------------------------------------------------------------------------------------
# Write
# --------------------------------------------------------------------------------------------
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
for r in records:
    if r["kind"] == "result":
        assert r["attributes"]["metric_qualifier"], r["id"]
records.sort(key=lambda r: r["id"])
out = os.path.join(os.path.dirname(HERE), "batch.jsonl")
with open(out, "w", encoding="utf-8") as fh:
    for r in records:
        fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
from collections import Counter
print(dict(Counter(r["kind"] for r in records)))
