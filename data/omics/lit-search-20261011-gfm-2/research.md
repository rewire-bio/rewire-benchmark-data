# Search notes: genomic foundation models, 2026-10-11

## Scope boundary with the parallel pass

`lit-genomics` covers the benchmark suites themselves and a completeness check of the suites already stored.
This pass covers independent evaluations comparing several genomic foundation models, and reviews as leads.
The boundary was agreed by message before extraction: anything whose main contribution is a suite went to
that pass, including DNALONGBENCH, GUANinE v1.1, GENEB, Genomic Touchstone and TraitGym.
`lit-rna-other` was told that You et al. 2026 is extracted here with only its splicing tables, and that its
non-coding RNA, m6A and translation-efficiency tables remain available.

## How the window was covered

Europe PMC first, by phrase (`genomic language model`, `DNA language model`, `genomic foundation model`,
`DNA foundation model`, `nucleotide transformer`) crossed with benchmark, evaluation and comparison terms, then
by model name, then by task family (variant effect, long range, probing, MPRA and enhancers, plants, microbes
and viruses, sequence to function). arXiv next, since several of this year's evaluations are preprints there
and never reach Europe PMC. Then eight reviews read in full for their benchmark tables and reference lists.

Two patterns shaped the result. First, most in-window independent evaluations publish per-model numbers only
in figures; the three extracted sources are the ones that print complete tables or supplementary tables.
Second, the reviews cite the same small set of suites and two or three independent evaluations, almost all of
which the store already holds, so the reviews produced no new source but did confirm coverage.

## Screening rule applied

A source had to report numbers for named models or methods on a defined benchmark or task, printed as text.
Developer papers were excluded as independent evidence (their own models' results are author-reported and
mostly already in the store). Reviews were excluded unless they printed new results; none did.
Nothing was read off a figure, and no value was computed from supplementary data, because the `derivation`
attribute had not landed on `origin/main` when this pass ran.
