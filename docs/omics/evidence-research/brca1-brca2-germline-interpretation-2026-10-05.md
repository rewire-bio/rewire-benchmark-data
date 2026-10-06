# BRCA1/BRCA2 germline interpretation: research intake, 2026-10-05

Research intake for `use-case-brca1-brca2-germline-interpretation`. This is a bounded writing pass over already-extracted and spot-checked facts, not a new systematic review and not a published catalogue claim. No model was run and no classification in this document has had qualified human scientific review.

Use-case decision endpoint: "Choose methods that assemble and assess variant evidence under gene-specific criteria for a professional BRCA1/BRCA2 classification review" (`data/omics/use-cases/inputs.json`, `use-case-brca1-brca2-germline-interpretation.decision`). Comparison question on file: can an evidence-support method reduce review effort without increasing serious classification or criteria errors relative to standard gene-specific review (`collection_plan.comparison_question`).

Linked follow-up: rewire-benchmarks [#25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), item B343, and the focused follow-up issue [#26](https://github.com/rewire-bio/rewire-benchmarks/issues/26).

## Search and retrieval ledger

The literature search itself was run by a prior Sonnet discovery session, same programme, dated 2026-10-05. This authoring pass did not search anew; it wrote this dossier from that session's and the subsequent source-resolution and extraction sessions' already-executed, already-checked results, plus a small number of its own targeted verification checks (noted below). The ten queries that session executed are inlined in full below, so this record does not depend on the `/tmp` working file for evidence of search scope:

1. `"HECTOR BRCA1 BRCA2 variant classification 2026"`
2. `"MARGINAL BRCA variant interpretation 2026"`
3. `"ClinGen ENIGMA BRCA1 BRCA2 Variant Curation Expert Panel specification version clinicalgenome.org"`
4. `"AutoGVP automated germline variant classification tool evaluation BRCA"`
5. `"HECTOR BRCA ENIGMA classifier published journal 2026 Düzenli Ergün"`
6. `"\"ENIGMA BRCA1 BRCA2\" cspec.genome.network specification version 1.1.0 PDF"`
7. `"\"ENIGMA\" BRCA1 BRCA2 cspec.genome.network version 1.2 2026"`
8. `"\"Challenges of Real-World Utilization\" ClinGen ENIGMA BRCA2 Chinese population abstract"`
9. `"HECTOR BRCA ENIGMA \"134\" concordant classification tool independent cohort"`
10. `"HECTOR medRxiv 26357220 full text abstract concordant \"generic ACMG\" classifiers InterVar CharGer"`

That session also ran direct WebFetch verification of: the medRxiv HECTOR preprint (article-info and full text), hector.gazi.edu.tr, cspec.genome.network GN092/GN097, PMC11869971, PMC11675547, PMC9687470/MARGINAL, Bioinformatics btae114/AutoGVP, medRxiv BIAS-2015 (blocked), ascopubs PO-25-00554 (blocked), nature.com s41431-026-02058-1 and s41467-026-71393-0 (both blocked by login redirect at that point), and Europe PMC MED/41576305 (blocked). Working file, for traceability only, not as the sole record of scope: `/tmp/rewire-evidence-programme/brca1-brca2/discovery-resumed.result.json`, `.result` lines 10-21.

Checks performed directly by this authoring pass, 2026-10-05:

| Source | Access method | Result |
|---|---|---|
| [Benet-Pagès et al. 2025, PMC11869971](https://pmc.ncbi.nlm.nih.gov/articles/PMC11869971/) | Full text via cached HTML (`/tmp/benet.html`), targeted grep | Confirmed verbatim |
| [HECTOR preprint, medRxiv](https://www.medrxiv.org/content/10.64898/2026.07.06.26357220v1.full) | Full text via cached HTML (`/tmp/hector.html`), targeted grep | Confirmed verbatim |
| [ClinGen ENIGMA BRCA1 spec, GN092](https://cspec.genome.network/cspec/ui/svi/doc/GN092) | Live WebFetch | Current version 1.2, released 2025-01-09 01:11:34; confirmed live |
| [ClinGen ENIGMA BRCA2 spec, GN097](https://cspec.genome.network/cspec/ui/svi/doc/GN097) | Live WebFetch | Current version 1.2, released 2025-01-09 01:12:40; confirmed live |
| [MARGINAL / Karalidou et al. 2022, PMC9687470](https://pmc.ncbi.nlm.nih.gov/articles/PMC9687470/) | Cached HTML (`/tmp/marginal-pmc.html`), targeted grep | Author and title confirmed verbatim |

Not independently re-verified this pass, carried forward from the prior extraction session as an already-checked fact:
- [So et al. 2024, PMC11675547](https://pmc.ncbi.nlm.nih.gov/articles/PMC11675547/)

Hu et al. 2026 access sequence, stated accurately across sessions: the discovery session's WebFetch of [nature.com/articles/s41467-026-71393-0](https://www.nature.com/articles/s41467-026-71393-0) hit a login redirect and was logged as blocked/unscreened at that point. A later same-day source-resolution session confirmed the article is in fact open access (CC-BY 4.0) via both nature.com and [PMC13223280](https://pmc.ncbi.nlm.nih.gov/articles/PMC13223280/), and the subsequent extraction session retrieved and extracted its full text from PMC13223280. This dossier's Hu 2026 row therefore reflects a source that was initially blocked by one access route and then successfully read in full via a second route in a later session; it is not independently re-verified in this authoring pass.

Access limits and exclusions:
- Benet-Pagès supplementary files mmc1–mmc5 (xlsx/pdf binaries) were not opened in any session to date; see the dedicated discrepancy section below for what could resolve the BRCA1/BRCA2 "n" discrepancy.
- So 2024 supplementary zip and Hu 2026 Supplementary Table 3 / Supplementary Data 1–2 were not opened; figure-derived numbers in the prior extraction come from figure legends and captions in HTML, not from pixel-level reading of chart images.
- [Kwong et al. 2026](https://doi.org/10.1200/PO-25-00554) (JCO Precision Oncology, DOI 10.1200/PO-25-00554): full text blocked at ascopubs.org, PubMed, and Europe PMC (cookie wall / 403) across both the discovery and this pass. Title and venue suggest a direct BRCA2 real-world discordance study, but scope and relevance are unresolved and it is excluded from the evidence table below.
- Also blocked during discovery and still unscreened: a Nature-family BRCA1/2 VUS-prioritization paper (DOI prefix s41431-026-02058-1, blocked by login redirect, not re-attempted via PMC or another route) and a BIAS-2015 v2.0.0 eRepo benchmark (medRxiv, blocked 403).
- This document does not claim the cited studies are a complete or representative sample of BRCA1/BRCA2 interpretation-method literature; absence of a method from this table is not evidence that no such study exists. No systematic search of trial registries, VCEP meeting minutes, or non-English literature was attempted in the discovery session or this pass.

## Evidence table

| Source | Scope | Denominator | Headline comparator | What it measures | Does NOT measure |
|---|---|---|---|---|---|
| [Benet-Pagès et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11869971/) (Genetics in Medicine Open, [DOI 10.1016/j.gimo.2024.101961](https://doi.org/10.1016/j.gimo.2024.101961)) | BRCA1 + BRCA2 VUS reclassification, 121 variants / 120 patients | 40 BRCA1, 81 BRCA2 (121 total) | ENIGMA VCEP v1.1.0 (t3): 83.5% (101/121) reclassified to B/LB; ACMG/AMP+SVI (t2): 20% (24/121) to LB; no LP/P at either step | Reclassification rate under successive criteria sets on the same fixed cohort | A gene-split reclassification rate; see discrepancy below |
| [So et al. 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11675547/) (Diagnostics (Basel), [DOI 10.3390/diagnostics14242821](https://doi.org/10.3390/diagnostics14242821)) | BRCA1 missense, ClinVar-conflicting only | 450 (of 12,719 total BRCA1 ClinVar variants, 654 conflicting, 450 missense retained) | VarSome vs. CanVIG-UK agreement: 58.9% (265/450, 95% CI 52.0-66.4%) | Tool-vs-tool agreement on a conflicting-variant subset | Accuracy against independent ground truth for the full 450; the only ground-truth-anchored comparator covers 17/450 (3.8%) |
| [HECTOR preprint](https://www.medrxiv.org/content/10.64898/2026.07.06.26357220v1.full) (medRxiv, [DOI 10.64898/2026.07.06.26357220](https://doi.org/10.64898/2026.07.06.26357220)) | BRCA1 + BRCA2, full ClinVar catalogue sweep, 2026-04-22 | 37,470 raw to 34,077 eligible to 33,913 classified | eRepo exact-classification agreement 108/143; code-level agreement 326/413; in-house 132-variant set, 96/132 definitive by the tool's likelihood-ratio method vs. 85/132 (GeneBe) and 31/132 (Franklin) | Classification coverage and agreement with the ENIGMA VCEP's expert-curated classifications and evidence-code assignments in the ClinGen Evidence Repository (eRepo), and resolution rate vs. two other automated tools | Accuracy against adjudicated truth; this is a preprint with no measured reviewer time, and "resolution" (a tool reaching a call) is not "correctness" |
| [Hu et al. 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13223280/) (Nature Communications, [DOI 10.1038/s41467-026-71393-0](https://doi.org/10.1038/s41467-026-71393-0)) | BRCA2 only, SGE functional assay, exons 15-26, 6,383 SNVs | 6,383 total, 4,438 missense subset | 5,926/6,383 (92.8%) classified using integrated functional data; matched six-model comparator panels: N=158 ClinVar missense standards, N=316 HDR standards | Functional-data-driven classification yield on two fixed, cross-model matched panels | A complete BRCA1/BRCA2 clinical review; per-model sensitivity/specificity figures are not restated here (see note below) |
| [Karalidou et al. 2022 ("MARGINAL")](https://pmc.ncbi.nlm.nih.gov/articles/PMC9687470/) (Biomolecules, [DOI 10.3390/biom12111552](https://doi.org/10.3390/biom12111552)) | BRCA1/BRCA2, CanVaS-derived tool validation, 497 variants | 497 (held-out 80/20 split), plus a separate external validation set of 11,932 ClinVar variants not used in training | Two-stage classifier performance against CanVaS labels on the 497-variant held-out split, and against ClinVar labels on the 11,932-variant external set (not restated here; proxy metric) | A single tool's held-out and external validation against existing registry labels | An independently adjudicated full clinical-review comparison, and a reviewer-time endpoint. Both CanVaS and ClinVar labels are existing registry classifications, not blinded independent adjudication performed for this study |

Locators for the headline figures above, checked directly against each cached source's actual section headings in this pass (headings quoted as they appear in the text, not guessed):
- Benet-Pagès: cohort in Materials and Methods, "Patients and variant data". t2 (20%, 24/121 to LB) in Results, "Reclassification of VUS with the ACMG/AMP classification system using SVI recommendations and new data (ACMG/AMP + SVI)". t3 (83.5%, 101/121 to B/LB) and the gene-split "n" sentence both in Results, "Reclassification of variants using the ENIGMA specifications (ENIGMA VCEP)".
- So 2024: cohort extraction (12,719 total, 654 conflicting, 450 missense) in Materials and Methods, Section 2.1, "ClinVar Data Extraction". 58.9% VarSome-vs-CanVIG-UK agreement (265/450) and the 137-vs-18 discordance pattern in Results, Section 3.3, "Comparison of Classification Results Between Varsome and CanVIG-UK", with Figure 2.
- HECTOR: 108/143 classification-level and 326/413 code-level agreement in Results, "Evidence Repository" subsection. 96/132, 94/132, 85/132 (GeneBe), 31/132 (Franklin) definitive-resolution counts in Results, "Benchmarking against generic classifiers" subsection, Table 1. The 37,470 / 34,077 / 33,913 catalogue-sweep counts in Methods, "ClinVar BRCA1/BRCA2 Full-Catalog Sweep".
- Hu 2026: per the extraction session (not independently re-opened in this pass), 6,383 total and discordant-study counts in Results, "Combined analysis"; N=158 ClinVar and N=316 HDR matched-panel figures in the Fig. 1a and Fig. 1b captions respectively.
- Karalidou et al. 2022 (MARGINAL): dataset (497 variants, CanVaS) in Materials and Methods, Section 2.1, "Data Acquisition", with the classifier-1/classifier-2 split given in Table 2. Held-out 80/20 test-set performance in Results, Section 3.1, "Machine Learning Model Comparison" (Tables 3-4). The 11,932-variant external ClinVar validation in Results, Section 3.3, "Performance Evaluation on ClinVar Data Set" (Table 6) — not Table 3 or 4, which belong to the earlier held-out comparison; checked directly against the cached source rather than assumed.

Notes carried forward from the extraction, reported as the source's own words where quoted:
- HECTOR's "could not be parsed" exclusion reason is cited at both the 37,470 to 34,077 step and the 34,077 to 33,913 step. Arithmetic is internally consistent (37,470 - 3,393 = 34,077; 34,077 - 164 = 33,913); whether these are two distinct pipeline checkpoints or a redundant description is unresolved from the text alone.
- Per the prior extraction session's (not independently re-checked in this authoring pass) reading of Hu 2026: Fig. 1a/1b report the index model's sensitivity/specificity on the fixed, cross-model matched N=158 (ClinVar) and N=316 (HDR) panels, and that extraction described these panels as genuinely matched across all six models. A separate per-model comparator table built in an earlier round was not confirmed against this matched panel versus the unmatched, per-model-varying denominators in Fig. 1c/1d, and Supplementary Table 3 was not opened to check. Those per-model percentages are omitted here pending independent re-verification, and the matched-panel sensitivity/specificity figures themselves should be treated as extraction-reported, not authoring-pass-verified.

## Benet-Pagès "n" discrepancy, unresolved

The source states: "We observe a similar reclassification rate toward LB/B for BRCA1 (85%, n = 40) and BRCA2 (83%, n = 67)" (Results, ENIGMA VCEP subsection; verified verbatim against cached HTML on 2026-10-05).

This single sentence cannot be read consistently against the Methods denominators (BRCA1 = 40, BRCA2 = 81 VUS) under any one definition of "n":
- If "n" is the denominator, it fits BRCA1 (40 matches Methods) but leaves BRCA2's stated denominator 14 short of 81.
- If "n" is the reclassified count (numerator), 67/81 = 82.7% ≈ 83% fits BRCA2, and 34 + 67 = 101 matches the separately stated aggregate (101/121 reclassified to B/LB). But applying the same reading to BRCA1 implies a denominator of 40/0.85 ≈ 47, which matches no number stated anywhere in the article.

No sentence in the retrieved Methods, Results, Discussion, or figure/table captions defines "n" in that sentence. Figure 2's caption and the three supplementary table captions (mmc3-mmc5, not opened as binaries) contain no gene-level split as far as retrievable. The 34+67=101 reconciliation is an arithmetic coincidence noted here, not a correction the source makes itself and not something this document treats as resolved. The aggregate, fully defined figures (83.5%, n=101/121 reclassified to B/LB; 20%, n=24/121 to LB; no LP/P) are unaffected and are what should be used in any derived catalogue entry; the gene-split percentages should not be used until this is resolved. Opening mmc4.xlsx (Supplementary Table 2, variant classification across t1/t2/t3) or mmc5.xlsx (Supplementary Table 3, ACMG code changes) is one route to resolution; direct clarification from the authors is another and has not been sought.

## Decision-endpoint assessment

The use-case decision asks which evidence-support methods improve BRCA1/BRCA2 variant review without increasing serious classification errors, under a comparison against manual criteria-based review with the same evidence cutoff and ENIGMA specification (`collection_plan.baselines`, `collection_plan.outcomes`).

None of the five accessible sources in this table provide that comparison:
- Benet-Pagès measures reclassification rate across successive criteria-set versions on a fixed cohort, not a tool/method comparison against a baseline reviewer process, and reports no reviewer time.
- So 2024 measures tool-vs-tool agreement (VarSome vs. CanVIG-UK) on a conflicting-variant subset, with a ground-truth-anchored comparator limited to 17/450 variants; no serious-error adjudication and no reviewer time.
- HECTOR measures agreement with the ENIGMA VCEP's expert-curated classifications and evidence-code assignments in the ClinGen Evidence Repository (eRepo), and resolution against two other automated tools on an in-house set; it is a preprint, reports no measured reviewer time, and "resolution" is not accuracy.
- Hu 2026 measures sensitivity/specificity of functional-data integration against ClinVar and HDR standards for BRCA2 only; it is a single-gene functional-assay study, not a full clinical classification-review comparison, and reports no reviewer time.
- Karalidou et al. 2022 (MARGINAL) reports held-out (80/20 split, 497 variants) and external (11,932 ClinVar variants) validation of a single tool, but against existing CanVaS and ClinVar registry labels rather than a blinded, independently adjudicated full clinical review, and with no reviewer-time endpoint reported.

Consistent with the use-case's own recorded `evidence_gaps`, no independently adjudicated paired serious-error-plus-equal-evidence-reviewer-time comparison was found in the sources reviewed in this pass or the prior 2026-09-30 intake (which covered ENIGMA calibration only). This is reported as a gap in the sources checked so far, not a claim that no such study exists in the broader literature; Kwong 2026 remains unresolved pending full-text access and was not checked for relevance to this gap.

## Unresolved items for follow-up

1. Benet-Pagès BRCA1/BRCA2 "n" discrepancy in the gene-split reclassification sentence (above): resolvable by opening mmc4.xlsx or mmc5.xlsx, or by author clarification; neither has been pursued.
2. Hu 2026 per-model comparator percentages (Concordance, GMM, Secondary Concordance, Huang, Sahu): need re-anchoring to Fig. 1a/1b (matched N=158/316) versus Fig. 1c/1d (unmatched, per-model N); Supplementary Table 3 not opened.
3. HECTOR's duplicated "could not be parsed" exclusion-reason wording across two pipeline stages: unexplained redundancy, not a numeric contradiction.
4. [Kwong et al. 2026](https://doi.org/10.1200/PO-25-00554) (DOI 10.1200/PO-25-00554): full text inaccessible; scope and relevance to this use case unresolved.
5. No serious-error-adjudicated, equal-evidence, reviewer-time comparison against manual gene-specific review was found for any evidence-support method in the sources checked to date. This is the primary gap blocking the use-case decision endpoint and is the subject of rewire-benchmarks [#25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), B343, and the follow-up issue [#26](https://github.com/rewire-bio/rewire-benchmarks/issues/26).

Resolved this pass, not carried forward as open: the ClinGen ENIGMA BRCA1/BRCA2 spec versions were confirmed live at [GN092](https://cspec.genome.network/cspec/ui/svi/doc/GN092) and [GN097](https://cspec.genome.network/cspec/ui/svi/doc/GN097), both v1.2, released 2025-01-09. This is the version baseline against which Benet-Pagès (pinned to v1.1.0) and Hu 2026 (v1.2.0) should be read.

## Correction, 2026-10-06

This document originally described the HECTOR eRepo comparator (108/143 classification agreement,
326/413 code-level agreement) as "ClinVar expert panel (eRepo) submissions" in two places. Re-verified
live against the preprint full text
(`https://www.medrxiv.org/content/10.64898/2026.07.06.26357220v1.full`, Results, "Evidence
Repository"): the 143-variant, 413-code comparator is the ENIGMA BRCA1/BRCA2 VCEP's own curation
of the ClinGen Evidence Repository (eRepo, https://erepo.genome.network), not ClinVar. The
preprint's separate full-catalog sweep (34,077 ClinVar BRCA1/BRCA2 variants) is a distinct
analysis from the eRepo validation tier. Both occurrences above have been corrected to name the
ENIGMA VCEP/eRepo comparator precisely; the 108/143 and 326/413 figures are unchanged.

## Scope note

This document separates source-reported observations (quoted or closely paraphrased, with locator) from arithmetic performed here on those numbers (labelled as derivation). No Rewire-run model output, benchmark execution, or independent experimental replication is included or implied. Nothing in this document should be read as a classification decision, a catalogue entry, or a validated comparison; it is an intake record for the next evidence-collection step referenced in rewire-benchmarks [#25](https://github.com/rewire-bio/rewire-benchmarks/issues/25), B343, and [#26](https://github.com/rewire-bio/rewire-benchmarks/issues/26).
