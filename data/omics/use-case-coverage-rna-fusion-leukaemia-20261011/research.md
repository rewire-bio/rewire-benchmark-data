# Research: Arriba-based whole RNA-seq against conventional diagnostics (Kim et al. 2025)

Use case: `use-case-tumour-rna-fusion-detection`. Pass: 2026-10-11 oncology literature search (lane `uc-oncology`). Ledger query `f-q08`.

## Why this source

The use case's fusion evidence is ascertained against callers' own calls (EnFusion ensemble; Tamura's four-caller rule). Kim et al. (Annals of Laboratory Medicine, epub 2025-10-16, CC BY-NC 4.0) score one workflow, STAR plus Arriba v2.4.0 with manual IGV review, against karyotyping, FISH and multiplex RT-PCR in 101 adult and paediatric acute leukaemia patients. This is the first linked evidence with orthogonal clinical truth. It is not a caller comparison.

## What was extracted

Every cell of Table 2 (26 fusion rows by: number detected by conventional diagnostics, number detected by RNA-seq, concordance %), 78 results, and five values printed in Results and Discussion: overall concordance 80.8%, sensitivity 83.3% (40 of 48), 1 minus specificity 21.4% (12 of 56), and sensitivity in AML (86.4%) and B-ALL (87.0%).

Table 2 sums agree with Results: 48 conventional-positive fusions, 40 found by RNA-seq, 12 RNA-seq-only.

## Things a reviewer should judge

1. Concordance printed as 0 for the RNA-seq-only rows is not a measured agreement; those results carry `undefined_reason` and a null numeric value.
2. "1 - specificity" counts RNA-seq-only fusions as errors, although the authors describe several as well-known recurrent fusions and confirmed one (MLLT10::UBE2L6) by RT-PCR and Sanger sequencing (Figure 1); recorded as `false-positive-rate` with that caveat in the protocol limitations.
3. Relevance `direct` for one workflow only; the judgement's comparison group has a single configuration, so the page will show no ranking.
