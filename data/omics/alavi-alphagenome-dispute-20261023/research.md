# Research: disputing the Alavi 2026 AlphaGenome results

The author of Alavi 2026 confirmed on 2026-10-20 that both AlphaGenome scripts scored every variant one base from its true position (upstream issue #2). This batch records what follows in the store. The reasoning for each change is in `docs/reviews/2026-10-23-alavi-alphagenome-dispute.md`.

## Records in this batch

| Record | What it is |
| --- | --- |
| `rna-splicing-20261011-alavi2026-source-supplementary-tables` | The supplementary archive on Zenodo, pinned by hash. Supplemental Table VI gives every multi-gene variant's coding coordinate. |
| `metadata-correction-alavi2026-20261023-dataset-population` | Keeps the dataset's previous population text. |
| `metadata-correction-alavi2026-20261023-evaluation-population` | Keeps the twelve multi-gene evaluations' previous population text. |
| `metadata-correction-alavi2026-20261023-discrepancy-review-links` | Keeps revision 1's previous subject links (six results, now disputed). |
| `discrepancy-review-20261023-alavi-alphagenome-splicing-corrected` | Revision 2 of the review of `discrepancy-52a714eb6bb63442`: `corrected-records`, `confirmed-error`. |

## Edits to existing records

`apply-changes.py` makes them; it rewrites only the lines of the 60 records it changes:

- 42 results of the nine AlphaGenome evaluations: `disputed`, with a source warning. Values unchanged.
- The article source: an evidence concern with `applies_to` naming the nine evaluations.
- The multi-gene dataset and its twelve evaluations: population text from Supplemental Table VI.
- Two relevance judgements and the use-case summary for patient RNA splicing validation: AlphaGenome evaluations excluded and the disputed values no longer quoted.
- Revision 1 of the discrepancy review: subjects moved from six results to their three evaluations, so it stays in the release, plus the two multi-gene Borzoi evaluations so the resolved finding names both systems.

## Decisions

| Item | Decision | Reason |
| --- | --- | --- |
| What becomes disputed | The results, not the evaluations | The transcription of each evaluation is still correct; the values do not measure what they claim. The discrepancy rules and the website read result status. |
| Which protocols | All three, not only the multi-gene set | The OPA1 scores were made by the same scripts, and the thresholds used on the multi-gene set were tuned on them. |
| Concern scope | The nine evaluations | Their results are the whole of what the bug affects; the other models' rows of the same article stay usable. |
| Superseding results | None yet | No corrected values have been published. |
| Population wording | From Supplemental Table VI | The preprint's text says "within the canonical splice sites"; the author's own per-variant table puts 26 of 76 there. |
