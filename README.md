# Rewire benchmark data

Reviewed benchmark results for omics and molecular models, the source evidence behind every value, and the procedures for collecting, reviewing and releasing them.

The website and API that display this data live in [rewire-database](https://github.com/rewire-bio/rewire-database). Benchmark execution lives in [rewire-benchmarks](https://github.com/rewire-bio/rewire-benchmarks). This repository is public and holds no credentials or private submissions.

## Collecting and updating data

| Document | What it covers |
| --- | --- |
| [docs/collection.md](docs/collection.md) | The collection procedure: search, capture sources, extract, review, validate. Start here. |
| [docs/record-contract.md](docs/record-contract.md) | Record kinds and fields |
| [docs/use-cases.md](docs/use-cases.md) | Use-case definitions, mappings and how to change them |
| [docs/evidence-tables.md](docs/evidence-tables.md) | The per-claim evidence export |
| [docs/refresh.md](docs/refresh.md) | The bounded monthly refresh cycle |
| [docs/release.md](docs/release.md) | When and how to cut a release |
| [docs/reviews/](docs/reviews/README.md) | Dated evidence reviews: search logs and value-by-value checks |

Agent skills in [.agents/skills/](.agents/skills) (also linked from `.claude/skills`):

- `literature-search`: find published results and log every search
- `extract-evaluations`: turn a pinned source into records with exact values and locators
- `review-evidence`: independently check an extracted batch and record the review
- `database-refresh`: run the monthly cycle using the three skills above

## Layout

```
data/omics/
  discovery.jsonl, migrated.jsonl      base records
  reviewed/                            benchmark extraction batches
  use-case-coverage-<batch>/           use-case evidence batches, by lane
  use-cases/                           use-case definitions and mappings
  pending-review/                      extractions not yet ready for the build
  evidence-sources.jsonl               pinned source artifacts
  evidence-concerns.jsonl              known problems that block comparison
  metadata-corrections.jsonl           superseding descriptive corrections
  search-ledger.jsonl, scope-audit.jsonl   searches and scope decisions
  reviews/, audits/                    review receipts and audit runs
  releases/                            frozen releases (receipt .json + archived files)
  release-config.json                  released_at for the current release
data/benchmark-literature/             paper-reported results table (see its README)
data/research/                         research investigation inputs (see its README)
docs/                                  procedures and dated reviews
scripts/omics/                         extraction, acquisition, audit and release code
services/omics/src/, lib/              validation and query code shared with the website
maintenance/                           refresh schedule, attempt records and reports
website/                               packaged inputs pinned by the website
```

`services/omics/src/` and `lib/` keep the directory names they have in rewire-database so imports match. There is no running service here. Changes to shared schemas need compatibility checks in both repositories.

## Build and validate

Requires Node 22 or newer and Python 3.

```sh
npm ci
npm run verify:archives   # historic release bytes are unchanged
npm test
npm run test:python
npm run typecheck
npm run build:current     # current release only; `npm run build` restores every historic release
```

CI runs the full build and fails if it changes anything under `data/` or `website/`.

## How the website consumes releases

`website/manifest.json` lists the prepared website inputs with destination, size and SHA-256. The website pins this manifest and a full git revision in its `benchmark-data.lock.json`, then verifies and unpacks the files without running any build step from here. No change in this repository reaches the live site until a website PR updates that lock.

## Provenance

This repository was split from rewire-database at `e13852aa4d190fb52fad29f38b0d6a5257aadb3b`. `docs/data-extraction.json` records every original file and hash from that split, and `verify:archives` checks that historic release exports still match it.
