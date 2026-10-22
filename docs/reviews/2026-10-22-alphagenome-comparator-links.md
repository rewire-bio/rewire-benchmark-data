# AlphaGenome comparator model links, 2026-10-22

Batch: `data/omics/configuration-links-20261022-alphagenome-comparators`. Issue #174 (RC3); PR #175.

Nine comparator configurations from the AlphaGenome Nature batch now carry a `configuration_of` link to the model they ran, each backed by a `source_checked` claim citing the supplementary methods. Two of them (SpliceAI, Pangolin) had a `family` link to the same target, which is replaced so the batch uses one relation. The research note in the batch gives the table and the decisions.

## How it was checked

- The pinned supplementary methods PDF was re-downloaded and its SHA-256 matched the source record.
- Each claim's locator was read against the PDF text. Page numbers are printed page numbers.
- Each target was checked to be the model record for the same published model (Borzoi, Enformer, SpliceAI, Pangolin, ChromBPNet, Orca), at family level.

## Limitations

- Automated review by a Claude agent; the extractor and reviewer were the same agent in one session. No human review is claimed.
- The links say which published model a comparator is. They do not identify the checkpoint, weights or settings.
- DeltaSplice, Splam and ProCapNet are left unlinked because the store has no model record for them.

## Effect

With these links, the discrepancy rules can join the AlphaGenome paper's Borzoi comparisons with Alavi 2026's, and `discrepancy-ead251c24ba272c1` appears in the derived graph. No result value or status changed.
