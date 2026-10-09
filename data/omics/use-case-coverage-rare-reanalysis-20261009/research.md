# Research: rare-disease reanalysis use-case pass, 2026-10-09

Use case: `use-case-unresolved-rare-disease-reanalysis` ("Which reanalysis methods find new diagnoses or reduce review effort when given the same updated information?"). Before this pass it had one direct judgement: new confirmed diagnoses and review workload during monthly Talos reanalysis. Its exclusions keep reranking of known solved cases, new knowledge counted as algorithmic improvement, and changed database labels out of new-yield evidence.

Goal: several reanalysis or prioritisation methods compared on the same unsolved cohort, with per-method values printed in tables.

Bounds: cutoff 2026-10-09; 25 queries budgeted, 10 used; at most three sources extracted, two used. Lane `genomics`. The related candidate-ranking dossier (`docs/reviews/use-cases/rare-disease-candidate-ranking-2026-10-08.md`) was read first, so ranking benchmarks on solved cases already covered there were not re-searched.

## Queries

All 10 are in `data/omics/search-ledger.jsonl` as `search-use-case-rare-reanalysis-genomics-q1` to `q8` and two `source-resolution` entries.

| # | Query (shortened) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | automated reanalysis unsolved exomes, Exomiser, LIRICAL, AMELIE | web | AMELIE 3, settings rebuttal, single-method cohort reanalyses |
| 2 | Vestito 2024 Exomiser reinterpretation, 100kGP | web, Europe PMC | Vestito et al. retrieved and extracted |
| 3 | comparison of automated reanalysis tools, 2024-2026 | web (extended) | Talos in PMC; Kaschta et al. 2026 automated versus manual |
| 4 | reanalysis of undiagnosed cohort, several prioritisation tools | web, Europe PMC | Moon versus Exomiser (closed access); ranking studies |
| 5 | Europe PMC: exome reanalysis with Exomiser, Moon, LIRICAL or automated | Europe PMC | 3 hits, none open access |
| 6 | systematic reanalysis, two pipelines on the same cohort | web, Europe PMC | Romero et al. 2022; Solve-RD |
| 7 | Europe PMC: Solve-RD reanalysis, open access | Europe PMC | Demidov et al. 2024 extracted; two more Solve-RD papers screened |
| 8 | UDN reanalysis comparisons | web | Ranking studies only |
| 9 | medRxiv API: Kaschta et al. 2026 | medRxiv API | JATS and supplement retrieved; earlier pass had HTTP 403 |
| 10 | medRxiv API: AMELIE 3 | medRxiv API | JATS retrieved; tables are images |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Demidov et al. 2024 (Solve-RD CNV reanalysis), Table 1 and Supplementary Table 4 | Extract all per-caller cells | Three CNV callers on the same 9171 unsolved exomes; the tables count calls each returned for expert interpretation, which is the review-effort half of the question |
| Vestito et al. 2024 (Exomiser), Supplementary Table 1 | Extract all 81 rows | Varies only the flagging rule while holding the knowledge update fixed, and counts candidates to review (FP) against diagnoses recovered |
| Talos 2026, Table 1 and the Exomiser comparison (already in the store) | Judge 7 existing protocols; no new extraction | Default versus strict Talos filtering, and Exomiser rank budgets, trade recovered diagnoses against candidates to review on the same cohorts |
| Kaschta et al. 2026 (manual versus automated Talos reanalysis, 219 unsolved genomes) | Not extracted | The closest match to the question, with new diagnoses, review minutes and candidates per case for both arms on the same cases. But every per-method value is printed only in prose, Table 1 is an image, and the supplement is per-patient clinical data. All rights reserved. Gap |
| AMELIE 3 (2020) | Not extracted | Tables are images |
| Solve-RD Nature Medicine 2025 | Not extracted | Yields for one workflow by ERN and variant type; no method comparison |
| MEI benchmark (EJHG 2024) | Not extracted | Caller benchmark on reference genomes plus single-workflow reanalysis yield |
| Romero et al. 2022 | Not extracted | Tables list individual variants, not per-pipeline summary values |
| Moon versus Exomiser (Genet Med 2022), J Mol Diagn 2019 | Not retrieved | Not open access |
| Ranking benchmarks on solved cases (AI-MARRVEL, retinal-disease benchmark, UDN Exomiser optimisation, settings rebuttal) | Not extracted here | Belong to the candidate-ranking use case; under this use case's first exclusion they would be proxy at most |

## Relevance judgements

Nine, all `proxy`, all status `needs_review`. None is direct, because no extracted table measures new confirmed diagnoses per method on the same unsolved cohort.

- **Demidov et al.** (`demidov2024-solverd-cnv`, headline count): same unsolved cohort and same downstream filters, but the tables count calls to review, not diagnoses per caller.
- **Vestito et al.** (`vestito2024-exomiser-thresholds`, headline F2): flagging rules compared on 37 cases already diagnosed after a new disease-gene association. Under the first exclusion this is recovery of known diagnoses, not new yield.
- **Talos 2026, six strata** (`talos2026-known-diagnoses`, headline recall): default versus strict filtering on known diagnoses.
- **Exomiser comparator** (`talos2026-exomiser-acg`, headline recall): rank budgets on known ACG trio diagnoses, with the unresolved 194 versus 190 denominator conflict.

The Talos and Exomiser protocols are already mapped as proxy for `use-case-rare-disease-candidate-ranking`, so the same evaluations will appear on both pages. That is intended: the use cases ask different questions of the same records.

## Use-case changes proposed

`coverage.json` lists the nine `assessed_by` links and six new evidence gaps. No change is proposed to the decision, inputs, output, setting or exclusions, which are pinned by the existing Talos programme judgement.

## Vocabulary added

`true-negative-count` in `data/vocab/metric.ttl`, needed for Vestito et al.'s TN column. It follows the existing `true-positive-count`, `false-positive-count` and `false-negative-count` concepts. No STATO match was added because the identifier was not checked.

## Things a reviewer should judge

1. Demidov et al. print the ExomeDepth Bayes factor threshold two ways (BF > 15; discard BF < 0.15). Both are kept in the configuration parameters.
2. Demidov et al. Supplementary Table 5's caption swaps the deletion and duplication counts relative to Supplementary Table 4 and the text. Table 5 was not extracted.
3. Demidov et al. Supplementary Table 4 uses European number formatting. The conversion is asserted against Table 1.
4. Vestito et al. Supplementary Table 1 does not name the database releases. The 0.2/0.8 row matches the text's February 2019 versus February 2022 result, and a claim records the inference.
5. Vestito et al. tuned the thresholds on the same 37 cases they are scored on.
6. ClinCNV evaluations are `author_reported`.
7. Whether Kaschta et al. 2026 should be extracted by exact-locator prose transcription. Its prose also has internal inconsistencies: the automated yield is printed as 41.9% where 161 of 377 is 42.7%, and the pipeline-conversion share is 8.6% in the text and 9.6% in the Fig. 2 legend. Its two arms also did not receive equal inputs: the manual arm re-called variants with an updated DRAGEN, while Talos used the archived calls.

## Privacy

Two downloaded supplements (Kaschta et al. and the Solve-RD Nature Medicine workbook) contain per-patient clinical rows. They were inspected only for their headers, hashed, and deleted from the scratch directory. No per-patient data entered the batch.

## Coverage

Bounded pass, not systematic. Not covered: closed-access reanalysis comparisons (Genet Med 2022 and 2026, J Mol Diagn 2019); AMELIE 3 values (image tables); repeated-cycle false alerts per method; and LIRICAL, Xrare, PhenIX, VarSeq or GEM on unsolved cohorts, which were not found.
