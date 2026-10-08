# Cutting a release

A release is an immutable, content-addressed snapshot of every reviewed record. Its ID is `<date>-<hash>`, derived from the records and the `released_at` time in `data/omics/release-config.json`. The website pins one release; old releases stay downloadable byte for byte.

## When

Cut a release deliberately, not on every evidence PR:

- after a monthly refresh that finished `review_required` and whose changes have been reviewed and merged (see [refresh.md](refresh.md)), or
- after a reviewed batch that should reach the website before the next refresh.

Evidence PRs leave `release-config.json` alone. Several merged batches can go out in one release. A no-change refresh does not create a release.

## Steps

1. On a branch from `main`, set `released_at` in `data/omics/release-config.json` to the current UTC time.
2. Build the candidate and run the checks:

   ```sh
   npm run omics:release -- --current-only
   npm test
   npm run test:python
   npm run typecheck
   ```

3. Freeze it. Copy the exact `public/omics/releases/<release-id>/manifest.json` bytes to `data/omics/releases/<release-id>.json`. For every entry in `manifest.files`, verify its SHA-256 and save the bytes as `data/omics/releases/<release-id>/<filename>.gz` (gzip level 9, no timestamp). Check that each decompressed file matches the receipt. Never overwrite an existing receipt or archive with different bytes.
4. Run the full build, which restores every archived release through `restoreReleaseBundles` and packages the website inputs:

   ```sh
   npm run build
   npm run verify:package
   ```

   Before publishing, restore the new release into a clean temporary directory and check its inventory and every checksum. That proves a fresh clone can serve the same evidence.
5. Open the PR with the config change, receipt, archive and updated `website/` files. Review scientific changes separately from packaging.
6. After merge, open a PR in [rewire-database](https://github.com/rewire-bio/rewire-database) updating `benchmark-data.lock.json` (revision, manifest digest and release ID). The website verifies the artifact and renders it; its own deployment checks control activation.
7. Once the release is live, record it with `npm run refresh -- record-publication` and `npm run refresh -- export` (see [refresh.md](refresh.md#review-prs-and-publication)).

Archived files may be shared through hardlinks during a full build, so never edit a restored file in place. Corrections always go into a new release.
