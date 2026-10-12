# Research notes

Why: an independent perturbation benchmark that scores the DE calls researchers act on, comparing simple baselines (majority vote, KNN, logistic regression on GenePT embeddings) with scVI, a scGen-based VAE, Scouter, TranScouter and STATE, within a cell line and across cell lines (K562, RPE1, HepG2, Jurkat).

Decisions:
- Tables 1-4 extracted in full. The headline macro-F1 and balanced accuracy values are in figures (some appear in the text); they are not extracted.
- Proportion of pairs predicted DE: metric 'proportion', unit percent, direction unknown (closeness to the true prevalence matters, not the size). 3-class accuracy by |log2 FC| quantile: metric 'accuracy', the quantile in metric_qualifier, on the four-cell-line average subset.
- Origin independent_paper for scVI and STATE; author_reported for the authors' baselines, their scGen-based VAE, and Scouter and TranScouter, which co-author Ouyang Zhu developed (review S1).
- Relevance judgements (needs_review, proxy) for both protocols to use-case-genetic-perturbation-response.

For the reviewer:
- Methods report both full and PerturbQA-downsampled settings; the table captions do not say which one Tables 1-4 use. The printed true DE prevalence (1.75-4.41%) matches the full data (Table 5). Recorded as an evidence concern.
- STATE is few-shot in the cross-cell-line task (it sees the held-out line's training split).
- Table 2 prints scVI mean before VAE scGen, unlike Table 1; the script asserts each table's own order.
