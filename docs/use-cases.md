# Research and clinical use cases

A use case is a decision someone needs to make, such as "which workflow detects copy-number changes accurately?", with the evidence that bears on it. There are 26. Use-case pages show the question, what the user brings and needs, the reviewed evidence, and what is still missing. They never recommend clinical care.

## How use cases are stored

Use cases are records in the store, like models and benchmarks.

| Record | Where | What it holds |
| --- | --- | --- |
| `use_case` | `data/entities/use-cases.jsonl` | The question, intended users, decision, inputs, desired output, setting, exclusions, clinical scope, evidence gaps, collection plan and planned work. Areas and settings are facets. Links `assessed_by` each protocol judged to bear on it. |
| relevance judgement (`claim`) | `data/evidence/claims.jsonl` | One per use case and protocol: subject the use case, `field` `links:assessed_by:<protocol>`, `value` the protocol. Records `relevance` (`direct`, `proxy` or `outside_scope`; scheme `data/vocab/relevance.ttl`), `endpoint`, `rationale`, `constraints`, `limitations`, the sources it rests on (`source_ids`, `citation_locators`), its review, and `pins`. |

A judgement is a decision, not a fact from a source: someone read the protocol and the question and decided how closely one answers the other. The agent that makes it (usually the one extracting the evidence) records its reasoning in the claim with status `needs_review`. A different worker reviews it with `review-evidence`, as for any other claim. In the knowledge graph a judgement is `rb:RelevanceJudgement`, a subclass of SEPIO assertion (`obo:SEPIO_0000001`); `rb:UseCase` and `rb:assessedBy` are rewire terms because no external term matches (see the basis notes in `data/ontology/mapping.json`).

A reviewed judgement lists the evaluations its reviewer checked (`reviewed_evaluations`). The release shows every evaluation on the protocol, minus any the judgement excludes with a reason (`excluded_evaluations`), that passes the usual evidence gates: reviewed evaluation and configuration, at least one reviewed result, clean sources. A new evaluation on a mapped protocol therefore appears without a new judgement; a new or changed result on a reviewed evaluation withholds the judgement until it is re-reviewed. If a reviewed evaluation stops passing the gates, the whole judgement is withheld, so a comparison never silently loses a member. A protocol with more than 500 eligible evaluations is withheld until it is split.

Each use case can also carry a summary claim (`field` `summary`): a short, descriptive account of what the evidence shows, never a recommendation. It is published only once it is reviewed, its sources are clean and its pins match; a draft summary is not published.

## When a judgement is shown

`deriveUseCaseInputs` in `shared/omics/use-cases.ts` turns the records into the use-case artifact (`use-cases.json`) that releases publish and the website reads. A judgement is:

- **draft** while its claim is `needs_review`: recorded, not shown as evidence;
- **active** when its claim is reviewed, its pins match, its sources are clean, the use case links `assessed_by` the protocol and at least one evaluation is eligible;
- **withheld** (`needs_review` in the artifact, with the reason) when any of those fails, or when the claim is `disputed`, a source the use case cites has concerns, or its task is disputed or unreviewed;
- **dropped** when its claim is `excluded` or `superseded`.

**Pins.** A reviewed judgement or summary pins the records it rests on (`judgementPinFields`, `claimPins`): the use case's status, name, description, facets and decision fields (question, decision, inputs, output, exclusions, setting, scope, users); the protocol's status, name, description, facets, sources, links and attributes; the status and artifact hash of the protocol's and the claim's sources; and each reviewed evaluation (status, links, origin, comparison) with its results (status, metric, qualifier, printed and numeric value). If any of these changes, the claim is withheld until it is reviewed again. Adding a judgement, gap or citation to a use case does not withhold its other judgements; its cited sources are checked live instead.

`npm run use-cases:repin -- <review.md>` pins reviewed claims that have no pins yet. After a re-review, name the claims: `npm run use-cases:repin -- <review.md> <claim-id>...`. Only a reviewed change of form that alters no meaning, such as a vocabulary relabel or a relation rename, justifies `--all`. Each pinned claim is recorded in provenance. The release workflow refuses a release that withholds or drops a judgement the previous release served, unless its claim was excluded or superseded (`scripts/release/next.mjs withheld`).

## Content and evidence ownership

- Use cases and their first judgements were curated by Codex and Claude research agents with independent automated cross-review. Recorded actors and methods mean automated review, not human domain review or experimental replication.
- Engineering and release responsibility stays with the repository maintainers through review, CI, release and deployment.
- Human scientific review is unassigned, tracked in [#31](https://github.com/rewire-bio/rewire-database/issues/31).

## Adding or changing a use case

1. Add or edit the `use_case` record through a batch (`npm run records -- add`) or a reviewed change (`npm run records -- change`).
2. For each protocol that bears on it, add the `assessed_by` link and a relevance judgement claim with status `needs_review`. Use `excluded_evaluations` only for evaluations on the protocol that do not apply, each with a reason.
3. A different worker reviews the judgement (`review-evidence`), lists the evaluations it checked in `reviewed_evaluations`, sets it to `source_checked`, and records its pins with `npm run use-cases:repin -- <review.md> <claim-id>...`. Summaries are reviewed and pinned the same way, after the judgements they describe.
4. To withdraw a judgement, set its claim to `excluded` (or `superseded`, with a `supersedes` link from its replacement). Earlier releases keep the evidence they served.

The documentation sources that some use cases cite keep their reviewed bytes in `data/omics/use-cases/sources/`, bound by `data/omics/use-cases/review.json`; releases publish them at `/omics/sources/<sha256>.md`.

The move from the old `inputs.json` file to records is batch `data/omics/use-case-records-20261009/`: all 26 use cases and 100 mappings round-trip to the same artifact, apart from the new presentation fields.

## Initial review boundaries

The MFASS mapping covers the four matched canonical-annotation configurations,
all on the same 8,297 of 8,324 held-out variants. Its 23 assembly-orientation
exclusions and four canonical-transcript-span exclusions remain explicit.
Missing scores are not negative predictions, and the four transcript exclusions
are not established faulty variants. The reporter endpoint is proxy evidence
for wider follow-up decisions, not patient-RNA or pathogenicity validation.
Individual-condition uncertainty is unreported; paired-contrast intervals must
not be assigned to individual conditions. Historical MFASS configurations remain
in their existing protocol groups.

The two AMFR mappings describe separate completed evaluations of 2,972 mixed
single/double variants in a 47-residue construct. They do not become a joint
comparison or establish a winner. The protocols currently have no reviewed
direct task-membership relation, so the mappings omit `task_id`. The planned
single-substitution comparison under #40 remains blocked in `planned_work` and
supplies no evaluation or result. Its resource ceilings are planning limits,
not measured hardware requirements. Neither page supports clinical suitability.

The pinned documentation was obtained through the authenticated GitHub contents
API and compared byte for byte with the pinned Git objects. This is recorded in
source metadata rather than presented as unauthenticated public retrieval.
Original source URLs and SHA-256 digests remain available for audit.
The two reviewed documents also have public copies at
`/omics/sources/<sha256>.md`. Source pages link to these accessible copies and
retain the original pinned URLs in `original_url` and `original_artifact_url`.
They are exact copies, not newly written evidence or republished measurements.

## Release contract

A release with use cases has a `coverage.use_cases` declaration (schema version 1.0, input SHA-256, use-case count, mapping count) and `use-cases.json` in `manifest.files`. The input SHA-256 is the logical digest of the artifact derived from the use-case records and judgements, and it is fixed before the release ID is derived. Old releases with no declaration remain valid and return an empty collection. Declared-but-missing or inconsistent artifacts fail release and import validation.

`coverage.use_case_sources` declares each `use-case-source-<sha256>.md` file and its digest. Archive restoration reconstructs their public aliases and refuses unsafe filenames, changed bytes or alias collisions.

The artifact keeps the shape it had before use cases became records, so the website and the release-pinned API read it unchanged. Each judgement becomes one mapping with the claim's ID; its `evaluation_ids` are the derived list and its `evidence_sha256` is computed at build time. `validateUseCaseArtifact` rebuilds the artifact from the snapshot and refuses any difference. Model backlinks identify the tested configurations and require reviewed relationships; they do not imply that every configuration in a model family applies.

Historical tombstones in archived releases are still checked by `validateUseCaseHistory`.

Do not add patient inputs, private contributor fields, automated clinical recommendations or unreviewed AI-generated judgements as active evidence. Freezing a release is described in [release.md](release.md).
