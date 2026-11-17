# Cross-batch record fixes, 2026-11-16

Batch `data/omics/coordinator-fixes-20261116/`. Reviewed and applied by a Claude coordinator-fix
agent that extracted none of the thirteen batches of 2026-11-15 and 2026-11-16. Not human
scientific review. Nothing was reproduced: every change is a reviewed correction to a stored
record, justified by a dated review already in this repository and checked here against the store
and, where the identity needed it, against a primary source.

No value was changed. No result was superseded, no evidence concern was added and no record was
marked disputed. Each changed descriptive field carries a `metadata-correction-*` claim in the
batch that keeps the previous value, as `docs/collection.md` requires.

Eleven stored records changed. The items come from the "for the owner" and "left for the
coordinator" notes of five reviews, each of which deliberately stopped short because the record it
wanted to fix sits outside its own batch.

## 1. `catalog-task-cell-perturbation`: what "unseen perturbations" means

From `docs/reviews/2026-11-15-perturbpfn.md`, ruling 7 and its closing note.

Checked. The task's `attributes.scope_note` read "Predict expression changes after unseen
perturbations." The PerturbPFN batch is the first user of this task: exactly two records in the
store link to it, `perturbpfn-20261115-protocol-sciplex-highest-dose-normalised` and
`perturbpfn-20261115-benchmark-sciplex-highest-dose`, both by `evaluates_task` and both from that
batch. Appendix D.2 of arXiv:2607.23447v1 says in its own words "The held-out drug is not
completely unseen, since lower-dose responses are available". The holdout is a dose of a drug whose
lower doses are in context, not an unseen drug.

The review kept the link, for the reason it gives: the queried condition, a named drug at its
highest dose in a named cell line, was never observed, and the task is a broad catalogue entry with
no metrics of its own. What was owed is the scope note, which as written reads as a claim that every
protocol under this task holds out an agent the model has never seen.

Applied. `attributes.scope_note` now says the held-out condition is a perturbation condition, that
it may be a dose, a time point or a cell context of an agent whose other conditions are available,
that the protocol record says which, and that a result here is not evidence of prediction for an
unseen agent. The record's `description` (empty), `status` (`discovered`), `profile` and
`attributes.task` were not touched; the profile describes the task guide, not the holdout, and
nothing in it asserts unseen agents.

Previous value in `metadata-correction-coordfix-20261116-cell-perturbation-scope-note`.

## 2. The BEELINE GRNBOOST2 and PPCOR entries: parented

From the same review, closing note: the BEELINE `acquired-configuration-*` entries "could now be
linked to this batch's GRNBoost2 and PPCOR method records".

Checked, and wider than the brief asked. The store holds six such entries, not two: three named
GRNBOOST2 and three named PPCOR, one of each per BEELINE source-data CSV
(`acquired-source-0f6c059ffdc338b70a5c`, `...-3156602fda847ae943b4`, `...-31344fb7e5e8ae6b9666`,
the MOESM12, MOESM13 and MOESM14 files of doi:10.1038/s41592-019-0690-6). All six had an empty
`links` array and status `discovered`. No other record in the store names either method, apart from
`discovery-model-grnboost`, which is the earlier Aertslab Spark GRNBoost and not GRNBoost2, and
`lit-cells-networks-20261011-ye2026grn-config-grnboost`, which configures it.

The relation is `configuration_of`: `shared/omics/relations.ts` defines it as configuration to the
model, method or pipeline it configures, and `lit-cells-networks-20261011-ye2026grn-config-grnboost`
is the precedent in the store for a benchmark entry parented to a method record this way. `family`
is for a model family and does not fit a method.

The identity was not taken on the name match. The BEELINE paper is already in the store as
`evidence-discovery-final-beeline` (Europe PMC `PMC7098173` full text XML), and its Methods name
both tools and both references:

- "GRNBoost2 is a fast alternative for GENIE3 ... Like GENIE3, GRNBoost2 trains a regression model
  to select the most important regulators for each gene in the dataset. GRNBoost2 achieves its
  efficiency by using stochastic Gradient Boosting Machine regression with early-stopping
  regularization", citing reference 8, Moerman et al., "GRNBoost2 and Arboreto".
- "PPCOR ... This R package computes the partial and semi-partial correlation coefficients for every
  pair of variables (genes, in our case) with respect to all the other variables ... We use this
  package to compute the partial correlation coefficients", citing reference 7, Kim, "ppcor: An R
  Package".

Those are the two methods the PerturbPFN batch registered: `perturbpfn-20261115-method-grnboost2`
("Tree-based network inference from the arboreto package ...") and
`perturbpfn-20261115-method-ppcor` ("Ranks gene pairs by partial Pearson correlation ... computed
with the ppcor R package"). BEELINE does not print the word Pearson for PPCOR; ppcor's partial
correlation is Pearson by default and the paper names the same package, so the two records describe
one tool. The difference is recorded in the claims rather than smoothed over.

A retrieval note, not a change: the Europe PMC full text XML was re-fetched for this check and
hashes to `18986b6d4aae64c945146730f35acd5fd591366792a2b441879281b4f09e178e`, while the source
record pins `99b59a6941878779b34ab8eed9ea27c8d8967c24fb67b92fce418e7f512d3a11` and carries no
`hash_scope`. Europe PMC regenerates that XML, so this is the same mutable-endpoint pattern four
reviews recorded tonight. The sentences quoted above were read from my own retrieval. Setting
`hash_scope` on that record is a recommendation below, not a change made here.

Applied, to all six records, three fields each: a `configuration_of` link to the matching method,
a `description` that no longer says the method behind the entry is unidentified, and an
`attributes.provenance_note` that keeps its original sentences and adds how the method was
established, that the edge is `configuration_of` to the named method record, and that the run
settings, checkpoint identity and aliases behind the label are still not inferred. Each entry's status stays
`discovered`: the parent is now known, but the BEELINE run settings behind the label still are not,
and nothing about the entries themselves was source-checked here.

Previous values in twelve claims, `metadata-correction-coordfix-20261116-beeline-*`: for each
record one `*-link` claim under field `links:configuration_of:<method>`, and one
`*-description` claim under field `description and attributes.provenance_note` carrying both
previous texts.

## 3. `esmfold2-2026-runs-n-poses-method-openfold3-msa`: the family edge

From `docs/reviews/2026-11-16-poisk.md`, ruling 7, and its remaining-gaps list: "still has no
`family` edge".

Checked. The configuration is named "OpenFold3 (MSA)", its locator is "Figure 2C Runs N' Poses, bar
label OpenFold3 (MSA); Appendix A.2.10" of `model-coverage-esmfold2-2026-v1-source`, and its `links`
array was empty. `poisk-20261115-model-openfold3` is a family-level model record for OpenFold3,
added by the POISK batch and already in the store. The right edge is `family`, not a new model
record and not `configuration_of`: every other configuration of that same ESMFold2 batch carries
`family` to a model record (`...-alphafold3-msa` to `discovery-model-alphafold-3`, the three Chai-1
and ESMFold2 entries to their families, and so on), and the POISK batch's own
`poisk-20261115-config-openfold3` uses `configuration_of` for a configuration of the paper's own
run, which this is not.

Applied. One `family` link to `poisk-20261115-model-openfold3`. The description, status and
`missing_metadata` were not touched; the edge adds a parent and asserts nothing about the
checkpoint, which both records still record as unreported.

Previous value in `metadata-correction-coordfix-20261116-openfold3-msa-family`.

## 4. `gfm-guides-20261014-gpnmsa-source-biorxiv-v2`: the text-layer hash

From `docs/reviews/2026-11-16-gpn-msa-published.md`, ruling 5.

Checked, by re-downloading and re-deriving rather than by trusting the ruling. The record's
`hash_scope` said that a re-download does not reproduce the pinned `artifact_sha256` and that a
fresh copy has "an identical pdftotext -layout text layer", without naming the hash of that text
layer, so nobody could run the check the sentence promises. Ruling 5 names
`c6e95eb807550bb97aa2b8991c013f28fe11742006582c25818fcf90cad30c79` and asks for it to be recorded.

`https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2.full.pdf` answered HTTP 429 with the
17-byte body `error code: 1015`, Cloudflare's rate-limit response, on the first attempts of this
session; a later attempt returned the PDF, 2,247,726 bytes, 37 pages, SHA-256
`688e3788e0555b0b1089f474c5cc7dfd22113fdaa168339c1b9f21490fa22646`. That is not the pinned
`10411077df1ae59614f9a9a9f85384103d54127ba67a9b3c469a4a2d6c33cee4`, as expected: bioRxiv restamps
the container. `pdftotext -layout` (poppler 26.08.0) on it gives a 137,403-byte file whose SHA-256
is `c6e95eb807550bb97aa2b8991c013f28fe11742006582c25818fcf90cad30c79`, exactly the hash ruling 5
names. The text layer is the GPN-MSA preprint v2: its first line reads "this version posted April 6,
2024", it carries the CC-BY-NC-ND 4.0 notice, and "Supplementary Table 4: Ablation study" is the
caption the 136 stored ablation results are located at.

Applied. `hash_scope` keeps every word it had and gains the text-layer hash, the command and the
poppler version that produce it, and this download's size and PDF hash as a second data point for
the container's instability. `artifact_sha256` was not touched: it is not wrong about what was
downloaded on 2026-10-14, and 138 stored results pin it.

Previous value in `metadata-correction-coordfix-20261116-gpnmsa-v2-hash-scope`.

## 5. `reported-task-ed3dd3b83c4505`: the reference to the retired duplicate source

From `docs/reviews/2026-11-16-phylogpn.md`, ruling 3, whose closing note names this record, and
ruling 5, which left the silo decision open.

Checked. `phylogpn-2025` and `evidence-expansion-p2-phylogpn-2025-807f3a26cbfa` pin the same bytes:
both carry `artifact_sha256`
`807f3a26cbfa9b5ce238d92164bd523302c67d1c5794b08273c51cca1acd4224` and the same Europe PMC
`fullTextXML` artifact URL. Ruling 3 made `phylogpn-2025` the survivor, gave it a `supersedes` link
to the duplicate and set the duplicate's status to `superseded`; the store confirms all three.

This legacy task was the only record still citing the duplicate. It named it twice: in `source_ids`,
alongside `phylogpn-2025`, and as the sole entry of
`attributes.benchmark_research.primary_sources`. Nothing else in the store references the duplicate.

Applied, and kept to the reference itself. `source_ids` is now `["phylogpn-2025"]`, which drops a
redundant pointer to a superseded record whose survivor was already listed, and
`benchmark_research.primary_sources` is now `["phylogpn-2025"]`, the same bytes under the surviving
ID. No evidence is withdrawn and no locator moves, because the two records pin one artifact.

What was deliberately not done: the record stays `needs_review`, and the other three legacy records
behind `b2-phylogpn-2025` (`reported-dataset-a28180d33f7a23`, `reported-model-cbbe04b826ceff` and
the retired result itself) were left alone. Ruling 5 is right that retiring or folding in that silo
is a decision of its own, and it is not needed to stop a live record citing a retired duplicate.

Previous values in `metadata-correction-coordfix-20261116-legacy-task-source-ids` and
`metadata-correction-coordfix-20261116-legacy-task-primary-sources`.

## 6. `vep-uc-20261014-model-gpn-star`: one of the six enrichments

From `docs/reviews/2026-11-16-gpn-star.md`, ruling 9, and the recommendation list in
`data/omics/gpn-star-20261116/notes.md`.

Established what "model-record enrichments" meant. The notes name six: `status`, `version`,
`access`, `licence`, `training_data` and `source_ids`, plus `family` or `variant_of` edges to GPN
and GPN-MSA. Ruling 9 declined all of them in that pass, on the ground that they are additions
drawn from claims the batch adds rather than corrections of wrong values, so the
`metadata-correction-*` route does not fit them, and that the claims already carry the content with
this model as their subject. I agree with that reasoning and did not override it.

One of the six is different in kind, and it is the one applied: `source_ids`. The record cites only
`vep-uc-20261014-source-gpn-star`, the mutable Nature URL whose stored hash pins a preview PDF;
the same review established that the URL now serves the version of record, and added `companion_of`
from that record to `gpn-star-20261116-source-nature-2026`. A model record holds no measurement, so
naming the version of record among its sources changes no value, and the exact precedent was set
tonight on `lit-genomics-20261011-traitgym-benchmark-traitgym`
(`metadata-correction-traitgym-20261116-benchmark-source-ids`).

Applied. `source_ids` is now `["vep-uc-20261014-source-gpn-star", "gpn-star-20261116-source-nature-2026"]`.
Previous value in `metadata-correction-coordfix-20261116-gpn-star-source-ids`.

The other five enrichments, and the edges to GPN and GPN-MSA, are recommendations below. They are
not corrections of wrong fields, and two of them (`status`, and whether the Supplementary
Information's "Key differences between GPN-MSA and GPN-Star" supports a family edge) need a
judgement about the record's evidence state across the whole pass rather than a one-field fix.

## Recommendations, not applied

1. `vep-uc-20261014-model-gpn-star`: `version`, `access`, `licence` and `training_data` could be
   enriched from `gpn-star-20261116-claim-software-version`, `-claim-access`, `-claim-licence` and
   `-claim-training-data`, and `status` could move from `discovered` to `source_checked`. The claims
   carry the content today. The status move is a judgement about the record's evidence state across
   the whole of tonight's pass, which is why ruling 9 left it and why I did not take it in a
   fixes-only batch.
2. `vep-uc-20261014-source-gpn-star`: its `review.method_note` says the record was verified as "PMC
   pages after blanking the ncbi_phid and csrfmiddlewaretoken values", which is boilerplate from
   another batch's PMC sources and does not describe a Nature PDF. The gpn-star review flagged it
   and left it. Rewriting it means asserting what verification was actually done on that artifact,
   which needs whoever did it, not a later agent.
3. `esmfold2-2026-runs-n-poses-method-protenix-v1-msa` is the other unparented configuration in that
   batch, and `ucc-research-model-protenix` exists in the store. The POISK review established that
   Protenix-v1 and Protenix-v2 are configurations of that model. The edge was not made here because
   no review has ruled on this record; it is the same shape of fix as item 3 and worth one.
4. `evidence-discovery-final-beeline` has no `hash_scope` and its pinned `artifact_sha256` does not
   reproduce, because Europe PMC regenerates the full text XML. The BenchBench and SpliceAI-2
   precedent applies: say what the hash covers. Out of scope for a batch that only needed to read
   the paper's Methods.
5. The three GRNBOOST2 and three PPCOR entries are one method each, duplicated per source CSV. They
   are now parented, so the duplication is visible as three configurations of one method with no
   distinguishing settings. Whether they should be merged, or kept and given `alias_of` edges, is a
   decision about the acquired silo and not a one-field fix.

## Checks run

All four under the shared heavy lock, held across the whole sequence, with the eleven record edits
applied between the add and the change (`addBatch` calls `loadRecords`, which fails if a stored
record differs from its provenance; `change` hashes each record as it then stands).

| Command | Result |
| --- | --- |
| `records -- add data/omics/coordinator-fixes-20261116/batch.jsonl data/omics/coordinator-fixes-20261116` | 18 records added; 726 quads, 18 records and 17 link targets conform to the shapes |
| the eleven stored-record edits | 11 lines rewritten, one per changed record, in four entity files |
| `records -- change docs/reviews/2026-11-16-coordinator-fixes.md data/omics/coordinator-fixes-20261116` with the eleven IDs | changes recorded for 11 records; 32,613 quads, 901 records and 359 link targets conform to the shapes |
| `records -- check` | 93,187 records match their provenance, up from 93,169 by this batch's 18 claims |
| `check:task-links` | passed: 1,562 protocols checked, 425 still with no task link, all of them in `data/ontology/task-link-baseline.json`, none added and none newly linked by this batch |

Tests, typecheck and the data build were not run; the coordinator runs those. Nothing was committed.
