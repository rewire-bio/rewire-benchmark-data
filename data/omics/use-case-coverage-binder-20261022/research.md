# Research notes: de novo binder design evidence (#176)

What this pass decided and why. The literature search it builds on is
`data/omics/lit-search-20261022-uc-binder/report.md` (search ledger IDs
`search-binder-20261022-s1` to `-s19`, scope decisions dated 2026-10-22 in
`data/omics/scope-audit.jsonl`).

## What this pass is for

The search pass established that the use case cannot be answered in the form it asks. No paper runs
two design methods and a conventional comparator on the same targets, with the same expression and
assay pipeline and the same hit definition. So this pass does not build a ranking. It records honest
per-method, per-target direct evidence whose stated finding is the per-target spread and the
antibody-versus-miniprotein gap, with evidence limits that say in plain words that it does not support
a workflow recommendation.

## The AlphaProteo RFdiffusion arm: what Section S4.1 actually says

The search pass could not read Section S4.1 and flagged the RFdiffusion arm's provenance as
unconfirmed. It is now confirmed, and the answer changes how the arm must be recorded.

> Published experimental success rates of RFdiffusion were based on 96-well biolayer interferometry
> (BLI) measurements [S28], which are impractical for us to perform on our own designs. Therefore, to
> quantitatively compare success rates, we downloaded sequences of the published RFdiffusion designs
> and synthesized and tested them by yeast display (Section S1.2) alongside our own designs. Our
> results matched the published success rates for PD-L1 but were 2-fold lower for IL-7RA (16% versus
> 33%) and 0% for TrkA (versus 6%) (Table S2). This is potentially due to differences between the
> yeast surface environment versus purified proteins, as well as our use of 10- to 20-fold lower
> target concentrations (0.5-1 µM versus 10 µM in [S28]), which may exclude lower-affinity hits.

So the AlphaProteo authors did not run RFdiffusion. They downloaded the design sequences the
RFdiffusion authors published, on figshare, and tested those in their own yeast-display assay. The
assay is shared. The selection funnel is not: the AlphaProteo candidates were chosen by the
AlphaProteo filter from a larger in silico set, 47 to 172 per target, while the RFdiffusion
candidates are the flat 95 designs per target that the RFdiffusion authors chose to publish.
Section S4.1 states one shared assay and says nothing about one shared selection funnel.

**Consequence.** The arms are recorded as separate evaluations sharing the assay protocol, and every
comparison field describing selection, population or budget is null with a reason, which blocks
automatic comparison. The brief said to promote them to a comparison only if S4.1 states one shared
selection funnel. It does not, so they are not promoted.

## Table S2 is the better table, and Table 1 pools three design systems

Table 1's AlphaProteo column is not one design system. Section S2 says so:

> We experimentally tested a design system containing the v1 model against all 7 targets, a v1-based
> system with an improved filter against SC2RBD and PD-L1, and a v2-based system on PD-L1 and TrkA
> (Table S2). Both improving the filter and the model resulted in increased experimental success
> rates. For simplicity, the results in Table 1 are pooled over all tested designs for each target.

Table S2's denominators sum to Table 1's for every multi-system target, so the pooling is confirmed
arithmetically: SC2RBD 94+47+31 = 172, PD-L1 94+31+34 = 159, TrkA 94+37 = 131, TNF-alpha 30+24 = 54.
Both tables are extracted in full, and the use case's exclusions use the Table S2 numbers to make the
coupling point concretely: changing only the filter moved the PD-L1 rate from 9.6% over 94 designs to
16.1% over 31.

## What was deliberately not recorded as a result, and why

### AlphaProteo's compilation rows

Table 1's "Other design methods" and "Other design methods, optimized" rows and Table S2's
"RFdiffusion (published)" row copy values from six other publications, cited by footnote. Two things
make them unusable as results here:

1. The primary sources behind the cells were not retrieved, so nothing pins those numbers.
2. Section S4.2 states that the asterisked values were re-measured by the AlphaProteo authors
   themselves by HTRF, and that for PD-L1 they substituted a different design for the published best
   one: "we found a design with 1000-fold better KD (RFD_PDL1_76, KD=1.6 nM) than the published 'best'
   design (RFD_PDL1_77, KD =1.4 µM). Therefore, we compared our results to the higher-affinity PD-L1
   binder". That is a third party adjusting another group's published result.

This is the same defect the brief identifies in PXDesign's baseline column, so it gets the same
treatment. Every cell of all three rows is transcribed verbatim into
`uc-binder-20261022-claim-alphaproteo-other-design-methods-compilation`, with the footnote key, so
nothing is lost and nothing is comparable. The unretrieved primary sources are an evidence gap.

### Adaptyv per-method hit rates

The brief asked for per-method outcomes from the data packages rather than the figures. The data
packages do not support them. `results/result_summary.csv` has one row per design with a binding flag
and an affinity, but:

- `design_models` is the entrant's own free-text declaration (`["Custom PLM"]`, and so on), and
  Section 4.2 states that the organisers "manually curated and categorized" entrants' prose workflow
  summaries into five categories. Method identity is self-declared and then curated by hand.
- Neither the README's Methods section nor the paper states any aggregation over these rows.
- Section 4.1 reports Figure 8's binder counts "across the 3 binding thresholds" and the body never
  defines those thresholds.
- The file has 402 data rows against the 400 designs the paper says were tested.

`docs/collection.md` allows a value computed from a source's own rows only where the source states the
aggregation in its own words. It does not, so nothing is computed. What is recorded instead is every
per-method outcome the paper prints in prose: BindCraft's five round-1 designs with four expressing and
a best of 491 nM, its ten round-2 beta-sheeted designs with all ten expressing and a best of 82 nM,
the five GB1-linked composite designs that all expressed and none bound, Cradle's 1.21 nM winner, and
the statement that seven of the eight round-2 de novo binders were BindCraft designs. The missing
denominators per method, and the 60 affinities in Figure 10, are recorded as gaps.

### BindCraft's three unreconciled targets

See the retrieval log. Supplementary Data 1's row filter reconciles with the prose for nine of twelve
targets and fails for PD-L1, CrSAS-6 and CbAgo. Nothing is computed from it, so CrSAS-6 and CbAgo have
affinity results and no hit count, and PD-L1's count comes from the prose (7 of 9) rather than from the
file (11 of 13).

### Bennett's computational success-rate columns

Supplementary Methods Table 6's last four columns are filter pass rates, which issue #176 defines as a
step inside the pipeline rather than an outcome. They are extracted, because the instruction is to
extract every cell, but they sit on two separate protocols (`insilico-rf2`, `insilico-af3`) whose
relevance judgements grade them `outside_scope`. They matter for a different reason: they describe the
filter that chose which designs were tested, and the paper itself attributes its low measured rates
partly to that filter being weak.

## Granularity choices

- **A protocol is one hit definition, not one target.** Targets are datasets. So AlphaProteo's
  0.2-threshold screen is one protocol over seven targets and its 1.3-threshold IL-17A screen is
  another, because the threshold is part of the hit definition. This keeps the judgement count at 14
  and lets the per-target spread show inside one comparison group, which is the finding the use case
  needs. Each protocol's `limitations` say that a rate on one target does not transfer to another.
- **Where a source prints a count and no rate, a count is recorded.** BindCraft prints per-target
  numerators and denominators in prose and never prints a per-target rate, so those results carry
  metric `count` with a `numerator` and a `denominator`, not an invented rate. Bennett and AlphaProteo
  print rates, so those carry metric `hit-rate`.
- **Affinities are graded `direct`.** Issue #176 names "the affinities reached" as part of the
  endpoint. Every affinity protocol's constraints say the value is a best-of-subset and name the assay,
  because an HTRF value, a BLI value and a bivalent-Fc apparent value are not interchangeable.
- **Expression and funnel attrition are graded `proxy`.** They are measured, and #176 asks for the
  funnel, but expression is not binding.

## Metric and unit concepts added

Two metrics and three units, in `data/vocab/metric.ttl` and `data/vocab/unit.ttl`:

- `hit-rate`, "Experimental hit rate": the share of candidates that met a measured experimental
  criterion, out of the candidates actually synthesised and assayed. It is declared
  `skos:broader :success-rate` and `skos:broadMatch STATO_0000607`, direction `higher`. It is narrower
  than `success-rate` in two ways that matter: the criterion is a wet-lab measurement, and the
  denominator is the tested set rather than the generated set. Without that distinction a display-signal
  threshold and an in silico filter pass rate would share a concept.
- `dissociation-constant`, direction `lower`, with a scope note that values measured on different
  assays or construct formats are not comparable.
- `nanomolar` and `micromolar`, each `skos:exactMatch` a QUDT `...MOL-PER-L` unit. Separate concepts
  per scale rather than one molar concept with the scale in `unit_detail`, because a comparison checks
  metric, qualifier, unit and direction but not `unit_detail`, so one shared concept would let a
  nanomolar and a micromolar value compare as equals.

No picomolar concept was added, because no result needs one: AlphaProteo's 82 pM best binder is
printed in Table 1 as 0.082 in a nanomolar column. The two unit concepts are used by 38 and 2 results
respectively. The QUDT IRIs were written from QUDT's prefixed-unit naming pattern and were not
dereferenced.

The `skos:broadMatch` on `hit-rate` reuses `STATO_0000607`, the IRI this same file already gives to
`:proportion` as an `exactMatch` and to `:success-rate` as a `broadMatch`. It is confirmed by the
repository's own vocabulary for that meaning rather than invented, and keeping it makes `hit-rate`
consistent with the concept it is declared `skos:broader` of. The IRI was not dereferenced.
`dissociation-constant` carries no external match, because none was confirmed.

The other evidence batch landing in the same pull request (`claude/uc-hitdisc`, issue #177) adds
`enrichment-factor`, `normalized-enrichment-factor`, `bedroc`, `cache-challenge-activity-score`,
`cache-challenge-novelty-score` and `cache-challenge-normalized-hit-score` to the same file. None of
those keys is used or needed here, and none of this batch's keys appears there, so the two sets of
additions do not overlap in key or in meaning.

## Reused IDs

`discovery-model-rfdiffusion` (the AlphaProteo comparator arm's configuration and the Bennett
antibody pipeline's `variant_of` parent) and `discovery-model-proteinmpnn` (`uses_model` from the
BindCraft and Bennett configurations). `discovery-model-genie-3` and `catalog-model-boltz-2` were
searched for and are not used: neither Genie 3 nor Boltz-2 appears in any extracted source with a
measured binder design outcome. The AlphaBind protocols
(`lit-interactions-20261011-mochibind-protocol-alphabind-*`) and the nanobody protocols
(`structural-20261009-protocol-smorodina2026-vhh-*`) were checked and are not linked: they score
affinity and pairing prediction, not design, so they bear on
`use-case-structural-hypotheses-experiments` rather than on this one. No new source record duplicates
an existing URL in `data/entities/sources.jsonl`.

## Status of everything in this batch

Every record is `needs_review`. The relevance judgements and the summary carry a `review` block that
names the extraction agent and says explicitly that a different worker must review them. No
`review.json` is written. Nothing in this batch has been added to the store.
