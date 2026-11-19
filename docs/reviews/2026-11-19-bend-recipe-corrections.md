# BEND run guide corrections, 2026-11-19

Reviewer: Claude agent, automated. No human review is claimed. Nothing was installed or run, and no data or checkpoint was downloaded; share URLs were checked with HEAD requests only. The audit is in rewire-bio/rewire-benchmarks#71.

## What changed

The BEND benchmark record (`discovery-benchmark-bend`) had a run guide, run documentation and a run recipe pinned to commit ac6e80c. The audit on 2026-11-17 found three problems with the guide, and a later check found a fourth (the precompute step ran a second task). Upstream fixed both upstream problems on 2026-11-18. The record is now pinned to 58ad410 and the guide is corrected. Each correction is a claim on the benchmark that keeps the previous value, in batch `data/omics/bend-recipe-corrections-20261119`:

| Claim | Field | Problem | Whose | Upstream |
| --- | --- | --- | --- | --- |
| `bend-recipe-corrections-20261119-guide-checkout` | `attributes.run_guide.steps.0.shell` | checkout moved from ac6e80c to 58ad410 | follows from #53 and #78 | fixed in PR #79, merge commit 58ad410 |
| `bend-recipe-corrections-20261119-gene-finding-download` | `attributes.run_guide.steps.1.shell` | the guide downloaded the whole 7.25 GB share for one task | ours | not reported |
| `bend-recipe-corrections-20261119-missing-dependencies` | `attributes.run_guide.steps.1.explanation` | requirements.txt lacked lxml, h5py and pysam | upstream | frederikkemarin/BEND#53, filed by a third party in April 2024, still open; fixed in code by 58ad410 |
| `bend-recipe-corrections-20261119-precompute-task` | `attributes.run_guide.steps.2.shell` | precompute also ran enhancer_annotation, whose inputs the guide no longer fetches | ours | not reported |
| `bend-recipe-corrections-20261119-checkpoint-links` | `attributes.run_guide.steps.2.explanation` | checkpoint links returned 403, and the configured folder names did not exist on the share | upstream | frederikkemarin/BEND#78, filed by Rewire on 2026-11-18, fixed in PR #79 the same day |
| `bend-recipe-corrections-20261119-repin-58ad410` | `attributes.run_recipes.0.version` | recipe moved from ac6e80c to 58ad410 | follows from #78 | |

Each claim's `previous_value` equals the origin/main field exactly, and each `value` equals the working-tree field exactly. The guide keeps its four steps in the same order (checkout; install and download; precompute; train), so every step index means the same step before and after. This was checked by script against origin/main, along with a second check that every step whose `shell` changed has a claim on it. Claims cover each changed command and each correction. A leaf-by-leaf diff of the record against origin/main lists what changed without a claim of its own:

- Citations and locators that follow from the repin: `source_ids`, `run_guide.source_ids`, each step's `source_ids` and `source_locator`, and in `run_recipes.0` and `run_documentation` the `source_ids` and `source_locator` of the recipe and of each instruction.
- Wording that follows from the corrections: `run_guide.summary`, `run_documentation.summary`, `steps.0.explanation` (names 58ad410), `steps.1.title` (gene-finding data), `steps.2.title` (gene-finding embeddings), `prerequisites.1` to `prerequisites.3` (curl and wget, disk, data host) and the new `limitations.3`, which says the download and the task list are Rewire's changes.
- `run_guide.review.date`, now 2026-11-19.

The diff was run on the committed claim shards, not only on `batch.jsonl`.

`upstream_response` quotes the maintainer's comment on #78 from "Thank you" to its last sentence (only the greeting "Hi," is left out) and the one comment on PR #79, whose closing emoji is described rather than reproduced. #53 has no maintainer reply; its two user comments are quoted.

On the benchmark record:

- `run_guide`: the checkout uses 58ad410. The install step keeps its two pip commands and fetches only the four gene-finding files with curl, in place of `python scripts/download_bend.py`. Precompute names `task=gene_finding` only and relies on the embedders' automatic checkpoint download, which the maintainer tested; its explanation names `download_model` with `destination_dir` for anyone fetching ahead of time. Prerequisites list curl and wget and about 3.7 GB of disk (3,509,054,493 bytes of inputs and 166,351,422 bytes for the two `pytorch_model.bin` files).
- `run_recipes[0]` (`bend-official`): only the version, sources and locators changed. The three quoted commands are on the same lines at 58ad410.
- `run_documentation`: cites the README and embed.yaml at 58ad410.
- `source_ids`: the four new pinned sources are added. The ac6e80c sources stay.

`scripts/omics/recipes/projects.ts` now pins BEND at 58ad410 with the README hash of that commit, so a later run of the generator does not revert the recipe. The generator was not rerun; its inputs are no longer in the repository.

## Share IDs

The 2026-11-17 recipe on rewire-benchmarks#71 fetched data and checkpoints from share f6hdp1zTzh. At ac6e80c the share differed by file:

| Where | Share at ac6e80c | At 58ad410 |
| --- | --- | --- |
| `scripts/download_bend.py` | f6hdp1zTzh | aNQa0Oz2lY |
| `download_model` in `bend/utils/download.py` | dbQM0pgSlM (403) | aNQa0Oz2lY |
| README Embedders table, lines 72-73 | eXAmVvbRSW (403) | aNQa0Oz2lY |
| README data links, lines 18 and 48 | aNQa0Oz2lY | unchanged |

So the README already pointed at aNQa0Oz2lY for data at ac6e80c, and the #71 recipe's use of f6hdp1zTzh was Rewire's choice. No store field held a share ID before this change (the old guide called `download_bend.py`), so this has no claim of its own; it is recorded in the rationales of the gene-finding-download and checkpoint-links claims.

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
4. An earlier draft of this batch split install and download into two steps. That shifted the later step indices, so two claims paired a new index with the old step's text and the precompute change had no claim. The download was folded back into step 1 to keep the indices, and the precompute and checkout changes got claims of their own.
5. `run_guide.review` keeps `date` (2026-11-19), because the run guide schema (`shared/omics/run-guide.ts`) is strict and requires it. Every new claim and source review uses `reviewed_at`.

## Limits

The guide status stays `source_reviewed_not_executed`. Upstream says PR #79 was tested on a small synthetic gene-finding example on CPU, not on the full benchmark or a GPU. The new source bytes are not yet in the archive object store; the next whole-store `npm run archive -- fetch` pass picks them up. The benchmark page does not yet show correction claims next to the run guide: the evidence table attaches claims to flattened fields, and run guide steps are added as rows of their own without a claim lookup. The claims are in the store and the KG.
