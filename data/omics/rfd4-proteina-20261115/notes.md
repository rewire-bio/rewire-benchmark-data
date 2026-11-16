# RFD4-Proteina, 2026-10-19 matched flow and autoencoder release

Requested in rewire-bio/rewire-benchmark-data issue #240. Lane `structure-design`, search cutoff
2026-11-15. RFD4-Proteina is a flow-matching biomolecular design model released by the Institute for
Protein Design (Baker Lab) with NVIDIA GenAIR, published as code under BSD 3-Clause at
RosettaCommons/RFD4-Proteina and as weights at nvidia/RFD4-Proteina.

This batch registers the model, its release configurations, its runtime packages, the frozen project
benchmark the release ships with, and extracts every cell of the published efficiency table. It also
pins the project preprint, which exists and is now at version 3.

Extraction only. A different agent reviews it. Nothing here is marked reproduced and no review
sign-off is claimed; every `review` object names the extraction agent.

## Frozen extraction hash

`batch.jsonl` SHA-256: `f959706bc624873cfabc6db992dab16d8b61481422c2b17118e9c4fd97ceda8b`

Rebuild it with `python3 -I extract/parse_efficiency_table.py` then `python3 -I extract/build_batch.py`
from this folder. Both are deterministic and read only the archived artifacts.

## Sources

Every artifact was retrieved twice on 2026-11-15 with identical bytes, so no hash below is a
per-download stamp. The small text artifacts are archived gzipped under `artifacts/`; each source
record carries both the raw `artifact_sha256` and the `archive_sha256`.

| Source record suffix | Artifact | SHA-256 |
| --- | --- | --- |
| `source-hf-model-card` | `nvidia/RFD4-Proteina` README.md at revision `621b785abf9d61dd24f4b81ae4dbd1330728f030` | `38479d8e4c6e46ed7e1ec4ece0dd02c358ae46d73d56790c44be813201fd9b98` |
| `source-hf-release-checkpoints` | same revision, `release-checkpoints.json` | `17b8b56247bcae1caf5b39e758c40178863572de0485048dd41f261c93ad16c4` |
| `source-hf-benchmark-provenance` | same revision, `benchmarks/provenance.json` | `4e7a3051a58902cc7713d02c52941894eb9581b82e5af85a3b4f256f1a258336` |
| `source-hf-benchmark-methods` | same revision, `benchmarks/METHODS.md` | `46d1e181c495d4ecc9a3992a4e7f3cd8fae0b4904fb799ab5c1a883090ca837b` |
| `source-hf-benchmark-summary` | same revision, `benchmarks/summary.csv` | `5c6d525d988d0df7fecb74396f86401c1ddb4c31fa83f00b357ba77d855d8a10` |
| `source-github-readme` | repository README.md at commit `68058693cb88762a8aaf806571e13b291ce6318a` | `e3327fb127c36d9ff3d464caf14afbbd76ded521158a6be1abf860c11169fa64` |
| `source-github-licence` | same commit, LICENSE | `0927a01536709c20efa64834482fd4d50c9bb954353dbcf35c95a98675545470` |
| `source-github-checkpoints-doc` | same commit, `docs/reference/checkpoints.md` | `b18b755f5098208611f02cb4b4100eedeeca5730a450d484b2356e844fec8f3b` |
| `source-github-docs-index` | same commit, `docs/index.rst` | `228ddfd74255e4458fd8e542bdd8d0a2926ba639c5178f411996848b693c9c48` |
| `source-docs-site` | `https://rfd4-proteina.org/latest/` as served 2026-11-15 (mutable) | `3156b3a2e728a2d656cc0f16bcba75ab088e71641abf8518d502944383becf61` |
| `source-rosettacommons-post` | RosettaCommons post of 23 October 2026 (mutable) | `cb0d0739ef0d8f367f10f910c721ca299ca7a7b24d214f8929373604c9760f6b` |
| `source-preprint-v3` | preprint PDF version 3, 101 pages, versioned URL | `b581fc10da53e94b263c36a7871906f10ba6559f993c02e08f8b3de6b1d0347e` |
| `source-preprint-versions` | `https://rfd4-proteina.org/data/preprint-versions.json` as served 2026-11-15 (mutable) | `1c6c825a8694c5987d47c03d044385cc38b8a9162e2dbb69d78e9edb5cbc0b4d` |

Two internal consistency checks came out of this, both recorded on the source records:

- `benchmarks/provenance.json` declares `summary.csv` SHA-256
  `5c6d525d988d0df7fecb74396f86401c1ddb4c31fa83f00b357ba77d855d8a10`, which equals the hash of the
  retrieved file. The benchmark packet is internally consistent.
- `preprint-versions.json` declares version 3 SHA-256 `b581fc10...0347e`, which equals the hash of
  the PDF served at the unversioned `assets/paper/RFD4-Proteina.pdf`. Its declared version 2 hash
  also matched a separate retrieval of the version 2 PDF.

The preprint PDF is 54 MB at the version 2 URL and 13 MB at version 3; neither is archived here,
because both are refetchable at versioned URLs. The RosettaCommons post and the documentation site
are not archived, because neither states a reuse licence.

## Questions the issue raised, and what the source says

### Does the store already hold RFdiffusion, RFdiffusion2 or Proteina as models?

Only RFdiffusion. `data/entities/models.jsonl` holds `discovery-model-rfdiffusion`, a family-level
record with status `discovered`. There is no RFdiffusion2, RFdiffusion3 or Proteina model record.
Proteina appears in the store only as three evaluated configurations from a third-party comparison
(`genie3-2026-table3-method-proteina-mfs`, `genie3-2026-table3-method-la-proteina-ld1`,
`genie3-2026-table3-method-la-proteina-ld2`), and RFdiffusion also appears as evaluated
configurations (`genie3-2026-table3-method-rfdiffusion`,
`lit-structure-20261011-scaffoldlab-config-rfdiffusion`).

So nothing was duplicated. `claim-lineage` records the RosettaCommons post's statement that
RFD4-Proteina is the next generation of RFdiffusion, building on RFdiffusion, RFdiffusion2 and
RFdiffusion3 and incorporating advances from NVIDIA's Proteina model, with `target_id`
`discovery-model-rfdiffusion`. No graph edge was added: `variant_of` and `supersedes` both say more
than an announcement's "next generation of", and `supersedes` means record replacement in this
store. **Reviewer ruling wanted** on whether an edge is appropriate and which one.

Note also that the efficiency table's protein-binding comparator is **Proteina-Complexa**, which is
not the Proteina in the store's Genie 3 configurations. They are kept apart.

### Are the native and Diffusers packages one model or two?

One. The model card states it plainly: "It is one model throughout — nothing is retrained. The
Diffusers weights are the same tensors re-prefixed and split across `transformer/` and `vae/`", in a
separate repository only because Diffusers requires `model_index.json` at the root. So there is one
`model` record and two configurations of it, `config-release-2026-10-19` (native bundle) and
`config-diffusers-release-2026-10-19`, plus `claim-one-model-two-packages` recording the statement.

### Must the flow model and the autoencoder be a matched pair?

Yes, and the sources say so three times over, so this is recorded both as a claim and as a
configuration constraint:

- Checkpoints reference, "Types of checkpoints": "RFD4-Proteina always loads **two** checkpoints
  together to generate: a denoiser and the autoencoder it was trained against", and for the
  autoencoder row, "Fixes the latent space the released denoiser was trained in; use this pair
  together."
- Model card, "Checkpoints in this release": "The release is a **matched pair** ... They are not
  interchangeable across releases — the autoencoder defines the latent space the flow model
  generates in, and mixing a flow model with a different autoencoder produces nonsense rather than an
  error."
- `release-checkpoints.json`, `policy`: "The flow model and autoencoder are matched and must be used
  together; this release changes the latent dimension (16 -> 32) and residue vocabulary (33 -> 147
  classes), so its components are not interchangeable with the previous release's."

`claim-matched-pair` carries it, and `config-release-2026-10-19` carries it in `limitations` and
names both checkpoint files, their stable filenames and their published SHA-256 values. The optional
PEFT adapter has the same constraint: it loads onto the exact base pair it was fine-tuned against.

### Which checkpoint does the published efficiency table describe?

Not the 2026-10-19 release. The card prints, above the table: "**These numbers were measured on the
previous release pair**, in the October 9, 2026 frozen project benchmark, which predates the current
checkpoints. They have not been re-measured on the current release and should not be read as
describing it." The issue's framing is correct.

The source does **not** tie the table to a named checkpoint file, and the batch does not either. What
the sources give:

- The scope note names only "the previous release pair".
- The card's own "Checkpoints in this release" table has a column headed "Previous release", naming
  flow `chk_epoch_00000169_step_000000340000-ema` with autoencoder
  `2026_09_04_release_ae_z16_400k-ema`, latent dimension 16, 33 residue classes, 434,348,737 stored
  parameters.
- The same card also says the 2026-10-19 pair "supersedes the 2026-10-15 pair
  (`2026_10_15_hero_s43_c512_80k-ema` and `2026_10_15_unified_ae_s43_400k-ema`), which has the same
  architecture", and `release-checkpoints.json` repeats that in its `supersedes` key.
- `benchmarks/METHODS.md`, model recipes, RFD4-Proteina row: "exact schedule/checkpoint comes from
  each native config", and that native config is not in the packet.

So "the previous release pair" has two candidates in the same document and the table names neither.
The eight printed values are therefore attached to
`config-previous-release-high-thinking`, whose `version` says "The release pair preceding 2026-10-19,
as the model card names it; no checkpoint filename is tied to the efficiency table", whose
`checkpoint` is absent with missing reason `conflicting`, and whose `model_identity_note` sets out
both candidates. `claim-previous-pair-identity` records the same for the reviewer.
`config-release-2026-10-19` carries no results at all.

**Reviewer ruling wanted.** The October 9 freeze predates both dated October pairs, which points at
the "Previous release" column rather than the 2026-10-15 pair, but the card does not say so and this
batch does not infer it.

### What does the table's metric actually count?

Structurally distinct computational passers per GPU-hour, not experimentally active designs. The
issue is right. Three statements of it:

- Card: "**Metric:** mean per-target structurally distinct computational passers per GPU-hour,
  including generation and common AF3 evaluation. Higher is better." and "Computational passers do
  not establish experimental activity."
- `benchmarks/provenance.json`: `mean_over_targets(3600 * passing_structure_clusters /
  (generation_gpu_s + af3_gpu_s))`.
- `benchmarks/METHODS.md`: clusters are computed within each model, protocol and target with Foldseek
  at TM threshold 0.5, and "These are algorithmic structural clusters, not experimental successes or
  globally distinct proteins."

No existing metric concept fits. The nearest are `inference-throughput` (samples processed per
second, which counts work rather than passes), `energy-efficiency` (throughput per watt),
`accelerator-time` (the time itself, direction lower) and the proportion metrics `success-rate`,
`hit-rate` and `designability`, none of which has a compute denominator. There is also no per-hour
unit: the store has `sample-per-second` and `sample-per-joule` only.

`vocab-proposal.ttl` therefore proposes two concepts for the coordinator to add before the batch is
stored: metric `passing-design-clusters-per-accelerator-hour` and unit `count-per-hour`. The results
use them, with `unit_detail` "structurally distinct computational passers per GPU-hour, counting
generation time and common AlphaFold3 evaluation time" and a `metric_qualifier` that carries the
clustering rule, the attempt accounting and the benchmark's own pass criterion. Two points for the
coordinator: no STATO, QUDT or EDAM term was found for the metric, so it carries no external match,
and the unit's `closeMatch` to QUDT `PER-HR` should be confirmed to resolve before committing.

`claim-efficiency-metric-meaning` records the definition on the benchmark record, and every result
carries the "not experimentally active designs" statement in `scope_note`.

### Does target conditioning differ between comparator rows?

Yes, for two of the four rows, and the card says so: "Conditioning differs between some methods: PPI
uses RFD4 backbone conditioning versus all-atom conditioning for several baselines; DNA compares
unfixed RFD4 inputs with fixed-DNA baselines; Proteina-Complexa's small-molecule route uses fixed
ligands. Only three DNA targets are included."

The parser establishes which arm each printed cell came from, rather than taking it from that
sentence: each card value was matched to its `summary.csv` row, whose `dataset` column names the arm.

| Table row | RFD4 cell arm | Comparator cell arm |
| --- | --- | --- |
| Protein binders | `ppi_backbone` | `ppi_all_atom` |
| Small-molecule binders | `studio_figure_2c_unfixed` | `studio_figure_2c_unfixed` |
| Atomic Motif Enzyme | `mcsa_fixed` | `mcsa_fixed` |
| DNA binders | `dna_unfixed` | `dna_fixed` |

The difference is preserved rather than flattened: each arm is its own `protocol` record, with the
conditioning in `allowed_information` and repeated in each evaluation's `comparison.inputs` and in
each result's `conditioning`. The two protein-binding rows and the two DNA rows therefore sit on
different protocols with different `inputs`, which blocks automatic comparison between them. The
small-molecule and enzyme rows share a protocol, because both of their printed methods used the same
arm.

The source labels these arms in a column headed `dataset`, but under docs/collection.md a protocol
fixes the split, inputs and metric, and the target set is identical across arms. They are therefore
protocols over one dataset per target set, and each protocol's `scope_note` records the source's own
label for the arm.

### What does BSD 3-Clause cover?

The RFD4-Proteina model, weights and code only, Copyright (c) 2026, Institute for Protein Design,
University of Washington. `claim-licence-scope` records the card's own separation:

- Optional `alphafold2/runtime/` and `openfold3/runtime/` container images package third-party
  software that "stays under its own upstream licenses, some of which restrict commercial use or
  redistribution". The card says to review each upstream licence and "do not assume the BSD license
  applies to them".
- The ported OpenFold3 weights in `openfold3/weights/` are Apache-2.0.
- Neither refolding oracle is needed for generation.
- The training data "has its own source terms, described on the dataset card"
  (`claim-training-data-terms`).

The LICENSE file itself names no weights or third-party assets; what the licence covers is stated on
the model card, so both are cited together.

## What was extracted

### Results: 8, every cell of the efficiency table

| Row | Targets | RFD4-Proteina, high thinking | Best other method in this comparison |
| --- | --- | --- | --- |
| Protein binders | 24 | 71.60 | Proteina-Complexa 13.24 |
| Small-molecule binders | 77 | 112.25 | BoltzGen 15.48 |
| Atomic Motif Enzyme | 37 | 91.18 | AlphaProtein-novo (Codesign) 26.02 |
| DNA binders | 3 | 41.97 | BoltzGen (fixed DNA) 9.46 |

The table has four columns. The eight numeric cells are the eight `result` records. The `Benchmark`
column cells are the dataset and protocol names. The `Targets` column cells are carried as
`total_targets` on each dataset and `assessable_targets` on each evaluation, and were asserted
against the `targets` column of every matching `summary.csv` row. The two column headers are the
printed names: the RFD4 column header is the printed method name, and each comparator cell prints its
own name, kept in `printed_source_cell` and in `source_locator`.

`extract/parse_efficiency_table.py` reads the archived model card, checks it against the pinned
artifact hash, asserts the four printed row labels and the four printed header cells, requires each
value to be printed to two decimals, and asserts the scope note and the 200-attempts sentence are
present. It then cross-checks each value against `benchmarks/summary.csv` from the same revision,
which prints the same quantity per 10 GPU-minutes: every card value equals its `summary.csv` row
times six at the printed precision, and each row's `attempts` equals its targets times 200. All eight
cells passed. `extract/efficiency-table.json` holds the parse and the cross-check, including the
`summary.csv` panel, label, criterion and conditioning arm behind each cell.

`npm run batch -- check-values` was not run: it reads JATS XML tables or a `pdftotext -layout` text
layer, and this table is a Markdown table in a model card. The deterministic parse plus the
`summary.csv` cross-check stands in for it, and a reviewer can rerun both from `artifacts/` without
network access.

### Record counts

| Kind | Count |
| --- | --- |
| source | 13 |
| model | 1 |
| configuration | 6 |
| benchmark | 1 |
| dataset | 4 |
| protocol | 6 |
| evaluation | 8 |
| result | 8 |
| claim | 23 |
| **total** | **70** |

The six configurations are: the 2026-10-19 native release pair; the same release as a Diffusers
pipeline; the previous-release high-thinking setup that carries the efficiency table's RFD4 rows; and
three comparator configurations (Proteina-Complexa, BoltzGen, AlphaProtein-novo Codesign). One
BoltzGen configuration carries both printed BoltzGen cells, because the methods supplement gives one
recipe and the difference between the cells is the DNA conditioning arm, which lives on the protocol.
No model record was created for any comparator: no primary source for those methods was retrieved and
the store holds none, so each comparator configuration says so in `model_identity_note` and leaves
checkpoint, version and commit absent with reasons.

All eight evaluations have origin `author_reported`: the benchmark was built, run and published by the
RFD4-Proteina authors, who are also the authors of its best-performing method. Each evaluation's
`comparison.dataset_version` and `comparison.budget` are null, which blocks automatic comparison, and
that is intended.

`extract/validate_batch.ts` (the repository's own validators over `batch.jsonl`, without adding it to
the store) reports 70 records and no problems. Every concept key in the batch resolves against
`data/vocab/` except the two proposed in `vocab-proposal.ttl`.

## Gaps

- **The two vocabulary concepts are not in the store yet.** `npm run records -- add` will reject the
  results until the coordinator adds `vocab-proposal.ttl` to `data/vocab/metric.ttl` and
  `data/vocab/unit.ttl`.
- **Which checkpoint pair the efficiency table describes is not resolvable from the source.** Two
  candidates, named above; the batch records the identity as the source gives it.
- **`benchmarks/summary.csv` holds 52 method rows and only 8 were taken into records.** The rest
  include low and medium thinking arms, a reward-guided search arm, nine further comparators and a
  second small-molecule pass criterion (`disco`, the looser historical one) with its own 10 rows.
  They are a bounded next pass, not a gap in this table.
- **`benchmarks/source_data.csv` was not retrieved** (1.5 MB of per-target rows). It holds the
  numerators behind each rate, which is why `numerator` is absent on every result.
- **The preprint's result tables were not extracted.** Only the title page, Sections S4.1 to S4.2
  with Tables S11 and S12, and the code-availability statement were read. Tables S18, S22 and S28
  also report passers per GPU-hour, and Table S11 reports clustered pass rates for an ablation
  reference, a development-scale model and the release-scale model with their training GPU-hours.
  Table S11 is the one table in the project's own sources that ties efficiency-adjacent numbers to
  named training scales, so it is the strongest candidate for the next pass.
- **The project page's live benchmark explorer was not extracted, and it disagrees with the model
  card by design.** `website/benchmarks/coverage.csv` at the pinned code commit
  (sha256 `0af0eca8f63938c18b2de9a97407808625a2da376d7ec40bfb44821cf8362c4d`; no source record,
  because nothing in this batch rests on it) labels its RFD4 rows "Current
  October19 cohort" with `catalog_model` `rfd4_proteina_oct19_high`, and its
  `mean_unique_passers_per_gpu_hour_including_af3` column gives 66.48 for protein binders, 237.11 for
  small molecules, 155.19 for the enzyme set and 52.30 for DNA, against the card's 71.60, 112.25,
  91.18 and 41.97 for the previous pair. This is consistent with the card's own statement that the
  frozen packet is not the live catalog, and it is a lead for a later pass rather than a
  contradiction. Worth noting that protein binders is the only panel where the newer cohort scores
  lower on this metric.
- **The companion training-data dataset card was not retrieved or hashed**, so the training data's own
  licence is unverified beyond the model card's statement that it has separate terms. The Hugging
  Face API reports the dataset repository's `cardData.license` as `cc-by-4.0` at revision
  `aa86df1eb9e3529a0f39279f216dce3a95bb3dc2`, which was not confirmed against the card text and is
  not recorded in any record.
- **No checkpoint file was downloaded**, so none of the published weight SHA-256 values on
  `config-release-2026-10-19` was verified against the bytes. They are transcribed from
  `release-checkpoints.json`.
- **No preprint-server record or DOI was found** for the preprint. It is self-hosted on the project
  page, and its version history rests on the project's own `preprint-versions.json`.
- **No LinkedIn or other announcement URL was verified**, as the issue asked. None is recorded.
- **No inference was run.** Every record is source-checked, nothing is reproduced.

## Things a reviewer should look at first

1. The `config-previous-release-high-thinking` identity ruling (two candidate pairs, above).
2. The two proposed vocabulary concepts, in particular whether `count-per-hour` should instead be a
   single combined metric-and-unit concept, and whether the QUDT `PER-HR` close match is right.
3. Whether modelling the conditioning arms as protocols rather than dataset subsets is the call this
   store wants, given the source labels them `dataset`.
4. Whether `claim-lineage` should become a `variant_of` or `supersedes` edge to
   `discovery-model-rfdiffusion`, or stay a claim.
5. Whether one BoltzGen configuration for two printed cells is right, or whether the printed labels
   "BoltzGen" and "BoltzGen (fixed DNA)" should be two configurations.
