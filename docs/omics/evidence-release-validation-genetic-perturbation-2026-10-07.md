# Genetic-perturbation-response evidence-release validation — 2026-10-07 (revised)

Validates the prepared release candidate that adds the bounded, additive genetic-perturbation-response
PertEval-scFM intake (B334/BL334, rewire-benchmarks #25; focused execution gap rewire-benchmarks #29;
`use-case-genetic-perturbation-response`) on top of the unchanged prior catalogue. **This is a prepared
candidate pending staging/PR — it has not been staged by this process for commit, committed, pushed,
opened as a PR, or deployed.**

**Revision note:** this replaces the prior version of this document, which validated release candidate
`2026-10-07-2febb643131b`. That candidate was rejected after Codex found one mischaracterization in a
result record's `evidence_overlap` field (see "Correction 1" below) and one historical packaging
omission (see "Correction 2" below). The rejected candidate's untracked release/package bytes were
preserved under `workbench/genetic-perturbation-20261007/rejected-candidate-2febb643131b/` (confirmed
untracked via `git ls-files` before removal) and then deleted from their live paths; **no previously
tracked historical release was touched**. This document now validates the corrected replacement
candidate, `2026-10-07-12bc4df80b96`.

## Correction 1 — result-record characterization

`perteval-scfm-2025-result-mean-baseline-auspc`'s `attributes.evidence_overlap` called the context-mean
baseline the protocol's "no-effect reference row." This is not established: the source's own Mean
baseline (mean expression of "all cells in the same context" minus the cell's own expression) is not
necessarily a zero-effect predictor, and the population it averages over is explicitly ambiguous in the
source text. Corrected to: "the protocol's own Mean-baseline reference row, distinct from Table 6's 'No
Perturb' control." No other field on this or any other record changed — printed value, numeric value,
status, links, and all counts are identical to the rejected candidate. `experimental/records.jsonl` and
the mapping's `evidence_sha256` were both refreshed to reflect this one-field change.

## Correction 2 — historical coverage packaging omission

The rejected candidate's full package build silently omitted `public/omics/coverage/2026-10-07-b7e5907c917f.json`
from `website/manifest.json`, even though its tracked gzip (`website/files/public/omics/coverage/2026-10-07-b7e5907c917f.json.gz`)
still existed on disk. Fixed by decompressing that **exact tracked** gzip back into the live
`public/omics/coverage/` directory before the final full package step; its decompressed SHA-256 was
confirmed to match the value Codex supplied, `a98150689d7e66746af241791e2de91f0f59fd5094171464d0decdd830044c93`,
**before** repackaging. A full diff of the resulting `website/manifest.json` against the last git-committed
(`HEAD`) manifest confirmed **zero dropped entries** and exactly two legitimate non-scope-label changes
(`website/files/public/omics/catalogue.json.gz` and `website/files/public/omics/manifest.json.gz`, both
expected to change for any new current release); all other 416 changed entries are pure
`scope: "current" -> "historical"` label flips for the now-superseded prior-current release
(`b7e5907c917f`), with identical bytes.

## Release identity

- `data/omics/release-config.json` `released_at` updated once more, to a new actual UTC timestamp:
  `2026-10-07T13:25:04.000Z`.
- Build commands, in order: `npm run build:current` (regenerates the release data as current-only; does
  **not** re-restore or re-export all 31 historical releases, per instruction), then a manual restore of
  the one historical coverage file described above, then `node scripts/package-website.mjs` (full, no
  `--current-only` flag) to rebuild the complete website manifest including historical destinations.
  (Two intermediate attempts at this sequence failed and were corrected in-place before the final clean
  run: the first `build:current` packaging step failed on a stale manifest reference left over from the
  rejected candidate; after restoring `website/manifest.json` to its clean `HEAD` state and removing
  leftover gitignored `public/` scratch directories for the rejected candidate, both the `--current-only`
  and full packaging steps completed cleanly with zero stale references. No code change was involved in
  any of this — only working-tree state cleanup.)
- New release ID: **`2026-10-07-12bc4df80b96`**.
- Immediate prior release: **`2026-10-07-b7e5907c917f`** (released_at `2026-10-07T10:38:35.000Z`,
  28,234 public records).
- Build console output: `Omics 2026-10-07-12bc4df80b96: 28246 public records; 12285 source-checked
  result rows; 15 in review.` Final full packaging: `Packaged benchmark website data
  (2026-10-07-12bc4df80b96): 9200 files (current-only: false)`.
- Top-level release manifest SHA-256 (`data/omics/releases/2026-10-07-12bc4df80b96.json`):
  `f265ce9e2f9ded5b9b47c0da95c31873f39e0018b0864c6e9169c45d13714895`.
- Website package manifest SHA-256 (`website/manifest.json`):
  `6afd35795e2ff956a829ead162c3d1a6d6ed92452b25559b078624e256ed3a4a`.

## Independently verified counts

| Metric | Prior (`b7e5907c917f`) | New (`12bc4df80b96`) | Delta | Expected | Match |
|---|---|---|---|---|---|
| Public records (`catalogue.json.gz`) | 28,234 | 28,246 | +12 | +12 | OK |
| `configuration` records | 2,613 | 2,616 | +3 | +3 | OK |
| `dataset_subset` records | 361 | 362 | +1 | +1 | OK |
| `protocol` records | 416 | 417 | +1 | +1 | OK |
| `evaluation` records | 9,094 | 9,097 | +3 | +3 | OK |
| `result` records | 12,294 | 12,297 | +3 | +3 | OK |
| `source` records | 1,007 | 1,008 | +1 | +1 | OK |
| Use cases (`use-cases.json.gz`) | 17 | 17 | 0 | 17 | OK |
| Mappings (`use-cases.json.gz`) | 72 | 73 | +1 | 73 (72 unchanged) | OK |

Counts computed independently by decompressing and parsing `catalogue.json.gz` / `use-cases.json.gz`
directly with Python, not read from console output alone.

## Byte-identity of every pre-existing record

Compared all 28,234 prior-release record objects against the new release by ID:

- Prior IDs missing from the new release: **0**
- Prior IDs present but byte-different in the new release: **0**
- Brand-new IDs: **12**, exactly: `perteval-scfm-2025-source`,
  `perteval-scfm-2025-dataset-norman-single-2000hvg`,
  `perteval-scfm-2025-protocol-norman-single-2000hvg-auspc`, `perteval-scfm-2025-method-gears`,
  `perteval-scfm-2025-method-mlp-baseline`, `perteval-scfm-2025-method-mean-baseline`,
  `perteval-scfm-2025-evaluation-gears`, `perteval-scfm-2025-evaluation-mlp-baseline`,
  `perteval-scfm-2025-evaluation-mean-baseline`, `perteval-scfm-2025-result-gears-auspc`,
  `perteval-scfm-2025-result-mlp-baseline-auspc`, `perteval-scfm-2025-result-mean-baseline-auspc`.

## Use-case mappings

- All 72 prior mapping objects (by ID) are byte-identical between the two releases.
- All 17 `use_cases` entries are byte-identical between the two releases.
- Exactly one new mapping: `use-case-map-perteval-scfm-norman-single-auspc`. The two prior mappings for
  this use case (`use-case-map-gears-norman-table6-mse`, `use-case-map-gears-norman-table6-pearson-de`)
  are among the 72 unchanged mappings; their eight underlying GEARS Supplementary Table 6 result records
  are among the byte-identical pre-existing records above.

## Manifest-declared checksums

`website/manifest.json` declares 9,200 files. Every declared SHA-256 (a hash of each file's
**decompressed** content) was independently recomputed from the gzip-compressed archive bytes under
`website/files/`: **9,200/9,200 verified, 0 missing, 0 mismatches.**

## Immutable archive/index integrity

- `git status --short data/omics/releases/` shows only additions under the new release directory
  (`2026-10-07-12bc4df80b96/` and its `.json` manifest copy); no modifications to any prior release
  directory were found.
- `npm run verify:archives` (`node scripts/verify-extraction.mjs --archives-only`): **exit 0**, "Verified
  6163 source files from rewire-bio/rewire-database@e13852aa4d190fb52fad29f38b0d6a5257aadb3b."
- No previously tracked file, in any prior release directory or elsewhere, was modified or removed by
  this pass. The only deletions performed were of the rejected candidate's own untracked paths,
  confirmed untracked via `git ls-files` immediately beforehand (empty output for every path checked).

## Clean restore — new release only

Per instruction, only the new release was restored to a fresh external-SSD directory this pass (the 31
unchanged historical releases were **not** re-restored, since they were already verified intact in the
prior pass and are confirmed untouched by `git status` above).

- Copied `data/omics/releases/2026-10-07-12bc4df80b96/` (415 files) and its top-level `.json` manifest to
  a fresh sibling directory: `/Volumes/Extreme SSD/rewire-data-separation/genetic-perturbation-release-verify-20261007/`
  (the prior pass's verification directories, which referenced the now-rejected candidate, were removed
  first).
- `diff` of `shasum -a 256` listings for all 415 files: **identical**. Top-level manifest SHA-256:
  identical (`f265ce9e2f9ded5b9b47c0da95c31873f39e0018b0864c6e9169c45d13714895`) in both locations.
- `gunzip -t` confirmed gzip integrity for `records.jsonl.gz`, `catalogue.json.gz` and `use-cases.json.gz`
  in the restored copy.

## Test, typecheck, and verification receipts

| Command | Result | Notes |
|---|---|---|
| `vitest run` (full suite, 51 files / 571 tests) | **passed** | Retained from earlier in this session; not re-run, since this pass's only changes are one record attribute's text, the corresponding receipt/mapping hashes, and release metadata/build state — no code or type change beyond what was already typechecked and build-exercised. |
| `vitest run tests/omics-genetic-perturbation-perteval-intake.test.ts` | **6/6 passed** | Re-run after the Correction 1 wording fix, and again after the final clean release build, to confirm the focused intake remains internally consistent |
| `tsc --noEmit` | **exit 0**, no output | Re-run after the final build |
| `python3 -m unittest discover -s scripts/omics/tests -p "test_*.py"` | **6/6 passed** (prior pass) | Not re-run; no Python-relevant file changed in this pass |
| `npm run build:current` | **exit 0** (after in-place cleanup of a stale manifest left by the rejected candidate) | |
| `node scripts/package-website.mjs` (full) | **exit 0** (after restoring the historical coverage file and removing leftover rejected-candidate scratch directories) | |
| `npm run verify:archives` | **exit 0**, 6,163 files verified | |
| Manifest-declared checksum re-verification | **9,200/9,200 verified, 0 mismatches** | |
| Clean restore (new release only) | **415/415 files + manifest byte-identical** | |

`npm run verify:extraction` (full, not `--archives-only`) and `npm run verify:package` were not re-run in
this pass: both have the same pre-existing/by-design characteristics documented in the prior version of
this report (the former fails on the immutable `docs/data-extraction.json` migration receipt pinning an
old `release-config.json` hash, not altered here; the latter requires git-index tracking that only
exists after staging, which this pass does not perform).

## Scientific scope — unchanged limitations

This release candidate adds one proxy mapping. It does not:

- Establish prospective experiment-selection hit rate (case 6, `use-case-phenotype-perturbation-selection`,
  is the separate endpoint for that question).
- Constitute qualified human scientific review or new Rewire model execution — all three ingested results
  are author-reported, transcribed from PertEval-scFM's Table 1 (Norman single-gene, 2,000 HVGs): GEARS
  (trained from scratch, no pretrained weights; checkpoint/artifact identifier unknown, not inapplicable)
  0.815 +/- 0.039; an MLP baseline (input Xc concatenated with perturbed-gene co-expression features,
  Eq. 3) 4.484 +/- 0.299; a context-mean baseline (population not fully specified by the source as
  control-only or training-only; not established as a no-effect/zero-effect reference) 4.612 +/- 0.317 —
  all x10^-2, scoring the perturbation-effect delta=P-Xc (Eq. 5), not raw post-perturbation expression.
- Resolve the source's own internal inconsistencies, left explicit: Table 1's double-gene section prints
  a GEARS/Mean-baseline/Delta trio that does not reproduce by simple subtraction
  (4.255-0.808=3.447, not the printed 4.254); Table 2 (Replogle RPE1, not part of this intake) has a
  running-text-vs-table-row labeling conflict; Appendix I's Figure I1 caption states "8 train-test
  splits" against Table 1's seven printed S-columns.

**Case completion status.** This bounded evidence-research case's completion requires Codex's independent
source and release review and merge of this prepared candidate; that review and merge have not occurred
by this process. A future, separately tracked benchmark-execution effort (rewire-benchmarks
[#29](https://github.com/rewire-bio/rewire-benchmarks/issues/29), a frozen Norman control panel with a
metric-sensitivity check and a separately registered context-transfer protocol) remains open, but is
**not** required by programme tracker rewire-benchmark-data
[#3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3)'s own research scope, which concerns
bounded evidence collection and review, not new benchmark execution. No human scientific review and no
model execution are claimed anywhere in this document or the underlying intake.

See `docs/omics/evidence-research/genetic-perturbation-response-2026-10-07.md` for the full research
dossier and source locators, and `data/omics/use-case-coverage-genetic-perturbation-20261007/` for the
intake's own reviewed records and receipt.
