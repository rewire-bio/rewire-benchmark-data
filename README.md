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
| [docs/linked-data.md](docs/linked-data.md) | Ontology mapping, JSON-LD context and the N-Quads export |
| [docs/reviews/](docs/reviews/README.md) | Dated evidence reviews: search logs and value-by-value checks |

Agent skills in [.agents/skills/](.agents/skills) (also linked from `.claude/skills`):

- `literature-search`: find published results and log every search
- `extract-evaluations`: turn a pinned source into records with exact values and locators
- `review-evidence`: independently check an extracted batch and record the review
- `database-refresh`: run the monthly cycle using the three skills above

## Layout

```
data/
  entities/                            canonical records, one JSONL file per kind (models, benchmarks, sources, ...)
  evidence/                            evaluations, results and claims
  provenance/records.jsonl             per-record hash, originating batch and reviewed changes
  ontology/                            RDF mapping and JSON-LD context for the records
  omics/
    <batch folders>/                   evidence for each extraction: receipts, retrieval logs, archived sources
    use-cases/                         use-case definitions and mappings
    pending-review/                    extractions not yet ready for the store
    search-ledger.jsonl, scope-audit.jsonl   searches and scope decisions
    audits/                            append-only audit runs
    releases/                          current release files, plus a receipt .json for every release
    release-config.json                released_at for the current release
  benchmark-literature/                paper-reported results table (see its README)
  research/                            research investigation inputs (see its README)
docs/                                  procedures and dated reviews
scripts/omics/                         record store, extraction, acquisition, audit and release code
services/omics/src/, lib/              validation and query code shared with the website
maintenance/                           refresh schedule, attempt records and reports
website/                               packaged inputs pinned by the website
```

Records are edited only through the store: `npm run records -- add` appends a reviewed batch, `npm run records -- change` records a reviewed edit, and `npm run records -- check` verifies every record against its provenance. See [docs/collection.md](docs/collection.md).

`services/omics/src/` and `lib/` keep the directory names they have in rewire-database so imports match. There is no running service here. Changes to shared schemas need compatibility checks in both repositories.

## Build and validate

Requires Node 22 or newer and Python 3.

```sh
npm ci
npm test
npm run test:python
npm run typecheck
npm run build
```

The build rebuilds the current release from the inputs and fails if any byte differs from the frozen copy in `data/omics/releases/`. CI runs it and also fails if anything under `data/` or `website/` changes.

## How the website consumes releases

`website/manifest.json` lists the prepared website inputs with destination, size and SHA-256. The website pins this manifest and a full git revision in its `benchmark-data.lock.json`, then verifies and unpacks the files without running any build step from here. No change in this repository reaches the live site until a website PR updates that lock.

## Provenance

This repository was split from rewire-database at `e13852aa4d190fb52fad29f38b0d6a5257aadb3b`. Only the current release is stored. Each earlier release keeps its receipt (`data/omics/releases/<id>.json`: counts, file hashes and changelog); its files remain in git history.
