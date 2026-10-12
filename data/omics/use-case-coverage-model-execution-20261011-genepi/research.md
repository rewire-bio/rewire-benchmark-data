# Research: Marangoni et al. 2026, GeNePi (Briefings in Bioinformatics 27(1), bbag001)

Use case: `use-case-diagnostic-genomics-model-execution`. Pass: diagnostic genomics execution literature search, window 2025-10-01 to 2026-10-11. The search log, candidates and gaps for the whole pass are in `data/omics/lit-search-20261011-uc-execution/` (ledger, scope audit and report).

Selected because it prints per-genome germline runtime at five read depths for the CPU GATK equivalent and Parabricks on three GPU node types, from a regional genomics centre running routine WGS. It was an open lead in the 2026-10-09 ledger (`search-use-case-model-execution-genomics-q1`: "GeNePi 2026 ... not opened").

Modelling:
- Configurations reuse `model-execution-20261009-method-gatk-best-practices-cpu` and `model-execution-20261009-method-parabricks`.
- One protocol; depth is in `metric_qualifier`.
- Origin: GPU rows `author_reported` (GeNePi's PB_germ module is the authors' pipeline around Parabricks); CPU row `independent_paper`.
- Judgement drafted as `direct` (stated hardware, whole FASTQ-to-VCF germline workflow, clinical WGS setting).

Things a reviewer should judge:
1. Whether `direct` is right given one unnamed sample per depth and single runs.
2. Whether the CPU-equivalent configuration should carry `independent_paper` or `author_reported`.

## Records

| Kind | Count |
| --- | --- |
| claim | 1 |
| configuration | 4 |
| dataset | 1 |
| evaluation | 4 |
| protocol | 1 |
| result | 20 |
| source | 2 |
