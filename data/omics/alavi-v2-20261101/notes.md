# Alavi 2026 version 2: rerun AlphaGenome results (issue #213)

Version 2 of Alavi 2026 (bioRxiv 10.64898/2026.10.02.756289v2, posted 2026-10-31) reruns AlphaGenome after the
1-base coordinate fix reported in upstream issue #2. This batch adds the rerun AlphaGenome rows of Tables III
and IV and revision 3 of the discrepancy review.

## Retrieval

- The v2 PDF was downloaded in a browser on 2026-11-01; bioRxiv refused the scripted request. SHA-256
  `07bd32ff...7a798`, 12 pages, 2,165,572 bytes.
- The v2 JATS XML holds metadata only, as v1's did.
- Zenodo record 23784751 is version 02 of the supplement. Its Supplemental Table VI gives the same multi-gene
  composition as v01 (`classify-table-vi.py` of the dispute batch, identical output).
- The repository is now `marcel-2c8/splicing-model-eval-2026` (renamed). Pinned to commit `2a3875de`. All three
  AlphaGenome scripts pass the 1-based position to `genome.Variant`.

## Decisions

- **Only the AlphaGenome rows changed.** `build.py` asserts that all 126 other cells of Tables III and IV equal
  the stored v1 results. The v1 results stand, and no record is added for them.
- **Four configurations, not three.** v2 replaces v1's either-module, splice scorer and junction scorer rows with
  composite, splice-site usage, splice-sites and splice-junctions. Each gets a new configuration, because the
  thresholds changed (splice-sites 0.14 to 0.32; junctions 0.43 to 2.63) and the junction score now uses a
  natural-log fold change.
- **Which results replace which.** Splice-sites reruns `2c8_alphagenome_splicescorer.py` and splice-junctions
  reruns `2c8_alphagenome_junctionscorer.py`, the two scripts of v1, so their 28 results replace the matching v1
  results (same protocol and column). `supersession.tsv` lists the pairs. Composite and splice-site usage come
  from the new merged scorer script and replace nothing. v1's either-module row has no successor.
- **No `supersedes` links; the v1 results stay `disputed`.** The release drops any record that links to a
  disputed record (`publicRecords` in `scripts/omics/schema.ts`), so a `supersedes` link would have removed the
  28 new results from the release. Changing the v1 results to `superseded` instead would have put the wrong v1
  values back in the release. The pairs are kept in `supersession.tsv`, in each result's review note and in the
  revision 3 claim. A relation for "corrects a disputed record" that the release tolerates would fix this.
- **Composite and splice-site usage thresholds.** Methods D prints one sentence: pathogenic "if their composite
  score was greater than or equal to 2.60 or their splice-site usage score greater than or equal to 0.93". The
  tables print them as separate rows, so each configuration carries one threshold. Recorded as a limitation on the
  source.
- **Protocols and datasets are reused** from the v1 batch: the variant sets, the OPA1-tuned threshold procedure
  and the columns are unchanged.

## Checks

- `build.py`: pdftotext -layout, 13 rows per table, label fragments asserted, bracketed percentages within 0.05
  of count over denominator, accuracy and PPV recomputed from each AlphaGenome row's counts (all 8 rows exact).
- `check_cells.py`: pdftotext -raw, labels read from their own lines, header order asserted; 56 of 56 cells match
  (`cell-check.tsv`).
- `npm run batch -- check-values` cannot parse Roman-numeral table locators ("Table III"), so it reported
  `locator_not_parsed` for all 56; `check_cells.py` replaces it.

## Not changed

- The v1 evidence concern and the 42 v1 result warnings still say the values are disputed "until the rerun is
  published". The v1 values remain wrong, so the warnings still apply; the dated review records that the rerun is
  now published.
