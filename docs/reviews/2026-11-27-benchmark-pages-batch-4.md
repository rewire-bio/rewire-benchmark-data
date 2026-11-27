# Benchmark pages, batch 4, 2026-11-27

Prepared by Claude agents. No human review is claimed. Two research agents fetched sources and wrote the content, two agents verified it, two applied their findings, and a separate session checked and applied the result.

## What changed

25 Tier 3 benchmark records gain a `profile`, and 19 of them a `run_guide`. These are every Tier 3 benchmark that had no page: single-cell, virtual screening, drug-target affinity, mass spectrometry and perturbation benchmarks. The new source records in `batch.jsonl` pin the files the content was written from. No result, evaluation, protocol or claim was added or changed, and no existing attribute was edited.

With this batch every benchmark record in the store has been through the page process. The ones without a page are listed in the reviews of batches 2 and 3, with the reason for each.

## How statements were checked

Every copied passage was confirmed present in its saved file by `scripts/enrich/check_spec.py`. Two verifier agents that had not written the content judged 858 statements and raised 37 findings (4.3%): 9 contradicted by a source, 22 that went partly beyond it and 6 with no support. All were applied, with further corrections where the same fault recurred, and the checker was run again. One verifier also confirmed that no email address appears in any page text.

The faults that would most mislead a reader comparing methods were a primary metric named differently from the one the saved scripts select on, a dataset counted in a task it is not scored in, a description of a selection step taken from a stale code comment when the code does something else, and several statements of a check or search that no saved file records. Each is corrected, and where code and comment or paper and code differ the page says so.

No page in this batch was read in full by the applying session before merge.

## Found in the sources themselves

Each is stated on the page concerned: figures and definitions that differ between a paper's abstract and its body, between a paper and its released code, between versions of a preprint, or between a README and the script it documents. They are leads, not conclusions, and no person has confirmed them.

## Sources

Every fetched file was kept, whatever its licence, and uploaded to the private archive bucket under the sha256 its source record pins. Two bioRxiv papers were read from the store's own archive, where they had been saved earlier, and their hashes match the existing source records.

## Structured facts

The content files in `specs/` carry a `structured` list: 105 entries, one per task or track. They are not written to the records in this change.

## Run guides

All have status `source_reviewed_not_executed`. None was run.

## Per benchmark

Notes for a later reader are in each content file under `specs/`.

| Record | Sources | Run guide | Structured entries |
| --- | --- | --- | --- |
| `lit-cells-networks-20261011-ye2026grn-benchmark-static-grn-fm` | 1 (1 stored in the repository) | no | 9 |
| `gfm-guides-20261014-kedzierska2025-benchmark-zero-shot-scfm` | 5 (4 stored in the repository) | yes | 5 |
| `hitdisc-20261022-benchmark-dekois2` | 3 (1 stored in the repository) | no | 2 |
| `lit-cells-networks-20261011-chen2026-benchmark-harmonised-sc-spatial-fm` | 5 (3 stored in the repository) | yes | 5 |
| `hitdisc-20261022-benchmark-cache3` | 1 (1 stored in the repository) | no | 3 |
| `lit-interactions-20261011-leakctl-benchmark-plabench` | 5 (5 stored in the repository) | yes | 9 |
| `lit-cells-networks-20261011-scmbench-benchmark-scmbench` | 5 (5 stored in the repository) | yes | 5 |
| `hycell-20261106-benchmark-held-out-atlases` | 3 (3 stored in the repository) | yes | 8 |
| `msalign-2026-molecular-retrieval` | 6 (3 stored in the repository) | yes | 4 |
| `bacformer-20261115-benchmark-bacbench` | 13 (13 stored in the repository) | yes | 5 |
| `lit-cells-networks-20261011-sun2026de-benchmark-de-classification` | 4 (1 stored in the repository) | yes | 5 |
| `hitdisc-20261022-benchmark-gpcrrecent` | 3 (2 stored in the repository) | no | 2 |
| `hitdisc-20261022-benchmark-litpcba` | 5 (1 stored in the repository) | no | 3 |
| `lit-interactions-20261011-plmdta-benchmark-davis-kiba-dta-deepdta-split` | 6 (0 stored in the repository) | yes | 2 |
| `ucc-research-benchmark-cppc` | 3 (0 stored in the repository) | yes | 6 |
| `dreams-2025-mist-canopus-retrieval` | 6 (6 stored in the repository) | yes | 2 |
| `perturbpfn-20261115-benchmark-sciplex-highest-dose` | 4 (0 stored in the repository) | yes | 1 |
| `perturbpfn-20261115-benchmark-genernib` | 7 (4 stored in the repository) | yes | 2 |
| `gfm-guides-20261014-kendiukhov2026-benchmark-perturbation-target-prediction` | 4 (3 stored in the repository) | yes | 6 |
| `ucc-research-benchmark-sctab` | 4 (4 stored in the repository) | yes | 3 |
| `model-coverage-scfoundation-cell-annotation` | 4 (3 stored in the repository) | yes | 2 |
| `hitdisc-20261022-benchmark-dude` | 3 (1 stored in the repository) | yes | 1 |
| `hitdisc-20261022-benchmark-mfpcba` | 3 (3 stored in the repository) | yes | 2 |
| `intake-283-20261121-benchmark-cycpepnet` | 6 (6 stored in the repository) | yes | 12 |
| `intake-403-20261126-benchmark-cellbench-ls` | 1 (0 stored in the repository) | no | 1 |
