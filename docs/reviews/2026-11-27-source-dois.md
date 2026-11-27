# DOIs filled on sources that held one only in a URL or name, 2026-11-27

Reviewer: `claude`, the agent that made the change. No human review. An independent verification pass
is needed before merge.

Rule (accepted by the team lead on 27 November): sources that share a DOI are one study, for the
boards and for the discrepancy finder, and a difference between results of one paper is not a
disagreement between studies. Both programs already join sources by the `doi` field. 292 sources had
no `doi` but held one in their URL or name, so the rule could not see them. The clearest case is
BEELINE: its three source-data files (`acquired-source-0f6c059ffdc338b70a5c`,
`-31344fb7e5e8ae6b9666`, `-3156602fda847ae943b4`, supplementary files MOESM12 to MOESM14 of
10.1038/s41592-019-0690-6) were three studies, and the published discrepancy
`discrepancy-0311356983b743d6` set one of them against the other two.

Batch `data/omics/source-dois-20261127/` fills the `doi` field on 289 of the 292. `extract/find.py`
finds them by pattern, `extract/classify.py` normalises each DOI (drops bioRxiv version suffixes,
query strings and trailing `/pdf` or `/fulltext`) and states where it came from; `evidence.jsonl`
gives the origin for every source:

| Origin | Sources |
| --- | --- |
| The source's URL is the doi.org address of the DOI | 247 |
| The source's URL is the bioRxiv page or API record of the preprint | 19 |
| The source is the Europe PMC record of the preprint, and its name states the DOI | 9 |
| The source is a supplementary file whose Springer Nature address names the article DOI | 8 |
| The source is a Nature article page whose name states the article DOI | 2 |
| The source's URL is the publisher's article address containing the DOI | 2 |
| The source is a PLOS supplementary item, recorded under its article's DOI | 2 |

Checked against "is this DOI the source's own": every DOI is the DOI of the work the source is part of.
Two are not exactly the source's own DOI and are filled by the store's existing practice for
supplements (supplementary files carry their article's DOI): the PLOS FramePool Supplementary Tables
S1 and S4, whose own item DOIs are 10.1371/journal.pcbi.1008982.s020 and .s023. Three are left unfilled
and listed in `not-filled.jsonl`: trRosettaRNA files whose URL holds the Zenodo concept DOI (all
versions), not the version DOI of the record they name. No URL was a citing page.

## What changed

- **Studies.** Results now fall into 362 studies instead of 365: BEELINE's three files are one study.
  No other DOI had results split across studies, so no board changes on main (BEELINE is linked to no
  use case there).
- **Discrepancies.** 209 live findings before, 208 after; no other finding's ID changed. The BEELINE
  finding `discrepancy-0311356983b743d6` stopped firing because its outlier and consensus are now one
  study. It had no review claim, so it would have vanished. A `discrepancy_review` claim
  (`data/omics/discrepancy-review-20261127-beeline/`, revision 1, state `false-positive`, action
  `investigated`) records why, and the build now keeps it as a resolved finding under the same ID,
  with its history, as `docs/discrepancies.md` describes for settled findings.
- **Test.** `kb/tests/test_studies.py` checks on the built store that every DOI's sources are one study,
  and that BEELINE's three files are one.
