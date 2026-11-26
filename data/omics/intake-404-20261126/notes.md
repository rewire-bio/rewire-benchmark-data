# Intake for issue #404

Add discovered model MirrorDNA: MirrorDNA: strand-equivariant learned DNA tokenizer language model

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-26. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-404-20261126-model-mirrordna` (model, depth tier 1)

## Sources

- https://github.com/NIRJHOR-DATTA/MirrorDNA: `intake-404-20261126-source-github-nirjhor-datta-mirrordna-github`, SHA-256 f52ad8d85bb2396778a6b359a092e39c1ce98235fe6bb95178493f554a79a9c3, text/html
- https://www.biorxiv.org/content/10.64898/2026.11.04.764207v1: `intake-404-20261126-source-learning-strand-equivariant-tokenizations-of-dna-with-mirror`, SHA-256 258f18339b33f662d8663fa4d6a9686fe6d59c63f510bba0c3a30f61891e9103, text/html
- https://huggingface.co/nirjhor123/mirrordna-duplex: `intake-404-20261126-source-nirjhor123-mirrordna-duplex-hugging-face`, SHA-256 dd36cc57f47ebbc2fa5e21da274170057795c00f1e3d3557bedc0138fe558b01, text/html
- https://huggingface.co/nirjhor123/chunker-rcaug: `intake-404-20261126-source-nirjhor123-chunker-rcaug-hugging-face`, SHA-256 04f44382fa7790a977cf02d4909a846ee192b3f78d0925e275a395b6f4219cc3, text/html

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
| MirrorDNA | source | https://huggingface.co/nirjhor123/mirrordna-duplex | No |
| MirrorDNA | source | https://huggingface.co/nirjhor123/chunker-rcaug | No |
| MirrorDNA | version |   | No |
| MirrorDNA | access | GitHub repository https://github.com/NIRJHOR-DATTA/MirrorDNA; Hugging Face checkpoint pages https://huggingface.co/nirjh | Yes |
| MirrorDNA | licence | Code MIT, per issue text only; weights licence not verified | Yes |
| MirrorDNA | training_data |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 9755 | 3598 | 39672 | 6241 | 0 | 3 | $0.0049 |
| claude-sonnet-5-5 | 4 | 11107 | 10695 | 1995 | 0 | 0 | $0.0488 |
| Total | | | | | | | $0.0537 |
