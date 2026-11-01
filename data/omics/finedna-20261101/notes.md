# FineDNA and Carbon-X

FineDNA (`HuggingFaceBio/FineDNA`, Apache-2.0, created 2026-10-30) is the training data of Carbon-X, a DNA
language model extended from Qwen3-14B. Found through a LinkedIn post by one of its authors; the dataset card is
the source.

## Decisions

- **A training corpus, recorded as a dataset.** Every other dataset in the store is an evaluation set. FineDNA is
  recorded so that training overlap can be checked for Carbon-X and for models trained on GENERator or
  OpenGenome2. `scope_note` says it is not an evaluation set; no protocol uses it.
- **No link from the model to the dataset.** `shared/omics/relations.ts` has no model-to-training-data relation.
  Carbon-X's `training_data` attribute names the dataset record ID instead.
- **Carbon-X added as a checkpoint** (`entity_level: checkpoint`), pinned to model commit `17de8916`, because no
  Carbon-X record existed.
- **Carbon-X's evaluation table is not extracted.** It compares Carbon-X with frontier language models on
  BioReason Coding, BioReason Non-SNV, GenomeQA, NextBase and FrontierVEP. Left as a follow-up.

## Points for readers

- The RL blend contains bioreason, vepqa and genomeqa prompts, the same task families as the Carbon-X evaluation
  benchmarks. The model card states that all training data was decontaminated against those benchmarks by
  whole-span DNA overlap, text n-gram overlap and homology search. Recorded on the model's `training_data`.
- `mid_dna_mrna_splice` holds 56.9 million OpenGenome2 mRNA sequences with splice and promoter context. That
  matters for any splicing evaluation of Carbon-X.
