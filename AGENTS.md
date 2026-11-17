# Benchmark data

Reviewed benchmark records, their source evidence, and the procedures for collecting and releasing them. The benchmark website and API live in rewire-bio/rewire-database. Execution lives in rewire-bio/rewire-benchmarks.

Read `docs/collection.md` before adding or changing data. Use the skills in `.agents/skills/`: `literature-search` to find sources, `extract-evaluations` to turn a source into records, `review-evidence` to check a batch independently, and `database-refresh` for the bounded monthly cycle (`docs/refresh.md`; the schedule stays planned until a full manual pilot and explicit activation).

Collection depth is tiered (`attributes.depth_tier` on models, methods, benchmarks and use cases; [docs/tiers.md](docs/tiers.md)). Tier 1, DNA/RNA genomic models, methods, use cases and their benchmarks, gets full records, articles, executed recipes and a monthly sweep. Tier 2, protein, gets full records, recipes for the top models, leads only and a quarterly sweep. Tier 3 gets metadata only. Read the tier before deciding how far to take a record, and give every new model, method, benchmark and use case its depth tier.

Discrepancies between studies (`docs/discrepancies.md`) are leads flagged by the knowledge-graph build, not errors; what is done about one is recorded as a `discrepancy_review` claim revision.

Preserve IDs, numerical values and source evidence. Releases are recorded by their receipts in `data/omics/releases/*.json`; their files are not committed but published as release assets (`npm run release:fetch` downloads them). Changes to scientific records require review and a new release (`docs/release.md`). Never publish private contributor data or automatically publish submissions. Do not add credentials or emulator state. Run tests, type checking and a data build before publishing.
