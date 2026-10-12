# Research notes

Part of the 2026-10-11 microbial and interactions literature pass (window 2025-10-01 to 2026-10-11).
The search log is in `data/omics/lit-search-20261011-microbial-interactions/ledger.jsonl`.

## Why this source

Small but specific: it is the only source found in the window that scores Boltz-2 against
structure-based and sequence-based antibody-antigen affinity methods on held-out antigens, with each
of the four AlphaBind antigens held out in turn. That rotation is what makes the numbers worth
keeping, because cross-antigen generalisation is the failure mode the lane cares about.

The result is that interface confidence used as an affinity proxy is weak here: Boltz-2 ipLDDT
reaches 55.52 to 60.09 percent pairwise accuracy across the four antigens, and GeoDock 47.11 to
51.21, against a 50 percent chance level.

## Record counts

- benchmark: 1
- configuration: 4
- dataset: 4
- evaluation: 16
- model: 3
- protocol: 4
- result: 16
- source: 1

## Extraction notes (written before review)

- Four protocols, one per held-out antigen (PEM, PP489, TRA, VHH72), each with the four systems.
- Metric is `accuracy` with the qualifier "pairwise: stronger binder identified within sampled
  antibody pairs", in percent as printed.
- The MochiBind cells print the accuracy with a p-value, for example "72.35% (p < 0.0001)". The
  printed value keeps the whole string, `numeric_value` is the accuracy, and the p-value is in
  `reported_p_value`. The p-values are one-sided McNemar tests against the baselines, not an
  uncertainty on the accuracy.
- Origin: `author_reported` for MochiBind (the paper proposes it), `independent_paper` for
  Graphinity, Boltz-2 and GeoDock, which the authors ran. Graphinity's values are the fine-tuned
  model, per the table note.
- Boltz-2 and GeoDock are scored through interface pLDDT as an affinity proxy, not an affinity head.
  That is recorded in the configurations and in the protocol limitations, because it is the main
  thing that would make a naive comparison misleading.
- **Needs a reviewer's judgement.** The sampling of the pairs (how many pairs per antigen, and how
  they were drawn) is in STAR Methods prose that was not fully transcribed; the protocols have no
  denominator. A reviewer should decide whether the pairwise accuracies need a pair count before
  they support comparison.
