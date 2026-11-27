# Differences found in the sources

`kb/curation/source_leads.jsonl` is a register of places where a model's or a benchmark's own files disagree:
a paper with its released code or weights, an abstract with its results, a README with the script it documents,
a model card with its config, two licence statements for the same files, or a leaderboard with the developer's
current result. Each was found while writing the model and benchmark pages of 26 and 27 November 2026. Most are
stated on the page concerned; the eight whose evidence comes from the upgrade pass of existing pages (folder
`upgrade1`) are not yet on a committed page.

The register holds 73 leads. Eight were added on 27 November from the full text of the cdsFM preprint, which covers DeCodon and EnCodon; those eight are not yet on a committed page and have not been checked by a second pass, which their `basis` says. None has been raised with anyone. The owner of this repository raises them himself;
Reports for the ten judged most worth raising are drafted and held by the owner until he posts them.

## How a lead was admitted

- Both sides are quoted from a file saved under the page batch's `artifacts/` folder. The quote must occur in the
  file after collapsing runs of whitespace to one space, the rule `check_spec.py` uses. A script checked every quote.
- Each side names the file it was read from (relative to the batch working folders) and, where the file is
  pinned by a source record on that model or benchmark record, the source record id. Eight sides read from the
  newer upgrade pass have no source record yet, so their `source_id` is null.
- A count made by Rewire from a saved file (the SEQC2 gain calls) says so in the side's text, with how it was counted.
- The control from `docs/rebuild.md` was applied where it fits: is there an innocent explanation in the same files,
  such as a later version, a rounding, a subset, a concept against a version DOI, or code that states the change
  itself? If a saved file explains the difference, it is not a lead.

## Grades

- `strength`: strong when both sides are unambiguous statements about the same thing in files by the same developers
  or authors; moderate when an innocent explanation is plausible but not shown, or the two sides are by different
  groups; weak when one side is only a name or a computed count.
- `impact`: high when it changes a headline result, a comparison between models, whether a result can be reproduced,
  or what a user is licensed to do; medium when it would cost a user time or give a wrong figure in a description;
  low when cosmetic.
- `where_to_raise` is the repository or discussion page the saved files name for the model or benchmark, and null
  when none is named.

## Strong leads with high or medium impact

| Lead | Impact | What | Who could answer |
| --- | --- | --- | --- |
| `dnalongbench-cnn-best-checkpoint-unused` | high | The released CNN baseline script saves the weights of the best validation epoch but scores the test set with the last epoch's weights and never loads the saved file. | the benchmark's maintainers |
| `protssn-licence-readme-vs-card` | high | The ProtSSN repository says the project is under CC BY-NC-ND 4.0, while the Hugging Face repository holding the checkpoints declares Apache-2.0. | the model's developers |
| `puffin-weights-zenodo-cc-by-vs-academic-only` | high | The Zenodo record that hosts puffin_D.pth declares CC BY 4.0, while the README and LICENSE restrict Puffin to non-commercial academic use. | the model's developers |
| `deepfoldrna-licence-readme-vs-license-file` | high | The DeepFoldRNA README says the code is under the PolyForm Noncommercial licence, while the repository LICENSE file is an MIT text naming other copyright holders. | the model's developers |
| `molforge-three-licences` | high | The MolForge README badge says CC BY-NC 4.0, its License section says CC BY-SA 4.0, and the LICENSE file is CC BY-NC-SA 4.0. | the model's developers |
| `trednet-weights-licence-zenodo-vs-kipoi` | high | The Zenodo record holding the TREDNet weights declares CC BY 4.0, while the repository's Kipoi model description declares CC-BY-ND. | the model's developers |
| `virocaduceus-base-model-paper-vs-release` | high | The ViroBench paper says ViroCaduceus was built from Caduceus-PS, while the released model card and embedding script use the Caduceus-Ph base. | the benchmark's authors, who also released the model |
| `genos-licence-readme-vs-paper-and-hub` | medium | The Genos README puts the models and code under Apache-2.0, while the paper and the Hugging Face metadata for the checkpoints say MIT. | the model's developers |
| `protgpt2-license-file-vs-card` | medium | The LICENSE file in the ProtGPT2 Hugging Face repository is MIT, while the model card metadata in the same repository declares Apache-2.0. | the model's developers |
| `ankh-licence-text-vs-link` | medium | The Ankh README names CC BY-NC-SA 4.0 for the pretrained models but links to the CC BY 4.0 deed. | the model's developers |
| `escott-gpl-vs-setup-special-license` | medium | The PRESCOTT repository LICENSE and the paper say GPLv3, while setup.py declares a Special License. | the model's developers |
| `kendiukhov-readme-contact-vs-zenodo-cc-by` | medium | The code repository asks users to contact the author before reuse, while the Zenodo software record for the same release states CC BY 4.0. | the benchmark's author |
| `graphdta-pretrained-models-not-in-repository` | medium | The GraphDTA paper says pre-trained models are available in the GitHub repository, but the complete repository tree at the commit read holds no model file. | the model's developers |
| `s2f-gvp-hidden-size-paper-vs-config` | medium | The S3F paper gives the GVP layers 100 scalar hidden channels, while the released evaluation configs set node_h_dim to 256 scalar and 16 vector channels. | the model's developers |
| `brandes-stop-gain-counts-legend-vs-methods` | medium | The Brandes et al. 2023 Fig. 6d legend gives 32,362 and 36,034 pathogenic stop-gain variants, while the Methods give 32,441 and 36,113 for the same groups. | the paper's authors |
| `elixir-ppi-submission-columns` | medium | The ELIXIR interface benchmark README asks submitters for columns entry_id and score, while the validation script rejects a file without a raw_score column. | the benchmark's maintainers |
| `genie-readme-weight-path` | medium | The Genie README loads weights/configuration and weights/genie_l_128_epoch=49999.ckpt, while the repository holds the checkpoints in per-model folders such as weights/scope_l_128/. | the model's developers |
| `openfold3-default-parameters` | medium | The OpenFold3 parameters page marks openbind-2025-06-30-174k as the default, while the flowchart on the same page says to use openfold3-p2-155k as the default. | the model's developers |
| `hycell-gene-selection-readme-vs-report` | medium | The HyCell README says the 818 expressed genes that enter the model are the highest by value, while the technical report says they are sampled when a cell expresses more. | the model's developers |
| `utr-lm-example-pretraining-flags` | medium | The UTR-LM README's example pretraining command sets 6 heads and an embedding size of 16, while the same README's General Parameters give 16 heads and 128. | the model's developers |
| `birna-bert-readme-example-model` | medium | The BiRNA-BERT README example loads Lancelot53/birnabert-2ep, while the model card loads buetnlpbio/birna-bert. | the model's developers |
| `seqc2-ascatngs-version` | medium | The SEQC2 CNV paper names ascatNgs v2.5.1 in its Methods text and version 4.2.1 in its methods table. | the paper's authors |
| `aido-protein-rag-zero-shot-repository-missing` | medium | The zero-shot ProteinGym model card for GB.Protein-RAG points to a GitHub repository for installation details that the GitHub API reports as not found. | the model's developers |

Two moderate leads with high impact should be read with these.

- `frigid-superseded-result-on-massspecgym-leaderboard`: the FRIGID developers withdrew their MassSpecGym top-1
  accuracy of 18.29% after finding test-set information in an encoder's training data, and now report 9.05%. The
  updated leaderboard in MassSpecGym in the Wild (arXiv v1, the version saved) lists 18.29%. It is moderate because
  the two sides are by different groups and no saved file shows the current leaderboard.
- `lol-eve-hf-wrapper-not-the-model`: the Hugging Face modelling code that the LOL-EVE README loads calls itself a
  simplified demonstration and takes no gene embedding input, while the README lists ESM embeddings as gene context.
  It is moderate because the trained weights may still load into it.

## Counts

By kind: paper_vs_weights 16, readme_vs_code 11, licence_conflict 11, paper_internal 10, paper_vs_code 7, card_vs_config 6, other 5, abstract_vs_body 4, benchmark_vs_developer 2, address_dead 1.

| Strength | High | Medium | Low | All |
| --- | --- | --- | --- | --- |
| strong | 7 | 20 | 13 | 40 |
| moderate | 4 | 10 | 8 | 22 |
| weak | 0 | 0 | 11 | 11 |

6 leads have no named place to raise them: seqc2-gain-calls-paper-vs-deposit, dreams-mist-retrieval-match-rule, zero-shot-rna-benchmark-zenodo-link, seqc2-ascatngs-version, casp16-affinity-maximum-tau, ppi-embedding-ogbl-ppa-species-count.

## What was left out, and why

40 entries from the reviews and the content files were not admitted. Each is in
`kb/curation/source_leads_left_out.jsonl` with its reason; some entries group several small items. The groups are:

- Explained by a saved file (22). Examples: Sun et al.'s 80/20 split is merged to the paper's 60/40 in the
  preprocessing README; Chroma's README says the paper used t=0.0 and why the default is 0.5; the DEKOIS and POISK
  differences are disclosed in the same files; OncoVI's 80% against 81% is a rounding of 75 of 93; Hall and Coin's
  DOIs are concept against version records; LncRFM's blocks 6 and 12 are indices 5 and 11 in its code;
  release-against-paper differences that the developers state themselves (MIST, 3DMolMS, BPNet, BulkFormer,
  FrameDiff, E1).
- A record's own description against a source (3 entries, about 20 records). These are corrections to this store,
  already listed in the batch reviews, not questions for developers.
- Code and weights under different licences (2 entries). Different objects, so not a conflict.
- One side only (6): a missing file with no saved listing, a method concern with nothing to compare it with, or a
  figure the review names that could not be found in the saved text (LIT-PCBA totals in Shen et al., ChemBERTa's 512).
- Not checked in this pass (5 entries, about 40 small items): low-impact counts, names, spellings and two dead
  addresses. They remain on their pages and are unfinished work, not rejections.
- Outside the batch folders (2): Rewire's own Evo 2 cloud study, and the skipped folders that have no page.

## How this differs from kb/curation/leads.jsonl

`leads.jsonl` (table `lead`) holds differences between studies: two papers reporting different values for the same
model on the same setting. This register (table `source_lead`) holds differences inside one model's or one study's
own files. `python3 kb/curate.py` loads both. To list the strong ones:

```sh
sqlite3 -header -column kb/build/kb.sqlite "SELECT id, impact, where_to_raise FROM source_lead WHERE strength = 'strong' ORDER BY impact"
```

## State

Every lead is `open`. When one is raised, answered or withdrawn, change `state` and record what happened; the
`basis` field says who found it and how it was checked.
