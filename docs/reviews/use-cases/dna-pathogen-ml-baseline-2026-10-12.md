# DNA pathogen identification and RNA fusion: ML-versus-baseline sources, independent review, 2026-10-12

Batches (issue #121):

- `data/omics/use-case-coverage-dna-pathogen-20261012-bertax/` (Mock et al., PNAS 2022; 227 records, 153 results, 3 judgements)
- `data/omics/use-case-coverage-dna-pathogen-20261012-metagenn/` (Moreno et al., BMC Bioinformatics 2024; 58 records after review, 24 results, 2 judgements)
- `data/omics/use-case-coverage-rna-fusion-20261012-haas2019/` (Haas et al., Genome Biology 2019; source and 5 descriptive claims, no results)

Reviewer: a separate Claude review agent (rev-mlvb) that did not extract these batches. No human review is claimed. Nothing was executed or reproduced: this checks transcription and scope against the pinned sources.

## Outcome

- All three batches hold after the corrections below. Every record is `source_checked` and added with `records -- add` (SHACL passed for each).
- All 177 results match their sources. No value was changed.
- The five judgements are approved as `proxy`, with added limitations. One MetageNN evaluation is excluded from the isolates judgement.
- The use case `use-case-diagnostic-dna-pathogen-identification` gets five `assessed_by` links, a replacement for the gap that said no machine-learning method is compared with the baseline, one new gap and one amended gap.
- New metric concept `reference-storage-size` approved, with a reworded definition.

## Sources and hashes

All bytes were re-retrieved with curl into an empty scratch folder.

| Source record | Re-retrieved from | Result |
| --- | --- | --- |
| `dna-pathogen-20261012-bertax-source` | Europe PMC fullTextXML PMC9436379 | Matches `c0bb2f1b...b3bcd7` |
| `dna-pathogen-20261012-bertax-source-si` | `https://pmc-oa-opendata.s3.amazonaws.com/PMC9436379.1/pnas.2122636119.sapp.pdf` | Matches `89a2f86f...fbc1c0` (the pinned PDF member) |
| `dna-pathogen-20261012-bertax-source-pdf` | `www.pnas.org/doi/pdf/10.1073/pnas.2122636119` | Not re-verified. PNAS returns HTTP 403 (a Cloudflare challenge page) to curl, and this review did not use a browser. See below. |
| `dna-pathogen-20261012-metagenn-source` | Europe PMC fullTextXML PMC11022314 | Matches `ac4b1375...f14e12`; the archived `artifacts/PMC11022314.xml.gz` decompresses to the same bytes |
| `rna-fusion-20261012-haas2019-source` | Europe PMC fullTextXML PMC6802306 | Matches `98284288...65108`; the archived gzip decompresses to the same bytes |

The BERTax PDF hash `79774246...daec` was computed by the extractor inside a browser and its bytes were not saved, so it cannot be checked here. Instead, Table 1 was checked against the PMC open-access copy of the same version-of-record PDF (`https://pmc-oa-opendata.s3.amazonaws.com/PMC9436379.1/PMC9436379.1.pdf`, 1,342,319 bytes, SHA-256 `725c99ba8bb95d9e5e73997cbbe45d3a889185163749f494673a084de534c835`). Its bytes differ from the PNAS file (1,271,730 bytes), but its page-4 Table 1 is a text layer, and all 63 cells match the extractor's archived excerpt. The source record keeps the extractor's hash and now records the PMC copy in `review_artifact`, with `review_artifact_matches_original_artifact_sha256: false` and a limitation saying the pinned hash is not independently re-verified. The Table 1 results' reviews name the PMC copy as the checked artifact.

## How the values were checked

- BERTax: a separate parser written for this review read `pdftotext -layout` output of the PMC PDF (Table 1) and the SI PDF (Tables S2 and S5). It asserts the row labels and column counts, maps each result to its cell from its locator, and checks the evaluation's tool and dataset against the row and column. 153 of 153 cells match, with no duplicate or missing cell. The `random` rows are a chance reference and correctly not extracted.
- MetageNN: Table 1 read from its XML `table-wrap`, and each prose value found in its sentence, with sentence numbers counted from the XML paragraphs. 24 of 24 match. The relative improvements printed in the text (100%, 23%, 17%, 36%; 77%, 61%, 83%, 96%) are not recorded, which is correct: they are derived ratios, and the gap is listed in `coverage.json`.
- Haas: Table 1 rows and Discussion sentences compared verbatim with the claim values.
- Descriptive fields (dataset sizes, splits, class counts, the training-partition restriction, the 516-genome database, 81 isolates, 30 pseudo-mocks) were checked against the article text.

### BERTax Table 1 (macro AveP, %), PMC copy of the PNAS PDF page 4

| Tool | Close Supk. | Close Phyl. | Distant Supk. | Distant Phyl. | Final Supk. | Final Phyl. | Final Genus | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MMseqs2 | 92.19 | 85.66 | 62.76 | 41.36 | 96.94 | 92.90 | 74.76 | Match |
| MMseqs2 tax.∗ | 94.33 | 86.56 | 67.47 | 43.44 | 98.11 | 93.47 | 75.09 | Match |
| minimap2 | 86.12 | 76.06 | 44.12 | 20.03 | 93.46 | 86.71 | 66.68 | Match |
| Kraken2 | 86.26 | 75.99 | 44.36 | 19.50 | 93.65 | 87.13 | 70.56 | Match |
| sourmash | 30.69 | 9.04 | 25.14 | 3.48 | 31.04 | 8.00 | 3.07 | Match |
| DeepMicrobes | 97.18 | 86.62 | 67.25 | 36.61 | 98.13 | 92.11 | 66.43 | Match |
| BERTax | 95.65 | 83.88 | 90.06 | 54.10 | 98.62 | 95.10 | 66.92 | Match (see conflicts) |
| MMseqs2 + DeepMicrobes | 99.33 | 93.67 | 76.91 | 50.51 | 97.23 | 93.20 | 77.85 | Match |
| MMseqs2 + BERTax | 99.33 | 94.84 | 87.57 | 60.34 | 99.76 | 97.83 | 79.33 | Match |

### BERTax SI Table S2 (accuracy and proportion classified, %), SI page S15

| Tool | Close Supk. acc. | prop. | Close Phyl. acc. | prop. | Distant Supk. acc. | prop. | Distant Phyl. acc. | prop. | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MMseqs2 | 99.63 | 87.45 | 97.30 | 87.45 | 90.73 | 52.78 | 75.04 | 52.78 | Match |
| MMseqs2 taxonomy∗ | 98.06 | 92.69 | 92.62 | 92.69 | 80.50 | 71.37 | 59.19 | 71.37 | Match |
| minimap2 | 99.95 | 75.59 | 99.55 | 75.59 | 94.42 | 19.88 | 77.12 | 19.88 | Match |
| Kraken2 | 99.82 | 76.11 | 98.82 | 75.95 | 90.71 | 21.56 | 68.26 | 21.08 | Match |
| sourmash | 99.96 | 6.91 | 99.81 | 6.90 | 99.56 | 0.17 | 91.67 | 0.16 | Match |
| DeepMicrobes | 96.68 | 100 | 87.72 | 100 | 68.39 | 100 | 41.95 | 100 | Match |
| BERTax | 94.78 | 100 | 85.55 | 100 | 88.95 | 100 | 60.10 | 100 | Match |
| MMseqs2 + DeepMicrobes | 99.10 | 100 | 94.03 | 100 | 78.20 | 100 | 56.28 | 100 | Match |
| MMseqs2 + BERTax | 99.10 | 100 | 95.21 | 100 | 89.42 | 100 | 66.60 | 100 | Match |

All 36 accuracy cells: qualifier corrected (denominator). All 36 proportion cells: direction corrected to `unknown`.

### BERTax SI Table S5 (accuracy on the distantly related set, %), SI page S16

| Tool | Supk. unfiltered | Supk. filtered | Supk. left-out | Phyl. unfiltered | Phyl. filtered | Phyl. left-out | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BERTax | 88.95 | 88.30 | 93.48 | 60.10 | 59.15 | 63.52 | Match |
| DeepMicrobes | 68.39 | 63.24 | 81.13 | 41.95 | 39.89 | 47.80 | Match |
| MMseqs2 taxonomy∗ | 80.50 | 74.51 | 95.83 | 59.19 | 53.31 | 80.36 | Match |

All 18: qualifier corrected (denominator). The "unfiltered" column repeats the Table S2 accuracy for the same tools; both are kept because they are separate printed cells with different qualifiers.

### MetageNN

| Result | Metric | Printed | Numeric | Locator | Outcome |
| --- | --- | --- | --- | --- | --- |
| `genet-resources-speed` | inference-throughput | 134 | 134 | Table 1, row "GeNet", column "Speed (reads/sec)" | Match |
| `genet-resources-storage` | reference-storage-size | 0.758 | 0.758 | Table 1, row "GeNet", column "Memory (GB)" | Match; unit_detail added |
| `kraken2-isolates-all-f1` | f1-score | 0.83 | 0.83 | Results 'Results for all genomes' paragraph 1, sentence 4 (values shown in Fig. 3a) | Match; sentence number corrected |
| `kraken2-isolates-all-recall` | recall | 0.79 | 0.79 | Results 'Results for all genomes' paragraph 1, sentence 4 (values shown in Fig. 3a) | Match; sentence number corrected |
| `kraken2-mocks-reads-classified` | proportion | 64.90% | 64.90 | Results 'Read classification results' paragraph 1 (values shown in Fig. 4a) | Match; direction set to unknown |
| `kraken2-resources-speed` | inference-throughput | 13.471 | None | Table 1, row "Kraken2", column "Speed (reads/sec)" | Match; numeric null kept (see conflicts) |
| `kraken2-resources-speed-text` | inference-throughput | 13,471 | 13471 | Results 'MetageNN is faster and requires less storage than alignment and k-mer-based tools, respectively' paragraph 3, sentence 5 | Match; conflicts with the Table 1 cell; sentence number corrected |
| `kraken2-resources-storage` | reference-storage-size | 3.7 | 3.7 | Table 1, row "Kraken2", column "Memory (GB)" | Match; unit_detail added |
| `megan-lr-mocks-reads-classified` | proportion | 53.06% | 53.06 | Results 'Read classification results' paragraph 1 (values shown in Fig. 4a) | Match; direction set to unknown |
| `megan-lr-resources-speed` | inference-throughput | 606 | 606 | Table 1, row "MEGAN-LR", column "Speed (reads/sec)" | Match |
| `megan-lr-resources-storage` | reference-storage-size | 5.1 | 5.1 | Table 1, row "MEGAN-LR", column "Memory (GB)" | Match; unit_detail added |
| `metagenn-isolates-out-gt3-f1` | f1-score | 0.88 | 0.88 | Results 'Results for “Species out of the database” settings' paragraph 3, last sentences (values shown in Fig. 3f) | Match |
| `metagenn-isolates-out-gt3-recall` | recall | 0.87 | 0.87 | Results 'Results for “Species out of the database” settings' paragraph 3, last sentences (values shown in Fig. 3f) | Match |
| `metagenn-mocks-reads-classified` | proportion | 93.26% | 93.26 | Results 'Read classification results' paragraph 1 (values shown in Fig. 4a) | Match; direction set to unknown |
| `metagenn-resources-speed` | inference-throughput | 1424 | 1424 | Table 1, row "MetageNN", column "Speed (reads/sec)" | Match |
| `metagenn-resources-storage` | reference-storage-size | 0.839 | 0.839 | Table 1, row "MetageNN", column "Memory (GB)" | Match; unit_detail added |
| `metamaps-mocks-reads-classified` | proportion | 37.30% | 37.30 | Results 'Read classification results' paragraph 1 (values shown in Fig. 4a) | Match; direction set to unknown |
| `metamaps-resources-speed` | inference-throughput | 194 | 194 | Table 1, row "MetaMaps", column "Speed (reads/sec)" | Match |
| `metamaps-resources-storage` | reference-storage-size | 2.2 | 2.2 | Table 1, row "MetaMaps", column "Memory (GB)" | Match; unit_detail added |
| `mmseqs2-isolates-all-f1` | f1-score | 0.85 | 0.85 | Results 'Results for all genomes' paragraph 1, sentence 4 (values shown in Fig. 3a) | Match; sentence number corrected |
| `mmseqs2-isolates-all-recall` | recall | 0.81 | 0.81 | Results 'Results for all genomes' paragraph 1, sentence 4 (values shown in Fig. 3a) | Match; sentence number corrected |
| `mmseqs2-mocks-reads-classified` | proportion | 85.49% | 85.49 | Results 'Read classification results' paragraph 1 (values shown in Fig. 4a) | Match; direction set to unknown |
| `mmseqs2-resources-speed` | inference-throughput | 588 | 588 | Table 1, row "MMseqs2", column "Speed (reads/sec)" | Match |
| `mmseqs2-resources-storage` | reference-storage-size | 27.8 | 27.8 | Table 1, row "MMseqs2", column "Memory (GB)" | Match; unit_detail added |

### Haas et al. 2019

| Claim | Locator | Outcome |
| --- | --- | --- |
| `rna-fusion-20261012-haas2019-claim-arriba-filters` | Table 1, row 'Arriba' | Verbatim |
| `rna-fusion-20261012-haas2019-claim-ericscript-classifier` | Table 1, row 'EricScript' | Verbatim |
| `rna-fusion-20261012-haas2019-claim-star-fusion-filters` | Table 1, row 'STAR-Fusion' | Verbatim |
| `rna-fusion-20261012-haas2019-claim-top-performers` | Discussion paragraph 2, sentence 1 | Verbatim |
| `rna-fusion-20261012-haas2019-claim-ericscript-least-accurate` | Discussion paragraph 2, sentence 5 | Verbatim; locator corrected from sentence 4 |

The extractor's finding stands: the paper prints no per-method accuracy value in a table or the text, so no protocol, result or judgement is added for the RNA fusion use case, and its gap about Haas et al. 2019 is unchanged.

## Corrections

BERTax:

1. Accuracy denominator. Tables S2 and S5 do not say what "acc." is computed over. It must be the samples each tool classified: sourmash prints 99.56% superkingdom accuracy with 0.17% of the distantly related set classified, which is impossible over all samples (at most 0.17%, or about 25% if unclassified samples were scored as random guesses), and the Table S5 caption notes that MMseqs2 taxonomy* "is only able to make predictions for 71.37% of all sequences". The 54 accuracy results now say "among the samples the tool classified", and the closely and distantly related protocols state this basis instead of leaving it open.
2. Proportion classified: direction changed from `higher` to `unknown` (36 results). Classifying more samples is not better by itself; the paper describes a trade-off with accuracy, and BERTax and DeepMicrobes reach 100% "due to their mode of operation without confidence thresholds".
3. Final-dataset protocol: its metric definition, limitation and locator referred to Table S2, which has no final-dataset columns. They now describe macro AveP only. The final judgement's `source_locator` is corrected the same way.
4. Judgement limitations: added that macro AveP scores unclassified samples as random guesses, so it partly reflects how many samples each tool classifies (with Kraken2 and minimap2's classified shares from Table S2), and that Table S2 accuracy must be read with the proportion classified. The author-reported limitation now says the authors developed BERTax.
5. Training-data claim locator: "Results paragraph 4" changed to "Results opening paragraph 3", which is the paragraph that prints 2,492,474 (the fourth `<p>` only if the Fig. 1 caption is counted).

MetageNN:

6. Duplicate method: the batch created `dna-pathogen-20261012-metagenn-method-metamaps`, but `dna-pathogen-20261009-method-metamaps` already exists (Portik et al. 2022 pass). The new record is removed and `dna-pathogen-20261012-metagenn-config-metamaps` now configures the existing one. `coverage.json` is updated.
7. Isolates judgement: the protocol's baseline values (Kraken2, MMseqs2) are means over all 81 isolates, while the only printed MetageNN values are for out-of-database isolates in genera with more than three species. No printed baseline value covers that subset, so showing MetageNN on this judgement would suggest a same-data comparison that the printed numbers do not support. `dna-pathogen-20261012-metagenn-eval-metagenn-isolates` is listed in `excluded_evaluations` with that reason, and the rationale and endpoint now describe Kraken2 and MMseqs2 over all isolates.
8. Mocks judgement: added that the pseudo-mocks are assembled in silico from isolate reads, and that a larger share of reads assigned is not better by itself (correctness is only in Figure 4b).
9. Share of reads classified: direction changed from `higher` to `unknown` (5 results), as in correction 2. The qualifier already says "correct or not".
10. Locators: the Kraken2 speed sentence is sentence 5 of paragraph 3, not 4; the all-isolate MMseqs2 and Kraken2 values are in sentence 4 of paragraph 1, not 3.
11. Storage results: `unit_detail` "GB as printed", as the gigabyte concept asks.
12. Out-of-database ranking claim: added the source's own qualification that the precision differences were "non-significant results except for MEGAN-LR".

Haas: 13. The EricScript ranking sentence is sentence 5 of Discussion paragraph 2, not 4.

The extractors' scripts in each batch's `extract/` reproduce the pre-review `batch.jsonl`, not the reviewed one; the differences are exactly the corrections above.

## Conflicts

- BERTax 95.20 against 95.10. The Results text ("Performance of Final BERTax Model", paragraph 1) prints 95.20% for BERTax phylum AveP on the final dataset; Table 1 (in both the PNAS PDF text layer and the PMC PDF) and SI Table S7's BERTax row print 95.10. Stored: the Table 1 cell, 95.10, with `source_discrepancy` on the result and the `printed_value_conflict` claim `dna-pathogen-20261012-bertax-claim-final-phylum-discrepancy`. No source `evidence_concerns`: two tables agree, the text is the outlier, and the 0.1-point difference changes no ordering (BERTax is above every database tool at 95.10 or 95.20, and below MMseqs2 + BERTax at 97.83 either way). A concern would withhold all 153 results for a typographical difference.
- MetageNN 13.471 against 13,471. Table 1 prints Kraken2 speed as "13.471" reads/sec, bolded as the best; the Results text prints 13,471 and calls Kraken2 the fastest; the Discussion says MetageNN (1424 reads/sec) "was slower than Kraken2". So the cell's "." is a thousands separator or typesetting error. Stored: the cell with `printed_value` "13.471" and `numeric_value` null, and the text value as a separate result, "13,471" with numeric value 13471. Both carry `source_discrepancy`. No source concern: the source resolves the conflict itself, and the value sits on the resources protocol, which no judgement uses.

## Records reused and method types

Configuration links checked against the store: `catalog-model-kraken2`, `dna-pathogen-20261009-method-minimap2`, `dna-pathogen-20261009-method-sourmash`, `dna-pathogen-20261009-method-megan-lr`, `dna-pathogen-20261009-method-metamaps` (after correction 6) and `discovery-model-mmseqs2`. There is no other MMseqs2, DeepMicrobes, BERTax, MetageNN or GeNet record, so the new models and pipelines are not duplicates. `discovery-model-mmseqs2` is a discovered method record tagged protein-function, but its reviewed profile describes nucleotide search and "configured taxonomic assignments", so reuse is right; its area facet is a separate question. The 27 BERTax configurations (one per tool and dataset) are justified because each dataset gives the tools a different reference or training partition. Method types: BERTax, DeepMicrobes, MetageNN and GeNet `supervised_machine_learning`; the MMseqs2 hybrids both tags; the database and alignment tools `conventional_pipeline`. Every evaluation is `author_reported`, which is right: Mock et al. developed BERTax and Moreno et al. developed MetageNN, and each ran every tool.

## New metric concept

`reference-storage-size` (data/vocab/metric.ttl) is needed: MetageNN Table 1 "Memory (GB)" is "the memory requirements to store its database" (Kraken2's database, MetaMaps' reference database, MMseqs2's indices, MetageNN's learned weights). `peak-memory`, which already has the alt label "Memory (GB)", is memory used while running, so using it would be wrong. No concept in the scheme covers stored size, and no STATO, QUDT or EDAM class matches, so there is no external match. Default direction `lower` is right. The definition is reworded from "what a classifier consults" to "what a method consults", with a pointer to peak memory.

## Judgements

| Judgement | Relevance | Evaluations reviewed | Excluded | Notes |
| --- | --- | --- | --- | --- |
| `use-case-mapping-dna-pathogen-20261012-bertax-closely` | proxy | 9 | none | Test genera present in the reference |
| `use-case-mapping-dna-pathogen-20261012-bertax-distantly` | proxy | 9 | none | Test genera absent from the reference; bears on the question about organisms absent from the reference |
| `use-case-mapping-dna-pathogen-20261012-bertax-final` | proxy | 9 | none | Larger reference, genus rank |
| `use-case-mapping-dna-pathogen-20261012-metagenn-isolates` | proxy | 2 (Kraken2, MMseqs2) | MetageNN (correction 7) | Real ONT isolate reads, genus level |
| `use-case-mapping-dna-pathogen-20261012-metagenn-mocks` | proxy | 5 | none | Share of reads assigned, not correctness |

Proxy, not direct, for all five: the use case asks about diagnostic specimens (plasma cell-free DNA in its decision), and these use simulated 1,500-nt genome fragments, or ONT reads from cultured bacterial isolates and in silico pseudo-mocks, with 516-genome or training-partition references, at genus rank or above. Each judgement's limitations now carry those caveats, the source's own design caveats (training-partition references, unclassified samples as random guesses, figures-only accuracy) and the developer-authorship of each paper. No judgement was drafted for the MetageNN resources protocol (storage and speed), which does not answer the detection question; that is right.

The judgements were pinned with `npm run use-cases:repin -- docs/reviews/use-cases/dna-pathogen-ml-baseline-2026-10-12.md <five claim IDs>`.

## Use-case changes

Applied to `use-case-diagnostic-dna-pathogen-identification` with `records -- change` and this review:

- `assessed_by` links to the five protocols above.
- Gap replaced. Old: "No machine-learning method has been compared with Kraken2, minimap2 or MEGAN-LR on the same data in the linked evidence." New: "In the linked evidence, machine-learning classifiers are compared with the baseline only on simulated or isolate-derived data, in papers by the developers of BERTax and MetageNN: BERTax and DeepMicrobes against Kraken2 and minimap2 on simulated 1,500-nt genome fragments at superkingdom, phylum and genus rank (Mock et al. 2022), and MetageNN against Kraken2 and MEGAN-LR on ONT reads from 30 pseudo-mock communities of species absent from the reference, where the only printed endpoint is the share of reads assigned at genus level, not whether they were assigned correctly (Moreno et al. 2024). No machine-learning method is compared with the baseline on clinical specimens or at species level."

  This differs from the extractor's proposal in four ways. "Constructed data" is replaced by "simulated or isolate-derived data", because the MetageNN reads are real ONT reads. The MetageNN comparison is limited to the pseudo-mocks, because after correction 7 no linked judgement shows MetageNN beside a baseline on the isolates. It names the developer authorship. And it keeps "in the linked evidence". Checked against the baseline claim `use-case-baseline-diagnostic-dna-pathogen-identification` ("Kraken2 and minimap2 with MEGAN-LR", method IDs Kraken2, minimap2 and MEGAN-LR): BERTax scores Kraken2 and minimap2 (minimap2 alone, not with MEGAN-LR), MetageNN scores Kraken2 and MEGAN-LR on minimap2 alignments. No other linked protocol scores a machine-learning method beside these, so the last sentence holds.
- Gap added: "Moreno et al. 2024 show per-tool sensitivity, precision and F1 for MetageNN, Kraken2, MEGAN-LR, MetaMaps and MMseqs2 only in Figures 3 and 4; these were not extracted."
- Gap amended, because it listed only two indirect sources for organisms absent from the reference and would be incomplete with the new judgements active: it now adds "genus or species exclusion on non-clinical data (the distantly related set of Mock et al. 2022; out-of-database species in Moreno et al. 2024)". Its last sentence, "No clade-exclusion benchmark with a pathogen focus was extracted", still holds.

Not changed: `evidence_checked` (this was not a literature search), the collection plan, and the RNA fusion use case.

## Publication state

Checked with `deriveUseCaseInputs` on the store before and after these changes (378 mappings before, 383 after):

- The five new judgements are active, with 9, 9, 9, 2 and 5 evaluations.
- No mapping changed state: the 351 previously active mappings stay active, and the 20 withheld and 7 draft mappings are unchanged.
- The baseline for DNA pathogen identification still publishes.
- The DNA pathogen summary (`use-case-summary-diagnostic-dna-pathogen-identification`) is now withheld. A summary pins the reviewed evaluations of all the use case's reviewed judgements, so the five new judgements change its pins. Its text is still accurate as far as it goes, but it does not mention the new evidence. It is not rewritten or re-pinned here; that needs its own review. Every other use case's summary and baseline is unchanged.

## Remaining gaps

- The PNAS PDF hash is the extractor's in-browser hash, not re-verified. A later browser check can confirm it.
- BERTax: PR and ROC curves, confusion matrices and the architecture and ablation tables (S1, S3, S4, S6, S7) are not extracted; no tool versions or uncertainty are printed.
- MetageNN: per-tool accuracy for isolates (Figure 3) and communities (Figure 4b) is figures-only; the resources protocol does not say which reads were timed.
- Haas et al. 2019: accuracy is figures-only; the per-fusion predictions in Additional file 1 are not enough for a derivation because the scoring rules are not stated precisely.
- No search-ledger or scope-audit entries: the sources were named in issue #121, not found by search.
