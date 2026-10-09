# Prepared release file

Each release ships one prepared SQLite file that the website pages and public API read directly. It holds the outputs of the live query engine, computed once per release, so no consumer parses the whole catalogue or rebuilds its indexes. This is the producer side of [issue #31](https://github.com/rewire-bio/rewire-benchmark-data/issues/31).

```
npm run build            # release, RDF export, then npm run serving
npm run serving          # public/serving/catalogue-<release>.sqlite and its .json receipt
npm run serving:parity   # every answer must equal the live engine's for the same release
npm run serving:publish  # GitHub Release asset on tag serving/<release> (CI does this on main)
```

## Why SQLite

The data is read-only and changes about once a month. One file gives indexed lookups, ordered pages and small reads on a cold start without a database service, a sharding scheme or a cache. Node's built-in `node:sqlite` reads it (Node 22.13 or newer), so there is no native dependency. Request-time work is limited to filtering and paging one record's rows.

## Contents

| Table | Content |
| --- | --- |
| `meta` | `serving_contract_version` (`2.0`), `record_schema_version`, `release_id`, `released_at`, `catalogue_sha256`, `generator_sha256`, `release_json` (the `release()` answer), `counts_json` |
| `records` | every non-excluded record, by ID, with kind and status |
| `details` | gzipped `get({ id, include_comparisons: true })` per record |
| `result_rows` | gzipped full result row per result |
| `result_index` | each record's result IDs in the engine's order |
| `evidence` | gzipped evidence-table rows per record |
| `audit_checks` | gzipped audit checks per audited record, in index order |
| `blobs` | gzipped list entries (search text, readiness, row origins, counts), research readiness, research data, inactive assessment IDs, the use-case state, the homepage summary, the evidence-guide counts, the baseline coverage audit, reviewed association keys, and the audit index, runs and resolutions |

For release `2026-10-07-061436ccd3b9`: 28,677 records, 12,487 result rows, 77,369 result memberships and 113,042 audit checks; 369 MB, built in under a minute. Same inputs and Node version give a byte-identical file.

## Reading it

`shared/omics/prepared-catalogue.ts` opens the file read-only and exposes the engine's methods: `release`, `record`, `get`, `comparison`, `results`, `evidence`, `list`, `compare`, `researchReadiness`, `investigations`, `useCases()`, `homeSummary`, `evidenceSummary`, `baselineAudit`, `verifiedAssociation`, `research`, `auditRuns`, `auditRecords` and `auditChecks`. Each uses the same exported functions as `createCatalogueQuery` (`resultPage`, `evidencePage`, `listPage`, `compareResults`, `readinessPage`, `investigationsPage`, `useCaseQueryFrom`), so filters, facet counts, ordering and cursors cannot drift. Cursors remain release-bound and interchangeable with the live engine's.

`serving_contract_version` changes major version when a table or meaning changes incompatibly; the reader refuses an unsupported major version.

## Checks

- `tests/prepared-catalogue.test.ts` builds the file from the canonical store, checks counts and runs the parity checks without use cases.
- `npm run serving:parity` (CI, after the build) runs over 1,500 parity checks on the real release, including use cases, the busiest records, several cursor pages, filters, comparisons and missing IDs.
- `npm run serving:publish` never replaces a published asset. It compares receipts: a build by the same generator must be byte-identical, and a build by a later generator leaves the published asset in place.

The website pins the asset by tag, file name and SHA-256 in `benchmark-data.lock.json`, verifies it at image build time and copies it into the image.
