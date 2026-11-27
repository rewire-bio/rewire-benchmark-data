# Run guide trial 4: CARP, MIF, MIF-ST and MSA Transformer

Prepared by Claude agents. No human review is claimed.

Workflow run 45985445745 on 27 November 2026 ran four guides corrected after
[trial 2](2026-11-27-run-guide-trial-2.md). Each ran on a clean `ubuntu-latest` runner (Ubuntu
26.04.1, Python 3.11, no GPU). Each got further than in its last run, and each failed. Three of
the failures were one missing package. So this round lists every third-party import of the code
each guide runs, and makes the install line cover them all at once.

## Results

| Record | Steps passed | Failed at | Last error line | Fault |
| --- | --- | --- | --- | --- |
| `uc20260930-model-carp` | 1 | Step 2 | `AttributeError: 'dict' object has no attribute 'shape'` | Guide |
| `uc20260930-model-mif` | 1 to 3 | Step 4 | `ModuleNotFoundError: No module named 'tqdm'` | Source |
| `uc20260930-model-mif-st` | 1 to 3 | Step 4 | `ModuleNotFoundError: No module named 'tqdm'` | Source |
| `uc20260930-model-msa-transformer` | 1 and 2 | Step 3 | `ModuleNotFoundError: No module named 'pandas'` | Source |

CARP. The model downloaded and ran; the failure is in the last line of step 2,
`print(rep.shape)`. That line was added by Rewire; the README's snippet ends at
`rep = model(x)  # (n, max_len, d_model)`. The README's comment describes a tensor, but the
model's `forward` in `sequence_models/pretrained.py` (the saved source, SHA-256 159ede46...)
returns a dictionary and puts each requested layer's tensor under `result['representations']`.
Our print was wrong, and the README's comment does not match the code.

MIF and MIF-ST. The structure-based snippet in step 3 now runs. Step 4 runs
`scripts/extract_mif.py`, which imports tqdm, and nothing installs it.

MSA Transformer. Step 3 runs `examples/variant-prediction/predict.py`, which imports pandas, and
neither the README nor fair-esm installs it.

## Imports of the code each guide runs

I fetched the two repositories at the pinned commits as archives and read them as text; nothing
was imported or run. Their files match the saved sources where saved sources exist:

- `microsoft/protein-sequence-models` at af69577: archive SHA-256 573e16cb...
  - The README matches the saved source (8e277de5...).
  - `pretrained.py` matches the saved source (159ede46...).
  - `scripts/extract.py` (7d63ce0d...), `scripts/extract_mif.py` (7545eb2a...) and `setup.py`
    (71c1f8d0...) are not saved sources.
- `facebookresearch/esm` at 2b36991: archive SHA-256 28146f62...
  - The README matches the saved source (8b273c21...).
  - `examples/variant-prediction/predict.py` matches the saved source (8efe87c6...).

A static scan read each file's imports with Python's `ast` module and followed imports of the
repository's own package from the code each guide runs. Its findings:

| Guide | Code it runs | Third-party imports |
| --- | --- | --- |
| CARP | step 2 snippet, `scripts/extract.py`, the `sequence_models` modules they load | torch, numpy, pandas, scipy, tqdm |
| MIF, MIF-ST | step 3 snippet, `scripts/extract_mif.py`, the `sequence_models` modules they load | torch, numpy, pandas, scipy, tqdm |
| MSA Transformer | `predict.py` and `esm` | torch, numpy, pandas, tqdm, Bio (biopython) |

Some imports sit inside functions that these steps do not reach, so they are left out:

- In `sequence_models/trRosetta_utils.py`, `wget` and `tensorflow` are imported only inside the
  function that downloads and converts trRosetta weights.
- In `esm`, `apex`, `torchvision`, `openfold`, `biotite`, `torch_geometric` and `torch_scatter`
  are imported only inside functions or in the ESMFold and inverse-folding modules.

ESM-1b completed with fair-esm and torch alone, which shows that importing `esm` does not need
them.

## Changes to the records

Four run guides changed in one `npm run records -- change` call. The before and after of each
are in `data/omics/run-guide-trials-20261127/run-guide-changes-trial-4.jsonl`. No record has a
twin.

CARP, MIF and MIF-ST:

- Step 1 is now `pip install torch sequence-models numpy pandas scipy tqdm wget`.
- The explanation quotes both README passages, "Models require PyTorch." and "you may also need
  to install pandas, scipy, and wget".
- It says that torch, numpy, pandas, scipy and tqdm are added by Rewire from the imports above,
  because the package declares no dependencies. wget is kept because the README suggests it.

CARP only:

- Step 2's added print is now
  `print({layer: tuple(t.shape) for layer, t in rep['representations'].items()})`.
- The step now cites `pretrained.py`, a source the record already lists, for the dictionary the
  model returns.

MSA Transformer:

- Step 1 is now `pip install torch fair-esm numpy pandas tqdm biopython`.
- The explanation says which packages are the README's and which Rewire added from
  `predict.py`'s imports.
- The step now cites the saved `predict.py`.

All four guides: the limitation recording earlier runs now gives this trial's result. Status
stays `source_reviewed_not_executed`.

## What to expect next

MSA Transformer's own limitations already say two things:

- The example's alignment file, `./data/BLAT_ECOLX_1_b0.5.a3m`, has no download in the files read.
- The MSA Transformer branch of `predict.py` calls `.cuda()`.

Once its imports are satisfied, step 3 is expected to stop at one of these on a CPU runner. That
would be a GPU or data limit, not a missing package.

## Candidate reports to developers

One new observation, to add to the sequence-models draft in the trial 2 review:

- The README says `rep = model(x)  # (n, max_len, d_model)`, but the `forward` method in
  `sequence_models/pretrained.py` at af69577 returns a dictionary with the tensors under
  `'representations'`.
- `scripts/extract.py` and `scripts/extract_mif.py` import tqdm, which the package does not
  declare.

## Rerun

`uc20260930-model-carp uc20260930-model-mif uc20260930-model-mif-st uc20260930-model-msa-transformer hycell-20261106-model-stack`

Stack's checkpoint path was corrected after trial 3 and has not run since.
