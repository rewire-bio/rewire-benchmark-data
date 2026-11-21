# Evo 2 cloud operations: Rewire-run records, 2026-11-21

Rewire's own study `rewire-bio/evo2-cloud-operations`, pinned at commit `f8ae11c9a1c45505487c978b4cb7e064c4e59905`. This is not a literature pass, so there is no search ledger entry and no scope-audit entry. The store held no record of the study before this batch.

## What is in the batch

90 records, all built by `extract/build_batch.py evo2ops` from files at the pinned commit:

| Kind | Count | Content |
| --- | --- | --- |
| source | 9 | `results.json`, `operations.json` and three `receipt-main.json` files of recorded run b75c67aa, `evidence/current-predictors/results.json`, `protocol.md`, `protocol/amendments/007-current-predictors.md`, `README.md` |
| benchmark | 1 | the study |
| dataset_subset | 4 | BRCA1 SNVs: all 3,893, coding 2,768, noncoding 1,125, missense 2,086 |
| protocol | 5 | AUROC on each subset, and W1 scoring throughput |
| configuration | 9 | Evo 2 7B on each of three platforms; CADD v1.3, phyloP, consequence rule, CADD v1.7, SpliceAI, REVEL |
| evaluation | 31 | 28 AUROC, 3 throughput |
| result | 31 | one per evaluation |

Every evaluation has origin `rewire_run`.

## Status

12 results and their 12 evaluations are `reproduced`: Evo 2 7B AUROC on the all, coding and noncoding subsets on each of the three platforms (9), and W1 throughput on each platform (3). Each cites the `receipt-main.json` of its own platform, and that receipt is the `full_protocol` validation receipt of an executed instruction in the protocol's run recipe. The receipt records that the run completed and scored all 3,893 variants.

19 results and their evaluations are `source_checked` and cite no receipt: the lookup predictors (no GPU run), and all four missense results, which come from the amendment 7 analysis done after the recorded run.

`reproduced` here means Rewire ran the full protocol and the receipt is cited. It does not mean a published score was reproduced, and the run is the project's own.

## Decisions

- The Google Cloud H100 (P2) value is read from `/brca1_evo2_vs_baselines/<subset>/evo2_7b`, which carries the interval. The script asserts that it equals `/platforms/P2/w1_auroc/<subset>`. P3 and P5 are read from `/platforms/<ID>/w1_auroc/<subset>`, which has no interval.
- P5 used attempt 2. The script reads the attempt from `operations.json` and asserts it.
- New protocols were written instead of reusing the Evo 2 paper's BRCA1 protocols (`gfm-guides-20261014-evo2-brixi2026-protocol-brca1-*`). The class definition and subsets were not shown to match exactly.
- Scoring seconds and peak memory are kept as evaluation attributes (`timing_seconds`, `peak_memory`), not as results. The vocabulary has no byte unit.
- A lookup score has a `version` only where amendment 7 states it (CADD v1.3, CADD v1.7, REVEL v1.3; the script asserts the strings). phyloP, SpliceAI and the consequence rule are marked unextracted.
- No source carries a licence: the README says the study code licence is to be set at publication.
- No use-case link and no judgement was written. The judgements needed are listed in the dated review.

## Not ingested

- W0 loss, W2 exon classifier AUROC, W3 memory by sequence length, W4 repeat scores.
- Cross-platform agreement (`/agreement_with_reference`), classification flips (`evidence/classification-flips/results.json`) and the follow-up runs (`evidence/followup-20261011/`, nine receipts).
- The reproduction run `evidence/runs/reproduction-30e7ae49/` (three receipts) and the `receipt-repeat.json` files. No result in this batch rests on them.
- Costs (`operations.json`, `evidence/checks/verification.json`).
- `rewire-bio/evo2-size-by-use-case` at `027c2c1fcbdf14a0cc00e203795a630bd91020e7`: its README says no paid runs have been made, `evidence/claims.json` is empty and it has no result file. Nothing to ingest.
