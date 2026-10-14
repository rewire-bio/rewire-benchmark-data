# Independent review of the GFM guide evidence and record fixes, 2026-10-14

Review of rewire-benchmark-data#159 (issue #129): the seven evidence batches, the 20 identity claims in `data/omics/gfm-guides-20261014-identity/`, and the linked-count change in `shared/omics/catalogue-query.ts`. The extraction notes are in `docs/reviews/2026-10-14-gfm-guide-record-fixes.md`.

Reviewer: Claude (Opus 5.5) research agent, independent of the extractor. No human review is claimed and nothing was reproduced. Every value was compared with its source by a script written for this review, which does not import the extractors' code (openpyxl for workbooks, a separate text-layer parser for the GPN-MSA table), plus a hand-checked sample of six values per large batch. The scripts were run from a scratch directory and are not kept.

## Sources and hashes

| Source | Pinned SHA-256 | Check on 2026-10-14 |
| --- | --- | --- |
| Kedzierska 2025, article PDF | `8efcc5fc…c47f` | The publisher now returns a 3,038-byte bot-check page. The archived copy in `artifacts/` hashes to the pinned value and was used. |
| Kedzierska 2025, Additional file 1 | `7adee121…3b5e` | Re-downloaded; matches. Archived copy matches. |
| Kendiukhov 2026, article PDF | `4c1699cb…08fe` | Bot-check page, as above. Archived copy matches. Europe PMC XML re-downloaded; matches. |
| Evo 2, Europe PMC full text (reused record) | `d043dbda…8bd` | Re-downloaded; matches. |
| Evo 2, Supplementary Information | `fe2a9910…b925` | Re-downloaded; matches. |
| Evo 2, Supplementary Data 1 | `159f3217…0a51` | Re-downloaded; matches. |
| GPN-MSA, bioRxiv v2 PDF | `10411077…cee4` | The extractor's file hashes to the pinned value. A fresh download (`5f308637…e631`, same 2,247,726 bytes) differs in 51 bytes, all bioRxiv per-download stamps (XMP ModifyDate, MetadataDate, DocumentID, InstanceID, Info ModDate, trailer /ID). The `pdftotext -layout` text is identical. `hash_scope` added to the source record, following the BioML-bench and SpliceAI-2 precedent. |
| GPN README and docs/models/gpn-msa.md at dc5fd287 | `0312fb96…9d0`, `8076d5e5…aedaee` | Re-downloaded; match. |
| Brandes 2023, JATS, Supplementary Table 2, Supplementary Information | `919ca366…4a04`, `093c32e4…72e2`, `30f1c271…7c2a` | Re-downloaded; all match, as do the archived copies. |
| Nguyen 2024 (Evo), PMC JATS | `6bf1e056…5caa` | Re-downloaded; matches. |
| Mahtha 2026, Europe PMC JATS | `aae321d0…98b8` | Re-downloaded; matches. |

## Values checked

| Batch | Results | Automated comparison | Hand sample | Outcome |
| --- | --- | --- | --- | --- |
| Kedzierska 2025 | 602 | 600 workbook cells: value, General display, metric block, dataset row, model column, protocol and evaluation links; all 600 expected cells present once | TableS7 G36, C12, M32; TableS6 G12, K17; TableS3 H8 | All match |
| Kendiukhov 2026 | 20 | None (text values) | All 20 re-read by hand on pages 7 to 10, with n and configuration | All match; 2 disputed (below) |
| Evo 2 | 1,410 | All 705 rows and both metric cells: stored value, metric, model label, stratum to protocol (49 protocols, one each), class counts in the evaluation population | Rows 81, 206, 511, 612, 654, 661 | All numeric values match; `printed_value` corrected on all 1,410; 114 disputed (below) |
| GPN-MSA | 104 | All 17 rows of Supplementary Table 4 by six columns, one system per row | Six cells; the TADBP sentence | All match |
| ESM-1b | 80 | 76 workbook cells: value, metric, row label against configuration, n_var, included flag; every eligible cell present once | B6, B7, B9 (ClinVar); B18, C4, C17 (HGMD) | All match; 4 text results disputed (below) |
| Evo generation | 2 results, 1 claim | None | All re-read | Match |
| Mahtha 2026 claim | 1 claim | None | Abstract, Table 2, Results, Discussion | Match |

Configurations, protocols, datasets and model or method links were read for every batch. Every record of every batch is now `source_checked` except the disputed results.

## Decisions on the flagged judgement calls

### Kedzierska et al. 2025

- Unlabelled columns. Medians of the single-value columns over the five main datasets reproduce 54 of the 56 TableS3 ranks; the bracketed central values reproduce 39. With Pancreas (8k) included, the single values reproduce only 40. So the single values are the whole-dataset scores the paper ranks, and Pancreas (8k) is not one of the five ranked datasets. The reading is confirmed.
- Sheet numbering. A labelling difference, not a value problem.
- Both extraction-time `evidence_concerns` on the workbook source would have blocked comparison of all 600 workbook results. Neither puts a value in doubt, so both are removed and kept as limitations, with a `metadata-correction-*` claim holding the previous concerns.
- Pancreas (8k). The Methods (page 9) say the complete Pancreas dataset and its subset without GSE84133 were both scored "in Additional file 1: Tables S1 and S5", which are the two score sheets, and Pancreas (8k) is their only extra Pancreas row. The dataset description now says so (correction claim keeps the old text).
- The page 4 sentence that HVG gave the best batch integration "for all datasets" is not true per dataset in TableS6 (scGPT random scores higher on both Pancreas rows); HVG is first on the median (TableS3). The values are as printed; no record change.
- scGPT random as an architecture-only configuration of `catalog-model-scgpt`, Harmony on the SCMBench Harmony method record, and the tied ranks: accepted.

### Kendiukhov 2026

- CRISPRa. The article calls the dataset "K562 CRISPRa [25]" and Table 1 lists "Adamson CRISPRa [25]", but reference 25 (Adamson et al. 2016) is a CRISPRi screen. The two CRISPRa results (`...-k562-crispra-77`) are `disputed` with a `source_warnings` entry.
- The source-level `evidence_concerns` blocked all 20 results. The CRISPRa problem is now held on the two results it affects. The two K562 and two RPE1 perturbation sets are different analyses, each already its own dataset subset; that is a limitation, not a conflict. Both concerns are moved to limitations, with a correction claim.
- Origin split (gene-level logistic regression `author_reported`, other baselines and Geneformer `independent_paper`): accepted. The K562 n = 151 assignment of the variance baseline is confirmed by the Fig. 3 caption.

### Evo 2 (Brixi et al. 2026)

- `printed_value`. The extractor stored the full stored decimal (for example `0.690344855120559`). The cells use the number format `0.000`, so the printed value is `0.690`. The store's precedent for fixed-format cells (AlphaGenome, `printed_value_basis` "Workbook number format 0.000") is printed display plus the stored decimal in `numeric_value`. All 1,410 results now follow it; `numeric_value` and `raw_xml_value` are unchanged. Four stored values are exact halves (0.8125, 0.8875) and display rounded up, as Excel does. These records were never released, so they are corrected in place rather than superseded.
- Workbook against legend and Supplementary Tables 6 to 8. Seven strata have workbook counts that differ from the Fig. 3 legend. Supplementary Tables 6 and 7 print Evo 2 7B base values that differ from the workbook for four of them. Those four strata are `disputed` (114 results, every model), each with a `source_warnings` entry that gives both counts and both values:

  | Stratum | Workbook n | Legend n | Supplementary Table value against workbook (Evo 2 7B base) |
  | --- | --- | --- | --- |
  | ClinVar noncoding SNV | 33,747 | 34,761 | ST6 AUPRC 0.956 against 0.958 |
  | ClinVar coding non-SNV | 978 | 1,236 | ST6 AUROC 0.918 against 0.865; AUPRC 0.954 against 0.960 |
  | ClinVar noncoding non-SNV | 3,623 | 3,894 | ST6 0.929 against 0.926; 0.825 against 0.826 |
  | SpliceVarDB intronic | 3,708 | 3,769 | ST7 0.923 against 0.925; 0.968 against 0.969 |

  Not disputed: ClinVar coding SNV (14,313 against 14,319; ST6 0.829 and 0.883 agree), SpliceVarDB exonic (1,179 against 1,181; ST7 agrees) and BRCA1 coding (2,768 against 2,077; ST8 agrees, and 2,768 plus 1,125 noncoding is the n = 3,893 of Fig. 3f, so the legend's 2,077 is the odd number). The "Both" strata are not the union of their parts and the source does not define them, so ST6 "All" and ST7 "All" were not compared with them; their protocols already say so.
- No source-level `evidence_concerns` entry: on Supplementary Data 1 it would block all 1,410 results, including the 45 strata with no conflict. A limitation on that source lists the disputed and the not-disputed strata.
- The batch's GPN-MSA configuration still pointed at the GPN family. It now joins `gfm-guides-20261014-gpnmsa-model-gpn-msa`, with an association claim (`source_checked`) like the ten repoints.

### GPN-MSA

- Values all match. The Supplementary Table 4 caption's figure numbers (off by two in v2) stay a limitation. The Default row and the main-results model stay separate configurations and are not tied to `songlab/gpn-msa-sapiens`. Equal mean and max for the two non-neural rows are kept as printed. "89 non-human species" matches the Methods (the 51-vertebrate ablation subsets "from 89 to 51"). No `variant_of` link to GPN: agreed.

### ESM-1b (Brandes et al. 2023)

- Text against table. The Results print ESM1b 0.905 and EVE 0.885 on 36,537 ClinVar variants, and 0.897 and 0.882 on 30,497 HGMD/gnomAD variants. Supplementary Table 2's EVE head-to-head row gives 0.906 and 0.885 on 36,522, and 0.898 and 0.884 on 30,483. The four text results are `disputed` with `source_warnings`. An `evidence_concerns` entry on the article source would also block the 76 table results, whose evaluations cite the article.
- EVE as `specialist` matches the only other EVE configuration in the store. fitCons is integrated fitCons: the Methods exclude the three cell-line versions. Balanced AUPRC stays `auprc` with its qualifier.

### Evo sequence generation

- The counts (11 of 24 IS200-like, 3 of 24 IS605-like with evidence of both excision and insertion in vitro) match the text. They stay in the catalogue: they are the only printed quantitative generation outcome in the paper and they answer the gap #129 named. The protocol limitations already say the denominator is the author-selected designs. The Cas9 claim (11 tested, one active) matches.

### Mahtha et al. 2026 claim

- Matches the source. Field name `printed_value_conflict` follows the existing claim. No `evidence_concerns` entry: the stored results come from Table 2, which agrees with the Results text. Not recorded: the Abstract gives ESMFold 76% of monomers where the Discussion gives 77%.

## Identity claims

All 20 accepted and set to `source_checked`.

| Claims | Decision | Reason |
| --- | --- | --- |
| `alias_of` Evo 2, ESM-2, ESMFold (`catalog-model-*` to `discovery-model-*`) | Accepted | Each pair has the same name, the same official source artifacts and the same profile; the configurations on the catalog record span several checkpoints, so it is the family. |
| GENEB leaderboard `part_of` `discovery-benchmark-geneb` | Accepted | Both describe darlednik/GENEB at commit 9642d481; the leaderboard is the suite's published aggregate. `alias_of` is not allowed between benchmarks. |
| Ten GPN-MSA `configuration_of` repoints | Accepted | Each configuration is named GPN-MSA in its source; the GPN family is the single-sequence model. |
| Six `metadata-correction-*` version claims | Accepted | The removed versions named one checkpoint on records that hold several. |

Follow-up done, as the extractor described: the `variant_of` links from `catalog-model-evo-2`, `catalog-model-esm-2` and `catalog-model-esmfold` to their canonical records are removed, and the claims they replace (`model-evaluation-identity-1cd8474f1b1d39d47971`, `profile-association-b77dc7ed3e4c0e21c842`, `profile-association-1e3a9f8e48d3e9042bca`) are `superseded`. With the alias claims reviewed, the alias records leave the list and their results reach the canonical records through the verified alias.

## Code

`shared/omics/catalogue-query.ts`: the linked counts walk reverse `configuration_of`, `variant_of`, `family` and `alias_of` links between system records and `part_of` between assessment records, transitively, and collect results in a map keyed by result ID and evaluations in a set of evaluation identities, so a result reached by two paths counts once. `uses_model` and `evaluates_task` are not followed. The verified counts and `results()` are unchanged. The tests cover a result reached twice, an unverified alias, a `uses_model` pipeline that must not count, and an unverified benchmark component. One observation, not changed: `alias_of` is followed only between records of the same kind, which is stricter than the relation rules; the store has no cross-kind alias. The 3.2 bump is justified: list entries in the `blobs` table gain fields that 3.1 readers ignore, and `docs/serving-contract.md` documents them and the fallback for older files.

rewire-database#193: one fix pushed. A child record linked to the page's record by two relations, one reviewed and one not, was listed under "Further results on linked records" through the unreviewed one, although its results were already in the page's table (Evo 2, ESM-2 and ESMFold had exactly this before the alias claims were reviewed). Records with any reviewed identity link are now left out, with a test. The section lists direct children only, while the list counts are transitive, so a grandchild reached through a reviewed version is counted in the list row but not listed on the page; noted in the PR.

## Use cases

No new evaluation lands on a protocol mapped to a use case (`assessed_by`), so no judgement is withheld or changed by the new evidence. `tests/use-case-records.test.ts` passes after the identity follow-up.

## Remaining gaps for #129

- Association claims for the 1,803 `configuration_of` links that have none.
- Metric concepts for AvgBIO and average batch score (Kedzierska), AUROC difference (Kendiukhov) and odds ratio (GPN-MSA gnomAD columns).
- Figure-only comparisons: GPN-MSA ClinVar, COSMIC and DMS against ESM-1b and CADD; Evo 2 Fig. 3 and Extended Data Figs. 4 and 5 beyond Supplementary Data 1; the Evo 2 supervised BRCA1 classifier.
- Brandes 2023 head-to-head columns, indel and stop-gain sheets.
- The disputed Evo 2 strata and ESM-1b text values need the authors' clarification to resolve.
