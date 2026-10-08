# Ranking rare-disease variants for review: bounded evidence research, 2026-10-08

Case 9 of 17 in the evidence programme ([rewire-benchmark-data #3](https://github.com/rewire-bio/rewire-benchmark-data/issues/3); benchmark programme [rewire-benchmarks #25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), items B341 and BL341). Use case `use-case-rare-disease-candidate-ranking`, slug `rare-disease-candidate-ranking`.

The article issue is [rewire.it #341](https://github.com/rewire-bio/rewire.it/issues/341) ("[Article plan] Choosing models for rare-disease candidate ranking"). It was resolved from repository evidence, not from the label "C1": `docs/omics/use-case-coverage-2026-09-30.md` links #341 to this use case, the 30 September audit comment on #341 describes the same mapping, the issue body ends with "Use-case ID: `use-case-rare-disease-candidate-ranking`", and the body carries the `rewire-benchmark-development:2026-10-01` block naming B341/BL341. "C1" is only the source locator in `inputs.json` (`use-case-source-clinical-priorities-2026-09-28`). The reanalysis question is a different article, [#342](https://github.com/rewire-bio/rewire.it/issues/342) (B342).

Starting commit: producer `main` f5a4214994e2596213511d85e1385927cf586b1e (branch `codex/rare-disease-ranking-evidence-20261008`). No catalogue, mapping, definition, release, builder, test or generated file was changed. No scientific model was run, trained or downloaded, no weights or patient data were fetched, and none of the sources' tools (Talos, Exomiser, PhEval, RankVar) was executed. Public pages, articles, supplements and repository metadata were fetched with curl and parsed with small local text-extraction scripts (`tx.py`, inline Python run with `-I`). No access was paid for, bypassed or requested. Times are UTC request starts from `workbench/rare-disease-ranking-20261008/request-log.tsv` (ignored workbench). This is a research intake awaiting independent review, not a completed case. Nothing here is a clinical recommendation, diagnostic validation or human adjudication.

## Disposition in brief

1. Docs-only. The stored Talos Table 1 and Exomiser rank counts match the primary text and need no change. No numeric intake is proposed now; any intake is held for Codex independent review.
2. The Talos versus Exomiser denominator conflict is unresolved: 194 families in the Results and Methods text, 190 in the Extended Data Fig. 1 legend. The printed Exomiser percentages round correctly from 194 and not from 190, which is arithmetic consistency only. The figure image could not be retrieved, so nothing printed explains 190. No cause is asserted.
3. Talos recovery is of callable known diagnoses and its output is an unranked list; Exomiser is a rank-limited list. A fixed rank budget is not measured analyst effort, and neither arm measured reviewer time.
4. No controlled addition of a molecular-effect model at identical inputs, knowledge and review effort was found in the bounded sources. The closest item is a UDN step that added two pathogenicity sources together (AlphaMissense and SpliceAI) to an Exomiser configuration already tuned on the same cohort (section 3). It is exploratory and does not isolate either source.
5. The Talos comparator was Exomiser v14, default configuration. In the UDN study, tuning on the evaluation cohort itself changed Exomiser top-10 share a great deal. That does not show the same change would occur on the Talos cohorts; an independent held-out cohort would be needed. Exomiser 15.1.0 has since been released.
6. Intake and issue: numeric intake is held for Codex independent review. The focused gap is posted as [rewire-benchmarks #35](https://github.com/rewire-bio/rewire-benchmarks/issues/35) (matched-input, equal-effort added-model evaluation; links #25, tracker #3 and article #341), after a full open and closed title and body dedup. Parent #25 is a programme tracker, not a focused ticket.

## Existing inventory (unchanged)

Definition (`data/omics/use-cases/inputs.json`): decision "choose methods for prioritising variants in an initial exome or genome analysis"; setting "initial ES/GS interpretation in a defined congenital-anomaly or developmental-disorder population", singleton and family analysis compared separately. Exclusions: ranking alone does not establish pathogenicity or diagnosis; balanced pathogenic/benign classification is not case-level performance; reanalysis, cancer risk and treatment are separate. Collection status `collecting`; review method `automated_source_review` (2026-09-30), no qualified human review.

Mappings (all `proxy`): six Talos protocols (`uc-clinical-20260930-talos-{acg,rgp}-{trio,singleton,full}-protocol`, each with default and strict evaluations) via `use-case-mapping-20260930-341-*`, and `uc-clinical-20260930-exomiser-acg-protocol` / `-evaluation`. Source records `uc-clinical-20260930-source-talos` and `-table1`. The 30 September audit stored sha256 `629b9578…` for the article page and `cb86e1a5…` for Table 1; today's fetches have different bytes (section 1). The cause is unknown: no diff was done and none is inferred.

## Search log (exact, dated)

| ID | Batch start (UTC) | Mode | Exact query | Outcome |
|---|---|---|---|---|
| Q1 | 2026-10-08T08:54:20Z | standard | `Exomiser v14 benchmark rare disease diagnostic variant rank top-1 top-10 exome genome phenotype 2025 2026` | UDN optimisation study; no v14-specific benchmark paper |
| Q2 | 2026-10-08T08:54:20Z | standard | `AI-MARRVEL LIRICAL Exomiser comparison diagnostic variant prioritization independent cohort top-k recall` | LA-MARRVEL preprint (snippet only) |
| Q3 | 2026-10-08T08:54:20Z | standard | `Vestito 2024 Efficient reinterpretation of rare disease cases using Exomiser npj Genomic Medicine` | Vestito 2024 (reanalysis; #342 scope) |
| Q4 | 2026-10-08T08:54:20Z | extended | `2026 rare disease variant prioritisation benchmark held-out cohort deep learning phenotype genotype ranking solved cases Exomiser comparison diagnostic yield prospective` | RankVar read; DAVP, DeepBD, DiagAI seen as snippets only |
| Q5 | 2026-10-08T08:55:40Z | standard | `Phenopacket Store Danis curated GA4GH phenopackets rare disease cases publications Genetics in Medicine` | HGG Advances 2024 (not Genet Med); repo |
| Q6 | 2026-10-08T08:55:40Z | standard | `AlphaMissense added to variant prioritisation pipeline rare disease diagnostic variant rank improvement Exomiser ablation exome cohort` | no clean standalone ablation retrieved; UDN study read |

Queries within a batch were sent together and are not individually timed. Inclusion rule: a primary source with a case-level known-diagnosis ranking or recovery endpoint and enough cohort, version or split detail to judge it. Seen only as snippets and not assessed (no numbers adopted): LA-MARRVEL (arXiv 2511.02263), DAVP (medRxiv 2026.02.17.26346421), DeepBD (arXiv 2606.24779), DiagAI, AIVA (blog). Findings are bounded to these queries; no global absence or novelty claim is made. Web search was US-only and returned snippets, so every adopted figure below was read in the cached primary.

Retrievals (HTTP 200 unless noted): Nature Medicine article and Table 1 (08:53:50Z, 08:53:51Z); Europe PMC full text for PMC12539062 (08:54:38Z), PMC11655964 (08:54:39Z), PMC13617915 (08:54:58Z), PMC11929307 (08:54:44Z); Genomics England page (08:55:21Z); GitHub repository, release and commit metadata for four repositories (08:55:52Z to 08:55:56Z). Talos Supplementary Information files 1 and 2 (08:59:24Z, 200); Talos Extended Data Fig. 1 image, two path variants (08:59:33Z, 08:59:38Z, both 404, not retried); Europe PMC supplementary archive for PMC12539062 (08:59:46Z, 200, slow transfer).

## Findings

### 1. Talos (Nature Medicine 2026), primary

[10.1038/s41591-026-04477-5](https://www.nature.com/articles/s41591-026-04477-5), version of record 24 June 2026, CC BY-NC-ND 4.0. Article HTML, fetched 2026-10-08T08:53:50Z (582,435 B), sha256 `862fa375bdb1ecf2794c09b2a819881ac79740d80395b1d585c07edd3e7c22fb`. An independent publisher-HTML fetch at 2026-10-08 08:53:05.735944 UTC (582,435 B) has sha256 `359ad536021ab127db79c50abb5ea5204dbf58e0365315a6d4c7ccde0c3f095e`, and the 30 September stored value is `629b9578…`. The three hashes differ; the reason is unknown and none is inferred. All three readings show the 194 (text) versus 190 (Extended Data Fig. 1 legend) conflict. [Table 1](https://www.nature.com/articles/s41591-026-04477-5/tables/1) sha256 `d1e5f81551e18c81dc5a2d0067df020e874a035f039dbf2f23fa168006289928`; all printed rows were checked against the stored records. Read: Results, Methods (Talos workflow, Exomiser comparison, statistics), Table 1, the Extended Data Fig. 1 legend and Extended Data Table 1 to 4 titles. Supplementary Information file 1 (sha256 `472db602fe3f8875a4f65c4c07ffaabd44dd633ee5a2326daf8620174764c2e6`, fetched 08:59:24Z) holds only Supplementary Table 1, the reanalysis diagnoses (#342 scope, not used); file 2 (sha256 `b35c2129ebcf860b8bfe48cc25b42d66197a44d59a0c7c3dca1c659f0ccfaa61`) is the Reporting Summary (4 pages, no text layer). Extended Data Fig. 1 image: two attempts at 08:59:33Z and 08:59:38Z used guessed `/image/` paths and returned HTTP 404; these say nothing about whether the publisher-linked image exists. The publisher-linked `/esm/` path (`https://media.springernature.com/lw685/springer-static/esm/art%3A10.1038%2Fs41591-026-04477-5/MediaObjects/41591_2026_4477_Fig4_ESM.jpg`) was tried independently and timed out after 40 s; it was not retried. A text search of the article HTML found no "source data" link. Extended Data Table 1 to 4 bodies were not read. The figure image is therefore unread and the conflict is unexplained.

**What it is.** Talos is an automated reanalysis tool. Its evaluation cohorts were reprocessed from raw data with a standardised pipeline (GATK, GATK-SV, GATK-gCNV), after earlier clinical and research analyses had produced the known diagnoses. This is not an initial-analysis ranking trial, and the use case defines initial analysis. Talos returns a small unranked candidate list; it does not rank.

**Cohorts and denominators (Table 1).**

| Item | ACG trio | ACG singleton | ACG full | RGP trio | RGP singleton | RGP full |
|---|---|---|---|---|---|---|
| Probands | 377 | 401 | 401 | 390 | 688 | 688 |
| Known diagnoses callable by the pipeline | 196 | 208 | 208 | 54 | 93 | 93 |
| Default: diagnoses recovered | 177 (90%) | 170 (82%) | 186 (89%) | 47 (87%) | 81 (87%) | 80 (86%) |
| Default: candidate variants (per proband) | 487 (1.3) | 729 (1.8) | 523 (1.3) | 519 (1.3) | 1,491 (2.2) | 1,095 (1.6) |
| Strict (phenotype match required): diagnoses | 164 (83%) | 160 (77%) | 173 (83%) | 45 (83%) | 78 (84%) | 77 (83%) |
| Strict: candidate variants (per proband) | 403 (1.1) | 491 (1.2) | 419 (1.0) | 335 (0.9) | 777 (1.1) | 582 (0.8) |

Table footnote: known diagnoses are those "detectable using the standardized GATK/GATK-SV/GATK-gCNV analysis pipeline". The percentage denominator is therefore the callable known diagnoses, not all diagnosed probands and not all probands. Candidates per proband are medians in the text and ratios of totals in the table (the stored 30 September audit already flags this).

**End-to-end denominators.** The text gives ACG primary manual yield 220/401 probands (55%, three with dual diagnoses), 275 diagnostic variants of which 260 SNV/indel, and 208 callable diagnoses; RGP prior yield 106 diagnoses, 93 callable. Proband counts and diagnosis counts are different units. The text names the diagnoses outside the pipeline (STR expansions, low-level mosaic variants, retrotransposon insertions, one SMN1 CNV) but gives no workload denominator beyond the per-proband candidate counts. An end-to-end recovery percentage over all known diagnoses is not printed and is not computed here because the units differ.

**Text and table inconsistencies, recorded as found, no cause asserted.**

- ACG trio probands: 377 in Table 1, 378/401 (94%) in the text.
- "Of the 208 trios with known diagnoses ... detectable for 196 (94%) ... remaining 11": 208 is the all-family count in Table 1, and 208 minus 196 is 12, not 11.
- "Of the 20 missed diagnoses" in the ACG trio analysis, while 196 minus 177 is 19.
- Candidate counts are called medians in the text and are totals-based ratios in the table.

**Exomiser comparison.** Exomiser v14, default configuration, ACG trio SNV/indel call sets. Success for Talos is the causative variant being returned under default settings; success for Exomiser is rank within top 1, 5, 10 or "all". Whether phenotype terms were supplied to Exomiser, which Exomiser data release and which frequency or pathogenicity sources were used is not stated in the text read. Stored records (`uc-clinical-20260930-exomiser-*`) match the text:

| Endpoint | Exomiser count | Printed % | Share of 194 | Share of 190 |
|---|---|---|---|---|
| All prioritised variants (lowest-ranked diagnosis at 32) | 172 | 89% | 88.7% | 90.5% |
| Top 10 | 164 | 85% | 84.5% | 86.3% |
| Top 5 | 157 | 81% | 80.9% | 82.6% |
| Top 1 | 127 | 65% | 65.5% | 66.8% |

The shares are computed here for the check only. The printed percentages round correctly from 194 at all four endpoints and not from 190 at any. The McNemar discordant pairs give a second consistency check: Talos-only versus Exomiser-only 12 vs 12 (all), 18 vs 10 (top 10), 25 vs 10 (top 5), 53 vs 8 (top 1). Exomiser count minus Exomiser-only plus Talos-only is 172 at all four endpoints, so the paired analysis implies Talos recovered 172 in the compared set at every threshold. That fits 194 and the "172 (89%)" for Exomiser-all, but it is derived. The 190 in the Extended Data Fig. 1 legend ("analysed as trios ... N = 190", singletons N = 202) is unexplained: the figure image could not be retrieved, so no printed count explains it and the conflict stays open. Singleton Exomiser results appear only in the figure legend, not as numbers in the text.

**Effort.** Exomiser top-k limits a ranked list per family; Talos returns about 1.3 unranked candidates per trio (default). Top 1 favours Talos by the authors' paired test (P < 0.0001), top 5 also (P = 0.017); all and top 10 show no significant difference. These are not equal analyst effort: no reviewer time or candidates inspected was measured for either.

**Independence and overlap.** The cohorts are described as independent validation cohorts, but the known diagnoses came from earlier manual analysis by the same programmes. Knowledge release dates for the benchmarking runs are not stated; Talos reads ClinVar and PanelApp Australia at runtime and gnomAD v4. The Methods state the ACG variants were reported to ClinVar (accessions SUB15793101, SUB15793127, SUB15796069). Whether the evaluated diagnoses appeared in the ClinVar release used, and whether Talos configuration was tuned on these cohorts, is not stated. The Methods say investigators were not blinded to prior diagnoses. Centre and time: ACG is an Australian national study (2018 to 2022, critically ill infants and children, 94% trios); RGP is a US remote-enrolment study (genomes before September 2022, median age 26 years, previously negative testing). Phenotype data: HPO terms, per-proband term counts and quality were not read. Inheritance baseline versions: PanelApp Australia, ClinvArbitration, gnomAD v4, HPO and Monarch are cited without release dates in the text read.

**Reanalysis kept separate.** The same paper's iterative-reanalysis arm and Vestito et al. below are reanalysis of previously unsolved cases with clinical-laboratory or clinical-team review. That is case 16 (#342) evidence on a different endpoint and population, and is not used here.

**Access and reuse (separate).**

| Item | Terms |
|---|---|
| Paper | Open access, CC BY-NC-ND 4.0 |
| Code | [populationgenomics/talos](https://github.com/populationgenomics/talos), MIT; HEAD af069ea9 (2026-10-08T05:05:00Z), latest release v12.2.0 (2026-09-30). The paper does not state which release was used |
| Data | RGP sequence data in dbGaP phs003047 (controlled access, review "typically within several weeks"); Australian Genomics data on request for ethically approved secondary research; ClinVar submissions as above. No access was requested |
| Weights | Not applicable (no trained model) |

### 2. Exomiser as comparator

- Release state at retrieval: [Exomiser](https://github.com/exomiser/Exomiser) latest release 15.1.0 (2026-06-09T11:32:00Z), AGPL-3.0. The Talos comparator was v14.
- [Genomics England validation page](https://pipeline-rd-help.genomicsengland.co.uk/Mira/variant-prioritisation-approaches/exomiser/exomiser-performance/) (sha256 `76d8ba4938e358aeaa7a3cc49d20f0f884676621d810d3fc615d0ca565d90eb5`; service-operator documentation (Genomics England), not peer reviewed): Exomiser v13.1.0 returned the reported diagnostic variant in the top 3 for 1,709 of 1,869 variants (91%, 95% CI 90 to 93%) across 1,659 cases, against 80% for v12.0.0. The denominator is every diagnostic variant reported in NHS GLH outcome questionnaires at November 2022: reported, solved diagnostic variants, variant-level, no unresolved cases. How uncallable or unreported variants were handled is not established by the page. It is not unselected case-level diagnostic yield, as the #341 body already says.
- Vestito et al., npj Genomic Medicine 2024 ([10.1038/s41525-024-00456-2](https://doi.org/10.1038/s41525-024-00456-2), PMC11655964): Exomiser 13.1.0 default on unsolved 100kGP cases with review of candidates by the Genomics England clinical team. This is reanalysis (#342 scope) with clinically reviewed new diagnoses; it has no known-truth ranking-recall endpoint and is not used here.

### 3. Exomiser configuration sensitivity (Genome Medicine 2025)

Cooperstein et al., [10.1186/s13073-025-01546-1](https://doi.org/10.1186/s13073-025-01546-1), PMC12539062, CC BY-NC-ND 4.0, Europe PMC XML sha256 `36a21b374b1028e42d5407e5a8d78a79386ed3ed2314b3eaf712ef8c5def8575`. Read: Abstract, Results, Methods, Discussion. Supplementary archive read in part (see below).

- Population: 386 diagnosed UDN probands, truth set chosen by inclusion criteria (comprehensive HPO list; diagnosis "certain" or "highly likely"; made mainly by genome-scale sequencing; SNV/indel only), UDN database queried 2024-04-08. Cohorts: GS coding 231 probands, 296 variants; ES coding 125 probands, 153 variants; GS noncoding 39 probands, 60 variants. All solved cases; unsolved UDN cases are absent. The authors note over half had earlier nondiagnostic clinical exome, and that solved cases may favour well-documented gene-phenotype links.
- Versions: Exomiser/Genomiser v14.0.0 with data release 2406, CADD v1.7, ReMM v0.4; the ClinVar whitelist was disabled because UDN diagnoses are periodically submitted to ClinVar.
- Result: top-10 share of coding diagnostic variants rose from 49.7% to 85.5% (GS) and 67.3% to 88.2% (ES) after stepwise parameter changes chosen on the same cohorts (filtered VCF, human-only hiPHIVE, REVEL + MVP + AlphaMissense + SpliceAI); noncoding Genomiser top 10 from 15.0% to 40.0%. 35 of 509 diagnostic variants (6.9%) were not prioritised by default parameters on raw VCFs and were excluded from the filtering analysis. Step gains are reported in the text with mixed units ("2.7%"; percentage points versus relative change is not stated).
- Pathogenicity-source step: in the GS Exomiser cohort, adding AlphaMissense and SpliceAI together to REVEL + MVP "increased the proportion of diagnostic variants ranked within the top 10 by 2.7% over default settings" (text wording). In Fig. 3A this is the orange-to-green step. Its baseline (orange) already includes the filtered VCF and human-only hiPHIVE gene-phenotype associations with REVEL + MVP; it is not the raw-VCF default configuration (red curve), which is the 49.7% starting point. The two sources were added as a pair, so neither is isolated (AlphaMissense and MVP mainly contribute to missense, SpliceAI to splice variants). This is the closest item found to adding a molecular-effect score at a fixed rank budget. Limits: single cohort, steps selected and measured on the same cases, unit unresolved (percentage points or relative; "over default settings" does not match the plotted baseline), solved UDN probands only, and the authors warn that REVEL-type predictors are trained on ClinVar and may inflate scores for these diagnoses. Fixed top-10 is a rank budget, not measured analyst effort. Fig. 3A (cohort curves, JPEG from the Europe PMC supplementary archive) shows cumulative curves only, with no per-step counts printed; the exact top-10 counts per step were not obtained.
- Exact configuration, partial read: Europe PMC supplementary archive (`/supplementaryFiles`, fetched 08:59:46Z, HTTP 200, 4,902,265 B, sha256 `2b8cc124c3a7f851fc4af8e4dbd8d7599480fff9f84d017c7141002c86a5d638`; file list in `workbench/.../cache/optimisation-supp/x`). Additional file 4 Text S1 states dataset version 2406 (gnomAD v4 based), default frequency sources gnomAD (exomes and genomes, AFR, AMR, EAS, NFE, SAS) plus UK10K, and maxFrequency 2.0% retained as default. The authors' YAML files are in `github.com/icooperstein/exomiser_optimization`; that repository was not fetched. The full optimised YAML was therefore not read.
- Independent check: 17 newly diagnosed UDN probands (23 variants) after cohort assembly; 22 of 23 within the top 30, "improvements in ranking" reported without a stated top-10 count in the text read.
- Phenotype and pedigree: no phenotype algorithm 40.9% top 10; PhenIX 62.8%; default hiPHIVE 66.6%; human-only hiPHIVE 82.8% (GS coding, intermediate settings). Pedigree errors prevented ranking of 24 diagnostic variants in 22 families; 21 of 24 were recovered with proband-only data. These show the baseline depends on phenotype quality, pedigree accuracy and configuration.
- Family structure: the cohorts mix singleton, duo, trio, quad and larger families (for GS coding, 24 singletons of 231 probands). No singleton-versus-family result was read.
- Data access: UDN data are in dbGaP phs001232 and variants in ClinVar; no access requested.

### 4. Other ranking methods read or seen

- RankVar, Genome Medicine 2026 ([10.1186/s13073-026-01701-2](https://doi.org/10.1186/s13073-026-01701-2), PMC13617915, CC BY-NC-ND 4.0; XML sha256 `04fe48cd0f2ad744dfadbe96fc86b6240d9d1ff841a93369291e8550495d9ba5`): random forest trained on 1000 Genomes samples with ClinVar P/LP variants spiked in, tested on CHOP positive diagnoses, a birth-defects biorepository (BDB, includes CNV/SV) and SSC/SPARK autism cohorts (candidate de novo variants, not confirmed diagnoses), against Exomiser, PhenIX and LIRICAL; endpoint top-k variant accuracy, author-reported. Not usable here as a comparison: the Exomiser version and settings and comparator values are in supplementary figures not retrieved, ClinVar overlaps knowledge the comparators also use, and the authors ran a ClinVar-feature ablation on their own model only. Per-cohort accuracies are not adopted.
- PhEval (BMC Bioinformatics 2025, [10.1186/s12859-025-06105-4](https://doi.org/10.1186/s12859-025-06105-4), PMC11929307, Apache-2.0): benchmarking framework that runs Exomiser (14.0.2, data 2406) on the publication-derived Phenopacket Store cases ([10.1016/j.xhgg.2024.100371](https://doi.org/10.1016/j.xhgg.2024.100371); BSD-3-Clause repository). For the public corpora the VCFs are synthetic (a causal variant spiked into a healthy-donor exome), so results are not real-background candidate pools, and the authors name the lack of public real clinical data as the main limitation. The store is solved published cases, not an unselected cohort. A public synthetic run can serve as a reproducible benchmark of the specified public, synthetic-genotype phenotype population (gene and variant ranking given the spiked variant). It cannot validate clinical utility or real-background yield.
- Seen as snippets, no numbers adopted: LA-MARRVEL, DAVP, DeepBD, DiagAI, AIVA. These vary in whether Exomiser is run as default, tuned, or as the first stage that is reranked; none was read in full.

## What the sources can and cannot support

- Gene versus variant versus diagnosis: Talos and the Exomiser rank comparison score recovery of a previously reported diagnostic variant in cohorts with established (reference) diagnoses; GEL top-3 is variant-level against reported diagnostic variants; PhEval and several preprints are gene-level. Recovery of a known diagnostic variant is not a newly established diagnosis. Reanalysis diagnoses (Talos reanalysis arm, Vestito) are case 16 evidence and are kept separate.
- Known callable subset versus all patients: Talos percentages use callable known diagnoses; the GEL figure uses reported diagnostic variants with callability handling unestablished; neither includes unresolved cases in the recovery denominator. End-to-end sensitivity with calling failures and unresolved cases in the denominator is not reported in any source read.
- Candidate recovery versus diagnostic yield versus effort: recall at top-k, candidates per proband, and confirmed yield are distinct and no source reports analyst minutes for ranking.
- Added-model benefit: no source read holds inputs, knowledge release, review effort and cohort fixed while adding only a molecular-effect model. The bounded closest item (section 3) is a pair of pathogenicity sources added in a configuration tuned on the same cohort. Tools in section 4 differ in inputs, knowledge and training data, so differences between them are not additive benefit. Each source should be judged on its own protocol; a novel ML addition is not assumed to be needed.
- Singleton versus family: Talos reports both on ACG and RGP (derived by removing parents); family-aware Exomiser results by structure were not read.
- Variant classes: all numbers are SNV/indel or coding unless stated; CNV, SV, STR, mitochondrial and noncoding are separate (Genomiser top 10 is 40.0% after tuning).
- Congenital anomaly or developmental disorder setting: ACG (critically ill infants and children) is the closest; RGP, UDN and 100kGP are broader.
- Qualified clinical review remains outside automated source curation. No clinical validation or recommendation is made.

## Source conflicts (kept explicit)

1. 194 (Results and Methods text, with printed percentages) versus 190 (Extended Data Fig. 1 legend) for ACG trio families with SNV/indel diagnoses. Unresolved.
2. ACG trio probands 377 (Table 1) versus 378 (text); callable 196 versus "208 trios" and "11" remaining; "20 missed" versus 196 minus 177 equals 19.
3. Candidates are "median" in the text and totals-based in Table 1.
4. Exomiser configuration dependence (not a source conflict, since the settings differ): in the UDN study, top-10 share was 49.7% (genome) and 67.3% (exome) under default settings and 85.5% and 88.2% after tuning on the same cohorts. Default and tuned results can differ much on that cohort. This does not show that default Exomiser understated performance on the Talos cohorts; that needs an independent held-out cohort.

## New access limitations

- Talos: the Extended Data Fig. 1 image was not read (two guessed-path 404s here, one independent timeout on the linked path; no retry), so the 194 versus 190 conflict cannot be examined at figure level and singleton Exomiser counts are unavailable. Extended Data Tables 1 to 4 bodies were not read. Supplementary Table 1 is reanalysis only.
- Cooperstein: supplementary archive retrieved (one slow transfer, completed); the figure shows curves without printed counts, and the optimised YAML lives in a GitHub repository that was not fetched. RankVar supplementary files were not retrieved.
- Patient-level cohorts (RGP dbGaP phs003047, UDN phs001232, Australian Genomics) need data access requests; none were made.
- Web search is US-only and returned snippets; unread preprints are not evidence here.
- Talos HTML hashes differ between the 2026-10-08 fetches and the 30 September stored value. The cause is unknown and is not inferred.

## Paths

Changed: `docs/omics/evidence-research/rare-disease-candidate-ranking-2026-10-08.md`. Ignored workbench (not committed): `workbench/rare-disease-ranking-20261008/` containing `intake-plan.md`, `draft-issue-b341.md` (copy of the draft; the reviewed body is posted as rewire-benchmarks #35), `request-log.tsv`, `search-batch1.time`, `search-batch2.time`, `tx.py` and `cache/` (Talos HTML, text and supplements; Europe PMC XML and text for three studies and PhEval; Cooperstein supplementary archive; Genomics England page; GitHub metadata). Earlier dossiers, history and unrelated caches were not touched. Pending Codex independent review, CI and merge; not complete.
