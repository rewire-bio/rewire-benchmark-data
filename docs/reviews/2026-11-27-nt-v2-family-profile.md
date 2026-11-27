# Nucleotide Transformer v2 profile describes the family, 2026-11-27

Reviewer: `claude`. No human review.

`catalog-model-nt-v2` stands for the Nucleotide Transformer v2 family: configurations of every v2 size
link to it. Its profile was written from the 50M checkpoint's model card and called that checkpoint
"the linked checkpoint". Batch `data/omics/nt-v2-family-profile-20261127/` (`build.py`) changes only
the profile:

- The "Versions and reproducibility" section, and the parameters and versions facts, now describe the
  four checkpoints (50M, 100M, 250M, 500M). They cite the repository's `docs/nucleotide_transformer.md`
  (`evidence-official-657e83427ab59f3aec83`, pinned commit 2dc37b86). That file lists the four
  `*_multi_species_v2` models, says they range from 50 million to 500 million parameters, and says all
  were pretrained on the multispecies dataset (300B tokens for 50M and 100M, 1T for 250M and 500M).
  The fetched file matches the recorded SHA-256.
- Training data: the family's pretraining is stated first. The 50M card's genome and nucleotide
  counts are kept and attributed to that card.
- The access fact, the weights-licence fact and the limitation say that the model card is the 50M
  checkpoint's.

The conflict between the 50M card (1,000 tokens) and the documentation (2,048 tokens) is kept.
