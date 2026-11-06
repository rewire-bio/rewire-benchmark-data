"""The README, licence, attribution and checkpoint source records for HyCell."""

from sources import (SRC_CITATION, SRC_LICENSE, SRC_NOTICE, SRC_PYPROJECT, SRC_README,
                     SRC_SIDECAR, SRC_WEIGHTS, text_source)

T0, T1, T2 = "2026-11-06T11:42:11Z", "2026-11-06T11:45:18Z", "2026-11-06T11:45:37Z"
P = "AI4Science/hycell"


def sources2():
    return [
        text_source(SRC_README, "HyCell package README (Tencent Hunyuan, commit 0dcc533c)",
                    "README of the hycell package, with the recorded benchmark result, method "
                    "summary, installation, embedding, decoding, fine-tuning and input rules.",
                    f"{P}/README.md",
                    "cd2eb7ae932124cacf9875b0ed1c48504b3e95b8e36169520bd1fe83cc0eecde", T0,
                    "Apache-2.0 (repository LICENSE)", "text/markdown", "repository README",
                    {"archive_note": "Archived as artifacts/hycell-README.md.",
                     "limitations": ["Its results table is a six-model subset of Table 3 and its "
                                     "fine-tuning table repeats Table 5; both are asserted equal to "
                                     "the report and not recorded again. Its throughput figures "
                                     "(about 1,500 cells per second on an H20, about 13 on CPU) are "
                                     "approximate and appear only here."]}),
        text_source(SRC_LICENSE, "Hyra Results repository LICENSE (commit 0dcc533c)",
                    "Root licence file of the Hyra Results repository: Apache-2.0 for "
                    "Tencent-authored materials unless otherwise specified, followed by the "
                    "licences of listed third-party materials.",
                    "LICENSE", "9c9fa2250f057e2bd19c1353851977b49df26898f62e7dac914da577093bfa3b",
                    T0, "Apache-2.0", "text/plain", "licence file",
                    {"archive_note": "Archived as artifacts/repository-LICENSE.",
                     "scope_note": "Shared across the Hyra batches, so its ID is not HyCell-specific. "
                                   "Opens: 'Unless otherwise specified, all Tencent-authored materials "
                                   "in this repository are licensed under the Apache License, Version "
                                   "2.0.' Its third-party section lists SOL-ExecBench and several MIT "
                                   "items and does not mention HyCell or CELLxGENE. HyInv and "
                                   "HyPLM-Flash ship their own MIT LICENSE files, which is the "
                                   "'otherwise specified' case; HyCell ships none."}),
        text_source(SRC_NOTICE, "HyCell NOTICE (commit 0dcc533c)",
                    "Attribution notice of the hycell package, naming the third-party data the "
                    "weights were trained on and the test cells come from.",
                    f"{P}/NOTICE", "66cfe5d9272cf9964594444a7f81a5cf355ca25336ce9698bd6c1ca1f5fb392a",
                    T0, "Apache-2.0 (repository LICENSE); third-party data under CC BY 4.0",
                    "text/plain", "attribution notice",
                    {"archive_note": "Archived as artifacts/hycell-NOTICE."}),
        text_source(SRC_CITATION, "HyCell CITATION.cff (commit 0dcc533c)",
                    "Citation metadata of the hycell package.",
                    f"{P}/CITATION.cff",
                    "fa5e4edb1f9a8310184d74345e3e1361feeeaadbf20a454fa5855cfe15a57641", T0,
                    "Apache-2.0", "application/x-yaml", "citation metadata",
                    {"archive_note": "Archived as artifacts/hycell-CITATION.cff.",
                     "scope_note": "Gives version 0.1.0, license Apache-2.0, author 'Hyra Team' and "
                                   "the technical report as the preferred citation."}),
        text_source(SRC_PYPROJECT, "HyCell pyproject.toml (commit 0dcc533c)",
                    "Package metadata of hycell, giving its name, version and licence.",
                    f"{P}/pyproject.toml",
                    "6a12a9e90aa834794fecfc447fb0e9849c36b8fe6b786737eaac64c419c3ab16", T1,
                    "Apache-2.0", "text/plain", "package metadata",
                    {"archive_note": "Archived as artifacts/hycell-pyproject.toml.",
                     "scope_note": "name 'hycell', version 0.1.0, license {text = 'Apache-2.0'}."}),
        text_source(SRC_SIDECAR, "HyCell checkpoint sidecar weights.json (commit 0dcc533c)",
                    "Metadata file shipped beside the HyCell weights, with the model configuration, "
                    "tokenizer settings, parameter count and the weights' SHA-256.",
                    f"{P}/src/hycell/checkpoints/hycell-16m/weights.json",
                    "b1c1d53badd8f688705bf77fb9de24b3f72e2f5ab071633a708c79d032cc3084", T1,
                    "Apache-2.0 (repository LICENSE)", "application/json", "checkpoint metadata",
                    {"archive_note": "Archived as artifacts/hycell-weights.json.",
                     "scope_note": "model_id hycell-16m, version 0.1.0, n_parameters 16,108,766, "
                                   "training_tokens 64,000,195,776, training_cells_seen 78,201,849, "
                                   "n_datasets 555, n_donors 12,533, weights_sha256 11197d80...d744."}),
        text_source(SRC_WEIGHTS, "HyCell weights hycell-16m weights.safetensors (commit 0dcc533c)",
                    "The released HyCell checkpoint, 64,439,816 bytes of FP32 safetensors shipped "
                    "inside the hycell package.",
                    f"{P}/src/hycell/checkpoints/hycell-16m/weights.safetensors",
                    "11197d805aa6bafd7a69996bf8e0c7cfd7706b4fbbf5466f9e350d5b3e79d744", T2,
                    "Apache-2.0 (repository LICENSE); trained on CZ CELLxGENE Census data under "
                    "CC BY 4.0", "application/octet-stream", "model weights",
                    {"archive_note": "Not archived: 64 MB of binary weights, refetchable at the "
                                     "pinned commit.",
                     "scope_note": "Downloaded and hashed for this batch. Its SHA-256 equals the "
                                   "weights_sha256 that the sidecar weights.json publishes, so the "
                                   "released checkpoint's identity is verified from the bytes."}),
    ]
