# Review: feng-dna-fm-20261013, 2026-10-13

Reviewer: an independent Claude (Opus 5.5) review agent, separate from the extraction agent `feng-19`. No human review claimed. Source transcription is not reproduction.

Dated review: [docs/reviews/2026-10-13-feng-dna-foundation-models.md](../../../docs/reviews/2026-10-13-feng-dna-foundation-models.md).

## Outcome

Approved with corrections. Every number was right in the first pass. Four descriptive errors were found; the extractor fixed them in `extract/extract_feng.py` and regenerated the batch. The regenerated batch was checked again, and `review/signoff.py` then set all 447 records to `source_checked` and wrote the review objects.

## Checks

- Sources: re-downloaded the article XML, Supplementary Data workbook, Supplementary Information PDF, `job_scripts/gtex_hyena.py` and README at commit 3f4c81c. All five SHA-256 values match their source records. `artifacts/MOESM3_ESM.xlsm.gz` decompresses to the workbook bytes.
- Results: a separate ElementTree parser of the XML tables compared all 126 results (110 in Table 1, 16 in Table 4): printed and numeric value, metric, qualifier, unit, direction, locator, bold marking and the linked configuration and protocol. 0 mismatches. The 50 bold Table 1 cells are exactly those whose locator says so.
- Datasets: all 22 Table 1 datasets match Supplementary Data 6 (training and test size, median, minimum and maximum length, label counts). The three notes on label counts that do not sum to the split sizes, and the Enhancer Ensembl three-class note, are correct.
- Baseline CNN claims: all 26 match Supplementary Data 1 and 2.
- Configurations, protocols and evaluations: all 118 evaluations are `independent_paper` with one system, assessment and data link. Frozen embeddings plus a supervised random forest is stated throughout; nothing claims label-free scoring. Checkpoints match Methods "Model configuration selection" and the bold rows of Supplementary Table 8. GTEx access and the reproduction constraints match the Data availability statement and the pinned script.
- Descriptive claims: the two expression findings, the TAD finding (checked against the rendered Supplementary Fig. 2) and the tables-not-extracted inventory match the cited text.
- Relevance judgements: both are proxy for `use-case-regulatory-variant-gene-follow-up`. The endpoint is cross-individual expression prediction from personal sequence. That bears on allele-effect prediction, which the use case keeps as a separate comparison; it does not score variants or link elements to genes. Limitations now carry the authors' "preliminary indicators" caveat and the lack of held-out loci. Reviewed evaluations: 5 on the 6 kb protocol, 3 on the 768-gene protocol.
- Scope: leaving the Table 1 region-classification rows unmapped is right; none of the use cases makes that decision. Nothing maps to `use-case-patient-rna-splicing-validation`.
- Duplicates: no ID collides with the store, and no stored Feng result (140) shares a locator with this batch.
- The regenerated `batch.jsonl` and `claims.csv` are byte-identical to a fresh run of `extract/extract_feng.py` on the pinned artifacts. The signed-off batch validates against the store's record, vocabulary and attribute schemas (dry run, nothing written).

## Corrections applied by the extractor

1. The Supplementary Information PDF has 11 pages and contains Supplementary Table 8 and Supplementary Figures 1 and 2. The source record and research.md had said these were missing. The real discrepancy is now recorded instead: the main text puts the TAD region at about token positions 300 to 700, the Supplementary Fig. 2 caption at about 200 to 600.
2. The GTEx configurations said the article does not state how the two allele embeddings are combined. Methods says they are averaged, and that Enformer uses its final hidden state mean-pooled over regions. The text now says so.
3. "dbGaP" was removed: the Data availability statement names only the GTEx Protected Data Access portal.
4. The TAD dataset no longer says GRCh38; the source says only "the human reference genome" for it.
5. The extractor also applied the recommended items: added the authors' caveat, the missing held-out loci, the distal-element and 131 kb versus 196 kb notes to the judgements; listed Supplementary Tables 5 to 8 and Supplementary Fig. 1 in the tables-not-extracted claim; and set the DNABERT-2 and GROVER checkpoints.

## Remaining work for integration

- Add `assessed_by` links from `use-case-regulatory-variant-gene-follow-up` to the two expression protocols, then run `npm run use-cases:repin` for the two judgement claims.
- Supplementary Data 4 (per-chromosome-group AUCs behind Tables 5 and 6) is still not extracted.

## Integration note (extractor, 2026-10-13)

At integration the store's attribute normaliser drops `review.date` when `review.reviewed_at` is present, which failed `tests/attributes.test.ts`. The `date` key was removed from the 161 signed-off review objects in `batch.jsonl` before `records add`; no other byte changed. File hashes in `review.json` were refreshed for this edit and this note. The assessed_by links and repin were then done as listed above.
