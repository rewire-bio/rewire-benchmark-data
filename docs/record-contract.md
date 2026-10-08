# Omics catalogue interchange v1

Reviewed JSONL records are the publication source. The release builder writes the catalogue snapshot and versioned JSONL/CSV exports for each release. This is a public-data contract; email addresses, submission tokens, and private correspondence must never be exported.

Each record is an object:

- `id`: stable lowercase slug, unique across kinds.
- `kind`: one of `model`, `method`, `configuration`, `pipeline`, `service`, `benchmark`, `task`, `protocol`, `evaluator`, `dataset`, `dataset_subset`, `baseline`, `evaluation`, `result`, `source`, `claim`. The list and the allowed link relations are defined in `services/omics/src/entity-kinds.ts`.
- `name`: display name.
- `description`: plain text.
- `status`: `discovered`, `needs_review`, `source_checked`, `reproduced`, `disputed`, `superseded`, or `excluded`. Source-checked is not reproduced.
- `facets`: object mapping facet names (e.g. `areas`, `tasks`, `modalities`, `organisms`, `method_types`) to arrays of strings. No closed domain enum.
- `source_ids`: IDs of source records supporting this entity.
- `links`: array of `{ "relation": "...", "target_id": "..." }`. Allowed relations are listed in `services/omics/src/entity-kinds.ts` (for example `model`, `benchmark`, `dataset`, `variant_of`, `alias_of`, `part_of`, `supersedes`, `source`). References resolve within a release.
- `attributes`: kind-specific JSON object. Explicit unknown metadata uses null and `missing_metadata` reasons, never invented values.

A `source` has attributes `url`, `version`, `retrieved_at`, optional `doi`, `publication_status`, `artifact_sha256`, `locator` and `licence`.
A `model` has `entity_level` (`family`, `checkpoint`, `method`, `service`), `version`, `reported_name`, `missing_metadata`, and optional architecture/training/input/output/licence/access metadata. Do not collapse unidentified versions into a concrete checkpoint.
A `benchmark` has `entity_level` (`suite`, `protocol`, `task`, `challenge`, `evaluator`), `version`, `task`, `scope_note`, `missing_metadata`.
A `dataset` has `version`, `split`, `missing_metadata`, optional assay/context/accession metadata.
A `baseline` has `baseline_type`, `applicability` (`proposed` or `source_supported`), `requirements`, `missing_metadata`.
An `evaluation` has `origin` (`author_reported`, `independent_paper`, `paper_compilation`, `rewire_run`, `unreported`), `protocol`, `version`, `comparison` object, `missing_metadata`, links to model/benchmark/dataset, and optional `original_evaluation` link. Comparison fields: `protocol_id`, `dataset_version`, `split`, `population`, `inputs`, `adaptation`, `metric_implementation`, `aggregation`, `budget`; unknown fields are null and block automatic comparison.
A `result` links to exactly one evaluation. Attributes: `printed_value` (string), `numeric_value` (string decimal or null), `metric`, `metric_direction` (`higher`, `lower`, `unknown`), `unit`, `uncertainty` (string or null), `source_locator`, `review` (object with `method`, `reviewer`, `reviewed_at`, `notes`), `missing_metadata`, optional `legacy_id`. Retain original paper IDs and result IDs for migration. Reviewed results need a precise locator and source.
A `claim` links to a `subject` and has `field`, `value`, `source_locator`, `review` and supporting source IDs. A checked score does not mark all metadata as checked.

Snapshot JSON: `{ "schema_version": "1.0", "release_id": "...", "released_at": "UTC ISO date", "records": [...], "coverage": {...} }`. Manifest: schema/release/time, record counts, input digests, file hashes and changelog. All records sorted by ID; release building is deterministic given the records and explicit timestamp. Excluded records remain in the archive but are absent from public catalogue pages.

## Biological extensions

`attributes.extensions` supports validated `genomics`, `protein`, `cellular`, `molecular_measurement`, `microbial` and `mechanistic` blocks. The contract is in `scripts/omics/extensions.ts`. Coordinates carry their assembly, convention, strand and window orientation; variant offsets are zero-based within the window. Protein identity thresholds are fractions, with MSA/template provenance separate. Cellular doses and times require units. Molecular measurements carry identifier namespace, platform, preprocessing and units; microbial references carry taxonomy/database versions. Mechanistic evaluations carry solver, constraints and conditions. Missing blocks are unextracted, not evidence that these factors are inapplicable; null records an explicitly unknown field. Extend the schema through a reviewed change when a new modality requires more fields.

## Explanatory profiles and supported associations

Model and benchmark explanations are validated enrichment inputs merged into `attributes.profile`. They contain a summary, evidence-cited sections and facts, strengths, limitations, optional diagram steps, coverage, gaps and an explicit automated review note. Current summaries include `summary_source_ids` and `summary_source_locator`; both are optional for historical releases but must occur together. Current facts include an explicit `status`: `source_checked`, `unreported`, `unextracted`, `unavailable` or `inapplicable`. Coverage `reviewed` describes the explanatory claims only; `limited` records a specific evidence limitation. Neither changes scientific result review status or establishes independent reproduction.

`variant_of`, `family` and `alias_of` describe supported model relationships. `part_of` links benchmark components to suites; `evaluates_task` connects a concrete resource to a task. These edges participate in result navigation only when backed by source-checked association claims. `uses_model` identifies a service or separately evaluated pipeline's dependency and does not assign its result to the base model. Retain exact configuration identity and legacy detail URLs.

Hosted services retain their own operational limits and terms rather than inheriting a downloadable checkpoint’s licence or configuration. Source warnings under `attributes.evidence_concerns` preserve the original transcription status while preventing affected results from supporting automatic comparisons. Every warning has an artifact hash, precise locator and review date.

When a model or benchmark receives reviewed profile content, the original discovery `missing_metadata` map is retained as `historical_missing_metadata`. Current field-level evidence states are in `profile.facts`. This prevents old extraction gaps from contradicting newly reviewed descriptive claims; archived releases remain byte-identical.
