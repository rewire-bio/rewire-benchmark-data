# Test fixtures

`catalogue.ts` is a small synthetic release used across the query engine and validation tests.

## Historical dataset reuse

`release-compatibility-2026-09-22.json` contains 42 unmodified record objects from the 21,974-record release `2026-09-22-f58a0f1d267f`, preserved in `rewire-bio/rewire-benchmark-data` at `7ced2cd01a9f59da51a1eab562c991e142f5e494`. The adjacent provenance JSON records the source archive and uncompressed catalogue SHA-256, original record count, fixture checksum and a checksum for every retained record.

Selection starts with the two AMFR datasets, their random and ESM2 evaluations, and all ten result rows. It follows every string-valued reference to another record, including links, sources, profiles and run recipes, until the dependency closure is complete. Original record order and values are retained. The schema version, release ID and release date are retained; the aggregate `coverage` object is empty because full-release totals would misrepresent this subset. Per-record hashes use UTF-8 JSON with sorted object keys, no insignificant whitespace and literal Unicode.

`tests/shared/release-compatibility.test.ts` validates this 42-record closure, the exact `same_data_as` relationship, all four invalid relationship variants, separate five-row result sets, their exact evaluation identities and disjoint result IDs. The original 21,974 count is extraction provenance, not a claim that this fixture includes the complete release. Full release generation and historical artifact verification belong to the data repository. No archive lookup, producer checkout or fixture generation occurs at test runtime.
