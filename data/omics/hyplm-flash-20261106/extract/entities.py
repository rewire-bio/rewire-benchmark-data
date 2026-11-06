"""Entity records for the HyPLM-Flash batch: sources, models, configurations,
benchmark, datasets and protocols. Store records are reused where the report
describes the same thing at the same version; see notes.md for each choice.
"""

B = "hyplm-flash-20261106"
COMMIT = "0dcc533cc9f8f76c90ecbfe944df816b6672328a"
RAW = f"https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/{COMMIT}"
BLOB = f"https://github.com/Tencent-Hunyuan/Hyra-results/blob/{COMMIT}"
RETRIEVED = "2026-11-06T11:08:21Z"
PDF_SHA = "d81d88a415a91c2b00d8e97513a90c03ccffd857ec75033fa7de77227dea1710"

SRC_REPO = "hyra-results-20261106-source-repository-readme"  # reused, added by the HyInv batch
SRC_REPORT = f"{B}-source-report"
SRC_README = f"{B}-source-model-readme"
SRC_LICENCE = f"{B}-source-licence"

MODEL = f"{B}-model-hyplm-flash"
BENCHMARK = f"{B}-benchmark-report-evaluation"
AREAS = ["protein-function", "proteins-complexes"]

CONFIG_BF16 = f"{B}-config-hyplm-flash-bf16-evaluation"
CONFIG_INT8 = f"{B}-config-hyplm-flash-int8-engine"

PROTEINGYM_DATA = "vep-lit-20261014-data-proteingym-dms-substitutions-144fe22"


def record(rid, kind, name, description, attributes, links=None, sources=None,
           facets=None, status="needs_review"):
    return {
        "id": rid, "kind": kind, "name": name, "description": description, "status": status,
        "facets": facets if facets is not None else {"areas": AREAS, "contexts": ["research"]},
        "source_ids": sources if sources is not None else [SRC_REPORT],
        "links": links or [], "attributes": attributes,
    }


def concern(message, locator, applies_to):
    return {"source_id": SRC_REPORT, "message": message, "source_locator": locator,
            "artifact_sha256": PDF_SHA, "reviewed_at": RETRIEVED,
            "review_method": "ai-assisted-source-review", "applies_to": applies_to}


def sources():
    report_limits = [
        "Author-released report, not peer reviewed. All three authors are at Tencent Hunyuan, "
        "which released the model, and every baseline was run by the same team through its own "
        "adapters; no result here is independent of the developer.",
        "All accuracy results were computed with BF16 arithmetic. The released default is the INT8 "
        "engine, for which the report prints no per-task value; it states only that INT8 keeps "
        "zero-shot fitness, structure, function annotation and likelihood within 0.01 of the BF16 "
        "results.",
        "Section 4 states that confidence intervals are paired bootstrap intervals, but the report "
        "prints intervals only for four ProteinGym paired differences. Every table cell is printed "
        "without its interval.",
        "Tables 6 and 7 print every task for 13 of the 29 models only. The other 16 checkpoints "
        "appear at most in Figure 3a, Table 3, Table 5 or the prose, and 8 of the 28 public "
        "checkpoints are never named with a value, so the report's list of 28 cannot be "
        "reconstructed from it.",
        "Table 5's rows without a dagger are published ProteinGym leaderboard values at commit "
        "144fe22, quoted rather than run by the authors; they are not recorded from this source.",
        "Throughput was measured on one NVIDIA H20 with the INT8 engine for HyPLM-Flash and with "
        "reference implementations for the baselines, each with the fastest attention kernel its "
        "implementation supports. Only HyPLM-Flash's own figure and the baselines' range are "
        "printed.",
    ]
    return [
        record(
            SRC_REPORT, "source", "HyPLM Technical Report (Hyra Team, 2026-10-12)",
            "Technical report for HyPLM-Flash, with its architecture, training, INT8 inference "
            "engine and a 32-task evaluation against 28 public protein language model checkpoints.",
            {
                "url": f"{BLOB}/AI4Science/hyplm_flash/HyPLM_Technical_Report.pdf",
                "artifact_url": f"{RAW}/AI4Science/hyplm_flash/HyPLM_Technical_Report.pdf",
                "version": f"Dated 2026-10-12 on page 1; retrieved at commit {COMMIT} (13 pages)",
                "version_note": "The report is dated 2026-10-12 on page 1. The PDF's own CreationDate "
                                "and ModDate are both 2026-10-29T23:28:47+08 (pdfTeX-1.40.19), so "
                                "these bytes were built 17 days after the printed date. The printed "
                                "date is what version records. No earlier PDF exists at the pinned "
                                "commit, so whether the rebuild changed any content was not checked.",
                "retrieved_at": RETRIEVED,
                "artifact_sha256": PDF_SHA,
                "publication_status": "official_project_source",
                "licence": "Apache-2.0 (repository LICENSE)",
                "media_type": "application/pdf",
                "source_type": "vendor technical report",
                "extraction_method": "pdftotext -layout text layer, parsed by extract/parse.py with "
                                     "every row label, metric label and cell count asserted.",
                "archive_note": "The PDF is not committed: it is refetchable at the pinned commit and "
                                "extract/parse.py refuses any other bytes. Its gzipped text layer is "
                                "artifacts/HyPLM_Technical_Report.txt.gz.",
                "archive_sha256": "e051bbea5e0c0ddb2f61f11cfb0fb9247c51b031cbd5568db70e25e720b3067f",
                "archive_transformation_receipt": "gzip -n9 of the pdftotext -layout output of "
                                                  "the pinned PDF (poppler pdftotext, macOS).",
                "limitations": report_limits,
                "evidence_concerns": [
                    concern(
                        "The recent-PDB likelihood panel is described two ways. Section 4.3 and the "
                        "Table 3 caption give 887 PDB chains released after 2 September 2026; Table 4 "
                        "gives 887 RCSB PDB entries released 9 September to 7 October 2026. The start "
                        "of the window and whether the unit is a chain or an entry both differ, so the "
                        "panel cannot be rebuilt from the report.",
                        "Section 4.3; Table 3 caption; Table 4 row 'PDB time split'",
                        [f"{B}-data-nll-recent-pdb"]),
                    concern(
                        "Appendix A states that the authors could not reproduce xTrimoPGLM's published "
                        "ProteinGym scores (their runs fall 0.07 to 0.09 below the leaderboard) and "
                        "that its likelihood is implausibly high, pointing to an incompatibility "
                        "between their adapter and its masked-language-model head. They withhold its "
                        "zero-shot and likelihood results and keep its embedding-based results as "
                        "unaffected, but those results come from the same adapter and that claim was "
                        "not tested.",
                        "Appendix A 'Deviations'",
                        [f"{B}-config-xtrimopglm-1b"]),
                    concern(
                        "Appendix A states that for GB1 two-vs-rest, GB1 three-vs-rest and the "
                        "cross-protein hydrolase split of FLIP2, validation data come from the "
                        "training distribution while the test sets are strongly shifted, so probe "
                        "selection is dominated by noise and numerically equivalent runs of the same "
                        "model differ by up to 0.2. The authors print these cells but leave them out "
                        "of every summary statistic.",
                        "Appendix A 'Statistics'",
                        [f"{B}-protocol-gb1-two-vs-rest", f"{B}-protocol-gb1-three-vs-rest",
                         f"{B}-protocol-hydrolase-to-p06241"]),
                ],
            },
            sources=[],
        ),
        record(
            SRC_README, "source", "HyPLM-Flash package README (Tencent Hunyuan, commit 0dcc533c)",
            "README of the released hyplm package, with installation, the encoding and logits "
            "interface, the two precision modes and their recommended uses.",
            {
                "url": f"{BLOB}/AI4Science/hyplm_flash/README.md",
                "artifact_url": f"{RAW}/AI4Science/hyplm_flash/README.md",
                "version": f"GitHub repository Tencent-Hunyuan/Hyra-results at commit {COMMIT}",
                "retrieved_at": RETRIEVED,
                "artifact_sha256": "db6ab273ef190a40199a5a8d17c474a2809fd9cedac6013c45ec7c06642542a3",
                "publication_status": "official_project_source",
                "licence": "MIT (AI4Science/hyplm_flash/LICENSE)",
                "media_type": "text/markdown",
                "source_type": "repository README",
                "archive_note": "Archived in the batch as artifacts/hyplm-flash-README.md.",
                "archive_sha256": "db6ab273ef190a40199a5a8d17c474a2809fd9cedac6013c45ec7c06642542a3",
                "limitations": [
                    "The weights are not in the repository: README states the 2.6 GB of FP32 weights "
                    "are two shards in the repository's GitHub Releases, fetched and verified by "
                    "weights/download.sh. Neither the release tag nor the shard hashes were "
                    "retrieved for this batch.",
                    "The precision table gives rounded throughputs (about 130,000 and about 90,000 "
                    "residues per second); the report's measured figure is 131,000.",
                ],
            },
            links=[{"relation": "companion_of", "target_id": SRC_REPORT}],
            sources=[],
        ),
        record(
            SRC_LICENCE, "source", "HyPLM-Flash LICENSE (MIT, commit 0dcc533c)",
            "MIT licence file of the released hyplm package, with a note that third-party weights, "
            "datasets and compatibility implementations keep their own licences.",
            {
                "url": f"{BLOB}/AI4Science/hyplm_flash/LICENSE",
                "artifact_url": f"{RAW}/AI4Science/hyplm_flash/LICENSE",
                "version": f"GitHub repository Tencent-Hunyuan/Hyra-results at commit {COMMIT}",
                "retrieved_at": RETRIEVED,
                "artifact_sha256": "a0a9dc95e81d7a1374275195bccb72442e0126be826919b13ff67f52eb64a031",
                "publication_status": "official_project_source",
                "licence": "MIT",
                "code_licence": "MIT",
                "media_type": "text/plain",
                "source_type": "licence file",
                "archive_note": "Archived in the batch as artifacts/hyplm-flash-LICENSE.",
                "archive_sha256": "a0a9dc95e81d7a1374275195bccb72442e0126be826919b13ff67f52eb64a031",
                "scope_note": "Copyright line 'Copyright (c) 2026 HyPLM contributors'. Adds after the "
                              "MIT text: 'Third-party model weights, datasets, and compatibility "
                              "implementations retain their own licenses and attribution; see their "
                              "individual provenance records.' Those provenance records are not in "
                              "the pinned folder.",
            },
            links=[{"relation": "companion_of", "target_id": SRC_REPORT}],
            sources=[],
        ),
    ]


NEW_MODELS = [
    ("e1", "E1", "E1 is a retrieval-augmented protein language model trained with homologous "
     "sequences in its context, which can also be run on a query sequence alone.",
     "E1-150M, E1-300M, E1-600M", "Jain et al., 2025, as cited by the HyPLM report. The report runs "
     "it in single-sequence mode, without retrieved context sequences."),
    ("amplify", "AMPLIFY", "AMPLIFY is a masked protein language model encoder trained on UniRef100, "
     "antibody and SCOP sequences.", "AMPLIFY-350M", "Fournier et al., 2024, as cited by the HyPLM "
     "report."),
    ("dplm", "DPLM", "DPLM is a discrete diffusion protein language model that continues training "
     "from ESM-2 and is used both to generate sequences and as an encoder.",
     "DPLM-650M, DPLM-3B", "Wang et al., 2024, as cited by the HyPLM report. Not DPLM-2, which the "
     "store holds separately as hyinv-20261106-model-dplm-2."),
    ("ankh", "Ankh", "Ankh is a family of encoder-decoder protein language models whose encoder "
     "gives per-residue representations.", "Ankh-base, Ankh3-large",
     "Named by the HyPLM report; it runs them through Hugging Face Transformers and caches their "
     "features in FP32 because their activations exceed the FP16 range."),
]


def models():
    out = [record(
        MODEL, "model", "HyPLM-Flash",
        "HyPLM-Flash is a 650-million-parameter masked protein language model that returns "
        "per-residue or pooled 1280-dimensional embeddings and masked-language-model logits.",
        {
            "reported_name": "HyPLM-Flash",
            "entity_level": "checkpoint",
            "version": "First release of the HyPLM family, published 2026-11-02 with FP32 weights "
                       "(2.61 GB safetensors) as two GitHub Release shards; technical report dated "
                       "2026-10-12",
            "licence": "MIT (AI4Science/hyplm_flash/LICENSE); third-party weights, datasets and "
                       "compatibility implementations keep their own licences",
            "access": "Public: the hyplm package and weights/download.sh in AI4Science/hyplm_flash/ "
                      "of Tencent-Hunyuan/Hyra-results; the script fetches, merges and verifies the "
                      "two weight shards from the repository's GitHub Releases. Needs a CUDA GPU "
                      "(Hopper such as H20 or H100 recommended), Python 3.10+, torch, safetensors, "
                      "triton and flash-attn.",
            "training_data": "726 billion tokens from 2.6 billion sequences (659 billion residues): "
                             "UniRef90 plus the UniRef50 representatives it lacks, MGnify90, active "
                             "UniParc entries and JGI IMG isolate proteomes, sequences of 30 to "
                             "8,192 residues, exact duplicates removed and benchmark sequences used "
                             "during development removed by exact match, including all ProteinGym "
                             "wild types and variants. A second stage adds auxiliary structure "
                             "objectives on 1.6 million experimental or predicted chains.",
            "source_locator": "Technical report Sections 2.1 and 2.2, Table 1; "
                              "AI4Science/hyplm_flash/README.md 'Installation', 'Usage', 'Layout'",
            "provenance_note": "Released by Tencent Hunyuan in the Hyra Results repository and "
                               "trained by the team's Hyra 2.0 research agent; authors Haowei Lin, "
                               "Cai Zhou and Xiangxin Zhou. Kept at checkpoint level because one set "
                               "of weights is released and evaluated; the report says later versions "
                               "will follow.",
            "missing_metadata": {"checkpoint_revision": {
                "reason": "unextracted",
                "note": "The weights are a GitHub Release whose tag and shard hashes were not "
                        "retrieved; download.sh verifies them but was not run for this batch."}},
        },
        sources=[SRC_REPORT, SRC_README, SRC_LICENCE, SRC_REPO],
        facets={"areas": AREAS, "contexts": ["research"], "method_types": ["foundation_model"]},
    )]
    for slug, name, description, reported, note in NEW_MODELS:
        out.append(record(
            f"{B}-model-{slug}", "model", name, description,
            {
                "reported_name": reported, "entity_level": "family",
                "access": "Public checkpoints, used by the HyPLM report through thin adapters around "
                          "their reference implementations.",
                "source_locator": "Technical report Section 4, Appendix A 'Models', Table 1 and "
                                  "references",
                "provenance_note": note + " Created here because the store held no record of this "
                                          "family.",
                "missing_metadata": {
                    "version": {"reason": "unreported", "note": "No checkpoint revision is printed."},
                    "licence": {"reason": "unextracted", "note": "Not stated in these sources."},
                },
            },
            facets={"areas": AREAS, "contexts": ["research"], "method_types": ["foundation_model"]},
        ))
    return out


# label printed in the report -> (config slug, model id, checkpoint wording)
BASELINES = {
    "ESM-2 150M": ("esm-2-150m", "catalog-model-esm-2", "ESM-2 150M"),
    "ESM-2 650M": ("esm-2-650m", "catalog-model-esm-2", "ESM-2 650M"),
    "ESM-2 3B": ("esm-2-3b", "catalog-model-esm-2", "ESM-2 3B"),
    "ESM-2 15B": ("esm-2-15b", "catalog-model-esm-2", "ESM-2 15B"),
    "ESM-1b": ("esm-1b", "uc20260930-model-esm-1b", "ESM-1b"),
    "ESM C 300M": ("esm-c-300m", "discovery-model-esmc", "ESM C 300M"),
    "ESM C 600M": ("esm-c-600m", "discovery-model-esmc", "ESM C 600M"),
    "ESM C 6B": ("esm-c-6b", "discovery-model-esmc", "ESM C 6B"),
    "E1-150M": ("e1-150m", f"{B}-model-e1", "E1-150M"),
    "E1-300M": ("e1-300m", f"{B}-model-e1", "E1-300M"),
    "E1-600M": ("e1-600m", f"{B}-model-e1", "E1-600M"),
    "AMPLIFY-350M": ("amplify-350m", f"{B}-model-amplify", "AMPLIFY-350M"),
    "DPLM-650M": ("dplm-650m", f"{B}-model-dplm", "DPLM-650M"),
    "DPLM-3B": ("dplm-3b", f"{B}-model-dplm", "DPLM-3B"),
    "ESM3-open": ("esm3-open", "discovery-model-esm3", "ESM3-open (1.4B)"),
    "ProtBERT": ("protbert", "lit-protein-20261011-deepprotein-model-protbert", "ProtBERT"),
    "ProtT5-XL": ("prott5-xl", "lit-protein-20261011-deepprotein-model-prot-t5-xl", "ProtT5-XL"),
    "Ankh-base": ("ankh-base", f"{B}-model-ankh", "Ankh-base"),
    "Ankh3-large": ("ankh3-large", f"{B}-model-ankh", "Ankh3-large"),
    "xTrimoPGLM-1B": ("xtrimopglm-1b", "uc20260930-model-xtrimopglm", "xTrimoPGLM-1B"),
}
ADAPTER = {
    "esm-1b": "Hugging Face Transformers", "esm-2": "Hugging Face Transformers",
    "dplm": "Hugging Face Transformers", "protbert": "Hugging Face Transformers",
    "prott5": "Hugging Face Transformers", "ankh": "Hugging Face Transformers",
    "esm-c": "the esm package", "esm3": "the esm package",
    "e1": "the authors' code, single-sequence mode without retrieved context sequences",
    "amplify": "the authors' code", "xtrimopglm": "the authors' code",
}


def adapter_for(slug):
    for prefix, text in ADAPTER.items():
        if slug.startswith(prefix):
            return text
    raise KeyError(slug)


def configurations():
    common = {"foundation_model_eligible": True,
              "access_reuse": "Public checkpoint run by the HyPLM report authors"}
    facets = {"areas": AREAS, "contexts": ["research"], "method_types": ["foundation_model"]}
    out = [
        record(CONFIG_BF16, "configuration", "HyPLM-Flash, BF16 evaluation (HyPLM report)",
               "Runs the released HyPLM-Flash weights in BF16 arithmetic to produce embeddings, "
               "probe features and masked-language-model scores.",
               {"reported_name": "HyPLM-Flash", "version": "Released weights; report dated 2026-10-12",
                "parameters": "BF16 arithmetic, the setting every accuracy result in the report uses. "
                              "Zero-shot scores from the masked-language-model head; supervised tasks "
                              "use a linear probe on frozen representations from the best of six "
                              "relative depths on validation data. The report does not say whether "
                              "these runs used the engine's bf16 mode or another BF16 path.",
                "foundation_model_eligible": True,
                "access_reuse": f"Public MIT weights and code at commit {COMMIT[:8]}",
                "source_locator": "Section 3 'Accuracy in this report is evaluated with BF16 "
                                  "arithmetic'; Section 4; Appendix A"},
               links=[{"relation": "configuration_of", "target_id": MODEL}],
               sources=[SRC_REPORT, SRC_README], facets=facets),
        record(CONFIG_INT8, "configuration", "HyPLM-Flash, INT8 inference engine (HyPLM report)",
               "Runs HyPLM-Flash through its INT8 inference engine, which packs proteins without "
               "padding and performs the block projections as INT8 matrix multiplications.",
               {"reported_name": "HyPLM-Flash (INT8 engine)",
                "version": "Released engine, precision=\"int8\" (the package default)",
                "parameters": "Padding-free packing with variable-length FlashAttention-3; three fused "
                              "Triton kernels; the four projections of every block as INT8 matrix "
                              "multiplications with activations scaled per token and per group of 128 "
                              "channels and weights per output channel, accumulating in INT32 per "
                              "128-wide slice and promoted to FP32; residual stream in FP32.",
                "foundation_model_eligible": True,
                "access_reuse": f"Public MIT weights and code at commit {COMMIT[:8]}",
                "condition": "INT8 is applied per packed batch and only when the batch holds at "
                             "least quant_min_tokens tokens (default 1,024; model.py lines 41 and "
                             "102). Smaller batches run BF16 although precision is int8, including "
                             "a job's final batch when it falls under the threshold and every "
                             "CUDA-graph bucket (64 to 512 tokens, graphs.py line 12), so the "
                             "low-latency single-protein path always runs BF16. A configuration "
                             "labelled INT8 does not run INT8 throughout.",
                "limitations": [
                    "No accuracy value is printed for this configuration: every accuracy result "
                    "in the report is a BF16 run. Section 3 says INT8 keeps zero-shot fitness, "
                    "structure, function annotation and likelihood within 0.01 of BF16, a list "
                    "that omits regression, and the release recommends BF16 for regressors on "
                    "near-identical variants. HyPLM-Flash's largest supervised margin over "
                    "ESM-2 650M, AAV two-vs-many (0.650 against 0.518), is a regression task "
                    "measured in BF16, so the INT8 cost on the task family with the headline "
                    "margin is not measured anywhere in the release."],
                "missing_metadata": {"result_status": {
                    "reason": "unreported",
                    "note": "No accuracy result, on any task, is printed for the INT8 engine."}},
                "source_locator": "Section 3; Appendix A 'Throughput'; README 'Precision'; "
                                  "hyplm/engine/model.py lines 7, 41 and 102; "
                                  "hyplm/engine/graphs.py line 12"},
               links=[{"relation": "configuration_of", "target_id": MODEL}],
               sources=[SRC_REPORT, SRC_README, f"{B}-source-engine-model",
                        f"{B}-source-engine-packing", f"{B}-source-engine-graphs"], facets=facets),
    ]
    notes = {
        "esm3-open": " Scored from sequence alone, whereas its published ProteinGym results also use "
                     "structure inputs.",
        "xtrimopglm-1b": " Zero-shot and likelihood results are withheld by the authors because of an "
                         "adapter incompatibility with its masked-language-model head.",
    }
    for label, (slug, model_id, checkpoint) in BASELINES.items():
        out.append(record(
            f"{B}-config-{slug}", "configuration", f"{label} (HyPLM report)",
            f"Runs the public {checkpoint} checkpoint in BF16 through {adapter_for(slug)} to produce "
            "embeddings, probe features and masked-language-model scores.",
            {"reported_name": label, "version": f"Public {checkpoint} checkpoint; no revision printed",
             "parameters": f"BF16 through {adapter_for(slug)}. Inputs longer than the model's window "
                           "are processed in windows with 50% overlap whose residue representations "
                           "are averaged. Zero-shot scores from the masked-language-model head; "
                           "supervised tasks use a linear probe on frozen representations from the "
                           "best of six relative depths on validation data." + notes.get(slug, ""),
             "source_locator": "Appendix A 'Models' and 'Deviations'; Section 4", **common,
             "missing_metadata": {"checkpoint_revision": {
                 "reason": "unreported", "note": "No checkpoint revision or hash is printed."}}},
            links=[{"relation": "configuration_of", "target_id": model_id}], facets=facets))
    return out
