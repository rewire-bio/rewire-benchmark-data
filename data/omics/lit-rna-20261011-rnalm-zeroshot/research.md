# Research notes

Part of the 2026-10-11 RNA and other-omics literature pass (window 2025-10-01 to 2026-10-11). The search log is in `data/omics/lit-search-20261011-rna-otheromics/ledger.jsonl`.

## Why this source

Wang et al. 2026 (Briefings in Bioinformatics, bbag098, CC BY) is the largest independent zero-shot comparison of RNA language models found in the window: 21 RNA LMs, with DNABERT, DNABERT-2, Nucleotide Transformer and Evo as controls, on three tasks with no fine-tuning. None of these models or tasks were in the store from this source.

## Record counts

- benchmark: 1
- configuration: 40
- dataset: 5
- evaluation: 1190
- model: 14
- protocol: 36
- result: 1190
- source: 2

## Extraction notes

- Every cell of Supplementary Tables 4-11. Tables 4, 5, 10 and 11 print a median and a 'Mean ± Std' per metric; each is a separate result with its own protocol (median or mean). Tables 6-9 print 'mean ± std' over repeated random samplings of sequence pairs; the std is recorded as a standard deviation with that scope.
- Directions come from the Methods: higher is better for F1, MCC, AUC, 1 - OR and |Spearman|. The header arrows are lost in the .docx symbol font.
- New metric concept `one-minus-overlap-ratio` (added to `data/vocab/metric.ttl`) for the '1 − OR' column; the definition follows the supplement's 'Calculation of the overlap ratio (OR)'.
- 'SR' is the absolute Spearman correlation (Methods: 'the absolute value of the Spearman correlation coefficient (SR)'), recorded as `absolute-spearman-correlation`.
- Starred rows (sequences longer than 440 or 512 nt excluded) carry the exclusion in the evaluation's comparison population.
- Origin: RNA-MSM is from the corresponding authors' group and is `author_reported`; all other models are `independent_paper`.
- Model families reused from the store: RNA-FM (`discovery-model-rna-fm`), RNA-MSM, RNABERT, RNAErnie, SpliceBERT, UTR-LM and DNABERT (You et al. 2026 batch), DNABERT-2 (`discovery-model-dnabert-2`), Nucleotide Transformer v2 (`catalog-model-nt-v2`), LucaOne and Evo (GENEB batch; Evo 1 and Evo 1.5 are configurations of that family). Fourteen new family records were created for RNA LMs not in the store (AIDO.RNA, RiNALMo, ERNIE-RNA, Uni-RNA and others). The store also holds pipeline records named ERNIE-RNA and RiNALMo from mRNABench batches; they were not reused because they are pipeline-specific.
- Configuration versions are the variant labels printed in the results tables, with the Supplementary Table 1 download URL, date and version column in `checkpoint`.
