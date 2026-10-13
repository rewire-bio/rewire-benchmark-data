# BioML-bench: research notes

Scope: add BioML-bench (Science Machine; github.com/science-machine/biomlbench) and its preprint. Search window: to 2026-10-13. Budget: about 10 queries; 6 used. Extractor: Claude (Opus 5.5) research agent; no human review claimed. Nothing here is reviewed.

## Scope decision

docs/collection.md listed "language-agent benchmarks" as out of scope, yet BioDiscoveryAgent and Biomni A1 were already in the store for target validation because they are scored on omics endpoints. The scope text was amended in this PR: agent systems are in scope when scored on a task with a molecular or omics endpoint; question answering, clinical and literature-reasoning agent benchmarks and imaging-only tasks stay out.

BioML-bench is included on that basis. Its drug discovery (9 tasks: ADME, kinase inhibition and toxicity prediction from SMILES), protein engineering (6 ProteinGym DMS assays) and single-cell omics (5 tasks adapted from Open Problems) domains have molecular or omics endpoints. The biomedical imaging domain (4 Kaggle tasks: CT-based lung function, histopathology patches, MRI MGMT methylation status and GI tract segmentation) is excluded as imaging. The MGMT task predicts a molecular label from MRI only; it is still an imaging-input task and is excluded with the rest of its domain, because results are only printed per domain.

## Searches

| Time (UTC) | Channel | Query | Outcome |
| --- | --- | --- | --- |
| 12:37 | GitHub API | repos/science-machine/biomlbench; commits/main | Repo metadata, head commit 673f3d8 |
| 12:38 | bioRxiv API | details/biorxiv/10.1101/2025.09.01.673319; pubs/biorxiv/... | 3 versions, CC BY, no published version |
| 12:38 | arXiv API | search_query=ti:"BioML-bench" | 0 hits |
| 12:41 | Europe PMC REST | "BioML-bench" | 3 hits: the preprint (PPR1078781); Agentomics (doi:10.1093/bioinformatics/btag250, 2026); a cancer-imaging review (doi:10.21147/j.issn.1000-9604.2026.04.05) |
| 12:41 | arXiv API | search_query=abs:"BioML-bench" | 1 hit: AutoScientists (arXiv:2605.28655v1) |
| 12:41 | arXiv API | search_query=all:BioML-bench | same AutoScientists hit |

The preprint has no arXiv version. Agentomics and AutoScientists cite or use BioML-bench; they were not read and are recorded as leads in the ledger, not extracted.

## How agents are modelled

Following BioDiscoveryAgent (`tgtval-20261009-method-biodiscoveryagent` with one configuration per LLM backbone, each with `uses_model`):

- Agent scaffolds are `method` records: AIDE, STELLA, MLAgentBench (new) and Biomni (reused: `tgtval-20261009-method-biomni`, "Biomni A1"; the repository wrapper imports `biomni.agent.A1`). The Dummy agent is a method with no method type.
- Each agent as run is a `configuration` (`configuration_of` the method, `uses_model` the LLM where the paper names one).
- LLMs are `model` records at service level: GPT-4.1 and Claude Sonnet 4, both new (no existing record for either). Versions are missing with reason `unreported`: the paper prints only the family names. The repository configs name `gpt-4.1-2025-04-14` and `claude-sonnet-4-20250514`; these are recorded as claims about repository defaults, not as the evaluated versions.
- STELLA: the paper says "the OpenRouter default"; the repository config sets `model: claude-sonnet-4`. No `uses_model` link; `missing_metadata.model` is `conflicting`.
- Versions printed: Biomni v0.0.5, AIDE v6.3.3. MLAgentBench and STELLA versions are unreported.

## What was extracted

Table 4 (results by domain), the Drug Discovery, Protein Engineering and Single Cell Omics blocks, both the Penalized and Non-penalized settings: 5 agents x 3 domains x 2 settings = 30 evaluations, 132 results. Every printed cell in those blocks was extracted except:

- Completion Rate "NA" for Dummy in the three penalized blocks (3 cells): not numeric. Table 2 prints 100.0 for Dummy overall.
- Completion Rate "-" in all 15 non-penalized rows: not applicable in that setting.

Not extracted:

- Table 2 (overall): aggregates all 24 tasks including the 4 imaging tasks, so it is not a molecular or omics endpoint.
- Table 4 Biomedical Imaging blocks: out of scope.
- Figures 2 and 4 (per-task leaderboard percentiles as points): no printed values; not read by eye.
- Figures 3, 5 and 6 (strategy, architecture and failure-mode proportions): no printed values, and not benchmark results.
- Section 4.3 mentions AIDE reaching the 100th and 54th leaderboard percentile in two runs on "the Tsuboyama 2023 ProteinGym benchmark". Not recorded as results: the assay is not named exactly and they are single runs chosen as examples.

Metrics: leaderboard percentile uses a new vocabulary concept `leaderboard-percentile` (added to data/vocab/metric.ttl; no STATO match found). Mean rank uses `rank` with a qualifier; Above Median, Any Medal and Completion Rate use `proportion` with qualifiers that quote Section 3.4. The source states the direction for leaderboard percentile (higher) and mean rank (lower); `higher` for the three proportions is the extractor's reading and should be checked.

Uncertainty: every "x ± y" cell is recorded as `unresolved_spread`. The Table 4 caption does not say what the spread is; Figures 2 and 4 describe the per-domain percentiles as mean ± SEM across tasks, and the Table 2 caption refers to "the reported SEM". A reviewer may decide this is enough to record `standard_error`.

Origin: `independent_paper`, as for Biomni A1 on AssayBench: the benchmark's authors ran agents they did not build.

## Tasks and links to existing records

Results attach to three domain-level protocols, because that is the level at which values are printed. The 20 in-scope tasks are recorded as `task` records (`part_of` BioML-bench, `parent` their domain protocol) so the composition of each aggregate is explicit.

Links to existing benchmarks:

- 6 protein tasks: `part_of` `discovery-benchmark-proteingym`. The repository's grader averages Spearman over ProteinGym's own supervised folds (fold_random_5, fold_modulo_5, fold_contiguous_5), so these are ProteinGym supervised assays. No per-assay ProteinGym records exist in the store to link.
- 5 tdcommons tasks (cyp2d6-substrate, lipophilicity, herg, bbb-martins, caco2-wang): `part_of` `discovery-benchmark-tdc-molecular-tasks`. Not linked to the `tdc-task-tdc-*` or `tdc-dataset-tdc-*` records: those fix the TDC ADMET benchmark group split, and whether the Polaris Hub copies use the same split was not checked. Candidate links for a reviewer: tdc-task-tdc-cyp2d6-substrate, tdc-task-tdc-lipo, tdc-task-tdc-herg, tdc-task-tdc-bbb, tdc-task-tdc-caco2.
- 4 Polaris tasks (pkis2-egfr-wt-c-1, adme-fang-hclint-1, -hppb-1, -solu-1): no Polaris records exist in the store.
- 5 single-cell tasks: not linked to `discovery-benchmark-open-problems`. BioML-bench prepares its own data and splits (for example a 10/90 split of the TNBC data for cell-cell communication; diabetic kidney disease data for label projection, which is not among the store's Open Problems label-projection subsets).

## Use cases

No use-case mapping. Checked against data/entities/use-cases.jsonl:

- use-case-protein-stability asks for per-method correlation and error on held-out or dissimilar proteins. The protein domain mixes stability, binding and fitness assays, uses within-assay cross-validation and reports leaderboard percentiles, so it does not match.
- use-case-genetic-perturbation-response and use-case-phenotype-perturbation-selection concern genetic perturbations; the one perturbation task here is small-molecule, and it is reported only inside a 5-task aggregate.
- use-case-cell-type-annotation-transfer: label projection is one of 5 tasks in the single-cell aggregate.

## Gaps and points for the reviewer

1. Task identity conflict: Table 3 lists SPA_STAAU_Tsuboyama_2023, PSAE_PICP2_indels and CBX4_HUMAN_multi-sub; the repository task list at commit 673f3d8 has SBI_STAAM_Tsuboyama_2023_2JVG, PSAE_PICP2_Tsuboyama_2023_1PSE and CBX4_HUMAN_Tsuboyama_2023_2K28 in those positions. The three task records use the paper's labels and say so. This may warrant a source `evidence_concerns` entry.
2. Denominators: Section 3.4 defines Above Median, Any Medal and Completion Rate over tasks, but the printed values are multiples of 1/(4 x tasks) (for example protein 45.8% = 11/24, drug discovery 30.6% = 11/36, single-cell 55.0% = 11/20), which fits counting replicate runs. Recorded as a source and protocol limitation.
3. Spread type in Table 4 (see Uncertainty above).
4. Repository configs differ from the paper: STELLA's model, and time limits (repository: 43,200 s for AIDE, Biomni and MLAgentBench; 57,600 s for STELLA; paper: 8 hours for non-imaging tasks).
5. Leaderboard snapshots: the paper does not give the size or date of each human leaderboard; the repository fetches them at grading time. Percentiles cannot be re-derived from the pinned sources.
6. bioRxiv v1 and v2 were not compared with v3.
7. Agentomics (Bioinformatics 2026) and AutoScientists (arXiv:2605.28655v1) may report BioML-bench results; not read.
8. Competing interests: an author is CTO of ScienceMachine, which provided compute and LLM API resources (recorded as a source limitation).
