"""Models, the pseudobulk method and configurations for the HyCell batch."""

from sources import (AREAS, B, COMMIT, SRC_CITATION, SRC_LICENSE, SRC_NOTICE, SRC_PYPROJECT,
                     SRC_README, SRC_REPO, SRC_REPORT, SRC_SIDECAR, SRC_WEIGHTS, record)

MODEL = f"{B}-model-hycell"
FM = {"areas": AREAS, "contexts": ["research"], "method_types": ["foundation_model"]}

# How each system produces its embedding. Evaluations copy this into comparison.adaptation,
# so systems run under different conditions are never compared automatically.
PER_CELL = ("Frozen zero-shot embedding of each cell on its own, released weights and default "
            "inference settings, no batch, donor or cell-type labels at inference")
# HyCell runs under the same condition as the other per-cell models; how its embedding uses
# the cell's counts and the measured-gene list is a property of the model, kept in its
# configuration, not a different test condition.
HYCELL_INPUT = ("The embedding uses only the cell's own counts and the list of genes its dataset "
                "measures.")
ADAPT = {
    "stack": "Frozen embedding with batch-grouped inference: Stack encodes sets of 256 cells and the "
             "cells of each batch are encoded together, so batch labels are used at inference "
             "(the mode its released tutorial recommends)",
    "scimilarity": PER_CELL + "; the model was pretrained with cell-type labels",
    "scprint": PER_CELL + "; the model was pretrained with cell-type labels",
    "pca": "No pretraining: PCA fitted to each evaluation atlas on 2,000 highly variable genes of the "
           "log-normalised counts, 50 components, so the fit sees the evaluation cells",
}
NEW_MODELS = [
    ("stack", "Stack", "Stack is a single-cell foundation model that embeds sets of cells together "
     "and learns biology in context from the other cells of a sample.", "Dong et al., 2026"),
    ("scimilarity", "SCimilarity", "SCimilarity is a single-cell embedding model trained with "
     "cell-type labels for searching an atlas for similar human cells.", "Heimberg et al., 2025"),
    ("tahoe-x1", "Tahoe-x1", "Tahoe-x1 is a family of perturbation-trained single-cell foundation "
     "models scaled up to 3 billion parameters.", "Gandhi et al., 2025"),
    ("transcriptformer", "TranscriptFormer", "TranscriptFormer is a generative single-cell "
     "transcriptome model whose cell embeddings are used as representations.",
     "Pearce et al., 2026"),
]
# printed label -> (config slug, model id, params as printed in Table 3, cells as printed)
SYSTEMS = {
    "HyCell": ("hycell", MODEL, "16", "79.5M"),
    "Stack": ("stack", f"{B}-model-stack", "218", "149M"),
    "SCimilarity": ("scimilarity", f"{B}-model-scimilarity", "31", "7.9M"),
    "scFoundation": ("scfoundation", "catalog-model-scfoundation", "100", ">50M"),
    "UCE": ("uce", "cell-type-20261009-model-uce", "675", ">36M"),
    "Tahoe-x1 (70M)": ("tahoe-x1-70m", f"{B}-model-tahoe-x1", "71", "n/s"),
    "TranscriptFormer": ("transcriptformer", f"{B}-model-transcriptformer", "429", "57M"),
    "scGPT": ("scgpt", "catalog-model-scgpt", "51", "33M"),
    "Geneformer V2": ("geneformer-v2", "catalog-model-geneformer", "104", "104M"),
    "STATE-SE": ("state-se", "discovery-model-state", "600", "167M"),
    "scPRINT": ("scprint", "lit-cells-networks-20261011-ye2026grn-model-scprint", "19", "54M"),
    "PCA": ("pca", "lit-cells-networks-20261011-scmbench-method-pca", None, None),
}


def adapt(label):
    return ADAPT.get(SYSTEMS[label][0], PER_CELL)


def models():
    out = [record(MODEL, "model", "HyCell",
                  "HyCell maps the raw counts of a human cell to a 512-dimensional embedding with a "
                  "16-million-parameter set transformer and decodes embeddings back to expected "
                  "expression.",
                  {"reported_name": "HyCell", "entity_level": "checkpoint",
                   "version": "hycell-16m, package version 0.1.0, released 2026-11-02; weights "
                              "SHA-256 11197d805aa6bafd7a69996bf8e0c7cfd7706b4fbbf5466f9e350d5b3e79d744; "
                              "technical report dated 2026-11-01",
                   "checkpoint_revision": "weights_sha256 11197d805aa6bafd7a69996bf8e0c7cfd7706b4fbbf5466f9e350d5b3e79d744, "
                                          "verified against the downloaded weights",
                   "licence": "Apache-2.0 for the code and weights, through the repository LICENSE's "
                              "default for Tencent-authored materials, as NOTICE, CITATION.cff and "
                              "pyproject.toml state; no file names the weights explicitly. The "
                              "training data (CZ CELLxGENE Census, release of 8 November 2025) and the "
                              "gene vocabulary drawn from it are CC BY 4.0 and keep their own terms.",
                   "access": "Public: the hycell package installs from the repository subdirectory and "
                             "ships the 64 MB weights inside it, so it runs offline; 'hycell info "
                             "--verify' checks their SHA-256. Python 3.10+, torch 2.4+; a CUDA GPU is "
                             "recommended and flash-attn is optional.",
                   "training_data": "Human primary cells with raw counts from the CZ CELLxGENE Census "
                                    "release of 8 November 2025: 95.0 million cells from 555 datasets, "
                                    "reduced to 79.5 million training cells from 532 datasets by "
                                    "removing every dataset and collection that contributes to an "
                                    "evaluation atlas or to a separate development set of eight "
                                    "tissues. No cell-type labels.",
                   "source_locator": "Technical report Sections 2 and 2.5, Table 1; README 'Install', "
                                     "'License'; weights.json; NOTICE",
                   "provenance_note": "Released by Tencent Hunyuan in the Hyra Results repository and "
                                      "trained by its Hyra research agent. Kept at checkpoint level "
                                      "because the released weights were hashed and match the "
                                      "published weights_sha256."},
                  sources=[SRC_REPORT, SRC_README, SRC_LICENSE, SRC_NOTICE, SRC_CITATION,
                           SRC_PYPROJECT, SRC_SIDECAR, SRC_WEIGHTS, SRC_REPO], facets=FM)]
    for slug, name, description, cite in NEW_MODELS:
        out.append(record(
            f"{B}-model-{slug}", "model", name, description,
            {"reported_name": name, "entity_level": "family",
             "access": "Released weights, run by the HyCell report authors at default settings.",
             "source_locator": "Technical report Section 3.1 'Models' and references",
             "provenance_note": f"{cite}, as cited by the HyCell report. Created here because the "
                                "store held no record of this published model; the store's Stack "
                                "entries are challenge submissions, not the model.",
             "missing_metadata": {"version": {"reason": "unreported",
                                              "note": "No checkpoint revision is printed."}}},
            facets=FM))
    out.append(record(
        f"{B}-method-pseudobulk-counts", "method", "Pseudobulk count fold change",
        "Sums the raw counts of the cells in each state and compares the totals gene by gene to "
        "give a counted fold change between two states.",
        {"reported_name": "pseudobulk counts", "entity_level": "method",
         "reference_kind": "count-based comparator",
         "source_locator": "Section 4.3; Figure 5",
         "provenance_note": "The comparator the HyCell report sets against its decoder when reading "
                            "gene programs; not a model."},
        facets={"areas": AREAS, "contexts": ["research"], "method_types": ["conventional_pipeline"]}))
    return out


def configurations():
    out = []
    for label, (slug, target, params, cells) in SYSTEMS.items():
        size = (f"Table 3: {params} million parameters, {cells} pretraining cells as reported by "
                "its authors. " if params else "")
        out.append(record(
            f"{B}-config-{slug}", "configuration", f"{label} (HyCell report)",
            f"Produces a frozen cell embedding with {label} as the HyCell report runs it.",
            {"reported_name": label,
             "version": "Released weights at default inference settings; no revision printed"
                        if slug != "hycell" else "hycell-16m, package 0.1.0",
             "parameters": size + adapt(label) + "." + (" " + HYCELL_INPUT if slug == "hycell"
                                                        else ""),
             "condition": adapt(label),
             "foundation_model_eligible": slug != "pca",
             "access_reuse": "Public release run by the HyCell report authors" if slug != "hycell"
                             else f"Public Apache-2.0 package at commit {COMMIT[:8]}",
             "source_locator": "Section 3.1 'Models'; Table 3"},
            links=[{"relation": "configuration_of", "target_id": target}],
            facets=FM if slug != "pca" else {"areas": AREAS, "contexts": ["research"],
                                             "method_types": ["conventional_pipeline"]}))
    out.append(record(
        f"{B}-config-hycell-finetuned", "configuration", "HyCell fine-tuned annotator (HyCell report)",
        "Fine-tunes the HyCell encoder with a linear head on a labelled reference to predict cell "
        "types.",
        {"reported_name": "Fine-tuned", "version": "hycell-16m, package 0.1.0",
         "parameters": "Encoder and linear head trained together with cross-entropy from the "
                       "pretrained weights; 64 labelled cells per step with the pretraining "
                       "augmentations; learning rate 1e-5 for the network and 1e-3 for the head; at "
                       "most 2,000 steps with early stopping on 10% of the reference cells.",
         "condition": "Fine-tuned on the labelled cells of the other batches, so it uses cell-type "
                      "labels, unlike the frozen embeddings",
         "foundation_model_eligible": True, "fine_tuning": {"labels": "cell type",
                                                            "max_steps": 2000},
         "access_reuse": f"Public Apache-2.0 package at commit {COMMIT[:8]}",
         "source_locator": "Section 5; Table 5"},
        links=[{"relation": "configuration_of", "target_id": MODEL}], facets=FM))
    out.append(record(
        f"{B}-config-pseudobulk-counts", "configuration", "Pseudobulk counts (HyCell report)",
        "Computes counted fold changes between two cell states from pseudobulk raw counts.",
        {"reported_name": "pseudobulk counts", "version": "As described in Section 4.3",
         "parameters": "Counts summed per state; programs compared donor against the other donors.",
         "foundation_model_eligible": False, "source_locator": "Section 4.3; Figure 5c"},
        links=[{"relation": "configuration_of", "target_id": f"{B}-method-pseudobulk-counts"}],
        facets={"areas": AREAS, "contexts": ["research"], "method_types": ["conventional_pipeline"]}))
    return out
