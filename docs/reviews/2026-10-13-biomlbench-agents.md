# BioML-bench agent evidence review, 2026-10-13

Batch: `data/omics/lit-agents-20261013-biomlbench` (PR #139). Reviewer: Claude (Opus 5.5) research agent, independent of the extractor; no human review claimed.

## Outcome

All 132 results match bioRxiv v3 Table 4. 112 are `source_checked`. The 20 Mean Rank results in the Drug Discovery and Protein Engineering blocks are `disputed`, because the v3 table is internally inconsistent there (below). No number was changed. Four descriptive fields were corrected with `metadata-correction-*` claims, and one claim was added. No source `evidence_concerns` entry was raised.

## Sources and hashes

| Source | Pinned SHA-256 | Check |
| --- | --- | --- |
| bioRxiv 10.1101/2025.09.01.673319 v3 PDF | `875cb351…38b35` | The extractor's downloaded file is still on disk and hashes to the pinned value. A fresh download (`4c3462e3…442b57`, same 2,282,513 bytes) differs in 43 bytes, all in bioRxiv's per-download stamps: XMP ModifyDate, MetadataDate, DocumentID and InstanceID, the Info ModDate and the trailer /ID. Both copies give the same `pdftotext -layout` text. The source record now has a `hash_scope` that says so. |
| science-machine/biomlbench @ 673f3d8, codeload tar.gz | `c2397827…ae559` | Re-downloaded; identical. The 9 per-file hashes in `sources.md` match. |

bioRxiv v1 and v2 were also downloaded and compared with v3 (not pinned; used only for the consistency check below).

## Results checked

An independent parser (written without reference to `extract/extract_biomlbench.py`) located the 40 Table 4 rows by domain and agent label, asserted 5 cells per row, and compared every in-scope cell with the batch.

| Block | Domain | Results | Outcome |
| --- | --- | --- | --- |
| Penalized | Drug Discovery | 23 | All match. Mean Rank (5) disputed |
| Penalized | Protein Engineering | 23 | All match. Mean Rank (5) disputed |
| Penalized | Single Cell Omics | 23 | All match |
| Non-penalized | Drug Discovery | 20 | All match. Mean Rank (5) disputed |
| Non-penalized | Protein Engineering | 20 | All match. Mean Rank (5) disputed |
| Non-penalized | Single Cell Omics | 20 | All match |
| Total | | 132 | 132 match; 20 disputed |

Checked per result: `printed_value`, `numeric_value`, the spread value, `source_locator`, metric (`leaderboard-percentile`, `rank`, `proportion`), unit, direction and the evaluation link (domain, setting, agent). The 3 penalized Dummy "NA" completion cells and the 15 non-penalized "-" completion cells are correctly not recorded. Imaging rows are correctly excluded.

All 13 extractor claims were checked: the 5 repository claims against the cited files, the 8 paper claims against the text layer. All match. `claim-benchmark-human-baselines` joins the Figure 1 caption and Section 5.1 ("in-evitably" is hyphenated across a line in the PDF); the wording is a close paraphrase and acceptable. The 20 task records match Table 3 and the repository task configs (grader names, Polaris main metrics, ProteinGym fold columns).

## Conflict found: Mean Rank in v3 Table 4

Mean Rank is each agent's rank among the five agents, averaged over the domain's tasks, so the five values in a block should sum to 15. They do in the penalized Imaging and Single Cell Omics blocks of v3 and in every Drug Discovery and Protein Engineering block of v2. In v3:

| Block | v2 sum | v3 sum | STELLA v2 | STELLA v3 | STELLA change |
| --- | --- | --- | --- | --- | --- |
| Drug Discovery, penalized | 15.00 | 13.83 | 3.56 | 2.39 | 1.17 |
| Drug Discovery, non-penalized | 15.00 | 14.11 | 3.67 | 2.78 | 0.89 |
| Protein Engineering, penalized | 15.00 | 14.58 | 2.75 | 2.33 | 0.42 |
| Protein Engineering, non-penalized | 15.01 | 14.67 | 2.92 | 2.58 | 0.34 |

v3 replaced only the STELLA rows of these blocks (and STELLA's Table 2 rows), with much higher values (for example protein penalized percentile 14.78 to 34.98, completion 87.5 to 100.0), and gives no reason in the text. The other agents' rows, including their Mean Rank, are identical to v2. The shortfall in each sum equals STELLA's change, so the other agents' ranks were not recomputed. The source cannot say which values are wrong, so all 20 Mean Rank results of those blocks are `disputed` with a `source_warnings` entry. Leaderboard percentile, Above Median, Any Medal and Completion Rate do not depend on the other agents and are not affected.

A result-level mark was chosen over a source-level `evidence_concerns` entry, which would withhold all 132 results, as in the 2026-10-12 RNA and other-omics review. Table 2 has the same problem (penalized sum 14.45 in v3, 15.00 in v2) but is not extracted.

The Section 4.2 sentence "in Protein Engineering and Drug Discovery Biomni leads" (penalized) is unchanged from v2. In v3 STELLA has the higher penalized protein percentile and Above Median, and Biomni the better Mean Rank. This is recorded as a source limitation.

## Flagged items

1. **Protein assay identity (Table 3 vs repository).** The repository task descriptions were read. SPA_STAAU_Tsuboyama_2023 (protein A) vs SBI_STAAM_Tsuboyama_2023_2JVG (Sbi, single substitutions) is a real conflict: different proteins, and the repository also has a separate SPA_STAAU_Tsuboyama_2023_1LP1 task that is not in the list. PSAE_PICP2_indels vs PSAE_PICP2_Tsuboyama_2023_1PSE is a real conflict: 1PSE is the substitution assay, and a separate `_indels` task exists. CBX4_HUMAN_multi-sub vs CBX4_HUMAN_Tsuboyama_2023_2K28 is not a conflict: the 2K28 description says it holds multi-substitution variants of CBX4_HUMAN. v1 and v2 Table 3 print the same labels as v3. **Decision: no `evidence_concerns`.** All agents ran the same task set, so comparison between agents within the table holds. What is uncertain is the exact composition of the protein aggregate, which the limitations already state. The source limitation, the protein dataset limitation and the CBX4 task's `dataset` and `scope_note` were corrected from "three" to two conflicts (4 metadata-correction claims).
2. **Table 4 "±".** The caption does not name the spread. Arithmetic check: every "x ± x" cell (12.5 ± 12.5, 1.11 ± 1.11, 5.6 ± 5.6 and others) is what an SEM gives when one unit is non-zero, and an SD would not give it. For all 40 penalized Above Median and Any Medal cells, some vector of per-task replicate fractions (k/4) reproduces both the mean and the spread as SEM across tasks; SD across tasks reproduces none of the 28 non-zero cells. Figures 2 and 4 say mean ± SEM across tasks, and the Table 2 caption refers to "the reported SEM". **Decision: keep `unresolved_spread`.** The evidence is consistent with SEM across tasks, but Table 4 never states it, and the type would be inferred. The finding is in each result's review note.
3. **Denominators.** The same fit shows the three rates are means over tasks of the per-task fraction of the 4 replicate runs (for example protein STELLA Above Median 45.8 = per-task fractions 0, 0, 1/4, 2/4, 1, 1). This is consistent with the repository grader, which sets `above_median` and the medals per run (`biomlbench/grade_helpers.py`). So Section 3.4's "proportion of tasks" describes the values loosely. The source and protocol limitations already record this. No change.
4. **Direction of the three proportions.** Section 3.4 does not state it. Section 4.1 supports `higher` for Above Median and Any Medal: in the non-penalized setting STELLA "outperform[s]" Biomni "on most metrics", which holds only if higher is better (STELLA is higher on percentile, Above Median and Any Medal, and worse on Mean Rank). For Completion Rate, the paper treats failed runs as the poorest outcome (Section 4.1). `higher` is confirmed for all three.
5. **Repository configuration vs paper.** The STELLA model conflict is recorded correctly (`missing_metadata.model: conflicting`, no `uses_model` link, repository claim). The time-limit note in `research.md` and the repository source limitation is incomplete. The runner replaces the agent's `TIME_LIMIT_SECS` with the task's `time_limit` (`biomlbench/agents.py`, `agents/registry.py`). 18 of the 20 in-scope tasks set 28800 s (8 h), which matches Section 3.4. Only Q8EG35_SHEON_Campbell_2022_indels and CSN4_MOUSE_Tsuboyama_2023_1UFM_indels set none, so the agent default (43200 s, or 57600 s for STELLA) would apply. A new claim (`claim-repo-time-limits`) and a repository source limitation record this.
6. **Leaderboard snapshots.** Confirmed unstated in the paper, and no leaderboard file exists in the repository. There is a further caveat, added as a repository source limitation. For ProteinGym tasks the "leaderboard" is ProteinGym's own per-assay row, one entry per published model, with a placeholder date (`biomlbench/data_sources/proteingym.py`). The Open Problems spatial-genes description says its leaderboard "is comprised of existing methods". The manual data source returns an empty leaderboard at this commit. So for protein and single-cell tasks, "above the median human submission" means above the median of published methods. The paper's description of "largely expert-populated" human leaderboards fits the Polaris tasks better.
7. **v1 and v2.** v1 and v2 Table 3 are the same as v3. v2 Table 4 differs from v3 only in the 4 STELLA rows (see the conflict above); v1 Table 4 was not compared. In the text, v3 rewrote the conclusions around STELLA ("STELLA overtook it once failed-run penalties were removed").

## Other findings

- All six ProteinGym task configs set `awards_medals: false`, but Table 4 prints non-zero protein Any Medal values. The grader computes medal thresholds from leaderboard size and ignores the flag. Added as a repository source limitation.
- The Competing Interests section also names M. G. as a contract employee of ScienceMachine. Added to the source limitations.
- The `leaderboard-percentile` concept is sound. STATO has `percentile` (STATO:0000293), but it is a quantile cut point, the inverse of what is needed here. OBI has no match. NCIT:C181342 "Percentile Rank" ("what percent of the reference population the individual would equal or exceed") is close but includes ties, while the BioML-bench grader counts only strictly worse entries. `metric.ttl` maps only to STATO, so leaving the concept unmapped is right. The definition is accurate against the grader code: 0 to 100, share of leaderboard scores the submission beats, direction-aware.
- Scope edit to `docs/collection.md`: accepted. It makes the written rule match what the store already holds (BioDiscoveryAgent, Biomni A1) and keeps question answering, clinical and literature-reasoning agent benchmarks out. BioML-bench's three included domains have molecular endpoints. Excluding the imaging domain, including the MGMT task, follows the existing imaging rule.

## Corrections made in review

| Record | Change | Reason |
| --- | --- | --- |
| 20 Mean Rank results (Drug Discovery, Protein Engineering; both settings) | `disputed`, `source_warnings` | Block sums no longer 15 after the v3 STELLA update |
| `lit-agents-20261013-biomlbench-source-miller2025-v3` | `hash_scope` added; `limitations[2]` corrected (claim); 3 limitations appended | Download stamps; two not three assay conflicts; v2 to v3 change; Section 4.2 text; competing interests |
| `lit-agents-20261013-biomlbench-source-repo-673f3d8` | 3 limitations appended | Time-limit override; leaderboard composition; `awards_medals` |
| `lit-agents-20261013-biomlbench-task-cbx4-human-multi-sub` | `dataset`, `scope_note` corrected (2 claims) | Same assay under a shortened label |
| `lit-agents-20261013-biomlbench-data-protein-engineering-tasks` | `limitations[0]` corrected (claim) | Two, not three, conflicts |
| `lit-agents-20261013-biomlbench-claim-repo-time-limits` | New claim | Per-task time limits |

Every other record moves from `needs_review` to `source_checked`.

After `records -- add`, the attribute normalisation test found the `missing_metadata` keys of `config-stella-openrouter-default`, `model-claude-sonnet-4` and `model-gpt-4-1` out of alphabetical order. The keys were sorted, with no change of content, and recorded with `records -- change` against this review.

## Remaining gaps

- Which SPA/SBI and PSAE assays were run is unresolved.
- Leaderboard sizes, snapshot dates and the single-cell leaderboards cannot be recovered, so percentiles cannot be re-derived.
- Why STELLA's v3 values changed is not stated; the run configuration behind them is unknown.
- Figures 2 to 6 were not read by eye.
- Agentomics (Bioinformatics 2026) and AutoScientists (arXiv:2605.28655v1) were not read.

## Verdict

Fit to merge once the store add and the checks pass. The values are faithfully transcribed. Each known problem is marked on the record it affects.
