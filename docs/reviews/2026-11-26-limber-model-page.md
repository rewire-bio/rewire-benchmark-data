# LIMBER model page, 2026-11-26

Prepared by a Claude agent. No human review is claimed, and the writer and reviewer were the same agent.

## What changed

`intake-384-20261124-model-limber` gains a `profile` and a `run_guide`. Its `missing_metadata.licence` reason moves from `unextracted` to `unreported`, because the repository and the model card were read and neither states a licence. No result, evaluation or claim was added.

Model and method records may now carry a `run_guide` (`shared/omics/attribute-registry.ts`, `shared/omics/run-guide.ts`). Until now only benchmarks, tasks, protocols and evaluators could, so no model page could say how to run the model.

## Sources

The three source records the intake run pinned on 2026-11-24 are cited. The README was last pushed on 2026-11-05, so the text read on 2026-11-26 at commit `72a328a` is the text the stored GitHub source was fetched from. The Hugging Face repository was read at revision `d2d6ae6`.

## How statements were checked

Each fact, section and run step was written from the fetched README, the repository root listing, the Hugging Face file listing or `LIMBER-macro/model_config.json`, and names the section it came from. Parameter counts, layer counts and hidden sizes are the Model zoo table's. The context limit is the README's (1,022 nucleotides) and agrees with `max_position_embeddings` of 1,026 in the config.

## Rulings

- **Licence.** Recorded as unreported for both code and weights. The preprint's own licence is not a code or weights licence.
- **Run guide status.** `source_reviewed_not_executed`. The quick start needs a CUDA device and GPU work is parked.
- **Author-reported results.** The README prints result tables. They are described in the profile and not added as results in this change.

## Gaps

- The preprint was not read in full.
- Inference hardware is not stated by the authors.
