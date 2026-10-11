# Research: VarNet-T tumour-only benchmark (Krishnamachari et al. 2026)

Use case: `use-case-tumour-dna-somatic-variant-detection`. Pass: 2026-10-11 oncology literature search (lane `uc-oncology`), window 2025-10-01 to 2026-10-11. Ledger queries `s-q02`, `s-q03`.

## Why this source

A second tumour-only comparison, on Illumina WGS, covering SEQC2 HCC1395, COLO829, ten PCAWG primary tumours from five cancer types not used in training, and three low-burden tumours (AML, medulloblastoma, CLL). Nine configurations: VarNet-T, five DeepSom models, DeepSomatic, Mutect2 and ClairS-TO, all tumour-only. Developer paper (CC BY 4.0).

## What was extracted

Every cell of Supplementary Tables 1 (SEQC2 and COLO829, SNV and indel AUPRC), 2 (PCAWG per-sample SNV AUPRC) and 4 (AML, MBL and CLL SNV AUPRC). 153 results.

All three tables were parsed from the text layer of the Supplementary Information PDF (physical pages 18, 19 and 21) and checked cell by cell against the authors' Source Data sheets of the same names. The three values printed in Results (VarNet-T 0.773 on SEQC2 and 0.656 on COLO829, DeepSom-ESAD 0.577 on SEQC2) match. No figure was read. (The first extraction wrongly treated Tables 1 and 4 as images; the review found their text layer and the extraction was corrected.)

## Modelling choices

- Six protocols: SEQC2 SNV and indel, COLO829 SNV and indel, PCAWG SNV (sample in qualifier), low-TMB SNV (sample in qualifier).
- ClairS-TO links to the method record created in `use-case-coverage-somatic-clairs-to-20261011`; add that batch first.
- DeepSom is a new method family; its five pre-trained models are separate configurations.
- DeepSomatic is excluded from the two SEQC2 judgements: the source says it was trained on SEQC2 data.

## Things a reviewer should judge

Relevance after review: all six judgements are `proxy`; the use case's scope is unchanged.
3. The source prints indel AUPRC for DeepSom models, which the DeepSom paper describes as an SNV method; the values are kept as printed.
4. The AML, MBL and CLL samples are the same samples as the existing Wang et al. 2020 protocols, here downsampled to about 100x and called without the normal.
