# Evidence-table release validation (candidate only, not frozen)

Candidate release: `2026-10-06-161b59a1d02c` (`released_at: 2026-10-06T23:43:41.000Z`). Produced by the
documented procedure (`npm run build:current`, per `package.json`), NOT committed, pushed, or opened as
a PR. This document validates that existing candidate's bytes; it does not regenerate or re-timestamp
it, and it does not freeze a release.

**Scope note:** the candidate carries only the bounded cell-type-annotation-transfer additive intake
(issue #349) layered on the already-merged BRCA release. It does not resolve scArches's unexplained
accuracy-formula denominator, Hao et al.'s 73.8%/79.4% internal conflict, or any other item in
`workbench/cell-type-ingestion-plan.md`. `use-case-cell-type-annotation-transfer.collection_plan.status`
remains `"collecting"`. This validation pass does not change that.

## What was checked

| Check | Result |
| --- | --- |
| Candidate present on disk, correct release ID | `data/omics/releases/2026-10-06-161b59a1d02c/` and matching `.json` manifest exist; `release_id` field matches directory name |
| Candidate's own manifest-declared checksums | 415/415 files verified independently (SHA-256 recomputed from the actual bytes, compared to `manifest.json`); 0 mismatches |
| All 67 prior mappings + 17 use cases preserved | Confirmed in the prior turn's independent review (receipt hashes, Abdelaal gzip SHA `6df0937c5a2d8ba06465ba356c2321fb9f52d9ecf23456876acd82f828b41d4c`); not re-litigated here |
| `npm run verify:archives` (`--archives-only`) | **Pass** — 6,163 source files verified against `docs/data-extraction.json` |
| `npm run verify:extraction` (full) | **Fails on `data/omics/release-config.json`** — pre-existing at HEAD (`c9e734f`), not caused by this candidate; see "Remaining issues" below |
| `npm run verify:package` | **Fails** — candidate's new files are not yet git-tracked; expected while uncommitted, per instruction not to commit |
| `npx tsc --noEmit` | Pass, no errors |
| `npx vitest run` (full suite) | **543/543 tests pass**, 48 files |
| Clean restore of **all** releases | `restoreReleaseBundles("data/omics/releases", "<verify-dir>/releases")` completed without throwing for all 29 release directories (every manifest-declared file present, every checksum verified internally, every use-case artifact binding validated) |
| Independent re-verification of the restore | Separately recomputed SHA-256 for every manifest-declared file in all 29 restored releases: **7,825/7,825 files, 0 mismatches** |
| Restored source copies (content-addressed `sources/`) | 4 files; each filename (SHA-256) matches `shasum -a 256` of its own content, 4/4 |
| Disk location and de-duplication | External SSD only (`/Volumes/Extreme SSD/...`), sibling to the worktree, not inside it; `restoreReleaseBundles`'s own hardlink de-duplication (`fs.linkSync`) kept repeated identical bytes to one inode. Total restored size: 33 GB on a volume with ~1.3 TB free; nothing written to the internal disk |

## Restore verification directory

`/Volumes/Extreme SSD/rewire-data-separation/cell-type-release-verify-20261007/` — layout:
`releases/<release-id>/*` + sibling `sources/<sha256>.md`, matching the existing
`restoreReleaseBundles` output convention (same layout as the pre-existing, untouched
`brca-restore-verify-20261005/` and `-20261006/` directories alongside it, which this pass did not
read from, write to, or otherwise disturb).

## Remaining issues (unresolved, not fixed here)

1. **`npm run verify:extraction` (full) fails on `data/omics/release-config.json`.** Checked directly:
   `git show HEAD:data/omics/release-config.json` (commit `c9e734f`, before any work in this session)
   already has SHA-256 `92fa70cd600b843aee05c219c8e9134820d22703760237de2ddf24d8137a0885` (75 bytes),
   not the migration-baseline-pinned `42d031ca0a3f7e39485edf29fef2f10b942e889e1a79e9190cdf714f4d8f0c49`
   (71 bytes) recorded in `docs/data-extraction.json`. This divergence predates this candidate (it
   comes from the BRCA release's own `released_at` bump) and is not a regression introduced by this
   pass. `docs/data-extraction.json` is a one-time migration-audit receipt
   (`rewire-bio/rewire-database@e13852aa4d190fb52fad29f38b0d6a5257aadb3b`); whether `release-config.json`
   is meant to be exempt from it on an ongoing basis, or whether the receipt needs a deliberate,
   separately-reviewed update, is not decided here. **Not fixed**; `docs/data-extraction.json` was not
   edited.
2. **`npm run verify:package` fails** because the candidate's new files (`data/omics/releases/2026-10-06-161b59a1d02c/*`,
   packaged `website/files/public/omics/...` outputs) are not yet tracked by git. This is the expected,
   correct state for an uncommitted candidate under the explicit no-commit/no-push instruction; it is
   not a defect in the candidate's bytes. It will resolve itself once (and if) these files are staged
   and committed in a future, separately authorized step.
3. All items already on record as unresolved in `docs/omics/evidence-research/cell-type-annotation-transfer-2026-10-06.md`
   and `workbench/cell-type-ingestion-plan.md` (scArches's accuracy-formula denominator, Hao et al.'s
   internal conflict, Abdelaal's un-ingested inter-dataset figures, and the other deferred sources)
   remain exactly as unresolved as before. This validation pass neither resolves them nor claims to.

No historical release bytes were changed. No commit, push, or PR was made. The candidate remains a
local, reviewable, bounded intake.
