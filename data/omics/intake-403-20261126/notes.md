# Intake for issue #403

Add discovered benchmark CellBench: CellBench: benchmark of single-cell foundation model embeddings vs classical baselines

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-26. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-403-20261126-benchmark-cellbench-ls` (benchmark, depth tier 3)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.04.01.714123v1: `intake-403-20261126-source-cellbench-ls-benchmark-evaluation-of-single-cell-foundation`, SHA-256 62942031e98040688f7d13d0a8ab278fb2d884dd0e5e3ced9a0089842ed62091, text/html
- https://www.biorxiv.org/content/10.64898/2026.04.01.714123v2: `intake-403-20261126-source-task-dependent-performance-of-single-cell-foundation-models`, SHA-256 ccba348555279f2f211ec02652a759969c339e457e2fd512623c604b7d85a244, text/html
- https://www.biorxiv.org/content/10.64898/2026.04.01.714123v3: `intake-403-20261126-source-cellbench-task-dependent-performance-and-generalization-limi`, SHA-256 b9a8b0101b3a7f217ac5a8dc19db996a6245e7956605ff362929d0855fd2ee42, text/html
- https://github.com/sky-Yongjie-Xu/2026-CellBench-J: `intake-403-20261126-source-github-sky-yongjie-xu-2026-cellbench-j-github`, SHA-256 d1e0a5f99c6b962c45efd5f7ae2216a34ce9a9b8dcd2296b2fbf60e852f58797, text/html
- https://arxiv.org/html/2602.16696: `intake-403-20261126-source-abstract`, SHA-256 44a8a4d3caf583e2e99978d35b854727d0674f8a51df5805639814174cfa6472, text/html

## Not added

- None.

## Links

- None.

## Possible duplicates in the store

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| CellBench-LS | version |   | No |
| CellBench-LS | task | Zero-shot representational evaluation of cell clustering and batch correction, and lightweight fine-tuning of task-speci | Yes |
| CellBench-LS | scope_note | Single-cell foundation models in low-supervision settings. | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 2647 | 24957 | 282140 | 8880 | 0 | 3 | $0.0532 |
| claude-haiku-5-5 | 8411 | 0 | 0 | 3178 | 0 | 0 | $0.0024 |
| claude-sonnet-5-5 | 4 | 40899 | 0 | 2010 | 0 | 0 | $0.1224 |
| Total | | | | | | | $0.1780 |
