# MFASS v2 baseline recipe: executed instruction, review, 2026-10-12

Batch: `data/omics/mfass-recipe-receipt-20261012/`. `proposal.json` is the drafter's proposal. It adds one command-line instruction, "Run the registered baseline with the released wheel", with status `executed`, to the run recipe `mfass-v2-baseline` on `rewire-mfass-v2`. Its validation receipt is a new source record for the receipt folder in rewire-bio/rewire-benchmarks, `benchmarks/mfass/reproductions/2026-10-12-cpu-baselines/` at commit `779eeb5c88712442fbc9682c3d417cb7a7427fe3` (the merge commit of rewire-benchmarks PR #43, merged 2026-10-12).

Reviewer: a separate Claude review agent that did not draft the proposal. No human review is claimed. I did not rerun the baseline. This is a check of the receipt's bytes and contents against the proposal and the store.

## Outcome

- Approved without changes to the proposed values.
- Source `runner-receipt-mfass-v2-cpu-baselines-779eeb5c` added with status `source_checked` and a review block (`npm run records -- add`).
- `rewire-mfass-v2`: the source ID added to `source_ids`, and the instruction appended to `mfass-v2-baseline` (`npm run records -- change`). The two existing instructions use other entry points (`rewirebench.run` with `KmerBaseline`, and `rewirebench run --adapter` at `f80cef7f`) and stay `source_reviewed_not_executed`.
- No result or evaluation changes. The stored corrected-baseline results already carry these values.

## Checks

| Check | Outcome |
| --- | --- |
| SHA-256 of `SHA256SUMS` at the pinned commit | `fab950f4...2163c644`, matches `artifact_sha256` |
| Every file listed in `SHA256SUMS` (10 files) | all match |
| Files in the folder not listed | `README.md` only. Its SHA-256 at this commit is `4862b90ea7b0a66764e66bc89ba6f1ff118f21981441973235681f8de7e5171b`, recorded in the source's review note |
| `mfass-kmer-position-v2/report.json`, `metrics` | `precision_at_capacity` 0.61, `average_precision_sklearn` 0.28641674595892375, `auroc` 0.7779498064677238, n 8324, positives 315 |
| Coverage | 8324 scored of 8324, 0 unscored; `scope` and `protocol_results.scope` both `full`, `completion` `complete` |
| Protocol | `protocol_id` `mfass-v2`, `protocol_version` and `runner_revision` `bee9133b83f3aedaf2bbb9013f1875515845607e`, as the recipe's data requirement names |
| Split | `split_sha256` `999ebcb7...7f052`, matches `rewire-mfass-v2` and the split profile record. Train 19,409 plus test 8,324 is the 27,733-variant split the requirement names |
| Cohort | `cohort_sha256` `389702ff...7bd0`, matches the MFASS matched-v1 configurations |
| Prepared artifact | `prepared_sha256` `cbba55d1...7f38d3`, matches the stored 2026-09-21 training-prior evaluation |
| Training prior | `training-prior-v1/predictions.json` SHA-256 `c9f2d729...b3f8`, identical to the predictions hash of the stored 2026-09-21 evaluation |
| Stored corrected baseline (`rewire-result-baseline-kmer-position-v2-*`) | P@100 0.61 and AUROC 0.7779498064677238 identical. AP stored as 0.2864167459589237; the new report has 0.28641674595892375, one unit in the last place apart. Both are 0.2864 at the proposal's precision |
| Wheel | `rewirebench-0.5.0-py3-none-any.whl` from the v0.5.0 release passes the release `SHA256SUMS` check as written in the instruction |
| CLI | `rewirebench/cli.py` in the wheel is byte-identical to `packages/rewirebench/src/rewirebench/cli.py` at tag v0.5.0. `prepare PROTOCOL --source --output` and `run-baselines --prepared --output` exist with those flags |
| Skill | `skills/bio-model-benchmarks/SKILL.md` at the pinned commit uses the same download, check, `uv venv`, `uv pip install`, `prepare` and `run-baselines` commands |
| Rerun wording | The source description says "A rerun with the project's own code and data, not an independent reproduction". The receipt README says "a rerun with the project's own code and data on new hardware, not an independent reproduction by another group", each report has `independently_reproduced: false`, and the manifest has `scientific_reproduction: not_established` |
| Platform | `environment` gives macOS-26.6.2-arm64, Python 3.11.13, rewirebench 0.5.0; the CLI-only run reports no container |

## Use-case judgement re-review

`use-case-mapping-20260930-339-25925e279972` (relevance of MFASS v2 to "Prioritise variants for splicing experiments") pins all of `rewire-mfass-v2`'s `source_ids` and `attributes`, so this change withholds it. I re-read the judgement against the changed record. Its relevance (`proxy`), endpoint, rationale, constraints and limitations do not refer to the run recipes, and the executed instruction reproduces the stored corrected-baseline values the judgement's reviewed evaluations already carry. Nothing in it becomes false. It is repinned unchanged with `npm run use-cases:repin -- docs/reviews/2026-10-12-mfass-recipe-receipt.md use-case-mapping-20260930-339-25925e279972`.

## Limitations

- The README gives the commands as `rewirebench prepare mfass-v2 ...` then `rewirebench run-baselines`; it does not print the exact paths. The instruction's `data/mfass`, `prepared` and `runs/mfass-baselines` paths are placeholders consistent with the other recipe instructions, not a verbatim transcript.
- The README says "`SHA256SUMS` covers every file", but it does not cover the README itself. The README hash is recorded in the review note so the "How it was run" locator can still be checked.
- The run is by the benchmark's own maintainers with its own code and data. It shows the released wheel reproduces the stored baseline on this platform; it is not independent reproduction.
- The recipe-level `version` stays `f80cef7f`. The new instruction pins its own version through the v0.5.0 wheel URL and release checksum.
