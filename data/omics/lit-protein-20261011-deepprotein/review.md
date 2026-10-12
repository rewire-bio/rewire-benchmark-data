# Review: lit-protein-20261011-deepprotein, 2026-10-11

Reviewer: Claude review agent `reviewer-ps-1`, independent of the extractor `lit-protein-structure`. No human review claimed. Source transcription is not reproduction.

## Reviewer's report (verbatim)

The reviewer reported on this batch and `lit-protein-20261011-prime` together. The common sections, this batch's corrections, the relevance judgement and the use-case summary sections follow, unchanged.

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

## Corrections: lit-protein-20261011-deepprotein

**C1. The regression correlation is Spearman, not an unsettled coefficient.** This answers collector
question 1, and it is a correction, not a confirmation. The article's own Evaluation metrics section
defines the metric: "Spearman rank correlation ( ρ ), also known as Spearman's ρ , is a
nonparametric statistical test that measures the association between two ranked variables. A higher
ρ value indicates better performance." It defines R squared separately in the same section. The
Figure 3 caption wording "Spearman (Pearson) Coefficient" is loose caption text covering both
regression metrics of the figure; it does not unsettle the definition. Apply to the 51 results whose
IDs match `lit-protein-20261011-deepprotein-result-fluorescence-rho-*`,
`lit-protein-20261011-deepprotein-result-stability-rho-*` and
`lit-protein-20261011-deepprotein-result-beta-lactamase-rho-*` (17 each), and to the three protocols
`lit-protein-20261011-deepprotein-protocol-fluorescence-rho`,
`lit-protein-20261011-deepprotein-protocol-stability-rho` and
`lit-protein-20261011-deepprotein-protocol-beta-lactamase-rho`:

- `attributes.metric`: `correlation` becomes `spearman-correlation`
- `attributes.metric_qualifier` becomes exactly: `Spearman rank correlation, as defined in the article's Evaluation metrics section; supervised split`
- leave `metric_direction` (`higher`) and `unit` (`unitless`) unchanged.

On the protocol records also replace the description text (see C3) and leave `replicates` as it is.

On `lit-protein-20261011-deepprotein-source-shen2025`, replace the single
`attributes.evidence_concerns[0].message` with exactly:

`Figure 3's caption calls the regression metric 'Spearman (Pearson) Coefficient' while the Evaluation metrics section defines rho as Spearman rank correlation and R2 separately. The section's definition is taken as authoritative and the rho columns are recorded as Spearman; the caption wording is noted so a reader of the figure is not surprised.`

Keep that entry's `source_id`, `source_locator` and `artifact_sha256` as they are and set
`review_date` to the date of the applied change. This edits an unreviewed note the collector wrote
as a question for review; it does not erase a reviewed finding.

Also remove the second entry of `attributes.limitations` on the same source record (the one
beginning "Tables 2 to 7 print the metric for the regression tasks as rho") and put in its place
exactly:

`The regression correlation columns are printed as rho. The Evaluation metrics section defines rho as Spearman rank correlation; Figure 3's caption calls it 'Spearman (Pearson) Coefficient'. The section's definition is used.`

**C2. ROC-AUC unit.** Table 5 prints ROC-AUC on the same 0 to 100 scale as the PR-AUC, accuracy and
averaged F1 columns of this batch, which are recorded as `percent`, but the nine ROC-AUC results are
recorded as `unitless`. A 0 to 100 AUROC recorded as unitless can be compared against the store's
many 0 to 1 AUROC values, which is exactly what the unit field exists to prevent. Set
`attributes.unit` to `percent` on these nine results, leaving the qualifier and direction unchanged:

`lit-protein-20261011-deepprotein-result-iedb-roc-auc-cnn`,
`...-result-iedb-roc-auc-cnn-rnn`, `...-result-iedb-roc-auc-transformer`,
`...-result-pdb-jespersen-roc-auc-cnn`, `...-result-pdb-jespersen-roc-auc-cnn-rnn`,
`...-result-pdb-jespersen-roc-auc-transformer`, `...-result-sabdab-liberis-roc-auc-cnn`,
`...-result-sabdab-liberis-roc-auc-cnn-rnn`, `...-result-sabdab-liberis-roc-auc-transformer`.

Make the same change to `attributes.unit` on the three protocols those results hang from
(`...-protocol-iedb-roc-auc`, `...-protocol-pdb-jespersen-roc-auc`,
`...-protocol-sabdab-liberis-roc-auc`) so protocol and results agree.

**C3. Protocol description text artifact.** The three rho protocol records read "Scored by printed as
rho; Figure 3's caption calls it ...", which is assembled text, not a sentence. Replace
`description` on each with, respectively:

- `lit-protein-20261011-deepprotein-protocol-fluorescence-rho`: `Fluorescence regression, as distributed with TAPE. Scored by Spearman rank correlation on the task's test split.`
- `lit-protein-20261011-deepprotein-protocol-stability-rho`: `Protein stability regression, as distributed with TAPE. Scored by Spearman rank correlation on the task's test split.`
- `lit-protein-20261011-deepprotein-protocol-beta-lactamase-rho`: `Beta-lactamase activity regression, as distributed with PEER. Scored by Spearman rank correlation on the task's test split.`

**C4. Relevance judgement fields.** `use-case-mapping-lit-protein-20261011-deepprotein-stability-rho`
is approved as `proxy` (see the judgement section below), but two fields must be filled before it is
set to `source_checked` and pinned:

- `attributes.reviewed_evaluations`: the 17 evaluations on the protocol, that is every ID matching
  `lit-protein-20261011-deepprotein-eval-stability-rho-*` (attentivefp, chemllm-7b, cnn, cnn-rnn,
  deep-prot-t5, esm-1b, esm-2-650m, gat, gcn, graphormer, llasmol-mistral-7b, mpnn, neuralfp, pagtn,
  prot-t5-xl, protbert, transformer). `excluded_evaluations` stays empty: the Graphormer cell is an
  OOM result, which is a published outcome rather than an inapplicable evaluation.
- `attributes.constraints`: replace the second entry (the one about the coefficient type not being
  settled) with exactly: `Spearman rank correlation on one supervised split; not comparable with zero-shot stability rankings or with ddG values in kcal/mol.`
- `attributes.limitations`: add exactly this fourth entry, because the truth set matters here and the
  judgement does not yet say what it is: `The TAPE stability truth set is proteolysis-derived stability of designed mini-proteins, so it is biased towards small designed domains and away from the larger natural proteins the use case asks about.`

**C5. Prot-T5 identity (collector question 8).** Keeping Table 8's "Prot-T5" as a configuration
separate from Tables 2 to 7's "Prot-T5-XL" is confirmed: the article never says they are the same
checkpoint, and Table 8 reports resource usage for three representative methods rather than scores.
Add to each of `lit-protein-20261011-deepprotein-config-prot-t5` and
`lit-protein-20261011-deepprotein-config-prot-t5-xl` an attribute
`identity_note` with exactly: `Table 8 prints 'Prot-T5' and Tables 2 to 7 print 'Prot-T5-XL'. They are kept as separate configurations because the article does not state that they are the same checkpoint; their values must not be pooled.`

**Confirmed without change in this batch:** every origin is `author_reported`, which matches the
store's convention for a benchmark paper that runs the compared methods itself (FLIP, PFMBench,
ProteinBench and ProteinGym records all do this), and the author-overlap caveat is already on the
benchmark, the source and the judgement, naming DeepProt-T5 as the authors' own model. Table 8's
`runtime` in hours and `peak-memory` in gigabytes, with `uncertainty` missing as unreported, are
right: Table 8 prints single values. The sixteen local model records are not duplicates; the store
holds no model entity for Prot-T5, ProtBert, Graphormer, PAGTN, AttentiveFP, NeuralFP, MPNN, GAT,
GCN or either chemistry LLM, and ESM-1b and ESM-2 correctly reuse `uc20260930-model-esm-1b` and
`catalog-model-esm-2`. No source record for this DOI or PMC ID exists anywhere in the store, so the
source record is new, not a duplicate. Nothing in this batch overlaps another open lit branch: no
`claude/lit-20261011-*` branch and no `../rewire-benchmark-data-lit-*` worktree holds a record,
batch or source for 10.1093/bioinformatics/btaf165 or PMC12553333.

## Relevance judgement

One judgement falls in my batches:
`use-case-mapping-lit-protein-20261011-deepprotein-stability-rho`, on
`use-case-protein-stability`, proposing `assessed_by`
`lit-protein-20261011-deepprotein-protocol-stability-rho`.

**Approved as `proxy`**, with the field changes in C4 and no change to the use case's inputs,
output or exclusions.

Endpoint against the use case: the use case brings a wild-type sequence plus substitutions and a
defined construct and experimental stability endpoint, and wants per-method correlation and error on
held-out or dissimilar proteins, antisymmetry on reverse variants, and the change from small domains
to larger proteins. The protocol gives per-method Spearman correlation on one supervised split of
the TAPE stability task, whose truth set is proteolysis-derived stability of designed mini-proteins.
The quantity is the right kind, so it is evidence; the split is supervised rather than held-out by
protein, there is no reverse-variant arm and no kcal/mol error, so it is not direct. Proxy is the
correct call, and it is the right instrument here rather than widening the use case: nothing in this
evidence justifies touching `inputs` or `exclusions`, and changing those fields would withhold all
fifteen existing judgements until they were re-pinned.

The use case's exclusion "Transfer of a benchmark result to a different target protein, protein size
or assay without validation on that protein" is carried by the judgement's constraints, and the
author-overlap caveat (the DeepProtein authors ran every baseline and also introduce DeepProt-T5,
which tops several tasks) is already in its limitations. The truth-set bias was missing and is added
in C4. Every entry in `excluded_evaluations` is accounted for: there are none, and that is right.

The other four judgements in the collector's question 9 belong to the LiPP and AlphaFold against
ESMFold batches, not to mine, and I have not reviewed them. Collector questions 2, 3 and 6
(the two new vocabulary concepts, the Scaffold-Lab designability cutoff and the LiPP origins) are
likewise outside these two batches.

## Use-case summary text

The collector proposed no new summary text, for either batch. The use case already carries a
reviewed, pinned summary claim, `use-case-summary-protein-stability`, whose opening sentence counts
the comparisons it describes ("Three published comparisons add evidence beyond the AMFR assay"). Once
the DeepProtein stability protocol is linked, the page carries a fourth comparison and that count is
wrong, so the summary needs the minimal edit below and a re-pin with the dated review. Adding an
`assessed_by` link does not withhold the other judgements: the use case's pinned fields do not
include `links`.

The final approved summary text, verbatim, is the existing text with its first sentence replaced and
one sentence added before the closing two sentences. Nothing else in it changes:

`Four published comparisons add evidence beyond the AMFR assay. Each uses its own dataset, split and metric, so values cannot be pooled. Pancotti et al. 2022 ran 21 predictors on S669, 669 experimental ddG variants in proteins dissimilar to the main training sets, plus their reverse variants; several of the tools, including ACDC-NN, DDGun, INPS and I-Mutant, were developed by the paper's own authors. The highest Pearson correlation on direct variants was 0.5 (MAESTRO), but MAESTRO fell to 0.2 on reverse variants with a bias of -0.57, while tools built to be antisymmetric, such as INPS-Seq, kept 0.43 in both directions with a bias of 0. On all 1,338 variants the highest correlations were 0.62 (PremPS) and 0.61 (ACDC-NN and INPS-Seq). Dieckhaus et al. 2024, the ThermoMPNN developers, held out proteins clustered at 25% identity in the mega-scale proteolysis set: ThermoMPNN reached Pearson 0.75 and RMSE 0.71 kcal/mol, retrained RaSP 0.71 and Rosetta 0.53 with RMSE 5.18. On a homologue-free FireProtDB split ThermoMPNN reached 0.65 against 0.59 for retrained PROSTATA and 0.47 for retrained RaSP. Chu et al. 2024, the ESM therm developers, show the limit of transfer: on held-out mega-scale domains of 40 to 72 residues RaSP and ELASPIC-2 reached Spearman 0.64 and Rosetta 0.61, but on six single proteins of 177 to 501 residues their fine-tuned model scored between -0.11 and 0.06, while ELASPIC-2 scored 0.47 to 0.58 on five of them and Rosetta 0.33 to 0.49. The DeepProtein benchmark adds a supervised rather than held-out view on the TAPE stability task, where its authors ran every method themselves and also contribute the best-scoring fine-tuned model: Prot-T5-XL reached Spearman 0.767 plus or minus 0.008, their Deep Prot-T5 0.725, ESM-2-650M 0.689 plus or minus 0.020, ESM-1b 0.682 plus or minus 0.077, a CNN 0.715 plus or minus 0.025 and the graph baselines 0.013 to 0.443, with Graphormer out of memory; the truth set is proteolysis-derived stability of designed mini-proteins, so it says nothing about larger proteins or reverse variants. Before choosing a method, a user still needs to validate transfer to proteins larger than the small domains these models were trained on, and to check antisymmetry on reverse variants, which only one of these comparisons tests across many tools. None of the comparisons covers the AMFR construct, and none establishes whole-protein function, fitness or pathogenicity.`

Every number in the added sentence is a stored printed value from Table 2's Stability column
(`lit-protein-20261011-deepprotein-result-stability-rho-prot-t5-xl` 0.767 ± 0.008, `-deep-prot-t5`
0.725, `-esm-2-650m` 0.689 ± 0.020, `-esm-1b` 0.682 ± 0.077, `-cnn` 0.715 ± 0.025, `-attentivefp`
0.013 ± 0.004 and `-gcn` 0.443 ± 0.017 as the ends of the graph-baseline range, `-graphormer` OOM).
The sentence names the author-reported status and the truth-set bias, and it recommends nothing.

If the team would rather not touch the pinned summary in this pass, the alternative is to hold the
judgement at `needs_review` so the protocol is recorded but not served, and leave the summary alone.
It is not acceptable to link the protocol and leave the "Three published comparisons" count
standing.

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

Applied by the extractor in `extract/extract_deepprotein.py`, as the reviewer specified, before the batch was added to the store.

1. C1: the 51 rho results and the three rho protocols use `spearman-correlation` with the reviewer's qualifier verbatim. The source's evidence concern message and its second limitation are the reviewer's text verbatim.
2. C2: the nine ROC-AUC results and their three protocols use unit `percent`.
3. C3: the three rho protocol descriptions are the reviewer's text verbatim.
4. C4: the judgement lists the 17 stability rho evaluations in `reviewed_evaluations`, its second constraint is the reviewer's text and its fourth limitation the reviewer's truth-set caveat. `headline_metric` follows the protocol's metric, `spearman-correlation`.
5. C5: both Prot-T5 configurations carry the reviewer's identity note verbatim. The reviewer named the attribute `identity_note`, which is not declared for configurations in `shared/omics/attribute-registry.ts`; the declared `model_identity_note` holds the text.
6. Every record except the judgement is `source_checked`; each result's `review` block names the reviewer and keeps the extraction note.

## Judgement and use-case summary

The reviewer approved the judgement as `proxy` and gave a revised use-case summary. Correction C1 also keeps an `evidence_concerns` entry on this batch's source. The use-case derivation (`shared/omics/use-cases.ts`, `cleanSource`) withholds every judgement whose source has any evidence concern, and a summary may only cite clean sources, so serving the judgement and the revised summary is not possible while the concern stands. The reviewer named the fallback: "hold the judgement at `needs_review` so the protocol is recorded but not served, and leave the summary alone." That is what was applied, after the conflict was put to the team lead and no other instruction came back:

- the judgement carries every C4 change, is linked from `use-case-protein-stability` with `assessed_by`, and stays `needs_review` (draft), with a `reason` saying why it is not shown;
- the use case's reviewed summary is unchanged and still published;
- every judgement that was active on the use case before this batch is still active.

Serving the judgement needs either the concern cleared (the reviewer's own text calls the caption wording a note rather than an unresolved conflict) or a re-review; then the summary text in the report above can be applied verbatim and re-pinned.

## Records after correction

- benchmark: 1
- claim: 1 (relevance judgement)
- configuration: 18
- dataset: 17
- evaluation: 436
- model: 16
- protocol: 60
- result: 436
- source: 1
