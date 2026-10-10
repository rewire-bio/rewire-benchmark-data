# Research: Kaschta et al. reanalysis follow-up, 2026-10-10

Use case: `use-case-unresolved-rare-disease-reanalysis` ("Which reanalysis methods find new diagnoses or reduce review effort when given the same updated information?"). This pass extracts one named source found in the 2026-10-09 rare-reanalysis pass (ledger entry `search-use-case-rare-reanalysis-source-resolution-q9`), which was left unextracted because its values are printed only in prose.

No new search was run.

## What was extracted

- Reanalysis of 219 cases without a prior P/LP finding: manual (Emedgene, DRAGEN v4.2.4 re-calling) and Talos 8.2.0 (archived DRAGEN v3.7.5 VCFs). Counts of new P/LP and VUS cases, case-category counts after reanalysis, total diagnostic yield as printed, manual time per case and Talos variants per case. 15 results.
- Talos benchmarking on known findings: singletons (45 cases) and trios (162 cases, trio and proband-only mode). Concordance, VUS captured and failure-mode shares. 12 results.
- Two claims: the input difference and the reported drivers of new findings.

## Judgements

- Reanalysis comparison: `direct`. Same cohort, same interval, both arms with updated knowledge, and the endpoints the question asks for (new findings and review effort). The arms did not get the same variant calls, which favours the manual arm, and the manual result is the reference; both are the first limitations listed.
- Singleton and trio benchmarks: `proxy`. They rerank known findings, which the use case excludes as evidence of new yield.

## Known problems, recorded as limitations

1. Unequal inputs: manual re-called the reads with DRAGEN v4.2.4; Talos used archived v3.7.5 calls through a customised ingestion step.
2. The automated yield is printed as 41.9% (Results 'Automated Reanalysis' P1); 161 of 377 is 42.7%, the value the manual paragraph and the Figure 4 legend print. The stored result keeps 41.9% with a note.
3. The singleton conversion share is 8.6% in Results 'Singleton Cases' P3 and 9.6% in the Figure 2 legend; 3 of 35 is 8.6%, which is stored.
4. Talos output is an average of three variants per case in Results and Discussion P3, and a median of approximately three in Discussion P1.

Items 2 and 3 are printed-versus-printed differences. Following the brief, they are limitations rather than evidence concerns; a reviewer may decide that either should block comparison.

## Not used

- Table 1 (image) and the figures.
- The per-patient supplement, which was not downloaded.
- Case numbers, genes and variants in Results 'Manual Reanalysis' P1-P2.

## Vocabulary

`review-time-per-case` was added for the 81-minute manual review time, because `runtime` is defined as computation time.
