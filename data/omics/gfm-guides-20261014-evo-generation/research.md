# Evo sequence generation: what the primary source prints (Nguyen et al., Science 2024)

Issue rewire-bio/rewire-benchmark-data#129, genomics lane, 2026-10-14. Question: does the Evo paper report a
quantitative sequence-generation evaluation as a printed number, with an exact locator?

Answer: almost none. The paper's generation assessments are figures. The one exception is the in vitro assay
outcome for the generated mobile-element designs, printed in the Results as numerals with their denominator. That
is extracted; everything else is recorded as a gap.

## Sources checked

The Science version (DOI 10.1126/science.ado9336) was retrieved as the PubMed Central author manuscript full text
and pinned by hash; see `sources.md` and `retrieval-log.md`. The Science supplement could not be retrieved
(HTTP 403 at the publisher; PMC12057570 is not open access, so Europe PMC serves no supplementary files), so the
supplementary tables and figures were not checked. The bioRxiv version 1 PDF was downloaded to see whether the
preprint prints anything the journal version does not; its Tables S1 to S3 are architecture, pretraining
hyperparameter and dataset-statistics tables. No value was taken from the preprint or from any summary or review.

## Existing Evo records

The Evo (version 1) family record in the store is `lit-genomics-20261011-geneb-model-evo` ("Evo", `entity_level`
`family`, from the GENEB leaderboard). It is reused as the family of the new configuration. Existing Evo 1
configurations (`lit-genomics-20261011-geneb-config-evo-1-131k-base`,
`lit-microbial-20261011-virobench-config-evo1-*`, `lit-rna-20261011-rnalm-zeroshot-config-evo1-*`,
`mrnabench-method-evo1`) are other papers' or leaderboards' checkpoints under prediction protocols, not the
fine-tuned generator in this paper, so a new configuration was created.

## What was extracted

One source, one configuration (Evo fine-tuned on the mobile-element loci), one dataset (the 48 selected designs),
one protocol (count of tested designs scored active in vitro), two evaluations and two results: 11 of 24 for the
IS200-like designs and 3 of 24 for the IS605-like designs, both with `metric` `count`, `unit` `count`, direction
`higher`, `coverage` {scored 24, eligible 24} and `denominator` 24. Origin `author_reported`. All records
`needs_review`. One claim records that 11 generated Cas9-family designs were selected and tested and that the
source says one of them was active; the active count is printed as a word, not a numeral, so it is a claim rather
than a result.

## Extraction note for the reviewer

Method: `extract/extract_evo_generation.py`, run on the pinned JATS XML. The script asserts the artifact SHA-256,
then asserts verbatim the sentence that carries both counts and the sentence stating that 24 designs per family
were tested, before writing records. Values were transcribed by hand from the asserted sentences; there is no
table parser, because the paper has no tables. Nothing was read from a figure.

Tables extracted: none; the paper's JATS full text contains no `<table-wrap>` elements. The two results come from
the Results text of the section on generated mobile elements.

Checked and not extracted, with reasons:

1. Generated-sequence quality metrics at genome scale: coding density of generated sequences against natural and
   random controls, protein structure prediction confidence, secondary-structure proportions, structural matches,
   tetranucleotide usage deviations, stop-codon frequencies, GC content, dinucleotide and codon-usage patterns.
   All of these are figures (Fig. 6B to H and fig. S28) with no printed numbers. The Materials and methods describe
   the pipelines and the controls (100 genome crops, 1,000 random sequences) but print no metric values.
   Figure source data are not published for this paper, so no value could be computed from the source's own rows.
2. Counts of generated features quoted in the Results (tRNA sequences across the sampled megabases, rRNA count,
   total sampled length) are descriptive tallies of a single sampling run with no protocol, denominator or
   comparator, so they are not recorded as results. A reviewer who wants them in the store should add them as
   claims on the configuration.
3. Perplexity: printed only in the scaling-law figures (Fig. 1F, 1G) and the long-context figure (Fig. S2), with no
   numeric values in text or tables. Recorded as a gap. This is the clearest missing item for the guides: there is
   no printed per-architecture or per-context perplexity value in this source.
4. Sequence-identity percentages for individual validated designs (protein identity to the nearest training-set
   match, guide-RNA identity to the canonical sequence) and one structure-prediction confidence value for one
   design are printed, but they describe single designs, not an evaluation over a dataset. Not extracted.
5. The approximate success-rate phrasing in the same paragraph ("nearing 50%") is not a printed value and was not
   recorded; the exact counts it refers to are the two results extracted.
6. Gene essentiality AUROC values printed in the Results (0.90 for one phage dataset, 0.84 for one bacterial
   dataset, plus the count of 49 of 58 genomes with a significant association) are prediction, not generation, and
   fall outside this batch's scope. They are printed numbers with locators and could support a separate batch; no
   existing record covers them (`lambda-prophage-2026` is a different paper's source).

Gaps and conflicts a reviewer should weigh:

1. The Science supplement was not retrievable. If a reviewer has institutional access, the supplementary figures
   (figs. S18 to S28) and any supplementary tables should be checked for printed generation numbers before the
   "figures only" conclusion is treated as final.
2. The extracted counts are a laboratory outcome for a filtered, author-selected subset of generations, not a
   benchmark score: the denominator is the 24 designs chosen per family, and the number of generations they were
   selected from is not printed. The protocol and the source record both say so. A reviewer may judge that this
   belongs in the catalogue only with that caveat attached, or not at all.
3. Scoring is binary active or inactive from a single assay format per family, with no replicates, uncertainty or
   activity level printed, so the results carry `missing_metadata.uncertainty` with reason `inapplicable`.
4. The pinned artifact is the author manuscript, not the publisher's typeset article; wording and figure numbering
   follow the accepted manuscript. The source record's `limitations` says so.
5. The licence is not open, so no archived bytes are kept. A reviewer must re-fetch the efetch URL and check the
   hash in `sources.md`.
