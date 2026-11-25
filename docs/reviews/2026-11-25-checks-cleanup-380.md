# Deterministic Checks Cleanup and Migration Review, 2026-11-25

Reviewer: deterministic store migration script (`checks-cleanup-380`) for issue #380, derived from the 23 November checks audit. No human scientific review is claimed; every modified value or status follows the source-backed audit findings and vocabulary schema.

## Outcome

- Retired noisy check modules and rules:
  - Deleted `C1.minority-unit` (`scripts/omics/checks/unit_for_metric.ts`), retaining `C1.unit-scope-note` as an advisory report rule.
  - Deleted `C2.asserted-where-none` (`scripts/omics/checks/direction_default.ts`).
  - Deleted `C3.numeric-is-the-second-number` (`scripts/omics/checks/printed_vs_numeric.ts`), added `C3.null-numeric-value` covering all 386 results with `numeric_value: null`, honoured declared European number formatting (`numeric_representation`) and `printed_value_basis`, and checked bracketed second numbers before rounding.
  - Deleted `C4` (`qualifier_shape.ts`) and `C5` (`column_coherence.ts`) from `scripts/omics/checks/cli.ts`.
  - Updated `C9` (`scripts/omics/checks/duplicate_artifact.ts`) to ignore `superseded` and `excluded` sources and `supersedes`-linked components.
  - Widened `parseCell` and `numberFrom` (`scripts/omics/extract/tables.ts`) for leading plus signs, mid-dot decimals, parenthetical `(± y)` uncertainties, confidence/range intervals, and explicit unit suffixes when `options.unit` is provided.
  - Switched `defaultRatchetMode` to `"selective"` in `scripts/omics/checks/cli.ts`, blocking by default on `C2.unknown-where-declared`, `C2.metric-not-a-concept`, `C9`, `C9.same-artifact-and-url`, `C13`, and `C13.would-be-rewritten`, while keeping `C1.unit-scope-note`, `C2.opposite`, and `C3` rules advisory unless `CHECKS_RATCHET=blocking` is set.
- Vocabulary change (`data/vocab/metric.ttl`):
  - Removed `rb:defaultDirection` from `:cohens-d`, because signed Cohen's d can favour either sign depending on group coding and all 59 `amp-feng` Cohen's d results intentionally carry `metric_direction: "unknown"`.
- Store migration (`data/omics/checks-cleanup-380/changes.jsonl`):
  - Merged all 187 `C9.same-artifact-and-url` duplicate source groups by adding `supersedes` links from each canonical source to its copies, marking redundant copies `status: "superseded"` (while preserving `status: "source_checked"` on the 3 shared `rewire-local-*` artifact groups whose evaluations are pinned by active use-case judgements), and repointing citing records outside the frozen `data/evidence/results/` span-resolution inputs (`lit-001`, `lit-002`, `lit-009`, `lit-010`, `lit-021`, `lit-022`) and `benchmark-evidence-2026/search-audit.jsonl` records, which retain their recorded `source_ids` and resolve via `supersedes` links (matching the `phylogpn-2025` precedent).
  - Backfilled `attributes.metric_direction` on all 147 remaining `C2.unknown-where-declared` results (`145` from `rb:defaultDirection` in `data/vocab/metric.ttl`, plus `"lower"` on the `2` `torchcraft-20261115` negative perplexity-to-expression correlation results where more negative correlation reflects stronger inverse association).
  - Updated 61 `hitdisc-20261022-result-cache3-*` compound selection and prediction count results from `metric_direction: "higher"` to `"unknown"`, because predicting or selecting more compounds is not inherently better.

## Scope and Limits

- `C1.unit-scope-note` (`298`), `C2.opposite` (`60` after the two `torchcraft` inverse correlations), `C3.unparseable-printed` (`301`), and `C3.null-numeric-value` (`386`) remain pinned as advisory findings in `data/omics/checks-baseline.json` rather than altering historical stored units or `null` values without separate source review.
- Applied with `npm run records -- change` across the store and verified against SHACL and use-case pin invariants.
