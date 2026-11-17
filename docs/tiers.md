# Depth tiers

How deeply a record is collected and kept up to date depends on its depth tier. This is the rule (#260). It is named `depth_tier` to keep it apart from licence tiers.

`attributes.depth_tier` (the integer 1, 2 or 3) on a `model`, `method`, `benchmark` or `use_case` says how deeply it is collected:

- Tier 1: DNA and RNA genomic models, methods and use cases, and the benchmarks those use cases rely on. Clinical genomics use cases are the priority within tier 1, not a condition for it. Full records, articles, executed recipes, our own benchmarks, a monthly sweep.
- Tier 2: protein models, methods, benchmarks and use cases. Full records, recipes for the top models, leads only, a quarterly sweep.
- Tier 3: everything else. Metadata only.

Records have no modality or lane field, so the depth tier is derived from `facets.areas` (`shared/omics/depth-tier.ts`). The search lanes map onto the areas as follows: `genomics` and `rna` are `dna-genomes` and `rna-transcriptomes`; `protein-fitness` and `structure-design` are `proteins-complexes`, `protein-function` and `protein-structure`; the other lanes are tier 3.

1. A record with a DNA or RNA area is tier 1. This includes records that also have a protein area, such as missense variant-effect predictors and RNA structure models: the lower tier number wins.
2. Otherwise, a record with a protein area is tier 2.
3. Otherwise it is tier 3, including single-cell and spatial models, `molecular-interactions` without a protein area, metabolomics, microbial communities and networks.
4. A use case follows the same area rule: any DNA or RNA area makes it tier 1, whether its context is clinical or research.
5. A benchmark takes the lowest tier of the use cases that judge one of its protocols or tasks relevant (a `links:assessed_by:<id>` claim on the use case that is not excluded), if that is lower than its own. The benchmarks a genomic use case relies on are therefore tier 1 whatever their own areas; for example ProteinGym (protein areas) and the pathogen-identification benchmarks (microbial areas) are tier 1 because genomic use cases judge them relevant.
6. A record with no areas cannot be placed by the rule (a benchmark with no areas but a linked use case takes that use case's tier). Set its tier by hand in `noAreaTiers` in `scripts/omics/depth-tier.ts`, and give the reason in the review that adds it.

`npm run depth-tier -- check` lists every record whose stored depth tier is missing or differs from the rule. `npm run depth-tier -- backfill <ids-file>` writes the derived tier and the changed IDs; record the change with `npm run records -- change <review> <batch-dir> $(cat <ids-file>)`. A new record should carry its depth tier when it is added; it is optional until #266. It is exported to the knowledge graph as `rb:depthTier` and to the prepared SQLite file as the `records.depth_tier` column (serving contract 3.5).
