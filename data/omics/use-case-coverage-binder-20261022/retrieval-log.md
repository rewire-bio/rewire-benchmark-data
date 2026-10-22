# Retrieval log: de novo binder design evidence (#176)

Every step, in order, on 2026-10-22. Extraction agent: Claude; no human review claimed.

## 1. AlphaProteo, arXiv:2409.08022v1

The search pass flagged this artifact as unretrievable because the PDF exceeds the 10 MB page-fetch
limit, and read Table 1 from the HTML rendition instead, which truncated at 100,000 characters and
left Section S4.1 unread.

1. `curl -sL -o alphaproteo-2409.08022v1.pdf https://arxiv.org/pdf/2409.08022v1` returned HTTP 200 and
   12,333,400 bytes.
2. `shasum -a 256` gave `953b35644c0fa06ff090d7614c2e19525831f8fde50242e176d54474133c5a42`.
3. `pdftotext -layout` produced a 2,811-line text layer. Three "Badly formatted number" syntax
   warnings were emitted on an object beyond the table pages and did not affect the tables read.
4. Table 1 (page 6), Table S2 (page 39), Table S3 (page 39), Section S1.2.1 (page 19) and Sections S2,
   S4.1 and S4.2 (pages 25 and 27) were read and transcribed by hand.
5. `curl` of https://arxiv.org/abs/2409.08022v1 gave the licence as `licenses/by-nc-sa/4.0`. The
   licence is therefore recorded from the abstract page, not from the PDF bytes.

**Column assignment check.** Table 1 and Table S2 are wide layout tables and `pdftotext` does not
label the columns, so the assignment was checked arithmetically rather than taken on trust. The
Table S2 per-design-system denominators sum to the Table 1 pooled denominators for every target that
has more than one system: SC2RBD 94+47+31 = 172, PD-L1 94+31+34 = 159, TrkA 94+37 = 131, TNF-alpha
30+24 = 54. The pooled rates follow: PD-L1 (9.6% of 94) + (16.1% of 31) + (26.5% of 34) is 23 of 159,
14.5%, against Table 1's 15; TrkA (9.6% of 94) + (8.1% of 37) is 12 of 131, 9.2%, against Table 1's 9.
The pooled best-of KD values also follow: PD-L1 min(3.4, 47, 0.18) = 0.18 and TrkA min(0.96, 60) =
0.96, both matching Table 1.

## 2. BindCraft, Nature doi 10.1038/s41586-025-09429-6

1. The PMC article PDF was refused: `https://pmc.ncbi.nlm.nih.gov/articles/instance/12507698/bin/41586_2025_Article_9429.pdf`
   returned HTTP 404, and the `bin/...MOESM1_ESM.pdf` path returned an HTML interstitial. The PMC OA
   service (`oa.fcgi`) returned a 404 diagnostic page.
2. `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12507698/fullTextXML` returned HTTP 200 and
   226,059 bytes. SHA-256 `74bd2902d46460ec387ed6ee46b5bf8fe61b9ea09f2d7be4daa2046ac7e59d5d`. The XML
   was flattened to plain text with a tag strip and HTML-entity unescape for reading only; every value
   was transcribed by hand with the surrounding sentence quoted into its source locator.
3. `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12507698/supplementaryFiles` returned HTTP 200
   and 13,409,376 bytes, SHA-256 `a402ac50b4860e24430494cb4344c569bf29ef3b8e769372adcd3298659267de`.
   It unzipped cleanly. `41586_2025_9429_MOESM1_ESM.pdf` was read with `pdftotext -layout`
   (Supplementary Table 1 on page 12) and `41586_2025_9429_MOESM4_ESM.csv` (Supplementary Data 1) with
   Python's `csv` module.
4. **Figure 1b was not read.** It carries the per-target numerator and denominator inside graphic
   boxes, which are not in the JATS text. The per-target counts recorded here come from the Results
   prose, which states them for ten of the twelve targets. CrSAS-6 and CbAgo have a denominator in the
   prose and no numerator, and no count is recorded for them.
5. **Supplementary Data 1 was checked and not used to compute anything.** Its `Binding` column holds
   1, 0 or an empty cell. Treating the non-empty cells as the tested set reconciles with the prose for
   BBF-14 (11 tested, 6 binding), Bet v1 (7, 2), CD45 (16, 4), Der f7 (10, 4), Der f21 (7, 4), IFNAR2
   (9, 3), PD-1 (53, 13), SpCas9 (6, 6) and CLDN1 (7, 6), and fails for PD-L1 (13 non-empty rows with
   11 binding against 9 tested with 7 binding), CrSAS-6 (10 non-empty rows against 9 tested) and CbAgo
   (2 non-empty rows against 12 tested). Under `docs/collection.md` an aggregation whose row filter
   cannot be applied is a gap, not a computation, so no result in this batch carries a derivation.

## 3. Bennett 2025, Nature doi 10.1038/s41586-025-09721-5

1. `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12727541/fullTextXML` returned HTTP 200 and
   169,840 bytes, SHA-256 `d7876bc73c47f2cb3fcb0fa1ef917c89c9b67750a22f6402bf515f978cd1564a`.
2. `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12727541/supplementaryFiles` returned HTTP 200
   and 103,690,987 bytes, SHA-256 `6b1bd61ba4d69d5393f56e0e0d12bb4349b45ce12496a1d3e6a5a8467c39203a`.
   The archive has no end-of-central-directory record, so `unzip` reports "End-of-central-directory
   signature not found" and Python `zipfile` reports "File is not a zip file".
3. `bsdtar -tf` listed the members as a stream. `bsdtar -xf ... '*MOESM*'` extracted
   `41586_2025_9721_MOESM1_ESM.pdf` (100,209,865 bytes) and `41586_2025_9721_MOESM2_ESM.pdf` before
   failing with "ZIP decompression failed (-5)" on a later member.
4. `pdfinfo` confirms the extracted Supplementary Information member is a complete 129-page PDF titled
   "Atomically accurate de novo design of antibodies with RFdiffusion". Its SHA-256 is
   `f5d4fc4f3a65a2dc3ab696e165bb86bf150b2437cdc1a7046cfbecae8ccab05c` and that is what is pinned; the
   truncated archive is not a source record.
5. `pdftotext -layout` produced a 3,582-line text layer. Supplementary Methods Tables 5 and 6 are on
   page 67 and were transcribed by hand, every cell. Table 6 has eleven columns with wrapped headers;
   the column assignment was checked against the caption's own description of the columns and against
   the main text's statement that the per-target success rates "range from 0% to 2%".

## 4. Adaptyv EGFR competition

1. `curl -sL -o adaptyv.full.html https://www.biorxiv.org/content/10.1101/2025.04.17.648362v1.full`
   returned HTTP 200 and 493,217 bytes, SHA-256
   `17039d69ecc37f45f6c402511b8f4497ce631003689fa95ad1ab221f8f787a4f`. Script and style elements were
   stripped and the remainder flattened to 118,036 characters of text for reading.
2. `git clone` of github.com/adaptyvbio/egfr_competition_2, checked out at
   `fc91b91ddc367830b755b215dbc69669675ad6a0`. `results/result_summary.csv` has 402 data rows and the
   columns `username, name, kd, binding_strength, binding, expression, sequence, dna, pae_interaction,
   esm_pll, iptm, plddt, similarity_check, design_models`. SHA-256
   `b98dd231fa663e10e2768ad0cb7c8b33ba993bc809bd6168390ac87120ce3b7b`.
3. **Figures 3, 8, 9 and 10 were not read.** The per-method comparison, the per-round counts across the
   three binding thresholds, the design-category breakdown and the 60 affinities are all in those
   figures. Only the values printed in the body prose are recorded.
4. **The search pass's description of Figure 8 was wrong and is corrected here.** It recorded Figure 8
   as "hit rates at three thresholds". Figure 8's caption is "Number of (A) selected designs per round,
   (B) expressed designs, and (C) binders", and Section 4.1 says it summarises "the total number of
   validated binders across the 3 binding thresholds". So the three thresholds are real and undefined,
   but Figure 8 reports counts, not rates. The binding protocol's `success_threshold` is left unstated
   with reason `unreported` and no threshold is inferred.
5. **Per-method rates were not computed from the repository.** `design_models` is the entrant's own
   free-text declaration, Section 4.2 states the organisers "manually curated and categorized"
   entrants' workflow summaries into five design choices, and neither the README nor the paper states
   an aggregation over these rows. The one cross-check that was possible was done: the 1.21 nM Cradle
   affinity printed in Section 3.2 matches the row
   `round1zeroshot.K5Q_N70S_K71R_N73T_S87T_N88D_R179K_K183R_E213D_S214P` (username `Cradle`), whose
   `kd` column holds `1.2071528940932701e-09` molar.

## 5. Not reached

| Item | Why |
| --- | --- |
| BoltzGen (bioRxiv 10.1101/2025.11.20.689494) Tables 2 and 3 | Budget. Fifth in the task's priority order |
| Filius et al. 2025 (ACS Chem Biol 10.1021/acschembio.5c00774) SI Table S3 | Budget. Fifth in the task's priority order |
| Nature Communications minibinder paper (doi 10.1038/s41467-026-76760-5) and its Source Data | Not in this pass's priority list; the closest thing to an independent replication |
| PXDesign's own measured values (Tables 1 and 2) | Not in this pass's priority list. Its baseline column is excluded by rule |
| Adaptyv round 1 repository, `package.zip`, `package_neutralisation.zip`, `structure_predictions.zip`, `embeddings.zip` | Not retrieved |
| BenchBB (benchbb.bio), ProtDBench (arXiv:2605.04118) | Not retrieved |
| The primary sources behind AlphaProteo's compilation rows (Procko, Gainza, Cao, Berger, Yang, Watson) | Not retrieved; the compilation cells are recorded as a transcription claim, not as results |

## 6. Build and validation

- `data/omics/use-case-coverage-binder-20261022/extract/build_batch.py` builds `batch.jsonl` and
  `claims.csv` from the per-source modules. It is deterministic, sorts by record ID, asserts the record
  count per kind, and refuses a batch where a link does not resolve, a result does not point at exactly
  one evaluation, an evaluation does not have exactly one system, assessment and data link, a field
  carries both a value and a missing reason, a result or claim has no review block, or any record is
  not `needs_review`.
- `extract/validate_batch.ts` runs everything `addBatch` checks except the SHACL subset: the record
  schema, the dangling-link check against the whole store, the controlled vocabularies, the attribute
  registry, the description rules and the derivation rules. All 420 records pass.
- The SHACL subset check was **not** run, because it requires the records to be in the store and this
  pass does not run `npm run records -- add`. It runs when the review agent adds the batch, and CI runs
  it over the whole store.
