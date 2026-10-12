# Record when each use case's evidence was last checked (2026-10-12)

Adds `attributes.evidence_checked` to 25 of the 26 use-case records: the date of the latest dated evidence pass for that use case, the search cutoff where the pass recorded one, and the files that record the pass. Releases derive `next_due`, one calendar month later, for the monthly check (`nextMonthlyCheck` in `shared/omics/use-cases.ts`). The field is not pinned, so no judgement or summary is withheld.

## How the dates were chosen

- **The nine AMP use cases:** the 2026-10-11 use-case literature passes (window 2025-10-01 to 2026-10-11). Each records the pass's search ledger and its dated review.
- **The other sixteen:** the date of the latest dated use-case review in `docs/reviews/use-cases/` that ran a literature search. The twelve 2026-10-09 passes recorded a cutoff of 2026-10-09 in `data/omics/search-ledger.jsonl`; the four 2026-10-07 and 2026-10-08 passes recorded none. Later single-source follow-ups that ran no new search (Ahlmann-Eltze derived values 2026-10-11, Kaschta 2026-10-10, NeuSomatic 2026-10-10, Jamshidi 2026-10-10) are not counted as checks.
- **`utr-translation-baselines`:** no dated use-case review exists for it, so the field is left out. The site shows the check as not recorded.

This change records when passes happened. It does not change any scientific value.

## Values

| Use case | Date | Cutoff | Records |
| --- | --- | --- | --- |
| `brca1-brca2-germline-interpretation` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/brca1-brca2-germline-interpretation-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `cell-type-annotation-transfer` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/cell-type-annotation-transfer-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `cnv-detection-characterisation` | 2026-10-11 | 2026-10-11 | `data/omics/lit-search-20261011-uc-splicing-cnv/ledger.jsonl`, `docs/reviews/use-cases/splicing-cnv-use-cases-2026-10-12.md` |
| `diagnostic-dna-pathogen-identification` | 2026-10-11 | 2026-10-11 | `data/omics/lit-search-20261011-uc-pathogens/ledger.jsonl`, `docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md` |
| `diagnostic-genomics-model-execution` | 2026-10-11 | 2026-10-11 | `data/omics/lit-search-20261011-uc-execution/ledger.jsonl`, `docs/reviews/use-cases/diagnostic-genomics-model-execution-2026-10-12.md` |
| `diagnostic-rna-pathogen-detection` | 2026-10-11 | 2026-10-11 | `data/omics/lit-search-20261011-uc-pathogens/ledger.jsonl`, `docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md` |
| `egfr-nsclc-actionability-resistance-evidence` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/egfr-nsclc-actionability-resistance-evidence-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `genetic-perturbation-response` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/genetic-perturbation-response-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `mass-spectrum-molecule-shortlisting` | 2026-10-07 |  | `docs/reviews/use-cases/mass-spectrum-molecule-shortlisting-2026-10-07.md` |
| `patient-rna-splicing-validation` | 2026-10-11 | 2026-10-11 | `data/omics/lit-search-20261011-uc-splicing-cnv/ledger.jsonl`, `docs/reviews/use-cases/splicing-cnv-use-cases-2026-10-12.md` |
| `phenotype-perturbation-selection` | 2026-10-07 |  | `docs/reviews/use-cases/phenotype-perturbation-selection-2026-10-07.md` |
| `plant-promoter-reporters` | 2026-10-08 |  | `docs/reviews/use-cases/plant-promoter-reporters-2026-10-08.md` |
| `plasma-ctdna-fragmentomics` | 2026-10-11 | 2026-10-11 | `data/omics/lit-search-20261011-uc-ctdna/ledger.jsonl`, `docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md` |
| `plasma-ctdna-methylation` | 2026-10-11 | 2026-10-11 | `data/omics/lit-search-20261011-uc-ctdna/ledger.jsonl`, `docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md` |
| `protein-variant-stability` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/protein-variant-stability-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `rare-disease-candidate-ranking` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/rare-disease-candidate-ranking-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `regulatory-variant-gene-follow-up` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/regulatory-variant-gene-follow-up-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `rhodopsin-wavelength-transfer` | 2026-10-08 |  | `docs/reviews/use-cases/rhodopsin-wavelength-transfer-2026-10-08.md` |
| `somatic-small-variant-oncogenicity` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/somatic-small-variant-oncogenicity-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `splicing-follow-up` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/splicing-follow-up-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `structural-hypotheses-experiments` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/structural-hypotheses-experiments-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `therapeutic-target-validation` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/therapeutic-target-validation-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `tumour-dna-somatic-variant-detection` | 2026-10-11 | 2026-10-11 | `data/omics/lit-search-20261011-uc-oncology/ledger.jsonl`, `docs/reviews/use-cases/tumour-dna-somatic-variant-detection-2026-10-11.md` |
| `tumour-rna-fusion-detection` | 2026-10-11 | 2026-10-11 | `data/omics/lit-search-20261011-uc-oncology/ledger.jsonl`, `docs/reviews/use-cases/tumour-rna-fusion-detection-2026-10-11.md` |
| `unresolved-rare-disease-reanalysis` | 2026-10-09 | 2026-10-09 | `docs/reviews/use-cases/unresolved-rare-disease-reanalysis-2026-10-09.md`, `data/omics/search-ledger.jsonl` |
| `utr-translation-baselines` | not recorded |  | No dated use-case pass found; due now. |

## Review

Reviewer: rev-checked, a separate Claude review agent that did not author this change. No human review is claimed. Nothing scientific was re-extracted; this checks dates, paths and code against the repository.

Outcome: pass, after one round of corrections. The first review found that the generated ontology files had not been rebuilt after the registry change (two `tests/linked-data.test.ts` failures), that `genetic-perturbation-response` was dated by a 2026-10-11 single-source extraction that ran no search, and that the twelve 2026-10-09 passes had a cutoff in `data/omics/search-ledger.jsonl` that was not recorded. All three were fixed and re-checked.

What was checked:

1. Dates. Every entry in the five `data/omics/lit-search-20261011-uc-*` ledgers has `searched_at` on 2026-10-11 and `cutoff_date` 2026-10-11. For the others, the latest `docs/reviews/use-cases/<slug>-YYYY-MM-DD.md` was compared with the central search ledger. The twelve 2026-10-09 query groups all have `searched_at` and `cutoff_date` 2026-10-09. The four 2026-10-07 and 2026-10-08 dossiers keep their search logs in an ignored workbench, so no cutoff is given. The later Ahlmann-Eltze, Kaschta, NeuSomatic and Jamshidi follow-ups are recorded in the ledger as targeted work on known sources, not searches. `utr-translation-baselines` has no dated use-case review and no ledger entry; it appears only in the cross-use-case tables of `coverage-audit-2026-09-30.md` and `amp-coverage-2026-10-07.md`.
2. Paths. Every path in `records` exists.
3. Record diff. Against origin/main, the 26 lines of `data/entities/use-cases.jsonl` keep their order and differ only in `attributes.evidence_checked` (25 lines). The values equal `plan.json` and the table above. In `data/provenance/records.jsonl` only those 25 rows change, by their hash and one appended `records:change` entry.
4. `nextMonthlyCheck`. It agreed with an independent calculation for all 37,620 dates from 1999 to 2101, including month ends, December to January and leap years (2000 and 2028 have 29 February; 2026 and 2100 do not). The schema now rejects 2026-02-29, 2026-02-30 and 2026-04-31. Month 13, month 00 and day 32 were rejected by an "Invalid time value" exception rather than a schema error; after review the author changed the check to test for an invalid date first, so they now fail with the schema message "Not a calendar date". No stored value is affected.
5. Lifecycle. `deriveUseCaseInputs` on an origin/main snapshot and on this change gives the same 376 mappings, identical as JSON, 349 active, and the same 23 published summaries. No use case changes except `evidence_checked`. The use-case pin fields do not include it, and the evidence hash does not cover the use-case record.

Checks, run one at a time: `npx tsc --noEmit -p .` passed; `npx vitest run` with two forks passed 516 of 516 tests in 48 files; `npm run -s test:kg` passed 25 tests; `npm run -s records -- check` reported 67714 records matching their provenance.
