# Research notes

Part of the 2026-10-11 protein-fitness and structure-design literature pass (window 2025-10-01 to
2026-10-11). The search log is in `data/omics/lit-search-20261011-protein-structure/ledger.jsonl`.

## Why this source

An independent comparison, by authors unconnected to any of the three tools, of AlphaFold2, AlphaFold3
and ESMFold on 1666 monomers and 994 dimers from the PDB released 2022 to 2024 with no close homologue
among pre-2022 structures. It is the largest in-window held-out-by-date structure comparison in these
lanes whose per-tool numbers are printed rather than drawn, and it separates the results by confidence,
experimental method and template quality, which is what the structural-hypotheses use case needs.

## Extraction notes (written before review; `review.md` takes precedence where they differ)

- Every cell is a count of predicted structures in a predictive class, so the metric concept is `count`
  with the class and the column subset in `metric_qualifier`, unit `count`.
- Direction is `unknown`: a high count is good for the accurate classes and bad for the incorrect class.
- One protocol per table column (the counted subset), one evaluation per tool and column, one result per
  predictive class. 18 protocols, 54 evaluations, 216 results.
- AlphaFold3 was run through its web service while AlphaFold2 (v2.2.3) and ESMFold were run locally; this
  is recorded on the configurations.
- TQ is template quality, defined in the text as sequence identity multiplied by query coverage.

## Record counts

- source 1, benchmark 1, model 1, configuration 3, dataset 2, protocol 18, evaluation 54, result 216 and
  two claims (the relevance judgements): 298 records.

## For the reviewer

- Check the class definitions in `metric_qualifier` against the Materials and methods thresholds, in
  particular the "special cases" class (LDDT below 0.7 and RMSD below 3.0 Angstrom).
- Check the dimer classes: the paper names high, medium and acceptable quality as DockQ bands but does
  not print the band boundaries in the table, so the qualifier says "as the paper defines it".
- The relevance judgements for `use-case-structural-hypotheses-experiments` are `direct` for monomers and
  `proxy` for dimers; the proposed `assessed_by` links are in `use-case-links.json` and are not applied.
