# Retrieval log

2026-10-22. Extractor: Claude extraction agent; no human review claimed.

## 1. Boltz-2 supplement

1. `curl -L "https://europepmc.org/api/fulltextRepo?pprId=PPR1038344&type=FILE&fileName=NIHPP2025.06.14.659707v1-supplement-1.pdf&mimeType=application/pdf"` returned HTTP 403 with a 46-byte body. Recorded as a failed route, not as absence of the file.
2. `curl -L "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12262699/supplementaryFiles"` returned HTTP 200, 7,085,747 bytes, SHA-256 `25050dabd9c66fdb955704095023037f1bbabc3a93b7b61f00344c75df8bdb70`.
3. Unzipped into an empty directory. It holds 16 figure images and one PDF, `NIHPP2025.06.14.659707v1-supplement-1.pdf`, 6,515,003 bytes, SHA-256 `be867a5d92add8b223d47d882a4213ad489741f3e4d5081a0901a54370342569`. That matches the hash the preceding literature search recorded, verified here by independent re-download.
4. `pdftotext -layout` (poppler 26.08.0) produced `supp-layout.txt`, SHA-256 `6e19c85a90c118fd5fd045981a7ebfa5559d9b0a2b4c700b2da0c7393a417c17`.
5. Read the text layer to locate the tables: Table 11 at line 1685, Table 12 at 1700, Table 13 at 1720, Table 14 at 1742, Table 15 at 1760, Table 16 at 1788, all in appendix E.2.1 and E.2.2. Read appendix D.2.1 ('We evaluate model performance on the following held-out affinity test sets', 'Data leakage control'), D.2.2 ('Evaluation metrics', 'Baselines').
6. `extract/extract_leadopt.py` splits each table row on two or more spaces and asserts, for each table, the column-header line, the sub-label line, every row label and the exact cell count per row (11 for Table 11, 12 for Table 12, 10 for Table 14). Any change to the pinned text layer breaks an assertion rather than shifting a value silently.

## 2. Ross et al. 2023

1. `curl -L "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10576784/fullTextXML"` returned HTTP 200, 162,763 bytes, SHA-256 `f371d2e373306588d11b695b8de21b253a90293d6a15884f635bcf927bdebb1d`. Matches the hash the literature search recorded.
2. `extract/extract_leadopt.py` parses the `<table-wrap>` elements, strips tags, normalises thin and non-breaking spaces inside unit labels, and asserts the header row and every row label of Tables 1, 2 and 3. Table 3's header is asserted to be exactly `["Accuracy metric", "Experimental survey", "FEP+ benchmark"]` and its body to be 6 rows.
3. Each Table 3 cell is matched against `^([\d.]+) \[([\d.]+), ([\d.]+)\]$`. A match becomes `printed_value` with the bracketed interval recorded as a 95% bootstrap confidence interval; the only non-matching cells are the two the source prints as `N/A`, and the script asserts that.
4. The aggregation and interval wording was read from the Table 3 legend and from Methods, 'Accuracy metrics'. The per-system tuning limit was read from Results, 'Using FEP to resolve ambiguities in the structural inputs'.

## 3. Gilson et al. 2026

1. `curl -L "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750038/fullTextXML"` returned HTTP 200, 162,736 bytes, SHA-256 `a1d7fdc52df61c4d75197f04be91b511b7d093d229d96a0815a11f95e350256b`.
2. The affinity-ranking results are in Figures 8 and 9 with no printed values, so nothing was extracted as a result. Six statements carrying numbers were transcribed by hand from the body text as claims.
3. For each of the six, `extract/extract_leadopt.py` asserts that the quoted sentence occurs in the tag-stripped artifact text after punctuation and whitespace are normalised. Two quotes were corrected during this check: 'typical best D3R result' is printed as 'typical best Stage 1 D3R result'.
4. Table 2 of this paper reports pose accuracy (skip-penalised mean LDDT-PLI), not affinity, and was not extracted. Table 1 was read for the series sizes and affinity ranges and is cited on the dataset record rather than extracted cell by cell.

## 4. Boltz repository check

The search pass noted, from a search snippet it could not verify, that `github.com/jwohlwend/boltz` listed
its FEP+, CASP16 and MF-PCBA affinity predictions and evaluation scripts as "coming soon". Checked here
against the repository itself through the GitHub API, 2026-10-22:

1. `GET /repos/jwohlwend/boltz`: MIT, default branch `main`, last pushed 2026-05-29T08:20:25Z. Latest
   release `v2.2.1` (2025-09-08).
2. `GET /repos/jwohlwend/boltz/commits/main` pins `main` to `b1ebfc46ecf57f5414e0d1a6f9027bbb122c53bc`.
3. `README.md` at that commit (SHA-256 `79149435313841e6f9cc0c8b581259f3952a2469cbe6f9a733f7143b557025c2`)
   reads "Coming soon: updated evaluation code for Boltz-2!" and "we will soon provide the evaluation
   scripts and structural predictions for Boltz-2, Boltz-1, Chai-1 and AlphaFold3 on our test benchmark
   dataset, and our affinity predictions on the FEP+ benchmark, CASP16 and our MF-PCBA test set."
4. `docs/evaluation.md` repeats that and marks "Evaluation files", "Evaluation setup" and "Evaluation
   script" all as coming soon for Boltz-2. Only the Boltz-1 section links published outputs, on Google
   Drive, and those are structure predictions rather than affinities.
5. The recursive tree at that commit holds `scripts/eval/{run_evals,aggregate_evals,physcialsim_metrics}.py`
   and `src/boltz/model/modules/affinity.py`, but no affinity prediction outputs and no FEP+, CASP16 or
   MF-PCBA evaluation data.

Conclusion: the snippet was accurate. No per-series Boltz-2 affinity value is published, so nothing was
extracted from the repository and no record cites it. Recorded as a gap and as planned work.

## 5. Store search before creating records

`git grep` over `data/entities/` and `data/evidence/` for: `boltz-2`, `boltz2`, `ligand-affinity`, `casp16`,
`FEP`, `FEP+`, `OpenFE`, `ABFE`, `MM/PBSA`, `MMPBSA`, `Chemgauss`, `BACPI`, `Ross`, `protein-ligand-benchmark`,
`CASF`, `experimental survey`.

Reused: `catalog-model-boltz-2`, `catalog-task-ligand-affinity`.
No existing record was found for FEP, FEP+, OpenFE, ABFE, MM/PBSA, FMO, Chemgauss4, BACPI, the Ross 2023
benchmark, the protein-ligand-benchmark or the CASP16 affinity assessment, so those are new.
`coverage.json` lists the existing protocols that bear on the use case but were left unmapped in this pass.

## 6. Validation run

- `extract/extract_leadopt.py` rebuilds `batch.jsonl`, `claims.csv` and `coverage.json` deterministically from the three pinned artifacts.
- Schema, attribute registry, vocabulary, description and link-target checks: all pass, run against the whole store plus this batch in memory.
- SHACL shapes: the batch's subset graph was built in a sandbox directory with `subsetQuadLines` over the store plus this batch, then checked with `npm run kg:build -- --shapes-only`. Result: 'Records conform to the shapes'. 113 of the 369 records enter the subset graph, because `publicRecords` keeps `needs_review` results (and anything linking to them) out of the public graph; that is the same set `records -- add` would check.
- `npm run records -- add` was deliberately **not** run. The review agent adds the batch after writing `review.json`.
