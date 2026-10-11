# Review: use-case-coverage-rna-pathogen-20261011-tisza2026, 2026-10-11

Reviewer: Claude (Opus 5.5) review agent `reviewer-path`, separate from the extracting agent `uc-pathogens`. No human review claimed. Source transcription is not reproduction. The full review, covering all five pathogen batches, is `docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-rna-pathogen-20261011-tisza2026` | Approved with corrections (T1 to T4) |

### Tisza et al. 2026 (EsViritu)

T1. Divergence-capped truth: the Results ('EsViritu is an accurate profiler of mock virus communities' paragraph 2) say "only the 'one-per-family' mock communities were measured in the divergence-capped metrics", while Methods 'Mock communities' says "All six communities were analyzed together" and the S9 caption says "across mock communities". The 15 capped results say "mean over six mock communities". For each of `rna-pathogen-20261011-tisza2026-result-mock-{centrifuger,esviritu,kraken2,metabuli,sylph}-capped-{f1,bray-curtis,pearson}`, replace `mean over six mock communities` with `mean over mock communities` in `metric_qualifier`, and add

`"source_anomaly": "Results 'EsViritu is an accurate profiler of mock virus communities' paragraph 2 says only the three one-per-family communities were measured in the divergence-capped metrics; Methods 'Mock communities' says all six communities were analysed together, and the Supplemental Table S9 caption says 'across mock communities'. The number of communities behind this mean is not certain. Value kept as printed."`

Append to `limitations` of `rna-pathogen-20261011-tisza2026-protocol-mock` and of `use-case-mapping-rna-pathogen-20261011-tisza2026-mock`: `Under divergence-capped truth the Results say only the three one-per-family communities were scored, while Methods say all six were analysed together; the capped means may cover three communities.`

T2. `comparison.inputs` on the ten pos and mock evaluations is wrong (it describes the negative-control libraries). Set it to `Synthetic read pairs (bbtools randomreads.sh)` on `rna-pathogen-20261011-tisza2026-eval-pos-{centrifuger,esviritu,kraken2,metabuli,sylph}` and to `Synthetic NovaSeq read pairs (InSilicoSeq)` on `rna-pathogen-20261011-tisza2026-eval-mock-{centrifuger,esviritu,kraken2,metabuli,sylph}`. Keep the neg evaluations as they are (Table S16 confirms one ONT library).

T3. The Results paragraph 4 of 'EsViritu reaches read-level sensitivity' prints model-estimated probabilities (EsViritu 0.995, Metabuli 0.99996, Sylph 1.8 × 10^-3) and odds ratios (for example Sylph 6.4 × 10^-8) that match neither Supplemental Table S2 nor the S3 contrasts (Sylph/EsViritu 2.3 × 10^-5 at 10 read pairs). Add to each of the ten `rna-pathogen-20261011-tisza2026-result-pos-*` results:

`"source_anomaly": "Results 'EsViritu reaches read-level sensitivity while avoiding false positives' paragraph 4 prints detection probabilities (EsViritu 0.995, Metabuli 0.99996, Sylph 1.8 x 10^-3) and odds ratios that do not match Supplemental Tables S2 and S3; the text appears to describe a different fit. Value is the S2 marginal mean as printed."`

T4. Append to `limitations` of `rna-pathogen-20261011-tisza2026-protocol-pos`: `The S2 caption does not name the parameter setting; the Results tie the regression to the headline parameters, so the results are attached to the headline configurations.`

## Corrections applied

Applied by the extractor as the reviewer specified, before the batch was added to the store.

1. T1: the 15 capped results now say 'mean over mock communities' and carry the reviewer's source_anomaly; the reviewer's limitation appended to protocol-mock and the RNA mock judgement.
2. T2: comparison.inputs set to the reviewer's text on the five pos and five mock evaluations; neg unchanged.
3. T3: the reviewer's source_anomaly added to the ten pos results.
4. T4: the reviewer's limitation appended to protocol-pos.
5. All records set to source_checked. Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note as specified; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
6. Corrections were applied in the extraction script under extract/, and batch.jsonl, claims.csv, coverage.json, sources.md and research.md were regenerated.

## Records after correction

- benchmark: 1
- claim: 6
- configuration: 5
- dataset: 3
- evaluation: 15
- method: 4
- protocol: 3
- result: 105
- source: 2
