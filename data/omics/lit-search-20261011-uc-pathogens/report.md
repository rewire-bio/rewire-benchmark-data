# Pathogen use-case literature pass, 2026-10-11

Use cases: `use-case-diagnostic-dna-pathogen-identification` and `use-case-diagnostic-rna-pathogen-detection`. Window: published or posted 2025-10-01 to 2026-10-11. Worker: Claude (Opus 5.5) research agent `uc-pathogens`. No human review is claimed. Nothing was executed or reproduced.

Searches: 28 for the DNA use case (24 Europe PMC, 4 web) and 25 for the RNA use case (23 Europe PMC, 2 web), against a budget of about 30 each, plus 5 shared source-resolution lookups. All are in `ledger.jsonl`; include and exclude decisions for 26 papers are in `scope-audit.jsonl`. Searches logged on 2026-10-09 for these use cases were not repeated, and every candidate was checked against `data/entities/sources.jsonl` (none was already present). This is a bounded pass, not a systematic review.

Every record in the five batches is `needs_review`. The extractor marked nothing reviewed. Each batch folder has `batch.jsonl`, `claims.csv`, `coverage.json`, `sources.md`, `retrieval-log.md`, `research.md` and `extract/`.

## Candidates extracted

| Batch | Source | Use case | Records | Results | Judgements |
| --- | --- | --- | --- | --- | --- |
| `use-case-coverage-dna-pathogen-20261011-hu2026` | Hu et al. 2026, Microbiol Spectr 14:e03993-25 (CC BY). MGISEQ-200 short-read and host-depleted ONT mNGS on 62 BALF specimens against culture, clinical microbiological tests (CMT) and a composite reference (CRS). Table 2, Supplemental Tables S6 and S7 | DNA | 128 | 108 | 3, proxy |
| `use-case-coverage-dna-pathogen-20261011-huang2026` | Huang et al. 2026, Respir Res 27:357 (CC BY-NC-ND). Blood targeted bstNGS, blood mNGS, CMT and blood culture on 122 ICU patients with pneumonia-associated sepsis against an adjudicated clinical diagnosis. Table 2 | DNA | 97 | 80 | 1, proxy |
| `use-case-coverage-dna-pathogen-20261011-wolf2026` | Wolf et al. 2026, Lancet Microbe 7:101312 (CC BY). Prospective Karius plasma mcfDNA-Seq in high-risk paediatric leukaemia: predictive and diagnostic sensitivity against blood-culture organisms, specificity in 162 control samples. Tables 2 and 3 | DNA | 62 | 44 | 3: diagnosis direct (proposed), prediction and specificity proxy |
| `use-case-coverage-rna-pathogen-20261011-tisza2026` | Tisza et al. 2026, bioRxiv v1 (CC BY-NC). EsViritu, Kraken2, Centrifuger, Metabuli and Sylph on one shared virus database: divergent positive controls, seven pathogen-free libraries, six mutated mock communities. Supplemental Tables S2, S6 and S9. Developer benchmark | RNA and DNA | 144 | 105 | 5, proxy (3 RNA, 2 DNA) |
| `use-case-coverage-rna-pathogen-20261011-sanderson2026` | Sanderson et al. 2026, medRxiv v2 (CC BY). Prospective validation of a nanopore RNA metagenomic workflow on 344 nasopharyngeal swabs against routine multiplex PCR. Values printed in the Results text | RNA | 24 | 14 | 1, direct (proposed) |
| Total | 5 sources (7 source records) | | 455 | 351 | 13 |

Existing records reused: `catalog-model-kraken2` (the Kraken2 configuration in the EsViritu batch). New vocabulary: `bray-curtis-dissimilarity` in `data/vocab/metric.ttl` (unmapped; needs review with the batch).

Archived copies (`gzip -n -9`) are kept only for the CC BY sources (Hu article and supplement, Wolf, Sanderson). The CC BY-NC and CC BY-NC-ND sources are pinned by hash and locator only.

## Candidates not extracted

| Source | Reason |
| --- | --- |
| Winnow-tax preprint (bioRxiv 10.64898/2026.10.02.756312, 2026-10-10, CC BY-NC-ND) | Kraken2/Bracken, Sylph, MetaPhlAn 4 and winnow-tax on a clinical stool cohort with culture and PCR reference (Peterson et al. 2022 data). The PDF was retrieved after repeated HTTP 429 (XML 404), but the clinical comparison is in Figures 4 and 5 with only partial prose values; Table 1 is runtime. Developer benchmark |
| DNA versus RNA mNGS in LRTI (J Infect 2025, 10.1016/j.jinf.2025.106659, CC BY) | 82 patients with both workflows; the abstract gives precision 1.00 versus 0.50 and F1 0.80 versus 0.67. Publisher full text returned HTTP 403 and there is no PMC copy yet. High value for the RNA use case; retry later |
| Nucleosome host-depletion plasma HD-mNGS (J Transl Med 2026, 10.1186/s12967-026-08597-x, CC BY-NC-ND) | HD-mNGS versus standard plasma mNGS, blood culture and CMT on 107 patients against a composite diagnosis. Per-method contingency tables are a figure (Fig. 6); the prose gives PPA for all four methods but NPA and TPA only partly, and the standard mNGS detection rate differs between Results (50.47%) and Discussion (51.40%). PPA could be extracted from prose |
| Multicentre CSF mNGS EQA (Clin Microbiol Infect 2026, 10.1016/j.cmi.2026.01.015) | 127 laboratories; paywalled and laboratories are anonymised in the abstract |
| cfDNA aligner benchmark in leukaemia sepsis (medRxiv 10.1101/2025.10.17.25338171) | Tables are images and the licence does not permit reuse |
| Metax (Cell 2026) | Developer benchmark; paywalled |
| LEMMIv2 (Genome Biol 2026) | Article tables are calibration thresholds; results are on the LEMMI platform and in figures |
| CMGD clinical database (Front Cell Infect Microbiol 2026) | Figures only; supplementary rows would need an unstated aggregation |
| Paediatric stool TB mNGS (Clin Infect Dis 2026); ICU pan-microbial service (Lancet Microbe 2025) | Single workflows; lower priority within the six-source limit |
| JCV 2025 assembler comparison; probe-capture versus mNGS (Spectrum 2026); RPIP versus RT-qPCR (Diagn Microbiol Infect Dis 2026) | Genome-completeness endpoint; agreement between methods only; paywalled |
| Reviews (AI in clinical metagenomics, J Microbiol Methods 2026; foundation models for taxonomy, Comput Biol Chem 2026) | No new results; abstracts mined for leads |

## Gaps

- No independent comparison of named clinical pipelines (CZ ID, SURPI+, DRAGEN Microbial, BugSeq, Explify, One Codex) on patient specimens was found for either use case; a title search for these names in the window returned nothing.
- No foundation model or other deep-learning classifier with a clinical pathogen-detection benchmark was found in the window. The deep-learning taxonomic classifiers found (Metaxa, ICCTax, Genos-m) report general taxonomy benchmarks only.
- RNA: the DNA versus RNA mNGS comparison (J Infect 2025) could not be retrieved. Apart from it, no multi-workflow comparison on RNA clinical specimens with per-workflow values was found. The RNA evidence added here is one workflow (Sanderson) and one developer benchmark on synthetic and pathogen-free data (EsViritu).
- DNA: the new clinical comparisons (Hu, Huang) score against reference standards that incorporate sequencing results. The only reference built without sequencing is blood culture (Wolf; the culture columns in Hu and Huang).
- Organisms absent from the reference: covered only by EsViritu's divergent positive controls (75.9% to 95.6% ANI, family-level scoring) and its mutated mock communities.
- Targeted panels (Huang bstNGS) cannot detect organisms outside the panel; no study measured that directly.
- Figure-only results not used: Winnow-tax clinical cohort, HD-mNGS contingency tables, Hu mock communities, Wolf day-by-day sensitivity.

## What needs a reviewer's judgement

1. Hu 2026 Table 2: HD-ONT NPA against CMT is printed 79.2% (Table 2 and Results); its counts give 42/52 = 80.8%. Recorded as `source_anomaly` on the result. Is a result-level dispute needed?
2. Sanderson 2026: the Abstract gives specificity 3836/3845 and the Results 3901/3910 for the same criteria. Recorded as `source_anomaly` on the Results value. A source-level concern would withhold the whole judgement; a result-level note or dispute is the alternative.
3. Sanderson 2026: the alternative criterion's sensitivity 159/274 is described as "samples passing batch controls from 260 to 274", although 260 elsewhere counts PCR-positive targets.
4. Relevance `direct` is proposed for two judgements: Wolf diagnosis (same assay type and endpoint as the DNA use case's Karius anchor, in a different population) and Sanderson validation (same inputs and endpoint as the RNA use case's UCSF anchor, with thresholds fixed on a separate derivation set). The existing anchors are judged proxy, so the reviewer may prefer proxy for consistency.
5. Incorporation bias in the Hu CRS (organisms detected by both workflows are added) and the Huang clinical diagnosis (uses NGS and CMT results). Both are stated in the protocols and judgements; check the wording.
6. Developer or vendor involvement: EsViritu authors ran all comparators; Karius took part in processing and analysis for Wolf; Genskey (Hu) and Geneplus (Huang) co-authors with no conflicts declared. All evaluations are `author_reported`.
7. EsViritu S2 values are model-estimated detection probabilities (Firth regression marginal means), stored as `recall` with a qualifier. EsViritu printed values are shortest round-trip decimals of stored floats.
8. Huang 2026: blood-culture PPV in fungal pneumonia is printed 0.00% (0.00% to 0.00%) with a zero denominator. The Table 2 p value is attached to accuracy, following the Results text.
9. EsViritu judgements on the DNA use case (two, proxy): keep or drop.
10. New metric concept `bray-curtis-dissimilarity`.
11. The 13 `assessed_by` links are listed per batch in `coverage.json` (`use_case_changes.add_links`). They are not added to the use_case records; as in the 2026-10-09 batches, the integrator adds them after review.

## Proposed updated summaries

Drafts for the reviewer; not applied to the summary claims. Every number traces to a result in these batches or to an existing reviewed result. Summaries should be applied only after the judgements they describe are reviewed and pinned (docs/use-cases.md).

### DNA pathogen identification

> Most workflow comparisons in the reviewed evidence use mock communities or constructed metagenomes; two use patient specimens, and in both the only reference standard built without sequencing is culture. For the Karius plasma cell-free DNA assay, the developers report 93.7% (59 of 63) agreement with initial blood culture in a sepsis-alert cohort, and a prospective study in children and young people with high-risk leukaemia, run with Karius involvement, found the blood-culture organisms in 81·3% (65 of 80) of bloodstream infection episodes at onset and in 51·9% (42 of 81) during the three days before; 82·7% of 162 afebrile control samples had no bacterium or yeast detected. In 62 bronchoalveolar lavage specimens (Hu et al. 2026), a short-read MGI workflow and a host-depleted nanopore workflow both had 95.2% positive agreement with culture but 44.6% and 46.4% negative agreement, because they found organisms culture did not; against a composite reference that adds organisms found by both workflows, positive agreement was 93.3% and 90.7%. In 122 intensive-care patients with pneumonia-associated sepsis (Huang et al. 2026), a targeted probe-capture assay on blood had 63.46% sensitivity against the clinical diagnosis, against 35.58% for untargeted blood mNGS, 49.04% for conventional tests and 9.62% for blood culture, with specificity of 44.44% and 61.11% for the two sequencing assays among 18 reference-negative patients; the clinical diagnosis used the sequencing results. In mock communities (Portik et al. 2022), Kraken2 and Bracken called 44 to 204 absent species at a 0.001% read threshold (precision 0.05 to 0.21), while long-read MEGAN-LR and BugSeq-V2 called 0 to 2; the first author is a PacBio employee. In seven pathogen-free libraries scored against a shared virus database by the EsViritu developers, the median number of false virus species was 0 for EsViritu, Centrifuger and Sylph, 6 for Kraken2 and 18 for Metabuli. For M. tuberculosis reads (Hall and Coin 2024), kraken with its standard database classified 0.07 to 0.74 of reads correctly, against 0.97 to 0.995 with a Mycobacterium database. Each study used its own reference database and reporting rules, and none of these results is clinical validation.

### RNA pathogen detection

> The single-assay results are a UCSF respiratory RNA metagenomic assay at 93.6% (103 of 110) sensitivity against original clinical respiratory panel testing, as reported by its developers, and a prospective Oxford nanopore workflow on 344 nasopharyngeal swabs (preprint) that, with thresholds fixed beforehand, detected 51% (133 of 260) of PCR-positive targets, from 85% for RSV to 19% for rhinovirus/enterovirus, with 99.8% specificity; post-hoc criteria raised sensitivity to 58%, and the nine false positives were attributed to barcode crossover. Three comparisons of several workflows add proxy evidence. On 88 nasal washings scored against 1144 respiratory virus PCR results (Carbo et al. 2022), all five classifiers detected 22 or 23 of the 24 PCR-positive results at species level at a read-count cut-off chosen on the same data, but 31% to 58% of their positive calls were PCR-negative. When 13 European clinical virology laboratories each ran their own pipeline on the same 13 clinical datasets (de Vries et al. 2021, preprint), 10 to 13 samples were correctly called positive, and the three pipelines that found every sample reported 6, 2 and 0 additional PCR-negative viruses. In the CAMI II blood metagenome challenge (Meyer et al. 2022), 4 of 10 submissions listed the causal virus. In a developer benchmark of five virus profilers on one shared database (Tisza et al. 2026, preprint), the model-estimated probability of detecting a divergent virus from 10 reads was 0.974 for EsViritu and 0.9998 for Metabuli but 0.045 for Kraken2, 0.012 for Centrifuger and 0.0009 for Sylph at the authors' headline settings, and Metabuli reported a median of 18 false species in seven pathogen-free libraries against 0 for EsViritu. None of this is clinical validation: the cohorts are small or single-site, reference databases and reporting rules differ, and the benchmark data are mostly synthetic.

The DNA draft omits Song et al. 2025, whose judgements are withheld by its existing source concern.

## Checks

Dry runs in the worktree on 2026-10-11; the store was reset afterwards with `git checkout -- data/entities data/evidence data/provenance`, so the store files are unchanged in this branch.

- `npm run -s records -- add` for each of the five batches in sequence: all passed attribute validation and the SHACL shapes (128, 144, 24, 97 and 62 records added). The Wolf batch first failed on an undeclared `source_locator` on the service record; this was fixed in the extraction script and the batch regenerated.
- `npm run -s records -- check` with all five added: 52,901 records match their provenance.
- `deriveUseCaseInputs` with the 13 proposed `assessed_by` links added in memory: all 13 judgements resolve as `draft` with the expected evaluations (Hu 2 each, Huang 4, Wolf 1, 1 and 2, EsViritu 5 each, Sanderson 2). The existing active judgements (Karius, UCSF, ENNGS) stay active.
- `npx tsc --noEmit -p .`: passed. `npx vitest run`: 48 files, 515 tests passed.
- `npm run build` was not run, as instructed.
