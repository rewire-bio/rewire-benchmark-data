# EGFR evidence-release validation — 2026-10-07

Validates the prepared release candidate that adds the bounded, additive EGFR NSCLC
evidence-retrieval proxy intake (B345/BL345, rewire-benchmarks #25 and #28;
`use-case-egfr-nsclc-actionability-resistance-evidence`) on top of the unchanged prior catalogue.
**This is a prepared candidate pending PR — it has not been staged by this process for commit,
committed, pushed, opened as a PR, or deployed.**

## Release identity

- `data/omics/release-config.json` `released_at` updated once, to the actual build-time UTC
  timestamp: `2026-10-07T10:38:35.000Z`.
- Build command: `TMPDIR="/Volumes/Extreme SSD/rewire-test-tmp" npm run build` (full historical
  build; **not** `build:current`). Started `2026-10-07T10:38:56Z`, exit `0`, finished
  `2026-10-07T10:45:05Z` (~6m9s).
- New release ID: **`2026-10-07-b7e5907c917f`**.
- Prior release compared against: `2026-10-07-e11db1d1c586`.
- Build console output: `Omics 2026-10-07-b7e5907c917f: 28234 public records; 12282 source-checked
  result rows; 15 in review.`

## Independently verified counts

| Metric | Prior (`e11db1d1c586`) | New (`b7e5907c917f`) | Delta | Expected | Match |
|---|---|---|---|---|---|
| Public records (`catalogue.json.gz`) | 28,225 | 28,234 | +9 | +9 | ✅ |
| `result` records (manifest `counts.result`) | 12,292 | 12,294 | +2 | +2 | ✅ |
| `result` records with `status: "source_checked"` | 12,280 | 12,282 | +2 | +2 | ✅ |
| Use cases (`use-cases.json.gz`) | 17 | 17 | 0 | 17 | ✅ |
| Mappings (`use-cases.json.gz`) | 71 | 72 | +1 | 72 (71 unchanged) | ✅ |

Counts were computed independently by decompressing and parsing
`data/omics/releases/<release_id>/catalogue.json.gz` and `use-cases.json.gz` directly with
Python (`gzip`/`json`), not read from console output alone.

## Byte-identity of every pre-existing record

Compared all 28,225 prior-release record objects against the new release by ID:

- Prior IDs missing from the new release: **0**
- Prior IDs present but byte-different in the new release: **0**
- Brand-new IDs in the new release: **9**, exactly:
  `ucc-clinical-egfr-source-civicfact-v3`, `ucc-clinical-egfr-data-civicfact-v3-postcutoff`,
  `ucc-clinical-egfr-protocol-civicfact-v3-retrieval`, `ucc-clinical-egfr-config-medcpt-ft`,
  `ucc-clinical-egfr-config-qwen3-reranker-8b`, `ucc-clinical-egfr-eval-medcpt-ft-postcutoff`,
  `ucc-clinical-egfr-eval-qwen3-8b-postcutoff`,
  `ucc-clinical-egfr-result-medcpt-ft-postcutoff-appropriate`,
  `ucc-clinical-egfr-result-qwen3-8b-postcutoff-appropriate`.

## Use-case mappings

- All 71 prior mapping objects (by ID) are byte-identical between the two releases.
- All 17 `use_cases` entries are byte-identical between the two releases.
- Exactly one new mapping: `use-case-mapping-20261007-345-7c4af3e091bd` (second `proxy` mapping
  for `use-case-egfr-nsclc-actionability-resistance-evidence`; the first,
  `use-case-mapping-20260930-345-ba1ec69965eb`, is one of the 71 unchanged mappings).

## Manifest-declared checksums

`public/omics/manifest.json` declares 415 files for the new release. Every declared SHA-256 was
independently recomputed from the gzip-compressed archive bytes under
`data/omics/releases/2026-10-07-b7e5907c917f/` (decompressed then hashed): **415/415 verified,
0 missing, 0 mismatches.**

## Immutable archive/index integrity

- `git status --short data/omics/releases/` shows only additions under the new release directory
  (`2026-10-07-b7e5907c917f/` and its `.json` manifest copy); no modifications to any prior
  release directory were found.
- `data/omics/releases/2026-10-07-e11db1d1c586/` (and all other prior release directories) were
  read-only inputs to the comparisons above and were not written to by this process.

## Clean restore to a fresh external-SSD sibling directory

Used the existing `restoreReleaseBundles` routine (`scripts/omics/archives.ts`) directly via a
short script (`workbench/egfr-20261007/run-restore-verify.ts`), reading from the immutable
`data/omics/releases/` archive and writing to a **brand-new sibling directory** outside this
worktree: `/Volumes/Extreme SSD/rewire-data-separation/egfr-restore-verify-20261007/`.

- Command: `TMPDIR="/Volumes/Extreme SSD/rewire-test-tmp" node_modules/.bin/tsx
  workbench/egfr-20261007/run-restore-verify.ts`. Started `2026-10-07T10:47:19Z`, exit `0`,
  finished `2026-10-07T10:50:02Z` (~2m43s). The routine's own internal checksum/manifest-binding
  checks (which throw on any mismatch) completed without error.
- **Independent re-verification** (separate from the routine's own internal checks): recomputed
  SHA-256 for every file in every restored release directory against its restored
  `manifest.json`, across all 31 restored releases: **8,655 files checked, 0 missing, 0
  mismatches.**
- Restored use-case source copies (4 files under `.../sources/`): each file's SHA-256 matches its
  own `use-case-source-<sha256>.md` filename exactly: **4/4 verified.**

No bytes in `data/omics/releases/` (the source of truth for this restore) were modified by
running this routine; it is read-only against that directory by construction.

## Test, typecheck, and verification receipts

All commands run with `TMPDIR="/Volumes/Extreme SSD/rewire-test-tmp"`; full logs under the
git-ignored `workbench/egfr-20261007/`.

| Command | Result | Log |
|---|---|---|
| `vitest run` (full suite, run once before the build; no test-relevant source changed afterward) | 50 files / **565 tests passed**, 298.36s | `full-vitest-run.log` |
| `tsc --noEmit` | **exit 0**, no output | `typecheck.log` |
| `python3 -m unittest discover -s scripts/omics/tests -p "test_*.py"` | **6/6 passed**, exit 0 | `python-tests.log` |
| `npm run build` (full) | **exit 0** | `build.log` |
| Restore to fresh sibling SSD directory | **exit 0** | `restore.log` |
| `node scripts/verify-extraction.mjs --archives-only` (pre-build) | **exit 0**, verified 6,163 source files | `verify-archives.log` |
| `node scripts/verify-extraction.mjs --archives-only` (post-build) | **exit 0**, verified 6,163 source files | `verify-archives-postbuild.log` |
| `node scripts/verify-extraction.mjs` (full, **not** archives-only) | **exit 1** — documented, see below | `verify-extraction-full.log` |
| `node scripts/verify-package-tracking.mjs` | exit 0 (see "Package tracking" below) | `verify-package.log` |

### Full `verify:extraction` issue, documented (not fixed)

The full (non-`--archives-only`) check fails with `Extraction preservation failed:
data/omics/release-config.json`. This is **expected and was not altered**: `docs/data-extraction.json`
is the pre-existing migration receipt that pins the original SHA-256 of
`data/omics/release-config.json` from the extraction-migration baseline. Updating
`released_at` in `release-config.json` (required, once, per this task) necessarily changes that
file's hash and trips the full check, which audits migration-baseline preservation rather than
current release state. `--archives-only` filters the receipt to only
`data/omics/releases/...` paths and passes cleanly both before and after the build. The migration
receipt (`docs/data-extraction.json`) itself was **not modified** by this process.

### Package tracking — reported accurately, not resolved here

Codex explicitly staged the scoped source files, new immutable release and prepared package after the full build. This was an operator action, not automatic staging by the build scripts. Package verification then passed for all **8,775 tracked prepared sources**. Codex independently checked all 415 candidate checksums, preserved all 28,225 prior records, and confirmed that the 8,300 prior release inventory entries retain their source paths, destinations, SHA-256 values and sizes. The previous current release changes inventory scope to archive; its bytes remain unchanged.

## Scientific scope — unchanged limitations

This release candidate adds one proxy mapping. It does not:

- Establish an EGFR- or NSCLC-specific evidence-retrieval score (the ingested cohort and the
  already-catalogued CIViC MCP triplets are both pan-cancer).
- Close the focused execution gap tracked at
  [rewire-benchmarks #28](https://github.com/rewire-bio/rewire-benchmarks/issues/28) (an
  independently adjudicated, context-sensitive EGFR/NSCLC evidence-retrieval comparison at equal
  reviewer effort remains unestablished).
- Constitute qualified human scientific review, clinical validation, or new Rewire model
  execution — both ingested results are author-reported, transcribed from CIViC-Fact v3's
  post-cutoff temporal cohort (150→66→42→40 selection chain; 37/40, 92.5%, appropriate-content
  rate on manual review for both a fine-tuned MedCPT cross-encoder and a pretrained
  Qwen3-Reranker-8B, on the identical cohort — one cohort, two configurations, not two
  independent cohorts).
- Mark the 17-use-case programme complete, or claim any deployment: this document records a
  **prepared, independently verified release candidate pending PR**, not a published or deployed
  release.

See `docs/omics/evidence-research/egfr-nsclc-evidence-retrieval-2026-10-07.md` for the full
research dossier, source locators, and the licence-fact correction (nested
`data_builder/LICENSE`, GPLv3, pinned commit `1a767d889b015a836f0f4331afcac5cef165ec7f`, blob
`f288702d2fa16d3cdf0035b15a9fcbc552cd88e7`) this candidate incorporates.
