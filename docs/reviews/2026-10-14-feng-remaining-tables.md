# Review: Feng et al. 2025 remaining tables, 2026-10-14

Independent review of batch `data/omics/feng-dna-fm-20261014/` (rewire-benchmark-data#142, PR #157), which completes the stored Feng et al. 2025 records (prefixes `amp-feng-20261007-`, `feng-dna-fm-20261013-`). Reviewer: an independent Claude (Opus 5.5) review agent; the batch was extracted by a separate Claude agent for #142. No human review is claimed. Source transcription is not reproduction, and nothing was executed.

Feng H. et al. Benchmarking DNA foundation models for genomic and genetic tasks. Nature Communications 16, 10780 (2025). DOI 10.1038/s41467-025-65823-8.

## Outcome

Approved with corrections. No printed or numeric value was wrong. One structural error was fixed: the 177 Supplementary Data 4 results were attached to the stored Table 5/6 evaluations, whose `comparison.aggregation` is the three-group mean. They now sit on 59 per-group evaluations of their own. Three descriptive changes were made: the HyenaDNA-160K note, the 4mC notes and the superseded inventory claim. All changes were made in `extract/extract_feng.py`, which was rerun; `review/signoff.py` then checked the regenerated batch and set all 698 records to `source_checked`.

Counts checked: 305 results (40 Table 2, 88 Table 3, 177 Supplementary Data 4), 25 datasets against Supplementary Data 6 and Supplementary Note 2, 26 baseline-CNN claims against Supplementary Data 1 and 2, 1 inventory claim, 128 configurations, 187 evaluations, 26 protocols. Mismatches in values: 0.

## Sources and hashes

All artifacts were re-downloaded on 2026-10-14 (13:51 UTC) and matched the stored source records. No new source record is added.

| Source record | Artifact | SHA-256 |
| --- | --- | --- |
| `evidence-expansion-dna-foundation-models-2025-5d8ca9bc` | Europe PMC fullTextXML, PMC12663285 | `5d8ca9bcf88cc1b38ad667906a2e4699b1aefa6d31c6f49259784930353f3202` |
| `feng-dna-fm-20261013-source-supplementary-data` | MOESM3_ESM.xlsm (Supplementary Data 1-6) | `4804c801e0e054eca5f776617c18a6a0cb31d6ce3d2a7a52f70e4dda5b3abd7a` |
| `feng-dna-fm-20261013-source-supplementary-information` | MOESM1_ESM.pdf (11 pages) | `373f59b825c9e2bc51a0f122a9e2653f427c492727fbf73768cc9af02d094a15` |

## Method

- `extract/extract_feng.py` was rerun on the pinned artifacts before any change; its output was byte-identical to the submitted `batch.jsonl`, `claims.csv` and `extract/sd4-mean-check.json`. After the corrections it was rerun again and the output signed off.
- `review/signoff.py` does not import the extraction script. It parses Tables 2, 3, 5 and 6 from the XML with ElementTree and reads workbook sheets Data 1, 2, 4 and 6 as zip XML (no macros run). For every result it checks printed and numeric value, metric, qualifier, unit, direction, locator (including bold), source, and the linked configuration (name and checkpoint), protocol and dataset. For Supplementary Data 4 it checks that each displayed value equals the stored double, that the result's evaluation has exactly the links and comparison of the stored Table 5/6 evaluation apart from `aggregation`, and that the stored mean is within rounding of the mean of the three groups. A mutation test (one value, one bold cell, one class count, one chromosome list and one configuration link changed in turn) made it fail each time.
- Manual sample, read against the rendered table text and workbook cells: Table 2 Promoter R.Capsulatus GROVER (0.7154, bold), Table 3 G.Subterraneus 4mC GROVER (0.6061), Human 6 mA NT-v2 (0.7508, bold), Yeast H3K14ac HyenaDNA (0.7067), Supplementary Data 4 cells B11 (0.7312), D41 (0.5816) and C77 (0.7188), and Supplementary Data 6 rows 6mA, G.subterraneus 4mC, Yeast H3K14ac, Human vs Worm and Mouse TFBS 4. All match.
- The Supplementary Information PDF was read with `pdftotext -layout`: Supplementary Note 1 (pages 1-2) for dataset names and origin, Supplementary Note 2 (pages 3-4) for the experimental-evidence flags.
- Methods ("Sequence classification datasets", "Variant effect quantification benchmark", "Model configuration selection") were read against every protocol, configuration, dataset and evaluation statement.

## Values checked

Bold as printed (Tables 2 and 3: higher than at least two other AUCs, p < 0.01, one-sided DeLong). "stored" marks the two Human 5mC cells already held as `lit-001` and `lit-002`, whose stored values also match. Metric `auroc`, unit `unitless`, direction higher throughout.

### Table 2

| Row | DNABERT-2 | NT-v2 | HyenaDNA | Caduceus-Ph | GROVER | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| Human vs worm | 0.9799 | 0.9785 | 0.9502 | **0.9915** | **0.9843** | match (5 of 5) |
| Mouse TFBS 1 | 0.711 | 0.704 | 0.5899 | 0.6841 | 0.6947 | match (5 of 5) |
| Mouse TFBS 2 | **0.9072** | 0.9005 | 0.8996 | **0.9472** | **0.9093** | match (5 of 5) |
| Mouse TFBS 3 | 0.9308 | 0.9269 | 0.8944 | 0.9351 | 0.9327 | match (5 of 5) |
| Mouse TFBS 4 | **0.7622** | 0.6942 | 0.588 | 0.7047 | 0.6815 | match (5 of 5) |
| Mouse TFBS 5 | 0.6783 | **0.7077** | 0.627 | **0.715** | 0.6822 | match (5 of 5) |
| Promoter B.Amyloliquefaciens | 0.8518 | 0.8225 | 0.8643 | 0.8686 | 0.8617 | match (5 of 5) |
| Promoter R.Capsulatus | 0.6855 | 0.6746 | **0.7116** | 0.67 | **0.7154** | match (5 of 5) |

### Table 3

| Row | DNABERT-2 | NT-v2 | HyenaDNA | Caduceus-Ph | GROVER | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| Human 5mC | 0.685 | stored | 0.6843 | stored | **0.7437** | match (3 of 3) |
| Human 6 mA | 0.7351 | **0.7508** | 0.7377 | **0.7731** | **0.7671** | match (5 of 5) |
| Yeast H3 | **0.9137** | 0.8951 | 0.8996 | **0.9285** | 0.9056 | match (5 of 5) |
| Yeast H3K14ac | **0.7597** | **0.7407** | 0.7067 | 0.7297 | 0.7301 | match (5 of 5) |
| Yeast H3K36me3 | **0.7989** | **0.7849** | 0.7395 | **0.7662** | 0.7533 | match (5 of 5) |
| Yeast H3K4me1 | **0.7306** | **0.7115** | 0.6994 | 0.7071 | 0.696 | match (5 of 5) |
| Yeast H3K4me2 | **0.7078** | 0.6847 | 0.6854 | 0.6895 | **0.6939** | match (5 of 5) |
| Yeast H3K4me3 | **0.6813** | 0.6603 | 0.6486 | 0.6595 | 0.668 | match (5 of 5) |
| Yeast H3K79me3 | **0.8565** | 0.8436 | 0.8215 | 0.845 | 0.8427 | match (5 of 5) |
| Yeast H3K9ac | **0.7922** | 0.7687 | 0.7555 | **0.7779** | 0.7692 | match (5 of 5) |
| Yeast H4 | **0.9314** | 0.9104 | 0.8983 | **0.9304** | 0.908 | match (5 of 5) |
| Yeast H4ac | **0.7473** | 0.7263 | 0.6979 | 0.7235 | 0.7175 | match (5 of 5) |
| A.Thaliana 4mC | 0.5994 | **0.6332** | 0.5941 | **0.6146** | 0.6026 | match (5 of 5) |
| C.Elegans 4mC | 0.5985 | **0.6487** | 0.5964 | 0.5964 | **0.6057** | match (5 of 5) |
| D.Melanogaster 4mC | 0.6147 | **0.6519** | 0.6096 | 0.6161 | 0.6167 | match (5 of 5) |
| E.Coli 4mC | 0.5492 | 0.6028 | 0.6105 | **0.6283** | 0.5851 | match (5 of 5) |
| G.Pickeringii 4mC | 0.5958 | 0.6302 | 0.6292 | 0.6348 | 0.6293 | match (5 of 5) |
| G.Subterraneus 4mC | 0.5802 | 0.6145 | 0.609 | 0.6079 | 0.6061 | match (5 of 5) |

### Supplementary Data 4

Values as the workbook displays them (General format; every stored double equals its 4-decimal display). The last column compares the stored Table 5 or 6 mean with the mean of the three groups.

| Block | Workbook row | Group 1 | Group 2 | Group 3 | Stored Table 5/6 mean | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| Pathogenic variants vs common | Caduceus-Ph | 0.704 | 0.6877 | 0.696 | 0.6959 | match |
| Pathogenic variants vs common | Caduceus-Ph, long sequence | 0.6296 | 0.6178 | 0.6254 | 0.6243 | match |
| Pathogenic variants vs common | DNABERT-2 | 0.5471 | 0.5322 | 0.5346 | 0.538 | match |
| Pathogenic variants vs common | Enformer, hidden states | 0.7145 | 0.6575 | 0.6921 | 0.688 | match |
| Pathogenic variants vs common | Enformer, output tracks | 0.6807 | 0.6482 | 0.6697 | 0.6662 | match |
| Pathogenic variants vs common | GROVER | 0.6055 | 0.5942 | 0.6088 | 0.6029 | match; mean of groups 0.6028, rounding |
| Pathogenic variants vs common | HyenaDNA-160K | 0.624 | 0.6158 | 0.596 | 0.612 | match; mean of groups 0.6119, rounding |
| Pathogenic variants vs common | HyenaDNA-450K, long sequence | 0.6357 | 0.622 | 0.6206 | 0.6261 | match |
| Pathogenic variants vs common | NT-v2 | 0.7312 | 0.7318 | 0.7326 | 0.7319 | match |
| Pathogenic variants vs common | Sei, hidden states | 0.686 | 0.6472 | 0.6461 | 0.6598 | match |
| Pathogenic variants vs common | Sei, output tracks | 0.6755 | 0.6495 | 0.6669 | 0.664 | match |
| eQTL | AlphaGenome, output tracks | 0.7925 | 0.8032 | 0.8129 | 0.8029 | match |
| eQTL | Caduceus-Ph | 0.6361 | 0.6705 | 0.641 | 0.6492 | match |
| eQTL | Caduceus-Ph, long sequence | 0.621 | 0.6441 | 0.6145 | 0.6265 | match |
| eQTL | DNABERT-2 | 0.5636 | 0.5745 | 0.5723 | 0.5702 | match; mean of groups 0.5701, rounding |
| eQTL | Enformer, hidden states | 0.7747 | 0.7706 | 0.778 | 0.7744 | match |
| eQTL | Enformer, output tracks | 0.768 | 0.7676 | 0.7742 | 0.7699 | match |
| eQTL | GROVER | 0.595 | 0.6055 | 0.5683 | 0.5896 | match |
| eQTL | HyenaDNA-160K | 0.5892 | 0.6234 | 0.6224 | 0.6117 | match |
| eQTL | HyenaDNA-450K, long sequence | 0.5914 | 0.6176 | 0.5992 | 0.6027 | match |
| eQTL | NT-v2 | 0.6006 | 0.6068 | 0.62 | 0.6091 | match |
| eQTL | Sei, hidden states | 0.7434 | 0.7601 | 0.7647 | 0.7561 | match |
| eQTL | Sei, output tracks | 0.74 | 0.7604 | 0.7486 | 0.7497 | match |
| sQTL | AlphaGenome, output tracks | 0.713 | 0.7266 | 0.7047 | 0.7147 | match; mean of groups 0.7148, rounding |
| sQTL | Caduceus-Ph | 0.5619 | 0.541 | 0.597 | 0.5666 | match |
| sQTL | Caduceus-Ph, long sequence | 0.5755 | 0.5583 | 0.5772 | 0.5703 | match |
| sQTL | DNABERT-2 | 0.5408 | 0.5984 | 0.5993 | 0.5795 | match |
| sQTL | Enformer, hidden states | 0.679 | 0.6621 | 0.6573 | 0.6662 | match; mean of groups 0.6661, rounding |
| sQTL | Enformer, output tracks | 0.6207 | 0.6122 | 0.6192 | 0.6174 | match |
| sQTL | GROVER | 0.4652 | 0.486 | 0.4713 | 0.4742 | match |
| sQTL | HyenaDNA-160K | 0.5484 | 0.5293 | 0.5816 | 0.5531 | match |
| sQTL | HyenaDNA-450K, long sequence | 0.5306 | 0.5314 | 0.5166 | 0.5262 | match |
| sQTL | NT-v2 | 0.5193 | 0.5062 | 0.4887 | 0.5047 | match |
| sQTL | Sei, hidden states | 0.6594 | 0.6168 | 0.6839 | 0.6534 | match |
| sQTL | Sei, output tracks | 0.6355 | 0.5794 | 0.668 | 0.6276 | match |
| paQTL | AlphaGenome, output tracks | 0.6781 | 0.7354 | 0.8495 | 0.7543 | match |
| paQTL | Caduceus-Ph | 0.5059 | 0.505 | 0.5136 | 0.5082 | match |
| paQTL | Caduceus-Ph, long sequence | 0.4637 | 0.4667 | 0.4645 | 0.4649 | match; mean of groups 0.4650, rounding |
| paQTL | DNABERT-2 | 0.5118 | 0.5392 | 0.4689 | 0.5066 | match |
| paQTL | Enformer, hidden states | 0.6486 | 0.6437 | 0.7288 | 0.6737 | match |
| paQTL | Enformer, output tracks | 0.642 | 0.6275 | 0.7284 | 0.666 | match |
| paQTL | GROVER | 0.4107 | 0.4363 | 0.5011 | 0.4494 | match |
| paQTL | HyenaDNA-160K | 0.5176 | 0.425 | 0.467 | 0.4699 | match |
| paQTL | HyenaDNA-450K, long sequence | 0.6474 | 0.5133 | 0.4954 | 0.5521 | match; mean of groups 0.5520, rounding |
| paQTL | NT-v2 | 0.5482 | 0.5821 | 0.4451 | 0.5251 | match |
| paQTL | Sei, hidden states | 0.5928 | 0.6262 | 0.6375 | 0.6189 | match; mean of groups 0.6188, rounding |
| paQTL | Sei, output tracks | 0.621 | 0.6933 | 0.6515 | 0.6553 | match |
| ipaQTL | AlphaGenome, output tracks | 0.8628 | 0.8525 | 0.8779 | 0.8644 | match |
| ipaQTL | Caduceus-Ph | 0.5712 | 0.5931 | 0.5392 | 0.5678 | match |
| ipaQTL | Caduceus-Ph, long sequence | 0.5278 | 0.5563 | 0.4767 | 0.5203 | match |
| ipaQTL | DNABERT-2 | 0.4002 | 0.5619 | 0.446 | 0.4694 | match |
| ipaQTL | Enformer, hidden states | 0.6554 | 0.6763 | 0.7442 | 0.6919 | match; mean of groups 0.6920, rounding |
| ipaQTL | Enformer, output tracks | 0.6458 | 0.6669 | 0.6634 | 0.6587 | match |
| ipaQTL | GROVER | 0.4549 | 0.4812 | 0.4915 | 0.4759 | match |
| ipaQTL | HyenaDNA-160K | 0.4332 | 0.4381 | 0.4727 | 0.448 | match |
| ipaQTL | HyenaDNA-450K, long sequence | 0.4557 | 0.5775 | 0.4948 | 0.5093 | match |
| ipaQTL | NT-v2 | 0.5686 | 0.6331 | 0.604 | 0.6019 | match |
| ipaQTL | Sei, hidden states | 0.6502 | 0.5813 | 0.5898 | 0.6071 | match |
| ipaQTL | Sei, output tracks | 0.5469 | 0.7188 | 0.5523 | 0.606 | match |

### Datasets against Supplementary Data 6

SN2 is Supplementary Note 2. Every dataset also carries Supplementary Note 1 as its origin locator.

| Dataset | Train | Test | Median (min-max) bp | Positive/negative | Notes | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| Human vs worm | 75000 | 25000 | 200 (200-200) | 50000/50000 | - | match |
| Mouse TFBS 1 | 5668 | 2430 | 101 (101-101) | 4049/4049 | SN2: not fully experimental | match |
| Mouse TFBS 2 | 47209 | 20233 | 101 (101-101) | 33721/33721 | SN2: not fully experimental | match |
| Mouse TFBS 3 | 2293 | 983 | 101 (101-101) | 1638/1638 | SN2: not fully experimental | match |
| Mouse TFBS 4 | 1667 | 715 | 101 (101-101) | 1191/1191 | SN2: not fully experimental | match |
| Mouse TFBS 5 | 13180 | 5650 | 101 (101-101) | 9415/9415 | SN2: not fully experimental | match |
| Promoter B.Amyloliquefaciens | 1483 | 636 | 40 (40-40) | 1064/1055 | - | match |
| Promoter R.Capsulatus | 7406 | 3175 | 40 (40-40) | 5374/5207 | - | match |
| A.Thaliana 4mC | 156697 | 67157 | 41 (41-41) | 111927/111927 | Methods: computational annotations; SN2 Yes, Methods human-category note | match |
| C.Elegans 4mC | 84926 | 36398 | 41 (41-41) | 60662/60662 | Methods: computational annotations; SN2 Yes, Methods human-category note | match |
| D.Melanogaster 4mC | 126466 | 54200 | 41 (41-41) | 90333/90333 | Methods: computational annotations; SN2 Yes, Methods human-category note | match |
| E.Coli 4mC | 8681 | 3721 | 41 (41-41) | 2067/10335 | Methods human-category note | match |
| G.Pickeringii 4mC | 24053 | 10309 | 41 (41-41) | 5727/28365 | labels do not sum to splits, Methods human-category note | match |
| G.Subterraneus 4mC | 63567 | 27243 | 41 (41-41) | 15135/75675 | Methods human-category note | match |
| Human 6 mA | 25668 | 11002 | 41 (41-41) | 18335/18335 | - | match |
| Yeast H3 | 10475 | 4490 | 500 (500-500) | 7667/7298 | SN2: Unknown | match |
| Yeast H3K14ac | 23133 | 9915 | 500 (500-500) | 18771/14277 | SN2: Unknown | match |
| Yeast H3K36me3 | 24415 | 10465 | 500 (500-500) | 18892/15988 | SN2: Unknown | match |
| Yeast H3K4me1 | 22173 | 9504 | 500 (310-500) | 17266/14411 | SN2: Unknown | match |
| Yeast H3K4me2 | 21478 | 9205 | 500 (500-500) | 18143/12450 | labels do not sum to splits, SN2: Unknown | match |
| Yeast H3K4me3 | 25759 | 11040 | 500 (290-500) | 19604/17195 | SN2: Unknown | match |
| Yeast H3K79me3 | 20185 | 8652 | 500 (500-500) | 15337/13500 | SN2: Unknown | match |
| Yeast H3K9ac | 19447 | 8335 | 500 (500-500) | 15415/12367 | SN2: Unknown | match |
| Yeast H4 | 10220 | 4381 | 500 (500-500) | 6480/8121 | SN2: Unknown | match |
| Yeast H4ac | 23866 | 10229 | 500 (500-500) | 18410/15685 | SN2: Unknown | match |

### Baseline CNN claims

All 26 claims (8 Table 2 rows, 18 Table 3 rows) match the model lists in Supplementary Data 1 and 2 row for row. The CNN's own AUC is not printed anywhere.

## Corrections

1. Per-group results moved to their own evaluations. The record contract (`docs/record-contract.md`) puts `aggregation` in the evaluation's `comparison` object, and comparisons require the same comparison fields. The stored Table 5/6 evaluations say "Mean of AUC/Cohen's d across the three outer chromosome test folds", which is false for a single-group value. The store already keeps a different aggregation on a separate evaluation of the same configuration and protocol (for example the SCMBench per-dataset and overall evaluations). The batch now adds 59 evaluations `feng-dna-fm-20261014-eval-sd4-<block>-<configuration>` with the stored evaluation's links, origin, missing-metadata and comparison, except `aggregation`: "Per outer chromosome test group: one AUC for each of the three held-out groups, not averaged (Supplementary Data 4)". The paQTL and ipaQTL evaluations quote the Supplementary Data 4 legend on notable differences between test sets. As a result no reviewed evaluation gains a result.
2. HyenaDNA-160K note. The extractor flagged a checkpoint conflict. There is none. Methods name Hyena-160K as the default checkpoint and Hyena-450K for gene expression and variant effect quantification "to leverage its ability to process longer sequences". Tables 5 and 6 print the short-window row as "HyenaDNA" and the long-input row as "HyenaDNA-450K, long sequence"; Supplementary Data 4 lists both, the short one as "HyenaDNA-160K". The link to the short-window HyenaDNA configuration is right, and the result notes now say so. The stored configuration's checkpoint stays unreported; Supplementary Data 4 names it, and a later change could record it.
3. 4mC datasets. Methods give 4mC detection as an example of a human epigenetic task, but all six 4mC datasets are non-human. Each dataset keeps its printed species and now carries that note. The three eukaryotic datasets also note that Supplementary Note 2 marks them "Yes" for experimental evidence, while Methods say their annotations often rely on computational predictions.
4. Superseded inventory claim. `feng-dna-fm-20261013-claim-not-extracted` was set to `superseded` with `records -- change`; the new claim links to it with `supersedes`.
5. A code comment in `extract_feng.py` gave Supplementary Note 2 as pages 1-2; it is pages 3-4. The records already said pages 3-4.

## Use-case effect

The 59 per-group evaluations sit on the five protocols mapped as proxy to `use-case-rare-disease-candidate-ranking` and `use-case-regulatory-variant-gene-follow-up`. Without action they would appear on both use-case pages beside the means. The five judgements were re-reviewed: see [use-cases/feng-variant-effect-per-group-2026-10-14.md](use-cases/feng-variant-effect-per-group-2026-10-14.md). The new Table 2 and Table 3 protocols are not mapped, which is right: none of the 26 use cases decides bacterial promoters, mouse TFBS, yeast marks or 4mC, and the human 5mC and 6mA site tasks do not measure tumour DNA in plasma.

## Source discrepancies

Kept as printed:

- Methods list 4mC as a human epigenetic task; all 4mC datasets are non-human (correction 3).
- Supplementary Note 2 marks the eukaryotic 4mC datasets "Yes" for experimental evidence; Methods say their annotations often rely on computational predictions.
- Table 2 prints "Human vs worm"; Supplementary Note 1 and Supplementary Data 1, 2 and 6 print "Human vs Worm".
- Supplementary Data 6 label counts for G.Pickeringii 4mC and Yeast H3K4me2 do not sum to training plus test size (noted on the datasets).
- Nine Supplementary Data 4 rows average to a value one unit off the printed Table 5/6 mean in the fourth decimal, consistent with averaging unrounded values (`extract/sd4-mean-check.json`).

## Remaining gaps

- Per-group Cohen's d is not published.
- Supplementary Data 3 and 5, Supplementary Tables 1-8, Supplementary Fig. 1 and Figures 2-4 are not extracted (`feng-dna-fm-20261014-claim-not-extracted`).
- The Human 5mC task and dataset records reused here are discovery-era `needs_review` records; the new protocol links to them but does not review them.
- No result was reproduced, and no human scientific review has been done.
