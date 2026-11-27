# Use-case boards

A board orders the models assessed for one use case by the comparisons studies made between them.
`kb/board.py` builds one board per use case from the store. Every release publishes them as one file,
`public/omics/boards/<release_id>.json`, for the website's use-case pages.

## What a board is and is not

Two papers rarely run the same test on the same models, so their numbers cannot share a column. What
can be used is the order inside one study: when a study scores two models on the same test with the
same metric, it says which did better. A board collects those verdicts from every study on the use
case's tests and fits one order to them (a Bradley-Terry model, each study weighted equally).

- It orders models by the comparisons studies made. It does not say what would happen if every model
  were run on one test, and it gives no score on any metric.
- It ranks at the model, not the checkpoint. "Evo 2" on a board pools its sizes and versions, because
  results are not yet tied to checkpoints for most use cases. As grounding reaches a use case, its
  board can rank checkpoints instead ([todo.md](todo.md), item 11).
- It is separate from the ranking a use-case page shows today, which takes one comparison (one
  protocol and metric) and orders the tools by their value on it.

## How to read a row

| Field | Meaning |
| --- | --- |
| `positions` | Best and worst place the comparisons support, for example `[1, 3]`. One number when they agree. |
| `strength` | Chance of beating an average model on this board, from 0 to 1. The average is taken over every model fitted, including those not ranked |
| `interval` | Lowest and highest strength when the fit is repeated with each study left out |
| `studies` | The studies the model was compared in, with how many comparisons came from each |
| `opponents` | How many other models it was compared with directly |
| `comparisons` | How many pairwise comparisons, inside one study and one test, it took part in |
| `basis` | `mostly one study` when one study gives 80 percent or more of its comparisons, else `several studies` |

A wide range in `positions` means the studies do not settle the order. Rows are listed by strength, so
two rows can show overlapping ranges: neither is placed above the other.

## The rules

The rules are stated in full in the docstring of `kb/board.py`. In short:

1. Only results inside one study's group (same protocol, data, metric, unit and conditions) are
   compared. A model's value in a group is its best configuration. Disputed, excluded and superseded
   results, results copied from another paper and metrics with no direction are left out. A test feeds
   a board only when the use case judges it `direct` or `proxy`; one judged `outside_scope` stays
   linked for the record but is not evidence. Leaderboard imports record each submission's identity in
   a structured scoring condition; the board compares those without the keys that name the
   submission, the system's own configuration or the result's own counts, so the entries of one
   leaderboard round can be compared with each other.
2. Study ids joined by " + " that share a part are one study, so one piece of work counts once.
3. Records with the same name, ignoring case and punctuation, are one row when one of them is a model
   record. The row lists every record id.
4. Each study gives one verdict per pair of models. A study with many groups counts no more than one
   with a single group. One imagined draw against an average model keeps a model with one win from
   being placed first.
5. Every model is fitted, but only some get a row:
   - the record must be a model, method, pipeline or service, and not excluded. A configuration with no
     parent model, or a baseline, is listed as `not a model record`;
   - the model must have been compared in at least two studies. Otherwise it is listed as `one study`;
   - it must be joined, through comparisons, to the largest group of models on the board. Otherwise it is
     listed as `not compared with the main group`.
6. A board with fewer than two rows has none (`no second model to rank`), and its summary says so.
7. Model A is placed above B only when A is stronger, by more than 0.1 percent, in the full fit and
   in every refit with one study left out, and no refit leaves the two in groups of models never
   compared with each other. Positions follow from that rule, so near-ties share positions, and an
   order that rests on a single study joining two groups is not taken as settled.

## The file

`public/omics/boards/<release_id>.json` is written by `python3 kb/board.py --manifest
public/omics/manifest.json` and checked by `npm run boards:check` (`shared/omics/boards.ts` holds the
types and the validator). The website package lists it like any other file under `public/omics`, so
it is published as the asset `public.omics.boards.<release_id>.json.gz` of the `serving/<release_id>`
release. Releases made before boards were added have no such file; a reader treats that as no boards.

```
{ "schema_version": 1, "release_id": "...", "released_at": "2026-11-27T11:48:36.000Z", "method": "...",
  "boards": [ one board per use case, by slug ] }
```

A board:

| Field | Content |
| --- | --- |
| `use_case`, `use_case_id`, `title` | The use case's slug, record id and name |
| `release_id`, `released_at` | The release the board was computed from, and its date |
| `method` | The method in one sentence |
| `summary` | One sentence: how many models are ranked, from how many groups and studies, and what was left out |
| `counts` | `studies`, `groups` and `models` it rests on; `ranked`; and `one_study`, `not_a_model`, `not_connected`, `too_few`, which with `ranked` add up to `models` |
| `rows` | The ranked models, strongest first (fields above, plus `model_id`, `record_ids` and `name`) |
| `not_ranked` | Every other model: `model_id`, `name`, `reason` and `study_ids` |
| `studies` | For each study id a row or a not-ranked model cites: `source_ids` (source records) and `dois` |

A row of the splicing board in release 2026-11-27-60cac85951eb, shortened:

```
{ "model_id": "discovery-model-pangolin", "record_ids": ["discovery-model-pangolin"], "name": "Pangolin",
  "positions": [1, 3], "strength": 0.869, "interval": [0.833, 0.919],
  "studies": { "doi:10.1038/s41586-026-10176-5": 34, "doi:10.1186/s13059-023-03144-z": 144, ... },
  "opponents": 22, "comparisons": 212, "basis": "several studies" }
```

A study id is not always a record id (`doi:...` names a group of sources with one DOI), so link a study
through its `source_ids`.

## Building it locally

`python3 kb/migrate.py && python3 kb/board.py` writes `kb/build/boards.json` for release `unreleased`
in about 8 seconds. `--use-case <slug>` prints one board. `npm run boards` writes and checks the
release's file after `npm run omics:release`. The tests are `kb/tests/test_board.py` and
`tests/boards.test.ts`.
