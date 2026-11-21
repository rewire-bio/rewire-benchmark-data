# Intake for issue #347

Add discovered method Multi-Peptide Prompting (MPEPs): Training-free peptide classification via multi-peptide prompts in protein LMs

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-21. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-347-20261121-method-multi-peptide-prompting-mpeps` (method, depth tier 2)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.08.26.747074v2: not opened (HTTP 429)
- https://www.biorxiv.org/content/10.64898/2026.08.26.747074v2.full: not opened (HTTP 429)
- https://github.com/thiedelab/peptide_icl: `intake-347-20261121-source-github-thiedelab-peptide-icl-in-context-learning-for-peptide`, SHA-256 a06c50849edb0db5dc1113ece48ecb5cdefe11b2c1de3f57d0c21b2cdb24f6dd, text/html

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
| Multi-Peptide Prompting (MPEPs) | version |   | No |
| Multi-Peptide Prompting (MPEPs) | access | Code at thiedelab/peptide_icl per issue text (unverified); no weights released per issue text (unverified). | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 9037 | 11420 | 29407 | 6834 | 0 | 3 | $0.0060 |
| claude-sonnet-5-5 | 4 | 12283 | 0 | 1458 | 0 | 0 | $0.0453 |
| Total | | | | | | | $0.0513 |
