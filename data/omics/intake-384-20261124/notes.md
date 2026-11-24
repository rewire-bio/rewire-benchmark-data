# Intake for issue #384

Add discovered model LIMBER: LIMBER: hybrid Transformer-Mamba RNA foundation model for structure and function

Added by the intake agent (`.github/workflows/intake.yml`, prompt `agents/intake.md`) on 2026-11-24. Entities only: no evaluation, result or claim was extracted. Every record has status `discovered` until an independent review.

## Records

- `intake-384-20261124-model-limber` (model, depth tier 1)

## Sources

- https://github.com/ziyaow1010/LIMBER: `intake-384-20261124-source-github-ziyaow1010-limber-github`, SHA-256 11a140f2c9ac2735797474910c879239fdcc9404f974c8b179cfb60a6f46a3b3, text/html
- https://www.biorxiv.org/content/10.64898/2026.10.28.762670v1: not opened (HTTP 429)
- https://www.biorxiv.org/content/10.64898/2026.10.28.762670v2: `intake-384-20261124-source-limber-a-hybrid-rna-foundation-model-for-predicting-and-unde`, SHA-256 0b9ec0d06397509e0887afd47b8e1a30629ff4af6f7507a15441fa2926e13ac1, text/html
- https://huggingface.co/Ziyao1010/LIMBER: `intake-384-20261124-source-ziyao1010-limber-hugging-face`, SHA-256 b9086893b6fbd36addfc3cc643995e6625492b1f826f37ab0ca8bf42db6bff8c, text/html

## Not added

- None.

## Links

- None.

## Possible duplicates in the store

- LIMBER against `catalog-model-rna-fm` ("RNA-FM"): distinct, different_resource: the stored record is RNA-FM, a separate model from the ml4bio/RNA-FM repository. The LIMBER README lists RNA-FM only as a baseline in the Results tables, and a baseline is not an alias. No shared address.
- LIMBER against `lit-microbial-20261011-virobench-model-mp-rna` ("MP-RNA"): distinct, different_resource: the store's MP-RNA is cited only to ViroBench. No LIMBER source mentions MP-RNA.
- LIMBER against `lit-rna-20261011-rnalm-zeroshot-model-mp-rna` ("MP-RNA"): distinct, different_resource: cited only to the zero-shot RNA language model benchmarking supplement. No LIMBER source mentions MP-RNA.

## Fields

Each proposed field and whether the verification pass confirmed it. An empty kept value is in `missing_metadata` with reason `unextracted`.

| Entity | Field | Proposed | Kept |
| --- | --- | --- | --- |
| LIMBER | version |   | No |
| LIMBER | access | Code at the GitHub repository ziyaow1010/LIMBER. Weights at the Hugging Face repo Ziyao1010/LIMBER, one subfolder per mo | Yes |
| LIMBER | licence |   | No |
| LIMBER | training_data | RNAcentral, exact-sequence deduplicated to 40,498,819 sequences plus a fixed held-out validation set; sequences of 1,022 | Yes |

## Cost

| Model | Input | Cache write | Cache read | Output | Web searches | Web fetches | Estimated cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 (prompt over 100k) | 2760 | 11242 | 90185 | 6219 | 0 | 3 | $0.0285 |
| claude-haiku-5-5 | 7760 | 0 | 0 | 4535 | 0 | 0 | $0.0030 |
| claude-sonnet-5-5 | 807 | 19021 | 40411 | 1878 | 0 | 0 | $0.0720 |
| Total | | | | | | | $0.1035 |
