# Research: HG008 external evaluation of somatic callers (Hasan 2026)

Use case: `use-case-tumour-dna-somatic-variant-detection`. Pass: 2026-10-11 oncology literature search (lane `uc-oncology`), window 2025-10-01 to 2026-10-11. Ledger: `data/omics/lit-search-20261011-uc-oncology/ledger.jsonl` (queries `s-q01`, `s-q02`, `s-q04`, `s-q07` and lookups `s-a01` to `s-a03`).

## Why this source

The use case lists "No peer-reviewed HG008 small-variant caller comparison was found" as a gap. The 2026-10-09 pass found this preprint but could not read it (ledger `search-use-case-tumour-somatic-genomics-q10`). Version 1 is now readable as a PDF from Research Square, and the author's Zenodo deposit holds the result tables. The author developed none of the three callers.

## What was extracted

Every cell of Zenodo `tables/Table1_HG008_primary_metrics.tsv` (6 rows), `Table2_HG008_variant_class_metrics.tsv` (12 rows) and `Table4_HG008_sensitivity_all_region.tsv` (6 rows): TP, FP, FN, precision, recall and F1, with the printed 95% block-bootstrap interval attached to F1 as `uncertainty` where printed (Tables 1 and 2). 144 results.

The Zenodo values carry six decimals; the manuscript prints some of them rounded to four (for example Mutect2 precision 0.9412, recall 0.8582, F1 0.8978; DeepSomatic F1 0.8973 with CI 0.8929 to 0.9015). They agree after rounding. The Zenodo table is used because it prints every cell.

## Modelling choices

- Four protocols: primary region overall, SNV and indel (Tables 1 and 2), and the all-benchmark sensitivity region (Table 4). `denominator` is TP + FN, which is constant within each table and equals the truth counts in Results (14,014; 9,078; 4,936) and 18,207 for the all region.
- Callers reuse the existing method families (Mutect2, Strelka, DeepSomatic). The three ensembles reuse `somatic-20261009-method-majority-vote` with the threshold stated on each configuration (union at least one, majority at least two, strict intersection all three).
- Origin: `independent_paper` for the three callers, `author_reported` for the author's ensembles.

## Things a reviewer should judge

1. Source quality. Single-author preprint from the author's own company (AmbioSpire LLC); the author says the original scoring code was not retained and that an internal reimplementation reproduced the numbers. The study design (freezing before truth access) is unusual and carefully described, but nothing has been externally checked. Decide whether `direct` relevance is acceptable for an unreviewed preprint or whether an evidence concern is warranted.
2. DeepSomatic training overlap. The author does not claim DeepSomatic's training was independent of HCC1395/SEQC2, but HG008 is a different cell line; I kept DeepSomatic in the judgements. Check whether the DeepSomatic 1.10.0 WGS model was trained on HG008 data (not stated in the source).
3. The HG008-T v0.3 truth set is a draft covering clonal and truncal variants only.
