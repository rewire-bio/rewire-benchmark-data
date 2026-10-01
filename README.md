# Rewire benchmark data

Reviewed biological benchmark records, source evidence, ingestion, validation and immutable releases. Extracted from `rewire-bio/rewire-database` at `e13852aa4d190fb52fad29f38b0d6a5257aadb3b` (PR #78).

The benchmark frontend and Firebase API remain in [rewire-database](https://github.com/rewire-bio/rewire-database). Benchmark execution remains in [rewire-benchmarks](https://github.com/rewire-bio/rewire-benchmarks). This repository has no website, deployment credentials or private submission store.

## Build and validate

Requires Node 22 or newer and Python 3.

```sh
npm ci
npm run verify:archives
npm test
npm run test:python
npm run typecheck
npm run build
```

`data/` contains the canonical editable records, reviewed evidence and original compressed historical exports. `scripts/omics/` owns migration, extraction and release generation. Pure validation/query contracts under `services/omics/src/` and `lib/` were copied at the extraction revision to retain the exact release semantics. Their directory names preserve source imports; there is no running API service here. Changes to shared schemas require compatibility checks in both repositories.

`website/manifest.json` describes prepared frontend inputs by destination, size and SHA-256. Compressed objects preserve original bytes. The website pins this manifest and a full Git revision in `benchmark-data.lock.json`; it verifies and unpacks them without running ingestion or release generation. Generated compatibility files in the website are ignored and are never edited there.

## Review and release

1. Submit evidence changes here, retaining provenance and source locators. Update `data/omics/release-config.json` only for a reviewed new release. Never modify old release exports.
2. Run data tests and build the prepared artifact. Review scientific changes independently of website changes.
3. Publish the prepared artifact with its Git revision. Open a website pull request updating its data lock (revision, manifest digest and release ID).
4. The website verifies the artifact and renders pages. Existing deployment checks still control activation and preserve historical downloads.

No data change automatically changes the live website or activates submissions. The frontend uses a read-only token scoped to this private repository. It does not need write access or data-generation credentials.

`docs/data-extraction.json` records all 6,592 original data files and their hashes. The initial release preserves `2026-09-29-06401fd5b220` and 26,126 public records. Upstream PR #80 was subsequently preserved from `bc6b40772298f518ec1827311cc0e89f71c3c37e`; its latest release is `2026-09-30-e37e3ab1284d`, with 28,133 public records and evidence/gap audits for all 17 use cases. `docs/upstream-sync-80.json` records every imported path and checksum separately from the original extraction receipt.

The extraction receipt is permanent provenance. `verify:extraction` checks the entire original snapshot during migration; CI uses `verify:archives` so reviewed source updates and new release timestamps remain possible while original historical exports stay immutable.
