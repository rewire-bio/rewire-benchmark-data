# Research: the state of the Alavi 2026 AlphaGenome splicing discrepancy

The discrepancy `discrepancy-ead251c24ba272c1` is derived by `scripts/kg/contradictions.py`: Alavi 2026 ranks Borzoi above AlphaGenome on its 65-gene splicing set, while the AlphaGenome paper's own tables rank AlphaGenome above Borzoi on every task both appear in. This batch records what has been done about it, so the state is in the database rather than only in correspondence.

## What was done

| Date (2026) | Step |
| --- | --- |
| 10-16 | An AlphaGenome developer said the splicing result could not be right, in reply to a request to check an article. |
| 10-19 | A 1-base coordinate offset was found in both published AlphaGenome scripts by cross-tabulating the preprint's per-variant calls against the shifted base, and reported as issue #2. |
| 10-20 | The author labelled it a bug, confirmed that rerunning with `pos_1based` substantially improved accuracy, and promised scripts in calendar week 44 and a revised manuscript in early November. |
| 10-22 | This record: state `awaiting-correction`, next check 2026-11-10. |

## Decisions

| Item | Decision | Reason |
| --- | --- | --- |
| State | `awaiting-correction` | The authors have accepted the problem; what is outstanding is their rerun, not our investigation. |
| The affected results | Left as reported | A review claim records where the discrepancy stands. Changing a value needs the corrected source, through a reviewed record change. Marking the results `disputed` is separate work, tracked in issue #174. |
| Subjects | The six multigene AlphaGenome sensitivity and specificity results | These are the rows the offset affects and the ones that were republished elsewhere. The OPA1 rows share the same shifted thresholds and are covered by the issue, but the 65-gene rows are what the discrepancy compares. |
| `resolved_by` | Not set | There is no corrected source yet. It is filled in when the revised preprint is added. |

## What is still open

- The corrected preprint and scripts, expected early November 2026.
- Whether the rerun removes the disagreement or leaves part of it, which decides whether the final state is `confirmed-error` alone or also an `explained` remainder.
- The discrepancy only appears in the derived graph once the AlphaGenome paper's comparator configurations are linked to their models; that identity work is separate. This claim is keyed by the discrepancy's stable ID, so it applies as soon as the links land.
