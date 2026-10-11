# Review: fusion batches from the 2026-10-11 oncology pass (reviewer-onc-2)

Reviewer: Claude research agent (reviewer-onc-2); no human review claimed. I did not extract these batches. Date 2026-10-11. Worktree `rewire-benchmark-data-lit-uc-oncology`, uncommitted files; no record was edited.

Batch file hashes reviewed (SHA-256 of the bytes on disk at review time):

- longread `batch.jsonl` 2eedce31aad02e4e44ae79fb77d46cca7c6b2294731ad183c24ebe02afd8a181, `coverage.json` 86bdaa9ec8956ec7d48ab187d76cebb529dfd8271aaf0f50aa9f5e091436d894, `claims.csv` 02a21d4909dca11511e13ca412790bac0c4a7c0268368efa55ea924024fe1c92
- leukaemia `batch.jsonl` fe9584e7333147829ed712f00d301ba20f25a7546a9cb9ee7f160210baea7bec, `coverage.json` 521fd24838b1b330c59584ef02af7a119cc867622e9350158ea4bac5cd5e0f19, `claims.csv` a74f5cc5f9c70ad0cb329888003eeb310690c9a417d84f6f5834bea44d899459

If any of these change before the receipts are written, the changed records need re-checking.

## Verdicts

### use-case-coverage-rna-fusion-longread-20261011 (Dorney et al. 2026): approved with corrections

All 597 values are correct. The corrections are one duplicate method, one relevance change and some wording.

D1. Duplicate method. `rna-fusion-longread-20261011-method-jaffal` duplicates the stored `rna-fusion-20261009-method-jaffa`; Lin 2026's JAFFAL configuration `rna-fusion-20261009-config-lin2026-jaffal` already links to it.
- Delete the record `rna-fusion-longread-20261011-method-jaffal`.
- In `rna-fusion-longread-20261011-config-jaffal`, change the `configuration_of` target to `rna-fusion-20261009-method-jaffa`.
- In `coverage.json`: add `rna-fusion-20261009-method-jaffa` to `existing_reused`, remove the jaffal ID from `new_ids_by_kind.method`, and set `new_record_counts.method` to 4.

D2. Huh7 judgement `use-case-mapping-rna-fusion-longread-20261011-huh7-known-fusions`: change `relevance` from `direct` to `proxy`. Each value pools six long-read callers, or three short-read callers for Illumina, so it scores no workflow a user would run. Platform and the number of pooled callers are confounded, and there are only three counts. Replace both `description` and `attributes.rationale` with:
> Proxy, not direct: the same Huh7 RNA sequenced on PacBio Kinnex, ONT PCR-cDNA and Illumina gives the first linked short- versus long-read comparison on identical samples, but each value pools several callers (six long-read callers, three short-read callers for Illumina), so it compares platforms with unequal caller pools, not workflows a user would run.

Update the matching entry in `coverage.json` `judgements` to `proxy`.

D3. Configuration locators. Each `attributes.source_locator` currently cites `Run_GFSLGF.sh header and RunJAFFAL.sh` for every caller. Set them to:
- `rna-fusion-longread-20261011-config-ctat-lr-fusion`: `Methods 'Reference genomes', 'Fusion caller configuration'; repository Fusions/runtools/RunCTAT-LR-fusion.sh header`
- `rna-fusion-longread-20261011-config-gfseeker`: `Methods 'Reference genomes', 'Fusion caller configuration'; repository Fusions/runtools/RunGFSeeker.sh`
- `rna-fusion-longread-20261011-config-fusionseeker`, `-config-genion`, `-config-longgf`: `Methods 'Reference genomes', 'Fusion caller configuration'; repository Fusions/runtools/Run_GFSLGF.sh header (caller versions, min_read_supp=2)`
- `rna-fusion-longread-20261011-config-jaffal`: `Methods 'Reference genomes', 'Fusion caller configuration'; repository Fusions/runtools/RunJAFFAL.sh`

D4. Add this limitation to the `limitations` of protocol `rna-fusion-longread-20261011-protocol-sgnex-k562` and of claim `use-case-mapping-rna-fusion-longread-20261011-sgnex-k562`:
> CTAT-LR-Fusion has no K562 PCR-cDNA rows at 7.5 or 10 Gb, and no caller has K562 direct-RNA rows above 2.5 Gb or direct-cDNA rows above 5 Gb; the source does not say why.

D5. Add this limitation to protocols `rna-fusion-longread-20261011-protocol-sgnex-k562` and `-protocol-sgnex-mcf7`, and to claims `use-case-mapping-rna-fusion-longread-20261011-sgnex-k562` and `-sgnex-mcf7`:
> knownnumber is the number of distinct call records the authors' script labels known (grouped by gene pair, chromosomes and fusion type); the script does not deduplicate them to listed fusions, so it is an upper bound on the number of listed fusions recovered.

No numeric value changes.

### use-case-coverage-rna-fusion-leukaemia-20261011 (Kim et al. 2025): approved with corrections

All 83 values are correct. The corrections are one unsupported statement and the numeric form of ten non-measurements.

L1. The batch says several of the RNA-seq-only fusions were confirmed by RT-PCR and Sanger sequencing. The retrieved article does not support this. Figure 1 shows RT-PCR and Sanger confirmation for KMT2A::THAP12, which is a conventional-positive fusion with an unspecified partner (row KMT2A::?), and for MLLT10::UBE2L6, which is RNA-seq only. FUS::ZNF362 and RUNX1::PRPF19 were not tested. Supplemental Figure S1 was not retrieved. Make these replacements:
- In `limitations` of protocol `rna-fusion-leukaemia-20261011-protocol-conventional-diagnostics` and of claim `use-case-mapping-rna-fusion-leukaemia-20261011-conventional-diagnostics`, replace "Truth is conventional diagnostics (karyotyping, FISH, multiplex RT-PCR), which miss some fusions: RNA-seq-only fusions count against specificity although several were confirmed by RT-PCR and Sanger sequencing." with:
  > Truth is conventional diagnostics (karyotyping, FISH, multiplex RT-PCR), which miss some fusions: the 12 RNA-seq-only fusions count against specificity, although the authors describe several as well-known recurrent fusions and confirmed one of them (MLLT10::UBE2L6) by RT-PCR and Sanger sequencing (Figure 1); validation was attempted only for novel or rare fusions with residual sample.
- In result `rna-fusion-leukaemia-20261011-result-arriba-one-minus-specificity`, set `metric_qualifier` to:
  > overall, 56 fusion-negative results by conventional diagnostics; RNA-seq-only fusions counted as errors, though the authors describe several as well-known recurrent fusions and confirmed one by RT-PCR and Sanger sequencing
- In `coverage.json` `use_case_changes.evidence_gaps_add[0]`, use the text approved below.

L2. In the ten RNA-seq-only concordance results, the printed 0 is not a measured agreement, yet `numeric_value` is "0". As stored, the page would show 0% agreement. Every `undefined_reason` result in the store has a null `numeric_value`, and so do this lane's Dorney F1 'NA' rows. For each ID below, keep `printed_value` "0" and `undefined_reason`, set `numeric_value` to null, and add `missing_metadata.value` = `{"reason": "inapplicable", "note": "Concordance is not defined for fusions with no conventional detection; the table prints 0"}`. If the validator rejects a null numeric value with a numeric printed value, report it instead of working around it.
`rna-fusion-leukaemia-20261011-result-etv6-ncoa2-concordance`, `-fus-znf362-concordance`, `-hnrnph1-erg-concordance`, `-igh-crlf2-concordance`, `-mllt10-ube2l6-concordance`, `-p2ry8-crlf2-concordance`, `-pax5-jak2-concordance`, `-pax5-nol4l-concordance`, `-picalm-mllt10-concordance`, `-runx1-usp42-concordance` (each with prefix `rna-fusion-leukaemia-20261011-result`). Do not change `kmt2a-mllt10-concordance` or `tra-d-unspecified-concordance`: those are real 0% agreements (0 of 1 and 0 of 2).

L3. Add this limitation to the protocol and the claim:
> Per-patient results (Supplemental Data Tables S2 and S3) and Supplemental Figure S1 were not retrieved; the AML (86.4%) and B-ALL (87.0%) sensitivities are printed only in the Discussion, without denominators.

## Answers to the collector's questions (fusion batches)

3. Repository values. I accept them. `stat_summary.tsv` and `counts_SGNex_summary.tsv.gz` are the authors' own output files at a pinned commit, written by the pinned R scripts (`Precision_Recall_ReadSupp_stats.R` writes `stat_summary.tsv` directly; `SGNex_DiscoveryNRecall.R` writes the counts). The preprint cites the repository in Code availability, and where its text prints numbers they agree with the tables: CTAT-LR-Fusion recall 0.14 at 85% and 0.28 at 95% identity, no F1 above 0.35, no recall above 30%. Recording full-precision strings with `printed_value_basis` is correct. No values are computed.
4. Dorney conflicts. The prose false-call counts (632, 519, 106, 38) name no scenario, so they do not contradict a specific table row, and none of them is stored. A protocol limitation is enough; no evidence concern. The Spiked_Number denominators of 187 to 208 at 1 Gb, and 397 at 10 Gb and 85% identity, are as the authors' script computes them (`Spiked_Counts_wo_SF`); keeping them in each result's qualifier is right. The 25-versus-34 Huh7 list difference is plausibly 21 recovered Huh7 fusions plus HCC fusions not reported in Huh7 (Results paragraph 1 says two HCC-only fusions were found in Illumina data), but the source does not say so; the existing limitation wording is fine.
5. Not applicable to these batches.
6. Headline metrics. True-positive count is the right headline for K562, MCF7 and Huh7: those protocols print only counts, with denominators 6, 53 and 34 on the protocols. F1 for the simulated protocol and recall for Kim are correct.
Relevance: simulated `proxy` is approved. K562 and MCF7 `direct` are approved: real cancer cell-line long-read RNA, known-fusion recovery and a review-burden count, with inputs matching the use case. Huh7 changes to `proxy` (D2). Kim `direct` is approved: real patient RNA-seq against orthogonal assays, one workflow, with limitations corrected (L1, L3). No judgement excludes any evaluation, and none needs to.

## Approved summary for use-case-tumour-rna-fusion-detection

Every number below matches a stored result in these batches, a protocol denominator or qualifier, or the existing reviewed summary text. Text kept from the current summary is reproduced unchanged. Final text, verbatim:

> Four comparisons join the Seraseq reference and paediatric NCH cohort evidence; values cannot be pooled across studies. Tamura et al. 2026 ran 12 short-read callers on haematologic cancer cell lines; one, Genomon, comes from a co-author's group. On 61 driver fusions in conventional RNA-seq of 170 cell lines, Arriba detected all 61 (TPR 1), FusionCatcher 0.98, STAR-Fusion 0.93, InFusion 0.43 and STARChip 0.41. On 24 driver fusions in targeted RNA-seq of 26 cell lines, Arriba again reached 1 and STAR-Fusion 0.92, InFusion 0.17 and STARChip 0. A driver fusion entered these truth sets only if at least four callers, including the one scored, found it and it had literature or RT-PCR support, so fusions that most callers miss are under-represented and these values may overstate sensitivity. Against a consensus of the other callers, the number of single-caller calls, a measure of review burden, ranged on conventional RNA-seq from 327 for TrinityFusion-D and 1,061 for STAR-Fusion (PPV 0.39) to 9,567 for Arriba (PPV 0.08), 22,445 for FusionCatcher and 695,295 for Pizzly. On nanopore long reads from 51 paediatric B-ALL samples (Lin et al. 2026), scored on the dominant fusion per sample, JAFFAL reached sensitivity 0.76, LongGF 0.70 and FusionSeeker 0.63, with precision 0.79 to 0.95; the authors' own FUSILLI reached 0.81. At about one tenth of the depth, sensitivity was 0.09 to 0.27. In an independent long-read benchmark (Dorney et al. 2026 preprint), no caller exceeded F1 0.35 on 400 simulated fusions at 100 Gb and 95% read identity: CTAT-LR-Fusion 0.35 (recall 0.28, precision 0.46), JAFFAL 0.29, Genion 0.20, FusionSeeker 0.14, GFSeeker 0.07 and LongGF 0.04. On all ONT PCR-cDNA reads of the MCF7 cell line, CTAT-LR-Fusion's calls matched 20 of 53 previously reported fusions, with 51 other calls; JAFFAL matched 19 with 38 other calls and FusionSeeker 11 with 359. The other calls mix real fusions missing from the literature list and false calls. On the Huh7 cell line, pooling six long-read callers per long-read platform and three short-read callers for Illumina, PacBio Kinnex recovered 20 of 34 previously reported fusions, ONT PCR-cDNA 17 and Illumina 15. Against karyotyping, FISH and RT-PCR in 101 adult and paediatric acute leukaemia patients (Kim et al. 2025), an Arriba workflow with manual review detected 40 of 48 conventionally detected fusions (sensitivity 83.3%) and called fusions in 21.4% of 56 conventionally negative results; these count against specificity, although the authors describe several as well-known recurrent fusions and confirmed one by RT-PCR and Sanger sequencing. These are cell lines, simulations and leukaemia samples: no linked comparison covers solid-tumour specimens, FFPE tissue or novel-fusion discovery, only Kim et al. score against orthogonal clinical assays, none reports interval estimates, and none establishes clinical performance.

Changes from the collector's draft: "using all reads" and a statement that other calls mix unlisted real fusions with false calls (truth-set bias); the unequal caller pools in the Huh7 comparison; "several confirmed by RT-PCR" corrected (L1); the RNA-seq-only count given as the stored 21.4% of 56; and "no linked comparison covers adult or solid tumours" replaced, because Kim et al. include adults (median age 48) and MCF7 and Huh7 come from solid tumours, though neither is a tumour specimen.

## Approved use-case field changes

Approved, verbatim. Neither change withholds existing judgements.

- `evidence_gaps`: replace "No linked study compares short-read and long-read callers on the same samples." with:
  > Short- and long-read evidence on the same RNA comes from one cell line (Huh7), with calls pooled over callers per platform (Dorney et al. 2026 preprint); no per-caller comparison across platforms on the same samples is linked.
- `evidence_gaps`: add
  > Only one workflow (Arriba with manual review) is scored against orthogonal clinical assays (Kim et al. 2025, acute leukaemia); its specificity counts RNA-seq-only fusions as errors, although some are well-known recurrent fusions and one was confirmed by RT-PCR and Sanger sequencing.
  > Long-read caller precision and recall come from simulated reads only; on cancer cell lines only counts of known and other calls are available.
- `source_ids`: add `rna-fusion-longread-20261011-source-dorney2026`, `rna-fusion-longread-20261011-source-dorney2026-repository`, `rna-fusion-leukaemia-20261011-source-kim2025`. `citation_locators`: one per batch, as proposed.
- `links`: add `assessed_by` for the five protocols as listed in each `coverage.json`.

Not approved for this release: `setting_append`. `setting` is a pinned field, so changing it would withhold the eight reviewed judgements (two AMP, six rna-fusion-20261009) and the summary until each is re-reviewed. The release workflow refuses to withhold a judgement the previous release served. The new evidence is described in the summary and the gaps. The append can go in a later pass that re-reviews those judgements. `inputs` and `exclusions` stay unchanged. The evidence fits the existing inputs, which name long reads, and touches none of the exclusions.

## Checks run and outcomes

Sources and hashes:
- Kim XML: I downloaded Europe PMC `PMC13071280/fullTextXML` myself (156,853 bytes). SHA-256 4d3a6d48fc107763bffe18ff7dbcb6ab97b86757e69ff89ae595f3243f30bad1 matches the source record.
- Dorney preprint: bioRxiv blocked the direct download (Cloudflare error 1015, 17 bytes returned). I unpacked the archived `artifacts/preprint-v1.xml.gz` instead. Its raw SHA-256 c665bb407799324bc50ae1792d82574a41ae4a9182befd360973d89a82cbaa5b matches the source record, and the gzip hash matches `sources.md`. The bioRxiv API record matches the source record: version 1, posted 2026-08-12, cc_by, the same JATS URL, and authors Dorney, Wu, Hung, Hebbard and Schmitz (James Cook University).
- Dorney repository: I downloaded all eight files myself from raw.githubusercontent.com at commit 83e629fed3098881079fd9ac1c8bc13478ce69ed. Each file's SHA-256 matches its entry in the archived bundle, and each file's content (gunzipped for the .gz) equals the bundle's content byte for byte. The bundle's SHA-256 c2fa853553979a11b8cb665cf3d195cbe64530c755054f5768d05ab6ba46d17e matches the source record.

Values:
- Dorney, automated: my own parser (not the collector's) read both repository tables and matched every result by its locator. All 594 table cells were recorded (250 from `stat_summary.tsv`: 50 rows by 5 columns; 344 from the counts table: 172 rows by 2 columns). None was missed or duplicated and 0 values mismatched. The 4 F1 'NA' cells are stored as printed 'NA' with a null numeric value and an `undefined_reason`. The caller, cell line, library and depth in each qualifier and evaluation match the row. The three Huh7 counts (20, 17, 15) appear verbatim in Results.
- Dorney, by hand: I checked 41 values against the raw table rows, stratified as 4 per column across all six callers, the three depths and the three identities, 3 per cell line and library, and the 3 Huh7 values. All match.
- Kim, automated: my own parse of the Table 2 XML gives 26 rows by 3 numeric columns, 78 cells. All 78 were recorded and match. The column sums (48 conventional, 40 RNA-seq, 12 RNA-seq only) and the subtype counts of RNA-seq-only fusions (3 AML, 6 B-ALL, 2 T-ALL, 1 MPAL) agree with Results. The five text values are verbatim in the XML. Overall concordance, (40 + 44) / 104 = 80.8%, is consistent.
- Kim, by hand: I read all 83 values against the rendered table and the quoted sentences. All match.

Mapping:
- Metric, direction and unit are correct throughout: counts of known calls are `true-positive-count` higher; other calls and conventional counts are `count` unknown; false calls are `false-positive-count` lower; precision, recall and F1 are fractions; Kim's percentages are percent.
- The only Kim value mapped differently from its label is "1 minus specificity", stored as `false-positive-rate` lower. That is acceptable with the L1 caveat.
- Denominators (6, 53, 34, 48, and Spiked_Number per scenario) match the source and scripts. No uncertainty is reported anywhere, and the `unreported` entries are correct. Splits and datasets are correct.
- Configuration versions match the run scripts: FusionSeeker v1.0.1, Genion v1.1.0 and LongGF v0.1.2 (Run_GFSLGF.sh header); JAFFA 2.3 (path in RunJAFFAL.sh); minimap2 2.28. CTAT-LR-Fusion and GFSeeker versions are genuinely unstated. Kim's Arriba v2.4.0, STAR 2.7.7a, IGV 2.16.0 and HemaVision are verbatim in Methods.
- Minor, no change needed: RunJAFFAL.sh passes `annotation=genCode44` although Methods say JAFFAL used UCSC GENCODE v43.

Origin:
- Dorney: `independent_paper` is correct. The authors (Dorney, Wu, Hung, Hebbard, Schmitz) developed none of the six callers, and the preprint declares no competing interests.
- Kim: `independent_paper` is correct. None of the authors is an Arriba developer, and the article declares no conflicts.

Locators: all result locators resolve to the cited row and column or sentence. The configuration locators need D3.

Duplicates:
- Store: no source, DOI, repository or PMC ID from these batches is in data/entities, data/evidence or data/omics on main. The method duplicate is D1. FusionSeeker, LongGF and Arriba correctly reuse the stored methods. No CTAT-LR-Fusion, Genion, GFSeeker or union-of-callers method exists in the store.
- Other lit branches and worktrees: `git grep` of every `claude/lit-20261011-*` branch and a grep of every `../rewire-benchmark-data-lit-*` worktree for the DOIs, the repository name and the PMC ID found only this lane's and rna-other's ledger and scope-audit entries, and no batch.

Scope and judgements: as in the answer to question 6 above.

Summary: I checked every number in the approved text against stored values. Rounding: 0.3493 to 0.35, 0.2825 to 0.28, 0.4575 to 0.46, 0.2907 to 0.29, 0.2003 to 0.20, 0.1351 to 0.14, 0.0695 to 0.07, 0.0426 to 0.04. The MCF7 counts are the 'Total' rows, which equal the 10 Gb rows. The text names the author-reported FUSILLI, the Genomon co-author link and the truth-set biases (Tamura's consensus, the literature lists, Kim's conventional assays), and it does not recommend.

Not run: `npm test`, `npm run typecheck` and `npm run build`. Records were not to be edited and the batches are not in the store, so those runs belong to the integrator after the corrections. Receipts (`review.json`) and the dated review in `docs/reviews/use-cases/` are not written; they should be written from this file after D1 to D5 and L1 to L3 are applied, and the five judgements and the summary then re-pinned with `npm run use-cases:repin -- <dated review> <claim-id>...`. For each result's `review`, suggested method text: "Independent re-retrieval and hash check; reviewer's own parser compared every table cell; stratified hand check against the rendered table or quoted sentence", with reviewer "Claude research agent (reviewer-onc-2); no human review claimed", date 2026-10-11, and the artifact hash and retrieval URL of the result's own source.
