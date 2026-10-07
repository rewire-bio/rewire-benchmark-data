# AMP use-case evidence intake — 7 October 2026

Frozen candidate: `2026-10-07-fc6ee0920cef`. Publication and consumer adoption are pending.

This intake adds nine definitions, 19 mappings and 431 records, including 190 numerical results. The original 17 definitions, 72 mappings and 28,234 scientific records are unchanged. All 26 cases resolve to numerical evidence; no active direct/proxy mapping is empty or stale. Counts are distinct IDs within each case. Shared evidence must not be summed across cases.

| Use-case ID | Protocols | Evaluations | Results | Numeric |
| --- | ---: | ---: | ---: | ---: |
| `use-case-brca1-brca2-germline-interpretation` | 10 | 10 | 48 | 46 |
| `use-case-cell-type-annotation-transfer` | 5 | 24 | 27 | 27 |
| `use-case-cnv-detection-characterisation` | 1 | 1 | 1 | 1 |
| `use-case-diagnostic-dna-pathogen-identification` | 1 | 1 | 1 | 1 |
| `use-case-diagnostic-genomics-model-execution` | 1 | 1 | 1 | 1 |
| `use-case-diagnostic-rna-pathogen-detection` | 1 | 1 | 1 | 1 |
| `use-case-egfr-nsclc-actionability-resistance-evidence` | 2 | 5 | 164 | 164 |
| `use-case-genetic-perturbation-response` | 2 | 8 | 8 | 8 |
| `use-case-mass-spectrum-molecule-shortlisting` | 7 | 39 | 69 | 69 |
| `use-case-patient-rna-splicing-validation` | 1 | 1 | 2 | 2 |
| `use-case-phenotype-perturbation-selection` | 2 | 21 | 21 | 21 |
| `use-case-plant-promoter-reporters` | 10 | 26 | 26 | 26 |
| `use-case-plasma-ctdna-fragmentomics` | 1 | 1 | 1 | 1 |
| `use-case-plasma-ctdna-methylation` | 1 | 1 | 1 | 1 |
| `use-case-protein-stability` | 3 | 99 | 107 | 107 |
| `use-case-rare-disease-candidate-ranking` | 8 | 24 | 90 | 90 |
| `use-case-regulatory-variant-gene-follow-up` | 5 | 54 | 106 | 106 |
| `use-case-rhodopsin-wavelength-transfer` | 6 | 20 | 70 | 69 |
| `use-case-somatic-small-variant-oncogenicity` | 4 | 5 | 27 | 27 |
| `use-case-splicing-follow-up` | 4 | 16 | 32 | 32 |
| `use-case-structural-hypotheses-experiments` | 5 | 9 | 64 | 64 |
| `use-case-therapeutic-target-validation` | 2 | 21 | 21 | 21 |
| `use-case-tumour-dna-somatic-variant-detection` | 1 | 2 | 24 | 24 |
| `use-case-tumour-rna-fusion-detection` | 2 | 6 | 20 | 20 |
| `use-case-unresolved-rare-disease-reanalysis` | 1 | 1 | 14 | 14 |
| `use-case-utr-translation-baselines` | 5 | 32 | 36 | 34 |

## Evidence and provenance

All 17 existing cases have bounded current primary-source checks in [group A](../../data/omics/amp-coverage-20261007/existing-a/review.json), [group B](../../data/omics/amp-coverage-20261007/existing-b/review.json) and [group C](../../data/omics/amp-coverage-20261007/existing-c/review.json). CIViC-Fact current PDF access returned HTTP 429; archived v3 bytes and fresh version metadata are distinguished. Retrieval of a historical dataset pin does not establish that it is the newest upstream version.

The nine new decisions have primary sources, exact locators, printed values, uncertainty, configuration/population scope and explicit unknowns in the [native intake](../../data/omics/use-case-coverage-amp-20261007/clinical/research.md). Direct/proxy labels apply to the declared endpoint. Virtual tumours, ascertained fusion cohorts, known-event recovery, culture/panel agreement, internal cross-validation, one deletion bin and conventional runtime do not establish broad clinical decision utility.

The Feng expansion contains 138 exact primary table values in 79 task-specific evaluations. Acceptor/donor, TATA/NonTATA, pathogenic/common variants and each QTL task are distinct. Short and long generated-window datasets are separate. AlphaGenome shares the long QTL dataset, consumes central 131,072 bp and averages output tracks over central 2,048 bp. Task-specific supervised random forests and specialised genomic comparators are identified. Eight negative signs and the AUC prose/table conflict are preserved. Unselected tasks and supplements remain open in [data #19](https://github.com/rewire-bio/rewire-benchmark-data/issues/19).

The [archive transformation receipt](../../data/omics/amp-coverage-20261007/archive-transformation.json) binds 24 public factual copies separately from original retrieved sources. Restricted or unestablished-reuse full copies remain in the ignored local audit cache. A fresh checkout verifies public-copy bytes; it does not claim fresh access to an undistributed original. URLs, retrieval times, access/licence facts, original hashes and locators are retained. Historical review receipts remain unchanged.

## Validation

The full producer suite passed 583 tests. Final focused scientific, coverage and archive checks passed 24 tests; Python passed 10 tests; typechecking passed. Tests compare all 138 Feng cells against primary XML, preserve original records/definitions/mappings, reject changed archives and missing review registries, preserve comma-containing CSV values, withhold stale evidence and paginate beyond 100 cases. All 24 public and retained-original archive identities were independently checked. The full producer build includes 32 immutable releases: the new candidate and 31 historical releases; archive verification passed for 6,163 files. Packaging verified 9,199 tracked prepared sources. No prior immutable release artifact changed.

The consumer has natively hydrated 513 current-release files with strict package/payload hashes. Independent queries resolve all 26 cases (pages of 10, 10 and 6) and return all 190 new result records with identical values and provenance. Its 885 tests, lint, typechecking and production build passed (29,479 static pages). The complete export check verified 28,665 rendered record pages and catalogue identities, generated metadata and local links, 100 historical paper pages, MFASS history and release checksums. This local preview explicitly permits the uncommitted producer revision; the final published lock must bind the actual producer commit. The temporary tracked test pin was restored to baseline after validation. Independent HTML checks passed for all 26 case pages and 190 new result pages, including exact printed/numeric technical metadata, locators and source links. The consumer baseline also gains the previously merged EGFR intake (nine records/two results), so its total change is 440 records and 192 results.

## Remaining delivery

The consumer’s committed pin remains `2026-10-07-e11db1d1c586` at data revision `aeb2b20033997330e46a3ff061edd0e54256f062`. The final pin requires the immutable producer revision and package checksum. This report does not assert a live deployment. Qualified human scientific review is unassigned. No experimental reproduction or new model execution is claimed.

[Parent #365](https://github.com/rewire-bio/rewire.it/issues/365), [original collection #3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3), data #10–#19, [runner #30](https://github.com/rewire-bio/rewire-benchmarks/issues/30), [consumer #97](https://github.com/rewire-bio/rewire-database/issues/97), [scientific review #31](https://github.com/rewire-bio/rewire-database/issues/31) and [articles #366](https://github.com/rewire-bio/rewire.it/issues/366) remain open for their actual completion contracts.
