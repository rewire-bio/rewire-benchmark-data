# Brief: write the model page content for one model

You are filling in the page for a biological AI model on benchmarks.rewirebio.io. Today these pages
are nearly empty. For each model folder you are given, research the model's own primary sources,
save them, and write `spec.json` in that folder. You do not touch any git repository, run npm,
or write to GitHub. You only fetch, save files in the model folder, and write `spec.json`.
Do not start sub-agents.

A reader of the finished page should learn: what the model is for, how it works, which sizes and
versions exist, its licence and where to get it, and how to run it.

## Inputs

Each folder `NN-slug/` holds `input.json`: the record ID, name, the one-line description now in the
database, and the sources already attached to the record. Those existing sources are usually a
benchmark paper that evaluated the model, not the model's own documentation. You may cite an
existing source by its ID, but you cannot quote from it unless you fetch it as a new source.

Two finished examples, as merged pull requests in rewire-bio/rewire-benchmark-data: 398 (LIMBER)
and 399 (GPN-MSA). Read the build script of 399 for the level of detail and the tone:
`gh api repos/rewire-bio/rewire-benchmark-data/contents/data/omics/model-pages-20261126-gpn-msa/build.py --jq .content | base64 -d`

A finished spec in this exact format, to copy the shape from: `data/omics/model-pages-20261126-batch1/specs/caduceus.json`.

## What to fetch

Find the model's official sources. In order of usefulness:
1. The official code repository README, at a pinned commit. Use `gh api repos/OWNER/REPO/commits/BRANCH --jq .sha`
   for the commit, `gh api repos/OWNER/REPO --jq '{license:.license.spdx_id,pushed_at,default_branch}'` for the licence,
   and fetch the file from `https://raw.githubusercontent.com/OWNER/REPO/<sha>/README.md`. Also fetch any docs page
   that holds the usage instructions.
2. The Hugging Face model card and `config.json` at a pinned revision:
   `https://huggingface.co/api/models/ORG/NAME?expand[]=safetensors&expand[]=sha&expand[]=cardData&expand[]=gated`
   gives the revision, licence field, gating and, when present, the parameter count. Save that JSON response as a
   source too. Card: `https://huggingface.co/ORG/NAME/raw/<revision>/README.md`.
3. The paper, only as an open text you can fetch plainly: an arXiv abstract page
   (`https://arxiv.org/abs/<id>`), a Europe PMC full-text XML
   (`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC<id>/fullTextXML`), or a bioRxiv page. bioRxiv rate-limits:
   on a 429 or error 1015, wait and retry once, then leave it. Never set a browser User-Agent and never get round
   a paywall. If no open text is fetchable, cite the README and say in `gaps` that the paper was not read.

Use `gh api` for GitHub (plain unauthenticated calls are limited to 60 an hour). Use plain `curl -sL` for
raw.githubusercontent.com, huggingface.co and paper pages. Use web search only to locate the official repository
or model card, never as a source of facts.

Save every fetched file under the model folder's `artifacts/` with a plain name (`readme.md`, `hf-card.md`,
`hf-config.json`, `hf-api.json`, `paper-abstract.html`, ...). Aim for 3 to 6 sources per model.

Some models are a family (several sizes or checkpoints). Write about the family and list the checkpoints.
Some have no public weights or code. Then say so plainly, with status `unavailable`, and give no run guide.

## The one rule that matters

Every statement is written from the text you fetched, never from what you remember about the model.
Each fact, section, strength, limitation, diagram and run step carries `quotes`: one or more passages copied
verbatim from a saved source file, which support the statement. A checker confirms each quote is in the file
(whitespace is normalised, nothing else). If you cannot find a supporting passage, do not make the statement:
give the fact status `unreported` (the developers do not say), `unextracted` (it may be in a source you could
not read) or `unavailable` (nothing is released), and say that in the value. Those three statuses need no quote.
Do not turn a number in a source into a different number. Do not guess hardware needs.

## spec.json

```json
{
  "record_id": "<from input.json>",
  "sources": [
    {"key": "readme", "name": "OWNER/REPO README.md at commit abcdef12", "description": "Official repository file, pinned to a commit.",
     "file": "artifacts/readme.md", "artifact_url": "https://raw.githubusercontent.com/OWNER/REPO/<full sha>/README.md",
     "url": "https://github.com/OWNER/REPO", "version": "git commit <full sha>", "media_type": "text/markdown",
     "sha256": "<sha256 of the saved file>", "retrieved_at": "2026-11-26T17:00:00Z",
     "licence": "MIT", "store_bytes": true}
  ],
  "profile": {
    "summary": "Two or three plain sentences: the problem, the input, the output. A newcomer must understand it.",
    "summary_source_ids": ["@readme"], "summary_source_locator": "README.md: Overview",
    "summary_quotes": [{"source": "@readme", "text": "verbatim passage"}],
    "sections": [
      {"title": "How it works", "body": "One paragraph on the architecture and the training objective.",
       "source_ids": ["@readme"], "source_locator": "README.md: Model", "quotes": [{"source": "@readme", "text": "..."}]},
      {"title": "Versions and reproducibility", "body": "Which checkpoints exist, how they differ, what a result must name.",
       "source_ids": ["@hf-api"], "source_locator": "...", "quotes": [...]}
    ],
    "facts": [
      {"label": "Model type", "value": "...", "status": "source_checked", "source_ids": ["@readme"], "source_locator": "...", "quotes": [...]}
    ],
    "strengths": [{"text": "...", "source_ids": [...], "source_locator": "...", "quotes": [...]}],
    "limitations": [{"text": "...", "source_ids": [...], "source_locator": "...", "quotes": [...]}],
    "diagram": {"title": "<Name> workflow", "steps": ["input", "...", "output"], "caption": "...", "source_ids": [...], "source_locator": "...", "quotes": [...]},
    "coverage": "reviewed",
    "gaps": ["What a reader would want that the sources read do not give."],
    "review": {"method": "automated_source_review", "date": "2026-11-26", "note": "Which files were read, at which commit or revision, on which date. No command was executed and no human review is claimed."}
  },
  "run_guide": {
    "summary": "One sentence: what the steps achieve.",
    "prerequisites": ["Python version, GPU need, data needed, licence terms, each only as the sources state them."],
    "steps": [
      {"title": "Install", "shell": "pip install ...", "explanation": "...", "source_ids": ["@readme"], "source_locator": "README.md: Installation", "quotes": [{"source": "@readme", "text": "pip install ..."}]}
    ],
    "outputs": ["What the last step prints or writes, as the sources describe it."],
    "limitations": ["These commands were read from the repository and have not been executed by Rewire.", "..."],
    "source_ids": ["@readme"]
  },
  "notes": "Anything the person applying this should know: a second record this model may duplicate, a doubt about which repository is official, a source that failed to fetch."
}
```

Rules for the fields:

- A source `key` is lower-case letters, digits and hyphens only (`readme`, `hf-card`, `hf-api-v2`).
- A source `licence` is a short identifier only: `MIT`, `Apache-2.0`, `BSD-3-Clause`, `CC BY 4.0`, `CC BY-NC 4.0`,
  `CC BY-NC-ND 4.0`, `CC-BY-4.0`, `CC-BY-NC-4.0`, `CC0-1.0`. If the licence is anything else, or none is stated,
  leave `licence` out of the source and describe the terms in the Weights licence or Code licence fact instead.

- `source_ids` hold `@key` for a source you fetched, or the ID of an existing source from `input.json`.
- `facts` must include these twelve labels, in this order: Model type, Architecture, Inputs, Outputs, Parameters,
  Training data, Known versions, Training cutoff, Context limits, Weights licence, Code licence, Access.
  Keep code licence and weights licence apart. A paper's own licence (CC BY) is not a code or weights licence.
  Give parameter counts per checkpoint. Put URLs for code and weights in Access.
  The first words of Parameters, Context limits, Weights licence and Code licence are shown alone in a small
  tile, cut at about 60 characters, so start each value with the figure or the licence name itself
  ("7.7M (Caduceus-PS and Caduceus-Ph)...", "131,072 bases...", "Apache-2.0, as declared..."), then add detail.
- `store_bytes`: true only when the source's licence clearly allows redistribution (MIT, Apache-2.0, BSD,
  CC BY, CC0, or a model card under such a licence). Otherwise false: the file is hashed and not committed.
  Hugging Face API responses and config files: true. Paper pages: false unless the paper is CC BY.
- `run_guide`: commands taken from the sources, runnable in order from an empty machine: get the code at the
  pinned commit, install, load or download the weights, run one minimal inference. You may wrap a Python example
  in a shell heredoc and add a `git checkout --detach <sha>` line; say so in `explanation`. Invent nothing else:
  no flags, paths or model names the sources do not give. If the sources give no usable instructions, set
  `"run_guide": null` and add `"no_run_guide_reason": "..."`.
- `coverage` is `reviewed` when you read the README and at least one of the model card or the paper;
  otherwise `limited`, with the reason in `gaps`.
- 2 to 4 strengths and 2 to 4 limitations. A limitation is something a user needs to know before choosing the
  model (context length, licence, needs an alignment, no weights, GPU only, deprecated by its authors).
  Do not write benchmark claims as strengths unless you say whose claim it is.

## Style

Plain English, short sentences, no marketing words ("powerful", "state-of-the-art", "seamless", "robust").
No em dashes or en dashes, no arrows. British spelling. Write numbers as the source prints them.
The summary is for a scientist who has not heard of the model.

## Check your work

After writing each `spec.json`, run:

    python3 -I <batch folder>/check_spec.py <model folder>

Fix every line it prints until it prints `OK`. Then move to the next model. If a model cannot be done (no
official source can be found or fetched), write `spec.json` with only `record_id` and `notes` explaining why,
and move on.

## Report

When all your folders are done, reply with one line per model: folder, OK or not, number of sources,
whether a run guide was written, and any doubt worth a human look. Nothing else.
