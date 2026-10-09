# Cutting a release

A release is an immutable, content-addressed snapshot of every reviewed record. Its ID is `<date>-<hash>`, derived from the records, the `released_at` time in `data/omics/release-config.json` and the release coverage. The coverage includes hashes of some generator source files (for example `lib/baseline-coverage.ts` and the evidence-table and research modules in `shared/omics/`), so changing those files' bytes, even only an import path, changes the ID of a rebuilt release. CI rebuilds the current release and fails if its ID changes, so make such changes together with a new release. The website pins one release. Only the current release's files are kept in the repository; earlier releases keep their receipts.

## When

Cut a release deliberately, not on every evidence PR:

- after a monthly refresh that finished `review_required` and whose changes have been reviewed and merged (see [refresh.md](refresh.md)), or
- after a reviewed batch that should reach the website before the next refresh.

Evidence PRs leave `release-config.json` alone. Several merged batches can go out in one release. A no-change refresh does not create a release.

## Automated releases

`.github/workflows/release.yml` runs on every push to `main` and on demand (Actions, "Cut and publish a release"). It builds a candidate release dated now and compares it with the current release, ignoring only the release ID and date (`scripts/release/next.mjs`). If nothing else differs it stops, so pushes that change no data cost one build and nothing else. Otherwise it keeps only the new release, rebuilds it to confirm it reproduces, runs every check (store, types, all tests, Python and KG tests, packaging, prepared-file parity, bundle format), commits it to `main` as `Cut release <id>`, publishes `serving/<id>` and `kg/<id>` tagged at that commit, and dispatches `data-release` to rewire-database. That starts its adopt-data-release workflow, which checks and deploys the release. A release cut by hand and merged as a pull request is published by `data.yml` and dispatched the same way.

The dispatch needs the repository secret `WEBSITE_DISPATCH_TOKEN`: a fine-grained personal access token (or GitHub App token) for `rewire-bio/rewire-database` with Contents read and write. GitHub's workflow token cannot reach another repository. Without the secret the release is still published, and the workflow warns that the website must adopt it by hand.

The workflow only packages what reviewed pull requests have already merged. It writes no release notes; add one to `scripts/omics/release.ts` in an evidence PR when a change needs it. Cut a release by hand, with the steps below, when you want it reviewed as a pull request first.

## Steps

1. On a branch from `main`, set `released_at` in `data/omics/release-config.json` to the current UTC time.
2. Build it and run the checks:

   ```sh
   npm run build
   npm test
   npm run test:python
   npm run test:kg
   npm run typecheck
   npm run verify:package
   ```

   The build writes the new release's receipt (`data/omics/releases/<release-id>.json`, the exact manifest bytes) and its gzipped files (`data/omics/releases/<release-id>/`), builds the knowledge-graph bundle in `public/kg/` and the prepared SQLite file in `public/serving/` (see [serving-contract.md](serving-contract.md)), and packages the website inputs. It never overwrites existing bytes.
3. Remove the previous release's files, keeping its receipt:

   ```sh
   npm run release:prune
   ```

4. Run `npm run build` again. It restores the frozen release first, so this confirms a fresh clone rebuilds it byte for byte. CI on the release PR repeats this without inference (`npm run build:check`); after merge, CI on main runs the full build with inference and publishes.
5. Open the PR with the config change, receipt, archive and updated `website/` files. Review scientific changes separately from packaging.
6. After merge, CI publishes the knowledge-graph bundle (tag `kg/<release-id>`, see [linked-data.md](linked-data.md#bundle)) and the prepared file (tag `serving/<release-id>`) as GitHub releases. Then open a PR in [rewire-database](https://github.com/rewire-bio/rewire-database) that updates `benchmark-data.lock.json` (revision, manifest digest, release ID, and `serving` with the tag, file name and SHA-256 from the published receipt) and runs `npm run shared:sync` from a checkout of this repository at that revision. The website builds the prepared file into a new image; its deployment checks control activation.
7. Once the release is live, record it with `npm run refresh -- record-publication` and `npm run refresh -- export` (see [refresh.md](refresh.md#review-prs-and-publication)).

Never edit a frozen release in place. Corrections always go into a new release.
