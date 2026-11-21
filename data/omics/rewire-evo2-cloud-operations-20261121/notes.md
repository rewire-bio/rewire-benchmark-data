# Evo 2 cloud operations: Rewire-run records, 2026-11-21

Rewire's own study `rewire-bio/evo2-cloud-operations`, pinned at commit `f8ae11c9a1c45505487c978b4cb7e064c4e59905`. This is not a literature pass, so there is no search ledger entry and no scope-audit entry. The store held no record of the study before this batch.

## What is in the batch

92 records, all built by `extract/build_batch.py evo2ops` from files at the pinned commit:

| Kind | Count | Content |
| --- | --- | --- |
| source | 11 | `results.json`, `operations.json` and three `receipt-main.json` files of recorded run b75c67aa, `evidence/current-predictors/results.json`, `protocol.md`, `protocol/amendments/007-current-predictors.md`, `README.md`, `evidence/run-log.md`, and the Runpod L40S `receipt-main.json` of reproduction run 30e7ae49 |
| benchmark | 1 | the study |
| dataset_subset | 4 | BRCA1 SNVs: all 3,893, coding 2,768, noncoding 1,125, missense 2,086 |
| protocol | 5 | AUROC on each subset, and W1 scoring throughput |
| configuration | 9 | Evo 2 7B on each of three platforms; CADD v1.3, phyloP, consequence rule, CADD v1.7, SpliceAI, REVEL |
| evaluation | 31 | 28 AUROC, 3 throughput |
| result | 31 | one per evaluation |

Every evaluation has origin `rewire_run`.

## Status

All 92 records are `source_checked`. No result or evaluation is `reproduced`, no protocol carries a run recipe, and no evaluation has a `reproduction` attribute. So no receipt is a recipe's validation receipt, and the board cannot show a "Reproduced" badge on a result of this batch.

An earlier draft of this batch marked 12 results `reproduced` and gave four protocols (AUROC on all, coding and noncoding SNVs, and throughput) a run recipe naming the three receipts. Review found two faults, and the draft was rebuilt before it reached main:

- The receipts hold counts, timings and throughput. They hold no AUROC and no hash of `w1_brca1_scores.tsv`. AUROC is computed afterwards, off the machine, into `results.json`. The nine Evo 2 7B AUROC results therefore cite `results.json` only.
- The Runpod L40S throughput of the recorded run, 0.6117 sequences per second, was not repeated. Reproduction run 30e7ae49 measured 0.9081 on another L40S host for the same 5,219 sequences, and `evidence/run-log.md` calls the recorded host a slower one. The result, its evaluation and the throughput protocol state both figures in `limitations` and cite the reproduction receipt and the run log.

The three throughput results cite the receipt of their own platform, because the value is read from it. The Runpod L40S receipt of the reproduction run is a source only for the limitation above. No value is taken from it.

The store's other `reproduced` records are evaluations with a `reproduction` attribute and a receipt whose own metrics equal the stored values (`docs/reviews/2026-11-21-mfass-receipt-citation.md`). These records do not meet that bar.

## Decisions

- The Google Cloud H100 (P2) value is read from `/brca1_evo2_vs_baselines/<subset>/evo2_7b`, which carries the interval. The script asserts that it equals `/platforms/P2/w1_auroc/<subset>`. P3 and P5 are read from `/platforms/<ID>/w1_auroc/<subset>`, which has no interval.
- P5 used attempt 2. The script reads the attempt from `operations.json` and asserts it.
- New protocols were written instead of reusing the Evo 2 paper's BRCA1 protocols (`gfm-guides-20261014-evo2-brixi2026-protocol-brca1-*`). The class definition and subsets were not shown to match exactly.
- Scoring seconds and peak memory are kept as evaluation attributes (`timing_seconds`, `peak_memory`), not as results. The vocabulary has no byte unit.
- A lookup score has a `version` only where amendment 7 states it (CADD v1.3, CADD v1.7, REVEL v1.3; the script asserts the strings). phyloP, SpliceAI and the consequence rule are marked unextracted.
- No source carries a licence: the README says the study code licence is to be set at publication.
- `metric_implementation` names the revision the recorded run used, `e93491a` (`provenance.json` of the run), not the pinned commit. Between the two, `src/study/analysis.py` gained 82 lines and lost none, and `src/evo2ops`, `configs` and `container` did not change.
- No use-case link and no judgement was written. The judgements needed are listed in the dated review.

## Not ingested

- W0 loss, W2 exon classifier AUROC, W3 memory by sequence length, W4 repeat scores.
- Cross-platform agreement (`/agreement_with_reference`), classification flips (`evidence/classification-flips/results.json`) and the follow-up runs (`evidence/followup-20261011/`, nine receipts).
- The results of the reproduction run `evidence/runs/reproduction-30e7ae49/` and the `receipt-repeat.json` files. No value in this batch is read from them. Its `results.json` holds the same nine Evo 2 7B AUROCs as the recorded run at `/platforms/P2|P3|P5/w1_auroc`, and its Runpod H100 and Google Cloud H100 throughputs are 2.9232 and 2.9232 against 2.9075 and 2.9297 recorded. Ingesting it as a second run, with a `reproduction` attribute on the evaluations it repeats, is the route to `reproduced` if the owner wants that status here.
- Costs (`operations.json`, `evidence/checks/verification.json`).
- `rewire-bio/evo2-size-by-use-case` at `027c2c1fcbdf14a0cc00e203795a630bd91020e7`: its README says no paid runs have been made, `evidence/claims.json` is empty and it has no result file. Nothing to ingest.
