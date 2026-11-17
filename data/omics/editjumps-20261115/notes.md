# EditJumps, issue #244

EditJumps is an open implementation of the Edit Flows and EvoFlows sequence-editing framework,
released on 16 September 2026 as an arXiv preprint with an MIT-licensed repository and a model
checkpoint on Hugging Face. It takes one seed amino-acid sequence and an approximate edit budget
and returns related candidate sequences carrying substitutions, insertions and deletions. This
batch registers the method, the arm the paper scores, the released checkpoint, its comparators,
the corpora and reference sets, the protocols, and every printed value of Tables 2, 1 (lower
block) and 4 plus the three reference-size values Appendix E prints in prose. Lanes:
`protein-fitness`, `structure-design`. Search cutoff 2026-11-15.

Extraction only, by a Claude extraction agent. A different agent reviews it. Nothing is marked
reproduced, no review sign-off is claimed, and every record carries status `needs_review` for the
reviewer to rule on. Every evaluation is developer-reported (`author_reported`,
`retrospective: true`).

Frozen extraction hash (`shasum -a 256 data/omics/editjumps-20261115/batch.jsonl`):
`8c6cf9464cc3a31ada50a8b11b30440e049369c377dbf24251518b836b8556e1`

## What the evaluation measures, and what it does not

Everything reported in every source is computational distribution comparison: how similar a set of
generated sequences is to a reference set of natural sequences. The metrics are edit counts,
Levenshtein distances, k-mer spectrum MMD, composition KL and Jensen-Shannon divergences,
covariance and mutual-information-product agreement, an entropy delta, and profile and ESM-2
log-likelihoods. **No binding affinity, specificity, expression, stability or retained function is
measured anywhere in any of the nine pinned sources.** The paper states this itself: "we note that
our evaluation is strictly in silico".

That is recorded in four places, so it cannot be lost: the task record's `scope_note`, every
protocol's `scope_note`, the first entry of every result's and evaluation's `limitations`, and the
claim `editjumps-20261115-claim-evaluation-is-in-silico`. The paper's own region-resolved finding,
that fidelity is driven by conserved framework scaffolds and that under 25% of the CDR gap is
closed, is a limitation on every reimplemented-block result as well as a claim; the candidate
variants are nowhere described here as improved antibodies.

## Sources

| ID suffix | Artifact | SHA-256 |
| --- | --- | --- |
| `source-arxiv-pdf-v1` | arXiv:2609.18745v1 PDF. Primary source for every value | `4211d8ef46c55efe8d89ba4ee6c0b4e57cca1e78d0856e9cdfbde37046a7f4e1` |
| `source-arxiv-html-v1` | arXiv HTML rendering of v1, used only to confirm column assignment | `ae0b05f6a7488dabd73990f02b6a6280a6673e0a6a0f2917713f913a5ec3ec4f` |
| `source-code-readme` | `README.md` at commit `d827d47c` | `fbf05022b8140519c13bf60db99276df3edcbaeac57f091f54a0dc3921716c05` |
| `source-code-licence` | `LICENSE` at commit `d827d47c` | `9f1abe28a25b5f6f95c58a81a647de3fa72ff6388d228c59bddd079255709989` |
| `source-code-performance` | `docs/performance.md` at commit `d827d47c` | `01e59ef27b2e93b118b15239e57c6500045c99facd72f0b956e78ecf161217e3` |
| `source-code-limitations` | `docs/limitations.md` at commit `d827d47c` | `e11bb92210012e08e6a0bc0e6298d098818419f3d661bdae6082c71de9c0b6d8` |
| `source-code-claims` | `docs/claims.md` at commit `d827d47c` | `7c7103723b23aa8b36e58974717d5a6e4bc368c83167caac9e8954127c0bcfcc` |
| `source-model-card` | Hugging Face `README.md` at revision `44a0ca3e` | `552199e1e3be6d07de661baf23876fcbc354f8cfd33b391d2913291a3a5a8c32` |
| `source-model-encoder-config` | `model/encoder/config.json` at revision `44a0ca3e` | `5ab36d96756d5a5f78582be7143e89fff113e15f36101f2658d7208d73667be9` |

The PDF was downloaded twice with identical bytes. Its text layer, which every value assertion runs
against, is `pdftotext -layout` output from poppler 26.08.0, SHA-256
`08fa7d4b91c13ddcd5531b66cdec3629427ad1ef9ceef047d785bf1c408617f5`. For the review, regenerate it:

```sh
curl -sSL -o arxiv-2609.18745v1.pdf https://arxiv.org/pdf/2609.18745v1
pdftotext -layout arxiv-2609.18745v1.pdf arxiv-v1-layout.txt
npm run -s batch -- check-values data/omics/editjumps-20261115 \
  editjumps-20261115-source-arxiv-pdf-v1=<path to arxiv-v1-layout.txt>
```

The extraction copies live in the session scratchpad at
`/private/tmp/claude-501/-Users-timrichardson-Documents-projects-personal-blog/2b3e629e-c97e-4855-9278-c3793c720747/scratchpad/editjumps/dl/`.
Nothing is archived under `artifacts/`: the preprint carries no licence statement, so its bytes are
not redistributed here, and the MIT-licensed repository and model-card files are regenerable from
their pinned commit and revision.

The GitHub and Hugging Face licence files are byte-identical, so the hash does not tell them apart;
the URL and the revision do.

## Identities reused rather than duplicated

- **The protein language model.** The store already holds ESM-2 as `catalog-model-esm-2`, at family
  level, with 35M among its listed released scales. The EditJumps method, its scored arm, the
  released checkpoint and both evotuning arms link to it with `uses_model`. No new ESM-2 record was
  created, and the released checkpoint is a `configuration` of the EditJumps method, not a new
  pretrained model: it fine-tunes an existing released ESM-2 checkpoint.
- **The training corpus.** The store holds no Observed Antibody Space record. `data/entities` was
  searched for "Observed Antibody Space", "OAS" and "antibody"; the only hits were unrelated
  antibody-antigen datasets. New records were created for the paired corpus and for the homolog
  pairs built from it. One concurrent batch in this worktree, `poisk-20261115`, mentions the
  Observed Antibody Space in prose but creates no dataset record for it, so there is no collision;
  the coordinator should still check this before storing both.
- **EvoDiff.** The store holds `proteinbench-method-evodiff`, a bare ProteinBench configuration with
  no links, no attributes and a different setting. EvoDiff-MSA here is the alignment-conditioned
  variant run under a matched mutation budget, so it is a new method record rather than a reuse. A
  reviewer may prefer to link the two; that is a ruling for the review.
- No store record exists for EvoFlows, Edit Flows or evotuning, so all three are new.

## Decisions taken from the source text

**Which tables were stored, and why Table 1's upper block is not duplicated.** Table 1's upper
block ("ours") prints four metrics for six arms over two families. Table 2 prints ten metrics for
eight arms over the same two families under the same frame. `extract/check_tables.py` asserts, cell
by cell, that all 48 values of Table 1's upper block are identical to the matching four columns of
Table 2, and the assertion passes. The batch therefore stores those values once, from Table 2,
which is the superset. Table 1's *lower* block is a different thing entirely, the EvoFlows paper's
own reported values, and is stored in full.

**The two blocks are not pooled.** The paper opens section 4 with "our computed values and published
EvoFlows values are not comparable and we could not recover the original experimental conditions
from the paper", and Table 1's caption says the two blocks are not comparable and that each row
compares only against its own block's floor and ceiling. This is recorded three ways:

1. as a claim, `claim-values-not-comparable`, quoting both statements;
2. as four separate `protocol-published-*` protocols, so no evaluation of the reimplemented block
   and no evaluation of the published block ever share a protocol, and every comparison field on a
   published evaluation is null, which blocks automatic comparison by itself;
3. as an `evidence_concerns` entry on the arXiv source record, scoped with `applies_to` to the 118
   records that carry or rest on the published values: the six `config-published-*` records, the
   four `protocol-published-*` records, the 48 published evaluations and their 48 results, and the
   four Table 4 EvoFlows-column evaluations, results and protocols.

The concern is scoped rather than source-wide on purpose. The paper is a sound citation and its own
reimplemented values are usable; it is the upstream numbers whose conditions are unrecoverable.

**One protocol per reference-set condition.** Section 5 reports that expanding the reference
alignment from 200 to 800 homologs alters the normalised spectrum MMD ratio by 50% on Ty1 and 26%
on HER2-VH, "a difference sufficiently large to invert method rankings", and Appendix E reports
that scoring real homologs against real homologs gives covariance 0.790 at N=20, 0.921 at N=100 and
0.985 at N=800, so "raw scores from evaluations with differing reference set sizes are
mathematically non-comparable". Each reported reference-set condition is therefore its own
protocol, with the exact set size written into the protocol's `dataset`, `metric_qualifier` and
`protocol` fields:

| Protocol group | Reference set | Results |
| --- | --- | --- |
| `protocol-ours-200-*` (10) | 200 held-out homologs per family, ceiling 300 | 116 |
| `protocol-published-*` (4) | unrecoverable | 48 |
| `protocol-ceiling-ours-*` (4) | two families, 200 references each | 4 |
| `protocol-ceiling-published-*` (4) | six families, recovered from a figure | 4 |
| `protocol-covariance-references-{20,100,800}` (3) | 20, 100, 800 natural homologs | 3 |
| `protocol-ours-800-spectrum-mmd` (1) | 800-homolog alignment | 0 |

The 800-homolog protocol holds no result because the paper prints only the size of the change the
condition causes, not the scores under it. It is registered anyway so the condition and its
consequence have somewhere to live; `claim-reference-set-size-inverts-rankings` takes it as subject.

The ordering instability is recorded as a limitation on **every** affected result and evaluation,
in the shared `L_REFSET` string, and again on every affected protocol. The reviewer should rule on
whether it also warrants its own `evidence_concerns` entry. The argument against: each protocol
pins its own reference-set size, so comparisons across sizes are already blocked by the protocol
split, and a source-wide concern would withhold the paper's own reimplemented results from every
use. The argument for: the paper states the orderings themselves can invert, which is a claim about
the conclusions and not only about the numbers.

**Two configurations for EditJumps, because the sources disagree about the heads.** Section 3 lists
"linear rather than MLP rate heads" among four operational adaptations of the scored arm. The model
card's Heads row gives three MLP rate heads, and its quickstart loads the released weights with
`--rate-head mlp --q-head esm_lm_head`. Appendix E reports the two parameterisations give different
edit ratios, 0.19 against 0.22 to 0.28, so they are not interchangeable. The batch therefore holds:

- `config-editjumps-clock-40`, the arm Tables 1, 2 and 4 score, which carries every result; and
- `config-released-checkpoint`, the downloadable weights, which carries **no** result.

No result is assigned to the released checkpoint, because no source states that the scored arm and
the downloadable weights are the same configuration. This is a question for the reviewer.

**The released configuration, exactly as stated.** 35,213,590 parameters; a stock
`facebook/esm2_t12_35M_UR50D` trunk of 12 layers, hidden 480, intermediate 1920, 20 heads,
vocabulary 33, rotary positions, fp32; 1,660,105 unordered homolog pairs from an Observed Antibody
Space paired corpus of 2,586,927 VH.VL sequences; 20,000 steps at batch 16, which the card gives as
320,000 pairs and **about 19% of one epoch**, "not converged, and not claimed to be". The paper's
Appendix D agrees that the model remained non-converged at the 20,000-step budget and gives the
validation curve, 798.0 at initialisation to 135.2 at step 19,999.

Non-convergence is recorded as a configuration claim (`claim-released-training-budget`,
`claim-non-convergence`) **and** as a limitation on both configurations, not as a footnote. It is
not carried onto every result, because the limitation belongs to the system rather than to the
measurement; a reviewer who disagrees can move it.

**The edit budget is calibrated on average.** Recorded as `claim-edit-budget-approximate` from three
sources that say it independently: the paper's Limitations ("achieving a specific edit budget
requires empirical calibration rather than deterministic control"), `docs/limitations.md`
("approximate guidance via clock calibration"), and the README ("`--edits` is a target, not a
guarantee"). It is also the first limitation on `config-editjumps-clock-40`.

**Single-chain test constructs against two-chain training pairs.** Ty1 is a camelid single-domain
VHH and HER2-VH an isolated heavy chain, while training pairs are concatenated VH.VL. Recorded as
`claim-domain-shift`, as a limitation on `config-editjumps-clock-40`, and as a limitation on every
reimplemented-block protocol, evaluation and result.

**Licence scope.** MIT covers the repository's code and the released weights, stated in the paper's
Appendix D, in both byte-identical LICENSE files and in the model card. It does **not** cover the
pretrained ESM-2 checkpoint or the Observed Antibody Space corpus, which carry their own terms.
Recorded as two claims, `claim-licence-code-and-weights` and `claim-licence-scope`, and as
`access_and_reuse` on every repository and model-card source record and `reuse_restrictions` on
every Observed Antibody Space dataset record.

**Runtime is not flattened.** The three sources do not agree on what each describes as the same
20,000-step run. The review's reading of the three figures: the repository and the model card agree
with each other, about 5.8 h at about 1.05 s/step on an L4 and about 3 h at 0.54 s/step on an A100,
and it is the paper's Appendix D that differs, at 6 h 29 m and 1.09 s/step on an L4. It is one
disagreement between the paper and the two project artifacts, not three mutually inconsistent
figures, and the `source-code-performance` limitation was corrected to say so.

| Source | Figure |
| --- | --- |
| Paper, Appendix D | single NVIDIA L4, 6 h 29 m wall clock, 1.09 s/step |
| `docs/performance.md` | L4 about 1.05 s/step, about 5.8 h; separately an A100 at 3 h 0 m 43 s and 0.54 s/step |
| Model card | about 3 h on one A100 at about 0.54 s/step; about 5.8 h on an L4 |

Each is a separate claim against its own source (`claim-runtime-paper`, `claim-runtime-repository`,
`claim-runtime-model-card`), each naming the disagreement in its own `limitations`. No runtime
result was created and no single figure was chosen. The same was done for the best validation loss,
130.48 at step 18,500 on the card against 135.2 at step 19,999 in the paper
(`claim-best-validation-loss-disagreement`); the card marks its own step with a "TODO: confirm
step" comment.

**Metric scaling.** Table 2's "KL pool." column and Table 1's "KL ×103" column are printed times ten
cubed, and "JS pos." times ten squared. `printed_value` holds the value exactly as printed and the
scaling is in `unit_detail`, following the existing `"10^-2 (printed column header units)"`
precedent in the store.

**Printed dashes are not values.** Four cells of Table 2, the profile log-likelihood of `rand. mut.`
and `rand. pair.` in both families, print an en dash. No result was created for them and nothing was
recorded as zero. `check_tables.py` asserts the dash count of every row, so a dash cannot be
silently read as a number.

## Gaps

- **BF-DiT and BF-ESM.** Table 2 prints two further arms under these labels: one row per arm per
  family, ten metric columns each, so **40 cells** (corrected by the review from the 20 first written
  here). The labels appear nowhere else: not in the paper body, not in the repository at the pinned
  commit, not in the README and not in the model card. The evaluated system cannot be identified, so
  the 40 values are not stored. Recorded as `claim-unidentified-table-2-arms` and here.
  The review searched all 410 files of the repository tarball at commit `d827d47c` and confirms the
  two labels are absent, but found a lead the extraction missed: `docs/reproducing.md` prices "the
  four Branching Flows cells (45-80 min each)" in the section on regenerating the section 4.2 table,
  and `deploy/gcp/train.sky.yaml` says "there is no `dit` and no split head (that is Branching Flows,
  deliberately kept out)" and rejects a `branching_flows` run mode as "not part of this repository".
  Four cells, two trunks named `dit` and ESM: that is very likely what BF-DiT and BF-ESM are. It is
  an inference, not a stated definition, and neither file is a pinned source, so nothing was stored
  on it. A follow-up pass should pin those two files and the Branching Flows paper and decide whether
  the 40 cells can then be attached to an identified system.
- **Figures 1, 2, 3 and 4 carry no printed numeric markers.** Only the numbers their captions and the
  body print in words were taken: the clock normalisation values (ours 40, about 95 reproduces the
  published edit ratio of 0.43, about 80 optimises MMD at about 8.5 edits) and the Figure 3 novelty
  shifts. No marker position was read off a figure by eye, by colour or from pixels.
- **"Diversity" names two different quantities.** Table 1 heads its pairwise Levenshtein column
  "diversity", values 22.61 to 133.34, while Figure 1's caption defines diversity as a ratio to real
  homolog pairs with an axis of about 1.0 to 1.4. Recorded as `claim-diversity-column-label` and as
  a limitation on the arXiv source record. The stored metric for both Table 1 columns is Levenshtein
  distance, because that is what the values are; the printed heading is preserved in
  `metric_qualifier` and in the locator.
- **The 800-homolog reference condition prints no scores**, only the percentage change it causes.
- **The strictly disjoint reference sets print no scores**, only the shifts they cause (-36.7% Ty1,
  -12.6% HER2-VH, covariance up 12 to 17 points). The two disjoint subsets are registered with their
  size unreported, and no protocol or result was created for them.
- **No seed values are printed anywhere.** Table 1's caption says it reports individual runs and
  intervals across three seeds; Table 2 prints one value per cell with no interval, and Table 4
  prints a spread on two of its eight cells whose type the paper does not state. Those two are
  recorded as `unresolved_spread`.
- **The 697 MB of released weight files were not downloaded**, so no weight hash is recorded; only
  the model card and the encoder configuration were pinned.
- **No independent evaluation of EditJumps was searched for.** This is a source-resolution pass over
  the three URLs the issue names, not a literature search.
- **No Observed Antibody Space snapshot date, data units or accession list** is printed in any source.
- **MMseqs2 version is not printed**, and the paper records that the Needleman-Wunsch substitution
  matrix and gap penalties are left to third-party library defaults.

## Value checking

`extract/tables.py` holds every printed cell as a string. `extract/check_tables.py` asserts each
against the pinned PDF's text layer by matching whole printed rows, so a value taken from a
neighbouring column fails; it also asserts the printed row order, the column headings, the dash
counts, the Table 1 upper-block-to-Table 2 identity, and the Appendix E prose phrases. Three
negative controls were run and all three were rejected, with the unmutated transcription accepted:
two neighbouring Table 2 columns exchanged, one Table 1 lower-block cell changed in the last digit,
and the Table 1 upper-block identity broken by one digit.

`npm run -s batch -- check-values` over the whole batch gives **8 `in_cell`, 164 `in_row`, 3
`locator_not_parsed`**, with no `wrong_column` and no `overclaimed_in_row`
(`value-check.tsv`). The three unparsed locators are the Appendix E prose values, which are printed
in a sentence rather than a table; each says so in its own review note and needs the reviewer's
manual check. Two things the automated check cannot do, which the reviewer's sampled manual check
must cover:

1. **Block assignment.** Tables 1 and 2 each print the same row labels twice, once per block or
   family. A locator-based check matches a row label anywhere near the caption and cannot tell the
   blocks apart. `check_tables.py` does, by splitting the printed block at the family or block
   heading before matching rows, but the reviewer's sample should confirm it independently.
2. **Column assignment on a text layer**, which `check-values` does not verify directly.

Separately, `extract/validate_batch.py` checks all 465 records against the repository's own attribute
registry, relation rules, SKOS vocabularies and description rules. It passes, given the eight
proposed metric concepts. It is not a substitute for `records -- add`, which also runs the Zod
schema and the SHACL shapes:

```sh
# after the coordinator has added vocab-proposal.ttl to data/vocab/metric.ttl
python3 -I data/omics/editjumps-20261115/extract/validate_batch.py . data/omics/editjumps-20261115/batch.jsonl
```

To run it before the vocabulary lands, copy `data/vocab/*.ttl` to a scratch tree, append
`vocab-proposal.ttl` to its `metric.ttl`, symlink `shared/`, `data/entities` and `data/evidence`
into it, and pass that tree as the repository root.

## Vocabulary

Eight metric concepts are missing and proposed in `vocab-proposal.ttl`: `edit-count`,
`levenshtein-distance`, `maximum-mean-discrepancy`, `kullback-leibler-divergence`,
`covariance-agreement`, `mutual-information-product-agreement`, `entropy-delta` and
`log-likelihood`. The file states for each why it is not a respelling of an existing concept and
gives an external match where one exists. The ninth metric the paper reports, Jensen-Shannon
divergence, reuses the existing concept with the positional formulation in `metric_qualifier`.

The review accepted all eight, with the corrections listed above, and added them to
`data/vocab/metric.ttl`, so the batch validates. `vocab-proposal.ttl` is kept as the proposal it was;
the concepts as stored are the ones in `data/vocab/metric.ttl`.

## What the review changed

The rulings and their reasons are in `docs/reviews/2026-11-16-editjumps.md`. In this folder the
review added `review/column_check.py`, rewrote every record's `review` object, moved every record
from `needs_review` to `source_checked`, and made four content changes:

- the BF-DiT and BF-ESM cell count, 20 to 40, in `claim-unidentified-table-2-arms` and in the arXiv
  source record's limitations;
- the `source-code-performance` limitation, which said its L4 figures differ from the model card's
  when the two agree;
- `claim-clock-normalisation-governs-budget`, which now records that the body says a clock rate of
  about 95 replicates the published edit ratio while Figure 2's own annotation says about 94;
- the non-convergence of the scored editor, added as a limitation to the 24 results and 24
  evaluations on `config-editjumps-clock-40` rather than left only on the configuration.

The proposed `skos:exactMatch` on `kullback-leibler-divergence` was dropped before the concept was
added to `data/vocab/metric.ttl`: `STATO_0000471` is STATO's term for "estimate", and STATO holds no
Kullback-Leibler term at all.

## For the reviewer to rule on

1. Whether the reference-set sensitivity needs its own `evidence_concerns` entry on top of the
   per-result limitations, and if so how it should be scoped.
2. Whether keeping `config-released-checkpoint` result-free is right, or whether the head
   parameterisation difference between section 3 and the model card should instead be resolved one
   way and the results attached.
3. Whether the 20 BF-DiT and BF-ESM cells should be stored against a deliberately unidentified
   configuration rather than left out.
4. Whether `proteinbench-method-evodiff` and the new `method-evodiff-msa` should be linked.
5. Whether `status` should move from `needs_review` to `source_checked` across the batch.
6. Whether the Table 1 "diversity" heading warrants an `evidence_concerns` entry rather than the
   claim and source limitation it currently has.
