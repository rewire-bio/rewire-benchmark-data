# Retrieval log

All requests were made with curl from the collector's scratch area. No personal identifier was sent.

1. 2026-10-14T12:12Z. Europe PMC search for DOI 10.1126/science.ado9336 returned PMID 39541441, PMC12057570, and
   for DOI 10.1101/2024.02.27.582234 the preprint record PPR812521. Europe PMC reports the Science record as not in
   its own full-text store (`inEPMC: N`), and its full-text endpoint for PMC12057570 returned HTTP 500.
2. NCBI efetch (`db=pmc&id=12057570`) returned the author-manuscript JATS full text, HTTP 200, 294 kB. SHA-256 in
   `sources.md`. It carries the Science metadata (volume 386, issue 6723, eado9336, epub 2024-11-15) and the full
   Results and Materials and methods text.
3. The XML has no `<table-wrap>` elements: the paper has no numbered main tables. Its supplementary-material list
   names four files (the PDF manuscript, a supplement PDF, a data zip and a reporting checklist). Both the
   publisher supplement (`science.org/doi/suppl/...`) and the Europe PMC supplementary-files endpoint failed
   (HTTP 403 and "not open access"), so the supplement was not read. No value was taken from any secondary source.
4. The bioRxiv version 1 full PDF was downloaded (HTTP 200) and converted with `pdftotext -layout` to check whether
   the preprint prints generation numbers the journal version does not. Its Tables S1, S2 and S3 are scaling-law
   model settings, pretraining hyperparameters and dataset summary statistics. Perplexity appears only as figures
   (Fig. 1F and 1G, Fig. S2) and in prose about them. Nothing was extracted from the preprint.
5. Searched the journal full text for printed numbers attached to a generation evaluation: matches for AUROC, AUPRC,
   perplexity, coding density, CheckM, tetranucleotide usage and pLDDT. The outcome is in `research.md`. The two
   values extracted are the in vitro assay counts for the generated mobile-element designs, printed in the Results
   as numerals with their denominator.

Re-run the extraction with:

```sh
python3 -I extract/extract_evo_generation.py <pmc_efetch.xml> <batch folder>
```

The script asserts the artifact SHA-256 and the exact sentences the two counts come from before writing anything.
