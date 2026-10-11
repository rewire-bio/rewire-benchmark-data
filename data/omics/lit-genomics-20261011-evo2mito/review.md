# Review: lit-genomics-20261011-evo2mito, 2026-10-11

Reviewer: Claude review agent `reviewer-gen-1`, independent of the extractor `lit-genomics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

evo2mito (lit-genomics-20261011-evo2mito): approved with corrections. The 8 Evo2 results are fine. The 56 comparator results should be removed.

Checks:
- Source: I unpacked the archived PDF. Its SHA-256 8fe2977a...cf7d matches the source record.
- Values: all 64 results match Table 2 exactly (PDF page 10, locators correct). Metric mapping is correct: Sensitivity maps to recall, and every metric is higher-is-better.
- Evo2 row: origin independent_paper is correct (the authors are not the Evo2 developers). discovery-model-evo-2 is the family that the existing mrnabench and mimic Evo2 records already use.

Correction 1 (main finding): the comparator rows were not measured on the authors' test split. They are copied from the APOGEE 2 paper (Bianco et al. 2023, Nat Commun 14:5058, PMC10439926), which reports APOGEE 2 auPRC 0.716 / auROC 0.95 and APOGEE 1 0.573 / 0.855. These are the same numbers as Table 2. In that paper they come from repeated 20-fold cross-validation on APOGEE Dataset 1: 140 pathogenic and 1,734 neutral missense variants only. Table 2's own numbers agree. From precision, sensitivity and specificity, every comparator row implies a neutral:pathogenic ratio of about 12:1 (1,734/140 = 12.4). The Evo2 row implies about 5:1 (623/130 = 4.8, all variant types).
So the 7 comparator evaluations (lit-genomics-20261011-evo2mito-eval-{apogee-1,apogee-2,covec-wmv,carol,metasnp,condel,mtoolbox-ds}) wrongly link `data` to lit-genomics-20261011-evo2mito-data-mtdna-test-split and are named "on mtDNA pathogenicity test split". My recommendation is to drop these 7 evaluations, their 7 configurations, their 56 results, and the 6 new method records (keep the existing brca-20261009-method-condel). They are a secondary quotation of another paper, measured on a different variant set, and not genomic foundation models. If someone wants them later, the primary source is APOGEE 2 Supplementary Data 4.
Either way, rewrite the source's evidence_concern to state the finding instead of the hypothesis: "Comparator rows reproduce APOGEE 2 (Bianco et al. 2023) cross-validation results on a missense-only set (140 pathogenic, 1,734 neutral). They were not measured on this paper's test split, so Table 2 does not compare like with like." Update the matching item in source limitations and in the protocol limitations the same way.

Correction 2 (concern wording): the Table 2 Evo2 row is internally consistent: (0.867 + 0.825) / 2 = 0.846. The Figure 2B legend and Section 4.3.1 report TPR 90.2% and TNR 85.0%, so balanced accuracy 87.6%. Sensitivity and specificity differ as well as balanced accuracy, so the two are different counts, not a single-cell typo. Keep the Table 2 values. Extend the concern to say "Table 2 sensitivity/specificity 0.867/0.825 versus Figure 2B and text 90.2%/85.0%; the source does not explain the difference."

No other issues. Dataset counts (130/623, all variant types, 70/30 split with a Youden threshold) match Section 3.1 and Section 3.4.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. The 7 comparator evaluations, their 7 configurations, 56 results and 6 new method records were removed: the comparator rows reproduce APOGEE 2 (Bianco et al. 2023) cross-validation results on a different, missense-only variant set.
2. The source evidence concern, source limitations and protocol limitations state that finding, and the concern records the Table 2 versus Figure 2B sensitivity/specificity discrepancy (0.867/0.825 versus 90.2%/85.0%).

## Records after correction

- configuration: 1
- dataset: 1
- evaluation: 1
- protocol: 1
- result: 8
- source: 1
