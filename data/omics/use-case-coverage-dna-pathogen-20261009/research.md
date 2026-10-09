# Research: DNA pathogen-identification use-case pass, 2026-10-09

Use case: `use-case-diagnostic-dna-pathogen-identification` ("Which DNA sequencing classification workflow detects clinically relevant pathogens and handles contamination or organisms absent from the reference?"). Before this pass it had one judgement: Karius plasma cfDNA positive percent agreement against initial blood culture, a single result with no comparator.

Goal: published comparisons of several workflows on the same clinical or clinically realistic DNA data, with per-tool values printed in tables.

Bounds: cutoff 2026-10-09; budget 25 queries, 19 used (one failed); at most three sources extracted. Lane `microbial`. RNA virus detection was out of scope. Values read from figures were not allowed.

## Queries

All 19 are in `data/omics/search-ledger.jsonl` as `search-use-case-dna-pathogen-microbial-q1` to `q19`, with exact query strings, times and gaps.

| # | Query (shortened) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | taxonomic classifiers clinical metagenomic pathogen detection Kraken2 Centrifuge Kaiju precision recall | web | Govender and Eyre 2022; respiratory virus classifier study (excluded, RNA viruses) |
| 2 | clinical mNGS pipelines CZ ID SURPI DRAGEN BugSeq Kraken2 spiked samples | web | No head-to-head of the named clinical pipelines; ENNGS viral benchmark (excluded) |
| 3 | Portik 2022 long-read profiling mock communities | web, Europe PMC | Portik et al. 2022 (extracted); Valencia 2024 and Van Uffelen 2024 screened |
| 4 | CAMI II pathogen detection challenge | web | Followed in q17 |
| 5 | false-positive species, host background, spike-in | web | Older leads only |
| 6 | clinical mNGS pipeline comparison, culture or PCR reference | web | Developers' in-house pipeline validations (not opened) |
| 7 | Europe PMC title/abstract query with quoted wildcard | Europe PMC | Failed: zero hits |
| 8 | Europe PMC title/abstract query, corrected | Europe PMC | 4 hits; one new lead (PMC13623680, not opened) |
| 9 | Europe PMC abstract query with precision or sensitivity terms | Europe PMC | 5 single-assay validations |
| 10 | external quality assessment of mNGS bioinformatics | web | None with per-pipeline values; viral proficiency test only |
| 11 | nanopore clinical metagenomics tool comparison | web, Europe PMC | Lao et al. 2024 16S (accuracy in prose only) |
| 12 | LEMMI unknown organisms, host contamination | web | LEMMI, LEMMIv2, host-removal benchmark (not opened) |
| 13 | shotgun clinical samples, classifier agreement with culture | web, Europe PMC | Song et al. 2025 (extracted); Peterson et al. 2022 (figure-only) |
| 14 | in silico human background with spiked pathogens | web, Europe PMC | SEPATH (figure-only) |
| 15 | patient samples, culture reference, joint, urine, lower respiratory | web, Europe PMC | Watts et al. 2019, Buffet-Bataillon 2022 (not extracted) |
| 16 | Kraken2, Centrifuge, BugSeq, CZ ID on nanopore blood cultures | web, Europe PMC | BugSeq developer paper (not extracted) |
| 17 | Europe PMC: CAMI II paper | Europe PMC | Pathogen challenge is an RNA virus with manually curated submissions (excluded) |
| 18 | clade exclusion, organisms absent from reference | web | Developer papers only (not opened) |
| 19 | 2025-2026 clinical pipeline benchmarks | web, Europe PMC | Hall and Coin 2024 (extracted) |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Portik et al. 2022, Table 4 | Extract all 560 cells | The broadest independent comparison found: 14 configurations (Kraken2, Bracken, Centrifuge x2, MetaPhlAn3, mOTUs2, sourmash x2, MetaMaps, MMseqs2, MEGAN-LR x3, BugSeq) on six DNA mock-community datasets, with false-positive counts that bear directly on contamination-like spurious calls |
| Song et al. 2025, Tables 1 and 2 | Extract all cells | The only multi-pipeline comparison found on patient DNA specimens with a reference standard and negative controls (BLAST, Kraken, MetaPhlAn, RTG Core; five blood-culture-positive samples) |
| Hall and Coin 2024, Tables 5-8 | Extract all 120 cells | Shows how reference database completeness changes identification of a clinically relevant pathogen (M. tuberculosis): kraken and minimap2 with standard and pathogen-focused databases, with intervals |
| Hall and Coin 2024, Tables 1-4 | Not extracted | Human read removal for privacy; a different endpoint from pathogen identification. Gap |
| Govender and Eyre 2022 | Not extracted | Printed tables are regression-model predictions; observed values are in figures |
| Lao et al. 2024 (nanopore 16S, 213 sterile fluids) | Not extracted | Per-pipeline culture concordance is printed only in prose; supplementary tables are per sample. High relevance; listed as a gap |
| Peterson et al. 2022 (stool) | Not extracted | Per-tool comparison is figure-only |
| SEPATH 2019 | Not extracted | Figure-only |
| CAMI II pathogen challenge | Excluded | Causal pathogen is an RNA virus; submissions manually curated |
| Watts et al. 2019, BugSeq 2021, Valencia et al. 2024 | Not extracted | Source limit; BugSeq is a developer evaluation already covered independently by Portik; Valencia is gut-microbiome oriented; Watts's clinical arm is Centrifuge-only |
| Respiratory virus classifier study (PMC8953373), ENNGS viral benchmark | Excluded | Mostly RNA viruses |

## Relevance judgements

All 12 are `proxy`, status `needs_review`:

- Portik, six protocols (one per dataset), grouped as strata of `portik2022-mock-species`, headline F1. Proxy because the samples are mock communities without host DNA, not specimens.
- Song Table 1 (`song2025-zymo-standard`), headline proportion. Proxy: one mock library, abundance only.
- Song Table 2 (`song2025-bsi-blood`), headline proportion. This is the closest to the use case's setting (patient blood, blood-culture reference, negative controls). It is held at proxy because the table prints relative abundances rather than detection calls, has five samples of one organism group and no culture-negative patients. A reviewer could reasonably argue for `direct`.
- Hall, four protocols, strata of `hall2024-mtb-reads`, headline Youden's index. Proxy: read-level classification of one pathogen in constructed metagenomes.

## Vocabulary added

Concepts needed for printed columns that had no fitting concept: `eta-squared`, `f-beta-score` (Portik F0.5), `peak-memory` (Hall memory) and `youden-index` in `data/vocab/metric.ttl`; `gigabyte` in `data/vocab/unit.ttl`. They need review with the batch.

## Existing records reused

Configurations link `configuration_of` to `catalog-model-kraken2`, `catalog-model-metaphlan` and `discovery-model-mmseqs2`. The store also holds `discovery-model-kraken-2` and `discovery-model-metaphlan`, which duplicate the first two; they were not linked. No existing records describe Bracken, Centrifuge, mOTUs2, sourmash, MetaMaps, MEGAN-LR, BugSeq, BLAST, Kraken 1, RTG Core or minimap2 as methods, so new family records were added.

## Things a reviewer should judge

1. Song Table 1, Kraken column: 5.17E‐10, 5.17E‐10, 5.17E‐11 and 5.17E‐12 for four species. The repeated mantissa is unusual. Transcribed as printed.
2. Song Discussion and Conclusion say BLAST reached complete concordance without false positives; that is the e-value-optimised run in Figure 1. Table 2 (extracted) shows BLAST signal in both negative controls. Recorded in the protocol version and in claim `dna-pathogen-20261009-claim-song2025-blast-controls`.
3. Song cites Kraken as Wood and Salzberg 2014 and ran it on Galaxy. Whether Kraken 1 or Kraken 2 ran is not stated; the configuration links to a new Kraken method on the strength of the citation.
4. Song Results paragraph 1 says the standard includes yeasts; Table 1 lists eight bacteria only.
5. Portik sourmash rows are `author_reported` because two co-authors wrote the cited sourmash papers; the competing-interests statement does not say this.
6. Portik Results says short-read methods had 40-300 false positives; Table 4 short-read rows range from 0 to 307. Table values recorded.
7. Hall gives kraken v2.1.2 only for the library download used to simulate reads, so kraken configuration versions are left unreported; minimap2 v2.26 comes from the human read removal methods.
8. Whether Song Table 2 should be `direct` rather than `proxy`.

## Coverage

Bounded pass, not systematic. Not covered: independent comparisons of hosted clinical pipelines (CZ ID, SURPI+, DRAGEN Microbial, One Codex) on DNA specimens; LEMMI and the CAMI Benchmarking Portal; clade-exclusion benchmarks for organisms absent from the reference; Portik genus-level and higher-threshold tables; Hall human read removal tables; the 2026 microbial genomic database framework paper (PMC13623680), which was found but not opened.
