# Review: pathogen use-case batches, 2026-10-11

Reviewer: Claude (Opus 5.5) review agent `reviewer-path`, separate from the extracting agent `uc-pathogens`. No human review is claimed. Nothing was executed or reproduced. I did not edit any record, store file or batch file; all corrections below are for the collector to apply.

Worktree reviewed: `rewire-benchmark-data-lit-uc-pathogens`, batch folders as the source of truth.

## Verdicts

| Batch | Verdict |
| --- | --- |
| `use-case-coverage-dna-pathogen-20261011-hu2026` | Approved with corrections (H1 to H3) |
| `use-case-coverage-dna-pathogen-20261011-huang2026` | Approved with corrections (G1 to G6) |
| `use-case-coverage-dna-pathogen-20261011-wolf2026` | Approved with corrections (W1 to W4) |
| `use-case-coverage-rna-pathogen-20261011-tisza2026` | Approved with corrections (T1 to T4) |
| `use-case-coverage-rna-pathogen-20261011-sanderson2026` | Approved with corrections (S1 to S3) |
| `bray-curtis-dissimilarity` (data/vocab/metric.ttl) | Approved as written |
| DNA and RNA summary proposals | Approved with the corrected text below |

Every printed value in all five batches matches the pinned source. No value needs a superseding record. The corrections are to descriptive text, relevance, two qualifiers, one numeric_value and two result-level notes.

## Corrections

All edits are to records in the batch folders before `records -- add`. After applying them, regenerate `claims.csv` and `coverage.json` from the batch as the extraction scripts do.

### Hu et al. 2026

H1. Author overlap is understated. Eight of the listed authors (Hui Miao, Jianpo Zheng, Dongdan Zhang, Weiqing Guo, Peng Hu, Rui Han, Jing Wang and co-corresponding author Lifeng Li) are affiliated with Genskey Medical Technology (aff3), not one. Replace the string

`One co-corresponding author is affiliated with Genskey Medical Technology, a clinical mNGS provider; the article states that the authors declare no conflict of interest. The workflows are the authors' own, so the evaluations are author_reported.`

with

`Eight of the listed authors, including co-corresponding author Lifeng Li, are affiliated with Genskey Medical Technology (Beijing), a clinical mNGS provider; the article states that the authors declare no conflict of interest. The workflows are the authors' own, so the evaluations are author_reported.`

in `attributes.limitations` of all six evaluations (`dna-pathogen-20261011-hu2026-eval-{culture,cmt,crs}-{mgi,hdont}`) and of the three judgements (`use-case-mapping-dna-pathogen-20261011-hu2026-{culture,cmt,crs}`). Make the same change in `sources.md` ("Authorship and origin").

H2. The CMT reference uses discrepant analysis: qPCR or GeneXpert verification was run on sequencing-positive, culture-negative findings (19 NGS-positive and 17 TGS-positive findings confirmed, Results 'Diagnostic performance for clinical samples' paragraph 2). Append to `limitations` of `dna-pathogen-20261011-hu2026-protocol-cmt` and of `use-case-mapping-dna-pathogen-20261011-hu2026-cmt`:

`Discrepant analysis: confirmatory qPCR or GeneXpert was run on discordant sequencing-positive findings where residual BALF allowed (19 NGS-positive and 17 TGS-positive findings confirmed), so the CMT reference depends partly on the sequencing results and favours the sequencing workflows.`

H3. Append to `limitations` of `use-case-mapping-dna-pathogen-20261011-hu2026-crs`:

`The use case's exclusion of sensitivity against a composite or adjudicated reference was recorded for the Karius source's composite endpoint; this composite reference from a different source is recorded as proxy evidence only, because it is built partly from the scored workflows' own calls.`

No change to the 79.2% result (question 1 below).

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

### Wolf et al. 2026

W1. Relevance of `use-case-mapping-dna-pathogen-20261011-wolf2026-diagnosis`: set `relevance` to `proxy` (question 4). Replace `rationale` with

`Diagnostic sensitivity of the Karius plasma cell-free DNA assay against blood-culture organisms at bloodstream infection onset matches the use case's inputs and endpoint (agreement with blood culture for plasma microbial cell-free DNA), measured prospectively in a second population. It is proxy evidence for the same reason as the Karius anchor: blood culture does not identify every infection, so this is agreement with culture, not sensitivity against all infections. The population is children and young adults with high-risk leukaemia, and Karius took part in processing and analysis.`

and in `reason` delete the sentence `The direct relevance is a proposal.`

W2. `dna-pathogen-20261011-wolf2026-protocol-specificity`: replace `protocol` with

`Proportion of evaluable control samples (no fever or documented infection in the 7 days before or after collection) in which mcfDNA-Seq detected no bacterium or yeast (moulds, viruses and parasites excluded a priori; Burkholderia cepacia excluded afterwards for possible local contamination), or no common bloodstream infection pathogen; with all positive tests and with the post-hoc 140 molecules per microlitre cut-off. 95% CIs as printed. The laboratory was masked to sample status.`

set `version` to `Table 3`, and replace `limitations` with `["Control samples come from the same high-risk leukaemia population and are not patients tested for suspected infection.", "The 140 molecules per microlitre cut-off was chosen post hoc by maximising Youden's index on the consolidated data."]`.

W3. Set `version` to `Table 2` on `dna-pathogen-20261011-wolf2026-protocol-prediction` and `dna-pathogen-20261011-wolf2026-protocol-diagnosis`.

W4. In the three Wolf judgements, replace the limitation `Karius provided testing and took part in processing, analysis and data management; one author is a Karius employee.` with `Karius provided testing and took part in sample processing and analysis, data management and manuscript review; one author (AAA) is a Karius employee and coinventor on a pending Karius patent, and two others report research or sequencing support from Karius.`

### Tisza et al. 2026 (EsViritu)

T1. Divergence-capped truth: the Results ('EsViritu is an accurate profiler of mock virus communities' paragraph 2) say "only the 'one-per-family' mock communities were measured in the divergence-capped metrics", while Methods 'Mock communities' says "All six communities were analyzed together" and the S9 caption says "across mock communities". The 15 capped results say "mean over six mock communities". For each of `rna-pathogen-20261011-tisza2026-result-mock-{centrifuger,esviritu,kraken2,metabuli,sylph}-capped-{f1,bray-curtis,pearson}`, replace `mean over six mock communities` with `mean over mock communities` in `metric_qualifier`, and add

`"source_anomaly": "Results 'EsViritu is an accurate profiler of mock virus communities' paragraph 2 says only the three one-per-family communities were measured in the divergence-capped metrics; Methods 'Mock communities' says all six communities were analysed together, and the Supplemental Table S9 caption says 'across mock communities'. The number of communities behind this mean is not certain. Value kept as printed."`

Append to `limitations` of `rna-pathogen-20261011-tisza2026-protocol-mock` and of `use-case-mapping-rna-pathogen-20261011-tisza2026-mock`: `Under divergence-capped truth the Results say only the three one-per-family communities were scored, while Methods say all six were analysed together; the capped means may cover three communities.`

T2. `comparison.inputs` on the ten pos and mock evaluations is wrong (it describes the negative-control libraries). Set it to `Synthetic read pairs (bbtools randomreads.sh)` on `rna-pathogen-20261011-tisza2026-eval-pos-{centrifuger,esviritu,kraken2,metabuli,sylph}` and to `Synthetic NovaSeq read pairs (InSilicoSeq)` on `rna-pathogen-20261011-tisza2026-eval-mock-{centrifuger,esviritu,kraken2,metabuli,sylph}`. Keep the neg evaluations as they are (Table S16 confirms one ONT library).

T3. The Results paragraph 4 of 'EsViritu reaches read-level sensitivity' prints model-estimated probabilities (EsViritu 0.995, Metabuli 0.99996, Sylph 1.8 × 10^-3) and odds ratios (for example Sylph 6.4 × 10^-8) that match neither Supplemental Table S2 nor the S3 contrasts (Sylph/EsViritu 2.3 × 10^-5 at 10 read pairs). Add to each of the ten `rna-pathogen-20261011-tisza2026-result-pos-*` results:

`"source_anomaly": "Results 'EsViritu reaches read-level sensitivity while avoiding false positives' paragraph 4 prints detection probabilities (EsViritu 0.995, Metabuli 0.99996, Sylph 1.8 x 10^-3) and odds ratios that do not match Supplemental Tables S2 and S3; the text appears to describe a different fit. Value is the S2 marginal mean as printed."`

T4. Append to `limitations` of `rna-pathogen-20261011-tisza2026-protocol-pos`: `The S2 caption does not name the parameter setting; the Results tie the regression to the headline parameters, so the results are attached to the headline configurations.`

### Sanderson et al. 2026

S1. Relevance of `use-case-mapping-rna-pathogen-20261011-sanderson2026-validation`: set `relevance` to `proxy` (question 4). Replace `rationale` with

`A prospective validation of one RNA metagenomic workflow on respiratory swabs, scored as target-level sensitivity and specificity against the original clinical PCR, with thresholds fixed on a separate derivation set, matches the use case's inputs (nuclease-treated respiratory RNA, reverse-transcribed) and its output (sensitivity against original clinical testing for one respiratory mNGS assay). It is proxy evidence for the same reason as the UCSF anchor: agreement with the clinical PCR panel is not sensitivity against all infections, and samples were selected by PCR result. It compares detection criteria within one workflow, not different workflows.`

and in `reason` delete `; the direct relevance is a proposal`.

S2. Add two limitations the judgement misses (Methods 'Respiratory samples for pathogen detection' paragraph 1 and 'Procedures' paragraph 4). Append to `limitations` of the judgement and of `rna-pathogen-20261011-sanderson2026-protocol-validation`:

`Spectrum bias: inclusion required a pathogen detected at Ct or Cn 30 or below on the four-target assays, or FilmArray testing, with about one FilmArray-negative sample collected per eight positive samples; sensitivity and specificity are not estimates for unselected swabs.`

`Reads were mapped only to a curated database of the 23 PCR-panel pathogens, so the study does not measure detection of organisms outside the panel or false calls outside it.`

S3. On `rna-pathogen-20261011-sanderson2026-result-prespecified-specificity`, append to `source_anomaly`: ` Independent review 2026-10-11: both counts give 99.8%; the result-level note is sufficient and no source-level concern is raised.` On `rna-pathogen-20261011-sanderson2026-result-alternative-sensitivity`, append: ` Independent review 2026-10-11: 159/274 = 58.0% and 159/260 = 61.2% are each arithmetically consistent with the printed percentages; the 274 denominator appears to include the DNA targets that the 61% result excludes, and 'samples' in that sentence appears to mean targets. Kept as printed with this note.`

## Answers to the collector's questions

1. Hu Table 2 HD-ONT NPA against CMT (79.2% printed, counts give 42/52 = 80.8%). The value is printed twice (Table 2 and Results paragraph 2), so it is the authors' figure. Keep the result-level `source_anomaly`; no dispute and no source concern. A dispute would withhold the whole CMT judgement for a 1.6-point arithmetic slip that the counts beside it expose.
2. Sanderson specificity (Abstract 3836/3845, Results 3901/3910). Both are 99.8%. A result-level note is enough (S3). A source-level concern would withhold the judgement for a discrepancy that does not change the printed percentage.
3. Sanderson 159/274. Keep as printed with the note in S3.
4. Direct relevance. Change both to `proxy` (W1, S1). The existing anchors (Karius, UCSF) are proxy because their references (blood culture, the clinical PCR panel) do not identify every infection; Wolf and Sanderson use the same kinds of reference, and Sanderson also selected samples by PCR result. Proxy keeps the use case consistent and needs no scope change.
5. Incorporation bias wording. Hu CRS wording is correct; add the CMT discrepant-analysis limitation (H2). Huang wording understates the source; use G2.
6. Developer involvement. All 29 evaluations are correctly `author_reported`; none qualifies as `independent_paper`. Author overlap was understated for Hu (eight Genskey authors, H1) and Huang (two Geneplus authors, G1). Wolf disclosures are now complete (W4). EsViritu: all five authors are the developers. Sanderson: the authors' own workflow, no competing interests declared.
7. EsViritu S2 as `recall` with a "model-estimated" qualifier is acceptable; the protocol says they are Firth marginal means, not observed proportions. Add T3 and T4. Shortest round-trip decimals are acceptable as the printed form of an XLSX number with no display format; my parser reproduced every one (Python `repr` of the stored double, written in positional notation).
8. Huang fungal blood-culture PPV: keep printed, set `numeric_value` null (G5). Attaching the p values to accuracy follows Results paragraph 4 and is acceptable with the note in G6.
9. EsViritu judgements on the DNA use case: keep both, as proxy. The positive controls are the only evidence in either use case on organisms poorly represented in the reference (four of the seven genomes are Genomoviridae, DNA viruses), and the negative controls include human genome reads. Their limitations already say viral-only and developer-run.
10. `bray-curtis-dissimilarity`: approved. The definition is correct (sum of absolute differences over the sum of both profiles), direction `lower` is right, and no existing concept respells it. On profiles normalised to relative abundance it equals half the L1 distance, so it is related to `composition-l1-distance` but not the same quantity or scale. Leaving it unmapped is correct; I did not check external ontologies, so no external match should be added without that check.
11. The 13 `assessed_by` links: approved for the integrator to add after the corrections, with the relevance values as corrected (all 13 proxy).

## Judgement review

All 13 judgements hold after the corrections above: each endpoint matches what the protocol measures, proxy is justified, the limitations carry the sources' caveats once H1 to H3, G1 to G4, W1 to W4, T1 and T4, S1 and S2 are applied, and no judgement uses `excluded_evaluations`. `reviewed_evaluations` for each:

| Judgement | reviewed_evaluations |
| --- | --- |
| `use-case-mapping-dna-pathogen-20261011-hu2026-culture` | `dna-pathogen-20261011-hu2026-eval-culture-hdont`, `dna-pathogen-20261011-hu2026-eval-culture-mgi` |
| `use-case-mapping-dna-pathogen-20261011-hu2026-cmt` | `dna-pathogen-20261011-hu2026-eval-cmt-hdont`, `dna-pathogen-20261011-hu2026-eval-cmt-mgi` |
| `use-case-mapping-dna-pathogen-20261011-hu2026-crs` | `dna-pathogen-20261011-hu2026-eval-crs-hdont`, `dna-pathogen-20261011-hu2026-eval-crs-mgi` |
| `use-case-mapping-dna-pathogen-20261011-huang2026-clinical-diagnosis` | `dna-pathogen-20261011-huang2026-eval-bstngs`, `-eval-cmt`, `-eval-culture`, `-eval-mngs` (prefix `dna-pathogen-20261011-huang2026`) |
| `use-case-mapping-dna-pathogen-20261011-wolf2026-diagnosis` | `dna-pathogen-20261011-wolf2026-eval-diagnosis` |
| `use-case-mapping-dna-pathogen-20261011-wolf2026-prediction` | `dna-pathogen-20261011-wolf2026-eval-prediction` |
| `use-case-mapping-dna-pathogen-20261011-wolf2026-specificity` | `dna-pathogen-20261011-wolf2026-eval-specificity-all`, `dna-pathogen-20261011-wolf2026-eval-specificity-cutoff140` |
| `use-case-mapping-dna-pathogen-20261011-tisza2026-pos` and `use-case-mapping-rna-pathogen-20261011-tisza2026-pos` | `rna-pathogen-20261011-tisza2026-eval-pos-{centrifuger,esviritu,kraken2,metabuli,sylph}` |
| `use-case-mapping-dna-pathogen-20261011-tisza2026-neg` and `use-case-mapping-rna-pathogen-20261011-tisza2026-neg` | `rna-pathogen-20261011-tisza2026-eval-neg-{centrifuger,esviritu,kraken2,metabuli,sylph}` |
| `use-case-mapping-rna-pathogen-20261011-tisza2026-mock` | `rna-pathogen-20261011-tisza2026-eval-mock-{centrifuger,esviritu,kraken2,metabuli,sylph}` |
| `use-case-mapping-rna-pathogen-20261011-sanderson2026-validation` | `rna-pathogen-20261011-sanderson2026-eval-prespecified`, `rna-pathogen-20261011-sanderson2026-eval-alternative` |

Review object for each result, claim and judgement (fill per batch with that batch's artifact hash and URL from its `source` record; for the Hu and Tisza supplement results use the supplement's hash and URL):

- `method`: results with table sources `["source-hash-verification", "deterministic-table-parse", "independent-cell-check"]`; Sanderson results and all descriptive claims and judgements `["source-hash-verification", "independent-cell-check", "scope-review"]` (drop `scope-review` for results)
- `reviewer`: `["claude"]`
- `reviewer_note`: `Separate Claude review agent (reviewer-path), independent of the extractor; no human review claimed`
- `date`: `2026-10-11`
- `note`: `Re-downloaded the pinned artifact and matched its SHA-256; compared every value with a separate stdlib parser written for this review (the extractor's script was not run) and checked a stratified sample by hand against the rendered table.` Add the batch-specific correction note where one applies.

## Approved summary text

Apply only after the judgements above are reviewed and pinned. Every number traces to a stored result: the Karius, Portik, Hall and Coin, Carbo, de Vries, Meyer and UCSF figures to the existing reviewed summaries' results, the rest to results in these batches.

### use-case-diagnostic-dna-pathogen-identification

> Most workflow comparisons in the reviewed evidence use mock communities or constructed metagenomes. Two compare workflows on patient specimens, and in both the reference standard draws partly on sequencing: in Hu et al. 2026 only the culture comparison is independent of the sequencing results, and in Huang et al. 2026 the reference was built mainly from BALF mNGS and the conventional tests that are themselves scored. Both are author-reported and have co-authors from sequencing companies (Genskey Medical Technology for Hu; Geneplus-Beijing, which supplies the targeted assay's probes, for Huang). For the Karius plasma cell-free DNA assay, the developers report 93.7% (59 of 63) agreement with initial blood culture in a sepsis-alert cohort, and blood culture does not detect every infection. A prospective study in children and young adults with high-risk leukaemia, with Karius taking part in sample processing and analysis, found every blood-culture organism in 81.3% (65 of 80) of evaluable bloodstream infection episodes on the day of or after onset and in 51.9% (42 of 81) during the three days before; 82.7% (134 of 162) of control samples from patients without fever or infection had no bacterium or yeast detected. In 62 bronchoalveolar lavage specimens (Hu et al. 2026), a short-read MGI workflow and a host-depleted nanopore workflow both had 95.2% positive agreement with culture but 44.6% and 46.4% negative agreement, because they found organisms culture did not; against a composite reference that adds organisms found by both workflows, positive agreement was 93.3% and 90.7%. In 122 intensive-care patients with pneumonia-associated sepsis (Huang et al. 2026), a targeted probe-capture assay on plasma had 63.46% sensitivity against the reference diagnosis, against 35.58% for untargeted blood mNGS, 49.04% for conventional tests and 9.62% for blood culture, with specificity of 44.44% and 61.11% for the two blood sequencing assays. In mock communities (Portik et al. 2022), Kraken2 and Bracken called 44 to 204 absent species at a 0.001% read threshold (precision 0.05 to 0.21), while long-read MEGAN-LR and BugSeq-V2 called 0 to 2; the first author is a PacBio employee. In seven pathogen-free libraries scored against one shared virus database by the EsViritu developers (preprint), the median number of false virus species was 0 for EsViritu, Centrifuger and Sylph, 6 for Kraken2 and 18 for Metabuli. For M. tuberculosis reads in constructed metagenomes (Hall and Coin 2024), kraken with its standard database classified 0.07 to 0.74 of the M. tuberculosis reads as M. tuberculosis, against 0.97 to 0.995 with a Mycobacterium database. Each study used its own reference database and reporting rules, and none of these results is clinical validation.

Changes from the draft: the claim that culture is the only non-sequencing reference "in both" was wrong for Huang (culture there is a scored comparator, not a reference); industry co-authorship for Hu and Huang added; "afebrile" replaced by the source's definition and the count added; "among 18 reference-negative patients" removed (not printed); Lancet decimal points normalised; "the clinical diagnosis used the sequencing results" replaced by the source's statement; "on blood" changed to "on plasma"; the Hall and Coin wording restored to the reviewed summary's.

### use-case-diagnostic-rna-pathogen-detection

> The single-assay results are a UCSF respiratory RNA metagenomic assay at 93.6% (103 of 110) sensitivity against original clinical respiratory panel testing, as reported by its developers, and the developers' own prospective validation of an Oxford nanopore workflow on 344 nasopharyngeal swabs (preprint). With thresholds fixed on a separate derivation set, the nanopore workflow detected 51% (133 of 260) of PCR-positive targets in the samples passing quality control, from 85% for RSV to 19% for rhinovirus/enterovirus, and 99.8% of PCR-negative targets were not detected; criteria chosen after the validation raised sensitivity to 58%, and the authors attributed all nine false positives to barcode crossover. Its swabs were selected mostly as PCR-positive at Ct 30 or below, with about one negative per eight positives, and reads were matched only to the 23 panel pathogens, so it does not test detection outside the panel. Three comparisons of several workflows add proxy evidence. On 88 nasal washings scored against 1144 respiratory virus PCR results (Carbo et al. 2022), all five classifiers detected 22 or 23 of the 24 PCR-positive results at species level at a read-count cut-off chosen on the same data, but 31% to 58% of their positive calls were PCR-negative. When 13 European clinical virology laboratories each ran their own pipeline on the same 13 clinical datasets (de Vries et al. 2021, preprint), 10 to 13 samples were correctly called positive, and the three pipelines that found every sample reported 6, 2 and 0 additional PCR-negative viruses. In the CAMI II blood metagenome challenge (Meyer et al. 2022), 4 of 10 submissions listed the causal virus. In a developer benchmark of five virus profilers on one shared database (Tisza et al. 2026, preprint), the model-estimated probability of reporting the correct family for reads from seven divergent viruses at 10 read pairs was 0.974 for EsViritu and 0.9998 for Metabuli but 0.045 for Kraken2, 0.012 for Centrifuger and 0.0009 for Sylph at the authors' headline settings, and Metabuli reported a median of 18 false species in seven pathogen-free libraries against 0 for EsViritu. None of this is clinical validation: the cohorts are small or single-site, reference databases and reporting rules differ, and the benchmark data are mostly synthetic.

Changes from the draft: Sanderson named as developer-reported; its sample selection and panel-limited database added (truth-set and spectrum bias); specificity stated without the conflicting counts; the EsViritu probability described as family-level detection of seven divergent genomes.

## Approved use-case field changes

No change to `inputs`, `exclusions`, `output`, `decision`, `setting` or `clinical_scope` of either use case. Add the 13 `assessed_by` links listed in the batches' `coverage.json`.

Evidence gaps are not pinned (docs/use-cases.md, Pins), so one stale gap may be updated. In `use-case-diagnostic-dna-pathogen-identification` `evidence_gaps`, replace

`The multi-tool evidence is from mock communities (Portik et al. 2022) or constructed metagenomes (Hall and Coin 2024); the only patient-sample comparison (Song et al. 2025) has five culture-positive samples of one organism group and prints relative abundances, not detection calls.`

with

`Patient-specimen comparisons of workflows (Hu et al. 2026 on BALF, Huang et al. 2026 on plasma) score against references that draw partly on sequencing; only Hu's culture comparison is independent of it. Song et al. 2025 has five culture-positive samples of one organism group and prints relative abundances, not detection calls.`

This is optional; the integrator may leave the gaps as they are.

## Checks run and outcomes

Sources and hashes. Each artifact was re-downloaded into its own scratch folder and hashed (2026-10-11, about 23:29 UTC):

| Source ID | Re-download SHA-256 | Outcome |
| --- | --- | --- |
| `dna-pathogen-20261011-hu2026-source` | `555995fd870d878dd0e6c112064bbf1d2535a1cb1af17f70570ecc11774caa2d` | Match |
| `dna-pathogen-20261011-hu2026-source-supp` | `7ab6c2cde30619e506a5e015ef5bbb253dfa6359ebd56140577eef136b153ed9` (DOCX member; the ZIP hash differs per request, as recorded) | Match |
| `dna-pathogen-20261011-huang2026-source` | `79b237d733d9ad3af33722c30013afb0539adf03098ca1e1c2f18344bcc4a67d` | Match |
| `dna-pathogen-20261011-wolf2026-source` | `0f6905d0a0c9ace686bcc61970c711558ccf530b5c31f882607a305f8b5ca689` | Match |
| `rna-pathogen-20261011-tisza2026-source` | `fd92099655ddefdec31d35e273b80c4b233eed395c1cfc137eaddaa4efee232b` | Match (the recorded URL returns HTTP 301 to `/content/biorxiv/early/...`) |
| `rna-pathogen-20261011-tisza2026-source-supp` | `0559022a3ff5ef5b2682e3c451eda51835c4c8d9be9dfdb1ebc9cd9295fb7701` | Match |
| `rna-pathogen-20261011-sanderson2026-source` | `c0bc5c035742f53fe291e08b9d956102e102fd743a55de503f00bcaead36a7e2` | Match (recorded URL returns HTTP 301 to `/content/medrxiv/early/...`) |

All four archived gzip copies hash to their recorded gzip SHA-256 and decompress to the recorded raw hash.

Automated full comparison. I wrote separate stdlib parsers (ElementTree for the JATS and DOCX, a minimal OOXML reader for the XLSX); the extractor's scripts were not run. Each asserts the header and row labels and compares `printed_value`, `numeric_value`, metric, interval bounds, numerator and denominator.

| Batch | Cells in chosen tables | Matched | Missed | Mismatched |
| --- | --- | --- | --- | --- |
| Hu (Table 2, S6, S7) | 108 | 108 | 0 | 0 |
| Huang (Table 2, with intervals and p values) | 80 | 80 | 0 | 0 (4 p values differ only in U+2009 whitespace, G6) |
| Wolf (Tables 2 and 3) | 44 | 44 | 0 | 0; all 12 sensitivities and 4 specificities equal numerator/denominator to one decimal |
| Tisza (S2, S6, S9) | 105 | 105 | 0 | 0; every printed value equals the shortest round-trip decimal of the stored double; all 12 NA cells are NA with null numeric_value |
| Sanderson (Results text) | 14 | 14 | 0 | 0; every quoted fragment occurs in the cited paragraph and contains the printed value, interval and fraction |

Hand check against the rendered tables. A seeded random sample (seed 20261011) was printed beside the source table and checked by eye: Hu 40 of 108 (Table 2, S6 and S7, both workflows, all three references, all six cell types); Huang 40 of 80 (all four strata, all four methods, all five metrics); Wolf 40 of 44 (both tables, both periods, both data treatments, all three groups); Tisza 42 of 105 (S2, S6 and S9, all five tools, all ranks and truth modes, NA cells); Sanderson all 14. All agreed. Arithmetic checked by hand: every Hu PPA and NPA against its counts (all agree except the known 79.2%); Huang's specificities are consistent with 18 negatives but that count is not printed.

Metric, qualifier, direction, unit, uncertainty, denominator. PPA and sensitivity as `recall`, NPA and specificity as `specificity`, PPV as `precision`, NPV as `negative-predictive-value`, counts with the right direction, Bray-Curtis lower, F1 and Pearson higher, false-positive read percentage as `false-positive-rate` in percent. Intervals are 95% where printed and null with a reason where not. Corrections T1 (capped qualifier) and G5 (undefined PPV) are the only changes.

Origin and author overlap. Affiliations read from the JATS contributor lists and competing-interest statements; findings in H1, G1 and W4 and question 6.

Locators. Every result locator was resolved to its cell or paragraph by the parsers above. Configuration, protocol and claim locators were spot-checked against the cited Methods and Results sections; the Hu CRS claim (31 organisms), Huang reference definition, Wolf outcome definitions and Burkholderia exclusion, EsViritu headline settings, shared database and family-level scoring, and Sanderson blinding, Clopper-Pearson intervals and sample counts all match.

Missed cells. None in the chosen tables. Values outside them that were not extracted, for the record: Wolf cut-off sensitivities printed in Results (predictive 51.9%, diagnostic 80.7%); Sanderson sample-level result (36 of 38 PCR-negative samples negative by sequencing) and derivation-set results; Hu Supplemental Table S5 per-sample rows (spectrum.03993-25-s0002.xlsx, not pinned). None is required.

Duplicates. No match for any of the five DOIs, PMC IDs, `EsViritu`, `mcfDNA-Seq`, `bstNGS`, Genskey, Geneplus, the Wolf pilot (Goggin) or the Sanderson code repository in `data/entities` or `data/evidence` of the main clone, in the other eight `../rewire-benchmark-data-lit-*` worktrees, or (by `git grep`) in the 13 other `claude/lit-20261011-*` branches. `catalog-model-kraken2` exists in the store and is correctly reused.

Batch files. `claims.csv` covers every result and claim; Hu also lists its judgement claims and the other four do not (harmless, but make it consistent when regenerating). Huang's `claims.csv` printed values carry the full cell text (G6).

Not run: `npm test`, `npm run typecheck`, `npm run build` and `use-cases:repin`, since I was told not to edit records or commit. The collector's report says type checking and 515 tests passed on the uncorrected batches; rerun them after the corrections.
