# RFD4-Proteina, 2026-10-19 release: independent review

Batch `data/omics/rfd4-proteina-20261115`, 70 records (13 sources, 1 model, 6 configurations,
1 benchmark, 4 datasets, 6 protocols, 8 evaluations, 8 results, 23 claims). Extracted by a Claude
agent against issue rewire-bio/rewire-benchmark-data#240; reviewed by a different Claude (Opus 5)
agent. No human review and no reproduction is claimed. Receipt:
`data/omics/rfd4-proteina-20261115/review.json`. Mismatch report:
`data/omics/rfd4-proteina-20261115/review/value-check.tsv`.

Extraction reviewed at `batch.jsonl` SHA-256
`f959706bc624873cfabc6db992dab16d8b61481422c2b17118e9c4fd97ceda8b`. Two descriptive corrections
were made during the review, so the stored batch is
`dadbac38cdd354df387105491b2e9e033ec20a1f29e38c4779c9103adb6a42b4`; the frozen hash in the batch's
`notes.md` is the pre-review state.

## Sources and hashes

All thirteen artifacts were re-retrieved on 2026-11-15. Twelve hashed exactly to the
`artifact_sha256` on their source record:

| Source record suffix | SHA-256 | Re-retrieval |
| --- | --- | --- |
| `source-hf-model-card` | `38479d8e...1fd9b98` | matched |
| `source-hf-release-checkpoints` | `17b8b562...3ad16c4` | matched |
| `source-hf-benchmark-provenance` | `4e7a3051...a1f2588` | matched |
| `source-hf-benchmark-methods` | `46d1e181...090ca837b` | matched |
| `source-hf-benchmark-summary` | `5c6d5265...d855d8a10` | matched |
| `source-github-readme` | `e3327fb1...11169fa64` | matched |
| `source-github-licence` | `0927a015...675545470` | matched |
| `source-github-checkpoints-doc` | `b18b755f...e844fec8f3b` | matched |
| `source-github-docs-index` | `228ddfd7...48b693c9c48` | matched |
| `source-docs-site` | `3156b3a2...2944383becf61` | matched |
| `source-preprint-v3` | `b581fc10...6b5d0347e` | matched |
| `source-preprint-versions` | `1c6c825a...9edb5cbc0b4d` | matched |
| `source-rosettacommons-post` | `cb0d0739...3604c9760f6b` | **did not match, and cannot** |

Each of the ten archived gzipped artifacts was decompressed and hash-checked against the raw
`artifact_sha256`, and each `.gz` against its `archive_sha256`. Twenty of twenty matched, so every
archive is provably the pinned bytes.

Three sources are recorded as mutable (the documentation site, the RosettaCommons post and
`preprint-versions.json`) and each says so in its `version` and `limitations`. The two preprint PDFs
are unarchived because they are refetchable at versioned URLs, and the post and documentation site
are unarchived because neither states a reuse licence. Both statements are on the records.

### The RosettaCommons post hash is not reproducible

The post hashed to `c74c3f08...` on the first retrieval and `83c0ddae...` on a second four minutes
later, neither equal to the recorded `cb0d0739...`. Diffing the two shows why: the page embeds a
per-request Akismet comment nonce (`ak_js` went from `118` to `235`), a per-request WordPress.com
connect challenge with its own `expires` and `signature`, and a footer reading `generated in 1.295
seconds` against `generated in 1.332 seconds`. Nothing else differs.

The source record's limitation says the hash "describes one retrieval, although two retrievals on
2026-11-15 were byte-identical". For this page that cannot be right, and the claim is the finding.
The recorded hash is kept as published rather than updated, per the rule that a hash mismatch is a
finding and not something to fix by rewriting the hash. The page's prose was diffed instead and is
unchanged: the lineage sentences `claim-lineage` cites are present word for word, including the
first-mention spelling `RDF4-Proteina` that the record already notes. No value or performance claim
rests on this source.

### The two internal consistency checks hold

Both were re-run from the re-retrieved files, not from the extractor's output.

- `benchmarks/provenance.json` declares `"summary.csv":
  "5c6d525d988d0df7fecb74396f86401c1ddb4c31fa83f00b357ba77d855d8a10"`, which equals the SHA-256 of
  the re-retrieved `benchmarks/summary.csv`. The benchmark packet is internally consistent.
- `preprint-versions.json` declares version 3 SHA-256
  `b581fc10da53e94b263c36a7871906f10ba6559f993c02e08f8b3de6b1d0347e`. The PDF served at the
  unversioned `https://rfd4-proteina.org/assets/paper/RFD4-Proteina.pdf` and the PDF served at the
  versioned v3 URL are both 13,781,188 bytes with exactly that hash, so the declared hash is right
  and the latest pointer currently serves version 3.

## How the values were compared

`npm run batch -- check-values` does not apply here and was not run: it reads JATS XML tables or a
`pdftotext -layout` text layer, and the efficiency table is a Markdown table in a model card. The
extractor said so and that is correct.

In its place, `review/check_values.py` was written for this pass. It does not import or reuse
`extract/parse_efficiency_table.py`. It finds the "Measured design efficiency" section by its own
heading, asserts the four printed header cells and the four row labels, requires every value to be
printed to two decimals, splits comparator cells on the printed middle dot, and compares each
stored `printed_value`, `numeric_value`, `denominator`, `metric`, `unit`, `metric_direction` and
conditioning arm against that parse and against the archived `benchmarks/summary.csv`.

Three independent cross-checks all hold for all eight cells:

- every card value equals its `summary.csv` `unique_per_10_gpu_min` times six at the printed
  precision, the card publishing per GPU-hour where the CSV publishes per 10 GPU-minutes;
- each row's `attempts` equals its `targets` times 200, matching the card's own Targets column and
  each result's `denominator`;
- each cell's conditioning arm equals the `dataset` column of the `summary.csv` row behind it.

The script also re-derives which `summary.csv` row each cell must come from, rather than taking the
extractor's mapping: every RFD4 cell is the `rfd4_proteina_high` row of its panel, and every
comparator cell is the highest non-RFD4 `unique_per_10_gpu_min` in that panel and criterion. That
confirms the card's own column headings, "RFD4-Proteína, high thinking" and "Best other method in
this comparison", are what was extracted.

No sample was drawn, because there are only eight cells and all eight were read by eye against the
model card as well, column assignment included. `review/value-check.tsv` records 8 of 8 `in_cell`
with no mismatch. Every `null` and every `missing_metadata` entry on the eight results was checked
and is genuinely unstated: no GPU model is named, no seed is published, no uncertainty is printed,
and the passing-cluster counts are in `benchmarks/source_data.csv`, which neither pass retrieved, so
`numerator` is absent.

All 23 claims were read back sentence by sentence against the locators they name, including a
`pdftotext -layout` text layer of the 101-page version 3 preprint for the four preprint-sourced
claims.

## Rulings

### The eight values are attached to the previous pair, and the records cannot be read otherwise

Confirmed, and confirmed from the sources rather than from the issue.

The deciding text is the card's own blockquote above the table: "**These numbers were measured on
the previous release pair**, in the October 9, 2026 frozen project benchmark, which predates the
current checkpoints. They have not been re-measured on the current release and should not be read
as describing it."

The benchmark files do not say which checkpoint was used, and this matters for how the ruling is
worded. `benchmarks/provenance.json` gives only `"source_release": "supplement-20261009"`,
`"paper_commit": "8614542c..."` and `"scope": "Frozen project benchmark runs; not a new evaluation
of every model Hub revision."` `benchmarks/METHODS.md` says of the RFD4-Proteina row that the
"exact schedule/checkpoint comes from each native config", and closes with "executed receipts, not
the newest README, identify what each cohort actually ran". The native configs and the executed
receipts are not in the packet. So the packet is silent on the checkpoint and does not contradict
the card; the card's scope note is the only statement tying the table to a pair, and it is what the
batch records.

The records cannot be read as describing the 2026-10-19 release. Each of the three places checks
out:

- Configuration identity. The eight results reach
  `rfd4-proteina-20261115-config-previous-release-high-thinking`, whose `name` is "RFD4-Proteina
  (high thinking), previous release pair", whose `version` is "The release pair preceding
  2026-10-19, as the model card names it; no checkpoint filename is tied to the efficiency table",
  whose first limitation is "This is not the 2026-10-19 release", and whose `checkpoint` is absent
  with reason `conflicting`. `config-release-2026-10-19` carries no result and its own limitations
  say so.
- Protocol descriptions. All six protocols are named and described as the frozen project benchmark
  and are `part_of` `benchmark-frozen-project-benchmark-20261009`, which carries the October 9 2026
  freeze in its identity. The protocols deliberately name no checkpoint, which is right: each
  protocol is shared between RFD4 and a comparator, so a checkpoint on it would be false for one
  side. The checkpoint belongs to the configuration, and that is where it sits.
- Locators. Every one of the eight `source_locator` values names the card's "Measured design
  efficiency" table and its row and column, and each of the four RFD4 results carries the scope
  note in its own `scope_note`: "The card states this number was measured on the previous release
  pair in the October 9, 2026 frozen project benchmark, not on the 2026-10-19 release." The four
  evaluations repeat it in `limitations`.

### Which previous pair: narrowed, not resolved

The extractor asked for a ruling and left `checkpoint` absent with reason `conflicting`. That stays,
because the table names no checkpoint and no record should assert one. The weight of the source text
does narrow it towards the card's "Previous release" column, and the review records that in
`claim-previous-pair-identity`'s review note:

- `release-checkpoints.json`, key `policy`: "this release changes the latent dimension (16 -> 32)
  and residue vocabulary (33 -> 147 classes), so its components are not interchangeable with the
  previous release's". The previous release therefore had latent dimension 16 and 33 residue
  classes, which is the card's "Previous release" column
  (`chk_epoch_00000169_step_000000340000-ema` with `2026_09_04_release_ae_z16_400k-ema`), not the
  2026-10-15 pair.
- The card says the 2026-10-19 pair "supersedes the 2026-10-15 pair
  (`2026_10_15_hero_s43_c512_80k-ema` and `2026_10_15_unified_ae_s43_400k-ema`), which has the same
  architecture". A pair with the same architecture as 2026-10-19 cannot be the pair the policy
  describes as having a different latent dimension and vocabulary.
- The checkpoints reference closes the loop: the current release autoencoder's own training recipe
  is `configs/releases/ae/2026_10_15_unified_biomolecule.yaml`, so the 2026-10-15 "unified" names
  belong to the current architecture rather than to a predecessor of it.
- The October 9 2026 freeze also predates both dated October pairs.

That is a reading of the sources, not something any of them states, so it stays in a review note and
changes no record.

### Vocabulary: both proposed concepts survive

Neither is a respelling.

`metric:passing-design-clusters-per-accelerator-hour` was added to `data/vocab/metric.ttl` by this
review. The nearest existing concepts do not carry it. `:inference-throughput` is defined as "Number
of samples processed per second at inference", and the store uses it for reads, tokens and residues
processed per second with the counted entity in `unit_detail`; this metric's numerator is designs
that passed a criterion, not work done, so putting it under that concept would make the stored
concept definitionally false rather than merely loose. `:accelerator-time` is the time itself with
default direction lower. `:energy-efficiency` is throughput per watt. `:success-rate`, `:hit-rate`
and `:designability` are proportions with a per-attempt or per-tested-set denominator and no compute
denominator at all. A qualifier would not rescue any of them, because what differs is the quantity,
not its setting. The definition and scope note added to the file say what the numerator is, that the
clustering rule, pass criterion, accelerator time and aggregation go in `metric_qualifier`, and that
it is not comparable with a pass rate or with inference throughput. No STATO, QUDT or EDAM term was
found, so it carries no external match, which matches how `:inference-throughput` and
`:energy-efficiency` are already recorded.

`unit:count-per-hour` is also needed. The store has `:sample-per-second`, `:sample-per-joule` and a
dimensionless `:count`, and nothing per hour. The eight values are printed per GPU-hour, so
`:sample-per-second` would contradict `printed_value` and `:count` is not a rate. The store already
has precedent for a domain-specific rate unit with an unusual denominator in
`:variants-per-proband` and `:variants-per-diagnosis`.

**`unit:count-per-hour` was added to `data/vocab/unit.ttl` by the coordinator, not by this
reviewer.** `unit.ttl` was outside this reviewer's permitted edits, and the general ban on editing
`data/vocab/*.ttl` in the batch brief exists to stop several agents editing one file at once rather
than to forbid a new concept, which docs/collection.md allows in the same change. The reviewer
proposed the Turtle and the coordinator added it. This review then checked the result rather than
assuming it: the committed concept is byte for byte the proposed Turtle, placed alphabetically
between `:count` and `:day`, and `loadSchemes` parses all 22 schemes with
`unit:count-per-hour` and `metric:passing-design-clusters-per-accelerator-hour` both resolving to
their expected IRIs and labels. The reviewer did change one thing against the extractor's
`vocab-proposal.ttl` before proposing it: the definition now says the counted entity "and whether
the hour is wall-clock or device time such as a GPU-hour" go in `unit_detail`, because a GPU-hour is
not a wall-clock hour and the proposal did not say so.

The proposed `skos:closeMatch` to `<http://qudt.org/vocab/unit/PER-HR>` is kept:
the IRI resolves (HTTP 200) and QUDT defines PER-HR as reciprocal hour with dimension vector
`A0E0L0I0M0H0T-1D0`, which is right for a count per hour since a count is dimensionless. It is a
close rather than exact match because the device-time denominator lives in `unit_detail`.

### The version 3 preprint is not the primary source for any stored value, and it does hold tables this batch did not take

Two parts to this.

No stored value needs re-sourcing. None of the eight efficiency values is printed anywhere in
version 3. Searching the text layer for the eight printed strings `71.60`, `112.25`, `91.18`,
`41.97`, `13.24`, `15.48`, `26.02` and `9.46` returns nothing; loosening the search to `71.6`
returns a single unrelated hit, a `71.6` in the DNA-to-RNA nucleotide confusion matrix of the
latent-space analysis figure. The model card and `benchmarks/summary.csv` remain the only sources
for those cells. The preprint is the
stronger source for the architecture and training settings, and it is already cited for them:
`claim-flow-training` and `claim-autoencoder-training` both rest on it and both check out against
Section S4.2 ("We first trained the unified biomolecular autoencoder from scratch with 256-token
crops and a global batch size of 512 ... Complete training of the autoencoder required ~4,000 GPU
hours on NVIDIA H200s ... Pretraining with 256-token crops to 320,000 optimizer steps thus required
~16,000 GPU-hours ... fine-tuned the model for another ~2,000 GPU-hours with low-rank adaptation
(LoRA) with rank 32, scaling factor 64, and no adapter dropout") and against Tables S12 and S14.

Version 3 does print evaluation tables this batch did not extract: S11, S15, S16, S18, S22, S28 and
S29. They were not extracted in this pass and are recorded as a gap, per the instruction not to
widen the batch. Two are worth naming for the follow-up:

- Table S22, "Passing structural clusters per GPU-hour across six MCSA targets", reports the same
  metric concept this batch just added, on a six-target subset rather than the frozen packet's 37.
- Table S11, "Approximate flow-training compute and clustered pass rates (%) across model variants",
  ties efficiency-adjacent numbers to named training scales, and its release-scale row disagrees
  with the frozen packet in a way the follow-up should handle deliberately. S11 gives the K = 4
  release-scale model 10.6, 14.3, 12.1 and 3.5 per cent clustered pass rates for the protein,
  small-molecule, enzyme and DNA sets, over the same 24, 77, 37 and 3 targets at 200 attempts each
  with high-thinking sampling. `summary.csv` gives `rfd4_proteina_high` 9.77, 8.74, 8.91 and 2.17
  per cent on the same sets. That is consistent with the card's statement that the packet describes
  the previous pair and the preprint the release model, and it is the cleanest published evidence of
  what changed between the pairs, but it is a second author-reported figure for the same target sets
  and should be extracted with that relationship stated rather than silently.

### The conditioning difference is preserved, and no evidence concern is needed

The card's own sentence is "Conditioning differs between some methods: PPI uses RFD4 backbone
conditioning versus all-atom conditioning for several baselines; DNA compares unfixed RFD4 inputs
with fixed-DNA baselines; Proteina-Complexa's small-molecule route uses fixed ligands. Only three
DNA targets are included."

The arms are preserved three times over: each is its own protocol with the arm in
`allowed_information`, each evaluation repeats it in `comparison.inputs`, and each result repeats it
in `conditioning`. The extractor also established each cell's arm from the `dataset` column of its
`summary.csv` row rather than from that sentence, which this review re-derived independently and
confirmed:

| Table row | RFD4 cell arm | Comparator cell arm |
| --- | --- | --- |
| Protein binders | `ppi_backbone` | `ppi_all_atom` |
| Small-molecule binders | `studio_figure_2c_unfixed` | `studio_figure_2c_unfixed` |
| Atomic Motif Enzyme | `mcsa_fixed` | `mcsa_fixed` |
| DNA binders | `dna_unfixed` | `dna_fixed` |

An automatic comparison cannot treat the protein-binding or DNA rows as equivalent:
`shared/omics/catalogue-query.ts` checks `comparison.protocol_id` and `comparison.inputs` among its
compatibility fields, and both differ for those rows. The small-molecule and enzyme rows do share a
protocol, which is correct rather than a flattening: `summary.csv` puts both printed methods of each
of those rows in the same arm under the same criterion, and their `timing_note` is `per_attempt` on
both sides, so no timing-basis asymmetry separates them either. The batch-amortized RFD4 timing
(`batch_amortized;batched_generation_remeasurement_v1`) appears only on the PPI rows, which are
already split by protocol, so it never sits opposite a `per_attempt` comparator in a comparable
pair.

All eight are in any case withheld from automatic comparison while `comparison.budget` and
`comparison.dataset_version` are null, which the same `check` treats as "not fully reported". If
those were ever filled in, the protocol split would still hold the two rows that need holding.

No scoped `evidence_concerns` entry is needed. The author-run origin, the packet's own statement
that "the release does not assert that all models were equally optimized", and the disclosed
per-method adaptations are already carried on the protocols, the configurations and the evaluations,
and every evaluation has `origin: author_reported`.

Keeping `claim-conditioning-differences` on the benchmark rather than as a concern is right: it is
the source describing its own design, not a defect that should withhold records.

### Relating the release to RFdiffusion by a claim, not a link, is right

The only source is the RosettaCommons announcement, which says RFD4-Proteina "is the next
generation of RFdiffusion from the Institute for Protein Design (IPD)" and is built "upon previous
models, including RFdiffusion, RFdiffusion2, and RFdiffusion3, and incorporating advances from
NVIDIA's Proteina model".

`variant_of` would assert a shared architecture that the announcement does not describe and the
technical sources do not support: the preprint's architecture is a latent flow-matching model over a
learned biomolecular autoencoder with a 32-channel latent and a 147-class sequence head (Tables S13
and S14), which is not a variant of RFdiffusion's. `supersedes` means record replacement in this
store, and `discovery-model-rfdiffusion` is a live family-level record that this release does not
replace. "Next generation of" in an announcement is weaker than either relation, so the claim with
its `target_id` is the right shape and no graph edge should be added.

Two related calls were checked and both hold. The efficiency table's protein-binding comparator is
Proteina-Complexa, which is not the Proteina already in the store as the Genie 3 comparison
configurations, and the two are kept apart. One BoltzGen configuration carrying both printed
BoltzGen cells is also right: `benchmarks/METHODS.md` gives BoltzGen one recipe, the difference
between "BoltzGen" and "BoltzGen (fixed DNA)" is the conditioning arm, which lives on the protocol,
and each result keeps its own `printed_source_cell`.

## Corrections

Both were made in `batch.jsonl` before the batch was stored, so neither needed `records -- change`.
The previous value is kept in the review note of each record that changed.

1. The Atomic Motif Enzyme conditioning text read "Fixed-ligand conditioning. The methods
   supplement states that 'partially fixed' refers to ligand conditioning and that catalytic motif
   constraints are present in both conditions." The second half is not in any of the thirteen
   sources: "catalytic" appears once across all of them, in the repository README's list of
   tutorials, and the supplement's only statement about the degree of fixing is "AME compares
   *partially* to fully fixed ligand, not fully unfixed." The text now says that and nothing more.
   It was replaced in the AME protocol's `allowed_information` and `description`, in both AME
   evaluations' `comparison.inputs` and in both AME results' `conditioning`. The AME protocol's
   `description` was also repaired, since the invented sentence had been spliced into it mid-clause.
2. `claim-inputs` listed "coordinate groups" as an annotation type. The phrase occurs in the
   sources only in `benchmarks/METHODS.md`, about how motif RMSD is scored against stored input
   references, and that file is not among the claim's sources. The value now follows the repository
   README's own list, "fixed motifs, hotspots, burial, hydrogen bonds, and more".

The other glosses in the arm descriptions were checked and left alone. "Backbone conditioning: the
target sequence and backbone coordinates are supplied, target sidechains are not" and "All-atom
conditioning: the target sequence, backbone coordinates and sidechains are supplied" are readings of
the card's "backbone conditioning versus all-atom conditioning", not quotations, but they are the
only reading those terms admit and each protocol's `scope_note` records the packet's own label for
the arm, so a later reader can check them.

## Conflicts

Only the RosettaCommons hash, above. Nothing in the thirteen sources contradicts anything else, and
no stored value disagrees with its source.

No discrepancy involves this batch. Its results are new to the store and the metric concept is new
with them, so no existing result shares their metric, qualifier, unit and direction and none can be
flagged as an outlier or consensus against them. No `discrepancy_review` claim was raised.

## Gaps that remain

The extractor's recorded gaps were checked and all stand. The ones a later pass should pick up, in
order of value:

- The preprint's supplementary result tables, Table S11 first for the reason given above, then S22,
  S18, S28 and S29.
- `benchmarks/summary.csv`'s other 44 method rows: the low and medium thinking arms, the
  reward-guided search arms, nine further comparators and the looser historical `disco` criterion
  panel.
- `benchmarks/source_data.csv`, which holds the passing-cluster counts behind the eight rates and
  would let `numerator` be filled.
- The companion training-data dataset card, whose licence is unverified beyond the model card's
  statement that it has separate terms. The Hugging Face API reports the dataset repository's
  `cardData.license` as `cc-by-4.0`, which was not confirmed against the card text and is recorded
  in no record.
- The project page's live benchmark explorer, whose `coverage.csv` at the pinned code commit labels
  its RFD4 rows a current October 19 cohort and gives different values. The card itself says the
  frozen packet is not the live catalog, so this is a lead rather than a contradiction, and no
  source record rests on it.

Still unverified and staying so in this pass: no checkpoint file was downloaded, so the published
weight hashes on `config-release-2026-10-19` are checked as transcriptions and not against the
bytes; the GPU model behind the GPU-hours is unreported in every source; and no preprint-server
record or DOI exists for the preprint, so its version history rests on the project's own manifest.
