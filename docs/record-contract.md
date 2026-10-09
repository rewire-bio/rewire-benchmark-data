# Omics catalogue interchange v1

Reviewed JSONL records are the publication source. The release builder writes the catalogue snapshot and versioned JSONL/CSV exports for each release. This is a public-data contract; email addresses, submission tokens, and private correspondence must never be exported.

Each record is an object. Fields marked as concept keys hold the last segment of a concept IRI from a SKOS scheme in `data/vocab/`; the JSON-LD context (`data/ontology/context.jsonld`) expands them to IRIs such as `https://benchmarks.rewire.it/vocab/metric/auprc`. Validation rejects any other value.

- `id`: stable lowercase slug, unique across kinds.
- `kind`: one of `model`, `method`, `configuration`, `pipeline`, `service`, `benchmark`, `task`, `protocol`, `evaluator`, `dataset`, `dataset_subset`, `baseline`, `evaluation`, `result`, `source`, `claim`, `use_case`. The list and the allowed link relations are defined in `shared/omics/entity-kinds.ts`.
- `name`: display name.
- `description`: plain text.
- `status`: `discovered`, `needs_review`, `source_checked`, `reproduced`, `disputed`, `superseded`, or `excluded`. Source-checked is not reproduced.
- `facets`: object mapping facet names to arrays. `areas`, `method_types` and `contexts` hold concept keys from `data/vocab/area.ttl`, `method-type.ttl` and `context.ttl`; `tasks` is free text.
- `source_ids`: IDs of source records supporting this entity.
- `links`: array of `{ "relation": "...", "target_id": "..." }`. Each relation has one meaning and a fixed set of record kinds it may link from and to, listed in `shared/omics/relations.ts`:
  - evaluation: `system` (what was evaluated: a configuration, model, method, pipeline or service), `assessment` (the task, protocol or benchmark) and `data` (the dataset or subset), exactly one each; optional `original_evaluation`;
  - result: `evaluation`; claim: `subject`;
  - baseline: `implemented_by`, `measured_in`, `uses_data`, `applicable_to`;
  - task and protocol: `part_of`, `parent`, `evaluates_task`, `uses_data`; dataset subset: `used_in`, `same_data_as`;
  - model and configuration identity: `family`, `variant_of` (model to model), `configuration_of` (configuration to what it configures), `alias_of`, `uses_model`;
  - any record: `supersedes`, `source`.

  References resolve within a release. Releases written before October 2026 used other names (`model`, `benchmark`, `dataset` and typed names on evaluations, and the same names with other meanings on baselines and subsets); readers translate them with `normalizeRecords`.
- `attributes`: kind-specific JSON object. Every key is declared for its kind, with a type, in `shared/omics/attribute-registry.ts`; `npm run records -- check` and `records -- add` reject undeclared keys, badly typed values and nulls. A value that is not known is absent, and `missing_metadata.<field>` gives `{reason, note?}`, where `reason` is a concept from `data/vocab/missingness.ttl` (`unreported`, `unextracted`, `unavailable`, `inapplicable`, `conflicting`). A field never has both a value and a missing reason. Never invent values. Batches written in older shapes are converted with `npm run attributes:migrate -- --batch <batch.jsonl>` before review.

A `source` has attributes `url`, `version`, `retrieved_at`, optional `doi`, `publication_status`, `artifact_sha256`, `source_locator`, `licence` and `review`.
A `model` has `entity_level` (`family`, `checkpoint`, `method`, `service`), `version`, `reported_name`, `missing_metadata`, and optional architecture/training/input/output/licence/access metadata. Do not collapse unidentified versions into a concrete checkpoint.
A `benchmark` has `entity_level` (`suite`, `protocol`, `task`, `challenge`, `evaluator`), `version`, `task`, `scope_note`, `missing_metadata`.
A `dataset` has `version`, `split`, `missing_metadata`, optional assay/context/accession metadata.
A `baseline` has `baseline_type`, `applicability` (`proposed` or `source_supported`), `requirements`, `missing_metadata`.
An `evaluation` has `origin` (`author_reported`, `independent_paper`, `paper_compilation`, `rewire_run`, `unreported`), `protocol`, `version`, `comparison` object, `missing_metadata`, links `system`, `assessment` and `data`, and an optional `original_evaluation` link. Comparison fields: `protocol_id`, `dataset_version`, `split`, `population`, `inputs`, `adaptation`, `metric_implementation`, `aggregation`, `budget`; unknown fields are null and block automatic comparison.
A `result` links to exactly one evaluation. Attributes: `printed_value` (string), `numeric_value` (string decimal or null), `metric` (concept key, `data/vocab/metric.ttl`), optional `metric_qualifier` (what distinguishes results that share a metric concept: class, setting, scope, cutoff or aggregation), `metric_direction` (`higher`, `lower`, `unknown`), `unit` (concept key, `data/vocab/unit.ttl`), optional `unit_detail`, `uncertainty` (absent with a missing reason, or an object whose `type` is `standard_deviation`, `standard_error`, `confidence_interval`, `credible_interval` or `unresolved_spread`, with decimal-string `value`, `lower`, `upper`, `half_width` or `center`, a `level` between 0 and 1, and optional `method`, `n`, `resamples`, `printed`, `scope`, `unit`, `source_column`, `note`; `shared/omics/attributes.ts` has the full rules), optional `coverage` (`{scored, eligible, unit, note}` integers where known), `source_locator`, `review` (object with `method` (list of concept keys, `review-method.ttl`), optional `method_note`, `reviewer` (list of concept keys, `agent.ttl`), optional `reviewer_note`, `date` (a date), `reviewed_at` (a date-time), `note`, `scope`), `missing_metadata`, optional `legacy_id`. Comparisons require the same metric, qualifier, unit and direction. Retain original paper IDs and result IDs for migration. Reviewed results need a precise locator and source.
A `claim` links to a `subject` and has `field`, `value`, `source_locator`, `review` and supporting source IDs. A checked score does not mark all metadata as checked.

Snapshot JSON: `{ "schema_version": "1.0", "release_id": "...", "released_at": "UTC ISO date", "records": [...], "coverage": {...} }`. Manifest: schema/release/time, record counts, input digests, file hashes and changelog. All records sorted by ID; release building is deterministic given the records and explicit timestamp. Excluded records remain in the archive but are absent from public catalogue pages.

## Biological extensions

`attributes.extensions` supports validated `genomics`, `protein`, `cellular`, `molecular_measurement`, `microbial` and `mechanistic` blocks. The contract is in `scripts/omics/extensions.ts`. Coordinates carry their assembly, convention, strand and window orientation; variant offsets are zero-based within the window. Protein identity thresholds are fractions, with MSA/template provenance separate. Cellular doses and times require units. Molecular measurements carry identifier namespace, platform, preprocessing and units; microbial references carry taxonomy/database versions. Mechanistic evaluations carry solver, constraints and conditions. Missing blocks are unextracted, not evidence that these factors are inapplicable; null records an explicitly unknown field. Extend the schema through a reviewed change when a new modality requires more fields.

## Explanatory profiles and supported associations

Model and benchmark explanations are validated enrichment inputs merged into `attributes.profile`. They contain a summary, evidence-cited sections and facts, strengths, limitations, optional diagram steps, coverage, gaps and an explicit automated review note. Current summaries include `summary_source_ids` and `summary_source_locator`; both are optional for historical releases but must occur together. Current facts include an explicit `status`: `source_checked`, `unreported`, `unextracted`, `unavailable` or `inapplicable`. Coverage `reviewed` describes the explanatory claims only; `limited` records a specific evidence limitation. Neither changes scientific result review status or establishes independent reproduction.

`variant_of`, `configuration_of`, `family` and `alias_of` describe supported model relationships. `part_of` links benchmark components to suites; `evaluates_task` connects a concrete resource to a task. These edges participate in result navigation only when backed by source-checked association claims. `uses_model` identifies a service or separately evaluated pipeline's dependency and does not assign its result to the base model. Retain exact configuration identity and legacy detail URLs.

Hosted services retain their own operational limits and terms rather than inheriting a downloadable checkpoint’s licence or configuration. Source warnings under `attributes.evidence_concerns` preserve the original transcription status while preventing affected results from supporting automatic comparisons. Every warning has an artifact hash, precise locator and review date.

Current field-level evidence states for profiled models and benchmarks are in `profile.facts`. Discovery-era missing maps (`historical_missing_metadata`) and other extraction scaffolding (`legacy_row`, `legacy_paper`, `acquisition_candidate_id`, `local_cache_path`, `historical_entity_links`, `legacy_import_source_id`) are kept per record in `data/provenance/moved-attributes.jsonl`, not on the record. Archived releases remain byte-identical; readers convert them on load with `shared/omics/current.ts`.
