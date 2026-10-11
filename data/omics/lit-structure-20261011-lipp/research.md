# Research notes

Part of the 2026-10-11 protein-fitness and structure-design literature pass (window 2025-10-01 to
2026-10-11). The search log is in `data/omics/lit-search-20261011-protein-structure/ledger.jsonl`.

## Why this source

A new benchmark set, open access, with printed per-tool success rates for three co-folding tools
(AlphaFold 3, Chai-1, RoseTTAFold AA), one AI docking tool (DiffDock-L) and one physics-based docking
tool (AutoDock Vina). It is the only in-window co-folding benchmark in these lanes whose per-method
numbers are printed rather than drawn: the molecular-glue and covalent-complex co-folding benchmarks are
subscription only, and the Runs N' Poses journal version prints its success rates in figures.

The 36-complex test set matters for the structural-hypotheses use case: it holds only complexes released
after every tool's training cutoff, and AlphaFold 3 drops from 76.1% to 47.2% on it.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- Two tables, two criteria, four dataset columns, five tools.
- The LiPP columns are the authors' own runs (`independent_paper`); the PoseBusters columns are values
  the authors compiled from the literature (`paper_compilation`), and the AlphaFold 3 PoseBusters cells
  carry the paper's dagger for a different training cutoff (2019-09-30).
- Cells printed as `-` mean the tool has not been evaluated on that set. They are left out, not recorded
  as zero: 4 such cells in Table 2 and 9 in Table 3.
- Braced values are 95% exact binomial confidence intervals (table footnote a), recorded as the result's
  uncertainty.
- The two AlphaFold 3 PoseBusters cells start with the footnote dagger, which the XML holds as a separate
  element; `printed_value` keeps it, so those two strings read "†76.4 {72.1–80.3}" and
  "†80.5 {75.6–84.8}".
- Table 3's criterion is RMSD below 2 Angstrom plus PoseBusters validity. The store's
  `ligand-rmsd-1a-pb-valid-rate` concept is for a 1 Angstrom cutoff, so these results use the generic
  `success-rate` concept with the criterion in `metric_qualifier`.

## Record counts

- benchmark 1, model 1, configuration 5, dataset 4, protocol 7, evaluation 27, result 27 and
  two claims (the relevance judgements): 74 records after review (the source record and one empty protocol were removed).

## For the reviewer

- Check the dagger handling and the origin split between the LiPP and PoseBusters columns.
- Check that leaving out the `-` cells is the right call rather than recording them with a missing reason.
- The relevance judgement for `use-case-structural-hypotheses-experiments` is `proxy` for both criteria;
  the proposed `assessed_by` links are in `use-case-links.json` and are not applied.
