# Research: three callers on a synthetic WES pair (López-Cade et al. 2025)

Use case: `use-case-tumour-dna-somatic-variant-detection`. Pass: 2026-10-11 oncology literature search (lane `uc-oncology`). Ledger queries `s-q01`, `s-q03`, `s-q05`. The 2026-10-09 pass had noted this paper as a lead (ledger `search-use-case-tumour-somatic-genomics-q8`).

## Why this source

Independent clinical group, open access (CC BY 4.0), in the window (2025-10-30). Small: one synthetic tumour-normal WES pair, three callers via nf-core/sarek defaults. It adds a WES operating point for a standard pipeline, which the existing evidence lacks.

## What was extracted

Every numeric cell of Table 1: Total Query, TP, FP, FN, recall and precision for Mutect2, FreeBayes and Strelka2 (18 results). Total Truth (4,709) is the protocol `denominator`.

## Conflict found

The FreeBayes row does not add up: TP 1,908 plus FN 2,314 is 4,222, not 4,709, and the printed recall 0.4519 is 1,908/4,222 (1,908/4,709 would be 0.4052). The abstract repeats 45.2%. Mutect2 and Strelka2 rows sum to 4,709. The values are kept as printed and the FreeBayes evaluation is excluded from the judgement with this reason. A reviewer could instead raise a source `evidence_concern`, which would withhold the whole judgement.

## Other notes

- Mutect2 is printed as "version 2.2", which is not a GATK release; the configuration records the version as conflicting.
- Relevance `proxy`: synthetic SNVs inserted into clean reads make precision near 1 by construction.
