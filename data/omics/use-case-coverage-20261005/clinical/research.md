# BRCA1/BRCA2 germline interpretation: additive research-evidence intake, 2026-10-05

Additive intake for `use-case-brca1-brca2-germline-interpretation` (issue #343), scoped to the
five sources checked in `docs/omics/evidence-research/brca1-brca2-germline-interpretation-2026-10-05.md`.
This pass wires new records into the build; it does not add new use-case mappings and does not
freeze a release. The use case's five existing active mappings
(`use-case-mapping-20260930-343-{2b9e45a46d4b,64fb29b5bff8,77a677a9f119,cf70c367d48e,dd4044ac3f2f}`)
are untouched and byte-identical.

## Benet-Pages et al. 2025 (PMC11869971, DOI 10.1016/j.gimo.2024.101961)

Ingested the aggregate, fully defined reclassification figures only: t2 (ACMG/AMP + SVI) 24/121
(20%) reclassified to LB, and t3 (ENIGMA VCEP v1.1.0) 101/121 (83.5%) reclassified to B/LB, both
verified verbatim against the cached full text (`/tmp/benet.html`) in Results, "Reclassification
of variants using the ACMG/AMP classification system with SVI recommendations and new data
(ACMG/AMP + SVI)" and "Reclassification of variants using the ENIGMA specifications (ENIGMA
VCEP)". The source's single gene-split sentence ("BRCA1 85%, n = 40 and BRCA2 83%, n = 67") is
**not** ingested: it cannot be read consistently against the Methods denominators (BRCA1 = 40,
BRCA2 = 81) under any single definition of "n" (see Unresolved conflicts below). This is a
reclassification-rate study across successive criteria-set versions on a fixed 121-variant VUS
cohort, not a tool/method comparison against a baseline reviewer process; no reviewer time is
reported.

## So et al. 2024 (PMC11675547, DOI 10.3390/diagnostics14242821)

Ingested the overall VarSome-vs-CanVIG-UK concordance rate, 58.9% (265/450, 95% CI 52.0-66.4%),
verified verbatim against the cached full text (`/tmp/so.html`) in Results, Section 3.3,
"Comparison of Classification Results Between Varsome and CanVIG-UK". This is labelled as
tool-vs-tool agreement, not accuracy: the only ground-truth-anchored comparator in the source
covers 17/450 (3.8%) of variants and is not ingested. The 137-vs-18 discordance breakdown is not
transcribed to locator-level precision in this pass and is not ingested.

## HECTOR preprint (medRxiv 10.64898/2026.07.06.26357220, v1, posted 2026-07-06)

Ingested the eRepo validation-tier figures: 108/143 (75.5%) exact classification-level agreement
and 326/413 (78.9%) code-level agreement with the ENIGMA VCEP's expert-curated calls on the
143-variant ClinGen Evidence Repository set, verified verbatim against the cached full text
(`/tmp/hector.html`) in Results, "Evidence Repository". This is a preprint: `source.attributes`
and the protocol both carry `publication_status: "preprint_not_peer_reviewed"`, and the protocol
states the comparator is "agreement with the ENIGMA VCEP's expert-curated classifications and
evidence-code assignments in the ClinGen Evidence Repository (eRepo), not independent accuracy;
not peer reviewed." `source_checked` status here reflects verbatim verification of the
cached text, not peer review or independent adjudication. The in-house 132-variant, three-tool
comparator (HECTOR vs. GeneBe vs. Franklin) is real and verifiable but is deliberately left out of
this pass to keep the add minimal (it would add three more evaluations/configurations for one
paper); this is flagged as a follow-up, not a permanent exclusion.

Correction, 2026-10-06: the 2026-10-05 pass had mislabelled the eRepo comparator as "ClinVar
expert-panel submissions" in several places. Re-verified live against the preprint full text
(`https://www.medrxiv.org/content/10.64898/2026.07.06.26357220v1.full`, Results, "Evidence
Repository"): the 143-variant, 413-code comparator is the ENIGMA VCEP's own curation of the
ClinGen Evidence Repository (eRepo), not ClinVar. The preprint's separate full-catalog sweep
(34,077 ClinVar BRCA1/BRCA2 variants) is a distinct analysis and is not the eRepo comparator. All
occurrences of the ClinVar/eRepo conflation in this coverage package and in
`data/omics/use-cases/inputs.json` have been corrected to name the ENIGMA VCEP/eRepo comparator
precisely; the 108/143 and 326/413 figures themselves are unchanged.

## Hu et al. 2026 (PMC13223280, DOI 10.1038/s41467-026-71393-0, Nature Communications)

The primary source was fetched and checked directly this pass via live retrieval and cached to
local byte-identical text (`/tmp/hu-brca2.html`), retrieved 2026-10-05T16:34:46Z, `artifact_sha256`
`1caeb3b18e369afb0db2015700c4a07b5985fd55a04d953a0ae5f01532f8f3b0`. Ingested one aggregate figure:
"Thus, 92.8% (5926 of 6383) overall... were classified as P/LP or B/LB," in Results,
"Incorporation of the 'Integrated VarCall model' functional data into the BRCA1/2 ClinGen variant
classification specifications." This is labelled as classification yield/coverage using an
integrated functional-data (SGE) proxy, not clinical accuracy or a complete clinical review, and
is scoped to BRCA2 exons 15-26 (6,383 SNVs) only. The matched six-model comparator panels
(N=158 ClinVar, N=316 HDR standards) and all per-model sensitivity/specificity figures are not
ingested in this pass.

## Karalidou et al. 2022 ("MARGINAL", PMC9687470, DOI 10.3390/biom12111552)

Source-only entry. Author, title and venue were verified verbatim against the cached full text
(`/tmp/marginal-pmc.html`). The headline performance tables are located (Results 3.1, Tables 3-4:
held-out 80/20-split classifier comparison on 497 variants; Results 3.3, Table 6: external
validation on 11,932 ClinVar variants) but no numeric cell was transcribed from them in this or
any prior pass. This is recorded as a value-not-extracted gap in `attributes.evidence_concerns`,
not as a resolved or irresolvable discrepancy, and not as a proxy exclusion.

## Kwong et al. 2026

No source record added. Full text remains blocked at ascopubs.org, PubMed and Europe PMC across
every pass to date; scope and relevance to this use case remain unresolved.

## Unresolved conflicts preserved from the research dossier

- Benet-Pages BRCA1/BRCA2 "n" discrepancy: the single sentence "We observe a similar
  reclassification rate toward LB/B for BRCA1 (85%, n = 40) and BRCA2 (83%, n = 67)" cannot be
  reconciled against the Methods denominators (BRCA1 = 40, BRCA2 = 81 VUS) under any one
  definition of "n". Not ingested; see the dossier's dedicated discrepancy section for detail.
- Hu 2026 per-model comparator percentages remain unanchored to the matched (N=158/316) vs.
  unmatched per-model denominators; not ingested.
- HECTOR's duplicated "could not be parsed" exclusion-reason wording across two pipeline stages
  is an unexplained redundancy, not a numeric contradiction; not relevant to the figures ingested
  here.
- Kwong et al. 2026 scope and relevance remain unresolved; no source record added.

## What this pass does not do

No new use-case mapping was added to `data/omics/use-cases/inputs.json`. No release was frozen.
The five existing active mappings for this use case are preserved byte-for-byte. No Rewire model
execution, independent experimental replication or qualified human scientific review is included
or implied by any record in this intake.
