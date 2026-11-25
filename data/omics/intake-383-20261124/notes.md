# Intake for issue #383

Add discovered model LncRFM: Long non-coding RNA foundation model, corpus and benchmark

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-24. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-383-20261124-model-lncrfm` (model, depth tier 1)
- `intake-383-20261124-benchmark-lncbench` (benchmark, depth tier 1)
- `intake-383-20261124-dataset-lnccorpus` (dataset)

## Sources

- https://www.biorxiv.org/content/10.64898/2026.11.20.768117v1: not opened (HTTP 429)
- https://github.com/chuyhu/LncRFM: `intake-383-20261124-source-github-chuyhu-lncrfm-lncrfm-github`, SHA-256 6dc8d420d97585f6794d70e6687bfb064370893ec0d5dc2f7888a72492b5a160, text/html
- https://zenodo.org/records/24356997: `intake-383-20261124-source-lncrfm-pretrained-model-weights-300-000-steps-zenodo`, SHA-256 db26ac717f3ae88a1a11cb450cdeac798c26890c253a3f9f7c8bb6b265bf560d, text/html
- https://zenodo.org/records/24345986: `intake-383-20261124-source-lncbench-zenodo`, SHA-256 0111bec47c046678598b8faef7efe825ab134d5a7db1b56644a6c7aa1bfa79d6, text/html
- https://zenodo.org/records/24344559: `intake-383-20261124-source-lnccorpus-zenodo`, SHA-256 e39cc7c988ab6eb099adaeee2288471e5d32289aa3e0aefab48810ecb2c485a0, text/html

## Not added

- None.

## Links

- None.

Proposed but not written:

- LncBench uses_data e3: not supported at a location in a source

## Possible duplicates in the store

- None.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| LncRFM | version |   | Yes |
| LncRFM | access | Code in the GitHub repository chuyhu/LncRFM; weights on Zenodo 24356997 linked from the README. Access terms not read. | Yes |
| LncRFM | licence |   | No |
| LncRFM | training_data | LncCorpus, described as 9.6 million lncRNA sequences within a 24.7 million sequence pretraining corpus. Pretraining data | Yes |
| LncBench | version |   | Yes |
| LncBench | task | Downstream prediction on lncRNA sequences, 10 tasks, 15 datasets, over 1,010,000 sequences. Two of the 15 datasets allow | Yes |
| LncBench | scope_note | Would use the underlying data of LncCorpus. Whether Zenodo 24345986 is the dataset or the benchmark has not been checked | No |
| LncCorpus | version |   | Yes |
| LncCorpus | access | Via Zenodo 24344559 | Yes |
| LncCorpus | species |   | No |
| LncCorpus | scope_note |   | No |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | 11398 | 12063 | 31335 | 11696 | 0 | 3 | $0.0088 |
| claude-sonnet-5-5 | 4 | 21655 | 0 | 5571 | 0 | 0 | $0.1099 |
| Total | | | | | | | $0.1187 |

## Revision after review

The reviewer agent requested changes (https://github.com/rewire-bio/rewire-benchmark-data/pull/387#pullrequestreview-6046029119). The intake agent revised the batch once; it changes only the fields the review did not pass, and it does not revise again.

- `intake-383-20261124-model-lncrfm` training_data: dropped the value.
