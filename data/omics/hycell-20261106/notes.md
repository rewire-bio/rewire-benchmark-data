# HyCell extraction, 2026-11-06

Batch for issue #234: HyCell, Tencent Hunyuan's 16.1M-parameter single-cell embedding model
released on 2026-11-02, and the benchmark in its technical report (dated 2026-11-01).

Extractor: Claude agent. Not reviewed: every record is `needs_review`, no human review is claimed,
and `review-evidence` has not run. Built in `wt/hycell` on `claude/hycell`, off `claude/hyplm-flash`
at b4c9fbf.

## Sources

Pinned to commit `0dcc533cc9f8f76c90ecbfe944df816b6672328a` of `Tencent-Hunyuan/Hyra-results`.

| Record | Artifact | SHA-256 |
| --- | --- | --- |
| `hycell-20261106-source-report` | `AI4Science/hycell/paper/HyCell_Technical_Report.pdf` | `dc2cacf8…6680a28` |
| `hycell-20261106-source-model-readme` | `AI4Science/hycell/README.md` | `cd2eb7ae…c0eecde` |
| `hyra-results-20261106-source-repository-licence` | `LICENSE` (repository root) | `9c9fa225…bfa3b` |
| `hycell-20261106-source-notice` | `AI4Science/hycell/NOTICE` | `66cfe5d9…fb392a` |
| `hycell-20261106-source-citation` | `AI4Science/hycell/CITATION.cff` | `fa5e4edb…57641` |
| `hycell-20261106-source-pyproject` | `AI4Science/hycell/pyproject.toml` | `6a12a9e9…3ab16` |
| `hycell-20261106-source-weights-sidecar` | `src/hycell/checkpoints/hycell-16m/weights.json` | `b1c1d53b…cc3084` |
| `hycell-20261106-source-weights` | `src/hycell/checkpoints/hycell-16m/weights.safetensors` | `11197d80…79d744` |

The repository README is reused as `hyra-results-20261106-source-repository-readme`. The root
LICENSE is new and given a neutral ID, `hyra-results-20261106-source-repository-licence`, because
every Hyra batch rests on it; neither earlier batch created it.

**Checkpoint identity is verified.** I downloaded the 64,439,816-byte weights and hashed them; the
SHA-256 equals the `weights_sha256` the sidecar publishes. This was not possible for HyInv or
HyPLM-Flash. The weights are not archived (64 MB of binary, refetchable).

**Dates.** Printed 2026-11-01; the PDF's CreationDate and ModDate are 2026-11-02T00:14:59+08,
which is 2026-11-01T16:14:59Z, the same day in UTC. Recorded as a note per the standing ruling; no
earlier PDF exists at the pinned commit, so whether a rebuild changed content was not checked.

## Licence

There is no package LICENSE (the path returns 404). What governs the checkpoint:

- The root LICENSE says "Unless otherwise specified, all Tencent-authored materials in this
  repository are licensed under the Apache License, Version 2.0." Its third-party section lists
  SOL-ExecBench and several MIT items, none related to HyCell, and does not mention CELLxGENE.
- NOTICE, CITATION.cff and pyproject.toml each state Apache-2.0 for HyCell.
- No file names the weights explicitly; they fall under the root file's default as Tencent-authored
  material.
- Upstream data terms are separate: NOTICE says the weights were trained on, and the gene vocabulary
  taken from, the CZ CELLxGENE Census release of 8 November 2025, under CC BY 4.0, and that the 512
  scIB lung test cells in `tests/data` are CC BY 4.0.

HyInv and HyPLM-Flash ship their own MIT LICENSE files, which is the root file's "otherwise
specified" case. HyCell ships none, which is why its licence differs.

## How the values were extracted and checked

`extract/parse.py` parses the `pdftotext -layout` text layer with every row label and cell count
asserted, and checks, within rounding: that S equals 0.3 Bio + 0.2 Batch + 0.25 LR + 0.25 kNN for
all 12 rows of Table 3; that Table 3's S equals the mean of Table 4's seven atlases for all 12
models; that Figure 1b's Mean row equals Table 3's Bio for its six models and its atlas cells
average to it; and that Figure 5c contains the six consistency values the prose prints.
`extract/build.py` also asserts the README's two tables equal the report's.

`check-values` gave 60 `in_cell`, 96 `in_row`, 67 `locator_not_parsed`. Its first run gave 36
`not_in_row`, all on the three rows the text layer prints with a superscript glued on (`Stackb`,
`SCimilarityl`, `scPRINTl`); my locators named them without it. Locators now give the row as
printed, with the superscript explained.

The `in_row` values carry a real false-pass risk: Tables 3 and 4 share a page and their row labels,
and HyCell's Table 4 Immune value (0.735) equals its Table 3 S. `extract/check_cells.py` places them
a second way: a `pdftotext -raw` parse anchored at each table's own caption must give the same
ordered values for every row of Tables 3, 4 and 5 and Figure 1b (36 rows, all equal,
`cell-check.tsv`). Raw mode also prints Figure 1b's rotated column headers as plain words, so the
check confirms the figure's column identities, which the layout parse could only infer. The 25 prose
values are not checked by the tool; their only check is the parser's sentence-anchored match.

## Record counts

| Kind | Count |
| --- | --- |
| source | 8 (plus the reused repository README) |
| model | 5 |
| method | 1 |
| configuration | 14 |
| benchmark | 1 |
| dataset | 8 |
| protocol | 16 |
| evaluation | 223 |
| result | 223 |
| claim | 61 |
| total | 560 |

## What was extracted

| Location | Results |
| --- | --- |
| Table 3, S and its four components for 12 systems, seven-atlas means | 60 |
| Table 4, S per atlas for 12 systems | 84 |
| Figure 1b, biological conservation per atlas for 6 models | 42 (its Mean row repeats Table 3) |
| Table 5, fine-tuned, frozen + LR and frozen + kNN on 4 atlases | 12 |
| Section 3.2, cross-tissue batch correction and Bio for PCA and HyCell | 3 |
| Section 4.1, CD4 and gamma-delta T splits | 7 |
| Section 4.2, pseudotime ordering for 4 systems, two aggregations | 8 |
| Section 4.3, decoder fold change and donor consistency | 7 |

Not extracted as results: Table 1 and Table 2 (descriptive; their numbers are claims or dataset
attributes); Table 3's Params and Cells columns (model facts, kept in configurations); Figures 3, 4
and 5a/5b (no labelled values beyond what the prose prints); the README tables (repeats, asserted
equal); the README's throughput (approximate, below).

## The decisions the issue's substance required

### The near-tie, not a win

HyCell's S is 0.735 and Stack's 0.736. The report calls them level, prints no uncertainty anywhere,
and the README bolds Stack's 0.736 as the column's best. Both suite S results carry a `claim_scope`
saying it is not a win for either and that the two ran under different conditions. Nothing records
a rank on S, and the claims quote the report's "level with" wording and the README's bolding.

### The weighting and its components are visible

S is stored beside all four components for every system (Table 3), and the composite protocol
states the weights, that they are the authors' choice, and that another weighting can reorder models
whose components differ, as HyCell's and Stack's do (Bio 0.700 against 0.657, Batch 0.527 against
0.596). S uses a new generic concept, `weighted-composite-score`, whose qualifier carries the weights.
Table 4 prints S per atlas without its components, which every Table 4 result and the protocol state.

### The comparators run under different conditions

Each configuration states its system's condition, and each evaluation copies it into
`comparison.adaptation`, so results under different conditions are never compared automatically:

- HyCell and seven self-supervised models (scFoundation, UCE, Tahoe-x1, TranscriptFormer, scGPT,
  Geneformer V2, STATE-SE): each cell embedded on its own, no labels at inference. One condition,
  152 evaluations, so these compare with each other.
- Stack: batch-grouped inference, sets of 256 cells with each batch's cells encoded together, so
  batch labels are used at inference. 21 evaluations.
- SCimilarity and scPRINT: per cell at inference but pretrained with cell-type labels. 26.
- PCA: fitted to each evaluation atlas on 2,000 highly variable genes, so the fit sees the
  evaluation cells. 17.

HyCell's own description of its inputs (counts plus the measured-gene list) is kept in its
configuration, not in `adaptation`, so it is not mistaken for a different test condition.

### Scope limits

On the benchmark and every protocol: cell-level tasks only, with donor and sample-level tasks such
as a donor's disease state excluded; human genes only, out-of-vocabulary genes dropped; raw counts
with measured zeros required, not a preselected highly-variable-gene matrix. On donor effects I
record the source's own wording, not the issue's: the report says HyCell is trained to discount
donor effects and that donor-level properties "such as sex or disease state, are better read from
embeddings aggregated per donor or sample". It does not say that removing donor effects removes
disease signal; the issue's phrasing is a paraphrase that goes further than the source.

### The excluded atlases

The seven evaluation atlases are the scIB human immune, pancreas and lung atlases (integer-count
parts), PBMC from 10x pbmc4k and pbmc8k, the MultiVINE brain vasculature healthy donors, a
40,322-cell sample of the cross-tissue immune atlas and a 41,140-cell sample of AIDA. A separate,
unnamed development set of eight tissues was also removed from the corpus and used for every design
choice; the issue does not mention it. All seven atlases are new datasets: the store's scIB-derived
pancreas and PBMC sets are different subsets (16k and 8k pancreas cells against HyCell's 10,963).

## Other decisions

- **No `evidence_concerns`.** I first drafted one for the decoder's 555 dataset-code entries against
  532 training datasets. Scoped to the model it would have blocked comparison for every HyCell result
  over a detail none rests on, the same over-broad scoping avoided for HyPLM-Flash's Figure 1b. It is
  a claim. None of the asymmetries makes a value unreliable; they are setting differences, carried by
  `comparison.adaptation`.
- **Throughput is a claim.** "About 1,500 cells per second on one H20 for atlases of 40,000 cells"
  is approximate, names no atlas and appears only in the README. By the rule used for HyPLM-Flash's
  "about 130,000", a printed approximation without an identified workload is a claim.
- **Vocabulary**: `weighted-composite-score`, `scib-bio-conservation-score` and
  `scib-batch-correction-score`, each generic with the estimator in the qualifier (ruling 10). The
  store's `avg-bio` (mean of three metrics) and `average-batch-score` (mean of two) encode estimators
  HyCell's seven- and five-metric means do not match, so reusing them would mislabel the values.
- **Reuse**: models scFoundation, UCE, scGPT, Geneformer, STATE and scPRINT, and the PCA method. New:
  HyCell, Stack, SCimilarity, Tahoe-x1, TranscriptFormer and a pseudobulk-counts method. The store's
  Stack and STATE configurations are challenge submissions, not the published models.
- `facets.method_types` is on every model, method and configuration.

## Gaps

1. No uncertainty is printed anywhere in the report.
2. Table 4's per-atlas S has no per-atlas Batch, LR or kNN; Bio per atlas exists for six models only.
3. Downstream values are printed for a few models; the rest appear only as Figure 4 bars and bounds
   (at most 0.031 ARI; NMI 0.31 to 0.55), which are claims.
4. The development set's eight tissues are not named.
5. No cell list or sampling seed is published for any atlas or for the two sampled atlases.
6. The 23 extra dataset-code entries are not explained.
