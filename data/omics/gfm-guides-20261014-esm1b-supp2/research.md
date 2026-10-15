# Research notes

Batch for rewire-benchmark-data issue #163: the parts of Brandes et al. 2023 (Nature Genetics 55:1512) Supplementary Table 2 that the first extraction, `gfm-guides-20261014-esm1b` (reviewed, in the store), listed as gaps: the head-to-head columns of the two clinical sheets, and the in-frame indel and stop-gain sheets.

## Do the head-to-head columns map to the record contract?

Yes. Each row of `Table_of_results_ClinVar` and `Table_of_results_HGMD` gives, for one comparator, the ROC-AUC and balanced PRC-AUC of that method and of ESM1b on the variants both score, and the number of those variants (`Contents` sheet definitions, asserted by the script). That is one dataset subset per comparator and sheet (with `scored_count` = head2head_n_variants), two evaluations on it (comparator and ESM1b) under one head-to-head protocol per sheet, and two results per evaluation. ESM1b uses the existing configuration `gfm-guides-20261014-esm1b-config-esm1b`.

All 45 comparators are extracted on both sheets: the 18 already in the store from the 19-method comparison, and 27 that the paper excluded from that comparison because they were trained on clinical databases or use allele frequency. The exclusion note from column K is kept in each new configuration's `training_overlap`, and the protocol's limitations say those values are inflated by the overlap. Comparator values on different subsets are not comparable with each other, only with the ESM1b value on the same subset; that is what the per-comparator subsets encode.

## Decisions

- New configurations for the 27 excluded methods, each `configuration_of` the store's existing method record (BayesDel, CADD, ClinPred, DANN, DEOGEN2, Eigen, FATHMM, FATHMM-MKL, FATHMM-XF, LIST-S2, M-CAP, MPC, MVP, MetaLR, MetaRNN, MetaSVM, MutPred, MutationTaster, PolyPhen-2, PrimateAI, REVEL, VARITY, VEST4). Two-version tools (BayesDel with and without AF, Eigen and Eigen-PC, PolyPhen-2 HDIV and HVAR, VARITY_ER and VARITY_R) are two configurations of one method, as in the Lee 2026 batch. Method types copy what the store's existing configurations of the same method use. VARITY is not in dbNSFP (Methods 'Other VEP methods'), so its version is unreported.
- Indels and stop-gains: a new benchmark (`...-benchmark-brandes2023-clinvar-multiresidue`), two datasets (ClinVar in-frame indels; ClinVar stop-gains), five subsets (insertions, deletions, delins; stop-gains not expected and expected to undergo NMD), two protocols. Overall values link to the dataset, per-type values to the subset.
- New systems: four ESM1b configurations of `uc20260930-model-esm-1b` (absolute-valued, vanilla and weighted PLLR for indels; minimum LLR for stop-gains), a CADD indel configuration (version and score source not stated; dbNSFP holds SNV scores only), and five baseline methods (pairwise alignment score, BlastP score, number of residues lost, percentage of residues lost, 50 bp rule). Edit distance reuses `flip-method-levenshtein`.
- Origin: author_reported for ESM1b and the authors' baselines; independent_paper for CADD and every head-to-head comparator.
- `NaN` cells in the indel and stop-gain sheets are not values and have no result (ESM1b-wPLLR, alignment, BlastP and edit distance by indel type; the 50 bp rule by NMD status).
- Workbook values are written as the shortest round-trip decimal of the stored number, as in the first batch. The Results text values were not added as separate results.
- Records are `needs_review`. No review.json yet.

## Record counts

- benchmark: 1
- protocol: 4 (two head-to-head, indels, stop-gains)
- dataset: 2
- dataset_subset: 95 (90 head-to-head, 5 indel or stop-gain strata)
- method: 5
- configuration: 32 (27 head-to-head comparators, 4 ESM1b scores, CADD for indels)
- evaluation: 206 (180 head-to-head, 16 indel, 10 stop-gain)
- result: 386 (360 head-to-head, 16 indel, 10 stop-gain)

## Extraction note for the reviewer

Method: deterministic parse of the pinned workbook with `extract/build_supp2.py` (stdlib OOXML reader). Inputs are the archived artifacts of the first batch, gunzipped; run from the repository root:

```sh
A=data/omics/gfm-guides-20261014-esm1b/artifacts
gunzip -c $A/brandes2023-supplementary-table-2.xlsx.gz > <scratch>/st2.xlsx
gunzip -c $A/brandes2023-pmc10484790.xml.gz > <scratch>/brandes.xml
gunzip -c $A/brandes2023-supplementary-information.pdf.gz > <scratch>/si.pdf
python3 -I data/omics/gfm-guides-20261014-esm1b-supp2/extract/build_supp2.py <scratch>/st2.xlsx <scratch>/brandes.xml <scratch>/si.pdf . data/omics/gfm-guides-20261014-esm1b-supp2
```

The script asserts the three input hashes; the `Contents` definitions of every extracted column; the header row A1:K1 of both clinical sheets, the `included` flag of every row, the set of 45 comparator labels and one exclusion note per excluded method; the headers and row labels of the indel and stop-gain sheets; the benchmark sizes in the Fig. 4 legend, the Methods and the Supplementary Methods; and that every reused record exists and every new ID does not.

Gaps (not extracted):

- Sheet `Table_of_results_DMS` (Spearman correlation with DMS measurements, protein function rather than pathogenicity).
- Extended Data Fig. 1 (true-positive rate at 5% false-positive rate), gene-average ROC-AUC, Figs. 2e-h, 3 and 4 (figure-only beyond the workbook).
- Per-type indel counts (Fig. 4b pie chart only) and the class counts of each head-to-head subset (only the total is printed).
- One-tailed P values for the indel comparisons (Fig. 4b) and the head-to-head P values ("P < 0.001", text only).

Needs reviewer judgement:

- Stop-gain counts: the Fig. 4d legend and the Supplementary Methods give 32,362 pathogenic NMD variants and 36,034 overall; the Methods bootstrap paragraph gives 32,441 and 36,113 (benign counts agree). Recorded on the stop-gain dataset (`denominator_warning`) and the NMD subset (`scored_count` missing as `conflicting`).
- Stop-gain ROC-AUC basis: Fig. 4d plots the mean of 20 bootstrap iterations of 140 pathogenic and 140 benign variants. Whether the workbook values are those means or whole-set ROC-AUCs is not stated; recorded as missing `comparison.aggregation` and a protocol limitation.
- Text versus workbook: the Results print the indel and stop-gain values to three decimals, sometimes truncated rather than rounded (CADD 0.835 for 0.8358, edit distance 0.501 for 0.5017, BlastP 0.581 for 0.5817, ESM1b NMD 0.565 for 0.5658, residues lost 0.649 for 0.6499 and 0.599 for 0.5996), while ESM1b non-NMD 0.734 for 0.7337 is rounded. Only the workbook values are recorded; the text values agree with them to within the last printed digit.
- CADD for indels: the article says CADD "was not directly trained on ClinVar"; the score file and version are not stated.
- The ESM1b head-to-head values differ slightly from row to row (for example 0.905880 on the 39,165-variant sets and 0.906018 against EVE). That is expected, since each subset differs, but it is why the head-to-head ESM1b results are separate records.
- Whether the 27 excluded comparators should be extracted at all. They were included because the issue asks for the head-to-head columns; their circularity is stated on each configuration and in the protocol.
