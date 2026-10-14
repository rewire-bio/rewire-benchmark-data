"""Use-case records for rewire-benchmark-data #151 and #152, their baseline claims and the
relevance judgements drafted for them. All are drafts (needs_review); a separate reviewer decides."""

COLLECTOR = "Collector agent for the 2026-10-14 VEP use-case pass (Claude Opus 5.5); extraction only, not a review. Pending an independent review-evidence pass."
TODAY = "2026-10-14"
CONSTRAINTS = ["Inspect every linked evaluation's source locator before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results.",
               "Compare rows only within this protocol."]
TRANSCRIBED = "Transcribed from the source; no reproduction by Rewire and no human scientific review."

# Existing protocols and the sources their judgements rest on (from the reviewed first pass).
LIV_S2 = "vep-lit-20261014-source-livesey2025-supplementary-2"
LIV_ART = "vep-lit-20261014-source-livesey2025-article"
PG_PAPER = "profile-protocol-proteingym-paper-xml-a58110e0"
PG_CLIN_ZS = "vep-lit-20261014-source-proteingym-clinical-zero-shot-substitutions-auc-summary-144fe22"
PG_CLIN_SUP = "vep-lit-20261014-source-proteingym-clinical-supervised-substitutions-auc-summary-144fe22"
PG_DMS = "vep-lit-20261014-source-proteingym-dms-substitutions-spearman-summary-144fe22"
PG_README = "run-doc-proteingym-readme-md-144fe22b"
PG_REF = "profile-protocol-proteingym-reference-files-dms-substitutions-csv-a8f49801"
WITHIN_PROTEIN = ("Correlation is assessed within each protein, so the ranking does not test whether scores are comparable across genes; the authors report that DMS and clinical "
                  "rankings agree closely for population-free and population-tuned VEPs (Pearson r 0.978 and 0.994) and less for clinical-trained VEPs (Results, Fig. 4).")
LIVESEY_DMS = [
    ("livesey2025-dms-all", "DMS benchmark, all 36 DMS sets", 1, "Average pairwise win rate of each missense VEP against 96 others, by |Spearman| with 36 human DMS datasets",
     "Supplementary Material 2 Table S3; Methods 'Spearman's correlation and rank score'", ["DMS phenotypes are chosen per protein and are not pathogenicity labels.",
     "Rank scores are relative to the VEP set compared; they are not a correlation and cannot be compared with other tables."]),
    ("livesey2025-dms-direct", "DMS benchmark, direct assays only", 2, "Average pairwise win rate by |Spearman| with the DMS assays the authors class as direct",
     "Supplementary Material 2 Table S5; Results", ["Which assays are direct is not fully recoverable from Table S1 (four blank assay descriptions)."]),
    ("livesey2025-dms-indirect", "DMS benchmark, indirect assays only", 3, "Average pairwise win rate by |Spearman| with the DMS assays the authors class as indirect",
     "Supplementary Material 2 Table S5; Results", ["Which assays are indirect is not fully recoverable from Table S1."]),
    ("livesey2025-dms-snv", "DMS benchmark, SNV-accessible substitutions", 4, "Average pairwise win rate by |Spearman| restricted to substitutions reachable by one nucleotide change",
     "Supplementary Material 2 Table S6; Results", []),
    ("livesey2025-dms-snv-filled", "DMS benchmark, SNV-accessible, gaps filled", 5, "Average pairwise win rate by |Spearman| on SNV-accessible substitutions with missing predictions set to each VEP's most benign score",
     "Supplementary Material 2 Table S7; Results", []),
]


def claim_review(note, sha=None, url=None):
    r = {"method": ["scope-review"], "method_note": "Judgement drafted against the use case's question, inputs and exclusions.",
         "reviewer": ["claude"], "reviewer_note": COLLECTOR, "date": TODAY, "note": note}
    if sha:
        r["artifact_sha256"], r["retrieval_url"] = sha, url
    return r


def judgement(uc, uc_slug, protocol, short, relevance, endpoint, rationale, limitations, citations, headline, group, title, stratum, order, extra_constraints=()):
    return {"id": f"use-case-mapping-vep-uc-20261014-{uc_slug}-{short}", "kind": "claim",
            "name": f"Relevance of {protocol} to {uc}", "description": "Relevance judgement drafted by the extraction agent; not reviewed.",
            "status": "needs_review", "facets": {}, "source_ids": sorted({c["source_id"] for c in citations}),
            "links": [{"relation": "subject", "target_id": uc}],
            "attributes": {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance, "endpoint": endpoint,
                           "rationale": rationale, "constraints": CONSTRAINTS + list(extra_constraints), "limitations": limitations + [TRANSCRIBED],
                           "citation_locators": citations, "source_locator": "; ".join(f"{c['source_id']}: {c['locator']}" for c in citations),
                           "headline_metric": headline, "comparison_group": group, "comparison_title": title, "stratum_label": stratum, "stratum_order": order,
                           "reason": "VEP use-case pass 2026-10-14: relevance of a protocol to a new use case (rewire-benchmark-data #151/#152).",
                           "review": claim_review("Drafted, not reviewed.")}}


def use_case_records(P, sid, tool_ids, prot, idx):
    for pid in [f"vep-lit-20261014-protocol-{p[0]}" for p in LIVESEY_DMS] + ["vep-lit-20261014-protocol-livesey2025-clinical-auroc",
                "vep-lit-20261014-protocol-proteingym-clinical-zero-shot-substitutions-auc-144fe22", "vep-lit-20261014-protocol-proteingym-clinical-supervised-substitutions-auc-144fe22",
                "rewire-proteingym-v1-3-dms-substitutions", "brca-20261009-protocol-ramadane2025-pp3-bp4",
                "uc-clinical-20260930-enigma-brca1-generic-protocol", "uc-clinical-20260930-enigma-brca2-generic-protocol"]:
        assert pid in idx, pid
    for s in (LIV_S2, LIV_ART, PG_PAPER, PG_CLIN_ZS, PG_CLIN_SUP, PG_DMS, PG_README, PG_REF, "brca-20261009-source-ramadane2025", "uc-clinical-20260930-source-enigma"):
        assert s in idx, s
    out = []
    PEJ, BQ, STN, TEJ = sid["pejaver2022"], sid["bergquist2025"], sid["stenton2024"], sid["tejura2024"]
    UC151, S151 = "use-case-missense-pp3-bp4-calibrated-evidence", "missense-pp3-bp4-calibrated-evidence"
    UC152, S152 = "use-case-protein-variant-effect-prediction", "protein-variant-effect-prediction"
    genome_wide = "Calibration is an average over genes; Tejura et al. 2024 found that about 70% of the gene-level REVEL and BayesDel intervals with enough control variants exceeded the incorrect predictions the genome-wide recommendations imply (Summary)."
    devs = "The developers of BayesDel, MutPred2, REVEL and VEST4, the four tools that reach PP3_Strong, and of MPC are authors of Pejaver et al. 2022; those evaluations are recorded as author_reported."
    j151 = []
    j151.append(judgement(UC151, S151, prot["intervals"], "pejaver2022-intervals", "direct",
        "Score interval per ACMG/AMP evidence strength (BP4 and PP3, Supporting to Very Strong) for 13 missense predictors, ClinGen SVI calibration on ClinVar 2019 missense variants",
        "Direct: these are the calibrated thresholds the use case asks for, from the calibration behind the ClinGen PP3/BP4 recommendation, for predictors usable in any gene.",
        [genome_wide, devs, "Table S1 point estimates and confidence bounds were not retrieved; only the printed intervals are recorded.",
         "Labels are ClinVar classifications, which the authors assume were not driven by computational evidence (Stenton et al. 2024, Table 1)."],
        [{"source_id": PEJ, "locator": "Table 2 and footnote; Methods; author list; references 13, 18, 19, 23, 25"}, {"source_id": TEJ, "locator": "Summary"}, {"source_id": STN, "locator": "Table 1"}],
        "evidence-strength-score-interval", "clingen-svi-pp3-bp4-calibration", "ClinGen SVI PP3/BP4 calibrations", "Pejaver et al. 2022: four-level intervals, 13 tools", 1,
        ["numeric_value of an interval result is the bound a score must reach for that strength; read printed_value for the interval itself."]))
    j151.append(judgement(UC151, S151, prot["bergquist"], "bergquist2025-point-intervals", "direct",
        "Score interval per point value (−4 to +4, including ±3 and indeterminate) for BayesDel, MutPred2, REVEL, VEST4, AlphaMissense, ESM1b and VARITY_R",
        "Direct: extends the ClinGen calibration to three newer predictors with the same data and method, and gives the points-scale intervals.",
        [genome_wide, "MutPred2 and REVEL were co-developed by authors of Bergquist et al. 2025.",
         "The developer thresholds of AlphaMissense (0.564) and ESM1b (−7.5) do not reach Supporting under this calibration (Results).",
         "EVE could not be calibrated reliably (about half the benign variants unscored) and is not included (Results)."],
        [{"source_id": BQ, "locator": "Table 1 and caption; Materials and Methods; Results"}, {"source_id": TEJ, "locator": "Summary"}],
        "evidence-strength-score-interval", "clingen-svi-pp3-bp4-calibration", "ClinGen SVI PP3/BP4 calibrations", "Bergquist et al. 2025: points scale, 7 tools", 2,
        ["numeric_value of an interval result is the bound a score must reach for that strength; read printed_value for the interval itself."]))
    j151.append(judgement(UC151, S151, prot["lr"], "pejaver2022-developer-threshold-lr", "direct",
        "Local positive likelihood ratio at the developer-recommended thresholds of SIFT, PolyPhen-2 and CADD, against the PP3 Supporting cut-off of 2.406",
        "Direct: tests the common practice of applying developer thresholds as PP3 evidence; none reaches Supporting.",
        [genome_wide],
        [{"source_id": PEJ, "locator": "Table 3 and footnote; Results 'Investigation of commonly used developer-recommended thresholds'"}],
        "likelihood-ratio", "clingen-svi-pp3-bp4-calibration", "ClinGen SVI PP3/BP4 calibrations", "Developer thresholds: local likelihood ratio", 3))
    j151.append(judgement(UC151, S151, prot["fraction"], "pejaver2022-developer-threshold-gnomad-fraction", "proxy",
        "Fraction of the gnomAD reference set called pathogenic by SIFT, PolyPhen-2 and CADD at their developer thresholds, against a 4.41% prior",
        "Proxy: shows over-calling at uncalibrated thresholds on unlabelled population variants; it is not a measure of evidence strength.",
        ["The gnomAD set is unlabelled; a fraction above the prior suggests false positive calls but does not count them."],
        [{"source_id": PEJ, "locator": "Table 3 last column; Results 'Investigation of commonly used developer-recommended thresholds'"}],
        "proportion", "clingen-svi-pp3-bp4-calibration", "ClinGen SVI PP3/BP4 calibrations", "Developer thresholds: gnomAD fraction called pathogenic", 4))
    j151.append(judgement(UC151, S151, "vep-lit-20261014-protocol-livesey2025-clinical-auroc", "livesey2025-clinical-auroc", "proxy",
        "Average pairwise win rate by per-protein AUROC separating ClinVar P/LP from gnomAD v4.1 missense variants in 819 proteins",
        "Proxy: ranks many more predictors than are calibrated, which helps choose candidates for calibration, but it measures discrimination within proteins, not evidence strength at a threshold.",
        ["No calibration to ACMG/AMP evidence strength and no thresholds.",
         "The negative class is gnomAD v4.1 missense variants not classed pathogenic ('putatively benign'); the authors note it will include unclassified pathogenic variants, particularly in recessive and incomplete-penetrance genes (Results).",
         "VEPs that use allele frequency as a feature likely benefit from circularity, because frequency is used to classify variants as benign (Discussion); the gnomAD negative class reduces but does not remove this.",
         "No training variants were removed; the authors attribute most of the clinical-trained VEPs' advantage over the DMS ranking to circularity (Results, Fig. 4).",
         "AUROC is computed per protein, so the ranking does not test whether scores are comparable across genes, which genome-wide thresholds assume."],
        [{"source_id": LIV_S2, "locator": "Supplementary Material 2 Table S8; Methods 'ClinVar and gnomAD data', 'AUROC and AUPRC'"}],
        "pairwise-win-rate", "livesey-marsh-2025-vep-ranking", "Livesey and Marsh 2025 VEP rankings", "Clinical benchmark, ClinVar P/LP versus gnomAD missense", 6))
    for short, stratum, order, endpoint, loc, lims in LIVESEY_DMS:
        j151.append(judgement(UC151, S151, f"vep-lit-20261014-protocol-{short}", short, "proxy", endpoint,
            "Proxy: DMS-based ranking avoids clinical-label circularity, which the calibrations cannot fully remove, and so is an independent check on which predictors to calibrate; it gives no thresholds or evidence strengths.",
            lims + ["No calibration to ACMG/AMP evidence strength and no thresholds.", WITHIN_PROTEIN],
            [{"source_id": LIV_S2, "locator": loc}], "pairwise-win-rate", "livesey-marsh-2025-vep-ranking", "Livesey and Marsh 2025 VEP rankings", stratum, order))
    j151.append(judgement(UC151, S151, "vep-lit-20261014-protocol-proteingym-clinical-zero-shot-substitutions-auc-144fe22", "proteingym-clinical-zero-shot-substitutions-auc-144fe22", "proxy",
        "Average over proteins of AUC separating pathogenic from benign clinical substitutions, zero-shot models",
        "Proxy: discrimination of ClinVar missense labels by zero-shot models, some of which are calibration candidates (for example ESM1b); no thresholds or evidence strengths.",
        ["Only 13 models are listed; the file's completeness is not stated.", "Averaging and uncertainty construction not verified for the clinical summaries.",
         "Clinical labels are biased towards heavily studied proteins, such as well-known cancer genes, and towards European ancestry (ProteinGym paper, Limitations)."],
        [{"source_id": PG_CLIN_ZS, "locator": "Summary_performance_clinical_substitutions_AUC.csv (zero-shot); README lines 22-28, 106"},
         {"source_id": PG_PAPER, "locator": "ProteinGym NeurIPS 2023 paper (PMC10723403): 'Clinical datasets', Appendix A.3.2, Appendix 'Limitations' ('Bias', 'Circularity')"}],
        "auroc", "proteingym-clinical-144fe22", "ProteinGym clinical benchmark (commit 144fe22)", "Substitutions, zero-shot", 1))
    j151.append(judgement(UC151, S151, "vep-lit-20261014-protocol-proteingym-clinical-supervised-substitutions-auc-144fe22", "proteingym-clinical-supervised-substitutions-auc-144fe22", "proxy",
        "Average over proteins of AUC for supervised clinical predictors from dbNSFP 4.4a",
        "Proxy: includes most calibrated tools (for example REVEL, BayesDel, VEST4), but scores them on all ClinVar labels without thresholds.",
        ["Do not compare with the zero-shot rows as if on equal footing.",
         "Performance is reported on all available ClinVar labels, so supervised methods whose training data overlap these labels are likely overestimated; models trained on population frequencies leak further, because most ClinVar benign labels rest on observed frequency (ProteinGym paper, 'Clinical datasets', supervised benchmark).",
         "Clinical labels are biased towards heavily studied proteins, such as well-known cancer genes, and towards European ancestry (ProteinGym paper, Limitations)."],
        [{"source_id": PG_CLIN_SUP, "locator": "Summary_performance_clinical_substitutions_AUC.csv (supervised); README line 106"},
         {"source_id": PG_PAPER, "locator": "ProteinGym NeurIPS 2023 paper (PMC10723403): 'Clinical datasets', Appendix A.3.2, Appendix 'Limitations' ('Bias', 'Circularity')"}],
        "auroc", "proteingym-clinical-144fe22", "ProteinGym clinical benchmark (commit 144fe22)", "Substitutions, supervised predictors", 2))
    j151.append(judgement(UC151, S151, "brca-20261009-protocol-ramadane2025-pp3-bp4", "ramadane2025-pp3-bp4", "proxy",
        "Log2 likelihood ratio of BP4 and PP3 score ranges for AlphaMissense, FoldX ΔΔG and BayesDel on 1,519 BRCA1 RING and BRCT missense variants with MAVE labels",
        "Proxy: shows how genome-wide and gene-specific thresholds perform in one gene against functional labels; the use case concerns genes with no gene-specific calibration.",
        ["BRCA1 RING and BRCT domains only; functional labels stand in for pathogenicity.",
         "Some thresholds were chosen on the same variants (see the protocol's limitations)."],
        [{"source_id": "brca-20261009-source-ramadane2025", "locator": "Table 1; Material and methods paragraph 4; Results paragraphs 8-12"}],
        "log2-likelihood-ratio", "gene-level-checks-of-calibrated-thresholds", "Gene-level checks of calibrated thresholds", "BRCA1 MAVE, Ramadane-Morchadi et al. 2025", 1))
    for gene in ("brca1", "brca2"):
        j151.append(judgement(UC151, S151, f"uc-clinical-20260930-enigma-{gene}-generic-protocol", f"enigma-{gene}-generic", "proxy",
            f"{gene.upper()} BP4 coverage and erroneous PP3 assignment when the generic Pejaver BayesDel thresholds are applied to functional reference variants",
            "Proxy: a gene-level check of the genome-wide BayesDel thresholds in a gene that has an expert-panel specification; not a classification outcome.",
            ["Functional proxy labels, not independent clinical classifications.", "Primary narrative only; complete Supplementary Table S4 unavailable (protocol limitations)."],
            [{"source_id": "uc-clinical-20260930-source-enigma", "locator": "Generic BayesDel threshold comparison (see the protocol record)"}],
            "proportion", "gene-level-checks-of-calibrated-thresholds", "Gene-level checks of calibrated thresholds", f"{gene.upper()} generic BayesDel thresholds (ENIGMA)", 2 if gene == "brca1" else 3))

    j152 = []
    j152.append(judgement(UC152, S152, "rewire-proteingym-v1-3-dms-substitutions", "rewire-proteingym-v1-3-dms-substitutions", "direct",
        "Average_Spearman: mean over proteins of assay-level Spearman correlation between zero-shot scores and DMS readouts, 217 substitution assays, with breakdowns by MSA depth, function type, taxon and mutational depth",
        "Direct: ranks 97 zero-shot predictors by how well they order substitution effects measured by DMS across many proteins, which is the choice the use case asks for; the MSA-depth breakdown speaks to proteins with shallow alignments.",
        ["Averages over proteins do not predict performance on a single protein of interest.",
         "Leaderboard rows were computed by the ProteinGym maintainers with their scoring scripts (origin unreported); no Rewire run on the full track.",
         "Assays include multiple substitutions; Depth_1 is the singles-only column.",
         "Bootstrap standard errors are relative to the top model (the top row prints 0.0)."],
        [{"source_id": PG_DMS, "locator": "Summary_performance_DMS_substitutions_Spearman.csv; performance_DMS_benchmarks.py lines 269-348"},
         {"source_id": PG_README, "locator": "README line 22 (217 DMS assays) and lines 66-70"}],
        "spearman-correlation", "proteingym-dms-144fe22", "ProteinGym zero-shot DMS substitutions (commit 144fe22)", "All assays (Average_Spearman) and breakdowns", 1,
        ["Use Average_Spearman as the headline; the other columns are breakdowns of the same evaluation and must be read with their metric_qualifier."]))
    for short, stratum, order, endpoint, loc, lims in LIVESEY_DMS:
        j152.append(judgement(UC152, S152, f"vep-lit-20261014-protocol-{short}", short, "direct", endpoint,
            "Direct: ranks 97 predictors by agreement with DMS measurements of human proteins, with ClinVar and gnomAD variants removed from the DMS sets, which is the comparison the use case needs; limited to human proteins.",
            lims + ["Human proteins only (36 DMS sets, one per protein).",
                    "Several VEPs were trained on DMS data (for example Envision, DeMaSk, CPT-1); overlap with these 36 sets is not stated for each.",
                    "Per-protein correlations are in the figshare deposit, not retrieved; averages do not predict a single protein."],
            [{"source_id": LIV_S2, "locator": loc}, {"source_id": LIV_ART, "locator": "Methods 'DMS datasets'"}], "pairwise-win-rate", "livesey-marsh-2025-vep-ranking",
            "Livesey and Marsh 2025 VEP rankings", stratum, order))

    checked = {"date": TODAY, "cutoff_date": TODAY, "records": ["docs/reviews/use-cases/vep-use-cases-2026-10-14.md", "data/omics/search-ledger.jsonl"]}
    uc_review = {"method": ["scope-review"], "reviewer": ["claude"], "reviewer_note": COLLECTOR, "date": TODAY,
                 "note": "Drafted by the collector agent from the GitHub issue and the cited sources; not reviewed. No new model execution, independent replication, qualified human scientific review or clinical validation."}
    uc151 = {"id": UC151, "kind": "use_case", "name": "Use calibrated computational evidence for missense variants (PP3/BP4)",
             "description": "Which predictor and score thresholds give calibrated ACMG/AMP computational evidence (PP3/BP4) for a missense variant in a gene without a gene-specific calibration, and at what strength?",
             "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
             "source_ids": [PEJ, BQ, STN, TEJ],
             "links": [{"relation": "assessed_by", "target_id": j["attributes"]["value"]} for j in j151],
             "attributes": {
                 "slug": S151,
                 "question": "Which predictor and score thresholds give calibrated ACMG/AMP computational evidence (PP3/BP4) for a missense variant in a gene without a gene-specific calibration, and at what strength?",
                 "intended_users": ["Clinical scientists classifying germline variants under ACMG/AMP criteria", "Variant curation expert panels deciding whether to adopt or replace genome-wide thresholds"],
                 "decision": "Choose one predictor in advance and the score thresholds at which it supplies PP3 or BP4 evidence at Supporting, Moderate or Strong strength, for a missense variant in a gene with no gene-specific calibration.",
                 "inputs": ["A germline missense variant on a stated transcript and genome build",
                            "The chosen predictor's precomputed score at a pinned version",
                            "Whether a gene- or region-specific specification exists that supersedes genome-wide thresholds"],
                 "output": "Calibrated score intervals for each evidence strength per predictor, the highest strength each reaches, the calibration data and its limits, and independent rankings of the same predictors. No variant classification.",
                 "setting": "Germline missense variants assessed under ACMG/AMP criteria. The genome-wide calibrations use ClinVar pathogenic and benign missense variants rare in gnomAD, from genes with at least one pathogenic variant, with tools' training variants removed where available, and a prior probability of pathogenicity of 4.41% estimated from gnomAD.",
                 "exclusions": ["Genes with an expert-panel specification that sets its own thresholds (BRCA1/BRCA2 is a separate use case)",
                                "Splicing, in-frame indel, protein-truncating and non-coding variants",
                                "Combining several predictors, or counting PP3 together with overlapping evidence such as PM1 or allele frequency beyond the recommended caps",
                                "Somatic variant oncogenicity",
                                "Final variant classification or patient management"],
                 "clinical_scope": "Clinical research on the evidence strength of computational predictions. Calibrated thresholds hold on average across genes; they do not classify a variant and do not replace expert review.",
                 "evidence_gaps": [
                     "The four tools that reach PP3_Strong in Pejaver et al. 2022 (BayesDel, MutPred2, REVEL, VEST4) each have a developer among that paper's authors; no independent recalibration of them is in the store.",
                     "The calibrations are genome-wide; Tejura et al. 2024 show that gene-level performance of REVEL and BayesDel often departs from them. No gene-level calibration is extracted.",
                     "Thirteen predictors have four-level intervals (Pejaver et al. 2022) and seven have points-scale intervals (Bergquist et al. 2025). Newer predictors ranked highly by Livesey and Marsh 2025 (for example popEVE, CPT-1) have no ClinGen calibration in the store.",
                     "Pejaver et al. 2022 Table S1 (point estimates and one-sided confidence bounds) was not retrieved.",
                     "A 2026 Genetics in Medicine calibration of machine-learning predictors (doi:10.1016/j.gim.2026.102606) is closed access and was not retrieved; the BayesQuantify (J Med Genet 2025) and P-KNN (bioRxiv 2025) joint calibrations were found but not extracted.",
                     "Evidence yield in real genomes (Stenton et al. 2024 Table 2) and reclassification impact (Dubé et al. 2026, Genet Med Open) were found but not extracted.",
                     "The Livesey and Marsh and ProteinGym rankings measure discrimination, not calibrated evidence strength; they help choose which predictors to calibrate, not which thresholds to apply.",
                     "Qualified human scientific review is outstanding; automated transcription does not establish replication."],
                 "search_terms": ["PP3", "BP4", "ACMG/AMP", "missense", "in silico predictor", "calibration", "evidence strength", "ClinGen", "REVEL", "BayesDel", "AlphaMissense", "VUS"],
                 "citation_locators": [{"source_id": PEJ, "locator": "Tables 2-4; Methods; Discussion"}, {"source_id": BQ, "locator": "Table 1; Results"},
                                       {"source_id": STN, "locator": "Table 1 (guidance and limitations)"}, {"source_id": TEJ, "locator": "Summary"}],
                 "collection_plan": {
                     "status": "planned",
                     "comparison_question": "On missense variants classified after every calibration and training cutoff, do the published PP3/BP4 thresholds give the stated likelihood ratios, overall and per gene where labels allow?",
                     "baselines": ["SIFT at its developer threshold and at its calibrated thresholds", "Each predictor's genome-wide ClinGen thresholds"],
                     "outcomes": ["Interval likelihood ratio per evidence strength with confidence intervals", "Share of variants left indeterminate", "Spread of likelihood ratios across genes"],
                     "validation_requirements": ["Labels dated after the calibration set and each predictor's training data", "Exclude classifications that used PP3 or BP4",
                                                 "Report developer and author overlap for each predictor", "Freeze predictor score versions"],
                     "next_step": "Retrieve Pejaver et al. 2022 Table S1 and search for independent post-2022 recalibrations before deciding whether a Rewire recalibration is needed."},
                 "review": uc_review, "evidence_checked": checked}}
    uc152 = {"id": UC152, "kind": "use_case", "name": "Predict missense variant effects in a protein of interest",
             "description": "Which predictor best ranks the functional effects of amino acid substitutions in a given protein, with or without an alignment or structure?",
             "status": "needs_review", "facets": {"areas": ["proteins-complexes"], "contexts": ["research"]},
             "source_ids": [PG_README, PG_DMS, LIV_ART, LIV_S2],
             "links": [{"relation": "assessed_by", "target_id": j["attributes"]["value"]} for j in j152],
             "attributes": {
                 "slug": S152,
                 "question": "Which predictor best ranks the functional effects of amino acid substitutions in a given protein, with or without an alignment or structure?",
                 "intended_users": ["Researchers planning or interpreting deep mutational scans", "Protein scientists choosing variants for functional assays",
                                    "Computational biologists selecting a zero-shot variant effect predictor"],
                 "decision": "Choose a predictor, or a short list, to rank substitutions in the target protein before or alongside an assay, given whether a deep alignment, a structure or labelled data are available.",
                 "inputs": ["Wild-type protein sequence and the substitutions to score", "Optionally a multiple sequence alignment, an experimental or predicted structure, and labelled assay data",
                            "The readout of interest (activity, binding, expression, stability or organismal fitness)"],
                 "output": "Per-predictor rank correlation with deep mutational scanning readouts across many proteins, with breakdowns by alignment depth, function type and taxon, and pairwise win rates on human proteins. No guarantee for a specific protein.",
                 "setting": "Zero-shot scoring of amino acid substitutions benchmarked against DMS assays: ProteinGym at commit 144fe22 (217 substitution assays across many organisms) and Livesey and Marsh 2025 (36 human DMS sets with ClinVar and gnomAD variants removed).",
                 "exclusions": ["Clinical pathogenicity classification (see the PP3/BP4 and rare-disease use cases)", "Folding stability alone (see the protein stability use case)",
                                "Supervised models trained on the target assay", "Insertions and deletions", "Design of new sequences"],
                 "clinical_scope": "Research use. Agreement with DMS readouts does not establish clinical pathogenicity.",
                 "evidence_gaps": [
                     "Benchmarks report averages over proteins; performance on a single protein varies and is not predicted by the averages.",
                     "ProteinGym supervised DMS results are stored as tasks from the 2023 paper, not as protocols, so they cannot be linked here; the supervised summaries at commit 144fe22 were not extracted.",
                     "ProteinGym zero-shot DMS AUC, MCC, NDCG and top-recall summaries at commit 144fe22 were not extracted.",
                     "Livesey and Marsh rank scores are relative to the 97 compared predictors; per-protein Spearman values are in the figshare deposit, not retrieved.",
                     "No Rewire run of a full DMS track exists; the ProteinGym rows are leaderboard values.",
                     "Qualified human scientific review is outstanding; automated transcription does not establish replication."],
                 "search_terms": ["deep mutational scanning", "DMS", "MAVE", "variant effect prediction", "zero-shot", "ProteinGym", "protein language model", "fitness", "Spearman"],
                 "citation_locators": [{"source_id": PG_README, "locator": "README line 22 and lines 39-70"}, {"source_id": PG_DMS, "locator": "Summary_performance_DMS_substitutions_Spearman.csv"},
                                       {"source_id": LIV_ART, "locator": "Methods 'DMS datasets'; Results 'Comparison of VEP performance using DMS data'"}, {"source_id": LIV_S2, "locator": "Tables S3, S5-S7"}],
                 "review": uc_review, "evidence_checked": checked}}
    bl151 = {"id": f"use-case-baseline-{S151}", "kind": "claim", "name": "Baseline: Use calibrated computational evidence for missense variants (PP3/BP4)",
             "description": "Baseline method for the use case, drafted by the extraction agent; not reviewed.", "status": "needs_review", "facets": {},
             "source_ids": [PEJ], "links": [{"relation": "subject", "target_id": UC151}],
             "attributes": {"field": "baseline", "value": "SIFT", "method_ids": ["somatic-oncogenicity-20261009-method-sift"],
                            "rationale": "SIFT is a conservation-based predictor that predates machine-learning ensembles; Pejaver et al. 2022 describe SIFT, PolyPhen-2 and CADD as among the first and most frequently used in silico tools, calibrate SIFT (Table 2) and test its developer threshold (Table 3). PolyPhen-2 and CADD are trained classifiers.",
                            "source_locator": f"{PEJ}: Results 'Investigation of commonly used developer-recommended thresholds'; Tables 2 and 3",
                            "review": claim_review("Drafted, not reviewed.")}}
    bl152 = {"id": f"use-case-baseline-{S152}", "kind": "claim", "name": "Baseline: Predict missense variant effects in a protein of interest",
             "description": "Baseline method for the use case, drafted by the extraction agent; not reviewed.", "status": "needs_review", "facets": {},
             "source_ids": [PG_README, "qa-descriptions-20261011-a-source-hopf2017"], "links": [{"relation": "subject", "target_id": UC152}],
             "attributes": {"field": "baseline", "value": "Site-independent alignment model", "method_ids": ["uc20260930-method-site-independent"],
                            "rationale": "An alignment-based model that scores each position separately, without the dependencies between positions that EVmutation adds, and with no neural network. It is the first and simplest model in the ProteinGym substitution baselines table (input modality MSA; Hopf et al. 2017).",
                            "source_locator": f"{PG_README}: README lines 66-70",
                            "review": claim_review("Drafted, not reviewed.")}}
    out += [uc151, uc152, bl151, bl152] + j151 + j152
    for j in j151 + j152:
        assert j["attributes"]["value"] in idx or j["attributes"]["value"].startswith(P), j["attributes"]["value"]
    return out
