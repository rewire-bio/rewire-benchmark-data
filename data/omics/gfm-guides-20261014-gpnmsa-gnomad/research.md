# Research notes

Batch for rewire-benchmark-data issue #163: the gnomAD odds-ratio column group of GPN-MSA Supplementary Table 4 (bioRxiv v2, PDF page 23). The first extraction, `gfm-guides-20261014-gpnmsa` (reviewed, in the store), took the ClinVar, COSMIC and OMIM groups and left these 34 cells for want of an odds-ratio concept. This PR adds `odds-ratio` to `data/vocab/metric.ttl` (closeMatch STATO_0000182).

## Decisions

- One new dataset (`gfm-guides-20261014-gpnmsa-data-gnomad-rare-vs-common-ablation-set`), one new protocol (`...-protocol-ablation-gnomad-odds-ratio`, part of the existing benchmark `...-benchmark-gpn-msa-vep`), 17 evaluations (one per table row) and 34 results (mean and max over three seeds).
- Systems are the existing row records: 15 ablation configurations and the two method records (MSA frequency, combined phyloP and phastCons). Each evaluation takes the origin of the reviewed ClinVar evaluation of the same row (author_reported, except independent_paper for the phyloP and phastCons combination).
- The protocol follows the Supplementary Table 4 caption ("gnomAD (odds ratio): same approach as Figure 2d, including all variant types, but subsetting the rare variants to match the number of common variants"), the Figure 2 caption panel (f) (rare = singletons, common = MAF > 5%, threshold at 30 false discoveries, one-sided Fisher's exact test) and Methods 'Additional VEP metrics' ("gnomAD (ablation set)").
- Direction `higher`: the paper reads a larger odds ratio as stronger enrichment of rare variants in the deleterious tail. The concept's default direction is `unknown`, because an odds ratio is not better-higher in general.
- Records are `needs_review`. No review.json yet.

## Record counts

- dataset: 1
- protocol: 1
- evaluation: 17
- result: 34

## Extraction note for the reviewer

Method: deterministic parse of the `pdftotext -layout` text of a 2026-10-14 re-download with `extract/build_gnomad.py` (see retrieval-log.md). Printed values are the strings in the text layer (three decimals). Because the pinned bytes are not archived, the script ties the text layer to the reviewed version by asserting that all 102 ClinVar, COSMIC and OMIM cells it parses equal the values already in the store.

Gaps:

- Variant counts and p-values of the ablation set are not printed.
- The false-discovery threshold for the ablation table is not restated; 30 is the value given for Figure 2f and in Methods 'Main VEP metrics' ("such as 30").
- Figure 2f (the main gnomAD comparison with CADD, phyloP and the language models) and Supplementary Figures 9-13 are figure-only and were not read.

Needs reviewer judgement:

- The caption points to "Figure 2d"; in v2 the gnomAD panel is Figure 2f (the off-by-two already noted for the other columns). Recorded as a protocol limitation.
- Whether the 30-false-discovery threshold applies to the ablation table; the result qualifier states it as the figure's threshold.
- For the two non-neural rows, mean and max are printed and equal; kept as printed.
