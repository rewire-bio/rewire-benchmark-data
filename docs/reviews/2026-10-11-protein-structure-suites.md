# Review: protein-fitness and structure-design batches, 2026-10-11

Independent review of the five batches from the `lit-protein-structure` literature pass. Reviewers: Claude
review agents `reviewer-ps-1` (deepprotein, prime) and `reviewer-ps-2` (scaffoldlab, lipp, afesmfold and
the two new metric concepts). Neither extracted these batches. No human review is claimed. Source
transcription is not reproduction.

Each batch folder holds the reviewer's report for that batch, verbatim, and the corrections applied
(`review.md`), and the receipt (`review.json`, binding the SHA-256 of every file in the folder). The
corrections were applied by the extractor in the extraction scripts, as the reviewers specified, before the
batches were added to the store.

## Outcome

Every batch passed with corrections. No printed or numeric value was wrong. Each reviewer re-retrieved the
pinned Europe PMC JATS XML, matched its SHA-256, and compared every result with an independent parse, plus
a hand sample.

| Batch | Source | Artifact SHA-256 | Reviewer | Values |
| --- | --- | --- | --- | --- |
| `lit-protein-20261011-deepprotein` | DeepProtein: deep learning library and benchmark for protein sequence learning (Bioinformatics 2025) | `b5869213…64b7f` | reviewer-ps-1 | 436 results |
| `lit-protein-20261011-prime` | PRIME: an evaluation framework for protein representation inference and generalization in viral mutation space (BMC Genomics 2026) | `f6aac4c2…047971` | reviewer-ps-1 | 168 results |
| `lit-structure-20261011-scaffoldlab` | Scaffold-Lab: critical evaluation and ranking of protein backbone generation methods (PLoS Comput Biol 2026) | `9ff68ef8…9840d0` | reviewer-ps-2 | 160 results |
| `lit-structure-20261011-lipp` | The LiPP benchmark set for modeling lipid-protein complexes (J Chem Inf Model 2026) | `6ff34f2f…4a2ca` | reviewer-ps-2 | 27 results |
| `lit-structure-20261011-afesmfold` | Comparative evaluation of AlphaFold and ESMFold for monomeric and dimeric proteins (NAR Genom Bioinform 2026) | `aae321d0…798b8` | reviewer-ps-2 | 216 results |

Total: 1007 results.

## Main corrections

- **deepprotein.** The rho columns are Spearman rank correlation, as the article's Evaluation metrics section
  defines them; the 51 results and 3 protocols move from `correlation` to `spearman-correlation`. ROC-AUC on
  a 0 to 100 scale is `percent`. The Prot-T5 and Prot-T5-XL configurations carry an identity note.
- **prime.** All 168 evaluations are `author_reported`. The spread is the standard deviation across random
  seeds, with no sample count recorded. ESM-C configurations point at the store's `discovery-model-esmc`.
  The new source supersedes `prime-2026` and `evidence-expansion-prime-2026-f6aac4c2`; two re-extracted
  cells supersede `lit-021` and `lit-022`.
- **scaffoldlab.** Designability keeps its concept but its qualifier and an evidence concern state that the
  criterion is sc-TM above 0.5 and the aggregation behind the column is not stated. Two metric concepts are
  added: `rank` and `topsis-relative-closeness`.
- **lipp.** The batch reuses the store's existing source record for these bytes
  (`evidence-expansion-p2-lipp-2026-6ff34f2f709a`) instead of adding a third; its limitations moved there.
  The two full-set cells already stored as `lit-041` and `lit-042` are superseded. PoseBusters protocols
  describe small-molecule poses from the cited literature; the empty PB-valid v1 protocol is removed. Dash
  cells: 4 in Table 2 and 9 in Table 3.
- **afesmfold.** Dimer classes carry their DockQ bands. Five evidence concerns record internal conflicts in
  the experimental-method and template-quality columns. The monomer judgement is `proxy`, not `direct`.

## Use-case judgements

Five relevance judgements, all `proxy`, were approved with corrections, and their `assessed_by` links were
added to the use cases.

- The two LiPP post-cutoff judgements on `use-case-structural-hypotheses-experiments` are `source_checked`
  and pinned, and active.
- The two AlphaFold and ESMFold judgements on the same use case, and the DeepProtein stability judgement on
  `use-case-protein-stability`, stay `needs_review`. Their sources carry evidence concerns the reviewers
  required, and the use-case derivation withholds every judgement on a source with concerns. Each batch's
  `review.md` gives the detail and what would let them be served.
- The DeepProtein reviewer's revised summary for `use-case-protein-stability` was not applied, because it
  describes the held judgement; the reviewer gave holding the judgement and leaving the summary alone as
  the alternative. The existing summary is unchanged and still published.
- The `use-case-structural-hypotheses-experiments` summary pins the reviewed evaluations of every reviewed
  judgement on the use case, so adding the two LiPP judgements withheld it. `reviewer-ps-2` confirmed in
  writing that the summary "stays as it is in the store, verbatim and unchanged. It is still accurate", so
  it was re-pinned unchanged with `npm run use-cases:repin`.

Every judgement that was active on either use case before these batches is still active.

## Changes to records already in the store

- `evidence-expansion-p2-lipp-2026-6ff34f2f709a`: limitations added (LiPP L1, L3), with a
  `metadata-correction-` claim keeping the previous value.
- `lit-041` and `lit-042`: `superseded` by the new LiPP full-set results (L2). Values unchanged.
- `use-case-structural-hypotheses-experiments` and `use-case-protein-stability`: `assessed_by` links.
- PRIME's new source and two results supersede `prime-2026`, `evidence-expansion-prime-2026-f6aac4c2`,
  `lit-021` and `lit-022` through `supersedes` links; those records are not edited.

## Remaining gaps

- No figures were read. Supplementary files (PRIME Supplementary Table 6, DeepProtein, LiPP, Scaffold-Lab)
  were not retrieved.
- No second publication channel was reachable for the DeepProtein and PRIME hand samples.
- The structural-hypotheses use-case summary does not yet mention the new links; a revised summary needs a
  separate drafting and review pass.
