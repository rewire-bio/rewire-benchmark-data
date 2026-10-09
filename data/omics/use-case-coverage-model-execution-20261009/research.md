# Research: diagnostic genomics execution use-case pass, 2026-10-09

Use case: `use-case-diagnostic-genomics-model-execution` ("Which eligible model configuration and execution workflow can meet a diagnostic genomics team's resource, throughput and reproducibility constraints?"). Before this pass it had one proxy judgement: the DRAGEN 4.2 developer runtime for HG002 on two hardware configurations.

Bounds: cutoff 2026-10-09; budget 25 queries, 8 used; at most 3 sources, 3 extracted. Lane `genomics`. In scope: several pipelines or execution set-ups run on the same input with printed runtime, cost, memory or throughput.

## Queries

Ledger IDs `search-use-case-model-execution-genomics-q1` to `-q8`. Times for q4, q6 and q7 are approximate (same command or minute as the neighbouring logged time).

| # | Query | Channel | Outcome |
| --- | --- | --- | --- |
| 1 | (DRAGEN OR Parabricks OR Sentieon) AND (GATK OR DeepVariant) AND (runtime OR "run time" OR "wall-clock" OR cost) AND (WGS OR "whole genome"), open access, 2018 to cutoff | Europe PMC REST | 245 hits; Samarakoon 2025 and O'Connell 2023 selected; Betschart 2022 and Zhao 2020 screened |
| 2 | Springer supplementary files for Betschart 2022 and Zhao 2020 | publisher files | Runtime not printed per pipeline |
| 3 | reproducibility or concordance across reruns or versions, GATK/DRAGEN/DeepVariant | Europe PMC REST | No rerun-concordance study in the screened titles |
| 4 | DeepVariant or Clair3 with GPU/CPU runtime or peak memory | Europe PMC REST | Only categorical runtime and memory found (PLoS One 2026) |
| 5 | "non-deterministic" or "run-to-run" or "computational reproducibility" with variant calling | Europe PMC REST | Nothing usable |
| 6 | (Sentieon OR DNAscope OR "GATK4") AND (DRAGEN OR Parabricks OR DeepVariant) AND wall time, core hours or cost per sample | Europe PMC REST | Franzoso 2025 selected |
| 7 | Wiley supplement URL for Franzoso Table S2 | web fetch | HTTP 403; Europe PMC used |
| 8 | QUDT unit pages for USDollar and MIN | web fetch | Labels and types checked |

## Decisions

| Source | Decision | Reason |
| --- | --- | --- |
| Samarakoon et al. 2025, Bioinform Adv, Supplementary Tables S3-S4 | Extract every cell (196 results) | Same ten WGS samples through a CPU-only GATK pipeline, Parabricks on L4, A100 and H100 and DRAGEN v4.2, per stage; Table S4 shows a version change alone on fixed hardware. University of Oslo, no competing interests. |
| O'Connell et al. 2023, BMC Bioinformatics, Table 1 | Extract every printed cell (252 results) | Six callers on CPU and 2, 4, 8 GPU machines on AWS, GCP and a DGX with runtime, cost, speedup and cost saving. Authors declare an NVIDIA, AWS and Google alliance; recorded. |
| Franzoso et al. 2025, Clin Transl Sci, Table S2 | Extract every cell (40 results) | Sentieon and Parabricks on cost-matched GCP machines, five WES and five WGS, aimed at hospital diagnostics. No conflicts declared. |
| Betschart et al. 2022 | Lead | 70 sequencing runs of HG002; runtime only as pairwise differences; variant-count spread across runs reflects sequencing replicates, not computational reruns |
| Zhao et al. 2020 | Excluded | Runtime only in a figure |
| PLoS One 2026 caller comparison | Excluded | Runtime and memory only as categories |

## Modelling choices

- One protocol per timed computation: four Samarakoon stage sub-tables plus the Table S4 version comparison; one O'Connell protocol per caller; one Franzoso protocol each for WES and WGS. Each has one relevance judgement. Page groups: `samarakoon2025-wgs-stages` (strata are stages), `samarakoon2025-dv-version`, `oconnell2023-germline`, `oconnell2023-somatic` (strata are callers), `franzoso2025-gcp` (WES, WGS). Headline metric `runtime`.
- Configurations are execution set-ups (software plus hardware), linked to method families: a new GATK CPU pipeline method, a new Parabricks method, a new Sentieon DNASeq method and the existing DRAGEN method. O'Connell CPU configurations run different callers per protocol and have no method link.
- Samarakoon results carry the sample in `metric_qualifier`, so comparisons pair the same sample. O'Connell prints minutes and hours separately; both are kept, with the hour column qualified as printed in hours.
- New vocabulary: metrics `compute-cost`, `cost-saving`, `speedup`; units `minute`, `us-dollar` (`coverage.json`, `vocabulary_additions`). They need review.
- All judgements are `direct`: each protocol measures runtime or cost of a complete workflow stage on a fixed input, which is the use case's resource and throughput endpoint. None measures a foundation model.
- No measured peak memory is printed in any table, so the peak-memory exclusion stays.

## Things a reviewer should judge

1. Samarakoon Table S3c: NA12778 on L4 prints 117.59 minutes against a stage sum of 31.94.
2. Samarakoon Parabricks version: Methods say 4.3.0-1; Table S4 says the pipeline used 4.1.0-1.
3. O'Connell AWS GPU hardware: the footnote says V100 (p3), the text ties the same values to A100 (p4).
4. O'Connell Mutect2 AWS CPU: text 16.9 h, table 6.91 h.
5. Franzoso Table S2: two WGS runtime cells look entered as minutes and seconds.
6. Whether any of these should become a source evidence concern, which would withhold all judgements citing that source.
7. The new vocabulary concepts and their QUDT matches.

## Coverage

Bounded pass. Not covered: rerun reproducibility with printed values, measured peak memory, accuracy next to runtime, long-read pipelines, foundation-model inference, O'Connell Table S1 (AWS A100) and Samarakoon Supplementary Text tables.
