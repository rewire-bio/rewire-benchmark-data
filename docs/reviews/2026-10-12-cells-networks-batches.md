# Review: cells-spatial and networks-mechanistic batches, 2026-10-12

Independent review of the five batches from the 2026-10-11 `lit-cells-networks` literature pass. Reviewers:
Claude review agents `reviewer-cn-1` (ye2026grn, sun2026de) and `reviewer-cn-2` (perturbench-v4, chen2026,
scmbench and the five new metric concepts). Neither extracted these batches. No human review is claimed.
Source transcription is not reproduction.

Each batch folder holds the reviewer's report for that batch, verbatim, and the corrections applied
(`review.md`), and the receipt (`review.json`, binding the SHA-256 of every file in the folder). The
corrections were applied by the extractor in the extraction scripts, as the reviewers specified, before the
batches were added to the store.

## Outcome

Every batch passed with corrections. No printed, numeric or uncertainty value was wrong, so nothing is
superseded. Each reviewer matched the SHA-256 of every pinned artifact (re-downloaded where the host allowed;
bioRxiv returned HTTP 429, so the Ye and Sun checks used the archived gzip copies, whose contents match the
recorded hashes), compared every result with their own parser, and hand-checked a stratified sample against
the rendered source.

| Batch | Source | Artifact SHA-256 | Reviewer | Values checked |
| --- | --- | --- | --- | --- |
| `lit-cells-networks-20261011-ye2026grn` | Ye et al. 2026, static GRN reconstruction from single-cell foundation models (bioRxiv v1), Tables 4-7 | `a6c3aae5…330dc7` | reviewer-cn-1 | 2,352 of 2,352 by parser; 48 by hand |
| `lit-cells-networks-20261011-sun2026de` | Sun et al. 2026, DE classification benchmark for perturbation models (bioRxiv v1), Tables 1-4 | `fa1c6a63…36cfdf` | reviewer-cn-1 | 170 results and 10 claims by parser; 48 by hand |
| `lit-cells-networks-20261011-perturbench-v4` | PerturBench arXiv v4 (NeurIPS 2025 Datasets and Benchmarks), Tables 2-13 | `b73f2644…0996a` | reviewer-cn-2 | 340 of 340 by parser; 48 by hand |
| `lit-cells-networks-20261011-chen2026` | Chen et al. 2026, harmonised single-cell and spatial foundation model benchmark (arXiv v2), Tables 2-5 and S2 | `8137338c…5ba539da` | reviewer-cn-2 | 378 of 378 by parser; 45 by hand |
| `lit-cells-networks-20261011-scmbench` | SCMBench, Nature Communications 2026, Supplementary Data 2 | `77582bcc…015443` (SD2) | reviewer-cn-2 | 241 of 241 by parser; 40 by hand |

Total: 3,481 results.

## Main corrections

- **ye2026grn.** A new evidence concern on the source: the Table 7 GENIE3 column repeats Table 6 in three
  reference blocks, and the 21 affected results say so in their review note. All 1,176 evaluations share one
  adaptation, split and inputs text per gene set, so the foundation models and the fitted baselines can be
  compared. Protocol descriptions say AUPRC uses the full ranked list. Checkpoints named in Appendix A.2 are
  recorded. DeepSEM is `specialist`.
- **sun2026de.** Scouter and TranScouter are `author_reported`: co-author Ouyang Zhu developed both. STATE
  runs without its pretrained embedding, so its configuration is not a foundation model here. Both
  judgements carry the reviewer's limitations, and the cross-cell-line rationale is the reviewer's text.
- **perturbench-v4.** Table 12 'DecoderOnly' is Decoder (Cov); the mode-collapse evaluation links to it and
  keeps its ID. Judgement constraints and endpoints are corrected, and `perturbench-energy-mmd` has the
  reviewer's definition.
- **chen2026.** DE metrics use the top 20 DE genes; PR-AUC and ROC-AUC are macro-averaged. Precision and
  recall are 'global' but appear to be averaged differently between models, which is now an evidence
  concern on the source. The spatial codes come from the Figure 2 legend.
- **scmbench.** Two evidence concerns record that some across-dataset means cover fewer datasets, and seven
  qualifiers say which. The 2,500-cell sampling is no longer asserted for the per-batch sheets.

## Use-case judgements

Twelve relevance judgements, all `proxy`, were approved with corrections. All are `source_checked` and
pinned, and their `assessed_by` links were added to the use cases.

- The three PerturBench v4 judgements (Norman19, Jiang24, Frangieh21) on
  `use-case-genetic-perturbation-response` are active.
- The two Sun judgements on `use-case-genetic-perturbation-response`, and the seven Chen judgements (four on
  `use-case-cell-type-annotation-transfer`, three on `use-case-genetic-perturbation-response`), are
  withheld by the use-case derivation. Both sources carry evidence concerns the reviewers required (Sun:
  which data setting the tables report; Chen: precision and recall averaging), and the derivation withholds
  every judgement on a source with concerns.
- No summary text or use-case field change was proposed or approved. The optional PerturBench evidence-gap
  wording was not applied.
- The `use-case-cell-type-annotation-transfer` summary pins the reviewed evaluations of every reviewed
  judgement on the use case, so adding the Chen judgements withheld it. `reviewer-cn-2` confirmed in writing
  that "The existing summaries do not cite these batches and remain accurate", so it was re-pinned unchanged
  with `npm run use-cases:repin`.
- The `use-case-genetic-perturbation-response` summary was already withheld on main before these batches;
  it was not re-pinned.

Every judgement that was active on either use case before these batches is still active.

## Changes to records already in the store

- `use-case-genetic-perturbation-response` and `use-case-cell-type-annotation-transfer`: `assessed_by`
  links.
- `use-case-summary-cell-type-annotation-transfer`: re-pinned, text unchanged.
- PerturBench v4 reuses the v1 configuration records for rows with the same printed name; they are not
  edited.

## Remaining gaps

- No figures were read.
- bioRxiv rate-limited the re-download of the Ye and Sun PDFs, so their checks used the archived copies.
- A revised genetic-perturbation summary that covers the new judgements needs a separate drafting and
  review pass.
