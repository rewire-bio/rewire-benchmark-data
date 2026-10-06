# Retrieval log — BRCA1/BRCA2 additive intake, 5 October 2026

This authoring pass did not run a new literature search; it ingests numeric evidence from the
five sources already identified and dossiered in
`docs/omics/evidence-research/brca1-brca2-germline-interpretation-2026-10-05.md`, after directly
verifying each figure against cached or freshly fetched source bytes.

## Issue #343 — Interpret BRCA1/BRCA2 germline variants

- Benet-Pages et al. 2025 (PMC11869971): cached full text at `/tmp/benet.html`, verified via
  targeted text search for the t2/t3 reclassification sentences. No live fetch performed this
  pass; the cache was already present.
- So et al. 2024 (PMC11675547): cached full text at `/tmp/so.html`, verified via targeted text
  search for the Section 3.3 concordance sentence. No live fetch performed this pass.
- HECTOR preprint (medRxiv 2026.07.06.26357220v1): cached full text at `/tmp/hector.html`,
  verified via targeted text search for the "Evidence Repository" Results subsection. No live
  fetch performed this pass.
- Hu et al. 2026 (PMC13223280): live fetch performed this pass
  (`https://pmc.ncbi.nlm.nih.gov/articles/PMC13223280/`) to directly check the "Combined analysis"
  / "Incorporation of the 'Integrated VarCall model'" Results subsection before any numeric entry,
  per the task requirement that this source be checked directly. The fetched text was cached
  byte-identically to `/tmp/hu-brca2.html` and verbatim-matched against the dossier's quoted
  sentence.
- Karalidou et al. 2022 ("MARGINAL", PMC9687470): cached full text at `/tmp/marginal-pmc.html`,
  verified for author, title, DOI and venue only. Headline performance tables (Results 3.1 Tables
  3-4; Results 3.3 Table 6) were located but not transcribed; recorded as a source-only record with
  `evidence_concerns`.
- Kwong et al. 2026 (DOI 10.1200/PO-25-00554): not retried this pass; remains blocked per the
  dossier.

No model was run. All five source files are exactly the bytes already cached under `/tmp`; none
were modified by this pass.
