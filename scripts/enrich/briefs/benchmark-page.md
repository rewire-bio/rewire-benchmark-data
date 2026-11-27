# Brief: write the benchmark page content for one benchmark

You are filling in the page for a biological benchmark on benchmarks.rewirebio.io. Today most of these
pages hold a one-line description. For each benchmark folder you are given, research the benchmark's own
primary sources, save them, and write `spec.json` in that folder. You do not touch any git repository,
run npm, or write to GitHub. You only fetch, save files in the benchmark folder, and write `spec.json`.
Do not start sub-agents.

A reader of the finished page should learn: what the benchmark measures and for whom, how its data and
splits were built, how a submission is scored, where the data, code and results are, on what terms, and
how to run it.

## Inputs

Each folder `NN-slug/` holds `input.json`:

- `record_id`, `name`, `description` and `attributes`: the record as it is in the database today. The
  attributes are earlier notes (a research summary, a scope note, links to run documentation). They tell
  you where to look. They are not sources: do not copy a statement from them unless a file you fetch says it.
- `existing_sources`: the source records already attached, with their addresses. You may cite one by its
  ID, but you cannot quote from it unless you fetch it again as a new source.
- `protocols` and `datasets`: the names of the tests and datasets in the store that belong to this
  benchmark, with `protocol_count` and `dataset_count` (the lists stop at 50). `results_in_store` counts the
  results recorded against it. Use these to see which tasks matter to the store; write about every task
  the sources describe, not only these.

Some records are not a released suite but one paper's evaluation (their names often end with the authors
and year), or a study Rewire ran. Write that page about the evaluation itself, from the paper or the study's
own saved files. Where there is no separate code, data or leaderboard, say so and leave those structured
addresses null.

A finished model page in the same format, to copy the shape from:
`data/omics/model-pages-20261126-batch6/specs/hyplm-flash.json` in rewire-bio/rewire-benchmark-data.
No benchmark page has been written in this format yet.

## What to fetch

Find the benchmark's official sources. In order of usefulness:

1. The benchmark paper, full text, where an open copy exists: the arXiv PDF
   (`https://arxiv.org/pdf/<id>`), the NCBI PMC full-text XML through E-utilities
   (`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=<PMC number without the PMC prefix>`),
   an open-access publisher PDF, or the proceedings PDF (PMLR, NeurIPS, OpenReview). Save the full text
   whenever one is open: the abstract alone rarely gives the splits, the metrics or the leakage controls.
   A PDF cannot be quoted directly. Keep the PDF, extract its text layer with `pdftotext -layout`, save
   the text beside it, and make the text file the source you quote (describe it as the text layer of the
   PDF at that address). An XML file can be quoted as it is.
2. The official code repository README at a pinned commit, and the files that hold the data download,
   the evaluation or scoring script's usage, and the licence. Use `gh api repos/OWNER/REPO/commits/BRANCH --jq .sha`
   for the commit, `gh api repos/OWNER/REPO --jq '{license:.license.spdx_id,default_branch}'` for the
   licence, and fetch each file from `https://raw.githubusercontent.com/OWNER/REPO/<sha>/<path>`.
3. The official leaderboard or results page, and the data host's page (Zenodo record JSON at
   `https://zenodo.org/api/records/<id>`, a Hugging Face dataset at
   `https://huggingface.co/api/datasets/ORG/NAME`, a figshare or project download page). These usually
   carry the data licence and the version.

Fetching rules:

- One request at a time. Wait 3 seconds between requests to the same host.
- Do not request biorxiv.org or medrxiv.org more than once every 15 seconds. On a 429 or error 1015,
  wait at least 60 seconds and retry once, then leave it and say so in `notes`.
- Never set a browser User-Agent. Never get round a paywall, a login, a gate or a robot check. If a
  page asks for any of these, stop requesting it.
- Use `gh api` for GitHub (plain unauthenticated calls are limited to 60 an hour). Use plain `curl -sL`
  for everything else. Use web search only to find the official addresses, never as a source of facts.
- Keep every fetched file under the folder's `artifacts/`, whatever its licence, with a plain name
  (`paper.pdf`, `paper.txt`, `paper-pmc.xml`, `readme.md`, `leaderboard.html`, `zenodo.json`, ...).
  `store_bytes` only decides which files may be published in the repository; every file is kept and
  hashed. Aim for 3 to 7 sources per benchmark.

## The one rule that matters

Every statement is written from the text you fetched, never from what you remember about the benchmark.
Each fact, section, strength, limitation, diagram, run step and structured entry carries `quotes`: one or
more passages copied verbatim from a saved source file, which support the statement. A checker confirms
each quote is in the file (whitespace is normalised, nothing else). If you cannot find a supporting
passage, do not make the statement: give the fact status `unreported` (the authors do not say),
`unextracted` (it may be in a source you could not read), `unavailable` (nothing is released) or
`inapplicable` (the label does not apply, for example Organisms for a benchmark of small molecules), and
say that in the value. Those four statuses need no quote. Do not turn a number in a source into a
different number.

Do not state anything no saved file shows. In particular, do not describe how other websites or
catalogues list the benchmark, how popular it is, or when its repository was last changed, unless a
saved file says so.

## spec.json

```json
{
  "record_id": "<from input.json>",
  "sources": [
    {"key": "paper", "name": "Text layer of the <Name> paper, arXiv 2101.00001v2", "description": "Text extracted with pdftotext -layout from the arXiv PDF. The PDF is kept beside it as artifacts/paper.pdf.",
     "file": "artifacts/paper.txt", "artifact_url": "https://arxiv.org/pdf/2101.00001v2",
     "url": "https://arxiv.org/abs/2101.00001v2", "version": "arXiv v2", "media_type": "text/plain",
     "sha256": "<sha256 of the saved file>", "retrieved_at": "2026-11-26T17:00:00Z",
     "licence": "CC BY 4.0", "store_bytes": true},
    {"key": "readme", "name": "OWNER/REPO README.md at commit abcdef12", "description": "Official repository file, pinned to a commit.",
     "file": "artifacts/readme.md", "artifact_url": "https://raw.githubusercontent.com/OWNER/REPO/<full sha>/README.md",
     "url": "https://github.com/OWNER/REPO", "version": "git commit <full sha>", "media_type": "text/markdown",
     "sha256": "...", "retrieved_at": "...", "licence": "MIT", "store_bytes": true}
  ],
  "profile": {
    "summary": "Two or three plain sentences: what the benchmark measures, on what data, and who would use it to choose or compare models.",
    "summary_source_ids": ["@paper"], "summary_source_locator": "Paper: Abstract",
    "summary_quotes": [{"source": "@paper", "text": "verbatim passage"}],
    "sections": [
      {"title": "What it measures", "body": "The biological question or capability each task tests, and why it matters.",
       "source_ids": ["@paper"], "source_locator": "Paper: Section 1", "quotes": [{"source": "@paper", "text": "..."}]},
      {"title": "How it is built", "body": "Where the data come from, how examples and labels were made, how the splits were drawn.",
       "source_ids": ["@paper"], "source_locator": "...", "quotes": [...]},
      {"title": "Evaluation methodology", "body": "What a submission provides, how it is scored, how scores are aggregated across tasks, what counts as a fair comparison.",
       "source_ids": ["@paper"], "source_locator": "...", "quotes": [...]},
      {"title": "How to run it", "body": "In prose: get the data, produce predictions, run the scoring code. Only when the sources give steps.",
       "source_ids": ["@readme"], "source_locator": "...", "quotes": [...]}
    ],
    "facts": [
      {"label": "Datasets", "value": "...", "status": "source_checked", "source_ids": ["@paper"], "source_locator": "...", "quotes": [...]}
    ],
    "strengths": [{"text": "...", "source_ids": [...], "source_locator": "...", "quotes": [...]}],
    "limitations": [{"text": "...", "source_ids": [...], "source_locator": "...", "quotes": [...]}],
    "diagram": {"title": "<Name> workflow", "steps": ["data", "split", "model predictions", "metric", "leaderboard"], "caption": "...", "source_ids": [...], "source_locator": "...", "quotes": [...]},
    "coverage": "reviewed",
    "gaps": ["What a reader would want that the sources read do not give."],
    "review": {"method": "automated_source_review", "date": "2026-11-26", "note": "Which files were read, at which commit, version or revision, on which date. No command was executed and no human review is claimed."}
  },
  "run_guide": {
    "summary": "One sentence: what the steps achieve.",
    "prerequisites": ["Software, data size, licence terms, each only as the sources state them."],
    "steps": [
      {"title": "Get the code", "shell": "git clone https://github.com/OWNER/REPO\ncd REPO\ngit checkout --detach <sha>", "explanation": "...", "source_ids": ["@readme"], "source_locator": "README.md: Installation", "quotes": [{"source": "@readme", "text": "git clone https://github.com/OWNER/REPO"}]}
    ],
    "outputs": ["What the last step prints or writes, as the sources describe it."],
    "limitations": ["These commands were read from the repository and have not been executed by Rewire.", "..."],
    "source_ids": ["@readme"]
  },
  "structured": [],
  "notes": "Anything the person applying this should know: another record this benchmark may duplicate, a doubt about which repository or version is official, a source that failed to fetch."
}
```

Rules for the fields:

- A source `key` is lower-case letters, digits and hyphens only (`paper`, `readme`, `zenodo`, `leaderboard`).
- A source `licence` is a short identifier only: `MIT`, `Apache-2.0`, `BSD-3-Clause`, `CC BY 4.0`, `CC BY-NC 4.0`,
  `CC BY-NC-ND 4.0`, `CC-BY-4.0`, `CC-BY-NC-4.0`, `CC0-1.0`. If the licence is anything else, or none is
  stated, leave `licence` out of the source and record the terms in the `structured` licence fields and,
  if they restrict use, in a limitation.
- `source_ids` hold `@key` for a source you fetched, or the ID of an existing source from `input.json`.
- `sections` must include "What it measures", "How it is built" and "Evaluation methodology", and "How to
  run it" when you write a run guide. Add a section per task or track when the tasks differ enough that one
  paragraph cannot describe them.
- `facts` must include these eleven labels, in this order:
  - Datasets: the datasets, with sizes as the source prints them.
  - Splits: how train, validation and test are drawn, per task when they differ.
  - Metrics: the metric for each task, and which direction is better.
  - Baselines: the methods the authors report as reference points.
  - Leakage controls: what keeps test examples out of training data (sequence identity cut-offs, time
    splits, held-out families), or that the sources describe none.
  - Uncertainty: replicates, seeds, confidence intervals or standard errors the benchmark asks for or
    reports, or that it reports none.
  - Entity type: what one example is (a variant, a sequence, a cell, a structure, a molecule pair).
  - Organisms: the species the data cover.
  - Assays: the experimental measurements behind the labels.
  - Allowed inputs: what a model may read (sequence only, structure, alignments, metadata).
  - Adaptation: zero-shot, linear probe, fine-tuning, or training from scratch, as the benchmark allows.
  Start each value with the direct answer, then add detail.
- `store_bytes`: true only when the source's licence clearly allows redistribution (MIT, Apache-2.0, BSD,
  CC BY, CC0). Otherwise false. Zenodo and Hugging Face API responses: true. A paper: false unless it is
  CC BY or CC0. A false value still keeps the file in `artifacts/`; it only stays out of the repository.
- `run_guide`: commands taken from the sources, runnable in order from an empty machine: get the code at
  the pinned commit, install, download the data, run the evaluation or scoring for one task. You may add a
  `git checkout --detach <sha>` line or wrap a Python example in a shell heredoc; say so in `explanation`.
  Invent nothing else: no flags, paths, task names or file names the sources do not give. If the sources give
  no usable instructions, set `"run_guide": null` and add `"no_run_guide_reason": "..."`.
- `coverage` is `reviewed` when you read the paper's full text and the repository or data page; otherwise
  `limited`, with the reason in `gaps` (for example, only the abstract was open).
- 2 to 4 strengths and 2 to 4 limitations. A limitation is something a user needs to know before relying on
  the benchmark (a random split with likely leakage, one organism only, a non-commercial data licence, no
  maintained leaderboard, a known label noise problem the authors state). Do not write a claim about the
  benchmark's quality as a strength unless you say whose claim it is.

## Structured facts

Add a top-level `"structured"` list, one entry per task or track (or one entry for the whole benchmark when
it has a single task). These will be loaded into a queryable table, so each value must be a plain number,
identifier or address, or null when the sources do not give it:

```json
"structured": [
  {"task": "name as the authors write it", "dataset": "dataset name as the authors write it",
   "size": 2500, "size_unit": "variants", "split": "30% sequence identity",
   "primary_metric": "Spearman", "metric_direction": "higher",
   "results_url": "https://...", "code_url": "https://github.com/...", "data_url": "https://zenodo.org/records/...",
   "data_licence": "CC-BY-4.0", "code_licence": "MIT", "released": "2023-06-01",
   "quotes": [{"source": "@paper", "text": "verbatim passage for the numbers and the split"}]}
]
```

`size` is an integer count of examples in the test set, or the whole dataset when the source gives only that
(say which in `size_unit`, for example `test variants`, `sequences`, `cells`, `assays`). `split` is a short
phrase from the source. `metric_direction` is `higher` or `lower`. Licences are SPDX identifiers where one
exists, otherwise a short name such as `custom-noncommercial`, or null when none is stated. `released` is a
date a source states, or null. Every entry needs at least one passage in `quotes`, and every non-null value
must be backed by one of them.

## Style

Plain English, short sentences, no marketing words ("powerful", "state-of-the-art", "seamless", "robust",
"comprehensive"). No em dashes or en dashes, no arrows: write ranges as "3 to 8" and "Sections 3 to 5".
British spelling. Write numbers as the source prints them. The summary is for a scientist who has not heard
of the benchmark.

## Check your work

After writing each `spec.json`, run:

    python3 -I <batch folder>/check_spec.py <benchmark folder>

Fix every line it prints until it prints `OK`. Then move to the next benchmark. If a benchmark cannot be
done (no official source can be found or fetched), write `spec.json` with only `record_id` and `notes`
explaining why, and move on.

## Numbers belong to the exact set they are quoted for

The first benchmark batch was reviewed at twice the error rate of model pages, and most faults were
a number attached to the wrong set. Before you write a size, a count or a split:

- A size in a `structured` entry is the size of that entry's own set. A whole-corpus size does not
  go on each of its panels, and the count from one pairwise comparison is not the benchmark's size.
  If no saved file gives the figure for that exact set, the field is null and the notes say what the
  file does give.
- A count must match the list or table it summarises. Count the rows.
- A split rule or metric stated for one task or one adaptation setting is written for that task or
  setting only.
- A licence, an address, a model wrapper or a metric goes on the page only if a saved file prints it.
- When you describe what a script does, read the script: say what it runs, not what its name or its
  README suggests.

## Report

When all your folders are done, reply with one line per benchmark: folder, OK or not, number of sources,
whether the paper's full text was read, whether a run guide was written, and any doubt worth a human look.
Nothing else.
