# Review: genomic foundation model suite batches, 2026-10-11

Independent review of the eight batches from the `lit-genomics` literature pass on genomic foundation model
benchmark suites. Reviewers: Claude review agents `reviewer-gen-1` (geneb, evo2mito), `reviewer-gen-2`
(ntbench, genbench) and `reviewer-gen-3` (dnalongbench, traitgym, guanine, gfmbench). None of them extracted
these batches. No human review is claimed. Source transcription is not reproduction.

Each batch folder holds the reviewer's report and the corrections applied (`review.md`) and the receipt
(`review.json`, binding the SHA-256 of every file in the folder). The corrections were applied by the
extractor in the extraction scripts, as the reviewers specified, before the batches were added to the store.

## Outcome

Every batch passed with corrections. No printed or numeric value was wrong. Each reviewer re-retrieved or
unpacked the pinned artifact, matched its SHA-256, and compared every result with an independent parse;
`reviewer-gen-2` also checked seeded samples against the rendered PDF pages.

| Batch | Source | Artifact SHA-256 | Reviewer | Values | Records after correction |
| --- | --- | --- | --- | --- | --- |
| `lit-genomics-20261011-guanine` | GUANinE v1.1 reveals complementarity of supervised and genomic language models | `f6cc4294…33ef79` | reviewer-gen-3 | 225 results | 539 records |
| `lit-genomics-20261011-gfmbench` | GFMBench-API: A Standardized Interface for Benchmarking Genomic Foundation Models | `df9934c8…acdf72` | reviewer-gen-3 | 552 results | 770 records |
| `lit-genomics-20261011-ntbench` | Nucleotide Transformer: Supplementary Information (Supplementary Tables 1-12) | `ef0f357a…fc436e` | reviewer-gen-2 | 419 results | 921 records |
| `lit-genomics-20261011-genbench` | GenBench: A Benchmarking Suite for Systematic Evaluation of Genomic Foundation Models | `24105d26…154f12` | reviewer-gen-2 | 367 results | 836 records |
| `lit-genomics-20261011-dnalongbench` | DNALONGBENCH: a benchmark suite for long-range DNA prediction tasks | `0d7db21f…3fe41b` | reviewer-gen-3 | 135 results | 188 records |
| `lit-genomics-20261011-traitgym` | TraitGym official metrics: AUPRC by chromosome, weighted average (Hugging Face dataset songlab/TraitGym) | `44dfedc0…d0372e` | reviewer-gen-3 | 156 results | 411 records |
| `lit-genomics-20261011-geneb` | GENEB leaderboard (leaderboard.json, 13 task-type aggregates) | `7c8a9d98…01f738` | reviewer-gen-1 | 1845 results | 2034 records |
| `lit-genomics-20261011-evo2mito` | Benchmarking DNA Foundation Models: Biological Blind Spots in Evo2 Variant-Effect Prediction | `8fe2977a…dacf7d` | reviewer-gen-1 | 8 results | 13 records |

Total: 3707 results, 5712 records.

## Main corrections

- **evo2mito.** The seven comparator rows of Table 2 reproduce APOGEE 2 (Bianco et al. 2023) cross-validation
  results on a missense-only set, not this paper's test split. Their 56 results, 7 evaluations, 7
  configurations and 6 new method records were removed; only the 8 Evo2 results remain. The source's evidence
  concern states the finding and the Table 2 versus Figure 2B sensitivity and specificity discrepancy.
- **ntbench.** The 72 Supplementary Table 7 copies of the Raw Probe and BPNet rows duplicated Table 6 and were
  removed. BPNet evaluations are `independent_paper` and "trained from scratch". The all-tasks dataset links
  `same_data_as` to `gfm2-20261011-datta2026-data-nt-benchmark` (informational; values are not merged).
- **genbench.** The NT configuration is NT-v2 500M (Table 9 architecture). Two Table 10 rows that repeat Table 4
  were removed (14 results). "Top-1" is recorded as undefined. Datasets carry their Table 2 sizes.
- **dnalongbench.** The journal-version ETGP AUROC results for HyenaDNA and Caduceus-Ph supersede the preprint
  records `lit-007` and `lit-008` (and their evaluations), which are set to `superseded`.
- **geneb.** The macro MCC is the unweighted mean of the 13 category MCCs, not of 100 tasks. Protocols name the
  logistic-regression probe. METAGENE-1 uses the existing `catalog-model-metagene-1` family.
- **gfmbench.** The 20 "NA" cells were dropped. A result-level anomaly marks the six Caduceus-Ps Songlab ClinVar
  embedding results. Judgement claims were corrected (Mendelian AUROC ranges, BRCA1 endpoint wording, Evo2 as
  the only autoregressive model).
- **guanine.** Sei-Aggr. and the authors' own baselines are `author_reported`; ID slugs fixed; PhyloGPN
  locators carry the Eval value; a limitation on ρ against Boolean labels.
- **traitgym.** Judgement claims carry the truth-set caveat and, for linear probing, why the scores are not
  comparable with zero-shot scores.

## Use-case judgements

Thirteen relevance judgements (`proxy`) were approved with corrections: six GFMBench TraitGym protocols and
four TraitGym protocols for `use-case-regulatory-variant-gene-follow-up`, and three GFMBench BRCA1 protocols for
`use-case-brca1-brca2-germline-interpretation`. Their `reviewed_evaluations` list every evaluation on the
protocol, each of which had its values checked in the batch review. The `assessed_by` links were added to the
two use cases and the claims pinned with `npm run use-cases:repin`.

## Remaining gaps

- No figures were read. GENEB accuracy, F1 and per-task scores are not extracted.
- Suites still missing from the store: Genomics Long-Range Benchmark (PDF not retrievable), GV-Rep,
  OmniGenBench, Genomic Touchstone and BGCs-Bench.
- TraitGym's standard error is described as bootstrap from the paper's text; the reviewer did not read
  Appendix B.4.
