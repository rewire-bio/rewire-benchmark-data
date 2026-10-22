"""Lead-optimisation affinity ranking: Ross et al. 2023 Table 3 and the Boltz-2 supplement Tables 11, 12 and 14.

Usage:
  python3 -I extract_leadopt.py <boltz2-supplement.pdf> <pdftotext -layout output> \
      <ross2023.xml> <gilson2025.xml> <batch-folder>

Every record is written with status needs_review. The review objects on results record how the
value was extracted; they are not a review sign-off.
"""
import sys, os, re, html, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, source_review, sha256, slug, num

supp_pdf, supp_txt, ross_xml, gilson_xml, folder = sys.argv[1:6]

SUPP_SHA = sha256(supp_pdf)
SUPP_TXT_SHA = sha256(supp_txt)
ROSS_SHA = sha256(ross_xml)
GILSON_SHA = sha256(gilson_xml)
assert SUPP_SHA == "be867a5d92add8b223d47d882a4213ad489741f3e4d5081a0901a54370342569", SUPP_SHA
assert ROSS_SHA == "f371d2e373306588d11b695b8de21b253a90293d6a15884f635bcf927bdebb1d", ROSS_SHA
assert GILSON_SHA == "a1d7fdc52df61c4d75197f04be91b511b7d093d229d96a0815a11f95e350256b", GILSON_SHA

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12262699/supplementaryFiles"
ROSS_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10576784/fullTextXML"
GILSON_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12750038/fullTextXML"

P = "uc-leadopt-20261022"
b = Batch(folder, P, areas=["molecular-interactions"])

# ---------------------------------------------------------------- sources

SUPP = b.source(P + "-source-boltz2-supplement", "Boltz-2: Towards Accurate and Efficient Binding Affinity Prediction, supplementary appendix", {
    "url": "https://doi.org/10.1101/2025.06.14.659707",
    "artifact_url": SUPP_URL,
    "artifact_member": "NIHPP2025.06.14.659707v1-supplement-1.pdf",
    "version": "bioRxiv v1 posted 2025-06-18; supplement PDF as deposited in Europe PMC PMC12262699 (PPR1038344)",
    "retrieved_at": "2026-10-22T11:52:00Z",
    "artifact_sha256": SUPP_SHA,
    "doi": "10.1101/2025.06.14.659707",
    "publication_status": "preprint",
    "licence": "CC-BY-4.0",
    "media_type": "application/pdf",
    "hash_scope": "The recorded hash is of the supplement PDF itself, extracted from the Europe PMC supplementaryFiles ZIP (ZIP SHA-256 25050dabd9c66fdb955704095023037f1bbabc3a93b7b61f00344c75df8bdb70 on 2026-10-22; the ZIP is rebuilt per request and its hash is not stable).",
    "limitations": [
        "The preprint has not been peer reviewed. The direct bioRxiv PDF returns HTTP 403, so the appendix was taken from the Europe PMC supplementary-files deposit of version 1; the version 2 main-text PDF was not retrieved.",
        "Values were read from the pdftotext (poppler 26.08.0) -layout text layer of the pinned PDF, SHA-256 " + SUPP_TXT_SHA + ".",
        "Tables 11, 12 and 14 print one value per cell with no uncertainty. Bootstrap standard errors appear only as error bars in Figure 6, which prints no numbers.",
        "The results of FEP+ are intended to show the maximum attainable accuracy of current (commercial) FEP simulations by manually adjusting the protocol (input preparation, perturbation map, force field) to the system at hand after observing the error with respect to the experiment (appendix D.2.2, 'Baselines'), so the FEP+ arm is not a prospective baseline.",
        "The ABFE arm 'may also represent an optimistic estimate of its prospective performance given that the protocol was optimized based this dataset' (appendix D.2.2, 'Baselines').",
        "The OpenFE arm's cited source is a blog post (Horton, 2025), which is not a primary source under this repository's rules and was not retrieved.",
        "The column headers read 'target avg.' while appendix D.2.2 'Evaluation metrics' defines every regression metric as computed per assay and averaged across assays weighted by compound count. Assays and targets are not the same unit, and the source does not reconcile the two labels.",
        "The paper's claim of being more than 1,000 times faster than FEP is not backed by a measured FEP+ cost: the FEP+ time cell in Table 12 is printed as '-'.",
        "Per-assay and per-series values behind the target averages are not printed anywhere in the supplement. Figure 12 shows per-assay scatter plots for the validation set only and prints no numbers.",
    ]})

ROSS = b.source(P + "-source-ross2023", "The maximal and current accuracy of rigorous protein-ligand binding free energy calculations", {
    "url": "https://doi.org/10.1038/s42004-023-01019-9",
    "artifact_url": ROSS_URL,
    "version": "Communications Chemistry 6:222 (2023); Europe PMC full-text XML snapshot PMC10576784",
    "retrieved_at": "2026-10-22T11:58:25Z",
    "artifact_sha256": ROSS_SHA,
    "doi": "10.1038/s42004-023-01019-9",
    "publication_status": "peer_reviewed",
    "licence": "CC-BY-4.0",
    "media_type": "application/xml",
    "venue": "Communications Chemistry",
    "year": 2023,
    "limitations": [
        "The FEP+ protocol was tuned per system after seeing the error against experiment: structural inputs, rotamer and protonation states, atom mappings and torsion scaling were adjusted by visual inspection and manual intervention when poor sampling was observed in prior simulations (Results, 'Using FEP to resolve ambiguities in the structural inputs'). The paper therefore reports a maximum-attainable rather than a prospective accuracy.",
        "Table 3 prints weighted averages over FEP graphs and assay comparisons, not per-series values. Per-system values are in the Supplementary Results and the public benchmark repository, neither of which was retrieved in this pass.",
        "The paper assumes that IC50, Ki and Kd ratios are interchangeable when converting measured affinities to relative binding free energies.",
        "The authors are the developers of the FEP+ workflow being assessed.",
    ]})

GILSON = b.source(P + "-source-gilson2025", "Assessment of protein-ligand pose and affinity predictions in CASP16", {
    "url": "https://doi.org/10.1002/prot.70061",
    "artifact_url": GILSON_URL,
    "version": "Proteins, cover date January 2026; Europe PMC full-text XML snapshot PMC12750038",
    "retrieved_at": "2026-10-22T11:58:25Z",
    "artifact_sha256": GILSON_SHA,
    "doi": "10.1002/prot.70061",
    "publication_status": "peer_reviewed",
    "licence": "CC-BY-4.0",
    "media_type": "application/xml",
    "venue": "Proteins: Structure, Function, and Bioinformatics",
    "year": 2026,
    "limitations": [
        "The per-group affinity ranking results are in figures with no printed values, so only the values stated in the body text were extracted. Per-group Kendall tau values were not extracted and the official per-target results file at predictioncenter.org was not downloaded.",
        "The achievable ceiling is an estimate from resampling under an assumed experimental error, not a measured quantity.",
        "The abstract gives the maximum Kendall tau achieved across participants as 0.42, while Section 3.3.1 says 'This is well above the maximum achieved value of 0.39 (Figure 9A)' and, two sentences later, 'the maximum value of Kendall's tau observed here, about 0.4'. The source does not say which figure or penalty convention each number belongs to.",
    ]})

SIDS_SUPP, SIDS_ROSS, SIDS_GILSON = [SUPP], [ROSS], [GILSON]

SUPP_REVIEW = lambda loc: extraction_review(
    ["pdf-text-parse"],
    "Parsed the pdftotext -layout text layer of the pinned supplement PDF with extract/extract_leadopt.py; the table's row labels, column header line and the number of cells per row are asserted. " + loc,
    SUPP_SHA, SUPP_URL)
ROSS_REVIEW = lambda loc: extraction_review(
    ["deterministic-table-parse"],
    "Parsed the <table-wrap> elements of the pinned Europe PMC full-text XML with extract/extract_leadopt.py; the row labels and the number of cells per row are asserted. " + loc,
    ROSS_SHA, ROSS_URL)
GILSON_REVIEW = lambda loc: extraction_review(
    ["transcription"],
    "Transcribed by hand from the body text of the pinned Europe PMC full-text XML; the quoted sentence is asserted to occur in the artifact by extract/extract_leadopt.py. " + loc,
    GILSON_SHA, GILSON_URL)

# ---------------------------------------------------------------- benchmarks

BM_FEP = b.entity("benchmark", P + "-benchmark-fep-public", "Public binding free energy benchmark (Ross et al. 2023)",
    "Assembled collection of proteins and congeneric small-molecule series with measured affinities, used to score relative binding free energy predictions against experiment.",
    SIDS_ROSS + SIDS_SUPP, {
        "entity_level": "suite",
        "version": "As curated for Ross et al. 2023; data released as the public_binding_free_energy_benchmark repository, releases v1.0 and v2.0 (both 2023-06-26, MIT)",
        "task": "Relative binding affinity prediction for congeneric series",
        "scope_note": "Table 3 (FEP+ accuracy beside experimental reproducibility), Table 2 (the data sets and their compound counts) and Table 1 (the assay-reproducibility survey) extracted. Per-system values in the Supplementary Results and the repository were not retrieved. The Boltz-2 supplement's two subsets of this collection are recorded as separate protocols.",
        "source_locator": "Ross et al. 2023 Tables 1-3; Boltz-2 supplement appendix D.2.1 and E.2.1",
        "limitations": [
            "Ross et al. 2023 states its results use release v1.0 of the public benchmark repository; the Boltz-2 supplement does not state which release its subsets come from.",
            "The 876-complex OpenFE subset and the 87-compound 4-target subset both derive from this collection and must partly overlap, so results on the two subsets are not independent. Neither source states the overlap.",
        ],
    })

BM_CASP16 = b.entity("benchmark", P + "-benchmark-casp16-affinity", "CASP16 binding affinity challenge",
    "Blind challenge in which participants submit predicted binding affinities for undisclosed pharmaceutical ligand series, scored after the experimental values are released.",
    SIDS_SUPP + SIDS_GILSON, {
        "entity_level": "challenge",
        "version": "CASP16 (2024 round), protein-ligand affinity track",
        "task": "Blind ranking of ligand series by measured affinity",
        "scope_note": "Boltz-2 supplement Table 14 extracted in full. The CASP16 assessors' per-group Kendall tau values are figure-only and were not extracted; the assessors' stated achievable ceiling and maximum observed tau are recorded as claims.",
        "source_locator": "Boltz-2 supplement Table 14; Gilson et al. 2026 Sections 2.3, 3.3.1 and Table 1",
    })

# ---------------------------------------------------------------- datasets

D_FEP = b.entity("dataset", P + "-data-fep-benchmark", "Curated public FEP benchmark compounds (Ross et al. 2023)",
    "Protein structures and congeneric ligand series with measured Kd, Ki or IC50 values converted to relative binding free energies in kcal/mol.",
    SIDS_ROSS, {
        "version": "As curated for Ross et al. 2023 after structural curation",
        "split": "Whole collection; no training split because the evaluated method is not trained",
        "population": "1,237 compounds over the 14 data sets listed in Table 2, spanning more than 50 proteins",
        "assay": "Mixed binding and functional assays reporting Kd, Ki or IC50",
        "source_locator": "Table 2; Methods, 'Experimental data'",
        "scope_note": "Measured affinities are converted to relative binding free energies under the paper's stated assumption that IC50, Ki and Kd ratios are interchangeable.",
    })

D_SURVEY = b.entity("dataset", P + "-data-experimental-survey", "Repeat-assay affinity survey (Ross et al. 2023)",
    "Sets of compounds whose binding affinities were measured in at least two independent assays, used to quantify how well affinity measurements reproduce.",
    SIDS_ROSS, {
        "version": "As surveyed for Ross et al. 2023",
        "split": "Whole survey",
        "population": "1,867 compounds across the three comparison types in Table 1 (binding vs binding 250, binding vs functional 1,207, functional vs functional 410)",
        "assay": "Pairs of publicly reported binding and functional affinity assays, plus Schrodinger internal project data",
        "source_locator": "Table 1; Methods, 'Experimental reproducibility'",
    })

D_OPENFE = b.entity("dataset", P + "-data-fep-openfe-subset", "OpenFE subset of the public FEP benchmark",
    "876 protein-ligand complexes drawn from hit-to-lead and lead optimisation campaigns with measured affinities.",
    SIDS_SUPP, {
        "version": "Subset of the FEP+ benchmark as used in the Boltz-2 supplement",
        "split": "Held-out affinity test set",
        "population": "876 protein-ligand complexes",
        "source_locator": "Appendix D.2.1, 'We evaluate model performance on the following held-out affinity test sets'",
        "missing_metadata": {"total_targets": {"reason": "unreported", "note": "The supplement states the complex count but not how many targets or assays the subset covers"}},
    })

D_4T = b.entity("dataset", P + "-data-fep-4target", "Four-target subset of the public FEP benchmark",
    "87 neutral compounds against CDK2, TYK2, JNK1 and P38 with measured affinities.",
    SIDS_SUPP, {
        "version": "Subset of the FEP+ benchmark as used in the Boltz-2 supplement; ligand sets curated in the protein-ligand-benchmark of Hahn et al. 2022",
        "split": "Held-out affinity test set",
        "population": "87 neutral compounds over 4 targets (CDK2, TYK2, JNK1, P38)",
        "source_locator": "Appendix D.2.1, 'a 4 targets subset (CDK2, TYK2, JNK1, P38; curated in the protein-ligand-benchmark [Hahn et al., 2022]) with 87 neutral compounds [Chen et al., 2023]'",
        "scope_note": "The supplement attributes the 87 compounds to 'Chen et al., 2023'. The citation does not resolve to a congeneric-series paper in the reference list, so the series definition behind this subset is not established.",
    })

D_CASP16 = b.entity("dataset", P + "-data-casp16-affinity", "CASP16 affinity targets L1000 and L3000",
    "Measured IC50 values for the CASP16 chymase and autotaxin ligand series, withheld from participants until after submission.",
    SIDS_SUPP + SIDS_GILSON, {
        "version": "CASP16 protein-ligand affinity track",
        "split": "Blind test; affinities released after submission",
        "population": "Chymase (L1000) and autotaxin (L3000) ligand series; Gilson et al. 2026 Table 1 records 17 chymase affinities and 123 stage-1 autotaxin affinities, both contributed by F. Hoffmann-La Roche",
        "assay": "IC50",
        "source_locator": "Boltz-2 supplement appendix D.2.1; Gilson et al. 2026 Table 1",
        "scope_note": "The Boltz-2 supplement averages over the CASP16 targets, so this record covers both series together. The same two series are recorded separately for PLABench as lit-interactions-20261011-leakctl-data-casp16-l1000 and -l3000.",
    })

# ---------------------------------------------------------------- protocols

WEIGHTED_AGG = ("All regression metrics are calculated per assay and averaged across assays with weight "
                "proportional to the number of compounds in each assay")
BOLTZ_METRIC_DEF = ("Appendix D.2.2 'Evaluation metrics': Pearson R, Kendall tau, pairwise MAE (PMAE), MAE and the "
                    "fraction of predictions within 1 and 2 kcal/mol, each computed per assay and averaged across "
                    "assays weighted by compound count, with predictions converted to kcal/mol first; the centered "
                    "variants translate each assay's predictions to the ground-truth mean")
BOLTZ_LIMITS = [
    "One value per cell with no uncertainty; bootstrap standard errors appear only as error bars in Figure 6, which prints no numbers.",
    "The column headers read 'target avg.' while appendix D.2.2 defines the aggregation as a compound-weighted mean across assays. Assays and targets are not the same unit and the source does not reconcile the two labels.",
    "No per-assay or per-series value is printed, so the table supports statements about the mean over series and not about any one series.",
    "The units of the PMAE and MAE columns are not printed in the table header; appendix D.2.2 states that all predictions are converted to kcal/mol before the metrics are computed.",
    "The 'Perc. within 1' and 'Perc. within 2' headers say percentage, but appendix D.2.2 defines them as the fraction of predictions with absolute error below the threshold and the printed values lie on a 0 to 1 scale.",
    "The results of FEP+ are intended to show the maximum attainable accuracy of current (commercial) FEP simulations by manually adjusting the protocol to the system at hand after observing the error with respect to the experiment, so the FEP+ arm is not a prospective baseline.",
]
LEAK_FEP = ("Training proteins with at least 90% sequence similarity to a validation or test protein were removed, by "
            "clustering all affinity-dataset protein sequences with 'mmseqs easy-cluster ... --min-seq-id 0.9 "
            "--cov-mode 0 -c 0.01' and dropping any training protein sharing a cluster with a validation or test "
            "protein (appendix D.2.1, 'Data leakage control'). Compound-level dependence was checked in Figure 10 "
            "and no strong dependence was observed; that figure prints no values.")
LEAK_CASP16 = ("The sequence-level filtering described in appendix D.2.1 was not applied to CASP16, because the CASP16 "
               "data was released after the training-data cutoff. The maximum Tanimoto similarity of test compounds "
               "to the affinity training set is stated as 0.41 for L1000 and 0.59 for L3000.")

PR_ROSS_FEP = b.entity("protocol", P + "-protocol-ross-fep-plus", "Public FEP benchmark, FEP+ accuracy against experiment",
    "Scores relative binding free energies from a free energy perturbation workflow against measured affinities over every congeneric series in the collection, reporting compound-weighted and edge-weighted averages with bootstrap confidence intervals.",
    SIDS_ROSS, {
        "protocol": "Pairwise and edgewise RMSE and MUE in kcal/mol, coefficient of determination and Kendall tau of the cycle-closure-corrected absolute free energies, each a weighted average over FEP graphs",
        "version": "Ross et al. 2023 Table 3, 'FEP+ benchmark' column",
        "aggregation": WEIGHTED_AGG.replace("All regression metrics are calculated per assay and averaged across assays with weight proportional to the number of compounds in each assay", "Weighted average over FEP graphs; the weight is the number of compounds in the graph for the pairwise, R2 and Kendall tau metrics and the number of edges for the edgewise errors (Table 3 legend)"),
        "metric_definition": "Pairwise errors are computed over the inferred predicted free energy difference between every pair of ligands in a graph; edgewise errors over the graph's edges only and are therefore dependent on the graph topology (Methods, 'Accuracy metrics')",
        "uncertainty_reporting": {"definition": "95% confidence intervals from bootstrap sampling over the pairs of experimental series or FEP+ graphs (Table 3 legend)"},
        "heldout_test": ["Not applicable: the workflow is not trained"],
        "source_locator": "Table 3, column 'FEP+ benchmark'",
        "limitations": [
            "The FEP+ protocol was tuned per system after seeing the error against experiment: structural inputs, rotamer and protonation states, atom mappings and torsion scaling were adjusted by visual inspection and manual intervention when poor sampling was observed in prior simulations. The reported accuracy is maximum-attainable, not prospective.",
            "Every value is a weighted average over series; no per-series value is printed in the paper's tables.",
            "The authors developed the workflow being assessed.",
            "Running this workflow needs a commercial Schrodinger licence, so its values can only ever be recorded from publication, never re-run here.",
            "Compute cost is not reported.",
        ],
        "missing_metadata": {"capacity": {"reason": "unreported", "note": "No compute cost is reported for the FEP+ calculations"}},
    }, links=[{"relation": "part_of", "target_id": BM_FEP},
              {"relation": "uses_data", "target_id": D_FEP},
              {"relation": "evaluates_task", "target_id": "catalog-task-ligand-affinity"}])

PR_ROSS_SURVEY = b.entity("protocol", P + "-protocol-ross-experimental-survey", "Repeat-assay reproducibility of relative binding free energies",
    "Compares relative binding free energies for the same compounds measured in two independent affinity assays, reporting compound-weighted averages with bootstrap confidence intervals.",
    SIDS_ROSS, {
        "protocol": "Pairwise RMSE and MUE in kcal/mol, coefficient of determination and Kendall tau between two independent assays of the same compounds, weighted by the number of compounds in each assay comparison",
        "version": "Ross et al. 2023 Table 3, 'Experimental survey' column",
        "aggregation": "Weighted by the number of compounds in each assay comparison; confidence intervals by bootstrap sampling over each assay comparison (Results, 'Comparing the accuracy of FEP+ with experimental reproducibility')",
        "metric_definition": "The same pairwise metric definitions as the FEP+ column, so that the two columns are comparable; the paper states 'The pairwise errors and correlation metrics of the experimental survey and FEP+ benchmark are directly comparable'",
        "uncertainty_reporting": {"definition": "95% confidence intervals from bootstrap sampling over the pairs of experimental series (Table 3 legend)"},
        "heldout_test": ["Not applicable: no method is being scored"],
        "source_locator": "Table 3, column 'Experimental survey'",
        "limitations": [
            "This protocol measures assay reproducibility, not a prediction method. It bounds the accuracy any method could reach on this kind of data; it does not rank analogues.",
            "Edgewise errors have no equivalent here, because they depend on the topology of an FEP perturbation graph; Table 3 prints N/A for both.",
            "The survey pools publicly reported assays with Schrodinger internal project data; the weighted experimental values carry wider bootstrap intervals than the FEP+ values.",
            "Only 6 functional-vs-functional assay comparisons contribute, which the paper says makes that category's weighted means less meaningful.",
        ],
    }, links=[{"relation": "part_of", "target_id": BM_FEP},
              {"relation": "uses_data", "target_id": D_SURVEY}])

PR_OPENFE = b.entity("protocol", P + "-protocol-boltz2-fep-openfe-subset", "FEP+ benchmark OpenFE subset, affinity ranking",
    "Scores predicted affinities against measured affinities on 876 protein-ligand complexes, computing each metric inside one assay and averaging across assays weighted by compound count.",
    SIDS_SUPP, {
        "protocol": "Pearson R, Kendall tau, PMAE, MAE (non-centered and centered) and the fraction of predictions within 1 and 2 kcal/mol, as printed in Table 11",
        "version": "Boltz-2 supplement (bioRxiv v1) Table 11",
        "aggregation": WEIGHTED_AGG + " (appendix D.2.2); the table's columns are labelled 'target avg.'",
        "metric_definition": BOLTZ_METRIC_DEF,
        "control": LEAK_FEP,
        "heldout_test": ["Held-out affinity test set; training proteins sharing an mmseqs 90% identity cluster with a test protein were removed"],
        "source_locator": "Table 11, 'OpenFE subset of the FEP+ benchmark'",
        "limitations": BOLTZ_LIMITS + [
            "The supplement does not state whether the OpenFE and FEP+ rows were re-run here or taken from the cited prior work, so the origin of those evaluations is recorded as unreported.",
            "This subset and the 4-target subset both derive from the same collection and must partly overlap; the two tables are not independent.",
        ],
        "missing_metadata": {"uncertainty_reporting": {"reason": "unreported", "note": "Table 11 prints no uncertainty"}},
    }, links=[{"relation": "part_of", "target_id": BM_FEP},
              {"relation": "uses_data", "target_id": D_OPENFE},
              {"relation": "evaluates_task", "target_id": "catalog-task-ligand-affinity"}])

PR_4T = b.entity("protocol", P + "-protocol-boltz2-fep-4target", "FEP+ benchmark four-target subset, affinity ranking and cost",
    "Scores predicted affinities against measured affinities for 87 neutral compounds on four kinases and prints each method's compute cost beside its accuracy.",
    SIDS_SUPP, {
        "protocol": "Per-method compute time plus Pearson R, Kendall tau, PMAE, MAE (non-centered and centered) and the fraction of predictions within 1 and 2 kcal/mol, as printed in Table 12",
        "version": "Boltz-2 supplement (bioRxiv v1) Table 12",
        "aggregation": WEIGHTED_AGG + " (appendix D.2.2); the table's columns are labelled 'target avg.'",
        "metric_definition": BOLTZ_METRIC_DEF + "; the 'time' column prints a per-method cost with no stated denominator",
        "control": LEAK_FEP,
        "heldout_test": ["Held-out affinity test set; training proteins sharing an mmseqs 90% identity cluster with a test protein were removed"],
        "source_locator": "Table 12, '4 target subset of the FEP+ benchmark'",
        "limitations": BOLTZ_LIMITS + [
            "The supplement does not state whether the OpenFE, FEP+ and ABFE rows were re-run here or taken from the cited prior work, so the origin of those evaluations is recorded as unreported.",
            "The 'time' column does not say what it counts: whether it is per compound, per edge, per target or for the whole subset, nor on what hardware. The FEP+ cell is printed as '-', so the table carries no measured FEP+ cost.",
            "Four of the ten rows print the accuracy columns beyond Pearson R and Kendall tau as N/A, so the arms are not all comparable on the same metrics.",
            "This subset and the 876-complex OpenFE subset both derive from the same collection and must partly overlap; the two tables are not independent.",
            "The series definition behind the 87 compounds rests on a citation ('Chen et al., 2023') that does not resolve in the supplement's reference list.",
        ],
        "missing_metadata": {"uncertainty_reporting": {"reason": "unreported", "note": "Table 12 prints no uncertainty"}},
    }, links=[{"relation": "part_of", "target_id": BM_FEP},
              {"relation": "uses_data", "target_id": D_4T},
              {"relation": "evaluates_task", "target_id": "catalog-task-ligand-affinity"}])

PR_CASP16 = b.entity("protocol", P + "-protocol-boltz2-casp16", "CASP16 affinity challenge, Boltz-2 against the top-ranked participants",
    "Scores predicted affinities against the withheld CASP16 measurements for the chymase and autotaxin series, computing each metric inside one series and averaging across series weighted by compound count.",
    SIDS_SUPP, {
        "protocol": "Pearson R, Kendall tau, pairwise MAE, MAE (non-centered and centered) and the fraction of predictions within 1 and 2 kcal/mol, as printed in Table 14",
        "version": "Boltz-2 supplement (bioRxiv v1) Table 14",
        "aggregation": WEIGHTED_AGG + " (appendix D.2.2); the table's columns are labelled 'target avg.'",
        "metric_definition": BOLTZ_METRIC_DEF,
        "control": LEAK_CASP16,
        "heldout_test": ["Blind challenge data released after the training-data cutoff; no sequence filtering was applied"],
        "source_locator": "Table 14, 'CASP16 competition'",
        "limitations": [
            "One value per cell with no uncertainty.",
            "The column headers read 'target avg.' while appendix D.2.2 defines the aggregation as a compound-weighted mean across assays; the source does not reconcile the two labels.",
            "No per-series value is printed, so the table cannot say how either target was ranked on its own.",
            "The participant rows are anonymous CASP16 group identifiers and the supplement says nothing about what methods they used.",
            "The supplement does not state how the participants' submissions were obtained or re-scored.",
            "The mmseqs 90% identity filtering applied to the other affinity benchmarks was not applied here.",
            "The units of the pairwise MAE and MAE columns are not printed in the table header; appendix D.2.2 states that all predictions are converted to kcal/mol before the metrics are computed.",
            "The 'Perc. within 1' and 'Perc. within 2' headers say percentage, but the printed values lie on a 0 to 1 scale.",
        ],
        "missing_metadata": {"uncertainty_reporting": {"reason": "unreported", "note": "Table 14 prints no uncertainty"}},
    }, links=[{"relation": "part_of", "target_id": BM_CASP16},
              {"relation": "uses_data", "target_id": D_CASP16},
              {"relation": "evaluates_task", "target_id": "catalog-task-ligand-affinity"}])

# ---------------------------------------------------------------- methods, models and configurations

BACPI = b.entity("model", P + "-model-bacpi", "BACPI",
    "Sequence-based affinity predictor whose 1D convolutional protein network and ligand graph attention transformer are joined by bi-directional attention.",
    SIDS_SUPP, {
        "entity_level": "family",
        "reported_name": "BACPI",
        "source_locator": "Appendix D.2.2, 'Baselines'",
        "missing_metadata": {"version": {"reason": "unreported", "note": "No checkpoint or release version is printed"}},
    }, method_types=["supervised_machine_learning"])

M_FEP_PLUS = b.entity("method", P + "-method-fep-plus", "FEP+",
    "Commercial relative free energy perturbation workflow that computes binding free energy differences between ligands along a perturbation map with cycle closure correction.",
    SIDS_ROSS + SIDS_SUPP, {
        "entity_level": "method",
        "reported_name": "FEP+",
        "access": "Commercial Schrodinger licence required; cannot be re-run in this repository.",
        "source_locator": "Ross et al. 2023 Methods; Boltz-2 supplement appendix D.2.2",
        "missing_metadata": {"version": {"reason": "unreported", "note": "Neither source prints the FEP+ release used"}},
    }, method_types=["conventional_pipeline"])

M_OPENFE = b.entity("method", P + "-method-openfe", "OpenFE",
    "Open-source relative binding free energy workflow that runs alchemical perturbations between ligands under a fixed automated protocol.",
    SIDS_SUPP, {
        "entity_level": "method",
        "reported_name": "OpenFE",
        "access": "Open source.",
        "source_locator": "Appendix D.2.2, 'Baselines'",
        "missing_metadata": {"version": {"reason": "unreported", "note": "The supplement cites Gowers et al. 2023 and a blog post but prints no OpenFE version"}},
    }, method_types=["conventional_pipeline"])

M_ABFE = b.entity("method", P + "-method-abfe", "ABFE protocol (Wu et al. 2025)",
    "Absolute binding free energy protocol that computes each ligand's binding free energy by alchemically decoupling it from the binding site.",
    SIDS_SUPP, {
        "entity_level": "method",
        "reported_name": "ABFE",
        "source_locator": "Appendix D.2.2, 'Baselines'",
        "missing_metadata": {"version": {"reason": "unreported", "note": "The supplement cites Wu et al. 2025 but prints no protocol version"}},
    }, method_types=["conventional_pipeline"])

M_FMO = b.entity("method", P + "-method-fmo", "FMO (DFTB3 fragment molecular orbital scoring)",
    "Scores a docked pose with a DFTB3-based fragment molecular orbital calculation of the interaction energy.",
    SIDS_SUPP, {
        "entity_level": "method",
        "reported_name": "FMO",
        "access": "In-house code; not publicly available.",
        "source_locator": "Appendix D.2.2, 'Baselines'",
        "missing_metadata": {"version": {"reason": "unreported", "note": "An in-house code with no printed version"}},
    }, method_types=["conventional_pipeline"])

M_MMPBSA = b.entity("method", P + "-method-mmpbsa", "MM/PBSA (AMBER)",
    "End-state free energy method that scores the final frame of a short restrained-then-free molecular dynamics simulation with molecular mechanics and Poisson-Boltzmann surface area terms.",
    SIDS_SUPP, {
        "entity_level": "method",
        "reported_name": "MM/PBSA",
        "access": "AMBER implementation.",
        "source_locator": "Appendix D.2.2, 'Baselines'",
        "missing_metadata": {"version": {"reason": "unreported", "note": "The supplement cites the AMBER implementation but prints no version"}},
    }, method_types=["conventional_pipeline"])

M_CG4 = b.entity("method", P + "-method-chemgauss4", "Chemgauss4",
    "Empirical docking scoring function that rates a posed ligand by shape and chemical complementarity with the binding site.",
    SIDS_SUPP, {
        "entity_level": "method",
        "reported_name": "Chemgauss4",
        "access": "OpenEye commercial licence required.",
        "source_locator": "Appendix D.2.2, 'Baselines'",
        "missing_metadata": {"version": {"reason": "unreported", "note": "No OpenEye toolkit version is printed"}},
    }, method_types=["conventional_pipeline"])

M_REASSAY = b.entity("method", P + "-method-experimental-reassay", "Independent repeat affinity assay",
    "Takes a second, independent experimental affinity measurement of the same compounds as the estimate of their relative binding free energies.",
    SIDS_ROSS, {
        "entity_level": "method",
        "reported_name": "Experimental survey",
        "reference_kind": "experimental_reference",
        "source_locator": "Table 3, column 'Experimental survey'; Methods, 'Experimental reproducibility'",
        "provenance_note": "Recorded as a method so that the assay noise floor can sit beside the prediction methods on the same protocol family. It is an experimental reference, not a predictive method.",
    })

CASP16_GROUPS = ["LG016", "LG082", "LG204", "LG055", "LG207", "LG008"]
group_method, group_config = {}, {}
for g in CASP16_GROUPS:
    gid = b.entity("method", P + "-method-casp16-group-" + slug(g), "CASP16 group " + g,
        "Submitted blind binding-affinity predictions for the CASP16 chymase and autotaxin ligand series as group " + g + ".",
        SIDS_SUPP, {
            "entity_level": "method",
            "reported_name": g,
            "source_locator": "Table 14, row '" + g + "'",
            "missing_metadata": {
                "model_family": {"reason": "unreported", "note": "The supplement names the group identifier only and says nothing about the method it used"},
                "version": {"reason": "unreported"},
            },
        })
    group_method[g] = gid


def config(cid, name, description, source_ids, attrs, parent, method_types=None):
    links = [{"relation": "configuration_of", "target_id": parent}] if parent else []
    return b.entity("configuration", cid, name, description, source_ids, attrs, method_types=method_types, links=links)


C_BOLTZ2 = config(P + "-config-boltz2-affinity", "Boltz-2 affinity prediction",
    "Boltz-2 run as published to co-fold the complex from sequence and ligand and read a binding affinity in kcal/mol off its affinity head.",
    SIDS_SUPP, {
        "configuration_type": "paper_evaluation",
        "reported_name": "Boltz-2",
        "version": "Boltz-2 as described in the 2025-06-18 preprint; no checkpoint identifier printed",
        "access_reuse": "MIT code and weights.",
        "foundation_model_eligible": True,
        "source_locator": "Tables 11, 12 and 14, row 'Boltz-2'; appendix D.2.2",
        "missing_metadata": {"checkpoint": {"reason": "unreported", "note": "The supplement does not name a checkpoint for the affinity benchmarks"}},
    }, "catalog-model-boltz-2", ["foundation_model"])

C_IPTM = config(P + "-config-boltz2-iptm", "Boltz-2 ipTM as an affinity score",
    "Uses Boltz-2's predicted interface confidence (ipTM) in place of an affinity value, as a control for how much of the ranking comes from pose confidence alone.",
    SIDS_SUPP, {
        "configuration_type": "paper_evaluation",
        "reported_name": "Boltz-2 iptm",
        "version": "Boltz-2 as described in the 2025-06-18 preprint; no checkpoint identifier printed",
        "access_reuse": "MIT code and weights.",
        "source_locator": "Tables 11, 12 and 14, row 'Boltz-2 iptm'",
        "limitations": ["A confidence score is not an affinity value; the error and within-threshold columns are printed as N/A for this arm."],
        "missing_metadata": {"checkpoint": {"reason": "unreported"}},
    }, "catalog-model-boltz-2", ["foundation_model"])

C_BACPI = config(P + "-config-bacpi", "BACPI as trained for the Boltz-2 affinity baselines",
    "BACPI retrained on the Boltz-2 affinity training data with the original hyperparameters except a batch size of 32.",
    SIDS_SUPP, {
        "configuration_type": "paper_evaluation",
        "reported_name": "BACPI",
        "version": "Retrained for the Boltz-2 comparison; no release version printed",
        "hyperparameters": "Default hyperparameters of the original publication except batch size, raised to 32",
        "access_reuse": "Not stated in this source; see the BACPI release.",
        "source_locator": "Tables 11, 12 and 14, row 'BACPI'; appendix D.2.2",
    }, BACPI, ["supervised_machine_learning"])

C_GAT = config(P + "-config-gat-ligand-only", "BACPI ligand-only ablation (GAT)",
    "BACPI with its protein sequence network switched off, so that affinity is predicted from the ligand alone, which estimates how much of the signal is ligand bias.",
    SIDS_SUPP, {
        "configuration_type": "paper_evaluation",
        "reported_name": "GAT",
        "version": "Retrained for the Boltz-2 comparison; no release version printed",
        "hyperparameters": "Default hyperparameters of the original publication except batch size, raised to 32; the protein sequence CNN is deactivated",
        "access_reuse": "Not stated in this source; see the BACPI release.",
        "source_locator": "Tables 11, 12 and 14, row 'GAT'; appendix D.2.2",
    }, BACPI, ["supervised_machine_learning"])

C_FEP_PLUS = config(P + "-config-fep-plus", "FEP+ with per-system manual protocol adjustment",
    "FEP+ applied with the input preparation, perturbation map and force field adjusted by hand for each system after the error against experiment has been seen.",
    SIDS_ROSS + SIDS_SUPP, {
        "configuration_type": "reported_configuration",
        "reported_name": "FEP+",
        "version": "As benchmarked in Ross et al. 2023; no FEP+ release printed",
        "access_reuse": "Commercial Schrodinger licence required.",
        "source_locator": "Ross et al. 2023 Table 3 and Results; Boltz-2 supplement Tables 11 and 12, row 'FEP+'",
        "limitations": [
            "The protocol was tuned per system after seeing the error against experiment, so the reported accuracy is maximum-attainable rather than prospective.",
            "The Boltz-2 supplement does not state whether its FEP+ values were re-run or taken from the per-system results published with Ross et al. 2023.",
        ],
    }, M_FEP_PLUS, ["conventional_pipeline"])

C_OPENFE = config(P + "-config-openfe", "OpenFE under a fixed automated protocol",
    "OpenFE run with its default settings and no per-system adjustment, which the comparison treats as the automated open-source free energy arm.",
    SIDS_SUPP, {
        "configuration_type": "reported_configuration",
        "reported_name": "OpenFE",
        "version": "Not printed; the supplement cites Gowers et al. 2023 for the method and Horton 2025 for the results",
        "access_reuse": "Open source.",
        "source_locator": "Tables 11 and 12, row 'OpenFE'; appendix D.2.2",
        "limitations": ["The cited source for these results is a blog post, which is not a primary source under this repository's rules and was not retrieved. The peer-reviewed OpenFE assessment (doi 10.1021/acs.jcim.6c00089) is behind an ACS paywall and was not retrieved."],
    }, M_OPENFE, ["conventional_pipeline"])

C_ABFE = config(P + "-config-abfe", "ABFE protocol optimised on the four-target subset",
    "The absolute binding free energy protocol run on the four-target subset with settings that were optimised on that same data.",
    SIDS_SUPP, {
        "configuration_type": "reported_configuration",
        "reported_name": "ABFE",
        "version": "Not printed; the supplement cites Wu et al. 2025",
        "source_locator": "Table 12, row 'ABFE'; appendix D.2.2",
        "limitations": ["The supplement states the ABFE results 'may also represent an optimistic estimate of its prospective performance given that the protocol was optimized based this dataset'."],
    }, M_ABFE, ["conventional_pipeline"])

C_FMO = config(P + "-config-fmo", "FMO scoring of Glide poses",
    "Scores ligand poses generated by Glide with a DFTB3-based fragment molecular orbital calculation.",
    SIDS_SUPP, {
        "configuration_type": "reported_configuration",
        "reported_name": "FMO",
        "version": "Not printed; an in-house DFTB3-based code",
        "access_reuse": "In-house code; not publicly available.",
        "source_locator": "Table 12, row 'FMO'; appendix D.2.2",
    }, M_FMO, ["conventional_pipeline"])

C_MMPBSA = config(P + "-config-mmpbsa", "MM/PBSA scoring after a 1 ns simulation",
    "Thermalises the modelled complex with a restrained minimisation and equilibration, runs 1 ns of unrestrained NPT dynamics and scores the final frame with MM/PBSA.",
    SIDS_SUPP, {
        "configuration_type": "reported_configuration",
        "reported_name": "MM/PBSA",
        "version": "Not printed; the AMBER implementation",
        "source_locator": "Table 12, row 'MM/PBSA'; appendix D.2.2",
    }, M_MMPBSA, ["conventional_pipeline"])

C_CG4 = config(P + "-config-chemgauss4", "Chemgauss4 scoring of Glide poses",
    "Scores ligand poses generated by Glide with the Chemgauss4 function on protein structures prepared by OpenEye Spruce.",
    SIDS_SUPP, {
        "configuration_type": "reported_configuration",
        "reported_name": "Chemgauss4",
        "version": "Not printed",
        "access_reuse": "OpenEye commercial licence required.",
        "source_locator": "Table 12, row 'Chemgauss4'; appendix D.2.2",
    }, M_CG4, ["conventional_pipeline"])

C_REASSAY = config(P + "-config-experimental-reassay", "Second independent assay as the predictor",
    "Treats one assay's measured affinities as the prediction of another assay's measured affinities for the same compounds, which gives the reproducibility ceiling for the same metrics.",
    SIDS_ROSS, {
        "configuration_type": "reported_configuration",
        "reported_name": "Experimental survey",
        "version": "As surveyed for Ross et al. 2023",
        "access_reuse": "Publicly reported assays plus Schrodinger internal project data; the internal data is not public.",
        "source_locator": "Table 3, column 'Experimental survey'",
        "limitations": ["This is an experimental reference, not a predictive method. Its values bound what any method could achieve on this kind of data."],
    }, M_REASSAY)

for g in CASP16_GROUPS:
    group_config[g] = config(P + "-config-casp16-group-" + slug(g), "CASP16 group " + g + " affinity submission",
        "The affinity predictions that CASP16 group " + g + " submitted for the chymase and autotaxin ligand series.",
        SIDS_SUPP, {
            "configuration_type": "reported_configuration",
            "reported_name": g,
            "version": "CASP16 submission; no method version printed",
            "source_locator": "Table 14, row '" + g + "'",
            "limitations": ["The supplement identifies this arm by its anonymous CASP16 group number only and says nothing about the method behind it."],
            "missing_metadata": {"access_reuse": {"reason": "unreported"}},
        }, group_method[g])

# ---------------------------------------------------------------- Boltz-2 table parsing

lines = open(supp_txt, encoding="utf-8").read().split("\n")


def row_cells(lineno, label, expect):
    cells = re.split(r"\s{2,}", lines[lineno - 1].strip())
    assert cells[0] == label, (lineno, label, cells)
    assert len(cells) == expect, (lineno, label, len(cells), expect)
    return cells


def assert_header(lineno, expected):
    got = re.split(r"\s{2,}", lines[lineno - 1].strip())
    assert got == expected, (lineno, got, expected)


# (slug, metric, unit, direction, qualifier, unit_detail, column label)
KCAL_DETAIL = ("Unit not printed in the table header; appendix D.2.2 states that all predictions are converted to "
               "kcal/mol before the metrics are computed")
FRAC_DETAIL = ("Counted entity: predictions. The header reads 'Perc.' but appendix D.2.2 defines the column as the "
               "fraction of predictions with absolute error below the threshold, and the printed values lie on a 0 to "
               "1 scale")
AGG = "weighted mean over assays, weight proportional to compound count"

FEP_COLS = [
    ("pearson", "pearson-correlation", "unitless", "higher", AGG, None, 'column "Pearson R", sub-column "target avg."'),
    ("kendall-tau", "kendall-tau", "unitless", "higher", AGG, None, 'column "Kendall tau", sub-column "target avg."'),
    ("pmae", "mean-absolute-error", "kilocalorie-per-mole", "lower", "pairwise, " + AGG, KCAL_DETAIL, 'column "PMAE", sub-column "target avg."'),
    ("mae-non-centered", "mean-absolute-error", "kilocalorie-per-mole", "lower", "non-centered, " + AGG, KCAL_DETAIL, 'column "MAE", sub-column "non-cent."'),
    ("mae-centered", "mean-absolute-error", "kilocalorie-per-mole", "lower", "centered, " + AGG, KCAL_DETAIL, 'column "MAE", sub-column "cent."'),
    ("within-1-non-centered", "proportion", "fraction", "higher", "within 1 kcal/mol, non-centered, " + AGG, FRAC_DETAIL, 'column "Perc. within 1", sub-column "non-cent."'),
    ("within-1-centered", "proportion", "fraction", "higher", "within 1 kcal/mol, centered, " + AGG, FRAC_DETAIL, 'column "Perc. within 1", sub-column "cent."'),
    ("within-2-non-centered", "proportion", "fraction", "higher", "within 2 kcal/mol, non-centered, " + AGG, FRAC_DETAIL, 'column "Perc. within 2", sub-column "non-cent."'),
    ("within-2-centered", "proportion", "fraction", "higher", "within 2 kcal/mol, centered, " + AGG, FRAC_DETAIL, 'column "Perc. within 2", sub-column "cent."'),
]
CASP16_COLS = [c if i != 2 else ("pmae", c[1], c[2], c[3], c[4], c[5], 'column "Pairwise MAE", sub-column "target avg."')
               for i, c in enumerate(FEP_COLS)]

MISSING_NA = {"reason": "inapplicable", "note": "Printed as N/A. The source prints no value for this metric on this arm and does not say why; the arm either produces a score rather than an affinity in kcal/mol, or predicts only relative affinities, so the non-centered columns do not apply"}
MISSING_DASH = {"reason": "unreported", "note": "Printed as '-' with no value"}

TIME_UNITS = {"GPU sec": ("accelerator-time", "second"), "GPU ms": ("accelerator-time", "millisecond"),
              "GPU hours": ("accelerator-time", "hour"), "CPU min": ("cpu-time", "minute"),
              "CPU sec": ("cpu-time", "second")}


def value_missing(printed):
    if printed == "N/A":
        return MISSING_NA
    if printed == "-":
        return MISSING_DASH
    return None


def emit_table(table_no, table_title, protocol, dataset, header, labels, first_row, arms, cols, has_time,
               locator_prefix):
    assert_header(header[0], header[1])
    assert_header(labels[0], labels[1])
    expect = len(cols) + (2 if table_no != 14 else 1) + (1 if has_time else 0)
    for i, (label, cfg, origin, origin_note) in enumerate(arms):
        lineno = first_row + i
        cells = row_cells(lineno, label, expect)
        values = cells[-len(cols):]
        aslug = slug(label)
        comparison = {
            "protocol_id": protocol,
            "dataset_version": table_title,
            "split": "Held-out affinity test set" if table_no != 14 else "CASP16 blind test",
            "population": POPULATION[table_no],
            "inputs": "Protein sequence and ligand structure" if cfg in (C_BOLTZ2, C_IPTM, C_BACPI, C_GAT) else None,
            "adaptation": ADAPTATION.get(cfg),
            "metric_implementation": BOLTZ_METRIC_DEF,
            "aggregation": WEIGHTED_AGG + " (appendix D.2.2); the table prints the columns as 'target avg.'",
            "budget": cells[2] if has_time else None,
        }
        ev = b.evaluation(P + "-eval-t" + str(table_no) + "-" + aslug,
                          label + " on " + table_title, SIDS_SUPP, cfg, protocol, dataset, origin, comparison,
                          locator_prefix + ", row '" + label + "' (text-layer line " + str(lineno) + ")",
                          extra={"limitations": [origin_note]} if origin_note else None)
        if has_time:
            printed = cells[2]
            unit_key = next((k for k in TIME_UNITS if printed.endswith(k)), None)
            if unit_key:
                metric, unit = TIME_UNITS[unit_key]
                head = printed[: -len(unit_key)].strip()
                numeric = num(head)
                vm = None if numeric else {"reason": "unreported", "note": "Printed as a range or bound ('" + printed + "'); no single value is given"}
            else:
                metric, unit, numeric, vm = "accelerator-time", "unit-unreported", None, MISSING_DASH
            b.result(P + "-result-t" + str(table_no) + "-" + aslug + "-time",
                     label + " compute cost on " + table_title, SUPP, SIDS_SUPP, ev, printed, metric, "lower", unit,
                     locator_prefix + ', row "' + label + '", column "time" (text-layer line ' + str(lineno) + ")",
                     SUPP_REVIEW('Table ' + str(table_no) + ', column "time", text-layer line ' + str(lineno) + "."),
                     qualifier="per-method cost as printed beside the accuracy columns", numeric=numeric,
                     unit_detail="The table does not state what the time counts (per compound, per edge, per target or for the whole subset) or on what hardware",
                     value_missing=vm)
        for (cslug, metric, unit, direction, qualifier, unit_detail, clabel), printed in zip(cols, values):
            vm = value_missing(printed)
            b.result(P + "-result-t" + str(table_no) + "-" + aslug + "-" + cslug,
                     label + " " + cslug.replace("-", " ") + " on " + table_title, SUPP, SIDS_SUPP, ev,
                     printed, metric, direction, unit,
                     locator_prefix + ', row "' + label + '", ' + clabel + " (text-layer line " + str(lineno) + ")",
                     SUPP_REVIEW("Table " + str(table_no) + ", " + clabel + ", text-layer line " + str(lineno) + "."),
                     qualifier=qualifier, unit_detail=unit_detail,
                     numeric=None if vm else num(printed), value_missing=vm)


POPULATION = {
    11: "876 protein-ligand complexes",
    12: "87 neutral compounds over 4 targets (CDK2, TYK2, JNK1, P38)",
    14: "CASP16 chymase (L1000) and autotaxin (L3000) ligand series",
}
ADAPTATION = {
    C_BOLTZ2: "Published model applied without retraining; training proteins clustered with the test proteins were removed",
    C_IPTM: "Published model applied without retraining; the interface confidence is read in place of an affinity",
    C_BACPI: "Retrained on the Boltz-2 affinity training data",
    C_GAT: "Retrained on the Boltz-2 affinity training data with the protein network switched off",
    C_FEP_PLUS: "Protocol adjusted by hand per system after seeing the error against experiment",
    C_OPENFE: "Fixed automated protocol with no per-system adjustment",
    C_ABFE: "Protocol optimised on this same data set",
}

QUOTED = "The supplement cites prior work for this arm and does not say whether the values were re-run here or taken from that work"
CASP_QUOTED = "The supplement presents these rows as the top-ranked CASP16 participants and does not say how their submissions were obtained or re-scored"

H11 = (1688, ["Pearson R", "Kendall tau", "PMAE", "MAE", "Perc. within 1", "Perc. within 2"])
L11 = (1689, ["method", "type", "target avg.", "target avg.", "target avg.", "non-cent. cent.", "non-cent.", "cent.", "non-cent.", "cent."])
H12 = (1703, ["Pearson R", "Kendall tau", "PMAE", "MAE", "Perc. within 1", "Perc. within 2"])
L12 = (1704, ["method", "type", "time", "target avg.", "target avg.", "target avg.", "non-cent. cent.", "non-cent.", "cent.", "non-cent.", "cent."])
H14 = (1745, ["Pearson R", "Kendall tau", "Pairwise MAE", "MAE", "Perc. within 1", "Perc. within 2"])
L14 = (1746, ["method", "target avg.", "target avg.", "target avg.", "non-cent. cent.", "non-cent.", "cent.", "non-cent.", "cent."])

emit_table(11, "the FEP+ benchmark OpenFE subset", PR_OPENFE, D_OPENFE, H11, L11, 1690, [
    ("Boltz-2", C_BOLTZ2, "author_reported", None),
    ("Boltz-2 iptm", C_IPTM, "author_reported", None),
    ("GAT", C_GAT, "author_reported", None),
    ("BACPI", C_BACPI, "author_reported", None),
    ("OpenFE", C_OPENFE, "unreported", QUOTED),
    ("FEP+", C_FEP_PLUS, "unreported", QUOTED),
], FEP_COLS, False, "Table 11")

emit_table(12, "the FEP+ benchmark four-target subset", PR_4T, D_4T, H12, L12, 1706, [
    ("Boltz-2", C_BOLTZ2, "author_reported", None),
    ("Boltz-2 iptm", C_IPTM, "author_reported", None),
    ("BACPI", C_BACPI, "author_reported", None),
    ("GAT", C_GAT, "author_reported", None),
    ("OpenFE", C_OPENFE, "unreported", QUOTED),
    ("FEP+", C_FEP_PLUS, "unreported", QUOTED),
    ("ABFE", C_ABFE, "unreported", QUOTED),
    ("FMO", C_FMO, "author_reported", None),
    ("MM/PBSA", C_MMPBSA, "author_reported", None),
    ("Chemgauss4", C_CG4, "author_reported", None),
], FEP_COLS, True, "Table 12")

emit_table(14, "the CASP16 affinity challenge", PR_CASP16, D_CASP16, H14, L14, 1747, [
    ("Boltz-2", C_BOLTZ2, "author_reported", None),
] + [(g, group_config[g], "paper_compilation", None) for g in CASP16_GROUPS] + [
    ("Boltz-2 iptm", C_IPTM, "author_reported", None),
    ("GAT", C_GAT, "author_reported", None),
    ("BACPI", C_BACPI, "author_reported", None),
], CASP16_COLS, False, "Table 14")

# ---------------------------------------------------------------- Ross 2023 tables

ross = open(ross_xml, encoding="utf-8").read()


def xml_tables(text):
    out = {}
    for m in re.finditer(r"<table-wrap\b.*?</table-wrap>", text, re.S):
        s = m.group(0)
        label = re.search(r"<label>(.*?)</label>", s, re.S)
        rows = []
        for row in re.finditer(r"<tr>(.*?)</tr>", s[s.find("<table"):], re.S):
            # Thin and non-breaking spaces inside unit labels are normalised to ordinary spaces;
            # the numeric cells themselves contain none.
            rows.append([re.sub(r"[   ]", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip()
                         for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row.group(1), re.S)])
        out[label.group(1) if label else "?"] = rows
    return out


rt = xml_tables(ross)
t3 = rt["Table 3"]
assert t3[0] == ["Accuracy metric", "Experimental survey", "FEP+ benchmark"], t3[0]
assert len(t3) == 7, len(t3)

ROSS_T3_ROWS = [
    ("Pairwise RMSE (kcal mol−1)", "pairwise-rmse", "root-mean-squared-error", "kilocalorie-per-mole", "lower",
     "pairwise, weighted mean over series, weight equal to compound count"),
    ("Pairwise MUE (kcal mol−1)", "pairwise-mue", "mean-absolute-error", "kilocalorie-per-mole", "lower",
     "pairwise mean unsigned error, weighted mean over series, weight equal to compound count"),
    ("Edgewise RMSE (kcal mol−1)", "edgewise-rmse", "root-mean-squared-error", "kilocalorie-per-mole", "lower",
     "edgewise, weighted mean over FEP graphs, weight equal to edge count"),
    ("Edgewise MUE (kcal mol−1)", "edgewise-mue", "mean-absolute-error", "kilocalorie-per-mole", "lower",
     "edgewise mean unsigned error, weighted mean over FEP graphs, weight equal to edge count"),
    ("R2", "r2", "coefficient-of-determination", "unitless", "higher",
     "of the cycle-closure-corrected absolute free energies, weighted mean over series, weight equal to compound count"),
    ("Kendall τ", "kendall-tau", "kendall-tau", "unitless", "higher",
     "of the cycle-closure-corrected absolute free energies, weighted mean over series, weight equal to compound count"),
]

ARM_NAMES = {"experimental-survey": "Repeat-assay reproducibility,", "fep-plus": "FEP+ on the public FEP benchmark,"}

ROSS_ARMS = [
    (1, "Experimental survey", C_REASSAY, PR_ROSS_SURVEY, D_SURVEY, "experimental-survey",
     "Independent repeat affinity assay on the repeat-assay survey",
     "Weighted by the number of compounds in each assay comparison; confidence intervals by bootstrap sampling over each assay comparison",
     "1,867 compounds across 62 assay comparisons (26 binding vs binding, 30 binding vs functional, 6 functional vs functional)"),
    (2, "FEP+ benchmark", C_FEP_PLUS, PR_ROSS_FEP, D_FEP, "fep-plus",
     "FEP+ on the curated public FEP benchmark",
     "Weighted average over FEP graphs; the weight is the number of compounds in the graph for the pairwise, R2 and Kendall tau metrics and the number of edges for the edgewise errors",
     "1,237 compounds over more than 50 proteins in congeneric series"),
]

for col, col_label, cfg, protocol, dataset, aslug, ev_name, agg, population in ROSS_ARMS:
    ev = b.evaluation(P + "-eval-ross-t3-" + aslug, ev_name, SIDS_ROSS, cfg, protocol, dataset, "author_reported", {
        "protocol_id": protocol,
        "dataset_version": "As curated for Ross et al. 2023",
        "split": "Whole collection; the assessed workflow is not trained",
        "population": population,
        "inputs": "Curated protein structures and congeneric ligand series with measured affinities",
        "adaptation": "Protocol adjusted by hand per system after seeing the error against experiment" if cfg == C_FEP_PLUS else "Not applicable: a second independent assay is used as the estimate",
        "metric_implementation": "Pairwise errors over every ligand pair in a graph; edgewise errors over the graph's edges; R2 and Kendall tau of the cycle-closure-corrected absolute free energies (Methods, 'Accuracy metrics')",
        "aggregation": agg,
        "budget": None,
    }, "Table 3, column '" + col_label + "'", missing={"comparison.budget": {"reason": "unreported", "note": "No compute cost is reported"}})
    for i, (row_label, rslug, metric, unit, direction, qualifier) in enumerate(ROSS_T3_ROWS):
        row = t3[i + 1]
        assert row[0] == row_label, (row[0], row_label)
        printed = row[col]
        m = re.fullmatch(r"([\d.]+) \[([\d.]+), ([\d.]+)\]", printed)
        if m:
            numeric = m.group(1)
            unc = {"type": "confidence_interval", "lower": m.group(2), "upper": m.group(3), "level": 0.95,
                   "method": "bootstrap", "printed": "[" + m.group(2) + ", " + m.group(3) + "]",
                   "note": "95% confidence interval from bootstrap sampling over the pairs of experimental series or FEP+ graphs (Table 3 legend)"}
            vm = None
        else:
            assert printed == "N/A", printed
            numeric, unc = None, None
            vm = {"reason": "inapplicable",
                  "note": "Printed as N/A: the edgewise error depends on the topology of an FEP+ graph, so the source states there is no equivalent metric in the experimental survey"}
        b.result(P + "-result-ross-t3-" + aslug + "-" + rslug,
                 ARM_NAMES[aslug] + " " + rslug.replace("-", " ").replace("rmse", "RMSE").replace("mue", "MUE").replace("r2", "R2"),
                 ROSS, SIDS_ROSS, ev, printed, metric, direction, unit,
                 'Table 3, row "' + row_label + '", column "' + col_label + '"',
                 ROSS_REVIEW('Table 3, row "' + row_label + '", column "' + col_label + '".'),
                 qualifier=qualifier, numeric=numeric, uncertainty=unc, value_missing=vm)

# Table 2: the data sets behind the benchmark. Table 1: the assay survey.
t2 = rt["Table 2"]
assert t2[0] == ["Data set name", "Proteins in data set", "No. compounds"], t2[0]
for row in t2[1:]:
    if len(row) == 3:
        name, proteins, n = row
        value = proteins + "; " + n + " compounds"
    else:
        name, n = row
        value, proteins = n + " compounds", None
    b.claim(P + "-claim-ross-t2-" + slug(name), "Public FEP benchmark composition: " + name,
            "Composition of one data set inside the assembled public FEP benchmark, as printed by the source.",
            BM_FEP, SIDS_ROSS, {
                "field": "composition:" + slug(name),
                "value": value,
                "source_locator": 'Table 2, row "' + name + '"',
                "review": ROSS_REVIEW('Table 2, row "' + name + '".'),
            }, source_id=ROSS)

t1 = rt["Table 1"]
assert t1[0] == ["Comparison type", "Proteins in set", "No. compounds"], t1[0]
for row in t1[1:]:
    if len(row) == 3:
        name, proteins, n = row
        value = proteins + "; " + n + " compounds"
    else:
        name, n = row
        value = n + " compounds"
    b.claim(P + "-claim-ross-t1-" + slug(name), "Repeat-assay survey composition: " + name,
            "Composition of one comparison type inside the repeat-assay affinity survey, as printed by the source.",
            D_SURVEY, SIDS_ROSS, {
                "field": "composition:" + slug(name),
                "value": value,
                "source_locator": 'Table 1, row "' + name + '"',
                "review": ROSS_REVIEW('Table 1, row "' + name + '".'),
            }, source_id=ROSS)

# ---------------------------------------------------------------- descriptive claims

b.claim(P + "-claim-fep-plus-tuned", "FEP+ protocol tuned per system after seeing the error against experiment",
        "Limit the Boltz-2 supplement states about the FEP+ arm it compares against.",
        C_FEP_PLUS, SIDS_SUPP + SIDS_ROSS, {
            "field": "limitation",
            "value": "The Boltz-2 supplement states that 'The results of FEP+ are intended to show the maximum attainable accuracy of current (commercial) FEP simulations by manually adjusting the protocol (input preparation, perturbation map, force field) to the system at hand after observing the error with respect to the experiment [Ross et al., 2023]'. Ross et al. 2023 describes the same adjustments in its own words: extra rotamer states, protonation states, atom mappings and scaled torsions were added 'from visual inspection and manual intervention' when poor sampling was observed in prior simulations.",
            "source_locator": "Boltz-2 supplement appendix D.2.2, 'Baselines'; Ross et al. 2023 Results, 'Using FEP to resolve ambiguities in the structural inputs'",
            "review": SUPP_REVIEW("Appendix D.2.2 'Baselines' and Ross et al. 2023 Results."),
        }, source_id=SUPP)

b.claim(P + "-claim-abfe-optimised", "ABFE protocol optimised on the data it is scored on",
        "Limit the Boltz-2 supplement states about the ABFE arm of its four-target comparison.",
        C_ABFE, SIDS_SUPP, {
            "field": "limitation",
            "value": "The supplement states that 'the results of the ABFE protocol [Wu et al., 2025] on the 4 target subset may also represent an optimistic estimate of its prospective performance given that the protocol was optimized based this dataset'.",
            "source_locator": "Appendix D.2.2, 'Baselines'",
            "review": SUPP_REVIEW("Appendix D.2.2, 'Baselines'."),
        }, source_id=SUPP)

b.claim(P + "-claim-leakage-fep-subsets", "Leakage control applied to the FEP+ benchmark subsets",
        "The training-data filtering the Boltz-2 supplement applied before scoring the FEP+ benchmark subsets.",
        PR_OPENFE, SIDS_SUPP, {
            "field": "leakage_control",
            "value": LEAK_FEP,
            "source_locator": "Appendix D.2.1, 'Data leakage control'; Figure 10",
            "review": SUPP_REVIEW("Appendix D.2.1, 'Data leakage control'."),
        }, source_id=SUPP)

b.claim(P + "-claim-leakage-4target", "Leakage control applied to the four-target subset",
        "The training-data filtering the Boltz-2 supplement applied before scoring the four-target subset.",
        PR_4T, SIDS_SUPP, {
            "field": "leakage_control",
            "value": LEAK_FEP,
            "source_locator": "Appendix D.2.1, 'Data leakage control'; Figure 10",
            "review": SUPP_REVIEW("Appendix D.2.1, 'Data leakage control'."),
        }, source_id=SUPP)

b.claim(P + "-claim-leakage-casp16", "No sequence filtering applied to the CASP16 affinity benchmark",
        "The leakage position the Boltz-2 supplement states for its CASP16 comparison.",
        PR_CASP16, SIDS_SUPP, {
            "field": "leakage_control",
            "value": LEAK_CASP16,
            "source_locator": "Appendix D.2.1, 'Data leakage control'",
            "review": SUPP_REVIEW("Appendix D.2.1, 'Data leakage control'."),
        }, source_id=SUPP)

b.claim(P + "-claim-speed-claim-unbacked", "The speed claim against FEP is not backed by a measured FEP cost",
        "Gap between the supplement's compute comparison and the values its own table prints.",
        PR_4T, SIDS_SUPP, {
            "field": "limitation",
            "value": "Table 12 is the only table that prints compute cost. Its FEP+ time cell is printed as '-' and its OpenFE and ABFE cells are ranges ('6-12 GPU hours', '>20 GPU hours'), so no measured FEP+ cost appears anywhere in the extracted tables.",
            "source_locator": "Table 12, column 'time'",
            "review": SUPP_REVIEW("Table 12, column 'time'."),
        }, source_id=SUPP)

b.claim(P + "-claim-no-per-series-values", "Per-series affinity-ranking values are not printed",
        "What the extracted tables can and cannot support about ranking inside one series.",
        BM_FEP, SIDS_SUPP + SIDS_ROSS, {
            "field": "limitation",
            "value": "Every value in Boltz-2 supplement Tables 11, 12 and 14 and in Ross et al. 2023 Table 3 is an average over series: the Boltz-2 metrics are computed per assay and averaged across assays weighted by compound count, and the Ross values are weighted averages over FEP graphs. Neither source prints a per-series value, and neither prints the spread across series, so these tables support statements about the mean over series and not about any one series.",
            "source_locator": "Boltz-2 supplement appendix D.2.2 'Evaluation metrics' and Tables 11, 12, 14; Ross et al. 2023 Table 3 legend",
            "review": SUPP_REVIEW("Appendix D.2.2 and the Table 3 legend."),
        }, source_id=SUPP)

# Gilson et al. 2026: in-text affinity values.
GILSON_QUOTES = [
    ("max-kendall-tau", "Maximum affinity-ranking accuracy reached in CASP16",
     "maximum Kendall's τ = 0.42 (abstract); the body text gives 0.39 for Figure 9A and 'about 0.4' elsewhere",
     "The CASP affinity predictions showed modest correlation with experimental data (maximum Kendall's τ = 0.42), well below the theoretical maximum possible given experimental uncertainty (~0.73).",
     "Abstract; compare Section 3.3.1, 'This is well above the maximum achieved value of 0.39 (Figure 9A)' and 'the maximum value of Kendall's tau observed here, about 0.4'"),
    ("achievable-ceiling", "Estimated achievable ranking accuracy under assay error",
     "expected mean best Kendall's τ of 0.73",
     "Weighting these values by the number of measurements in each dataset, as done in preparing the summary data in Figure 9A, we obtain an expected mean best Kendall's τ of 0.73.",
     "Section 3.3.1"),
    ("ceiling-per-target", "Per-target achievable ranking accuracy under assay error",
     "chymase 0.54 (SD 0.11), autotaxin 0.76 (SD 0.02)",
     "For chymase, the mean resampled Kendall's τ is 0.54 (SD: 0.11), and for autotaxin, the value is 0.76 (SD: 0.02).",
     "Section 3.3.1"),
    ("ceiling-2kcal", "Achievable ranking accuracy under a larger assumed assay error",
     "mean expected best Kendall's τ of 0.43 for autotaxin at 2 kcal/mol assumed error",
     "Thus, if we assign an error of 30× in IC50 (2 kcal/mol in binding free energy), we obtain a mean expected best Kendall's τ of 0.43 for autotaxin, which is similar to the best result in Figure 8A.",
     "Section 3.3.1"),
    ("structures-did-not-help", "Supplying experimental structures did not improve affinity accuracy",
     "no shift toward greater accuracy in stage 2",
     "It is evident from the histograms of Kendall's τ values over all groups (Figure 8B,C) that knowledge of the structures did not lead to a shift toward greater accuracy.",
     "Section 3.3.1"),
    ("no-better-than-d3r", "CASP16 affinity accuracy is no better than the earlier D3R challenges",
     "best CASP16 stage 1 results no better than the typical best stage 1 D3R result, which averaged Kendall's τ of 0.48 (min 0.21, max 0.71)",
     "For affinity predictions, it seems clear that the best Stage 1 CASP16 results are no better than the typical best Stage 1 D3R result, which averaged Kendall's τ of 0.48, with min/max of 0.21 and 0.71.",
     "Discussion"),
]
gilson_text = re.sub(r"<[^>]+>", " ", html.unescape(open(gilson_xml, encoding="utf-8").read()))
gilson_text = re.sub(r"\s+", " ", gilson_text)
for cslug, title, value, quote, locator in GILSON_QUOTES:
    needle = re.sub(r"\s+", " ", re.sub(r"[()×~,.:;]", " ", quote))
    needle = re.sub(r"\s+", " ", needle).strip()
    haystack = re.sub(r"\s+", " ", re.sub(r"[()×~,.:;]", " ", gilson_text))
    assert needle in haystack, needle[:120]
    b.claim(P + "-claim-gilson-" + cslug, title,
            "Affinity-ranking finding stated in the body text of the CASP16 assessment.",
            BM_CASP16, SIDS_GILSON, {
                "field": "finding:" + cslug,
                "value": value + ". Source wording: \"" + quote + "\"",
                "source_locator": locator,
                "review": GILSON_REVIEW(locator + "."),
            }, source_id=GILSON)

# ---------------------------------------------------------------- use case

LOCATORS = {
    ROSS: "Tables 1, 2 and 3; Methods 'Accuracy metrics'; Results 'Using FEP to resolve ambiguities in the structural inputs'",
    SUPP: "Appendix D.2.1 'Data leakage control'; D.2.2 'Evaluation metrics' and 'Baselines'; Tables 11, 12 and 14",
    GILSON: "Abstract; Table 1; Sections 2.3 and 3.3.1; Discussion",
}

SUMMARY = (
    "Three sources carry the extracted evidence, and none of them publishes a per-series value: every number below "
    "is an average across congeneric series.\n\n"
    "Ross et al. 2023, written by the developers of the FEP+ workflow, sets both the free energy baseline and the "
    "assay noise floor on the same page. On a curated collection of 1,237 compounds across more than 50 proteins, "
    "FEP+ reached a compound-weighted pairwise RMSE of 1.25 kcal/mol [1.17, 1.33], a pairwise mean unsigned error "
    "of 0.98 [0.91, 1.05], a coefficient of determination of 0.56 [0.51, 0.60] and a Kendall tau of 0.51 "
    "[0.48, 0.55]; its edgewise errors, which depend on the perturbation graph's topology, were 1.17 [1.08, 1.25] "
    "and 0.91 [0.84, 0.98]. The same table's survey of 1,867 compounds whose affinities were measured in at least "
    "two independent assays gives the noise floor: pairwise RMSE 0.91 kcal/mol [0.83, 1.11], mean unsigned error "
    "0.67 [0.61, 0.83], R2 0.79 [0.75, 0.82] and Kendall tau 0.71 [0.65, 0.74]. So the error of the free energy "
    "calculation is close to the error between two assays, while its rank correlation sits well below. The FEP+ "
    "protocol was adjusted by hand per system after the error against experiment had been seen, so this is a "
    "maximum-attainable rather than a prospective figure.\n\n"
    "The Boltz-2 supplement, written by the developers of Boltz-2, is the only source here that puts a "
    "machine-learning predictor beside free energy calculation on the same compounds. On 876 protein-ligand "
    "complexes from the same collection, Boltz-2 reached an assay-weighted Pearson R of 0.62 and Kendall tau of "
    "0.46, against 0.63 and 0.47 for OpenFE under a fixed automated protocol and 0.72 and 0.53 for FEP+; the "
    "sequence-only baselines reached 0.29 and 0.19 (BACPI) and 0.28 and 0.20 for its ligand-only ablation, and "
    "Boltz-2's own interface confidence score reached -0.07 and -0.05. On a four-target subset of 87 neutral "
    "compounds the supplement prints compute cost beside accuracy: Boltz-2 0.66 and 0.48 at 20 GPU seconds, "
    "OpenFE 0.66 and 0.51 at 6-12 GPU hours, ABFE 0.75 and 0.54 at more than 20 GPU hours, FEP+ 0.78 and 0.63 with "
    "its time cell printed as '-', FMO 0.55 and 0.38 at 2-10 CPU minutes, Chemgauss4 0.26 and 0.17 at 20-30 CPU "
    "seconds and MM/PBSA 0.18 and 0.16 at 10-15 CPU minutes. No measured FEP+ cost appears in the table. On the "
    "CASP16 blind challenge, where the mmseqs 90% identity filtering used for the other benchmarks was not "
    "applied because the data postdates the training cutoff, the supplement reports Boltz-2 at 0.65 and 0.45 "
    "against the highest-ranked participant at 0.54 and 0.42. Tables 11, 12 and 14 print one value per cell with "
    "no uncertainty.\n\n"
    "The independent CASP16 assessment sets those challenge figures against a ceiling. Its abstract gives the "
    "maximum Kendall tau across all participants as 0.42, against an estimated best achievable value of 0.73 "
    "derived by resampling the measurements under an assumed threefold IC50 error (0.54 with a standard deviation "
    "of 0.11 for chymase, 0.76 with 0.02 for autotaxin); under an assumed 30-fold error the expected best tau for "
    "autotaxin falls to 0.43. Its body text gives the maximum achieved value as 0.39 for one figure and 'about "
    "0.4' elsewhere without reconciling the three numbers, and it scores submissions under its own weighting and "
    "skip conventions, so its 0.42 and the 0.42 printed for group LG016 in the Boltz-2 supplement are not "
    "established to be the same quantity. Supplying experimental structures in stage 2 produced no shift toward "
    "greater accuracy, and the assessors note that the best CASP16 stage-1 results are no better than the typical "
    "best stage 1 D3R result, which averaged a Kendall tau of 0.48 with a minimum of 0.21 and a maximum of 0.71.\n\n"
    "Two comparisons bear on the use case's question and both are author-reported: the Boltz-2 supplement's two "
    "FEP+ benchmark subsets. Both take their FEP+ arm from a benchmark whose protocol was tuned per system after "
    "seeing the experimental error, and both average over series rather than printing per-series values, so "
    "neither can say how well a given series would be ranked."
)

JUDGED = [
    (PR_ROSS_FEP, "proxy", "Weighted-average pairwise error and rank correlation of a free energy perturbation workflow against measured relative affinities over more than 50 proteins' congeneric series",
     "This is the free energy baseline the use case has to beat, measured on congeneric medicinal-chemistry series with measured affinities, which is the right kind of data. It is proxy rather than direct evidence because the use case asks for within-series ranking and these numbers are averages across series: Table 3 prints weighted averages over FEP graphs, no per-series value, and no spread across series, so they cannot say how well any one series would be ranked.",
     ["Do not compare these cells with the FEP+ cells quoted in the AEV-PLIG paper (Pearson 0.68, Kendall tau 0.49): those are a different metric and probably a different subset.",
      "Do not compare Ross's weighted averages with the Boltz-2 supplement's assay-weighted target averages as if they were the same aggregation.",
      "Keep the pairwise and edgewise error families separate; the source states the edgewise errors depend on graph topology."],
     ["The FEP+ protocol was tuned per system after seeing the error against experiment, so this is a maximum-attainable rather than a prospective baseline.",
      "Reported by the developers of the workflow being assessed.",
      "No per-series values and no across-series spread are printed.",
      "No compute cost is reported, so the accuracy-against-cost half of the decision cannot be answered from this protocol.",
      "Running the workflow needs a commercial licence, so its values can only ever be recorded from publication."],
     SIDS_ROSS, "fep-baseline", "Free energy baseline against measured affinities", "Public FEP benchmark", 1, "kendall-tau"),
    (PR_ROSS_SURVEY, "proxy", "Weighted-average pairwise error and rank correlation between two independent assays of the same compounds",
     "This is the noise floor the decision rests on: it says how well relative affinities reproduce between assays, so it bounds what any method could achieve on this kind of data. It is proxy evidence because it scores assay reproducibility, not a method's ability to rank analogues, and its values are weighted averages over assay comparisons rather than per-series values.",
     ["Read these values as a ceiling on achievable accuracy, not as a method's score.",
      "Edgewise errors have no equivalent in this column and are printed as N/A."],
     ["Measures assay reproducibility, not prediction.",
      "Pools publicly reported assays with Schrodinger internal project data that is not public.",
      "Only 6 functional-vs-functional comparisons contribute, which the source says makes that category's weighted means less meaningful.",
      "The bootstrap intervals are wider than those of the FEP+ column, so the gap between the two columns is less precisely resolved than the point estimates suggest."],
     SIDS_ROSS, "fep-baseline", "Free energy baseline against measured affinities", "Repeat-assay ceiling", 2, "kendall-tau"),
    (PR_OPENFE, "proxy", "Assay-weighted average Pearson R, Kendall tau and absolute error of predicted against measured affinities over 876 protein-ligand complexes",
     "This protocol puts a machine-learning affinity predictor beside two free energy workflows on the same hit-to-lead and lead-optimisation complexes with measured affinities, which is the comparison the use case exists to make. It is proxy rather than direct evidence because the use case asks for within-series ranking and these numbers are averages across series: each metric is computed inside one assay and then averaged across assays weighted by compound count, and no per-assay or per-series value is printed.",
     ["Keep the author-reported Boltz-2, GAT and BACPI rows distinct from the OpenFE and FEP+ rows, whose origin the supplement does not state.",
      "Do not treat the results on this subset and on the four-target subset as independent; both derive from the same collection and must partly overlap.",
      "Compare only cells that share the centering convention."],
     ["Reported by the developers of the machine-learning model being promoted.",
      "No per-series value and no uncertainty are printed; bootstrap error bars exist only in a figure with no printed numbers.",
      "The FEP+ arm's protocol was tuned per system after seeing the error against experiment, which raises the baseline being compared against.",
      "The column headers read 'target avg.' while the methods define the aggregation as a compound-weighted mean across assays; the source does not reconcile the two labels.",
      "The OpenFE arm's cited source is a blog post, which is not a primary source under this repository's rules and was not retrieved.",
      "No compute cost is printed in this table."],
     SIDS_SUPP, "ml-vs-fep", "Machine learning against free energy calculation on the same series", "FEP+ benchmark, 876-complex OpenFE subset", 1, "kendall-tau"),
    (PR_4T, "proxy", "Assay-weighted average Pearson R, Kendall tau and absolute error of predicted against measured affinities for 87 neutral compounds on four kinases, beside each method's compute cost",
     "This is the only extracted protocol that prints accuracy and compute cost side by side across a machine-learning predictor, two relative free energy workflows, an absolute free energy protocol, an end-state method and a docking score, which is both halves of the decision. It is proxy rather than direct evidence because the use case asks for within-series ranking and these numbers are averages across series: each metric is computed inside one assay and then averaged across assays weighted by compound count, and no per-assay or per-series value is printed.",
     ["Read the time column as printed and do not derive a per-compound cost from it; the table does not say what it counts or on what hardware.",
      "Do not quote a measured FEP+ cost from this table; its FEP+ time cell is '-'.",
      "Four of the ten arms print N/A for every column beyond Pearson R and Kendall tau, so do not build a cross-method comparison on the error or within-threshold columns.",
      "Do not treat the results on this subset and on the 876-complex subset as independent."],
     ["Reported by the developers of the machine-learning model being promoted.",
      "No per-series value and no uncertainty are printed.",
      "The FEP+ arm's protocol was tuned per system after seeing the error against experiment, and the supplement says the ABFE arm's protocol was optimised on this same data set, so both physics baselines are optimistic.",
      "The time column has no stated denominator or hardware, and three of its cells are ranges or bounds rather than values.",
      "The series definition behind the 87 compounds rests on a citation that does not resolve in the supplement's reference list.",
      "Four targets is a small sample on which to average."],
     SIDS_SUPP, "ml-vs-fep", "Machine learning against free energy calculation on the same series", "FEP+ benchmark, four-target subset", 2, "kendall-tau"),
    (PR_CASP16, "proxy", "Assay-weighted average Pearson R, Kendall tau and absolute error of predicted against withheld measured affinities on the CASP16 chymase and autotaxin series",
     "This is blind evidence on two pharmaceutical ligand series whose affinities were withheld until after submission, which is the closest thing in this batch to a prospective read. It is proxy rather than direct evidence because the use case asks for within-series ranking and these numbers are averages across the two series, not per-series values, and because the CASP16 series are target ligand sets rather than a single congeneric series around one confirmed hit.",
     ["Keep the Boltz-2 row, which its developers report, distinct from the participant rows, which the supplement compiles.",
      "Do not read a per-target value from this table; the same two series are recorded per-target for PLABench and those values are not these values.",
      "Do not treat the anonymous group identifiers as named methods."],
     ["Reported by the developers of the machine-learning model being promoted, and the participants' submissions were not obtained independently.",
      "The mmseqs 90% identity filtering applied to the other affinity benchmarks was not applied here; the stated protection is that the data was released after the training cutoff and that maximum compound Tanimoto similarity to the training set was 0.41 and 0.59.",
      "No per-series value and no uncertainty are printed.",
      "The supplement says nothing about what methods the participant groups used.",
      "The chymase series spans a narrow affinity range, which the CASP16 assessors say limits how well the challenge resolves accuracy."],
     SIDS_SUPP, "blind-casp16", "Blind affinity ranking in CASP16", "CASP16 affinity challenge, target-averaged", 1, "kendall-tau"),
]

uc_links = [{"relation": "assessed_by", "target_id": p} for p, *_ in JUDGED]

UC = b.add({
    "id": "use-case-lead-optimisation-affinity-ranking",
    "kind": "use_case",
    "name": "Rank close analogues of a hit by binding affinity",
    "description": "Which method ranks a hit's close analogues by binding affinity accurately enough to choose what to make next, and at what compute cost against free energy calculation?",
    "status": "needs_review",
    "facets": {"areas": ["molecular-interactions", "proteins-complexes"], "contexts": ["research"]},
    "source_ids": SIDS_ROSS + SIDS_SUPP + SIDS_GILSON,
    "links": uc_links,
    "attributes": {
        "slug": "lead-optimisation-affinity-ranking",
        "question": "Which method ranks a hit's close analogues by binding affinity accurately enough to choose what to make next, and at what compute cost against free energy calculation?",
        "intended_users": [
            "Medicinal chemists choosing which analogues of a confirmed hit to synthesise next",
            "Computational chemists deciding whether to spend free energy calculation on a series",
            "Project leads budgeting compute against synthesis in a lead-optimisation campaign",
        ],
        "decision": "Choose which analogues of a confirmed hit to make next, and choose the method and compute budget used to rank them.",
        "inputs": [
            "A confirmed hit and a set of close analogues, with the series' chemical relationship stated",
            "A protein structure or sequence for the target, and its relationship to any structure used in training",
            "Measured affinities for part of the series, with the assay type and units recorded",
            "An available compute budget and a synthesis budget",
        ],
        "output": "A ranking of the analogues by predicted binding affinity, with an error estimate against measured affinities on comparable series, the leakage control that estimate rests on, and the compute cost of producing it.",
        "setting": "Research-stage lead optimisation within one target's congeneric series. Ranking across unrelated targets, hit discovery from a large library and absolute affinity prediction are separate questions.",
        "exclusions": [
            "No reviewed source in this batch publishes a per-series affinity-ranking value for any method: every extracted number is an average across series, so none of them says how well a given series would be ranked.",
            "A correlation pooled or averaged over unrelated targets does not answer this question and flatters every method.",
            "Accuracy on a benchmark series does not establish that a chosen analogue will be more potent, nor that it will be developable.",
            "IC50, Ki and Kd are not interchangeable; sources that convert between them do so under a stated assumption that must be carried with the number.",
            "Compute-cost comparisons are only meaningful against a measured alternative. The extracted tables print no measured cost for FEP+.",
        ],
        "clinical_scope": "Research only. Affinity ranking does not establish efficacy, safety or clinical suitability.",
        "evidence_gaps": [
            "Automated source review only; independent human scientific review remains outstanding.",
            "No per-series value is published for any method in the extracted sources. The route to per-series evidence is the public_binding_free_energy_benchmark repository (MIT, releases v1.0 and v2.0), which holds FEP+ per-edge results, and the OpenFE per-transformation deposits on Zenodo; nothing was computed from either in this pass.",
            "No fully independent evaluation of a machine-learning affinity predictor against free energy calculation on the same measured congeneric series was found. Both same-series comparisons that exist are reported by the developers of the machine-learning method, and both take their FEP+ arm from a benchmark whose protocol was tuned per system after seeing the error against experiment.",
            "The peer-reviewed OpenFE industry benchmark (doi 10.1021/acs.jcim.6c00089) is behind an ACS paywall and was not retrieved, so the open-source free energy arm rests on a blog post the Boltz-2 supplement cites.",
            "No measured compute cost for FEP+ exists in any extracted table; the only cost column prints '-' for FEP+ and ranges for OpenFE and ABFE.",
            "No uncertainty is printed for any Boltz-2 supplement cell; the bootstrap error bars are figure-only.",
            "The CASP16 assessors' per-group and per-target Kendall tau values are figure-only and were not extracted; the official per-target results file was not downloaded.",
            "Neither the Merck FEP benchmark (Schindler et al. 2020) nor the Hahn et al. 2022 benchmark-construction paper nor the Wu et al. 2025 ABFE protocol paper was retrieved, so the series definitions behind the four-target subset are not established.",
            "MM/GBSA and docking-score comparators on congeneric series were not searched for beyond the arms the Boltz-2 supplement chose for itself; recent affinity models other than Boltz-2, GAT and BACPI were not covered.",
            "The overlap between the 876-complex OpenFE subset and the 87-compound four-target subset is not stated in any source, so the two comparisons cannot be treated as independent.",
        ],
        "search_terms": [
            "lead optimisation", "congeneric series", "binding affinity ranking", "relative binding free energy",
            "free energy perturbation", "FEP+", "OpenFE", "absolute binding free energy", "MM/PBSA",
            "docking score", "affinity prediction benchmark", "assay reproducibility", "CASP16 affinity",
        ],
        "citation_locators": [
            {"source_id": ROSS, "locator": "Tables 1, 2 and 3; Methods 'Accuracy metrics' and 'Experimental reproducibility'; Results 'Using FEP to resolve ambiguities in the structural inputs'"},
            {"source_id": SUPP, "locator": "Appendix D.2.1 'Data leakage control'; D.2.2 'Evaluation metrics' and 'Baselines'; Tables 11, 12 and 14"},
            {"source_id": GILSON, "locator": "Abstract; Table 1; Sections 2.3 and 3.3.1; Discussion"},
        ],
        "collection_plan": {
            "status": "planned",
            "comparison_question": "On one target's congeneric series at a time, how do a machine-learning affinity predictor, a relative free energy workflow and a docking score rank the analogues, and what does each cost?",
            "baselines": [
                "A relative free energy perturbation workflow run under a fixed protocol with no per-system adjustment",
                "A docking score and an end-state method as the cheap comparators",
            ],
            "outcomes": [
                "Per-series rank correlation and pairwise error against measured affinities, with the series' affinity range stated",
                "The spread of those values across series, not only their mean",
                "Measured compute cost per compound for every arm, including the free energy arm",
            ],
            "validation_requirements": [
                "Report per-series values, not only an average over series.",
                "State the assay type and units for every series and do not mix endpoints.",
                "State the leakage control for the target, the series and close analogues.",
                "State the affinity range each series spans; a series spanning one log unit is the real task.",
                "Measure the free energy arm's cost rather than quoting it.",
            ],
            "next_step": "Decide whether to compute per-series FEP+ values from the public_binding_free_energy_benchmark repository under the repository's derivation rule, which would need its per-edge files pinned and a stated aggregation, and retrieve the OpenFE industry benchmark paper.",
        },
        "planned_work": [
            "Retrieve doi 10.1021/acs.jcim.6c00089 (OpenFE industry benchmark) to replace the blog-post citation behind the OpenFE arm.",
            "Pin the public_binding_free_energy_benchmark releases and assess whether per-series FEP+ values can be recorded under the derivation rule.",
            "Extract the CASP16 assessors' per-group affinity results from the official predictioncenter.org results file.",
            "Screen the leakage candidates the search pass noted and did not retrieve: PDBbind CleanSplit (PMC12552120), the GEMS preprint and the DAVIS-completeness preprint.",
        ],
        "review": {
            "method": ["ai-assisted-source-review"],
            "reviewer": ["claude"],
            "reviewer_note": "Claude extraction agent; no human review claimed",
            "date": "2026-10-22",
            "note": "Use-case definition drafted alongside the extraction of its first evidence. Not reviewed; a separate review-evidence pass must check it.",
        },
        "evidence_checked": {
            "date": "2026-10-22",
            "cutoff_date": "2026-10-22",
            "records": ["data/omics/lit-search-20261022-uc-leadopt/report.md", "data/omics/search-ledger.jsonl"],
        },
    },
})

for protocol, relevance, endpoint, rationale, constraints, limitations, sids, group, group_title, stratum, order, headline in JUDGED:
    b.claim(P + "-judgement-" + protocol[len(P) + len("-protocol-"):], "Relevance of " + stratum + " to ranking analogues of a hit",
            "Judgement of how closely this protocol answers the lead-optimisation ranking decision. Drafted by the extracting agent; not reviewed.",
            UC, sids, {
                "field": "links:assessed_by:" + protocol,
                "value": protocol,
                "relevance": relevance,
                "endpoint": endpoint,
                "rationale": rationale,
                "constraints": constraints,
                "limitations": limitations,
                "comparison_group": group,
                "comparison_title": group_title,
                "stratum_label": stratum,
                "stratum_order": order,
                "headline_metric": headline,
                "citation_locators": [{"source_id": s, "locator": LOCATORS[s]} for s in sids],
                "source_locator": LOCATORS[sids[0]],
                "review": {
                    "method": ["ai-assisted-source-review"],
                    "reviewer": ["claude"],
                    "reviewer_note": "Claude extraction agent; no human review claimed",
                    "date": "2026-10-22",
                    "note": "Drafted by the agent that extracted the evidence. A separate review-evidence pass must check the relevance call, the endpoint and the limitations, and list the evaluations it checked.",
                },
            }, source_id=sids[0])

b.claim("use-case-summary-lead-optimisation-affinity-ranking", "Evidence summary: ranking analogues of a hit by affinity",
        "Plain-language summary of what the extracted evidence shows. Draft until reviewed.",
        UC, SIDS_ROSS + SIDS_SUPP + SIDS_GILSON, {
            "field": "summary",
            "value": SUMMARY,
            "source_locator": "Ross et al. 2023 Tables 1-3; Boltz-2 supplement Tables 11, 12 and 14; Gilson et al. 2026 Abstract and Section 3.3.1",
            "citation_locators": [{"source_id": s, "locator": LOCATORS[s]} for s in (ROSS, SUPP, GILSON)],
            "review": {
                "method": ["ai-assisted-source-review"],
                "reviewer": ["claude"],
                "reviewer_note": "Claude extraction agent; no human review claimed",
                "date": "2026-10-22",
                "note": "Descriptive draft. Every number is traceable to a result record in this batch. Not reviewed and carries no recommendation.",
            },
        }, source_id=ROSS)

counts = b.write()

coverage = {
    "schema_version": "1.0",
    "batch": "data/omics/use-case-coverage-leadopt-20261022",
    "use_case": UC,
    "pass": "Extraction only. No record was marked reviewed; review.json and every review sign-off are left to a separate review-evidence pass.",
    "record_counts": counts,
    "reused_ids": {
        "catalog-model-boltz-2": "Boltz-2 model record; the two new configurations are configuration_of it",
        "catalog-task-ligand-affinity": "Small-molecule affinity task; the three Boltz-2 protocols and the Ross FEP+ protocol link evaluates_task to it",
    },
    "existing_ids_considered_and_not_used": {
        "expansion-p3-boltz2": "The existing Boltz-2 source record is a Europe PMC full-text XML snapshot that holds the main text, figure captions and Table 1 only. Tables 11 to 16 are not in it, so a new source record was created for the supplement PDF.",
        "lit-interactions-20261011-leakctl-protocol-casp16-l1000": "PLABench's per-series CASP16 protocol. It bears on the use case but no assessed_by link or judgement was added for it in this pass; it needs its own judgement and it is recorded here as a gap, not as an exclusion.",
        "lit-interactions-20261011-leakctl-protocol-casp16-l3000": "As above.",
        "lit-interactions-20261011-leakctl-protocol-chembl35": "As above: leakage-controlled ChEMBL35 affinity prediction, which bears on the use case and is unmapped.",
        "paper-protocol-0c5a1c5ef6896a2d96": "CASF-2016 ranking power on PDBbind-2016 core-set clusters. Within-target but not congeneric medicinal-chemistry series, so proxy; unmapped in this pass.",
        "lit-interactions-20261011-plmdta-protocol-davis-deepdta-holdout": "Pooled across targets, so a weak proxy at best; unmapped in this pass.",
        "lit-interactions-20261011-plmdta-protocol-kiba-deepdta-holdout": "As above.",
    },
    "new_protocols_judged": [{"protocol": p, "relevance": r, "comparison_group": g} for p, r, _e, _ra, _c, _l, _s, g, *_ in JUDGED],
    "vocabulary_added": {
        "data/vocab/unit.ttl": "millisecond, with a QUDT exactMatch. Needed for the Boltz-2 Table 12 time column, which prints '0.48 GPU ms' and '0.18 GPU ms'. No existing unit concept covers milliseconds."
    },
    "tables_extracted": [
        {"source": ROSS, "locator": "Table 3", "cells": 12, "note": "Both columns, all six rows; 2 cells printed N/A"},
        {"source": ROSS, "locator": "Table 2", "cells": 15, "note": "Recorded as composition claims on the benchmark, not as results"},
        {"source": ROSS, "locator": "Table 1", "cells": 4, "note": "Recorded as composition claims on the survey dataset, not as results"},
        {"source": SUPP, "locator": "Table 11", "cells": 54, "note": "6 arms x 9 metric columns; 13 cells printed N/A (7 for Boltz-2 iptm, 3 each for OpenFE and FEP+)"},
        {"source": SUPP, "locator": "Table 12", "cells": 100, "note": "10 arms x (1 time + 9 metric) columns; 34 metric cells printed N/A (7 each for Boltz-2 iptm, FMO, MM/PBSA and Chemgauss4, 3 each for OpenFE and FEP+) and the FEP+ time cell is '-'"},
        {"source": SUPP, "locator": "Table 14", "cells": 90, "note": "10 arms x 9 metric columns; 7 cells printed N/A for Boltz-2 iptm and 8 cells printed '-' for LG204, whose only printed value is Kendall tau 0.34"},
        {"source": GILSON, "locator": "Abstract, Sections 2.3 and 3.3.1, Discussion", "cells": 6, "note": "In-text values recorded as claims; the per-group results are figure-only and were not extracted"},
    ],
    "gaps": [
        "Boltz-2 supplement Tables 13, 15 and 16 were not extracted. Table 13 is binary classification (MF-PCBA), outside this use case. Tables 15 and 16 are hit-to-lead validation and the eight blinded Recursion assays; they bear on hit-to-lead rather than lead optimisation and were not reached in this pass.",
        "No per-series value exists for any method in the extracted sources. The route to per-series FEP+ values is github.com/schrodinger/public_binding_free_energy_benchmark (MIT, releases v1.0 and v2.0, both 2023-06-26), which holds per-edge FEP+ results. Nothing was computed from it in this pass, as instructed.",
        "The OpenFE industry benchmark (doi 10.1021/acs.jcim.6c00089) is behind an ACS paywall and was not retrieved, so the OpenFE arm rests on a blog post the supplement cites.",
        "Hahn et al. 2022, Schindler et al. 2020 (Merck FEP set) and Wu et al. 2025 (ABFE) were not retrieved, so the series definitions behind the four-target subset are not established.",
        "The 'Chen et al., 2023' citation the supplement gives for the 87 compounds does not resolve in its reference list.",
        "Figure-only material was not read: Boltz-2 Figure 6 (bootstrap error bars), Figure 10 (compound-similarity bins), Figure 12 (per-assay scatter plots); Gilson Figures 8 and 9 (per-group Kendall tau).",
        "The overlap between the 876-complex and 87-compound subsets is not stated in any source.",
        "The SHACL shape check was run on this batch in a sandbox copy of the subset graph; `npm run records -- add`, which runs it against the store, was deliberately not run and is left to the review agent.",
    ],
    "reviewer_must_judge": [
        "Column label against methods definition: Tables 11, 12 and 14 label their columns 'target avg.', while appendix D.2.2 defines every regression metric as computed per assay and averaged across assays weighted by compound count. Assays and targets are not the same unit. Every result's metric_qualifier follows the methods wording ('weighted mean over assays, weight proportional to compound count') and every protocol records the discrepancy.",
        "Units of the PMAE and MAE columns are not printed in the Boltz-2 table headers. They are recorded as kilocalorie-per-mole on the strength of appendix D.2.2 ('All predictions are converted to kcal/mol prior to computing the metrics'), with that stated in each result's unit_detail.",
        "The 'Perc. within 1' and 'Perc. within 2' headers say percentage, but appendix D.2.2 defines them as fractions and the printed values lie on 0 to 1. They are recorded with metric 'proportion' and unit 'fraction'.",
        "Origin of the OpenFE, FEP+ and ABFE rows in Tables 11 and 12 is recorded as 'unreported' because the supplement cites prior work without saying whether it re-ran those arms. The CASP16 participant rows are recorded as 'paper_compilation'.",
        "The experimental-reproducibility column of Ross Table 3 is modelled as a method ('Independent repeat affinity assay') on its own protocol, so the noise floor can sit beside the prediction arms. That is a modelling choice, not something the source states.",
        "Gilson et al. 2026 gives the maximum participant Kendall tau as 0.42 in the abstract, 0.39 for Figure 9A in Section 3.3.1 and 'about 0.4' two sentences later, without saying which figure or penalty convention each belongs to. Recorded in the claim's value and in the source's limitations; not raised as an evidence concern, because that would withhold every judgement citing the source.",
        "One FEP+ configuration is shared between the Ross Table 3 evaluation and the Boltz-2 Tables 11 and 12 evaluations, on the grounds that both describe the same per-system-tuned FEP+ setup. Its limitations record that the supplement does not state whether its FEP+ values were re-run or taken from Ross.",
        "N/A cells carry missing_metadata.value reason 'inapplicable'. The sources print N/A without saying why, so the note gives the likely reasons rather than asserting one.",
    ],
}
with open(os.path.join(folder, "coverage.json"), "w") as f:
    json.dump(coverage, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(json.dumps(counts, indent=1))
print(sum(counts.values()), "records")
