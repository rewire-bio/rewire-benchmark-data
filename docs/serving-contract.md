# Serving-data contract

The producer prepares page data once per release, so the website can read bounded documents instead of loading and indexing the whole catalogue at startup. This is the producer side of [issue #31](https://github.com/rewire-bio/rewire-benchmark-data/issues/31). Website adoption is separate work in rewire-database.

Status: envelope schema 2, serving contract 1.0, first slice. `npm run serving` writes the artifacts to `public/serving/<release_id>/`; `npm run build` runs it. They are not yet packaged into `website/` or published.

## Versions

| Field | Meaning |
| --- | --- |
| `schema_version` | Packaging envelope, `2` |
| `serving_contract_version` | Payload format and semantics, `1.0` |
| `record_schema_version` | The scientific record schema of the release |

A major serving version changes for removals, type changes, changed meaning or ordering, or new required fields. Optional additions are minor; consumers ignore unknown optional fields and reject unsupported majors or missing required capabilities.

## Artifacts

| Group | Status | Files | Content |
| --- | --- | --- | --- |
| `bootstrap` | available | `bootstrap.json.gz` | Counts by kind, results by review status, evaluations by origin, facet labels |
| `routes` | available | `routes/<kind>.json.gz` | Every route, including legacy alias kinds, with its canonical route and page shard |
| `pages` | available | `pages/<00-ff>.json.gz` | One page per non-excluded record, all 16 kinds |
| `downloads` | available | `downloads.json.gz` | Release files with SHA-256 and archive path, a commit-pinned URL template, and earlier release receipts |
| `browse`, `search`, `supporting` | not yet | | Declared `false` in `capabilities` |

Each file entry in `manifest.json` gives `source`, `group`, `artifact_type`, `artifact_schema_version`, `encoding` (`gzip`), decoded `bytes` and `sha256`, and `stored_bytes` and `stored_sha256`. For the current release: 28,677 pages in 274 files, 42 MB stored.

## Pages

A page is keyed by record ID in shard `sha256(id)[0:2]`. Alias routes point to the same page.

| Field | Content |
| --- | --- |
| `record` | The complete record |
| `direct`, `reverse` | Relationships as `{relation, id}` |
| `source_ids` | Sources supporting the record and its evaluations |
| `summary` | Totals: results, evaluations, evidence rows, published comparisons, use-case links |
| `sections.results` | First 25 result rows; each holds the full result record and IDs of related records |
| `sections.evaluations` | Full evaluation records for those rows |
| `sections.evidence` | First 10 evidence-table rows |
| `sections.published_comparisons` | Source-scoped comparison panels |
| `sections.use_case_links` | Use cases that cite the record |
| `references` | `{id, kind, name, status}` for every ID the page mentions |

Tables carry `items`, `total`, `limit` and `next_cursor`. A cursor continues the table through the release-pinned API. Related records are referenced, never copied recursively. A page larger than 1 MB decoded is rebuilt with smaller tables (totals and cursors unchanged); the build fails if it still does not fit. Files are capped at 16 MB decoded.

## Schemas and fixtures

The zod schemas in `scripts/serving/contract.ts` are the source of truth. `npm run serving -- schemas` regenerates `docs/serving/schemas/*.schema.json` (JSON Schema 2020-12), and a test fails if the committed files drift. `docs/serving/fixtures/` holds a valid page shard and an invalid one.

## Differences from the issue

- The manifest records `generator_sha256`, a hash of the generator source files, instead of `generator_revision`. The commit that publishes the artifacts cannot be known while building them; the website lock already pins it.
- Outputs are generated, not committed. Packaging them for the website, and publishing them with the release, waits for the website adapter so the format can still change.

## Next steps

1. `browse`: prepared list rows and facet counts for index, category and use-case pages.
2. `search`: compact search documents and lookup indexes with the current API's matching and ordering.
3. `supporting`: use-case coverage, research readiness, audit metadata and update-feed receipts in bounded parts.
4. Parity checks against the website's current page and API output, and timing and size reports.
5. In rewire-database, a verified artifact reader that replaces runtime catalogue preparation.
