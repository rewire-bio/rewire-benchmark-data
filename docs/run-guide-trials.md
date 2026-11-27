# Run guide trials

A run guide (`attributes.run_guide` on a model, method, benchmark or protocol record) lists the
commands a reader would type to install and run something. Every guide was read from a README and
none has been run. A trial runs one guide, unchanged, on a fresh GitHub Actions runner and keeps a
receipt of what happened. Trials do not change records.

The code is `scripts/runs/trial.py` and `.github/workflows/run-guide-trial.yml`; the tests are in
`scripts/runs/tests` and run with `npm run test:python`.

## Starting a trial

Pick guides that look cheap to try on a CPU runner:

```sh
python3 scripts/runs/trial.py candidates --limit 25
```

The rules: no step mentions CUDA or a GPU, and no prerequisite does unless it calls the GPU
optional, recommended or unstated; at most 4 steps; a pip, conda, mamba or uv install; no sudo,
docker or other container runtime; no placeholder such as `<file>`, `/path/to` or "your data"; no
step that is only comments; no size over 3 GB named in the guide; and no checkpoint over 750M
parameters (about 3 GB of fp32 weights) or gated, taken from the `structured` checkpoint facts in
`data/omics/*/specs/*.json`. When the steps name no checkpoint, the largest in the family counts.

Then start up to 10 trials, one runner each:

```sh
gh workflow run run-guide-trial.yml -f record_ids="ID1 ID2" -f timeout_minutes=30
```

`timeout_minutes` is the time each guide gets, at most 90. Download the receipts with
`gh run download <run id>`; each is an artifact named `run-guide-receipt-<record id>`, kept 30 days.

`trial.py script <record id> --out run-guide.sh` writes the script a trial runs, for reading. Do
not run it on your own machine: its commands come from third-party repositories.

## How a guide is run

The script starts one bash session and sources each step into it in order, so a `cd`, an `export`
or an activated environment in one step holds in the next, as it would for a person at a terminal.
Each step's text is written to its own file first and sourced with standard input from `/dev/null`,
so a step cannot read the next one as input. The session runs with `set -e`: a step stops at its
first failing command, which is where a person would stop, and the session ends. The steps after it
are recorded as not run. A step that calls `exit` also ends the session and is recorded with its
exit code. Pipelines are judged by their last command, as in a normal shell.

Before the first step the session activates a fresh Python venv (so `pip install` works without
sudo), loads conda's shell functions if the runner has conda, and sets `CONDA_ALWAYS_YES`,
`PIP_NO_INPUT` and `DEBIAN_FRONTEND=noninteractive` so that prompts a person would answer with yes
do not hang the run. If the prerequisites name exactly one version as "Python 3.x", that Python is
installed first; otherwise the runner's own Python is used.

The session stops itself after `timeout_minutes`. The workflow step and job have longer limits as
a backstop, so a receipt is written even when the session has to be killed.

## What the receipt holds

`receipt.json`, with one log file per step beside it:

- the record id, kind and name, and the commit of this repository the trial ran from;
- `run_guide_sha256`: the SHA-256 of the guide's canonical JSON (keys sorted, no spaces), so a
  later change to the guide shows;
- the runner: OS, CPU count, memory, free disk, the session's Python and whether a GPU is present;
- start and finish times and the timeout;
- per step: title, shell text, status (`completed`, `failed`, `timed_out`, `not_run`,
  `ended_session`), exit code, seconds, whether it holds only comments, and the last 200 lines of
  its combined output;
- `result`: `completed` (every step exited 0), `failed_at_step_<n>` or `timed_out`;
- `likely_cause` when a step failed;
- `manual_steps`: steps holding only comments, which a completed run did not exercise;
- `outputs`: the guide's outputs are prose, so the receipt picks out the words that look like paths
  and gives each file found its size and SHA-256 (files over 200 MB get a size only), lists
  directories, and lists the names it did not find.

## Reading a failure

`likely_cause` is the first rule that matches the failing step's log tail, in this order:
`out_of_disk`, `out_of_memory` (also exit code 137 with no message), `gated_download`, `no_gpu`,
`python_version`, `dependency`, `network`, `needs_root`, `missing_file`, `other`. It is a guess;
read the log tail before acting on it.

Runners have no GPU. A guide that needs one fails with `no_gpu`. That is a real result: it says the
guide does not run on a CPU, not that the guide is wrong.

## Security rules

A guide runs code from a repository we do not control, so the workflow treats it as hostile:

- `permissions: {}` at the top and `contents: read` per job: the job token can do almost nothing.
- No secrets are referenced. Nothing in the workflow can leak one.
- `persist-credentials: false` on checkout: no token is left in the checkout's git config.
- The guide runs as a separate user, `trial`, with no sudo. The runner's own user has passwordless
  sudo, and with root a guide could read the runner's memory for the tokens later steps use and
  poison the caches that `data.yml` restores on main.
- That user gets an empty environment (`env -i`) with `HOME` set to a fresh directory: no
  `GITHUB_TOKEN` (also set to empty on the step), no runner variables, no git config. It cannot
  write the checkout or the files the runner reads `GITHUB_ENV` and `GITHUB_PATH` from, so it cannot
  change the code that builds the receipt or the steps that follow.
- The guide works in `/trial`, outside the checkout, with a hard time limit. Its output goes to log
  files only, never to the step's output, so it cannot issue workflow commands.
- After the run every process of that user is killed before the receipt is built.
- Nothing the guide makes is committed, cached or passed to another job. Only the receipt and log
  tails are kept, as an artifact.
- Record ids and the timeout are passed through environment variables and checked (at most 10 ids
  of `[a-z0-9._-]`, each a record with a run guide; at most 90 minutes) before they name a job or an
  artifact.

A failed guide does not fail the workflow. A job fails only when the harness broke and no receipt
could be written. The pipeline alert workflow does not watch this one.

## Not done yet

- The run guide schema has only `source_reviewed_not_executed`. No status exists for an executed
  guide, so a successful receipt cannot yet be recorded on the record.
- Receipts live only as workflow artifacts for 30 days. They are not stored in this repository.
- Guides that need a GPU are recorded as failing for that reason. There is no GPU runner.
- The workflow has not run yet. Assumptions to check on the first run: that the runner's
  `python3 -m venv` works for a second user, and whether the runner image has conda (`$CONDA`).
