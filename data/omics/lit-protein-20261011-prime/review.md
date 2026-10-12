# Review: lit-protein-20261011-prime, 2026-10-11

Reviewer: Claude review agent `reviewer-ps-1`, independent of the extractor `lit-protein-structure`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

The reviewer reported on this batch and `lit-protein-20261011-deepprotein` together. The common sections and this batch's corrections follow, unchanged.

## Verdicts

- `data/omics/lit-protein-20261011-deepprotein` (436 results): **approved with corrections** (five corrections, below).
- `data/omics/lit-protein-20261011-prime` (168 results): **approved with corrections** (six corrections, below).

No printed value, numeric value, uncertainty value or locator was wrong in either batch. Every
correction concerns a metric concept, a unit, an origin, a duplicate record, or wording that
misstates what the source says.

## Source checks

Both artifacts were re-retrieved from Europe PMC with curl and hashed with shasum.

| Source record | URL retrieved | SHA-256 | Match |
| --- | --- | --- | --- |
| `lit-protein-20261011-deepprotein-source-shen2025` | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12553333/fullTextXML | b586921363170806d9f332afb37762ea61f464da6067a3ef0ab8853281964b7f | Yes |
| `lit-protein-20261011-prime-source-prime2026` | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13425921/fullTextXML | f6aac4c25dd93026f87ce9a2e327c95faf4c3014d7f9ae04bb11f208ce047971 | Yes |

Licence, DOI, venue, year and publication status match the JATS metadata. No derivation records are
present in either batch, so no recomputation was needed.

## Value checks

I wrote my own JATS table-grid parser (rowspan and colspan expanded) and compared every result
against the pinned bytes. The collector's `extract/` scripts were not used.

DeepProtein, full comparison of all 436 results:

- 436 of 436 printed values match the cell text after normalising only whitespace around the
  plus-minus sign and the Unicode minus (collector question 7 confirmed: every digit matches; the
  JATS text itself is inconsistent about the spacing).
- 436 of 436 numeric values match the leading number; every printed standard deviation is carried in
  `uncertainty.value` with `n: 5`, and no result carries an uncertainty the cell does not print.
- Coverage: every measurement cell of Tables 2 to 8 is extracted exactly once. The only cells not
  extracted are the twelve `/` cells of Table 7 (GCN, ESM-2-650M, Prot-T5-XL, LlaSMol, ChemLLM and
  Deep Prot-T5 under Secondary Structure), which the Table 5 and Table 7 footnotes explain as models
  that were not run. Leaving them out rather than recording them as zero or as missing-value results
  is correct.
- Non-numeric cells: 2 OOM (Table 2 Stability, Graphormer), 2 OOM (Table 2 Solubility, Graphormer),
  2 "Length Exceeded" (Table 2 Solubility, ESM-1b) and the NaN cells in Tables 2 and 6 are all
  recorded as results with `numeric_value: null` and a stated reason. Confirmed as the right
  treatment: the cell is printed, so it is a published outcome, unlike `/`.
- Metric, direction, unit, qualifier and dataset mapping are uniform within every column group, and
  the train/valid/test row of each table is carried on the dataset and protocol records.

Hand sample, DeepProtein: 49 values (7 per table, Tables 2 to 8, spread across CNN, CNN-RNN,
Transformer, GCN, GAT, NeuralFP, AttentiveFP, ESM-1b, ESM-2-650M, Prot-T5-XL, ProtBert,
Deep Prot-T5, ChemLLM-7B, LlaSMol-Mistral-7B and Prot-T5) read off the rendered table grid and
compared by hand with the record. All 49 match, including the `**` significance marks kept inside
`printed_value` ("74.46 ± 0.21**", "74.00**") and the five-decimal Table 8 values.

PRIME, full comparison of all 168 results:

- 168 of 168 printed values, numeric values and standard deviations match Table 1.
- Coverage: Table 1 has 21 body rows by 8 measurement columns, that is 168 cells, and each is
  extracted exactly once. Nothing is missed and nothing is duplicated.
- Row mapping checked cell by cell: each result's configuration matches the row's model, embedding
  method and fine-tuning tick, including the One-Hot Mean row whose three leading cells repeat the
  row label in the XML.
- Column mapping checked against all three header rows: split, target, metric. R squared maps to
  `coefficient-of-determination` (unitless) and RMSE to `root-mean-squared-error`
  (`unit-unreported`). Table 1 prints no unit for RMSE, so `unit-unreported` is right (collector
  question 4 confirmed for PRIME).

Hand sample, PRIME: 40 values (5 per split-target-metric column, covering every column and every
model scale including the baseline row) read off the rendered grid and compared by hand. All 40
match, negative values and the `-0.0080 ± 0.00` and `1.8726 ± 0.00` cells included.

No independent rendering could be used for the hand sample: the publisher HTML for the PRIME paper
and the Europe PMC HTML for DeepProtein were not retrievable (empty or 404 responses), so the hand
check was read from the rendered table grid of the pinned artifact through my own parser rather than
from a second publication channel. That is the remaining limitation of these value checks.

## Corrections: lit-protein-20261011-prime

**P1. Origin.** All 168 evaluations carry `independent_paper`. The PRIME authors ran every model
themselves, and the fine-tuned rows are their own domain adaptation of ESM-2 and ESM-C, which the
paper presents as its contribution ("domain-specific fine-tuning of the ESM-C 600 M model"). The
store records a benchmark paper's own runs of third-party models as `author_reported` (FLIP,
PFMBench, ProteinBench, ProteinGym), and the DeepProtein batch in this same pass does the same, so
leaving PRIME at `independent_paper` would make two identical situations incomparable. Set
`attributes.origin` to `author_reported` on all 168 evaluations (every ID matching
`lit-protein-20261011-prime-eval-*`).

Add to `lit-protein-20261011-prime-benchmark-prime` `attributes.limitations` exactly:
`Author-reported: the PRIME authors ran every model and also contribute the fine-tuned ESM-RBD variants, which are the best-scoring rows.`

**P2. Uncertainty and aggregation wording.** The records say the number of runs is "not stated",
which understates the source. The Table 1 footnote says: "Performance is reported as the coefficient
of determination (R2) and Root Mean Square Error (RMSE), with ± values representing the standard
deviation across random seeds seen in Supplementary Table 6." The Fig. 1C caption says five folds
are used in Table 1, and the Methods say the stratified evaluation was repeated across three
independent random seeds (seeds 0, 1 and 2). The article does not say whether the printed spread is
across the three seeds or the five folds, and the supplement was not retrieved, so `n` must stay
unset, but the wording must say what is actually printed. On all 168 results set
`attributes.uncertainty.scope` to exactly:

`Standard deviation across random seeds (Table 1 footnote: 'with ± values representing the standard deviation across random seeds seen in Supplementary Table 6'). Table 1 uses five folds (Fig. 1C) and the Methods name three seeds, and the article does not say which of the two the spread is taken over, so no sample count is recorded.`

On all 168 evaluations set `attributes.comparison.aggregation` to exactly:
`Mean with standard deviation across random seeds, over five cross-validation folds (Table 1 footnote; Fig. 1C)`

On all 8 protocols set `attributes.uncertainty_reporting` to exactly:
`{"printed": "mean plus or minus standard deviation across random seeds", "runs": "Five folds (Fig. 1C) and three seeds (Methods) are stated; which the printed spread is taken over is not"}`

Replace the third entry of `lit-protein-20261011-prime-source-prime2026` `attributes.limitations`
(the one beginning "The paper does not state how many runs") with exactly:
`The plus-minus values are the standard deviation across random seeds (Table 1 footnote, pointing at Supplementary Table 6, which was not retrieved). Table 1 uses five folds and the Methods name three seeds, so the sample count behind each spread is not determined by the article.`

**P3. Protocol description is missing the joint head.** The Methods say one multi-task fully
connected network predicts binding and expression jointly ("served as input to a multi-task FCN to
jointly predict binding affinity and expression", five layers, 1000 epochs, learning rate 1e-5). The
batch splits this into eight protocols by target and metric, which is right for the printed columns,
but each protocol's `attributes.protocol` should say the scores come from one joint model, otherwise
the binding and expression columns look like independent runs. Append to `attributes.protocol` on all
8 protocols exactly: ` Binding and expression are predicted jointly by one multi-task fully connected network over the representations (Methods, Input features), so the two targets are not independent runs.`

**P4. Duplicate ESM-C model entity.** The batch adds
`lit-protein-20261011-prime-model-esm-c` although the store already holds `discovery-model-esmc`
("ESMC"), which `pfmbench-method-esm-c` and the two ProteinGym AMFR ESM-C configurations already
point at. Repoint the eight ESM-C configurations
(`lit-protein-20261011-prime-config-esm-c-300m-cls-finetuned`, `...-300m-cls-frozen`,
`...-300m-mean-finetuned`, `...-300m-mean-frozen`, `...-600m-cls-finetuned`, `...-600m-cls-frozen`,
`...-600m-mean-finetuned`, `...-600m-mean-frozen`) so their `configuration_of` link targets
`discovery-model-esmc`, and add to `lit-protein-20261011-prime-model-esm-c` the link
`{"relation": "alias_of", "target_id": "discovery-model-esmc"}` so the two IDs are not read as two
model families. ESM-2 needs no change: it already reuses `catalog-model-esm-2`.

**P5. Duplicate source record.** The store already holds two source records for exactly these bytes:
`prime-2026` (status `discovered`) and `evidence-expansion-prime-2026-f6aac4c2` (status
`source_checked`), both with `artifact_sha256`
`f6aac4c25dd93026f87ce9a2e327c95faf4c3014d7f9ae04bb11f208ce047971`. The batch adds a third,
`lit-protein-20261011-prime-source-prime2026`, which is what `docs/collection.md` warns against. The
new record is the most complete (licence, media type, venue, hash scope, limitations), so keep it and
make the identity explicit rather than repointing 370 records: add to it the links
`{"relation": "supersedes", "target_id": "prime-2026"}` and
`{"relation": "supersedes", "target_id": "evidence-expansion-prime-2026-f6aac4c2"}`.

**P6. Two cells already in the store.** `lit-021` ("0.0248") and `lit-022` ("-0.0162") are the
position-stratified binding R squared cells for ESM-2 8M / Mean / not fine-tuned and
ESM-C 300M / Mean / not fine-tuned, attached to `prime-2026`. The batch re-extracts both, with the
printed spread and a full locator. Add a `supersedes` link to each new result so the pair is not
served twice:

- `lit-protein-20261011-prime-result-position-stratified-binding-r2-esm-2-8m-mean-frozen` gains
  `{"relation": "supersedes", "target_id": "lit-021"}`
- `lit-protein-20261011-prime-result-position-stratified-binding-r2-esm-c-300m-mean-frozen` gains
  `{"relation": "supersedes", "target_id": "lit-022"}`

The old values are not edited and the old records keep their claims.

**Optional, not required for approval:** `lit-protein-20261011-prime-data-rbd-mutants` records the
variant total as `unextracted`. The Results state the dataset is 347,432 SARS-CoV-2 RBD sequences, so
the field can be filled with that figure and the locator "Results, first paragraph" instead of a
missing-metadata entry.

**Confirmed without change in this batch:** every printed value, numeric value, spread, locator,
metric concept, direction, qualifier and configuration mapping; full coverage of Table 1; the
decision to extract Table 1 only, the other analyses being figures; `unit-unreported` for RMSE; the
One-Hot Mean row as a single baseline configuration with a `method` record rather than a model.
Nothing in this batch overlaps another open lit branch: no other `claude/lit-20261011-*` branch and
no other `../rewire-benchmark-data-lit-*` worktree adds a batch, result or source record for
10.1186/s12864-026-12976-5, beyond the two pre-existing store sources and `lit-021` and `lit-022`
handled in P5 and P6.

## Checks run and their outcomes

| Check | Outcome |
| --- | --- |
| Re-retrieve both artifacts and match SHA-256 | Both match |
| Full automated comparison of all 436 DeepProtein values with my own JATS parser | 436 of 436 printed and numeric values and spreads match |
| Full automated comparison of all 168 PRIME values with my own parser | 168 of 168 match |
| Cell coverage of the chosen tables | DeepProtein Tables 2 to 8 and PRIME Table 1 fully covered; only the twelve justified `/` cells omitted |
| Hand sample against the rendered table | 49 DeepProtein and 40 PRIME values, every table and column, all match |
| Metric, qualifier, direction, unit, uncertainty, denominator, dataset and split mapping | Two faults: C1 (metric concept) and C2 (unit); PRIME wording fault P2 |
| Non-numeric and omitted cells | Confirmed as recorded (collector question 5) |
| Printed spacing and footnote markers | Confirmed, digits match (collector question 7) |
| Origin and author overlap | DeepProtein correct; PRIME wrong, P1 |
| Locators | All resolve to exactly one cell in both batches |
| Duplicates against `data/entities` and `data/evidence` | DeepProtein clean; PRIME has P4, P5, P6 |
| Duplicates against other open lit branches and worktrees | None for either DOI |
| Scope fit | Both in the `protein-fitness` lane and in scope |
| Relevance judgement against the use case | Approved as proxy with C4 |
| Proposed summary text | None proposed; existing pinned summary needs the edit above once the protocol is linked |

## Remaining gaps after this review

- The PRIME supplement (Supplementary Table 6) was not retrieved, so the sample count behind each
  printed spread stays undetermined.
- The DeepProtein supplementary files and the wandb runs named in the article were not retrieved; the
  five-seed protocol is taken from the table footnote.
- No second publication channel was reachable for either paper, so the hand sample rests on the
  pinned JATS bytes rather than on an independent rendering.
- `npm test`, `npm run typecheck` and `npm run build` were not run by me: the corrections above have
  to be applied first, and the collector's branch already carries the records in the store, so the
  validation belongs with the change that applies them.

## Corrections applied

Applied by the extractor in `extract/extract_prime.py`, as the reviewer specified, before the batch was added to the store.

1. P1: all 168 evaluations are `author_reported`; the benchmark carries the author-reported limitation verbatim.
2. P2: every result's `uncertainty.scope`, every evaluation's `comparison.aggregation`, every protocol's `uncertainty_reporting` and the source's third limitation use the reviewer's text verbatim. `n` stays unset.
3. P3: every protocol's `attributes.protocol` ends with the reviewer's sentence on the joint multi-task network.
4. P4: the eight ESM-C configurations point at `discovery-model-esmc`; `lit-protein-20261011-prime-model-esm-c` carries `alias_of` `discovery-model-esmc`.
5. P5: the source supersedes `prime-2026` and `evidence-expansion-prime-2026-f6aac4c2`.
6. P6: the two re-extracted position-stratified cells supersede `lit-021` and `lit-022`. The old records are not edited.
7. Every record is `source_checked`; each result's `review` block names the reviewer and keeps the extraction note.

## Not applied

- The optional dataset total. The 347,432 sequences the reviewer cites are the "outbreak" dataset (Methods, Data collection and curation), while Table 1's binding and expression values come from the deep mutational scanning data, so the figure would mislabel this dataset. `total` stays `unextracted`.

## Records after correction

- benchmark: 1
- configuration: 21
- dataset: 1
- evaluation: 168
- method: 1
- model: 1
- protocol: 8
- result: 168
- source: 1
