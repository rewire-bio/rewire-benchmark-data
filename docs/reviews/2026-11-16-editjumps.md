# EditJumps, independent review

2026-11-16. Batch `data/omics/editjumps-20261115/`, issue
[#244](https://github.com/rewire-bio/rewire-benchmark-data/issues/244). Reviewed by a Claude
(Opus 5) agent that did not extract the batch, against the extraction frozen at `batch.jsonl`
SHA-256 `8c6cf9464cc3a31ada50a8b11b30440e049369c377dbf24251518b836b8556e1`, 465 records including
175 results. Not human scientific review. Nothing was reproduced: no model was run, no sequence was
generated and no metric was recomputed. Transcription is not reproduction.

Receipt: `data/omics/editjumps-20261115/review.json`. Mismatch report:
`data/omics/editjumps-20261115/value-check.tsv`. Reviewer script:
`data/omics/editjumps-20261115/review/column_check.py`.

Every stored number stands as extracted. No printed value, numeric value, source locator, metric
concept, qualifier, unit, direction or uncertainty was changed. Four descriptive fields were
corrected and one limitation was added to 24 results and 24 evaluations before the batch was stored;
they are listed under [Edits](#edits). All eight proposed metric concepts were accepted, one of them
after dropping a wrong external match.

## Sources and hashes

All nine artifacts were re-retrieved on 2026-11-16 from the `artifact_url` in their source records.

| Record | SHA-256 | Refetched |
| --- | --- | --- |
| `source-arxiv-pdf-v1` | `4211d8ef46c55efe8d89ba4ee6c0b4e57cca1e78d0856e9cdfbde37046a7f4e1` | matches |
| `source-arxiv-html-v1` | `ae0b05f6a7488dabd73990f02b6a6280a6673e0a6a0f2917713f913a5ec3ec4f` | matches |
| `source-code-readme` | `fbf05022b8140519c13bf60db99276df3edcbaeac57f091f54a0dc3921716c05` | matches |
| `source-code-licence` | `9f1abe28a25b5f6f95c58a81a647de3fa72ff6388d228c59bddd079255709989` | matches |
| `source-code-performance` | `01e59ef27b2e93b118b15239e57c6500045c99facd72f0b956e78ecf161217e3` | matches |
| `source-code-limitations` | `e11bb92210012e08e6a0bc0e6298d098818419f3d661bdae6082c71de9c0b6d8` | matches |
| `source-code-claims` | `7c7103723b23aa8b36e58974717d5a6e4bc368c83167caac9e8954127c0bcfcc` | matches |
| `source-model-card` | `552199e1e3be6d07de661baf23876fcbc354f8cfd33b391d2913291a3a5a8c32` | matches |
| `source-model-encoder-config` | `5ab36d96756d5a5f78582be7143e89fff113e15f36101f2658d7208d73667be9` | matches |

The arXiv HTML rendering is mutable and its hash describes one retrieval; it reproduced here
unchanged. The text layer every value was read from is exact: `pdftotext -layout` from poppler
26.08.0 over the refetched PDF gives SHA-256
`08fa7d4b91c13ddcd5531b66cdec3629427ad1ef9ceef047d785bf1c408617f5`, the value `notes.md` records.
Nothing is archived in the batch folder, which is right: the preprint carries no licence statement,
and the repository and model-card files are regenerable from their pinned commit and revision.

The five GitHub files were also checked against a tarball of commit `d827d47c3bcd29e0f4c15a15f9ac92a6cd859e99`,
where all five are byte-identical to the refetched raw files. That tarball is also what the BF-DiT
ruling below rests on.

## How the values were checked

`npm run -s batch -- check-values` over the whole batch, against the regenerated text layer,
reproduced the extractor's figures exactly: **8 `in_cell`, 164 `in_row`, 3 `locator_not_parsed`**,
with no `wrong_column` and no `overclaimed_in_row`.

164 results at `in_row` means the automated check confirmed the value appears somewhere in the row
the locator names, not that it sits in the column the locator names. Column assignment was therefore
checked separately by `review/column_check.py`, written for this pass. It uses neither
`extract/tables.py` nor `extract/check_tables.py`, and it never matches a value against row text. It
builds two independent column models:

- **PDF text layer.** Tables 2 and 4 print right-aligned columns, so every printed field is assigned
  to a column by clustering field right edges across the whole table; the script asserts exactly ten
  clusters for Table 2 and two for Table 4, and that each row puts exactly one field in each. Table
  1's lower block runs its columns together, `93.86` and `30.28` are one space apart, so right edges
  are useless there and the assignment is by ordinal position of the field within the printed row.
- **arXiv HTML rendering.** Each table is parsed as a cell grid from the table markup, with LaTeXML's
  `<annotation>` echo of the LaTeX source stripped. Column identity comes from the markup, not from
  spacing.

The two models agree on every cell of Tables 1, 2 and 4, and on the printed left-to-right order of
Table 2's headings. All **172** table-located results match the column, sub-column and block their
locator names under both models. Four negative controls are rejected by both:

| Control | Rejected |
| --- | --- |
| Table 2 ty1 EditJumps, `KL pos.` and `KL pool.` exchanged | 2 mismatches in each model |
| Table 2 her2vh Evotune, whole row shifted one column left | 10 mismatches in each model |
| Table 1 lower EvoFlows, `diversity` Ty1 and HER2 sub-columns exchanged | 2 mismatches in each model |
| Table 1 `EvoDiff-MSA`, upper and lower blocks exchanged | 8 mismatches in each model |

The block control matters most here. Tables 1 and 2 each print the same row labels twice, once per
block or family, and a locator-based check cannot tell the two apart. Both of this review's models
can, and both reject the swap.

### Manual sample

Thirteen cells were read by hand off the printed page and compared with the stored record, chosen to
cover every table, both blocks of Table 1, both family blocks of Table 2, both columns of Table 4,
the first and last metric column of Table 2, the two adjacent columns most easily confused
(`KL pos.` and `KL pool.`), and both printed spreads. All thirteen match:

| Locator | Printed | Stored |
| --- | --- | --- |
| Table 2, ty1, EditJumps, `edits` | 4.58 | 4.58 |
| Table 2, ty1, EditJumps, `prof. LL` | -64.01 | -64.01 |
| Table 2, ty1, rand. pair., `KL pos.` | 0.03 | 0.03 |
| Table 2, ty1, rand. pair., `KL pool.` | 0.14 | 0.14 |
| Table 2, her2vh, EditJumps, `cov. agr.` | 0.93 | 0.93 |
| Table 2, her2vh, Evotune, `KL pool.` | 0.37 | 0.37 |
| Table 1 lower, EvoFlows, diversity, Ty1 | 35.59 | 35.59 |
| Table 1 lower, EvoFlows, diversity, HER2 | 90.86 | 90.86 |
| Table 1 lower, evotuning (forced), KL ×10³, Ty1 | 54.79 | 54.79 |
| Table 1 lower, random pairing, edits/seq, HER2 | 93.86 | 93.86 |
| Table 4, Covariance (% of ceiling), EvoFlows (Published) | 98.4 | 98.4 |
| Table 4, Positional JS† (× floor), EditJumps (Ours) | 2.68 ± 0.10 | 2.68 ± 0.10 |
| Table 4, Pairwise Distance‡, EvoFlows (Published) | 1.00 | 1.00 |

Four absences were checked as well, and all four hold: no result carries a `Table 1, upper block`
locator; no BF-DiT or BF-ESM value is stored anywhere; no printed dash is stored as a value or a
zero, so the `prof. LL` column has eight results and not twelve; and the batch stores no value from
any figure.

The three results `check-values` cannot parse are the Appendix E prose values. They were read by
hand from the sentence they cite: "Scoring real homologs against real homologs yields covariance
scores of 0.790 at N = 20, 0.921 at N = 100, and saturates at 0.985 at N = 800." Each value, its
reference-set size and its unitless scale match.

The extractor's reason for storing Table 1's upper block only once, from Table 2, was re-derived
here rather than accepted: all 48 upper-block cells were compared by hand against the matching four
columns of Table 2 in both family blocks, and all 48 are identical. Storing them once is right.

Every one of the 43 claims was re-read at its locator in each source it cites, and every figure
quoted in a claim was checked against the source text.

## Rulings

### The paper's own statement that the two blocks are not comparable

Section 4 opens: "Before interpreting our results in Table 1, we note that our computed values and
published EvoFlows values are not comparable and we could not recover the original experimental
conditions from the paper." Table 1's caption adds: "The two blocks are not comparable; each row
compares against its own block's floor and ceiling, respectively random pairing and random
mutations."

The batch does not pool them. 93 distinct (configuration, protocol) pairs were enumerated and **no
protocol sees both a published configuration and a reimplemented one**; no evaluation pairs a
published configuration with a reimplemented protocol or the reverse. The published block has its
own four `protocol-published-*` records and its own four `protocol-ceiling-published-*` records, and
every comparison field on a published evaluation is null.

**The `evidence_concerns` entry is needed on top of the separation. Confirmed as written.** The
protocol split stops this store from computing a comparison; it does not tell a reader of a single
published-block result anything. The concern is what the website, the use-case judgements and the
discrepancy rules read, through `shared/omics/concerns.ts` and `_excluded` in
`scripts/kg/contradictions.py`. Its scope was checked record by record: `applies_to` names 118
records, every one of them exists in the batch, and the set is exactly the 118 published-block
configurations, protocols, evaluations and results, with nothing missing and nothing extra. There is
a second reason to keep it that the entry does not state and should: the EvoFlows column of Table 4
and the whole lower block of Table 1 were not published as numbers at all. Appendix E says they were
"recovered by extracting vector paths from the published PDF and calibrating against axis tick
marks". That is recorded as `claim-published-values-recovered-from-a-figure`, which carries the
detail; the concern already withholds the records it applies to, so no change was made.

### The reference-set instability

Section 5: "expanding the reference alignment from 200 to 800 homologs alters the normalised ratio
by 50% on Ty1 and 26% on HER2-VH, a difference sufficiently large to invert method rankings."
Appendix E: "raw scores from evaluations with differing reference set sizes are mathematically
non-comparable."

**No separate `evidence_concerns` entry. The extractor's argument holds, and the instrument would be
wrong.** Three reasons.

An entry with `applies_to` withholds every result that rests on the named record from comparisons,
use-case judgements and discrepancy inference. The 116 reimplemented-block results are not wrong and
are not individually unreliable: every arm in them was scored against the same 200 references, so the
comparison the table actually makes is internally valid. Withholding all of them would remove the
one thing this paper contributes that the comparability warning does not touch, its grounded
baseline set, from every use case.

The thing the paper warns about is comparing scores taken at different reference-set sizes, and that
is already blocked structurally, not by annotation: each reference-set condition is its own protocol,
with the set size written into the protocol's `dataset`, `metric_qualifier` and `protocol` fields,
and comparisons run within a protocol. The 800-homolog condition is registered as its own protocol
holding no result, because the paper prints only the size of the change and not the scores under it.

The inverted-ordering statement is a claim about conclusions, and it is recorded as one,
`claim-reference-set-size-inverts-rankings`, with the 800-homolog protocol as its subject. It is also
the second limitation on every affected result, evaluation and protocol, so a reader of any single
number sees it without looking anything up. The training-set overlap that compounds it, 113 of Ty1's
and 103 of HER2-VH's 200 references were in the training set, is the third limitation on the same
records.

### The released checkpoint carries no result

**Confirmed. The split is right, and the sources are further apart than the batch says.**

The paper's section 3 lists, among four operational adaptations of the arm it scores, "linear rather
than MLP rate heads (Figure 3)". Figure 3's caption defines the two arms it compares as "the
published Appendix A specification (filled markers; adapting ESM-2 language model heads) versus
lightweight linear rate heads with random token heads (open markers)". Appendix E's
"Non-Explanations for the Edit Budget Discrepancy" states the two are not interchangeable:
"Adhering to the published Appendix A head parameterization is more conservative (0.19) than
lightweight linear heads (0.22–0.28)."

The model card's Model details table gives the released weights "3 rate heads (`mlp`) + 2 token
heads", with the authors' own unresolved `<!-- TODO: confirm head count/names -->` on that very row,
and its quickstart loads them with `--rate-head mlp --q-head esm_lm_head`. That is the Appendix A
parameterisation, not the one section 3 says the scored arm uses.

No source states that the released weights are the configuration Tables 1, 2 and 4 score. The
checkpoint must therefore carry no result, and `config-released-checkpoint` carries none; the
reason is on the record, in its third limitation. Two further facts, found in this review, make the
split harder rather than easier to resolve and are recorded here as leads rather than stored,
because neither rests on a pinned source:

- `docs/reproducing.md` at the same commit tells a reader to regenerate the editor's section 4.2
  cells with `RATE_HEAD=mlp Q_HEAD=esm_lm_head`, which is the released checkpoint's parameterisation
  and contradicts section 3.
- The arithmetic leans the same way. The paper gives the scored arm's edit ratio as 0.180 at 35M and
  the reproduced gap as "0.20 reproduced vs 0.43 published", both nearer Appendix E's 0.19 for the
  Appendix A heads than its 0.22 to 0.28 for linear heads.

So there is real evidence that the scored arm used MLP heads and that section 3's sentence is the
error. It is not enough. One pinned source says linear, another says MLP, and the paper's own
ablation says the choice moves the number being compared. Assigning the results to the released
weights on the strength of an unpinned file and an arithmetic hint would be a guess. The right
follow-up is to pin `docs/reproducing.md` and ask the authors, not to decide it here.

### BF-DiT and BF-ESM

**Leaving them out is right. The cell count was wrong and is corrected: 40, not 20.** Two arms, two
families, ten metric columns is 40 printed cells, and that is what `claim-unidentified-table-2-arms`
and the arXiv source record's limitation now say.

Confirmed independently that the labels are defined nowhere in the pinned sources. The repository
tarball at commit `d827d47c3bcd29e0f4c15a15f9ac92a6cd859e99` was downloaded and all 410 files
searched: neither `BF-DiT` nor `BF-ESM` appears, and neither does a bare `BF-` or `BF_` token
anywhere. Neither label appears in the README, the model card, the encoder configuration, or in the
paper outside the two Table 2 rows per family. The repository's own README describes the section 4.2
benchmark as covering "six methods", which is the six arms this batch stores.

They should not be stored against a deliberately unidentified configuration. A result has to hang
off a configuration, a configuration off a method, and a method record would have to describe a
system no source describes. Forty numbers attached to a name nobody can resolve would enter the
graph, be picked up by discrepancy inference and use-case queries, and support nothing. The
collection rules say an unidentified system stays at the coarsest level that can be identified, and
here no level can be. The gap is recorded, which is what the rules ask for.

The review did find a lead the extraction missed, and it is in `notes.md` for a follow-up rather
than in a record. `docs/reproducing.md` prices "the four Branching Flows cells (45–80 min each)" in
the section on regenerating the section 4.2 table, and `deploy/gcp/train.sky.yaml` says "there is no
`dit` and no split head (that is Branching Flows, deliberately kept out)" and rejects a
`branching_flows` run mode as "not part of this repository". Four cells, and two trunks named `dit`
and ESM: BF is almost certainly Branching Flows. That is an inference from two incidental comments in
files that are not pinned sources, and the repository contradicts itself about whether those runs
exist in it at all, so nothing was stored on it. A follow-up pass should pin the two files and the
Branching Flows paper and decide then.

### Whether the awkward facts are where a reader would see them

- **Training budget and non-convergence.** They were on both configurations and on two claims, and
  on no result. **Changed.** The paper states the scored editor "remained non-converged at the
  20,000-step budget" with validation loss still falling at step 19,999, and the model card calls the
  budget about 19% of one epoch and says it is "not converged, and not claimed to be". That is not a
  property of the system in the abstract; it is what the reader of one of its scores most needs to
  know. The
  limitation is now the last entry on the 24 results and 24 evaluations that run on
  `config-editjumps-clock-40`, and on nothing else, because the budget belongs to the editor and not
  to evotuning, EvoDiff-MSA or the model-free baselines.
- **The edit budget is an average, not a guarantee.** Adequately placed, no change. It is a claim
  from three independent sources, the first limitation on `config-editjumps-clock-40`, and a
  limitation on all 12 `edits` results, which are the numbers it bears on.
- **Single-chain test constructs against two-chain training pairs.** Adequately placed, no change. A
  claim, a configuration limitation, and the fourth limitation on every reimplemented-block protocol,
  evaluation and result. Correctly absent from the published block, whose values are EvoFlows' own.

### Runtime and validation loss, kept as separate per-source claims

**Right, and no single figure should be chosen.** Each of `claim-runtime-paper`,
`claim-runtime-repository` and `claim-runtime-model-card` is a faithful record of its own source at
its own locator, no runtime result was created, and nothing was averaged or picked. Reconciling them
would be invention.

One correction to how the disagreement is described. It is not three figures that disagree three
ways. The repository and the model card agree with each other, about 5.8 h at about 1.05 s/step on an
L4 and about 3 h at 0.54 s/step on an A100; the paper's Appendix D is the outlier, at 6 h 29 m and
1.09 s/step for what it calls the same run. The `source-code-performance` limitation said its figures
differ "from the paper's and from the model card's", and the second half of that is wrong. Corrected.

The best validation loss is a genuine disagreement and stays as the separate claim
`claim-best-validation-loss-disagreement`: the card's 130.48 at step 18,500, carrying its own
`<!-- TODO: confirm step -->`, cannot be reconciled with Appendix D's 135.2 at step 19,999 reached
after "the final four evaluations improving by 2.3 units", which has the loss still falling at the
end.

### The remaining questions the extractor raised

- **EvoDiff.** Not linked to `proteinbench-method-evodiff`. That record is a bare ProteinBench
  configuration with no links, no attributes and a different setting; EvoDiff-MSA here is the
  alignment-conditioned variant under a matched mutation budget. Linking them would assert a sameness
  no source supports. Left as a new method record.
- **Status.** Moved from `needs_review` to `source_checked` on all 465 records. Every value and every
  claim has now been re-checked against re-retrieved, hash-matched sources by an agent that did not
  extract them. Nothing is marked `reproduced`.
- **The Table 1 "diversity" heading.** No `evidence_concerns` entry. The claim and the source
  limitation are the right weight: the heading is a wording collision inside one paper, between
  Table 1's column of unnormalised Levenshtein distances from 22.61 to 133.34 and Figure 1's ratio
  running about 1.0 to 1.4. The stored metric is `levenshtein-distance`, which is what the values
  are, the printed heading is preserved in `metric_qualifier` and the locator, and no figure value is
  stored, so nothing in the store can confuse the two. A concern here would withhold results over a
  label.

## Vocabulary

Eight concepts were proposed and **all eight were accepted** and added to `data/vocab/metric.ttl`.
Each was checked against the nearest existing concept in that file; none is a respelling.

| Concept | Nearest existing | Why it is not the same |
| --- | --- | --- |
| `edit-count` | `count` | `count` is a tally of items meeting a criterion, matched to STATO's count. This is a mean over a generated set, 4.58 on Ty1, and is matched across generators rather than ranked. |
| `levenshtein-distance` | `sequence-diversity` | `sequence-diversity` is a mean pairwise normalised Hamming distance at fixed length, which cannot express an insertion or a deletion. These arms change sequence length by design. |
| `maximum-mean-discrepancy` | `perturbench-energy-mmd` | That concept is scoped to PerturBench and is an energy distance reported under the name MMD. This is the general kernel two-sample statistic over k-mer spectra. |
| `kullback-leibler-divergence` | `jensen-shannon-divergence` | JS is the symmetrised, bounded relative of KL. KL is asymmetric and unbounded above, and the paper reports both. |
| `covariance-agreement` | `correlation` | The paper reports the scalar reduction of the covariance matrix as undefined upstream, so the concept must not imply a correlation coefficient. |
| `mutual-information-product-agreement` | `normalized-mutual-information` | NMI scores cluster assignments against labels on a bounded scale. This is an agreement between two MIP matrices with the reduction again undefined upstream. |
| `entropy-delta` | none close | A signed difference of positional entropies whose target is zero. No existing divergence concept has a zero target. |
| `log-likelihood` | `negative-log-likelihood` | The sign complement, not a respelling. The values are printed negative, -64.01 and the like, and the column's printed direction marker is ↑. Storing them under a concept defined as the negative, with direction `lower`, would need the printed value changed. The scheme already carries `jensen-shannon-divergence` and `jensen-shannon-similarity` as a pair for the same reason. |

Three changes were made to the proposal before it was added.

**The one proposed external match is wrong and was dropped.** `vocab-proposal.ttl` gave
`kullback-leibler-divergence` a `skos:exactMatch` to `STATO_0000471`. That IRI resolves to STATO's
term for **"estimate"**, not to any divergence. STATO was then searched for "Kullback",
"Kullback-Leibler", "divergence" and "relative entropy" and holds no Kullback-Leibler term at all, so
no exact match exists to substitute. The concept now carries a scope note saying so. The method was
validated against four IRIs already in `metric.ttl`, `STATO_0000047`, `STATO_0000240`,
`STATO_0000611` and `STATO_0000619`, which resolve to count, Kendall's correlation coefficient,
measure of correlation and negative predictive value, exactly as the file claims. The seven other
proposed concepts carry no external match, which is correct: STATO, QUDT and EDAM have no term for
any of them.

`edit-count`'s preferred label was changed from "Edits per sequence" to "Mean edits per sequence", so
that a key reading "count" is not read as a tally, and a scope note points at `:count`. Every
accepted concept gained a scope note and, where one exists, a `skos:related` link to the concept it
is most likely to be confused with, so that the next extractor meets the distinction before
proposing a ninth.

`data/vocab/metric.ttl` now holds 275 concepts, parses as Turtle, and nothing existing was removed or
reordered. `data/vocab/unit.ttl` was not touched: the batch reuses `percent` and `unitless`.

One vocabulary gap is recorded rather than filled. `data/vocab/direction.ttl` has only `higher`,
`lower` and `unknown`. Table 2 prints "→0" over the entropy delta column and "≈" over the pairwise
Levenshtein column, neither of which is any of the three. Both are stored as `unknown` with the
meaning in `metric_qualifier`, which is the closest honest option. A `target-value` direction would
fit several metrics in the store and is worth a separate proposal.

## Edits

Made in `batch.jsonl` before the batch was stored, so no `records -- change` cycle was needed. None
of them is a stored value. No `metadata-correction-*` claim was written, because the batch has never
been in a release and no reader has ever seen the previous wording; the before and after are here
instead.

| Record | Field | Change |
| --- | --- | --- |
| `claim-unidentified-table-2-arms` | `value` | "whose 20 cells this batch does not store" to 40, with the arithmetic spelled out and the repository search stated as all 410 files of the pinned commit |
| `source-arxiv-pdf-v1` | `limitations` | the same cell count, 20 to 40 |
| `source-code-performance` | `limitations` | "differ from the paper's and from the model card's" corrected: its figures agree with the model card and differ from the paper's |
| `claim-clock-normalisation-governs-budget` | `value` | records that the body says a clock rate of about 95 replicates the published edit ratio while Figure 2's own annotation says about 94, and that the paper reconciles neither |
| 24 results, 24 evaluations | `limitations` | non-convergence of the scored editor added, on `config-editjumps-clock-40` only |
| all 465 records | `status` | `needs_review` to `source_checked` |
| all 464 records carrying one | `review` | rewritten for this pass |

`notes.md` was corrected where it stated the same two wrong facts, and carries a "What the review
changed" section. The extractor's `review` objects described an extraction pass and have been
replaced throughout; one of them, on the four Table 4 results, also carried text about "the two
family blocks of Table 4" and about Table 1's upper block being stored from Table 4, neither of which
is true of Table 4. That text is gone with the rest.

## Conflicts and gaps that remain open

- **BF-DiT and BF-ESM.** 40 printed cells unstored and the arms unidentified. The Branching Flows
  lead above is the way in.
- **Which head parameterisation produced the scored numbers.** Section 3 says linear, the model card
  and `docs/reproducing.md` say MLP, and the paper's own ablation says the choice moves the edit
  ratio. Unresolvable from the pinned sources; the released checkpoint carries no result until it is
  resolved.
- **Two of the paper's own numbers disagree with themselves.** The clock rate that reproduces the
  published edit ratio is about 95 in the body and about 94 in Figure 2. The best validation loss is
  130.48 at step 18,500 on the card and 135.2 at step 19,999 in the paper.
- **The model card marks two of its own rows unresolved** with `TODO` comments, on the head count and
  on the step of the best validation loss. Both are recorded on the source record.
- **Figures.** No value was read off any figure. Figures 1, 2, 3 and 4 print no numeric markers, so
  only the numbers their captions and the body give in words are stored.
- **No seed values are printed.** Table 1's caption says it reports individual runs and intervals
  across three seeds; Table 2 prints one value per cell with no interval, and the two spreads Table 4
  prints are stored as `unresolved_spread` because the paper does not say what they are.
- **The released weights were not downloaded**, so no weight hash is recorded.
- **No independent evaluation of EditJumps was searched for.** This is a source-resolution pass over
  three URLs, and the review did not widen it.
- **The Observed Antibody Space corpus** has no snapshot date, data units or accession list in any
  source, and MMseqs2's version is not printed. The paper also records that the Needleman-Wunsch
  substitution matrix and gap penalties are left to third-party library defaults.
