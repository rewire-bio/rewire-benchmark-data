# Review: use-case-coverage-model-execution-20261011-genepi, 2026-10-12

Reviewer: Claude (Opus 5.5) review agent `reviewer-exec`, independent of the extractor `uc-execution`. No human review claimed. Source transcription is not reproduction. Full review: `docs/reviews/use-cases/diagnostic-genomics-model-execution-2026-10-12.md`.

## Reviewer's verdict for this batch (verbatim)

| Batch or item | Verdict |
| --- | --- |
| `use-case-coverage-model-execution-20261011-genepi` | Approved with corrections (A1, A2, G1, G2) |

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

### genepi (Marangoni et al. 2026)

G1. Table S1 is on page 7 of the supplementary PDF (printed and physical), not page 8. In the 20 result locators and the matching 20 `claims.csv` rows, replace `Supplementary Table S1 (page 8)` with `Supplementary Table S1 (page 7)`.

G2. In the protocol and its judgement, append to `limitations`: `The article states a 10- to 78-fold average acceleration over CPU (Discussion, citing Figure 2 and Supplementary Figure S11); the Table S1 ratios run from about 10 to 34, so the upper figure comes from runs not in Table S1.`

## Reviewer's judgement review (verbatim)

Each judgement's endpoint matches its protocol and the use case's inputs (team hardware, required turnaround and throughput) and output (per-sample runtime, cost and resource values for exact configurations); the limitations carry the sources' own caveats after the corrections; none has `excluded_evaluations`. Set `reviewed_evaluations` as follows.

| Judgement | Relevance | Outcome | `reviewed_evaluations` |
| --- | --- | --- | --- |
| `use-case-mapping-model-execution-20261011-marangoni2026-germline-runtime-by-depth` | direct | Holds with A1 and G2 | `model-execution-20261011-eval-marangoni2026-gatk-cpu`, `model-execution-20261011-eval-marangoni2026-parabricks-4-3-0-2xa100`, `model-execution-20261011-eval-marangoni2026-parabricks-4-3-0-2xv100`, `model-execution-20261011-eval-marangoni2026-parabricks-4-3-0-4xa100` |

## Reviewer's answers to the collector's questions (verbatim)

5. Relevance. All ten levels hold; details under "Judgement review". The Clair3 resource proxies are right, and the hardware is in fact stated in the Methods (C4). GeNePi `direct` holds: per-genome runtime on stated hardware for an exact pipeline version matches the use case's inputs and output, as for the Samarakoon judgements already marked direct; the unnamed sample and unstated run count are carried as limitations.
6. Origin. All correct. Author overlap checked from the author lists and affiliations: Zheng et al. are the Clair3 group (HKU); Aspidova, Kuratov, Burtsev and Fishman are GENA-LM authors; Yu et al. include Egan and Wang of the DOE Joint Genome Institute, home of GenomeOcean; all six Hu et al. authors are Sentieon employees; Marangoni et al. built GeNePi, whose PB_germ module is the configuration evaluated, so `author_reported` for the GPU rows is the right conservative reading even though Parabricks itself is NVIDIA's. DeepVariant, DNABERT-2, NTv2 and the CPU GATK baseline are `independent_paper`.

## Corrections applied

Applied by the extractor in the extraction scripts (`extract/build.py`), as the reviewer specified, before the batch was added to the store; `claims.csv` was regenerated with the batch. Then `extract/apply_review.py` recorded the review on every record.

1. A1: run-count wording replaced in the dataset, protocol, evaluations and judgement.
2. A2: review block from the review on every result; judgement review block and reviewed_evaluations on the judgement; every record source_checked.
3. G1: the 20 result locators and 20 claims.csv rows now say Supplementary Table S1 (page 7).
4. G2: 10- to 78-fold limitation appended to the protocol and judgement.
5. Form, after review: missing_metadata keys on the dataset record put in sorted order (accession before version), the store's normal form; no value changed.

## Records after correction

- claim: 1
- configuration: 4
- dataset: 1
- evaluation: 4
- protocol: 1
- result: 20
- source: 2
