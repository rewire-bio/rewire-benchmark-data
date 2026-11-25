# Intake for issue #371

Add discovered model structRFM: Structure-guided RNA foundation model for RNA representation and structure prediction

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-23. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-371-20261123-model-structrfm` (model, depth tier 1)
- `intake-371-20261123-dataset-rnacentral-512-ss-connects` (dataset)

## Sources

- https://github.com/heqin-zhu/structRFM: `intake-371-20261123-source-github-heqin-zhu-structrfm-structrfm-an-open-structure-guide`, SHA-256 718c61eedb78ef0e623f808e6e248eadd7028939d0728592afb257192e826c22, text/html
- https://huggingface.co/heqin-zhu/structRFM: `intake-371-20261123-source-heqin-zhu-structrfm-hugging-face`, SHA-256 2d346e1478f3173e29f67ec60cfc2c5312fd5d08d566098d5ef695cce14b346e, text/html
- https://www.biorxiv.org/content/10.1101/2025.08.06.668731v3: not opened (HTTP 429)
- https://doi.org/10.5281/zenodo.16754363: `intake-371-20261123-source-data-and-checkpoints-for-structrfm-zenodo`, SHA-256 c00fbc15ac940c13588b3e873898577e6ab5bd9ab5006f46e1367c60a231bfdb, text/html
- https://www.nature.com/articles/s41586-026-11210-2: `intake-371-20261123-source-client-challenge`, SHA-256 32ed63159c77e21ee19ca1b9aa3213ccf0218eb59539560b132a8e68ef0e18ea, text/html

## Not added

- None.

## Links

- None.

Proposed but not written:

- structRFM family nabench-method-structrfm: not supported at a location in a source
- structRFM variant_of nabench-method-structrfm: not supported at a location in a source
- structRFM alias_of nabench-method-structrfm: not supported at a location in a source
- structRFM uses_data e2: not supported at a location in a source

## Possible duplicates in the store

- structRFM against `lit-rna-20261011-rnalm-zeroshot-model-uni-rna` ("Uni-RNA"): distinct, Stored description describes Uni-RNA RNA foundation model (L8, L12 and L16 checkpoints), a different model from a zero-shot benchmarking supplement, not the structRFM sources.
- structRFM pre-training sequence-structure dataset against `reported-dataset-6212e779949708` ("Liu training dataset"): distinct, Stored source is a paper on a BERT model for enhancers and their strength, with no description and no shared address with the RNAcentral and BPfold data.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| structRFM | source |   | Yes |
| structRFM | version |   | No |
| structRFM | access | Code: GitHub repository https://github.com/heqin-zhu/structRFM (also on PyPI as structRFM). Pre-trained weights: GitHub  | Yes |
| structRFM | licence | MIT for code; weights licence not stated | Yes |
| structRFM | training_data | About 21 million RNAcentral-derived sequence-structure pairs (sequences filtered to 512 nt); structure source MUSES ense | Yes |
| structRFM pre-training sequence-structure dataset | name | structRFM pre-training sequence-structure dataset | Yes |
| structRFM pre-training sequence-structure dataset | version |   | No |
| structRFM pre-training sequence-structure dataset | access |   | Yes |
| structRFM pre-training sequence-structure dataset | species |   | No |
| structRFM pre-training sequence-structure dataset | scope_note |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 3154 | 20338 | 258190 | 9322 | 0 | 3 | $0.0505 |
| claude-haiku-5-5 | 10694 | 0 | 0 | 6849 | 0 | 0 | $0.0045 |
| claude-sonnet-5-5 | 1951 | 10213 | 31603 | 3619 | 0 | 0 | $0.0688 |
| Total | | | | | | | $0.1238 |

## Revision after review

- `intake-371-20261123-model-structrfm` description: dropped the 'and accepts sequences up to 512 nt' clause.
