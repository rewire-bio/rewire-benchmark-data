# Use-case baselines: source locators, 2026-10-12

Scope: the 26 `use-case-baseline-*` claims reviewed in [baselines-2026-10-12.md](baselines-2026-10-12.md).

Reviewer: the same separate Claude review agent. No human review is claimed.

## Why

The release validates its snapshot with the service schema (`validateSnapshot` in `shared/omics/validation.ts`). That schema requires every claim to have `attributes.source_locator`. The baseline claims had none, so the release failed with "Claim needs field, subject and source locator". `records -- add` and the pull-request tests do not run that rule.

## Change

- Each claim now has a `source_locator` naming, for each cited source in order, the section, table, figure or page that supports its rationale. The locators record the passages read during the review. The section names for Hwang 2026, Yuan 2024, Csendes 2025 and Segers 2026 were confirmed again from their Europe PMC full text. The Kaschta 2026 section names are copied from the store's own protocol and method locators.
- No value, rationale, method or source changed. Baseline pins cover the use case and its sources, not the claim's own attributes, so no claim needed re-pinning.
- `tests/release-validation.test.ts` runs `validateSnapshot` over every public record in the store. It is part of the fast test set, so pull requests now fail on any record the release would refuse.

## Checks

- `deriveUseCaseInputs` still publishes all 26 baselines.
- The release validation passes over the whole store. Before this change it reported exactly these 26 claims.
