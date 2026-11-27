# Intake for issue #464

Add discovered model AlphaGenome 2: Conditional DNA effect prediction for cell states from sequence and single-cell data

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-27. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-464-20261127-model-alphagenome-2` (model, depth tier 1)

## Sources

- https://deepmind.google/blog/alphagenome-2-deciphering-how-cells-read-dna-to-better-understand-disease/: `intake-464-20261127-source-alphagenome-2-deciphering-how-cells-read-dna-to-better-under`, SHA-256 123f806f00887e30ac7fb1725db2e30435722a04823aaeca35b6339d7e19841f, text/html
- https://www.alphagenomedocs.com/: `intake-464-20261127-source-alphagenome-documentation-8212-alphagenome`, SHA-256 a76853a0b960d5f81e091c06c368bd2bfd8183b424f25eb54fddfed97b4fdd2b, text/html
- https://www.alphagenomedocs.com/user_guides/ag1_vs_ag2.html: `intake-464-20261127-source-migrating-from-alphagenome-1-8212-alphagenome`, SHA-256 717357b5f5ddf55029fb2e320638a8038d29bbbeacd9a0a72f0fe989fd3d36b0, text/html
- https://www.biorxiv.org/content/10.64898/2026.11.11.765857: not opened (HTTP 429)

## Not added

- None.

## Links

- None.

Proposed but not written:

- AlphaGenome 2 variant_of catalog-model-alphagenome: not supported at a location in a source
- AlphaGenome 2 family catalog-model-alphagenome: not supported at a location in a source
- AlphaGenome 2 alias_of catalog-model-alphagenome: not supported at a location in a source

## Possible duplicates in the store

- AlphaGenome 2 against `catalog-model-alphagenome` ("AlphaGenome"): distinct, Docs home page cards list AlphaGenome 1 as the original model and AlphaGenome 2 as a separate latest model. The migration guide (ag1_vs_ag2.html, 'When to use each model' and 'Output types') describes different architectures and outputs: AlphaGenome 2 is conditional and adds methylation and single-cell outputs, while AlphaGenome 1 predicts all tissues in parallel and includes PRO-cap. The store description covers AlphaGenome 1 only ('expression, splicing, chromatin and contact maps'). Ground: different_resource.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| AlphaGenome 2 | source | https://www.biorxiv.org/content/10.64898/2026.11.11.765857 | No |
| AlphaGenome 2 | version | 2.0.0 | No |
| AlphaGenome 2 | access | API with quota (unverified lead) | Yes |
| AlphaGenome 2 | licence |   | No |
| AlphaGenome 2 | training_data |   | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 10849 | 12228 | 31750 | 8380 | 0 | 3 | $0.0071 |
| claude-sonnet-5-5 | 283 | 21622 | 21622 | 2126 | 0 | 0 | $0.0780 |
| Total | | | | | | | $0.0852 |
