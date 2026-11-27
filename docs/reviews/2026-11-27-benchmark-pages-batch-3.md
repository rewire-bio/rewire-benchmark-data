# Benchmark pages, batch 3, 2026-11-27

Prepared by Claude agents. No human review is claimed. Two research agents fetched sources and wrote the content, two agents verified it, two applied their findings, and a separate session checked and applied the result.

## What changed

24 Tier 2 benchmark records gain a `profile`, and 12 of them a `run_guide`. The new source records in `batch.jsonl` pin the files the content was written from. No result, evaluation, protocol or claim was added or changed, and no existing attribute was edited.

Three of the 27 Tier 2 benchmarks without a page are not in this batch. For two, the agent applying review findings was interrupted while editing the page, the open findings were not applied, and the page was not taken further. For one, the only source is a bioRxiv preprint with no other copy, which was not requested because the server was rate limiting.

## How statements were checked

Every copied passage was confirmed present in its saved file by `scripts/enrich/check_spec.py`. Two verifier agents that had not written the content judged 990 statements on the 26 researched pages and raised 26 findings (2.6%): 4 contradicted by a source, 12 that went partly beyond it and 10 with no support. That is about half the rate of the two Tier 1 benchmark batches (4.7% and 4.5%). The research agents for this batch were given a list of the specific faults earlier reviews had found. The table below covers the 24 pages in the batch (908 statements, 22 findings). All were applied.

The commonest fault this time was a name no saved file prints: a script, notebook or output file in a run step. Those were removed, and the run steps now use only commands a saved file gives. Each page's notes say what its sources do and do not state.

No page in this batch was read in full by the applying session before merge.

## Found in the sources themselves

Each is stated on the page concerned: figures that differ between a paper's abstract and its body, between a paper and its released code, or between a README and the script it documents. They are leads, not conclusions, and no person has confirmed them.

## Sources

Every fetched file was kept, whatever its licence, and uploaded to the private archive bucket under the sha256 its source record pins.

## Structured facts

The content files in `specs/` carry a `structured` list: 122 entries, one per task or track. They are not written to the records in this change.

## Run guides

All have status `source_reviewed_not_executed`. None was run.

## Per benchmark

Notes for a later reader are in each content file under `specs/`.

| Record | Sources | Run guide | Structured entries |
| --- | --- | --- | --- |
| `hyinv-20261106-benchmark-report-comparison` | 3 (2 stored in the repository) | yes | 9 |
| `hyplm-flash-20261106-benchmark-report-evaluation` | 3 (2 stored in the repository) | yes | 21 |
| `lit-interactions-20261011-ppiemb-benchmark-ppi-embedding-gnn-comparison` | 2 (0 stored in the repository) | no | 4 |
| `lit-structure-20261011-afesmfold-benchmark-promodev-2022-2024` | 2 (1 stored in the repository) | no | 2 |
| `ucc-research-benchmark-foldbench` | 4 (3 stored in the repository) | yes | 9 |
| `lit-otheromics-20261011-pepspecbench-benchmark-pepspecbench` | 2 (1 stored in the repository) | no | 9 |
| `lit-protein-20261011-prime-benchmark-prime` | 4 (4 stored in the repository) | yes | 4 |
| `uc-leadopt-20261022-benchmark-fep-public` | 5 (5 stored in the repository) | yes | 2 |
| `lit-structure-20261011-scaffoldlab-benchmark-scaffold-lab` | 4 (4 stored in the repository) | yes | 6 |
| `lit-agents-20261013-biomlbench-benchmark-biomlbench` | 5 (5 stored in the repository) | yes | 3 |
| `ucc-docking-cluspro-bm5-2020-benchmark` | 1 (0 stored in the repository) | no | 10 |
| `uc-leadopt-20261022-benchmark-casp16-affinity` | 1 (1 stored in the repository) | no | 5 |
| `poisk-20261115-benchmark-binder-decoy` | 1 (1 stored in the repository) | no | 1 |
| `uc20260930-benchmark-rhomax` | 5 (1 stored in the repository) | yes | 5 |
| `lit-structure-20261011-lipp-benchmark-lipp` | 6 (1 stored in the repository) | yes | 7 |
| `torchcraft-20261115-benchmark-runtime` | 3 (2 stored in the repository) | yes | 5 |
| `lit-interactions-20261011-mochibind-benchmark-alphabind-universal-affinity` | 4 (0 stored in the repository) | yes | 4 |
| `rfd4-proteina-20261115-benchmark-frozen-project-benchmark-20261009` | 4 (4 stored in the repository) | no | 6 |
| `torchcraft-20261115-benchmark-ligand-pocket-10-ligand` | 3 (2 stored in the repository) | no | 3 |
| `torchcraft-20261115-benchmark-cyclic-peptide-8-target` | 3 (2 stored in the repository) | no | 1 |
| `torchcraft-20261115-benchmark-minibinder-12-target` | 3 (2 stored in the repository) | no | 1 |
| `torchcraft-20261115-benchmark-vhh-15-target` | 3 (2 stored in the repository) | no | 1 |
| `intake-349-20261121-benchmark-met-kinase-dms-benchmark` | 6 (1 stored in the repository) | no | 3 |
| `intake-385-20261124-benchmark-elixir-protein-protein-interface-benchmark-openebench-experi` | 7 (1 stored in the repository) | yes | 1 |
