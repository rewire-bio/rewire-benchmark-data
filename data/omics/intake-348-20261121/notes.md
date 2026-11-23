# Intake for issue #348

Add discovered model scRM: scRM: single-cell embeddings directly from raw FASTQ reads

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-21. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-348-20261121-model-scrm` (model, depth tier 3)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.10.24.761590v2: not opened (HTTP 429)
- https://github.com/altoslabs/scRM: `intake-348-20261121-source-github-altoslabs-scrm-github`, SHA-256 fa42a279823c092798a0cad910b9a7c23f15de253775fb17f96c684a41697a27, text/html

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
| scRM | version |   | No |
| scRM | access | Pipeline public at github.com/altoslabs/scRM; weights not confirmed; baseline weights not redistributed | Yes |
| scRM | licence | MIT (code, per issue text only); weights licence empty | Yes |
| scRM | training_data |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 9165 | 10438 | 27495 | 6474 | 0 | 3 | $0.0057 |
| claude-sonnet-5-5 | 4 | 19474 | 0 | 1856 | 0 | 0 | $0.0673 |
| Total | | | | | | | $0.0730 |
