# HyInv ProteinMPNN baselines: link to the family, not the checkpoint, 2026-11-17

Batch `data/omics/hyinv-proteinmpnn-family-20261117`. Change made by a Claude agent, requested by
the coordinating agent and approved by the repository owner on 2026-11-17. The source reading
below is the agent's; no human source review is claimed. Nothing was reproduced and no value was
changed.

## The change

The HyInv batch (`data/omics/hyinv-20261106`, #232) stored three ProteinMPNN baseline
configurations as `configuration_of` `catalog-model-proteinmpnn`, the record for a specific released
ProteinMPNN checkpoint (`variant_of` `discovery-model-proteinmpnn`). They now link to
`discovery-model-proteinmpnn`, the ProteinMPNN family:

| Configuration | Before | After |
| --- | --- | --- |
| `hyinv-20261106-config-proteinmpnn` | `catalog-model-proteinmpnn` | `discovery-model-proteinmpnn` |
| `hyinv-20261106-config-proteinmpnn-grouped` | `catalog-model-proteinmpnn` | `discovery-model-proteinmpnn` |
| `hyinv-20261106-config-proteinmpnn-low-noise-grouped` | `catalog-model-proteinmpnn` | `discovery-model-proteinmpnn` |

Each change keeps the previous link in a `metadata-correction-hyinv-20261117-*` claim.

## Why

The HyInv technical report (`hyinv-20261106-source-report`, the PDF pinned at Hyra-results commit
0dcc533) names no ProteinMPNN weight file. Table 5, "Baseline settings, weights and reproduction
check", gives each baseline's decoding and temperature, and the note under it says only "All
baselines use the released weights". The low-noise row says the checkpoint was trained with less
coordinate noise, but names no file. ProteinMPNN is released as several weight files (vanilla
models at several noise levels, plus CA-only and soluble models), so "the released weights" does
not identify one checkpoint. The batch's own records already say so: each configuration carries
`missing_metadata.checkpoint_revision` with reason `unreported`.

Linking the configurations to a specific checkpoint record therefore claims more than the source
supports. Where a checkpoint's identity is unresolved, the configuration stays at the family level.
The HyInv notes (section "Model level is `checkpoint`, not `family`") reasoned from HyInv's own
release, whose weights are a single file. That holds for HyInv, not for its ProteinMPNN baselines.

Read from the stored text layer of the report,
`data/omics/hyinv-20261106/artifacts/HyInv_Technical_Report.txt.gz` (decompressed sha256
`52ae9552b72266481b8c7190796f0bf2c93e4f8e84453c76b749b702edc50f52`): Table 5 and the note under it,
section 5.1 "Baselines" and Appendix D.1. The package README and Hyra-results README in the same
folder name no ProteinMPNN weight file either.

## Effect

- HyInv's ProteinMPNN evaluations and results now count for the ProteinMPNN family. The checkpoint
  `catalog-model-proteinmpnn` again has no evidence attributed to it directly, as before #232.
- Discrepancy inference compares these results as `discovery-model-proteinmpnn`. The three
  ProteinMPNN findings in release 2026-11-17-28b826b7be87 already use that ID and are all settled
  (`explained`).
- The website's adoption of release 2026-11-17-28b826b7be87 failed a test that checks the
  checkpoint page links to the family's results. That test encodes the rule above.
