# Review: lit-genomics-20261011-traitgym, 2026-10-11

Reviewer: Claude review agent `reviewer-gen-3`, independent of the extractor `lit-genomics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

traitgym (lit-genomics-20261011-traitgym): approved with corrections. The changes are to the judgement claims only.
Checked: the archived bundle's SHA-256 matches 44dfedc0...372e. All 156 per-file SHA-256s inside the bundle match their content. I re-downloaded 3 CSVs from HF at revision 1fde1955 and their hashes match the bundle. All 156 results: printed, numeric and SE values equal the CSV score/se exactly; metric AUPRC; dataset and protocol mapping right. LogisticRegression.chrom rows are in linear-probing and the rest are zero-shot. config/models.csv at GitHub 4d80fe88 confirms GPN_final=GPN-Promoter. Origin is right: GPN-MSA, GPN-Promoter and their ensembles (CADD+GPN-MSA, CADD+GPN-MSA+Borzoi, GPN-MSA+Borzoi) are author_reported (33), the rest independent_paper. No other TraitGym results exist in the store, so no duplicates. One gap: I could not check "bootstrap" as the SE method against paper Appendix B.4 (paper not read). Keep the citation.
Judgement claims (4, use-case-regulatory-variant-gene-follow-up). "proxy" is right: the inputs match fine-mapped variants, but the output ranks variants only, with no element-gene link or effect direction. Corrections to all 4 claims:
1. Add a truth-set caveat to limitations. Complex-trait positives come from UK Biobank fine-mapping (high PIP, mostly European ancestry). Mendelian positives are curated regulatory pathogenic variants, enriched for conserved promoter and UTR sites, which favours conservation scores and CADD.
2. Add to the two linear-probing claims' limitations: these scores are fitted on TraitGym labels with leave-one-chromosome-out training, so they are not comparable to zero-shot scores. The constraints already say not to mix protocols; the limitation should state why.
3. The rationale repeats the description word for word. Make the rationale state why the relevance is proxy (no gene or element link, no effect direction).
Then apply the use-case-links.json assessed_by links once the reviewer sets reviewed_evaluations and runs the repin. That is not done yet.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. Judgement claims: truth-set caveat added (UK Biobank fine-mapping for complex traits; curated, conserved promoter and UTR sites for Mendelian traits).
2. Linear-probing judgement claims: limitation that the scores are fitted on TraitGym labels with leave-one-chromosome-out training and are not comparable with zero-shot scores.
3. Judgement rationale now states why the relevance is proxy (no element-gene link, no effect direction).

## Records after correction

- benchmark: 1
- claim: 4
- configuration: 81
- dataset: 2
- evaluation: 156
- method: 5
- model: 1
- protocol: 4
- result: 156
- source: 1
