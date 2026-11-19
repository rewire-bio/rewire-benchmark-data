# BEND run guide corrections, 2026-11-19

Reviewer: Claude agent, automated. No human review is claimed. Nothing was installed or run, and no data or checkpoint was downloaded; share URLs were checked with HEAD requests only. The audit is in rewire-bio/rewire-benchmarks#71.

## What changed

The BEND benchmark record (`discovery-benchmark-bend`) had a run guide, run documentation and a run recipe pinned to commit ac6e80c. The audit on 2026-11-17 found three problems with the guide. Upstream fixed the second of them on 2026-11-18. The record is now pinned to 58ad410 and the guide is rewritten. Each correction is a claim on the benchmark that keeps the previous value, in batch `data/omics/bend-recipe-corrections-20261119`:

| Claim | Problem | Whose | Upstream |
| --- | --- | --- | --- |
| `bend-recipe-corrections-20261119-missing-dependencies` | requirements.txt lacked lxml, h5py and pysam | upstream | frederikkemarin/BEND#53, filed by a third party in April 2024, still open. Fixed in code by 58ad410 |
| `bend-recipe-corrections-20261119-checkpoint-links` | checkpoint links returned 403, and the configured folder names did not exist on the share | upstream | frederikkemarin/BEND#78, filed by Rewire on 2026-11-18, fixed in PR #79 (merge commit 58ad410) the same day |
| `bend-recipe-corrections-20261119-gene-finding-download` | the guide downloaded the whole 7.25 GB share for one task | ours | not reported |
| `bend-recipe-corrections-20261119-repin-58ad410` | recipe, guide and documentation moved from ac6e80c to 58ad410 | follows from #78 | |

On the benchmark record:

- `run_guide`: the checkout uses 58ad410. Install and data download are separate steps. The download fetches only the four gene-finding files. Precompute names `task=gene_finding` only. Prerequisites now list curl and wget and the disk needed.
- `run_recipes[0]` (`bend-official`): only the version, sources and locators changed. The three quoted commands are on the same lines at 58ad410.
- `run_documentation`: cites the README and embed.yaml at 58ad410.
- `source_ids`: the four new pinned sources are added. The ac6e80c sources stay.

## Sources

| Source | Artifact SHA-256 |
| --- | --- |
| `project-recipe-bend-58ad4101`, README.md at 58ad410 | d42e3a8990c0a3492dbba665024360f97c82007f9153875cfb4a8048f181ddd4 |
| requirements.txt at ac6e80c | dc072753c5d2dfaa7ae5b8c249a3a317df6fe6b7f5e7996e9048505c4b624496 |
| requirements.txt at 58ad410 | d40d2faabe18b84b53cbb10fa4ce65f9758fad2e9e0a4f0227a585d42870c69c |
| conf/embedding/embed.yaml at 58ad410 | 7ded9f625a78d1336688ba7648f773a12fb6aac3a27edfd672c40f5b740dadc9 |
| commit 58ad410, unified diff | dfb53ed4e656e48e91dc4316ef7f13d97f83dbf2b70f7492766223e47f50b3fd |
| BEND issues #53 and #78, PR #79 | no stable hash; pinned by number, timestamps and quoted text |

## Rulings

1. The task summary for this pass said that the three problems stood as written on rewire-benchmarks#71. The primary sources differ in four places, and the records follow the sources:
   - Commit 58ad410 also added lxml, h5py and pysam to requirements.txt, so problem 1 is fixed in code even though #53 is still open. The guide no longer installs them separately.
   - At 58ad410, embed.yaml points `resnetlm` at `pretrained_models/convnet/` and `awdlstm` at `pretrained_models/awd_lstm/`, and `download_bend.py` uses share aNQa0Oz2lY. The rename loop in the #71 recipe, which copied checkpoints into `resnetlm/` and `awdlstm/`, would now put them where the configuration does not look, so it was dropped.
   - `download_model('convnet')` with its default `destination_dir` writes the files directly into `./pretrained_models/`. The follow-up on #71 says to call it that way. The guide relies on the embedders' automatic download, which passes the model directory, and names `destination_dir` for anyone fetching ahead of time.
   - #78 was opened on 2026-11-18, not 17 November. The 403 checks behind it were made on 2026-11-17.
2. #53 was not filed by Rewire. Its claim says so. Its `reported_on` is the date the third party filed it.
3. The two sizes come from different measurements. 7,251,859,341 bytes is the f6hdp1zTzh share listing on 2026-11-17. 3,509,054,493 bytes is the sum of HEAD Content-Length values for the four gene-finding files on aNQa0Oz2lY on 2026-11-19. Both shares served the same four files at the same sizes on 2026-11-19.
4. `run_guide.review` keeps `date` (2026-11-19), because the run guide schema (`shared/omics/run-guide.ts`) is strict and requires it. Every new claim and source review uses `reviewed_at`.

## Limits

The guide status stays `source_reviewed_not_executed`. Upstream says PR #79 was tested on a small synthetic gene-finding example on CPU, not on the full benchmark or a GPU. The new source bytes are not yet in the archive object store; the next whole-store `npm run archive -- fetch` pass picks them up. `scripts/omics/recipes/projects.ts` still pins BEND at ac6e80c. That generator's inputs (`data/omics/reviewed/run-recipes/records.jsonl` and `overlays.json`) are no longer in the repository, so it was not rerun.
