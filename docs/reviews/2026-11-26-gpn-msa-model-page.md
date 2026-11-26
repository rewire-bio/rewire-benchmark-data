# GPN-MSA model page, 2026-11-26

Prepared by a Claude agent. No human review is claimed, and the writer and reviewer were the same agent.

## What changed

`gfm-guides-20261014-gpnmsa-model-gpn-msa` gains a `profile` and a `run_guide`, and cites four new source records. The model holds 381 results directly or through its configurations and its page showed no description of the model beyond one sentence.

No result, evaluation or claim was added or changed. The record's existing `licence` attribute still reads "Checkpoint licence not checked"; the profile now records the weights licence as MIT from the model card. Correcting the attribute needs a claim record that keeps the old value and is left for a separate change.

## Sources

| Source | File | SHA-256 |
| --- | --- | --- |
| `model-pages-20261126-gpn-msa-source-hf-model-card` | model card at Hugging Face revision `4a7d4f75` | `a572bab27004f238bb1b8e3e59eeacc64a0ff4acd73013cd67a4fd4eff06d353` |
| `model-pages-20261126-gpn-msa-source-hf-config` | `config.json` at the same revision | `6f557f8ab4dc61dec763331e7e35bf0aa8f140ef2a51c280099994c84f8af1f2` |
| `model-pages-20261126-gpn-msa-source-hf-api` | Hugging Face API response, as served on 2026-11-26 | `0484189dbb7c871f7b7070e498b33335365767e86ade4001418f0f480633f0a1` |
| `model-pages-20261126-gpn-msa-source-gpn-cli` | `docs/getting-started/cli.md` at commit `dc5fd287` | `0e39259e5c69b9bdb033889f5ea9bbae943698d7a033335b0ef31d3ce9dda730` |

The fetched bytes are kept in `artifacts/`. The repository README and `docs/models/gpn-msa.md` were fetched again at commit `dc5fd287` and match the hashes already stored (`0312fb96...`, `8076d5e5...`). The API response is not a pinned file and may change; it is the source of the parameter count and the gating status.

## How statements were checked

Each fact, section and run step was written from the fetched text and names the file and section. The architecture figures are `config.json` fields. The parameter count is `safetensors.total` in the API response. The description of the score is the command-line guide's.

## Rulings

- **Deprecation.** The repository says GPN-MSA is deprecated in favour of GPN-Star. The profile states this in the summary and as a limitation.
- **Window size.** The command-line guide takes a window size and the documentation read does not give one for this checkpoint. The run guide leaves it as a placeholder and says so. The `Context limits` fact has status `unextracted`.
- **Run guide status.** `source_reviewed_not_executed`.

## Gaps

- The paper was not re-read. Training window, training cutoff and inference hardware are not recorded.
