# Review: Bůžková et al. 2026 batch, 2026-10-11

Reviewer: Claude (Opus 5.5) review agent `reviewer-gfm-a`, independent of the extractor `lit-gfm-2`. No human
review claimed. Source transcription is not reproduction.

Verdict: **pass with corrections**. All 90 printed values and 9 claims match the source. Six kinds of
descriptive error were fixed in review (38 edits, listed below). No numerical value changed. All 196 records
are `source_checked`.

## Source and hashes

| Item | SHA-256 | Check |
| --- | --- | --- |
| Pinned PDF, bioRxiv v1 (`artifacts/buzkova2026-v1.pdf.gz`, decompressed) | `9a589a2088f8466502b1035228db3e594065e984e5755c25d907471225f75c19` | Matches the source record |
| Archive `artifacts/buzkova2026-v1.pdf.gz` | `d0e35f3314c4cab758d79d0162ef52ee4e16195832a60e92f958aa45763fa081` | Matches `sources.md` |
| Fresh download, 2026-10-11, same URL | `708973e8d87cb40c85e1362cf97fba848b90951d27ea123577e0b577e728222e` | Differs in 34 bytes (per-request banner, as `sources.md` says) |
| `pdftotext -layout` (poppler 26.08.0) text of both copies | `e1a2027c0ac0f6ac14306635cc5f2301b248eecd1f5b0dcf24a142fed9a2f5ac` | Identical for the pinned and the fresh copy |

Licence: the PDF banner on every page states CC BY 4.0, so archiving the PDF is allowed.

## Method

`review/review.py` parses Tables 2, 3, 7 and 10 and the interval sentences in Sections 2.9, 3.6 and 3.8
from the text layer with its own row and column matching. It does not import the extractor. For every
result it asserts printed value, numeric value, metric concept, qualifier, unit, direction and the
evaluation's configuration, protocol and dataset. For every claim it rebuilds the value from the Table 2
row. It then applies the corrections and writes the review blocks. `review/corrections.json` lists each
edit by record ID. Run order: `extract/extract.py`, then
`python3 -I review/review.py <text layer>`.

Model identity: configurations keep the printed names (NTv1 Multispecies 2.5B, NTv2-50M/250M/500M,
NTv3-8M/100M/650M, DNABERT-2, DNABERT-S) and mark the checkpoint revision unreported; Section 2.4 names
only "official Hugging Face repositories". No checkpoint is collapsed into another. NTv1 and NTv3 link to the
Nucleotide Transformer family record and NTv2 to `catalog-model-nt-v2`, which is a family record whose
`version` field reads "50M multi-species"; that existing record is not changed here, but its version field
does not describe the 250M and 500M configurations linked to it.

## Corrections

1. **Uncertainty recorded as unreported when the text prints it.** Section 2.9 states 95% Wilson binomial
   intervals, and Sections 3.6 and 3.8 print them for five accuracy results: Table 7 33-class blastn
   (0.962 to 0.972), NTv3-650M (0.919 to 0.933), megablast (0.891 to 0.907); Table 10 NTv3-650M
   (0.920 to 0.973) and blastn (0.950 to 0.989). Added as `confidence_interval`, level 0.95, method
   `analytic`.
2. **Precision and recall qualifiers.** These 22 results had the qualifier "macro-averaged over classes"
   and lost the dataset and the "chunk-scored" marker that the other metrics of the same row carry. A
   chunk-scored DNABERT-2 precision therefore had the same qualifier as a whole-sequence NTv3-650M one. Now
   "<dataset>[, chunk-scored], macro-averaged over classes".
3. **Table 10 configuration identity.** The four foundation-model rows were linked to the Table 3
   best-pooling configurations (mean for DNABERT-2 and NTv2, max for NTv3-650M). The paper never says which
   pooling the long-sequence runs used (Sections 2.3, 2.5 and 3.8; Section 2.3 says the four models are
   the best variant of each family, not the best pooling). Four new configurations,
   `config-<model>-long-pooling-unreported`, carry `missing_metadata.representation: unreported` and the
   chunking stated in Section 2.5. The evaluations now link to them.
4. **Source conflict on chunk scoring.** Section 2.5 says chunk embeddings were pooled to a sequence-level
   representation; the Table 10 footnote and Section 4 say the three chunked rows were scored per chunk.
   Added as a limitation on the three chunked evaluations. These rows are already kept apart from the
   whole-sequence rows by their `comparison.inputs` and `aggregation`, so no source-level
   `evidence_concerns` entry was added (it would block all 90 results).
5. **Residual label redundancy.** Section 3.2 and Table 11 say ICTV reconciliation found one more redundant
   label pair inside the 33-class dataset. Added as a limitation on the 33-class protocols.
6. **Approximate total.** `data-rvdb-long` had `total: 320`; Table 1 prints "about 320". Removed and marked
   unreported with the printed wording.

## Conflicts and notes, not changed

- Table 9's unperturbed cell for NTv3-650M (0% mutation, 0% masking) prints 0.9244, while Tables 3, 6
  (ratio 1.00) and 7 print 0.9265 for the same configuration and test set. Tables 8 and 9 are not
  extracted; the extracted 0.9265 is consistent across three tables. Recorded in the review notes of the
  two affected results. Table 8's unperturbed blastn cell (0.9677) agrees with Table 7.
- The `⋆` in `⋆0.9265` (Table 3) is the printed overall-best marker; keeping it in `printed_value` is
  correct.
- `data-rvdb-40` gives "6,000 test queries"; the paper prints 150 per class and 40 classes, not the
  product. Left as is.
- `protocol-blast-compare` links `uses_data` to the 33-class dataset only, although its evaluations also
  use the 40-class dataset. Each evaluation's `data` link is correct.
- The BLAST method record `dna-pathogen-20261009-method-blast` describes alignment to NCBI nt; these
  configurations use a custom database, which their `parameters` state.

## Relevance judgements

None in the batch. I agree with the extractor's recommendation not to link
`use-case-diagnostic-dna-pathogen-identification`: the endpoint is closed-set RVDB label retrieval, not
clinical cfDNA pathogen detection against culture.

## Remaining gaps

Tables 4, 5, 6, 8, 9 and 11 and all figures are unextracted. Table 6 (PCA retention) is a complete printed
table and could be added later.

## Values checked

| Result | Locator | Printed | Metric | Unit | Outcome |
| --- | --- | --- | --- | --- | --- |
| `result-t10-blastn-accuracy` | Table 10, row 'BLAST (blastn)', column 'Accuracy' | 0.9766 | accuracy | fraction | Match; uncertainty added |
| `result-t10-blastn-bal-acc` | Table 10, row 'BLAST (blastn)', column 'Bal. Acc.' | 0.9766 | balanced-accuracy | fraction | Match |
| `result-t10-blastn-f1` | Table 10, row 'BLAST (blastn)', column 'F1' | 0.9765 | macro-f1 | fraction | Match |
| `result-t10-blastn-mcc` | Table 10, row 'BLAST (blastn)', column 'MCC' | 0.9751 | matthews-correlation-coefficient | unitless | Match |
| `result-t10-blastn-precision` | Table 10, row 'BLAST (blastn)', column 'Precision' | 0.9776 | precision | fraction | Match; qualifier corrected |
| `result-t10-blastn-recall` | Table 10, row 'BLAST (blastn)', column 'Recall' | 0.9766 | recall | fraction | Match; qualifier corrected |
| `result-t10-dnabert-2-accuracy` | Table 10, row 'DNABERT-2ᵃ', column 'Accuracy' | 0.7864 | accuracy | fraction | Match |
| `result-t10-dnabert-2-bal-acc` | Table 10, row 'DNABERT-2ᵃ', column 'Bal. Acc.' | 0.8170 | balanced-accuracy | fraction | Match |
| `result-t10-dnabert-2-f1` | Table 10, row 'DNABERT-2ᵃ', column 'F1' | 0.8127 | macro-f1 | fraction | Match |
| `result-t10-dnabert-2-mcc` | Table 10, row 'DNABERT-2ᵃ', column 'MCC' | 0.7711 | matthews-correlation-coefficient | unitless | Match |
| `result-t10-dnabert-2-precision` | Table 10, row 'DNABERT-2ᵃ', column 'Precision' | 0.8139 | precision | fraction | Match; qualifier corrected |
| `result-t10-dnabert-2-recall` | Table 10, row 'DNABERT-2ᵃ', column 'Recall' | 0.8170 | recall | fraction | Match; qualifier corrected |
| `result-t10-ntv2-250m-accuracy` | Table 10, row 'NTv2-250Mᵃ', column 'Accuracy' | 0.8306 | accuracy | fraction | Match |
| `result-t10-ntv2-250m-bal-acc` | Table 10, row 'NTv2-250Mᵃ', column 'Bal. Acc.' | 0.8443 | balanced-accuracy | fraction | Match |
| `result-t10-ntv2-250m-f1` | Table 10, row 'NTv2-250Mᵃ', column 'F1' | 0.8423 | macro-f1 | fraction | Match |
| `result-t10-ntv2-250m-mcc` | Table 10, row 'NTv2-250Mᵃ', column 'MCC' | 0.8181 | matthews-correlation-coefficient | unitless | Match |
| `result-t10-ntv2-250m-precision` | Table 10, row 'NTv2-250Mᵃ', column 'Precision' | 0.8435 | precision | fraction | Match; qualifier corrected |
| `result-t10-ntv2-250m-recall` | Table 10, row 'NTv2-250Mᵃ', column 'Recall' | 0.8443 | recall | fraction | Match; qualifier corrected |
| `result-t10-ntv2-50m-accuracy` | Table 10, row 'NTv2-50Mᵃ', column 'Accuracy' | 0.8532 | accuracy | fraction | Match |
| `result-t10-ntv2-50m-bal-acc` | Table 10, row 'NTv2-50Mᵃ', column 'Bal. Acc.' | 0.8699 | balanced-accuracy | fraction | Match |
| `result-t10-ntv2-50m-f1` | Table 10, row 'NTv2-50Mᵃ', column 'F1' | 0.8689 | macro-f1 | fraction | Match |
| `result-t10-ntv2-50m-mcc` | Table 10, row 'NTv2-50Mᵃ', column 'MCC' | 0.8423 | matthews-correlation-coefficient | unitless | Match |
| `result-t10-ntv2-50m-precision` | Table 10, row 'NTv2-50Mᵃ', column 'Precision' | 0.8705 | precision | fraction | Match; qualifier corrected |
| `result-t10-ntv2-50m-recall` | Table 10, row 'NTv2-50Mᵃ', column 'Recall' | 0.8699 | recall | fraction | Match; qualifier corrected |
| `result-t10-ntv3-650m-accuracy` | Table 10, row 'NTv3-650M', column 'Accuracy' | 0.9531 | accuracy | fraction | Match; uncertainty added |
| `result-t10-ntv3-650m-bal-acc` | Table 10, row 'NTv3-650M', column 'Bal. Acc.' | 0.9531 | balanced-accuracy | fraction | Match |
| `result-t10-ntv3-650m-f1` | Table 10, row 'NTv3-650M', column 'F1' | 0.9534 | macro-f1 | fraction | Match |
| `result-t10-ntv3-650m-mcc` | Table 10, row 'NTv3-650M', column 'MCC' | 0.9504 | matthews-correlation-coefficient | unitless | Match |
| `result-t10-ntv3-650m-precision` | Table 10, row 'NTv3-650M', column 'Precision' | 0.9583 | precision | fraction | Match; qualifier corrected |
| `result-t10-ntv3-650m-recall` | Table 10, row 'NTv3-650M', column 'Recall' | 0.9531 | recall | fraction | Match; qualifier corrected |
| `result-t3-dnabert-2-cls` | Table 3, column 'DNABERT-2', row 'CLS token only' | 0.7053 | accuracy | fraction | Match |
| `result-t3-dnabert-2-max-all` | Table 3, column 'DNABERT-2', row 'Max, all tokens' | 0.7198 | accuracy | fraction | Match |
| `result-t3-dnabert-2-max-excl` | Table 3, column 'DNABERT-2', row 'Max, special tokens excluded' | 0.7495 | accuracy | fraction | Match |
| `result-t3-dnabert-2-mean-all` | Table 3, column 'DNABERT-2', row 'Mean, all tokens' | 0.8855 | accuracy | fraction | Match |
| `result-t3-dnabert-2-mean-excl` | Table 3, column 'DNABERT-2', row 'Mean, special tokens excluded' | 0.8848 | accuracy | fraction | Match |
| `result-t3-dnabert-s-cls` | Table 3, column 'DNABERT-S', row 'CLS token only' | 0.7713 | accuracy | fraction | Match |
| `result-t3-dnabert-s-max-all` | Table 3, column 'DNABERT-S', row 'Max, all tokens' | 0.7907 | accuracy | fraction | Match |
| `result-t3-dnabert-s-max-excl` | Table 3, column 'DNABERT-S', row 'Max, special tokens excluded' | 0.8000 | accuracy | fraction | Match |
| `result-t3-dnabert-s-mean-all` | Table 3, column 'DNABERT-S', row 'Mean, all tokens' | 0.8735 | accuracy | fraction | Match |
| `result-t3-dnabert-s-mean-excl` | Table 3, column 'DNABERT-S', row 'Mean, special tokens excluded' | 0.8733 | accuracy | fraction | Match |
| `result-t3-ntv1-cls` | Table 3, column 'NTv1', row 'CLS token only' | 0.8655 | accuracy | fraction | Match |
| `result-t3-ntv1-max-all` | Table 3, column 'NTv1', row 'Max, all tokens' | 0.9030 | accuracy | fraction | Match |
| `result-t3-ntv1-max-excl` | Table 3, column 'NTv1', row 'Max, special tokens excluded' | 0.9028 | accuracy | fraction | Match |
| `result-t3-ntv1-mean-all` | Table 3, column 'NTv1', row 'Mean, all tokens' | 0.9109 | accuracy | fraction | Match |
| `result-t3-ntv1-mean-excl` | Table 3, column 'NTv1', row 'Mean, special tokens excluded' | 0.9097 | accuracy | fraction | Match |
| `result-t3-ntv2-250m-cls` | Table 3, column 'NTv2-250M', row 'CLS token only' | 0.7651 | accuracy | fraction | Match |
| `result-t3-ntv2-250m-max-all` | Table 3, column 'NTv2-250M', row 'Max, all tokens' | 0.8343 | accuracy | fraction | Match |
| `result-t3-ntv2-250m-max-excl` | Table 3, column 'NTv2-250M', row 'Max, special tokens excluded' | 0.8331 | accuracy | fraction | Match |
| `result-t3-ntv2-250m-mean-all` | Table 3, column 'NTv2-250M', row 'Mean, all tokens' | 0.9103 | accuracy | fraction | Match |
| `result-t3-ntv2-250m-mean-excl` | Table 3, column 'NTv2-250M', row 'Mean, special tokens excluded' | 0.9099 | accuracy | fraction | Match |
| `result-t3-ntv2-500m-cls` | Table 3, column 'NTv2-500M', row 'CLS token only' | 0.7451 | accuracy | fraction | Match |
| `result-t3-ntv2-500m-max-all` | Table 3, column 'NTv2-500M', row 'Max, all tokens' | 0.8701 | accuracy | fraction | Match |
| `result-t3-ntv2-500m-max-excl` | Table 3, column 'NTv2-500M', row 'Max, special tokens excluded' | 0.8731 | accuracy | fraction | Match |
| `result-t3-ntv2-500m-mean-all` | Table 3, column 'NTv2-500M', row 'Mean, all tokens' | 0.9063 | accuracy | fraction | Match |
| `result-t3-ntv2-500m-mean-excl` | Table 3, column 'NTv2-500M', row 'Mean, special tokens excluded' | 0.9059 | accuracy | fraction | Match |
| `result-t3-ntv2-50m-cls` | Table 3, column 'NTv2-50M', row 'CLS token only' | 0.7584 | accuracy | fraction | Match |
| `result-t3-ntv2-50m-max-all` | Table 3, column 'NTv2-50M', row 'Max, all tokens' | 0.8673 | accuracy | fraction | Match |
| `result-t3-ntv2-50m-max-excl` | Table 3, column 'NTv2-50M', row 'Max, special tokens excluded' | 0.8667 | accuracy | fraction | Match |
| `result-t3-ntv2-50m-mean-all` | Table 3, column 'NTv2-50M', row 'Mean, all tokens' | 0.9133 | accuracy | fraction | Match |
| `result-t3-ntv2-50m-mean-excl` | Table 3, column 'NTv2-50M', row 'Mean, special tokens excluded' | 0.9127 | accuracy | fraction | Match |
| `result-t3-ntv3-100m-max-all` | Table 3, column 'NTv3-100M', row 'Max, all tokens' | 0.8271 | accuracy | fraction | Match |
| `result-t3-ntv3-100m-mean-all` | Table 3, column 'NTv3-100M', row 'Mean, all tokens' | 0.9174 | accuracy | fraction | Match |
| `result-t3-ntv3-650m-max-all` | Table 3, column 'NTv3-650M', row 'Max, all tokens' | ⋆0.9265 | accuracy | fraction | Match |
| `result-t3-ntv3-650m-mean-all` | Table 3, column 'NTv3-650M', row 'Mean, all tokens' | 0.6745 | accuracy | fraction | Match |
| `result-t3-ntv3-8m-max-all` | Table 3, column 'NTv3-8M', row 'Max, all tokens' | 0.8210 | accuracy | fraction | Match |
| `result-t3-ntv3-8m-mean-all` | Table 3, column 'NTv3-8M', row 'Mean, all tokens' | 0.6509 | accuracy | fraction | Match |
| `result-t7-33-blastn-accuracy` | Table 7, row '33 classes / blastn', column 'Accuracy' | 0.9677 | accuracy | fraction | Match; uncertainty added |
| `result-t7-33-blastn-f1` | Table 7, row '33 classes / blastn', column 'F1' | 0.9379 | macro-f1 | fraction | Match |
| `result-t7-33-blastn-precision` | Table 7, row '33 classes / blastn', column 'Precision' | 0.9401 | precision | fraction | Match; qualifier corrected |
| `result-t7-33-blastn-recall` | Table 7, row '33 classes / blastn', column 'Recall' | 0.9392 | recall | fraction | Match; qualifier corrected |
| `result-t7-33-megablast-accuracy` | Table 7, row '33 classes / megablast', column 'Accuracy' | 0.8994 | accuracy | fraction | Match; uncertainty added |
| `result-t7-33-megablast-f1` | Table 7, row '33 classes / megablast', column 'F1' | 0.8989 | macro-f1 | fraction | Match |
| `result-t7-33-megablast-precision` | Table 7, row '33 classes / megablast', column 'Precision' | 0.9600 | precision | fraction | Match; qualifier corrected |
| `result-t7-33-megablast-recall` | Table 7, row '33 classes / megablast', column 'Recall' | 0.8729 | recall | fraction | Match; qualifier corrected |
| `result-t7-33-ntv3-650m-max-accuracy` | Table 7, row '33 classes / NTv3-650M (max)', column 'Accuracy' | 0.9265 | accuracy | fraction | Match; uncertainty added |
| `result-t7-33-ntv3-650m-max-f1` | Table 7, row '33 classes / NTv3-650M (max)', column 'F1' | 0.9249 | macro-f1 | fraction | Match |
| `result-t7-33-ntv3-650m-max-precision` | Table 7, row '33 classes / NTv3-650M (max)', column 'Precision' | 0.9263 | precision | fraction | Match; qualifier corrected |
| `result-t7-33-ntv3-650m-max-recall` | Table 7, row '33 classes / NTv3-650M (max)', column 'Recall' | 0.9265 | recall | fraction | Match; qualifier corrected |
| `result-t7-40-blastn-accuracy` | Table 7, row '40 classes / blastn', column 'Accuracy' | 0.9120 | accuracy | fraction | Match |
| `result-t7-40-blastn-f1` | Table 7, row '40 classes / blastn', column 'F1' | 0.8886 | macro-f1 | fraction | Match |
| `result-t7-40-blastn-precision` | Table 7, row '40 classes / blastn', column 'Precision' | 0.8925 | precision | fraction | Match; qualifier corrected |
| `result-t7-40-blastn-recall` | Table 7, row '40 classes / blastn', column 'Recall' | 0.8898 | recall | fraction | Match; qualifier corrected |
| `result-t7-40-megablast-accuracy` | Table 7, row '40 classes / megablast', column 'Accuracy' | 0.8490 | accuracy | fraction | Match |
| `result-t7-40-megablast-f1` | Table 7, row '40 classes / megablast', column 'F1' | 0.8512 | macro-f1 | fraction | Match |
| `result-t7-40-megablast-precision` | Table 7, row '40 classes / megablast', column 'Precision' | 0.9064 | precision | fraction | Match; qualifier corrected |
| `result-t7-40-megablast-recall` | Table 7, row '40 classes / megablast', column 'Recall' | 0.8283 | recall | fraction | Match; qualifier corrected |
| `result-t7-40-ntv3-650m-max-accuracy` | Table 7, row '40 classes / NTv3-650M (max)', column 'Accuracy' | 0.8750 | accuracy | fraction | Match |
| `result-t7-40-ntv3-650m-max-f1` | Table 7, row '40 classes / NTv3-650M (max)', column 'F1' | 0.8735 | macro-f1 | fraction | Match |
| `result-t7-40-ntv3-650m-max-precision` | Table 7, row '40 classes / NTv3-650M (max)', column 'Precision' | 0.8744 | precision | fraction | Match; qualifier corrected |
| `result-t7-40-ntv3-650m-max-recall` | Table 7, row '40 classes / NTv3-650M (max)', column 'Recall' | 0.8750 | recall | fraction | Match; qualifier corrected |
