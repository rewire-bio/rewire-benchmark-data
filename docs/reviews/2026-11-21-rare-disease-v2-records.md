# Rare-disease case tests, second run: Rewire-run records, 2026-11-21

Reviewer: Claude agent, automated. One agent wrote the generator and ran the checks. A second automated pass then reviewed the draft, and the batch was rebuilt on main to fix what it found (receipt citations on the indel cases, `comparison.split`, and the wording of the gnomAD concern). There was no human review. Nothing was rerun and no GPU or paid run was made.

Batch: `data/omics/rewire-rare-disease-v2-20261121/` (229 records). Notes and the list of what was left out are in its `notes.md`.

## Source

`rewire-bio/amp-2026-studies` at commit `3fbab97b0f437972a1a6e0f2171ebb5d9a3d9f19`, tag `amp-2026-v7` (public). One source record per file. Each file was downloaded again from its raw URL on 2026-11-21 and hashes to the recorded SHA-256:

| Source record | File under `rare-disease-v2/` | SHA-256 |
| --- | --- | --- |
| `rewire-local-20261121-rdv2-source-results-replication-500` | `results/replication_main.json` | `b50c2a14c02fa4a1d86047895d09eb8ed9d2daa52b9848d57bf5da01fb347023` |
| `rewire-local-20261121-rdv2-source-results-snv-200` | `results/snv_main.json` | `052f7beb544f826333a1b627b6beadd77aa26fcb3e5e0fe53d73064f011901bc` |
| `rewire-local-20261121-rdv2-source-results-indel-120` | `results/indel_main.json` | `84f688bb18d08390bc62ff72726efc9e2d981503acc0936cb7a308745c3ab88c` |
| `rewire-local-20261121-rdv2-source-results-snv-all1kg` | `results/snv_all1kg.json` | `e4e5292ecdbcfdf248ea576b6074fcb05179b8c42b9b597c932fe7e442d9d38b` |
| `rewire-local-20261121-rdv2-source-protocol` | `PROTOCOL.md` | `1cd87827233991a886601526908cda1c08d8f5c50a2bb6e83367a7e9cf554a47` |
| `rewire-local-20261121-rdv2-source-readme` | `README.md` | `570ab11fba7a829fc8abe355ab5968bda9070ed8a8c909d77da727c7d144798b` |
| `rewire-local-20261121-rdv2-source-analysis-snv-indel` | `results/analysis_snv_indel.md` | `f7f2d75e3be1df390c5429e4cc730389cdc42f9fc33e1e4a6d31edc993de189c` |
| `rewire-local-20261121-rdv2-receipt-evo2-run2` | `evo2/run2/receipt.json` | `d937576844eec7a416f224c6d2bf4ccaa68d2517fbe13b9d1c2842ca1721ede0` |
| `rewire-local-20261121-rdv2-receipt-evo2-run` | `../rare-disease/evo2/run/receipt.json` | `fc161ed5d7d061de4445d33a1fdde87aaef212d0e941ed81733d7aef3c5bb3b4` |
| `rewire-local-20261121-rdv2-receipt-evo2-run-extra` | `../rare-disease/evo2/run/receipt_extra.json` | `a53128489d205f05d9b599adebc339bf56e0560730f403a50d5a456ad36434ed` |
| `rewire-local-20261121-rdv2-receipt-evo2-run3` | `../rare-disease/evo2/run3/receipt.json` | `ed533ea8cb514a72d904e7622c1d2465f55c99b4c31f8f8fabc2c58767593d51` |

## How values were checked

`extract/build_batch.py rdv2 <checkout> <batch folder>` builds the batch from a checkout at the pinned commit and refuses any other commit. It reads JSON with floats kept as strings, so each `printed_value` is the literal number token in the file, a fraction. Each result's `source_locator` is the file path and the JSON pointer, for example `rare-disease-v2/results/replication_main.json, JSON pointer /strata/all/scores/Lookups combined (locked)/top_1`. After building, the script reads every pointer again and compares the token and both interval bounds with the record. `--check` rebuilds in memory and compares with the stored `batch.jsonl` byte for byte.

The script asserts: 11 sources, 1 benchmark, 3 subsets, 3 protocols, 31 configurations, 45 evaluations and 135 results; that every record is `source_checked`; 23, 17 and 5 scores in the `all` stratum of the three files; analysis `main`, `max_af` 0.001 and the inheritance filter in each file; no case lost its diagnostic; 1,000 resamples of people; the gnomAD split flag in `snv_all1kg.json` and no flag in the three main files; the README limit headings the records quote; the main-analysis split values the concern quotes; that each receipt's variant count equals the rows of its scores file; the count of Evo 2 scores per run and case set; that every source is cited by a record; the contrast names the gnomAD split check tests in each file; the fit named in each evaluation's `comparison.split`; and how many evaluations and results cite each receipt (28 each for `run2` and `run3`, 20 for the first study's `run`, 8 for `receipt_extra.json`), with no record of the 120 indel cases citing `run`.

`npm run batch -- check-values` was not run. It parses table and row locators and cannot read a JSON pointer.

## Rulings

- Status. Every result is `source_checked`. No receipt covers the ranking analysis, so nothing is `reproduced`.
- Evo 2 receipts. Four scoring runs produced the Evo 2 scores, one in this study and three in the first study. Each score was traced to its run by key, and a receipt is cited only on the case sets where it produced a score for a variant of the type the analysis ranks. A second automated pass found that the first draft counted both variant types and so cited `rare-disease/evo2/run/receipt.json` on the 120 indel cases, where that run scored SNVs only and no SNV is ranked. Nine records lost that citation: two evaluations, their six results and the configuration `lookups-evo-2-cv-indel-120`. The table of counts is in the batch `notes.md`, and each Evo 2 evaluation carries its counts in `reproduction_note`.
- gnomAD presence. Recorded as a scoped evidence concern on the README source, `applies_to` `rewire-local-20261121-rdv2-evaluation-rule-avi-snv-200`, the one evaluation whose gain the study's split check flags (`results/snv_all1kg.json`). The concern also quotes the main-analysis split from `results/snv_main.json`. Applying a flag raised in the all1kg check to the main-analysis evaluation is a judgement; the scope is the owner's call. Its three results are withheld from comparisons and judgements. The split check tests only two gains per SNV analysis, both from adding AVI, and none on the indel cases, so the concern now says the limit is untested, not cleared, for every other score. `avi-snv-200` and `lookups-avi-snv-200` carry the same AVI score on the same cases and are not withheld; widening is the owner's call. The limit is also the first `limitations` entry on the benchmark, protocols and subsets. The reasoning is in the batch `notes.md`.
- Split. `comparison.split` names the fit of each evaluation: locked (6 on the 500), cross-validated (a combined model fitted on its own case set) or none (a single score or a rule-based ranking). The first draft put the file's `/fits` summary on every evaluation of a case set.
- Values are not rescaled. The files hold fractions (`results/README.md`: "Proportions are fractions (0.906 is 90.6%)").

## Checks

- `npm run records -- add` accepted the batch and the SHACL check of the 229 records and their 8 link targets passed.
- `npm run records -- check`: 93,538 records match their provenance.
- `npm run check:task-links`: passes. Each new protocol is `part_of` the new benchmark.
- `npm run depth-tier -- check`: 0 records differ from the rule, so tier 1 on the new benchmark matches it.
- Not run: `npm run archive -- fetch`. The eleven sources have no archive object yet. The fetch writes rows that name a local cache as the home of the bytes, and this pass ran in a clone that was deleted afterwards.
- `npm run checks -- report`: one rule rises above `data/omics/checks-baseline.json`.

| Check | Rule | Baseline | After this batch | Rise |
| --- | --- | --- | --- | --- |
| C1 unit for metric | minority-unit | 5,093 | 5,228 | 135 |
| C1 unit for metric | all rules | 5,391 | 5,526 | 135 |
| total findings | | 10,754 | 10,889 | 135 |

All 135 findings are the 135 results of this batch. They carry unit `fraction` for `top-1-accuracy`, `top-5-accuracy` and `top-10-accuracy`. Before this batch the store held those metrics as percent 216 and fraction 74, percent 160, and percent 107 and fraction 6, so percent is the majority unit and a fraction is reported as a minority unit. The values are right as stored: the result files hold fractions and the contract says `printed_value` is the value as the source gives it. `tests/checks-baseline.test.ts` will fail on this rule. The baseline was not changed. Whether to raise it, or to settle the proportion-unit convention first (issue #272, step 6), is the owner's decision.

## Use-case judgements needed

No use case links to these protocols and no judgement was written in this pass. To put these results on a use-case page, a judgement is needed for each pair below. Relevance is for the judgement to decide.

| Use case | Protocols |
| --- | --- |
| `use-case-rare-disease-candidate-ranking` | `rewire-local-20261121-rdv2-protocol-replication-500-main`, `-snv-200-main`, `-indel-120-main` |
| `use-case-unresolved-rare-disease-reanalysis` | the same three, if a judgement finds them relevant |

## Gaps

Listed in the batch `notes.md` under "Not ingested": the filter checks, the sweep, the per-group strata, the paired contrasts including the primary result, and the first study.
