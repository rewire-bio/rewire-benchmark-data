# Discrepancy grouping, study identity, board completeness, and use-case payload compaction (2026-11-27)

## Summary of changes

1. **Discrepancy comparison grouping (`kb/discrepancies.py`, `scripts/kg/contradictions.py`)**
   Added `aggregation` and normalized `scoring_conditions` to the within-study comparison group key in both derivations, stripping submission-specific, configuration-specific, and count keys (`IGNORED_CONDITION_KEYS`) identically to `kb/board.py`. Distinct scoring thresholds, reference versions, and aggregations now remain separate comparison groups while different submissions on the same test continue to compare together.

2. **Study identity (`data/entities/sources.jsonl`)**
   - Joined MSAlign arXiv v2 (`uc20260930-source-msalign-v2`) as a companion of the primary paper PDF (`evidence-official-760ab2fa8c396aeb796c`).
   - Joined the five Rewire local FLIP2 execution report sources (`rewire-local-20260920-source-flip2-composition`, `rewire-local-20260920-source-flip2-train-mean`, `rewire-local-20260921-source-composition22`, `rewire-local-20260921-source-esm2-35m`, `rewire-local-20260921-source-esm2-8m`) into one study via `companion_of`.
   - Set `doi` to `10.5281/zenodo.10616895` (verified in the archived `zenodo.json` metadata for Zenodo record 10616895) on the three trRosettaRNA Zenodo package sources (`model-pages-20261126-batch3-trrosettarna-source-package-env`, `package-readme`, `zenodo`) and linked the Zenodo record as a companion of the trRosettaRNA paper (`model-pages-20261126-batch3-trrosettarna-source-paper`).

3. **Board store gaps, AlphaMissense kind, and use-case groups (`kb/board.py`, `shared/omics/boards.ts`, `data/entities/`)**
   - Added `configuration_of` links to the 43 unlinked `amp-feng-20261007-config-*` records (linking to AlphaGenome, Caduceus, Enformer, HyenaDNA, and Sei) and to `amp-oncology-rna-20261007-issue-10-config-strelka2` (linking to Strelka).
   - Added `legacy_kinds` to `attributeRegistry.model` (`shared/omics/attribute-registry.ts`), regenerated `data/ontology/rb-attributes.ttl` and `data/ontology/attribute-shapes.ttl` via `npm run kg -- terms`, and updated `somatic-oncogenicity-20261009-method-alphamissense` to `kind: "model"` with `entity_level: "family"` and `legacy_kinds: ["method"]`.
   - Emitted data-driven `groups` in `kb/board.py` and validated `groups` in `shared/omics/boards.ts`.

4. **Use-case detail payload and judgement evaluation limit (`shared/omics/use-cases.ts`)**
   - Raised `MAX_JUDGEMENT_EVALUATIONS` and the `evaluation_ids` limit from 500 to 2000.
   - Deduplicated protocol, task, and citation source records into a top-level `records` map on `useCaseQueryFrom(...).get()` responses rather than repeating them on every mapping.
