# Review: lit-genomics-20261011-dnalongbench, 2026-10-11

Reviewer: Claude review agent `reviewer-gen-3`, independent of the extractor `lit-genomics`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

dnalongbench (lit-genomics-20261011-dnalongbench): approved with corrections.
Checked: re-fetched PMC12627797 XML, SHA-256 matches 0d7db21f...e41b. All 135 values compared by an independent <td> parse of Tables 3-7: 135/135 printed and numeric values match, locators correct. Metric, direction and protocol mapping are right (ETGP AUROC/AUPRC, CMP SCC, RSAP and TISP PCC, eQTLP AUROC). Expert model per task matches Methods (ABC, Enformer for eQTL and RSAP, Akita, Puffin-D). Origin is right: the CNN is author_reported, all other rows independent_paper. The ABC non-sequence-input caveat is present.
SCC concept: the definition is accurate (HiCRep: a weighted average of Pearson correlations within distance strata). Optional: add skos:broader :pearson-correlation (or the store's equivalent) and a HiCRep citation (Yang et al. 2017 Genome Res, doi 10.1101/gr.220640.117).
Corrections:
1. metric_qualifier on Table 6 and 7 results uses bare abbreviations. Expand them from the table footnotes. Table 6: FC=FANTOM CAGE, EC=ENCODE CAGE, ER=ENCODE RAMPAGE, GC=GRO-cap, PC=PRO-cap. Table 7: CCF=Cells_Cultured_fibroblasts, WB=Whole_Blood, SNSES=Skin_Not_Sun_Exposed_Suprapubic, SSELL=Skin_Sun_Exposed_Lower_leg, MS=Muscle Skeletal, NT=Nerve Tibial, AT=Artery_Tibial, AS=Adipose_Subcutaneous. Affects the 25 TISP non-Avg results (*-tisp-fc/ec/er/gc/pc) and the 45 eQTLP non-Avg results.
2. Duplicates: lit-007 and lit-008 (evaluation-lit-007/008, preprint source dnalongbench-2025) hold the same values as this batch's hyenadna-etgp-auroc (0.828) and caduceus-ph-etgp-auroc (0.826). Supersede them with the journal-version results, or mark them as duplicates, so the cells are not counted twice.
Minor, no change needed: the eQTL foundation-model adaptation is recorded as "Fine-tuned", but Methods describes a classification head on last-layer representations and does not say whether the backbone was frozen. A limitation note would be enough.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/`), as the reviewer specified, before the batch was added to the store.

1. Table 6 and Table 7 qualifiers expand the column abbreviations from the table footnotes.
2. The two journal-version ETGP AUROC results and their evaluations supersede the preprint records lit-007, lit-008, evaluation-lit-007 and evaluation-lit-008, which are set to superseded.
3. eQTL protocol limitation: Methods do not say whether the backbone was frozen.
4. Metric concept stratum-adjusted-correlation-coefficient gains skos:broader pearson-correlation and the HiCRep citation.

## Records after correction

- benchmark: 1
- configuration: 13
- dataset: 5
- evaluation: 25
- model: 3
- protocol: 5
- result: 135
- source: 1
