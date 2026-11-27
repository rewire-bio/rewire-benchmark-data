# Intake for issue #466

Add discovered model MGM2: MGM2: microbial community foundation model with OTU sequence embeddings

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-27. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-466-20261127-model-mgm2` (model, depth tier 3)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.07.20.739063v2: not opened (HTTP 429)
- https://pypi.org/project/microformer-mgm2/: `intake-466-20261127-source-microformer-mgm2-pypi`, SHA-256 5657234ec32f6be033484752da73e1663f93b40b0207de6f2773ea1c82d12fdd, text/html
- https://github.com/HUST-NingKang-Lab/MGM2: `intake-466-20261127-source-github-hust-ningkang-lab-mgm2-github`, SHA-256 a62841f866790c2f1db6fb3f7e31ee3987f4eaa7b559129dd663db3eea6919c5, text/html

## Not added

- None.

## Links

- None.

## Possible duplicates in the store

- MGM2 against `lit-genomics-20261011-geneb-model-gpt-2-gene-models` ("GPT-2 gene models"): distinct, A different resource (a GPT-2 gene model family) with no connection to MGM2 in the sources; the shared word is only the name fragment 'model'. Ruling rests on names and sources, not the stored record.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| MGM2 | source |   | Yes |
| MGM2 | version | 2.1.1 | Yes |
| MGM2 | access | PyPI package microformer-mgm2 (pip install, version 2.1.1; import name mgm2); pretrained encoders downloaded from Huggin | Yes |
| MGM2 | licence | MIT for code, per the PyPI licence section; weights licence not stated | Yes |
| MGM2 | training_data | MicrobeAtlas, 1,821,291 samples comprising 225,067 OTUs clustered at 99% sequence similarity; OTU sequence embeddings fr | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 2947 | 17834 | 179798 | 6334 | 0 | 3 | $0.0374 |
| claude-haiku-5-5 | 7656 | 0 | 0 | 2843 | 0 | 0 | $0.0022 |
| claude-sonnet-5-5 | 4 | 9552 | 10695 | 1628 | 0 | 0 | $0.0412 |
| Total | | | | | | | $0.0809 |
