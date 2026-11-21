# Evo 2 cloud operations: Rewire-run records, 2026-11-21

Reviewer: Claude agent, automated. One agent wrote the generator and ran the checks. A second automated pass then reviewed the draft and found the two faults listed under "Status rulings"; the batch was rebuilt to fix them before it reached main. There was no human review. Nothing was rerun and no GPU or paid run was made.

Batch: `data/omics/rewire-evo2-cloud-operations-20261121/` (92 records). Notes and the list of what was left out are in its `notes.md`.

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
| `rewire-local-20261121-evo2ops-source-run-log` | `evidence/run-log.md` | `9b42944eb2c1c7afeeb295f725bf1945ad8470f355b6a2e21531348c3f56e0e0` |
| `rewire-local-20261121-evo2ops-receipt-reproduction-runpod-l40s` | `evidence/runs/reproduction-30e7ae49/platforms/P5/attempt-1/receipt-main.json` | `60f60324a7cda6b66b370ea2569e71175f66a1baf64455d17b6a65813df02fd8` |

## How values were checked

`extract/build_batch.py evo2ops <checkout> <batch folder>` builds the batch from a checkout at the pinned commit and refuses any other commit. It reads JSON with floats kept as strings, so each `printed_value` is the literal number token in the file. Each result's `source_locator` is the file path and the JSON pointer. After building, the script reads every pointer again and compares the token and the interval bounds with the record. `--check` rebuilds in memory and compares with the stored `batch.jsonl` byte for byte.

The script asserts: 11 sources, 1 benchmark, 4 subsets, 5 protocols, 9 configurations, 31 evaluations and 31 results; every record `source_checked` and none with a run recipe; that no receipt of the recorded run contains the word AUROC; that the L40S throughput is 0.6117 in the recorded receipt and 0.9081 in the reproduction receipt for the same GPU model, sequence count and variant count; that the run log has the sentence about the slower L40S host; that the recorded run's revision is `e93491a`; the attempt used per platform (P2 attempt 1, P3 attempt 1, P5 attempt 2, from `operations.json`); that each receipt has status `completed`, its own platform ID and 3,893 variants scored; that the P2 AUROC is the same at both pointers that hold it; that no CADD v1.7, SpliceAI or missense REVEL score is missing; that amendment 7 states the version and origin of each lookup score; that every source is cited by a record; that a result cites a receipt exactly when its value is read from that receipt; and that the reproduction receipt is cited by the L40S throughput result alone, with 0.9081 in its limitations.

`npm run batch -- check-values` was not run. It parses table and row locators and cannot read a JSON pointer.

## Status rulings

All 92 records are `source_checked`. None is `reproduced`, no protocol carries a run recipe and no evaluation has a `reproduction` attribute.

The first draft marked 12 results and evaluations `reproduced` and gave three AUROC protocols (all, coding and noncoding SNVs) and the throughput protocol a run recipe whose executed instructions named the three receipts. The second pass found:

1. **The receipts do not hold or bind the AUROC.** `receipt-main.json` holds W0 to W3 counts, timings and throughput. It has no AUROC and no hash of `w1_brca1_scores.tsv`. AUROC is computed off the machine into `results.json`. The nine Evo 2 7B AUROC results now cite `results.json` and no receipt.
2. **The Runpod L40S throughput was not repeated.** The stored value is 0.6117 sequences per second (`platforms/P5/attempt-2/receipt-main.json`, `/results/w1/sequences_per_second`). The study's reproduction run measured 0.9081 on an NVIDIA L40S for the same 5,219 sequences and 3,893 variants (`evidence/runs/reproduction-30e7ae49/platforms/P5/attempt-1/receipt-main.json`). `evidence/run-log.md` says the recorded attempt ran "on a slower L40S host (0.61 windows per second, against 0.93 on the host used earlier the same day)". The result, its evaluation and the throughput protocol now state both figures in `limitations` and cite both files.

Why the recipes were removed and not only the status changed: the board's "Reproduced" badge does not read `status`. It is given to any result that cites, or whose evaluation cites, the validation receipt of an executed `full_protocol` recipe instruction (`run_receipts` in `scripts/kg/release_graph.py`, used by `scripts/kg/product_queries.py`). The L40S throughput exists only in its receipt, so the result must cite it. While any recipe named that receipt, the badge would stay. Removing the recipes also removes two smaller faults: the instruction code was the README block with one platform filled in, which is not the command the recorded run used, and the recipe said "at the pinned commit" although the run was made at `e93491a`.

This matches the store. On main, 14 of 18 `rewire_run` evaluations are `source_checked`, complete runs among them. The `reproduced` ones are MFASS evaluations with a `reproduction` attribute, and the one receipt citation was accepted after comparing the receipt's own metrics with the stored values (`docs/reviews/2026-11-21-mfass-receipt-citation.md`).

Open for the owner: reproduction run 30e7ae49 does repeat all nine Evo 2 7B AUROCs exactly (`/platforms/P2|P3|P5/w1_auroc` is equal in both `results.json` files, and the two Runpod L40S `w1_brca1_scores.tsv` files are byte-identical). If `reproduced` should cover that, ingest the reproduction run as a second source set and move those nine records with `records -- change`. This batch does not make that call.

`tests/omics-run-receipt-badge.test.ts` holds these rulings: no record of the batch is `reproduced` or carries a recipe, no result of the batch can get the badge, a receipt is cited only by a result whose value is read from it, and the L40S throughput states both figures. It also checks, for the whole store, that the badge never lands on a result whose status is not `reproduced`.

## Checks

- `npm run records -- add` accepted the batch and the SHACL check of the 92 records and their 5 link targets passed.
- `npm run records -- check`: 93,309 records match their provenance.
- `npm run check:task-links`: passes. Each new protocol is `part_of` the new benchmark.
- `tests/checks-baseline.test.ts` passes after the add: every rule count equals `data/omics/checks-baseline.json`, which is untouched.
- `tests/omics-run-receipt-badge.test.ts` passes.
- `npm run depth-tier -- check`: 0 records differ from the rule, so tier 1 on the new benchmark matches it.
- Not run: `npm run archive -- fetch`. The eleven sources have no archive object yet. The fetch writes rows that name a local cache as the home of the bytes, and this pass ran in a clone that was deleted afterwards.

## Use-case judgements needed

No use case links to these protocols and no judgement was written in this pass. To put these results on a use-case page, a judgement is needed for each pair below. Relevance is for the judgement to decide.

| Use case | Protocols |
| --- | --- |
| `use-case-brca1-brca2-germline-interpretation` | `rewire-local-20261121-evo2ops-protocol-brca1-all-auroc`, `-coding-auroc`, `-noncoding-auroc`, `-missense-auroc` |
| `use-case-missense-pp3-bp4-calibrated-evidence` | `rewire-local-20261121-evo2ops-protocol-brca1-missense-auroc` |
| `use-case-diagnostic-genomics-model-execution` | `rewire-local-20261121-evo2ops-protocol-brca1-scoring-throughput` |

## Gaps

Listed in the batch `notes.md` under "Not ingested": the other workloads, cross-platform agreement, classification flips, the follow-up runs, the results of the reproduction run, costs, and `evo2-size-by-use-case`, which has no result file.
