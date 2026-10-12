# Research notes

Part of the 2026-10-11 protein-fitness and structure-design literature pass (window 2025-10-01 to
2026-10-11). The search log is in `data/omics/lit-search-20261011-protein-structure/ledger.jsonl`.

## Why this source

The in-window benchmark for protein backbone generation: five generative methods (Chroma, FrameDiff,
FrameFlow, Genie, RFdiffusion) run inside one refolding pipeline (ProteinMPNN for sequence design,
ESMFold for refolding) at nine lengths from 50 to 1000 residues, with designability, novelty, diversity
and runtime printed per method and length. The store already holds Genie 3's own Table 3 and
ProteinBench's design tables; this adds an independent, length-resolved comparison.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- Designability here is sc-TM above 0.5, not the 2 Angstrom sc-RMSD criterion in the store's
  `designability` concept definition, so the cutoff is recorded in `metric_qualifier`. The paper
  discusses both criteria and chooses sc-TM.
- Novelty is the mean pdb-TM of designable backbones against the PDB and is lower-is-better; it is
  recorded with the `tm-score` concept, direction `lower`, and the novelty reading in the qualifier.
- Diversity is unique Foldseek clusters divided by the number of backbones, recorded as `proportion`.
- Efficiency has no printed unit. The text says it is the average time to generate one backbone and that
  current methods take several minutes, but the table does not say minutes, so the unit concept is
  `unit-unreported`.
- Two metric concepts were added to `data/vocab/metric.ttl` for this table: `topsis-relative-closeness`
  (the Ci and mean Ci columns) and `rank` (the rank column). Both need review with the batch.
- Mean Ci and rank are printed once per method and repeat down the group's rows; one record is created
  per method and group, after asserting that the repeated cells agree.

## Record counts

- source 1, benchmark 1, model 4, configuration 5, dataset 1, protocol 7, evaluation 160, result 160:
  339 records.

## For the reviewer

- Check the designability cutoff decision (concept plus qualifier against adding a new concept).
- Check the two new vocabulary concepts and their definitions.
- Check the unreported efficiency unit; if a later reader needs minutes, that is a question for the
  authors, not an inference.
