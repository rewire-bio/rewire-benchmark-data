# Cutting a release

A release is an immutable, content-addressed snapshot of every reviewed record. Its ID is `<date>-<hash>`, derived from the records, the `released_at` time in `data/omics/release-config.json` and the release coverage. The coverage includes hashes of some generator source files (for example `lib/baseline-coverage.ts` and the evidence-table and research modules in `shared/omics/`), so changing those files' bytes, even only an import path, changes the catalogue: the next automated release is cut even if no record changed. The coverage also lists a SHA-256 for each input file (`source_inputs`). The record store appears there as one logical file per kind plus `data/provenance/records.jsonl`, each hashed over its lines in ID order, so splitting store files into shards ([collection.md](collection.md#where-records-live)) does not change the ID; any change to a stored line does. The release notes (`changelog` in the receipt) are not part of the ID or the catalogue. The website pins one release. Only the current release's files are kept in the repository; earlier releases keep their receipts.

## Automated releases

`.github/workflows/release.yml` runs after "Benchmark data checks" pass for a push to `main`, and on demand (Actions, "Cut and publish a release"). Evidence PRs leave `release-config.json` alone; the workflow cuts the release. It:

1. Runs `node scripts/release/next.mjs prepare`, which dates a candidate release now and writes into the release config the commit it is built from (`source_revision`) and the release notes.
2. Builds it once with `npm run build`.
3. Compares it with the current release, ignoring only the release ID and date (`next.mjs pending`). If nothing else differs, and the serving contract is unchanged, it stops: pushes that change no data cost one build.
4. Refuses a release that withholds or drops use-case mappings the current release serves, unless their judgement was excluded or superseded (`next.mjs withheld`); re-review and re-pin those relevance judgements first ([use-cases.md](use-cases.md)).
5. Removes the previous release's files (`npm run release:prune`), checks the packaging (`npm run verify:package`) and the prepared file against the live query engine (`npm run serving:parity`). Types, tests, the store check and SHACL already passed for this commit in "Benchmark data checks".
6. Commits the release to `main` as `Cut release <id>`, publishes the prepared SQLite file as `serving/<id>` tagged at that commit, and dispatches `data-release` to rewire-database. That starts its adopt-data-release workflow, which checks and deploys the release.

The build never changes an archived file: packaging (`scripts/package-website.mjs`) refuses to overwrite a file in `data/omics/releases/<id>/` with different bytes. There is no second build to confirm reproduction.

The dispatch needs the repository secret `WEBSITE_DISPATCH_TOKEN`: a fine-grained personal access token (or GitHub App token) for `rewire-bio/rewire-database` with Contents read and write. GitHub's workflow token cannot reach another repository. Without the secret the release is still published, and the workflow warns that the website must adopt it by hand.

### Merging while a release is being cut

Merge reviewed PRs whenever they are ready; there is no need to wait for a release run. Release runs share one concurrency group and queue rather than cancel. GitHub keeps one waiting run, so a run waiting behind the current one may be replaced by a newer one; that loses nothing, because each run builds `main` as it is when it starts. If a PR is merged while a release is being cut, the release push is rejected; the workflow rebases the release commit onto the new `main` and pushes again (up to five attempts). The merged PR is not in that release, and the run its merge starts releases it next. A rebase conflict, which only a hand-cut release merged at the same time can cause, fails the run.

"Benchmark data checks" also accepts `merge_group` events, so a merge queue can be enabled for `main` in the repository settings. If it is, the release bot must be allowed to push to `main` directly.

### Release notes

`next.mjs prepare` lists every pull request merged on `main` (first-parent history) after the previous release's `source_revision`, one line each: its title and number (`scripts/release/changelog.mjs`). Commits pushed directly to `main`, such as release commits, are left out. Write PR titles so they read as release notes. The notes go in the receipt (`data/omics/releases/<id>.json`) only; nothing in `scripts/omics/release.ts` needs editing for a release.

## Knowledge graph

The knowledge-graph bundle is not built in the data release, which does not need Python, uv, the reasoner or rdf-kg-mcp. Once a release is published, the release workflow starts "Build and publish a knowledge-graph bundle" (`.github/workflows/kg-release.yml`) for it, so every release still gets its bundle a few minutes later without the release waiting for it. To build one by hand, run "Build and publish a knowledge-graph bundle" (`.github/workflows/kg-release.yml`) from the Actions tab, with a release ID or none for the newest published release. It checks out the commit `serving/<id>` was published from, rebuilds the catalogue and confirms it matches the receipt, builds the bundle (`npm run kg:bundle`), checks it with `npm run kg:verify` and publishes it as `kg/<id>` ([linked-data.md](linked-data.md#bundle)). Running it again for a release that has a bundle only checks that the build reproduces it.

## Cutting a release by hand

Cut a release by hand when you want it reviewed as a pull request first:

1. On a branch from `main`, run `node scripts/release/next.mjs prepare`. It sets `released_at` to the current UTC time and writes `source_revision` and the release notes. Edit the notes if needed.
2. Build it and run the checks:

   ```sh
   npm run build
   npm run release:prune
   npm test
   npm run typecheck
   npm run verify:package
   ```

   The build writes the new release's receipt (`data/omics/releases/<release-id>.json`, the exact manifest bytes) and its gzipped files (`data/omics/releases/<release-id>/`), builds the prepared SQLite file in `public/serving/` (see [serving-contract.md](serving-contract.md)), and packages the website inputs. It never overwrites existing bytes. `release:prune` removes the previous release's files and keeps its receipt.
3. Open the PR with the config change, receipt, archive and updated `website/` files. Review scientific changes separately from packaging. CI rebuilds the release and fails if any file differs from the PR's.
4. After merge, CI publishes the prepared file (tag `serving/<release-id>`) and dispatches `data-release` to the website, as for an automated release. The publish job then starts the knowledge-graph bundle build for it.
5. Once the release is live, record it with `npm run refresh -- record-publication` and `npm run refresh -- export` (see [refresh.md](refresh.md#review-prs-and-publication)).

Never edit a frozen release in place. Corrections always go into a new release.

## Release files in git

The current release's gzipped files (`data/omics/releases/<id>/`) and the website package (`website/`) are still committed with each release, because the website reads them from git: rewire-database's adopt-data-release workflow and `scripts/select-current-data.mjs` sparse-check-out the sources that `website/manifest.json` lists at the pinned revision, and `scripts/adopt-data-release.mjs` reads `data/omics/releases/<id>/use-cases.json.gz` from both revisions with `git show` to refuse withheld mappings. Publishing them as release assets only (#110) needs those three places to download and verify a package asset from the `serving/<id>` release instead. Until then, only the receipt and the current release's files are kept, as now.
