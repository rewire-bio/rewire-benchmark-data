# Research notes: You et al. 2026

## Why this source

Eleven pre-trained language models and five task-specific methods on the same splits, run by authors who
developed none of them, with the per-method values printed in full in the supplement rather than only drawn
in figures. It is the strongest head-to-head in this pass.

## Scope note

The article is framed around RNA processes. The two tables extracted here are splice-site classification on
the Nucleotide Transformer benchmark datasets and tissue-specific splice site usage from GTEx, both DNA
sequence tasks that the genomics lane covers, and both involving DNA language models (DNABERT, DNABERT-2,
Nucleotide Transformer, GENA-LM) alongside RNA language models. The remaining tables (non-coding RNA
classification, m6A, translation efficiency) sit in the RNA lane; `lit-rna-other` was told this source is
here and that those tables are unextracted.

## How the records are shaped

- One configuration per method, since every method gets the same 500 bp input and the same fine-tuning
  treatment in both tables. The language models are `foundation_model`, SpTransformer and SpliceAI are
  `specialist`.
- Six protocols: three Nucleotide Transformer splice-site datasets (Supplementary Table 4) and three GTEx task
  settings (Supplementary Table 5). The GTEx settings share one dataset record and differ in what is scored.
- `origin` is `independent_paper` throughout: the authors fine-tuned and scored every method themselves,
  including SpliceAI and SpTransformer.
- `printed_value` keeps the source's `mean(sd)` form, for example `0.9677(0.0029)`; `numeric_value` is the
  mean, and the standard deviation is in `uncertainty` with `n = 3`.

## Judgement calls a reviewer should check

1. `Average Top-k` is recorded as `splice-top-k-accuracy`, the SpliceAI-style metric the vocabulary already
   defines, because the Results section says top-k accuracy was chosen for the sparse, imbalanced splice task.
   `Average PR-AUC` is `auprc` with a qualifier saying it is averaged over the task's categories.
2. Supplementary Table 4's F1, precision and recall are recorded as plain `f1-score`, `precision` and
   `recall`; the source does not say whether they are macro- or micro-averaged for the three-class
   `NT-splice-sites-all` task. Nothing in the batch claims an averaging scheme.
3. GENA-LM-base and GENA-LM-large share one family record and differ only by configuration, matching how the
   source names them.
4. The three fine-tuning runs are random initialisations, not data resamples, so the spread describes training
   variance at a fixed split.
