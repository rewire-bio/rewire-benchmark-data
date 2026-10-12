# Review: use-case-coverage-model-execution-20261011-clair3gpu, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-exec`, independent of the extractor `uc-execution`. No human review claimed. Source transcription is not reproduction. Full review: `docs/reviews/use-cases/diagnostic-genomics-model-execution-2026-10-12.md`.

## Reviewer's verdict for this batch (verbatim)

| Batch or item | Verdict |
| --- | --- |
| `use-case-coverage-model-execution-20261011-clair3gpu` | Approved with corrections (A1, A2, C1 to C6). Source concern C2 withholds its five judgements |

All edits are to records in the batch folders before `records -- add`. After applying them, regenerate `claims.csv` and `coverage.json` from `batch.jsonl` as the extraction scripts do.

### All batches

A1. None of the five sources states how many runs sit behind each printed value. The batches say "one run" or "single runs", which is an inference. Replace these exact JSON string values (whole value unless marked "substring") wherever they occur in the five `batch.jsonl` files:

| Find | Replace with |
| --- | --- |
| `One run per configuration and coverage; no repeats or variance are printed.` | `One value per configuration and coverage is printed; the number of runs behind it is not stated and no spread is printed.` |
| `One run per caller and coverage; hardware not stated in the table` | `One value per caller and coverage; number of runs and hardware not stated in the table` |
| `One run per depth and hardware configuration; no repeats.` | `One value per depth and hardware configuration is printed; the number of runs behind it is not stated and no spread is printed.` |
| `Five average depths, one run each` | `Five average depths, one value each; number of runs not stated` |
| `One run per depth; no fixed hardware budget, hardware is part of each configuration` | `Number of runs not stated; no fixed hardware budget, hardware is part of each configuration` |
| `One run per depth` | `One value per depth; number of runs not stated` |
| `One run per pipeline; no repeats or variance. The Sentieon software version is not stated for Table 2.` | `One value per pipeline is printed; the number of runs behind it is not stated and no spread is printed. The Sentieon software version is not stated for Table 2.` |
| `One run per pipeline` | `One value per pipeline; number of runs not stated` |
| `One run` | `One value; number of runs not stated` |
| substring `the runs are not repeated` | `the number of runs is not stated` |
| substring `single runs and runtimes that differ` | `an unstated number of runs and runtimes that differ` |
| substring `hardware not stated in the table, single runs.` | `hardware not stated in the table, an unstated number of runs.` |
| substring `one unnamed sample per depth, single runs and author-reported GPU rows` | `one unnamed sample per depth, an unstated number of runs per value and author-reported GPU rows` |
| substring `vendor-reported single runs on an unnamed sample, different inputs per pipeline and no licence cost` | `vendor-reported values with an unstated number of runs, an unnamed sample, different inputs per pipeline, no stated software version and no licence cost` |

The substring rows apply to both the `description` and `attributes.rationale` of the affected judgement claims.

A2. Review fields, on every result and every non-judgement claim in the five batches: set `status` to `source_checked` and replace `attributes.review` with

```json
{
  "method": <per batch, below>,
  "method_note": <per batch, below>,
  "reviewer": ["claude"],
  "reviewer_note": "Claude (Opus 5.5) review agent reviewer-exec, independent of the extractor uc-execution; no human review claimed",
  "reviewed_at": "2026-10-12T07:50:32Z",
  "artifact_sha256": <the result's source artifact_sha256>,
  "retrieval_url": <that source's artifact_url>,
  "note": "Independent review 2026-10-12: printed value, numeric value, metric, qualifier, unit, direction, uncertainty, locator and configuration and protocol identity match the source. Transcribed, not reproduced."
}
```

| Batch | `method` | `method_note` |
| --- | --- | --- |
| clair3gpu | `["source-hash-verification", "pdf-text-parse", "rendered-source-visual-check", "independent-cell-check"]` | `Re-downloaded the Europe PMC supplementaryFiles zip and matched the PDF member's SHA-256. Supplementary Table 1 parsed from pdftotext -layout with a separate review script; Supplementary Tables 2 and 3 read in full by the reviewer from the embedded image and a 250 dpi render of page 3, written down independently and compared cell by cell (350 cells). Article XML re-downloaded and matched.` |
| moderngena | `["source-hash-verification", "pdf-text-parse", "rendered-source-visual-check", "independent-cell-check"]` | `Archived PDF matched the pinned SHA-256; a fresh bioRxiv download had the same text-layer SHA-256. Appendix B Table 2 parsed from pdftotext -layout with a separate review script (108 cells, 16 dashes) and every row read against a 200 dpi render of page 9.` |
| fp8genomeocean | same as moderngena | `Archived PDF matched the pinned SHA-256; a fresh bioRxiv download had the same text-layer SHA-256. Tables 3 and 4 parsed from pdftotext -layout with a separate review script, including every ± value, and every cell read against a 170 dpi render of page 8.` |
| genepi | `["source-hash-verification", "pdf-text-parse", "rendered-source-visual-check", "independent-cell-check"]` | `Re-downloaded the Europe PMC supplementaryFiles zip and matched the PDF member's SHA-256; article XML re-downloaded and matched. Table S1 parsed from pdftotext -layout with a separate review script, minutes recomputed from the printed hours and minutes, and every cell read against a 150 dpi render of page 7.` |
| dnascopehybrid | `["source-hash-verification", "deterministic-table-parse", "independent-cell-check"]` | `Re-downloaded the Europe PMC article XML and matched its SHA-256. Table 2 parsed from the XML table cells with a separate review script and every cell read in the parsed output.` |

On the ten judgement claims: set `status` to `source_checked`, add `reviewed_evaluations` (lists under "Judgement review"), and replace `attributes.review` with `{"method": ["source-hash-verification", "independent-cell-check", "scope-review"], "reviewer": ["claude"], "reviewer_note": "Claude (Opus 5.5) research agent uc-execution extracted and drafted; Claude (Opus 5.5) review agent reviewer-exec checked every value and this judgement against the pinned sources", "reviewed_at": "2026-10-12T07:50:32Z", "note": "Bounded primary-source transcription with independent cell check and relevance review. No execution, reproduction, qualified human scientific review or clinical validation."}`, then record pins with `npm run use-cases:repin`. Set every other new record (sources, models, methods, configurations, datasets, protocols, evaluations) to `source_checked`.

### clair3gpu (Zheng et al. 2026)

C1. Duplicate. `origin/main` now holds `somatic-clairs-to-20261011-method-clair3` (kind `method`, name `Clair3`, `source_checked`), merged with the oncology pass after this extraction. Delete the record `model-execution-20261011-model-clair3` from `batch.jsonl`, and in the `configuration_of` link of these three configurations change the target to `somatic-clairs-to-20261011-method-clair3`:
`model-execution-20261011-config-zheng2026-clair3-1-2-0-gpu`, `model-execution-20261011-config-zheng2026-clair3-accuracy`, `model-execution-20261011-config-zheng2026-clair3-pileup-accuracy`. Move the ID from the new to the reused list in `coverage.json`. `model-execution-20261011-model-deepvariant` has no counterpart on `origin/main` or any open lit branch; keep it.

C2. Source concern. Append to `attributes.evidence_concerns` of `model-execution-20261011-source-zheng2026-clair3-supplement`:

```json
{
  "source_id": "model-execution-20261011-source-zheng2026-clair3-supplement",
  "message": "Supplementary Table 2 runtimes differ from the article's Results for what appear to be the same HG003 comparisons. ONT at 30x and 50x: Clair3 GPU 17 and 20 minutes in the table, 16 and 15 in Results 3.1.1; DeepVariant GPU 48 and 82 in the table, 106 to 128 in the text. PacBio Revio at 30x and 50x: Clair3 GPU 12 and 12 in the table, 23 and 21 in Results 3.1.2; DeepVariant GPU 40 and 53 in the table, 93 and 118 in the text. The table's Clair3 PacBio runtimes equal the macOS M3 Ultra runtime in Results 3.1.3, not the Linux RTX 4090 runtimes. The table and the Supplementary Notes commands give DeepVariant v1.10-beta; Results 3.1 say v1.8. Supplementary Table 3 DeepVariant ONT SNP precision, recall and F1 at 10x and 20x (97.58%, 92.35%, 94.89% and 99.32%, 99.02%, 99.17%) differ from Results 3.2 (97.34%, 92.17%, 94.68% and 98.75%, 98.79%, 98.79%), while the Clair3 values agree. Results 3.2 cite Supplementary Table 2 for the HG001 to HG007 comparison, which is Supplementary Table 4. The hardware, DeepVariant version and runs behind Supplementary Tables 2 and 3 are therefore uncertain. Supplementary Table 1 agrees with Results 3.1.4 except WhatsHap ONT 30x (723 seconds in the table, 724 in the text). Table values are recorded; text values are not.",
  "source_locator": "Supplementary Tables 1 to 3 (pages 2 and 3) versus article Results 3.1.1 to 3.1.4 and 3.2",
  "artifact_sha256": "feec482c5befbb44f93b82782b200a3abebaf7d81a0aad81e28de191be1523d9",
  "reviewed_at": "2026-10-12T07:50:32Z",
  "review_method": "automated-source-review"
}
```

C3. Memory measurement is stated. The article's Methods ("Computational performance") say "We used the GNU time command to benchmark the runtime and memory usage."
- In `model-execution-20261011-protocol-zheng2026-hg003-resource-ont` and `-resource-pacbio`: remove `missing_metadata.memory_measurement` (delete `missing_metadata` if it becomes empty) and add `attributes.memory_measurement`: `GNU time (article Methods 'Computational performance')`.
- In those two protocols and their two judgement claims, replace the limitation `How peak and average memory and data movement were measured is not stated.` with `The Methods say runtime and memory were measured with the GNU time command, which reports host process memory, not GPU memory; how data movement was measured is not stated.`
- In the 40 memory results (metrics `peak-memory` and `mean-memory`), replace `unit_detail` `MB as printed; the table does not say whether host or GPU memory` with `MB as printed; the Methods say memory was measured with GNU time (host process memory)`.

C4. Hardware is stated in the Methods. In both GPU configurations (`model-execution-20261011-config-zheng2026-clair3-1-2-0-gpu`, `model-execution-20261011-config-zheng2026-deepvariant-1-10-beta-gpu`) replace `hardware.description` with
`Not stated in Supplementary Table 2. Methods 'Computational performance' say the GPU version was benchmarked with other callers on an NVIDIA GeForce RTX 4090 with two 12-core Intel Xeon Silver 4116 processors; Results 3.1.1 and 3.1.2 give the Figure 2a runs as a Linux system with one RTX 4090 and 32 CPU threads; Supplementary Figure 2 says Clair3 used one NVIDIA 4090 GPU.`
In the two resource protocols and their two judgements replace the limitation `Hardware for Supplementary Table 2 is not stated; Results 3.1 describe the Figure 2a runs on one RTX 4090 GPU with 32 CPU threads.` with `Hardware is not stated in Supplementary Table 2; the Methods give an NVIDIA GeForce RTX 4090 with two 12-core Intel Xeon Silver 4116 processors for the GPU benchmarks, and Results 3.1 describe the Figure 2a runs on one RTX 4090 with 32 CPU threads.` In the stage-runtime protocol and its judgement replace `Hardware is not stated in the table.` with `Hardware is not stated in the table; the Methods give an NVIDIA GeForce RTX 4090 with two 12-core Intel Xeon Silver 4116 processors for the GPU benchmarks.`

C5. In `model-execution-20261011-protocol-zheng2026-hg003-resource-pacbio` and `use-case-mapping-model-execution-20261011-zheng2026-hg003-resource-pacbio`, append to `limitations`: `Supplementary Table 2 prints 12 minutes for Clair3 at 30x, 40x and 50x, which equals the macOS M3 Ultra runtime in Results 3.1.3 rather than the Linux RTX 4090 runtimes in Results 3.1.2.`

C6. In all five Clair3 protocols and judgements, append to `limitations`: `The source has an unresolved evidence concern (Supplementary Tables 2 and 3 conflict with the Results text); see the source record.`

### Vocabulary

V1. In `:energy-efficiency` (`data/vocab/metric.ttl`), replace `skos:altLabel "tok/W"@en` with `skos:altLabel "performance per watt"@en`; the source's wording belongs in `unit_detail`, where it already is.

## Reviewer's judgement review (verbatim)

Each judgement's endpoint matches its protocol and the use case's inputs (team hardware, required turnaround and throughput) and output (per-sample runtime, cost and resource values for exact configurations); the limitations carry the sources' own caveats after the corrections; none has `excluded_evaluations`. Set `reviewed_evaluations` as follows.

| Judgement | Relevance | Outcome | `reviewed_evaluations` |
| --- | --- | --- | --- |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-resource-ont` | proxy | Holds; withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-1-2-0-gpu-hg003-resource-ont`, `model-execution-20261011-eval-zheng2026-deepvariant-1-10-beta-gpu-hg003-resource-ont` |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-resource-pacbio` | proxy | Holds; withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-1-2-0-gpu-hg003-resource-pacbio`, `model-execution-20261011-eval-zheng2026-deepvariant-1-10-beta-gpu-hg003-resource-pacbio` |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-clair3-stage-runtime` | proxy | Holds; withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-1-2-0-gpu-hg003-clair3-stage-runtime-ont`, `model-execution-20261011-eval-zheng2026-clair3-1-2-0-gpu-hg003-clair3-stage-runtime-pacbio` |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-accuracy-ont` | proxy | Holds (accuracy beside resource use is a named gap); withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-accuracy-hg003-accuracy-ont`, `model-execution-20261011-eval-zheng2026-clair3-pileup-accuracy-hg003-accuracy-ont`, `model-execution-20261011-eval-zheng2026-deepvariant-accuracy-hg003-accuracy-ont` |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-accuracy-pacbio` | proxy | Holds; withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-accuracy-hg003-accuracy-pacbio`, `model-execution-20261011-eval-zheng2026-clair3-pileup-accuracy-hg003-accuracy-pacbio`, `model-execution-20261011-eval-zheng2026-deepvariant-accuracy-hg003-accuracy-pacbio` |

## Reviewer's answers to the collector's questions (verbatim)

1. Clair3, text against tables. Yes, a source-level concern is needed (C2). The conflict is wider than reported: the Clair3 runtimes also differ (PacBio 12 minutes in the table, 23 and 21 in the text, and 12 equals the macOS figure), and Results 3.2 cross-reference the wrong supplementary table. The comparison the table is meant to support, Clair3 against DeepVariant runtime, changes from about 3 to 4 fold in the table to about 4 to 8 fold in the text, so the values should not support comparison until the authors' intent is known. The concern withholds all five Clair3 judgements; that is the intended effect. Keep `model-execution-20261011-source-zheng2026-clair3` and `-supplement` out of the use case's and the summary's `source_ids`, because a concerned source there withholds every judgement on the use case (`shared/omics/use-cases.ts:601`) and the summary (`:525`).
2. Clair3 image tables. Re-read in full: Table 2 from the embedded raster at native resolution (80 cells) and Table 3 from a 250 dpi render of page 3 (270 cells; its DeepVariant rows are raster, its Clair3 rows vector outlines). My own transcription matches all 350. Table 1 (24 cells) is in the text layer and matches. The `retrieval_note` saying Tables 2 and 3 are raster images is close enough; Table 3 is part raster, part outline.
5. Relevance. All ten levels hold; details under "Judgement review". The Clair3 resource proxies are right, and the hardware is in fact stated in the Methods (C4). GeNePi `direct` holds: per-genome runtime on stated hardware for an exact pipeline version matches the use case's inputs and output, as for the Samarakoon judgements already marked direct; the unnamed sample and unstated run count are carried as limitations.
6. Origin. All correct. Author overlap checked from the author lists and affiliations: Zheng et al. are the Clair3 group (HKU); Aspidova, Kuratov, Burtsev and Fishman are GENA-LM authors; Yu et al. include Egan and Wang of the DOE Joint Genome Institute, home of GenomeOcean; all six Hu et al. authors are Sentieon employees; Marangoni et al. built GeNePi, whose PB_germ module is the configuration evaluated, so `author_reported` for the GPU rows is the right conservative reading even though Parabricks itself is NVIDIA's. DeepVariant, DNABERT-2, NTv2 and the CPU GATK baseline are `independent_paper`.
7. Vocabulary. Approved: `cpu-time`, `data-io-volume`, `energy-efficiency` (with V1), `maximum-batch-size`, `mean-memory`, `power-draw`, `throughput-change`, `megabyte`, `watt`, `sample-per-joule`. None respells an existing concept. `throughput-change` is a signed percent change, not the existing `speedup` ratio; storing "−24.9%" as a speedup would misstate it.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/build.py`), as the reviewer specified, before the batch was added to the store; `claims.csv` was regenerated with the batch. Then `extract/apply_review.py` recorded the review on every record.

1. A1: every "one run" and "single runs" value replaced with the reviewer's wording in the protocols, evaluations and judgements.
2. A2: review block from the review on every result and on the descriptive claim; judgement review block and reviewed_evaluations on the five judgements; every record source_checked.
3. C1: model-execution-20261011-model-clair3 deleted; the three Clair3 configurations now link configuration_of to somatic-clairs-to-20261011-method-clair3; coverage.json lists it as reused.
4. C2: the reviewer's evidence concern appended to model-execution-20261011-source-zheng2026-clair3-supplement. It withholds the five judgements.
5. C3: memory_measurement set on the two resource protocols (missing_metadata removed); memory limitation replaced in those protocols and judgements; unit_detail replaced on the 40 memory results.
6. C4: hardware description replaced on the two GPU configurations; hardware limitations replaced in the resource and stage-runtime protocols and judgements.
7. C5: PacBio 12-minute limitation appended to the PacBio resource protocol and judgement.
8. C6: evidence-concern limitation appended to all five protocols and judgements.
9. V1: :energy-efficiency altLabel changed to "performance per watt" in data/vocab/metric.ttl.

The five judgements are withheld by the source concern on the supplement (C2).

## Records after correction

- claim: 6
- configuration: 5
- dataset: 2
- evaluation: 12
- model: 1
- protocol: 5
- result: 374
- source: 2
