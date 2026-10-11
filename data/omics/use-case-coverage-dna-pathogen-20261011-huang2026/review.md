# Review: use-case-coverage-dna-pathogen-20261011-huang2026, 2026-10-11

Reviewer: Claude (Opus 5.5) review agent `reviewer-path`, separate from the extracting agent `uc-pathogens`. No human review claimed. Source transcription is not reproduction. The full review, covering all five pathogen batches, is `docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md`.

## Reviewer's report (verbatim)

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-dna-pathogen-20261011-huang2026` | Approved with corrections (G1 to G6) |

### Huang et al. 2026

G1. Author overlap is understated. Two authors, Dejian Gu and Hao Liu (Aff6), are affiliated with Geneplus-Beijing. Replace

`One co-author is affiliated with Geneplus-Beijing, which supplies the bstNGS probes and analysis kits; the article declares no competing interests.`

with

`Two co-authors (Dejian Gu and Hao Liu) are affiliated with Geneplus-Beijing, which supplies the bstNGS probes and analysis kits; the article declares no competing interests.`

in `limitations` of all four evaluations (`dna-pathogen-20261011-huang2026-eval-{bstngs,mngs,cmt,culture}`) and in `sources.md`. In `use-case-mapping-dna-pathogen-20261011-huang2026-clinical-diagnosis` replace the limitation `Commercial assay with a co-author from its supplier; no competing interests declared.` with `Commercial assay with two co-authors from its supplier (Geneplus-Beijing); no competing interests declared.`

G2. The reference wording is weaker than the source. Methods 'Sample enrollment and standard-of-care microbiology testing' paragraph 3 says "the composite reference standard was established primarily based on BALF mNGS and CMT results", and the Table 2 footnote says the same. CMTs is both a scored column and part of the reference. Replace the first limitation of `dna-pathogen-20261011-huang2026-protocol-clinical-diagnosis` with

`Incorporation bias: the reference was established primarily from BALF mNGS and CMT results (Methods 'Sample enrollment and standard-of-care microbiology testing' paragraph 3; Table 2 footnote), with clinical adjudication. CMTs is scored against a reference that contains it, which favours CMTs, and BALF mNGS is a sequencing assay on a different specimen.`

and replace the judgement limitation `Incorporation bias: NGS and CMT results are part of the reference diagnosis.` with the same text. Replace the evaluation limitation `The reference diagnosis incorporates NGS and CMT results.` (four evaluations) with `The reference was established primarily from BALF mNGS and CMT results, so CMTs is scored against a reference that contains it.`

G3. In the judgement `rationale`, replace `the specimens are whole-blood cfDNA for pneumonia-associated sepsis` with `the specimens are plasma microbial cell-free DNA in pneumonia-associated sepsis`. The source says plasma samples (inclusion criterion 4) and mcfDNA; "whole-blood" is not stated.

G4. The count of reference-negative patients is not printed. In the judgement, replace the limitation `Only 18 patients are reference-negative overall (specificity denominators are small; specificity 44.44% for bstNGS with a 24.56% to 66.28% interval).` with `Few patients are reference-negative: the count is not printed, and the specificity intervals are wide (44.44% for bstNGS, 24.56% to 66.28%).`

G5. Result `dna-pathogen-20261011-huang2026-result-fungal-culture-ppv`: set `numeric_value` to `null`, add `"missing_metadata": {"uncertainty": {"reason": "unreported"}, "numeric_value": {"reason": "inapplicable", "note": "PPV is undefined: blood culture had no positive call in this stratum (sensitivity 0.00%, specificity 100.00%); the printed 0.00% is not interpreted"}}` (keep any existing `missing_metadata` keys), and append to `source_anomaly`: ` Independent review 2026-10-11: numeric_value set to null so the undefined value is not ranked as zero; printed_value and the printed interval are kept.` This follows the Carbo et al. 2022 precedent (`rna-pathogen-20261009-result-carbo2022-family-cutoff-0-clark-excl-human-npv`). Keep `uncertainty` as printed.

G6. Whitespace exactness (minor). The source cells use U+2009 (thin space) after U+2212 in every interval and between `<` and `0.0001`. Replace `− ` with `− ` in `uncertainty.printed` of all 80 results, and set `reported_p_value` to `< 0.0001` on `all-mngs-accuracy`, `all-culture-accuracy`, `gnb-mngs-accuracy` and `gnb-culture-accuracy` (IDs prefixed `dna-pathogen-20261011-huang2026-result-`). Add to the note on each of the 16 results carrying `reported_p_value`: `McNemar test against blood-bstNGS with Bonferroni adjustment (Table 2 footnote); attached to accuracy following Results paragraph 4.` Also make `claims.csv` `printed_value` equal the result's `printed_value` (it currently carries the full cell text with the interval, unlike the other four batches).

## Corrections applied

Applied by the extractor as the reviewer specified, before the batch was added to the store.

1. G1: the Geneplus authorship limitation on the four evaluations names Dejian Gu and Hao Liu; the judgement limitation replaced with the reviewer's text; sources.md updated.
2. G2: the incorporation-bias limitation replaced on the protocol and the judgement, and the evaluation limitation replaced, with the reviewer's text.
3. G3: 'whole-blood cfDNA' replaced by 'plasma microbial cell-free DNA' in the judgement rationale.
4. G4: the reference-negative limitation replaced with the reviewer's text.
5. G5: result fungal-culture-ppv: numeric_value set to null and the reviewer's sentence appended to source_anomaly. The store rejects a missing_metadata key for an attribute that is present (numeric_value: null) and for uncertainty, which the reviewer said to keep, so the reviewer's numeric_value reason is recorded under missing_metadata.value, as in the cnv-20261009 NA results, and no missing_metadata.uncertainty entry is added.
6. G6: the parser now keeps U+2009 exactly, so all 80 uncertainty.printed values and the four '< 0.0001' p values carry the thin space; the reviewer's McNemar note is on the 16 results with reported_p_value; claims.csv printed_value equals the result printed_value.
7. All records set to source_checked. Each result, descriptive claim and judgement carries the reviewer's review block (method, reviewer, reviewer_note, date and note as specified; the extraction note moved to method_note). Each judgement lists the reviewer's reviewed_evaluations.
8. Corrections were applied in the extraction script under extract/, and batch.jsonl, claims.csv, coverage.json, sources.md and research.md were regenerated.

## Records after correction

- claim: 2
- configuration: 4
- dataset: 1
- evaluation: 4
- method: 4
- protocol: 1
- result: 80
- source: 1
