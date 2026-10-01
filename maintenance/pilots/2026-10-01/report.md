# Bounded evidence-refresh pilot — 1 October 2026

**Disposition: incomplete monthly cycle.** The discovery, source-check and use-case validation components were exercised successfully within the scope below. This is not a completed monthly evidence sweep, does not advance a completed-sweep date, and does not establish scientific review approval. Keep the monthly schedule described as planned.

## Baseline and scope

Producer revision: `261168d9e70aadb4ad18d050b17d6bd023577755`. Local archived release: `2026-09-30-e37e3ab1284d` (2026-09-30T21:54:42.169287Z); 28,133 records, including 999 sources. The release's catalogue and use-case artifact hashes were checked against its immutable manifest. Live website/API alignment was not checked.

The search ledger has 11 entries covering nine research lanes and two cross-cutting scope/access entries. Its 16 September acquisition was bounded. No prior completed monthly sweep was established. Search target: 2 September–1 October, with a 14-day overlap around the earlier cutoff; older pending leads were eligible for revisiting. Four targeted web queries were used, without exhaustive index pagination.

Open PR inventory on 1 October: no producer PRs; consumer [#81](https://github.com/rewire-bio/rewire-database/pull/81) and [#74](https://github.com/rewire-bio/rewire-database/pull/74). Their scientific content and deployment status were not reviewed here.

## Discovery decisions

1. **GPN-Star — candidate for identity and protocol review.** The [primary Nature article](https://www.nature.com/articles/s41586-026-11005-5) was published 9 September 2026. The [official repository](https://github.com/songlab-cal/gpn) distinguishes it from PhyloGPN. Searches across all baseline records found no GPN-Star name, paper DOI or preprint-DOI match. The existing PhyloGPN README already mentions it, so this is a catalogue omission found through overlap, not a claim of a newly released model after the last search. Exact checkpoints, alignment/data versions, protocols and source tables remain unreviewed. No score or model-selection recommendation was imported.
2. **GlycoGym — known pending lead revisited.** The [official README](https://raw.githubusercontent.com/BojarLab/GlycoGym/7630b9c12f52e1671fb9143a4e400816cfd31f75/README.md) is accessible and lists glycan benchmark tasks and a dataset landing page. This lead was already pending in the 16 September ledger. It remains pending because task-level protocols, split integrity, dataset releases, licences and stated NMR exclusions need dedicated review. The linked Zenodo landing page was not retrieved.

Logged queries (web search, 1 October):

- `GlycoGym glycan benchmark official github paper 2026`
- `genomics benchmark September 2026 preprint genome foundation models`
- `"GPN-Star" "github.com"`
- `"Predicting genome-wide functional constraints with GPN-Star" "code"`

## Existing-source checks

Two existing sources were checked by fetching the current GitHub HEAD and both pinned/current README bytes. All nine direct HTTP requests in this pilot succeeded. Exact response bytes and request dates are bound in `retrievals.json`; publisher HTML is represented by its retrieval hash rather than redistributed text.

| Source | Pinned/current HEAD | README receipt | Decision |
| --- | --- | --- | --- |
| TAPE | Both `6d345c2b2bbf52cd32cf179325c222afd92aec7e` | Original hash matches; current bytes unchanged | No change in the inspected document |
| GPN | `6f28c81bcbfe7d65cb6d8ece9ce88f87ca583791` → `dc5fd287599f2955a79d010bca0e0f7f8178c67e` | Original hash matches; current bytes unchanged | Repository HEAD changed; code/release diff still requires review |

The existing `check-updates.ts` considers 62 pinned sources from `discovery.jsonl` and `migrated.jsonl`; it checks HEADs, not scientific claims. This bounded pilot sampled TAPE from that set and additionally checked the GPN enriched source outside that script's inventory. It did not execute the entire updater. A changed repository HEAD does not establish changed numerical evidence; recorded versions and receipts were retained.

## Use-case completeness and staleness

Existing `loadUseCases`, `buildUseCaseArtifact` and `validateUseCaseArtifact` checks passed against the archived catalogue. They verified the frozen input receipt and all 62 mapping fingerprints without replacing any hash. All 17 questions have mappings; all 62 mappings are active in this baseline, with zero automatic demotions. Ten collection plans remain `collecting`; the other seven questions have no collection-plan object. Every question retains evidence gaps.

All 17 question reviews and 62 mapping reviews are explicitly automated source review. Mapping dates range from 25–30 September; question review dates are 30 September. No question is more than one month old on the pilot date. These age and integrity checks do not reverify source claims or suitability. Human scientific review remains unassigned. Unimported upstream changes do not automatically alter the frozen baseline's fingerprints.

| Use case | Active mappings | Collection plan | Recorded gaps |
| --- | ---: | --- | ---: |
| Interpret BRCA1/BRCA2 germline variants | 5 | collecting | 5 |
| Transfer cell-type annotations to a new dataset | 1 | collecting | 4 |
| Review EGFR lung-cancer actionability evidence | 1 | collecting | 5 |
| Assess models for genetic perturbation experiments | 2 | absent | 6 |
| Shortlist molecular identities from tandem mass spectra | 7 | absent | 9 |
| Select perturbations for a defined cellular response | 2 | collecting | 6 |
| Compare methods for plant promoter experiments | 8 | absent | 10 |
| Assess methods for protein stability experiments | 3 | absent | 10 |
| Rank rare-disease variants for review | 7 | collecting | 4 |
| Select regulatory variants and genes for functional follow-up | 1 | collecting | 3 |
| Assess rhodopsin wavelength prediction across sequence backgrounds | 6 | absent | 9 |
| Assess somatic small-variant oncogenicity | 4 | collecting | 4 |
| Prioritise variants for splicing experiments | 2 | absent | 9 |
| Choose structural hypotheses to guide experiments | 5 | collecting | 5 |
| Select therapeutic targets for validation | 2 | collecting | 6 |
| Reanalyse unresolved rare-disease cases | 1 | collecting | 4 |
| Set baselines for UTR translation experiments | 5 | absent | 10 |

The issue's seven-mapped/ten-planned description is historical; the 30 September archive contains 62 scoped mappings across all 17 questions. It still does not establish complete evidence for any end-to-end decision.

## Coverage, remaining work and controls

Three lanes were touched: genomics (candidate plus source check), other-omics (pending lead), and protein fitness (one source check). **No lane was completed.** RNA, structure/design, cellular/spatial, microbial, molecular-interaction and network/mechanistic discovery were not checked. No exhaustive corrections/retractions, licence/access, broken-link or pending-candidate sweep was performed. Other search hits were not screened or counted as accepted candidates.

Scientific records changed: **0**. Review receipts renewed: **0**. Numeric results imported: **0**. Model executions: **0**. The scientific-data worktree diff remained empty. This pilot does not publish, change a review date, propose a clinical winner or claim qualified human review.

Next work: complete a declared all-lane scoped sweep; review the two candidates and the GPN repository change; assign scientific and operational owners; prepare a focused update PR when evidence supports changes; and verify release/publication alignment through the normal gates. Until then the monthly cycle remains incomplete and scheduling remains planned.

## Audit and replay

`report.json` contains baseline and pilot SHA256 inventories, full queries/decisions, scope counts and explicit gaps. `use-case-check.json` includes every question's existing gap text. `sources/` retains exact GitHub API and README responses with upstream URLs in `retrievals.json`.

Read-only use-case validation: `node_modules/.bin/tsx maintenance/pilots/2026-10-01/check-use-cases.ts`. The source collector refuses to overwrite an existing retrieval log: future checks belong in a new run directory. Comparing stored hashes is sufficient to verify these exact artifacts; reretrieval of a mutable endpoint can legitimately produce different bytes.
