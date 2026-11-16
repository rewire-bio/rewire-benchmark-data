# TorchCraft, independent review

2026-11-16. Batch `data/omics/torchcraft-20261115/`, issue
[#243](https://github.com/rewire-bio/rewire-benchmark-data/issues/243). Reviewed by a Claude
(Opus 5) agent that did not extract the batch, against the extraction frozen at `batch.jsonl`
SHA-256 `2cb2377abde1bb43b44a4ff84c55023d18cc91ab691ce95f135bb37e53647f22`, 165 records. Not human
scientific review. Nothing was reproduced: no design run, score, docking calculation or binding
measurement was repeated, and transcription is not reproduction.

Receipt: `data/omics/torchcraft-20261115/review.json`. Mismatch report:
`data/omics/torchcraft-20261115/value-check.tsv`. Reviewer scripts:
`data/omics/torchcraft-20261115/review/`.

Every stored number stands as extracted. No value, numeric value, source locator, metric, unit,
direction, coverage or uncertainty was changed. Twenty-two wording and link edits were made before
the batch was stored; they are listed under [Edits](#edits).

## Sources and hashes

All seven artifacts were re-retrieved at 2026-11-16T00:08Z.

| Record | SHA-256 | Refetched |
| --- | --- | --- |
| `source-arxiv-v1` | `f8145b5b95552dd30996eda2940507c0f32d09adfc60f44f28458e7872788f21` | matches |
| `source-arxiv-abs` | `cac39821a99125fe2f245a30d72d8f1465a3a99b784298ada10f68748b2236a0` | matches |
| `source-project-site` | `fa95060dad51bd3e04278b48c7e3bc62c66f8f909db3871e654f79d5a98dcd3c` | matches |
| `source-torchx-readme` | `88da821dfed6d76a6d1d2efd1e3e124a18f35c07d6fdf45a8e374fc2c35fccf0` | matches |
| `source-torchx-licence` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | matches |
| `source-torchcraft-gpu-readme` | `77a6b7b67f29a7931e58e5ee2bcbaa5efa08a5ff33debd6d658f85ae305ec313` | matches |
| `source-huggingface-torchfold` | `39268aab20e07bb615c1b96c8eb5684686dc953036a7d062dec7684581fbdfcf` | does not reproduce, by design |

The text layer every value was read from is exact. `pdftotext -layout` over the refetched PDF gives
SHA-256 `90f1da5f8a936766087beba0ade3f038f5b69504b9f581b42f2391f5640c5e6b`, the value recorded in
`hash_scope`. Nothing is archived in the batch, and that is right: the only licence the abstract page
links is the arXiv.org perpetual non-exclusive distribution licence 1.0, which grants arXiv a
distribution right and grants a reader none, so neither the PDF nor its text layer may be committed.
Each of the seven source records states its licence or access terms, and the three that would
otherwise invite a copy say so explicitly. The PDF and its text layer are reproducible from
`artifact_url` with the two commands in `notes.md`, and both hashes were confirmed here.

### The Hugging Face page claim is right in substance and understated in detail

The extractor reported that the page "differed only in per-request CSS class hashes
(`hf-sanitized-...`)". Checked rather than accepted, and it is narrower than what the page does.

Three consecutive reviewer fetches gave three different hashes
(`4781fee5a24deb5e...`, `c2cf63d1f6c732d8...`, `2ccfe27d4e5dcdc4...`), so the page cannot be hashed
stably at all. Normalising the three `hf-sanitized-*` class hashes leaves exactly one further
difference between fetches a second apart: `window.requestId`, a per-request trace token
(`Root=1-6afa4987-...` against `Root=1-6afa4991-...`). The page also prints a download counter
("Downloads last month 25"), which is a counter and will move. With the per-request values
normalised the markup is identical.

The substantive conclusion holds. The licence tag (`License: mit`), the gate heading ("Request access
to TorchFold-AbAg training data"), the gate text, "Access is provided after manual review", the card
("`data.tar.gz`: processed training examples (`.pkl.gz`; unpacks to `data/`)") and "Total file size:
1.13 GB" all match the recorded quotations word for word. The recorded hash is a per-retrieval stamp,
not a check on content. The source record's limitation now says that, naming every per-request
element rather than only the class hashes.

## How the values were compared

`npm run -s batch -- check-values` reproduced the extractor's figures exactly,
`{"locator_not_parsed": 11, "row_not_found": 20}`, and rewrote `value-check.tsv` byte-identically.
Both outcomes are benign and the extractor's diagnosis of the second one is correct, verified in the
tool's own source: `scripts/omics/batch.py` builds its caption pattern as
`re.escape(table) + r"\b[:.]"` and requires `[:.]\s*\S` after the label, and the preprint prints
"Table S9 TorchCraft runtime benchmark across sequence lengths…" with neither a colon nor a full
stop, so the caption is never recognised and the body is never searched. `npm run -s batch -- table`
confirms it directly: "Table S9: no table body found next to the caption". The locators are correct;
the checker cannot reach them.

All 31 results were therefore re-read with `review/recheck_values.py`, written for this review. It
imports and reads neither `extract/parse_runtime_table.py` nor `extract/check_transcriptions.py`, and
it checks column and target assignment rather than mere presence:

- **Table S9, 20 cells.** The header line is located by its own printed labels, and every numeric
  token in a body row is assigned to the length column whose header label *starts nearest to it in
  character offset*, with a one-to-one assignment asserted. A value copied from a neighbouring column
  fails this, where splitting on whitespace would not. All four row labels, all five column headers
  and all 20 cells were asserted. The same 20 cells were then read a second time out of the HTML
  table the official project site reprints, and agreed cell for cell.
- **The 8 measured KD values.** The caption sentence is asserted verbatim, the four values are taken
  in the order the caption prints them, and each result's value must sit at the ordinal position its
  target holds in the caption's own target list *and* at the same position among the figure's four
  `KD: …nM` panel labels.
- **The 3 Figure S4b statistics.** The fragments `MCC = 0.598`, `Pearson r = −0.538` and
  `Spearman ρ = −0.602` are asserted verbatim in the normalised text layer and matched to their own
  results.

Result: 31 checked, 0 failures.

### Negative controls

The checker was run against deliberately corrupted records to show it rejects what it claims to
catch. All four were rejected:

| Control | Rejected on |
| --- | --- |
| IFNAR2 and IL-7Rα KD values swapped | caption order, panel-label order and the numeric field, for both results |
| 200 aa cell given the 300 aa value (column shift) | `printed_value '4.54' but Table S9 [GPU w/ cuequivariance \| 200 aa] prints '4.27'` |
| NPU w/ FA 300 aa given the NPU w/o FA value (row swap) | `printed_value '8.63' but Table S9 [NPU w/ FA \| 300 aa] prints '6.23'` |
| MCC result given the Pearson value | `the source fragment is 'MCC = 0.598'` |

### Manual read

All 8 measured binding values and all 3 figure statistics were also read by hand in the refetched
text layer, in every place the preprint prints them.

Figure 2a caption: "Apparent dissociation constants of the displayed binders were 60.2, 8.55, 2.04,
and 23.3 nM, respectively", for "IFNAR2, IL-7Rα, PDGFRβ, and PD-L1"; panel labels "KD: 60.2nM
KD: 8.55nM KD: 2.04nM KD: 23.3nM" under "IFNAR2 IL7RA PDGFR PD-L1"; the same four numbers repeated in
Section 2.2. Figure 3a caption: "Apparent dissociation constants of the displayed binders were 24.3,
122, 268, and 354 nM, respectively", for "BHRF1, EFNA5, PDGFRβ, and S100A4"; panel labels "KD: 24.3nM
KD: 122nM KD: 268nM KD: 354nM" in the same order; repeated in Section 2.3. Figure S4 caption, panel b:
"The selected threshold of 6.309 maximizes the Matthews correlation coefficient (MCC = 0.598; Pearson
r = −0.538; Spearman ρ = −0.602)". The page numbers on the locators are right: the text layer's page
footers put Figure 2 on page 4, Figure 3 on page 5, Table S9 on page 29 and Figure S4 on page 32.

One transcription convention stands. The 500-residue NPU cell without fused attention is printed
`33.47∗`, with a footnote marker, and `printed_value` holds `33.47`. That is correct: the marker is a
reference mark pointing at "∗ Batch size 1; batch size 2 exceeded memory (OOM).", not part of the
value, and the exception it points to is recorded on the result, the configuration, the protocol and
in `claim-runtime-oom-exception`. The checker reports the stripped marker rather than passing over it.

## Rulings

### 1. The eight measured values cannot be read as a campaign success rate. Confirmed

This is the reading most likely to mislead, so it was checked on the result fields, the evaluations,
the protocols, the tasks, the claims and the descriptions, not only on the numbers.

What the source states, and all it states. Section 2.2: "Candidates were selected from 3,000
generated designs per target using the filters and ranking procedure in Appendix A.2.2.1.
Multi-concentration BLI measurements identified binders in all four campaigns, with representative
apparent dissociation constants of 60.2, 8.55, 2.04, and 23.3 nM, respectively". Appendix A.2.2.1:
"For each minibinder target, 3,000 TorchCraft candidates were sampled. After generation, candidates
were filtered by radius of gyration (ROG < 17), binder pTM (> 0.7), and TorchCraft ipTM (> 0.7).
Passing candidates were then ranked using Rosetta Interface Analyzer. Candidates were selected for
experimental validation using the composite score… Higher composite scores were prioritized for
wet-lab validation." Appendix A.2.2.2 is the same shape for VHHs: "For each VHH target, 12,500
TorchCraft candidates were generated… the top-ranked designs were selected for experimental
validation."

The tested denominator is genuinely absent. Appendix A.5.1.5 and A.5.2.6 describe an initial BLI
screen whose "Baseline-subtracted signals (in nanometers) were calculated to prioritize binders for
further characterization", then multi-concentration measurement "of selected binder designs". Neither
says how many designs were ordered, expressed, screened or measured. Supplementary Tables S7 and S8
list the assay proteins, not design counts. The strings "hit rate" and "success rate" appear nowhere
in the preprint except the Discussion's warning against the latter.

So no campaign hit rate exists in this source, and the batch invents none. Each of the eight results
carries `coverage.scored` 1 with unit "displayed designs", `denominator` absent with a
`missing_metadata` reason of `unreported`, a `claim_scope` of "One displayed design against one
target. It is not a success rate and not a solution-phase equilibrium constant", and a
`metric_qualifier` ending "not a campaign hit rate". Each evaluation's `comparison.population` reads
"One displayed representative design against <target>; the number of designs expressed and tested is
not stated", its `interpretation` says "One selected design bound its target; this is not a campaign
hit rate", and its limitations repeat it. Both protocols carry a `selection_bias` paragraph ("The
measured designs are the survivors of a confidence filter and a Rosetta ranking over a large
generated pool, and only representative designs are displayed… it is not a success rate for the
campaign") and the limitation "The tested denominator is unreported, so no hit rate can be derived".
`claim-minibinder-candidate-pool` and `claim-vhh-candidate-pool` fix the generated pool and state
that the tested number is not given. The two design tasks describe an input and a desired output and
assert nothing about rates.

Nothing in the batch repeats the source's "identified binders in all four campaigns" as a
denominator, which is the one phrase a reader could turn into 4/4. Recording the measurements is
preferable to recording nothing: they are the only experimental evidence in the preprint, and every
record that carries them says what they are and what they are not.

One wording gap was found and fixed. The `dissociation-constant` concept's own definition requires
that "the assay, the valency of the tested construct and whether the value is apparent rather than a
fitted monovalent constant go in metric_qualifier", and its scope note says values "measured on
different assays (yeast display, BLI, SPR, HTRF) or in different construct formats are not
comparable". The extractor's qualifier named the apparent nature and the selection but not the assay,
and used one identical string for the minibinder and the VHH campaigns, which are different construct
formats. The two qualifiers now differ and each names biolayer interferometry, the immobilised binder
and the 1:1 fit. Without that, two apparent-KD results from different assays would have compared as
like for like.

### 2. The licence conflict: the scoping is right, and the gated terms need no separate concern

Three official sources, three different statements, all verified at review time.

The repository's own `LICENSE` at commit `ebf9dc6676ecb1be505bc72f87de408995f0d8fd` is the unmodified
Apache-2.0 text ("Apache License / Version 2.0, January 2004"), and the README's License section says
the same. That governs the code, so `claim-code-licence` recording Apache-2.0 is right.

The project site's closing line reads, verbatim: "GPU and Ascend NPU implementations, TorchFold
training code, and the TorchFold-AbAg model weights are open under the MIT license." That is a
specific, checkable statement that the repository's own licence file contradicts. Recording it as
`claim-project-site-licence-statement` at status `disputed`, with an `evidence_concerns` entry on the
project-site source scoped by `applies_to` to that one claim, is the correct resolution. The claim is
kept rather than discarded, because it is the project's own site and a reader who finds the MIT
statement needs to see that we looked at it; and the concern withholds only the claim that asserts
the licence we do not accept, not the source as a citation.

**The concern should not be widened to the site's other statements.** The site is used for four
things: the TorchFold and TorchCraft summaries, the reprinted runtime table, and the licence line. Of
these, only one is independently checkable, and it checks out: the 20 runtime cells were extracted
from the site's HTML table by this review and agree with the PDF cell for cell, including the `33.47∗`
footnote marker. A page that reprints the primary source's only numeric table correctly, and
misstates one licence, has one specific error, not general unreliability. Widening the concern would
withhold the agreeing runtime cross-check, which is the opposite of what the evidence supports. A
blanket concern is reserved for a source that is unreliable as a whole, and this one is not.

**The gated checkpoint terms already have their own claim, and should not also get a concern.** The
Hugging Face page is internally inconsistent: its tag reads `License: mit` while its gate reads "By
requesting access, you agree to use the TorchFold-AbAg training data only for the purpose described
below. Redistribution, rehosting, selling, or sharing these files without written permission from
Changping Laboratory is not allowed." `claim-checkpoint-access-terms` records the gate as the
operative condition and states that the tag "does not match that condition", and the source record's
`licence` attribute carries both halves. That is the right shape, and it is why no concern is needed:
the claim does not rest on the `mit` tag, so there is nothing for a concern to withhold. Scoping a
concern to that claim would withhold the record that documents the conflict, which is self-defeating.
The asymmetry with the project site is principled: a claim that asserts a licence we reject is
`disputed` and withheld; a claim that records a conflict and resolves it is neither. The page supports
no result, so no comparison is at risk either way.

Three layers, three answers, and the batch keeps them apart: Apache-2.0 for the code, a
no-redistribution gate for the checkpoint and training data, and unretrieved DeepMind terms for the
upstream AlphaFold 3 parameters (`claim-af3-parameter-terms`, an open gap).

### 3. Every reported experiment used the general pretrained predictor weights. Confirmed, four for four

All four cited statements say what the extractor says they say, verbatim in the refetched text layer:

- Abstract: "Using pretrained AlphaFold3 weights, TorchCraft generated representative minibinders and
  VHHs with experimentally measured binding across four targets in each format, without post hoc
  sequence redesign."
- Section 1, final paragraph: "All designs reported here, including experimentally validated binders
  and computational benchmarks, were generated using pretrained AF3 weights."
- Appendix A.1.1: "All designs reported in this study used pretrained AF3 weights."
- Figure 1 caption: "Experimental campaigns and computational benchmarks reported here used the same
  AF3-weight setting."

Appendix A.2.1 adds it per campaign: minibinders and VHHs were each designed "using pretrained AF3
weights through TorchFold". So `config-torchfold-af3-parameters` is correctly the configuration every
result sits on, and every design configuration links `uses_model` to it.

The antibody-specialised checkpoint carries no result and inherits no performance claim, and the
record structure enforces that rather than merely asserting it.
`config-torchfold-abag-checkpoint` has status `discovered`, no evaluation links to it, nothing in the
batch links to it as a `system`, and its only inbound link is its own `configuration_of` to
`method-torchfold`. Its `configuration_type` is `reported_configuration`, whose definition is "a
configuration… as reported in a source", which is exactly right: the README offers it
(`CHECKPOINT_PATH` or `MODEL_DIR`, "exactly one", checkpoint takes priority if both are set, verified
in both READMEs at the pinned commit), and the preprint does not evaluate it. The Discussion names it
as untested: "TorchFold's reported improvements in antibody–antigen structure prediction provide a
promising direction for antibody design. Its specialized checkpoint may offer more informative
guidance during CDR optimization. Matched comparisons of experimental binding and expression under
the same targets, frameworks, and candidate-selection procedures will be needed to test this
potential." That is the only mention of it in the whole preprint.

The README's percentage figure is a developer-reported claim, not a result, and correctly so. The
README states: "We compare TorchFold with AlphaFold3, Protenix-v2 and OpenDDE; MSAs for every method,
including OpenDDE, were generated with the official AF3 Jackhmmer search. On FoldBench-AB, TorchFold
reaches 70.1% ranked success." The batch records this as `claim-torchfold-readme-benchmark`, field
`developer_reported_benchmark`, with no FoldBench-AB benchmark record, no protocol, no evaluation and
no result. That is the right treatment: the figure belongs to reference 21, the separate TorchFold
report, which carries no URL or DOI and whose link on the project site points at the site itself, so
there is no primary source for it. One qualification for a later reader: the README does not say in
so many words that the 70.1% was obtained with the gated checkpoint. The attribution to that
configuration rests on the README's own framing a few lines earlier, "TorchFold keeps the AlphaFold 3
architecture and improves antibody–antigen prediction with an interface-specific loss, a high-noise
diffusion schedule, and two-round distillation that expands unique Ab–Ag examples from 5.0k to 24.5k",
which is the antibody-distilled model the gated release holds. Reasonable, and worth a
source-resolution pass if the TorchFold report ever becomes retrievable.

### 4. The three new comparator identities should exist, and the reused identities needed two changes

`model-iglm`, `model-abmpnn` and `model-flowpacker`: confirmed independently that the store holds none
of them under any ID. A case-insensitive search over every record in `data/entities` and
`data/evidence` on `id`, `name`, `reported_name` and `description`, and a recursive grep over all of
`data/`, found no record for any of the three; the only hits anywhere are the query strings in two
search ledgers and this batch's own files. Creating them is right, because three configurations
depend on them and `uses_model` needs a target; each is `entity_level` `family` with version, licence
and training data absent and a `provenance_note` saying it was created from a single naming in this
preprint, two of them without a citation. That is the honest shape for an identity known only by name.

The reused identities were checked one at a time, and two were wrong.

- `discovery-model-alphafold-3`, family level, no version. Right: the preprint says "pretrained
  AlphaFold3 weights" and names no parameter release.
- `hyinv-20261106-model-ligandmpnn`, family level, the store's only LigandMPNN record. Right as an
  identity. Noted for a later reader, not changed here: its `version` string reads "As run in the
  HyInv report, on backbone coordinates only", which is another batch's framing carried on a shared
  identity. It is outside this batch and not this review's to edit.
- **ProteinMPNN: changed.** The extractor linked `catalog-model-proteinmpnn`, which is `variant_of`
  `discovery-model-proteinmpnn` and pins version `v_48_020`. The preprint names ProteinMPNN seven
  times and never gives a version, checkpoint or weight set; its only other mention is the Science
  2022 citation. Linking the versioned record assigns a checkpoint the source does not state, against
  the rule that an unidentified version stays at family level. Store precedent agrees: all three
  existing `uses_model` links to ProteinMPNN in `data/entities/configurations.jsonl` point at
  `discovery-model-proteinmpnn`. Retargeted on the three configurations that use it.
- **ESM-2: changed.** The extractor linked `catalog-model-esm-2`, which is `alias_of`
  `discovery-model-esm-2`. `shared/omics/relations.ts` defines `alias_of` as "Same identity under
  another ID; never merges results", so a dependency link to the alias is invisible to a query on the
  canonical record. All twenty existing `uses_model` links to ESM-2 in the store point at
  `discovery-model-esm-2`, which carries the same profile. Family level is right either way: the
  preprint names "ESM2-150M" with no checkpoint revision, and the size stays on the configuration with
  a `missing_metadata` note. Retargeted.

### 5. No comparator identities for BoltzGen, RFdiffusion, RFantibody, Germinal, RFpeptides or BoltzDesign. Confirmed

Every comparison involving them is printed as a figure with no numbers (Figures 2f, 3i, 4c, 5c, 5d and
Supplementary Figures S3, S5, S6, S7, S9), so there is no value to attach to an identity. They are
named in each protocol's text and in each benchmark's `scope_note` and figure-only claim, which is
where a reader looking for them will find them. Creating six `discovered` identities now would add
graph surface carrying nothing. If a later batch extracts a comparison with numbers, they can be
created then, with the value that justifies them.

### 6. TorchScore's shared weights are now a limitation on all four protocols that use it. One was missing

Appendix A.4.2, verified verbatim: "TorchScore is a score-only loading of the TorchFold
implementation. Given input coordinates, it bypasses the diffusion-based structure module and
evaluates the complex through the confidence pathway… No separate scoring network is trained. In this
study, TorchScore used pretrained AF3 weights, the same checkpoint used for design. Designed sequences
that were rebuilt with FlowPacker were scored from the resulting coordinates; they were not refolded
from sequence by TorchScore." The Figure 2f and Figure 3i captions repeat it: "TorchScore… scores
supplied coordinates using the same pretrained AF3 weights used for design and does not refold
sequences."

Both halves matter. The scorer carries the weights the designs were optimised against, and it never
re-predicts the structure from the final sequence, so a pass rate measures the designed or rebuilt
coordinates under the objective they were produced by.

Four protocols use TorchScore. `protocol-minibinder-torchscore-pass-rate`,
`protocol-vhh-torchscore-perplexity-pass-rate` and `protocol-cyclic-peptide-pass-rate` carried the
first half ("The evaluator uses the weights the TorchCraft designs were optimised against") and not
the second. `protocol-ligand-pocket-torchscore-pass-rate` carried neither. All four now carry one
limitation stating both. The evaluator's own `scope_note` already stated both, and
`claim-torchscore-shared-weights` and `claim-pass-rates-not-success-rates` are accurate; the gap was
on the protocols, which is where a reader comparing two protocols will look.

The Discussion's own warning is recorded as `claim-pass-rates-not-success-rates` and is verbatim:
"Predictor-derived pass rates are sensitive to the evaluator and should not be interpreted as
experimental success rates."

### 7. The computational benchmarks are separate protocols and cannot pool. Confirmed

Four benchmarks, four panels, four different criteria, verified in the appendix:

- Minibinder, 12 targets at 4 binder lengths (A.4.3.1): "A minibinder design was counted as passing
  the computational criterion when both TorchScore pTM and TorchScore ipTM exceeded 0.7."
- VHH, 15 targets over 5 frameworks (A.4.3.2): "A VHH design passed the computational criterion only
  when it satisfied both a structural-confidence criterion and an expression proxy: TorchScore ipTM
  had to exceed 0.7, and ESM2-150M perplexity had to be below 6.31."
- Cyclic peptide, 8 target systems in 2 cyclisation modes (A.4.3.3): "A cyclic-peptide design passed
  the computational criterion only if the predicted structure formed the intended cycle without chain
  breaks and satisfied TorchScore pLDDT > 70 and ipTM > 0.5."
- Ligand pocket, 10 ligands (A.4.3.4): "a design passed the computational criterion when TorchScore
  pLDDT exceeded 70 and TorchScore ipTM exceeded 0.7."

The four share the `success-rate` concept, which is why the qualifier is what keeps them apart, and
each `metric_qualifier` spells out its own criterion and thresholds. Comparisons require the same
metric *and* qualifier, so none of the four can pool with another. Each protocol is `part_of` its own
benchmark and `uses_data` its own dataset. The question is moot in practice, since all four are at
status `discovered` with no result at all, but the shape will hold when numbers arrive.

They cannot pool with the measured results either, by metric: `dissociation-constant` in nanomolar,
lower-better, against `success-rate`, unitless, higher-better. The BLI protocols are deliberately not
`part_of` any benchmark; they sit under their own tasks, so no laboratory measurement can be read
through a benchmark's panel. The two ligand-pocket figure protocols (AutoDock Vina score, Boltz-2
affinity) carry no metric concept at all, so they cannot compare with anything.

### 8. Table S9 belongs in the batch, and one protocol per sequence length is right

The issue does not name it, and it is in anyway. That was the right call: it is the only complete
printed numeric table in the preprint, every cell is unambiguous, and the official project site
reprints it, so the parse has a second independent source, which this review used. Extracting all 20
cells rather than a selection is what the collection procedure asks for.

One protocol per sequence length is the right shape, not one protocol with the length in the
qualifier. The sequence length is an input to the timed run, not an aggregation over runs, and a
protocol fixes the inputs. The alternative would let a 100-residue timing compare with a 500-residue
one as the same measurement.

The caption's derivation is the source's own, not ours: "Runtime is reported in minutes per design,
obtained by dividing the total wall-clock time of a batch-size-2 run by 2. GPU timings are the mean of
three independent runs." So `printed_value` is the printed cell and no `derivation` is needed, which
is correct. The GPU evaluations carry `comparison.aggregation` "Mean of three independent runs" and
the NPU evaluations carry `null`, since the preprint states no NPU replicate count; the null blocks
automatic comparison across the two platforms, which is right, and the protocols also carry the
limitation that the two platforms are different machines and not a controlled comparison. Within a
platform the two kernel settings share their aggregation and do compare, which is the one controlled
comparison the table supports.

One contradiction was fixed. The 500-residue NPU cell without fused attention had the
`metric_qualifier` "wall-clock minutes per design at 500 residues, batch size 2 run divided by 2,
measured at batch size 1 for this cell", which asserts both derivations at once; and
`protocol-runtime-500aa` said flatly "batch size 2", which is untrue for one of its four cells. The
result's qualifier now says it was measured at batch size 1 because batch size 2 exceeded memory and
is not the batch-size-2 run divided by 2 that the other cells report, and the protocol names the
exception in its qualifier and in a limitation. The effect is that this cell no longer compares with
the other three at 500 residues, which is what the footnote requires.

### 9. The threshold's two printed values: 6.31 is right in the protocol

Appendix A.4.3.2 prints "ESM2-150M perplexity had to be below 6.31"; the Supplementary Figure S4b
caption prints "The selected threshold of 6.309 maximizes the Matthews correlation coefficient".
Both are recorded on `config-esm2-150m-expression-classifier` and in `claim-expression-threshold`, and
the VHH pass-rate protocol's criterion quotes 6.31. Confirmed as correct: the protocol records the
criterion as the methods state it, and the methods state 6.31. The figure's 6.309 is the fitted
threshold at one more digit, not a different threshold, and the claim carries both so neither is lost.

### 10. The status split is right, including the mixed case

Records tied to an extracted value are `source_checked`; the four computational benchmarks, their
protocols and datasets, and the optional redesign configurations are `discovered`. Confirmed. The
split tracks whether a number exists, which is what the status means, not whether the source was read.

The mixed case the extractor flagged, a `discovered` protocol using a `discovered` dataset under a
`discovered` benchmark, is coherent rather than awkward: the whole chain is registered from the
source and none of it carries a result. The three expression statistics are the reverse case and are
handled correctly: the protocols are `source_checked` because values exist, and the in-sample problem
is recorded where it belongs, as `selection_bias` ("Retrospective and threshold-fitted on the same
collection, so the reported figures are in-sample"), as a limitation on each protocol, and in each
result's qualifier. The threshold was chosen on the same collection the statistics describe, and
every record that carries them says so.

### 11. Vocabulary: nothing to add

No `vocab-proposal.ttl` was written and none is needed. `data/vocab` is untouched by this batch.

Two protocols deliberately carry no `metric`: `protocol-ligand-pocket-vina-score` and
`protocol-ligand-pocket-boltz2-affinity`. `data/vocab/metric.ttl` has no concept for a raw AutoDock
Vina docking score or a Boltz-2 affinity prediction; its nearest entries, the CASF and CAPRI docking
concepts, are challenge-specific success rates and would be a wrong fit rather than a near one.
Neither protocol carries a value, because Figures 5c and 5d print no numbers. Confirmed that recording
a `missing_metadata` reason of `unextracted` with a note is the right outcome and that no concept
should be added: a metric concept with no printed value behind it cannot be checked against a source,
and adding one that nothing uses is the kind of respelling the procedure warns against. When a later
batch extracts a Vina or Boltz-2 figure with numbers, the concept gets added with a value to anchor it.

Every other controlled field was re-checked against `data/vocab/`: `dissociation-constant`, `runtime`,
`success-rate`, `matthews-correlation-coefficient`, `pearson-correlation`, `spearman-correlation`,
their units (`nanomolar`, `minute`, `unitless`) and the `reported_configuration` configuration type
all exist and fit. The two correlation results keep `metric_direction` `unknown` against the scheme's
`higher` default, which is right here: the expected relation between perplexity and expression is
negative, so neither direction is uniformly better, and each qualifier says so.

## Edits

Twenty-two edits, all before the receipt was written and the batch stored, applied by
`review/apply_review.py` so they are reproducible. No stored value changed, so no superseding result
and no `metadata-correction-*` claim was needed: section 5 of the collection procedure puts every
reviewer ruling into `batch.jsonl` before the batch is added, and nothing here was in the store.

| Ruling | Records | Change |
| --- | --- | --- |
| 6 | 4 protocols | the TorchScore shared-weights and no-refold limitation, stated in full on all four pass-rate protocols; it was absent from `protocol-ligand-pocket-torchscore-pass-rate` and half-stated on the other three |
| 4 | 3 configurations | `uses_model` retargeted from `catalog-model-proteinmpnn` to `discovery-model-proteinmpnn` |
| 4 | 1 configuration | `uses_model` retargeted from `catalog-model-esm-2` to `discovery-model-esm-2` |
| 1 | 8 results, 2 protocols | `metric_qualifier` now names the assay and the construct format, as the `dissociation-constant` concept's definition requires, and the minibinder and VHH strings now differ |
| 8 | 1 result, 1 protocol | the batch-size-1 Table S9 cell: the result's qualifier no longer claims both batch sizes, and the 500 aa protocol names the exception in its qualifier and a limitation |
| Sources | 1 source | the Hugging Face page's limitation names every per-request element, not only the CSS class hashes |
| — | 158 records | the extractor's `review` object replaced by this review's, with its own method concepts, notes, artifact hash and retrieval URL |
| — | 6 tasks, 1 evaluator | the `review` object removed. `shared/omics/attribute-registry.ts` declares no `review` field for the `task` or `evaluator` kinds, and `records -- add` rejects an undeclared attribute; the frozen extraction left it off these seven records for the same reason. Their text was reviewed all the same, and that is recorded here and in the receipt |

`batch.jsonl` after the edits: SHA-256
`db918f70fe71f27466780303c30472fa05bef3188d3e34f3b04987ca2613b58c`. The reviewer's value check, the
extractor's two scripts and `npm run -s batch -- check-values` were all re-run afterwards and all
agree; no printed value, numeric value, locator, metric, unit, direction, coverage or uncertainty
differs from the frozen extraction.

## Discrepancies

None involve this batch. Its results are new and not yet in the store, so they cannot appear in any
`outlier_results` or `consensus_results` list, and this worktree holds no `discrepancies.json` to
check. No `discrepancy_review` revision was written.

## Remaining gaps

- The gated Hugging Face release was not accessed by this review either, so the file list behind the
  gate is unseen and `claim-released-artifact-mismatch` stays open: the README says trained weights
  (`.pt`) are released there, and the page, read without signing in, describes only training data.
- Reference 21, the TorchFold report, is unretrievable. The README's 70.1% FoldBench-AB figure stays a
  developer-reported claim with no benchmark and no result. A separate source-resolution pass is
  warranted if the report appears.
- DeepMind's terms for the AlphaFold 3 parameters were not retrieved, so nothing here says whether the
  evaluated configuration can be used commercially.
- Every computational pass rate, Rosetta interface-score distribution, cyclisation fraction, docking
  score and Boltz-2 prediction is figure-only. The preprint publishes no source data behind its
  figures, so none of it qualifies for a computed value either.
- No use-case relevance judgement was written: this was a lane pass (`structure-design`,
  `interactions`). The BLI protocols and the four computational benchmarks may bear on the
  `uc-binder-20261022` material, and a use-case pass is left for a separate decision.
- `hyinv-20261106-model-ligandmpnn` carries another batch's framing in its `version` string. Outside
  this batch; noted for whoever next touches that record.
