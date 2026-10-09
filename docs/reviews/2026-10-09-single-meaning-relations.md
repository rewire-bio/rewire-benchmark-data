# Single-meaning relations, 2026-10-09

Stage 2 of [issue #42](https://github.com/rewire-bio/rewire-benchmark-data/issues/42). Every relationship name now has one meaning and a fixed set of record kinds it may link from and to (`shared/omics/relations.ts`), and evaluations use one link style. No record IDs, values, sources or locators change.

9,756 of 28,719 records changed: 9,197 evaluations, 169 configurations, 143 claims, 98 tasks, 72 baselines, 51 dataset subsets, 23 protocols and 3 benchmarks. Each is recorded in `data/provenance/records.jsonl` with inputs `shared/omics/relations.ts` and this review.

## What changed

| Record kind | Before | After | Links |
| --- | --- | --- | --- |
| evaluation | `model`, or typed `configuration` | `system` | 8,725 + 472 |
| evaluation | `benchmark`, or typed `protocol` | `assessment` | 8,725 + 472 |
| evaluation | `dataset`, or typed `dataset_subset` | `data` | 8,999 + 198 |
| baseline | `model`, `configuration` | `implemented_by` | 15 + 56 |
| baseline | `evaluation` | `measured_in` | 52 |
| baseline, task, protocol, benchmark | `dataset` | `uses_data` | 1 + 98 + 25 + 3 |
| dataset subset | `benchmark` | `used_in` | 51 |
| configuration | `variant_of` | `configuration_of` | 169 |

The 143 claims whose `field` cited a configuration's `variant_of` link now cite `links:configuration_of:...`, so the association they verify is unchanged.

Before this change, the same name meant different things on different kinds of record. On an evaluation, `model` named what was evaluated; on a baseline it named what implements it. `benchmark` on an evaluation pointed at tasks and protocols, never a benchmark, and on a dataset subset it named the protocol that uses it. The RDF mapping needed per-kind overrides (`by_kind`) and the reasoner had to merge the two evaluation link styles. Both are gone: each relation maps to one property, and `rb:testedSystem`, `rb:testedOn` and `rb:dataset` are asserted rather than inferred.

## How it was checked

- The migration is `normalizeRecords` from `relations.ts`, the same function every reader applies to older releases. It runs once over the store and is idempotent: a second run changes nothing.
- Every link in the migrated store satisfies its relation's rules, and every evaluation has exactly one `system`, `assessment` and `data` (`npm run records -- check`).
- Older releases stay readable. The query engine, snapshot validation, the release builder, the use-case and research readers, the baseline audit and `lib/omics` translate old names on load. Tests that build catalogues with the old names (`tests/fixtures/catalogue.ts`, the legacy cases in `tests/omics-entity-boundaries.test.ts`) still pass.
- Rollups through family links behave as before: `configuration_of` is treated like the `variant_of` it replaces, and only when a reviewed claim backs the link.
- The extraction and import scripts write the new names, and `records -- add` rejects the old ones.

## Consumers

The release workflow cuts and publishes a release after this merges and dispatches it to the website, which copies `shared/omics` and adopts the release automatically when its checks pass. Website code that reads relation names must accept the new names before that adoption, or the adoption stops at its checks and the website stays on the previous release.
