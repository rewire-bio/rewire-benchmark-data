# Run guide trial 1: five failures

Workflow run 45974679008 on 27 November 2026 tried eight run guides on clean `ubuntu-latest`
runners (Ubuntu 26.04.1, 4 CPUs, 16 GB memory, no GPU), as described in
[run-guide-trials.md](../run-guide-trials.md). SAFFRON and GPN-Promoter completed. DNALONGBENCH
produced no receipt because the harness broke. This review covers the other five, which failed.

For each one it reads the receipt's log tail, the record's run guide and the saved sources, and
says where the fault lies:

- **guide**: we left out a step the source has, or copied it wrongly;
- **source**: the developers' own commands fail on a clean machine today;
- **harness**: the trial environment caused the failure.

No record was changed. The guide changes below are proposals.

All five failed trials ran on Python 3.14.4, the runner's default, because the guides name no
Python version. The harness now uses Python 3.11 when a guide names none. The installs
picked the newest packages: torch 2.15.0, transformers 5.24.1, tokenizers 0.23.3, numpy 2.5.5.

## Verdicts

| Record | Failed at | Fault | Proposed guide change |
| --- | --- | --- | --- |
| Akita (`lit-genomics-20261011-dnalongbench-model-akita`) | Step 1: `conda: command not found` | Harness | None yet. Run it again now that the runner has conda |
| ProSST (`uc20260930-model-prosst`) | Step 1: no `ginnm==0.0.2` on PyPI | Source | Add a limitation; no command the sources give works |
| ESM-1b (`uc20260930-model-esm-1b`) | Step 2: `No module named 'torch'` | Guide | Install torch in step 1 |
| IgLM (`torchcraft-20261115-model-iglm`) | Step 2: `AssertionError: Unrecognized token supplied in starting tokens` | Source, likely | Bound transformers below 5 once a second trial confirms it |
| LOL-EVE (`vep-uc-20261014-model-lol-eve`) | Step 2: `AttributeError: 'int' object has no attribute 'is_floating_point'` | Source, likely | Bound transformers below 5 once a second trial confirms it |

## Akita

The receipt: step 1 cloned basenji and checked out commit 06ce5d3, then stopped with exit code 127
at `conda env create -f environment.yml`, because the runner had no conda. Steps 2 and 3 did not
run.

Fault: harness. The guide's prerequisites do not say conda, but its step 1 uses it, as the basenji
README's "Installation" section does. The runner now installs Miniforge.

The saved `environment.yml` (pinned to 06ce5d3) suggests the next run will hit a source fault. Its
`pip:` list has `tensorflow=2.15`, and pip accepts only `==` there, so `conda env create` is likely
to fail when it reaches pip. This has not been observed yet.

Proposed change: none until a trial with conda has run. If the `tensorflow=2.15` line fails as
expected, add a limitation that quotes it.

## ProSST

The receipt: step 1 cloned the repository at 13bd564 and ran `pip install -r requirements.txt`.
It stopped with `ERROR: Could not find a version that satisfies the requirement ginnm==0.0.2 (from
versions: none)`.

Fault: source. The guide copies the README's "1 Install" commands exactly. The `requirements.txt`
at that commit pins `ginnm==0.0.2`, and PyPI has no project of that name: on 27 November 2026,
`https://pypi.org/pypi/ginnm/json` returned 404. The same file pins five packages with local CUDA
versions (`pyg-lib==0.4.0+pt21cu118`, `torch-scatter==2.1.2+pt21cu118` and three others) and names
no wheel index. pip cannot find those on PyPI either, so the install would fail on them next. It
also pins `torch==2.1.1`, which has no wheels for Python newer than 3.11.

Proposed change: add a limitation saying that `pip install -r requirements.txt` at 13bd564 fails on
a clean machine because `ginnm==0.0.2` is not on PyPI, and that the `+pt21cu118` pins need the PyG
wheel index. The saved sources give no working install, so no command change is proposed.

## ESM-1b

The receipt: `pip install fair-esm` installed fair-esm 2.0.0 and nothing else. Step 2 then
stopped at `import torch` with `ModuleNotFoundError`.

Fault: guide. The README ("Getting started with this repo") says: "As a prerequisite, you must have
PyTorch installed to use this repository." The guide recorded that as a prerequisite but gives no
command for it, so the guide does not run from a clean machine. The README is not wrong: it states
the requirement.

Proposed change: make step 1 `pip install torch fair-esm`, citing the same README section for the
torch prerequisite. One more thing to note in the guide: step 2 downloads the ESM-1b checkpoint
from Meta's servers on first use, and the saved sources do not give its file size.

## IgLM

The receipt: `pip install iglm` installed iglm 0.1.0 with transformers 5.24.1 and tokenizers
0.23.3. Step 2, the README's "Re-design spans" example, loaded the bundled model and then failed
the package's own check in `IgLM.infill`:
`AssertionError: Unrecognized token supplied in starting tokens`.

Fault: source, likely. The guide copies the README's package-usage example exactly; it only adds
a `print`. `setup.cfg` at de819b5 declares `transformers>=4.6.1` with no upper bound. `IgLM.py`
builds its tokenizer with `transformers.BertTokenizerFast(vocab_file=...)`, and under transformers
5.24.1 that tokenizer maps the `[HEAVY]` or `[HUMAN]` token to unknown. The cause is most likely
the transformers 5 tokenizer changes, but the run was also on Python 3.14, so that is not yet
separated out.

Proposed change: after a second trial on Python 3.11 confirms it, change step 1 to
`pip install iglm "transformers<5"` and add a limitation naming the failing version. The saved
sources give only the lower bound. The upper bound would come from the receipts.

## LOL-EVE

The receipt: step 1 installed torch 2.15.0 and transformers 5.24.1 under the guide's lower bounds.
Step 2, the README's "Using Hugging Face Model" example, failed inside
`AutoModelForCausalLM.from_pretrained('Marks-lab/LOL-EVE', trust_remote_code=True)`.
transformers' `get_state_dict_dtype` met an `int` in the checkpoint's state dict.

Fault: source, likely. The guide copies the README example and the Hugging Face `requirements.txt`
(at 397bbb8). That file has `transformers>=4.35.0` with no upper bound, and the saved
`config.json` records `"transformers_version": "4.35.0"`. The traceback suggests that transformers
5 reads the default dtype from the state dict, and this checkpoint holds a non-tensor value. In
transformers 4 that code runs only when `torch_dtype="auto"` is asked for. This is a reading of the
traceback and has not been tested.

Proposed change: after a second trial confirms it, change step 1 to
`"transformers>=4.35.0,<5"`, citing the saved `config.json` for the version the model was saved
with. Also pin the model revision in step 2 (`revision="397bbb87341c7afa569dd3139217fdbd10480d36"`,
the commit of the saved files), so the remote code that runs is the code that was reviewed.

## Candidate reports to developers

These are not in the leads register. Each needs a confirming trial or a person's reading before
anyone writes to the developers.

1. ProSST (ai4protein/ProSST): `requirements.txt` at 13bd564 cannot be installed with pip from
   PyPI. `ginnm==0.0.2` is not on PyPI, and the `+pt21cu118` pins need the PyG wheel index, which
   the file does not name. Observed in trial 1; ready to report.
2. IgLM (Graylab/IgLM): `setup.cfg` allows any transformers from 4.6.1. With transformers 5.24.1
   the README's infill example fails with "Unrecognized token supplied in starting tokens".
   Report after a Python 3.11 trial reproduces it.
3. LOL-EVE (Marks-lab/LOL-EVE on Hugging Face): `requirements.txt` allows any transformers from
   4.35.0. With transformers 5.24.1 the README's Hugging Face example fails while loading the
   model. Report after a Python 3.11 trial reproduces it.
4. basenji (calico/basenji): `environment.yml` at 06ce5d3 lists `tensorflow=2.15` under `pip:`,
   which pip rejects. Not observed yet. Report only if the next Akita trial fails there.
