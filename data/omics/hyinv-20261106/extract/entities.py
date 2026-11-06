"""Entity records for the HyInv batch: sources, models, configurations,
benchmark, datasets, protocols. Values and locators come from the pinned
sources only; nothing here is inferred.
"""

B = "hyinv-20261106"
SHARED = "hyra-results-20261106"
COMMIT = "0dcc533cc9f8f76c90ecbfe944df816b6672328a"
RAW = f"https://raw.githubusercontent.com/Tencent-Hunyuan/Hyra-results/{COMMIT}"
BLOB = f"https://github.com/Tencent-Hunyuan/Hyra-results/blob/{COMMIT}"
RETRIEVED = "2026-11-06T09:52:00Z"

SRC_REPO = f"{SHARED}-source-repository-readme"
SRC_REPORT = f"{B}-source-report"
SRC_README = f"{B}-source-model-readme"
SRC_LICENCE = f"{B}-source-licence"
ALL_SOURCES = [SRC_REPORT, SRC_README, SRC_LICENCE, SRC_REPO]

BENCHMARK = f"{B}-benchmark-report-comparison"
NATIVE = f"{B}-method-native-sequence-refold"
MODEL = f"{B}-model-hyinv"

PROTEINMPNN_MODEL = "catalog-model-proteinmpnn"
PIFOLD_MODEL = "lit-interactions-20261011-ppiemb-model-pifold"

AREAS = ["proteins-complexes", "protein-structure"]


def record(rid, kind, name, description, attributes, links=None, sources=None,
           facets=None, status="needs_review"):
    return {
        "id": rid,
        "kind": kind,
        "name": name,
        "description": description,
        "status": status,
        "facets": facets if facets is not None else {"areas": AREAS, "contexts": ["research"]},
        "source_ids": sources if sources is not None else [SRC_REPORT],
        "links": links or [],
        "attributes": attributes,
    }


def sources():
    repo_note = (
        "Shared with the other Hyra model batches: the same README lists HyInv, "
        "HyPLM-Flash, HyCell and HyFF. Its ID is deliberately not HyInv-specific."
    )
    return [
        record(
            SRC_REPO,
            "source",
            "Hyra Results repository README (Tencent Hunyuan, commit 0dcc533c)",
            "Top-level README of the Hyra Results repository, which announces the released "
            "Hyra models and lists the agent's results against prior published values.",
            {
                "url": f"{BLOB}/README.md",
                "artifact_url": f"{RAW}/README.md",
                "version": f"GitHub repository Tencent-Hunyuan/Hyra-results at commit {COMMIT}",
                "retrieved_at": RETRIEVED,
                "artifact_sha256": "da0c496f17cad0505bdd26779ffd05f1d335eb6a7dc1065fb576e22c8a5a2bdb",
                "publication_status": "official_project_source",
                "licence": "Apache-2.0 (repository LICENSE)",
                "media_type": "text/markdown",
                "source_type": "repository README",
                "scope_note": repo_note,
                "limitations": [
                    "A launch post is linked (hy.tencent.com/research/hyra) but was not retrieved, "
                    "so nothing in this batch rests on it.",
                    "The README's own results table compares Hyra against prior published values on "
                    "mathematics, engineering and AI tasks outside this repository's scope; only its "
                    "model-release section is used here.",
                ],
                "archive_note": "Archived in the batch as artifacts/hyra-results-README.md.",
                "archive_sha256": "da0c496f17cad0505bdd26779ffd05f1d335eb6a7dc1065fb576e22c8a5a2bdb",
            },
            links=[{"relation": "companion_of", "target_id": SRC_REPORT}],
            sources=[],
        ),
        record(
            SRC_REPORT,
            "source",
            "HyInv Technical Report (Hyra Team, 2026-10-14)",
            "Technical report for HyInv, with the five-panel inverse-folding comparison against "
            "ten published baselines, the sampler and numerics ablations, the inference-time "
            "measurements and the four application protocols.",
            {
                "url": f"{BLOB}/AI4Science/hyinv/HyInv_Technical_Report.pdf",
                "artifact_url": f"{RAW}/AI4Science/hyinv/HyInv_Technical_Report.pdf",
                "version": f"Dated 2026-10-14; retrieved at commit {COMMIT} (21 pages)",
                "retrieved_at": RETRIEVED,
                "artifact_sha256": "0f10b390be399c341d1f7497c5a3ca0ac857ce78172c4732bdc86a9c66e46419",
                "publication_status": "official_project_source",
                "licence": "Apache-2.0 (repository LICENSE)",
                "media_type": "application/pdf",
                "source_type": "vendor technical report",
                "extraction_method": "pdftotext -layout text layer, parsed by extract/parse.py with "
                                     "every row label and column count asserted.",
                "archive_note": "The PDF itself is not committed; its gzipped text layer is in "
                                "artifacts/HyInv_Technical_Report.txt.gz and the PDF can be refetched "
                                "at the pinned commit and checked against artifact_sha256.",
                "archive_sha256": "49f48831fd845c24ca557d06f31aec6d0c363ba709f9a8f6aa62f06f0aa00f27",
                "archive_transformation_receipt": "gzip -n9 of the pdftotext -layout output of the "
                                                  "pinned PDF (poppler pdftotext, macOS).",
                "limitations": [
                    "Author-released report, not peer reviewed and not independently refereed. All "
                    "three authors are at Tencent Hunyuan, which released the model, and the baselines "
                    "were run by the same team.",
                    "Every quantity is computed on predicted structures and designed sequences. "
                    "Appendix B states that none is an experimental measurement, so no binding, "
                    "stability or activity is measured anywhere in the report.",
                    "Appendix C states: 'We do not claim zero sequence overlap between the training "
                    "data and the evaluation panels.' The RL pool was filtered against the panels with "
                    "a same-source homology mask and the supervised corpus by exact-sequence removal "
                    "and a homology filter, which is weaker than no overlap.",
                    "The ten baselines are each at one published single-temperature setting and were "
                    "not tuned to the panels, so the scTM comparisons are at comparable rather than "
                    "equal sequence diversity. Appendix D.2 states that PiFold, CMLM, LM-Design and "
                    "DPLM-2 3B are single points at much lower diversity than HyInv.",
                    "ESMFold2 is both the primary scoring predictor and the reinforcement-learning "
                    "reward, so the five ESMFold2 panels favour the trained model by construction; "
                    "only RecentPDB is also folded by Boltz2 and Protenix2.",
                    "Some baseline ESMFold2 cells were regenerated for the report rather than taken "
                    "from the released scores (Table 5), and the ProteinMPNN temperatures other than "
                    "the published one were generated for the report.",
                    "Appendix A records run-to-run noise of about +/-0.0015 scTM per panel and says "
                    "differences between checkpoints below about 0.003 are not resolvable; intervals "
                    "are not adjusted for multiple comparisons.",
                    "Latencies were measured on one NVIDIA H20 and exclude model loading, CUDA graph "
                    "capture and kernel compilation. Baselines ran as released, unbatched where the "
                    "released adapter handles one structure per call, so Appendix F states the "
                    "speed-ups are against those implementations and not against the best achievable "
                    "speed of the baseline models.",
                    "Figures 1, 5, 6, 7, 8, 9b, 11c, 13, 16 and 17 carry results that are not printed "
                    "as labelled cells, or whose bar order cannot be recovered from the text layer; "
                    "they are recorded as gaps in notes.md, not read by eye.",
                ],
                "evidence_concerns": [
                    {
                        "source_id": SRC_REPORT,
                        "message": "Appendix C states 'We do not claim zero sequence overlap between "
                                   "the training data and the evaluation panels', and Appendix G's "
                                   "homology screen is a coverage rule under which partial hits remain "
                                   "(Table 10: 28 of 74 de novo backbones and 7 of 12 pocket backbones "
                                   "have partial hits, and all 4 named enzymes are homologous to "
                                   "training data by design). Results on these panels are therefore "
                                   "not clean held-out measurements and must not be compared with "
                                   "results from sources that do establish no overlap.",
                        "source_locator": "Appendix C 'Data and pool', final bullet; Appendix G "
                                          "'Homology of the panels' and Table 10",
                        "artifact_sha256": "0f10b390be399c341d1f7497c5a3ca0ac857ce78172c4732bdc86a9c66e46419",
                        "reviewed_at": RETRIEVED,
                        "review_method": "ai-assisted-source-review",
                    },
                    {
                        "source_id": SRC_REPORT,
                        "message": "The ten baselines are single published settings at one temperature "
                                   "each, so their design-set diversity differs from HyInv's: on "
                                   "CATH4.3 test HyInv samples at diversity 0.331 against 0.093 for "
                                   "PiFold, 0.104 for CMLM, 0.144 for LM-Design 650M and 0.000 for "
                                   "DPLM-2 3B, which decodes by argmax. Appendix D.2 states that these "
                                   "four differences are not at matched diversity. The scTM and scTM "
                                   "difference results listed here must not be read as a "
                                   "matched-diversity ranking; only the scTM at fixed diversity "
                                   "results (Tables 8 and 9 and Appendix D.3) are read at a stated "
                                   "diversity level.",
                        "source_locator": "Appendix D.1 and D.2; Table 7; Figure 14 diversity block; "
                                          "Section 5.1 'Baselines' and 'HyInv'",
                        "artifact_sha256": "0f10b390be399c341d1f7497c5a3ca0ac857ce78172c4732bdc86a9c66e46419",
                        "reviewed_at": RETRIEVED,
                        "review_method": "ai-assisted-source-review",
                    },
                    {
                        "source_id": SRC_REPORT,
                        "message": "The inference-time results were measured with the supervised-stage "
                                   "weights and a rewrite temperature of 0.23, not with the released "
                                   "checkpoint and its default temperatures, and the quality read-outs "
                                   "of the two numerical paths used the RL checkpoint at update 288, "
                                   "not update 640. Speed and quality in this report are therefore "
                                   "measured on different weights, and the 57x figure compares HyInv's "
                                   "optimised BF16 path with ProteinMPNN's released implementation "
                                   "rather than with an equally optimised baseline.",
                        "source_locator": "Table 1 footnote; Appendix F 'Timing protocol' and "
                                          "'Baseline timings'",
                        "artifact_sha256": "0f10b390be399c341d1f7497c5a3ca0ac857ce78172c4732bdc86a9c66e46419",
                        "reviewed_at": RETRIEVED,
                        "review_method": "ai-assisted-source-review",
                    },
                ],
            },
            sources=[],
        ),
        record(
            SRC_README,
            "source",
            "HyInv package README (Tencent Hunyuan, commit 0dcc533c)",
            "README of the released hyinv package, with the checkpoint identity, the command line "
            "and Python interface, the input and output formats and the accelerated inference modes.",
            {
                "url": f"{BLOB}/AI4Science/hyinv/README.md",
                "artifact_url": f"{RAW}/AI4Science/hyinv/README.md",
                "version": f"GitHub repository Tencent-Hunyuan/Hyra-results at commit {COMMIT}",
                "retrieved_at": RETRIEVED,
                "artifact_sha256": "b44c6d0c4c7f73aaf920cf734670a8d4649df175c14a105afaf5e74172fd6891",
                "publication_status": "official_project_source",
                "licence": "MIT (AI4Science/hyinv/LICENSE)",
                "media_type": "text/markdown",
                "source_type": "repository README",
                "archive_note": "Archived in the batch as artifacts/hyinv-README.md.",
                "archive_sha256": "b44c6d0c4c7f73aaf920cf734670a8d4649df175c14a105afaf5e74172fd6891",
                "limitations": [
                    "The README's speed figures differ from the technical report's for the exact FP32 "
                    "path (about 119 / 281 ms against the report's 130 / 303 ms) because, as it states, "
                    "the report's exact path uses another set of kernels. The report's values are the "
                    "ones recorded as results.",
                    "The README states the weights are the structure-reward reinforcement-learning "
                    "version but does not print an update number; the report's update 640 is what "
                    "identifies the checkpoint, and no hash of the weights file is published.",
                ],
            },
            links=[{"relation": "companion_of", "target_id": SRC_REPORT}],
            sources=[],
        ),
        record(
            SRC_LICENCE,
            "source",
            "HyInv LICENSE (MIT, commit 0dcc533c)",
            "MIT licence file of the released hyinv package, which also carries the ProteinMPNN "
            "copyright the model modules come from.",
            {
                "url": f"{BLOB}/AI4Science/hyinv/LICENSE",
                "artifact_url": f"{RAW}/AI4Science/hyinv/LICENSE",
                "version": f"GitHub repository Tencent-Hunyuan/Hyra-results at commit {COMMIT}",
                "retrieved_at": RETRIEVED,
                "artifact_sha256": "816fb3d74b232ce2348dc1e4d93e41564780985789bd01fd4a15369af99ce350",
                "publication_status": "official_project_source",
                "licence": "MIT",
                "media_type": "text/plain",
                "source_type": "licence file",
                "code_licence": "MIT",
                "archive_note": "Archived in the batch as artifacts/hyinv-LICENSE.",
                "archive_sha256": "816fb3d74b232ce2348dc1e4d93e41564780985789bd01fd4a15369af99ce350",
                "scope_note": "Holds two copyright lines: 'Copyright (c) 2022 Justas Dauparas "
                              "(ProteinMPNN)' and 'Copyright (c) 2026 HyInv contributors'. The "
                              "repository's top-level LICENSE is Apache-2.0, so the package licence "
                              "and the repository licence differ.",
            },
            links=[{"relation": "companion_of", "target_id": SRC_REPORT}],
            sources=[],
        ),
    ]


def models():
    """The released model, the native-sequence control and the baseline models
    that the store does not already hold at family level."""
    out = [
        record(
            MODEL,
            "model",
            "HyInv",
            "HyInv designs amino-acid sequences for a supplied protein backbone with a "
            "message-passing graph network and a two-temperature draft-and-rewrite sampler.",
            {
                "reported_name": "HyInv",
                "entity_level": "checkpoint",
                "version": "Released weights, 2026-11-02: the structure-reward reinforcement-learning "
                           "checkpoint at update 640 of a 656-update run, with draft temperature 0.6 "
                           "and rewrite temperature 0.34 as the deployed default; technical report "
                           "dated 2026-10-14",
                "licence": "MIT (AI4Science/hyinv/LICENSE), which also carries the ProteinMPNN "
                           "copyright the model modules come from",
                "access": "Public: the hyinv package, its command line and Python API, and the FP32 "
                          "weights (model.safetensors, 7.8 MB) ship in AI4Science/hyinv/ of the "
                          "Tencent-Hunyuan/Hyra-results repository. Python 3.10+ and PyTorch; "
                          "accelerated inference also needs triton. Runs on CPU and GPU.",
                "training_data": "Supervised stage: 627,945 unique sequences from natural and "
                                 "predicted structures, weighted to give experimental structures about "
                                 "70% and predicted structures about 30% of the expected loss mass. "
                                 "Reinforcement-learning stage: a pool of 50,000 backbones (16,839 "
                                 "experimental, 33,161 predicted; mean length 254, range 48 to 512) "
                                 "filtered against the benchmark panels with a same-source MMseqs2 "
                                 "homology mask. The authors do not claim zero sequence overlap with "
                                 "the evaluation panels.",
                "source_locator": "AI4Science/hyinv/README.md opening paragraph, 'Layout' and "
                                  "'Citation and license'; technical report Sections 2 and 2.1, "
                                  "Section 3.2, Appendix C and Table 4",
                "provenance_note": "Released by Tencent Hunyuan as part of the Hyra Results "
                                   "repository and trained by the team's Hyra 2.0 research agent. "
                                   "Authors: Haowei Lin, Cai Zhou and Xiangxin Zhou. Kept at "
                                   "checkpoint level because the report names the evaluated update "
                                   "(640) and the README states the released weights are that "
                                   "structure-reward reinforcement-learning version.",
                "missing_metadata": {
                    "checkpoint_revision": {
                        "reason": "unreported",
                        "note": "No hash or revision is published for weights/model.safetensors, and "
                                "the README prints no update number.",
                    },
                },
            },
            sources=[SRC_REPORT, SRC_README, SRC_LICENCE, SRC_REPO],
        ),
        record(
            NATIVE,
            "method",
            "Native sequence refold (HyInv report control)",
            "Refolds the experimental sequence of a benchmark chain with the report's structure "
            "predictor, to give the score a native sequence reaches under the same protocol.",
            {
                "reported_name": "Native",
                "entity_level": "method",
                "reference_kind": "native-sequence control",
                "source_locator": "Table 6 row 'Native' and its footnote; Figures 14 and 15 row "
                                  "'Native'; Appendix A 'Folding and seeds'",
                "provenance_note": "A control row of the HyInv report, not a design method. Recorded "
                                   "so that the Native cells of Table 6 and Figures 14 and 15 have a "
                                   "system to attach to.",
            },
        ),
    ]
    new_baselines = [
        (
            "proteinzero-v2",
            "ProteinZero V2",
            "ProteinZero V2 designs sequences for a supplied backbone with an inverse-folding model "
            "improved by online reinforcement learning against a structure predictor.",
            "ProteinZero V2",
            "Version 2 as run in the HyInv report, with the ESM1 and the ESM2 variant; the cited "
            "preprint is arXiv:2506.07459, first posted June 2025, version 5 revised September 2026",
            "Wang et al., ProteinZero: Self-improving protein generation via online reinforcement "
            "learning, arXiv:2506.07459. Declared by its authors for backbones of up to 100 residues; "
            "the HyInv report runs it on the full panels.",
        ),
        (
            "cmlm",
            "CMLM",
            "CMLM designs a sequence for a supplied backbone by conditional masked language "
            "modelling, decoding all positions in parallel from one categorical distribution.",
            "CMLM",
            "As run in the HyInv report; the cited paper is Ghazvininejad et al. 2019",
            "Ghazvininejad et al., Mask-predict: Parallel decoding of conditional masked language "
            "models, EMNLP-IJCNLP 2019.",
        ),
        (
            "lm-design",
            "LM-Design",
            "LM-Design designs sequences for a supplied backbone by reprogramming a protein language "
            "model with structural information.",
            "LM-Design 650M",
            "650M variant as run in the HyInv report; the cited paper is Zheng et al. 2023",
            "Zheng et al., Structure-informed language models are protein designers, ICML 2023.",
        ),
        (
            "dplm-2",
            "DPLM-2",
            "DPLM-2 is a multimodal diffusion protein language model that generates sequence and "
            "structure, and designs a sequence for a supplied backbone.",
            "DPLM-2 3B",
            "3B variant as run in the HyInv report; the cited paper is Wang et al. 2025 (ICLR)",
            "Wang et al., DPLM-2: A multimodal diffusion protein language model, ICLR 2025 "
            "(arXiv:2410.13782).",
        ),
        (
            "ligandmpnn",
            "LigandMPNN",
            "LigandMPNN designs amino-acid sequences for a supplied backbone conditioned on the "
            "atomic context of bound ligands and cofactors.",
            "LigandMPNN",
            "As run in the HyInv report, on backbone coordinates only; the cited preprint is "
            "Dauparas et al. 2023",
            "Dauparas et al., Atomic context-conditioned protein sequence design using LigandMPNN, "
            "bioRxiv 2023. The HyInv report runs it on backbone coordinates only, so its ligand "
            "context is unused there.",
        ),
    ]
    for slug, name, description, reported, version, note in new_baselines:
        out.append(
            record(
                f"{B}-model-{slug}",
                "model",
                name,
                description,
                {
                    "reported_name": reported,
                    "entity_level": "family",
                    "version": version,
                    "access": "Released weights, used by the HyInv report at their published setting.",
                    "source_locator": "Technical report Section 5.1 'Baselines', Appendix D.1 and "
                                      "Table 5; references list",
                    "provenance_note": note + " Created here because the store held no record of this "
                                              "model; identity is as named by the HyInv report and its "
                                              "citation, which does not print a checkpoint revision.",
                    "missing_metadata": {
                        "checkpoint_revision": {
                            "reason": "unreported",
                            "note": "Table 5 states all baselines use the released weights but prints "
                                    "no revision or hash.",
                        },
                        "licence": {"reason": "unextracted", "note": "Not stated in these sources."},
                        "training_data": {
                            "reason": "unreported",
                            "note": "Not stated in these sources.",
                        },
                    },
                },
                sources=[SRC_REPORT],
            )
        )
    return out


BASELINE_SETTINGS = {
    "ProteinMPNN": (
        "config-proteinmpnn", PROTEINMPNN_MODEL,
        "ProteinMPNN at its published setting: autoregressive decoding at temperature 0.1.",
        "autoregressive, T = 0.1",
        "Released weights; the report regenerated no cell for this row (Table 5 'Regenerated on': none).",
    ),
    "ProteinMPNN grouped": (
        "config-proteinmpnn-grouped", PROTEINMPNN_MODEL,
        "ProteinMPNN with grouped autoregressive decoding at temperature 0.1.",
        "autoregressive, grouped, T = 0.1",
        "Released weights; regenerated on CATH4.3 test with |dscTM| 0.0009 and 100.0% identical sequences.",
    ),
    "ProteinMPNN (low-noise, grouped)": (
        "config-proteinmpnn-low-noise-grouped", PROTEINMPNN_MODEL,
        "ProteinMPNN with grouped autoregressive decoding at temperature 0.1 and the checkpoint "
        "trained with less coordinate noise.",
        "autoregressive, grouped, T = 0.1, low-coordinate-noise checkpoint",
        "Released weights; regenerated on four panels with |dscTM| 0.0007 and 100.0% identical sequences.",
    ),
    "ProteinZero V2 (ESM2)": (
        "config-proteinzero-v2-esm2", f"{B}-model-proteinzero-v2",
        "ProteinZero V2 with the ESM2 weights, decoding autoregressively at temperature 0.1.",
        "autoregressive, T = 0.1, ESM2 weights",
        "Released weights; the report regenerated no cell for this row (Table 5 'Regenerated on': none). "
        "Declared by its authors for backbones of up to 100 residues and run here on the full panels.",
    ),
    "ProteinZero V2 (ESM1)": (
        "config-proteinzero-v2-esm1", f"{B}-model-proteinzero-v2",
        "ProteinZero V2 with the ESM1 weights, decoding autoregressively at temperature 0.1.",
        "autoregressive, T = 0.1, ESM1 weights",
        "Released weights; regenerated on CATH4.3 test with |dscTM| 0.0006 and 100.0% identical "
        "sequences. Declared by its authors for backbones of up to 100 residues and run here on the "
        "full panels.",
    ),
    "PiFold": (
        "config-pifold", PIFOLD_MODEL,
        "PiFold decoding all positions in one parallel pass from one categorical distribution at "
        "temperature 0.1.",
        "one parallel pass, T = 0.1",
        "Released weights; regenerated on four panels with |dscTM| 0.0004 and 100.0% identical sequences.",
    ),
    "CMLM": (
        "config-cmlm", f"{B}-model-cmlm",
        "CMLM decoding all positions in one parallel pass from one categorical distribution at "
        "temperature 0.1.",
        "one parallel pass, T = 0.1",
        "Released weights; regenerated on four panels with |dscTM| 0.0022 and 100.0% identical sequences.",
    ),
    "LM-Design 650M": (
        "config-lm-design-650m", f"{B}-model-lm-design",
        "LM-Design 650M decoding by five-step iterative denoising at temperature 0.1.",
        "iterative denoising (5 steps), T = 0.1",
        "Released weights; regenerated on four panels with |dscTM| 0.0005 and 100.0% identical sequences.",
    ),
    "DPLM-2 3B": (
        "config-dplm-2-3b", f"{B}-model-dplm-2",
        "DPLM-2 3B decoding by argmax with deterministic unmasking over 100 steps, run in BF16 autocast.",
        "argmax decoding (100 steps), T = 0.1, BF16 autocast",
        "Released weights; regenerated on four panels with |dscTM| 0.0001 and 99.2% identical "
        "sequences. Because it decodes by argmax, its two designs of a chain are almost always the "
        "same sequence, and its printed diversity on CATH4.3 test is 0.000.",
    ),
    "LigandMPNN": (
        "config-ligandmpnn", f"{B}-model-ligandmpnn",
        "LigandMPNN decoding autoregressively at temperature 0.1 on backbone coordinates only.",
        "autoregressive, T = 0.1, backbone coordinates only",
        "Released weights; regenerated on four panels with |dscTM| 0.0005 and 100.0% identical sequences.",
    ),
}

HYINV_SETTINGS = {
    "config-hyinv-default": (
        "HyInv default",
        "HyInv as deployed: the update-640 reinforcement-learning checkpoint sampled by the "
        "draft-and-rewrite sampler at draft temperature 0.6 and rewrite temperature 0.34.",
        "Final checkpoint, update 640. Draft-and-rewrite sampler: one encoder pass, 8 blind draft "
        "rounds at T = 0.6 over 8 fixed random groups, then 8 rewrite rounds at T = 0.34, 16 decoder "
        "passes in all. Truncation q = 0.9 (top-p) and m = 0.1 (min-p). FP32 reference sampler. "
        "Checkpoint and both temperatures were chosen on the development panel (CATH4.3 validation) "
        "at development diversity 0.30, before any test panel was generated.",
        "Section 5.1 'HyInv'; Section 3.1 and 3.2; Appendix A 'Checkpoint and sampler setting'; "
        "Appendix E",
    ),
    "config-hyinv-reference-sampler-timing": (
        "HyInv FP32 reference sampler (timing configuration)",
        "HyInv run by the unoptimised FP32 reference sampler, as timed in the report's "
        "inference-time measurements.",
        "Reference implementation of the draft-and-rewrite sampler, FP32. Timed with the "
        "supervised-stage weights (same architecture and tensor shapes as the final checkpoint) and a "
        "rewrite temperature of 0.23.",
        "Table 1 row 'HyInv, FP32 reference sampler' and its footnote; Figure 4a row 'HyInv reference "
        "sampler'; Appendix F 'Timing protocol'",
    ),
    "config-hyinv-exact-fp32-timing": (
        "HyInv exact FP32 path (timing configuration)",
        "HyInv run by the accelerated FP32 path, which returns the reference sampler's sequences, as "
        "timed in the report's inference-time measurements.",
        "Exact FP32 path: matrix products by a three-pass TF32 emulation of FP32, erf GELU, no BF16 "
        "operands; fused Triton kernels and CUDA graph capture. Returns the reference sampler's "
        "sequences for the same seeds (1,600 of 1,600 eager, 400 of 400 with graph capture, 352 of 352 "
        "in padded multi-target batches), and graph replay equals eager execution bit for bit. Timed "
        "with the supervised-stage weights and a rewrite temperature of 0.23.",
        "Table 1 row 'HyInv, exact FP32 path' and its footnote; Appendix F 'The two numerical paths' "
        "and 'Timing protocol'",
    ),
    "config-hyinv-bf16-timing": (
        "HyInv BF16 path (timing configuration)",
        "HyInv run by the fastest BF16 path, as timed in the report's inference-time measurements.",
        "BF16 path: edge messages and the node update with BF16 operands and FP32 accumulation, "
        "hardware tanh GELU, FP32 inputs and outputs, fused Triton kernels, one CUDA graph per shape "
        "bucket with pre-drawn noise. A numerically different path from the reference sampler, not "
        "sequence-identical to it. Timed with the supervised-stage weights and a rewrite temperature "
        "of 0.23, 128 candidates per request and a maximum candidate batch of 32.",
        "Table 1 row 'HyInv (BF16)' and its footnote; Figure 4a; Appendix F 'The two numerical paths' "
        "and 'Timing protocol'",
    ),
    "config-hyinv-reference-update288": (
        "HyInv FP32 reference sampler (update 288, equal-diversity read-out)",
        "Designs sequences for a backbone with the update-288 reinforcement-learning checkpoint "
        "through the unoptimised FP32 reference sampler.",
        "Reference sampler, FP32, RL checkpoint at update 288. Development read-out: scTM at diversity "
        "0.30 from a quadratic fit through four rewrite temperatures, draft temperature 0.6, ESMFold2, "
        "2 designs per chain.",
        "Table 9 and its footnote; Appendix F 'Quality of the BF16 path'",
    ),
    "config-hyinv-bf16-update288": (
        "HyInv BF16 path (update 288, equal-diversity read-out)",
        "Designs sequences for a backbone with the update-288 reinforcement-learning checkpoint "
        "through the BF16 inference path.",
        "BF16 path, RL checkpoint at update 288. Same development read-out as the reference sampler: "
        "scTM at diversity 0.30 from a quadratic fit through four rewrite temperatures, draft "
        "temperature 0.6, ESMFold2, 2 designs per chain.",
        "Table 9 and its footnote; Appendix F 'Quality of the BF16 path'",
    ),
    "config-hyinv-unmodified-sampler-update288": (
        "HyInv unmodified sampler (update 288)",
        "HyInv at the update-288 checkpoint sampled at a single temperature by the unmodified "
        "sampler, which is the reference setting of the report's sampler confirmation.",
        "Unmodified single-temperature sampler, RL checkpoint at update 288, rewrite-temperature grid "
        "{0.3, 0.4, 0.5, 0.7}. The reference against which the decoupled and truncated settings of "
        "Table 8 are measured at equal diversity.",
        "Table 8 and its footnote; Appendix A 'Scores at equal diversity'; Appendix E 'Confirmation of "
        "the decoupled draft'",
    ),
    "config-hyinv-decoupled-td06-update288": (
        "HyInv decoupled draft Td = 0.6 (update 288)",
        "HyInv at the update-288 checkpoint sampled with separate draft and rewrite temperatures at "
        "draft temperature 0.6, which is the released default's draft setting.",
        "Decoupled draft-and-rewrite sampler at draft temperature 0.6, rewrite-temperature grid "
        "{0.1, 0.2, 0.3, 0.5}, RL checkpoint at update 288. The setting of the released default, "
        "confirmed on held-out panels with new draws and fold seeds.",
        "Table 8 row 'Decoupled draft, Td = 0.6 (HyInv default)'; Appendix E 'Confirmation of the "
        "decoupled draft'",
    ),
    "config-hyinv-decoupled-td03-update288": (
        "HyInv decoupled draft Td = 0.3 (update 288)",
        "HyInv at the update-288 checkpoint sampled with separate draft and rewrite temperatures at "
        "draft temperature 0.3.",
        "Decoupled draft-and-rewrite sampler at draft temperature 0.3, rewrite-temperature grid "
        "{0.3, 0.4, 0.5, 0.7}, RL checkpoint at update 288.",
        "Table 8 row 'Decoupled draft, Td = 0.3'; Appendix A 'Scores at equal diversity'",
    ),
    "config-hyinv-topp09-update288": (
        "HyInv top-p 0.9 truncation (update 288)",
        "HyInv at the update-288 checkpoint sampled by the unmodified sampler with top-p truncation "
        "at 0.9.",
        "Unmodified single-temperature sampler with top-p truncation at q = 0.9, RL checkpoint at "
        "update 288.",
        "Table 8 row 'Top-p 0.9'; Appendix E 'Random streams, truncation and fixed residues'",
    ),
    "config-hyinv-minp01-update288": (
        "HyInv min-p 0.1 truncation (update 288)",
        "HyInv at the update-288 checkpoint sampled by the unmodified sampler with min-p truncation "
        "at 0.1.",
        "Unmodified single-temperature sampler with min-p truncation at m = 0.1, RL checkpoint at "
        "update 288.",
        "Table 8 row 'Min-p 0.1'; Appendix E 'Random streams, truncation and fixed residues'",
    ),
    "config-hyinv-plain-sampling-update640": (
        "HyInv plain sampling (update 640)",
        "HyInv at the released update-640 checkpoint sampled at a single temperature, which is the "
        "reinforcement-learning ablation's trained arm.",
        "Plain single-temperature sampling, final RL checkpoint at update 640, read at development "
        "diversity 0.30.",
        "Section 5.4 'Reinforcement learning'; Figure 8a; Figure 13b",
    ),
    "config-hyinv-plain-sampling-supervised": (
        "HyInv supervised checkpoint, plain sampling",
        "HyInv at the supervised-stage checkpoint, before reinforcement learning, sampled at a single "
        "temperature.",
        "Plain single-temperature sampling, supervised-stage checkpoint (85,000 updates of "
        "random-order likelihood training), read at development diversity 0.30.",
        "Section 5.4 'Reinforcement learning'; Figure 8a; Table 4",
    ),
}


def configurations():
    out = []
    for slug, (name, description, parameters, locator) in HYINV_SETTINGS.items():
        out.append(
            record(
                f"{B}-{slug}",
                "configuration",
                f"{name} (HyInv report)",
                description,
                {
                    "reported_name": name.split(" (")[0],
                    "version": "HyInv as released 2026-11-02; technical report dated 2026-10-14",
                    "parameters": parameters,
                    "foundation_model_eligible": False,
                    "access_reuse": "Public MIT-licensed weights and code in AI4Science/hyinv/ at "
                                    f"commit {COMMIT[:8]}",
                    "source_locator": locator,
                },
                links=[{"relation": "configuration_of", "target_id": MODEL}],
                sources=[SRC_REPORT, SRC_README],
            )
        )
    for label, (slug, model_id, description, decoding, note) in BASELINE_SETTINGS.items():
        out.append(
            record(
                f"{B}-{slug}",
                "configuration",
                f"{label} (HyInv report)",
                description,
                {
                    "reported_name": label,
                    "version": "Released weights at the published setting, as run in the HyInv "
                               "technical report; no checkpoint revision printed",
                    "parameters": f"Decoding: {decoding}. " + note,
                    "foundation_model_eligible": False,
                    "temperature_note": "One published single-temperature setting, not tuned to the "
                                        "panels, so its design-set diversity is whatever that setting "
                                        "gives and is not matched to HyInv's.",
                    "source_locator": "Table 5 row "
                                      f"'{label}'; Section 5.1 'Baselines'; Appendix D.1",
                    "missing_metadata": {
                        "checkpoint_revision": {
                            "reason": "unreported",
                            "note": "Table 5 states the released weights were used but prints no "
                                    "revision or hash.",
                        },
                    },
                },
                links=[{"relation": "configuration_of", "target_id": model_id}],
                sources=[SRC_REPORT],
            )
        )
    return out


PANEL_DATA = {
    "CATH4.3 test": (
        "data-cath43-test", "CATH4.3 test (1,882 chains)", "1,882", "103",
        "Test split of CATH 4.3, 1,882 chains in 103 CATH topology clusters.",
        "test",
    ),
    "CATH4.2 test": (
        "data-cath42-test", "CATH4.2 test (1,120 chains)", "1,120", "109",
        "Test split of CATH 4.2 as used by Ingraham et al. 2019, 1,120 chains in 109 CATH "
        "topology clusters.",
        "test",
    ),
    "TS500": (
        "data-ts500", "TS500 (500 chains)", "500", "500",
        "TS500 inverse-folding test set of 500 chains, as used by Gao et al. 2023; one cluster "
        "per chain for the report's resampling.",
        "test",
    ),
    "TS50": (
        "data-ts50", "TS50 (50 chains)", "50", "50",
        "TS50 inverse-folding test set of 50 chains, as used by Gao et al. 2023; one cluster per "
        "chain for the report's resampling.",
        "test",
    ),
    "RecentPDB": (
        "data-recentpdb", "RecentPDB (121 chains from 111 recent PDB entries)", "121", "121",
        "121 experimental chains from 111 recent PDB entries, 26,766 residues, lengths 42 to 978: "
        "all standard chains with complete backbones and no length truncation, screened for homology "
        "to PDB and CATH entries before 2025 and fixed before evaluation, not selected by model "
        "performance.",
        "test",
    ),
    "CATH4.3 validation": (
        "data-cath43-validation", "CATH4.3 validation (1,529 chains, development panel)", "1,529",
        "91",
        "Validation split of CATH 4.3, 1,529 chains in 91 CATH topology clusters. The report's "
        "development panel: it fixed the sampler setting and the checkpoint and monitored "
        "reinforcement-learning training, so it is not a held-out test set.",
        "validation",
    ),
}


def datasets():
    out = []
    for label, (slug, name, chains, clusters, scope, split) in PANEL_DATA.items():
        out.append(
            record(
                f"{B}-{slug}",
                "dataset",
                name,
                scope.split(".")[0] + ".",
                {
                    "reported_name": label,
                    "version": "As assembled for the HyInv technical report (2026-10-14)",
                    "split": split,
                    "total_targets": int(chains.replace(",", "")),
                    "independent_test_groups": int(clusters.replace(",", "")),
                    "scope_note": scope + " A residue is a valid site if its N, CA, C and O atoms are "
                                  "present and its native residue is a standard amino acid; all scores "
                                  "are computed over valid sites. Panel values are macro-averages over "
                                  "chains.",
                    "source_locator": "Table 3 row "
                                      f"'{label}'; Section 5.1 'Panels'; Appendix A 'Panels'",
                    "reuse_restrictions": "Chain lists are not published with the report.",
                    "missing_metadata": {
                        "manifest": {
                            "reason": "unavailable",
                            "note": "The report publishes no chain list or split manifest for this "
                                    "panel, so the exact targets cannot be checked.",
                        },
                    },
                },
                sources=[SRC_REPORT],
            )
        )
    out.append(
        record(
            f"{B}-data-de-novo-backbones",
            "dataset",
            "De novo backbones application panel (74 backbones)",
            "74 de novo protein backbones used as the HyInv report's de novo design application panel.",
            {
                "reported_name": "74 de novo backbones",
                "version": "As assembled for the HyInv technical report (2026-10-14)",
                "split": "application panel",
                "total_targets": 74,
                "independent_test_groups": 58,
                "scope_note": "74 de novo backbones in 58 clusters of 30% sequence identity, none "
                              "with a hit that passes the report's homology rule, with 4 designs per "
                              "backbone; the control is a set of 193 length-matched native chains. "
                              "Table 10 records that 28 of the 74 have partial homology hits that stay "
                              "below the coverage limit, so the screen is weaker than no similar "
                              "fragment in the library.",
                "source_locator": "Section 6 'De novo backbones'; Appendix G 'De novo backbones'; "
                                  "Table 10 row 'De novo backbones'",
                "missing_metadata": {
                    "manifest": {
                        "reason": "unavailable",
                        "note": "The report names four backbones in Figure 9a (9DWA, 2LCI, 7M5T, "
                                "2LR0) but publishes no list of the 74.",
                    },
                },
            },
            sources=[SRC_REPORT],
        )
    )
    out.append(
        record(
            f"{B}-data-latency-backbones",
            "dataset",
            "Timing backbones for the HyInv inference-time measurements",
            "The single backbones of 148, 402 and 250 residues on which the HyInv report times a "
            "design request.",
            {
                "reported_name": "148 res. / 402 res. / 250-residue backbone",
                "version": "As used for the HyInv technical report's timings (2026-10-14)",
                "split": "timing input",
                "scope_note": "One 148-residue and one 402-residue backbone for the 128-design "
                              "columns and one 250-residue backbone for the 10,000-design column. "
                              "Every system designs 128 candidates per request with a maximum "
                              "candidate batch of 32.",
                "source_locator": "Table 1 header and footnote; Figure 4a; Appendix F 'Timing "
                                  "protocol'",
                "missing_metadata": {
                    "manifest": {
                        "reason": "unreported",
                        "note": "The report identifies the timing backbones by length only; no PDB "
                                "identifiers are printed.",
                    },
                },
            },
            sources=[SRC_REPORT],
        )
    )
    return out


def dataset_subsets():
    out = []
    for index, (targets, clusters) in enumerate(
        [("512", "51"), ("512", "50"), ("505", "61")], start=1
    ):
        out.append(
            record(
                f"{B}-data-cath43-validation-subset-{index}",
                "dataset_subset",
                f"CATH4.3 validation subset {index} ({targets} chains)",
                f"Subset {index} of the HyInv report's development panel, one of the three disjoint "
                "parts whose union is the whole panel.",
                {
                    "version": "As used for the HyInv technical report's numerics check (2026-10-14)",
                    "population_count": f"{int(targets)} chains",
                    "independent_groups": int(clusters),
                    "source_dataset": f"{B}-data-cath43-validation",
                    "subset_scope": f"Printed as 'Subset {index}'. {targets} chains in {clusters} "
                                    "CATH topology clusters, one of the three disjoint parts whose "
                                    "union is the whole development panel. The report states that "
                                    "subsets of about five hundred chains cannot resolve a difference "
                                    "of the size checked.",
                    "source_locator": f"Table 9 row 'Subset {index}' and its footnote",
                    "missing_metadata": {
                        "exact_manifest": {
                            "reason": "unavailable",
                            "note": "No chain list is published for the subsets.",
                        },
                    },
                },
                # same_data_as is the only data-to-data relation; the subset is one
                # disjoint third of that panel, which the scope note states.
                links=[
                    {"relation": "same_data_as", "target_id": f"{B}-data-cath43-validation"},
                ],
                sources=[SRC_REPORT],
            )
        )
    return out


def benchmark():
    return [
        record(
            BENCHMARK,
            "benchmark",
            "HyInv technical report inverse-folding comparison",
            "Compares inverse-folding methods by the structural consistency, native recovery and "
            "diversity of the sequences they design for held-out protein backbones.",
            {
                "entity_level": "suite",
                "version": "HyInv technical report, 2026-10-14",
                "task": "Protein inverse folding: design amino-acid sequences for a given backbone, "
                        "scored by refolding the designs and comparing the predicted structure with "
                        "the input backbone.",
                "scope_note": "Five test panels (CATH4.3 test, CATH4.2 test, TS500, TS50, RecentPDB) "
                              "with ESMFold2, RecentPDB also with Boltz2 and Protenix2, giving seven "
                              "panel-predictor columns; a development panel (CATH4.3 validation) that "
                              "fixed the checkpoint and sampler; and four single-chain design "
                              "applications. Assembled and run by the model's own authors, so every "
                              "evaluation in it is author-reported.",
                "limitations": [
                    "Author-assembled and author-run: the panels, the baseline settings and the "
                    "scoring were all chosen by the team that released HyInv.",
                    "Baselines are single published settings, so comparisons are at comparable rather "
                    "than equal sequence diversity.",
                    "ESMFold2 is the primary predictor and also the reinforcement-learning reward.",
                    "No chain list or split manifest is published, so the panels cannot be rebuilt.",
                ],
                "source_locator": "Sections 5 and 6; Table 3; Appendices A, D and G",
                "missing_metadata": {
                    "split_manifest": {
                        "reason": "unavailable",
                        "note": "No manifest is published for any panel.",
                    },
                },
            },
            links=[{"relation": "evaluates_task", "target_id": "catalog-task-protein-design"}],
            sources=[SRC_REPORT],
        )
    ]


FOLDING = (
    "ESMFold2 runs with its fused backend, 3 recycling loops, 50 diffusion steps and one structure "
    "per sequence, in FP32 with TF32 off; the input is the designed sequence with sequence-derived "
    "templates only, and native coordinates enter only through TM-align. Fold seeds on the public "
    "panels with K = 2 designs per chain are the seeds recorded with the baseline samples, so "
    "comparisons with baseline sequences share the folding randomness."
)
PAIRED = (
    "A paired difference is the macro-average of the per-chain difference between HyInv and the "
    "baseline. Its 95% interval is the percentile interval of 10,000 resamples of the resampling unit "
    "(CATH topology cluster on the two CATH panels, single chain elsewhere) with one resample shared "
    "by all rows compared and a fixed seed (20260922). Intervals are not adjusted for multiple "
    "comparisons, and the report notes that a few starred intervals have a lower end within 0.001 of "
    "zero."
)
EQUAL_DIVERSITY = (
    "A sampler family is evaluated at a grid of rewrite temperatures, giving points of diversity and "
    "scTM on the same chains. The scTM at fixed diversity D is the value at D of the least-squares "
    "quadratic fit s = a + b*d + c*d^2, with no extrapolation."
)
DIVERSITY_CAVEAT = (
    "Baselines run at one published temperature each, so their design-set diversity is not matched to "
    "HyInv's: Appendix D.2 states that PiFold, CMLM, LM-Design and DPLM-2 3B are single points at much "
    "lower diversity than HyInv and that their differences are not at matched diversity. This protocol "
    "does not read scTM at a stated diversity level."
)

PROTOCOLS = {
    "protocol-sctm-esmfold2": dict(
        name="scTM of designed sequences under ESMFold2",
        description="Design sequences for each panel backbone, fold them with ESMFold2 and score the "
                    "TM-score of each predicted structure against the input backbone.",
        metric="sctm", direction="higher", unit="unitless",
        qualifier="Mean TM-score of the predicted structure to the native backbone, averaged over the "
                  "designs of a target and then over targets (macro-average); computed on the CA trace "
                  "at valid sites, normalised by the native length and clipped at one; ESMFold2 as the "
                  "structure predictor, which is also the reinforcement-learning reward of HyInv",
        implementation="TM-align (Zhang and Skolnick 2005) of the ESMFold2 prediction against the "
                       "native CA trace at valid sites. " + FOLDING,
        aggregation="Designs of a target averaged first, then a macro-average over the chains of the "
                    "panel. A failed fold is a gap in the average, not imputed.",
        locator="Table 6, ESMFold2 columns; Section 5.1 'Metrics'; Appendix A; Appendix B 'scTM'",
        limits=[DIVERSITY_CAVEAT,
                "ESMFold2 is also the reward predictor of HyInv's reinforcement learning, so this "
                "protocol is not independent of the trained model.",
                "Appendix A records run-to-run noise of about +/-0.0015 per panel."],
        data=None,
    ),
    "protocol-sctm-boltz2": dict(
        name="scTM of designed sequences under Boltz2",
        description="Fold the RecentPDB designs with Boltz2 and score the TM-score of each predicted "
                    "structure against the input backbone.",
        metric="sctm", direction="higher", unit="unitless",
        qualifier="Mean TM-score of the predicted structure to the native backbone, averaged over the "
                  "designs of a target and then over targets; Boltz2 as the structure predictor, with "
                  "the alignment built from the designed sequence by MMseqs2 against UniRef50; "
                  "RecentPDB only",
        implementation="Boltz2 (Passaro et al. 2025) on the same RecentPDB design sequences as the "
                       "ESMFold2 column, with an MMseqs2 alignment against UniRef50.",
        aggregation="Designs of a target averaged first, then a macro-average over the 121 chains.",
        locator="Table 6, column 'Boltz2'; Section 5.3; Appendix A 'Folding and seeds'",
        limits=[DIVERSITY_CAVEAT,
                "The report states these scores partly reflect resemblance to a natural family, "
                "because the alignment is built from the designed sequence, and serve as a robustness "
                "check rather than a primary measurement."],
        data=f"{B}-data-recentpdb",
    ),
    "protocol-sctm-protenix2": dict(
        name="scTM of designed sequences under Protenix2",
        description="Fold the RecentPDB designs with Protenix2 and score the TM-score of each "
                    "predicted structure against the input backbone.",
        metric="sctm", direction="higher", unit="unitless",
        qualifier="Mean TM-score of the predicted structure to the native backbone, averaged over the "
                  "designs of a target and then over targets; Protenix2 as the structure predictor, "
                  "with the alignment built from the designed sequence by MMseqs2 against UniRef50; "
                  "RecentPDB only",
        implementation="Protenix2 (Zhang et al. 2026) on the same RecentPDB design sequences as the "
                       "ESMFold2 column, with an MMseqs2 alignment against UniRef50.",
        aggregation="Designs of a target averaged first, then a macro-average over the 121 chains.",
        locator="Table 6, column 'Protenix2'; Section 5.3; Appendix A 'Folding and seeds'",
        limits=[DIVERSITY_CAVEAT,
                "The report states these scores partly reflect resemblance to a natural family, "
                "because the alignment is built from the designed sequence, and serve as a robustness "
                "check rather than a primary measurement."],
        data=f"{B}-data-recentpdb",
    ),
    "protocol-sequence-recovery": dict(
        name="Native sequence recovery of designed sequences",
        description="Measure the fraction of scored positions at which a designed sequence carries "
                    "the native residue.",
        metric="sequence-recovery", direction="higher", unit="fraction",
        qualifier="Fraction of valid sites at which the design carries the native residue, averaged "
                  "over the designs of a target and then over targets; descriptive in this report, "
                  "with weight zero in HyInv's reward and no role in checkpoint selection",
        implementation="Position-wise comparison of the designed sequence with the native sequence at "
                       "valid sites. No structure prediction is involved.",
        aggregation="Designs of a target averaged first, then a macro-average over the chains.",
        locator="Figure 14, 'Recovery' block; Appendix B 'Recovery'",
        limits=["Appendix B states recovery is descriptive and not an objective: methods with high "
                "recovery tend to have low diversity and lower scTM, so a higher value is not "
                "evidence of a better design method.",
                "Printed inside Figure 14 as a labelled numeric matrix rather than in a numbered "
                "table."],
        data=None,
    ),
    "protocol-sequence-diversity": dict(
        name="Sequence diversity of a design set",
        description="Measure how different the sequences a method designs for one backbone are from "
                    "each other.",
        metric="sequence-diversity", direction="unknown", unit="fraction",
        qualifier="Mean pairwise normalised Hamming distance between the K designs of a chain over "
                  "valid sites, then a macro-average over targets; counted at valid sites for every "
                  "method, because baseline sequences carry X at invalid sites and counting those as "
                  "identical would lower their diversity",
        implementation="D = 2/(K(K-1)) * sum over design pairs of the normalised Hamming distance "
                       "over valid sites (Appendix A, equation 2). The report gives ProteinMPNN on "
                       "CATH4.3 test as 0.290 at all sites against 0.314 at valid sites.",
        aggregation="Macro-average over the chains of the panel.",
        locator="Figure 14, 'Diversity' block; Appendix A 'Scores'; Appendix B 'Diversity'",
        limits=["Appendix B states diversity is a property of the design set and is matched rather "
                "than ranked, so neither direction is better on its own; the direction is recorded as "
                "unknown.",
                "Each method is at one sampling setting, so its diversity is whatever that setting "
                "gives.",
                "Printed inside Figure 14 as a labelled numeric matrix rather than in a numbered "
                "table."],
        data=None,
    ),
    "protocol-plddt-esmfold2": dict(
        name="pLDDT of ESMFold2 predictions of designed sequences",
        description="Record the structure predictor's own mean per-residue confidence in its "
                    "prediction for a designed sequence.",
        metric="plddt", direction="higher", unit="unitless",
        qualifier="ESMFold2 mean per-residue confidence over valid sites on a scale from 0 to 100, "
                  "averaged over the designs of a target and then over targets; from a second fold of "
                  "the same sequences with the confidence head on",
        implementation="Second ESMFold2 fold of the scored sequences with the confidence head on, "
                       "whose scTM agrees with the scoring run to 0.0003 on average over 69 cells.",
        aggregation="Designs of a target averaged first, then a macro-average over the chains.",
        locator="Figure 15, 'pLDDT' block; Appendix A 'Folding and seeds'; Appendix B 'pLDDT'",
        limits=["Appendix B states pLDDT comes from the same folder as scTM and is not compared "
                "across predictors; it is the predictor's confidence in itself, not a measurement of "
                "the design.",
                "Printed inside Figure 15 as a labelled numeric matrix rather than in a numbered "
                "table."],
        data=None,
    ),
    "protocol-scrmsd-esmfold2": dict(
        name="Self-consistency RMSD of designed sequences under ESMFold2",
        description="Measure the CA RMSD between the ESMFold2 prediction for a designed sequence and "
                    "the input backbone.",
        metric="scrmsd", direction="lower", unit="angstrom",
        qualifier="CA RMSD between the ESMFold2 prediction of a design and the native backbone at "
                  "valid sites after optimal Kabsch superposition with the residue correspondence "
                  "fixed by position, averaged over the designs of a target and then over targets",
        implementation="Kabsch superposition of predicted and native CA atoms at valid sites, "
                       "correspondence fixed by position. Same second fold as pLDDT.",
        aggregation="Designs of a target averaged first, then a macro-average over the chains.",
        locator="Figure 15, 'scRMSD' block; Appendix B 'scRMSD'",
        limits=[DIVERSITY_CAVEAT,
                "Printed inside Figure 15 as a labelled numeric matrix rather than in a numbered "
                "table."],
        data=None,
    ),
    "protocol-lddt-esmfold2": dict(
        name="CA-lDDT of designed sequences under ESMFold2",
        description="Measure a superposition-free distance-difference score between the ESMFold2 "
                    "prediction for a designed sequence and the input backbone.",
        metric="lddt", direction="higher", unit="unitless",
        qualifier="CA-only lDDT-style score without superposition, over all CA pairs below 15 "
                  "Angstrom in the native structure, as the fraction whose distance error is below "
                  "0.5, 1, 2 and 4 Angstrom averaged over the four thresholds with the pairs pooled "
                  "over the whole design; between 0 and 1",
        implementation="As defined in Appendix B 'lDDT'; computed on the same ESMFold2 predictions as "
                       "pLDDT and scRMSD.",
        aggregation="Designs of a target averaged first, then a macro-average over the chains.",
        locator="Figure 15, 'CA-lDDT' block; Appendix B 'lDDT'",
        limits=[DIVERSITY_CAVEAT,
                "A CA-only lDDT-style score with pooled pairs, not the standard all-atom lDDT, so it "
                "is not comparable with lDDT values from other sources.",
                "Printed inside Figure 15 as a labelled numeric matrix rather than in a numbered "
                "table."],
        data=None,
    ),
}

PROTOCOLS.update({
    "protocol-sctm-difference-esmfold2": dict(
        name="Paired scTM difference from HyInv under ESMFold2",
        description="Measure the per-chain scTM difference between HyInv's designs and a baseline's "
                    "on the same panel, averaged over chains with a bootstrap interval.",
        metric="sctm-difference", direction="higher", unit="unitless",
        qualifier="HyInv default minus the baseline, paired by chain on the same panel with shared "
                  "folding randomness, printed in units of 10^-3 scTM with a 95% percentile interval; "
                  "ESMFold2 as the structure predictor; the reference system is the HyInv default "
                  "setting",
        implementation=PAIRED,
        aggregation="Macro-average of the per-chain differences; 10,000 bootstrap resamples of the "
                    "resampling unit.",
        locator="Table 7, ESMFold2 columns; Appendix A 'Paired differences and intervals'; Figure 6a",
        limits=[DIVERSITY_CAVEAT,
                "The sign of every one of the 70 differences in Table 7 favours HyInv and 61 of 70 "
                "intervals exclude zero, but the comparison was designed and run by HyInv's authors.",
                "Intervals are not adjusted for multiple comparisons."],
        data=None,
    ),
    "protocol-sctm-difference-boltz2": dict(
        name="Paired scTM difference from HyInv under Boltz2",
        description="Measure the per-chain scTM difference between HyInv's designs and a baseline's "
                    "on RecentPDB folded by Boltz2.",
        metric="sctm-difference", direction="higher", unit="unitless",
        qualifier="HyInv default minus the baseline, paired by chain on RecentPDB with shared folding "
                  "randomness, printed in units of 10^-3 scTM with a 95% percentile interval; Boltz2 "
                  "as the structure predictor; the reference system is the HyInv default setting",
        implementation=PAIRED,
        aggregation="Macro-average of the per-chain differences over the 121 chains; 10,000 bootstrap "
                    "resamples, one cluster per target.",
        locator="Table 7, column 'RecentPDB, Boltz2'; Figure 6b",
        limits=[DIVERSITY_CAVEAT,
                "Boltz2 scores partly reflect resemblance to a natural family, because the alignment "
                "is built from the designed sequence."],
        data=f"{B}-data-recentpdb",
    ),
    "protocol-sctm-difference-protenix2": dict(
        name="Paired scTM difference from HyInv under Protenix2",
        description="Measure the per-chain scTM difference between HyInv's designs and a baseline's "
                    "on RecentPDB folded by Protenix2.",
        metric="sctm-difference", direction="higher", unit="unitless",
        qualifier="HyInv default minus the baseline, paired by chain on RecentPDB with shared folding "
                  "randomness, printed in units of 10^-3 scTM with a 95% percentile interval; "
                  "Protenix2 as the structure predictor; the reference system is the HyInv default "
                  "setting",
        implementation=PAIRED,
        aggregation="Macro-average of the per-chain differences over the 121 chains; 10,000 bootstrap "
                    "resamples, one cluster per target.",
        locator="Table 7, column 'RecentPDB, Protenix2'; Figure 6b",
        limits=[DIVERSITY_CAVEAT,
                "Protenix2 scores partly reflect resemblance to a natural family, because the "
                "alignment is built from the designed sequence."],
        data=f"{B}-data-recentpdb",
    ),
    "protocol-sctm-fixed-diversity-esmfold2": dict(
        name="scTM at fixed sequence diversity on the development panel",
        description="Read scTM from a method's own scTM-against-diversity curve at a stated diversity "
                    "level, so that settings are compared at equal diversity rather than at equal "
                    "temperature.",
        metric="sctm-at-fixed-diversity", direction="higher", unit="unitless",
        qualifier="scTM at development diversity D = 0.30, read from a least-squares quadratic fit of "
                  "scTM against design-set diversity over a rewrite-temperature grid, plain "
                  "single-temperature sampling, ESMFold2, development panel (CATH4.3 validation)",
        implementation=EQUAL_DIVERSITY + " The development read-out uses 2 designs per chain.",
        aggregation="Fitted value at the stated diversity of the panel macro-averaged curve.",
        locator="Section 5.4 'Reinforcement learning'; Figure 8a; Appendix A 'Scores at equal "
                "diversity'",
        limits=["Read on the development panel, which fixed the checkpoint and the sampler setting "
                "and monitored training, so it is not a held-out measurement.",
                "A fitted value, not a directly measured one; no interval is printed for the two "
                "levels in Section 5.4."],
        data=f"{B}-data-cath43-validation",
    ),
    "protocol-sctm-fixed-diversity-gain-vs-unmodified-sampler": dict(
        name="Gain in scTM at fixed diversity over the unmodified sampler",
        description="Measure how much a sampler setting raises scTM over the unmodified "
                    "single-temperature sampler of the same checkpoint when both are read at the same "
                    "diversity.",
        metric="sctm-at-fixed-diversity-difference", direction="higher", unit="unitless",
        qualifier="Setting minus the unmodified single-temperature sampler of the same checkpoint on "
                  "the same panel, both read at fixed diversity (D = 0.30 on the development panel, "
                  "0.32 on CATH4.3 test, 0.30 on RecentPDB), paired, with a 95% interval; ESMFold2; "
                  "checkpoint at update 288; the reference system is the unmodified sampler",
        implementation=EQUAL_DIVERSITY + " The gain of a setting is its S@D minus that of the "
                       "unmodified sampler of the same checkpoint on the same panel, with an interval "
                       "from 1,000 draws in which all points of all curves are recomputed from one "
                       "cluster resample. Grids: {0.3, 0.4, 0.5, 0.7} for the unmodified sampler, "
                       "{0.1, 0.2, 0.3, 0.5} for the decoupled sampler at Td = 0.6 and {0.3, 0.4, "
                       "0.5, 0.7} at Td = 0.3. On the held-out panels D is the development value times "
                       "the ratio of the panel to the development diversity of the unmodified sampler. "
                       "Development chains K = 2, held-out panels K = 4 with new draws and fold seeds.",
        aggregation="Difference of fitted values, paired; 95% percentile interval over CATH topology "
                    "clusters, over chains on RecentPDB.",
        locator="Table 8; Appendix E 'Confirmation of the decoupled draft'; Appendix A 'Scores at "
                "equal diversity'",
        limits=["Measured on the checkpoint at update 288, not on the released update-640 checkpoint.",
                "The draft temperature was chosen on the development panel, so the report treats the "
                "held-out confirmation on CATH4.3 test and RecentPDB as the evidence for the gain.",
                "This compares two settings of HyInv itself; it says nothing about any baseline."],
        data=None,
    ),
    "protocol-sctm-fixed-diversity-bf16-minus-reference": dict(
        name="BF16 path minus reference sampler in scTM at fixed diversity",
        description="Check whether the BF16 inference path changes the quality of the design "
                    "distribution, by reading both paths at the same diversity on the development "
                    "panel.",
        metric="sctm-at-fixed-diversity-difference", direction="higher", unit="unitless",
        qualifier="BF16 path minus the FP32 reference sampler at development diversity D = 0.30, "
                  "four-point quadratic fit, paired by chain, with a 95% interval; ESMFold2, 2 designs "
                  "per chain, draft temperature 0.6; checkpoint at update 288; the reference system is "
                  "the FP32 reference sampler",
        implementation="S@D of the development read-out (scTM at diversity 0.30 from a quadratic fit "
                       "through four rewrite temperatures, ESMFold2, 2 designs per chain, draft "
                       "temperature 0.6) on the RL checkpoint at update 288, differenced and paired by "
                       "chain. The report fixed a margin of -0.002 for the lower end of the interval "
                       "before the check.",
        aggregation="Difference of fitted values, paired by chain; 95% percentile interval over CATH "
                    "topology clusters.",
        locator="Table 9; Appendix F 'Quality of the BF16 path'",
        limits=["The report states the check covers the development panel, ESMFold2, 2 designs and "
                "rewrite temperatures up to 0.5 only: test panels, the independent predictors and "
                "other checkpoints are not covered by it.",
                "Measured at update 288 and not repeated at the released update 640.",
                "Two of the four rows have a lower interval end below the fixed -0.002 margin, which "
                "the report attributes to subsets of about five hundred chains being unable to "
                "resolve a difference of that size."],
        data=None,
    ),
    "protocol-sctm-fixed-diversity-vs-proteinmpnn-curve": dict(
        name="HyInv above the ProteinMPNN temperature curve at HyInv's diversity",
        description="Compare HyInv with ProteinMPNN at equal diversity by reading ProteinMPNN's "
                    "temperature curve at the diversity HyInv samples at.",
        metric="sctm-at-fixed-diversity-difference", direction="higher", unit="unitless",
        qualifier="HyInv default minus the quadratic fit through ProteinMPNN's three temperatures "
                  "read at the HyInv diversity, with a 95% interval over clusters; ESMFold2; the "
                  "reference system is ProteinMPNN over its temperature grid",
        implementation="Figure 16 places every method in the scTM-diversity plane of each panel. "
                       "ProteinMPNN is the only baseline with a temperature sweep (three "
                       "temperatures, two of which were generated for this report). The quadratic fit "
                       "through its three points is read at the HyInv diversity.",
        aggregation="Difference of the HyInv point and the fitted ProteinMPNN curve; 95% intervals "
                    "over clusters.",
        locator="Appendix D.3 'scTM against diversity'; Figure 16",
        limits=["ProteinMPNN is the only baseline with a temperature grid, so this equal-diversity "
                "reading exists for ProteinMPNN alone and cannot be extended to the other nine "
                "baselines.",
                "Two of ProteinMPNN's three temperatures were generated for this report rather than "
                "taken from its published setting.",
                "Only CATH4.3 test and RecentPDB are reported; the per-temperature points themselves "
                "are printed only in Figure 16."],
        data=None,
    ),
    "protocol-sctm-fixed-diversity-gain-vs-supervised-checkpoint": dict(
        name="Gain in scTM at fixed diversity from reinforcement learning",
        description="Measure how much structure-reward reinforcement learning raises scTM over the "
                    "supervised checkpoint when both are read at the same diversity.",
        metric="sctm-at-fixed-diversity-difference", direction="higher", unit="unitless",
        qualifier="Update-640 checkpoint minus the supervised checkpoint at development diversity "
                  "D = 0.30, plain single-temperature sampling, ESMFold2, development panel; the "
                  "reference system is the supervised checkpoint",
        implementation=EQUAL_DIVERSITY + " Read with plain sampling on the development panel for the "
                       "supervised checkpoint and for update 640.",
        aggregation="Difference of fitted values at the stated diversity.",
        locator="Section 5.4 'Reinforcement learning'; Figure 8a; Figure 13b",
        limits=["Read on the development panel, which monitored the same training run, so it is not "
                "a held-out measurement.",
                "The printed difference (+0.0133) is the difference of two values printed to three "
                "decimal places (0.839 and 0.852); no interval is printed in Section 5.4."],
        data=f"{B}-data-cath43-validation",
    ),
    "protocol-design-latency-h20": dict(
        name="Latency of a design request on one NVIDIA H20",
        description="Time how long a system takes to design a stated number of sequences for one "
                    "backbone on a single GPU.",
        metric="runtime", direction="lower", unit="millisecond",
        qualifier="Median wall-clock time of one design request on one NVIDIA H20, 128 candidates per "
                  "request with a maximum candidate batch of 32 unless the request is the "
                  "10,000-design library; the timed region excludes model loading, CUDA graph capture "
                  "and kernel compilation; the backbone length is named per result",
        implementation="PyTorch 2.7.1, CUDA 12.9, TF32 for matrix products off unless stated, on one "
                       "NVIDIA H20 of a node on which nothing else ran. The timed region starts at "
                       "host arrays and ends at the sampled tokens on the device: upload, backbone "
                       "batch, encoder and structure terms and all 16 decoder passes of every "
                       "candidate batch, but not model loading, graph capture or kernel compilation "
                       "(first call 67.7 ms to 834 ms per shape bucket). Every call draws fresh seeds "
                       "and nothing is cached across calls. HyInv rows were timed with the "
                       "supervised-stage weights and a rewrite temperature of 0.23. Baselines ran "
                       "with their released implementations in FP32 without graph capture or "
                       "compilation, DPLM-2 3B in BF16 autocast, each at its published setting.",
        aggregation="Median of 11 repeats (headline cells), 7 (sweeps) or 3 (slow systems of the "
                    "library cells) after 3 warm-up calls; the interquartile range is below 1% of the "
                    "median in every ladder row.",
        locator="Table 1; Figure 4a; Appendix F 'Timing protocol' and 'Baseline timings'",
        limits=["Appendix F states that where a released adapter handles one structure per call, 128 "
                "designs are 128 calls, so a batched reimplementation of the baseline would be "
                "faster; the measured times are of those released implementations and not of the best "
                "achievable speed of the baseline models.",
                "HyInv's rows were timed with the supervised-stage weights and a rewrite temperature "
                "of 0.23, not with the released checkpoint at its default temperatures.",
                "DPLM-2 3B decodes by argmax, so every call returns the same sequence and its time is "
                "that of producing 128 designs scaled from eight timed calls.",
                "One GPU model (NVIDIA H20, Hopper class) on one node; no other hardware was timed.",
                "Compilation and CUDA graph capture are excluded from the timed region, so a first "
                "call in practice costs more than the printed figure."],
        data=f"{B}-data-latency-backbones",
    ),
    "protocol-design-speedup-vs-proteinmpnn-h20": dict(
        name="Speed-up of a design request over ProteinMPNN on one NVIDIA H20",
        description="Express a system's design-request time as the ratio of ProteinMPNN's time to its "
                    "own under the report's timing protocol.",
        metric="speedup", direction="higher", unit="unitless",
        qualifier="Printed speed-up against the released ProteinMPNN implementation under the "
                  "report's timing protocol on one NVIDIA H20; ProteinMPNN's own cell is printed as a "
                  "dash, so the baseline has no value",
        implementation="Ratio of ProteinMPNN's time to the system's time for the same request under "
                       "the timing protocol of Appendix F. The report does not state which of the "
                       "three printed request sizes the single printed ratio is taken from.",
        aggregation="One printed ratio per system.",
        locator="Table 1, column 'Speed-up vs ProteinMPNN'",
        limits=["The comparison is against ProteinMPNN's released implementation, run unbatched where "
                "its adapter handles one structure per call, and not against an equally optimised "
                "baseline. Appendix F says so explicitly.",
                "Compilation and CUDA graph capture are excluded from HyInv's timed region but the "
                "baseline needs neither, so the ratio favours the optimised path.",
                "The report does not state which request size the printed ratio uses; the ratio of "
                "the printed 402-residue times (2,907/50.6 = 57.5) matches the 57x row and "
                "2,907/2,633 = 1.10 matches the 1.1x row, but this was not stated by the authors and "
                "is not recorded as a value here."],
        data=f"{B}-data-latency-backbones",
    ),
    "protocol-novel-and-foldable-yield": dict(
        name="Novel and foldable designs per de novo backbone at matched diversity",
        description="Count how many of the designs made for a de novo backbone are both foldable by "
                    "the structure predictor and distant from known natural sequences.",
        metric="count", direction="higher", unit="count",
        qualifier="Number of designs per backbone (of 4) that are both foldable (ESMFold2 scTM at "
                  "least 0.9) and novel (sequence identity below 0.3 to the nearest UniRef50 sequence "
                  "and to the nearest sequence of the pretraining library), at matched diversity; two "
                  "readings, with and without the report's composition filter",
        implementation="74 de novo backbones, 4 designs each. A design is foldable if its ESMFold2 "
                       "scTM is at least 0.9 and novel if its identity to the nearest UniRef50 "
                       "sequence and to the nearest pretraining-library sequence is below 0.3. The "
                       "composition filter keeps sequences with entropy at least 3.5 bits, hydrophobic "
                       "fraction (AVILMFWY) between 0.25 and 0.55 and longest homopolymer run at most "
                       "6, which excludes low-complexity sequences a structure predictor can fold to "
                       "a high scTM. Both readings were fixed before designs were generated. HyInv is "
                       "compared with ProteinMPNN and ProteinZero V2 over their temperature grids, "
                       "interpolating each curve at the HyInv diversity without extrapolating by more "
                       "than 0.05.",
        aggregation="Mean number of qualifying designs per backbone over the 74 backbones; the "
                    "resampling unit is the cluster of 30% identity.",
        locator="Section 6 'De novo backbones'; Appendix G 'De novo backbones'; Figure 9b",
        limits=["Baseline values are interpolated at the HyInv diversity from a temperature grid, not "
                "measured at a single published setting, so they are not the same kind of number as "
                "the Table 6 baseline cells.",
                "Novelty is sequence identity to UniRef50 and to the pretraining library, not an "
                "experimental test; foldability is an ESMFold2 score, and ESMFold2 is HyInv's reward "
                "predictor.",
                "Table 10 records that 28 of the 74 backbones have partial homology hits below the "
                "coverage limit.",
                "With 74 backbones in 58 clusters, Appendix G notes the intervals are wide; no "
                "interval is printed for these six values."],
        data=f"{B}-data-de-novo-backbones",
    ),
})


def protocols():
    out = []
    for slug, spec in PROTOCOLS.items():
        attributes = {
            "metric": spec["metric"],
            "metric_direction": spec["direction"],
            "unit": spec["unit"],
            "metric_qualifier": spec["qualifier"],
            "metric_implementation": spec["implementation"],
            "aggregation": spec["aggregation"],
            "protocol": spec["description"],
            "version": "HyInv technical report, 2026-10-14",
            "source_locator": spec["locator"],
            "limitations": spec["limits"],
            "publication_status": "official_project_source",
        }
        links = [{"relation": "part_of", "target_id": BENCHMARK}]
        if spec["data"]:
            links.append({"relation": "uses_data", "target_id": spec["data"]})
        out.append(
            record(
                f"{B}-{slug}",
                "protocol",
                f"{spec['name']} (HyInv report)",
                spec["description"],
                attributes,
                links=links,
                sources=[SRC_REPORT],
            )
        )
    return out


def entities():
    return sources() + models() + configurations() + benchmark() + datasets() \
        + dataset_subsets() + protocols()
