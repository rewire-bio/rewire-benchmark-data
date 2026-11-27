# Run guide trial 5, and a correction to ProtBert's licence sentence

Prepared by Claude agents. No human review is claimed.

Workflow run 45993455735 on 27 November 2026 ran the five guides corrected after
[trial 4](2026-11-27-run-guide-trial-4.md), on clean `ubuntu-latest` runners (Ubuntu 26.04.1,
Python 3.11, no GPU). No run failed on a missing package. Each guide now runs to its last step,
and each stops there.

## Results

| Record | Steps completed | Stopped at | Last error line | Fault |
| --- | --- | --- | --- | --- |
| `uc20260930-model-carp` | 1 to 3 | Step 4 | `RuntimeError: Parent directory examples/results/some_proteins_emb_carp_640M does not exist.` | Source |
| `uc20260930-model-mif` | 1 to 3 | Step 4 | `RuntimeError: Parent directory examples/results/some_proteins_mifst does not exist.` | Source |
| `uc20260930-model-mif-st` | 1 to 3 | Step 4 | Same as MIF | Source |
| `hycell-20261106-model-stack` | 1 and 2 | Step 3 | `FileNotFoundError: [Errno 2] No such file or directory: 'hvg_genes.pkl'` | Source gap (the reader's own data) |
| `uc20260930-model-msa-transformer` | 1 and 2 | Step 3 | `RuntimeError: Received unaligned sequences for input to MSA, all sequence lengths must be equal.` | Source |

CARP, MIF and MIF-ST. The README's bulk commands write to `examples/results/...`. The repository
at af69577 ships the example inputs (`examples/some_proteins.fasta`, `examples/gb1s.csv` and the
GB1 PDB file) but no `examples/results` folder. `scripts/extract.py` and
`scripts/extract_mif.py` build each output path as `out_dir + name` and pass it to `torch.save`
without creating the folder. I read both at the pinned commit as text; their hashes are in the
trial 4 review.

Stack. Steps 1 and 2 installed the package and downloaded Stack-Large. Step 3 needs an AnnData
file (`data.h5ad`) and a gene list (`hvg_genes.pkl`). The README names them only as
placeholders, and the model card does not mention them. The Hugging Face file list shows
`basecount_1000per_15000max.pkl` beside the checkpoint, but no saved source says it is the gene
list, so it is not used.

MSA Transformer. Step 3 downloaded the model and stopped at the check for equal lengths. The
alignment `examples/variant-prediction/data/BLAT_ECOLX_1_b0.5.a3m` ships with the repository at
2b36991 (archive SHA-256 28146f62..., file SHA-256 4510d322...). So the guide's earlier
limitation, that no source says where to download it, was wrong.

`predict.py` reads the first 400 sequences (the `--msa-samples` default) and deletes lower-case
letters, `.` and `*` as insertions. I read the file as text and applied that same rule; I did
not run the code. The 400 sequences come out at 262 (225 sequences), 263 (166), 261 (7), 259 (1)
and 260 (1) characters. The query itself has lower-case letters (`hpETLV...`, `...IKHw`). This is
the length mismatch the error reports. Whether the file or the reading rule is at fault is not
established. The `.cuda()` call in the MSA branch, already a limitation, comes after this point
and was not reached.

## Changes to the records

Six records changed in one `npm run records -- change` call. The before and after are in
`data/omics/run-guide-trials-20261127/record-changes-trial-5.jsonl`. No record has a twin.

- CARP, MIF and MIF-ST: step 4 now begins with `mkdir -p` for its output folder. The explanation
  says the line is added by Rewire and why. The limitation recording earlier runs now says steps
  1 to 3 completed.
- Stack: the limitation recording earlier runs now says steps 1 and 2 completed. It also says
  step 3 needs a data file and a gene list that neither source provides.
- MSA Transformer:
  - The limitation recording earlier runs now gives this result.
  - The limitation saying no source tells where to download the alignment is replaced. The
    alignment ships with the repository, and read with `predict.py`'s rule its first 400
    sequences have unequal lengths.
- ProtBert: see below.

Status stays `source_reviewed_not_executed` on every guide.

## ProtBert's licence sentence

`lit-protein-20261011-deepprotein-model-protbert`, `profile.limitations[0]`, said: "The weights
are not under an open-source software licence. The ProtTrans README puts them under the Academic
Free License v3.0 while the code is MIT, and the Hugging Face repository declares no licence at
all."

The first sentence is wrong. The Academic Free License v3.0 is an open-source licence approved by
the Open Source Initiative. The saved sources do not say so, but they do not support the
sentence either. Here is what each states:

- The ProtTrans README at 27c02f0, "License": "The ProtTrans pretrained models are released
  under the under terms of the [Academic Free License v3.0 License]".
- The ProtTrans `LICENSE`: "MIT License".
- The Hugging Face API response for Rostlab/prot_bert: `cardData` with no `license` key.

The limitation now reads: "The weights and the code are under different licences: the ProtTrans
README puts the pretrained models under the Academic Free License v3.0, the code is MIT, and the
Hugging Face repository declares no licence at all."

Every part of that is stated by the three sources the limitation already cites. The page's other
licence statements are left as they were, because they already said the same:

- the "Weights licence" fact;
- the licence section of the profile;
- the run guide's prerequisite;
- the checkpoints' `weights_licence: AFL-3.0`.

The same sentence was in the revision-1 batch's content file
(`data/omics/model-pages-20261127-revision1/specs/protbert.json`) and its prepared
`models.json`. Both are changed to match, so that applying the batch again does not restore it.
The earlier batch-5 content file is kept as it was. Revision 1 replaced it.

## Where the trials stop

Five rounds of corrections took ESM-1b to completion. They took CARP, MIF and MIF-ST to their
last step, which should now complete, and Stack and MSA Transformer to a step that needs data or
an input the sources do not provide.

Most rounds found one missing package. This loop stops here. The next step is the
`trial.py imports` check in the todo list, which would find undeclared imports before a run.

Rerun when convenient: `uc20260930-model-carp uc20260930-model-mif uc20260930-model-mif-st`.
