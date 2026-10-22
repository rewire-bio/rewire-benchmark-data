# Lead optimisation, ranking analogues by affinity: extraction pass

2026-10-22. Extraction for `use-case-lead-optimisation-affinity-ranking` (rewire-benchmark-data #178).
Extractor: Claude extraction agent; no human review claimed. No record in this batch is marked reviewed.

The preceding search pass is `data/omics/lit-search-20261022-uc-leadopt/report.md`, committed as `973c98d`
and `ed2be99` on this branch. This pass extracts the three candidates it named as priorities and does not
re-run its screen.

## What was extracted and why

The use case asks two things: which method ranks a hit's close analogues accurately enough to choose what
to make next, and at what compute cost against free energy calculation. Three sources between them carry
the baseline, the noise floor, the machine-learning comparison and a blind read.

**Ross et al. 2023** is the free energy baseline the store completely lacked, and it is the only source
here that prints the assay noise floor beside a method's accuracy. Table 3 gives both columns: FEP+ on a
curated collection of 1,237 compounds over more than 50 proteins, and a survey of 1,867 compounds whose
affinities were measured in at least two independent assays. All 12 cells were extracted, including the
two the source prints as `N/A`. Tables 2 and 1 (the data sets and the assay survey) are recorded as
composition claims rather than results, because they are counts of the benchmark's contents, not
measurements of a method.

The experimental-reproducibility column is the single most important number for this use case: it says
how well relative affinities reproduce between assays, so it bounds what any method could reach. To let
it sit beside the prediction arms under the same metrics, it is modelled as a `method` record,
'Independent repeat affinity assay', on its own protocol. That is a modelling choice this pass made, not
something the source states, and it is flagged for the reviewer.

**The Boltz-2 supplement** is the only extracted source that puts a machine-learning affinity predictor
beside free energy calculation on the same compounds with measured affinities. Tables 11, 12 and 14 were
extracted in full: every arm, every column, 244 cells. Table 12 is the only one that prints compute cost.
Tables 13, 15 and 16 were not extracted; Table 13 is binary classification, and Tables 15 and 16 are
hit-to-lead rather than lead optimisation.

**Gilson et al. 2026** is the independent read on the CASP16 affinity track. Its affinity results are
figure-only, so nothing was extracted as a result. Six in-text statements carrying numbers were recorded
as claims, including the achievable ceiling derived from resampling under an assumed assay error, which
is the honest frame for every other number in this batch.

## The aggregation question, settled from the methods section

The search pass flagged that Boltz-2's columns are labelled 'target avg.' and asked whether per-series
values are recoverable. They are not, and this pass found the stronger statement that settles what the
columns mean. Appendix D.2.2, 'Evaluation metrics', reads:

> All regression metrics are calculated per assay and averaged across assays with weight proportional to
> the number of compounds in each assay, ensuring that larger assays contribute proportionally to the
> overall performance summary. All predictions are converted to kcal/mol prior to computing the metrics.

Three consequences, all carried onto the records:

1. The aggregation is a **compound-weighted mean across assays**, not an unweighted mean over targets,
   and it applies to every regression column, not only the three labelled 'target avg.'. Every result's
   `metric_qualifier` says 'weighted mean over assays, weight proportional to compound count'.
2. The label 'target avg.' and the methods definition disagree about the unit of aggregation: assays and
   targets are not the same thing, and one target can carry several assays. The source does not reconcile
   them. Every protocol records the discrepancy and it is flagged for the reviewer.
3. The units of the PMAE and MAE columns, which the table headers do not print, are kcal/mol by the
   source's own statement. Each such result carries that in `unit_detail`.

The same section defines the 'Perc. within 1' and 'Perc. within 2' columns as 'the fraction of
predictions with absolute error below 1 and 2 kcal/mol'. Despite the 'Perc.' header the printed values lie
on a 0 to 1 scale, so they are recorded with metric `proportion` and unit `fraction`, with the header
wording noted in `unit_detail`.

Ross Table 3 aggregates the same way in kind: a weighted average over FEP graphs, weight equal to the
number of compounds for the pairwise, R² and Kendall tau metrics and the number of edges for the edgewise
errors, with bootstrap 95% intervals over the graphs or assay comparisons.

## Why every judgement is proxy, not direct

The use case asks about ranking inside **one** series. Every extracted number is an average over series:
Boltz-2's metrics are computed inside one assay and then averaged across assays, and Ross's are weighted
averages over FEP graphs. No source prints a per-series value, and no source prints the spread across
series. So the records support 'on average over these series, method X ranked analogues this well' and
cannot support 'method X would have ranked your series this well', nor any statement about variance
between series. All five judgements are therefore `proxy`, each saying so in its rationale and
limitations.

The route to per-series evidence, deliberately not taken in this pass:
`github.com/schrodinger/public_binding_free_energy_benchmark` (MIT, releases v1.0 and v2.0, both published
2023-06-26) holds the FEP+ per-edge results behind Ross Table 3. Recording values from it would need the
per-edge files pinned with their hashes, a stated aggregation quoted from Ross, and a deterministic script
in the repository under the derivation rule in `docs/collection.md`. The OpenFE per-transformation Zenodo
deposits are a parallel route for the OpenFE arm, with the caveat the search pass recorded: they are
force-field benchmark runs deposited by one author, not the published OpenFE industry benchmark result.

Combining published per-series FEP+ numbers with Boltz-2's series averages in one comparison would mix two
granularities and must not be done.

## Limits carried onto the records in the sources' own words

- FEP+ in both sources: 'The results of FEP+ are intended to show the maximum attainable accuracy of
  current (commercial) FEP simulations by manually adjusting the protocol (input preparation, perturbation
  map, force field) to the system at hand after observing the error with respect to the experiment'
  (Boltz-2 supplement, appendix D.2.2). Ross et al. 2023 describes the same adjustments itself: extra
  rotamers, protonation states, atom mappings and scaled torsions added 'from visual inspection and manual
  intervention' when poor sampling was observed in prior simulations. The limit is on the FEP+
  configuration, on the Ross protocol, on both Boltz-2 FEP protocols, on both sources' `limitations`, and
  as its own claim record.
- ABFE: 'may also represent an optimistic estimate of its prospective performance given that the protocol
  was optimized based this dataset.'
- Leakage control: the mmseqs 90% identity protein clustering was applied to the FEP+ benchmark subsets
  and **not** to CASP16 (released after the training cutoff) or to the Recursion assays (proprietary, and
  not extracted here). Recorded per protocol, as a `control` attribute and as its own claim.
- No uncertainty is printed for any Boltz-2 cell; the bootstrap error bars are figure-only.
- The speed claim against FEP is not backed by a measured FEP+ cost: the FEP+ time cell is '-'.

## Not conflated

The search pass warned that the FEP+ cells quoted in the AEV-PLIG paper (Pearson 0.68, Kendall tau 0.49)
are not the same cells as Ross Table 3 (R² 0.56, Kendall tau 0.51): different metric and probably a
different subset. AEV-PLIG was not extracted in this pass, so no record mixes them, and the constraint is
written onto the Ross FEP+ judgement so a later pass does not.

## Existing protocols that bear on the use case and were left unmapped

Listed in `coverage.json` with reasons. In short: the PLABench CASP16 L1000 and L3000 protocols and its
leakage-controlled ChEMBL35 protocol, the CASF-2016 ranking-power protocol, and the Davis and KIBA DeepDTA
holdout protocols all bear on the question at varying distance. None was given an `assessed_by` link or a
judgement here. That is a gap recorded as a gap, not a decision that they are out of scope. The budget in
this pass went to the three priority sources and to building the FEP baseline the store did not have.

## Vocabulary

One concept added: `millisecond` in `data/vocab/unit.ttl`, with `skos:exactMatch` to
`http://qudt.org/vocab/unit/MilliSEC` and direction inherited from the metric. It is needed for Boltz-2
Table 12's time column, which prints '0.48 GPU ms' and '0.18 GPU ms'; the scheme held second, minute, hour
and day but nothing smaller than a second.

Every metric this batch needed already existed and nothing was added to `metric.ttl`:
`pearson-correlation`, `kendall-tau`, `mean-absolute-error` (for both MAE and MUE, which is the same
quantity under another name, distinguished by `metric_qualifier`), `root-mean-squared-error`,
`coefficient-of-determination`, `proportion`, `accelerator-time` and `cpu-time`. `concordance-index` and
`spearman-correlation` exist and were not needed by these tables.
