# Review claims carried forward to rules version 4

Date: 2026-10-24. Design: `docs/design/discrepancy-rules-v4.html`.

Rules version 4 gives some findings new IDs. A pair that only two studies give a verdict on is now one two-study conflict, and its key names both studies instead of an outlier. For each accepted `discrepancy_review` claim whose finding stopped firing, `scripts/kg/migrate-discrepancy-ids.py` looked for the new ordering finding of the same two systems that includes the old outlier study. Where there was exactly one, it wrote the next revision of the claim with the new ID, the old ID in `previous_ids`, and the same state, rationale and links. `migration.tsv` lists every decision.

| Old ID | New ID | State | Decision |
| --- | --- | --- | --- |
| `discrepancy-4db3e5d24233e19b` | `discrepancy-a2ed36d1ca54b5b9` | investigating | carried forward (#210, PFMBench and ProteinGym on ESM-2 and ESM3) |
| `discrepancy-8c69346a6089882b` | `discrepancy-055eb0dd61040574` | explained | carried forward (#209) |
| `discrepancy-d734930095432234` | `discrepancy-1f1fd7fb7ee75052` | explained | carried forward (#201) |
| `discrepancy-f82ed80f71c6f0bd` | `discrepancy-d586dd34b17efa52` | explained | carried forward (#205) |
| `discrepancy-fed245c475fd08dc` | (same) | explained | the mirror of `f82ed80f`; both now map to one conflict, but two claim chains cannot share it, so this one retires as a resolved finding |
| `discrepancy-1980d1e1d257348a`, `discrepancy-80cbd3e7a2363fde` | none | explained | Geneformer and scGPT no longer fire: with one scGPT configuration per study, the studies no longer disagree |
| `discrepancy-826efbc8dbe634da` | none | explained | Mutect2 and Octopus no longer fire: Sahraeian 2022's 154 rows now count as one study |
| `discrepancy-90953ef91286fc66` | none | false-positive | the vote ensembles are their own systems and are not compared with DeepSomatic, a member (#204) |
| `discrepancy-6e0a1543c1c68a64` | none | false-positive | the ProteinGym paper and repository are one study (#207) |
| `discrepancy-52a714eb6bb63442` | none | confirmed-error | already retired: the Alavi results are disputed (#174) |

`discrepancy-36711e250f9269de` (#211) keeps its ID, so its claim is unchanged.

## Limits

Mechanical carry-forward by a script run by a Claude agent; no human review. No decision was re-examined: each new revision repeats the previous one's state and rationale.
