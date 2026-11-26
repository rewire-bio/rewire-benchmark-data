#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${PROJECT_ROOT}"
PYTHON_BIN="${LNCRFM_PYTHON:-python}"
export TOKENIZERS_PARALLELISM=false

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  exec "${PYTHON_BIN}" main.py --help
fi

args=(
  main.py
  --run_name "${RUN_NAME:-${PROJECT_ROOT}/outputs/pretraining}"
  --data_path "${DATA_PATH:-${LNCRFM_CORPUS_ROOT:-${PROJECT_ROOT}/LncCorpus/data}}"
  --max_length 2050
  --min_seq_len 200
  --max_seq_len 2048
  --motif_kernel_sizes 3 7
  --batch_size "${BATCH_SIZE:-20}"
  --gradient_accumulation_steps "${GRAD_ACCUM:-2}"
  --lr "${LR:-2e-6}"
  --warmup_steps "${WARMUP_STEPS:-1000}"
  --lr_scheduler_type linear
  --epoch "${EPOCH:-100}"
  --max_steps_override "${MAX_STEPS:-300000}"
  --step_interval_override "${SAVE_STEPS:-5000}"
)
if [[ "${ENABLE_EVAL:-0}" != "1" ]]; then
  args+=(--disable_eval)
fi

if [[ "${NPROC_PER_NODE:-1}" -gt 1 ]]; then
  exec "${PYTHON_BIN}" -m torch.distributed.run --standalone \
    --nproc_per_node "${NPROC_PER_NODE}" "${args[@]}" "$@"
fi
exec "${PYTHON_BIN}" "${args[@]}" "$@"
