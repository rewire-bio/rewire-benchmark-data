# Review: You et al. 2026 batch, 2026-10-11

Reviewer: Claude (Opus 5.5) review agent `reviewer-gfm-a`, independent of the extractor `lit-gfm-2`. No human
review claimed. Source transcription is not reproduction.

Verdict: **pass with corrections, 22 results rejected**. All 176 printed values and spreads match
Supplementary Tables 4 and 5. Of these, 154 are accepted. The 22 "Average Top-k" results are rejected and
moved to `data/omics/pending-review/gfm2-20261011-you2026-topk/`: the source's definition of top-k accuracy
does not match the metric concept they were given. Several descriptive errors were fixed (listed below),
and two duplicate family records were removed. No numerical value changed. 242 records remain, all
`source_checked`.

## Sources and hashes

| Item | SHA-256 | Check |
| --- | --- | --- |
| Article, Europe PMC PMC12780105 full-text XML, fresh download | `2c6b2816846a21296c56b4dd58f3d1e8810e9d96e224d3ab21b5eb8faa9928e4` | Matches the source record |
| `41467_2025_66899_MOESM1_ESM.pdf` from a fresh supplementaryFiles zip | `cbb69e05045a4526e35479d2c1361ebb9cfadfd968e00675390dad597035d882` | Matches the supplement source record |
| Its `pdftotext -layout` (poppler 26.08.0) text | `4a54c8b1acbb475db01d8768b4ff7279a9b503714b395738496d6f817127308e` | Matches `sources.md` |

The outer zip differed in size from the extractor's copies (6,929,975 bytes), as `sources.md` says it
would: the zip is assembled per request. Licence: CC BY-NC-ND 4.0. No copy of either artifact is committed,
which is correct.

## Method

`review/review.py` parses Supplementary Tables 4 and 5 from the supplement text (the captions sit below
their tables, and the script uses them as boundaries). It reads the article XML for Table 1, the Methods
and the reference list. It does not import the extractor. For every result it asserts printed value,
numeric value, spread, n, metric, unit, direction, locator and the evaluation's configuration, protocol and
dataset. Then it applies the corrections. `review/corrections.json` lists each edit by record ID. Run
order: `extract/extract.py`, then `python3 -I review/review.py <supplement text> <article XML>`.

## Rejected

**22 "Average Top-k" results** (Supplementary Table 5). They were recorded as `splice-top-k-accuracy`,
which the vocabulary defines as SpliceAI-style top-k accuracy with k equal to the number of true sites. The
source defines top-k accuracy as "the fraction of times the true label is among the top k predicted labels"
(Methods). It never states k or the averaging over categories. The values are transcribed correctly; the
concept is not supported. See the pending-review README for what would bring them back.

## Corrections

1. **SpTransformer is the authors' own method.** Reference 12 is You, N. et al. 2024, "SpliceTransformer
   predicts tissue-specific splicing linked to human diseases". Ningyuan You is first author of both. The
   four SpTransformer evaluations now have `origin: author_reported` and a limitation saying so.
   `research.md` states that the authors developed none of the methods; that statement is wrong for
   SpTransformer.
2. **500 bp input applies to the GTEx task only.** The Results and Methods state the 500 bp division for
   the GTEx splicing task. The batch also put it on the three NT splice-site datasets (Supplementary Table
   4) in protocol names, descriptions, limitations, evaluation names, `comparison.inputs` and result
   qualifiers. This source does not state their input length, so all of these were corrected (168
   records).
3. **SpliceAI and SpTransformer were retrained.** Their configurations said "as distributed". Methods:
   "The task-specific methods used for comparison-including ... SpliceAI, SpliceTransformer, and
   others-were retrained under our framework", with non-PyTorch methods reimplemented in PyTorch. Names,
   parameters and `training_setting` now say this.
4. **Duplicate family records.** `sources.md` says the store held none of the new families. It already
   holds RNA-FM (`discovery-model-rna-fm`) and GENA-LM (`regulatory-variant-20261009-model-gena-lm`). The
   RNAFM and both GENA-LM configurations now link to those, and the batch's `model-rna-fm` and
   `model-gena-lm` records are removed.
5. **DNABERT and SpTransformer kind.** Both were `method` records. Both are trained neural networks, and
   the store records SpliceAI and the other language models as `model` families. They are now
   `model-dnabert` and `model-sptransformer`, and their links were updated.
6. **GTEx epoch selection.** Methods says the reported epoch is the one with the highest average PR-AUC.
   The dataset has a train and a test split and no validation split is named. Added as a limitation on
   the three GTEx protocols.
7. **Zero spreads.** UTRLM prints 0.0000 for every spread in both tables, and SpliceAI does in Table 5.
   Three runs with different random initialisations would not normally give that, and the source does not
   explain it. Added as a limitation on the affected evaluations.

## Notes, not changed

- Supplementary Table 4's F1, precision and recall on the three-class NT-splice-sites-all set. Methods
  says "For the multi-class classification task, macro-averaged results were reported". The singular
  "task" most likely means ncRNA classification, so the plain concepts are kept, as the extractor chose.
- Methods says PR-AUC "cannot be statistically averaged" and is shown from a fixed seed. Supplementary
  Table 5 still prints PR-AUC as mean (SD), and its caption says so. The sentence probably refers to the
  PR curves. The printed spreads are kept.
- The configurations do not name checkpoints; Supplementary Table 1 has fine-tuning parameters only. No
  checkpoint is collapsed into another.

## Relevance judgements

None in the batch. I agree with not linking `use-case-splicing-follow-up`: these are splice-site and
site-usage predictions, not variant splicing effects measured experimentally.

## Remaining gaps

Supplementary Tables 2, 3 and 6 (claim `claim-not-extracted`) and all figures. The top-k results are
pending.

## Values checked

| Result | Locator | Printed | Metric | Outcome |
| --- | --- | --- | --- | --- |
| `result-t4-nt-splice-acceptors-dnabert-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'DNABERT', column 'Accuracy' | 0.9832(0.0011) | accuracy | Match |
| `result-t4-nt-splice-acceptors-dnabert-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'DNABERT', column 'F1 Score' | 0.9832(0.0011) | f1-score | Match |
| `result-t4-nt-splice-acceptors-dnabert-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'DNABERT', column 'Precision' | 0.9832(0.0011) | precision | Match |
| `result-t4-nt-splice-acceptors-dnabert-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'DNABERT', column 'Recall' | 0.9832(0.0011) | recall | Match |
| `result-t4-nt-splice-acceptors-dnabert2-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'DNABERT2', column 'Accuracy' | 0.9776(0.0005) | accuracy | Match |
| `result-t4-nt-splice-acceptors-dnabert2-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'DNABERT2', column 'F1 Score' | 0.9776(0.0005) | f1-score | Match |
| `result-t4-nt-splice-acceptors-dnabert2-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'DNABERT2', column 'Precision' | 0.9777(0.0005) | precision | Match |
| `result-t4-nt-splice-acceptors-dnabert2-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'DNABERT2', column 'Recall' | 0.9776(0.0006) | recall | Match |
| `result-t4-nt-splice-acceptors-gena-lm-base-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'GENA-LM-base', column 'Accuracy' | 0.9545(0.0028) | accuracy | Match |
| `result-t4-nt-splice-acceptors-gena-lm-base-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'GENA-LM-base', column 'F1 Score' | 0.9544(0.0028) | f1-score | Match |
| `result-t4-nt-splice-acceptors-gena-lm-base-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'GENA-LM-base', column 'Precision' | 0.9555(0.0023) | precision | Match |
| `result-t4-nt-splice-acceptors-gena-lm-base-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'GENA-LM-base', column 'Recall' | 0.9543(0.0029) | recall | Match |
| `result-t4-nt-splice-acceptors-gena-lm-large-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'GENA-LM-large', column 'Accuracy' | 0.9618(0.0011) | accuracy | Match |
| `result-t4-nt-splice-acceptors-gena-lm-large-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'GENA-LM-large', column 'F1 Score' | 0.9618(0.0011) | f1-score | Match |
| `result-t4-nt-splice-acceptors-gena-lm-large-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'GENA-LM-large', column 'Precision' | 0.9621(0.0011) | precision | Match |
| `result-t4-nt-splice-acceptors-gena-lm-large-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'GENA-LM-large', column 'Recall' | 0.9618(0.0012) | recall | Match |
| `result-t4-nt-splice-acceptors-nucleotidetransformer-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'NucleotideTransformer', column 'Accuracy' | 0.9899(0.0014) | accuracy | Match |
| `result-t4-nt-splice-acceptors-nucleotidetransformer-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'NucleotideTransformer', column 'F1 Score' | 0.9899(0.0014) | f1-score | Match |
| `result-t4-nt-splice-acceptors-nucleotidetransformer-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'NucleotideTransformer', column 'Precision' | 0.9899(0.0014) | precision | Match |
| `result-t4-nt-splice-acceptors-nucleotidetransformer-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'NucleotideTransformer', column 'Recall' | 0.9900(0.0014) | recall | Match |
| `result-t4-nt-splice-acceptors-rnabert-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNABERT', column 'Accuracy' | 0.9590(0.0005) | accuracy | Match |
| `result-t4-nt-splice-acceptors-rnabert-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNABERT', column 'F1 Score' | 0.9590(0.0005) | f1-score | Match |
| `result-t4-nt-splice-acceptors-rnabert-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNABERT', column 'Precision' | 0.9590(0.0005) | precision | Match |
| `result-t4-nt-splice-acceptors-rnabert-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNABERT', column 'Recall' | 0.9590(0.0005) | recall | Match |
| `result-t4-nt-splice-acceptors-rnaernie-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAErnie', column 'Accuracy' | 0.9794(0.0014) | accuracy | Match |
| `result-t4-nt-splice-acceptors-rnaernie-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAErnie', column 'F1 Score' | 0.9794(0.0014) | f1-score | Match |
| `result-t4-nt-splice-acceptors-rnaernie-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAErnie', column 'Precision' | 0.9794(0.0014) | precision | Match |
| `result-t4-nt-splice-acceptors-rnaernie-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAErnie', column 'Recall' | 0.9794(0.0014) | recall | Match |
| `result-t4-nt-splice-acceptors-rnafm-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAFM', column 'Accuracy' | 0.9796(0.0007) | accuracy | Match |
| `result-t4-nt-splice-acceptors-rnafm-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAFM', column 'F1 Score' | 0.9796(0.0007) | f1-score | Match |
| `result-t4-nt-splice-acceptors-rnafm-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAFM', column 'Precision' | 0.9796(0.0007) | precision | Match |
| `result-t4-nt-splice-acceptors-rnafm-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAFM', column 'Recall' | 0.9796(0.0007) | recall | Match |
| `result-t4-nt-splice-acceptors-rnamsm-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAMSM', column 'Accuracy' | 0.9784(0.0009) | accuracy | Match |
| `result-t4-nt-splice-acceptors-rnamsm-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAMSM', column 'F1 Score' | 0.9784(0.0009) | f1-score | Match |
| `result-t4-nt-splice-acceptors-rnamsm-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAMSM', column 'Precision' | 0.9784(0.0009) | precision | Match |
| `result-t4-nt-splice-acceptors-rnamsm-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'RNAMSM', column 'Recall' | 0.9783(0.0009) | recall | Match |
| `result-t4-nt-splice-acceptors-splicebert-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'SpliceBERT', column 'Accuracy' | 0.9868(0.0009) | accuracy | Match |
| `result-t4-nt-splice-acceptors-splicebert-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'SpliceBERT', column 'F1 Score' | 0.9868(0.0009) | f1-score | Match |
| `result-t4-nt-splice-acceptors-splicebert-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'SpliceBERT', column 'Precision' | 0.9868(0.0009) | precision | Match |
| `result-t4-nt-splice-acceptors-splicebert-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'SpliceBERT', column 'Recall' | 0.9868(0.0009) | recall | Match |
| `result-t4-nt-splice-acceptors-utrlm-accuracy` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'UTRLM', column 'Accuracy' | 0.9693(0.0000) | accuracy | Match |
| `result-t4-nt-splice-acceptors-utrlm-f1-score` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'UTRLM', column 'F1 Score' | 0.9693(0.0000) | f1-score | Match |
| `result-t4-nt-splice-acceptors-utrlm-precision` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'UTRLM', column 'Precision' | 0.9695(0.0000) | precision | Match |
| `result-t4-nt-splice-acceptors-utrlm-recall` | Supplementary Table 4, block 'NT-splice-sites-acceptors', row 'UTRLM', column 'Recall' | 0.9693(0.0000) | recall | Match |
| `result-t4-nt-splice-all-dnabert-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'DNABERT', column 'Accuracy' | 0.9833(0.0004) | accuracy | Match |
| `result-t4-nt-splice-all-dnabert-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'DNABERT', column 'F1 Score' | 0.9834(0.0004) | f1-score | Match |
| `result-t4-nt-splice-all-dnabert-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'DNABERT', column 'Precision' | 0.9834(0.0003) | precision | Match |
| `result-t4-nt-splice-all-dnabert-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'DNABERT', column 'Recall' | 0.9833(0.0004) | recall | Match |
| `result-t4-nt-splice-all-dnabert2-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'DNABERT2', column 'Accuracy' | 0.9499(0.0037) | accuracy | Match |
| `result-t4-nt-splice-all-dnabert2-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'DNABERT2', column 'F1 Score' | 0.9500(0.0036) | f1-score | Match |
| `result-t4-nt-splice-all-dnabert2-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'DNABERT2', column 'Precision' | 0.9503(0.0034) | precision | Match |
| `result-t4-nt-splice-all-dnabert2-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'DNABERT2', column 'Recall' | 0.9499(0.0037) | recall | Match |
| `result-t4-nt-splice-all-gena-lm-base-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'GENA-LM-base', column 'Accuracy' | 0.9336(0.0021) | accuracy | Match |
| `result-t4-nt-splice-all-gena-lm-base-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'GENA-LM-base', column 'F1 Score' | 0.9337(0.0023) | f1-score | Match |
| `result-t4-nt-splice-all-gena-lm-base-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'GENA-LM-base', column 'Precision' | 0.9341(0.0026) | precision | Match |
| `result-t4-nt-splice-all-gena-lm-base-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'GENA-LM-base', column 'Recall' | 0.9336(0.0021) | recall | Match |
| `result-t4-nt-splice-all-gena-lm-large-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'GENA-LM-large', column 'Accuracy' | 0.9482(0.0032) | accuracy | Match |
| `result-t4-nt-splice-all-gena-lm-large-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'GENA-LM-large', column 'F1 Score' | 0.9483(0.0030) | f1-score | Match |
| `result-t4-nt-splice-all-gena-lm-large-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'GENA-LM-large', column 'Precision' | 0.9488(0.0025) | precision | Match |
| `result-t4-nt-splice-all-gena-lm-large-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'GENA-LM-large', column 'Recall' | 0.9482(0.0032) | recall | Match |
| `result-t4-nt-splice-all-nucleotidetransformer-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'NucleotideTransformer', column 'Accuracy' | 0.9842(0.0009) | accuracy | Match |
| `result-t4-nt-splice-all-nucleotidetransformer-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'NucleotideTransformer', column 'F1 Score' | 0.9842(0.0009) | f1-score | Match |
| `result-t4-nt-splice-all-nucleotidetransformer-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'NucleotideTransformer', column 'Precision' | 0.9843(0.0009) | precision | Match |
| `result-t4-nt-splice-all-nucleotidetransformer-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'NucleotideTransformer', column 'Recall' | 0.9842(0.0009) | recall | Match |
| `result-t4-nt-splice-all-rnabert-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNABERT', column 'Accuracy' | 0.9694(0.0006) | accuracy | Match |
| `result-t4-nt-splice-all-rnabert-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNABERT', column 'F1 Score' | 0.9694(0.0006) | f1-score | Match |
| `result-t4-nt-splice-all-rnabert-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNABERT', column 'Precision' | 0.9694(0.0006) | precision | Match |
| `result-t4-nt-splice-all-rnabert-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNABERT', column 'Recall' | 0.9694(0.0006) | recall | Match |
| `result-t4-nt-splice-all-rnaernie-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAErnie', column 'Accuracy' | 0.9809(0.0005) | accuracy | Match |
| `result-t4-nt-splice-all-rnaernie-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAErnie', column 'F1 Score' | 0.9809(0.0005) | f1-score | Match |
| `result-t4-nt-splice-all-rnaernie-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAErnie', column 'Precision' | 0.9809(0.0005) | precision | Match |
| `result-t4-nt-splice-all-rnaernie-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAErnie', column 'Recall' | 0.9809(0.0005) | recall | Match |
| `result-t4-nt-splice-all-rnafm-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAFM', column 'Accuracy' | 0.9806(0.0008) | accuracy | Match |
| `result-t4-nt-splice-all-rnafm-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAFM', column 'F1 Score' | 0.9806(0.0008) | f1-score | Match |
| `result-t4-nt-splice-all-rnafm-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAFM', column 'Precision' | 0.9806(0.0008) | precision | Match |
| `result-t4-nt-splice-all-rnafm-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAFM', column 'Recall' | 0.9806(0.0008) | recall | Match |
| `result-t4-nt-splice-all-rnamsm-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAMSM', column 'Accuracy' | 0.9793(0.0018) | accuracy | Match |
| `result-t4-nt-splice-all-rnamsm-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAMSM', column 'F1 Score' | 0.9793(0.0018) | f1-score | Match |
| `result-t4-nt-splice-all-rnamsm-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAMSM', column 'Precision' | 0.9794(0.0018) | precision | Match |
| `result-t4-nt-splice-all-rnamsm-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'RNAMSM', column 'Recall' | 0.9793(0.0018) | recall | Match |
| `result-t4-nt-splice-all-splicebert-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'SpliceBERT', column 'Accuracy' | 0.9861(0.0014) | accuracy | Match |
| `result-t4-nt-splice-all-splicebert-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'SpliceBERT', column 'F1 Score' | 0.9861(0.0014) | f1-score | Match |
| `result-t4-nt-splice-all-splicebert-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'SpliceBERT', column 'Precision' | 0.9862(0.0013) | precision | Match |
| `result-t4-nt-splice-all-splicebert-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'SpliceBERT', column 'Recall' | 0.9861(0.0014) | recall | Match |
| `result-t4-nt-splice-all-utrlm-accuracy` | Supplementary Table 4, block 'NT-splice-sites-all', row 'UTRLM', column 'Accuracy' | 0.9757(0.0000) | accuracy | Match |
| `result-t4-nt-splice-all-utrlm-f1-score` | Supplementary Table 4, block 'NT-splice-sites-all', row 'UTRLM', column 'F1 Score' | 0.9757(0.0000) | f1-score | Match |
| `result-t4-nt-splice-all-utrlm-precision` | Supplementary Table 4, block 'NT-splice-sites-all', row 'UTRLM', column 'Precision' | 0.9757(0.0000) | precision | Match |
| `result-t4-nt-splice-all-utrlm-recall` | Supplementary Table 4, block 'NT-splice-sites-all', row 'UTRLM', column 'Recall' | 0.9757(0.0000) | recall | Match |
| `result-t4-nt-splice-donors-dnabert-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'DNABERT', column 'Accuracy' | 0.9851(0.0007) | accuracy | Match |
| `result-t4-nt-splice-donors-dnabert-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'DNABERT', column 'F1 Score' | 0.9851(0.0007) | f1-score | Match |
| `result-t4-nt-splice-donors-dnabert-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'DNABERT', column 'Precision' | 0.9851(0.0007) | precision | Match |
| `result-t4-nt-splice-donors-dnabert-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'DNABERT', column 'Recall' | 0.9851(0.0007) | recall | Match |
| `result-t4-nt-splice-donors-dnabert2-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'DNABERT2', column 'Accuracy' | 0.9677(0.0029) | accuracy | Match |
| `result-t4-nt-splice-donors-dnabert2-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'DNABERT2', column 'F1 Score' | 0.9677(0.0029) | f1-score | Match |
| `result-t4-nt-splice-donors-dnabert2-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'DNABERT2', column 'Precision' | 0.9678(0.0028) | precision | Match |
| `result-t4-nt-splice-donors-dnabert2-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'DNABERT2', column 'Recall' | 0.9677(0.0029) | recall | Match |
| `result-t4-nt-splice-donors-gena-lm-base-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'GENA-LM-base', column 'Accuracy' | 0.9472(0.0016) | accuracy | Match |
| `result-t4-nt-splice-donors-gena-lm-base-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'GENA-LM-base', column 'F1 Score' | 0.9472(0.0016) | f1-score | Match |
| `result-t4-nt-splice-donors-gena-lm-base-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'GENA-LM-base', column 'Precision' | 0.9477(0.0012) | precision | Match |
| `result-t4-nt-splice-donors-gena-lm-base-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'GENA-LM-base', column 'Recall' | 0.9472(0.0016) | recall | Match |
| `result-t4-nt-splice-donors-gena-lm-large-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'GENA-LM-large', column 'Accuracy' | 0.9595(0.0005) | accuracy | Match |
| `result-t4-nt-splice-donors-gena-lm-large-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'GENA-LM-large', column 'F1 Score' | 0.9595(0.0005) | f1-score | Match |
| `result-t4-nt-splice-donors-gena-lm-large-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'GENA-LM-large', column 'Precision' | 0.9596(0.0005) | precision | Match |
| `result-t4-nt-splice-donors-gena-lm-large-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'GENA-LM-large', column 'Recall' | 0.9595(0.0005) | recall | Match |
| `result-t4-nt-splice-donors-nucleotidetransformer-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'NucleotideTransformer', column 'Accuracy' | 0.9913(0.0008) | accuracy | Match |
| `result-t4-nt-splice-donors-nucleotidetransformer-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'NucleotideTransformer', column 'F1 Score' | 0.9913(0.0008) | f1-score | Match |
| `result-t4-nt-splice-donors-nucleotidetransformer-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'NucleotideTransformer', column 'Precision' | 0.9914(0.0008) | precision | Match |
| `result-t4-nt-splice-donors-nucleotidetransformer-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'NucleotideTransformer', column 'Recall' | 0.9913(0.0008) | recall | Match |
| `result-t4-nt-splice-donors-rnabert-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNABERT', column 'Accuracy' | 0.9673(0.0008) | accuracy | Match |
| `result-t4-nt-splice-donors-rnabert-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNABERT', column 'F1 Score' | 0.9673(0.0008) | f1-score | Match |
| `result-t4-nt-splice-donors-rnabert-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNABERT', column 'Precision' | 0.9673(0.0008) | precision | Match |
| `result-t4-nt-splice-donors-rnabert-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNABERT', column 'Recall' | 0.9673(0.0008) | recall | Match |
| `result-t4-nt-splice-donors-rnaernie-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAErnie', column 'Accuracy' | 0.9832(0.0020) | accuracy | Match |
| `result-t4-nt-splice-donors-rnaernie-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAErnie', column 'F1 Score' | 0.9832(0.0020) | f1-score | Match |
| `result-t4-nt-splice-donors-rnaernie-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAErnie', column 'Precision' | 0.9832(0.0020) | precision | Match |
| `result-t4-nt-splice-donors-rnaernie-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAErnie', column 'Recall' | 0.9832(0.0020) | recall | Match |
| `result-t4-nt-splice-donors-rnafm-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAFM', column 'Accuracy' | 0.9841(0.0018) | accuracy | Match |
| `result-t4-nt-splice-donors-rnafm-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAFM', column 'F1 Score' | 0.9841(0.0018) | f1-score | Match |
| `result-t4-nt-splice-donors-rnafm-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAFM', column 'Precision' | 0.9842(0.0017) | precision | Match |
| `result-t4-nt-splice-donors-rnafm-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAFM', column 'Recall' | 0.9841(0.0019) | recall | Match |
| `result-t4-nt-splice-donors-rnamsm-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAMSM', column 'Accuracy' | 0.9735(0.0005) | accuracy | Match |
| `result-t4-nt-splice-donors-rnamsm-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAMSM', column 'F1 Score' | 0.9735(0.0005) | f1-score | Match |
| `result-t4-nt-splice-donors-rnamsm-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAMSM', column 'Precision' | 0.9735(0.0005) | precision | Match |
| `result-t4-nt-splice-donors-rnamsm-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'RNAMSM', column 'Recall' | 0.9735(0.0005) | recall | Match |
| `result-t4-nt-splice-donors-splicebert-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'SpliceBERT', column 'Accuracy' | 0.9915(0.0010) | accuracy | Match |
| `result-t4-nt-splice-donors-splicebert-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'SpliceBERT', column 'F1 Score' | 0.9915(0.0010) | f1-score | Match |
| `result-t4-nt-splice-donors-splicebert-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'SpliceBERT', column 'Precision' | 0.9915(0.0009) | precision | Match |
| `result-t4-nt-splice-donors-splicebert-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'SpliceBERT', column 'Recall' | 0.9915(0.0010) | recall | Match |
| `result-t4-nt-splice-donors-utrlm-accuracy` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'UTRLM', column 'Accuracy' | 0.9741(0.0000) | accuracy | Match |
| `result-t4-nt-splice-donors-utrlm-f1-score` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'UTRLM', column 'F1 Score' | 0.9741(0.0000) | f1-score | Match |
| `result-t4-nt-splice-donors-utrlm-precision` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'UTRLM', column 'Precision' | 0.9741(0.0000) | precision | Match |
| `result-t4-nt-splice-donors-utrlm-recall` | Supplementary Table 4, block 'NT-splice-sites-donors', row 'UTRLM', column 'Recall' | 0.9741(0.0000) | recall | Match |
| `result-t5-acceptors-donors-nucleotidetransformer-average-pr-auc` | Supplementary Table 5, block 'Splice acceptors and donors', row 'NucleotideTransformer', column 'Average PR-AUC' | 0.8826(0.0036) | auprc | Match |
| `result-t5-acceptors-donors-nucleotidetransformer-average-top-k` | Supplementary Table 5, block 'Splice acceptors and donors', row 'NucleotideTransformer', column 'Average Top-k' | 0.8061(0.0023) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-acceptors-donors-rnaernie-average-pr-auc` | Supplementary Table 5, block 'Splice acceptors and donors', row 'RNAErnie', column 'Average PR-AUC' | 0.8063(0.0015) | auprc | Match |
| `result-t5-acceptors-donors-rnaernie-average-top-k` | Supplementary Table 5, block 'Splice acceptors and donors', row 'RNAErnie', column 'Average Top-k' | 0.7518(0.0002) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-acceptors-donors-rnafm-average-pr-auc` | Supplementary Table 5, block 'Splice acceptors and donors', row 'RNAFM', column 'Average PR-AUC' | 0.7959(0.0011) | auprc | Match |
| `result-t5-acceptors-donors-rnafm-average-top-k` | Supplementary Table 5, block 'Splice acceptors and donors', row 'RNAFM', column 'Average Top-k' | 0.7433(0.0015) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-acceptors-donors-rnamsm-average-pr-auc` | Supplementary Table 5, block 'Splice acceptors and donors', row 'RNAMSM', column 'Average PR-AUC' | 0.8094(0.0010) | auprc | Match |
| `result-t5-acceptors-donors-rnamsm-average-top-k` | Supplementary Table 5, block 'Splice acceptors and donors', row 'RNAMSM', column 'Average Top-k' | 0.7554(0.0018) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-acceptors-donors-spliceai-average-pr-auc` | Supplementary Table 5, block 'Splice acceptors and donors', row 'SpliceAI', column 'Average PR-AUC' | 0.8622(0.0000) | auprc | Match |
| `result-t5-acceptors-donors-spliceai-average-top-k` | Supplementary Table 5, block 'Splice acceptors and donors', row 'SpliceAI', column 'Average Top-k' | 0.7930(0.0000) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-acceptors-donors-splicebert-average-pr-auc` | Supplementary Table 5, block 'Splice acceptors and donors', row 'SpliceBERT', column 'Average PR-AUC' | 0.8317(0.0096) | auprc | Match |
| `result-t5-acceptors-donors-splicebert-average-top-k` | Supplementary Table 5, block 'Splice acceptors and donors', row 'SpliceBERT', column 'Average Top-k' | 0.7680(0.0064) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-acceptors-donors-sptransformer-average-pr-auc` | Supplementary Table 5, block 'Splice acceptors and donors', row 'SpTransformer', column 'Average PR-AUC' | 0.8841(0.0018) | auprc | Match |
| `result-t5-acceptors-donors-sptransformer-average-top-k` | Supplementary Table 5, block 'Splice acceptors and donors', row 'SpTransformer', column 'Average Top-k' | 0.8070(0.0019) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-acceptors-donors-utrlm-average-pr-auc` | Supplementary Table 5, block 'Splice acceptors and donors', row 'UTRLM', column 'Average PR-AUC' | 0.8334(0.0000) | auprc | Match |
| `result-t5-acceptors-donors-utrlm-average-top-k` | Supplementary Table 5, block 'Splice acceptors and donors', row 'UTRLM', column 'Average Top-k' | 0.7794(0.0000) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-15class-nucleotidetransformer-average-pr-auc` | Supplementary Table 5, block 'Splice-15class', row 'NucleotideTransformer', column 'Average PR-AUC' | 0.8646(0.0032) | auprc | Match |
| `result-t5-splice-15class-nucleotidetransformer-average-top-k` | Supplementary Table 5, block 'Splice-15class', row 'NucleotideTransformer', column 'Average Top-k' | 0.7886(0.0003) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-15class-rnaernie-average-pr-auc` | Supplementary Table 5, block 'Splice-15class', row 'RNAErnie', column 'Average PR-AUC' | 0.6868(0.0055) | auprc | Match |
| `result-t5-splice-15class-rnaernie-average-top-k` | Supplementary Table 5, block 'Splice-15class', row 'RNAErnie', column 'Average Top-k' | 0.6593(0.0033) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-15class-rnafm-average-pr-auc` | Supplementary Table 5, block 'Splice-15class', row 'RNAFM', column 'Average PR-AUC' | 0.6770(0.0033) | auprc | Match |
| `result-t5-splice-15class-rnafm-average-top-k` | Supplementary Table 5, block 'Splice-15class', row 'RNAFM', column 'Average Top-k' | 0.6474(0.0012) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-15class-rnamsm-average-pr-auc` | Supplementary Table 5, block 'Splice-15class', row 'RNAMSM', column 'Average PR-AUC' | 0.6907(0.0044) | auprc | Match |
| `result-t5-splice-15class-rnamsm-average-top-k` | Supplementary Table 5, block 'Splice-15class', row 'RNAMSM', column 'Average Top-k' | 0.6618(0.0034) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-15class-splicebert-average-pr-auc` | Supplementary Table 5, block 'Splice-15class', row 'SpliceBERT', column 'Average PR-AUC' | 0.7538(0.0014) | auprc | Match |
| `result-t5-splice-15class-splicebert-average-top-k` | Supplementary Table 5, block 'Splice-15class', row 'SpliceBERT', column 'Average Top-k' | 0.7071(0.0017) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-15class-sptransformer-average-pr-auc` | Supplementary Table 5, block 'Splice-15class', row 'SpTransformer', column 'Average PR-AUC' | 0.8568(0.0005) | auprc | Match |
| `result-t5-splice-15class-sptransformer-average-top-k` | Supplementary Table 5, block 'Splice-15class', row 'SpTransformer', column 'Average Top-k' | 0.7808(0.0010) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-15class-utrlm-average-pr-auc` | Supplementary Table 5, block 'Splice-15class', row 'UTRLM', column 'Average PR-AUC' | 0.7367(0.0000) | auprc | Match |
| `result-t5-splice-15class-utrlm-average-top-k` | Supplementary Table 5, block 'Splice-15class', row 'UTRLM', column 'Average Top-k' | 0.6961(0.0000) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-53class-nucleotidetransformer-average-pr-auc` | Supplementary Table 5, block 'Splice-53class', row 'NucleotideTransformer', column 'Average PR-AUC' | 0.8634(0.0004) | auprc | Match |
| `result-t5-splice-53class-nucleotidetransformer-average-top-k` | Supplementary Table 5, block 'Splice-53class', row 'NucleotideTransformer', column 'Average Top-k' | 0.7859(0.0003) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-53class-rnaernie-average-pr-auc` | Supplementary Table 5, block 'Splice-53class', row 'RNAErnie', column 'Average PR-AUC' | 0.6851(0.0182) | auprc | Match |
| `result-t5-splice-53class-rnaernie-average-top-k` | Supplementary Table 5, block 'Splice-53class', row 'RNAErnie', column 'Average Top-k' | 0.6587(0.0136) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-53class-rnafm-average-pr-auc` | Supplementary Table 5, block 'Splice-53class', row 'RNAFM', column 'Average PR-AUC' | 0.6844(0.0035) | auprc | Match |
| `result-t5-splice-53class-rnafm-average-top-k` | Supplementary Table 5, block 'Splice-53class', row 'RNAFM', column 'Average Top-k' | 0.6516(0.0013) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-53class-rnamsm-average-pr-auc` | Supplementary Table 5, block 'Splice-53class', row 'RNAMSM', column 'Average PR-AUC' | 0.6955(0.0094) | auprc | Match |
| `result-t5-splice-53class-rnamsm-average-top-k` | Supplementary Table 5, block 'Splice-53class', row 'RNAMSM', column 'Average Top-k' | 0.6659(0.0067) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-53class-splicebert-average-pr-auc` | Supplementary Table 5, block 'Splice-53class', row 'SpliceBERT', column 'Average PR-AUC' | 0.7387(0.0020) | auprc | Match |
| `result-t5-splice-53class-splicebert-average-top-k` | Supplementary Table 5, block 'Splice-53class', row 'SpliceBERT', column 'Average Top-k' | 0.6971(0.0011) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-53class-sptransformer-average-pr-auc` | Supplementary Table 5, block 'Splice-53class', row 'SpTransformer', column 'Average PR-AUC' | 0.8552(0.0053) | auprc | Match |
| `result-t5-splice-53class-sptransformer-average-top-k` | Supplementary Table 5, block 'Splice-53class', row 'SpTransformer', column 'Average Top-k' | 0.7797(0.0016) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
| `result-t5-splice-53class-utrlm-average-pr-auc` | Supplementary Table 5, block 'Splice-53class', row 'UTRLM', column 'Average PR-AUC' | 0.7244(0.0000) | auprc | Match |
| `result-t5-splice-53class-utrlm-average-top-k` | Supplementary Table 5, block 'Splice-53class', row 'UTRLM', column 'Average Top-k' | 0.6889(0.0000) | splice-top-k-accuracy | Rejected: metric concept unsupported (value matches) |
