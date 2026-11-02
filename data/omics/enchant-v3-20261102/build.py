"""Build the Enchant v3 batch (issue #229): three Iambic pages as sources and the Enchant v3 model.

Usage: python3 -I build.py <report.html> <release.html> <platform.html> <batch folder>

The inputs are the pages as served on 2026-11-02, checked by SHA-256. Each statement quoted in the records
is asserted against the page text. The pages are developer-reported; no result is extracted. Figure 7 of the
report prints TM-scores but gives no configuration, split or averaging, so it is recorded as a gap.
Records are written needs_review; review.py records the review.
"""
import hashlib
import html
import json
import os
import re
import sys

REPORT, RELEASE, PLATFORM, OUT = sys.argv[1:5]
SHA = {
    REPORT: "045f05652d2f8986fbf509ea32eda93fc4ec7d7f94e5ebf6bc0aa76b243fa3d8",
    RELEASE: "1c0424831dc79abd3be4024ad0d54d45c2d0c6d7425370f32dfa43e27e63a90f",
    PLATFORM: "c555311e25c43f5d88c6345757045dd73d9cf22779f856713963e85af47b1e6e",
}


def text(path):
    raw = open(path, "rb").read()
    assert hashlib.sha256(raw).hexdigest() == SHA[path], path
    s = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", raw.decode("utf-8"))
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s)


report, release, platform = text(REPORT), text(RELEASE), text(PLATFORM)
for phrase in ("September 21, 2026", "Fred Manby", "Matt Welborn", "a 41-billion parameter model",
               "a mixture-of-experts architecture", "In 2024, we trained Enchant v1 with 1 billion parameters",
               "In 2025, we trained Enchant v2 with 7 billion parameters",
               "molecular and biomolecular structures, sequence and omics data, tabular assay data, physics data, biomedical text, and images",
               "Every Enchant prediction relies on uncertainty quantification",
               "inverse design, omics-based prediction, image-based prediction, and peptides",
               "on held out structures in the CASP14 and CAMEO22 sets",
               "Figure 7: Enchant’s ability to make protein structure predictions compared to other methods.",
               "deploy Enchant v3 to our internal and partner drug discovery work",
               "approximately 12 million inferences per month",
               "IAM-C1", "IAM217"):
    assert phrase in report, phrase
for phrase in ("Pretrained on 4.5 trillion tokens", "6,000+ molecular properties", "16 biomedical modalities",
               "text, assay data, molecule structure, protein structure, 3D structure, images, multi-omics, biologics, clinical trial data, and pharmacokinetics",
               "Sept. 21, 2026"):
    assert phrase in release, phrase
for phrase in ("Enchant, for multimodal endpoint prediction, and NeuralPLexer for protein-ligand structural predictions",
               "Enchant v3 is a tenfold increase in scale"):
    assert phrase in platform, phrase

P = "enchant-v3-20261102"
FACETS = {"areas": ["molecular-interactions"], "contexts": ["research"]}
RETRIEVED = "2026-11-02T10:47:00Z"
LIMIT = "Developer-reported company web page; not peer reviewed, and no independent replication."
records = []


def add(rec):
    records.append(rec)
    return rec["id"]


def source(slug, name, description, url, version, sha, limitations):
    return add({
        "id": f"{P}-source-{slug}", "kind": "source", "name": name, "description": description,
        "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
        "attributes": {
            "url": url, "version": version, "retrieved_at": RETRIEVED, "artifact_sha256": sha,
            "publication_status": "official_project_source", "media_type": "text/html",
            "missing_metadata": {"licence": {"reason": "unreported", "note": "Iambic web page, all rights reserved; hashed, not stored."}},
            "limitations": [LIMIT, *limitations],
        }})


REP = source("report", "Enchant v3: Molecular superintelligence for end-to-end drug R&D (Iambic report)",
             "Iambic's report introducing Enchant v3, by Fred Manby and Matt Welborn, with its architecture, scale, uses in two drug programmes and a structure-prediction comparison.",
             "https://www.iambic.ai/news/enchant-3", "Web page dated 21 September 2026, as served on 2026-11-02", SHA[REPORT],
             ["Figures are SVG artwork with no text layer; Figure 7 prints TM-score labels without model configurations, split or averaging."])
REL = source("release", "Iambic launches Enchant v3 (Iambic press release)",
             "Iambic's press release for Enchant v3, with its parameter count, pretraining tokens, number of molecular properties and modalities.",
             "https://www.iambic.ai/post/iambic-launches-enchant-v3---molecular-superintelligence-designed-to-advance-end-to-end-drug-discovery-development",
             "Press release dated 21 September 2026, as served on 2026-11-02", SHA[RELEASE],
             ["Press release; its figures are not broken down by modality or endpoint."])
PLAT = source("platform", "Iambic platform page",
              "Iambic's platform page, which describes Enchant and NeuralPLexer as the AI parts of its drug discovery platform.",
              "https://www.iambic.ai/platform", "Web page as served on 2026-11-02", SHA[PLATFORM],
              ["Undated page that can change; it gives no access terms for Enchant."])

SRCS = [REP, REL, PLAT]
summary = ("Enchant v3 is Iambic's multimodal transformer for drug discovery. It predicts molecular properties and "
           "preclinical and clinical endpoints from structures, sequences, omics, assay data, text and images, and Iambic "
           "uses it to choose compounds and prioritise experiments.")
profile = {
    "summary": summary,
    "summary_source_ids": [REP, REL],
    "summary_source_locator": f"{REP}: introduction and 'Ingest diverse data'; {REL}: subtitle and highlights",
    "sections": [
        {"title": "How it works",
         "body": ("A mixture-of-experts transformer trained jointly on many data types and endpoints, so that data on one "
                  "endpoint or molecule informs predictions for related ones. Each prediction carries an uncertainty "
                  "estimate, which Iambic uses to decide which experiments to run. The model is fine-tuned each week on "
                  "new laboratory data."),
         "source_ids": [REP], "source_locator": f"{REP}: 'Leverage model scale', 'Convert model outputs into probability-guided decisions', 'How Enchant impacts discovery at Iambic', 'Enchant v3: Achieving scalable predictability'"},
        {"title": "Versions",
         "body": ("Enchant v1 (2024) had 1 billion parameters and Enchant v2 (2025) 7 billion. Enchant v3 has 41 billion. "
                  "New in v3: inverse design, omics-based and image-based prediction, and peptides. Results and access terms "
                  "of v1 or v2 do not carry over to v3. NeuralPLexer is a separate Iambic model for protein-ligand structure."),
         "source_ids": [REP, PLAT], "source_locator": f"{REP}: 'Enchant v3: Achieving scalable predictability'; {PLAT}: platform description"},
    ],
    "facts": [
        {"label": "Parameters", "value": "41 billion", "status": "source_checked", "source_ids": [REP, REL], "source_locator": f"{REP}: 'Enchant v3: Achieving scalable predictability'; {REL}: highlights"},
        {"label": "Architecture", "value": "Multimodal mixture-of-experts transformer", "status": "source_checked", "source_ids": [REP], "source_locator": f"{REP}: 'Enchant v3: Achieving scalable predictability'"},
        {"label": "Pretraining", "value": "4.5 trillion tokens", "status": "source_checked", "source_ids": [REL], "source_locator": f"{REL}: highlights"},
        {"label": "Prediction targets", "value": "More than 6,000 molecular properties", "status": "source_checked", "source_ids": [REL], "source_locator": f"{REL}: subtitle and highlights"},
        {"label": "Input modalities", "value": "16, including text, assay data, molecule, protein and 3D structure, images, multi-omics, biologics, clinical trial data and pharmacokinetics", "status": "source_checked", "source_ids": [REL], "source_locator": f"{REL}: highlights"},
        {"label": "Training data", "value": "Public, proprietary and partner data; not itemised", "status": "unreported", "source_ids": [REP, REL], "source_locator": f"{REP}: 'Expand therapeutic opportunity'; {REL}: 'Ingest diverse data'"},
        {"label": "Weights, API and licence", "value": "None located; Iambic describes internal and partner deployment", "status": "unavailable", "source_ids": [REP, PLAT], "source_locator": f"{REP}: 'Enchant drives an engine for new medicines'; {PLAT}: platform description"},
    ],
    "strengths": [
        {"text": "Iambic reports that prediction accuracy improved with scale across Enchant v1, v2 and v3, on preclinical and clinical endpoints.",
         "source_ids": [REP, REL], "source_locator": f"{REP}: Figure 5 caption and text; {REL}: 'Predictable scaling laws'"},
    ],
    "limitations": [
        {"text": "All descriptions and figures are reported by the developer. No independent evaluation of v3 was found.",
         "source_ids": SRCS, "source_locator": "All three pages"},
        {"text": "The IAM-C1 and IAM217 programmes are case studies of drug programmes that used Enchant, not evaluations of the model; the report does not separate v3's contribution.",
         "source_ids": [REP], "source_locator": f"{REP}: 'Example #1: IAM-C1 for CDK2/4' and 'Example #2: IAM217 for KIF18A'"},
        {"text": "Figure 7 compares structure prediction with ESM3 and DPLM-2 on held-out CASP14 and CAMEO22 structures, but does not say which Enchant version or which ESM3 and DPLM-2 configurations were used, which structures were held out, or how TM-scores were averaged.",
         "source_ids": [REP], "source_locator": f"{REP}: 'Enchant excels at token-based structure prediction' and Figure 7"},
    ],
    "coverage": "limited",
    "gaps": [
        "No result is recorded: Figure 7's TM-score labels lack the configuration, split and averaging details needed for a result.",
        "No weights, public API, model card or licence for v3 was located.",
        "Training data composition and endpoint-level accuracy are not reported.",
    ],
    "review": {"method": "automated_source_review", "date": "2026-11-02",
               "note": "Checked against the three pinned Iambic pages; build.py asserts each quoted figure. See docs/reviews/2026-11-02-enchant-v3.md."},
}
add({
    "id": f"{P}-model-enchant-v3", "kind": "model", "name": "Enchant v3",
    "description": "Iambic's 41-billion-parameter multimodal transformer that predicts molecular properties and preclinical and clinical endpoints for drug discovery.",
    "status": "needs_review", "facets": {**FACETS, "method_types": ["foundation_model"]}, "source_ids": SRCS, "links": [],
    "attributes": {
        "reported_name": "Enchant v3",
        "entity_level": "service",
        "version": "Enchant v3 (announced 21 September 2026)",
        "access": "Proprietary. Iambic deploys it internally and with partners; no downloadable weights, public inference API or model licence was located.",
        "missing_metadata": {
            "licence": {"reason": "unreported", "note": "No model licence located in the official sources."},
            "training_data": {"reason": "unreported", "note": "Public, proprietary and partner data; not itemised."},
        },
        "provenance_note": ("Developed by Iambic (Iambic Therapeutics). Third generation after Enchant v1 (2024, 1B parameters) "
                            "and v2 (2025, 7B); kept separate from those versions and from NeuralPLexer."),
        "profile": profile,
        "source_locator": f"{REP}: whole report; {REL}: highlights; {PLAT}: platform description",
    }})

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in sorted(records, key=lambda r: r["id"]):
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
print({k: sum(r["kind"] == k for r in records) for k in {r["kind"] for r in records}})
