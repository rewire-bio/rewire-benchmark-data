# Review: VEP literature batch, 2026-10-14

Independent review of `data/omics/vep-literature-20261014/` (extraction commit b0ff762, branch `claude/vep-literature-pass`), following `.agents/skills/review-evidence/SKILL.md` and `docs/collection.md` section 5. Reviewer: a Claude (Opus 5.5) review agent that did not extract this batch. Automated review only; no human review is claimed, and nothing was reproduced.

Outcome: the batch passes after descriptive corrections made before it entered the store. All 2,461 values match their sources. All 3,365 records (3,364 extracted plus one method added in review) are `source_checked`, and the 13 relevance judgements are `source_checked` with pins.

## Sources and hashes

Every artifact was re-downloaded on 2026-10-14 (from 14:06Z) from the URL on its source record. All hashes match the source records and the archived copies in `artifacts/` decompress to the same bytes.

| Source record | Artifact | SHA-256 | Match |
| --- | --- | --- | --- |
| `vep-lit-20261014-source-livesey2025-article` | Europe PMC fullTextXML, PMC12016141 | `1735ee461ef192d9de67c914e9ad73d72d8aa255ea0e3479eb68cd8631d99fa2` | Yes |
| `vep-lit-20261014-source-livesey2025-supplementary-2` | Springer `13059_2025_3575_MOESM2_ESM.xlsx` | `1b0d792d1a5d3daa95545a7973cabb131c45e42c952e7e5a447a72deef1d1e70` | Yes |
| `vep-lit-20261014-source-proteingym-dms-substitutions-spearman-summary-144fe22` | `Summary_performance_DMS_substitutions_Spearman.csv` at 144fe22 | `ee61a7c09efbfbd8d9a6c9355092c798032a578fa58c6f6256b5da8778555fd4` | Yes |
| `vep-lit-20261014-source-proteingym-clinical-zero-shot-substitutions-auc-summary-144fe22` | clinical zero-shot substitutions AUC summary | `fbe453d1aaa6c30a1d0adf610f7fc23c36044a8e2548b178d316777383f8fe93` | Yes |
| `vep-lit-20261014-source-proteingym-clinical-supervised-substitutions-auc-summary-144fe22` | clinical supervised substitutions AUC summary | `f2e38aeac2624d87e7a35a5b16bd580de62c24db36973848e1d94ac3ce510359` | Yes |
| `vep-lit-20261014-source-proteingym-clinical-zero-shot-indels-auc-summary-144fe22` | clinical zero-shot indels AUC summary | `98a532c0e2c3d4720b73b7c05cf0dcf0419438c326761aaae3b788799f5aa836` | Yes |
| `run-doc-proteingym-readme-md-144fe22b` (existing) | `README.md` at 144fe22 | `321487a8de52c6cfa647a658f61150dd72e0acb0125470524fb94d1f8b23321a` | Yes |
| `profile-protocol-proteingym-proteingym-performance-dms-benchmarks-py-0002bc1b` (existing) | `performance_DMS_benchmarks.py` at 144fe22 | `0002bc1b031c02dc2d67fde53da092c8fd301415645e8e83b425b4183570eba2` | Yes |
| `profile-protocol-proteingym-reference-files-dms-substitutions-csv-a8f49801` (existing, newly cited) | `reference_files/DMS_substitutions.csv` at 144fe22 | `a8f498011532a74aa9fe556a50555a75e928c5837d19c06a87592ae04049b308` | Yes |
| `profile-protocol-proteingym-paper-xml-a58110e0` (existing, newly cited) | Europe PMC fullTextXML, PMC10723403 (ProteinGym paper) | `a58110e02c3efc8395c534d48630f577c3d45e90d48198b7f9989cf52600b045` | Yes |

## Values checked

`review/check_values.py` was written for this review. It does not import or copy the extractor's `extract/extract_vep.py` or `extract/ooxml.py`. It reads the workbook as sheet XML and the CSVs with the `csv` module, and for every result compares printed value, numeric value, raw cell, cell reference or CSV line, row label, column header, metric, qualifier, unit, direction, uncertainty, coverage, and the evaluation's protocol, dataset and configuration label. It also checks that every value cell in the extracted columns has exactly one result, that every evaluation has a result and that `claims.csv` agrees. Before relying on it, three errors were seeded into a copy of the batch (a changed printed value, a changed standard error, a result moved to another protocol); it reported all three, and the batch was restored byte for byte. It was run on the extractor's output and again on the corrected batch.

| Source | Table or column set | Results | Mismatches |
| --- | --- | --- | --- |
| Livesey and Marsh 2025, Supplementary Material 2 | Table S3, `rank_score` and `top_5_winrate` | 194 | 0 |
| | Table S5, `rank_score_direct` and `rank_score_indirect` | 194 | 0 |
| | Table S6, `rank_score` | 97 | 0 |
| | Table S7, `rank_score` | 97 | 0 |
| | Table S8, `rank_score` | 85 | 0 |
| ProteinGym 144fe22 | DMS substitutions Spearman summary, 18 metric columns x 97 models (97 bootstrap standard errors) | 1,746 | 0 |
| | Clinical zero-shot substitutions AUC | 13 | 0 |
| | Clinical supervised substitutions AUC | 17 | 0 |
| | Clinical zero-shot indels AUC | 18 | 0 |
| Total | | 2,461 | 0 |

Hand checks (seed 20261014): 8 workbook cells (S3 MOIpred_benign and gMVP `rank_score`; S5 PHACTboost `rank_score_direct`; S6 ESCOTT, Grantham, SIFT4G; S7 MVP, DEOGEN2), 6 DMS CSV cells (Progen3 3B Medium_MSA_depth and Function_Activity, Progen3 112m Function_Activity, ProtSSN (k=30, h=512) Taxa_Other_Eukaryote, xTrimoPGLM-100B-int4 High_MSA_depth, ESM2 (3B) Depth_5+), and 4 clinical indel rows (Unirep, RITA M, Progen2 L, RITA S). Each was read beside the raw cell or CSV line, with the column position counted against the header, and each was attached to the expected configuration and protocol. The article's printed figures agree with the workbook: CPT-1 92.8% and 66.2% (S3 92.81631101, 66.16379311), AlphaMissense 90.7% and 65.3% (S3 90.69319162, 65.25670498), SNPred and MetaRNN first and second in the clinical ranking (S8 rows 2 and 3).

Nulls and missing reasons: uncertainty on Livesey results is unreported (Fig. 2 and Fig. 3 error bars are not printed; Table S4 holds bootstrap counts only); the clinical indel file has no bootstrap column; ProteinGym comparison budgets are unreported and clinical aggregation is unextracted (the clinical scoring script was not read). These match the sources.

## Rulings on the extractor's open questions

1. **Runner protocol reuse for leaderboard rows.** Accepted. `rewire-proteingym-v1-3-dms-substitutions` is pinned to upstream 144fe22, uses the same 217 assays and labels, and its profile describes the same aggregation as `performance_DMS_benchmarks.py` lines 269 to 315, which produced the leaderboard columns. A protocol here fixes data, split, inputs and metric, not who ran it; the leaderboard rows and a future full-track Rewire run are the same protocol, and sharing it is what makes them comparable. The protocol profile already says a selected assay does not establish complete-track performance: partial Rewire runs must keep their own subset protocol (as the AMFR runs do), or they would sit beside full-track leaderboard rows on the use-case page.
2. **Origin of ProteinGym rows.** Changed from `author_reported` to `unreported` on all 145 ProteinGym evaluations. `author_reported` means the method's developers reported the result; most ProteinGym models are not by ProteinGym's authors. `paper_compilation` means copied from earlier papers; ProteinGym computes every metric with its own scripts, and that origin would also block comparison. `independent_paper` would be wrong for rows where the ProteinGym authors developed the model (for example Tranception, TranceptEVE, EVE) and for baselines whose scores the requester supplied (README, 'New baselines'). The summary files do not say who generated each model's scores, so `unreported` is the accurate value. Livesey and Marsh rows keep `independent_paper`: no VEP reference in the workbook's References sheet lists either author (one DMS dataset, PAX6, reference 5, is co-authored by Livesey). The existing ProteinGym evaluations in the store (`uc20260930-proteingym-amfr-eval-*`, `proteingym-evaluation-*`) use `author_reported` for the same kind of row; they were not edited here and should be audited.
3. **printed_value as shortest round-trip decimal.** Accepted. Every value cell is General format, so the workbook fixes no display precision; what Excel shows depends on column width (for example `20.77274813` for 3Cnet in S8). The shortest decimal that round-trips to the stored double is the closest stable reading of "as printed", and `raw_xml_value` and `workbook_number_format` keep the exact stored text. The article rounds to one decimal place in its text.
4. **Table S8 labels.** 'CPT' to CPT-1 and 'fathmm-XF' to FathmmXF accepted: Table S2 has exactly one CPT and one Fathmm-XF row, and the text names CPT-1 as the top population-free VEP in the clinical benchmark. Each result keeps its `source_anomaly`. 'CADD' as its own configuration with version unreported accepted: S3 prints CADD_1.6 and CADD_1.7 while S8 prints CADD and CADD_1.7, which suggests but does not state that 'CADD' is 1.6. COSMIS has no S2 row and is not mentioned in the text; its record says so. A related conflict is now recorded on the clinical protocol: the text says 83 VEPs (46 clinical-trained, 31 population-free, 6 population-tuned) and that CPT-1 outperforms 38 of 48 clinical-trained VEPs, while S8 has 85 rows. The dossier's explanation (split variants counted as one) is a hypothesis; the paper does not explain the difference. It does not change any printed rank score, so it is a limitation, not an evidence concern.
5. **mutationTCN rather than MTBAN.** Accepted. Table S2 labels it mutationTCN and cites Kim and Kim 2020 (Bioinformatics 36:2047, "Prediction of mutation effects using a deep temporal convolutional network"); only the prediction source is the MTBAN server. Whether those predictions are MTBAN's is not stated, so #154's MTBAN stays without results, as `coverage.json` says.
6. **MVP and fitCons.** MVP to `somatic-oncogenicity-20261009-method-mvp` accepted: it comes from dbNSFP 4.2 and is the missense predictor, not the metabolomics model `uc20260930-model-mvp`. fitCons corrected: dbNSFP carries an integrated fitCons score and cell-type fitCons scores, and the paper does not say which was used. Assigning it to `integrated_fitCons` would collapse an unidentified score into a specific one. A new family-level method `vep-lit-20261014-method-fitcons` was added and the configuration relinked to it.
7. **Method types.** Accepted. They follow the existing method records where those exist, and Table S2 otherwise: CPT-1, DeMaSk and Envision are supervised (trained on DMS data, Results), protein language models are foundation models, alignment and conservation methods are specialist or conventional pipeline. Two minor points are left as they are: BLOSUM62 is `conventional_pipeline` and Grantham is `specialist` (following the existing Grantham record), and COSMIS is `specialist` without a source classification; both are broad labels that make no false claim.
8. **ProteinGym bootstrap standard errors.** Accepted. `compute_bootstrap_standard_error_functional_categories` at 144fe22 resamples (protein, selection type) rows within each selection type and returns the standard deviation of the model's difference from the top-ranked model (lines 95 to 111 and 310 to 315), so the top model prints 0.0. Recording it as a standard error of that difference, with 10,000 resamples and the scope stated, matches the code. The clinical files' `Bootstrap_standard_error_AUC` stays `unresolved_spread` because the clinical script was not read.
9. **pairwise-win-rate.** Accepted. The definition matches the Methods ('Spearman's correlation and rank score', 'AUROC and AUPRC'): wins over times tested per pair, averaged over the other VEPs, 0 to 100, relative to the comparison set. It does not respell an existing concept. No external match was found (EBI OLS search of STATO, EDAM, OBI and NCIT for "win rate", 2026-10-14, returned nothing relevant). The top-5 restriction is correctly carried in `metric_qualifier`.
10. **The 13 relevance judgements.** All accepted as proxy, with limitations revised (below). None is direct: each scores variants pan-gene, without the use case's inputs (phenotype, pedigree, ENIGMA specification, a defined stability construct).
    - Rare-disease candidate ranking (9). The use case excludes balanced pathogenic/benign classification as a measure of case-level diagnostic performance; the four clinical judgements now say so. Proxy still holds: the variant-effect evidence these tools provide is one input to candidate ranking. The five DMS judgements are proxy because the authors show that DMS and clinical rankings agree closely for population-free and population-tuned VEPs (Fig. 4); they are strata of one comparison group, so they display together.
    - BRCA1/BRCA2 (3). Proxy for choosing a PP3/BP4 tool. Not BRCA-specific, not calibrated to evidence strength, and whether BRCA1 or BRCA2 is in the test sets is not stated.
    - Protein stability (1). Proxy only through the Function_Stability column. Each evaluation also carries 17 results on endpoints the use case excludes; a constraint now says only the Stability result applies. The stability column is 66 assays, 64 of them from the Tsuboyama proteolysis study that also supplies the AMFR assay the use case already cites, so it is not independent of that evidence.
    - Clinical AUROC truth sets. The Livesey judgements now carry the authors' caveats: the gnomAD negative class contains unclassified pathogenic variants; allele-frequency features gain from circularity; no training variants were removed. The ProteinGym clinical judgements now cite the ProteinGym paper: supervised methods are scored on all ClinVar labels and are likely overestimated; frequency-trained models leak through ClinVar benign labels; conservation is a ClinVar criterion, so zero-shot models are not free of circularity; labels are biased to well-studied genes and European ancestry; indel benign labels are common gnomAD pseudocontrols and only short in-frame indels are included. The extractor's indel rationale said the set includes frameshifts; the paper says frameshifts were filtered out, so the rationale was corrected.

## Changes made

All are descriptive corrections to the batch before it entered the store, made by `review/signoff.py`, which refuses to run on anything but the extractor's `batch.jsonl` (SHA-256 `96b3318f89b08edad03e56cb376f86c7d67bad6a64fc4e286f539052e63299c9`).

- Origin `unreported` on the 145 ProteinGym evaluations (ruling 2).
- New method `vep-lit-20261014-method-fitcons`; `vep-lit-20261014-config-livesey2025-fitcons` relinked to it and its version text says the fitCons score is unstated (ruling 6).
- Clinical protocol limitation on the 83 versus 85 VEP count (ruling 4).
- ProteinGym clinical protocols: the unsourced "ClinVar-type assertions" limitation replaced with the paper's description of the label sets; the supervised protocol gained it alongside its overlap caveat. Each cites `profile-protocol-proteingym-paper-xml-a58110e0`.
- Judgement limitations, constraints and citations revised (ruling 10); one rationale corrected (indels).
- Review objects on every record; `reviewed_evaluations` on every judgement. The dataset subsets' review hash now names the README they were read from, not a summary CSV.
- `coverage.json` status, method count (28) and the added ID. Pointers to this review in the dossier and `research.md`.

No value, ID, locator or source hash was changed.

## Remaining gaps

- The existing ProteinGym evaluations in the store use `author_reported` for leaderboard rows (ruling 2); they need an audit and a reviewed change, outside this batch.
- A judgement has no field that selects results by qualifier, so the stability judgement relies on its constraint text to point readers at Function_Stability.
- The clinical summary script and per-protein clinical files were not read; clinical aggregation and the clinical bootstrap column remain unverified.
- The gaps the extractor recorded stand: earlier Livesey and Marsh editions, CAGI6 Annotate-All-Missense, Tabet et al. 2024, the two 2026 preprints, other ProteinGym summaries, figures, and the #155 non-coding predictors.
- `evidence_checked` on the seven use cases searched was not updated in this review; the docs ask each literature pass to set it.
- No use-case summary claim was drafted.
