# Depth tier backfill, 2026-11-17 (#260)

Reviewer: Claude agent, automated. No human review is claimed. The edge-case rulings below are the coordinator's.

## What changed

Every model, method, benchmark and use case now carries `attributes.depth_tier`, derived by `npm run depth-tier -- backfill` with the rule in [tiers.md](../tiers.md) (`shared/omics/depth-tier.ts`). No other field, value, ID, link or status changed. The change was recorded with `npm run records -- change` against this review and `data/omics/depth-tier-backfill-20261117`, which holds the list of changed IDs and their tiers.

| Kind | Tier 1 | Tier 2 | Tier 3 |
| --- | --- | --- | --- |
| model | 140 | 125 | 121 |
| method | 370 | 70 | 178 |
| benchmark | 56 | 33 | 39 |
| use case | 19 | 6 | 6 |

## Rulings

1. Genomic use cases are tier 1 whatever their context. This places the research-only use cases plant-promoter-reporters, regulatory-variant-gene-follow-up and utr-translation-baselines in tier 1. Clinical genomics is the priority within tier 1, not a condition for it.
2. A record with both a DNA/RNA area and a protein area takes tier 1. This covers 7 models (five RNA 3D structure models, glm2 and MIMIC), 41 missense variant-effect methods and 4 benchmarks.
3. `molecular-interactions` without a protein area, and single-cell models under `cells-tissues`, are tier 3.
4. Records with no areas were set by hand from their names and sources (`noAreaTiers` in `scripts/omics/depth-tier.ts`). HelixFold3 and Protenix are structure models and are tier 2. The 16 methods are tier 3: acquired-configuration-c7901cd0e9a2eb889951, plus the ucc-research cell-type annotation and MPRA baselines. The four benchmarks with no areas take the tier of the use cases that judge them: foldbench 2, mprabc 1, cppc 3 and sctab 3. A follow-up issue asks for their areas to be filled in.
5. A benchmark takes the lowest tier of the use cases that judge one of its protocols or tasks relevant. Each of these was raised above the tier of its own areas:
   - ProteinGym, from 2 to 1.
   - Seven pathogen-identification benchmarks, from 3 to 1: Hall 2024 MTB, Portik 2022, Hu 2026, Wolf 2026, BERTax, MetaGeNN and Tisza 2026.
   - CASP16 affinity and FEP public, from 3 to 2.

## Limits

The depth tier is stored, so it does not follow later changes to areas or relevance judgements by itself. `npm run depth-tier -- check` lists records whose stored tier differs from the rule. It is optional until the intake agent sets it on new records.
