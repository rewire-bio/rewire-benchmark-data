# Run guide trial 2, and the guide corrections that follow from trials 1 and 2

Prepared by Claude agents. No human review is claimed.

Workflow run 45977697777 on 27 November 2026 tried ten run guides with the harness fixed after
[trial 1](2026-11-27-run-guide-trial-1.md). Every trial ran on a clean `ubuntu-latest` runner:
Ubuntu 26.04.1, 4 CPUs, 16 GB memory, no GPU. Each runner had Miniforge (conda 26.9.4), and Python
3.11 unless the guide named another version. [run-guide-trials.md](../run-guide-trials.md)
describes the harness.

MutBERT completed. The other nine failed.

This review gives a verdict for each failure and records the changes made to eleven run guides.
A fault lies in one of three places:

- **guide**: we left out something the source has, or copied it wrongly;
- **source**: the developers' own commands fail on a clean machine today;
- **harness**: the trial environment caused it.

No guide's status changed. All stay `source_reviewed_not_executed`.

## Verdicts

The evidence column quotes the failing step's last error line.

| Record | Failed at | Evidence | Fault |
| --- | --- | --- | --- |
| `agront-2024-plant-genomic-benchmark` | Step 2, load one task | `RuntimeError: Dataset scripts are no longer supported, but found plant-genomic-benchmark.py` (datasets 5.2.0) | Source |
| `gfm-guides-20261014-gpnmsa-model-gpn-msa` | Step 3, score variants | `Invalid value for --window-size: unable to convert "WINDOW_SIZE" into int.` | Guide |
| `hycell-20261106-model-stack` | Step 2, download the model | `ModuleNotFoundError: No module named 'huggingface_hub'` | Guide (fixed) |
| `lit-genomics-20261011-dnalongbench-benchmark-dnalongbench` | Step 2, train and test | `FileNotFoundError: ... './data/enhancer_target_gene/config/CRISPRi_EPI_K562_hg19.config'` | Source gap, already stated |
| `lit-genomics-20261011-dnalongbench-model-akita` | Step 1, install | `ERROR: Invalid requirement: 'tensorflow=2.15'`, then `CondaEnvException: Pip failed` | Source |
| `torchcraft-20261115-model-iglm` | Step 2, infill | `AssertionError: Unrecognized token supplied in starting tokens` (transformers 5.24.1, Python 3.11) | Source, likely |
| `uc20260930-model-carp` | Step 2, load a checkpoint | `ModuleNotFoundError: No module named 'torch'` | Guide (fixed) |
| `uc20260930-model-mif` | Step 3, load MIF | `ModuleNotFoundError: No module named 'torch'` | Guide (fixed) |
| `vep-uc-20261014-model-lol-eve` | Step 2, score variants | `AttributeError: 'int' object has no attribute 'is_floating_point'` (transformers 5.24.1, Python 3.11) | Source, likely |

Plant Genomic Benchmark (PGB). The guide copies the dataset card's example at revision 78ec815
exactly. `pip install datasets` installed datasets 5.2.0, which refuses to run the loading script
the dataset depends on. The card names no datasets version, and no older release was tried.

GPN-MSA. Steps 1 and 2 completed. The package installed, and the published checkpoint loaded
(12 layers, hidden size 768). Step 3 is the CLI's `gpn msa vep` command with two placeholders,
`LOCAL_MSA_PATH` and `WINDOW_SIZE`, and an input file, `variants.parquet`, that no step makes. Its
explanation tells the reader to fill those in. The trial summary first showed only the border of
the error box; it now shows the message line. The guide is at fault only in that step 3 cannot run
as written, which its explanation and limitations already say: the documentation read gives no
window size. No change is made. The candidate rules missed this kind of placeholder and now catch
an option followed by an upper-case word.

Stack. The model card's download snippet imports `huggingface_hub`. `arc-stack` does not install
it, and neither the README nor the card does. Step 3 uses placeholder paths (`data.h5ad`,
`hvg_genes.pkl`), as its explanation says, so the guide will still stop there after the fix.

DNALONGBENCH. Step 1 completed. conda created the Python 3.9 environment the README names, even
though setup-python had no 3.9 and the harness fell back to 3.11 for the venv (the receipt records
`failed_used_default`). Step 2 stopped because no data had been downloaded. The README gives no
download command and no folder layout, which the guide's prerequisites and limitations already
say. No change is made.

Akita. Trial 1 predicted this failure, and trial 2 confirms it. conda installed the conda part of
`environment.yml` at 06ce5d3, then pip rejected the file's `tensorflow=2.15` entry. The basenji
README's own `conda env create -f environment.yml` fails on a clean machine today.

CARP and MIF. The sequence-models README says "Models require PyTorch." but gives no install
command, and `pip install sequence-models` (1.8.0) does not install torch. ESM-1b failed the same
way in trial 1 with fair-esm.

## What Python 3.11 establishes for IgLM and LOL-EVE

Both failed in trial 1 on Python 3.14 and again in trial 2 on Python 3.11. Each failed with the
same error at the same line. In both trials pip installed transformers 5.24.1, tokenizers 0.23.3
and torch 2.15.0.

What this establishes:

- The failure does not depend on the Python version.
- The developers' commands, as written, fail on a clean machine today.

What it does not establish:

- That transformers 5 is the cause. No run used an older transformers. The package versions were
  the same in both trials, so tokenizers 0.23.3 or torch 2.15.0 remain possible causes.
- That pinning `transformers<5` would fix it.

Testing that needs a trial of a modified guide, which the harness does not offer. So the guides
get a limitation that states what fails and with which versions. Their commands are not changed.

## Changes to the records

Eleven run guides changed in one `npm run records -- change` call. Every changed guide's
`review.date` is now 2026-11-27. The before and after of each guide are in
`data/omics/run-guide-trials-20261127/run-guide-changes.jsonl`.

No record has a twin: no other record carries the same steps or the same name.

### Commands we left out

Each change adds one package to the first step's install line. The step's explanation says the
package was added by Rewire and quotes what the source states. The cited sources are unchanged
and still hold the quoted text. I hash-checked them: the saved ESM README and freshly fetched
copies of the sequence-models README and the Stack card match their source records'
`artifact_sha256`.

| Record | Step 1 now | Source statement behind it | Tried |
| --- | --- | --- | --- |
| `uc20260930-model-esm-1b` | `pip install torch fair-esm` | ESM README, "Getting started with this repo": "As a prerequisite, you must have PyTorch installed to use this repository." | Trial 1 |
| `uc20260930-model-msa-transformer` | `pip install torch fair-esm` | Same README and passage | Not tried; same package, same omission |
| `uc20260930-model-carp` | `pip install torch sequence-models` | sequence-models README, "Loading pretrained models": "Models require PyTorch." | Trial 2 |
| `uc20260930-model-mif` | `pip install torch sequence-models` | Same | Trial 2 |
| `uc20260930-model-mif-st` | `pip install torch sequence-models` | Same | Not tried; same package, same omission |
| `hycell-20261106-model-stack` | `pip install arc-stack huggingface_hub` | Stack-Large model card, "Download Model": `from huggingface_hub import snapshot_download` | Trial 2 |

For CARP, MIF and MIF-ST, the step's locator now names "Loading pretrained models" as well as
"Installation". For Stack, the step now also cites the model card, which the record already
listed as a source.

In the five guides that were tried, the limitation "have not been executed by Rewire" was no
longer true. It now says that an earlier version ran on 27 November 2026 and failed for the
reason given, and that the commands as now written have not run. ESM-1b's prerequisite now says
step 1 installs PyTorch.

### Faults in the sources

The commands are unchanged. Each guide gets a limitation that states what fails on a clean
machine, with which versions, and cites trial 1 or this review. The "not executed" limitation now
says the commands ran and failed at the named step.

- `uc20260930-model-prosst` (trial 1): `requirements.txt` pins `ginnm==0.0.2`, which is not on
  PyPI. It also pins five `+pt21cu118` packages without naming a wheel index.
- `torchcraft-20261115-model-iglm`: the infill example fails with transformers 5.24.1 on Python
  3.11 and 3.14. `setup.cfg` sets no upper bound.
- `vep-uc-20261014-model-lol-eve`: model loading fails with transformers 5.24.1 on Python 3.11
  and 3.14. The requirements set no upper bound, and the config was saved with 4.35.0.
- `lit-genomics-20261011-dnalongbench-model-akita`: pip rejects `tensorflow=2.15` in
  `environment.yml`.
- `agront-2024-plant-genomic-benchmark`: datasets 5.2.0 does not run the dataset's loading script.

These limitations cite this review and trial 1 as their evidence. They do not cite a source record:
the receipts are workflow artifacts and are not stored here.

## Candidate reports to developers

These are not in the leads register. Each is now backed by a failed run on a clean machine.

1. ProSST (ai4protein/ProSST, 13bd564): `pip install -r requirements.txt` fails because
   `ginnm==0.0.2` is not on PyPI. The `+pt21cu118` pins need a wheel index the file does not name.
2. IgLM (Graylab/IgLM, de819b5): the README's infill example fails with "Unrecognized token supplied
   in starting tokens" under transformers 5.24.1, on Python 3.11 and 3.14. `setup.cfg` allows any
   transformers from 4.6.1. Ask which transformers release they support. The cause has not been
   confirmed.
3. LOL-EVE (Marks-lab/LOL-EVE, 397bbb8): the README's Hugging Face example fails while loading the
   model under transformers 5.24.1, on Python 3.11 and 3.14 (`'int' object has no attribute
   'is_floating_point'` in `get_state_dict_dtype`). `requirements.txt` allows any transformers from
   4.35.0.
4. basenji (calico/basenji, 06ce5d3): `environment.yml` lists `tensorflow=2.15` under `pip:`.
   pip rejects it, so `conda env create -f environment.yml` fails. The fix is `tensorflow==2.15`.
5. Plant Genomic Benchmark (InstaDeepAI/plant-genomic-benchmark, 78ec815): the card's
   `load_dataset` example fails under datasets 5.2.0, which no longer runs loading scripts.

## Rerun

These test the corrected guides:

- `uc20260930-model-esm-1b`
- `uc20260930-model-carp`
- `uc20260930-model-mif`
- `uc20260930-model-mif-st`
- `hycell-20261106-model-stack` (expected to stop at its placeholder step 3)

So far there have been 18 trials (8 in trial 1, 10 in trial 2) of 14 distinct guides.
DNALONGBENCH, Akita, IgLM and LOL-EVE were tried in both. Three guides completed: SAFFRON,
GPN-Promoter and MutBERT.

## Rerun results

Workflow run 45982556374 reran four of the corrected guides on the same kind of runner, with
Python 3.11.18. MIF-ST was not rerun.

| Record | Result | Last error line | Fault | Change |
| --- | --- | --- | --- | --- |
| `uc20260930-model-esm-1b` | Completed | | | Limitation updated |
| `uc20260930-model-carp` | Failed at step 2 | `ModuleNotFoundError: No module named 'numpy'` | Source | Install line extended |
| `uc20260930-model-mif` | Failed at step 3 | `ModuleNotFoundError: No module named 'numpy'` | Source | Install line extended |
| `hycell-20261106-model-stack` | Failed at step 3 | `FileNotFoundError: Checkpoint not found: checkpoints/pretrained.ckpt` | Guide | Checkpoint path corrected |

CARP and MIF. `pip install torch sequence-models` installed sequence-models 1.8.0 and torch
2.15.0 and no numpy. `sequence_models/constants.py` line 4 imports numpy. The package declares no
dependencies. I fetched `setup.py` and `requirements.txt` at commit af69577 to check this; they are
not saved as sources. `setup.py` (SHA-256 71c1f8d0...) has no `install_requires`, and
`requirements.txt` is empty (SHA-256 e3b0c442..., the hash of an empty file). The saved README
says: "If you installed into a clean conda environment, you may also need to install pandas,
scipy, and wget."

Step 1 of CARP, MIF and MIF-ST now reads `pip install torch sequence-models pandas scipy wget`.
The step's explanation says the three packages are added by Rewire on the README's advice and
that numpy comes with pandas and scipy. Each guide also gets a limitation recording the
undeclared dependency.

Stack. Step 2 downloads the released model into `Stack-Large`, as the model card's snippet does.
Step 3 kept the README's `--checkpoint "./checkpoints/pretrained.ckpt"`. That path is the folder
the README's training command saves to, not a released file. The step's own explanation already
said to replace it. The saved Hugging Face file list for Stack-Large (revision 6e1f352) shows the
checkpoint is `bc_large.ckpt`. Step 3 now uses `--checkpoint "Stack-Large/bc_large.ckpt"` and
cites the model card and the file list. Its `data.h5ad` and `hvg_genes.pkl` are still
placeholders, so the step cannot complete without the reader's own data.

ESM-1b. Its limitation said that the commands as now written had not been executed. It now says
they ran to completion on 27 November 2026. Its status stays `source_reviewed_not_executed`,
because the schema has no status for an executed guide.

The five records (CARP, MIF, MIF-ST, Stack and ESM-1b) changed in one `npm run records -- change`
call.
The before and after of each guide are in
`data/omics/run-guide-trials-20261127/run-guide-changes-rerun.jsonl`.

Rerun next: `uc20260930-model-carp`, `uc20260930-model-mif`, `uc20260930-model-mif-st` and
`hycell-20261106-model-stack`.

So far there have been 18 trials and 4 reruns. Four guides completed: SAFFRON, GPN-Promoter,
MutBERT and ESM-1b.

## Candidate reports to developers (drafts)

These are drafts for a person to read and send. They are not in the leads register. All runs
were on GitHub Actions `ubuntu-latest` (Ubuntu 26.04.1 LTS, 4 CPUs, no GPU), each in a fresh Python
virtual environment, on 27 November 2026.

**ProSST (ai4protein/ProSST).** At commit 13bd564 we ran the README's install commands
(`git clone`, `cd ProSST`, `pip install -r requirements.txt`) with Python 3.14.4. pip stopped
with: `ERROR: Could not find a version that satisfies the requirement ginnm==0.0.2 (from versions:
none)`. The file also pins five packages with `+pt21cu118` versions, for example
`torch-scatter==2.1.2+pt21cu118`. Is `ginnm` published on another index, and which index should
pip use for the `+pt21cu118` packages?

**basenji, used by Akita (calico/basenji).** At commit 06ce5d3 we ran `conda env create -f
environment.yml` with conda 26.9.4 (Miniforge). The conda packages installed, and then the pip
stage stopped with: `ERROR: Invalid requirement: 'tensorflow=2.15': Expected end or semicolon
(after name and no valid version specifier)` and `Hint: = is not a valid operator. Did you mean ==
?`, followed by `CondaEnvException: Pip failed`. Is `tensorflow==2.15` the intended pin?

**Plant Genomic Benchmark (InstaDeepAI/plant-genomic-benchmark).** We ran `pip install datasets`,
which installed datasets 5.2.0, and then the dataset card's example (revision 78ec815) with
`task_name='terminator_strength.protoplast'`, on Python 3.11.18. `load_dataset` stopped with:
`RuntimeError: Dataset scripts are no longer supported, but found plant-genomic-benchmark.py`.
Which version of datasets do you support for this dataset, or is there a way to load it without
the script?

**IgLM (Graylab/IgLM).** We ran `pip install iglm`, which installed iglm 0.1.0, transformers 5.24.1,
tokenizers 0.23.3 and torch 2.15.0, and then the README's "Re-design spans" package example. On
Python 3.11.18 and on Python 3.14.4 it stopped in `IgLM.infill` with: `AssertionError: Unrecognized
token supplied in starting tokens`. We have not tried other versions of transformers. Which
versions of transformers and tokenizers do you support?

**LOL-EVE (Marks-lab/LOL-EVE on Hugging Face).** We installed the packages in the model's
`requirements.txt` (revision 397bbb8), which gave transformers 5.24.1 and torch 2.15.0, and ran
the README's "Using Hugging Face Model" example. On Python 3.11.18 and on Python 3.14.4,
`AutoModelForCausalLM.from_pretrained('Marks-lab/LOL-EVE', trust_remote_code=True)` stopped with:
`AttributeError: 'int' object has no attribute 'is_floating_point'`, raised in transformers'
`get_state_dict_dtype`. We have not tried other versions of transformers. Which version of
transformers do you support?

**sequence-models, used by CARP and MIF (microsoft/protein-sequence-models).** We ran `pip install
torch sequence-models`, which installed sequence-models 1.8.0 and torch 2.15.0 on Python 3.11.18,
and then `from sequence_models.pretrained import load_model_and_alphabet`. It stopped with:
`ModuleNotFoundError: No module named 'numpy'`, raised at `sequence_models/constants.py` line 4.
At commit af69577, `setup.py` lists no `install_requires` and `requirements.txt` is empty. Would
you accept a change that declares the package's dependencies?
