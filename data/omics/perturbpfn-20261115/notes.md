# PerturbPFN

Requested in issue #246. PerturbPFN (Gao, Hernández-Lobato and Guo; arXiv:2607.23447v1, submitted
26 July 2026, accepted at the 2nd ICML Workshop on Foundation Models for Structured Data) is a
transformer trained only on simulated perturbation episodes. In context it infers a latent gene
graph, sparse intervention targets and strengths, and rolls them through a causal decoder to
predict the expression distribution under a new perturbation. This batch registers the model, its
one reported checkpoint in two run configurations, three evaluation protocols, the comparators,
and every cell of Tables 1, 2 and 3.

Extraction only, by the Claude extraction agent. A different agent reviews it. Every record has
status `needs_review`; nothing is marked reviewed or reproduced.

## Sources

| ID | Artifact | SHA-256 |
| --- | --- | --- |
| `perturbpfn-20261115-source-arxiv-v1` | arXiv PDF v1, https://arxiv.org/pdf/2607.23447v1, 19 pages | `42191efa04b45ca04b2be38b51ea374cd9bf891efe2399d331fec9eaeab200b1` |
| `perturbpfn-20261115-source-arxiv-abs` | arXiv abstract page, for date, comments and licence | `1f42d94a62e4251c24e7e138abd0a4904a6863a3e1ab94c5b155c885c929922a` |

The PDF was downloaded three times on 2026-11-15 with identical bytes. The abstract page was
fetched twice at the unversioned URL with identical bytes; the `v1` URL serves different bytes
(its title carries "v1"), so the hash describes one retrieval of a mutable page.

Text layer for check-values: `artifacts/arxiv-2607.23447v1.pdftotext-layout.txt.gz` (gzip -n -9 of
`pdftotext -layout`, poppler 26.08.0; gz SHA-256
`bb23dabbced4f8a40a42d8d0f74c10a0b27b1c54dddbbb53d314bff9c04221c6`, decompressed SHA-256
`28b341ce3c893e7d734d05de5e522973152a3b0936bf0e6dd16565112eb9c0bb`). Decompress it and pass the
plain text:

```sh
gunzip -c data/omics/perturbpfn-20261115/artifacts/arxiv-2607.23447v1.pdftotext-layout.txt.gz > /tmp/pfn.txt
npm run -s batch -- check-values data/omics/perturbpfn-20261115 perturbpfn-20261115-source-arxiv-v1=/tmp/pfn.txt
```

The paper is CC BY 4.0. The LinkedIn announcement cited in the issue was not retrieved; it is a
lead, not a source.

## How the values were extracted

- `extract/parse_tables.py` parses Tables 1, 2 and 3 from the text layer, asserting every row
  label and header, and asserts that each Table 2 "Avg. ŝ" equals the mean of the three normalised
  columns (largest residue under 0.00006). Output: `extract/tables.json`.
- `extract/build.py` writes `batch.jsonl` from `tables.json` plus hand transcription of the
  descriptive fields.
- `extract/check_tables.py` re-reads every cell a second way (split on runs of two or more spaces,
  indexed by header position) and checks printed value, numeric value and the system each result
  belongs to: 81 of 81 agree.
- `npm run batch -- check-values`: 64 `in_cell`, 11 `in_row`, 6 `locator_not_parsed`, no
  `not_in_row`, `wrong_column` or `overclaimed_in_row` (`value-check.tsv`). The `in_row` rows are
  Table 1 (three label and value pairs per line, so only the row is checked) and the two
  PerturbPFN runtime rows. The six unparsed locators are the five PerturbPFN Table 2 scores, which
  sit on an unlabelled line between the "PerturbPFN (amortized)" and "PerturbPFN (ICL only)" rows,
  and the Section 4.1 prose value 0.6287. `check_tables.py` covers all of them by position.
- `extract/validate_batch.ts` (run under the heavy lock) checks attributes, descriptions,
  relations, link targets and source IDs against the store: no problems. Concept keys pass only
  with `vocab-proposal.ttl` applied (see below).

## Record counts

135 records: 81 result, 14 evaluation, 13 claim, 10 method, 6 configuration, 3 protocol,
2 benchmark, 2 dataset, 2 source, 1 dataset_subset, 1 model.

Results: Table 1, 9; Section 4.1 prose, 1; Table 2, 41 (6 runtimes, 21 normalised scores, 7
overall scores, 7 ranks); Table 3, 30.

## Decisions

1. **Sci-Plex identity.** The store holds Sci-Plex only as two PerturBench Srivatsan20
   covariate-transfer subsets (`lit-cells-networks-20261011-perturbench-v4-data-srivatsan20`,
   `perturbench-dataset-srivatsan20`), with no parent dataset record. This benchmark uses a
   different slice (4 HDAC inhibitors by 3 cell lines, GIM preprocessing, 50 marker genes per
   protocol), so it gets a new `dataset_subset` linked to both with `same_data_as`. No parent
   Sci-Plex dataset record was created because the Srivatsan 2020 paper was not retrieved.
2. **Highest-dose holdout protocol.** Appendix D.2 fixes it: for each of 12 cell line and drug
   pairs the highest dose is the query; context is controls, lower doses of that drug and all doses
   of the other three drugs in that cell line; drug targets are not given; same held-out cells and
   same metric code for every method. The paper says the drug "is not completely unseen". This is
   recorded on the protocol and in a claim; nothing is labelled unseen-drug validation.
3. **Normalised scores.** Table 2 prints only min-max normalised scores, rescaled across the seven
   rows within each protocol, averaged over 12 protocols, then averaged over three metrics
   (Appendix D.3, which says the scores "depend on the included comparison set"). They are recorded
   under a proposed concept `min-max-normalised-score` (overall score under
   `weighted-composite-score`), with a metric qualifier and a limitation on every value. I did not
   add an evidence concern: nothing in the source conflicts, and the metric and qualifier already
   stop automatic comparison with other studies. Raw MD, Pearson r and W2 are only in Figure 2's box
   plots, with no printed values: not extracted.
4. **Ranks.** The "Avg. ŝ / rank" cell prints a score and a bracketed rank. Each is its own result;
   the rank's `printed_value` is "(#1)" and so on, exactly as printed, with numeric value 1.
5. **Runtime.** Table 2 prints two times for PerturbPFN: 1.11 s (ICL only, applying the checkpoint)
   and 432.8 s (amortized, adding the one-time pretraining cost divided over 12 protocols). Both are
   results on the one PerturbPFN evaluation, with different metric qualifiers so the amortized time
   is never compared with inference times. Naive and Observational print "/": no result, recorded as
   `timing_seconds` inapplicable. The spread is recorded as a standard deviation; the caption does
   not say what it is taken over. The amortized and ICL-only rows print the same spread (0.34), as
   expected when a constant is added.
6. **Baselines.** Table 2 compares GIM, CondOT, MLP, RF X-Learner, Naive and Observational; Table 3
   compares Pearson correlation, PPCOR, GRNBoost2, PORTIA and SCENIC. None of GIM, CondOT, RF
   X-Learner, PORTIA or SCENIC was in the store. GRNBoost2 and PPCOR exist only as unlinked BEELINE
   configurations, and `discovery-model-grnboost` is the earlier Spark GRNBoost, so new method
   records were made. The Observational baseline (predict the control distribution) reuses the
   existing `perturbation-ahlmann-20261011-method-no-change`. The four fitted Sci-Plex baselines
   get configurations with the Appendix D.4 settings; Naive and Observational link to their method
   records directly.
7. **Origins.** Table 2 rows and the PerturbPFN Table 3 row are `author_reported` (the PerturbPFN
   authors ran them). The five Table 3 baseline rows are `paper_compilation`: Appendix E.3 says they
   "are taken from the official GeneRNIB score archive".
8. **Separate protocols.** In-prior synthetic recovery (Table 1) and GeneRNIB 300BCG (Table 3) are
   printed as tables and are separate protocols from Sci-Plex. The in-prior protocol carries a
   `task_link_exemption`; GeneRNIB gets a benchmark record built from the PerturbPFN text alone.
9. **Model level.** PerturbPFN is a `family`-level model. The paper names the checkpoint (step 3100
   of a 3,500-step seed-17 run, 14.98M parameters) and says every result uses it; that identity is
   on the two configurations (Sci-Plex and synthetic: single forward pass; GeneRNIB: 190-panel
   aggregation). No weights or hash exist, so the model is not at checkpoint level.
10. **Code and weights.** None released. A GitHub repository search for "perturbpfn" returned 0
    repositories, code search hits were all third-party lists (one records `code_status:
    none-found`), the first author's and Prior Labs' repositories hold none, and Hugging Face
    returned nothing (2026-11-15). Access and licence for code and weights are recorded as
    unavailable, not open.
11. **Method types.** PerturbPFN is `specialist`: it is pretrained on a task-specific synthetic
    prior, not on broad data, although the authors present it as a step towards structured
    foundation models.
12. **Vocabulary.** Six metric concepts are missing and proposed in `vocab-proposal.ttl`:
    `min-max-normalised-score` (21 results), `magnitude-ratio` (Table 1 |ψ| ratio, direction
    unknown because the target is 1), `negative-log-likelihood` (Table 1 Obs. NLL; `log-loss` is
    for class probabilities), and `genernib-regression-precision`, `genernib-regression-recall`,
    `genernib-virtual-cell-score` (Table 3; GeneRNIB's R-Precision is not the retrieval measure
    `r-precision`). The batch validates against the vocabulary with these applied in a scratch copy.

## Gaps

- No code, weights, checkpoint hash or code licence (decision 10).
- Figure 2 raw per-protocol MD, Pearson r and W2: plot only, no printed values.
- Section 4.3 gives edge AUROC 0.9168 and average precision 0.7570 "in the auxiliary
  graph-ranking evaluation (Appendix E)", but Appendix E in v1 describes only the GeneRNIB
  protocol. With no reference edges or protocol the values were not extracted; a claim on the
  source records it.
- The GIM paper and codebase (protocol, preprocessing, marker genes) were not retrieved; the Sci-Plex
  protocol is recorded from the PerturbPFN text.
- The GeneRNIB paper, repository and score archive were not retrieved: the archive version, the
  baseline method versions and the GeneRNIB metric definitions are taken from the PerturbPFN text.
- Cell counts per condition, number of doses per drug, seeds and repeated runs are not reported.
- Whether Table 1 metrics are pooled over 1,024 episodes or averaged over 128 batches is not stated.
- Baseline metrics were recomputed "whenever prediction arrays are available" (Appendix D.4); the
  paper does not say whether any baseline lacked them.
- What the Table 2 runtime spread is taken over is not stated.

## Questions for the reviewer

1. Accept the six proposed metric concepts, or map any of them to an existing concept?
2. Is a metric qualifier plus a limitation enough for the comparison-set dependence of Table 2, or
   should the source carry an `evidence_concerns` entry scoped to the Table 2 results?
3. Is reusing `perturbation-ahlmann-20261011-method-no-change` for the Observational baseline
   right, or should Observational be its own method?
4. Is `paper_compilation` the right origin for the five GeneRNIB archive rows?
5. Should the Sci-Plex subset's `same_data_as` links to the two PerturBench Srivatsan20 subsets
   stay, given they are different slices of the same measurements?
6. Linking the Sci-Plex protocol to `catalog-task-cell-perturbation`: that task's scope note says
   "unseen perturbations", while this protocol is dose extrapolation. Keep the link?
7. Splitting the "Avg. ŝ / rank" cell into a score result and a rank result with printed values
   "0.8870" and "(#1)": acceptable?
8. Keep the Section 4.1 prose value 0.6287 (top-k gate F1) as a result, or drop it as outside the
   tables?

## Files

`batch.jsonl`, `notes.md`, `ledger.jsonl` (search and source-resolution entry),
`scope-audit.jsonl`, `vocab-proposal.ttl`, `value-check.tsv`, `artifacts/` (text layer),
`extract/` (`parse_tables.py`, `tables.json`, `build.py`, `check_tables.py`, `validate_batch.ts`).

## Frozen extraction hash

SHA-256 of `batch.jsonl`: `1b50664da2bfe60287cbe48e3b996d562f6c5594539bb07a06f46505560a12ca`
