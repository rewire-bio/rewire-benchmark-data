# Controlled vocabularies, 2026-10-09

Stage 1 of [issue #42](https://github.com/rewire-bio/rewire-benchmark-data/issues/42): free-text values in the canonical store are replaced by keys of SKOS concepts in `data/vocab/`. Record IDs, printed and numeric values, source evidence and locators are unchanged. 17,288 of 28,719 records changed; each change is recorded in `data/provenance/records.jsonl` with inputs `data/vocab/migration` and this review.

## Method

Reviews were AI-assisted; no human review is claimed.

1. Two drafting agents profiled every distinct value with example records, wrote one concept scheme per field, and mapped every current value to concepts. External matches were verified against downloaded releases: STATO 2026-04-20, QUDT units 3.5.2 and EDAM 1.25. Every cited IRI exists and is not deprecated.
2. A third, independent agent joined all 12,508 results to the metric table and grouped them by concept, qualifier and protocol to look for values that would become falsely comparable. It checked every external match and spot-checked benchmark-specific definitions against ProteinBench (arXiv 2409.06744), Genie 3 (bioRxiv 10.64898/2026.05.01.722168), the CPPC competition paper (PMC13228547) and public Virtual Cell Challenge material.
3. All of its must-fix findings were applied before migration (below). A trial migration on a copy of the store validated before the real run.

## Schemes

| Scheme | Field | Concepts | Source values | External matches |
| --- | --- | --- | --- | --- |
| metric | `attributes.metric` | 174 | 536 | STATO |
| unit | `attributes.unit` | 16 | 41 | QUDT |
| area | `facets.areas` | 15 | 22 | EDAM topics |
| method-type | `facets.method_types`, `attributes.method_type` | 5 | 6 | |
| context | `facets.contexts` | 1 | 1 | |
| publication-status | `attributes.publication_status` | 3 | 5 | |
| origin | `attributes.origin` | 5 | 5 | |
| direction | `attributes.metric_direction` | 3 | 3 | |
| entity-level | `attributes.entity_level` | 10 | 9 | |
| baseline-type | `attributes.baseline_type` | 12 | 13 | |
| configuration-type | `attributes.configuration_type` | 3 | 3 | |
| review-method | `review.method` | 11 | 39 | |
| agent | `review.reviewer`, `review.actor` | 6 | 22 | |
| status | `status` | 7 | 7 | |

Closed lists that code already compares against (status, origin, direction, publication status, entity level and the like) keep their existing spellings as keys, so only genuine merges change those values.

## What the migration does

- **Metrics.** Each source string maps to one concept. Where a string carries more than the concept (a class, a setting such as zero-shot, a scope such as SNV only, a cutoff, or an aggregation such as median over targets), the text goes into `metric_qualifier` (239 of the 536 strings). Results are comparable only when metric, qualifier, unit and direction all match, and curated panels take their metric, unit and qualifier from their results.
- **Units.** Strings that named a quantity rather than a unit (score, correlation, AUC, F1 score) become `unitless`. Detail a unit concept cannot hold (the counted entity, a printed scale) goes into `unit_detail`. The catch-all "score" is resolved per metric (`unit-by-metric.csv`). RMSD and Rosetta energies labelled "score" become `unit-unreported`, because the sources do not state their units.
- **Areas.**
  - Near-duplicates are merged: genomics into dna-genomes; rna and rna-transcriptomics into rna-transcriptomes; microbiome into microbes-communities; glycomics into glycans; cells-spatial-multiomics into cells-tissues.
  - `molecular-omics` is split by record (`area-by-record.csv`): MSAlign records become metabolomics and MIMIC records become rna-transcriptomes.
- **Review method and reviewer.** Each sentence becomes method concepts plus `method_note`, and each reviewer string becomes agent concepts plus `reviewer_note`. Nothing in the original sentences is lost.
- **Retired.** `facets.domain` (26 records) duplicated `areas` and is removed.

## Corrections from the independent review

1. The 21 ProteinGym zero-shot substitution NDCG rows are NDCG at the top 10% and now share `ndcg-at-10-percent` with the AMFR rows (`metric-by-record.csv`). Other `ndcg` rows carry the qualifier "cutoff not stated".
2. `new_candidates_per_1000` is its own concept, a rate per 1000 cases per reanalysis cycle, not candidates per case.
3. Cosine similarity is split into spectrum (MassSpecGym) and fingerprint (MIST, DreaMS) concepts.
4. Several ProteinBench definitions are corrected from appendix B.1.4:
   - CN-score is the peptide-bond length density;
   - total energy is summed over CDR-H3 residues;
   - binding energy is CDR-H3 to antigen, from InterfaceAnalyzer;
   - SeqNat is marked as an unconfirmed transform.

   Antibody AAR, RMSD and TM-score rows carry the qualifier "cdr-h3" (and "ca atoms" for RMSD).
5. The Genie 3 diversity and novelty definitions no longer assert an unstated denominator or formula, and carry an "unverified" scope note.
6. The CPPC concepts name the Cancer Immunotherapy Machine Learning Competition. Challenge 2's score is the minimum of the filtered and unfiltered averages. The reimplemented column-J rows carry the qualifier "reimplemented model; scoring rule unconfirmed".
7. The Virtual Cell Challenge score is described as an organiser-defined composite whose 2026 formula is unpublished.
8. Seventeen result directions are corrected (`direction-by-record.csv`):
   - ENIGMA high-benign and low-pathogenic fractions become lower;
   - the middle-interval fractions and descriptive reanalysis shares become unknown;
   - mean total fusions identified becomes unknown.
9. Match relations that overstated equivalence are weakened:
   - log loss to STATO log likelihood becomes relatedMatch;
   - MCC (binary only in STATO) becomes closeMatch;
   - the general correlation coefficient becomes closeMatch;
   - success rate, unassigned rate and percent agreement become broadMatch;
   - squared Pearson becomes relatedMatch.

## Known limitations, for later releases

- 24 metric strings remain marked uncertain in `metric.csv`, each with its reason. Examples: bare "AUC" assumed to be ROC; `f1` with mixed averaging, where Open Problems is probably weighted and GUE probably macro; ligand pass rate with an unrecorded criterion.
- Top-k accuracy mixes retrieval and de novo exact-match settings without a qualifier. LiPP ligand RMSD is all-atom; Boltz RMSDs are medians.
- Units are inconsistent between rows:
  - TM-score, AUROC and NDCG use fraction on some rows and unitless on others;
  - BEACON correlations ×100 are stored as percent;
  - MCES distances are counted rather than unitless.
- Some area matches are loose: molecular-interactions should probably match EDAM topic_0128. Cells-spatial-multiomics records might belong under single-cell.
- Some concepts sit in the wrong scheme. Method type `baseline` is a role, and some baseline types (random forest, linear regression, gradient-boosted trees) are algorithms.
- Values recording missing data (origin `unreported`, direction `unknown`) and entity levels that repeat the record kind are left for stage 3 (declared attributes and `missing_metadata`).
