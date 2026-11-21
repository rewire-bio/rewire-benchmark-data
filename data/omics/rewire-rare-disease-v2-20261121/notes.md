# Rare-disease case tests, second run: Rewire-run records, 2026-11-21

Rewire's own study `rewire-bio/amp-2026-studies`, folder `rare-disease-v2`, pinned at commit `3fbab97b0f437972a1a6e0f2171ebb5d9a3d9f19` (tag `amp-2026-v7`). This is not a literature pass, so there is no search ledger entry and no scope-audit entry. The store held no record of the study before this batch.

## What is in the batch

229 records, all built by `extract/build_batch.py rdv2` from files at the pinned commit:

| Kind | Count | Content |
| --- | --- | --- |
| source | 11 | `results/replication_main.json`, `results/snv_main.json`, `results/indel_main.json`, `results/snv_all1kg.json`, `results/analysis_snv_indel.md`, `PROTOCOL.md`, `README.md`, and four Evo 2 scoring receipts |
| benchmark | 1 | the study |
| dataset_subset | 3 | 500 replication SNV cases, 200 SNV cases, 120 indel cases |
| protocol | 3 | diagnostic variant ranking under the main filters, one per case set |
| configuration | 31 | 9 single scores, 2 rule-based rankings, 20 combined models (6 locked, 6 cross-validated on the 500, 6 on the 200, 2 on the 120) |
| evaluation | 45 | 23 on the 500, 17 on the 200, 5 on the 120 |
| result | 135 | top 1, top 5 and top 10 for each evaluation, with the file's 95% bootstrap interval |

Every evaluation has origin `rewire_run`. Every record is `source_checked`. Nothing is `reproduced`: no full-protocol run receipt exists for the ranking analysis.

## The Evo 2 receipts

Evo 2 7B scores come from four scoring runs, each with a receipt at the pinned commit. `evo2/select_variants.py` reuses a first-study score where one exists, and among the first study's files the first in sorted order wins. The script repeats that rule, checks each reused score against the file it came from, and counts, per case set, the case variants whose used score came from each run (diagnostic variants in brackets):

| Receipt | Run | 500 replication | 200 SNV | 120 indel |
| --- | --- | --- | --- | --- |
| `rare-disease-v2/evo2/run2/receipt.json` | this study, 2 November 2026 | 6,513 (481) | 188 (188) | 107 (107) |
| `rare-disease/evo2/run/receipt.json` | first study, 16 to 17 October 2026 | 700 (11) | 7,497 (0) | 0 |
| `rare-disease/evo2/run/receipt_extra.json` | first study, second job, 16 October 2026 | 0 | 9 (9) | 0 |
| `rare-disease/evo2/run3/receipt.json` | first study, 19 October 2026 | 8 (8) | 3 (3) | 1,064 (13) |

Counts are over each case set's case variants of the type the analysis ranks, before the frequency and inheritance filters: SNVs on the 500 and the 200, indels on the 120. `case_benchmark.py` ranks a diagnostic among variants of its own type only (`/filter/variants_after_dropping_other_type`). Every diagnostic variant is ranked, so the bracketed counts are scores that the results certainly use.

An earlier draft counted both variant types. That made the first study's run of 16 to 17 October look like a source of scores on the 120 indel cases, where all 7,497 of its variants are SNVs and none is ranked. Its receipt is no longer cited on the indel cases.

A receipt is cited by a case set's Evo 2 evaluations and results only if it produced at least one of that case set's scores. So `receipt_extra.json` is cited only on the 200 SNV cases, and `rare-disease/evo2/run/receipt.json` only on the 500 and the 200. The seven Evo 2 evaluations (Evo 2 and Lookups + Evo 2 on each case set, and the locked Lookups + Evo 2 on the 500) carry the counts in `reproduction_note`. No other record of the batch cites a receipt, apart from the Evo 2 configurations. These are scoring receipts, not receipts for the benchmark, so they do not make a result `reproduced`.

## Known limit recorded as a concern

The README's Limits section says gnomAD presence is only partly fixed. Diagnostics keep their full gnomAD frequency and most are absent from gnomAD; background variants rarely are. The study's own split check (`gnomad_split`) flags one gain: Rule + AVI over the rule-based ranking on the 200 SNV cases, in the all1kg check (`results/snv_all1kg.json`, `/gnomad_split/difference/Rule + AVI minus Rule-based/possibly_gnomad_presence` is true). The script asserts that flag and asserts that the three main files flag nothing. The split check tests two gains per SNV analysis, both from adding AVI (to the rule-based ranking and to the combined lookups), and none on the indel cases. The script asserts those contrast names. So no gain from GPN-MSA, GPN-Star, Evo 2 or a single lookup was tested. In the main analysis of the 200 the same gain is 0.0608 (0.0195 to 0.1149) where the diagnostic is absent from gnomAD and 0.0 where it is found (`results/snv_main.json`, `/gnomad_split`), and `results/analysis_snv_indel.md` says the gain is confined to absent cases in every analysis.

The concern is on `rewire-local-20261121-rdv2-source-readme` and its `applies_to` names one evaluation: `rewire-local-20261121-rdv2-evaluation-rule-avi-snv-200`. That evaluation's three results are withheld from comparisons and use-case judgements. The flagged check is on the same cases and configurations as the main analysis but with a different background frequency, so scoping the concern to the main-analysis evaluation is a judgement, and the scope is the owner's call. It follows the README, which states the limit for the study and not for one check. For every other evaluation the design limit is untested, not cleared. Two evaluations carry the same AVI score on the same 200 cases and are not withheld: `rewire-local-20261121-rdv2-evaluation-avi-snv-200` and `rewire-local-20261121-rdv2-evaluation-lookups-avi-snv-200`. Whether to widen the concern to them is also the owner's call. The limit is the first entry of `limitations` on the benchmark, each protocol and each dataset subset.

## Decisions

- `comparison.split` is set per evaluation: `locked` for the six locked models on the 500 (fitted on the 200 SNV cases), `cross-validated` for a combined model fitted on its own case set, and `none` for a single score or a rule-based ranking, where nothing is fitted. An earlier draft copied the file's `/fits` text, which lists every kind of fit, onto all evaluations of a case set.
- Only the `all` stratum of the three `main` files is ingested. Top 1, top 5 and top 10 are fractions in the files and are stored as fractions with unit `fraction`.
- Combined models fitted by cross-validation are separate configurations per case set, because each is a different fit. The locked models are their own configurations.
- `version` is given for a score only where `PROTOCOL.md` or `data/README.md` states it (the script asserts the strings). Otherwise it is marked unextracted.
- Sources carry the licence string `MIT (repository LICENSE)`, which is already in `data/archive/licence-map.tsv`. CADD and REVEL scores are not in the repository.
- No use-case link and no judgement was written. The judgements needed are listed in the dated review.

## Not ingested

- The filter checks (`bg1pct`, `nomoi`, `all1kg`, `heldout`, `evee`), the frequency sweep and the per-group strata.
- The paired contrasts, including the primary result (Lookups + AVI locked minus Lookups combined locked, +0.018, `/primary`). A contrast between two configurations has no single `system`, so it does not fit an evaluation as the store defines one.
- The first study, `rare-disease/`, apart from its three Evo 2 scoring receipts.
