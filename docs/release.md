# Cutting a release

A release is an immutable, content-addressed snapshot of every reviewed record. Its ID is `<date>-<hash>`, derived from the records and the `released_at` time in `data/omics/release-config.json`. The website pins one release. Only the current release's files are kept in the repository; earlier releases keep their receipts.

## When

Cut a release deliberately, not on every evidence PR:

- after a monthly refresh that finished `review_required` and whose changes have been reviewed and merged (see [refresh.md](refresh.md)), or
- after a reviewed batch that should reach the website before the next refresh.

Evidence PRs leave `release-config.json` alone. Several merged batches can go out in one release. A no-change refresh does not create a release.

## Steps

1. On a branch from `main`, set `released_at` in `data/omics/release-config.json` to the current UTC time.
2. Build the candidate and run the checks:

   ```sh
   npm run omics:release
   npm test
   npm run test:python
   npm run typecheck
   ```

3. Freeze it:

   ```sh
   npm run release:freeze
   ```

   This copies the exact manifest bytes to `data/omics/releases/<release-id>.json`, stores every manifest file as `data/omics/releases/<release-id>/<filename>.gz` (gzip level 9, no timestamp, round trip checked), and removes the previous release's folder. Earlier releases keep their receipts. It never overwrites existing bytes.
4. Run the full build, which restores the frozen release, checks the rebuilt release against it byte for byte, and packages the website inputs:

   ```sh
   npm run build
   npm run verify:package
   ```

5. Open the PR with the config change, receipt, archive and updated `website/` files. Review scientific changes separately from packaging.
6. After merge, open a PR in [rewire-database](https://github.com/rewire-bio/rewire-database) updating `benchmark-data.lock.json` (revision, manifest digest and release ID). The website verifies the artifact and renders it; its own deployment checks control activation.
7. Once the release is live, record it with `npm run refresh -- record-publication` and `npm run refresh -- export` (see [refresh.md](refresh.md#review-prs-and-publication)).

Never edit a frozen release in place. Corrections always go into a new release.
