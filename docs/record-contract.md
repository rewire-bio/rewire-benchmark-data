# Omics catalogue interchange v1

Reviewed JSONL records are the publication source. The release builder writes the catalogue snapshot and versioned JSONL/CSV exports for each release. This is a public-data contract; email addresses, submission tokens, and private correspondence must never be exported.

Each record is an object. Fields marked as concept keys hold the last segment of a concept IRI from a SKOS scheme in `data/vocab/`; the JSON-LD context (`data/ontology/context.jsonld`) expands them to IRIs such as `https://benchmarks.rewire.it/vocab/metric/auprc`. Validation rejects any other value.

- `id`: stable lowercase slug, unique across kinds.
- `kind`: one of `model`, `method`, `configuration`, `pipeline`, `service`, `benchmark`, `task`, `protocol`, `evaluator`, `dataset`, `dataset_subset`, `baseline`, `evaluation`, `result`, `source`, `claim`, `use_case`. The list and the allowed link relations are defined in `shared/omics/entity-kinds.ts`.
- `name`: display name.
- `description`: plain text. For a `model`, `method`, `pipeline`, `service` or `configuration`, one sentence saying what it does (a configuration may say what it is: what it configures and with which settings). Where the record was reported, run or quoted, and what was not inferred about its identity, go in `attributes.provenance_note`, not in the description. `npm run records -- check` and `records -- add` reject placeholders ("Identity as reported in this paper"), provenance ("as run in the cited comparison", "quoted in Table S11", "(Author et al. 2025 Table 3)") and a description shared with a differently named model, method, pipeline or service; the rules are in `shared/omics/descriptions.ts`, and `npm run records -- descriptions` lists any record that fails them.
- `status`: `discovered`, `needs_review`, `source_checked`, `reproduced`, `disputed`, `superseded`, or `excluded`. Source-checked is not reproduced.
- `facets`: object mapping facet names to arrays. `areas`, `method_types` and `contexts` hold concept keys from `data/vocab/area.ttl`, `method-type.ttl` and `context.ttl`; `tasks` is free text.
- `source_ids`: IDs of source records supporting this entity.
- `links`: array of `{ "relation": "...", "target_id": "..." }`. Each relation has one meaning and a fixed set of record kinds it may link from and to, listed in `shared/omics/relations.ts`:
  - evaluation: `system` (what was evaluated: a configuration, model, method, pipeline or service), `assessment` (the task, protocol or benchmark) and `data` (the dataset or subset), exactly one each; optional `original_evaluation`;
  - result: `evaluation`; claim: `subject`;
  - baseline: `implemented_by`, `measured_in`, `uses_data`, `applicable_to`;
  - task and protocol: `part_of`, `parent`, `evaluates_task`, `uses_data`; dataset subset: `used_in`, `same_data_as`;
  - model and configuration identity: `family`, `variant_of` (model to model), `configuration_of` (configuration to what it configures), `alias_of`, `uses_model`;
  - source: `companion_of` (a repository, leaderboard, supplement or another version of a paper, to that paper's source);
  - any record: `supersedes`, `source`.

  References resolve within a release. Releases written before October 2026 used other names (`model`, `benchmark`, `dataset` and typed names on evaluations, and the same names with other meanings on baselines and subsets); readers translate them with `normalizeRecords`.
- `attributes`: kind-specific JSON object. Every key is declared for its kind, with a type, in `shared/omics/attribute-registry.ts`; `npm run records -- check` and `records -- add` reject undeclared keys, badly typed values and nulls. A value that is not known is absent, and `missing_metadata.<field>` gives `{reason, note?}`, where `reason` is a concept from `data/vocab/missingness.ttl` (`unreported`, `unextracted`, `unavailable`, `inapplicable`, `conflicting`). A field never has both a value and a missing reason. Never invent values. Batches written in older shapes are converted with `npm run attributes:migrate -- --batch <batch.jsonl>` before review.

A `source` has attributes `url`, `version`, `retrieved_at`, optional `doi`, `publication_status`, `artifact_sha256`, `source_locator`, `licence` and `review`.
A `model` has `entity_level` (`family`, `checkpoint`, `method`, `service`), `version`, `reported_name`, `missing_metadata`, and optional architecture/training/input/output/licence/access metadata. Do not collapse unidentified versions into a concrete checkpoint.
A `benchmark` has `entity_level` (`suite`, `protocol`, `task`, `challenge`, `evaluator`), `version`, `task`, `scope_note`, `missing_metadata`.
A `dataset` has `version`, `split`, `missing_metadata`, optional assay/context/accession metadata.
A `baseline` has `baseline_type`, `applicability` (`proposed` or `source_supported`), `requirements`, `missing_metadata`.
An `evaluation` has `origin` (`author_reported`, `independent_paper`, `paper_compilation`, `rewire_run`, `unreported`), `protocol`, `version`, `comparison` object, `missing_metadata`, links `system`, `assessment` and `data`, and an optional `original_evaluation` link. Comparison fields: `protocol_id`, `dataset_version`, `split`, `population`, `inputs`, `adaptation`, `metric_implementation`, `aggregation`, `budget`; unknown fields are null and block automatic comparison.
A `result` links to exactly one evaluation. Attributes: `printed_value` (string), `numeric_value` (string decimal or null), `metric` (concept key, `data/vocab/metric.ttl`), optional `metric_qualifier` (what distinguishes results that share a metric concept: class, setting, scope, cutoff or aggregation), `metric_direction` (`higher`, `lower`, `unknown`), `unit` (concept key, `data/vocab/unit.ttl`), optional `unit_detail`, optional `derivation` (below), `uncertainty` (absent with a missing reason, or an object whose `type` is `standard_deviation`, `standard_error`, `confidence_interval`, `credible_interval` or `unresolved_spread`, with decimal-string `value`, `lower`, `upper`, `half_width` or `center`, a `level` between 0 and 1, and optional `method`, `n`, `resamples`, `printed`, `scope`, `unit`, `source_column`, `note`; `shared/omics/attributes.ts` has the full rules), optional `coverage` (`{scored, eligible, unit, note}` integers where known), `source_locator`, `review` (object with `method` (list of concept keys, `review-method.ttl`), optional `method_note`, `reviewer` (list of concept keys, `agent.ttl`), optional `reviewer_note`, `date` (a date), `reviewed_at` (a date-time), `note`, `scope`), `missing_metadata`, optional `legacy_id`. Comparisons require the same metric, qualifier, unit and direction. Retain original paper IDs and result IDs for migration. Reviewed results need a precise locator and source.

`printed_value` is the value exactly as the source prints it, unless the result has a `derivation`. A `derivation` records a value the source does not print but that Rewire computed from the source's own supplementary data (a Source Data workbook, a supplementary table of per-item rows) with an aggregation the source states. Its fields:

- `method`: concept key from `data/vocab/derivation-method.ttl` (`computed-from-source-data`).
- `inputs`: one or more `{source_id, artifact_sha256, locator, row_filter, row_count}`. Each `source_id` is a `source` record for one supplementary file, whose `artifact_sha256` must equal the input's. `locator` names the file, sheet and panel; `row_filter` says which rows were read; `row_count` is how many.
- `aggregation`: the source's own wording for how values are aggregated, quoted exactly, with `aggregation_source_id` and `aggregation_locator` saying where it is printed.
- `script` and `script_sha256`: the repository path of the deterministic script that computes the value, and the SHA-256 of its bytes.
- `precision`: how the computed value was rounded, for example "rounded half to even to 3 decimal places".
- optional `note`.

With a `derivation`, `printed_value` holds the computed value formatted at the stated precision and `numeric_value` is required. `source_locator` points at the input rows. `npm run records -- add` and `records -- check` reject a derivation whose script is missing or does not match its hash, whose input hash differs from its source record, whose input and aggregation sources have different DOIs (only the source's own data counts), with no stated aggregation, or on an evaluation with origin `rewire_run` or `paper_compilation`. The evaluation keeps the origin of whoever ran the models (usually `author_reported`); the derivation marks the number as computed by Rewire. Derived results are compared under the same checks as printed ones: same metric, qualifier, unit and direction, and the same evaluation comparison fields, including `aggregation`.
A `claim` links to a `subject` and has `field`, `value`, `source_locator`, `review` and supporting source IDs. A checked score does not mark all metadata as checked.

Snapshot JSON: `{ "schema_version": "1.0", "release_id": "...", "released_at": "UTC ISO date", "records": [...], "coverage": {...} }`. Manifest: schema/release/time, record counts, input digests, file hashes and changelog. All records sorted by ID; release building is deterministic given the records and explicit timestamp. Excluded records remain in the archive but are absent from public catalogue pages.

## Locators

`source_locator` is a free-text string on every result and claim. `shared/omics/locator.ts` reads one as structure, so a locator can be checked rather than only read. The grammar, applied to each segment after splitting on `;` and on commas outside quotes and brackets:

    locator   := anchor+ address? selector* qualifier*
    anchor    := table | figure | sheet | file | container
    address   := sheet_cell | cell_range | line | row_number | xml_cell | json_path
               | quote | sentence | paragraph
    selector  := key ('=' | ':' | ' ') value, the value quoted, bracketed or bare
    qualifier := page | layer | commit | parenthetical note

An anchor names the object the value is printed in. An address points straight at a place in it. A selector is a key and a value, so `row 'Bacformer'`, `column 'Binary AUPRC'`, `tool cn.MOPS` and `model='scGPT'` all read the same way. A qualifier narrows the reading without locating anything: a page, a text layer, a commit. Text no token consumes is reported as residue, never dropped, and residue is why a locator is not counted as addressed.

How far a locator pins a value down:

| bucket | meaning |
| --- | --- |
| full | an anchor or address, something naming the row, something naming the column, and no residue; or a cell address with labels that check it; or a text span |
| partial | addressed in one direction only, or a bare cell address with nothing to check it |
| residue | part of the string was not read into a field |
| unanchored | no anchor and no address |

`npm run locator -- coverage` parses every stored result locator and writes `maintenance/reports/locator-coverage-<date>.tsv`, broken down by class. Measured on 2026-11-17 over 52,278 locators: 39,416 full (75.4%), 3,212 partial, 8,192 carrying residue, 1,458 unanchored. The v1 regex at `scripts/omics/batch.py:30-31`, which is still what `check-values` uses, parses 20,540 of the same locators (39.3%). It is ported into `shared/omics/locator.ts` for comparison only, and `tests/locator-grammar.test.ts` checks the port against the 14 `data/omics/*/value-check.tsv` files row by row: the rows it rejects are exactly the rows `check-values` recorded as `locator_not_parsed`.

`renderLocator` writes a parsed locator back out in the canonical form `anchors, address, selectors (qualifiers)`. It renders from the typed fields, not from the text they were read from, so it reproduces the original string only where the original was already canonical: 36.6% of the addressed locators today, with 95.8% parsing back to the same structure. That gap is the measure of what inverting the contract would cost, where the structure is authored and the string is rendered from it.

A locator carries no span yet. The span type is declared now because the offset basis is expensive to change later: `start` and `end` count Unicode code points from 0, as `oa:TextPositionSelector` does; `byte_start` and `byte_end` count UTF-8 bytes into the same text layer, as `oa:DataPositionSelector` does; `exact`, with optional `prefix` and `suffix`, is `oa:TextQuoteSelector` and relocates the span when a layer is rebuilt. `layer_sha256` names the layer the offsets index, and that layer is never Unicode-normalised. JavaScript string indices are UTF-16 code units and are neither basis.

## Biological extensions

`attributes.extensions` supports validated `genomics`, `protein`, `cellular`, `molecular_measurement`, `microbial` and `mechanistic` blocks. The contract is in `scripts/omics/extensions.ts`. Coordinates carry their assembly, convention, strand and window orientation; variant offsets are zero-based within the window. Protein identity thresholds are fractions, with MSA/template provenance separate. Cellular doses and times require units. Molecular measurements carry identifier namespace, platform, preprocessing and units; microbial references carry taxonomy/database versions. Mechanistic evaluations carry solver, constraints and conditions. Missing blocks are unextracted, not evidence that these factors are inapplicable; null records an explicitly unknown field. Extend the schema through a reviewed change when a new modality requires more fields.

## Explanatory profiles and supported associations

Model and benchmark explanations are validated enrichment inputs merged into `attributes.profile`. They contain a summary, evidence-cited sections and facts, strengths, limitations, optional diagram steps, coverage, gaps and an explicit automated review note. Current summaries include `summary_source_ids` and `summary_source_locator`; both are optional for historical releases but must occur together. Current facts include an explicit `status`: `source_checked`, `unreported`, `unextracted`, `unavailable` or `inapplicable`. Coverage `reviewed` describes the explanatory claims only; `limited` records a specific evidence limitation. Neither changes scientific result review status or establishes independent reproduction.

`variant_of`, `configuration_of`, `family` and `alias_of` describe supported model relationships. `part_of` links benchmark components to suites; `evaluates_task` connects a concrete resource to a task. These edges participate in result navigation only when backed by source-checked association claims. `uses_model` identifies a service or separately evaluated pipeline's dependency and does not assign its result to the base model. Retain exact configuration identity and legacy detail URLs.

Hosted services retain their own operational limits and terms rather than inheriting a downloadable checkpoint’s licence or configuration. Source warnings under `attributes.evidence_concerns` preserve the original transcription status while preventing affected results from supporting automatic comparisons. Every warning has an artifact hash, precise locator and review date. An entry with `applies_to` covers only the records it lists and the results that rest on them (a result's evaluation, configuration, dataset, the protocol, task or benchmark it was tested on, and what that is directly part of), from any source; an entry without it covers everything the source supports. `npm run records -- check` rejects an `applies_to` that names a missing record or a kind outside that list. Result-level `source_warnings` and `source_discrepancy` are notes for readers and do not block.

Current field-level evidence states for profiled models and benchmarks are in `profile.facts`. Discovery-era missing maps (`historical_missing_metadata`) and other extraction scaffolding (`legacy_row`, `legacy_paper`, `acquisition_candidate_id`, `local_cache_path`, `historical_entity_links`, `legacy_import_source_id`) are kept per record in `data/provenance/moved-attributes.jsonl`, not on the record. Archived releases remain byte-identical; readers convert them on load with `shared/omics/current.ts`.
