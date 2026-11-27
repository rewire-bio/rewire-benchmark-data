# Model pages, revision 2, 2026-11-27

Prepared by Claude agents. No human review is claimed. One agent revised the pages, a second verified them, the first applied the verifier's findings, and a separate session wrote this review and applied the result.

## What changed

Two model records have their `profile` and `run_guide` replaced and their `checkpoints` list updated: RNA-km and PromoterAI. Both pages were written earlier without the full text of the model's paper. The owner downloaded the papers in a browser on 27 November 2026, and their text is now a source on each record (batch `paper-full-texts-20261127b`, reviewed in [2026-11-27-paper-full-texts-b.md](2026-11-27-paper-full-texts-b.md)).

No result, evaluation or claim was added or changed.

## What the revisions did

- Facts the page marked as not reported were filled where the paper states them: parameter counts, architecture, training data and masking settings.
- Where the paper and a README, config or code file differ, the page states both and does not prefer one.
- Limitations the paper states about its own model were added.

The record of every change to each page is in the batch's `changes/` folder.

| Page | Statements checked | Supported | Partly supported |
| --- | --- | --- | --- |
| RNA-km | 34 | 33 | 1 |
| PromoterAI | 37 | 35 | 2 |

## How the revisions were checked

Every copied passage was confirmed present in its saved file by `scripts/enrich/check_spec.py`. A verifier agent that had not made the revisions judged 71 statements against their sources. It found 3 partly supported and none unsupported or wrong: 4.2 percent before correction. The verdicts and the corrections are in the batch's `fixes/` folder.

The three findings, all corrected before applying:

- RNA-km: the paper's parameter count describes the architecture. The page had placed it on the released weight file, which no saved file counts. The checkpoint entry now has no parameter count and the page gives the figure as the paper's.
- PromoterAI: a parameter count was applied to both members of the model's ensemble; the paper states it for one. The page now says which.
- PromoterAI: a reason for an input column that no source gives was removed.

No page in this batch was read in full by the applying session before merge.

## Pages not revised

Four pages whose papers were archived in the same batch are not revised here: DeCodon, EnCodon, E1 and ProGen3. Work on each was interrupted and, by the project's rule, was not retried by an agent. They are listed in [todo.md](../todo.md) as set aside for a person. Their papers are sources in the archive, so the remaining work is a revision from text the store already holds.

## Found in the papers

Differences between a paper and its released files that were found while reading are recorded in `kb/curation/source_leads.jsonl`. They are leads, not conclusions.
