# Review: lit-genomics-20261011-gfmbench, 2026-10-11

Reviewer: Claude review agent `reviewer-gen-3`, independent of the extractor `lit-genomics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

gfmbench (lit-genomics-20261011-gfmbench): approved with corrections.
Checked: the archived PDF's SHA-256 matches df9934c8...fdf72. I re-parsed Tables 1-5 from pdftotext -layout with my own block assignment: 572 cells, and all 572 results match on printed and numeric value. That includes "0" and "−0.0031" (Evo2 meQTL MCC) and the 20 NA cells. Task labels are printed mid-block, so I confirmed the block assignment from AUPRC prevalence: OMIM ~0.002, TraitGym ~0.1, Songlab ClinVar ~0.55. It holds, including Table 4's VEP-eval-before-BRCA1 order. Metric and qualifier mapping are right (Cos, L2, SNV Cos, MLM LLR, AR LLR). Origin independent_paper is right: the authors are at NVIDIA and developed none of the models. Model links are right (new DNA-BERT family; NTv3 from the guanine batch, so add guanine first). No duplicates.
Corrections:
1. The 20 results printed "NA" (SNV Cos AUROC/AUPRC on ClinVar Indel Pathogenicity and LOL-EVE, 5 models each; ids *-clinvar-indel-pathogenicity-zs-embedding-snv-cos-* and *-lol-eve-zs-embedding-snv-cos-*) are not measurements. The Table 3 caption says the metric does not apply to indels. Drop them, as was done for the GUANinE "–" cells, or confirm the store wants inapplicable cells kept as null.
2. Evidence concern on the source for Table 3, Songlab ClinVar, row Caduceus-Ps: AUROCs of 0.9333 and 0.8667 (=14/15 and 13/15) with AUPRC 0.99. The other four models score 0.50-0.84 on the same task. This looks like a tiny or failed evaluation subset. Attach the concern to all 6 Caduceus-Ps songlab-clinvar-zs-embedding results.
3. Judgement claims on TraitGym Mendelian (traitgym-mendelian-zs-ar-llr, -zs-embedding, -zs-mlm-llr): the limitations were copied from the complex-trait claims and are wrong here. "All AUROCs are close to 0.5 for the complex-trait task" should say that Mendelian AUROCs reach 0.60-0.63 (Evo2, DNABERT-2) with no uncertainty. "Fine-mapping labels" should be "curated Mendelian regulatory variants, not experimental allele effects".
4. BRCA1 claims (3): the endpoint says "saturation-genome-editing function classes", but the source says only "3,893 variants ... LOF, INT, FUNC based on experimentally measured DNA-repair activity" (Supplementary Note, BRCA1 task). Use the source's wording, or cite the assay separately. Also add "single run; no uncertainty printed" to the limitations, as the TraitGym claims have.
5. The ar-llr claims (5) say "for genomic language models", but only Evo2 is scored. Say "Evo2 (1B, BioNeMo, FP16)".
Relevance "proxy" is justified for all 9. Supervised protocols mix the Table 1 full fine-tuning rows with the Table 2 Evo2 linear-probing rows. comparison.adaptation separates them, so this is acceptable, but the protocol limitations should say so. The degenerate rows (MCC 0, AUROC 0.5) are transcribed as printed, which is correct.

Clarifying gfmbench correction 3: the AUROC ranges differ by claim. Mendelian zs-embedding: up to 0.63 (Evo2 L2 0.6263, DNABERT-2 L2 0.6051). zs-ar-llr: Evo2 0.6041. zs-mlm-llr: all 0.47-0.52, so "close to 0.5" is true for that claim, but it should say Mendelian, not complex-trait. The label-wording fix applies to all three.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. The 20 results printed 'NA' (SNV Cos metrics on ClinVar Indel Pathogenicity and LOL-EVE) were dropped: the Table 3 caption says the metric does not apply to indels.
2. The 6 Caduceus-Ps Songlab ClinVar zero-shot embedding results carry a source_anomaly (AUROC 0.9333 and 0.8667, AUPRC about 0.99, unlike the other four models). It is attached to these results rather than to the source, so the batch's other results stay comparable.
3. TraitGym Mendelian judgement claims: AUROC ranges and label wording corrected per the reviewer's clarification.
4. BRCA1 judgement claims: endpoint uses the source's wording (3,893 variants, LOF/INT/FUNC from DNA-repair activity); 'single run; no uncertainty printed' added.
5. Autoregressive LLR judgement claims name Evo2 (1B, NVIDIA BioNeMo, FP16) instead of 'genomic language models'.
6. Supervised protocols: limitation added that they hold both Table 1 full fine-tuning rows and Table 2 Evo2 linear-probing rows.
7. Judgement rationale now states why the relevance is proxy, separate from the description.

## Records after correction

- benchmark: 1
- claim: 9
- configuration: 10
- dataset: 20
- evaluation: 139
- model: 1
- protocol: 37
- result: 552
- source: 1
