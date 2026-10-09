# Use cases as records: independent review, 2026-10-09

Reviewer: a separate Claude review agent that did not write the migration. No human review is claimed.

Scope: branch `claude/use-case-records` at `8a81eb7` (two WIP commits on `origin/main` `1ebc8b5`). The review covers:

- batch `data/omics/use-case-records-20261009/` (127 records: 26 `use_case` records, 100 relevance judgement claims, 1 draft summary claim) and its `presentation.json`;
- `deriveUseCaseInputs` and `judgementPins` in `shared/omics/use-cases.ts`;
- `scripts/omics/migrate-use-cases.ts`, `scripts/omics/repin-use-cases.ts` and `docs/use-cases.md`;
- the ontology additions.

The baseline is `data/omics/use-cases/inputs.json` and `sources.json` on `origin/main`. All checks used scripts written for this review. The author's round-trip claim was not relied on.

## Outcome

The migration is faithful. The records hold every field of the old inputs, and the derived inputs equal the old inputs. The presentation values are correct. The ontology additions are accurate apart from some wording.

Two problems need a decision before merge:

- The new gate is weaker than the old one. Several changes that used to withhold an active mapping now leave it active (findings 1 and 2).
- The draft CNV summary contains one false statement and leaves out a material caveat (finding 3).

## Checks and results

1. **Round trip.** I compared `deriveUseCaseInputs(loadRecords())` field by field with `inputs.json` from `origin/main`. I ignored the new `presentation` field (9 mappings) and `summary` field (1 use case). 26 of 26 use cases and 100 of 100 mappings are identical, including `evidence_sha256`, `lifecycle`, `reason` and review. The only other difference is the order of `evaluation_ids` in 37 mappings. Sorted, the lists are equal.
2. **Record fidelity.**
   - Every use-case field is present and equal to the old value: title, area, contexts, search terms, intended users, decision, inputs, output, setting, exclusions, clinical scope, evidence gaps, collection plan and planned work.
   - Every mapping field is present and equal: relevance, endpoint, rationale, constraints, limitations, revision, reason and task_id.
   - Citations equal `citation_locators`, and `source_ids` equal the set of cited sources.
   - Review method, time and note match. `reviewer_note` equals the old actor text verbatim in all 126 migrated records.
   - Each use case's `assessed_by` links equal the set of its mapped protocols.
   - The batch equals the records in the store.
   - In all 100 judgements, `excluded_evaluations` lists exactly the protocol evaluations that the old mapping left out. There are three on `use-case-mapping-20260930-339-25925e279972`, two on `use-case-mapping-20260930-349-1af09c2e0e0f`, and none elsewhere.
   - The four documentation source records from the retired `sources.json` are in the store with the same content. They are in the declared-attribute shape, so `review_scope` has moved into `review.scope`.
3. **Reviewer keys.** There are eight distinct actor strings, and every named agent is captured. "Codex ..." gives `codex`. "Claude Sonnet ..." gives `claude-sonnet`. "Claude (Opus 5.5) ..." gives `claude`. A string that names two agents gives both keys. See finding 11.
4. **Lifecycle.** The 97 active mappings are `source_checked` claims and the 3 drafts are `needs_review` claims. The derived output has 97 active and 3 draft mappings, with the same three draft IDs as before.
5. **Presentation.** All nine judgements carry exactly the values in `presentation.json`, and no other claim has grouping fields.
   - The five Behera deletion protocols are DRAGEN Table S4 rows 6 to 10. Their bins are `[1000,5000)`, `[5,000-10,000)`, `[10,000-20,0000)`, `[20,000-50,000)` and `>50,000`. The third label is a typo in the source, recorded in `scope_note`.
   - The bins match the labels "1 to 5 kb" to "Over 50 kb" and the order 1 to 5. Each bin has the same three configurations.
   - Each headline metric exists among its protocol's results: f1-score for Behera and Nardone, recall for Gabrielaite and the De La Vega HG002 protocol, and precision for the De La Vega Coriell panel, which reports precision only.
6. **Gate semantics.** I compared `deriveUseCaseInputs` and `evaluationBlocker` with `validateMapping`. I then probed the behaviour by editing an in-memory copy of the store and running both `deriveUseCaseInputs` and `buildUseCaseArtifact`. Per evaluation, `evaluationBlocker` applies the same checks as `validateMapping` with active checks. Two new checks are stricter than before: the "no eligible evaluation" blocker, and the clean-source check on every cited source. The weaker points are findings 1, 2, 4, 5 and 6.
7. **Ontology.** These all agree with each other:
   - the classes `rb:UseCase` and `rb:RelevanceJudgement` (a subclass of `rb:Claim` and `obo:SEPIO_0000001`), and the property `rb:assessedBy`;
   - the `use_case` class, the `assessed_by` relation and the `relevance` field and scheme in `mapping.json`;
   - the `research` concept in `context.ttl`, and the new terms in `context.jsonld`;
   - `PROTECTED` in `build.py`, the type assignment in `export.ts`, and the new presentation attribute declarations.

   I re-downloaded `http://purl.obolibrary.org/obo/sepio/releases/2023-06-13/sepio.owl`. Its SHA-256 is `ae9161620d677fe16857e0704006b7d07086e2ac75688261be901b0f9c3db488`, equal to `source_sha256`. Re-running `scripts/kg/extract_terms.py` on it reproduces `sepio-subset.nt` byte for byte.

   SEPIO_0000001 is defined as "a statement made by a particular agent on a particular occasion that a particular proposition is true, based on the evaluation of one or more lines of evidence". A relevance judgement is an agent's dated statement, made after reading the sources, that a protocol bears on a use case to a given degree. The subclass claim holds.

   I checked the basis notes on external terms against OLS and schema.org. IAO_0000005 and IAO_0000104 are directive information entities. NCIT C81930 "Use Case" describes steps of interaction between a user and a system. schema:Question is a subclass of schema:Comment. See finding 9.
8. **Commands.**
   - `npm run records -- check`: 29,444 records match their provenance (exit 0).
   - `npm run typecheck`: exit 0.
   - `npx vitest run tests/use-case-records.test.ts`: 8 tests pass in 4.7 s.
   - `npm run test:kg`: 24 tests OK.

## Summary text check

I checked `use-case-summary-cnv-detection-characterisation` against the stored results for Behera Table S4 (rows 6 to 10) and Gabrielaite Table S2 (the NA12878 rows).

| Statement | Stored values | Verdict |
| --- | --- | --- |
| DRAGEN 4.2 CNV+SV found 87 to 100% of deletions in every bin | recall 0.873, 0.933, 0.888, 0.909, 1 | Supported |
| precision 0.99 to 1.00 | 0.986, 1, 1, 1, 1 | Supported |
| CNVnator matched it above 10 kb | F1 0.976, 0.949, 0.99 against 0.941, 0.952, 1 | Supported |
| CNVnator missed half or more of the deletions under 10 kb | recall 0.264 (1 to 5 kb), 0.505 (5 to 10 kb) | Not supported for 5 to 10 kb: it found 50.5% and missed 49.5% |
| LUMPY, DELLY, Manta recovered about 90% | recall 0.941, 0.904, 0.875 | Supported |
| only 20 to 33% of their calls were correct | precision 0.31, 0.199, 0.326 | Supported (19.9% rounds to 20%) |
| depth-only callers recovered 11 to 43% | CNVnator 0.434, GATK gCNV 0.232, cn.MOPS 0.170, Control-FREEC 0.107, CLC 0.012 | Holds only if CLC is left out. The records do not classify callers by signal type, so this grouping is not backed by any record |

## Findings

The probes below use `use-case-map-gears-norman-table6-mse` unless another record is named. "Old" means `origin/main`. There, `evidence_sha256` was fixed at review time and covered every dependency record in full, so any change to a dependency withheld the mapping.

1. **High. The evaluation set is live, so a reviewed comparison can lose members while the judgement stays active** (`shared/omics/use-cases.ts`, `deriveUseCaseInputs`, the `candidates` and `eligible` lists).
   - If one of the four evaluations is marked `disputed`, or its configuration is disputed, the mapping stays active with three evaluations.
   - The rationale names the complete comparison ("includes a no-change control, CPA, CPA with knowledge-graph features and GEARS"). Dropping a member changes what the published mapping supports.
   - A changed result value also leaves the mapping active.
   - Old: withheld in each case.

   Adding new evaluations without review is documented and tested as intended. Silent removal is not documented. Suggested fix: record the reviewed evaluation set, or pin it, and withhold the judgement when a previously included evaluation drops out. Additions can stay as designed.
2. **High. The pin set misses fields that carry meaning** (`judgementPinFields`, `judgementPins`). Each of these changes leaves the judgement active:
   - a change to the protocol's `description` or `name`;
   - the use case's `facets.contexts` changing from `research` to `clinical_research`;
   - a change to the use case's `setting`;
   - a protocol link relation changing from `part_of` to `supersedes`;
   - a change to the `artifact_sha256` of a cited source that is not a protocol source.

   Of the 98 mapped protocols, 23 have neither `attributes.protocol` nor `attributes.version`. Their definition is in `name` and `description`, so their pin covers only status and link targets.

   These fields are not pinned:
   - On protocols: `metric`, `metric_direction` (15 protocols carry these), `dataset`, `task`, `comparison_panels` and facets.
   - On use cases: name, description, setting, clinical_scope, intended_users and contexts.
   - Sources: 12 of 100 judgements cite a source that is not pinned, and 16 use cases cite a source that none of their judgements pins.

   Old: withheld in every case.

   Suggested fix:
   - On protocols, pin name, description, facets, and every attribute except review and locator fields.
   - On use cases, pin name, description, facets and all decision attributes.
   - Pin every source in `claim.source_ids` and in the use case's `source_ids`.
   - Leaving relation names out of the pin is reasonable for renames. Pinning `(relation, target)` pairs after relation names are normalised would keep the #50 behaviour and still catch a change of relation.
3. **High for the summary, which is still a draft. The CNV summary has one false statement and omits the truth-set bias** (`data/omics/use-case-records-20261009/presentation.json`, `summaries`).
   - "Missed half or more of the deletions under 10 kb" is false for 5 to 10 kb, where recall is 0.505.
   - "Depth-only callers recovered 11 to 43%" leaves out CLC Genomics Workbench (1.2%), and no record classifies callers by signal type.
   - The NA12878 sentence favours LUMPY, DELLY and Manta. The protocol's own limitation says Manta and CNVnator were used to build the NA12878 truth set, which can favour them. The summary does not say so.
   - "No independent evidence here covers duplications" also needs checking. The Gabrielaite NA12878 truth set is described as known CNVs, and the protocol notes that the formula ignores dosage direction.

   Fix the text before anyone reviews it to `source_checked`.
4. **Medium. A draft summary is published and is not gated.**
   - `deriveUseCaseInputs` emits the `needs_review` summary into `use-cases.json` with `status: "draft"`. Unreviewed numerical prose therefore ships in the release unless the website hides drafts.
   - Once the summary is `source_checked`, nothing withholds it when its sources gain concerns or the results it quotes change. It has no pins and no source check.

   Either drop drafts from the artifact, or confirm that the site does not show them. Gate a reviewed summary the same way as a judgement.
5. **Medium. Some gate failures that used to withhold now stop the release** (`deriveUseCaseInputs`, the task check; `validateMapping`; `validateEntries`).
   - If `catalog-task-mfass-splice` is disputed, `deriveUseCaseInputs` keeps `use-case-mapping-splicing-mfass-matched-v1` active. `buildUseCaseArtifact` then throws "Active applicability cannot target an inactive task".
   - If a use case's own cited source gains an evidence concern, `validateEntries` throws for that use case's other active mappings.
   - Old: those mappings were withheld.

   This fails closed, but it blocks every release until someone fixes it. Suggested fix: check task status and the use case's cited sources in `deriveUseCaseInputs`, and withhold instead of throwing.
6. **Medium. `use-cases:repin` re-pins every reviewed judgement that no longer matches** (`scripts/omics/repin-use-cases.ts`). Step 3 of `docs/use-cases.md` tells reviewers to run it to record pins for a newly reviewed judgement. A run at that point would also re-pin any judgement that was withheld for a real change, and re-activate it without review. Suggested fix: take explicit claim IDs, or re-pin only claims that have no pins.
7. **Medium. Withdrawal no longer leaves a tombstone, and the release guard does not see it** (`deriveUseCaseInputs`, the `excluded`/`superseded`/`disputed` skip; `scripts/release/next.mjs withheld`).
   - A claim set to `excluded`, `superseded` or `disputed` disappears from the artifact. The old contract kept a `withdrawn` tombstone with `prior_release_id`.
   - `next.mjs withheld` checks only for `needs_review`, so a served mapping that disappears passes.
   - `deriveUseCaseInputs` throws while the use case still links `assessed_by` the protocol. Step 4 of `docs/use-cases.md` does not mention this, so a reviewer who marks a judgement `disputed` breaks the build.

   No tombstone exists today, so the current data is not affected.
8. **Low. Evaluation lists are silently truncated at 100** (`.slice(0, 100)` in `deriveUseCaseInputs`). `use-case-mapping-20260930-337-fa51fe46268a` already has 97 evaluations. Because additions are automatic, four more evaluations on `uc20260930-proteingym-amfr-protocol` would drop IDs without notice. Throw or withhold instead.
9. **Low. Ontology wording.**
   - (a) `rb:assessedBy` in `rb.ttl`, and its basis in `mapping.json`, say the link holds only when a reviewed judgement backs it. The three draft judgements' links are asserted in `use-case-cnv-detection-characterisation` and will be exported.
   - (b) `rb:RelevanceJudgement` calls itself "a claim that a protocol's evaluations are evidence for a use case". That does not fit an `outside_scope` judgement.
   - (c) It says "other claims are study findings". About 1,170 claims are curator assertions about links (`links:part_of`, `links:family` and others), not study findings.
   - (d) The basis says SEPIO has_evidence starts from an assertion. Its domain is proposition or assertion.

   None of these affects the subclass claim.
10. **Low. `not_assessed` is allowed by the mapping schema but missing from `data/vocab/relevance.ttl`.** `docs/use-cases.md` lists only three values. Pick one set and make the schema and the vocabulary agree.
11. **Low. `reviewer` lists workers as well as reviewers.** In 29 records the actor text names a worker and a separate reviewer, for example "Claude Sonnet AMP-integration worker ... independently reviewed by Codex". Both become reviewer keys. Unnamed reviewers ("independent worker cross-review", "root integration review") are not represented. `reviewer_note` keeps the full text, so no information is lost.
12. **Low. The batch README overstates the round trip.** It says the 100 mappings are identical in every field. They now also carry `presentation`, and one use case carries `summary`. Say "apart from the new presentation and summary fields".

## Must change before merge

- Findings 1 and 2: fix them, or record an explicit maintainer decision to accept them, with the doc and tests stating what no longer withholds a judgement.
- Finding 3: correct the summary text.
- Finding 4: decide whether draft summaries ship.
- Findings 5 and 6 are small fixes and should go in with this change. The rest can follow.

## Re-review of the fixes, commit df7e245

Same reviewer: a separate Claude review agent that did not write the fixes. No human review is claimed. All checks were rerun with this review's own scripts against `origin/main` `1ebc8b5`.

### Verdict

The fixes hold. Findings 1 to 10 and 12 are resolved. Finding 11 is unchanged by decision; `reviewer_note` keeps the full text. One gap from finding 2 remains, recorded below as a new low finding. It does not block merge. The corrected CNV summary is supported by the sources, and I have marked it reviewed and pinned it.

### Checks and results

- **Round trip.** 26 of 26 use cases and 100 of 100 mappings match `origin/main` `inputs.json`, ignoring `presentation` (9 CNV judgements) and the order of `evaluation_ids` (37 mappings). The derived output has 97 active and 3 draft mappings. The summary no longer appears while it is a draft.
- **Record fidelity.** The earlier field checks pass unchanged. In all 100 judgements, `reviewed_evaluations` equals the old mapping's `evaluation_ids`. All 97 reviewed judgements carry pins, and the 3 drafts carry none.
- **Gate probes**, on an in-memory copy of the store, running both `deriveUseCaseInputs` and `buildUseCaseArtifact`. Unless another record is named, the target is `use-case-map-gears-norman-table6-mse`.
  - These changes now withhold the judgement:
    - a disputed evaluation or configuration;
    - a changed result value;
    - a new result on a reviewed evaluation;
    - a change to the protocol's description;
    - a protocol relation changing from `part_of` to `supersedes`;
    - a change to the use case's contexts or setting;
    - a changed artifact hash on a cited source that is not a protocol source;
    - an evidence concern on a source the use case cites;
    - a disputed task (on `use-case-mapping-splicing-mfass-matched-v1`);
    - a disputed judgement.
  - None of these probes makes the build throw any more.
  - A new evaluation on the protocol is added and the judgement stays active, as designed.
  - A change to the use case's evidence gaps does not withhold the judgement, as designed.
  - An excluded judgement whose `assessed_by` link is still in place is dropped without an error.
  - A reviewed judgement set back to `needs_review` becomes a draft.
  - A summary set to `source_checked` but not yet pinned is not published.
- **`repin`.** By default it pins only reviewed claims that have no pins. Named claim IDs must be reviewed judgement or summary claims. `--all` cannot be combined with claim IDs.
- **`next.mjs withheld`.** It now flags any served mapping that is no longer active, and any served mapping that is missing from the next release unless its claim is `excluded` or `superseded`. I read the code; I did not run it against two releases.
- **Schema.** No use-case artifact in the repository uses `not_assessed`, so removing it from the schema does not break any archive.
- **Ontology wording.** The new `rb:assessedBy`, `rb:RelevanceJudgement` and `mapping.json` text is accurate, including the domain of SEPIO has_evidence.
- **Commands.**
  - `npm run records -- check`: 29,444 records match their provenance.
  - `npm run typecheck`: exit 0.
  - `npx vitest run tests/use-case-records.test.ts`: 14 tests pass before the summary review. After it, "publishes a summary only once it is reviewed and pinned" fails, because it asserts the stored summary is unpublished (finding 15). `npm test`: 498 of 499, the same test.
  - `npm run test:kg`: OK.

### CNV summary against the sources

I re-downloaded the DRAGEN supplementary XLSX from its recorded URL. Its SHA-256 is `c8d66e8373f22382f1c5e4a576d2c85825a18232a14767d239966bc8ab56c3d9`, equal to the `artifact_sha256` recorded in the result reviews. I read sheet "S4 CNV benchmarking", rows 6 to 10, with openpyxl.

The Gabrielaite Table S2 workbook in `data/omics/use-case-coverage-cnv-20261009/artifacts/` decompresses to SHA-256 `eb4bb389b248508531ca371ba80e004a573f4e85029583cff336f217307fde85`, equal to the source record. I read its `GB-WGS-NA12878` rows.

Every cell matches the stored results.

| Statement | Source values | Verdict |
| --- | --- | --- |
| DRAGEN 4.2 CNV+SV found 87 to 100% in every size bin | recall 0.873, 0.933, 0.888, 0.909, 1.0 | Supported |
| precision 0.99 to 1.00 | 0.986, 1.0, 1.0, 1.0, 1.0 | Supported |
| the developers' own benchmark | The judgements record "Author-run comparison (DRAGEN developers)" | Supported by the records |
| CNVnator matched it above 10 kb | F-score 0.976, 0.949, 0.99 against 0.941, 0.952, 1.0 | Supported |
| CNVnator found only 26% of 1 to 5 kb and 51% of 5 to 10 kb | recall 0.264, 0.505 | Supported (0.505 rounds to 51%) |
| LUMPY, DELLY and Manta recovered 88 to 94% | recall 0.9408, 0.9037, 0.8752 | Supported |
| only 20 to 33% of their calls matched | precision 0.31, 0.1988, 0.3262 | Supported |
| Manta and CNVnator were used to build this truth set | Protocol limitation, citing Results 3.7 | Supported by the record |
| the other callers recovered 1 to 43% | CLC 0.0116, Control-FREEC 0.1069, cn.MOPS 0.1696, GATK gCNV 0.2322, CNVnator 0.4345 | Supported |
| none of the comparisons shown reports duplications separately | Behera S4 covers deletions only. Gabrielaite S2 gives call counts by type (`N_DEL`, `N_DUP`) but pools precision and recall | Supported for the reviewed comparisons |

The last statement depends on draft judgements not being shown as evidence. The De La Vega HG002 protocol, still a draft, does report duplications. When any further judgement on this use case is reviewed, the summary's pins change and the summary is withheld until it is re-reviewed. That covers this case.

I set `use-case-summary-cnv-detection-characterisation` to `source_checked` with a review, recorded the change with `npm run records -- change`, and pinned it with `npm run use-cases:repin -- docs/reviews/2026-10-09-use-case-records.md use-case-summary-cnv-detection-characterisation`.

### New findings

13. **Low. Configuration and dataset records are not pinned.** Disputing a configuration withholds the judgement, but a change to its name or attributes (for example its version) leaves the judgement active. A change to a dataset's description also leaves it active. The evaluation pin covers its links, so swapping in a different configuration or dataset is caught; editing that configuration or dataset in place is not. Consider pinning the reviewed evaluations' configurations (name, status, attributes) and datasets (name, description, status).
14. **Low. One code comment is slightly inaccurate.** `judgementPinFields` says a new result never stales a judgement. A new result on a reviewed evaluation does withhold it (probe above). That is the safe direction, but the comment and `docs/use-cases.md` should say so.
15. **Low. One test needs updating now that the summary is reviewed.** `tests/use-case-records.test.ts`, "publishes a summary only once it is reviewed and pinned", expects the stored summary to be unpublished (`expect(cnv(store).summary).toBeUndefined()`). It should start from a `needs_review` copy of the summary instead. I did not edit the test because it is outside this review's scope.
