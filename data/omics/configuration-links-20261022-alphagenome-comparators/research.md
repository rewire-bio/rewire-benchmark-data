# Research: model links for the AlphaGenome paper's comparator configurations

The discrepancy rules in `scripts/kg/contradictions.py` compare configurations as the model they configure. Of the 13 comparator configurations in the AlphaGenome Nature batch, 11 had no `configuration_of` or `family` link, and the other two (SpliceAI and Pangolin) had an unbacked `family` link. So the paper's comparisons against Borzoi could not be joined with other studies' Borzoi results, and the Alavi 2026 discrepancy (issue #174) did not appear.

## What was linked

| Configuration | Linked to | Evidence |
| --- | --- | --- |
| Borzoi (paper Table 3) | `regulatory-variant-20261009-model-borzoi` | Supplementary Methods p.21 and p.24 ("the published Borzoi model") |
| borzoi-ensemble (paper Table 4) | `regulatory-variant-20261009-model-borzoi` | p.21; pp.37-38 ("the Borzoi ensemble", against "Borzoi fold-0") |
| SpliceAI (paper Table 3) | `discovery-model-spliceai` | p.21; p.22, Splice Site Classification |
| Pangolin (paper Table 4) | `discovery-model-pangolin` | p.21; p.30, splicing variant benchmarks |
| Enformer (human fine-tuned) and (human not fine-tuned), Table 3 | `regulatory-variant-20261009-model-enformer` | p.21; p.24 ("the original Enformer model") |
| ChromBPNet (Table 3) and chrombpnet (Table 4) | `discovery-model-chrombpnet` | p.21; p.35 (variant evaluations "from ChromBPNet paper") |
| Orca (paper Table 3) | `lit-genomics-20261011-genbench-model-orca` | p.21; p.23 ("the Orca 1 Mb model") |

Page numbers are the printed page numbers of the pinned PDF.

## Decisions

| Item | Decision | Reason |
| --- | --- | --- |
| Relation | `configuration_of` for all nine | The record contract defines it as configuration to what it configures. The Alavi and SpliceAI2 batches use it; the two `family` links on SpliceAI and Pangolin are replaced by it, to the same targets. |
| Target for SpliceAI | `discovery-model-spliceai` | The existing link's target. `catalog-model-spliceai`, which the Alavi and SpliceAI2 configurations use, is an `alias_of` it; the discrepancy rules now resolve aliases. |
| Target level | The model family, not a checkpoint | The paper cites each model's original publication but does not give checkpoints or weights. The configurations keep their "checkpoint not identified" facts. |
| DeltaSplice, Splam, ProCapNet | Not linked | The store has no model record for them. Adding one is separate work. |
| AlphaGenome's own configurations | Unchanged | They keep their `family` link to `catalog-model-alphagenome`, which has no backing claim, so discrepancies involving them stay marked `identityBasis "unreviewed"`. |

No result value, status or evaluation changed.
