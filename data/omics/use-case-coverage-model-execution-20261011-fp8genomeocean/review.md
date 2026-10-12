# Review: use-case-coverage-model-execution-20261011-fp8genomeocean, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-exec`, independent of the extractor `uc-execution`. No human review claimed. Source transcription is not reproduction. Full review: `docs/reviews/use-cases/diagnostic-genomics-model-execution-2026-10-12.md`.

## Reviewer's verdict for this batch (verbatim)

| Batch or item | Verdict |
| --- | --- |
| `use-case-coverage-model-execution-20261011-fp8genomeocean` | Approved with corrections (A2, Y1, Y2) |

All edits are to records in the batch folders before `records -- add`. After applying them, regenerate `claims.csv` and `coverage.json` from `batch.jsonl` as the extraction scripts do.

### All batches

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

### fp8genomeocean (Yu et al. 2026)

Y1. The preprint does not say the checkpoints are public. In all nine configurations replace `access_reuse` `Public GenomeOcean checkpoints; benchmarking code at https://github.com/jgi-genomeocean/genomeocean_efficiency (not pinned)` with `Checkpoint release not stated in this source; benchmarking code at https://github.com/jgi-genomeocean/genomeocean_efficiency (not pinned)`.

Y2. The generation protocol copies the embedding protocol's fidelity limitation. In `model-execution-20261011-protocol-yu2026-genomeocean-generation-fp8` and `use-case-mapping-model-execution-20261011-yu2026-genomeocean-generation-fp8` only, replace `Microbial genomes and a metagenomic-binning fidelity check, not human diagnostic sequence; the paper says the fidelity metrics are benchmark-specific (Section 4.4).` with `Microbial genomes (96 GTDB Bacteria sequences) and a perplexity check, not human diagnostic sequence; the paper says perplexity measures sequence-likelihood preservation, not the biological function of generated sequences (Section 4.4).`

## Reviewer's judgement review (verbatim)

Each judgement's endpoint matches its protocol and the use case's inputs (team hardware, required turnaround and throughput) and output (per-sample runtime, cost and resource values for exact configurations); the limitations carry the sources' own caveats after the corrections; none has `excluded_evaluations`. Set `reviewed_evaluations` as follows.

| Judgement | Relevance | Outcome | `reviewed_evaluations` |
| --- | --- | --- | --- |
| `use-case-mapping-model-execution-20261011-yu2026-genomeocean-embedding-fp8` | proxy | Holds | `model-execution-20261011-eval-yu2026-genomeocean-100m-bf16-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-100m-fp8-weights-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-4b-bf16-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-4b-fp8-weights-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-500m-bf16-embedding`, `model-execution-20261011-eval-yu2026-genomeocean-500m-fp8-weights-embedding` |
| `use-case-mapping-model-execution-20261011-yu2026-genomeocean-generation-fp8` | proxy | Holds with Y2 | `model-execution-20261011-eval-yu2026-genomeocean-4b-bf16-vllm`, `model-execution-20261011-eval-yu2026-genomeocean-4b-fp8-kv-vllm`, `model-execution-20261011-eval-yu2026-genomeocean-4b-w8a8-fp8-kv-vllm` |

## Reviewer's answers to the collector's questions (verbatim)

4. Token units. Acceptable as done: tokens per second under `inference-throughput` with `sample-per-second` and a `unit_detail` naming input or generated tokens, and tokens per watt under `sample-per-joule`, whose definition already covers tokens. The judgement constraints and the per-protocol qualifiers keep these from being compared with reads per second. No token unit is needed now.
6. Origin. All correct. Author overlap checked from the author lists and affiliations: Zheng et al. are the Clair3 group (HKU); Aspidova, Kuratov, Burtsev and Fishman are GENA-LM authors; Yu et al. include Egan and Wang of the DOE Joint Genome Institute, home of GenomeOcean; all six Hu et al. authors are Sentieon employees; Marangoni et al. built GeNePi, whose PB_germ module is the configuration evaluated, so `author_reported` for the GPU rows is the right conservative reading even though Parabricks itself is NVIDIA's. DeepVariant, DNABERT-2, NTv2 and the CPU GATK baseline are `independent_paper`.
8. GenomeOcean checkpoints. The preprint names scales only (100M, 500M, 4B) and gives no Hugging Face revision; leaving the configurations at scale level is correct. Y1 removes the unstated "public" claim.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/build.py`), as the reviewer specified, before the batch was added to the store; `claims.csv` was regenerated with the batch. Then `extract/apply_review.py` recorded the review on every record.

1. A2: review block from the review on every result; judgement review block and reviewed_evaluations on the two judgements; every record source_checked.
2. Y1: access_reuse on all nine configurations replaced with the reviewer's text.
3. Y2: fidelity limitation replaced in the generation protocol and judgement only.

## Records after correction

- claim: 2
- configuration: 9
- dataset: 2
- evaluation: 9
- protocol: 2
- result: 33
- source: 1
