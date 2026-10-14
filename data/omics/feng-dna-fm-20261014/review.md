# Review: feng-dna-fm-20261014, 2026-10-14

Reviewer: an independent Claude (Opus 5.5) review agent for PR #157, separate from the extraction agent for #142. No human review claimed. Source transcription is not reproduction.

Dated review: [docs/reviews/2026-10-14-feng-remaining-tables.md](../../../docs/reviews/2026-10-14-feng-remaining-tables.md). Use-case re-review: [docs/reviews/use-cases/feng-variant-effect-per-group-2026-10-14.md](../../../docs/reviews/use-cases/feng-variant-effect-per-group-2026-10-14.md).

## Outcome

Approved with corrections. Every number was right. The reviewer changed `extract/extract_feng.py` so the 177 Supplementary Data 4 results sit on 59 per-group evaluations instead of the stored three-group-mean evaluations, rewrote the HyenaDNA-160K note, and added the 4mC notes. The script was rerun on the pinned artifacts, and `review/signoff.py` checked the output and set all 698 records to `source_checked`.

## Checks

- Sources: the article XML, workbook and Supplementary Information PDF were re-downloaded on 2026-10-14; all three SHA-256 values match their source records.
- Reproduction of the extraction: the submitted `batch.jsonl`, `claims.csv` and `extract/sd4-mean-check.json` were byte-identical to a fresh run before any change.
- Results: `review/signoff.py` parses the XML tables and workbook sheets with its own code and compared all 305 results (printed and numeric value, metric, qualifier, unit, direction, locator, bold, source, and the linked configuration, protocol and dataset). 0 mismatches. A mutation test made it fail on each of five planted errors. Eleven values were also checked by hand.
- Datasets: all 25 match Supplementary Data 6 and the Supplementary Note 2 flags.
- Baseline CNN claims: all 26 match Supplementary Data 1 and 2.
- Supplementary Data 4 linkage: every per-group evaluation has the links, origin and comparison of the stored Table 5/6 evaluation except `aggregation`; every stored mean is within rounding of the mean of its three groups.
- Store write: `records -- add` passed the SHACL subset check. The old inventory claim was set to `superseded`, and the five Feng variant-effect judgements were re-reviewed, given exclusions and a limitation, and re-pinned.

## Reproduce

```sh
python3 -I data/omics/feng-dna-fm-20261014/extract/extract_feng.py <epmc.xml> <MOESM3_ESM.xlsm> <MOESM1_ESM.pdf> . data/omics/feng-dna-fm-20261014
python3 -I data/omics/feng-dna-fm-20261014/review/signoff.py <epmc.xml> <MOESM3_ESM.xlsm> <MOESM1_ESM.pdf> .
```

Both must run against the store as it was before this batch was added: the extractor refuses IDs already in the store. The second command reproduces the signed-off `batch.jsonl`.
