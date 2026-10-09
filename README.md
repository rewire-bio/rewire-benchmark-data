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
| [docs/linked-data.md](docs/linked-data.md) | Ontology mapping, vocabulary, inference and the knowledge-graph bundle for MCP clients |
| [docs/serving-contract.md](docs/serving-contract.md) | Prepared release file the website and API read (issue #31) |
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
  ontology/                            RDF mapping, JSON-LD context, vocabulary, pinned imports and SHACL shapes
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
services/omics/src/                    record validation, query engine and prepared-file reader, mirrored by the website
lib/                                   rendering helpers shared with the website
maintenance/                           refresh schedule, attempt records and reports
website/                               packaged inputs pinned by the website
```

Records are edited only through the store: `npm run records -- add` appends a reviewed batch, `npm run records -- change` records a reviewed edit, and `npm run records -- check` verifies every record against its provenance. See [docs/collection.md](docs/collection.md).

`services/omics/src/` is the source of truth for the code the website mirrors in its `shared/omics/` (its tests are in `tests/shared/`); there is no running service here. The website copies it with `npm run shared:sync` when it adopts a release. The folder keeps its name because release IDs hash some of these files' bytes, so renaming it means a new release; do it alongside the next real one. Changes to shared schemas need compatibility checks in both repositories.

## Build and validate

Requires Node 22 or newer, Python 3 and [uv](https://docs.astral.sh/uv/) (for the knowledge-graph build).

```sh
npm ci
npm test
npm run test:python
npm run test:kg
npm run typecheck
npm run build
```

The build rebuilds the current release from the inputs and fails if any byte differs from the frozen copy in `data/omics/releases/`.

CI keeps data pull requests fast. Every run validates the store (`npm run records -- check`) and runs the KG rule tests, the Python tests and type checking; pull requests run the fast test set (`npm run test:fast`), main runs everything (`npm test`). Only runs that cut a release (a change to `data/omics/release-config.json`) rebuild the release, in a separate job that runs at the same time as the checks: release pull requests without inference (`npm run build:check`), main with inference (`npm run build`, which runs inference and the prepared SQLite file side by side), followed by the parity and bundle checks. On main, a publish job then waits for both jobs to pass before publishing. A failure that `npm run build` would catch therefore shows up in the release PR, not in each evidence PR.

## How the website consumes releases

`website/manifest.json` lists the prepared website inputs with destination, size and SHA-256. Each release also has a prepared SQLite file, published as the GitHub release asset `serving/<release-id>` (see [docs/serving-contract.md](docs/serving-contract.md)); the website's pages and public API read only that file. The website pins the manifest, a full git revision and the prepared file's SHA-256 in its `benchmark-data.lock.json`, verifies them and builds the file into its image, without running any build step from here. No change in this repository reaches the live site until a website PR updates that lock (see [docs/release.md](docs/release.md)).

## Provenance

This repository was split from rewire-database at `e13852aa4d190fb52fad29f38b0d6a5257aadb3b`. Only the current release is stored. Each earlier release keeps its receipt (`data/omics/releases/<id>.json`: counts, file hashes and changelog); its files remain in git history.
