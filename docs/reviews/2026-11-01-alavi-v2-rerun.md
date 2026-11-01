# Alavi 2026 version 2: rerun AlphaGenome results added, 2026-11-01

Record changes for [#213](https://github.com/rewire-bio/rewire-benchmark-data/issues/213), the follow-up to the [2026-10-23 dispute](2026-10-23-alavi-alphagenome-dispute.md). Prepared by a Claude agent. No human review is claimed, and the extractor and reviewer were the same agent. Nothing was reproduced.

The batch is `data/omics/alavi-v2-20261101/`. `build.py` writes the new records, `check_cells.py` checks them with a second parse, `review.py` records this review, and `apply-changes.py` edits three stored use-case claims. Those IDs were recorded with `npm run records -- change` against this review and re-pinned with `npm run use-cases:repin`.

## Sources

| Source | Artifact | SHA-256 |
| --- | --- | --- |
| `rna-splicing-20261101-alavi2026-v2-source-article` | bioRxiv v2 full-text PDF, posted 2026-10-31, 12 pages, downloaded in a browser on 2026-11-01 (bioRxiv refused the scripted request) | `07bd32fffc1b31c222d43b0b18c213928e3fe111cc71c02fe2f95e64e6f7a798` |
| `rna-splicing-20261101-alavi2026-v2-source-supplementary-tables` | Zenodo 23784751, `supplementary_materials_alavi_2026_v02.zip` | `4652a256f70c8bde80fbc0408c914b951652b6435a78ad2d1107ab40a014bbac` |
| `rna-splicing-20261101-alavi2026-v2-source-scoring-scripts` | `2c8_alphagenome_merged_splicing_scorer.py` at `marcel-2c8/splicing-model-eval-2026` commit `2a3875de` | `84b4887ca3b44a6600d6a02046ab6de9d2f78c49592f82b16221d32fa5160516` |

The repository was renamed from `Probing-genomic-foundation-models-2026`; GitHub redirects the old URLs, so the existing issue #2 source record was left as retrieved. Through the GitHub API: the coordinate fix went into both v1 scripts on 2026-10-23 (`da0cf43e`, `4a5c9163`), the merged scorer was added on 2026-10-30 (`102a107f`), and issue #2 was closed on 2026-10-31. At the pinned commit, all three AlphaGenome scripts pass the 1-based position to `genome.Variant`.

## What changed between versions 1 and 2

- **Only the AlphaGenome rows.** All 126 other cells of Tables III and IV are printed as in version 1. `build.py` asserts each one against the stored version 1 result, so those results stand unchanged. The four count and percentage mismatches recorded on the version 1 source are still printed.
- **Four AlphaGenome rows instead of three.** Version 1 had either module, splice scorer and junction scorer. Version 2 has composite (the weighted score of AlphaGenome's splicing notebook, threshold 2.60), splice-site usage (0.93), splice-sites (0.32) and splice-junctions (natural-log fold change, 2.63). Each is a new configuration.
- **The multi-gene set is unchanged.** Supplemental Table VI in the v02 archive gives the same composition as v01 (`classify-table-vi.py` from the dispute batch, identical output). Methods A still calls the positives canonical splice-site variants, so the corrected population text stays.

## How the values were checked

- `build.py` parses `pdftotext -layout`. It asserts 13 rows per table and the row-label fragments around each row. It checks every bracketed percentage against count over denominator (within 0.05), and recomputes accuracy and PPV from each AlphaGenome row's counts. All 8 rows match exactly.
- `check_cells.py` parses `pdftotext -raw`, where each label sits on its own lines before the value line. It asserts the column header order and matches all 56 cells (`cell-check.tsv`).
- `npm run batch -- check-values` cannot parse Roman-numeral table locators ("Table III") and reported every result as `locator_not_parsed`, so `check_cells.py` takes its place. A manual read of both tables in the text layer against the stored values found no difference.

## Rulings

- **Composite and splice-site usage thresholds.** Methods D says variants were pathogenic "if their composite score was greater than or equal to 2.60 or their splice-site usage score greater than or equal to 0.93". The tables print the two as separate rows with different counts, so each is recorded as its own configuration with one threshold. This is noted as a limitation on the v2 source.
- **Which version 1 results the rerun replaces.** Splice-sites and splice-junctions rerun the two version 1 scripts, so their 28 results replace the version 1 splice scorer and junction scorer results of the same protocol and column (`supersession.tsv`). Composite and splice-site usage are new. The version 1 either-module row has no successor.
- **No `supersedes` links.** `publicRecords` (`scripts/omics/schema.ts`) drops every record that links to a disputed record. A `supersedes` link from a version 2 result to a disputed version 1 result would therefore have removed the version 2 result from the release. Marking the version 1 results `superseded` would have put their wrong values back into the release. The version 1 results stay `disputed`, and the pairing is recorded in `supersession.tsv`, in each result's review note and in the revision 3 claim. This needs a relation the release tolerates; see Gaps.
- **Version 1 warnings left as they are.** The version 1 evidence concern and the 42 result warnings say the values are disputed "until the rerun is published". The rerun is now published, but the version 1 values remain wrong and stay withheld, so the warnings still apply.

## Discrepancy `discrepancy-52a714eb6bb63442`

Revision 3 (`discrepancy-review-20261101-alavi-alphagenome-splicing-rerun`) keeps the state `confirmed-error` with action `corrected-records`. Its `resolved_by` names the version 2 source and its 56 results. Its subjects are the nine version 1 AlphaGenome evaluations and the twelve version 2 ones.

## Use-case claims

- The judgements `use-case-mapping-rna-splicing-20261011-alavi2026-multigene` and `...-opa1-evaluation` now list the four version 2 AlphaGenome evaluations of their protocol in `reviewed_evaluations`. They cite version 2, and they say the version 1 AlphaGenome evaluations stay excluded. Relevance (`proxy`), comparison group and strata are unchanged.
- The use-case summary `use-case-summary-patient-rna-splicing-validation` previously said the AlphaGenome rows were being rerun. It now gives version 2's Table IV sensitivity and specificity for the four AlphaGenome scores. `apply-changes.py` asserts each number against the version 2 result it comes from.

## Gaps

- The store has no relation for "corrects a disputed record" that survives the release filter. Until it does, corrections of disputed results cannot be linked to the records they replace.
- ROC-AUC and PR-AUC values printed in the version 2 text (Results G; Supplementary Figs. S7 and S8) were not extracted.
