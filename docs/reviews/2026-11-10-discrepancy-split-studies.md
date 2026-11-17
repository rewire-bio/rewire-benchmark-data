# Discrepancy rules version 5: a split study takes no side

Date: 2026-11-10. Issues: #210. Rules: `data/ontology/discrepancy-rules.json`, version 5.

Version 4 counted a split study as one of the studies an ordering finding is measured against. Version 5 counts only studies that take a side. A split study is still listed in the finding's `studies` with verdict `split`; it no longer forms a party to a two-study conflict, and no longer sits in the consensus denominator.

## What went wrong

Four evidence batches merged on 7 November (PRs #236 to #239). The release build then failed, every time, on the orphan check:

    review claim(s) discrepancy-review-20261023-pfmbench-esm2-esm3, ...-r2
    name discrepancy-a2ed36d1ca54b5b9, which is not derived and is not settled

The finding had not been re-keyed. It had stopped firing. `scripts/kg/migrate-discrepancy-ids.py` found no ordering finding for the pair to carry the review forward to, and exited non-zero rather than guess.

Three studies compare ESM-2 with ESM3 on the store at this commit:

| Study | Comparisons | Ties | Verdict |
| --- | --- | --- | --- |
| ProteinGym, doi:10.1101/2023.12.07.570727 | 19 | 1 | ESM3, 18 of 18 untied |
| PFMBench, doi:10.48550/arxiv.2506.14796 | 12 | 0 | ESM-2, 9 of 12 |
| HyPLM-Flash, repository tencent-hunyuan/hyra-results | 28 | 6 | split, 11 to 11 |

`verdicts` returns a split study with the value `None` rather than leaving it out. Under version 4 that put the HyPLM-Flash study in the count both rules read:

- the two-study conflict needed exactly two studies in that dict and saw three, so it did not fire;
- each reversal candidate had two others, only one of which had an opinion, giving a consensus share of 0.5 against the 0.8 threshold, so neither fired.

None of the review's 24 subject results are disputed or under an evidence concern. The disagreement between ProteinGym and PFMBench is the same as it was. A study with no opinion silenced it, and took an open review with it.

Reading "no opinion" as "disagrees" is the defect. A split study has no side to be an outlier from and none to add to a consensus.

## Counts

Measured on this branch with one `npm run kg:bundle`. The middle column is version 4 on the same store, derived in the same process as version 5 so the two share an inference pass.

| | Release 2026-11-02 | Version 4, current store | Version 5, current store |
| --- | --- | --- | --- |
| Live findings | 126 | 124 | 191 |
| Two-study conflicts | 91 | 88 | 124 |
| Ordering reversals | 35 | 35 | 66 |
| Gap outliers | 0 | 1 | 1 |
| Medium / low | 1 / 125 | 0 / 124 | 2 / 189 |
| Resolved findings kept | 7 | 7 | 7 |

67 findings appear: 36 two-study conflicts and 31 ordering reversals. 65 are low severity. None is removed, and no finding changes its rule, severity or ID, so nothing already published is restated: every one of the 67 is a disagreement that version 4 held back.

`discrepancy-a2ed36d1ca54b5b9` returns as a two-study conflict at medium severity, same-task scope, listed public, which is exactly its identity at release 2026-11-02. Its review claims need no edit and keep their IDs. The other medium finding is `discrepancy-44e5640b79522964`, a new ordering reversal.

The hand-reviewed findings in `scripts/kg/fixtures/labelled-findings.json` all still resolve: the Alavi real error retires as a resolved finding, and the three open leads, including #210, are live and public.

## Why not the alternatives

Settling the review as `explained` or `false-positive` would have unblocked the release in one commit. It would also have been false. Nobody explained anything: PFMBench gives ESM3 0.414 and ESM-2 0.439 on its ProteinGym zero-shot row while ProteinGym's own files give 0.466 and 0.414, and issue #210 is open on exactly that. Settling a live disagreement to make a build pass is the failure mode the orphan check exists to prevent.

Changing only the two-study branch would have restored this finding with about half the new ones. It leaves the same conflation in the reversal denominator, where a single split study among three others still drags the share under the threshold.

## Scope and risk

The rules are part of the release coverage (`discrepancy_generator_sha256`), so this cuts a new release with no record changed. No record, value or link is touched; `check_derived` and the derived-graph SHACL shapes passed. The site gains 67 leads, 65 of them low severity. Of the 191 live findings, 19 are listed public and 172 for curation, so most of the new ones are not on the default contested page.

Two tests pin the behaviour in `scripts/kg/tests/test_build.py`: a split third study does not end a two-study conflict, and does not dilute a consensus. Both fail on version 4.
