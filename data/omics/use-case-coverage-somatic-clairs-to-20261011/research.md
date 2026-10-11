# Research: ClairS-TO tumour-only benchmark (Chen et al. 2025)

Use case: `use-case-tumour-dna-somatic-variant-detection`. Pass: 2026-10-11 oncology literature search (lane `uc-oncology`), window 2025-10-01 to 2026-10-11. Ledger queries `s-q02`, `s-q03`, `s-q06`.

## Why this source

The use case excludes tumour-only calling and lists it as a gap. ClairS-TO (Nature Communications, published 2025-10-31) compares tumour-only callers on two held-out cell lines with consortium truth sets on ONT, PacBio and Illumina, including Mutect2, Octopus, Pisces and DeepSomatic on short reads. It is a developer paper.

## What was extracted

Every cell of Supplementary Tables 2a (ONT COLO829, 25x to 75x), 2b (ONT HCC1395), 7a (PacBio COLO829, 50x) and 7b (Illumina COLO829, 50x): AUPRC, precision, recall, F1, TP, FP and FN. 62 printed rows, 434 results. Tables 3 to 6 and 8 were not extracted (listed in `coverage.json` gaps).

printed_value comes from the PDF text layer. Each printed row was matched in order to the authors' Source Data sheet for the same table, which supplies the row labels (caller, coverage, type); every number was asserted equal at the printed precision. The Source Data workbook is pinned as a third source for that identity check.

## Modelling choices

- Eight protocols: dataset (ONT COLO829, ONT HCC1395, PacBio COLO829, Illumina COLO829) by variant type. Coverage is in `metric_qualifier`.
- Precision, recall, F1 and the counts are at the best-F1 quality threshold, which the authors chose on the test data (Figure 2 legend: "The dot on each dashed line indicates where the best F1-score was achieved"); this is in every qualifier and in the protocol limitations.
- Origin: ClairS-TO SS and SSRS and Clair3 (same group) `author_reported`; DeepSomatic, Mutect2, Octopus and Pisces `independent_paper`.
- New method families: ClairS-TO, Clair3, Pisces. Octopus, Mutect2 and DeepSomatic reuse store families.

## Things a reviewer should judge

1. Relevance after review: all eight judgements are `proxy`; the use case scope is unchanged (reviewer-onc-1, C1).
2. Best-F1 thresholds chosen on the test data favour every caller equally but are not operating points; AUPRC may be the better headline. I used F1 as headline for consistency with the other somatic judgements.
3. Clair3 is a germline caller run as a baseline; consider excluding it from the judgements.
4. DeepSomatic is absent from HCC1395 by the authors' choice (trained on it); it is present on COLO829. Whether DeepSomatic 1.7.0 tumour-only models saw COLO829 is not stated.
