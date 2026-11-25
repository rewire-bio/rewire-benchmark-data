# Intake for issue #396

Add discovered model USM-AA: Genomic FM pretraining for sparse, non-contiguous DNA inputs

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-25. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-396-20261125-model-usm-aa` (model, depth tier 1)
- `intake-396-20261125-model-usm-aa-100m` (model, depth tier 1)
- `intake-396-20261125-model-usm-aa-1b` (model, depth tier 1)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.10.10.757278v1: `intake-396-20261125-source-alignment-aware-genomic-coordinate-encoding-for-long-range-d`, SHA-256 c807028f171834ec192fe914e2587b48f96d12fd1f2c79ff7229b50a4d49eed8, text/html
- https://github.com/Jimmy0743/USM-AA: `intake-396-20261125-source-github-jimmy0743-usm-aa-usm-aa-github`, SHA-256 d6e8d6bba81099eb76345f6379f251a1b4b8598ce818cf11b821144ce6962c27, text/html
- https://www.biorxiv.org/content/10.64898/2026.10.10.757278v2: `intake-396-20261125-source-alignment-aware-genomic-coordinate-encoding-for-long-range-d-2`, SHA-256 b5ffd5f29e94ddd8222248a3e248bcf2eeb9cf264da236a762ff2c9ee732bd8c, text/html

## Not added

- None.

## Links

- `intake-396-20261125-model-usm-aa-100m` family `intake-396-20261125-model-usm-aa` (USM-AA), in this batch: README Download Pretrained Models lists USM-AA 100M as a model of USM-AA
- `intake-396-20261125-model-usm-aa-1b` family `intake-396-20261125-model-usm-aa` (USM-AA), in this batch: README Download Pretrained Models lists USM-AA 1B as a model of USM-AA

## Possible duplicates in the store

- USM-AA-1B against `uc20260930-model-esm-1b` ("ESM-1b"): distinct, README Overview: USM-AA-1B is a DNA model pretrained on GRCh38, 1000 Genomes and multi-species genomes; ESM-1b is a protein language model. The match on 1B is only in the name.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| USM-AA | source |   | Yes |
| USM-AA | version |   | No |
| USM-AA | access | Source code at https://github.com/Jimmy0743/USM-AA (README, Installation section). Pretrained weights are downloaded fro | Yes |
| USM-AA | licence | PolyForm Noncommercial License 1.0.0 | Yes |
| USM-AA | training_data | Human reference genome hg38 (about 3.2 Gbp), the DNABERT2 multi-species corpus (about 32.5 Gbp from 135 species), and 10 | Yes |
| USM-AA-100M | version |   | No |
| USM-AA-100M | access | Google Drive file linked from the README Download Pretrained Models table, fetched by bash models/download.sh 100m (abou | Yes |
| USM-AA-100M | licence |   | No |
| USM-AA-100M | training_data |   | No |
| USM-AA-1B | version |   | No |
| USM-AA-1B | access | Google Drive file linked from the README Download Pretrained Models table, fetched by bash models/download.sh 1b (about  | Yes |
| USM-AA-1B | licence |   | No |
| USM-AA-1B | training_data |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 2546 | 20403 | 196019 | 8100 | 0 | 3 | $0.0441 |
| claude-haiku-5-5 | 8632 | 0 | 0 | 5993 | 0 | 0 | $0.0039 |
| claude-sonnet-5-5 | 4 | 11424 | 10695 | 1897 | 0 | 0 | $0.0486 |
| Total | | | | | | | $0.0965 |
