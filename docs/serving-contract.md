# Prepared release file

Each release ships one prepared SQLite file that the website pages and public API read directly. It holds the outputs of the live query engine, computed once per release, so no consumer parses the whole catalogue or rebuilds its indexes. This is the producer side of [issue #31](https://github.com/rewire-bio/rewire-benchmark-data/issues/31).

```
npm run build            # release, then npm run serving and the website package
npm run serving          # public/serving/catalogue-<release>.sqlite and its .json receipt
npm run serving:parity   # every answer must equal the live engine's for the same release
npm run serving:publish  # GitHub Release asset on tag serving/<release> (CI does this on main)
```

## Why SQLite

The data is read-only and changes about once a month. One file gives indexed lookups, ordered pages and small reads on a cold start without a database service, a sharding scheme or a cache. Node's built-in `node:sqlite` reads it (Node 22.13 or newer), so there is no native dependency. Request-time work is limited to filtering and paging one record's rows.

## Contents

| Table | Content |
| --- | --- |
| `meta` | `serving_contract_version` (`3.3`), `record_schema_version`, `release_id`, `released_at`, `catalogue_sha256`, `generator_sha256`, `release_json` (the `release()` answer), `counts_json` |
| `records` | every non-excluded record, by ID, with kind and status, its JSON gzipped |
| `details` | gzipped `get({ id, include_comparisons: true })` per record |
| `result_rows` | gzipped full result row per result |
| `result_index` | each record's result IDs in the engine's order |
| `evidence` | gzipped evidence-table rows per record, in packed form (below) |
| `audit_checks` | gzipped audit checks per audited record, in index order |
| `use_case_entries` | gzipped use-case mappings and sources per use case, and result rows per mapping and evaluation, keyed by section and ID |
| `source_records` | per source, one row per kind of citing record: the count and the gzipped record IDs in display order (3.1) |
| `discrepancies`, `discrepancy_results`, `discrepancy_systems`, `discrepancy_actions`, `discrepancy_aliases` | discrepancies between studies inferred by the knowledge-graph build for this release, with their follow-up actions, indexed by result, system and earlier ID (3.3; [discrepancies.md](discrepancies.md#serving-database-contract-33)) |
| `blobs` | gzipped list entries (the record's ID, kind, status, facets and origin, search text, readiness, row origins, counts, and from 3.2 the linked counts below), the use-case index (entries and backlinks), evidence source fields, research readiness, research data, inactive assessment IDs, the homepage summary, the evidence-guide counts, the baseline coverage audit, reviewed association keys, the audit index, runs and resolutions, and from 3.3 the discrepancy list entries (`discrepancy_index`) |

Each record is stored once. In `details`, `result_rows` and `use_case_entries`, an embedded object that is exactly a stored record is written as `{"$r": "<id>"}`, and one that is exactly its `recordReference` form as `{"$ref": "<id>"}` (`shared/omics/serving-codec.ts`). An evidence row keeps only the fields that cannot be derived: its record fields, `row_id` and `value` are rebuilt from the record and `value_json`, and its source fields come from the `evidence_sources` blob. The producer decodes every value it writes and refuses the file unless the result equals the engine's answer.

For release `2026-10-10-f5a0b65d47b6`: 45,277 records, 24,727 result rows, 138,569 result memberships and 2,354 use-case entries; 186 MB in contract 3, against 559 MB in contract 2, built in under a minute. Same inputs and Node version give a byte-identical file.

A record cites a source when the source's ID appears in its `source_ids`, its links or anywhere in its attributes (profile facts, claim citation locators, review sources, pins); a result also cites the sources its result row shows, which include its evaluation's. Kinds follow the vocabulary order in `shared/omics/entity-kinds.ts`. Results are ordered by evaluation name, then metric and qualifier; other kinds by name (`shared/omics/source-records.ts`). For release `2026-10-10-457d7eaef7d6` the table holds 59,649 IDs for 1,143 of 1,149 sources in 3,247 rows and adds 0.96 MB to the file.

## Reading it

`shared/omics/prepared-catalogue.ts` opens the file read-only and exposes the engine's methods: `release`, `record`, `get`, `comparison`, `results`, `evidence`, `list`, `compare`, `researchReadiness`, `investigations`, `useCases()`, `homeSummary`, `evidenceSummary`, `baselineAudit`, `verifiedAssociation`, `research`, `auditRuns`, `auditRecords`, `auditChecks`, `sourceRecords` and `sourceResults`, and from 3.3 `discrepancies`, `discrepancy`, `contestedBy`, `discrepanciesForSystem`, `discrepancyActions`, `discrepancyRules` and `hasDiscrepancies`. Each uses the same exported functions as `createCatalogueQuery` (`resultPage`, `evidencePage`, `listPage`, `compareResults`, `readinessPage`, `investigationsPage`, `useCaseQueryFrom`), so filters, facet counts, ordering and cursors cannot drift. Cursors remain release-bound and interchangeable with the live engine's.

`list` returns `evaluation_summaries` per record. `evaluation_count` and `result_count` count the results that reach the record through links backed by a reviewed association claim, the same rows `results()` pages. `linked_evaluation_count` and `linked_result_count` (3.2) also count results held on records linked to it as configurations, versions, aliases (`configuration_of`, `variant_of`, `family`, `alias_of`) or benchmark components (`part_of`), whether or not a claim backs the link, so a family whose results all sit on its configurations no longer reads as empty. Each result and each evaluation is counted once however many links lead to it. `uses_model` and `evaluates_task` are not followed. On a file written before 3.2 the linked counts equal the verified ones.

`serving_contract_version` changes major version when a table or meaning changes incompatibly. The reader opens contracts 2 and 3, so a website can serve a release of either form while it switches, and refuses any other major version. A minor version adds tables that older readers ignore. On a 3.0 file, which has no `source_records`, `sourceRecords` and `sourceResults` answer as if no record cited the source. On a file before 3.3, or one built without the knowledge graph, the discrepancy readers return no findings.

`sourceRecords({ id, kind?, cursor?, limit? })` returns `counts` by kind, `total` and `pages`: the first page of IDs of every kind, or with `kind`, the page of that kind the cursor names. `sourceResults({ id, cursor?, limit? })` returns one page of the source's results as table rows (`printed_value`, `unit`, `metric`, `qualifier`, `evaluation`, `tested`, `benchmarks`, `datasets`, each named record as `{ id, kind, name }`), reading only that page's rows and the records they name.

## Checks

- `tests/prepared-catalogue.test.ts` builds the file from the canonical store, checks counts and runs the parity checks without use cases. It checks the source index against a brute-force scan of the store, its paging, and that a 3.0 file reads as having no source records. It also rewrites that file into the contract 2 layout and runs the same parity checks on it.
- `npm run serving:parity` (CI, after the build) also checks that the discrepancy tables hold exactly the knowledge-graph build's findings for the release. It runs over 2,600 parity checks on the real release, including use cases, the busiest records and sources, several cursor pages, filters, comparisons and missing IDs.
- `npm run serving:publish` never replaces a published asset. It compares receipts: a build by the same generator must be byte-identical, and a build by a later generator leaves the published asset in place.

The website pins the asset by tag, file name and SHA-256 in `benchmark-data.lock.json`, verifies it at image build time and copies it into the image.
