# Model pages, revision 1, 2026-11-27

Prepared by Claude agents. No human review is claimed. Three agents revised the pages, three others verified the revisions, one applied their findings, and a separate session checked and applied the result.

## What changed

36 model records have their `profile` replaced, and their `run_guide` where the paper contradicted it. These pages were first written on 26 November without the full text of the model's paper, which could not be fetched at the time. The papers were then saved (`docs/reviews/2026-11-26-paper-full-texts.md` and `2026-11-27-paper-full-texts.md`). Each page has now been revised by an agent that read the whole paper, including methods and appendices.

30 source records are added: the text of each paper as it was quoted. For a PDF that is its text layer, which has its own hash; the PDF itself is already a source on the record. No result, evaluation or claim was added or changed.

One page with a saved paper is not revised here. The agent revising RNAGenesis was interrupted and redid the folder, and that revision was discarded.

## What the revisions did

- Facts that the page marked as not reported or not extracted were searched for in the paper and filled where the paper states them: parameter counts, architecture, training data and its cutoff, context limits. Where the paper is silent the gap is kept, and its status now says not reported.
- Statements the paper contradicts were corrected. Examples: CARP's parameter counts had been read from checkpoint names and now use the paper's table; Tranception's page said no parameter count was published and the paper gives three; ProtBert's count is in the paper's table.
- Where the paper and another source differ (a README, a model card, a released config or weights file), the page states both and does not prefer one.
- Each page now carries a `structured` list of released checkpoints (90 entries across the batch). Pages from the first three batches had none.
- Limitations the paper states about its own model were added.

Each content file in `specs/` has a sibling record of every change in the working folder; the count per page is in the table below (510 changes in all).

## How the revisions were checked

Every copied passage was confirmed present in its saved file by `scripts/enrich/check_spec.py`. Three verifier agents that had not made the revisions judged 1153 statements on the revised pages, checking each change against the paper text around its quote, and raised 27 findings (2.3%): 1 contradicted by a source, 25 that went partly beyond it and 1 with no support. The one contradiction was a note describing a change that had since been reverted. 25 findings were applied and 2 were left, because the saved files showed the verifier was mistaken.

Most findings concerned the `structured` list: a count the paper gives for a model placed on a released file that no source ties to it, a code licence carried over to weights, a release date read from a file name. The rules applied are that a parameter count stays only when a saved file states it for that exact checkpoint, a weights licence only when a saved file states one for the weights, and a release date only when a saved file states it as a release.

No page in this batch was read in full by the applying session before merge.

## Found in the papers

Each is stated on the page concerned. They are leads, not conclusions.

- DGRNA: the paper gives 1 attention head in its Methods and 32 elsewhere; the code uses 32.
- ProtRNA: 6 million training sequences in the Results, Methods and a table, and 23 million in the Discussion.
- Uni-RNA: the paper's parameter counts for two sizes differ from the released weights, and it describes a larger model that is not released.
- EVE: the preprint reports 1,081 proteins and 11 million variants; the README and the journal abstract report 3,219 and 36 million.
- DeepVariant: the saved preprint describes the 2016 version and v0.4.1, not the version the record's results come from.
- DeepSTARR: 246 filters in the first layer in the paper's methods, 256 in the released model file.
- Genomics-FM: 1,160 species in the main text and 1,100 in the supplement; no source says which of two sizes the released checkpoint is.
- LucaOne: 1.8 billion parameters in the paper, 1.58 billion counted in the released weights.
- GROVER: the paper cites archive records for code and tutorial that differ from the ones read, and gives two input length limits.
- Orthrus: 45 million transcripts on the model card, 32 million unique in the paper.
- AIDO.DNA: a cosine schedule in the main text, linear decay in the appendix config for the smaller model.
- ProSST: 110 million parameters and a feed-forward size of 3172 in the paper; 115.6 to 118.7 million and 3072 in the released files.
- ModernGENA: absolute position embeddings in the released config; RoPE in the paper and the card.
- LncRFM: 6 and 12 attention blocks in the paper; 5 and 11 in the released config.
- CARP: two different training times in the paper.
- Puffin-D: two different web server addresses.

## Per model

| Record | Changes made | Structured entries | Coverage | Verifier findings |
| --- | --- | --- | --- | --- |
| `bacformer-20261115-model-glm2` | 14 | 2 | reviewed | 1 |
| `gfm2-20261011-you2026-model-rnaernie` | 13 | 2 | reviewed | 1 |
| `gfm2-20261011-you2026-model-utr-lm` | 21 | 16 | reviewed | 1 |
| `hyinv-20261106-model-hyinv` | 7 | 1 | reviewed | 0 |
| `intake-250-20261119-model-hevo` | 20 | 2 | reviewed | 1 |
| `intake-250-20261119-model-hevo-base-o` | 18 | 1 | reviewed | 0 |
| `intake-250-20261119-model-hevo-large-o` | 18 | 1 | reviewed | 0 |
| `intake-383-20261124-model-lncrfm` | 18 | 1 | reviewed | 1 |
| `ladon-20261115-model-bulkformer` | 18 | 3 | reviewed | 3 |
| `ladon-20261115-model-bulkrnabert` | 17 | 4 | reviewed | 2 |
| `ladon-20261115-model-ladon` | 9 | 1 | limited | 2 |
| `lit-genomics-20261011-dnalongbench-model-akita` | 15 | 2 | reviewed | 0 |
| `lit-genomics-20261011-dnalongbench-model-puffin-d` | 13 | 1 | reviewed | 1 |
| `lit-genomics-20261011-genbench-model-deepstarr` | 9 | 1 | reviewed | 0 |
| `lit-genomics-20261011-geneb-model-biofm` | 11 | 1 | reviewed | 0 |
| `lit-genomics-20261011-geneb-model-genomics-fm` | 14 | 1 | reviewed | 0 |
| `lit-genomics-20261011-geneb-model-grover` | 14 | 1 | reviewed | 0 |
| `lit-genomics-20261011-geneb-model-lucaone` | 17 | 6 | reviewed | 0 |
| `lit-genomics-20261011-guanine-model-aido-dna` | 12 | 2 | reviewed | 2 |
| `lit-genomics-20261011-guanine-model-phylogpn` | 12 | 1 | reviewed | 0 |
| `lit-protein-20261011-deepprotein-model-protbert` | 11 | 2 | reviewed | 0 |
| `lit-rna-20261011-rna3d-model-deepfoldrna` | 11 | 1 | reviewed | 0 |
| `lit-rna-20261011-rnagym-model-orthrus` | 14 | 4 | reviewed | 0 |
| `lit-rna-20261011-rnalm-zeroshot-model-dgrna` | 15 | 1 | reviewed | 2 |
| `lit-rna-20261011-rnalm-zeroshot-model-protrna` | 15 | 1 | reviewed | 0 |
| `lit-rna-20261011-rnalm-zeroshot-model-uni-rna` | 16 | 3 | reviewed | 1 |
| `model-execution-20261011-model-deepvariant` | 11 | 5 | reviewed | 0 |
| `model-execution-20261011-model-moderngena` | 15 | 2 | reviewed | 0 |
| `rna-splicing-20261013-spliceai2-model-spliceai2` | 12 | 2 | reviewed | 0 |
| `traitgym-20261116-model-gpn-promoter` | 15 | 1 | reviewed | 1 |
| `uc20260930-model-carp` | 18 | 4 | reviewed | 0 |
| `uc20260930-model-eve` | 14 | 1 | reviewed | 0 |
| `uc20260930-model-prosst` | 14 | 6 | reviewed | 2 |
| `uc20260930-model-trancepteve` | 12 | 3 | reviewed | 2 |
| `uc20260930-model-tranception` | 16 | 3 | reviewed | 2 |
| `vep-uc-20261014-model-lol-eve` | 11 | 1 | reviewed | 2 |
