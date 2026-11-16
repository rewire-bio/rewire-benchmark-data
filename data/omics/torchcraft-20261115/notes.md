# TorchCraft

Requested in issue #243. TorchCraft is a protein binder design framework published by the TorchCraft
Team at Changping Laboratory as arXiv:2609.19770v1 on 17 September 2026. It optimises a trainable
amino-acid logit matrix through a frozen all-atom structure predictor and discretises the result into
a sequence. This batch registers the software suite, the predictor implementation, the scoring
component and the design procedure as four separate records, pins their configurations and sources,
and extracts every printed numeric value in the preprint.

Extraction only. A different agent reviews it. No record is marked reproduced, no design run or
measurement was repeated, and no value was read off a figure.

Frozen extraction hash: `batch.jsonl` sha256
`2cb2377abde1bb43b44a4ff84c55023d18cc91ab691ce95f135bb37e53647f22` (165 records).

Timing, for the record: the artifacts were retrieved on 2026-11-15 between 23:36:17Z and 23:42:58Z,
the search cutoff is 2026-11-15, and the extraction was finished and every value last checked just
after 00:00Z on 2026-11-16, which is the review date on each record.

## Sources

| ID suffix | Artifact | SHA-256 |
| --- | --- | --- |
| `source-arxiv-v1` | arXiv PDF v1, the primary source | `f8145b5b95552dd30996eda2940507c0f32d09adfc60f44f28458e7872788f21` |
| `source-arxiv-abs` | arXiv abstract page, for the date, version and licence | `cac39821a99125fe2f245a30d72d8f1465a3a99b784298ada10f68748b2236a0` |
| `source-project-site` | torchx-cpl.github.io, official project site | `fa95060dad51bd3e04278b48c7e3bc62c66f8f909db3871e654f79d5a98dcd3c` |
| `source-torchx-readme` | TorchX README at commit `ebf9dc6` | `88da821dfed6d76a6d1d2efd1e3e124a18f35c07d6fdf45a8e374fc2c35fccf0` |
| `source-torchx-licence` | TorchX LICENSE at commit `ebf9dc6` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |
| `source-torchcraft-gpu-readme` | `torchcraft_gpu/README.md` at commit `ebf9dc6` | `77a6b7b67f29a7931e58e5ee2bcbaa5efa08a5ff33debd6d658f85ae305ec313` |
| `source-huggingface-torchfold` | Hugging Face dataset page, gated, not signed in | `39268aab20e07bb615c1b96c8eb5684686dc953036a7d062dec7684581fbdfcf` |

All seven were refetched at 2026-11-16T00:02Z. Six came back byte-identical, so their hashes are not
per-download stamps. The Hugging Face page differed only in per-request CSS class hashes
(`hf-sanitized-...`); the licence tag, the gate text and the dataset card were identical, so for that
page the hash describes one retrieval.

Not archived in `artifacts/`: the arXiv licence is the arXiv.org perpetual non-exclusive distribution
licence 1.0, which grants no redistribution right, so neither the PDF nor its text layer is committed.
Every stored value was read from the `pdftotext -layout` text layer, whose sha256 is
`90f1da5f8a936766087beba0ade3f038f5b69504b9f581b42f2391f5640c5e6b`. To reproduce it:

```sh
curl -sSL -o arxiv-2609.19770v1.pdf https://arxiv.org/pdf/2609.19770v1
shasum -a 256 arxiv-2609.19770v1.pdf     # f8145b5b9555...
pdftotext -layout arxiv-2609.19770v1.pdf arxiv-v1-layout.txt
shasum -a 256 arxiv-v1-layout.txt        # 90f1da5f8a93...
```

The arXiv HTML rendering (`https://arxiv.org/html/2609.19770v1`, sha256
`69d9afd5e726d003253c0849c5f58457814293bc78dfa856073bb0f52f9d2b5d`) was retrieved as a cross-check.
No value was taken from it, so it gets no source record; the scope audit records the decision.

## Four entities, not one

The issue asked for the suite, the predictor, the scoring component and the design procedure to be
kept apart, and for no new pretrained generative model identity. What the source says, and what was
recorded:

| Thing | Kind | ID suffix | Why that kind |
| --- | --- | --- | --- |
| TorchX | `method`, entity level `suite` | `method-torchx` | A software stack of four modules (README, 'Repository layout'). Nothing is evaluated at this level. |
| TorchFold | `method`, entity level `method` | `method-torchfold` | The predictor implementation. It keeps the AlphaFold 3 architecture (README) and in this preprint carries released AlphaFold 3 weights, so it is an implementation, not a new trained model. Linked `uses_model` to the existing `discovery-model-alphafold-3`. |
| TorchScore | `evaluator` | `evaluator-torchscore` | A score-only loading of TorchFold used as the assessment in the pass-rate protocols (Appendix A.4.2). The `evaluator` kind can be an evaluation's assessment; it cannot carry a configuration, so the weight dependency is on its `scope_note` and in a claim. |
| TorchCraft | `pipeline` | `pipeline-torchcraft` | The design procedure, the thing the configurations configure. Linked `uses_model` to AlphaFold 3 and to TorchFold, which the relation contract defines as a dependency that does not assign results to the base model. |

No `model` record was created for TorchCraft. Appendix A.1.1 states that the predictor is frozen and
"Only the editable sequence variables are updated", and the final sequence comes from discrete
decoding, so the method trains no weights. That is recorded as `claim-no-trained-weights`.

Reused rather than duplicated, after grepping `data/entities`:

- `discovery-model-alphafold-3` for the predictor weights.
- `catalog-model-proteinmpnn` for the ProteinMPNN polishing steps. The store also holds
  `discovery-model-proteinmpnn`, which `catalog-model-proteinmpnn` is a `variant_of`; the catalogue
  record carries the version (`v_48_020`) and the profile, so it is the one linked.
- `hyinv-20261106-model-ligandmpnn` for the LigandMPNN redesign variant.
- `catalog-model-esm-2` for the ESM2-150M perplexity classifier. The store has no per-size ESM-2
  checkpoint record, and the preprint names "ESM2-150M" without a checkpoint revision, so the family
  record is linked and the size is on the configuration.

Three identities were created because the store holds none and the configurations need them: `model-iglm`
(cited as reference 22), `model-abmpnn` and `model-flowpacker` (both named in Appendix A.4.3 with no
citation). Each carries a `provenance_note` saying so and missing reasons for version, licence and
training data.

Comparator methods (BoltzGen, RFdiffusion, RFantibody, Germinal, RFpeptides, BoltzDesign) got **no**
identities. Every comparison that involves them is printed as a figure without numbers, so there is
no value to attach. They are named instead in each protocol's
`configurations_in_same_table_not_intaken` and in the figure-only claims. If a later batch extracts a
comparison that carries numbers, the identities can be created then.

## The evaluated configuration

Four independent statements in the preprint fix one weight setting for every reported experiment:

- Abstract: "Using pretrained AlphaFold3 weights, TorchCraft generated representative minibinders and
  VHHs ..."
- Section 1, final paragraph: "All designs reported here, including experimentally validated binders
  and computational benchmarks, were generated using pretrained AF3 weights."
- Appendix A.1.1: "All designs reported in this study used pretrained AF3 weights."
- Figure 1 caption: "Experimental campaigns and computational benchmarks reported here used the same
  AF3-weight setting."

So `config-torchfold-af3-parameters` is the configuration every result sits on, and the design
configurations link `uses_model` to it.

The README's other option is a different configuration, `config-torchfold-abag-checkpoint`
(status `discovered`, no result): the README requires exactly one of `CHECKPOINT_PATH` (the gated
TorchFold weights) or `MODEL_DIR` (official AlphaFold 3 parameters), with the checkpoint taking
priority if both are set. The preprint's Discussion names the specialised checkpoint as a direction
still to be tested: "Its specialized checkpoint may offer more informative guidance during CDR
optimization. Matched comparisons ... will be needed to test this potential." It therefore inherits no
performance claim. The README's FoldBench-AB figure of 70.1% is recorded as
`claim-torchfold-readme-benchmark`, a developer-reported claim on that configuration, not as a result.

## What was extracted as results (31)

| Values | Where printed | Records |
| --- | --- | --- |
| 4 minibinder apparent KD (60.2, 8.55, 2.04, 23.3 nM) | Figure 2a caption, repeated in Section 2.2 and in the panel labels | 4 evaluations, 4 results |
| 4 VHH apparent KD (24.3, 122, 268, 354 nM) | Figure 3a caption, repeated in Section 2.3 and in the panel labels | 4 evaluations, 4 results |
| 20 runtime cells | Supplementary Table S9, all four rows by five sequence lengths | 20 evaluations, 20 results |
| 3 expression-classifier statistics (MCC 0.598, Pearson -0.538, Spearman -0.602) | Supplementary Figure S4b caption | 3 evaluations, 3 results |

Why the runtime table is in, although the issue does not name it: it is the only complete printed
numeric table in the preprint, every cell is unambiguous, and the official project site reprints it so
the parse has a second source to check against. It is extracted in full, cell for cell, with the
hardware and operator setting as separate configurations and one protocol per sequence length, because
the sequence length is an input and not an aggregation.

The 500-residue NPU cell without fused attention carries a footnote marker in the source
(`33.47*`, footnote "Batch size 1; batch size 2 exceeded memory (OOM)."). `printed_value` holds
`33.47` without the marker; the exception is on the result's `scope_note` and `source_anomaly`, on the
evaluation's `limitations` and in `claim-runtime-oom-exception`. It is the one cell of the table that
is not a batch-size-2 run.

The expression-classifier statistics are in because the VHH benchmark criterion depends on the
threshold they justify. They are marked retrospective and in-sample: the threshold was chosen on the
same collection the statistics describe.

## What was not extracted, and why

Figures 2f, 3i, 4c, 5c, 5d, S1, S2, S3, S5, S6, S7 and S9 print no numbers. That covers every
computational pass rate, every Rosetta interface-score distribution, the cyclisation fractions, the
docking scores and the Boltz-2 affinity predictions. Nothing was read off a bar, a colour or a pixel,
and the preprint publishes no source data behind the figures, so none of it qualifies for a computed
value either. Each benchmark is registered with its panel, its design counts, its criterion and its
comparators, at status `discovered`, and carries a figure-only claim saying what the figure shows and
that no value was taken.

The four computational benchmarks are kept apart, as the issue asked, because their panels differ:
12 minibinder targets at four binder lengths, 15 VHH targets over five frameworks, eight cyclic-peptide
target systems in two cyclisation modes, and ten ligands. They are also kept apart from the
laboratory-measured records: the BLI protocols sit under their own tasks, not under any benchmark. The
cyclic-peptide and ligand-pocket work is computational only, which the Discussion states and which is
recorded on each benchmark, each configuration and in `claim-experimental-scope`.

The optional redesign settings are separate configurations with no results
(`config-minibinder-mpnn-polished`, `config-vhh-abmpnn-polished`, the two cyclic MPNN settings and
`config-ligand-pocket-ligandmpnn`), so a polished pass rate can never be read as the raw method's.

Two further things that are stated but unmeasured here: the amino-acid composition regulariser's
effect on ESMFold confidence and on expression (Figure 2e, Supplementary Figure S1) is figure-only and
is recorded in `claim-composition-regulariser`; the structural novelty and diversity analyses
(Figures 2c, 2d, 3g, 3h) print no numbers either.

## The tested denominators

The issue asked for the exact tested denominators from the methods. The answer from the source is that
they are not stated. What is stated:

- Minibinders: 3,000 candidates generated per target (Section 2.2, Appendix A.2.1 and A.2.2.1),
  filtered by radius of gyration below 17, binder pTM above 0.7 and TorchCraft ipTM above 0.7, then
  ranked by Rosetta Interface Analyzer on the composite score `100 x ipTM(TorchCraft) - score(Rosetta
  interface)`. "Candidates were selected for experimental validation using the composite score."
- VHHs: 12,500 candidates generated per target (Appendix A.2.2.2), filtered by CDR interface rate
  above 0.6, CDR3 hotspot coverage rate above 0 and TorchCraft ipTM above 0.7, ranked by the same
  composite score, and "the top-ranked designs were selected for experimental validation".
- Appendix A.5.1.5 and A.5.2.6 describe an initial BLI screen that prioritised designs, then
  multi-concentration measurement of "selected" designs. Neither says how many were ordered,
  expressed, screened or measured.

So no campaign hit rate exists in this source, and none was invented. Each KD result is a single
displayed representative design: `coverage.scored` is 1, `denominator` is absent with a
`missing_metadata` reason of `unreported`, the metric qualifier says "not a campaign hit rate", and the
protocols carry a `selection_bias` paragraph saying the measured designs are survivors of a confidence
filter and a Rosetta ranking. Supplementary Tables S7 and S8 list the assay proteins, not design counts.

## TorchScore and what the pass rates mean

Appendix A.4.2: "TorchScore is a score-only loading of the TorchFold implementation ... No separate
scoring network is trained. In this study, TorchScore used pretrained AF3 weights, the same checkpoint
used for design. Designed sequences that were rebuilt with FlowPacker were scored from the resulting
coordinates; they were not refolded from sequence by TorchScore."

That is recorded as `claim-torchscore-shared-weights` and repeated as a limitation on every protocol
that uses TorchScore, on each of the four computational benchmarks and in the evaluator's `scope_note`.
The Discussion's own statement that predictor-derived pass rates "should not be interpreted as
experimental success rates" is `claim-pass-rates-not-success-rates`.

## Licensing: three layers, and a conflict

| Layer | What the source says | Where |
| --- | --- | --- |
| Code | Apache License 2.0 | Repository `LICENSE` (unmodified Apache-2.0 text) and README 'License' at commit `ebf9dc6`; the GitHub repository API also reports `spdx_id: Apache-2.0` |
| Gated checkpoint and training data | Manual access review, and "Redistribution, rehosting, selling, or sharing these files without written permission from Changping Laboratory is not allowed", while the page's licence tag reads `mit` | Hugging Face dataset page |
| Upstream predictor parameters | Official AlphaFold 3 parameters, "apply from DeepMind"; not distributed with the repository | README 'Checkpoints' |

The official project site states something different again: its closing line says the GPU and NPU
implementations, the TorchFold training code and the TorchFold-AbAg model weights "are open under the
MIT license". The repository's own licence file governs the code, so Apache-2.0 is what the batch
records (`claim-code-licence`). The MIT statement is recorded as `claim-project-site-licence-statement`
at status `disputed`, and the project-site source carries an `evidence_concerns` entry scoped
(`applies_to`) to that claim, so it cannot support a comparison. This is the conflict the issue warned
about, but it is not a third-party directory: it is the project's own site, which makes it a question
for the reviewer rather than something to discard.

Two more licence findings:

- The README says the Hugging Face dataset holds "TorchFold trained weights (`.pt`) and public
  TorchFold training data". The page, retrieved without signing in, describes "TorchFold-AbAg training
  data" as `data.tar.gz` of processed training examples, 1.13 GB in total, and does not itself list
  trained weights; the file list is not visible without approved access. Recorded as
  `claim-released-artifact-mismatch`, with the gap left open.
- DeepMind's terms for the AlphaFold 3 parameters were not retrieved, so nothing in this batch says
  whether the evaluated configuration can be used commercially (`claim-af3-parameter-terms`).

## Value checking

`npm run -s batch -- check-values data/omics/torchcraft-20261115
torchcraft-20261115-source-arxiv-v1=<text layer>` reports `{"locator_not_parsed": 11,
"row_not_found": 20}` and writes `value-check.tsv`. Both outcomes are expected and neither means a
value is missing:

- The 11 KD and Figure S4b values are printed in figure captions and prose, which the checker lists
  for manual checking by design.
- The 20 Table S9 values come back `row_not_found` because the checker's caption pattern requires a
  colon or full stop after the table label (`table s9[:.]`), and this preprint prints
  "Table S9 TorchCraft runtime benchmark across ..." with no delimiter. The table body is never found,
  so no row is searched. The locators are correct; the checker cannot reach them.

Two scripts in `extract/` stand in for it, and both are deterministic and assert what they expect:

- `parse_runtime_table.py` finds the Table S9 caption and the `Code Operator Machine` header in the
  text layer, asserts the five column headers and the four row labels, asserts five cells per row, and
  compares the result with the values the script was written against. It writes
  `extract/runtime-table.tsv`, which `build.py` reads, so no runtime number in `batch.jsonl` is typed
  by hand.
- `check_transcriptions.py` asserts, in the whitespace-normalised text layer, each of the 14 quoted
  fragments and 8 figure panel labels that the other 11 values and the main claims rest on; checks
  that every result's `printed_value` occurs in the fragment its locator names; checks that the four
  KD values of each campaign are in target order in the caption sentence; and cross-checks all 20
  runtime cells against the copy printed on the official project site. It reports
  `{"results_checked": 31, "fragments_checked": 22, "site_cross_check": true}`.

Run both from the repository root with the refetched PDF or its text layer as the first argument, and
the project site HTML as the second argument to `check_transcriptions.py`.

## Decisions a reviewer should rule on

1. **The licence conflict.** Three official sources disagree: repository Apache-2.0, project site MIT,
   Hugging Face `mit` tag with a no-redistribution gate. This batch records Apache-2.0 for the code and
   marks the site's MIT claim `disputed` with an evidence concern scoped to that claim. Confirm that is
   the right resolution, and whether the concern should also cover the site's other statements.
2. **Table S9.** Whether a hardware runtime table belongs in this batch at all, given the issue does
   not name it, and whether one protocol per sequence length is the right shape against one protocol
   with the length in the metric qualifier.
3. **The threshold's two printed values.** Appendix A.4.3.2 prints the VHH expression proxy threshold
   as 6.31, Supplementary Figure S4b as 6.309. Both are recorded on
   `config-esm2-150m-expression-classifier` and in `claim-expression-threshold`; the VHH pass-rate
   protocol quotes 6.31, as the methods do. Confirm which should be carried in the protocol.
4. **Three new model identities.** `model-iglm`, `model-abmpnn` and `model-flowpacker` are created from
   a single naming each in this preprint, two of them without a citation. Confirm they should exist
   rather than being left as text inside the configurations.
5. **No comparator identities.** BoltzGen, RFdiffusion, RFantibody, Germinal, RFpeptides and
   BoltzDesign are named in protocol text only, because no value of theirs is extractable. Confirm, or
   ask for discovered-status identities now.
6. **Status split.** Records tied to an extracted value are `source_checked`; the four computational
   benchmarks, their protocols and datasets, and the optional redesign configurations are `discovered`
   because no number exists for them. Confirm the split, including the mixed case where a `discovered`
   protocol uses a `discovered` dataset under a `discovered` benchmark.
7. **The KD records' framing.** Each is one displayed design with `coverage.scored` of 1 and an
   unreported denominator. Confirm that is preferable to recording no result at all for the measured
   campaigns.
8. **The missing TorchFold report.** Reference 21 has no URL or DOI and the project site's TorchFold
   paper link points at the site itself. Its benchmark figures are recorded only as a developer-reported
   claim with no benchmark or result records. Confirm, or ask for a separate source-resolution pass.
9. **Use cases.** This was run as a lane pass (`structure-design`, `interactions`), so no use-case
   relevance judgement was written. The store holds binder-design use-case material
   (`uc-binder-20261022-*`), and the BLI protocols and the four benchmarks may be relevant to it.
   Decide whether a use-case pass should follow.

## Shapes and store checks not run here

`records -- add` validates against the SHACL shapes, and the extractor does not add the batch, so the
shapes have not been run over these records. What was run, from the repository root, with no store
loaded and no file outside this folder touched:

- The record schema, link relation rules, dangling-link and evaluation-role checks
  (`validateRecords` over `batch.jsonl` plus the four external records it links to): pass.
- The attribute registry (`attributeIssues`): 0 problems.
- Description rules (`descriptionProblems`): 0 problems.
- Concept keys for every `concept:`-typed attribute and for the `areas`, `method_types` and `contexts`
  facets, against `data/vocab/`: 0 problems. No vocabulary concept was needed, so there is no
  `vocab-proposal.ttl`. Two protocols deliberately carry no `metric`: `data/vocab/metric.ttl` has no
  concept for an AutoDock Vina docking score or a Boltz-2 affinity prediction, and neither protocol
  carries a value, so a `missing_metadata` reason of `unextracted` records that rather than adding a
  concept nothing uses.
- Every protocol has an `evaluates_task` or `part_of` link, so `check:task-links` has nothing to add to
  its baseline list.
- No ID in the batch already exists in `data/entities` or `data/evidence`.
