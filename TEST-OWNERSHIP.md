# Test ownership after the data split

The original website had 90 test files. They are partitioned into 39 producer test files and 60 website test files, plus the new consumer artifact suite (`benchmark-data-consumer.test.ts`). Split suites explain the higher combined file count.

The test-title audit found 706 original case declarations. All original declarations remain except two deployment fingerprint cases rewritten for the new lock-only data contract. Their tracked edits, additions, renames, deletions, environment filtering, and symlink checks remain covered. No test was skipped or disabled for the split.

## Producer

The producer owns acquisition, extraction, migration, numerical/source integrity, profile enrichment, evidence tables, release generation, archive restoration, local-run ingestion, recipes, research imports, and scientific coverage floors. Its 39 suites contain 439 executable tests, including 26 new packaging checks. They import no React, Next.js, website components, or website pages. `tests/fixtures/catalogue.ts` is the former pure API fixture copied locally, with no runtime service dependency.

Python source/artifact review checks under `scripts/omics/tests/` also belong to the producer. Service/API emulator tests remain with the website.

## Website

The website owns rendering, query presentation, search/filter behavior, SEO, analytics, contribution UI/export, transport, API storage, Hosting/deployment safety, and prepared-artifact verification. Broad corpus checks use the pinned prepared public catalogue. Five focused historical/synthetic fixtures under website `tests/fixtures/` preserve exact historical counts and output assertions without retaining generator code or complete release archives; their README records provenance and hashes.

## Split suites

| Original suite | Producer assertions | Website assertions |
| --- | --- | --- |
| `omics-benchmark-evidence` | Reviewed source expansion, preserved scientific rows, source-cell accounting, panel resolution | Literature audit rendering and public schema validation |
| `omics-source-label-identities` | Renaming, graph integrity, guards, input hashes, query validation | Released identity search/chart behavior, source notices, synthetic unresolved identity rendering |
| `omics-baseline-coverage` | Baseline audit semantics, deterministic export, historical release counts | Baseline component rendering with small explicit fixtures |
| `omics-run-recipes` | Original source quotations and pinned instructions (`omics-recipe-sources`) | Recipe rendering and runtime recipe validation |
| `omics-query-budget` | Scientific coverage-floor regression (`omics-coverage-floor`) | Bounded response size and lazy comparison behavior |
| `omics-evidence-completion` | Source concerns preserve data and prevent invalid comparison | Concern explanation rendering (`omics-evidence-concerns`) |
| `benchmark-literature` | Build-validator CLI checks and parity with runtime validator | CSV parser, runtime validator and prepared literature checks |
| `omics-research` | Research schema, release, import, archive and pinned snapshot checks | Backend immutable research chunk storage (`omics-research-storage`) |

Profile rendering and model coverage page suites now consume released records directly. They no longer reconstruct a release as test setup. Deployment tests treat `benchmark-data.lock.json` as the data fingerprint and still verify independent backend/source tracking and publication receipts.

The new `package-website.test.ts` covers exact prepared-byte round trips, required inputs, immutable receipt/archive conflicts, reuse of existing compressed files, current-only scope, and preservation of local files.

## Verification

Producer: 38 suites / 437 tests passed in the complete run, then the newly split literature build suite passed its two tests; total 39 suites / 439 tests. Producer TypeScript validation passed. Website: the initial complete run and targeted rerun of all six affected suites passed all 61 suites / 592 tests in aggregate. Exact historical navigation, model-count, result-count, and comparison-count assertions remain present.

## Upstream PR #80 preservation

The later upstream sync adds the unchanged archive-storage and use-case-coverage suites from `bc6b40772298f518ec1827311cc0e89f71c3c37e`, and preserves its updated use-case-release suite. The producer now has 41 suites / 449 passing tests. TypeScript validation and all six Python tests pass. Original extraction provenance remains in `docs/data-extraction.json`; the separate import receipt is `docs/upstream-sync-80.json`.
