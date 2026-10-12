# Review: diagnostic genomics execution batches, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-exec`, separate from the extracting agent `uc-execution`. No human review is claimed. Nothing was executed or reproduced. I did not edit any record, store file, vocabulary file or batch file; every correction below is for the collector to apply.

Worktree reviewed: `rewire-benchmark-data-lit-uc-execution` (uncommitted batch folders as the source of truth), against `origin/main` at `bba147c` (release 2026-10-12-a3dac44c7353).

## Verdicts

| Batch or item | Verdict |
| --- | --- |
| `use-case-coverage-model-execution-20261011-clair3gpu` | Approved with corrections (A1, A2, C1 to C6). Source concern C2 withholds its five judgements |
| `use-case-coverage-model-execution-20261011-moderngena` | Approved with corrections (A1, A2, M1 to M3). Source concern M1 withholds its judgement |
| `use-case-coverage-model-execution-20261011-fp8genomeocean` | Approved with corrections (A2, Y1, Y2) |
| `use-case-coverage-model-execution-20261011-genepi` | Approved with corrections (A1, A2, G1, G2) |
| `use-case-coverage-model-execution-20261011-dnascopehybrid` | Approved with corrections (A1, A2) |
| New vocabulary in `data/vocab/metric.ttl` and `unit.ttl` (10 concepts) | Approved with one correction (V1) |
| Summary for `use-case-diagnostic-genomics-model-execution` | Approved with the rewritten text below |
| Use-case field changes | Approved with the rewritten text below |

All 540 printed values in the five batches match the pinned sources. No value needs a superseding record. The corrections are to descriptive text, one duplicate record, locators, two source concerns, and wording that states more than the sources do.

## Corrections

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

### moderngena (Aspidova et al. 2026)

M1. Source concern (question 3). Figure 1's axis reads "Inference speed (tokens/s)", so the paper does not state a scale; but the printed values cannot be tokens per second. Append to `attributes.evidence_concerns` of `model-execution-20261011-source-aspidova2026-moderngena`:

```json
{
  "source_id": "model-execution-20261011-source-aspidova2026-moderngena",
  "message": "Appendix B Table 2 and Figure 1 (axis 'Inference speed (tokens/s)') give throughput in tokens/s, but the printed values are inconsistent with the printed batch sizes: ModernGENA base (FA2 + autocast bf16) at L = 256 prints 552.44 tokens/s with a batch of 3,631 sequences (929,536 tokens), about 28 minutes per batch, and ModernGENA base without FA2 at L = 8192 prints 71.15 tokens/s with a batch of 92 (753,664 tokens), about 2.9 hours per batch, against a stated pretraining throughput of 1.33M tokens/s on eight A100 GPUs (Section 3.2.4). The unit or scale of the throughput column is unclear. Batch sizes share the table. Values are recorded as printed.",
  "source_locator": "Appendix B Table 2 (page 9); Figure 1 (page 4); Section 3.2.4",
  "artifact_sha256": "238ab9916d54b419bf31fd79ecf146d654eb6574d3b441aa2043d39632e709fa",
  "reviewed_at": "2026-10-12T07:50:32Z",
  "review_method": "automated-source-review"
}
```

In the protocol and judgement, replace the limitation beginning `The printed tokens/s values are far below what the batch sizes imply` with `The printed tokens/s values are inconsistent with the printed batch sizes and the stated pretraining throughput (1.33M tokens/s on eight A100s, Section 3.2.4); the source carries an evidence concern, and values are kept as printed.` In the judgement `description` and `rationale`, replace `and with a printed throughput scale that needs checking.` with `and with a printed throughput unit that is inconsistent with its batch sizes (source evidence concern).`

M2. Duplicate names. Rename `model-execution-20261011-config-aspidova2026-ntv2-100m` to `NTv2 (100M) on one A100 80 GB (Aspidova et al. 2026)` and `model-execution-20261011-config-aspidova2026-ntv2-250m` to `NTv2 (250M) on one A100 80 GB (Aspidova et al. 2026)`.

M3. Access is not stated in this source for the comparison models. In `model-execution-20261011-config-aspidova2026-dnabert-2`, `-gena-base`, `-gena-large`, `-ntv2-100m` and `-ntv2-250m`, replace `access_reuse` `Public pretrained checkpoint` with `Pretrained checkpoint; access not stated in this source`. Keep it on the four ModernGENA configurations (the paper says they are on Hugging Face).

### fp8genomeocean (Yu et al. 2026)

Y1. The preprint does not say the checkpoints are public. In all nine configurations replace `access_reuse` `Public GenomeOcean checkpoints; benchmarking code at https://github.com/jgi-genomeocean/genomeocean_efficiency (not pinned)` with `Checkpoint release not stated in this source; benchmarking code at https://github.com/jgi-genomeocean/genomeocean_efficiency (not pinned)`.

Y2. The generation protocol copies the embedding protocol's fidelity limitation. In `model-execution-20261011-protocol-yu2026-genomeocean-generation-fp8` and `use-case-mapping-model-execution-20261011-yu2026-genomeocean-generation-fp8` only, replace `Microbial genomes and a metagenomic-binning fidelity check, not human diagnostic sequence; the paper says the fidelity metrics are benchmark-specific (Section 4.4).` with `Microbial genomes (96 GTDB Bacteria sequences) and a perplexity check, not human diagnostic sequence; the paper says perplexity measures sequence-likelihood preservation, not the biological function of generated sequences (Section 4.4).`

### genepi (Marangoni et al. 2026)

G1. Table S1 is on page 7 of the supplementary PDF (printed and physical), not page 8. In the 20 result locators and the matching 20 `claims.csv` rows, replace `Supplementary Table S1 (page 8)` with `Supplementary Table S1 (page 7)`.

G2. In the protocol and its judgement, append to `limitations`: `The article states a 10- to 78-fold average acceleration over CPU (Discussion, citing Figure 2 and Supplementary Figure S11); the Table S1 ratios run from about 10 to 34, so the upper figure comes from runs not in Table S1.`

### dnascopehybrid (Hu et al. 2026)

Only A1 and A2.

### Vocabulary

V1. In `:energy-efficiency` (`data/vocab/metric.ttl`), replace `skos:altLabel "tok/W"@en` with `skos:altLabel "performance per watt"@en`; the source's wording belongs in `unit_detail`, where it already is.

## Answers to the collector's questions

1. Clair3, text against tables. Yes, a source-level concern is needed (C2). The conflict is wider than reported: the Clair3 runtimes also differ (PacBio 12 minutes in the table, 23 and 21 in the text, and 12 equals the macOS figure), and Results 3.2 cross-reference the wrong supplementary table. The comparison the table is meant to support, Clair3 against DeepVariant runtime, changes from about 3 to 4 fold in the table to about 4 to 8 fold in the text, so the values should not support comparison until the authors' intent is known. The concern withholds all five Clair3 judgements; that is the intended effect. Keep `model-execution-20261011-source-zheng2026-clair3` and `-supplement` out of the use case's and the summary's `source_ids`, because a concerned source there withholds every judgement on the use case (`shared/omics/use-cases.ts:601`) and the summary (`:525`).
2. Clair3 image tables. Re-read in full: Table 2 from the embedded raster at native resolution (80 cells) and Table 3 from a 250 dpi render of page 3 (270 cells; its DeepVariant rows are raster, its Clair3 rows vector outlines). My own transcription matches all 350. Table 1 (24 cells) is in the text layer and matches. The `retrieval_note` saying Tables 2 and 3 are raster images is close enough; Table 3 is part raster, part outline.
3. ModernGENA throughput scale. Yes, a source concern (M1). Figure 1's axis also says tokens/s, so there is no stated scale to apply.
4. Token units. Acceptable as done: tokens per second under `inference-throughput` with `sample-per-second` and a `unit_detail` naming input or generated tokens, and tokens per watt under `sample-per-joule`, whose definition already covers tokens. The judgement constraints and the per-protocol qualifiers keep these from being compared with reads per second. No token unit is needed now.
5. Relevance. All ten levels hold; details under "Judgement review". The Clair3 resource proxies are right, and the hardware is in fact stated in the Methods (C4). GeNePi `direct` holds: per-genome runtime on stated hardware for an exact pipeline version matches the use case's inputs and output, as for the Samarakoon judgements already marked direct; the unnamed sample and unstated run count are carried as limitations.
6. Origin. All correct. Author overlap checked from the author lists and affiliations: Zheng et al. are the Clair3 group (HKU); Aspidova, Kuratov, Burtsev and Fishman are GENA-LM authors; Yu et al. include Egan and Wang of the DOE Joint Genome Institute, home of GenomeOcean; all six Hu et al. authors are Sentieon employees; Marangoni et al. built GeNePi, whose PB_germ module is the configuration evaluated, so `author_reported` for the GPU rows is the right conservative reading even though Parabricks itself is NVIDIA's. DeepVariant, DNABERT-2, NTv2 and the CPU GATK baseline are `independent_paper`.
7. Vocabulary. Approved: `cpu-time`, `data-io-volume`, `energy-efficiency` (with V1), `maximum-batch-size`, `mean-memory`, `power-draw`, `throughput-change`, `megabyte`, `watt`, `sample-per-joule`. None respells an existing concept. `throughput-change` is a signed percent change, not the existing `speedup` ratio; storing "−24.9%" as a speedup would misstate it.
8. GenomeOcean checkpoints. The preprint names scales only (100M, 500M, 4B) and gives no Hugging Face revision; leaving the configurations at scale level is correct. Y1 removes the unstated "public" claim.

## Judgement review

Each judgement's endpoint matches its protocol and the use case's inputs (team hardware, required turnaround and throughput) and output (per-sample runtime, cost and resource values for exact configurations); the limitations carry the sources' own caveats after the corrections; none has `excluded_evaluations`. Set `reviewed_evaluations` as follows.

| Judgement | Relevance | Outcome | `reviewed_evaluations` |
| --- | --- | --- | --- |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-resource-ont` | proxy | Holds; withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-1-2-0-gpu-hg003-resource-ont`, `model-execution-20261011-eval-zheng2026-deepvariant-1-10-beta-gpu-hg003-resource-ont` |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-resource-pacbio` | proxy | Holds; withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-1-2-0-gpu-hg003-resource-pacbio`, `model-execution-20261011-eval-zheng2026-deepvariant-1-10-beta-gpu-hg003-resource-pacbio` |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-clair3-stage-runtime` | proxy | Holds; withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-1-2-0-gpu-hg003-clair3-stage-runtime-ont`, `model-execution-20261011-eval-zheng2026-clair3-1-2-0-gpu-hg003-clair3-stage-runtime-pacbio` |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-accuracy-ont` | proxy | Holds (accuracy beside resource use is a named gap); withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-accuracy-hg003-accuracy-ont`, `model-execution-20261011-eval-zheng2026-clair3-pileup-accuracy-hg003-accuracy-ont`, `model-execution-20261011-eval-zheng2026-deepvariant-accuracy-hg003-accuracy-ont` |
| `use-case-mapping-model-execution-20261011-zheng2026-hg003-accuracy-pacbio` | proxy | Holds; withheld by C2 | `model-execution-20261011-eval-zheng2026-clair3-accuracy-hg003-accuracy-pacbio`, `model-execution-20261011-eval-zheng2026-clair3-pileup-accuracy-hg003-accuracy-pacbio`, `model-execution-20261011-eval-zheng2026-deepvariant-accuracy-hg003-accuracy-pacbio` |
| `use-case-mapping-model-execution-20261011-yu2026-genomeocean-embedding-fp8` | proxy | Holds | `model-execution-20261011-eval-yu2026-genomeocean-100m-bf16-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-100m-fp8-weights-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-4b-bf16-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-4b-fp8-weights-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-500m-bf16-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-500m-fp8-weights-embedding` |
| `use-case-mapping-model-execution-20261011-yu2026-genomeocean-generation-fp8` | proxy | Holds with Y2 | `model-execution-20261011-eval-yu2026-genomeocean-4b-bf16-vllm`, `model-execution-20261011-eval-yu2026-genomeocean-4b-fp8-kv-vllm`, `model-execution-20261011-eval-yu2026-genomeocean-4b-w8a8-fp8-kv-vllm` |
| `use-case-mapping-model-execution-20261011-aspidova2026-a100-inference-throughput` | proxy | Holds; withheld by M1 | the nine `model-execution-20261011-eval-aspidova2026-*` evaluations: `-dnabert-2`, `-gena-base`, `-gena-large`, `-moderngena-base`, `-moderngena-base-fa2-bf16`, `-moderngena-large`, `-moderngena-large-fa2-bf16`, `-ntv2-100m`, `-ntv2-250m` |
| `use-case-mapping-model-execution-20261011-marangoni2026-germline-runtime-by-depth` | direct | Holds with A1 and G2 | `model-execution-20261011-eval-marangoni2026-gatk-cpu`, `model-execution-20261011-eval-marangoni2026-parabricks-4-3-0-2xa100`, `model-execution-20261011-eval-marangoni2026-parabricks-4-3-0-2xv100`, `model-execution-20261011-eval-marangoni2026-parabricks-4-3-0-4xa100` |
| `use-case-mapping-model-execution-20261011-hu2026-dnascope-azure-compute` | proxy | Holds with A1; proxy is right because Table 2 has no software version and each pipeline has different inputs | `model-execution-20261011-eval-hu2026-dnascope-hybrid-azure`, `model-execution-20261011-eval-hu2026-dnascope-longread-pb-azure`, `model-execution-20261011-eval-hu2026-dnascope-short-read-azure` |

## Approved summary text

Replace the whole `value` of `use-case-summary-diagnostic-genomics-model-execution` with:

Eight published execution benchmarks are linked, alongside the DRAGEN 4.2 developer total runtime for HG002 (1,838.5 seconds); two are withheld pending source concerns (see the end of this summary). Of the six active benchmarks, five measure conventional variant-calling pipelines and one measures inference of a genomic foundation model on microbial genomes, outside any diagnostic workflow. Only the foundation-model benchmark prints spread over repeated runs (five trials); none reruns a variant-calling pipeline to measure concordance of the calls, none prints variant-calling accuracy in the same table as runtime, and hardware differs within most comparisons, so differences mix software and hardware. On ten WGS samples run by a University of Oslo and Oslo University Hospital group with no declared competing interests (Samarakoon et al. 2025), read mapping plus HaplotypeCaller for NA12878 (47.55x) took 2,317.7 minutes on a CPU-only GATK pipeline, 123.45 minutes with Parabricks on four L4 GPUs, 78.12 on four A100 GPUs, 54.22 on eight H100 GPUs and 60.29 with DRAGEN v4.2. On the same H100 machine, Parabricks DeepVariant took 14.58 minutes for NA12878 with the version the pipeline used (printed 4.1.0-1; Methods say 4.3.0-1) and 16.05 minutes with the updated version (printed 4.3.0-1; Discussion says 4.3.1-1). On one HG002 30x genome on Google Cloud (O'Connell et al. 2023; the authors' employer funded the study and is an NVIDIA, AWS and Google alliance partner), HaplotypeCaller took 38.8 hours and cost 67.9 USD on a 32-vCPU machine and 0.59 hours and 17.5 USD on eight A100 GPUs, while the somatic caller LoFreq cost 8.1 USD on the CPU machine and 19 to 30.1 USD on 2 to 8 A100 GPUs. On Google Cloud machines of similar hourly cost (Franzoso et al. 2025, no declared conflicts), Sentieon DNASeq took 0:14:00 to 0:16:00 per exome at 0.82 to 1.03 USD and 3:00:00 to 3:50:00 per genome at 8.02 to 10.7 USD, and Parabricks Germline on one T4 GPU took 0:10:00 to 0:14:00 per exome at 0.71 to 0.93 USD and 4:06:00 to 4:40:00 per genome at 8.13 to 10.6 USD; costs exclude the Sentieon licence, and two genome runtime cells that cannot be genome runtimes are disputed and left out of these ranges. On human WGS at five read depths on the HPC nodes of a regional genome project (Marangoni et al. 2026; the GeNePi developers, no declared competing interests; one unnamed sample per depth), a 30x genome took 17h with the CPU GATK equivalent and 1h 36m, 42 m and 30m with Parabricks v4.3.0 on two V100, two A100 and four A100 GPUs, and a 100x genome 60h, 6h 30m, 2h 30m and 2h 06m. On one 120-vCPU Azure instance (Hu et al. 2026; all authors employed by Sentieon), DNAscope took 18.9 minutes for 30x Illumina, DNAscope LongRead 41.2 minutes for 30x PacBio HiFi and DNAscope Hybrid 85.8 minutes for 10x PacBio HiFi plus 35x Illumina, at 1.1, 2.5 and 5.2 USD on demand excluding the licence; each pipeline had different input data, so the three are not a ranking. For GenomeOcean on one H100 (Yu et al. 2026; two authors are at the DOE Joint Genome Institute, which develops GenomeOcean; GTDB bacterial genomes; mean and standard deviation over five trials), embedding extraction with the 4B model ran at 21,386 ± 126 input tokens per second with 72.14 GB peak GPU memory in BF16 and 22,401 ± 204 with 67.91 GB with FP8 weights, and generation ran at 1818.79 ± 7.95 generated tokens per second in BF16 and 2169.04 ± 24.30 with FP8 weights, activations and KV cache. No active linked result measures variant-calling accuracy against a truth set; the GenomeOcean ARI values score metagenomic binning against GTDB species labels. The two withheld studies are Zheng et al. 2026 (Clair3 developers; Clair3 and DeepVariant on HG003 long reads), whose supplementary runtimes, DeepVariant version and DeepVariant accuracy differ from its Results text and whose accuracy uses one GIAB sample's v4.2.1 confident regions, which leave out the hardest regions; and Aspidova et al. 2026 (ModernGENA and GENA-LM developers; four DNA language model families on one A100), whose printed tokens per second are far too low for its batch sizes. Apart from the five GenomeOcean trials, each comparison prints one value per sample and set-up on at most ten samples, and costs are list prices at the time of each study.

Set its `source_ids` to the six existing ones plus `model-execution-20261011-source-marangoni2026-genepi`, `model-execution-20261011-source-marangoni2026-genepi-supplement`, `model-execution-20261011-source-hu2026-dnascope-hybrid` and `model-execution-20261011-source-yu2026-fp8-genomeocean`. Do not add the Zheng or Aspidova sources: the summary names them only to say they are withheld, and a concerned source in `source_ids` blocks publication of the summary. Append to its `source_locator`: `; model-execution-20261011-source-marangoni2026-genepi-supplement: Table S1; model-execution-20261011-source-marangoni2026-genepi: Competing interest; model-execution-20261011-source-hu2026-dnascope-hybrid: Table 2, Conflict of interest; model-execution-20261011-source-yu2026-fp8-genomeocean: Tables 3 and 4, author affiliations`. Record a `metadata-correction-*` claim keeping the previous value, update the summary's `review` (reviewer-exec, 2026-10-12), and re-pin it.

Every number checked: each value in the new sentences equals a stored `printed_value` in these batches (GeNePi Table S1 30x and 100x cells, DNAscope total runtime and on-demand cost, GenomeOcean 4B Table 3 throughput and peak VRAM, Table 4 BF16 and B.2 throughput); the retained sentences are copied from the reviewed summary on `origin/main`. It names the author-reported sources, says no active result measures accuracy against a truth set, names the GIAB confident-region limit of the withheld accuracy table, and recommends nothing.

## Approved use-case field changes (`use-case-diagnostic-genomics-model-execution`)

These change pinned fields (`setting`, `decision`, `output`, `exclusions`, `clinical_scope`), so the existing 14 judgements and the summary must be re-pinned in the same change after `records -- change`. The exclusions change is warranted, not a proxy question: the two entries being removed said "none is ingested" and "not measured", and GenomeOcean throughput and peak memory (Yu et al. 2026) are now ingested and active.

`links`: append `assessed_by` for all ten new protocols as the report lists.

`source_ids`: append `model-execution-20261011-source-marangoni2026-genepi`, `model-execution-20261011-source-marangoni2026-genepi-supplement`, `model-execution-20261011-source-hu2026-dnascope-hybrid`, `model-execution-20261011-source-yu2026-fp8-genomeocean`. Not the Zheng or Aspidova sources (see answer 1).

`citation_locators`: append
- `{"source_id": "model-execution-20261011-source-marangoni2026-genepi", "locator": "Results 'Benchmarking'; Discussion; Competing interest"}`
- `{"source_id": "model-execution-20261011-source-marangoni2026-genepi-supplement", "locator": "Supplementary S3.1-S3.2; Table S1 (page 7)"}`
- `{"source_id": "model-execution-20261011-source-hu2026-dnascope-hybrid", "locator": "Results 'Compute resource benchmark'; Table 2; Conflict of interest"}`
- `{"source_id": "model-execution-20261011-source-yu2026-fp8-genomeocean", "locator": "Sections 2.2-2.7; Tables 3 and 4; author affiliations"}`

`setting`:

Published execution benchmarks, each on stated inputs: CPU-only GATK, Parabricks on L4, A100 and H100 GPUs and DRAGEN v4.2 on ten germline WGS samples (Samarakoon et al. 2025); two germline and four somatic callers on CPU and 2, 4 and 8 GPU cloud and DGX machines on one HG002 30x genome (O'Connell et al. 2023); Sentieon DNASeq and Parabricks Germline on Google Cloud machines of similar hourly cost, five exomes and five genomes (Franzoso et al. 2025); the DRAGEN 4.2 developer total runtime for HG002, 1,838.5 seconds on one hardware configuration and 5,521.21 seconds on an AWS f1.4xlarge configuration, whose stage times cannot be summed because of concurrency; Parabricks v4.3.0 on V100 and A100 nodes against the CPU GATK equivalent at five read depths of human WGS (Marangoni et al. 2026); three Sentieon DNAscope pipelines on one Azure instance (Hu et al. 2026); and GenomeOcean inference in BF16 and FP8 on one H100 with microbial genomes (Yu et al. 2026). Two further linked studies, Clair3 and DeepVariant on HG003 long reads (Zheng et al. 2026) and DNA language model inference on one A100 (Aspidova et al. 2026), are withheld pending source concerns. Hardware differs within most comparisons, so differences mix software and hardware.

`decision`:

Compare published per-sample runtime and cost of CPU, GPU and DRAGEN server execution set-ups that resemble the team's hardware and sequencing type when budgeting a workflow; most are conventional variant-calling pipelines, the one active foundation-model inference benchmark is outside any diagnostic workflow, and none measures run-to-run concordance of variant calls.

`output`:

Sourced per-sample runtime, cost, speedup, cost-saving, throughput and peak-memory values for exact pipeline, model, version and hardware configurations, with the limits of each comparison; no foundation-model execution benchmark inside a diagnostic workflow, no reproducibility measurement and no clinical turnaround claim.

`clinical_scope`:

Clinical applicability is not established: the linked evidence is published runtime, cost and resource use of conventional variant-calling pipelines on a few samples and one foundation-model inference benchmark on microbial genomes, not a foundation-model execution benchmark inside a diagnostic workflow, a reproducibility study or a clinical validation.

`exclusions` (whole list):

1. Foundation-model execution inside a diagnostic workflow on human data (none found in the 2026-10-11 pass)
2. Clinical-reporting turnaround time

`evidence_gaps` (whole list; entries 6 and 7 are the existing last two, unchanged):

1. Measured peak memory is printed only for GenomeOcean inference on one H100 (Yu et al. 2026); no active linked variant-calling study prints it (Samarakoon et al. 2025 and Franzoso et al. 2025 show memory use only in figures), and the Clair3 and DeepVariant memory table (Zheng et al. 2026) is withheld.
2. No linked study reruns the same pipeline on the same input and prints concordance of the calls, so run-to-run reproducibility of variant calls is not measured; Yu et al. 2026 print spread over five trials of throughput only, Samarakoon et al. 2025 compare Parabricks on two A100 clusters only in a figure, and O'Connell et al. 2023 repeated DGX runs but print only the final run.
3. No active linked study reports variant-calling accuracy in the same printed table as runtime; Samarakoon et al. 2025 show accuracy and CPU concordance in Figure 5 only, and the Clair3 and DeepVariant accuracy table (Zheng et al. 2026) is withheld and not stated to come from the same runs as its runtime table.
4. The one active foundation-model execution benchmark uses microbial genomes; none measures a genomic foundation model inside a diagnostic workflow on human data, and the four-family A100 throughput table (Aspidova et al. 2026) is withheld because its printed tokens per second are inconsistent with its batch sizes.
5. Marangoni et al. 2026, Hu et al. 2026 and Zheng et al. 2026 do not state how many runs lie behind each printed runtime.
6. Costs are cloud list prices or authors' estimates at the time of each study and exclude storage and software licences unless stated.
7. A separate ~2-hour joint-aggregation figure over 3,202 genomes at concurrency 200 is a different operation and is not assigned to this single-sample runtime.

## Checks run and outcomes

Sources and hashes.
- Europe PMC full-text XML re-downloaded for PMC13141153 (Zheng), PMC12813096 (Hu) and PMC12832024 (Marangoni): SHA-256 `99ef4db5...a965`, `b138dd89...b6c859`, `6251ae29...64e6`, all equal to the source records. The archived `.xml.gz` copies decompress to the same bytes and their gzip hashes equal `sources.md`.
- Europe PMC supplementaryFiles zips re-downloaded and unpacked: `btag181_supplementary_data.pdf` SHA-256 `feec482c...23d9` and `genepi_supplinfo_rev_bbag001.pdf` `afa166a3...e1bb9`, both equal to the source records. The zip wrappers themselves differ from the hashes in `retrieval_note` on each request (my downloads: `e2cd2ba2...` and `412a6bb1...`); the PDF members are stable, so the source hashes hold. The `sources.md` statement that Europe PMC "serves the same bytes on every request" is true of the PDF members only.
- bioRxiv PDFs: the archived `aspidova2026-preprint-v1.pdf.gz` and `yu2026-preprint-v1.pdf.gz` decompress to `238ab991...09fa` and `ca54817d...a076`, equal to the source records. Fresh downloads on 2026-10-12 had different bytes (download stamping) but `pdftotext -layout` text SHA-256 `ebaf0541...4b4b` and `bec6e695...1453501`, equal to the recorded text-layer hashes.

Values (my own parsers in the scratchpad; the collector's `extract/` scripts were not run or imported).

| Batch | Automated comparison | By hand against the rendered table | Outcome |
| --- | --- | --- | --- |
| clair3gpu | Supplementary Table 1 from the text layer: 24 of 24 (totals also re-added: pileup + LongPhase + full-alignment + workflow control equals the total to within 1 s) | Supplementary Table 2: all 80 cells; Supplementary Table 3: all 270 cells; transcribed independently and compared by script | 374 of 374 match: printed value, numeric value, caller-to-configuration, platform, coverage, metric and column |
| moderngena | Appendix B Table 2: 108 cells parsed (92 numeric, 16 dashes); 92 of 92 match, metric by column, length in qualifier | All nine rows read against the page 9 render | 92 of 92 match; no cell missed |
| fp8genomeocean | Tables 3 and 4: 33 of 33 match, including every ± value against `uncertainty.value`; change percentages recomputed from the means (−24.9%, −11.1%, +4.7%); efficiency equals throughput over power | All 33 against the page 8 render | 33 of 33 match; the three BF16 change cells are dashes, so 33 is complete |
| genepi | Table S1: 20 of 20, minutes recomputed from printed hours and minutes | All 20 against the page 7 render | 20 of 20 match; locator page wrong (G1) |
| dnascopehybrid | Table 2 from XML cells: 21 of 21 | All 21 read in the parsed XML | 21 of 21 match |

Stratified sample: every batch except moderngena has fewer than 40 values, so every value was checked by hand; for clair3gpu all 350 image cells and for moderngena all 92 cells were checked by hand, covering every table and every model or configuration.

Mapping checks: metric, qualifier, direction, unit and `unit_detail` read on every result. Uncertainty: Yu standard deviations with n = 5 trials (seeds 42 to 46, Section 2.7) and n = 96 sequences for perplexity match the captions; ModernGENA is a mean over 10 runs with no spread, recorded as missing. Denominators: none applicable. Datasets and splits: Clair3 HG003 ONT giab-2025.01 and PacBio Revio 2022Q4 with GIAB v4.2.1 truth and hap.py 0.3.12 vcfeval PASS-only match the Supplementary Notes; GenomeOcean GTDB pool of 50 genomes and 96 sequences match Sections 2.5 and 2.7; GeNePi and Hu samples are unnamed as recorded. Problems found: memory measurement and hardware stated in the Clair3 Methods but recorded as unstated (C3, C4); run counts inferred everywhere (A1); generation limitation copied from embedding (Y2); access stated without support (M3, Y1).

Origin and author overlap: checked from each paper's author list, affiliations and competing-interest or conflict statement; all 37 evaluation origins correct (answer 6).

Duplicates: all seven reused IDs exist on `origin/main`. Searched `origin/main` and every local and remote `claude/lit-20261011-*` branch plus the six other `../rewire-benchmark-data-lit-*` worktrees for the five DOIs and PMCIDs and for Clair3, DeepVariant, DNAscope, Sentieon, ModernGENA and GenomeOcean model, method and source IDs. Found one duplicate, the Clair3 method (C1). The DOIs bbag001 and btag181 appear only as unopened leads in `use-case-coverage-model-execution-20261009/coverage.json`. `discovery-model-dnabert-2` is the right DNABERT-2 record to reuse (29 configurations link it; `catalog-model-dnabert-2` is a separate existing duplicate outside this review).

Scope: all five sources are in scope (genomics lane; execution resources for germline variant calling and genomic foundation models). Clair3 Supplementary Tables 4 to 6 were left out with a stated reason (no execution resources); I agree.

Not run: `npm test`, `npm run typecheck`, `npm run build` and `kg:shapes`, because I made no edits; the collector must run them after applying the corrections. The collector's report says the batches passed shape and record validation in a scratch copy before these corrections.
