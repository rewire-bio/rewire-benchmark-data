# Research notes

Scope: rewire-benchmark-data#142, the follow-up to #19 and PR #141. Extract the Feng et al. 2025 parts still missing from the store: Supplementary Data 4, the Table 2 rows other than Arabidopsis, and the Table 3 rows other than the two Human 5mC cells. Bounded to one paper; not a literature search.

## Existing records reused, none changed

- Sources: `evidence-expansion-dna-foundation-models-2025-5d8ca9bc` (article XML), `feng-dna-fm-20261013-source-supplementary-data` (workbook) and `feng-dna-fm-20261013-source-supplementary-information` (PDF). All three artifacts were re-downloaded on 2026-10-14 and match their stored SHA-256, so no new source record was needed.
- Supplementary Data 4: the 59 existing Table 5 and Table 6 evaluations (`amp-feng-20261007-eval-variant-*`, `amp-feng-20261007-eval-qtl-*`). Each block and configuration gets a new per-group evaluation with the same configuration, protocol and dataset as the existing evaluation (changed at review; see below). The stored evaluations and mean results are untouched.
- Table 3 Human 5mC: results `lit-001` (Caduceus-Ph) and `lit-002` (NT-v2) stay as they are. The other three cells use the existing task `reported-task-988ff78f86471e` (via `evaluates_task` on the new protocol) and the existing dataset `reported-dataset-463197d6a98b99` (as the evaluations' `data` link).
- `feng-dna-fm-20261013-claim-not-extracted` is superseded by `feng-dna-fm-20261014-claim-not-extracted` through a `supersedes` link. The reviewer set the old claim's status to `superseded` with `records -- change`.

## Added in this batch (698 records)

| Part | Results | Other records |
| --- | --- | --- |
| Table 2, 8 rows (B. amyloliquefaciens and R. capsulatus promoters, human vs worm, mouse TFBS 1-5) | 40 AUC | 8 datasets, 8 protocols, 40 configurations, 40 evaluations, 8 baseline-CNN claims |
| Table 3, 18 rows (Human 5mC: 3 remaining cells; human 6mA, 10 yeast marks, 6 species 4mC: all cells) | 88 AUC | 17 datasets, 18 protocols, 88 configurations, 88 evaluations, 18 baseline-CNN claims |
| Supplementary Data 4, 5 blocks x 11 or 12 models x 3 test groups | 177 AUC | 59 per-group evaluations on the existing configurations, protocols and datasets |
| Inventory | | 1 `tables_not_extracted` claim |

Datasets carry training and test sizes, length statistics and class counts from Supplementary Data 6, and the Supplementary Note 2 evidence flags: mouse TFBS 1-5 are "No" (not fully relying on experimental evidence or gold-standard sources) and "All Yeast Datasets" are "Unknown". The three eukaryotic 4mC datasets carry the Methods caveat that their annotations often rely on computational predictions; the Results call these tasks exploratory.

## Supplementary Data 4

- Sheet "Data 4" has five blocks in the order the legend gives (pathogenic vs common, eQTL, sQTL, paQTL, ipaQTL), each with columns "Test Group 1 AUC", "Test Group  2 AUC" (two spaces, as printed) and "Test Group 3 AUC". Groups 1-3 are the chromosome sets in Methods, "Variant effect quantification benchmark".
- Cells are stored as binary doubles in General number format. `printed_value` is the shortest decimal, which is what the workbook displays (at most 4 decimals; asserted).
- Each result's `metric_qualifier` is the existing Table 5/6 qualifier plus "outer test group N only (chromosomes ...), not averaged", so per-group values are never compared with the stored three-group means. The existing evaluations' `comparison.aggregation` says "Mean ... across the three outer chromosome test folds"; that describes the stored mean results, not these. At review the per-group results were moved to their own evaluations (see Review outcome).
- Linkage check: for all 59 rows the mean of the three displayed values is within 0.0001 of the stored Table 5/6 AUC. 50 match exactly; 9 differ in the fourth decimal, consistent with averaging unrounded values (`extract/sd4-mean-check.json`).
- Supplementary Data 4 prints AUC only. Per-group Cohen's d is not published; recorded as a gap.

## Frozen embeddings versus label-free scoring

Every result here is frozen pretrained representations plus a supervised random forest fitted on the task labels (Tables 2-3: mean token embeddings; Supplementary Data 4: the existing alternate-minus-reference set-up, including the Sei, Enformer and AlphaGenome comparators). None is label-free scoring. Every new protocol, configuration and evaluation says so.

## Use-case mapping decisions

No new mappings.

- Table 2 bacterial promoters, human vs worm and mouse TFBS: none of the 26 use cases makes these decisions. `use-case-plant-promoter-reporters` keeps only the Arabidopsis rows.
- Table 3 human 5mC and 6mA: these classify 41 bp genomic sequences for a modification site. `use-case-plasma-ctdna-methylation` concerns detecting tumour DNA from plasma methylation data, which these tasks do not measure; not mapped.
- Table 3 yeast and 4mC: outside every use case.
- Supplementary Data 4: the five protocols are already mapped as proxy (pathogenic vs common to `use-case-rare-disease-candidate-ranking`; the four QTL protocols to `use-case-regulatory-variant-gene-follow-up`). The per-group results inherit those proxy labels through their evaluations. No mapping is added or changed.

## Why the batch is not yet in the store

A trial `records add` on 2026-10-14 succeeded (SHACL subgraph check passed, 639 records added) and `records -- check` passed. `npm test` then failed two tests in `tests/use-case-records.test.ts`: active judgements dropped from 97 to 92, and 5 reviewed judgements had pins that no longer match the store. Re-pinning is a review action, so the store write was reverted. The reviewer should run `records add`, review and re-pin the five judgements, and then run the tests.

Consequence for review: judgements pin the results of their reviewed evaluations. The new per-group results sit on those evaluations, so after the store write the five judgements on the Table 5 and Table 6 protocols (and any summary built on them) are withheld until the reviewer re-pins them with `npm run use-cases:repin`.

## Source discrepancies found

- Supplementary Data 4 labels the short-window HyenaDNA row "HyenaDNA-160K". Tables 5 and 6 print "HyenaDNA", and Methods ("Model configuration selection") say Hyena-450K was used for gene expression and variant effect quantification. The row is linked to `amp-feng-20261007-eval-*-hyenadna` because its means match; which checkpoint produced it is left for review (noted on each affected result).
- Methods ("Sequence classification datasets", the paragraph defining the four categories) list "detection of N4-methylcytosine (4mC) sites" as an example of a human epigenetic task, but every 4mC dataset is non-human (Table 3; Methods, "Sequence classification datasets").
- Supplementary Note 1 names the Genomic Benchmarks set "Human vs Worm" and Table 2 prints "Human vs worm"; Supplementary Data 1, 2 and 6 use "Human vs Worm". Same dataset; recorded only for locators.

## Review outcome (independent reviewer, 2026-10-14)

Dated review: `docs/reviews/2026-10-14-feng-remaining-tables.md`. Use-case re-review: `docs/reviews/use-cases/feng-variant-effect-per-group-2026-10-14.md`.

- Per-group evaluations. The record contract makes `comparison.aggregation` an evaluation field, and comparisons require it to match. The stored Table 5/6 evaluations say "Mean of AUC/Cohen's d across the three outer chromosome test folds", which is false for a per-group value. The store already keeps a different aggregation on its own evaluation for the same configuration and protocol (for example the SCMBench per-dataset and overall evaluations). So `extract_feng.py` now writes 59 evaluations `feng-dna-fm-20261014-eval-sd4-<block>-<configuration>`, each with the stored evaluation's links and comparison except `aggregation`, which says "Per outer chromosome test group ... not averaged". No reviewed evaluation gains a result, so no judgement is withheld by a pin change.
- Use cases. The 59 new evaluations sit on five mapped protocols and would otherwise appear on the use-case pages beside the means. The five judgements were re-reviewed: relevance holds, the new evaluations are excluded with a reason, and one limitation on per-group spread was added to each.
- HyenaDNA-160K. Not a conflict. Methods name Hyena-160K as the default checkpoint and Hyena-450K for variant effect quantification "to leverage its ability to process longer sequences". Tables 5 and 6 print the short-window row as "HyenaDNA" and the long-input row as "HyenaDNA-450K, long sequence", and Supplementary Data 4 lists both. The short row's link is kept; the result notes now say this.
- 4mC labelled human. A source inconsistency, not an extraction error. All six 4mC datasets keep their printed species, and each now carries a note quoting the Methods category description. The eukaryotic ones also note that Supplementary Note 2 marks them "Yes" for experimental evidence while Methods say their annotations often rely on computational predictions.
- Superseded inventory claim. `feng-dna-fm-20261013-claim-not-extracted` is now `superseded`.
