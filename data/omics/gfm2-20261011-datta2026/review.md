# Review: Datta et al. 2026 batch, 2026-10-11

Reviewer: Claude (Opus 5.5) review agent `reviewer-gfm-a`, independent of the extractor `lit-gfm-2`. No human
review claimed. Source transcription is not reproduction.

Verdict: **pass with corrections**. All 144 printed values and spreads match Table 1, and every printed
recovery percentage agrees with the two extracted scores (frozen divided by FT, times 100, within 1 point
of rounding), which is an independent check on the transcription. No numerical value changed. All 303
records are `source_checked`. Because the source carries evidence concerns, none of its results can
support an automatic comparison; I think that is right for this source (see below).

## Source and hashes

| Item | SHA-256 | Check |
| --- | --- | --- |
| arXiv:2608.05329v1 PDF, fresh download 2026-10-11 | `df36e4772562329550c924004a546812c8d76149a1b5238e4d0b0cfa8a82bb5c` | Matches the source record |
| `pdftotext -layout` (poppler 26.08.0) text | `b2458cdb3a338c1ec39021610df8229050a8082065fbe5489f0e16a443e4f401` | Bound in `review/review.py` |

Licence: the abstract page links the arXiv non-exclusive distribution licence 1.0. No copy of the PDF or
its text is committed, which is correct.

## Method

`review/review.py` parses Table 1 and Table 4 from the text layer with its own matching; it does not import
the extractor. For every result it asserts printed value, numeric value, printed spread, metric (Section
3.2: MCC for histone and enhancer tasks, F1 for promoter and splice tasks), unit, direction, locator, the
evaluation ID, configuration, protocol, dataset, origin and `metric_implementation`. It recomputes each
cell's recovery, checks the model list and parameter counts in Section 2.2 and the readout grid in Section
2.5, then applies the corrections. `review/corrections.json` lists each edit by record ID. Run order:
`extract/extract.py`, then `python3 -I review/review.py <text layer>`.

Model identity: configurations keep the printed names and sizes (HyenaDNA-436K, NT-500M, GENERATOR-v2-1.2B,
Omni-DNA-116M) and mark the checkpoint revision unreported. NT-500M is linked to the Nucleotide Transformer
family, not to NTv2, which is correct: the paper cites Dalla-Torre et al. 2025 without saying which 500M
checkpoint. HyenaDNA is linked to the HyenaDNA family record. Nothing is collapsed.

## Corrections

1. **FT spread type.** The 54 reference fine-tuned results with a printed `±` were typed
   `standard_deviation`. Section 3.3 defines only the frozen-probe spread (SD over five seeds). The FT
   values are benchmark- or model-reported, and the table never says what their spread is. They are now
   `unresolved_spread`.
2. **Task missing from the qualifier.** All 18 tasks share one protocol and one dataset record, and the
   qualifier was the same for every task ("frozen-embedding probe"). Only free text in `comparison.inputs`
   told the tasks apart. The qualifier now names the task, for example "NT benchmark H3K4me3,
   frozen-embedding probe".
3. **Probe set.** `protocol-frozen-probe` listed an RBF-SVM probe. Section 2.4 lists one, but the grid
   behind the reported results is {mean, max, CLS, last, attn, top-k} × {LR, MLP} (Section 2.5). Corrected.
   The four frozen configurations now say that the readout and probe are chosen per task over the test
   grid (Table 3).
4. **What Table 1's frozen numbers are.** Table 4 shows that five of seven HyenaDNA cells in Table 1 equal
   the diagnostic test-set grid-best values. The authors say these values are not unbiased
   model-selection estimates. Added as a limitation on both protocols.
5. **DNABERT-2 limitation.** The text "DNABERT-2 appears only in the controlled LoRA comparison (Table 9)"
   was wrong: DNABERT-2 is also in Tables 2, 7 and 8. Corrected on 146 records.
6. **Second evidence concern.** For HyenaDNA Splice Acceptor, Table 1 prints .4752±.0108, while Table 4
   prints 0.7308 (validation-selected) and 0.7360 (grid-best). Splice Donor in Table 1 equals Table 4's
   validation-selected value, not its grid-best value. Table 3 and Table 4 name different grid-best
   readouts for Splice All. All of this is recorded in a second `evidence_concerns` entry on the source.

## The extractor's questions

- **Duplicated NT cell (Enhancer, Enhancer Types).** Confirmed: both print `.5252±.0262`. The printed
  recoveries (96 and 124) both follow from that value, so the duplication is in the authors' numbers, not
  only in typesetting. The concern's wording is accurate. Note that an `evidence_concerns` entry blocks
  every result of the source from automatic comparison, not just the two cells
  (`shared/omics/catalogue-query.ts`, `published-comparisons.ts`). I kept the source-level block on purpose.
  The frozen values are test-set maxima. The FT values are unmatched references. Table 1 conflicts with
  Table 4. That is enough to keep this source out of automatic comparisons.
- **Recovery metric.** I agree with storing the two inputs and a definition claim, not a new concept.
- **Mixed-provenance split** (`origin: unreported` FT protocol and configurations): this is the right shape.
  It stops a reader treating the frozen and FT numbers as one matched run.
- **NT benchmark dataset identity.** Not changed. The single `data-nt-benchmark` record covers 18 tasks.
  Once the `lit-genomics` per-task records land, the evaluations should be repointed to them. That needs a
  `records change` with a dated review.

## Relevance judgements

None in the batch, and none proposed.

## Remaining gaps

Tables 2 to 9 are unextracted. Tables 2 and 7 print no metric name; Table 9 (the matched DNABERT-2 LoRA
comparison) also gives no metric per task. Figures not read.

## Values checked

| Result | Locator | Printed | Spread | Metric | Outcome |
| --- | --- | --- | --- | --- | --- |
| `result-generator-v2-enhancer-frozen` | Table 1, row 'Enhancer', column 'GENERATOR-v2', frozen value | .5314 | ±.0238 | matthews-correlation-coefficient | Match |
| `result-generator-v2-enhancer-ft` | Table 1, row 'Enhancer', column 'GENERATOR-v2', FT value | .580 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-enhancer-types-frozen` | Table 1, row 'Enhancer Types', column 'GENERATOR-v2', frozen value | .4305 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-generator-v2-enhancer-types-ft` | Table 1, row 'Enhancer Types', column 'GENERATOR-v2', FT value | .477 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3-frozen` | Table 1, row 'H3', column 'GENERATOR-v2', frozen value | .7381 | ±.0150 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3-ft` | Table 1, row 'H3', column 'GENERATOR-v2', FT value | .806 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k14ac-frozen` | Table 1, row 'H3K14ac', column 'GENERATOR-v2', frozen value | .5036 | ±.0046 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k14ac-ft` | Table 1, row 'H3K14ac', column 'GENERATOR-v2', FT value | .605 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k36me3-frozen` | Table 1, row 'H3K36me3', column 'GENERATOR-v2', frozen value | .5667 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k36me3-ft` | Table 1, row 'H3K36me3', column 'GENERATOR-v2', FT value | .657 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k4me1-frozen` | Table 1, row 'H3K4me1', column 'GENERATOR-v2', frozen value | .4997 | ±.0134 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k4me1-ft` | Table 1, row 'H3K4me1', column 'GENERATOR-v2', FT value | .553 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k4me2-frozen` | Table 1, row 'H3K4me2', column 'GENERATOR-v2', frozen value | .3159 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k4me2-ft` | Table 1, row 'H3K4me2', column 'GENERATOR-v2', FT value | .424 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k4me3-frozen` | Table 1, row 'H3K4me3', column 'GENERATOR-v2', frozen value | .3822 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k4me3-ft` | Table 1, row 'H3K4me3', column 'GENERATOR-v2', FT value | .512 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k79me3-frozen` | Table 1, row 'H3K79me3', column 'GENERATOR-v2', frozen value | .5621 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k79me3-ft` | Table 1, row 'H3K79me3', column 'GENERATOR-v2', FT value | .670 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k9ac-frozen` | Table 1, row 'H3K9ac', column 'GENERATOR-v2', frozen value | .6098 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h3k9ac-ft` | Table 1, row 'H3K9ac', column 'GENERATOR-v2', FT value | .612 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h4-frozen` | Table 1, row 'H4', column 'GENERATOR-v2', frozen value | .7928 | ±.0078 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h4-ft` | Table 1, row 'H4', column 'GENERATOR-v2', FT value | .815 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-h4ac-frozen` | Table 1, row 'H4ac', column 'GENERATOR-v2', frozen value | .4439 | ±.0035 | matthews-correlation-coefficient | Match |
| `result-generator-v2-h4ac-ft` | Table 1, row 'H4ac', column 'GENERATOR-v2', FT value | .592 | none | matthews-correlation-coefficient | Match |
| `result-generator-v2-promoter-all-frozen` | Table 1, row 'Promoter All', column 'GENERATOR-v2', frozen value | .9630 | ±.0000 | f1-score | Match |
| `result-generator-v2-promoter-all-ft` | Table 1, row 'Promoter All', column 'GENERATOR-v2', FT value | .962 | none | f1-score | Match |
| `result-generator-v2-promoter-non-tata-frozen` | Table 1, row 'Promoter Non-TATA', column 'GENERATOR-v2', frozen value | .9662 | ±.0000 | f1-score | Match |
| `result-generator-v2-promoter-non-tata-ft` | Table 1, row 'Promoter Non-TATA', column 'GENERATOR-v2', FT value | .962 | none | f1-score | Match |
| `result-generator-v2-promoter-tata-frozen` | Table 1, row 'Promoter TATA', column 'GENERATOR-v2', frozen value | .9525 | ±.0080 | f1-score | Match |
| `result-generator-v2-promoter-tata-ft` | Table 1, row 'Promoter TATA', column 'GENERATOR-v2', FT value | .948 | none | f1-score | Match |
| `result-generator-v2-splice-acceptor-frozen` | Table 1, row 'Splice Acceptor', column 'GENERATOR-v2', frozen value | .9089 | ±.0000 | f1-score | Match |
| `result-generator-v2-splice-acceptor-ft` | Table 1, row 'Splice Acceptor', column 'GENERATOR-v2', FT value | .981 | none | f1-score | Match |
| `result-generator-v2-splice-all-frozen` | Table 1, row 'Splice All', column 'GENERATOR-v2', frozen value | .7754 | ±.0000 | f1-score | Match |
| `result-generator-v2-splice-all-ft` | Table 1, row 'Splice All', column 'GENERATOR-v2', FT value | .978 | none | f1-score | Match |
| `result-generator-v2-splice-donor-frozen` | Table 1, row 'Splice Donor', column 'GENERATOR-v2', frozen value | .9094 | ±.0021 | f1-score | Match |
| `result-generator-v2-splice-donor-ft` | Table 1, row 'Splice Donor', column 'GENERATOR-v2', FT value | .978 | none | f1-score | Match |
| `result-hyenadna-enhancer-frozen` | Table 1, row 'Enhancer', column 'HyenaDNA', frozen value | .5243 | ±.0635 | matthews-correlation-coefficient | Match |
| `result-hyenadna-enhancer-ft` | Table 1, row 'Enhancer', column 'HyenaDNA', FT value | .517 | ±.117 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-enhancer-types-frozen` | Table 1, row 'Enhancer Types', column 'HyenaDNA', frozen value | .3710 | ±.0187 | matthews-correlation-coefficient | Match |
| `result-hyenadna-enhancer-types-ft` | Table 1, row 'Enhancer Types', column 'HyenaDNA', FT value | .386 | ±.185 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h3-frozen` | Table 1, row 'H3', column 'HyenaDNA', frozen value | .6926 | ±.0158 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h3-ft` | Table 1, row 'H3', column 'HyenaDNA', FT value | .779 | ±.037 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h3k14ac-frozen` | Table 1, row 'H3K14ac', column 'HyenaDNA', frozen value | .3295 | ±.0132 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h3k14ac-ft` | Table 1, row 'H3K14ac', column 'HyenaDNA', FT value | .612 | ±.065 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h3k36me3-frozen` | Table 1, row 'H3K36me3', column 'HyenaDNA', frozen value | .3961 | ±.0095 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h3k36me3-ft` | Table 1, row 'H3K36me3', column 'HyenaDNA', FT value | .613 | ±.041 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h3k4me1-frozen` | Table 1, row 'H3K4me1', column 'HyenaDNA', frozen value | .3315 | ±.0107 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h3k4me1-ft` | Table 1, row 'H3K4me1', column 'HyenaDNA', FT value | .512 | ±.024 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h3k4me2-frozen` | Table 1, row 'H3K4me2', column 'HyenaDNA', frozen value | .2792 | ±.0079 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h3k4me2-ft` | Table 1, row 'H3K4me2', column 'HyenaDNA', FT value | .455 | ±.095 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h3k4me3-frozen` | Table 1, row 'H3K4me3', column 'HyenaDNA', frozen value | .2215 | ±.0100 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h3k4me3-ft` | Table 1, row 'H3K4me3', column 'HyenaDNA', FT value | .549 | ±.056 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h3k79me3-frozen` | Table 1, row 'H3K79me3', column 'HyenaDNA', frozen value | .5499 | ±.0085 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h3k79me3-ft` | Table 1, row 'H3K79me3', column 'HyenaDNA', FT value | .672 | ±.048 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h3k9ac-frozen` | Table 1, row 'H3K9ac', column 'HyenaDNA', frozen value | .4299 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h3k9ac-ft` | Table 1, row 'H3K9ac', column 'HyenaDNA', FT value | .581 | ±.061 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h4-frozen` | Table 1, row 'H4', column 'HyenaDNA', frozen value | .7267 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h4-ft` | Table 1, row 'H4', column 'HyenaDNA', FT value | .763 | ±.044 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-h4ac-frozen` | Table 1, row 'H4ac', column 'HyenaDNA', frozen value | .3041 | ±.0171 | matthews-correlation-coefficient | Match |
| `result-hyenadna-h4ac-ft` | Table 1, row 'H4ac', column 'HyenaDNA', FT value | .564 | ±.038 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-hyenadna-promoter-all-frozen` | Table 1, row 'Promoter All', column 'HyenaDNA', frozen value | .9329 | ±.0004 | f1-score | Match |
| `result-hyenadna-promoter-all-ft` | Table 1, row 'Promoter All', column 'HyenaDNA', FT value | .960 | ±.005 | f1-score | Match; spread type corrected |
| `result-hyenadna-promoter-non-tata-frozen` | Table 1, row 'Promoter Non-TATA', column 'HyenaDNA', frozen value | .9350 | ±.0016 | f1-score | Match |
| `result-hyenadna-promoter-non-tata-ft` | Table 1, row 'Promoter Non-TATA', column 'HyenaDNA', FT value | .959 | ±.008 | f1-score | Match; spread type corrected |
| `result-hyenadna-promoter-tata-frozen` | Table 1, row 'Promoter TATA', column 'HyenaDNA', frozen value | .9338 | ±.0000 | f1-score | Match |
| `result-hyenadna-promoter-tata-ft` | Table 1, row 'Promoter TATA', column 'HyenaDNA', FT value | .944 | ±.040 | f1-score | Match; spread type corrected |
| `result-hyenadna-splice-acceptor-frozen` | Table 1, row 'Splice Acceptor', column 'HyenaDNA', frozen value | .4752 | ±.0108 | f1-score | Match; source conflict noted |
| `result-hyenadna-splice-acceptor-ft` | Table 1, row 'Splice Acceptor', column 'HyenaDNA', FT value | .958 | ±.010 | f1-score | Match; spread type corrected |
| `result-hyenadna-splice-all-frozen` | Table 1, row 'Splice All', column 'HyenaDNA', frozen value | .5243 | ±.0051 | f1-score | Match |
| `result-hyenadna-splice-all-ft` | Table 1, row 'Splice All', column 'HyenaDNA', FT value | .956 | ±.011 | f1-score | Match; spread type corrected |
| `result-hyenadna-splice-donor-frozen` | Table 1, row 'Splice Donor', column 'HyenaDNA', frozen value | .7247 | ±.0087 | f1-score | Match; source conflict noted |
| `result-hyenadna-splice-donor-ft` | Table 1, row 'Splice Donor', column 'HyenaDNA', FT value | .949 | ±.024 | f1-score | Match; spread type corrected |
| `result-nt-enhancer-frozen` | Table 1, row 'Enhancer', column 'NT', frozen value | .5252 | ±.0262 | matthews-correlation-coefficient | Match; source conflict noted |
| `result-nt-enhancer-ft` | Table 1, row 'Enhancer', column 'NT', FT value | .548 | ±.144 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-enhancer-types-frozen` | Table 1, row 'Enhancer Types', column 'NT', frozen value | .5252 | ±.0262 | matthews-correlation-coefficient | Match; source conflict noted |
| `result-nt-enhancer-types-ft` | Table 1, row 'Enhancer Types', column 'NT', FT value | .424 | ±.132 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h3-frozen` | Table 1, row 'H3', column 'NT', frozen value | .6952 | ±.0111 | matthews-correlation-coefficient | Match |
| `result-nt-h3-ft` | Table 1, row 'H3', column 'NT', FT value | .784 | ±.047 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h3k14ac-frozen` | Table 1, row 'H3K14ac', column 'NT', frozen value | .3315 | ±.0068 | matthews-correlation-coefficient | Match |
| `result-nt-h3k14ac-ft` | Table 1, row 'H3K14ac', column 'NT', FT value | .551 | ±.021 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h3k36me3-frozen` | Table 1, row 'H3K36me3', column 'NT', frozen value | .3999 | ±.0160 | matthews-correlation-coefficient | Match |
| `result-nt-h3k36me3-ft` | Table 1, row 'H3K36me3', column 'NT', FT value | .625 | ±.013 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h3k4me1-frozen` | Table 1, row 'H3K4me1', column 'NT', frozen value | .3278 | ±.0152 | matthews-correlation-coefficient | Match |
| `result-nt-h3k4me1-ft` | Table 1, row 'H3K4me1', column 'NT', FT value | .550 | ±.021 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h3k4me2-frozen` | Table 1, row 'H3K4me2', column 'NT', frozen value | .2535 | ±.0128 | matthews-correlation-coefficient | Match |
| `result-nt-h3k4me2-ft` | Table 1, row 'H3K4me2', column 'NT', FT value | .319 | ±.045 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h3k4me3-frozen` | Table 1, row 'H3K4me3', column 'NT', frozen value | .2037 | ±.0227 | matthews-correlation-coefficient | Match |
| `result-nt-h3k4me3-ft` | Table 1, row 'H3K4me3', column 'NT', FT value | .410 | ±.033 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h3k79me3-frozen` | Table 1, row 'H3K79me3', column 'NT', frozen value | .5660 | ±.0085 | matthews-correlation-coefficient | Match |
| `result-nt-h3k79me3-ft` | Table 1, row 'H3K79me3', column 'NT', FT value | .672 | ±.048 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h3k9ac-frozen` | Table 1, row 'H3K9ac', column 'NT', frozen value | .3994 | ±.0155 | matthews-correlation-coefficient | Match |
| `result-nt-h3k9ac-ft` | Table 1, row 'H3K9ac', column 'NT', FT value | .562 | ±.040 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h4-frozen` | Table 1, row 'H4', column 'NT', frozen value | .7144 | ±.0084 | matthews-correlation-coefficient | Match |
| `result-nt-h4-ft` | Table 1, row 'H4', column 'NT', FT value | .799 | ±.025 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-h4ac-frozen` | Table 1, row 'H4ac', column 'NT', frozen value | .3025 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-nt-h4ac-ft` | Table 1, row 'H4ac', column 'NT', FT value | .495 | ±.032 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-nt-promoter-all-frozen` | Table 1, row 'Promoter All', column 'NT', frozen value | .9279 | ±.0042 | f1-score | Match |
| `result-nt-promoter-all-ft` | Table 1, row 'Promoter All', column 'NT', FT value | .976 | ±.006 | f1-score | Match; spread type corrected |
| `result-nt-promoter-non-tata-frozen` | Table 1, row 'Promoter Non-TATA', column 'NT', frozen value | .9373 | ±.0024 | f1-score | Match |
| `result-nt-promoter-non-tata-ft` | Table 1, row 'Promoter Non-TATA', column 'NT', FT value | .976 | ±.005 | f1-score | Match; spread type corrected |
| `result-nt-promoter-tata-frozen` | Table 1, row 'Promoter TATA', column 'NT', frozen value | .9182 | ±.0056 | f1-score | Match |
| `result-nt-promoter-tata-ft` | Table 1, row 'Promoter TATA', column 'NT', FT value | .966 | ±.013 | f1-score | Match; spread type corrected |
| `result-nt-splice-acceptor-frozen` | Table 1, row 'Splice Acceptor', column 'NT', frozen value | .8600 | ±.0012 | f1-score | Match |
| `result-nt-splice-acceptor-ft` | Table 1, row 'Splice Acceptor', column 'NT', FT value | .981 | ±.011 | f1-score | Match; spread type corrected |
| `result-nt-splice-all-frozen` | Table 1, row 'Splice All', column 'NT', frozen value | .6871 | ±.0083 | f1-score | Match |
| `result-nt-splice-all-ft` | Table 1, row 'Splice All', column 'NT', FT value | .983 | ±.008 | f1-score | Match; spread type corrected |
| `result-nt-splice-donor-frozen` | Table 1, row 'Splice Donor', column 'NT', frozen value | .8099 | ±.0054 | f1-score | Match |
| `result-nt-splice-donor-ft` | Table 1, row 'Splice Donor', column 'NT', FT value | .985 | ±.022 | f1-score | Match; spread type corrected |
| `result-omni-dna-enhancer-frozen` | Table 1, row 'Enhancer', column 'Omni-DNA', frozen value | .4947 | ±.0276 | matthews-correlation-coefficient | Match |
| `result-omni-dna-enhancer-ft` | Table 1, row 'Enhancer', column 'Omni-DNA', FT value | .593 | ±.005 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-enhancer-types-frozen` | Table 1, row 'Enhancer Types', column 'Omni-DNA', frozen value | .4129 | ±.0345 | matthews-correlation-coefficient | Match |
| `result-omni-dna-enhancer-types-ft` | Table 1, row 'Enhancer Types', column 'Omni-DNA', FT value | .498 | ±.001 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h3-frozen` | Table 1, row 'H3', column 'Omni-DNA', frozen value | .7220 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h3-ft` | Table 1, row 'H3', column 'Omni-DNA', FT value | .818 | ±.005 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h3k14ac-frozen` | Table 1, row 'H3K14ac', column 'Omni-DNA', frozen value | .3873 | ±.0052 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h3k14ac-ft` | Table 1, row 'H3K14ac', column 'Omni-DNA', FT value | .685 | ±.014 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h3k36me3-frozen` | Table 1, row 'H3K36me3', column 'Omni-DNA', frozen value | .4739 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h3k36me3-ft` | Table 1, row 'H3K36me3', column 'Omni-DNA', FT value | .661 | ±.013 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h3k4me1-frozen` | Table 1, row 'H3K4me1', column 'Omni-DNA', frozen value | .3790 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h3k4me1-ft` | Table 1, row 'H3K4me1', column 'Omni-DNA', FT value | .577 | ±.083 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h3k4me2-frozen` | Table 1, row 'H3K4me2', column 'Omni-DNA', frozen value | .2658 | ±.0143 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h3k4me2-ft` | Table 1, row 'H3K4me2', column 'Omni-DNA', FT value | .576 | ±.003 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h3k4me3-frozen` | Table 1, row 'H3K4me3', column 'Omni-DNA', frozen value | .2512 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h3k4me3-ft` | Table 1, row 'H3K4me3', column 'Omni-DNA', FT value | .587 | ±.222 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h3k79me3-frozen` | Table 1, row 'H3K79me3', column 'Omni-DNA', frozen value | .5621 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h3k79me3-ft` | Table 1, row 'H3K79me3', column 'Omni-DNA', FT value | .718 | ±.027 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h3k9ac-frozen` | Table 1, row 'H3K9ac', column 'Omni-DNA', frozen value | .4545 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h3k9ac-ft` | Table 1, row 'H3K9ac', column 'Omni-DNA', FT value | .658 | ±.029 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h4-frozen` | Table 1, row 'H4', column 'Omni-DNA', frozen value | .7501 | ±.0000 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h4-ft` | Table 1, row 'H4', column 'Omni-DNA', FT value | .802 | ±.002 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-h4ac-frozen` | Table 1, row 'H4ac', column 'Omni-DNA', frozen value | .3222 | ±.0167 | matthews-correlation-coefficient | Match |
| `result-omni-dna-h4ac-ft` | Table 1, row 'H4ac', column 'Omni-DNA', FT value | .663 | ±.029 | matthews-correlation-coefficient | Match; spread type corrected |
| `result-omni-dna-promoter-all-frozen` | Table 1, row 'Promoter All', column 'Omni-DNA', frozen value | .9524 | ±.0000 | f1-score | Match |
| `result-omni-dna-promoter-all-ft` | Table 1, row 'Promoter All', column 'Omni-DNA', FT value | .973 | ±.002 | f1-score | Match; spread type corrected |
| `result-omni-dna-promoter-non-tata-frozen` | Table 1, row 'Promoter Non-TATA', column 'Omni-DNA', frozen value | .9539 | ±.0000 | f1-score | Match |
| `result-omni-dna-promoter-non-tata-ft` | Table 1, row 'Promoter Non-TATA', column 'Omni-DNA', FT value | .972 | ±.016 | f1-score | Match; spread type corrected |
| `result-omni-dna-promoter-tata-frozen` | Table 1, row 'Promoter TATA', column 'Omni-DNA', frozen value | .9539 | ±.0000 | f1-score | Match |
| `result-omni-dna-promoter-tata-ft` | Table 1, row 'Promoter TATA', column 'Omni-DNA', FT value | .967 | ±.001 | f1-score | Match; spread type corrected |
| `result-omni-dna-splice-acceptor-frozen` | Table 1, row 'Splice Acceptor', column 'Omni-DNA', frozen value | .8147 | ±.0049 | f1-score | Match |
| `result-omni-dna-splice-acceptor-ft` | Table 1, row 'Splice Acceptor', column 'Omni-DNA', FT value | .968 | ±.002 | f1-score | Match; spread type corrected |
| `result-omni-dna-splice-all-frozen` | Table 1, row 'Splice All', column 'Omni-DNA', frozen value | .4221 | ±.0000 | f1-score | Match |
| `result-omni-dna-splice-all-ft` | Table 1, row 'Splice All', column 'Omni-DNA', FT value | .927 | ±.025 | f1-score | Match; spread type corrected |
| `result-omni-dna-splice-donor-frozen` | Table 1, row 'Splice Donor', column 'Omni-DNA', frozen value | .8082 | ±.0054 | f1-score | Match |
| `result-omni-dna-splice-donor-ft` | Table 1, row 'Splice Donor', column 'Omni-DNA', FT value | .951 | ±.007 | f1-score | Match; spread type corrected |
