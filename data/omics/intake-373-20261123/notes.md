# Intake for issue #373

Add discovered benchmark BEND 2.0: BEND 2.0: benchmark for DNA language models across prior, function, context, interaction and design

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-23. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-373-20261123-benchmark-bend-2-0` (benchmark, depth tier 1)

## Sources

- https://arxiv.org/abs/2611.03806: `intake-373-20261123-source-2611-03806-bend-2-0-benchmarking-the-capabilities-needed-to`, SHA-256 cbfed9e703c84e4c4f8011b4ac104be76368126115f47cfbb8ef6ea22f1bd84b, text/html
- https://arxiv.org/html/2611.03806: `intake-373-20261123-source-bend-2-0-benchmarking-the-capabilitiesneeded-to-design-dna`, SHA-256 ebbbe044e5d0b69bab1052c1f3f95ed8a5888e98dbd34ca4d0426e7e155a2ecf, text/html
- https://github.com/machinelearninglifescience/BEND2: `intake-373-20261123-source-github-machinelearninglifescience-bend2-benchmarking-the-cap`, SHA-256 313315840af8ea4a9ace70c6f69fc6d5327ea2a8eaba71ed76a598721bb45476, text/html
- https://huggingface.co/datasets/yhsure/BEND2: `intake-373-20261123-source-yhsure-bend2-datasets-at-hugging-face`, SHA-256 9e82e7ab94c9359ac3740da8d4af9bdb083e5503d9759e148599d0ea5208a7a2, text/html
- https://machinelearninglifescience.github.io/BEND2/: `intake-373-20261123-source-bend-2-0-benchmarking-dna-models`, SHA-256 3a754c80a8b844f1d4a1c798898426457c815708910a200df57aa1a5982acdea, text/html

## Not added

- None.

## Links

- None.

## Possible duplicates in the store

- BEND 2.0 against `discovery-benchmark-bend` ("BEND"): distinct, The stored record is the original BEND benchmark with the frederikkemarin/BEND repository and ICLR 2024 paper, and seven tasks. The arXiv HTML Introduction says BEND 2.0 builds on BEND (Marin et al., 2024). It has five capabilities and eight tasks, its own repository and data release, and shares no source address with the stored record.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| BEND 2.0 | source |   | Yes |
| BEND 2.0 | source |   | Yes |
| BEND 2.0 | source |   | Yes |
| BEND 2.0 | source |   | Yes |
| BEND 2.0 | version | 2.0 | No |
| BEND 2.0 | task | Eight tasks built on five experimental datasets | Yes |
| BEND 2.0 | scope_note | Tests how well models predict effects of DNA changes and whether these predictions guide design. | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 9650 | 5275 | 54084 | 6979 | 0 | 1 | $0.0057 |
| claude-sonnet-5-5 | 671 | 33779 | 33779 | 1773 | 0 | 0 | $0.1069 |
| Total | | | | | | | $0.1126 |
