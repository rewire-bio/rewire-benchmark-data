# BioEmu-2, October 2026 release: extraction notes

Batch: `data/omics/bioemu2-20261115/`. Lane: `structure-design`. Search cutoff: 2026-11-15.
Issue: rewire-bio/rewire-benchmark-data #241. Article counterpart: rewire-bio/rewire.it #439.

Frozen extraction hash: `batch.jsonl` SHA-256
`4e40c0c17e77b781c00b90eb27d48e25dd24aff077f650901762a3c63e4bf516` (94 records).
Nothing in `batch.jsonl` was changed after this hash was computed.

Extractor: Claude (Opus 5) extraction agent; no human review claimed. Review is a separate pass by
a different worker. Nothing here was reproduced: no model was run and no value was recomputed.

## What was pinned

Thirteen artifacts, all retrieved on 2026-11-15, hashed, and archived gzipped under `artifacts/`.
`build.py` rechecks every hash before using the text, so the batch can be rebuilt from the
archive alone.

Repository `microsoft/bioemu2` at commit `6d1ca744fa8ed285edafae7b98da65205bf00fd3`:
`MODEL_CARD.md`, `README.md`, `NOTICES.md`, `LICENSE`, `pyproject.toml`, `docs/checkpoints.md`,
`docs/sampling.md`, `docs/context-parallel-sampling.md`, `docs/propagation.md`.

Hugging Face `microsoft/bioemu2` at revision `dd4b0c1b69984b68edcb6200a544213be4d75242`:
`README.md` (the model card as published there), `checkpoints/bioemu2-preview/config.yaml`, the
Git LFS pointer for `checkpoints/bioemu2-preview/checkpoint.ckpt`, and the API file listing for
the revision.

The API listing is the one mutable artifact: its response carries counters such as downloads and
likes, so its hash describes that single retrieval. Its source record says so.

## Record counts

| Kind | Count |
| --- | --- |
| source | 13 |
| model | 1 |
| configuration | 5 |
| claim | 75 |
| evaluation | 0 |
| result | 0 |
| benchmark, dataset | 0 |

`extract/parse_model_card.py` parses the two printed tables in the model card, asserting the nine
summary row labels and all twelve training-data row labels in order, and writes
`extract/model-card-tables.json`; `build.py` reads the cells from there. Every other claim is a
hand transcription from a named section, which each claim's `review.method` and `review.note`
state. `extract/check_batch.py` checks the batch against the repository's own schema sources
(attribute registry, relation rules, entity kinds, the SKOS vocabularies) and reports zero
problems. The repository's own validators were also run over `batch.jsonl` alone:
`validateRecords`, `descriptionProblems` and `attributeIssues` all pass with nothing to report.

## Decisions, with reasons

### No evaluation or result records

The model card has an Evaluation methodology section that describes four settings, but it prints
no numeric value anywhere: no RMSD, TM-score, lDDT, DockQ, coverage or divergence figure, and no
table of results. The four descriptions are recorded as `evaluation_protocol` claims on the model.
No `evaluation` or `result` record was written, and nothing was inferred from the prose. The two
throughput figures in the context-parallel guide are linked images with no printed numbers, so
nothing was read from them either.

### No benchmark or dataset records

Each evaluation setting fails a different precondition for a benchmark record:

- Folding quality is measured on the Boltz-1 test set, which is defined in the Boltz-1 paper, not
  here, and the baselines are described only as "a range of state-of-the-art cofolding models"
  with none named. The store already holds `reported-dataset-e45a5a140888ee`, "Boltz-1 structure
  test set" (status `needs_review`, sourced to `boltz1-2025`). That is the ID to reuse if a
  reviewer later decides to register this protocol, but no link was made here, because the model
  card gives no version, split or target count to check the identity against.
- The multiconformational set is an in-house curated subset of paired PDB structures: unpublished,
  unsized, no accession.
- The MD emulation holdout is drawn from the same MD datasets the model was trained on, and
  `docs/collection.md` forbids creating a benchmark from a training dataset.
- The large-complex set is described only as "a subset of complexes exceeding 1,500 tokens".

The twelve training-data rows are recorded as `training_data_sets` claims with their printed
counts and modalities, not as dataset records, because the model card gives only a name, a modality
and a count for each, with no version, accession or split.

### Earlier BioEmu

The store holds no BioEmu, BioEmu2 or BioEmu-adjacent model record: `grep -ril bioemu data/`
returns nothing. So there was no identity to reuse. The pinned BioEmu-2 artifacts never mention a
predecessor either, in any of the thirteen files, so no `family`, `variant_of` or `supersedes` link
was recorded. Search does show an earlier BioEmu from the same group (a Microsoft Research page
titled "Scalable emulation of protein equilibrium ensembles with generative deep learning",
Science, July 2025, and a Nature Methods article at `nature.com/articles/s41592-025-02874-1`), but
neither article was retrieved in this pass. That is recorded in `scope-audit.jsonl` as deferred to
a separate discovery pass, not as a scope exclusion.

### Checkpoints and runtime packages are configurations, not models

The pinned Hugging Face revision releases exactly one checkpoint: the only files are
`.gitattributes`, `MODEL_CARD.md`, `README.md` and the two files under
`checkpoints/bioemu2-preview/`. So there is one model record, at `family` level, and five
configuration records:

- `config-checkpoint-bioemu2-preview`: the released weights, with the layer widths, conditioning
  switches and noise schedule from the distributed `config.yaml`, and the default precision from
  `docs/checkpoints.md`.
- `config-runtime-package-0-1-0rc0`: the `bioemu2` package at version 0.1.0rc0, holding both
  install paths. The `cuda` and `cuda12` extras are two install configurations of one package,
  declared mutually exclusive in `pyproject.toml`; nothing in the sources says they change the
  model's outputs, so they are not separate records.
- `config-mode-structure-prediction` and `config-mode-equilibrium-sampling`: the two tasks
  `docs/sampling.md` says the model was trained for, which select different sampling settings
  (sharpening at step scale 1.5, against step scale 1.0 without sharpening).
- `config-mode-propagation`: time-lagged propagation with implicit transfer operator models, usable
  at lags of 1 ns to 1000 ns.

The model record stays at `family` level because the model card prints no version number for the
model and does not name the checkpoint its evaluations used; `missing_metadata.checkpoint_revision`
records that. The mode configurations link `configuration_of` the model rather than nesting under
the checkpoint configuration, and name `bioemu2-preview` in their `checkpoint` attribute. Nesting
them under the checkpoint record is allowed by `relations.ts` and is a reviewer's call.

### The checkpoint digest was not recomputed

The checkpoint is 2,047,661,181 bytes and was not downloaded. The Git LFS pointer served at the
pinned revision publishes `oid sha256:3b4ba9236b7b458f47b40b694847b6bb4110c744becd6d2c53de7b1d04c07a81`
and that size. That digest is recorded in `checkpoint_sha256` on the checkpoint configuration with
a note saying it is the publisher's, and `weights_sha256` carries a missing reason of `unextracted`.

### The hardware disagreement

The two statements, at the same commit:

- `MODEL_CARD.md`, Technical requirements: "BioEmu-2 has been tested using NVIDIA GPUs, with an
  80 GB A100 being the smallest tested device."
- `README.md`, System requirements: compute capability 7.0 is the oldest supported, through the
  `cuda12` extra; the `cuda` extra needs 7.5 or newer; and "We have tested V100 (compute capability
  7.0), T4 (7.5, with the CUDA 12 installation), A100 and RTX A6000 (8.0 and 8.6), and B200
  (10.0)".

A V100 and a T4 are both smaller than an 80 GB A100, so the model card's "smallest tested device"
cannot be read as the floor. Neither artifact prints a memory figure for any system size, so no
minimum in gigabytes is supported by either. What the sources do support is a per-configuration
requirement, which is where it is recorded: the `hardware` object on the runtime package
configuration carries both statements and the tested list, and `accelerator_details` says in prose
why no single minimum is stated. Both statements are also kept as separate `hardware_tested`
claims, one on the model from the model card and one on the runtime configuration from the README,
each with its own locator, so neither overwrites the other. No minimum hardware value is asserted
on the model record.

One further asymmetry worth a reviewer's eye: the README ties the evaluated benchmark metrics to
Python 3.12, not to any GPU ("We tested BioEmu2 and evaluated its benchmark metrics with Python
3.12"), so the model card's testing statement and the README's evaluation statement are about
different things.

### Licence and third-party notices

Three separate facts, recorded as separate claims:

- `LICENSE` is the standard MIT text with Microsoft Corporation as copyright holder, and the model
  card's License row and the Hugging Face card metadata both say MIT.
- `NOTICES.md` states that MIT covers code "authored for BioEmu2 by Microsoft" except where
  otherwise noted, and that the distribution also contains third-party code under seven licence
  files. Two distributed files are not MIT: `src/bioemu2/assets/stereo_chemistry.yaml`, whose
  `monlib` section derives from CCP4 MON_LIB under LGPL-3.0, and
  `src/bioemu2/patches/mdtraj_patcher.py`, licensed LGPL-3.0 or later. Other portions come from
  Boltz v1.0.0 (MIT), PyTorch3D (BSD), torch_scatter (MIT), NVIDIA Fold-CP (MIT), OpenMM (MIT) and
  geostd.
- The model card separately says the model is "released for research purposes" and does not
  recommend commercial or real-world use without further testing. That is a developer
  recommendation, recorded as `usage_recommendation`, and it is not restated as a licence term.

The model's `licence` attribute says MIT and names the notices and the LGPL-3.0 files, so a reader
cannot take MIT as covering the whole distribution.

### Uncalibrated ensembles

The model card's limitation is explicit: "sampling frequency must not be interpreted as a
calibrated Boltzmann probability or quantitative free energy". It is carried three ways: as the
claim `limitation-uncalibrated-ensembles` on the model, in `limitations` on the released checkpoint
configuration, and in `limitations` on the equilibrium-sampling configuration, which is the
configuration a protocol would use if it tried to read state populations or free energy
differences off sample counts. Any later protocol or use-case judgement that scores state
populations, free energies or relative stabilities from BioEmu-2 samples contradicts the model
card and should not be created without saying so.

### Other wording decisions

- The training dates cell prints the two month names joined by an en dash. The claim value writes
  the span as "August to September 2026" and the review note says what the cell prints.
- The propagation lag range prints the upper bound with a micro sign; the claim spells out
  "microsecond". Grid sizes printed with a multiplication sign are written "2x2" and "4x4". Each is
  noted on the claim.
- Claims that join two printed sentences, strip markdown links or drop code spans say so in their
  review note. Everything else is verbatim.
- "Research preview", the phrase in the issue title, is not in the model card. What the sources
  support is that the single checkpoint is named `bioemu2-preview` and that the model card says the
  model is released for research purposes. The records use those words, not "research preview".

## Gaps

1. No numeric evaluation value exists in any pinned artifact, so the batch holds no result. The
   four evaluation descriptions are claims, not evaluations.
2. No paper, preprint or technical report for BioEmu-2 was found by 2026-11-15. The tree at the
   commit has no CITATION file, the README has no citation section, and the model card cites no
   publication. Three searches (general, arXiv-restricted, publisher-restricted) returned only the
   earlier BioEmu papers and third-party work. This is a recorded failure to find one, not a claim
   that none exists.
3. The evaluated checkpoint is unnamed in the model card.
4. No baseline is named for the folding comparison.
5. The curated paired-conformation subset and the MD holdout are neither published nor sized.
6. The smallest supported GPU is not stated consistently and no memory figure is printed.
7. The checkpoint bytes were not downloaded, so its digest was not recomputed here.
8. Throughput appears only as images; no runtime or memory figure was extracted.
9. The earlier BioEmu and the third-party evaluation in OriDynamics (arXiv:2611.11958, which names
   BioEmu2 as a baseline) were not retrieved. Both are leads for separate passes, recorded in
   `scope-audit.jsonl`.
10. No announcement URL or author was verified, so no announcement source exists and nothing rests
    on one.

## Questions for the reviewer

1. **Hardware.** Is the per-configuration treatment the right ruling: both statements kept as
   claims, the conflict described in `accelerator_details`, and no minimum asserted on the model?
   The alternative is an `evidence_concerns` entry on the model card source scoped with
   `applies_to` to the two `hardware_tested` claims. Adding concerns is a reviewer action under
   `docs/collection.md`, so none was added here.
2. **Model entity level.** `family` with one checkpoint configuration, or `checkpoint` on the model
   record itself? The model card prints no model version and does not name the evaluated
   checkpoint, which is why `family` was chosen.
3. **Mode configurations.** Keep the three sampling modes as configurations of the model, nest them
   under the checkpoint configuration, or drop them and keep only the settings claims?
4. **Boltz-1 test set.** Should `reported-dataset-e45a5a140888ee` be linked, or a protocol record
   created for the folding evaluation, given that no value, baseline or split is printed? This
   extraction created nothing rather than create an assessment with no result.
5. **Published checkpoint digest.** Is recording the publisher's LFS digest in `checkpoint_sha256`,
   with `weights_sha256` marked `unextracted`, acceptable, or should the 2 GB file be downloaded
   and hashed before anything is stored?
6. **Absence of results.** The absence of numeric evaluation values is recorded in this file, in
   the ledger `gaps` and in the model card source record's `limitations`, but not as a claim. If an
   in-store claim is wanted for it, that is a reviewer's call, because it is an observation about
   the source rather than a statement the source makes.
7. **Claim granularity.** 75 claims is a lot. The five README feature bullets and the three model
   card capability bullets could be merged into two claims if that is preferred; they are kept
   separate because each is a distinct printed statement with its own locator.
8. **Earlier BioEmu.** Should a separate batch register BioEmu (2025) and relate the two models,
   once its paper is pinned?
