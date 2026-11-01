# AlphaGenome Atlas and Lu et al. 2025 batches reviewed, 2026-11-01

Independent review of the two batches saved in PR #214: `data/omics/alphagenome-atlas-20261019/` and `data/omics/lu-brandes-2025-heterogeneity-20261019/`. They were moved out of `pending-review`. Reviewed by a Claude agent that did not extract them. No human review is claimed.

## Sources

| Batch | Source | Pinned SHA-256 | 2026-11-01 retrieval |
| --- | --- | --- | --- |
| Atlas | medRxiv 10.64898/2026.09.16.26363192 v1 (still the only version) | `b32d1539…c453` | `b61f2811…10e4`, 83 pages |
| Lu et al. | bioRxiv 10.1101/2025.09.05.674459 v2 (still the latest) | `5b8e9392…9bf2` | `cfc74137…171e`, 21 pages |

Both servers stamp each download, so the 2026-11-01 copies have different bytes from the pinned ones. Each extractor was rerun on the new copy with only its hash assertion relaxed. Both reproduced the committed `batch.jsonl` byte for byte, with every row label and value assertion passing. So the new copies carry the content that was extracted. The pinned hashes stay on the records.

## How the values were checked

`npm run batch -- check-values` could not check either batch: Table S2 rows were not found in its row model, and Figure 1 and Supplementary Figure S2 have no text layer. The checks below replace it.

- **Atlas Table S2 (70 results).** Re-parsed from `pdftotext -raw` (the extractor used `-layout`): 14 rows by 5 columns. All 70 cells match in printed value, numeric value and metric (`auprc` for the baseline row, `auprc-relative-difference` for the ablations).
- **Atlas text and legends (39 results).**
  - 25 values: each sits inside its quoted sentence, and each quote is in the text layer.
  - 4 GREGoR recalls (29.5%, 12.5%, 74.3%, 61%): read against the paragraph on page 7. The 105 and 112 variant counts are in the GREGoR figure captions and Methods ('GREGoR analysis').
  - Legends of fig. S7E, S7F and S9E: checked the same way. The caption confirms S7E is SNVs only and S7F is SNVs and indels, which matches the batch.
- **Lu et al. Figure 1 (123 results).** Every bar label, the row order and each panel's N and %P compared with a 300 dpi render of page 8. The small labels of column 3 were also checked at 400 dpi. All match.
- **Lu et al. Supplementary Figure S2 (9 results).** Compared with a render of page 21; all match.
- **Claims.** Spot-checked against the text:
  - the window-position statement;
  - overlap filtering;
  - the SGE random baselines 0.146 and 0.194;
  - the Methods sentence behind "the original publication's splice scorer" (AUROC 0.708 against 0.614 and 0.779).

## Corrections made

1. **Atlas source page count.** The version said 53 pages, but its own locators cite page 70 and the PDF has 83. Corrected to 83.
2. **Two Table S2 rows with the same label.** Both are '+ No Indel Type' in 'Features Set to Zero', and their locators and qualifiers were identical. The second row (below 'No AlphaMissense Indel Features') now says so in its locator. Every ablation qualifier now names its row. The record IDs were already distinct and correct.

3. **Task links (rules v4 ratchet, #208).** The 14 new protocols had no task link, which `npm run check:task-links` now refuses.
   - The four TraitGym protocols are now `part_of` the existing TraitGym benchmark.
   - The other ten (ClinVar and ncVar, saturation genome editing, rare complex traits, GREGoR ranking, the DNM1 case) carry a `task_link_exemption` saying that no task in the store covers them, so the discrepancy rules treat their scope as unknown.
   - This correction is applied in each batch's `review.py`.

Corrections 1 and 2 were made in `extract/build_batch.py`. The rerun changed only those fields: 10 locators, 65 qualifiers and 1 version.

## Rulings

- **Values transcribed from rendered figures (Lu et al.).** Allowed: every bar prints its value as a label, and docs/collection.md forbids reading only figures without printed numbers.
- **The splice subsets differ (11,042 in Figure 1, 11,047 in Supplementary Figure S2).** Kept as two subsets, as extracted, with the limitation that the two all-outputs AUROCs (0.592 and 0.614) are on different variant sets.
- **AlphaGenome AUROC 0.310 on all variants (Lu et al. Figure 1).** Printed as such, below chance, with no comment in the text. Kept as reported.
- **The new metric `auprc-relative-difference`.** Its definition matches the Table S2 caption ("percentage difference relative to this baseline"). The scope note keeps it apart from AUPRC. Accepted.

## Gaps

- The Lu et al. authors' repository names a 2026 Nature Communications version with a rebuilt benchmark. It is not in the store.
- Atlas Fig. 2A, 2B and fig. S7A bars identified only by colour are not extracted, as recorded in `ag-atlas-20261019-claim-figures-not-extracted`.
