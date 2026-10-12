# Research: Fragmentia-AI WGS by ichorCNA tumour fraction, 2026-10-11

Use case: `use-case-plasma-ctdna-fragmentomics`.

Bounds: window 2025-10-01 to 2026-10-11; about 30 queries per use case for the whole uc-ctdna pass (26 logged); at most about 6 sources extracted across both use cases. Lane `genomics`. Worker: Claude (Opus 5.5) research agent uc-ctdna; no human review claimed. The search log is `data/omics/lit-search-20261011-uc-ctdna/ledger.jsonl` and the pass report is `data/omics/lit-search-20261011-uc-ctdna/report.md`.

## Why this source

Fragmentia-AI WGS (Molecular Biomedicine 2026, 10.1186/s43556-026-00538-w) reports AUC within ichorCNA tumour-fraction strata (< 3%, 3-5%, > 5%) for three fine-tuning schemes, and sensitivity at a training-derived 98%-specificity cutoff overall, by stratum and for low-TF cancers by stage, on a 5,996-sample independent test cohort and the public DELFI cohort. The use case's gap list says tumour-fraction-stratified evidence comes from one developer study (UNITE); this is a second, larger one, with a fixed cutoff carried to an independent cohort.

## Record design

- Two sources (article XML, archived; supplementary DOCX). Values from asserted Results sentences (24) and every cell of Table S4 (6): 30 results.
- Four datasets (training, validation, test, DELFI via FinaleDB) and four protocols; three configurations (fine-tuning schemes) of the Fragmentia-AI method added by the Fragmentia-AI batch, which must be added first.
- Sensitivity at the transferred cutoff uses `recall` with the cutoff in the qualifier, because observed specificity is not 98% outside training (0.97 test, 0.92 DELFI).
- Three relevance judgements (`proxy`): validation, test and DELFI. The training protocol is stored but not mapped.

## Things a reviewer should judge

1. **Strata.** ichorCNA estimates below its own 3% limit define the low-TF stratum.
2. **No comparator.** Only Fragmentia-AI configurations are compared.
3. **Overlap.** The DELFI cohort overlaps the DELFI 2019 samples behind other fragmentomics evidence.
4. **Metric choice.** `recall` against a sensitivity-at-specificity concept for the transferred cutoff.
