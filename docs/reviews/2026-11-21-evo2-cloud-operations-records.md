# Evo 2 cloud operations: Rewire-run records, 2026-11-21

Reviewer: Claude agent, automated. The same agent wrote the generator and ran the checks. There was no independent second pass and no human review. Nothing was rerun and no GPU or paid run was made.

Batch: `data/omics/rewire-evo2-cloud-operations-20261121/` (90 records). Notes and the list of what was left out are in its `notes.md`.

## Source

`rewire-bio/evo2-cloud-operations` at commit `f8ae11c9a1c45505487c978b4cb7e064c4e59905` (public). One source record per file. Each file was downloaded again from its raw URL on 2026-11-21 and hashes to the recorded SHA-256:

| Source record | File | SHA-256 |
| --- | --- | --- |
| `rewire-local-20261121-evo2ops-source-results` | `evidence/runs/recorded-b75c67aa/results.json` | `2c1b5eabcb0e84f2e73f01c55184fe756a340e764fbaffd2bcd133ebca3fe044` |
| `rewire-local-20261121-evo2ops-source-operations` | `evidence/runs/recorded-b75c67aa/operations.json` | `12d03225c4933b1aa4c5ffe7012ce83b12a47409fb7de319f3b896f77e3d2e1f` |
| `rewire-local-20261121-evo2ops-receipt-gcp-h100` | `evidence/runs/recorded-b75c67aa/platforms/P2/attempt-1/receipt-main.json` | `9ed23981f6ab253fad808f84b02fdddc9664fbc15563df41364bf10ad9ee55a6` |
| `rewire-local-20261121-evo2ops-receipt-runpod-h100` | `evidence/runs/recorded-b75c67aa/platforms/P3/attempt-1/receipt-main.json` | `4bfe70c67740043bef2f383beade8bdb09696f88a4c673c1194520b354e7ff30` |
| `rewire-local-20261121-evo2ops-receipt-runpod-l40s` | `evidence/runs/recorded-b75c67aa/platforms/P5/attempt-2/receipt-main.json` | `d26432852833b76a63d4b91024cbe2c7a07a670dd5bbbcca2977f2139975a1eb` |
| `rewire-local-20261121-evo2ops-source-current-predictors` | `evidence/current-predictors/results.json` | `403437941f5a0e08b3730fa7bbfcba0b8e616b0e87b2f8e3f227b2f86a342318` |
| `rewire-local-20261121-evo2ops-source-protocol` | `protocol.md` | `e24ab6967b409dcf8663b5b9d8917b85ba91146987089240206dfa737b25e2f7` |
| `rewire-local-20261121-evo2ops-source-amendment-7` | `protocol/amendments/007-current-predictors.md` | `ddaa89b7ed8a4660221b08f49bfba708ce519ae36a7ab8fa58ea2b9ea4f2590e` |
| `rewire-local-20261121-evo2ops-source-readme` | `README.md` | `a5beed84f477a15b8682ee8e8a4903de75d28b5b3292f2ad89f18fd06b7068ca` |

## How values were checked

`extract/build_batch.py evo2ops <checkout> <batch folder>` builds the batch from a checkout at the pinned commit and refuses any other commit. It reads JSON with floats kept as strings, so each `printed_value` is the literal number token in the file. Each result's `source_locator` is the file path and the JSON pointer. After building, the script reads every pointer again and compares the token and the interval bounds with the record. `--check` rebuilds in memory and compares with the stored `batch.jsonl` byte for byte.

The script asserts: 9 sources, 1 benchmark, 4 subsets, 5 protocols, 9 configurations, 31 evaluations and 31 results; 12 `reproduced` and 19 `source_checked`; the attempt used per platform (P2 attempt 1, P3 attempt 1, P5 attempt 2, from `operations.json`); that each receipt has status `completed`, its own platform ID and 3,893 variants scored; that the P2 AUROC is the same at both pointers that hold it; that no CADD v1.7, SpliceAI or missense REVEL score is missing; that amendment 7 states the version and origin of each lookup score; that every source is cited by a record; and that a result is `reproduced` exactly when it cites one receipt, with its evaluation carrying the same status and sources.

`npm run batch -- check-values` was not run. It parses table and row locators and cannot read a JSON pointer.

## Status rulings

- `reproduced`, 12 results and their 12 evaluations: Evo 2 7B AUROC on the all, coding and noncoding subsets for each platform, and W1 throughput for each platform. Each cites its own platform's `receipt-main.json` and no other receipt. Each protocol holding them carries a run recipe whose executed instruction names that receipt as a `full_protocol` validation receipt.
- `source_checked`, 19 results: CADD v1.3, phyloP, the consequence rule, CADD v1.7, SpliceAI and REVEL (lookup scores, no GPU run, no receipt), and the Evo 2 7B missense AUROC. The missense analysis is amendment 7, run after the recorded run on the committed P2 scores (`followup/current_predictors.py` lines 115 and 116). No receipt covers that analysis, so it is not marked `reproduced` and its protocol has no run recipe.
- The receipt covers the GPU run. AUROC is computed afterwards from the committed scores by `scripts/analyse.py`. The recipe's limitations say so.
- The runs are the project's own. `reproduced` does not claim that a published score was reproduced.

## Checks

- `npm run records -- add` accepted the batch and the SHACL check of the 90 records and their 5 link targets passed.
- `npm run records -- check`: 93,307 records match their provenance.
- `npm run check:task-links`: passes. Each new protocol is `part_of` the new benchmark.
- `npm run checks -- report` before and after the add: every rule count is unchanged and equals `data/omics/checks-baseline.json`.

- `npm run depth-tier -- check`: 0 records differ from the rule, so tier 1 on the new benchmark matches it.
- Not run: `npm run archive -- fetch`. The nine sources have no archive object yet. The fetch writes rows that name a local cache as the home of the bytes, and this pass ran in a clone that was deleted afterwards.

## Use-case judgements needed

No use case links to these protocols and no judgement was written in this pass. To put these results on a use-case page, a judgement is needed for each pair below. Relevance is for the judgement to decide.

| Use case | Protocols |
| --- | --- |
| `use-case-brca1-brca2-germline-interpretation` | `rewire-local-20261121-evo2ops-protocol-brca1-all-auroc`, `-coding-auroc`, `-noncoding-auroc`, `-missense-auroc` |
| `use-case-missense-pp3-bp4-calibrated-evidence` | `rewire-local-20261121-evo2ops-protocol-brca1-missense-auroc` |
| `use-case-diagnostic-genomics-model-execution` | `rewire-local-20261121-evo2ops-protocol-brca1-scoring-throughput` |

## Gaps

Listed in the batch `notes.md` under "Not ingested": the other workloads, cross-platform agreement, classification flips, the follow-up and reproduction runs with their receipts, costs, and `evo2-size-by-use-case`, which has no result file.
