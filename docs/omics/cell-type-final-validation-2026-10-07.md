# Cell-type supplement intake validation, 7 October 2026

Reviewed release: `2026-10-07-e11db1d1c586`, timestamp `2026-10-07T08:35:35.000Z`. Adds 23 records, nine source-checked results, and one proxy mapping from the independently inspected Abdelaal Figure S10B supplement. No model was executed.

| Check | Result |
| --- | --- |
| Source archive | Decompressed PDF SHA-256 `797a2b22f584135f4ff6f7c98203d8e9529d6600f675b500205607b47b212a81`, matching the independent primary-source download |
| Review receipts | All 22 declared file hashes match; use-case inputs receipt matches; new mapping fingerprint checked |
| Prior catalogue preservation | All 28,202 records in release `2026-10-06-161b59a1d02c` compare equal by ID; exactly 23 records added |
| Prior use cases and mappings | All 17 definitions and 70 prior mapping objects preserved |
| Full tests | 553 tests validated: full SSD run passed 552, and the single IPC temporary-path failure passed in its 11-test file rerun with a shorter SSD TMPDIR |
| Type checking | Passed |
| Python tests | 6 passed |
| Archive extraction audit | 6,163 original source files verified |
| Full release build | Release, literature validation/export, refresh export completed; prepared packaging resumed successfully after the interruption |
| Prepared package | 8,351 tracked sources verified |
| Clean historical restoration | Full build started with empty public/omics; independently recomputed 8,240 manifest checksums across 30 restored releases, zero mismatches |
| Prior prepared archive bytes | All 7,911 prior release/baseline entries retain source, destination, SHA-256 and size; prior current release becomes historical |
| Diff validation | Passed; no earlier scientific archive changed |

The first full test attempt encountered internal-disk ENOSPC while creating temporary copies. The SSD rerun encountered one tsx IPC socket-path-length failure because TMPDIR was too long; the failed file passed with `/Volumes/Extreme SSD/rewire-test-tmp`. These were environment failures and required no source changes. Future local tests should use that short external TMPDIR.

The pre-existing full extraction migration-receipt mismatch for release-config.json remains outside this intake; archives-only verification is the CI gate and passes. No historic migration receipt was rewritten.

Scope limitations remain explicit in the records and dossier: percentage unlabeled is context dependent, scored denominators are unreported, and independent-study holdout cannot be inferred for every VISp/ALM/MTG combination. Source conflicts and version/access limitations in other papers remain recorded. The existing benchmark-gap issue #27 concerns separate follow-on execution.
