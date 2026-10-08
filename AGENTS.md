# Benchmark data

Reviewed benchmark records, their source evidence, and the procedures for collecting and releasing them. The benchmark website and API live in rewire-bio/rewire-database. Execution lives in rewire-bio/rewire-benchmarks.

Read `docs/collection.md` before adding or changing data. Use the skills in `.agents/skills/`: `literature-search` to find sources, `extract-evaluations` to turn a source into records, `review-evidence` to check a batch independently, and `database-refresh` for the bounded monthly cycle (`docs/refresh.md`; the schedule stays planned until a full manual pilot and explicit activation).

Preserve IDs, numerical values and source evidence. Only the current release is kept in the repository; earlier releases are recorded by their receipts in `data/omics/releases/*.json`. Changes to scientific records require review and a new release (`docs/release.md`). Never publish private contributor data or automatically publish submissions. Do not add credentials or emulator state. Run tests, type checking and a data build before publishing.
