# Research: RNA pathogen-detection use-case pass, 2026-10-09

Use case: `use-case-diagnostic-rna-pathogen-detection` ("Which RNA sequencing workflow detects RNA pathogens reliably in the intended specimen and distinguishes real detections from host/background contamination?"). Before this pass it had one judgement: a UCSF respiratory RNA mNGS assay at 103 of 110 sensitivity against the original clinical respiratory panel, a single result with no comparator.

Goal: comparisons of several workflows or classifiers on the same RNA data, with per-tool values printed in tables.

Bounds: cutoff 2026-10-09; 25 queries budgeted, 10 used; at most three sources extracted. Lane `microbial`. Values read from figures were not allowed.

## Queries

All 10 are in `data/omics/search-ledger.jsonl` as `search-use-case-rna-pathogen-microbial-q*` (and one `source-resolution` entry), with the exact query strings, times, failed retrievals and gaps.

| # | Query (shortened) | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | de Vries 2021 ENNGS thirteen-pipeline benchmark | web | ENNGS benchmark located and extracted from the preprint after five retrieval failures on the published version |
| 2 | Europe PMC: the two ENNGS DOIs | Europe PMC | Published version is PMC7615111 (CC BY); preprint record PPR337157 |
| 3 | RNA virus pipeline comparison, CZ ID, Genome Detective, Kraken2, DIAMOND versus PCR | web | Known leads only; no CZ ID comparison |
| 4 | RNA virus spike-in or mock virome benchmark | web | None found; ancient-DNA simulation and a student thesis excluded |
| 5 | SARS-CoV-2 or respiratory mNGS pipeline comparison against RT-PCR | web | One single-pipeline synthetic study; not opened |
| 6 | Brinkmann 2019 in silico virus proficiency test | web, Europe PMC | Opened. Per-participant sensitivity for four viruses, but participants are anonymised and not linked to tools; not extracted |
| 7 | 2024-2026 viral classifier benchmarks | web | No peer-reviewed multi-classifier RNA benchmark with printed tables in that window |
| 8 | CZ ID versus other pipelines on CSF | web | No head-to-head found |
| 9 | classifier benchmark, clinical metagenomic pathogen detection, precision and recall | web, Europe PMC | Carbo et al. 2022 retrieved and extracted; its own supplement unretrievable, preprint supplement used |
| 10 | Europe PMC: CAMI II second round | Europe PMC, Springer | CAMI II retrieved; Supplementary Table 39 extracted from the Springer workbook |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Carbo et al. 2022, Supplementary Table 1 (all three sheets) | Extract all 720 cells | Five classifiers on the same 88 respiratory specimens against a 1144-result RNA respiratory virus PCR panel, with and without host read removal: the closest match to both halves of the use-case question in the intended specimen |
| de Vries et al. 2021, Supplementary Tables 2 and 4 | Extract all cells | Thirteen clinical virology laboratories ran their own pipelines blind on the same 13 clinical datasets; Table 4 counts additional viruses whose PCR was negative, which is the contamination half of the question |
| Meyer et al. 2022, Supplementary Table 39 | Extract all 20 cells | The CAMI II pathogen challenge's causal organism is an RNA virus (CCHFV), and the table scores ten submissions on listing it and on naming it causal |
| Brinkmann et al. 2019 (COMPARE in silico proficiency test) | Not extracted | Table 3 scores two highly divergent RNA viruses (measles at 82%, a bornavirus at 55% nucleotide identity) per participant, which is exactly the hard case for this use case, but participants are anonymised and not linked to named tools, so no configuration can be identified. Recorded as a gap; a strong candidate if the standard allowed anonymous participants as configurations |
| Carbo et al. Supplementary Table 2 | Not extracted | Duplicates the LR slope, intercept and r2 columns of Supplementary Table 1 |
| de Vries et al. Supplementary Table 3 | Not extracted | Free-text taxon names per pipeline, not scored values |
| de Vries et al. Tables 1 and 2 | Not transcribed | Images in the preprint. Gap: pipeline versions and databases are unextracted |
| CAMI II Supplementary Fig. 16 | Not read | Figure |
| Ancient viral DNA simulation (PeerJ 2022) | Excluded | DNA virus targets |
| 2025 nanopore classifier thesis | Excluded | Student thesis, not a peer-reviewed primary source |
| BMC Research Notes 2024 respiratory pipeline | Excluded | Single in-house pipeline on synthetic data |
| CSF DNA and RNA mNGS protocol comparison (PMC8976360) | Excluded | Compares wet-lab protocols, not bioinformatic workflows |

## Relevance judgements

Seven, all status `needs_review`:

- **Carbo et al., four protocols** grouped as strata of `carbo2022-respiratory` (species cut-off 0, species cut-off 10, genus, family), headline recall. Species, species cut-off 10 and genus are `direct`: the cohort is the use case's specimen type, the targets are RNA respiratory viruses, and species or genus assignment is a reportable identification. Family level is `proxy` because a family-level call does not identify the pathogen at a reportable level.
- **de Vries et al., two protocols** grouped as strata of `devries2021-ennngs` (sample level, virus-hit level), headlines recall and precision. Both `proxy`: 5 of 15 targets are DNA viruses, specimens include CSF, brain and plasma, and each laboratory used its own database and reporting rules.
- **Meyer et al., one protocol**, headline success-rate, `proxy`: one blood sample, outside the respiratory specimen scope, with manually curated submissions.

## Proposed use-case changes

`coverage.json` holds the seven `assessed_by` links, proposed `setting` text, six new `evidence_gaps`, and a proposal to broaden the non-respiratory exclusion. The two multi-workflow comparisons that bear on contamination are not respiratory-only: the ENNGS panel is 5 respiratory of 13 datasets, and the CAMI II sample is blood. Keeping the exclusion absolute would drop the only evidence this use case has on separating real detections from background. The proposal keeps the exclusion but allows non-respiratory specimens where a multi-workflow comparison is recorded as proxy and names its specimen type. `coverage.json` also records what to do if the integrator declines: drop the CAMI judgement and mark the two ENNGS judgements `outside_scope`.

No change is proposed to question, decision, inputs or output. Those fields and `setting` and `exclusions` are pinned by the existing UCSF judgement, so applying the setting or exclusion change needs that judgement re-pinned in the same reviewed change.

## Vocabulary added

Four metric concepts in `data/vocab/metric.ttl` for printed columns with no fitting concept: `negative-predictive-value`, `regression-intercept`, `regression-slope` and `roc-distance`. The DNA pathogen pass on `claude/uc-dna-pathogen` added `eta-squared`, `f-beta-score`, `peak-memory`, `youden-index` and the `gigabyte` unit; none of those is needed here, and none of the four added here duplicates them, so the two branches add disjoint blocks to the same file.

## Existing records reused

Configurations link `configuration_of` to `catalog-model-kraken2` and `catalog-model-metaphlan`. The store also holds `discovery-model-kraken-2` and `discovery-model-metaphlan`, which duplicate them; they were not linked. New family records were added for Centrifuge, CLARK, Kaiju, Genome Detective, Bracken, LSHVec, MetaPhyler, NSSAC, PathoScope, CCMetagen and the eleven ENNGS pipelines.

## Things a reviewer should judge

1. Eight cells of Carbo et al. Supplementary Table 1 print `10000` for quantities bounded by 0 and 1, almost certainly `1.0000` with the decimal point lost. `printed_value` keeps `10000`, `numeric_value` is null, and each result carries `source_anomaly`. No evidence concern was raised on the source, on the view that this is a transcription artefact rather than a disputed measurement. A reviewer may prefer a concern.
2. The Carbo et al. column headed `Informedness` holds the ROC distance, not Youden's J. Section 2.7 defines it that way, and all 56 in-range rows match sqrt((1-SN)^2 + (1-SL)^2) within rounding. Stored as `roc-distance` with the printed label in `source_label` and a claim recording the check.
3. Carbo et al. gives the Genome Detective version as 1.126 in Table 2 and its database as 1.130 in Section 2.5. Both are in the configuration version field.
4. What the 0 and 10 read cut-offs mean alongside the ROC-selected threshold is not defined beyond a sheet note. The two species blocks are separate protocols.
5. de Vries et al. Supplementary Table 2 has 14 pipeline rows including `DIAMOND pipeline 3A`, while the Methods say 13 pipelines and that DAMIAN was run by two participants as A and B. Evidence concern recorded on the supplement source.
6. The same source's abstract gives the lowest sample-level sensitivity as 80% (10/13); 10/13 is 76.9%, which the Results and the supplement print, and 80% matches the lowest hit-level value (12/15). Part of the same concern.
7. CAMI II Supplementary Table 39 and the article text disagree on which Bracken version predicted the causal pathogen. Evidence concern on the supplement source; table values recorded.
8. Whether the Carbo et al. species and genus judgements should be `direct` as recorded, given that the reference is the original PCR panel rather than an adjudicated standard.
9. Whether to broaden the non-respiratory exclusion.
10. Both Carbo et al. and de Vries et al. values come from preprint supplements because the published files could not be retrieved. Each source record carries this as a limitation.

## Coverage

Bounded pass, not systematic. Not covered: independent comparisons of hosted clinical RNA pipelines (CZ ID, SURPI+, DRAGEN, VirMAP); RNA virus spike-in or reference-material studies; the COMPARE proficiency test values; 2024-2026 literature beyond web search, since no Europe PMC structured query was run for that window; and pipeline versions and databases for the ENNGS pipelines, which sit in an image table.
