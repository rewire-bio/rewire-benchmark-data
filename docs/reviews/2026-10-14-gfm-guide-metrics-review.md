# Independent review of the GFM guide metric concepts and evidence batches, 2026-10-14

Review of rewire-benchmark-data#170 (part of #163): the four metric concepts added to `data/vocab/metric.ttl` and the five evidence batches that use them. The extraction notes are in each batch's `research.md`.

Reviewer: Claude (Opus 5.5) research agent, independent of the extractor. No human review is claimed and nothing was reproduced. Values were compared with their sources by scripts written for this review, which do not import the extractors' code (openpyxl for the two workbooks, a separate text-layer parser for the GPN-MSA table), plus a hand-checked sample. The scripts ran from a scratch directory and are not kept.

## Metric concepts

| Concept | Check | Outcome |
| --- | --- | --- |
| `avg-bio` | Kedzierska et al. 2025 Methods page 9: "AvgBIO is the arithmetic mean of three individual metrics [7]: ASW, Normalized Mutual Information (NMI), and Adjusted Rand Index (ARI)", NMI and ARI on Louvain clusters at the best-NMI resolution out of 20, ASW normalised to [0, 1]. Reference 7 is scGPT (Cui et al.). | Definition and scope note match. Direction `higher` is right. |
| `average-batch-score` | Methods page 10: "the Average Batch Score, which is computed as the arithmetic mean between the PCR and batch integration scores"; batch integration is 1 minus the absolute batch silhouette per cell type, averaged. | Matches; the scope note correctly limits the concept to this definition. Direction `higher`. |
| `auroc-difference` | Kendiukhov 2026 Methods 'Statistical framework' (page 16): "AUROC differences (ΔAUROC) for incremental-value tests". | Matches. Direction `higher` follows from the stated order of subtraction (evaluated minus reference). |
| `odds-ratio` | GPN-MSA v2 Figure 2 caption (f), Methods 'Main VEP metrics' and 'Additional VEP metrics'. STATO_0000182 is odds ratio. | Matches. Default direction `unknown` is right for a general odds ratio; the GPN-MSA results set `higher` explicitly. |

No duplicates: the scheme's other aggregate single-cell scores (`scmbench-integration-accuracy`, the scIB components) and ratio concepts (`auprc-ratio`, `likelihood-ratio`, `early-precision-ratio`) are different quantities, and no result in the store used a qualifier for these four before this PR. Labels and definitions follow the scheme's style.

## Sources and hashes

| Source | Pinned SHA-256 | Check on 2026-10-14 |
| --- | --- | --- |
| Kedzierska 2025, Additional file 1 | `7adee121…3b5e` | Re-downloaded; matches. Archived copy matches. |
| Kedzierska 2025, article PDF | `8efcc5fc…c47f` | Publisher returned a 3,038-byte bot-check page. Archived copy matches; used for the metric definitions. |
| Kendiukhov 2026, article PDF | `4c1699cb…08fe` | Bot-check page, as above. Archived copy matches and was used. |
| GPN-MSA, bioRxiv v2 PDF | `10411077…cee4` | Fresh download `ea7f7c3a…3389`, 2,247,726 bytes (the pinned length). The pinned bytes are not archived (CC BY-NC-ND) and bioRxiv stamps each download, as the source's existing `hash_scope` records. A second download was refused (rate limit). The text layer is tied to the reviewed version because its ClinVar column equals the 34 reviewed ClinVar results row for row. Results carry the fresh copy's hash as review `artifact_sha256` and their review method omits `source-hash-verification`, following the CpGPT precedent. |
| Brandes 2023, Supplementary Table 2 | `093c32e4…72e2` | Re-downloaded; matches. |
| Brandes 2023, Europe PMC JATS | `919ca366…4a04` | Re-downloaded; matches. |
| Brandes 2023, Supplementary Information | `30f1c271…7c2a` | Re-downloaded; matches. |
| Mahtha 2026, Europe PMC JATS | `aae321d0…98b8` | Re-downloaded; matches. |

No source record needed a new `hash_scope`: the only per-download stamping source (GPN-MSA) already has one, and the two bot-check pages are an access failure, not a change of the artifact.

## Values checked

| Batch | Results | Automated comparison | Hand sample | Outcome |
| --- | --- | --- | --- | --- |
| Kedzierska 2025 AvgBIO and average batch | 176 | All 176: cell value, General display, metric block, dataset row, model column, sheet against protocol (full or UMAP), evaluation system and data; all 176 single-value cells of both blocks in TableS6 and TableS7 present exactly once | TableS6 Q40, Q25, E21, I37; TableS7 C21, K41 | All match |
| Kendiukhov 2026 ΔAUROC | 8 | None (text values) | All 8 re-read with sign, interval, page, perturbation set and reference system (table below) | All match; 1 disputed |
| GPN-MSA gnomAD odds ratios | 34 | All 34: value, mean or max, metric, protocol; each row's system equals that of the reviewed ClinVar result of the same row | Default mean and max, 51 vertebrates max, Window size = 4 mean, MSA frequency mean and max | All match |
| Brandes 2023 Supplementary Table 2 | 386 | All 386: value (shortest round-trip decimal), header, row label, metric; head-to-head system (ESM1b or the comparator whose reported name is the row label), origin, included flag and note against the configuration, head2head_n_variants against the subset's scored_count; every numeric cell present exactly once; `NaN` cells have no result | ClinVar E21, F21, G21, H21 (BayesDel no AF), H46 (VARITY_R); HGMD E37 to H37 (MetaRNN); indels D5 (CADD deletions); stop-gains C2 (ESM1b NMD), D5 (50 bp rule) | All match |
| Mahtha 2026 monomer claim | 1 claim | None | Abstract, Discussion, Results, Table 1 | Matches |

Kendiukhov 2026, every value:

| Value | Interval | Comparison | Data | Page | Outcome |
| --- | --- | --- | --- | --- | --- |
| −0.0004 | [−0.001, 0.000] | gene + attention minus gene only | K562, 280 (559,720 = 280 x 1,999 observations) | 8 | Match |
| −0.002 | [−0.005, 0.000] | gene + correlation minus gene only | K562, 280 | 8 | Match |
| −0.000 | 95% CI [−0.000, +0.000] | gene + attention minus gene only | K562 propensity-matched pairs | 9 | Match |
| +0.0001 | 95% CI [+0.0001, +0.0001] | gene + attention minus gene only | RPE1, 1,167 | 10 | Match |
| −0.0006 | none | gene + correlation minus gene only | RPE1, 1,167 | 10 | Match |
| +0.060 | [+0.040, +0.080] | attention minus correlation | K562, 280 | 10 | Match as printed; disputed |
| +0.090 | [+0.079, +0.101] | attention minus correlation | RPE1, 1,251 | 10 | Match |
| +0.168 | none | attention minus correlation | RPE1, top 2,000 HVGs, 418 | 10 | Match |

All other records of the five batches (configurations, methods, protocols, datasets, subsets, evaluations, benchmark) were read against their locators. Every record is now `source_checked` except the one disputed result.

## Decisions on the flagged calls

### Brandes: the 27 comparators the paper excluded

Kept in the store. The paper itself publishes them: "Evaluation results for all 46 methods, including those excluded for data leakage concerns, are reported in Supplementary Table 2" (Results). The record design already prevents an unfair comparison: each comparator has its own head-to-head subset, so its value can only be compared with the ESM1b value on the same variants, never with another comparator or with the 19-method results, and the exclusion reason from column K is in each configuration's `training_overlap`. No use case is assessed by these protocols. The protocol limitation said the values "are inflated" by the overlap, which the paper does not show; it now says they "may be inflated" and quotes the paper's "data leakage concerns".

### Brandes: stop-gain counts and statistic

A limitation, not a dispute. The workbook values themselves settle both questions. Each stop-gain ROC-AUC, multiplied by twice the product of its class counts, is an integer (to 1e-8) for the Methods counts (3,672 x 147; 32,441 x 198; 36,113 x 345) and is not for the legend and Supplementary Methods counts (32,362 and 36,034 pathogenic): for example ESM1b with NMD gives 7,268,921.000000 with 32,441 and 7,251,219.796 with 32,362. A mean of 20 bootstrap ROC-AUCs on 140 + 140 variants does not give these fractions either. So the workbook values are whole-set ROC-AUCs on the Methods counts, not the bootstrap means plotted in the figure. The values are not in doubt, so they stay `source_checked`. Because the source does not state this, `comparison.aggregation` stays unreported and the NMD subset's `scored_count` stays `conflicting`; the finding is added to the protocol limitations, the dataset's `denominator_warning`, the subset's missing-reason note and the ten evaluations' aggregation note. The in-frame indel values are likewise exact fractions of 1,791 x 1,679, consistent with whole-set ROC-AUCs.

### Kendiukhov: K562 +0.060 on the "layer not stated" configuration

The assignment is right (the sentence names no layer) but the value is now `disputed`, with a `source_warnings` entry. On the same 280 K562 perturbations the article prints attention 0.704 against correlation 0.703 at L13 (page 7, "statistically indistinguishable", p = 0.73) and 0.743 at L15 (page 7), 0.040 above correlation. Neither gives +0.060 [+0.040, +0.080], and the same paragraph sums up K562 CRISPRi as "equal". The RPE1 value in the same sentence, +0.090, equals the printed L15 difference (0.748 − 0.658), so the two bootstrap values are not obviously on one basis. The RPE1 value stays `source_checked` on the layer-not-stated configuration; the L15 match is noted in its review but not used to assign a layer.

Not changed: the existing RPE1 1,251 evaluations say the LFC threshold is not restated. The page 10 sentence ("LFC > 0.5: +0.090") together with the L15 arithmetic suggests LFC > 0.5, but that is an inference, and those evaluations are outside this PR.

### GPN-MSA

The 30-false-discovery threshold for the ablation table: the table caption says "same approach as Figure 2d" (Figure 2f in v2), and the Figure 2f caption gives 30. Stating it in the qualifier is acceptable; the protocol limitation records that the table does not restate it. Equal mean and max on the two non-neural rows are as printed.

### Mahtha 2026

The claim matches. Its reading of "accuracy" as accurate plus domain movement is supported by the Results, which say of AlphaFold2 that the 386 domain-movement predictions "were also considered as correct predictions. Taken together, AlphaFold2 achieved 87.4% accuracy". No `evidence_concerns` entry: the stored results are Table 1 counts, which agree with the Results text.

## Corrections

All corrections are to records added by this PR and never released, so they are made in place (as for the Evo 2 `printed_value` fix in the previous review) and recorded with `records -- change`; no `metadata-correction-*` claims. Previous values are in git history and listed here.

| Records | Field | Previous | Now |
| --- | --- | --- | --- |
| Brandes multiresidue benchmark; in-frame indel dataset and its three subsets; stop-gain dataset and its two subsets; indel and stop-gain protocols (11 records) | locators, names, subset description, missing-reason notes, `denominator_warning` | "Fig. 4", "Fig. 4a,b", "Fig. 4b", "Fig. 4d" | "Fig. 6", "Fig. 6a,b", "Fig. 6b", "Fig. 6d". In the pinned version of record Fig. 4 is the isoform figure; the indel and stop-gain figure is Fig. 6, as the JATS text itself cites it. |
| ClinVar and HGMD head-to-head protocols | `name` | "Fig. 2f" | "Fig. 2g,h": the Fig. 2 caption gives the head-to-head comparison as panels g and h; e and f are the 19-method comparison. |
| ClinVar and HGMD head-to-head protocols | limitation | "their head-to-head values are inflated by that overlap" | "('data leakage concerns' in the Results); their head-to-head values may be inflated by that overlap and are not the paper's unbiased comparison" |
| Stop-gain protocol, dataset, NMD subset, ten stop-gain evaluations | limitations and notes | (no arithmetic finding) | the whole-set ROC-AUC finding above |
| `...kendiukhov2026-result-pf-k562-crispri-...-attention-layer-unstated-auroc-difference` | status, `source_warnings` | `needs_review` | `disputed`, with the warning above |

The extraction scripts in `extract/` still produce the pre-review bytes; `batch.jsonl` holds the reviewed records.

## Use cases

None of the nine protocols these batches use is in any use case's `assessed_by` links, so no judgement gains or loses evaluations. `tests/use-case-records.test.ts` passes.

## Remaining gaps

- What the K562 +0.060 attention advantage measures (layer and summary statistic), and the CRISPRa dataset identity from the previous review: questions for the author.
- Which stop-gain counts are correct; the workbook fits the Methods counts.
- Kendiukhov synthetic positive control, LFC > 0.25 advantage and ΔAUPRC, as listed in the batch's research notes.
- Brandes `Table_of_results_DMS`, gene-average ROC-AUC and figure-only panels.
- GPN-MSA Figure 2f and Supplementary Figures 9 to 13 (figure-only).
