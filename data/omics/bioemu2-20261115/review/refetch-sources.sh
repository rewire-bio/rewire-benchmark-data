#!/bin/bash
# Re-retrieve the thirteen pinned BioEmu-2 artifacts into a directory and print their SHA-256,
# for comparison with each source record's artifact_sha256 and with the archives in artifacts/.
#
#   bash data/omics/bioemu2-20261115/review/refetch-sources.sh <empty-output-dir>
set -euo pipefail
OUT=${1:?output directory}
mkdir -p "$OUT"
C=6d1ca744fa8ed285edafae7b98da65205bf00fd3
R=dd4b0c1b69984b68edcb6200a544213be4d75242
RAW=https://raw.githubusercontent.com/microsoft/bioemu2/$C
HF=https://huggingface.co/microsoft/bioemu2/raw/$R
curl -sS -f -o "$OUT/repo_MODEL_CARD.md" "$RAW/MODEL_CARD.md"
curl -sS -f -o "$OUT/repo_README.md" "$RAW/README.md"
curl -sS -f -o "$OUT/repo_NOTICES.md" "$RAW/NOTICES.md"
curl -sS -f -o "$OUT/repo_LICENSE" "$RAW/LICENSE"
curl -sS -f -o "$OUT/repo_pyproject.toml" "$RAW/pyproject.toml"
curl -sS -f -o "$OUT/repo_docs_checkpoints.md" "$RAW/docs/checkpoints.md"
curl -sS -f -o "$OUT/repo_docs_sampling.md" "$RAW/docs/sampling.md"
curl -sS -f -o "$OUT/repo_docs_context-parallel-sampling.md" "$RAW/docs/context-parallel-sampling.md"
curl -sS -f -o "$OUT/repo_docs_propagation.md" "$RAW/docs/propagation.md"
curl -sS -f -o "$OUT/hf_README.md" "$HF/README.md"
curl -sS -f -o "$OUT/hf_config.yaml" "$HF/checkpoints/bioemu2-preview/config.yaml"
curl -sS -f -o "$OUT/hf_checkpoint_pointer.txt" "$HF/checkpoints/bioemu2-preview/checkpoint.ckpt"
# The API listing carries mutable counters, so its hash describes one retrieval.
curl -sS -f -o "$OUT/hf_api_revision.json" "https://huggingface.co/api/models/microsoft/bioemu2/revision/$R?blobs=true"
shasum -a 256 "$OUT"/*
